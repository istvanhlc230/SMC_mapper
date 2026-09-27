from decimal import Decimal

import bos_engine
import structural_engine as structural
from microstructure_engine import BreachMode, Candle, QuarantineError
from minor_structure_engine import PullbackDirection


def c(cid, o, h, l, close):
    return Candle(cid, Decimal(o), Decimal(h), Decimal(l), Decimal(close))


def qualified_analysis(*, direction=PullbackDirection.BULLISH, qualified=True):
    idm = structural.IDMEvent(
        structural.IDMClass.MINOR_IDM, structural.IDMOrigin.PULLBACK_DERIVED,
        direction, Decimal("7"), "idm-source", "pb-ref", "pb-done", "idm-taken"
    )
    swing = structural.ConfirmedStructuralSwing(
        direction, Decimal("10"), "swing-source", "idm-source", "idm-taken"
    )
    q = structural.RetracementQualification(
        qualified, Decimal("0.50"), 3, False, False,
        "STANDARD_EQUILIBRIUM" if qualified else "INSUFFICIENT_CANDLE_STRUCTURE",
        "exec"
    )
    return structural.StructuralAnalysis(
        (idm,), (swing,), q, idm,
        structural.StructuralResolution.RETRACEMENT_QUALIFIED if qualified
        else structural.StructuralResolution.RETRACEMENT_INSUFFICIENT,
    )


def test_wick_break_is_valid_bos_when_layer3_is_qualified():
    candles = (
        c("idm-taken", "8", "9", "7", "8"),
        c("exec", "8", "9.5", "8", "9"),
        c("break", "9", "10.1", "8.8", "9.5"),
    )
    result = bos_engine.detect_bos(candles, qualified_analysis(), execution_start_candle_id="exec")
    assert result.resolution is bos_engine.BOSResolution.VALID_BOS
    assert result.structural_break is not None
    assert result.structural_break.mode is BreachMode.WICK_ONLY


def test_equality_is_not_bos():
    candles = (
        c("idm-taken", "8", "9", "7", "8"),
        c("exec", "8", "9.5", "8", "9"),
        c("equal", "9", "10", "8.8", "9.5"),
    )
    result = bos_engine.detect_bos(candles, qualified_analysis(), execution_start_candle_id="exec")
    assert result.resolution is bos_engine.BOSResolution.NO_STRUCTURAL_BREAK
    assert not result.valid_bos


def test_unqualified_external_break_is_not_valid_bos():
    candles = (
        c("idm-taken", "8", "9", "7", "8"),
        c("exec", "8", "9.5", "8", "9"),
        c("break", "9", "10.1", "8.8", "9.5"),
    )
    result = bos_engine.detect_bos(candles, qualified_analysis(qualified=False), execution_start_candle_id="exec")
    assert result.resolution is bos_engine.BOSResolution.IMPULSE_EXTENSION
    assert not result.valid_bos


def test_major_idm_boundary_is_not_promoted_to_structural_bos():
    active = structural.IDMEvent(
        structural.IDMClass.MAJOR_IDM, structural.IDMOrigin.PROTECTED_EXTERNAL_BOUNDARY,
        PullbackDirection.BULLISH, Decimal("10"), "protected", None, None, "boundary-taken"
    )
    analysis = structural.StructuralAnalysis(
        (active,), (), None, active, structural.StructuralResolution.IDM_ACTIVE
    )
    candles = (c("exec", "9", "10", "8", "9"), c("boundary-taken", "9", "10.1", "8", "9.5"))
    result = bos_engine.detect_bos(candles, analysis, execution_start_candle_id="exec")
    assert result.resolution is bos_engine.BOSResolution.MAJOR_IDM_SWEEP
    assert not result.valid_bos
    assert result.structural_break is None


def test_execution_start_must_match_layer3_qualification_end():
    candles = (
        c("idm-taken", "8", "9", "7", "8"),
        c("exec", "8", "9.5", "8", "9"),
        c("later", "9", "10.1", "8.8", "9.5"),
    )
    try:
        bos_engine.detect_bos(candles, qualified_analysis(), execution_start_candle_id="later")
    except QuarantineError:
        pass
    else:
        raise AssertionError("Layer-4 execution provenance must be explicit")


def test_layer4_does_not_export_downstream_semantics():
    assert not hasattr(bos_engine, "CHoCH")
    assert not hasattr(bos_engine, "POI")
    assert not hasattr(bos_engine, "RR")
    assert not hasattr(bos_engine, "TARGET")