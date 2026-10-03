
import os
import json
import pytest
import argparse
from datetime import datetime, timezone, timedelta
import sys

# Add parent directory to path so we can import calendar.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import calendar as cal_module

def test_cli_period_validation():
    # Mutual exclusion
    parser = cal_module.build_argument_parser()
    args = parser.parse_args(["--query", "USDJPY"])
    assert cal_module.parse_calendar_request(args) == "ACQUISITION"
    
    args = parser.parse_args(["--symbol", "USDJPY", "--current"])
    assert cal_module.parse_calendar_request(args) == "LOCAL_QUERY"
    
    args = parser.parse_args(["--delete", "--before", "2026.01.01"])
    assert cal_module.parse_calendar_request(args) == "DELETE"
    
    # Validation
    args = parser.parse_args(["--query", "USDJPY", "--symbol", "USDJPY"])
    with pytest.raises(SystemExit):
        cal_module.parse_calendar_request(args)

def test_ff_date_conversion():
    parser = cal_module.build_argument_parser()
    args = parser.parse_args(["--query", "USDJPY", "--day", "2026.10.28"])
    ptype, pval = cal_module.resolve_provider_period(args)
    assert ptype == "day"
    assert pval == "oct28.2026"
    
def test_extract_days_payload():
    html = "<html><body><script>var calendar = { 'days': [{\"events\":[]}] };</script></body></html>"
    payload = cal_module.extract_days_payload(html)
    assert payload == '[{"events":[]}]'
    
def test_parse_calendar_days():
    # Valid empty day
    json_str = '[{"events":[]}]'
    days = cal_module.parse_calendar_days(json_str)
    assert len(days) == 1
    assert len(days[0]["events"]) == 0
    
    # Malformed payload
    with pytest.raises(SystemExit):
        cal_module.parse_calendar_days("invalid_json")

def test_normalize_provider_event():
    raw = {
        "id": "123",
        "dateline": "1730122200", # 2026-10-28T13:30:00Z
        "impact": 3,
        "country": "USD",
        "title": "Fed Rate Decision",
        "actual": "5.5%",
        "forecast": "5.5%",
        "previous": "5.25%"
    }
    normalized = cal_module.normalize_provider_event(raw)
    assert normalized["event_id"] == "forexfactory:123"
    assert normalized["datetime"] == "2024-10-28T13:30:00Z" # UTC normalization
    assert normalized["currency"] == "USD"
    assert normalized["impact"] == "HIGH"
    
def test_missing_event_id_or_dateline():
    with pytest.raises(SystemExit):
        cal_module.normalize_provider_event({"dateline": "1730122200"})
    with pytest.raises(SystemExit):
        cal_module.normalize_provider_event({"id": "123"})
        
def test_invalid_dateline():
    with pytest.raises(SystemExit):
        cal_module.normalize_provider_event({"id": "123", "dateline": "invalid"})

def test_merge_and_deduplicate():
    old = [{
        "event_id": "forexfactory:1",
        "datetime": "2024-10-28T13:30:00Z",
        "actual": None
    }]
    new = [{
        "event_id": "forexfactory:1",
        "datetime": "2024-10-28T13:30:00Z",
        "actual": "Update" # Mutable update
    }, {
        "event_id": "forexfactory:2",
        "datetime": "2026-10-28T14:00:00Z"
    }]
    merged = cal_module.merge_calendar_events(old, new)
    assert len(merged) == 2
    assert merged[0]["actual"] == "Update" # Equivalent duplicate merge
    
    # Conflicting duplicate rejection
    bad_new = [{
        "event_id": "forexfactory:1",
        "datetime": "2026-10-28T15:30:00Z", # time conflict
        "actual": "Update"
    }]
    with pytest.raises(SystemExit):
        cal_module.merge_calendar_events(old, bad_new)

def test_coverage_union():
    c1 = {"start": "2026-10-01T00:00:00Z", "end": "2026-10-05T00:00:00Z", "fetched_at": "2026-10-01T12:00:00Z"}
    c2 = {"start": "2026-10-04T00:00:00Z", "end": "2026-10-10T00:00:00Z", "fetched_at": "2026-10-02T12:00:00Z"}
    merged = cal_module.merge_coverage([c1], c2)
    assert len(merged) == 1
    assert merged[0]["start"] == "2026-10-01T00:00:00Z"
    assert merged[0]["end"] == "2026-10-10T00:00:00Z"
    assert merged[0]["fetched_at"] == "2026-10-02T12:00:00Z"

