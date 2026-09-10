# METHODOLOGY_PARAMETER

**Role:** Numeric and configurable methodology parameters.

## Current canonical parameters

### Minimum retracement

- Canonical default: `38.2%`.
- The minimum retracement may be exposed as a configurable engine parameter where applicable.
- Configuration changes the threshold, not the semantic definition of Valid Pullback or IDM.
- Do not encode the numeric default into semantic state names.

### Two-candle momentum exception

Exactly two opposing candles may qualify only when the canonical exception conditions are satisfied. The qualitative `large/high-momentum` condition remains unverified until an authoritative quantitative definition exists.

Do not invent ATR, body-ratio, volatility, or standard-deviation thresholds and present them as canonical methodology.

### Implementation parameters

Future quantitative thresholds may be configurable, but they must remain explicitly classified as implementation parameters unless independently verified and approved as methodology.

## Parameter boundaries

```text
PARAMETER ≠ OBJECT DEFINITION
PARAMETER ≠ STRUCTURAL TRUTH
CONFIGURATION ≠ METHODOLOGY REDEFINITION
```

Changing a threshold must never create an otherwise invalid structural event.

## Obsolete parameter

The historical sub-38.2% Fibonacci bootstrap variant is obsolete and must not be retained as a scoring, compatibility, fixture, logging, state-name, or entry/setup classification.

## Source of truth

The complete existing rules remain in `skill.md` during the migration phase. This file isolates parameter semantics without deleting or rewriting the original rules.
