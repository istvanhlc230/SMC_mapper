# SMC Mapper Specification

**Status:** Working specification. Sections are approved incrementally.  
**Scope:** Functional and implementation specification for the future `smc_mapper.py`.  
**Canonical authority:** `.agents/skills/smc/` remains the sole authority for canonical SMC semantics. This document does not redefine those rules.

---

# A. INPUT / ORCHESTRATION

## A0. Active product runtime components

The intended finished product uses these active Python runtime components:

- `market_data.py` — standalone Market Data CLI: provider access, normalization, completion handling, deterministic range retrieval, incremental update, bounded retention, completed-candle persistence, current-candle snapshot refresh, and persistence to `<SYMBOL>_marketdata.json`.
- `smc_mapper.py` — canonical SMC mapper: structural analysis, HTF/LTF processing, and persistent structural state in `<SYMBOL>_structures.json`.
- `smc_monitor.py` — interactive runtime: scheduling, user interaction, runtime/target monitoring, alerts, and orchestration of Market Data CLI and mapper execution.

The older `smc_htf_ltf_monitor.py`, `smc_analyzer.py`, and Layer-1-to-Layer-6 `*_engine.py` test/implementation artifacts are not components of the finished product architecture.

This specification defines the mapper contract and its boundaries with the standalone Market Data CLI and interactive monitor.

## A1. Symbol

One required instrument per mapper execution.

One mapper execution analyzes one symbol.

---

## A2. HTF

Optional.

Exactly one timeframe may be supplied.

Example:

`--htf H4`

---

## A3. LTF

Optional.

Exactly one timeframe may be supplied.

Example:

`--ltf M15`

---

## A4. Timeframe relationship

The mapper determines the analysis mode from the supplied timeframe parameters.

### Single-timeframe analysis

Use single-timeframe analysis when:

- only `--htf` is supplied;
- only `--ltf` is supplied; or
- both are supplied but they specify the **same timeframe**.

In single-timeframe analysis, the selected timeframe is analyzed once.

Internally, the analysis may represent:

`HTF = LTF = selected timeframe`

but this does **not** activate HTF pullback validation.

### Two-timeframe analysis

Use two-timeframe analysis only when both are supplied and they are different:

`HTF > LTF`

An invalid relationship is an input error.

The mapper must never silently swap or otherwise correct the supplied timeframes.

---

## A5. HTF Pullback Validation

HTF pullback validation is enabled only in **two-timeframe analysis**, when both HTF and LTF are explicitly supplied and they are different.

### Both supplied and different

`--htf H4 --ltf M15`

- Analyze H4 first.
- Analyze M15 second.
- M15 may consume the required H4 structural context for canonical HTF pullback validation.

### Only HTF supplied

`--htf H4`

- Analyze only H4.
- Do not perform HTF pullback validation.

### Only LTF supplied

`--ltf M15`

- Analyze only M15.
- Do not perform HTF pullback validation.

### Both supplied and equal

`--htf H1 --ltf H1`

- Treat the request as a single-timeframe H1 analysis.
- Analyze H1 once.
- Do not perform HTF pullback validation.
- Do not treat H1 as its own Higher Timeframe for canonical Gate 2.

The mapper must never automatically select or invent a different HTF when only one timeframe is supplied.

---


## A6. Analysis order and timeframe synchronization

When both timeframes are supplied, the mapper reads the required normalized HTF/LTF candle ranges from the corresponding timeframe sections of `<SYMBOL>_marketdata.json` and processes them chronologically on their shared time axis.

"HTF context establishment -> synchronized HTF/LTF processing"

The HTF analysis provides the structural context required by canonical LTF rules. The LTF analysis may consume that context where required, but the LTF analysis must never redefine or mutate HTF structure.

Within synchronized processing:

- a newly completed HTF candle updates HTF canonical state before later LTF evaluations may consume that new HTF information;
- each completed LTF candle is evaluated against only the HTF canonical context that already exists at that LTF evaluation time;
- the mapper does not use a later HTF event to reinterpret an earlier LTF event.

The monitor/launcher ensures that required candle ranges are present in `<SYMBOL>_marketdata.json` by invoking the Market Data CLI as needed.

When only one timeframe is supplied, only that timeframe is analyzed.

## A7. Start time

`--starttime` defines the requested start of the analysis window.

It may be specified as:

- a date, or
- an exact datetime.

Examples:

`--starttime 2026-09-01`

`--starttime 2026-09-01T09:30:00`

The mapper does not access a concrete provider to obtain earlier candles. Any candles required for structural bootstrap/warm-up are obtained by ensuring the required range is present in `<SYMBOL>_marketdata.json` through the Market Data CLI, then reading the persisted normalized range.

The mapper must distinguish:

- `requested_start`
- `effective_start`

If the requested start precedes the available completed data, the mapper uses the earliest available completed candle that is valid for the requested analysis/bootstrap and reports that the effective start is later than requested.

If required historical data is outside the retained market-data window, the Market Data CLI reacquires the missing range before mapper processing.

Missing historical data must never be fabricated.

## A8. End time

`--endtime` is optional.

It may be specified as:

- a date, or
- an exact datetime.

Examples:

`--endtime 2026-09-29`

`--endtime 2026-09-29T15:30:00`

If omitted, use the latest completed driving-timeframe candle available in `<SYMBOL>_marketdata.json` after the required update.

If supplied, use the latest completed candle in `<SYMBOL>_marketdata.json` whose canonical completion boundary is less than or equal to the requested end time.

The normalized candle `timestamp` alone must not be treated as proof that a candle has completed. Completion is determined by the normalized completion status/time contract in B6.

An incomplete/current candle must never enter canonical analysis.

## A9. Independent timeframe feed ranges

