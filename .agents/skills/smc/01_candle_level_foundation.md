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

### 3.3 Outside bar

A single outside bar must not activate both directional branches.

Canonical candle-level sequencing:

```text
Bullish outside-bar sequence = LOW → HIGH
Bearish outside-bar sequence = HIGH → LOW
```

Directional interpretation comes from the applicable context and sequence. The outside-bar relationship itself does not independently create higher-level structure.

## 4. Candle-Level Valid Pullback — Unit of Origin

The unit of origin for a candle-level Valid Pullback is a reference-candle relationship. Candle color and body size do not independently determine whether a sequence is valid.

A candle-level Valid Pullback is not created by a single reference-level breach. The complete directional sequence must be satisfied.

### 4.1 Bullish sequence

1. A valid reference high exists.
2. Price breaks the reference high.
3. Price subsequently breaches the reference low.
4. The breach may be wick or body.
5. Candle color is irrelevant.
6. Price subsequently breaks the relevant continuation/reference high.
7. The completed sequence establishes the candle-level Valid Pullback.

Do not reduce this to a previous-candle-low breach.

### 4.2 Bearish sequence

1. A valid reference low exists.
2. Price breaks the reference low.
3. Price subsequently breaches the reference high.
4. The breach may be wick or body.
5. Candle color is irrelevant.
6. Price subsequently breaks the relevant continuation/reference low.
7. The completed sequence establishes the candle-level Valid Pullback.

Do not reduce this to a previous-candle-high breach.

A candle-level Valid Pullback is only the Layer 1/2 origin object. It is not by itself a Structurally Valid Pullback, IDM, confirmed swing, BOS, CHoCH, or Trading Range transition.

## 5. Layer 1 validation contract

A compliant implementation must preserve all of the following:

- OHLC is raw data; candle relationships are observations.
- EQH/EQL reference transfer is directional and uses the second candle as the active reference.
- Strict inside bars require strict containment; equality does not qualify.
- A single outside bar cannot activate both directional branches.
- Candle-level Valid Pullback requires the complete directional sequence.
- Wick or body breach may satisfy the relevant candle-level breach; candle color does not independently determine validity.
- Candle-level relationships do not manufacture IDM, Confirmed Swing, BOS, CHoCH, or Trading Range.

## 6. Downstream boundary

The output of this layer is consumed by Layer 2:

```text
RAW OHLC
  ↓
CANDLE RELATIONSHIPS
  ↓
CANDLE-LEVEL VALID PULLBACK
  ↓
Layer 2 — Minor Structure
```

The semantic identity of Layer 1 objects must remain separate from later structural lifecycle objects.
