# SMC Monitor Specification

**Status:** Current implementation specification.
**Scope:** Functional and implementation specification for the future smc_monitor.py.
**Canonical authority:** .agents/skills/smc/ remains the sole authority for canonical SMC semantics. This document defines runtime orchestration, scheduling, target evaluation, alerting, and process boundaries only.

---

# 0. SCOPE, AUTHORITY, AND RUNTIME BOUNDARIES

## 0.1 Finished-product role

smc_monitor.py is the interactive runtime coordinator for the finished product.

Responsibilities:

1. load selected symbols and explicit HTF/LTF configuration from the Monitor CLI;
2. schedule fresh mapping according to each configured symbol's entry timeframe;
3. plan and request the required Market Data coverage through the standalone process before mapper execution;
4. invoke market_data.py and smc_mapper.py as separate processes;
5. validate the successful Mapper JSON result and retain it in memory;
6. obtain the latest current market reference from a validated Market Data `--current` process result;
7. request Calendar Update Engine work asynchronously when News coverage needs refresh;
8. read validated Calendar facts from the committed local calendar.json snapshot;
9. evaluate downstream News warning policy;
10. evaluate targets/RR/alerts;
11. emit runtime alerts/notifications;
12. maintain transient runtime scheduling, evaluation, and alert-deduplication state;
13. keep symbol and timeframe-configuration execution isolated.

The Monitor is an orchestrator and downstream consumer. It is not a Calendar provider, Update Engine, canonical SMC analyzer, Mapper, POI lifecycle engine, or broker/order-management system.

## 0.2 Ownership boundaries

Canonical SMC semantics:
~~~text
.agents/skills/smc/
~~~

Market Data acquisition, normalization, completion, retention, and persistence:
~~~text
market_data.py
specifications/market_data_specification.md
~~~

Mapper structural processing and Structures persistence:
~~~text
smc_mapper.py
specifications/smc_mapper_specification.md
~~~

Calendar provider acquisition, normalization, coverage, watermarks, deduplication, and calendar.json persistence:
~~~text
calendar.py
specifications/calendar_specification.md
~~~

Monitor scheduling, process orchestration, current-price observation, session context, News warning evaluation, target evaluation, RR policy, alerting, and transient runtime state:
~~~text
smc_monitor.py
specifications/smc_monitor_specification.md
~~~

The Monitor must not create an alternative canonical SMC ontology.

## 0.3 Runtime dependency direction

~~~text
market_data.py
        ├── machine CSV STDOUT ──→ smc_mapper.py
        └── machine CSV STDOUT ──→ smc_monitor.py

smc_mapper.py
        ↓
per-invocation JSON STDOUT (no Structures file)

Calendar Update Engine
        ↓
<DATA_ROOT>/calendar.json
        ↓
smc_monitor.py
~~~

The Monitor may launch Market Data, Mapper, and Calendar subprocesses.

The Monitor must not:

- call a Calendar provider directly;
- invoke provider APIs;
- parse provider HTML/JSON;
- wait for Calendar network completion inside the candle-close critical path;
- write calendar.json;
- invoke legacy monitor/analyzer/engine runtime artifacts;
- write canonical SMC state into Market Data or Structures JSON.

The Monitor reads the Calendar contract only. Market Data and Mapper are consumed through their process-output contracts; no Structures file exists.

# 1. CLI AND INPUT RESOLUTION

## 1.1 build_argument_parser

Signature:

~~~python
def build_argument_parser() -> argparse.ArgumentParser:
    ...
~~~

Approved options:

~~~text
--symbol SYMBOL [SYMBOL ...]
--htf TF
--ltf TF
--rr DECIMAL
--timezone TZ
--alert-json
--debug
--help
~~~

The parser performs no network access and no canonical analysis.

`--timezone` is presentation/reporting timezone only. It must be a valid IANA timezone name. Canonical scheduling, comparisons and session evaluation remain based on canonical UTC; each named trading session continues to use its own configured IANA timezone.

## 1.2 --symbol

At least one symbol is required.

Multiple symbols are allowed. Each symbol is monitored independently.

The Monitor must never merge structures, market data, schedules, targets, or alerts between symbols.

Each symbol uses one dedicated data directory for Market Data and Structures:

~~~text
<DATA_ROOT>/<SYMBOL>/
    <SYMBOL>_marketdata.json
~~~

The single global Calendar data file is:

~~~text
<DATA_ROOT>/calendar.json
~~~

The Monitor automatically resolves the symbol directory from the common data root. It does not expose per-file path CLI options.

## 1.3 --htf and --ltf

The Monitor accepts the same timeframe selection semantics as Mapper:

- at least one of `--htf` or `--ltf` is required;
- if both are supplied and differ, HTF must be strictly higher than LTF;
- if both are equal, use single-timeframe mode and do not treat that timeframe as its own HTF;
- the same configuration applies independently to every selected symbol;
- a different timeframe configuration requires a separate Monitor process;
- these flags configure each fresh Mapper invocation and are not loaded from a file.

## 1.3 --rr

Optional downstream minimum Projected_RR policy.

Rules:

- no default minimum RR;
- when absent, no RR filter is applied;
- when supplied, require Projected_RR >= --rr;
- invalid or non-positive input fails explicitly;
- RR policy must never alter canonical structure, POI lifecycle, target coordinates, or mapper state;
- the supplied value applies only to the current Monitor invocation.

## 1.4 --debug

Diagnostics are written to stderr only.

Debug output must never be:

- parsed as machine data;
- forwarded into Market Data or Mapper input;
- stored in JSON;
- used to change canonical or alert decisions.

Normal successful execution is silent except for actual runtime alerts/notifications.

## 1.5 Process result model

Use an explicit subprocess result container:

~~~python
@dataclass(frozen=True)
class ProcessResult:
    exit_code: int
    stdout: str
    stderr: str
~~~

Rules:

- `stdout` and `stderr` are separate process streams whose interpretation is defined by the invoked component contract;
- for `market_data.py`, `stdout` is the machine-readable candle transport and `stderr` is diagnostics;
- for `smc_mapper.py`, stdout is the per-invocation JSON result by default, while stderr is diagnostics/errors;
- the Monitor may retain process output transiently for validation, diagnostics, or downstream contract handling as defined by the invoked process;
- debug STDERR may be shown on the terminal only;
- no subprocess diagnostic output is persisted as canonical state.

## 1.6 Request model

~~~python
@dataclass(frozen=True)
class MonitorRequest:
    symbols: list[str]
    min_rr: Decimal | None
    timezone: str | None
    alert_json: bool
    debug: bool
~~~

The Monitor's HTF/LTF configuration applies to each selected symbol for this process invocation. At least one timeframe is required; when both are supplied, HTF must be strictly higher. Equal HTF/LTF values resolve to single-timeframe mode. To monitor a different timeframe configuration, run a separate Monitor instance. The Monitor does not infer configuration from persisted analysis files and does not expose a data-path CLI option.

---

# 2. PERSISTED INPUT CONTRACTS

## 2.1 Mapper result STDOUT

There is no Structures JSON file. For each mapping invocation, the Monitor captures Mapper STDOUT as the result of that invocation.

By default, Mapper STDOUT must be exactly one complete JSON result document. The Monitor captures STDOUT and STDERR separately, validates the JSON schema and symbol/timeframe/period metadata, and passes the parsed in-memory result to downstream evaluation. It must not attempt to load or write `<SYMBOL>_structures.json`.

