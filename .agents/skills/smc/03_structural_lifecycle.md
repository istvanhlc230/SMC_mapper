# TRUE SMC — STRUCTURAL LIFECYCLE

**Role:** Canonical Layer 3 Structural Lifecycle authority for Major Structure, Genesis, Confirmed Swing / Protected Structural Extreme, BOS, and CHoCH.

**Authority:** This document owns the high-level Structural Lifecycle, Sections 3.1–3.5. Detailed BOS mechanics are maintained in `03_structural_lifecycle_bos.md`. Detailed CHoCH mechanics are maintained in `03_structural_lifecycle_choch.md`. Those modules are subordinate to this document and do not create competing lifecycle authorities.

## Structural lifecycle invariant

Higher-level structural events may consume lower-level validated state, but no stage may be skipped or manufactured by configuration, scoring, visualization, or implementation convenience.

```text
RAW OHLC
  ↓
CANDLE RELATIONSHIPS
  ↓
MINOR STRUCTURE
  ↓
CANDLE-LEVEL VALID PULLBACK
  ↓
VERIFIED PULLBACK EXTREME
  ↓
STRUCTURAL RETRACEMENT QUALIFICATION
  ↓
STRUCTURALLY VALID PULLBACK
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
CONFIRMED_STRUCTURAL_SWING
  ↓
PHYSICAL EXTERNAL BREAK
  ↓
BREAK CLASSIFICATION
  ↓
VALID_BOS / CHoCH_CONFIRMED
```

Layer 1 and Layer 2 semantic foundations are owned by:

- `01_candle_level_foundation.md`
- `02_minor_structure.md`

The Structural Lifecycle begins once those validated prerequisites are available and owns the external structural state machine from Major Structure through CHoCH and post-regime initialization.

---

## 3.1 — Major Structure: Definition & Scope

Major Structure is the governing external structural framework defined strictly by the active Trading Range and its canonical external boundaries.

The governing range boundaries are derived from canonical external structural events and confirmed swing context. Internal Minor Structure, arbitrary local highs/lows, liquidity nodes, or IDM events cannot independently redefine the governing Trading Range.

A CONFIRMED_STRUCTURAL_SWING does not automatically become a Trading Range Boundary. A Protected Structural Extreme is a distinct structural state established through the canonical swing and break lifecycle.

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
CONFIRMED_STRUCTURAL_SWING
≠ TRADING RANGE BOUNDARY

PROTECTED STRUCTURAL EXTREME
≠ ARBITRARY CONFIRMED_STRUCTURAL_SWING

MINOR STRUCTURE
≠ MAJOR STRUCTURE

IDM
≠ MAJOR STRUCTURE
```

---

## 3.2 — Genesis & Structural Unit of Origin

The unit of origin for Major Structure is not an isolated candlestick, fractal pivot, or raw price extreme. Major Structure originates from the complete **Confirmed Dealing Range Cycle**, anchored by liquidity-validated structural extremes.

A governing Trading Range does not exist merely because an impulse has occurred. It becomes formally established only when a qualified IDM liquidity takeout unlocks the SWING_CONFIRMATION_GATE **and the subsequent canonical confirmation prerequisites establish a CONFIRMED_STRUCTURAL_SWING**. A liquidity sweep alone never establishes the range.

### 3.2.1 — Genesis / Bootstrap

Prior to the first confirmed IDM sweep, including chart inception or the initial active impulse following a valid CHoCH_CONFIRMED, the market resides in an unconfirmed expansion state such as `BOOTSTRAP_EXPANSION`.

In bootstrap:

- candle-level minor structures may form;
- candidate IDM structures may form;
- no governing dealing range is fabricated;
- no CONFIRMED_STRUCTURAL_SWING is manufactured without the required confirmation lifecycle.

Bootstrap must remain distinguishable from organically confirmed structure.

### 3.2.2 — Impulse Origin vs Protected Structural Extreme

An impulse origin is the physical price/time anchor where an expansion began. It does not automatically constitute a Protected Structural Extreme.

A Protected Structural Extreme is a later macro-state created and locked through valid BOS.

```text
QUALIFIED IDM
    ↓
