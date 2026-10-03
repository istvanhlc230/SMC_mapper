import contextlib
import html as html_module
import json
import os
import re
import sys
import tempfile
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any, Dict, List, Optional, Tuple

DATA_ROOT = os.environ.get("SMC_DATA_ROOT", ".")
CALENDAR_FILE = os.path.join(DATA_ROOT, "calendar.json")
PROVIDER_URL = "https://www.forexfactory.com/calendar"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)
HTTP_TIMEOUT = 10.0

SUPPORTED_CURRENCIES = {
    "USD", "EUR", "GBP", "JPY", "CHF",
    "AUD", "CAD", "NZD", "CNY", "HUF",
}
RELATIVE_SCOPES = {
    "today",
    "next_day",
    "week",
    "next_week",
    "month",
    "next_month",
}
EVALUATIONS = {"current", "next"}

HELP_TEXT = """Calendar V1 - economic calendar acquisition and local query

USAGE
  python calendar.py [scope] [symbol] [evaluation]
  python calendar.py delete [scope]
  python calendar.py delete
  python calendar.py --help

PIPELINE
  scope -> ensure coverage -> symbol filter -> optional evaluation
  A scope performs acquisition/coverage handling.
  A symbol without a scope is cache-only and never acquires network data.
  When scope and symbol are combined, evaluation uses the post-acquisition dataset.

SCOPE
  today          Current UTC calendar day
  next_day       Following UTC calendar day
  week           Current UTC calendar week
  next_week      Following UTC calendar week
  month          Current UTC calendar month
  next_month     Following UTC calendar month
  today@HH:MM    Current day with an explicit UTC reference time
  YYYY.MM.DD     Explicit UTC calendar day
  YYYY.MM.DD@HH:MM
                 Explicit date with UTC reference time
  YYYY.MM.DD-YYYY.MM.DD
                 Inclusive UTC date range

SYMBOL
  Six-letter FX pair using supported currencies:
  USD EUR GBP JPY CHF AUD CAD NZD CNY HUF
  Common separators are normalized: EUR/HUF, USD-HUF, USD_HUF.

EVALUATION
  current        Events matching reference date/hour/minute
  next           Earliest event strictly after the reference timestamp
  No evaluation token returns all matching symbol events inside the scope.

DELETE
  python calendar.py delete
                 Delete the complete calendar dataset.
  python calendar.py delete today
                 Delete today's UTC interval.
  python calendar.py delete next_week
                 Delete the next UTC week.
  python calendar.py delete YYYY.MM.DD-YYYY.MM.DD
                 Delete the inclusive date range.
  python calendar.py delete YYYY.MM.DD@HH:MM
                 Delete the one-minute interval beginning at HH:MM.

EXAMPLES
  python calendar.py today
  python calendar.py today USDHUF
  python calendar.py today USDHUF current
  python calendar.py today USDHUF next
  python calendar.py today@14:30 EURHUF current
  python calendar.py next_week USDHUF next
  python calendar.py next_month EURUSD
  python calendar.py 2026.10.03@14:30 USDJPY current
  python calendar.py 2026.10.01-2026.10.31 EURHUF
  python calendar.py USDHUF current
  python calendar.py delete 2026.10.01-2026.10.31

TIME
  All internal timestamps and scope boundaries are UTC.
  @HH:MM sets the evaluation reference time; acquisition remains day-based.

ERRORS
  Invalid dates, times, ranges, scopes, symbols, evaluations, and argument
  combinations are rejected explicitly. No old flag-based CLI is supported.
"""


def print_help() -> None:
    print(HELP_TEXT)


def normalize_symbol(symbol: str) -> str:
    return re.sub(r"[/_-]", "", symbol).upper().strip()


def validate_symbol(symbol: str) -> str:
    normalized = normalize_symbol(symbol)
    if len(normalized) != 6:
        sys.exit(
            f"Error: Invalid FX symbol '{symbol}'. "
            "Expected a six-letter FX pair."
        )
    first, second = normalized[:3], normalized[3:]
    if first not in SUPPORTED_CURRENCIES or second not in SUPPORTED_CURRENCIES:
        sys.exit(f"Error: Unsupported FX symbol '{symbol}'.")
    return normalized


def is_symbol(token: str) -> bool:
    normalized = normalize_symbol(token)
    return (
        len(normalized) == 6
        and normalized[:3] in SUPPORTED_CURRENCIES
        and normalized[3:] in SUPPORTED_CURRENCIES
    )


