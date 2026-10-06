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


if __name__ == "__main__":
    main()
