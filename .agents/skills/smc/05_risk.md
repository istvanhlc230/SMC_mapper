# 05 — RISK

**Role:** Risk, scoring, position sizing, trade management, and execution-lifecycle policy.

**Authority boundary:** Risk is downstream from canonical structural validation. It consumes canonical structural/execution state and must never create, validate, reinterpret, or redefine structural truth.

## 5.1 Structural Stop-Loss Placement — PASS / CLOSED

### Tier 1 — Structural / Zone Boundary Stop

Conservative stop placement is beyond the furthest relevant boundary of the parent Valid Order Flow / Valid Order Block according to the applicable execution module.

A stop placement or stop touch does not itself create structural truth:

```text
EXECUTION_STOPPED_OUT ≠ ORDER_FLOW_FAILED
EXECUTION_STOPPED_OUT ≠ ORDER_BLOCK_FAILED
EXECUTION_STOPPED_OUT ≠ VALID_BOS
EXECUTION_STOPPED_OUT ≠ VALID_CHoCH
```

### Tier 2 — Refined Pattern Extreme Stop

Tier 2 is optional and available only after a deterministic canonical candlestick reversal has actually triggered the entry.

Bullish:

```text
SL = min(Low_pattern_candles) - P
```

Bearish:

```text
SL = max(High_pattern_candles) + P
```

`P` is a downstream/configurable buffer. The methodology does not define a universal pip/tick or Spread + Minimum Tick value.

Tier 2 is not available for a direct limit entry without deterministic candle confirmation, and qualitative-only Momentum/Shrinking filters cannot authorize it.

### Tier-2 stop-out semantics

```text
Price <= Tier-2 bullish SL
OR
Price >= Tier-2 bearish SL
        ↓
EXECUTION_STOPPED_OUT
```

This remains an execution/risk event and is not POI failure, structural invalidation, BOS, CHoCH, or IDM creation.

## 5.2 Target audit — PASS / CLOSED

### Primary pro-trend target

The primary final target is the current Trading Range confirmed external extreme where the applicable execution module requires it:

```text
bullish → Confirmed_Swing_High
bearish → Confirmed_Swing_Low
```

The target is an execution/risk object. It does not validate BOS.

```text
TARGET_HIT ≠ VALID_BOS
```

When `VALID_BOS` occurs, the previous external target expires and the new Trading Range external extreme becomes the active structural target.

When `VALID_CHoCH` occurs, targets belonging exclusively to the invalidated structural regime become invalid as an execution/risk lifecycle consequence. This does not manufacture a structural event.

### RR gating

Where required by the canonical execution layer:

```text
Projected_RR_to_Primary_Target >= 1:2
```

This is an entry/setup gate, not a target-location rule.

### Counter-trend / pullback execution

Counter-trend execution may use IDM/Engineering Liquidity sweep + valid POI + closed canonical reversal. Its expected structural destination may be an unmitigated parent Decisional/Extreme OF/OB, but no universal hard TP coordinate is canonicalized here.

IRL is not a canonical TP category. Internal liquidity, Engineering Liquidity, internal OF/OB, and Minor IDM remain context/execution objects rather than mandatory TP coordinates.

No fixed partial-TP percentage, break-even trigger, or trailing algorithm is canonicalized here.

## 5.3 Pending-order and open-position lifecycle — PASS / CLOSED

### 5.3.1 Pending Order Invalidation

```text
ORDER_FLOW_FAILED / ORDER_BLOCK_FAILED
        ↓
associated pending order
        ↓
PENDING_ORDER_CANCELLED
```

```text
VALID_BOS
        ↓
previous Trading Range dependent orders
        ↓
EXPIRED_CANCELLED
```

```text
VALID_CHoCH
        ↓
pending orders dependent on invalidated regime
        ↓
PENDING_ORDER_CANCELLED
```

`CHoCH_ELIGIBLE` alone does not automatically cancel pending orders.

