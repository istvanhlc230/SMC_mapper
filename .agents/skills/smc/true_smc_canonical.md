# TRUE_SMC_CANONICAL

**Role:** Project-specific canonical True SMC methodology for the Layer 1 Candle-Level Foundation and Layer 2 Minor Structure.

**Authority:** Authoritative for Layer 1 and Layer 2 semantic definitions. Generic SMC/ICT terminology cannot override these project-specific rules.

**Lifecycle authority:** Layer 3 Structural Lifecycle rules are owned by `true_smc_structural_lifecycle.md`. Detailed CHoCH mechanics are provided by `true_smc_choch.md` as the detailed Section 3.5 module. Older Layer 3 wording previously retained in this document is superseded by the validated lifecycle documents and is intentionally not duplicated here.

Configuration, scoring, visualization, and implementation convenience must never redefine structural meaning.

## 1. Methodology architecture

True SMC is organized into three logical layers:

```text
TRUE SMC METHODOLOGY
│
├── 1. Candle-Level Foundation
│
├── 2. Minor Structure
│
└── 3. Structural Lifecycle
    ├── 3.1 Major Structure
    ├── 3.2 Genesis
    ├── 3.3 Swing / Protected Structural Extreme
    ├── 3.4 BOS
    └── 3.5 CHoCH
```

This document owns Layers 1–2 only.

The dependency boundary is:

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
ACTIVE / MINOR IDM
  ↓
[Layer 3 lifecycle begins]
```

Every higher-level event must consume previously validated lower-level state. No stage may be skipped or manufactured by configuration, scoring, visualization, or implementation convenience.

## 2. Mandatory semantic non-equivalences

The following distinctions are foundational and apply across the methodology:

```text
CANDLE-LEVEL VALID PULLBACK  ≠ STRUCTURALLY VALID PULLBACK
CANDLE-LEVEL VALID PULLBACK  ≠ IDM
STRUCTURALLY VALID PULLBACK  ≠ IDM
PULLBACK EXTREME             ≠ AUTOMATIC IDM
MINOR STRUCTURE              ≠ MAJOR STRUCTURE
MINOR STRUCTURE              ≠ LIQUIDITY
MINOR STRUCTURE              ≠ IDM
LOCAL / PIVOT EXTREME        ≠ CONFIRMED SWING
REFERENCE TRANSFER           ≠ VALID PULLBACK
INSIDE-BAR BREAK             ≠ VALID PULLBACK
INSIDE-BAR LIQUIDITY         ≠ IDM
LIQUIDITY                    ≠ STRUCTURE
CONFIGURATION OPTION         ≠ CANONICAL METHODOLOGY RULE

IDM SWEEP                    ≠ BOS
IDM SWEEP                    ≠ CHoCH
CHoCH                        ≠ BOS
CHoCH                        ≠ IDM
```

The final four distinctions are lifecycle boundaries; their detailed rules are authoritative in `true_smc_structural_lifecycle.md` and its detailed CHoCH module rather than being redefined here.

## 3. Candle-Level Minor Structure

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

## 5. Equal High / Equal Low Directional Reference Transfer

Equal High / Equal Low is a candle-level relationship. It participates in reference transfer only within the applicable directional candle context; it is not a directionless structural or IDM event.

### 5.1 Bullish context

When two consecutive candles have equal highs:

1. The shared high forms the Equal High relationship.
2. The **second candle becomes the active reference**.
3. Price must subsequently break below the **second candle low**.
4. Price must then break above the **shared high**.
5. This completes the applicable candle-level Valid Pullback sequence.

### 5.2 Bearish context

When two consecutive candles have equal lows:

1. The shared low forms the Equal Low relationship.
2. The **second candle becomes the active reference**.
3. Price must subsequently break above the **second candle high**.
4. Price must then break below the **shared low**.
5. This completes the applicable candle-level Valid Pullback sequence.

Reference transfer is directional and belongs to candle-level Valid Pullback construction.

Reference transfer does not by itself create a Structurally Valid Pullback, IDM, confirmed swing, BOS, or CHoCH.

## 6. Inside Bars

A strict inside bar is:

```text
current.high < mother.high
AND
current.low  > mother.low
```

Equality does not count as a strict inside bar.

A strict inside bar does not independently create a Valid Pullback, Structurally Valid Pullback, IDM, confirmed swing, BOS, or CHoCH.

A break of an inside-bar relationship requires independent structural validation.

## 7. Outside Bars

A single outside bar must not activate both directional branches.

Canonical candle-level sequencing:

```text
Bullish outside-bar sequence = LOW → HIGH
Bearish outside-bar sequence = HIGH → LOW
```

Directional interpretation comes from the applicable context and sequence. The outside-bar relationship itself does not independently create higher-level structure.

## 8. Verified Pullback Extreme

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
Structural Qualification
  ↓
Structurally Valid Pullback
  ↓
IDM Eligibility
```

## 9. Structural Retracement Qualification

A previous strict rule of “at least 3 opposing candles AND 38.2%” is no longer absolute. There are two validated qualification paths.

### 9.1 Standard path

```text
>= 3 opposing candles
AND
>= configured minimum retracement depth
```

The canonical default minimum is **38.2%**, exposed as a configurable methodology parameter where applicable.

Changing the configured value changes the threshold; it does not redefine the semantic identity of a Structurally Valid Pullback or IDM.

### 9.2 Exactly-two-candle momentum exception

Exactly 2 opposing candles may qualify when:

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

Mandatory constraints:

