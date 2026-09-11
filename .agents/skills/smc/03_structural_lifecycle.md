# TRUE SMC — STRUCTURAL LIFECYCLE

**Role:** Canonical Layer 3 Structural Lifecycle authority for Major Structure, Genesis, Confirmed Swing / Protected Structural Extreme, BOS, and CHoCH.

**Authority:** This document owns the complete validated Structural Lifecycle, Sections 3.1–3.5. `true_smc_choch.md` is the detailed mechanics module for Section 3.5; it does not create a separate lifecycle category or competing authority.

**Validation status:** Sections 3.1–3.4 are methodologically validated and closed. Section 3.5 is methodologically validated and closed, with its detailed mechanics maintained in `true_smc_choch.md`.

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
ACTIVE/MINOR IDM
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

Layer 1 and Layer 2 semantic foundations are owned by `true_smc_canonical.md`.

The Structural Lifecycle begins once those validated prerequisites are available and owns the external structural state machine from Major Structure through CHoCH and post-CHoCH regime initialization.

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

## 3.2 — Major Structure: Unit of Origin

The unit of origin for Major Structure is not an isolated candlestick, fractal pivot, or raw price extreme. Major Structure originates strictly from the complete **Confirmed Dealing Range Cycle**, anchored by liquidity-validated structural extremes.

Major Structure defines governing market bias, structural continuation (BOS), and trend reversal boundaries (CHoCH). It is ontologically distinct from candle-level and minor structure.

### 3.2.1 — Emergence of the Governing Dealing Range

A governing Trading Range does not exist merely because an impulse has occurred. A governing range is formally locked and established only when price retraces and sweeps the active qualified Inducement (Minor or Major IDM), thereby confirming the provisional expansion extreme as a **Confirmed Swing Point**.

### 3.2.2 — Genesis and Bootstrap Lifecycle

Prior to the first confirmed IDM sweep, such as chart inception or the initial active impulse following a CHoCH, the market resides in an unconfirmed expansion state (`BOOTSTRAP_EXPANSION`). In this state, candle-level minor structures may form candidate inducements, but no governing dealing range is finalized until the Swing Confirmation Gate is unlocked by a verified liquidity sweep.

Bootstrap is not permission to fabricate historical structure. It must remain distinguishable from organically confirmed structure.

### 3.2.3 — Impulse Origin vs Protected Structural Extreme

An impulse origin is the physical price/time anchor where an expansion began. It does not automatically constitute a Protected Structural Extreme.

A Protected Structural Extreme is an asymmetric macro-state established and locked exclusively through the validated BOS lifecycle defined below.

```text
CANDLE-LEVEL MINOR ACTION
        ↓
QUALIFIED IDM
        ↓
IDM SWEEP
        ↓
SWING CONFIRMATION GATE
        ↓
CONFIRMED SWING
        ↓
EXTERNAL BREAK
        ↓
VALID_BOS
        ↓
PROTECTED STRUCTURAL EXTREME LOCK
```

**Verdict: PASS / CLOSED.**

---

## 3.3 — Confirmed Swing & Protected Structural Extreme Lifecycle

### 3.3.1 — Ontological Asymmetry

```text
Confirmed Swing Point
        ≠
Protected Structural Extreme
```

A **Confirmed Swing Point** is established through the canonical Swing Confirmation Gate after the required qualified IDM liquidity takeout and all other confirmation prerequisites.

A Confirmed Swing records the current expansion extreme and serves as the external structural landmark for the active lifecycle. It is not automatically protected.

A **Protected Structural Extreme** is a later lifecycle state created by valid BOS. It becomes the governing trend anchor for the resulting structural lifecycle.

A Protected Structural Extreme may later be violated as the governing opposing range boundary, opening the CHoCH path.

**Verdict: PASS / CLOSED.**

### 3.3.2 — Dynamic Retracement & Sufficiency Gate

The corrective extreme must be tracked dynamically across the complete corrective window from swing confirmation until BOS.

