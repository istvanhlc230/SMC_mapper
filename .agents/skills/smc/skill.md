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
- `03_structural_lifecycle.md` — Layer 3 high-level lifecycle authority;
- `03_structural_lifecycle_bos.md` — detailed Section 3.4 BOS mechanics, subordinate to `03_structural_lifecycle.md`;
- `03_structural_lifecycle_choch.md` — detailed Section 3.5 CHoCH mechanics, subordinate to `03_structural_lifecycle.md`;
- `methodology_parameters.md` — numeric/configurable parameter definitions;
- `06_implementation.md` — implementation representation and state-transition requirements;
- `04_execution.md` — execution-layer semantics;
- `05_risk.md` — risk/scoring policy;
- `independent_validator_prompt.md` — explicit validator handoff; it restates canonical rules for independent validation and is not a competing semantic owner.

A rule belongs to one primary semantic owner. Cross-category references must point to that owner rather than create competing definitions.

## 2. Source classification and authority

Generic SMC/ICT terminology is context only. It cannot replace project-specific True SMC semantics.

Use these classifications when provenance is incomplete:

- **CANONICAL / VALIDATED** — accepted True SMC rule owned by a current semantic-owner document;
- **PARAMETERIZED** — implementation/configuration value whose identity is defined by the methodology but whose numeric value is configurable;
- **SOURCE-PENDING / UNVERIFIED** — claim that lacks sufficient provenance for presentation as universal SMC knowledge; it must not be silently promoted;
- **OBSOLETE / SUPERSEDED** — historical wording that must not drive validation or implementation.

Important examples of SOURCE-PENDING claims:

- a quantitative definition of `large/high-momentum`;
- any invented ATR, body-ratio, volatility, or standard-deviation threshold;
- treating exact 38.2%, >=3 opposing candles, >=5 prior extremes, the three-pillar OB model, or repository scoring weights as universal SMC axioms.

Project-specific accepted rules remain authoritative even when their numeric parameters are not universal SMC facts.

## 3. Mandatory structural principles

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

## 4. Canonical dependency chain

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

## 5. Retracement qualification invariant

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

## 6. Lifecycle invariants

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

## 7. Documentation architecture

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
independent_validator_prompt.md
```

The BOS and CHoCH files are detailed subordinate modules, not competing top-level authorities. The validator prompt is an explicit handoff artifact, not a methodology source.

## 8. Generic terminology boundary

General SMC/ICT terms such as liquidity, BSL/SSL, swing, IDM, BOS, CHoCH, displacement, FVG and OB may be used as terminology. Their presence does not establish universal thresholds, lifecycle rules, object identity, or qualification semantics.

In particular:

- generic IDM does not permit arbitrary local highs/lows to become IDM;
- generic BOS does not replace project structural prerequisites and break-acceptance rules;
- generic CHoCH does not replace the governing Trading Range boundary rule;
- FVG, displacement, liquidity, and OB do not independently create IDM, BOS, CHoCH, or a tradable POI.

## 9. Implementation validation

The validator must distinguish methodology validation from implementation validation.

Methodology validation asks whether a rule is canonical, parameterized, source-pending, obsolete, or conflicting. Implementation validation asks whether `SMC_Mapper` implements the accepted rule without skipping prerequisites, manufacturing structure, or confusing distinct state objects.

`06_implementation.md` defines implementation representation, state-transition, anti-pattern, and regression requirements. Implementation must consume methodology; it must not redefine it.

## 10. Execution and risk boundaries

`04_execution.md` owns POI and entry/execution semantics. Execution must consume structural state and must never manufacture structural events.

`05_risk.md` owns scoring and risk policy. Risk and scoring consume canonical state and must never create or validate structure.

`methodology_parameters.md` owns numeric/configurable parameters. Configuration may change permitted thresholds but never structural identity.

The structural engine and POI lifecycle engine remain separate subsystems. Structural rollover is communicated by an event; the structural engine does not directly delete or mutate POI registry state.

## 11. Authority and conflict resolution

```text
CURRENT VALIDATED TRUE SMC RULE
            ↓
CURRENT SEMANTIC OWNER
            ↓
OLDER CONFLICTING WORDING
            ↓
OBSOLETE / SUPERSEDED HISTORY
```

Do not retain historical obsolete wording merely as an active reference source. If an old rule is relevant to traceability, its supersession should be recorded in the owning canonical document or commit history, not maintained as a second rule source.

**Canonical entry-point verdict: PASS / CLOSED.**