The Monitor must never pass `--cleartext` to Mapper in an invocation whose result is consumed programmatically. Mapper cleartext is a user-facing presentation mode only.

A successful Mapper process result is transient. It is not a durable canonical cache, and the Monitor must not use a previous invocation's result as input to a later Mapper computation.

## 2.2 Market Data process output

Market Data is a standalone process boundary. The Monitor must not open or parse `<SYMBOL>_marketdata.json` as runtime input.

For market-data acquisition and current-reference operations, the Monitor launches `market_data.py` and consumes its machine-readable CSV STDOUT. The Monitor must not use `--cleartext` for this purpose.

The protocol header is:

~~~text
timeframe,time,open,high,low,close,tick_volume,spread,real_volume,volume_total,orderflow_buy,orderflow_sell,completed
~~~

The Monitor may consume completed rows (`completed=1`) for coverage/update decisions and current rows (`completed=0`) for current market reference observation. `volume_total` is the only protocol field used as normalized total-volume input; `orderflow_buy` and `orderflow_sell` are observed orderflow only when both are present. The Monitor must not infer volume fields from `tick_volume` or `real_volume`; current-price observation uses OHLC/price fields and does not require volume analytics.

The Monitor validates the process exit code and machine protocol before using the result. STDERR is diagnostics only. A non-zero Market Data exit blocks the dependent operation.

## 2.3 In-memory result model

Use an explicit immutable view of the result received from Mapper STDOUT, for example:

~~~python
@dataclass(frozen=True)
class MapperResultView:
    symbol: str
    htf: str | None
    ltf: str | None
    analysis_mode: str
    entry_timeframe: str
    requested_period: str | None
    available_coverage: dict[str, tuple[datetime | None, datetime | None]]
    last_completed_candle_time: datetime
    canonical_result: dict[str, object]
~~~

The result exists only in memory for the current runtime cycle. It must not be persisted as a canonical cache or used as the source of the next mapping invocation.

---

# 3. TRANSIENT MAPPING CONTEXT AND SCHEDULING

## 3.1 Runtime configuration

The Monitor obtains its timeframe configuration from its own `--htf` and/or `--ltf` CLI arguments. It applies that same configuration independently to every selected symbol. It does not discover analyses from files, infer timeframe configuration from Market Data, or load a persisted analysis registry.

## 3.2 Runtime registry

Use transient per-symbol scheduling state only:

~~~python
@dataclass
class MonitoredSymbol:
    symbol: str
    analysis_key: str  # transient correlation key: symbol + timeframe configuration; never persisted
    entry_timeframe: str
    htf: str | None
    ltf: str | None
    analysis_mode: str
    last_mapped_candle_time: datetime | None
    next_due_time: datetime | None
    latest_mapper_result: MapperResultView | None
    emitted_alert_keys: set[str]
~~~

The registry exists only in process memory. It is not a durable checkpoint or canonical cache. After restart, the Monitor obtains the latest completed candle from Market Data and recomputes Mapper output when needed.

## 3.3 Runtime invariants

For every monitored symbol:

- one independent symbol and one explicitly configured timeframe combination;
- no shared runtime result across symbols;
- no persisted persistent Mapper checkpoint or runtime analysis correlation identity;
- no mutation of canonical Mapper results;
- every new full Mapper result is produced from Market Data candles, never from the previous Mapper result.

# 4. MARKET-DATA UPDATE ORCHESTRATION

## 4.1 General cycle

~~~text
load explicit Monitor symbol/timeframe configuration
        ↓
plan required Market Data ranges
        ↓
invoke market_data.py
        ↓
consume Market Data machine CSV result
        ↓
check whether a new completed entry-timeframe candle exists
        ↓
invoke Mapper for the configured timeframe combination
        ↓
validate and retain the result in memory
        ↓
refresh current market reference
        ↓
evaluate session context
        ↓
ensure dynamic Calendar News coverage through calendar.py
        ↓
evaluate News warning
        ↓
evaluate targets / RR / alerts
        ↓
schedule next cycle
~~~

The Monitor keeps the validated Market Data CSV result in memory and supplies it to Mapper through STDIN. No intermediate market-data file is introduced. Market Data CSV STDOUT is the machine-readable process boundary; Mapper JSON STDOUT is the transient canonical-result boundary; Calendar JSON remains the Calendar read boundary.

## 4.2 Mapper execution eligibility

The Monitor invokes Mapper when a newly completed entry-timeframe candle is observed compared with the current process's transient `last_mapped_candle_time`, or when no Mapper result exists in the current process and an initial mapping is required.

The transient timestamp is only a scheduling optimization. It is not persisted and is never passed to Mapper as a canonical checkpoint. After restart, the Monitor re-establishes current coverage from Market Data and recomputes a complete Mapper result.

A current-only candle refresh does not trigger canonical Mapper execution.

## 4.3 Market Data planning

Function:

~~~python
def plan_market_data_updates(
    symbols: list[str],
    timeframe_configuration: TimeframeConfiguration,
    market_data_coverage: dict[str, Any],
    now: datetime,
) -> list[MarketDataUpdatePlan]:
    ...
~~~

Model:

~~~python
@dataclass(frozen=True)
class MarketDataUpdatePlan:
    symbol: str
    timeframes: list[str]
    start_time: datetime | None
    end_time: datetime | None
    last_closed_only: bool
~~~

Plan invariants:

- one plan belongs to one symbol and the Monitor's explicit timeframe configuration;
- `timeframes` contains exactly the selected timeframe set: one timeframe in single-timeframe mode or both HTF and LTF in two-timeframe mode;
- `last_closed_only=True` is a latest-completed-candle probe and requires null range boundaries;
- current/in-progress snapshots are handled by the separate current-snapshot path;
- no provider-specific acquisition logic belongs in the Monitor.

Planning rules:

- Market Data's retained cache determines whether a provider update is needed;
- the Monitor uses returned completed-candle coverage to determine whether a fresh Mapper run is due;
- Mapper receives enough retained history for the requested output period plus all required warm-up/context candles;
- in two-timeframe mode, the stream includes all HTF/LTF overlap needed for point-in-time context;
- `-END` historical scopes resolve from each timeframe's earliest retained completed candle, not its latest candle;
- no plan uses a Mapper checkpoint; no durable Mapper checkpoint exists.

## 4.4 No-new-candle path

When no new completed entry-timeframe candle is observed:

- do not invoke Mapper solely for that reason;
- a current-snapshot change may still trigger downstream target/alert evaluation using the current runtime result;
- no checkpoint or persisted Mapper state is changed.

## 4.5 Missed-cycle path

When multiple completed entry-timeframe candles accumulated:

- allow Market Data to update its own candle cache;
- retrieve the complete required history from that cache in one operation when possible;
- invoke Mapper once for the resulting chronological stream;
- evaluate downstream state only from the newly validated Mapper JSON result.

The Monitor must not invoke Mapper once per missed candle unless an explicit implementation limitation requires it.

## 4.6 Calendar / News planning

News acquisition is independent of canonical Mapper processing.

For each monitored symbol/timeframe configuration:

~~~text
base_window = duration(entry_timeframe)

HIGH   -> warning_window = base_window × 2
MEDIUM -> warning_window = base_window
LOW    -> warning_window = base_window ÷ 2
UNKNOWN / HOLIDAY -> no warning
~~~

