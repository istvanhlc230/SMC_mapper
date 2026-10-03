import json
import
HELP_TEXT = """
Calendar V1 - economic calendar acquisition and local query

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
  today       Current UTC calendar day
  next_day    Following UTC calendar day
  week        Current UTC calendar week
  next_week   Following UTC calendar week
  month       Current UTC calendar month
  next_month  Following UTC calendar month
  today@HH:MM  Current day with an explicit UTC reference time
  YYYY.MM.DD  Explicit UTC calendar day
  YYYY.MM.DD@HH:MM  Explicit date with UTC reference time
  YYYY.MM.DD-YYYY.MM.DD  Inclusive UTC date range

SYMBOL
  Six-letter FX pair using supported currencies:
  USD EUR GBP JPY CHF AUD CAD NZD CNY HUF
  Common separators are normalized: EUR/HUF, USD-HUF, USD_HUF.

EVALUATION
  current     Events matching reference date/hour/minute
  next        Earliest event strictly after the reference timestamp
  No evaluation token returns all matching symbol events in the scope.

DELETE
  python calendar.py delete              Delete the complete calendar dataset
  python calendar.py delete today         Delete today's UTC interval
  python calendar.py delete next_week     Delete the next UTC week
  python calendar.py delete YYYY.MM.DD-YYYY.MM.DD
                                          Delete an inclusive date range
  python calendar.py delete YYYY.MM.DD@HH:MM
                                          Delete the one-minute interval

EXAMPLES
  python calendar.py today
  python calendar.py today USDHUF current
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
 os
import re
import sys
import tempfile
import urllib.request
import urllib.error
import contextlib
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Set

DATA_ROOT = os.environ.get("SMC_DATA_ROOT", ".")
CALENDAR_FILE = os.path.join(DATA_ROOT, "calendar.json")
PROVIDER_URL = "https://www.forexfactory.com/calendar"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
HTTP_TIMEOUT = 10

def normalize_symbol(symbol: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", symbol).upper()


def print_help() -> None:
    print(HELP_TEXT)


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


def parse_time(time_str: str) -> Tuple[int, int]:
    if not re.fullmatch(r"\d{2}:\d{2}", time_str):
        sys.exit(f"Error: Invalid time format '{time_str}'. Expected HH:MM.")
    hour, minute = (int(part) for part in time_str.split(":"))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        sys.exit(f"Error: Invalid time '{time_str}'. Expected HH:MM.")
    return hour, minute


def parse_date(date_str: str) -> datetime:
    if not re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", date_str):
        sys.exit(f"Error: Invalid date format '{date_str}'. Expected YYYY.MM.DD.")
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
        return base, parse_time(time_token)
    datetime_match = re.fullmatch(
        r"(\d{4}\.\d{2}\.\d{2})@(\d{2}:\d{2})",
        scope_token,
    )
    if datetime_match:
        return datetime_match.group(1), parse_time(datetime_match.group(2))
    if re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", scope_token):
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
        return True
    except SystemExit:
        return False


def is_symbol(token: str) -> bool:
    return token == normalize_symbol(token) and len(token) == 6 and (
        token[:3] in SUPPORTED_CURRENCIES and token[3:] in SUPPORTED_CURRENCIES
    )


def is_evaluation(token: str) -> bool:
    return token in EVALUATIONS

def extract_symbol_currencies(symbol: str) -> List[str]:
    normalized = validate_symbol(symbol)
    return [normalized[:3], normalized[3:]]


def filter_events_for_symbol(events: List[Dict[str, Any]], symbol: str) -> List[Dict[str, Any]]:

    currencies = extract_symbol_currencies(symbol)

    if not currencies: return []

    return [e for e in events if e.get("currency") in currencies]

def parse_date(date_str: str) -> datetime:

    try:

        parts = date_str.split(".")

        if len(date_str) != 10 or len(parts) != 3: raise ValueError

        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])

        if not (2000 <= y <= 2100): raise ValueError

        dt = datetime(y, m, d, tzinfo=timezone.utc)

        if dt.year != y or dt.month != m or dt.day != d: raise ValueError

        return dt

    except Exception:

        sys.exit(f"Error: Invalid date format: {date_str}. Expected YYYY.MM.DD")

def normalize_calendar_events(days_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    events = []

    for day in days_data:

        for evt in day.get("events", []):

            events.append(normalize_provider_event(evt))

    return events

def find_uncovered_intervals(req_start: datetime, req_end: datetime, coverage: List[Dict[str, Any]]) -> List[Tuple[datetime, datetime]]:

    uncovered = []

    current = req_start

    sorted_cov = sorted(coverage, key=lambda c: parse_iso8601(c["start"]))

    for c in sorted_cov:

        c_start = parse_iso8601(c["start"])

        c_end = parse_iso8601(c["end"])

        if c_end <= current: continue

        if c_start > current:

            if c_start >= req_end: break

            uncovered.append((current, c_start))

        current = max(current, c_end)

        if current >= req_end: break

    if current < req_end:

        uncovered.append((current, req_end))

    return uncovered

@contextlib.contextmanager
def acquire_calendar_lock():

    if os.name == "nt":

        import ctypes

        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

        mutex = kernel32.CreateMutexW(None, False, "SMC_Calendar_Lock")

        if not mutex:

            sys.exit(f"Error: Failed to create lock mutex, error {ctypes.get_last_error()}")

        res = kernel32.WaitForSingleObject(mutex, 0xFFFFFFFF)

        if res not in (0, 0x80):

            sys.exit(f"Error: Failed to acquire lock mutex, result {res}")

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

def delete_events(events: List[Dict[str, Any]], start: Optional[datetime], end: Optional[datetime]) -> List[Dict[str, Any]]:
    if start is None and end is None: return []
    kept = []
    for e in events:
        dt = parse_iso8601(e["datetime"])
        if start <= dt < end:
            pass
        else:
            kept.append(e)
    return kept

def delete_coverage(coverage: List[Dict[str, Any]], start: Optional[datetime], end: Optional[datetime]) -> List[Dict[str, Any]]:
    if start is None and end is None: return []
    current_cov = coverage
    new_cov = []
    for c in current_cov:
        cs = parse_iso8601(c["start"])
        ce = parse_iso8601(c["end"])
        if start <= cs and end >= ce:
            continue
        elif start > cs and end < ce:
            c1, c2 = c.copy(), c.copy()
            c1["end"] = format_iso8601(start)
            c2["start"] = format_iso8601(end)
            new_cov.extend([c1, c2])
            continue
        elif start <= cs < end:
            c["start"] = format_iso8601(end)
        elif start < ce <= end:
            c["end"] = format_iso8601(start)
            
        if parse_iso8601(c["start"]) < parse_iso8601(c["end"]):
            new_cov.append(c)
    return resolve_coverage(new_cov)

def query_current_events(events: List[Dict[str, Any]], ref_dt: datetime) -> List[Dict[str, Any]]:
    res = []
    for e in events:
        dt = parse_iso8601(e["datetime"])
        if dt.date() == ref_dt.date() and dt.hour == ref_dt.hour and dt.minute == ref_dt.minute:
            res.append(e)
    res.sort(key=lambda x: (parse_iso8601(x["datetime"]), x["event_id"]))
    return res

def query_next_events(events: List[Dict[str, Any]], ref_dt: datetime) -> List[Dict[str, Any]]:
    future = [e for e in events if parse_iso8601(e["datetime"]) > ref_dt]
    if not future: return []
    future.sort(key=lambda x: (parse_iso8601(x["datetime"]), x["event_id"]))
    earliest = future[0]["datetime"]
    return [e for e in future if e["datetime"] == earliest]

def run_acquisition(scope: str):
    start, end = resolve_scope_interval(scope)
    
    if os.path.exists(CALENDAR_FILE) and os.path.getsize(CALENDAR_FILE) > 0:
        try:
            with open(CALENDAR_FILE, "r", encoding="utf-8") as f: pre_doc = json.load(f)
            if not find_uncovered_intervals(start, end, pre_doc.get("coverage", [])):
                return
        except Exception: pass
            
    with acquire_calendar_lock():
        doc = load_calendar_document()
        uncovered = find_uncovered_intervals(start, end, doc["coverage"])
        if not uncovered: pass
        else:
            now = datetime.now(timezone.utc)
            for u_start, u_end in uncovered:
                fetch_start = u_start.replace(hour=0, minute=0, second=0, microsecond=0)
                fetch_end = u_end
                if fetch_end.hour != 0 or fetch_end.minute != 0:
                    fetch_end = (fetch_end + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                
                d1_str = fetch_start.strftime("%b%d.%Y").lower()
                d2_str = (fetch_end - timedelta(days=1)).strftime("%b%d.%Y").lower()
                pval = f"{d1_str}-{d2_str}"
                
                html = fetch_calendar_source("range", pval)
                payload = extract_days_payload(html)
                days_data = parse_calendar_days(payload)
                expected_days = (fetch_end - fetch_start).days
                if len(days_data) < expected_days:
                    sys.exit(f"Error: Provider returned incomplete coverage. Expected {expected_days} days, got {len(days_data)}.")
                new_events = normalize_calendar_events(days_data)
                doc["events"] = merge_calendar_events(doc["events"], new_events)
                doc["coverage"] = merge_coverage(doc["coverage"], {
                    "start": format_iso8601(fetch_start),
                    "end": format_iso8601(fetch_end),
                    "requested": {"type": "range", "value": pval},
                    "fetched_at": format_iso8601(now)
                })
            validate_calendar_document(doc)
            save_calendar_atomic(doc)

def run_query(symbol: str, scope: Optional[str], evaluation: Optional[str]):
    symbol = normalize_symbol(symbol)
    if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:
        output_query_result("NO_CALENDAR_DATA", symbol, [])
        return
    doc = load_calendar_document()
    events = filter_events_for_symbol(doc["events"], symbol)
    
    if scope:
        start, end = resolve_scope_interval(scope)
        events = [e for e in events if start <= parse_iso8601(e["datetime"]) < end]
        
    if not events:
        output_query_result("NO_RELEVANT_EVENT", symbol, [])
        return
        
    ref_dt = resolve_scope_reference(scope)
    
    if evaluation == "current":
        res = query_current_events(events, ref_dt)
    elif evaluation == "next":
        res = query_next_events(events, ref_dt)
    else:
        res = events
        
    output_query_result("OK" if res else "NO_RELEVANT_EVENT", symbol, res)

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


def main():
    run()

if __name__ == "__main__":
    main()
