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
   - Conditional 38.2% retracement qualification through applicable immediate-HTF valid pullback
   - Canonical HTF-valid-pullback ↔ complete LTF structure mapping, including IDM takeout followed by qualified BOS
   - Dynamic W1-to-D1/H4 resolution using pullback size, extent, candle span/count, and volume/activity evidence
   - Mandatory distinct-timeframe mapping requirement and fail-closed unavailable-context contract
   - Confirmed Structural Swing / Protected Structural Extreme lifecycle
   - First-BOS bootstrap initialization, dedicated bootstrap-reversal lifecycle, and post-CHoCH first-BOS lifecycle boundary
   - Shared lifecycle invariants

4. `04_BOS_mechanics.md`
   - Dedicated BOS mechanics and lifecycle
   - Continuation and opposing-break classification boundaries
   - Consumes shared structural qualification; does not redefine it

5. `05_CHOCH_mechanics.md`
   - Dedicated CHoCH mechanics and lifecycle
   - CHoCH-facing Major IDM interaction outcomes
   - LTF-CHoCH context route after HTF POI/core-liquidity interaction
   - Consumes Layer 3 Major IDM semantics/lifecycle; does not redefine IDM formation or governance

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
   - First-BOS bootstrap/process-state representation, dedicated bootstrap-reversal event routing, `dynamic_retracement_extreme` lifecycle mapping, explicit pre-BOS observation boundaries, and mapping-origin `C0` invariants
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

## 5. Semantic ownership and precedence

This index deliberately does not restate methodology rules. Each canonical concept has one primary semantic owner; other documents may define consumer contracts but must not introduce competing definitions.

| Semantic area | Primary owner |
|---|---|
| Candle-level observations | `01_micro_structure.md` |
| Sequential / Minor Structure and Minor IDM formation | `02_minor_structure.md` |
| Major Structure, Major IDM governance, retracement qualification, mandatory MTF context, and structural lifecycle | `03_structural_semantic_authority.md` |
| BOS classification and mechanics | `04_BOS_mechanics.md` |
| CHoCH classification and mechanics | `05_CHOCH_mechanics.md` |
| POI, OF/OB/RB, execution liquidity, and entry authorization | `06_execution.md` |
| Structural stop anchors and downstream risk/target lifecycle | `07_risk.md` |
| Numeric/configurable methodology values | `methodology_parameters.md` |
| Deterministic implementation representation and validation | `08_implementation.md` |
| Configurable account/trading-plan rules | `trading_policy.md` |
| Venue order/fill/position/backtest contracts | `platform_execution.md` |
| Composition of the three source-defined countertrend scenarios | `countertrend_scenarios.md` |
| Source-to-canonical change control | `source_reconciliation.md` |

When documents conflict:

```text
CURRENT SEMANTIC OWNER
        >
CROSS-REFERENCE / CONSUMER CONTRACT
        >
OLDER OR SUPERSEDED WORDING
```

`knowledgebase/` is source evidence, not a replacement for the current canonical owner. Generic SMC knowledge must not override the project's source reconciliation and canonical semantic-owner documents.
