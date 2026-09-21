"""Phase 1 C1 contract tests: deterministic candle-extreme breach taxonomy."""
from SMC_mapper import classify_candle_extreme_breach


def candle(o, h, l, c):
    return {"open": o, "high": h, "low": l, "close": c}


def test_wick_only_high_breach():
    r = classify_candle_extreme_breach(candle(14, 16, 13, 14), 15, 10)
    assert r["PHYSICAL_BREACH"]
    assert r["WICK_ONLY_BREACH"]
    assert not r["BODY_BREACH"]
    assert not r["CLOSE_BREACH"]


def test_body_breach_with_open_above_reference_close_at_reference():
    r = classify_candle_extreme_breach(candle(16, 17, 12, 15), 15, 10)
    assert r["PHYSICAL_BREACH"]
    assert not r["WICK_ONLY_BREACH"]
    assert r["BODY_BREACH"]
    assert not r["CLOSE_BREACH"]
    assert not r["PROVEN_INTRABAR_CROSSING"]


def test_close_breach_is_body_and_physical_breach():
    r = classify_candle_extreme_breach(candle(14, 17, 12, 16), 15, 10)
    assert r["CLOSE_BREACH"]
    assert r["BODY_BREACH"]
    assert r["PHYSICAL_BREACH"]


def test_exact_equality_is_not_a_physical_breach():
    r = classify_candle_extreme_breach(candle(14, 15, 10, 14), 15, 10)
    assert not r["PHYSICAL_BREACH"]
    assert not r["WICK_ONLY_BREACH"]
    assert not r["BODY_BREACH"]
    assert not r["CLOSE_BREACH"]


def test_gap_body_breach_does_not_prove_intrabar_crossing():
    r = classify_candle_extreme_breach(candle(16, 17, 16, 17), 15, 10)
    assert r["BODY_BREACH"]
    assert r["PHYSICAL_BREACH"]
    assert not r["PROVEN_INTRABAR_CROSSING"]
