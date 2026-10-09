# SMC Mapper Specification

**Status:** Current implementation specification.
**Scope:** Functional and implementation specification for the future `smc_mapper.py`.
**Canonical authority:** `.agents/skills/smc/` remains the sole authority for canonical SMC semantics. This document does not redefine those rules.

---

# 0. SCOPE, AUTHORITY, AND RUNTIME BOUNDARIES

## 0.1 Active product runtime components

The intended finished product uses these active Python runtime components:

- `market_data.py` — standalone Market Data CLI: provider access, normalization, completion handling, deterministic range retrieval, incremental update, bounded retention, completed-candle persistence, current-candle snapshot refresh, and persistence to `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json`.
- `smc_mapper.py` — canonical SMC mapper: structural analysis, HTF/LTF processing, and persistent structural state in `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_structures.json`.
- `smc_monitor.py` — interactive runtime: scheduling, user interaction, runtime/target monitoring, alerts, and orchestration of Market Data CLI and mapper execution across multiple symbols and multiple stored analyses per symbol.

The older `smc_htf_ltf_monitor.py`, `smc_analyzer.py`, and Layer-1-to-Layer-6 `*_engine.py` implementation artifacts are not components of the finished product architecture.

These legacy artifacts are optional source material only. Reusable implementation patterns, algorithms, tests, or utility code may be extracted into the finished product when they are compatible with this specification and the canonical skill. The finished product must not retain a runtime, import, schema, or behavioral dependency on any legacy artifact.

This specification defines the mapper contract and its boundaries with the standalone Market Data CLI and interactive monitor.

## 0.2 Implementation ownership boundaries

The mapper has no direct connection to any concrete market-data provider and has no runtime import dependency on `market_data.py`.

`market_data.py` is a standalone Market Data CLI process. It owns provider access, provider abstraction, normalization, completion handling, timestamp normalization, availability detection, deterministic range retrieval, incremental updates, retention and persistence to `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json`.

The Market Data process boundary is the standalone `market_data.py` executable and its machine-readable STDOUT candle protocol.

The normal data flow is:

```text
Provider(s)
    |
    v
market_data.py (CLI)
    |
    +----> internal persistence/cache
    |
    +----> machine STDOUT (CSV-like candle stream)
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

The machine-readable candle stream is the Mapper's market-data portability boundary. The Mapper must not know whether the Market Data process obtained data from LSE, a future MT4/MT5 adapter, a broker, replay data, cache, or another provider.

The persisted market-data JSON is an internal Market Data storage format. It is not the Mapper process-input contract and must not be opened, parsed, or depended on by the Mapper.

The Mapper must never call a concrete provider, perform provider-specific API requests, depend on provider-specific response formats, request market data from the monitor, or import `market_data.py` as a Python data API.

V1 implements the process boundary with Python `market_data.py`. Future platform implementations may provide the same machine-readable candle contract without changing Mapper/SMC logic. MT4/MT5 are portability targets only; no MT4/MT5 implementation is part of V1.

## 0.3 Time-domain contract

The Mapper operates on canonical UTC only.

The Market Data process supplies:

- `timestamp` — canonical UTC candle interval-start timestamp;
- OHLC values;
- optional primitive volume fields from the machine protocol;
- `completed` — process-protocol completion state.

Datasource-native timestamps are not canonical Mapper input.

Local time is a transient presentation/runtime value derived from canonical UTC with an explicit IANA timezone. It may be used for human-readable diagnostics or for converting explicitly identified user-local input before the Mapper contract is invoked.

Local time must never change:

- candle ordering;
- completion eligibility;
- analysis identity;
- Dealing Range timestamps;
- mapper checkpoints;
- canonical SMC calculations.

All Mapper start/end boundaries must resolve to canonical UTC before analysis identity generation, effective-window selection, checkpoint comparison, or candle eligibility.

The analysis key must use the resolved canonical UTC boundary, not the original local-time spelling.

At the Mapper contract boundary, datetime input must be timezone-aware ISO-8601 and date-only input is accepted only as the deterministic UTC calendar-date shorthand defined in §§2.7–2.8. Explicit local-time input must be converted to canonical UTC before the Mapper contract is invoked.

## 0.4 Symbol data-directory and process input

Durable outputs for one symbol remain under one directory beneath the common data root:

```text
<DATA_ROOT>/
└── <SYMBOL>/
    ├── <SYMBOL>_marketdata.json
    └── <SYMBOL>_structures.json
```

Market Data owns creation and maintenance of `<SYMBOL>_marketdata.json`. Mapper owns `<SYMBOL>_structures.json`.

Mapper market-data input is obtained by launching the standalone Market Data process with the required symbol/timeframe/range parameters and reading its machine-readable STDOUT. The Mapper does not discover or open the Market Data persistence file.

### Process boundary

```text
Mapper
    |
    | launches market_data.py
    | reads machine STDOUT
    v
CSV-like completed-candle stream
```

Rules:

- Mapper consumes machine STDOUT only;
- Market Data diagnostics and errors are emitted on STDERR and are never treated as candle data;
- Mapper must fail the data acquisition operation if the machine protocol is malformed;
- Mapper must not fall back to reading the Market Data JSON file;
- `--cleartext` must never be used by Mapper;
- the process contract is independent of the internal Python module layout;
- the candle protocol uses only simple cross-language values and is intentionally suitable for a future MQL4/MQL5 implementation;
- symbol-directory persistence remains an internal Market Data concern.

The symbol directory is still the common durable storage location for Market Data and Mapper outputs, but the Mapper does not use the Market Data JSON file as its runtime input.

# 1. EXTERNAL MARKET-DATA CONTRACT

## 1.1 Market Data process boundary

The standalone Market Data CLI receives provider-specific market data, converts it into the provider-independent completed-candle representation, and emits the requested completed candles through the machine-readable STDOUT protocol defined by `market_data_specification.md`.

```text
Provider-specific data
        |
        v
market_data.py
 acquisition / normalization / persistence
        |
        +-----> internal <SYMBOL>_marketdata.json
        |
        +-----> machine STDOUT
                    |
                    +-----> smc_mapper.py
                    +-----> other compatible consumers
