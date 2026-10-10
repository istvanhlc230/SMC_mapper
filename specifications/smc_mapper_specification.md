# SMC Mapper Specification

**Status:** Current implementation specification.
**Scope:** Functional and implementation specification for the future `smc_mapper.py`.
**Canonical authority:** `.agents/skills/smc/` remains the sole authority for canonical SMC semantics. This document does not redefine those rules.

---

# 0. SCOPE, AUTHORITY, AND RUNTIME BOUNDARIES

## 0.1 Active product runtime components

The intended finished product uses these active Python runtime components:

- `market_data.py` — standalone Market Data CLI: provider access, normalization, completion handling, deterministic range retrieval, incremental update, bounded retention, completed-candle persistence, current-candle snapshot refresh, and persistence to `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json`.
- `smc_mapper.py` — stateless canonical SMC mapper: structural analysis, HTF/LTF processing, and per-invocation JSON or `--cleartext` output. It does not persist structural state.
- `smc_monitor.py` — interactive runtime: scheduling, user interaction, runtime/target monitoring, alerts, and orchestration of Market Data CLI and Mapper execution across configured symbols/timeframes. Mapper analyses are recomputed, not discovered from persisted Structures files.

The older `smc_htf_ltf_monitor.py`, `smc_analyzer.py`, and Layer-1-to-Layer-6 `*_engine.py` implementation artifacts are not components of the finished product architecture.

These legacy artifacts are optional source material only. Reusable implementation patterns, algorithms, tests, or utility code may be extracted into the finished product when they are compatible with this specification and the canonical skill. The finished product must not retain a runtime, import, schema, or behavioral dependency on any legacy artifact.

This specification defines the mapper contract and its boundaries with the standalone Market Data CLI and interactive monitor.

## 0.2 Implementation ownership boundaries

The mapper has no direct connection to any concrete market-data provider and has no runtime import dependency on `market_data.py`. The Monitor/orchestrator owns process invocation: it launches `market_data.py`, validates the successful machine-output result, and supplies that exact CSV stream to the Mapper process through STDIN. The Mapper does not launch Market Data itself.

`market_data.py` is a standalone Market Data CLI process. It owns provider access, provider abstraction, normalization, completion handling, timestamp normalization, availability detection, deterministic range retrieval, incremental updates, retention and persistence to `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json`.

The Market Data process boundary is the standalone `market_data.py` executable and its machine-readable STDOUT candle protocol; the Mapper consumes that protocol on its STDIN.

The normal data flow is:

```text
Provider/cache -> market_data.py -> machine CSV STDOUT
              -> smc_monitor.py validates and passes CSV as Mapper STDIN
              -> smc_mapper.py computes canonical state in memory
              -> one per-invocation result on STDOUT (JSON by default)
```



The machine-readable candle stream is the Mapper's market-data portability boundary. The Mapper must not know whether the Market Data process obtained data from LSE, a future MT4/MT5 adapter, a broker, replay data, cache, or another provider.

The persisted market-data JSON is an internal Market Data storage format. It is not the Mapper process-input contract and must not be opened, parsed, or depended on by the Mapper.

The Mapper must never call a concrete provider, perform provider-specific API requests, depend on provider-specific response formats, dynamically request additional data during canonical processing, or import `market_data.py` as a Python data API. It consumes only the validated input stream supplied by the orchestrator for that invocation.

V1 implements the process boundary with Python `market_data.py`. Future platform implementations may provide the same machine-readable candle contract without changing Mapper/SMC logic. MT4/MT5 are portability targets only; no MT4/MT5 implementation is part of V1.

## 0.3 Time-domain and positional period contract

The Mapper operates on canonical UTC only. Market Data supplies canonical UTC candle interval-start timestamps, OHLC values, optional primitive volume fields, and completed status. Source-native timestamps are not canonical Mapper input.

The optional positional `PERIOD` grammar is:

- `YYYY.MM.DD` — the full UTC calendar day;
- `YYYY.MM.DD-YYYY.MM.DD` — both endpoint dates inclusive, represented as a half-open UTC interval;
- `YYYY.MM.DD[@HH:MM]-YYYY.MM.DD[@HH:MM]` — explicit range; each endpoint may independently include a time;
- `YYYY.MM.DD[@HH:MM]-` — from the date's midnight or specified UTC minute through the current UTC time;
- `-YYYY.MM.DD[@HH:MM]` — from the earliest completed candle retained in the Market Data cache through the specified UTC day/minute.

If PERIOD is omitted, analyze all completed history supplied by Market Data, from the earliest available candle through the latest completed candle.

Date-only starts resolve to 00:00 UTC. Date-only ends resolve to the exclusive boundary at 00:00 UTC on the day after the named date. A time may appear only as an endpoint of a range; a standalone date-time without a hyphen is invalid. A date-only scope without a hyphen means the full UTC day. A trailing hyphen means from the start date/time to now. Only `HH:MM` is accepted; seconds, timezone suffixes, and machine-local timezone interpretation are rejected. For an open-end period, capture current UTC once at invocation start and use the same instant across all timeframes. Future starts and reversed/empty ranges are rejected.

Period selection uses candle interval-start timestamps with half-open semantics: `start <= candle.timestamp < end`. Completion status is checked separately. Open-start selection uses each timeframe's earliest completed candle present in the validated Market Data stream, which must correspond to the earliest retained candle in that timeframe's cache, not its latest candle. The Mapper derives coverage from CSV rows and never reads Market Data's private JSON metadata. HTF and LTF may therefore have different earliest retained boundaries.

The requested period defines the output/evaluation window, not the start of canonical computation. For deterministic SMC state, Mapper processes all completed candles present in the supplied stream from the earliest available candle through the resolved requested end. The input stream must therefore include the full retained history through that end for every requested timeframe. If required history/context is unavailable, fail closed or preserve the specific unresolved dependency as required by the canonical skill. Output includes structures/events relevant to the requested window plus any earlier carry-in state required to interpret them or describe the canonical state at the requested end. Metadata distinguishes requested period, actual per-timeframe coverage, canonical processing coverage, and requested output window. There is no persistent identity or checkpoint.

