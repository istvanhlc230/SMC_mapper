# Full Specification — Consolidated Market-Data Architecture

> This document preserves the detailed specification material that was removed from `AGENT_REVIEW.md`.
> It is kept under `specifications/` so normative/detailed architecture content remains outside the agent communication log.
>
> The active implementation specifications remain:
> - `specifications/smc_mapper_specification.md`
> - `specifications/market_data_specification.md`
>
> This file is the consolidated historical/full specification record for the approved two-file market-data architecture.

---

# FULL SPECIFICATION AUDIT — CONSOLIDATED MARKET-DATA JSON PLAN

## Result

**FAIL — the current specification is not yet internally consistent with the latest approved two-file market-data architecture.**

## Findings

### 1. BLOCKER — stale CLI candle-data transport

`A16`, `A6`, `A15`, `B1`, `C2`, and `A19.1` still contain the previous model where normalized candle data is emitted on CLI stdout and consumed directly by the mapper. The latest approved model is file-based:

`market_data.py -> <SYMBOL>_marketdata.json -> smc_mapper.py`.

Therefore stdout must not be the candle-data transport between Market Data CLI and mapper.

### 2. BLOCKER — stale Market Data Layer/service wording

Several sections still describe a provider-independent in-process/range-query service even though the approved boundary is a standalone `market_data.py` CLI plus persistent market-data JSON.

### 3. BLOCKER — market-data retention is undefined

`<SYMBOL>_marketdata.json` is now persistent and multi-timeframe, but the specification does not define how long candle data is retained, when old candles may be deleted, or how missing older data is reacquired.

The clean separation should remain: retention is an operational market-data policy, not SMC logic. A bounded per-timeframe retention policy is recommended; data outside retention may be reacquired from the provider when needed for an explicit bootstrap/rebuild.

### 4. BLOCKER — multiple analyses + `history_no` is ambiguous

`<SYMBOL>_structures.json` now contains multiple analyses, but `history_no` remains one symbol-level value while the older text describes one symbol-level/one-history context. The specification must explicitly state whether that single value is applied independently to each analysis's own closed-range history.

Recommended simple interpretation: one stored symbol-level `history_no` configuration value, applied independently to each analysis's own applicable closed Dealing Range history.

### 5. BLOCKER — concurrent file update semantics are not specified

The agreed `wait until writable` behavior is not sufficient by itself to prevent lost updates if two processes both read the same JSON before either writes it.

To stay simple, the finished architecture should make the monitor the serial orchestrator for a symbol and define each JSON update as a single read-modify-write transaction with atomic replacement. If multiple independent writers are explicitly supported, a real OS file lock or equivalent transaction mechanism is required.

### 6. GAP — periodic one-candle update contract is not fully specified

The specification does not yet fully define the normal monitor cycle in file terms:

`existing last completed candle -> market_data update -> append/deduplicate new completed candles -> mapper reads persisted file -> analysis checkpoint advances`.

It also needs the no-new-candle no-op and missed-multiple-candle batch cases.

### 7. GAP — one market-data file containing all timeframes needs update semantics

`<SYMBOL>_marketdata.json` correctly groups all acquired timeframes, but the specification must define how a timeframe section is created, incrementally extended, deduplicated, ordered, and independently retained without affecting other timeframe sections.

### 8. CLEANUP — debug contract

The terminal-only debug rule is conceptually correct, but the current debug section still describes stdout as a process-to-process machine-data channel. Under the latest file-based design, candle data is persisted to JSON instead. Debug remains `stderr` -> terminal only; normal runtime should produce no user-visible CLI output.

## Canonical SMC audit

No canonical SMC semantic conflict was found in the reviewed specification architecture. The canonical skill remains authoritative, and the mapper specification still avoids redefining the core Layer 1-8 semantics. The key canonical boundaries remain consistent:

- Layer 3 owns retracement qualification and IDM governance.
- Layer 4 consumes stored qualification and does not recompute it.
- `VALID_BOS` remains gated by `IDM_TAKEN`, qualified retracement, and structural swing break.
- Layer 5 retains the LTF Structural Glitch route.
- Layer 6 owns canonical POI/Rule-of-Two semantics.
- Layer 7/8 retain downstream target and notification boundaries; BE/trailing remain trade-management concepts.

## Required repair order

1. Replace every stale stdout/CLI candle-transfer statement with the persistent `<SYMBOL>_marketdata.json` boundary.
2. Remove the obsolete in-process Market Data service wording.
3. Define simple market-data retention and reacquisition policy.
4. Resolve symbol-level `history_no` application across multiple analyses.
5. Define serialized/atomic JSON update semantics.
6. Define the one-candle, no-op, and missed-batch monitor update cycle.
7. Re-audit A-D after the repair.

