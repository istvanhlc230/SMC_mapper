# SMC Mapper Specification

**Status:** Working specification. Sections are approved incrementally.  
**Scope:** Functional and implementation specification for the future `smc_mapper.py`.  
**Canonical authority:** `.agents/skills/smc/` remains the sole authority for canonical SMC semantics. This document does not redefine those rules.

---

# A. INPUT / ORCHESTRATION

## A0. Active product runtime components

The intended finished product uses these active Python runtime components:

- `market_data.py` — standalone Market Data CLI: provider access, normalization, completion handling, and deterministic candle-range retrieval. It emits the normalized candle contract for downstream consumers.
- `smc_mapper.py` — canonical SMC mapper: structural analysis, HTF/LTF processing, and persistent structural state.
- `smc_monitor.py` — interactive runtime: scheduling, user interaction, runtime/target monitoring, and alerts.

The older `smc_htf_ltf_monitor.py`, `smc_analyzer.py`, and Layer-1-to-Layer-6 `*_engine.py` test/implementation artifacts are not components of the finished product architecture.

This specification defines the mapper contract and its boundaries with the Market Data Layer and interactive monitor.
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

When both timeframes are supplied, the mapper obtains the required normalized HTF/LTF candle ranges from the Market Data Layer and processes them chronologically on their shared time axis.

"HTF context establishment -> synchronized HTF/LTF processing"

The HTF analysis provides the structural context required by canonical LTF rules. The LTF analysis may consume that context where required, but the LTF analysis must never redefine or mutate HTF structure.

Within synchronized processing:

- a newly completed HTF candle updates HTF canonical state before later LTF evaluations may consume that new HTF information;
- each completed LTF candle is evaluated against only the HTF canonical context that already exists at that LTF evaluation time;
- the mapper does not use a later HTF event to reinterpret an earlier LTF event.

The mapper determines which candle ranges are required and obtains them from the Market Data CLI in deterministic batch form. The CLI response is the mapper's market-data input boundary. It does not request market data from the monitor.

When only one timeframe is supplied, only that timeframe is analyzed.
## A7. Start time

`--starttime` defines the requested start of the analysis window.

It may be specified as:

- a date, or
- an exact datetime.

Examples:

`--starttime 2026-09-01`

`--starttime 2026-09-01T09:30:00`

The mapper does not access a concrete provider to obtain earlier candles. Any candles required for structural bootstrap/warm-up are obtained by invoking the Market Data CLI for the required normalized range.

The mapper must distinguish:

- `requested_start`
- `effective_start`

If the requested start precedes the available completed data, the mapper uses the earliest supplied completed candle that is valid for the requested analysis/bootstrap and reports that the effective start is later than requested.

Missing historical data must never be fabricated.
## A8. End time

`--endtime` is optional.

It may be specified as:

- a date, or
- an exact datetime.

Examples:

`--endtime 2026-09-29`

`--endtime 2026-09-29T15:30:00`

If omitted, use the latest supplied completed driving-timeframe candle.

If supplied, use the latest supplied completed candle whose canonical completion boundary is less than or equal to the requested end time.

The normalized candle `timestamp` alone must not be treated as proof that a candle has completed. Completion is determined by the normalized completion status/time contract in B6.

An incomplete/current candle must never enter canonical analysis.


## A9. Independent timeframe feed ranges

HTF and LTF candle data may cover different temporal ranges.

The Market Data CLI owns acquisition and exposes the actual available range for each timeframe through its normalized CLI contract. The mapper obtains only the range required by its current analysis and must not fabricate unavailable candles.

Example:

- HTF data: 2026-06-01 -> 2026-09-29
- LTF data: 2026-01-01 -> 2026-09-29

The longer LTF history must not be truncated merely because the HTF history is shorter.

The absence of HTF data before its available start does not imply that HTF structure did not exist.

Availability metadata may be used by the mapper to determine whether a requested structural range can be satisfied. If the required range cannot be satisfied, the mapper must represent the resulting data/context unavailability explicitly and fail closed where canonical rules require unavailable context.

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


## A11. HTF Closed Dealing Range history and `history_no`

`history_no` is one **collective symbol-level value**.

