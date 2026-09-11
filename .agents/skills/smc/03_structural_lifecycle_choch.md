# TRUE SMC — CHoCH MECHANICS

**Role:** Detailed Section 3.5 CHoCH lifecycle module of `03_structural_lifecycle.md`.

**Authority:** This document contains the validated and closed True SMC CHoCH mechanics in Sections 3.5.1–3.5.5. It is the detailed mechanics authority for CHoCH classification and post-CHoCH regime initialization within the Structural Lifecycle. It does **not** create a separate top-level methodology category or separate lifecycle ownership.

**Lifecycle ownership:** `03_structural_lifecycle.md` owns Section 3.5 as part of the complete Layer 3 Structural Lifecycle. This document provides the detailed deterministic rules used by that lifecycle.

**Methodology:** CLOSED / CANONICAL BASELINE  
**Implementation:** CONDITIONAL / AUDIT OPEN  
**Data Feed:** OHLC Intrabar Ambiguity recognized as an Implementation Limitation  
**Safe-Mode Guard:** ACTIVE (Momentum exceptions & OF failure triggers isolated)

**Validation status:** Sections 3.5.1–3.5.5 are methodologically validated and closed. No implementation change is implied by this document.

## 3.5 — Change of Character (CHoCH) Mechanics

CHoCH is a governing trend-reversal transition. It is not an arbitrary internal break, liquidity event, IDM sweep, or candle pattern.

### 3.5.1 — Unit of Origin

The eligible CHoCH reference object is the active Dealing Range's **Protected Opposing Structural Extreme / Governing Opposing Range Boundary**.

- Bullish lifecycle → Protected Swing Low.
- Bearish lifecycle → Protected Swing High.

Minor Structure, arbitrary local highs/lows, IDM levels, liquidity nodes, and continuation Confirmed Swings cannot independently create CHoCH.

```text
Protected Opposing Structural Extreme
        ↓
CHoCH Physical-Break Gate
```

A physical violation only opens the CHoCH classification gate; it does not itself establish `VALID_CHoCH`.

**Verdict: PASS / CLOSED.**

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
VALID_CHoCH
```

This gate records only the physical occurrence of the break. Final classification is determined by 3.5.3 and the Fallback Major IDM exception in 3.5.4.

**Verdict: PASS / CLOSED.**

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

A body close beyond an eligible Protected Opposing Boundary is a CHoCH-eligible event. It becomes `VALID_CHoCH` only when **all applicable CHoCH prerequisites** pass. A body close alone is never sufficient to manufacture CHoCH, and the result does not depend on an internal Major IDM being present.

#### B. Wick-Break Reversal

Bullish:

```text
Low_t < Protected_Swing_Low
AND
Close_t >= Protected_Swing_Low
```

Bearish:

```text
High_t > Protected_Swing_High
AND
Close_t <= Protected_Swing_High
```

A wick break is `CHoCH_ELIGIBLE` only when the active Dealing Range contains an independently formed **REAL_MAJOR_IDM**. It becomes `VALID_CHoCH` only when all applicable CHoCH prerequisites also pass.

```text
REAL_MAJOR_IDM
+
OPPOSING WICK BREAK
+
ALL CHoCH PREREQUISITES
        ↓
VALID_CHoCH
```

If the tested boundary is instead the Fallback Major IDM / Range-Boundary Proxy, the event is governed by 3.5.4 and is `MAJOR_IDM_SWEEP`, not CHoCH.

The wick/body geometry does not determine structural identity by itself. Level provenance and the active liquidity state determine the final classification.

**Verdict: PASS / CLOSED.**

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
NOT VALID_CHoCH
NOT VALID_BOS
NOT TRADING_RANGE_ROLLOVER
NOT PROTECTED_EXTREME_LOCK
```

The proxy sweep satisfies the applicable liquidity requirement and **unlocks the Confirmation Gate**, but it does not automatically create a Confirmed Swing; all remaining swing-confirmation prerequisites remain mandatory.

#### B. Body Close Beyond the Fallback Boundary

