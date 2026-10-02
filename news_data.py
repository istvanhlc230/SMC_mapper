"""Normalized economic-news acquisition CLI with a shared global FMP cache."""
from __future__ import annotations
import argparse, hashlib, json, os, sys, tempfile, time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request as URLRequest, urlopen

NEWS_DATA_FILENAME = "news_data.json"
NEWS_DATA_PATH = Path(__file__).resolve().parent / NEWS_DATA_FILENAME
FMP_API_URL = "https://financialmodelingprep.com/stable/economic-calendar"
FMP_API_KEY_ENV = "FMP_API_KEY"
FMP_MAX_RANGE_DAYS = 90
FMP_TIMEOUT_SECONDS = 20
NEWS_FORWARD_DAYS = 7
NEWS_REFRESH_INTERVAL = timedelta(hours=24)
NEWS_REFRESH_BACKFILL_DAYS = 1
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
class NewsDataRequest:
    symbol: str
    start_time: datetime | None
    end_time: datetime | None
    live: bool
    force: bool
    debug: bool

class NewsDataProvider:
    """Stable extension boundary for future providers."""
    def fetch_range(self, start_time: datetime, end_time: datetime) -> list[ProviderEvent]:
        raise NotImplementedError
    def fetch_current(self) -> list[ProviderEvent]:
        raise NotImplementedError

class FMPNewsDataProvider(NewsDataProvider):
    def __init__(self, api_key: str | None = None, opener: Any = urlopen,
                 timeout: float = FMP_TIMEOUT_SECONDS) -> None:
        self.api_key = api_key or os.environ.get(FMP_API_KEY_ENV)
        if not self.api_key:
            raise RuntimeError(f"{FMP_API_KEY_ENV} is required")
        self.opener, self.timeout = opener, timeout

    def _fetch(self, start_time: datetime, end_time: datetime) -> list[ProviderEvent]:
        start_time = start_time.astimezone(timezone.utc)
        end_time = end_time.astimezone(timezone.utc)
        if start_time > end_time:
            raise ValueError("FMP start must not exceed end")
        result: list[ProviderEvent] = []
        cursor, final = start_time.date(), end_time.date()
        while cursor <= final:
            chunk_end = min(final, cursor + timedelta(days=FMP_MAX_RANGE_DAYS - 1))
            query = urlencode({"from": cursor.isoformat(), "to": chunk_end.isoformat(),
                               "apikey": self.api_key})
            req = URLRequest(f"{FMP_API_URL}?{query}",
                             headers={"Accept": "application/json",
                                      "User-Agent": "SMC_Mapper/news_data.py"})
            try:
                with self.opener(req, timeout=self.timeout) as response:
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
                    raise RuntimeError("FMP response contains a non-object event")
                result.append(ProviderEvent(item))
            cursor = chunk_end + timedelta(days=1)
        return result

    def fetch_range(self, start_time: datetime, end_time: datetime) -> list[ProviderEvent]:
        return self._fetch(start_time, end_time)

    def fetch_current(self) -> list[ProviderEvent]:
        now = datetime.now(timezone.utc)
        return self._fetch(
            now - timedelta(days=NEWS_REFRESH_BACKFILL_DAYS),
            now + timedelta(days=NEWS_FORWARD_DAYS),
        )

def create_news_provider(provider_name: str = "fmp") -> NewsDataProvider:
    if provider_name.lower() != "fmp":
        raise ValueError("V1 supports only the FMP news provider")
    return FMPNewsDataProvider()

def parse_iso8601(value: str) -> datetime:
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)

def normalize_symbol(symbol: str) -> str:
    value = symbol.strip()
    if not value or value in {".", ".."} or "\x00" in value:
        raise ValueError("invalid symbol")
    if "/" in value or "\\" in value or Path(value).drive:
        raise ValueError("symbol must be one safe input component")
    return value

def normalize_impact(value: Any) -> str:
    value = str(value or "").strip().upper()
    return value if value in {"LOW", "MEDIUM", "HIGH"} else "UNKNOWN"

