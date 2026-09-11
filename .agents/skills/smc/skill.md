---
name: true-smc
description: Governs and validates the canonical True SMC methodology and SMC_Mapper implementation. Use for True SMC audits, walkthroughs, implementation plans, code changes, regression validation, and methodology validation.
---

# TRUE SMC — CANONICAL STRUCTURAL RULESET

**Status:** Authoritative entry point
**Purpose:** Master validation contract for the True SMC methodology and SMC_Mapper.

## 1. Scope and authority

This skill is the master entry point for True SMC methodology and SMC_Mapper validation.

The detailed rules are organized into dedicated category documents. The canonical structural lifecycle is split by ownership:

- `true_smc_canonical.md` — core semantic definitions and foundational structural rules;
- `true_smc_structural_lifecycle.md` — validated Major Structure, Swing/Protected Extreme, and BOS lifecycle rules (3.1–3.4);
- `true_smc_choch.md` — validated CHoCH lifecycle rules (3.5.1–3.5.5).

A rule belongs to one primary category. Cross-category references must point to the authoritative category rather than create competing definitions.

## 2. Category model

```text
STANDARD_SMC
TRUE_SMC_CANONICAL
  ├── TRUE_SMC_STRUCTURAL_LIFECYCLE
  │      └── 3.1–3.4
  └── TRUE_SMC_CHOCH
         └── 3.5.1–3.5.5
METHODOLOGY_PARAMETER
IMPLEMENTATION
EXECUTION
RISK
UNVERIFIED
DEPRECATED
```

### STANDARD_SMC

General SMC/ICT concepts used as the baseline vocabulary. Generic terminology must not override project-specific True SMC semantics.

See `standard_smc.md`.

### TRUE_SMC_CANONICAL

Project-specific canonical True SMC semantic rules, including candle relationships, Valid Pullback qualification, liquidity, IDM identity, structural object separation, and foundational dependencies.

Detailed structural lifecycle ownership is delegated to the lifecycle extensions below.

See `true_smc_canonical.md`.

### TRUE_SMC_STRUCTURAL_LIFECYCLE

Canonical validated lifecycle extension for:

- 3.1 Major Structure — Definition & Scope;
- 3.2 Major Structure — Unit of Origin;
- 3.3 Confirmed Swing & Protected Structural Extreme Lifecycle;
- 3.4 BOS Mechanics, including 3.4.1–3.4.5.

This document is part of the canonical methodology, not an independent competing category. Where older canonical wording conflicts with an explicitly validated lifecycle rule in this document, the later validated rule is authoritative and the conflicting wording is non-canonical/legacy.

See `true_smc_structural_lifecycle.md`.

### TRUE_SMC_CHOCH

Canonical validated lifecycle extension for CHoCH:

- 3.5.1 CHoCH — Definition & Unit of Origin;
- 3.5.2 Physical Boundary Break;
- 3.5.3 Break Classification: Wick vs Body Close;
- 3.5.4 Fallback Major IDM / CHoCH Exception;
- 3.5.5 Downstream State Changes & Regime Initialization.

This document owns the validated CHoCH lifecycle. Older CHoCH wording in `true_smc_canonical.md` or `true_smc_structural_lifecycle.md` is retained only for traceability and must not be treated as a competing canonical path.

See `true_smc_choch.md`.

### METHODOLOGY_PARAMETER

Numeric or configurable methodology parameters such as the canonical 38.2% default and momentum/qualification thresholds.

A parameter changes a threshold; it does not redefine the semantic identity of a structural object.

See `methodology_parameters.md`.

### IMPLEMENTATION

Rules governing how SMC_Mapper represents and transitions canonical methodology state, including the structural state machine, implementation anti-patterns, and regression coverage requirements.

The mapper must implement the methodology; it must not redefine it.

See `implementation.md`.

### EXECUTION

Canonical execution-layer concepts including POI, Valid Order Flow, Valid Order Block, FVG validation, and entry modules.

Execution logic must consume structural state and must never manufacture structural events.

See `execution.md`.

### RISK

Risk, scoring, quality tiers, RR requirements, and related execution constraints.

Scoring and risk evaluation consume canonical state; they must never create or validate structure.