In **two-timeframe analysis**, it applies to the HTF CLOSED DEALING RANGE history only. It defines the maximum number of recent closed HTF Dealing Ranges retained in the symbol JSON.

The LTF does **not** have a separate `history_no`. Any number of LTF structural records may be interpreted and stored within the context of an HTF Dealing Range. The number of LTF structures is therefore not limited by `history_no`.

The history unit is the canonical closed Dealing Range. Only a Dealing Range that has been canonically closed may enter history. The currently open HTF Dealing Range is never a history item.

Retention is newest-first by canonical HTF `close_time`, with **oldest-first (FIFO) eviction** when capacity is exceeded.

Example with `history_no = 3`:

```
R1 -> [R1]

R2 -> [R2, R1]

R3 -> [R3, R2, R1]

R4 -> [R4, R3, R2]
               R1 evicted
```

Eviction is a storage-retention operation only. A range evicted because of `history_no` remains canonical historical structure; it is not invalidated, deleted semantically, or marked stale.

A repeated mapper execution must not create a duplicate closed HTF range when the same range identity is already retained.

In **single-timeframe analysis**, where no distinct HTF/LTF pair exists, `history_no` applies to the selected timeframe's CLOSED DEALING RANGE history.

## A12. Closed Dealing Range identity and retention configuration

A stored CLOSED DEALING RANGE is identified by the tuple:

```
timeframe + start_time + close_time
```

This is the history identity. `structure_hash` is not a closed-range identity and must not be used to distinguish repeated representations of the same closed range.

`start_time` and `close_time` are lifecycle timestamps derived from the canonical Dealing Range lifecycle. The mapper must not invent a new range-start rule, provisional range boundary, or synthetic start timestamp.

`formation_time`, where present on structural objects or state within the range, identifies when that structural object/state formed. It is semantically distinct from the Dealing Range `close_time`.

A closed range's identity is immutable once canonically closed. For an existing retained range with the same identity, reconciliation updates that range in place rather than creating a duplicate. A newly closed range with a new identity is inserted. If a previously evicted range is reconstructed, it may be reinserted using its canonical identity when it again falls within the retained window.

### `history_no` persistence rules

`history_no` is stored **once per symbol JSON**, not per timeframe.

- **New symbol JSON** + no `--history_no` -> initialize and persist `history_no = 5000`.
- **New symbol JSON** + `--history_no=N` -> initialize and persist `history_no = N`.
- **Existing symbol JSON** + no `--history_no` -> preserve the stored `history_no`.
- **Existing symbol JSON** + `--history_no=N` -> `--history_no` has **no effect**. Preserve the stored `history_no`; do not update or replace it from the CLI.
- If an existing symbol JSON has no stored `history_no` value, initialize and persist `history_no = 5000`. A CLI `--history_no=N` still has no effect for that existing file.
- `N` must be an integer >= 1 when the CLI value is supplied.

`--history_no` is therefore a **creation-time setting only**. Once the symbol JSON exists, the stored collective `history_no` is authoritative.

Changing `history_no` changes retention capacity only. It does not change canonical SMC semantics.

---

## A12a. HTF Dealing Range history contract

Each retained history element represents one CLOSED HTF Dealing Range and may contain the canonical HTF structural state and, where two-timeframe analysis is active, any number of LTF structures interpreted in that HTF range context.

The LTF records stored under an HTF range are **context-scoped execution analysis**, not a new canonical parent/child ontology. LTF semantic ownership remains with the LTF canonical rules.

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

The history record must preserve the canonical formation/provenance times of its contained objects.

History is not an append-only mapper execution log. It is a retained representation of canonically closed HTF Dealing Ranges with their context-scoped LTF analysis.

The mapper must reconcile canonical closed HTF ranges deterministically:

1. same `timeframe + start_time + close_time` -> update existing retained HTF range;
2. new identity -> insert new HTF range;
3. duplicate identity -> never create a second history entry;
4. reconcile the associated LTF context-scoped records without changing their canonical ownership;
5. apply the single symbol-level `history_no` after reconciliation;
6. if capacity is exceeded, evict the oldest retained HTF Dealing Range.

A range falling outside the retention window is not a canonical removal event.

