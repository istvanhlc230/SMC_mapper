# TRUE SMC — STRUCTURAL LIFECYCLE / BOS

**Role:** Detailed Section 3.4 BOS mechanics module under the canonical Layer 3 Structural Lifecycle authority.

**Authority:** `03_structural_lifecycle.md` remains the Layer 3 lifecycle authority. This document owns the detailed mechanics of Section 3.4 only. It is subordinate to Layer 3 and must not create a competing structural-lifecycle category.

**Validation status:** Section 3.4 BOS mechanics are methodologically validated and closed.

## 3.4 — Break of Structure (BOS) Mechanics

BOS is a macro structural continuation event. It is not a local candle pattern, arbitrary liquidity takeout, IDM sweep, or internal structural break.

### 3.4.1 — BOS Reference Identity

The only legitimate continuation-BOS reference object is an eligible **Confirmed Structural Swing Point** of the active lifecycle:

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
Confirmed Continuation Swing
        ↓
Eligible BOS Reference
```

**Verdict: PASS / CLOSED.**

### 3.4.2 — Physical External Break

A Physical External Break occurs when price physically penetrates the governing external level of an eligible Confirmed Structural Swing.

Bullish:

```text
High_t > Confirmed_Swing_High
```

Bearish:

```text
Low_t < Confirmed_Swing_Low
```

The penetration may occur through wick/shadow or candle body.

A physical external break does **not** itself establish `VALID_BOS`, Trading Range rollover, or Protected Structural Extreme locking. It opens the break-classification path.

Mandatory prerequisites remain:

1. IDM takeout has occurred;
2. governing retracement depth is at least 38.2%;
3. the reference has correct external structural identity;
4. the broken level is not the applicable Fallback Major IDM / Range-Boundary Proxy;
5. the final break classification satisfies the canonical BOS predicate.

If an external continuation break occurs before either BOS gate condition is satisfied:

```text
EXT_CONT_BREAK
+
BOS GATE NOT SATISFIED
        ↓
IMPULSE_EXTENSION
```

No `VALID_BOS` is created and the current structural lifecycle remains active.

**Verdict: PASS / CLOSED.**

### 3.4.3 — Canonical BOS Qualification Gate

The BOS Qualification Gate is a **macro structural gate**. It does not define or create the candle-level Valid Pullback.

A candle-level Valid Pullback may exist without a 38.2% retracement. The 38.2% requirement enters only when determining whether the subsequent external swing break qualifies as `VALID_BOS`.

#### Gate Condition 1 — IDM Liquidity Takeout

The retracement must physically take the active, BOS-relevant Inducement liquidity.

The takeout may occur by wick or body.

```text
IDM_TAKEN = TRUE
```

IDM takeout alone is insufficient for BOS.

#### Gate Condition 2 — Deep Retracement

The governing Dealing Range retracement must reach at least **38.2%** Fibonacci depth.

```text
RETRACEMENT_DEPTH >= 0.382
```

This requirement is **not** a candle-level Valid Pullback requirement.

It is a BOS Qualification Gate requirement only.

#### Canonical BOS Predicate

```text
VALID_BOS
    ⇔
    IDM_TAKEN
    AND
    RETRACEMENT_DEPTH >= 0.382
    AND
    STRUCTURAL_SWING_BREAK
```

`STRUCTURAL_SWING_BREAK` may be a wick break or body break. Wick BOS is not required to wait for a later body close.

#### Canonical Lifecycle Separation

```text
CANDLE-LEVEL VALID PULLBACK
        ↓
PULLBACK EXTREME
        ↓
IDM / LIQUIDITY REFERENCE
        ↓
IDM TAKEOUT
        ↓
DEEP RETRACEMENT >= 38.2%
        ↓
STRUCTURAL SWING BREAK
        ↓
VALID_BOS
        ↓
