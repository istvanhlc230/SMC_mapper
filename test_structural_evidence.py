import pytest
from dataclasses import replace

from structural_evidence import (
    StructuralEvidence,
    StructuralEvidenceError,
    validate_evidence,
)


def ev(i, typ, parents=(), candles=("c1",), state=None, payload=None,
       workflow="wf1", ts="2026-09-23T12:00:00+00:00"):
    states = {
        "MINOR_IDM": "ACTIVE",
        "CONFIRMED_STRUCTURAL_SWING": "ACTIVE",
        "PROTECTED_STRUCTURAL_EXTREME": "ACTIVE",
        "FALLBACK_MAJOR_IDM": "ACTIVE",
        "REAL_MAJOR_IDM": "ACTIVE",
        "TRADING_RANGE": "ACTIVE",
    }
    return StructuralEvidence(
        i, workflow, "EURUSD", "5m", ts, "structural-engine", "canonical-v1",
        typ, i, tuple(parents), tuple(candles),
        state if state is not None else states.get(typ),
        {"source": "upstream"}, payload or {},
    )


def base_chain():
    pb = ev("pb", "CANDLE_LEVEL_VALID_PULLBACK")
    vpe = ev("vpe", "VERIFIED_PULLBACK_EXTREME", ("pb",))
    svp = ev(
        "svp", "STRUCTURALLY_VALID_PULLBACK", ("vpe",),
        payload={
            "source_verified_pullback_extreme_id": "vpe",
            "qualification_evidence_id": "q",
            "active_impulsive_leg_id": "leg1",
            "retracement_depth": 0.382,
            "opposing_candle_count": 2,
        },
    )
    idm = ev(
        "idm", "MINOR_IDM", ("svp", "vpe"),
        payload={
            "source_svp_id": "svp",
            "source_verified_extreme_id": "vpe",
            "active_impulsive_leg_id": "leg1",
            "liquidity_extreme": 1.1,
        },
    )
    it = ev(
        "it", "IDM_TAKEN", ("idm",),
        payload={"idm_id": "idm", "interaction_type": "WICK", "event_identity": "evt-it"},
    )
    sw = ev(
        "sw", "CONFIRMED_STRUCTURAL_SWING", ("it",),
        payload={"source_idm_taken_id": "it", "expansion_extreme": 2.0, "direction": "BULLISH"},
    )
    br = ev(
        "br", "PHYSICAL_EXTERNAL_BREAK", ("sw",),
        payload={
            "boundary_id": "sw",
            "break_type": "WICK",
            "boundary_type": "CONFIRMED_STRUCTURAL_SWING",
        },
    )
    bos = ev(
        "bos", "VALID_BOS", ("sw", "it", "br", "svp"),
        payload={
            "confirmed_swing_id": "sw",
            "idm_taken_id": "it",
            "structural_break_id": "br",
            "stored_qualification_id": "svp",
            "retracement_depth": 0.382,
            "bos_gate_result": True,
        },
    )
    return [pb, vpe, svp, idm, it, sw, br, bos]


def protected_chain():
    chain = base_chain()
    return chain + [
        ev(
            "p", "PROTECTED_STRUCTURAL_EXTREME", ("bos",),
            payload={
                "source_valid_bos_id": "bos",
                "lock_event_id": "bos",
                "boundary_price": 1.0,
                "direction": "BULLISH",
            },
        )
    ]


def test_u01_missing_parent_rejected():
    with pytest.raises(StructuralEvidenceError, match="missing parent"):
        validate_evidence([ev("vpe", "VERIFIED_PULLBACK_EXTREME", ("missing",))])


def test_u02_unknown_type_rejected():
    with pytest.raises(StructuralEvidenceError, match="unsupported object_type"):
        validate_evidence([ev("x", "NOT_CANONICAL")])


def test_u03_missing_provenance_fields_rejected():
    chain = base_chain()
    bad = replace(chain[3], payload={})
    with pytest.raises(StructuralEvidenceError, match="missing payload"):
        validate_evidence(chain[:3] + [bad] + chain[4:])


def test_u04_parent_context_mismatch_rejected():
    p = ev("pb", "CANDLE_LEVEL_VALID_PULLBACK", workflow="wf2")
    c = ev("vpe", "VERIFIED_PULLBACK_EXTREME", ("pb",))
    with pytest.raises(StructuralEvidenceError, match="context mismatch"):
        validate_evidence([p, c])


def test_u05_svp_cannot_self_attest():
    with pytest.raises(StructuralEvidenceError, match="requires parent types"):
        validate_evidence([ev(
            "svp", "STRUCTURALLY_VALID_PULLBACK",
            payload={
                "source_verified_pullback_extreme_id": "x",
                "qualification_evidence_id": "q",
                "active_impulsive_leg_id": "l",
                "retracement_depth": 0.382,
                "opposing_candle_count": 2,
            },
        )])


def test_u06_svp_source_reference_must_exist():
    p = ev("pb", "CANDLE_LEVEL_VALID_PULLBACK")
    v = ev("vpe", "VERIFIED_PULLBACK_EXTREME", ("pb",))
    s = ev(
        "svp", "STRUCTURALLY_VALID_PULLBACK", ("vpe",),
        payload={
            "source_verified_pullback_extreme_id": "wrong",
            "qualification_evidence_id": "q",
            "active_impulsive_leg_id": "l",
            "retracement_depth": 0.382,
            "opposing_candle_count": 2,
        },
    )
    with pytest.raises(StructuralEvidenceError, match="does not reference supplied evidence"):
        validate_evidence([p, v, s])


