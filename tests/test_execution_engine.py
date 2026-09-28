import pytest
from decimal import Decimal
from execution_engine import (
    ExecutionObject, ExecutionObjectType, ExecutionState,
    POISet, OBPillars, _is_discount, _is_premium, check_rule_of_two_discount_premium,
    refine_ob_wick, refine_ob_inside_bar, validate_ob_pillars,
    expire_pois, fail_pois, evaluate_execution_state, ExecutionAnalysis,
    check_fvg, check_sweep
)
from minor_structure_engine import PullbackDirection, CandleLevelValidPullback, VerifiedPullbackExtreme, PullbackDerivedLiquidityReference, LiquiditySide
from microstructure_engine import Candle

def c(id_: str, open_: str, high_: str, low_: str, close_: str) -> Candle:
    return Candle(id_, Decimal(open_), Decimal(high_), Decimal(low_), Decimal(close_))

class DummyL3:
    def __init__(self, idm_taken=False, range_high=None, range_low=None, num_swings=1, idm_price=Decimal("15.0")):
        self.active_idm = type("IDM", (), {"takeout_candle_id": "c_take" if idm_taken else None, "reference_price": idm_price, "source_candle_id": "c_idm"})()
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

# --- Test 1: IDM_TAKEN without genuine OF Candidate -> no OF_CONFIRMED ---
def test_idm_taken_but_smt():
    # IDM taken is true, but pullback is higher than IDM -> SMT
    pb1 = make_pb("c1", "c1", "c2", "c2", "15.5")
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "15.1", "16", "15", "15.5"), c("c2", "15.6", "15.8", "15.5", "15.7"))
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=True, idm_price=Decimal("15.0")), None, None)
    assert result.order_flows[0].object_type == ExecutionObjectType.SMT_INDUCEMENT_TRAP

# --- Test 2: Mitigation logic ---
def test_geometric_overlap_without_valid_pullback_does_not_mitigate():
    # pb1 top is 11, bottom 9.
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    # c3 drops to 8.0, but it is NOT a valid pullback in L2 result!
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
        c("c3", "10", "12", "8.0", "9") # Dips into pb1, but NO PULLBACK generated!
    )
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=True, idm_price=Decimal("15.0")), None, None)
    # MUST REMAIN ACTIVE!
    assert result.order_flows[0].state == ExecutionState.ACTIVE

def test_of_mitigation_from_l2():
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    pb2 = make_pb("c3", "c3", "c4", "c4", "8.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"), # PB1 top 11, bottom 9
        c("c3", "11.1", "12", "11.1", "11.5"), c("c4", "10", "10.5", "8.0", "9")  # PB2 drops to 8.0, mitigating PB1
    )
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=True, idm_price=Decimal("15.0")), None, None)
    assert result.order_flows[0].state == ExecutionState.MITIGATED

# --- Test 3: Closest OF before BOS but wrong causal lineage -> not DECISIONAL_OF ---
def test_decisional_of_wrong_lineage():
    # PB1 and PB2. Break candle is c6. PB2 completes AFTER the break candle!
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    pb2 = make_pb("c7", "c7", "c8", "c8", "10.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
        c("c5", "12", "13", "11.5", "12.5"), c("c6", "13", "15", "12.5", "14"), # c6 is break_candle_id
        c("c7", "11.1", "12", "11.1", "11.5"), c("c8", "11.2", "12", "11.1", "11.5"), # PB2 completes AFTER BOS!
    )
    l4_result = DummyL4(structural_break=True, valid_bos=True, break_c_id="c6")
    res_valid = evaluate_execution_state(candles, l2_result, DummyL3(True, "15", "5"), l4_result, None)
    dec_of = next((o for o in res_valid.order_flows if o.object_type == ExecutionObjectType.DECISIONAL_OF), None)
    assert dec_of is not None
    assert dec_of.origin_pullback_id == "c1" # PB1 is selected because PB2 is after the BOS!

# --- Test 4: Extreme OF alone -> must not satisfy Pillar 1 ---
def test_extreme_of_alone_no_pillar1():
    # Extreme OF exists. But L4 valid_bos is FALSE!
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (
        c("c1", "10", "11", "10", "10.5"),
        c("c2", "10", "12", "9", "11"), # sweep, FVG!
        c("c3", "11", "12", "10", "11.5"),
        c("c4", "12.5", "14", "12.5", "13")
    )
    # L4 valid_bos is FALSE
    res = evaluate_execution_state(candles, l2_result, DummyL3(True), DummyL4(False, False), None)
    # Even though sweep and FVG exist, is_causal is False, so Pillar 1 fails!
    assert len(res.order_blocks) == 0

# --- Test 5: Origin OB and RB ---
def test_origin_ob_reachable():
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    pb2 = make_pb("c3", "c3", "c4", "c4", "8.0") # mitigates PB1
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"), # PB1 top 11, bottom 9
        c("c3", "11.1", "12", "11.1", "11.5"), c("c4", "10", "10.5", "8.0", "9")  # PB2 drops to 8.0
    )
    result = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    assert result.active_pois.origin_ob_latent is not None
    assert result.active_pois.origin_ob_latent.object_type == ExecutionObjectType.ORIGIN_OB

def test_rb_reachable():
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (
        c("c1", "10", "11", "10", "10.5"),
        c("c2", "10", "12", "9", "11"), # sweep
        c("c3", "11", "12", "10", "11.5"),
        c("c4", "12.5", "14", "12.5", "13")
    )
    # L5 CHoCH confirmed -> Extreme OB fails -> RB
    res = evaluate_execution_state(candles, l2_result, DummyL3(True), DummyL4(True, True, "c4"), DummyL5(True))
    assert res.active_pois.rejection_block is not None
    assert res.active_pois.rejection_block.object_type == ExecutionObjectType.REJECTION_BLOCK

# --- Test 6: Engineering Liquidity Dependency ---
def test_eng_lqd_valid_pullback_preceding():
    pb1 = make_pb("c1", "c1", "c2", "c2", "9.0")
    pb2 = make_pb("c3", "c3", "c4", "c4", "10.0") 
    pb3 = make_pb("c5", "c5", "c6", "c6", "11.0")
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2, pb3]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"), 
        c("c3", "10", "10.5", "9", "9.5"), c("c4", "9", "10", "8.0", "8.5"), # mitigates pb1. So pb2 is extreme!
        c("c5", "11.1", "12", "11.1", "11.5"), c("c6", "11.2", "12", "11.1", "11.5")
    )
    result = evaluate_execution_state(candles, l2_result, DummyL3(True, "15.0", "0"), None, None)
    assert result.engineering_liquidity is not None
    assert result.engineering_liquidity.bottom == Decimal("9.0")
