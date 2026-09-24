# TRUE SMC — CHoCH MECHANICS

**Role:** Detailed Section 3.5 CHoCH lifecycle module of `03_structural_semantic_authority.md`.

**Authority:** This document contains the canonical True SMC CHoCH mechanics in Sections 3.5.1–3.5.5. It is the detailed mechanics authority for CHoCH classification and post-CHoCH regime initialization within the Structural Lifecycle. It does **not** create a separate top-level methodology category or separate lifecycle ownership.

**Lifecycle ownership:** `03_structural_semantic_authority.md` owns Section 3.5 as part of the complete Layer 3 Structural Lifecycle. This document provides the detailed deterministic rules used by that lifecycle.

## 3.5 — Change of Character (CHoCH) Mechanics

CHoCH is a governing trend-reversal transition. It is not an arbitrary internal break, liquidity event, IDM sweep, or candle pattern.

### Canonical CHoCH Lifecycle

```text
OPPOSING STRUCTURAL BOUNDARY VIOLATION (Body Close)
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

This gate records only the physical occurrence of the break. Final classification is determined by 3.5.3 and the Fallback Major IDM exception in 3.5.4.

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

A wick break of an eligible **Protected Opposing Structural Extreme / Governing Opposing Range Boundary** is `CHoCH_ELIGIBLE` unless the tested external level carries **Major IDM provenance**. A Real Major IDM is therefore **not a positive prerequisite** for a wick-path CHoCH.

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

If the tested boundary is `FALLBACK_MAJOR_IDM`, the event is governed by 3.5.4 and is `MAJOR_IDM_SWEEP`, not CHoCH. The same exclusion applies whenever the tested external level has Major IDM provenance; a later reclassification must not be inferred from the wick geometry alone.

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

The source examples treat the LTF CHoCH trigger as a break of the governing LTF inducement/pullback reference. The canonical implementation route uses a **completed-candle close beyond that reference**:

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

This route does not create a new top-level lifecycle state and does not convert the LTF inducement into a Real Major IDM. The LTF reference is a temporary CHoCH reference object for the active context.

#### Non-equivalences

```text
HTF POI INTERACTION ≠ CHoCH
HTF CORE-LIQUIDITY TAKEOUT ≠ CHoCH
LTF VALID PULLBACK ≠ CHoCH
LTF INDUCEMENT SWEEP ≠ CHoCH
LTF CHoCH CONTEXT ≠ NEW LIFECYCLE STATE
LTF CHoCH REFERENCE ≠ REAL_MAJOR_IDM
```
### 3.5.4 — Fallback Major IDM / CHoCH Exception

When the tested opposing boundary carries `FALLBACK_MAJOR_IDM` provenance and the active lifecycle has not yet produced an independently qualified Real Major IDM, the proxy exception applies.

`FALLBACK_MAJOR_IDM` is a **temporary external proxy** for the governing opposing range boundary. It is not the same entity as `REAL_MAJOR_IDM` and is never directly converted into Real Major IDM.

#### A. Wick Breach of the Fallback Boundary

```text
FALLBACK_MAJOR_IDM
        +
WICK BREACH
        ↓
MAJOR_IDM_SWEEP
```

The event is strictly:

```text
NOT CHoCH_CONFIRMED
NOT VALID_BOS
NOT TRADING_RANGE_ROLLOVER
NOT PROTECTED_EXTREME_LOCK
```

The proxy sweep satisfies the applicable liquidity requirement and **unlocks the Confirmation Gate**, but it does not automatically create a CONFIRMED_STRUCTURAL_SWING; all remaining swing-confirmation prerequisites remain mandatory. Trend remains intact, with no CHoCH and no rollover.

#### B. Body Close Beyond the Fallback Boundary

```text
FALLBACK_MAJOR_IDM
        +
BODY CLOSE BEYOND BOUNDARY
        ↓
CHoCH_ELIGIBLE
```

A body close beyond the Fallback boundary enters the CHoCH qualification gate (`CHoCH_ELIGIBLE`). When all applicable structural prerequisites pass, it becomes `CHoCH_CONFIRMED`, producing a true trend reversal, regime shift, and terminating the old dealing range.

```text
BODY CLOSE
→ CHoCH_ELIGIBLE
→ ALL CHoCH PREREQUISITES
→ CHoCH_CONFIRMED (true trend reversal, regime shift, terminates old dealing range)
```

#### C. Fallback vs. Real Major IDM Lineage

The two provenance paths remain distinct:

```text
FIRST QUALIFYING POST-BREAK SVP
        ↓
VERIFIED PULLBACK EXTREME
        ↓
MAJOR IDM ELIGIBILITY
        ↓
REAL_MAJOR_IDM
        ↓
FALLBACK → SUPERSEDED
```

When the first genuine post-BOS Structurally Valid Pullback forms: `REAL_MAJOR_IDM` is created, `FALLBACK_MAJOR_IDM` is permanently `SUPERSEDED`, and the boundary reverts to a protected structural pivot.

Therefore:

```text
FALLBACK_MAJOR_IDM ≠ REAL_MAJOR_IDM
FALLBACK_MAJOR_IDM + WICK ≠ CHoCH_CONFIRMED
```

Anti-retroactive invariant:

```text
t1: MAJOR_IDM_SWEEP

t1+n: later candle

