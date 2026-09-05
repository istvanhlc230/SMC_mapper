"""
True SMC mapper — Institutional Structure Engine
State-Lifecycle Audited & Fixed Engine
Data layer decoupled via data_provider.py.
"""
import os
import json
import time
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

from data_provider import (
    ProviderConfig, DataRequest, fetch_candles, auto_detect_provider,
)

# ============================================================
# CONSTANTS  (engine-only — immutable)
# ============================================================

# ============================================================
# MAPPER SETTINGS — loaded once from config.json at startup
# ============================================================

def _load_settings() -> dict:
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    try:
        with open(cfg_path, "r", encoding="utf-8") as _f:
            _cfg = json.load(_f)
            return _cfg["mapper"]
    except FileNotFoundError:
        raise FileNotFoundError(
            "config.json not found. Create it from .env.example or see the README."
        )
    except KeyError:
        raise KeyError("config.json is missing the required 'mapper' section.")
    except Exception as _e:
        raise RuntimeError(f"Could not load config.json: {_e}")

_SETTINGS = _load_settings()
TICKERS: List[str]           = _SETTINGS["tickers"]
INTERVAL: str                = _SETTINGS["interval"]
BAR_COUNT: int               = _SETTINGS.get("bar_count", 1000)
HISTORY_SIZE: int            = _SETTINGS.get("structure_history_size", 20)
EQUAL_LEVEL_TOLERANCE: float = _SETTINGS["equal_level_tolerance"]
DEBUG: bool                  = _SETTINGS["debug"]
BOS_MIN_RETRACEMENT_PCT: float = _SETTINGS.get("bos_min_retracement_pct", 0.382)

# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class StructuralLevel:
    kind: str        # "HIGH" or "LOW"
    price: float
    index: int
    time: str
    close: float
    open: float = 0.0


@dataclass
class IDMState:
    kind: str        # "LOW" (bull IDM) or "HIGH" (bear IDM)
    price: float
    index: int
    time: str
    major: bool = False
    fallback: bool = False
    active: bool = True
    swept: bool = False
    liquidity: bool = False
    sweep_index: int = -1
    sweep_time: str = ""
    leg_id: int = 0


@dataclass
class PullbackState:
    direction: str           # trend direction when pullback started
    reference_index: int
    reference_high: float
    reference_low: float
    extreme: float
    extreme_index: int
    active: bool = True
    confirmed: bool = False
    retracement: float = 0.0
    reached_threshold: bool = False


@dataclass
class RangeState:
    direction: str
    high: float
    low: float
    high_index: int
    low_index: int
    high_source: str = "INITIAL_BOUNDARY"
    low_source: str = "INITIAL_BOUNDARY"


@dataclass
class LiquidityLevel:
    price: float
    index: int
    time: str
    source: str      # "MAJOR_IDM", "MINOR_IDM", "STRUCTURAL"
    side: str        # "BUY_SIDE" or "SELL_SIDE"
    taken: bool = False
    sweep_index: int = -1
    sweep_time: str = ""


@dataclass
class StructureRecord:
    event: str               # "BOS" or "CHoCH"
    direction: str           # "BULLISH" or "BEARISH"
    time: str
    index: int
    break_price: float
    breaker_reference: float
    weak_price: Optional[float]
    protected_price: Optional[float]
    retracement: float
    minor_idm_price: Optional[float]
    major_idm_price: Optional[float]
    major_idm_status: str = "NONE"
    idm_swept: bool = False
    idm_swept_price: Optional[float] = None
    idm_swept_type: str = ""
    context: str = ""


@dataclass
class EngineState:
    trend: str = "UNCONFIRMED"
    implied_trend: str = "UNCONFIRMED"
    bias_source: str = "NONE"

    protected_high: Optional[StructuralLevel] = None
    protected_low: Optional[StructuralLevel] = None

    weak_high: Optional[StructuralLevel] = None
    weak_low: Optional[StructuralLevel] = None

    candidate_high: float = 0.0
    candidate_high_index: int = -1
    candidate_low: float = float('inf')
    candidate_low_index: int = -1

    dealing_range: Optional[RangeState] = None

    reference_index: Optional[int] = None
    reference_high: Optional[float] = None
    reference_low: Optional[float] = None

    pullback: Optional[PullbackState] = None

    minor_idm: Optional[IDMState] = None
    major_idm: Optional[IDMState] = None

    mother_bar_index: int = -1
    eqh_history: List[dict] = field(default_factory=list)
    eql_history: List[dict] = field(default_factory=list)

    # Track preceding IDM provenance
    last_swept_idm_price: Optional[float] = None
    last_swept_idm_time: str = ""
    last_swept_idm_type: str = ""
    
    current_leg_id: int = 1
    last_valid_idm_sweep_leg_id: int = -1

    liquidity: List[LiquidityLevel] = field(default_factory=list)

    bos: Optional[dict] = None
    choch: Optional[dict] = None

    range_has_bos: bool = False
    last_pullback_depth: float = 0.0

    structure_history: List[StructureRecord] = field(default_factory=list)

    debug_log: List[str] = field(default_factory=list)


# ============================================================
# MAPPER RESULT
# ============================================================

@dataclass
class MAPPERResult:
    symbol: str
    timeframe: str
    current_price: float
    structural_bias: str
    bias_source: str
    structure_state: str
    protected_high: Optional[float]
    protected_low: Optional[float]
    major_idm: Optional[float]
    major_idm_status: str        # "FALLBACK", "REAL", "SWEPT", "NONE"
    minor_idm: Optional[float]
    minor_idm_status: str        # "ACTIVE", "SWEPT", "NONE"
    dealing_range_high: Optional[float]
    dealing_range_low: Optional[float]
    dealing_range_eq: Optional[float]
    dealing_range_high_source: Optional[str]
    dealing_range_low_source: Optional[str]
    market_location: str         # "PREMIUM", "DISCOUNT", "EQUILIBRIUM"
    retracement_pct: float
    fib_382: bool
    info_fibs: dict
    candidate_high: Optional[float]
    candidate_low: Optional[float]
    active_pullback_extreme: Optional[float]
    liquidity_objective: str
    liquidity_objective_price: Optional[float]
    setup_state: str
    structure_quality: int       # 0-100
    setup_quality: int
    location_quality: Optional[int]  # None = unavailable (no confirmed structure)
    liquidity_quality: int
    risk_quality: Optional[int]      # None = unavailable (no confirmed structure)
    final_score: int
    quality_tier: str = "WATCH"
    explanation: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error: str = ""


# ============================================================
# SWING DETECTION
# ============================================================

def make_level(c: dict, i: int, kind: str) -> StructuralLevel:
    return StructuralLevel(
        kind=kind,
        price=c["high"] if kind == "HIGH" else c["low"],
        index=i, time=c["time"], close=c["close"], open=c.get("open", 0.0)
    )

def get_swings(candles: List[dict]) -> Tuple[List[StructuralLevel], List[StructuralLevel]]:
    """F-03: Use strict > on the right neighbour to prevent duplicate pivots on flat bars.
    Convention: pivot high requires strictly lower right neighbour.
                pivot low  requires strictly higher right neighbour.
    This ensures only the first bar of a flat run is tagged as the pivot.
    """
    highs, lows = [], []
    for i in range(1, len(candles) - 1):
        if candles[i]["high"] >= candles[i-1]["high"] and candles[i]["high"] > candles[i+1]["high"]:
            highs.append(make_level(candles[i], i, "HIGH"))
        if candles[i]["low"] <= candles[i-1]["low"] and candles[i]["low"] < candles[i+1]["low"]:
            lows.append(make_level(candles[i], i, "LOW"))
    return highs, lows


# ============================================================
# HELPERS
# ============================================================

def breaker_reference(c: dict, direction: str) -> float:
    bullish = c["close"] >= c["open"]
    if direction == "BULLISH":
        return c["close"] if bullish else c["open"]
    return c["close"] if not bullish else c["open"]

