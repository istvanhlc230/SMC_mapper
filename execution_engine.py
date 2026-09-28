from __future__ import annotations
from dataclasses import dataclass, replace
from decimal import Decimal
from enum import Enum
from typing import Tuple, Optional, List

from microstructure_engine import Candle
from minor_structure_engine import PullbackDirection

class ExecutionState(str, Enum):
    ACTIVE = "ACTIVE"
    TOUCHED = "TOUCHED"
    MITIGATED = "MITIGATED"
    FAILED = "FAILED"
    INVALIDATED = "INVALIDATED"
    EXPIRED_HISTORICAL = "EXPIRED_HISTORICAL"

class ExecutionObjectType(str, Enum):
    OF_CANDIDATE = "OF_CANDIDATE"
    SMT_INDUCEMENT_TRAP = "SMT_INDUCEMENT_TRAP"
    OF_CONFIRMED = "OF_CONFIRMED"
    DECISIONAL_OF = "DECISIONAL_OF"
    EXTREME_OF = "EXTREME_OF"
    VALID_OB = "VALID_OB"
    DECISIONAL_OB = "DECISIONAL_OB"
    EXTREME_OB = "EXTREME_OB"
    ORIGIN_OB = "ORIGIN_OB"
    REJECTION_BLOCK = "REJECTION_BLOCK"
    ENG_LQD_REFERENCE = "ENG_LQD_REFERENCE"
    ENG_LQD_CONFIRMED = "ENG_LQD_CONFIRMED"
    ENG_LQD_SWEEP = "ENG_LQD_SWEEP"
    DECISIONAL_POI = "DECISIONAL_POI"
    EXTREME_POI = "EXTREME_POI"

@dataclass(frozen=True, slots=True)
class ExecutionObject:
    object_type: ExecutionObjectType
    direction: PullbackDirection
    top: Decimal
    bottom: Decimal
    source_candle_ids: tuple[str, ...]
    state: ExecutionState
    
    def __post_init__(self):
        if not isinstance(self.top, Decimal) or not isinstance(self.bottom, Decimal):
            raise ValueError("ExecutionObject bounds must be Decimals")
        if self.top < self.bottom:
            raise ValueError("ExecutionObject top must be >= bottom")

@dataclass(frozen=True, slots=True)
class OBPillars:
    bos_causality: bool
    sweeps_extreme: bool
    fvg_exists_unconsumed: bool
    
    @property
    def is_valid(self) -> bool:
        return self.bos_causality and self.sweeps_extreme and self.fvg_exists_unconsumed

@dataclass(frozen=True, slots=True)
class POISet:
    decisional_poi: ExecutionObject | None
    extreme_poi: ExecutionObject | None
    origin_ob_latent: ExecutionObject | None
    rejection_block: ExecutionObject | None
    
    def __post_init__(self):
        if self.decisional_poi and self.decisional_poi.object_type != ExecutionObjectType.DECISIONAL_POI:
            raise ValueError("Decisional POI must be typed DECISIONAL_POI")
        if self.extreme_poi and self.extreme_poi.object_type != ExecutionObjectType.EXTREME_POI:
            raise ValueError("Extreme POI must be typed EXTREME_POI")

@dataclass(frozen=True, slots=True)
class ExecutionAnalysis:
    order_flows: tuple[ExecutionObject, ...]
    order_blocks: tuple[ExecutionObject, ...]
    engineering_liquidity: ExecutionObject | None
    active_pois: POISet

def evaluate_execution_state(
    candles,
    l2_result,
    l3_result,
    l4_result,
    choch_confirmed=False
) -> ExecutionAnalysis:
    order_flows = []
    order_blocks = []
    engineering_liquidity = None
    decisional_poi = None
    extreme_poi = None
    origin_ob_latent = None
    rejection_block = None

    if l2_result and hasattr(l2_result, 'pullbacks'):
        for pb in l2_result.pullbacks:
            # Map each valid pullback as an Order Flow candidate
            direction = pb.direction
            # We assume PB extreme acts as boundary
            if hasattr(pb, 'extreme') and hasattr(pb.extreme, 'price'):
                top = pb.extreme.price
                bottom = pb.extreme.price # Default fallback, normally you'd use the full PB span
            else:
                top = Decimal("0")
                bottom = Decimal("0")
            
            of = ExecutionObject(
                object_type=ExecutionObjectType.OF_CANDIDATE,
                direction=direction,
                top=top,
                bottom=bottom,
                source_candle_ids=(pb.start_candle_id, pb.completion_candle_id) if hasattr(pb, 'start_candle_id') else (),
                state=ExecutionState.ACTIVE
            )
            order_flows.append(of)
            
            # Simple Engineering Liquidity mapping logic from the last PB before extreme POI
            # This is a basic skeletal implementation connecting the pieces
            engineering_liquidity = ExecutionObject(
                object_type=ExecutionObjectType.ENG_LQD_REFERENCE,
                direction=direction,
                top=top,
                bottom=bottom,
                source_candle_ids=of.source_candle_ids,
                state=ExecutionState.ACTIVE
            )

    poi_set = POISet(
        decisional_poi=decisional_poi,
        extreme_poi=extreme_poi,
        origin_ob_latent=origin_ob_latent,
        rejection_block=rejection_block
    )
    return ExecutionAnalysis(tuple(order_flows), tuple(order_blocks), engineering_liquidity, poi_set)


