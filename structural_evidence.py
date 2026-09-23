from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import math
from typing import Any, Iterable, Mapping

OBJECT_TYPES = frozenset({
    "CANDLE_LEVEL_VALID_PULLBACK", "VERIFIED_PULLBACK_EXTREME",
    "STRUCTURALLY_VALID_PULLBACK", "MINOR_IDM", "IDM_TAKEN",
    "CONFIRMED_STRUCTURAL_SWING", "PHYSICAL_EXTERNAL_BREAK", "VALID_BOS",
    "PROTECTED_STRUCTURAL_EXTREME", "TRADING_RANGE", "CHoCH_ELIGIBLE",
    "CHoCH_CONFIRMED", "FALLBACK_MAJOR_IDM", "REAL_MAJOR_IDM",
    "MAJOR_IDM_SWEEP",
})
EVENT_TYPES = frozenset({
    "IDM_TAKEN", "PHYSICAL_EXTERNAL_BREAK", "VALID_BOS",
    "CHoCH_ELIGIBLE", "CHoCH_CONFIRMED", "MAJOR_IDM_SWEEP",
})
ALLOWED_STATES = {
    "MINOR_IDM": {"ACTIVE", "SWEPT", "SUPERSEDED", "HISTORICAL"},
    "FALLBACK_MAJOR_IDM": {"ACTIVE", "SWEPT", "SUPERSEDED", "HISTORICAL"},
    "REAL_MAJOR_IDM": {"ACTIVE", "SWEPT", "SUPERSEDED", "HISTORICAL"},
    "CONFIRMED_STRUCTURAL_SWING": {"ACTIVE", "HISTORICAL", "SUPERSEDED"},
    "PROTECTED_STRUCTURAL_EXTREME": {"ACTIVE", "BROKEN", "SUPERSEDED", "HISTORICAL"},
    "TRADING_RANGE": {"ACTIVE", "SUPERSEDED", "HISTORICAL"},
}
REQUIRED_PARENTS = {
    "VERIFIED_PULLBACK_EXTREME": {"CANDLE_LEVEL_VALID_PULLBACK"},
    "STRUCTURALLY_VALID_PULLBACK": {"VERIFIED_PULLBACK_EXTREME"},
    "MINOR_IDM": {"STRUCTURALLY_VALID_PULLBACK", "VERIFIED_PULLBACK_EXTREME"},
    "IDM_TAKEN": {"MINOR_IDM"},
    "CONFIRMED_STRUCTURAL_SWING": {"IDM_TAKEN"},
    "VALID_BOS": {"CONFIRMED_STRUCTURAL_SWING", "IDM_TAKEN",
                  "PHYSICAL_EXTERNAL_BREAK", "STRUCTURALLY_VALID_PULLBACK"},
    "PROTECTED_STRUCTURAL_EXTREME": {"VALID_BOS"},
    "CHoCH_ELIGIBLE": {"PROTECTED_STRUCTURAL_EXTREME", "PHYSICAL_EXTERNAL_BREAK"},
    "CHoCH_CONFIRMED": {"CHoCH_ELIGIBLE", "PROTECTED_STRUCTURAL_EXTREME",
                        "PHYSICAL_EXTERNAL_BREAK"},
    "MAJOR_IDM_SWEEP": {"FALLBACK_MAJOR_IDM"},
}


class StructuralEvidenceError(ValueError):
    """Strict upstream structural-evidence contract violation."""


