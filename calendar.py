import contextlib
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import re
import sys
import tempfile
import traceback
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from html import unescape
from html.parser import HTMLParser
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any, Dict, List, Optional, Tuple

# DATA_ROOT — root directory for Calendar persistent data.
DATA_ROOT = os.environ.get("SMC_DATA_ROOT", ".")
# CALENDAR_FILE — path to persistent normalized calendar.json.
CALENDAR_FILE = os.path.join(DATA_ROOT, "calendar.json")
# FOREXFACTORY_URL — ForexFactory economic-calendar endpoint.
FOREXFACTORY_URL = "https://www.forexfactory.com/calendar"
# FOREXFACTORY_DETAIL_URL — provider event-detail JSON endpoint template.
FOREXFACTORY_DETAIL_URL = "https://www.forexfactory.com/calendar/details/1-{event_id}"
# YAHOO_SEARCH_URL — Yahoo Finance search endpoint.
YAHOO_SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"
# USER_AGENT — HTTP User-Agent sent to providers.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)
# HTTP_TIMEOUT — provider HTTP timeout in seconds.
HTTP_TIMEOUT = 15.0
# SCHEMA_VERSION — persistent calendar.json schema version.
SCHEMA_VERSION = 2
# __version__ — Calendar CLI implementation version, independent from SCHEMA_VERSION.
__version__ = "2.3.3"

# SUPPORTED_CURRENCIES — standalone currencies accepted by the CLI.
SUPPORTED_CURRENCIES = {
    "USD", "EUR", "GBP", "JPY", "CHF",
    "AUD", "CAD", "NZD", "CNY", "HUF",
    "HKD", "SGD", "INR", "MXN", "PHP", "IDR", "THB", "MYR",
    "ZAR", "RUB", "BRL", "NOK", "QAR",
}

# ISO 4217 alpha-3 currency codes are used to recognize a six-letter
# candidate as an FX pair. Yahoo remains authoritative for whether the
# concrete pair actually exists as a Forex instrument.
# FX_CURRENCY_CODES — currency-code universe used for six-letter FX recognition.
FX_CURRENCY_CODES = {
    "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
    "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV",
    "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF",
    "CHW", "CLF", "CLP", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE",
    "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "FJD",
    "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD",
    "HNL", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD",
    "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD",
    "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA",
    "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV",
    "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB",
    "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB",
    "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL",
    "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT",
    "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USN",
    "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAF",
    "XCD", "XOF", "XPF", "YER", "ZAR", "ZMW", "ZWG",
}

# USD_BASE_YAHOO_SYMBOLS — explicit USD-base Yahoo FX representations.
USD_BASE_YAHOO_SYMBOLS = {
    "USDJPY": "JPY=X",
    "USDCHF": "CHF=X",
    "USDCAD": "CAD=X",
    "USDCNY": "CNY=X",
    "USDHKD": "HKD=X",
    "USDSGD": "SGD=X",
    "USDINR": "INR=X",
    "USDMXN": "MXN=X",
    "USDPHP": "PHP=X",
    "USDIDR": "IDR=X",
    "USDTHB": "THB=X",
    "USDMYR": "MYR=X",
    "USDZAR": "ZAR=X",
    "USDRUB": "RUB=X",
}

# DATE_RE — canonical YYYY.MM.DD date expression.
DATE_RE = r"\d{4}\.\d{2}\.\d{2}"
# TIME_RE — canonical HH:MM time expression.
TIME_RE = r"\d{2}:\d{2}"

# HELP_TEXT — CLI help text containing software/schema versions.
HELP_TEXT = f"""Calendar CLI v{__version__} (schema {SCHEMA_VERSION}) - unified economic calendar and news update engine

USAGE
  python calendar.py SYMBOL YYYY.MM.DD
  python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD
  python calendar.py SYMBOL YYYY.MM.DD@HH:MM
  python calendar.py SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
  python calendar.py SYMBOL current
  python calendar.py SYMBOL latest
  python calendar.py SYMBOL next
  python calendar.py delete
  python calendar.py delete --debug
  python calendar.py delete SYMBOL YYYY.MM.DD
  python calendar.py delete SYMBOL YYYY.MM.DD-YYYY.MM.DD
  python calendar.py delete SYMBOL YYYY.MM.DD@HH:MM
  python calendar.py delete SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
  python calendar.py SYMBOL <scope> --cleartext
  python calendar.py SYMBOL <scope> --debug
  python calendar.py SYMBOL <scope> --cleartext --debug
  python calendar.py --help

FLAGS
  --cleartext  Human-readable presentation only; does not change data.
  --debug      Emit diagnostic exception/traceback output to stderr only.

SCOPE
  YYYY.MM.DD                         Exact UTC calendar day.
  YYYY.MM.DD-YYYY.MM.DD              Inclusive UTC date range.
  YYYY.MM.DD@HH:MM                   Exact UTC minute.
  YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM  Half-open UTC datetime range.
  current                             Incremental update from each
                                      provider+canonical-symbol watermark
                                      through current UTC time.
  latest                              Return the most recent past/current event for
                                      SYMBOL from the committed calendar cache.
  next                                Return the nearest future event for
                                      SYMBOL from the committed calendar cache.

SYMBOL
  Supported FX pair, standalone supported currency, or Yahoo ticker.
  Provider selection is automatic.

PROVIDERS
  ForexFactory -> primary economic-calendar events.
  Yahoo Finance -> complementary news.

CURRENT
  current is not "event at the current minute" and not "next".
  It loads each applicable provider+canonical-symbol watermark, performs
  incremental acquisition, normalizes/deduplicates, atomically persists,
  and returns events newer than the watermark through now.
  Missing watermark -> BOOTSTRAP_REQUIRED. No timestamp is fabricated.

LATEST
  latest is a read-only most-recent-event lookup.
  It reads only the committed calendar.json snapshot, filters events visible
  for SYMBOL, keeps only timestamps at or before current UTC time, selects the
  most recent event deterministically by timestamp, source, and event identity,
  and never calls a provider or changes persistent state.
  No past/current event -> NO_LATEST_EVENT.

NEXT
  next is a read-only nearest-future-event lookup.
  It reads only the committed calendar.json snapshot, filters events visible
  for SYMBOL, keeps only timestamps strictly later than current UTC time,
  sorts chronologically, and returns the first event.
  next never calls a provider, never changes coverage, and never changes
  watermarks. No future event -> NO_NEXT_EVENT.

OUTPUT
  Default output is JSON. --cleartext changes presentation only.

ERRORS
  Invalid syntax and unsupported symbols are rejected explicitly.
  Provider failures are never converted to successful empty data.
"""

# Class: CalendarInputError — invalid CLI or Calendar input.
class CalendarInputError(Exception):
    pass

# Class: ProviderError — external provider acquisition failure.
class ProviderError(Exception):
    pass


# Class: YahooForexPairUnavailable — Yahoo does not expose a verified Forex instrument.
class YahooForexPairUnavailable(Exception):
    pass


# Class: DataIntegrityError — persistent Calendar data integrity violation.
class DataIntegrityError(Exception):
    pass


