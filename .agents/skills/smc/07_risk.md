# 05 — RISK

**Role:** Risk, scoring, position sizing, trade management, and execution-lifecycle policy.

**Authority boundary:** Risk is downstream from canonical structural validation. It consumes canonical structural/execution state and must never create, validate, reinterpret, or redefine structural truth.

**Scoring boundary:** The methodology defines the risk concepts and gating semantics. The concrete risk_quality calculation and final weighted score are implementation behavior owned by SMC_mapper.py and documented in 08_implementation.md. This document must not invent a competing scoring formula.

## 5.1 Structural Stop-Loss Placement

### Tier 1 — Structural / Zone Boundary Stop

Conservative stop placement is beyond the furthest relevant boundary of the parent OF_CONFIRMED / Valid Order Block according to the applicable execution module.

A stop placement or stop touch does not itself create structural truth:

```
EXECUTION_STOPPED_OUT ≠ ORDER_FLOW_FAILED
EXECUTION_STOPPED_OUT ≠ ORDER_BLOCK_FAILED
EXECUTION_STOPPED_OUT ≠ VALID_BOS
EXECUTION_STOPPED_OUT ≠ CHoCH_CONFIRMED
```

### Tier 2 — Refined Pattern Extreme Stop

Tier 2 is optional and available only after a deterministic canonical candlestick reversal has actually triggered the entry.

Bullish:

```
SL = min(Low_pattern_candles) - P
```

Bearish:

```
SL = max(High_pattern_candles) + P
```

P is a downstream/configurable buffer. The methodology does not define a universal pip/tick or Spread + Minimum Tick value.

Tier 2 is not available for a direct limit entry without deterministic candle confirmation, and qualitative-only Momentum/Shrinking filters cannot authorize it.

### Tier-2 stop-out semantics

```
Price <= Tier-2 bullish SL
OR
Price >= Tier-2 bearish SL
        ↓
EXECUTION_STOPPED_OUT
```

This remains an execution/risk event and is not POI failure, structural invalidation, BOS, CHoCH, or IDM creation.

## 5.2 Target Policy

### Primary pro-trend target

The primary final target is the current Trading Range confirmed external extreme where the applicable execution module requires it:

```
bullish → Confirmed_Swing_High
bearish → Confirmed_Swing_Low
```

The target is an execution/risk object. It does not validate BOS.

```
TARGET_HIT ≠ VALID_BOS
```

When VALID_BOS occurs, the previous external target expires and the new Trading Range external extreme becomes the active structural target.

When CHoCH_CONFIRMED occurs, targets belonging exclusively to the invalidated structural regime become invalid as an execution/risk lifecycle consequence. This does not manufacture a structural event.

### RR gating

Where required by the canonical execution layer:

```
Projected_RR_to_Primary_Target >= 1:2
```

This is an entry/setup gate, not a target-location rule.

### Counter-trend / pullback execution

Counter-trend execution may use IDM/Engineering Liquidity sweep + valid POI + closed canonical reversal. Its expected structural destination may be an unmitigated parent Decisional POI / Extreme POI (OF_CONFIRMED / Valid OB), but no universal hard TP coordinate is canonicalized here.

IRL is not a canonical TP category. Internal liquidity, Engineering Liquidity, internal OF/OB, and Minor IDM remain context/execution objects rather than mandatory TP coordinates.

No fixed partial-TP percentage, break-even trigger, or trailing algorithm is canonicalized here.

## 5.3 Pending-Order and Open-Position Lifecycle

### 5.3.1 Pending Order Invalidation

```
ORDER_FLOW_FAILED / ORDER_BLOCK_FAILED
        ↓
associated pending order
        ↓
PENDING_ORDER_CANCELLED
```

```
VALID_BOS
        ↓
previous Trading Range dependent orders
        ↓
EXPIRED_CANCELLED
```

```
CHoCH_CONFIRMED
        ↓
pending orders dependent on invalidated regime
        ↓
PENDING_ORDER_CANCELLED
```

CHoCH_ELIGIBLE alone does not automatically cancel pending orders.

