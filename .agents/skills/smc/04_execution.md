# EXECUTION

**Role:** Trading/execution-layer rules built on validated structural facts.

**Boundary:** Execution consumes structure; execution must never manufacture structural truth.

## 36. POI ontology — canonical tradable POIs

The canonical POI ontology is a closed set. A tradable Point of Interest may be either **Valid Order Flow (OF)** or **Valid Order Block (OB)**. No third POI entity may be introduced by generic SMC convention or implementation convenience.

```text
VALID ORDER FLOW (OF)
VALID ORDER BLOCK (OB)
        ↓
   CANONICAL POI
```

The following are not canonical POI entities:

- standalone FVG / imbalance;
- Breaker Block;
- Mitigation Block;
- Liquidity Void;
- arbitrary liquidity pool;
- IDM;
- generic displacement zone.

These concepts may exist as structural observations, validators, liquidity, or historical annotations where separately defined, but they must not silently become tradable POIs.

### Rule of Two

For a canonical dealing range, there may be one or two tradable POIs:

```text
DECISIONAL POI
      +
EXTREME POI
```

Everything outside the active one-or-two-POI structure is non-tradable/SMT unless a canonical rule explicitly promotes it. Multiple arbitrary POIs must not be created merely because multiple zones are visually present.

### POI semantic separation

```text
IDM              ≠ POI
LIQUIDITY        ≠ POI
FVG              ≠ POI
DISPLACEMENT     ≠ POI
POI              ≠ ENTRY EXECUTION
```

A POI is a validated execution-location object. Its existence must never alter structural validation of IDM, swing, BOS, CHoCH, or Trading Range.

### POI and execution invariants

The following invariants are mandatory:

```text
POI ∈ {VALID_OF, VALID_OB}
STANDALONE_FVG → NOT_POI
IDM → NOT_POI
LIQUIDITY → NOT_POI
POI → NOT_STRUCTURE
POI → NOT_BOS
POI → NOT_CHoCH
POI → NOT_AUTOMATIC_ENTRY
FVG → OB_VALIDATOR_ONLY
```

A code path that violates these invariants is non-canonical even if its output appears visually plausible.

## 37. Decisional and Extreme POI

The canonical dealing-range POI model distinguishes the **Decisional POI** from the **Extreme POI**.

### Decisional POI

The Decisional POI is the primary execution location. Its directional location is mandatory:

```text
BUY → POI must be in DISCOUNT
      normalized location < 0.50

SELL → POI must be in PREMIUM
       normalized location > 0.50
```

A Decisional POI outside its required premium/discount side is not a valid Decisional POI and must not be promoted to a canonical entry merely because the underlying zone is otherwise valid.

### Extreme POI

The Extreme POI is the secondary/fallback execution location of the same dealing-range framework. It is used when the Decisional POI is unavailable, fails its execution conditions, or is otherwise not the applicable module according to the canonical entry sequence.

The Extreme POI must still be a Valid OF or Valid OB. It is not an arbitrary fallback to any visually convenient zone.

### Origin OB

An Origin OB is a canonical absolute range-origin Order Block. It is not required to disappear merely because its parent Valid Order Flow has been mitigated. Its validity must be evaluated according to the OB validation rules rather than by inheritance from the current OF state.

## 38. Order Block validation

A candle/zone may be treated as a Valid Order Block only when the canonical three-pillar validation is satisfied.

```text
PILLAR 1
Origin of impulsive displacement that causes structural BOS
        +
PILLAR 2
Candle sweeps previous candle's extreme
        +
PILLAR 3
Active, fully unmitigated FVG/imbalance adjacent to the candle
        ↓
VALID ORDER BLOCK
        ↓
POI ELIGIBILITY
```

All three pillars are required. A visually strong candle, displacement alone, or an FVG alone must not create an OB.

The structural BOS referenced by Pillar 1 must be independently canonical. An implementation must not manufacture BOS merely to validate an OB.

### Valid Order Flow

Valid OF is a canonical POI class distinct from OB. OF and OB must not be conflated into a single generic zone type merely for implementation convenience.

### OB mitigation

Mitigation changes execution eligibility; it does not rewrite historical structural meaning. A mitigated OF does not automatically invalidate a separately valid Origin OB. A failed Decisional POI does not authorize arbitrary zone substitution; the canonical Extreme POI must be used when its own validity conditions are satisfied.

### OB refinement — Wick-Only and Inside-Bar bases

Refinement narrows the execution geometry of an already qualified Order Block. Refinement does **not** replace or relax the canonical three-pillar OB validation.

#### Long-wick / Pinbar base — Wick-Only OB

Where the qualified base candle contains an extended wick that performs the preceding liquidity sweep, the refined Order Block is limited to the sweeping wick region between the swept extreme and the candle body boundary.

