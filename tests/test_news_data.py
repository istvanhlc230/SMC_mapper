import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import news_data


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def sample_event(
    date: str = "2026-10-05 12:30:00",
    currency: str = "USD",
    impact: str = "High",
):
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


def update_request(force=False, start=None, end=None):
    return news_data.NewsUpdateRequest(
        start_time=start,
        end_time=end,
        force=force,
        debug=False,
    )


def query_request(symbol="USDJPY", start=None, end=None, force=False):
    return news_data.NewsQueryRequest(
        symbol=symbol,
        start_time=start,
        end_time=end,
        impacts=(),
        statuses=(),
        limit=None,
        force=force,
        debug=False,
    )


def test_fmp_provider_returns_raw_events():
    provider = news_data.FMPNewsDataProvider(
        "key",
        opener=opener_for([sample_event()]),
    )
    result = provider.fetch_range(
        dt("2026-10-05T00:00:00Z"),
        dt("2026-10-05T23:59:59Z"),
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
        news_data.ProviderEvent(sample_event()),
        now=dt("2026-10-02T12:00:00Z"),
    )
    assert event.source == "FMP"
    assert event.event_time_utc == dt("2026-10-05T12:30:00Z")
    assert event.source_timezone == "UTC"
    assert event.impact == "HIGH"
    assert event.affected_currencies == ["USD"]
    assert event.forecast == "3.2"




def test_provider_id_is_preserved():
    raw = dict(sample_event(), id="fmp-event-42")
    event = news_data.normalize_source_event(
        news_data.ProviderEvent(raw),
        now=dt("2026-10-02T12:00:00Z"),
    )
    assert event.event_id == "fmp-event-42"

def test_fallback_identity_ignores_mutable_fields():
    first = sample_event()
    second = dict(first, estimate=9, actual=3.4, impact="Low")
    assert news_data.build_event_id(
        news_data.ProviderEvent(first)
    ) == news_data.build_event_id(news_data.ProviderEvent(second))


def test_duplicate_merge_updates_actual():
    first = news_data.normalize_source_event(
        news_data.ProviderEvent(sample_event()),
        now=dt("2026-10-02T12:00:00Z"),
    )
    second = news_data.normalize_source_event(
        news_data.ProviderEvent(dict(sample_event(), actual=3.4)),
        now=dt("2026-10-02T12:00:00Z"),
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
        "key",
        opener=opener_for([sample_event()], calls),
    )
    existing = {
        "events": [],
        "available_start": "2026-10-01T00:00:00Z",
        "available_end": "2026-10-10T00:00:00Z",
        "last_successful_update_utc": "2026-10-02T11:30:00Z",
    }
    document, changed = news_data.update_news_cache(
        update_request(force=True),
        provider,
        existing,
        now=dt("2026-10-02T12:00:00Z"),
    )
    assert changed
    assert document["events"]
    assert calls


def test_fresh_cache_skips_provider():
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
        update_request(),
        FailingProvider(),
        existing,
        now=dt("2026-10-02T12:00:00Z"),
    )
    assert not changed
    assert document == existing


def test_fx_symbol_query_uses_currency_metadata():
    event = news_data.normalize_source_event(
        news_data.ProviderEvent(sample_event()),
        now=dt("2026-10-02T12:00:00Z"),
    )
    result = news_data.query_news_events(
        query_request("EURUSD"),
        {"events": [event]},
    )
    assert result == [event]


def test_query_limit_and_filters():
    events = [
        news_data.normalize_source_event(
            news_data.ProviderEvent(
                sample_event(
                    date=f"2026-10-0{day} 12:30:00",
                    impact="High" if day != 6 else "Low",
                )
            ),
            now=dt("2026-10-02T12:00:00Z"),
        )
        for day in (5, 6, 7)
    ]
    request = news_data.NewsQueryRequest(
        symbol="EURUSD",
        start_time=dt("2026-10-05T00:00:00Z"),
        end_time=dt("2026-10-07T23:59:59Z"),
        impacts=("HIGH",),
        statuses=("SCHEDULED",),
        limit=1,
        force=False,
        debug=False,
    )
    result = news_data.query_news_events(request, {"events": events})
    assert len(result) == 1
    assert result[0].impact == "HIGH"


