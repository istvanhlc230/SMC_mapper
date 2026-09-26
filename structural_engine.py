"""Layer 3 structural lifecycle engine.

Consumes Layer 1 candle primitives and Layer 2 minor-structure outputs. Owns
IDM classification/lifecycle, IDM takeout, confirmed structural swings and
structural retracement qualification. It deliberately does not implement BOS,
CHoCH, POI, RR, or mapper integration.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from microstructure_engine import Candle, Direction, ExtremeReference, QuarantineError, classify_breach
from minor_structure_engine import CandleLevelValidPullback, MinorStructureAnalysis, PullbackDirection

STANDARD_EQUILIBRIUM_THRESHOLD = Decimal("0.50")
HTF_CONDITIONAL_THRESHOLD = Decimal("0.382")
NORMAL_RETRACEMENT_CANDLE_COUNT = 3
MIN_RETRACEMENT_CANDLE_COUNT = 2
MIN_OUTLIER_EXTREMES_TAKEN = 5


class IDMClass(str, Enum):
    MINOR_IDM = "MINOR_IDM"
    MAJOR_IDM = "MAJOR_IDM"


class StructuralResolution(str, Enum):
    NO_EVIDENCE = "NO_EVIDENCE"
    IDM_ACTIVE = "IDM_ACTIVE"
    IDM_TAKEN = "IDM_TAKEN"
    RETRACEMENT_QUALIFIED = "RETRACEMENT_QUALIFIED"
    RETRACEMENT_INSUFFICIENT = "RETRACEMENT_INSUFFICIENT"


@dataclass(frozen=True, slots=True)
class IDMEvent:
    idm_class: IDMClass
    direction: PullbackDirection
    reference_price: Decimal
    source_candle_id: str
    pullback_reference_candle_id: str
    pullback_completion_candle_id: str
    takeout_candle_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.idm_class, IDMClass):
            raise QuarantineError("invalid IDM class")
        if not isinstance(self.direction, PullbackDirection):
            raise QuarantineError("invalid IDM direction")
        if not isinstance(self.reference_price, Decimal) or not self.reference_price.is_finite():
            raise QuarantineError("IDM price requires finite Decimal")
        for value, name in (
            (self.source_candle_id, "source_candle_id"),
            (self.pullback_reference_candle_id, "pullback_reference_candle_id"),
            (self.pullback_completion_candle_id, "pullback_completion_candle_id"),
        ):
            if not isinstance(value, str) or not value:
                raise QuarantineError(f"IDM requires {name}")
        if self.takeout_candle_id is not None and (not isinstance(self.takeout_candle_id, str) or not self.takeout_candle_id):
            raise QuarantineError("invalid IDM takeout candle ID")


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

    def __post_init__(self) -> None:
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


@dataclass(frozen=True, slots=True)
class StructuralAnalysis:
    idm_events: tuple[IDMEvent, ...]
    confirmed_swings: tuple[ConfirmedStructuralSwing, ...]
    retracement: RetracementQualification | None
    active_idm: IDMEvent | None
    resolution: StructuralResolution

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
        if not {pb.reference_candle_id, pb.start_candle_id, pb.completion_candle_id, pb.extreme.source_candle_id} <= candle_ids:
            raise QuarantineError("Layer 2 provenance references unknown candle")


def _index(candles: tuple[Candle, ...]) -> dict[str, int]:
    return {c.candle_id: i for i, c in enumerate(candles)}


def _pullback_idm(pb: CandleLevelValidPullback, idm_class: IDMClass) -> IDMEvent:
    return IDMEvent(
        idm_class=idm_class,
        direction=pb.direction,
        reference_price=pb.extreme.price,
        source_candle_id=pb.extreme.source_candle_id,
        pullback_reference_candle_id=pb.reference_candle_id,
        pullback_completion_candle_id=pb.completion_candle_id,
    )


def _takeout_after(candles: tuple[Candle, ...], start: int, pb: CandleLevelValidPullback) -> str | None:
    level = ExtremeReference(pb.extreme.price, pb.extreme.source_candle_id, "PULLBACK_EXTREME")
    direction = Direction.DOWN if pb.direction is PullbackDirection.BULLISH else Direction.UP
    for candle in candles[start + 1 :]:
        if classify_breach(candle, level, direction).is_break:
            return candle.candle_id
    return None


def classify_idm(
    minor: MinorStructureAnalysis,
    *,
    post_bos_pullback_ids: frozenset[str] = frozenset(),
) -> tuple[IDMEvent, ...]:
    """Classify Layer-2 pullback liquidity references as Minor or Major IDM.

    A pullback is Major IDM after BOS only when the caller explicitly supplies
    source-backed post-BOS structural qualification for that pullback. Otherwise
    pullback-derived IDM is Minor IDM. No fallback/proxy IDM ontology is made.
    """
    if not isinstance(post_bos_pullback_ids, frozenset):
        post_bos_pullback_ids = frozenset(post_bos_pullback_ids)
    return tuple(
        _pullback_idm(
            pb,
            IDMClass.MAJOR_IDM if pb.completion_candle_id in post_bos_pullback_ids else IDMClass.MINOR_IDM,
        )
        for pb in minor.pullbacks
    )


def qualify_retracement(
    candles: tuple[Candle, ...],
    swing: ConfirmedStructuralSwing,
    *,
    range_high: Decimal,
    range_low: Decimal,
    htf_valid_pullback: bool = False,
    attempt_end_candle_id: str | None = None,
) -> RetracementQualification:
    """Evaluate Layer-3 retracement gates without implementing BOS.

    The dealing-range boundaries and HTF evidence are explicit inputs. Missing
    evidence is therefore not repaired or inferred.
    """
    if not isinstance(range_high, Decimal) or not isinstance(range_low, Decimal):
        raise QuarantineError("range boundaries require Decimal")
    if not range_high.is_finite() or not range_low.is_finite() or range_high <= range_low:
        raise QuarantineError("invalid dealing-range boundaries")
    if not isinstance(htf_valid_pullback, bool):
        raise QuarantineError("HTF valid-pullback evidence must be explicit boolean")

    idx = _index(candles)
    if swing.confirmation_candle_id not in idx:
        raise QuarantineError("swing confirmation candle is absent")
    start = idx[swing.confirmation_candle_id]
    end = idx[attempt_end_candle_id] if attempt_end_candle_id is not None else len(candles) - 1
    if end <= start:
        return RetracementQualification(False, Decimal("0"), 0, htf_valid_pullback, False, "NO_POST_CONFIRMATION_RETRACEMENT")

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
        if opposing >= NORMAL_RETRACEMENT_CANDLE_COUNT:
            return RetracementQualification(True, depth, opposing, htf_valid_pullback, False, "STANDARD_EQUILIBRIUM")
        if opposing >= MIN_RETRACEMENT_CANDLE_COUNT and _outlier_condition(window, swing.direction, candles):
            return RetracementQualification(True, depth, opposing, htf_valid_pullback, True, "REDUCED_CANDLE_DISPLACEMENT")
        if len(window) == 1 and _outlier_condition(window, swing.direction, candles):
            return RetracementQualification(True, depth, opposing, htf_valid_pullback, True, "ONE_CANDLE_DISPLACEMENT_OUTLIER")
        return RetracementQualification(False, depth, opposing, htf_valid_pullback, False, "INSUFFICIENT_CANDLE_STRUCTURE")

    if HTF_CONDITIONAL_THRESHOLD <= depth < STANDARD_EQUILIBRIUM_THRESHOLD:
        if htf_valid_pullback:
            return RetracementQualification(True, depth, opposing, True, False, "HTF_VALID_PULLBACK")
        return RetracementQualification(False, depth, opposing, False, False, "HTF_PULLBACK_EVIDENCE_REQUIRED")

    return RetracementQualification(False, depth, opposing, htf_valid_pullback, False, "BELOW_CONDITIONAL_THRESHOLD")


def _outlier_condition(
    window: tuple[Candle, ...],
    direction: PullbackDirection,
    all_candles: tuple[Candle, ...],
) -> bool:
    if not window:
        return False
    exceptional = max(window, key=lambda c: (c.high - c.low))
    exceptional_index = next(i for i, c in enumerate(all_candles) if c.candle_id == exceptional.candle_id)
    preceding = list(all_candles[:exceptional_index])
    if len(preceding) < MIN_OUTLIER_EXTREMES_TAKEN:
        return False
    if direction is PullbackDirection.BULLISH:
        extreme = exceptional.low
        return sum(extreme < c.low or extreme < min(c.open, c.close) for c in preceding) >= MIN_OUTLIER_EXTREMES_TAKEN
    extreme = exceptional.high
    return sum(extreme > c.high or extreme > max(c.open, c.close) for c in preceding) >= MIN_OUTLIER_EXTREMES_TAKEN


def analyze_layer3(
    candles: list[Candle] | tuple[Candle, ...],
    minor: MinorStructureAnalysis,
    *,
    range_high: Decimal | None = None,
    range_low: Decimal | None = None,
    htf_valid_pullback: bool = False,
    post_bos_pullback_ids: frozenset[str] = frozenset(),
    attempt_end_candle_id: str | None = None,
) -> StructuralAnalysis:
    sequence = tuple(candles)
    _validate_inputs(sequence, minor)
    idms = classify_idm(minor, post_bos_pullback_ids=post_bos_pullback_ids)
    if not idms:
        return StructuralAnalysis((), (), None, None, StructuralResolution.NO_EVIDENCE)

    positions = _index(sequence)
    taken_events: list[IDMEvent] = []
    confirmed: list[ConfirmedStructuralSwing] = []
    for idm in idms:
        pb = next(pb for pb in minor.pullbacks if pb.completion_candle_id == idm.pullback_completion_candle_id)
        takeout = _takeout_after(sequence, positions[pb.completion_candle_id], pb)
        updated = IDMEvent(
            idm.idm_class,
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
            swing_price = ref_candle.high if idm.direction is PullbackDirection.BULLISH else ref_candle.low
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
    if active.takeout_candle_id is None:
        return StructuralAnalysis(tuple(taken_events), tuple(confirmed), None, active, StructuralResolution.IDM_ACTIVE)

    swing = next((s for s in reversed(confirmed) if s.confirmation_candle_id == active.takeout_candle_id), None)
    if swing is None:
        raise QuarantineError("IDM takeout has no confirmed structural swing")
    if range_high is None or range_low is None:
        return StructuralAnalysis(tuple(taken_events), tuple(confirmed), None, active, StructuralResolution.IDM_TAKEN)

    qualification = qualify_retracement(
        sequence,
        swing,
        range_high=range_high,
        range_low=range_low,
        htf_valid_pullback=htf_valid_pullback,
        attempt_end_candle_id=attempt_end_candle_id,
    )
    resolution = StructuralResolution.RETRACEMENT_QUALIFIED if qualification.qualified else StructuralResolution.RETRACEMENT_INSUFFICIENT
    return StructuralAnalysis(tuple(taken_events), tuple(confirmed), qualification, active, resolution)


__all__ = [
    "ConfirmedStructuralSwing", "HTF_CONDITIONAL_THRESHOLD", "IDMClass", "IDMEvent",
    "MIN_OUTLIER_EXTREMES_TAKEN", "MIN_RETRACEMENT_CANDLE_COUNT",
    "NORMAL_RETRACEMENT_CANDLE_COUNT", "RetracementQualification", "STANDARD_EQUILIBRIUM_THRESHOLD",
    "StructuralAnalysis", "StructuralResolution", "analyze_layer3", "classify_idm", "qualify_retracement",
]
