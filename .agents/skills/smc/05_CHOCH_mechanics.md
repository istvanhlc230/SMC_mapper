# TRUE SMC — CHoCH MECHANICS

**Role:** Detailed Section 3.5 CHoCH lifecycle module of `03_structural_semantic_authority.md`.

**Authority:** This document contains the canonical True SMC CHoCH mechanics in Sections 3.5.1–3.5.5. It is the detailed mechanics authority for CHoCH classification and post-CHoCH regime initialization within the Structural Lifecycle. It does **not** create a separate top-level methodology category or separate lifecycle ownership.

**Lifecycle ownership:** `03_structural_semantic_authority.md` owns Section 3.5 as part of the complete Layer 3 Structural Lifecycle. This document provides the detailed deterministic rules used by that lifecycle.

## 3.5 — Change of Character (CHoCH) Mechanics

### Structural namespace boundary

CHoCH is a structural lifecycle transition, not a synonym for every break. Its governing reference may be a Major/External protected boundary or, under the canonical LTF Structural Glitch context, the latest valid LTF pullback/IDM reference.

The LTF route does not rename or promote that Minor reference into Major Structure. Break mode is determined by the active IDM provenance and the applicable CHoCH gate.



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

The ordinary CHoCH reference object is the active Dealing Range's **Protected Opposing Structural Extreme / Governing Opposing Range Boundary**.

- Bullish lifecycle → Protected Swing Low.
- Bearish lifecycle → Protected Swing High.

Minor Structure, arbitrary local highs/lows, IDM levels, liquidity nodes, and continuation CONFIRMED_STRUCTURAL_SWING cannot independently create CHoCH **on the ordinary external-boundary route**. The canonical LTF Structural Glitch is the explicit exception: while that context is active, the most recently formed valid LTF pullback / active LTF IDM reference temporarily becomes the governing CHoCH reference under §3.5.3A. This is reference substitution, not promotion of the Minor object into Major Structure.

```text
ORDINARY ROUTE
Protected Opposing Structural Extreme
        ↓
CHoCH Physical-Break Gate

LTF STRUCTURAL GLITCH
Most Recent Valid LTF Pullback / Active LTF IDM
        ↓
CHoCH Physical-Break Gate
```

A physical violation only opens the CHoCH classification gate; it does not itself establish `CHoCH_CONFIRMED`.

**Bootstrap exclusion and precedence:** `BOOTSTRAP_ORIGIN_ANCHOR` is not an eligible CHoCH reference. When `ACTIVE_FIRST_BOS_BOOTSTRAP = TRUE` for the current mapping domain, physical breach of that initialization anchor is classified first as `BOOTSTRAP_ANCHOR_BREAK → BOOTSTRAP_REVERSAL`, not as `EXT_OPP_BREAK`, `CHoCH_ELIGIBLE`, or `CHoCH_CONFIRMED`, regardless of whether the runtime state is `BOOTSTRAP`, `CONFIRMATION_LOCKED`, or `POST_CHOCH`. This bootstrap preclassification has precedence over the normal CHoCH classifier for that mapping domain. An independently scoped LTF Structural Glitch context remains governed by §3.5.3A in its own applicable mapping context, but it cannot reinterpret the bootstrap anchor itself as a CHoCH boundary. The bootstrap reversal only changes the active mapping lineage; it does not manufacture structural state.

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

The wick/body geometry does not determine structural identity by itself. Level provenance and the active liquidity state determine the final classification. If the tested level's provenance cannot be established, do not infer either `CHoCH_ELIGIBLE` or `MAJOR_IDM_SWEEP` from geometry alone; keep the structural classification blocked until the required canonical provenance inputs are available.
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

The reference is the most recently formed valid LTF pullback / its verified pullback extreme. This is a temporary CHoCH reference only; the reference is not promoted into Major Structure. Reference selection and Major IDM identity must remain separate.

The classification must evaluate two distinct facts:

- **Active LTF IDM context:** whether a pullback-derived Major IDM has qualified in the active LTF range, or whether the prior protected external boundary remains the active Major IDM reference because only Minor IDM is available.
- **Tested-level provenance:** whether the exact LTF reference being physically broken itself carries the active Major IDM provenance.

The presence of a Major IDM somewhere in the LTF range does **not**, by itself, prove that the tested LTF reference carries Major IDM provenance. Conversely, a distinct LTF reference must not be assumed merely because its label differs; its level identity and provenance must be deterministically established.

#### LTF Structural Glitch — reference substitution and IDM-dependent break mode

