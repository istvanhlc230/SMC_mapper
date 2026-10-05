"""Market Data CLI parsing and execution."""
from __future__ import annotations

import argparse
import re
from datetime import datetime, timedelta, timezone
from typing import Sequence

from .models import MarketDataRequest, SUPPORTED_TIMEFRAMES
from .provider import create_provider
from .service import update_market_data


def build_argument_parser():
    """Define the Market Data CLI without performing I/O."""
    parser = argparse.ArgumentParser(
        description="Acquire, normalize and persist market data."
    )
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframes", nargs="+", required=True)
    parser.add_argument("--startdate")
    parser.add_argument("--starttime")
    parser.add_argument("--enddate")
    parser.add_argument("--endtime")
    parser.add_argument("--lastcandle", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser


def normalize_symbol(symbol):
    """Normalize and validate the requested symbol."""
    value = symbol.strip()
    if not value:
        raise ValueError("symbol cannot be empty")
    if any(ch in value for ch in "/\\\x00"):
        raise ValueError("unsafe symbol")
    return value.upper()


def normalize_timeframe(timeframe):
    """Normalize and validate a requested timeframe."""
    value = timeframe.strip().upper()
    if value not in SUPPORTED_TIMEFRAMES:
        raise ValueError(f"unsupported timeframe: {timeframe}")
    return value


def parse_calendar_date(value):
    """Parse the Calendar-compatible YYYY.MM.DD date format."""
    if not re.fullmatch(r"\\d{4}\\.\\d{2}\\.\\d{2}", value.strip()):
        raise ValueError(f"invalid date, expected YYYY.MM.DD: {value}")
    try:
        return datetime.strptime(value.strip(), "%Y.%m.%d").date()
    except ValueError as exc:
        raise ValueError(
            f"invalid date, expected YYYY.MM.DD: {value}"
        ) from exc


def parse_calendar_time(value):
    """Parse the Calendar-compatible HH:MM 24-hour time format."""
    if not re.fullmatch(r"\\d{2}:\\d{2}", value.strip()):
        raise ValueError(f"invalid time, expected HH:MM: {value}")
    try:
        return datetime.strptime(value.strip(), "%H:%M").time()
    except ValueError as exc:
        raise ValueError(
            f"invalid time, expected HH:MM: {value}"
        ) from exc


def resolve_boundary(date_value, time_value, *, boundary_name, now):
    """Resolve independent Calendar-style date/time components into UTC."""
    if date_value is None and time_value is None:
        return None

    if date_value is not None:
        boundary_date = parse_calendar_date(date_value)
    else:
        boundary_date = now.date()

    if time_value is not None:
        boundary_time = parse_calendar_time(time_value)
    elif date_value is not None:
        boundary_time = datetime.min.time()
    else:
        boundary_time = now.time().replace(second=0, microsecond=0)

    resolved = datetime.combine(
        boundary_date,
        boundary_time,
        tzinfo=timezone.utc,
    )

    # An end date without an explicit time denotes the complete UTC
    # calendar day, represented internally by the next day's exclusive bound.
    if boundary_name == "end" and date_value is not None and time_value is None:
        resolved += timedelta(days=1)

    return resolved


def validate_request(request):
    """Validate Market Data request combinations and temporal ordering."""
    if not request.timeframes:
        raise ValueError("at least one timeframe is required")
    if len(set(request.timeframes)) != len(request.timeframes):
        raise ValueError("duplicate timeframe")
    if request.last_candle_only and (request.start_time or request.end_time):
        raise ValueError(
            "--lastcandle is mutually exclusive with explicit date/time boundaries"
        )
    if (
        request.start_time
        and request.end_time
        and request.start_time >= request.end_time
    ):
        raise ValueError("start boundary must be before end boundary")


def parse_market_data_request(argv: Sequence[str] | None = None):
    """Parse Calendar-style date/time CLI fields into a MarketDataRequest."""
    args = build_argument_parser().parse_args(argv)
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)

    start_time = resolve_boundary(
        args.startdate,
        args.starttime,
        boundary_name="start",
        now=now,
    )
    end_time = resolve_boundary(
        args.enddate,
        args.endtime,
        boundary_name="end",
        now=now,
    )

    request = MarketDataRequest(
        normalize_symbol(args.symbol),
        [normalize_timeframe(x) for x in args.timeframes],
        start_time,
        end_time,
        args.lastcandle,
        args.live,
        args.debug,
    )
    validate_request(request)
    return request


def run(request):
    """Execute the requested Market Data acquisition."""
    provider = create_provider("yahoo_charts")
    try:
        update_market_data(request, provider)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        if request.debug:
            import traceback
            traceback.print_exc()
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Parse and execute the Market Data CLI."""
    request = parse_market_data_request(argv)
    return run(request)


if __name__ == "__main__":
    raise SystemExit(main())
