import sys
import os
import subprocess
import pytest
from unittest.mock import patch
from typing import List

import SMC_mapper as eng
from data_provider import ProviderConfig, DataRequest


@pytest.fixture(autouse=True)
def restore_globals():
    saved = {
        'INTERVAL': eng.INTERVAL,
        'BAR_COUNT': eng.BAR_COUNT,
        'HISTORY_SIZE': eng.HISTORY_SIZE,
        'DEBUG': eng.DEBUG,
        'BOS_MIN_RETRACEMENT_PCT': eng.BOS_MIN_RETRACEMENT_PCT,
        'EQUAL_LEVEL_TOLERANCE': eng.EQUAL_LEVEL_TOLERANCE,
    }
    yield
    for k, v in saved.items():
        setattr(eng, k, v)


def _make_candles():
    return [
        {'time': 't-1', 'open': 10, 'high': 10, 'low': 10, 'close': 10, 'volume': 1000},
        {'time': 't00', 'open': 8,  'high': 8,  'low': 5,  'close': 8,  'volume': 1000},
        {'time': 't01', 'open': 8,  'high': 15, 'low': 11, 'close': 14, 'volume': 1000},
        {'time': 't02', 'open': 14, 'high': 14, 'low': 12, 'close': 13, 'volume': 1000},
        {'time': 't04', 'open': 11, 'high': 11, 'low': 9,  'close': 10, 'volume': 1000},
        {'time': 't05', 'open': 10, 'high': 16, 'low': 10, 'close': 16, 'volume': 1000},
        {'time': 't06', 'open': 15, 'high': 15, 'low': 8,  'close': 10, 'volume': 1000},
        {'time': 't07', 'open': 10, 'high': 20, 'low': 10, 'close': 20, 'volume': 1000},
    ]


_WORKSPACE = os.path.dirname(os.path.abspath(eng.__file__))
_MOCK_PROVIDER = ProviderConfig(name='demo', api_key='demo')


def test_symbol_is_required():
    result = subprocess.run(
        [sys.executable, 'SMC_mapper.py'],
        capture_output=True, text=True, cwd=_WORKSPACE,
    )
    assert result.returncode == 2, f'Expected 2 got {result.returncode}: {result.stderr}'


def test_symbol_is_authoritative():
    candles = _make_candles()
    with patch('SMC_mapper.auto_detect_provider', return_value=_MOCK_PROVIDER), \
         patch('SMC_mapper.fetch_candles', return_value=candles) as mock_fetch, \
         patch('sys.argv', ['SMC_mapper.py', 'TSLA']):
        eng.main()
    assert mock_fetch.call_count == 1
    req_arg = mock_fetch.call_args[0][1]
    assert isinstance(req_arg, DataRequest)
    assert req_arg.symbol == 'TSLA'


def test_interval_option():
    candles = _make_candles()
    with patch('SMC_mapper.auto_detect_provider', return_value=_MOCK_PROVIDER), \
         patch('SMC_mapper.fetch_candles', return_value=candles), \
         patch('sys.argv', ['SMC_mapper.py', 'AAPL', '--interval', '15min']):
        eng.main()
    assert eng.INTERVAL == '15min'


def test_bars_option():
    candles = _make_candles()
    with patch('SMC_mapper.auto_detect_provider', return_value=_MOCK_PROVIDER), \
         patch('SMC_mapper.fetch_candles', return_value=candles) as mock_fetch, \
         patch('sys.argv', ['SMC_mapper.py', 'AAPL', '--bars', '500']):
        eng.main()
    req_arg = mock_fetch.call_args[0][1]
    assert req_arg.bar_count == 500
    assert eng.BAR_COUNT == 500


def test_history_option():
    candles = _make_candles()
    with patch('SMC_mapper.auto_detect_provider', return_value=_MOCK_PROVIDER), \
         patch('SMC_mapper.fetch_candles', return_value=candles), \
         patch('sys.argv', ['SMC_mapper.py', 'AAPL', '--history', '50']):
        eng.main()
    assert eng.HISTORY_SIZE == 50