### A12b. Dealing Range lifecycle boundary

The mapper derives Dealing Range history boundaries strictly from the canonical structural lifecycle.

- A currently open Dealing Range is runtime state, not history.
- `VALID_BOS` is the canonical lifecycle event that establishes the next confirmed Dealing Range lifecycle; when a governing range already exists, it closes that previous range first. The first `VALID_BOS` establishes the first confirmed Dealing Range and therefore has no pre-existing governing range to close.
- The mapper must not close or start a Dealing Range because of a physical break, IDM sweep, CHoCH-eligible break, insufficient-retracement `IMPULSE_EXTENSION`, mapper execution boundary, or retention operation.
- Before the first canonical `VALID_BOS`, no governing Dealing Range may be fabricated for history or used as a substitute for the unresolved first-BOS canonical baseline.
- The exact first-BOS retracement baseline remains the canonical/source gap documented by the SMC skill; the mapper must fail closed rather than invent a synthetic initialization rule.

---

## A13. JSON storage

Use **one JSON file per symbol**.

Example:

```
structures/
    CCCC.json
    BABA.json
    DTE.DE.json
```

A mapper execution for one symbol updates only that symbol's file.

The monitor must be capable of discovering and processing all symbol files.

There is no single multi-symbol mapper JSON file.

Illustrative logical structure for two-timeframe analysis:

```json
{
  "symbol": "CCCC",
  "history_no": 5000,
  "htf": "H4",
  "ltf": "M15",
  "last_processed_candle_time": "2026-09-29T18:45:00Z",

  "current": {
    "start_time": "...",
    "close_time": null,
    "structural_state": {},
    "ltf_structures": []
  },

  "history": [
    {
      "start_time": "...",
      "close_time": "...",
      "structural_state": {},
      "ltf_structures": [
        {},
        {}
      ]
    }
  ]
}
```

This is a logical schema illustration, not a new canonical ontology.

- "history_no" is stored once at symbol level.
- In two-timeframe mode it limits retained CLOSED HTF Dealing Ranges only.
- "ltf_structures" are context-scoped records inside the applicable HTF range and are not counted against "history_no".
- "current.start_time" and historical "start_time" values are HTF Dealing Range lifecycle timestamps. They are not separate LTF start timestamps.
- "last_processed_candle_time" is root-level mapper processing metadata and, in two-timeframe mode, refers to the LTF driving timeframe already identified by "ltf".

The JSON does not require a separate "ltf" object merely to repeat the LTF timeframe.
## A14. Stored state

The mapper JSON stores canonical **structural analysis** plus the minimal mapper-processing metadata required for deterministic incremental execution.

It may contain canonical structural state, provenance and structural history, including:

- structural lifecycle/state;
- structural swings;
- protected structural extremes;
- dealing range;
- IDM state/provenance;
- retracement qualification;
- BOS;
- CHoCH;
- canonical L6 structural / POI results;
- retained closed Dealing Range history;
- structural provenance/change metadata (distinct from CLOSED DEALING RANGE history identity).

The mapper must not persist dynamic monitoring or trade state such as:

- current market price;
- active trade/order state;
- stop state;
- break-even state;
- trailing state;
- target-hit state.

Those are owned by the monitor.

The root-level "last_processed_candle_time" is an exception to the structural-only content above: it is mapper processing provenance/checkpoint metadata and carries no canonical SMC meaning.

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

The mapper has no direct connection to any concrete market-data provider and has no in-process dependency on `market_data.py`.

`market_data.py` is a standalone Market Data CLI process. It owns provider access, provider abstraction, normalization, completion handling, timestamp normalization, price-basis handling, availability detection, and deterministic candle-range retrieval.

The only mapper-to-market-data boundary is **CLI data transfer**.

The Market Data CLI accepts a deterministic range request, for example:

    python market_data.py --symbol CCCC --timeframe M15 --start 2026-09-01T00:00:00Z --end 2026-09-29T18:45:00Z

It emits the normalized candle contract on stdout. The mapper consumes that normalized result through its CLI input boundary. The exact transport mechanism is an implementation detail, but the runtime contract remains CLI-based.

