# TRUE SMC — CANDLE-LEVEL FOUNDATION

**Role:** Canonical Layer 1 Candle-Level Foundation of the True SMC methodology.

**Authority:** This document owns the deterministic candle-level microstructure primitives and candle-level observations derived directly from OHLC. It does not own Sequential / Minor Pullback Formation, Macro Pullback Qualification, or Structural Lifecycle decisions.

## 1. Methodology boundary

The Candle-Level Foundation is the **Microstructure** layer. Microstructure describes deterministic OHLC relationships and emits candle-level observations/events.

**Candle-Level does not mean single-candle.** It means that the primitive observations are defined from candle OHLC relationships. A sequence composed from those observations belongs to the Sequential / Minor layer.

~~~
RAW OHLC
  ↓
CANDLE-LEVEL MICROSTRUCTURE
  ↓
SEQUENTIAL / MINOR STRUCTURE
  ↓
MACRO QUALIFICATION
  ↓
STRUCTURAL LIFECYCLE
~~~

Microstructure must not manufacture higher-level structural truth.

## 2. Canonical microstructure ontology

The canonical Layer 1 microstructure vocabulary is:

1. **Candle Extreme Breach**
2. **Candle Extreme Protection**
3. **Inside Bar**
4. **Outside Bar**
5. **Equal High (EQH)**
6. **Equal Low (EQL)**
7. **Equal Extreme Reference Transfer**
8. **Candle Internal Sequence**
9. **Candlestick-Based Trend**

These names are canonical. Other documents may reference them, but must not introduce competing names for the same objects.

## 3. Candle Extreme Breach

A Candle Extreme Breach occurs when the current candle exceeds a referenced candle extreme:

~~~
High_t > High_ref
OR
Low_t < Low_ref
~~~

The breach mode may be:

- **Wick Breach**
- **Body Breach**

The breach mode describes **how** the extreme was breached; it does not create a separate microstructure object.

~~~
Candle Extreme Breach
    ≠
STRUCTURAL_SWING_BREAK
    ≠
VALID_BOS
    ≠
CHoCH_ELIGIBLE
    ≠
IDM_TAKEN
~~~

Structural classification is downstream.

## 4. Candle Extreme Protection

**Candle Extreme Protection** records the applicable candle-level reference/protection relationship.

For a bullish candle-level directional sequence, the relevant low remains protected while the applicable high is breached. For a bearish candle-level directional sequence, the relevant high remains protected while the applicable low is breached. This is a candle-level OHLC relationship only; it does not establish structural protection.

It is a microstructure object and must remain distinct from:

~~~
Candle Extreme Protection
≠ Protected Structural Extreme
≠ CONFIRMED_STRUCTURAL_SWING
~~~

The latter objects belong to the Structural layer.

## 5. Inside Bar

A strict **Inside Bar** is:

~~~
current.high < mother.high
AND
current.low  > mother.low
~~~

Equality does not qualify as a strict Inside Bar.

Inside Bar is a valid candle relationship. It is not itself an invalid microstructure state.

~~~
Inside Bar
≠ Candle-Level Valid Pullback
≠ IDM
≠ VALID_BOS
≠ CHoCH_CONFIRMED
~~~

An Inside Bar does not independently establish a structural sweep or liquidity extreme.

## 6. Outside Bar

An **Outside Bar** satisfies:

~~~
current.high > reference.high
AND
current.low  < reference.low
~~~

The Outside Bar relationship and the internal order of the two breached extremes are separate observations.

The internal order is represented by **Candle Internal Sequence**:

~~~
LOW → HIGH
or
HIGH → LOW
~~~

A single Outside Bar must not be treated as two independent structural events merely because both extremes were breached.

## 7. Equal High (EQH) / Equal Low (EQL)

**Equal High (EQH)** and **Equal Low (EQL)** are candle-level relationships.

Canonical equality is exact unless an independently verified methodology tolerance is defined:

~~~
EQH:
High_a = High_b

EQL:
Low_a = Low_b
~~~

Do not invent a numerical tolerance and present it as canonical methodology.

EQH/EQL do not independently create IDM, Confirmed Structural Swing, VALID_BOS, or CHoCH.

## 8. Equal Extreme Reference Transfer

**Equal Extreme Reference Transfer** is the candle-level transfer of the active reference when the applicable equal-extreme relationship is formed.

For a bullish directional sequence:

~~~
Equal High relationship
        ↓
second candle becomes active reference
~~~

For a bearish directional sequence:

~~~
Equal Low relationship
        ↓
second candle becomes active reference
~~~

Reference transfer is still a microstructure/reference operation.

~~~
Equal Extreme Reference Transfer
≠ Pullback Formation
≠ Pullback Extreme
≠ Confirmed Structural Swing
~~~

The subsequent multi-event interpretation belongs to Sequential / Minor Structure.

## 9. Candle Internal Sequence

**Candle Internal Sequence** records the order in which relevant candle extremes are breached within the applicable candle relationship.

Canonical directional forms include:

~~~
LOW → HIGH
HIGH → LOW
~~~

This observation does not by itself establish EQH/EQL, Pullback Formation, IDM, BOS, or CHoCH.

Equal-extreme transfer occurs only when the required equal-extreme relationship also exists.

## 10. Candlestick-Based Trend

**Candlestick-Based Trend** describes candle-level directional relationships derived from OHLC. In the source-backed candle-level usage, a bullish directional sequence may be observed when the applicable previous candle high is breached while the relevant low remains protected; the bearish counterpart breaches the applicable previous candle low while the relevant high remains protected. This is a directional candle relationship, not a structural-trend classification.

