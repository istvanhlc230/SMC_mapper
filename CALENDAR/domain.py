# (c) Istvan Jakab <istvanhlc230@gmail.com>
"""Calendar semantic/domain operations independent of provider I/O."""

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from .config import CalendarInputError, DataIntegrityError, DATE_RE, FX_CURRENCY_CODES, SCHEMA_VERSION, SUPPORTED_CURRENCIES, TIME_RE

# Module state: domain functions operate on the caller-owned Calendar document; no provider I/O or persistent module state is kept here.

def utc_now() -> datetime:
    """Calendar operation: utc_now performs the focused utc now step in the Calendar implementation."""
    return datetime.now(timezone.utc)

def format_iso8601(value: datetime) -> str:
    """Calendar operation: format_iso8601 performs the focused format iso8601 step in the Calendar implementation."""
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_iso8601(value: str) -> datetime:
    """Calendar operation: parse_iso8601 performs the focused parse iso8601 step in the Calendar implementation."""
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise DataIntegrityError(f"Invalid UTC timestamp '{value}'.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise DataIntegrityError(f"Non-UTC timestamp '{value}'.")
    return parsed.astimezone(timezone.utc)

def normalize_symbol(value: str) -> str:
    """Calendar operation: normalize_symbol performs the focused normalize symbol step in the Calendar implementation."""
    return value.strip().upper()

def is_currency(value: str) -> bool:
    """Calendar operation: is_currency performs the focused is currency step in the Calendar implementation."""
    return value in SUPPORTED_CURRENCIES

def canonicalize_fx_token(value: str) -> str:
    """Calendar operation: canonicalize_fx_token performs the focused canonicalize fx token step in the Calendar implementation."""
    return re.sub(r"[/_-]", "", value.strip().upper())

def is_fx_pair(value: str) -> bool:
    """Calendar operation: is_fx_pair performs the focused is fx pair step in the Calendar implementation."""
    token = canonicalize_fx_token(value)
    return (
        len(token) == 6
        and token[:3] in FX_CURRENCY_CODES
        and token[3:] in FX_CURRENCY_CODES
    )

def is_ticker(value: str) -> bool:
    """Calendar operation: is_ticker performs the focused is ticker step in the Calendar implementation."""
    token = normalize_symbol(value)
    if is_currency(token) or is_fx_pair(token):
        return False
    return bool(re.fullmatch(r"[A-Z0-9][A-Z0-9._-]{0,14}", token))

def validate_symbol(value: str) -> str:
    """Calendar operation: validate_symbol performs the focused validate symbol step in the Calendar implementation."""
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
    """Calendar operation: parse_time performs the focused parse time step in the Calendar implementation."""
    if not re.fullmatch(TIME_RE, value):
        raise CalendarInputError(f"Invalid time '{value}'. Expected HH:MM.")
    hour, minute = (int(part) for part in value.split(":"))
    if hour > 23 or minute > 59:
        raise CalendarInputError(f"Invalid time '{value}'. Expected HH:MM.")
    return hour, minute

def parse_date(value: str) -> datetime:
    """Calendar operation: parse_date performs the focused parse date step in the Calendar implementation."""
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
    """Calendar operation: parse_point performs the focused parse point step in the Calendar implementation."""
    if "@" not in value:
        return parse_date(value), False
    date_part, time_part = value.split("@", 1)
    base = parse_date(date_part)
    hour, minute = parse_time(time_part)
    return base.replace(hour=hour, minute=minute), True

def resolve_scope_interval(scope: str) -> Tuple[datetime, datetime]:
    """Calendar operation: resolve_scope_interval performs historical scope resolution."""
    if is_open_end_scope(scope):
        return resolve_open_end_scope(scope)

    # Relative day scopes use Calendar's canonical UTC clock rather than the
    # host-local date, so midnight boundaries remain deterministic.
    if scope in {"today", "tomorrow", "yesterday"}:
        today = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        offsets = {"today": 0, "yesterday": -1, "tomorrow": 1}
        start = today + timedelta(days=offsets[scope])
        return start, start + timedelta(days=1)

    if scope in {"current", "latest", "next", "prev", "news"}:
        raise CalendarInputError("'" + scope + "' is not a historical scope.")

    if scope in {"current day", "current week", "current month", "next day", "next week", "next month", "prev day", "prev week", "prev month"}:
        return resolve_relative_scope_interval(scope)

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


def resolve_relative_scope_interval(scope: str, now: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """Resolve current/next/prev day, week, and month scopes to UTC intervals."""
    current = (now or utc_now()).replace(hour=0, minute=0, second=0, microsecond=0)
    if scope == "current day":
        return current, current + timedelta(days=1)
    if scope == "next day":
        start = current + timedelta(days=1)
        return start, start + timedelta(days=1)
    if scope == "prev day":
        start = current - timedelta(days=1)
        return start, start + timedelta(days=1)

    week_start = current - timedelta(days=current.weekday())
    if scope == "current week":
        return week_start, week_start + timedelta(days=7)
    if scope == "next week":
        start = week_start + timedelta(days=7)
        return start, start + timedelta(days=7)
    if scope == "prev week":
        start = week_start - timedelta(days=7)
        return start, start + timedelta(days=7)

    month_start = current.replace(day=1)
    if scope in {"current month", "next month", "prev month"}:
        if scope == "current month":
            start = month_start
        elif scope == "next month":
            start = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        else:
            start = (month_start - timedelta(days=1)).replace(day=1)
        end = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        return start, end

    raise CalendarInputError("Unsupported relative scope: " + scope)

def is_open_start_scope(scope: str) -> bool:
    """Identify the CLI-only open-start range form."""
    return scope.startswith("-")


def is_open_end_scope(scope: str) -> bool:
    """Identify a range whose end boundary is the current UTC time."""
    return scope.endswith("-") and not scope.startswith("-") and len(scope) > 1


def resolve_open_end_scope(scope: str) -> Tuple[datetime, datetime]:
    """Resolve START- to START through the current UTC time."""
    if not is_open_end_scope(scope):
        raise CalendarInputError(f"Invalid open-end range '{scope}'.")
    endpoint = scope[:-1]
    if "@" in endpoint:
        date_part, time_part = endpoint.split("@", 1)
        normalized_time = time_part.replace(".", ":", 1)
        start, _ = parse_point(f"{date_part}@{normalized_time}")
    else:
        start = parse_date(endpoint)
    end = utc_now()
    if start >= end:
        raise CalendarInputError(
            f"Open-end range '{scope}' starts at or after the current UTC time."
        )
    return start, end


def resolve_open_start_scope(
    document: Dict[str, Any],
    symbol: str,
    scope: str,
) -> Tuple[datetime, datetime]:
    """Resolve an open-start range from the latest visible persisted event to END."""
    if not is_open_start_scope(scope):
        raise CalendarInputError(f"Invalid open-start range '{scope}'.")

    endpoint = scope[1:]
    if not endpoint or endpoint.startswith("-"):
        raise CalendarInputError(
            f"Invalid open-start range '{scope}'. Expected -YYYY.MM.DD or -YYYY.MM.DD@HH:MM."
        )

    if "@" in endpoint:
        date_part, time_part = endpoint.split("@", 1)
        normalized_time = time_part.replace(".", ":", 1)
        point, _ = parse_point(f"{date_part}@{normalized_time}")
        end = point + timedelta(minutes=1)
    else:
        end = parse_date(endpoint) + timedelta(days=1)

    visible = filter_events_for_symbol(document["events"], symbol)
    timestamps = [
        parse_iso8601(event["timestamp"])
        for event in visible
    ]
    if not timestamps:
        raise CalendarInputError(
            f"No recorded Calendar event exists for {symbol}; an open-start range requires retained history."
        )

    start = max(timestamps)
    if end <= start:
        raise CalendarInputError(
            f"Open-start range '{scope}' ends at or before the latest recorded event for {symbol}."
        )
    return start, end


def parse_scope(scope: str) -> str:
    """Calendar operation: parse_scope validates the canonical and open-start scope forms."""
    if scope in {
        "current", "latest", "next", "prev", "news",
        "today", "tomorrow", "yesterday",
        "current day", "current week", "current month",
        "next day", "next week", "next month",
        "prev day", "prev week", "prev month",
    }:
        if " " in scope:
            resolve_relative_scope_interval(scope)
        return scope
    if is_open_start_scope(scope):
        endpoint = scope[1:]
        if not endpoint or endpoint.startswith("-"):
            raise CalendarInputError(
                f"Invalid open-start range '{scope}'. Expected -YYYY.MM.DD or -YYYY.MM.DD@HH:MM."
            )
        if "@" in endpoint:
            date_part, time_part = endpoint.split("@", 1)
            parse_date(date_part)
            parse_time(time_part.replace(".", ":", 1))
        else:
            parse_date(endpoint)
        return scope
    if is_open_end_scope(scope):
        endpoint = scope[:-1]
        if not endpoint:
            raise CalendarInputError(
                f"Invalid open-end range '{scope}'. Expected YYYY.MM.DD- or YYYY.MM.DD@HH:MM-."
            )
        if "@" in endpoint:
            date_part, time_part = endpoint.split("@", 1)
            parse_date(date_part)
            parse_time(time_part.replace(".", ":", 1))
        else:
            parse_date(endpoint)
        return scope
    resolve_scope_interval(scope)
    return scope

def build_empty_calendar_document() -> Dict[str, Any]:
    """Calendar operation: build_empty_calendar_document performs the focused build empty calendar document step in the Calendar implementation."""
    return {
        "schema_version": SCHEMA_VERSION,
        "events": [],
        "coverage": [],
        "watermarks": {},
    }

def _validate_calendar_event(event: Dict[str, Any], event_ids: set[str]) -> None:
    """Internal helper: _validate_calendar_event performs the focused validate calendar event step in the Calendar implementation."""
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
    if event["source"] not in {"lse", "forexfactory", "yahoo_finance"}:
        raise DataIntegrityError("Invalid event source.")
    sources = event.get("sources", [event["source"]])
    if not isinstance(sources, list) or not sources or any(item not in {"lse", "forexfactory", "yahoo_finance"} for item in sources):
        raise DataIntegrityError("Invalid event sources.")
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
    if event["event_type"] == "economic":
        if not set(sources).intersection({"lse", "forexfactory"}):
            raise DataIntegrityError("Economic event must have an LSE or ForexFactory source.")
        if event["details"].get("currency") not in FX_CURRENCY_CODES and event["details"].get("currency") != "ALL":
            raise DataIntegrityError("Invalid economic-event currency.")
        if "specs" in event["details"]:
            _validate_forexfactory_details(event["details"])
    elif event["event_type"] == "news":
        if "yahoo_finance" not in sources:
            raise DataIntegrityError("News event must have a Yahoo Finance source.")

def _validate_forexfactory_details(details: Dict[str, Any]) -> None:
    """Internal helper: _validate_forexfactory_details performs the focused validate forexfactory details step in the Calendar implementation."""
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
    """Internal helper: _validate_coverage_records performs the focused validate coverage records step in the Calendar implementation."""
    seen = set()
    for coverage in records:
        if not isinstance(coverage, dict):
            raise DataIntegrityError("Invalid coverage record.")
        for field in ("provider", "symbol", "start", "end", "status"):
            if field not in coverage:
                raise DataIntegrityError(f"Malformed coverage; missing '{field}'.")
        if coverage["provider"] not in {"lse", "forexfactory", "yahoo_finance"}:
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
    """Internal helper: _validate_watermarks performs the focused validate watermarks step in the Calendar implementation."""
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

def _event_merge_key(event: Dict[str, Any]) -> Tuple[str, str, str]:
    """Build a provider-independent identity for scheduled economic events."""
    title = re.sub(r"[^a-z0-9]+", " ", event["title"].lower()).strip()
    currency = str(event.get("details", {}).get("currency", "")).upper()
    return event["event_type"], currency, f'{event["timestamp"]}|{title}'


def _merge_event_details(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Merge non-conflicting provider facts without discarding existing information."""
    details = dict(existing.get("details", {}))
    incoming_details = incoming.get("details", {})
    provider = incoming.get("source", "unknown")
    provider_fields = dict(details.get("provider_fields", {}))
    for key, value in incoming_details.items():
        if value in (None, "", [], {}):
            continue
        if key == "provider_fields":
            provider_fields[provider] = value
            continue
        if key not in details or details[key] in (None, "", [], {}):
            details[key] = value
        elif details[key] != value:
            provider_fields.setdefault(provider, {})[key] = value
    if provider_fields:
        details["provider_fields"] = provider_fields
    return details


def merge_events(
    document: Dict[str, Any],
    new_events: List[Dict[str, Any]],
    clear_suppressed_symbol: Optional[str] = None,
    preserve_detail_failure_ids: Optional[set[str]] = None,
) -> None:
    """Merge provider events by stable provider ID and shared economic-event identity."""
    by_id = {event["event_id"]: event for event in document["events"]}
    economic_keys = {
        _event_merge_key(event): event["event_id"]
        for event in document["events"]
        if event["event_type"] == "economic"
    }
    failed_detail_ids = preserve_detail_failure_ids or set()
    for event in new_events:
        event_id = event["event_id"]
        old_event = by_id.get(event_id)
        merge_id = event_id
        if old_event is None and event["event_type"] == "economic":
            merge_id = economic_keys.get(_event_merge_key(event), event_id)
            old_event = by_id.get(merge_id)
        if old_event is not None and old_event["timestamp"] != event["timestamp"]:
            raise DataIntegrityError(f"Provider identity/time conflict for {event_id}.")
        if old_event is None:
            normalized_event = dict(event)
        else:
            normalized_event = dict(old_event)
            normalized_event["details"] = _merge_event_details(old_event, event)
            sources = sorted(set(old_event.get("sources", [old_event["source"]])) | set(event.get("sources", [event["source"]])))
            normalized_event["sources"] = sources
            if event["source"] == "lse" and old_event["source"] == "forexfactory":
                normalized_event["source"] = "lse"
            if event["source"] == "yahoo_finance" and old_event["source"] != "yahoo_finance" and event["event_type"] == "news":
                normalized_event["source"] = "yahoo_finance"
        suppressed = set(normalized_event.get("suppressed_for", []))
        suppressed.update(event.get("suppressed_for", []))
        if clear_suppressed_symbol is not None:
            suppressed.discard(clear_suppressed_symbol)
        if suppressed:
            normalized_event["suppressed_for"] = sorted(suppressed)
        else:
            normalized_event.pop("suppressed_for", None)
        by_id[merge_id] = normalized_event
        if event["event_type"] == "economic":
            economic_keys[_event_merge_key(normalized_event)] = merge_id
    document["events"] = sorted(
        by_id.values(),
        key=lambda item: (parse_iso8601(item["timestamp"]), item["source"], item["event_id"]),
    )

def merge_coverage(document: Dict[str, Any], item: Dict[str, Any]) -> None:
    """Calendar operation: merge_coverage performs the focused merge coverage step in the Calendar implementation."""
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
    """Calendar operation: find_uncovered_intervals performs the focused find uncovered intervals step in the Calendar implementation."""
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
    """Calendar operation: watermark_key performs the focused watermark key step in the Calendar implementation."""
    return f"{provider}|{symbol}"

def resolve_applicable_providers(symbol: str) -> List[str]:
    """Return all Calendar provider adapters; each adapter decides symbol relevance."""
    return ["lse", "forexfactory", "yahoo_finance"]

def filter_events_for_symbol(events: List[Dict[str, Any]], symbol: str) -> List[Dict[str, Any]]:
    """Filter merged events by canonical symbol visibility and provider contribution."""
    def visible(event: Dict[str, Any]) -> bool:
        return symbol not in event.get("suppressed_for", [])

    if is_currency(symbol):
        currencies = {symbol}
    elif is_fx_pair(symbol):
        currencies = {symbol[:3], symbol[3:]}
    else:
        currencies = set()

    result: List[Dict[str, Any]] = []
    for event in events:
        if not visible(event):
            continue
        sources = set(event.get("sources", [event.get("source")]))
        event_type = event.get("event_type") or ("economic" if sources.intersection({"lse", "forexfactory"}) else "news" if "yahoo_finance" in sources else "")
        if event_type == "economic" and sources.intersection({"lse", "forexfactory"}):
            if event["details"].get("currency") in currencies:
                result.append(event)
        elif event_type == "news" and "yahoo_finance" in sources and event["symbol"] == symbol:
            result.append(event)
    return result

def filter_events_for_interval(
    events: List[Dict[str, Any]],
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
    """Calendar operation: filter_events_for_interval performs the focused filter events for interval step in the Calendar implementation."""
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
    """Calendar operation: update_watermark performs the focused update watermark step in the Calendar implementation."""
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
    """Calendar operation: query_current_events performs the focused query current events step in the Calendar implementation."""
    return [
        event for event in events
        if since < parse_iso8601(event["timestamp"]) <= until
    ]

def query_latest_event(
    events: List[Dict[str, Any]],
    symbol: str,
    now: datetime,
) -> List[Dict[str, Any]]:
    """Calendar operation: query_latest_event performs the focused query latest event step in the Calendar implementation."""
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
    """Calendar operation: query_next_event performs the focused query next event step in the Calendar implementation."""
    # Yahoo Finance supplies published/current news, not scheduled future events.
    # Future-event lookup therefore only considers canonical scheduled economic
    # events from ForexFactory.
    visible_future = [
        event
        for event in filter_events_for_symbol(events, symbol)
        if (
            "forexfactory" in set(event.get("sources", [event.get("source")] ))
            and event["event_type"] == "economic"
            and parse_iso8601(event["timestamp"]) > now
        )
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

def query_prev_event(
    events: List[Dict[str, Any]],
    symbol: str,
    now: datetime,
) -> List[Dict[str, Any]]:
    """Return the nearest past scheduled economic event for SYMBOL."""
    visible_past = [
        event
        for event in filter_events_for_symbol(events, symbol)
        if (
            "forexfactory" in set(event.get("sources", [event.get("source")]))
            and event["event_type"] == "economic"
            and parse_iso8601(event["timestamp"]) < now
        )
    ]
    if not visible_past:
        return []
    return [max(visible_past, key=lambda event: (parse_iso8601(event["timestamp"]), event["source"], event["event_id"]))]


def query_relative_events(
    events: List[Dict[str, Any]],
    symbol: str,
    scope: str,
) -> List[Dict[str, Any]]:
    """Return all visible events in a resolved relative calendar period."""
    start, end = resolve_relative_scope_interval(scope)
    return sorted(
        filter_events_for_interval(filter_events_for_symbol(events, symbol), start, end),
        key=lambda event: (parse_iso8601(event["timestamp"]), event["source"], event["event_id"]),
    )


def query_ongoing_events(
    events: List[Dict[str, Any]],
    symbol: str,
    now: datetime,
) -> List[Dict[str, Any]]:
    """Return all events whose canonical one-minute activity window contains NOW."""
    visible = filter_events_for_symbol(events, symbol)
    return sorted(
        [
            event for event in visible
            if parse_iso8601(event["timestamp"]) <= now < parse_iso8601(event["timestamp"]) + timedelta(minutes=1)
        ],
        key=lambda event: (parse_iso8601(event["timestamp"]), event["source"], event["event_id"]),
    )


def query_active_news(
    events: List[Dict[str, Any]],
    symbol: str,
    now: datetime,
) -> List[Dict[str, Any]]:
    """Return scheduled economic news events active in the current UTC minute."""
    return sorted(
        [
            event for event in filter_events_for_symbol(events, symbol)
            if (
                set(event.get("sources", [event.get("source")])).intersection({"lse", "forexfactory"})
                and event["event_type"] == "economic"
                and parse_iso8601(event["timestamp"]) <= now < parse_iso8601(event["timestamp"]) + timedelta(minutes=1)
            )
        ],
        key=lambda event: (parse_iso8601(event["timestamp"]), event["source"], event["event_id"]),
    )

def status_from_provider_results(provider_results: List[Dict[str, Any]]) -> str:
    """Aggregate isolated provider results into the public Calendar status."""
    statuses = [result["status"] for result in provider_results]
    if not statuses:
        return "UNAVAILABLE"
    if all(status == "SKIPPED_NO_FOREX_PAIR" for status in statuses):
        return "NO_FOREX_PAIR"
    if all(status == "ERROR" for status in statuses):
        return "UNAVAILABLE"
    if any(status == "ERROR" for status in statuses):
        return "PARTIAL"
    if any(status == "PARTIAL" for status in statuses):
        return "PARTIAL"
    if all(status == "NO_MATCH" for status in statuses):
        return "NO_RELEVANT_EVENT"
    if any(status == "SKIPPED_NO_FOREX_PAIR" for status in statuses):
        return "PARTIAL"
    return "OK"

def query_last_update(
    document: Dict[str, Any],
    symbol: str,
) -> List[Dict[str, Any]]:
    """Calendar operation: query_last_update returns committed provider watermark timestamps."""
    results: List[Dict[str, Any]] = []
    for provider in resolve_applicable_providers(symbol):
        key = watermark_key(provider, symbol)
        watermark = document["watermarks"].get(key)
        results.append({
            "provider": provider,
            "symbol": symbol,
            "last_successful_at": (
                watermark.get("last_successful_at") if watermark else None
            ),
        })
    return results

def filter_query_events(
    document: Dict[str, Any],
    events: List[Dict[str, Any]],
    symbol: str,
    start: datetime,
    end: datetime,
    yahoo_pair_available: bool = True,
) -> List[Dict[str, Any]]:
    """Apply symbol visibility and source-specific coverage guards to cached results."""
    result: List[Dict[str, Any]] = []
    coverage_valid = {
        provider: not bool(find_uncovered_intervals(document, provider, symbol, start, end))
        for provider in ("lse", "forexfactory", "yahoo_finance")
    }
    for event in events:
        sources = set(event.get("sources", [event.get("source")]))
        if (
            event.get("source") == "yahoo_finance"
            and is_fx_pair(symbol)
            and not yahoo_pair_available
        ):
            continue
        if event.get("event_type") == "economic":
            economic_sources = sources.intersection({"lse", "forexfactory"})
            if economic_sources and not any(coverage_valid.get(provider, False) for provider in economic_sources):
                continue
        elif event.get("event_type") == "news" and "yahoo_finance" in sources:
            if not coverage_valid["yahoo_finance"]:
                continue
        result.append(event)
    return result