def normalize_status(value: Any) -> str:
    aliases = {"UPCOMING": "SCHEDULED", "ACTUAL": "RELEASED", "CANCELED": "CANCELLED"}
    value = str(value or "").strip().upper()
    return aliases.get(value, value if value in {"SCHEDULED","RELEASED","CANCELLED"} else "UNKNOWN")

def normalize_affected_metadata(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        values = value.replace(";", ",").split(",")
    elif isinstance(value, (list, tuple, set)):
        values = value
    else:
        values = [value]
    return sorted({str(v).strip().upper() for v in values if str(v).strip()})

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
        provider_id = event.raw.get("id") or event.raw.get("eventId") or event.raw.get("event_id")
        if provider_id not in (None, ""):
            return str(provider_id)
        event_time, _ = _fmp_time(event)
        identity = {
            "source": "FMP", "event_time_utc": event_time.isoformat(),
            "title": str(event.raw.get("event", "")).strip().casefold(),
            "affected_currencies": normalize_affected_metadata(event.raw.get("currency")),
            "affected_instruments": normalize_affected_metadata(event.raw.get("affected_instruments")),
        }
    else:
        identity = {
            "source": event.source, "event_time_utc": event.event_time_utc.isoformat(),
            "title": event.title.strip().casefold(),
            "affected_currencies": sorted(event.affected_currencies),
            "affected_instruments": sorted(event.affected_instruments),
        }
    return hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def normalize_source_event(event: ProviderEvent) -> NewsEvent:
    event_time, source_tz = _fmp_time(event)
    raw = event.raw
    title = str(raw.get("event", "")).strip()
    if not title:
        raise ValueError("FMP event title is missing")
    status = normalize_status(raw.get("status"))
    if status == "UNKNOWN":
        status = "SCHEDULED" if event_time > datetime.now(timezone.utc) else "RELEASED"
    result = NewsEvent("", event_time, source_tz, event_time, title, normalize_impact(raw.get("impact")),
        normalize_affected_metadata(raw.get("currency")),
        normalize_affected_metadata(raw.get("affected_instruments")), status,
        None if raw.get("estimate") is None else str(raw.get("estimate")),
        None if raw.get("previous") is None else str(raw.get("previous")),
        None if raw.get("actual") is None else str(raw.get("actual")), "FMP")
    return NewsEvent(**{**result.__dict__, "event_id": build_event_id(result)})

def validate_news_event(event: NewsEvent) -> None:
    if not event.event_id or not event.title or event.source != "FMP":
        raise ValueError("invalid NewsEvent")
    if event.event_time_utc.tzinfo is None or event.source_timestamp.tzinfo is None:
        raise ValueError("NewsEvent timestamps must be timezone-aware")
    if event.impact not in {"LOW","MEDIUM","HIGH","UNKNOWN"}:
        raise ValueError("invalid impact")
    if event.status not in {"SCHEDULED","RELEASED","CANCELLED","UNKNOWN"}:
        raise ValueError("invalid status")

def sort_news_events(events: Sequence[NewsEvent]) -> list[NewsEvent]:
    return sorted(events, key=lambda e: (e.event_time_utc, e.event_id))

def _same_identity(a: NewsEvent, b: NewsEvent) -> bool:
    return (a.event_id, a.event_time_utc, a.title.casefold(),
            tuple(a.affected_currencies), tuple(a.affected_instruments), a.source) ==            (b.event_id, b.event_time_utc, b.title.casefold(),
            tuple(b.affected_currencies), tuple(b.affected_instruments), b.source)

def _merge_pair(old: NewsEvent, new: NewsEvent) -> NewsEvent:
    if not _same_identity(old, new):
        raise ValueError(f"conflicting identity for event_id {old.event_id}")
    return NewsEvent(old.event_id, old.source_timestamp, old.source_timezone, old.event_time_utc,
        old.title, new.impact if new.impact != "UNKNOWN" else old.impact,
        old.affected_currencies, old.affected_instruments,
        new.status if new.status != "UNKNOWN" else old.status,
        new.forecast if new.forecast is not None else old.forecast,
        new.previous if new.previous is not None else old.previous,
        new.actual if new.actual is not None else old.actual, old.source)

def merge_news_events(existing: Sequence[NewsEvent], incoming: Sequence[NewsEvent]) -> list[NewsEvent]:
    merged: dict[str, NewsEvent] = {}
    for event in list(existing) + list(incoming):
        validate_news_event(event)
        merged[event.event_id] = _merge_pair(merged[event.event_id], event) if event.event_id in merged else event
    return sort_news_events(list(merged.values()))

def normalize_news_events(events: Sequence[ProviderEvent]) -> list[NewsEvent]:
    return merge_news_events([], [normalize_source_event(e) for e in events])

def apply_news_retention(events: Sequence[NewsEvent], now: datetime | None = None,
                         protected_start: datetime | None = None,
                         protected_end: datetime | None = None) -> list[NewsEvent]:
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=NEWS_RETENTION_DAYS)
    return sort_news_events([e for e in events if
        (protected_start is not None and protected_end is not None and protected_start <= e.event_time_utc <= protected_end)
        or e.event_time_utc >= cutoff])