For future acquisition planning:

~~~text
max_news_horizon =
    max(duration(entry_timeframe) × 2)
~~~

The Monitor plans from the current UTC date through the UTC date containing now + max_news_horizon.

The request uses only explicit Calendar date-range syntax:

~~~text
python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD
~~~

The Calendar Update Engine performs network acquisition in a separate asynchronous process. The Monitor does not wait for provider completion merely to continue Market Data/Mapper processing.

Required planning function:

~~~python
def plan_news_acquisition(
    symbol: str,
    monitored_symbols: list[MonitoredSymbol],
    now: datetime,
) -> tuple[date, date] | None:
    ...
~~~

Rules:

- no direct ForexFactory or Yahoo access from Monitor;
- no provider payload parsing;
- Calendar acquisition failure does not block Market Data/Mapper processing;
- missing, partial, bootstrap-required, or unavailable Calendar state is not canonical failure;
- News evaluation uses only validated normalized Calendar facts;
- News context cannot change persistent Mapper checkpoints or canonical SMC state;
- acquisition is an availability step only; it is never a setup/target/RR gate.

# 5. PROCESS INVOCATION CONTRACT

## 5.1 invoke_market_data

Signature:

~~~python
def invoke_market_data(
    plan: MarketDataUpdatePlan,
    debug: bool = False,
) -> ProcessResult:
    ...
~~~

Launch:

~~~text
python market_data.py ...
~~~

The process result contains exit status, machine CSV STDOUT, and diagnostic STDERR. The machine-readable candle result is the Market Data CSV STDOUT protocol.

When debug is enabled, the Monitor may propagate --debug to market_data.py so provider/process diagnostics remain visible on stderr. It must never parse those diagnostics as data.

The Monitor must parse only the validated Market Data CSV protocol as candle data; it must never parse STDERR diagnostics as data. When the stream is passed to Mapper, pass the validated machine CSV as STDIN without modifying rows or writing an intermediate file; Mapper independently validates the protocol again.

A non-zero exit status blocks dependent mapper execution for the affected data path.

## 5.2 Calendar invocation

Calendar is an asynchronous Update Engine boundary, not a blocking step in the Monitor candle-close path.

Required helper:

~~~python
def request_calendar_update_async(
    symbol: str,
    scope: str,
    debug: bool = False,
) -> None:
    ...
~~~

Allowed launches:

~~~text
python calendar.py SYMBOL YYYY.MM.DD
python calendar.py SYMBOL YYYY.MM.DD-YYYY.MM.DD
python calendar.py SYMBOL YYYY.MM.DD@HH:MM
python calendar.py SYMBOL YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
python calendar.py SYMBOL current
~~~

For planned future News coverage, use an explicit date range.

For incremental refresh, use:

~~~text
python calendar.py SYMBOL current
~~~

`current` requires existing provider+canonical-symbol watermark state. A missing watermark is reported by Calendar as `BOOTSTRAP_REQUIRED`; the Monitor never invents a bootstrap timestamp.

The Monitor starts the Calendar process without waiting for provider/network completion. Calendar owns atomic persistence to `<DATA_ROOT>/calendar.json`.

The Monitor may read the currently committed Calendar snapshot after dispatch.

The Monitor excludes any normalized event whose optional suppressed_for metadata contains the monitored canonical symbol.

The Monitor never:

- calls ForexFactory or Yahoo directly;
- parses provider HTML/JSON;
- waits for Calendar acquisition before continuing canonical processing;
- writes calendar.json;
- uses old relative scopes;
- uses next.

## 5.3 invoke_mapper

Signature:

~~~python
def invoke_mapper(
    symbol: str,
    htf: str | None,
    ltf: str | None,
    period: str | None,
    market_data_stdout: str,
    debug: bool = False,
) -> ProcessResult:
    ...
~~~

Launch:

~~~text
python smc_mapper.py --symbol SYMBOL [--htf HTF] [--ltf LTF] [PERIOD]
                     [--volume-method ...] [--debug]
~~~

The Monitor passes the timeframe configuration from its CLI and the resolved requested period, if any. It passes the validated Market Data machine-output result as Mapper STDIN; Mapper does not launch Market Data itself. The stream must correspond to the requested symbol, timeframe configuration, requested period, and all required canonical warm-up/context history.

The Monitor must not infer timeframe configuration from previous Mapper output, create or change a persistent analysis identity, set or edit Mapper checkpoints, calculate BOS/CHoCH/IDM/retracement/POI lifecycle, or pass `--cleartext` when it expects a machine-readable result.

On success, Mapper STDOUT contains exactly one JSON document. The Monitor captures STDOUT separately from STDERR, parses and validates the result, and never treats STDERR as data. It does not reload or compare a Structures file because none exists.

When debug is enabled, the Monitor may propagate `--debug` so Mapper diagnostics remain visible on STDERR. A non-zero Mapper exit or malformed/mismatched JSON result blocks downstream use of that invocation's result. The Monitor must not fall back to a prior result as if it were newly computed.

## 5.4 Process isolation

Each subprocess receives explicit arguments and the environment required for execution.

stdout/stderr are captured as separate streams and interpreted according to the invoked process contract. Market Data stdout is CSV input for Mapper; Mapper stdout is its per-invocation JSON result. STDERR is diagnostics/errors only and is never parsed as canonical data.

No process may consume another process's debug output as machine data.

## 5.5 Successful result dependency

For downstream evaluation, Mapper success requires a successful process exit, exactly one valid JSON document from STDOUT, required result fields, symbol/timeframe configuration matching the request, and requested-period/coverage metadata consistent with the supplied Market Data stream.

If STDOUT is empty, contains extra non-JSON text, or contains malformed/mismatched JSON, the Monitor treats the invocation as failed and does not use that result for downstream evaluation. No persisted Structures file is loaded or compared. The Monitor does not advance a Mapper checkpoint.

---

# 6. SCHEDULING MODEL

## 6.1 Entry timeframe

Scheduling is driven by the analysis entry timeframe:

- single timeframe: selected timeframe;
- two timeframes: LTF.

HTF is contextual and does not become the mapper scheduling driver.

## 6.2 Polling

Use one operational constant:

~~~text
MONITOR_POLL_INTERVAL_SECONDS
~~~

Its exact V1 value is a Monitor implementation decision.

The Monitor must not execute redundant Mapper processing when no new completed entry-timeframe candle exists.

## 6.3 Due evaluation

Function:

~~~python
def get_due_symbols(
    registry: list[MonitoredSymbol],
    now: datetime,
) -> list[MonitoredSymbol]:
    ...
~~~

Wall-clock scheduling selects when to check. Actual candle completion eligibility comes from Market Data completion_time, not from wall-clock inference alone.

## 6.4 Missed scheduler intervals

A scheduler gap is recovered by range catch-up:

~~~text
scheduled analysis
        ↓
Market Data range catch-up
        ↓
single chronological Mapper update
~~~

## 6.5 Trading-session model

Use an explicit runtime model:

~~~python
@dataclass(frozen=True)
class TradingSession:
    name: str
    timezone_name: str
    local_start: time
    local_end: time
    enabled: bool
~~~

Trading-session awareness is Monitor runtime context, not canonical SMC logic.

The Monitor knows named regional sessions and determines their current status from canonical UTC using explicit IANA timezones and session-local definitions.