def test_query_materializes_symbol_view(tmp_path, monkeypatch):
    monkeypatch.setattr(news_data, "NEWS_CACHE_PATH", Path(tmp_path) / "news_data.json")
    monkeypatch.setattr(
        news_data,
        "DEFAULT_DATA_DIRECTORY",
        Path(tmp_path) / "data",
    )

    event = news_data.normalize_source_event(
        news_data.ProviderEvent(sample_event()),
        now=dt("2026-10-02T12:00:00Z"),
    )
    request = query_request("USDJPY")
    request = news_data.NewsQueryRequest(
        symbol=request.symbol,
        start_time=dt("2026-10-05T00:00:00Z"),
        end_time=dt("2026-10-12T00:00:00Z"),
        impacts=(),
        statuses=(),
        limit=None,
        force=False,
        debug=False,
    )

    cache_document = {
        "schema_version": 1,
        "provider": "FMP",
        "events": [event],
        "available_start": "2026-10-04T00:00:00+00:00",
        "available_end": "2026-10-12T00:00:00+00:00",
        "last_successful_update_utc": "2026-10-02T12:00:00+00:00",
    }
    path = news_data.materialize_symbol_news(request, cache_document)
    assert path == (
        Path(tmp_path) / "data" / "USDJPY" / "USDJPY_news_data.json"
    )
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["symbol"] == "USDJPY"
    assert len(saved["events"]) == 1


def test_run_query_refreshes_then_materializes(tmp_path, monkeypatch):
    monkeypatch.setattr(news_data, "NEWS_CACHE_PATH", Path(tmp_path) / "news_data.json")
    monkeypatch.setattr(news_data, "DEFAULT_DATA_DIRECTORY", Path(tmp_path) / "data")

    calls = []
    provider = news_data.FMPNewsDataProvider(
        "key",
        opener=opener_for([sample_event()], calls),
    )
    request = query_request("USDJPY")
    rc = news_data.run_query(
        request,
        provider=provider,
        now=dt("2026-10-02T12:00:00Z"),
    )
    assert rc == 0
    assert len(calls) == 1
    assert (
        Path(tmp_path) / "data" / "USDJPY" / "USDJPY_news_data.json"
    ).exists()


def test_query_reuses_fresh_shared_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(news_data, "NEWS_CACHE_PATH", Path(tmp_path) / "news_data.json")
    monkeypatch.setattr(news_data, "DEFAULT_DATA_DIRECTORY", Path(tmp_path) / "data")

    event = news_data.normalize_source_event(
        news_data.ProviderEvent(sample_event()),
        now=dt("2026-10-02T12:00:00Z"),
    )
    news_data.save_news_data_atomic(
        Path(tmp_path) / "news_data.json",
        {
            "schema_version": 1,
            "provider": "FMP",
            "events": [event],
            "available_start": "2026-10-02T00:00:00+00:00",
            "available_end": "2026-10-12T00:00:00+00:00",
            "last_successful_update_utc": "2026-10-02T11:30:00+00:00",
        },
    )

    class FailingProvider(news_data.NewsDataProvider):
        def fetch_range(self, start_time, end_time):
            raise AssertionError("FMP must not be called")

    assert news_data.run_query(
        query_request("USDJPY"),
        provider=FailingProvider(),
        now=dt("2026-10-02T12:00:00Z"),
    ) == 0
    assert (
        Path(tmp_path) / "data" / "USDJPY" / "USDJPY_news_data.json"
    ).exists()


def test_fmp_range_chunks_at_90_days():
    calls = []
    provider = news_data.FMPNewsDataProvider(
        "key",
        opener=opener_for([], calls),
    )
    provider.fetch_range(
        dt("2026-01-01T00:00:00Z"),
        dt("2026-04-01T00:00:00Z"),
    )
    assert len(calls) == 2


def test_cli_query_mode():
    parser = news_data.build_argument_parser()
    args = parser.parse_args(["--query", "USDJPY", "--force"])
    assert args.query == "USDJPY"
    assert args.force is True


def test_update_mode_has_no_symbol():
    parser = news_data.build_argument_parser()
    args = parser.parse_args(["--update"])
    assert args.update is True


def test_query_refreshes_when_start_is_outside_cache():
    now = dt("2026-10-02T12:00:00Z")
    document = {
        "events": [],
        "available_start": "2026-10-02T00:00:00Z",
        "available_end": "2026-10-12T00:00:00Z",
        "last_successful_update_utc": "2026-10-02T11:30:00Z",
    }
    request = news_data.NewsQueryRequest(
        symbol="USDJPY",
        start_time=dt("2026-09-30T00:00:00Z"),
        end_time=dt("2026-10-03T00:00:00Z"),
        impacts=(),
        statuses=(),
        limit=None,
        force=False,
        debug=False,
    )
    assert news_data.should_refresh_for_query(request, document, now)
