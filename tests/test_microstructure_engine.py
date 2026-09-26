from decimal import Decimal
import dataclasses
import inspect

import microstructure_engine as m


def c(i, o, h, l, cl):
    return m.Candle(i, Decimal(o), Decimal(h), Decimal(l), Decimal(cl))


def test_decimal_strict_and_finite():
    x = c("c1", "1", "2", "0", "1.5")
    assert all(isinstance(getattr(x, n), Decimal) for n in ("open", "high", "low", "close"))
    for bad in (float("nan"), float("inf"), float("-inf")):
        try:
            m.Candle("bad", bad, bad, bad, bad)
        except m.QuarantineError:
            pass
        else:
            raise AssertionError("non-finite float accepted")


def test_equality_is_not_break():
    candle = c("c2", "6", "10", "5", "9")
    ref = m.ExtremeReference(Decimal("10"), "c1", "H")
    obs = m.classify_breach(candle, ref, m.Direction.UP)
    assert obs.mode is m.BreachMode.EQUAL
    assert obs.is_break is False


def test_breach_taxonomy_and_no_intrabar_inference():
    ref = m.ExtremeReference(Decimal("10"), "r", "H")
    wick = m.classify_breach(c("w", "9", "11", "8", "9.5"), ref, m.Direction.UP)
    body = m.classify_breach(c("b", "10.5", "11", "8", "10"), ref, m.Direction.UP)
    close = m.classify_breach(c("x", "11", "12", "9", "11"), ref, m.Direction.UP)
    assert wick.mode is m.BreachMode.WICK_ONLY
    assert body.mode is m.BreachMode.BODY
    assert close.mode is m.BreachMode.CLOSE
    assert wick.physical and not wick.body and not wick.close
    assert body.physical and body.body and not body.close
    assert close.physical and close.body and close.close


def test_inside_bar_is_strict():
    mother = c("m", "5", "10", "1", "6")
    assert m.inside_bar(c("i", "5", "9", "2", "6"), mother).mother_candle_id == "m"
    assert m.is_inside_bar(c("i", "5", "9", "2", "6"), mother)
    assert not m.is_inside_bar(c("eq", "5", "10", "2", "6"), mother)
    assert not m.is_inside_bar(c("eq2", "5", "9", "1", "6"), mother)


def test_outside_bar_geometry_and_unavailable_sequence():
    reference = c("r", "5", "10", "2", "6")
    ob = m.outside_bar(c("o", "6", "12", "1", "7"), reference)
    assert ob is not None
    assert ob.sequence_evidence.status is m.SequenceStatus.UNAVAILABLE
    assert ob.sequence_evidence.sequence == ()
    assert ob.candle_id == "o"
    assert ob.high_breach.candle_id == "o"
    assert ob.low_breach.candle_id == "o"


def test_outside_bar_does_not_accept_fabricated_unavailable_sequence():
    try:
        m.SequenceEvidence(m.SequenceStatus.UNAVAILABLE, ("LOW", "HIGH"))
    except m.QuarantineError:
        pass
    else:
        raise AssertionError("fabricated sequence accepted")


def test_equal_reference_transfer_is_independent():
    high = m.ExtremeReference(Decimal("10"), "h1", "ACTIVE_HIGH")
    low = m.ExtremeReference(Decimal("2"), "l1", "ACTIVE_LOW")
    candle = c("c", "5", "10", "2", "6")
    new_high = m.transfer_high_reference(high, candle)
    new_low = m.transfer_low_reference(low, candle)
    assert new_high.candle_id == "c"
    assert new_low.candle_id == "c"
    other = c("d", "5", "10", "3", "6")
    assert m.transfer_low_reference(low, other).candle_id == "l1"


def test_eqh_eql_are_exact():
    a = c("a", "5", "10.0", "2.0", "6")
    b = c("b", "5", "10.00", "2.00", "7")
    assert m.equal_high(a, b).kind == "EQH"
    assert m.equal_low(a, b).kind == "EQL"
    c2 = c("c", "5", "10.0001", "2", "7")
    assert m.equal_high(a, c2) is None


def test_evidence_id_is_content_addressed_and_immutable():
    e1 = m.EvidenceEnvelope("OUTSIDE_BAR", ("c1", "c2"), (("high", "2"), ("low", "1")))
    e2 = m.EvidenceEnvelope("OUTSIDE_BAR", ("c1", "c2"), (("low", "1"), ("high", "2")))
    e3 = m.EvidenceEnvelope("OUTSIDE_BAR", ("c1", "c3"), (("high", "2"), ("low", "1")))
    assert e1.evidence_id == e2.evidence_id
    assert e1.evidence_id != e3.evidence_id
    assert dataclasses.is_dataclass(e1)
    try:
        e1.payload += (("x", "y"),)
    except (dataclasses.FrozenInstanceError, AttributeError):
        pass
    else:
        raise AssertionError("immutable envelope mutated")


def test_invalid_candle_is_quarantined():
    for args in [
        ("bad", "1", "0", "2", "1"),
        ("bad", "1", "2", "0", "3"),
    ]:
        try:
            c(*args)
        except m.QuarantineError:
            pass
        else:
            raise AssertionError("invalid candle accepted")


def test_trend_is_only_candle_level():
    p = c("p", "5", "10", "2", "9")
    u = c("u", "9", "11", "2", "10")
    d = c("d", "9", "10", "1", "8")
    assert m.candle_trend(p, u).direction is m.TrendDirection.BULLISH
    assert m.candle_trend(p, d).direction is m.TrendDirection.BEARISH


def test_hermetic_ast_has_no_layer2_plus_symbols():
    violations = m.validate_hermetic_layer1(inspect.getsource(m))
    assert violations == ()
