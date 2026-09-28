import pytest
from decimal import Decimal
from execution_engine import (
    ExecutionObject, ExecutionObjectType, ExecutionState,
    POISet, OBPillars, _is_discount, _is_premium, check_rule_of_two_discount_premium,
    refine_ob_wick, refine_ob_inside_bar, validate_ob_pillars, create_engineering_liquidity,
    expire_pois, fail_pois, evaluate_execution_state, ExecutionAnalysis,
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
    def __init__(self, idm_taken=False, range_high=None, range_low=None, num_swings=1, idm_price=Decimal("15.0")):
        self.active_idm = type("IDM", (), {"takeout_candle_id": "c_take" if idm_taken else None, "reference_price": idm_price})()
        if range_high and range_low:
            self.confirmed_swings = [type("Swing", (), {"high": Decimal(range_high), "low": Decimal(range_low)})() for _ in range(num_swings)]
        else:
            self.confirmed_swings = []

class DummyL4:
    def __init__(self, structural_break=False, valid_bos=False):
        self.structural_break = type("Brk", (), {})() if structural_break else None
        self.valid_bos = valid_bos

class DummyL5:
    def __init__(self, confirmed=False):
        self.confirmed = confirmed

# --- Test 1: OF_CANDIDATE semantics & Pre-IDM exclusion ---
def test_pre_idm_exclusion_smt():
    # IDM taken is False -> all pullbacks are SMTs.
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"))
    
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=False), None, None)
    assert result.order_flows[0].object_type == ExecutionObjectType.SMT_INDUCEMENT_TRAP

def test_idm_taken_exclusion_above_idm():
    # IDM is taken, IDM price is 15.0. Pullback top is 16.0 -> SMT!
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("15.5"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "15.1", "16", "15", "15.5"), c("c2", "15.6", "15.8", "15.5", "15.7")) # Top is 16
    
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=True, idm_price=Decimal("15.0")), None, None)
    assert result.order_flows[0].object_type == ExecutionObjectType.SMT_INDUCEMENT_TRAP

# --- Test 2: Mitigation logic ---
def test_of_mitigation_from_l2():
    # PB1 creates OF. PB2 interacts with it structurally (PB2 low <= PB1 top).
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("8.0")) # PB2 goes down to 8.0, interacting with PB1's top (11.0)
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"), # PB1 top 11, bottom 9
        c("c3", "11.1", "12", "11.1", "11.5"), c("c4", "10", "10.5", "8.0", "9")  # PB2 drops to 8.0
    )
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=True, idm_price=Decimal("15.0")), None, None)
    # PB1 should be mitigated! PB2 should be active.
    assert result.order_flows[0].state == ExecutionState.MITIGATED
    assert result.order_flows[1].state == ExecutionState.ACTIVE

# --- Test 3: Decisional OF causality ---
def test_decisional_of_causal():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("8.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
               c("c3", "11.1", "12", "11.1", "11.5"), c("c4", "11.2", "12", "11.1", "11.5"))
    
    # Valid BOS -> Decisional OF created
    res_valid = evaluate_execution_state(candles, l2_result, DummyL3(True, "15", "5"), DummyL4(structural_break=True, valid_bos=True), None)
    assert any(o.object_type == ExecutionObjectType.DECISIONAL_OF for o in res_valid.order_flows)
    
    # Structural break but NO VALID BOS -> No Decisional OF
    res_invalid = evaluate_execution_state(candles, l2_result, DummyL3(True, "15", "5"), DummyL4(structural_break=True, valid_bos=False), None)
    assert not any(o.object_type == ExecutionObjectType.DECISIONAL_OF for o in res_invalid.order_flows)

# --- Test 4: Extreme OF lineage ---
def test_extreme_of_lineage_selection():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("10.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"), # PB1 bottom 9.0
        c("c3", "11.1", "12", "11.1", "11.5"), c("c4", "11.2", "12", "11.1", "11.5") # PB2 bottom 10.0
    )
    result = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    # The extreme OF should be PB1 (lowest bottom)
    assert any(o.object_type == ExecutionObjectType.EXTREME_OF and o.bottom == Decimal("9.0") for o in result.order_flows)