later candle ≠ retroactive CHoCH at t1
```

Every event is classified using the structural state active at its own event time.

### 3.5.5 — CHoCH Downstream State Changes & Post-CHoCH Dual Lineage

A `CHoCH_CONFIRMED` performs a multi-phase, asymmetric regime transition. The post-CHoCH lifecycle contains two distinct lineages: an **internal structural lineage** and an **external proxy lineage**.

```text
                        CHoCH_CONFIRMED
                              │
                  ┌───────────┴───────────┐
                  ▼                       ▼
         OLD REGIME TERMINATED     NEW REGIME INITIALIZED
                                          │
                               INITIAL_ACTIVE_IMPULSE
                                          │
                               CONFIRMATION_LOCKED
                                          │
               ┌──────────────────────────┴──────────────────────────┐
               ▼                                                     ▼
      INTERNAL LINEAGE                                      EXTERNAL PROXY LINEAGE
               │                                                     │
      FIRST_POST_CHOCH_SVP                                  GOVERNING OPPOSING
               │                                             RANGE BOUNDARY
               ▼                                                     │
   VERIFIED_PULLBACK_EXTREME                                          ▼
               │                                             FALLBACK_MAJOR_IDM
               ▼                                             (temporary proxy)
  FIRST_POST_CHOCH_MINOR_IDM                                          │
               │                                                     │
               └──────────────────────┬──────────────────────────────┘
                                      ▼
                            QUALIFYING IDM SWEEP
                                      │
                                      ▼
                        CONFIRMATION GATE UNLOCKED
                                      │
                                      ▼
                          CONFIRMED SWING QUALIFICATION
                                      │
                                      ▼
                                   FIRST BOS
                                      │
                                      ▼
                                POST-BOS SVP
                                      │
                                      ▼
                                REAL_MAJOR_IDM
                                      │
                                      ▼
                          FALLBACK → SUPERSEDED
```

#### Phase 1 — Old regime termination

The previous governing trend terminates immediately and the previous Trading Range is closed. Any POI expiration is handled through the separate POI lifecycle; the structural engine must not silently delete POI history.

#### Phase 2 — New trend initialization

Market bias switches to the new direction. The CHoCH-causing leg becomes the new trend's **initial active impulsive leg (`INITIAL_ACTIVE_IMPULSE`)**.

The CHoCH-causing leg is not itself an automatic Structurally Valid Pullback, IDM, CONFIRMED_STRUCTURAL_SWING, or Protected Structural Extreme.

#### Phase 3 — Confirmation lock

Immediately after CHoCH, the new trend is not yet a normal confirmed Dealing Range. Candidate detection remains allowed, but structural confirmation remains locked:

```text
Candidate Detection = ALLOWED
Confirmation Gate = LOCKED
```

No new `CONFIRMED_STRUCTURAL_SWING` and no new trend-direction `VALID_BOS` may be declared until the first qualifying **Structurally Valid Pullback (SVP)** forms on the new active leg and its IDM lifecycle is completed through the canonical liquidity/swing-confirmation gate.

#### Phase 4 — Internal lineage

The first qualifying post-CHoCH SVP provides the basis for the first Minor IDM of the new lifecycle:

```text
FIRST_POST_CHOCH_SVP
        ↓
VERIFIED_PULLBACK_EXTREME
        ↓
FIRST_POST_CHOCH_MINOR_IDM
```

The first post-CHoCH Minor IDM is distinct from the First Post-CHoCH SVP and is not a Real Major IDM.

#### Phase 5 — External proxy lineage

In parallel, the governing opposing external range boundary may carry temporary Fallback Major IDM provenance:

```text
GOVERNING OPPOSING RANGE BOUNDARY
        ↓
FALLBACK_MAJOR_IDM
```

This proxy exists to model the external liquidity condition before a new Real Major IDM is independently qualified. It does not become a Real Major IDM merely because it is swept.

#### Phase 6 — Confirmation Gate unlock

A qualifying sweep of the applicable post-CHoCH IDM lineage unlocks the **Confirmation Gate**. Gate unlock is a process condition, not a new lifecycle state enum.

```text
CONFIRMATION_LOCKED
        │
        ├─ FIRST_POST_CHOCH_MINOR_IDM sweep
        │
        └─ FALLBACK_MAJOR_IDM sweep
                 ↓
       CONFIRMATION GATE UNLOCKED
                 ↓
      CONFIRMED_STRUCTURAL_SWING QUALIFICATION
                 ↓
             FIRST BOS
```

Gate unlock does not automatically create a CONFIRMED_STRUCTURAL_SWING. All remaining swing-confirmation prerequisites remain mandatory.

#### Phase 7 — First BOS and Real Major IDM lifecycle

Once the first valid BOS establishes the new confirmed Dealing Range, the post-BOS lifecycle resumes the canonical Real Major IDM path:

```text
FIRST VALID BOS
        ↓
NEW CONFIRMED DEALING RANGE
        ↓
POST-BOS SVP
        ↓
VERIFIED PULLBACK EXTREME
        ↓
REAL_MAJOR_IDM
        ↓
FALLBACK_MAJOR_IDM → SUPERSEDED
```

The FALLBACK_MAJOR_IDM is therefore superseded by an independently qualified Real Major IDM; it is never retroactively reclassified as Real Major IDM.

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

FALLBACK_MAJOR_IDM + OPPOSING WICK BREAK
→ MAJOR_IDM_SWEEP
→ NOT CHoCH_CONFIRMED
→ NOT VALID_BOS
→ NOT TRADING_RANGE_ROLLOVER

FALLBACK_MAJOR_IDM + BODY CLOSE
→ CHoCH_ELIGIBLE
→ CHoCH_CONFIRMED only if all prerequisites pass (true trend reversal, regime shift)

FIRST_POST_CHOCH_SVP
≠ FIRST_POST_CHOCH_MINOR_IDM

FALLBACK_MAJOR_IDM
≠ REAL_MAJOR_IDM

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
→ POST-BOS REAL_MAJOR_IDM LIFECYCLE
```

This file is the detailed Section 3.5 module of `03_structural_semantic_authority.md`, not a separate lifecycle authority.
