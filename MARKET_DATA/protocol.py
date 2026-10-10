"""Stable Market Data process-output serialization."""
from __future__ import annotations

import csv
import io
from datetime import timezone
from decimal import Decimal
from typing import Mapping, Sequence

from .models import NormalizedCandle

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
) -> str:
    """Format candles as a human-readable table for the Market Data CLI."""
    lines = [f"MARKET DATA | {symbol}"]
    for timeframe, entries in candles_by_timeframe.items():
        ordered = sorted(entries, key=lambda item: item[0].timestamp)
        lines.extend(
            [
                "",
                f"TIMEFRAME | {timeframe} | CANDLES {len(ordered)}",
                "-" * 78,
                "Time (UTC)           Open         High         Low          Close       Completed",
                "-" * 78,
            ]
        )
        for candle, completed in ordered:
            timestamp = candle.timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            lines.append(
                f"{timestamp}  "
                f"{str(candle.open_price):>11}  "
                f"{str(candle.high_price):>11}  "
                f"{str(candle.low_price):>11}  "
                f"{str(candle.close_price):>11}  "
                f"{'YES' if completed else 'NO'}"
            )
        lines.append("-" * 78)
    return "\n".join(lines)