It must remain distinct from structural trend:

~~~
Candlestick-Based Trend
≠ Structural Trend
≠ Trading Range
≠ Major Structure
~~~

Candle-level trend observations do not independently establish structural state.

## 11. Candlestick reversal observations

Candlestick reversal formations remain candle-level observations consumed by the Execution Engine. Layer 1 owns their candle anatomy and OHLC relationships; 04_execution.md owns execution eligibility, POI/liquidity gating, trigger timing, and entry authorization.

They do not create, alter, confirm, or invalidate structural objects.

The existing execution observation catalog remains:

1. Long Wick Rejection (Pinbar)
2. Multiple Wick Rejection
3. Engulfing (Outside-Bar Reversal)
4. Momentum Candle
5. Morning Star / Evening Star
6. Shrinking Candles

The qualitative terms used by these observations must not be silently converted into deterministic numeric methodology thresholds.

## 12. Microstructure output contract

The Layer 1 microstructure engine may emit deterministic candle-level observations such as:

~~~
CANDLE_EXTREME_BREACH
CANDLE_EXTREME_PROTECTION
INSIDE_BAR
OUTSIDE_BAR
EQH
EQL
EQUAL_EXTREME_REFERENCE_TRANSFER
CANDLE_INTERNAL_SEQUENCE
CANDLESTICK_BASED_TREND
~~~

The implementation may use equivalent internal event identifiers, but the semantic names above are canonical documentation names.

Microstructure output does **not** directly emit:

~~~
PULLBACK_FORMATION
CANDLE_LEVEL_VALID_PULLBACK
MACRO_PULLBACK_FORMATION
MACRO_VALID_PULLBACK
CONFIRMED_STRUCTURAL_SWING
IDM
VALID_BOS
CHoCH
ORDER BLOCK
ORDER FLOW
POI
RETRACEMENT DEPTH
DEALING RANGE
HTF SWING
ENTRY AUTHORIZATION
~~~

## 13. Explicit layer boundaries

The following ownership is mandatory:

~~~
MICRO / CANDLE-LEVEL
    ↓
Candle Extreme Breach
Candle Extreme Protection
Inside Bar
Outside Bar
Equal High (EQH)
Equal Low (EQL)
Equal Extreme Reference Transfer
Candle Internal Sequence
Candlestick-Based Trend

SEQUENTIAL / MINOR
    ↓
Engulfed Candle Sequence
Pullback Formation
Candle-Level Valid Pullback
Pullback Extreme
Minor structural sequence

MACRO
    ↓
Macro Pullback Formation
Macro Valid Pullback
Opposing-candle qualification
Significant / high-momentum qualitative qualification
Retracement Depth
38.2% / 50% depth qualification
HTF qualification

STRUCTURAL
    ↓
Confirmed Structural Swing
IDM
BOS
CHoCH
Protected Structural Extreme
Trading Range
~~~

The candle-count and significant/high-momentum qualification rules are therefore **not Microstructure rules**. They must not be inserted into this document as candle-level predicates.

## 14. Non-equivalences

~~~
Candle Extreme Breach ≠ STRUCTURAL_SWING_BREAK
Candle Extreme Breach ≠ VALID_BOS
Inside Bar ≠ Invalid Microstructure
Inside Bar ≠ Invalid Pullback
Outside Bar ≠ BOS
EQH/EQL ≠ IDM
Equal Extreme Reference Transfer ≠ Swing Formation
Candle Internal Sequence ≠ Pullback Formation
Candlestick-Based Trend ≠ Structural Trend
Candle-Level Valid Pullback ≠ Microstructure Primitive
Pullback Extreme ≠ Confirmed Structural Swing
~~~

## 15. Layer 1 validation contract

A compliant implementation must preserve:

- Microstructure is deterministic OHLC observation, not structural interpretation.
- Wick and body are breach modes of **Candle Extreme Breach**, not competing objects.
- Strict Inside Bar requires strict containment.
- Outside Bar records the two-sided extreme relationship; internal order is represented separately by **Candle Internal Sequence**.
- EQH/EQL use exact equality unless an authoritative tolerance is defined.
- Equal Extreme Reference Transfer transfers the active candle reference; it does not create a swing.
- Candle Internal Sequence records extreme order without manufacturing a pullback or structural event.
- Candlestick-Based Trend remains distinct from Structural Trend.
- Candle-level reversal observations remain execution observations and cannot manufacture structure.
- Pullback Formation and Candle-Level Valid Pullback are sequential constructs, not primitive Microstructure events.
- Macro candle-count, momentum, and retracement-depth qualification is outside Layer 1.
- Microstructure does not create IDM, Confirmed Structural Swing, VALID_BOS, CHoCH, POI, or Trading Range.

## 16. Downstream interface

~~~
RAW OHLC
  ↓
CANDLE-LEVEL MICROSTRUCTURE
  ↓
SEQUENTIAL / MINOR STRUCTURE
  ↓
MACRO QUALIFICATION
  ↓
STRUCTURAL LIFECYCLE

CANDLE REVERSAL OBSERVATION
  ↓
04 — EXECUTION GATING / CONFIRMATION
~~~

Layer 1 provides deterministic observations. Higher layers interpret those observations according to their own semantic ownership. No downstream structural rule may be retroactively encoded as a Microstructure predicate.