```

Canonical SMC logic consumes only completed candles from the machine-readable normalized candle stream. The Mapper must reject `completed=0` records for structural analysis.

Provider-specific API access, transport, retry, pagination, authentication, timestamp parsing, completion detection, and raw-field mapping belong to Market Data.

The detailed internal structure, interfaces, function names, variable naming, implementation order, test boundaries, and extension points for `market_data.py` are defined in `market_data_specification.md`. This file defines the Mapper-facing contract; it does not define Market Data internal Python APIs.

The machine protocol is the stable external boundary. Internal JSON schema, Python dataclasses, provider classes, and service functions may change without requiring Mapper changes, provided the external protocol remains compatible.

## 1.2 Persisted market-data store

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

Completed candles are stored in candles[]. They are the only market-data records eligible for canonical Mapper processing and are emitted through the machine protocol when requested. The optional current field stores only the latest in-progress candle snapshot for that timeframe and is never canonical structural input.

A current snapshot may be refreshed while the candle is forming. It may contain the provider-available OHLC and total volume for that in-progress interval. It must never be copied into candles[] until the interval is confirmed completed.

Market-data retention is a bounded rolling operational policy applied independently to each timeframe. Its capacity is a market-data implementation/storage setting, not a canonical SMC parameter.

If an analysis requires candles outside the retained window, the Market Data CLI reacquires that missing range and merges it into the corresponding timeframe before mapper processing.

Each timeframe section is independently created, extended, deduplicated by canonical candle identity, chronologically ordered, and retention-managed. Updating one timeframe must not alter another timeframe's completed candle series or current snapshot.

The available_start and available_end fields refer only to the persisted completed-candle series, not to the current snapshot.

## 1.2.1 Machine protocol field semantics

The machine protocol header is:

    timeframe,time,open,high,low,close,tick_volume,spread,real_volume,completed

The Mapper parses the CSV stream without importing Market Data Python classes.

`time` is the canonical UTC interval-start epoch. `completed` is `1` only for a completed candle and `0` only for a current/in-progress snapshot.

The protocol does not redundantly transmit `completion_time`. The Mapper deterministically derives the canonical completion boundary from `timeframe + timestamp` using the canonical timeframe rules defined by the Market Data contract. This derived boundary is used for explicit end-time eligibility.

`tick_volume`, `spread`, and `real_volume` are independent optional fields. Empty fields mean unavailable; the Mapper must not infer one from another or from Market Data's internal `volume.total`.

The Mapper must reject malformed required fields, invalid timestamps, malformed OHLC, duplicate candle identities, non-ascending timestamps within a timeframe, and any record with `completed=0` for structural processing.

## 1.3 Normalized candle representation

The Mapper's external candle view is the machine-protocol record, not the Market Data persistence model. It contains the required OHLC fields plus the optional `tick_volume`, `spread`, and `real_volume` fields defined by the process contract.

The Mapper derives the canonical completion boundary from `timestamp + timeframe`; `completion_time` is therefore a derived analysis value and is not part of the wire record.

The optional volume fields are availability signals. Empty fields remain unavailable; the Mapper must not fabricate, rename, or infer one optional field from another.

The Market Data persistence branches `volume.total`, `volume.ohlc`, and `volume.orderflow` are not Mapper process-input fields. POI volume enrichment may run only when the required volume evidence is actually available through the process contract. Otherwise the result is the defined no-supported-volume-path case.

The Mapper reads canonical structural input only from records marked `completed=1`. A current/in-progress record is never part of canonical structural processing.

## 1.4 Candle identity

`candle_id` must be deterministic and stable across repeated downloads of the same candle.

It must be derived from stable candle identity information rather than from an in-memory array index.

The candle index must never be used as permanent candle identity.

The exact identifier format remains an implementation detail.

---

## 1.5 Timestamp, ordering, and completion

All normalized timestamps must be represented consistently in UTC.

Provider-specific timezone information must be normalized before canonical analysis.

Provider timezone details must not leak into canonical SMC calculations.

---

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

Only completed candles may enter canonical analysis.

A candle is considered completed only after its canonical timeframe interval has closed and the normalized provider/completion contract confirms that closure. Every persisted normalized candle carries a UTC `completion_time` representing that canonical interval-close boundary. The mapper uses `completion_time` for explicit end-time eligibility; timestamp alone is not sufficient evidence of completion.

The mapper must use the candle's canonical completion boundary when deciding whether it is eligible for an explicit analysis end time. The candle timestamp is not by itself sufficient evidence of completion.

An incomplete/current candle must be excluded from the canonical analysis series. It may be stored only in the per-timeframe current snapshot of <SYMBOL>_marketdata.json and must never be consumed as canonical structural input.

The current snapshot is runtime market-data state, not historical candle state. Refreshing it must not alter structural history or mapper checkpoints.

## 1.6 Numeric and OHLC integrity

OHLC values must use a deterministic financial numeric representation.

The canonical implementation must use `Decimal`, not binary floating-point values, for normalized OHLC prices.

Invalid values include:

- NaN;
- Infinity;
- non-numeric values;
- silently coerced invalid numeric values.

The same deterministic numeric policy applies to normalized volume values when present. Total, buy, sell, and delta volume values must use Decimal-compatible deterministic numeric representation, be finite, and must not be silently coerced or fabricated.

---

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

## 1.7 Data gaps and series integrity

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

Every normalized candle series belongs to exactly one timeframe.

A candle from one timeframe must never be silently mixed with another timeframe.

For a two-timeframe analysis:

```
HTF candle series
LTF candle series
```

remain distinct series.

---

A normalized candle series belongs to exactly one symbol for a mapper execution.

Data from different symbols must never be merged into the same canonical candle series.

---

Provider-specific concepts must be normalized before the canonical engine receives the data.

Examples include:

- provider-specific timestamp formats;
- provider-specific field names;
- provider-specific completion flags;
- provider-specific numeric representations;
- provider-specific timezone conventions.

The canonical engine must not contain provider-specific conversion logic.

---

## 1.8 Data availability and reacquisition

`market_data.py` persists the actual available temporal range of each timeframe in `<SYMBOL>_marketdata.json`.

At minimum, each timeframe section tracks:

- `available_start`
- `available_end`

This is important because HTF and LTF may have different available history.

The mapper distinguishes requested analysis range from available/retained market-data range using the Market Data process response. It selects the required range from the corresponding `timeframe` records in the machine-output stream. The CSV-like candle representation consumed here is the external Market Data process contract; its wire-format owner is `market_data_specification.md`, not the mapper.

If the requested range is outside the retained market-data window, the monitor/orchestrator triggers Market Data CLI reacquisition before mapper processing.

If the requested range cannot be supplied, the mapper must represent the resulting data/context unavailability explicitly and must fail closed where a canonical decision depends on unavailable information.

The mapper does not access provider availability APIs directly.

The Market Data CLI must not discard candles from a requested acquisition range before persistence.

The launcher ensures that all required bootstrap/warm-up candles are acquired and persisted through the Market Data CLI, and the mapper then determines the effective analysis interval from the persisted data and requested start/end constraints.

Market-data retention may remove older candles according to the bounded timeframe retention policy. Such removal is storage policy only and does not rewrite mapper structural history.

If a later analysis requires removed candles, the Market Data CLI reacquires the missing range from the provider before that analysis is processed.

## 1.9 Candle metadata, determinism, failure, and volume retention

The canonical candle representation contains information required for candle-level structural processing.

Provider-specific metadata must not enter the canonical candle representation unless a canonical rule explicitly requires it.

---

---

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

Invalid provider data or normalization failure must not be silently ignored.

The mapper must report sufficient information to identify the affected symbol, timeframe and candle/time range.

The canonical engine must never receive malformed or ambiguous candle data.

---

When total traded volume is available from the provider, market_data.py preserves it as volume.total on the underlying normalized candle.

When genuine orderflow is available, it is preserved independently under volume.orderflow. When deterministic OHLC directional estimation is available, it may be preserved independently under volume.ohlc.

The mapper must preserve the applicable POI volume information when storing POI references to source candles. Parallel volume types must not overwrite one another.

Volume provenance is represented by the data branch that is actually present. A single exclusive volume source or volume method field is not required on the candle.

---

# 2. CLI AND INPUT RESOLUTION

## 2.1 Symbol

One required instrument per mapper execution.

One mapper execution analyzes one symbol.

---

## 2.2 HTF

Optional.

Exactly one timeframe may be supplied.

Example:

`--htf H4`

---

## 2.3 LTF

Optional.

Exactly one timeframe may be supplied.

Example:

`--ltf M15`

---

## 2.4 Timeframe relationship and analysis mode

The mapper uses exactly two analysis modes:

- `SINGLE_TIMEFRAME`
- `HTF_LTF`

The mapper determines the mode from the supplied timeframe parameters.

### Single-timeframe analysis

Use single-timeframe analysis when:

- only `--htf` is supplied;
- only `--ltf` is supplied; or
- both are supplied but they specify the **same timeframe**.

In single-timeframe analysis, the selected timeframe is analyzed once. The normalized identity is based only on the selected timeframe, so `--htf H1`, `--ltf H1`, and `--htf H1 --ltf H1` address the same single-timeframe analysis identity when the analysis boundary is the same.

Internally, the analysis may represent:

`HTF = LTF = selected timeframe`

but this does **not** activate HTF pullback validation.

### Two-timeframe analysis

Use two-timeframe analysis only when both are supplied and they are different:

`HTF > LTF`

An invalid relationship is an input error.

The mapper must never silently swap or otherwise correct the supplied timeframes.

---

## 2.5 Entry timeframe

The entry timeframe is the driving timeframe for incremental processing and runtime scheduling.

- Single-timeframe analysis: the selected timeframe is the entry timeframe.
- Two-timeframe analysis: the LTF is the entry timeframe.

The entry timeframe determines `last_processed_candle_time`, incremental market-data acquisition, mapper processing boundaries, and monitor update scheduling. HTF remains the higher-context timeframe and is processed as required to provide point-in-time context for the entry timeframe.

---

## 2.6 HTF pullback validation

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

## 2.7 Start-time resolution

`--starttime` is optional.

When supplied, it defines the requested start of the analysis window and selects the analysis identity associated with that normalized boundary.

Accepted forms:

- timezone-aware ISO-8601 datetime; or
- ISO calendar date, normalized deterministically to `00:00:00Z`.

Examples:

`--starttime 2026-09-01` → `2026-09-01T00:00:00Z`

`--starttime 2026-09-01T09:30:00+02:00` → canonical UTC before identity generation.

Date-only input is a UTC calendar-date shorthand, not local time.

When `--starttime` is omitted:

- if exactly one existing analysis matches the supplied timeframe configuration, the mapper resumes that analysis from its persisted `last_processed_candle_time`;
- if multiple existing analyses match the supplied timeframe configuration but have different analysis start boundaries, the request is ambiguous and must fail explicitly; `--starttime` is required to select one;
- if no existing analysis matches the supplied timeframe configuration, the mapper creates a new analysis using the earliest available completed entry-timeframe candle returned by the Market Data process for the requested bootstrap range as its persisted initial analysis boundary. This boundary comes from actual market data and is not invented.

For an existing analysis, the next eligible completed entry-timeframe candle after `last_processed_candle_time` is the incremental processing start.

For a newly created analysis without `--starttime`, the mapper performs the required bootstrap/warm-up from the persisted available history beginning at the selected initial analysis boundary.

The resume path is specifically intended to support restarting the program after a previous shutdown.

The mapper must distinguish the explicitly requested `requested_start`, when supplied, from the persisted analysis boundary and the computed `effective_start`.

If required historical data is outside the retained market-data window, the Market Data CLI reacquires the missing range before mapper processing.

Missing historical data must never be fabricated.

## 2.8 End-time resolution

`--endtime` is optional.

Accepted forms:

- timezone-aware ISO-8601 datetime; or
- ISO calendar date, normalized deterministically to the end of that UTC calendar day.

Examples:

`--endtime 2026-09-29` → `2026-09-29T23:59:59.999999Z`

`--endtime 2026-09-29T15:30:00+02:00` → canonical UTC before candle eligibility.

Date-only input is a UTC calendar-date shorthand, not local time.

If omitted, use the latest completed entry-timeframe candle returned by the Market Data process after the required update.

If supplied, use the latest completed candle returned by the Market Data process whose canonical completion boundary is less than or equal to the requested end time.

For an existing analysis resumed from `last_processed_candle_time`, an end-time earlier than that checkpoint is an invalid incremental request. The mapper must fail explicitly rather than process the analysis backwards or silently create a second identity.

When an explicit end-time limits processing, the persisted checkpoint must never advance beyond the resolved end-time boundary.

The normalized candle `timestamp` alone must not be treated as proof that a candle has completed. Completion is determined by the normalized completion status/time contract in §1.5.

An incomplete/current candle must never enter canonical analysis.

## 2.9 Input validation

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

Provider-specific availability checks, provider/API failures, and acquisition errors belong to the Market Data CLI process. The mapper sees only the normalized machine-output result after the Market Data process has completed the required acquisition/update request.

Invalid mapper configuration or normalized candle data must fail explicitly.

## 2.10 Configuration boundary

No separate mapper configuration file is required.

Mapper behavior is controlled by CLI parameters, explicit defaults, Market Data machine-output metadata and candle records, and the canonical SMC skill.

Market-data provider configuration belongs to the Market Data CLI and is not a mapper semantic dependency.

`market_data.py` provides the CLI interface for market-data acquisition, normalization, incremental update, retention and persistence into `<SYMBOL>_marketdata.json` and machine-output through STDOUT. It is a separate process.

No mapper configuration file is to be introduced for timeframe selection, history retention or analysis window.

Timeframe selection is controlled only by `--htf` and/or `--ltf` according to the timeframe-relationship and synchronization contracts in this specification. The supported-timeframe catalog and timeframe-duration ownership remain with the Market Data contract; the mapper must not introduce a second hard-coded `SUPPORTED_TIMEFRAMES` list. The mapper may validate timeframe syntax and HTF/LTF duration ordering, then fail with explicit data-availability/error status when the requested timeframe is not present in the Market Data machine-output response.

Volume analysis is controlled by the optional mapper CLI parameter:

```
--volume-method {NONE,OHLC,ORDERFLOW,BOTH}
```

When the parameter is omitted, the default is BOTH.

BOTH uses both available genuine orderflow analytics and OHLC-derived directional volume analytics in parallel. The two evidence branches remain separate and are never combined into a single volume value. If only one branch is available, that branch is used. If neither branch is available, no POI volume analytics are produced.

The selected method is an analysis-time processing decision. It is not persisted as a single exclusive volume provenance field in normalized market-data candles, and it does not remove or overwrite any parallel volume data that is available. Explicit CLI values override the default.

## 2.11 CLI and --help contracts

Every CLI option defined by this specification is a real implementation contract. Each documented option must be parsed, validated, functionally applied, and documented by the corresponding English --help output. Documentation-only, placeholder, or future CLI options are not permitted.

--help must work without other required arguments, print the English option descriptions, and exit successfully.

### smc_mapper.py

```text
Usage:
  python smc_mapper.py --symbol SYMBOL [--htf TF] [--ltf TF]
                       [--starttime TIME_BOUNDARY] [--endtime TIME_BOUNDARY]
                       [--history-no N]
                       [--volume-method {NONE,OHLC,ORDERFLOW,BOTH}]
                       [--debug]
                       [--help]