## 0.4 Process input and output boundaries

Market Data owns the retained candle cache. The Mapper owns no data directory, persistent Structures JSON, structural cache, checkpoint file, or analysis registry.

The Mapper consumes captured machine-readable Market Data STDOUT through STDIN. It does not launch Market Data, discover or open the Market Data persistence file, or accept an alternate JSON input path.

Rules:

- malformed machine input fails the invocation;
- Market Data diagnostics on STDERR are never treated as candle data;
- Mapper never falls back to reading Market Data's JSON file;
- JSON is the default output; `--cleartext` is an optional presentation mode;
- Mapper creates or updates no persistent Structures file, structural cache, checkpoint, or analysis registry.

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

    timeframe,time,open,high,low,close,tick_volume,spread,real_volume,volume_total,orderflow_buy,orderflow_sell,completed

The Mapper parses the CSV stream without importing Market Data Python classes.

`time` is the canonical UTC interval-start epoch. `completed` is `1` only for a completed candle and `0` only for a current/in-progress snapshot.

The protocol does not redundantly transmit `completion_time`. The Mapper deterministically derives the canonical completion boundary from `timeframe + timestamp` using the canonical timeframe rules defined by the Market Data contract. This derived boundary is used for explicit end-time eligibility.

`tick_volume`, `spread`, and `real_volume` are independent optional provider fields. `volume_total` explicitly transports normalized `volume.total`; `orderflow_buy` and `orderflow_sell` explicitly transport genuine normalized `volume.orderflow.buy/sell`. Empty fields mean unavailable. The Mapper must never infer `volume_total` from tick/real volume or treat an OHLC estimate as observed orderflow.

The Mapper must reject malformed required fields, invalid timestamps, malformed OHLC, duplicate candle identities, non-ascending timestamps within a timeframe, and any record with `completed=0` for structural processing. A row with only one of `orderflow_buy` and `orderflow_sell` populated is malformed and must be rejected; a valid unavailable orderflow pair has both fields empty.

## 1.3 Normalized candle representation

The Mapper's external candle view is the machine-protocol record, not the Market Data persistence model. It contains the required OHLC fields plus the optional `tick_volume`, `spread`, `real_volume`, `volume_total`, `orderflow_buy`, and `orderflow_sell` fields defined by the process contract.

The Mapper derives the canonical completion boundary from `timestamp + timeframe`; `completion_time` is therefore a derived analysis value and is not part of the wire record.

The optional volume fields are availability signals. Empty fields remain unavailable; the Mapper must not fabricate, rename, or infer one optional field from another.

The process protocol explicitly carries `volume.total` as `volume_total` and genuine `volume.orderflow.buy/sell` as `orderflow_buy/orderflow_sell`. It does not carry the Market Data persistence JSON or a precomputed `volume.ohlc` branch. When `--volume-method` enables OHLC analytics, the Mapper derives directional estimates from `volume_total` and the same candle's OHLC values using §9.4. When it enables ORDERFLOW analytics, both observed orderflow fields must be present.

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

A candle is considered completed only after its canonical timeframe interval has closed and the normalized provider/completion contract confirms that closure. Every persisted normalized candle carries a UTC `completion_time` representing that canonical interval-close boundary. Mapper uses the candle interval-start `timestamp` for positional-period membership and validates `completed` separately; `completion_time` is used to exclude candles that have not yet closed, not as the period-range coordinate.

The mapper must use the candle's canonical completion boundary when deciding whether it is eligible for an explicit analysis end time. The candle timestamp is not by itself sufficient evidence of completion.

An incomplete/current candle must be excluded from the canonical analysis series. It may be stored only in the per-timeframe current snapshot of <SYMBOL>_marketdata.json and must never be consumed as canonical structural input.

The current snapshot is runtime market-data state, not historical candle history. Refreshing it does not change the historical completed-candle stream used by a Mapper invocation.

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

When total traded volume is available from the provider, market_data.py preserves it as `volume.total` internally and transports it as `volume_total` on the machine protocol. When genuine orderflow is available, it is preserved independently under `volume.orderflow` and transported as `orderflow_buy` / `orderflow_sell`. The Market Data persistence JSON remains private to Market Data.

The Mapper calculates its POI-scoped OHLC directional estimate from the transported `volume_total` and OHLC fields; it does not require a wire-level `volume.ohlc` object. The Mapper must preserve the applicable POI volume analytics and source-candle provenance. Parallel volume types must not overwrite one another.

Volume provenance is represented by the data branch that is actually present. A single exclusive volume source or volume method field is not required on the candle.

---

# 2. CLI AND INPUT RESOLUTION

## 2.1 Symbol

One required instrument per mapper execution.

One mapper execution analyzes one symbol.

---

## 2.2 HTF

Required. Exactly one valid timeframe must be supplied.

Example: `--htf H4`

---

## 2.3 LTF

Required. Exactly one valid timeframe must be supplied.

Example: `--ltf M15`

---

## 2.4 Timeframe relationship and analysis mode

The Mapper supports one conformant analysis mode only:

- `HTF_LTF`: both `--htf` and `--ltf` are explicitly supplied, the timeframes are distinct, and `HTF > LTF`.

Missing timeframe arguments, equal HTF/LTF values, or `HTF < LTF` are input errors. The Mapper must never silently swap, invent, or relabel timeframe inputs.

Single-timeframe-only analysis is not a conformant True SMC mapping mode. A selected timeframe must never be treated as both HTF and LTF.

If both timeframe arguments are present but required historical coverage or context for either series is unavailable, the Mapper must preserve the dependent result as unavailable and fail closed; it must not downgrade the run to single-timeframe analysis.

---

## 2.5 Entry timeframe

The LTF is the entry timeframe and drives Monitor runtime scheduling. Market Data may use incremental provider acquisition internally, but Mapper always recomputes from the full retained history supplied to the invocation.

The entry timeframe determines completed-candle cadence for runtime scheduling and the requested processing/output boundaries. HTF remains the higher-context timeframe and is processed first as required to provide point-in-time context for the entry timeframe.

---

## 2.6 HTF pullback validation

HTF pullback validation is mandatory wherever required by canonical True SMC structural qualification. It is available only when both distinct timeframe series are supplied.

