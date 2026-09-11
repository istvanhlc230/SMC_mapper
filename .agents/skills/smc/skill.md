---
name: true-smc
description: Governs and validates the canonical True SMC methodology and SMC_Mapper implementation. Use for True SMC audits, walkthroughs, implementation plans, code changes, regression validation, and methodology validation.
---

# TRUE SMC — CANONICAL STRUCTURAL RULESET

**Status:** Authoritative entry point
**Purpose:** Master validation contract for the True SMC methodology and SMC_Mapper.

## 1. Scope and authority

This skill is the master entry point for True SMC methodology and SMC_Mapper validation.

The methodology is organized into three logical layers. File ownership is documentation architecture; it must not create competing methodology categories.

```text
TRUE SMC METHODOLOGY
│
├── 1. Candle-Level Foundation
│
├── 2. Minor Structure
│
└── 3. Structural Lifecycle
    ├── 3.1 Major Structure
    ├── 3.2 Genesis
    ├── 3.3 Swing / Protected Structural Extreme
    ├── 3.4 BOS
    └── 3.5 CHoCH
```

The primary documentation ownership is:

- `true_smc_canonical.md` — Layer 1 and Layer 2 semantic foundations;
- `true_smc_structural_lifecycle.md` — Layer 3 lifecycle authority, Sections 3.1–3.5;
- `true_smc_choch.md` — detailed Section 3.5 CHoCH mechanics module; it does not create a separate methodology category or separate lifecycle ownership;
- `methodology_parameters.md` — numeric/configurable parameter definitions;
- `implementation.md` — implementation representation and state-transition requirements;
- `execution.md` — execution-layer semantics;
- `risk.md` — risk/scoring policy;
- `standard_smc.md` — generic terminology/reference only;
- `unverified.md` — uncertainty/provenance classification;
- `deprecated.md` — superseded/obsolete rules retained for traceability only.

A rule belongs to one primary semantic owner. Cross-category references must point to that owner rather than create competing definitions.

## 2. Category model

```text
STANDARD_SMC
TRUE_SMC_CANONICAL
  ├── Layer 1: Candle-Level Foundation
  └── Layer 2: Minor Structure
TRUE_SMC_STRUCTURAL_LIFECYCLE
  └── Layer 3: Structural Lifecycle
       ├── 3.1 Major Structure
       ├── 3.2 Genesis
       ├── 3.3 Swing / Protected Structural Extreme
       ├── 3.4 BOS
       └── 3.5 CHoCH
       
       detailed 3.5 module → true_smc_choch.md
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

Project-specific canonical True SMC semantic foundations for Layer 1 and Layer 2, including candle relationships, candle-level Valid Pullback qualification, Minor Structure, structural qualification prerequisites, liquidity/IDM foundations, and structural object separation.

Detailed Layer 3 lifecycle ownership is delegated to `true_smc_structural_lifecycle.md`.

See `true_smc_canonical.md`.

### TRUE_SMC_STRUCTURAL_LIFECYCLE

Canonical validated lifecycle authority for the complete Layer 3 Structural Lifecycle:

- 3.1 Major Structure — Definition & Scope;
- 3.2 Genesis;
- 3.3 Confirmed Swing & Protected Structural Extreme Lifecycle;
- 3.4 BOS Mechanics;
- 3.5 CHoCH lifecycle.

This document is part of the canonical methodology, not an independent competing methodology category.

Where older canonical wording conflicts with a later explicitly validated lifecycle rule, the later validated rule is authoritative and the conflicting wording is superseded/non-canonical.

See `true_smc_structural_lifecycle.md`.

### TRUE_SMC_CHOCH

Detailed module for Section 3.5 of the Structural Lifecycle.

`true_smc_choch.md` contains the validated 3.5.1–3.5.5 CHoCH mechanics in detail. It does not own a separate top-level lifecycle category. The lifecycle ownership remains with `true_smc_structural_lifecycle.md`.

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

## 3. Authority and conflict-resolution hierarchy

Authority is not determined merely by which file contains a rule.

For any conflict, apply this order:

```text
1. Explicitly validated / accepted newer True SMC rule
                    ↓