Options:
  --symbol SYMBOL
      Required instrument symbol.

  --htf TF
      Optional Higher Timeframe. With --ltf, HTF must be strictly higher.

  --ltf TF
      Optional Lower/selected timeframe. With --htf, this is the entry timeframe.
      At least one of --htf or --ltf must be supplied.

  --starttime ISO8601
      Optional analysis start boundary. When supplied, it selects the analysis
      identity associated with that boundary.

  --endtime ISO8601
      Optional analysis end boundary. The latest completed candle whose
      completion_time is <= this value is used.

  --history-no N
      Optional symbol-level closed Dealing Range history capacity. N must be >= 1.
      Default when initializing a symbol structure file is 5000; an existing
      stored value is preserved.

  --volume-method {NONE,OHLC,ORDERFLOW,BOTH}
      POI volume analytics method. Default: BOTH.
      NONE disables volume analytics.
      OHLC uses OHLC-derived directional volume estimates.
      ORDERFLOW uses genuine orderflow only.
      BOTH uses both available branches independently.

  --debug
      Enable diagnostic output on stderr.

  --help
      Show this help message and exit.
```

The Market Data and Monitor CLIs are specified only in their owner documents:

- `market_data.py` → `specifications/market_data_specification.md` §0.4 and §5
- `smc_monitor.py` → `specifications/smc_monitor_specification.md` §1

The Mapper must not duplicate those CLI contracts here.
The monitor does not accept --htf or --ltf; it monitors the analyses already persisted in each symbol's structures JSON. Timeframe analysis configuration remains owned by smc_mapper.py.

CLI options are independent of canonical SMC semantic authority. Invalid option combinations must fail explicitly rather than being silently corrected.

---

# 3. ANALYSIS IDENTITY AND PERSISTENT STATE MODEL

## 3.1 Analysis identity and structures JSON

`<DATA_ROOT>/<SYMBOL>/<SYMBOL>_structures.json` is the canonical mapper structural-state file for that symbol.

It contains all distinct mapper analyses for the symbol in one file. Each analysis is identified by a deterministic analysis key derived from its normalized timeframe configuration and persisted `analysis_start` boundary.

Examples:

```text
H4_M15_2026-06-10T12:00:00Z
H1_M5_2026-07-01T09:00:00Z
M15_2026-06-10T12:00:00Z
```

The persisted `analysis_start` is required and is the stable boundary used by the analysis identity.

Persisted timeframe fields use this normalized shape:
- `SINGLE_TIMEFRAME`: `entry_timeframe` is the selected timeframe; `htf` and `ltf` preserve supplied timeframe values or null when omitted.
- `HTF_LTF`: both `htf` and `ltf` are present and `htf > ltf`; `entry_timeframe = ltf`.

When `--starttime` is supplied, `analysis_start` equals the normalized requested start boundary.
- When `--starttime` is omitted for a new analysis, `analysis_start` equals the earliest available completed entry-timeframe candle completion boundary selected by §2.7.
- `requested_start` records the explicitly supplied boundary and may be null/absent for analyses created without `--starttime`.
- `effective_start` is an execution-window value and is not part of analysis identity. It need not be persisted in V1.

When `--starttime` is omitted, an existing analysis is selected by timeframe configuration only when that selection is unambiguous. If multiple analysis keys share the same timeframe configuration, `--starttime` is required.

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
      "canonical_pois": [],
      "history": []
    }
  }
}
```

`history_no` is stored once at symbol level and applies independently to each analysis's applicable closed Dealing Range history.

A Market Data CLI execution updates only its internal `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json` and emits the requested machine-output stream. A mapper execution updates only its relevant analysis entry inside `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_structures.json`.

Downstream consumers identify each stored analysis from its deterministic analysis key and validate the stored `analysis_mode`, `htf`, `ltf`, `entry_timeframe`, and required `analysis_start`. `requested_start` is provenance metadata and may be null/absent for an analysis created without an explicit `--starttime`.

## 3.2 Stored mapper state

Each mapper analysis entry stores canonical structural analysis plus the minimal mapper-processing metadata required for deterministic incremental execution.

