# CROSS-MODULE AUDIT — POST-CHoCH DUAL-LINEAGE ARCHITECTURE

**Status:** PASS / CLOSED (methodology); implementation must satisfy the requirements below.

**Audit scope:** Post-CHoCH lifecycle provenance and ontological separation across the category-based True SMC documentation.

## Core invariant

A confirmed `VALID_CHoCH` creates two independent post-CHoCH lineages:

```text
VALID_CHoCH
        │
        ├──────────────────────────────┐
        ▼                              ▼
MINOR IDM LINEAGE              FALLBACK PROXY LINEAGE
internal / post-CHoCH          external / range-boundary
        │                              │
FIRST_POST_CHOCH_SVP            FALLBACK_MAJOR_IDM
        │                              │
Verified Pullback Extreme       previous Protected Structural Extreme
        │                              │
IDM Eligibility                 wick → MAJOR_IDM_SWEEP only
        │                              │
FIRST_POST_CHOCH_MINOR_IDM      body close → CHoCH eligibility only
        │
MINOR_IDM_SWEEP
        │
SWING CONFIRMATION GATE
        │
CONFIRMED SWING
        │
FIRST VALID BOS
        │
REAL_MAJOR_IDM → FALLBACK SUPERSEDED
```

The branches must never be collapsed into a generic `IDM` whose provenance silently changes.

## Post-CHoCH confirmation lock

`VALID_CHoCH` terminates the old regime, establishes the new trend, marks the CHoCH-causing leg as `INITIAL_ACTIVE_IMPULSE`, and enters `CONFIRMATION_LOCKED`.

```text
VALID_CHoCH
 → NEW_TREND
 → INITIAL_ACTIVE_IMPULSE
 → CONFIRMATION_LOCKED
 → FIRST_POST_CHOCH_SVP
 → FIRST_POST_CHOCH_MINOR_IDM
 → MINOR_IDM_SWEEP
 → CONFIRMED_SWING
 → FIRST_VALID_BOS
```

No Protected Structural Extreme or normal trend-direction BOS is manufactured at the moment of CHoCH.

## First post-CHoCH SVP and Minor IDM

```text
CANDLE-LEVEL VALID PULLBACK
 → STRUCTURAL RETRACEMENT QUALIFICATION
 → STRUCTURALLY VALID PULLBACK
 → VERIFIED_PULLBACK_EXTREME
 → IDM ELIGIBILITY
 → FIRST_POST_CHOCH_MINOR_IDM
```

Therefore:

```text
FIRST_POST_CHOCH_SVP ≠ FIRST_POST_CHOCH_MINOR_IDM
```

## Fallback Major IDM parallel lineage

The fallback lineage is initialized from the **external structural boundary**, not from the first post-CHoCH pullback:

```text
VALID_CHoCH
 → previous Protected Structural Extreme / external boundary
 → FALLBACK_MAJOR_IDM
```

Mandatory distinctions:

```text
FALLBACK_MAJOR_IDM ≠ FIRST_POST_CHOCH_MINOR_IDM
FALLBACK_MAJOR_IDM ≠ REAL_MAJOR_IDM
```

## Fallback wick quarantine

```text
FALLBACK_MAJOR_IDM + WICK BREACH
 → MAJOR_IDM_SWEEP
```

This is strictly not:

```text
VALID_CHoCH
VALID_BOS
TRADING_RANGE_ROLLOVER
PROTECTED_EXTREME_LOCK
```

The sweep may unlock the Swing Confirmation Gate but does not automatically create a Confirmed Swing.

## First BOS and Real Major IDM

```text
post-CHoCH SVP
 → Minor IDM
 → Minor IDM Sweep
 → Confirmed Swing
 → Retracement Sufficiency
 → Physical External Break
 → BOS classification
 → VALID_BOS
```

After the first valid BOS:

```text
VALID_BOS
 → FIRST_QUALIFYING_POST_BOS_SVP
 → VERIFIED_PULLBACK_EXTREME
 → MAJOR_IDM_ELIGIBILITY
 → REAL_MAJOR_IDM
```

A Minor IDM is never promoted by age or label. A fallback proxy is never directly converted into Real Major IDM.

## Fallback supersession

```text
REAL_MAJOR_IDM
 → FALLBACK_MAJOR_IDM = SUPERSEDED / TERMINATED
```

Historical existence may remain recorded, but the fallback must cease to compete as the active Major IDM source.

## Ontological invariants

```text
FIRST_POST_CHOCH_SVP ≠ FIRST_POST_CHOCH_MINOR_IDM
FIRST_POST_CHOCH_MINOR_IDM ≠ FALLBACK_MAJOR_IDM
FALLBACK_MAJOR_IDM ≠ REAL_MAJOR_IDM
MINOR_IDM_SWEEP ≠ VALID_BOS
MAJOR_IDM_SWEEP ≠ VALID_BOS
MAJOR_IDM_SWEEP ≠ VALID_CHoCH
VALID_CHoCH ≠ PROTECTED_STRUCTURAL_EXTREME
VALID_CHoCH ≠ FIRST_POST_CHOCH_SVP
```

## Implementation boundary

Implementation must preserve explicit provenance for `MINOR_IDM`, `REAL_MAJOR_IDM`, and `FALLBACK_MAJOR_IDM`, and must represent `CONFIRMATION_LOCKED` after CHoCH.

A `VALID_CHoCH` must not immediately manufacture a normal confirmed Trading Range or Protected Structural Extreme, and the fallback proxy must not be omitted.

```text
EVENT PRECEDENCE ≠ INTRABAR EVENT ORDER
OHLC ≠ INTRABAR_SEQUENCE
```

**Final methodology verdict: PASS / CLOSED.**

Implementation compliance is conditional on the actual engine satisfying the state/provenance requirements above.