### Valid two-timeframe request

`--htf H4 --ltf M15`

- Establish H4 structural context first.
- Process M15 in chronological order against the HTF facts already canonical at each LTF evaluation time.
- Never allow a later HTF event to retroactively reinterpret an earlier LTF event.

### Invalid requests

- `--htf H4`: LTF is missing.
- `--ltf M15`: HTF is missing.
- `--htf H1 --ltf H1`: HTF and LTF are not distinct.
- Any configuration where `HTF < LTF`: invalid timeframe relationship.

Each invalid configuration is rejected; no substitute timeframe or single-timeframe mode is inferred.

---

## 2.7 Positional period resolution

The CLI accepts one optional positional `PERIOD` argument. The `--starttime`, `--endtime`, and `--update-range` options are not part of the CLI contract.

| Positional value | Resolved scope |
|---|---|
| omitted | all completed candle history supplied by Market Data |
| `YYYY.MM.DD` | full UTC day, `[00:00, next day 00:00)` |
| `YYYY.MM.DD-YYYY.MM.DD` | inclusive full-day range |
| `YYYY.MM.DD[@HH:MM]-YYYY.MM.DD[@HH:MM]` | explicit half-open UTC interval; time is optional independently on either endpoint |
| `YYYY.MM.DD[@HH:MM]-` | start date/time through the current UTC time captured at invocation start |
| `-YYYY.MM.DD[@HH:MM]` | earliest retained completed candle through the exclusive end of the specified UTC day/minute |

The canonical date spelling is `YYYY.MM.DD` and time spelling is `HH:MM`. Time is optional on each explicit range endpoint. All values are UTC. Seconds, timezone suffixes, and machine-local timezone interpretation are not accepted. The parser must recognize the leading-hyphen `-YYYY.MM.DD[@HH:MM]` expression as the positional PERIOD, not misinterpret it as an unknown option; users must not need an extra `--` delimiter.

For open-start periods, resolve the earliest completed candle present in the validated returned CSV separately for each timeframe; the stream must cover the full retained cache history through the explicit end boundary. The Mapper must not assume private Market Data JSON metadata is available. For an open-end period, capture current UTC once at invocation start and use that fixed instant for all timeframe groups. Reject future starts and reversed/empty intervals.

The requested period filters which events/structures are presented as belonging to the requested output window, but does not truncate canonical processing history. `select_processing_candles()` must select every supplied completed candle from the earliest available candle through the requested end; it must not apply the requested start. `select_output_window_candles()` separately selects the requested interval for presentation. The result may include earlier carry-in structures needed to interpret in-window events or represent state at the requested end, but must identify them as context rather than claim they formed in the requested window.

## 2.8 Completed-candle and window selection

A candle is eligible for canonical processing only when the normalized completion contract confirms that it is completed. An incomplete/current candle is never processed as canonical history.

The requested output window uses candle interval-start timestamps and half-open semantics: `start_time <= candle.timestamp < end_time`. This filter controls output-window membership only; canonical processing still begins at the earliest completed candle supplied and continues through the resolved requested end. Completion status is checked separately. A date-only end includes the entire named UTC date by resolving to the following day's midnight as the exclusive boundary.

The Mapper distinguishes requested period, actual completed-candle coverage per timeframe, canonical processing coverage, and requested output window. There is no persisted analysis identity, checkpoint, resume point, or historical-update mode. Every invocation reconstructs canonical state from the full retained candle history supplied through the requested end.

## 2.9 Input validation

Before canonical analysis, validate symbol, both timeframe values, strict HTF > LTF relationship, positional-period syntax and resolved UTC boundaries, timestamp ordering, duplicate timestamps, completed-candle status, OHLC integrity, required volume-field pairing, and required MTF context coverage.

Malformed dates/times, impossible dates, invalid 24-hour times, unsupported seconds/timezone suffixes, standalone date-time values without a range hyphen, reversed/empty intervals, and future range starts fail explicitly before canonical processing. Provider/API failures and acquisition errors belong to Market Data. Missing required historical/context candles must not be fabricated.

## 2.10 Configuration boundary

No separate Mapper configuration file is required. Mapper behavior is controlled by CLI parameters, explicit defaults, Market Data machine-output metadata/candle records, and the canonical SMC skill. Provider configuration and retained candle storage belong to Market Data; Mapper never reads its private JSON file.

Timeframe selection is controlled only by `--htf` and/or `--ltf`. Timeframe catalog and duration ownership remain with the Market Data contract; Mapper must not introduce a second hard-coded `SUPPORTED_TIMEFRAMES` list.

Volume analysis uses `--volume-method {NONE,OHLC,ORDERFLOW,BOTH}`, default `BOTH`. Genuine orderflow and OHLC-derived directional-volume analytics remain separate branches. If only one is available, use that branch; if neither is available, produce no POI volume analytics.

## 2.11 CLI and --help contracts

Every documented CLI option must be parsed, validated, applied, and documented in English `--help`. `--help` works without other required arguments and exits successfully.

### `smc_mapper.py`

```text
Usage:
  python smc_mapper.py --symbol SYMBOL [--htf TF] [--ltf TF] [PERIOD]
                       [--history-no N]
                       [--volume-method {NONE,OHLC,ORDERFLOW,BOTH}]
                       [--cleartext] [--debug] [--help]

Options:
  --symbol SYMBOL
      Required instrument symbol.

  --htf TF
      Optional Higher Timeframe. With --ltf, HTF must be strictly higher.

  --ltf TF
      Optional selected/entry timeframe. With --htf, this is the entry timeframe.
      At least one of --htf or --ltf must be supplied.

  PERIOD
      Optional positional UTC scope. Supports YYYY.MM.DD,
      YYYY.MM.DD-YYYY.MM.DD, YYYY.MM.DD-YYYY.MM.DD, YYYY.MM.DD[@HH:MM]-YYYY.MM.DD[@HH:MM],
      YYYY.MM.DD[@HH:MM]-, and -YYYY.MM.DD[@HH:MM]. Omission means all completed
      history supplied by Market Data.

  --history-no N
      Closed Dealing Range history capacity, N >= 1; default 5000.
      Applies to this invocation only and is not persisted.

  --volume-method {NONE,OHLC,ORDERFLOW,BOTH}
      Select non-canonical POI volume analytics. Default: BOTH.

  --cleartext
      Render the result in human-readable form instead of JSON.
      Presentation-only; does not change canonical processing.

  --debug
      Emit additional diagnostics to STDERR only.

  --help
      Show this help and exit.
```

