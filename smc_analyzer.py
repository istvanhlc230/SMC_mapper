from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from typing import List, Optional, Any, Tuple

from microstructure_engine import Candle, SequenceEvidence
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
    FIRST_BOS_RETRACEMENT_UNRESOLVED = auto()

class FirstBOSRetracementBaselineStatus(Enum):
    AVAILABLE = auto()
    UNSPECIFIED_CANONICAL_INPUT = auto()

class SMCError(Exception):
    pass

class DataNormalizationError(SMCError):
    pass

class InsufficientHistoryError(SMCError):
    pass

class MarketDataNormalizer:
    @staticmethod
    def normalize(raw_data: List[dict]) -> List[Candle]:
        if not raw_data:
            return []
            
        candles = []
        last_timestamp = None
        
        for i, row in enumerate(raw_data):
            ts = row['timestamp']
            if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
                raise DataNormalizationError(f"Timestamp {ts} must be timezone-aware.")
            
            ts_utc = ts.astimezone(timezone.utc)
            
            if last_timestamp is not None:
                if ts_utc < last_timestamp:
                    raise DataNormalizationError(f"Timestamps must be strictly ordered. {ts_utc} is before {last_timestamp}.")
                if ts_utc == last_timestamp:
                    raise DataNormalizationError(f"Duplicate timestamp detected: {ts_utc}.")
            last_timestamp = ts_utc
            
            try:
                c_open = Decimal(str(row['open']))
                c_high = Decimal(str(row['high']))
                c_low = Decimal(str(row['low']))
                c_close = Decimal(str(row['close']))
            except (ValueError, TypeError) as e:
                raise DataNormalizationError(f"Invalid numeric data at {ts_utc}: {e}")
                
            if c_high < c_low:
                raise DataNormalizationError(f"Invalid OHLC at {ts_utc}: high ({c_high}) < low ({c_low}).")
                
            if 'is_completed' not in row:
                raise DataNormalizationError(f"Missing 'is_completed' status at {ts_utc}.")
            is_completed = row['is_completed']
            if not isinstance(is_completed, bool):
                raise DataNormalizationError(f"'is_completed' must be a boolean at {ts_utc}.")
                
            if not is_completed:
                continue
                
            candles.append(Candle(
                candle_id=f"c_{ts_utc.timestamp()}",
                open=c_open,
                high=c_high,
                low=c_low,
                close=c_close
            ))
            
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
        return next((candidate for candidate in self.candidates
                     if candidate.target_id == target_id), None)

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

@dataclass
class RRResult:
    is_evaluable: bool
    rr_ratio: Optional[Decimal]

@dataclass
class AnalyzerOutput:
    instrument: str
    timeframe: str
    lifecycle_state: LifecycleState
    detected_event: DetectionEvent
    process_conditions: List[ProcessCondition]
    structural_facts: List[StructuralFact]
    classification_outcome: Optional[ClassificationOutcome]
    l2_result: Any
    l3_result: Any
    l4_result: Any
    l5_result: Any
    first_bos_retracement_baseline_status: FirstBOSRetracementBaselineStatus
    poi_result: Optional[StructuralPOICandidate]
    target_candidates: List[TargetCandidate]
    resolved_target: Optional[TargetCandidate]
    rr_result: RRResult

