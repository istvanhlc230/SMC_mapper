"""Layer-8 implementation orchestrator for the canonical SMC engine chain.

The analyzer is an integration layer. It consumes the existing Layer-1 through
Layer-5 engines and represents their results without redefining their semantic
rules. Missing canonical inputs fail closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum, auto
from typing import Any, List, Optional, Tuple

from microstructure_engine import Candle
import minor_structure_engine as minor
import structural_engine as structural
import bos_engine as bos
import choch_engine as choch


class LifecycleState(Enum):
    BOOTSTRAP = auto()
    CONFIRMATION_LOCKED = auto()
    CONFIRMED_RANGE = auto()
    POST_BOS = auto()
    POST_CHOCH = auto()


class DetectionEvent(Enum):
    NO_EVENT_INTERNAL_PB = auto()
    MINOR_IDM_EVENT = auto()
    EXT_CONT_BREAK = auto()
    EXT_OPP_BREAK = auto()
    MAJOR_IDM_EVENT = auto()
    NEW_SVP_QUALIFIED = auto()


class ProcessCondition(Enum):
    IDM_TAKEN = auto()
    STRUCTURAL_RETRACEMENT_EVALUATION = auto()
    CONFIRMATION_GATE_UNLOCKED = auto()


class StructuralFact(Enum):
    SWING_CANDIDATE = auto()
    CONFIRMED_STRUCTURAL_SWING = auto()
    STRUCTURAL_SWING_BREAK = auto()
    SWING_REVOKED = auto()
    PULLBACK_REFERENCE_SHIFT = auto()


class ClassificationOutcome(Enum):
    VALID_BOS = auto()
    IMPULSE_EXTENSION = auto()
    MAJOR_IDM_SWEEP = auto()
    CHoCH_ELIGIBLE = auto()
    CHoCH_CONFIRMED = auto()


class FirstBOSRetracementBaselineStatus(Enum):
    AVAILABLE = auto()
    UNSPECIFIED_CANONICAL_INPUT = auto()


class SMCError(Exception):
    pass


class DataNormalizationError(SMCError):
    pass


class InsufficientHistoryError(SMCError):
    pass


class AnalyzerContractError(SMCError):
    pass


class MarketDataNormalizer:
    """External-input adapter that emits canonical Layer-1 Candle objects."""

    @staticmethod
    def normalize(raw_data: List[dict]) -> List[Candle]:
        if not isinstance(raw_data, list):
            raise DataNormalizationError("raw_data must be a list")
        if not raw_data:
            return []

        candles: list[Candle] = []
        last_timestamp: datetime | None = None

        for row in raw_data:
            if not isinstance(row, dict):
                raise DataNormalizationError("each market-data row must be a dict")

            try:
                ts = row["timestamp"]
            except KeyError as exc:
                raise DataNormalizationError("Missing 'timestamp'") from exc

            if not isinstance(ts, datetime):
                raise DataNormalizationError("timestamp must be datetime")
            if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
                raise DataNormalizationError(f"Timestamp {ts} must be timezone-aware.")

            ts_utc = ts.astimezone(timezone.utc)
            if last_timestamp is not None:
                if ts_utc < last_timestamp:
                    raise DataNormalizationError(
                        f"Timestamps must be strictly ordered. {ts_utc} is before {last_timestamp}."
                    )
                if ts_utc == last_timestamp:
                    raise DataNormalizationError(f"Duplicate timestamp detected: {ts_utc}.")
            last_timestamp = ts_utc

            if "is_completed" not in row:
                raise DataNormalizationError(f"Missing 'is_completed' status at {ts_utc}.")
            is_completed = row["is_completed"]
            if not isinstance(is_completed, bool):
                raise DataNormalizationError(
                    f"'is_completed' must be a boolean at {ts_utc}."
                )
            if not is_completed:
                continue

            try:
                values = {
                    name: Decimal(str(row[name]))
                    for name in ("open", "high", "low", "close")
                }
            except (KeyError, ValueError, TypeError) as exc:
                raise DataNormalizationError(
                    f"Invalid numeric data at {ts_utc}: {exc}"
                ) from exc

            if any(not value.is_finite() for value in values.values()):
                raise DataNormalizationError(f"Non-finite OHLC at {ts_utc}.")
            if values["high"] < values["low"]:
                raise DataNormalizationError(
                    f"Invalid OHLC at {ts_utc}: high ({values['high']}) < low ({values['low']})."
                )
            if not (values["low"] <= values["open"] <= values["high"]):
                raise DataNormalizationError(f"Open is outside [low, high] at {ts_utc}.")
            if not (values["low"] <= values["close"] <= values["high"]):
                raise DataNormalizationError(f"Close is outside [low, high] at {ts_utc}.")

            candles.append(
                Candle(
                    candle_id=f"c_{ts_utc.isoformat()}",
                    open=values["open"],
                    high=values["high"],
                    low=values["low"],
                    close=values["close"],
                )
            )

        return candles


@dataclass(frozen=True)
class TargetCandidate:
    target_id: str
    target_type: str
    price: Decimal
    provenance: str


@dataclass(frozen=True)
class TargetLeg:
    leg_id: str
    target_id: str
    allocation_pct: Decimal


@dataclass(frozen=True)
class TargetPlan:
    candidates: List[TargetCandidate]
    legs: List[TargetLeg]

    def candidate_by_id(self, target_id: str) -> Optional[TargetCandidate]:
        return next(
            (candidate for candidate in self.candidates if candidate.target_id == target_id),
            None,
        )


@dataclass
class StructuralPOICandidate:
    ticker: str
    direction: str
    poi_top: Decimal
    poi_bottom: Decimal
    poi_class: str
    execution_role: str
    target: Optional[Decimal] = None
    is_executable: bool = False


@dataclass(frozen=True)
class RRResult:
    is_evaluable: bool
    rr_ratio: Optional[Decimal]
    reason: str = "NO_RESOLVED_TARGET"


@dataclass(frozen=True)
class AnalyzerOutput:
    instrument: str
    timeframe: str
    lifecycle_state: LifecycleState
    previous_lifecycle_state: LifecycleState
    detected_event: DetectionEvent
    process_conditions: Tuple[ProcessCondition, ...]
    structural_facts: Tuple[StructuralFact, ...]
    classification_outcome: Optional[ClassificationOutcome]
    l2_result: Any
    l3_result: Any
    l4_result: bos.BOSAnalysis
    l5_result: choch.CHoCHAnalysis
    first_bos_retracement_baseline_status: FirstBOSRetracementBaselineStatus
    poi_result: Optional[StructuralPOICandidate]
    target_candidates: Tuple[TargetCandidate, ...]
    resolved_target: Optional[TargetCandidate]
    rr_result: RRResult


def determine_next_state(
    current_state: LifecycleState,
    event: DetectionEvent,
    conditions: List[ProcessCondition],
    first_bos_status: FirstBOSRetracementBaselineStatus,
    major_retracement_qualified: bool,
    is_choch_confirmed: bool = False,
    is_major_idm_sweep: bool = False,
    is_choch_eligible: bool = False,
    major_idm_qualified: bool = False,
) -> Tuple[LifecycleState, Optional[ClassificationOutcome]]:
    """Apply the L8 decision key:
    state + event/outcome + required canonical process/context conditions.
    """

    idm_taken = ProcessCondition.IDM_TAKEN in conditions
    gate_unlocked = ProcessCondition.CONFIRMATION_GATE_UNLOCKED in conditions

    if current_state == LifecycleState.BOOTSTRAP:
        if idm_taken:
            return LifecycleState.CONFIRMATION_LOCKED, None
        return current_state, None

    if current_state == LifecycleState.CONFIRMATION_LOCKED:
        if event == DetectionEvent.EXT_CONT_BREAK and gate_unlocked:
            if first_bos_status is FirstBOSRetracementBaselineStatus.UNSPECIFIED_CANONICAL_INPUT:
                return current_state, None
            if major_retracement_qualified:
                return LifecycleState.POST_BOS, ClassificationOutcome.VALID_BOS
            return current_state, ClassificationOutcome.IMPULSE_EXTENSION

        if event == DetectionEvent.EXT_OPP_BREAK:
            if is_choch_confirmed:
                return LifecycleState.POST_CHOCH, ClassificationOutcome.CHoCH_CONFIRMED
            if is_choch_eligible:
                return current_state, ClassificationOutcome.CHoCH_ELIGIBLE

        if event == DetectionEvent.MAJOR_IDM_EVENT and is_major_idm_sweep:
            return current_state, ClassificationOutcome.MAJOR_IDM_SWEEP

        return current_state, None

    if current_state == LifecycleState.CONFIRMED_RANGE:
        if event == DetectionEvent.EXT_CONT_BREAK:
            if major_retracement_qualified:
                return LifecycleState.POST_BOS, ClassificationOutcome.VALID_BOS
            return current_state, ClassificationOutcome.IMPULSE_EXTENSION

        if event == DetectionEvent.EXT_OPP_BREAK:
            if is_choch_confirmed:
                return LifecycleState.POST_CHOCH, ClassificationOutcome.CHoCH_CONFIRMED
            if is_choch_eligible:
                return current_state, ClassificationOutcome.CHoCH_ELIGIBLE

        if event == DetectionEvent.MAJOR_IDM_EVENT and is_major_idm_sweep:
            return current_state, ClassificationOutcome.MAJOR_IDM_SWEEP

        return current_state, None

    if current_state == LifecycleState.POST_BOS:
        if event == DetectionEvent.EXT_OPP_BREAK:
            if is_choch_confirmed:
                return LifecycleState.POST_CHOCH, ClassificationOutcome.CHoCH_CONFIRMED
            if is_choch_eligible:
                return current_state, ClassificationOutcome.CHoCH_ELIGIBLE
        if event == DetectionEvent.MAJOR_IDM_EVENT and is_major_idm_sweep:
            return current_state, ClassificationOutcome.MAJOR_IDM_SWEEP
        if event == DetectionEvent.NEW_SVP_QUALIFIED and major_idm_qualified:
            return LifecycleState.CONFIRMED_RANGE, None
        return current_state, None

    if current_state == LifecycleState.POST_CHOCH:
        if event == DetectionEvent.EXT_CONT_BREAK and gate_unlocked:
            if first_bos_status is FirstBOSRetracementBaselineStatus.UNSPECIFIED_CANONICAL_INPUT:
                return current_state, None
            if major_retracement_qualified:
                return LifecycleState.POST_BOS, ClassificationOutcome.VALID_BOS
            return current_state, ClassificationOutcome.IMPULSE_EXTENSION

        if event == DetectionEvent.EXT_OPP_BREAK:
            if is_choch_confirmed:
                return current_state, ClassificationOutcome.CHoCH_CONFIRMED
            if is_choch_eligible:
                return current_state, ClassificationOutcome.CHoCH_ELIGIBLE

        if event == DetectionEvent.MAJOR_IDM_EVENT and is_major_idm_sweep:
            return current_state, ClassificationOutcome.MAJOR_IDM_SWEEP

        if event == DetectionEvent.NEW_SVP_QUALIFIED and major_idm_qualified:
            return LifecycleState.CONFIRMATION_LOCKED, None

        return current_state, None

    raise AnalyzerContractError(f"Unsupported lifecycle state: {current_state!r}")


def _result_event(
    l2_result: minor.MinorStructureAnalysis,
    l3_result: structural.StructuralAnalysis,
    l4_result: bos.BOSAnalysis,
    l5_result: choch.CHoCHAnalysis,
) -> DetectionEvent:
    """Resolve one event using the L8 implementation precedence."""

    if l5_result.resolution in {
        choch.CHoCHResolution.CHOCH_ELIGIBLE,
        choch.CHoCHResolution.CHOCH_CONFIRMED,
    }:
        return DetectionEvent.EXT_OPP_BREAK

    if l5_result.resolution is choch.CHoCHResolution.MAJOR_IDM_SWEEP:
        return DetectionEvent.MAJOR_IDM_EVENT

    if l4_result.resolution in {
        bos.BOSResolution.VALID_BOS,
        bos.BOSResolution.IMPULSE_EXTENSION,
    }:
        return DetectionEvent.EXT_CONT_BREAK

    if l4_result.resolution is bos.BOSResolution.MAJOR_IDM_SWEEP:
        return DetectionEvent.MAJOR_IDM_EVENT

    if l3_result.active_idm is not None and l3_result.active_idm.takeout_candle_id is not None:
        return DetectionEvent.MINOR_IDM_EVENT

    if l2_result.active.pullback is not None:
        return DetectionEvent.NEW_SVP_QUALIFIED

    return DetectionEvent.NO_EVENT_INTERNAL_PB


class SMCAnalyzer:
    """Snapshot orchestrator over the canonical Layer-1 through Layer-5 engines."""

    def __init__(
        self,
        instrument: str,
        timeframe: str,
        direction: minor.PullbackDirection | None = None,
        initial_state: LifecycleState = LifecycleState.BOOTSTRAP,
    ):
        if not instrument:
            raise AnalyzerContractError("instrument is required")
        if not timeframe:
            raise AnalyzerContractError("timeframe is required")
        if not isinstance(initial_state, LifecycleState):
            raise AnalyzerContractError("initial_state must be a LifecycleState")
        self.instrument = instrument
        self.timeframe = timeframe
        self.direction = direction
        self.state = initial_state

    def analyze(
        self,
        raw_data: List[dict],
        *,
        direction: minor.PullbackDirection | None = None,
        range_high: Decimal | None = None,
        range_low: Decimal | None = None,
        first_bos_range_high: Decimal | None = None,
        first_bos_range_low: Decimal | None = None,
        first_bos_retracement_baseline_status: FirstBOSRetracementBaselineStatus =
        FirstBOSRetracementBaselineStatus.UNSPECIFIED_CANONICAL_INPUT,
        htf_valid_pullback: bool = False,
        lifecycle: structural.IDMLifecycleContext | None = None,
        attempt_end_candle_id: str | None = None,
        execution_start_candle_id: str | None = None,
        break_candle_id: str | None = None,
        choch_reference: choch.CHoCHReference | None = None,
        choch_confirmation_gate_open: bool = False,
        ltf_context_active: bool = False,
        external_major_idm_reference: choch.CHoCHReference | None = None,
        major_idm_qualified: bool = False,
    ) -> AnalyzerOutput:
        analysis_direction = direction or self.direction
        if not isinstance(analysis_direction, minor.PullbackDirection):
            raise AnalyzerContractError("direction is required for Layer-2 orchestration")

        if not isinstance(htf_valid_pullback, bool):
            raise AnalyzerContractError("htf_valid_pullback must be boolean")
        if not isinstance(
            first_bos_retracement_baseline_status,
            FirstBOSRetracementBaselineStatus,
        ):
            raise AnalyzerContractError("invalid First-BOS baseline status")

        first_bos_state = self.state in {
            LifecycleState.BOOTSTRAP,
            LifecycleState.CONFIRMATION_LOCKED,
            LifecycleState.POST_CHOCH,
        }

        supplied_first_bos_baseline = (
            first_bos_range_high is not None or first_bos_range_low is not None
        )
        if supplied_first_bos_baseline and (
            first_bos_range_high is None or first_bos_range_low is None
        ):
            raise AnalyzerContractError("First-BOS baseline requires both high and low coordinates")
        if first_bos_state and first_bos_retracement_baseline_status is FirstBOSRetracementBaselineStatus.AVAILABLE:
            if first_bos_range_high is None or first_bos_range_low is None:
                raise AnalyzerContractError(
                    "AVAILABLE First-BOS baseline requires explicit implementation input coordinates"
                )
        if first_bos_state and supplied_first_bos_baseline:
            if first_bos_retracement_baseline_status is not FirstBOSRetracementBaselineStatus.AVAILABLE:
                raise AnalyzerContractError(
                    "First-BOS coordinates require AVAILABLE baseline status"
                )

        candles = MarketDataNormalizer.normalize(raw_data)
        if len(candles) < 2:
            raise InsufficientHistoryError("at least two completed candles are required")

        l2_result = minor.detect_valid_pullbacks(candles, analysis_direction)

        effective_range_high = range_high
        effective_range_low = range_low
        if (
            first_bos_state
            and effective_range_high is None
            and effective_range_low is None
            and first_bos_retracement_baseline_status is FirstBOSRetracementBaselineStatus.AVAILABLE
        ):
            effective_range_high = first_bos_range_high
            effective_range_low = first_bos_range_low

        l3_result = structural.analyze_layer3(
            candles,
            l2_result,
            range_high=effective_range_high,
            range_low=effective_range_low,
            htf_valid_pullback=htf_valid_pullback,
            lifecycle=lifecycle,
            attempt_end_candle_id=attempt_end_candle_id,
        )

        if l3_result.retracement is not None:
            l4_start = execution_start_candle_id or l3_result.retracement.qualification_end_candle_id
            l4_result = bos.detect_bos(
                candles,
                l3_result,
                execution_start_candle_id=l4_start,
                break_candle_id=break_candle_id,
            )
        else:
            l4_result = bos.BOSAnalysis(
                bos.BOSResolution.NO_EVIDENCE,
                None,
                False,
                bool(
                    l3_result.active_idm
                    and l3_result.active_idm.takeout_candle_id is not None
                ),
                False,
            )

        if choch_reference is not None:
            l5_result = choch.detect_choch(
                candles,
                choch_reference,
                confirmation_gate_open=choch_confirmation_gate_open,
                break_candle_id=break_candle_id,
                ltf_context_active=ltf_context_active,
                fallback_major_idm_reference=external_major_idm_reference,
            )
        else:
            l5_result = choch.CHoCHAnalysis(
                choch.CHoCHResolution.NO_EVIDENCE,
                None,
                False,
                choch_confirmation_gate_open,
            )

        conditions: list[ProcessCondition] = []
        if l3_result.active_idm and l3_result.active_idm.takeout_candle_id is not None:
            conditions.append(ProcessCondition.IDM_TAKEN)
            conditions.append(ProcessCondition.CONFIRMATION_GATE_UNLOCKED)
        if l3_result.retracement is not None:
            conditions.append(ProcessCondition.STRUCTURAL_RETRACEMENT_EVALUATION)

        structural_facts: list[StructuralFact] = []
        if l3_result.confirmed_swings:
            structural_facts.append(StructuralFact.CONFIRMED_STRUCTURAL_SWING)
        if l4_result.structural_break is not None or l5_result.structural_break is not None:
            structural_facts.append(StructuralFact.STRUCTURAL_SWING_BREAK)
        if l4_result.resolution is bos.BOSResolution.IMPULSE_EXTENSION:
            structural_facts.extend(
                [StructuralFact.SWING_REVOKED, StructuralFact.PULLBACK_REFERENCE_SHIFT]
            )

        event = _result_event(l2_result, l3_result, l4_result, l5_result)
        is_choch_confirmed = l5_result.resolution is choch.CHoCHResolution.CHOCH_CONFIRMED
        is_choch_eligible = l5_result.resolution is choch.CHoCHResolution.CHOCH_ELIGIBLE
        is_major_idm_sweep = l5_result.resolution is choch.CHoCHResolution.MAJOR_IDM_SWEEP or (
            l4_result.resolution is bos.BOSResolution.MAJOR_IDM_SWEEP
        )
        major_retracement_qualified = bool(
            l3_result.retracement and l3_result.retracement.qualified
        )

        next_state, outcome = determine_next_state(
            current_state=self.state,
            event=event,
            conditions=conditions,
            first_bos_status=first_bos_retracement_baseline_status,
            major_retracement_qualified=major_retracement_qualified,
            is_choch_confirmed=is_choch_confirmed,
            is_major_idm_sweep=is_major_idm_sweep,
            is_choch_eligible=is_choch_eligible,
            major_idm_qualified=major_idm_qualified,
        )
        previous_state = self.state
        self.state = next_state

        return AnalyzerOutput(
            instrument=self.instrument,
            timeframe=self.timeframe,
            lifecycle_state=next_state,
            previous_lifecycle_state=previous_state,
            detected_event=event,
            process_conditions=tuple(conditions),
            structural_facts=tuple(dict.fromkeys(structural_facts)),
            classification_outcome=outcome,
            l2_result=l2_result,
            l3_result=l3_result,
            l4_result=l4_result,
            l5_result=l5_result,
            first_bos_retracement_baseline_status=first_bos_retracement_baseline_status,
            poi_result=None,
            target_candidates=(),
            resolved_target=None,
            rr_result=RRResult(False, None, "NO_RESOLVED_TARGET"),
        )


__all__ = [
    "AnalyzerContractError",
    "AnalyzerOutput",
    "ClassificationOutcome",
    "DataNormalizationError",
    "DetectionEvent",
    "FirstBOSRetracementBaselineStatus",
    "InsufficientHistoryError",
    "LifecycleState",
    "MarketDataNormalizer",
    "ProcessCondition",
    "RRResult",
    "SMCAnalyzer",
    "StructuralFact",
    "TargetCandidate",
    "TargetLeg",
    "TargetPlan",
    "determine_next_state",
]
