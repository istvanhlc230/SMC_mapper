# TRUE SMC — CANDLE-LEVEL FOUNDATION

**Role:** Canonical Layer 1 Candle-Level Foundation of the True SMC methodology.

**Authority:** Authoritative for raw OHLC interpretation and candle-level relationships. Candle relationships are observations and do not independently create higher-level structural objects.

## 1. Methodology boundary

True SMC is organized into three logical layers:

```text
TRUE SMC METHODOLOGY
│
├── 1. Candle-Level Foundation
├── 2. Minor Structure
└── 3. Structural Lifecycle
```

This document owns **Layer 1 — Candle-Level Foundation**.

The dependency boundary begins with raw OHLC and candle relationships. Higher-level structure is owned by the subsequent layers and must consume validated lower-level state.

```text
RAW OHLC
  ↓
CANDLE RELATIONSHIPS
  ↓
Layer 2 — Minor Structure
```

No higher-level event may be manufactured by configuration, scoring, visualization, or implementation convenience.

## 2. Foundational semantic non-equivalences

```text
CANDLE RELATIONSHIP       ≠ VALID PULLBACK
CANDLE RELATIONSHIP       ≠ STRUCTURALLY VALID PULLBACK
CANDLE RELATIONSHIP       ≠ IDM
CANDLE RELATIONSHIP       ≠ CONFIRMED SWING
CANDLE RELATIONSHIP       ≠ BOS
CANDLE RELATIONSHIP       ≠ CHoCH
LIQUIDITY                  ≠ STRUCTURE
CANDLE REVERSAL PATTERN   ≠ STRUCTURE
CANDLE REVERSAL PATTERN   ≠ IDM
CANDLE REVERSAL PATTERN   ≠ BOS
CANDLE REVERSAL PATTERN   ≠ CHoCH
CONFIGURATION              ≠ CANONICAL METHODOLOGY RULE
```

OHLC is raw market data. Candle-level relationships describe observations in that data; they are not automatically structural classifications.

## 3. Candle relationships

Candle relationships include, among others, HH/HL, LH/LL, EQH/EQL, inside-bar and outside-bar relationships. Their presence alone does not establish a Valid Pullback, SVP, IDM, swing, BOS, CHoCH, or Trading Range.

### 3.1 Equal High / Equal Low directional reference transfer

Equal High / Equal Low is a candle-level relationship. It participates in reference transfer only within the applicable directional candle context.

#### Bullish context

When two consecutive candles have equal highs:

1. The shared high forms the Equal High relationship.
2. The **second candle becomes the active reference**.
3. Price must subsequently break below the **second candle low**.
4. Price must then break above the **shared high**.
5. This completes the applicable candle-level Valid Pullback sequence.

#### Bearish context

When two consecutive candles have equal lows:

1. The shared low forms the Equal Low relationship.
2. The **second candle becomes the active reference**.
3. Price must subsequently break above the **second candle high**.
4. Price must then break below the **shared low**.
5. This completes the applicable candle-level Valid Pullback sequence.

Reference transfer is directional and belongs to candle-level Valid Pullback construction. It does not itself create a Structurally Valid Pullback, IDM, confirmed swing, BOS, or CHoCH.

### 3.2 Strict inside bar

A strict inside bar is:

```text
current.high < mother.high
AND
current.low  > mother.low
```

Equality does not count as a strict inside bar.

A strict inside bar does not independently create a Valid Pullback, Structurally Valid Pullback, IDM, confirmed swing, BOS, or CHoCH.

A break of an inside-bar relationship requires independent structural validation.

**Inside-bar sweep boundary:** An inside bar cannot independently establish a structural sweep or an independent liquidity extreme. Where an Order Block refinement later uses an inside-bar base, any liquidity sweep must be attributed to the **Mother Bar**, while the inside bar supplies only the refinement coordinate. This is an execution-layer refinement rule and does not promote the inside bar to a structural object.

### 3.3 Outside bar

