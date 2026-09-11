# TRUE SMC — STRUCTURAL LIFECYCLE

**Role:** Canonical Layer 3 Structural Lifecycle authority for Major Structure, Genesis, Confirmed Swing / Protected Structural Extreme, BOS, and CHoCH.

**Authority:** This document owns the high-level Structural Lifecycle, Sections 3.1–3.5. Detailed BOS mechanics are maintained in `03_structural_lifecycle_bos.md`. Detailed CHoCH mechanics are maintained in `03_structural_lifecycle_choch.md`. Those modules are subordinate to this document and do not create competing lifecycle authorities.

**Validation status:** Sections 3.1–3.5 are methodologically validated and closed.

## Structural lifecycle invariant

Higher-level structural events may consume lower-level validated state, but no stage may be skipped or manufactured by configuration, scoring, visualization, or implementation convenience.

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
LIQUIDITY
  ↓
IDM ELIGIBILITY
  ↓
ACTIVE / MINOR IDM
  ↓
IDM LIQUIDITY TAKEOUT
  ↓
SWING CONFIRMATION GATE
  ↓
CONFIRMED STRUCTURAL SWING
  ↓
PHYSICAL EXTERNAL BREAK
  ↓
BREAK CLASSIFICATION
  ↓
BOS / CHoCH
```

Layer 1 and Layer 2 semantic foundations are owned by:

- `01_candle_level_foundation.md`
- `02_minor_structure.md`

The Structural Lifecycle begins once those validated prerequisites are available and owns the external structural state machine from Major Structure through CHoCH and post-regime initialization.

---

## 3.1 — Major Structure: Definition & Scope

Major Structure is the governing external structural framework defined strictly by the active Trading Range and its canonical external boundaries.

The governing range boundaries are derived from canonical external structural events and confirmed swing context. Internal Minor Structure, arbitrary local highs/lows, liquidity nodes, or IDM events cannot independently redefine the governing Trading Range.

A Confirmed Swing does not automatically become a Trading Range Boundary. A Protected Structural Extreme is a distinct structural state established through the canonical swing and break lifecycle.

```text
Major Structure
    ↓
Governing Trading Range
    ↓
External Structural Boundaries

Minor Structure / IDM / Internal Liquidity
    ≠
Governing Range Boundary
```

### Mandatory identity separation

```text
CONFIRMED SWING
≠ TRADING RANGE BOUNDARY

PROTECTED STRUCTURAL EXTREME
≠ ARBITRARY CONFIRMED SWING

MINOR STRUCTURE
≠ MAJOR STRUCTURE

IDM
≠ MAJOR STRUCTURE
```

**Verdict: PASS / CLOSED.**

---

## 3.2 — Genesis & Structural Unit of Origin

The unit of origin for Major Structure is not an isolated candlestick, fractal pivot, or raw price extreme. Major Structure originates from the complete **Confirmed Dealing Range Cycle**, anchored by liquidity-validated structural extremes.

A governing Trading Range does not exist merely because an impulse has occurred. It becomes formally established only when a qualified IDM liquidity takeout unlocks the Swing Confirmation Gate **and the subsequent canonical confirmation prerequisites establish a Confirmed Swing**. A liquidity sweep alone never establishes the range.

### 3.2.1 — Genesis / Bootstrap

Prior to the first confirmed IDM sweep, including chart inception or the initial active impulse following a valid CHoCH, the market resides in an unconfirmed expansion state such as `BOOTSTRAP_EXPANSION`.

In bootstrap:

- candle-level minor structures may form;
- candidate IDM structures may form;
- no governing dealing range is fabricated;
- no Confirmed Swing is manufactured without the required confirmation lifecycle.

Bootstrap must remain distinguishable from organically confirmed structure.

### 3.2.2 — Impulse Origin vs Protected Structural Extreme

An impulse origin is the physical price/time anchor where an expansion began. It does not automatically constitute a Protected Structural Extreme.

A Protected Structural Extreme is a later macro-state created and locked through valid BOS.

```text
QUALIFIED IDM
    ↓