- The verified exception is for **exactly 2 candles**.
- There is **no automatic 1-candle exception**.
- “Large/high momentum” remains qualitative unless independently verified source material provides a quantitative threshold.
- Do not invent ATR, body-ratio, volatility, or standard-deviation thresholds and present them as canonical methodology.
- Numeric/configurable threshold ownership belongs to `methodology_parameters.md`.

If retracement sufficiency is not satisfied, the higher lifecycle must not manufacture a Structurally Valid Pullback from the insufficient sequence.

## 10. Structurally Valid Pullback

A candle-level Valid Pullback becomes a Structurally Valid Pullback only after structural retracement qualification.

Only a Structurally Valid Pullback can become the basis for active/minor IDM.

A candle-level pullback must never directly create IDM.

```text
CANDLE-LEVEL VALID PULLBACK
        ↓
RETRACEMENT QUALIFICATION
        ↓
STRUCTURALLY VALID PULLBACK
```

The semantic identity of the object is independent of any configured numeric threshold name.

## 11. Liquidity Taxonomy

For the active structural leg:

```text
Uptrend pullback low    → Sell-Side Liquidity (SSL)
Downtrend pullback high → Buy-Side Liquidity (BSL)
```

Every Structurally Valid Pullback extreme may represent liquidity, but not every liquidity node is IDM.

Liquidity is a market-state/reference concept. It is not automatically a structural event.

## 12. Single Active Pullback Pointer

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

Major IDM, Fallback Major IDM, Confirmed Swing, Protected Structural Extreme, Trading Range, BOS, and CHoCH lifecycle ownership begins in Layer 3 and is defined in `true_smc_structural_lifecycle.md`.

## 13. IDM Definition — Layer 2 Eligibility

IDM is liquidity resting beyond the most recent Structurally Valid Pullback on the active impulsive leg.

Therefore an active/minor IDM must be:

1. derived from a Structurally Valid Pullback;
2. associated with the active impulsive leg;
3. the most recent qualifying pullback;
4. represented by its relevant liquidity extreme.

Random bars, arbitrary pivots, inside bars, generic local highs/lows, Fibonacci levels, or every visible liquidity node are not IDM.

The existence of liquidity is not sufficient to establish IDM identity.

## 14. Minor / Active IDM Lifecycle

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

## 15. Minor IDM — Classification and Structural Role

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

## 16. Minor IDM Takeout Threshold

A qualified active/minor IDM does not require a candle body close to be breached or taken out.

Wick and body interaction are both valid for the IDM liquidity takeout.

```text
Qualified IDM
→ Wick or Body Takeout
→ IDM Liquidity Sweep
```

A body close beyond the IDM is not required.

A wick or body interaction with an arbitrary minor structural level, liquidity node, or local extreme does not independently create or activate an IDM. IDM identity must first be established through the eligibility rules above.

## 17. Layer 2 → Layer 3 Interface

Layer 2 produces validated structural inputs consumed by the Structural Lifecycle:

```text
CANDLE RELATIONSHIPS
        ↓
CANDLE-LEVEL VALID PULLBACK
        ↓
RETRACEMENT QUALIFICATION
        ↓
STRUCTURALLY VALID PULLBACK
        ↓
VERIFIED PULLBACK EXTREME
        ↓
LIQUIDITY
        ↓
ACTIVE PULLBACK POINTER
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

See `true_smc_structural_lifecycle.md`.

For detailed CHoCH mechanics, see `true_smc_choch.md`.

## 18. Parameter ownership boundary

Numeric methodology parameters are defined in `methodology_parameters.md`.

This document defines the semantic rule that retracement qualification is required and that the validated exception exists. The parameter document owns the configurable numeric values.

```text
SEMANTIC RULE
    ≠
CONFIGURATION VALUE
```

Configuration may change a threshold only where explicitly permitted. It must never change the identity of Valid Pullback, Structurally Valid Pullback, IDM, Minor IDM, or any Layer 3 structural object.

## 19. Layer 1 / Layer 2 Validation Contract

A compliant implementation must preserve all of the following:

- Candle relationships are observations, not automatically higher-level structure.
- Strict inside bars require strict containment and equality does not qualify.
- A single outside bar cannot activate both directional branches.
- Candle-level Valid Pullback requires the complete directional sequence.
- EQ High / EQ Low reference transfer is directional and uses the second candle as the active reference.
- Verified Pullback Extreme follows the candle-level Valid Pullback and is not automatically IDM.
- Structural retracement qualification has the standard path and the exactly-two-candle exception.
- There is no automatic one-candle exception.
- High-momentum remains qualitative unless independently verified quantitatively.
- Only a Structurally Valid Pullback can become the basis for active/minor IDM.
- Only the newest Structurally Valid Pullback remains the active Minor IDM target for the active leg.
- Minor IDM remains distinct from Major IDM, Confirmed Swing, Protected Structural Extreme, BOS, CHoCH, and Trading Range.
- A qualified IDM can be swept by wick or body without requiring body close.
- Arbitrary minor-level interaction does not manufacture IDM.
- Layer 3 lifecycle rules are consumed only after the required Layer 1/2 prerequisites exist.

## 20. Authority boundary and supersession rule

Older Layer 3 material previously contained in this file is not an alternative canonical implementation path.

The repository's validated lifecycle rules supersede conflicting older wording regardless of the historical location of that wording.

```text
NEWER EXPLICITLY VALIDATED RULE
        >
OLDER CONFLICTING RULE
```

Superseded rules that remain necessary for historical traceability belong in `deprecated.md` and must not silently re-enter canonical semantics.

The complete Layer 3 lifecycle is maintained in one logical methodology category: `true_smc_structural_lifecycle.md`, with `true_smc_choch.md` serving as its detailed 3.5 mechanics module.
