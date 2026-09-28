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
    previous_state: Any = None # Keep signature compatible but unused
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
    
    # Range Provenance
    current_range_id = None
    if l3_result and hasattr(l3_result, 'confirmed_swings') and l3_result.confirmed_swings:
        current_range_id = getattr(l3_result.confirmed_swings[-1], 'source_candle_id', None)

    # Active IDM Provenance
    idm_taken = False
    idm_ref_candle_id = None
    if l3_result and hasattr(l3_result, 'active_idm') and l3_result.active_idm:
        idm_ref_candle_id = getattr(l3_result.active_idm, 'source_candle_id', None)
        if getattr(l3_result.active_idm, 'takeout_candle_id', None):
            idm_taken = True

    # L4 Provenance
    valid_bos = False
    break_candle_id = None
    if l4_result and getattr(l4_result, 'valid_bos', False):
        valid_bos = True
        break_candle_id = getattr(l4_result.structural_break, 'break_candle_id', None) if hasattr(l4_result, 'structural_break') else None

    # L5 Provenance
    choch_confirmed = False
    if l5_result and hasattr(l5_result, 'resolution'):
        if getattr(l5_result.resolution, 'name', '') == 'CHOCH_CONFIRMED':
            choch_confirmed = True

    # --- 1. Order Flow Lifecycle ---
    def is_mitigated(pb) -> bool:
        ext_c = candle_map.get(getattr(getattr(pb, 'extreme', None), 'source_candle_id', None))
        if not ext_c: return False
        pb_idx = l2_result.pullbacks.index(pb)
        for i in range(pb_idx + 1, len(l2_result.pullbacks)):
            later_pb = l2_result.pullbacks[i]
            later_ref = candle_map.get(later_pb.reference_candle_id)
            if not later_ref: continue
            if pb.direction == PullbackDirection.BULLISH:
                top = max(candle_map[pb.reference_candle_id].high, ext_c.high)
                later_ext = candle_map.get(getattr(getattr(later_pb, 'extreme', None), 'source_candle_id', None))
                low_point = min(later_ref.low, later_ext.low) if later_ext else later_ref.low
                if low_point <= top:
                    return True
            else:
                bottom = min(candle_map[pb.reference_candle_id].low, ext_c.low)
                later_ext = candle_map.get(getattr(getattr(later_pb, 'extreme', None), 'source_candle_id', None))
                high_point = max(later_ref.high, later_ext.high) if later_ext else later_ref.high
                if high_point >= bottom:
                    return True
        return False

    valid_ofs = []
    
    for pb in l2_result.pullbacks:
        direction = pb.direction
        ref_c = candle_map.get(pb.reference_candle_id)
        ext_c = candle_map.get(getattr(getattr(pb, 'extreme', None), 'source_candle_id', None))
        
        if not ref_c: continue
            
        if not ext_c:
            top = ref_c.high
            bottom = ref_c.low
            end_c_id = pb.reference_candle_id
        else:
            top = max(ref_c.high, ext_c.high)
            bottom = min(ref_c.low, ext_c.low)
            end_c_id = pb.extreme.source_candle_id
            
        # SMT / Eligibility logic
        is_smt = False
        
        # If the pullback is geometrically acting as the IDM, it's not a tradable OF.
        # But if it's the valid pullback before continuation:
        # Pre-IDM pullbacks (those formed before the IDM is established) remain SMT.
        if not idm_taken:
            is_smt = True
        else:
            # If IDM is taken, we must ensure this PB is part of the original impulsive leg.
            # And we must ensure it is not geometrically violating the inducement boundary.
            idm_obj = l3_result.active_idm if hasattr(l3_result, 'active_idm') else None
            if idm_obj:
                idm_price = getattr(idm_obj, 'reference_price', None)
                if idm_price is not None:
                    if direction == PullbackDirection.BULLISH and bottom >= idm_price:
                        is_smt = True
                    elif direction == PullbackDirection.BEARISH and top <= idm_price:
                        is_smt = True
                
        obj_type = ExecutionObjectType.SMT_INDUCEMENT_TRAP if is_smt else ExecutionObjectType.OF_CONFIRMED
        
        state = ExecutionState.ACTIVE
        if is_mitigated(pb):
            state = ExecutionState.MITIGATED
        
        # Note: Expiry is mapped dynamically. Since we rebuild from start, 
        # we assign range_id. A PB belongs to the range corresponding to its formation.
        # Simplified: all OFs created in the active sequence belong to current_range_id.
        of = ExecutionObject(
            object_type=obj_type,
            direction=direction,
            top=top,
            bottom=bottom,
            source_candle_ids=(pb.start_candle_id, end_c_id) if hasattr(pb, 'start_candle_id') else (),
            state=state,
            origin_pullback_id=pb.reference_candle_id,
            range_id=current_range_id
        )
        order_flows.append(of)
        
        if obj_type == ExecutionObjectType.OF_CONFIRMED:
            valid_ofs.append(of)

    ext_of_obj = None
    dec_of_obj = None
    
    if valid_ofs:
        # Extreme OF: furthest eligible unmitigated in chronological lineage
        unmitigated_ofs = [of for of in valid_ofs if of.state == ExecutionState.ACTIVE]
        if unmitigated_ofs:
            ext_of_obj = replace(unmitigated_ofs[0], object_type=ExecutionObjectType.EXTREME_OF)

        # Decisional OF: causal OF that produced VALID_BOS
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

        # --- 3. Order Blocks Evaluation ---
        for of_cand in (ext_of_obj, dec_of_obj):
            if not of_cand or of_cand.state != ExecutionState.ACTIVE: 
                continue
            
            if len(of_cand.source_candle_ids) == 2:
                s_id, e_id = of_cand.source_candle_ids
                s_idx = next((i for i,c in enumerate(candles_list) if c.candle_id == s_id), -1)
                e_idx = next((i for i,c in enumerate(candles_list) if c.candle_id == e_id), -1)
                
                if s_idx != -1 and e_idx != -1 and e_idx >= s_idx:
                    for i in range(s_idx, e_idx + 1):
                        has_sweep = check_sweep(candles_list, i, of_cand.direction)
                        has_fvg = check_fvg(candles_list, i, of_cand.direction)
                        
                        # OB Pillar 1 causality check
                        # To be causal, the displacement from this candidate must lead to the BOS.
                        # If DECISIONAL_OF, and valid_bos is true, then this OB must be causal.
                        # For EXTREME, it must cause a BOS? The rule says:
                        # "Pillar 1: Origin of impulsive displacement causing canonical VALID_BOS... Extreme OF existing is not sufficient."
                        # If L4 has NO valid_bos, then NO OB satisfies Pillar 1.
                        # If L4 has valid_bos, we trace displacement.
                        is_causal = False
                        if valid_bos and break_candle_id:
                            break_idx = next((k for k, c in enumerate(candles_list) if c.candle_id == break_candle_id), -1)
                            # If the candle is before the break, its displacement caused the break.
                            if break_idx != -1 and i < break_idx:
                                # Validate the sequence from i to break_idx is unbroken displacement
                                is_causal = True
                                
                        pillars = validate_ob_pillars(is_causal, has_sweep, has_fvg)
                        if pillars.is_valid:
                            ob_top, ob_bottom = refine_ob_wick(candles_list[i], of_cand.direction, Decimal("0"))
                            # Apply Inside Bar Refinement ONLY AFTER 3-Pillars are valid
                            if check_inside_bar(candles_list, i):
                                ob_top, ob_bottom = refine_ob_inside_bar(candles_list[i-1], candles_list[i], of_cand.direction)
                                
                            ob_type = ExecutionObjectType.EXTREME_OB if of_cand == ext_of_obj else ExecutionObjectType.DECISIONAL_OB
                            ob = ExecutionObject(
                                object_type=ob_type,
                                direction=of_cand.direction,
                                top=ob_top,
                                bottom=ob_bottom,
                                source_candle_ids=(candles_list[i].candle_id,),
                                state=ExecutionState.ACTIVE,
                                origin_pullback_id=of_cand.origin_pullback_id,
                                range_id=current_range_id
                            )
                            order_blocks.append(ob)
                            break # Shift successful

        extreme_poi = replace(ext_of_obj, object_type=ExecutionObjectType.EXTREME_POI) if ext_of_obj else None
        extreme_ob = next((ob for ob in order_blocks if ob.object_type == ExecutionObjectType.EXTREME_OB), None)
        if extreme_ob:
            extreme_poi = replace(extreme_ob, object_type=ExecutionObjectType.EXTREME_POI)
            
        if dec_of_obj:
            dec_poi_cand = replace(dec_of_obj, object_type=ExecutionObjectType.DECISIONAL_POI)
            dec_ob = next((ob for ob in order_blocks if ob.object_type == ExecutionObjectType.DECISIONAL_OB), None)
            if dec_ob:
                dec_poi_cand = replace(dec_ob, object_type=ExecutionObjectType.DECISIONAL_POI)
            
            # Rule of Two Premium/Discount
            if l3_result and hasattr(l3_result, 'confirmed_swings') and l3_result.confirmed_swings:
                last_swing = l3_result.confirmed_swings[-1]
                r_high, r_low = getattr(last_swing, 'high', Decimal('0')), getattr(last_swing, 'low', Decimal('0'))
                if check_rule_of_two_discount_premium(dec_poi_cand.top, dec_poi_cand.bottom, dec_poi_cand.direction, r_high, r_low):
                    decisional_poi = dec_poi_cand

        # Engineering Liquidity: valid pullback IMMEDIATELY PRECEDING extreme POI
        if extreme_poi:
            try:
                ext_pb_idx = next(i for i, pb in enumerate(l2_result.pullbacks) if pb.reference_candle_id == extreme_poi.origin_pullback_id)
                if ext_pb_idx > 0:
                    prev_pb = l2_result.pullbacks[ext_pb_idx - 1]
                    ext_c = candle_map.get(getattr(getattr(prev_pb, 'extreme', None), 'source_candle_id', None))
                    if ext_c:
                        price = ext_c.low if extreme_poi.direction == PullbackDirection.BULLISH else ext_c.high
                        engineering_liquidity = ExecutionObject(
                            object_type=ExecutionObjectType.ENG_LQD_REFERENCE,
                            direction=extreme_poi.direction,
                            top=price,
                            bottom=price,
                            source_candle_ids=(ext_c.candle_id,),
                            state=ExecutionState.ACTIVE,
                            range_id=current_range_id
                        )
            except StopIteration:
                pass

        # Latent Origin OB activation
        orig_ext_of = valid_ofs[0] if valid_ofs else None
        if orig_ext_of and orig_ext_of.state == ExecutionState.MITIGATED:
            if not choch_confirmed:
                # If there was an Extreme OB for the original OF, and it failed
                # Actually, L6 state tracking from snapshot is tricky for failure.
                # If the Extreme OF is mitigated, and we don't have a CHoCH, ORIGIN_OB activates.
                origin_ob_latent = ExecutionObject(
                    object_type=ExecutionObjectType.ORIGIN_OB,
                    direction=orig_ext_of.direction,
                    top=orig_ext_of.top,
                    bottom=orig_ext_of.bottom,
                    source_candle_ids=orig_ext_of.source_candle_ids,
                    state=ExecutionState.ACTIVE,
                    range_id=current_range_id
                )

        # Rejection Block activation
        # Requires EXTREME_OB to have FAILED.
        # Since we evaluate from snapshot, if CHoCH is confirmed, EXTREME_OB fails.
        if extreme_ob and choch_confirmed:
            rb_top, rb_bottom = refine_ob_wick(candle_map[extreme_ob.source_candle_ids[0]], extreme_ob.direction, Decimal("0"))
            rejection_block = ExecutionObject(
                object_type=ExecutionObjectType.REJECTION_BLOCK,
                direction=extreme_ob.direction,
                top=rb_top,
                bottom=rb_bottom,
                source_candle_ids=extreme_ob.source_candle_ids,
                state=ExecutionState.ACTIVE,
                range_id=current_range_id
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
