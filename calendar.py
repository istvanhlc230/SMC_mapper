import json
import os
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

def is_scope(token: str) -> bool:
    if token in ("today", "next_day", "week", "next_week", "month", "next_month"): return True
    if token.startswith("today@"): return True
    if re.match(r"^\d{4}\.\d{2}\.\d{2}(@\d{2}:\d{2})?$", token): return True
    if re.match(r"^\d{4}\.\d{2}\.\d{2}-\d{4}\.\d{2}\.\d{2}$", token): return True
    return False

def is_symbol(token: str) -> bool:
    token = normalize_symbol(token)
    valid_currencies = {"USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD", "CNY", "HUF"}
    if len(token) == 6:
        if token[:3] in valid_currencies and token[3:] in valid_currencies:
            return True
    return False

def is_evaluation(token: str) -> bool:
    return token in ("current", "next")

def extract_symbol_currencies(symbol: str) -> List[str]:
    symbol = normalize_symbol(symbol)
    valid_currencies = {"USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD", "CNY", "HUF"}
    if len(symbol) == 6:
        c1, c2 = symbol[:3], symbol[3:]
        if c1 in valid_currencies and c2 in valid_currencies:
            return [c1, c2]
    return [symbol]

def parse_calendar_request(args_list: List[str]) -> Dict[str, Any]:
    if not args_list:
        sys.exit("Error: No arguments provided. Use --help for usage.")
        
    if args_list[0] in ("-h", "--help"):
        print("Usage: python calendar.py [scope] [symbol] [evaluation]")
        print("       python calendar.py delete [scope]")
        print("       python calendar.py delete")
        sys.exit(0)
        
    if args_list[0] == "delete":
        if len(args_list) > 2:
            sys.exit("Error: Invalid arguments mixed with delete")
        scope = args_list[1] if len(args_list) == 2 else None
        if scope and not is_scope(scope):
            sys.exit(f"Error: Invalid scope token '{scope}' for delete")
        return {"operation": "DELETE", "scope": scope, "symbol": None, "evaluation": None}
        
    scope = None
    symbol = None
    evaluation = None
    
    idx = 0
    if idx < len(args_list) and is_scope(args_list[idx]):
        scope = args_list[idx]
        idx += 1
        
    if idx < len(args_list) and is_symbol(args_list[idx]):
        symbol = args_list[idx]
        idx += 1
        
    if idx < len(args_list) and is_evaluation(args_list[idx]):
        evaluation = args_list[idx]
        idx += 1
        
    if idx < len(args_list):
        sys.exit(f"Error: Unexpected or invalid token '{args_list[idx]}'")
        
    if not scope and not symbol:
        sys.exit(f"Error: Invalid query format. Must provide scope or symbol. Invalid token '{args_list[0]}'")
        
    if evaluation and not symbol:
        sys.exit("Error: Evaluation tokens require a symbol")

    return {"operation": "PIPELINE", "scope": scope, "symbol": symbol, "evaluation": evaluation}