IDM SWEEP
    ↓
SWING CONFIRMATION GATE
    ↓
CONFIRMED SWING
    ↓
VALID_BOS
    ↓
PROTECTED STRUCTURAL EXTREME
```

**Verdict: PASS / CLOSED.**

---

## 3.3 — Confirmed Swing & Protected Structural Extreme Lifecycle

### 3.3.1 — Ontological Asymmetry

```text
CONFIRMED SWING POINT
        ≠
PROTECTED STRUCTURAL EXTREME
```

A **Confirmed Swing Point** is established through the canonical Swing Confirmation Gate after the required qualified IDM liquidity takeout and all other applicable confirmation prerequisites.

A Confirmed Swing records the current expansion extreme and serves as the external structural landmark for the active lifecycle. It is not automatically protected.

A **Protected Structural Extreme** is a later lifecycle state created by valid BOS. It becomes the governing trend anchor for the resulting structural lifecycle.

### 3.3.2 — Dynamic Retracement & Sufficiency Gate

The corrective extreme is tracked dynamically across the complete corrective window from swing confirmation until BOS.

Bullish lifecycle:

```text
E_retrace(t) = min(Low_k)
```

Bearish lifecycle:

```text
E_retrace(t) = max(High_k)
```

The tracked extreme must not be frozen prematurely at a local pivot, IDM-sweeping candle, or internal microstructure point.

**Standard qualification path**

```text
>= 3 opposing candles
AND
>= configured minimum retracement depth
```

Canonical default minimum depth: **38.2%**.

**Exactly-two-candle exception**

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

If retracement sufficiency is not satisfied, the attempted continuation remains `IMPULSE_EXTENSION`; it does not create a new Protected Structural Extreme or roll the Trading Range.

The detailed retracement and BOS classification rules are owned by `02_minor_structure.md` and `03_structural_lifecycle_bos.md` respectively.

### 3.3.3 — Protected Structural Extreme Lock

The absolute corrective extreme remains dynamically tracked until the structural event that produces `VALID_BOS`.

```text
Retracement Sufficiency
        ↓
Dynamic E_retrace
        ↓
VALID_BOS
        ↓
E_retrace LOCKED
        ↓
Protected Structural Extreme
```

A valid wick BOS locks `E_retrace` immediately. No later body close is required.

If the penetrated external level is the Fallback Major IDM / Range-Boundary Proxy, the wick event is instead `MAJOR_IDM_SWEEP`; it is not BOS and does not lock `E_retrace`.

Detailed BOS locking mechanics are owned by `03_structural_lifecycle_bos.md`.

### 3.3.4 — Dealing Range Rollover & New Cycle

A valid BOS closes the previous governing Trading Range and starts a new structural lifecycle.

```text
VALID_BOS
   ↓
PREVIOUS RANGE CLOSED
   ↓
TRADING_RANGE_ROLLED_OVER
   ↓
NEW RANGE ACTIVE
```

Post-BOS retracement, internal liquidity collection, fallback-proxy handling, and subsequent displacement belong to the new lifecycle. A later event must not be interpreted as delayed acceptance of the preceding BOS.

POI expiration is handled through the separate POI lifecycle; the structural engine must not silently delete POI history.

**Verdict: PASS / CLOSED.**

---

# 3.4 — Break of Structure (BOS): Lifecycle Ownership

BOS is a macro structural continuation event. It is not a local candle pattern, arbitrary liquidity takeout, IDM sweep, or internal structural break.

The high-level BOS lifecycle is:

```text
ELIGIBLE CONFIRMED CONTINUATION SWING
        ↓
PHYSICAL EXTERNAL BREAK
        ↓
RETRACEMENT / STRUCTURAL GATES
        ↓