A single outside bar must not activate both directional branches.

Canonical candle-level sequencing:

```text
Bullish outside-bar sequence = LOW → HIGH
Bearish outside-bar sequence = HIGH → LOW
```

Directional interpretation comes from the applicable context and sequence. The outside-bar relationship itself does not independently create higher-level structure.

## 4. Candlestick reversal-pattern observations

Candlestick reversal patterns are **candle-level observations used by the Execution Engine as confirmation/trigger inputs**. They never create, alter, confirm, or invalidate structural objects.

The canonical direct-entry catalog contains six formations:

1. Long Wick Rejection (Pinbar)
2. Multiple Wick Rejection
3. Engulfing (Outside-Bar Reversal)
4. Momentum Candle
5. Morning Star / Evening Star
6. Shrinking Candles

The execution eligibility, POI/liquidity gating, and order trigger are owned by `04_execution.md`. Layer 1 records only the candle anatomy and OHLC relationships required to identify the pattern observation.

### 4.1 Long Wick Rejection (Pinbar)

Morphology:

- small body relative to the candle's observed range;
- minimal opposite shadow;
- extended wick on the rejection side;
- the wick may penetrate a downstream execution reference such as a POI boundary or liquidity level.

Execution polarity is defined downstream by OHLC close/open:

```text
Bullish pattern polarity: Close > Open
Bearish pattern polarity: Close < Open
```

This execution polarity rule does **not** modify Layer-1 Valid Pullback semantics. Candle color/body direction remains irrelevant to structural Valid Pullback validation.

### 4.2 Multiple Wick Rejection

A Multiple Wick Rejection is a sequence of at least two consecutive candles whose rejection wicks penetrate the same **contextual execution zone** and then close without crossing the applicable execution-failure boundary.

The exact POI/liquidity-zone geometry is supplied by the Execution Engine; Layer 1 does not create or validate the zone.

For the final rejecting candle:

```text
Bullish execution polarity: Close > Open
Bearish execution polarity: Close < Open
```

The formation is an observation of repeated rejection/absorption. It is not itself a structural sweep, IDM, BOS, or CHoCH.

### 4.3 Engulfing (Outside-Bar Reversal)

For direct-entry classification, the canonical bullish and bearish engulfing relationships are:

#### Bullish Engulfing

```text
Low_t < Low_(t-1)
AND
Close_t > max(Open_(t-1), Close_(t-1))
AND
Close_t > Open_t
```

The lower wick sweep is mandatory. A body-only engulfing without the required sweep does not qualify as the canonical liquidity-sweeping engulfing pattern.

#### Bearish Engulfing

```text
High_t > High_(t-1)
AND
Close_t < min(Open_(t-1), Close_(t-1))
AND
Close_t < Open_t
```

The upper wick sweep is mandatory.

These are candle-level pattern relationships. They do not independently establish a structural sweep, IDM, BOS, or CHoCH.

### 4.4 Momentum Candle

A Momentum Candle is an immediate, above-average full-bodied expansion candle with minimal opposing wick, emerging directly from a downstream execution reference.

The terms **above-average**, **full-bodied**, and **minimal wick** remain qualitative because the authoritative source provides no discrete numeric threshold. They are therefore a **Qualitative Filter / SOURCE-PENDING** classification and are not an independent deterministic trigger.

No ATR, body-ratio, volatility, percentile, or other numerical threshold may be invented without authoritative validation.

### 4.5 Morning Star / Evening Star

The canonical three-candle observation is:

```text
t-2 = incoming trend candle
t-1 = small-bodied / indecision base candle
t   = reversal confirmation candle
```

The `t-1` small-body/indecision property is a **Qualitative Filter**, not a binary canonical gate. At binary level, the `t-1` candle must physically interact with the downstream POI or swept-liquidity reference supplied by the Execution Engine.

#### Bullish Morning Star

```text
Close_(t-2) < Open_(t-2)
Close_t > Open_t
Close_t > (Open_(t-2) + Close_(t-2)) / 2
```