HTF and LTF candle data may cover different temporal ranges.

The Market Data CLI owns acquisition and persists the actual available range for each timeframe in `<SYMBOL>_marketdata.json`. The mapper reads only the range required by its current analysis and must not fabricate unavailable candles.

Example:

- HTF data: 2026-06-01 -> 2026-09-29
- LTF data: 2026-01-01 -> 2026-09-29

The longer LTF history must not be truncated merely because the HTF history is shorter.

The absence of HTF data before its available start does not imply that HTF structure did not exist.

Availability metadata may be read from `<SYMBOL>_marketdata.json` or obtained through the Market Data CLI availability operation. If the required range cannot be satisfied, the mapper must represent the resulting data/context unavailability explicitly and fail closed where canonical rules require unavailable context.

The mapper does not perform provider-specific acquisition.

## A10. Missing HTF context

When an LTF canonical rule requires HTF pullback validation but the required HTF historical context is unavailable, represent the condition explicitly as:

`HTF_CONTEXT_UNAVAILABLE`

Do not convert it to:

`HTF_VALID_PULLBACK = FALSE`

Therefore:

`HTF_CONTEXT_UNAVAILABLE != HTF_VALID_PULLBACK_FALSE`

If a canonical decision depends on unavailable HTF context, the decision must remain unresolved / fail closed.

---


## A11. Closed Dealing Range history and `history_no`

`history_no` is one collective symbol-level configuration value, stored once in `<SYMBOL>_structures.json`.

In two-timeframe mode, it applies independently to the HTF CLOSED DEALING RANGE history retained inside each distinct mapper analysis entry. The LTF does not have a separate `history_no`.

In single-timeframe analysis, it applies to the selected timeframe's CLOSED DEALING RANGE history for that analysis.

The history unit is the canonical closed Dealing Range. Only a Dealing Range that has been canonically closed may enter history. The currently open Dealing Range is never a history item.

Retention is newest-first by canonical `close_time`, with oldest-first (FIFO) eviction within each analysis when that analysis's retained history exceeds `history_no`.

Eviction is a storage-retention operation only. It does not invalidate canonical historical structure.

A repeated mapper execution must reconcile an existing range identity in place and must not create a duplicate history entry.

## A12. Closed Dealing Range identity and retention configuration

A stored CLOSED DEALING RANGE is identified by:

```
timeframe + start_time + close_time
```

This is the history identity. `structure_hash` is not a closed-range identity.

`start_time` and `close_time` are lifecycle timestamps derived from the canonical Dealing Range lifecycle. The mapper must not invent a new range-start rule, provisional range boundary, or synthetic start timestamp.

`formation_time`, where present on structural objects or state within the range, identifies when that structural object/state formed. It is semantically distinct from the Dealing Range `close_time`.

A closed range identity is immutable once canonically closed. For an existing retained range with the same identity, reconciliation updates that range in place. A newly closed range with a new identity is inserted.

### `history_no` persistence rules

`history_no` is stored once per symbol structures JSON, not per timeframe or analysis.

- New symbol structures JSON + no `--history_no` -> initialize and persist `history_no = 5000`.
- New symbol structures JSON + `--history_no=N` -> initialize and persist `history_no = N`.
- Existing symbol structures JSON + no `--history_no` -> preserve the stored `history_no`.
- Existing symbol structures JSON + `--history_no=N` -> ignore the CLI value and preserve the stored `history_no`.
- If an existing symbol structures JSON lacks `history_no`, initialize and persist `5000`.
- `N` must be an integer >= 1 when supplied.

Changing `history_no` changes retention capacity only. It does not change canonical SMC semantics.

## A12a. HTF Dealing Range history contract

Within each retained mapper analysis entry, each history element represents one CLOSED Dealing Range for that analysis and may contain canonical HTF structural state and, where two-timeframe analysis is active, any number of LTF structures interpreted in that HTF range context.

The LTF records stored under an HTF range are context-scoped execution analysis, not a new canonical parent/child ontology. LTF semantic ownership remains with the LTF canonical rules.

The history record may contain, where applicable:

- HTF structural direction/lifecycle state;
- HTF structural swings;
- HTF protected structural extremes;
- HTF IDM provenance;
- HTF retracement qualification;
- HTF BOS;
- HTF CHoCH;
- canonical HTF Layer-6 POIs;
- associated LTF structural/entry-analysis records;
- volume metadata associated with canonical structural points/POIs.

There is no fixed maximum number of LTF structures within one HTF Dealing Range.

The history record must preserve canonical formation/provenance times of its contained objects.

History is not an append-only mapper execution log. It is retained canonical Dealing Range history for the specific mapper analysis.

### A12b. Dealing Range lifecycle boundary

The mapper derives Dealing Range history boundaries strictly from the canonical structural lifecycle.

- A currently open Dealing Range is runtime state, not history.
- `VALID_BOS` is the canonical lifecycle event that establishes the next confirmed Dealing Range lifecycle; when a governing range already exists, it closes that previous range first. The first `VALID_BOS` establishes the first confirmed Dealing Range and therefore has no pre-existing governing range to close.
- The mapper must not close or start a Dealing Range because of a physical break, IDM sweep, CHoCH-eligible break, insufficient-retracement `IMPULSE_EXTENSION`, mapper execution boundary, or retention operation.
- Before the first canonical `VALID_BOS`, no governing Dealing Range may be fabricated for history or used as a substitute for the unresolved first-BOS canonical baseline.
- The exact first-BOS retracement baseline remains the canonical/source gap documented by the SMC skill; the mapper must fail closed rather than invent a synthetic initialization rule.

---

## A13. JSON storage

Use two symbol-scoped JSON files per symbol:

```text
data/
    CCCC_marketdata.json
    BABA_marketdata.json
    DTE.DE_marketdata.json

structures/
    CCCC_structures.json
    BABA_structures.json
    DTE.DE_structures.json
```

### Market-data JSON

<SYMBOL>_marketdata.json is the persistent normalized market-data store for that symbol.

It contains all acquired timeframes for the symbol in one file. Each timeframe section contains a completed-candle series plus an optional current in-progress candle snapshot. A separate market-data file is not created per timeframe.

Logical shape:

    {
      "symbol": "CCCC",
      "timeframes": {
        "H4": { "available_start": "...", "available_end": "...", "candles": [], "current": null },
        "M15": { "available_start": "...", "available_end": "...", "candles": [], "current": null },
        "M5": { "available_start": "...", "available_end": "...", "candles": [], "current": null }
      }
    }

Only normalized market-data state belongs here. No canonical structure, mapper history, POIs, trade state, monitor state, or debug text may be stored.

Completed candles are stored in candles[]. They are the only market-data records eligible for canonical mapper processing. The optional current field stores only the latest in-progress candle snapshot for that timeframe and is never canonical structural input.

A current snapshot may be refreshed while the candle is forming. It may contain the provider-available OHLC and total volume for that in-progress interval. It must never be copied into candles[] until the interval is confirmed completed.

Market-data retention is a bounded rolling operational policy applied independently to each timeframe. Its capacity is a market-data implementation/storage setting, not a canonical SMC parameter.

If an analysis requires candles outside the retained window, the Market Data CLI reacquires that missing range and merges it into the corresponding timeframe before mapper processing.

Each timeframe section is independently created, extended, deduplicated by canonical candle identity, chronologically ordered, and retention-managed. Updating one timeframe must not alter another timeframe's completed candle series or current snapshot.

The available_start and available_end fields refer only to the persisted completed-candle series, not to the current snapshot.

### Structures JSON

`<SYMBOL>_structures.json` is the canonical mapper structural-state file for that symbol.

It contains all distinct mapper analyses for the symbol in one file. Each analysis is identified by a deterministic analysis key derived from its timeframe configuration and requested start boundary.

Examples:

```text
H4_M15_2026-06-10T12:00:00Z
H1_M5_2026-07-01T09:00:00Z
M15_2026-06-10T12:00:00Z
```

The analysis key is an implementation-level identifier only; it does not redefine canonical SMC ontology.

Logical shape:

```json
{
  "symbol": "CCCC",
  "history_no": 5000,
  "analyses": {
    "H4_M15_2026-06-10T12:00:00Z": {
      "htf": "H4",
      "ltf": "M15",
      "analysis_mode": "HTF_LTF",
      "requested_start": "2026-06-10T12:00:00Z",
      "last_processed_candle_time": "...",
      "current": {},
      "history": []
    }
  }
}
```

`history_no` is stored once at symbol level and applies independently to each analysis's applicable closed Dealing Range history.

A Market Data CLI execution updates only `<SYMBOL>_marketdata.json`. A mapper execution updates only its relevant analysis entry inside `<SYMBOL>_structures.json`.

The monitor identifies each stored analysis from its deterministic analysis key and validates the stored `analysis_mode`, `htf`, `ltf`, and `requested_start`.

There is no single multi-symbol mapper JSON file and no single multi-symbol market-data JSON file.

## A14. Stored state

Each mapper analysis entry stores canonical structural analysis plus the minimal mapper-processing metadata required for deterministic incremental execution.

It may contain structural lifecycle/state, structural swings, protected structural extremes, dealing range, IDM state/provenance, retracement qualification, BOS, CHoCH, canonical L6 structural / POI results, retained closed Dealing Range history, and structural provenance/change metadata.

The mapper must not persist dynamic monitoring or trade state such as current market price, active trade/order state, stop state, break-even state, trailing state, or target-hit state. Those are owned by the monitor.

Each analysis entry contains its own `last_processed_candle_time` as mapper processing provenance/checkpoint metadata. It carries no canonical SMC meaning.

## A15. Input validation

Before canonical analysis, the mapper validates the supplied configuration and normalized candle contract, including at minimum:

- symbol;
- timeframe values;
- HTF/LTF relationship;
- start/end values;
- starttime < endtime when both are specified;
- history_no;
- timestamp ordering;
- duplicate timestamps;
- timezone validity;
- completed-candle status;
- OHLC integrity;
- two-timeframe HTF/LTF mode requirements.

Provider-specific availability checks, provider/API failures, and acquisition errors belong to the Market Data CLI process. The mapper sees only the normalized CLI result or an explicit acquisition/error result.

Invalid mapper configuration or normalized candle data must fail explicitly.

## A16. Market-data boundary and ownership

The mapper has no direct connection to any concrete market-data provider and has no runtime import dependency on `market_data.py`.

`market_data.py` is a standalone Market Data CLI process. It owns provider access, provider abstraction, normalization, completion handling, timestamp normalization, availability detection, deterministic range retrieval, incremental updates, retention and persistence to `<SYMBOL>_marketdata.json`.

The durable market-data boundary is `<SYMBOL>_marketdata.json`.

The normal data flow is:

```text
Provider(s)
    |
    v
market_data.py (CLI)
    |
    v
<SYMBOL>_marketdata.json
    |
    v
smc_mapper.py
    |
    v
<SYMBOL>_structures.json
    |
    v
smc_monitor.py
```

The normalized candle contract is the portability boundary. The mapper must not know whether the Market Data CLI obtained data from Yahoo, MT4/MT5, Pine/replay, a broker adapter, or another provider.

The Market Data CLI may internally use a bounded cache/buffer, but that is only an optimization. The persisted market-data JSON is the mapper's normalized data source.