def resolve_scope_interval(scope_token: str) -> Tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    base = scope_token.split("@")[0] if "@" in scope_token else scope_token
    
    if base == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif base == "next_day":
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif base == "week":
        start = (now - timedelta(days=(now.weekday() + 1) % 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    elif base == "next_week":
        start = (now + timedelta(days=7 - (now.weekday() + 1) % 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    elif base == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (start + timedelta(days=32)).replace(day=1)
        end = next_month
    elif base == "next_month":
        start = (now.replace(day=1) + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (start + timedelta(days=32)).replace(day=1)
        end = next_month
    elif re.match(r"^\d{4}\.\d{2}\.\d{2}$", base):
        start = datetime(int(base[0:4]), int(base[5:7]), int(base[8:10]), tzinfo=timezone.utc)
        end = start + timedelta(days=1)
    elif re.match(r"^\d{4}\.\d{2}\.\d{2}-\d{4}\.\d{2}\.\d{2}$", base):
        d1, d2 = base.split("-")
        start = datetime(int(d1[0:4]), int(d1[5:7]), int(d1[8:10]), tzinfo=timezone.utc)
        end = datetime(int(d2[0:4]), int(d2[5:7]), int(d2[8:10]), tzinfo=timezone.utc) + timedelta(days=1)
    else:
        sys.exit(f"Error: Unknown scope {base}")
        
    if start >= end:
        sys.exit("Error: Invalid date range")
    return start, end

def resolve_scope_reference(scope_token: str) -> datetime:
    now = datetime.now(timezone.utc)
    if not scope_token:
        return now
    if "@" in scope_token:
        base, t_str = scope_token.split("@")
        h, m = map(int, t_str.split(":"))
        if base == "today":
            return now.replace(hour=h, minute=m, second=0, microsecond=0)
        elif re.match(r"^\d{4}\.\d{2}\.\d{2}$", base):
            dt = datetime(int(base[0:4]), int(base[5:7]), int(base[8:10]), tzinfo=timezone.utc)
            return dt.replace(hour=h, minute=m, second=0, microsecond=0)
        else:
            sys.exit("Error: Time specifier @HH:MM only supported for today and YYYY.MM.DD")
    return now

def resolve_delete_intervals(scope_token: Optional[str]) -> Tuple[Optional[datetime], Optional[datetime]]:
    if not scope_token:
        return None, None
        
    start, end = resolve_scope_interval(scope_token)
    if "@" in scope_token:
        base, t_str = scope_token.split("@")
        h, m = map(int, t_str.split(":"))
        if base == "today":
            now = datetime.now(timezone.utc)
            start = now.replace(hour=h, minute=m, second=0, microsecond=0)
            end = start + timedelta(minutes=1)
        elif re.match(r"^\d{4}\.\d{2}\.\d{2}$", base):
            dt = datetime(int(base[0:4]), int(base[5:7]), int(base[8:10]), tzinfo=timezone.utc)
            start = dt.replace(hour=h, minute=m, second=0, microsecond=0)
            end = start + timedelta(minutes=1)
    return start, end

def parse_time(time_str: str) -> Tuple[int, int]:

    try:

        parts = time_str.split(":")

        if len(parts) != 2: raise ValueError

        h, m = int(parts[0]), int(parts[1])

        if not (0 <= h <= 23 and 0 <= m <= 59): raise ValueError

        return h, m

    except Exception:

        sys.exit(f"Error: Invalid time format: {time_str}. Expected HH:MM")

def output_query_result(status: str, symbol: str, events: List[Dict[str, Any]]):

    print(json.dumps({"status": status, "symbol": symbol, "events": events}))

def parse_iso8601(ts: str) -> datetime:

    if ts.endswith("Z"): ts = ts[:-1] + "+00:00"

    dt = datetime.fromisoformat(ts)

    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) != timedelta(0):

        sys.exit("Error: Non-UTC timestamp")

    return dt

def save_calendar_atomic(doc: Dict[str, Any]) -> None:

    dirname = os.path.dirname(CALENDAR_FILE) or "."

    fd, tmp_path = tempfile.mkstemp(dir=dirname, suffix=".tmp")

    try:

        with os.fdopen(fd, "w", encoding="utf-8") as f:

            json.dump(doc, f, indent=2)

            f.flush()

            os.fsync(f.fileno())

        os.replace(tmp_path, CALENDAR_FILE)

    except Exception as e:

        if os.path.exists(tmp_path): os.remove(tmp_path)

        sys.exit(f"Error: Atomic save failed: {e}")

def parse_calendar_days(json_str: str) -> List[Dict[str, Any]]:

    try:

        return json.loads(json_str)

    except Exception as e:

        sys.exit(f"Error: Malformed provider payload: {e}")

def format_iso8601(dt: datetime) -> str:

    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def resolve_coverage(intervals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    if not intervals: return []

    intervals.sort(key=lambda x: parse_iso8601(x["start"]))

    merged = [intervals[0].copy()]

    for current in intervals[1:]:

        prev = merged[-1]

        prev_end = parse_iso8601(prev["end"])

        curr_start = parse_iso8601(current["start"])

        curr_end = parse_iso8601(current["end"])

        if curr_start <= prev_end:

            merged[-1]["end"] = format_iso8601(max(prev_end, curr_end))

            if parse_iso8601(current["fetched_at"]) > parse_iso8601(prev["fetched_at"]):

                merged[-1]["fetched_at"] = current["fetched_at"]

                if "requested" in current: merged[-1]["requested"] = current["requested"]

        else:

            merged.append(current.copy())

    return merged

def validate_calendar_document(doc: Dict[str, Any]) -> None:

    if doc.get("schema_version") != 1: sys.exit("Error: Invalid schema version")

    if doc.get("source") != "forexfactory": sys.exit("Error: Invalid source")

    if not isinstance(doc.get("coverage"), list): sys.exit("Error: Invalid coverage")

    

    prev_end = None

    for c in doc["coverage"]:

        for field in ["start", "end", "fetched_at", "requested"]:

            if field not in c: sys.exit(f"Error: Malformed coverage, missing {field}")

        

        req = c["requested"]

        if not isinstance(req, dict): sys.exit("Error: Malformed coverage requested type")

        if "type" not in req or "value" not in req: sys.exit("Error: Malformed requested structure")

        if not isinstance(req["type"], str) or not isinstance(req["value"], str): sys.exit("Error: Malformed requested types")

        

        cs = parse_iso8601(c["start"])

        ce = parse_iso8601(c["end"])

        if cs >= ce: sys.exit("Error: Invalid coverage bounds")

        

        if prev_end and cs < prev_end:

            sys.exit("Error: Overlapping or unsorted coverage intervals")

        prev_end = ce

        parse_iso8601(c["fetched_at"])

        

    if not isinstance(doc.get("events"), list): sys.exit("Error: Invalid events")

    seen_ids = set()

    for e in doc["events"]:

        for field in ["event_id", "datetime", "impact", "currency", "event", "actual", "forecast", "previous", "source"]:

            if field not in e: sys.exit(f"Error: Corrupt event, missing {field}")

            

        if e["source"] != "forexfactory": sys.exit("Error: Invalid event source")

        if e["impact"] not in ["HIGH", "MEDIUM", "LOW", "HOLIDAY", "UNKNOWN"]: sys.exit("Error: Invalid impact")

        

        eid = e["event_id"]

        if not isinstance(eid, str) or not eid.startswith("forexfactory:") or len(eid) <= 13: sys.exit("Error: Invalid provider identity")

        

        if eid in seen_ids: sys.exit("Error: Duplicate event ID")

        seen_ids.add(eid)

        

        dt = parse_iso8601(e["datetime"])

        if e["datetime"] != dt.strftime("%Y-%m-%dT%H:%M:%SZ"):

            sys.exit("Error: Non-canonical UTC timestamp format")

def load_calendar_document() -> Dict[str, Any]:

    if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:

        return build_empty_calendar_document()

    try:

        with open(CALENDAR_FILE, "r", encoding="utf-8") as f:

            doc = json.load(f)

        validate_calendar_document(doc)

        return doc

    except Exception as e:

        sys.exit(f"Error: Calendar data integrity error: {e}")

def merge_coverage(old_coverage: List[Dict[str, Any]], new_coverage: Dict[str, Any]) -> List[Dict[str, Any]]:

    return resolve_coverage(old_coverage + [new_coverage])

def merge_calendar_events(old_events: List[Dict[str, Any]], new_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    return deduplicate_calendar_events(old_events + new_events)

def fetch_calendar_source(period_type: str, period_value: str) -> str:

    url = f"{PROVIDER_URL}?{period_type}={period_value}"

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:

        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:

            if response.status != 200: raise Exception(f"HTTP {response.status}")

            return response.read().decode("utf-8")

    except Exception as e:

        sys.exit(f"Error: Provider fetch failed: {e}")

def extract_days_payload(html: str) -> str:

    match = re.search(r"'days':\s*(\[.*\])\s*\}", html, re.DOTALL)

    if not match:

        sys.exit("Error: Missing days payload in provider response")

    return match.group(1)

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

def run_delete(scope: Optional[str]):
    if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:
        return
    start, end = resolve_delete_intervals(scope)
    with acquire_calendar_lock():
        doc = load_calendar_document()
        old_events = json.dumps(doc["events"], sort_keys=True)
        old_coverage = json.dumps(doc.get("coverage", []), sort_keys=True)
        
        doc["events"] = delete_events(doc["events"], start, end)
        doc["coverage"] = delete_coverage(doc.get("coverage", []), start, end)
        
        new_events = json.dumps(doc["events"], sort_keys=True)
        new_coverage = json.dumps(doc["coverage"], sort_keys=True)
        
        if old_events != new_events or old_coverage != new_coverage:
            validate_calendar_document(doc)
            save_calendar_atomic(doc)

def run():
    args = parse_calendar_request(sys.argv[1:])
    if args["operation"] == "DELETE":
        run_delete(args["scope"])
    elif args["operation"] == "PIPELINE":
        if args["scope"]:
            run_acquisition(args["scope"])
        if args["symbol"]:
            run_query(args["symbol"], args["scope"], args["evaluation"])
        elif args["scope"]:
            # If no symbol but scope is provided, wait... what should it output?
            # "python calendar.py today" -> acquire/ensure coverage handling rather than symbol evaluation.
            # But the user also wants it to be silent or output nothing?
            # "Also verify scope-only commands such as: python calendar.py today ... perform acquisition/coverage handling rather than symbol evaluation."
            pass

def main():
    run()

if __name__ == "__main__":
    main()
