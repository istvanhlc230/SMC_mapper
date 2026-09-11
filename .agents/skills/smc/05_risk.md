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

### Tier 2 — Deterministic Pattern Extreme Stop

Optional refined stop is permitted only after a deterministic canonical candlestick reversal has produced the entry trigger by confirmed close.

Canonical deterministic patterns:

- Long Wick Rejection
- Multiple Wick Rejection
- Engulfing
- Morning Star
- Evening Star

Bullish:

```text
SL = min(Low_pattern_candles) - P
```

Bearish:

```text
SL = max(High_pattern_candles) + P
```

`P` is **SOURCE-PENDING / downstream configuration**. No universal pip/tick or `Spread + Minimum Tick` default is canonicalized.

Qualitative-only momentum filters cannot authorize Tier-2 placement.

### Stop-Out

Broker hard-stop touch produces:

```text
EXECUTION_STOPPED_OUT
```

It does not retroactively create POI failure or structural invalidation.

---

## 5.2 Target Definition & Take-Profit Hierarchy — PASS / CLOSED

### 5.2.1 Primary Macro Target

The primary pro-trend final target is the current Trading Range confirmed external extreme.

```text
Bullish → Confirmed_Swing_High
Bearish → Confirmed_Swing_Low
```

### 5.2.2 Target Hit vs BOS

```text
TARGET_HIT ≠ PHYSICAL_BREAK ≠ VALID_BOS
```

Target execution does not manufacture BOS.

`VALID_BOS` expires the previous external target and establishes the new Trading Range external extreme as the active target.

```text
VALID_BOS
    ↓
previous target → TARGET_EXPIRED
    ↓
new range external extreme → ACTIVE_PRIMARY_TARGET
```

### 5.2.3 CHoCH Target Lifecycle

When `VALID_CHoCH` invalidates a structural regime, pending execution targets belonging to that invalidated regime become:

```text
TARGET_INVALIDATED
```

This is an execution/risk lifecycle consequence, not a rewrite of historical structural meaning.

### 5.2.4 R:R Gate

```text
Projected_RR_to_Primary_Target >= 1:2
```

is an **entry/setup gating constraint**, not a TP coordinate. It must not be interpreted as `TP = 2R`.

### 5.2.5 Counter-Trend / Pullback Target — SOURCE-PENDING / SAFE-MODE

Counter-trend/pullback execution may use canonical IDM/Engineering Liquidity Sweep + valid POI + closed canonical reversal. An unmitigated parent Decisional/Extreme OF/OB may be the expected destination, but no mandatory universal hard TP coordinate is canonicalized here.

### 5.2.6 IRL / Internal Targets — SOURCE-PENDING / NOT CANONICALIZED

IRL and other internal target categories are not canonical fixed TP destinations in this specification.

### 5.2.7 Partial TP / BE / Trailing — DOWNSTREAM / OUT OF CANONICAL SCOPE

No canonical fixed partial percentage, break-even trigger, or trailing algorithm is established here.

---

## 5.3 Invalidation & Kill-Switch Mechanics — PASS / CLOSED

### 5.3.1 Pending Order Invalidation

A pending order remains valid only while its execution premise remains valid.

```text
ORDER_FLOW_FAILED / ORDER_BLOCK_FAILED
    ↓
associated pending order
    ↓
PENDING_ORDER_CANCELLED
```

`VALID_BOS` expires pending orders dependent on the previous Trading Range:

```text
VALID_BOS → EXPIRED_CANCELLED
```

Historical Origin OB references may remain passive historical objects when independently valid; they do not remain tradable merely because they exist historically.

`VALID_CHoCH` cancels pending orders dependent on the invalidated structural regime:

```text
VALID_CHoCH
    ↓
pending orders dependent on invalidated regime
    ↓
PENDING_ORDER_CANCELLED
```

`CHoCH_ELIGIBLE` alone does not trigger this cancellation.

### 5.3.2 Zone Failure Boundaries

Zone failure requires a candle **body close** beyond the opposite boundary.

Bullish zone:

```text
Close < lower_zone_boundary
```

Bearish zone:

```text
Close > upper_zone_boundary
```

Therefore:

```text
WICK PENETRATION ≠ ZONE FAILURE
```

A wick may represent mitigation or a sweep according to canonical context.

### 5.3.3 Open Position Exit Separation

Broker-side SL is the canonical mechanical risk exit. `TARGET_HIT` is a separate broker-side profit exit.

```text
OPEN POSITION
├── TARGET_HIT → broker-side profit exit
└── STOP_LOSS_TOUCH → broker-side risk exit
```

There is no synthetic structural exit generated merely by POI/zone failure or CHoCH.