2. Current authoritative semantic owner
                    ↓
3. Older conflicting wording
                    ↓
4. DEPRECATED / SUPERSEDED traceability
```

The critical invariant is:

```text
NEWER VALIDATED RULE
        >
OLDER CONFLICTING RULE
```

A rule does not remain authoritative merely because it was historically stored in `true_smc_canonical.md`.

For lifecycle-specific rules:

```text
3.1–3.5 → true_smc_structural_lifecycle.md
3.5.1–3.5.5 detailed mechanics → true_smc_choch.md
```

`true_smc_choch.md` is the detailed module for 3.5, not a competing authority against the structural lifecycle document.

`STANDARD_SMC` supplies general terminology only. It cannot override project-specific True SMC methodology.

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
 ↓
CONFIRMATION LOCK
 ↓
FIRST NEW SVP / IDM CYCLE
 ↓
CONFIRMED SWING
 ↓
NORMAL BOS LIFECYCLE
```

Every higher-level event must consume a previously validated lower-level event. No stage may be skipped.

## 6. Final architecture rules

1. No methodology rule may be silently deleted.
2. Existing semantics must not be weakened merely to simplify file structure.
3. A rule belongs in one primary semantic category; cross-category references must point to the authoritative owner rather than create competing definitions.
4. `mapper` is the canonical implementation term; do not introduce `scanner` as the implementation name in newly written material.
5. Generic SMC/ICT terminology must remain subordinate to project-specific True SMC rules.
6. Configuration, scoring, visualization, or implementation convenience must never redefine structural meaning.
7. The structural engine and POI lifecycle engine remain separate subsystems. Structural rollover is communicated by an event; the structural engine does not directly delete or mutate POI registry state.
8. A later validated rule explicitly supersedes conflicting legacy wording; legacy text must not be treated as an alternative canonical path.
9. Numeric threshold ownership belongs to `methodology_parameters.md`; lifecycle and semantic documents reference the parameter definition rather than creating competing configurable values.
10. Newer explicitly validated methodology rules are authoritative over older conflicting rules regardless of the older rule's historical file location.
11. Documentation reorganization must preserve the validated rule itself; only duplicate ownership or superseded wording may be removed or converted to a reference.

## 7. Validation requirements

A code-review or validation agent must verify both:

### Methodology validation

Is the rule itself canonical, project-specific, parameterized, unverified, or deprecated?

The validator must first resolve chronology and authority before treating conflicting text as a methodology failure.

### Implementation validation

Does `SMC_Mapper` implement the accepted rule without skipping prerequisites, manufacturing structure, or confusing distinct state objects?

For lifecycle validation, the validator uses the Structural Lifecycle authority for the complete Layer 3 lifecycle:

- sections 3.1–3.4 → `true_smc_structural_lifecycle.md`;
- section 3.5 → `true_smc_structural_lifecycle.md`, with detailed mechanics in `true_smc_choch.md`.

Passing a regression test does not by itself prove that the underlying methodology rule is correct.

## 8. Migration-state contract

The canonical documentation ownership migration for the current True SMC methodology has been completed for the primary methodology files.

The intended architecture is now:

```text
true_smc_canonical.md
    → Layer 1 + Layer 2 semantic foundations

true_smc_structural_lifecycle.md
    → Layer 3, Sections 3.1–3.5

true_smc_choch.md
    → detailed Section 3.5 mechanics

methodology_parameters.md
    → numeric/configurable parameters
```

The validator must therefore treat these ownership boundaries as current, not as an in-progress migration state. If older lifecycle wording is encountered elsewhere, it must be classified against the current authoritative owner before use:

```text
CURRENT AUTHORITATIVE
DUPLICATE OF CURRENT AUTHORITATIVE
SUPERSEDED / LEGACY
```

Duplicate or superseded wording must never be promoted into a competing canonical rule merely because it remains physically present for traceability.

The migration was performed by rule ownership, not blind section deletion. The validated rule itself remains authoritative regardless of which historical file previously contained it.

**Acceptance condition:** No rule may be deleted or semantically changed merely because the architecture is reorganized. Any future methodology change must be explicit, separately approved, and independently validated.

