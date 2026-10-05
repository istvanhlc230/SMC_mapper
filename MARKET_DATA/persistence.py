"""Canonical Market Data JSON persistence and atomic storage."""
from __future__ import annotations
import json, os, tempfile
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
from typing import Any
from .models import DECIMAL_PERSISTENCE_PLACES, TIMEFRAME_SECONDS, WRITE_RETRY_DELAY_SECONDS, WRITE_RETRY_LIMIT

def _timestamp(value: str | None) -> datetime | None:
    if value is None: return None
    parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
    if parsed.tzinfo is None: raise ValueError("persisted timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)

def _safe_symbol(symbol: str) -> str:
    if not symbol or symbol in {".",".."} or any(x in symbol for x in ("/","\\","\x00")) or ":" in symbol: raise ValueError("unsafe symbol path component")
    return symbol

def get_symbol_data_directory(symbol: str, data_directory: Path) -> Path: return Path(data_directory) / _safe_symbol(symbol)
def get_market_data_path(symbol: str, data_directory: Path) -> Path: return get_symbol_data_directory(symbol,data_directory) / f"{_safe_symbol(symbol)}_marketdata.json"
def create_empty_market_data(symbol: str) -> dict[str,Any]: return {"symbol":symbol,"timeframes":{}}

def ensure_timeframe_state(market_data, timeframe):
    return market_data["timeframes"].setdefault(timeframe,{"available_start":None,"available_end":None,"candles":[],"current":None})

def update_available_bounds(timeframe_state):
    candles=timeframe_state["candles"]
    timeframe_state["available_start"]=candles[0]["timestamp"] if candles else None
    timeframe_state["available_end"]=candles[-1]["timestamp"] if candles else None

def _validate_persisted_decimal(value: Any, field_name: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"persisted {field_name} must be a Decimal string")
    parsed = Decimal(value)
    if not parsed.is_finite():
        raise ValueError(f"persisted {field_name} must be finite")
    if parsed < 0:
        raise ValueError(f"persisted {field_name} must be non-negative")

def _validate_candle_record(candle):
    required={"candle_id","timestamp","completion_time","open","high","low","close","volume"}
    if not required <= set(candle): raise ValueError("malformed persisted candle")
    stamp=_timestamp(candle["timestamp"]); completion=_timestamp(candle["completion_time"])
    if completion is None or stamp is None or completion <= stamp: raise ValueError("invalid persisted candle time")
    for key in ("open","high","low","close"): _validate_persisted_decimal(candle[key], key)
    if Decimal(candle["high"]) < Decimal(candle["low"]): raise ValueError("invalid persisted OHLC")
    if not Decimal(candle["low"]) <= Decimal(candle["open"]) <= Decimal(candle["high"]): raise ValueError("invalid persisted OHLC")
    if not Decimal(candle["low"]) <= Decimal(candle["close"]) <= Decimal(candle["high"]): raise ValueError("invalid persisted OHLC")
    volume=candle["volume"]
    if not isinstance(volume,dict): raise ValueError("invalid persisted volume")
    for branch in ("total","ohlc","orderflow"):
        if branch not in volume: continue
        if branch=="total": _validate_persisted_decimal(volume[branch],"volume.total")
        else:
            if not isinstance(volume[branch],dict) or set(volume[branch]) != {"buy","sell"}: raise ValueError(f"invalid volume.{branch}")
            _validate_persisted_decimal(volume[branch]["buy"],f"volume.{branch}.buy")
            _validate_persisted_decimal(volume[branch]["sell"],f"volume.{branch}.sell")

def _validate_current_snapshot(
    current: dict[str, Any],
    candles: list[dict[str, Any]],
    timeframe: str,
) -> None:
    """Validate current-snapshot structural invariants without using wall-clock state."""
    _validate_candle_record(current)
    current_id = current["candle_id"]
    if any(candle["candle_id"] == current_id for candle in candles):
        raise ValueError("current candle identity must not also exist in candles")
    stamp = _timestamp(current["timestamp"])
    completion = _timestamp(current["completion_time"])
    if stamp is None or completion is None:
        raise ValueError("invalid current snapshot timestamps")
    expected_completion = stamp + __import__("datetime").timedelta(
        seconds=TIMEFRAME_SECONDS[timeframe]
    )
    if completion != expected_completion:
        raise ValueError("current completion_time does not match timeframe boundary")


def load_market_data(path: Path, symbol: str) -> dict[str,Any]:
    if not path.exists(): return create_empty_market_data(symbol)
    try: market_data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: raise ValueError(f"invalid market-data JSON: {path}") from exc
    if market_data.get("symbol") != symbol or not isinstance(market_data.get("timeframes"),dict): raise ValueError("invalid market-data document")
    for timeframe,state in market_data["timeframes"].items():
        if not isinstance(state,dict) or set(("available_start","available_end","candles","current"))-set(state): raise ValueError(f"invalid timeframe state: {timeframe}")
        if not isinstance(state["candles"],list): raise ValueError("candles must be a list")
        last=None; ids=set()
        for candle in state["candles"]:
            _validate_candle_record(candle)
            if candle["candle_id"] in ids or (last is not None and _timestamp(candle["timestamp"]) <= last): raise ValueError("invalid candle ordering or duplicate identity")
            ids.add(candle["candle_id"]); last=_timestamp(candle["timestamp"])
        expected_start = state["candles"][0]["timestamp"] if state["candles"] else None
        expected_end = state["candles"][-1]["timestamp"] if state["candles"] else None
        if state["available_start"] != expected_start or state["available_end"] != expected_end:
            raise ValueError(f"invalid availability bounds: {timeframe}")
        if timeframe not in TIMEFRAME_SECONDS:
            raise ValueError(f"unsupported persisted timeframe: {timeframe}")
        current = state["current"]
        if current is not None:
            _validate_current_snapshot(current, state["candles"], timeframe)
    return market_data

def serialize_decimal(value: Decimal) -> str:
    if not value.is_finite(): raise ValueError("cannot serialize non-finite Decimal")
    quantum=Decimal(1).scaleb(-DECIMAL_PERSISTENCE_PLACES)
    return format(value.quantize(quantum,rounding=ROUND_HALF_EVEN),"f")

def _serialize(value):
    if isinstance(value,Decimal): return serialize_decimal(value)
    if isinstance(value,datetime): return value.astimezone(timezone.utc).isoformat().replace("+00:00","Z")
    if isinstance(value,dict): return {key:_serialize(item) for key,item in value.items()}
    if isinstance(value,list): return [_serialize(item) for item in value]
    return value

def serialize_market_data(market_data):
    return json.dumps(_serialize(market_data),ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def save_market_data_atomic(path: Path, market_data, retry_limit=WRITE_RETRY_LIMIT):
    path.parent.mkdir(parents=True,exist_ok=True)
    payload=serialize_market_data(market_data)
    last_error=None
    for attempt in range(retry_limit):
        temporary=None
        try:
            with tempfile.NamedTemporaryFile("w",encoding="utf-8",dir=path.parent,delete=False,prefix=".market_data.",suffix=".tmp") as handle:
                temporary=Path(handle.name); handle.write(payload); handle.flush(); os.fsync(handle.fileno())
            os.replace(temporary,path); return
        except OSError as exc:
            last_error=exc
            if temporary and temporary.exists(): temporary.unlink(missing_ok=True)
            if attempt+1 < retry_limit:
                import time; time.sleep(WRITE_RETRY_DELAY_SECONDS)
    raise OSError(f"atomic market-data save failed: {last_error}")