IDM SWEEP (Wick or Body: IDM_TAKEN = TRUE)
    ↓
SWING_CONFIRMATION_GATE UNLOCKED
    ↓
CONFIRMED_STRUCTURAL_SWING (Swing confirmed ONLY; not BOS, not CHoCH, no range rollover)
    ↓
CONSUME STORED QUALIFICATION (Depth >= 38.2% & candle count)
    ├─ NOT SATISFIED (Depth < 38.2%) → Break of Swing is IMPULSE_EXTENSION (Range remains open)
    └─ SATISFIED (Depth >= 38.2%)
            ↓
       STRUCTURAL_SWING_BREAK (Wick or Body)
            ↓
        VALID_BOS
            ↓
PROTECTED_STRUCTURAL_EXTREME_LOCK + TRADING_RANGE_ROLLOVER
```

---

## 3.3 — Confirmed Swing & Protected Structural Extreme Lifecycle

### 3.3.1 — Ontological Asymmetry

```text
CONFIRMED_STRUCTURAL_SWING
        ≠
PROTECTED STRUCTURAL EXTREME
```

A provisional Expansion Extreme becomes a **CONFIRMED_STRUCTURAL_SWING** when and only when the active IDM is taken out (`IDM_TAKEN = TRUE`). Wick or body penetration of the IDM level exclusively opens the `SWING_CONFIRMATION_GATE` and is sufficient to trigger IDM takeout; a candle body close beyond IDM is NOT required.

A CONFIRMED_STRUCTURAL_SWING records the current expansion extreme and serves as the external structural landmark for the active lifecycle. It is not automatically protected.

Crucially:
- IDM takeout confirms the swing ONLY.
- IDM takeout does NOT create a new Dealing Range.
- IDM takeout does NOT flip trend.
- IDM takeout is NEVER a CHoCH.
- IDM takeout does NOT create VALID_BOS.
- IDM takeout does NOT roll the dealing range.
- `CONFIRMED_STRUCTURAL_SWING ≠ VALID_BOS`. Having a CONFIRMED_STRUCTURAL_SWING is a necessary prerequisite for BOS, NOT BOS itself.

A **Protected Structural Extreme** is a later lifecycle state created by valid BOS. It becomes the governing trend anchor for the resulting structural lifecycle.

### 3.3.2 — Major Structural Retracement Qualification

This section is the single semantic owner of the major structural qualification rule. Other documents may consume or reference the result but must not redefine the criteria.

The corrective extreme is tracked dynamically across the complete corrective window from swing confirmation until BOS. This section is the canonical semantic owner of **major structural retracement qualification**. Layer 2 produces the candle-level Valid Pullback and verified pullback extreme; Layer 3 determines whether that retracement is structurally qualified.

Bullish lifecycle:

```text
E_retrace(t) = min(Low_k)
```

Bearish lifecycle:

```text
E_retrace(t) = max(High_k)
```

The tracked extreme must not be frozen prematurely at a local pivot, IDM-sweeping candle, or internal microstructure point.

**Opposing Candle Definition**

An "opposing candle" is defined strictly by candle direction / body direction relative to the active trend / dominant impulse:
- In a bullish trend (dominant upward impulse): an opposing candle is a bearish candle (`Close < Open`).
- In a bearish trend (dominant downward impulse): an opposing candle is a bullish candle (`Close > Open`).

Do NOT define opposing candles by displacement, directional movement, higher/lower extremes, or candle ranges. Candle color / body direction is the definitive criterion.

**Mandatory Macro BOS Retracement Gate (38.2%)**

The 38.2% retracement threshold is anchored strictly to the active Major Structure Dealing Range:
- **Bullish trend**: Dealing range from Protected Swing Low ($ProtectedLow$, impulse origin) to provisional Expansion High ($ExpansionHigh$, CONFIRMED_STRUCTURAL_SWING):
  $$\text{Retracement depth } R = \frac{ExpansionHigh - RetracementLow}{ExpansionHigh - ProtectedLow}$$
  $$\text{Threshold level } P_{38.2} = ExpansionHigh - 0.382 \times (ExpansionHigh - ProtectedLow)$$
  $$\text{Condition: } RetracementLow \le P_{38.2} \iff R \ge 0.382$$
- **Bearish trend**: Dealing range from Protected Swing High ($ProtectedHigh$, impulse origin) to provisional Expansion Low ($ExpansionLow$, CONFIRMED_STRUCTURAL_SWING):
  $$\text{Retracement depth } R = \frac{RetracementHigh - ExpansionLow}{ProtectedHigh - ExpansionLow}$$
  $$\text{Threshold level } P_{38.2} = ExpansionLow + 0.382 \times (ProtectedHigh - ExpansionLow)$$
  $$\text{Condition: } RetracementHigh \ge P_{38.2} \iff R \ge 0.382$$

Retracement depth $\ge 38.2\%$ is a **MANDATORY** gate for macro BOS. Without $\ge 38.2\%$ depth ($R \ge 0.382$), NO break of the expansion extreme can be classified as `VALID_BOS`.

**Standard qualification path**

```text
>= 3 OPPOSING CANDLES
AND
RETRACEMENT DEPTH >= 38.2% (R >= 0.382)
```

The canonical minimum depth is **38.2%**. Any configurable exposure of this numeric threshold belongs to `methodology_parameters.md` and must not alter the semantic ownership of this rule.

**Exactly-two-candle exception**

```text
EXACTLY 2 OPPOSING CANDLES
AND
RETRACEMENT DEPTH >= 38.2% (R >= 0.382)
```

**Retracement Depth Invariant:**
No heuristic, candle count sweep (such as sweeps of prior candle extremes), or safe mode may substitute for the 38.2% depth requirement in macro BOS qualification.

**Candle Count Rule:**
1 opposing candle is NEVER sufficient for macro BOS retracement qualification under any circumstances. There is NO 1-candle exception.

**CONFIRMED_STRUCTURAL_SWING ≠ VALID_BOS & IMPULSE_EXTENSION:**
VALID_BOS requires ALL of:
1. `IDM_TAKEN = TRUE` (swing is confirmed)
2. `RETRACEMENT_DEPTH >= 38.2%` (retracement sufficiency satisfied)
3. `STRUCTURAL_SWING_BREAK` (wick breach or body close beyond CONFIRMED_STRUCTURAL_SWING)

If IDM is taken out (`IDM_TAKEN = TRUE`), the provisional expansion extreme becomes a CONFIRMED_STRUCTURAL_SWING. However, if retracement depth is `< 38.2%` ($R < 0.382$):
- The swing remains confirmed.
- Retracement sufficiency is NOT satisfied.
- Any subsequent break of the CONFIRMED_STRUCTURAL_SWING is classified as `IMPULSE_EXTENSION`, NOT `VALID_BOS`.
- The dealing range remains OPEN (does not roll over).
- No new Protected Structural Extreme is established.

The detailed BOS break-classification mechanics are owned by `03_structural_lifecycle_bos.md`. That module consumes the structural qualification defined here and must not redefine its semantic criteria.

### 3.3.3 — Protected Structural Extreme Lock

The absolute corrective extreme remains dynamically tracked until the structural event that produces `VALID_BOS`.

```text
Retracement Sufficiency
        ↓