### STDIN contract

Every non-help invocation reads one complete machine-readable Market Data CSV stream from STDIN. Empty input, malformed protocol, unexpected timeframe rows, incomplete/current rows in the completed-candle stream, or symbol/timeframe/coverage mismatch is an explicit failure. Mapper never launches Market Data and never opens `<SYMBOL>_marketdata.json`.

### Stateless execution and output contract

Mapper is a stateless computation component. It has no Structures JSON file, structural cache, analysis registry, checkpoint, incremental-resume mode, query/list/delete mode, or historical cache-update mode. Every invocation reconstructs canonical state from all validated retained completed candles supplied through the requested end.

Default STDOUT contains exactly one complete JSON document for the current invocation. It includes symbol, timeframe configuration, normalized requested period, actual per-timeframe coverage, canonical processing coverage, requested output window, canonical structural results, and relevant provenance. It is generated from the validated in-memory result; no file is persisted or re-read. STDOUT contains no progress text, banners, diagnostics, or partial JSON.

With `--cleartext`, STDOUT contains a human-readable rendering of that same successful result instead of JSON. STDERR is reserved for diagnostics/errors in both modes. `--debug` adds diagnostic detail to STDERR only. A non-zero exit means no successful result is emitted.

The result is per-invocation output, not a durable source of truth. If a caller needs to retain it, that caller owns storage; Mapper never writes output to a file.

### Historical recomputation

Historical recomputation is an ordinary invocation with a positional period. Mapper rebuilds state from all retained completed candles supplied through the requested end, beginning at the earliest candle in each timeframe's returned history. A corrected historical candle in the Market Data cache is naturally reflected by the next invocation and all downstream structural lifecycle outcomes. No special update command is required.

