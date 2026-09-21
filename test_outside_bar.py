"""Phase 1 C3/C5 contract tests: Outside Bar geometry vs sequence evidence."""
from SMC_mapper import classify_outside_bar, run_true_smc


def candle(t, o, h, l, c):
    return {"time": t, "open": o, "high": h, "low": l, "close": c, "volume": 1000}


def setup_bull_genesis():
    return [
        candle("t-1", 10, 10, 10, 10),
        candle("t00", 8, 8, 5, 8),
        candle("t01", 8, 15, 11, 14),
        candle("t02", 14, 14, 12, 13),
    ]


def test_single_timeframe_outside_bar_is_geometric_only():
    bars = setup_bull_genesis()
    bars.append(candle("t04", 13, 20, 8, 16))
    state, _, _ = run_true_smc(bars, init_end_index=4)
    assert state.outside_bar is True
    assert state.intrabar_sequence_evidence == "UNAVAILABLE"
    assert state.outside_bar_reversal is None


def test_outside_bar_does_not_infer_low_first_or_high_first():
    bar = candle("t04", 13, 20, 8, 16)
    assert classify_outside_bar(bar, 15, 11) is True
