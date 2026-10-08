# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""Calendar command-line entrypoint and request dispatch."""

import json
import re
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

from . import domain, operations, presentation, storage
from .config import HELP_TEXT, CalendarInputError, DataIntegrityError

# CLI state is request-local: parsed arguments determine one operation and its diagnostic/presentation flags.

def execute_calendar_query(
    symbol: str,
    scope: str,
    cleartext: bool = False,
    debug: bool = False,
    refresh: bool = False,
) -> int:
    """Run a local Calendar query, optionally preceded by a provider refresh."""
    with storage.acquire_calendar_lock():
        document = storage.load_calendar_document()

        if refresh:
            if scope == "current":
                refresh_result = operations.refresh_current_scope(
                    document,
                    symbol,
                    debug=debug,
                )
            else:
                if domain.is_open_start_scope(scope):
                    start, end = domain.resolve_open_start_scope(document, symbol, scope)
                elif domain.is_open_end_scope(scope):
                    start, end = domain.resolve_open_end_scope(scope)
                else:
                    start, end = domain.resolve_scope_interval(scope)
                refresh_result = operations.refresh_calendar_scope(
                    document,
                    symbol,
                    start,
                    end,
                    debug=debug,
                )

            # Refresh operations already return the canonical post-refresh
            # event result. Do not reapply cache coverage or watermark filters:
            # that would hide first-use refresh events and rescheduled events
            # that intentionally moved outside the original query interval.
            events = refresh_result["events"]

            provider_status = domain.status_from_provider_results(
                refresh_result["provider_results"]
            )
            if provider_status == "UNAVAILABLE":
                status = "UNAVAILABLE"
            elif provider_status == "NO_FOREX_PAIR":
                status = "NO_FOREX_PAIR"
            elif provider_status == "PARTIAL":
                status = "PARTIAL"
            else:
                status = "OK" if events else "NO_RELEVANT_EVENT"

            if cleartext:
                presentation.output_query_result(
                    status,
                    symbol,
                    events,
                    refresh_result["provider_results"],
                    cleartext=True,
                )
                print(
                    f"REFRESH | added={refresh_result['summary']['added']} "
                    f"changed={refresh_result['summary']['changed']} "
                    f"unchanged={refresh_result['summary']['unchanged']}"
                )
            else:
                print(json.dumps({
                    "status": status,
                    "symbol": symbol,
                    "events": events,
                    "providers": presentation.sanitize_provider_results(
                        refresh_result["provider_results"]
                    ),
                    "refresh": refresh_result["summary"],
                }, ensure_ascii=False))
            return 0 if status != "UNAVAILABLE" else 2

        if scope == "current":
            # Current is a read-only active-event lookup. It never performs provider I/O.
            events = domain.query_ongoing_events(
                document["events"], symbol, domain.utc_now()
            )
            status = "OK" if events else "NO_CURRENT_EVENT"
            presentation.output_query_result(status, symbol, events, [], cleartext)
            return 0

        if scope == "latest":
            events = domain.query_latest_event(
                document["events"], symbol, domain.utc_now()
            )
            status = "OK" if events else "NO_LATEST_EVENT"
            presentation.output_query_result(status, symbol, events, [], cleartext)
            return 0

        if scope == "next":
            events = domain.query_next_event(
                document["events"], symbol, domain.utc_now()
            )
            status = "OK" if events else "NO_NEXT_EVENT"
            presentation.output_query_result(status, symbol, events, [], cleartext)
            return 0

        if scope == "prev":
            events = domain.query_prev_event(
                document["events"], symbol, domain.utc_now()
            )
            status = "OK" if events else "NO_PREV_EVENT"
            presentation.output_query_result(status, symbol, events, [], cleartext)
            return 0

        if scope == "news":
            events = domain.query_active_news(
                document["events"], symbol, domain.utc_now()
            )
            status = "NEWS_ACTIVE" if events else "NO_ACTIVE_NEWS"
            presentation.output_query_result(status, symbol, events, [], cleartext)
            return 0

        if scope in {
            "current day", "current week", "current month",
            "next day", "next week", "next month",
            "prev day", "prev week", "prev month",
        }:
            events = domain.query_relative_events(
                document["events"], symbol, scope
            )
            status = "OK" if events else "NO_RELEVANT_EVENT"
            presentation.output_query_result(status, symbol, events, [], cleartext)
            return 0

        if domain.is_open_end_scope(scope):
            # Open-end range is a cache query unless trailing refresh requests acquisition.
            start, end = domain.resolve_open_end_scope(scope)
            events = domain.filter_events_for_interval(
                domain.filter_events_for_symbol(document["events"], symbol),
                start,
                end,
            )
            status = "OK" if events else "NO_RELEVANT_EVENT"
            presentation.output_query_result(
                status,
                symbol,
                events,
                [],
                cleartext,
            )
            return 0

        if domain.is_open_start_scope(scope):
            # Plain open-start range is a cache query. Only the trailing
            # refresh modifier is allowed to contact providers.
            start, end = domain.resolve_open_start_scope(document, symbol, scope)
            events = domain.filter_events_for_interval(
                domain.filter_events_for_symbol(document["events"], symbol),
                start,
                end,
            )
            status = "OK" if events else "NO_RELEVANT_EVENT"
            presentation.output_query_result(
                status,
                symbol,
                events,
                [],
                cleartext,
            )
            return 0

        if scope == "last-update":
            updates = domain.query_last_update(document, symbol)
            status = "OK" if any(item["last_successful_at"] for item in updates) else "NO_LAST_UPDATE"
            if cleartext:
                print(f"CALENDAR RESULT | {status} | {symbol}")
                for item in updates:
                    print(
                        f"PROVIDER | {item['provider']} | "
                        f"{item['last_successful_at'] or 'N/A'}"
                    )
            else:
                print(json.dumps({
                    "status": status,
                    "symbol": symbol,
                    "last_updates": updates,
                }, ensure_ascii=False))
            return 0

        start, end = domain.resolve_scope_interval(scope)
        acquisition = operations.acquire_explicit(
            document, symbol, start, end, debug=debug
        )
        events = domain.filter_events_for_interval(
            domain.filter_events_for_symbol(document["events"], symbol),
            start,
            end,
        )
        yahoo_pair_available = not any(
            item["provider"] == "yahoo_finance"
            and item["status"] == "SKIPPED_NO_FOREX_PAIR"
            for item in acquisition["provider_results"]
        )
        events = domain.filter_query_events(
            document,
            events,
            symbol,
            start,
            end,
            yahoo_pair_available=yahoo_pair_available,
        )
        provider_statuses = [
            item["status"] for item in acquisition["provider_results"]
        ]
        if provider_statuses and all(status == "ERROR" for status in provider_statuses):
            status = "UNAVAILABLE"
        elif acquisition["failures"]:
            status = "PARTIAL"
        else:
            status = "OK" if events else "NO_RELEVANT_EVENT"
            if any(
                result["status"] in {"PARTIAL", "SKIPPED_NO_FOREX_PAIR"}
                for result in acquisition["provider_results"]
            ):
                status = "PARTIAL"
        presentation.output_query_result(
            status,
            symbol,
            events,
            acquisition["provider_results"],
            cleartext,
        )
        return 0 if status != "UNAVAILABLE" else 2