V1 named sessions:

~~~text
Sydney  -> Australia/Sydney
Tokyo   -> Asia/Tokyo
London  -> Europe/London
New York -> America/New_York
~~~

Session definitions are represented by one Monitor-owned configuration structure. Each session contains at minimum:

- session name;
- IANA timezone;
- local start time;
- local end time;
- enabled flag.

The implementation must convert canonical UTC to the session timezone and evaluate the local session interval there. It must not encode fixed UTC offsets because London, New York, and Sydney observe daylight-saving changes on different calendars, while Tokyo does not. This is why session definitions use named timezones rather than fixed offsets.

Session status may be:

~~~text
OPEN
CLOSED
~~~

The Monitor may additionally expose overlap information, for example London/New York overlap, as transient runtime context.

Session state is never:

- canonical SMC structure;
- a POI lifecycle state;
- a transient last-mapped candle timestamp;
- a reason to rewrite a historical candle.

Session context may be used for:

- runtime display;
- diagnostics;
- scheduling/reporting;
- future explicitly approved downstream alert/execution policies.

Session context must not alter canonical Mapper calculations.

Function:

~~~python
def get_active_sessions(
    utc_time: datetime,
    session_definitions: list[TradingSession],
) -> list[TradingSession]:
    ...
~~~

The exact session hours are operational policy and have one Monitor-owned definition. They must not be duplicated in Mapper or Market Data specifications.

A scheduler gap is recovered by range catch-up:

~~~text
scheduled analysis
        ↓
Market Data range catch-up
        ↓
single chronological Mapper update
~~~

---

## 6.6 Economic News warning and runtime event-status context

The dynamic warning formula applies only to ForexFactory economic events:

~~~text
HIGH   -> 2 × duration(entry_timeframe)
MEDIUM -> 1 × duration(entry_timeframe)
LOW    -> 0.5 × duration(entry_timeframe)
UNKNOWN / HOLIDAY -> no warning
~~~

Yahoo Finance news is complementary context. It has no normalized Calendar impact contract and is not warning-eligible by default.

The Monitor must not infer Yahoo severity from publisher, headline, URL, category, or source.

Pre-event eligibility remains:

~~~text
0 < (event_time_utc - current_utc) <= warning_window
~~~

Runtime event status remains:

~~~text
UPCOMING
ONGOING
ENDED
~~~

For an economic event:

~~~text
event_end_time = event_time + duration(analysis.entry_timeframe)
~~~

Event-status transitions are transient Monitor observations only. They do not mutate canonical SMC state, POI lifecycle, Mapper checkpoint, or Calendar persistence.

Adding Yahoo-news warning severity requires a separate explicit Monitor specification decision.

# 7. CURRENT MARKET REFERENCE

## 7.1 Source

The Monitor never calls a provider directly.

The current reference price comes from persisted Market Data state.

V1 target-reached observation uses this single current reference price only. It does not infer intrabar touch order, high/low microsequence, or broker execution from OHLC.

Preferred source:

~~~text
latest current snapshot close on the analysis entry timeframe
~~~

If no current snapshot exists:

1. request a current refresh through the Market Data process;
2. reload the persisted current snapshot;
3. if a valid current reference remains unavailable, fail closed for target clearance and alerting.

A stale completed candle close must not silently be relabeled as a live current reference where current reference is required.

## 7.2 CurrentMarketView

~~~python
@dataclass(frozen=True)
class CurrentMarketView:
    symbol: str
    timeframe: str
    price: Decimal | None
    observation_time: datetime | None
    source_candle_id: str | None
~~~

This view is transient.

## 7.3 refresh_current_market_view

~~~python
def refresh_current_market_view(
    symbol: str,
    timeframe: str,
) -> CurrentMarketView:
    ...
~~~

Current refresh must use the Market Data process boundary and consume the current CSV row.

A current snapshot update never advances a persistent Mapper checkpoint.

---

# 8. CANONICAL STATE CONSUMPTION

## 8.1 No semantic reimplementation

The Monitor consumes canonical mapper results.

It must not independently calculate or reclassify:

- IDM;
- IDM_TAKEN;
- CONFIRMED_STRUCTURAL_SWING;
- retracement qualification;
- VALID_BOS;
- CHoCH lifecycle state;
- Dealing Range lifecycle;
- canonical POI lifecycle;
- canonical entry authorization.

When required canonical state is unresolved or unavailable, downstream alerting fails closed.

## 8.2 Entry authorization

If the Mapper exposes canonical ENTRY_AUTHORIZED state under the canonical implementation contract, the Monitor may consume that state.

The Monitor must never convert:

~~~text
ENTRY_AUTHORIZED -> POSITION_OPEN
ENTRY_AUTHORIZED -> ORDER_FILLED
ENTRY_AUTHORIZED -> ORDER_FILLED

The Monitor must preserve the canonical distinction ENTRY_AUTHORIZED != ORDER_SUBMITTED != ORDER_FILLED != POSITION_OPEN.
~~~

Current product behavior remains alert/notification-only.

---

# 9. TARGET REPRESENTATION AND RESOLUTION

## 9.1 Responsibility

Target evaluation is downstream of canonical structure.

The Monitor owns runtime target evaluation, but uses canonical target-coordinate semantics from the applicable canonical downstream contract.

The Monitor must not invent an alternative target hierarchy.

Target provenance remains explicit.

## 9.2 TargetPlan

~~~python
@dataclass(frozen=True)
class TargetPlan:
    symbol: str
    analysis_key: str
    direction: str
    source_poi_id: str | None
    target_type: str | None
    target_coordinate: str | None
    target_price: Decimal | None
    entry_reference_price: Decimal | None
    stop_price: Decimal | None
    provenance: dict[str, Any]
~~~

Exact canonical target types/coordinates are owned by the canonical downstream target contract.

The Monitor may use a transient candidate envelope to carry source-backed target candidates, but this envelope is not a canonical target ontology.

V1 resolves one target per active setup. Target allocation beyond one resolved target is out of scope for the current Monitor product and must not be introduced as an additional runtime target model.

## 9.3 Target principles

Preserve:

- canonical target semantics from the applicable Layer-7 contract;
- target provenance;
- target-plan as runtime architecture, not a canonical SMC ontology.

The Monitor must not assume a universal target-priority ordering, universal countertrend coordinate, or universal RR target.

V1 has no target-policy CLI and no second target configuration file. Therefore:
- if the canonical/downstream state provides exactly one applicable resolved target candidate, the Monitor may use it;
- if multiple applicable candidates exist and no explicit downstream policy resolves one, target resolution returns `None`;
- no candidate may be promoted to the resolved target merely because it is first, nearest, highest-RR, or otherwise convenient.

A target must never be manufactured solely to satisfy RR.

## 9.4 POI eligibility

Target selection is permitted only for POIs that remain eligible under canonical Layer-6 lifecycle.

The Monitor must reject POIs that are not eligible active canonical execution-location objects under Layer 6, including terminal/historical states:

~~~text
POI_FAILURE
POI_INVALIDATION
EXPIRED_HISTORICAL
~~~

POI_MITIGATION must not be reclassified by the Monitor as POI_FAILURE or POI_INVALIDATION; mitigation is a distinct canonical execution lifecycle state. The Monitor does not introduce an age-based freshness rule and must consume the canonical lifecycle result rather than define its own eligibility semantics.

