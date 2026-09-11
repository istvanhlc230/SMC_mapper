# RISK

**Role:** Risk, scoring, position-sizing, and trade-management policy.

**Authority boundary:** Risk and scoring are downstream policy layers, not structural truth. They consume canonical structural state and cannot create or validate it.

## 41. Execution, structural validation, and risk

Execution priority and structural validation are separate domains.

```text
EXECUTION PRIORITY ≠ STRUCTURAL VALIDATION
ORDER FLOW FAILED ≠ BOS
ORDER FLOW FAILED ≠ CHoCH
POI FAILURE ≠ STRUCTURAL FAILURE
EXECUTION STOP-OUT ≠ ORDER_FLOW_FAILED
EXECUTION STOP-OUT ≠ VALID_CHoCH
```

A failed execution condition must not be converted into a structural event. Likewise, a structurally valid event does not automatically authorize execution.

## 44. Scoring

Existing scoring weights:

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

Scoring evaluates canonical structural state. Scoring must never create or validate structure.

## Risk/reward

A canonical executable setup must satisfy a minimum risk/reward of **1:2** where required by the canonical execution layer. Risk management consumes structural state; it must not redefine structure.

## 5.1 Structural Stop-Loss Placement

Risk provides two distinct stop-loss tiers for execution. Neither tier creates, confirms, or invalidates structural objects.

```text
TIER 1 — MACRO / ZONE INVALIDATION STOP
TIER 2 — REFINED PATTERN EXTREME STOP
```

### Tier 1 — Macro / Zone Invalidation SL

The conservative stop is placed beyond the furthest boundary of the **parent Valid Order Flow / Valid Order Block** that authorizes the execution.

```text
Tier-1 SL
    ↓
beyond parent OF/OB furthest boundary
```

Tier 1 is the canonical conservative zone-invalidation stop. Its execution is a risk/position-management event and must not be reinterpreted as automatic `ORDER_FLOW_FAILED`, BOS, CHoCH, IDM, or structural invalidation.

### Tier 2 — Refined Pattern Extreme SL

Tier 2 is an **optional strategy/risk-management choice** available only when entry was triggered by a confirmed close of a canonical candlestick reversal pattern that has a deterministic execution trigger.

It is not available for a direct limit entry without candlestick reversal confirmation, and it cannot be independently authorized by a qualitative-only filter.

Entry is the close of the completed reversal-pattern candle/sequence.

For a bullish entry:

```text
SL = min(Low_pattern_candles) - P
```

For a bearish entry:

```text
SL = max(High_pattern_candles) + P
```

The pattern-extreme stop is intended as an aggressive/refined risk option that may improve R:R by reducing stop distance. It does not replace the parent POI/OF/OB geometry as a structural definition.

### Tier-2 stop-out semantics

A Tier-2 stop-out is an execution/risk event only:

```text
Price <= Tier-2 bullish SL
OR
Price >= Tier-2 bearish SL
        ↓
EXECUTION_STOPPED_OUT
```

`EXECUTION_STOPPED_OUT` is not equivalent to:

```text
ORDER_FLOW_FAILED
ORDER_BLOCK_FAILED
VALID_BOS
VALID_CHoCH
STRUCTURAL_INVALIDATION
```

The position may be stopped while the parent POI and macro structure remain structurally valid, including where price remains within the Tier-1 parent-zone boundary.

### Pattern-scope rule

Tier 2 may be used only when a direct entry was actually triggered by a deterministic canonical reversal pattern defined in `04_execution.md`:

```text
Long Wick Rejection
Multiple Wick Rejection
Engulfing
Morning / Evening Star
```

`Momentum Candle` remains a Qualitative Filter / SOURCE-PENDING classification and is not an independent binary trigger. `Shrinking Candles` is an approach filter and not an entry trigger. Neither can independently authorize Tier 2.

### Spread buffer P

`P` is a **SOURCE-PENDING / DOWNSTREAM CONFIG VARIABLE**.

The True SMC methodology does not define a universal pip/tick value for `P`. The canonical rule is only that the Tier-2 stop is placed beyond the relevant pattern extreme by the configured downstream buffer.

```text
P ∈ downstream risk/execution configuration
P ≠ structural methodology constant
```

No default such as `Spread + Minimum Tick` is canonicalized without authoritative validation.

## Critical separation

```text
POI INVALIDATION
        ≠
STRUCTURAL INVALIDATION
        ≠
RISK STOP
        ≠
EXECUTION_STOPPED_OUT
```

A risk stop cannot manufacture or confirm structural events.

## Risk boundaries

- Scoring evaluates canonical structural state.
- Position sizing must not validate or invalidate structural objects.
- Risk management must consume structural state rather than redefine it.
- Configuration switches must not silently redefine canonical semantics.
- Risk policy is downstream from structural validation.
- The Tier-2 pattern stop is an optional execution/risk optimization, not a structural rule.
