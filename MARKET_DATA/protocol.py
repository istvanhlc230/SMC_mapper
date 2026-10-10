"""Stable Market Data process-output serialization."""
from __future__ import annotations

import csv
import io
from datetime import timezone
from decimal import Decimal
from typing import Mapping, Sequence

from .models import MarketDepthSnapshot, NormalizedCandle

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
    "completed",
)


def _decimal_text(value: Decimal) -> str:
    """Return a locale-independent decimal representation."""
    return format(value, "f")


def _machine_row(timeframe: str, candle: NormalizedCandle, completed: bool) -> list[str]:
    """Build one portable machine-protocol candle row."""
    return [
        timeframe,
        str(int(candle.timestamp.astimezone(timezone.utc).timestamp())),
        _decimal_text(candle.open_price),
        _decimal_text(candle.high_price),
        _decimal_text(candle.low_price),
        _decimal_text(candle.close_price),
        "",
        "",
        "",
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
                _decimal_text(candle.volume.total)
                if candle.volume.has_total and candle.volume.total is not None
                else "N/A"
            )
            lines.append(
                f"{timestamp:<19} "
                f"{str(candle.open_price):>12} "
                f"{str(candle.high_price):>12} "
                f"{str(candle.low_price):>12} "
                f"{str(candle.close_price):>12} "
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
                f"{_decimal_text(bid.price) if bid is not None else '':>12}  "
                f"{_decimal_text(bid.volume) if bid is not None else '':>12}  "
                f"{_decimal_text(ask.price) if ask is not None else '':>12}  "
                f"{_decimal_text(ask.volume) if ask is not None else '':>12}"
            )
        lines.append("-" * 63)

    return "\n".join(lines)
