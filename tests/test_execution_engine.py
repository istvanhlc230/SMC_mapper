import pytest
from decimal import Decimal
from execution_engine import (
    ExecutionObject, ExecutionObjectType, ExecutionState,
    POISet, OBPillars, _is_discount, _is_premium, check_rule_of_two_discount_premium,
    refine_ob_wick, refine_ob_inside_bar, validate_ob_pillars,
    expire_pois, fail_pois, evaluate_execution_state, ExecutionAnalysis,
    check_fvg, check_sweep
)
from minor_structure_engine import PullbackDirection
from microstructure_engine import Candle
import sys

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

# --- Test 1: OF_CANDIDATE semantics & Pre-IDM exclusion ---
def test_pre_idm_exclusion_smt():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"))
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=False), None, None)
    assert result.order_flows[0].object_type == ExecutionObjectType.SMT_INDUCEMENT_TRAP

# --- Test 2: Mitigation logic ---
def test_of_mitigation_from_l2():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("8.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"), # PB1 top 11, bottom 9
        c("c3", "11.1", "12", "11.1", "11.5"), c("c4", "10", "10.5", "8.0", "9")  # PB2 drops to 8.0, mitigating PB1
    )
    result = evaluate_execution_state(candles, l2_result, DummyL3(idm_taken=True, idm_price=Decimal("15.0")), None, None)
    assert result.order_flows[0].state == ExecutionState.MITIGATED

# --- Test 3: Decisional OF causality ---
def test_decisional_of_causal_break_id():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("10.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
        c("c3", "11.1", "12", "11.1", "11.5"), c("c4", "11.2", "12", "11.1", "11.5"), # PB2
        c("c5", "12", "13", "11.5", "12.5"), c("c6", "13", "15", "12.5", "14") # c6 is break_candle_id
    )
    l4_result = DummyL4(structural_break=True, valid_bos=True, break_c_id="c6")
    res_valid = evaluate_execution_state(candles, l2_result, DummyL3(True, "15", "5"), l4_result, None)
    dec_of = next((o for o in res_valid.order_flows if o.object_type == ExecutionObjectType.DECISIONAL_OF), None)
    assert dec_of is not None
    assert dec_of.origin_pullback_id == "c3" # PB2 is closest to break_candle c6

# --- Test 4: Extreme OF lineage ---
def test_extreme_of_shifts_when_mitigated():
    # If PB1 is mitigated, Extreme OF should naturally shift to PB2!
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("8.0")) # mitigates PB1
    pb3 = DummyPullback(PullbackDirection.BULLISH, "c5", "c5", "c6", Decimal("10.0")) # does not mitigate PB2
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2, pb3]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
        c("c3", "10", "10.5", "9", "9.5"), c("c4", "9", "10", "8.0", "8.5"), # mitigates pb1 but pb2 top is 10.5
        c("c5", "11.1", "12", "11.1", "11.5"), c("c6", "11.2", "12", "11.1", "11.5")
    )
    res = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    ext_of = next((o for o in res.order_flows if o.object_type == ExecutionObjectType.EXTREME_OF), None)
    assert ext_of is not None
    assert ext_of.origin_pullback_id == "c3" # PB2 becomes Extreme OF

# --- Test 5: Order Block Generation & Shifts ---
def test_ob_candidate_fvg_shift_and_consumption():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c6", Decimal("9.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1]})()
    candles = (
        c("c1", "10", "11", "10", "10.5"),
        c("c2", "10", "12", "9", "11"), # sweep, but FVG formed at c4 is immediately consumed by c5
        c("c3", "11", "12", "10", "11.5"),
        c("c4", "12.5", "14", "12.5", "13"), # FVG (12 to 12.5)
        c("c5", "10", "11", "10", "10.5"), # Consumes FVG completely!
        c("c6", "10", "12", "8.5", "11"), # Next sweep! 
        c("c7", "11", "12", "10", "11.5"),
        c("c8", "12.5", "14", "12.5", "13") # Valid FVG (12 to 12.5) for c6!
    )
    res = evaluate_execution_state(candles, l2_result, DummyL3(True), DummyL4(True, True), None)
    assert len(res.order_blocks) > 0
    ob = res.order_blocks[0]
    assert ob.source_candle_ids == ("c6",) # It skipped c2 and correctly selected c6!

