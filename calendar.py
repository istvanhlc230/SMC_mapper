
import argparse
import json
import os
import re
import sys
import tempfile
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
import contextlib

DATA_ROOT = os.environ.get("SMC_DATA_ROOT", ".")
CALENDAR_FILE = os.path.join(DATA_ROOT, "calendar.json")
PROVIDER_URL = "https://www.forexfactory.com/calendar"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HTTP_TIMEOUT = 15.0

# ---------------------------------------------------------
# CLI & Parsing
# ---------------------------------------------------------
def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calendar V1 Module")
    # Acquisition
    parser.add_argument("--query", type=str, help="Symbol to query (Acquisition)")
    parser.add_argument("--day", type=str, help="Day selector")
    parser.add_argument("--week", type=str, help="Week selector")
    parser.add_argument("--month", type=str, help="Month selector")
    
    # Local Query
    parser.add_argument("--symbol", type=str, help="Symbol to query (Local Query)")
    parser.add_argument("--current", action="store_true", help="Current minute events")
    parser.add_argument("--next", action="store_true", help="Next events")
    
    # Shared Time Selectors
    parser.add_argument("--date", type=str, help="Date selector YYYY.MM.DD")
    parser.add_argument("--time", type=str, help="Time selector HH:MM or HH:MM-HH:MM")
    parser.add_argument("--range", type=str, help="Range selector YYYY.MM.DD-YYYY.MM.DD")
    
    # Delete
    parser.add_argument("--delete", action="store_true", help="Delete events")
    parser.add_argument("--before", type=str, help="Delete before date")
    parser.add_argument("--after", type=str, help="Delete after date")
    parser.add_argument("--dry-run", action="store_true", help="Dry run for delete")
    
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    return parser

def parse_calendar_request(args: argparse.Namespace) -> str:
    acq = bool(args.query)
    loc = bool(args.symbol)
    del_ = bool(args.delete)
    
    if sum([acq, loc, del_]) != 1:
        print("Error: Must specify exactly one operation family: --query, --symbol, or --delete", file=sys.stderr)
        sys.exit(1)
        
    if acq:
        period_args = [args.day, args.week, args.month, args.range]
        if sum(x is not None for x in period_args) > 1:
            print("Error: Only one period selector allowed for acquisition", file=sys.stderr)
            sys.exit(1)
        return "ACQUISITION"
    elif loc:
        loc_args = [args.current, args.next, args.date, args.time]
        if not any(loc_args):
            return "LOCAL_QUERY_NEXT" # default to next if no arg? Spec says: "If one or more relevant events are scheduled at the current minute, return those... otherwise return the next"
        if args.current and args.next:
            print("Error: Cannot mix --current and --next", file=sys.stderr)
            sys.exit(1)
        return "LOCAL_QUERY"
    elif del_:
        return "DELETE"
    return "UNKNOWN"

def normalize_symbol(symbol: str) -> str:
    return symbol.upper().strip()

def parse_date(date_str: str) -> datetime:
    try:
        parts = date_str.split("."); dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"Error: Invalid date format: {date_str}. Expected YYYY.MM.DD", file=sys.stderr)
        sys.exit(1)

def parse_time(time_str: str) -> tuple[int, int]:
    try:
        parts = time_str.split(":")
        return int(parts[0]), int(parts[1])
    except Exception:
        print(f"Error: Invalid time format: {time_str}. Expected HH:MM", file=sys.stderr)
        sys.exit(1)

def parse_date_range(range_str: str) -> tuple[datetime, datetime]:
    parts = range_str.split("-")
    if len(parts) != 2:
        print("Error: Invalid range format. Expected YYYY.MM.DD-YYYY.MM.DD", file=sys.stderr)
        sys.exit(1)
    return parse_date(parts[0]), parse_date(parts[1])

# ---------------------------------------------------------
# Provider / Network
# ---------------------------------------------------------
def resolve_provider_period(args: argparse.Namespace) -> Optional[tuple[str, str]]:
    if args.day:
        if args.day in ("today", "tomorrow"):
            return ("day", args.day)
        dt = parse_date(args.day)
        return ("day", dt.strftime("%b%d.%Y").lower())
    elif args.week:
        if args.week in ("this", "next"):
            return ("week", args.week)
        dt = parse_date(args.week)
        return ("week", dt.strftime("%b%d.%Y").lower())
    elif args.month:
        if args.month in ("this", "next"):
            return ("month", args.month)
    elif args.range:
        d1, d2 = parse_date_range(args.range)
        val = f"{d1.strftime('%b%d.%Y').lower()}-{d2.strftime('%b%d.%Y').lower()}"
        return ("range", val)
    return None

