# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""Calendar persistence and cross-process synchronization."""

import contextlib
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict

from .config import DataIntegrityError
from .domain import build_empty_calendar_document, normalize_calendar_document_provider_fields, validate_calendar_document
from COMMON.atomic_file import atomic_write_text

# PROJECT_ROOT — repository root used to derive the default Calendar data directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# DATA_ROOT — active runtime directory; SMC_DATA_ROOT overrides the repository-local default.
DATA_ROOT = os.path.abspath(os.environ.get("SMC_DATA_ROOT", str(PROJECT_ROOT / "CALENDAR")))
# CALENDAR_FILE — canonical persistent Calendar cache path for the active DATA_ROOT.
CALENDAR_FILE = os.path.join(DATA_ROOT, "calendar.json")

def _load_json_file() -> Dict[str, Any]:
    """Read the persisted Calendar JSON file or return a new empty document."""
    if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:
        return build_empty_calendar_document()
    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataIntegrityError(f"Calendar data integrity error: {exc}") from exc

def load_calendar_document() -> Dict[str, Any]:
    """Load, normalize legacy provider fields, and validate the Calendar document."""
    document = _load_json_file()
    normalize_calendar_document_provider_fields(document)
    validate_calendar_document(document)
    return document

def save_calendar_atomic(document: Dict[str, Any]) -> None:
    """Normalize provider fields, then atomically persist the Calendar JSON document."""
    try:
        normalize_calendar_document_provider_fields(document)
        serialized_document = json.dumps(document, indent=2, ensure_ascii=False)
        atomic_write_text(
            CALENDAR_FILE,
            serialized_document,
            prefix="calendar_",
            retry_limit=1,
        )
    except Exception as exc:
        raise DataIntegrityError(f"Atomic save failed: {exc}") from exc


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
