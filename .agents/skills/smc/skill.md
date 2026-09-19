---
name: true-smc
description: Entry point for the canonical True SMC skill. This file contains references only; methodology rules are defined in the semantic-owner documents below.
---

# TRUE SMC — SKILL INDEX

This file is **reference/index only**.

It must not contain competing methodology definitions, duplicate rules, implementation logic, or alternate interpretations.

Read the referenced documents in this order when the full methodology is required.

## 1. Core methodology

1. `01_candle_level_foundation.md`
   - Candle-level observations and relationships
   - Candle-level Valid Pullback
   - Inside / outside bar semantics
   - Equal-extreme and candle-level foundation rules

2. `02_minor_structure.md`
   - Layer 2 Minor Structure
   - Verified pullback extreme
   - Minor liquidity / IDM foundations
   - Minor structural lifecycle inputs
   - Does **not** own Major Structural Retracement Qualification

3. `03_structural_lifecycle.md`
   - Layer 3 Major Structural Lifecycle
   - Major Structural Retracement Qualification
   - Structurally Valid Pullback
   - Structural extremes and swing lifecycle
   - IDM lifecycle
   - Structural state transitions
   - Canonical semantic owner of Major Structural Qualification

4. `03_structural_lifecycle_bos.md`
   - Subordinate BOS module
   - BOS prerequisites and break classification
   - Consumes Major Structural Qualification from `03_structural_lifecycle.md`
   - Does not redefine Major Structural Qualification

5. `03_structural_lifecycle_choch.md`
   - Subordinate CHoCH module
   - CHoCH prerequisites and lifecycle
   - Fallback Major IDM / Major IDM Sweep distinctions
   - Consumes structural state from `03_structural_lifecycle.md`

## 2. Execution and risk

6. `04_execution.md`
   - Execution-layer semantics
   - Valid POIs
   - Entry modules
   - POI refinement
   - Execution consumes structure; it does not create structure

7. `05_risk.md`
   - Risk and scoring policy
   - Structural stop / invalidation boundaries
   - Risk consumes structure; it does not create structure

## 3. Parameters and implementation representation

8. `methodology_parameters.md`
   - Numeric and configurable methodology parameters
   - Parameter ownership only
   - Does not redefine semantic methodology

9. `06_implementation.md`
   - Implementation representation requirements
   - State-transition requirements
   - Regression and validation requirements
   - Must consume the canonical methodology; it must not redefine it

## 4. Documentation authority

Semantic ownership is:

```text
CANDLE-LEVEL FOUNDATION
    → 01_candle_level_foundation.md

MINOR STRUCTURE
    → 02_minor_structure.md

MAJOR STRUCTURAL LIFECYCLE
    → 03_structural_lifecycle.md

BOS DETAILS
    → 03_structural_lifecycle_bos.md

CHoCH DETAILS
    → 03_structural_lifecycle_choch.md

EXECUTION
    → 04_execution.md

RISK
    → 05_risk.md

NUMERIC / CONFIGURABLE PARAMETERS
    → methodology_parameters.md

IMPLEMENTATION REPRESENTATION
    → 06_implementation.md
```

A rule must have one primary semantic owner. Other documents may reference that rule, but must not create a competing definition.

## 5. Audit rule

When documents conflict:

```text
CURRENT SEMANTIC OWNER
        >
CROSS-REFERENCE
        >
OLDER / SUPERSEDED WORDING
```

Do not use generic SMC knowledge to override the project's canonical semantic-owner documents.

## 6. Canonical document set

```text
.agents/skills/smc/
├── skill.md
├── 01_candle_level_foundation.md
├── 02_minor_structure.md
├── 03_structural_lifecycle.md
├── 03_structural_lifecycle_bos.md
├── 03_structural_lifecycle_choch.md
├── 04_execution.md
├── 05_risk.md
├── 06_implementation.md
└── methodology_parameters.md
```