def test_u07_idm_requires_svp_and_extreme():
    with pytest.raises(StructuralEvidenceError, match="requires parent types"):
        validate_evidence([ev(
            "idm", "MINOR_IDM",
            payload={
                "source_svp_id": "s",
                "source_verified_extreme_id": "x",
                "active_impulsive_leg_id": "l",
                "liquidity_extreme": 1.2,
            },
        )])


def test_u08_idm_taken_requires_idm():
    with pytest.raises(StructuralEvidenceError, match="requires parent types"):
        validate_evidence([ev(
            "it", "IDM_TAKEN",
            payload={"idm_id": "idm", "interaction_type": "WICK", "event_identity": "e"},
        )])


def test_u09_swing_requires_idm_taken():
    with pytest.raises(StructuralEvidenceError, match="requires parent types"):
        validate_evidence([ev(
            "s", "CONFIRMED_STRUCTURAL_SWING",
            payload={"source_idm_taken_id": "t", "expansion_extreme": 2, "direction": "BULLISH"},
        )])


def test_u10_protected_requires_bos():
    with pytest.raises(StructuralEvidenceError, match="requires parent types"):
        validate_evidence([ev(
            "p", "PROTECTED_STRUCTURAL_EXTREME",
            payload={"source_valid_bos_id": "b", "lock_event_id": "b",
                     "boundary_price": 1, "direction": "BULLISH"},
        )])


def test_u11_bos_requires_complete_parent_graph():
    chain = base_chain()
    bad = replace(chain[-1], parent_evidence_ids=("sw", "it", "br"))
    with pytest.raises(StructuralEvidenceError, match="requires parent types"):
        validate_evidence(chain[:-1] + [bad])


def test_u12_bos_requires_depth_382():
    chain = base_chain()
    bad = replace(chain[-1], payload={**chain[-1].payload, "retracement_depth": 0.381})
    with pytest.raises(StructuralEvidenceError, match="retracement_depth"):
        validate_evidence(chain[:-1] + [bad])


def test_u13_fallback_and_real_major_idm_are_distinct():
    chain = protected_chain()
    fb = ev(
        "fb", "FALLBACK_MAJOR_IDM", ("p",),
        payload={"boundary_id": "p", "provenance_role": "FALLBACK_MAJOR_IDM"},
    )
    real = ev(
        "real", "REAL_MAJOR_IDM", ("svp", "vpe"),
        payload={
            "source_svp_id": "svp",
            "source_verified_extreme_id": "vpe",
            "provenance_role": "REAL_MAJOR_IDM",
        },
    )
    sweep = ev(
        "sweep", "MAJOR_IDM_SWEEP", ("fb", "real"),
        payload={"fallback_major_idm_id": "fb", "sweep_type": "WICK"},
    )
    with pytest.raises(StructuralEvidenceError, match="fallback lineage"):
        validate_evidence(chain + [fb, real, sweep])


def test_u14_fallback_wick_is_not_choch_confirmation():
    chain = protected_chain()
    fb = ev(
        "fb", "FALLBACK_MAJOR_IDM", ("p",),
        payload={"boundary_id": "p", "provenance_role": "FALLBACK_MAJOR_IDM"},
    )
    sweep = ev(
        "sweep", "MAJOR_IDM_SWEEP", ("fb",),
        payload={"fallback_major_idm_id": "fb", "sweep_type": "WICK"},
    )
    assert validate_evidence(chain + [fb, sweep])[-1].object_type == "MAJOR_IDM_SWEEP"


def test_u15_choch_requires_protected_boundary():
    with pytest.raises(StructuralEvidenceError, match="requires parent types"):
        validate_evidence([ev(
            "ce", "CHoCH_ELIGIBLE",
            payload={
                "protected_opposing_boundary_id": "p",
                "physical_break_id": "b",
                "classification": "BODY",
            },
        )])


def test_u16_choch_wick_requires_explicit_real_major_idm_lineage():
    chain = protected_chain()
    br = ev(
        "oppbr", "PHYSICAL_EXTERNAL_BREAK", ("p",),
        payload={
            "boundary_id": "p",
            "break_type": "WICK",
            "boundary_type": "PROTECTED_STRUCTURAL_EXTREME",
        },
    )
    eligible = ev(
        "ce", "CHoCH_ELIGIBLE", ("p", "oppbr"),
        payload={
            "protected_opposing_boundary_id": "p",
            "physical_break_id": "oppbr",
            "classification": "WICK",
        },
    )
    with pytest.raises(StructuralEvidenceError, match="REAL_MAJOR_IDM lineage"):
        validate_evidence(chain + [br, eligible])


def test_u17_later_parent_event_cannot_precede_child():
    p = ev("pb", "CANDLE_LEVEL_VALID_PULLBACK", ts="2026-09-23T12:01:00+00:00")
    c = ev("vpe", "VERIFIED_PULLBACK_EXTREME", ("pb",), ts="2026-09-23T12:00:00+00:00")
    with pytest.raises(StructuralEvidenceError, match="occurs after child"):
        validate_evidence([p, c])


def test_u18_duplicate_event_id_rejected():
    a = ev("x", "CANDLE_LEVEL_VALID_PULLBACK")
    b = ev("x", "CANDLE_LEVEL_VALID_PULLBACK")
    with pytest.raises(StructuralEvidenceError, match="duplicate evidence_id"):
        validate_evidence([a, b])


def test_u19_naive_timestamp_rejected():
    with pytest.raises(StructuralEvidenceError, match="timezone-aware"):
        validate_evidence([ev(
            "x", "CANDLE_LEVEL_VALID_PULLBACK", ts="2026-09-23T12:00:00"
        )])


def test_u20_complete_evidence_graph_accepted():
    assert len(validate_evidence(base_chain())) == 8
