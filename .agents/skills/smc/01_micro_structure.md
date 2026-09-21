# TRUE SMC — MICRO STRUCTURE

**Role:** Canonical Layer 1 Candle-Level Foundation of the True SMC methodology.

**Authority:** This document owns deterministic candle-level microstructure primitives and candle-level observations derived directly from OHLC. Sequential / Minor Structure, structural qualification, BOS, CHoCH, and execution decisions are defined by their respective owner documents.

## 1. Methodology boundary

The Candle-Level Foundation is the **Microstructure** layer. Microstructure defines deterministic OHLC relationships and emits candle-level observations.

**Candle-Level does not mean single-candle.** It means that the primitive observations are defined from candle OHLC relationships. Sequences composed from those observations are interpreted by the Sequential / Minor layer.

~~~
RAW OHLC
  ↓
CANDLE-LEVEL MICROSTRUCTURE
  ↓
SEQUENTIAL / MINOR STRUCTURE
  ↓
STRUCTURAL QUALIFICATION
  ↓
STRUCTURAL LIFECYCLE
~~~

## 2. Canonical microstructure ontology

The canonical Layer 1 vocabulary is:

1. **Candle Extreme Breach**
2. **Candle Extreme Protection**
3. **Inside Bar**
4. **Outside Bar**
5. **Equal High (EQH)**
6. **Equal Low (EQL)**
7. **Equal Extreme Reference Transfer**
8. **Candle Internal Sequence**
9. **Candlestick-Based Trend**

These names are canonical. Downstream documents reference these objects by these semantic names.

## 3. Candle Extreme Breach

A **Candle Extreme Breach** is classified against an applicable reference extreme using four deterministic levels:

~~~
1. PHYSICAL_BREACH
   H_t > H_ref OR L_t < L_ref

2. WICK_ONLY_BREACH
   Up: H_t > H_ref AND max(O_t, C_t) <= H_ref
   Down: L_t < L_ref AND min(O_t, C_t) >= L_ref

3. BODY_BREACH
   Up: max(O_t, C_t) > H_ref
   Down: min(O_t, C_t) < L_ref

4. CLOSE_BREACH
   Up: C_t > H_ref
   Down: C_t < L_ref
~~~

The classifications are relations of the completed candle's OHLC values. Candle color is irrelevant.

The ontology is nested:

~~~
CLOSE_BREACH ⊂ BODY_BREACH ⊂ PHYSICAL_BREACH
~~~

A Body Breach is a static body-endpoint/range relation. Historical intrabar crossing requires independent sequence evidence. A gap may satisfy BODY_BREACH without exposing an intrabar crossing path.

## 4. Candle Extreme Protection

**Candle Extreme Protection** records the candle-level protection relationship used by the Candlestick-Based Trend model.

For a bullish candle-level directional sequence, the relevant low is protected while the applicable high is breached. For a bearish candle-level directional sequence, the relevant high is protected while the applicable low is breached.

The applicable reference and trend context are supplied by the candle-level sequence. Downstream structural layers use their own structural protection definitions.

## 5. Inside Bar

A strict **Inside Bar** is:

~~~
current.high < mother.high
AND
current.low  > mother.low
~~~

Equality does not qualify.

The **mother candle** is the governing reference for the Inside Bar relationship. When an Inside Bar occurs inside a downstream sequence, the mother-candle reference remains the applicable candle-level reference unless a later owner-layer rule explicitly establishes a new reference.

Inside Bar is a candle-level relationship. Its definition ends at strict containment and reference identity.

## 6. Outside Bar

An **Outside Bar** is a candle-level geometric relationship against an applicable reference candle:

~~~
OUTSIDE_BAR(C_t, C_ref)
⇔
H_t > H_ref
AND
L_t < L_ref
~~~

The applicable reference candle is established by the governing candle-level context.

Outside Bar is a canonical candle-geometry observation that can be consumed by downstream sequence and execution owners. Layer 2 may use the observation as an input to Candle-Level Pullback formation, while Layer 6 may use it as an input to its own reversal predicate.

The order in which the two breached extremes were reached is represented separately by Candle Internal Sequence when evidence is available.

## 7. Equal High (EQH) / Equal Low (EQL)

**Equal High (EQH)** and **Equal Low (EQL)** are exact candle-level equality relationships:

~~~
EQH(C_a, C_b) ⇔ High_a = High_b
EQL(C_a, C_b) ⇔ Low_a  = Low_b
~~~

No numerical tolerance is canonical unless independently established and approved as methodology.

## 8. Equal Extreme Reference Transfer

**Equal Extreme Reference Transfer** separates geometric equality from reference identity.