# Function: utc_now — returns current UTC time.
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# Function: format_iso8601 — formats a datetime as UTC ISO-8601.
# Variables: value=input value.
def format_iso8601(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# Function: parse_iso8601 — parses and validates a UTC timestamp.
# Variables: value=input value.
# Local variables: exc=local intermediate value; normalized=normalized record; parsed=parsed datetime.
def parse_iso8601(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise DataIntegrityError(f"Invalid UTC timestamp '{value}'.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise DataIntegrityError(f"Non-UTC timestamp '{value}'.")
    return parsed.astimezone(timezone.utc)


# Function: normalize_symbol — normalizes a user symbol.
# Variables: value=input value.
def normalize_symbol(value: str) -> str:
    return value.strip().upper()


# Function: is_currency — checks standalone currency support.
# Variables: value=input value.
def is_currency(value: str) -> bool:
    return value in SUPPORTED_CURRENCIES


# Function: canonicalize_fx_token — canonicalizes an FX token.
# Variables: value=input value.
def canonicalize_fx_token(value: str) -> str:
    return re.sub(r"[/_-]", "", value.strip().upper())


# Function: is_fx_pair — checks six-letter FX-pair syntax.
# Variables: value=input value.
# Local variables: token=canonical token.
def is_fx_pair(value: str) -> bool:
    token = canonicalize_fx_token(value)
    return (
        len(token) == 6
        and token[:3] in FX_CURRENCY_CODES
        and token[3:] in FX_CURRENCY_CODES
    )


# Function: is_ticker — checks generic Yahoo ticker syntax.
# Variables: value=input value.
# Local variables: token=canonical token.
def is_ticker(value: str) -> bool:
    token = normalize_symbol(value)
    if is_currency(token) or is_fx_pair(token):
        return False
    return bool(re.fullmatch(r"[A-Z0-9][A-Z0-9._-]{0,14}", token))


# Function: validate_symbol — validates and canonicalizes a CLI symbol.
# Variables: value=input value.
# Local variables: token=canonical token.
def validate_symbol(value: str) -> str:
    token = canonicalize_fx_token(value)
    if is_currency(token):
        return token
    if (
        len(token) == 6
        and token[:3] in FX_CURRENCY_CODES
        and token[3:] in FX_CURRENCY_CODES
    ):
        return token
    if is_ticker(value):
        return normalize_symbol(value)
    raise CalendarInputError(
        f"Invalid calendar symbol '{value}'. Expected a supported currency, "
        "FX pair, or Yahoo Finance ticker."
    )


# Function: parse_time — parses HH:MM time.
# Variables: value=input value.
# Local variables: hour=hour component; minute=minute component; part=local intermediate value.
def parse_time(value: str) -> Tuple[int, int]:
    if not re.fullmatch(TIME_RE, value):
        raise CalendarInputError(f"Invalid time '{value}'. Expected HH:MM.")
    hour, minute = (int(part) for part in value.split(":"))
    if hour > 23 or minute > 59:
        raise CalendarInputError(f"Invalid time '{value}'. Expected HH:MM.")
    return hour, minute


# Function: parse_date — parses YYYY.MM.DD into UTC.
# Variables: value=input value.
# Local variables: day=calendar day; exc=local intermediate value; month=calendar month; part=local intermediate value; year=calendar year.
def parse_date(value: str) -> datetime:
    if not re.fullmatch(DATE_RE, value):
        raise CalendarInputError(
            f"Invalid date '{value}'. Expected YYYY.MM.DD."
        )
    try:
        year, month, day = (int(part) for part in value.split("."))
        return datetime(year, month, day, tzinfo=timezone.utc)
    except ValueError as exc:
        raise CalendarInputError(f"Invalid calendar date '{value}'.") from exc


# Function: parse_point — parses a date/datetime point.
# Variables: value=input value.
# Local variables: base=date base; date_part=date portion; hour=hour component; minute=minute component; time_part=time portion.
def parse_point(value: str) -> Tuple[datetime, bool]:
    if "@" not in value:
        return parse_date(value), False
    date_part, time_part = value.split("@", 1)
    base = parse_date(date_part)
    hour, minute = parse_time(time_part)
    return base.replace(hour=hour, minute=minute), True


# Function: resolve_scope_interval — resolves an explicit scope into a UTC interval.
# Variables: scope=CLI scope.
# Local variables: _=local intermediate value; end=interval end; end_date=local intermediate value; end_is_point=local intermediate value; parts=parsed scope parts; point=single datetime; start=interval start; start_is_point=local intermediate value.
def resolve_scope_interval(scope: str) -> Tuple[datetime, datetime]:
    if scope == "current":
        raise CalendarInputError("'current' is not a historical scope.")

    if "@" in scope:
        parts = scope.split("-", 1)
        if len(parts) == 2:
            start, start_is_point = parse_point(parts[0])
            end, end_is_point = parse_point(parts[1])
            if not start_is_point or not end_is_point or end <= start:
                raise CalendarInputError(
                    f"Invalid datetime range '{scope}'."
                )
            return start, end
        point, _ = parse_point(scope)
        return point, point + timedelta(minutes=1)

    if "-" in scope:
        parts = scope.split("-")
        if len(parts) != 2:
            raise CalendarInputError(
                f"Invalid date range '{scope}'."
            )
        start = parse_date(parts[0])
        end_date = parse_date(parts[1])
        if end_date < start:
            raise CalendarInputError(
                f"Invalid date range '{scope}': end must not precede start."
            )
        return start, end_date + timedelta(days=1)

    start = parse_date(scope)
    return start, start + timedelta(days=1)


# Function: parse_scope — classifies or validates a scope.
# Variables: scope=CLI scope.
def parse_scope(scope: str) -> str:
    if scope in {"current", "latest", "next"}:
        return scope
    resolve_scope_interval(scope)
    return scope


# Function: build_empty_calendar_document — builds a clean V2 Calendar document.
def build_empty_calendar_document() -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "events": [],
        "coverage": [],
        "watermarks": {},
    }


# Function: _load_json_file — loads raw Calendar JSON.
# Local variables: exc=local intermediate value; handle=local intermediate value.
def _load_json_file() -> Dict[str, Any]:
    if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:
        return build_empty_calendar_document()
    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataIntegrityError(f"Calendar data integrity error: {exc}") from exc


# Function: validate_calendar_document — validates the Calendar document.
# Variables: document=in-memory Calendar document.
# Local variables: coverage=local intermediate value; currency=currency code; event=normalized event; event_id=local intermediate value; field=local intermediate value; ids=event-ID set; impact=local intermediate value; item=current collection item; key=dictionary key; missing=local intermediate value; provider=provider identifier; required=local intermediate value; seen_coverage=validated coverage-ID set; suppressed_for=local intermediate value; symbol=canonical symbol; value=input value; watermark=provider/symbol watermark.
def validate_calendar_document(document: Dict[str, Any]) -> None:
    if not isinstance(document, dict):
        raise DataIntegrityError("Calendar document must be an object.")
    if document.get("schema_version") != SCHEMA_VERSION:
        raise DataIntegrityError("Unsupported calendar schema version.")
    if not isinstance(document.get("events"), list):
        raise DataIntegrityError("Invalid events collection.")
    if not isinstance(document.get("coverage"), list):
        raise DataIntegrityError("Invalid coverage collection.")
    if not isinstance(document.get("watermarks"), dict):
        raise DataIntegrityError("Invalid watermarks collection.")

    ids = set()
    for event in document["events"]:
        if not isinstance(event, dict):
            raise DataIntegrityError("Invalid event record.")
        required = {
            "event_id", "symbol", "asset_type", "event_type",
            "source", "timestamp", "title", "details",
        }
        missing = required.difference(event)
        if missing:
            raise DataIntegrityError(
                f"Corrupt event; missing {sorted(missing)}."
            )
        event_id = event["event_id"]
        if not isinstance(event_id, str) or not event_id:
            raise DataIntegrityError("Invalid event_id.")
        if event_id in ids:
            raise DataIntegrityError("Duplicate event_id.")
        ids.add(event_id)
        if event["event_type"] not in {
            "economic", "news", "earnings", "press_release", "sec_filing"
        }:
            raise DataIntegrityError("Invalid event_type.")
        if event["source"] not in {"forexfactory", "yahoo_finance"}:
            raise DataIntegrityError("Invalid event source.")
        if event["asset_type"] not in {"forex", "ticker"}:
            raise DataIntegrityError("Invalid asset_type.")
        if not isinstance(event["symbol"], str) or not event["symbol"]:
            raise DataIntegrityError("Invalid event symbol.")
        suppressed_for = event.get("suppressed_for", [])
        if not isinstance(suppressed_for, list) or any(
            not isinstance(item, str) or not item
            for item in suppressed_for
        ):
            raise DataIntegrityError("Invalid suppressed_for metadata.")
        if len(set(suppressed_for)) != len(suppressed_for):
            raise DataIntegrityError("Duplicate suppressed_for symbol.")
        if not isinstance(event["title"], str) or not event["title"].strip():
            raise DataIntegrityError("Event title must not be empty.")
        if not isinstance(event["details"], dict):
            raise DataIntegrityError("Event details must be an object.")
        parse_iso8601(event["timestamp"])

        if event["source"] == "forexfactory":
            if event["event_type"] != "economic":
                raise DataIntegrityError(
                    "ForexFactory events must use event_type=economic."
                )
            currency = event["details"].get("currency")
            if currency not in FX_CURRENCY_CODES and currency != "ALL":
                raise DataIntegrityError("Invalid ForexFactory currency.")
            impact = event["details"].get("impact")
            if impact not in {"HIGH", "MEDIUM", "LOW", "HOLIDAY", "UNKNOWN"}:
                raise DataIntegrityError("Invalid ForexFactory impact.")
            specs = event["details"].get("specs", [])
            if not isinstance(specs, list):
                raise DataIntegrityError("Invalid ForexFactory specs.")
            for spec in specs:
                if not isinstance(spec, dict):
                    raise DataIntegrityError("Invalid ForexFactory detail spec.")
                if set(spec) != {"order", "title", "html"}:
                    raise DataIntegrityError("Invalid ForexFactory detail spec fields.")
                if isinstance(spec["order"], bool):
                    raise DataIntegrityError("Invalid ForexFactory detail spec order.")
                try:
                    int(spec["order"])
                except (TypeError, ValueError) as exc:
                    raise DataIntegrityError("Invalid ForexFactory detail spec order.") from exc
                if not isinstance(spec["title"], str) or not spec["title"].strip():
                    raise DataIntegrityError("ForexFactory detail spec title must not be empty.")
                if not isinstance(spec["html"], str):
                    raise DataIntegrityError("ForexFactory detail spec html must be a string.")

        if event["source"] == "yahoo_finance":
            if event["event_type"] != "news":
                raise DataIntegrityError(
                    "Yahoo Finance events must use event_type=news."
                )

    seen_coverage = set()
    for coverage in document["coverage"]:
        if not isinstance(coverage, dict):
            raise DataIntegrityError("Invalid coverage record.")
        for field in ("provider", "symbol", "start", "end", "status"):
            if field not in coverage:
                raise DataIntegrityError(
                    f"Malformed coverage; missing '{field}'."
                )
        if coverage["provider"] not in {"forexfactory", "yahoo_finance"}:
            raise DataIntegrityError("Invalid coverage provider.")
        parse_iso8601(coverage["start"])
        parse_iso8601(coverage["end"])
        if parse_iso8601(coverage["end"]) <= parse_iso8601(coverage["start"]):
            raise DataIntegrityError("Invalid coverage interval.")
        if coverage["status"] not in {"COMPLETE", "PARTIAL"}:
            raise DataIntegrityError("Invalid coverage status.")
        key = (
            coverage["provider"],
            coverage["symbol"],
            coverage["start"],
            coverage["end"],
        )
        if key in seen_coverage:
            raise DataIntegrityError("Duplicate coverage entry.")
        seen_coverage.add(key)

    for key, watermark in document["watermarks"].items():
        if not isinstance(watermark, dict):
            raise DataIntegrityError("Invalid watermark record.")
        if "|" not in key:
            raise DataIntegrityError("Invalid watermark key.")
        provider, symbol = key.split("|", 1)
        if provider not in {"forexfactory", "yahoo_finance"} or not symbol:
            raise DataIntegrityError("Invalid watermark identity.")
        for field in ("last_successful_at", "last_event_timestamp"):
            if field not in watermark:
                raise DataIntegrityError(
                    f"Malformed watermark; missing '{field}'."
                )
            value = watermark[field]
            if value is not None:
                parse_iso8601(value)


# Function: load_calendar_document — loads and validates Calendar state.
# Local variables: document=in-memory Calendar document.
def load_calendar_document() -> Dict[str, Any]:
    document = _load_json_file()
    validate_calendar_document(document)
    return document


# Function: save_calendar_atomic — atomically persists Calendar state.
# Variables: document=in-memory Calendar document.
# Local variables: exc=local intermediate value; fd=temporary file descriptor; handle=local intermediate value; prefix=local intermediate value; temp_path=temporary file path.
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
# Function: acquire_calendar_lock — serializes Calendar access.
# Local variables: fd=temporary file descriptor; kernel32=local intermediate value; lock_path=POSIX lock-file path; mutex=Windows mutex handle; result=computed result.
def acquire_calendar_lock():
    os.makedirs(DATA_ROOT, exist_ok=True)
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        mutex = kernel32.CreateMutexW(None, False, "SMC_Calendar_Lock")
        if not mutex:
            raise DataIntegrityError(
                f"Failed to create Calendar mutex: {ctypes.get_last_error()}"
            )
        result = kernel32.WaitForSingleObject(mutex, 0xFFFFFFFF)
        if result not in (0, 0x80):
            kernel32.CloseHandle(mutex)
            raise DataIntegrityError(
                f"Failed to acquire Calendar mutex: {result}"
            )
        try:
            yield
        finally:
            kernel32.ReleaseMutex(mutex)
            kernel32.CloseHandle(mutex)
        return

    import fcntl

    lock_path = os.path.join(DATA_ROOT, ".calendar.lock")
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


# Function: merge_events — merges provider events by identity.
# Variables: document=in-memory Calendar document; new_events=incoming events; clear_suppressed_symbol=local intermediate value.
# Local variables: by_id=local intermediate value; event=normalized event; incoming=incoming suppression metadata; inherited=previous suppression metadata; key=dictionary key; normalized=normalized record; old=previous record; suppressed=combined suppression metadata.
def merge_events(
    document: Dict[str, Any],
    new_events: List[Dict[str, Any]],
    clear_suppressed_symbol: Optional[str] = None,
) -> None:
    by_id = {event["event_id"]: event for event in document["events"]}
    for event in new_events:
        old = by_id.get(event["event_id"])
        if old is not None and old["timestamp"] != event["timestamp"]:
            raise DataIntegrityError(
                f"Provider identity/time conflict for {event['event_id']}."
            )

        normalized = event.copy()
        inherited = set(old.get("suppressed_for", [])) if old else set()
        incoming = set(normalized.get("suppressed_for", []))
        suppressed = inherited | incoming
        if clear_suppressed_symbol is not None:
            suppressed.discard(clear_suppressed_symbol)
        if suppressed:
            normalized["suppressed_for"] = sorted(suppressed)
        else:
            normalized.pop("suppressed_for", None)
        by_id[event["event_id"]] = normalized

    document["events"] = sorted(
        by_id.values(),
        key=lambda item: (
            parse_iso8601(item["timestamp"]),
            item["source"],
            item["event_id"],
        ),
    )

# Function: merge_coverage — merges coverage intervals.
# Variables: document=in-memory Calendar document; item=current collection item.
# Local variables: candidates=candidate provider records; coverage=local intermediate value; current=local intermediate value; key=dictionary key; previous=local intermediate value; same_scope=local intermediate value.
def merge_coverage(document: Dict[str, Any], item: Dict[str, Any]) -> None:
    candidates = [coverage.copy() for coverage in document["coverage"]]
    candidates.append(item.copy())
    candidates.sort(
        key=lambda coverage: (
            coverage["provider"], coverage["symbol"],
            parse_iso8601(coverage["start"]),
        )
    )
    merged: List[Dict[str, Any]] = []
    for current in candidates:
        if not merged:
            merged.append(current)
            continue
        previous = merged[-1]
        same_scope = (
            previous["provider"] == current["provider"]
            and previous["symbol"] == current["symbol"]
        )
        if same_scope and parse_iso8601(current["start"]) <= parse_iso8601(previous["end"]):
            previous["end"] = format_iso8601(max(
                parse_iso8601(previous["end"]),
                parse_iso8601(current["end"]),
            ))
            if current["status"] == "PARTIAL":
                previous["status"] = "PARTIAL"
            continue
        merged.append(current)
    document["coverage"] = merged


# Function: find_uncovered_intervals — computes missing complete coverage segments.
# Variables: document=in-memory Calendar document; provider=provider identifier; symbol=canonical symbol; start=interval start; end=interval end.
# Local variables: complete_intervals=local intermediate value; coverage=local intermediate value; coverage_end=existing coverage end; coverage_start=existing coverage start; cursor=provider cursor.
def find_uncovered_intervals(
    document: Dict[str, Any],
    provider: str,
    symbol: str,
    start: datetime,
    end: datetime,
) -> List[Tuple[datetime, datetime]]:
    if end <= start:
        raise CalendarInputError("Coverage interval must have end after start.")

    complete_intervals = []
    for coverage in document["coverage"]:
        if (
            coverage["provider"] != provider
            or coverage["symbol"] != symbol
            or coverage["status"] != "COMPLETE"
        ):
            continue

        coverage_start = parse_iso8601(coverage["start"])
        coverage_end = parse_iso8601(coverage["end"])
        if coverage_end <= start or coverage_start >= end:
            continue

        overlap_start = max(start, coverage_start)
        overlap_end = min(end, coverage_end)

        # Existing 2.2.x ForexFactory events predate Detail specs. Treat the
        # covered interval as incomplete until its events are Detail-enriched.
        if provider == "forexfactory":
            legacy_detail_needed = any(
                event["source"] == "forexfactory"
                and overlap_start <= parse_iso8601(event["timestamp"]) < overlap_end
                and "specs" not in event["details"]
                for event in document["events"]
            )
            if legacy_detail_needed:
                continue

        complete_intervals.append(
            (
                overlap_start,
                overlap_end,
            )
        )

    complete_intervals.sort(key=lambda interval: interval[0])

    gaps: List[Tuple[datetime, datetime]] = []
    cursor = start
    for coverage_start, coverage_end in complete_intervals:
        if coverage_start > cursor:
            gaps.append((cursor, coverage_start))
        if coverage_end > cursor:
            cursor = coverage_end
        if cursor >= end:
            break

    if cursor < end:
        gaps.append((cursor, end))

    return gaps


# Function: watermark_key — builds watermark identity.
# Variables: provider=provider identifier; symbol=canonical symbol.
def watermark_key(provider: str, symbol: str) -> str:
    return f"{provider}|{symbol}"


# Function: resolve_applicable_providers — selects providers for a symbol.
# Variables: symbol=canonical symbol.
def resolve_applicable_providers(symbol: str) -> List[str]:
    if is_currency(symbol):
        return ["forexfactory"]
    if is_fx_pair(symbol):
        return ["forexfactory", "yahoo_finance"]
    return ["yahoo_finance"]


# Function: _fetch_yahoo_search_payload — fetches Yahoo search payload.
# Variables: query_symbol=local intermediate value.
# Local variables: data=local intermediate value; exc=local intermediate value; params=HTTP query parameters; payload=provider payload; query=provider query symbol.
def _fetch_yahoo_search_payload(query_symbol: str) -> Dict[str, Any]:
    params = {
        "q": query_symbol,
        "quotesCount": "20",
        "newsCount": "100",
        "enableFuzzyQuery": "false",
    }
    query = urllib.parse.urlencode(params)
    payload = fetch_url(f"{YAHOO_SEARCH_URL}?{query}")
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"Malformed Yahoo Finance JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ProviderError("Yahoo Finance response is not an object.")
    return data


# Function: _is_verified_yahoo_forex_quote — verifies a Yahoo Forex quote.
# Variables: quote=local intermediate value; candidate_symbol=local intermediate value.
# Local variables: quote_type=provider classification; returned_symbol=provider-returned symbol; type_display=provider display classification.
def _is_verified_yahoo_forex_quote(
    quote: Dict[str, Any],
    candidate_symbol: str,
) -> bool:
    returned_symbol = normalize_symbol(str(quote.get("symbol", "")))
    quote_type = normalize_symbol(str(quote.get("quoteType", "")))
    type_display = str(quote.get("typeDisp", "")).strip().lower()
    return (
        returned_symbol == normalize_symbol(candidate_symbol)
        and (
            quote_type == "CURRENCY"
            or type_display == "currency"
        )
    )


# Function: _resolve_yahoo_instrument — resolves a Yahoo FX instrument.
# Variables: symbol=canonical symbol.
# Local variables: candidate=local intermediate value; data=local intermediate value; derived_usd_base=local intermediate value; direct=direct candidate; mapped=mapped candidate; query_symbol=local intermediate value; quote=local intermediate value; quotes=local intermediate value.
def _resolve_yahoo_instrument(
    symbol: str,
) -> Tuple[str, Dict[str, Any]]:
    if not is_fx_pair(symbol):
        return symbol, _fetch_yahoo_search_payload(symbol)

    candidates: List[str] = []
    mapped = USD_BASE_YAHOO_SYMBOLS.get(symbol)
    if mapped:
        candidates.append(mapped)

    # Yahoo commonly represents USD-base FX pairs as the quote currency's
    # =X instrument (for example GBP=X for USDGBP). This is only a
    # provider candidate; it must still be verified by Yahoo Search.
    if symbol.startswith("USD") and len(symbol) == 6:
        derived_usd_base = f"{symbol[3:]}=X"
        if derived_usd_base not in candidates:
            candidates.append(derived_usd_base)

    direct = f"{symbol}=X"
    if direct not in candidates:
        candidates.append(direct)

    queried: set[str] = set()
    for candidate in candidates:
        for query_symbol in (candidate, symbol):
            if query_symbol in queried:
                continue
            queried.add(query_symbol)
            data = _fetch_yahoo_search_payload(query_symbol)
            quotes = data.get("quotes", [])
            if not isinstance(quotes, list):
                continue
            for quote in quotes:
                if not isinstance(quote, dict):
                    continue
                if _is_verified_yahoo_forex_quote(quote, candidate):
                    return candidate, data

    raise YahooForexPairUnavailable(
        f"Yahoo Finance has no verified Forex instrument for '{symbol}'."
    )


# Function: resolve_yahoo_symbol — returns verified Yahoo symbol.
# Variables: symbol=canonical symbol.
# Local variables: _=local intermediate value; provider_symbol=verified provider symbol.
def resolve_yahoo_symbol(symbol: str) -> Optional[str]:
    try:
        provider_symbol, _ = _resolve_yahoo_instrument(symbol)
    except YahooForexPairUnavailable:
        return None
    return provider_symbol


# Function: fetch_url — performs an HTTP GET.
# Variables: url=local intermediate value.
# Local variables: exc=local intermediate value; headers=local intermediate value; request=parsed CLI request; response=provider response.
def fetch_url(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            if response.status != 200:
                raise ProviderError(f"HTTP {response.status}")
            return response.read().decode("utf-8")
    except Exception as exc:
        raise ProviderError(str(exc)) from exc


# Function: _forexfactory_date_token — formats a provider date token without zero-padding the day.
# Variables: value=UTC date value.
# Local variables: month=lowercase abbreviated month; day=calendar day; year=calendar year.
def _forexfactory_date_token(value: datetime) -> str:
    month = value.strftime("%b").lower()
    day = value.day
    year = value.year
    return f"{month}{day}.{year}"


# Function: build_forexfactory_query — selects the native ForexFactory query form for an interval.
# Variables: start=request/provider interval start; end=request/provider interval end.
# Local variables: query=provider query parameters; first_day=first calendar day; last_day=last calendar day.
def build_forexfactory_query(start: datetime, end: datetime) -> str:
    if end <= start:
        raise CalendarInputError("ForexFactory query interval must have a positive duration.")

    first_day = start.replace(hour=0, minute=0, second=0, microsecond=0)
    last_day = (end - timedelta(microseconds=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    if first_day == last_day:
        query = {"day": _forexfactory_date_token(first_day)}
    else:
        query = {
            "range": (
                f"{_forexfactory_date_token(first_day)}-"
                f"{_forexfactory_date_token(last_day)}"
            )
        }
    return urllib.parse.urlencode(query)


# Function: fetch_forexfactory — fetches FF calendar data.
# Variables: start=interval start; end=interval end.
# Local variables: days=provider calendar days; end_token=local intermediate value; event=normalized event; hour=hour component; html=provider HTML; last_day=last processed day; normalized=normalized record; provider_end=provider interval end; provider_start=provider interval start; query=provider query symbol; request_end=requested interval end; request_start=requested interval start; start_token=local intermediate value.
# Function: fetch_forexfactory — fetches FF calendar data using structured payload or current HTML rows.
# Variables: start=interval start; end=interval end.
# Local variables: request_start=requested start; request_end=requested end; provider_start=provider day start; provider_end=provider day end; last_day=last provider day; start_token=range-start token; end_token=range-end token; query=provider query parameters; html=provider HTML; days=legacy structured days; normalized=canonical events; fallback_raw=HTML-derived raw events.
def fetch_forexfactory(
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
    request_start = start
    request_end = end
    provider_start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    provider_end = end.replace(hour=0, minute=0, second=0, microsecond=0)
    if provider_end < end:
        provider_end += timedelta(days=1)
    query = build_forexfactory_query(provider_start, provider_end)
    html = fetch_url(f"{FOREXFACTORY_URL}?{query}")
    try:
        days = parse_calendar_days(extract_days_payload(html))
        normalized = normalize_calendar_events(days)
    except ProviderError:
        fallback_raw = parse_forexfactory_html_events(
            html,
            request_start,
            request_end,
        )
        normalized = [
            normalize_provider_event(raw_event)
            for raw_event in fallback_raw
        ]

    normalized = [
        event for event in normalized
        if request_start <= parse_iso8601(event["timestamp"]) < request_end
    ]

    # ForexFactory Detail is provider data, not a canonical event URL.
    # It is acquired separately by numeric provider event ID after the calendar
    # event set is normalized and interval-filtered. Detail requests are
    # intentionally bounded-parallel to avoid N sequential network round-trips;
    # results are assigned back in normalized event order.
    def fetch_detail(event: Dict[str, Any]) -> List[Dict[str, Any]]:
        provider_event_id = event["event_id"].split(":", 1)[1]
        return fetch_forexfactory_event_detail(provider_event_id)

    if normalized:
        max_workers = min(6, len(normalized))
        with ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="ff-detail",
        ) as executor:
            detail_specs = list(executor.map(fetch_detail, normalized))

        for event, specs in zip(normalized, detail_specs):
            event["details"]["specs"] = specs

    return normalized


# Function: _normalize_forexfactory_impact_value — normalizes provider impact text to a canonical token.
# Variables: value=provider impact text.
# Local variables: lowered=lowercase provider text.
def _normalize_forexfactory_impact_value(value: str) -> str:
    lowered = value.strip().lower()
    if "high" in lowered:
        return "high"
    if "medium" in lowered or lowered.startswith("med"):
        return "medium"
    if "low" in lowered:
        return "low"
    if "non-economic" in lowered or "holiday" in lowered:
        return "holiday"
    return ""


# Function: _classify_forexfactory_impact — classifies FF impact from CSS classes.
# Variables: classes=HTML element CSS classes.
# Local variables: class_name=current CSS class.
def _classify_forexfactory_impact(classes: set[str]) -> str:
    for class_name in classes:
        lowered = class_name.lower()
        if lowered.endswith("--high") or lowered in {"high", "icon--ff-impact-red"}:
            return "high"
        if lowered.endswith("--medium") or lowered in {
            "medium", "med", "icon--ff-impact-orange", "icon--ff-impact-ora"
        }:
            return "medium"
        if lowered.endswith("--low") or lowered in {
            "low",
            "icon--ff-impact-yellow",
            "icon--ff-impact-yel",
            "icon--ff-impact-green",
            "icon--ff-impact-grn",
        }:
            return "low"
        if lowered in {
            "holiday",
            "non-economic",
            "icon--ff-impact-grey",
            "icon--ff-impact-gray",
            "icon--ff-impact-gry",
        }:
            return "holiday"
    return ""


# Class: ForexFactoryHTMLCalendarParser — parses current rendered ForexFactory calendar rows.
class ForexFactoryHTMLCalendarParser(HTMLParser):
    # Function: __init__ — initializes parser state.
    # Variables: none.
    # Local state: rows=completed provider rows; current_row=active provider row; current_cell=active cell classes; text_buffer=active cell text; capture_title=event-title flag; last_date_text=latest date; last_time_text=latest numeric time.
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: List[Dict[str, Any]] = []
        self.current_row: Optional[Dict[str, Any]] = None
        self.current_cell: Optional[str] = None
        self.text_buffer: List[str] = []
        self.capture_title = False
        self.last_date_text = ""
        self.last_time_text = ""

    # Function: handle_starttag — processes opening tags belonging to a calendar row.
    # Variables: tag=HTML tag; attrs=attribute pairs.
    # Local variables: attributes=attribute map; classes=CSS classes; event_id=provider event ID; impact_title=impact metadata.
    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attributes = dict(attrs)
        classes = set(str(attributes.get("class") or "").split())

        if tag == "tr":
            event_id = (
                attributes.get("data-eventid")
                or attributes.get("data-event-id")
                or attributes.get("data-eid")
            )
            is_calendar_row = (
                "calendar__row" in classes
                or "calendar_row" in classes
            )
            # The provider event-instance ID is the stable row anchor. Current
            # CSS row classes are advisory because ForexFactory may change them.
            if event_id or is_calendar_row:
                self.current_row = {
                    "id": event_id,
                    "date": "",
                    "time": "",
                    "currency": "",
                    "impact": "",
                    "title": "",
                    "actual": "",
                    "forecast": "",
                    "previous": "",
                }
                self.current_cell = None
                self.text_buffer = []
                return

        if self.current_row is None:
            return

        if tag == "td":
            self.current_cell = " ".join(classes)
            if "calendar__impact" in self.current_cell:
                impact = _classify_forexfactory_impact(classes)
                if impact:
                    self.current_row["impact"] = impact
            self.text_buffer = []
            return

        if tag == "span" and "calendar__event-title" in classes:
            self.capture_title = True
            self.text_buffer = []

        if tag == "span" and self.current_cell and "calendar__impact" in self.current_cell:
            impact_title = str(attributes.get("title") or "").strip()
            if impact_title:
                normalized_title = _normalize_forexfactory_impact_value(impact_title)
                if normalized_title:
                    self.current_row["impact"] = normalized_title
            impact = _classify_forexfactory_impact(classes)
            if impact:
                self.current_row["impact"] = impact

    # Function: handle_endtag — finalizes cells and complete rows.
    # Variables: tag=HTML tag; no external arguments beyond parser state.
    # Local variables: cell_text=normalized cell text; row=completed row; date_text=visible date; time_text=visible time.
    def handle_endtag(self, tag: str) -> None:
        if self.current_row is None:
            return

        if tag == "span" and self.capture_title:
            self.current_row["title"] = " ".join(self.text_buffer).strip()
            self.capture_title = False
            return

        if tag == "td":
            cell_text = " ".join(self.text_buffer).strip()
            if self.current_cell:
                if "calendar__date" in self.current_cell:
                    self.current_row["date"] = cell_text
                elif "calendar__time" in self.current_cell:
                    self.current_row["time"] = cell_text
                elif "calendar__currency" in self.current_cell:
                    self.current_row["currency"] = cell_text
                elif "calendar__actual" in self.current_cell:
                    self.current_row["actual"] = cell_text
                elif "calendar__forecast" in self.current_cell:
                    self.current_row["forecast"] = cell_text
                elif "calendar__previous" in self.current_cell:
                    self.current_row["previous"] = cell_text
            self.current_cell = None
            self.text_buffer = []
            return

        if tag == "tr":
            row = self.current_row
            self.current_row = None
            self.current_cell = None
            self.text_buffer = []
            date_text = str(row.get("date") or "").strip()
            time_text = str(row.get("time") or "").strip()
            if date_text:
                self.last_date_text = date_text
            else:
                row["date"] = self.last_date_text
            if time_text and re.search(r"\d{1,2}:\d{2}\s*(?:am|pm)", time_text, re.IGNORECASE):
                self.last_time_text = time_text
            elif not time_text:
                row["time"] = self.last_time_text
            self.rows.append(row)

    # Function: handle_data — captures text inside the active calendar cell.
    # Variables: data=HTML text fragment.
    def handle_data(self, data: str) -> None:
        if self.current_row is not None:
            self.text_buffer.append(data)


# Function: _extract_forexfactory_timezone — extracts the provider-declared Calendar Time Zone.
# Variables: html=provider HTML.
# Local variables: match=timezone declaration; timezone_name=IANA timezone name; offset_match=GMT offset fallback; sign=offset sign; hours=offset hours; minutes=offset minutes.
def _extract_forexfactory_timezone(html: str) -> timezone:
    match = re.search(
        r"Calendar\s+Time\s+Zone:\s*([A-Za-z_]+(?:/[A-Za-z0-9_.+-]+)+)",
        html,
        re.IGNORECASE,
    )
    if not match:
        raise ProviderError("ForexFactory response has no calendar timezone declaration.")

    timezone_name = match.group(1)
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        offset_match = re.search(
            r"Calendar\s+Time\s+Zone:.*?\(GMT\s*([+-])(\d{1,2})(?::(\d{2}))?\)",
            html,
            re.IGNORECASE | re.DOTALL,
        )
        if not offset_match:
            raise ProviderError(
                f"Unsupported ForexFactory calendar timezone '{timezone_name}'."
            )
        sign = 1 if offset_match.group(1) == "+" else -1
        hours = int(offset_match.group(2))
        minutes = int(offset_match.group(3) or "0")
        return timezone(sign * timedelta(hours=hours, minutes=minutes))


# Function: _parse_forexfactory_date — resolves a rendered FF date to a concrete date.
# Variables: date_text=rendered date; reference_start=request start; reference_end=request end.
# Local variables: cleaned=normalized text; match=date match; month_text=month token; day_text=day token; candidates=candidate dates; year=candidate year; parsed=parsed candidate.
def _parse_forexfactory_date(
    date_text: str,
    reference_start: datetime,
    reference_end: datetime,
) -> datetime:
    cleaned = " ".join(date_text.split())
    match = re.search(
        r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})",
        cleaned,
    )
    if not match:
        raise ProviderError(f"Invalid ForexFactory event date '{date_text}'.")

    month_text = match.group(1)
    day_text = match.group(2)
    month_numbers = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }
    month_number = month_numbers.get(month_text.title())
    if month_number is None:
        raise ProviderError(f"Invalid ForexFactory event month '{month_text}'.")
    day_number = int(day_text)
    candidates: List[datetime] = []
    for year in range(reference_start.year - 1, reference_end.year + 2):
        try:
            parsed = datetime(
                year,
                month_number,
                day_number,
                tzinfo=timezone.utc,
            )
        except ValueError:
            continue
        candidates.append(parsed)

    in_window = [
        candidate
        for candidate in candidates
        if reference_start.date() <= candidate.date() <= reference_end.date()
    ]
    if in_window:
        return min(in_window, key=lambda item: abs(item - reference_start))
    if not candidates:
        raise ProviderError(f"Unable to resolve ForexFactory event date '{date_text}'.")
    return min(candidates, key=lambda item: abs(item - reference_start))


# Function: _parse_forexfactory_time — resolves a rendered FF clock.
# Variables: time_text=rendered time text.
# Local variables: cleaned=normalized time; match=time match; hour=24-hour hour; minute=minute component.
def _parse_forexfactory_time(time_text: str) -> Tuple[int, int]:
    cleaned = " ".join(time_text.split()).lower()
    match = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm)", cleaned)
    if not match:
        return 0, 0

    hour = int(match.group(1))
    minute = int(match.group(2))
    if match.group(3) == "pm" and hour < 12:
        hour += 12
    if match.group(3) == "am" and hour == 12:
        hour = 0
    return hour, minute


# Function: parse_forexfactory_html_events — converts rendered FF HTML rows to provider-shaped events.
# Variables: html=provider HTML; start=request start; end=request end.
# Local variables: parser=HTML parser; timezone_info=provider timezone; normalized_events=provider-shaped events; row=parsed row; event_id=provider ID; currency=currency; title=title; event_date=resolved date; hour=event hour; minute=event minute; local_datetime=timezone-aware datetime; raw_event=provider-shaped record.
def parse_forexfactory_html_events(
    html: str,
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
    parser = ForexFactoryHTMLCalendarParser()
    parser.feed(html)
    parser.close()

    timezone_info = _extract_forexfactory_timezone(html)
    normalized_events: List[Dict[str, Any]] = []

    for row in parser.rows:
        currency = str(row.get("currency") or "").strip().upper()
        title = str(row.get("title") or "").strip()

        # Structural/helper rows may share the calendar-row CSS class but are not
        # economic event records. Ignore rows without an event title before the
        # provider-ID requirement is enforced.
        if not title:
            continue

        if currency not in FX_CURRENCY_CODES and currency != "ALL":
            raise ProviderError(f"Unsupported ForexFactory currency '{currency}'.")

        event_id = str(row.get("id") or "").strip()
        if not event_id:
            raise ProviderError("ForexFactory calendar event has no provider ID.")

        event_date = _parse_forexfactory_date(str(row.get("date") or ""), start, end)
        hour, minute = _parse_forexfactory_time(str(row.get("time") or ""))
        local_datetime = event_date.replace(
            hour=hour,
            minute=minute,
            tzinfo=timezone_info,
        )

        normalized_events.append({
            "id": event_id,
            "dateline": int(local_datetime.timestamp()),
            "currency": currency,
            "name": title,
            "impactName": str(row.get("impact") or "").replace(" Impact Expected", "").strip(),
            "actual": str(row.get("actual") or "").strip() or None,
            "forecast": str(row.get("forecast") or "").strip() or None,
            "previous": str(row.get("previous") or "").strip() or None,
        })

    return normalized_events


# Function: extract_days_payload — extracts provider day payloads.
# Variables: html=provider HTML.
# Local variables: decoded=local intermediate value; end_offset=local intermediate value; exc=local intermediate value; match=regular-expression/provider match; payload_start=local intermediate value.
def extract_days_payload(html: str) -> str:
    match = re.search(r"[\"']days[\"']\s*:\s*\[", html, re.IGNORECASE)
    if not match:
        raise ProviderError("ForexFactory response has no structured days payload.")
    payload_start = match.end() - 1
    try:
        decoded, end_offset = json.JSONDecoder().raw_decode(
            html[payload_start:]
        )
    except json.JSONDecodeError as exc:
        raise ProviderError(
            f"Malformed ForexFactory days payload: {exc}"
        ) from exc
    if not isinstance(decoded, list):
        raise ProviderError("ForexFactory days payload is not a list.")
    return html[payload_start:payload_start + end_offset]


# Function: parse_calendar_days — parses FF calendar days.
# Variables: payload=provider payload.
# Local variables: exc=local intermediate value; parsed=parsed datetime.
def parse_calendar_days(payload: str) -> List[Dict[str, Any]]:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"Malformed provider JSON: {exc}") from exc
    if not isinstance(parsed, list):
        raise ProviderError("ForexFactory days payload is not a list.")
    return parsed


# Function: _resolve_impact — normalizes provider impact.
# Variables: raw=local intermediate value.
# Local variables: direct=direct candidate; impact_class=normalized impact class; name=local intermediate value; needle=local intermediate value; value=input value.
def _resolve_impact(raw: Dict[str, Any]) -> str:
    # ForexFactory's structured calendar uses explicit impactTitle and
    # impactClass fields. impactName is accepted as a compatibility alias.
    impact_text = ""
    for field_name in ("impactTitle", "impactName", "impact"):
        candidate = str(raw.get(field_name, "")).strip()
        if candidate:
            impact_text = candidate.lower()
            break

    normalized_text = re.sub(r"[^a-z]+", " ", impact_text).strip()
    if re.search(r"\bhigh\b", normalized_text):
        return "HIGH"
    if re.search(r"\b(?:med|medium)\b", normalized_text):
        return "MEDIUM"
    if re.search(r"\blow\b", normalized_text):
        return "LOW"
    if "non economic" in normalized_text or "holiday" in normalized_text:
        return "HOLIDAY"

    impact_class = str(raw.get("impactClass", "")).strip().lower()
    class_tokens = re.sub(r"[^a-z]+", " ", impact_class).strip()
    if "red" in class_tokens or "high" in class_tokens:
        return "HIGH"
    if (
        "orange" in class_tokens
        or re.search(r"\bora\b", class_tokens)
        or "medium" in class_tokens
        or re.search(r"\bmed\b", class_tokens)
    ):
        return "MEDIUM"
    if (
        "yellow" in class_tokens
        or re.search(r"\byel\b", class_tokens)
        or "green" in class_tokens
        or re.search(r"\bgrn\b", class_tokens)
        or "low" in class_tokens
    ):
        return "LOW"
    if (
        "grey" in class_tokens
        or "gray" in class_tokens
        or re.search(r"\bgry\b", class_tokens)
        or re.search(r"\bgre\b", class_tokens)
        or "holiday" in class_tokens
    ):
        return "HOLIDAY"

    return "UNKNOWN"


# Function: fetch_forexfactory_event_detail — fetches one ForexFactory Detail specification set.
# Variables: event_id=provider event identifier.
# Local variables: data=decoded response; exc=local exception; payload=provider response text; spec=provider specification; specs=provider specification collection; normalized=canonical specification collection.
def fetch_forexfactory_event_detail(event_id: str) -> List[Dict[str, Any]]:
    event_id = str(event_id).strip()
    if not re.fullmatch(r"\d+", event_id):
        raise ProviderError("ForexFactory event detail has an invalid provider ID.")

    payload = fetch_url(
        FOREXFACTORY_DETAIL_URL.format(event_id=event_id)
    )
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ProviderError(
            f"Malformed ForexFactory detail JSON for event {event_id}: {exc}"
        ) from exc

    if not isinstance(data, dict) or not isinstance(data.get("data"), dict):
        raise ProviderError(
            f"Malformed ForexFactory detail response for event {event_id}."
        )

    specs = data["data"].get("specs", [])
    if not isinstance(specs, list):
        raise ProviderError(
            f"ForexFactory detail specs are not a list for event {event_id}."
        )

    normalized: List[Dict[str, Any]] = []
    for spec in specs:
        if not isinstance(spec, dict):
            raise ProviderError(
                f"Malformed ForexFactory detail specification for event {event_id}."
            )
        if "order" not in spec or "title" not in spec or "html" not in spec:
            raise ProviderError(
                f"Malformed ForexFactory detail specification for event {event_id}."
            )
        if isinstance(spec["order"], bool):
            raise ProviderError(
                f"Invalid ForexFactory detail spec order for event {event_id}."
            )
        try:
            order = int(spec["order"])
        except (TypeError, ValueError) as exc:
            raise ProviderError(
                f"Invalid ForexFactory detail spec order for event {event_id}."
            ) from exc
        title = str(spec["title"]).strip()
        html_value = spec["html"]
        if not title or not isinstance(html_value, str):
            raise ProviderError(
                f"Malformed ForexFactory detail specification for event {event_id}."
            )
        normalized.append({
            "order": order,
            "title": title,
            "html": html_value,
        })

    # The provider response sequence is authoritative. The numeric order value
    # is metadata, not a local sorting key.
    return normalized


# Function: normalize_provider_event — normalizes one provider event.
# Variables: raw=local intermediate value.
# Local variables: currency=currency code; exc=local intermediate value; timestamp=event timestamp; title=event title;
def normalize_provider_event(raw: Dict[str, Any]) -> Dict[str, Any]:
    if raw.get("id") in (None, "", "None"):
        raise ProviderError("ForexFactory event has no provider ID.")
    try:
        timestamp = datetime.fromtimestamp(
            int(raw["dateline"]), tz=timezone.utc
        )
    except (TypeError, ValueError, OSError, KeyError) as exc:
        raise ProviderError("ForexFactory event has an invalid dateline.") from exc

    currency = str(raw.get("currency", "")).strip().upper()
    if currency not in FX_CURRENCY_CODES and currency != "ALL":
        raise ProviderError(
            f"Unsupported ForexFactory currency '{currency}'."
        )
    title = str(raw.get("name", "")).strip()
    if not title:
        raise ProviderError("ForexFactory event has an empty title.")

    return {
        "event_id": f"forexfactory:{raw['id']}",
        "symbol": currency,
        "asset_type": "forex",
        "event_type": "economic",
        "source": "forexfactory",
        "timestamp": format_iso8601(timestamp),
        "title": title,
        "details": {
            "currency": currency,
            "impact": _resolve_impact(raw),
            "actual": (
                str(raw["actual"])
                if raw.get("actual") not in (None, "") else None
            ),
            "forecast": (
                str(raw["forecast"])
                if raw.get("forecast") not in (None, "") else None
            ),
            "previous": (
                str(raw["previous"])
                if raw.get("previous") not in (None, "") else None
            ),
            "specs": [],
        },
    }


# Function: normalize_calendar_events — normalizes provider events.
# Variables: days_data=local intermediate value.
# Local variables: day=calendar day; raw=local intermediate value.
def normalize_calendar_events(days_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for day in days_data:
        if not isinstance(day, dict):
            raise ProviderError("Malformed ForexFactory day record.")
        for raw in day.get("events", []):
            if not isinstance(raw, dict):
                raise ProviderError("Malformed ForexFactory event record.")
            normalized.append(normalize_provider_event(raw))
    return normalized


# Function: fetch_yahoo_news — fetches Yahoo news.
# Variables: symbol=canonical symbol.
# Local variables: data=local intermediate value; item=current collection item; link=local intermediate value; news=provider news collection; provider_symbol=verified provider symbol; publish_epoch=local intermediate value; publisher=local intermediate value; stable_id=local intermediate value; timestamp=event timestamp; title=event title; uuid=local intermediate value; uuid_raw=local intermediate value.
def fetch_yahoo_news(symbol: str) -> List[Dict[str, Any]]:
    provider_symbol, data = _resolve_yahoo_instrument(symbol)

    news = data.get("news")
    if not isinstance(news, list):
        raise ProviderError(
            "Yahoo Finance response has no valid news collection."
        )

    normalized: List[Dict[str, Any]] = []
    for item in news:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        publish_epoch = item.get("providerPublishTime")
        if publish_epoch in (None, ""):
            continue
        try:
            timestamp = datetime.fromtimestamp(
                int(publish_epoch), tz=timezone.utc
            )
        except (TypeError, ValueError, OSError):
            continue

        link = str(item.get("link", "")).strip() or None
        publisher = str(item.get("publisher", "")).strip() or None
        uuid_raw = item.get("uuid")
        uuid = (
            str(uuid_raw).strip()
            if uuid_raw not in (None, "")
            else ""
        )
        stable_id = uuid or hashlib.sha256(
            f"{provider_symbol}|{title}|{timestamp.isoformat()}|{link or ''}".encode(
                "utf-8"
            )
        ).hexdigest()

        normalized.append(
            {
                "event_id": f"yahoo:{stable_id}",
                "symbol": symbol,
                "asset_type": "forex" if is_fx_pair(symbol) else "ticker",
                "event_type": "news",
                "source": "yahoo_finance",
                "timestamp": format_iso8601(timestamp),
                "title": title,
                "details": {
                    "publisher": publisher,
                    "url": link,
                    "provider_symbol": provider_symbol,
                    "summary": (
                        str(item.get("summary")).strip()
                        if item.get("summary") not in (None, "")
                        else None
                    ),
                },
            }
        )
    return normalized


# Function: filter_events_for_symbol — filters symbol-visible events.
# Variables: events=event collection; symbol=canonical symbol.
# Local variables: currencies=symbol-relevant currencies; event=normalized event.
def filter_events_for_symbol(events: List[Dict[str, Any]], symbol: str) -> List[Dict[str, Any]]:
    def visible(event: Dict[str, Any]) -> bool:
        return symbol not in event.get("suppressed_for", [])

    if is_currency(symbol):
        return [
            event for event in events
            if (
                event["source"] == "forexfactory"
                and event["details"].get("currency") == symbol
                and visible(event)
            )
        ]

    if is_fx_pair(symbol):
        currencies = {symbol[:3], symbol[3:]}
        return [
            event for event in events
            if (
                event["source"] == "forexfactory"
                and event["details"].get("currency") in currencies
                and visible(event)
            )
            or (
                event["source"] == "yahoo_finance"
                and event["symbol"] == symbol
                and visible(event)
            )
        ]

    return [
        event for event in events
        if (
            event["source"] == "yahoo_finance"
            and event["symbol"] == symbol
            and visible(event)
        )
    ]

# Function: filter_events_for_interval — filters events by interval.
# Variables: events=event collection; start=interval start; end=interval end.
# Local variables: event=normalized event.
def filter_events_for_interval(
    events: List[Dict[str, Any]],
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
    return [
        event for event in events
        if start <= parse_iso8601(event["timestamp"]) < end
    ]


# Function: update_watermark — updates provider/symbol watermark.
# Variables: document=in-memory Calendar document; provider=provider identifier; symbol=canonical symbol; successful_at=local intermediate value; events=event collection.
# Local variables: event=normalized event; event_timestamps=event timestamp collection; key=dictionary key; max_event_ts=latest event timestamp; old=previous record; old_event_ts=previous latest event timestamp; old_successful_at=previous successful-acquisition timestamp.
def update_watermark(
    document: Dict[str, Any],
    provider: str,
    symbol: str,
    successful_at: datetime,
    events: List[Dict[str, Any]],
) -> None:
    key = watermark_key(provider, symbol)
    old = document["watermarks"].get(key, {})
    old_successful_at = (
        parse_iso8601(old["last_successful_at"])
        if old.get("last_successful_at") else None
    )
    if old_successful_at is not None and successful_at < old_successful_at:
        return
    old_event_ts = (
        parse_iso8601(old["last_event_timestamp"])
        if old.get("last_event_timestamp") else None
    )
    event_timestamps = [
        parse_iso8601(event["timestamp"])
        for event in events
    ]
    max_event_ts = (
        max(event_timestamps) if event_timestamps else old_event_ts
    )
    document["watermarks"][key] = {
        "provider": provider,
        "symbol": symbol,
        "last_successful_at": format_iso8601(successful_at),
        "last_event_timestamp": (
            format_iso8601(max_event_ts) if max_event_ts else None
        ),
    }


# Function: query_current_events — filters current incremental events.
# Variables: events=event collection; since=local intermediate value; until=local intermediate value.
# Local variables: event=normalized event.
def query_current_events(
    events: List[Dict[str, Any]],
    since: datetime,
    until: datetime,
) -> List[Dict[str, Any]]:
    return [
        event for event in events
        if since < parse_iso8601(event["timestamp"]) <= until
    ]


# Function: query_latest_event — selects the most recent past/current visible event.
# Variables: events=event collection; symbol=canonical symbol; now=current UTC reference time.
# Local variables: event=normalized event; visible_past=local intermediate value.
def query_latest_event(
    events: List[Dict[str, Any]],
    symbol: str,
    now: datetime,
) -> List[Dict[str, Any]]:
    visible_past = [
        event
        for event in filter_events_for_symbol(events, symbol)
        if parse_iso8601(event["timestamp"]) <= now
    ]
    if not visible_past:
        return []
    return [
        max(
            visible_past,
            key=lambda event: (
                parse_iso8601(event["timestamp"]),
                event["source"],
                event["event_id"],
            ),
        )
    ]


# Function: query_next_event — selects the nearest future visible event.
# Variables: events=event collection; symbol=canonical symbol; now=current UTC reference time.
# Local variables: event=normalized event; key=dictionary key; visible_future=local intermediate value.
def query_next_event(
    events: List[Dict[str, Any]],
    symbol: str,
    now: datetime,
) -> List[Dict[str, Any]]:
    visible_future = [
        event
        for event in filter_events_for_symbol(events, symbol)
        if parse_iso8601(event["timestamp"]) > now
    ]
    if not visible_future:
        return []
    return [
        min(
            visible_future,
            key=lambda event: (
                parse_iso8601(event["timestamp"]),
                event["source"],
                event["event_id"],
            ),
        )
    ]


# Function: acquire_explicit — performs explicit-range acquisition.
# Variables: document=in-memory Calendar document; symbol=canonical symbol; start=interval start; end=interval end; debug=diagnostic flag.
# Local variables: exc=local intermediate value; fetched_events=local intermediate value; file=local intermediate value; gap_end=local intermediate value; gap_start=local intermediate value; gaps=local intermediate value; in_range=local intermediate value; now=current UTC reference time; provider=provider identifier; successful=successful-provider state/count.
def acquire_explicit(
    document: Dict[str, Any],
    symbol: str,
    start: datetime,
    end: datetime,
    debug: bool = False,
) -> Dict[str, Any]:
    now = utc_now()
    provider_results: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []
    successful = 0
    for provider in resolve_applicable_providers(symbol):
        try:
            if provider == "forexfactory":
                gaps = find_uncovered_intervals(document, provider, symbol, start, end)
                events: List[Dict[str, Any]] = []
                for gap_start, gap_end in gaps:
                    events.extend(fetch_forexfactory(gap_start, gap_end))
                if gaps:
                    merge_events(document, events, clear_suppressed_symbol=symbol)
                    for gap_start, gap_end in gaps:
                        merge_coverage(document, {
                            "provider": provider, "symbol": symbol,
                            "start": format_iso8601(gap_start),
                            "end": format_iso8601(gap_end),
                            "status": "COMPLETE", "updated_at": format_iso8601(now),
                        })
                    update_watermark(document, provider, symbol, now, events)
                    provider_results.append({"provider": provider, "status": "OK", "events_acquired": len(events), "coverage": "UPDATED"})
                else:
                    provider_results.append({"provider": provider, "status": "OK", "events_acquired": 0, "coverage": "CACHED"})
                successful += 1
            else:
                fetched_events = fetch_yahoo_news(symbol)
                in_range = filter_events_for_interval(
                    fetched_events,
                    start,
                    end,
                )
                # Explicit Yahoo acquisition persists only the requested
                # interval. The current cursor is advanced only to the
                # requested end (capped at now), never to the wall-clock
                # acquisition time of an older historical request.
                merge_events(document, in_range)
                if start < now:
                    update_watermark(
                        document,
                        provider,
                        symbol,
                        min(end, now),
                        in_range,
                    )
                provider_results.append({
                    "provider": provider,
                    "status": "PARTIAL",
                    "events_acquired": len(in_range),
                    "historical_coverage": "NOT_GUARANTEED",
                })
                successful += 1
        except YahooForexPairUnavailable as exc:
            if debug:
                print(
                    f"DEBUG | {provider} YahooForexPairUnavailable: {exc}",
                    file=sys.stderr,
                )
            provider_results.append({
                "provider": provider,
                "status": "SKIPPED_NO_FOREX_PAIR",
                "reason": str(exc),
            })
        except ProviderError as exc:
            if debug:
                print(
                    f"DEBUG | {provider} ProviderError traceback:",
                    file=sys.stderr,
                )
                traceback.print_exc()
            failures.append({"provider": provider, "error": str(exc)})
            provider_results.append({"provider": provider, "status": "ERROR", "error": str(exc)})
    if successful:
        validate_calendar_document(document)
        save_calendar_atomic(document)
        if debug:
            print(
                f"DEBUG | Persisted Calendar file: {CALENDAR_FILE}",
                file=sys.stderr,
            )
    return {"provider_results": provider_results, "failures": failures}


# Function: acquire_current — performs watermark-based acquisition.
# Variables: document=in-memory Calendar document; symbol=canonical symbol; debug=diagnostic flag.
# Local variables: clear_suppressed_symbol=local intermediate value; event=normalized event; events=event collection; exc=local intermediate value; fetch_end=local intermediate value; fetch_start=local intermediate value; file=local intermediate value; hour=hour component; key=dictionary key; last_successful_at=local intermediate value; now=current UTC reference time; provider=provider identifier; result=computed result; unique=deduplicated event mapping; watermark=provider/symbol watermark.
def acquire_current(
    document: Dict[str, Any],
    symbol: str,
    debug: bool = False,
) -> Dict[str, Any]:
    now = utc_now()
    provider_results: List[Dict[str, Any]] = []
    incremental: List[Dict[str, Any]] = []

    for provider in resolve_applicable_providers(symbol):
        key = watermark_key(provider, symbol)
        watermark = document["watermarks"].get(key)

        if not watermark or not watermark.get("last_successful_at"):
            provider_results.append({
                "provider": provider,
                "status": "BOOTSTRAP_REQUIRED",
            })
            continue

        last_successful_at = parse_iso8601(watermark["last_successful_at"])
        try:
            if provider == "forexfactory":
                fetch_start = (
                    last_successful_at - timedelta(days=1)
                ).replace(hour=0, minute=0, second=0, microsecond=0)
                fetch_end = (now + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                events = fetch_forexfactory(fetch_start, fetch_end)
                merge_events(
                    document,
                    events,
                    clear_suppressed_symbol=symbol,
                )
                incremental.extend(
                    query_current_events(events, last_successful_at, now)
                )
            else:
                events = fetch_yahoo_news(symbol)
                merge_events(document, events)
                incremental.extend(
                    query_current_events(events, last_successful_at, now)
                )

            if provider == "forexfactory":
                merge_coverage(
                    document,
                    {
                        "provider": provider,
                        "symbol": symbol,
                        "start": format_iso8601(fetch_start),
                        "end": format_iso8601(fetch_end),
                        "status": "COMPLETE",
                        "updated_at": format_iso8601(now),
                    },
                )

            update_watermark(document, provider, symbol, now, events)
            provider_results.append({
                "provider": provider,
                "status": "OK" if provider == "forexfactory" else "PARTIAL",
                "events_acquired": len(events),
                "events_returned": len(
                    query_current_events(events, last_successful_at, now)
                ),
                "historical_coverage": (
                    "NOT_GUARANTEED"
                    if provider == "yahoo_finance"
                    else "COMPLETE"
                ),
            })
        except YahooForexPairUnavailable as exc:
            if debug:
                print(
                    f"DEBUG | {provider} YahooForexPairUnavailable: {exc}",
                    file=sys.stderr,
                )
            provider_results.append({
                "provider": provider,
                "status": "SKIPPED_NO_FOREX_PAIR",
                "reason": str(exc),
            })
        except ProviderError as exc:
            if debug:
                print(
                    f"DEBUG | {provider} ProviderError traceback:",
                    file=sys.stderr,
                )
                traceback.print_exc()
            provider_results.append({
                "provider": provider,
                "status": "ERROR",
                "error": str(exc),
            })

    if any(
        result["status"] in {"OK", "PARTIAL"}
        for result in provider_results
    ):
        validate_calendar_document(document)
        save_calendar_atomic(document)
        if debug:
            print(
                f"DEBUG | Persisted Calendar file: {CALENDAR_FILE}",
                file=sys.stderr,
            )

    unique = {
        event["event_id"]: event
        for event in incremental
    }
    return {
        "events": sorted(
            unique.values(),
            key=lambda event: (
                parse_iso8601(event["timestamp"]),
                event["event_id"],
            ),
        ),
        "provider_results": provider_results,
    }


# Function: status_from_provider_results — derives aggregate status.
# Variables: provider_results=provider result collection.
# Local variables: result=computed result; status=local intermediate value; statuses=status collection.
def status_from_provider_results(provider_results: List[Dict[str, Any]]) -> str:
    statuses = [result["status"] for result in provider_results]
    if not statuses:
        return "UNAVAILABLE"
    if all(status == "SKIPPED_NO_FOREX_PAIR" for status in statuses):
        return "NO_FOREX_PAIR"
    if all(status == "BOOTSTRAP_REQUIRED" for status in statuses):
        return "BOOTSTRAP_REQUIRED"
    if all(status == "ERROR" for status in statuses):
        return "UNAVAILABLE"
    if any(status in {"ERROR", "BOOTSTRAP_REQUIRED"} for status in statuses):
        return "PARTIAL"
    if any(status in {"PARTIAL", "SKIPPED_NO_FOREX_PAIR"} for status in statuses):
        return "PARTIAL"
    return "OK"


# Function: _detail_html_to_text — strips provider HTML for cleartext presentation.
# Variables: value=provider HTML fragment.
def _detail_html_to_text(value: str) -> str:
    # ForexFactory may return Detail HTML with markup escaped one or more times
    # (for example &lt;br&gt;, &amp;lt;br&amp;gt;, or escaped <img ...> markup).
    # Decode repeatedly to a stable value before removing provider markup so
    # cleartext never exposes raw HTML tags.
    text = value
    for _ in range(3):
        decoded = unescape(text)
        if decoded == text:
            break
        text = decoded
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)</(p|div|li|tr|table|h[1-6])\s*>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    return text.strip()


# Function: format_cleartext_details — renders normalized details for human-readable CLI output.
# Variables: details=normalized event details.
# Local variables: display=human-readable value; key=detail key; label=display label; ordered_keys=preferred key order; spec=detail specification; value=detail value.
def format_cleartext_details(details: Dict[str, Any]) -> List[str]:
    """Render details without exposing the internal dictionary representation."""
    preferred_keys = ("currency", "impact", "actual", "forecast", "previous")
    ordered_keys = [key for key in preferred_keys if key in details]
    extra_keys = [
        key for key in details
        if key not in ordered_keys and key != "specs"
    ]
    ordered_keys.extend(sorted(extra_keys))

    lines: List[str] = []
    for key in ordered_keys:
        value = details[key]
        display = "N/A" if value is None else str(value)
        label = key.replace("_", " ").title()
        lines.append(f"  {label:<9}: {display}")

    for spec in details.get("specs", []):
        title = str(spec.get("title", "")).strip()
        content = _detail_html_to_text(str(spec.get("html", "")))
        lines.append(f"  {title:<9}: {content or 'N/A'}")
    return lines


# Function: output_query_result — renders query output.
# Variables: status=local intermediate value; symbol=canonical symbol; events=event collection; provider_results=provider result collection; cleartext=human-readable output flag.
# Local variables: event=normalized event; index=local intermediate value; provider=provider identifier.
def output_query_result(
    status: str,
    symbol: str,
    events: List[Dict[str, Any]],
    provider_results: List[Dict[str, Any]],
    cleartext: bool = False,
) -> None:
    if cleartext:
        print(f"CALENDAR RESULT | {status} | {symbol}")
        for provider in provider_results:
            print(f"PROVIDER | {provider['provider']} | {provider['status']}")
        if not events:
            print("No matching events.")
            return
        for index, event in enumerate(events, start=1):
            print(f"--- EVENT {index:02d} ------------------------------")
            print(f"Timestamp : {event['timestamp']}")
            print(f"Source    : {event['source']}")
            print(f"Type      : {event['event_type']}")
            print(f"Symbol    : {event['symbol']}")
            print(f"Title     : {event['title']}")
            print("Details   :")
            for detail_line in format_cleartext_details(event["details"]):
                print(detail_line)
            print(f"Event ID  : {event['event_id']}")
            print()
        return

    print(json.dumps({
        "status": status,
        "symbol": symbol,
        "events": events,
        "providers": provider_results,
    }, ensure_ascii=False))


# Function: filter_query_events — applies cache visibility guards.
# Variables: document=in-memory Calendar document; events=event collection; symbol=canonical symbol; start=interval start; end=interval end; yahoo_pair_available=Yahoo instrument availability.
# Local variables: event=normalized event; ff_coverage_valid=ForexFactory coverage validity.
def filter_query_events(
    document: Dict[str, Any],
    events: List[Dict[str, Any]],
    symbol: str,
    start: datetime,
    end: datetime,
    yahoo_pair_available: bool = True,
) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    ff_coverage_valid = not bool(
        find_uncovered_intervals(
            document,
            "forexfactory",
            symbol,
            start,
            end,
        )
    )

    for event in events:
        if (
            event["source"] == "yahoo_finance"
            and is_fx_pair(symbol)
            and not yahoo_pair_available
        ):
            # A pair that Yahoo explicitly reported as unavailable must not
            # leak previously cached Yahoo news back into an explicit query.
            continue
        if event["source"] == "forexfactory" and not ff_coverage_valid:
            # ForexFactory records are shared facts. If this symbol's coverage
            # was deleted or is unavailable, do not leak the shared record back
            # into this symbol's query from another symbol's cache.
            continue
        result.append(event)
    return result

# Function: run_query — executes a Calendar query.
# Variables: symbol=canonical symbol; scope=CLI scope; cleartext=human-readable output flag; debug=diagnostic flag.
# Local variables: acquisition=explicit acquisition result; document=in-memory Calendar document; end=interval end; events=event collection; item=current collection item; provider_statuses=provider status list; result=computed result; start=interval start; status=local intermediate value; yahoo_pair_available=Yahoo instrument availability.
def run_query(
    symbol: str,
    scope: str,
    cleartext: bool = False,
    debug: bool = False,
) -> int:
    with acquire_calendar_lock():
        document = load_calendar_document()

        if scope == "current":
            result = acquire_current(document, symbol, debug=debug)
            events = filter_events_for_symbol(result["events"], symbol)
            status = status_from_provider_results(result["provider_results"])
            if status == "OK" and not events:
                status = "NO_RELEVANT_EVENT"
            output_query_result(
                status,
                symbol,
                events,
                result["provider_results"],
                cleartext,
            )
            return 0 if status != "UNAVAILABLE" else 2

        if scope == "latest":
            events = query_latest_event(document["events"], symbol, utc_now())
            status = "OK" if events else "NO_LATEST_EVENT"
            output_query_result(status, symbol, events, [], cleartext)
            return 0

        if scope == "next":
            events = query_next_event(document["events"], symbol, utc_now())
            status = "OK" if events else "NO_NEXT_EVENT"
            output_query_result(status, symbol, events, [], cleartext)
            return 0

        start, end = resolve_scope_interval(scope)
        acquisition = acquire_explicit(
            document,
            symbol,
            start,
            end,
            debug=debug,
        )
        events = filter_events_for_interval(
            filter_events_for_symbol(document["events"], symbol),
            start,
            end,
        )
        yahoo_pair_available = not any(
            item["provider"] == "yahoo_finance"
            and item["status"] == "SKIPPED_NO_FOREX_PAIR"
            for item in acquisition["provider_results"]
        )
        events = filter_query_events(
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
        output_query_result(
            status,
            symbol,
            events,
            acquisition["provider_results"],
            cleartext,
        )
        return 0 if status != "UNAVAILABLE" else 2

# Function: delete_symbol_interval — deletes/suppresses a symbol interval.
# Variables: document=in-memory Calendar document; symbol=canonical symbol; start=interval start; end=interval end.
# Local variables: applicable_providers=providers selected for symbol; coverage=local intermediate value; coverage_end=existing coverage end; coverage_start=existing coverage start; currencies=symbol-relevant currencies; event=normalized event; key=dictionary key; last_event=latest event timestamp; last_event_timestamp=local intermediate value; left=left retained coverage segment; provider=provider identifier; right=right retained coverage segment; suppressed=combined suppression metadata; timestamp=event timestamp; updated=updated record; watermark=provider/symbol watermark.
def delete_symbol_interval(
    document: Dict[str, Any],
    symbol: str,
    start: datetime,
    end: datetime,
) -> None:
    applicable_providers = set(resolve_applicable_providers(symbol))
    currencies = ({symbol} if is_currency(symbol) else
                  {symbol[:3], symbol[3:]} if is_fx_pair(symbol) else set())

    retained_events: List[Dict[str, Any]] = []
    for event in document["events"]:
        timestamp = parse_iso8601(event["timestamp"])
        if timestamp < start or timestamp >= end:
            retained_events.append(event)
            continue

        if (
            event["source"] == "yahoo_finance"
            and event["symbol"] == symbol
            and "yahoo_finance" in applicable_providers
        ):
            # Yahoo news is owned by one canonical symbol, so it can be deleted.
            continue

        if (
            event["source"] == "forexfactory"
            and "forexfactory" in applicable_providers
            and event["details"].get("currency") in currencies
        ):
            # ForexFactory facts are shared. Record a symbol-level suppression
            # instead of deleting the provider fact for every other FX symbol.
            suppressed = set(event.get("suppressed_for", []))
            suppressed.add(symbol)
            updated = event.copy()
            updated["suppressed_for"] = sorted(suppressed)
            retained_events.append(updated)
            continue

        retained_events.append(event)

    document["events"] = retained_events

    retained_coverage: List[Dict[str, Any]] = []
    for coverage in document["coverage"]:
        if (
            coverage["symbol"] != symbol
            or coverage["provider"] not in applicable_providers
        ):
            retained_coverage.append(coverage)
            continue

        coverage_start = parse_iso8601(coverage["start"])
        coverage_end = parse_iso8601(coverage["end"])
        if end <= coverage_start or start >= coverage_end:
            retained_coverage.append(coverage)
            continue

        if coverage_start < start:
            left = coverage.copy()
            left["end"] = format_iso8601(start)
            retained_coverage.append(left)

        if end < coverage_end:
            right = coverage.copy()
            right["start"] = format_iso8601(end)
            retained_coverage.append(right)

    document["coverage"] = retained_coverage

    for provider in applicable_providers:
        key = watermark_key(provider, symbol)
        watermark = document["watermarks"].get(key)
        if watermark is None:
            continue
        last_event_timestamp = watermark.get("last_event_timestamp")
        if last_event_timestamp is None:
            continue
        last_event = parse_iso8601(last_event_timestamp)
        if start <= last_event < end:
            del document["watermarks"][key]

# Function: run_delete — executes full or scoped Calendar deletion.
# Variables: symbol=canonical symbol; scope=CLI scope.
# Local variables: document=in-memory Calendar document; end=interval end; start=interval start.
def run_delete(
    symbol: Optional[str],
    scope: Optional[str],
) -> int:
    # A bare DELETE is an explicit full-cache reset; it bypasses legacy-schema
    # validation so an incompatible calendar.json cannot block the reset.
    with acquire_calendar_lock():
        if symbol is None and scope is None:
            save_calendar_atomic(build_empty_calendar_document())
        else:
            document = load_calendar_document()
            if symbol is None or scope is None:
                raise CalendarInputError(
                    "Scoped delete requires DELETE + SYMBOL + SCOPE. "
                    "Use bare 'delete' only for full cache deletion."
                )
            if scope == "current":
                raise CalendarInputError(
                    "current cannot be used as a delete scope."
                )
            start, end = resolve_scope_interval(scope)
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

# Function: parse_request — parses public CLI arguments.
# Variables: args=local intermediate value.
# Local variables: cleartext=human-readable output flag; debug=diagnostic flag; item=current collection item; positional=CLI positional arguments; scope=CLI scope; symbol=canonical symbol.
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

        symbol = validate_symbol(positional[1])
        scope = parse_scope(positional[2])
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

    symbol = validate_symbol(positional[0])
    scope = parse_scope(positional[1])
    return {
        "operation": "QUERY",
        "symbol": symbol,
        "scope": scope,
        "cleartext": cleartext,
        "debug": debug,
    }


# Function: run — dispatches the parsed CLI operation.
# Local variables: debug=diagnostic flag; exc=local intermediate value; request=parsed CLI request.
def run() -> int:
    debug = "--debug" in sys.argv[1:]
    try:
        request = parse_request(sys.argv[1:])
        debug = request["debug"]
        if request["operation"] == "DELETE":
            return run_delete(
                request["symbol"],
                request["scope"],
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


# Function: main — processes the CLI entry point.
def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
