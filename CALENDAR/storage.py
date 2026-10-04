"""Calendar persistence and cross-process synchronization."""

import contextlib
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

from .config import DataIntegrityError
from .domain import build_empty_calendar_document, validate_calendar_document

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = os.path.abspath(os.environ.get("SMC_DATA_ROOT", str(PROJECT_ROOT / "CALENDAR")))
CALENDAR_FILE = os.path.join(DATA_ROOT, "calendar.json")

def _load_json_file() -> Dict[str, Any]:
    if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:
        return build_empty_calendar_document()
    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataIntegrityError(f"Calendar data integrity error: {exc}") from exc

def load_calendar_document() -> Dict[str, Any]:
    document = _load_json_file()
    validate_calendar_document(document)
    return document

def save_calendar_atomic(document: Dict[str, Any]) -> None:
    os.makedirs(DATA_ROOT, exist_ok=True)
    temp_path = None
    fd = None
    try:
        fd, temp_path = tempfile.mkstemp(
            prefix="calendar_", suffix=".tmp", dir=DATA_ROOT
        )
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd = None
            json.dump(document, handle, indent=2, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, CALENDAR_FILE)
        temp_path = None
    except Exception as exc:
        raise DataIntegrityError(f"Atomic save failed: {exc}") from exc
    finally:
        if fd is not None:
            os.close(fd)
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@contextlib.contextmanager
def acquire_calendar_lock():
    """Serialize Calendar state access with a lock isolated by DATA_ROOT."""
    os.makedirs(DATA_ROOT, exist_ok=True)
    if os.name == "nt":
        import ctypes
        mutex_name = "SMC_Calendar_Lock_" + hashlib.sha256(
            os.path.abspath(CALENDAR_FILE).casefold().encode("utf-8")
        ).hexdigest()[:16]
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        mutex = kernel32.CreateMutexW(None, False, mutex_name)
        if not mutex:
            raise DataIntegrityError(
                f"Failed to create Calendar mutex: {ctypes.get_last_error()}"
            )
        result = kernel32.WaitForSingleObject(mutex, 0xFFFFFFFF)
        if result not in (0, 0x80):
            kernel32.CloseHandle(mutex)
            raise DataIntegrityError(f"Failed to acquire Calendar mutex: {result}")
        try:
            yield
        finally:
            kernel32.ReleaseMutex(mutex)
            kernel32.CloseHandle(mutex)
        return
    import fcntl
    lock_path = os.path.join(DATA_ROOT, ".calendar.lock")
    file_descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(file_descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(file_descriptor, fcntl.LOCK_UN)
        os.close(file_descriptor)
