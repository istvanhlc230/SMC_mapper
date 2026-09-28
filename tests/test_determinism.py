import pytest
from smc_analyzer import (
    determine_next_state, LifecycleState, DetectionEvent, ProcessCondition,
    FirstBOSRetracementBaselineStatus, ClassificationOutcome
)

def test_determinism_bootstrap():
    # IDM_TAKEN -> CONFIRMATION_LOCKED
    state, outcome = determine_next_state(
        LifecycleState.BOOTSTRAP,
        DetectionEvent.NO_EVENT_INTERNAL_PB,
        [ProcessCondition.IDM_TAKEN],
        FirstBOSRetracementBaselineStatus.UNSPECIFIED_CANONICAL_INPUT,
        False
    )
    assert state == LifecycleState.CONFIRMATION_LOCKED
    
    # Not IDM_TAKEN -> BOOTSTRAP
    state, outcome = determine_next_state(
        LifecycleState.BOOTSTRAP,
        DetectionEvent.MINOR_IDM_EVENT,
        [],
        FirstBOSRetracementBaselineStatus.UNSPECIFIED_CANONICAL_INPUT,
        False
    )
    assert state == LifecycleState.BOOTSTRAP

def test_determinism_confirmation_locked():
    # EXT_CONT_BREAK + GATE LOCKED -> DISQUALIFIED (REMAIN)
    state, outcome = determine_next_state(
        LifecycleState.CONFIRMATION_LOCKED,
        DetectionEvent.EXT_CONT_BREAK,
        [],
        FirstBOSRetracementBaselineStatus.AVAILABLE,
        True
    )
    assert state == LifecycleState.CONFIRMATION_LOCKED
    assert outcome is None # DISQUALIFIED is implicit

    # EXT_CONT_BREAK + GATE UNLOCKED + FIRST BOS UNSPECIFIED -> FIRST_BOS_RETRACEMENT_UNRESOLVED
    state, outcome = determine_next_state(
        LifecycleState.CONFIRMATION_LOCKED,
        DetectionEvent.EXT_CONT_BREAK,
        [ProcessCondition.CONFIRMATION_GATE_UNLOCKED],
        FirstBOSRetracementBaselineStatus.UNSPECIFIED_CANONICAL_INPUT,
        True
    )
    assert state == LifecycleState.CONFIRMATION_LOCKED
    assert outcome == ClassificationOutcome.FIRST_BOS_RETRACEMENT_UNRESOLVED

    # EXT_CONT_BREAK + GATE UNLOCKED + QUALIFIED -> VALID_BOS -> POST_BOS
    state, outcome = determine_next_state(
        LifecycleState.CONFIRMATION_LOCKED,
        DetectionEvent.EXT_CONT_BREAK,
        [ProcessCondition.CONFIRMATION_GATE_UNLOCKED],
        FirstBOSRetracementBaselineStatus.AVAILABLE,
        True
    )
    assert state == LifecycleState.POST_BOS
    assert outcome == ClassificationOutcome.VALID_BOS

    # EXT_CONT_BREAK + GATE UNLOCKED + NOT QUALIFIED -> IMPULSE_EXTENSION
    state, outcome = determine_next_state(
        LifecycleState.CONFIRMATION_LOCKED,
        DetectionEvent.EXT_CONT_BREAK,
        [ProcessCondition.CONFIRMATION_GATE_UNLOCKED],
        FirstBOSRetracementBaselineStatus.AVAILABLE,
        False
    )
    assert state == LifecycleState.CONFIRMATION_LOCKED
    assert outcome == ClassificationOutcome.IMPULSE_EXTENSION

def test_determinism_confirmed_range():
    # EXT_CONT_BREAK + QUALIFIED -> VALID_BOS
    state, outcome = determine_next_state(
        LifecycleState.CONFIRMED_RANGE,
        DetectionEvent.EXT_CONT_BREAK,
        [],
        FirstBOSRetracementBaselineStatus.AVAILABLE,
        True
    )
    assert state == LifecycleState.POST_BOS
    assert outcome == ClassificationOutcome.VALID_BOS

    # EXT_CONT_BREAK + NOT QUALIFIED -> IMPULSE_EXTENSION
    state, outcome = determine_next_state(
        LifecycleState.CONFIRMED_RANGE,
        DetectionEvent.EXT_CONT_BREAK,
        [],
        FirstBOSRetracementBaselineStatus.AVAILABLE,
        False
    )
    assert state == LifecycleState.CONFIRMED_RANGE
    assert outcome == ClassificationOutcome.IMPULSE_EXTENSION

    # EXT_OPP_BREAK -> POST_CHOCH
    state, outcome = determine_next_state(
        LifecycleState.CONFIRMED_RANGE,
        DetectionEvent.EXT_OPP_BREAK,
        [],
        FirstBOSRetracementBaselineStatus.AVAILABLE,
        False,
        is_choch_confirmed=True
    )
    assert state == LifecycleState.POST_CHOCH
    assert outcome == ClassificationOutcome.CHoCH_CONFIRMED

def test_determinism_post_choch():
    # EXT_CONT_BREAK + GATE UNLOCKED + FIRST BOS UNSPECIFIED -> FIRST_BOS_RETRACEMENT_UNRESOLVED
    state, outcome = determine_next_state(
        LifecycleState.POST_CHOCH,
        DetectionEvent.EXT_CONT_BREAK,
        [ProcessCondition.CONFIRMATION_GATE_UNLOCKED],
        FirstBOSRetracementBaselineStatus.UNSPECIFIED_CANONICAL_INPUT,
        True
    )
    assert state == LifecycleState.POST_CHOCH
    assert outcome == ClassificationOutcome.FIRST_BOS_RETRACEMENT_UNRESOLVED