#### Bearish Evening Star

```text
Close_(t-2) > Open_(t-2)
Close_t < Open_t
Close_t < (Open_(t-2) + Close_(t-2)) / 2
```

The midpoint is the arithmetic midpoint of Candle `t-2`'s body. The reversal candle's close beyond that midpoint is the deterministic confirmation condition.

### 4.6 Shrinking Candles

Shrinking Candles are a sequence showing progressive reduction in candle body size as price approaches a downstream execution reference.

They are a **Qualitative Filter / Approach Filter only**.

```text
SHRINKING CANDLES ≠ ENTRY TRIGGER
```

They may indicate momentum exhaustion but cannot independently authorize an entry or create any structural object.

## 5. Candle-level sweep observations

A wick penetration of an execution reference is an OHLC observation only. It becomes an execution-state event only when the downstream Execution Engine applies the relevant POI/liquidity definition and gating rules.

```text
WICK PENETRATION
      ↓
CANDLE-LEVEL OBSERVATION
      ↓
Execution Engine classification
```

Therefore:

```text
CANDLE WICK SWEEP ≠ IDM
CANDLE WICK SWEEP ≠ BOS
CANDLE WICK SWEEP ≠ CHoCH
```

The strict inside-bar rule remains unchanged: an inside bar cannot independently create a sweep or liquidity extreme.

## 6. Candle-Level Valid Pullback — Unit of Origin

The unit of origin for a candle-level Valid Pullback is a reference-candle relationship. Candle color and body size do not independently determine whether a sequence is valid.

A candle-level Valid Pullback is not created by a single reference-level breach. The complete directional sequence must be satisfied.

### 6.1 Bullish sequence

1. A valid reference high exists.
2. Price breaks the reference high.
3. Price subsequently breaches the reference low.
4. The breach may be wick or body.
5. Candle color is irrelevant.
6. Price subsequently breaks the relevant continuation/reference high.
7. The completed sequence establishes the candle-level Valid Pullback.

Do not reduce this to a previous-candle-low breach.

### 6.2 Bearish sequence

1. A valid reference low exists.
2. Price breaks the reference low.
3. Price subsequently breaches the reference high.
4. The breach may be wick or body.
5. Candle color is irrelevant.
6. Price subsequently breaks the relevant continuation/reference low.
7. The completed sequence establishes the candle-level Valid Pullback.

Do not reduce this to a previous-candle-high breach.

A candle-level Valid Pullback is only the Layer 1/2 origin object. It is not by itself a Structurally Valid Pullback, IDM, confirmed swing, BOS, CHoCH, or Trading Range transition.

## 7. Layer 1 validation contract

A compliant implementation must preserve all of the following:

- OHLC is raw data; candle relationships are observations.
- EQH/EQL reference transfer is directional and uses the second candle as the active reference.
- Strict inside bars require strict containment; equality does not qualify.
- A single outside bar cannot activate both directional branches.
- An inside bar cannot independently create a structural sweep or liquidity extreme.
- Candle-level Valid Pullback requires the complete directional sequence.
- Wick or body breach may satisfy the relevant candle-level breach; candle color does not independently determine validity.
- Candlestick reversal patterns are execution observations and do not manufacture structural truth.
- Qualitative candle morphology must not be silently converted into a deterministic numeric trigger.
- Candle-level relationships do not manufacture IDM, Confirmed Swing, BOS, CHoCH, or Trading Range.

## 8. Downstream boundary

The output of this layer is consumed by Layer 2 and by the Execution Engine only through the appropriate downstream interfaces:

```text
RAW OHLC
  ↓
CANDLE RELATIONSHIPS / REVERSAL OBSERVATIONS
  ↓
Layer 2 — Minor Structure

CANDLE REVERSAL OBSERVATION
  ↓
04 — EXECUTION GATING / CONFIRMATION
```

The semantic identity of Layer 1 objects must remain separate from later structural lifecycle and execution objects.
