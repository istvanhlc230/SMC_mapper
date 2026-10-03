import os
import json
import pytest
import argparse
from datetime import datetime, timezone, timedelta
import sys
import threading
import time

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
    
    with pytest.raises(SystemExit): cal_module.parse_calendar_request(parser.parse_args(["--query", "USDJPY", "--symbol", "USDJPY"]))
    with pytest.raises(SystemExit): cal_module.parse_calendar_request(parser.parse_args(["--delete", "--time", "12:00"]))
    with pytest.raises(SystemExit): cal_module.parse_calendar_request(parser.parse_args(["--delete", "--date", "2026.01.01", "--time", "12:00-13:00"]))
    with pytest.raises(SystemExit): cal_module.parse_calendar_request(parser.parse_args(["--delete", "--range", "2026.01.01-2026.02.01", "--time", "12:00"]))

def test_ff_date_conversion():
    parser = cal_module.build_argument_parser()
    args = parser.parse_args(["--query", "USDJPY", "--day", "2026.10.28"])
    ptype, pval = cal_module.resolve_provider_period(args)
    assert ptype == "day" and pval == "oct28.2026"
    
def test_input_parsing_strictness():
    with pytest.raises(SystemExit): cal_module.parse_date("2026.1.1") # < 10 chars
    with pytest.raises(SystemExit): cal_module.parse_date_range("2026.10.05-2026.10.01") # reversed
    
def test_extract_days_payload():
    html = "<html><body><script>var calendar = { 'days': [{\"events\":[]}] };</script></body></html>"
    assert cal_module.extract_days_payload(html) == "[{\"events\":[]}]"
    
def test_normalize_provider_event():
    raw = {"id": "123", "dateline": "1730122200", "impact": 3, "country": "USD", "title": "Fed Rate Decision"}
    normalized = cal_module.normalize_provider_event(raw)
    assert normalized["event_id"] == "forexfactory:123"
    
def test_merge_and_deduplicate():
    old = [{"event_id": "forexfactory:1", "datetime": "2024-10-28T13:30:00Z", "currency": "USD", "impact": "HIGH", "event": "A", "actual": None, "forecast": None, "previous": None, "source": "f"}]
    new = [{"event_id": "forexfactory:1", "datetime": "2024-10-28T13:30:00Z", "currency": "USD", "impact": "HIGH", "event": "A", "actual": "Update", "forecast": None, "previous": None, "source": "f"}]
    merged = cal_module.merge_calendar_events(old, new)
    assert merged[0]["actual"] == "Update"

def test_coverage_union():
    c1 = {"start": "2026-10-01T00:00:00Z", "end": "2026-10-05T00:00:00Z", "fetched_at": "2026-10-01T12:00:00Z", "requested": {"type": "day", "value": "x"}}
    c2 = {"start": "2026-10-04T00:00:00Z", "end": "2026-10-10T00:00:00Z", "fetched_at": "2026-10-02T12:00:00Z", "requested": {"type": "day", "value": "x"}}
    merged = cal_module.merge_coverage([c1], c2)
    assert len(merged) == 1 and merged[0]["end"] == "2026-10-10T00:00:00Z"

def test_find_uncovered_intervals():
    cov = [{"start": "2026-10-02T00:00:00Z", "end": "2026-10-05T00:00:00Z", "fetched_at": "2026-10-01T12:00:00Z", "requested": {"type": "day", "value": "x"}}]
    uncovered = cal_module.find_uncovered_intervals(datetime(2026, 9, 28, tzinfo=timezone.utc), datetime(2026, 10, 8, tzinfo=timezone.utc), cov)
    assert len(uncovered) == 2

def test_symbol_relevance():
    assert cal_module.extract_symbol_currencies("USDJPY") == {"USD", "JPY"}
    assert cal_module.extract_symbol_currencies("US-DJP") == set()
    # invalid string
    assert cal_module.extract_symbol_currencies("USDKRW") == set() # KRW not in ForexFactory valid list
    assert cal_module.extract_symbol_currencies("ABCDEF") == set()

def test_delete_coverage():
    cov = [{"start": "2026-10-01T00:00:00Z", "end": "2026-10-05T00:00:00Z", "fetched_at": "test", "requested": {"type": "x", "value": "y"}}]
    args = argparse.Namespace(date=None, range=None, before="2026.10.02", after=None, time=None)
    new_cov = cal_module.delete_coverage(cov, args)
    assert len(new_cov) == 1 and new_cov[0]["start"] == "2026-10-02T00:00:00Z"
    