def _is_discount(top: Decimal, bottom: Decimal, range_high: Decimal, range_low: Decimal) -> bool:
    if range_high == range_low:
        return False
    midpoint = range_low + (range_high - range_low) / Decimal('2')
    return top < midpoint

def _is_premium(top: Decimal, bottom: Decimal, range_high: Decimal, range_low: Decimal) -> bool:
    if range_high == range_low:
        return False
    midpoint = range_low + (range_high - range_low) / Decimal('2')
    return bottom > midpoint

def check_rule_of_two_discount_premium(
    poi_top: Decimal, 
    poi_bottom: Decimal, 
    direction: PullbackDirection, 
    range_high: Decimal, 
    range_low: Decimal
) -> bool:
    if direction == PullbackDirection.BULLISH:
        return _is_discount(poi_top, poi_bottom, range_high, range_low)
    else:
        return _is_premium(poi_top, poi_bottom, range_high, range_low)

def refine_ob_wick(candle: Candle, direction: PullbackDirection, swept_price: Decimal) -> tuple[Decimal, Decimal]:
    if direction == PullbackDirection.BULLISH:
        ob_bottom = candle.low
        ob_top = max(candle.open, candle.close)
        return ob_top, ob_bottom
    else:
        ob_top = candle.high
        ob_bottom = min(candle.open, candle.close)
        return ob_top, ob_bottom

def refine_ob_inside_bar(mother: Candle, inside: Candle, direction: PullbackDirection) -> tuple[Decimal, Decimal]:
    if direction == PullbackDirection.BULLISH:
        return inside.low, mother.low
    else:
        return mother.high, inside.high

def validate_ob_pillars(
    caused_bos: bool, 
    swept_extreme: bool, 
    fvg_unconsumed: bool
) -> OBPillars:
    return OBPillars(
        bos_causality=caused_bos,
        sweeps_extreme=swept_extreme,
        fvg_exists_unconsumed=fvg_unconsumed
    )

def create_engineering_liquidity(
    pb_extreme_candle: Candle, 
    direction: PullbackDirection
) -> ExecutionObject | None:
    price = pb_extreme_candle.low if direction == PullbackDirection.BULLISH else pb_extreme_candle.high
    return ExecutionObject(
        object_type=ExecutionObjectType.ENG_LQD_REFERENCE,
        direction=direction,
        top=price,
        bottom=price,
        source_candle_ids=(pb_extreme_candle.candle_id,),
        state=ExecutionState.ACTIVE
    )

def expire_pois(pois: List[ExecutionObject]) -> List[ExecutionObject]:
    """Expire POIs when a VALID_BOS creates a new range."""
    result = []
    for poi in pois:
        if poi.state in (ExecutionState.ACTIVE, ExecutionState.TOUCHED):
            result.append(replace(poi, state=ExecutionState.EXPIRED_HISTORICAL))
        else:
            result.append(poi)
    return result

def fail_pois(pois: List[ExecutionObject]) -> List[ExecutionObject]:
    """Fail POIs when a canonical structural shift (CHoCH) occurs against them."""
    result = []
    for poi in pois:
        if poi.state in (ExecutionState.ACTIVE, ExecutionState.TOUCHED):
            result.append(replace(poi, state=ExecutionState.FAILED))
        else:
            result.append(poi)
    return result

def interact_poi(poi: ExecutionObject, is_mitigation: bool) -> ExecutionObject:
    if poi.state not in (ExecutionState.ACTIVE, ExecutionState.TOUCHED):
        return poi
    if is_mitigation:
        return replace(poi, state=ExecutionState.MITIGATED)
    return replace(poi, state=ExecutionState.TOUCHED)