TRADING_RANGE_ROLLOVER
```

The following concepts must remain distinct:

```text
CANDLE-LEVEL VALID PULLBACK
    ≠ DEEP RETRACEMENT
    ≠ IDM TAKEOUT
    ≠ VALID_BOS
```

#### Gate Outcome A — Both Conditions Satisfied

```text
IDM_TAKEN = TRUE
AND
RETRACEMENT_DEPTH >= 0.382
AND
STRUCTURAL_SWING_BREAK
```

Result:

```text
VALID_BOS
    ↓
TRADING_RANGE_ROLLOVER
```

The previous governing Trading Range is closed, the validated retracement extreme becomes the new Protected Structural Extreme, and the next Trading Range lifecycle begins.

#### Gate Outcome B — Insufficient Retracement

```text
RETRACEMENT_DEPTH < 0.382
```

The later Confirmed Swing Point break is **not** a BOS, even if IDM liquidity was taken.

```text
NO_VALID_BOS
    ↓
IMPULSE_EXTENSION
```

There is no Trading Range rollover and no new Protected Structural Extreme created solely by this break.

The existing governing range remains active and continues through the expansion.

The retracement extreme remains the latest liquidity/IDM reference as applicable; it does not become a protected structural extreme through the rejected break.

Diagnostic classification:

```text
INSUFFICIENT_RETRACEMENT
```

#### Gate Outcome C — IDM Not Taken

```text
IDM_TAKEN = FALSE
```

The later Confirmed Swing Point break is **not** a BOS, even if retracement depth is at least 38.2%.

```text
NO_VALID_BOS
    ↓
IMPULSE_EXTENSION
```

There is no Trading Range rollover and no new Protected Structural Extreme created solely by this break.

The existing governing range remains active.

Diagnostic classification:

```text
IDM_NOT_TAKEN
```

#### Gate Outcome D — Both Conditions Fail

```text
RETRACEMENT_DEPTH < 0.382
AND
IDM_TAKEN = FALSE
```

Result:

```text
NO_VALID_BOS
    ↓
IMPULSE_EXTENSION
```

Both diagnostic causes remain independently identifiable:

```text
INSUFFICIENT_RETRACEMENT
AND
IDM_NOT_TAKEN
```

### 3.4.4 — Non-Canonical 38.2% Exception Disqualification

There is **no canonical exception** that permits a retracement below 38.2% to qualify a subsequent external break as `VALID_BOS` because of momentum, prior-extreme count, engulfment count, or any other secondary condition.

The following rule is explicitly non-canonical:

```text
RETRACEMENT_DEPTH < 0.382
AND
PRIOR_EXTREMES_SWEPT >= 5
    ⇒ VALID_BOS
```

Likewise, this is non-canonical:

```text
EXACTLY 2 OPPOSING CANDLES
AND
HIGH_MOMENTUM
AND
PRIOR_EXTREMES_SWEPT >= 5
AND
RETRACEMENT_DEPTH < 0.382
    ⇒ VALID_BOS
```

Therefore:

```text
RETRACEMENT_DEPTH < 0.382
    ⇒ BOS DISQUALIFIED
```

The `>=5 PRIOR CANDLE EXTREMES` condition must not bypass the canonical 38.2% BOS gate.

Any future exception requires independent authoritative source validation before entering the canonical methodology.

### 3.4.5 — Canonical Break Classification

The validated continuation pipeline is:

```text
EXT_CONT_BREAK
        ↓
BOS QUALIFICATION GATE
        ├── INSUFFICIENT_RETRACEMENT
        │       ↓
        │  IMPULSE_EXTENSION
        │
        ├── IDM_NOT_TAKEN
        │       ↓
        │  IMPULSE_EXTENSION
        │
        └── BOTH CONDITIONS SATISFIED
                ↓
        BREAK PROVENANCE
                ├── REAL
                │      ↓
                │  VALID_BOS
                │
                └── FALLBACK
                       ↓
                  MAJOR_IDM_SWEEP