targeted is selection state, not lifecycle state, and is not written to any Structures JSON file.

## 9.5 resolve_target_plan

~~~python
def resolve_target_plan(
    canonical_state: dict[str, Any],
) -> TargetPlan | None:
    ...
~~~

Responsibilities:

1. identify canonical eligible setup context;
2. resolve the applicable downstream target coordinate;
3. preserve target provenance;
4. obtain entry/stop references where canonical downstream state provides them;
5. return None when target resolution is unavailable.

It must not mutate canonical structures.

---

# 10. TARGET CLEARANCE

## 10.1 Separation

Target resolution answers what the target is.

Target clearance answers whether the target is currently beyond price and not already reached.

These are separate operations.

## 10.2 is_target_cleared

~~~python
def is_target_cleared(
    target_price: Decimal | None,
    current_price: Decimal | None,
    direction: str,
) -> bool:
    ...
~~~

V1:

Bullish:
~~~text
target_price > current_price
~~~

Bearish:
~~~text
target_price < current_price
~~~

Equal target/current price is not clear.

Missing target or current price returns false.

## 10.3 Reached target

Target clearance is an entry/setup-side predicate. Target reached is a separate downstream notification event.

~~~python
def is_target_reached(
    target_price: Decimal | None,
    current_price: Decimal | None,
    direction: str,
) -> bool:
    ...
~~~

V1:

~~~text
Bullish: current_price >= target_price
Bearish: current_price <= target_price
~~~

Missing target or current price returns false.

The Monitor must not mutate canonical POI lifecycle because a target has been reached.

## 10.4 Position state

The Monitor must not infer that reaching a target closes a position.

---

# 11. RISK / REWARD POLICY

## 11.1 calculate_projected_rr

~~~python
def calculate_projected_rr(
    target_price: Decimal | None,
    entry_reference_price: Decimal | None,
    stop_price: Decimal | None,
) -> Decimal | None:
    ...
~~~

V1:

~~~text
reward_distance = abs(target_price - entry_reference_price)
risk_distance   = abs(stop_price - entry_reference_price)
Projected_RR    = reward_distance / risk_distance
~~~

Return None when target, entry reference, or stop is missing, or when risk_distance <= 0.

Use deterministic Decimal arithmetic.

## 11.2 RR gate order

~~~text
canonical POI eligibility
        ↓
canonical execution authorization/state
        ↓
target resolution
        ↓
target clearance
        ↓
Projected_RR
        ↓
Projected_RR >= --rr
        ↓
alert eligibility
~~~

RR is checked only after target resolution and clearance.

RR failure never mutates canonical state.

## 11.3 No default RR

No implicit minimum RR is applied when --rr is absent.

---

# 12. ALERT ELIGIBILITY AND NOTIFICATION

## 12.1 Eligibility

~~~python
def evaluate_alert_eligibility(
    result: MapperResultView,
    target: TargetPlan | None,
    current_market_view: CurrentMarketView,
    min_rr: Decimal | None,
) -> AlertDecision:
    ...
~~~

Model:

~~~python
@dataclass(frozen=True)
class AlertDecision:
    alert_type: str
    eligible: bool
    reason: str
    target: TargetPlan | None
    projected_rr_to_resolved_target: Decimal | None
    entry_reference_price: Decimal | None
    stop_price: Decimal | None
    tp1: Decimal | None
    tp2: Decimal | None
    tp3: Decimal | None
    current_price: Decimal | None
    event_id: str | None
    event_time: datetime | None
    event_status: str | None
~~~

SETUP_ELIGIBLE evaluation flow:

~~~text
CANONICAL SETUP/ENTRY STATE
        ↓
TARGET RESOLUTION
        ↓
TARGET CLEARANCE
        ↓
OPTIONAL RR
        ↓
SETUP_ELIGIBLE
~~~

`evaluate_alert_eligibility()` returns `alert_type = SETUP_ELIGIBLE` when eligible.

## 12.2 Alert content and JSON output

Every emitted alert has the same logical detail payload regardless of presentation format.

At minimum, the logical alert detail contains:

- alert type;
- symbol;
- runtime analysis key where applicable;
- direction where applicable;
- canonical setup/entry event reference where available;
- source POI identity where applicable;
- entry reference price when available;
- stop-loss reference when available;
- TP1, TP2 and TP3 when source-backed downstream target-leg levels are available;
- current reference price when available;
- resolved target price and its exact canonical/downstream target type and coordinate when resolved;
- Projected_RR_to_Resolved_Target when calculable;
- News event identity/time/impact/status when the alert is News-related;
- evaluation time.

TP1/TP2/TP3 are presentation fields only. They do not create or modify a target ontology. A level is populated only when the canonical/downstream state already provides a corresponding source-backed target level. Otherwise its value is `null`.

For `SETUP_ELIGIBLE`, the payload may contain entry, SL and available TP levels.

For `TARGET_REACHED`, the resolved target is populated and TP1/TP2/TP3 are populated only when independently source-backed.

For `NEWS_WARNING`, trading levels are `null` unless a separate canonical alert context already provides them; the payload focuses on News details.

The Monitor must never claim that an order was submitted, filled, or a position opened.

### 12.2.1 `--alert-json`

CLI option:

```text
--alert-json
```

When enabled, each emitted alert is written as exactly one complete JSON object to stdout.

The JSON object is the machine-readable alert contract and contains numeric `schema_version: 1` for V1. Human-readable alert text is not mixed into stdout when `--alert-json` is enabled.

Diagnostics, debug output, warnings, and errors remain on stderr.

When `--alert-json` is absent, the existing human-readable alert/notification output is unchanged.

The option changes output representation only. It must not change:

- alert eligibility;
- target resolution;
- target clearance;
- RR evaluation;
- News warning evaluation;
- event-status evaluation;
- deduplication;
- canonical SMC state;
- persistence behavior.

Recommended logical JSON shape:

```json
{
  "schema_version": 1,
  "alert_type": "SETUP_ELIGIBLE",
  "symbol": "EURUSD",
  "analysis_key": "EURUSD|H4|H1|...",
  "direction": "BUY",
  "entry_reference_price": 1.17000,
  "stop_price": 1.16500,
  "tp1": 1.17500,
  "tp2": null,
  "tp3": null,
  "target_price": 1.17500,
  "target_type": "<exact canonical target-source type>",
  "target_coordinate": "<exact canonical target coordinate>",
  "projected_rr_to_resolved_target": 1.0,
  "current_price": 1.16950,
  "event_status": null,
  "event": null,
  "evaluation_time": "2026-10-03T12:30:00Z"
}
```

Field values that are unavailable or not applicable are `null`. The exact JSON numeric serialization follows the Monitor's approved deterministic numeric representation.

### Canonical target vocabulary rule

`target_type` and `target_coordinate` must be copied from the resolved target object exact canonical/downstream terminology. The Monitor must not define a second target taxonomy.

The target representation must preserve the distinction between:

- a canonical target source/candidate;
- a configured target policy;
- the downstream resolved target;
- the target exact coordinate.

Canonical source/candidate terms such as the confirmed external range extreme / external liquidity, policy identifiers such as `HTF_EXTERNAL_TARGET` and `LTF_STRUCTURAL_TARGET`, and setup-specific countertrend destinations are not interchangeable and must not be collapsed into one Monitor-defined `target_type` enum.

