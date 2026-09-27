"""Layer 5 Change-of-Character mechanics.

Consumes Layer-3 structural state and owns only CHoCH boundary classification.
Canonical CHoCH prerequisites that are established outside this layer are passed
explicitly as confirmation_gate_open; this engine never invents missing
structural prerequisites.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from microstructure_engine import (
    BreachMode,
    Candle,
    Direction,
    ExtremeReference,
    QuarantineError,
    classify_breach,
)
from structural_engine import IDMClass, IDMOrigin, IDMEvent, PullbackDirection


class CHoCHResolution(str, Enum):
    NO_EVIDENCE = "NO_EVIDENCE"
    NO_BOUNDARY_BREAK = "NO_BOUNDARY_BREAK"
    MAJOR_IDM_SWEEP = "MAJOR_IDM_SWEEP"
    CHOCH_ELIGIBLE = "CHOCH_ELIGIBLE"
    CHOCH_CONFIRMED = "CHOCH_CONFIRMED"


class CHoCHReferenceKind(str, Enum):
    PROTECTED_OPPOSING_BOUNDARY = "PROTECTED_OPPOSING_BOUNDARY"
    LTF_ACTIVE_IDM = "LTF_ACTIVE_IDM"


@dataclass(frozen=True, slots=True)
class CHoCHReference:
    direction: PullbackDirection
    price: Decimal
    source_candle_id: str
    kind: CHoCHReferenceKind
    idm_class: IDMClass | None = None
    idm_origin: IDMOrigin | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.direction, PullbackDirection):
            raise QuarantineError("invalid CHoCH reference direction")
        if not isinstance(self.price, Decimal) or not self.price.is_finite():
            raise QuarantineError("CHoCH reference price requires finite Decimal")
        if not isinstance(self.source_candle_id, str) or not self.source_candle_id:
            raise QuarantineError("CHoCH reference requires source candle ID")
        if not isinstance(self.kind, CHoCHReferenceKind):
            raise QuarantineError("invalid CHoCH reference kind")
        if (self.idm_class is None) != (self.idm_origin is None):
            raise QuarantineError("CHoCH IDM provenance must be complete")
        if self.kind is CHoCHReferenceKind.LTF_ACTIVE_IDM and self.idm_class is None:
            raise QuarantineError("LTF CHoCH reference requires IDM provenance")
        if self.idm_class is not None and not isinstance(self.idm_class, IDMClass):
            raise QuarantineError("invalid CHoCH IDM class")
        if self.idm_origin is not None and not isinstance(self.idm_origin, IDMOrigin):
            raise QuarantineError("invalid CHoCH IDM origin")


@dataclass(frozen=True, slots=True)
class CHoCHBreak:
    direction: PullbackDirection
    reference_price: Decimal
    reference_candle_id: str
    break_candle_id: str
    mode: BreachMode
    reference_kind: CHoCHReferenceKind

    def __post_init__(self) -> None:
        if not isinstance(self.direction, PullbackDirection):
            raise QuarantineError("invalid CHoCH-break direction")
        if not isinstance(self.reference_price, Decimal) or not self.reference_price.is_finite():
            raise QuarantineError("CHoCH break price requires finite Decimal")
        for value, name in (
            (self.reference_candle_id, "reference_candle_id"),
            (self.break_candle_id, "break_candle_id"),
        ):
            if not isinstance(value, str) or not value:
                raise QuarantineError(f"CHoCH break requires {name}")
        if self.mode is BreachMode.EQUAL:
            raise QuarantineError("CHoCH break requires physical penetration")
        if not isinstance(self.reference_kind, CHoCHReferenceKind):
            raise QuarantineError("invalid CHoCH reference kind")


@dataclass(frozen=True, slots=True)
class PostCHoCHRegime:
    new_direction: PullbackDirection
    initial_active_impulse_candle_id: str
    confirmation_locked: bool
    ltf_context_cleared: bool

    def __post_init__(self) -> None:
        if not isinstance(self.new_direction, PullbackDirection):
            raise QuarantineError("invalid post-CHoCH direction")
        if not isinstance(self.initial_active_impulse_candle_id, str) or not self.initial_active_impulse_candle_id:
            raise QuarantineError("post-CHoCH regime requires initial impulse provenance")
        if not isinstance(self.confirmation_locked, bool) or not isinstance(self.ltf_context_cleared, bool):
            raise QuarantineError("post-CHoCH regime flags must be boolean")
        if not self.confirmation_locked:
            raise QuarantineError("post-CHoCH regime must begin confirmation-locked")


@dataclass(frozen=True, slots=True)
class CHoCHAnalysis:
    resolution: CHoCHResolution
    structural_break: CHoCHBreak | None
    confirmed: bool
    confirmation_gate_open: bool
    post_choch_regime: PostCHoCHRegime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.resolution, CHoCHResolution):
            raise QuarantineError("invalid CHoCH resolution")
        if not isinstance(self.confirmed, bool) or not isinstance(self.confirmation_gate_open, bool):
            raise QuarantineError("CHoCH flags must be boolean")
        if self.confirmed != (self.resolution is CHoCHResolution.CHOCH_CONFIRMED):
            raise QuarantineError("CHoCH confirmation flag and resolution disagree")
        if self.resolution in {
            CHoCHResolution.CHOCH_ELIGIBLE,
            CHoCHResolution.CHOCH_CONFIRMED,
        } and self.structural_break is None:
            raise QuarantineError("classified CHoCH outcome requires structural break")
        if self.confirmed and self.post_choch_regime is None:
            raise QuarantineError("confirmed CHoCH requires post-CHoCH regime initialization")
        if not self.confirmed and self.post_choch_regime is not None:
            raise QuarantineError("unconfirmed CHoCH cannot initialize post-CHoCH regime")


def reference_from_boundary(
    direction: PullbackDirection,
    *,
    price: Decimal,
    source_candle_id: str,
    idm_class: IDMClass | None = None,
    idm_origin: IDMOrigin | None = None,
) -> CHoCHReference:
    return CHoCHReference(
        direction,
        price,
        source_candle_id,
        CHoCHReferenceKind.PROTECTED_OPPOSING_BOUNDARY,
        idm_class,
        idm_origin,
    )


def reference_from_ltf_idm(idm: IDMEvent) -> CHoCHReference:
    if not isinstance(idm, IDMEvent):
        raise QuarantineError("LTF CHoCH reference requires Layer-3 IDMEvent")
    if idm.origin is not IDMOrigin.PULLBACK_DERIVED:
        raise QuarantineError("LTF CHoCH reference requires pullback-derived IDM provenance")
    return CHoCHReference(
        idm.direction,
        idm.reference_price,
        idm.source_candle_id,
        CHoCHReferenceKind.LTF_ACTIVE_IDM,
        idm.idm_class,
        idm.origin,
    )


def _physical_break(candle: Candle, reference: CHoCHReference) -> tuple[BreachMode, bool] | None:
    side = Direction.DOWN if reference.direction is PullbackDirection.BULLISH else Direction.UP
    observation = classify_breach(
        candle,
        ExtremeReference(reference.price, reference.source_candle_id, "CHOCH_REFERENCE"),
        side,
    )
    if not observation.is_break:
        return None
    body_close = (
        candle.close < reference.price
        if reference.direction is PullbackDirection.BULLISH
        else candle.close > reference.price
    )
    return observation.mode, body_close


def _eligible_for_break(reference: CHoCHReference, body_close: bool) -> CHoCHResolution | None:
    if reference.idm_class is IDMClass.MAJOR_IDM and not body_close:
        if reference.kind is CHoCHReferenceKind.PROTECTED_OPPOSING_BOUNDARY:
            return CHoCHResolution.MAJOR_IDM_SWEEP
    if reference.kind is CHoCHReferenceKind.LTF_ACTIVE_IDM and reference.idm_class is IDMClass.MINOR_IDM and not body_close:
        return CHoCHResolution.NO_BOUNDARY_BREAK
    return None


def detect_choch(
    candles: list[Candle] | tuple[Candle, ...],
    reference: CHoCHReference,
    *,
    confirmation_gate_open: bool,
    break_candle_id: str | None = None,
    ltf_context_active: bool = False,
) -> CHoCHAnalysis:
    """Classify the first physical opposing-boundary break.

    A body close or an eligible non-Major-IDM wick opens CHoCH eligibility.
    Final confirmation is deliberately gated by the caller-supplied complete
    CHoCH prerequisite result. This preserves the canonical rule that a
    physical break or body close alone cannot manufacture CHoCH_CONFIRMED.
    """
    sequence = tuple(candles)
    if any(not isinstance(c, Candle) for c in sequence):
        raise QuarantineError("Layer 5 accepts only Layer 1 Candle objects")
    ids = [c.candle_id for c in sequence]
    if len(ids) != len(set(ids)):
        raise QuarantineError("duplicate candle IDs are not allowed")
    if not isinstance(reference, CHoCHReference):
        raise QuarantineError("Layer 5 requires an explicit CHoCH reference")
    if not isinstance(confirmation_gate_open, bool):
        raise QuarantineError("confirmation_gate_open must be boolean")
    if not isinstance(ltf_context_active, bool):
        raise QuarantineError("ltf_context_active must be boolean")
    if reference.kind is CHoCHReferenceKind.LTF_ACTIVE_IDM and not ltf_context_active:
        raise QuarantineError("LTF CHoCH reference requires active Structural Glitch context")

    candidates = sequence
    if break_candle_id is not None:
        matches = [c for c in sequence if c.candle_id == break_candle_id]
        if not matches:
            raise QuarantineError("break candle is absent")
        candidates = tuple(matches)

    for candle in candidates:
        event = _physical_break(candle, reference)
        if event is None:
            continue
        mode, body_close = event
        gated = _eligible_for_break(reference, body_close)
        if gated is not None:
            return CHoCHAnalysis(gated, None, False, confirmation_gate_open)

        structural_break = CHoCHBreak(
            reference.direction,
            reference.price,
            reference.source_candle_id,
            candle.candle_id,
            mode,
            reference.kind,
        )
        if not confirmation_gate_open:
            return CHoCHAnalysis(
                CHoCHResolution.CHOCH_ELIGIBLE,
                structural_break,
                False,
                False,
            )
        new_direction = (
            PullbackDirection.BEARISH
            if reference.direction is PullbackDirection.BULLISH
            else PullbackDirection.BULLISH
        )
        regime = PostCHoCHRegime(
            new_direction=new_direction,
            initial_active_impulse_candle_id=candle.candle_id,
            confirmation_locked=True,
            ltf_context_cleared=True,
        )
        return CHoCHAnalysis(
            CHoCHResolution.CHOCH_CONFIRMED,
            structural_break,
            True,
            True,
            regime,
        )

    return CHoCHAnalysis(
        CHoCHResolution.NO_BOUNDARY_BREAK,
        None,
        False,
        confirmation_gate_open,
    )


__all__ = [
    "CHoCHAnalysis",
    "CHoCHBreak",
    "CHoCHReference",
    "CHoCHReferenceKind",
    "PostCHoCHRegime",
    "CHoCHResolution",
    "detect_choch",
    "reference_from_boundary",
    "reference_from_ltf_idm",
]
