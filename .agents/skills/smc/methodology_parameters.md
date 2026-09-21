# METHODOLOGY_PARAMETER

**Role:** Numeric and configurable methodology parameters.

**Authority boundary:** This document owns numeric/configurable values only. It does not redefine the semantic identity or lifecycle of any methodology object. The semantic rules that consume these parameters remain authoritative in their current semantic-owner documents: `01_micro_structure.md`, `02_minor_structure.md`, and `03_structural_semantic_authority.md` with its subordinate BOS/CHoCH modules.

## 9. Structural retracement parameters

### 9.1 Standard minimum retracement depth

- Canonical default: `38.2%`.
- The minimum retracement depth may be exposed as a configurable engine parameter where explicitly permitted.
- Configuration changes the numeric threshold only; it does not redefine the semantic meaning of Valid Pullback, Structurally Valid Pullback, IDM, or any higher-level structural state.
- Do not encode the numeric default into semantic state names.

The implementation may expose `BOS_MIN_RETRACEMENT_PCT` with canonical default `38.2%`.

#### Mathematical formulation (Active Major Structure Dealing Range)

The 38.2% retracement threshold is anchored strictly to the active Major Structure Dealing Range:

- **Bullish trend**: Dealing range from Protected Swing Low ($ProtectedLow$, impulse origin) to provisional Expansion High ($ExpansionHigh$, Confirmed Swing):
  $$\text{Retracement depth } R = \frac{ExpansionHigh - RetracementLow}{ExpansionHigh - ProtectedLow}$$
  $$\text{Threshold level } P_{38.2} = ExpansionHigh - 0.382 \times (ExpansionHigh - ProtectedLow)$$
  $$\text{Condition: } RetracementLow \le P_{38.2} \iff R \ge 0.382$$

- **Bearish trend**: Dealing range from Protected Swing High ($ProtectedHigh$, impulse origin) to provisional Expansion Low ($ExpansionLow$, Confirmed Swing):
  $$\text{Retracement depth } R = \frac{RetracementHigh - ExpansionLow}{ProtectedHigh - ExpansionLow}$$
  $$\text{Threshold level } P_{38.2} = ExpansionLow + 0.382 \times (ProtectedHigh - ExpansionLow)$$
  $$\text{Condition: } RetracementHigh \ge P_{38.2} \iff R \ge 0.382$$

Retracement depth $\ge 38.2%$ is a **MANDATORY** gate for macro BOS. Without $\ge 38.2%$ depth ($R \ge 0.382$), NO break of the expansion extreme can be classified as `VALID_BOS`.

#### Layer separation

The 38.2% requirement applies strictly to the **Macro BOS Retracement Gate (Layer 3)**. It does **NOT** apply to microscopic candle-level pullbacks (Layer 1) or minor internal pullback validation (Layer 2).

### 9.2 Reduced-candle displacement parameter

The semantic reduced-candle displacement qualification is defined by `03_structural_semantic_authority.md` Section 3.3.2. This section owns the numeric source-backed support value used by that semantic rule:

- canonical support value: **5 previous candle extremes** in the retracement direction;
- the condition applies to rare retracements containing fewer than three opposing candles when the displacement is exceptionally large;
- the canonical macro retracement-depth minimum remains **38.2%**;
- the value may be exposed as a parameter only where explicitly approved; changing it must not redefine the semantic identity of the displacement-outlier condition.

This parameter replaces the former exactly-two-candle rule. No one-candle prohibition is encoded here.

### 9.3 Qualitative parameters

The qualitative requirement for LARGE / HIGH-MOMENTUM PRICE ACTION has no authoritative quantitative value at present and therefore must not be invented here.

Do not invent ATR, body-ratio, volatility, or standard-deviation thresholds and present them as canonical methodology.

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