def parse_time(time_str: str) -> Tuple[int, int]:
    if not re.fullmatch(r"\d{2}:\d{2}", time_str):
        sys.exit(f"Error: Invalid time format '{time_str}'. Expected HH:MM.")
    hour, minute = (int(part) for part in time_str.split(":"))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        sys.exit(f"Error: Invalid time '{time_str}'. Expected HH:MM.")
    return hour, minute


def parse_date(date_str: str) -> datetime:
    if not re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", date_str):
        sys.exit(
            f"Error: Invalid date format '{date_str}'. Expected YYYY.MM.DD."
        )
    try:
        year, month, day = (int(part) for part in date_str.split("."))
        return datetime(year, month, day, tzinfo=timezone.utc)
    except ValueError:
        sys.exit(f"Error: Invalid calendar date '{date_str}'.")


def parse_date_range(range_str: str) -> Tuple[datetime, datetime]:
    parts = range_str.split("-")
    if len(parts) != 2:
        sys.exit(
            f"Error: Invalid range '{range_str}'. "
            "Expected YYYY.MM.DD-YYYY.MM.DD."
        )
    start = parse_date(parts[0])
    end = parse_date(parts[1])
    if start > end:
        sys.exit(f"Error: Reversed date range '{range_str}'.")
    return start, end


def parse_scope_token(scope_token: str) -> Tuple[str, Optional[Tuple[int, int]]]:
    if scope_token in RELATIVE_SCOPES:
        return scope_token, None

    if scope_token.startswith("today@"):
        base, time_token = scope_token.split("@", 1)
        if base != "today":
            sys.exit(f"Error: Invalid scope token '{scope_token}'.")
        return base, parse_time(time_token)

    datetime_match = re.fullmatch(
        r"(\d{4}\.\d{2}\.\d{2})@(\d{2}:\d{2})",
        scope_token,
    )
    if datetime_match:
        return datetime_match.group(1), parse_time(datetime_match.group(2))

    if re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", scope_token):
        parse_date(scope_token)
        return scope_token, None

    if re.fullmatch(
        r"\d{4}\.\d{2}\.\d{2}-\d{4}\.\d{2}\.\d{2}",
        scope_token,
    ):
        parse_date_range(scope_token)
        return scope_token, None

    sys.exit(f"Error: Invalid scope token '{scope_token}'.")


def is_scope(token: str) -> bool:
    try:
        parse_scope_token(token)
    except SystemExit:
        return False
    return True


def is_evaluation(token: str) -> bool:
    return token in EVALUATIONS


def parse_calendar_request(args_list: List[str]) -> Dict[str, Any]:
    if not args_list:
        sys.exit("Error: No arguments provided. Use --help for detailed usage.")

    if len(args_list) == 1 and args_list[0] in ("-h", "--help"):
        print_help()
        raise SystemExit(0)

    if any(arg in ("-h", "--help") for arg in args_list):
        sys.exit("Error: --help cannot be combined with other arguments.")

    if args_list[0] == "delete":
        if len(args_list) > 2:
            sys.exit("Error: delete accepts at most one scope.")
        scope = args_list[1] if len(args_list) == 2 else None
        if scope is not None:
            parse_scope_token(scope)
        return {
            "operation": "DELETE",
            "scope": scope,
            "symbol": None,
            "evaluation": None,
        }

    scope = None
    symbol = None
    evaluation = None
    index = 0

    if index < len(args_list) and is_scope(args_list[index]):
        scope = args_list[index]
        index += 1

    if index < len(args_list) and is_symbol(args_list[index]):
        symbol = validate_symbol(args_list[index])
        index += 1

    if index < len(args_list) and is_evaluation(args_list[index]):
        evaluation = args_list[index]
        index += 1

    if index < len(args_list):
        sys.exit(f"Error: Unexpected or invalid token '{args_list[index]}'.")

    if scope is None and symbol is None:
        sys.exit(
            f"Error: Expected a scope or FX symbol, got '{args_list[0]}'. "
            "Use --help for the canonical grammar."
        )

    if evaluation is not None and symbol is None:
        sys.exit("Error: An evaluation requires a symbol.")

    return {
        "operation": "PIPELINE",
        "scope": scope,
        "symbol": symbol,
        "evaluation": evaluation,
    }