The mapper must never call a concrete provider, perform provider-specific API requests, depend on provider-specific response formats, request market data from the monitor, or import `market_data.py` for runtime data access.

Future provider adapters may include Yahoo Charts, MetaTrader / MT4 / MT5, Pine Script data integration, broker feeds, and historical/replay sources.

Provider-specific API details remain outside the canonical SMC engine.

## A17. Bootstrap

The mapper constructs structural state by processing normalized candle ranges read from `<SYMBOL>_marketdata.json`.

For an initial build, or whenever a complete bootstrap is explicitly required:

earliest required effective candle -> latest completed driving-timeframe candle

The mapper must not use a latest-window shortcut that bypasses required structural bootstrap.

The launcher invokes the Market Data CLI for the required bootstrap range in deterministic batch form and updates `<SYMBOL>_marketdata.json`. The mapper then reads the required bootstrap range from that file.

For incremental execution after a valid persisted checkpoint, the launcher invokes the Market Data CLI for only the subsequently completed driving-timeframe range after the checkpoint, in chronological order, updates `<SYMBOL>_marketdata.json`, and then invokes the mapper against the resulting persisted range as defined by A18.

The mapper does not obtain market data from the monitor and does not access a concrete provider.

### A17.1 Two-timeframe LTF bootstrap

In two-timeframe analysis, the mapper establishes an LTF bootstrap coverage reference from the applicable HTF canonical structural context.

When a confirmed HTF Dealing Range exists, the applicable HTF Protected Structural Extreme is the preferred LTF bootstrap coverage reference. This reference determines the minimum historical LTF coverage needed for deterministic structural buildup. It is a data-coverage/reference point only; it is not an LTF structural start and does not create or promote any LTF structure.

When LTF bootstrap is required, the launcher invokes the Market Data CLI once for one deterministic LTF range covering the anchor through the activation/current boundary, subject to any additional LTF warm-up required by the canonical LTF rules, updates `<SYMBOL>_marketdata.json`, and then invokes the mapper against the persisted range.

If the requested LTF coverage begins later than the anchor because the source has no completed LTF data at or after the requested anchor, the mapper uses the first actually available completed LTF candle after the reference as the effective LTF bootstrap start. No attempt is made by the mapper to access the provider directly.

If the supplied LTF data begins before the HTF reference, that earlier data may be retained and used as additional canonical LTF warm-up when required; the HTF Protected Structural Extreme remains the context/coverage reference.

If the applicable confirmed HTF Protected Structural Extreme does not exist, the mapper does not fabricate one. The LTF bootstrap then follows the supplied LTF history subject to the canonical genesis/source-gap boundaries.

The LTF bootstrap reference is not an LTF structural-start ontology. The first LTF structural object is determined only by the canonical LTF rules.

## A18. Monitor boundary and mapper checkpoint

The monitor owns interactive runtime control, scheduling, current-price/runtime monitoring, target monitoring, alerts/notifications, and orchestration of Market Data CLI and mapper execution.

The mapper and Market Data CLI are separate processes. `market_data.py` persists normalized candles to `<SYMBOL>_marketdata.json`; the mapper reads the required ranges from that file.

The monitor orchestrates each symbol update cycle in this order:

1. Determine which configured analysis entries need new completed driving-timeframe data.
2. Invoke the Market Data CLI to update the required timeframe sections in `<SYMBOL>_marketdata.json`.
3. Invoke each affected mapper analysis.
4. The mapper reads the persisted ranges, processes new candles chronologically, and updates only its analysis entry.
5. The completed mapper result is persisted in `<SYMBOL>_structures.json`.

A normal monitor cycle may add exactly one newly completed candle to a timeframe. This is the normal incremental case.

If the monitor was not running for multiple completed candles, the Market Data CLI adds the entire missing completed range in one update and the mapper processes those candles chronologically.

The Market Data CLI may also refresh the current in-progress snapshot when live mode is requested, even when no new completed candle exists. A current-snapshot-only refresh must not trigger canonical structural processing or advance any mapper checkpoint.

If neither a new completed candle nor a changed or newly available requested current snapshot exists, that Market Data update is a no-op.

Each analysis entry has its own `last_processed_candle_time`. It identifies the latest completed driving-timeframe candle incorporated by that analysis.

Multiple analyses for the same symbol may overlap in time and share the same `<SYMBOL>_marketdata.json`. Their structural state and checkpoints remain separate inside `<SYMBOL>_structures.json`.

To keep file coordination simple, the finished product supports one active `smc_monitor.py` orchestration instance per symbol. Multiple analyses run inside that monitor instance.

Each JSON update is performed as a complete read-modify-write operation using a temporary file followed by atomic replacement. If a target file is temporarily unavailable for writing, the writer waits briefly and retries up to a finite timeout. No separate lock file is required.

The monitor advances an analysis checkpoint only after the corresponding structural state has been successfully persisted.

## A19. Configuration

No separate mapper configuration file is required.

Mapper behavior is controlled by CLI parameters, explicit defaults, normalized market-data JSON metadata, and the canonical SMC skill.

Market-data provider configuration belongs to the Market Data CLI and is not a mapper semantic dependency.

`market_data.py` provides the CLI interface for market-data acquisition, normalization, incremental update, retention and persistence into `<SYMBOL>_marketdata.json`. It is a separate process.

No mapper configuration file is to be introduced for timeframe selection, history retention or analysis window.

Timeframe selection is controlled only by `--htf` and/or `--ltf` according to A4-A6.

Volume analysis is controlled by the optional mapper CLI parameter:

```
--volume-method {NONE,OHLC,ORDERFLOW}
```

When the parameter is omitted, the mapper uses automatic runtime selection in this order:

