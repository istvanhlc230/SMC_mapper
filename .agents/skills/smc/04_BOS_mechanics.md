# TRUE SMC — BOS MECHANICS

**Role:** Detailed Section 3.4 BOS mechanics module under the canonical Layer 3 Structural Lifecycle authority.

**Authority:** `03_structural_semantic_authority.md` remains the Layer 3 lifecycle authority. This document owns the detailed mechanics of Section 3.4 only. It is subordinate to Layer 3 and must not create a competing structural-lifecycle category.

## 3.4 — Break of Structure (BOS) Mechanics

BOS is a macro structural continuation event. It is not a local candle pattern, arbitrary liquidity takeout, IDM sweep, or internal structural break.

### Canonical BOS Lifecycle

```text
PHYSICAL EXTERNAL BREAK (Wick OR Body)
        ↓
STRUCTURAL_SWING_BREAK
        ↓
CONSUME STORED MAJOR-RETRACEMENT QUALIFICATION FROM LAYER 3
        ↓
COMPLETE BOS GATE SATISFIED
        ↓
VALID_BOS
        ↓
PROTECTED_STRUCTURAL_EXTREME_LOCK + TRADING_RANGE_ROLLOVER
```

### 3.4.1 — BOS Reference Identity

The only legitimate continuation-BOS reference object is an eligible **CONFIRMED_STRUCTURAL_SWING** of the active lifecycle:

- bullish lifecycle → Confirmed Swing High;
- bearish lifecycle → Confirmed Swing Low.

The following are not continuation-BOS references:

- Minor Structure;
- provisional swings;
- IDM;
- liquidity pools;
- arbitrary local highs/lows;
- Protected Opposing Extremes.

If no eligible confirmed external swing exists, BOS evaluation is blocked.

```text
CONFIRMED_STRUCTURAL_SWING
        ↓
Eligible BOS Reference
```

### 3.4.2 — Physical External Break

A Physical External Break occurs when price physically penetrates the governing external level of an eligible CONFIRMED_STRUCTURAL_SWING.

Bullish:

```text
High_t > Confirmed_Swing_High
```

Bearish:

```text
Low_t < Confirmed_Swing_Low
```

The penetration may occur through wick/shadow or candle body. Both physical wick breach and physical body close beyond CONFIRMED_STRUCTURAL_SWING satisfy `STRUCTURAL_SWING_BREAK`.

A physical external break does **not** itself establish `VALID_BOS`, Trading Range rollover, or Protected Structural Extreme locking. It opens the break-classification path.

Mandatory prerequisites remain:

1. Layer 3 has produced a qualified major-retracement result;
2. `IDM_TAKEN == True` (swing confirmation gate satisfied);
3. the reference has correct external structural identity;
4. the broken level is not the applicable FALLBACK_MAJOR_IDM;
5. the final break classification satisfies 3.4.3.

If an external continuation break occurs before the Layer 3 qualification result is satisfied or before `IDM_TAKEN == True`:

```text
EXT_CONT_BREAK
+
RETRACEMENT_SUFFICIENCY = NOT_SATISFIED (or IDM_TAKEN == False)
        ↓
IMPULSE_EXTENSION
```

No `VALID_BOS` is created and the current structural lifecycle remains active (no rollover, no protected extreme lock).

### 3.4.3 — Qualification Phase vs Execution Phase

The structural lifecycle explicitly separates the temporal **Qualification Phase** from the **Execution Phase**.

#### 1. Qualification Phase

Qualification occurs *before* price returns to the BOS level. Layer 3 dynamically evaluates the major retracement and structural qualification using its canonical semantic owner rules.

```text
IDM_TAKEN
→ CONFIRMED_STRUCTURAL_SWING
→ LAYER 3 RETRACEMENT / STRUCTURAL QUALIFICATION
→ STORED QUALIFICATION RESULT
```

The canonical qualification rules are defined once in 03_structural_semantic_authority.md. This module consumes the stored result and does not reproduce the opposing-candle, displacement-outlier, higher-timeframe, or retracement-depth rules.

The qualification result (`is_bos_qualified`) is stored state. It is **not** a new BOS predicate. It is strictly the result of the preceding qualification phase.

#### 2. Execution Phase

Execution occurs when price later returns to the structural level. The engine does *not* recompute the opposing-candle qualification from scratch at the physical break moment. It evaluates the already established stored qualification.

```text
price returns to structural level
→ PHYSICAL_EXTERNAL_BREAK (Wick OR Body)
→ STRUCTURAL_SWING_BREAK
→ CONSUME STORED LAYER 3 QUALIFICATION
→
    ├── COMPLETE BOS GATE SATISFIED → VALID_BOS → PROTECTED_STRUCTURAL_EXTREME_LOCK + TRADING_RANGE_ROLLOVER
    └── DISQUALIFIED → IMPULSE_EXTENSION
```

