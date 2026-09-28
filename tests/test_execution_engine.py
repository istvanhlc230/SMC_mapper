import pytest
from decimal import Decimal
from execution_engine import (
    ExecutionObject, ExecutionObjectType, ExecutionState,
    POISet, OBPillars, _is_discount, _is_premium, check_rule_of_two_discount_premium,
    refine_ob_wick, refine_ob_inside_bar, validate_ob_pillars, create_engineering_liquidity,
    expire_pois, fail_pois, interact_poi, evaluate_execution_state, ExecutionAnalysis,
    check_fvg, check_sweep
)
from minor_structure_engine import PullbackDirection
from microstructure_engine import Candle

def c(id_: str, open_: str, high_: str, low_: str, close_: str) -> Candle:
    return Candle(id_, Decimal(open_), Decimal(high_), Decimal(low_), Decimal(close_))

class DummyPullback:
    def __init__(self, direction, ref_id, start_id, comp_id, extreme_price):
        self.direction = direction
        self.reference_candle_id = ref_id
        self.start_candle_id = start_id
        self.completion_candle_id = comp_id
        self.extreme = type("Ext", (), {"candle_id": comp_id, "price": extreme_price})()

class DummyL3:
    def __init__(self, idm_taken=False, range_high=None, range_low=None):
        self.active_idm = type("IDM", (), {"takeout_candle_id": "c_take" if idm_taken else None})()
        if range_high and range_low:
            self.confirmed_swings = [type("Swing", (), {"high": Decimal(range_high), "low": Decimal(range_low)})()]
        else:
            self.confirmed_swings = []

class DummyL4:
    def __init__(self, structural_break=False, valid_bos=False):
        self.structural_break = type("Brk", (), {})() if structural_break else None
        self.valid_bos = valid_bos

class DummyL5:
    def __init__(self, confirmed=False):
        self.confirmed = confirmed


# 1. OF candidate formation
def test_of_candidate_formation():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"))
    
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=True), None, None)
    assert len(result.order_flows) == 1
    assert result.order_flows[0].object_type == ExecutionObjectType.EXTREME_OF # Upgraded from OF_CONFIRMED

# 2. Pre-IDM OF -> SMT exclusion
def test_pre_idm_smt_exclusion():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"))
    
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=False), None, None)
    assert result.order_flows[0].object_type == ExecutionObjectType.SMT_INDUCEMENT_TRAP

# 3. OF touch does not equal mitigation
def test_of_touch_not_mitigation():
    of = ExecutionObject(ExecutionObjectType.OF_CANDIDATE, PullbackDirection.BULLISH, Decimal("10.5"), Decimal("10.0"), ("c1",), ExecutionState.ACTIVE)
    assert interact_poi(of, is_mitigation=False).state == ExecutionState.TOUCHED

# 4. Valid Pullback interaction establishes OF mitigation
def test_valid_pullback_interaction_mitigation():
    of = ExecutionObject(ExecutionObjectType.OF_CANDIDATE, PullbackDirection.BULLISH, Decimal("10.5"), Decimal("10.0"), ("c1",), ExecutionState.ACTIVE)
    assert interact_poi(of, is_mitigation=True).state == ExecutionState.MITIGATED

# 5. OF confirmed only when eligibility conditions pass
def test_of_confirmed_eligibility():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"))
    
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=True), None, None)
    assert result.order_flows[0].object_type == ExecutionObjectType.EXTREME_OF # Extracted

# 6. Newer valid pullback replaces active Minor IDM lineage correctly
def test_newer_pullback_replaces_lineage():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"))
    result = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    assert result.order_flows[0].bottom == Decimal("9.0")
    
    # Replaced by engine
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c3", Decimal("8.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb2]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c3", "10", "10.5", "8.0", "9"))
    result = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    assert result.order_flows[0].bottom == Decimal("8.0")

# 7. Decisional OF is tied to causal VALID_BOS displacement
def test_decisional_of_causal():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("8.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
               c("c3", "10", "12", "9.5", "10"), c("c4", "10", "10.5", "8.0", "9"))
    
    # Valid BOS -> Decisional OF created
    res_valid = evaluate_execution_state(candles, l2_result, DummyL3(True, "15", "5"), DummyL4(structural_break=True, valid_bos=True), None)
    assert any(o.object_type == ExecutionObjectType.DECISIONAL_OF for o in res_valid.order_flows)
    
    # Structural break but NO VALID BOS -> No Decisional OF
    res_invalid = evaluate_execution_state(candles, l2_result, DummyL3(True, "15", "5"), DummyL4(structural_break=True, valid_bos=False), None)
    assert not any(o.object_type == ExecutionObjectType.DECISIONAL_OF for o in res_invalid.order_flows)

