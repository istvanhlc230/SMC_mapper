---
name: true-smc
description: Entry point for the canonical True SMC skill. This file contains references only; methodology rules are defined in the semantic-owner documents below.
---

# TRUE SMC — SKILL INDEX

This file is **reference/index only**.

It must not contain competing methodology definitions, duplicate rules, implementation logic, or alternate interpretations.

Read the referenced documents in this order when the full methodology is required.

## 1. Core methodology

1. `01_micro_structure.md`
   - Canonical candle-level microstructure observations and relationships

2. `02_minor_structure.md`
   - Layer 2 Minor Structure
   - Pullback Formation, Candle-Level Valid Pullback, verified pullback extreme
   - Minor liquidity / IDM foundations
   - Does **not** own Major Structural Qualification

3. `03_structural_semantic_authority.md`
   - Shared Layer 3 Major Structural Semantic Authority
   - Major Structure ontology and structural qualification
   - Confirmed Structural Swing / Protected Structural Extreme lifecycle
   - Shared lifecycle invariants

4. `04_BOS_mechanics.md`
   - Dedicated BOS mechanics and lifecycle
   - Continuation and opposing-break classification boundaries
   - Consumes shared structural qualification; does not redefine it

5. `05_CHOCH_mechanics.md`
   - Dedicated CHoCH mechanics and lifecycle
   - Fallback Major IDM / Major IDM Sweep distinctions
   - LTF-CHoCH context route after HTF POI/core-liquidity interaction
   - Consumes shared structural state; does not redefine it

## 2. Execution and risk

6. `06_execution.md`
   - Execution-layer semantics
   - Momentum Candle remains a qualitative execution observation / SOURCE-PENDING filter
   - Execution consumes structure; it does not create structure

7. `07_risk.md`
   - Risk policy and structural risk boundaries
   - Risk consumes structure; it does not create structure

## 3. Parameters and implementation representation

8. `methodology_parameters.md`
   - Numeric and configurable methodology parameters
   - Parameter ownership only

9. `08_implementation.md`
   - Implementation representation requirements
   - State-transition and validation requirements
   - Must consume canonical methodology; it must not redefine it

## 4. Source reconciliation governance

`source_reconciliation.md`
- Controlled source-to-canonical reconciliation workflow
- Human approval gate, contract ledger, change set, and independent validation
- Process authority only; it does not define SMC methodology

## 5. Documentation authority

Semantic ownership is:

```text
MICRO STRUCTURE
    → 01_micro_structure.md

MINOR STRUCTURE
    → 02_minor_structure.md

STRUCTURAL SEMANTIC AUTHORITY
    → 03_structural_semantic_authority.md

BOS MECHANICS
    → 04_BOS_mechanics.md

CHoCH MECHANICS
    → 05_CHOCH_mechanics.md

EXECUTION
    → 06_execution.md

RISK
    → 07_risk.md

NUMERIC / CONFIGURABLE PARAMETERS
    → methodology_parameters.md

IMPLEMENTATION REPRESENTATION / EXECUTABLE SCORING MAPPING
    → 08_implementation.md
```

A rule must have one primary semantic owner. Other documents may reference that rule, but must not create a competing definition.

## 6. Precedence rule

When documents conflict:

```text
CURRENT SEMANTIC OWNER
        >
CROSS-REFERENCE
        >
OLDER / SUPERSEDED WORDING
```

Do not use generic SMC knowledge to override the project's canonical semantic-owner documents.

## 7. Canonical document set

```text
.agents/skills/smc/
├── skill.md
├── 01_micro_structure.md
├── 02_minor_structure.md
├── 03_structural_semantic_authority.md
├── 04_BOS_mechanics.md
├── 05_CHOCH_mechanics.md
├── 06_execution.md
├── 07_risk.md
├── 08_implementation.md
└── methodology_parameters.md
```