# --- Test 6: Engineering Liquidity Dependency ---
def test_eng_lqd_requires_pullback():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("10.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"),
        c("c3", "11.1", "12", "11.1", "11.5"), c("c4", "11.2", "12", "11.1", "11.5")
    )
    
    result = evaluate_execution_state(candles, l2_result, DummyL3(True), None, None)
    # The Extreme POI is pb1. There is NO pullback before pb1!
    assert result.engineering_liquidity is None

def test_eng_lqd_valid_pullback_preceding():
    pb1 = DummyPullback(PullbackDirection.BULLISH, "c1", "c1", "c2", Decimal("9.0"))
    pb2 = DummyPullback(PullbackDirection.BULLISH, "c3", "c3", "c4", Decimal("10.0")) # Extreme OF (since PB1 is SMT because of IDM not taken yet? No, if IDM is taken, both are OFs)
    pb3 = DummyPullback(PullbackDirection.BULLISH, "c5", "c5", "c6", Decimal("11.0"))
    l2_result = type("L2Result", (), {"pullbacks": [pb1, pb2, pb3]})()
    candles = (
        c("c1", "10", "11", "9.5", "10"), c("c2", "10", "10.5", "9.0", "9"), # pb1 is mitigated by pb2
        c("c3", "10", "10.5", "9", "9.5"), c("c4", "9", "10", "8.0", "8.5"), # mitigates pb1 but pb2 top is 10.5 pb1. So pb2 is extreme!
        c("c5", "11.1", "12", "11.1", "11.5"), c("c6", "11.2", "12", "11.1", "11.5")
    )
    result = evaluate_execution_state(candles, l2_result, DummyL3(True, "15.0", "0"), None, None)
    # The Extreme POI is PB2. The preceding pullback is PB1!
    # So Engineering Liquidity should reference PB1's extreme (9.0).
    assert result.engineering_liquidity is not None
    assert result.engineering_liquidity.bottom == Decimal("9.0")
    assert result.engineering_liquidity.source_candle_ids == ("c2",)

# --- Test 7: Expiry & Failure Provenance ---
def test_bos_expires_pois():
    poi1 = ExecutionObject(ExecutionObjectType.DECISIONAL_POI, PullbackDirection.BULLISH, Decimal("1"), Decimal("0"), ("c",), ExecutionState.ACTIVE, range_id="sc_0")
    
    # Current range is sc_1 -> expires!
    expired = expire_pois([poi1], DummyL4(structural_break=True, valid_bos=True), current_range_id="sc_1")
    assert expired[0].state == ExecutionState.EXPIRED_HISTORICAL
    
    # Current range is sc_0 -> DOES NOT EXPIRE
    not_expired = expire_pois([poi1], DummyL4(structural_break=True, valid_bos=True), current_range_id="sc_0")
    assert not_expired[0].state == ExecutionState.ACTIVE

def test_poi_failure_requires_choch():
    poi1 = ExecutionObject(ExecutionObjectType.DECISIONAL_POI, PullbackDirection.BULLISH, Decimal("1"), Decimal("0"), ("c",), ExecutionState.ACTIVE)
    
    # CHoCH Confirmed
    failed = fail_pois([poi1], DummyL5(confirmed=True))
    assert failed[0].state == ExecutionState.FAILED
    
    # CHoCH Eligible (Not Confirmed)
    not_failed = fail_pois([poi1], DummyL5(confirmed=False))
    assert not_failed[0].state == ExecutionState.ACTIVE
