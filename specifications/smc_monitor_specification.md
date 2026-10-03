# SMC Monitor Specification

**Status:** Current implementation specification.
**Scope:** Functional and implementation specification for the future smc_monitor.py.
**Canonical authority:** .agents/skills/smc/ remains the sole authority for canonical SMC semantics. This document defines runtime orchestration, scheduling, target evaluation, alerting, and process boundaries only.

---

# 0. SCOPE, AUTHORITY, AND RUNTIME BOUNDARIES

## 0.1 Finished-product role

smc_monitor.py is the interactive runtime coordinator for the finished product.

Responsibilities:

1. load selected symbols and all stored mapper analyses for those symbols;
2. schedule analysis updates according to each analysis entry timeframe;
3. ensure required persisted market-data coverage exists before mapper execution;
4. invoke market_data.py and smc_mapper.py as separate processes;
5. reload persisted state after each successful mapper update;
6. obtain the latest current market reference from persisted Market Data current state;
7. evaluate downstream target eligibility and optional minimum RR policy;
8. emit runtime alerts/notifications;
9. maintain transient runtime scheduling, evaluation, and alert-deduplication state;
10. keep symbol and analysis execution isolated.

The Monitor is an orchestrator and downstream consumer. It is not a provider, canonical SMC analyzer, mapper, POI lifecycle engine, or broker/order-management system.

## 0.2 Ownership boundaries

Canonical SMC semantics:
~~~text
.agents/skills/smc/
~~~

Market Data acquisition, normalization, completion, retention, and market-data JSON persistence:
~~~text
market_data.py
specifications/market_data_specification.md
~~~

Mapper analysis identity, canonical structural processing, structural state, canonical POI lifecycle, and structures JSON persistence:
~~~text
smc_mapper.py
specifications/smc_mapper_specification.md
~~~

Economic calendar acquisition, normalization, shared cache, and Calendar query result persistence:
~~~text
calendar.py
specifications/calendar_specification.md
~~~

Monitor scheduling, process orchestration, current-price observation, session context, News warning evaluation, target evaluation, RR policy, alerting, and transient runtime state:
~~~text
smc_monitor.py
specifications/smc_monitor_specification.md
~~~

The Monitor must not create an alternative canonical ontology for structure, POIs, lifecycle, BOS, CHoCH, IDM, Dealing Range, retracement, or targeting.

## 0.3 Runtime dependency direction

~~~text
market_data.py
        ↓
<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json
        ↓
smc_mapper.py
        ↓
<DATA_ROOT>/<SYMBOL>/<SYMBOL>_structures.json

calendar.py
        ↓
<DATA_ROOT>/calendar.json
        ↓
smc_monitor.py
~~~

The Monitor may launch Market Data and Mapper as subprocesses.

The Monitor must not:

- call a concrete provider directly;
- invoke provider APIs;
- import market_data.py for provider access;
- invoke legacy smc_htf_ltf_monitor.py, smc_analyzer.py, or old engine modules;
- write canonical SMC state into either JSON store;
- reinterpret canonical POI lifecycle;
- modify mapper checkpoints directly;
- use current/in-progress candles as canonical structural input.

The Monitor may read both persisted JSON stores as external contracts and may invoke the owning processes.

## 0.4 Legacy artifacts

smc_htf_ltf_monitor.py, smc_analyzer.py, and old engine/test artifacts are extraction-only source material.

The finished Monitor must not retain runtime, import, schema, or behavioral dependencies on those artifacts.

---

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
--rr DECIMAL
--timezone TZ
--debug
--help
~~~

The parser performs no network access and no canonical analysis.

`--timezone` is presentation/reporting timezone only. It must be a valid IANA timezone name. Canonical scheduling, comparisons, checkpoints and session evaluation remain based on canonical UTC; each named trading session continues to use its own configured IANA timezone.

## 1.2 --symbol

At least one symbol is required.

Multiple symbols are allowed. Each symbol is monitored independently.

The Monitor must never merge structures, market data, schedules, checkpoints, targets, or alerts between symbols.

Each symbol uses one dedicated data directory for Market Data and Structures:

~~~text
<DATA_ROOT>/<SYMBOL>/
    <SYMBOL>_marketdata.json
    <SYMBOL>_structures.json
~~~

The single global Calendar data file is:

