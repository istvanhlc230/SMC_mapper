import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Set
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
    parser.add_argument("--query", type=str)
    parser.add_argument("--day", type=str)
    parser.add_argument("--week", type=str)
    parser.add_argument("--month", type=str)
    parser.add_argument("--symbol", type=str)
    parser.add_argument("--current", action="store_true")
    parser.add_argument("--next", action="store_true")
    parser.add_argument("--date", type=str)
    parser.add_argument("--time", type=str)
    parser.add_argument("--range", type=str)
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--before", type=str)
    parser.add_argument("--after", type=str)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser

def parse_calendar_request(args: argparse.Namespace) -> str:
    acq = bool(args.query)
    loc = bool(args.symbol)
    del_ = bool(args.delete)
    
    if sum([acq, loc, del_]) != 1:
        sys.exit("Error: Must specify exactly one operation family: --query, --symbol, or --delete")
        
    if acq:
        if any([args.current, args.next, args.delete, args.before, args.after, args.dry_run, args.date, args.time]):
            sys.exit("Error: Invalid arguments mixed with acquisition")
        periods = [args.day, args.week, args.month, args.range]
        if sum(x is not None for x in periods) > 1:
            sys.exit("Error: Multiple period selectors")
        return "ACQUISITION"
    elif loc:
        if any([args.day, args.week, args.month, args.range, args.delete, args.before, args.after, args.dry_run]):
            sys.exit("Error: Invalid arguments mixed with local query")
        if args.current and args.next:
            sys.exit("Error: Cannot mix --current and --next")
        if args.date and not args.time:
            pass
        return "LOCAL_QUERY"
    elif del_:
        if any([args.day, args.week, args.month, args.current, args.next]):
            sys.exit("Error: Invalid arguments mixed with delete")
        if args.range and any([args.before, args.after, args.date]):
            sys.exit("Error: --range cannot be combined with --before, --after, or --date")
        if args.date and any([args.before, args.after, args.range]):
            sys.exit("Error: --date cannot be combined with --before, --after, or --range")
        if not any([args.before, args.after, args.range, args.date]):
            sys.exit("Error: Delete requires a valid boundary selector")
        return "DELETE"
    return "UNKNOWN"

def normalize_symbol(symbol: str) -> str:
    return symbol.upper().strip()

def parse_date(date_str: str) -> datetime:
    try:
        parts = date_str.split(".")
        if len(parts) != 3: raise ValueError
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        if not (2000 <= y <= 2100): raise ValueError
        return datetime(y, m, d, tzinfo=timezone.utc)
    except Exception:
        sys.exit(f"Error: Invalid date format: {date_str}. Expected YYYY.MM.DD")

def parse_time(time_str: str) -> Tuple[int, int]:
    try:
        parts = time_str.split(":")
        if len(parts) != 2: raise ValueError
        h, m = int(parts[0]), int(parts[1])
        if not (0 <= h <= 23 and 0 <= m <= 59): raise ValueError
        return h, m
    except Exception:
        sys.exit(f"Error: Invalid time format: {time_str}. Expected HH:MM")

def parse_date_range(range_str: str) -> Tuple[datetime, datetime]:
    parts = range_str.split("-")
    if len(parts) != 2:
        sys.exit("Error: Invalid range format. Expected YYYY.MM.DD-YYYY.MM.DD")
    d1 = parse_date(parts[0])
    d2 = parse_date(parts[1])
    if d1 > d2:
        sys.exit("Error: Reversed date range")
    return d1, d2

# ---------------------------------------------------------
# Provider / Network
# ---------------------------------------------------------
def resolve_provider_period(args: argparse.Namespace) -> Optional[Tuple[str, str]]:
    if args.day:
        if args.day in ("today", "tomorrow"): return ("day", args.day)
        return ("day", parse_date(args.day).strftime("%b%d.%Y").lower())
    elif args.week:
        if args.week in ("this", "next"): return ("week", args.week)
        return ("week", parse_date(args.week).strftime("%b%d.%Y").lower())
    elif args.month:
        if args.month in ("this", "next"): return ("month", args.month)
    elif args.range:
        d1, d2 = parse_date_range(args.range)
        return ("range", f"{d1.strftime('%b%d.%Y').lower()}-{d2.strftime('%b%d.%Y').lower()}")
    return None

def fetch_calendar_source(period_type: str, period_value: str) -> str:
    url = f"{PROVIDER_URL}?{period_type}={period_value}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        import urllib.request
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

def parse_calendar_days(json_str: str) -> List[Dict[str, Any]]:
    try:
        return json.loads(json_str)
    except Exception as e:
        sys.exit(f"Error: Malformed provider payload: {e}")

