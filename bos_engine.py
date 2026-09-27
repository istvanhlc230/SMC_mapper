"""Layer 4 Break of Structure mechanics.

Consumes Layer 3 structural qualification and confirmed-swing state.
Owns only physical continuation-break detection and VALID_BOS classification.
It does not recompute Layer 3 retracement gates and does not implement CHoCH,
POI, RR, targets, or trade management.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from microstructure_engine import BreachMode, Candle, Direction, ExtremeReference, QuarantineError, classify_breach
from structural_engine import IDMOrigin, PullbackDirection, StructuralAnalysis


class BOSResolution(str, Enum):
    NO_EVIDENCE = "NO_EVIDENCE"
    NO_STRUCTURAL_BREAK = "NO_STRUCTURAL_BREAK"
    MAJOR_IDM_SWEEP = "MAJOR_IDM_SWEEP"
    IMPULSE_EXTENSION = "IMPULSE_EXTENSION"
    VALID_BOS = "VALID_BOS"


@dataclass(frozen=True, slots=True)
class StructuralSwingBreak:
    direction: PullbackDirection
    reference_price: Decimal
    reference_candle_id: str
    break_candle_id: str
    mode: BreachMode

    def __post_init__(self) -> None:
        if not isinstance(self.direction, PullbackDirection):
            raise QuarantineError("invalid structural-break direction")
        if not isinstance(self.reference_price, Decimal) or not self.reference_price.is_finite():
            raise QuarantineError("structural-break price requires finite Decimal")
        for value, name in ((self.reference_candle_id, "reference_candle_id"), (self.break_candle_id, "break_candle_id")):
            if not isinstance(value, str) or not value:
                raise QuarantineError(f"structural break requires {name}")
        if not isinstance(self.mode, BreachMode) or self.mode is BreachMode.EQUAL:
            raise QuarantineError("structural break requires a physical breach mode")


@dataclass(frozen=True, slots=True)
class BOSAnalysis:
    resolution: BOSResolution
    structural_break: StructuralSwingBreak | None
    valid_bos: bool
    idm_taken: bool
    retracement_qualified: bool

    def __post_init__(self) -> None:
        if not isinstance(self.resolution, BOSResolution):
            raise QuarantineError("invalid BOS resolution")
        if not all(isinstance(v, bool) for v in (self.valid_bos, self.idm_taken, self.retracement_qualified)):
            raise QuarantineError("BOS flags must be boolean")
        if self.valid_bos != (self.resolution is BOSResolution.VALID_BOS):
            raise QuarantineError("VALID_BOS flag and resolution disagree")
        if self.resolution in {BOSResolution.VALID_BOS, BOSResolution.IMPULSE_EXTENSION} and self.structural_break is None:
            raise QuarantineError("classified BOS outcome requires structural break")


def _positions(candles: tuple[Candle, ...]) -> dict[str, int]:
    if any(not isinstance(c, Candle) for c in candles):
        raise QuarantineError("Layer 4 accepts only Layer 1 Candle objects")
    result = {c.candle_id: i for i, c in enumerate(candles)}
    if len(result) != len(candles):
        raise QuarantineError("duplicate candle IDs are not allowed")
    return result


def _active_confirmed_swing(structural: StructuralAnalysis):
    active = structural.active_idm
    if active is None or active.takeout_candle_id is None:
        return None
    for swing in reversed(structural.confirmed_swings):
        if swing.confirmation_candle_id == active.takeout_candle_id:
            return swing
    raise QuarantineError("IDM_TAKEN has no matching CONFIRMED_STRUCTURAL_SWING")


def _break(candle: Candle, price: Decimal, direction: PullbackDirection, source_id: str):
    side = Direction.UP if direction is PullbackDirection.BULLISH else Direction.DOWN
    observation = classify_breach(
        candle, ExtremeReference(price, source_id, "STRUCTURAL_REFERENCE"), side
    )
    if not observation.is_break:
        return None
    return StructuralSwingBreak(direction, price, source_id, candle.candle_id, observation.mode)


def _major_boundary_sweep(candle: Candle, active):
    side = Direction.UP if active.direction is PullbackDirection.BULLISH else Direction.DOWN
    observation = classify_breach(
        candle, ExtremeReference(active.reference_price, active.source_candle_id, "MAJOR_IDM"), side
    )
    return observation.is_break


def detect_bos(
    candles: list[Candle] | tuple[Candle, ...],
    structural: StructuralAnalysis,
    *,
    execution_start_candle_id: str,
    break_candle_id: str | None = None,
) -> BOSAnalysis:
    """Classify a continuation break from validated Layer-3 state.

    Layer 4 consumes Layer-3 retracement qualification and never reconstructs
    its depth, candle-count, displacement, or HTF gates. The execution start
    is explicit provenance and must occur after the IDM confirmation. A Major
    IDM boundary sweep is reported as MAJOR_IDM_SWEEP and never creates a
    Confirmed Structural Swing or VALID_BOS.
    """
    sequence = tuple(candles)
    positions = _positions(sequence)
    if not isinstance(structural, StructuralAnalysis):
        raise QuarantineError("Layer 4 requires Layer 3 StructuralAnalysis")
    if execution_start_candle_id not in positions:
        raise QuarantineError("execution-start candle is absent")

    active = structural.active_idm
    retracement_qualified = bool(structural.retracement and structural.retracement.qualified)
    if active is None:
        return BOSAnalysis(BOSResolution.NO_EVIDENCE, None, False, False, retracement_qualified)

    start = positions[execution_start_candle_id]
    if structural.retracement is not None:
        if structural.retracement.qualification_end_candle_id not in positions:
            raise QuarantineError("Layer-3 qualification-end provenance is absent from Layer-4 sequence")
        if positions[structural.retracement.qualification_end_candle_id] != start:
            raise QuarantineError("execution-start candle must equal Layer-3 qualification-end provenance")

    # A governing Protected-External-Boundary Major IDM is not a BOS swing
    # candidate. Its sweep is handled by the structural/CHoCH lifecycle; Layer 4
    # must not manufacture a Confirmed Structural Swing from it.
    if active.origin is IDMOrigin.PROTECTED_EXTERNAL_BOUNDARY:
        return BOSAnalysis(
            BOSResolution.MAJOR_IDM_SWEEP if active.takeout_candle_id is not None else BOSResolution.NO_EVIDENCE,
            None,
            False,
            active.takeout_candle_id is not None,
            retracement_qualified,
        )

    swing = _active_confirmed_swing(structural)
    if swing is None:
        return BOSAnalysis(BOSResolution.NO_EVIDENCE, None, False, False, retracement_qualified)
    if active.takeout_candle_id is None or positions[active.takeout_candle_id] >= start:
        raise QuarantineError("execution phase must begin after IDM_TAKEN / confirmed swing")

    if break_candle_id is not None:
        if break_candle_id not in positions or positions[break_candle_id] <= start:
            raise QuarantineError("break candle must occur after execution-start boundary")
        candidates = (sequence[positions[break_candle_id]],)
    else:
        candidates = sequence[start + 1:]

    structural_break = None
    for candidate in candidates:
        structural_break = _break(candidate, swing.price, swing.direction, swing.source_candle_id)
        if structural_break is not None:
            break
    if structural_break is None:
        return BOSAnalysis(BOSResolution.NO_STRUCTURAL_BREAK, None, False, True, retracement_qualified)
    if not retracement_qualified:
        return BOSAnalysis(BOSResolution.IMPULSE_EXTENSION, structural_break, False, True, False)
    return BOSAnalysis(BOSResolution.VALID_BOS, structural_break, True, True, True)


__all__ = ["BOSAnalysis", "BOSResolution", "StructuralSwingBreak", "detect_bos"]