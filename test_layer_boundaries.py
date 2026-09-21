"""Phase 1 C4 boundary tests: Outside Bar is not an automatic reversal trigger."""
from SMC_mapper import EngineState, classify_outside_bar


def test_outside_bar_is_not_implicitly_reversal():
    state = EngineState()
    bar = {"open": 13, "high": 20, "low": 8, "close": 16}
    assert classify_outside_bar(bar, 15, 11) is True
    state.outside_bar = True
    assert state.outside_bar_reversal is None


def test_layer_one_outside_bar_state_has_no_reversal_authority():
    state = EngineState(outside_bar=True, outside_bar_reversal=None)
    assert state.outside_bar is True
    assert state.outside_bar_reversal is None
