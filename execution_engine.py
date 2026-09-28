from __future__ import annotations
from dataclasses import dataclass, replace
from decimal import Decimal
from enum import Enum
from typing import Tuple, Optional, List, Any

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
    l5_result
) -> ExecutionAnalysis:
    order_flows = []
    order_blocks = []
    engineering_liquidity = None
    decisional_poi = None
    extreme_poi = None
    origin_ob_latent = None
    rejection_block = None

    if not l2_result or not hasattr(l2_result, 'pullbacks') or not l2_result.pullbacks:
        return ExecutionAnalysis((), (), None, POISet(None, None, None, None))

    candle_map = {c.candle_id: c for c in candles}
    
    idm_taken = False
    if l3_result and hasattr(l3_result, 'active_idm') and l3_result.active_idm:
        if hasattr(l3_result.active_idm, 'takeout_candle_id') and l3_result.active_idm.takeout_candle_id:
            idm_taken = True

    bos_confirmed = False
    if l4_result and hasattr(l4_result, 'structural_break') and l4_result.structural_break:
        bos_confirmed = True

    valid_ofs = []
    
    for pb in l2_result.pullbacks:
        direction = pb.direction
        ref_c = candle_map.get(pb.reference_candle_id)
        ext_c = candle_map.get(pb.extreme.candle_id) if hasattr(pb, 'extreme') and hasattr(pb.extreme, 'candle_id') else None
        
        if not ref_c:
            top = Decimal("0")
            bottom = Decimal("0")
        else:
            if not ext_c:
                top = ref_c.high
                bottom = ref_c.low
            else:
                top = max(ref_c.high, ext_c.high)
                bottom = min(ref_c.low, ext_c.low)
        
        obj_type = ExecutionObjectType.OF_CANDIDATE
        if not idm_taken:
            obj_type = ExecutionObjectType.SMT_INDUCEMENT_TRAP
            
        of = ExecutionObject(
            object_type=obj_type,
            direction=direction,
            top=top,
            bottom=bottom,
            source_candle_ids=(pb.start_candle_id, getattr(pb, 'completion_candle_id', pb.start_candle_id)) if hasattr(pb, 'start_candle_id') else (),
            state=ExecutionState.ACTIVE
        )
        order_flows.append(of)
        
        if obj_type == ExecutionObjectType.OF_CANDIDATE:
            valid_ofs.append(of)

    if valid_ofs:
        if valid_ofs[0].direction == PullbackDirection.BULLISH:
            valid_ofs.sort(key=lambda x: x.bottom)
            extreme_of = valid_ofs[0]
            decisional_of = valid_ofs[-1]
        else:
            valid_ofs.sort(key=lambda x: x.top, reverse=True)
            extreme_of = valid_ofs[0]
            decisional_of = valid_ofs[-1]
            
        ext_of = replace(extreme_of, object_type=ExecutionObjectType.EXTREME_OF)
        dec_of = replace(decisional_of, object_type=ExecutionObjectType.DECISIONAL_OF)
        
        extreme_poi = replace(ext_of, object_type=ExecutionObjectType.EXTREME_POI)
        
        if l3_result and hasattr(l3_result, 'confirmed_swings') and l3_result.confirmed_swings:
            last_swing = l3_result.confirmed_swings[-1]
            range_high = last_swing.high
            range_low = last_swing.low
            
            is_valid_dec = check_rule_of_two_discount_premium(
                dec_of.top, dec_of.bottom, dec_of.direction, range_high, range_low
            )
            if is_valid_dec:
                decisional_poi = replace(dec_of, object_type=ExecutionObjectType.DECISIONAL_POI)
            else:
                decisional_poi = None
        else:
            decisional_poi = replace(dec_of, object_type=ExecutionObjectType.DECISIONAL_POI)

        pb_match = next((p for p in l2_result.pullbacks if candle_map.get(p.reference_candle_id) and 
                         (max(candle_map[p.reference_candle_id].high, getattr(candle_map.get(getattr(p, 'extreme', type('E',(),{'candle_id':None})()).candle_id), 'high', Decimal("-inf"))) == ext_of.top or
                          min(candle_map[p.reference_candle_id].low, getattr(candle_map.get(getattr(p, 'extreme', type('E',(),{'candle_id':None})()).candle_id), 'low', Decimal("inf"))) == ext_of.bottom)), None)
                          
        if pb_match:
            engineering_liquidity = ExecutionObject(
                object_type=ExecutionObjectType.ENG_LQD_REFERENCE,
                direction=pb_match.direction,
                top=ext_of.top,
                bottom=ext_of.bottom,
                source_candle_ids=ext_of.source_candle_ids,
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

def expire_pois(pois: List[ExecutionObject], l4_result: Any) -> List[ExecutionObject]:
    has_break = False
    if l4_result and hasattr(l4_result, 'structural_break') and l4_result.structural_break:
        has_break = True
        
    result = []
    for poi in pois:
        if has_break and poi.state in (ExecutionState.ACTIVE, ExecutionState.TOUCHED):
            result.append(replace(poi, state=ExecutionState.EXPIRED_HISTORICAL))
        else:
            result.append(poi)
    return result

def fail_pois(pois: List[ExecutionObject], l5_result: Any) -> List[ExecutionObject]:
    choch_confirmed = False
    if l5_result and hasattr(l5_result, 'resolution'):
        if l5_result.resolution.name == 'CHOCH_CONFIRMED':
            choch_confirmed = True
            
    result = []
    for poi in pois:
        if choch_confirmed and poi.state in (ExecutionState.ACTIVE, ExecutionState.TOUCHED):
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