A historical Origin OB (latent POI) may remain as a historical object after a parent OF lifecycle transition when its own validity remains canonical.

### 5.3.2 Zone Failure

Bullish zone failure:

```
Close < lower_zone_boundary
```

Bearish zone failure:

```
Close > upper_zone_boundary
```

Wick penetration alone is not zone failure unless a canonical execution rule explicitly says otherwise.

### 5.3.3 Open Position Exit Separation

Broker-side stop and target events remain mechanical execution events:

```
OPEN POSITION
   ├── TARGET_HIT
   └── STOP_LOSS_TOUCH
```

Do not synthesize a market close merely because a POI failed, a zone failed, BOS occurred, or CHoCH occurred.

```
EXECUTION_STOPPED_OUT
≠ POI_FAILED
≠ ORDER_FLOW_FAILED
≠ ORDER_BLOCK_FAILED
≠ VALID_BOS
≠ CHoCH_CONFIRMED
```

### 5.3.4 Emergency Structural Kill-Switch

“Kill-Switch” is project execution-control terminology, not an independent structural entity.

```
CHoCH_CONFIRMED ↛ mandatory MARKET_CLOSE_ON_CHOCH
ORDER_FLOW_FAILED ↛ mandatory MARKET_CLOSE
ORDER_BLOCK_FAILED ↛ mandatory MARKET_CLOSE
```

No authoritative forced market-close behavior is canonicalized solely from these events.

### 5.3.5 Pending vs Open Position

Pending-order premise invalidation terminates the pending order. An already-open position continues its own execution lifecycle until a mechanical target/stop event or a separately authorized exit occurs.

```
PENDING ORDER INVALIDATION → CANCEL
OPEN POSITION → CONTINUE LIFECYCLE
```

### 5.3.6 G1 — OHLC vs Intrabar Sequence

Absolute invariant:

```
OHLC ≠ INTRABAR_SEQUENCE
```

Intrabar execution events may include:

```
ORDER_TRIGGERED
STOP_TOUCH
TARGET_TOUCH
```

Candle-close structural/execution events include:

```
ORDER_FLOW_FAILED
ORDER_BLOCK_FAILED
VALID_BOS
CHoCH_CONFIRMED
```

If STOP_TOUCH and TARGET_TOUCH are both reachable inside one OHLC candle, the methodology cannot deterministically establish which occurred first. That requires lower-timeframe/tick data or broker execution records. Do not invent microsequence from OHLC.

## 5.4 Risk Invariants

```
RISK CONSUMES STRUCTURE
RISK DOES NOT CREATE STRUCTURE

POI INVALIDATION ≠ STRUCTURAL INVALIDATION
STRUCTURAL INVALIDATION ≠ RISK STOP
RISK STOP ≠ EXECUTION_STOPPED_OUT
TARGET_HIT ≠ VALID_BOS
CHoCH_CONFIRMED ↛ mandatory MARKET_CLOSE_ON_CHOCH
```

## 5.5 Scoring boundary — IMPLEMENTATION-OWNED

The mapper exposes a weighted quality score, but the weights, tier thresholds, penalty arithmetic, and liquidity-quality values are implementation behavior rather than independent SMC methodology.

`07_risk.md` does not own those numeric values. The single detailed implementation mapping is maintained in `08_implementation.md`, alongside the executable risk-quality calculation.

This document therefore records only the ownership boundary:

```
RISK METHODOLOGY
    ↓
consumes canonical structural/execution state
    ↓
08_implementation.md / SMC_mapper.py
    ↓
concrete scoring arithmetic
```

No risk score, tier, or implementation penalty may manufacture or validate IDM, CONFIRMED_STRUCTURAL_SWING, Protected Structural Extreme, VALID_BOS, CHoCH_CONFIRMED, Trading Range, or POI ontology.

## 5.6 Architectural Separation

Risk remains a downstream consumer of structural and execution state. No risk rule may manufacture IDM, CONFIRMED_STRUCTURAL_SWING, Protected Structural Extreme, VALID_BOS, CHoCH_CONFIRMED, Trading Range, or POI ontology.

The canonical separation:

```
STRUCTURE → EXECUTION → RISK
```