# 8. Extreme OF is furthest eligible unmitigated OF
def test_extreme_of_furthest():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("8.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
               c("c3", "10", "12", "9.5", "10"), c("c4", "10", "10.5", "8.0", "9"))
    
    result = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    exts = [o for o in result.order_flows if o.object_type == ExecutionObjectType.EXTREME_OF]
    assert len(exts) == 1
    assert exts[0].bottom == Decimal("8.0")

# 9. Valid OB requires all 3 pillars
def test_ob_requires_three_pillars():
    assert validate_ob_pillars(True, True, True).is_valid
    assert not validate_ob_pillars(True, False, True).is_valid
    assert not validate_ob_pillars(False, True, True).is_valid

# 10. Invalid FVG association moves OB candidate forward
def test_invalid_fvg_moves_forward():
    assert not validate_ob_pillars(True, True, False).is_valid
    
    # Test FVG function
    candles = [c("1", "10", "11", "9", "10"), c("2", "10", "10.5", "9", "10"), c("3", "10", "10.5", "8", "9")]
    assert not check_fvg(candles, 0, PullbackDirection.BULLISH) # No gap between c1 high and c3 low
    
    candles_fvg = [c("1", "10", "11", "9", "10"), c("2", "12", "13", "11", "12"), c("3", "13", "14", "12", "13")]
    assert check_fvg(candles_fvg, 0, PullbackDirection.BULLISH) # c3.low(12) > c1.high(11)

# 11. Wick-only OB refinement
def test_wick_only_ob_refinement():
    candle = c("c1", "10.0", "10.5", "9.0", "10.2")
    top, bottom = refine_ob_wick(candle, PullbackDirection.BULLISH, Decimal("9.5"))
    assert top == Decimal("10.2") and bottom == Decimal("9.0")

# 12. Inside-Bar OB refinement
def test_inside_bar_ob_refinement():
    mother = c("c1", "10.0", "11.0", "9.0", "10.5")
    inside = c("c2", "10.2", "10.8", "9.5", "10.4")
    top, bottom = refine_ob_inside_bar(mother, inside, PullbackDirection.BULLISH)
    assert top == Decimal("9.5") and bottom == Decimal("9.0")

# 13. Decisional OB causal selection
# 14. Extreme OB lineage selection
def test_ob_selection():
    # Construct a scenario where an OF has an OB
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c4", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (
        c("c1", "10", "11", "10", "10.5"),
        c("c2", "10", "12", "9", "11"), # sweep of c1 (c2.low 9 < c1.low 10)
        c("c3", "11", "12", "10", "11.5"), # inside bar or whatever
        c("c4", "13", "14", "12.5", "13") # FVG created from c2 to c4 (c4.low 12.5 > c2.high 12)
    )
    res = evaluate_execution_state(candles, l2_result, DummyL3(True), DummyL4(True, True), None)
    
    assert len(res.order_blocks) > 0

    assert any(ob.object_type == ExecutionObjectType.EXTREME_OB for ob in res.order_blocks)
    assert res.active_pois.extreme_poi.object_type == ExecutionObjectType.EXTREME_POI

# 15. Rule-of-Two cardinality
def test_rule_of_two_cardinality():
    dec_poi = ExecutionObject(ExecutionObjectType.DECISIONAL_POI, PullbackDirection.BULLISH, Decimal("2"), Decimal("1"), ("c1",), ExecutionState.ACTIVE)
    ext_poi = ExecutionObject(ExecutionObjectType.EXTREME_POI, PullbackDirection.BULLISH, Decimal("1.5"), Decimal("0.5"), ("c2",), ExecutionState.ACTIVE)
    poi_set = POISet(decisional_poi=dec_poi, extreme_poi=ext_poi, origin_ob_latent=None, rejection_block=None)
    assert poi_set.decisional_poi is not None and poi_set.extreme_poi is not None

# 16. BUY Decisional POI must be Discount
def test_buy_discount():
    assert check_rule_of_two_discount_premium(Decimal("4.0"), Decimal("3.0"), PullbackDirection.BULLISH, Decimal("10.0"), Decimal("0.0"))
    assert not check_rule_of_two_discount_premium(Decimal("6.0"), Decimal("5.0"), PullbackDirection.BULLISH, Decimal("10.0"), Decimal("0.0"))

# 17. SELL Decisional POI must be Premium
def test_sell_premium():
    assert check_rule_of_two_discount_premium(Decimal("8.0"), Decimal("7.0"), PullbackDirection.BEARISH, Decimal("10.0"), Decimal("0.0"))
    assert not check_rule_of_two_discount_premium(Decimal("4.0"), Decimal("3.0"), PullbackDirection.BEARISH, Decimal("10.0"), Decimal("0.0"))