def prices_equal(a: float, b: float) -> bool:
    if b == 0:
        return abs(a) < 1e-10
    return abs(a - b) / max(abs(a), abs(b)) < EQUAL_LEVEL_TOLERANCE

def bull_retracement(high: float, low: float, extreme: float) -> float:
    span = high - low
    return (high - extreme) / span if span > 0 else 0.0

def bear_retracement(high: float, low: float, extreme: float) -> float:
    span = high - low
    return (extreme - low) / span if span > 0 else 0.0

def update_pullback_depth(pb: PullbackState, state: EngineState) -> None:
    """F-07: Report raw retracement without clamping. Out-of-range pullbacks (>100%)
    are structurally meaningful and should be visible to the scorer, not silently capped.
    """
    if not state.dealing_range:
        return
    dr = state.dealing_range
    if pb.direction == "BULLISH":
        high = max(dr.high, state.candidate_high) if state.candidate_high > 0 else dr.high
        low = state.protected_low.price if state.protected_low else dr.low
        pb.retracement = bull_retracement(high, low, pb.extreme)
    else:
        high = state.protected_high.price if state.protected_high else dr.high
        low = min(dr.low, state.candidate_low) if state.candidate_low < float('inf') else dr.low
        pb.retracement = bear_retracement(high, low, pb.extreme)
    pb.reached_threshold = pb.retracement >= (BOS_MIN_RETRACEMENT_PCT / 100.0)

def dbg(state: EngineState, i: int, msg: str, time: str = "") -> None:
    if DEBUG:
        t_str = f" [{time}]" if time else ""
        state.debug_log.append(f"  BAR {i}{t_str}: {msg}")


# ============================================================
# IDM / LIQUIDITY LIFECYCLE
# ============================================================

def retire_to_liquidity(state: EngineState, idm: Optional[IDMState]) -> None:
    """F-05: Retire an unswept IDM to the liquidity pool.
    Guard against duplicate entries at the same price within EQUAL_LEVEL_TOLERANCE.
    """
    if idm is None or idm.swept or idm.liquidity:
        return
    # Dedup: skip if a pool entry already exists at this price on the same side
    side = "SELL_SIDE" if idm.kind == "LOW" else "BUY_SIDE"
    for existing in state.liquidity:
        if existing.side == side and prices_equal(existing.price, idm.price):
            idm.active = False
            idm.liquidity = True
            return  # same level already pooled
    idm.active = False
    idm.liquidity = True
    state.liquidity.append(LiquidityLevel(
        price=idm.price, index=idm.index, time=idm.time,
        source="MAJOR_IDM" if idm.major else "MINOR_IDM", side=side,
    ))

def replace_minor_idm(state: EngineState, price: float, index: int, candles: List[dict], current_i: Optional[int] = None) -> None:
    old = state.minor_idm
    if old and old.active and not old.swept:
        retire_to_liquidity(state, old)
    active_dir = state.trend
    if active_dir == "UNCONFIRMED":
        if state.pullback and state.pullback.direction:
            active_dir = state.pullback.direction
        elif state.implied_trend != "UNCONFIRMED":
            active_dir = state.implied_trend
        else:
            active_dir = "BULLISH"
    state.minor_idm = IDMState(
        kind="LOW" if active_dir == "BULLISH" else "HIGH",
        price=price, index=index, time=candles[index]["time"],
        leg_id=state.current_leg_id
    )
    log_i = current_i if current_i is not None else index
    origin_str = f" (origin: BAR {index} [{candles[index]['time']}])" if log_i != index else ""
    dbg(state, log_i, f"Minor IDM created @ {price:.2f}{origin_str}", candles[log_i]["time"])

def replace_major_idm(state: EngineState, price: float, index: int,
                       candles: List[dict], fallback: bool = False, current_i: Optional[int] = None) -> None:
    old = state.major_idm
    if old and old.active and not old.swept and not old.fallback:
        retire_to_liquidity(state, old)
    active_dir = state.trend if state.trend in ["BULLISH", "BEARISH"] else state.dealing_range.direction if state.dealing_range else "UNKNOWN"
    idm_swept_before_bar = state.last_valid_idm_sweep_leg_id == state.current_leg_id
    if active_dir == "UNKNOWN" and state.pullback:
        active_dir = state.pullback.direction
    state.major_idm = IDMState(
        kind="LOW" if active_dir == "BULLISH" else "HIGH",
        price=price, index=index, time=candles[index]["time"],
        major=True, fallback=fallback, leg_id=state.current_leg_id
    )
    log_i = current_i if current_i is not None else index
    origin_str = f" (origin: BAR {index} [{candles[index]['time']}])" if log_i != index else ""
    dbg(state, log_i, f"Major IDM {'(fallback) ' if fallback else '(real) '}created @ {price:.2f}{origin_str}", candles[log_i]["time"])

def sweep_idms(state: EngineState, c: dict, i: int) -> None:
    # Check Minor IDM sweep
    if state.minor_idm and state.minor_idm.active and not state.minor_idm.swept:
        swept = False
        if state.minor_idm.kind == "LOW" and c["low"] < state.minor_idm.price:
            swept = True
        elif state.minor_idm.kind == "HIGH" and c["high"] > state.minor_idm.price:
            swept = True

        if swept:
            state.minor_idm.swept = True
            state.minor_idm.active = False
            state.minor_idm.sweep_index = i
            state.minor_idm.sweep_time = c["time"]
            state.last_swept_idm_price = state.minor_idm.price
            state.last_swept_idm_time = c["time"]
            state.last_swept_idm_type = "MINOR"
            state.last_valid_idm_sweep_leg_id = state.minor_idm.leg_id
            dbg(state, i, f"Minor IDM SWEPT @ {state.minor_idm.price:.2f}", c["time"])

    # Check Major IDM sweep
    if state.major_idm and state.major_idm.active and not state.major_idm.swept:
        swept = False
        if state.major_idm.kind == "LOW" and c["low"] < state.major_idm.price:
            swept = True
        elif state.major_idm.kind == "HIGH" and c["high"] > state.major_idm.price:
            swept = True

        if swept:
            state.major_idm.swept = True
            state.major_idm.active = False
            state.major_idm.sweep_index = i
            state.major_idm.sweep_time = c["time"]
            state.last_swept_idm_price = state.major_idm.price
            state.last_swept_idm_time = c["time"]
            state.last_swept_idm_type = "MAJOR_FALLBACK" if state.major_idm.fallback else "MAJOR"
            state.last_valid_idm_sweep_leg_id = state.major_idm.leg_id
            dbg(state, i, f"Major IDM {'(fallback)' if state.major_idm.fallback else ''} SWEPT @ {state.major_idm.price:.2f}", c["time"])

    # Check retired liquidity pool
    for liq in state.liquidity:
        if not liq.taken:
            hit = False
            if liq.side == "SELL_SIDE" and c["low"] <= liq.price:
                hit = True
            elif liq.side == "BUY_SIDE" and c["high"] >= liq.price:
                hit = True
            if hit:
                liq.taken = True
                liq.sweep_index = i
                liq.sweep_time = c["time"]


def has_taken_idm(state: EngineState) -> bool:
    """Verifies that an IDM originating from the current structural leg was taken."""
    # Strict Provenance match: the latest swept IDM must belong to the active leg.
    return state.last_valid_idm_sweep_leg_id == state.current_leg_id


# ============================================================
# STRUCTURE HISTORY
# ============================================================

