# Phase 1 Contract Ledger — Initial Reconciliation Run

| Contract | Current status | Source evidence | Decision |
|---|---|---|---|
| C1 — Candle Extreme Breach deterministic OHLC model | OPEN | No direct Phase 1 source definition found in inspected knowledgebase passages | Preserve existing canonical rule; no source-driven change |
| C2 — Candle Extreme Protection + Equal Extreme Reference Transfer | OPEN | No direct source definition found | Preserve existing canonical rule; no source-driven change |
| C3 — Outside Bar internal sequence / state transition | OPEN | No direct OHLC/OLHC sequence definition found | Preserve determinism requirement; never infer intrabar order from OHLC alone |
| C4 — Reversal formations ownership / layer boundary | OPEN | Source material discusses reversal patterns in structural/execution contexts but does not establish a deterministic Layer 1 contract | Keep anatomy in Layer 1 and execution eligibility in `06_execution.md`; no promotion |

## Gate rule

No contract is marked resolved merely because a source passage is absent or ambiguous.

All four remain explicitly **OPEN** pending direct evidence and/or human-approved canonical resolution.
