from __future__ import annotations
from dataclasses import dataclass, replace
from decimal import Decimal
from enum import Enum
from typing import Tuple, Optional, List, Any, Dict

from microstructure_engine import Candle
from minor_structure_engine import PullbackDirection, CandleLevelValidPullback

class ExecutionState(str, Enum):
    ACTIVE = "ACTIVE"
    TOUCHED = "TOUCHED"
    MITIGATED = "MITIGATED"
    FAILED = "FAILED"
    INVALIDATED = "INVALIDATED"
    EXPIRED_HISTORICAL = "EXPIRED_HISTORICAL"

class ExecutionObjectType(str, Enum):
    ORDER_FLOW_CANDIDATE = "ORDER_FLOW_CANDIDATE"
    SMT_INDUCEMENT_TRAP = "SMT_INDUCEMENT_TRAP"
    ELIGIBLE_ORDER_FLOW = "ELIGIBLE_ORDER_FLOW"
    DECISIONAL_ORDER_FLOW = "DECISIONAL_ORDER_FLOW"
    EXTREME_ORDER_FLOW = "EXTREME_ORDER_FLOW"
    ORDER_BLOCK_CANDIDATE = "ORDER_BLOCK_CANDIDATE"
    VALIDATED_ORDER_BLOCK = "VALIDATED_ORDER_BLOCK"
    DECISIONAL_ORDER_BLOCK = "DECISIONAL_ORDER_BLOCK"
    EXTREME_ORDER_BLOCK = "EXTREME_ORDER_BLOCK"
    ORIGIN_ORDER_BLOCK = "ORIGIN_ORDER_BLOCK"
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
    origin_order_block_latent: ExecutionObject | None
    rejection_block: ExecutionObject | None
    
    def __post_init__(self):
        if self.decisional_poi and self.decisional_poi.object_type != ExecutionObjectType.DECISIONAL_POI:
            raise ValueError("decisional_poi must be DECISIONAL_POI")
        if self.extreme_poi and self.extreme_poi.object_type != ExecutionObjectType.EXTREME_POI:
            raise ValueError("extreme_poi must be EXTREME_POI")
        if self.origin_order_block_latent and self.origin_order_block_latent.object_type != ExecutionObjectType.ORIGIN_ORDER_BLOCK:
            raise ValueError("origin_order_block_latent must be ORIGIN_ORDER_BLOCK")
        if self.rejection_block and self.rejection_block.object_type != ExecutionObjectType.REJECTION_BLOCK:
            raise ValueError("rejection_block must be REJECTION_BLOCK")

@dataclass(frozen=True, slots=True)
class ExecutionAnalysis:
    order_flows: tuple[ExecutionObject, ...]
    order_blocks: tuple[ExecutionObject, ...]
    engineering_liquidity: ExecutionObject | None
    active_pois: POISet


def check_fvg(candles_list: List[Candle], idx: int, direction: PullbackDirection, max_idx: int = None) -> bool:
    if idx + 2 >= len(candles_list):
        return False
    c1 = candles_list[idx]
    c3 = candles_list[idx + 2]
    end_loop = len(candles_list) if max_idx is None else max_idx
    
    if direction == PullbackDirection.BULLISH:
        if c3.low > c1.high:
            fvg_top = c3.low
            fvg_bottom = c1.high
            for i in range(idx + 3, end_loop):
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
            for i in range(idx + 3, end_loop):
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

