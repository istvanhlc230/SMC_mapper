# SMC_Mapper Full Specification — Consolidated Current Architecture

**Status:** Current consolidated architecture reference.
**Purpose:** One clean cross-file reference for the approved market-data, structures, monitor, and news runtime model, including datasource, canonical UTC, local-time, trading-session, and news-warning handling.

**Normative ownership:**
- `specifications/market_data_specification.md` owns the detailed Market Data implementation contract.
- `specifications/smc_mapper_specification.md` owns the detailed Mapper implementation contract.
- `specifications/smc_monitor_specification.md` owns the detailed Monitor implementation contract.
- `.agents/skills/smc/` remains the sole authority for canonical SMC semantics.

This document consolidates the approved architecture and final audit outcomes. It does not override a more specific owner document.

The former historical FAIL findings that were embedded here have been removed from the active specification body. They are preserved only by repository history, not presented as current requirements.

---

# Final Approved Architecture

## Trading sessions and news

Named regional trading sessions are Monitor runtime context. V1 knows Sydney, Tokyo, London, and New York using explicit IANA timezones; exact local session hours are one Monitor-owned operational configuration.

Economic-news acquisition is separated from price Market Data and is owned by `news_data.py` / `specifications/news_data_specification.md`. The Monitor consumes normalized UTC news events from shared `<DATA_ROOT>/news_data.json` and emits warning-only runtime notifications.

News warnings do not alter canonical SMC state, POI lifecycle, target coordinates, RR calculation, mapper checkpoints, or order/position behavior.

## Symbol output-directory contract

The common data root contains one dedicated directory per normalized symbol:

```text
<DATA_ROOT>/<SYMBOL>/
    <SYMBOL>_marketdata.json
    <SYMBOL>_structures.json
    news_data.json
```

Market Data, Mapper, Monitor, and News Data automatically resolve their symbol directory from the requested symbol. No cross-symbol flat output store is used. The existing common data root is retained; this change only introduces the symbol directory boundary beneath it.

## Time-domain contract

The system distinguishes three time domains:

1. datasource time — provider-native source representation handled only at the Market Data boundary;
2. canonical UTC — the authoritative domain for normalized timestamps, completion, ordering, persistence, Mapper structural processing, checkpoints, scheduling decisions, target identity, and alert evaluation;
3. local time — a DST-aware runtime/presentation view derived from canonical UTC.

Datasource timezone must never be guessed. Naive datasource wall-clock timestamps without a known timezone are rejected. Canonical JSON remains UTC-based. Local-time values are not added to canonical JSON solely for display.



## Final architecture

- Every symbol has one dedicated output directory: `<DATA_ROOT>/<SYMBOL>/`.
- `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json` stores normalized completed candles for all acquired timeframes of the symbol.
- `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_structures.json` stores all distinct mapper analyses for the symbol.
- `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_news_data.json` stores normalized external news events for that symbol.
- Each active product program automatically resolves the selected symbol directory and discovers its owned input/output files there.
- `smc_monitor.py` owns runtime scheduling, process orchestration, current-price observation, downstream target/RR evaluation, and alerting; its runtime state is transient.
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

- Candle data is persisted to `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json`; it is not transferred to the mapper through stdout.
- Market-data and structure outputs are grouped under each symbol's directory; the external news event cache is intentionally shared at `<DATA_ROOT>/news_data.json`.
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

Final architecture revision: symbol-directory / symbol-news-store model.

**FINAL STATUS: PASS — SPECIFICATION RECONCILED WITH THE SYMBOL-DIRECTORY, THREE-PERSISTENT-STORE RUNTIME MODEL**

---


---

# SHARED NEWS CACHE V1

The external news store is intentionally global rather than symbol-scoped. FMP's Economic Calendar endpoint accepts date ranges and has a maximum 90-day request interval; it does not require one request per trading symbol. citeturn743230search0

The V1 cache maintains approximately 7 days forward coverage, refreshes at most once per 24 hours by default, and supports `--force` for an immediate refresh. This keeps identical calendar acquisition shared across all monitored symbols. FMP's Basic free tier currently documents 250 API requests/day. citeturn743230search7