~~~text
<DATA_ROOT>/calendar.json
~~~

The Monitor automatically resolves the symbol directory from the common data root. It does not expose per-file path CLI options.

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

- stdout and stderr are diagnostics/process output, never candle-data transport;
- the Monitor may retain them transiently for diagnostics/error reporting;
- debug stderr may be shown on the terminal only;
- no subprocess output is persisted as canonical state.

## 1.6 Request model

~~~python
@dataclass(frozen=True)
class MonitorRequest:
    symbols: list[str]
    min_rr: Decimal | None
    timezone: str | None
    debug: bool
~~~

The request contains no HTF/LTF configuration because the Monitor does not create analyses. The existing common data root is unchanged; the Monitor automatically derives the symbol subdirectory from the selected normalized symbol and does not expose a data-path CLI option.

---

# 2. PERSISTED INPUT CONTRACTS

## 2.1 Structures JSON

For each selected symbol, load:

~~~text
<DATA_ROOT>/<SYMBOL>/<SYMBOL>_structures.json
~~~

Validate at minimum:

- symbol identity;
- analysis key;
- htf;
- ltf;
- analysis_mode;
- entry_timeframe;
- required `analysis_start`;
- requested_start provenance where present;
- last_processed_candle_time;
- canonical structural state required for downstream evaluation.

The Monitor must preserve:

~~~text
canonical structure
implementation checkpoint
transient monitor state
~~~

The Monitor never modifies last_processed_candle_time.

Mapper remains the sole structures writer.

## 2.2 Market Data JSON

For each selected symbol, load:

~~~text
<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json
~~~

The Monitor may consume:

- completed candle coverage;
- completed candle timestamps;
- timeframe availability;
- current in-progress snapshot;
- current snapshot OHLC/volume where needed for current reference observation.

The current snapshot is never canonical structural input.

Market Data JSON serialization remains owned by market_data.py.

## 2.3 Read-only consumer model

Use explicit read-only view models at the file boundary.

~~~python
@dataclass(frozen=True)
class StoredAnalysisView:
    symbol: str
    analysis_key: str
    htf: str | None
    ltf: str | None
    analysis_mode: str
    entry_timeframe: str
    analysis_start: datetime
    requested_start: datetime | None
    last_processed_candle_time: datetime | None
~~~

Additional canonical-state views may be added for downstream evaluation.

The Monitor must not create a second persistent canonical representation.

---

# 3. ANALYSIS DISCOVERY AND RUNTIME REGISTRY

## 3.1 Stored analysis discovery

Load all stored analyses for every requested symbol.

The Monitor does not infer analyses from:

- symbol input;
- RR input;
- current price;
- Market Data timeframes;
- legacy monitor state.

If a selected symbol has no stored analyses, the Monitor performs no configuration inference. It may report the condition under debug and continue with other symbols.

## 3.2 Runtime registry

Use transient runtime scheduling state:

~~~python
@dataclass
class MonitoredAnalysis:
    symbol: str
    analysis_key: str
    entry_timeframe: str
    htf: str | None
    ltf: str | None
    analysis_mode: str
    last_checkpoint: datetime | None
    next_due_time: datetime | None
    emitted_alert_keys: set[str]
~~~

This registry is not persisted.

After mapper completion, reload the structures JSON and refresh the relevant runtime record.

## 3.3 Registry invariants

For every monitored analysis:

- one symbol;
- one deterministic analysis key;
- one entry timeframe;
- one independent checkpoint;
- no shared checkpoint;
- no runtime mutation of canonical structure.

---

# 4. MARKET-DATA UPDATE ORCHESTRATION

## 4.1 General cycle

~~~text
discover/load stored analyses
        ↓
plan required Market Data ranges
        ↓
invoke market_data.py
        ↓
reload persisted market-data state
        ↓
identify analyses requiring mapper update
        ↓
invoke affected mapper analyses
        ↓
reload structures state
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

Persisted JSON files are the machine-readable process boundary.

## 4.2 Analysis update eligibility

An analysis requires mapper execution when:

- new completed entry-timeframe candles exist after its durable checkpoint; or
- the analysis has no valid checkpoint and bootstrap processing is required.

A current-only change does not require canonical mapper execution.

## 4.3 Market Data planning

Function:

~~~python
def plan_market_data_updates(
    analysis_views: list[StoredAnalysisView],
    market_data: dict[str, Any],
    now: datetime,
) -> list[MarketDataUpdatePlan]:
    ...
~~~

Model:

~~~python
@dataclass(frozen=True)
class MarketDataUpdatePlan:
    symbol: str
    timeframe: str
    start_time: datetime | None
    end_time: datetime | None
    last_candle_only: bool
    live: bool
~~~

Rules:

- entry-timeframe coverage extends through all missing completed candles after the durable checkpoint;
- two-timeframe analyses may require HTF updates;
- bootstrap uses the persisted `analysis_start` plus canonical warm-up needs;
- current-price monitoring may request live current snapshots;
- no provider-specific acquisition logic belongs here.

Compatible requests may be grouped for efficiency. Incompatible ranges must be issued separately rather than being silently widened or narrowed.

Function:

~~~python
## 4.4 No-new-candle path

When no completed candle changed:

- do not invoke Mapper solely for that reason;
- a current-snapshot change may still trigger downstream target/alert evaluation;
- the mapper checkpoint does not change.

## 4.5 Missed-cycle path

When multiple completed entry-timeframe candles accumulated:

- retrieve the required range in one Market Data operation when possible;
- invoke Mapper once for the resulting chronological range;
- rely on the Mapper's durable checkpoint after atomic persistence;
- evaluate downstream state only from the updated persisted structures state.

The Monitor must not invoke the Mapper once per missed candle unless an explicit implementation limitation requires it.

---

## 4.6 Calendar / News planning

News acquisition is independent of canonical Mapper processing.

The Monitor derives its future News acquisition horizon from the stored analyses' entry timeframes. It does not use a fixed minute-based warning horizon or a warning-window lookup table.

For each analysis:

```text
base_window = duration(entry_timeframe)

HIGH   -> warning_window = base_window × 2
MEDIUM -> warning_window = base_window
LOW    -> warning_window = base_window ÷ 2
UNKNOWN / HOLIDAY -> no warning
```

For acquisition planning, use the maximum possible eligible horizon across the selected analyses:

```text
max_news_horizon =
    max(duration(entry_timeframe) × 2)
```

Request Calendar coverage from the current UTC date through the UTC date containing `now + max_news_horizon`.

The Calendar layer owns coverage validation and redundant-download avoidance.

The exact timeframe duration comes from the existing Market Data timeframe-duration contract. The Monitor must not introduce a second hard-coded timeframe-duration table.

Required planning function:

```python
def plan_news_acquisition(
    symbol: str,
    analysis_views: list[StoredAnalysisView],
    now: datetime,
) -> tuple[date, date] | None:
    ...
```

Rules:

- no ForexFactory access from Monitor code;
- no HTML or provider-response parsing in Monitor;
- Calendar acquisition failure does not block Market Data/Mapper processing;
- missing `calendar.json` is a normal no-data condition;
- valid empty Calendar query results are distinct from Calendar-unavailable errors;
- News warning evaluation occurs only from validated normalized Calendar query results;
- News context cannot advance or alter the Mapper checkpoint;
- the acquisition date range is operationally rounded outward to whole UTC dates because the Calendar acquisition CLI uses date ranges;
- News acquisition is only a data-availability step; it never becomes a canonical setup/target/RR gate.
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

The process result contains exit status plus diagnostics. The machine-readable result is persisted market-data JSON.

When debug is enabled, the Monitor may propagate --debug to market_data.py so provider/process diagnostics remain visible on stderr. It must never parse those diagnostics as data.

The Monitor must never parse stdout as candle data.

A non-zero exit status blocks dependent mapper execution for the affected data path.

## 5.2 Calendar invocation

Use separate acquisition and local-query process boundaries.

### Calendar acquisition

```python
def invoke_calendar_acquisition(
    symbol: str,
    start_date: date,
    end_date: date,
    debug: bool = False,
) -> ProcessResult:
    ...
```

Launch:

```text
python calendar.py --query SYMBOL --range YYYY.MM.DD-YYYY.MM.DD [--debug]
```

Rules:

- the Monitor never calls ForexFactory directly;
- the date range is derived from the dynamic News warning horizon;
- acquisition may update the single global `<DATA_ROOT>/calendar.json`;
- a non-zero exit is a News acquisition failure for that cycle;
- an acquisition failure does not block canonical Market Data/Mapper processing.

