# Phase 1 Change Set — C1–C5 Implementation

Status: **IMPLEMENTED / VALIDATION PENDING**

## Implemented changes

### C1
Added deterministic Physical/Wick-Only/Body/Close breach taxonomy with the no-crossing invariant.

### C2
Separated EQH/EQL geometric confirmation from independent active-high/active-low reference identity transfer. Reference identity preserves price, candle ID, and role.

### C3
Canonical Layer 1 now records only the OLHC/OHLC methodology model. Implementation owns sequence observability.

### C4
Outside Bar is a Layer 1 geometric relationship. Outside-Bar Reversal remains Layer 6-owned and is not auto-derived.

### C5
Added the explicit methodology-versus-observability boundary and implementation-only INTRABAR_SEQUENCE_EVIDENCE states.

## Files changed

- .agents/skills/smc/01_micro_structure.md
- .agents/skills/smc/08_implementation.md
- .agents/skills/smc/02_minor_structure.md
- .agents/skills/smc/06_execution.md
- SMC_mapper.py
- test_micro_breach.py
- test_reference_transfer.py
- test_outside_bar.py
- test_layer_boundaries.py

## Source protection

main/knowledgebase/ was not modified.

## Deferred

No structural redesign, retracement-threshold reconciliation, or new reversal-pattern predicate was introduced.