def get_news_data_path() -> Path:
    """Return the shared cache located beside this module."""
    return NEWS_DATA_PATH

def _event_to_dict(event: NewsEvent) -> dict[str, Any]:
    return {"event_id": event.event_id, "source_timestamp": event.source_timestamp.astimezone(timezone.utc).isoformat(),
            "source_timezone": event.source_timezone, "event_time_utc": event.event_time_utc.astimezone(timezone.utc).isoformat(),
            "title": event.title, "impact": event.impact, "affected_currencies": event.affected_currencies,
            "affected_instruments": event.affected_instruments, "status": event.status,
            "forecast": event.forecast, "previous": event.previous, "actual": event.actual, "source": event.source}

def _event_from_dict(raw: dict[str, Any]) -> NewsEvent:
    event = NewsEvent(str(raw["event_id"]), parse_iso8601(str(raw["source_timestamp"])),
        raw.get("source_timezone"), parse_iso8601(str(raw["event_time_utc"])), str(raw["title"]),
        str(raw["impact"]), normalize_affected_metadata(raw.get("affected_currencies")),
        normalize_affected_metadata(raw.get("affected_instruments")), str(raw["status"]),
        raw.get("forecast"), raw.get("previous"), raw.get("actual"), str(raw["source"]))
    validate_news_event(event)
    return event

def load_news_data(path: Path | str) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {"events": [], "available_start": None, "available_end": None,
                "last_successful_update_utc": None}
    document = json.loads(target.read_text(encoding="utf-8"))
    document["events"] = [_event_from_dict(e) for e in document.get("events", [])]
    return document

def _serialize_document(document: dict[str, Any]) -> dict[str, Any]:
    return {"events": [_event_to_dict(e) if isinstance(e, NewsEvent) else e for e in document.get("events", [])],
            "available_start": document.get("available_start"),
            "available_end": document.get("available_end"),
            "last_successful_update_utc": document.get("last_successful_update_utc")}