**FVG must never be emitted as `target_type` merely because an FVG exists.** FVG is a distinct canonical ontology and an OB validation/property; standalone FVG is not a tradable POI or target.

For the current V1 single-target runtime, `target_price` is the resolved target. `tp1`, `tp2`, and `tp3` are optional presentation slots for already source-backed downstream target legs. They must not cause the Monitor to invent, rank, or split targets.

The JSON output is transient runtime output. It is never written to Calendar, Structures, Market Data, or Monitor persistent state.

The JSON schema must remain stable for downstream automation and should be versioned when its structure changes.

## 12.3 Alert identity and deduplication

Alerts are runtime notifications, not canonical state.

Alert types are explicitly separated:

~~~text
SETUP_ELIGIBLE
TARGET_REACHED
NEWS_WARNING
~~~

`SETUP_ELIGIBLE` is the existing entry/setup notification path and uses target clearance plus optional RR.

`TARGET_REACHED` is a mechanical downstream notification when the resolved target is observed at the current reference price. It does not require target clearance and does not apply the RR gate.

Use a deterministic transient alert identity composed from alert type plus stable setup/target identity, for example:

~~~text
alert_type
+ symbol
+ analysis_key
+ canonical_setup_or_entry_event_id
+ direction
+ target_coordinate
+ target_price
~~~

The Monitor keeps emitted alert identities in `emitted_alert_keys`.

A key is added only after the corresponding notification has been emitted successfully. A failed notification must remain retryable.

Unchanged state must not emit the same alert repeatedly during one Monitor runtime.

Alert history is transient in V1 and is not persisted in a Structures JSON file.

## 12.4 Target-reached evaluation

```python
def evaluate_target_reached(
    target: TargetPlan | None,
    current_market_view: CurrentMarketView,
) -> AlertDecision:
    ...
```

Rules:
- return `alert_type = TARGET_REACHED`;
- return eligible only when a resolved target exists and `is_target_reached(...) == True`;
- never apply target clearance or `--rr`;
- never mutate canonical state.

## 12.5 News warning and event-status evaluation

```python
def calculate_news_warning_window(
    entry_timeframe: str,
    impact: str,
) -> timedelta | None:
    ...
```

The function consumes the existing Market Data timeframe-duration contract and applies:

```text
HIGH   -> 2 × timeframe duration
MEDIUM -> 1 × timeframe duration
LOW    -> 0.5 × timeframe duration
UNKNOWN / HOLIDAY -> None
```

```python
def evaluate_news_warnings(
    result: MapperResultView,
    news_events: list[dict[str, Any]],
    now: datetime,
) -> list[NewsWarningDecision]:
    ...
```

Rules:

- evaluate every candidate event independently;
- calculate the warning window from the analysis entry timeframe and event impact;
- an event is warning-eligible only when `0 < event_time - now <= warning_window`;
- return one decision per eligible event;
- return decisions deterministically sorted by `event_time`, then `event_id`;
- use `PRE_EVENT` only for NEWS_WARNING;
- do not alter setup/target/RR evaluation;
- do not mutate canonical JSON.

NEWS_WARNING identity:

```text
NEWS_WARNING
+ symbol
+ analysis_key
+ event_id
```

Each successful warning notification records its transient identity in `emitted_alert_keys`. A failed notification remains retryable.

### Event status

```python
def evaluate_news_event_status(
    result: MapperResultView,
    event: dict[str, Any],
    now: datetime,
) -> NewsEventStatus:
    ...
```

The runtime observation window is:

```text
event_end_time = event_time + duration(analysis.entry_timeframe)
```

Status:

```text
UPCOMING: now < event_time
ONGOING:  event_time <= now < event_end_time
ENDED:    now >= event_end_time
```

Output transitions:

- first transition into `ONGOING` -> `NEWS_EVENT_STARTED`;
- transition from `ONGOING` to `ENDED` -> `NEWS_EVENT_ENDED`.

A News-related alert emitted during `ONGOING` must expose `event_status = ONGOING`.

Event-status transition identity:

```text
symbol + analysis_key + event_id + status_transition
```

Event-status memory is transient only. It is not written to `calendar.json` or a persistent Structures file.
## 12.6 Re-evaluation

The Monitor may re-evaluate downstream eligibility when current price or another downstream input changes.

A new notification is emitted only for a new alert identity or changed alert identity.

For `TARGET_REACHED`, the event is evaluated from the resolved target and current reference price. It does not require target clearance or the optional RR gate.

Canonical structure is never changed by re-evaluation.

---

# 13. MULTI-SYMBOL AND MULTI-ANALYSIS ISOLATION

## 13.1 Symbol isolation

All runtime state and persisted external-data consumption are symbol-scoped.

No symbol may receive another symbol's market-data, structural, target, or alert state.

## 13.2 Analysis isolation

Each analysis retains:

- independent identity;
- independent transient scheduling state;
- independent entry timeframe;
- independent schedule;
- independent canonical structural state;
- independent target evaluation.

Sharing a market-data file does not imply shared structural state.

## 13.3 One active Monitor per symbol

~~~text
at most one active smc_monitor.py orchestration instance per symbol
~~~

A single Monitor may handle multiple symbols, but concurrent workers must not create two independent writers/orchestrators for the same symbol.

The Monitor serializes orchestration per symbol.

## 13.4 Failure isolation

A failure for one symbol/analysis must not corrupt another symbol/analysis.

A failed symbol cycle produces no usable new Mapper result; unrelated symbols may continue. Any older result still held in memory must not be presented as the fresh result of the failed cycle.

---

# 14. RECOMPUTATION AND PROCESSING GUARANTEES

## 14.1 No durable Mapper checkpoint

Mapper has no persistent checkpoint or Structures file. The Monitor may retain `last_mapped_candle_time` only in transient runtime memory to avoid redundant executions during one process lifetime. It must not serialize that value to disk or treat it as canonical state.

## 14.2 Result validity

A Mapper result is usable only after Mapper exits successfully, STDOUT parses as exactly one JSON document, symbol and timeframe configuration match the request, requested period and available-coverage metadata are valid, and the result includes all required canonical output fields. Process exit alone is not sufficient evidence of a valid result.

## 14.3 Restart and historical correction

After Monitor restart, no Mapper state is restored. The Monitor obtains the latest completed candles from Market Data's cache and recomputes the full Mapper result. If historical candles have changed in the Market Data cache, the new Mapper invocation naturally reflects those corrections.

A failed invocation does not alter the Market Data cache through Mapper. The Monitor may continue unrelated symbols and retry according to its transient retry policy; it must not represent an older in-memory result as a fresh successful computation.

# 15. PERSISTENCE OWNERSHIP

The Monitor does not own a persistent canonical JSON schema and must not read the Market Data persistence JSON. Market Data state used for scheduling is transiently derived from validated process-output records.

## 15.1 Market Data

Only `market_data.py` writes:

~~~text
<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json
~~~

## 15.2 Mapper

Mapper writes no persistent file. Its JSON or cleartext output is emitted only to STDOUT for the current invocation.

## 15.3 Monitor runtime state

Transient only in V1:

- scheduler state;
- current market view;
- latest parsed Mapper result;
- target evaluation result;
- Projected_RR;
- alert decision;
- alert deduplication keys;
- process execution results;
- temporary retry/backoff state;
- last-mapped candle timestamp used only for in-process scheduling.

