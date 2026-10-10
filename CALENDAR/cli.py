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
    table: bool = False,
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

            if table:
                presentation.output_query_result(
                    status,
                    symbol,
                    events,
                    refresh_result["provider_results"],
                    table=True,
                )
                presentation.output_refresh_summary(refresh_result["summary"])
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
            presentation.output_query_result(status, symbol, events, [], table)
            return 0

        if scope == "latest":
            events = domain.query_latest_event(
                document["events"], symbol, domain.utc_now()
            )
            status = "OK" if events else "NO_LATEST_EVENT"
            presentation.output_query_result(status, symbol, events, [], table)
            return 0

        if scope == "next":
            events = domain.query_next_event(
                document["events"], symbol, domain.utc_now()
            )
            status = "OK" if events else "NO_NEXT_EVENT"
            presentation.output_query_result(status, symbol, events, [], table)
            return 0

        if scope == "prev":
            events = domain.query_prev_event(
                document["events"], symbol, domain.utc_now()
            )
            status = "OK" if events else "NO_PREV_EVENT"
            presentation.output_query_result(status, symbol, events, [], table)
            return 0

        if scope == "news":
            events = domain.query_active_news(
                document["events"], symbol, domain.utc_now()
            )
            status = "NEWS_ACTIVE" if events else "NO_ACTIVE_NEWS"
            presentation.output_query_result(status, symbol, events, [], table)
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
            presentation.output_query_result(status, symbol, events, [], table)
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
                table,
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
                table,
            )
            return 0

        if scope == "last-update":
            updates = domain.query_last_update(document, symbol)
            status = "OK" if any(item["last_successful_at"] for item in updates) else "NO_LAST_UPDATE"
            if table:
                presentation.output_last_updates_table(status, symbol, updates)
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
            freshly_acquired_event_ids=set(acquisition.get("acquired_event_ids", [])),
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
            table,
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

def parse_calendar_cli_request(cli_arguments: List[str]) -> Dict[str, Any]:
    """Parse Calendar flags plus one positional scope using the common date/time grammar."""
    if not cli_arguments:
        raise CalendarInputError("No arguments provided. Use --help.")

    if len(cli_arguments) == 1 and cli_arguments[0] in {"-h", "--help"}:
        print(HELP_TEXT)
        raise SystemExit(0)
    if any(item in {"-h", "--help"} for item in cli_arguments):
        raise CalendarInputError("--help cannot be combined with other arguments.")

    retired_flags = ("--date", "--time", "--range")
    if any(
        item == flag or item.startswith(flag + "=")
        for item in cli_arguments
        for flag in retired_flags
    ):
        raise CalendarInputError(
            "Date/time input is positional. Use SYMBOL <scope>; "
            "--date, --time, and --range are no longer supported."
        )

    if any(item == "--cleartext" or item.startswith("--cleartext=") for item in cli_arguments):
        raise CalendarInputError("--cleartext was replaced by --table.")
    table = "--table" in cli_arguments
    debug = "--debug" in cli_arguments
    last_update = "--last-update" in cli_arguments
    recognized_flags = {"--table", "--debug", "--last-update"}
    positional: List[str] = []
    for argument in cli_arguments:
        if argument in recognized_flags:
            continue
        if argument.startswith("--"):
            raise CalendarInputError(f"Unknown CLI option '{argument}'.")
        positional.append(argument)

    if not positional:
        raise CalendarInputError("Expected a symbol query.")

    if last_update:
        if len(positional) != 1 or positional[0] == "delete":
            raise CalendarInputError(
                "--last-update requires exactly one SYMBOL and cannot be combined with a scope or refresh."
            )
        return {
            "operation": "LAST_UPDATE",
            "symbol": domain.validate_symbol(positional[0]),
            "scope": None,
            "table": table,
            "debug": debug,
            "refresh": False,
        }

    # refresh is an optional trailing query modifier; it is not a separate command.
    refresh = positional[-1] == "refresh"
    if refresh:
        positional.pop()
    if not positional:
        raise CalendarInputError("refresh requires SYMBOL + SCOPE.")

    if positional[0] == "delete":
        if refresh:
            raise CalendarInputError("refresh is not valid for delete.")
        if table:
            raise CalendarInputError("--table is not valid for delete.")
        if len(positional) == 1:
            return {
                "operation": "DELETE",
                "symbol": None,
                "scope": None,
                "table": False,
                "debug": debug,
                "refresh": False,
            }
        if len(positional) < 3:
            raise CalendarInputError(
                "Scoped delete requires DELETE + SYMBOL + positional SCOPE."
            )
        symbol = domain.validate_symbol(positional[1])
        scope_text = " ".join(positional[2:])
        scope = domain.parse_scope(scope_text)
        if scope in {
            "current", "latest", "next", "prev", "news",
            "current day", "current week", "current month",
            "next day", "next week", "next month",
            "prev day", "prev week", "prev month",
        }:
            raise CalendarInputError(
                "Relative event queries cannot be used as delete scopes."
            )
        return {
            "operation": "DELETE",
            "symbol": symbol,
            "scope": scope,
            "table": False,
            "debug": debug,
            "refresh": False,
        }

    if len(positional) < 2:
        raise CalendarInputError(
            "Expected SYMBOL + SCOPE, optionally followed by refresh."
        )
    symbol = domain.validate_symbol(positional[0])
    scope_text = " ".join(positional[1:])
    scope = domain.parse_scope(scope_text)

    if refresh and scope in {"latest", "next", "prev", "news"}:
        raise CalendarInputError("refresh is not valid for latest, next, prev, or news.")

    return {
        "operation": "QUERY",
        "symbol": symbol,
        "scope": scope,
        "table": table,
        "debug": debug,
        "refresh": refresh,
    }


def execute_calendar_cli() -> int:
    """Execute the Calendar CLI, showing help when invoked without arguments."""

    # A bare invocation is a help request, not an incomplete query or an error.
    if len(sys.argv) == 1:
        print(HELP_TEXT)
        return 0

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
            if request["table"]:
                presentation.output_last_updates_table(status, request["symbol"], updates)
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
            request["table"],
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
