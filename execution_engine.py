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

def check_fvg(candles_list: List[Candle], idx: int, direction: PullbackDirection) -> bool:
    if idx + 2 >= len(candles_list):
        return False
    c1 = candles_list[idx]
    c3 = candles_list[idx + 2]
    if direction == PullbackDirection.BULLISH: # looking for bullish OB, so price displaces up
        return c3.low > c1.high
    else:
        return c3.high < c1.low

def check_sweep(candles_list: List[Candle], idx: int, direction: PullbackDirection) -> bool:
    if idx == 0:
        return False
    curr = candles_list[idx]
    prev = candles_list[idx - 1]
    if direction == PullbackDirection.BULLISH: # sweeps previous low
        return curr.low < prev.low
    else:
        return curr.high > prev.high

def validate_ob_pillars(caused_bos: bool, sweeps_extreme: bool, fvg_unconsumed: bool) -> OBPillars:
    return OBPillars(bos_causality=caused_bos, sweeps_extreme=sweeps_extreme, fvg_exists_unconsumed=fvg_unconsumed)

def evaluate_execution_state(
    candles: tuple[Candle, ...],
    l2_result: Any,
    l3_result: Any,
    l4_result: Any,
    l5_result: Any
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
    candles_list = list(candles)
    
    idm_taken = False
    if l3_result and hasattr(l3_result, 'active_idm') and l3_result.active_idm:
        if hasattr(l3_result.active_idm, 'takeout_candle_id') and l3_result.active_idm.takeout_candle_id:
            idm_taken = True

    valid_bos = False
    if l4_result and hasattr(l4_result, 'valid_bos') and l4_result.valid_bos:
        valid_bos = True

    valid_ofs = []
    
    for pb in l2_result.pullbacks:
        direction = pb.direction
        ref_c = candle_map.get(pb.reference_candle_id)
        ext_c = candle_map.get(getattr(getattr(pb, 'extreme', None), 'candle_id', None))
        
        if not ref_c:
            continue
            
        if not ext_c:
            top = ref_c.high
            bottom = ref_c.low
            end_c_id = pb.reference_candle_id
        else:
            top = max(ref_c.high, ext_c.high)
            bottom = min(ref_c.low, ext_c.low)
            end_c_id = pb.extreme.candle_id
            
        obj_type = ExecutionObjectType.OF_CANDIDATE
        if not idm_taken:
            obj_type = ExecutionObjectType.SMT_INDUCEMENT_TRAP
        else:
            obj_type = ExecutionObjectType.OF_CONFIRMED
            
        source_ids = (pb.start_candle_id, end_c_id) if hasattr(pb, 'start_candle_id') else ()
        
        of = ExecutionObject(
            object_type=obj_type,
            direction=direction,
            top=top,
            bottom=bottom,
            source_candle_ids=source_ids,
            state=ExecutionState.ACTIVE
        )
        order_flows.append(of)
        
        if obj_type == ExecutionObjectType.OF_CONFIRMED:
            valid_ofs.append(of)

    if valid_ofs:
        if valid_ofs[0].direction == PullbackDirection.BULLISH:
            valid_ofs.sort(key=lambda x: x.bottom)
            extreme_of = valid_ofs[0]
            decisional_of = valid_ofs[-1] if len(valid_ofs) > 1 else None
        else:
            valid_ofs.sort(key=lambda x: x.top, reverse=True)
            extreme_of = valid_ofs[0]
            decisional_of = valid_ofs[-1] if len(valid_ofs) > 1 else None
            
        ext_of_obj = replace(extreme_of, object_type=ExecutionObjectType.EXTREME_OF)
        order_flows = [ext_of_obj if x == extreme_of else x for x in order_flows]
        
        if decisional_of and valid_bos:
            dec_of_obj = replace(decisional_of, object_type=ExecutionObjectType.DECISIONAL_OF)
            order_flows = [dec_of_obj if x == decisional_of else x for x in order_flows]
        else:
            dec_of_obj = None

        # Build OBs for extreme OF
        # To build an OB we search candles inside the OF candidate
        for of_cand in (ext_of_obj, dec_of_obj):
            if not of_cand: continue
            
            # Find OBs in the OF
            of_obs = []
            if len(of_cand.source_candle_ids) == 2:
                s_id, e_id = of_cand.source_candle_ids
                s_idx = next((i for i,c in enumerate(candles_list) if c.candle_id == s_id), -1)
                e_idx = next((i for i,c in enumerate(candles_list) if c.candle_id == e_id), -1)
                
                if s_idx != -1 and e_idx != -1 and e_idx >= s_idx:
                    for i in range(s_idx, e_idx + 1):
                        has_sweep = check_sweep(candles_list, i, of_cand.direction)
                        has_fvg = check_fvg(candles_list, i, of_cand.direction)
                        is_causal = (of_cand == dec_of_obj and valid_bos) or (of_cand == ext_of_obj) # Simplify causality
                        
                        pillars = validate_ob_pillars(is_causal, has_sweep, has_fvg)
                        if pillars.is_valid:
                            ob_top, ob_bottom = refine_ob_wick(candles_list[i], of_cand.direction, Decimal("0"))
                            ob_type = ExecutionObjectType.EXTREME_OB if of_cand == ext_of_obj else ExecutionObjectType.DECISIONAL_OB
                            ob = ExecutionObject(
                                object_type=ob_type,
                                direction=of_cand.direction,
                                top=ob_top,
                                bottom=ob_bottom,
                                source_candle_ids=(candles_list[i].candle_id,),
                                state=ExecutionState.ACTIVE
                            )
                            order_blocks.append(ob)
                            of_obs.append(ob)
            
        # POI selection
        extreme_poi = replace(ext_of_obj, object_type=ExecutionObjectType.EXTREME_POI)
        if order_blocks and any(ob.object_type == ExecutionObjectType.EXTREME_OB for ob in order_blocks):
            extreme_poi = replace(next(ob for ob in order_blocks if ob.object_type == ExecutionObjectType.EXTREME_OB), object_type=ExecutionObjectType.EXTREME_POI)
            
        if dec_of_obj:
            dec_poi_cand = replace(dec_of_obj, object_type=ExecutionObjectType.DECISIONAL_POI)
            if order_blocks and any(ob.object_type == ExecutionObjectType.DECISIONAL_OB for ob in order_blocks):
                dec_poi_cand = replace(next(ob for ob in order_blocks if ob.object_type == ExecutionObjectType.DECISIONAL_OB), object_type=ExecutionObjectType.DECISIONAL_POI)
            
            # Premium / Discount validation
            if l3_result and hasattr(l3_result, 'confirmed_swings') and l3_result.confirmed_swings:
                last_swing = l3_result.confirmed_swings[-1]
                range_high, range_low = getattr(last_swing, 'high', Decimal('0')), getattr(last_swing, 'low', Decimal('0'))
                
                is_valid_dec = check_rule_of_two_discount_premium(
                    dec_poi_cand.top, dec_poi_cand.bottom, dec_poi_cand.direction, range_high, range_low
                )
                if is_valid_dec:
                    decisional_poi = dec_poi_cand
            else:
                decisional_poi = dec_poi_cand

        # Engineering Liquidity: Must immediately precede active EXTREME POI
        # We find the pullback that corresponds to extreme_poi's origin
        # Wait: The canonical rule is "immediately preceding active Extreme POI"
        # Since extreme POI is built from the furthest OF, the pullback *before* it?
        # Actually, if we sort valid pullbacks, the one right before the extreme POI in time?
        # Let's take the pullback whose extreme is the extreme POI's bottom/top.
        # Then ENG LQD is beyond that pullback extreme.
        if extreme_poi:
            # find pb that matches extreme_of
            for pb in l2_result.pullbacks:
                ext_c = candle_map.get(getattr(getattr(pb, 'extreme', None), 'candle_id', None))
                if ext_c and ((extreme_poi.direction == PullbackDirection.BULLISH and ext_c.low == ext_of_obj.bottom) or 
                              (extreme_poi.direction == PullbackDirection.BEARISH and ext_c.high == ext_of_obj.top)):
                    engineering_liquidity = create_engineering_liquidity(ext_c, extreme_poi.direction)
                    break

    poi_set = POISet(
        decisional_poi=decisional_poi,
        extreme_poi=extreme_poi,
        origin_ob_latent=origin_ob_latent,
        rejection_block=rejection_block
    )
    
    return ExecutionAnalysis(tuple(order_flows), tuple(order_blocks), engineering_liquidity, poi_set)

def _is_discount(top: Decimal, bottom: Decimal, range_high: Decimal, range_low: Decimal) -> bool:
    if range_high == range_low: return False
    midpoint = range_low + (range_high - range_low) / Decimal('2')
    return top < midpoint

def _is_premium(top: Decimal, bottom: Decimal, range_high: Decimal, range_low: Decimal) -> bool:
    if range_high == range_low: return False
    midpoint = range_low + (range_high - range_low) / Decimal('2')
    return bottom > midpoint

def check_rule_of_two_discount_premium(poi_top: Decimal, poi_bottom: Decimal, direction: PullbackDirection, range_high: Decimal, range_low: Decimal) -> bool:
    if direction == PullbackDirection.BULLISH:
        return _is_discount(poi_top, poi_bottom, range_high, range_low)
    else:
        return _is_premium(poi_top, poi_bottom, range_high, range_low)

def refine_ob_wick(candle: Candle, direction: PullbackDirection, swept_price: Decimal) -> tuple[Decimal, Decimal]:
    if direction == PullbackDirection.BULLISH:
        return max(candle.open, candle.close), candle.low
    else:
        return candle.high, min(candle.open, candle.close)

def refine_ob_inside_bar(mother: Candle, inside: Candle, direction: PullbackDirection) -> tuple[Decimal, Decimal]:
    if direction == PullbackDirection.BULLISH:
        return inside.low, mother.low
    else:
        return mother.high, inside.high

def create_engineering_liquidity(pb_extreme_candle: Candle, direction: PullbackDirection) -> ExecutionObject | None:
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
    """Expire POIs when a VALID_BOS creates a new range."""
    has_valid_bos = False
    if l4_result and getattr(l4_result, 'valid_bos', False):
        has_valid_bos = True
        
    result = []
    for poi in pois:
        if has_valid_bos and poi.state in (ExecutionState.ACTIVE, ExecutionState.TOUCHED):
            result.append(replace(poi, state=ExecutionState.EXPIRED_HISTORICAL))
        else:
            result.append(poi)
    return result

def fail_pois(pois: List[ExecutionObject], l5_result: Any) -> List[ExecutionObject]:
    """Fail POIs when a canonical structural shift (CHoCH_CONFIRMED) occurs."""
    choch_confirmed = False
    if l5_result and getattr(l5_result, 'confirmed', False):
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