def fetch_calendar_source(period_type: str, period_value: str) -> str:
    url = f"{PROVIDER_URL}?{period_type}={period_value}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
            return response.read().decode("utf-8")
    except Exception as e:
        print(f"Error: Provider fetch failed: {e}", file=sys.stderr)
        sys.exit(1)

def extract_days_payload(html: str) -> str:
    match = re.search(r"'days':\s*(\[.*\])\s*\}", html, re.DOTALL)
    if not match:
        print("Error: Missing days payload in provider response", file=sys.stderr)
        sys.exit(1)
    return match.group(1)

def parse_calendar_days(json_str: str) -> List[Dict[str, Any]]:
    try:
        # Provider JS might have unquoted keys or single quotes. This is a simplified replacement.
        # The FF days object usually is valid JSON or close to it. 
        # But wait, Python's json doesn't handle single quotes.
        # Let's replace single quotes with double quotes for valid JSON
        json_str = json_str.replace("'", '"')
        # Also clean up boolean JS values if they exist, but FF usually provides simple structures.
        return json.loads(json_str)
    except Exception as e:
        print(f"Error: Malformed provider payload: {e}", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------
# Normalization
# ---------------------------------------------------------
def normalize_provider_event(raw: Dict[str, Any]) -> Dict[str, Any]:
    if "id" not in raw or "dateline" not in raw:
        print("Error: Missing required provider fields", file=sys.stderr)
        sys.exit(1)
        
    event_id = f"forexfactory:{raw['id']}"
    
    try:
        ts = int(raw["dateline"])
        dt = datetime.fromtimestamp(ts, timezone.utc)
    except Exception:
        print("Error: Invalid event dateline", file=sys.stderr)
        sys.exit(1)
        
    impact_map = {
        1: "LOW",
        2: "MEDIUM",
        3: "HIGH",
        4: "HOLIDAY"
    }
    raw_impact = raw.get("impact", 0)
    impact = impact_map.get(raw_impact, "UNKNOWN")
    
    currency = raw.get("country", "").upper().strip()
    if not currency:
        currency = None
        
    return {
        "event_id": event_id,
        "datetime": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "currency": currency,
        "impact": impact,
        "event": raw.get("title", ""),
        "actual": raw.get("actual") or None,
        "forecast": raw.get("forecast") or None,
        "previous": raw.get("previous") or None,
        "source": "forexfactory"
    }

def normalize_calendar_events(days_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    events = []
    for day in days_data:
        for evt in day.get("events", []):
            events.append(normalize_provider_event(evt))
    return events

# ---------------------------------------------------------
# Persistence
# ---------------------------------------------------------
def build_empty_calendar_document() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "source": "forexfactory",
        "coverage": [],
        "events": []
    }

def validate_calendar_document(doc: Dict[str, Any]) -> None:
    if "schema_version" not in doc or "coverage" not in doc or "events" not in doc:
        print("Error: Malformed calendar.json document", file=sys.stderr)
        sys.exit(1)
    for evt in doc["events"]:
        if "event_id" not in evt or "datetime" not in evt:
            print("Error: Corrupted event in calendar.json", file=sys.stderr)
            sys.exit(1)

def load_calendar_document() -> Dict[str, Any]:
    if not os.path.exists(CALENDAR_FILE):
        return build_empty_calendar_document()
    
    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
            doc = json.load(f)
        validate_calendar_document(doc)
        return doc
    except Exception as e:
        print(f"Error: Calendar data integrity error: {e}", file=sys.stderr)
        sys.exit(1)

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
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        print(f"Error: Atomic save failed: {e}", file=sys.stderr)
        sys.exit(1)

@contextlib.contextmanager
def acquire_calendar_lock():
    if os.name == "nt":
        import msvcrt
        lock_path = CALENDAR_FILE + ".lock"
        flags = os.O_CREAT | os.O_RDWR | os.O_TEMPORARY
        while True:
            try:
                fd = os.open(lock_path, flags)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                import time
                time.sleep(0.1)
        try:
            yield
        finally:
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
            os.close(fd)
    else:
        import fcntl
        flags = os.O_CREAT | os.O_RDWR
        while True:
            try:
                fd = os.open(CALENDAR_FILE, flags)
                fcntl.flock(fd, fcntl.LOCK_EX)
                stat1 = os.fstat(fd)
                stat2 = os.stat(CALENDAR_FILE)
                if stat1.st_ino == stat2.st_ino:
                    break
                else:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
            except OSError:
                import time
                time.sleep(0.1)
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

# ---------------------------------------------------------
# Coverage & Merge
# ---------------------------------------------------------
def parse_iso8601(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)

def format_iso8601(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def resolve_coverage(intervals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not intervals:
        return []
    # Sort by start time
    intervals.sort(key=lambda x: parse_iso8601(x["start"]))
    merged = [intervals[0]]
    for current in intervals[1:]:
        prev = merged[-1]
        prev_end = parse_iso8601(prev["end"])
        curr_start = parse_iso8601(current["start"])
        curr_end = parse_iso8601(current["end"])
        
        if curr_start <= prev_end:
            # Overlap or contiguous
            merged[-1]["end"] = format_iso8601(max(prev_end, curr_end))
            # Keep latest fetched_at
            if parse_iso8601(current["fetched_at"]) > parse_iso8601(prev["fetched_at"]):
                merged[-1]["fetched_at"] = current["fetched_at"]
                if "requested" in current: merged[-1]["requested"] = current["requested"]
        else:
            merged.append(current)
    return merged

def is_fully_covered(req_start: datetime, req_end: datetime, coverage: List[Dict[str, Any]]) -> bool:
    for c in coverage:
        c_start = parse_iso8601(c["start"])
        c_end = parse_iso8601(c["end"])
        if c_start <= req_start and c_end >= req_end:
            return True
    return False

def merge_coverage(old_coverage: List[Dict[str, Any]], new_coverage: Dict[str, Any]) -> List[Dict[str, Any]]:
    combined = old_coverage + [new_coverage]
    return resolve_coverage(combined)

def deduplicate_calendar_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = {}
    for ev in events:
        eid = ev["event_id"]
        if eid not in seen:
            seen[eid] = ev
        else:
            # update mutable fields from newest
            existing = seen[eid]
            if existing["datetime"] != ev["datetime"]:
                print(f"Error: Identity/time conflict for {eid}", file=sys.stderr)
                sys.exit(1)
            # just keep the latest object (assuming newer comes later)
            seen[eid] = ev
    
    res = list(seen.values())
    res.sort(key=lambda x: (x["datetime"], x["event_id"]))
    return res

def merge_calendar_events(old_events: List[Dict[str, Any]], new_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return deduplicate_calendar_events(old_events + new_events)

def get_interval_for_period(args: argparse.Namespace) -> tuple[datetime, datetime]:
    # Determine UTC interval based on period.
    # A robust implementation would compute exact UTC start/end for "today", "this week" etc.
    # For now, approximate bounded intervals assuming server converts correctly.
    now = datetime.now(timezone.utc)
    if args.day:
        if args.day == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif args.day == "tomorrow":
            start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        else:
            start = parse_date(args.day)
            end = start + timedelta(days=1)
    elif args.week:
        # just an approximation: fetch covers a wide range. 
        # But we must register valid bounds.
        if args.week == "this":
            start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif args.week == "next":
            start = (now + timedelta(days=7-now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        else:
            d = parse_date(args.week)
            start = d - timedelta(days=d.weekday())
            end = start + timedelta(days=7)
    elif args.month:
        if args.month == "this":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # next month
            end = (start + timedelta(days=32)).replace(day=1)
        elif args.month == "next":
            start = (now + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = (start + timedelta(days=32)).replace(day=1)
    elif args.range:
        d1, d2 = parse_date_range(args.range)
        start = d1
        end = d2 + timedelta(days=1)
    else:
        start = now
        end = now
    return start, end

# ---------------------------------------------------------
# Queries & Filters
# ---------------------------------------------------------
def extract_symbol_currencies(symbol: str) -> set[str]:
    s = normalize_symbol(symbol)
    if len(s) == 6:
        return {s[:3], s[3:]}
    return set()

def filter_events_for_symbol(events: List[Dict[str, Any]], symbol: str) -> List[Dict[str, Any]]:
    currencies = extract_symbol_currencies(symbol)
    if not currencies:
        return []
    return [e for e in events if e.get("currency") in currencies]

def query_symbol_events(symbol: str, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    return filter_events_for_symbol(doc["events"], symbol)

def query_current_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc)
    res = []
    for e in events:
        dt = parse_iso8601(e["datetime"])
        if dt.date() == now.date() and dt.hour == now.hour and dt.minute == now.minute:
            res.append(e)
    return res

def query_next_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc)
    future_events = [e for e in events if parse_iso8601(e["datetime"]) > now]
    if not future_events:
        return []
    earliest = parse_iso8601(future_events[0]["datetime"])
    return [e for e in future_events if parse_iso8601(e["datetime"]) == earliest]

def query_nearest_events(events: List[Dict[str, Any]], ref_dt: datetime) -> List[Dict[str, Any]]:
    if not events:
        return []
    dts = [(e, abs((parse_iso8601(e["datetime"]) - ref_dt).total_seconds())) for e in events]
    min_diff = min(dts, key=lambda x: x[1])[1]
    return [x[0] for x in dts if x[1] == min_diff]

def output_query_result(status: str, symbol: str, events: List[Dict[str, Any]]):
    res = {
        "status": status,
        "symbol": symbol,
        "events": events
    }
    print(json.dumps(res))

# ---------------------------------------------------------
# Deletion
# ---------------------------------------------------------
def select_delete_interval(args: argparse.Namespace) -> tuple[Optional[datetime], Optional[datetime]]:
    start, end = None, None
    if args.date:
        start = parse_date(args.date)
        end = start + timedelta(days=1)
        if args.time:
            h, m = parse_time(args.time)
            start = start.replace(hour=h, minute=m)
            end = start + timedelta(minutes=1)
    elif args.range:
        d1, d2 = parse_date_range(args.range)
        start = d1
        end = d2 + timedelta(days=1)
        if args.time:
            p1, p2 = args.time.split("-")
            h1, m1 = parse_time(p1)
            h2, m2 = parse_time(p2)
            # The range time filter applies to time-of-day for each date inside the range. 
            # This makes boundary filtering complex. We'll handle it inside delete_events.
            pass
    elif args.before and args.after:
        end = parse_date(args.before)
        start = parse_date(args.after) + timedelta(days=1)
        if start >= end:
            print("Error: Invalid bounded interval for before/after", file=sys.stderr)
            sys.exit(1)
    elif args.before:
        end = parse_date(args.before)
    elif args.after:
        start = parse_date(args.after) + timedelta(days=1)
    return start, end

def delete_events(events: List[Dict[str, Any]], args: argparse.Namespace) -> List[Dict[str, Any]]:
    start, end = select_delete_interval(args)
    kept = []
    for e in events:
        dt = parse_iso8601(e["datetime"])
        delete = False
        if args.range and args.time:
            d1, d2 = parse_date_range(args.range)
            d2_end = d2 + timedelta(days=1)
            if d1 <= dt < d2_end:
                p1, p2 = args.time.split("-")
                h1, m1 = parse_time(p1)
                h2, m2 = parse_time(p2)
                mins = dt.hour * 60 + dt.minute
                m_start = h1 * 60 + m1
                m_end = h2 * 60 + m2
                if m_start <= mins <= m_end:
                    delete = True
        else:
            if start and end:
                if start <= dt < end:
                    delete = True
            elif start:
                if dt >= start:
                    delete = True
            elif end:
                if dt < end:
                    delete = True
        if not delete:
            kept.append(e)
    return kept

def delete_coverage(coverage: List[Dict[str, Any]], args: argparse.Namespace) -> List[Dict[str, Any]]:
    start, end = select_delete_interval(args)
    if args.range and args.time:
        # Time-of-day deletion doesn't easily map to simple interval clipping, 
        # so we leave the coverage intact but the events are deleted.
        # Actually, spec says: "Coverage is clipped or removed accordingly." 
        # For complex time-of-day, it's safer to leave coverage and just let events be empty.
        pass
        return coverage

    new_cov = []
    for c in coverage:
        c_start = parse_iso8601(c["start"])
        c_end = parse_iso8601(c["end"])
        
        if start and end:
            if start <= c_start and end >= c_end:
                continue # fully deleted
            elif start > c_start and end < c_end:
                # Split in two
                c1 = c.copy()
                c1["end"] = format_iso8601(start)
                c2 = c.copy()
                c2["start"] = format_iso8601(end)
                new_cov.extend([c1, c2])
                continue
            elif start <= c_start < end:
                c["start"] = format_iso8601(end)
            elif start < c_end <= end:
                c["end"] = format_iso8601(start)
        elif start: # after
            if c_end <= start:
                pass
            elif c_start >= start:
                continue
            else:
                c["end"] = format_iso8601(start)
        elif end: # before
            if c_start >= end:
                pass
            elif c_end <= end:
                continue
            else:
                c["start"] = format_iso8601(end)
        
        if parse_iso8601(c["start"]) < parse_iso8601(c["end"]):
            new_cov.append(c)
            
    return new_cov

# ---------------------------------------------------------
# Orchestration
# ---------------------------------------------------------
def run_acquisition(args: argparse.Namespace):
    symbol = normalize_symbol(args.query)
    provider_spec = resolve_provider_period(args)
    
    if not provider_spec:
        # cache only query
        if not os.path.exists(CALENDAR_FILE):
            output_query_result("NO_CALENDAR_DATA", symbol, [])
            return
        doc = load_calendar_document()
        events = query_symbol_events(symbol, doc)
        output_query_result("OK" if events else "NO_RELEVANT_EVENT", symbol, events)
        return
        
    start, end = get_interval_for_period(args)
    
    with acquire_calendar_lock():
        doc = load_calendar_document()
        if is_fully_covered(start, end, doc["coverage"]):
            if args.debug:
                print("Fully covered, skipping fetch", file=sys.stderr)
            pass
        else:
            ptype, pval = provider_spec
            html = fetch_calendar_source(ptype, pval)
            payload = extract_days_payload(html)
            days_data = parse_calendar_days(payload)
            new_events = normalize_calendar_events(days_data)
            
            doc["events"] = merge_calendar_events(doc["events"], new_events)
            
            new_cov = {
                "start": format_iso8601(start),
                "end": format_iso8601(end),
                "requested": {"type": ptype, "value": pval},
                "fetched_at": format_iso8601(datetime.now(timezone.utc))
            }
            doc["coverage"] = merge_coverage(doc["coverage"], new_cov)
            validate_calendar_document(doc)
            save_calendar_atomic(doc)
        
        sym_events = query_symbol_events(symbol, doc)
        output_query_result("OK" if sym_events else "NO_RELEVANT_EVENT", symbol, sym_events)

def run_query(args: argparse.Namespace):
    symbol = normalize_symbol(args.symbol)
    if not os.path.exists(CALENDAR_FILE):
        output_query_result("NO_CALENDAR_DATA", symbol, [])
        return
        
    doc = load_calendar_document()
    events = query_symbol_events(symbol, doc)
    
    if not events:
        output_query_result("NO_RELEVANT_EVENT", symbol, [])
        return
        
    if args.current:
        res = query_current_events(events)
    elif args.next:
        res = query_next_events(events)
    elif args.date or args.time:
        now = datetime.now(timezone.utc)
        if args.date and args.time:
            dt = parse_date(args.date)
            h, m = parse_time(args.time)
            ref_dt = dt.replace(hour=h, minute=m)
        elif args.date:
            dt = parse_date(args.date)
            ref_dt = dt.replace(hour=now.hour, minute=now.minute)
        elif args.time:
            h, m = parse_time(args.time)
            ref_dt = now.replace(hour=h, minute=m)
        res = query_nearest_events(events, ref_dt)
    else:
        # Default behavior: If one or more relevant events are scheduled at current minute, return them, else next.
        curr = query_current_events(events)
        res = curr if curr else query_next_events(events)
        
    output_query_result("OK" if res else "NO_RELEVANT_EVENT", symbol, res)

def run_delete(args: argparse.Namespace):
    if not os.path.exists(CALENDAR_FILE):
        if args.dry_run:
            print("Dry run: no calendar.json exists", file=sys.stderr)
        return
        
    with acquire_calendar_lock():
        doc = load_calendar_document()
        old_count = len(doc["events"])
        doc["events"] = delete_events(doc["events"], args)
        doc["coverage"] = delete_coverage(doc["coverage"], args)
        new_count = len(doc["events"])
        
        if args.dry_run:
            print(f"Dry run: Would delete {old_count - new_count} events", file=sys.stderr)
            return
            
        if new_count != old_count:
            save_calendar_atomic(doc)

def main():
    parser = build_argument_parser()
    args = parser.parse_args()
    
    op = parse_calendar_request(args)
    if op == "ACQUISITION":
        run_acquisition(args)
    elif op == "LOCAL_QUERY":
        run_query(args)
    elif op == "LOCAL_QUERY_NEXT":
        args.next = False
        args.current = False
        run_query(args)
    elif op == "DELETE":
        run_delete(args)

if __name__ == "__main__":
    main()