The normalized candle contract is the portability boundary. The mapper must not know whether the Market Data CLI obtained the range from Yahoo, MT4/MT5, Pine/replay, a broker adapter, or another provider.

The monitor may orchestrate the CLI calls and may independently invoke the Market Data CLI for runtime/current-data needs. The monitor is not a provider relay and does not feed individual candles through a Python object API.

The architectural relationship is:

```text
Provider(s)
    |
    v
market_data.py (CLI)
    |
    | normalized candle range
    v
smc_mapper.py (CLI)
    |
    v
structural JSON
    |
    v
smc_monitor.py
```

The architecture must not require:

- importing `market_data.py` into the mapper;
- a shared in-memory `CandleStore` between processes;
- a mapper-to-monitor `DATA_REQUEST` channel;
- direct mapper access to Yahoo Charts or another concrete provider;
- provider-specific response formats inside the mapper.

Any cache or buffer used by the Market Data CLI is an implementation optimization only. It is not shared runtime state with the mapper and must not be required for correctness. If persistence is later added, it remains behind the Market Data CLI boundary.

Future provider adapters may include:

- Yahoo Charts;
- MetaTrader / MT4 / MT5;
- Pine Script data integration;
- broker feeds;
- historical/replay sources.

Provider-specific API details remain outside the canonical SMC engine.

The normalized candle contract is the portability boundary for future platform adapters.

## A17. Bootstrap

The mapper constructs structural state by processing normalized candle ranges received through the Market Data CLI boundary.

For an initial build, or whenever a complete bootstrap is explicitly required:

earliest required effective candle -> latest completed driving-timeframe candle

The mapper must not use a latest-window shortcut that bypasses required structural bootstrap.

The launcher invokes the Market Data CLI for the required bootstrap range in deterministic batch form and passes the normalized result to the mapper CLI. The mapper does not obtain bootstrap data from the monitor and does not access a concrete provider.

For incremental execution after a valid persisted checkpoint, the launcher invokes the Market Data CLI for only the subsequently completed driving-timeframe range after the checkpoint, in chronological order, then passes that normalized range to the mapper CLI as defined by A18.

### A17.1 Two-timeframe LTF bootstrap

In two-timeframe analysis, the mapper establishes an LTF bootstrap coverage reference from the applicable HTF canonical structural context.

When a confirmed HTF Dealing Range exists, the applicable HTF Protected Structural Extreme is the preferred LTF bootstrap coverage reference. This reference determines the minimum historical LTF coverage needed for deterministic structural buildup. It is a data-coverage/reference point only; it is not an LTF structural start and does not create or promote any LTF structure.

When LTF bootstrap is required, the launcher invokes the Market Data CLI once for one deterministic LTF range covering the anchor through the activation/current boundary, subject to any additional LTF warm-up required by the canonical LTF rules, then passes that range to the mapper CLI.

If the requested LTF coverage begins later than the anchor because the source has no completed LTF data at or after the requested anchor, the mapper uses the first actually supplied completed LTF candle after the reference as the effective LTF bootstrap start. No attempt is made by the mapper to access the provider directly.

If the supplied LTF data begins before the HTF reference, that earlier data may be retained and used as additional canonical LTF warm-up when required; the HTF Protected Structural Extreme remains the context/coverage reference.

If the applicable confirmed HTF Protected Structural Extreme does not exist, the mapper does not fabricate one. The LTF bootstrap then follows the supplied LTF history subject to the canonical genesis/source-gap boundaries.

The LTF bootstrap reference is not an LTF structural-start ontology. The first LTF structural object is determined only by the canonical LTF rules.

The requested/effective analysis-window rules in A7-A8 and the Market Data Layer availability rules in A9/B13 continue to apply. No missing LTF candles are fabricated.

## A18. Monitor boundary and mapper checkpoint

The monitor owns interactive runtime control, scheduling, current-price/runtime monitoring, target monitoring, alerts/notifications, and CLI orchestration.

The mapper and Market Data CLI communicate only by CLI input/output. The mapper does not import `market_data.py` and the monitor is not a market-data object relay.

The normal runtime relationship is:

```text
                 smc_monitor.py
                      |
          invokes Market Data CLI
                      v
                 market_data.py
                      |
            normalized candle range
                      v
                 smc_mapper.py
                      |
               structural JSON
                      v
                 smc_monitor.py
```