def record_structure(state: EngineState, event: str, direction: str,
                     c: dict, index: int, weak: StructuralLevel,
                     breaker_ref: float, retracement: float, context: str = "") -> None:
    protected = state.protected_low if direction == "BULLISH" else state.protected_high
    maj_status = ("FALLBACK" if state.major_idm and state.major_idm.fallback
                  else "REAL" if state.major_idm and state.major_idm.active
                  else "SWEPT" if state.major_idm and state.major_idm.swept
                  else "NONE")
    rec = StructureRecord(
        event=event, direction=direction, time=c["time"], index=index,
        break_price=c["high"] if direction == "BULLISH" else c["low"],
        breaker_reference=breaker_ref, weak_price=weak.price if weak else None,
        protected_price=protected.price if protected else None,
        retracement=retracement,
        minor_idm_price=state.minor_idm.price if state.minor_idm else None,
        major_idm_price=state.major_idm.price if state.major_idm else None,
        major_idm_status=maj_status,
        idm_swept=has_taken_idm(state),
        idm_swept_price=state.last_swept_idm_price,
        idm_swept_type=state.last_swept_idm_type,
        context=context,
    )
    state.structure_history.insert(0, rec)
    del state.structure_history[HISTORY_SIZE:]


# ============================================================
# BOS / CHoCH QUALIFICATION
# ============================================================

def bullish_break_qualified(state: EngineState, c: dict,
                            weak: StructuralLevel, depth: float) -> bool:
    if c["high"] <= weak.price:
        return False
    if prices_equal(c["high"], weak.price):
        return False  # Touch/wick equal high is only a retest/violation, not a break
    ref = breaker_reference(c, "BULLISH")
    body_ok = ref > weak.close
    idm_ok = has_taken_idm(state)
    return body_ok and idm_ok and depth >= (BOS_MIN_RETRACEMENT_PCT / 100.0)

def bearish_break_qualified(state: EngineState, c: dict,
                            weak: StructuralLevel, depth: float) -> bool:
    if c["low"] >= weak.price:
        return False
    if prices_equal(c["low"], weak.price):
        return False
    ref = breaker_reference(c, "BEARISH")
    body_ok = ref < weak.close
    idm_ok = has_taken_idm(state)
    return body_ok and idm_ok and depth >= (BOS_MIN_RETRACEMENT_PCT / 100.0)

def choch_qualified(state: EngineState, c: dict, direction: str, candles: List[dict] = None) -> bool:
    """PDF CHoCH rule: body breaker reference past protected swing close. (IDM decoupled for structural reversal)"""
    if state.trend == "UNCONFIRMED":
        return False
    if direction == "BULLISH":
        level_price = state.protected_high.price if state.protected_high else (state.dealing_range.high if state.dealing_range else None)
        if level_price is None or c["high"] <= level_price:
            return False
        level_close = state.protected_high.close if state.protected_high else (candles[state.dealing_range.high_index]["close"] if state.dealing_range and candles else level_price)
        return breaker_reference(c, "BULLISH") > level_close
    if direction == "BEARISH":
        level_price = state.protected_low.price if state.protected_low else (state.dealing_range.low if state.dealing_range else None)
        if level_price is None or c["low"] >= level_price:
            return False
        level_close = state.protected_low.close if state.protected_low else (candles[state.dealing_range.low_index]["close"] if state.dealing_range and candles else level_price)
        return breaker_reference(c, "BEARISH") < level_close
    return False


# ============================================================
# INITIALIZATION
# ============================================================

def initialize(candles: List[dict], highs: List[StructuralLevel],
               lows: List[StructuralLevel]):
    # F-02: Only one pivot in each direction is required to determine initial trend context.
    # We bootstrap the state machine from the EARLIEST pivots (highs[0], lows[0]) in the dataset.
    if DEBUG:
        print(f"  INIT: highs={len(highs)} lows={len(lows)}")
    if len(highs) < 1 or len(lows) < 1:
        if DEBUG:
            print(f"  INIT FAILED: reason=insufficient pivots (highs={len(highs)}, lows={len(lows)})")
        return None
    state = EngineState()
    first_high = highs[0]
    first_low = lows[0]
    if DEBUG:
        print(f"  INIT: first_high={first_high.price}@{first_high.index} first_low={first_low.price}@{first_low.index}")

    if first_high.index > first_low.index:
        state.trend = "UNCONFIRMED"
        state.bias_source = "INITIAL/UNCONFIRMED"
        state.weak_high = first_high
        state.weak_low = first_low
        state.candidate_high = first_high.price
        state.candidate_high_index = first_high.index
        state.candidate_high_source = "INITIAL_BOUNDARY"
        state.dealing_range = RangeState("BULLISH", first_high.price, first_low.price,
                                          first_high.index, first_low.index)
        state.reference_index = first_high.index
        state.implied_trend = "BULLISH"
        state.mother_bar_index = first_high.index
    else:
        state.trend = "UNCONFIRMED"
        state.bias_source = "INITIAL/UNCONFIRMED"
        state.weak_high = first_high
        state.weak_low = first_low
        state.candidate_low = first_low.price
        state.candidate_low_index = first_low.index
        state.candidate_low_source = "INITIAL_BOUNDARY"
        state.dealing_range = RangeState("BEARISH", first_high.price, first_low.price,
                                          first_high.index, first_low.index)
        state.reference_index = first_low.index
        state.implied_trend = "BEARISH"
        state.mother_bar_index = first_low.index

    state.reference_high = candles[state.reference_index]["high"]
    state.reference_low = candles[state.reference_index]["low"]
    bars_remaining = len(candles) - state.reference_index - 1
    if DEBUG:
        print(f"  INIT SUCCESS: trend={state.trend} reference_index={state.reference_index} bars_remaining={bars_remaining}")
    return state


# ============================================================
# PULLBACK COMPLETION
# ============================================================

def is_structurally_valid_pullback(pb: PullbackState, state: EngineState, candles: List[dict], current_i: Optional[int] = None, large_momentum: bool = False) -> bool:
    """Canonical structural pullback qualification.

    Standard path:
      >= 3 structurally opposing candles + >= configured retracement depth.

    Exact 2-candle exception:
      exactly 2 structurally opposing candles + structural large-move evidence
      + (>= 5 prior candle extremes swept/engulfed OR >= configured retracement depth).

    Candle colour is never used as the definition of opposing movement.
    The mother/reference candle is excluded. When called from finish_pullback,
    the continuation/break candle is also excluded from the pullback leg.
    """
    if pb.reference_index < 0 or pb.reference_index >= len(candles):
        return False

    # During normal engine completion, current_i is the continuation candle.
    # The pullback leg therefore ends immediately before current_i. For direct
    # unit calls without current_i, include the recorded extreme itself.
    if current_i is None:
        end_exclusive = min(len(candles), pb.extreme_index + 1)
    else:
        end_exclusive = min(len(candles), current_i + 1)

    start_idx = pb.reference_index + 1
    if end_exclusive <= start_idx:
        return False

    opposing_count = 0
    prev = candles[pb.reference_index]
    pullback_indices: list[int] = []

    for idx in range(start_idx, end_exclusive):
        c = candles[idx]
        if pb.direction == "BULLISH":
            # Opposing structural movement is movement lower: lower high OR lower low.
            opposing = c["high"] < prev["high"] or c["low"] < prev["low"]
        else:
            # Opposing structural movement is movement higher: higher high OR higher low.
            opposing = c["high"] > prev["high"] or c["low"] > prev["low"]
        if opposing:
            opposing_count += 1
            pullback_indices.append(idx)
        prev = c

    threshold = (BOS_MIN_RETRACEMENT_PCT / 100.0) if BOS_MIN_RETRACEMENT_PCT > 1 else BOS_MIN_RETRACEMENT_PCT
    depth_ok = pb.retracement >= threshold

    # Count all prior candle extremes engulfed by the pullback extreme. Do not
    # stop at the first non-swept candle: liquidity may exist behind intervening bars.
    swept = 0
    lookback_start = max(0, pb.reference_index - 20)
    for idx in range(lookback_start, pb.reference_index):
        c = candles[idx]
        if pb.direction == "BULLISH" and pb.extreme < c["low"]:
            swept += 1
        elif pb.direction == "BEARISH" and pb.extreme > c["high"]:
            swept += 1

    # The canonical rule provides no ATR/body-ratio formula for "large/high
    # momentum". Therefore do not invent one. Structural magnitude is evidenced
    # only by the canonical depth or prior-extreme sweep gates.

    if opposing_count >= 3 and depth_ok:
        return True

    if opposing_count == 2 and large_momentum and (swept >= 5 or depth_ok):
        return True

    return False


