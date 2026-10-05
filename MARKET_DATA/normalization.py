"""Canonical timestamp, completion, numeric normalization and candle validation."""
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Iterable
from .models import TIMEFRAME_SECONDS, NormalizedCandle, ProviderCandle, VolumeState

def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)

def _decimal(value, field_name: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"invalid numeric value for {field_name}") from exc
    if not result.is_finite():
        raise ValueError(f"non-finite numeric value for {field_name}")
    return result

def derive_completion_time(timestamp: datetime, timeframe: str) -> datetime:
    timestamp = _utc(timestamp)
    if timeframe not in TIMEFRAME_SECONDS:
        raise ValueError(f"unsupported timeframe duration: {timeframe}")
    from datetime import timedelta
    return timestamp + timedelta(seconds=TIMEFRAME_SECONDS[timeframe])

def is_candle_complete(
    provider_candle: ProviderCandle,
    timeframe: str,
    now: datetime | None = None,
) -> bool:
    # The canonical interval boundary is authoritative. Provider hints are
    # advisory evidence and must never mark a candle complete before its
    # deterministic timeframe boundary or keep it incomplete after that boundary.
    completion_time = derive_completion_time(provider_candle.timestamp, timeframe)
    return _utc(now or datetime.now(timezone.utc)) >= completion_time

def build_candle_id(symbol: str, timeframe: str, timestamp: datetime) -> str:
    stamp = _utc(timestamp).isoformat().replace("+00:00", "Z")
    return f"{symbol}_{timeframe}_{stamp}"

def normalize_provider_candle(provider_candle: ProviderCandle, timeframe: str, symbol: str = "") -> NormalizedCandle:
    timestamp = _utc(provider_candle.timestamp)
    completion_time = derive_completion_time(timestamp, timeframe)
    open_price = _decimal(provider_candle.open_price, "open")
    high_price = _decimal(provider_candle.high_price, "high")
    low_price = _decimal(provider_candle.low_price, "low")
    close_price = _decimal(provider_candle.close_price, "close")
    total = None if provider_candle.total_volume is None else _decimal(provider_candle.total_volume, "total_volume")
    order_buy = None if provider_candle.orderflow_buy is None else _decimal(provider_candle.orderflow_buy, "orderflow_buy")
    order_sell = None if provider_candle.orderflow_sell is None else _decimal(provider_candle.orderflow_sell, "orderflow_sell")
    volume = VolumeState(total is not None, total, False, None, None, order_buy is not None or order_sell is not None, order_buy, order_sell)
    candle = NormalizedCandle(build_candle_id(symbol, timeframe, timestamp), timestamp, completion_time, open_price, high_price, low_price, close_price, volume)
    validate_normalized_candle(candle)
    return candle

def normalize_provider_candles(provider_candles: Iterable[ProviderCandle], timeframe: str, symbol: str = "") -> list[NormalizedCandle]:
    candles = [normalize_provider_candle(item, timeframe, symbol) for item in provider_candles]
    return sorted(candles, key=lambda item: item.timestamp)

def validate_normalized_candle(candle: NormalizedCandle) -> None:
    values = (candle.open_price, candle.high_price, candle.low_price, candle.close_price)
    if any(not value.is_finite() for value in values):
        raise ValueError("candle contains non-finite OHLC")
    if candle.completion_time <= candle.timestamp:
        raise ValueError("completion_time must be after timestamp")
    if candle.high_price < candle.low_price or not (candle.low_price <= candle.open_price <= candle.high_price) or not (candle.low_price <= candle.close_price <= candle.high_price):
        raise ValueError("invalid OHLC formation")
    volume_values = (candle.volume.total, candle.volume.ohlc_buy, candle.volume.ohlc_sell, candle.volume.orderflow_buy, candle.volume.orderflow_sell)
    if any(value is not None and (not value.is_finite() or value < 0) for value in volume_values):
        raise ValueError("invalid volume value")
    if candle.volume.has_orderflow and (candle.volume.orderflow_buy is None or candle.volume.orderflow_sell is None):
        raise ValueError("orderflow branch must contain buy and sell")