Bullish lifecycle:

```text
E_retrace(t) = min(Low_k)
```

Bearish lifecycle:

```text
E_retrace(t) = max(High_k)
```

The tracked extreme must not be frozen prematurely at a local pivot, the IDM-sweeping candle, or an internal microstructure point.

Retracement sufficiency has two canonical qualification paths:

**Standard path**

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

**Verdict: PASS / CLOSED.**

### 3.3.3 — Protected Structural Extreme Locking Threshold

The absolute corrective extreme remains dynamically tracked until the structural event that produces `VALID_BOS`.

Prerequisite:

```text
Retracement Sufficiency Gate = SATISFIED
```

Locking trigger:

```text
VALID_BOS
    ↓
E_retrace LOCKED
    ↓
PROTECTED STRUCTURAL EXTREME
```

For an eligible external Confirmed Swing, both canonical break paths are valid:

- **Body-Close BOS:** the candle closes beyond the confirmed external level.
- **Wick-Break BOS:** price penetrates the confirmed external level by wick/shadow and the candle closes back at or inside the level, provided the broken level is not the Fallback Major IDM / Range-Boundary Proxy.

A valid wick BOS locks `E_retrace` immediately. No later body close is required.

**Fallback exception:** if the penetrated external level is simultaneously the Fallback Major IDM / Range-Boundary Proxy, the wick event is strictly `MAJOR_IDM_SWEEP`. It is not BOS and does not lock `E_retrace`.

The protected state is lifecycle-scoped. A later structural rollover establishes a new Protected Structural Extreme for the new lifecycle.

**Verdict: PASS / CLOSED.**

### 3.3.4 — Dealing Range Rollover & Post-BOS Cycle

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

The new cycle must not be interpreted as delayed acceptance of the preceding BOS. Post-BOS retracement, internal liquidity collection, and later displacement belong to the new range cycle.

**Verdict: PASS / CLOSED.**

---

# 3.4 — Break of Structure (BOS) Mechanics

BOS is a macro structural continuation event. It is not a local candle pattern, arbitrary liquidity takeout, or internal structural break.

## 3.4.1 — BOS Definition & Unit of Origin

The only legitimate **reference object type** for continuation BOS is the eligible **Confirmed Structural Swing Point** of the active lifecycle:

- bullish lifecycle → Confirmed Swing High;
- bearish lifecycle → Confirmed Swing Low.

Minor Structure, provisional swings, IDM, liquidity pools, arbitrary local levels, and Protected Opposing Extremes are not continuation-BOS reference objects.

```text
Confirmed Continuation Swing
        ↓
Eligible BOS Reference
```

A provisional or internal break remains non-BOS. If no eligible confirmed external swing exists, BOS evaluation is blocked.

**Verdict: PASS / CLOSED.**

## 3.4.2 — External Break: Physical Threshold

A Physical External Break is the discrete OHLC event in which price physically penetrates the governing external level of an eligible Confirmed Structural Swing.

Bullish:

```text
High_t > Confirmed_Swing_High
```

Bearish:

```text
Low_t < Confirmed_Swing_Low
```

The physical break may occur through wick/shadow or candle-body penetration.

A physical external break does not itself establish `VALID_BOS`, Trading Range rollover, or Protected Structural Extreme locking. It opens the Structural Classification Gate.

The following remain mandatory before BOS:

1. retracement sufficiency must already be satisfied;
2. the reference level must have correct external structural identity;
3. the broken level must not be the applicable Fallback Major IDM / Range-Boundary Proxy exception;
4. the final break must satisfy 3.4.3.

If the external break occurs without sufficient preceding retracement, the event remains `IMPULSE_EXTENSION` and does not create `VALID_BOS`.

**Verdict: PASS / CLOSED.**

## 3.4.3 — Canonical Break Execution: Body-Close & Wick-Break BOS

There are two first-class canonical BOS execution paths.

### A. Body-Close BOS

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

### B. Wick-Break BOS

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

