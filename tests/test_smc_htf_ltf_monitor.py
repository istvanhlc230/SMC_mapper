import json
import os
import tempfile
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

import pytest

from smc_htf_ltf_monitor import (
    MONITOR_SCHEMA_VERSION,
    Monitor,
    MonitorContractError,
    Candle,
    Notifier,
)


def make_setup(
    *,
    ticker="TEST",
    direction="BUY",
    target_id="T1",
    price="100",
    state="TARGET_ACTIVE",
    monitor_id="TEST:1h:L1",
    source="CONFIGURATION",
    structural_hash=None,
    analysis_timestamp=None,
    provenance="CONFIGURED_TARGET_POLICY",
):
    setup = {
        "monitor_id": monitor_id,
        "setup_id": "TEST:1h",
        "leg_id": "L1",
        "ticker": ticker,
        "timeframe": "1h",
        "direction": direction,
        "state": state,
        "analysis_timestamp": analysis_timestamp,
        "structural_hash": structural_hash,
        "target_resolution": {
            "status": "RESOLVED",
            "resolved_target_id": target_id,
        },
        "target_candidates": [
            {
                "target_id": target_id,
                "target_type": "configured target",
                "price": price,
                "provenance": provenance,
            }
        ],
        "target_plan": {
            "leg_id": "L1",
            "target_id": target_id,
            "allocation_pct": "100",
        },
        "target": {
            "target_id": target_id,
            "target_type": "configured target",
            "price": price,
            "provenance": provenance,
        },
    }
    if source == "ANALYZER":
        setup["analysis_timestamp"] = analysis_timestamp or "2026-01-02T00:00:00+00:00"
        setup["structural_hash"] = structural_hash or "abc123"
    return setup


@pytest.fixture
def mock_zones_config():
    return {
        "schema_version": MONITOR_SCHEMA_VERSION,
        "source": "CONFIGURATION",
        "analysis": {
            "instrument": "TEST",
            "timeframe": "1h",
            "analysis_timestamp": None,
            "structural_hash": None,
        },
        "setups": [
            make_setup(ticker="TEST_TICKER_A", direction="BUY", target_id="A", price="100", monitor_id="A:L1"),
            make_setup(ticker="TEST_TICKER_B", direction="SELL", target_id="B", price="50", monitor_id="B:L1"),
        ],
        "unrelated_top_level": "preserved",
    }


def write_config(config):
    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
    json.dump(config, tmp)
    tmp.close()
    return tmp.name


def test_selective_mutation_and_untouched_state(mock_zones_config):
    config_path = write_config(mock_zones_config)
    try:
        with patch.object(Notifier, "alert") as mock_alert:
            monitor = Monitor(config_path=config_path)
            monitor.load_config()
            assert monitor.targets[0].target_price == Decimal("100")
            assert monitor.targets[0].state == "TARGET_ACTIVE"

            monitor.evaluate({
                "TEST_TICKER_A": Candle(datetime(2026, 1, 2, tzinfo=timezone.utc), Decimal("105"), Decimal("95")),
                "TEST_TICKER_B": Candle(datetime(2026, 1, 2, tzinfo=timezone.utc), Decimal("60"), Decimal("55")),
            })

            assert monitor.targets[0].state == "TARGET_REACHED"
            assert monitor.targets[1].state == "TARGET_ACTIVE"
            mock_alert.assert_called_once()

        persisted = json.load(open(config_path, encoding="utf-8"))
        assert persisted["setups"][0]["state"] == "TARGET_REACHED"
        assert persisted["setups"][1]["state"] == "TARGET_ACTIVE"
        assert persisted["unrelated_top_level"] == "preserved"
    finally:
        os.remove(config_path)