def finish_pullback(state: EngineState, candles: List[dict], current_i: int) -> None:
    pb = state.pullback
    if pb is None:
        return
    update_pullback_depth(pb, state)
    state.last_pullback_depth = pb.retracement
    
    if not is_structurally_valid_pullback(pb, state, candles, current_i=current_i):
        pb.active = False
        dbg(state, current_i, f"Pullback @ {pb.extreme:.2f} failed structural qualification.", candles[current_i]["time"])
        return
        
    pb.confirmed = True
    pb.active = False
    replace_minor_idm(state, pb.extreme, pb.extreme_index, candles, current_i=current_i)

    # Post-BOS sticky Major IDM logic:
    # Only promote an existing fallback Major IDM to real, or replace a swept/retired Major IDM.
    # Do NOT create a Major IDM from None during bootstrap — BOS must seed the fallback first.
    if state.major_idm and state.major_idm.fallback:
        retire_to_liquidity(state, state.major_idm)
        replace_major_idm(state, pb.extreme, pb.extreme_index, candles, fallback=False, current_i=current_i)
    elif state.major_idm and not state.major_idm.active:
        replace_major_idm(state, pb.extreme, pb.extreme_index, candles, fallback=False, current_i=current_i)

    dbg(state, current_i, f"Structurally Valid Pullback confirmed @ {pb.extreme:.2f}, depth={pb.retracement*100:.1f}%", candles[current_i]["time"])


# ============================================================
# CHoCH RESET
# ============================================================

def reset_for_choch(state: EngineState, new_trend: str, c: dict, i: int,
                    candles: List[dict]) -> None:
    """Full state reset on CHoCH while preserving retired liquidity & history."""
    retire_to_liquidity(state, state.minor_idm)
    retire_to_liquidity(state, state.major_idm)

    state.current_leg_id += 1
    state.last_valid_idm_sweep_leg_id = -1

    state.trend = new_trend
    state.bias_source = "CHoCH"
    state.reference_index = i
    state.mother_bar_index = i
    state.reference_high = c["high"]
    state.reference_low = c["low"]
    state.pullback = None
    state.minor_idm = None
    state.major_idm = None
    state.protected_high = None
    state.protected_low = None
    state.range_has_bos = False
    state.last_swept_idm_price = None
    state.last_swept_idm_type = ""

    if new_trend == "BULLISH":
        state.candidate_high = c["high"]
        state.candidate_high_index = i
        state.candidate_high_source = "PHYSICAL_CANDLE"
        state.candidate_low = float('inf')
        state.candidate_low_index = -1
        state.candidate_low_source = "NONE"
    else:
        state.candidate_low = c["low"]
        state.candidate_low_index = i
        state.candidate_low_source = "PHYSICAL_CANDLE"
        state.candidate_high = 0.0
        state.candidate_high_index = -1
        state.candidate_high_source = "NONE"


# ============================================================
# BOS HANDLER
# ============================================================

def handle_bos(state: EngineState, direction: str, c: dict, i: int,
               old_weak: StructuralLevel, depth: float, candles: List[dict]) -> None:
    ref = breaker_reference(c, direction)
    state.bos = {"direction": direction, "time": c["time"], "index": i, "depth": depth}
    state.trend = direction
    state.bias_source = "BOS"

    # Record structure snapshot BEFORE retiring IDMs / setting state.minor_idm = None
    record_structure(state, "BOS", direction, c, i, old_weak, ref, depth)

    if direction == "BULLISH":
        state.protected_high = None
        low_idx = state.candidate_low_index if (state.candidate_low_index >= 0 and state.candidate_low < float('inf')) else (state.dealing_range.low_index if state.dealing_range else i)
        low_price = candles[low_idx]["low"]
        state.protected_low = StructuralLevel(
            "LOW", low_price, low_idx,
            candles[low_idx]["time"], candles[low_idx]["close"])
        state.dealing_range = RangeState(
            "BULLISH", c["high"], state.protected_low.price,
            i, state.protected_low.index)
        state.dealing_range.low_source = "PROTECTED_SWING"
        state.dealing_range.high_source = "CANDIDATE_EXTREME"

        # Retire old IDMs and seed fallback Major IDM from new protected low
        retire_to_liquidity(state, state.minor_idm)
        retire_to_liquidity(state, state.major_idm)
        state.minor_idm = None
        replace_major_idm(state, state.protected_low.price,
                          state.protected_low.index, candles, fallback=True, current_i=i)

        state.candidate_high = c["high"]
        state.candidate_high_index = i
        state.candidate_high_source = "PHYSICAL_CANDLE"
        state.candidate_low = float('inf')
        state.candidate_low_index = -1
        state.candidate_low_source = "NONE"
    else:
        state.protected_low = None
        high_idx = state.candidate_high_index if (state.candidate_high_index >= 0 and state.candidate_high > 0) else (state.dealing_range.high_index if state.dealing_range else i)
        high_price = candles[high_idx]["high"]
        state.protected_high = StructuralLevel(
            "HIGH", high_price, high_idx,
            candles[high_idx]["time"], candles[high_idx]["close"])
        state.dealing_range = RangeState(
            "BEARISH", state.protected_high.price, c["low"],
            state.protected_high.index, i)
        state.dealing_range.high_source = "PROTECTED_SWING"
        state.dealing_range.low_source = "CANDIDATE_EXTREME"

        retire_to_liquidity(state, state.minor_idm)
        retire_to_liquidity(state, state.major_idm)
        state.minor_idm = None
        replace_major_idm(state, state.protected_high.price,
                          state.protected_high.index, candles, fallback=True, current_i=i)

        state.candidate_low = c["low"]
        state.candidate_low_index = i
        state.candidate_low_source = "PHYSICAL_CANDLE"
        state.candidate_high = 0.0
        state.candidate_high_index = -1
        state.candidate_high_source = "NONE"

    state.weak_high = None
    state.weak_low = None
    state.range_has_bos = True
    state.reference_index = i
    state.reference_high = c["high"]
    state.reference_low = c["low"]
    state.pullback = None

    state.current_leg_id += 1
    state.last_valid_idm_sweep_leg_id = -1
    state.last_swept_idm_price = None
    state.last_swept_idm_time = ""
    state.last_swept_idm_type = ""

    dbg(state, i, f"BOS {direction} confirmed, depth={depth*100:.1f}%, active leg: {state.current_leg_id}", c["time"])


# ============================================================
# PER-BAR STRUCTURAL PROCESSOR  (F-01: shared by normal loop AND outside-bar sub-events)
# ============================================================

