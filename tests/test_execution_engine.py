import pytest
from decimal import Decimal
from execution_engine import (
    ExecutionObject, ExecutionObjectType, ExecutionState,
    POISet, OBPillars, check_rule_of_two_discount_premium,
    refine_ob_wick, refine_ob_inside_bar, validate_ob_pillars,
    expire_pois, fail_pois, evaluate_execution_state, ExecutionAnalysis,
    check_fvg, check_sweep
)
from minor_structure_engine import PullbackDirection, CandleLevelValidPullback, VerifiedPullbackExtreme, PullbackDerivedLiquidityReference, LiquiditySide
from microstructure_engine import Candle

def c(id_: str, open_: str, high_: str, low_: str, close_: str) -> Candle:
    return Candle(id_, Decimal(open_), Decimal(high_), Decimal(low_), Decimal(close_))

class DummyL3:
    def __init__(self, idm_taken=False, range_high=None, range_low=None, num_swings=1, idm_price=Decimal("15.0"), range_id="range_0", takeout_candle_id=None):
        _takeout = takeout_candle_id if takeout_candle_id else ("c_take" if idm_taken else None)
        self.active_idm = type("IDM", (), {"takeout_candle_id": _takeout, "reference_price": idm_price, "source_candle_id": "c_idm"})()
        self.active_dealing_range = type("Range", (), {"range_id": range_id})()
        if range_high and range_low:
            self.confirmed_swings = [type("Swing", (), {"high": Decimal(range_high), "low": Decimal(range_low), "source_candle_id": f"sc_{i}"})() for i in range(num_swings)]
        else:
            self.confirmed_swings = []

class DummyL4:
    def __init__(self, structural_break=False, valid_bos=False, break_c_id=None):
        self.structural_break = type("Brk", (), {"break_candle_id": break_c_id})() if structural_break else None
        self.valid_bos = valid_bos

class DummyL5:
    def __init__(self, confirmed=False):
        self.resolution = type("Res", (), {"name": "CHOCH_CONFIRMED" if confirmed else "CHOCH_ELIGIBLE"})()

def make_pb(ref, start, comp, ext_c, ext_p):
    return CandleLevelValidPullback(
        direction=PullbackDirection.BULLISH,
        reference_candle_id=ref,
        start_candle_id=start,
        completion_candle_id=comp,
        extreme=VerifiedPullbackExtreme(price=Decimal(ext_p), source_candle_id=ext_c, direction=PullbackDirection.BULLISH),
        liquidity_reference=PullbackDerivedLiquidityReference(side=LiquiditySide.SELL_SIDE, price=Decimal(ext_p), source_candle_id=ext_c)
    )

# 1. IDM_TAKEN but no real OF candidate -> no ELIGIBLE_ORDER_FLOW.
def test_idm_taken_but_smt():
    pb1 = make_pb("c1", "c1", "c2", "c2", "15.5")
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "15.1", "16", "15", "15.5"), c("c2", "15.6", "15.8", "15.5", "15.7"))
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=True, idm_price=Decimal("15.0")), None, None)
    assert result.order_flows[0].object_type == ExecutionObjectType.SMT_INDUCEMENT_TRAP

# 2. Post-IDM pullback that is not the last opposing move -> grouped into complex correction
def test_complex_correction_groups_pullbacks():
    pb1 = make_pb("c1", "c1", "c2", "c2", "10.0")
    pb2 = make_pb("c3", "c3", "c4", "c4", "9.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    # c3 is lower than c1, meaning PB2 did not break PB1's high before forming. It's a complex correction!
    candles = (
        c("c1", "11", "12", "10.5", "11"), c("c2", "10", "11", "10.0", "10.5"),
        c("c3", "10.5", "11.5", "10", "10.5"), c("c4", "9", "10", "9.0", "9.5")
    )
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=True, idm_price=Decimal("8.0")), None, None)
    # They should form ONE ELIGIBLE_ORDER_FLOW!
    assert len(result.order_flows) == 1
    assert result.order_flows[0].top == Decimal("12")
    assert result.order_flows[0].bottom == Decimal("9.0")

# 3. Touch/penetration without canonical Valid Pullback -> no mitigation.
def test_geometric_overlap_without_valid_pullback_does_not_mitigate():
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
        c("c3", "10", "12", "8.0", "9") # Dips into pb1, but NO PULLBACK generated!
    )
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=True, idm_price=Decimal("15.0")), None, None)
    assert result.order_flows[0].state == ExecutionState.ACTIVE

# 4. Closest OF but wrong causal lineage -> not DECISIONAL_ORDER_FLOW.
def test_decisional_of_wrong_lineage():
    # OF1 and OF2. Break candle is c6. OF2 completes AFTER the break candle!
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    pb2 = make_pb("c7", "c7", "c8", "c8", "10.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
        c("c5", "12", "13", "11.5", "12.5"), c("c6", "13", "15", "12.5", "14"), # c6 is break_candle_id
        c("c7", "11.1", "12", "11.1", "11.5"), c("c8", "11.2", "12", "11.1", "11.5")
    )
    res_valid = evaluate_execution_state(candles, l2_result, DummyL3(True, "15", "5", takeout_candle_id="c1"), DummyL4(True, True, "c6"), None)
    dec_of = next((o for o in res_valid.order_flows if o.object_type == ExecutionObjectType.DECISIONAL_ORDER_FLOW), None)
    assert dec_of is not None
    assert dec_of.origin_pullback_id == "c1" # PB1 is selected because PB2 is after the BOS!