```text
FALLBACK_MAJOR_IDM
        +
BODY CLOSE BEYOND BOUNDARY
        ↓
CHoCH_ELIGIBLE
```

A body close beyond the Fallback boundary is **not** automatically `CHoCH_CONFIRMED` and does not by itself establish `VALID_CHoCH`. It enters the CHoCH qualification gate, where all applicable structural prerequisites must pass.

```text
BODY CLOSE
→ CHoCH_ELIGIBLE
→ ALL CHoCH PREREQUISITES
→ VALID_CHoCH only if prerequisites pass
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

Therefore:

```text
FALLBACK_MAJOR_IDM ≠ REAL_MAJOR_IDM
FALLBACK_PROXY + WICK ≠ CHoCH
```

Anti-retroactive invariant:

```text
t1: MAJOR_IDM_SWEEP

t1+n: later candle

later candle ≠ retroactive CHoCH at t1
```

Every event is classified using the structural state active at its own event time.

**Verdict: PASS / CLOSED.**

### 3.5.5 — CHoCH Downstream State Changes & Post-CHoCH Dual Lineage

A `VALID_CHoCH` performs a multi-phase, asymmetric regime transition. The post-CHoCH lifecycle contains two distinct lineages: an **internal structural lineage** and an **external fallback-proxy lineage**.

```text
                         VALID_CHoCH
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

The CHoCH-causing leg is not itself an automatic Structurally Valid Pullback, IDM, Confirmed Swing, or Protected Structural Extreme.

#### Phase 3 — Confirmation lock

Immediately after CHoCH, the new trend is not yet a normal confirmed Dealing Range. Candidate detection remains allowed, but structural confirmation remains locked:

```text
Candidate Detection = ALLOWED
Confirmation Gate = LOCKED
```

No new `CONFIRMED_SWING_POINT` and no new trend-direction `VALID_BOS` may be declared until the first qualifying **Structurally Valid Pullback (SVP)** forms on the new active leg and its IDM lifecycle is completed through the canonical liquidity/swing-confirmation gate.

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
      Confirmed Swing Qualification
                 ↓
             FIRST BOS
```

Gate unlock does not automatically create a Confirmed Swing. All remaining swing-confirmation prerequisites remain mandatory.

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
FALLBACK_PROXY → SUPERSEDED
```

The Fallback proxy is therefore superseded by an independently qualified Real Major IDM; it is never retroactively reclassified as Real Major IDM.

**Verdict: PASS / CLOSED.**

## 3.5 Canonical invariants

```text
PHYSICAL OPPOSING BREAK
≠ AUTOMATIC CHoCH

BODY CLOSE
→ CHoCH_ELIGIBLE
→ VALID_CHoCH only if all prerequisites pass

REAL_MAJOR_IDM + OPPOSING WICK BREAK
+ ALL CHoCH PREREQUISITES
→ VALID_CHoCH

FALLBACK_MAJOR_IDM + OPPOSING WICK BREAK
→ MAJOR_IDM_SWEEP
→ NOT CHoCH
→ NOT BOS
→ NOT TRADING_RANGE_ROLLOVER

FALLBACK_MAJOR_IDM + BODY CLOSE
→ CHoCH_ELIGIBLE
→ NOT AUTOMATIC CHoCH_CONFIRMED

FIRST_POST_CHOCH_SVP
≠ FIRST_POST_CHOCH_MINOR_IDM

FALLBACK_MAJOR_IDM
≠ REAL_MAJOR_IDM

CONFIRMATION GATE UNLOCKED
≠ NEW STATE ENUM

LATER CANDLE
≠ RETROACTIVE CLASSIFICATION

VALID_CHoCH
→ NEW TREND
→ INITIAL_ACTIVE_IMPULSE
→ CONFIRMATION_LOCKED
→ POST-CHOCH SVP / IDM LINEAGE
→ CONFIRMED SWING QUALIFICATION
→ FIRST BOS
→ POST-BOS REAL_MAJOR_IDM LIFECYCLE
```

This file is the detailed Section 3.5 module of `03_structural_lifecycle.md`, not a separate lifecycle authority.