# ---------------------------------------------------------
# Normalization
# ---------------------------------------------------------
def normalize_provider_event(raw: Dict[str, Any]) -> Dict[str, Any]:
    if "id" not in raw or "dateline" not in raw:
        sys.exit("Error: Missing required provider fields")
    event_id = f"forexfactory:{raw['id']}"
    try:
        ts = int(raw["dateline"])
        dt = datetime.fromtimestamp(ts, timezone.utc)
    except Exception:
        sys.exit("Error: Invalid event dateline")
    
    impact_map = {1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "HOLIDAY"}
    impact = impact_map.get(raw.get("impact"), "UNKNOWN")
    currency = raw.get("country", "").upper().strip() or None
    
    return {
        "event_id": event_id,
        "datetime": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "currency": currency,
        "impact": impact,
        "event": str(raw.get("title", "")),
        "actual": str(raw["actual"]) if raw.get("actual") is not None and raw.get("actual") != "" else None,
        "forecast": str(raw["forecast"]) if raw.get("forecast") is not None and raw.get("forecast") != "" else None,
        "previous": str(raw["previous"]) if raw.get("previous") is not None and raw.get("previous") != "" else None,
        "source": "forexfactory"
    }

def normalize_calendar_events(days_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    events = []
    for day in days_data:
        for evt in day.get("events", []):
            events.append(normalize_provider_event(evt))
    return events

# ---------------------------------------------------------
# Persistence & Validation
# ---------------------------------------------------------
def build_empty_calendar_document() -> Dict[str, Any]:
    return {"schema_version": 1, "source": "forexfactory", "coverage": [], "events": []}

def parse_iso8601(ts: str) -> datetime:
    if ts.endswith("Z"): ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)

