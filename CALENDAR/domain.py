"""Calendar semantic/domain operations independent of provider I/O."""

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from .config import CalendarInputError, DataIntegrityError, DATE_RE, FX_CURRENCY_CODES, SCHEMA_VERSION, SUPPORTED_CURRENCIES, TIME_RE

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
    if scope in {"current", "latest", "next"}:
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

def _validate_calendar_event(event: Dict[str, Any], event_ids: set[str]) -> None:
    if not isinstance(event, dict):
        raise DataIntegrityError("Invalid event record.")
    required = {"event_id", "symbol", "asset_type", "event_type", "source", "timestamp", "title", "details"}
    missing = required.difference(event)
    if missing:
        raise DataIntegrityError(f"Corrupt event; missing {sorted(missing)}.")
    event_id = event["event_id"]
    if not isinstance(event_id, str) or not event_id:
        raise DataIntegrityError("Invalid event_id.")
    if event_id in event_ids:
        raise DataIntegrityError("Duplicate event_id.")
    event_ids.add(event_id)
    if event["event_type"] not in {"economic", "news", "earnings", "press_release", "sec_filing"}:
        raise DataIntegrityError("Invalid event_type.")
    if event["source"] not in {"forexfactory", "yahoo_finance"}:
        raise DataIntegrityError("Invalid event source.")
    if event["asset_type"] not in {"forex", "ticker"}:
        raise DataIntegrityError("Invalid asset_type.")
    if not isinstance(event["symbol"], str) or not event["symbol"]:
        raise DataIntegrityError("Invalid event symbol.")
    suppressed_for = event.get("suppressed_for", [])
    if not isinstance(suppressed_for, list) or any(not isinstance(item, str) or not item for item in suppressed_for):
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
            raise DataIntegrityError("ForexFactory events must use event_type=economic.")
        _validate_forexfactory_details(event["details"])
    elif event["event_type"] != "news":
        raise DataIntegrityError("Yahoo Finance events must use event_type=news.")

def _validate_forexfactory_details(details: Dict[str, Any]) -> None:
    if details.get("currency") not in FX_CURRENCY_CODES and details.get("currency") != "ALL":
        raise DataIntegrityError("Invalid ForexFactory currency.")
    if details.get("impact") not in {"HIGH", "MEDIUM", "LOW", "HOLIDAY", "UNKNOWN"}:
        raise DataIntegrityError("Invalid ForexFactory impact.")
    specs = details.get("specs", [])
    if not isinstance(specs, list):
        raise DataIntegrityError("Invalid ForexFactory specs.")
    for spec in specs:
        if not isinstance(spec, dict) or set(spec) != {"order", "title", "html"}:
            raise DataIntegrityError("Invalid ForexFactory detail spec.")
        if isinstance(spec["order"], bool):
            raise DataIntegrityError("Invalid ForexFactory detail spec order.")
        try:
            order = int(spec["order"])
        except (TypeError, ValueError) as exc:
            raise DataIntegrityError("Invalid ForexFactory detail spec order.") from exc
        if not isinstance(spec["order"], int) and not (isinstance(spec["order"], str) and str(order) == spec["order"]):
            raise DataIntegrityError("Invalid ForexFactory detail spec order.")
        if not isinstance(spec["title"], str) or not spec["title"].strip():
            raise DataIntegrityError("ForexFactory detail spec title must not be empty.")
        if not isinstance(spec["html"], str):
            raise DataIntegrityError("ForexFactory detail spec html must be a string.")

def _validate_coverage_records(records: List[Dict[str, Any]]) -> None:
    seen = set()
    for coverage in records:
        if not isinstance(coverage, dict):
            raise DataIntegrityError("Invalid coverage record.")
        for field in ("provider", "symbol", "start", "end", "status"):
            if field not in coverage:
                raise DataIntegrityError(f"Malformed coverage; missing '{field}'.")
        if coverage["provider"] not in {"forexfactory", "yahoo_finance"}:
            raise DataIntegrityError("Invalid coverage provider.")
        start = parse_iso8601(coverage["start"])
        end = parse_iso8601(coverage["end"])
        if end <= start:
            raise DataIntegrityError("Invalid coverage interval.")
        if coverage["status"] not in {"COMPLETE", "PARTIAL"}:
            raise DataIntegrityError("Invalid coverage status.")
        key = (coverage["provider"], coverage["symbol"], coverage["start"], coverage["end"])
        if key in seen:
            raise DataIntegrityError("Duplicate coverage entry.")
        seen.add(key)

def _validate_watermarks(watermarks: Dict[str, Any]) -> None:
    for key, watermark in watermarks.items():
        if not isinstance(watermark, dict):
            raise DataIntegrityError("Invalid watermark record.")
        if "|" not in key:
            raise DataIntegrityError("Invalid watermark key.")
        provider, symbol = key.split("|", 1)
        if provider not in {"forexfactory", "yahoo_finance"} or not symbol:
            raise DataIntegrityError("Invalid watermark identity.")
        for field in ("last_successful_at", "last_event_timestamp"):
            if field not in watermark:
                raise DataIntegrityError(f"Malformed watermark; missing '{field}'.")
            value = watermark[field]
            if value is not None:
                parse_iso8601(value)

def validate_calendar_document(document: Dict[str, Any]) -> None:
    """Validate the complete persisted Calendar document."""
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
    event_ids: set[str] = set()
    for event in document["events"]:
        _validate_calendar_event(event, event_ids)
    _validate_coverage_records(document["coverage"])
    _validate_watermarks(document["watermarks"])

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
            previous_start = parse_iso8601(previous["start"])
            previous_end = parse_iso8601(previous["end"])
            current_start = parse_iso8601(current["start"])
            current_end = parse_iso8601(current["end"])
            previous["end"] = format_iso8601(max(previous_end, current_end))

            if current["status"] == "PARTIAL":
                previous["status"] = "PARTIAL"
            elif previous["status"] == "PARTIAL":
                # A retry may re-acquire the exact partial interval
                # successfully. Promote only when the new COMPLETE record
                # fully covers the previously partial interval.
                if current_start <= previous_start and current_end >= previous_end:
                    previous["status"] = "COMPLETE"
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

def watermark_key(provider: str, symbol: str) -> str:
    return f"{provider}|{symbol}"

def resolve_applicable_providers(symbol: str) -> List[str]:
    if is_currency(symbol):
        return ["forexfactory"]
    if is_fx_pair(symbol):
        return ["forexfactory", "yahoo_finance"]
    return ["yahoo_finance"]

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

def query_current_events(
    events: List[Dict[str, Any]],
    since: datetime,
    until: datetime,
) -> List[Dict[str, Any]]:
    return [
        event for event in events
        if since < parse_iso8601(event["timestamp"]) <= until
    ]

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

def filter_query_events(
    document: Dict[str, Any],
    events: List[Dict[str, Any]],
    symbol: str,
    start: datetime,
    end: datetime,
    yahoo_pair_available: bool = True,
) -> List[Dict[str, Any]]:
    """Apply symbol visibility and coverage guards to cached results."""
    result: List[Dict[str, Any]] = []
    ff_coverage_valid = not bool(
        find_uncovered_intervals(document, "forexfactory", symbol, start, end)
    )
    for event in events:
        if (
            event["source"] == "yahoo_finance"
            and is_fx_pair(symbol)
            and not yahoo_pair_available
        ):
            continue
        if event["source"] == "forexfactory" and not ff_coverage_valid:
            continue
        result.append(event)
    return result