def test_delete_range_time_coverage():
    cov = [{"start": "2026-10-01T00:00:00Z", "end": "2026-10-03T00:00:00Z", "fetched_at": "test", "requested": {"type": "x", "value": "y"}}]
    args = argparse.Namespace(date=None, range="2026.10.01-2026.10.02", before=None, after=None, time="12:00-13:00")
    new_cov = cal_module.delete_coverage(cov, args)
    assert len(new_cov) > 1

def test_dry_run_delete(capsys, monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    f.write_text('{"schema_version": 1, "source": "forexfactory", "coverage": [], "events": [{"event_id": "forexfactory:1", "datetime": "2024-10-01T00:00:00Z", "impact": "LOW", "currency": "USD", "event": "A", "actual": "B", "forecast": "C", "previous": "D", "source": "forexfactory"}]}')
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    args = argparse.Namespace(date=None, range=None, before="2026.10.01", after=None, time=None, dry_run=True)
    cal_module.run_delete(args)
    assert "Dry run" in capsys.readouterr().err

def test_cache_only_network_bypass(monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    f.write_text('{"schema_version": 1, "source": "forexfactory", "coverage": [], "events": []}')
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    args = argparse.Namespace(query="USDJPY", day=None, week=None, month=None, range=None)
    def mock_urlopen(*a, **k): raise Exception("Network called")
    monkeypatch.setattr(cal_module.urllib.request, "urlopen", mock_urlopen)
    cal_module.run_acquisition(args)

def test_acquisition_failure_preserves_last_known_good(monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    valid_json = '{"schema_version": 1, "source": "forexfactory", "coverage": [], "events": []}'
    f.write_text(valid_json)
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    args = argparse.Namespace(query="USDJPY", day="today", week=None, month=None, range=None)
    def mock_urlopen(*a, **k): raise Exception("Intentional failure")
    monkeypatch.setattr(cal_module.urllib.request, "urlopen", mock_urlopen)
    with pytest.raises(SystemExit):
        cal_module.run_acquisition(args)
    assert f.read_text() == valid_json

def test_malformed_document_handling(monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    f.write_text('{"schema_version": 999}')
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    with pytest.raises(SystemExit):
        cal_module.load_calendar_document()

def test_atomic_persistence(monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    doc = cal_module.build_empty_calendar_document()
    cal_module.save_calendar_atomic(doc)
    assert json.loads(f.read_text())["schema_version"] == 1

def test_concurrent_lock_waiting(monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    events = []
    def lock_acquirer():
        with cal_module.acquire_calendar_lock():
            events.append("acquired")
    
    with cal_module.acquire_calendar_lock():
        t = threading.Thread(target=lock_acquirer)
        t.start()
        time.sleep(0.5)
        assert len(events) == 0
    t.join(timeout=2)
    assert len(events) == 1

def test_coverage_only_deletion_persistence(monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    # Document has coverage, but no events.
    valid_json = '{"schema_version": 1, "source": "forexfactory", "coverage": [{"start": "2026-10-01T00:00:00Z", "end": "2026-10-05T00:00:00Z", "fetched_at": "2026-09-01T00:00:00Z", "requested": {"type": "range", "value": "x"}}], "events": []}'
    f.write_text(valid_json)
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    args = argparse.Namespace(date=None, range=None, before="2026.10.02", after=None, time=None, dry_run=False)
    cal_module.run_delete(args)
    
    doc = json.loads(f.read_text())
    assert doc["coverage"][0]["start"] == "2026-10-02T00:00:00Z" # saved!

def test_pre_lock_coverage_check_skips_fetch(monkeypatch, tmp_path, capsys):
    f = tmp_path / "cal.json"
    valid_json = '{"schema_version": 1, "source": "forexfactory", "coverage": [{"start": "2026-10-01T00:00:00Z", "end": "2026-10-02T00:00:00Z", "fetched_at": "2026-09-01T00:00:00Z", "requested": {"type": "day", "value": "x"}}], "events": []}'
    f.write_text(valid_json)
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    args = argparse.Namespace(query="USDJPY", day="2026.10.01", week=None, month=None, range=None)
    
    # ensure it doesn't crash on urllib
    def mock_urlopen(*a, **k): raise Exception("Should not be called")
    monkeypatch.setattr(cal_module.urllib.request, "urlopen", mock_urlopen)
    
    cal_module.run_acquisition(args)
    out = capsys.readouterr().out
    assert "NO_RELEVANT_EVENT" in out
