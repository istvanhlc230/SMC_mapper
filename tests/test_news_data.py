import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import news_data

def dt(v): return datetime.fromisoformat(v.replace("Z", "+00:00"))

class FakeResponse:
    def __init__(self, payload): self.payload = payload
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return json.dumps(self.payload).encode()

def opener_for(payload, calls=None):
    def opener(request, timeout):
        if calls is not None: calls.append(request.full_url)
        return FakeResponse(payload)
    return opener

def payload():
    return [{"date":"2026-10-05 12:30:00","country":"US","event":"CPI",
              "currency":"USD","previous":3.1,"estimate":3.2,"actual":None,"impact":"High"}]

def request(symbol="EURUSD", force=False, live=False):
    return news_data.NewsDataRequest(symbol, None, None, live, force, False)

def test_fmp_provider_returns_raw_events():
    p = news_data.FMPNewsDataProvider("key", opener=opener_for(payload()))
    result = p.fetch_range(dt("2026-10-05T00:00:00Z"), dt("2026-10-05T23:59:59Z"))
    assert isinstance(result[0], news_data.ProviderEvent)
    assert result[0].raw["currency"] == "USD"

def test_fmp_provider_requires_key(monkeypatch):
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    try: news_data.FMPNewsDataProvider()
    except RuntimeError: return
    assert False

def test_fmp_normalization_matches_contract():
    e = news_data.normalize_source_event(news_data.ProviderEvent(payload()[0]))
    assert e.source == "FMP" and e.event_time_utc == dt("2026-10-05T12:30:00Z")
    assert e.source_timezone == "UTC" and e.impact == "HIGH"
    assert e.affected_currencies == ["USD"]
    assert e.forecast == "3.2" and e.previous == "3.1" and e.actual is None
    assert e.status == "SCHEDULED"

def test_fallback_identity_ignores_mutable_fields():
    a = dict(payload()[0]); b = dict(a, estimate=9, actual=3.4, impact="Low")
    assert news_data.build_event_id(news_data.ProviderEvent(a)) == news_data.build_event_id(news_data.ProviderEvent(b))

def test_duplicate_merge_updates_actual():
    a = news_data.normalize_source_event(news_data.ProviderEvent(payload()[0]))
    b = news_data.normalize_source_event(news_data.ProviderEvent(dict(payload()[0], actual=3.4)))
    merged = news_data.merge_news_events([a], [b])
    assert len(merged) == 1 and merged[0].actual == "3.4"

def test_shared_global_path(tmp_path):
    assert news_data.get_news_data_path(tmp_path) == (Path(tmp_path)/"news_data.json").resolve()

def test_cache_not_due():
    now = dt("2026-10-02T12:00:00Z")
    d = {"events": [], "available_end":"2026-10-10T12:00:00Z",
         "last_successful_update_utc":"2026-10-02T00:00:00Z"}
    assert not news_data.cache_refresh_due(d, now)

def test_cache_due_when_stale():
    now = dt("2026-10-03T12:00:00Z")
    d = {"events": [], "available_end":"2026-10-10T12:00:00Z",
         "last_successful_update_utc":"2026-10-02T00:00:00Z"}
    assert news_data.cache_refresh_due(d, now)

def test_force_bypasses_cache(monkeypatch):
    calls=[]
    provider = news_data.FMPNewsDataProvider("key", opener=opener_for(payload(), calls))
    existing={"events":[],"available_start":"2026-10-01T00:00:00Z",
              "available_end":"2026-10-10T00:00:00Z",
              "last_successful_update_utc":"2026-10-02T11:30:00Z"}
    events, start, end, changed = news_data.update_news_events(
        request(force=True), provider, existing, now=dt("2026-10-02T12:00:00Z"))
    assert changed and events and calls

def test_fresh_cache_skips_network():
    class FailingProvider(news_data.NewsDataProvider):
        def fetch_range(self, start_time, end_time): raise AssertionError("network should not be called")
        def fetch_current(self): raise AssertionError("network should not be called")
    existing={"events":[],"available_start":"2026-10-01T00:00:00Z",
              "available_end":"2026-10-10T00:00:00Z",
              "last_successful_update_utc":"2026-10-02T11:30:00Z"}
    events, start, end, changed = news_data.update_news_events(
        request(), FailingProvider(), existing, now=dt("2026-10-02T12:00:00Z"))
    assert not changed and events == []

def test_symbol_does_not_create_symbol_scoped_file(tmp_path):
    assert news_data.get_news_data_path(tmp_path).name == "news_data.json"

def test_atomic_save_reload(tmp_path):
    path = news_data.get_news_data_path(tmp_path)
    e = news_data.normalize_source_event(news_data.ProviderEvent(payload()[0]))
    news_data.save_news_data_atomic(path, {"events":[e],
        "available_start":"2026-10-05T00:00:00+00:00","available_end":"2026-10-10T00:00:00+00:00",
        "last_successful_update_utc":"2026-10-02T12:00:00+00:00"})
    loaded = news_data.load_news_data(path)
    assert loaded["events"][0].event_id == e.event_id

def test_fmp_range_chunks_at_90_days():
    calls=[]
    provider = news_data.FMPNewsDataProvider("key", opener=opener_for([], calls))
    provider.fetch_range(dt("2026-01-01T00:00:00Z"), dt("2026-04-01T00:00:00Z"))
    assert len(calls) == 2


def test_live_uses_provider_current_but_still_honors_cache():
    class CurrentProvider(news_data.NewsDataProvider):
        def __init__(self): self.current_calls = 0
        def fetch_range(self, start_time, end_time): raise AssertionError("range path not expected")
        def fetch_current(self):
            self.current_calls += 1
            return [news_data.ProviderEvent(payload()[0])]
    provider = CurrentProvider()
    existing = {"events": [], "available_start": "2026-10-01T00:00:00Z",
                "available_end": "2026-10-10T00:00:00Z",
                "last_successful_update_utc": "2026-10-02T00:00:00Z"}
    events, _, _, changed = news_data.update_news_events(
        request(live=True), provider, existing, now=dt("2026-10-02T12:00:00Z"))
    assert changed and provider.current_calls == 1
