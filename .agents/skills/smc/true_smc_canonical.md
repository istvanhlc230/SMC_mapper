# TRUE_SMC_CANONICAL

**Role:** Project-specific canonical True SMC methodology.

**Authority:** This category contains rules that define the project's True SMC semantics and are not to be silently replaced by generic SMC/ICT interpretations.

## Structural chain

```text
RAW OHLC
↓
CANDLE RELATIONSHIPS
↓
CANDLE-LEVEL MINOR STRUCTURE
↓
CANDLE-LEVEL VALID PULLBACK
↓
STRUCTURAL RETRACEMENT QUALIFICATION
↓
STRUCTURALLY VALID PULLBACK
↓
VERIFIED PULLBACK EXTREME
↓
BSL / SSL LIQUIDITY
↓
ACTIVE PULLBACK POINTER
↓
IDM ELIGIBILITY
↓
ACTIVE/MINOR IDM
↓
IDM LIQUIDITY TAKEOUT
↓
SWING CONFIRMATION
↓
CONFIRMED STRUCTURAL SWING
↓
PHYSICAL STRUCTURAL BREAK
↓
BREAK ACCEPTANCE
↓
BOS
↓
NEW TRADING RANGE
```

## Core canonical rules

### Valid Pullback

A candle-level Valid Pullback is a formal multi-step sequence. It is not a previous-candle-low/high shortcut and is not itself a Structurally Valid Pullback or IDM.

### Structural qualification

The standard path requires `>= 3` opposing candles and the configured minimum retracement depth. The canonical default retracement is `38.2%`.

Exactly two opposing candles may qualify through the verified momentum exception when the required high-momentum condition and either the `>= 5` prior candle-extreme condition or `>= 38.2%` retracement condition are satisfied. A one-candle exception must not be invented.

### IDM

IDM is liquidity resting beyond the most recent Structurally Valid Pullback on the active impulsive leg.

Therefore IDM must be derived from a Structurally Valid Pullback, be on the active impulsive leg, be the most recent qualifying pullback, and be represented by its relevant liquidity extreme.

Arbitrary local highs/lows, pivots, inside bars, Fibonacci levels, generic liquidity pools, or candle count alone do not create IDM.

### Minor / active IDM

The newest Structurally Valid Pullback on the same active impulsive leg replaces the previous active Minor IDM target. Historical IDM remains historical and is not a competing active target.

### Major IDM

Real Major IDM follows the post-BOS lifecycle:

```text
BOS → New Trading Range → first real post-BOS Structurally Valid Pullback → Major IDM
```

Fallback Major IDM is distinct from Real Major IDM and must not be treated as equivalent.

### IDM sweep / swing / BOS separation

An IDM sweep is a liquidity event. It is not automatically BOS or CHoCH.

Swing confirmation requires the canonical IDM/liquidity sequence. Confirmed range-side structure and Protected/Strong Swing state are separate lifecycle states.

External BOS requires the canonical structural context, IDM takeout, confirmed swing/range side, physical break, break acceptance, and active-Major-IDM gate where applicable.

Eligible external Wick BOS and Full Body-Close BOS remain distinct canonical outcomes.

### CHoCH

CHoCH is caused by violation of the governing Trading Range boundary. It is not an IDM sweep, BOS, local-pivot break, or displacement event.

The CHoCH-causing price leg becomes the initial active impulsive leg of the new trend, but does not automatically create a pullback, IDM, or protected swing.

### Trading Range

Trading Range is separate from Active/Minor IDM, Major IDM, Fallback Major IDM, confirmed swing, local pivot, and POI. Internal fluctuations, liquidity sweeps, FVG interaction, Order Block interaction, and displacement do not automatically create a new range.

### Deep retracement

Deep retracement alone does not reset confirmed structure or re-anchor a confirmed swing. Trading Range boundaries govern regime health; Active IDM governs the short-term swing-confirmation mechanism.

### POI ontology

Canonical tradable POIs are limited to Valid Order Flow (OF) and Valid Order Block (OB). Rule of Two permits the Decisional POI and Extreme POI within the canonical dealing-range model.

Standalone FVG, IDM, liquidity, displacement zones, Breaker Blocks, Mitigation Blocks, and arbitrary liquidity pools are not silently promoted to POIs.

### Order Block

Valid OB requires all three canonical pillars:

1. origin of impulsive displacement causing structural BOS;
2. candle sweeps the previous candle's extreme;
3. active, fully unmitigated adjacent FVG/imbalance.

The BOS used by Pillar 1 must itself be independently canonical.

### FVG

FVG is a validator/property and never a standalone tradable POI or direct entry trigger. It may participate as the OB-validation pillar but must not create BOS or CHoCH.

### Entry modules

The canonical execution layer contains four modules: IDM Sweep, Decisional POI Mitigation, Engineering Liquidity Sweep, and Extreme POI Mitigation. These consume structural facts; they do not manufacture structural events.

### Genesis

Genesis must not fabricate historical IDM, confirmed swing, BOS, Major IDM, or protected structure. Bootstrap behavior must remain distinguishable from organically confirmed structure.

### Obsolete variant

The historical sub-38.2% Fibonacci bootstrap variant is obsolete and must not exist in canonical methodology or implementation semantics.

## Full-source preservation

This file is a category view created without deleting the existing canonical rules. The complete original rule text remains in `skill.md` until the final verified split replaces it.