def save_news_data_atomic(path: Path | str, document: dict[str, Any]) -> None:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(_serialize_document(document), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    last_error = None
    for attempt in range(WRITE_RETRY_LIMIT):
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as f:
                temp_name = f.name; f.write(payload); f.flush(); os.fsync(f.fileno())
            os.replace(temp_name, target); return
        except OSError as exc:
            last_error = exc
            if temp_name:
                try: os.unlink(temp_name)
                except OSError: pass
            if attempt + 1 < WRITE_RETRY_LIMIT: time.sleep(WRITE_RETRY_DELAY_SECONDS)
    raise RuntimeError(f"atomic news-data save failed: {last_error}")

def _parse_doc_time(value: Any) -> datetime | None:
    if not value: return None
    return parse_iso8601(str(value))

def cache_refresh_due(document: dict[str, Any], now: datetime) -> bool:
    last = _parse_doc_time(document.get("last_successful_update_utc"))
    end = _parse_doc_time(document.get("available_end"))
    return (last is None or now - last >= NEWS_REFRESH_INTERVAL or
            end is None or end < now + timedelta(days=NEWS_FORWARD_DAYS))

def resolve_news_range(request: NewsDataRequest, existing: dict[str, Any]) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    if request.start_time is not None or request.end_time is not None:
        start = request.start_time or now - timedelta(days=NEWS_REFRESH_BACKFILL_DAYS)
        end = request.end_time or now + timedelta(days=NEWS_FORWARD_DAYS)
    else:
        start = now - timedelta(days=NEWS_REFRESH_BACKFILL_DAYS)
        end = now + timedelta(days=NEWS_FORWARD_DAYS)
        existing_end = _parse_doc_time(existing.get("available_end"))
        if existing_end and existing_end > end:
            end = existing_end
    if start > end: raise ValueError("news start_time must not exceed end_time")
    return start, end

def update_news_events(request: NewsDataRequest, provider: NewsDataProvider,
                       existing: dict[str, Any], now: datetime | None = None) -> tuple[list[NewsEvent], datetime, datetime, bool]:
    now = now or datetime.now(timezone.utc)
    explicit_range = request.start_time is not None or request.end_time is not None
    if not request.force and not explicit_range and not cache_refresh_due(existing, now):
        current = [_event_from_dict(e) if isinstance(e, dict) else e for e in existing.get("events", [])]
        end = _parse_doc_time(existing.get("available_end")) or now
        start = _parse_doc_time(existing.get("available_start")) or now
        return sort_news_events(current), start, end, False

    start, end = resolve_news_range(request, existing)
    acquired = provider.fetch_current() if request.live and not explicit_range else provider.fetch_range(start, end)
    normalized = normalize_news_events(acquired)
    current = [_event_from_dict(e) if isinstance(e, dict) else e for e in existing.get("events", [])]
    merged = merge_news_events(current, normalized)
    return apply_news_retention(merged, now=now, protected_start=request.start_time, protected_end=request.end_time), start, end, True

def build_argument_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Maintain shared normalized FMP economic-calendar cache.")
    p.add_argument("--symbol", required=True)
    p.add_argument("--starttime"); p.add_argument("--endtime")
    p.add_argument("--live", action="store_true")
    p.add_argument("--force", action="store_true", help="bypass the news cache refresh limit")
    p.add_argument("--debug", action="store_true")
    return p

def parse_news_data_request(argv: Sequence[str] | None = None) -> NewsDataRequest:
    args = build_argument_parser().parse_args(argv)
    request = NewsDataRequest(normalize_symbol(args.symbol),
        parse_iso8601(args.starttime) if args.starttime else None,
        parse_iso8601(args.endtime) if args.endtime else None,
        bool(args.live), bool(args.force), bool(args.debug))
    validate_news_data_request(request); return request

def validate_news_data_request(request: NewsDataRequest) -> None:
    normalize_symbol(request.symbol)
    if request.start_time and request.end_time and request.start_time > request.end_time:
        raise ValueError("starttime must not be after endtime")

def run(request: NewsDataRequest, provider: NewsDataProvider | None = None) -> int:
    path = get_news_data_path()
    existing = load_news_data(path)
    try:
        events, start, end, changed = update_news_events(request, provider or create_news_provider(),
                                                         existing)
        if not changed:
            return 0
        document = {"events": events, "available_start": start.isoformat(),
                    "available_end": end.isoformat(),
                    "last_successful_update_utc": datetime.now(timezone.utc).isoformat()}
        save_news_data_atomic(path, document)
        return 0
    except Exception as exc:
        if request.debug: print(f"news_data: {exc}", file=sys.stderr)
        return 1

def main(argv: Sequence[str] | None = None) -> int:
    try: return run(parse_news_data_request(argv))
    except Exception as exc:
        print(f"news_data: {exc}", file=sys.stderr); return 1

if __name__ == "__main__":
    raise SystemExit(main())