Do not create a Structures JSON file or a third Monitor JSON file unless the product specification is explicitly expanded.

# 16. ERROR, RETRY, AND FAIL-CLOSED CONTRACT

## 16.1 Error categories

At minimum distinguish:

~~~text
CLI/input error
Mapper JSON STDOUT validation error
market-data machine-output validation error
market-data acquisition/process error
mapper process error
Mapper result-contract validation error
current-price unavailable
target unresolved
target not cleared
RR unresolved
RR policy rejected
calendar/news acquisition error
calendar/news JSON load/validation error
notification error
~~~

Errors identify:

- symbol;
- runtime analysis key where applicable;
- timeframe where applicable;
- concise cause.

## 16.2 Retry

Transient subprocess/file failures may use finite retries.

Retry values are Monitor implementation policy with one owner.

Never retry indefinitely.

Never manufacture:

- candles;
- targets;
- canonical success.

## 16.3 Fail closed

When required canonical or market-data information is unavailable:

~~~text
no alert
~~~

Do not convert:

- unavailable to false canonical fact;
- unresolved to valid;
- stale/current ambiguity to confirmed;
- provider failure to successful empty state.

Canonical state remains unchanged.

---

# 17. PURE-FUNCTION AND IMPLEMENTATION BOUNDARIES

Prefer deterministic functions for:

~~~text
parse_monitor_request
validate_monitor_request
parse_decimal
build_alert_output
build_monitored_symbols
build_market_data_update_plan
get_due_symbols
is_target_cleared
calculate_projected_rr
plan_news_acquisition
calculate_news_warning_window
evaluate_news_warnings
evaluate_news_event_status
build_news_warning_key
build_alert_key
evaluate_alert_eligibility
~~~

Side effects belong in:

~~~text
parse_market_data_stdout
invoke_market_data
request_calendar_update_async
load_calendar_snapshot
invoke_mapper
refresh_current_market_view
emit_alert
run_monitor_cycle
run
main
~~~

Canonical decisions must not depend on alert history, scheduler retries, or debug state.

---

# 18. MQL4/MQL5 PORTABILITY

Portable Monitor domain contracts should use explicit named fields and arrays.

~~~text
MonitorRequest
MonitoredSymbol
CurrentMarketView
TargetPlan
AlertDecision
~~~

Requirements:

- explicit state fields;
- explicit symbol/analysis ownership;
- no dynamic attributes as correctness dependencies;
- no Python-specific reflection or metaprogramming;
- UTC timestamps map to MQL datetime semantics;
- Decimal is a Python arithmetic implementation detail;
- subprocess launching is an OS/runtime-specific implementation detail, not the domain contract.

---

# 19. FUNCTION NAMING AND RESPONSIBILITY CONTRACT

The global developer-agent naming and portability rules are defined in `AGENTS.md`; this section defines Monitor-specific function ownership boundaries.

Required top-level functions:

~~~python
build_argument_parser()
parse_monitor_request(argv)
validate_monitor_request(request)

normalize_symbol(symbol)
parse_decimal(value)


parse_market_data_stdout(stdout, symbol, requested_timeframes)


plan_market_data_updates(symbols, timeframe_configuration, coverage, now)
get_due_symbols(registry, now)

invoke_market_data(plan, debug)
invoke_mapper(symbol, htf, ltf, period, market_data_stdout, debug)

refresh_current_market_view(symbol, timeframe)

request_calendar_update_async
load_calendar_snapshot
calculate_news_warning_window
evaluate_news_warnings(analysis, news_events, now)
build_news_warning_key(analysis_key, event_id)

resolve_target_plan(canonical_state)
is_target_cleared(target_price, current_price, direction)
calculate_projected_rr(target_price, entry_reference_price, stop_price)
get_active_sessions(utc_time, session_definitions)

build_alert_key(analysis, target, alert_type)
build_alert_output(decision)
is_target_reached(target_price, current_price, direction)
evaluate_target_reached(target, current_market_view)
evaluate_alert_eligibility(analysis, target, current_market_view, min_rr)
emit_alert(decision, alert_json)

run_monitor_cycle(request, registry, now)
run(request)
main(argv)
~~~

Each function has one primary responsibility. No function may discover or load persisted Mapper analyses or Structures JSON.

Avoid vague names such as:

~~~text
process_data
handle_monitor
check_everything
manage_setup
do_update
~~~

---

# 20. VARIABLE NAMING CONTRACT

Prefer:

~~~text
request
symbols
analysis
monitored_symbols
analysis_key
entry_timeframe
market_data
market_data_plan
current_market_view
target_plan
target_price
entry_reference_price
stop_price
projected_rr
alert_decision
alert_key
process_result
~~~

Use:

- snake_case for variables/functions;
- PascalCase for classes;
- UPPER_SNAKE_CASE for constants.

---

# 21. IMPLEMENTATION ORDER

## Phase 1 — skeleton

Create:

~~~text
constants
data models
main/run shell
process-result model
~~~

## Phase 2 — CLI and validation

Implement:

~~~text
build_argument_parser
parse_monitor_request
validate_monitor_request
normalize_symbol
parse_decimal
~~~

Verify help, multiple symbols, RR validation, --alert-json output selection, and debug behavior.

## Phase 3 — transient result models

Implement:

~~~text
parse_mapper_json_stdout
validate_mapper_result
build_transient_runtime_key
~~~

## Phase 4 — scheduling and Market Data planning

Implement:

~~~text
get_due_symbols
plan_market_data_updates
~~~

## Phase 5 — subprocess orchestration

Implement:

~~~text
invoke_market_data
invoke_mapper
~~~

Verify the Market Data CSV STDOUT is the machine-readable boundary.

## Phase 6 — current market reference

Implement:

~~~text
refresh_current_market_view
~~~

## Phase 7 — target evaluation

Implement:

~~~text
resolve_target_plan
is_target_cleared
calculate_projected_rr
~~~

Do not redefine canonical target/POI semantics.

## Phase 8 — session context

Implement:

~~~text
get_active_sessions
~~~

Verify DST-aware session handling and non-interference with canonical state.

## Phase 9 — Calendar and News warning

Implement:

```text
request_calendar_update_async
load_calendar_snapshot
calculate_news_warning_window
evaluate_news_warnings
build_news_warning_key
```

Verify:

```text
calendar.json is the sole persistent News store
dynamic warning horizon is derived from each configured symbol's entry timeframe
HIGH/MEDIUM/LOW warning scaling is deterministic
Calendar Update Engine acquisition and Monitor local snapshot read are separate operations
the committed normalized calendar.json snapshot is the machine-readable News boundary
missing calendar data does not block canonical processing
UTC event timing
impact policy
per-analysis/per-event warning evaluation
NEWS_EVENT_STARTED / ONGOING / NEWS_EVENT_ENDED transitions
warning deduplication
no canonical-state mutation
```
## Phase 10 — alerting

Implement:

~~~text
build_alert_key
evaluate_alert_eligibility
emit_alert
~~~

## Phase 11 — full runtime cycle

Implement:

~~~text
run_monitor_cycle
run
main
~~~

Verify:

~~~text
bootstrap
incremental one-candle update
missed multiple-candle update
no-new-candle current-price refresh
multi-symbol isolation
multi-symbol isolation and timeframe-configuration isolation
target clearance
optional RR
alert deduplication
failure isolation
~~~

