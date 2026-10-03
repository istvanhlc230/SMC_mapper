import pytest
from decimal import Decimal
from minor_structure_engine import PullbackDirection, CandleLevelValidPullback, VerifiedPullbackExtreme, PullbackDerivedLiquidityReference, LiquiditySide
from microstructure_engine import Candle
from execution_engine import evaluate_execution_state, ExecutionObjectType, ExecutionState

def c(id_: str, open_: str, high_: str, low_: str, close_: str) -> Candle:
    return Candle(id_, Decimal(open_), Decimal(high_), Decimal(low_), Decimal(close_))

def make_pb(ref, start, comp, ext_c, ext_p, dir_=PullbackDirection.BULLISH):
    return CandleLevelValidPullback(
        direction=dir_,
        reference_candle_id=ref,
        start_candle_id=start,
        completion_candle_id=comp,
        extreme=VerifiedPullbackExtreme(price=Decimal(ext_p), source_candle_id=ext_c, direction=dir_),
        liquidity_reference=PullbackDerivedLiquidityReference(side=LiquiditySide.SELL_SIDE if dir_ == PullbackDirection.BULLISH else LiquiditySide.BUY_SIDE, price=Decimal(ext_p), source_candle_id=ext_c)
    )

class MockIDM:
    def __init__(self, takeout_id):
        self.takeout_candle_id = takeout_id
        self.reference_price = Decimal("15.0")
        self.source_candle_id = "c_idm"

class MockRange:
    def __init__(self):
        self.range_id = "range_1"

class MockL3:
    def __init__(self, idm_takeout):
        self.active_idm = MockIDM(idm_takeout) if idm_takeout else None
        self.active_dealing_range = MockRange()
        self.confirmed_swings = []

class MockL4:
    def __init__(self, valid_bos, break_id):
        self.valid_bos = valid_bos
        self.structural_break = type("Brk", (), {"break_candle_id": break_id})() if break_id else None

class MockL5:
    def __init__(self):
        self.resolution = type("Res", (), {"name": "CHOCH_ELIGIBLE"})()

class MockL2:
    def __init__(self, pbs):
        self.pullbacks = pbs

def test_integration_full_of_lifecycle():
    # Sequence: 
    # c1-c2 (PB1 - before IDM) -> SMT
    # c3 = IDM takeout candle
    # c4-c5 (PB2 - after IDM) -> ELIGIBLE_ORDER_FLOW, becomes DECISIONAL_ORDER_FLOW because it causes BOS at c6
    # c7 = BOS candle
    
    pb1 = make_pb("c1", "c1", "c2", "c2", "10.0")
    pb2 = make_pb("c4", "c4", "c5", "c5", "12.0")
    
    candles = (
        c("c1", "10", "11", "9.5", "10"),
        c("c2", "10", "12", "9", "11"), # PB1 completes
        c("c3", "12", "13", "11", "12.5"), # IDM takeout
        c("c4", "12.5", "14", "12", "13.5"),
        c("c5", "13.5", "15", "11.5", "14"), # PB2 completes
        c("c6", "14", "16", "13", "15"),
        c("c7", "15", "18", "14", "17") # BOS Break candle
    )
    
    l2 = MockL2([pb1, pb2])
    l3 = MockL3("c3") # IDM taken at c3
    l4 = MockL4(True, "c7") # BOS break at c7
    l5 = MockL5()
    
    res = evaluate_execution_state(candles, l2, l3, l4, l5)
    
    # 2 OFs total.
    assert len(res.order_flows) == 2
    
    smt = [of for of in res.order_flows if of.object_type == ExecutionObjectType.SMT_INDUCEMENT_TRAP]
    assert len(smt) == 1
    assert smt[0].origin_pullback_id == "c1" # PB1 completed before c3
    
    dec_of = [of for of in res.order_flows if of.object_type == ExecutionObjectType.DECISIONAL_ORDER_FLOW]
    assert len(dec_of) == 1
    assert dec_of[0].origin_pullback_id == "c4" # PB2 caused BOS at c7

def test_integration_ext_of_none():
    # Test line 341 crash: when ext_of_obj is None (all OFs mitigated)
    pb1 = make_pb("c1", "c1", "c2", "c2", "10.0")
    pb2 = make_pb("c4", "c4", "c5", "c5", "9.0") # pb2 drops below pb1, mitigating it
    
    candles = (
        c("c1", "10", "11", "9.5", "10"),
        c("c2", "10", "12", "9", "11"), # PB1
        c("c3", "12", "13", "11", "12.5"), # IDM takeout
        c("c4", "12.5", "14", "12", "13.5"),
        c("c5", "13.5", "15", "8.5", "14"), # PB2 drops to 8.5, mitigating PB1 (bottom=9.0)
    )
    l2 = MockL2([pb1, pb2])
    l3 = MockL3("c3")
    l4 = MockL4(False, None)
    l5 = MockL5()
    
    res = evaluate_execution_state(candles, l2, l3, l4, l5)
    assert res is not None