# --- Test 5: Order Block Generation & Shifts ---
def test_ob_candidate_fvg_shift():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c4", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (
        c("c1", "10", "11", "10", "10.5"),
        c("c2", "10", "12", "9", "11"), # sweeps c1. No FVG because c4 overlaps. Wait, let's make c4 NOT overlap.
        c("c3", "11", "12", "10", "11.5"),
        c("c4", "12.5", "14", "12.5", "13") # FVG created from c2 high(12) to c4 low(12.5)
    )
    res = evaluate_execution_state(candles, l2_result, DummyL3(True), DummyL4(True, True), None)
    assert len(res.order_blocks) > 0
    # Ob was formed by c2!
    ob = res.order_blocks[0]
    assert ob.source_candle_ids == ("c2",)

def test_ob_fvg_consumed():
    # If a later candle consumes the FVG, it's invalid.
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c5", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (
        c("c1", "10", "11", "10", "10.5"),
        c("c2", "10", "12", "9", "11"), # sweep
        c("c3", "11", "12", "10", "11.5"),
        c("c4", "12.5", "14", "12.5", "13"), # FVG (12 to 12.5)
        c("c5", "10", "11", "10", "10.5") # This candle drops to 10, completely consuming the FVG!
    )
    res = evaluate_execution_state(candles, l2_result, DummyL3(True), DummyL4(True, True), None)
    assert len(res.order_blocks) == 0 # OB invalidated!

# --- Test 6: Engineering Liquidity Dependency ---
def test_eng_lqd_requires_pullback():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"))
    
    result = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    assert result.engineering_liquidity is not None
    assert result.engineering_liquidity.bottom == Decimal("9.0")

def test_no_pullback_no_eng_lqd():
    result = evaluate_execution_state((), None, None, None, None)
    assert result.engineering_liquidity is None

# --- Test 7: Rule of Two Premium/Discount ---
def test_buy_discount_decisional_poi():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("8.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
               c("c3", "11.1", "12", "11.1", "11.5"), c("c4", "11.2", "12", "11.1", "11.5"))
    
    # Range: 0 to 10 (Discount is < 5). PB1 top is 11! Not in discount!
    res_no_dec = evaluate_execution_state(candles, l2_result, DummyL3(True, "10", "0"), DummyL4(True, True), None)
    assert res_no_dec.active_pois.decisional_poi is None # Rejected!
    
    # Range: 0 to 25 (Discount is < 12.5). PB1 top is 11! In discount!
    res_dec = evaluate_execution_state(candles, l2_result, DummyL3(True, "25", "0"), DummyL4(True, True), None)
    assert res_dec.active_pois.decisional_poi is not None

# --- Test 8: Expiry & Failure Provenance ---
def test_bos_expires_pois():
    poi1 = ExecutionObject(ExecutionObjectType.DECISIONAL_POI, PullbackDirection.BULLISH, Decimal("1"), Decimal("0"), ("c",), ExecutionState.ACTIVE, range_id="1")
    
    # Current range is "2", BOS is True -> POI from range "1" expires!
    expired = expire_pois([poi1], DummyL4(structural_break=True, valid_bos=True), current_range_id="2")
    assert expired[0].state == ExecutionState.EXPIRED_HISTORICAL
    
    # Current range is "1", BOS is True -> POI from range "1" does NOT expire (it's new!)
    not_expired = expire_pois([poi1], DummyL4(structural_break=True, valid_bos=True), current_range_id="1")
    assert not_expired[0].state == ExecutionState.ACTIVE

def test_poi_failure_requires_choch():
    poi1 = ExecutionObject(ExecutionObjectType.DECISIONAL_POI, PullbackDirection.BULLISH, Decimal("1"), Decimal("0"), ("c",), ExecutionState.ACTIVE)
    
    # CHoCH Confirmed
    failed = fail_pois([poi1], DummyL5(confirmed=True))
    assert failed[0].state == ExecutionState.FAILED
    
    # CHoCH Not Confirmed
    not_failed = fail_pois([poi1], DummyL5(confirmed=False))
    assert not_failed[0].state == ExecutionState.ACTIVE