---

# 22. REQUIRED TEST STRUCTURE

The global developer-agent naming, portability, prompt-efficiency, and validation rules in `AGENTS.md` apply to the Monitor. Monitor validation scenarios are defined by the implementation contract.

Focused tests must cover at minimum.

### CLI

~~~text
test_monitor_requires_symbol
test_monitor_accepts_multiple_symbols
test_monitor_does_not_require_structures_output_directory
test_monitor_uses_global_calendar_data
test_monitor_rr_optional
test_monitor_rejects_invalid_rr
test_monitor_debug_is_terminal_only
test_monitor_alert_json_flag_is_parsed
test_monitor_accepts_timezone
test_monitor_rejects_invalid_timezone
test_local_time_conversion_is_dst_aware
test_local_time_does_not_change_due_evaluation
~~~

### Analysis discovery

~~~text
test_monitor_uses_explicit_timeframe_configuration
test_monitor_does_not_infer_timeframes_from_market_data
test_runtime_mapping_context_is_symbol_isolated
test_transient_last_mapped_time_is_not_persisted
~~~

### Market Data orchestration

~~~text
test_plan_market_data_from_explicit_timeframe_configuration
test_plan_market_data_bootstrap_from_cached_history
test_plan_market_data_separates_symbol_ranges
test_two_timeframe_range_includes_required_htf_ltf_context
test_market_data_plan_contains_only_configured_timeframes
test_no_new_completed_candle_skips_mapper
test_missed_multiple_candles_use_one_full_recompute
test_current_snapshot_refresh_does_not_trigger_mapper
~~~

### Process boundary

~~~text
test_invoke_market_data_consumes_machine_stdout
test_invoke_mapper_passes_market_data_stdout_to_stdin
test_invoke_mapper_parses_json_stdout
test_invoke_mapper_validates_result_metadata
test_invoke_mapper_never_reads_structures_file
test_failed_market_data_blocks_dependent_mapper
test_failed_mapper_result_is_not_used_for_downstream_evaluation
~~~

### Calendar / News warning

~~~
test_monitor_calendar_snapshot_read_does_not_call_provider
test_calendar_bounded_query_ensures_requested_coverage
test_calendar_empty_interval_is_valid
test_calendar_provider_failure_is_not_empty_success
test_calendar_symbol_filters_currency_events
test_calendar_query_returns_machine_readable_json
test_calendar_missing_data_does_not_block_canonical_alert
test_plan_news_acquisition_uses_dynamic_warning_horizon
test_news_warning_dynamic_pre_event
test_news_warning_dynamic_window_boundary
test_news_warning_impact_timeframe_scaling
test_news_warning_identity_is_deterministic_per_analysis
test_news_warning_failed_notification_is_retryable
test_news_event_started_output
test_news_event_ongoing_status
test_news_event_ended_output
test_news_event_status_is_transient
test_news_warning_does_not_mutate_canonical_state
~~~

### Current market reference

~~~text
test_current_market_view_uses_current_snapshot
test_current_market_view_refreshes_via_market_data
test_missing_current_price_fails_closed
test_current_snapshot_never_enters_mapper_input
~~~

### Target

~~~text
test_target_plan_preserves_provenance
test_target_resolution_does_not_create_canonical_poi
test_target_clearance_bullish_requires_target_above_price
test_target_clearance_bearish_requires_target_below_price
test_target_equal_to_current_price_is_not_clear
test_missing_target_fails_closed
~~~

### RR

~~~text
test_projected_rr_calculation
test_projected_rr_missing_inputs_is_unresolved
test_rr_gate_is_applied_after_target_clearance
test_rr_failure_does_not_mutate_canonical_state
test_no_rr_filter_when_option_absent
~~~

### Alerts

~~~text
test_alert_eligibility_requires_target_clearance
test_alert_eligibility_with_rr
test_session_status_uses_named_timezone
test_session_status_handles_dst_transition
test_session_context_does_not_change_canonical_state
test_alert_identity_is_deterministic
test_failed_notification_is_retryable
test_unchanged_alert_is_not_repeated
test_target_reached_is_directional
test_target_reached_does_not_use_rr_gate
test_resolve_target_plan_does_not_use_current_price
test_mapper_invocation_passes_positional_period
test_monitor_restart_resets_transient_alert_memory
test_alert_does_not_claim_position_open
~~~

### Isolation and persistence

~~~text
test_symbol_isolation
test_analysis_isolation
test_monitor_serializes_symbol_orchestration
test_mapper_result_is_not_persisted_by_monitor
test_monitor_does_not_write_market_data_json
test_mapper_json_stdout_validation_is_required_before_downstream_evaluation
~~~

Core Monitor tests must not require live provider access. Provider/process behavior should use doubles.

---

# 23. DEVELOPER-AGENT RULES

Do not:

- implement canonical SMC rules inside the Monitor;
- create a Monitor-specific POI lifecycle;
- create a second target ontology;
- create a Mapper checkpoint or persistent Structures cache;
- write directly to either JSON store;
- parse any non-contract stdout as candle data;
- call provider APIs directly;
- use current candles as canonical mapper input;
- infer timeframe configuration from Market Data or previous Mapper output;
- automatically buy, sell, submit orders, or manage positions;
- silently downgrade missing canonical/context information;
- manufacture targets to satisfy RR;
- introduce a default minimum RR.

When an implementation decision is not specified here, choose the smallest direct implementation that preserves the existing external contracts and document the decision in AGENT_REVIEW.md.

After implementation, update AGENT_REVIEW.md with the completed audit/test result before committing.

---

# 24. NORMATIVE RUNTIME FLOW

~~~text
CLI
 ↓
MonitorRequest
 ↓
validate input
 ↓
load selected symbols / analyses
 ↓
plan Market Data coverage
 ↓
invoke market_data.py
 ↓
consume validated Market Data machine output
 ↓
invoke affected Mapper analyses
 ↓
reload Structures
 ↓
refresh current market reference
 ↓
plan News acquisition horizon
 ↓
launch Calendar Update Engine asynchronously when required
 ↓
read committed calendar.json snapshot
 ↓
evaluate News status / warning
 ↓
resolve target / RR / alerts
 ↓
schedule next evaluation
~~~

Calendar acquisition may still be running while canonical downstream evaluation continues.

A Calendar failure never blocks canonical Market Data/Mapper processing.

# 25. DEFINITION OF DONE

smc_monitor.py is implementation-complete when:

- the documented Monitor CLI and existing runtime contracts remain intact;
- Calendar Update Engine work is launched asynchronously;
- no Calendar provider is called from Monitor;
- no Calendar provider payload is parsed from Monitor;
- no old Calendar relative scope is referenced;
- next is not referenced;
- current is understood only as provider+canonical-symbol watermark-based incremental update;
- Monitor reads only validated committed calendar.json;
- missing/partial/bootstrap-required/unavailable Calendar data never blocks canonical Market Data/Mapper processing;
- Yahoo news has no invented warning severity;
- dynamic News warning scaling remains limited to ForexFactory economic events;
- News event-status observations remain informational and transient;
- target, RR, alert, session, stateless-recomputation, portability, and process-isolation contracts remain intact.

STATUS: CURRENT IMPLEMENTATION CONTRACT — CALENDAR UPDATE ENGINE BOUNDARY RECONCILED