Bullish / Demand:

```text
OB_bottom = Low_base
OB_top    = max(Open_base, Close_base)
```

Bearish / Supply:

```text
OB_top    = High_base
OB_bottom = min(Open_base, Close_base)
```

This refinement does not create a sweep, IDM, BOS, CHoCH, or any other structural event.

#### Inside-Bar base

If the base candle is a strict inside bar, the **Mother Bar** performs the liquidity sweep. The inside bar does not independently sweep liquidity or create a structural extreme. The canonical refined geometry is:

Bullish / Demand:

```text
OB_bottom = Low_(t-1)   # Mother Bar Low
OB_top    = Low_t       # Inside Bar Low
```

Bearish / Supply:

```text
OB_top    = High_(t-1)  # Mother Bar High
OB_bottom = High_t      # Inside Bar High
```

No alternative geometry such as an unspecified “sweeping wick range” is permitted. The inside-bar refinement is an execution-coordinate refinement only.

## 39. FVG / imbalance ontology

FVG exists in the canonical methodology, but it is **strictly a validator/property and never a standalone tradable POI**.

```text
FVG
 ↓
OB VALIDATION
 ↓
VALID OB
 ↓
POI
 ↓
ENTRY MODULE
```

The following are forbidden semantic shortcuts:

```text
FVG → POI
FVG → ENTRY
FVG TOUCH → ENTRY
FVG BREAK → BOS
FVG → CHoCH
```

A standalone FVG must not:

- create a tradable zone;
- create an entry signal;
- create a limit order;
- create or invalidate a POI;
- confirm a structural swing;
- create BOS or CHoCH.

An FVG may participate as Pillar 3 of OB validation. It remains ontologically distinct from IDM, liquidity, POI, and execution.

## 40. Canonical entry modules

The canonical execution layer contains four entry modules:

1. **IDM Sweep**
2. **Decisional POI Mitigation**
3. **Engineering Liquidity Sweep**
4. **Extreme POI Mitigation**

These are execution mechanisms, not alternative definitions of market structure. An entry module may consume canonical structural state, liquidity state, and validated POI state, but it must never manufacture IDM, BOS, CHoCH, or a Trading Range.

### Module 1 — IDM Sweep

The IDM Sweep module requires a canonically active IDM and its qualifying liquidity interaction. IDM sweep remains a liquidity/execution event and is not itself BOS or CHoCH.

### Module 2 — Decisional POI Mitigation

The Decisional POI must be a valid OF or OB, must satisfy the directional premium/discount gate, and must meet the independent execution conditions of the module. POI mitigation does not create structural validity.

### Module 3 — Engineering Liquidity Sweep

Engineering liquidity is an execution-layer liquidity event. It must not be promoted to structural liquidity, IDM, BOS, or CHoCH merely because price sweeps the engineered level.

### Module 4 — Extreme POI Mitigation

The Extreme POI module is the canonical fallback execution mechanism when the Decisional POI is not the applicable execution location. The Extreme POI must independently satisfy OF/OB validity; fallback execution does not relax POI validation.

## 40.5. Candlestick Reversal Triggers

Candlestick reversal patterns are **execution confirmation/trigger objects only**. They are downstream consumers of structural and execution eligibility and have zero structural authority.

### Architectural gate

A candlestick reversal pattern may authorize a direct entry only when an existing canonical execution route is already eligible:

```text
DIRECT CANDLE ENTRY ELIGIBILITY
        ↓
    (POI MITIGATION)
          OR
    (CORE LIQUIDITY SWEEP)
        ↓
CANDLE REVERSAL CONFIRMATION
        ↓
CANDLE CLOSE
        ↓
DIRECT ENTRY
```

Eligible key areas are:

- mitigation of a qualified **Decisional or Extreme Valid OF/OB**;
- a direct sweep of active **IDM**;
- a direct sweep of **Engineering Liquidity (ENG_LQD)**.

A standalone/unbacked FVG is not an eligible direct-entry location.

The candlestick pattern does not create the POI, IDM, ENG_LQD, or any structural condition. It only confirms an already eligible execution context.

### Close-only execution

Entry is permitted only on the **close of the completed pattern candle**.

```text
LIVE / UNCLOSED WICK → NO ENTRY
COMPLETED CANDLE CLOSE → ENTRY EVALUATION
```

A live wick cannot trigger a direct candle-pattern entry.

### Canonical pattern catalog

#### 1. Long Wick Rejection / Pinbar

Morphology:

- small body;
- minimal opposite shadow;
- extended rejection wick penetrating the eligible POI or sweeping the eligible liquidity reference.

Bullish direct-entry polarity:

```text
Close > Open
```

