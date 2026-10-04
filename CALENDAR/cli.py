"""Calendar command-line entrypoint and request dispatch."""

import sys
import traceback
from typing import Any, Dict, List, Optional

from . import domain, operations, presentation, storage
from .config import HELP_TEXT, CalendarInputError, DataIntegrityError

def run_query(
    symbol: str,
    scope: str,
    cleartext: bool = False,
    debug: bool = False,
) -> int:
    with storage.acquire_calendar_lock():
        document = storage.load_calendar_document()

        if scope == "current":
            result = operations.acquire_current(document, symbol, debug=debug)
            events = domain.filter_events_for_symbol(result["events"], symbol)
            status = domain.status_from_provider_results(result["provider_results"])
            if status == "OK" and not events:
                status = "NO_RELEVANT_EVENT"
            presentation.output_query_result(
                status,
                symbol,
                events,
                result["provider_results"],
                cleartext,
            )
            return 0 if status != "UNAVAILABLE" else 2

        if scope == "latest":
            events = domain.query_latest_event(document["events"], symbol, domain.utc_now())
            status = "OK" if events else "NO_LATEST_EVENT"
            presentation.output_query_result(status, symbol, events, [], cleartext)
            return 0

        if scope == "next":
            events = domain.query_next_event(document["events"], symbol, domain.utc_now())
            status = "OK" if events else "NO_NEXT_EVENT"
            presentation.output_query_result(status, symbol, events, [], cleartext)
            return 0

        start, end = domain.resolve_scope_interval(scope)
        acquisition = operations.acquire_explicit(
            document,
            symbol,
            start,
            end,
            debug=debug,
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

def run_refresh(
    symbol: str,
    scope: str,
    cleartext: bool = False,
    debug: bool = False,
) -> int:
    if scope in {"latest", "next", "current"}:
        raise CalendarInputError(
            "refresh requires an explicit date, date range, datetime, or datetime range."
        )

    start, end = domain.resolve_scope_interval(scope)

    with storage.acquire_calendar_lock():
        if debug:
            print(f"DEBUG | Calendar file: {storage.CALENDAR_FILE}", file=sys.stderr)
        document = storage.load_calendar_document()
        result = operations.refresh_calendar_scope(
            document,
            symbol,
            start,
            end,
            debug=debug,
        )

        provider_statuses = [item["status"] for item in result["provider_results"]]
        if provider_statuses and all(status == "ERROR" for status in provider_statuses):
            status = "UNAVAILABLE"
        elif result["failures"]:
            status = "PARTIAL"
        elif result["summary"]["changed"] or result["summary"]["added"]:
            status = "REFRESHED"
        else:
            status = "UNCHANGED"

        if cleartext:
            presentation.output_query_result(
                status,
                symbol,
                result["events"],
                result["provider_results"],
                cleartext=True,
            )
            print(
                f"REFRESH | added={result['summary']['added']} "
                f"changed={result['summary']['changed']} "
                f"unchanged={result['summary']['unchanged']}"
            )
        else:
            print(json.dumps({
                "status": status,
                "symbol": symbol,
                "events": result["events"],
                "providers": result["provider_results"],
                "refresh": result["summary"],
            }, ensure_ascii=False))
        return 0 if status != "UNAVAILABLE" else 2

def run_delete(
    symbol: Optional[str],
    scope: Optional[str],
) -> int:
    # A bare DELETE is an explicit full-cache reset; it bypasses legacy-schema
    # validation so an incompatible calendar.json cannot block the reset.
    with storage.acquire_calendar_lock():
        if symbol is None and scope is None:
            save_calendar_atomic(build_empty_calendar_document())
        else:
            document = storage.load_calendar_document()
            if symbol is None or scope is None:
                raise CalendarInputError(
                    "Scoped delete requires DELETE + SYMBOL + SCOPE. "
                    "Use bare 'delete' only for full cache deletion."
                )
            if scope == "current":
                raise CalendarInputError(
                    "current cannot be used as a delete scope."
                )
            start, end = domain.resolve_scope_interval(scope)
            delete_symbol_interval(document, symbol, start, end)
            validate_calendar_document(document)
            save_calendar_atomic(document)

    print(json.dumps({
        "status": "OK",
        "operation": "DELETE",
        "symbol": symbol,
        "scope": scope,
    }))
    return 0

def parse_request(args: List[str]) -> Dict[str, Any]:
    if not args:
        raise CalendarInputError("No arguments provided. Use --help.")

    if len(args) == 1 and args[0] in {"-h", "--help"}:
        print(HELP_TEXT)
        raise SystemExit(0)

    if any(item in {"-h", "--help"} for item in args):
        raise CalendarInputError(
            "--help cannot be combined with other arguments."
        )

    cleartext = "--cleartext" in args
    debug = "--debug" in args
    positional = [
        item for item in args
        if item not in {"--cleartext", "--debug"}
    ]

    if not positional:
        raise CalendarInputError(
            "--cleartext requires a symbol query."
        )

    if positional[0] == "refresh":
        if len(positional) != 3:
            raise CalendarInputError(
                "Refresh requires REFRESH + SYMBOL + SCOPE."
            )
        symbol = domain.validate_symbol(positional[1])
        scope = domain.parse_scope(positional[2])
        if scope in {"latest", "next", "current"}:
            raise CalendarInputError(
                "refresh requires an explicit date, date range, datetime, or datetime range."
            )
        return {
            "operation": "REFRESH",
            "symbol": symbol,
            "scope": scope,
            "cleartext": cleartext,
            "debug": debug,
        }

    if positional[0] == "delete":
        if cleartext:
            raise CalendarInputError("--cleartext is not valid for delete.")

        if len(positional) == 1:
            return {
                "operation": "DELETE",
                "symbol": None,
                "scope": None,
                "cleartext": False,
                "debug": debug,
            }

        if len(positional) != 3:
            raise CalendarInputError(
                "Scoped delete requires DELETE + SYMBOL + SCOPE."
            )

        symbol = domain.validate_symbol(positional[1])
        scope = domain.parse_scope(positional[2])
        if scope == "current":
            raise CalendarInputError("current cannot be used as a delete scope.")

        return {
            "operation": "DELETE",
            "symbol": symbol,
            "scope": scope,
            "cleartext": False,
            "debug": debug,
        }
    if len(positional) != 2:
        raise CalendarInputError(
            "Expected exactly SYMBOL + SCOPE."
        )

    symbol = domain.validate_symbol(positional[0])
    scope = domain.parse_scope(positional[1])
    return {
        "operation": "QUERY",
        "symbol": symbol,
        "scope": scope,
        "cleartext": cleartext,
        "debug": debug,
    }

def run() -> int:
    debug = "--debug" in sys.argv[1:]
    try:
        request = parse_request(sys.argv[1:])
        debug = request["debug"]
        if request["operation"] == "DELETE":
            return operations.run_delete(
                request["symbol"],
                request["scope"],
            )
        if request["operation"] == "REFRESH":
            return run_refresh(
                request["symbol"],
                request["scope"],
                request["cleartext"],
                debug=debug,
            )
        return run_query(
            request["symbol"],
            request["scope"],
            request["cleartext"],
            debug=debug,
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

def main() -> None:
    raise SystemExit(run())

if __name__ == "__main__":
    main()