```

Therefore:

```text
EXT_CONT_BREAK ≠ VALID_BOS
IMPULSE_EXTENSION ≠ VALID_BOS
MAJOR_IDM_SWEEP ≠ VALID_BOS
```

`IMPULSE_EXTENSION` is a lifecycle outcome of a failed BOS qualification, not a competing structural event class.

The rejection reason must remain diagnosable as `INSUFFICIENT_RETRACEMENT`, `IDM_NOT_TAKEN`, or both.

### 3.4.6 — Body-Close BOS

Bullish:

```text
Close_t > Confirmed_Swing_High
→ VALID_BOS
```

Bearish:

```text
Close_t < Confirmed_Swing_Low
→ VALID_BOS
```

A body close is valid only after the canonical BOS Qualification Gate and all applicable structural/provenance prerequisites have passed.

A body close alone cannot manufacture BOS.

**Verdict: PASS / CLOSED.**

### 3.4.7 — Wick-Break BOS

Bullish:

```text
High_t > Confirmed_Swing_High
AND
Close_t <= Confirmed_Swing_High
→ VALID_BOS
```

Bearish:

```text
Low_t < Confirmed_Swing_Low
AND
Close_t >= Confirmed_Swing_Low
→ VALID_BOS
```

Equality at the broken level is included in the wick-BOS path.

Wick-BOS is immediate. It does not wait for a later body close, and a later candle cannot retroactively rewrite the event.

The canonical exception is a Fallback Major IDM / Range-Boundary Proxy level, where the same wick geometry is classified as `MAJOR_IDM_SWEEP` rather than BOS.

**Verdict: PASS / CLOSED.**

### 3.4.8 — Fallback Major IDM / Range-Boundary Proxy

Fallback Major IDM is a temporary lifecycle-specific **external Range-Boundary Proxy** used after a confirmed macro event while the new expansion has not yet produced an independently qualified Real Major IDM from a post-break Structurally Valid Pullback.

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
≠ VALID_CHoCH
≠ TRADING_RANGE_ROLLOVER
≠ PROTECTED_EXTREME_LOCK
```

The sweep unlocks the Swing Confirmation Gate but does **not** automatically create a Confirmed Swing. All remaining swing-confirmation prerequisites remain mandatory.

#### Proxy body close through opposing boundary

A body close through a fallback opposing boundary is only geometrically eligible for the CHoCH pipeline. It becomes `VALID_CHoCH` only when all applicable Section 3.5 prerequisites pass.

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
FALLBACK PROXY → SUPERSEDED
```

The first SVP alone does not create Real Major IDM.

**Verdict: PASS / CLOSED.**

### 3.4.9 — Protected Structural Extreme Lock

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

A valid wick BOS locks the dynamic corrective extreme immediately. No later body close is required.

A fallback proxy wick sweep does not lock the extreme.

This module does not redefine the full Confirmed Swing / Protected Structural Extreme lifecycle; that ownership remains in `03_structural_lifecycle.md` Section 3.3.

### 3.4.10 — Trading Range Rollover

Only `VALID_BOS` closes the previous governing Trading Range and starts the next structural lifecycle.

```text
VALID_BOS
   ↓
PREVIOUS RANGE CLOSED
   ↓
NEW RANGE ACTIVE
```

The following do not independently roll the range:

- physical external break;
- wick penetration;
- Minor IDM sweep;
- Major IDM sweep;
- Fallback proxy sweep;
- insufficient-retracement impulse extension;
- IDM-not-taken impulse extension.

A rejected continuation break does **not** destroy the existing Trading Range. The governing range remains active and may continue to expand through `IMPULSE_EXTENSION`.

Post-BOS retracement and liquidity collection belong to the new range lifecycle.

### 3.4.11 — Post-BOS Fallback Initialization

After `VALID_BOS`, the new structural lifecycle enters the early-range phase in which a Fallback Major IDM / Range-Boundary Proxy may be active until a real post-BOS Major IDM is independently formed.

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
FALLBACK SUPERSEDED
```