```
ORDERFLOW -> OHLC -> NONE
```

The selected method is an analysis-time processing decision. It is not persisted as a single exclusive volume provenance field in normalized market-data candles, and it does not remove or overwrite any parallel volume data that is available. Explicit CLI values override automatic selection.

## A19.1 CLI debug output

The CLI interfaces must strictly separate persistent market data from user-visible diagnostics.

- Normalized candle data is persisted to `<SYMBOL>_marketdata.json` and is not emitted as a mapper data pipe.
- Debug and diagnostic information is written to `stderr` only.
- Debug `stderr` is terminal-only. The launcher/monitor must not capture, parse, forward, merge, persist, or pass it to `smc_mapper.py`, `smc_monitor.py`, or the market-data JSON.
- `stderr` must never be merged into a machine-readable data channel.
- Without `--debug`, debug/trace output is suppressed.
- With `--debug`, diagnostics are visible directly on the terminal.
- Debug mode must never alter canonical calculations or normalized market-data semantics.
- Normal runtime must produce no user-visible CLI output.

### Market Data CLI contract

market_data.py is invoked as a standalone process. Its CLI accepts:

    --symbol SYMBOL
    --timeframes TF [TF ...]
    --starttime ISO8601
    --endtime ISO8601
    --lastcandle
    --live
    --debug

symbol is required. timeframes accepts one or more supported timeframes and is not limited to the mapper's one- or two-timeframe analysis model. starttime and endtime are optional range bounds.

--lastcandle is an alternative completed-candle acquisition mode. When supplied, the Market Data CLI retrieves exactly the latest completed candle for each requested timeframe and reconciles it into that timeframe's candles[] series. It does not refresh or replace the current in-progress snapshot by itself.

--lastcandle is mutually exclusive with --starttime and --endtime because it requests a single latest completed candle rather than a historical range. --lastcandle may be combined with --live: in that case the latest completed candle is reconciled into candles[] and the latest in-progress snapshot is refreshed independently in current when available.

If the latest completed candle is already present in the persisted timeframe series, deduplication leaves the existing candle identity intact and no duplicate record is created. --lastcandle never fabricates a candle and never causes an incomplete/current candle to enter candles[].

Without live, the CLI persists completed candles only. With live, it also refreshes the latest provider-available in-progress candle snapshot for each requested timeframe when such a snapshot exists. If an endtime is supplied before the current interval, no current snapshot is stored for that request.

When an in-progress candle later becomes completed, its final completed version is persisted in candles[] and the next in-progress interval becomes current.

Market-data CLI execution persists the durable market-data result to <SYMBOL>_marketdata.json.

The market-data record may preserve volume information in parallel. Provider total volume, if available, is stored as volume.total; genuine orderflow may be stored under volume.orderflow; OHLC-derived directional estimates may be stored under volume.ohlc. The mapper determines which analytical data is actually available from the persisted record and may expose a helper such as has_volume_data(...) for boolean availability checks. No single exclusive candle-level method field represents provenance.

### Process-launch requirement

```text
market_data.py
    |
    +--> <SYMBOL>_marketdata.json
    |
    +--> stderr -> terminal (debug only)

smc_mapper.py
    |
    +--> reads <SYMBOL>_marketdata.json
    |
    +--> stderr -> terminal (debug only)
```

`stderr` must never be redirected into mapper or monitor data input.

With `--debug`, only the relevant process's diagnostics become visible on the terminal. Debug information is never written into the market-data JSON and never becomes mapper or monitor input.

# B. CANDLE / MARKET DATA NORMALIZATION


## B1. Provider boundary

The Market Data CLI, outside the canonical mapper, receives provider-specific market data, converts it into a provider-independent normalized candle representation, and persists the normalized candles into `<SYMBOL>_marketdata.json`.

Provider-specific data
        |
        v
market_data.py (CLI)
  acquisition / normalization
        |
        v
<SYMBOL>_marketdata.json
        |
        +-------> smc_mapper.py
        |
        +-------> smc_monitor.py

Canonical SMC logic must consume only normalized candle data.

Provider-specific API access, transport, retry, pagination, authentication, timestamp parsing, completion detection, and raw-field mapping belong to the Market Data CLI.

The concrete implementation resides initially in one standalone executable Python module, `market_data.py`. It may later be split internally without changing the persisted market-data schema or CLI contract.

The Market Data CLI must support deterministic range retrieval and incremental update rather than requiring one provider request per candle.

## B2. Normalized candle representation

Each normalized completed candle must contain at minimum:

- candle_id
- timestamp
- open
- high
- low
- close

When the provider supplies total candle volume, preserve it as normalized volume.total.

When genuine orderflow data is available, preserve it independently under volume.orderflow.

OHLC-derived directional volume is an analytical estimate and may be stored independently under volume.ohlc. It must never overwrite or be represented as observed orderflow.

A normalized candle may therefore contain parallel volume information:

    volume.total
    volume.ohlc = { buy, sell, delta }
    volume.orderflow = { buy, sell, delta }

Each nested volume section is optional and exists only when its corresponding data or deterministic estimate is available. Presence or absence is the availability signal; no single exclusive candle-level method field is required.

candles[] contains only completed normalized candles and is immutable after persistence. The separate current snapshot may change while its candle is in progress.

The current snapshot carries the same candle identity and basic OHLC fields needed to identify the in-progress interval. It may also contain the provider-available total volume and any separately available orderflow data for that interval. It is runtime state only and is not included in completed-candle retention or canonical structural history.

## B3. Candle identifier

`candle_id` must be deterministic and stable across repeated downloads of the same candle.

It must be derived from stable candle identity information rather than from an in-memory array index.

The candle index must never be used as permanent candle identity.

