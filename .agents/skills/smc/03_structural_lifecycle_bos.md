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

1. retracement sufficiency is satisfied;
2. the reference has correct external structural identity;
3. the broken level is not the applicable Fallback Major IDM / Range-Boundary Proxy;
4. the final break classification satisfies 3.4.3.

If an external continuation break occurs before retracement sufficiency is satisfied:

```text
EXT_CONT_BREAK
+
RETRACEMENT_SUFFICIENCY = NOT_SATISFIED
        ↓
IMPULSE_EXTENSION
```

No `VALID_BOS` is created and the current structural lifecycle remains active.

**Verdict: PASS / CLOSED.**

### 3.4.3 — Retracement Qualification Gate

The continuation-break classification is gated by the canonical retracement qualification rules.

**Standard path**

```text
>= 3 opposing candles
AND
retracement depth >= configured minimum
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

Canonical qualification matrix:

| Opposing candles | Retracement depth | Momentum / sweep condition | Result |
|---|---|---|---|
| 0 | any | any | INSUFFICIENT → IMPULSE_EXTENSION |
| 1 | any | any | INSUFFICIENT → IMPULSE_EXTENSION |
| exactly 2 | <38.2% | not qualified | INSUFFICIENT → IMPULSE_EXTENSION |
| exactly 2 | <38.2% | high momentum + >=5 extremes swept/engulfed | QUALIFIED |
| exactly 2 | >=38.2% | high momentum + any sweep count | QUALIFIED |
| >=3 | <38.2% | any | INSUFFICIENT → IMPULSE_EXTENSION |
| >=3 | >=38.2% | any | QUALIFIED |

The qualitative `LARGE / HIGH-MOMENTUM` condition must not be replaced by invented ATR, body-ratio, volatility, standard-deviation, or other numeric thresholds unless separately validated and parameterized.

**Verdict: PASS / CLOSED.**

### 3.4.4 — Canonical Break Classification

The validated continuation pipeline is:

```text
EXT_CONT_BREAK
        ↓
RETRACEMENT QUALIFICATION GATE
        ├── NOT_SATISFIED
        │       ↓
        │  IMPULSE_EXTENSION
        │
        └── SATISFIED
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
IMPULSE_EXTENSION ≠ EVENT CLASS
MAJOR_IDM_SWEEP ≠ VALID_BOS
```

The classification is based on structural level identity and provenance, not geometry alone.

### 3.4.5 — Body-Close BOS

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

A body close is valid only after the retracement gate and all applicable structural/provenance prerequisites have passed.

A body close alone cannot manufacture BOS.

**Verdict: PASS / CLOSED.**

### 3.4.6 — Wick-Break BOS

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

The only mandatory exception is a Fallback Major IDM / Range-Boundary Proxy level.

**Verdict: PASS / CLOSED.**

### 3.4.7 — Fallback Major IDM / Range-Boundary Proxy

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

A valid wick BOS locks the dynamic corrective extreme immediately. No later body close is required.

A fallback proxy wick sweep does not lock the extreme.

This module does not redefine the full Confirmed Swing / Protected Structural Extreme lifecycle; that ownership remains in `03_structural_lifecycle.md` Section 3.3.

### 3.4.9 — Trading Range Rollover

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
- insufficient-retracement impulse extension.

Post-BOS retracement and liquidity collection belong to the new range lifecycle.

### 3.4.10 — Post-BOS Fallback Initialization

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
≠ VALID_CHoCH
```

```text
A past event classification is immutable.
```

If `t1` is classified as `MAJOR_IDM_SWEEP`, later candles cannot rewrite `t1` as BOS. Each event is evaluated against the structural state and provenance active at its own event time.

### 3.4.13 — BOS State-Transition Contract

```text
EXT_CONT_BREAK
        ↓
classification
        ├── IMPULSE_EXTENSION → current lifecycle remains active
        ├── VALID_BOS         → POST_BOS / new range lifecycle
        └── MAJOR_IDM_SWEEP   → current lifecycle remains active
```

The transition outcome is deterministic once event identity, retracement qualification, and level provenance are known.

### 3.4.14 — BOS / CHoCH Boundary

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
3. Retracement sufficiency is a prerequisite to continuation BOS.
4. No automatic one-candle retracement exception exists.
5. Canonical default retracement depth is 38.2%.
6. Exactly-two-candle qualification requires high-momentum action and either >=5 prior candle extremes swept/engulfed or retracement depth >=38.2%.
7. Wick-BOS is immediate and equality at the broken level is valid.
8. Fallback Major IDM is a proxy, not Real Major IDM.
9. Fallback wick breach is `MAJOR_IDM_SWEEP`, not BOS or CHoCH.
10. `MAJOR_IDM_SWEEP` unlocks the Swing Confirmation Gate but does not automatically create a Confirmed Swing.
11. `NEW_SVP` does not automatically create Real Major IDM.
12. Real Major IDM supersedes the fallback proxy only through the validated post-break SVP → Verified Extreme → Eligibility → Real IDM lifecycle.
13. Only `VALID_BOS` rolls the Trading Range and locks the Protected Structural Extreme.
14. BOS event classification is anti-retroactive.
15. BOS mechanics are subordinate to `03_structural_lifecycle.md` and must not create a competing Layer 3 authority.

**Section 3.4 verdict: PASS / CLOSED.**