def _process_bar(state: EngineState, c: dict, i: int, candles: List[dict],
                 ref_high_at_bar_start: Optional[float] = None,
                 ref_low_at_bar_start: Optional[float] = None) -> None:
    """
    Process one structural candle (or synthetic sub-candle from outside-bar split).
    Uses state.reference_high / state.reference_low as the current reference frame.
    For outside-bar sub-events, the caller passes the ref values captured before
    the bar started so sub-events are evaluated against the same origin reference.
    """
    ref_h = ref_high_at_bar_start if ref_high_at_bar_start is not None else state.reference_high
    ref_l = ref_low_at_bar_start  if ref_low_at_bar_start  is not None else state.reference_low

    bH = c["high"] > ref_h if ref_h is not None else False
    bL = c["low"]  < ref_l if ref_l is not None else False

    if not bH and not bL:
        # Inside the current reference: only IDM sweep is valid
        sweep_idms(state, c, i)
        return

    active_dir = state.trend if state.trend in ["BULLISH", "BEARISH"] else state.dealing_range.direction if state.dealing_range else "UNKNOWN"
    
    idm_swept_before_bar = has_taken_idm(state)

    # ====================================================
    # BULLISH TREND
    # ====================================================
    if active_dir == "BULLISH":
        target_weak_high = state.weak_high
        if c["high"] > state.candidate_high:
            state.candidate_high = c["high"]
            state.candidate_high_index = i
            state.candidate_high_source = "PHYSICAL_CANDLE"
            if state.weak_high is None or c["high"] > state.weak_high.price:
                state.weak_high = make_level(c, i, "HIGH")
            if state.dealing_range and state.trend == "BULLISH":
                state.dealing_range.high = c["high"]
                state.dealing_range.high_index = i
                state.dealing_range.high_source = "CANDIDATE_EXTREME"

        if c["low"] < state.candidate_low:
            state.candidate_low = c["low"]
            state.candidate_low_index = i
            state.candidate_low_source = "PHYSICAL_CANDLE"

        if state.pullback is None:
            if bL:
                state.pullback = PullbackState(
                    "BULLISH", state.mother_bar_index,
                    ref_h, ref_l, c["low"], i)
                update_pullback_depth(state.pullback, state)
                bootstrap_tag = " [BOOTSTRAP]" if state.trend == "UNCONFIRMED" else ""
                dbg(state, i, f"Pullback started, extreme={c['low']:.2f}{bootstrap_tag}", c["time"])
                if bH and c["high"] > state.pullback.reference_high:
                    finish_pullback(state, candles, current_i=i)
                    state.reference_index = i
                    state.mother_bar_index = i
                    state.reference_high = c["high"]
                    state.reference_low  = c["low"]
                    state.pullback = None
            elif bH and not bL:
                state.reference_index = i
                state.mother_bar_index = i
                state.reference_high = c["high"]
                state.reference_low  = c["low"]
        else:
            if c["low"] < state.pullback.extreme:
                state.pullback.extreme = c["low"]
                state.pullback.extreme_index = i
                update_pullback_depth(state.pullback, state)
            if c["high"] > state.pullback.reference_high:
                finish_pullback(state, candles, current_i=i)
                state.reference_index = i
                state.mother_bar_index = i
                state.reference_high = c["high"]
                state.reference_low  = c["low"]
                state.pullback = None

        sweep_idms(state, c, i)

        # --- BOS check ---
        if (target_weak_high and c["high"] > target_weak_high.price
                and idm_swept_before_bar
                and not choch_qualified(state, c, "BEARISH", candles)):
            depth = state.last_pullback_depth
            if state.pullback:
                update_pullback_depth(state.pullback, state)
                depth = state.pullback.retracement
                
            ref = breaker_reference(c, "BULLISH")
            body_ok = ref > target_weak_high.close
            
            if body_ok and depth < (BOS_MIN_RETRACEMENT_PCT / 100.0):
                state.candidate_low = float('inf')
                state.candidate_low_index = -1
                state.candidate_low_source = "NONE"
                
            if bullish_break_qualified(state, c, target_weak_high, depth):
                handle_bos(state, "BULLISH", c, i, target_weak_high, depth, candles)
                return

        # Genesis breakout check for Bearish BOS when UNCONFIRMED
        if state.trend == "UNCONFIRMED" and state.weak_low and c["low"] < state.weak_low.price and idm_swept_before_bar:
            depth = state.last_pullback_depth
            if state.pullback:
                update_pullback_depth(state.pullback, state)
                depth = state.pullback.retracement
            if bearish_break_qualified(state, c, state.weak_low, depth):
                handle_bos(state, "BEARISH", c, i, state.weak_low, depth, candles)
                return

        # --- CHoCH check ---
        if choch_qualified(state, c, "BEARISH"):
            level = state.protected_low
            ref = breaker_reference(c, "BEARISH")
            state.choch = {"direction": "BEARISH", "time": c["time"], "index": i}
            choch_depth = state.pullback.retracement if state.pullback else state.last_pullback_depth
            record_structure(state, "CHoCH", "BEARISH", c, i, level, ref, choch_depth)
            carried_high = state.candidate_high
            carried_high_index = state.candidate_high_index
            reset_for_choch(state, "BEARISH", c, i, candles)
            state.weak_low = make_level(c, i, "LOW")
            state.dealing_range = RangeState(
                "BEARISH",
                carried_high,
                c["low"],
                carried_high_index,
                i,
                "CHoCH_STRUCTURAL_BOUNDARY",
                "CANDIDATE_EXTREME"
            )

            dbg(state, i, f"CHoCH BEARISH. Boundary @ {carried_high:.2f}", c["time"])

    # ====================================================
    # BEARISH TREND
    # ====================================================
    elif active_dir == "BEARISH":
        target_weak_low = state.weak_low
        if c["low"] < state.candidate_low:
            state.candidate_low = c["low"]
            state.candidate_low_index = i
            state.candidate_low_source = "PHYSICAL_CANDLE"
            if state.weak_low is None or c["low"] < state.weak_low.price:
                state.weak_low = make_level(c, i, "LOW")
            if state.dealing_range and state.trend == "BEARISH":
                state.dealing_range.low = c["low"]
                state.dealing_range.low_index = i
                state.dealing_range.low_source = "CANDIDATE_EXTREME"

        if c["high"] > state.candidate_high:
            state.candidate_high = c["high"]
            state.candidate_high_index = i
            state.candidate_high_source = "PHYSICAL_CANDLE"

        if state.pullback is None:
            if bH:
                state.pullback = PullbackState(
                    "BEARISH", state.mother_bar_index,
                    ref_h, ref_l, c["high"], i)
                update_pullback_depth(state.pullback, state)
                bootstrap_tag = " [BOOTSTRAP]" if state.trend == "UNCONFIRMED" else ""
                dbg(state, i, f"Pullback started, extreme={c['high']:.2f}{bootstrap_tag}", c["time"])
                if bL and c["low"] < state.pullback.reference_low:
                    finish_pullback(state, candles, current_i=i)
                    state.reference_index = i
                    state.reference_high = c["high"]
                    state.reference_low  = c["low"]
                    state.pullback = None
            elif bL and not bH:
                state.reference_index = i
                state.mother_bar_index = i
                state.reference_high = c["high"]
                state.reference_low  = c["low"]
        else:
            if c["high"] > state.pullback.extreme:
                state.pullback.extreme = c["high"]
                state.pullback.extreme_index = i
                update_pullback_depth(state.pullback, state)
            if c["low"] < state.pullback.reference_low:
                finish_pullback(state, candles, current_i=i)
                state.reference_index = i
                state.reference_high = c["high"]
                state.reference_low  = c["low"]
                state.pullback = None

        sweep_idms(state, c, i)

        # --- BOS check ---
        if (target_weak_low and c["low"] < target_weak_low.price
                and idm_swept_before_bar
                and not choch_qualified(state, c, "BULLISH", candles)):
            depth = state.last_pullback_depth
            if state.pullback:
                update_pullback_depth(state.pullback, state)
                depth = state.pullback.retracement
                
            ref = breaker_reference(c, "BEARISH")
            body_ok = ref < target_weak_low.close
            
            if body_ok and depth < (BOS_MIN_RETRACEMENT_PCT / 100.0):
                state.candidate_high = 0.0
                state.candidate_high_index = -1
                state.candidate_high_source = "NONE"
                
            if bearish_break_qualified(state, c, target_weak_low, depth):
                handle_bos(state, "BEARISH", c, i, target_weak_low, depth, candles)
                return

        # Genesis breakout check for Bullish BOS when UNCONFIRMED
        if state.trend == "UNCONFIRMED" and state.weak_high and c["high"] > state.weak_high.price and idm_swept_before_bar:
            depth = state.last_pullback_depth
            if state.pullback:
                update_pullback_depth(state.pullback, state)
                depth = state.pullback.retracement
            if bullish_break_qualified(state, c, state.weak_high, depth):
                handle_bos(state, "BULLISH", c, i, state.weak_high, depth, candles)
                return

        # --- CHoCH check ---
        if choch_qualified(state, c, "BULLISH"):
            level = state.protected_high
            ref = breaker_reference(c, "BULLISH")
            state.choch = {"direction": "BULLISH", "time": c["time"], "index": i}
            choch_depth = state.pullback.retracement if state.pullback else state.last_pullback_depth
            record_structure(state, "CHoCH", "BULLISH", c, i, level, ref, choch_depth)
            carried_low = state.candidate_low
            carried_low_index = state.candidate_low_index
            reset_for_choch(state, "BULLISH", c, i, candles)
            state.weak_high = make_level(c, i, "HIGH")
            state.dealing_range = RangeState(
                "BULLISH",
                c["high"],
                carried_low,
                i,
                carried_low_index,
                "CANDIDATE_EXTREME",
                "CHoCH_STRUCTURAL_BOUNDARY"
            )

            dbg(state, i, f"CHoCH BULLISH. Boundary @ {carried_low:.2f}", c["time"])