def resolve_scope_interval(scope_token: str) -> Tuple[datetime, datetime]:
    base, _ = parse_scope_token(scope_token)
    now = datetime.now(timezone.utc)

    if base == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif base == "next_day":
        start = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=1)
    elif base == "week":
        days_since_sunday = (now.weekday() + 1) % 7
        start = (now - timedelta(days=days_since_sunday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=7)
    elif base == "next_week":
        days_until_next_sunday = 7 - ((now.weekday() + 1) % 7)
        start = (now + timedelta(days=days_until_next_sunday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=7)
    elif base == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (start + timedelta(days=32)).replace(day=1)
    elif base == "next_month":
        start = (now.replace(day=1) + timedelta(days=32)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        end = (start + timedelta(days=32)).replace(day=1)
    elif re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", base):
        start = parse_date(base)
        end = start + timedelta(days=1)
    elif re.fullmatch(
        r"\d{4}\.\d{2}\.\d{2}-\d{4}\.\d{2}\.\d{2}",
        base,
    ):
        start_date, end_date = parse_date_range(base)
        return start_date, end_date + timedelta(days=1)
    else:
        sys.exit(f"Error: Unknown scope '{base}'.")

    return start, end


def resolve_scope_reference(scope_token: Optional[str]) -> datetime:
    now = datetime.now(timezone.utc)
    if scope_token is None:
        return now

    base, time_parts = parse_scope_token(scope_token)
    if time_parts is None:
        return now

    hour, minute = time_parts
    if base == "today":
        return now.replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )
    return parse_date(base).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )


def resolve_delete_intervals(
    scope_token: Optional[str],
) -> Tuple[Optional[datetime], Optional[datetime]]:
    if scope_token is None:
        return None, None

    start, end = resolve_scope_interval(scope_token)
    _, time_parts = parse_scope_token(scope_token)
    if time_parts is not None:
        reference = resolve_scope_reference(scope_token)
        return reference, reference + timedelta(minutes=1)
    return start, end


def format_iso8601(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso8601(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        sys.exit(f"Error: Invalid UTC timestamp '{value}'.")
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        sys.exit(f"Error: Non-UTC timestamp '{value}'.")
    return parsed


def build_empty_calendar_document() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "source": "forexfactory",
        "coverage": [],
        "events": [],
    }


def validate_calendar_document(doc: Dict[str, Any]) -> None:
    if doc.get("schema_version") != 1:
        sys.exit("Error: Invalid schema version.")
    if doc.get("source") != "forexfactory":
        sys.exit("Error: Invalid calendar source.")
    if not isinstance(doc.get("coverage"), list):
        sys.exit("Error: Invalid coverage collection.")
    if not isinstance(doc.get("events"), list):
        sys.exit("Error: Invalid events collection.")

    previous_end: Optional[datetime] = None
    for coverage in doc["coverage"]:
        for field in ("start", "end", "fetched_at", "requested"):
            if field not in coverage:
                sys.exit(f"Error: Malformed coverage, missing '{field}'.")
        requested = coverage["requested"]
        if not isinstance(requested, dict):
            sys.exit("Error: Malformed coverage.requested.")
        if not isinstance(requested.get("type"), str) or not isinstance(
            requested.get("value"), str
        ):
            sys.exit("Error: Malformed coverage.requested fields.")

        start = parse_iso8601(coverage["start"])
        end = parse_iso8601(coverage["end"])
        parse_iso8601(coverage["fetched_at"])

        if start >= end:
            sys.exit("Error: Invalid coverage bounds.")
        if previous_end is not None and start < previous_end:
            sys.exit("Error: Overlapping or unsorted coverage intervals.")
        previous_end = end

    seen_ids = set()
    for event in doc["events"]:
        for field in (
            "event_id",
            "datetime",
            "impact",
            "currency",
            "event",
            "actual",
            "forecast",
            "previous",
            "source",
        ):
            if field not in event:
                sys.exit(f"Error: Corrupt event, missing '{field}'.")
        if event["source"] != "forexfactory":
            sys.exit("Error: Invalid event source.")
        if event["impact"] not in {
            "HIGH", "MEDIUM", "LOW", "HOLIDAY", "UNKNOWN"
        }:
            sys.exit("Error: Invalid event impact.")

        event_id = event["event_id"]
        if (
            not isinstance(event_id, str)
            or not event_id.startswith("forexfactory:")
            or len(event_id) <= len("forexfactory:")
        ):
            sys.exit("Error: Invalid provider event identity.")
        if event_id in seen_ids:
            sys.exit("Error: Duplicate event ID.")
        seen_ids.add(event_id)

        timestamp = parse_iso8601(event["datetime"])
        if event["datetime"] != format_iso8601(timestamp):
            sys.exit("Error: Non-canonical event timestamp format.")


def load_calendar_document() -> Dict[str, Any]:
    if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:
        return build_empty_calendar_document()

    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"Error: Calendar data integrity error: {exc}")

    validate_calendar_document(document)
    return document


def save_calendar_atomic(doc: Dict[str, Any]) -> None:
    directory = os.path.dirname(CALENDAR_FILE) or "."
    fd, temporary_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(doc, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, CALENDAR_FILE)
    except Exception as exc:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)
        sys.exit(f"Error: Atomic save failed: {exc}")