@dataclass(frozen=True)
class StructuralEvidence:
    evidence_id: str
    workflow_id: str
    symbol: str
    timeframe: str
    event_timestamp: str
    producer: str
    methodology_version: str
    object_type: str
    object_id: str
    parent_evidence_ids: tuple[str, ...] = ()
    source_candle_ids: tuple[str, ...] = ()
    state: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    payload: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "StructuralEvidence":
        required = {
            "evidence_id", "workflow_id", "symbol", "timeframe", "event_timestamp",
            "producer", "methodology_version", "object_type", "object_id",
            "parent_evidence_ids", "source_candle_ids", "state", "provenance", "payload",
        }
        if not isinstance(value, Mapping):
            raise StructuralEvidenceError("SCHEMA_INVALID: evidence must be an object")
        missing = required - set(value)
        unknown = set(value) - required
        if missing:
            raise StructuralEvidenceError(f"SCHEMA_INVALID: missing fields: {sorted(missing)}")
        if unknown:
            raise StructuralEvidenceError(f"SCHEMA_INVALID: unknown fields: {sorted(unknown)}")

        def strings(name: str) -> tuple[str, ...]:
            raw = value[name]
            if not isinstance(raw, (list, tuple)) or any(
                not isinstance(x, str) or not x for x in raw
            ):
                raise StructuralEvidenceError(
                    f"SCHEMA_INVALID: {name} must contain non-empty strings"
                )
            return tuple(raw)

        for name in (
            "evidence_id", "workflow_id", "symbol", "timeframe",
            "event_timestamp", "producer", "methodology_version",
            "object_type", "object_id",
        ):
            if not isinstance(value[name], str) or not value[name].strip():
                raise StructuralEvidenceError(f"SCHEMA_INVALID: {name} must be non-empty")
        if value["state"] is not None and not isinstance(value["state"], str):
            raise StructuralEvidenceError("SCHEMA_INVALID: state must be string or null")
        if not isinstance(value["provenance"], Mapping) or not isinstance(value["payload"], Mapping):
            raise StructuralEvidenceError("SCHEMA_INVALID: provenance/payload must be objects")
        return cls(
            evidence_id=value["evidence_id"], workflow_id=value["workflow_id"],
            symbol=value["symbol"], timeframe=value["timeframe"],
            event_timestamp=value["event_timestamp"], producer=value["producer"],
            methodology_version=value["methodology_version"], object_type=value["object_type"],
            object_id=value["object_id"], parent_evidence_ids=strings("parent_evidence_ids"),
            source_candle_ids=strings("source_candle_ids"), state=value["state"],
            provenance=dict(value["provenance"]), payload=dict(value["payload"]),
        )