def test_persistent_target_reached_no_repeat_notification(mock_zones_config):
    config_path = write_config(mock_zones_config)
    try:
        with patch.object(Notifier, "alert") as mock_alert:
            monitor = Monitor(config_path=config_path)
            monitor.load_config()
            candle = Candle(datetime(2026, 1, 2, tzinfo=timezone.utc), Decimal("105"), Decimal("95"))
            monitor.evaluate({"TEST_TICKER_A": candle})
            mock_alert.assert_called_once()

            monitor2 = Monitor(config_path=config_path)
            monitor2.load_config()
            assert monitor2.targets[0].state == "TARGET_REACHED"
            monitor2.evaluate({"TEST_TICKER_A": candle})
            mock_alert.assert_called_once()
    finally:
        os.remove(config_path)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda c: c["setups"][0].pop("target"),
        lambda c: c["setups"][0]["target_resolution"].update(status="NO_RESOLVED_TARGET"),
        lambda c: c["setups"][0]["target"]["provenance"].__class__ and c["setups"][0]["target"].update(provenance=""),
        lambda c: c["setups"][0].update(direction="UP"),
        lambda c: c.update(schema_version=999),
        lambda c: c["setups"][0].pop("monitor_id"),
    ],
)
def test_invalid_contract_fails_closed(mock_zones_config, mutator):
    config = json.loads(json.dumps(mock_zones_config))
    mutator(config)
    path = write_config(config)
    try:
        monitor = Monitor(path)
        with pytest.raises(MonitorContractError):
            monitor.load_config()
        assert monitor.targets == []
    finally:
        os.remove(path)


def test_legacy_scalar_target_is_rejected():
    config = {
        "schema_version": MONITOR_SCHEMA_VERSION,
        "source": "CONFIGURATION",
        "setups": [
            {
                "ticker": "LEGACY",
                "direction": "BUY",
                "target": 100.0,
            }
        ],
    }
    path = write_config(config)
    try:
        with pytest.raises(MonitorContractError):
            Monitor(path).load_config()
    finally:
        os.remove(path)


def test_analyzer_source_requires_version_metadata(mock_zones_config):
    config = json.loads(json.dumps(mock_zones_config))
    config["source"] = "ANALYZER"
    config["setups"][0]["analysis_timestamp"] = None
    config["setups"][0]["structural_hash"] = None
    path = write_config(config)
    try:
        with pytest.raises(MonitorContractError, match="analysis_timestamp"):
            Monitor(path).load_config()
    finally:
        os.remove(path)


def test_decimal_and_utc_candle_contract():
    with pytest.raises(MonitorContractError):
        Candle(datetime(2026, 1, 2), Decimal("1"), Decimal("0"))
    candle = Candle(datetime(2026, 1, 2, tzinfo=timezone.utc), Decimal("1"), Decimal("0"))
    assert candle.timestamp.tzinfo is not None


def test_save_failure_suppresses_notification(mock_zones_config, monkeypatch):
    path = write_config(mock_zones_config)
    try:
        monitor = Monitor(path)
        monitor.load_config()
        with patch.object(Notifier, "alert") as mock_alert:
            monkeypatch.setattr(monitor, "save_config", lambda: (_ for _ in ()).throw(OSError("disk failure")))
            monitor.evaluate({
                "TEST_TICKER_A": Candle(datetime(2026, 1, 2, tzinfo=timezone.utc), Decimal("105"), Decimal("95"))
            })
            mock_alert.assert_not_called()
            assert monitor.targets[0].state == "TARGET_ACTIVE"
            assert monitor.targets[0].is_dirty is True
    finally:
        os.remove(path)


def test_multi_leg_target_contract_is_monitorable():
    config = {
        "schema_version": MONITOR_SCHEMA_VERSION,
        "source": "ANALYZER",
        "analysis": {
            "instrument": "TEST",
            "timeframe": "1h",
            "analysis_timestamp": "2026-01-02T00:00:00+00:00",
            "structural_hash": "hash",
        },
        "setups": [
            make_setup(
                target_id="T1",
                price="100",
                monitor_id="TEST:1h:L1",
                source="ANALYZER",
                structural_hash="hash",
                analysis_timestamp="2026-01-02T00:00:00+00:00",
            ),
            dict(
                make_setup(
                    target_id="T2",
                    price="110",
                    monitor_id="TEST:1h:L2",
                    source="ANALYZER",
                    structural_hash="hash",
                    analysis_timestamp="2026-01-02T00:00:00+00:00",
                ),
                leg_id="L2",
                target_plan={
                    "leg_id": "L2",
                    "target_id": "T2",
                    "allocation_pct": "50",
                },
            ),
        ],
    }
    path = write_config(config)
    try:
        monitor = Monitor(path)
        monitor.load_config()
        assert {t.leg_id for t in monitor.targets} == {"L1", "L2"}
    finally:
        os.remove(path)
