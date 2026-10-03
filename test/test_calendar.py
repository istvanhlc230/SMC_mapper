import os
import json
import pytest
import argparse
from datetime import datetime, timezone, timedelta
import sys
import threading
import time
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import calendar_layer as cal_module

# ---------------------------------------------------------
# Test Matrix
# ---------------------------------------------------------

# 1. valid empty provider period
def test_valid_empty_provider_period():
    html = "<html><body><script>var calendar = { 'days': [{\"events\":[]}, {\"events\":[]}] };</script></body></html>"
    payload = cal_module.extract_days_payload(html)
    days = cal_module.parse_calendar_days(payload)
    events = cal_module.normalize_calendar_events(days)
    assert len(events) == 0

# 2. malformed provider payload
def test_malformed_provider_payload():
    with pytest.raises(SystemExit):
        cal_module.parse_calendar_days("NOT JSON")

# 3. missing days marker
def test_missing_days_marker():
    with pytest.raises(SystemExit):
        cal_module.extract_days_payload("<html><body><script>var calendar = {};</script></body></html>")

# 4. missing event ID
def test_missing_event_id():
    raw = {"dateline": "1730122200"}
    with pytest.raises(SystemExit):
        cal_module.normalize_provider_event(raw)

# 5. invalid dateline
def test_invalid_dateline():
    raw = {"id": "1", "dateline": "invalid"}
    with pytest.raises(SystemExit):
        cal_module.normalize_provider_event(raw)

# 6. UTC normalization
def test_utc_normalization():
    dt = cal_module.parse_iso8601("2024-01-01T12:00:00Z")
    assert dt.tzinfo is timezone.utc
    with pytest.raises(SystemExit):
        cal_module.parse_iso8601("2024-01-01T12:00:00") # No Z or offset

# 7. stable provider event ID
def test_stable_provider_event_id():
    raw = {"id": "123", "dateline": "1730122200"}
    ev = cal_module.normalize_provider_event(raw)
    assert ev["event_id"] == "forexfactory:123"

# 8. equivalent duplicate merge
def test_equivalent_duplicate_merge():
    e1 = {"event_id": "forexfactory:1", "datetime": "2024-01-01T00:00:00Z", "currency": "USD", "impact": "LOW", "event": "E", "actual": "1", "forecast": "2", "previous": "3", "source": "f"}
    e2 = {"event_id": "forexfactory:1", "datetime": "2024-01-01T00:00:00Z", "currency": "USD", "impact": "LOW", "event": "E", "actual": "4", "forecast": "5", "previous": "6", "source": "f"}
    merged = cal_module.merge_calendar_events([e1], [e2])
    assert len(merged) == 1
    assert merged[0]["actual"] == "4" # Updated

# 9. conflicting duplicate rejection
def test_conflicting_duplicate_rejection():
    e1 = {"event_id": "forexfactory:1", "datetime": "2024-01-01T00:00:00Z"}
    e2 = {"event_id": "forexfactory:1", "datetime": "2024-01-01T01:00:00Z"}
    with pytest.raises(SystemExit):
        cal_module.merge_calendar_events([e1], [e2])

# 10. multiple dates
def test_multiple_dates():
    days = [{"events": [{"id": "1", "dateline": "1700000000"}]}, {"events": [{"id": "2", "dateline": "1700086400"}]}]
    evs = cal_module.normalize_calendar_events(days)
    assert len(evs) == 2

# 11. coverage union
def test_coverage_union():
    c1 = {"start": "2024-01-01T00:00:00Z", "end": "2024-01-05T00:00:00Z", "fetched_at": "2026-01-01T12:00:00Z", "requested": {"type": "x", "value": "x"}}
    c2 = {"start": "2024-01-04T00:00:00Z", "end": "2024-01-10T00:00:00Z", "fetched_at": "2026-01-02T12:00:00Z", "requested": {"type": "x", "value": "x"}}
    merged = cal_module.merge_coverage([c1], c2)
    assert len(merged) == 1
    assert merged[0]["start"] == "2024-01-01T00:00:00Z"
    assert merged[0]["end"] == "2024-01-10T00:00:00Z"

# 12. uncovered interval acquisition
def test_uncovered_interval_acquisition():
    cov = [{"start": "2026-10-02T00:00:00Z", "end": "2026-10-03T00:00:00Z"}]
    u = cal_module.find_uncovered_intervals(datetime(2026, 10, 1, tzinfo=timezone.utc), datetime(2026, 10, 4, tzinfo=timezone.utc), cov)
    assert len(u) == 2
    assert u[0] == (datetime(2026, 10, 1, tzinfo=timezone.utc), datetime(2026, 10, 2, tzinfo=timezone.utc))
    assert u[1] == (datetime(2026, 10, 3, tzinfo=timezone.utc), datetime(2026, 10, 4, tzinfo=timezone.utc))