Dynamic E_retrace
        ↓
VALID_BOS
        ↓
PROTECTED_STRUCTURAL_EXTREME_LOCK (E_retrace LOCKED)
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
PROTECTED_STRUCTURAL_EXTREME_LOCK + TRADING_RANGE_ROLLOVER
   ↓
NEW RANGE ACTIVE
```

Post-BOS retracement, internal liquidity collection, fallback-proxy handling, and subsequent displacement belong to the new lifecycle. A later event must not be interpreted as delayed acceptance of the preceding BOS.

POI expiration is handled through the separate POI lifecycle; the structural engine must not silently delete POI history.

---

# 3.4 — Break of Structure (BOS): Lifecycle Ownership

BOS is a macro structural continuation event. It is not a local candle pattern, arbitrary liquidity takeout, IDM sweep, or internal structural break.

The canonical BOS lifecycle is:

```text
PHYSICAL EXTERNAL BREAK (Wick OR Body)
        ↓
STRUCTURAL_SWING_BREAK
        ↓
CONSUME STORED QUALIFICATION (IDM_TAKEN == True AND RETRACEMENT_DEPTH >= 0.382)
        ↓
COMPLETE BOS GATE SATISFIED
        ↓
VALID_BOS
        ↓
PROTECTED_STRUCTURAL_EXTREME_LOCK + TRADING_RANGE_ROLLOVER
```

The qualification result (`is_bos_qualified`) is established and tracked **before price returns to the BOS level**. The execution event strictly consumes the previously established qualification state. It is NOT a new BOS predicate. The canonical BOS predicate remains:

```text
VALID_BOS ⇔
    IDM_TAKEN
    AND RETRACEMENT_DEPTH >= 0.382
    AND STRUCTURAL_SWING_BREAK
