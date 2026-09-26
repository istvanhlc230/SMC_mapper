# TRUE SMC — MINOR STRUCTURE

**Role:** Canonical Layer 2 Minor Structure of the True SMC methodology.

**Authority:** This document owns Sequential / Minor Structure, including Pullback Formation, Candle-Level Valid Pullback, verified pullback extremes, active pullback state, and pullback-derived liquidity references for the active minor leg. Candle-level primitives consumed by this layer are owned by 01_micro_structure.md.

Major structural qualification is owned by 03_structural_semantic_authority.md.

## 1. Methodology boundary

Layer 2 consumes the canonical Layer 1 candle observations and assembles them into sequential/minor-structure events.

~~~
LAYER 1 CANDLE OBSERVATIONS
        ↓
CANDLE-LEVEL VALID PULLBACK
        ↓
VERIFIED PULLBACK EXTREME
        ↓
PULLBACK-DERIVED LIQUIDITY REFERENCE
        ↓
LAYER 3 IDM CLASSIFICATION
        ↓
ACTIVE IDM
        ↓
IDM_TAKEN
        ↓
CONFIRMED_STRUCTURAL_SWING
        ↓
LAYER 3 STRUCTURAL RETRACEMENT QUALIFICATION
        ↓
STRUCTURAL_SWING_BREAK
        ↓
VALID_BOS
~~~

Each downstream state is produced only from the validated prerequisite state supplied by the preceding stage.

## 2. Candle-Level Valid Pullback

A **Candle-Level Valid Pullback** is a completed sequential candle-level event within an established Candlestick-Based Trend.

The pullback is defined by the ordered use of the applicable reference candle from the Layer 1 candle sequence.

### 2.1 Bullish Candle-Level Valid Pullback

In a bullish Candlestick-Based Trend:

1. The applicable reference is the active bullish-side high reference established by the Layer 1 candle sequence. A bullish continuation establishes the reference candle; Layer 1 Equal Extreme Reference Transfer may move that high reference to the later candle when EQH is confirmed.
2. The pullback begins when price takes out that reference candle's low through a canonical Layer 1 Candle Extreme Breach.
3. The breach may occur through a wick or candle body. The Layer 1 breach classification is consumed rather than redefined here.
4. The candle that performs the breach may be bullish or bearish.
5. Price then reverses in the prevailing bullish direction.
6. The pullback completes when price breaks above the high of the same reference candle.
7. The lowest price reached from pullback start until completion is the Pullback Low.
8. The sequence may contain one candle or multiple candles.

~~~
BULLISH CANDLE-LEVEL VALID PULLBACK

reference bullish candle
        ↓
take reference LOW
        ↓
pullback begins
        ↓
prevailing-direction reversal
        ↓
break reference HIGH
        ↓
Pullback Low = lowest point reached
~~~

### 2.2 Bearish Candle-Level Valid Pullback

In a bearish Candlestick-Based Trend:

1. The applicable reference is the active bearish-side low reference established by the Layer 1 candle sequence. A bearish continuation establishes the reference candle; Layer 1 Equal Extreme Reference Transfer may move that low reference to the later candle when EQL is confirmed.
2. The pullback begins when price takes out that reference candle's high through a canonical Layer 1 Candle Extreme Breach.
3. The breach may occur through a wick or candle body.
4. The candle that performs the breach may be bullish or bearish.
5. Price then reverses in the prevailing bearish direction.
6. The pullback completes when price breaks below the low of the same reference candle.
7. The highest price reached from pullback start until completion is the Pullback High.
8. The sequence may contain one candle or multiple candles.

~~~
BEARISH CANDLE-LEVEL VALID PULLBACK

reference bearish candle
        ↓
take reference HIGH
        ↓
pullback begins
        ↓
prevailing-direction reversal
        ↓
break reference LOW
        ↓
Pullback High = highest point reached
~~~