The exact identifier format remains an implementation detail.

---

## B4. Timestamp normalization

All normalized timestamps must be represented consistently in UTC.

Provider-specific timezone information must be normalized before canonical analysis.

Provider timezone details must not leak into canonical SMC calculations.

---

## B5. Chronological ordering

Normalized candles must be strictly chronological:

```
timestamp[n] < timestamp[n+1]
```

The normalization layer must reject:

- duplicate timestamps;
- reverse-ordered timestamps;
- ambiguous timestamps that cannot be normalized deterministically.

The canonical engine receives an already ordered series.

---

## B6. Completed-candle requirement

Only completed candles may enter canonical analysis.

A candle is considered completed only after its canonical timeframe interval has closed and the normalized provider/completion contract confirms that closure.

The mapper must use the candle's canonical completion boundary when deciding whether it is eligible for an explicit analysis end time. The candle timestamp is not by itself sufficient evidence of completion.

An incomplete/current candle must be excluded from the canonical analysis series. It may be stored only in the per-timeframe current snapshot of <SYMBOL>_marketdata.json and must never be consumed as canonical structural input.

The current snapshot is runtime market-data state, not historical candle state. Refreshing it must not alter structural history or mapper checkpoints.

## B7. Numeric representation

OHLC values must use a deterministic financial numeric representation.

The canonical implementation must use `Decimal`, not binary floating-point values, for normalized OHLC prices.

Invalid values include:

- NaN;
- Infinity;
- non-numeric values;
- silently coerced invalid numeric values.

The same deterministic numeric policy applies to normalized volume values when present. Total, buy, sell, and delta volume values must use Decimal-compatible deterministic numeric representation, be finite, and must not be silently coerced or fabricated.

---

## B8. OHLC / OLHC integrity

Every normalized candle must satisfy the basic OHLC constraints:

```
high >= low
low <= open <= high
low <= close <= high
```

In addition, the candle direction must be consistent with its canonical candle-formation model:

### Bullish candle

```
Low <= Open < Close <= High
canonical formation model = OLHC
```

### Bearish candle

```
Low <= Close < Open <= High
canonical formation model = OHLC
```

### Doji

```
Low <= Open = Close <= High
no directional OLHC/OHLC formation model
```

OHLC/OLHC here is a **methodology formation model**, not historical intrabar evidence.

Aggregate OHLC must never be used to fabricate the historical order in which intrabar extremes were reached.

Invalid OHLC/formation data must be rejected rather than silently repaired.

---

## B9. Missing candles / data gaps

The mapper must not manufacture synthetic candles to fill missing provider data.

Examples include:

- non-trading periods;
- market holidays;
- provider gaps;
- unavailable historical intervals.

A missing candle is not equivalent to a zero-volume or unchanged candle.

The temporal gap must remain observable to the provider/normalization/orchestration layer.

Whether a particular gap prevents a downstream structural calculation is determined by the relevant canonical layer, not by the normalization layer.

---

## B10. Timeframe integrity

Every normalized candle series belongs to exactly one timeframe.

A candle from one timeframe must never be silently mixed with another timeframe.

For a two-timeframe analysis:

```
HTF candle series
LTF candle series
```

remain distinct series.

---

## B11. Symbol integrity

A normalized candle series belongs to exactly one symbol for a mapper execution.

Data from different symbols must never be merged into the same canonical candle series.

---

## B12. Provider-independent semantics

Provider-specific concepts must be normalized before the canonical engine receives the data.

Examples include:

- provider-specific timestamp formats;
- provider-specific field names;
- provider-specific completion flags;
- provider-specific numeric representations;
- provider-specific timezone conventions.

The canonical engine must not contain provider-specific conversion logic.

---


## B13. Data availability

`market_data.py` persists the actual available temporal range of each timeframe in `<SYMBOL>_marketdata.json` and may expose it through an explicit CLI availability operation.

At minimum, each timeframe section tracks:

- `available_start`
- `available_end`

This is important because HTF and LTF may have different available history.

The mapper distinguishes requested analysis range from available/retained market-data range and reads the required range from the corresponding timeframe section of `<SYMBOL>_marketdata.json`.

If the requested range is outside the retained market-data window, the launcher triggers Market Data CLI reacquisition before mapper processing.

If the requested range cannot be supplied, the mapper must represent the resulting data/context unavailability explicitly and must fail closed where a canonical decision depends on unavailable information.

The mapper does not access provider availability APIs directly.

## B14. Data clipping

The Market Data CLI must not discard candles from a requested acquisition range before persistence.

The launcher ensures that all required bootstrap/warm-up candles are acquired and persisted through the Market Data CLI, and the mapper then determines the effective analysis interval from the persisted data and requested start/end constraints.

Market-data retention may remove older candles according to the bounded timeframe retention policy. Such removal is storage policy only and does not rewrite mapper structural history.

If a later analysis requires removed candles, the Market Data CLI reacquires the missing range from the provider before that analysis is processed.

## B15. Candle metadata

The canonical candle representation contains information required for candle-level structural processing.

Provider-specific metadata must not enter the canonical candle representation unless a canonical rule explicitly requires it.

---

---

## B16. Deterministic normalization

Given the same provider data and normalization policy:

```
same raw data
      ↓
same normalized candles
```

Normalization must not depend on:

- current wall-clock time;
- array position;
- random identifiers;
- mutable global state.

---

## B17. Normalization failure

Invalid provider data or normalization failure must not be silently ignored.

The mapper must report sufficient information to identify the affected symbol, timeframe and candle/time range.

The canonical engine must never receive malformed or ambiguous candle data.

---

## B18. Volume retention

When total traded volume is available from the provider, market_data.py preserves it as volume.total on the underlying normalized candle.