def test_symbol_relevance():
    currencies = cal_module.extract_symbol_currencies("USDJPY")
    assert currencies == {"USD", "JPY"}
    
    events = [
        {"currency": "USD"},
        {"currency": "EUR"},
        {"currency": "JPY"}
    ]
    filtered = cal_module.filter_events_for_symbol(events, "USDJPY")
    assert len(filtered) == 2
    assert filtered[0]["currency"] == "USD"
    assert filtered[1]["currency"] == "JPY"
    
def test_malformed_calendar_json(tmp_path):
    cal_file = tmp_path / "calendar.json"
    cal_file.write_text("invalid json")
    
    cal_module.CALENDAR_FILE = str(cal_file)
    with pytest.raises(SystemExit):
        cal_module.load_calendar_document()

def test_missing_calendar_returns_empty(tmp_path, capsys):
    cal_file = tmp_path / "calendar.json"
    cal_module.CALENDAR_FILE = str(cal_file)
    
    # Missing calendar.json returns valid empty result
    parser = cal_module.build_argument_parser()
    args = parser.parse_args(["--symbol", "USDJPY", "--current"])
    cal_module.run_query(args)
    
    captured = capsys.readouterr()
    res = json.loads(captured.out)
    assert res["status"] == "NO_CALENDAR_DATA"

def test_delete_before():
    events = [
        {"datetime": "2026-09-30T23:59:00Z"},
        {"datetime": "2026-10-01T00:00:00Z"},
        {"datetime": "2026-10-01T12:00:00Z"}
    ]
    args = argparse.Namespace(date=None, range=None, before="2026.10.01", after=None, time=None)
    kept = cal_module.delete_events(events, args)
    assert len(kept) == 2
    assert kept[0]["datetime"] == "2026-10-01T00:00:00Z"

def test_delete_after():
    events = [
        {"datetime": "2026-10-01T23:59:59Z"},
        {"datetime": "2026-10-02T00:00:00Z"}
    ]
    args = argparse.Namespace(date=None, range=None, before=None, after="2026.10.01", time=None)
    kept = cal_module.delete_events(events, args)
    assert len(kept) == 1
    assert kept[0]["datetime"] == "2026-10-01T23:59:59Z"

def test_delete_time_range():
    events = [
        {"datetime": "2026-10-01T13:00:00Z"},
        {"datetime": "2026-10-01T14:30:00Z"},
        {"datetime": "2026-10-01T15:00:00Z"}
    ]
    args = argparse.Namespace(date=None, range="2026.10.01-2026.10.01", before=None, after=None, time="14:00-14:59")
    kept = cal_module.delete_events(events, args)
    assert len(kept) == 2
    assert kept[0]["datetime"] == "2026-10-01T13:00:00Z"
    assert kept[1]["datetime"] == "2026-10-01T15:00:00Z"


def test_query_current_events():
    now = datetime.now(timezone.utc)
    events = [
        {"datetime": cal_module.format_iso8601(now)},
        {"datetime": cal_module.format_iso8601(now + timedelta(minutes=5))}
    ]
    curr = cal_module.query_current_events(events)
    assert len(curr) == 1
    assert curr[0]["datetime"] == events[0]["datetime"]

def test_query_next_events():
    now = datetime.now(timezone.utc)
    events = [
        {"datetime": cal_module.format_iso8601(now - timedelta(minutes=5))},
        {"datetime": cal_module.format_iso8601(now + timedelta(minutes=5))},
        {"datetime": cal_module.format_iso8601(now + timedelta(minutes=5, seconds=30))},
        {"datetime": cal_module.format_iso8601(now + timedelta(minutes=10))}
    ]
    next_evs = cal_module.query_next_events(events)
    assert len(next_evs) == 1
    assert next_evs[0]["datetime"] == events[1]["datetime"]

def test_query_nearest_events():
    now = datetime.now(timezone.utc)
    events = [
        {"datetime": cal_module.format_iso8601(now - timedelta(minutes=10))},
        {"datetime": cal_module.format_iso8601(now + timedelta(minutes=2))}
    ]
    nearest = cal_module.query_nearest_events(events, now)
    assert len(nearest) == 1
    assert nearest[0]["datetime"] == events[1]["datetime"]

def test_dry_run_delete(capsys):
    events = [{"datetime": "2026-10-01T00:00:00Z"}]
    args = argparse.Namespace(date=None, range=None, before="2026.10.02", after=None, time=None, dry_run=True)
    # in run_delete dry_run prevents save, we'll just test that it reports
    cal_module.CALENDAR_FILE = "nonexistent.json"
    cal_module.run_delete(args)
    captured = capsys.readouterr()
    assert "Dry run" in captured.err