The 2026 True SMC source explicitly describes a **small glitch in the structure cycle** after price has mitigated a higher-timeframe valid reversal zone / POI. In that context, the LTF CHoCH is not delayed until the ordinary LTF external boundary is broken. Instead, the **most recently formed valid LTF pullback / its inducement** becomes the operative CHoCH reference.

Source evidence: `truesmc2026.txt`, Part 5 / lower-timeframe execution example, approximately 00:08:47–00:10:36 and again 00:13:13–00:13:31.

Apply these rules in order:

1. **The tested LTF reference itself carries Major IDM provenance:** a wick breach is `MAJOR_IDM_SWEEP`, not `CHoCH_ELIGIBLE` or `CHoCH_CONFIRMED`. A completed body close beyond the Major IDM reference enters `CHoCH_ELIGIBLE`, subject to all applicable CHoCH prerequisites.
2. **A distinct pullback-derived Major IDM is active elsewhere in the LTF range:** if the tested LTF reference is an eligible structural reference and is demonstrably distinct from the active Major IDM level, a wick break may enter `CHoCH_ELIGIBLE`. The separate Major IDM's existence alone is insufficient; the tested reference's distinct identity and non-Major-IDM provenance must be established.
3. **Only Minor IDM is available and no newer pullback-derived Major IDM has qualified:** the prior protected external boundary remains the active Major IDM reference. A wick of that external boundary is `MAJOR_IDM_SWEEP`, not CHoCH. The substituted LTF reference may instead be the Minor IDM reference: a wick through that Minor reference is an LTF inducement sweep / `IDM_TAKEN`, not CHoCH and not automatically `MAJOR_IDM_SWEEP`; the applicable completed body close beyond the active LTF CHoCH reference is required to enter `CHoCH_ELIGIBLE`.
4. **Tested-reference provenance is missing or ambiguous:** fail closed. Do not emit `CHoCH_ELIGIBLE`, `CHoCH_CONFIRMED`, or `MAJOR_IDM_SWEEP` by assumption. Resolve the canonical reference/provenance inputs before classifying the structural outcome.

This preserves the source-supported LTF reference substitution while applying the ordinary CHoCH provenance rule to the **specific level being tested**. The LTF context does not override §3.5.4: a wick of the Major IDM itself is always a Major IDM sweep. It also does not impose a universal body-close requirement when a distinct eligible LTF reference and a separate active Major IDM are deterministically established.

Bullish HTF context / bearish LTF reversal:

```text
HTF POI / CORE-LIQUIDITY INTERACTION
        ↓
LTF STRUCTURAL GLITCH
        ↓
MOST RECENT VALID LTF PULLBACK / IDM
        ↓
IDM-TYPE VALIDATION
   ├─ MAJOR IDM → wick breach may satisfy CHoCH eligibility
   └─ MINOR IDM ONLY → body close beyond active LTF reference required
```

Bearish HTF context / bullish LTF reversal is the mirrored rule.

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
LTF STRUCTURAL GLITCH ≠ UNIVERSAL BODY-CLOSE RULE
LTF CHoCH CONFIRMATION MODE = IDM-TYPE DEPENDENT
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

A Major IDM wick sweep is neither `CHoCH_ELIGIBLE` nor `CHoCH_CONFIRMED`, is not `VALID_BOS`, and does not roll the Trading Range or lock the Protected Structural Extreme. The sweep satisfies the applicable IDM-takeout requirement (`IDM_TAKEN`) when the Major IDM reference is physically penetrated, and that `IDM_TAKEN` establishes the associated swing-point candidate / provisional structural extreme. Macro retracement qualification is still required before the candidate becomes `CONFIRMED_STRUCTURAL_SWING` on the continuation-BOS path. The sweep does not by itself create `VALID_BOS` or `CHoCH_CONFIRMED`.

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

After BOS, if no new Layer-2 **Candle-Level Valid Pullback → Verified Pullback Extreme** has established the next Major IDM, the previous protected external boundary remains the active Major IDM reference. When that post-BOS validated pullback state is reached, it establishes and supersedes the previous active Major IDM from that point forward.

```text
VALID_BOS
    ↓
POST-BOS PRICE ACTION
    ├─ NEW MAJOR IDM QUALIFIED → NEW MAJOR IDM ACTIVE
    └─ MINOR IDM ONLY → PREVIOUS PROTECTED BOUNDARY REMAINS MAJOR IDM
```

Historical IDM provenance is immutable; later candles do not retroactively rewrite earlier event classification.

## 3.6 Canonical invariants

```text
PHYSICAL OPPOSING BREAK
≠ AUTOMATIC CHoCH

ELIGIBLE OPPOSING STRUCTURAL BOUNDARY + BODY CLOSE BEYOND THAT BOUNDARY
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

MAJOR_IDM provenance
≠ CHoCH confirmation

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