It may contain Layer-3 structural lifecycle/state, CONFIRMED_STRUCTURAL_SWING, Protected Structural Extreme, Dealing Range state, IDM state/provenance (MINOR_IDM / MAJOR_IDM), retracement qualification, STRUCTURAL_SWING_BREAK / VALID_BOS, CHoCH lifecycle state, canonical Layer-6 POI results, canonical POI registry, retained closed Dealing Range history, and structural provenance/change metadata.

The mapper must not persist dynamic monitoring or trade state such as current market price, active trade/order state, stop state, break-even state, trailing state, target-hit state, or the monitor's transient POI selection state. Those are owned by the monitor.

Each analysis entry contains its own `last_processed_candle_time` as mapper processing provenance/checkpoint metadata. It carries no canonical SMC meaning.

---

# 4. DATA COVERAGE, BOOTSTRAP, AND RESUME PLANNING

## 4.1 Independent HTF/LTF feed ranges

HTF and LTF candle data may cover different temporal ranges.

The Market Data CLI owns acquisition and determines the actual available/returned range for each requested timeframe. The Mapper obtains that range only from the validated Market Data machine-output response and must not fabricate unavailable candles.

Example:

- HTF data: 2026-06-01 -> 2026-09-29
- LTF data: 2026-01-01 -> 2026-09-29

The longer LTF history must not be truncated merely because the HTF history is shorter.

The absence of HTF data before its available start does not imply that HTF structure did not exist.

Availability is determined from the Market Data process response and exit status. If the required range cannot be satisfied, the mapper must represent the resulting data/context unavailability explicitly and fail closed where canonical rules require unavailable context.

The mapper does not perform provider-specific acquisition.

## 4.2 Missing HTF context

When an LTF canonical rule requires HTF pullback validation but the required HTF historical context is unavailable, represent the condition explicitly as:

`HTF_CONTEXT_UNAVAILABLE`

Do not convert it to:

`HTF_VALID_PULLBACK = FALSE`

Therefore:

`HTF_CONTEXT_UNAVAILABLE != HTF_VALID_PULLBACK_FALSE`

If a canonical decision depends on unavailable HTF context, the decision must remain unresolved / fail closed.

---

## 4.3 Bootstrap and warm-up

The mapper constructs structural state by processing normalized candle ranges received from the Market Data process.

For an initial build, or whenever a complete bootstrap is explicitly required:

earliest required effective candle -> latest completed entry-timeframe candle

The mapper must not use a latest-window shortcut that bypasses required structural bootstrap.

The launcher invokes the Market Data CLI for the required bootstrap range in deterministic batch form. The mapper then consumes the machine-readable STDOUT stream for that request.

For incremental execution after a valid persisted checkpoint, the monitor/orchestrator invokes the Market Data CLI for only the subsequently completed entry-timeframe range after the checkpoint, in chronological order, updates internal Market Data persistence and then invokes the mapper against the resulting machine-output range as defined by §10.1.

The mapper does not obtain market data from the monitor and does not access a concrete provider.

### Two-timeframe LTF bootstrap

In two-timeframe analysis, the mapper establishes an LTF bootstrap coverage reference from the applicable HTF canonical structural context.

When a confirmed HTF Dealing Range exists, the applicable HTF Protected Structural Extreme is the preferred LTF bootstrap coverage reference. This reference determines the minimum historical LTF coverage needed for deterministic structural buildup. It is a data-coverage/reference point only; it is not an LTF structural start and does not create or promote any LTF structure.

When LTF bootstrap is required, the monitor/orchestrator invokes the Market Data CLI once for one deterministic LTF range covering the anchor through the activation/current boundary, subject to any additional LTF warm-up required by the canonical LTF rules, updates internal Market Data persistence and then invokes the mapper against the returned machine-output range.

If the requested LTF coverage begins later than the anchor because the source has no completed LTF data at or after the requested anchor, the mapper uses the first actually available completed LTF candle after the reference as the effective LTF bootstrap start. No attempt is made by the mapper to access the provider directly.

If the supplied LTF data begins before the HTF reference, that earlier data may be retained and used as additional canonical LTF warm-up when required; the HTF Protected Structural Extreme remains the context/coverage reference.

If the applicable confirmed HTF Protected Structural Extreme does not exist, the mapper does not fabricate one. The LTF bootstrap then follows the supplied LTF history subject to the canonical genesis/source-gap boundaries.

The LTF bootstrap reference is not an LTF structural-start ontology. The first LTF structural object is determined only by the canonical LTF rules.

---

# 5. MAPPER EXECUTION PIPELINE

## 5.1 Mapper execution pipeline

The mapper executes the following dependency-ordered pipeline for every analysis invocation:

1. Validate CLI inputs and the normalized market-data contract.
2. Resolve the analysis mode, entry timeframe, requested/effective analysis boundaries, and deterministic analysis identity.
3. Load the matching persisted analysis state, or create the required initial state.
4. Verify the required market-data coverage returned by the Market Data process and determine whether bootstrap, warm-up, or incremental processing is required.
5. Process completed candles only, in chronological order, using the canonical SMC skill as the sole semantic authority.
6. In single-timeframe mode, evaluate the selected timeframe without HTF pullback validation.
7. In two-timeframe mode, establish and maintain point-in-time HTF context and evaluate LTF candles only against HTF facts already canonical at the LTF evaluation time.
8. Reconcile canonical structural lifecycle, Dealing Range state/history, and canonical POI state according to the skill-owned semantics.
9. Enrich already-canonical POIs with optional non-canonical volume analytics when requested and available.
10. Persist the updated mapper analysis atomically and advance the mapper checkpoint only after successful persistence.

The mapper must never use a later event, incomplete candle, analytical volume result, storage-retention event, or downstream monitor state to retroactively redefine canonical structure.

## 5.2 Canonical semantic ownership

The exact SMC rules are implemented according to `.agents/skills/smc/`. This specification defines orchestration, data contracts, state boundaries, persistence, and downstream interfaces only.

The mapper must consume canonical outcomes from the applicable skill layers rather than reproduce their rules in the specification or invent alternative semantic gates.

Canonical ownership remains:

- structural and retracement/IDM rules: canonical skill Layer 3;
- BOS rules and required upstream gates: canonical skill Layer 4;
- CHoCH and LTF Structural Glitch routes: canonical skill Layer 5;
- canonical POI/Rule-of-Two semantics and lifecycle: canonical skill Layer 6;
- downstream risk/target policy: canonical downstream Layer 7 boundary;
- implementation/state and observability contracts: canonical downstream Layer 8 boundary where applicable.

No mapper-level section may redefine those semantic rules.

## 5.3 Processing-order invariants

The mapper must consume the Layer-3 `MAJOR_RETRACEMENT_QUALIFIED` result for continuation BOS. The canonical source corpus does not define the first-BOS measurement baseline; the project therefore resolves this source gap with the isolated `BOOTSTRAP_ORIGIN_ANCHOR` policy defined by the canonical skill.

The bootstrap contract is:

- `BOOTSTRAP_ORIGIN_ANCHOR` is a temporary initialization measurement anchor derived from an actual completed candle;
- chart inception uses the first effective completed candle as `C0`, the deterministic **mapping-origin candle**. `C0` is the causal start of the mapping state machine because no earlier candle belongs to that mapping domain;
- after `CHoCH_CONFIRMED`, an explicit active-impulse origin candle is required; missing origin provenance fails closed;
- `IDM_TAKEN` creates the active swing-point candidate / provisional structural extreme;
- the transient `BOOTSTRAP_RANGE` is activated from the `BOOTSTRAP_ORIGIN_ANCHOR` to the swing candidate so that macro retracement qualification has a deterministic measurement baseline; macro qualification then promotes the candidate to `CONFIRMED_STRUCTURAL_SWING`;
- `BOOTSTRAP_RANGE` activation occurs at swing-candidate establishment; the candidate source candle identifies the provisional extreme, while macro qualification is the later promotion gate;
- initial mapping boot begins at `C0` and all higher-layer state is constructed strictly forward, bar-by-bar;
- `BOOTSTRAP_RANGE` is measurement-only and is not a governing Dealing Range, Protected Structural Extreme, Trading Range boundary, or CHoCH boundary;
- bootstrap uses the existing Layer-3 50% / documented 38.2% qualification rules without introducing a new threshold or heuristic;
- `dynamic_retracement_extreme` is the live corrective state and remains mutable until the physical structural break;
- the first `VALID_BOS` locks the **pre-break** `dynamic_retracement_extreme` as the first `PROTECTED_STRUCTURAL_EXTREME`;
- the break/BOS candle is excluded from the pre-BOS retracement-extreme calculation under the aggregate OHLC observability contract;
- after lock, bootstrap state is destroyed and the first canonical Dealing Range is established;
- no bootstrap, dynamic, or structural state may be fabricated when required provenance is unavailable;
- chart inception uses `C0` as the deterministic mapping-origin candle;
- initial bootstrap direction is project-canonically resolved from `C0` body direction: close > open = bullish, close < open = bearish; a doji `C0` leaves direction unresolved until the first subsequent completed non-doji candle;
- once resolved, `BOOTSTRAP_ORIGIN_ANCHOR` is derived from the original `C0` in that direction;
- `ACTIVE_FIRST_BOS_BOOTSTRAP` remains active across `BOOTSTRAP`, `CONFIRMATION_LOCKED`, and post-CHoCH first-BOS processing until the current regime's first `VALID_BOS`;
- while `ACTIVE_FIRST_BOS_BOOTSTRAP` is active, physical penetration of `BOOTSTRAP_ORIGIN_ANCHOR` is handled before normal BOS/CHoCH classification by `BOOTSTRAP_ANCHOR_BREAK → BOOTSTRAP_REVERSAL`;
- the reversal retires the complete active pre-reversal bootstrap lineage, including provisional/confirmed swing, qualification, dynamic corrective state, active IDM/reference, and transient bootstrap range;
- the actual trigger candle becomes the new explicit active-impulse origin and seeds the new direction-consistent bootstrap anchor; processing resumes strictly forward from that real candle;
- the original `C0` remains the mapping-origin and is never redefined or replayed;
- bootstrap reversal cannot emit `VALID_BOS`, `CHoCH_CONFIRMED`, `MAJOR_IDM_SWEEP`, `PROTECTED_STRUCTURAL_EXTREME`, or a governing Dealing Range.
- when first-BOS processing spans mapper invocations, required bootstrap/process state must be persisted or deterministically reconstructible from the same persisted canonical candle history; resume must not alter the bootstrap anchor or the pre-break dynamic observation boundary.

