"""Shared FMP economic-news cache plus symbol-specific query/materialization CLI."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request as URLRequest, urlopen

DEFAULT_DATA_DIRECTORY = Path("data")
NEWS_DATA_FILENAME = "news_data.json"
NEWS_CACHE_PATH = Path(__file__).resolve().parent / NEWS_DATA_FILENAME

FMP_API_URL = "https://financialmodelingprep.com/stable/economic-calendar"
FMP_API_KEY_ENV = "FMP_API_KEY"
FMP_MAX_RANGE_DAYS = 90
FMP_TIMEOUT_SECONDS = 20

NEWS_FORWARD_DAYS = 7
NEWS_REFRESH_BACKFILL_DAYS = 1
NEWS_REFRESH_INTERVAL = timedelta(hours=24)
NEWS_RETENTION_DAYS = 180

WRITE_RETRY_LIMIT = 5
WRITE_RETRY_DELAY_SECONDS = 0.25


@dataclass(frozen=True)
class ProviderEvent:
    raw: dict[str, Any]


@dataclass(frozen=True)
class NewsEvent:
    event_id: str
    source_timestamp: datetime
    source_timezone: str | None
    event_time_utc: datetime
    title: str
    impact: str
    affected_currencies: list[str]
    affected_instruments: list[str]
    status: str
    forecast: str | None
    previous: str | None
    actual: str | None
    source: str


@dataclass(frozen=True)
class NewsUpdateRequest:
    start_time: datetime | None
    end_time: datetime | None
    force: bool
    debug: bool


@dataclass(frozen=True)
class NewsQueryRequest:
    symbol: str
    start_time: datetime | None
    end_time: datetime | None
    impacts: tuple[str, ...]
    statuses: tuple[str, ...]
    limit: int | None
    force: bool
    debug: bool


class NewsDataProvider:
    """Stable provider boundary for future provider adapters."""

    def fetch_range(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> list[ProviderEvent]:
        raise NotImplementedError


class FMPNewsDataProvider(NewsDataProvider):
    """FMP Economic Calendar adapter."""

    def __init__(
        self,
        api_key: str | None = None,
        opener: Any = urlopen,
        timeout: float = FMP_TIMEOUT_SECONDS,
    ) -> None:
        self.api_key = api_key or os.environ.get(FMP_API_KEY_ENV)
        if not self.api_key:
            raise RuntimeError(f"{FMP_API_KEY_ENV} is required")
        self.opener = opener
        self.timeout = timeout

    def fetch_range(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> list[ProviderEvent]:
        start = start_time.astimezone(timezone.utc)
        end = end_time.astimezone(timezone.utc)
        if start > end:
            raise ValueError("FMP start must not exceed end")

        result: list[ProviderEvent] = []
        cursor = start.date()
        final = end.date()

        while cursor <= final:
            chunk_end = min(
                final,
                cursor + timedelta(days=FMP_MAX_RANGE_DAYS - 1),
            )
            params = urlencode(
                {
                    "from": cursor.isoformat(),
                    "to": chunk_end.isoformat(),
                    "apikey": self.api_key,
                }
            )
            request = URLRequest(
                f"{FMP_API_URL}?{params}",
                headers={
                    "Accept": "application/json",
                    "User-Agent": "SMC_Mapper/news_data.py",
                },
            )

            try:
                with self.opener(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                raise RuntimeError(f"FMP HTTP error {exc.code}") from exc
            except (URLError, TimeoutError, OSError) as exc:
                raise RuntimeError(f"FMP request failed: {exc}") from exc
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise RuntimeError("FMP returned invalid JSON") from exc

            if isinstance(payload, dict):
                error = payload.get("Error Message") or payload.get("error")
                if error:
                    raise RuntimeError(str(error))
                payload = payload.get("data", [])

            if not isinstance(payload, list):
                raise RuntimeError("FMP response is not a list")

            for item in payload:
                if not isinstance(item, dict):
                    raise RuntimeError(
                        "FMP response contains a non-object event"
                    )
                result.append(ProviderEvent(item))

            cursor = chunk_end + timedelta(days=1)

        return result


def create_news_provider(provider_name: str = "fmp") -> NewsDataProvider:
    if provider_name.lower() != "fmp":
        raise ValueError("V1 supports only the FMP news provider")
    return FMPNewsDataProvider()


def parse_iso8601(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def normalize_impact(value: Any) -> str:
    text = str(value or "").strip().upper()
    return text if text in {"LOW", "MEDIUM", "HIGH"} else "UNKNOWN"


def normalize_status(value: Any) -> str:
    aliases = {
        "UPCOMING": "SCHEDULED",
        "ACTUAL": "RELEASED",
        "CANCELED": "CANCELLED",
    }
    text = str(value or "").strip().upper()
    return aliases.get(
        text,
        text if text in {"SCHEDULED", "RELEASED", "CANCELLED"} else "UNKNOWN",
    )


def normalize_affected_metadata(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        values = value.replace(";", ",").split(",")
    elif isinstance(value, (list, tuple, set)):
        values = value
    else:
        values = [value]
    return sorted(
        {str(item).strip().upper() for item in values if str(item).strip()}
    )


def _fmp_time(event: ProviderEvent) -> tuple[datetime, str]:
    raw = event.raw.get("date")
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("FMP event date is missing")

    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc), "UTC"


def build_event_id(event: ProviderEvent | NewsEvent) -> str:
    if isinstance(event, ProviderEvent):
        provider_id = (
            event.raw.get("id")
            or event.raw.get("eventId")
            or event.raw.get("event_id")
        )
        if provider_id not in (None, ""):
            return str(provider_id)

        event_time, _ = _fmp_time(event)
        identity = {
            "source": "FMP",
            "event_time_utc": event_time.isoformat(),
            "title": str(event.raw.get("event", "")).strip().casefold(),
            "affected_currencies": normalize_affected_metadata(
                event.raw.get("currency")
            ),
            "affected_instruments": normalize_affected_metadata(
                event.raw.get("affected_instruments")
            ),
        }
    else:
        identity = {
            "source": event.source,
            "event_time_utc": event.event_time_utc.isoformat(),
            "title": event.title.strip().casefold(),
            "affected_currencies": sorted(event.affected_currencies),
            "affected_instruments": sorted(event.affected_instruments),
        }

    return hashlib.sha256(
        json.dumps(
            identity,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def normalize_source_event(
    event: ProviderEvent,
    now: datetime | None = None,
) -> NewsEvent:
    now = now or datetime.now(timezone.utc)
    event_time, source_timezone = _fmp_time(event)
    raw = event.raw
    title = str(raw.get("event", "")).strip()
    if not title:
        raise ValueError("FMP event title is missing")

    raw_status = raw.get("status")
    status = normalize_status(raw_status)
    if raw_status is None or status == "UNKNOWN":
        status = "SCHEDULED" if event_time > now else "RELEASED"

    normalized = NewsEvent(
        event_id="",
        source_timestamp=event_time,
        source_timezone=source_timezone,
        event_time_utc=event_time,
        title=title,
        impact=normalize_impact(raw.get("impact")),
        affected_currencies=normalize_affected_metadata(
            raw.get("currency")
        ),
        affected_instruments=normalize_affected_metadata(
            raw.get("affected_instruments")
        ),
        status=status,
        forecast=None if raw.get("estimate") is None else str(raw["estimate"]),
        previous=None if raw.get("previous") is None else str(raw["previous"]),
        actual=None if raw.get("actual") is None else str(raw["actual"]),
        source="FMP",
    )

    return NewsEvent(
        **{**normalized.__dict__, "event_id": build_event_id(normalized)}
    )


def validate_news_event(event: NewsEvent) -> None:
    if not event.event_id or not event.title or event.source != "FMP":
        raise ValueError("invalid NewsEvent")
    if event.source_timestamp.tzinfo is None:
        raise ValueError("source_timestamp must be timezone-aware")
    if event.event_time_utc.tzinfo is None:
        raise ValueError("event_time_utc must be timezone-aware")
    if event.impact not in {"LOW", "MEDIUM", "HIGH", "UNKNOWN"}:
        raise ValueError("invalid impact")
    if event.status not in {
        "SCHEDULED",
        "RELEASED",
        "CANCELLED",
        "UNKNOWN",
    }:
        raise ValueError("invalid status")


def sort_news_events(events: Sequence[NewsEvent]) -> list[NewsEvent]:
    return sorted(
        events,
        key=lambda event: (event.event_time_utc, event.event_id),
    )


def _same_identity(old: NewsEvent, new: NewsEvent) -> bool:
    return (
        old.event_id,
        old.event_time_utc,
        old.title.casefold(),
        tuple(old.affected_currencies),
        tuple(old.affected_instruments),
        old.source,
    ) == (
        new.event_id,
        new.event_time_utc,
        new.title.casefold(),
        tuple(new.affected_currencies),
        tuple(new.affected_instruments),
        new.source,
    )


def _merge_pair(old: NewsEvent, new: NewsEvent) -> NewsEvent:
    if not _same_identity(old, new):
        raise ValueError(f"conflicting identity for event_id {old.event_id}")

    return NewsEvent(
        event_id=old.event_id,
        source_timestamp=old.source_timestamp,
        source_timezone=old.source_timezone,
        event_time_utc=old.event_time_utc,
        title=old.title,
        impact=new.impact if new.impact != "UNKNOWN" else old.impact,
        affected_currencies=old.affected_currencies,
        affected_instruments=old.affected_instruments,
        status=new.status if new.status != "UNKNOWN" else old.status,
        forecast=new.forecast if new.forecast is not None else old.forecast,
        previous=new.previous if new.previous is not None else old.previous,
        actual=new.actual if new.actual is not None else old.actual,
        source=old.source,
    )


def merge_news_events(
    existing: Sequence[NewsEvent],
    incoming: Sequence[NewsEvent],
) -> list[NewsEvent]:
    merged: dict[str, NewsEvent] = {}
    for event in list(existing) + list(incoming):
        validate_news_event(event)
        if event.event_id in merged:
            merged[event.event_id] = _merge_pair(
                merged[event.event_id],
                event,
            )
        else:
            merged[event.event_id] = event

    return sort_news_events(list(merged.values()))


def normalize_news_events(
    events: Sequence[ProviderEvent],
    now: datetime | None = None,
) -> list[NewsEvent]:
    return merge_news_events(
        [],
        [normalize_source_event(event, now=now) for event in events],
    )


def apply_news_retention(
    events: Sequence[NewsEvent],
    now: datetime | None = None,
) -> list[NewsEvent]:
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=NEWS_RETENTION_DAYS)
    return sort_news_events(
        [event for event in events if event.event_time_utc >= cutoff]
    )


def get_news_data_path() -> Path:
    return NEWS_CACHE_PATH


def _normalize_query_symbol(symbol: str) -> str:
    value = symbol.strip().upper()
    if not value or value in {".", ".."}:
        raise ValueError("invalid symbol")
    if any(char in value for char in ("/", "\\", ":", "\x00")):
        raise ValueError("invalid symbol")
    return value


def get_symbol_data_directory(symbol: str) -> Path:
    normalized = _normalize_query_symbol(symbol)
    root = DEFAULT_DATA_DIRECTORY.resolve()
    target = (root / normalized).resolve()
    if target == root or root not in target.parents:
        raise ValueError("symbol directory escapes data root")
    return target


def get_symbol_news_path(symbol: str) -> Path:
    normalized = _normalize_query_symbol(symbol)
    return get_symbol_data_directory(normalized) / (
        f"{normalized}_news_data.json"
    )


def _event_to_dict(event: NewsEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "source_timestamp": event.source_timestamp.astimezone(
            timezone.utc
        ).isoformat(),
        "source_timezone": event.source_timezone,
        "event_time_utc": event.event_time_utc.astimezone(
            timezone.utc
        ).isoformat(),
        "title": event.title,
        "impact": event.impact,
        "affected_currencies": event.affected_currencies,
        "affected_instruments": event.affected_instruments,
        "status": event.status,
        "forecast": event.forecast,
        "previous": event.previous,
        "actual": event.actual,
        "source": event.source,
    }


def _event_from_dict(raw: dict[str, Any]) -> NewsEvent:
    event = NewsEvent(
        event_id=str(raw["event_id"]),
        source_timestamp=parse_iso8601(str(raw["source_timestamp"])),
        source_timezone=raw.get("source_timezone"),
        event_time_utc=parse_iso8601(str(raw["event_time_utc"])),
        title=str(raw["title"]),
        impact=str(raw["impact"]),
        affected_currencies=normalize_affected_metadata(
            raw.get("affected_currencies")
        ),
        affected_instruments=normalize_affected_metadata(
            raw.get("affected_instruments")
        ),
        status=str(raw["status"]),
        forecast=raw.get("forecast"),
        previous=raw.get("previous"),
        actual=raw.get("actual"),
        source=str(raw["source"]),
    )
    validate_news_event(event)
    return event


def load_news_data(path: Path | str | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else get_news_data_path()
    if not target.exists():
        return {
            "schema_version": 1,
            "provider": "FMP",
            "events": [],
            "available_start": None,
            "available_end": None,
            "last_successful_update_utc": None,
        }

    document = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("news cache root must be an object")

    document.setdefault("schema_version", 1)
    document.setdefault("provider", "FMP")
    document["events"] = [
        _event_from_dict(item)
        for item in document.get("events", [])
    ]
    return document


def _serialize_cache(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": int(document.get("schema_version", 1)),
        "provider": str(document.get("provider", "FMP")),
        "events": [
            _event_to_dict(event) if isinstance(event, NewsEvent) else event
            for event in document.get("events", [])
        ],
        "available_start": document.get("available_start"),
        "available_end": document.get("available_end"),
        "last_successful_update_utc": document.get(
            "last_successful_update_utc"
        ),
    }


def save_json_atomic(
    path: Path | str,
    document: dict[str, Any],
    serializer: Any,
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        serializer(document),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"

    last_error: Exception | None = None
    for attempt in range(WRITE_RETRY_LIMIT):
        temp_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=target.parent,
                delete=False,
            ) as handle:
                temp_name = handle.name
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(temp_name, target)
            return
        except OSError as exc:
            last_error = exc
            if temp_name:
                try:
                    os.unlink(temp_name)
                except OSError:
                    pass
            if attempt + 1 < WRITE_RETRY_LIMIT:
                time.sleep(WRITE_RETRY_DELAY_SECONDS)

    raise RuntimeError(f"atomic JSON save failed: {last_error}")


def save_news_data_atomic(
    path: Path | str,
    document: dict[str, Any],
) -> None:
    save_json_atomic(path, document, _serialize_cache)


def save_symbol_news_atomic(
    path: Path | str,
    document: dict[str, Any],
) -> None:
    save_json_atomic(path, document, lambda value: value)


def _parse_doc_time(value: Any) -> datetime | None:
    return parse_iso8601(str(value)) if value else None


def cache_refresh_due(
    document: dict[str, Any],
    now: datetime,
    required_end: datetime | None = None,
) -> bool:
    last = _parse_doc_time(document.get("last_successful_update_utc"))
    available_end = _parse_doc_time(document.get("available_end"))
    coverage_end = required_end or (
        now + timedelta(days=NEWS_FORWARD_DAYS)
    )
    return (
        last is None
        or now - last >= NEWS_REFRESH_INTERVAL
        or available_end is None
        or available_end < coverage_end
    )


def resolve_update_range(
    request: NewsUpdateRequest,
    existing: dict[str, Any],
    now: datetime,
) -> tuple[datetime, datetime]:
    start = request.start_time or (
        now - timedelta(days=NEWS_REFRESH_BACKFILL_DAYS)
    )
    end = request.end_time or (
        now + timedelta(days=NEWS_FORWARD_DAYS)
    )

    old_end = _parse_doc_time(existing.get("available_end"))
    if old_end is not None and request.end_time is None:
        end = max(end, old_end)

    if start > end:
        raise ValueError("news start_time must not exceed end_time")

    return start, end


def update_news_cache(
    request: NewsUpdateRequest,
    provider: NewsDataProvider,
    existing: dict[str, Any],
    now: datetime | None = None,
) -> tuple[dict[str, Any], bool]:
    now = now or datetime.now(timezone.utc)

    if not request.force and not cache_refresh_due(
        existing,
        now,
        required_end=request.end_time,
    ):
        return existing, False

    start, end = resolve_update_range(request, existing, now)
    incoming = normalize_news_events(
        provider.fetch_range(start, end),
        now=now,
    )

    current = [
        event if isinstance(event, NewsEvent) else _event_from_dict(event)
        for event in existing.get("events", [])
    ]

    merged = apply_news_retention(
        merge_news_events(current, incoming),
        now=now,
    )

    old_start = _parse_doc_time(existing.get("available_start"))
    old_end = _parse_doc_time(existing.get("available_end"))
    available_start = (
        min(old_start, start) if old_start is not None else start
    )
    available_end = (
        max(old_end, end) if old_end is not None else end
    )

    return {
        "schema_version": 1,
        "provider": "FMP",
        "events": merged,
        "available_start": available_start.isoformat(),
        "available_end": available_end.isoformat(),
        "last_successful_update_utc": now.isoformat(),
    }, True


def should_refresh_for_query(
    request: NewsQueryRequest,
    cache_document: dict[str, Any],
    now: datetime,
) -> bool:
    required_end = request.end_time or (
        now + timedelta(days=NEWS_FORWARD_DAYS)
    )
    return request.force or cache_refresh_due(
        cache_document,
        now,
        required_end=required_end,
    )


def query_news_events(
    request: NewsQueryRequest,
    document: dict[str, Any],
) -> list[NewsEvent]:
    result: list[NewsEvent] = []
    for raw in document.get("events", []):
        event = raw if isinstance(raw, NewsEvent) else _event_from_dict(raw)

        if not event_matches_symbol(event, request.symbol):
            continue
        if request.start_time and event.event_time_utc < request.start_time:
            continue
        if request.end_time and event.event_time_utc > request.end_time:
            continue
        if request.impacts and event.impact not in request.impacts:
            continue
        if request.statuses and event.status not in request.statuses:
            continue

        result.append(event)

    result = sort_news_events(result)
    return result[:request.limit] if request.limit is not None else result


def event_matches_symbol(event: NewsEvent, symbol: str) -> bool:
    normalized = _normalize_query_symbol(symbol)
    instruments = {item.upper() for item in event.affected_instruments}
    if normalized in instruments:
        return True

    if len(normalized) == 6 and normalized.isalpha():
        currencies = {item.upper() for item in event.affected_currencies}
        return bool(
            currencies.intersection(
                (normalized[:3], normalized[3:])
            )
        )

    return False


def _default_query_window(
    request: NewsQueryRequest,
    now: datetime,
) -> NewsQueryRequest:
    if request.start_time is not None or request.end_time is not None:
        return request

    return NewsQueryRequest(
        symbol=request.symbol,
        start_time=now - timedelta(days=NEWS_REFRESH_BACKFILL_DAYS),
        end_time=now + timedelta(days=NEWS_FORWARD_DAYS),
        impacts=request.impacts,
        statuses=request.statuses,
        limit=request.limit,
        force=request.force,
        debug=request.debug,
    )


def build_symbol_news_document(
    request: NewsQueryRequest,
    cache_document: dict[str, Any],
) -> dict[str, Any]:
    events = query_news_events(request, cache_document)
    return {
        "schema_version": 1,
        "symbol": request.symbol,
        "source": {
            "provider": cache_document.get("provider", "FMP"),
            "cache_path": str(get_news_data_path()),
            "cache_available_start": cache_document.get("available_start"),
            "cache_available_end": cache_document.get("available_end"),
            "cache_last_successful_update_utc": cache_document.get(
                "last_successful_update_utc"
            ),
        },
        "query": {
            "symbol": request.symbol,
            "start_time": (
                request.start_time.isoformat()
                if request.start_time is not None
                else None
            ),
            "end_time": (
                request.end_time.isoformat()
                if request.end_time is not None
                else None
            ),
            "impacts": list(request.impacts),
            "statuses": list(request.statuses),
            "limit": request.limit,
        },
        "events": [_event_to_dict(event) for event in events],
    }


def materialize_symbol_news(
    request: NewsQueryRequest,
    cache_document: dict[str, Any],
) -> Path:
    path = get_symbol_news_path(request.symbol)
    document = build_symbol_news_document(request, cache_document)

    if path.exists():
        try:
            if json.loads(path.read_text(encoding="utf-8")) == document:
                return path
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            pass

    save_symbol_news_atomic(path, document)
    return path


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Maintain the shared FMP news cache and materialize symbol news views."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--query",
        metavar="SYMBOL",
        help="refresh cache when required, then materialize symbol news",
    )
    mode.add_argument(
        "--update",
        action="store_true",
        help="refresh the shared cache only",
    )
    parser.add_argument("--starttime")
    parser.add_argument("--endtime")
    parser.add_argument(
        "--impact",
        action="append",
        choices=["LOW", "MEDIUM", "HIGH", "UNKNOWN"],
    )
    parser.add_argument(
        "--status",
        action="append",
        choices=["SCHEDULED", "RELEASED", "CANCELLED", "UNKNOWN"],
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--force",
        action="store_true",
        help="bypass the shared-cache refresh gate",
    )
    parser.add_argument("--debug", action="store_true")
    return parser


def parse_cli_request(
    argv: Sequence[str] | None = None,
) -> tuple[str, NewsQueryRequest | NewsUpdateRequest]:
    args = build_argument_parser().parse_args(argv)

    if args.limit is not None and args.limit <= 0:
        raise ValueError("limit must be positive")

    start = parse_iso8601(args.starttime) if args.starttime else None
    end = parse_iso8601(args.endtime) if args.endtime else None
    if start and end and start > end:
        raise ValueError("starttime must not be after endtime")

    if args.query is not None:
        return "query", NewsQueryRequest(
            symbol=_normalize_query_symbol(args.query),
            start_time=start,
            end_time=end,
            impacts=tuple(args.impact or ()),
            statuses=tuple(args.status or ()),
            limit=args.limit,
            force=bool(args.force),
            debug=bool(args.debug),
        )

    return "update", NewsUpdateRequest(
        start_time=start,
        end_time=end,
        force=bool(args.force),
        debug=bool(args.debug),
    )


def run_update(
    request: NewsUpdateRequest,
    provider: NewsDataProvider | None = None,
    now: datetime | None = None,
) -> int:
    now = now or datetime.now(timezone.utc)
    try:
        cache_path = get_news_data_path()
        existing = load_news_data(cache_path)
        document, changed = update_news_cache(
            request,
            provider or create_news_provider(),
            existing,
            now=now,
        )
        if not changed:
            return 0
        save_news_data_atomic(cache_path, document)
        return 0
    except Exception as exc:
        if request.debug:
            print(f"news_data update: {exc}", file=sys.stderr)
        return 1


def run_query(
    request: NewsQueryRequest,
    provider: NewsDataProvider | None = None,
    now: datetime | None = None,
) -> int:
    now = now or datetime.now(timezone.utc)
    effective_request = _default_query_window(request, now)

    try:
        cache_path = get_news_data_path()
        existing = load_news_data(cache_path)

        if should_refresh_for_query(
            effective_request,
            existing,
            now,
        ):
            cache_document, changed = update_news_cache(
                NewsUpdateRequest(
                    start_time=effective_request.start_time,
                    end_time=effective_request.end_time,
                    force=effective_request.force,
                    debug=effective_request.debug,
                ),
                provider or create_news_provider(),
                existing,
                now=now,
            )
            if changed:
                save_news_data_atomic(cache_path, cache_document)
        else:
            cache_document = existing

        materialized = materialize_symbol_news(
            effective_request,
            cache_document,
        )
        result = build_symbol_news_document(
            effective_request,
            cache_document,
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))

        if request.debug:
            print(
                f"news_data: materialized {materialized}",
                file=sys.stderr,
            )

        return 0

    except Exception as exc:
        if request.debug:
            print(f"news_data query: {exc}", file=sys.stderr)
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    try:
        mode, request = parse_cli_request(argv)
        if mode == "query":
            return run_query(request)
        return run_update(request)
    except Exception as exc:
        print(f"news_data: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