### Calendar local query

```python
def invoke_calendar_query(
    symbol: str,
    mode: str,
    debug: bool = False,
) -> ProcessResult:
    ...
```

Launch:

```text
python calendar.py --symbol SYMBOL --current [--debug]
python calendar.py --symbol SYMBOL --next [--debug]
```

The local query API is network-free and reads only the global `calendar.json`.

For these Calendar query invocations:

- stdout is the machine-readable JSON result;
- stderr remains diagnostics only;
- the Monitor validates the returned schema before News warning evaluation;
- `NO_CALENDAR_DATA` and `NO_RELEVANT_EVENT` are valid non-error query results.

The Monitor decides whether it needs `--current`, `--next`, or both. Calendar performs only the requested time-based event search.

The Monitor never writes `calendar.json`.
## 5.3 invoke_mapper

Signature:

~~~python
def invoke_mapper(
    analysis: StoredAnalysisView,
    end_time: datetime,
    debug: bool = False,
) -> ProcessResult:
    ...
~~~

Launch:

~~~text
python smc_mapper.py --symbol SYMBOL [--htf HTF] [--ltf LTF]
                     --starttime ANALYSIS_START
                     --endtime END_TIME
                     [--volume-method ...] [--debug]
~~~

The Monitor must pass the stored timeframe configuration, the persisted `analysis_start`, and the resolved operational `end_time`. It must always pass `--starttime analysis_start` so the intended stored analysis is selected deterministically when multiple analyses share the same timeframe configuration. The Monitor does not pass `effective_start` because that is an execution-window concept.

The Monitor must not:

- generate alternate HTF/LTF configuration;
- change analysis identity;
- set or edit mapper checkpoints;
- calculate BOS, CHoCH, IDM, retracement, or POI lifecycle.

The machine-readable result is the persisted structures JSON.

When debug is enabled, the Monitor may propagate --debug to smc_mapper.py so mapper diagnostics remain visible on stderr. It must never parse those diagnostics as data.

A non-zero mapper exit status prevents downstream use of a newer structural state for that analysis. The last successfully persisted state remains authoritative.

## 5.4 Process isolation

Each subprocess receives explicit arguments and the environment required for execution.

stdout/stderr remain diagnostics/process output only.

No process may consume another process's debug output as machine data.

## 5.5 Successful persistence dependency

For downstream evaluation, Mapper success requires:

1. successful process exit;
2. valid reload of the expected structures JSON;
3. presence of the relevant analysis entry;
4. a checkpoint consistent with the completed candles the Mapper incorporated.

The Monitor does not independently advance checkpoint state.

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
def get_due_analyses(
    registry: list[MonitoredAnalysis],
    now: datetime,
) -> list[MonitoredAnalysis]:
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
- a mapper checkpoint;
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

## 6.6 Economic News warning context

News warning evaluation is per monitored analysis and per eligible event.

For each candidate event:

```text
base_window = duration(analysis.entry_timeframe)

HIGH   -> warning_window = base_window × 2
MEDIUM -> warning_window = base_window
LOW    -> warning_window = base_window ÷ 2
UNKNOWN / HOLIDAY -> no warning
```

Eligibility is strictly pre-event:

```text
0 < (event_time_utc - current_utc) <= warning_window
```

There is no Calendar-defined "active" or "post-event" lifecycle. Calendar supplies timestamped facts; the Monitor decides whether the current/next event falls inside the dynamic warning window.

Required model:

```python
@dataclass(frozen=True)
class NewsWarningDecision:
    alert_type: str
    eligible: bool
    warning_phase: str
    event_id: str | None
    symbol: str
    analysis_key: str
    event_time: datetime | None
    warning_window: timedelta | None
    minutes_to_event: Decimal | None
    reason: str
```

`warning_phase` is `PRE_EVENT` for an eligible warning and `NO_WARNING` otherwise.

Rules:

- evaluate each eligible event independently;
- apply explicit Monitor impact policy before dynamic window calculation when configured;
- use canonical UTC for event time and current time;
- do not infer event duration, intrabar timing, or trade impact;
- do not alter canonical setup/target/RR state;
- do not mutate canonical JSON.