See `risk.md`.

### UNVERIFIED

Claims, thresholds, or methodology interpretations that are not sufficiently verified to be treated as canonical.

See `unverified.md`.

### DEPRECATED

Superseded or obsolete rules retained for traceability only. Deprecated rules must not silently re-enter canonical methodology or implementation semantics.

See `deprecated.md`.

## 3. Authority hierarchy

When evaluating an implementation:

```text
TRUE_SMC_CANONICAL
        ↓
TRUE_SMC_STRUCTURAL_LIFECYCLE
        ↓
TRUE_SMC_CHOCH
        ↓
METHODOLOGY_PARAMETER
        ↓
IMPLEMENTATION
        ↓
EXECUTION / RISK
```

`TRUE_SMC_STRUCTURAL_LIFECYCLE` and `TRUE_SMC_CHOCH` are explicit extensions of the canonical methodology. They do not replace the broader semantic definitions in `TRUE_SMC_CANONICAL`.

For lifecycle-specific conflicts, the explicitly validated lifecycle document that owns the section is authoritative. In particular, `TRUE_SMC_CHOCH` owns 3.5.1–3.5.5; `TRUE_SMC_STRUCTURAL_LIFECYCLE` owns 3.1–3.4.

`STANDARD_SMC` supplies general terminology only. It cannot override `TRUE_SMC_CANONICAL` or its validated lifecycle extensions.

`UNVERIFIED` and `DEPRECATED` are non-authoritative and must never be promoted into canonical behavior without explicit methodology approval.

## 4. Mandatory structural principles

The following principles remain mandatory across the category documents:

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
```

Every higher-level event must consume a previously validated lower-level event. No stage may be skipped.

## 6. Final architecture rules

1. No methodology rule may be silently deleted.
2. Existing semantics must not be weakened merely to simplify file structure.
3. A rule belongs in one primary category; cross-category references must point to the authoritative category rather than create competing definitions.
4. `mapper` is the canonical implementation term; do not introduce `scanner` as the implementation name in newly written material.
5. Generic SMC/ICT terminology must remain subordinate to project-specific True SMC rules.
6. Configuration, scoring, visualization, or implementation convenience must never redefine structural meaning.
7. The structural engine and POI lifecycle engine remain separate subsystems. Structural rollover is communicated by an event; the structural engine does not directly delete or mutate POI registry state.
8. A later validated lifecycle rule explicitly supersedes conflicting legacy wording; legacy text must not be treated as an alternative canonical path.
9. Numeric threshold ownership belongs to `methodology_parameters.md`; lifecycle and semantic documents reference the parameter definition rather than creating competing configurable values.

## 7. Validation requirements

A code-review or validation agent must verify both:

### Methodology validation

Is the rule itself canonical, project-specific, parameterized, unverified, or deprecated?

### Implementation validation

Does `SMC_Mapper` implement the accepted rule without skipping prerequisites, manufacturing structure, or confusing distinct state objects?

For lifecycle validation, the validator must use the owning document for the section under review. In particular:

- sections 3.1–3.4 → `true_smc_structural_lifecycle.md`;
- sections 3.5.1–3.5.5 → `true_smc_choch.md`.

Passing a regression test does not by itself prove that the underlying methodology rule is correct.

## 8. Completeness contract

The final category architecture represents the complete pre-reorganization ruleset as follows:

- Sections 1–35, 42, and 49 → `true_smc_canonical.md`
- Sections 43 → `deprecated.md`
- Section 44 → `risk.md`
- Sections 45–48 → `implementation.md`
- Sections 36–41 → `execution.md`, with risk boundaries also represented in `risk.md`
- Section 9 parameter semantics → `methodology_parameters.md`
- General terminology boundary → `standard_smc.md`
- Provenance/uncertainty classification → `unverified.md`

Validated lifecycle ownership is now:

```text
true_smc_structural_lifecycle.md → 3.1–3.4
true_smc_choch.md                → 3.5.1–3.5.5
```

These destinations are the final architecture; historical migration ledgers are not required for agent operation.

**Acceptance condition:** No rule may be deleted or semantically changed merely because the architecture is reorganized. Any future methodology change must be explicit, separately approved, and independently validated.
