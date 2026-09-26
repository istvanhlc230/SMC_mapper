"""Layer 2 sequential/minor-structure engine.

Layer 2 consumes only Layer 1 candle observations and owns:
- Candle-Level Valid Pullback formation
- Verified Pullback Extreme
- pullback-derived liquidity reference
- active pullback pointer
- explicit unresolved/pending state when Layer 1 sequence evidence is unavailable

It does not define or implement IDM, BOS, CHoCH, POI, or structural retracement.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from microstructure_engine import (
    Candle,
    QuarantineError,
    SequenceStatus,
    outside_bar,
)


class PullbackDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class LiquiditySide(str, Enum):
    SELL_SIDE = "SELL_SIDE"
    BUY_SIDE = "BUY_SIDE"


class PullbackResolution(str, Enum):
    NONE = "NONE"
    CONFIRMED = "CONFIRMED"
    PENDING_UNAVAILABLE_SEQUENCE = "PENDING_UNAVAILABLE_SEQUENCE"


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
            raise QuarantineError("pullback liquidity provenance must match verified extreme")


@dataclass(frozen=True, slots=True)
class PendingPullback:
    direction: PullbackDirection
    reference_candle_id: str
    start_candle_id: str
    reason: PullbackResolution

    def __post_init__(self) -> None:
        if not isinstance(self.direction, PullbackDirection):
            raise QuarantineError("invalid pending pullback direction")
        for value, name in (
            (self.reference_candle_id, "reference_candle_id"),
            (self.start_candle_id, "start_candle_id"),
        ):
            if not isinstance(value, str) or not value:
                raise QuarantineError(f"pending pullback requires {name}")
        if self.reason is not PullbackResolution.PENDING_UNAVAILABLE_SEQUENCE:
            raise QuarantineError("pending pullback requires unavailable-sequence reason")


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
    pending: tuple[PendingPullback, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "pullbacks", tuple(self.pullbacks))
        object.__setattr__(self, "pending", tuple(self.pending))
        if self.pullbacks:
            if self.active.pullback is not self.pullbacks[-1]:
                raise QuarantineError("active pullback must be the newest completed pullback")
        if any(not isinstance(p, PendingPullback) for p in self.pending):
            raise QuarantineError("pending state must contain only PendingPullback objects")

    @property
    def resolution(self) -> PullbackResolution:
        if self.pullbacks:
            return PullbackResolution.CONFIRMED
        if self.pending:
            return PullbackResolution.PENDING_UNAVAILABLE_SEQUENCE
        return PullbackResolution.NONE


def _validate_candles(candles: tuple[Candle, ...]) -> None:
    if any(not isinstance(c, Candle) for c in candles):
        raise QuarantineError("Layer 2 accepts only Layer 1 Candle objects")
    ids = [c.candle_id for c in candles]
    if len(ids) != len(set(ids)):
        raise QuarantineError("duplicate candle IDs are not allowed")


def _is_bullish(candle: Candle) -> bool:
    return candle.close > candle.open


def _is_bearish(candle: Candle) -> bool:
    return candle.close < candle.open


def _outside_sequence_unavailable(candle: Candle, reference: Candle) -> bool:
    observation = outside_bar(candle, reference)
    return (
        observation is not None
        and observation.sequence_evidence.status is SequenceStatus.UNAVAILABLE
    )


def _bullish_continuation(candle: Candle, reference: Candle) -> bool:
    return (
        _is_bullish(reference)
        and candle.high > reference.high
        and candle.low >= reference.low
    )


def _bearish_continuation(candle: Candle, reference: Candle) -> bool:
    return (
        _is_bearish(reference)
        and candle.low < reference.low
        and candle.high <= reference.high
    )


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
    """Detect completed Layer-2 candle-level valid pullbacks.

    The engine is stateful over the ordered OHLC sequence:
    1. establish the applicable previous bullish/bearish reference candle from
       a confirmed candle-level continuation;
    2. require the reference extreme to be taken first;
    3. keep the same reference while the pullback is open;
    4. require the same reference's opposing extreme to be broken after the
       pullback starts;
    5. when aggregate OHLC cannot prove the required intrabar order for an
       Outside Bar, keep the candidate explicitly pending rather than
       manufacturing an order.

    Layer-2 does not reinterpret UNAVAILABLE as OBSERVED or ASSUMED.
    """
    sequence = tuple(candles)
    _validate_candles(sequence)
    if not isinstance(direction, PullbackDirection):
        raise QuarantineError("invalid pullback direction")
    if len(sequence) < 2:
        return MinorStructureAnalysis((), ActivePullbackState(None))

    completed: list[CandleLevelValidPullback] = []
    pending: list[PendingPullback] = []
    reference: Candle | None = None
    start_index: int | None = None

    for i, candle in enumerate(sequence[1:], start=1):
        previous = sequence[i - 1]

        if reference is None:
            if (
                direction is PullbackDirection.BULLISH
                and _bullish_continuation(candle, previous)
            ) or (
                direction is PullbackDirection.BEARISH
                and _bearish_continuation(candle, previous)
            ):
                reference = previous
            continue

        if start_index is None:
            took_reference_extreme = (
                candle.low < reference.low
                if direction is PullbackDirection.BULLISH
                else candle.high > reference.high
            )

            if took_reference_extreme:
                start_index = i
                if _outside_sequence_unavailable(candle, reference):
                    pending.append(
                        PendingPullback(
                            direction,
                            reference.candle_id,
                            candle.candle_id,
                            PullbackResolution.PENDING_UNAVAILABLE_SEQUENCE,
                        )
                    )
                continue

            if (
                direction is PullbackDirection.BULLISH
                and _bullish_continuation(candle, reference)
            ) or (
                direction is PullbackDirection.BEARISH
                and _bearish_continuation(candle, reference)
            ):
                reference = candle
            continue

        completion_breach = (
            candle.high > reference.high
            if direction is PullbackDirection.BULLISH
            else candle.low < reference.low
        )

        if not completion_breach:
            continue

        completion_ambiguous = _outside_sequence_unavailable(candle, reference)
        if completion_ambiguous:
            pending.append(
                PendingPullback(
                    direction,
                    reference.candle_id,
                    sequence[start_index].candle_id,
                    PullbackResolution.PENDING_UNAVAILABLE_SEQUENCE,
                )
            )
            continue

        completed.append(
            _build_pullback(direction, reference, start_index, i, sequence)
        )
        start_index = None

        # The completion candle becomes the next reference only when it is a
        # bullish/bearish candle in the prevailing direction. Otherwise the
        # next qualifying directional continuation establishes the next
        # reference. This mirrors the source definition's "previous bullish /
        # previous bearish candle" wording without inventing a pivot.
        if (
            direction is PullbackDirection.BULLISH
            and _is_bullish(candle)
        ) or (
            direction is PullbackDirection.BEARISH
            and _is_bearish(candle)
        ):
            reference = candle
        else:
            # The same previous directional candle remains the applicable
            # reference until a new directional continuation establishes a
            # newer reference. Completion by a non-directional candle does
            # not invent a new reference candle.
            pass

    # A pending candidate is meaningful only if it is still unresolved.
    # Remove stale pending records once a later observable completion confirms
    # the same candidate.
    unresolved: list[PendingPullback] = []
    completed_keys = {
        (p.reference_candle_id, p.start_candle_id)
        for p in completed
    }
    seen_pending: set[tuple[str, str]] = set()
    for p in pending:
        key = (p.reference_candle_id, p.start_candle_id)
        if key not in completed_keys and key not in seen_pending:
            unresolved.append(p)
            seen_pending.add(key)

    active = ActivePullbackState(completed[-1] if completed else None)
    return MinorStructureAnalysis(tuple(completed), active, tuple(unresolved))


__all__ = [
    "ActivePullbackState",
    "CandleLevelValidPullback",
    "LiquiditySide",
    "MinorStructureAnalysis",
    "PendingPullback",
    "PullbackDerivedLiquidityReference",
    "PullbackDirection",
    "PullbackResolution",
    "VerifiedPullbackExtreme",
    "detect_valid_pullbacks",
]