### 2.3 Candle color and sequence length

The candle performing the opposing-side breach does not need to match the direction of the pullback. Candle color is therefore not a validity discriminator for the breach candle.

The pullback may complete after one candle or after multiple candles. No candle-count threshold is part of the Candle-Level Valid Pullback definition.

### 2.4 Inside Bar reference handling

When a Layer 1 INSIDE_BAR occurs during pullback formation, the mother candle remains the applicable candle-level reference according to the Layer 1 definition.

The inner candle does not replace the applicable reference. Pullback evaluation continues against the mother-candle context.

When Equal High / Equal Low reference identity is transferred to a later candle, that transfer candle establishes the new reference; its own newly established reference extreme is not simultaneously treated as taken. Pullback takeout evaluation begins on the following candle.

## 3. Outside Bar consumption

Layer 2 may consume a Layer 1 OUTSIDE_BAR observation as part of Candle-Level Valid Pullback formation.

An Outside Bar can participate in pullback formation when its breached extremes occur within the applicable directional sequence and satisfy the pullback's canonical start, reversal, and completion conditions. The pullback remains an ordered event: one side is taken and the corresponding reference side is later broken after reversal.

~~~
OUTSIDE_BAR
    ↓
APPLICABLE CANDLE SEQUENCE
    ↓
CANDLE-LEVEL PULLBACK FORMATION
~~~

When aggregate OHLC does not expose the intrabar order needed by the sequence, Layer 2 uses the observability state provided by Layer 1 instead of manufacturing historical path evidence.

For an Outside Bar ordering that is unavailable at the point required to establish or complete the pullback sequence, Layer 2 terminally invalidates that specific candidate. The candidate is not promoted to PENDING_UNAVAILABLE_SEQUENCE and cannot be completed by any later candle. A later candle can only participate in a newly formed candidate with a new observable start; it cannot retroactively supply the missing historical intrabar order.

## 4. Pullback Extreme Verification

After a Candle-Level Valid Pullback completes, Layer 2 records its directional extreme:

~~~
Bullish Valid Pullback → Pullback Low = lowest Low reached
Bearish Valid Pullback → Pullback High = highest High reached
~~~

The verified pullback extreme is derived across the complete pullback sequence, from pullback initiation through completion.

~~~
CANDLE-LEVEL VALID PULLBACK
        ↓
COMPLETE PULLBACK WINDOW
        ↓
EXTREME VERIFICATION
        ↓
VERIFIED PULLBACK EXTREME
~~~

## 5. Layer-2 pullback handoff and Layer-3 IDM input

A completed Candle-Level Valid Pullback is sufficient for Layer 2 to verify its directional extreme and expose the corresponding pullback-derived liquidity reference. Layer 3 consumes that reference for IDM classification. The later major structural retracement qualification is NOT an initial IDM prerequisite; it belongs to the continuation-BOS gate after CONFIRMED_STRUCTURAL_SWING.

~~~
CANDLE-LEVEL VALID PULLBACK
        ↓
VERIFIED PULLBACK EXTREME
        ↓
PULLBACK-DERIVED LIQUIDITY REFERENCE
        ↓
LAYER 3 IDM CLASSIFICATION
~~~

STRUCTURALLY VALID PULLBACK remains a Layer-3 structural qualification outcome where applicable, but it must not be inserted between the Layer-2 verified extreme and the initial IDM reference. The detailed major retracement criteria remain exclusively owned by 03_structural_semantic_authority.md.

## 6. Active Pullback Pointer

The active pullback state tracks the most recent canonical pullback relevant to the **active impulsive leg**. Structural mapping and downstream IDM/POI identification consume this active impulsive-leg lineage; internal complexity belonging only to the corrective leg is not independently promoted into structural candidates.

A newer valid pullback **immediately supersedes the prior active pullback-derived reference** for the active lifecycle, even when the prior reference has not yet been taken. Historical pullbacks remain immutable history, but the active reference pointer moves forward to the newest valid pullback.

