"""Stable Market Data process-output serialization."""
from __future__ import annotations

import csv
import io
from datetime import timezone
from decimal import Decimal
from typing import Mapping, Sequence

from .models import MarketDepthSnapshot, NormalizedCandle
from .normalization import validate_normalized_candle

MACHINE_PROTOCOL_HEADER = (
    "timeframe",
    "time",
    "open",
    "high",
    "low",
    "close",
    "tick_volume",
    "spread",
    "real_volume",
    "volume_total",
    "orderflow_buy",
    "orderflow_sell",
    "completed",
)


def _decimal_text(value: Decimal) -> str:
    """Return a locale-independent decimal representation."""
    return format(value, "f")


def _human_decimal_text(value: Decimal) -> str:
    """Render a Decimal compactly for people without changing its numeric value."""
    text = _decimal_text(value)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _optional_decimal_text(value: Decimal | None, field_name: str) -> str:
    """Return one optional finite non-negative Decimal field or a CSV empty value."""
    if value is None:
        return ""
    if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
        raise ValueError(f"{field_name} must be a finite non-negative decimal when present")
    return _decimal_text(value)


def _machine_row(timeframe: str, candle: NormalizedCandle, completed: bool) -> list[str]:
    """Validate and build one portable machine-protocol candle row."""
    if (
        candle.timestamp.tzinfo is None
        or candle.timestamp.utcoffset() is None
        or candle.completion_time.tzinfo is None
        or candle.completion_time.utcoffset() is None
    ):
        raise ValueError("machine-protocol candle timestamps must be timezone-aware")
    if candle.completion_time <= candle.timestamp:
        raise ValueError("candle completion_time must be after timestamp")
    validate_normalized_candle(candle)

    prices = (
        candle.open_price,
        candle.high_price,
        candle.low_price,
        candle.close_price,
    )
    if any(not isinstance(value, Decimal) or not value.is_finite() for value in prices):
        raise ValueError("machine-protocol OHLC values must be finite Decimals")
    if (
        candle.high_price < candle.low_price
        or not candle.low_price <= candle.open_price <= candle.high_price
        or not candle.low_price <= candle.close_price <= candle.high_price
    ):
        raise ValueError("machine-protocol candle has invalid OHLC")

    if not isinstance(completed, bool):
        raise ValueError("machine-protocol completion state must be boolean")

    volume_total = ""
    if candle.volume.has_total:
        if (
            candle.volume.total is None
            or not candle.volume.total.is_finite()
            or candle.volume.total < 0
        ):
            raise ValueError("volume.total is marked available but has no finite non-negative value")
        volume_total = _decimal_text(candle.volume.total)

    orderflow_buy = ""
    orderflow_sell = ""
    if candle.volume.has_orderflow:
        if (
            candle.volume.orderflow_buy is None
            or candle.volume.orderflow_sell is None
            or not candle.volume.orderflow_buy.is_finite()
            or not candle.volume.orderflow_sell.is_finite()
            or candle.volume.orderflow_buy < 0
            or candle.volume.orderflow_sell < 0
        ):
            raise ValueError("orderflow must contain a complete finite non-negative buy/sell pair")
        orderflow_buy = _decimal_text(candle.volume.orderflow_buy)
        orderflow_sell = _decimal_text(candle.volume.orderflow_sell)

    return [
        timeframe,
        str(int(candle.timestamp.astimezone(timezone.utc).timestamp())),
        _decimal_text(candle.open_price),
        _decimal_text(candle.high_price),
        _decimal_text(candle.low_price),
        _decimal_text(candle.close_price),
        _optional_decimal_text(candle.tick_volume, "tick_volume"),
        _optional_decimal_text(candle.spread, "spread"),
        _optional_decimal_text(candle.real_volume, "real_volume"),
        volume_total,
        orderflow_buy,
        orderflow_sell,
        "1" if completed else "0",
    ]


