import json
from datetime import datetime, timezone
from pathlib import Path
import pytest
import news_data

def dt(v): return datetime.fromisoformat(v.replace("Z", "+00:00"))

class FakeResponse:
    def __init__(self, payload): self.payload = payload
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return json.dumps(self.payload).encode()

def opener_for(payload):
    def opener(request, timeout): return FakeResponse(payload)
    return opener

def payload():
    return [{"date":"2026-10-05 12:30:00","country":"US","event":"CPI",
              "currency":"USD","previous":3.1,"estimate":3.2,"actual":None,"impact":"High"}]

def test_fmp_provider_returns_raw_events():
    p = news_data.FMPNewsDataProvider("key", opener=opener_for(payload()))
    result = p.fetch_range(dt("2026-10-05T00:00:00Z"), dt("2026-10-05T23:59:59Z"))
    assert isinstance(result[0], news_data.ProviderEvent)
    assert result[0].raw["currency"] == "USD"

def test_fmp_provider_requires_key(monkeypatch):
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    with pytest.raises(RuntimeError): news_data.FMPNewsDataProvider()

def test_fmp_normalization_matches_contract():
    e = news_data.normalize_source_event(news_data.ProviderEvent(payload()[0]))
    assert e.source == "FMP"
    assert e.event_time_utc == dt("2026-10-05T12:30:00Z")
    assert e.source_timezone == "UTC"
    assert e.impact == "HIGH"
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

def test_symbol_scoped_path(tmp_path):
    assert news_data.get_news_data_path("EURUSD", tmp_path) == (Path(tmp_path)/"EURUSD"/"EURUSD_news_data.json").resolve()

def test_path_traversal_rejected(tmp_path):
    with pytest.raises(ValueError): news_data.get_news_data_path("../EURUSD", tmp_path)

def test_atomic_save_reload(tmp_path):
    path = news_data.get_news_data_path("EURUSD", tmp_path)
    e = news_data.normalize_source_event(news_data.ProviderEvent(payload()[0]))
    news_data.save_news_data_atomic(path, {"symbol":"EURUSD","events":[e],
        "available_start":"2026-10-05T00:00:00+00:00","available_end":"2026-10-05T23:59:59+00:00",
        "last_successful_update_utc":"2026-10-02T18:00:00+00:00"})
    loaded = news_data.load_news_data(path, "EURUSD")
    assert loaded["symbol"] == "EURUSD" and loaded["events"][0].event_id == e.event_id
