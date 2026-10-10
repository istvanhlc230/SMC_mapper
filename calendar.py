# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""SMC_Mapper Calendar CLI entrypoint."""

# The executable is intentionally named calendar.py, which shadows Python's
# standard-library calendar module when this repository is on sys.path. Load
# the standard-library implementation under a private name and expose its
# public attributes so urllib/email and other stdlib modules remain compatible.
import importlib.util as _importlib_util
import sys as _sys
import sysconfig as _sysconfig
from pathlib import Path as _Path

_stdlib_calendar_path = _Path(_sysconfig.get_paths()["stdlib"]) / "calendar.py"
_stdlib_calendar_spec = _importlib_util.spec_from_file_location(
    "_smc_mapper_stdlib_calendar",
    _stdlib_calendar_path,
)
if _stdlib_calendar_spec is None or _stdlib_calendar_spec.loader is None:
    raise ImportError(
        f"Cannot load standard-library calendar module: {_stdlib_calendar_path}"
    )

_stdlib_calendar = _importlib_util.module_from_spec(_stdlib_calendar_spec)

# Register before execution: Python 3.14 enum.global_enum resolves the module
# through sys.modules while the standard-library calendar module is loading.
_sys.modules[_stdlib_calendar_spec.name] = _stdlib_calendar
_stdlib_calendar_spec.loader.exec_module(_stdlib_calendar)

# Re-export public standard-library names so imports still work despite this
# executable's filename shadowing the standard-library calendar module.
for _name in dir(_stdlib_calendar):
    if not _name.startswith("__"):
        globals().setdefault(_name, getattr(_stdlib_calendar, _name))

import traceback as _traceback

# Load the Calendar application API lazily. During stdlib import chains (for
# example urllib.request -> email -> calendar), eager imports here would cycle
# back into COMMON.http_client before HttpClient is defined.
_CALENDAR_API_NAMES = frozenset({
    "__version__",
    "SCHEMA_VERSION",
    "HELP_TEXT",
    "DATA_ROOT",
    "CALENDAR_FILE",
    "CalendarInputError",
    "ProviderError",
    "YahooForexPairUnavailable",
    "DataIntegrityError",
    "utc_now",
    "format_iso8601",
    "parse_iso8601",
    "normalize_symbol",
    "is_currency",
    "canonicalize_fx_token",
    "is_fx_pair",
    "is_ticker",
    "validate_symbol",
    "parse_time",
    "parse_date",
    "parse_point",
    "resolve_scope_interval",
    "is_open_start_scope",
    "is_open_end_scope",
    "resolve_open_start_scope",
    "resolve_open_end_scope",
    "parse_scope",
    "build_empty_calendar_document",
    "validate_calendar_document",
    "merge_events",
    "merge_coverage",
    "find_uncovered_intervals",
    "watermark_key",
    "resolve_applicable_providers",
    "filter_events_for_symbol",
    "filter_events_for_interval",
    "update_watermark",
    "query_current_events",
    "query_latest_event",
    "query_next_event",
    "status_from_provider_results",
    "filter_query_events",
    "_fetch_yahoo_search_payload",
    "_is_verified_yahoo_forex_quote",
    "_resolve_yahoo_instrument",
    "resolve_yahoo_symbol",
    "fetch_url",
    "_forexfactory_date_token",
    "build_forexfactory_query",
    "fetch_forexfactory",
    "_enrich_forexfactory_details",
    "fetch_forexfactory_event_detail",
    "normalize_provider_event",
    "normalize_calendar_events",
    "fetch_yahoo_news",
    "_normalize_forexfactory_impact_value",
    "_classify_forexfactory_impact",
    "ForexFactoryHTMLCalendarParser",
    "_extract_forexfactory_timezone",
    "_parse_forexfactory_date",
    "_parse_forexfactory_time",
    "parse_forexfactory_html_events",
    "extract_days_payload",
    "parse_calendar_days",
    "format_table_details",
    "render_ascii_table",
    "output_last_updates_table",
    "output_refresh_summary",
    "output_query_result",
    "acquire_explicit",
    "delete_symbol_interval",
    "refresh_current_scope",
    "_refresh_provider_window",
    "_refresh_event_records",
    "refresh_calendar_scope",
    "run_query",
    "run_delete",
    "parse_request",
    "run",
    "main",
})


def __getattr__(name):
    """Resolve Calendar application API attributes without eager import side effects."""
    if name not in _CALENDAR_API_NAMES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from CALENDAR import api as _calendar_api
    try:
        return getattr(_calendar_api, name)
    except AttributeError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc


def __dir__():
    """Include lazily exposed Calendar API names in module introspection."""
    return sorted(set(globals()) | set(_CALENDAR_API_NAMES))


# Preserve star-import compatibility while deferring Calendar API loading until
# an application-specific name is requested.
__all__ = sorted(
    {name for name in dir(_stdlib_calendar) if not name.startswith("__")}
    | set(_CALENDAR_API_NAMES)
    | {"run"}
)


def run() -> int:
    """Compatibility CLI runner used by legacy callers and integration tests."""
    debug = "--debug" in _sys.argv[1:]
    try:
        from CALENDAR import cli as _calendar_cli
        request = _calendar_cli.parse_request(_sys.argv[1:])
        return _calendar_cli.run_query(
            request["symbol"],
            request["scope"],
            request.get("table", False),
            debug=request.get("debug", debug),
            refresh=request.get("refresh", False),
        )
    except Exception as exc:
        print(f"Error: Internal error: {exc}", file=_sys.stderr)
        if debug:
            print("DEBUG | Unexpected exception traceback:", file=_sys.stderr)
            _traceback.print_exc()
        return 1

def main() -> int:
    """Run the Calendar CLI without eagerly importing it during stdlib module loading."""
    from CALENDAR.cli import execute_calendar_cli
    return execute_calendar_cli()


if __name__ == "__main__":
    raise SystemExit(main())