```text
EXECUTION_STOPPED_OUT
    ≠ POI_FAILED
    ≠ ORDER_FLOW_FAILED
    ≠ ORDER_BLOCK_FAILED
    ≠ VALID_BOS
    ≠ VALID_CHoCH
```

### 5.3.4 Emergency Structural Kill-Switch — SOURCE-PENDING / OUT OF CANONICAL SCOPE

“Kill-Switch” is project terminology for execution-intent cancellation after a canonical invalidating event; it is not an independent structural entity.

For an open position:

```text
VALID_CHoCH ↛ mandatory MARKET_CLOSE_ON_CHOCH
ORDER_FLOW_FAILED ↛ mandatory MARKET_CLOSE
ORDER_BLOCK_FAILED ↛ mandatory MARKET_CLOSE
```

No authoritative canonical rule establishes forced market closure solely because one of these structural/execution events occurs.

### 5.3.5 Pending Order vs Open Position

Pending orders and open positions are separate lifecycle objects.

```text
PENDING ORDER
    ↓
premise invalidated
    ↓
CANCELLED
```

versus:

```text
OPEN POSITION
    ↓
existing lifecycle continues
    ↓
TARGET_HIT / STOP_LOSS_TOUCH / separately authorized exit
```

Cancellation of a pending order must never be implemented as an implicit market close of an existing position.

### 5.3.6 G1 — Intrabar Sequence — SOURCE-PENDING / SAFE-MODE

```text
OHLC ≠ INTRABAR_SEQUENCE
```

OHLC provides Open, High, Low, and Close, but does not encode the chronological path inside the candle.

Therefore the methodology must **not** assume a deterministic order such as:

```text
STOP_TOUCH < TARGET_TOUCH
```

or:

```text
TARGET_TOUCH < STOP_TOUCH
```

when both are reachable within the same candle. The same OHLC can correspond to different intrabar paths.

Canonical distinction:

```text
INTRABAR EVENTS
    ORDER_TRIGGERED
    STOP_TOUCH
    TARGET_TOUCH

CANDLE-CLOSE EVENTS
    ORDER_FLOW_FAILED
    ORDER_BLOCK_FAILED
    VALID_BOS
    VALID_CHoCH
```

This does not establish chronological precedence among multiple intrabar events. Conflict resolution belongs to broker/execution implementation, lower-timeframe data, or tick data when available. The methodology layer must not invent a synthetic micro-sequence.

---

## 5.4 Risk / Structural Boundary Invariants — PASS / CLOSED

```text
RISK CONSUMES STRUCTURE
RISK DOES NOT CREATE STRUCTURE

POI INVALIDATION ≠ STRUCTURAL INVALIDATION
STRUCTURAL INVALIDATION ≠ RISK STOP
RISK STOP ≠ EXECUTION_STOPPED_OUT

TARGET_HIT ≠ VALID_BOS
VALID_CHoCH ↛ mandatory MARKET_CLOSE_ON_CHOCH
```

Risk configuration must not silently redefine canonical semantics.

---

## 5.5 Canonical Scoring — PASS / CLOSED

```text
Structure = 25%
Setup     = 30%
Location  = 20%
Liquidity = 15%
Risk      = 10%
```

```text
HIGH   >= 70
MEDIUM >= 55
LOW    >= 40
WATCH  < 40
```

```text
Real Major IDM     = 80
Fallback Major IDM = 40
```

```text
Retracement > 78.6% → -25
Retracement > 90.0% → -20
```

Scoring evaluates canonical structural state; it cannot create or validate structural objects.

---

# 5.6 Audit Closure

```text
5.1 Structural Stop-Loss Placement
    → PASS / CLOSED

5.2 Target Definition & Take-Profit Hierarchy
    → PASS / CLOSED

5.3 Invalidation & Kill-Switch Mechanics
    → PASS / CLOSED

5.4 Risk / Structural Boundary Invariants
    → PASS / CLOSED

5.5 Canonical Scoring
    → PASS / CLOSED
```

The risk module is closed as a downstream policy layer.

## Cross-Module G1 Implementation Boundary

The structural state machine may use canonical event-class detection/precedence, but that precedence is **classification precedence**, not intrabar temporal precedence.

```text
CANDLE-LEVEL EVENT PRECEDENCE
        ≠
INTRABAR EVENT CHRONOLOGY
```

The implementation must not claim to reconstruct the chronological order of multiple intrabar touches from OHLC alone.

```text
OHLC ≠ INTRABAR_SEQUENCE
```

**Cross-module status: ACCEPT WITH CLARIFICATION / CLOSED FOR METHODOLOGY**
