from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from typing import List, Optional

class IntrabarSequenceEvidence(Enum):
    OBSERVED = "OBSERVED"
    METHODOLOGY_ASSUMED = "METHODOLOGY_ASSUMED"
    UNAVAILABLE = "UNAVAILABLE"

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
    FALLBACK_EVENT = auto()
    REAL_MAJOR_IDM_EVENT = auto()
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

class SMCError(Exception):
    pass

class DataNormalizationError(SMCError):
    pass

class InsufficientHistoryError(SMCError):
    pass

@dataclass
class Candle:
    index: int
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    is_completed: bool
    intrabar_sequence_evidence: IntrabarSequenceEvidence = IntrabarSequenceEvidence.UNAVAILABLE

class MarketDataNormalizer:
    @staticmethod
    def normalize(raw_data: List[dict]) -> List[Candle]:
        """
        raw_data expected as:
        [{'timestamp': datetime, 'open': float/str, 'high': float/str, 'low': float/str, 'close': float/str, 'is_completed': bool}, ...]
        """
        if not raw_data:
            return []
            
        candles = []
        last_timestamp = None
        
        for i, row in enumerate(raw_data):
            # Enforce timezone (UTC)
            ts = row['timestamp']
            if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
                raise DataNormalizationError(f"Timestamp {ts} must be timezone-aware.")
            
            ts_utc = ts.astimezone(timezone.utc)
            
            # Deterministic ordering & duplicate check
            if last_timestamp is not None:
                if ts_utc < last_timestamp:
                    raise DataNormalizationError(f"Timestamps must be strictly ordered. {ts_utc} is before {last_timestamp}.")
                if ts_utc == last_timestamp:
                    raise DataNormalizationError(f"Duplicate timestamp detected: {ts_utc}.")
            last_timestamp = ts_utc
            
            # Decimal conversion
            try:
                c_open = Decimal(str(row['open']))
                c_high = Decimal(str(row['high']))
                c_low = Decimal(str(row['low']))
                c_close = Decimal(str(row['close']))
            except (ValueError, TypeError) as e:
                raise DataNormalizationError(f"Invalid numeric data at {ts_utc}: {e}")
                
            # Invalid OHLC check
            if c_high < c_low:
                raise DataNormalizationError(f"Invalid OHLC at {ts_utc}: high ({c_high}) < low ({c_low}).")
                
            # Incomplete candle exclusion
            is_completed = bool(row.get('is_completed', True))
            if not is_completed:
                # We skip uncompleted candles for historical mapping
                continue
                
            candles.append(Candle(
                index=len(candles),
                timestamp=ts_utc,
                open=c_open,
                high=c_high,
                low=c_low,
                close=c_close,
                is_completed=True,
                intrabar_sequence_evidence=IntrabarSequenceEvidence.UNAVAILABLE
            ))
            
        return candles

@dataclass
class StructuralPOICandidate:
    ticker: str
    direction: str # "BUY" | "SELL"
    poi_top: Decimal
    poi_bottom: Decimal
    poi_class: str # "OF_CONFIRMED" | "VALID_OB"
    execution_role: str # "DECISIONAL" | "EXTREME"
    target: Optional[Decimal] = None
    is_executable: bool = False # RR NOT_EVALUABLE