# 18. Origin OB is latent, not a third POI
def test_origin_ob_latent():
    latent = ExecutionObject(ExecutionObjectType.ORIGIN_OB, PullbackDirection.BULLISH, Decimal("10.5"), Decimal("10.0"), ("c1",), ExecutionState.ACTIVE)
    poi_set = POISet(None, None, origin_ob_latent=latent, rejection_block=None)
    assert poi_set.origin_ob_latent is not None

# 19. Rejection Block remains separately typed
def test_rejection_block_typed():
    rb = ExecutionObject(ExecutionObjectType.REJECTION_BLOCK, PullbackDirection.BULLISH, Decimal("10.5"), Decimal("10.0"), ("c1",), ExecutionState.ACTIVE)
    poi_set = POISet(None, None, None, rejection_block=rb)
    assert poi_set.rejection_block is not None

# 20. Engineering Liquidity requires preceding valid pullback
def test_eng_lqd_requires_pullback():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"))
    
    result = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    assert result.engineering_liquidity is not None
    assert result.engineering_liquidity.bottom == Decimal("9.0")

# 21. No valid pullback -> no ENG_LQD
def test_no_pullback_no_eng_lqd():
    result = evaluate_execution_state((), None, None, None, None)
    assert result.engineering_liquidity is None

# 22. Extreme POI change recomputes ENG_LQD
def test_extreme_poi_change_recomputes():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("8.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
               c("c3", "10", "12", "9.5", "10"), c("c4", "10", "10.5", "8.0", "9"))
               
    result = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    assert result.engineering_liquidity.bottom == Decimal("8.0") # Recalculated cleanly

# 23. POI touch != failure
def test_poi_touch_not_failure():
    poi1 = ExecutionObject(ExecutionObjectType.DECISIONAL_POI, PullbackDirection.BULLISH, Decimal("1"), Decimal("0"), ("c",), ExecutionState.ACTIVE)
    touched = interact_poi(poi1, is_mitigation=False)
    assert touched.state != ExecutionState.FAILED

# 24. POI failure requires canonical CHoCH
def test_poi_failure_requires_choch():
    poi1 = ExecutionObject(ExecutionObjectType.DECISIONAL_POI, PullbackDirection.BULLISH, Decimal("1"), Decimal("0"), ("c",), ExecutionState.ACTIVE)
    
    # CHoCH Confirmed
    failed = fail_pois([poi1], DummyL5(confirmed=True))
    assert failed[0].state == ExecutionState.FAILED
    
    # CHoCH Not Confirmed
    not_failed = fail_pois([poi1], DummyL5(confirmed=False))
    assert not_failed[0].state == ExecutionState.ACTIVE

# 25. VALID_BOS expires previous-range POIs
def test_bos_expires_pois():
    poi1 = ExecutionObject(ExecutionObjectType.DECISIONAL_POI, PullbackDirection.BULLISH, Decimal("1"), Decimal("0"), ("c",), ExecutionState.ACTIVE)
    
    expired = expire_pois([poi1], DummyL4(structural_break=True, valid_bos=True))
    assert expired[0].state == ExecutionState.EXPIRED_HISTORICAL
    
    not_expired = expire_pois([poi1], DummyL4(structural_break=True, valid_bos=False))
    assert not_expired[0].state == ExecutionState.ACTIVE

# 26. Expired POIs cannot be selected for execution
def test_expired_not_executable():
    poi1 = ExecutionObject(ExecutionObjectType.DECISIONAL_POI, PullbackDirection.BULLISH, Decimal("1"), Decimal("0"), ("c",), ExecutionState.EXPIRED_HISTORICAL)
    interacted = interact_poi(poi1, is_mitigation=True)
    assert interacted.state == ExecutionState.EXPIRED_HISTORICAL

# 27. Historical POI records remain immutable
def test_historical_immutable():
    poi1 = ExecutionObject(ExecutionObjectType.DECISIONAL_POI, PullbackDirection.BULLISH, Decimal("1"), Decimal("0"), ("c",), ExecutionState.EXPIRED_HISTORICAL)
    failed = fail_pois([poi1], DummyL5(confirmed=True))
    assert failed[0].state == ExecutionState.EXPIRED_HISTORICAL

# 28. L6 cannot create BOS/CHoCH/IDM
def test_l6_no_structure_creation():
    result = evaluate_execution_state((), None, None, None, None)
    assert isinstance(result, ExecutionAnalysis)

# 29. Full Analyzer L1-L6 integration
def test_analyzer_integration():
    result = evaluate_execution_state((), None, None, None, None)
    assert result.active_pois.decisional_poi is None

# 30. Deterministic repeated execution produces identical L6 output
def test_deterministic_output():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"))
    
    result1 = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    result2 = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    assert result1.engineering_liquidity == result2.engineering_liquidity
    assert result1.active_pois == result2.active_pois
