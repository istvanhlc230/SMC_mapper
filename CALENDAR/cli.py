# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""Calendar command-line entrypoint and request dispatch."""

import json
import sys
import traceback
from typing import Any, Dict, List, Optional

from . import domain, operations, presentation, storage
from .config import HELP_TEXT, CalendarInputError, DataIntegrityError

# CLI state is request-local: parsed arguments determine one operation and its diagnostic/presentation flags.

def _current_public_provider_results(
    provider_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return only non-diagnostic provider metadata for current output."""
    # Internal provider results are authoritative for status aggregation, but
    # network/provider exception details must never leak into normal stdout.
    public_results: List[Dict[str, Any]] = []
    # diagnostic_fields contains details intended exclusively for --debug stderr.
    diagnostic_fields = {"error", "reason", "detail_failures"}

    for provider_result in provider_results:
        # A failed provider is represented by the aggregate status only; its
        # individual ERROR record and diagnostics are intentionally suppressed.
        if provider_result.get("status") == "ERROR":
            continue
        public_results.append({
            key: value
            for key, value in provider_result.items()
            if key not in diagnostic_fields
        })

    return public_results

def run_query(
    symbol: str,
    scope: str,
    cleartext: bool = False,
    debug: bool = False,
) -> int:
    """Calendar operation: run_query performs the focused run query step in the Calendar implementation."""
    with storage.acquire_calendar_lock():
        document = storage.load_calendar_document()

        if scope == "current":
            result = operations.acquire_current(document, symbol, debug=debug)
            events = domain.filter_events_for_symbol(result["events"], symbol)
            status = domain.status_from_provider_results(result["provider_results"])
            if status == "OK" and not events:
                status = "NO_RELEVANT_EVENT"
            # Use complete internal provider results for status calculation, then
            # suppress provider-error diagnostics from the public current output.
            public_provider_results = _current_public_provider_results(
                result["provider_results"]
            )
            presentation.output_query_result(
                status,
                symbol,
                events,
                public_provider_results,
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

        if scope == "last-update":
            updates = domain.query_last_update(document, symbol)
            status = "OK" if any(item["last_successful_at"] for item in updates) else "NO_LAST_UPDATE"
            if cleartext:
                print(f"CALENDAR RESULT | {status} | {symbol}")
                for item in updates:
                    value = item["last_successful_at"] or "N/A"
                    print(f"PROVIDER | {item['provider']} | {value}")
            else:
                print(json.dumps({
                    "status": status,
                    "symbol": symbol,
                    "last_updates": updates,
                }, ensure_ascii=False))
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
    """Calendar operation: run_refresh performs the focused run refresh step in the Calendar implementation."""
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

        provider_status = domain.status_from_provider_results(
            result["provider_results"]
        )
        if provider_status == "UNAVAILABLE":
            status = "UNAVAILABLE"
        elif provider_status == "NO_FOREX_PAIR":
            # A refresh must preserve provider availability semantics instead of
            # collapsing a verified Yahoo FX-pair absence into UNCHANGED.
            status = "NO_FOREX_PAIR"
        elif provider_status in {"PARTIAL", "BOOTSTRAP_REQUIRED"}:
            status = provider_status if provider_status == "BOOTSTRAP_REQUIRED" else "PARTIAL"
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
    """Calendar operation: run_delete performs the focused run delete step in the Calendar implementation."""
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
            if scope == "current":
                raise CalendarInputError(
                    "current cannot be used as a delete scope."
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

def parse_request(args: List[str]) -> Dict[str, Any]:
    """Calendar operation: parse_request performs the focused parse request step in the Calendar implementation."""
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
    last_update = "--last-update" in args

    date_values = [item for item in args if item.startswith("--date=")]
    if "--date" in args:
        index = args.index("--date")
        if index + 1 >= len(args):
            raise CalendarInputError("--date requires YYYY.MM.DD.")
        date_values.append(f"--date={args[index + 1]}")
    if len(date_values) > 1:
        raise CalendarInputError("--date may be specified only once.")
    cli_date = date_values[0].split("=", 1)[1] if date_values else None

    # --time is a Calendar-compatible convenience form: when no date is
    # supplied, it resolves against the current UTC calendar day; when a
    # date-only scope is supplied, it is normalized to the existing
    # canonical YYYY.MM.DD@HH:MM form before normal scope parsing.
    time_values = [item for item in args if item.startswith("--time=")]
    if "--time" in args:
        index = args.index("--time")
        if index + 1 >= len(args):
            raise CalendarInputError("--time requires HH:MM.")
        time_values.append(f"--time={args[index + 1]}")
    if len(time_values) > 1:
        raise CalendarInputError("--time may be specified only once.")
    cli_time = None
    if time_values:
        cli_time = time_values[0].split("=", 1)[1]

    positional = []
    skip_next = False
    for index, item in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if item in {"--cleartext", "--debug", "--last-update"}:
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
            "--cleartext/--debug/--time/--date/--last-update requires a symbol query."
        )
    if last_update:
        if len(positional) != 1 or cli_date is not None or cli_time is not None:
            raise CalendarInputError("--last-update requires SYMBOL and cannot be combined with --date or --time.")
        return {
            "operation": "LAST_UPDATE",
            "symbol": domain.validate_symbol(positional[0]),
            "scope": None,
            "cleartext": cleartext,
            "debug": debug,
        }

    if positional[0] == "refresh":
        if len(positional) not in {2, 3}:
            raise CalendarInputError(
                "Refresh requires REFRESH + SYMBOL + SCOPE, or REFRESH + SYMBOL with --date/--time."
            )
        if cli_date is not None and len(positional) == 3:
            raise CalendarInputError("--date cannot be combined with an explicit refresh scope.")
        symbol = domain.validate_symbol(positional[1])
        if len(positional) == 2:
            if cli_date is not None:
                domain.parse_date(cli_date)
                scope = domain.parse_scope(f"{cli_date}@{cli_time}") if cli_time is not None else domain.parse_scope(cli_date)
            elif cli_time is not None:
                current_date = domain.utc_now().strftime("%Y.%m.%d")
                scope = domain.parse_scope(f"{current_date}@{cli_time}")
            else:
                raise CalendarInputError("Refresh requires an explicit scope or --date/--time.")
        else:
            if cli_time is not None:
                raise CalendarInputError(
                    "--time cannot be combined with an explicit refresh scope."
                )
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
            if cli_date is not None or cli_time is not None:
                raise CalendarInputError("--date/--time cannot be used with bare delete.")
            return {
                "operation": "DELETE",
                "symbol": None,
                "scope": None,
                "cleartext": False,
                "debug": debug,
            }

        if len(positional) not in {2, 3}:
            raise CalendarInputError(
                "Scoped delete requires DELETE + SYMBOL + SCOPE, or DELETE + SYMBOL with --date/--time."
            )
        if cli_date is not None and len(positional) == 3:
            raise CalendarInputError("--date cannot be combined with an explicit delete scope.")

        symbol = domain.validate_symbol(positional[1])
        if len(positional) == 2:
            if cli_date is not None:
                domain.parse_date(cli_date)
                scope = domain.parse_scope(f"{cli_date}@{cli_time}") if cli_time is not None else domain.parse_scope(cli_date)
            elif cli_time is not None:
                current_date = domain.utc_now().strftime("%Y.%m.%d")
                scope = domain.parse_scope(f"{current_date}@{cli_time}")
            else:
                raise CalendarInputError("Scoped delete requires an explicit scope or --date/--time.")
        else:
            if cli_time is not None:
                raise CalendarInputError(
                    "--time cannot be combined with an explicit delete scope."
                )
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
    if len(positional) not in {1, 2}:
        raise CalendarInputError(
            "Expected SYMBOL + SCOPE, or SYMBOL with --date/--time."
        )

    symbol = domain.validate_symbol(positional[0])
    if len(positional) == 1:
        if cli_date is not None:
            domain.parse_date(cli_date)
            scope = domain.parse_scope(f"{cli_date}@{cli_time}") if cli_time is not None else domain.parse_scope(cli_date)
        elif cli_time is not None:
            current_date = domain.utc_now().strftime("%Y.%m.%d")
            scope = domain.parse_scope(f"{current_date}@{cli_time}")
        else:
            raise CalendarInputError("Expected SYMBOL + SCOPE, or SYMBOL with --date/--time.")
    else:
        if cli_time is not None or cli_date is not None:
            raise CalendarInputError("--date/--time cannot be combined with an explicit query scope.")
        scope = domain.parse_scope(positional[1])
    return {
        "operation": "QUERY",
        "symbol": symbol,
        "scope": scope,
        "cleartext": cleartext,
        "debug": debug,
    }

def run() -> int:
    """Calendar operation: run performs the focused run step in the Calendar implementation."""
    debug = "--debug" in sys.argv[1:]
    try:
        request = parse_request(sys.argv[1:])
        debug = request["debug"]
        if request["operation"] == "DELETE":
            return run_delete(
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
    """Calendar operation: main performs the focused main step in the Calendar implementation."""
    raise SystemExit(run())

if __name__ == "__main__":
    main()