A close exactly at the broken level remains a valid wick-BOS case.

Wick-BOS is immediate. It is not a provisional event waiting for a later candle close. A later candle does not retroactively approve or reject the previous BOS event.

The only mandatory exception is the Fallback Major IDM / Range-Boundary Proxy rule in 3.4.4.

```text
Eligible Confirmed Swing
+
Sufficient Retracement
+
Physical External Break
+
Non-Fallback Level
        ↓
Body Close OR Wick Break
        ↓
VALID_BOS
```

**Verdict: PASS / CLOSED.**

## 3.4.4 — Fallback Major IDM / Range-Boundary Proxy Exception

Fallback Major IDM is a temporary, lifecycle-specific **Range-Boundary Proxy**. It exists after a confirmed macro event (`VALID_BOS` or `VALID_CHoCH`) while the new expansion has not yet produced an independently qualified real Major IDM from a post-break Structurally Valid Pullback.

```text
Fallback Major IDM (Proxy)
        ≠
Real Major IDM
```

The proxy bridges the early-range liquidity/reference gap. It is not an independently formed internal liquidity pool.

### A. Proxy wick breach

If the tested external level has `provenance == FALLBACK` and price penetrates it by wick but closes back at or inside the level:

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

This event is terminal for the current evaluation and:

```text
MAJOR_IDM_SWEEP
≠ VALID_BOS
≠ VALID_CHoCH
≠ TRADING_RANGE_ROLLOVER
≠ PROTECTED_EXTREME_LOCK
```

The sweep satisfies the liquidity requirement and **unlocks the Swing Confirmation Gate**, but does not automatically create a `CONFIRMED_SWING_POINT`. All remaining swing-confirmation prerequisites are still mandatory.

### B. Proxy body close through opposing boundary

A body close beyond the opposing governing boundary is only geometrically eligible for CHoCH. The final result is:

```text
Body Close beyond opposing boundary
+
ALL APPLICABLE 3.5 CHoCH PREREQUISITES
        ↓
VALID_CHoCH
```

A body close alone is never sufficient to manufacture CHoCH.

### C. Proxy deprecation

Fallback does not convert directly into Real Major IDM.

The mandatory lifecycle is:

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

The first SVP alone is not enough to create Real Major IDM.

### D. Anti-retroactive invariant

If `t1` is classified as `MAJOR_IDM_SWEEP`, a later candle at `t1+n` can never rewrite the `t1` event as BOS. Every later candle is evaluated against the structural state active at its own event time.

**Verdict: PASS / CLOSED.**

## 3.4.5 — BOS Downstream State Changes & Range Rollover

Once `VALID_BOS` is emitted and the 3.4.4 fallback exception does not apply, the downstream state transition is deterministic.

### 3.4.5.1 — Trading Range rollover

```text
VALID_BOS
    ↓
previous Trading Range CLOSED
    ↓
TRADING_RANGE_ROLLED_OVER
    ↓
new Trading Range ACTIVE
```

A physical break, wick penetration, IDM sweep, or fallback proxy sweep cannot independently roll the Trading Range.

### 3.4.5.2 — Protected Structural Extreme

The 3.4.5 downstream transition consumes the rule already defined in 3.3.3:

```text
Retracement Sufficiency
        ↓
Dynamic E_retrace
        ↓
VALID_BOS
        ↓
LOCK E_retrace
        ↓
Protected Structural Extreme
```

3.4.5 does not redefine the locking threshold.

### 3.4.5.3 — Historical POI Expiration via Event-Driven Rollover

The structural engine does not directly delete or mutate the POI registry.

```text
STRUCTURAL ENGINE
        │
     VALID_BOS
        ↓
TRADING_RANGE_ROLLED_OVER
        │
        └──────────► POI LIFECYCLE SUBSYSTEM
                         ↓
                 previous-range POIs
                         ↓
                 EXPIRED_HISTORICAL
```

Only OF/OB entities belonging exclusively to the closed Trading Range transition to `EXPIRED_HISTORICAL`.

