# TRUE SMC — CHoCH MECHANICS

**Role:** Detailed Section 3.5 CHoCH lifecycle module of `03_structural_semantic_authority.md`.

**Authority:** This document contains the canonical True SMC CHoCH mechanics in Sections 3.5.1–3.5.5. It is the detailed mechanics authority for CHoCH classification and post-CHoCH regime initialization within the Structural Lifecycle. It does **not** create a separate top-level methodology category or separate lifecycle ownership.

**Lifecycle ownership:** `03_structural_semantic_authority.md` owns Section 3.5 as part of the complete Layer 3 Structural Lifecycle. This document provides the detailed deterministic rules used by that lifecycle.

## 3.5 — Change of Character (CHoCH) Mechanics

CHoCH is a governing trend-reversal transition. It is not an arbitrary internal break, liquidity event, IDM sweep, or candle pattern.

### Canonical CHoCH Lifecycle

```text
OPPOSING STRUCTURAL BOUNDARY VIOLATION (Wick OR Body)
        ↓
CHoCH CLASSIFICATION GATE
        ↓
CHoCH_ELIGIBLE
        ↓
CHoCH_CONFIRMED
        ↓
OLD TREND TERMINATED + INITIAL ACTIVE IMPULSE INITIALIZED
```

### 3.5.1 — Unit of Origin

The eligible CHoCH reference object is the active Dealing Range's **Protected Opposing Structural Extreme / Governing Opposing Range Boundary**.

- Bullish lifecycle → Protected Swing Low.
- Bearish lifecycle → Protected Swing High.

Minor Structure, arbitrary local highs/lows, IDM levels, liquidity nodes, and continuation CONFIRMED_STRUCTURAL_SWING cannot independently create CHoCH.

```text
Protected Opposing Structural Extreme
        ↓
CHoCH Physical-Break Gate
```

A physical violation only opens the CHoCH classification gate; it does not itself establish `CHoCH_CONFIRMED`.

### 3.5.2 — Opposing Boundary Break: Physical Threshold

A Physical Opposing Boundary Break is the discrete OHLC event in which price physically penetrates the governing trend-protecting opposing boundary.

Bullish lifecycle:

```text
Low_t < Protected_Swing_Low
```

Bearish lifecycle:

```text
High_t > Protected_Swing_High
```

Physical penetration may occur through wick/shadow or candle-body penetration.

```text
Physical Opposing Boundary Break
        ≠
CHoCH_CONFIRMED
```

This gate records only the physical occurrence of the break. Final classification is determined by 3.5.3 and the tested level's Major IDM provenance.

### 3.5.3 — CHoCH Break Classification: Wick vs. Body Close

After 3.5.2, the CHoCH Structural Classification Gate applies the following deterministic rules.

#### A. Body-Close Reversal

Bullish:

```text
Close_t < Protected_Swing_Low
→ CHoCH_ELIGIBLE
```

Bearish:

```text
Close_t > Protected_Swing_High
→ CHoCH_ELIGIBLE
```

A body close beyond an eligible Protected Opposing Boundary is a CHoCH-eligible event. It becomes `CHoCH_CONFIRMED` only when **all applicable CHoCH prerequisites** pass. A body close alone is never sufficient to manufacture CHoCH, and the result does not depend on an internal Major IDM being present.

#### B. Wick-Break Reversal

A wick break of an eligible **Protected Opposing Structural Extreme / Governing Opposing Range Boundary** is `CHoCH_ELIGIBLE` unless the tested external level carries **Major IDM provenance**. A Major IDM is therefore **not a positive prerequisite** for a wick-path CHoCH.

```text
ELIGIBLE OPPOSING EXTERNAL BOUNDARY
       ↓
OPPOSING WICK BREAK
       ↓
IF TESTED LEVEL = MAJOR IDM
       → NOT CHoCH
OTHERWISE
       → ALL APPLICABLE CHoCH PREREQUISITES
       → CHoCH_CONFIRMED
```

If the tested external level has Major IDM provenance, the wick is `MAJOR_IDM_SWEEP`, not CHoCH. A later reclassification must not be inferred from wick geometry alone.

The wick/body geometry does not determine structural identity by itself. Level provenance and the active liquidity state determine the final classification.
### 3.5.3A — LTF-CHoCH Context After HTF Interaction

The knowledgebase defines a specific lower-timeframe CHoCH route after price has interacted with a higher-timeframe Point of Interest or a core-liquidity level. This route is a **context-gated representation of the same CHoCH concept**, not a new lifecycle state.

#### Activation precondition

```text
ACTIVE HTF DIRECTIONAL NARRATIVE
        AND
HTF POI INTERACTION
        OR
HTF CORE-LIQUIDITY TAKEOUT
        ↓
LTF-CHoCH CONTEXT ACTIVE
```

HTF POI interaction means mitigation/reaction against a canonical HTF POI. HTF core-liquidity takeout means a canonical HTF IDM or Engineering Liquidity interaction. The LTF context may refine execution, but it must not independently reverse the HTF bias.

#### LTF governing reference

While the LTF-CHoCH context is active:

```text
MOST RECENTLY FORMED VALID LTF PULLBACK
        ↓
VERIFIED PULLBACK EXTREME
        ↓
LTF ACTIVE INDUCEMENT REFERENCE
        ↓
GOVERNING LTF CHoCH REFERENCE
```

The reference is the most recently formed **valid** LTF pullback. An arbitrary local pivot, invalid pullback, SMT, or visually convenient high/low cannot replace it.

