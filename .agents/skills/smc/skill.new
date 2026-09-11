---
name: true-smc
description: Governs and validates the canonical True SMC methodology and SMC_Mapper implementation. Use for True SMC audits, walkthroughs, implementation plans, code changes, regression validation, and methodology validation.
---

# TRUE SMC — CANONICAL STRUCTURAL RULESET

**Status:** Authoritative entry point
**Purpose:** Master validation contract for the True SMC methodology and SMC_Mapper.

## 1. Scope and authority

The methodology is organized into three logical layers. File ownership is documentation architecture; it must not create competing methodology categories.

```text
TRUE SMC METHODOLOGY
│
├── 1. Candle-Level Foundation
├── 2. Minor Structure
└── 3. Structural Lifecycle
    ├── 3.1 Major Structure
    ├── 3.2 Genesis
    ├── 3.3 Swing / Protected Structural Extreme
    ├── 3.4 BOS
    └── 3.5 CHoCH
```

Primary documentation ownership:

- `01_candle_level_foundation.md` — Layer 1 candle-level foundation;
- `02_minor_structure.md` — Layer 2 minor structure, pullback qualification, liquidity and IDM foundations;
- `03_structural_lifecycle.md` — Layer 3 lifecycle authority, Sections 3.1–3.5;
- `03_structural_lifecycle_bos.md` — detailed Section 3.4 BOS mechanics, subordinate to `03_structural_lifecycle.md`;
- `03_structural_lifecycle_choch.md` — detailed Section 3.5 CHoCH mechanics, subordinate to `03_structural_lifecycle.md`;
- `methodology_parameters.md` — numeric/configurable parameter definitions;
- `06_implementation.md` — implementation representation and state-transition requirements;
- `04_execution.md` — execution-layer semantics;
- `05_risk.md` — risk/scoring policy;
- `standard_smc.md` — generic terminology/reference only;
- `unverified.md` — uncertainty/provenance classification;
- `deprecated.md` — superseded/obsolete rules retained for traceability only.

A rule belongs to one primary semantic owner. Cross-category references must point to that owner rather than create competing definitions.

## 2. Category model

```text
STANDARD_SMC
01_CANDLE_LEVEL_FOUNDATION
02_MINOR_STRUCTURE
03_STRUCTURAL_LIFECYCLE
  ├── detailed 3.4 mechanics → 03_structural_lifecycle_bos.md
  └── detailed 3.5 mechanics → 03_structural_lifecycle_choch.md
04_EXECUTION
05_RISK
06_IMPLEMENTATION
METHODOLOGY_PARAMETERS
UNVERIFIED
DEPRECATED
```

Generic SMC/ICT terminology remains subordinate to project-specific True SMC semantics.

## 3. Authority and conflict resolution

Authority is not determined merely by which file contains a rule.

```text
1. Explicitly validated / accepted newer True SMC rule
                    ↓
2. Current authoritative semantic owner
                    ↓
3. Older conflicting wording
                    ↓
4. DEPRECATED / SUPERSEDED traceability
```

Critical invariant:

```text
NEWER VALIDATED RULE
        >
OLDER CONFLICTING RULE
```

`standard_smc.md` supplies terminology only. `unverified.md` and `deprecated.md` are non-authoritative and cannot silently become canonical.

## 4. Mandatory structural principles

```text
CANDLE-LEVEL VALID PULLBACK ≠ STRUCTURALLY VALID PULLBACK
CANDLE-LEVEL VALID PULLBACK ≠ IDM
STRUCTURALLY VALID PULLBACK → IDM ELIGIBILITY
PULLBACK EXTREME ≠ AUTOMATIC IDM
IDM SWEEP ≠ BOS
IDM SWEEP ≠ CHoCH
LIQUIDITY ≠ STRUCTURE
CHoCH ≠ BOS
CHoCH-CAUSING LEG ≠ AUTOMATIC PULLBACK
CHoCH-CAUSING LEG ≠ AUTOMATIC IDM
DEEP RETRACEMENT ≠ AUTOMATIC STRUCTURAL RESET
HISTORICAL STRUCTURE ≠ CURRENT GOVERNING STRUCTURE
IDM ≠ POI
FVG ≠ STANDALONE POI
POI ≠ ENTRY EXECUTION
SCORING ≠ STRUCTURAL VALIDATION
CONFIGURATION ≠ CANONICAL METHODOLOGY
CONFIRMED SWING ≠ PROTECTED STRUCTURAL EXTREME
PROTECTED STRUCTURAL EXTREME ≠ AUTOMATIC CHOCH
PHYSICAL EXTERNAL BREAK ≠ VALID_BOS
WICK BREAK OF FALLBACK PROXY ≠ VALID_BOS
WICK BREAK OF FALLBACK PROXY ≠ VALID_CHoCH
MAJOR_IDM_SWEEP ≠ CONFIRMED_SWING_POINT
```

## 5. Canonical dependency chain

Continuation/BOS path:

```text
RAW OHLC
 ↓
CANDLE RELATIONSHIPS
 ↓
CANDLE-LEVEL VALID PULLBACK
 ↓
STRUCTURAL QUALIFICATION
 ↓
STRUCTURALLY VALID PULLBACK
 ↓
VERIFIED PULLBACK EXTREME
 ↓
LIQUIDITY
 ↓
ACTIVE PULLBACK POINTER
 ↓
IDM ELIGIBILITY
 ↓
ACTIVE/MINOR IDM
 ↓
IDM TAKEOUT
 ↓
SWING CONFIRMATION GATE
 ↓
CONFIRMED STRUCTURAL SWING
 ↓
RETRACEMENT SUFFICIENCY
 ↓
PHYSICAL EXTERNAL BREAK
 ↓
BREAK CLASSIFICATION
 ↓
VALID_BOS
 ↓
TRADING RANGE ROLLOVER
```

CHoCH path:

```text
CURRENT TRADING RANGE
 ↓
GOVERNING OPPOSING PROTECTED STRUCTURAL EXTREME
 ↓
PHYSICAL BOUNDARY VIOLATION
 ↓
CHoCH STRUCTURAL PREREQUISITES
 ↓
VALID_CHoCH
 ↓
NEW TREND LIFECYCLE
 ↓
CHoCH-CAUSING LEG = INITIAL ACTIVE IMPULSIVE LEG
 ↓
CONFIRMATION LOCK
 ↓
FIRST NEW SVP / IDM CYCLE
 ↓
CONFIRMED SWING
 ↓
NORMAL BOS LIFECYCLE
```

Every higher-level event must consume previously validated lower-level state. No stage may be skipped.

## 6. Retracement qualification invariant

The canonical default minimum retracement is 38.2% with the validated exactly-two-candle momentum exception:

```text
>=3 opposing candles AND >= minimum depth
```

or:

```text
EXACTLY 2 OPPOSING CANDLES
AND LARGE / HIGH-MOMENTUM PRICE ACTION
AND (>=5 PRIOR CANDLE EXTREMES SWEPT/ENGULFED OR DEPTH >=38.2%)
```

There is no automatic one-candle exception. High momentum remains qualitative unless independently verified quantitatively. Do not invent ATR/body-ratio/volatility/std-dev thresholds as canonical methodology.

## 7. Lifecycle invariants

- Confirmed Swing ≠ Protected Structural Extreme.
- Protected Structural Extreme locks only through valid BOS.
- Wick-BOS is immediate when an eligible non-fallback external continuation level is penetrated and the close is at/inside the level.
- Fallback Major IDM is a Range-Boundary Proxy, not Real Major IDM.
- Fallback wick breach is `MAJOR_IDM_SWEEP`, not BOS or CHoCH, and only unlocks the Swing Confirmation Gate.
- `MAJOR_IDM_SWEEP` does not automatically create Confirmed Swing.
- First post-break SVP does not automatically equal Real Major IDM; the full eligibility chain is required.
- Later candles cannot retroactively rewrite earlier classifications.
- VALID_BOS closes the prior range and starts a new lifecycle.
- VALID_CHoCH terminates the old trend, starts the new trend, and locks confirmation until the first qualifying post-CHoCH SVP/IDM cycle completes.
- The CHoCH-causing leg becomes the new initial active impulsive leg.

## 8. Implementation validation

The validator must distinguish:

### Methodology validation

Is the rule canonical, project-specific, parameterized, unverified, or deprecated? Resolve chronology and authority before treating conflicting text as a methodology failure.

### Implementation validation

Does `SMC_Mapper` implement the accepted rule without skipping prerequisites, manufacturing structure, or confusing distinct state objects?

`06_implementation.md` defines representation, state-transition, anti-pattern, and regression requirements. Implementation must consume methodology; it must not redefine it.

## 9. Execution and risk boundaries

`04_execution.md` owns POI and entry/execution semantics. Execution must consume structural state and must never manufacture structural events.

`05_risk.md` owns scoring and risk policy. Risk and scoring consume canonical state and must never create or validate structure.

`methodology_parameters.md` owns numeric/configurable parameters. Configuration may change permitted thresholds but never structural identity.

The structural engine and POI lifecycle engine remain separate subsystems. Structural rollover is communicated by an event; the structural engine does not directly delete or mutate POI registry state.

## 10. Documentation migration invariant

The category-based file structure is now the canonical documentation architecture. Renaming or splitting files must preserve validated rules and must not weaken semantics.

```text
01_candle_level_foundation.md
02_minor_structure.md
03_structural_lifecycle.md
03_structural_lifecycle_bos.md
03_structural_lifecycle_choch.md
04_execution.md
05_risk.md
06_implementation.md
methodology_parameters.md
standard_smc.md
unverified.md
deprecated.md
```

The detailed BOS and CHoCH files are subordinate to category 03 and do not create separate top-level methodology categories. Duplicate or superseded wording must never be promoted into competing canonical behavior.
