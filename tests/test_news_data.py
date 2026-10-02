import json
from datetime import datetime, timezone
from pathlib import Path

import news_data


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def sample_event(date="2026-10-05 12:30:00", currency="USD", impact="High"):
    return {
        "date": date,
        "country": "US",
        "event": "CPI",
        "currency": currency,
        "previous": 3.1,
        "estimate": 3.2,
        "actual": None,
        "impact": impact,
    }


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def opener_for(payload, calls=None):
    def opener(request, timeout):
        if calls is not None:
            calls.append(request.full_url)
        return FakeResponse(payload)

    return opener


def update_request(force=False):
    return news_data.NewsUpdateRequest(
        start_time=None, end_time=None, force=force, debug=False
    )


def test_fmp_provider_returns_raw_events():
    provider = news_data.FMPNewsDataProvider(
        "key", opener=opener_for([sample_event()])
    )
    result = provider.fetch_range(
        dt("2026-10-05T00:00:00Z"), dt("2026-10-05T23:59:59Z")
    )
    assert isinstance(result[0], news_data.ProviderEvent)


def test_fmp_provider_requires_key(monkeypatch):
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    try:
        news_data.FMPNewsDataProvider()
    except RuntimeError:
        return
    assert False


def test_fmp_normalization():
    event = news_data.normalize_source_event(
        news_data.ProviderEvent(sample_event())
    )
    assert event.source == "FMP"
    assert event.event_time_utc == dt("2026-10-05T12:30:00Z")
    assert event.affected_currencies == ["USD"]
    assert event.impact == "HIGH"
    assert event.forecast == "3.2"


def test_fallback_identity_ignores_mutable_fields():
    a = sample_event()
    b = dict(a, estimate=9, actual=3.4, impact="Low")
    assert news_data.build_event_id(
        news_data.ProviderEvent(a)
    ) == news_data.build_event_id(news_data.ProviderEvent(b))


def test_duplicate_merge_updates_actual():
    first = news_data.normalize_source_event(
        news_data.ProviderEvent(sample_event())
    )
    second = news_data.normalize_source_event(
        news_data.ProviderEvent(dict(sample_event(), actual=3.4))
    )
    merged = news_data.merge_news_events([first], [second])
    assert len(merged) == 1
    assert merged[0].actual == "3.4"


def test_cache_path_is_module_local():
    path = news_data.get_news_data_path()
    assert path.name == "news_data.json"
    assert path.parent == Path(news_data.__file__).resolve().parent


def test_cache_not_due():
    now = dt("2026-10-02T12:00:00Z")
    document = {
        "events": [],
        "available_end": "2026-10-10T12:00:00Z",
        "last_successful_update_utc": "2026-10-02T00:00:00Z",
    }
    assert not news_data.cache_refresh_due(document, now)


def test_cache_due_when_stale():
    now = dt("2026-10-03T12:00:00Z")
    document = {
        "events": [],
        "available_end": "2026-10-10T12:00:00Z",
        "last_successful_update_utc": "2026-10-02T00:00:00Z",
    }
    assert news_data.cache_refresh_due(document, now)


def test_force_bypasses_cache():
    calls = []
    provider = news_data.FMPNewsDataProvider(
        "key", opener=opener_for([sample_event()], calls)
    )
    existing = {
        "events": [],
        "available_start": "2026-10-01T00:00:00Z",
        "available_end": "2026-10-10T00:00:00Z",
        "last_successful_update_utc": "2026-10-02T11:30:00Z",
    }
    document, changed = news_data.update_news_cache(
        update_request(force=True), provider, existing,
        now=dt("2026-10-02T12:00:00Z")
    )
    assert changed and document["events"] and calls


def test_fresh_cache_skips_network():
    class FailingProvider(news_data.NewsDataProvider):
        def fetch_range(self, start_time, end_time):
            raise AssertionError("provider must not be called")

    existing = {
        "events": [],
        "available_start": "2026-10-01T00:00:00Z",
        "available_end": "2026-10-10T00:00:00Z",
        "last_successful_update_utc": "2026-10-02T11:30:00Z",
    }
    document, changed = news_data.update_news_cache(
        update_request(), FailingProvider(), existing,
        now=dt("2026-10-02T12:00:00Z")
    )
    assert not changed
    assert document == existing


def test_query_by_fx_symbol():
    event = news_data.normalize_source_event(
        news_data.ProviderEvent(sample_event())
    )
    request = news_data.NewsQueryRequest(
        symbol="EURUSD", start_time=None, end_time=None,
        impacts=(), statuses=(), limit=None, force=False, debug=False
    )
    assert news_data.query_news_events(request, {"events": [event]}) == [event]


def test_query_does_not_call_provider_when_cache_is_fresh(monkeypatch):
    event = news_data.normalize_source_event(
        news_data.ProviderEvent(sample_event())
    )
    request = news_data.NewsQueryRequest(
        symbol="EURUSD", start_time=None, end_time=None,
        impacts=(), statuses=(), limit=None, force=False, debug=False
    )
    existing = {
        "events": [event],
        "available_start": "2026-10-01T00:00:00Z",
        "available_end": "2026-10-10T00:00:00Z",
        "last_successful_update_utc": "2026-10-02T11:30:00Z",
    }
    monkeypatch.setattr(news_data, "load_news_data", lambda path: existing)
    monkeypatch.setattr(
        news_data, "create_news_provider",
        lambda: (_ for _ in ()).throw(AssertionError("provider must not be created")),
    )
    assert news_data.run_query(request, now=dt("2026-10-02T12:00:00Z")) == 0


def test_materialized_symbol_file(tmp_path, monkeypatch):
    monkeypatch.setattr(news_data, "NEWS_DATA_PATH", Path(tmp_path) / "news_data.json")
    event = news_data.normalize_source_event(
        news_data.ProviderEvent(sample_event())
    )
    cache = {"events": [event], "provider": "FMP",
             "available_start": "2026-10-04T00:00:00+00:00",
             "available_end": "2026-10-12T00:00:00+00:00",
             "last_successful_update_utc": "2026-10-02T12:00:00+00:00"}
    request = news_data.NewsQueryRequest(
        symbol="USDJPY", start_time=None, end_time=None,
        impacts=(), statuses=(), limit=None, force=False, debug=False
    )
    monkeypatch.setattr(news_data, "__file__", str(tmp_path / "news_data.py"))
    path = news_data.materialize_symbol_news(request, cache)
    assert path == (tmp_path / "USDJPY" / "USDJPY_news_data.json").resolve()
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["symbol"] == "USDJPY"
    assert len(saved["events"]) == 1


def test_fmp_range_chunks_at_90_days():
    calls = []
    provider = news_data.FMPNewsDataProvider("key", opener=opener_for([], calls))
    provider.fetch_range(dt("2026-01-01T00:00:00Z"), dt("2026-04-01T00:00:00Z"))
    assert len(calls) == 2


def test_cli_has_query_mode():
    parser = news_data.build_argument_parser()
    args = parser.parse_args(["--query", "USDJPY"])
    assert args.query == "USDJPY"