When genuine orderflow is available, it is preserved independently under volume.orderflow. When deterministic OHLC directional estimation is available, it may be preserved independently under volume.ohlc.

The mapper must preserve the applicable volume information when storing structural-point references to source candles. Parallel volume types must not overwrite one another.

Volume provenance is represented by the data branch that is actually present. A single exclusive volume source or volume method field is not required on the candle.

# C. HTF-GUIDED LTF EXECUTION CONTEXT

## C1. Independent timeframe analysis

Each timeframe is analyzed according to its own canonical structural rules.

In two-timeframe mode, HTF and LTF remain separate canonical analyses while sharing a synchronized execution timeline.

The LTF is not a canonical child of the HTF and must not redefine or mutate HTF structure.

The HTF provides the execution context required by canonical LTF rules where such context is explicitly specified.

In single-timeframe mode, no HTF/LTF execution relationship exists.

## C2. HTF/LTF synchronization and execution context

When an HTF and LTF are both supplied:

1. the launcher ensures the required HTF range is present in `<SYMBOL>_marketdata.json`; the mapper reads it and establishes the current HTF canonical structural context first;
2. the mapper determines the applicable HTF execution context and any LTF bootstrap/activation requirement;
3. the launcher ensures the LTF range required by the applicable analysis state is present in `<SYMBOL>_marketdata.json`; the mapper reads that persisted range;
4. HTF and LTF candles are processed chronologically on the shared time axis;
5. each LTF candle is evaluated using only HTF canonical context that already exists at that LTF evaluation time;
6. a later HTF event must never reinterpret an earlier LTF event.

The LTF exists to refine and qualify entry within the applicable HTF context; it does not create a competing higher-level narrative.

The existence of HTF context must not automatically invalidate an LTF structural event. Only canonical rules that explicitly require HTF context may use it as a qualification, activation, or routing condition.

HTF/LTF synchronization is an orchestration relationship around persisted normalized market-data ranges; it does not transfer semantic ownership from HTF rules to LTF rules.

## C3. Point-in-time HTF context

For every LTF evaluation that requires HTF information, only HTF structural facts that already existed at that evaluation time may be used.

For each consumed HTF structural fact:

"formation_time <= LTF evaluation_time"

A later HTF structural event must never be used to reinterpret an earlier LTF event.

The applicable HTF Dealing Range and the canonical HTF structural facts available at that point in time provide the LTF context reference.
## C4. LTF structures within HTF range context

In two-timeframe analysis, LTF structural records may be stored within the applicable HTF Dealing Range record for execution-context organization.

This storage relationship uses the HTF Dealing Range as the LTF context container; it does not define an LTF structural start or transfer semantic ownership:

```
HTF Dealing Range
    ↓
execution context
    ↓
LTF canonical structure
```

The number of LTF structures associated with an HTF Dealing Range is unrestricted by "history_no".

An LTF structure must not be duplicated merely because multiple LTF evaluations occur inside the same HTF range.

For deterministic storage association, an LTF structural record is associated with the HTF Dealing Range that is applicable at that LTF structure's canonical `formation_time`. The association is storage/context provenance only; it does not change the LTF structure's canonical formation time, lifecycle, or semantic ownership.

If the LTF structure forms while a confirmed HTF Dealing Range is current, it is stored under that range. If no confirmed HTF Dealing Range exists at the LTF structure's formation time, the structure must not be assigned to a fabricated range.

When an HTF Dealing Range transition and an LTF formation occur at the same timestamp, the HTF lifecycle update is applied first on the synchronized timeline; the LTF structure is therefore associated with the HTF context that is canonical after that timestamp's HTF lifecycle processing.

If an LTF lifecycle crosses an HTF range transition, the canonical LTF lifecycle remains unchanged. The stored representation retains its original HTF context association and sufficient canonical provenance to represent the cross-boundary lifecycle without duplicating the same LTF object.

## C5. Canonical HTF-interaction routes

Where a canonical LTF route explicitly requires HTF interaction, the mapper consumes the applicable HTF context from its structural state and reads any required additional LTF analysis range from `<SYMBOL>_marketdata.json`; the launcher ensures that range is present before mapper execution.

This includes the canonical LTF Structural Glitch / CHoCH route after HTF POI interaction or HTF core-liquidity takeout, as defined by `05_CHOCH_mechanics.md`.

The mapper must align the persisted candle range with the applicable point-in-time HTF context but must not invent a new CHoCH, BOS, IDM, POI, or entry rule.

## C6. Historical independence

HTF history and LTF context-scoped records are structural analysis data, not dynamic monitor state.

Retention of HTF closed ranges is controlled by the single symbol-level `history_no`.

LTF structures do not consume a separate history quota.

Retention eviction must never invalidate canonical structure or cause historical LTF decisions to be rewritten.

The mapper preserves the canonical distinction between:

```
canonical structural truth
        ≠
JSON retention
        ≠
dynamic monitoring/trade state
```

---

## C7. Canonical ownership boundary

HTF canonical semantics remain owned by the HTF analysis and its canonical skill layers.

LTF canonical semantics remain owned by the LTF analysis and its canonical skill layers.

The mapper defines only the orchestration and storage relationship between them.

It must not introduce a general HTF-parent/LTF-child semantic ontology.

---

# D. POI VOLUME / DELTA ANALYTICS

## D1. Scope

POI volume analytics is a non-canonical analytical extension of the canonical POI result.

It may enrich an already canonical POI with total volume, buy volume, sell volume, volume delta, directional delta ratio, and a statistical probability value when a usable volume method and calibrated probability model are available.

Volume analytics must never create, remove, retype, or canonically invalidate a POI.

The canonical POI ontology and Rule-of-Two remain owned by Layer 6.

