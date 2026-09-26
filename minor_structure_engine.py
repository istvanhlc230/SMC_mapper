"""Layer 2 sequential/minor-structure engine.

Consumes only Layer 1 candle observations and owns:
- Candle-Level Valid Pullback formation
- Verified Pullback Extreme
- pullback-derived liquidity reference
- active pullback pointer

It does not define or implement IDM, BOS, CHoCH, POI, or structural retracement.
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
    is_outside_bar,
    classify_breach,
)


class PullbackDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class LiquiditySide(str, Enum):
    SELL_SIDE = "SELL_SIDE"
    BUY_SIDE = "BUY_SIDE"


@dataclass(frozen=True, slots=True)
class VerifiedPullbackExtreme:
    direction: PullbackDirection
    price: Decimal
    source_candle_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.direction, PullbackDirection):
            raise QuarantineError("invalid pullback direction")
        if not isinstance(self.price, Decimal) or not self.price.is_finite():
            raise QuarantineError("pullback extreme requires finite Decimal")
        if not isinstance(self.source_candle_id, str) or not self.source_candle_id:
            raise QuarantineError("pullback extreme requires source candle ID")


@dataclass(frozen=True, slots=True)
class PullbackDerivedLiquidityReference:
    side: LiquiditySide
    price: Decimal
    source_candle_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.side, LiquiditySide):
            raise QuarantineError("invalid liquidity side")
        if not isinstance(self.price, Decimal) or not self.price.is_finite():
            raise QuarantineError("liquidity reference requires finite Decimal")
        if not isinstance(self.source_candle_id, str) or not self.source_candle_id:
            raise QuarantineError("liquidity reference requires source candle ID")


@dataclass(frozen=True, slots=True)
class CandleLevelValidPullback:
    direction: PullbackDirection
    reference_candle_id: str
    start_candle_id: str
    completion_candle_id: str
    extreme: VerifiedPullbackExtreme
    liquidity_reference: PullbackDerivedLiquidityReference

    def __post_init__(self) -> None:
        ids = (
            self.reference_candle_id,
            self.start_candle_id,
            self.completion_candle_id,
        )
        if any(not isinstance(x, str) or not x for x in ids):
            raise QuarantineError("pullback event requires non-empty candle IDs")
        if self.extreme.direction is not self.direction:
            raise QuarantineError("pullback extreme direction mismatch")
        expected_side = (
            LiquiditySide.SELL_SIDE
            if self.direction is PullbackDirection.BULLISH
            else LiquiditySide.BUY_SIDE
        )
        if self.liquidity_reference.side is not expected_side:
            raise QuarantineError("pullback liquidity side mismatch")
        if self.liquidity_reference.price != self.extreme.price:
            raise QuarantineError("liquidity reference must derive from verified extreme")
        if self.liquidity_reference.source_candle_id != self.extreme.source_candle_id:
            raise QuarantineError("liquidity reference provenance must match verified extreme")


@dataclass(frozen=True, slots=True)
class ActivePullbackState:
    pullback: CandleLevelValidPullback | None

    @property
    def reference(self) -> PullbackDerivedLiquidityReference | None:
        return None if self.pullback is None else self.pullback.liquidity_reference


@dataclass(frozen=True, slots=True)
class MinorStructureAnalysis:
    pullbacks: tuple[CandleLevelValidPullback, ...]
    active: ActivePullbackState

    def __post_init__(self) -> None:
        object.__setattr__(self, "pullbacks", tuple(self.pullbacks))
        if self.pullbacks:
            if self.active.pullback is not self.pullbacks[-1]:
                raise QuarantineError("active pullback must be the newest completed pullback")


def _validate_candles(candles: tuple[Candle, ...]) -> None:
    if any(not isinstance(c, Candle) for c in candles):
        raise QuarantineError("Layer 2 accepts only Layer 1 Candle objects")
    ids = [c.candle_id for c in candles]
    if len(ids) != len(set(ids)):
        raise QuarantineError("duplicate candle IDs are not allowed")


def _reference_is_bullish_continuation(reference: Candle, next_candle: Candle) -> bool:
    return (
        reference.close > reference.open
        and next_candle.high > reference.high
        and next_candle.low >= reference.low
    )


def _reference_is_bearish_continuation(reference: Candle, next_candle: Candle) -> bool:
    return (
        reference.close < reference.open
        and next_candle.low < reference.low
        and next_candle.high <= reference.high
    )


def _reference_breach(candle: Candle, reference: Candle, direction: Direction) -> bool:
    level = reference.low if direction is Direction.DOWN else reference.high
    role = "REFERENCE_LOW" if direction is Direction.DOWN else "REFERENCE_HIGH"
    observation = classify_breach(
        candle,
        ExtremeReference(level, reference.candle_id, role),
        direction,
    )
    return observation.is_break


def _build_pullback(
    direction: PullbackDirection,
    reference: Candle,
    start_index: int,
    completion_index: int,
    candles: tuple[Candle, ...],
) -> CandleLevelValidPullback:
    window = candles[start_index : completion_index + 1]
    if direction is PullbackDirection.BULLISH:
        price = min(c.low for c in window)
        source = next(c.candle_id for c in window if c.low == price)
        side = LiquiditySide.SELL_SIDE
    else:
        price = max(c.high for c in window)
        source = next(c.candle_id for c in window if c.high == price)
        side = LiquiditySide.BUY_SIDE

    extreme = VerifiedPullbackExtreme(direction, price, source)
    liquidity = PullbackDerivedLiquidityReference(side, price, source)
    return CandleLevelValidPullback(
        direction=direction,
        reference_candle_id=reference.candle_id,
        start_candle_id=candles[start_index].candle_id,
        completion_candle_id=candles[completion_index].candle_id,
        extreme=extreme,
        liquidity_reference=liquidity,
    )


def detect_valid_pullbacks(
    candles: list[Candle] | tuple[Candle, ...],
    direction: PullbackDirection,
) -> MinorStructureAnalysis:
    """Detect completed candle-level pullbacks from an ordered OHLC sequence.

    A same-candle takeout-and-completion requires historical intrabar ordering.
    Aggregate OHLC Outside Bars expose that ordering as UNAVAILABLE in Layer 1,
    so such a candle cannot by itself confirm completion; the candidate remains
    open for a later, independently observable completed-candle break.
    """
    sequence = tuple(candles)
    _validate_candles(sequence)
    if not isinstance(direction, PullbackDirection):
        raise QuarantineError("invalid pullback direction")
    if len(sequence) < 2:
        return MinorStructureAnalysis((), ActivePullbackState(None))

    completed: list[CandleLevelValidPullback] = []

    for ref_index in range(len(sequence) - 1):
        reference = sequence[ref_index]
        continuation = sequence[ref_index + 1]

        if direction is PullbackDirection.BULLISH:
            if not _reference_is_bullish_continuation(reference, continuation):
                continue
            start_index = None
            for i in range(ref_index + 1, len(sequence)):
                low_taken = _reference_breach(sequence[i], reference, Direction.DOWN)
                high_broken = _reference_breach(sequence[i], reference, Direction.UP)
                if start_index is None:
                    if low_taken:
                        # A single aggregate Outside Bar cannot prove low-before-high.
                        if high_broken and is_outside_bar(sequence[i], reference):
                            continue
                        start_index = i
                    continue
                if high_broken:
                    completed.append(_build_pullback(direction, reference, start_index, i, sequence))
                    break
        else:
            if not _reference_is_bearish_continuation(reference, continuation):
                continue
            start_index = None
            for i in range(ref_index + 1, len(sequence)):
                high_taken = _reference_breach(sequence[i], reference, Direction.UP)
                low_broken = _reference_breach(sequence[i], reference, Direction.DOWN)
                if start_index is None:
                    if high_taken:
                        if low_broken and is_outside_bar(sequence[i], reference):
                            continue
                        start_index = i
                    continue
                if low_broken:
                    completed.append(_build_pullback(direction, reference, start_index, i, sequence))
                    break

    completed.sort(key=lambda p: sequence.index(next(c for c in sequence if c.candle_id == p.completion_candle_id)))
    active = ActivePullbackState(completed[-1] if completed else None)
    return MinorStructureAnalysis(tuple(completed), active)


__all__ = [
    "ActivePullbackState",
    "CandleLevelValidPullback",
    "LiquiditySide",
    "MinorStructureAnalysis",
    "PullbackDerivedLiquidityReference",
    "PullbackDirection",
    "VerifiedPullbackExtreme",
    "detect_valid_pullbacks",
]