def execute_calendar_delete(
    symbol: Optional[str],
    scope: Optional[str],
) -> int:
    """Internal helper for run delete."""
    # A bare DELETE is an explicit full-cache reset; it bypasses legacy-schema
    # validation so an incompatible calendar.json cannot block the reset.
    with storage.acquire_calendar_lock():
        if symbol is None and scope is None:
            storage.save_calendar_atomic(domain.build_empty_calendar_document())
        else:
            document = storage.load_calendar_document()
            if symbol is None or scope is None:
                raise CalendarInputError(
                    "Scoped delete requires DELETE + SYMBOL + SCOPE. "
                    "Use bare 'delete' only for full cache deletion."
                )
            if (
                scope in {
                    "current", "latest", "next", "prev", "news",
                    "current day", "current week", "current month",
                    "next day", "next week", "next month",
                    "prev day", "prev week", "prev month",
                }
                or domain.is_open_start_scope(scope)
                or domain.is_open_end_scope(scope)
            ):
                raise CalendarInputError(
                    "Relative scopes, latest, next, prev, news, open-start, and open-end ranges cannot be used as delete scopes."
                )
            start, end = domain.resolve_scope_interval(scope)
            operations.delete_symbol_interval(document, symbol, start, end)
            domain.validate_calendar_document(document)
            storage.save_calendar_atomic(document)

    print(json.dumps({
        "status": "OK",
        "operation": "DELETE",
        "symbol": symbol,
        "scope": scope,
    }))
    return 0