def format_iso8601(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def validate_calendar_document(doc: Dict[str, Any]) -> None:
    if doc.get("schema_version") != 1: sys.exit("Error: Invalid schema version")
    if doc.get("source") != "forexfactory": sys.exit("Error: Invalid source")
    if not isinstance(doc.get("coverage"), list): sys.exit("Error: Invalid coverage")
    for c in doc["coverage"]:
        if "start" not in c or "end" not in c or "fetched_at" not in c or "requested" not in c:
            sys.exit("Error: Malformed coverage")
        if parse_iso8601(c["start"]) >= parse_iso8601(c["end"]): sys.exit("Error: Invalid coverage bounds")
    if not isinstance(doc.get("events"), list): sys.exit("Error: Invalid events")
    seen_ids = set()
    for e in doc["events"]:
        if "event_id" not in e or "datetime" not in e or "impact" not in e: sys.exit("Error: Corrupt event")
        if e["impact"] not in ["HIGH", "MEDIUM", "LOW", "HOLIDAY", "UNKNOWN"]: sys.exit("Error: Invalid impact")
        eid = e["event_id"]
        if eid in seen_ids: sys.exit("Error: Duplicate event ID")
        seen_ids.add(eid)
        parse_iso8601(e["datetime"])

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

@contextlib.contextmanager
def acquire_calendar_lock():
    lock_path = CALENDAR_FILE + ".lock"
    if os.name == "nt":
        import msvcrt
        flags = os.O_CREAT | os.O_RDWR | os.O_TEMPORARY
        while True:
            try:
                fd = os.open(lock_path, flags)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                import time; time.sleep(0.1)
        try:
            yield
        finally:
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            except OSError: pass
            os.close(fd)
    else:
        import fcntl
        flags = os.O_CREAT | os.O_RDWR
        while True:
            try:
                fd = os.open(lock_path, flags)
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                import time; time.sleep(0.1)
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            try:
                os.unlink(lock_path)
            except OSError: pass

# ---------------------------------------------------------
# Coverage & Merge
# ---------------------------------------------------------
def resolve_coverage(intervals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not intervals: return []
    intervals.sort(key=lambda x: parse_iso8601(x["start"]))
    merged = [intervals[0]]
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
            merged.append(current)
    return merged

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

def merge_coverage(old_coverage: List[Dict[str, Any]], new_coverage: Dict[str, Any]) -> List[Dict[str, Any]]:
    return resolve_coverage(old_coverage + [new_coverage])

def deduplicate_calendar_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = {}
    for ev in events:
        eid = ev["event_id"]
        if eid not in seen:
            seen[eid] = ev
        else:
            if seen[eid]["datetime"] != ev["datetime"]:
                sys.exit(f"Error: Identity/time conflict for {eid}")
            seen[eid] = ev
    res = list(seen.values())
    res.sort(key=lambda x: (parse_iso8601(x["datetime"]), x["event_id"]))
    return res

def merge_calendar_events(old_events: List[Dict[str, Any]], new_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return deduplicate_calendar_events(old_events + new_events)

def get_interval_for_period(args: argparse.Namespace) -> Tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    if args.day:
        if args.day == "today": start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif args.day == "tomorrow": start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        else: start = parse_date(args.day)
        end = start + timedelta(days=1)
    elif args.week:
        if args.week == "this": start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        elif args.week == "next": start = (now + timedelta(days=7-now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        else: d = parse_date(args.week); start = d - timedelta(days=d.weekday())
        end = start + timedelta(days=7)
    elif args.month:
        if args.month == "this": start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0); end = (start + timedelta(days=32)).replace(day=1)
        elif args.month == "next": start = (now + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0); end = (start + timedelta(days=32)).replace(day=1)
    elif args.range:
        d1, d2 = parse_date_range(args.range)
        start, end = d1, d2 + timedelta(days=1)
    else:
        start, end = now, now
    return start, end

# ---------------------------------------------------------
# Queries & Filters
# ---------------------------------------------------------
def extract_symbol_currencies(symbol: str) -> Set[str]:
    s = normalize_symbol(symbol).replace("-", "").replace("/", "").replace("_", "")
    if len(s) == 6 and s.isalpha(): return {s[:3], s[3:]}
    return set()

def filter_events_for_symbol(events: List[Dict[str, Any]], symbol: str) -> List[Dict[str, Any]]:
    currencies = extract_symbol_currencies(symbol)
    if not currencies: return []
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
    res.sort(key=lambda x: (parse_iso8601(x["datetime"]), x["event_id"]))
    return res

def query_next_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc)
    future = [e for e in events if parse_iso8601(e["datetime"]) > now]
    if not future: return []
    future.sort(key=lambda x: (parse_iso8601(x["datetime"]), x["event_id"]))
    earliest = future[0]["datetime"]
    return [e for e in future if e["datetime"] == earliest]

def query_nearest_events(events: List[Dict[str, Any]], ref_dt: datetime) -> List[Dict[str, Any]]:
    if not events: return []
    dts = [(e, abs((parse_iso8601(e["datetime"]) - ref_dt).total_seconds())) for e in events]
    min_diff = min(dts, key=lambda x: x[1])[1]
    res = [x[0] for x in dts if x[1] == min_diff]
    res.sort(key=lambda x: (parse_iso8601(x["datetime"]), x["event_id"]))
    return res

def output_query_result(status: str, symbol: str, events: List[Dict[str, Any]]):
    print(json.dumps({"status": status, "symbol": symbol, "events": events}))

# ---------------------------------------------------------
# Deletion
# ---------------------------------------------------------
def select_delete_interval(args: argparse.Namespace) -> Tuple[Optional[datetime], Optional[datetime]]:
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
        start, end = d1, d2 + timedelta(days=1)
    elif args.before and args.after:
        end = parse_date(args.before)
        start = parse_date(args.after) + timedelta(days=1)
        if start >= end: sys.exit("Error: Invalid bounded interval for before/after")
    elif args.before:
        end = parse_date(args.before)
    elif args.after:
        start = parse_date(args.after) + timedelta(days=1)
    return start, end

def get_deleted_ranges(args: argparse.Namespace) -> List[Tuple[Optional[datetime], Optional[datetime]]]:
    start, end = select_delete_interval(args)
    if args.range and args.time:
        d1, d2 = parse_date_range(args.range)
        h1, m1 = parse_time(args.time.split("-")[0])
        h2, m2 = parse_time(args.time.split("-")[1])
        ranges = []
        curr = d1
        while curr <= d2:
            s = curr.replace(hour=h1, minute=m1)
            e = curr.replace(hour=h2, minute=m2) + timedelta(minutes=1)
            ranges.append((s, e))
            curr += timedelta(days=1)
        return ranges
    return [(start, end)]

def delete_events(events: List[Dict[str, Any]], args: argparse.Namespace) -> List[Dict[str, Any]]:
    ranges = get_deleted_ranges(args)
    kept = []
    for e in events:
        dt = parse_iso8601(e["datetime"])
        delete = False
        for s, end_t in ranges:
            if s and end_t:
                if s <= dt < end_t: delete = True
            elif s:
                if dt >= s: delete = True
            elif end_t:
                if dt < end_t: delete = True
        if not delete: kept.append(e)
    return kept

def delete_coverage(coverage: List[Dict[str, Any]], args: argparse.Namespace) -> List[Dict[str, Any]]:
    ranges = get_deleted_ranges(args)
    current_cov = coverage
    for start, end in ranges:
        new_cov = []
        for c in current_cov:
            cs = parse_iso8601(c["start"])
            ce = parse_iso8601(c["end"])
            if start and end:
                if start <= cs and end >= ce: continue
                elif start > cs and end < ce:
                    c1, c2 = c.copy(), c.copy()
                    c1["end"] = format_iso8601(start)
                    c2["start"] = format_iso8601(end)
                    new_cov.extend([c1, c2])
                    continue
                elif start <= cs < end: c["start"] = format_iso8601(end)
                elif start < ce <= end: c["end"] = format_iso8601(start)
            elif start:
                if cs >= start: continue
                elif ce > start: c["end"] = format_iso8601(start)
            elif end:
                if ce <= end: continue
                elif cs < end: c["start"] = format_iso8601(end)
            if parse_iso8601(c["start"]) < parse_iso8601(c["end"]):
                new_cov.append(c)
        current_cov = resolve_coverage(new_cov)
    return current_cov

def dry_run_delete(args: argparse.Namespace):
    if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:
        print("Dry run: no calendar data exists", file=sys.stderr)
        return
    doc = load_calendar_document()
    old_count = len(doc["events"])
    new_events = delete_events(doc["events"], args)
    deleted_count = old_count - len(new_events)
    print(f"Dry run: {deleted_count} events match deletion selectors.", file=sys.stderr)

# ---------------------------------------------------------
# Orchestration
# ---------------------------------------------------------
def run_acquisition(args: argparse.Namespace):
    symbol = normalize_symbol(args.query)
    provider_spec = resolve_provider_period(args)
    if not provider_spec:
        if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:
            output_query_result("NO_CALENDAR_DATA", symbol, [])
            return
        doc = load_calendar_document()
        events = query_symbol_events(symbol, doc)
        output_query_result("OK" if events else "NO_RELEVANT_EVENT", symbol, events)
        return
        
    start, end = get_interval_for_period(args)
    with acquire_calendar_lock():
        doc = load_calendar_document()
        uncovered = find_uncovered_intervals(start, end, doc["coverage"])
        if not uncovered:
            pass # fully covered
        else:
            now = datetime.now(timezone.utc)
            for u_start, u_end in uncovered:
                # Use provider range to fetch exact uncovered interval
                d1_str = u_start.strftime("%b%d.%Y").lower()
                d2_str = (u_end - timedelta(days=1)).strftime("%b%d.%Y").lower()
                pval = f"{d1_str}-{d2_str}"
                html = fetch_calendar_source("range", pval)
                payload = extract_days_payload(html)
                days_data = parse_calendar_days(payload)
                new_events = normalize_calendar_events(days_data)
                doc["events"] = merge_calendar_events(doc["events"], new_events)
                doc["coverage"] = merge_coverage(doc["coverage"], {
                    "start": format_iso8601(u_start),
                    "end": format_iso8601(u_end),
                    "requested": {"type": "range", "value": pval},
                    "fetched_at": format_iso8601(now)
                })
            validate_calendar_document(doc)
            save_calendar_atomic(doc)
        sym_events = query_symbol_events(symbol, doc)
        output_query_result("OK" if sym_events else "NO_RELEVANT_EVENT", symbol, sym_events)

def run_query(args: argparse.Namespace):
    symbol = normalize_symbol(args.symbol)
    if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:
        output_query_result("NO_CALENDAR_DATA", symbol, [])
        return
    doc = load_calendar_document()
    events = query_symbol_events(symbol, doc)
    if not events:
        output_query_result("NO_RELEVANT_EVENT", symbol, [])
        return
    if args.current: res = query_current_events(events)
    elif args.next: res = query_next_events(events)
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
        curr = query_current_events(events)
        res = curr if curr else query_next_events(events)
    output_query_result("OK" if res else "NO_RELEVANT_EVENT", symbol, res)

def run_delete(args: argparse.Namespace):
    if args.dry_run:
        dry_run_delete(args)
        return
    if not os.path.exists(CALENDAR_FILE) or os.path.getsize(CALENDAR_FILE) == 0:
        return
    with acquire_calendar_lock():
        doc = load_calendar_document()
        old_count = len(doc["events"])
        doc["events"] = delete_events(doc["events"], args)
        doc["coverage"] = delete_coverage(doc["coverage"], args)
        if len(doc["events"]) != old_count or len(doc["coverage"]) != len(doc.get("coverage", [])):
            save_calendar_atomic(doc)

def run():
    parser = build_argument_parser()
    args = parser.parse_args()
    op = parse_calendar_request(args)
    if op == "ACQUISITION": run_acquisition(args)
    elif op == "LOCAL_QUERY": run_query(args)
    elif op == "DELETE": run_delete(args)

def main():
    run()

if __name__ == "__main__":
    main()