The dynamic warning window is transient and is never persisted as canonical state.
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

Current refresh must use the Market Data process/JSON boundary.

A current snapshot update never advances a mapper checkpoint.

---

# 8. CANONICAL STATE CONSUMPTION

## 8.1 No semantic reimplementation

The Monitor consumes canonical mapper results.

It must not independently calculate or reclassify:

- IDM;
- IDM_TAKEN;
- structural swing;
- retracement qualification;
- VALID_BOS;
- CHoCH;
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
ENTRY_CONTEXT_VALID -> ORDER_FILLED
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

The Monitor must reject canonical terminal/historical POIs, including representations equivalent to:

~~~text
POI_MITIGATION
POI_FAILURE
POI_INVALIDATION
EXPIRED_HISTORICAL
~~~

The Monitor does not introduce an age-based freshness rule.

targeted is selection state, not lifecycle state, and is not written to structures JSON by the Monitor.

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
    analysis: StoredAnalysisView,
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
    projected_rr: Decimal | None
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

## 12.2 Alert content

Alert payloads must include the alert type.

At minimum:

- symbol;
- analysis key;
- direction;
- canonical setup/entry event reference where available;
- source POI identity where applicable;
- entry reference price;
- stop reference when available;
- resolved target price;
- target coordinate/type;
- projected RR when calculable;
- evaluation time.

The Monitor must not claim that an order was submitted, filled, or a position opened.

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

Alert history is not persisted in structures JSON V1.

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

## 12.5 News warning evaluation

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
    analysis: StoredAnalysisView,
    news_events: list[dict[str, Any]],
    now: datetime,
) -> list[NewsWarningDecision]:
    ...
```

Rules:

- evaluate every candidate event independently;
- calculate the warning window from the analysis entry timeframe and event impact;
- an event is eligible only when `0 < event_time - now <= warning_window`;
- return one decision per eligible event;
- return decisions deterministically sorted by `event_time`, then `event_id`;
- use `PRE_EVENT` only; there is no Calendar-defined EVENT_ACTIVE or POST_EVENT state;
- do not infer intrabar event timing, event duration, or trade impact;
- do not alter setup/target/RR evaluation;
- do not mutate canonical JSON.

NEWS_WARNING identity:

```text
NEWS_WARNING
+ symbol
+ analysis_key
+ event_id
```

Each successful notification records its transient identity in `emitted_alert_keys`. A failed notification remains retryable.
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
- independent checkpoint;
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

A failed analysis keeps its last successfully persisted canonical state while unrelated work may continue.

---

# 14. CHECKPOINT AND PROCESSING GUARANTEES

## 14.1 Checkpoint owner

The Mapper owns:

~~~text
last_processed_candle_time
~~~

The Monitor reads it only.

The Monitor never increments, decrements, rewrites, or fabricates it.

## 14.2 Durable checkpoint rule

The Monitor considers a Mapper update durable only after the Mapper has:

1. processed eligible completed candles;
2. atomically persisted the structures JSON;
3. advanced its own checkpoint inside that persistence transaction.

Process exit alone is not sufficient evidence of durable checkpoint advancement.

## 14.3 Backward range inconsistency

When a persisted checkpoint is later than the requested operational end boundary:

- do not process backward;
- do not rewrite checkpoint;
- surface the inconsistency;
- invoke Mapper only under a valid boundary.

---

# 15. PERSISTENCE OWNERSHIP

The Monitor does not own any persistent JSON schema.

## 15.1 Market Data

Only market_data.py writes:

~~~text
<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json
~~~

## 15.2 Structures

Only smc_mapper.py writes:

~~~text
<DATA_ROOT>/<SYMBOL>/<SYMBOL>_structures.json
~~~

## 15.3 Monitor runtime state

Transient only in V1:

- scheduler state;
- current market view;
- target evaluation result;
- Projected_RR;
- alert decision;
- alert deduplication keys;
- process execution results;
- temporary retry/backoff state.

Do not create a third Monitor JSON file unless the product specification is explicitly expanded.

---

# 16. ERROR, RETRY, AND FAIL-CLOSED CONTRACT

## 16.1 Error categories

At minimum distinguish:

~~~text
CLI/input error
structures JSON load/validation error
market-data JSON load/validation error
market-data acquisition/process error
mapper process error
mapper persistence/contract validation error
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
- analysis key where applicable;
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
discover_analysis_views
build_market_data_update_plan
get_due_analyses
is_target_cleared
calculate_projected_rr
extract_news_events
evaluate_news_warnings
build_news_warning_key
build_alert_key
evaluate_alert_eligibility
~~~

Side effects belong in:

~~~text
load_structures
load_market_data
invoke_market_data
invoke_calendar
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
MonitoredAnalysis
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

Required top-level functions:

~~~python
build_argument_parser()
parse_monitor_request(argv)
validate_monitor_request(request)

normalize_symbol(symbol)
parse_decimal(value)

get_symbol_data_directory(symbol, data_directory)
get_market_data_path(symbol, data_directory)
get_structures_path(symbol, data_directory)

load_structures(path, symbol)
load_market_data(path, symbol)

discover_analysis_views(structures)
validate_analysis_view(analysis)

plan_market_data_updates(analysis_views, market_data, now)
get_due_analyses(registry, now)

invoke_market_data(plan, debug)
invoke_mapper(analysis, end_time, debug)

refresh_current_market_view(symbol, timeframe)

invoke_calendar_acquisition
invoke_calendar_query
calculate_news_warning_window
evaluate_news_warnings(symbol, news_events, now)
build_news_warning_key(symbol, event_id, warning_phase)

resolve_target_plan(canonical_state)
is_target_cleared(target_price, current_price, direction)
calculate_projected_rr(target_price, entry_reference_price, stop_price)
get_active_sessions(utc_time, session_definitions)

build_alert_key(analysis, target, alert_type)
is_target_reached(target_price, current_price, direction)
evaluate_target_reached(target, current_market_view)
evaluate_alert_eligibility(analysis, target, current_market_view, min_rr)
emit_alert(decision)

run_monitor_cycle(request, registry, now)
run(request)
main(argv)
~~~

Each function has one primary responsibility.

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
analysis_views
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

Verify help, multiple symbols, RR validation, and debug behavior.

## Phase 3 — persisted readers

Implement:

~~~text
load_structures
load_market_data
discover_analysis_views
validate_analysis_view
~~~

## Phase 4 — scheduling and Market Data planning

Implement:

~~~text
get_due_analyses
plan_market_data_updates
~~~

## Phase 5 — subprocess orchestration

Implement:

~~~text
invoke_market_data
invoke_mapper
~~~

Verify persisted JSON is the machine-readable boundary.

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
invoke_calendar_acquisition
invoke_calendar_query
calculate_news_warning_window
evaluate_news_warnings
build_news_warning_key
```

