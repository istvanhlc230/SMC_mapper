---
name: true-smc
description: Governs and validates the canonical True SMC methodology and SMC_Mapper implementation. Use for True SMC audits, walkthroughs, implementation plans, code changes, regression validation, and methodology validation.
---

# TRUE SMC — CANONICAL STRUCTURAL RULESET

**Status:** Authoritative entry point
**Purpose:** Master validation contract for the True SMC methodology and SMC_Mapper.

## 1. Scope and authority

This skill is the master entry point for True SMC methodology and SMC_Mapper validation.

The detailed rules are organized into dedicated category documents. The original pre-reorganization ruleset is preserved in `skill_old.md` as an immutable baseline for completeness verification.

**No rule from `skill_old.md` may be deleted during reorganization.** Reorganization is structural only unless a rule is explicitly reviewed and changed in a separate approved methodology change.

## 2. Category model

The skill is organized into eight focused documents:

```text
STANDARD_SMC
TRUE_SMC_CANONICAL
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

Project-specific canonical True SMC structural rules, including Valid Pullback qualification, IDM lifecycle, swing confirmation, BOS, CHoCH, Trading Range, genesis, and canonical structural separation.

See `true_smc_canonical.md`.

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
METHODOLOGY_PARAMETER
        ↓
IMPLEMENTATION
        ↓
EXECUTION / RISK
```

`STANDARD_SMC` supplies general terminology only. It cannot override `TRUE_SMC_CANONICAL`.

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
```

## 5. Canonical dependency chain

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
SWING CONFIRMATION
 ↓
CONFIRMED STRUCTURAL SWING
 ↓
PHYSICAL STRUCTURAL BREAK
 ↓
BREAK ACCEPTANCE
 ↓
BOS
 ↓
NEW TRADING RANGE
```

CHoCH is a separate regime transition based on violation of the governing Trading Range boundary. The CHoCH-causing leg becomes the initial active impulsive leg of the new trend, but CHoCH does not automatically create a pullback, IDM, or protected swing.

## 6. Reorganization rules

1. No existing methodology rule may be silently deleted.
2. Existing semantics must not be weakened merely to simplify file structure.
3. A rule belongs in one primary category; cross-category references should link to the authoritative category rather than duplicate competing definitions.
4. `skill_old.md` is the preservation baseline for migration completeness.
5. `CATEGORY_MAP.md` remains unchanged during migration and may be used as an audit/classification ledger.
6. `mapper` is the canonical implementation term; do not introduce `scanner` as the implementation name in newly written material.
7. Generic SMC/ICT terminology must remain subordinate to project-specific True SMC rules.
8. Configuration, scoring, visualization, or implementation convenience must never redefine structural meaning.

## 7. Validation requirements

A code-review or validation agent must verify both:

### Methodology validation

Is the rule itself canonical, project-specific, parameterized, unverified, or deprecated?

### Implementation validation

Does `SMC_Mapper` implement the accepted rule without skipping prerequisites, manufacturing structure, or confusing distinct state objects?

Passing a regression test does not by itself prove that the underlying methodology rule is correct.

## 8. Migration status

The major rule bodies from the preserved pre-reorganization ruleset are now distributed across the category documents:

- Sections 1–35, 42, and 49 → `true_smc_canonical.md`
- Section 43 → `deprecated.md`
- Section 44 → `risk.md`
- Sections 45–48 → `implementation.md`
- Sections 36–41 → `execution.md` with risk boundaries also represented in `risk.md`
- Section 9 parameter semantics → `methodology_parameters.md`
- General terminology boundary → `standard_smc.md`
- Provenance/uncertainty classification → `unverified.md`

`skill_old.md` remains the immutable source baseline. The migration is structurally complete at the section level, but a final rule-by-rule audit against `skill_old.md` and `CATEGORY_MAP.md` is still required before `skill_old.md` can be considered archival-only rather than the migration control baseline.

**Important:** No absence from a category document is permission to delete a rule. The final audit must confirm every original rule, invariant, test requirement, and anti-pattern has a category owner and remains semantically intact.