"""Market Data CLI parsing and execution."""
from __future__ import annotations

import argparse
import re
from datetime import datetime, timedelta, timezone
from typing import Sequence

from .models import MarketDataRequest, SUPPORTED_TIMEFRAMES
from .provider import create_provider
from .service import update_market_data


DATE_RE = r"\d{4}\.\d{2}\.\d{2}"
TIME_RE = r"\d{2}:\d{2}"


def build_argument_parser():
    """Define the Market Data CLI without performing I/O."""
    parser = argparse.ArgumentParser(
        description="Acquire, normalize and persist market data."
    )
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframes", nargs="+", required=True)
    parser.add_argument(
        "--range",
        dest="scope",
        help=(
            "Calendar-compatible scope: YYYY.MM.DD, "
            "YYYY.MM.DD-YYYY.MM.DD, YYYY.MM.DD@HH:MM, "
            "YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM, or current."
        ),
    )
    parser.add_argument(
        "--current",
        action="store_true",
        help="Refresh the current in-progress candle snapshot.",
    )
    parser.add_argument(
        "--lastclosed",
        action="store_true",
        help="Acquire exactly the latest completed/closed candle.",
    )
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
    if not re.fullmatch(DATE_RE, value.strip()):
        raise ValueError(f"invalid date, expected YYYY.MM.DD: {value}")
    try:
        return datetime.strptime(value.strip(), "%Y.%m.%d").replace(
            tzinfo=timezone.utc
        )
    except ValueError as exc:
        raise ValueError(f"invalid date, expected YYYY.MM.DD: {value}") from exc


def parse_calendar_time(value):
    """Parse the Calendar-compatible HH:MM 24-hour time format."""
    if not re.fullmatch(TIME_RE, value.strip()):
        raise ValueError(f"invalid time, expected HH:MM: {value}")
    try:
        return datetime.strptime(value.strip(), "%H:%M").time()
    except ValueError as exc:
        raise ValueError(f"invalid time, expected HH:MM: {value}") from exc


def resolve_scope_interval(scope):
    """Resolve one Calendar-compatible historical scope into a UTC interval."""
    if scope == "current":
        raise ValueError("'current' is not a historical scope")

    if "@" in scope:
        parts = scope.split("-", 1)
        if len(parts) == 2:
            start = parse_calendar_point(parts[0], require_time=True)
            end = parse_calendar_point(parts[1], require_time=True)
            if end <= start:
                raise ValueError(f"invalid datetime range: {scope}")
            return start, end
        point = parse_calendar_point(scope, require_time=True)
        return point, point + timedelta(minutes=1)

    if "-" in scope:
        parts = scope.split("-")
        if len(parts) != 2:
            raise ValueError(f"invalid date range: {scope}")
        start = parse_calendar_date(parts[0])
        end = parse_calendar_date(parts[1])
        if end < start:
            raise ValueError(
                f"invalid date range: {scope}: end must not precede start"
            )
        return start, end + timedelta(days=1)

    start = parse_calendar_date(scope)
    return start, start + timedelta(days=1)


def parse_calendar_point(value, *, require_time=False):
    """Parse a Calendar-compatible date or date-time point."""
    if "@" not in value:
        if require_time:
            raise ValueError(f"invalid datetime point: {value}")
        return parse_calendar_date(value)

    date_part, time_part = value.split("@", 1)
    base = parse_calendar_date(date_part)
    clock = parse_calendar_time(time_part)
    return base.replace(hour=clock.hour, minute=clock.minute)


def validate_scope(scope):
    """Validate the Market Data scope grammar and return its canonical value."""
    if scope is None:
        return None
    if scope == "current":
        return scope
    return scope if resolve_scope_interval(scope) else scope


def validate_request(request):
    """Validate Market Data request combinations."""
    if not request.timeframes:
        raise ValueError("at least one timeframe is required")
    if len(set(request.timeframes)) != len(request.timeframes):
        raise ValueError("duplicate timeframe")
    if request.current and request.last_closed_only:
        raise ValueError("--current is mutually exclusive with --lastclosed")
    if request.current and request.start_time is not None:
        raise ValueError("current cannot be combined with a historical range")


def parse_market_data_request(argv: Sequence[str] | None = None):
    """Parse the Calendar-compatible Market Data scope into a MarketDataRequest."""
    args = build_argument_parser().parse_args(argv)
    scope = validate_scope(args.scope)

    if args.current:
        if scope is not None:
            raise ValueError("--current cannot be combined with --range")
        start_time = None
        end_time = None
        current = True
    elif scope is not None:
        start_time, end_time = resolve_scope_interval(scope)
        current = False
    else:
        start_time = None
        end_time = None
        current = False

    request = MarketDataRequest(
        normalize_symbol(args.symbol),
        [normalize_timeframe(x) for x in args.timeframes],
        start_time,
        end_time,
        args.lastclosed,
        current,
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