def _process_outside_bar(state: EngineState, c: dict, i: int, candles: List[dict]) -> None:
    """Process one outside bar as one candle-level event.

    The candle body determines the canonical intrabar ordering for physical
    sequencing (bullish LOW -> HIGH, bearish HIGH -> LOW), but the engine never
    calls the normal processor twice. This prevents one real candle from creating
    two independent structural transitions or a same-bar IDM-sweep+BOS compound.
    Structural confirmation is deferred to a subsequent candle.
    """
    ref_h = state.reference_high
    ref_l = state.reference_low
    if ref_h is None or ref_l is None:
        sweep_idms(state, c, i)
        return

    bullish_sequence = c["close"] > c["open"]
    if c["close"] == c["open"]:
        bullish_sequence = state.trend == "BULLISH"

    # Liquidity can be taken by the physical candle, but only once.
    sweep_idms(state, c, i)

    active_dir = state.trend if state.trend in ["BULLISH", "BEARISH"] else (
        state.dealing_range.direction if state.dealing_range else "UNKNOWN"
    )

    # Track both physical extremes without treating either as a confirmed swing.
    if c["high"] > state.candidate_high:
        state.candidate_high = c["high"]
        state.candidate_high_index = i
        state.candidate_high_source = "PHYSICAL_CANDLE"
    if c["low"] < state.candidate_low:
        state.candidate_low = c["low"]
        state.candidate_low_index = i
        state.candidate_low_source = "PHYSICAL_CANDLE"

    # Deterministic LOW -> HIGH sequence is structurally useful only when it
    # aligns with an active bullish leg. Mirror for HIGH -> LOW in a bearish leg.
    if active_dir == "BULLISH" and bullish_sequence:
        if c["low"] < ref_l:
            if state.pullback is None:
                state.pullback = PullbackState(
                    "BULLISH", state.mother_bar_index, ref_h, ref_l, c["low"], i
                )
            elif c["low"] < state.pullback.extreme:
                state.pullback.extreme = c["low"]
                state.pullback.extreme_index = i
            update_pullback_depth(state.pullback, state)

        if c["high"] > ref_h:
            # LOW happened first, HIGH happened second. The pullback can become
            # structurally valid here, but BOS/CHoCH must wait for a later candle.
            if state.pullback:
                state.pullback.extreme_index = min(state.pullback.extreme_index, i)
                finish_pullback(state, candles, current_i=i)
            state.reference_index = i
            state.mother_bar_index = i
            state.reference_high = c["high"]
            state.reference_low = c["low"]
            state.pullback = None
        else:
            state.reference_low = min(ref_l, c["low"])
    elif active_dir == "BEARISH" and not bullish_sequence:
        if c["high"] > ref_h:
            if state.pullback is None:
                state.pullback = PullbackState(
                    "BEARISH", state.mother_bar_index, ref_h, ref_l, c["high"], i
                )
            elif c["high"] > state.pullback.extreme:
                state.pullback.extreme = c["high"]
                state.pullback.extreme_index = i
            update_pullback_depth(state.pullback, state)

        if c["low"] < ref_l:
            if state.pullback:
                state.pullback.extreme_index = min(state.pullback.extreme_index, i)
                finish_pullback(state, candles, current_i=i)
            state.reference_index = i
            state.mother_bar_index = i
            state.reference_high = c["high"]
            state.reference_low = c["low"]
            state.pullback = None
        else:
            state.reference_high = max(ref_h, c["high"])
    else:
        # Opposing-direction outside bar: preserve the physical extremes and
        # defer all structural interpretation to the next candle.
        state.reference_high = max(ref_h, c["high"])
        state.reference_low = min(ref_l, c["low"])

    dbg(
        state, i,
        f"OUTSIDE BAR — {'LOW→HIGH' if bullish_sequence else 'HIGH→LOW'}; "
        "single candle event; structural confirmation deferred.",
        c["time"],
    )


def run_true_smc(candles: List[dict], init_end_index: Optional[int] = None):
    init_candles = candles[:init_end_index] if init_end_index is not None else candles
    highs, lows = get_swings(init_candles)
    state = initialize(candles, highs, lows)
    if state is None:
        return None, highs, lows

    start = max(1, state.reference_index + 1)

    for i in range(start, len(candles)):
        c = candles[i]
        state.bos = None
        state.choch = None

        bH = c["high"] > state.reference_high if state.reference_high else False
        bL = c["low"]  < state.reference_low  if state.reference_low  else False

        # Inside bar / EQH / EQL bounds check
        if not bH and not bL:
            eqH = prices_equal(c["high"], state.reference_high) if state.reference_high else False
            eqL = prices_equal(c["low"], state.reference_low) if state.reference_low else False
            if eqH or eqL:
                # P3 FIX: Mother-Bar reference inheritance.
                # Transfer reference boundaries to the EQ structural candle while preserving mother provenance.
                state.reference_index = i
                state.reference_high = c["high"]
                state.reference_low = c["low"]
                if eqH:
                    state.eqh_history.append({"price": c["high"], "index": i, "mother_index": state.mother_bar_index})
                if eqL:
                    state.eql_history.append({"price": c["low"], "index": i, "mother_index": state.mother_bar_index})
                dbg(state, i, f"EQUAL HIGH/LOW. Mother reference ({state.mother_bar_index}) inherited by ({i}).", c["time"])
            
            # IDM sweeps still valid inside the range
            sweep_idms(state, c, i)
            continue

        # Canonical outside-bar processing: one real candle, one state-machine step.
        if bH and bL:
            _process_outside_bar(state, c, i, candles)
            continue

        _process_bar(state, c, i, candles)

    return state, highs, lows


# ============================================================
# MAPPER LAYER
# ============================================================

