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
    origin_pullback_id: str | None = None
    range_id: str | None = None

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
    
    if direction == PullbackDirection.BULLISH:
        if c3.low > c1.high:
            fvg_top = c3.low
            fvg_bottom = c1.high
            for i in range(idx + 3, len(candles_list)):
                if candles_list[i].low < fvg_top:
                    fvg_top = candles_list[i].low
                if fvg_top <= fvg_bottom:
                    return False
            return True
        return False
    else:
        if c3.high < c1.low:
            fvg_bottom = c3.high
            fvg_top = c1.low
            for i in range(idx + 3, len(candles_list)):
                if candles_list[i].high > fvg_bottom:
                    fvg_bottom = candles_list[i].high
                if fvg_top <= fvg_bottom:
                    return False
            return True
        return False

def check_sweep(candles_list: List[Candle], idx: int, direction: PullbackDirection) -> bool:
    if idx == 0:
        return False
    curr = candles_list[idx]
    prev = candles_list[idx - 1]
    if direction == PullbackDirection.BULLISH:
        return curr.low < prev.low
    else:
        return curr.high > prev.high

def check_inside_bar(candles_list: List[Candle], idx: int) -> bool:
    if idx == 0:
        return False
    curr = candles_list[idx]
    prev = candles_list[idx - 1]
    return curr.high <= prev.high and curr.low >= prev.low

def validate_ob_pillars(caused_bos: bool, sweeps_extreme: bool, fvg_unconsumed: bool) -> OBPillars:
    return OBPillars(bos_causality=caused_bos, sweeps_extreme=sweeps_extreme, fvg_exists_unconsumed=fvg_unconsumed)

