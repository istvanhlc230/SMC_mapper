import os
import json
import tempfile
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import the Monitor class
from smc_htf_ltf_monitor import Monitor, Candle, TargetSetup, Notifier

@pytest.fixture
def mock_zones_config():
    return {
        "unrelated_top_level": "preserved",
        "setups": [
            {
                "ticker": "TEST_TICKER",
                "direction": "BUY",
                "target": 100.0,
                "name": "Test Configuration Setup",
                "unrelated_setup_field": "preserved"
            }
        ]
    }

def test_target_reached_persistence_and_no_repeat_notification(mock_zones_config):
    # Setup temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        json.dump(mock_zones_config, tmp)
        config_path = tmp.name

    try:
        # Patch Notifier to spy on notifications
        with patch.object(Notifier, 'alert') as mock_alert:
            monitor = Monitor(config_path=config_path)
            monitor.load_config()

            # 1. Verify initial load state is TARGET_ACTIVE
            assert len(monitor.targets) == 1
            assert monitor.targets[0].state == "TARGET_ACTIVE"
            assert monitor.targets[0].provenance == "Configuration Setup ID: Test Configuration Setup"

            # 2. Evaluate target (price reaches target)
            mock_candle = Candle(timestamp=datetime.now(), high=105.0, low=95.0)
            candles = {"TEST_TICKER": mock_candle}
            monitor.evaluate(candles)

            # 3. Verify in-memory state transition to TARGET_REACHED and notification fired
            assert monitor.targets[0].state == "TARGET_REACHED"
            mock_alert.assert_called_once()
            mock_alert.reset_mock()

            # 4. Verify state was persisted to JSON without losing unrelated fields
            with open(config_path, "r") as f:
                persisted_data = json.load(f)
            assert persisted_data["unrelated_top_level"] == "preserved"
            assert persisted_data["setups"][0]["unrelated_setup_field"] == "preserved"
            assert persisted_data["setups"][0]["state"] == "TARGET_REACHED"

            # 5. Reload config (simulating loop reload or restart)
            monitor.load_config()
            assert monitor.targets[0].state == "TARGET_REACHED"

            # 6. Evaluate again with same or new candle reaching target
            monitor.evaluate(candles)

            # 7. Verify NO second notification is emitted
            mock_alert.assert_not_called()

    finally:
        os.remove(config_path)

def test_invalid_lifecycle_input_fails_closed(mock_zones_config):
    # Inject an invalid state
    mock_zones_config["setups"][0]["state"] = "INVALID_UNKNOWN_STATE"
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        json.dump(mock_zones_config, tmp)
        config_path = tmp.name

    try:
        with patch.object(Notifier, 'alert') as mock_alert:
            monitor = Monitor(config_path=config_path)
            monitor.load_config()

            # The invalid state should fail closed to "INVALID_STATE" (or similar non-triggerable state)
            assert monitor.targets[0].state == "INVALID_STATE"

            mock_candle = Candle(timestamp=datetime.now(), high=105.0, low=95.0)
            candles = {"TEST_TICKER": mock_candle}
            monitor.evaluate(candles)

            # Should not emit alert because state != TARGET_ACTIVE
            mock_alert.assert_not_called()
    finally:
        os.remove(config_path)
