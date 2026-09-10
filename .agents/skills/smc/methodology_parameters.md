# METHODOLOGY_PARAMETER

**Role:** Numeric and configurable methodology parameters.

**Authority boundary:** A parameter qualifies a methodology object; it does not redefine the semantic identity of that object. Canonical structural meaning remains in `true_smc_canonical.md`.

## 9. Structural retracement parameters

### Standard minimum retracement

- Canonical default: `38.2%`.
- The minimum retracement may be exposed as a configurable engine parameter where applicable.
- Configuration changes the threshold, not the semantic definition of Valid Pullback or IDM.
- Do not encode the numeric default into semantic state names.

The implementation may expose `BOS_MIN_RETRACEMENT_PCT` with canonical default 38.2%.

### Two-candle momentum exception

Exactly two opposing candles may qualify only when the canonical exception conditions are satisfied:

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

The verified exception is for exactly 2 candles. Do not automatically extend it to 1 candle.

The qualitative `large/high-momentum` condition remains unverified until an authoritative quantitative definition exists.

Do not invent ATR, body-ratio, volatility, or standard-deviation thresholds and present them as canonical methodology.

## Parameter boundaries

```text
PARAMETER ≠ OBJECT DEFINITION
PARAMETER ≠ STRUCTURAL TRUTH
CONFIGURATION ≠ METHODOLOGY REDEFINITION
```

Changing a threshold must never create an otherwise invalid structural event.

## Implementation parameters

Future quantitative thresholds may be configurable, but they must remain explicitly classified as implementation parameters unless independently verified and approved as methodology.

## 43. Obsolete parameter

The historical sub-38.2% Fibonacci bootstrap variant is obsolete and is governed by `deprecated.md`. It must not be retained as a scoring, compatibility, fixture, logging, state-name, or entry/setup classification.

## Migration status

The numeric/configurable parameter semantics from the preserved pre-reorganization ruleset are isolated here. The immutable baseline remains `.agents/skills/smc/skill_old.md` for final completeness verification.