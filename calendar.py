import sys
import os

if __name__ == "__main__":
    import calendar_layer
    calendar_layer.main()
else:
    _orig_path = list(sys.path)
    # Remove the directory containing this script from sys.path to find stdlib
    _my_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path = [p for p in sys.path if p not in ("", _my_dir)]
    
    try:
        import importlib
        importlib.invalidate_caches()
        import calendar as _stdlib_calendar
        sys.modules[__name__] = _stdlib_calendar
    finally:
        sys.path = _orig_path
