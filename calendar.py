# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""SMC_Mapper Calendar CLI entrypoint."""

# The executable is intentionally named calendar.py, which shadows Python's
# standard-library calendar module when this repository is on sys.path. Load
# the standard-library implementation under a private name and expose its
# public attributes so urllib/email and other stdlib modules remain compatible.
import importlib.util as _importlib_util
import sysconfig as _sysconfig
from pathlib import Path as _Path

_stdlib_calendar_path = _Path(_sysconfig.get_paths()["stdlib"]) / "calendar.py"
_stdlib_calendar_spec = _importlib_util.spec_from_file_location(
    "_smc_mapper_stdlib_calendar",
    _stdlib_calendar_path,
)
_stdlib_calendar = _importlib_util.module_from_spec(_stdlib_calendar_spec)
_stdlib_calendar_spec.loader.exec_module(_stdlib_calendar)
for _name in dir(_stdlib_calendar):
    if not _name.startswith("__"):
        globals().setdefault(_name, getattr(_stdlib_calendar, _name))

from CALENDAR.api import *
import sys as _sys
import traceback as _traceback


def run() -> int:
    """Compatibility CLI runner used by legacy callers and integration tests."""
    debug = "--debug" in _sys.argv[1:]
    try:
        from CALENDAR import cli as _calendar_cli
        request = _calendar_cli.parse_request(_sys.argv[1:])
        return _calendar_cli.run_query(
            request["symbol"],
            request["scope"],
            request.get("cleartext", False),
            debug=request.get("debug", debug),
            refresh=request.get("refresh", False),
        )
    except Exception as exc:
        print(f"Error: Internal error: {exc}", file=_sys.stderr)
        if debug:
            print("DEBUG | Unexpected exception traceback:", file=_sys.stderr)
            _traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()
