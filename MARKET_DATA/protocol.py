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
    """Format candles with OHLC and available normalized total volume."""
    lines = [f"MARKET DATA | {symbol}"]
    table_width = 87
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

    return "\n".join(lines)