A mapper CLI invocation consumes a complete normalized candle range for its requested execution. It must process the supplied range chronologically.

In two-timeframe analysis, the launcher first obtains the required HTF range through the Market Data CLI, then obtains the required LTF range through the same CLI boundary and passes the normalized ranges to the mapper. The mapper establishes HTF context first and processes LTF candles against point-in-time HTF context.

A mapper invocation may cover multiple newly completed driving-timeframe candles. No per-candle subprocess contract is required.

`last_processed_candle_time` is mapper processing metadata, not canonical SMC state and not dynamic trade/monitor state. It is stored once at the JSON root, alongside symbol, history_no, htf, and ltf.

The monitor/launcher uses the persisted checkpoint to determine the next required range. The checkpoint advances only when the corresponding mapper result is successfully persisted.

There is no mapper-to-monitor market-data request channel and no requirement for shared process memory.

## A19. Configuration

## A19.1 CLI debug output

The Market Data CLI and mapper CLI must keep machine-readable data separate from human-visible diagnostics.

- Normalized candle data and other machine-readable CLI payloads are written to **stdout**.
- During normal application runtime, the launcher/monitor must capture the CLI `stdout` stream and must not display it to the user.
- Debug, diagnostic, timing, provider/request tracing, cache/buffer messages, and non-data status messages are written to **stderr**.
- Without `--debug`, debug/trace diagnostics are suppressed; required errors may still be reported through the application's error handling.
- With `--debug`, diagnostic messages are emitted to `stderr` and are visible to the user.
- Normal runtime must therefore produce no user-visible CLI output.
- Debug mode must never alter canonical SMC calculations, normalized candle values, ordering, timestamps, or CLI data semantics.
- Debug output must never contaminate `stdout`, because `stdout` is the machine-readable data channel.
- A CLI invocation used by the finished product is expected to be orchestrated/captured by `smc_monitor.py` or an equivalent launcher; the machine-readable stream is not a user interface.

Example runtime flow:

    smc_monitor.py -> market_data.py (capture stdout) -> smc_mapper.py (capture stdout)

With debugging enabled:

    smc_monitor.py -> market_data.py (capture stdout, show stderr) -> smc_mapper.py (capture stdout, show stderr)

In both cases, the mapper data channel remains machine-readable and non-user-facing; only debug diagnostics become visible when `--debug` is enabled.


No separate mapper configuration file is required. CLI execution includes an optional `--debug` flag as defined in A19.1.

Mapper behavior is controlled by:

- CLI parameters;
- explicit defaults;
- normalized feed capabilities/metadata;
- canonical SMC skill.

Market-data provider configuration belongs to the market-data layer and is not a mapper semantic dependency.

`market_data.py` provides the required CLI interface for explicit candle-range retrieval. The CLI emits the normalized candle contract consumed by the mapper CLI and monitor runtime. No in-process Market Data service is required.

No mapper configuration file is to be introduced for timeframe selection, history retention or analysis window.

Timeframe selection is controlled only by `--htf` and/or `--ltf` according to A4–A6.

Volume processing is controlled by the optional CLI parameter:

```
--volume-method {NONE,OHLC,ORDERFLOW}
```

When the parameter is omitted, the mapper uses **automatic method selection** in this order:

```
ORDERFLOW → OHLC → NONE
```

Selection rules:

1. If compatible orderflow data is available from the active market-data feed, use `ORDERFLOW`.
2. Otherwise, if usable OHLC/volume data is available, use `OHLC`.
3. Otherwise, use `NONE`.

The selected effective method must be stored in the normalized data/output as `NONE`, `OHLC`, or `ORDERFLOW`.

Explicit CLI values override automatic selection:

- `NONE` — skip volume/delta analytics and POI likelihood calculation.
- `OHLC` — use OHLC-based directional volume/delta processing; if the required volume data is unavailable, volume analytics cannot be calculated.
- `ORDERFLOW` — require an orderflow-capable source; if the required orderflow data is unavailable, do not silently substitute another method.

The mapper does not require the user to know which provider supports which data level. Provider capabilities are detected by the market-data interface.