PROVENANCE / LEVEL IDENTITY
        ↓
BOS CLASSIFICATION
        ├── IMPULSE_EXTENSION
        ├── MAJOR_IDM_SWEEP (fallback)
        └── VALID_BOS
                ↓
        PROTECTED EXTREME LOCK
                ↓
        TRADING RANGE ROLLOVER
                ↓
        POST_BOS LIFECYCLE
```

### 3.4.1 — BOS Reference Ownership

Continuation BOS may reference only the eligible **Confirmed Structural Swing Point** of the active lifecycle:

- bullish lifecycle → Confirmed Swing High;
- bearish lifecycle → Confirmed Swing Low.

Minor Structure, provisional swings, IDM, liquidity pools, arbitrary local levels, and Protected Opposing Extremes are not continuation-BOS references.

If no eligible confirmed external swing exists, BOS evaluation is blocked.

### 3.4.2 — BOS Lifecycle Classification

A physical external break does not automatically equal `VALID_BOS`.

The continuation path requires:

1. correct external structural identity;
2. sufficient retracement according to the canonical qualification rules;
3. correct break provenance;
4. non-fallback status for the final BOS outcome.

Insufficient retracement produces `IMPULSE_EXTENSION` rather than BOS. A fallback-proxy wick breach produces `MAJOR_IDM_SWEEP` rather than BOS.

The detailed Section 3.4 mechanics, including body-close BOS, wick BOS, retracement matrix, fallback provenance, and anti-retroactive behavior, are owned by:

`03_structural_lifecycle_bos.md`

### 3.4.3 — BOS Downstream Lifecycle

Only `VALID_BOS` may:

- close the current governing Trading Range;
- lock the current dynamic corrective extreme as the Protected Structural Extreme;
- initialize the next structural lifecycle;
- initialize the temporary fallback Major IDM / Range-Boundary Proxy where applicable.

A physical break, Minor IDM sweep, Major IDM sweep, fallback proxy sweep, or `IMPULSE_EXTENSION` cannot independently roll the Trading Range.

### 3.4.4 — BOS State Boundary

BOS is a continuation transition. CHoCH is the opposing-regime transition.

```text
CONTINUATION EXTERNAL BREAK
        ↓
BOS LIFECYCLE

OPPOSING EXTERNAL BREAK
        ↓
CHoCH LIFECYCLE
```

The two are not interchangeable, and fallback-proxy events may resolve as `MAJOR_IDM_SWEEP` rather than either macro transition.

**Detailed authority:** `03_structural_lifecycle_bos.md`

**Verdict: PASS / CLOSED.**

---

# 3.5 — Change of Character (CHoCH): Lifecycle Ownership

CHoCH is the macro regime-reversal event. It is not an arbitrary local break, IDM sweep, liquidity interaction, or candle pattern.

The high-level CHoCH lifecycle is:

```text
ACTIVE TREND
    ↓
PROTECTED OPPOSING STRUCTURAL EXTREME
    ↓
PHYSICAL OPPOSING BREAK
    ↓
CHoCH ELIGIBILITY
    ↓
ALL CHoCH PREREQUISITES
    ↓
VALID_CHoCH
    ↓
OLD TREND TERMINATED
    ↓
NEW TREND INITIALIZED
    ↓
INITIAL ACTIVE IMPULSE
    ↓
CONFIRMATION LOCKED
    ↓
FIRST POST-CHoCH SVP
    ↓