def build_mapper_result(symbol: str, candles: List[dict], state: EngineState) -> MAPPERResult:
    last = candles[-1]
    price = last["close"]
    expl = []
    warns = []

    has_bos = state.range_has_bos
    has_protected = bool(state.protected_high or state.protected_low)
    is_bootstrap = not has_bos and not has_protected and not state.structure_history
    active_dir = state.trend if state.trend in ["BULLISH", "BEARISH"] else state.dealing_range.direction if state.dealing_range else "UNKNOWN"

    has_confirmed_dr = state.trend != "UNCONFIRMED"

    # --- Pullback / Retracement ---
    ret_pct = 0.0
    f382 = False
    if state.pullback:
        update_pullback_depth(state.pullback, state)
        ret_pct = state.pullback.retracement * 100
        f382 = state.pullback.reached_threshold
    elif state.last_pullback_depth > 0:
        ret_pct = state.last_pullback_depth * 100

    invalid_retracement = ret_pct > 100.0

    info_fibs = {}
    if ret_pct > 0:
        for lvl in [23.6, 38.2, 50.0, 61.8, 68.0, 78.6, 88.6]:
            info_fibs[f"{lvl}"] = ret_pct >= lvl

    # --- Structure Quality (25% weight) ---
    sq = 0
    if has_protected:
        sq += 20; expl.append("Protected swing established")
    if has_bos:
        sq += 30; expl.append("BOS confirmed in current range")
    
    if is_bootstrap:
        warns.append("Bootstrap context; no confirmed BOS/CHoCH; no active protected swing")
    elif not has_bos:
        warns.append("No BOS in current range")

    if state.major_idm and state.major_idm.active:
        if state.major_idm.fallback:
            sq += 5; expl.append("Fallback Major IDM active")
        else:
            sq += 15; expl.append("Real Major IDM active")
    elif state.major_idm and state.major_idm.swept:
        sq += 10; expl.append("Major IDM swept")

    if state.minor_idm and state.minor_idm.active:
        sq += 15
    if state.dealing_range and has_confirmed_dr:
        sq += 10
    if state.structure_history:
        sq += 10
    sq = min(100, sq)

    # --- Location Quality (20% weight) & Normalized Invalidation Distance ---
    lq = None
    ml = "N/A"
    dr_h = dr_l = dr_eq = dr_h_src = dr_l_src = None
    inv_dist = None
    if state.dealing_range and has_confirmed_dr:
        dr = state.dealing_range
        dr_h = dr.high
        dr_l = dr.low
        dr_eq = (dr_h + dr_l) / 2
        dr_h_src = dr.high_source
        dr_l_src = dr.low_source
        span = dr_h - dr_l
        if span > 0:
            pct = (price - dr_l) / span
            if pct < 0.0 or pct > 1.0:
                ml = "OUTSIDE_DR"
                lq = 0
                warns.append("Price is outside the current dealing range")
            else:
                if pct > 0.618:
                    ml = "PREMIUM"
                    lq = 35 if active_dir == "BULLISH" else 85
                elif pct < 0.382:
                    ml = "DISCOUNT"
                    lq = 85 if active_dir == "BULLISH" else 35
                else:
                    ml = "EQUILIBRIUM"
                    lq = 60

            if active_dir == "BULLISH" and state.protected_low:
                inv_dist = (price - state.protected_low.price) / span
            elif active_dir == "BEARISH" and state.protected_high:
                inv_dist = (state.protected_high.price - price) / span

    # --- Setup Quality (30% weight) ---
    setup_q = 10
    setup_state = "NO_SETUP"
    
    if invalid_retracement:
        setup_state = "INVALIDATED_RETRACEMENT"
        setup_q = 0
    elif state.bos:
        setup_state = "BOS_CONFIRMED"
        setup_q = 85
    elif state.choch:
        if state.pullback and state.pullback.active:
            setup_state = "POST_CHOCH_PULLBACK_THRESHOLD" if f382 else "POST_CHOCH_PULLBACK"
            setup_q = 65 if f382 else 50
        else:
            setup_state = "CHOCH_CONFIRMED"
            setup_q = 60
    elif state.pullback and state.pullback.active:
        if has_bos:
            if f382:
                setup_state = "POST_BOS_PULLBACK_THRESHOLD"
                setup_q = 80
            else:
                setup_state = "PULLBACK_DEVELOPING"
                setup_q = 15
        else:
            if f382:
                setup_state = "BOOTSTRAP_PULLBACK_THRESHOLD"
                setup_q = 50
            else:
                setup_state = "PULLBACK_DEVELOPING"
                setup_q = 10
    elif has_taken_idm(state):
        setup_state = "IDM_SWEPT_WAITING"
        setup_q = 55 if has_bos else 30

    # --- Liquidity Quality (15% weight) ---
    liq_q = 0
    liq_obj = "None"
    liq_price = None
    if state.major_idm and state.major_idm.active:
        status_label = "FALLBACK" if state.major_idm.fallback else "REAL"
        liq_obj = f"Major IDM ({state.major_idm.kind} - {status_label})"
        liq_price = state.major_idm.price
        liq_q = 40 if state.major_idm.fallback else 80
    elif state.minor_idm and state.minor_idm.active:
        liq_obj = f"Minor IDM ({state.minor_idm.kind})"
        liq_price = state.minor_idm.price
        liq_q = 60

    # --- Risk Quality (10% weight) ---
    rq = 80
    depth_penalty = 0
    if has_confirmed_dr:
        if ret_pct > 100.0:
            depth_penalty = 80
            warns.append("Retracement > 100% — setup invalidated")
        elif ret_pct > 78.6:
            depth_penalty = 25
            warns.append(f"Deep retracement ({ret_pct:.1f}%) — near invalidation zone")
            if ret_pct > 90.0:
                depth_penalty = 45
                warns.append("Extreme retracement — high risk of protected level failure")

    prox_penalty = 0
    if inv_dist is not None:
        if inv_dist < 0.10:
            prox_penalty = 25
            warns.append(f"High invalidation proximity ({inv_dist*100:.1f}% range left to protected level)")
            if inv_dist < 0.03:
                prox_penalty = 45

    # Bounded penalty prevents double-counting of depth % and invalidation distance
    risk_penalty = max(depth_penalty, prox_penalty)
    rq -= risk_penalty

    if has_confirmed_dr:
        if ml == "PREMIUM" and active_dir == "BULLISH":
            rq -= 15; warns.append("Extended in premium (bullish)")
        if ml == "DISCOUNT" and active_dir == "BEARISH":
            rq -= 15; warns.append("Extended in discount (bearish)")
    if not has_bos:
        rq -= 10
    rq = max(0, min(100, rq))

    # --- Final Score & Gating ---
    if state.trend == "UNCONFIRMED" and not is_bootstrap:
        sq = 0
        setup_state = "NO_SETUP"
        setup_q = 0
        lq = None
        ml = "N/A"
        dr_h = dr_l = dr_eq = dr_h_src = dr_l_src = None
        info_fibs = {}
        liq_q = 0
        rq = None
        final = 0
        tier = "WATCH"
        warns.append("No confirmed structure; no confirmed BOS/CHoCH; no protected swing; no actionable setup")
    else:
        if lq is None:
            lq = 0
            warns.append("No confirmed dealing range — location unavailable")
        final = int(round(sq * 0.25 + setup_q * 0.30 + lq * 0.20 + liq_q * 0.15 + rq * 0.10))

        # Structural Gates
        if invalid_retracement or not has_protected:
            final = min(final, 49)
            tier = "WATCH"
        else:
            tier = "HIGH" if final >= 70 else "MEDIUM" if final >= 55 else "LOW" if final >= 40 else "WATCH"

    maj_status = ("FALLBACK" if state.major_idm and state.major_idm.fallback and state.major_idm.active
                  else "REAL" if state.major_idm and state.major_idm.active
                  else "SWEPT" if state.major_idm and state.major_idm.swept
                  else "NONE")

    min_status = ("ACTIVE" if state.minor_idm and state.minor_idm.active
                  else "SWEPT" if state.minor_idm and state.minor_idm.swept
                  else "NONE")

    return MAPPERResult(
        symbol=symbol, timeframe=INTERVAL, current_price=price,
        structural_bias=state.trend, bias_source=state.bias_source, structure_state=setup_state,
        protected_high=state.protected_high.price if state.protected_high else None,
        protected_low=state.protected_low.price if state.protected_low else None,
        major_idm=state.major_idm.price if state.major_idm else None,
        major_idm_status=maj_status,
        minor_idm=state.minor_idm.price if state.minor_idm else None,
        minor_idm_status=min_status,
        dealing_range_high=dr_h, dealing_range_low=dr_l, dealing_range_eq=dr_eq,
        dealing_range_high_source=dr_h_src, dealing_range_low_source=dr_l_src,
        market_location=ml, retracement_pct=ret_pct,
        fib_382=f382, info_fibs=info_fibs,
        candidate_high=state.candidate_high if state.candidate_high > 0 else None,
        candidate_low=state.candidate_low if state.candidate_low < float('inf') else None,
        active_pullback_extreme=state.pullback.extreme if state.pullback and state.pullback.active else None,
        liquidity_objective=liq_obj, liquidity_objective_price=liq_price,
        setup_state=setup_state, structure_quality=sq, setup_quality=setup_q,
        location_quality=lq, liquidity_quality=liq_q, risk_quality=rq,
        final_score=final, quality_tier=tier, explanation=expl, warnings=warns,
    )