An unsupported CLI value is an input error.

The selected/effective volume method is a data/implementation choice and does not alter canonical SMC rules.

---

# B. CANDLE / MARKET DATA NORMALIZATION


## B1. Provider boundary

The Market Data CLI, outside the canonical mapper, receives provider-specific market data and converts it into a provider-independent normalized candle representation.

Provider-specific data
        |
        v
market_data.py (CLI)
  acquisition / normalization
        |
        v
Normalized Candle Range (stdout)
        |
        +-------> smc_mapper.py (CLI)
        |
        +-------> smc_monitor.py

Canonical SMC logic must consume only normalized candle data.

Provider-specific API access, transport, retry, pagination, authentication, timestamp parsing, completion detection, and raw-field mapping belong to the Market Data CLI.

The concrete implementation resides initially in one standalone executable Python module, `market_data.py`. It may later be split internally without changing the CLI or normalized candle contract.

The Market Data CLI must support deterministic range retrieval rather than requiring one provider request per candle.
## B2. Normalized candle representation

Each normalized candle must contain at minimum:

- `candle_id`
- `timestamp`
- `open`
- `high`
- `low`
- `close`

When volume processing is enabled and the source provides volume, the normalized candle may additionally contain:

- `volume`
- `buy_volume`
- `sell_volume`
- `delta`
- `volume_method`

where `volume_method` is one of `NONE`, `OHLC`, or `ORDERFLOW`.

For `NONE`, the volume/delta analytics path is skipped and the optional side-volume fields are not calculated.

The normalized representation is immutable after creation.

---

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

The mapper must use the candle's canonical completion boundary when deciding whether it is eligible for an explicit analysis end time. The candle `timestamp` is not by itself sufficient evidence of completion.

An incomplete/current candle must be excluded from the canonical analysis series.

## B7. Numeric representation

OHLC values must use a deterministic financial numeric representation.

The canonical implementation must use `Decimal`, not binary floating-point values, for normalized OHLC prices.

Invalid values include:

- NaN;
- Infinity;
- non-numeric values;
- silently coerced invalid numeric values.

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

`market_data.py` must expose the actual available temporal range of each requested timeframe through its CLI result or explicit availability response.

At minimum:

- available_start
- available_end

This is useful because HTF and LTF may have different available history.

The mapper distinguishes:

requested analysis range
available/supplied range

and obtains the required range through the Market Data CLI boundary.

If the requested range cannot be fully supplied, the mapper must represent the resulting data/context unavailability explicitly and must fail closed where a canonical decision depends on unavailable information.

The mapper does not access provider availability APIs directly.

## B14. Data clipping

The Market Data CLI must not prematurely clip away candles required for structural bootstrap.

The launcher requests a range that includes all required bootstrap/warm-up candles through the Market Data CLI, and the mapper then determines the effective analysis interval from the requested start/end constraints.

CLI range retrieval may internally use a provider cache or buffer and may include more historical candles than the final requested structural interval when those candles are required for deterministic warm-up. Such cache/buffer state is internal to the Market Data CLI and is not shared with the mapper process.
## B15. Candle metadata

The canonical candle representation contains information required for candle-level structural processing.

Provider-specific metadata must not enter the canonical candle representation unless a canonical rule explicitly requires it.

---

## B16. Price basis

The provider implementation must use a clearly defined and consistent historical price basis.

Adjusted and unadjusted historical prices must not be mixed within one analysis.

The selected price basis is a data-policy concern, not a canonical SMC semantic rule.

The same basis must be used across the full structural history of an analysis.

---

## B17. Deterministic normalization

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

## B18. Normalization failure

Invalid provider data or normalization failure must not be silently ignored.

The mapper must report sufficient information to identify the affected symbol, timeframe and candle/time range.

The canonical engine must never receive malformed or ambiguous candle data.

---

## B19. Volume retention

When traded volume is available from the provider, the mapper must preserve the volume associated with the underlying candle.

Volume must be stored with every stored structural point that references a candle for which volume is available.

This includes, where applicable:

- confirmed structural swings;
- protected structural extremes;
- IDM;
- BOS;
- CHoCH;
- canonical POI structural points.

