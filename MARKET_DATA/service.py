"""Market Data acquisition, merge, retention and symbol transaction orchestration."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Sequence
from .models import DEFAULT_CANDLE_RETENTION, DEFAULT_DATA_DIRECTORY, TIMEFRAME_SECONDS, MarketDataRequest, NormalizedCandle
from .normalization import is_candle_complete, normalize_provider_candle, normalize_provider_candles
from .persistence import ensure_timeframe_state, get_market_data_path, load_market_data, save_market_data_atomic, update_available_bounds

def _candle_dict(candle: NormalizedCandle):
    volume={}
    if candle.volume.has_total: volume["total"]=candle.volume.total
    if candle.volume.has_ohlc: volume["ohlc"]={"buy":candle.volume.ohlc_buy,"sell":candle.volume.ohlc_sell}
    if candle.volume.has_orderflow: volume["orderflow"]={"buy":candle.volume.orderflow_buy,"sell":candle.volume.orderflow_sell}
    return {"candle_id":candle.candle_id,"timestamp":candle.timestamp,"completion_time":candle.completion_time,"open":candle.open_price,"high":candle.high_price,"low":candle.low_price,"close":candle.close_price,"volume":volume}

def _same(a,b): return a==b

def deduplicate_candles(candles: Sequence[dict[str,Any]]) -> list[dict[str,Any]]:
    result={}
    for candle in candles:
        identity=candle["candle_id"]
        if identity in result and not _same(result[identity],candle): raise ValueError(f"conflicting candle identity: {identity}")
        result[identity]=candle
    return sort_candles(list(result.values()))

def sort_candles(candles): return sorted(candles,key=lambda item:item["timestamp"])

def merge_completed_candles(existing_candles, incoming_candles):
    merged={c["candle_id"]:c for c in existing_candles}
    for normalized in incoming_candles:
        record=_candle_dict(normalized); identity=record["candle_id"]
        if identity in merged and not _same(merged[identity],record): raise ValueError(f"conflicting candle identity: {identity}")
        merged[identity]=record
    return deduplicate_candles(list(merged.values()))

def apply_candle_retention(candles, retention_limit, protected_start=None, protected_end=None):
    if retention_limit < 0: raise ValueError("retention_limit must be non-negative")
    protected=[]; unprotected=[]
    for candle in candles:
        stamp=candle["timestamp"]
        in_range=(protected_start is not None and stamp>=protected_start and (protected_end is None or stamp<=protected_end))
        (protected if in_range else unprotected).append(candle)
    if protected_start is None: return sort_candles(list(candles))[-retention_limit:] if retention_limit else []
    remaining=max(0,retention_limit-len(protected))
    return sort_candles(protected+sort_candles(unprotected)[-remaining:])

def resolve_acquisition_range(request,timeframe,existing_state):
    if request.last_closed_only: return None,None
    if request.start_time is not None:
        end=request.end_time or datetime.now(timezone.utc)
        return request.start_time,end
    if request.end_time is not None:
        if not existing_state or not existing_state.get("available_start"): raise ValueError(f"--endtime requires existing retained history for {timeframe}")
        return datetime.fromisoformat(existing_state["available_start"].replace("Z","+00:00")),request.end_time
    if existing_state and existing_state.get("available_end"):
        start=datetime.fromisoformat(existing_state["available_end"].replace("Z","+00:00"))
        return start,datetime.now(timezone.utc)
    return None,datetime.now(timezone.utc)

def fetch_completed_candles(provider,symbol,timeframe,start_time,end_time):
    records=provider.fetch_range(symbol,timeframe,start_time,end_time)
    normalized=normalize_provider_candles(records,timeframe,symbol)
    output=[]
    for candle in normalized:
        if candle.completion_time>=start_time and candle.completion_time<=end_time: output.append(candle)
    return [c for c in output if c.completion_time<=datetime.now(timezone.utc)]

def fetch_latest_completed_candle(provider,symbol,timeframe):
    record=provider.fetch_latest_completed(symbol,timeframe)
    if record is None: return None
    normalized=normalize_provider_candle(record,timeframe,symbol)
    return normalized if is_candle_complete(record,timeframe) else None

def fetch_current_candle(provider,symbol,timeframe):
    record=provider.fetch_current(symbol,timeframe)
    if record is None: return None
    normalized=normalize_provider_candle(record,timeframe,symbol)
    return None if is_candle_complete(record,timeframe) else normalized

def build_current_snapshot(normalized_candle): return _candle_dict(normalized_candle)
def clear_completed_current_snapshot(timeframe_state,completed_candle_id):
    current=timeframe_state.get("current")
    if current and current.get("candle_id")==completed_candle_id: timeframe_state["current"]=None

def update_timeframe(market_data,provider,request,timeframe):
    state=ensure_timeframe_state(market_data,timeframe); original=deepcopy(state)
    if state.get("current") is not None:
        current_completion = datetime.fromisoformat(state["current"]["completion_time"].replace("Z","+00:00"))
        if current_completion <= datetime.now(timezone.utc):
            state["candles"] = deduplicate_candles(state["candles"] + [state["current"]])
            state["current"] = None
    acquisition_start,acquisition_end=resolve_acquisition_range(request,timeframe,state)
    if request.last_candle_only:
        latest=fetch_latest_completed_candle(provider,request.symbol,timeframe)
        incoming=[] if latest is None else [latest]
        protected_start=protected_end=None
    elif acquisition_start is not None and acquisition_end is not None:
        incoming=fetch_completed_candles(provider,request.symbol,timeframe,acquisition_start,acquisition_end)
        protected_start,protected_end=acquisition_start,acquisition_end
    else: incoming=[]; protected_start=protected_end=None
    state["candles"]=merge_completed_candles(state["candles"],incoming)
    if request.live:
        current=fetch_current_candle(provider,request.symbol,timeframe)
        state["current"]=None if current is None else build_current_snapshot(current)
        if current is not None and current.completion_time<=datetime.now(timezone.utc):
            state["candles"]=merge_completed_candles(state["candles"],[current]); state["current"]=None
    elif state.get("current") and any(c["candle_id"]==state["current"]["candle_id"] for c in state["candles"]): state["current"]=None
    state["candles"]=apply_candle_retention(state["candles"],DEFAULT_CANDLE_RETENTION,protected_start,protected_end)
    update_available_bounds(state)
    return state != original

def update_market_data(request,provider):
    path=get_market_data_path(request.symbol, DEFAULT_DATA_DIRECTORY)
    market_data=load_market_data(path,request.symbol); working=deepcopy(market_data); changed=False
    for timeframe in request.timeframes: changed=update_timeframe(working,provider,request,timeframe) or changed
    if not changed: return False
    save_market_data_atomic(path,working); return True