```

- Physical wick breach of CONFIRMED_STRUCTURAL_SWING satisfies `STRUCTURAL_SWING_BREAK`.
- Physical body close beyond CONFIRMED_STRUCTURAL_SWING also satisfies `STRUCTURAL_SWING_BREAK`.
- Wick breach alone != `VALID_BOS`, Body close alone != `VALID_BOS`. Full qualification gate (`IDM_TAKEN == True AND RETRACEMENT_DEPTH >= 0.382`) is required.
- If `RETRACEMENT_DEPTH < 0.382` or `IDM_TAKEN == False`: external breach produces `IMPULSE_EXTENSION`, NOT `VALID_BOS` (no rollover, no protected extreme lock).
- No universal body-close requirement exists for continuation BOS.

### Fallback Major IDM & Continuation Distinction

`EXT_CONT_BREAK` is exclusively the continuation path for a confirmed continuation external swing.

`FALLBACK_MAJOR_IDM` is an opposing-boundary external proxy and must not be an outcome or provenance branch of `EXT_CONT_BREAK`:
- Wick breach past Fallback Boundary produces `MAJOR_IDM_SWEEP`, unlocks gate, trend intact, no CHoCH, no rollover.
- Body close past Fallback Boundary produces `CHoCH_ELIGIBLE` -> `CHoCH_CONFIRMED`, true trend reversal, regime shift, terminates old dealing range.
- When first genuine post-BOS Structurally Valid Pullback forms: `REAL_MAJOR_IDM` is created, `FALLBACK_MAJOR_IDM` is permanently `SUPERSEDED`, and boundary reverts to protected structural pivot.

### 3.4.1 — BOS Reference Ownership

Continuation BOS may reference only the eligible **CONFIRMED_STRUCTURAL_SWING** of the active lifecycle:

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

---

# 3.5 — Change of Character (CHoCH): Lifecycle Ownership

CHoCH is the macro regime-reversal event. It is not an arbitrary local break, IDM sweep, liquidity interaction, or candle pattern.

The canonical CHoCH lifecycle is:

```text
OPPOSING STRUCTURAL BOUNDARY VIOLATION (Body Close)
        ↓
CHoCH_ELIGIBLE
        ↓
CHoCH_CONFIRMED
        ↓
OLD TREND TERMINATED + INITIAL ACTIVE IMPULSE INITIALIZED
```

### 3.5.1 — CHoCH Reference Ownership

The normal CHoCH reference is the governing opposing Protected Structural Extreme / range boundary of the active lifecycle.

- bullish trend → protected opposing Swing Low;
- bearish trend → protected opposing Swing High.

An arbitrary local level, Minor IDM, liquidity pool, or provisional swing cannot independently create CHoCH.

### 3.5.2 — CHoCH Classification Ownership

A physical opposing break does not automatically equal `CHoCH_CONFIRMED`.

Body-close breaks enter the `CHoCH_ELIGIBLE` path and require all applicable CHoCH prerequisites before becoming `CHoCH_CONFIRMED`.

Wick breaks require the applicable provenance and CHoCH prerequisites:
- A fallback-proxy wick breach is `MAJOR_IDM_SWEEP`, not CHoCH.
- A wick break of a protected opposing boundary with an independently formed `REAL_MAJOR_IDM` is `CHoCH_ELIGIBLE` and becomes `CHoCH_CONFIRMED` only after all prerequisites pass.

Detailed physical-break, body/wick, REAL_MAJOR_IDM, fallback, equality, exclusivity, and anti-retroactive rules are owned by:

`03_structural_lifecycle_choch.md`

### 3.5.3 — Post-CHoCH Lifecycle

A valid `CHoCH_CONFIRMED` produces a structural regime flip:

```text
OPPOSING STRUCTURAL BOUNDARY VIOLATION (Body Close)
        ↓
