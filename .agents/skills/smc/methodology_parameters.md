# METHODOLOGY_PARAMETER

**Role:** Numeric and configurable methodology parameters.

**Authority boundary:** This document owns numeric/configurable values only. It does not redefine the semantic identity or lifecycle of any methodology object. The semantic rules that consume these parameters remain authoritative in their current semantic-owner documents: `01_candle_level_foundation.md`, `02_minor_structure.md`, `03_structural_lifecycle.md`, and its detailed BOS/CHoCH modules where applicable.

## 9. Structural retracement parameters

### 9.1 Standard minimum retracement depth

- Canonical default: `38.2%`.
- The minimum retracement depth may be exposed as a configurable engine parameter where explicitly permitted.
- Configuration changes the numeric threshold only; it does not redefine the semantic meaning of Valid Pullback, Structurally Valid Pullback, IDM, or any higher-level structural state.
- Do not encode the numeric default into semantic state names.

The implementation may expose `BOS_MIN_RETRACEMENT_PCT` with canonical default `38.2%`.

### 9.2 Exactly-two-candle exception parameters

The semantic qualification rule for the exactly-two-candle exception is defined by `02_minor_structure.md` and consumed by the Layer 3 BOS lifecycle. This section owns only its numeric constraints:

- the exception applies to **exactly 2 opposing candles**;
- the prior-extreme sweep/engulfment threshold is **5 prior candle extremes**;
- the alternative retracement-depth threshold is **38.2%**.

The qualitative requirement for `LARGE / HIGH-MOMENTUM PRICE ACTION` has no authoritative quantitative value at present and therefore must not be invented here.

There is no numeric parameter that authorizes a one-candle exception.

Do not invent ATR, body-ratio, volatility, or standard-deviation thresholds and present them as canonical methodology.

## Parameter boundaries

```text
PARAMETER ≠ OBJECT DEFINITION
PARAMETER ≠ STRUCTURAL TRUTH
CONFIGURATION ≠ METHODOLOGY REDEFINITION
```

Changing a threshold must never create an otherwise invalid structural event or bypass a non-numeric prerequisite.

## Implementation parameters

Future quantitative thresholds may be configurable, but they must remain explicitly classified as implementation parameters unless independently verified and approved as methodology.

## 43. Obsolete parameter

The historical sub-38.2% Fibonacci bootstrap variant is obsolete and is governed by `deprecated.md`. It must not be retained as a scoring, compatibility, fixture, logging, state-name, or entry/setup classification.