Verify:

```text
calendar.json is the sole persistent News store
dynamic warning horizon is derived from stored analysis entry timeframes
HIGH/MEDIUM/LOW warning scaling is deterministic
Calendar acquisition and local query are separate operations
missing calendar data does not block canonical processing
UTC event timing
impact policy
per-analysis/per-event warning evaluation
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
multi-analysis isolation
target clearance
optional RR
alert deduplication
failure isolation
~~~

---

# 22. REQUIRED TEST STRUCTURE

Focused tests must cover at minimum.

### CLI

~~~text
test_monitor_requires_symbol
test_monitor_accepts_multiple_symbols
test_monitor_resolves_symbol_output_directory
test_monitor_resolves_symbol_news_path
test_monitor_rr_optional
test_monitor_rejects_invalid_rr
test_monitor_debug_is_terminal_only
test_monitor_accepts_timezone
test_monitor_rejects_invalid_timezone
test_local_time_conversion_is_dst_aware
test_local_time_does_not_change_due_evaluation
~~~

### Analysis discovery

~~~text
test_discover_analysis_views_preserves_all_analyses
test_monitor_does_not_infer_analysis_from_market_data
test_analysis_registry_is_symbol_isolated
test_analysis_registry_is_checkpoint_isolated
~~~

### Market Data orchestration

~~~text
test_plan_market_data_updates_from_checkpoint
test_plan_market_data_bootstrap_range
test_plan_market_data_separates_incompatible_ranges
test_no_new_completed_candle_skips_mapper
test_missed_multiple_candles_use_one_range_update
test_current_snapshot_refresh_does_not_advance_checkpoint
~~~

### Process boundary

~~~text
test_invoke_market_data_uses_json_not_stdout
test_invoke_mapper_uses_persisted_structures_json
test_failed_market_data_blocks_dependent_mapper
test_failed_mapper_does_not_advance_monitor_checkpoint
~~~

### Calendar / News warning

~~~
test_calendar_cache_only_query_does_not_call_provider
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
test_mapper_invocation_passes_persisted_analysis_start
test_monitor_restart_resets_transient_alert_memory
test_alert_does_not_claim_position_open
~~~

### Isolation and persistence

~~~text
test_symbol_isolation
test_analysis_isolation
test_monitor_serializes_symbol_orchestration
test_monitor_does_not_write_structures_json
test_monitor_does_not_write_market_data_json
test_atomic_mapper_persistence_is_required_before_downstream_evaluation
~~~

Core Monitor tests must not require live provider access. Provider/process behavior should use doubles.

---

# 23. DEVELOPER-AGENT RULES

Do not:

- implement canonical SMC rules inside the Monitor;
- create a Monitor-specific POI lifecycle;
- create a second target ontology;
- create a second mapper checkpoint;
- write directly to either JSON store;
- parse Market Data or Mapper stdout as candle data;
- treat Calendar query stdout as diagnostics;
- call provider APIs directly;
- use current candles as canonical mapper input;
- infer new mapper analyses;
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
load selected symbols
 ↓
resolve each symbol data directory
 ↓
load structures and market-data JSON for each symbol
 ↓
discover stored analyses
 ↓
register analysis schedules
 ↓
for each due symbol
    ↓
    plan required Market Data coverage
    ↓
    invoke market_data.py
    ↓
    reload market-data JSON
    ↓
    invoke affected mapper analysis/analyses
    ↓
    reload structures JSON
    ↓
    refresh current market reference
    ↓
    evaluate trading-session context
    ↓
    invoke calendar.py --query SYMBOL
    ↓
    reload Calendar query result
    ↓
    evaluate NEWS_WARNING
    ↓
    consume canonical setup/entry state
    ↓
    resolve target
    ↓
    independently evaluate SETUP_ELIGIBLE
    ↓
    optionally emit SETUP_ELIGIBLE
    ↓
    independently evaluate TARGET_REACHED
    ↓
    optionally emit TARGET_REACHED

 ↓
schedule next evaluation
~~~

A current-snapshot-only update does not require canonical Mapper execution.

A completed-candle update requires Mapper execution before downstream target/alert evaluation of the new structural state.

---

# 25. DEFINITION OF DONE

smc_monitor.py is implementation-complete when:

- the documented CLI exactly matches implementation;
- selected symbols and all stored analyses are discovered correctly;
- each selected symbol automatically resolves its Market Data and Structures files; News remains in the single global calendar.json;
- Market Data and Mapper are invoked as independent processes;
- persisted JSON is the machine-readable process boundary;
- one active orchestration instance exists per symbol;
- analyses remain independently scheduled and isolated;
- mapper checkpoints are read-only from the Monitor;
- current price is obtained through persisted Market Data current state;
- Calendar is invoked only through its process boundary and its query stdout is validated as the machine-readable News result;
- News warning decisions are evaluated independently per eligible event;
- Calendar query result is validated before warning evaluation;
- NEWS_WARNING is separate from SETUP_ELIGIBLE and TARGET_REACHED;
- missing Calendar data does not suppress canonical setup/target evaluation;
- current snapshots never enter canonical Mapper processing;
- canonical SMC state is consumed rather than reimplemented;
- target resolution consumes only one unambiguous target candidate or fails closed when selection policy is absent;
- target clearance is deterministic and fail-closed;
- optional --rr is applied only to SETUP_ELIGIBLE evaluation, after target resolution and clearance;
- TARGET_REACHED notification is separate from target clearance/RR;
- there is no automatic order or position management;
- alerts are runtime notifications with deterministic deduplication;
- Monitor state is not persisted into canonical Market Data, Structures, or Calendar JSON;
- failures are isolated and finite-retry;
- tests cover orchestration, target, RR, alert, isolation, and process boundaries;
- domain contracts remain directly portable at the conceptual level to MQL4/MQL5.

**STATUS: CURRENT IMPLEMENTATION CONTRACT — CROSS-FILE OWNERSHIP RECONCILED**

---