The mapper's canonical processing boundary is the completion of each eligible completed candle within the resolved analysis interval.

For every processed candle:

- all required upstream canonical state is resolved before downstream state consumes it;
- a canonical decision is evaluated only from information point-in-time available at that candle's evaluation time;
- downstream analytical enrichment cannot mutate canonical structural truth;
- persistence metadata such as `last_processed_candle_time` carries implementation provenance only and has no canonical SMC meaning.

A successful invocation persists the resulting state before the checkpoint is advanced. A failed or unresolved canonical dependency must not be converted into a successful structural state.

---

# 6. SYNCHRONIZED HTF/LTF CONTEXT

## 6.1 Independent timeframe semantics

Each timeframe is analyzed according to its own canonical structural rules.

In two-timeframe mode, HTF and LTF remain separate canonical analyses while sharing a synchronized execution timeline.

The LTF is not a canonical child of the HTF and must not redefine or mutate HTF structure.

The HTF provides the execution context required by canonical LTF rules where such context is explicitly specified.

In single-timeframe mode, no HTF/LTF execution relationship exists.

## 6.2 Synchronized point-in-time processing

When an HTF and LTF are both supplied:

1. the monitor/orchestrator requests the required HTF range from Market Data; the mapper consumes that returned range and establishes the current HTF canonical structural context first;
2. the mapper determines the applicable HTF execution context and any LTF bootstrap/activation requirement;
3. the monitor/orchestrator requests the LTF range required by the applicable analysis state from Market Data; the mapper consumes that returned range;
4. HTF and LTF candles are processed chronologically on the shared time axis;
5. each LTF candle is evaluated using only HTF canonical context that already exists at that LTF evaluation time;
6. a later HTF event must never reinterpret an earlier LTF event.

The LTF exists to refine and qualify entry within the applicable HTF context; it does not create a competing higher-level narrative.

The existence of HTF context must not automatically invalidate an LTF structural event. Only canonical rules that explicitly require HTF context may use it as a qualification, activation, or routing condition.

HTF/LTF synchronization is an orchestration relationship around persisted normalized market-data ranges; it does not transfer semantic ownership from HTF rules to LTF rules.

## 6.3 Point-in-time HTF context

For every LTF evaluation that requires HTF information, only HTF structural facts that already existed at that evaluation time may be used.

For each consumed HTF structural fact:

"formation_time <= LTF evaluation_time"

A later HTF structural event must never be used to reinterpret an earlier LTF event.

The applicable HTF Dealing Range and the canonical HTF structural facts available at that point in time provide the LTF context reference.

## 6.4 LTF records within HTF context

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

## 6.5 Canonical HTF-interaction routes

Where a canonical LTF route explicitly requires HTF interaction, the mapper consumes the applicable HTF context from its structural state and requests/consumes any required additional LTF analysis range from the Market Data process; the monitor/orchestrator ensures that request is executed before mapper processing.

This includes the canonical LTF Structural Glitch / CHoCH route after HTF POI interaction or HTF core-liquidity takeout, as defined by `05_CHOCH_mechanics.md`.

The mapper must align the persisted candle range with the applicable point-in-time HTF context but must not invent a new CHoCH, BOS, IDM, POI, or entry rule.

## 6.6 Historical independence

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

## 6.7 Canonical ownership boundary

HTF canonical semantics remain owned by the HTF analysis and its canonical skill layers.

LTF canonical semantics remain owned by the LTF analysis and its canonical skill layers.

The mapper defines only the orchestration and storage relationship between them.

It must not introduce a general HTF-parent/LTF-child semantic ontology.

---

---

# 7. DEALING-RANGE LIFECYCLE, HISTORY, AND RETENTION

## 7.1 Closed Dealing Range history

`history_no` is one collective symbol-level configuration value, stored once in `<SYMBOL>_structures.json`.

In two-timeframe mode, it applies independently to the HTF CLOSED DEALING RANGE history retained inside each distinct mapper analysis entry. The LTF does not have a separate `history_no`.

In single-timeframe analysis, it applies to the selected timeframe's CLOSED DEALING RANGE history for that analysis.

The history unit is the canonical closed Dealing Range. Only a Dealing Range that has been canonically closed may enter history. The currently open Dealing Range is never a history item.

Retention is newest-first by canonical `close_time`, with oldest-first (FIFO) eviction within each analysis when that analysis's retained history exceeds `history_no`.

Eviction is a storage-retention operation only. It does not invalidate canonical historical structure.

A repeated mapper execution must reconcile an existing range identity in place and must not create a duplicate history entry.

## 7.2 Dealing Range identity and retention configuration

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

- New symbol structures JSON + no `--history-no` -> initialize and persist `history_no = 5000`.
- New symbol structures JSON + `--history-no=N` -> initialize and persist `history_no = N`.
- Existing symbol structures JSON + no `--history-no` -> preserve the stored `history_no`.
- Existing symbol structures JSON + `--history-no=N` -> ignore the CLI value and preserve the stored `history_no`.
- If an existing symbol structures JSON lacks `history_no`, initialize and persist `5000`.
- `N` must be an integer >= 1 when supplied.

Changing `history_no` changes retention capacity only. It does not change canonical SMC semantics.

## 7.3 HTF Dealing Range history contract

Within each retained mapper analysis entry, each history element represents one CLOSED Dealing Range for that analysis and may contain canonical HTF structural state and, where two-timeframe analysis is active, any number of LTF structures interpreted in that HTF range context.

The LTF records stored under an HTF range are context-scoped execution analysis, not a new canonical parent/child ontology. LTF semantic ownership remains with the LTF canonical rules.

The history record may contain, where applicable:

- HTF structural direction/lifecycle state;
- HTF CONFIRMED_STRUCTURAL_SWING state/records;
- HTF Protected Structural Extreme state/records;
- HTF IDM provenance (MINOR_IDM / MAJOR_IDM);
- HTF retracement qualification;
- HTF VALID_BOS outcomes;
- HTF CHoCH lifecycle outcomes;
- canonical HTF Layer-6 POIs;
- associated LTF structural/entry-analysis records;
- volume metadata associated with canonical POIs.

There is no fixed maximum number of LTF structures within one HTF Dealing Range.

The history record must preserve canonical formation/provenance times of its contained objects.

History is not an append-only mapper execution log. It is retained canonical Dealing Range history for the specific mapper analysis.

## 7.4 Dealing Range lifecycle boundary

The mapper derives Dealing Range history boundaries strictly from the canonical structural lifecycle.