def determine_next_state(
    current_state: LifecycleState,
    event: DetectionEvent,
    conditions: List[ProcessCondition],
    first_bos_status: FirstBOSRetracementBaselineStatus,
    major_retracement_qualified: bool,
    is_choch_confirmed: bool = False,
    is_major_idm_sweep: bool = False
) -> Tuple[LifecycleState, Optional[ClassificationOutcome]]:
    
    outcome = None
    next_state = current_state
    
    idm_taken = ProcessCondition.IDM_TAKEN in conditions
    gate_unlocked = ProcessCondition.CONFIRMATION_GATE_UNLOCKED in conditions
    
    if current_state == LifecycleState.BOOTSTRAP:
        if idm_taken:
            next_state = LifecycleState.CONFIRMATION_LOCKED
    
    elif current_state == LifecycleState.CONFIRMATION_LOCKED:
        if event == DetectionEvent.EXT_CONT_BREAK:
            if not gate_unlocked:
                pass 
            else:
                if first_bos_status == FirstBOSRetracementBaselineStatus.UNSPECIFIED_CANONICAL_INPUT:
                    outcome = ClassificationOutcome.FIRST_BOS_RETRACEMENT_UNRESOLVED
                    next_state = LifecycleState.CONFIRMATION_LOCKED
                elif major_retracement_qualified:
                    outcome = ClassificationOutcome.VALID_BOS
                    next_state = LifecycleState.POST_BOS
                else:
                    outcome = ClassificationOutcome.IMPULSE_EXTENSION
                    next_state = LifecycleState.CONFIRMATION_LOCKED
        elif event == DetectionEvent.EXT_OPP_BREAK:
            if is_choch_confirmed:
                outcome = ClassificationOutcome.CHoCH_CONFIRMED
                next_state = LifecycleState.POST_CHOCH
        elif event == DetectionEvent.MAJOR_IDM_EVENT:
            if is_major_idm_sweep:
                outcome = ClassificationOutcome.MAJOR_IDM_SWEEP
                
    elif current_state == LifecycleState.CONFIRMED_RANGE:
        if event == DetectionEvent.EXT_CONT_BREAK:
            if major_retracement_qualified:
                outcome = ClassificationOutcome.VALID_BOS
                next_state = LifecycleState.POST_BOS
            else:
                outcome = ClassificationOutcome.IMPULSE_EXTENSION
        elif event == DetectionEvent.EXT_OPP_BREAK:
            if is_choch_confirmed:
                outcome = ClassificationOutcome.CHoCH_CONFIRMED
                next_state = LifecycleState.POST_CHOCH
        elif event == DetectionEvent.MAJOR_IDM_EVENT:
            if is_major_idm_sweep:
                outcome = ClassificationOutcome.MAJOR_IDM_SWEEP
                
    elif current_state == LifecycleState.POST_CHOCH:
        if event == DetectionEvent.EXT_CONT_BREAK:
            if not gate_unlocked:
                pass 
            else:
                if first_bos_status == FirstBOSRetracementBaselineStatus.UNSPECIFIED_CANONICAL_INPUT:
                    outcome = ClassificationOutcome.FIRST_BOS_RETRACEMENT_UNRESOLVED
                    next_state = LifecycleState.POST_CHOCH
                elif major_retracement_qualified:
                    outcome = ClassificationOutcome.VALID_BOS
                    next_state = LifecycleState.POST_BOS
                else:
                    outcome = ClassificationOutcome.IMPULSE_EXTENSION
                    next_state = LifecycleState.POST_CHOCH
        elif event == DetectionEvent.EXT_OPP_BREAK:
            if is_choch_confirmed:
                outcome = ClassificationOutcome.CHoCH_CONFIRMED
                next_state = LifecycleState.POST_CHOCH
        elif event == DetectionEvent.MAJOR_IDM_EVENT:
            if is_major_idm_sweep:
                outcome = ClassificationOutcome.MAJOR_IDM_SWEEP
    
    return next_state, outcome

class SMCAnalyzer:
    def __init__(self, instrument: str, timeframe: str):
        self.instrument = instrument
        self.timeframe = timeframe
        self.state = LifecycleState.BOOTSTRAP

    def analyze(self, raw_data: List[dict]) -> AnalyzerOutput:
        candles = MarketDataNormalizer.normalize(raw_data)
        
        l2_result = minor.detect_valid_pullbacks(candles)
        
        l3_result = structural.analyze_layer3(
            minor=l2_result, 
            candles=candles, 
            lifecycle=structural.IDMLifecycleContext(structural.IDMClass.MINOR_IDM, structural.IDMOrigin.PULLBACK_DERIVED, None, None, None)
        )
        
        conditions = []
        if l3_result.idm_taken:
            conditions.append(ProcessCondition.IDM_TAKEN)
            conditions.append(ProcessCondition.CONFIRMATION_GATE_UNLOCKED)
            
        first_bos_status = FirstBOSRetracementBaselineStatus.UNSPECIFIED_CANONICAL_INPUT if self.state in (LifecycleState.BOOTSTRAP, LifecycleState.CONFIRMATION_LOCKED, LifecycleState.POST_CHOCH) else FirstBOSRetracementBaselineStatus.AVAILABLE
            
        l4_result = None
        event = DetectionEvent.NO_EVENT_INTERNAL_PB
        outcome = None
        
        major_retracement_qualified = False
        
        next_state, outcome = determine_next_state(
            current_state=self.state,
            event=event,
            conditions=conditions,
            first_bos_status=first_bos_status,
            major_retracement_qualified=major_retracement_qualified
        )
        self.state = next_state
        
        l5_result = None
        
        target_candidates = []
        resolved_target = None
        rr_result = RRResult(is_evaluable=False, rr_ratio=None)
        
        return AnalyzerOutput(
            instrument=self.instrument,
            timeframe=self.timeframe,
            lifecycle_state=self.state,
            detected_event=event,
            process_conditions=conditions,
            structural_facts=[],
            classification_outcome=outcome,
            l2_result=l2_result,
            l3_result=l3_result,
            l4_result=l4_result,
            l5_result=l5_result,
            first_bos_retracement_baseline_status=first_bos_status,
            poi_result=None,
            target_candidates=target_candidates,
            resolved_target=resolved_target,
            rr_result=rr_result
        )
