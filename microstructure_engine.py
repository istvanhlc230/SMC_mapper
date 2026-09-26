"""Hermetic Layer 1 microstructure primitives for SMC_Mapper.

This module owns only candle/OHLC-level geometry and observability.  It does not
import or name any Layer 2+ SMC concept.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from enum import Enum
import ast
import hashlib
import json


class QuarantineError(ValueError):
    """Raised when Layer 1 input cannot be safely represented."""


class Direction(str, Enum):
    UP = "UP"
    DOWN = "DOWN"


class SequenceStatus(str, Enum):
    OBSERVED = "OBSERVED"
    ASSUMED = "ASSUMED"
    UNAVAILABLE = "UNAVAILABLE"


class BreachMode(str, Enum):
    NONE = "NONE"
    EQUAL = "EQUAL"
    WICK_ONLY = "WICK_ONLY"
    BODY = "BODY"
    CLOSE = "CLOSE"


class TrendDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    UNDEFINED = "UNDEFINED"


def _decimal(value: Decimal | int | str) -> Decimal:
    """Return a finite Decimal; native floats are deliberately rejected."""
    if isinstance(value, bool) or isinstance(value, float):
        raise QuarantineError("Layer 1 requires Decimal/int/string numeric values; float is forbidden")
    if not isinstance(value, (Decimal, int, str)):
        raise QuarantineError(f"unsupported numeric type: {type(value).__name__}")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise QuarantineError("invalid decimal value") from exc
    if not result.is_finite():
        raise QuarantineError("NaN and Infinity are forbidden")
    return result


def _require_id(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise QuarantineError(f"{name} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class Candle:
    candle_id: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "candle_id", _require_id(self.candle_id, "candle_id"))
        for name in ("open", "high", "low", "close"):
            object.__setattr__(self, name, _decimal(getattr(self, name)))
        if self.high < self.low:
            raise QuarantineError("high must be >= low")
        if not (self.low <= self.open <= self.high):
            raise QuarantineError("open must be inside [low, high]")
        if not (self.low <= self.close <= self.high):
            raise QuarantineError("close must be inside [low, high]")


@dataclass(frozen=True, slots=True)
class ExtremeReference:
    price: Decimal
    candle_id: str
    role: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "price", _decimal(self.price))
        object.__setattr__(self, "candle_id", _require_id(self.candle_id, "candle_id"))
        object.__setattr__(self, "role", _require_id(self.role, "role"))


@dataclass(frozen=True, slots=True)
class BreachObservation:
    candle_id: str
    direction: Direction
    reference: ExtremeReference
    mode: BreachMode
    physical: bool
    body: bool
    close: bool

    def __post_init__(self) -> None:
        _require_id(self.candle_id, "candle_id")
        if not isinstance(self.direction, Direction) or not isinstance(self.mode, BreachMode):
            raise QuarantineError("breach direction and mode must use canonical enums")
        if self.mode == BreachMode.EQUAL and self.physical:
            raise QuarantineError("equality cannot be a physical breach")
        if self.mode == BreachMode.NONE and any((self.physical, self.body, self.close)):
            raise QuarantineError("NONE breach cannot contain breach flags")
        if self.mode == BreachMode.WICK_ONLY and not self.physical:
            raise QuarantineError("wick-only breach requires physical penetration")
        if self.mode == BreachMode.BODY and not (self.physical and self.body):
            raise QuarantineError("body breach requires physical penetration and body endpoint breach")
        if self.mode == BreachMode.CLOSE and not (self.physical and self.body and self.close):
            raise QuarantineError("close breach requires physical, body and close penetration")

    @property
    def is_break(self) -> bool:
        return self.physical


@dataclass(frozen=True, slots=True)
class EqualityObservation:
    kind: str
    left_candle_id: str
    right_candle_id: str
    price: Decimal

    def __post_init__(self) -> None:
        if self.kind not in {"EQH", "EQL"}:
            raise QuarantineError("equality kind must be EQH or EQL")
        _require_id(self.left_candle_id, "left_candle_id")
        _require_id(self.right_candle_id, "right_candle_id")
        object.__setattr__(self, "price", _decimal(self.price))


@dataclass(frozen=True, slots=True)
class InsideBarObservation:
    candle_id: str
    mother_candle_id: str
    strict: bool


@dataclass(frozen=True, slots=True)
class SequenceEvidence:
    status: SequenceStatus
    sequence: tuple[str, ...] = ()
    source_candle_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.status, SequenceStatus):
            raise QuarantineError("sequence status must use the canonical enum")
        object.__setattr__(self, "sequence", tuple(self.sequence))
        object.__setattr__(self, "source_candle_ids", tuple(self.source_candle_ids))
        if any(not isinstance(x, str) or not x for x in self.sequence + self.source_candle_ids):
            raise QuarantineError("sequence evidence identifiers must be non-empty strings")
        if self.status == SequenceStatus.UNAVAILABLE and self.sequence:
            raise QuarantineError("UNAVAILABLE sequence cannot contain an inferred sequence")


@dataclass(frozen=True, slots=True)
class OutsideBarObservation:
    candle_id: str
    reference_candle_id: str
    high_breach: BreachObservation
    low_breach: BreachObservation
    sequence_evidence: SequenceEvidence

    def __post_init__(self) -> None:
        _require_id(self.candle_id, "candle_id")
        _require_id(self.reference_candle_id, "reference_candle_id")
        if not (self.high_breach.physical and self.low_breach.physical):
            raise QuarantineError("Outside Bar requires physical expansion beyond both extremes")
        if self.high_breach.candle_id != self.candle_id or self.low_breach.candle_id != self.candle_id:
            raise QuarantineError("Outside Bar breach provenance must point to the creating candle")


@dataclass(frozen=True, slots=True)
class TrendObservation:
    direction: TrendDirection
    protected_high: ExtremeReference | None
    protected_low: ExtremeReference | None

    def __post_init__(self) -> None:
        if not isinstance(self.direction, TrendDirection):
            raise QuarantineError("trend direction must use the canonical enum")


@dataclass(frozen=True, slots=True)
class EvidenceEnvelope:
    """Immutable, content-addressed Layer 1 evidence envelope."""

    kind: str
    source_candle_ids: tuple[str, ...]
    payload: tuple[tuple[str, str], ...]
    status: SequenceStatus = SequenceStatus.OBSERVED
    evidence_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.status, SequenceStatus):
            raise QuarantineError("evidence status must use the canonical enum")
        object.__setattr__(self, "source_candle_ids", tuple(self.source_candle_ids))
        payload = tuple(self.payload)
        if any(
            not isinstance(item, tuple) or len(item) != 2
            or not isinstance(item[0], str) or not isinstance(item[1], str)
            for item in payload
        ):
            raise QuarantineError("evidence payload must be an immutable tuple of string pairs")
        object.__setattr__(self, "payload", tuple(sorted(payload)))
        _require_id(self.kind, "kind")
        if any(not isinstance(x, str) or not x for x in self.source_candle_ids):
            raise QuarantineError("evidence source IDs must be non-empty strings")
        canonical = json.dumps(
            {
                "kind": self.kind,
                "source_candle_ids": self.source_candle_ids,
                "payload": self.payload,
                "status": self.status.value,
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
        object.__setattr__(self, "evidence_id", digest)
        if self.evidence_id != hashlib.sha256(canonical).hexdigest():
            raise QuarantineError("evidence ID validation failed")


def classify_breach(candle: Candle, reference: ExtremeReference, direction: Direction) -> BreachObservation:
    """Classify a completed-candle relation without inferring an intrabar path."""
    ref = reference.price
    if direction is Direction.UP:
        extreme = candle.high
        body_end = max(candle.open, candle.close)
        close_breach = candle.close > ref
        body_breach = body_end > ref
        physical = extreme > ref
        equal = extreme == ref
    else:
        extreme = candle.low
        body_end = min(candle.open, candle.close)
        close_breach = candle.close < ref
        body_breach = body_end < ref
        physical = extreme < ref
        equal = extreme == ref

    if equal:
        mode = BreachMode.EQUAL
    elif not physical:
        mode = BreachMode.NONE
    elif close_breach:
        mode = BreachMode.CLOSE
    elif body_breach:
        mode = BreachMode.BODY
    else:
        mode = BreachMode.WICK_ONLY

    return BreachObservation(
        candle_id=candle.candle_id,
        direction=direction,
        reference=reference,
        mode=mode,
        physical=physical,
        body=body_breach,
        close=close_breach,
    )


def is_inside_bar(candle: Candle, mother: Candle) -> bool:
    return candle.high < mother.high and candle.low > mother.low


def inside_bar(candle: Candle, mother: Candle) -> InsideBarObservation | None:
    if not is_inside_bar(candle, mother):
        return None
    return InsideBarObservation(candle.candle_id, mother.candle_id, True)


def is_outside_bar(candle: Candle, reference: Candle) -> bool:
    return candle.high > reference.high and candle.low < reference.low


def outside_bar(candle: Candle, reference: Candle, sequence: SequenceEvidence | None = None) -> OutsideBarObservation | None:
    if not is_outside_bar(candle, reference):
        return None
    high_ref = ExtremeReference(reference.high, reference.candle_id, "REFERENCE_HIGH")
    low_ref = ExtremeReference(reference.low, reference.candle_id, "REFERENCE_LOW")
    evidence = sequence if sequence is not None else SequenceEvidence(SequenceStatus.UNAVAILABLE)
    return OutsideBarObservation(
        candle_id=candle.candle_id,
        reference_candle_id=reference.candle_id,
        high_breach=classify_breach(candle, high_ref, Direction.UP),
        low_breach=classify_breach(candle, low_ref, Direction.DOWN),
        sequence_evidence=evidence,
    )


def equal_high(left: Candle, right: Candle) -> EqualityObservation | None:
    if left.high != right.high:
        return None
    return EqualityObservation("EQH", left.candle_id, right.candle_id, left.high)


def equal_low(left: Candle, right: Candle) -> EqualityObservation | None:
    if left.low != right.low:
        return None
    return EqualityObservation("EQL", left.candle_id, right.candle_id, left.low)


def transfer_high_reference(active: ExtremeReference, candle: Candle) -> ExtremeReference:
    if candle.high != active.price:
        return active
    return ExtremeReference(candle.high, candle.candle_id, "ACTIVE_HIGH")


def transfer_low_reference(active: ExtremeReference, candle: Candle) -> ExtremeReference:
    if candle.low != active.price:
        return active
    return ExtremeReference(candle.low, candle.candle_id, "ACTIVE_LOW")


def candle_trend(previous: Candle, current: Candle) -> TrendObservation:
    """Return the candle-level directional observation from OHLC only."""
    if current.high > previous.high and current.low >= previous.low:
        return TrendObservation(TrendDirection.BULLISH, None, ExtremeReference(previous.low, previous.candle_id, "PROTECTED_LOW"))
    if current.low < previous.low and current.high <= previous.high:
        return TrendObservation(TrendDirection.BEARISH, ExtremeReference(previous.high, previous.candle_id, "PROTECTED_HIGH"), None)
    return TrendObservation(TrendDirection.UNDEFINED, None, None)


def validate_hermetic_layer1(source: str) -> tuple[str, ...]:
    """Positive AST import boundary plus downstream-vocabulary guard for tests."""
    tree = ast.parse(source)
    allowed_modules = {
        "__future__", "ast", "dataclasses", "decimal", "enum", "hashlib", "json"
    }
    downstream_names = {
        "IDM", "BOS", "CHoCH", "CHOCH", "Pullback", "PULLBACK",
        "MajorStructure", "MinorStructure", "OrderBlock", "FVG", "POI", "RR",
    }
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in allowed_modules:
                    violations.append(f"IMPORT:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in allowed_modules:
                violations.append(f"IMPORT:{node.module}")
        elif isinstance(node, ast.Name) and node.id in downstream_names:
            violations.append(node.id)
        elif isinstance(node, ast.Attribute) and node.attr in downstream_names:
            violations.append(node.attr)
    return tuple(sorted(set(violations)))


__all__ = [
    "BreachMode", "BreachObservation", "Candle", "Direction", "EqualityObservation",
    "EvidenceEnvelope", "ExtremeReference", "InsideBarObservation", "QuarantineError",
    "SequenceEvidence", "SequenceStatus", "TrendDirection", "TrendObservation",
    "OutsideBarObservation", "candle_trend", "classify_breach", "equal_high", "equal_low",
    "inside_bar", "is_inside_bar", "is_outside_bar", "outside_bar", "transfer_high_reference",
    "transfer_low_reference", "validate_hermetic_layer1",
]