`NEW_SVP` does not itself equal `REAL_MAJOR_IDM`.

### 3.4.12 — POI Lifecycle Boundary

BOS closes a Trading Range, but the structural engine does not directly delete POIs.

```text
VALID_BOS
    ↓
TRADING_RANGE_ROLLED_OVER
    ↓
POI LIFECYCLE SUBSYSTEM
```

Historical POI expiration is owned by the separate POI lifecycle/execution semantics. Structural BOS methodology must not silently redefine POI registry behavior.

### 3.4.13 — Anti-Retroactive and Exclusivity Invariants

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
≠ VALID_CHoCH
```

```text
A past event classification is immutable.
```

If `t1` is classified as `MAJOR_IDM_SWEEP` or `IMPULSE_EXTENSION`, later candles cannot rewrite `t1` as BOS. Each event is evaluated against the structural state and provenance active at its own event time.

### 3.4.14 — BOS State-Transition Contract

```text
EXT_CONT_BREAK
        ↓
BOS QUALIFICATION GATE
        ├── INSUFFICIENT_RETRACEMENT → IMPULSE_EXTENSION
        ├── IDM_NOT_TAKEN          → IMPULSE_EXTENSION
        ├── BOTH SATISFIED + REAL   → VALID_BOS
        └── BOTH SATISFIED + FALLBACK → MAJOR_IDM_SWEEP
```

A failed BOS qualification does not roll the range. It leaves the current lifecycle active.

### 3.4.15 — BOS / CHoCH Boundary

BOS and CHoCH are mutually exclusive structural outcomes for the same evaluated external event.

```text
CONTINUATION EXTERNAL BREAK
        ↓
BOS PIPELINE

OPPOSING EXTERNAL BREAK
        ↓
CHoCH PIPELINE
```

A fallback proxy event can produce `MAJOR_IDM_SWEEP`; it cannot be simultaneously classified as `VALID_BOS` or `VALID_CHoCH`.

## Canonical BOS Invariants

1. BOS requires an eligible Confirmed Structural Swing reference.
2. Physical break does not equal `VALID_BOS`.
3. BOS requires **both** IDM liquidity takeout and Deep Retracement >= 38.2% before the structural swing break can qualify as `VALID_BOS`.
4. The 38.2% requirement belongs to the BOS Qualification Gate, not candle-level Valid Pullback creation.
5. No automatic one-candle retracement exception exists.
6. No prior-extreme-count or momentum exception may bypass the canonical 38.2% BOS minimum.
7. `INSUFFICIENT_RETRACEMENT` and `IDM_NOT_TAKEN` are independent BOS disqualification causes and must remain diagnostically distinct.
8. Wick-BOS is immediate and equality at the broken level is valid.
9. Fallback Major IDM is a proxy, not Real Major IDM.
10. Fallback wick breach is `MAJOR_IDM_SWEEP`, not BOS or CHoCH.
11. `MAJOR_IDM_SWEEP` unlocks the Swing Confirmation Gate but does not automatically create a Confirmed Swing.
12. `NEW_SVP` does not automatically create Real Major IDM.
13. Real Major IDM supersedes the fallback proxy only through the validated post-break SVP → Verified Extreme → Eligibility → Real IDM lifecycle.
14. Only `VALID_BOS` rolls the Trading Range and locks the Protected Structural Extreme.
15. A failed BOS qualification leaves the governing Trading Range active; `IMPULSE_EXTENSION` does not destroy the range.
16. BOS event classification is anti-retroactive.
17. BOS mechanics are subordinate to `03_structural_lifecycle.md` and must not create a competing Layer 3 authority.

**Section 3.4 verdict: PASS / CLOSED.**