The Monitor/orchestrator must request the full retained Market Data history through the requested end (normally Market Data's open-start `--range -END` form), then pass that complete CSV stream to Mapper. If the stream lacks retained-history coverage or required canonical context, Mapper fails closed instead of presenting an incomplete result as complete.

Example process pipe:

```text
python market_data.py --symbol SYMBOL --timeframes HTF LTF --range MARKET_DATA_SCOPE | python smc_mapper.py --symbol SYMBOL --htf HTF --ltf LTF [PERIOD]
```

Market Data output must include all retained completed candles through the Mapper's requested end, not just the visible output window; use the Market Data open-start `--range -END` form for this full-history result. Market Data's `--range` is not passed to Mapper as a flag. The Monitor must pass its configured timeframe selection explicitly; it must not discover timeframe configuration from a Structures file.

# 3. PER-INVOCATION ANALYSIS MODEL

## 3.1 Invocation metadata

Each Mapper invocation is independent. There is no persistent analysis identity, stored analysis registry, Structures JSON, checkpoint, or resume selection.

The result identifies the invocation by symbol, normalized timeframe configuration, normalized requested period, actual available coverage, and processing/output boundaries. Any optional correlation identifier is output metadata only and must not load or mutate state.

The only conformant timeframe model is `HTF_LTF`: both timeframes are supplied, HTF is strictly higher than LTF, and LTF is the entry timeframe.

## 3.2 Per-run structural state

Canonical structures, lifecycle state, Dealing Range state/history, IDM provenance, BOS/CHoCH outcomes, canonical POIs, and volume enrichments exist only in memory for one invocation. They are serialized into the result and then released.

`history_no` is a per-invocation setting, default 5000, not a persisted symbol-level configuration. Mapper must not persist canonical structure or dynamic monitor/trade state.

The Market Data cache remains the only persistent candle-history source in this data path. Mapper receives its machine-readable candle stream and does not read Market Data's private JSON file.

# 4. DATA COVERAGE, BOOTSTRAP, AND WARM-UP PLANNING

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

The Monitor/orchestrator invokes the Market Data CLI for the required bootstrap range in deterministic batch form, then supplies the captured machine-readable STDOUT as Mapper STDIN.

Every invocation rebuilds canonical state from the full retained history supplied through the requested end; the requested start filters output, not canonical processing. The Monitor/orchestrator obtains that history from the Market Data cache (which may fetch only missing candles) and passes the validated stream through STDIN. In two-timeframe mode, the stream must include all HTF/LTF overlap and warm-up candles needed for point-in-time context. The Mapper does not compare against prior checkpoints or incrementally append structural events.

The mapper obtains its market-data stream from the Monitor/orchestrator through STDIN and does not access a concrete provider.

### Two-timeframe LTF bootstrap

In two-timeframe analysis, the mapper establishes an LTF bootstrap coverage reference from the applicable HTF canonical structural context.

When a confirmed HTF Dealing Range exists, the applicable HTF Protected Structural Extreme is the preferred LTF bootstrap coverage reference. This reference determines the minimum historical LTF coverage needed for deterministic structural buildup. It is a data-coverage/reference point only; it is not an LTF structural start and does not create or promote any LTF structure.

When LTF bootstrap is required, the Monitor/orchestrator invokes the Market Data CLI once for one deterministic LTF range covering the anchor through the activation/current boundary, subject to any additional LTF warm-up required by the canonical LTF rules, allows Market Data to update its internal persistence, then passes the returned machine-output range to the Mapper through STDIN.

If the requested LTF coverage begins later than the anchor because the source has no completed LTF data at or after the requested anchor, the mapper uses the first actually available completed LTF candle after the reference as the effective LTF bootstrap start. No attempt is made by the mapper to access the provider directly.

If the supplied LTF data begins before the HTF reference, that earlier data may be retained and used as additional canonical LTF warm-up when required; the HTF Protected Structural Extreme remains the context/coverage reference.

If the applicable confirmed HTF Protected Structural Extreme does not exist, the mapper does not fabricate one. The LTF bootstrap then follows the supplied LTF history subject to the canonical genesis/source-gap boundaries.

The LTF bootstrap reference is not an LTF structural-start ontology. The first LTF structural object is determined only by the canonical LTF rules.

---

# 5. MAPPER EXECUTION PIPELINE

## 5.1 Mapper execution pipeline

The mapper executes the following dependency-ordered pipeline for every analysis invocation:

1. Validate CLI inputs and the normalized market-data contract.
2. Resolve the analysis mode, requested period, available coverage, and required processing/output boundaries.
3. Initialize fresh in-memory canonical state for this invocation.
4. Verify the supplied stream covers the requested period and all required bootstrap/warm-up context.
5. Process completed candles only, in chronological order, using the canonical SMC skill as the sole semantic authority.
6. Establish and maintain point-in-time HTF context; evaluate LTF candles only against HTF facts already canonical at the LTF evaluation time. A required context that is not available remains unresolved / fails closed.
8. Reconcile canonical structural lifecycle, Dealing Range state/history, and canonical POI state according to the skill-owned semantics.
9. Enrich already-canonical POIs with optional non-canonical volume analytics when requested and available.
10. Serialize the completed in-memory result to the selected STDOUT presentation mode; do not persist canonical state.

The mapper must never use a later event, incomplete candle, analytical volume result, storage-retention event, or downstream monitor state to retroactively redefine canonical structure.

## 5.2 Canonical semantic ownership

The exact SMC rules are implemented according to `.agents/skills/smc/`. This specification defines orchestration, data contracts, state boundaries, persistence, and downstream interfaces only.

The mapper must consume canonical outcomes from the applicable skill layers rather than reproduce their rules in the specification or invent alternative semantic gates.

Canonical ownership remains:

- structural and retracement/IDM rules: canonical skill Layer 3;
- BOS rules and required upstream gates: canonical skill Layer 4;
- CHoCH mechanics, including the LTF-CHoCH Context After HTF Interaction and Valid-Pullback Reference Substitution: canonical skill Layer 5;
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
- when first-BOS processing is recomputed in a later invocation, required bootstrap/process state must be deterministically reconstructed from the same complete canonical candle history; it must not rely on saved Mapper state or alter the bootstrap anchor or pre-break dynamic observation boundary.

The mapper's canonical processing boundary is the completion of each eligible completed candle within the resolved analysis interval.

For every processed candle:

- all required upstream canonical state is resolved before downstream state consumes it;
- a canonical decision is evaluated only from information point-in-time available at that candle's evaluation time;
- downstream analytical enrichment cannot mutate canonical structural truth;
- per-run processing metadata carries implementation provenance only and has no canonical SMC meaning.

A successful invocation returns the validated in-memory result. A failed or unresolved canonical dependency must not be converted into a successful structural result.

---

# 6. SYNCHRONIZED HTF/LTF CONTEXT

## 6.1 Independent timeframe semantics

Each timeframe is analyzed according to its own canonical structural rules.

In every valid invocation, HTF and LTF remain separate canonical analyses while sharing a synchronized execution timeline.

The LTF is not a canonical child of the HTF and must not redefine or mutate HTF structure.

The HTF provides the execution context required by canonical LTF rules where such context is explicitly specified.

There is no conformant single-timeframe-only execution mode; a request lacking either distinct timeframe is rejected and unavailable context is never synthesized.

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

This includes the canonical LTF-CHoCH Context After HTF Interaction, implemented through Valid-Pullback Reference Substitution, after HTF POI interaction or HTF core-liquidity takeout, as defined by `05_CHOCH_mechanics.md`.

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

`history_no` is a per-invocation configuration value, defaulting to 5000, and is not persisted.

In two-timeframe mode, it applies independently to the HTF CLOSED DEALING RANGE history retained inside each distinct mapper analysis entry. The LTF does not have a separate `history_no`.

The conformant HTF/LTF analysis retains HTF CLOSED DEALING RANGE history; there is no single-timeframe-only history mode.

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

### `history_no` per-invocation rules

`history_no` is a per-invocation output-retention setting, not symbol-level persisted configuration. If omitted, use `5000`. If supplied, `N` must be an integer >= 1 and applies to the current invocation only. No value is loaded from or written to a Structures JSON file.

Changing `history_no` changes retained closed Dealing Range history in the returned result only. It does not change canonical SMC semantics.

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

The Market Data persistence record may contain multiple volume types in parallel. At the Mapper process boundary, availability is determined only from the explicit `volume_total` and observed `orderflow_buy/orderflow_sell` fields; the Mapper does not read the internal Market Data JSON.

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

# 10. MONITOR ORCHESTRATION AND RESULT DELIVERY

## 10.1 Mapper process-input boundary

The Mapper is invoked by the Monitor as a separate process and receives market-data input through STDIN. The Monitor owns the separate Market Data process invocation and passes its captured machine-readable STDOUT to the Mapper.

On invocation:

1. read the supplied machine stream from STDIN;
2. parse and validate the machine-readable CSV-like protocol;
3. group returned records by timeframe and process only records marked `completed=1`;
4. resolve the positional period and required canonical warm-up/context coverage;
5. initialize and compute canonical state in memory from the supplied history;
6. serialize one successful result to STDOUT as JSON by default or cleartext when explicitly requested.

The Mapper must reject malformed machine output and must never fall back to `<SYMBOL>_marketdata.json`.

The Mapper does not schedule itself, refresh current snapshots, resolve targets, apply RR, emit alerts, manage positions, or write any persistent file.

## 10.2 Stateless repeated invocation

Every invocation recomputes canonical state from the supplied completed-candle history. A historical correction in Market Data is reflected naturally by the next invocation. The Mapper never loads previous Mapper output, merges with old structures, advances a checkpoint, or depends on a previous process run.

The Monitor owns runtime scheduling cadence and supplies all timeframe/context data needed for each fresh computation. It may retain the latest parsed Mapper result in memory for downstream evaluation during the current runtime, but must not treat that transient result as a persistent canonical cache or as input to later Mapper computations.

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
- On successful completion, Mapper emits the per-invocation result to STDOUT as JSON by default, or as human-readable output when `--cleartext` is supplied.
- Debug, diagnostic, and error information is written to `stderr` only; it must never be mixed with either JSON protocol.
- Debug `stderr` is terminal-only. The launcher/monitor must not capture, parse, forward, merge, persist, or pass it to `smc_mapper.py`, `smc_monitor.py`, or the market-data JSON.
- `stderr` must never be merged into a machine-readable data channel.
- Without `--debug`, debug/trace output is suppressed.
- With `--debug`, diagnostics are visible directly on the terminal.
- A process wrapper may capture diagnostics transiently for error reporting, but must never parse or persist them as data.
- Debug mode must never alter canonical calculations or normalized market-data semantics.
- Normal JSON mode must produce no human-readable status output. Market Data CSV on Mapper STDIN and Mapper's default JSON result on STDOUT are distinct machine-readable process contracts. `--cleartext` intentionally replaces JSON presentation for direct human use; diagnostics remain on STDERR.

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

## 14.1 V1 executable and internal package

V1 exposes one root executable entry point, `smc_mapper.py`. The implementation is split into focused Python modules under `SMC_MAPPER/`; canonical layer implementations must not be collapsed into one large script.

Required source layout:

```text
smc_mapper.py
SMC_MAPPER/
    __init__.py
    models.py
    cli.py
    market_data_input.py
    period.py
    layer1_micro_structure.py
    layer2_minor_structure.py
    layer3_structural_semantics.py
    layer4_bos.py
    layer5_choch.py
    layer6_execution_poi.py
    htf_ltf_synchronization.py
    dealing_range_history.py
    volume_analytics.py
    processor.py
    output.py
```

Module responsibilities:

| Module | Sole responsibility |
|---|---|
| `smc_mapper.py` | Thin executable entry point; calls the package CLI/run path and returns its exit status. |
| `models.py` | Explicit cross-layer candle, request, transient structural-state, and result DTOs; no canonical decision logic. |
| `cli.py` | Mapper argument parsing and request validation; no file/network/process I/O. |
| `market_data_input.py` | Parse and validate the fixed Market Data CSV STDIN protocol; no provider or JSON-store access. |
| `period.py` | Parse positional period expressions and normalize UTC processing/output boundaries. |
| `layer1_micro_structure.py` | Implement only canonical Layer-1 candle/micro-structure semantics from the skill. |
| `layer2_minor_structure.py` | Implement only canonical Layer-2 pullback, verified-extreme, and Minor IDM semantics from the skill. |
| `layer3_structural_semantics.py` | Implement only canonical Layer-3 structural lifecycle, Major IDM, swing promotion, and retracement qualification semantics from the skill. |
| `layer4_bos.py` | Implement only canonical Layer-4 BOS mechanics and consume Layer-3-owned state. |
| `layer5_choch.py` | Implement only canonical Layer-5 CHoCH mechanics and tested-level provenance rules. |
| `layer6_execution_poi.py` | Implement only canonical Layer-6 POI/OF/OB/RB, mitigation, lifecycle, and execution-eligibility semantics. |
| `htf_ltf_synchronization.py` | Synchronize independent timeframe streams and expose only point-in-time HTF context to LTF processing. |
| `dealing_range_history.py` | Reconcile in-memory Dealing Range lifecycle records and apply the per-invocation output-history limit without changing canonical state. |
| `volume_analytics.py` | Calculate optional POI-scoped OHLC/orderflow analytics after canonical POI resolution; never feed results back into structure. |
| `processor.py` | Orchestrate chronological candle processing and cross-layer state flow; it must not redefine layer semantics. |
| `output.py` | Validate and serialize the per-invocation result as JSON or cleartext; performs no file I/O. |

Layer 7 runtime target/RR policy and monitor alert evaluation are not Mapper modules. The Mapper may preserve canonical structural/target-reference facts needed downstream, but it does not resolve runtime targets, apply RR policy, or emit alerts. Layer-8 state/observability requirements are implemented at the relevant module boundaries without creating a competing semantic layer.

The layer modules are new project components, not legacy `*_engine.py` artifacts. The finished product must not import or depend on `smc_htf_ltf_monitor.py`, `smc_analyzer.py`, or legacy engine/test files.

The Monitor launches Market Data and Mapper as separate processes. It passes the validated Market Data machine-readable STDOUT to Mapper STDIN; Mapper processes only records marked `completed=1`. Mapper does not spawn Market Data itself.

## 14.2 Dependency direction

The implementation dependency direction is:

```text
smc_mapper.py
  -> SMC_MAPPER.cli
      -> SMC_MAPPER.period
      -> SMC_MAPPER.market_data_input
      -> SMC_MAPPER.processor
           -> Layer 1 -> Layer 2 -> Layer 3
                -> Layer 4 BOS
                -> Layer 5 CHoCH (with applicable point-in-time HTF context)
                -> Layer 6 POI/execution consumes the applicable canonical outcomes
           -> HTF/LTF synchronization supplies point-in-time context
           -> Dealing Range history reconciliation
           -> optional volume analytics (downstream-only)
      -> SMC_MAPPER.persistence
```

This diagram expresses module responsibility, not a license to bypass canonical state prerequisites. The exact layer-to-layer semantic dependencies remain those defined by `.agents/skills/smc/`. Layer 4 and Layer 5 consume Layer-3-owned structural state without redefining it; Layer 6 consumes canonical structural outcomes without creating them. Result serialization and optional analytics must not feed decisions backward into canonical layers.

Canonical SMC logic must not depend on:

- monitor state;
- provider state;
- current/in-progress market-data snapshots;
- debug output;
- JSON retention policy;
- downstream target/RR policy.

POI volume enrichment may consume canonical POI provenance, but it cannot feed results back into canonical structure.

## 14.3 Domain-state containers

Use explicit state containers for Mapper-owned processing state. Python may use dataclasses for implementation convenience, but the architecture must remain directly reproducible in MQL4/MQL5.

Conceptual models:

    MapperRequest
        symbol
        htf
        ltf
        period
        history_no
        volume_method
        debug
        cleartext

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
        volume_total
        orderflow_buy
        orderflow_sell
        completed

    MarketDataSeries
        symbol
        timeframe
        available_start (derived from returned completed candles)
        available_end (derived from returned completed candles)
        candles: array of MarketDataCandleView

    MapperResult
        symbol
        htf
        ltf
        analysis_mode
        entry_timeframe
        requested_period
        available_coverage
        canonical_processing_coverage
        structural_state
        history

The structural_state and history fields are in-memory ownership containers for canonical layer state and are serialized only into the current invocation's result. Actual canonical objects and fields are taken from `.agents/skills/smc/` during implementation. A transient processing context may include explicit point-in-time inputs such as evaluation time, active HTF context reference, and current completed candle; it must not become persistent state.

## 14.4 MQL4/MQL5 portability

The mapper class contract must be reproducible in both MQL4 and MQL5.

Required portability rules:

- explicit state fields and explicit ownership;
- conceptual arrays of named records instead of Python-only collection semantics;
- no generators, Python Protocol, reflection, metaclasses, dynamic attributes, or properties as correctness dependencies;
- public operations expose explicit success/failure paths;
- UTC timestamps map to MQL datetime semantics;
- canonical field names and meanings remain stable across Python/MQL implementations;
- JSON dictionaries are output representation only;
- Python Decimal is an implementation detail of deterministic arithmetic, not a portable type requirement.

Portability does not require reproducing Python's CLI or JSON library implementation details in MQL. It requires the same domain contracts and state transitions.

---

## 14.5 Cross-file contract ownership

The following contracts have one implementation owner:

- Market Data acquisition, normalization, completion, availability, timeframe catalog, retention and market-data JSON serialization: market_data.py / market_data_specification.md.
- Mapper positional-period parsing, canonical processing orchestration, transient structures state, and STDOUT serialization: smc_mapper.py / this specification.
- Monitor scheduling, process orchestration, current-price/target monitoring and alerting: smc_monitor.py / its implementation contract.

Do not duplicate the Market Data timeframe catalog, provider semantics, candle completion logic, or JSON serialization rules inside the mapper. The mapper may validate and consume them at its boundary, but does not redefine them.

# 15. MAPPER FUNCTION NAMING AND RESPONSIBILITY CONTRACT

The following function boundaries are implementation contracts. Canonical layer-internal helper names are intentionally not prescribed here.

## 15.1 CLI and validation

Owner module: `SMC_MAPPER/cli.py`.

    build_argument_parser() -> parser
    parse_mapper_request(argv) -> MapperRequest
    validate_mapper_request(request) -> success/failure
    parse_period_expression(value) -> PeriodScope

These functions validate mapper CLI semantics only. They must not execute canonical SMC analysis.

## 15.2 Positional period parsing

Owner module: `SMC_MAPPER/period.py`.

    parse_period_expression(value) -> PeriodScope
    resolve_period_scope(period, market_data_coverage, invocation_time) -> ResolvedPeriod

Parsing is deterministic. Open-end periods use one UTC invocation timestamp captured once; open-start periods resolve against the earliest completed candle present in the validated CSV per timeframe. There is no persistent analysis identity or resume-selection behavior.

## 15.3 Market-data boundary

Owner modules: `SMC_MAPPER/market_data_input.py` for protocol parsing/validation; `SMC_MAPPER/period.py` for positional-period parsing and UTC window-boundary normalization.

    parse_market_data_stdout(stream) -> MarketDataSeries
    validate_market_data_stream(series, symbol, requested_timeframes) -> success/failure
    parse_period_expression(period_text) -> PeriodScope
    select_processing_candles(series, timeframe, end_time) -> candle array
    select_output_window_candles(series, timeframe, start_time, end_time) -> candle array

The process-input parser validates the Market Data machine protocol without importing Market Data classes. It groups records by the explicit `timeframe` field.

The Mapper derives `completion_time` deterministically from canonical candle `timestamp` and `timeframe`; it is not a wire field. Requested output-window membership is based on candle interval-start timestamp and half-open UTC boundaries: `start_time <= timestamp < end_time`. Canonical processing selection is independent of the requested start and includes all supplied completed candles through the resolved end. Completion status is checked separately. Available coverage metadata describes completed-candle coverage only, and the current snapshot is excluded from canonical processing.

## 15.4 Output serialization

Owner module: `SMC_MAPPER/output.py`.

    serialize_mapper_result_json(result) -> JSON text
    render_mapper_result_cleartext(result) -> human-readable text

Serialization is an output boundary only. It does not read or write a file. Canonical processing operates on explicit domain models; JSON dictionaries are produced only after the in-memory result has been validated.

## 15.5 Canonical processing

Owner module: `SMC_MAPPER/processor.py` for orchestration; semantic decisions belong to the corresponding `layer*_*.py` owner module.

    process_analysis(analysis, htf_series, ltf_series) -> changed
    process_candle(analysis, candle, htf_context) -> changed

These are orchestration boundaries. The canonical skill is the normative documentation authority, not an importable runtime library. The Layer-1-to-Layer-6 modules implement its rules in executable form and must not create mapper-specific substitutes for BOS, CHoCH, IDM, retracement qualification, Dealing Range, or POI rules. The processor sequences those implementations but does not redefine their semantics.

## 15.6 POI enrichment

Owner module: `SMC_MAPPER/volume_analytics.py`.

    enrich_poi_volume(poi, source_candles, volume_method) -> changed

This function is downstream of canonical POI formation and lifecycle. It cannot create, remove, retype, invalidate, or revive a canonical POI.

## 15.7 Entrypoint

Owner modules:

- `SMC_MAPPER/cli.py` owns `main(argv) -> exit_status`: parse/validate the CLI request, read the supplied machine protocol from STDIN, and call the processing entry point.
- `SMC_MAPPER/processor.py` owns `run(request, market_data_stream) -> MapperResult`: validate the supplied stream, initialize fresh in-memory state, process, and return the validated result without file I/O.
- The root `smc_mapper.py` contains only the import of `SMC_MAPPER.cli.main` and the executable guard.

Normal execution emits exactly one JSON document to STDOUT after successful in-memory processing. With `--cleartext`, it emits the human-readable rendering instead. No Structures JSON is persisted. Market-data input is consumed from STDIN as the validated machine protocol captured from Market Data STDOUT by the Monitor/orchestrator. Mapper diagnostics and errors are emitted only on STDERR according to Section 12; failure must not produce a success result.

---

# 16. RESULT OUTPUT CONTRACT

## 16.1 JSON result

Default successful execution emits exactly one complete JSON document on STDOUT. The result represents only the current invocation and includes symbol, timeframe configuration, normalized requested period, actual per-timeframe available coverage, canonical processing coverage, requested output window, canonical structural results, and applicable provenance/volume analytics.

The JSON document is created from validated in-memory domain state. It is not persisted, re-read, merged with previous output, or treated as a checkpoint. The Mapper does not create `<SYMBOL>_structures.json` or any other output file.

## 16.2 Cleartext result

When `--cleartext` is supplied, STDOUT contains a human-readable rendering of the same successful in-memory result instead of JSON. This is presentation-only and must not change canonical computation or result content. The Monitor must not enable `--cleartext` when it needs machine-readable Mapper output.

## 16.3 Failure behavior

If input validation, coverage validation, canonical processing, or result serialization fails, exit non-zero and emit no successful result to STDOUT. Error details and diagnostics go to STDERR. A failed invocation leaves Market Data's persistent candle cache untouched by the Mapper; only Market Data owns updates to that cache.

## 16.4 Historical recomputation

Historical recomputation is an ordinary invocation with a positional period. The Mapper rebuilds state from all retained completed candles supplied through the requested end, beginning at the earliest candle in each timeframe's returned history, so corrected historical candles automatically affect all downstream structural outcomes. There is no special update command, transaction, checkpoint, old-state preservation, or duplicate-event reconciliation because no previous Mapper state is loaded.

# 17. PURE-FUNCTION AND TESTABILITY BOUNDARIES

Where practical, the following operations must be deterministic/pure with explicit inputs:

- CLI validation after parsing;
- positional-period parsing and window selection;
- point-in-time HTF context selection;
- processing-history and output-window candle selection from the supplied Market Data stream;
- Dealing Range history reconciliation input/output;
- POI volume aggregation;
- OHLC directional-volume calculation;
- JSON serialization of already-resolved state.

Stateful orchestration is allowed only where state mutation is the purpose of the function. Avoid hidden global state, hidden caches that affect correctness, or provider calls from canonical processing.

Tests must be able to execute canonical-processing logic from fixed in-memory candle fixtures without network access or live wall-clock dependence. Period filtering must not truncate canonical history before the requested end.

---

# 18. REQUIRED TEST STRUCTURE AND DEFINITION OF DONE

The global developer-agent naming, portability, prompt-efficiency, and validation rules in `AGENTS.md` apply to the Mapper. Mapper validation scenarios are defined by the implementation contract.

At minimum, the finished mapper implementation must have focused tests covering:

- CLI option parsing requires both HTF and LTF, rejects equal timeframes, and rejects invalid HTF<LTF combinations;
- positional-period parser coverage for date-only, date ranges with independently optional endpoint times, open-start, and open-end forms;
- leading-hyphen positional PERIOD is accepted without requiring an extra `--` delimiter;
- standalone `YYYY.MM.DD@HH:MM` is rejected because a time requires a range hyphen;
- omitted period resolves to the full completed-candle history actually supplied by Market Data;
- UTC parsing, interval-start-based half-open period eligibility, and rejection of a standalone date-time without a range hyphen;
- rejection of current/in-progress candles as canonical input;
- independent HTF/LTF ranges and HTF_CONTEXT_UNAVAILABLE behavior;
- point-in-time HTF context, proving later HTF events do not reinterpret earlier LTF events;
- full recomputation from supplied history yields deterministic output;
- historical candle corrections are reflected in a fresh invocation without reading prior Mapper output;
- insufficient warm-up/context coverage fails closed;
- two-timeframe HTF/LTF overlap is handled by point-in-time completion rules without duplicate events within a single invocation;
- deterministic Dealing Range identity/history reconciliation and history_no retention;
- canonical POI lifecycle pass-through without introducing mapper-specific lifecycle states;
- POI volume provenance and branch separation for NONE/OHLC/ORDERFLOW/BOTH;
- machine-protocol parsing of `volume_total` and the observed orderflow pair, including empty optional fields, rejection of partial orderflow pairs, and no inference from `tick_volume` / `real_volume`;
- `market_data_input.py` parses the fixed CSV header and validates the exact field count and order;
- source-level delta derivation from buy/sell with no persisted candle-level delta dependency;
- deterministic OHLC directional-volume aggregation and zero-volume behavior;
- JSON/cleartext output modes are presentation-exclusive and do not alter canonical computation;
- successful CLI STDOUT is exactly one JSON result by default, or one cleartext rendering with `--cleartext`; diagnostics go only to STDERR; failure emits no success result and returns a non-zero exit status;
- Mapper never creates a Structures JSON file, cache, checkpoint, or other persistent output;
- MQL-portable domain-state behavior independent of Python-specific collection mechanics;
- absence of runtime/import dependencies on legacy modules and Market Data/Monitor modules;
- canonical Layer-1-to-Layer-6 behavior is implemented in separate modules with the ownership defined in §14.1, and no layer module bypasses another layer's canonical prerequisite/state contract.

Definition of done:

- smc_mapper.py implements the contracts in this specification;
- mapper consumes only normalized Market Data machine output and never a concrete provider;
- Market Data persistence remains internal to Market Data; Mapper emits its result only through STDOUT;
- canonical SMC decisions are governed by .agents/skills/smc/;
- Market Data current snapshot never enters canonical structural input;
- no source-level orderflow delta field is required;
- no Structures JSON, Mapper cache, persistent analysis identity, or Mapper checkpoint is created;
- repeated full recomputation is deterministic for identical normalized input and configuration;
- implementation contains no runtime dependency on legacy artifacts;
- focused mapper tests pass without network access;
- the code structure remains directly portable at the class/contract level to both MQL4 and MQL5.

**STATUS: CURRENT IMPLEMENTATION CONTRACT — CROSS-FILE OWNERSHIP RECONCILED**