def normalize_current_day_time_range_scope(time_range_scope: str) -> str:
    """Convert the preferred HH:MM-HH:MM shorthand to a canonical UTC datetime range.

    The CLI owns this convenience syntax so the domain layer only receives the
    canonical YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM representation.
    """
    if not re.fullmatch(r"\d{2}:\d{2}-\d{2}:\d{2}", time_range_scope):
        return time_range_scope

    # Validate both clock values before attaching today's UTC date.
    range_start_time, range_end_time = time_range_scope.split("-", 1)
    domain.parse_time(range_start_time)
    domain.parse_time(range_end_time)

    # Use Calendar's injectable UTC clock so CLI behavior is deterministic in tests.
    current_utc_date = domain.utc_now().strftime("%Y.%m.%d")
    canonical_datetime_range = (
        f"{current_utc_date}@{range_start_time}-{current_utc_date}@{range_end_time}"
    )
    return canonical_datetime_range


def parse_calendar_cli_request(cli_arguments: List[str]) -> Dict[str, Any]:
    """Parse CLI arguments into one canonical Calendar operation request."""

    if not cli_arguments:
        raise CalendarInputError("No arguments provided. Use --help.")

    if len(cli_arguments) == 1 and cli_arguments[0] in {"-h", "--help"}:
        print(HELP_TEXT)
        raise SystemExit(0)

    if any(item in {"-h", "--help"} for item in cli_arguments):
        raise CalendarInputError("--help cannot be combined with other arguments.")

    cleartext = "--cleartext" in cli_arguments
    debug = "--debug" in cli_arguments
    last_update = "--last-update" in cli_arguments

    range_values = [item for item in cli_arguments if item.startswith("--range=")]
    if "--range" in cli_arguments:
        index = cli_arguments.index("--range")
        if index + 1 >= len(cli_arguments):
            raise CalendarInputError("--range requires -YYYY.MM.DD or -YYYY.MM.DD@HH:MM.")
        range_values.append(f"--range={cli_arguments[index + 1]}")
    if len(range_values) > 1:
        raise CalendarInputError("--range may be specified only once.")
    cli_range = range_values[0].split("=", 1)[1] if range_values else None

    date_values = [item for item in cli_arguments if item.startswith("--date=")]
    if "--date" in cli_arguments:
        index = cli_arguments.index("--date")
        if index + 1 >= len(cli_arguments):
            raise CalendarInputError("--date requires YYYY.MM.DD.")
        date_values.append(f"--date={cli_arguments[index + 1]}")
    if len(date_values) > 1:
        raise CalendarInputError("--date may be specified only once.")
    cli_date = date_values[0].split("=", 1)[1] if date_values else None

    time_values = [item for item in cli_arguments if item.startswith("--time=")]
    if "--time" in cli_arguments:
        index = cli_arguments.index("--time")
        if index + 1 >= len(cli_arguments):
            raise CalendarInputError("--time requires HH:MM.")
        time_values.append(f"--time={cli_arguments[index + 1]}")
    if len(time_values) > 1:
        raise CalendarInputError("--time may be specified only once.")
    cli_time = time_values[0].split("=", 1)[1] if time_values else None

    positional: List[str] = []
    skip_next = False
    for item in cli_arguments:
        if skip_next:
            skip_next = False
            continue
        if item in {"--cleartext", "--debug", "--last-update"}:
            continue
        if item == "--range":
            skip_next = True
            continue
        if item.startswith("--range="):
            continue
        if item == "--time":
            skip_next = True
            continue
        if item.startswith("--time="):
            continue
        if item == "--date":
            skip_next = True
            continue
        if item.startswith("--date="):
            continue
        positional.append(item)

    if not positional:
        raise CalendarInputError(
            "--cleartext/--debug/--range/--time/--date/--last-update requires a symbol query."
        )

    # refresh is a trailing query modifier. It never forms its own CLI command.
    refresh = positional[-1] == "refresh"
    if refresh:
        positional.pop()

    if not positional:
        raise CalendarInputError(
            "refresh requires SYMBOL + SCOPE; use refresh only as a trailing modifier."
        )

    if last_update:
        if refresh or len(positional) != 1 or cli_range is not None or cli_date is not None or cli_time is not None:
            raise CalendarInputError(
                "--last-update requires SYMBOL and cannot be combined with "
                "refresh, --range, --date or --time."
            )
        return {
            "operation": "LAST_UPDATE",
            "symbol": domain.validate_symbol(positional[0]),
            "scope": None,
            "cleartext": cleartext,
            "debug": debug,
            "refresh": False,
        }

    if positional[0] == "delete":
        if cli_range is not None:
            raise CalendarInputError("--range is not valid for delete.")
        if refresh:
            raise CalendarInputError("refresh is not valid for delete.")
        if cleartext:
            raise CalendarInputError("--cleartext is not valid for delete.")

        if len(positional) == 1:
            if cli_date is not None or cli_time is not None:
                raise CalendarInputError("--date/--time cannot be used with bare delete.")
            return {
                "operation": "DELETE",
                "symbol": None,
                "scope": None,
                "cleartext": False,
                "debug": debug,
                "refresh": False,
            }

        if len(positional) not in {2, 3}:
            raise CalendarInputError(
                "Scoped delete requires DELETE + SYMBOL + SCOPE."
            )
        if cli_date is not None and len(positional) == 3:
            raise CalendarInputError(
                "--date cannot be combined with an explicit delete scope."
            )
        symbol = domain.validate_symbol(positional[1])
        if len(positional) == 2:
            if cli_date is not None:
                domain.parse_date(cli_date)
                scope = domain.parse_scope(
                    f"{cli_date}@{cli_time}" if cli_time is not None else cli_date
                )
            elif cli_time is not None:
                current_date = domain.utc_now().strftime("%Y.%m.%d")
                scope = domain.parse_scope(f"{current_date}@{cli_time}")
            else:
                raise CalendarInputError(
                    "Scoped delete requires an explicit scope or --date/--time."
                )
        else:
            if cli_time is not None:
                raise CalendarInputError(
                    "--time cannot be combined with an explicit delete scope."
                )
            scope = domain.parse_scope(normalize_current_day_time_range_scope(positional[2]))
        if scope == "current":
            raise CalendarInputError("current cannot be used as a delete scope.")

        return {
            "operation": "DELETE",
            "symbol": symbol,
            "scope": scope,
            "cleartext": False,
            "debug": debug,
            "refresh": False,
        }

    if len(positional) not in {1, 2, 3}:
        raise CalendarInputError(
            "Expected SYMBOL + SCOPE, optionally followed by refresh, "
            "or a relative scope such as next day, next week, prev month."
        )

    symbol = domain.validate_symbol(positional[0])
    if cli_range is not None:
        if len(positional) != 1:
            raise CalendarInputError("--range cannot be combined with a positional scope.")
        if cli_date is not None or cli_time is not None:
            raise CalendarInputError("--range cannot be combined with --date or --time.")
        scope = domain.parse_scope(cli_range)
        if scope in {
            "current", "latest", "next", "prev", "news",
            "today", "tomorrow", "yesterday",
            "current day", "current week", "current month",
            "next day", "next week", "next month",
            "prev day", "prev week", "prev month",
        }:
            raise CalendarInputError(
                "--range requires an explicit date/datetime range, an open-start -END range, "
                "or an open-end START- range."
            )
    elif len(positional) == 1:
        if cli_date is not None:
            domain.parse_date(cli_date)
            scope = domain.parse_scope(
                f"{cli_date}@{cli_time}" if cli_time is not None else cli_date
            )
        elif cli_time is not None:
            current_date = domain.utc_now().strftime("%Y.%m.%d")
            scope = domain.parse_scope(f"{current_date}@{cli_time}")
        else:
            raise CalendarInputError(
                "Expected SYMBOL + SCOPE, optionally followed by refresh."
            )
    else:
        if cli_date is not None or cli_time is not None:
            raise CalendarInputError(
                "--date/--time cannot be combined with an explicit query scope."
            )
        if len(positional) == 2:
            scope_text = normalize_current_day_time_range_scope(positional[1])
        else:
            scope_text = f"{positional[1]} {positional[2]}"
        scope = domain.parse_scope(scope_text)

    if refresh and scope in {"latest", "next", "prev", "news"}:
        raise CalendarInputError("refresh is not valid for latest, next, prev, or news.")

    return {
        "operation": "QUERY",
        "symbol": symbol,
        "scope": scope,
        "cleartext": cleartext,
        "debug": debug,
        "refresh": refresh,
    }