def _timestamp(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise StructuralEvidenceError("SCHEMA_INVALID: invalid event_timestamp") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise StructuralEvidenceError("SCHEMA_INVALID: event_timestamp must be timezone-aware")
    return dt


def _payload(e: StructuralEvidence, *keys: str) -> None:
    missing = [k for k in keys if k not in e.payload]
    if missing:
        raise StructuralEvidenceError(
            f"STRUCTURAL_PROVENANCE_UNVERIFIED: {e.object_type} missing payload: {missing}"
        )


def _ref(e: StructuralEvidence, graph: Mapping[str, StructuralEvidence],
         key: str, expected_type: str | None = None) -> StructuralEvidence:
    value = e.payload.get(key)
    if not isinstance(value, str) or not value:
        raise StructuralEvidenceError(
            f"STRUCTURAL_PROVENANCE_UNVERIFIED: {e.object_type} requires {key}"
        )
    parent = graph.get(value)
    if parent is None:
        raise StructuralEvidenceError(
            f"STRUCTURAL_PROVENANCE_UNVERIFIED: {e.object_type} {key} does not reference supplied evidence"
        )
    if expected_type and parent.object_type != expected_type:
        raise StructuralEvidenceError(
            f"STRUCTURAL_PROVENANCE_UNVERIFIED: {e.object_type} {key} must reference {expected_type}"
        )
    return parent


def validate_evidence(
    evidence: Iterable[StructuralEvidence | Mapping[str, Any]],
) -> tuple[StructuralEvidence, ...]:
    """Validate an upstream evidence graph; never infer missing structural truth."""
    items = tuple(
        x if isinstance(x, StructuralEvidence) else StructuralEvidence.from_mapping(x)
        for x in evidence
    )
    graph: dict[str, StructuralEvidence] = {}

    for e in items:
        if e.evidence_id in graph:
            raise StructuralEvidenceError(
                f"SCHEMA_INVALID: duplicate evidence_id: {e.evidence_id}"
            )
        graph[e.evidence_id] = e
        _timestamp(e.event_timestamp)
        if e.object_type not in OBJECT_TYPES:
            raise StructuralEvidenceError(
                f"SCHEMA_INVALID: unsupported object_type: {e.object_type}"
            )
        if len(set(e.parent_evidence_ids)) != len(e.parent_evidence_ids):
            raise StructuralEvidenceError(
                f"SCHEMA_INVALID: duplicate parent evidence id: {e.evidence_id}"
            )
        if e.object_type in EVENT_TYPES and not e.source_candle_ids:
            raise StructuralEvidenceError(
                f"STRUCTURAL_PROVENANCE_UNVERIFIED: event has no source candles: {e.evidence_id}"
            )
        allowed = ALLOWED_STATES.get(e.object_type)
        if allowed is not None and (e.state is None or e.state not in allowed):
            raise StructuralEvidenceError(
                f"SCHEMA_INVALID: invalid state for {e.object_type}: {e.state}"
            )
        if allowed is None and e.state is not None:
            raise StructuralEvidenceError(
                f"SCHEMA_INVALID: state is not defined for {e.object_type}"
            )

    for e in items:
        missing = [p for p in e.parent_evidence_ids if p not in graph]
        if missing:
            raise StructuralEvidenceError(
                f"STRUCTURAL_PROVENANCE_UNVERIFIED: missing parent evidence: {missing}"
            )
        parent_types = {graph[p].object_type for p in e.parent_evidence_ids}
        required = REQUIRED_PARENTS.get(e.object_type, set())
        if required and not required.issubset(parent_types):
            raise StructuralEvidenceError(
                f"STRUCTURAL_PROVENANCE_UNVERIFIED: {e.object_type} requires parent types "
                f"{sorted(required)}; got {sorted(parent_types)}"
            )
        child_time = _timestamp(e.event_timestamp)
        for pid in e.parent_evidence_ids:
            p = graph[pid]
            if (p.workflow_id, p.symbol, p.timeframe) != (e.workflow_id, e.symbol, e.timeframe):
                raise StructuralEvidenceError(
                    f"STRUCTURAL_PROVENANCE_UNVERIFIED: parent context mismatch for {e.evidence_id}"
                )
            if _timestamp(p.event_timestamp) > child_time:
                raise StructuralEvidenceError(
                    f"STRUCTURAL_PROVENANCE_UNVERIFIED: parent event occurs after child event: {pid} -> {e.evidence_id}"
                )

        if e.object_type == "STRUCTURALLY_VALID_PULLBACK":
            _payload(e, "source_verified_pullback_extreme_id", "qualification_evidence_id",
                     "active_impulsive_leg_id", "retracement_depth", "opposing_candle_count")
            _ref(e, graph, "source_verified_pullback_extreme_id", "VERIFIED_PULLBACK_EXTREME")
        elif e.object_type == "MINOR_IDM":
            _payload(e, "source_svp_id", "source_verified_extreme_id",
                     "active_impulsive_leg_id", "liquidity_extreme")
            _ref(e, graph, "source_svp_id", "STRUCTURALLY_VALID_PULLBACK")
            _ref(e, graph, "source_verified_extreme_id", "VERIFIED_PULLBACK_EXTREME")
        elif e.object_type == "IDM_TAKEN":
            _payload(e, "idm_id", "interaction_type", "event_identity")
            _ref(e, graph, "idm_id")
            if e.payload["interaction_type"] not in {"WICK", "BODY"}:
                raise StructuralEvidenceError("SCHEMA_INVALID: IDM_TAKEN interaction_type")
            if not isinstance(e.payload["event_identity"], str) or not e.payload["event_identity"]:
                raise StructuralEvidenceError("SCHEMA_INVALID: IDM_TAKEN event_identity")
        elif e.object_type == "CONFIRMED_STRUCTURAL_SWING":
            _payload(e, "source_idm_taken_id", "expansion_extreme", "direction")
            _ref(e, graph, "source_idm_taken_id", "IDM_TAKEN")
        elif e.object_type == "PHYSICAL_EXTERNAL_BREAK":
            _payload(e, "boundary_id", "break_type", "boundary_type")
            _ref(e, graph, "boundary_id")
            if e.payload["break_type"] not in {"WICK", "BODY"}:
                raise StructuralEvidenceError("SCHEMA_INVALID: break_type must be WICK or BODY")
            if e.payload["boundary_type"] not in {
                "CONFIRMED_STRUCTURAL_SWING", "PROTECTED_STRUCTURAL_EXTREME",
                "FALLBACK_MAJOR_IDM", "REAL_MAJOR_IDM",
            }:
                raise StructuralEvidenceError("SCHEMA_INVALID: unsupported boundary_type")
            if e.payload["boundary_type"] not in parent_types:
                raise StructuralEvidenceError(
                    "STRUCTURAL_PROVENANCE_UNVERIFIED: break boundary provenance mismatch"
                )
        elif e.object_type == "VALID_BOS":
            _payload(e, "confirmed_swing_id", "idm_taken_id", "structural_break_id",
                     "stored_qualification_id", "retracement_depth", "bos_gate_result")
            _ref(e, graph, "confirmed_swing_id", "CONFIRMED_STRUCTURAL_SWING")
            _ref(e, graph, "idm_taken_id", "IDM_TAKEN")
            _ref(e, graph, "structural_break_id", "PHYSICAL_EXTERNAL_BREAK")
            _ref(e, graph, "stored_qualification_id", "STRUCTURALLY_VALID_PULLBACK")
            depth = e.payload["retracement_depth"]
            if e.payload["bos_gate_result"] is not True:
                raise StructuralEvidenceError("STRUCTURAL_PROVENANCE_UNVERIFIED: BOS gate is false")
            if isinstance(depth, bool) or not isinstance(depth, (int, float)) or not math.isfinite(depth) or depth < 0.382:
                raise StructuralEvidenceError("STRUCTURAL_PROVENANCE_UNVERIFIED: BOS requires retracement_depth >= 0.382")
        elif e.object_type == "PROTECTED_STRUCTURAL_EXTREME":
            _payload(e, "source_valid_bos_id", "lock_event_id", "boundary_price", "direction")
            _ref(e, graph, "source_valid_bos_id", "VALID_BOS")
        elif e.object_type == "FALLBACK_MAJOR_IDM":
            _payload(e, "boundary_id", "provenance_role")
            _ref(e, graph, "boundary_id", "PROTECTED_STRUCTURAL_EXTREME")
            if e.payload["provenance_role"] != "FALLBACK_MAJOR_IDM":
                raise StructuralEvidenceError("STRUCTURAL_PROVENANCE_UNVERIFIED: fallback role mismatch")
        elif e.object_type == "REAL_MAJOR_IDM":
            _payload(e, "source_svp_id", "source_verified_extreme_id", "provenance_role")
            _ref(e, graph, "source_svp_id", "STRUCTURALLY_VALID_PULLBACK")
            _ref(e, graph, "source_verified_extreme_id", "VERIFIED_PULLBACK_EXTREME")
            if e.payload["provenance_role"] != "REAL_MAJOR_IDM":
                raise StructuralEvidenceError("STRUCTURAL_PROVENANCE_UNVERIFIED: real-major role mismatch")
        elif e.object_type == "MAJOR_IDM_SWEEP":
            _payload(e, "fallback_major_idm_id", "sweep_type")
            _ref(e, graph, "fallback_major_idm_id", "FALLBACK_MAJOR_IDM")
            if e.payload["sweep_type"] not in {"WICK", "BODY"}:
                raise StructuralEvidenceError("SCHEMA_INVALID: sweep_type must be WICK or BODY")
            if "REAL_MAJOR_IDM" in parent_types:
                raise StructuralEvidenceError(
                    "STRUCTURAL_PROVENANCE_UNVERIFIED: MAJOR_IDM_SWEEP fallback lineage cannot include REAL_MAJOR_IDM"
                )
        elif e.object_type == "CHoCH_ELIGIBLE":
            _payload(e, "protected_opposing_boundary_id", "physical_break_id", "classification")
            _ref(e, graph, "protected_opposing_boundary_id", "PROTECTED_STRUCTURAL_EXTREME")
            _ref(e, graph, "physical_break_id", "PHYSICAL_EXTERNAL_BREAK")
            if e.payload["classification"] not in {"WICK", "BODY"}:
                raise StructuralEvidenceError("SCHEMA_INVALID: CHoCH classification")
            if e.payload["classification"] == "WICK" and "REAL_MAJOR_IDM" not in parent_types:
                raise StructuralEvidenceError(
                    "STRUCTURAL_PROVENANCE_UNVERIFIED: CHoCH wick eligibility requires REAL_MAJOR_IDM lineage"
                )
        elif e.object_type == "CHoCH_CONFIRMED":
            _payload(e, "protected_opposing_boundary_id", "physical_break_id",
                     "classification", "prerequisite_evidence")
            _ref(e, graph, "protected_opposing_boundary_id", "PROTECTED_STRUCTURAL_EXTREME")
            _ref(e, graph, "physical_break_id", "PHYSICAL_EXTERNAL_BREAK")

    return items


def accept_for_monitor(
    evidence: Iterable[StructuralEvidence | Mapping[str, Any]],
) -> tuple[StructuralEvidence, ...]:
    """Monitor boundary: accept validated evidence; never synthesize missing state."""
    return validate_evidence(evidence)
