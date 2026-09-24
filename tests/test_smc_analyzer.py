import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from smc_analyzer import (
    MarketDataNormalizer, 
    DataNormalizationError, 
    InsufficientHistoryError,
    IntrabarSequenceEvidence
)

def make_dummy_data(count, start_time=None, incomplete_last=False):
    if start_time is None:
        start_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    
    data = []
    for i in range(count):
        data.append({
            'timestamp': start_time + timedelta(hours=i),
            'open': '1.1000',
            'high': '1.1050',
            'low': '1.0950',
            'close': '1.1020',
            'is_completed': True
        })
        
    if incomplete_last and count > 0:
        data[-1]['is_completed'] = False
        
    return data

def test_decimal_determinism_and_normalization():
    raw = make_dummy_data(15)
    candles = MarketDataNormalizer.normalize(raw)
    
    assert len(candles) == 15
    # Assert exact decimal conversion
    assert isinstance(candles[0].open, Decimal)
    assert candles[0].open == Decimal("1.1000")
    assert candles[0].intrabar_sequence_evidence == IntrabarSequenceEvidence.UNAVAILABLE
    assert candles[0].index == 0
    assert candles[-1].index == 14

def test_timezone_rejection():
    raw = make_dummy_data(15)
    # Strip timezone
    raw[0]['timestamp'] = raw[0]['timestamp'].replace(tzinfo=None)
    
    with pytest.raises(DataNormalizationError, match="must be timezone-aware"):
        MarketDataNormalizer.normalize(raw)

def test_duplicate_timestamps_halt():
    raw = make_dummy_data(15)
    raw[5]['timestamp'] = raw[4]['timestamp']
    
    with pytest.raises(DataNormalizationError, match="Duplicate timestamp detected"):
        MarketDataNormalizer.normalize(raw)

def test_out_of_order_timestamps_halt():
    raw = make_dummy_data(15)
    raw[5]['timestamp'] = raw[4]['timestamp'] - timedelta(hours=1)
    
    with pytest.raises(DataNormalizationError, match="strictly ordered"):
        MarketDataNormalizer.normalize(raw)

def test_invalid_ohlc_halt():
    raw = make_dummy_data(15)
    raw[5]['low'] = '1.2000' # low > high
    
    with pytest.raises(DataNormalizationError, match="Invalid OHLC"):
        MarketDataNormalizer.normalize(raw)

def test_incomplete_candle_exclusion():
    raw = make_dummy_data(15, incomplete_last=True)
    candles = MarketDataNormalizer.normalize(raw)
    
    assert len(candles) == 14
    assert candles[-1].index == 13
    assert candles[-1].timestamp == raw[13]['timestamp']

def test_missing_is_completed_halts():
    raw = make_dummy_data(15)
    del raw[5]['is_completed']
    with pytest.raises(DataNormalizationError, match="Missing 'is_completed' status"):
        MarketDataNormalizer.normalize(raw)

def test_non_boolean_is_completed_halts():
    raw = make_dummy_data(15)
    raw[5]['is_completed'] = "True"
    with pytest.raises(DataNormalizationError, match="'is_completed' must be a boolean"):
        MarketDataNormalizer.normalize(raw)

def test_detection_event_enum():
    from smc_analyzer import DetectionEvent
    # Ensure exactly 7 canonical event classes exist
    assert len(DetectionEvent) == 7
    expected_names = {
        "NO_EVENT_INTERNAL_PB",
        "MINOR_IDM_EVENT",
        "EXT_CONT_BREAK",
        "EXT_OPP_BREAK",
        "FALLBACK_EVENT",
        "REAL_MAJOR_IDM_EVENT",
        "NEW_SVP_QUALIFIED"
    }
    actual_names = {e.name for e in DetectionEvent}
    assert actual_names == expected_names

def test_float_input_conversion():
    raw = make_dummy_data(15)
    # Provide float instead of string to test deterministic string conversion internally
    raw[0]['open'] = 1.1000
    candles = MarketDataNormalizer.normalize(raw)
    assert candles[0].open == Decimal("1.1")