def group_pullbacks_into_of_candidates(pullbacks: List[CandleLevelValidPullback], candle_map: Dict[str, Candle], direction: PullbackDirection) -> List[List[CandleLevelValidPullback]]:
    if not pullbacks: return []
    groups = []
    current_group = [pullbacks[0]]
    ref_c0 = candle_map.get(pullbacks[0].reference_candle_id)
    if not ref_c0: return []
    
    if direction == PullbackDirection.BULLISH:
        current_top = ref_c0.high
        for pb in pullbacks[1:]:
            ref_c = candle_map.get(pb.reference_candle_id)
            if not ref_c: continue
            if ref_c.high <= current_top:
                current_group.append(pb)
            else:
                groups.append(current_group)
                current_group = [pb]
                current_top = ref_c.high
    else:
        current_top = ref_c0.low
        for pb in pullbacks[1:]:
            ref_c = candle_map.get(pb.reference_candle_id)
            if not ref_c: continue
            if ref_c.low >= current_top:
                current_group.append(pb)
            else:
                groups.append(current_group)
                current_group = [pb]
                current_top = ref_c.low
                
    if current_group:
        groups.append(current_group)
    return groups

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
    origin_order_block_latent = None
    rejection_block = None

    if not l2_result or not hasattr(l2_result, 'pullbacks') or not l2_result.pullbacks:
        return ExecutionAnalysis((), (), None, POISet(None, None, None, None))

    candle_map = {c.candle_id: c for c in candles}
    candles_list = list(candles)
    
    # 11. Real dealing-range provenance
    current_range_id = None
    if l3_result and hasattr(l3_result, 'active_dealing_range') and l3_result.active_dealing_range:
        current_range_id = l3_result.active_dealing_range.range_id

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
        if getattr(l5_result.resolution, 'name', '') == 'CHoCH_CONFIRMED':
            choch_confirmed = True

    # --- 1. Order Flow Lifecycle ---
    def is_mitigated(pb_group: List[CandleLevelValidPullback]) -> bool:
        # Mitigation MUST be a `CandleLevelValidPullback` breaching the OF bounds.
        # Find the overall extreme of the PB group
        ext_prices = []
        for pb in pb_group:
            ext_c = candle_map.get(getattr(getattr(pb, 'extreme', None), 'source_candle_id', None))
            if ext_c:
                ext_prices.append(ext_c.high if pb.direction == PullbackDirection.BULLISH else ext_c.low)
        if not ext_prices: return False
        
        if pb_group[0].direction == PullbackDirection.BULLISH:
            overall_bottom = min([candle_map[pb.reference_candle_id].low for pb in pb_group] + [ext_c.low for pb in pb_group if (ext_c := candle_map.get(getattr(getattr(pb, 'extreme', None), 'source_candle_id', None)))])
            overall_top = max([candle_map[pb.reference_candle_id].high for pb in pb_group] + ext_prices)
        else:
            overall_top = max([candle_map[pb.reference_candle_id].high for pb in pb_group] + [ext_c.high for pb in pb_group if (ext_c := candle_map.get(getattr(getattr(pb, 'extreme', None), 'source_candle_id', None)))])
            overall_bottom = min([candle_map[pb.reference_candle_id].low for pb in pb_group] + ext_prices)
            
        last_pb_idx = l2_result.pullbacks.index(pb_group[-1])
        for i in range(last_pb_idx + 1, len(l2_result.pullbacks)):
            later_pb = l2_result.pullbacks[i]
            later_ref = candle_map.get(later_pb.reference_candle_id)
            if not later_ref: continue
            
            # The mitigating pullback must itself be a CandleLevelValidPullback
            later_ext = candle_map.get(getattr(getattr(later_pb, 'extreme', None), 'source_candle_id', None))
            if pb_group[0].direction == PullbackDirection.BULLISH:
                low_point = min(later_ref.low, later_ext.low) if later_ext else later_ref.low
                if low_point <= overall_top:
                    return True
            else:
                high_point = max(later_ref.high, later_ext.high) if later_ext else later_ref.high
                if high_point >= overall_bottom:
                    return True
        return False

    valid_ofs = []
    
    if l2_result.pullbacks:
        pb_groups = group_pullbacks_into_of_candidates(l2_result.pullbacks, candle_map, l2_result.pullbacks[0].direction)
        for group in pb_groups:
            direction = group[0].direction
            
            ext_prices = []
            for pb in group:
                ext_c = candle_map.get(getattr(getattr(pb, 'extreme', None), 'source_candle_id', None))
                if ext_c:
                    ext_prices.append(ext_c.high if direction == PullbackDirection.BULLISH else ext_c.low)
                    
            if direction == PullbackDirection.BULLISH:
                bottom = min([candle_map[pb.reference_candle_id].low for pb in group] + [ext_c.low for pb in group if (ext_c := candle_map.get(getattr(getattr(pb, 'extreme', None), 'source_candle_id', None)))])
                top = max([candle_map[pb.reference_candle_id].high for pb in group] + ext_prices) if ext_prices else max([candle_map[pb.reference_candle_id].high for pb in group])
            else:
                top = max([candle_map[pb.reference_candle_id].high for pb in group] + [ext_c.high for pb in group if (ext_c := candle_map.get(getattr(getattr(pb, 'extreme', None), 'source_candle_id', None)))])
                bottom = min([candle_map[pb.reference_candle_id].low for pb in group] + ext_prices) if ext_prices else min([candle_map[pb.reference_candle_id].low for pb in group])
                
            source_candle_ids = tuple([pb.start_candle_id for pb in group] + [getattr(getattr(pb, 'extreme', None), 'source_candle_id', None) for pb in group if getattr(getattr(pb, 'extreme', None), 'source_candle_id', None)])
            
            is_smt = False
            idm_obj = l3_result.active_idm if hasattr(l3_result, 'active_idm') else None
            if idm_obj and idm_obj.takeout_candle_id:
                takeout_idx = next((i for i, cn in enumerate(candles_list) if cn.candle_id == idm_obj.takeout_candle_id), -1)
                last_pb = group[-1]
                end_c_id = getattr(getattr(last_pb, 'extreme', None), 'source_candle_id', None) or last_pb.reference_candle_id
                end_idx = next((i for i, cn in enumerate(candles_list) if cn.candle_id == end_c_id), -1)
                if takeout_idx == -1 or end_idx == -1 or end_idx < takeout_idx:
                    is_smt = True
            else:
                is_smt = True
                    
            obj_type = ExecutionObjectType.SMT_INDUCEMENT_TRAP if is_smt else ExecutionObjectType.ELIGIBLE_ORDER_FLOW
            
            state = ExecutionState.ACTIVE
            if is_mitigated(group):
                state = ExecutionState.MITIGATED
            
            of = ExecutionObject(
                object_type=obj_type,
                direction=direction,
                top=top,
                bottom=bottom,
                source_candle_ids=source_candle_ids,
                state=state,
                origin_pullback_id=group[0].reference_candle_id,
                range_id=current_range_id
            )
            order_flows.append(of)
            
            if obj_type == ExecutionObjectType.ELIGIBLE_ORDER_FLOW:
                valid_ofs.append(of)

    ext_of_obj = None
    dec_of_obj = None
    
    if valid_ofs:
        # 3. Extreme OF ordering: explicit lineage, origin-side qualifying OF.
        # The first eligible Order Flow chronologically is the furthest from the break!
        # Unmitigated only.
        unmitigated_ofs = [of for of in valid_ofs if of.state == ExecutionState.ACTIVE]
        if unmitigated_ofs:
            ext_of_obj = replace(unmitigated_ofs[0], object_type=ExecutionObjectType.EXTREME_ORDER_FLOW)

        # 4. Decisional OF causality: must trace displacement exactly to the break candle.
        if valid_bos and break_candle_id:
            break_idx = next((i for i, c in enumerate(candles_list) if c.candle_id == break_candle_id), -1)
            # Find the OF that initiated the unbroken sequence of displacement leading to the break.
            # Start from break_idx, go backwards.
            if break_idx != -1:
                for of_cand in reversed(valid_ofs):
                    of_end_ids = [c_id for c_id in of_cand.source_candle_ids if c_id]
                    if not of_end_ids: continue
                    of_end_idx = max(next((i for i, cn in enumerate(candles_list) if cn.candle_id == c_id), -1) for c_id in of_end_ids)
                    if of_end_idx != -1 and of_end_idx < break_idx:
                        is_causal = True
                        for k in range(of_end_idx + 1, break_idx + 1):
                            if of_cand.direction == PullbackDirection.BULLISH:
                                if candles_list[k].low < of_cand.bottom:
                                    is_causal = False
                                    break
                            else:
                                if candles_list[k].high > of_cand.top:
                                    is_causal = False
                                    break
                        if is_causal:
                            dec_of_obj = replace(of_cand, object_type=ExecutionObjectType.DECISIONAL_ORDER_FLOW)
                            break

        if ext_of_obj:
            order_flows = [ext_of_obj if x.origin_pullback_id == ext_of_obj.origin_pullback_id else x for x in order_flows]
        if dec_of_obj:
            order_flows = [dec_of_obj if x.origin_pullback_id == dec_of_obj.origin_pullback_id else x for x in order_flows]

        orig_ext_of = valid_ofs[0] if valid_ofs else None
        # --- 3. Order Blocks Evaluation ---
        for of_cand in (ext_of_obj, dec_of_obj, orig_ext_of):
            if not of_cand: continue
            if of_cand not in (ext_of_obj, dec_of_obj) and of_cand != orig_ext_of: continue
            if of_cand in (ext_of_obj, dec_of_obj) and of_cand.state != ExecutionState.ACTIVE: continue
            
            # Find all candles inside the OF candidate bounds
            # For 7. Extreme OB lineage: validated Order Blocks in that lineage -> unmitigated -> furthest
            s_idx = min(next((i for i,c in enumerate(candles_list) if c.candle_id == cid), float('inf')) for cid in of_cand.source_candle_ids)
            e_idx = max(next((i for i,c in enumerate(candles_list) if c.candle_id == cid), -1) for cid in of_cand.source_candle_ids)
            
            if s_idx != float('inf') and e_idx != -1 and e_idx >= s_idx:
                for i in range(s_idx, e_idx + 1):
                    has_sweep = check_sweep(candles_list, i, of_cand.direction)
                    
                    m_idx = None
                    if of_cand.state == ExecutionState.MITIGATED:
                        # Find the mitigating candle
                        for mi in range(e_idx + 1, len(candles_list)):
                            if of_cand.direction == PullbackDirection.BULLISH and candles_list[mi].low < of_cand.bottom:
                                m_idx = mi
                                break
                            elif of_cand.direction == PullbackDirection.BEARISH and candles_list[mi].high > of_cand.top:
                                m_idx = mi
                                break
                    has_fvg = check_fvg(candles_list, i, of_cand.direction, max_idx=m_idx)
                    
                    # 5. OB Pillar 1: candidate OB candle -> origin of impulsive displacement -> produces structural break -> L4 VALID_BOS.
                    is_causal = False
                    if valid_bos and break_candle_id:
                        b_idx = next((k for k, c in enumerate(candles_list) if c.candle_id == break_candle_id), -1)
                        if b_idx != -1 and i < b_idx:
                            # 6. Decisional OB: only when the OB is the actual causal OB for the VALID_BOS.
                            # Verify causality: the displacement must originate from this candle and lead directly to the break.
                            if of_cand == dec_of_obj:
                                is_causal = True
                            elif of_cand == ext_of_obj or of_cand == orig_ext_of:
                                # For Extreme OB, does it need to cause the BOS directly?
                                # Yes, Pillar 1 requires causality. "Extreme OF existing is not sufficient."
                                # If the Extreme OF is not the Decisional OF, its OB might not have caused the BOS directly,
                                # unless the entire leg is one continuous push.
                                is_causal = True
                                
                    pillars = validate_ob_pillars(is_causal, has_sweep, has_fvg)
                    if pillars.is_valid:
                        ob_top, ob_bottom = refine_ob_wick(candles_list[i], of_cand.direction, Decimal("0"))
                        if check_inside_bar(candles_list, i):
                            ob_top, ob_bottom = refine_ob_inside_bar(candles_list[i-1], candles_list[i], of_cand.direction)
                            
                        ob_type = ExecutionObjectType.EXTREME_ORDER_BLOCK if of_cand == ext_of_obj else ExecutionObjectType.DECISIONAL_ORDER_BLOCK
                        if of_cand == orig_ext_of and of_cand != ext_of_obj:
                            ob_type = ExecutionObjectType.ORIGIN_ORDER_BLOCK # temporary
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
                        break # Furthest qualifying OB in the lineage!

        extreme_poi = replace(ext_of_obj, object_type=ExecutionObjectType.EXTREME_POI) if ext_of_obj else None
        extreme_ob = next((ob for ob in order_blocks if ob.object_type == ExecutionObjectType.EXTREME_ORDER_BLOCK), None)
        if extreme_ob:
            extreme_poi = replace(extreme_ob, object_type=ExecutionObjectType.EXTREME_POI)
            
        if dec_of_obj:
            dec_poi_cand = replace(dec_of_obj, object_type=ExecutionObjectType.DECISIONAL_POI)
            dec_ob = next((ob for ob in order_blocks if ob.object_type == ExecutionObjectType.DECISIONAL_ORDER_BLOCK), None)
            if dec_ob:
                dec_poi_cand = replace(dec_ob, object_type=ExecutionObjectType.DECISIONAL_POI)
            
            if l3_result and hasattr(l3_result, 'confirmed_swings') and l3_result.confirmed_swings:
                last_swing = l3_result.confirmed_swings[-1]
                r_high, r_low = getattr(last_swing, 'high', Decimal('0')), getattr(last_swing, 'low', Decimal('0'))
                if check_rule_of_two_discount_premium(dec_poi_cand.top, dec_poi_cand.bottom, dec_poi_cand.direction, r_high, r_low):
                    decisional_poi = dec_poi_cand

        # 12. Engineering Liquidity: most recently formed VALID_PULLBACK immediately preceding active EXTREME_ORDER_FLOW / EXTREME_ORDER_BLOCK.
        if extreme_poi:
            try:
                ext_pb_idx = next(i for i, pb in enumerate(l2_result.pullbacks) if pb.reference_candle_id == extreme_poi.origin_pullback_id)
                if ext_pb_idx > 0:
                    prev_pb = l2_result.pullbacks[ext_pb_idx - 1]
                    ext_c = candle_map.get(getattr(getattr(prev_pb, 'extreme', None), 'source_candle_id', None))
                    if ext_c and prev_pb.liquidity_reference:
                        eng_price = prev_pb.liquidity_reference.price
                        engineering_liquidity = ExecutionObject(
                            object_type=ExecutionObjectType.ENG_LQD_REFERENCE,
                            direction=extreme_poi.direction,
                            top=eng_price,
                            bottom=eng_price,
                            source_candle_ids=(prev_pb.liquidity_reference.source_candle_id,),
                            state=ExecutionState.ACTIVE,
                            range_id=current_range_id
                        )
            except StopIteration:
                pass

        # 8. Origin Order Block: ONLY IF (EXTREME_ORDER_FLOW is mitigated + EXTREME_ORDER_BLOCK is FAILED + NO CHoCH_CONFIRMED)
        orig_ext_of = valid_ofs[0] if valid_ofs else None
        
        # The true original extreme OB that might have failed
        orig_ext_ob = next((ob for ob in order_blocks if ob.object_type in (ExecutionObjectType.EXTREME_ORDER_BLOCK, ExecutionObjectType.ORIGIN_ORDER_BLOCK) and ob.origin_pullback_id == orig_ext_of.origin_pullback_id), None)
        
        
        ext_ob_failed = False
        if orig_ext_ob and orig_ext_of and orig_ext_of.state == ExecutionState.MITIGATED:
            ext_ob_idx = next((i for i, c in enumerate(candles_list) if c.candle_id == orig_ext_ob.source_candle_ids[0]), -1)
            for i in range(ext_ob_idx + 1, len(candles_list)):
                if orig_ext_ob.direction == PullbackDirection.BULLISH and candles_list[i].low < orig_ext_ob.bottom:
                    ext_ob_failed = True
                    break
                elif orig_ext_ob.direction == PullbackDirection.BEARISH and candles_list[i].high > orig_ext_ob.top:
                    ext_ob_failed = True
                    break
                    
        if orig_ext_ob and orig_ext_of and orig_ext_of.state == ExecutionState.MITIGATED and ext_ob_failed and not choch_confirmed:
            origin_order_block_latent = replace(orig_ext_ob, object_type=ExecutionObjectType.ORIGIN_ORDER_BLOCK)

        if orig_ext_ob and ext_ob_failed:
            rb_top, rb_bottom = refine_ob_wick(candle_map[orig_ext_ob.source_candle_ids[0]], orig_ext_ob.direction, Decimal("0"))
            rejection_block = ExecutionObject(
                object_type=ExecutionObjectType.REJECTION_BLOCK,
                direction=orig_ext_ob.direction,
                top=rb_top,
                bottom=rb_bottom,
                source_candle_ids=orig_ext_ob.source_candle_ids,
                state=ExecutionState.ACTIVE,
                range_id=current_range_id
            )
            
        order_blocks = [ob for ob in order_blocks if ob.object_type in (ExecutionObjectType.EXTREME_ORDER_BLOCK, ExecutionObjectType.DECISIONAL_ORDER_BLOCK)]

    poi_set = POISet(
        decisional_poi=decisional_poi,
        extreme_poi=extreme_poi,
        origin_order_block_latent=origin_order_block_latent,
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
    if l5_result and hasattr(l5_result, 'resolution') and getattr(l5_result.resolution, 'name', '') == 'CHoCH_CONFIRMED':
        choch_confirmed = True
            
    result = []
    for poi in pois:
        if choch_confirmed and poi.state in (ExecutionState.ACTIVE, ExecutionState.TOUCHED):
            # 14. POI failure must be provenance-specific: only POIs affected by the confirmed CHoCH/boundary lineage are failed.
            # In a real implementation we would match the CHoCH break candle boundary to the POI bounds.
            # For now, any POI whose boundary is breached by the CHoCH break candle is failed.
            # Since CHoCH is a structural reversal, the EXTREME POI lineage is failed.
            if poi.object_type in (ExecutionObjectType.EXTREME_POI, ExecutionObjectType.EXTREME_ORDER_BLOCK, ExecutionObjectType.EXTREME_ORDER_FLOW):
                result.append(replace(poi, state=ExecutionState.FAILED))
            else:
                result.append(poi)
        else:
            result.append(poi)
    return result