def test_debug_option():
    candles = _make_candles()
    with patch('SMC_mapper.auto_detect_provider', return_value=_MOCK_PROVIDER), \
         patch('SMC_mapper.fetch_candles', return_value=candles), \
         patch('sys.argv', ['SMC_mapper.py', 'AAPL', '--no-debug']):
        eng.main()
    assert eng.DEBUG is False

    with patch('SMC_mapper.auto_detect_provider', return_value=_MOCK_PROVIDER), \
         patch('SMC_mapper.fetch_candles', return_value=candles), \
         patch('sys.argv', ['SMC_mapper.py', 'AAPL', '--debug']):
        eng.main()
    assert eng.DEBUG is True


def test_provider_option():
    candles = _make_candles()
    with patch('SMC_mapper.auto_detect_provider', return_value=_MOCK_PROVIDER) as mock_detect, \
         patch('SMC_mapper.fetch_candles', return_value=candles), \
         patch('sys.argv', ['SMC_mapper.py', 'AAPL', '--provider', 'demo']):
        eng.main()
    args, kwargs = mock_detect.call_args
    preferred_value = kwargs.get('preferred') if kwargs else (args[0] if args else None)
    assert preferred_value == 'demo'


def test_defaults_match_config_json():
    parser = eng.build_arg_parser()
    defaults = parser.parse_args(['AAPL'])
    assert defaults.interval == '5min'
    assert defaults.bars == 1000
    assert defaults.history == 20
    assert defaults.debug is True
    assert defaults.provider == 'twelvedata'


def test_works_without_config_json():
    assert eng is not None
    assert hasattr(eng, 'run_true_smc')
    assert hasattr(eng, 'build_arg_parser')
    candles = _make_candles()
    try:
        state, _, _ = eng.run_true_smc(candles, init_end_index=4)
    except FileNotFoundError as e:
        pytest.fail(f'run_true_smc raised FileNotFoundError: {e}')


def test_only_requested_symbol_analyzed():
    candles = _make_candles()
    with patch('SMC_mapper.auto_detect_provider', return_value=_MOCK_PROVIDER), \
         patch('SMC_mapper.fetch_candles', return_value=candles) as mock_fetch, \
         patch('sys.argv', ['SMC_mapper.py', 'NVDA']):
        eng.main()
    assert mock_fetch.call_count == 1
    req = mock_fetch.call_args[0][1]
    assert req.symbol == 'NVDA'


def test_existing_scanner_behavior_preserved():
    candles = [
        {'time': 't-1', 'open': 10, 'high': 10, 'low': 10, 'close': 10, 'volume': 1000},
        {'time': 't00', 'open': 8,  'high': 8,  'low': 5,  'close': 8,  'volume': 1000},
        {'time': 't01', 'open': 8,  'high': 15, 'low': 11, 'close': 14, 'volume': 1000},
        {'time': 't02', 'open': 14, 'high': 14, 'low': 12, 'close': 13, 'volume': 1000},
        {'time': 't04', 'open': 13, 'high': 13, 'low': 10, 'close': 10, 'volume': 1000},
        {'time': 't05', 'open': 10, 'high': 10, 'low': 9,  'close': 9,  'volume': 1000},
        {'time': 't06', 'open': 9,  'high': 9,  'low': 8,  'close': 8,  'volume': 1000},
        {'time': 't07', 'open': 8,  'high': 16, 'low': 8,  'close': 16, 'volume': 1000},
        {'time': 't08', 'open': 16, 'high': 16, 'low': 7,  'close': 10, 'volume': 1000},
        {'time': 't09', 'open': 10, 'high': 20, 'low': 10, 'close': 20, 'volume': 1000},
    ]
    state, _, _ = eng.run_true_smc(candles, init_end_index=4)
    assert state is not None
    bos_events = [e for e in state.structure_history if e.event == 'BOS']
    assert len(bos_events) == 1, f'Expected 1 BOS, got {len(bos_events)}'
    assert bos_events[0].direction == 'BULLISH'
    assert bos_events[0].break_price == 20
    assert bos_events[0].idm_swept is True
    assert state.protected_low is not None
    assert state.range_has_bos is True
    assert state.trend == 'BULLISH'


