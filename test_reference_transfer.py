"""Phase 1 C2 contract tests: equality relationship and identity transfer."""
from SMC_mapper import ActiveExtremeReference, EngineState, transfer_equal_extreme_references


def test_equal_high_transfers_only_high_reference_identity():
    state = EngineState(
        active_high_reference=ActiveExtremeReference(15.0, 2, "ACTIVE_HIGH"),
        active_low_reference=ActiveExtremeReference(10.0, 2, "ACTIVE_LOW"),
    )
    eqh, eql = transfer_equal_extreme_references(
        state, {"high": 15.0, "low": 9.0}, 4
    )
    assert eqh is True
    assert eql is False
    assert state.active_high_reference.candle_id == 4
    assert state.active_high_reference.price_value == 15.0
    assert state.active_low_reference.candle_id == 2


def test_equal_high_and_opposite_low_breach_can_coexist():
    state = EngineState(
        active_high_reference=ActiveExtremeReference(15.0, 2, "ACTIVE_HIGH"),
        active_low_reference=ActiveExtremeReference(10.0, 2, "ACTIVE_LOW"),
    )
    eqh, eql = transfer_equal_extreme_references(
        state, {"high": 15.0, "low": 9.0}, 4
    )
    assert eqh is True
    assert eql is False
    assert state.active_high_reference.candle_id == 4
    assert state.active_low_reference.price_value == 10.0


def test_eql_transfers_only_low_reference_identity():
    state = EngineState(
        active_high_reference=ActiveExtremeReference(20.0, 2, "ACTIVE_HIGH"),
        active_low_reference=ActiveExtremeReference(10.0, 2, "ACTIVE_LOW"),
    )
    eqh, eql = transfer_equal_extreme_references(
        state, {"high": 21.0, "low": 10.0}, 5
    )
    assert eqh is False
    assert eql is True
    assert state.active_low_reference.candle_id == 5
    assert state.active_high_reference.candle_id == 2
