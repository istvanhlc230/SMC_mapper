import os
import json
import math
import tempfile
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from smc_htf_ltf_monitor import Monitor, Candle, TargetSetup, Notifier

@pytest.fixture
def mock_zones_config():
    return {
        "unrelated_top_level": "preserved",
        "setups": [
            {
                "ticker": "TEST_TICKER_A",
                "direction": "BUY",
                "target": 100.0,
                "name": "Setup A"
            },
            {
                "ticker": "TEST_TICKER_B",
                "direction": "SELL",
                "target": 50.0,
                "name": "Setup B"
            }
        ]
    }

def test_selective_mutation_and_untouched_state(mock_zones_config):
    # Setup A -> hits target
    # Setup B -> doesn't hit target
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        json.dump(mock_zones_config, tmp)
        config_path = tmp.name

    try:
        with patch.object(Notifier, 'alert') as mock_alert:
            monitor = Monitor(config_path=config_path)
            monitor.load_config()

            # B both lack state in original config
            assert monitor.targets[0].state == "TARGET_ACTIVE"
            assert monitor.targets[1].state == "TARGET_ACTIVE"

            mock_candle_a = Candle(timestamp=datetime.now(), high=105.0, low=95.0) # Hits BUY target
            mock_candle_b = Candle(timestamp=datetime.now(), high=60.0, low=55.0)  # Doesn't hit SELL target (50.0)
            candles = {"TEST_TICKER_A": mock_candle_a, "TEST_TICKER_B": mock_candle_b}
            
            monitor.evaluate(candles)

            # A reached, B active
            assert monitor.targets[0].state == "TARGET_REACHED"
            assert monitor.targets[1].state == "TARGET_ACTIVE"
            
            mock_alert.assert_called_once()
            
            # Verify persistence
            with open(config_path, "r") as f:
                persisted_data = json.load(f)
            
            # Setup A should have state: TARGET_REACHED
            assert persisted_data["setups"][0]["state"] == "TARGET_REACHED"
            
            # Setup B should STILL lack a state field
            assert "state" not in persisted_data["setups"][1]

            # Top level preserved
            assert persisted_data["unrelated_top_level"] == "preserved"
    finally:
        os.remove(config_path)

def test_malformed_targets():
    malformed_config = {
        "setups": [
            {"ticker": "MISSING_TARGET", "direction": "BUY", "name": "M1"}, # missing target
            {"ticker": "NULL_TARGET", "direction": "BUY", "target": None, "name": "M2"}, # null
            {"ticker": "STRING_TARGET", "direction": "BUY", "target": "invalid_string", "name": "M3"}, # string
            {"ticker": "NAN_TARGET", "direction": "BUY", "target": math.nan, "name": "M4"}, # NaN
            {"ticker": "INF_TARGET", "direction": "BUY", "target": math.inf, "name": "M5"}, # +Inf
            {"ticker": "NEGINF_TARGET", "direction": "BUY", "target": -math.inf, "name": "M6"}, # -Inf
            {"ticker": "VALID_TARGET", "direction": "BUY", "target": 100.0, "name": "V1"} # valid neighbor
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        json.dump(malformed_config, tmp)
        config_path = tmp.name

    try:
        with patch.object(Notifier, 'alert') as mock_alert:
            monitor = Monitor(config_path=config_path)
            monitor.load_config()

            # All malformed targets should fail closed to INVALID_STATE
            assert monitor.targets[0].state == "INVALID_STATE"
            assert monitor.targets[1].state == "INVALID_STATE"
            assert monitor.targets[2].state == "INVALID_STATE"
            assert monitor.targets[3].state == "INVALID_STATE"
            assert monitor.targets[4].state == "INVALID_STATE"
            assert monitor.targets[5].state == "INVALID_STATE"
            
            # Valid neighbor is active
            assert monitor.targets[6].state == "TARGET_ACTIVE"

            mock_candle = Candle(timestamp=datetime.now(), high=105.0, low=95.0)
            # Evaluate all
            candles = {
                "MISSING_TARGET": mock_candle,
                "NULL_TARGET": mock_candle,
                "STRING_TARGET": mock_candle,
                "NAN_TARGET": mock_candle,
                "INF_TARGET": mock_candle,
                "NEGINF_TARGET": mock_candle,
                "VALID_TARGET": mock_candle
            }
            
            monitor.evaluate(candles)

            # Only VALID_TARGET reaches target and alerts
            mock_alert.assert_called_once()
            args, kwargs = mock_alert.call_args
            assert "VALID_TARGET" in kwargs["title"]

            with open(config_path, "r") as f:
                persisted = json.load(f)
            
            # Malformed ones remain untouched in JSON (no state field added)
            assert "state" not in persisted["setups"][0]
            assert "state" not in persisted["setups"][1]
            assert "state" not in persisted["setups"][2]
            
            # Valid one got its state updated
            assert persisted["setups"][6]["state"] == "TARGET_REACHED"

    finally:
        os.remove(config_path)

def test_direction_validation():
    config = {
        "setups": [
            {"ticker": "INVALID_DIR", "direction": "UP", "target": 100.0}
        ]
    }
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        json.dump(config, tmp)
        config_path = tmp.name
        
    try:
        monitor = Monitor(config_path=config_path)
        monitor.load_config()
        assert monitor.targets[0].state == "INVALID_STATE"
    finally:
        os.remove(config_path)