The bullish entry is evaluated at candle close. If `Close <= Open`, the bullish pattern does not qualify; a subsequent bullish close is required.

Bearish direct-entry polarity:

```text
Close < Open
```

If `Close >= Open`, the bearish pattern does not qualify; a subsequent bearish close is required.

#### 2. Multiple Wick Rejection

Two or more consecutive candles must penetrate the same eligible POI zone or swept-liquidity context and close without crossing the applicable execution-failure boundary.

For a bullish context:

```text
Low_(t-1) <= POI_top
Low_t     <= POI_top
Close_(t-1) >= POI_bottom
Close_t     >= POI_bottom
Close_t > Open_t
```

For a bearish context:

```text
High_(t-1) >= POI_bottom
High_t     >= POI_bottom
Close_(t-1) <= POI_top
Close_t     <= POI_top
Close_t < Open_t
```

No external tick-level tolerance is introduced. The previously validated POI geometry is authoritative.

The trigger is the close of the second or later rejecting candle that satisfies the directional close condition.

#### 3. Engulfing / Outside-Bar Reversal

Bullish:

```text
Low_t < Low_(t-1)
AND
Close_t > max(Open_(t-1), Close_(t-1))
AND
Close_t > Open_t
```

Bearish:

```text
High_t > High_(t-1)
AND
Close_t < min(Open_(t-1), Close_(t-1))
AND
Close_t < Open_t
```

The wick sweep is mandatory. A body-only engulfing without the required sweep is not the canonical direct-entry trigger.

#### 4. Momentum Candle

A Momentum Candle is an immediate, above-average full-bodied expansion candle with minimal opposing wick emerging from an eligible execution reference.

Because the authoritative source provides no discrete numerical definition for “above-average” or “minimal wick”, this remains a **Qualitative Filter / SOURCE-PENDING** classification and is not an independent binary trigger.

#### 5. Morning Star / Evening Star

Three-candle sequence:

```text
t-2 = incoming trend candle
t-1 = small-bodied / indecision base in the eligible area
t   = reversal confirmation candle
```

The `t-1` small-body/indecision morphology is a **Qualitative Filter**, not a binary gate. At binary level, Candle `t-1` must physically interact with the eligible POI or swept-liquidity reference.

Bullish Morning Star:

```text
Close_(t-2) < Open_(t-2)
Close_t > Open_t
Close_t > (Open_(t-2) + Close_(t-2)) / 2
```

Bearish Evening Star:

```text
Close_(t-2) > Open_(t-2)
Close_t < Open_t
Close_t < (Open_(t-2) + Close_(t-2)) / 2
```

Entry is evaluated at the close of Candle `t`.

#### 6. Shrinking Candles

Progressive reduction in candle body size while approaching the eligible POI or liquidity reference is an **Approach Filter only**.

```text
SHRINKING CANDLES ≠ ENTRY TRIGGER
```

It cannot independently authorize a direct entry.

### Pattern non-equivalences

```text
CANDLE_PATTERN       ≠ POI
CANDLE_PATTERN       ≠ IDM
CANDLE_PATTERN       ≠ ENG_LQD
CANDLE_PATTERN       ≠ SWING
CANDLE_PATTERN       ≠ BOS
CANDLE_PATTERN       ≠ CHoCH
CANDLE_PATTERN       ≠ TRADING_RANGE
CANDLE_PATTERN       ≠ STRUCTURAL_INVALIDATION
CANDLE_PATTERN       ≠ POI_CREATION
```

The candlestick trigger therefore follows this dependency:

```text
CANONICAL STRUCTURAL / EXECUTION ELIGIBILITY
        ↓
ELIGIBLE POI OR CORE LIQUIDITY CONTEXT
        ↓
CANDLE PATTERN OBSERVATION
        ↓
COMPLETED CANDLE CLOSE
        ↓
EXECUTION TRIGGER
```

It never runs in the reverse direction.

## 41. Execution, structural validation, and risk

Execution priority and structural validation are separate domains.

```text
EXECUTION PRIORITY ≠ STRUCTURAL VALIDATION
ORDER FLOW FAILED ≠ BOS
ORDER FLOW FAILED ≠ CHoCH
POI FAILURE ≠ STRUCTURAL FAILURE
```

A failed execution condition must not be converted into a structural event. Likewise, a structurally valid event does not automatically authorize execution.

### Order Flow failure / Extreme fallback

Do not fail over from Valid OF to Extreme OB solely because price wicked into or through the OF. The exact failure condition must be independently satisfied by the canonical execution module. A wick touch alone is insufficient to invent an execution-state transition.

### Risk and RR

A canonical executable setup must satisfy a minimum risk/reward of **1:2**. The primary target is the confirmed external range extreme where the applicable entry module requires it. Risk management must consume structural state; it must not redefine structure.