def test_main_works_without_config_json(monkeypatch):
    """Verify main() executes end-to-end when config.json is absent."""
    real_isfile = os.path.isfile
    monkeypatch.setattr(os.path, 'isfile', lambda p: False if 'config.json' in str(p) else real_isfile(p))
    candles = _make_candles()
    with patch('SMC_mapper.fetch_candles', return_value=candles) as mock_fetch, \
         patch('sys.argv', ['SMC_mapper.py', 'SPY']):
        eng.main()
    assert mock_fetch.call_count == 1
    req = mock_fetch.call_args[0][1]
    assert req.symbol == 'SPY'


def test_main_all_cli_options_combined():
    """Verify all optional arguments passed together are correctly parsed and applied."""
    candles = _make_candles()
    with patch('SMC_mapper.auto_detect_provider', return_value=_MOCK_PROVIDER) as mock_detect, \
         patch('SMC_mapper.fetch_candles', return_value=candles) as mock_fetch, \
         patch('sys.argv', ['SMC_mapper.py', 'AMD', '--interval', '1h', '--bars', '250', '--history', '15', '--no-debug', '--provider', 'demo']):
        eng.main()

    assert eng.INTERVAL == '1h'
    assert eng.BAR_COUNT == 250
    assert eng.HISTORY_SIZE == 15
    assert eng.DEBUG is False
    args, kwargs = mock_detect.call_args
    preferred = kwargs.get('preferred') if kwargs else (args[0] if args else None)
    assert preferred == 'demo'
    req = mock_fetch.call_args[0][1]
    assert req.symbol == 'AMD'
    assert req.interval == '1h'
    assert req.bar_count == 250


def test_main_provider_error_handled():
    """Verify that auto_detect_provider failure does not crash the CLI with an unhandled exception."""
    with patch('SMC_mapper.auto_detect_provider', side_effect=RuntimeError("Provider missing")), \
         patch('sys.argv', ['SMC_mapper.py', 'AAPL']):
        eng.main()


def test_main_fetch_exception_handled():
    """Verify that fetch errors produce a clean error result instead of unhandled crash."""
    with patch('SMC_mapper.auto_detect_provider', return_value=_MOCK_PROVIDER), \
         patch('SMC_mapper.fetch_candles', side_effect=RuntimeError("API timeout")), \
         patch('sys.argv', ['SMC_mapper.py', 'AAPL']):
        eng.main()


def test_main_insufficient_structure_handled():
    """Verify that insufficient structure produces an error result cleanly."""
    with patch('SMC_mapper.auto_detect_provider', return_value=_MOCK_PROVIDER), \
         patch('SMC_mapper.fetch_candles', return_value=[]), \
         patch('SMC_mapper.run_true_smc', return_value=(None, None, None)), \
         patch('sys.argv', ['SMC_mapper.py', 'AAPL']):
        eng.main()


def test_main_subprocess_demo_end_to_end():
    """Verify full CLI run as a real subprocess without mocks using the demo provider."""
    result = subprocess.run(
        [sys.executable, 'SMC_mapper.py', 'NVDA', '--provider', 'demo', '--bars', '50'],
        capture_output=True, text=True, cwd=_WORKSPACE,
    )
    assert result.returncode == 0, f"Process failed: {result.stderr}"
    assert "Provider: demo" in result.stdout
    assert "Symbol: NVDA" in result.stdout
    assert "TRUE SMC MAPPER" in result.stdout
    assert "SCAN COMPLETE" in result.stdout