Volume retention is market-data metadata only.

It must not become a canonical SMC decision input unless an explicit canonical skill rule defines a volume-dependent decision.


---

# C. HTF-GUIDED LTF EXECUTION CONTEXT

## C1. Independent timeframe analysis

Each timeframe is analyzed according to its own canonical structural rules.

In two-timeframe mode, HTF and LTF remain separate canonical analyses while sharing a synchronized execution timeline.

The LTF is not a canonical child of the HTF and must not redefine or mutate HTF structure.

The HTF provides the execution context required by canonical LTF rules where such context is explicitly specified.

In single-timeframe mode, no HTF/LTF execution relationship exists.

## C2. HTF/LTF synchronization and execution context

When an HTF and LTF are both supplied:

1. the launcher obtains the required HTF range from the Market Data CLI and passes the normalized range to the mapper CLI, which establishes the current HTF canonical structural context first;
2. the mapper determines the applicable HTF execution context and any LTF bootstrap/activation requirement;
3. the launcher obtains only the LTF range required by the applicable analysis state from the Market Data CLI and passes it to the mapper CLI in deterministic batch form;
4. HTF and LTF candles are processed chronologically on the shared time axis;
5. each LTF candle is evaluated using only HTF canonical context that already exists at that LTF evaluation time;
6. a later HTF event must never reinterpret an earlier LTF event.

The LTF exists to refine and qualify entry within the applicable HTF context; it does not create a competing higher-level narrative.

The existence of HTF context must not automatically invalidate an LTF structural event. Only canonical rules that explicitly require HTF context may use it as a qualification, activation, or routing condition.

HTF/LTF synchronization is an orchestration relationship implemented by the launcher/monitor around CLI-delivered normalized ranges; it does not transfer semantic ownership from HTF rules to LTF rules.
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

Where a canonical LTF route explicitly requires HTF interaction, the mapper consumes the HTF context already supplied in its CLI input and the launcher obtains any required additional LTF analysis range from the Market Data CLI.

This includes the canonical LTF Structural Glitch / CHoCH route after HTF POI interaction or HTF core-liquidity takeout, as defined by 05_CHOCH_mechanics.md.

The mapper must align the returned candle range with the applicable point-in-time HTF context but must not invent a new CHoCH, BOS, IDM, POI, or entry rule.
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

The user may explicitly select:

```
--volume-method {NONE,OHLC,ORDERFLOW}
```

When omitted, the effective method is selected automatically:

```
ORDERFLOW → OHLC → NONE
```

The Candle Data Interface/provider reports which volume information is actually available. The mapper then selects the highest available method in that order.

1. `ORDERFLOW` — use genuine orderflow buy/sell volume and delta supplied by an orderflow-capable source.
2. `OHLC` — calculate directional buy/sell volume and delta from available OHLC/volume data. Suitable lower-timeframe data may refine the estimate.
3. `NONE` — no volume/delta processing is performed.

For automatic selection:

- orderflow available → `ORDERFLOW`;
- no orderflow but usable OHLC/volume available → `OHLC`;
- neither available → `NONE`.

If `ORDERFLOW` is explicitly requested and unavailable, the mapper must not silently downgrade to `OHLC`.

If `OHLC` is explicitly requested but required volume data is unavailable, the mapper must not fabricate volume values.

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

OHLC-derived directional volume is marked as `OHLC`; genuine orderflow data is marked as `ORDERFLOW`.

## D6. POI JSON representation

Each canonical POI may contain:

```json
"volume": {
  "method": "OHLC",
  "formation": {
    "total": "...",
    "buy": "...",
    "sell": "...",
    "delta": "...",
    "delta_ratio": "..."
  },
  "causal_displacement": {
    "total": "...",
    "buy": "...",
    "sell": "...",
    "delta": "...",
    "delta_ratio": "..."
  },
  "aggregate": {
    "total": "...",
    "buy": "...",
    "sell": "...",
    "delta": "...",
    "delta_ratio": "..."
  },
  "probability": null
}
```

When method = NONE, the volume/delta analytics block is not processed and no volume-derived values or POI likelihood are calculated. Otherwise, values are null/omitted only when the relevant provenance data is unavailable.

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