- A currently open Dealing Range is runtime state, not history.
- `VALID_BOS` is the canonical lifecycle event that establishes the next confirmed Dealing Range lifecycle; when a governing range already exists, it closes that previous range first. The first `VALID_BOS` establishes the first confirmed Dealing Range and therefore has no pre-existing governing range to close.
- The mapper must not close or start a Dealing Range because of a physical break, IDM sweep, CHoCH-eligible break, insufficient-retracement `IMPULSE_EXTENSION`, mapper execution boundary, or retention operation.
- Before the first canonical `VALID_BOS`, no governing Dealing Range is created from bootstrap state.
- The project-canonical `BOOTSTRAP_RANGE` is transient and exists only to apply the already-defined Layer-3 retracement qualification rules.
- `BOOTSTRAP_ORIGIN_ANCHOR` is never promoted into canonical protected structure.
- `dynamic_retracement_extreme` is the live corrective state; the lock candidate is the value observed immediately before the physical structural break.
- The break/BOS candle is excluded from that pre-BOS calculation under aggregate OHLC because intrabar order is not available from final OHLC alone.
- `VALID_BOS` destroys bootstrap state and locks the pre-break `dynamic_retracement_extreme` as the first canonical `PROTECTED_STRUCTURAL_EXTREME`.
- After lock, the dynamic state is inactive and the protected extreme is canonical.
- If required bootstrap origin provenance is unavailable, the mapper fails closed rather than fabricating historical data or structural truth.

---

# 8. CANONICAL POI REPRESENTATION

The mapper uses a unified storage representation for canonical POIs. It does not redefine the Layer 6 POI ontology or lifecycle.

Canonical POI semantic types remain owned by Layer 6 and are represented in mapper storage using the canonical semantic identifiers:

    ELIGIBLE_ORDER_FLOW
    VALIDATED_ORDER_BLOCK

Execution role is represented separately:

    DECISIONAL
    EXTREME
    ORIGIN_ORDER_BLOCK

ORIGIN_ORDER_BLOCK represents the canonical Origin Order Block latent reserve and is not an additional active Rule-of-Two slot.

The mapper must not use abbreviated or ambiguous POI type aliases.

The complete canonical OF/OB semantic family is:

    ORDER_FLOW_CANDIDATE
    ELIGIBLE_ORDER_FLOW
    DECISIONAL_ORDER_FLOW
    EXTREME_ORDER_FLOW

    ORDER_BLOCK_CANDIDATE
    VALIDATED_ORDER_BLOCK
    DECISIONAL_ORDER_BLOCK
    EXTREME_ORDER_BLOCK
    ORIGIN_ORDER_BLOCK

These identifiers distinguish object identity, qualification, execution role, and the latent range-origin Order Block reserve.

## 8.1 Mandatory IDM gate for active OF/OB POIs

The Mapper must enforce the canonical Layer-6 rule from `.agents/skills/smc/06_execution.md`: an active tradable Order Flow or Order Block POI cannot be designated or used to authorize an entry until a valid active IDM has formed and that applicable IDM has been physically taken out (`IDM_TAKEN`).

- OF/OB formations predating the applicable active IDM remain `SMT / INDUCEMENT_TRAP` observations for that active dealing-range lineage. A later IDM takeout must not retroactively promote them.
- OF/OB candidates formed after IDM formation but before its takeout may be retained as non-tradable candidates, but must not be emitted as active tradable POIs.
- After the applicable `IDM_TAKEN` event, post-IDM candidates may be evaluated against all remaining canonical OF/OB validity, mitigation, POI ontology, Rule-of-Two, and execution constraints.
- IDM takeout is necessary but not sufficient: it does not automatically validate a candidate, create an active POI, or authorize an entry.
- The Mapper must preserve candidate/validation records separately from active tradable POI records. If active IDM identity, formation, takeout event, or event-time provenance is unresolved, it must fail closed and emit no executable OF/OB POI or entry authorization.
- This is a consumption/implementation contract for the skill-owned rule; it must not create an alternate IDM or POI lifecycle.

Canonical POI lifecycle is consumed verbatim from Layer 6:

    POI_TOUCH
    POI_INTERACTION
    POI_MITIGATION
    POI_FAILURE
    POI_INVALIDATION

The mapper must not introduce another lifecycle enum, rename these states, merge them, or reinterpret them.

Dealing-Range rollover may additionally assign the Layer-6 historical disposition:

    EXPIRED_HISTORICAL

EXPIRED_HISTORICAL is a historical/reactive disposition after range rollover, not a replacement for the Layer-6 POI lifecycle enum.

Logical canonical POI representation:

```json
{
  "poi_id": "POI-001",
  "poi_type": "ELIGIBLE_ORDER_FLOW",
  "poi_role": "DECISIONAL",
  "lifecycle": "POI_INTERACTION",
  "provenance": {
    "start_time": "...",
    "end_time": "...",
    "source_candles": ["CANDLE-101", "CANDLE-102", "CANDLE-103"]
  }
}
```

---

# 9. POI VOLUME / DELTA ANALYTICS

## 9.1 Scope

POI volume analytics is a non-canonical analytical extension of the canonical POI result.

An already canonical POI may be enriched with POI-scoped volume analytics such as total volume, buy volume, sell volume, volume delta, and directional delta ratio when a usable volume method is available.

Volume analytics must never create, remove, retype, or canonically invalidate a POI.

The canonical POI ontology and Rule-of-Two remain owned by Layer 6.

## 9.2 Volume provenance

POI volume is calculated only from candles deterministically associated with the POI's canonical provenance. The mapper must not use an arbitrary fixed candle window.

V1 stores one POI-level aggregate per available volume branch. Additional formation-only or causal-displacement sub-aggregates are not persisted in V1.

For canonical Order Flow:

- the provenance is the complete canonical opposing move;
- all candles belonging to that opposing move are included, including its internal legs;
- the subsequent continuation/displacement is excluded.

For canonical Order Block:

- the provenance is the defining Validated Order Block candle;
- V1 aggregates exactly that one candle.

The POI volume aggregate therefore includes only the candles that form the POI's canonical provenance. Post-formation displacement, reaction, mitigation, and target candles are excluded.

For each available volume branch:

```text
OHLC aggregate_total      = Σ volume.total
ORDERFLOW aggregate_total = Σ (volume.orderflow.buy + volume.orderflow.sell)
aggregate_buy             = Σ buy
aggregate_sell            = Σ sell
aggregate_delta           = aggregate_buy - aggregate_sell

delta_ratio = aggregate_delta / aggregate_total
```

For ORDERFLOW, source-candle delta is derived from each candle's buy and sell values when needed; it is not read from a persisted source-level delta field.

The aggregate is calculated from sums. Candle-level `delta_ratio` values must never be averaged.

The persisted POI provenance retains the source candle identities used for the aggregate. Historical POI outcome performance must not be used.

## 9.3 Volume method

The normalized market-data record may contain multiple volume types in parallel. Availability is determined from the actual presence of the relevant data, not from one exclusive provenance or method field.

The user may explicitly select the analytical method with:

    --volume-method {NONE,OHLC,ORDERFLOW,BOTH}

When omitted, the default is BOTH.

ORDERFLOW requires genuine orderflow buy/sell volume in volume.orderflow. Delta is derived when needed as buy - sell.

OHLC requires volume.total and calculates directional buy/sell volume and delta deterministically from OHLC data. V1 does not use lower-timeframe intrabar refinement.

BOTH uses both available OHLC-derived and genuine orderflow analytics in parallel. The two evidence branches remain separate and are never combined into a single volume value. If only one branch is available, that branch is used. If neither branch is available, no POI volume analytics are produced.

NONE disables POI volume analytics.

The selected method is a runtime processing decision. It does not erase, overwrite, or relabel other available volume data.

If ORDERFLOW is explicitly requested and unavailable, the mapper must not silently downgrade to OHLC.

If OHLC is explicitly requested but required volume data is unavailable, the mapper must not fabricate volume values.

The concrete external provider is implementation-defined and is not part of canonical SMC semantics.

An estimated buy/sell split must never be represented as observed orderflow data.

Evidence provenance remains explicit: genuine orderflow is observed execution-volume data when supplied by the provider; OHLC-derived directional volume is an estimate. BOTH preserves both branches rather than combining their values.

## 9.4 Deterministic OHLC aggregation

For each candle with total volume V > 0 and High > Low:

```text
buy_volume  = V * (Close - Low) / (High - Low)
sell_volume = V * (High - Close) / (High - Low)
delta       = buy_volume - sell_volume
delta_ratio = delta / V
```

Therefore:

```text
buy_volume + sell_volume = V
delta = V * (2*Close - High - Low) / (High - Low)
```

If High == Low and V > 0:

```text
buy_volume  = V / 2
sell_volume = V / 2
delta       = 0
delta_ratio = 0
```

If V == 0, no OHLC directional volume analytics are produced for that candle because there is no traded-volume basis for a directional estimate.

OHLC directional volume is an estimate, not proof of historical bid/ask execution.