# 5. Extreme OF alone -> not OB Pillar 1.
def test_extreme_of_alone_no_pillar1():
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (
        c("c1", "10", "11", "10", "10.5"), c("c2", "10", "12", "9", "11"), 
        c("c3", "11", "12", "10", "11.5"), c("c4", "12.5", "14", "12.5", "13")
    )
    res = evaluate_execution_state(candles, l2_result, DummyL3(True, takeout_candle_id="c1"), DummyL4(False, False), None)
    # Even though sweep and FVG exist, L4 valid_bos is FALSE, so Pillar 1 fails!
    assert len(res.order_blocks) == 0

# 6. Valid sweep + FVG but non-causal candle -> no VALIDATED_ORDER_BLOCK.
def test_valid_ob_wrong_lineage_no_pillar1():
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (
        c("c1", "10", "11", "10", "10.5"), c("c2", "10", "12", "9", "11"), 
        c("c3", "11", "12", "10", "11.5"), c("c4", "12.5", "14", "12.5", "13")
    )
    # L4 valid_bos is True, break is c1! So c2 didn't cause it!
    res = evaluate_execution_state(candles, l2_result, DummyL3(True, takeout_candle_id="c1"), DummyL4(True, True, "c1"), None)
    assert len(res.order_blocks) == 0

# 8. No failed Extreme OB -> no ORIGIN_ORDER_BLOCK.
def test_no_failed_extreme_ob_no_origin_ob():
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (
        c("c1", "10", "11", "10", "10.5"), c("c2", "10", "12", "9", "11"), 
        c("c3", "11", "12", "10", "11.5"), c("c4", "12.5", "14", "12.5", "13")
    )
    # Extreme OF is NOT mitigated, so Origin Order Block shouldn't activate.
    res = evaluate_execution_state(candles, l2_result, DummyL3(True, takeout_candle_id="c1"), DummyL4(True, True, "c4"), None)
    assert res.active_pois.origin_order_block_latent is None

# 9. CHoCH alone -> no RB.
def test_choch_alone_no_rb():
    # If no EXTREME_ORDER_BLOCK exists or failed, CHoCH does not create an RB.
    l2_result = type("L2Result", (), {"pullbacks": []})()
    candles = (c("c1", "10", "11", "10", "10.5"),)
    res = evaluate_execution_state(candles, l2_result, DummyL3(True, takeout_candle_id="c1"), DummyL4(False, False), DummyL5(True))
    assert res.active_pois.rejection_block is None

# 10. Wrong-lineage pullback -> no ENG_LQD.
def test_wrong_lineage_pullback_no_eng_lqd():
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "10", "11", "10", "10.5"), c("c2", "10", "12", "9", "11"))
    res = evaluate_execution_state(candles, l2_result, DummyL3(True, "15.0", "0"), None, None)
    # Only 1 pullback, so no "preceding" pullback exists.
    assert res.engineering_liquidity is None

# 11. Unrelated CHoCH -> POI remains active.
def test_unrelated_choch_poi_remains_active():
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "10", "11", "10", "10.5"), c("c2", "10", "12", "9", "11"))
    poi = ExecutionObject(ExecutionObjectType.DECISIONAL_POI, PullbackDirection.BULLISH, Decimal("10"), Decimal("9"), ("c1",), ExecutionState.ACTIVE)
    res = fail_pois([poi], DummyL5(True))
    # DECISIONAL POI should NOT be failed by CHoCH!
    assert res[0].state == ExecutionState.ACTIVE

# 12. Invalid POI ontology -> fail closed.
def test_invalid_poi_ontology_fails_closed():
    with pytest.raises(ValueError, match="decisional_poi must be DECISIONAL_POI"):
        poi = ExecutionObject(ExecutionObjectType.EXTREME_POI, PullbackDirection.BULLISH, Decimal("10"), Decimal("9"), ("c1",), ExecutionState.ACTIVE)
        POISet(decisional_poi=poi, extreme_poi=None, origin_order_block_latent=None, rejection_block=None)

# Extra: Real failure -> RB and Origin Order Block activation
def test_real_failure_origin_ob_and_rb():
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    pb2 = make_pb("c5", "c5", "c6", "c6", "8.0") # Mitigates pb1 later
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "12", "9", "11"), # PB1 OB candle c2
        c("c3", "11.5", "13", "11.1", "12"), c("c4", "13.1", "14", "12.5", "13"), # c4.low > c2.high -> FVG!
        c("c5", "14", "15", "13.5", "14.5"), c("c6", "10", "10.5", "8.0", "9"), # PB2 forms and fails c2!
        c("c7", "12", "14", "12", "13") # BOS candle
    )
    res = evaluate_execution_state(candles, l2_result, DummyL3(True, takeout_candle_id="c1"), DummyL4(True, True, "c7"), DummyL5(False))
    assert res.active_pois.origin_order_block_latent is not None
    assert res.active_pois.origin_order_block_latent.object_type == ExecutionObjectType.ORIGIN_ORDER_BLOCK
    assert res.active_pois.rejection_block is not None
    assert res.active_pois.rejection_block.object_type == ExecutionObjectType.REJECTION_BLOCK