**Current audit status: FAIL — architecture direction is sound, but the specification needs reconciliation before implementation.**

---

# FULL SPECIFICATION REPAIR — TWO-FILE MARKET-DATA ARCHITECTURE (COMPLETED)

## Final architecture

- One `<SYMBOL>_marketdata.json` stores normalized completed candles for all acquired timeframes of the symbol.
- One `<SYMBOL>_structures.json` stores all distinct mapper analyses for the symbol.
- Analysis identity is deterministic from timeframe configuration plus requested start boundary.
- Each analysis has its own `last_processed_candle_time` checkpoint.
- A single symbol-level `history_no` value is stored once and applies independently to each analysis's applicable closed Dealing Range history.
- Market-data retention is a bounded rolling operational policy per timeframe; it is not an SMC semantic rule.
- When required history is outside the retained market-data window, the Market Data CLI reacquires it.

## Runtime update contract

- Initial/bootstrap execution acquires required historical completed candles into the market-data JSON, then the mapper reads them.
- Normal monitor execution updates only newly completed candles.
- One new completed candle is a normal update case.
- Missed cycles are recovered as one chronological completed-candle range.
- No new completed candle is a no-op.
- Market-data and structure JSON updates are complete read-modify-write operations with temporary-file + atomic replacement.
- If a file is temporarily unavailable for writing, the writer waits and retries up to a finite timeout.
- One active monitor orchestration instance per symbol avoids multi-writer coordination complexity; multiple analyses run within that monitor.

## CLI/debug contract

- Candle data is persisted to `<SYMBOL>_marketdata.json`; it is not transferred to the mapper through stdout.
- Debug output is `stderr` only.
- Debug `stderr` is terminal-only and must not be captured, parsed, forwarded, merged, persisted, or passed to mapper/monitor.
- Normal runtime is user-silent.

## Full audit result

Re-audited the repaired `smc_mapper_specification.md` against the canonical `.agents/skills/smc/` Layer 1-8 files and the internal A-D specification structure.

Verified no remaining:
- Market Data Layer/in-process service contract;
- candle `stdout` pipe to mapper;
- direct provider dependency in mapper;
- single-analysis-only structures file model;
- unspecified one-candle / missed-batch update path;
- missing analysis identity/checkpoint separation;
- missing file write safety contract.

Verified canonical ownership remains intact and no `.agents/skills/smc/` file was modified.

Final specification commit:
`2ae61dcbbff50f32d55a2b2e514634e9e7d30d1e`

**FINAL STATUS: PASS — SPECIFICATION RECONCILED WITH THE APPROVED TWO-FILE, PERSISTENT-MARKET-DATA RUNTIME MODEL**

---

# FULL SPECIFICATION AUDIT + CURRENT-SNAPSHOT / PARALLEL-VOLUME REPAIR — COMPLETED

## Repaired model

- `<SYMBOL>_marketdata.json` stores all acquired timeframes for the symbol.
- Each timeframe has completed candles plus an optional current in-progress snapshot.
- current is never canonical structural input and never advances mapper checkpoints.
- `market_data.py` supports 1..N requested timeframes through `--timeframes TF [TF ...]`.
- `--live` refreshes current snapshots without forcing structural processing when no completed candle changed.
- Provider total volume, OHLC-derived directional estimates, and genuine orderflow can coexist as separate volume branches.
- No single candle-level volume method is used as provenance.
- POI volume analytics can preserve OHLC and ORDERFLOW branches simultaneously.
- Volume values have deterministic numeric validation.

## Full audit result

Re-audited the repaired `smc_mapper_specification.md` against the canonical `.agents/skills/smc/` Layer 1-8 files and the internal A-D specification structure.

PASS — file-based market-data boundary; no in-process Market Data Layer or candle stdout transport.

PASS — completed versus in-progress candle separation is explicit.

PASS — multi-timeframe market-data acquisition is distinct from mapper one/two-timeframe semantics.

PASS — current snapshot refresh is explicitly separate from completed-candle structural processing.

PASS — raw total volume, OHLC estimate, and orderflow are parallel data, not mutually exclusive alternatives.

PASS — runtime analytical-method selection is separate from persisted data availability/provenance.

PASS — POI volume analytics supports parallel OHLC and ORDERFLOW branches.

PASS — canonical Layer 1-8 ownership remains intact; no skill file was modified.

PASS — IDM governance, retracement qualification, VALID_BOS gates, LTF Structural Glitch, Rule-of-Two, and downstream target/risk boundaries remain unchanged.

PASS — no stale candle-level `volume_method` contract remains.

**FINAL STATUS: PASS — SPECIFICATION RECONCILED WITH CURRENT-SNAPSHOT MARKET DATA, MULTI-TIMEFRAME CLI, AND PARALLEL VOLUME DATA MODEL**
