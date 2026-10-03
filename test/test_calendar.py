import os
import json
import pytest
import argparse
from datetime import datetime, timezone, timedelta
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import calendar as cal_module

def test_cli_period_validation():
    parser = cal_module.build_argument_parser()
    args = parser.parse_args(["--query", "USDJPY"])
    assert cal_module.parse_calendar_request(args) == "ACQUISITION"
    
    args = parser.parse_args(["--symbol", "USDJPY", "--current"])
    assert cal_module.parse_calendar_request(args) == "LOCAL_QUERY"
    
    args = parser.parse_args(["--delete", "--before", "2026.01.01"])
    assert cal_module.parse_calendar_request(args) == "DELETE"
    
    args = parser.parse_args(["--query", "USDJPY", "--symbol", "USDJPY"])
    with pytest.raises(SystemExit): cal_module.parse_calendar_request(args)

    args = parser.parse_args(["--query", "USDJPY", "--day", "today", "--week", "this"])
    with pytest.raises(SystemExit): cal_module.parse_calendar_request(args)

def test_ff_date_conversion():
    parser = cal_module.build_argument_parser()
    args = parser.parse_args(["--query", "USDJPY", "--day", "2026.10.28"])
    ptype, pval = cal_module.resolve_provider_period(args)
    assert ptype == "day" and pval == "oct28.2026"
    
def test_extract_days_payload():
    html = "<html><body><script>var calendar = { 'days': [{\"events\":[]}] };</script></body></html>"
    payload = cal_module.extract_days_payload(html)
    assert payload == "[{\"events\":[]}]"
    
def test_parse_calendar_days():
    days = cal_module.parse_calendar_days("[{\"events\":[]}]")
    assert len(days) == 1 and len(days[0]["events"]) == 0
    with pytest.raises(SystemExit): cal_module.parse_calendar_days("invalid_json")

def test_normalize_provider_event():
    raw = {"id": "123", "dateline": "1730122200", "impact": 3, "country": "USD", "title": "Fed Rate Decision"}
    normalized = cal_module.normalize_provider_event(raw)
    assert normalized["event_id"] == "forexfactory:123"
    assert normalized["datetime"] == "2024-10-28T13:30:00Z"
    assert normalized["currency"] == "USD"
    assert normalized["impact"] == "HIGH"
    
def test_merge_and_deduplicate():
    old = [{"event_id": "forexfactory:1", "datetime": "2024-10-28T13:30:00Z", "actual": None, "impact": "HIGH"}]
    new = [{"event_id": "forexfactory:1", "datetime": "2024-10-28T13:30:00Z", "actual": "Update", "impact": "HIGH"}]
    merged = cal_module.merge_calendar_events(old, new)
    assert len(merged) == 1 and merged[0]["actual"] == "Update"
    bad_new = [{"event_id": "forexfactory:1", "datetime": "2024-10-28T15:30:00Z", "actual": "Update", "impact": "HIGH"}]
    with pytest.raises(SystemExit): cal_module.merge_calendar_events(old, bad_new)

def test_coverage_union():
    c1 = {"start": "2026-10-01T00:00:00Z", "end": "2026-10-05T00:00:00Z", "fetched_at": "2026-10-01T12:00:00Z", "requested": {}}
    c2 = {"start": "2026-10-04T00:00:00Z", "end": "2026-10-10T00:00:00Z", "fetched_at": "2026-10-02T12:00:00Z", "requested": {}}
    merged = cal_module.merge_coverage([c1], c2)
    assert len(merged) == 1 and merged[0]["end"] == "2026-10-10T00:00:00Z"

def test_find_uncovered_intervals():
    cov = [{"start": "2026-10-02T00:00:00Z", "end": "2026-10-05T00:00:00Z", "fetched_at": "2026-10-01T12:00:00Z", "requested": {}}]
    req_start = datetime(2026, 9, 28, tzinfo=timezone.utc)
    req_end = datetime(2026, 10, 8, tzinfo=timezone.utc)
    uncovered = cal_module.find_uncovered_intervals(req_start, req_end, cov)
    assert len(uncovered) == 2
    assert uncovered[0] == (req_start, datetime(2026, 10, 2, tzinfo=timezone.utc))
    assert uncovered[1] == (datetime(2026, 10, 5, tzinfo=timezone.utc), req_end)

def test_symbol_relevance():
    assert cal_module.extract_symbol_currencies("USDJPY") == {"USD", "JPY"}
    assert cal_module.extract_symbol_currencies("US-DJP") == set() # not exactly two recognizable

def test_delete_before():
    events = [{"datetime": "2026-10-01T00:00:00Z"}, {"datetime": "2026-10-01T12:00:00Z"}]
    args = argparse.Namespace(date=None, range=None, before="2026.10.01", after=None, time=None)
    kept = cal_module.delete_events(events, args)
    assert len(kept) == 2 # "before" is strict less than

def test_delete_coverage():
    cov = [{"start": "2026-10-01T00:00:00Z", "end": "2026-10-05T00:00:00Z", "fetched_at": "test", "requested": {}}]
    args = argparse.Namespace(date=None, range=None, before="2026.10.02", after=None, time=None)
    new_cov = cal_module.delete_coverage(cov, args)
    assert len(new_cov) == 1 and new_cov[0]["start"] == "2026-10-02T00:00:00Z"

def test_deterministic_query_ordering():
    events = [{"datetime": "2026-10-05T12:00:00Z", "event_id": "forexfactory:2"}, {"datetime": "2026-10-05T12:00:00Z", "event_id": "forexfactory:1"}]
    next_evs = cal_module.query_next_events(events) # now is earlier since these are in 2026
    assert next_evs[0]["event_id"] == "forexfactory:1"

def test_dry_run_delete(capsys, monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    f.write_text('{"schema_version": 1, "source": "forexfactory", "coverage": [], "events": [{"event_id": "1", "datetime": "2024-10-01T00:00:00Z", "impact": "LOW"}]}')
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    args = argparse.Namespace(date=None, range=None, before="2026.10.01", after=None, time=None, dry_run=True)
    cal_module.run_delete(args)
    assert "Dry run" in capsys.readouterr().err