## D2. POI volume provenance

POI volume must be calculated from candles deterministically associated with the POI's canonical provenance.

The mapper must not use an arbitrary fixed number of candles around the POI.

Where available, the JSON should distinguish formation volume, causal displacement volume, and their aggregate.

For a multi-leg canonical OF, the complete canonical opposing move must be represented where that move is the POI provenance; the implementation must not reduce it to an arbitrary final sub-leg.

Historical POI outcome performance must not be used.

## D3. Volume method

The normalized market-data record may contain multiple volume types in parallel. Availability is determined from the actual presence of the relevant data, not from one exclusive provenance or method field.

The user may explicitly select the analytical method with:

    --volume-method {NONE,OHLC,ORDERFLOW}

When omitted, the effective analytical method is selected automatically in this order:

    ORDERFLOW -> OHLC -> NONE

ORDERFLOW requires genuine orderflow buy/sell volume and delta in volume.orderflow.

OHLC requires volume.total and calculates directional buy/sell volume and delta deterministically from OHLC data. Suitable lower-timeframe data may refine the estimate.

NONE means that no supported analytical volume path is available.

The selected analytical method is a runtime processing decision. It does not erase, overwrite, or relabel other available volume data.

If ORDERFLOW is explicitly requested and unavailable, the mapper must not silently downgrade to OHLC.

If OHLC is explicitly requested but required volume data is unavailable, the mapper must not fabricate volume values.

The concrete external provider is implementation-defined and is not part of canonical SMC semantics.

An estimated buy/sell split must never be represented as observed orderflow data.

## D4. Aggregate-OHLC calculation

For each candle with total volume V and High > Low:

```
buy_volume  = V * (Close - Low) / (High - Low)
sell_volume = V * (High - Close) / (High - Low)
delta       = buy_volume - sell_volume
delta_ratio = delta / V
```

Therefore:

```
buy_volume + sell_volume = V
delta = V * (2*Close - High - Low) / (High - Low)
```

If High == Low:

```
buy_volume  = V / 2
sell_volume = V / 2
delta       = 0
delta_ratio = 0
```

This is a directional volume estimate, not proof of historical bid/ask execution.

## D5. OHLC lower-timeframe refinement

When `--volume-method OHLC` is selected and suitable lower-timeframe data is available, directional volume should be calculated from the contained completed intrabars instead of directly splitting the parent candle.

For each intrabar:

```
Close > Open → buy side
Close < Open → sell side
Close = Open → neutral; do not force a side
```

Parent-bar buy volume, sell volume and delta are the sums of the classified intrabar volumes.

OHLC-derived directional volume is stored under volume.ohlc; genuine orderflow data is stored under volume.orderflow. The two branches may coexist for the same candle.

## D6. POI JSON representation

Each canonical POI may contain parallel volume-analytics branches.

The logical representation is:

    volume.ohlc
        formation
        causal_displacement
        aggregate

    volume.orderflow
        formation
        causal_displacement
        aggregate

Each formation, causal_displacement, and aggregate object may contain total, buy, sell, delta, and delta_ratio.

The ohlc and orderflow branches may coexist for the same POI. Values are omitted or null only when the relevant provenance data is unavailable.

The runtime-selected analytical method does not delete or overwrite the other available branch.

When no supported volume analytical path is available, no volume-derived analytics or POI probability is calculated.

## D7. Statistical POI probability

The mapper may expose a **statistical probability** for an already canonical POI.

This value must represent an actual calibrated probability estimate, not a volume ratio, directional score, confidence score, or percentage derived directly from buy/sell volume.

POI-linked volume and delta are model inputs/features. They may increase or decrease the estimated probability, but the mapper must not convert:

```
buy / total
sell / total
delta / total
```

directly into a probability.

A valid probability requires an explicitly defined statistical model that has been trained/calibrated on labeled observations and whose output is interpretable as an estimated probability of the defined POI outcome.

The mapper runtime uses the current canonical POI context and its available volume/orderflow features as model inputs. The mapper does not calculate historical POI success rates on the fly.

The outcome being predicted must be explicitly defined by the statistical model contract. The model must not use an undefined notion of "POI success".

The stored value is a probability in normalized numeric form:

```
0.0 <= probability <= 1.0
```

not a percentage field.

For human-readable output, the mapper/reporting layer may display the same value as a percentage (for example, `0.73` displayed as `73%`), but the JSON canonical numeric representation remains `0.73`.

Recommended JSON representation:

```json
"probability": {
  "value": 0.73,
  "model": "MODEL_ID",
  "model_version": "VERSION",
  "calibrated": true
}
```

If no calibrated statistical model is available, probability must be absent/undefined. The mapper must not fabricate a probability from delta or volume ratios.

When method = NONE, no volume-derived statistical probability can be evaluated and the probability calculation branch must not run.

## D8. Statistical model provenance

Every POI probability record must retain sufficient provenance to identify and reproduce the probability estimate, including where applicable:

- model identifier;
- model version;
- calibration status;
- outcome definition/version;
- input feature set/version;
- volume method;
- source candle IDs or canonical provenance references;
- formation start/end;
- causal displacement start/end.

The statistical probability must never be used by downstream code as canonical POI validity.

The probability must be visible for each canonical POI for which a calibrated model and required inputs are available. If the probability cannot be evaluated, it must be absent/undefined rather than replaced by a neutral value.

When method = NONE, downstream code must treat volume analytics and probability as absent rather than as a zero/neutral weighting.

A statistical probability model necessarily requires empirical observations for training/calibration. Those observations may be prepared and maintained outside the mapper runtime; the mapper only consumes the resulting calibrated model. Without such empirical calibration, a true statistical probability cannot be claimed.
