# METHODOLOGY_PARAMETER

**Role:** Numeric and configurable methodology parameters.

**Authority boundary:** This document owns numeric/configurable values only. It does not redefine the semantic identity or lifecycle of any methodology object. The semantic rules that consume these parameters remain authoritative in their current semantic-owner documents: `01_micro_structure.md`, `02_minor_structure.md`, and `03_structural_semantic_authority.md` with its subordinate BOS/CHoCH modules.

## 9. Structural Retracement & Equilibrium

### 9.1 Standard equilibrium threshold

- `STANDARD_EQUILIBRIUM_THRESHOLD: 0.50`
- This is the canonical standard qualification threshold for the normal major retracement path.

### 9.2 Conditional HTF threshold

- `HTF_CONDITIONAL_THRESHOLD: 0.382`
- The 38.2% threshold is not sufficient on its own.
- The 38.2%–<50% path qualifies only when the entire retracement constitutes a valid single pullback event on the applicable immediate Higher Timeframe.
- The semantic qualification rule is owned by `03_structural_semantic_authority.md`.

### 9.3 Candle counts & displacement exception

- `NORMAL_RETRACEMENT_CANDLE_COUNT: 3`
- Normal qualification uses at least three opposing closing candles.
- A **2-candle retracement is not a separate normal qualification rule**. It is a permitted reduced-candle case only when the documented rare displacement exception is satisfied.
- Reduced-candle qualification therefore covers a 2-candle retracement when the unusually large candle(s) collectively take at least five preceding bodies/extremes and the required retracement depth is reached.
- A short retracement is not automatically valid merely because it contains two candles.
- `MIN_OUTLIER_EXTREMES_TAKEN: 5`
- These are numeric support parameters only; they do not redefine the semantic qualification rule.

### 9.4 Higher-timeframe evaluation scope

- `HTF_PULLBACK_EVALUATION_SCOPE: "applicable_immediate_higher_timeframe"`
- No rigid timeframe-pairing table is encoded here.
- The applicable immediate Higher Timeframe is determined by the structural context.
## 10. Risk scoring boundary

Concrete risk-quality penalties, weighted-score arithmetic, and quality-tier evaluation are implementation-owned by `SMC_mapper.py` and represented in `08_implementation.md`. This parameter document does not own those calculations and must not duplicate them as methodology rules.

```text
RISK SCORE PARAMETER
    ≠
STRUCTURAL QUALIFICATION
```

No scoring threshold may manufacture or validate IDM, Confirmed Swing, Protected Structural Extreme, BOS, CHoCH, or Trading Range state.

## 11. Parameter boundaries

```text
PARAMETER ≠ OBJECT DEFINITION
PARAMETER ≠ STRUCTURAL TRUTH
CONFIGURATION ≠ METHODOLOGY REDEFINITION
```

Changing a threshold must never create an otherwise invalid structural event or bypass a non-numeric prerequisite.

## 12. Implementation parameters

Future quantitative thresholds may be configurable, but they must remain explicitly classified as implementation parameters unless independently verified and approved as methodology.