@contextlib.contextmanager
def acquire_calendar_lock():
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        mutex = kernel32.CreateMutexW(None, False, "SMC_Calendar_Lock")
        if not mutex:
            sys.exit(
                "Error: Failed to create lock mutex, "
                f"error {ctypes.get_last_error()}"
            )

        result = kernel32.WaitForSingleObject(mutex, 0xFFFFFFFF)
        if result not in (0, 0x80):
            sys.exit(
                f"Error: Failed to acquire lock mutex, result {result}"
            )

        try:
            yield
        finally:
            kernel32.ReleaseMutex(mutex)
            kernel32.CloseHandle(mutex)
    else:
        import fcntl

        lock_path = os.path.dirname(os.path.abspath(CALENDAR_FILE)) or "."
        fd = os.open(lock_path, os.O_RDONLY)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)


def resolve_coverage(
    intervals: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if not intervals:
        return []

    ordered = sorted(
        intervals,
        key=lambda item: parse_iso8601(item["start"]),
    )
    merged = [ordered[0].copy()]

    for current in ordered[1:]:
        previous = merged[-1]
        previous_end = parse_iso8601(previous["end"])
        current_start = parse_iso8601(current["start"])
        current_end = parse_iso8601(current["end"])

        if current_start <= previous_end:
            previous["end"] = format_iso8601(
                max(previous_end, current_end)
            )
            if parse_iso8601(current["fetched_at"]) > parse_iso8601(
                previous["fetched_at"]
            ):
                previous["fetched_at"] = current["fetched_at"]
                previous["requested"] = current["requested"]
        else:
            merged.append(current.copy())

    return merged


def find_uncovered_intervals(
    request_start: datetime,
    request_end: datetime,
    coverage: List[Dict[str, Any]],
) -> List[Tuple[datetime, datetime]]:
    uncovered: List[Tuple[datetime, datetime]] = []
    cursor = request_start

    for entry in sorted(
        coverage,
        key=lambda item: parse_iso8601(item["start"]),
    ):
        coverage_start = parse_iso8601(entry["start"])
        coverage_end = parse_iso8601(entry["end"])

        if coverage_end <= cursor:
            continue
        if coverage_start > cursor:
            if coverage_start >= request_end:
                break
            uncovered.append((cursor, min(coverage_start, request_end)))
        cursor = max(cursor, coverage_end)
        if cursor >= request_end:
            break

    if cursor < request_end:
        uncovered.append((cursor, request_end))

    return uncovered


def merge_coverage(
    old_coverage: List[Dict[str, Any]],
    new_coverage: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return resolve_coverage(old_coverage + [new_coverage])


def deduplicate_calendar_events(
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    by_id: Dict[str, Dict[str, Any]] = {}

    for event in events:
        event_id = event["event_id"]
        if event_id not in by_id:
            by_id[event_id] = event
            continue

        if by_id[event_id]["datetime"] != event["datetime"]:
            sys.exit(f"Error: Identity/time conflict for {event_id}.")
        by_id[event_id] = event

    result = list(by_id.values())
    result.sort(
        key=lambda item: (
            parse_iso8601(item["datetime"]),
            item["event_id"],
        )
    )
    return result


def merge_calendar_events(
    old_events: List[Dict[str, Any]],
    new_events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    return deduplicate_calendar_events(old_events + new_events)


def fetch_calendar_source(period_type: str, period_value: str) -> str:
    request_url = f"{PROVIDER_URL}?{period_type}={period_value}"
    request = urllib.request.Request(
        request_url,
        headers={"User-Agent": USER_AGENT},
    )

    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status}")
            return response.read().decode("utf-8")
    except Exception as exc:
        sys.exit(f"Error: Provider fetch failed: {exc}")


def _html_text(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = html_module.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _html_cell_text(row_html: str, class_token: str) -> str:
    pattern = (
        r"<td\b[^>]*class=[\"']"
        r"[^\"']*\b"
        + re.escape(class_token)
        + r"\b[^\"']*[\"'][^>]*>(.*?)</td>"
    )
    match = re.search(pattern, row_html, re.DOTALL | re.IGNORECASE)
    return _html_text(match.group(1)) if match else ""


def _html_cell_inner(row_html: str, class_token: str) -> str:
    pattern = (
        r"<td\b[^>]*class=[\"']"
        r"[^\"']*\b"
        + re.escape(class_token)
        + r"\b[^\"']*[\"'][^>]*>(.*?)</td>"
    )
    match = re.search(pattern, row_html, re.DOTALL | re.IGNORECASE)
    return match.group(1) if match else ""


def _row_attribute(row_attributes: str, *names: str) -> Optional[str]:
    for name in names:
        match = re.search(
            rf"\b{re.escape(name)}\s*=\s*[\"']([^\"']+)[\"']",
            row_attributes,
            re.IGNORECASE,
        )
        if match:
            return html_module.unescape(match.group(1)).strip()
    return None


def _infer_row_year(month: int, day: int, fetch_start: datetime, fetch_end: datetime) -> int:
    candidates = []
    for year in range(fetch_start.year - 1, fetch_end.year + 2):
        try:
            candidate = datetime(year, month, day, tzinfo=timezone.utc)
        except ValueError:
            continue
        if fetch_start <= candidate < fetch_end:
            candidates.append(year)
    if candidates:
        return min(candidates)
    return fetch_start.year


def _parse_provider_date(
    value: str,
    fetch_start: datetime,
    fetch_end: datetime,
    current_date: Optional[datetime],
) -> Optional[datetime]:
    if not value:
        return current_date
    normalized = re.sub(r"\s+", " ", value).strip()
    for fmt in ("%a %b %d", "%b %d"):
        try:
            parsed = datetime.strptime(normalized, fmt)
            year = _infer_row_year(
                parsed.month,
                parsed.day,
                fetch_start,
                fetch_end,
            )
            return datetime(
                year,
                parsed.month,
                parsed.day,
                tzinfo=timezone.utc,
            )
        except ValueError:
            continue
    return current_date


def _resolve_provider_timezone(value: str):
    normalized = value.strip()
    if normalized.upper() in {"UTC", "GMT", "Z"}:
        return timezone.utc

    offset_match = re.fullmatch(
        r"(?:UTC|GMT)\s*([+-])\s*(\d{1,2})(?::?(\d{2}))?",
        normalized,
        re.IGNORECASE,
    )
    if offset_match:
        sign = 1 if offset_match.group(1) == "+" else -1
        hours = int(offset_match.group(2))
        minutes = int(offset_match.group(3) or "0")
        if hours > 23 or minutes > 59:
            sys.exit(f"Error: Invalid provider calendar timezone '{value}'.")
        return timezone(sign * timedelta(hours=hours, minutes=minutes))

    try:
        return ZoneInfo(normalized)
    except ZoneInfoNotFoundError:
        sys.exit(
            f"Error: Unsupported provider calendar timezone '{value}'. "
            "Install the tzdata package or provide a valid UTC offset."
        )


def _parse_provider_time(value: str) -> Tuple[int, int]:
    normalized = value.strip().lower()
    if not normalized or "all day" in normalized or normalized.startswith("day "):
        return 0, 0
    normalized = normalized.replace(" ", "")
    for fmt in ("%I:%M%p", "%I%p"):
        try:
            parsed = datetime.strptime(normalized, fmt)
            return parsed.hour, parsed.minute
        except ValueError:
            continue
    sys.exit(f"Error: Invalid provider event time '{value}'.")


def _parse_provider_impact(row_html: str) -> int:
    impact_html = _html_cell_inner(row_html, "calendar__impact")
    impact_match = re.search(
        r"\btitle=[\"]([^\"]*Impact[^\"]*)[\"]",
        impact_html,
        re.IGNORECASE,
    )
    title = impact_match.group(1).lower() if impact_match else ""
    if "high" in title:
        return 3
    if "medium" in title:
        return 2
    if "low" in title:
        return 1
    if "holiday" in title or "non-economic" in title:
        return 4
    class_match = re.search(
        r"calendar__impact--(high|medium|low|holiday)\b",
        impact_html,
        re.IGNORECASE,
    )
    if class_match:
        return {
            "high": 3,
            "medium": 2,
            "low": 1,
            "holiday": 4,
        }[class_match.group(1).lower()]
    return 0


def parse_calendar_html(
    html: str,
    fetch_start: datetime,
    fetch_end: datetime,
) -> List[Dict[str, Any]]:
    timezone_text = _html_text(html)
    timezone_match = re.search(
        r"Calendar Time Zone:\s*([A-Za-z_]+(?:/[A-Za-z_]+)+|UTC)\b",
        timezone_text,
        re.IGNORECASE,
    )
    if not timezone_match:
        sys.exit("Error: Missing provider calendar timezone.")
    provider_timezone = timezone_match.group(1)
    provider_tz = _resolve_provider_timezone(provider_timezone)

    row_matches = re.findall(
        r"<tr\b([^>]*)>(.*?)</tr>",
        html,
        re.DOTALL | re.IGNORECASE,
    )
    days: Dict[str, Dict[str, Any]] = {}
    current_date: Optional[datetime] = None
    event_count = 0

    for row_attributes, row_html in row_matches:
        row_class = _row_attribute(row_attributes, "class") or ""
        if "calendar__row" not in row_class.split():
            continue

        event_id = _row_attribute(row_attributes, "data-eventid", "data-event-id")
        if not event_id:
            continue

        date_text = _html_cell_text(row_html, "calendar__date")
        parsed_date = _parse_provider_date(
            date_text,
            fetch_start,
            fetch_end,
            current_date,
        )
        if parsed_date is None:
            sys.exit(
                f"Error: Provider event {event_id} has no resolvable calendar date."
            )
        current_date = parsed_date

        time_text = _html_cell_text(row_html, "calendar__time")
        hour, minute = _parse_provider_time(time_text)

        local_datetime = datetime(
            parsed_date.year,
            parsed_date.month,
            parsed_date.day,
            hour,
            minute,
            tzinfo=provider_tz,
        )
        event_timestamp = local_datetime.astimezone(timezone.utc)

        currency = _html_cell_text(row_html, "calendar__currency").upper()
        event_title = _html_cell_text(row_html, "calendar__event")
        actual = _html_cell_text(row_html, "calendar__actual")
        forecast = _html_cell_text(row_html, "calendar__forecast")
        previous = _html_cell_text(row_html, "calendar__previous")

        day_key = parsed_date.strftime("%Y-%m-%d")
        day = days.setdefault(
            day_key,
            {"date": day_key, "events": []},
        )
        day["events"].append(
            {
                "id": event_id,
                "dateline": int(event_timestamp.timestamp()),
                "impact": _parse_provider_impact(row_html),
                "country": currency,
                "title": event_title,
                "actual": actual or None,
                "forecast": forecast or None,
                "previous": previous or None,
            }
        )
        event_count += 1

    if event_count == 0:
        sys.exit("Error: No calendar event rows found in provider response.")

    return list(days.values())


def extract_days_payload(html: str) -> str:
    match = re.search(r"'days':\s*(\\[.*\\])\s*\\}", html, re.DOTALL)
    if not match:
        sys.exit(
            "Error: Provider response has no embedded days payload; "
            "HTML calendar parser is required."
        )
    return match.group(1)


def parse_calendar_days(payload: str) -> List[Dict[str, Any]]:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: Malformed provider payload: {exc}")
    if not isinstance(parsed, list):
        sys.exit("Error: Provider days payload is not a list.")
    return parsed


def normalize_provider_event(raw: Dict[str, Any]) -> Dict[str, Any]:
    if "id" not in raw or raw["id"] in (None, "", "None"):
        sys.exit("Error: Missing or invalid provider event ID.")
    if "dateline" not in raw:
        sys.exit("Error: Missing required provider dateline.")

    try:
        event_timestamp = datetime.fromtimestamp(
            int(raw["dateline"]),
            timezone.utc,
        )
    except (TypeError, ValueError, OSError):
        sys.exit("Error: Invalid provider event dateline.")

    impact = {
        1: "LOW",
        2: "MEDIUM",
        3: "HIGH",
        4: "HOLIDAY",
    }.get(raw.get("impact"), "UNKNOWN")
    currency = str(raw.get("country", "")).upper().strip() or None

    return {
        "event_id": f"forexfactory:{raw['id']}",
        "datetime": format_iso8601(event_timestamp),
        "currency": currency,
        "impact": impact,
        "event": str(raw.get("title", "")),
        "actual": (
            str(raw["actual"])
            if raw.get("actual") not in (None, "")
            else None
        ),
        "forecast": (
            str(raw["forecast"])
            if raw.get("forecast") not in (None, "")
            else None
        ),
        "previous": (
            str(raw["previous"])
            if raw.get("previous") not in (None, "")
            else None
        ),
        "source": "forexfactory",
    }


def normalize_calendar_events(
    days_data: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    normalized_events: List[Dict[str, Any]] = []
    for day in days_data:
        if not isinstance(day, dict):
            sys.exit("Error: Malformed provider day record.")
        for raw_event in day.get("events", []):
            if not isinstance(raw_event, dict):
                sys.exit("Error: Malformed provider event record.")
            normalized_events.append(normalize_provider_event(raw_event))
    return normalized_events


def extract_symbol_currencies(symbol: str) -> List[str]:
    normalized = validate_symbol(symbol)
    return [normalized[:3], normalized[3:]]


def filter_events_for_symbol(
    events: List[Dict[str, Any]],
    symbol: str,
) -> List[Dict[str, Any]]:
    currencies = extract_symbol_currencies(symbol)
    return [
        event
        for event in events
        if event.get("currency") in currencies
    ]


def filter_events_for_interval(
    events: List[Dict[str, Any]],
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
    return [
        event
        for event in events
        if start <= parse_iso8601(event["datetime"]) < end
    ]


def query_current_events(
    events: List[Dict[str, Any]],
    reference_datetime: datetime,
) -> List[Dict[str, Any]]:
    result = []
    for event in events:
        event_datetime = parse_iso8601(event["datetime"])
        if (
            event_datetime.date() == reference_datetime.date()
            and event_datetime.hour == reference_datetime.hour
            and event_datetime.minute == reference_datetime.minute
        ):
            result.append(event)

    return sorted(
        result,
        key=lambda item: (
            parse_iso8601(item["datetime"]),
            item["event_id"],
        ),
    )


def query_next_events(
    events: List[Dict[str, Any]],
    reference_datetime: datetime,
) -> List[Dict[str, Any]]:
    future = [
        event
        for event in events
        if parse_iso8601(event["datetime"]) > reference_datetime
    ]
    if not future:
        return []

    future.sort(
        key=lambda item: (
            parse_iso8601(item["datetime"]),
            item["event_id"],
        )
    )
    first_datetime = future[0]["datetime"]
    return [
        event
        for event in future
        if event["datetime"] == first_datetime
    ]


def query_nearest_events(
    events: List[Dict[str, Any]],
    reference_datetime: datetime,
) -> List[Dict[str, Any]]:
    if not events:
        return []

    distances = [
        (
            event,
            abs(
                (
                    parse_iso8601(event["datetime"])
                    - reference_datetime
                ).total_seconds()
            ),
        )
        for event in events
    ]
    minimum = min(distance for _, distance in distances)
    result = [event for event, distance in distances if distance == minimum]
    return sorted(
        result,
        key=lambda item: (
            parse_iso8601(item["datetime"]),
            item["event_id"],
        ),
    )


def output_query_result(
    status: str,
    symbol: str,
    events: List[Dict[str, Any]],
) -> None:
    print(
        json.dumps(
            {
                "status": status,
                "symbol": symbol,
                "events": events,
            }
        )
    )


def run_acquisition(scope: str) -> None:
    request_start, request_end = resolve_scope_interval(scope)

    if (
        os.path.exists(CALENDAR_FILE)
        and os.path.getsize(CALENDAR_FILE) > 0
    ):
        try:
            with open(CALENDAR_FILE, "r", encoding="utf-8") as handle:
                pre_document = json.load(handle)
            if not find_uncovered_intervals(
                request_start,
                request_end,
                pre_document.get("coverage", []),
            ):
                return
        except Exception:
            pass

    with acquire_calendar_lock():
        document = load_calendar_document()
        uncovered = find_uncovered_intervals(
            request_start,
            request_end,
            document["coverage"],
        )
        if not uncovered:
            return

        fetched_at = datetime.now(timezone.utc)

        for uncovered_start, uncovered_end in uncovered:
            fetch_start = uncovered_start.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            fetch_end = uncovered_end
            if fetch_end.hour != 0 or fetch_end.minute != 0:
                fetch_end = (
                    fetch_end + timedelta(days=1)
                ).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )

            first_day = fetch_start.strftime("%b%d.%Y").lower()
            last_day = (
                fetch_end - timedelta(days=1)
            ).strftime("%b%d.%Y").lower()
            provider_range = f"{first_day}-{last_day}"

            html = fetch_calendar_source("range", provider_range)
            try:
                payload = extract_days_payload(html)
            except SystemExit:
                days_data = parse_calendar_html(
                    html,
                    fetch_start,
                    fetch_end,
                )
            else:
                days_data = parse_calendar_days(payload)

            if not days_data:
                sys.exit("Error: Provider returned no calendar days.")

            new_events = normalize_calendar_events(days_data)
            document["events"] = merge_calendar_events(
                document["events"],
                new_events,
            )
            document["coverage"] = merge_coverage(
                document["coverage"],
                {
                    "start": format_iso8601(fetch_start),
                    "end": format_iso8601(fetch_end),
                    "requested": {
                        "type": "range",
                        "value": provider_range,
                    },
                    "fetched_at": format_iso8601(fetched_at),
                },
            )

        validate_calendar_document(document)
        save_calendar_atomic(document)


def run_query(
    symbol: str,
    scope: Optional[str],
    evaluation: Optional[str],
) -> None:
    normalized_symbol = validate_symbol(symbol)

    if (
        not os.path.exists(CALENDAR_FILE)
        or os.path.getsize(CALENDAR_FILE) == 0
    ):
        output_query_result(
            "NO_CALENDAR_DATA",
            normalized_symbol,
            [],
        )
        return

    document = load_calendar_document()
    events = filter_events_for_symbol(
        document["events"],
        normalized_symbol,
    )

    if scope is not None:
        start, end = resolve_scope_interval(scope)
        events = filter_events_for_interval(events, start, end)

    reference_datetime = resolve_scope_reference(scope)

    if evaluation == "current":
        result = query_current_events(events, reference_datetime)
    elif evaluation == "next":
        result = query_next_events(events, reference_datetime)
    else:
        result = events

    output_query_result(
        "OK" if result else "NO_RELEVANT_EVENT",
        normalized_symbol,
        result,
    )


def delete_events(
    events: List[Dict[str, Any]],
    start: Optional[datetime],
    end: Optional[datetime],
) -> List[Dict[str, Any]]:
    if start is None and end is None:
        return []

    result = []
    for event in events:
        event_datetime = parse_iso8601(event["datetime"])
        if start <= event_datetime < end:
            continue
        result.append(event)
    return result


def delete_coverage(
    coverage: List[Dict[str, Any]],
    start: Optional[datetime],
    end: Optional[datetime],
) -> List[Dict[str, Any]]:
    if start is None and end is None:
        return []

    remaining: List[Dict[str, Any]] = []

    for entry in coverage:
        coverage_start = parse_iso8601(entry["start"])
        coverage_end = parse_iso8601(entry["end"])

        if start <= coverage_start and end >= coverage_end:
            continue

        if start > coverage_start and end < coverage_end:
            left = entry.copy()
            right = entry.copy()
            left["end"] = format_iso8601(start)
            right["start"] = format_iso8601(end)
            remaining.extend([left, right])
            continue

        adjusted = entry.copy()
        if start <= coverage_start < end:
            adjusted["start"] = format_iso8601(end)
        elif start < coverage_end <= end:
            adjusted["end"] = format_iso8601(start)

        adjusted_start = parse_iso8601(adjusted["start"])
        adjusted_end = parse_iso8601(adjusted["end"])
        if adjusted_start < adjusted_end:
            remaining.append(adjusted)

    return resolve_coverage(remaining)


def run_delete(scope: Optional[str]) -> None:
    if (
        not os.path.exists(CALENDAR_FILE)
        or os.path.getsize(CALENDAR_FILE) == 0
    ):
        return

    start, end = resolve_delete_intervals(scope)

    with acquire_calendar_lock():
        document = load_calendar_document()

        if start is None and end is None:
            document["events"] = []
            document["coverage"] = []
        else:
            document["events"] = delete_events(
                document["events"], start, end
            )
            document["coverage"] = delete_coverage(
                document.get("coverage", []), start, end
            )

        validate_calendar_document(document)
        save_calendar_atomic(document)


def run() -> None:
    request = parse_calendar_request(sys.argv[1:])

    if request["operation"] == "DELETE":
        run_delete(request["scope"])
        return

    scope = request["scope"]
    symbol = request["symbol"]
    evaluation = request["evaluation"]

    if scope is not None:
        run_acquisition(scope)

    if symbol is not None:
        run_query(symbol, scope, evaluation)


def main() -> None:
    run()


if __name__ == "__main__":
    main()