def serialize_machine_csv(
    candles_by_timeframe: Mapping[str, Sequence[tuple[NormalizedCandle, bool]]],
) -> str:
    """Serialize the complete validated result as the stable CSV protocol."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(MACHINE_PROTOCOL_HEADER)

    for timeframe in candles_by_timeframe:
        candles = sorted(
            candles_by_timeframe[timeframe],
            key=lambda item: item[0].timestamp,
        )
        previous_timestamp = None
        seen_ids: set[str] = set()
        for candle, completed in candles:
            if candle.candle_id in seen_ids:
                raise ValueError(f"duplicate candle identity in output: {candle.candle_id}")
            if previous_timestamp is not None and candle.timestamp <= previous_timestamp:
                raise ValueError(f"non-ascending candle timestamps for {timeframe}")
            seen_ids.add(candle.candle_id)
            previous_timestamp = candle.timestamp
            writer.writerow(_machine_row(timeframe, candle, completed))

    return output.getvalue()


def format_table(
    symbol: str,
    candles_by_timeframe: Mapping[str, Sequence[tuple[NormalizedCandle, bool]]],
    market_depth: MarketDepthSnapshot | None = None,
) -> str:
    """Format candle rows and append an L2 section only when depth data exists."""
    lines = [f"MARKET DATA | {symbol}"]
    table_width = 86
    separator = "-" * table_width

    for timeframe, entries in candles_by_timeframe.items():
        ordered = sorted(entries, key=lambda item: item[0].timestamp)
        current_snapshot_present = any(not completed for _, completed in ordered)
        state_suffix = " | CURRENT SNAPSHOT" if current_snapshot_present else ""
        lines.extend(
            [
                "",
                f"TIMEFRAME | {timeframe} | CANDLES {len(ordered)}{state_suffix}",
                separator,
                f"{'Time (UTC)':<19} {'Open':>12} {'High':>12} {'Low':>12} {'Close':>12} {'Volume':>14}",
                separator,
            ]
        )

        for candle, _completed in ordered:
            timestamp = candle.timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            volume_text = (
                _human_decimal_text(candle.volume.total)
                if candle.volume.has_total and candle.volume.total is not None
                else "N/A"
            )
            lines.append(
                f"{timestamp:<19} "
                f"{_human_decimal_text(candle.open_price):>12} "
                f"{_human_decimal_text(candle.high_price):>12} "
                f"{_human_decimal_text(candle.low_price):>12} "
                f"{_human_decimal_text(candle.close_price):>12} "
                f"{volume_text:>14}"
            )

        lines.append(separator)

    if market_depth is not None and (market_depth.bids or market_depth.asks):
        timestamp = market_depth.timestamp
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("L2 snapshot timestamp must include an explicit timezone")
        timestamp_text = timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        lines.extend(
            [
                "",
                f"L2 MARKET DEPTH | PROVIDER {market_depth.provider} | TIME (UTC) {timestamp_text}",
                "-" * 63,
                f"{'Level':>5}  {'Bid Price':>12}  {'Bid Volume':>12}  {'Ask Price':>12}  {'Ask Volume':>12}",
                "-" * 63,
            ]
        )
        level_count = max(len(market_depth.bids), len(market_depth.asks))
        for index in range(level_count):
            bid = market_depth.bids[index] if index < len(market_depth.bids) else None
            ask = market_depth.asks[index] if index < len(market_depth.asks) else None
            lines.append(
                f"{index + 1:>5}  "
                f"{_human_decimal_text(bid.price) if bid is not None else '':>12}  "
                f"{_human_decimal_text(bid.volume) if bid is not None else '':>12}  "
                f"{_human_decimal_text(ask.price) if ask is not None else '':>12}  "
                f"{_human_decimal_text(ask.volume) if ask is not None else '':>12}"
            )
        lines.append("-" * 63)

    return "\n".join(lines)
