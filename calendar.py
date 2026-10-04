import contextlib
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
from typing import Any, Dict, List, Optional, Tuple

DATA_ROOT = os.environ.get("SMC_DATA_ROOT", ".")
CALENDAR_FILE = os.path.join(DATA_ROOT, "calendar.json")
FOREXFACTORY_URL = "https://www.forexfactory.com/calendar"
YAHOO_SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)
HTTP_TIMEOUT = 15.0
SCHEMA_VERSION = 2

SUPPORTED_CURRENCIES = {
    "USD", "EUR", "GBP", "JPY", "CHF",
    "AUD", "CAD", "NZD", "CNY", "HUF",
    "HKD", "SGD", "INR", "MXN", "PHP", "IDR", "THB", "MYR",
    "ZAR", "RUB", "BRL", "NOK", "QAR",
}

# ISO 4217 alpha-3 currency codes are used to recognize a six-letter
# candidate as an FX pair. Yahoo remains authoritative for whether the
# concrete pair actually exists as a Forex instrument.
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

DATE_RE = r"\d{4}\.\d{2}\.\d{2}"
TIME_RE = r"\d{2}:\d{2}"

HELP_TEXT = """Calendar V2 - unified economic calendar and news update engine

USAGE
  python calendar.py SYMBOL YYYY.MM.DD
  python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD
  python calendar.py SYMBOL YYYY.MM.DD@HH:MM
  python calendar.py SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
  python calendar.py SYMBOL current
  python calendar.py delete
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

OUTPUT
  Default output is JSON. --cleartext changes presentation only.

ERRORS
  Invalid syntax and unsupported symbols are rejected explicitly.
  Provider failures are never converted to successful empty data.
"""

class CalendarInputError(Exception):
    pass

class ProviderError(Exception):
    pass


class YahooForexPairUnavailable(Exception):
    pass


