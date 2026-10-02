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

Trading-session awareness is a Monitor runtime concern. Named regional sessions use explicit IANA timezones and local session definitions so daylight-saving changes are handled correctly.

V1 session identities include Sydney, Tokyo, London, and New York. Exact local session hours are Monitor-owned operational policy and are not duplicated elsewhere.

Economic-news acquisition is a separate external-data concern owned by `news_data.py`. The Monitor consumes normalized UTC news events and emits transient warning notifications. News warnings do not alter canonical SMC state, target/RR semantics, or order/position behavior.

## Trading sessions and news

Named regional trading sessions are Monitor runtime context. V1 knows Sydney, Tokyo, London, and New York using explicit IANA timezones; exact local session hours are one Monitor-owned operational configuration.

Economic-news acquisition is separated from price Market Data and is owned by `news_data.py` / `specifications/news_data_specification.md`. The Monitor consumes normalized UTC news events from `news_events.json` and emits warning-only runtime notifications.

News warnings do not alter canonical SMC state, POI lifecycle, target coordinates, RR calculation, mapper checkpoints, or order/position behavior.

## Time-domain contract

The system distinguishes three time domains:

1. datasource time — provider-native source representation handled only at the Market Data boundary;
2. canonical UTC — the authoritative domain for normalized timestamps, completion, ordering, persistence, Mapper structural processing, checkpoints, scheduling decisions, target identity, and alert evaluation;
3. local time — a DST-aware runtime/presentation view derived from canonical UTC.

Datasource timezone must never be guessed. Naive datasource wall-clock timestamps without a known timezone are rejected. Canonical JSON remains UTC-based. Local-time values are not added to canonical JSON solely for display.



## Final architecture

- One `<SYMBOL>_marketdata.json` stores normalized completed candles for all acquired timeframes of the symbol.
- One `<SYMBOL>_structures.json` stores all distinct mapper analyses for the symbol.
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
