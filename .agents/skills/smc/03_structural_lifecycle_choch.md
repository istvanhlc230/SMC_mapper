# TRUE SMC — CHoCH MECHANICS

**Role:** Detailed Section 3.5 CHoCH lifecycle module of `03_structural_lifecycle.md`.

**Authority:** This document contains the validated and closed True SMC CHoCH mechanics in Sections 3.5.1–3.5.5. It is the detailed mechanics authority for CHoCH classification and post-CHoCH regime initialization within the Structural Lifecycle. It does **not** create a separate top-level methodology category or separate lifecycle ownership.

**Lifecycle ownership:** `03_structural_lifecycle.md` owns Section 3.5 as part of the complete Layer 3 Structural Lifecycle. This document provides the detailed deterministic rules used by that lifecycle.

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

When the tested opposing boundary carries `FALLBACK_MAJOR_IDM` provenance and the active lifecycle has not yet produced an independently qualified Real Major IDM, the proxy wick exception applies.

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

The proxy sweep satisfies the liquidity requirement and unlocks the Swing Confirmation Gate, but it does not automatically create a Confirmed Swing; all remaining swing-confirmation prerequisites remain mandatory.

A body close beyond an opposing fallback boundary is geometrically eligible for CHoCH, but `VALID_CHoCH` still requires the complete applicable CHoCH prerequisite gate. A body close is not a license to manufacture CHoCH from an arbitrary level.

Fallback Proxy is never directly converted into Real Major IDM. Its lifecycle is:

```text
First Qualifying Post-Break SVP
        ↓
Verified Pullback Extreme
        ↓
Major IDM Eligibility
        ↓
REAL_MAJOR_IDM
        ↓
FALLBACK → SUPERSEDED
```

Anti-retroactive invariant:

```text
t1: MAJOR_IDM_SWEEP

t1+n: later candle

later candle ≠ retroactive CHoCH at t1
```

Every event is classified using the structural state active at its own event time.

**Verdict: PASS / CLOSED.**

### 3.5.5 — CHoCH Downstream State Changes & Regime Initialization

A `VALID_CHoCH` performs a multi-phase, asymmetric regime transition:

```text
VALID_CHoCH
    ↓
OLD_TREND_TERMINATED
    ↓
NEW_TREND
    ↓
INITIAL_ACTIVE_IMPULSE
    ↓
CONFIRMATION_LOCKED / WAITING_FOR_SVP
```

#### Phase 1 — Old regime termination

The previous governing trend terminates immediately and the previous Trading Range is closed. Any POI expiration is handled through the separate POI lifecycle; the structural engine must not silently delete POI history.

#### Phase 2 — New trend initialization

Market bias switches to the new direction.

#### Phase 3 — CHoCH-causing leg

The leg that physically causes the CHoCH becomes the new trend's **initial active impulsive leg (`INITIAL_ACTIVE_IMPULSE`)**. Its origin is the physical price/time anchor from which that reversal expansion began.

The CHoCH-causing leg is not itself an automatic Structurally Valid Pullback or IDM.

#### Phase 4 — Confirmation lock

Immediately after CHoCH, the new trend is not yet a normal confirmed Dealing Range. Candidate detection remains allowed, but structural confirmation remains locked:

```text
Candidate Detection = ALLOWED
Confirmation Gate = LOCKED
```

No new `CONFIRMED_SWING_POINT` and no new trend-direction `VALID_BOS` may be declared until the first qualifying **Structurally Valid Pullback (SVP)** forms on the new active leg and its IDM lifecycle is completed through the canonical liquidity/swing-confirmation gate.

The first qualifying post-CHoCH SVP provides the basis for the first Minor IDM of the new lifecycle. Once that active Minor IDM is swept and all Swing Confirmation prerequisites are satisfied, the confirmation lock is released and the first Confirmed Swing / new Trading Range can be established.

```text
VALID_CHoCH
    ↓
INITIAL_ACTIVE_IMPULSE
    ↓
CONFIRMATION_LOCKED
    ↓
FIRST STRUCTURALLY VALID PULLBACK
    ↓
MINOR IDM
    ↓
IDM SWEEP
    ↓
CONFIRMED SWING
    ↓
NEW TRADING RANGE
    ↓
NORMAL BOS LIFECYCLE
```

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

LATER CANDLE
≠ RETROACTIVE CLASSIFICATION

VALID_CHoCH
→ NEW TREND
→ CONFIRMATION LOCK
→ FIRST NEW SVP / IDM CYCLE
→ CONFIRMED SWING
→ NORMAL BOS LIFECYCLE
```

This file is the detailed Section 3.5 module of `03_structural_lifecycle.md`, not a separate lifecycle authority.