def execute_calendar_cli() -> int:
    """Execute the parsed Calendar CLI request and return its process exit code."""

    debug = "--debug" in sys.argv[1:]
    try:
        request = parse_calendar_cli_request(sys.argv[1:])
        debug = request["debug"]
        if request["operation"] == "DELETE":
            return execute_calendar_delete(
                request["symbol"],
                request["scope"],
            )
        if request["operation"] == "LAST_UPDATE":
            with storage.acquire_calendar_lock():
                document = storage.load_calendar_document()
            updates = domain.query_last_update(document, request["symbol"])
            status = "OK" if any(item["last_successful_at"] for item in updates) else "NO_LAST_UPDATE"
            if request["cleartext"]:
                print(f"CALENDAR RESULT | {status} | {request['symbol']}")
                for item in updates:
                    print(f"PROVIDER | {item['provider']} | {item['last_successful_at'] or 'N/A'}")
            else:
                print(json.dumps({
                    "status": status,
                    "symbol": request["symbol"],
                    "last_updates": updates,
                }, ensure_ascii=False))
            return 0
        return execute_calendar_query(
            request["symbol"],
            request["scope"],
            request["cleartext"],
            debug=debug,
            refresh=request.get("refresh", False),
        )
    except CalendarInputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        if debug:
            print("DEBUG | CalendarInputError traceback:", file=sys.stderr)
            traceback.print_exc()
        return 2
    except DataIntegrityError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        if debug:
            print("DEBUG | DataIntegrityError traceback:", file=sys.stderr)
            traceback.print_exc()
        return 3
    except Exception as exc:
        print(f"Error: Internal error: {exc}", file=sys.stderr)
        if debug:
            print("DEBUG | Unexpected exception traceback:", file=sys.stderr)
            traceback.print_exc()
        return 1

# Backward-compatible aliases retained for existing integration tests and callers.
parse_request = parse_calendar_cli_request
run_query = execute_calendar_query
run_delete = execute_calendar_delete

def main() -> None:
    """Internal helper for main."""
    raise SystemExit(execute_calendar_cli())

if __name__ == "__main__":
    main()