After a pullback completes, the reference candle that was broken is no longer reusable as a fresh pullback reference merely because no new directional candle has appeared. A new active candle-level reference must be established by the Layer 1 directional sequence (or its canonical equal-extreme reference transfer).

This pointer movement is consumed by Layer 3, which owns the IDM classification and lifecycle.

~~~
NEWER CANDLE-LEVEL VALID PULLBACK
        ↓
VERIFIED PULLBACK EXTREME
        ↓
PULLBACK-DERIVED LIQUIDITY REFERENCE SHIFT
~~~

Historical pullbacks remain part of structural history.

## 7. Pullback-derived liquidity reference

For the active impulsive leg, Layer 2 exposes the liquidity reference implied by the verified extreme of the relevant valid pullback:

~~~
Bullish active leg
    Pullback Low
        ↓
Sell-Side Liquidity reference

Bearish active leg
    Pullback High
        ↓
Buy-Side Liquidity reference
~~~

This is a Layer 2 input object, not an IDM definition. Layer 2 does not classify the reference as Minor IDM or Major IDM and does not own IDM lifecycle state.

## 8. Layer 2 → Layer 3 handoff

Layer 2 delivers:

~~~
CANDLE-LEVEL VALID PULLBACK
VERIFIED PULLBACK EXTREME
PULLBACK-DERIVED LIQUIDITY REFERENCE
~~~

Layer 3 then owns:

~~~
IDM DEFINITION
MINOR_IDM / MAJOR_IDM CLASSIFICATION
ACTIVE IDM LIFECYCLE
IDM REFERENCE SHIFT
IDM LIQUIDITY TAKEOUT
CONFIRMED_STRUCTURAL_SWING
MAJOR STRUCTURAL RETRACEMENT QUALIFICATION FOR CONTINUATION BOS
VALID_BOS
IMPULSE_EXTENSION
TRADING RANGE ROLLOVER
CHoCH
~~~

The Layer 3 definitions are consumed through their canonical owner document; Layer 2 does not redefine them. A STRUCTURALLY VALID PULLBACK result may be consumed where the Layer-3 owner requires it for later structural qualification, but it is not an initial IDM prerequisite.

## 9. Layer 2 validation contract

A compliant implementation preserves:

- Candle-Level Valid Pullback as a sequential Layer 2 construct built from Layer 1 observations.
- Bullish pullback formation through reference-low takeout followed by reversal and reference-high break.
- Bearish pullback formation through reference-high takeout followed by reversal and reference-low break.
- Wick and body breach modes through the Layer 1 Candle Extreme Breach taxonomy.
- Candle color of the breach candle as non-discriminating for Candle-Level Valid Pullback validity.
- Pullback completion over one or multiple candles.
- Inside Bar handling through the Layer 1 mother-candle reference.
- Equal High / Equal Low reference identity transfer through the Layer 1 owner; Layer 2 consumes the transferred reference and does not redefine equality semantics.
- Outside Bar as an input to pullback formation, with unavailable intrabar order causing terminal candidate invalidation rather than retroactive confirmation.
- Pullback Extreme Verification across the complete pullback window.
- Structural qualification through the Layer 3 owner.
- Active Pullback Pointer following the most recent structurally accepted pullback.
- Pullback-derived liquidity references following the active pullback and verified extreme provenance; IDM classification is owned by Layer 3.
- Structural lifecycle events being handed to Layer 3 rather than recreated in Layer 2.

## 11. Canonical precedence

Semantic ownership governs documentation:

~~~
LAYER 1 DEFINITION
        ↓
LAYER 2 CONSUMPTION / SEQUENCE
        ↓
LAYER 3 QUALIFICATION / LIFECYCLE
~~~

A downstream layer uses the upstream semantic definition instead of creating a competing definition for the same object.