The reference may represent a Minor IDM or another valid LTF pullback-derived IDM role. The source's determining property is recency and validity, not the label "major" versus "minor".

#### LTF break qualification

The True SMC source defines the LTF CHoCH confirmation gate as a **completed LTF candle body close beyond the governing LTF Inducement reference**. A wick-only penetration is a liquidity sweep/physical interaction, not LTF CHoCH confirmation:

Bullish HTF context / bearish LTF reversal:

```text
Close_LTF < LTF_Inducement_Reference_Low
        ↓
LTF_CHoCH_ELIGIBLE
```

Bearish HTF context / bullish LTF reversal:

```text
Close_LTF > LTF_Inducement_Reference_High
        ↓
LTF_CHoCH_ELIGIBLE
```

A wick-only penetration of the LTF inducement reference does not confirm this special route. It remains an unconfirmed physical interaction unless another canonical CHoCH route independently applies.

#### Confirmation and scope

```text
LTF_CHoCH_ELIGIBLE
        ↓
ALL APPLICABLE CHoCH PREREQUISITES
        ├─ FAIL → REMAIN / CONTEXT CONTINUES
        └─ PASS
             ↓
        CHoCH_CONFIRMED
             ↓
        NEW TREND / REGIME SHIFT
```

The special LTF reference replaces the normal HTF external boundary **only while the LTF-CHoCH context is active**. Once CHoCH_CONFIRMED occurs, the normal post-CHoCH lifecycle in 3.5.5 applies and the prior LTF context is cleared.

This route does not create a new top-level lifecycle state and does not convert the LTF inducement into a Major IDM. The LTF reference is a temporary CHoCH reference object for the active context.

#### Non-equivalences

```text
HTF POI INTERACTION ≠ CHoCH
HTF CORE-LIQUIDITY TAKEOUT ≠ CHoCH
LTF VALID PULLBACK ≠ CHoCH
LTF INDUCEMENT SWEEP ≠ CHoCH
LTF CHoCH CONTEXT ≠ NEW LIFECYCLE STATE
LTF CHoCH REFERENCE ≠ MAJOR_IDM
```
### 3.5.4 — Major IDM / CHoCH interaction

When the tested opposing boundary carries Major IDM provenance, the Major IDM interaction rule applies. This is not a separate fallback IDM type.

#### A. Wick Breach of Major IDM

```text
MAJOR_IDM
    +
WICK BREACH
    ↓
MAJOR_IDM_SWEEP
```

A Major IDM wick sweep is not CHoCH_CONFIRMED, not VALID_BOS, and does not roll the Trading Range or lock the Protected Structural Extreme. It may satisfy the applicable IDM-takeout requirement, but it does not automatically create a CONFIRMED_STRUCTURAL_SWING.

#### B. Body Close Beyond Major IDM

```text
MAJOR_IDM
    +
BODY CLOSE BEYOND BOUNDARY
    ↓
CHoCH_ELIGIBLE
```

A body close beyond a Major IDM boundary enters the CHoCH qualification gate. It becomes CHoCH_CONFIRMED only when all applicable CHoCH prerequisites pass.

#### C. Major IDM lifecycle

After BOS, if only a Minor IDM is formed and no new Major IDM is qualified, the previous protected external boundary remains the active Major IDM reference. When a new post-BOS Major IDM is independently qualified, it supersedes the previous active Major IDM from that point forward.

```text
VALID_BOS
    ↓
POST-BOS PRICE ACTION
    ├─ NEW MAJOR IDM QUALIFIED → NEW MAJOR IDM ACTIVE
    └─ MINOR IDM ONLY → PREVIOUS PROTECTED BOUNDARY REMAINS MAJOR IDM
```

Historical IDM provenance is immutable; later candles do not retroactively rewrite earlier event classification.

## 3.5 Canonical invariants

```text
PHYSICAL OPPOSING BREAK
≠ AUTOMATIC CHoCH

BODY CLOSE
→ CHoCH_ELIGIBLE
→ CHoCH_CONFIRMED only if all prerequisites pass

ELIGIBLE OPPOSING EXTERNAL BOUNDARY + OPPOSING WICK BREAK
+ TESTED LEVEL IS NOT MAJOR IDM
+ ALL CHoCH PREREQUISITES
→ CHoCH_CONFIRMED

MAJOR_IDM + OPPOSING WICK BREAK
→ MAJOR_IDM_SWEEP
→ NOT CHoCH_CONFIRMED
→ NOT VALID_BOS
→ NOT TRADING_RANGE_ROLLOVER

MAJOR_IDM + BODY CLOSE
→ CHoCH_ELIGIBLE
→ CHoCH_CONFIRMED only if all prerequisites pass (true trend reversal, regime shift)

FIRST_POST_CHOCH_SVP
≠ FIRST_POST_CHOCH_MINOR_IDM

MAJOR_IDM
≠ MAJOR_IDM

CONFIRMATION GATE UNLOCKED
≠ NEW STATE ENUM

LATER CANDLE
≠ RETROACTIVE CLASSIFICATION

CHoCH_CONFIRMED
→ NEW TREND
→ INITIAL_ACTIVE_IMPULSE
→ CONFIRMATION_LOCKED
→ POST-CHOCH SVP / IDM LINEAGE
→ CONFIRMED_STRUCTURAL_SWING QUALIFICATION
→ FIRST BOS
→ POST-BOS MAJOR_IDM LIFECYCLE
```

This file is the detailed Section 3.5 module of `03_structural_semantic_authority.md`, not a separate lifecycle authority.