`EXPIRED_HISTORICAL` POIs are non-tradable. The execution layer must not place limit orders or validate lower-timeframe entry modules against them.

This is an event-driven POI lifecycle transition, not a structural-engine database deletion.

### 3.4.5.4 — Fallback Proxy initialization

A new BOS lifecycle initializes the Fallback Major IDM / Range-Boundary Proxy while no independently qualified Real Major IDM exists.

```text
VALID_BOS
    ↓
NEW STRUCTURAL LIFECYCLE
    ↓
FALLBACK MAJOR IDM ACTIVE
    ↓
First qualifying post-BOS SVP
    ↓
Verified Pullback Extreme
    ↓
Major IDM Eligibility
    ↓
REAL_MAJOR_IDM
    ↓
FALLBACK → SUPERSEDED
```

Proxy initialization is not Real Major IDM creation.

**Verdict: PASS / CLOSED.**

---

## 3.5 — Change of Character (CHoCH) Lifecycle

CHoCH is a first-class part of the Structural Lifecycle and represents the governing trend-regime transition.

The lifecycle owner is this document. The detailed deterministic CHoCH mechanics are maintained in `true_smc_choch.md`.

The Section 3.5 lifecycle is:

```text
CURRENT GOVERNING RANGE
        ↓
GOVERNING OPPOSING PROTECTED STRUCTURAL EXTREME
        ↓
PHYSICAL OPPOSING BOUNDARY BREAK
        ↓
CHoCH BREAK CLASSIFICATION
        ↓
VALID_CHoCH
        ↓
OLD TREND TERMINATED
        ↓
NEW TREND
        ↓
CHoCH-CAUSING LEG = INITIAL ACTIVE IMPULSIVE LEG
        ↓
CONFIRMATION LOCKED
        ↓
FIRST QUALIFYING POST-CHoCH SVP
        ↓
MINOR IDM
        ↓
IDM SWEEP / SWING CONFIRMATION
        ↓
CONFIRMED SWING
        ↓
NEW TRADING RANGE
        ↓
NORMAL BOS LIFECYCLE
```

### 3.5.1 — Detailed CHoCH mechanics module

`true_smc_choch.md` is the detailed Section 3.5 module and contains the validated, closed rules for:

- eligible Protected Opposing Structural Extreme / Governing Opposing Range Boundary;
- physical boundary break;
- body-close and wick-break CHoCH classification;
- Real Major IDM requirement for opposing wick CHoCH;
- Fallback Major IDM / Range-Boundary Proxy exception;
- `MAJOR_IDM_SWEEP` classification and anti-retroactive invariant;
- old-regime termination;
- new-trend initialization;
- CHoCH-causing leg as `INITIAL_ACTIVE_IMPULSE`;
- post-CHoCH confirmation lock;
- first qualifying SVP / Minor IDM / Swing Confirmation cycle.

The detailed module must be read as Section 3.5 of this lifecycle, not as a separate methodology category.

**Verdict: PASS / CLOSED.**

## Structural lifecycle authority boundary

```text
Layer 1 + Layer 2 semantic foundations
        ↓
true_smc_canonical.md
        ↓
Layer 3 Structural Lifecycle
        ↓
true_smc_structural_lifecycle.md
        │
        └── 3.5 detailed mechanics
              ↓
          true_smc_choch.md
```

Newer explicitly validated lifecycle rules supersede older conflicting wording regardless of the historical file in which the older wording was stored. Superseded rules belong in `deprecated.md` for traceability and are not alternative canonical paths.

## Lifecycle invariants

```text
VALID_BOS
    ↓
TRADING_RANGE_ROLLED_OVER
    ↓
new structural lifecycle
```

```text
VALID_CHoCH
    ↓
new trend lifecycle
    ↓
CHoCH-causing leg = initial active impulsive leg
```

Neither transition manufactures an IDM, Confirmed Swing, or Protected Structural Extreme that has not independently satisfied its canonical prerequisites.