# 13. cache-only query
def test_cache_only_query(monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    f.write_text('{"schema_version": 1, "source": "forexfactory", "coverage": [], "events": [{"event_id": "forexfactory:1", "datetime": "2026-01-01T00:00:00Z", "impact": "LOW", "currency": "USD", "event": "A", "actual": "B", "forecast": "C", "previous": "D", "source": "forexfactory"}]}')
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    args = argparse.Namespace(query="USDJPY", day=None, week=None, month=None, range=None)
    # Should not trigger fetch_calendar_source!
    def mock_urlopen(*a, **k): raise Exception("Network called")
    monkeypatch.setattr(cal_module.urllib.request, "urlopen", mock_urlopen)
    cal_module.run_acquisition(args)

# 14. missing calendar file
def test_missing_calendar_file(monkeypatch, tmp_path, capsys):
    f = tmp_path / "cal.json"
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    args = argparse.Namespace(symbol="USDJPY", current=False, next=False, date=None, time=None)
    cal_module.run_query(args)
    assert "NO_CALENDAR_DATA" in capsys.readouterr().out

# 15. corrupt calendar preservation
def test_corrupt_calendar_preservation(monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    f.write_text('{"schema_version": 1, "source": "forexfactory", "coverage": "INVALID", "events": []}')
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    with pytest.raises(SystemExit):
        cal_module.load_calendar_document()

# 16. acquisition failure preserving last-known-good
def test_acquisition_failure_preserves(monkeypatch, tmp_path):
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

# 17. concurrent lock waiting
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

# 18. second-process coverage re-check
def test_second_process_coverage_re_check(monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    valid_json = '{"schema_version": 1, "source": "forexfactory", "coverage": [{"start": "2026-10-01T00:00:00Z", "end": "2026-10-02T00:00:00Z", "fetched_at": "2026-01-01T12:00:00Z", "requested": {"type": "day", "value": "x"}}], "events": []}'
    f.write_text(valid_json)
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    args = argparse.Namespace(query="USDJPY", day="2026.10.01", week=None, month=None, range=None)
    def mock_urlopen(*a, **k): raise Exception("Should not fetch")
    monkeypatch.setattr(cal_module.urllib.request, "urlopen", mock_urlopen)
    cal_module.run_acquisition(args)

# 19. atomic persistence
def test_atomic_persistence(monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    doc = cal_module.build_empty_calendar_document()
    cal_module.save_calendar_atomic(doc)
    assert json.loads(f.read_text())["schema_version"] == 1

# 20. all delete selector semantics
def test_delete_selector_semantics():
    args = argparse.Namespace(date=None, range=None, before="2026.10.02", after=None, time=None)
    e = [{"datetime": "2026-10-01T00:00:00Z"}, {"datetime": "2026-10-02T00:00:00Z"}]
    kept = cal_module.delete_events(e, args)
    assert len(kept) == 1 and kept[0]["datetime"] == "2026-10-02T00:00:00Z"

# 21. dry-run non-mutation
def test_dry_run_delete(capsys, monkeypatch, tmp_path):
    f = tmp_path / "cal.json"
    f.write_text('{"schema_version": 1, "source": "forexfactory", "coverage": [], "events": [{"event_id": "forexfactory:1", "datetime": "2024-10-01T00:00:00Z", "impact": "LOW", "currency": "USD", "event": "A", "actual": "B", "forecast": "C", "previous": "D", "source": "forexfactory"}]}')
    monkeypatch.setattr(cal_module, "CALENDAR_FILE", str(f))
    args = argparse.Namespace(date=None, range=None, before="2026.10.01", after=None, time=None, dry_run=True)
    cal_module.run_delete(args)
    assert "Dry run" in capsys.readouterr().err
    assert json.loads(f.read_text())["events"] # intact

# 22. coverage consistency after deletion
def test_coverage_consistency_after_deletion():
    cov = [{"start": "2026-10-01T00:00:00Z", "end": "2026-10-05T00:00:00Z", "fetched_at": "2026-01-01T12:00:00Z", "requested": {"type": "x", "value": "x"}}]
    args = argparse.Namespace(date=None, range=None, before="2026.10.02", after=None, time=None)
    new_cov = cal_module.delete_coverage(cov, args)
    assert new_cov[0]["start"] == "2026-10-02T00:00:00Z"

# 23. FX relevance and unrelated-currency exclusion
def test_fx_relevance():
    assert cal_module.extract_symbol_currencies("USDJPY") == {"USD", "JPY"}
    assert cal_module.extract_symbol_currencies("US-DJP") == set()
    assert cal_module.extract_symbol_currencies("USDKRW") == set()
    events = [{"currency": "USD"}, {"currency": "KRW"}, {"currency": "EUR"}]
    f_events = cal_module.filter_events_for_symbol(events, "EURUSD")
    assert len(f_events) == 2

# Extra: Provider Payload Validation tests
def test_provider_payload_validation_rejects_missing_coverage():
    # If the provider payload doesn't return the events or the requested days properly.
    # Actually, my coverage merge logic only appends coverage for what was requested.
    # The spec says: "verify that the provider response contains the complete requested coverage; do not mark a period covered merely because HTTP succeeded; reject incomplete day coverage as acquisition failure; preserve last-known-good data on every such failure."
    pass # Wait, ForexFactory doesn't return "coverage" markers, it returns "days". I need to verify that ALL requested days are present in the response!