The canonical sequence is:

~~~
CANDIDATE EQUALITY
      ↓
EQH / EQL RELATIONSHIP CONFIRMED
      ↓
REFERENCE IDENTITY TRANSFER
~~~

The implementation maintains independent high and low reference identities:

~~~
ActiveHighReference = (price_value, candle_id, role)
ActiveLowReference  = (price_value, candle_id, role)
~~~

When an EQH relationship is confirmed, the current candle becomes the active high reference. When an EQL relationship is confirmed, the current candle becomes the active low reference.

~~~
IF EQH(C_t, ActiveHighReference)
→ ActiveHighReference ← (H_t, candle_id_t, ACTIVE_HIGH)

IF EQL(C_t, ActiveLowReference)
→ ActiveLowReference ← (L_t, candle_id_t, ACTIVE_LOW)
~~~

High-reference and low-reference transfers are independent.

Protection state is maintained separately through the Candlestick-Based Trend context:

~~~
CandleTrendState = Uptrend
    → Low is protected

CandleTrendState = Downtrend
    → High is protected
~~~

## 9. Candle Internal Sequence

**Candle Internal Sequence** is the methodology model for the order in which relevant candle extremes are reached.

~~~
Bullish candle model:
OPEN → LOW → HIGH → CLOSE
(OLHC)

Bearish candle model:
OPEN → HIGH → LOW → CLOSE
(OHLC)
~~~

These are methodology formation models. They do not establish historical observability for a specific aggregate OHLC candle.

For an Outside Bar, the geometric relationship and the intrabar order are represented as separate observations. When aggregate OHLC does not expose the intrabar path, the sequence remains unavailable at the historical-observation level.

## 10. Candlestick-Based Trend

**Candlestick-Based Trend** describes candle-level directional relationships derived from OHLC.

Bullish candle-level trend:

~~~
applicable previous bullish-candle high is breached
WHILE
the relevant low remains protected
~~~

Bearish candle-level trend:

~~~
applicable previous bearish-candle low is breached
WHILE
the relevant high remains protected
~~~

The sequence continues until the opposing candle-level condition that starts a pullback is observed. The Sequential / Minor layer interprets that transition as part of Pullback Formation.

## 11. Methodology semantics and historical observability

**Methodology semantics do not imply historical observability.**

Layer 1 records the canonical OLHC/OHLC methodology model. Implementation observability states belong to 08_implementation.md and the executable data model.

~~~
CANONICAL METHODOLOGY
        ≠
HISTORICALLY OBSERVED INTRABAR PATH
~~~

The implementation-level evidence states are:

- OBSERVED — verified by lower-timeframe, tick, or replay evidence;
- METHODOLOGY_ASSUMED — the True SMC theoretical OLHC/OHLC formation model;
- UNAVAILABLE — aggregate OHLC does not expose the sequence.

~~~
METHODOLOGY_ASSUMED
MUST NOT
be represented as OBSERVED
~~~

~~~
UNAVAILABLE
MUST NOT
be silently promoted to OBSERVED
~~~

## 12. Downstream ownership

Layer 1 provides the following canonical observations:

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

Downstream ownership is:

~~~
01 MICRO
  ↓
candle relationships and observations

02 MINOR
  ↓
pullback formation and minor IDM eligibility

03 STRUCTURAL
  ↓
major qualification and structural lifecycle

04 BOS
  ↓
detailed BOS mechanics using Layer 3 qualification

05 CHOCH
  ↓
detailed CHoCH mechanics using Layer 3 lifecycle

06 EXECUTION
  ↓
reversal and execution-pattern semantics
~~~

## 13. Layer 1 validation contract

A compliant implementation preserves:

- deterministic OHLC-based candle observations;
- strict Inside Bar containment;
- mother-candle reference identity for Inside Bar;
- Outside Bar geometric expansion beyond both applicable extremes;
- exact EQH/EQL equality unless an approved tolerance exists;
- independent high and low reference identities;
- OLHC/OHLC as the canonical methodology formation models;
- explicit separation between methodology sequence and historical sequence evidence;
- Candlestick-Based Trend as a candle-level directional observation;
- downstream semantic ownership outside Layer 1.

## 14. Downstream interface

~~~
RAW OHLC
  ↓
CANDLE-LEVEL MICROSTRUCTURE
  ↓
SEQUENTIAL / MINOR STRUCTURE
  ↓
STRUCTURAL QUALIFICATION
  ↓
STRUCTURAL LIFECYCLE
~~~

Layer 1 supplies deterministic observations. Downstream layers define the sequence, qualification, lifecycle, and execution semantics that consume those observations.