Only `VALID_BOS` triggers Protected Structural Extreme Lock and Trading Range Rollover.

### 3.4.4 — Canonical Break Classification

`EXT_CONT_BREAK` exclusively represents a confirmed continuation swing break. Fallback Major IDM is an opposing-boundary proxy and must not be evaluated under the continuation path.

The validated continuation pipeline is:

```text
EXT_CONT_BREAK
        ↓
STORED LAYER 3 QUALIFICATION
        ├── NOT QUALIFIED
        │       ↓
        │  IMPULSE_EXTENSION (Dealing range remains open)
        │
        └── QUALIFIED
                ↓
           VALID_BOS (Dealing range rolls over, Protected Structural Extreme locks)
```


### 3.4.4.1 — CONFIRMED_STRUCTURAL_SWING ≠ VALID_BOS

Having a CONFIRMED_STRUCTURAL_SWING via IDM takeout (`IDM_TAKEN = TRUE`) is a prerequisite for BOS, NOT BOS itself.

`VALID_BOS` requires ALL of:
1. `IDM_TAKEN = TRUE` (swing is confirmed via wick or body takeout)
2. `MAJOR_RETRACEMENT_QUALIFIED = TRUE` (Layer 3 stored qualification result)
3. `STRUCTURAL_SWING_BREAK` (physical wick breach or body close beyond CONFIRMED_STRUCTURAL_SWING)

If IDM is taken out but Layer 3 has not produced MAJOR_RETRACEMENT_QUALIFIED:
- The swing remains confirmed.
- Macro retracement qualification is not satisfied.
- Any subsequent break of the CONFIRMED_STRUCTURAL_SWING is classified as IMPULSE_EXTENSION, NOT VALID_BOS.
- The dealing range remains OPEN (does not roll over).
- No new protected extreme is established.

Therefore:

```text
EXT_CONT_BREAK ≠ VALID_BOS
IMPULSE_EXTENSION ≠ EVENT CLASS
MAJOR_IDM_SWEEP ≠ VALID_BOS
```

The classification is based on structural role and provenance, not geometry alone.

### 3.4.5 — Canonical Break Classification: Wick vs Body (MC-01)

The canonical True SMC implementation distinguishes strictly between continuation boundaries and opposing boundaries. The earlier basic/pedagogical model requiring a body close for all BOS events is NOT a universal implementation rule and is superseded by this specification.

#### 1. Continuation External Boundary (CONFIRMED_STRUCTURAL_SWING)

When price breaks a confirmed continuation external swing, physical wick penetration immediately establishes the `STRUCTURAL_SWING_BREAK` mechanism when the continuation external boundary is an eligible structural level.

It does NOT by itself establish `VALID_BOS`.

* Wick penetration is sufficient for the structural break mechanism;
* Physical body close beyond CONFIRMED_STRUCTURAL_SWING also satisfies `STRUCTURAL_SWING_BREAK`;
* Body close is NOT additionally required for continuation BOS;
* Wick penetration alone != `VALID_BOS`, Body close alone != `VALID_BOS`. Full qualification gate (`IDM_TAKEN == True AND RETRACEMENT_DEPTH >= 0.382`) is required;
* If `RETRACEMENT_DEPTH < 0.382` or `IDM_TAKEN == False`: external breach produces `IMPULSE_EXTENSION`, NOT `VALID_BOS` (no rollover, no protected extreme lock);
* Only the completed canonical `VALID_BOS` causes Trading Range rollover and Protected Structural Extreme locking.

**Canonical Rule:**
```text
Continuation External Boundary
+
Physical Wick Breach OR Body Close
→ STRUCTURAL_SWING_BREAK

THEN:

IDM_TAKEN
+
RETRACEMENT_DEPTH >= 0.382
+
STRUCTURAL_SWING_BREAK
→ VALID_BOS
```

#### 2. Context-Dependent Wick Disambiguation

The parser MUST NOT apply the generic logic: "Wick = always sweep". The interpretation of a wick breach is structural-context dependent. Do not collapse these four cases:

**Canonical Disambiguation Matrix:**

1. **Continuation External Boundary / CONFIRMED_STRUCTURAL_SWING (`EXT_CONT_BREAK`)**
   * Wick breach → `STRUCTURAL_SWING_BREAK` (→ `VALID_BOS` only if the complete macro BOS qualification gate is satisfied).
