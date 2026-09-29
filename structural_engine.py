"""Layer 3 structural lifecycle engine.

Consumes Layer 1 candle primitives and Layer 2 minor-structure outputs.
Owns IDM classification/lifecycle, IDM takeout, confirmed structural
swings, and structural retracement qualification. It does not implement
BOS, CHoCH, POI, RR, or Mapper integration.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from microstructure_engine import (
    Candle,
    Direction,
    ExtremeReference,
    QuarantineError,
    classify_breach,
)
from minor_structure_engine import (
    CandleLevelValidPullback,
    MinorStructureAnalysis,
    PullbackDirection,
)

STANDARD_EQUILIBRIUM_THRESHOLD = Decimal("0.50")
HTF_CONDITIONAL_THRESHOLD = Decimal("0.382")
NORMAL_RETRACEMENT_CANDLE_COUNT = 3
MIN_RETRACEMENT_CANDLE_COUNT = 2
MIN_OUTLIER_EXTREMES_TAKEN = 5


class IDMClass(str, Enum):
    MINOR_IDM = "MINOR_IDM"
    MAJOR_IDM = "MAJOR_IDM"


class IDMOrigin(str, Enum):
    PULLBACK_DERIVED = "PULLBACK_DERIVED"
    PROTECTED_EXTERNAL_BOUNDARY = "PROTECTED_EXTERNAL_BOUNDARY"


class StructuralResolution(str, Enum):
    NO_EVIDENCE = "NO_EVIDENCE"
    IDM_ACTIVE = "IDM_ACTIVE"
    IDM_TAKEN = "IDM_TAKEN"
    RETRACEMENT_QUALIFIED = "RETRACEMENT_QUALIFIED"
    RETRACEMENT_INSUFFICIENT = "RETRACEMENT_INSUFFICIENT"


@dataclass(frozen=True, slots=True)
class ProtectedExternalBoundary:
    direction: PullbackDirection
    price: Decimal
    source_candle_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.direction, PullbackDirection):
            raise QuarantineError("invalid protected-boundary direction")
        if not isinstance(self.price, Decimal) or not self.price.is_finite():
            raise QuarantineError("protected-boundary price requires finite Decimal")
        if not isinstance(self.source_candle_id, str) or not self.source_candle_id:
            raise QuarantineError("protected boundary requires source candle ID")


@dataclass(frozen=True, slots=True)
class IDMLifecycleContext:
    """Layer-3-owned lifecycle input describing a completed BOS rollover.

    The caller may advance the lifecycle only with an explicit VALID_BOS
    transition. It cannot select an arbitrary pullback as Major IDM.
    """

    after_valid_bos: bool = False
    valid_bos_candle_id: str | None = None
    protected_external_boundary: ProtectedExternalBoundary | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.after_valid_bos, bool):
            raise QuarantineError("after_valid_bos must be boolean")
        if self.valid_bos_candle_id is not None and (
            not isinstance(self.valid_bos_candle_id, str) or not self.valid_bos_candle_id
        ):
            raise QuarantineError("valid_bos_candle_id must be a non-empty string")
        if not self.after_valid_bos:
            if (
                self.valid_bos_candle_id is not None
                or self.protected_external_boundary is not None
            ):
                raise QuarantineError("post-BOS lifecycle fields require VALID_BOS")
            return
        if self.valid_bos_candle_id is None:
            raise QuarantineError("post-BOS IDM lifecycle requires VALID_BOS candle provenance")


@dataclass(frozen=True, slots=True)
class IDMEvent:
    idm_class: IDMClass
    origin: IDMOrigin
    direction: PullbackDirection
    reference_price: Decimal
    source_candle_id: str
    pullback_reference_candle_id: str | None = None
    pullback_completion_candle_id: str | None = None
    takeout_candle_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.idm_class, IDMClass):
            raise QuarantineError("invalid IDM class")
        if not isinstance(self.origin, IDMOrigin):
            raise QuarantineError("invalid IDM origin")
        if not isinstance(self.direction, PullbackDirection):
            raise QuarantineError("invalid IDM direction")
        if not isinstance(self.reference_price, Decimal) or not self.reference_price.is_finite():
            raise QuarantineError("IDM price requires finite Decimal")
        if not isinstance(self.source_candle_id, str) or not self.source_candle_id:
            raise QuarantineError("IDM requires source candle ID")
        if self.origin is IDMOrigin.PULLBACK_DERIVED:
            for value, name in (
                (self.pullback_reference_candle_id, "pullback_reference_candle_id"),
                (self.pullback_completion_candle_id, "pullback_completion_candle_id"),
            ):
                if not isinstance(value, str) or not value:
                    raise QuarantineError(f"pullback-derived IDM requires {name}")
        elif self.pullback_reference_candle_id is not None or self.pullback_completion_candle_id is not None:
            raise QuarantineError("protected-boundary IDM cannot carry pullback provenance")
        if self.takeout_candle_id is not None and (
            not isinstance(self.takeout_candle_id, str) or not self.takeout_candle_id
        ):
            raise QuarantineError("invalid IDM takeout candle ID")


@dataclass(frozen=True, slots=True)
class CanonicalDealingRange:
    range_id: str
    origin_candle_id: str
    origin_price: Decimal | None = None
    direction: PullbackDirection | None = None
    idm_candle_id: str | None = None
    takeout_candle_id: str | None = None
    range_high: Decimal | None = None
    range_low: Decimal | None = None


@dataclass(frozen=True, slots=True)
class ConfirmedStructuralSwing:
    direction: PullbackDirection
    price: Decimal
    source_candle_id: str
    confirming_idm_source_candle_id: str
    confirmation_candle_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.direction, PullbackDirection):
            raise QuarantineError("invalid swing direction")
        if not isinstance(self.price, Decimal) or not self.price.is_finite():
            raise QuarantineError("swing price requires finite Decimal")
        for value, name in (
            (self.source_candle_id, "source_candle_id"),
            (self.confirming_idm_source_candle_id, "confirming_idm_source_candle_id"),
            (self.confirmation_candle_id, "confirmation_candle_id"),
        ):
            if not isinstance(value, str) or not value:
                raise QuarantineError(f"swing requires {name}")


@dataclass(frozen=True, slots=True)
class RetracementQualification:
    qualified: bool
    depth: Decimal
    opposing_candle_count: int
    htf_valid_pullback: bool
    used_outlier_exception: bool
    reason: str
    qualification_end_candle_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.qualified, bool):
            raise QuarantineError("qualification flag must be boolean")
        if not isinstance(self.depth, Decimal) or not self.depth.is_finite():
            raise QuarantineError("retracement depth requires finite Decimal")
        if self.opposing_candle_count < 0:
            raise QuarantineError("opposing candle count cannot be negative")
        if not isinstance(self.htf_valid_pullback, bool):
            raise QuarantineError("HTF evidence must be explicit boolean")
        if not isinstance(self.used_outlier_exception, bool):
            raise QuarantineError("outlier flag must be boolean")
        if not isinstance(self.reason, str) or not self.reason:
            raise QuarantineError("qualification reason is required")
        if not isinstance(self.qualification_end_candle_id, str) or not self.qualification_end_candle_id:
            raise QuarantineError("qualification end candle provenance is required")


@dataclass(frozen=True, slots=True)
class StructuralAnalysis:
    idm_events: tuple[IDMEvent, ...]
    confirmed_swings: tuple[ConfirmedStructuralSwing, ...]
    retracement: RetracementQualification | None
    active_idm: IDMEvent | None
    resolution: StructuralResolution
    active_dealing_range: CanonicalDealingRange | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "idm_events", tuple(self.idm_events))
        object.__setattr__(self, "confirmed_swings", tuple(self.confirmed_swings))
        if self.active_idm is not None and self.active_idm not in self.idm_events:
            raise QuarantineError("active IDM must be historical IDM")


def _validate_inputs(candles: tuple[Candle, ...], minor: MinorStructureAnalysis) -> None:
    if any(not isinstance(c, Candle) for c in candles):
        raise QuarantineError("Layer 3 accepts only Layer 1 Candle objects")
    if not isinstance(minor, MinorStructureAnalysis):
        raise QuarantineError("Layer 3 requires Layer 2 MinorStructureAnalysis")
    ids = [c.candle_id for c in candles]
    if len(ids) != len(set(ids)):
        raise QuarantineError("duplicate candle IDs are not allowed")
    candle_ids = set(ids)
    for pb in minor.pullbacks:
        if not {
            pb.reference_candle_id,
            pb.start_candle_id,
            pb.completion_candle_id,
            pb.extreme.source_candle_id,
        } <= candle_ids:
            raise QuarantineError("Layer 2 provenance references unknown candle")


def _index(candles: tuple[Candle, ...]) -> dict[str, int]:
    return {c.candle_id: i for i, c in enumerate(candles)}


def _pullback_idm(pb: CandleLevelValidPullback, idm_class: IDMClass) -> IDMEvent:
    return IDMEvent(
        idm_class=idm_class,
        origin=IDMOrigin.PULLBACK_DERIVED,
        direction=pb.direction,
        reference_price=pb.extreme.price,
        source_candle_id=pb.extreme.source_candle_id,
        pullback_reference_candle_id=pb.reference_candle_id,
        pullback_completion_candle_id=pb.completion_candle_id,
    )


def _boundary_idm(boundary: ProtectedExternalBoundary) -> IDMEvent:
    return IDMEvent(
        idm_class=IDMClass.MAJOR_IDM,
        origin=IDMOrigin.PROTECTED_EXTERNAL_BOUNDARY,
        direction=boundary.direction,
        reference_price=boundary.price,
        source_candle_id=boundary.source_candle_id,
    )


def _takeout_after(
    candles: tuple[Candle, ...],
    start: int,
    pb: CandleLevelValidPullback,
) -> str | None:
    level = ExtremeReference(pb.extreme.price, pb.extreme.source_candle_id, "PULLBACK_EXTREME")
    direction = Direction.DOWN if pb.direction is PullbackDirection.BULLISH else Direction.UP
    for candle in candles[start + 1 :]:
        if classify_breach(candle, level, direction).is_break:
            return candle.candle_id
    return None


def _comes_after(
    completion_candle_id: str,
    bos_candle_id: str,
    candles: tuple[Candle, ...],
) -> bool:
    """Return True only when pullback completion occurs after VALID_BOS."""
    positions = _index(candles)
    if completion_candle_id not in positions or bos_candle_id not in positions:
        raise QuarantineError("IDM lifecycle references unknown candle")
    return positions[completion_candle_id] > positions[bos_candle_id]


def classify_idm(
    minor: MinorStructureAnalysis,
    *,
    candles: tuple[Candle, ...] | None = None,
    lifecycle: IDMLifecycleContext | None = None,
) -> tuple[IDMEvent, ...]:
    """Classify Layer-2 references and advance the Layer-3 IDM lifecycle.

    Before VALID_BOS every pullback-derived IDM is Minor. After VALID_BOS,
    the newest completed post-BOS Layer-2 valid pullback / verified extreme
    becomes the Major IDM. If no new post-BOS valid pullback exists, the prior
    protected external boundary remains the active Major IDM.
    """
    if not isinstance(minor, MinorStructureAnalysis):
        raise QuarantineError("Layer 3 requires Layer 2 MinorStructureAnalysis")
    if lifecycle is not None and not isinstance(lifecycle, IDMLifecycleContext):
        raise QuarantineError("invalid IDM lifecycle context")
    if lifecycle is not None and lifecycle.after_valid_bos:
        if candles is None:
            raise QuarantineError("post-BOS IDM classification requires ordered Layer-1 candles")
        if lifecycle.valid_bos_candle_id not in _index(candles):
            raise QuarantineError("VALID_BOS candle is absent from Layer-1 sequence")

    pullback_events = [
        _pullback_idm(pb, IDMClass.MINOR_IDM)
        for pb in minor.pullbacks
    ]
    if lifecycle is None or not lifecycle.after_valid_bos:
        return tuple(pullback_events)

    if lifecycle.valid_bos_candle_id is None:
        raise QuarantineError("post-BOS IDM lifecycle requires VALID_BOS candle provenance")

    post_bos_pullbacks = [
        pb for pb in minor.pullbacks
        if _comes_after(pb.start_candle_id, lifecycle.valid_bos_candle_id, candles)
        and _comes_after(pb.completion_candle_id, lifecycle.valid_bos_candle_id, candles)
    ]

    # The Layer-2 valid-pullback / verified-extreme state is already the
    # canonical qualification. Every completed post-BOS valid pullback is
    # therefore a Major IDM event in the new lifecycle; the newest one is
    # the active Major IDM. Earlier post-BOS Major IDM events remain immutable.
    if post_bos_pullbacks:
        post_bos_ids = {
            pb.completion_candle_id for pb in post_bos_pullbacks
        }
        return tuple(
            _pullback_idm(
                pb,
                IDMClass.MAJOR_IDM
                if pb.completion_candle_id in post_bos_ids
                else IDMClass.MINOR_IDM,
            )
            for pb in minor.pullbacks
        )

    if lifecycle.protected_external_boundary is None:
        raise QuarantineError(
            "no post-BOS valid pullback requires protected external boundary fallback"
        )
    events = list(pullback_events)
    events.append(_boundary_idm(lifecycle.protected_external_boundary))
    return tuple(events)

def qualify_retracement(
    candles: tuple[Candle, ...],
    swing: ConfirmedStructuralSwing,
    *,
    range_high: Decimal,
    range_low: Decimal,
    htf_valid_pullback: bool = False,
    attempt_end_candle_id: str | None = None,
) -> RetracementQualification:
    """Evaluate Layer-3 retracement gates without implementing BOS."""
    if not isinstance(range_high, Decimal) or not isinstance(range_low, Decimal):
        raise QuarantineError("range boundaries require Decimal")
    if (
        not range_high.is_finite()
        or not range_low.is_finite()
        or range_high <= range_low
    ):
        raise QuarantineError("invalid dealing-range boundaries")
    if not isinstance(htf_valid_pullback, bool):
        raise QuarantineError("HTF valid-pullback evidence must be explicit boolean")

    idx = _index(candles)
    if swing.confirmation_candle_id not in idx:
        raise QuarantineError("swing confirmation candle is absent")
    if attempt_end_candle_id is not None and attempt_end_candle_id not in idx:
        raise QuarantineError("retracement attempt-end candle is absent")
    start = idx[swing.confirmation_candle_id]
    end = idx[attempt_end_candle_id] if attempt_end_candle_id is not None else len(candles) - 1
    qualification_end_candle_id = candles[end].candle_id
    if end <= start:
        return RetracementQualification(
            False, Decimal("0"), 0, htf_valid_pullback, False,
            "NO_POST_CONFIRMATION_RETRACEMENT", qualification_end_candle_id,
        )

    window = candles[start + 1 : end + 1]
    if swing.direction is PullbackDirection.BULLISH:
        extreme = min(c.low for c in window)
        depth = (range_high - extreme) / (range_high - range_low)
        opposing = sum(c.close < c.open for c in window)
    else:
        extreme = max(c.high for c in window)
        depth = (extreme - range_low) / (range_high - range_low)
        opposing = sum(c.close > c.open for c in window)

    if depth >= STANDARD_EQUILIBRIUM_THRESHOLD:
        # Standard evidence is evaluated first and owns the ordinary path.
        if opposing >= NORMAL_RETRACEMENT_CANDLE_COUNT:
            return RetracementQualification(
                True, depth, opposing, htf_valid_pullback, False,
                "STANDARD_EQUILIBRIUM", qualification_end_candle_id,
            )

        # The reduced/outlier path is an explicit exception to the normal
        # candle-count gate. It is never used to relabel a standard path.
        if len(window) in (1, 2) and _outlier_condition(window, swing.direction, candles):
            return RetracementQualification(
                True, depth, opposing, htf_valid_pullback, True,
                "REDUCED_DISPLACEMENT_EXCEPTION", qualification_end_candle_id,
            )
        return RetracementQualification(
            False, depth, opposing, htf_valid_pullback, False,
            "INSUFFICIENT_CANDLE_STRUCTURE", qualification_end_candle_id,
        )

    if HTF_CONDITIONAL_THRESHOLD <= depth < STANDARD_EQUILIBRIUM_THRESHOLD:
        if htf_valid_pullback:
            return RetracementQualification(
                True, depth, opposing, True, False, "HTF_VALID_PULLBACK", qualification_end_candle_id
            )
        return RetracementQualification(
            False, depth, opposing, False, False,
            "HTF_PULLBACK_EVIDENCE_REQUIRED", qualification_end_candle_id,
        )

    return RetracementQualification(
        False, depth, opposing, htf_valid_pullback, False,
        "BELOW_CONDITIONAL_THRESHOLD", qualification_end_candle_id,
    )


def _outlier_condition(
    window: tuple[Candle, ...],
    direction: PullbackDirection,
    all_candles: tuple[Candle, ...],
) -> bool:
    """Validate the explicit 1/2-candle displacement exception.

    The exceptional candle(s) collectively must take at least five immediately
    preceding candle bodies/extremes. The count is over unique preceding
    candles, so two displacement candles cannot double-count the same reference.
    """
    if not window:
        return False

    positions = _index(all_candles)
    exceptional = sorted(
        window,
        key=lambda c: c.high - c.low,
        reverse=True,
    )[:2]
    earliest = min(positions[c.candle_id] for c in exceptional)
    preceding = list(
        all_candles[
            max(0, earliest - MIN_OUTLIER_EXTREMES_TAKEN):earliest
        ]
    )
    if len(preceding) < MIN_OUTLIER_EXTREMES_TAKEN:
        return False

    if direction is PullbackDirection.BULLISH:
        return sum(
            any(
                candidate.low < ref.low
                or candidate.low < min(ref.open, ref.close)
                for candidate in exceptional
            )
            for ref in preceding
        ) >= MIN_OUTLIER_EXTREMES_TAKEN

    return sum(
        any(
            candidate.high > ref.high
            or candidate.high > max(ref.open, ref.close)
            for candidate in exceptional
        )
        for ref in preceding
    ) >= MIN_OUTLIER_EXTREMES_TAKEN


def analyze_layer3(
    candles: list[Candle] | tuple[Candle, ...],
    minor: MinorStructureAnalysis,
    *,
    range_high: Decimal | None = None,
    range_low: Decimal | None = None,
    htf_valid_pullback: bool = False,
    lifecycle: IDMLifecycleContext | None = None,
    attempt_end_candle_id: str | None = None,
) -> StructuralAnalysis:
    sequence = tuple(candles)
    _validate_inputs(sequence, minor)
    idms = classify_idm(minor, candles=sequence, lifecycle=lifecycle)
    if not idms:
        return StructuralAnalysis((), (), None, None, StructuralResolution.NO_EVIDENCE)

    positions = _index(sequence)
    taken_events: list[IDMEvent] = []
    confirmed: list[ConfirmedStructuralSwing] = []

    for idm in idms:
        if idm.origin is not IDMOrigin.PULLBACK_DERIVED:
            taken_events.append(idm)
            continue
        pb = next(
            pb for pb in minor.pullbacks
            if pb.completion_candle_id == idm.pullback_completion_candle_id
        )
        takeout = _takeout_after(
            sequence, positions[pb.completion_candle_id], pb
        )
        updated = IDMEvent(
            idm.idm_class,
            idm.origin,
            idm.direction,
            idm.reference_price,
            idm.source_candle_id,
            idm.pullback_reference_candle_id,
            idm.pullback_completion_candle_id,
            takeout,
        )
        taken_events.append(updated)
        if takeout is not None:
            ref_candle = sequence[positions[idm.pullback_reference_candle_id]]
            swing_price = (
                ref_candle.high
                if idm.direction is PullbackDirection.BULLISH
                else ref_candle.low
            )
            confirmed.append(
                ConfirmedStructuralSwing(
                    idm.direction,
                    swing_price,
                    ref_candle.candle_id,
                    idm.source_candle_id,
                    takeout,
                )
            )

    active = taken_events[-1]
    if active.origin is not IDMOrigin.PULLBACK_DERIVED:
        return StructuralAnalysis(
            tuple(taken_events), tuple(confirmed), None, active,
            StructuralResolution.IDM_ACTIVE,
        )
    if active.takeout_candle_id is None:
        return StructuralAnalysis(
            tuple(taken_events), tuple(confirmed), None, active,
            StructuralResolution.IDM_ACTIVE,
        )

    swing = next(
        (s for s in reversed(confirmed) if s.confirmation_candle_id == active.takeout_candle_id),
        None,
    )
    if swing is None:
        raise QuarantineError("IDM takeout has no confirmed structural swing")
    if range_high is None or range_low is None:
        return StructuralAnalysis(
            tuple(taken_events), tuple(confirmed), None, active,
            StructuralResolution.IDM_TAKEN,
        )

    qualification = qualify_retracement(
        sequence,
        swing,
        range_high=range_high,
        range_low=range_low,
        htf_valid_pullback=htf_valid_pullback,
        attempt_end_candle_id=attempt_end_candle_id,
    )
    resolution = (
        StructuralResolution.RETRACEMENT_QUALIFIED
        if qualification.qualified
        else StructuralResolution.RETRACEMENT_INSUFFICIENT
    )
    return StructuralAnalysis(
        tuple(taken_events), tuple(confirmed), qualification, active, resolution
    )


__all__ = [
    "ConfirmedStructuralSwing",
    "HTF_CONDITIONAL_THRESHOLD",
    "IDMClass",
    "IDMEvent",
    "IDMLifecycleContext",
    "_comes_after",
    "IDMOrigin",
    "MIN_OUTLIER_EXTREMES_TAKEN",
    "MIN_RETRACEMENT_CANDLE_COUNT",
    "NORMAL_RETRACEMENT_CANDLE_COUNT",
    "ProtectedExternalBoundary",
    "RetracementQualification",
    "STANDARD_EQUILIBRIUM_THRESHOLD",
    "StructuralAnalysis",
    "StructuralResolution",
    "analyze_layer3",
    "classify_idm",
    "qualify_retracement",
]