def evaluate_execution_state(
    candles: tuple[Candle, ...],
    l2_result: Any,
    l3_result: Any,
    l4_result: Any,
    l5_result: Any,
    previous_state: ExecutionAnalysis | None = None
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
    idm_price = None
    if l3_result and hasattr(l3_result, 'active_idm') and l3_result.active_idm:
        idm_price = l3_result.active_idm.reference_price
        if getattr(l3_result.active_idm, 'takeout_candle_id', None):
            idm_taken = True

    valid_bos = False
    break_candle_id = None
    if l4_result and getattr(l4_result, 'valid_bos', False):
        valid_bos = True
        break_candle_id = getattr(l4_result.structural_break, 'break_candle_id', None) if hasattr(l4_result, 'structural_break') else None

    range_id = None
    if l3_result and hasattr(l3_result, 'confirmed_swings') and l3_result.confirmed_swings:
        range_id = getattr(l3_result.confirmed_swings[-1], 'source_candle_id', None)

    choch_confirmed = False
    if l5_result and hasattr(l5_result, 'resolution'):
        if getattr(l5_result.resolution, 'name', '') == 'CHOCH_CONFIRMED':
            choch_confirmed = True

    # 1. Evaluate OF Candidates
    def is_mitigated(pb) -> bool:
        ext_c = candle_map.get(getattr(getattr(pb, 'extreme', None), 'candle_id', None))
        if not ext_c: return False
        pb_idx = l2_result.pullbacks.index(pb)
        for i in range(pb_idx + 1, len(l2_result.pullbacks)):
            later_pb = l2_result.pullbacks[i]
            later_ref = candle_map.get(later_pb.reference_candle_id)
            if not later_ref: continue
            if pb.direction == PullbackDirection.BULLISH:
                top = max(candle_map[pb.reference_candle_id].high, ext_c.high)
                later_ext = candle_map.get(getattr(getattr(later_pb, 'extreme', None), 'candle_id', None))
                low_point = min(later_ref.low, later_ext.low) if later_ext else later_ref.low
                if low_point <= top:
                    return True
            else:
                bottom = min(candle_map[pb.reference_candle_id].low, ext_c.low)
                later_ext = candle_map.get(getattr(getattr(later_pb, 'extreme', None), 'candle_id', None))
                high_point = max(later_ref.high, later_ext.high) if later_ext else later_ref.high
                if high_point >= bottom:
                    return True
        return False

    valid_ofs = []
    
    for pb in l2_result.pullbacks:
        direction = pb.direction
        ref_c = candle_map.get(pb.reference_candle_id)
        ext_c = candle_map.get(getattr(getattr(pb, 'extreme', None), 'candle_id', None))
        
        if not ref_c: continue
            
        if not ext_c:
            top = ref_c.high
            bottom = ref_c.low
            end_c_id = pb.reference_candle_id
        else:
            top = max(ref_c.high, ext_c.high)
            bottom = min(ref_c.low, ext_c.low)
            end_c_id = pb.extreme.candle_id
            
        is_smt = False
        if not idm_taken:
            is_smt = True
        elif idm_price is not None:
            if direction == PullbackDirection.BULLISH and bottom >= idm_price:
                is_smt = True
            elif direction == PullbackDirection.BEARISH and top <= idm_price:
                is_smt = True
                
        obj_type = ExecutionObjectType.SMT_INDUCEMENT_TRAP if is_smt else ExecutionObjectType.OF_CONFIRMED
        
        # State transitions based on history / current frame
        state = ExecutionState.ACTIVE
        if is_mitigated(pb):
            state = ExecutionState.MITIGATED
        if choch_confirmed:
            state = ExecutionState.FAILED

        # Note: Expire POIs logic is handled via the wrapper expire_pois, but if we do it here:
        if previous_state:
            for prev_of in previous_state.order_flows:
                if prev_of.origin_pullback_id == pb.reference_candle_id:
                    if prev_of.state == ExecutionState.EXPIRED_HISTORICAL:
                        state = ExecutionState.EXPIRED_HISTORICAL

        source_ids = (pb.start_candle_id, end_c_id) if hasattr(pb, 'start_candle_id') else ()
        
        of = ExecutionObject(
            object_type=obj_type,
            direction=direction,
            top=top,
            bottom=bottom,
            source_candle_ids=source_ids,
            state=state,
            origin_pullback_id=pb.reference_candle_id,
            range_id=range_id
        )
        order_flows.append(of)
        
        if obj_type == ExecutionObjectType.OF_CONFIRMED and state == ExecutionState.ACTIVE:
            valid_ofs.append(of)

    ext_of_obj = None
    dec_of_obj = None
    
    if valid_ofs:
        # Extreme OF: furthest eligible unmitigated in chronological lineage
        ext_of_obj = valid_ofs[0]
        ext_of_obj = replace(ext_of_obj, object_type=ExecutionObjectType.EXTREME_OF)

        # Decisional OF: tied to valid BOS producing displacement
        if valid_bos and break_candle_id:
            break_idx = next((i for i, c in enumerate(candles_list) if c.candle_id == break_candle_id), -1)
            best_of = None
            best_dist = float('inf')
            for of_cand in valid_ofs:
                if len(of_cand.source_candle_ids) == 2:
                    comp_id = of_cand.source_candle_ids[1]
                    comp_idx = next((i for i, c in enumerate(candles_list) if c.candle_id == comp_id), -1)
                    if comp_idx != -1 and comp_idx < break_idx:
                        dist = break_idx - comp_idx
                        if dist < best_dist:
                            best_dist = dist
                            best_of = of_cand
            if best_of:
                dec_of_obj = replace(best_of, object_type=ExecutionObjectType.DECISIONAL_OF)

        order_flows = [ext_of_obj if x.origin_pullback_id == ext_of_obj.origin_pullback_id else x for x in order_flows]
        if dec_of_obj:
            order_flows = [dec_of_obj if x.origin_pullback_id == dec_of_obj.origin_pullback_id else x for x in order_flows]

        # Order Blocks Evaluation
        for of_cand in (ext_of_obj, dec_of_obj):
            if not of_cand: continue
            if len(of_cand.source_candle_ids) == 2:
                s_id, e_id = of_cand.source_candle_ids
                s_idx = next((i for i,c in enumerate(candles_list) if c.candle_id == s_id), -1)
                e_idx = next((i for i,c in enumerate(candles_list) if c.candle_id == e_id), -1)
                
                if s_idx != -1 and e_idx != -1 and e_idx >= s_idx:
                    for i in range(s_idx, e_idx + 1):
                        has_sweep = check_sweep(candles_list, i, of_cand.direction)
                        has_fvg = check_fvg(candles_list, i, of_cand.direction)
                        
                        # Causal check: candle must actually initiate displacement for DECISIONAL
                        # For EXTREME, it must be the extreme candle.
                        is_causal = False
                        if of_cand == dec_of_obj and valid_bos:
                            # Verify displacement reaches BOS
                            is_causal = True # Simplified linkage to OF causality
                        if of_cand == ext_of_obj:
                            # Extreme OB must be the origin candle
                            is_causal = True
                            
                        pillars = validate_ob_pillars(is_causal, has_sweep, has_fvg)
                        if pillars.is_valid:
                            if check_inside_bar(candles_list, i):
                                ob_top, ob_bottom = refine_ob_inside_bar(candles_list[i-1], candles_list[i], of_cand.direction)
                            else:
                                ob_top, ob_bottom = refine_ob_wick(candles_list[i], of_cand.direction, Decimal("0"))
                                
                            ob_type = ExecutionObjectType.EXTREME_OB if of_cand == ext_of_obj else ExecutionObjectType.DECISIONAL_OB
                            ob = ExecutionObject(
                                object_type=ob_type,
                                direction=of_cand.direction,
                                top=ob_top,
                                bottom=ob_bottom,
                                source_candle_ids=(candles_list[i].candle_id,),
                                state=ExecutionState.ACTIVE,
                                origin_pullback_id=of_cand.origin_pullback_id,
                                range_id=range_id
                            )
                            order_blocks.append(ob)
                            break # Shift successful, found OB for this OF

        extreme_poi = replace(ext_of_obj, object_type=ExecutionObjectType.EXTREME_POI) if ext_of_obj else None
        extreme_ob = next((ob for ob in order_blocks if ob.object_type == ExecutionObjectType.EXTREME_OB), None)
        if extreme_ob:
            extreme_poi = replace(extreme_ob, object_type=ExecutionObjectType.EXTREME_POI)
            
        if dec_of_obj:
            dec_poi_cand = replace(dec_of_obj, object_type=ExecutionObjectType.DECISIONAL_POI)
            dec_ob = next((ob for ob in order_blocks if ob.object_type == ExecutionObjectType.DECISIONAL_OB), None)
            if dec_ob:
                dec_poi_cand = replace(dec_ob, object_type=ExecutionObjectType.DECISIONAL_POI)
            
            # Range constraint check for Decisional
            if l3_result and hasattr(l3_result, 'confirmed_swings') and l3_result.confirmed_swings:
                last_swing = l3_result.confirmed_swings[-1]
                r_high, r_low = getattr(last_swing, 'high', Decimal('0')), getattr(last_swing, 'low', Decimal('0'))
                if check_rule_of_two_discount_premium(dec_poi_cand.top, dec_poi_cand.bottom, dec_poi_cand.direction, r_high, r_low):
                    decisional_poi = dec_poi_cand

        # Engineering Liquidity: valid pullback immediately preceding extreme POI
        if extreme_poi:
            try:
                ext_pb_idx = next(i for i, pb in enumerate(l2_result.pullbacks) if pb.reference_candle_id == extreme_poi.origin_pullback_id)
                if ext_pb_idx > 0:
                    prev_pb = l2_result.pullbacks[ext_pb_idx - 1]
                    ext_c = candle_map.get(getattr(getattr(prev_pb, 'extreme', None), 'candle_id', None))
                    if ext_c:
                        price = ext_c.low if extreme_poi.direction == PullbackDirection.BULLISH else ext_c.high
                        engineering_liquidity = ExecutionObject(
                            object_type=ExecutionObjectType.ENG_LQD_REFERENCE,
                            direction=extreme_poi.direction,
                            top=price,
                            bottom=price,
                            source_candle_ids=(ext_c.candle_id,),
                            state=ExecutionState.ACTIVE,
                            range_id=range_id
                        )
            except StopIteration:
                pass

        # Latent Origin OB activation
        if ext_of_obj and ext_of_obj.state == ExecutionState.MITIGATED:
            if not choch_confirmed:
                if extreme_ob and extreme_ob.state == ExecutionState.FAILED:
                    origin_ob_latent = replace(extreme_ob, object_type=ExecutionObjectType.ORIGIN_OB, state=ExecutionState.ACTIVE)

        # Rejection Block activation
        if extreme_ob and extreme_ob.state == ExecutionState.FAILED:
            rb_top, rb_bottom = refine_ob_wick(candle_map[extreme_ob.source_candle_ids[0]], extreme_ob.direction, Decimal("0"))
            rejection_block = ExecutionObject(
                object_type=ExecutionObjectType.REJECTION_BLOCK,
                direction=extreme_ob.direction,
                top=rb_top,
                bottom=rb_bottom,
                source_candle_ids=extreme_ob.source_candle_ids,
                state=ExecutionState.ACTIVE,
                range_id=range_id
            )

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

def expire_pois(pois: List[ExecutionObject], l4_result: Any, current_range_id: str | None = None) -> List[ExecutionObject]:
    has_valid_bos = getattr(l4_result, 'valid_bos', False)
    result = []
    for poi in pois:
        if has_valid_bos and current_range_id and poi.range_id and poi.range_id != current_range_id:
            if poi.state in (ExecutionState.ACTIVE, ExecutionState.TOUCHED):
                result.append(replace(poi, state=ExecutionState.EXPIRED_HISTORICAL))
            else:
                result.append(poi)
        else:
            result.append(poi)
    return result

def fail_pois(pois: List[ExecutionObject], l5_result: Any) -> List[ExecutionObject]:
    choch_confirmed = False
    if l5_result and hasattr(l5_result, 'resolution') and getattr(l5_result.resolution, 'name', '') == 'CHOCH_CONFIRMED':
        choch_confirmed = True
            
    result = []
    for poi in pois:
        if choch_confirmed and poi.state in (ExecutionState.ACTIVE, ExecutionState.TOUCHED):
            result.append(replace(poi, state=ExecutionState.FAILED))
        else:
            result.append(poi)
    return result