CHoCH_ELIGIBLE
        ↓
CHoCH_CONFIRMED
        ↓
OLD TREND TERMINATED + INITIAL ACTIVE IMPULSE INITIALIZED
```

The CHoCH-causing leg becomes the initial active impulsive leg.

No new CONFIRMED_STRUCTURAL_SWING or BOS is created merely because CHoCH occurred. The first qualifying post-CHoCH SVP establishes the basis for the subsequent Minor IDM → sweep → Swing Confirmation lifecycle.

The first post-CHoCH SVP is not itself the first Minor IDM, and a fallback Major IDM is not internal liquidity. The fallback proxy remains an external range-boundary proxy until superseded through the validated Real Major IDM lifecycle.

A fallback Major IDM sweep unlocks the Swing Confirmation Gate but does not automatically create a CONFIRMED_STRUCTURAL_SWING.

### 3.5.4 — CHoCH / BOS Boundary

```text
CONTINUATION
    → BOS
    → VALID_BOS

OPPOSING REGIME BREAK
    → CHoCH
    → CHoCH_CONFIRMED

FALLBACK PROXY WICK BREACH
    → MAJOR_IDM_SWEEP
```

BOS and CHoCH are mutually exclusive outcomes for the same evaluated external event. `MAJOR_IDM_SWEEP` is also mutually exclusive with both macro outcomes.

**Detailed authority:** `03_structural_lifecycle_choch.md`

---

## Canonical Layer 3 Invariants

1. Layer 3 consumes validated Layer 1 and Layer 2 prerequisites; it does not redefine them.
2. Major Structure is governed by the active Trading Range and canonical external boundaries.
3. Minor Structure, IDM, arbitrary liquidity, and local extrema do not independently redefine Major Structure.
4. CONFIRMED_STRUCTURAL_SWING and Protected Structural Extreme are distinct lifecycle states.
5. Protected Structural Extreme is created by valid BOS, not by impulse origin or arbitrary swing confirmation.
6. Retracement sufficiency is mandatory before continuation BOS.
7. There is no automatic one-candle retracement exception.
8. Canonical default retracement depth is 38.2%.
9. Exactly-two-candle qualification requires retracement depth >= 38.2%; no prior candle extreme sweep may substitute for the depth requirement.
10. Physical external break does not automatically equal VALID_BOS or CHoCH_CONFIRMED.
11. `MAJOR_IDM_SWEEP` is not VALID_BOS and not CHoCH_CONFIRMED.
12. Fallback Major IDM is an external range-boundary proxy, not Real Major IDM or arbitrary internal liquidity.
13. A fallback sweep unlocks the Swing Confirmation Gate but does not automatically create a CONFIRMED_STRUCTURAL_SWING.
14. `NEW_SVP` does not automatically create Real Major IDM.
15. Only `VALID_BOS` rolls the Trading Range and locks the Protected Structural Extreme.
16. `CHoCH_CONFIRMED` initializes a new regime but does not itself create a new CONFIRMED_STRUCTURAL_SWING or VALID_BOS.
17. First post-CHoCH SVP and first post-CHoCH Minor IDM are distinct lifecycle states.
18. Structural event classification is anti-retroactive.
19. Detailed BOS mechanics are owned by `03_structural_lifecycle_bos.md`.
20. Detailed CHoCH mechanics are owned by `03_structural_lifecycle_choch.md`.
21. This document remains the single high-level Layer 3 Structural Lifecycle authority.