2. **Opposing Protected Boundary WITH an independently formed REAL_MAJOR_IDM (`EXT_OPP_INTERACTION`)**
   * Wick breach → `CHoCH_ELIGIBLE` (→ `CHoCH_CONFIRMED` only after all applicable macro CHoCH prerequisites pass).
3. **Opposing Boundary functioning as FALLBACK_MAJOR_IDM (`EXT_OPP_INTERACTION`)**
   * Wick breach → `MAJOR_IDM_SWEEP` (unlocks gate, trend remains unchanged, no CHoCH, no rollover, no protected extreme lock).
4. **Opposing Protected Boundary / Fallback Boundary**
   * Body Close → `CHoCH_ELIGIBLE` (→ `CHoCH_CONFIRMED`, true trend reversal, regime shift, terminates old dealing range. Requires all applicable macro CHoCH prerequisites).

### 3.4.7 — FALLBACK_MAJOR_IDM

Fallback Major IDM is ALWAYS an **opposing-boundary proxy**. It belongs under the opposing-boundary interaction path (`EXT_OPP_INTERACTION`), not under `EXT_CONT_BREAK`. It is a temporary lifecycle-specific external proxy used after a confirmed macro event while the new expansion has not yet produced an independently qualified Real Major IDM from a post-break Structurally Valid Pullback.

```text
FALLBACK_MAJOR_IDM
≠ REAL_MAJOR_IDM
≠ INTERNAL_LIQUIDITY
```

It bridges the early-range liquidity/reference gap and is not a direct Real Major IDM substitute.

#### Proxy wick breach

Bullish:

```text
High_t > Level
AND
Close_t <= Level
```

Bearish:

```text
Low_t < Level
AND
Close_t >= Level
```

Classification:

```text
MAJOR_IDM_SWEEP
```

The event is terminal for the current evaluation:

```text
MAJOR_IDM_SWEEP
≠ VALID_BOS
≠ CHoCH_CONFIRMED
≠ TRADING_RANGE_ROLLOVER
≠ PROTECTED_EXTREME_LOCK
```

The sweep unlocks the Swing Confirmation Gate but does **not** automatically create a CONFIRMED_STRUCTURAL_SWING. All remaining swing-confirmation prerequisites remain mandatory.

#### Proxy body close through opposing boundary

A body close through a fallback opposing boundary is geometrically eligible for the CHoCH pipeline (`CHoCH_ELIGIBLE`). It becomes `CHoCH_CONFIRMED` only when all applicable Section 3.5 prerequisites pass, producing a true trend reversal, regime shift, and terminating the old dealing range.

#### Fallback lifecycle

Fallback does not convert directly into Real Major IDM:

```text
First Qualifying Post-Break SVP
        ↓
Verified Pullback Extreme
        ↓
Major IDM Eligibility
        ↓
REAL_MAJOR_IDM
        ↓
FALLBACK_MAJOR_IDM → SUPERSEDED
```

When the first genuine post-BOS Structurally Valid Pullback forms: `REAL_MAJOR_IDM` is created, `FALLBACK_MAJOR_IDM` is permanently `SUPERSEDED`, and the boundary reverts to a protected structural pivot.

### 3.4.8 — Protected Structural Extreme Lock

The corrective extreme remains dynamic until `VALID_BOS`.

Bullish:

```text
E_retrace(t) = min(Low_k)
```

Bearish:

```text
E_retrace(t) = max(High_k)
```

After sufficient retracement and valid BOS:

```text
VALID_BOS
    ↓
E_retrace LOCKED
    ↓
PROTECTED STRUCTURAL EXTREME
```

The completed `VALID_BOS` event locks the dynamic corrective extreme immediately. No later body close is required.

A FALLBACK_MAJOR_IDM wick sweep does not lock the extreme.

This module does not redefine the full CONFIRMED_STRUCTURAL_SWING / Protected Structural Extreme lifecycle; that ownership remains in `03_structural_semantic_authority.md` Section 3.3.

### 3.4.9 — Trading Range Rollover

Only `VALID_BOS` closes the previous governing Trading Range and starts the next structural lifecycle.

```text
VALID_BOS
   ↓
PREVIOUS RANGE CLOSED
   ↓
PROTECTED_STRUCTURAL_EXTREME_LOCK + TRADING_RANGE_ROLLOVER
   ↓
NEW RANGE ACTIVE
```

The following do not independently roll the range:

- physical external break;
- wick penetration;
- Minor IDM sweep;
- Major IDM sweep;
- FALLBACK_MAJOR_IDM sweep;
- insufficient-retracement impulse extension.

Post-BOS retracement and liquidity collection belong to the new range lifecycle.

### 3.4.10 — Post-BOS Fallback Initialization

After `VALID_BOS`, the new structural lifecycle enters the early-range phase in which a FALLBACK_MAJOR_IDM may be active until a real post-BOS Major IDM is independently formed.