All volume arithmetic uses `Decimal`. Intermediate calculations retain full Decimal precision. When a division result must be persisted as a finite decimal string, it is rounded to 18 decimal places using `ROUND_HALF_EVEN`. The same deterministic policy applies to persisted `delta_ratio` values. Persisted volume values use decimal-compatible string representation.

## 9.5 Persisted POI volume representation

Volume analytics are stored on the canonical POI object, not as a general structural-point volume metric.

The V1 representation is one aggregate per available volume branch:

    volume.ohlc
    volume.orderflow

Each branch contains, where the required source data exists:

    total
    buy
    sell
    delta
    delta_ratio

The aggregate is scoped exactly to the POI provenance defined in §9.2. The persisted provenance retains the source candle identities used for the aggregate.

No formation-only or causal-displacement sub-aggregate is persisted in V1. No arbitrary fixed candle window is permitted.

OHLC-estimated and genuine orderflow evidence remain separate. BOTH means both available branches are calculated independently; it does not create a third combined branch or average the two sources.

Volume analytics never alter POI validity, lifecycle, type, role, or downstream monitor targeting.

When no supported volume analytical path is available, no POI-derived volume analytics are calculated.

---

# 10. MONITOR ORCHESTRATION AND CHECKPOINT PERSISTENCE

## 10.1 Mapper process-input boundary

The Mapper is invoked by the Monitor as a separate process and receives its market-data input from the standalone Market Data process.

On invocation:

1. launch/receive the Market Data process output for the requested symbol, timeframe, and range;
2. parse and validate the machine-readable CSV-like STDOUT protocol;
3. group returned records by timeframe and process only records marked `completed=1`;
4. resolve the requested analysis identity;
5. persist the complete symbol-scoped Structures JSON atomically;
6. advance `last_processed_candle_time` only within the same successful persistence transaction;
7. return a process status.

The Mapper must reject malformed machine output and must never fall back to `<SYMBOL>_marketdata.json`.

The Mapper does not schedule itself, refresh current snapshots, resolve targets, apply RR, emit alerts, or manage positions.

## 10.2 Multiple analyses in one Structures file

One symbol-scoped Structures JSON may contain multiple independent mapper analyses.

The Mapper updates only the selected analysis entry and must preserve all unrelated analysis entries. Scheduling, multi-symbol orchestration, and process serialization are Monitor-owned concerns.

---

# 11. DOWNSTREAM TARGET, RR, AND ALERT ELIGIBILITY

The Mapper does not own downstream target selection, target clearance, RR policy, or alert eligibility.

After successful canonical structure persistence, downstream consumers may use the persisted Mapper state as follows:

```text
canonical Mapper state
        ↓
Monitor target resolution
        ↓
target clearance
        ↓
optional --rr policy
        ↓
alert eligibility
```

Ownership remains:
- canonical target semantics: `.agents/skills/smc/` Layer 7;
- implementation/observability boundary: `.agents/skills/smc/` Layer 8 where applicable;
- runtime target evaluation, clearance, RR and alerts: `specifications/smc_monitor_specification.md`.

The Mapper must not create a second target ontology, select a target for alerting, apply `--rr`, or mutate canonical state because of downstream eligibility.
---

# 12. DIAGNOSTICS

## 12.1 CLI debug output

The CLI interfaces must strictly separate persistent market data from user-visible diagnostics.

- Normalized candle data is persisted internally by Market Data and is emitted through the machine-readable STDOUT protocol as the Mapper data pipe.
- Debug and diagnostic information is written to `stderr` only.
- Debug `stderr` is terminal-only. The launcher/monitor must not capture, parse, forward, merge, persist, or pass it to `smc_mapper.py`, `smc_monitor.py`, or the market-data JSON.
- `stderr` must never be merged into a machine-readable data channel.
- Without `--debug`, debug/trace output is suppressed.
- With `--debug`, diagnostics are visible directly on the terminal.
- A process wrapper may capture diagnostics transiently for error reporting, but must never parse or persist them as data.
- Debug mode must never alter canonical calculations or normalized market-data semantics.
- Normal runtime must produce no human-readable status output. Market-data machine input/output remains a process stream and is not a diagnostic/status channel.

## 12.2 Diagnostic data boundary

Debug and diagnostic output is terminal-only. It is not a machine-readable mapper data contract and must never be persisted into either JSON store.

---

# 13. IMPLEMENTATION CODE STYLE

Implementation code must be written for human readability, maintenance, and cross-language portability.

- Use descriptive, semantically meaningful names for variables, interfaces, classes, types, methods, and functions. Names must expose the concept or responsibility they represent.
- Avoid cryptic abbreviations and generic names when a domain-specific name is available.
- Use consistent naming conventions throughout the project: `snake_case` for variables and functions, `PascalCase` for classes/types/interfaces, and `UPPER_SNAKE_CASE` for constants.
- Keep functions and modules focused and reasonably short.
- Prefer simple, direct control flow over unnecessary abstraction.
- Use the same canonical term for the same concept everywhere in the implementation.
- Conventional local names such as `i` are acceptable only in a small, obvious loop where the meaning is immediate.
- Readability and semantic clarity take priority over saving characters.

# 14. IMPLEMENTATION ARCHITECTURE AND MODULE CONTRACT

## 14.1 V1 module boundary

V1 is implemented as one standalone executable module:

    smc_mapper.py

The module may later be split internally, but the following ownership boundaries must remain stable:

1. CLI/input parsing
2. analysis identity and configuration resolution
3. market-data machine-stream parsing/validation
4. coverage and analysis-window selection
5. synchronized HTF/LTF orchestration
6. canonical SMC processing
7. canonical Dealing Range / POI state reconciliation
8. optional POI volume enrichment
9. structures JSON persistence
10. process entrypoint and diagnostics

The mapper must not import or runtime-call market_data.py, smc_monitor.py, smc_htf_ltf_monitor.py, smc_analyzer.py, or legacy engine modules.

The monitor may launch both the Market Data CLI and mapper as separate processes. The mapper receives normalized market-data state only through the Market Data machine-readable STDOUT protocol and processes only records marked `completed=1`.

## 14.2 Dependency direction

The implementation dependency direction is:

    CLI -> identity -> persisted input -> coverage -> canonical processing -> enrichment -> persistence -> checkpoint

Canonical SMC logic must not depend on:

- monitor state;
- provider state;
- current/in-progress market-data snapshots;
- debug output;
- JSON retention policy;
- downstream target/RR policy.

POI volume enrichment may consume canonical POI provenance, but it cannot feed results back into canonical structure.

## 14.3 Domain-state containers

Use explicit state containers for mapper-owned processing state. Python may use dataclass for implementation convenience, but the architecture must remain directly reproducible in MQL4/MQL5.

The following conceptual models are sufficient for the V1 mapper boundary:

    MapperRequest
        symbol
        htf
        ltf
        start_time
        end_time
        history_no
        volume_method
        debug

    AnalysisIdentity
        analysis_key
        htf
        ltf
        analysis_mode
        entry_timeframe
        analysis_start

    MarketDataCandleView
        candle_id
        timestamp
        open
        high
        low
        close
        tick_volume
        spread
        real_volume
        completed

    MarketDataSeries
        symbol
        timeframe
        available_start
        available_end
        candles: array of MarketDataCandleView

    AnalysisState
        identity
        requested_start
        effective_start
        last_processed_candle_time
        structural_state
        history

    StructuresDocument
        symbol
        history_no
        analyses

The conceptual structural_state and history fields are ownership containers for canonical layer state. The mapper specification must not invent a second canonical ontology inside them. Actual canonical objects and fields are taken from .agents/skills/smc/ during implementation.

A transient processing context may be represented separately when needed, containing only explicit point-in-time inputs such as evaluation time, active HTF context reference, and the current completed candle. It must not become persisted monitor state.

## 14.4 MQL4/MQL5 portability

The mapper class contract must be reproducible in both MQL4 and MQL5.

Required portability rules:

- explicit state fields and explicit ownership;
- conceptual arrays of named records instead of Python-only collection semantics;
- no generators, Python Protocol, reflection, metaclasses, dynamic attributes, or properties as correctness dependencies;
- public operations expose explicit success/failure paths;
- UTC timestamps map to MQL datetime semantics;
- canonical field names and meanings remain stable across Python/MQL implementations;
- JSON dictionaries are persistence representation only;
- Python Decimal is an implementation detail of deterministic arithmetic, not a portable type requirement.

Portability does not require reproducing Python's CLI or JSON library implementation details in MQL. It requires the same domain contracts and state transitions.

---

## 14.5 Cross-file contract ownership

The following contracts have one implementation owner:

- Market Data acquisition, normalization, completion, availability, timeframe catalog, retention and market-data JSON serialization: market_data.py / market_data_specification.md.
- Mapper analysis identity, canonical processing orchestration, structures state and structures JSON persistence: smc_mapper.py / this specification.
- Monitor scheduling, process orchestration, current-price/target monitoring and alerting: smc_monitor.py / its implementation contract.

Do not duplicate the Market Data timeframe catalog, provider semantics, candle completion logic, or JSON serialization rules inside the mapper. The mapper may validate and consume them at its boundary, but does not redefine them.

# 15. MAPPER FUNCTION NAMING AND RESPONSIBILITY CONTRACT

The following function boundaries are implementation contracts. Canonical layer-internal helper names are intentionally not prescribed here.

## 15.1 CLI and validation

    build_argument_parser() -> parser
    parse_mapper_request(argv) -> MapperRequest
    validate_mapper_request(request) -> success/failure
    parse_iso8601(value) -> UTC datetime

These functions validate mapper CLI semantics only. They must not execute canonical SMC analysis.

## 15.2 Analysis identity

    build_analysis_key(identity) -> string
    resolve_analysis_identity(request, structures, market_data) -> AnalysisIdentity

Identity resolution must remain deterministic. `build_analysis_key` uses the normalized timeframe configuration plus persisted `analysis_start`. It must never use current wall-clock time. When no explicit start was supplied, `analysis_start` is first resolved from persisted completed data, then the key is built from that resolved boundary.

## 15.3 Market-data boundary

    get_symbol_data_directory(symbol, data_directory) -> Path
    get_structures_path(symbol, data_directory) -> Path
    parse_market_data_stdout(stream) -> MarketDataSeries
    validate_market_data_stream(series, symbol, requested_timeframes) -> success/failure
    select_completed_candles(series, timeframe, start_time, end_time) -> candle array

The mapper process-input parser must validate the Market Data machine protocol without importing Market Data classes. It must accept the CSV-like stream and group records by the explicit `timeframe` field.

The Mapper derives `completion_time` deterministically from the canonical candle `timestamp` and `timeframe`; it is not a wire field.

For explicit analysis-window selection, a candle is eligible when:

- derived `completion_time >= start boundary`; and
- derived `completion_time <= end boundary`.

At this boundary:

- available_start / available_end describe completed-candle coverage only;
- candles are canonical market-data input;
- current is excluded from canonical processing;
- candle completion_time is the eligibility boundary for explicit --endtime;
- optional protocol volume fields retain their independent meanings; no orderflow branch is assumed to exist unless a future compatible protocol explicitly supplies it;
- source-level delta may be derived only from an explicitly available buy/sell pair supplied by the applicable canonical volume contract;
- persisted numeric values must be parsed deterministically and validated before use.

## 15.4 Structures persistence

    create_empty_structures(symbol, history_no) -> StructuresDocument
    load_structures(path, symbol) -> StructuresDocument
    save_structures_atomic(path, structures) -> success/failure

The structures writer owns only mapper structural persistence. It must not write the Market Data JSON.

Persistence helpers may translate domain objects to/from plain Python dictionaries/lists, but mapper canonical logic must operate on explicit domain state rather than depending on dictionary layout.

## 15.5 Canonical processing

    process_analysis(analysis, htf_series, ltf_series) -> changed
    process_candle(analysis, candle, htf_context) -> changed

These are orchestration boundaries. They must delegate semantic decisions to the canonical SMC skill implementation rather than create mapper-specific substitutes for BOS, CHoCH, IDM, retracement qualification, Dealing Range, or POI rules.

## 15.6 POI enrichment

    enrich_poi_volume(poi, source_candles, volume_method) -> changed

This function is downstream of canonical POI formation and lifecycle. It cannot create, remove, retype, invalidate, or revive a canonical POI.

## 15.7 Entrypoint

    run(request) -> exit_status
    main(argv) -> exit_status

Normal execution emits no human-readable status text; market-data input is consumed from the Market Data process STDOUT and diagnostics are emitted only on STDERR according to Section 12.

---

# 16. PERSISTENCE AND CHECKPOINT CONTRACT

## 16.1 Structures JSON transaction boundary

The mapper persists one symbol-scoped file:

    <DATA_ROOT>/<SYMBOL>/<SYMBOL>_structures.json

Conceptually:

    {
      "symbol": "CCCC",
      "history_no": 5000,
      "analyses": {
        "H4_M15_2026-06-10T12:00:00Z": { ... }
      }
    }

The JSON form may use an object keyed by deterministic analysis key even though the portable domain model represents analyses as an explicit array. The key is an index/serialization convenience; canonical semantics do not depend on JSON container type.

A mapper invocation performs one complete read-modify-write transaction for the affected symbol. Unrelated analysis entries must be preserved semantically and must not be dropped or merged.

## 16.2 Atomic persistence

Use the same persistence discipline as Market Data:

1. serialize the complete structures document deterministically;
2. write a temporary file in the same directory;
3. flush and close successfully;
4. atomically replace the target;
5. retry finite transient failures;
6. remove temporary files on failure.

No separate lock file is required for V1 because the monitor serializes active orchestration per symbol.

## 16.3 Checkpoint ordering

The mapper must update last_processed_candle_time in the in-memory analysis state only as part of a successful processing result, and the persisted checkpoint is authoritative only after the complete structures document has been atomically persisted.

A failure before persistence must not leave a falsely advanced checkpoint in durable state.

The persisted checkpoint must correspond to the latest completed entry-timeframe candle actually incorporated by the successful processing transaction and must not be later than the resolved analysis end boundary.

The checkpoint is implementation provenance only; it has no canonical SMC meaning.

---

# 17. PURE-FUNCTION AND TESTABILITY BOUNDARIES

Where practical, the following operations must be deterministic/pure with explicit inputs:

- CLI validation after parsing;
- analysis-key construction;
- analysis-window selection;
- point-in-time HTF context selection;
- candle eligibility selection from persisted data;
- Dealing Range history reconciliation input/output;
- POI volume aggregation;
- OHLC directional-volume calculation;
- JSON serialization of already-resolved state.

Stateful orchestration is allowed only where state mutation is the purpose of the function. Avoid hidden global state, hidden caches that affect correctness, or provider calls from canonical processing.

Tests must be able to execute canonical-processing logic from fixed persisted candles without network access or live wall-clock dependence.

---

# 18. REQUIRED TEST STRUCTURE AND DEFINITION OF DONE

The global developer-agent naming, portability, prompt-efficiency, and validation rules in `AGENTS.md` apply to the Mapper. Mapper validation scenarios are defined by the implementation contract.

At minimum, the finished mapper implementation must have focused tests covering:

- CLI option parsing, including equal HTF/LTF single-timeframe mode and invalid HTF<LTF combinations;
- deterministic analysis-key creation from normalized timeframe configuration + persisted analysis_start;
- ambiguous existing-analysis selection;
- UTC parsing and completion_time-based end-time eligibility;
- rejection of current/in-progress candles as canonical input;
- independent HTF/LTF ranges and HTF_CONTEXT_UNAVAILABLE behavior;
- point-in-time HTF context, proving later HTF events do not reinterpret earlier LTF events;
- bootstrap versus incremental resume from last_processed_candle_time;
- deterministic Dealing Range identity/history reconciliation and history_no retention;
- canonical POI lifecycle pass-through without introducing mapper-specific lifecycle states;
- POI volume provenance and branch separation for NONE/OHLC/ORDERFLOW/BOTH;
- source-level delta derivation from buy/sell with no persisted candle-level delta dependency;
- deterministic OHLC directional-volume aggregation and zero-volume behavior;
- structures JSON atomic persistence and checkpoint ordering;
- MQL-portable domain-state behavior independent of Python-specific collection mechanics;
- absence of runtime/import dependencies on legacy modules and Market Data/Monitor modules.

Definition of done:

- smc_mapper.py implements the contracts in this specification;
- mapper consumes only normalized Market Data machine output and never a concrete provider;
- Market Data and mapper JSON stores remain strictly separated by ownership;
- canonical SMC decisions are governed by .agents/skills/smc/;
- Market Data current snapshot never enters canonical structural input;
- no source-level orderflow delta field is required;
- checkpoint advances only after successful atomic persistence;
- analysis_start is persisted and is the sole analysis-identity boundary;
- structures state is deterministic and incrementally resumable;
- implementation contains no runtime dependency on legacy artifacts;
- focused mapper tests pass without network access;
- the code structure remains directly portable at the class/contract level to both MQL4 and MQL5.

**STATUS: CURRENT IMPLEMENTATION CONTRACT — CROSS-FILE OWNERSHIP RECONCILED**