MINOR IDM / CONFIRMATION LIFECYCLE
```

### 3.5.1 — CHoCH Reference Ownership

The normal CHoCH reference is the governing opposing Protected Structural Extreme / range boundary of the active lifecycle.

- bullish trend → protected opposing Swing Low;
- bearish trend → protected opposing Swing High.

An arbitrary local level, Minor IDM, liquidity pool, or provisional swing cannot independently create CHoCH.

### 3.5.2 — CHoCH Classification Ownership

A physical opposing break does not automatically equal `VALID_CHoCH`.

Body-close breaks enter the `CHoCH_ELIGIBLE` path and require all applicable CHoCH prerequisites.

Wick breaks require the applicable provenance and CHoCH prerequisites. A fallback-proxy wick breach is `MAJOR_IDM_SWEEP`, not CHoCH.

Detailed physical-break, body/wick, REAL_MAJOR_IDM, fallback, equality, exclusivity, and anti-retroactive rules are owned by:

`03_structural_lifecycle_choch.md`

### 3.5.3 — Post-CHoCH Lifecycle

A valid CHoCH produces a structural regime flip:

```text
OLD_TREND_TERMINATED
        ↓
NEW_TREND
        ↓
INITIAL_ACTIVE_IMPULSE
        ↓
CONFIRMATION_LOCKED
```

The CHoCH-causing leg becomes the initial active impulsive leg.

No new Confirmed Swing or BOS is created merely because CHoCH occurred. The first qualifying post-CHoCH SVP establishes the basis for the subsequent Minor IDM → sweep → Swing Confirmation lifecycle.

The first post-CHoCH SVP is not itself the first Minor IDM, and a fallback Major IDM is not internal liquidity. The fallback proxy remains an external range-boundary proxy until superseded through the validated Real Major IDM lifecycle.

A fallback Major IDM sweep unlocks the Swing Confirmation Gate but does not automatically create a Confirmed Swing.

### 3.5.4 — CHoCH / BOS Boundary

```text
CONTINUATION
    → BOS

OPPOSING REGIME BREAK
    → CHoCH

FALLBACK PROXY WICK BREACH
    → MAJOR_IDM_SWEEP
```

BOS and CHoCH are mutually exclusive outcomes for the same evaluated external event. `MAJOR_IDM_SWEEP` is also mutually exclusive with both macro outcomes.

**Detailed authority:** `03_structural_lifecycle_choch.md`

**Verdict: PASS / CLOSED.**

---

## Canonical Layer 3 Invariants

1. Layer 3 consumes validated Layer 1 and Layer 2 prerequisites; it does not redefine them.
2. Major Structure is governed by the active Trading Range and canonical external boundaries.
3. Minor Structure, IDM, arbitrary liquidity, and local extrema do not independently redefine Major Structure.
4. Confirmed Swing and Protected Structural Extreme are distinct lifecycle states.
5. Protected Structural Extreme is created by valid BOS, not by impulse origin or arbitrary swing confirmation.
6. Retracement sufficiency is mandatory before continuation BOS.
7. There is no automatic one-candle retracement exception.
8. Canonical default retracement depth is 38.2%.
9. Exactly-two-candle qualification requires high-momentum action and either >=5 prior candle extremes swept/engulfed or retracement depth >=38.2%.
10. Physical external break does not automatically equal BOS or CHoCH.
11. `MAJOR_IDM_SWEEP` is not BOS and not CHoCH.
12. Fallback Major IDM is an external range-boundary proxy, not Real Major IDM or arbitrary internal liquidity.
13. A fallback sweep unlocks the Swing Confirmation Gate but does not automatically create a Confirmed Swing.
14. `NEW_SVP` does not automatically create Real Major IDM.
15. Only `VALID_BOS` rolls the Trading Range and locks the Protected Structural Extreme.
16. A valid CHoCH initializes a new regime but does not itself create a new Confirmed Swing or BOS.
17. First post-CHoCH SVP and first post-CHoCH Minor IDM are distinct lifecycle states.
18. Structural event classification is anti-retroactive.
19. Detailed BOS mechanics are owned by `03_structural_lifecycle_bos.md`.
20. Detailed CHoCH mechanics are owned by `03_structural_lifecycle_choch.md`.
21. This document remains the single high-level Layer 3 Structural Lifecycle authority.

**Layer 3 verdict: PASS / CLOSED.**