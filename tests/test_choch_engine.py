from decimal import Decimal

import choch_engine
import structural_engine as structural
from microstructure_engine import BreachMode, Candle
from minor_structure_engine import PullbackDirection


def c(cid, o, h, l, close):
    return Candle(cid, Decimal(o), Decimal(h), Decimal(l), Decimal(close))


def test_body_close_opposing_boundary_is_eligible_not_confirmed_without_gate():
    ref = choch_engine.reference_from_boundary(
        PullbackDirection.BULLISH, price=Decimal("10"), source_candle_id="protected"
    )
    result = choch_engine.detect_choch(
        (c("break", "10.2", "10.5", "9.5", "9.8"),),
        ref,
        confirmation_gate_open=False,
    )
    assert result.resolution is choch_engine.CHoCHResolution.CHOCH_ELIGIBLE
    assert result.structural_break is not None
    assert result.structural_break.mode is BreachMode.WICK_AND_BODY


def test_body_close_can_confirm_only_when_complete_gate_is_supplied():
    ref = choch_engine.reference_from_boundary(
        PullbackDirection.BEARISH, price=Decimal("20"), source_candle_id="protected"
    )
    result = choch_engine.detect_choch(
        (c("break", "19.8", "20.5", "19.5", "20.2"),),
        ref,
        confirmation_gate_open=True,
    )
    assert result.resolution is choch_engine.CHoCHResolution.CHOCH_CONFIRMED
    assert result.confirmed
    assert result.post_choch_regime is not None
    assert result.post_choch_regime.new_direction is PullbackDirection.BULLISH
    assert result.post_choch_regime.initial_active_impulse_candle_id == "break"
    assert result.post_choch_regime.confirmation_locked
    assert not result.post_choch_regime.ltf_context_cleared


def test_non_major_external_wick_can_enter_choch_gate():
    ref = choch_engine.reference_from_boundary(
        PullbackDirection.BULLISH, price=Decimal("10"), source_candle_id="protected"
    )
    result = choch_engine.detect_choch(
        (c("wick", "10.2", "10.4", "9.8", "10.1"),),
        ref,
        confirmation_gate_open=True,
        ltf_context_active=True,
    )
    assert result.resolution is choch_engine.CHoCHResolution.CHOCH_CONFIRMED
    assert result.post_choch_regime is not None
    assert result.post_choch_regime.ltf_context_cleared
    assert result.structural_break is not None
    assert result.structural_break.mode is BreachMode.WICK_ONLY


def test_major_idm_wick_is_major_idm_sweep_not_choch():
    idm = structural.IDMEvent(
        structural.IDMClass.MAJOR_IDM,
        structural.IDMOrigin.PULLBACK_DERIVED,
        PullbackDirection.BULLISH,
        Decimal("10"),
        "idm-source",
        "pb-ref",
        "pb-done",
    )
    ref = choch_engine.reference_from_ltf_idm(idm)
    result = choch_engine.detect_choch(
        (c("wick", "10.2", "10.4", "9.8", "10.1"),),
        ref,
        confirmation_gate_open=True,
    )
    assert result.resolution is choch_engine.CHoCHResolution.MAJOR_IDM_SWEEP
    assert not result.confirmed


def test_major_idm_body_close_enters_choch_gate():
    idm = structural.IDMEvent(
        structural.IDMClass.MAJOR_IDM,
        structural.IDMOrigin.PULLBACK_DERIVED,
        PullbackDirection.BULLISH,
        Decimal("10"),
        "idm-source",
        "pb-ref",
        "pb-done",
    )
    ref = choch_engine.reference_from_ltf_idm(idm)
    result = choch_engine.detect_choch(
        (c("body", "10.2", "10.3", "9.7", "9.8"),),
        ref,
        confirmation_gate_open=False,
    )
    assert result.resolution is choch_engine.CHoCHResolution.CHOCH_ELIGIBLE


def test_ltf_minor_idm_wick_requires_body_close():
    idm = structural.IDMEvent(
        structural.IDMClass.MINOR_IDM,
        structural.IDMOrigin.PULLBACK_DERIVED,
        PullbackDirection.BULLISH,
        Decimal("10"),
        "idm-source",
        "pb-ref",
        "pb-done",
    )
    ref = choch_engine.reference_from_ltf_idm(idm)
    result = choch_engine.detect_choch(
        (c("wick", "10.2", "10.4", "9.8", "10.1"),),
        ref,
        confirmation_gate_open=True,
    )
    assert result.resolution is choch_engine.CHoCHResolution.NO_BOUNDARY_BREAK


def test_equality_is_not_choch():
    ref = choch_engine.reference_from_boundary(
        PullbackDirection.BULLISH, price=Decimal("10"), source_candle_id="protected"
    )
    result = choch_engine.detect_choch(
        (c("equal", "10", "10.2", "10", "10.1"),),
        ref,
        confirmation_gate_open=True,
    )
    assert result.resolution is choch_engine.CHoCHResolution.NO_BOUNDARY_BREAK
    assert result.structural_break is None


def test_layer5_does_not_export_downstream_semantics():
    assert not hasattr(choch_engine, "POI")
    assert not hasattr(choch_engine, "RR")
    assert not hasattr(choch_engine, "TARGET")
    assert not hasattr(choch_engine, "BOS")

def test_protected_boundary_with_major_idm_provenance_wick_is_major_idm_sweep():
    ref = choch_engine.reference_from_boundary(
        PullbackDirection.BULLISH,
        price=Decimal("10"),
        source_candle_id="protected",
        idm_class=structural.IDMClass.MAJOR_IDM,
        idm_origin=structural.IDMOrigin.PROTECTED_EXTERNAL_BOUNDARY,
    )
    result = choch_engine.detect_choch(
        (c("wick", "10.2", "10.4", "9.8", "10.1"),),
        ref,
        confirmation_gate_open=True,
    )
    assert result.resolution is choch_engine.CHoCHResolution.MAJOR_IDM_SWEEP
