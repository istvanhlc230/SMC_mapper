"""Market Data CLI parsing and execution."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from typing import Sequence

from .models import MarketDataRequest, SUPPORTED_TIMEFRAMES
from .provider import create_provider
from .protocol import format_table, serialize_machine_csv
from .service import get_candles
from COMMON.date_time import DateTimeScopeError, DateTimeScopeParser, utc_now


def build_argument_parser():
    """Build the documented Market Data help parser without doing I/O."""
    parser = argparse.ArgumentParser(
        description=(
            "Acquire and persist Market Data. Successful default output is machine-readable CSV on STDOUT; "
            "--table selects human-readable tabular output."
        ),
        usage=(
            "%(prog)s SYMBOL --timeframes TF [TF ...] [SCOPE ...] "
            "[--current | --lastclosed] [--debug] [--table]"
        ),
    )
    parser.add_argument("symbol", nargs="?", metavar="SYMBOL", help="Instrument or ticker symbol (positional).")
    parser.add_argument(
        "--timeframes",
        metavar="TF",
        help="One or more supported timeframes (for example H1 M15).",
    )
    parser.add_argument(
        "scope",
        nargs="*",
        metavar="SCOPE",
        help=(
            "Optional positional date/time scope; date and time are separated by a space. "
            "The scope may contain multiple words."
        ),
    )
    parser.add_argument("--current", action="store_true", help="Refresh the current in-progress candle snapshot.")
    parser.add_argument("--lastclosed", action="store_true", help="Acquire exactly the latest completed candle.")
    parser.add_argument("--debug", action="store_true", help="Write diagnostic traceback/details to STDERR on failure.")
    parser.add_argument("--table", action="store_true", help="Use human-readable table output instead of machine CSV.")
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
    """Compatibility wrapper over the shared strict YYYY.MM.DD parser."""
    return DateTimeScopeParser.parse_date_value(value)


def parse_calendar_time(value):
    """Compatibility wrapper returning a time object from the shared HH:MM parser."""
    hour, minute = DateTimeScopeParser.parse_time_value(value)
    return datetime(2000, 1, 1, hour=hour, minute=minute).time()


def resolve_scope_interval(scope):
    """Resolve the common positional scope grammar into optional UTC boundaries."""
    parsed_scope = DateTimeScopeParser().parse(scope)
    return parsed_scope.start, parsed_scope.end


def parse_open_ended_point(value):
    """Compatibility wrapper for one shared-parser date/time point."""
    parsed_scope = DateTimeScopeParser().parse(value)
    if parsed_scope.kind not in {"DATETIME", "TIME"} or parsed_scope.start is None:
        raise DateTimeScopeError(f"invalid datetime point: {value}")
    return parsed_scope.start


def parse_calendar_point(value, *, require_time=False):
    """Compatibility wrapper for a single date/time endpoint."""
    parsed_scope = DateTimeScopeParser().parse(value)
    if parsed_scope.kind not in {"DATE", "DATETIME", "TIME"} or parsed_scope.start is None:
        raise DateTimeScopeError(f"invalid date/time point: {value}")
    if require_time and parsed_scope.kind == "DATE":
        raise DateTimeScopeError(f"invalid datetime point: {value}")
    return parsed_scope.start


def validate_scope(scope):
    """Validate one positional date/time scope and reject a future start."""
    if scope is None:
        return None
    parsed_scope = DateTimeScopeParser().parse(scope)
    if parsed_scope.start is not None and parsed_scope.start > utc_now():
        raise ValueError(f"future scope start is not allowed: {scope}")
    return parsed_scope




def validate_request(request):
    """Validate Market Data request combinations."""
    if not request.timeframes:
        raise ValueError("at least one timeframe is required")
    if len(set(request.timeframes)) != len(request.timeframes):
        raise ValueError("duplicate timeframe")
    if request.current and request.last_closed_only:
        raise ValueError("--current is mutually exclusive with --lastclosed")
    if request.current and (request.start_time is not None or request.end_time is not None):
        raise ValueError("current cannot be combined with a positional historical scope")
    if request.last_closed_only and (request.start_time is not None or request.end_time is not None):
        raise ValueError("lastclosed cannot be combined with a positional historical scope")


def parse_market_data_request(argv: Sequence[str] | None = None):
    """Parse Market Data flags and an optional positional scope consistently with Calendar."""
    raw_arguments = list(sys.argv[1:] if argv is None else argv)
    if any(argument in {"-h", "--help"} for argument in raw_arguments):
        build_argument_parser().print_help()
        raise SystemExit(0)

    symbol = None
    timeframes = []
    current = False
    last_closed_only = False
    debug = False
    table = False
    scope_tokens = []
    options_seen = set()
    index = 0

    while index < len(raw_arguments):
        argument = raw_arguments[index]
        if argument in {"--range", "--date", "--time"} or any(
            argument.startswith(flag + "=")
            for flag in ("--range", "--date", "--time")
        ):
            raise ValueError(
                "Date/time scope is positional; --range, --date, and --time are not supported."
            )
        if argument == "--symbol":
            raise ValueError("SYMBOL is positional; do not use --symbol. Example: market_data.py EURUSD --timeframes H1 M15.")
        elif argument == "--timeframes":
            if argument in options_seen:
                raise ValueError("--timeframes may be specified only once")
            options_seen.add(argument)
            index += 1
            while index < len(raw_arguments):
                candidate = raw_arguments[index]
                if candidate.upper() not in SUPPORTED_TIMEFRAMES:
                    break
                timeframes.append(normalize_timeframe(candidate))
                index += 1
            if not timeframes:
                raise ValueError("--timeframes requires at least one supported timeframe")
            continue
        elif argument == "--current":
            current = True
        elif argument == "--lastclosed":
            last_closed_only = True
        elif argument == "--debug":
            debug = True
        elif argument == "--cleartext":
            raise ValueError("--cleartext is no longer supported; use --table instead.")
        elif argument == "--table":
            table = True
        elif argument.startswith("--"):
            raise ValueError(f"unknown CLI option: {argument}")
        else:
            if symbol is None:
                symbol = argument
            else:
                scope_tokens.append(argument)
        index += 1

    if symbol is None:
        raise ValueError("expected SYMBOL as a positional argument")
    if not timeframes:
        raise ValueError("--timeframes requires at least one supported timeframe")

    normalized_symbol = normalize_symbol(symbol)
    normalized_timeframes = [normalize_timeframe(item) for item in timeframes]
    scope_text = " ".join(scope_tokens).strip()
    parsed_scope = validate_scope(scope_text) if scope_text else None
    start_time = parsed_scope.start if parsed_scope is not None else None
    end_time = parsed_scope.end if parsed_scope is not None else None

    if current and last_closed_only:
        raise ValueError("--current is mutually exclusive with --lastclosed")
    if (current or last_closed_only) and parsed_scope is not None:
        mode_name = "--current" if current else "--lastclosed"
        raise ValueError(f"{mode_name} cannot be combined with a positional historical scope")

    request = MarketDataRequest(
        normalized_symbol,
        normalized_timeframes,
        start_time,
        end_time,
        last_closed_only,
        current,
        debug,
        table,
    )
    validate_request(request)
    return request




def run(request):
    """Execute acquisition and emit only the selected process-output protocol."""
    provider = create_provider("lse")
    try:
        candles_by_timeframe = get_candles(request, provider)
        output_entries = {}
        for timeframe, candles in candles_by_timeframe.items():
            output_entries[timeframe] = [
                (
                    candle,
                    candle.completion_time <= datetime.now(timezone.utc),
                )
                for candle in candles
            ]

        if request.current:
            for timeframe, entries in output_entries.items():
                incomplete = [entry for entry in entries if not entry[1]]
                output_entries[timeframe] = incomplete[-1:]
        elif request.last_closed_only:
            for timeframe, entries in output_entries.items():
                output_entries[timeframe] = entries[-1:]

        if request.table:
            print(format_table(request.symbol, output_entries), end="\n")
        else:
            print(serialize_machine_csv(output_entries), end="")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        if request.debug:
            import traceback
            traceback.print_exc()
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Parse and execute the Market Data CLI, showing help when no arguments are supplied."""
    # Treat a bare invocation as a request for usage help instead of letting
    # argparse report missing required options as an error.
    supplied_arguments = sys.argv[1:] if argv is None else list(argv)
    if not supplied_arguments:
        build_argument_parser().print_help()
        return 0

    try:
        request = parse_market_data_request(supplied_arguments)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        debug_enabled = "--debug" in (sys.argv[1:] if argv is None else argv)
        if debug_enabled:
            import traceback
            traceback.print_exc()
        return 2
    return run(request)



if __name__ == "__main__":
    raise SystemExit(main())
