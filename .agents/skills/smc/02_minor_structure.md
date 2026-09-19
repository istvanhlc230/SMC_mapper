# TRUE SMC — MINOR STRUCTURE

**Role:** Canonical Layer 2 Minor Structure of the True SMC methodology.

**Authority:** Authoritative for candle-level pullback qualification, verified pullback extremes, liquidity/IDM foundations, active pullback state, and Minor IDM semantics.

Major structural retracement qualification is owned by `03_structural_lifecycle.md` Section 3.3.2. Layer 2 consumes that qualification; it does not define it.

## 1. Methodology boundary

Layer 2 consumes Layer 1 candle relationships and produces validated inputs for the Layer 3 lifecycle.

```text
RAW OHLC
  ↓
CANDLE RELATIONSHIPS
  ↓
CANDLE-LEVEL VALID PULLBACK
  ↓
VERIFIED PULLBACK EXTREME
  ↓
LAYER 3 — MAJOR STRUCTURAL RETRACEMENT QUALIFICATION
  ↓
STRUCTURALLY VALID PULLBACK
  ↓
LIQUIDITY / IDM ELIGIBILITY
  ↓
ACTIVE / MINOR IDM
  ↓
Layer 3 — Structural Lifecycle
```

Every higher-level event must consume previously validated lower-level state. No stage may be skipped or manufactured by configuration, scoring, visualization, or implementation convenience.

## 2. Candle-Level Minor Structure

Minor Structure consists of internal candle-level structural price action that does not define or alter the governing external Trading Range.

Within an established Trading Range, Minor Structure exists inside the governing external boundaries. Minor structural levels may provide liquidity references and may participate in IDM formation only when the independent IDM prerequisites are satisfied.

```text
Minor Structure
≠ Major Structure
≠ Liquidity
≠ IDM
≠ BOS
≠ CHoCH
```

A minor structural level or arbitrary local high/low does not become an IDM merely because price interacts with it.

## 3. Verified Pullback Extreme

After a candle-level Valid Pullback:

```text
Bullish: verified pullback extreme = Pullback Low
Bearish: verified pullback extreme = Pullback High
```

This extreme is a candidate liquidity reference, not automatic IDM.

The required dependency is:

```text
Candle-Level Valid Pullback
  ↓
Verified Pullback Extreme
  ↓
Layer 3 Structural Qualification
  ↓
Structurally Valid Pullback
  ↓
IDM Eligibility
```

## 4. Structural qualification boundary

Major structural retracement qualification is **not owned by Layer 2 Minor Structure**. It is a Layer 3 Major Structure rule owned by `03_structural_lifecycle.md`.

Layer 2 may produce the candle-level Valid Pullback and verified pullback extreme that become inputs to the Layer 3 structural qualification stage, but Layer 2 must not redefine the major-structure qualification criteria.

The canonical Layer 3 qualification paths are:

```text
STANDARD
>= 3 OPPOSING CANDLES
AND
RETRACEMENT DEPTH >= 38.2%
```

or:

```text
EXACTLY 2 OPPOSING CANDLES
AND
LARGE / HIGH-MOMENTUM PRICE ACTION
AND
(
    >= 5 PRIOR CANDLE EXTREMES SWEPT/ENGULFED
    OR
    RETRACEMENT DEPTH >= 38.2%
)
```

There is no automatic one-candle exception.

This section is a boundary reference, not a second semantic definition. The canonical semantic definition is `03_structural_lifecycle.md` Section 3.3.2; numeric/configurable ownership is in `methodology_parameters.md`.

## 5. Structurally Valid Pullback

A candle-level Valid Pullback becomes a Structurally Valid Pullback only after Layer 3 structural retracement qualification.

Only a Structurally Valid Pullback can become the basis for active/minor IDM.

A candle-level pullback must never directly create IDM.

```text
CANDLE-LEVEL VALID PULLBACK
        ↓
LAYER 3 STRUCTURAL QUALIFICATION
        ↓
STRUCTURALLY VALID PULLBACK
```

The semantic identity of the object is independent of any configured numeric threshold name.

## 6. Liquidity Taxonomy

For the active structural leg:

```text
Uptrend pullback low    → Sell-Side Liquidity (SSL)
Downtrend pullback high → Buy-Side Liquidity (BSL)
```

Every Structurally Valid Pullback extreme may represent liquidity, but not every liquidity node is IDM.

Liquidity is a market-state/reference concept. It is not automatically a structural event.

## 7. Single Active Pullback Pointer

The active structural leg must track one active pullback pointer: the most recent Structurally Valid Pullback.

If a newer Structurally Valid Pullback forms before the previous active target is swept, immediately replace the active pointer with the newer pullback.

Do not keep multiple competing minor IDM targets active simultaneously.

This does not mean deleting historical structure. Maintain these identities separately:

```text
ACTIVE PULLBACK POINTER
≠ MINOR IDM STATE
≠ MAJOR IDM STATE
≠ CONFIRMED SWING
≠ TRADING RANGE
≠ HISTORICAL STRUCTURE
```

Major IDM, Fallback Major IDM, Confirmed Swing, Protected Structural Extreme, Trading Range, BOS, and CHoCH lifecycle ownership begins in Layer 3 and is defined in `03_structural_lifecycle.md`.

## 8. IDM Definition — Layer 2 Eligibility

IDM is liquidity resting beyond the most recent Structurally Valid Pullback on the active impulsive leg.

Therefore an active/minor IDM must be:

1. derived from a Structurally Valid Pullback;
2. associated with the active impulsive leg;
3. the most recent qualifying pullback;
4. represented by its relevant liquidity extreme.

Random bars, arbitrary pivots, inside bars, generic local highs/lows, Fibonacci levels, or every visible liquidity node are not IDM.

The existence of liquidity is not sufficient to establish IDM identity.

## 9. Minor / Active IDM Lifecycle

The active/minor IDM shifts immediately to the newest Structurally Valid Pullback on the same active impulsive leg.

Historical IDM may remain in history but must not remain an active competing target.

```text
NEWER VALID STRUCTURALLY VALID PULLBACK
        ↓
ACTIVE PULLBACK POINTER TRANSFERS
        ↓
ACTIVE / MINOR IDM TARGET TRANSFERS
```

This transfer does not mutate Major IDM state, Confirmed Swing state, Protected Structural Extreme state, Trading Range state, or historical structure.

## 10. Minor IDM — Classification and Structural Role

A Minor IDM is a qualified inducement/liquidity structure associated with the active impulsive leg within the current structural lifecycle.

A Minor IDM must satisfy all canonical IDM eligibility requirements and must be derived directly from a Structurally Valid Pullback and its verified pullback extreme.

The mere existence of a pre-BOS state, post-CHoCH state, or arbitrary internal liquidity does not establish a Minor IDM.

The Minor IDM functions strictly as internal liquidity within the active structural leg. It is ontologically distinct from Confirmed Structural Swing and Protected Structural Extreme.

```text
Active Structural Lifecycle
           +
Active Impulsive Leg
           +
Structurally Valid Pullback
           +
Verified Pullback Extreme
           +
Canonical IDM Eligibility
           ↓
       MINOR IDM

Minor IDM ≠ Confirmed Swing
Minor IDM ≠ Protected Structural Extreme
Minor IDM ≠ BOS
Minor IDM ≠ CHoCH
```

## 11. Minor IDM Takeout Threshold

A qualified active/minor IDM does not require a candle body close to be breached or taken out.

Wick and body interaction are both valid for the IDM liquidity takeout.

```text
Qualified IDM
→ Wick or Body Takeout
→ IDM Liquidity Sweep
```

A body close beyond the IDM is not required.

A wick or body interaction with an arbitrary minor structural level, liquidity node, or local extreme does not independently create or activate an IDM. IDM identity must first be established through the eligibility rules above.

## 12. Layer 2 → Layer 3 Interface

Layer 2 produces validated structural inputs consumed by the Structural Lifecycle:

```text
CANDLE RELATIONSHIPS
        ↓
CANDLE-LEVEL VALID PULLBACK
        ↓
VERIFIED PULLBACK EXTREME
        ↓
LAYER 3 STRUCTURAL QUALIFICATION
        ↓
STRUCTURALLY VALID PULLBACK
        ↓
LIQUIDITY
        ↓
IDM ELIGIBILITY
        ↓
ACTIVE / MINOR IDM
        ↓
LAYER 3
```

Layer 3 owns:

- Major Structure;
- Genesis / bootstrap;
- Confirmed Swing;
- Protected Structural Extreme;
- Major IDM and Fallback Major IDM lifecycle;
- IDM sweep → Swing Confirmation Gate;
- Physical External Break;
- BOS;
- Trading Range rollover;
- CHoCH and post-CHoCH regime initialization.

See `03_structural_lifecycle.md`.

## 13. Parameter ownership boundary

Numeric methodology parameters are defined in `methodology_parameters.md`.

This document defines the semantic boundary that retracement qualification is required and that the validated exception exists. The parameter document owns the configurable numeric values.

```text
SEMANTIC RULE
    ≠
CONFIGURATION VALUE
```

Configuration may change a threshold only where explicitly permitted. It must never change the identity of Valid Pullback, Structurally Valid Pullback, IDM, Minor IDM, or any Layer 3 structural object.

## 14. Layer 2 Validation Contract

A compliant implementation must preserve all of the following:

- Candle relationships are observations, not automatically higher-level structure.
- Strict inside bars require strict containment and equality does not qualify.
- A single outside bar cannot activate both directional branches.
- Candle-level Valid Pullback requires the complete directional sequence.
- EQ High / EQ Low reference transfer is directional and uses the second candle as the active reference.
- Verified Pullback Extreme follows the candle-level Valid Pullback and is not automatically IDM.
- Major structural retracement qualification is owned by Layer 3 and has the standard path and exactly-two-candle exception.
- There is no automatic one-candle exception.
- High-momentum remains qualitative unless independently verified quantitatively.
- Only a Structurally Valid Pullback can become the basis for active/minor IDM.
- Only the newest Structurally Valid Pullback remains the active Minor IDM target for the active leg.
- Minor IDM remains distinct from Major IDM, Confirmed Swing, Protected Structural Extreme, BOS, CHoCH, and Trading Range.
- A qualified IDM can be swept by wick or body without requiring body close.
- Arbitrary minor-level interaction does not manufacture IDM.
- Layer 3 lifecycle rules are consumed only after the required Layer 1/2 prerequisites exist.

## 15. Authority and supersession

Older conflicting wording does not remain authoritative merely because it was historically stored in the canonical file.

```text
NEWER EXPLICITLY VALIDATED RULE
        >
OLDER CONFLICTING RULE
```

Superseded rules that remain necessary for historical traceability belong in repository history and must not silently re-enter canonical semantics.
