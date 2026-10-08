"""Canonical timestamp, completion, numeric normalization and candle validation."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
from typing import Iterable
from .models import TIMEFRAME_SECONDS, NormalizedCandle, ProviderCandle, VolumeState

def _to_utc(value: datetime) -> datetime:
    """Convert a timezone-aware datetime to UTC."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)

def _parse_decimal(value, field_name: str) -> Decimal:
    """Parse and validate one finite Decimal input field."""
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"invalid numeric value for {field_name}") from exc
    if not result.is_finite():
        raise ValueError(f"non-finite numeric value for {field_name}")
    return result

def canonical_interval_start(timestamp: datetime, timeframe: str) -> datetime:
    """Return the canonical UTC interval start for a timeframe."""
    timestamp = _to_utc(timestamp)
    if timeframe in TIMEFRAME_SECONDS:
        seconds = TIMEFRAME_SECONDS[timeframe]
        epoch = int(timestamp.timestamp())
        return datetime.fromtimestamp(epoch - (epoch % seconds), tz=timezone.utc)
    if timeframe == "W1":
        return (timestamp - timedelta(days=timestamp.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    if timeframe == "MN1":
        return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    raise ValueError(f"unsupported timeframe: {timeframe}")


def canonical_interval_end(timestamp: datetime, timeframe: str) -> datetime:
    """Return the exclusive UTC end of the canonical timeframe interval."""
    start = canonical_interval_start(timestamp, timeframe)
    if timeframe in TIMEFRAME_SECONDS:
        return start + timedelta(seconds=TIMEFRAME_SECONDS[timeframe])
    if timeframe == "W1":
        return start + timedelta(days=7)
    if timeframe == "MN1":
        if start.month == 12:
            return start.replace(year=start.year + 1, month=1, day=1)
        return start.replace(month=start.month + 1, day=1)
    raise ValueError(f"unsupported timeframe: {timeframe}")


def canonical_next_interval_start(timestamp: datetime, timeframe: str) -> datetime:
    """Return the canonical start of the interval immediately after timestamp."""
    return canonical_interval_end(timestamp, timeframe)


def derive_completion_time(timestamp: datetime, timeframe: str) -> datetime:
    """Return the deterministic completion boundary of a canonical candle."""
    return canonical_interval_end(timestamp, timeframe)

def is_candle_complete(
    provider_candle: ProviderCandle,
    timeframe: str,
    now: datetime | None = None,
) -> bool:
    # The canonical interval boundary is authoritative. Provider hints are
    # advisory evidence and must never mark a candle complete before its
    # deterministic timeframe boundary or keep it incomplete after that boundary.
    completion_time = derive_completion_time(provider_candle.timestamp, timeframe)
    return _to_utc(now or datetime.now(timezone.utc)) >= completion_time

def build_candle_id(symbol: str, timeframe: str, timestamp: datetime) -> str:
    """Build the stable candle identity from symbol, timeframe and interval start.""
    """Build the stable candle identity from symbol, timeframe and interval start."""
    stamp = _to_utc(timestamp).isoformat().replace("+00:00", "Z")
    return f"{symbol}_{timeframe}_{stamp}"

def normalize_provider_candle(provider_candle: ProviderCandle, timeframe: str, symbol: str = "") -> NormalizedCandle:
    """Normalize one provider candle into the canonical Market Data candle model.""
    """Normalize one provider candle into the canonical Market Data candle model."""
    source_timestamp = _to_utc(provider_candle.timestamp)
    canonical_start = canonical_interval_start(source_timestamp, timeframe)
    if source_timestamp != canonical_start:
        raise ValueError(
            f"provider timestamp does not match {timeframe} interval boundary: {source_timestamp.isoformat()}"
        )
    timestamp = canonical_start
    completion_time = derive_completion_time(timestamp, timeframe)
    open_price = _parse_decimal(provider_candle.open_price, "open")
    high_price = _parse_decimal(provider_candle.high_price, "high")
    low_price = _parse_decimal(provider_candle.low_price, "low")
    close_price = _parse_decimal(provider_candle.close_price, "close")
    total = None if provider_candle.total_volume is None else _parse_decimal(provider_candle.total_volume, "total_volume")
    order_buy = None if provider_candle.orderflow_buy is None else _parse_decimal(provider_candle.orderflow_buy, "orderflow_buy")
    order_sell = None if provider_candle.orderflow_sell is None else _parse_decimal(provider_candle.orderflow_sell, "orderflow_sell")
    volume = VolumeState(total is not None, total, False, None, None, order_buy is not None or order_sell is not None, order_buy, order_sell)
    candle = NormalizedCandle(build_candle_id(symbol, timeframe, timestamp), timestamp, completion_time, open_price, high_price, low_price, close_price, volume)
    validate_normalized_candle(candle)
    return candle

def normalize_provider_candles(provider_candles: Iterable[ProviderCandle], timeframe: str, symbol: str = "") -> list[NormalizedCandle]:
    """Normalize and chronologically order a provider candle collection.""
    """Normalize and chronologically order a provider candle collection."""
    candles = [normalize_provider_candle(item, timeframe, symbol) for item in provider_candles]
    return sorted(candles, key=lambda item: item.timestamp)

def validate_normalized_candle(candle: NormalizedCandle) -> None:
    """Validate canonical OHLC, completion-time and volume invariants.""
    """Validate canonical OHLC, completion-time and volume invariants."""
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