A historical Origin OB may remain as a historical object after a parent OF lifecycle transition when its own validity remains canonical.

### 5.3.2 Zone Failure

Bullish zone failure:

```text
Close < lower_zone_boundary
```

Bearish zone failure:

```text
Close > upper_zone_boundary
```

Wick penetration alone is not zone failure unless a canonical execution rule explicitly says otherwise.

### 5.3.3 Open Position Exit Separation

Broker-side stop and target events remain mechanical execution events:

```text
OPEN POSITION
   ├── TARGET_HIT
   └── STOP_LOSS_TOUCH
```

Do not synthesize a market close merely because a POI failed, a zone failed, BOS occurred, or CHoCH occurred.

```text
EXECUTION_STOPPED_OUT
≠ POI_FAILED
≠ ORDER_FLOW_FAILED
≠ ORDER_BLOCK_FAILED
≠ VALID_BOS
≠ VALID_CHoCH
```

### 5.3.4 Emergency Structural Kill-Switch

“Kill-Switch” is project execution-control terminology, not an independent structural entity.

```text
VALID_CHoCH ↛ mandatory MARKET_CLOSE_ON_CHOCH
ORDER_FLOW_FAILED ↛ mandatory MARKET_CLOSE
ORDER_BLOCK_FAILED ↛ mandatory MARKET_CLOSE
```

No authoritative forced market-close behavior is canonicalized solely from these events.

### 5.3.5 Pending vs Open Position

Pending-order premise invalidation terminates the pending order. An already-open position continues its own execution lifecycle until a mechanical target/stop event or a separately authorized exit occurs.

```text
PENDING ORDER INVALIDATION → CANCEL
OPEN POSITION → CONTINUE LIFECYCLE
```

### 5.3.6 G1 — OHLC vs Intrabar Sequence

Absolute invariant:

```text
OHLC ≠ INTRABAR_SEQUENCE
```

Intrabar execution events may include:

```text
ORDER_TRIGGERED
STOP_TOUCH
TARGET_TOUCH
```

Candle-close structural/execution events include:

```text
ORDER_FLOW_FAILED
ORDER_BLOCK_FAILED
VALID_BOS
VALID_CHoCH
```

If STOP_TOUCH and TARGET_TOUCH are both reachable inside one OHLC candle, the methodology cannot deterministically establish which occurred first. That requires lower-timeframe/tick data or broker execution records. Do not invent microsequence from OHLC.

## 5.4 Risk invariants — PASS / CLOSED

```text
RISK CONSUMES STRUCTURE
RISK DOES NOT CREATE STRUCTURE

POI INVALIDATION ≠ STRUCTURAL INVALIDATION
STRUCTURAL INVALIDATION ≠ RISK STOP
RISK STOP ≠ EXECUTION_STOPPED_OUT
TARGET_HIT ≠ VALID_BOS
VALID_CHoCH ↛ mandatory MARKET_CLOSE_ON_CHOCH
```

## 5.5 Scoring — PASS / CLOSED

Existing scoring weights remain:

```text
Structure = 25%
Setup     = 30%
Location  = 20%
Liquidity = 15%
Risk      = 10%
```

Quality tiers:

```text
HIGH   >= 70
MEDIUM >= 55
LOW    >= 40
WATCH  < 40
```

Liquidity quality:

```text
Real Major IDM     = 80
Fallback Major IDM = 40
```

Risk penalties:

```text
Retracement > 78.6% → -25
Retracement > 90.0% → -20
```

Scoring is downstream policy only. It cannot create, validate, or reinterpret structure.

## 5.6 Audit closure

Risk remains a downstream consumer of structural and execution state. No risk rule may manufacture IDM, Confirmed Swing, Protected Structural Extreme, BOS, CHoCH, Trading Range, or POI ontology.

The canonical separation is closed:

```text
STRUCTURE → EXECUTION → RISK
```