```text
VALID_BOS
    ↓
NEW STRUCTURAL LIFECYCLE
    ↓
FALLBACK MAJOR IDM ACTIVE
    ↓
First Qualifying Post-BOS SVP
    ↓
Verified Pullback Extreme
    ↓
Major IDM Eligibility
    ↓
REAL_MAJOR_IDM
    ↓
FALLBACK_MAJOR_IDM superseded
```

`NEW_SVP` does not itself equal `REAL_MAJOR_IDM`.

### 3.4.11 — POI Lifecycle Boundary

BOS closes a Trading Range, but the structural engine does not directly delete POIs.

```text
VALID_BOS
    ↓
TRADING_RANGE_ROLLED_OVER
    ↓
POI LIFECYCLE SUBSYSTEM
```

Historical POI expiration is owned by the separate POI lifecycle/execution semantics. Structural BOS methodology must not silently redefine POI registry behavior.

### 3.4.12 — Anti-Retroactive and Exclusivity Invariants

```text
MAJOR_IDM_SWEEP
≠ VALID_BOS
```

```text
IMPULSE_EXTENSION
≠ VALID_BOS
```

```text
MAJOR_IDM_SWEEP
≠ CHoCH_CONFIRMED
```

```text
A past event classification is immutable.
```

If `t1` is classified as `MAJOR_IDM_SWEEP`, later candles cannot rewrite `t1` as BOS. Each event is evaluated against the structural state and provenance active at its own event time.

### 3.4.13 — BOS State-Transition Contract

`EXT_CONT_BREAK` applies exclusively to continuation boundaries.

```text
EXT_CONT_BREAK
        ↓
evaluate stored qualification
        ├── DISQUALIFIED → IMPULSE_EXTENSION (current lifecycle remains active)
        └── QUALIFIED    → VALID_BOS (POST_BOS / new range lifecycle)
```

The transition outcome is deterministic once event identity, retracement qualification, and level provenance are known.

### 3.4.14 — BOS / CHoCH Boundary

BOS and CHoCH are mutually exclusive structural outcomes for the same evaluated external event.

```text
CONTINUATION EXTERNAL BREAK
        ↓
BOS PIPELINE (VALID_BOS)

OPPOSING EXTERNAL BREAK
        ↓
CHoCH PIPELINE (CHoCH_CONFIRMED)
```

A FALLBACK_MAJOR_IDM event can produce `MAJOR_IDM_SWEEP`; it cannot be simultaneously classified as `VALID_BOS` or `CHoCH_CONFIRMED`.

### 3.4.15 — Canonical Authority Hierarchy (MC-01)

For the canonical True SMC implementation, the implementation-level structural specification governs where it provides a more specific rule than earlier generic pedagogical formulations.

Therefore:
* earlier body-close-only BOS pedagogy is NOT a universal implementation rule;
* implementation-level Wick-BOS defines the valid STRUCTURAL_SWING_BREAK mechanism, while the complete VALID_BOS event still requires all canonical macro-BOS gates;
* continuation external wick-BOS is canonical for establishing the break;
* wick interpretation is structural-context dependent.

## Canonical BOS Invariants

1. BOS requires an eligible CONFIRMED_STRUCTURAL_SWING reference.
2. Physical break does not equal `VALID_BOS`.
3. Retracement sufficiency is a prerequisite to continuation BOS.
4. Major retracement qualification is produced by Layer 3 and consumed here as stored state.
5. Canonical default retracement depth is 38.2%; deeper retracements, including 50%, remain instances of the same depth criterion.
6. Reduced-candle displacement and higher-timeframe qualification are evaluated by Layer 3 and are not redefined here.
7. Wick-BOS is immediate and equality at the broken level is valid.
8. Fallback Major IDM is a proxy, not Real Major IDM.
9. FALLBACK_MAJOR_IDM wick breach is `MAJOR_IDM_SWEEP`, not VALID_BOS or CHoCH_CONFIRMED.
10. `MAJOR_IDM_SWEEP` unlocks the Swing Confirmation Gate but does not automatically create a CONFIRMED_STRUCTURAL_SWING.
11. `NEW_SVP` does not automatically create Real Major IDM.
12. Real Major IDM supersedes the FALLBACK_MAJOR_IDM only through the validated post-break SVP → Verified Extreme → Eligibility → Real IDM lifecycle.
13. Only `VALID_BOS` rolls the Trading Range and locks the Protected Structural Extreme.
14. BOS event classification is anti-retroactive.
15. BOS mechanics are subordinate to `03_structural_semantic_authority.md` and must not create a competing Layer 3 authority.