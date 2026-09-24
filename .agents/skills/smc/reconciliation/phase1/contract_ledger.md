# Phase 1 Contract Ledger — C1–C5 Closure

Status: **DOCUMENTATION COMPLETE / CURRENT-REPOSITORY VALIDATION PENDING**

| Contract | Status | Canonical disposition | Implementation evidence |
|---|---|---|---|

|---|---|---|---|
| C1 — Candle Extreme Breach deterministic OHLC model | CLOSED | Four-level ontology: PHYSICAL_BREACH, WICK_ONLY_BREACH, BODY_BREACH, CLOSE_BREACH. Body breach does not prove intrabar crossing. | 01_micro_structure.md + SMC_mapper.py breach classifier + test_micro_breach.py |
| C2 — Protection + Equal Extreme Reference Transfer | CLOSED | EQH/EQL relationship is evaluated before independent high/low reference identity transfer. Protection remains CandleTrendState-owned. | 01_micro_structure.md + ActiveExtremeReference + test_reference_transfer.py |
| C3 — Candle Internal Sequence / Outside Bar | CLOSED | OLHC/OHLC is methodology semantics. Outside Bar does not infer LOW_FIRST/HIGH_FIRST from aggregate OHLC. | 01_micro_structure.md + 08_implementation.md + test_outside_bar.py |
| C4 — Reversal ownership / layer boundary | CLOSED | Layer 1 owns Outside Bar geometry; Layer 6 owns Outside-Bar Reversal semantics. Outside Bar is never an automatic reversal trigger. | 01_micro_structure.md + 06_execution.md + test_layer_boundaries.py |
| C5 — Methodology vs historical observability | CLOSED | Methodology semantics do not imply historical observability. Observability state is implementation-owned. | 08_implementation.md + SMC_mapper.py |

## Current-main validation note

The dedicated Phase 1 test filenames referenced below are historical implementation evidence; they are **not present in the current `main` tree**. The current repository contains `tests/test_smc_analyzer.py`, which includes observability and IDM-state checks, but that file alone does not establish independent C1–C5 validation. Therefore the contract statuses below remain documentation/implementation disposition records, not a claim that the current main tree has dedicated passing tests for every contract.

## Mandatory invariants

~~~text
BODY_BREACH != PROVEN_INTRABAR_CROSSING
EQH/EQL != PROTECTION_STATE
OUTSIDE_BAR != OUTSIDE_BAR_REVERSAL
METHODOLOGY_ASSUMED != OBSERVED
UNAVAILABLE != OBSERVED
UNAVAILABLE MUST NOT BE AUTO-PROMOTED TO OBSERVED
~~~

## Untouched source

main/knowledgebase/ remains read-only. No canonical source material was modified.

## Acceptance gate

The semantic contracts are now closed in documentation and implementation. Final acceptance remains conditional on execution of the complete test suite and independent validation.