# ============================================================
# OUTPUT
# ============================================================

def print_mapper_summary(results: List[MAPPERResult]) -> None:
    results.sort(key=lambda r: r.final_score, reverse=True)
    print()
    print("TRUE SMC MAPPER")
    print("-" * 88)
    print(f"{'Rank':<5} {'Symbol':<8} {'Bias':<6} {'State':<25} {'Location':<12} {'Tier':<8} {'Score':>5}")
    print("-" * 88)
    for rank, r in enumerate(results, 1):
        if r.error:
            print(f"{rank:<5} {r.symbol:<8} {'ERR':<6} {r.error[:40]:<25}")
            continue
        print(f"{rank:<5} {r.symbol:<8} {r.structural_bias[:4]:<6} "
              f"{r.setup_state:<25} {r.market_location:<12} {r.quality_tier:<8} {r.final_score:>5}")
    print("-" * 88)


def print_detail(r: MAPPERResult, state: Optional[EngineState] = None) -> None:
    print()
    print(f"=== {r.symbol} DETAIL [{r.quality_tier}] ===")
    print(f"  Bias: {r.structural_bias}  |  Price: {r.current_price:.2f}  |  Location: {r.market_location}")
    if r.dealing_range_high is not None:
        print(f"  Dealing Range:")
        h_src_str = f" [{r.dealing_range_high_source}]" if r.dealing_range_high_source else ""
        l_src_str = f" [{r.dealing_range_low_source}]" if r.dealing_range_low_source else ""
        print(f"    Low:  {r.dealing_range_low:.2f}{l_src_str}")
        print(f"    EQ:   {r.dealing_range_eq:.2f}")
        print(f"    High: {r.dealing_range_high:.2f}{h_src_str}")
        if DEBUG and state and state.dealing_range:
            dr = state.dealing_range
            print(f"    DR: low={dr.low:.2f} @ BAR {dr.low_index} | eq={r.dealing_range_eq:.2f} | high={dr.high:.2f} @ BAR {dr.high_index}")
    else:
        print("  Dealing Range: N/A")
    if r.protected_high:
        print(f"  Protected High: {r.protected_high:.2f}")
    if r.protected_low:
        print(f"  Protected Low:  {r.protected_low:.2f}")
    if r.protected_high is None and r.protected_low is None:
        print(f"  Protected High: NONE")
        print(f"  Protected Low:  NONE")

    print()
    print(f"  Candidate High: {f'{r.candidate_high:.2f}' if r.candidate_high else 'NONE'}")
    print(f"  Candidate Low:  {f'{r.candidate_low:.2f}' if r.candidate_low else 'NONE'}")
    print(f"  Active Pullback Extreme: {f'{r.active_pullback_extreme:.2f}' if r.active_pullback_extreme else 'NONE'}")
    print()
    print(f"  Major IDM: {r.major_idm:.2f} [{r.major_idm_status}]" if r.major_idm else "  Major IDM: None")
    print(f"  Minor IDM: {r.minor_idm:.2f} [{r.minor_idm_status}]" if r.minor_idm else "  Minor IDM: None")

    if state and state.liquidity:
        active_pool = [f"${l.price:.2f}" for l in state.liquidity if not l.taken]
        swept_pool = [f"x${l.price:.2f}" for l in state.liquidity if l.taken]
        liq_parts = []
        if active_pool:
            liq_parts.append(f"Active Pool ($): {', '.join(active_pool[:4])}")
        if swept_pool:
            liq_parts.append(f"Swept Pool (x$): {', '.join(swept_pool[:4])}")
        if liq_parts:
            print(f"  Liquidity Pool: {' | '.join(liq_parts)}")

    if r.retracement_pct > 0:
        print(f"  Retracement: {r.retracement_pct:.1f}%")
        print(f"    Fib:")
        for lvl, met in r.info_fibs.items():
            print(f"      {lvl}={met}")
        print()
        print(f"    BOS Threshold ({BOS_MIN_RETRACEMENT_PCT}%): {r.fib_382}")
    print(f"  Liq Objective: {r.liquidity_objective}" +
          (f" @ {r.liquidity_objective_price:.2f}" if r.liquidity_objective_price else ""))
    print(f"  Setup: {r.setup_state}")
    print(f"  SCORES [W: sq 25%, setup 30%, loc 20%, liq 15%, risk 10%]:")
    lq_txt = "N/A" if r.location_quality is None else r.location_quality
    rq_txt = "N/A" if r.risk_quality is None else r.risk_quality
    print(f"    struct={r.structure_quality} setup={r.setup_quality} loc={lq_txt} "
          f"liq={r.liquidity_quality} risk={rq_txt} -> {r.final_score} ({r.quality_tier})")
    if r.explanation:
        print(f"  WHY: {'; '.join(r.explanation)}")
    if r.warnings:
        print(f"  WARN: {'; '.join(r.warnings)}")

    if state and state.structure_history:
        print(f"  HISTORY:")
        for n, h in enumerate(state.structure_history[:5], 1):
            proof = f" [IDM taken @ {h.idm_swept_price:.2f} ({h.idm_swept_type})]" if h.idm_swept and h.idm_swept_price else " [No IDM proof]"
            weak_str = f"{h.weak_price:.2f}" if h.weak_price is not None else "N/A"
            print(f"    [{n}] {h.event} {h.direction} {h.time} | break={h.break_price:.2f} ref={h.breaker_reference:.2f} weak={weak_str} depth={h.retracement*100:.1f}%{proof}")

    if state and DEBUG and state.debug_log:
        print(f"  DEBUG LOG:")
        for line in state.debug_log[-20:]:
            print(f"    {line}")


# ============================================================
# MAIN
# ============================================================

def _make_error_result(symbol: str, error: str) -> MAPPERResult:
    return MAPPERResult(
        symbol=symbol, timeframe=INTERVAL, current_price=0,
        structural_bias="NONE", structure_state="ERROR",
        protected_high=None, protected_low=None,
        major_idm=None, major_idm_status="NONE",
        minor_idm=None, minor_idm_status="NONE",
        dealing_range_high=None, dealing_range_low=None, dealing_range_eq=None,
        dealing_range_high_source=None, dealing_range_low_source=None,
        market_location="UNKNOWN", retracement_pct=0,
        fib_382=False, info_fibs={},
        candidate_high=None, candidate_low=None, active_pullback_extreme=None,
        liquidity_objective="None", liquidity_objective_price=None,
        setup_state="ERROR", structure_quality=0, setup_quality=0,
        location_quality=0, liquidity_quality=0, risk_quality=0,
        final_score=0, quality_tier="WATCH", error=error)


def main():
    try:
        provider = auto_detect_provider()
    except RuntimeError as e:
        print(f"ERROR: {e}")
        return

    print(f"Provider: {provider.name}  |  Interval: {INTERVAL}  |  Bars: {BAR_COUNT}")
    print()

    results = []
    states = {}

    for symbol in TICKERS:
        try:
            req = DataRequest(symbol=symbol, interval=INTERVAL, bar_count=BAR_COUNT)
            candles = fetch_candles(provider, req)
            state, _, _ = run_true_smc(candles)
            if state is None:
                r = _make_error_result(symbol, "Insufficient structure")
            else:
                r = build_mapper_result(symbol, candles, state)
                states[symbol] = state
            results.append(r)
        except Exception as e:
            results.append(_make_error_result(symbol, str(e)))
        if provider.name != "demo":
            time.sleep(1.0)

    print_mapper_summary(results)
    for r in sorted(results, key=lambda x: x.final_score, reverse=True):
        if not r.error:
            print_detail(r, states.get(r.symbol))

    print()
    print("=" * 40)
    print("SCAN COMPLETE")


if __name__ == "__main__":
    main()