class DataIntegrityError(Exception):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_iso8601(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso8601(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise DataIntegrityError(f"Invalid UTC timestamp '{value}'.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise DataIntegrityError(f"Non-UTC timestamp '{value}'.")
    return parsed.astimezone(timezone.utc)


def normalize_symbol(value: str) -> str:
    return value.strip().upper()


def is_currency(value: str) -> bool:
    return value in SUPPORTED_CURRENCIES


def canonicalize_fx_token(value: str) -> str:
    return re.sub(r"[/_-]", "", value.strip().upper())


def is_fx_pair(value: str) -> bool:
    token = canonicalize_fx_token(value)
    return (
        len(token) == 6
        and token[:3] in FX_CURRENCY_CODES
        and token[3:] in FX_CURRENCY_CODES
    )


def is_ticker(value: str) -> bool:
    token = normalize_symbol(value)
    if is_currency(token) or is_fx_pair(token):
        return False
    return bool(re.fullmatch(r"[A-Z0-9][A-Z0-9._-]{0,14}", token))


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


def parse_time(value: str) -> Tuple[int, int]:
    if not re.fullmatch(TIME_RE, value):
        raise CalendarInputError(f"Invalid time '{value}'. Expected HH:MM.")
    hour, minute = (int(part) for part in value.split(":"))
    if hour > 23 or minute > 59:
        raise CalendarInputError(f"Invalid time '{value}'. Expected HH:MM.")
    return hour, minute


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


def parse_point(value: str) -> Tuple[datetime, bool]:
    if "@" not in value:
        return parse_date(value), False
    date_part, time_part = value.split("@", 1)
    base = parse_date(date_part)
    hour, minute = parse_time(time_part)
    return base.replace(hour=hour, minute=minute), True


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


def parse_scope(scope: str) -> str:
    if scope == "current":
        return scope
    resolve_scope_interval(scope)
    return scope


def build_empty_calendar_document() -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "events": [],
        "coverage": [],
        "watermarks": {},
    }


def _load_json_file() -> Dict[str, Any]:
    if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:
        return build_empty_calendar_document()
    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataIntegrityError(f"Calendar data integrity error: {exc}") from exc


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

        if event["source"] == "yahoo_finance":
            if event["event_type"] != "news":
                raise DataIntegrityError(
                    "Yahoo Finance events must use event_type=news."
                )

    seen_coverage = set()
    for coverage in document["coverage"]:
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
        if "|" not in key:
            raise DataIntegrityError("Invalid watermark key.")
        provider, symbol = key.split("|", 1)
        if provider not in {"forexfactory", "yahoo_finance"} or not symbol:
            raise DataIntegrityError("Invalid watermark identity.")
        for field in ("last_successful_at", "last_event_timestamp"):
            value = watermark.get(field)
            if value is not None:
                parse_iso8601(value)


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

        complete_intervals.append(
            (
                max(start, coverage_start),
                min(end, coverage_end),
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


def watermark_key(provider: str, symbol: str) -> str:
    return f"{provider}|{symbol}"


def resolve_applicable_providers(symbol: str) -> List[str]:
    if is_currency(symbol):
        return ["forexfactory"]
    if is_fx_pair(symbol):
        return ["forexfactory", "yahoo_finance"]
    return ["yahoo_finance"]


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


def _resolve_yahoo_instrument(
    symbol: str,
) -> Tuple[str, Dict[str, Any]]:
    if not is_fx_pair(symbol):
        return symbol, _fetch_yahoo_search_payload(symbol)

    candidates: List[str] = []
    mapped = USD_BASE_YAHOO_SYMBOLS.get(symbol)
    if mapped:
        candidates.append(mapped)

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


def resolve_yahoo_symbol(symbol: str) -> Optional[str]:
    try:
        provider_symbol, _ = _resolve_yahoo_instrument(symbol)
    except YahooForexPairUnavailable:
        return None
    return provider_symbol


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


def fetch_forexfactory(start: datetime, end: datetime) -> List[Dict[str, Any]]:
    request_start = start
    request_end = end

    provider_start = start.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    provider_end = end.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    if provider_end < end:
        provider_end += timedelta(days=1)
    last_day = provider_end - timedelta(days=1)

    start_token = provider_start.strftime("%b%d.%Y").lower()
    end_token = last_day.strftime("%b%d.%Y").lower()
    query = urllib.parse.urlencode({"range": f"{start_token}-{end_token}"})
    html = fetch_url(f"{FOREXFACTORY_URL}?{query}")
    days = parse_calendar_days(extract_days_payload(html))
    normalized = normalize_calendar_events(days)

    return [
        event for event in normalized
        if request_start <= parse_iso8601(event["timestamp"]) < request_end
    ]

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


def parse_calendar_days(payload: str) -> List[Dict[str, Any]]:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"Malformed provider JSON: {exc}") from exc
    if not isinstance(parsed, list):
        raise ProviderError("ForexFactory days payload is not a list.")
    return parsed


def _resolve_impact(raw: Dict[str, Any]) -> str:
    name = str(raw.get("impactName", "")).strip().lower()
    direct = {
        "high": "HIGH",
        "medium": "MEDIUM",
        "low": "LOW",
        "holiday": "HOLIDAY",
        "non-economic": "HOLIDAY",
    }
    if name in direct:
        return direct[name]
    impact_class = str(raw.get("impactClass", "")).strip().lower()
    for needle, value in (
        ("high", "HIGH"),
        ("medium", "MEDIUM"),
        ("low", "LOW"),
        ("holiday", "HOLIDAY"),
    ):
        if needle in impact_class:
            return value
    return "UNKNOWN"


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
        },
    }


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
        uuid = str(item.get("uuid", "")).strip()
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

def filter_events_for_interval(
    events: List[Dict[str, Any]],
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
    return [
        event for event in events
        if start <= parse_iso8601(event["timestamp"]) < end
    ]


def update_watermark(
    document: Dict[str, Any],
    provider: str,
    symbol: str,
    successful_at: datetime,
    events: List[Dict[str, Any]],
) -> None:
    key = watermark_key(provider, symbol)
    old = document["watermarks"].get(key, {})
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


def query_current_events(
    events: List[Dict[str, Any]],
    since: datetime,
    until: datetime,
) -> List[Dict[str, Any]]:
    return [
        event for event in events
        if since < parse_iso8601(event["timestamp"]) <= until
    ]


def acquire_explicit(
    document: Dict[str, Any], symbol: str, start: datetime, end: datetime,
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
                events = fetch_yahoo_news(symbol)
                merge_events(document, events)
                update_watermark(document, provider, symbol, now, events)
                in_range = filter_events_for_interval(events, start, end)
                provider_results.append({"provider": provider, "status": "PARTIAL", "events_acquired": len(in_range), "historical_coverage": "NOT_GUARANTEED"})
                successful += 1
        except YahooForexPairUnavailable as exc:
            provider_results.append({
                "provider": provider,
                "status": "SKIPPED_NO_FOREX_PAIR",
                "reason": str(exc),
            })
        except ProviderError as exc:
            failures.append({"provider": provider, "error": str(exc)})
            provider_results.append({"provider": provider, "status": "ERROR", "error": str(exc)})
    if successful:
        validate_calendar_document(document)
        save_calendar_atomic(document)
    return {"provider_results": provider_results, "failures": failures}


def acquire_current(
    document: Dict[str, Any],
    symbol: str,
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
            provider_results.append({
                "provider": provider,
                "status": "SKIPPED_NO_FOREX_PAIR",
                "reason": str(exc),
            })
        except ProviderError as exc:
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
            print(f"Details   : {json.dumps(event['details'], ensure_ascii=False)}")
            print(f"Event ID  : {event['event_id']}")
            print("-----------------------------------------------")
        return

    print(json.dumps({
        "status": status,
        "symbol": symbol,
        "events": events,
        "providers": provider_results,
    }, ensure_ascii=False))


def filter_query_events(
    document: Dict[str, Any],
    events: List[Dict[str, Any]],
    symbol: str,
    start: datetime,
    end: datetime,
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
        if event["source"] == "forexfactory" and not ff_coverage_valid:
            # ForexFactory records are shared facts. If this symbol's coverage
            # was deleted or is unavailable, do not leak the shared record back
            # into this symbol's query from another symbol's cache.
            continue
        result.append(event)
    return result

def run_query(
    symbol: str,
    scope: str,
    cleartext: bool = False,
    debug: bool = False,
) -> int:
    with acquire_calendar_lock():
        document = load_calendar_document()

        if scope == "current":
            result = acquire_current(document, symbol)
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

        start, end = resolve_scope_interval(scope)
        acquisition = acquire_explicit(document, symbol, start, end)
        events = filter_events_for_interval(
            filter_events_for_symbol(document["events"], symbol),
            start,
            end,
        )
        events = filter_query_events(document, events, symbol, start, end)

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

def run_delete(
    symbol: Optional[str],
    scope: Optional[str],
    debug: bool = False,
) -> int:
    with acquire_calendar_lock():
        document = load_calendar_document()

        if symbol is None and scope is None:
            document["events"] = []
            document["coverage"] = []
            document["watermarks"] = {}
        else:
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


def run() -> int:
    debug = "--debug" in sys.argv[1:]
    try:
        request = parse_request(sys.argv[1:])
        debug = request["debug"]
        if request["operation"] == "DELETE":
            return run_delete(
                request["symbol"],
                request["scope"],
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


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
