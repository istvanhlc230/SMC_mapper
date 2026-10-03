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
   - First-BOS bootstrap initialization and post-CHoCH first-BOS lifecycle boundary
   - Shared lifecycle invariants

4. `04_BOS_mechanics.md`
   - Dedicated BOS mechanics and lifecycle
   - Continuation and opposing-break classification boundaries
   - Consumes shared structural qualification; does not redefine it

5. `05_CHOCH_mechanics.md`
   - Dedicated CHoCH mechanics and lifecycle
   - Major IDM / Major IDM Sweep interaction and lifecycle
   - LTF-CHoCH context route after HTF POI/core-liquidity interaction
   - Consumes shared structural state; does not redefine it

## 2. Execution and risk

6. `06_execution.md`
   - Execution-layer semantics
   - POI / Order Flow / Order Block / Rejection Block semantics
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
   - First-BOS bootstrap/process-state representation and `dynamic_retracement_extreme` lifecycle mapping (`E_retrace(t)` is mathematical notation)
   - Must consume canonical methodology; it must not redefine it

10. `trading_policy.md`
   - Configurable trading-plan and account-risk policy
   - Position sizing, risk budgets, session windows, news gate, trade-count limits, logging
   - Does not redefine structural SMC semantics

11. `platform_execution.md`
   - Broker/exchange execution and deterministic backtest contract
   - Order, fill, position, quote, slippage, reconciliation, and failure semantics
   - Does not redefine True SMC methodology or trading-policy semantics

12. `countertrend_scenarios.md`
   - Canonical composition of the three source-defined countertrend scenarios
   - Reuses IDM, liquidity, POI, CHoCH, entry, target, and risk owners
   - Does not introduce alternate structural semantics

## 4. Source reconciliation governance

`source_reconciliation.md`
- Controlled source-to-canonical reconciliation workflow
- Human approval gate, contract ledger, change set, and independent validation
- Process authority only; it does not define SMC methodology

## 5. Global structural terminology and namespace boundary

The canonical structural hierarchy is:

OHLC / CANDLE PRIMITIVES
        ↓
MICROSTRUCTURE
        ↓
MINOR STRUCTURE
  (Candle-Level Valid Pullback / Minor Structural Swing / Minor IDM)
        ↓
MAJOR / EXTERNAL STRUCTURE
  (Confirmed Structural Swing / Protected External Boundary / Major IDM)
        ↓
EXTERNAL STRUCTURAL BREAK
  (Structural Swing Break / VALID_BOS)

Terminology rules:
- Microstructure owns candle-level geometry and observations.
- Minor Structure owns validated sequential structure produced from Layer-1 observations.
- Major / External Structure owns CONFIRMED_STRUCTURAL_SWING, Protected External Boundary / Protected Structural Extreme, Major IDM, and the structural lifecycle.
- BOS is an external/major structural break, not a generic candle break or Minor Structural Swing break.
- CHoCH is a structural lifecycle transition whose governing reference is context-dependent; the LTF Structural Glitch does not promote a Minor object into Major Structure.
- Unqualified implementation-domain types such as Swing, Break, or Structure must not be used where a canonical layer-specific semantic type is required.
- Existing canonical names (CONFIRMED_STRUCTURAL_SWING, STRUCTURAL_SWING_BREAK, VALID_BOS, MINOR_IDM, MAJOR_IDM) remain authoritative and must not be replaced by parallel synonyms.
- Generic words such as “structure”, “swing”, or “break” may appear in descriptive prose only when the semantic owner is unambiguous. Normative rules and implementation contracts must use the specific canonical object/event name.

This is a terminology boundary, not a new SMC rule. It prevents Microstructure, Minor Structure, and Major/External Structure from being conflated while preserving the semantic-owner model.

## 6. Documentation authority

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

TRADING POLICY
    → trading_policy.md

PLATFORM EXECUTION / BACKTEST
    → platform_execution.md

COUNTERTREND SCENARIOS
    → countertrend_scenarios.md
```

A rule must have one primary semantic owner. Other documents may reference that rule, but must not create a competing definition.

## 7. Precedence rule

When documents conflict:

```text
CURRENT SEMANTIC OWNER
        >
CROSS-REFERENCE
        >
OLDER / SUPERSEDED WORDING
```

Do not use generic SMC knowledge to override the project's canonical semantic-owner documents.

## 8. Canonical document set

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
├── methodology_parameters.md
├── trading_policy.md
├── platform_execution.md
├── countertrend_scenarios.md
└── source_reconciliation.md
```
