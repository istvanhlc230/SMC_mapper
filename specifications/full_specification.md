# SMC_Mapper Full Specification — Architecture Index

**Status:** Current cross-file architecture index.
**Purpose:** One navigation and boundary reference for the V1 product. Detailed implementation rules live in the owning specification; canonical SMC semantics live only in `.agents/skills/smc/`.

## 1. Normative ownership

| Concern | Owner |
|---|---|
| Canonical SMC semantics | `.agents/skills/smc/` |
| Market Data acquisition, normalization, completion, retention, current snapshot, persistence | `specifications/market_data_specification.md` |
| Mapper orchestration, canonical-state consumption, analysis identity/checkpoint, structural persistence | `specifications/smc_mapper_specification.md` |
| Monitor scheduling, process orchestration, current-price observation, downstream target/RR evaluation, sessions, alerts | `specifications/smc_monitor_specification.md` |
| Historical audit narrative | `AGENT_REVIEW.md` only |

This document does not duplicate or override the owner specifications.

## 2. Persistent data boundary

```text
<DATA_ROOT>/<SYMBOL>/
    <SYMBOL>_marketdata.json
    <SYMBOL>_structures.json
```

- Market Data is the sole writer of `*_marketdata.json`.
- Mapper is the sole writer of `*_structures.json`.
- Monitor owns no persistent JSON schema.
- The two JSON files are the machine-readable process boundary.
- stdout/stderr are never used as candle or structure data transport.

## 3. Time contract

Three domains are distinguished:
1. provider/source time at the Market Data boundary;
2. canonical UTC for persisted timestamps, ordering, completion, checkpoints and structural processing;
3. local time as a DST-aware presentation/input-conversion view.

Naive or ambiguous source timestamps are rejected. Local time must never alter canonical ordering, analysis identity, checkpointing or SMC calculations.

## 4. Analysis model

- Mapper analyses are symbol-scoped and independently identifiable.
- Identity is deterministic from timeframe configuration plus the normalized requested start boundary.
- When no explicit start is supplied, the Mapper uses the deterministic existing-analysis resume path or, for a new analysis, the earliest available completed entry-timeframe candle as its initial persisted boundary.
- `requested_start`, persisted analysis boundary, and computed `effective_start` remain distinct concepts.
- Each analysis owns its own `last_processed_candle_time`.
- Market Data retention is operational storage policy, not canonical SMC semantics.

## 5. Runtime update flow

```text
CLI
 ↓
Monitor validates request and discovers stored analyses
 ↓
Market Data acquires/normalizes required completed candles
 ↓
Market Data persists market-data JSON atomically
 ↓
Mapper consumes completed candles only
 ↓
Mapper persists canonical structures and advances its checkpoint atomically
 ↓
Monitor reloads persisted state
 ↓
Monitor refreshes current market reference when required
 ↓
Monitor resolves downstream target
 ↓
Target clearance
 ↓
Optional --rr policy
 ↓
Alert eligibility
 ↓
Notification only
```

A current-snapshot-only refresh does not require Mapper execution. A completed-candle update requires successful Mapper persistence before downstream evaluation of the new structural state.

## 6. Current-state separation

- Market Data `current` is an in-progress market-data snapshot.
- `current` never enters canonical Mapper processing.
- Mapper structures JSON contains canonical structural state and mapper provenance/checkpoint metadata, not Monitor current price, trade state, stop/BE state, target-hit state or alert history.
- Monitor runtime state is transient.

## 7. Cross-file invariants

- One symbol directory per normalized symbol.
- One active Monitor orchestration instance per symbol.
- Multiple analyses may coexist for one symbol.
- Symbol and analysis state remain isolated.
- Missing/unresolved required data fails closed.
- No component may fabricate candles, canonical structure, targets or execution success.
- Monitor is notification-only: no order submission, automatic buy/sell or position management.
- Canonical SMC semantics are consumed from the skill; downstream policy must not redefine them.
- Volume analytics are non-canonical enrichment and must not alter POI validity, lifecycle or type.
- Probability and News are not part of the current product specification.

## 8. Downstream target/RR contract

Target semantics are owned by the canonical downstream Layer-7 contract and consumed by Monitor.

V1 Monitor resolves **one target per active setup**. Multi-target/multi-leg allocation is outside current product scope.

Monitor target clearance, optional `--rr`, and alert eligibility are downstream runtime policy. They must not mutate canonical Mapper state.

## 9. Versioning / audit rule

Owner specifications are the normative implementation contracts. This index must remain concise and structural; detailed rules belong in exactly one owner document. Historical audit findings belong in `AGENT_REVIEW.md` and must not be treated as current requirements.

**Current architecture state:** Cross-file ownership is intentionally defragmented; unresolved implementation-policy decisions remain only in their owning specification.
