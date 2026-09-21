# TRUE SMC — MINOR STRUCTURE

**Role:** Canonical Layer 2 Minor Structure of the True SMC methodology.

**Authority:** This document owns Sequential / Minor Structure, including Pullback Formation, Candle-Level Valid Pullback, verified pullback extremes, active pullback state, liquidity formation for the active minor leg, and Minor IDM eligibility. Candle-level primitives consumed by this layer are owned by 01_micro_structure.md.

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
LAYER 3 STRUCTURAL QUALIFICATION
        ↓
STRUCTURALLY VALID PULLBACK
        ↓
ACTIVE PULLBACK / LIQUIDITY
        ↓
MINOR IDM ELIGIBILITY
~~~

Each downstream state is produced only from the validated prerequisite state supplied by the preceding stage.

## 2. Candle-Level Valid Pullback

A **Candle-Level Valid Pullback** is a completed sequential candle-level event within an established Candlestick-Based Trend.

The pullback is defined by the ordered use of the applicable reference candle from the Layer 1 candle sequence.

### 2.1 Bullish Candle-Level Valid Pullback

In a bullish Candlestick-Based Trend:

1. The applicable reference candle is a bullish candle whose high was used to continue the candle-level uptrend.
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

1. The applicable reference candle is a bearish candle whose low was used to continue the candle-level downtrend.
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

The inner candle contributes its candle-level observations to the sequence, while the pullback reference continues to be evaluated against the applicable mother-candle context.

## 3. Outside Bar consumption

Layer 2 may consume a Layer 1 OUTSIDE_BAR observation as part of Candle-Level Valid Pullback formation.

The Outside Bar is evaluated inside the applicable directional sequence and reference context. The pullback remains an ordered event: one side is taken and the corresponding reference side is later broken after reversal.

**Derived architectural invariant:** one Outside Bar observation is evaluated within one applicable directional pullback branch for the active sequence state. Layer 2 does not create competing bullish and bearish pullback states from the same Outside Bar/reference context.

~~~
OUTSIDE_BAR
    ↓
APPLICABLE CANDLE SEQUENCE
    ↓
PULLBACK FORMATION
~~~

When aggregate OHLC does not expose the intrabar order needed by the sequence, Layer 2 uses the observability state provided by Layer 1 instead of manufacturing historical path evidence.

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

## 5. Structurally Valid Pullback handoff

A Candle-Level Valid Pullback is supplied to Layer 3 for structural qualification.

Layer 3 evaluates the major structural retracement requirements and returns the structural qualification result. When accepted, the pullback becomes a Structurally Valid Pullback for the structural lifecycle.

~~~
CANDLE-LEVEL VALID PULLBACK
        ↓
LAYER 3 QUALIFICATION
        ↓
STRUCTURALLY VALID PULLBACK
~~~

The detailed major retracement criteria, including depth, opposing-candle qualification, displacement-outlier handling, and higher-timeframe structural qualification are defined only by 03_structural_semantic_authority.md.

## 6. Active Pullback Pointer

The active pullback state tracks the **most recent structurally accepted pullback** relevant to the active impulsive leg.

When a newer Structurally Valid Pullback is established before the current active liquidity target is consumed, the active pointer transfers to the newer pullback.

~~~
NEWER STRUCTURALLY VALID PULLBACK
        ↓
ACTIVE PULLBACK POINTER TRANSFER
        ↓
CURRENT LIQUIDITY REFERENCE
~~~

Historical pullbacks remain part of the structural history.

## 7. Minor liquidity and IDM eligibility

For the active impulsive leg:

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

A Minor IDM becomes eligible from the liquidity associated with the most recent structurally accepted pullback on the active impulsive leg.

The eligibility sequence is:

~~~
STRUCTURALLY VALID PULLBACK
        ↓
VERIFIED PULLBACK EXTREME
        ↓
ACTIVE LIQUIDITY REFERENCE
        ↓
MINOR IDM ELIGIBILITY
        ↓
MINOR IDM
~~~

The Minor IDM state inherits the provenance of the pullback from which its liquidity reference was derived.

## 8. Minor IDM lifecycle

Within the active impulsive leg, the current Minor IDM follows the active pullback pointer.

~~~
NEW VALID PULLBACK
        ↓
NEW VERIFIED EXTREME
        ↓
ACTIVE PULLBACK POINTER TRANSFER
        ↓
MINOR IDM REFERENCE TRANSFER
~~~

The latest qualifying pullback is the active IDM reference. Historical IDM references remain available as history.

## 9. Layer 2 → Layer 3 handoff

Layer 2 delivers the following validated objects to Layer 3:

~~~
CANDLE-LEVEL VALID PULLBACK
VERIFIED PULLBACK EXTREME
STRUCTURALLY VALID PULLBACK STATUS
ACTIVE PULLBACK POINTER
MINOR IDM ELIGIBILITY
MINOR IDM
~~~

Layer 3 then owns the subsequent structural lifecycle, including:

~~~
IDM LIQUIDITY TAKEOUT
SWING CONFIRMATION
CONFIRMED_STRUCTURAL_SWING
MAJOR STRUCTURAL RETRACEMENT QUALIFICATION
VALID_BOS
IMPULSE_EXTENSION
TRADING RANGE ROLLOVER
CHoCH
~~~

The Layer 3 definitions are consumed through their canonical owner document; Layer 2 does not redefine them.

## 10. Layer 2 validation contract

A compliant implementation preserves:

- Candle-Level Valid Pullback as a sequential Layer 2 construct built from Layer 1 observations.
- Bullish pullback formation through reference-low takeout followed by reversal and reference-high break.
- Bearish pullback formation through reference-high takeout followed by reversal and reference-low break.
- Wick and body breach modes through the Layer 1 Candle Extreme Breach taxonomy.
- Candle color of the breach candle as non-discriminating for Candle-Level Valid Pullback validity.
- Pullback completion over one or multiple candles.
- Inside Bar handling through the Layer 1 mother-candle reference.
- Outside Bar as an input to pullback formation, with its applicable branch resolved from the active sequence context.
- Pullback Extreme Verification across the complete pullback window.
- Structural qualification through the Layer 3 owner.
- Active Pullback Pointer following the most recent structurally accepted pullback.
- Minor IDM eligibility following the active pullback and verified extreme provenance.
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
