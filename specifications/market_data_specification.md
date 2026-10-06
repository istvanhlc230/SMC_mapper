# Market Data Module Specification

**Status:** Implementation specification for V1 `market_data.py`.  
**Scope:** Internal structure, interfaces, function/class names, variable naming, execution order, persistence, validation, extension points, and developer-agent implementation guidance for the standalone Market Data CLI.  
**Canonical authority:** `smc_mapper_specification.md` defines the mapper-facing market-data contract. `.agents/skills/smc/` remains the sole authority for canonical SMC semantics. This document does not define or modify SMC rules.

---

# 0. PURPOSE AND HARD BOUNDARIES

## 0.1 Finished-product role

`market_data.py` is a standalone Market Data CLI process.

Its responsibilities are:

1. accept market-data acquisition/update requests from the CLI;
2. select the concrete provider adapter;
3. retrieve provider data in deterministic ranges;
4. normalize provider data into the provider-independent candle contract;
5. determine completion/current state;
6. merge completed candles without duplication;
7. maintain an independent current in-progress snapshot per timeframe;
8. maintain bounded operational candle retention per timeframe;
9. persist `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json` atomically;
10. expose no canonical SMC interpretation.

The module is a **data acquisition and normalization boundary**, not an SMC analyzer.

## 0.2 Explicit non-responsibilities

`market_data.py` must not:

- calculate BOS, CHoCH, IDM, Dealing Range, POI, target, RR, or trade state;
- select or validate Order Blocks or Order Flows;
- apply canonical HTF/LTF SMC semantics;
- depend on `smc_mapper.py` or `smc_monitor.py`;
- import or call `smc_htf_ltf_monitor.py`, `smc_analyzer.py`, or any legacy engine as a runtime dependency;
- emit candle data through stdout as an inter-process data channel;
- persist debug text;
- fabricate missing candles;
- silently repair malformed provider data;
- treat an incomplete/current candle as a completed canonical candle.

## 0.3 Legacy-code reuse rule

Legacy files such as `smc_htf_ltf_monitor.py`, `smc_analyzer.py`, and old engine/test artifacts are optional source material only.

Reusable code or algorithms may be extracted when they are compatible with this specification, but the resulting implementation must be self-contained and must not retain a runtime/import/schema/behavioral dependency on legacy files.

---

# 1. MODULE DESIGN

## 1.1 V1 implementation structure

The V1 executable entry point remains market_data.py in the repository root. Internal implementation is split into the MARKET_DATA directory by functional ownership, following the approved Calendar-style layout.

Permanent source structure:

market_data.py
MARKET_DATA/__init__.py
MARKET_DATA/models.py
MARKET_DATA/provider.py
MARKET_DATA/normalization.py
MARKET_DATA/persistence.py
MARKET_DATA/service.py
MARKET_DATA/cli.py

The root file is only the executable entry point. Domain models, provider acquisition, normalization, persistence and orchestration are owned by the corresponding MARKET_DATA modules. The internal module boundaries are deliberately small and functional; do not split further without a real ownership boundary.


## 1.2 Design principle

Use abstraction at **external boundaries**, not everywhere.

Required abstraction:

- provider interface.

Avoid unnecessary abstraction for:

- simple JSON dictionary manipulation;
- simple CLI validation;
- straightforward list merge/deduplication;
- one-step numeric/time normalization.

Prefer direct code over generic repositories, service containers, dependency injection frameworks, or factory hierarchies that do not solve a real V1 problem.

---

# 2. IMPORTS AND MODULE CONSTANTS

## 2.1 Standard-library imports

Prefer only standard-library dependencies for V1 unless an external dependency is explicitly required by the selected provider implementation.

Baseline imports include:

```python
import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Sequence
```

The concrete provider adapter may add its explicitly required provider/client dependency.

Do not add a general HTTP framework merely for abstraction.

## 2.2 Module constants

Use descriptive uppercase constants for immutable module policy values.

`DEFAULT_DATA_DIRECTORY` denotes the common product data root under which every symbol gets its own output directory.

Required names:

```python
DEFAULT_DATA_DIRECTORY
SUPPORTED_TIMEFRAMES
TIMEFRAME_SECONDS
DEFAULT_PROVIDER_NAME
DEFAULT_CANDLE_RETENTION
WRITE_RETRY_LIMIT
WRITE_RETRY_DELAY_SECONDS
DECIMAL_PERSISTENCE_PLACES
```

Rules:

- constants must contain implementation policy only;
- no canonical SMC thresholds belong here;
- provider-specific constants must be grouped/namespaced with the provider adapter;
- V1 exact retention capacity is an operational setting, not a mapper/canonical parameter and must not become a CLI SMC setting;
- `DECIMAL_PERSISTENCE_PLACES = 18` and deterministic `ROUND_HALF_EVEN` persistence are fixed by the current approved contract.

If a constant is configurable later, keep its use behind one function/owner instead of scattering the value through the code.

### V1 policy values requiring one authoritative implementation decision

The exact V1 `SUPPORTED_TIMEFRAMES` set is not defined by the current mapper-facing contract. Do not invent or duplicate a timeframe list in multiple functions. Until the supported set is explicitly approved, keep it behind the single `SUPPORTED_TIMEFRAMES` / `TIMEFRAME_SECONDS` owner in this module.

The exact V1 candle-retention capacity is likewise an operational storage policy rather than canonical SMC semantics. It must be represented by the single `DEFAULT_CANDLE_RETENTION` owner and must not become a CLI or mapper semantic parameter.

---

# 3. DATA MODELS

Use small explicit state models. Python may use `dataclass` for implementation convenience. JSON persistence is a serialization representation, not the portable domain-class architecture.

## 3.1 Market-data request

```python
@dataclass(frozen=True)
class MarketDataRequest:
    symbol: str
    timeframes: list[str]
    start_time: datetime | None
    end_time: datetime | None
    last_closed_only: bool
    current: bool
    debug: bool
```

Variable name: `request`.

## 3.2 Provider candle

Use `ProviderCandle`.

Provider-facing state may contain provider-specific types/metadata. Required conceptual fields are:

**Field semantics:**

- `source_timestamp` is the provider-native timestamp before canonical normalization.
- `source_timezone` is the authoritative source timezone when the provider supplies it separately.
- `timestamp` is the normalized UTC candle identity timestamp and represents the candle interval start.
- `completion_hint` is provider evidence only; it never overrides the canonical completion rules.
- `provider_metadata` remains provider-local and must not cross into the persisted normalized JSON boundary.

A provider adapter must either supply an unambiguous timezone with the timestamp or fail the record. It must never silently assume the machine-local timezone. If the provider expresses a candle by interval-end time, the provider adapter must convert it to the canonical interval-start `timestamp` before the record reaches normalization.

```text
source_timestamp
source_timezone
timestamp
open_price
high_price
low_price
close_price
total_volume
orderflow_buy
orderflow_sell
completion_hint
provider_metadata
```

Provider-specific fields terminate at this boundary.

## 3.3 Volume state

Use `VolumeState`:

```python
@dataclass(frozen=True)
class VolumeState:
    has_total: bool
    total: Decimal | None
    has_ohlc: bool
    ohlc_buy: Decimal | None
    ohlc_sell: Decimal | None
    has_orderflow: bool
    orderflow_buy: Decimal | None
    orderflow_sell: Decimal | None
```

The independent source branches are `total`, `ohlc_buy/sell`, and `orderflow_buy/sell`.

Source-level delta is not stored. When needed:

```text
delta = buy - sell
```

## 3.4 Normalized candle

A `NormalizedCandle` is the only candle representation allowed to cross from acquisition/normalization into persistence.

The canonical interval is:

```text
[timestamp, completion_time)
```

where `timestamp` is the interval start and `completion_time` is the interval close boundary. A candle is eligible for `candles[]` only after its completion status is true.

```python
@dataclass(frozen=True)
class NormalizedCandle:
    candle_id: str
    timestamp: datetime
    completion_time: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: VolumeState
```

## 3.5 Timeframe state

The state contains exactly one completed series and at most one current snapshot for the timeframe.

Invariants:

- `candles[]` contains completed candles only;
- `current` is either null or one in-progress candle;
- the same candle identity must never exist simultaneously in both locations;
- `available_start/end` are derived from `candles[]` only;
- current-snapshot changes do not change completed-candle availability bounds.

```python
@dataclass
class TimeframeState:
    timeframe: str
    available_start: datetime | None
    available_end: datetime | None
    candles: list[NormalizedCandle]
    current: NormalizedCandle | None
```

## 3.6 Market-data document

```python
@dataclass
class MarketDataDocument:
    symbol: str
    timeframes: list[TimeframeState]
```

The JSON persistence representation maps this array of timeframe objects to the approved object keyed by timeframe.

## 3.7 Cross-language class portability (MQL4/MQL5)

The class/data-model contract is language-neutral and must be directly reproducible in both MQL4 and MQL5.

Portable rules:

- classes use explicit state fields;
- collections are conceptually arrays of named records;
- public methods use simple values and explicit output/reference parameters or arrays conceptually;
- correctness must not depend on Python-only typing, generators, tuples, properties, reflection, metaclasses, or dynamic attributes;
- mutable state ownership is explicit;
- public operations have an explicit success/failure result path;
- UTC timestamps map naturally to MQL `datetime`;
- field names and field meanings remain stable across Python, MQL4, and MQL5;
- JSON dictionary structure is persistence-only and must not become a second domain-class architecture.

Python may use `Decimal` internally for deterministic financial arithmetic; `Decimal` is not part of the portable interface.

## 3.8 Model vs. JSON representation boundary

Core processing uses the explicit domain models above.

The persisted JSON contract has four deliberate boundaries:

1. source/provider fields are gone;
2. Decimal values are serialized as deterministic strings;
3. completed candles and current snapshot are represented separately;
4. optional volume branches are omitted when unavailable.

The Mapper consumes only this serialized contract and must not need provider-specific reconstruction logic. Persistence helpers may use plain Python dictionaries/lists while translating to and from the approved JSON schema.

No canonical SMC semantic meaning may depend on the JSON container type.

The persisted JSON form of VolumeState is explicitly normalized for the external mapper boundary:

    "volume": {
      "total": "...",
      "ohlc": {
        "buy": "...",
        "sell": "..."
      },
      "orderflow": {
        "buy": "...",
        "sell": "..."
      }
    }

Rules:

- total is present only when has_total is true;
- ohlc is present only when has_ohlc is true;
- orderflow is present only when has_orderflow is true;
- source-level delta is not persisted in any branch; derive delta as buy - sell when needed;
- absent optional branches are represented by omission or the canonical null form used by the serializer and must be interpreted as unavailable by consumers;
- persisted Decimal-backed numeric values use the deterministic decimal-compatible string representation;
- the JSON volume schema is a serialization boundary and does not redefine the internal VolumeState field names.

---

# 4. FUNCTION NAMING CONTRACT

Use verbs that describe the actual responsibility.

Do not use vague names such as:

```process_data
handle_data
run_data
manage_data
do_update
helper
util
```

Preferred names are explicit:

```build_argument_parser
parse_market_data_request
validate_request
normalize_symbol
normalize_timeframe
parse_calendar_point
resolve_acquisition_range
create_provider
fetch_completed_candles
fetch_latest_completed_candle
fetch_current_candle
is_candle_complete
derive_completion_time
normalize_provider_candle
normalize_provider_candles
validate_normalized_candle
build_candle_id
merge_completed_candles
deduplicate_candles
sort_candles
apply_candle_retention
build_current_snapshot
merge_current_snapshot
clear_completed_current_snapshot
load_market_data
create_empty_market_data
serialize_market_data
save_market_data_atomic
update_timeframe
update_market_data
run
main
```

Every function must have one owner responsibility.

---

# 5. CLI LAYER

## 5.1 build_argument_parser

Signature:

```python
def build_argument_parser() -> argparse.ArgumentParser:
    ...
```

Purpose:

- define the approved `market_data.py` CLI;
- provide English `--help`;
- do not execute provider or file I/O.

Required options:

```text
--symbol SYMBOL
--timeframes TF [TF ...]
--range SCOPE
--current
--lastclosed
--debug
--help
```

`--range` accepts the Calendar-compatible scope grammar:

```text
YYYY.MM.DD
YYYY.MM.DD-YYYY.MM.DD
YYYY.MM.DD@HH:MM
YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM
```

Open-start range forms are also supported:

    --range -YYYY.MM.DD
    --range -YYYY.MM.DD@HH:MM
    --range YYYY.MM.DD-
    --range YYYY.MM.DD@HH:MM-

A leading `-` omits the start boundary. The start is resolved separately for each requested timeframe from
that timeframe's latest persisted completed-candle timestamp (`available_end`). The explicit END remains
the upper boundary. An open-start range therefore requires retained completed history for every requested
timeframe; a missing `available_end` fails explicitly rather than fabricating a start.

A trailing `-` omits the end boundary. The explicit START is retained and the end resolves to the current
UTC time at execution. Therefore `--range YYYY.MM.DD-` means START at 00:00 UTC through NOW, while
`--range YYYY.MM.DD@HH:MM-` means the exact UTC minute through NOW. A future START is rejected.
Both open-start and open-end forms use the same UTC date/time grammar and half-open interval semantics.
The canonical time spelling is `HH:MM`; `HH.MM` is accepted only as a compatibility alias in open-ended datetime forms and is normalized to `HH:MM`.

Examples:

```text
--range 2026.10.05
--range 2026.10.05-2026.10.08
--range 2026.10.05@08:30
--range 2026.10.05@08:30-2026.10.05@16:45
--current
--lastclosed
```

The historical scope grammar is intentionally aligned with the Calendar CLI specification. Market Data does not introduce a second date/time syntax.

No price-basis option is allowed.

No volume-method option is allowed.

No mapper/SMC option is allowed.

## 5.2 parse_market_data_request

Signature:

```python
def parse_market_data_request(argv: Sequence[str] | None = None) -> MarketDataRequest:
    ...
```

Purpose:

- parse the Calendar-compatible scope;
- resolve the scope into timezone-aware UTC boundaries;
- construct `MarketDataRequest`;
- distinguish historical acquisition, `current`, and `lastclosed` modes.

### Scope resolution contract

| Scope | Resolved interval / mode |
|---|---|
| `YYYY.MM.DD` | full UTC calendar day: `[00:00, next-day 00:00)` |
| `YYYY.MM.DD-YYYY.MM.DD` | inclusive date range: `[start 00:00, day-after-end 00:00)` |
| `YYYY.MM.DD@HH:MM` | exact UTC minute: `[point, point+1 minute)` |
| `YYYY.MM.DD@HH:MM-YYYY.MM.DD@HH:MM` | half-open UTC interval |
| `-YYYY.MM.DD` | from persisted `available_end` through the exclusive end of the given UTC day |
| `-YYYY.MM.DD@HH:MM` | from persisted `available_end` through the exclusive end of the given UTC minute |
| `--current` | no historical interval; refresh the current in-progress candle snapshot |
| omitted | normal incremental completed-candle acquisition |
| `--lastclosed` | exactly the latest completed candle |

Malformed dates/times, impossible calendar dates, invalid 24-hour times, unexpected seconds/offset syntax, reversed/empty intervals, and future range starts must fail explicitly.

Historical range inclusion is based on the canonical candle interval start:
`start_time <= candle.timestamp < end_time`. Completion status is checked separately;
`completion_time` must not be used as the range boundary itself. The same rule applies to provider overfetch after normalization.

No machine-local timezone is ever assumed.

### Request-mode rules

- `--lastclosed` means **the latest completed/closed candle**, never the current in-progress candle.
- `--current` means **the current in-progress candle snapshot**.
- `--lastclosed` is mutually exclusive with `--range`.
- `--current` is mutually exclusive with `--lastclosed`.
- Historical `--range` scopes, including open-start `-END` ranges, are mutually exclusive with `current` and `lastclosed` modes.
- With no explicit mode, normal incremental completed-candle acquisition is used.
- `lastclosed` must use the provider's latest-completed acquisition path and completion validation.
- The implementation request fields are `last_closed_only` and `current`; these names are authoritative for service orchestration.
- A candle is eligible for `lastclosed` only when its canonical `completion_time` has passed.
- `lastclosed` must never promote an in-progress candle merely because it is the provider's newest record.
- `current` must use the provider current-candle path and must persist the candle only as the separate `current` snapshot while it remains incomplete.
- When a current candle reaches its canonical completion boundary, it becomes eligible for the completed-candle collection and the separate `current` snapshot must be cleared.

### Request object

`MarketDataRequest` uses these mode fields:

```text
symbol
timeframes
start_time
end_time
last_closed_only
current
debug
```

`last_closed_only` and `current` are explicit mutually exclusive mode states.


## 5.2.1 Explicit current CLI parameter

The current in-progress candle mode is exposed as the explicit `--current` CLI parameter.

Canonical forms:

    python market_data.py --symbol EURUSD --timeframes M1 M5 --current
    python market_data.py --symbol EURUSD --timeframes M1 M5 --range 2026.10.05
    python market_data.py --symbol EURUSD --timeframes M1 M5 --lastclosed

`--current` must not be encoded as `--range current`. The latter form is not part of the public Market Data CLI grammar and must be rejected. `--current` is mutually exclusive with `--range` and `--lastclosed`.

## 5.3 normalize_symbol

Signature:

```python
def normalize_symbol(symbol: str) -> str:
    ...
```

Rules:

- trim surrounding whitespace;
- reject empty input;
- preserve the provider-compatible instrument spelling unless the provider adapter requires an explicit mapping;
- do not silently change symbols.

## 5.4 normalize_timeframe

Signature:

```python
def normalize_timeframe(timeframe: str) -> str:
    ...
```

Rules:

- normalize the accepted spelling/casing;
- reject empty or structurally invalid timeframe values;
- return one canonical timeframe string;
- use `TIMEFRAME_SECONDS` only when completion arithmetic requires a known duration;
- do not reject an otherwise valid boundary-supplied timeframe solely because `SUPPORTED_TIMEFRAMES` is empty.

## 5.5 parse_calendar_date

Signature:

```python
def parse_calendar_date(value: str) -> date:
    ...
```

Purpose:

- parse the shared Calendar/Market Data date representation `YYYY.MM.DD`;
- reject malformed or impossible dates.

## 5.6 parse_calendar_time

Signature:

```python
def parse_calendar_time(value: str) -> time:
    ...
```

Purpose:

- parse the shared Calendar/Market Data time representation `HH:MM`;
- reject malformed times and seconds.

## 5.7 resolve_boundary

Signature:

```python
def resolve_boundary(
    date_value: str | None,
    time_value: str | None,
    *,
    boundary_name: str,
    now: datetime,
) -> datetime | None:
    ...
```

Purpose:

- combine independently supplied date/time components;
- apply the Calendar-compatible defaults;
- return a timezone-aware UTC boundary;
- represent a date-only end boundary as the following day's exclusive midnight.

No provider I/O is allowed.

---

# 6. PROVIDER ABSTRACTION

## 6.1 MarketDataProvider base class

Use the following small structural interface.

Required interface:

```python
class MarketDataProvider:
    def fetch_range(
        self,
        symbol: str,
        timeframe: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[ProviderCandle]:
        ...

    def fetch_latest_completed(
        self,
        symbol: str,
        timeframe: str,
    ) -> ProviderCandle | None:
        ...

    def fetch_current(
        self,
        symbol: str,
        timeframe: str,
    ) -> ProviderCandle | None:
        ...
```

The provider interface is the only place where concrete provider behavior is abstracted.

The mapper never imports this interface.

## 6.2 create_provider

Signature:

```python
def create_provider(provider_name: str) -> MarketDataProvider:
    ...
```

V1:

- return the concrete Yahoo Charts provider;
- keep provider selection behind this single function;
- provider selection must not leak into normalization or persistence.

The provider name is internal implementation policy in V1. Do not add a provider CLI option unless the product specification explicitly changes.

## 6.3 YahooChartsProvider

Use concrete class:

```python
class YahooChartsProvider:
    ...
```

Responsibilities:

- provider API access only;
- provider request pagination/chunking;
- provider timestamp interpretation;
- provider completion hints/data;
- provider field mapping into `ProviderCandle`;
- provider retry/error handling.

The class must not:

- build the persisted JSON document;
- perform canonical SMC logic;
- decide POI or structural state.

Required provider methods:

```fetch_range
fetch_latest_completed
fetch_current
```

Keep provider-specific parsing private to the provider adapter where possible.

## 6.4 Provider pagination

If Yahoo Charts requires multiple requests for one logical range:

- pagination belongs inside `YahooChartsProvider.fetch_range`;
- the caller sees one logical iterable/range;
- page order must be reconciled deterministically;
- duplicate provider records must not produce duplicate normalized candles;
- provider request chunking must not change persisted logical results.

---

## 6.5 Portable provider class contract

The provider abstraction is a simple base-class contract that can be implemented in Python, MQL4, and MQL5.

Conceptual methods:

```text
FetchRange(symbol, timeframe, start_time, end_time, out candles[]) -> success/failure
FetchLatestCompleted(symbol, timeframe, out candle) -> success/failure
FetchCurrent(symbol, timeframe, out candle) -> success/failure
```

Python V1 may use normal return values. An MQL4/MQL5 port should use virtual methods with explicit output references or arrays.

The base class owns acquisition only. Concrete provider classes own transport, pagination, parsing, retries and provider-specific field mapping.

The provider abstraction must not depend on JSON persistence, mapper state, monitor state, or canonical SMC logic.

### Provider result contract

Provider methods must obey these rules:

- `fetch_range()` returns provider candles whose logical records cover the requested provider range; it may overfetch minimal provider-boundary data needed to resolve completion correctly.
- The caller, not the provider, owns final inclusion into the normalized completed series.
- Provider pagination must be invisible to the caller.
- Provider-level duplicate records are tolerated only when they normalize to the same candle identity and equivalent content.
- A provider failure is an acquisition failure; it must not be represented as an empty successful result.
- An empty successful provider response means “no provider records available for the requested operation” and must remain distinguishable from a transport/API error.
- `fetch_latest_completed()` must return the newest record that is actually complete under the canonical completion check; the provider must not return an arbitrary latest in-progress record.
- `fetch_current()` must return the latest current record when available; if the provider cannot expose current state, returning `None` is valid and must not be converted into a fabricated candle.

### Provider boundary decision table

| Provider outcome | Mapper-facing result |
|---|---|
| valid records | normalize and validate |
| valid empty response | no incoming records; continue according to request mode |
| malformed record | normalization/data-integrity failure |
| ambiguous source time | normalization failure |
| transport/API failure | provider acquisition failure |
| timeout after retries | provider acquisition failure |
| provider reports incomplete record | current candidate only |
| provider reports completed record | completed candidate |

# 7. COMPLETION AND CURRENT-CANDLE LOGIC

## 7.1 is_candle_complete

Signature:

```python
def is_candle_complete(
    provider_candle: ProviderCandle,
    timeframe: str,
    now: datetime | None = None,
) -> bool:
    ...
```

Responsibilities:

- evaluate provider completion information against canonical timeframe boundaries;
- allow provider-specific completion hints;
- use current UTC time only when necessary for completion evaluation;
- never treat the candle timestamp alone as proof of completion.

The function must return deterministic results for historical candles when provider completion data is sufficient.

## 7.2 derive_completion_time

Signature:

```python
def derive_completion_time(
    timestamp: datetime,
    timeframe: str,
) -> datetime:
    ...
```

Purpose:

- calculate the canonical interval-close boundary when the timeframe semantics permit deterministic derivation.

Rules:

- return UTC;
- use the approved `TIMEFRAME_SECONDS` duration map;
- for an interval-start timestamp, compute `completion_time = timestamp + TIMEFRAME_SECONDS[timeframe]`;
- do not depend on local timezone;
- do not use wall-clock time to alter historical completion boundaries;
- the boundary is deterministic for a given normalized timestamp and timeframe.

## 7.3 Current snapshot separation

Completed candles and current snapshot are separate stores.

Rules:

```text
completed -> candles[]
in-progress -> current
```

A current snapshot:

- may change on repeated `--current` executions;
- must carry stable candle identity;
- must never be inserted into `candles[]` while incomplete;
- must never advance mapper checkpoints;
- may contain provider-available OHLC/total volume/orderflow;
- does not participate in completed-candle retention.

## 7.4 build_current_snapshot

Signature:

```python
def build_current_snapshot(
    normalized_candle: NormalizedCandle,
) -> dict[str, Any]:
    ...
```

The returned object is persisted under the timeframe's `current` field.

## 7.5 clear_completed_current_snapshot

Signature:

```python
def clear_completed_current_snapshot(
    timeframe_state: dict[str, Any],
    completed_candle_id: str,
) -> None:
    ...
```

When the current snapshot becomes the completed candle:

- move/persist the completed candle through the normal completed-candle merge path;
- remove the matching current snapshot;
- do not leave the same candle simultaneously as a completed candle and current snapshot.

### Current-snapshot state transitions

```text
NO CURRENT
   |
   | fetch_current -> incomplete candle
   v
CURRENT(id=X)
   |
   | same id, newer provider data
   v
CURRENT(id=X) [replace snapshot]
   |
   | new id
   v
CURRENT(id=Y) [replace X]
   |
   | candle becomes complete
   v
COMPLETED(id=X) + CURRENT=null
```

Rules:

- only one current snapshot exists per timeframe;
- repeated current refresh replaces the previous snapshot rather than appending history;
- a current snapshot may change OHLC/volume while its candle remains incomplete;
- when the candle completes, the final completed record is merged into `candles[]` and the current snapshot is removed;
- if completion occurs between fetch and persistence, the candle follows the completed path;
- when a current refresh succeeds but the provider returns no current record, `current` is cleared to null so stale current price is not presented as live state;
- when the provider operation fails, the whole symbol transaction fails and the previously persisted current snapshot remains untouched;
- a current-only update is a valid Market Data state change but never a Mapper checkpoint change.

Refresh decision table:

| Refresh result | State action |
|---|---|
| current record + incomplete | replace current snapshot |
| current record + completed | merge into completed series; set current null |
| successful no-current result | set current null |
| provider/API failure | fail transaction; preserve previous persisted state |

---

# 8. NORMALIZATION LAYER

## 8.1 normalize_provider_candle

Signature:

```python
def normalize_provider_candle(
    provider_candle: ProviderCandle,
    timeframe: str,
    symbol: str = "",
) -> NormalizedCandle:
    ...
```

Responsibilities:

- normalize timestamp to UTC;
- determine completion boundary;
- convert OHLC to Decimal;
- normalize total volume if present;
- preserve orderflow branch if genuinely supplied;
- never infer observed orderflow from OHLC;
- optionally calculate/store OHLC-derived directional volume if the normalized contract requires it as a preserved analytical branch;
- construct deterministic candle identity;
- validate the final normalized candle before returning it.

Provider-specific field names must disappear at this boundary.

## 8.2 normalize_provider_candles

Signature:

```python
def normalize_provider_candles(
    provider_candles: Iterable[ProviderCandle],
    timeframe: str,
    symbol: str = "",
) -> list[NormalizedCandle]:
    ...
```

Rules:

- normalize every candle;
- reject malformed entries rather than silently dropping them;
- reject ambiguous timestamps;
- reject invalid OHLC;
- produce a deterministic chronological series.

## 8.3 build_candle_id

Signature:

```python
def build_candle_id(
    symbol: str,
    timeframe: str,
    timestamp: datetime,
) -> str:
    ...
```

Rules:

- deterministic;
- stable across repeated downloads;
- based only on stable candle identity;
- never based on list index;
- exact string layout is an implementation detail but must be stable once V1 persists data.

## 8.4 validate_normalized_candle

Signature:

```python
def validate_normalized_candle(candle: NormalizedCandle) -> None:
    ...
```

Validate:

- finite Decimal values;
- `high >= low`;
- `low <= open <= high`;
- `low <= close <= high`;
- canonical candle formation-model constraints already defined by the market-data contract;
- valid completion boundary;
- non-negative volume values when present;
- no malformed nested volume branch.

Do not repair invalid data silently.

### Normalization acceptance/rejection matrix

| Input condition | Action |
|---|---|
| valid timezone-aware timestamp | normalize to UTC |
| naive/ambiguous timestamp | FAIL |
| finite numeric OHLC | convert to Decimal |
| non-numeric OHLC | FAIL |
| `high < low` | FAIL |
| open/close outside high-low range | FAIL |
| negative total volume | FAIL |
| negative buy/sell branch value | FAIL |
| missing optional volume branch | omit/unavailable |
| provider orderflow present | preserve as observed orderflow |
| only OHLC data available | preserve only OHLC-derived branch |
| provider-specific metadata | discard at normalized boundary |
| duplicate record with same normalized identity/content | deduplicate |
| duplicate record with same identity but conflicting content | FAIL |

No normalization path may silently coerce malformed financial values into another valid value.

---

# 9. VOLUME DATA NORMALIZATION

## 9.1 Parallel-data rule

A normalized candle may contain these independent branches:

```text
volume.total
volume.ohlc
volume.orderflow
```

Presence is the availability signal.

Do not create one exclusive `volume_method` field.

## 9.2 Provider total volume

When supplied:

```volume.total
```

is preserved as normalized total volume.

Do not discard provider total volume because directional estimation is unavailable.

## 9.3 Genuine orderflow

When supplied by the provider:

```volume.orderflow = {
    buy,
    sell
}
```

is preserved independently.

Never label estimated OHLC-derived values as orderflow.

## 9.4 OHLC directional estimate

When required by the normalized data contract and source values are usable, preserve the analytical estimate independently:

```volume.ohlc = {
    buy,
    sell
}
```

The exact OHLC estimation formulas are owned by the approved volume contract in `smc_mapper_specification.md` / the implementation-facing volume specification. Do not invent a different formula here.

Use Decimal arithmetic.

Zero total volume produces no directional estimate.

---

# 10. MERGE AND DEDUPLICATION

## 10.1 merge_completed_candles

Signature:

```python
def merge_completed_candles(
    existing_candles: Sequence[dict[str, Any]],
    incoming_candles: Sequence[NormalizedCandle],
) -> list[dict[str, Any]]:
    ...
```

Purpose:

- merge newly acquired completed candles into the persisted series.

Rules:

- identity is `candle_id`;
- repeated downloads must not duplicate candles;
- final output is strictly chronological;
- existing persisted completed candles are immutable;
- if the same `candle_id` arrives with materially different normalized content, treat it as a data-integrity conflict and fail explicitly rather than silently overwrite it;
- do not use array index as identity.

## 10.2 deduplicate_candles

Signature:

```python
def deduplicate_candles(
    candles: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    ...
```

Use candle identity, not timestamp alone, as the storage key.

Because timestamp is expected to be unique within one timeframe, a conflicting identity/timestamp mismatch is an explicit data-integrity error.

## 10.3 sort_candles

Signature:

```python
def sort_candles(
    candles: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    ...
```

Sort by canonical candle timestamp in ascending order.

Final persisted series must satisfy:

```text
timestamp[n] < timestamp[n+1]
```

---

# 11. RETENTION

## 11.1 apply_candle_retention

Signature:

```python
def apply_candle_retention(
    candles: Sequence[dict[str, Any]],
    retention_limit: int,
    protected_start: datetime | None = None,
    protected_end: datetime | None = None,
) -> list[dict[str, Any]]:
    ...
```

Rules:

- retention is per timeframe;
- newest candles are retained when no protected range applies;
- eviction is oldest-first;
- completed candle chronology remains intact;
- retention does not modify candle contents;
- retention does not invalidate mapper structural history;
- when `protected_start` is supplied, candles at or after that boundary are protected for the current requested processing range;
- when `protected_end` is supplied, only candles strictly before that exclusive boundary are protected by the requested range;
- when `protected_start` is supplied and `protected_end` is absent, protection extends through the newest currently available completed candle;
- protected candles are retained even when this temporarily exceeds `retention_limit`;
- once the protected range is no longer requested, normal rolling retention may evict old candles;
- retention is operational storage policy only.

The function must be pure with respect to its inputs.

### Retention algorithm

1. partition completed candles into protected and unprotected sets;
2. retain every protected candle;
3. from unprotected candles, retain the newest entries first until `retention_limit` is reached;
4. if protected candles alone exceed `retention_limit`, retain all protected candles for this invocation;
5. if no protected range exists, retain at most `retention_limit` completed candles;
6. restore strict chronological ordering before returning;
7. never mutate candle contents;
8. never delete the current snapshot because of completed-candle retention.

Retention therefore bounds ordinary storage while guaranteeing that an explicitly requested historical range survives long enough for the consuming Mapper invocation.

## 11.2 Retention and reacquisition

If a later mapper analysis requires candles outside the retained window, the surrounding launcher/orchestrator triggers reacquisition through `market_data.py`.

When an explicit historical acquisition range is requested, that requested range is protected during the current update so the just-reacquired candles remain available to the immediately following Mapper invocation. This protection is temporary and does not disable normal rolling retention for unrelated candles.

The resolved acquisition range, not merely the raw CLI fields, is the authoritative range for retention protection. The implementation must not assume retained storage is the only possible source of historical data.

---

# 12. JSON PERSISTENCE

## 12.1 Symbol directory and file naming

The product uses one dedicated symbol directory under the common data root:

```text
<DATA_ROOT>/
└── <SYMBOL>/
    └── <SYMBOL>_marketdata.json
```

Rules:

- `<DATA_ROOT>` is the existing `data_directory` / `DEFAULT_DATA_DIRECTORY` root; this change does not introduce a new user-facing path option;
- `<SYMBOL>` is the normalized symbol identity used by the request;
- the symbol directory is created automatically when persistence is required;
- `market_data.py` automatically resolves and loads the symbol's market-data file from that directory;
- normal callers do not supply an ad-hoc per-file path;
- all acquired timeframes for that symbol live inside the same market-data file;
- no market-data file is stored directly beside another symbol's file;
- no timeframe-specific file is created.

The symbol directory is a filesystem/output boundary only; it introduces no canonical SMC semantics.

## 12.2 get_symbol_data_directory

Signature:

```python
def get_symbol_data_directory(
    symbol: str,
    data_directory: Path,
) -> Path:
    ...
```

Rules:

- deterministic;
- resolves to `<DATA_ROOT>/<SYMBOL>`;
- path calculation itself does not perform I/O;
- directory creation occurs only as an explicit persistence prerequisite;
- does not silently rename the symbol;
- the symbol directory component must be a safe single filesystem path component; path separators, drive prefixes, `.`/`..`, NUL characters, and traversal sequences must be rejected rather than sanitized into another symbol identity.
- the resolved path must remain inside `<DATA_ROOT>`.

## 12.3 get_market_data_path

Signature:

```python
def get_market_data_path(
    symbol: str,
    data_directory: Path,
) -> Path:
    ...
```

Rules:

- deterministic;
- resolves to `<DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json`;
- uses `get_symbol_data_directory` as the single directory owner;
- no timeframe-specific market-data file;
- reject unsafe symbol path components rather than sanitizing them into another instrument identity;
- the resolved path must remain inside `<DATA_ROOT>/<SYMBOL>`;
- do not silently rename a symbol into another instrument identity.

## 12.4 load_market_data

Signature:

```python
def load_market_data(
    path: Path,
    symbol: str,
) -> dict[str, Any]:
    ...
```

Behavior:

- if the file does not exist, return a new valid symbol document;
- validate the symbol matches;
- validate top-level `timeframes` structure;
- validate each timeframe state;
- reject malformed JSON/data;
- do not silently discard malformed persisted state.

## 12.5 ensure_timeframe_state

Signature:

```python
def ensure_timeframe_state(
    market_data: dict[str, Any],
    timeframe: str,
) -> dict[str, Any]:
    ...
```

Creates the timeframe section when absent:

```json
{
  "available_start": null,
  "available_end": null,
  "candles": [],
  "current": null
}
```

Do not modify unrelated timeframe sections.

## 12.6 update_available_bounds

Signature:

```python
def update_available_bounds(
    timeframe_state: dict[str, Any],
) -> None:
    ...
```

Derive:

```text
available_start = first persisted completed candle timestamp
available_end   = last persisted completed candle timestamp
```

These fields describe completed-candle coverage only.

Current snapshot does not affect availability bounds.

## 12.7 save_market_data_atomic

Signature:

```python
def save_market_data_atomic(
    path: Path,
    market_data: dict[str, Any],
    retry_limit: int = WRITE_RETRY_LIMIT,
) -> None:
    ...
```

Required behavior:

1. serialize the complete document deterministically;
2. write to a temporary file in the same directory;
3. flush/close successfully;
4. atomically replace the target file;
5. retry transient write failures up to the configured finite limit;
6. clean up the temporary file on failure.

Do not update a JSON file in place.

Do not use a separate lock file in V1.

The finished monitor architecture serializes active orchestration per symbol.

## 12.8 Deterministic JSON serialization

Use one serialization helper for persisted Decimal values:

```python
def serialize_decimal(value: Decimal) -> str:
    ...
```

Rules:

- input must be finite;
- quantize to `DECIMAL_PERSISTENCE_PLACES` using `ROUND_HALF_EVEN` when persistence precision is required;
- serialize as a plain base-10 string, never scientific notation;
- do not serialize Decimal values as JSON floating-point numbers;
- parsing the persisted string back to Decimal must reproduce the persisted numeric value exactly.

Use deterministic serialization:

- stable key ordering;
- consistent UTF-8 encoding;
- consistent newline behavior;
- no Debug text;
- Decimal-backed persisted numeric values use the approved decimal-compatible string representation;
- no random IDs or timestamps generated merely for serialization.

The same logical market-data state must produce the same persisted JSON content.

---

## 12.9 External JSON schema contract

The following serialized structure is the mapper-facing V1 market-data contract:

    {
      "symbol": "CCCC",
      "timeframes": {
        "H4": {
          "available_start": "...",
          "available_end": "...",
          "candles": [ ... ],
          "current": null
        }
      }
    }

Each completed candle contains `candle_id`, `timestamp`, `completion_time`, `open`, `high`, `low`, `close`, and the volume object defined in Section 3.8. Timestamp and completion_time are UTC ISO-8601 values. Persisted numeric price and volume values use the deterministic decimal-compatible string representation.

Exact logical candle example:

```json
{
  "candle_id": "EURUSD_H4_2026-10-03T08:00:00Z",
  "timestamp": "2026-10-03T08:00:00Z",
  "completion_time": "2026-10-03T12:00:00Z",
  "open": "1.17000",
  "high": "1.17250",
  "low": "1.16800",
  "close": "1.17125",
  "volume": {
    "total": "12345",
    "ohlc": {
      "buy": "9000",
      "sell": "3345"
    },
    "orderflow": {
      "buy": "9100",
      "sell": "3245"
    }
  }
}
```

The example values are illustrative only; the field names, null/omission rules, time semantics, and numeric serialization are normative.

The current field uses the same serialized candle shape when present, but it is an in-progress runtime snapshot. It does not contribute to available_start/available_end and is never a completed-candle substitute.

The mapper may deserialize this schema into its own read-only view model. It must not import Market Data domain classes merely to read the JSON boundary.

### JSON validity invariants

A persisted Market Data document is valid only when all of the following hold:

- top-level `symbol` is a non-empty string;
- top-level `timeframes` is an object;
- every timeframe key is canonical and unique;
- every timeframe state contains `available_start`, `available_end`, `candles`, and `current`;
- `candles` is an array of completed candle records;
- `current` is null or one in-progress candle;
- candle IDs are deterministic and unique within the timeframe;
- candle timestamps are strictly ascending;
- each candle has UTC `timestamp` and `completion_time`;
- `completion_time > timestamp`;
- persisted numeric values use the approved Decimal string representation;
- availability bounds equal the first/last persisted completed candle timestamps, or both are null when `candles=[]`;
- `current` never changes availability bounds;
- `available_start` and `available_end` are coverage bounds, not proof of gapless history;
- missing candles inside the bounds are valid persisted state and must never be synthesized merely to fill a gap.

A malformed persisted document must fail validation. The loader must never “repair” it by dropping unknown or invalid records.

---

# 13. ACQUISITION PLANNING

## 13.1 resolve_acquisition_range

Signature:

```python
def resolve_acquisition_range(
    request: MarketDataRequest,
    timeframe: str,
    existing_state: dict[str, Any] | None,
) -> tuple[datetime | None, datetime | None]:
    ...
```

Purpose:

determine what the provider must retrieve for one timeframe.

Cases:

### Historical range

When explicit historical boundaries are supplied:

- `start_time + end_time`: acquire exactly the requested interval;
- `start_time` only: acquire from `start_time` through the latest completed candle available at evaluation time;
- `end_time` only (the internal representation of open-start `--range -END`): use the persisted `available_end` for the timeframe as the acquisition start; if no persisted completed history exists, fail explicitly;
- honor requested boundaries;
- do not invent candles outside requested scope.

### Current-only current refresh

When `current=True`, `last_closed_only=False`, and neither `start_time` nor `end_time` is supplied:

- fetch the latest provider candle needed for the current snapshot for each requested timeframe;
- persist it under the timeframe's `current` field while incomplete;
- if it is already completed when evaluated, route it through the completed-candle path and clear the matching current snapshot;
- do not fabricate or infer a historical acquisition range;
- do not require a new completed candle for the invocation to be valid.

### Last-candle mode

When `last_closed_only=True`:

- retrieve exactly the latest completed candle for the timeframe;
- do not treat `current` as the result;
- do not retrieve an arbitrary recent window.

### Incremental mode

When neither historical boundaries nor `--lastclosed` apply and `current=False`:

- if the timeframe has persisted completed candles, acquire only newly completed candles after the persisted `available_end`;
- if the timeframe has no persisted completed candles, acquire exactly the latest completed candle;
- preserve chronological order;
- allow multiple newly completed candles when execution was missed.

This function plans provider acquisition only. It does not manipulate mapper checkpoints.

### Incremental boundary rule

Normal incremental mode advances past the persisted `available_end` candle. The next acquisition start is:

    available_end + timeframe interval duration

This prevents an ordinary incremental run from re-requesting the already persisted terminal candle. The open-start
`--range -END` mode is intentionally different: it starts at `available_end` inclusively so the requested historical
range can reacquire/reconcile the retained boundary candle and deduplicate it by stable candle ID.

### Resolved acquisition range contract

`resolve_acquisition_range()` returns a logical canonical range after applying request mode, existing state, and current evaluation time.

The returned range must satisfy:

- start and end are timezone-aware UTC values when present;
- start <= end;
- the range never exceeds the explicit user-requested boundary;
- when no explicit end exists, the end is the latest completed candle boundary resolved at evaluation time;
- when incremental mode uses `available_end`, the next acquisition begins at the next canonical candle interval after the persisted end candle;
- acquisition logic must not use the current snapshot as a completed-candle boundary;
- the function must be deterministic when `now` is supplied explicitly.

The provider may fetch a slightly wider provider-native range when required by its API, but the normalized merge layer is responsible for final canonical inclusion.

## 13.2 Missing retained history

The Market Data CLI may be invoked for a range not currently retained.

The acquisition planner must allow the provider to reacquire the missing historical range.

The merge layer then reconciles the result into the persisted timeframe series.

---

# 14. TIMEFRAME UPDATE FUNCTIONS

## 14.1 fetch_completed_candles

Signature:

```python
def fetch_completed_candles(
    provider: MarketDataProvider,
    symbol: str,
    timeframe: str,
    start_time: datetime,
    end_time: datetime,
) -> list[NormalizedCandle]:
    ...
```

Process:

1. call provider `fetch_range`;
2. normalize every provider record;
3. reject malformed records and ambiguous timestamps;
4. evaluate completion;
5. keep only candles whose canonical interval start satisfies `start_time <= timestamp < end_time`;
6. exclude all incomplete/current candidates;
7. validate normalized candles;
8. return deterministic ascending chronology.

The function returns only completed canonical market-data candles whose interval starts fall inside the resolved half-open range. Completion status is evaluated independently. Provider-native overfetch outside the interval is discarded before persistence.

## 14.2 fetch_latest_completed_candle

Signature:

```python
def fetch_latest_completed_candle(
    provider: MarketDataProvider,
    symbol: str,
    timeframe: str,
) -> NormalizedCandle | None:
    ...
```

Must return exactly one latest completed candle when available.

Selection is by greatest canonical `timestamp`; for a fixed timeframe this is equivalent to greatest `completion_time`. Ties are a data-integrity error unless they refer to the same normalized candle identity.

## 14.3 fetch_current_candle

Signature:

```python
def fetch_current_candle(
    provider: MarketDataProvider,
    symbol: str,
    timeframe: str,
) -> NormalizedCandle | None:
    ...
```

Must return the latest in-progress candle when the provider can supply it.

Selection is by greatest canonical `timestamp` among incomplete provider records. If the provider returns only completed records, this function returns `None` and the completed branch handles them.

If the returned candle is already completed by the time it is evaluated, route it through the completed-candle path rather than persisting it as current.

## 14.4 update_timeframe

Signature:

```python
def update_timeframe(
    market_data: dict[str, Any],
    provider: MarketDataProvider,
    request: MarketDataRequest,
    timeframe: str,
) -> bool:
    ...
```

Responsibilities:

- resolve the timeframe-specific acquisition operation;
- acquire completed data and/or current snapshot according to the request;
- normalize and validate;
- merge completed candles;
- update current snapshot;
- clear a current snapshot when it becomes completed;
- apply retention, protecting the resolved historical acquisition range `(acquisition_start, acquisition_end)` for this invocation when the request is historical;
- update availability bounds;
- return whether persisted market-data state changed.

It must not modify any other timeframe.

### update_timeframe transaction semantics

`update_timeframe()` operates only on the supplied in-memory timeframe state.

It must:

1. compute the resolved acquisition operation;
2. fetch provider data;
3. normalize/validate all incoming records;
4. merge completed records;
5. refresh/clear current snapshot as required;
6. apply retention;
7. recompute availability bounds;
8. validate the resulting timeframe state;
9. return `True` only when the resulting state differs from the original state.

If any step fails, the caller receives a failure and the original symbol document remains unchanged because the top-level orchestration has not committed it.

The function must not write the target JSON file directly.

---

# 15. TOP-LEVEL ORCHESTRATION

## 15.1 update_market_data

Signature:

```python
def update_market_data(
    request: MarketDataRequest,
    provider: MarketDataProvider,
) -> bool:
    ...
```

Execution order:

1. resolve the symbol data directory and market-data path;
2. load or create the symbol-scoped market-data document;
3. apply the request to each requested timeframe in memory:
   - ensure timeframe state;
   - resolve acquisition;
   - acquire provider data;
   - normalize;
   - validate;
   - merge/deduplicate;
   - current-snapshot handling;
   - retention;
   - availability bounds;
4. if any requested timeframe fails, discard the entire in-memory update and do not persist a partial document;
5. save the complete symbol document once if any state changed;
6. return whether the document changed.

Important:

- all requested timeframes share one market-data JSON document;
- timeframe updates remain logically independent;
- a failure in one timeframe fails the current invocation and does not persist any partial change from that invocation;
- do not persist a partially updated document;
- use one complete read-modify-write transaction for the symbol.

### Symbol-level transaction semantics

The top-level operation behaves as:

```text
LOAD EXISTING DOCUMENT
        ↓
COPY IN-MEMORY WORKING STATE
        ↓
UPDATE TIMEFRAME 1
        ↓
UPDATE TIMEFRAME 2
        ↓
...
        ↓
VALIDATE COMPLETE WORKING DOCUMENT
        ↓
NO CHANGES? → RETURN False
        ↓
ATOMIC SAVE
        ↓
RETURN True
```

Commit rules:

- no file write occurs before all requested timeframes succeed;
- the existing on-disk document remains untouched if any timeframe fails;
- only one atomic replacement is performed for a successful multi-timeframe update;
- unrelated timeframe records remain byte/semantically intact except for deterministic serialization changes caused by a successful transaction;
- a persistence failure means the update is unsuccessful even if in-memory processing succeeded.

## 15.2 No-op behavior

No new completed candle and no changed current snapshot:

```text
update_market_data(...) -> False
```

No unnecessary file rewrite is required.

A current-snapshot change with no new completed candle still counts as a market-data file change when `--current` is active.

## 15.3 Multi-timeframe execution

For:

```text
--timeframes H4 M15 M5
```

the provider is called independently for each timeframe, but all changes are reconciled into the one symbol document.

Do not confuse `--timeframes` with mapper HTF/LTF semantics.

The Market Data CLI simply maintains requested market-data series.

---

# 16. DEBUG AND ERROR CONTRACT

## 16.1 run

Signature:

```python
def run(request: MarketDataRequest) -> int:
    ...
```

Responsibilities:

- instantiate the configured provider;
- call `update_market_data`;
- map defined runtime failures to a non-zero exit status;
- emit diagnostics only when debug is enabled.

## 16.2 Debug

Debug output:

```text
stderr -> terminal only
```

Never:

- write debug to JSON;
- print candle transport data to stdout;
- forward stderr to Mapper as data;
- use stdout as a machine-readable data API.

Normal successful execution must be user-silent.

## 16.3 Error categories

Use explicit, readable error messages.

Every failure must belong to exactly one primary category and must stop the affected operation. Categories are prioritized from boundary to persistence:

1. CLI/input error
2. symbol/path validation error
3. provider configuration error
4. provider acquisition error
5. provider response/schema error
6. timestamp/timezone error
7. completion-state error
8. normalization/OHLC error
9. volume-data validation error
10. data-integrity/merge conflict
11. retention/state validation error
12. JSON load/schema error
13. JSON serialization error
14. atomic-write/retry failure

Rules:

- no failure is converted to an empty successful result;
- no malformed persisted document is silently replaced;
- expected retryable I/O failures are retried only within the finite configured limit;
- after retry exhaustion, the operation fails;
- failure must not partially persist the current symbol transaction;
- debug output may include the category and concise cause, but never raw provider secrets or credentials.

A failure must identify:

- symbol;
- timeframe when applicable;
- affected timestamp/range when available;
- concise reason.

Do not swallow exceptions and continue with malformed state.

---

# 17. MAIN ENTRYPOINT

## 17.1 main

Signature:

```python
def main(argv: Sequence[str] | None = None) -> int:
    ...
```

Execution order:

```text
parse_market_data_request
        ↓
validate_request
        ↓
create_provider
        ↓
run
        ↓
exit code
```

## 17.2 __main__ guard

Use:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

This keeps the module importable for unit tests and future internal reuse without coupling it to the mapper.

---

# 18. VARIABLE NAMING CONTRACT

The project-wide developer-agent naming and portability rules in `specifications/agent_directives.md` apply. This section defines Market Data-specific naming examples.

Prefer names with semantic ownership.

## 18.1 CLI/runtime variables

```text
argv
args
request
symbol
timeframes
start_time
end_time
last_closed_only
live
debug
```

## 18.2 Provider variables

```text
provider
provider_candle
provider_candles
provider_response
source_timestamp
source_timezone
provider_timestamp
provider_metadata
```

## 18.3 Normalization variables

```text
normalized_candle
normalized_candles
timestamp
completion_time
open_price
high_price
low_price
close_price
total_volume
orderflow_buy
orderflow_sell
```

Avoid single-letter financial variables such as `o`, `h`, `l`, `c` in implementation logic except in tightly scoped mathematical expressions.

## 18.4 Persistence variables

```text
data_path
market_data
timeframe_state
existing_candles
incoming_candles
merged_candles
current_snapshot
temporary_path
serialized_json
```

Avoid vague names such as `data`, `obj`, `item`, `tmp` unless the scope is trivial.

---

# 19. PURE-FUNCTION BOUNDARIES

Prefer pure functions for:

```text
normalize_symbol
normalize_timeframe
parse_calendar_point
derive_completion_time
build_candle_id
validate_normalized_candle
merge_completed_candles
deduplicate_candles
sort_candles
apply_candle_retention
build_current_snapshot
```

These functions should not:

- access files;
- access network;
- inspect global mutable state;
- depend on wall-clock time unless explicitly passed a `now` argument.

Side effects must be concentrated in:

```text
provider methods
load_market_data
save_market_data_atomic
clear_completed_current_snapshot
update_timeframe
update_market_data
run
```

This separation makes future provider and storage changes easier.

---

# 20. EXTENSION POINTS

## 20.1 New provider

To add MetaTrader, broker API, replay data, or another provider later:

1. implement `MarketDataProvider`;
2. map provider records into `ProviderCandle`;
3. register the provider in `create_provider`;
4. do not change normalization, merge, retention, or persistence semantics unless the provider genuinely exposes a new approved data capability.

The mapper-facing JSON schema must remain unchanged.

## 20.2 New market-data source capability

For a future capability such as Level-2/orderflow:

- extend `ProviderCandle` / provider mapping only as needed;
- preserve existing `volume.total`, `volume.ohlc`, and `volume.orderflow` branches;
- do not convert a new observed source into an estimated source;
- preserve provenance through the relevant branch.

## 20.3 Internal module split later

If `market_data.py` becomes too large, split along existing boundaries:

```text
market_data_cli.py
market_data_provider.py
market_data_normalization.py
market_data_storage.py
```

This is a future implementation option, not required V1 architecture.

The current function ownership should make such a split possible without changing the persisted JSON schema or external CLI.

---

# 21. IMPLEMENTATION ORDER FOR THE DEVELOPER AGENT

Implement in this exact dependency order:

## Phase 0 — contract fixtures

Before writing provider code, create deterministic in-memory fixtures for:

- one completed candle;
- one incomplete/current candle;
- one empty timeframe state;
- one conflicting duplicate candle;
- one malformed candle;
- one historical reacquisition range;
- one current-only refresh;
- one multi-timeframe transaction where one timeframe fails.

Use these fixtures throughout unit tests so the contract is executable without network access.

## Phase 1 — skeleton

Create:

```text
constants
data models
base class
main/run shell
```

Do not connect the provider yet.

## Phase 2 — CLI

Implement:

```text
build_argument_parser
parse_market_data_request
validate_request
normalize_symbol
normalize_timeframe
parse_calendar_point
```

Verify `--help` and invalid-combination handling.

## Phase 3 — persistence

Implement:

```text
get_market_data_path
load_market_data
ensure_timeframe_state
update_available_bounds
save_market_data_atomic
```

Test create/load/atomic replacement/deterministic serialization.

## Phase 4 — normalization

Implement:

```text
derive_completion_time
build_candle_id
is_candle_complete
normalize_provider_candle
normalize_provider_candles
validate_normalized_candle
```

Test malformed values, completion, identity, UTC, OHLC integrity, and Decimal handling.

## Phase 5 — provider

Implement:

```text
YahooChartsProvider.fetch_range
YahooChartsProvider.fetch_latest_completed
YahooChartsProvider.fetch_current
```

Keep all Yahoo-specific parsing inside the provider adapter.

## Phase 6 — merge and retention

Implement:

```text
deduplicate_candles
sort_candles
merge_completed_candles
apply_candle_retention
build_current_snapshot
clear_completed_current_snapshot
```

Test repeated downloads, conflicts, retention and completed/current transitions.

## Phase 7 — timeframe orchestration

Implement:

```text
resolve_acquisition_range
fetch_completed_candles
fetch_latest_completed_candle
fetch_current_candle
update_timeframe
```

## Phase 8 — symbol-level orchestration

Implement:

```text
update_market_data
run
main
```

Verify one file containing all requested timeframes.

## Phase 9 — integration verification

Verify:

```text
historical range acquisition
lastclosed
lastclosed + live
current-only current refresh
one-new-candle incremental update
missed-multiple-candle batch
no-op
reacquisition outside retention
atomic persistence
multi-timeframe isolation
mapper-readable JSON boundary
```

Do not add SMC analysis logic.

---

# 22. REQUIRED TEST STRUCTURE

The global developer-agent naming, portability, prompt-efficiency, and test-batching rules in the repository-wide agent contract apply to Market Data. This specification does not create or prescribe a repository-root `test/` directory.

The developer agent must add focused tests around the module boundaries using the repository's currently approved test-placement rules. Temporary fixtures, downloaded provider payloads, debug dumps, and other development-only test artifacts belong under `dev_tmp/`; they are not test deliverables.

Test names:

```text
test_parse_market_data_request_lastcandle_conflicts
test_parse_market_data_request_lastcandle_live_allowed
test_parse_market_data_request_requires_timeframe
test_parse_iso8601_returns_utc
test_normalize_source_time_with_timezone
test_reject_naive_source_time_without_timezone
test_local_time_conversion_is_dst_aware
test_build_candle_id_is_deterministic
test_normalize_provider_candle_uses_decimal
test_normalize_provider_candle_rejects_invalid_ohlc
test_incomplete_candle_is_not_persisted_to_candles
test_current_snapshot_is_separate_from_completed_series
test_merge_completed_candles_deduplicates
test_merge_completed_candles_rejects_conflicting_identity
test_sort_candles_is_strictly_chronological
test_apply_candle_retention_evicts_oldest
test_available_bounds_ignore_current_snapshot
test_atomic_save_replaces_target
test_atomic_save_retries_transient_write_failure
test_lastcandle_fetches_exactly_one_completed_candle_per_timeframe
test_lastcandle_live_refreshes_current_independently
test_noop_does_not_rewrite_unchanged_market_data
test_multitimeframe_updates_share_one_symbol_file
test_symbol_output_directory_is_resolved_automatically
test_market_data_path_stays_within_symbol_directory
test_rejects_unsafe_symbol_path_component
test_multitimeframe_update_does_not_cross_contaminate
test_missing_range_can_be_reacquired
test_live_only_refresh_does_not_request_historical_range
test_failed_timeframe_update_does_not_persist_partial_symbol_change
test_historical_reacquisition_range_is_protected_from_immediate_eviction
test_end_only_request_requires_existing_range
test_empty_series_incremental_update_fetches_latest_completed
test_completion_boundary_is_timezone_independent
test_provider_completion_hint_cannot_override_canonical_boundary
test_current_snapshot_replaces_same_candle_id
test_new_current_candle_replaces_old_snapshot
test_completed_current_candle_moves_to_completed_series
test_current_snapshot_never_changes_available_bounds
test_merge_preserves_existing_completed_candle
test_conflicting_same_id_candle_fails
test_retention_keeps_protected_range
test_retention_does_not_count_current_snapshot
test_load_market_data_rejects_malformed_document
test_load_market_data_rejects_invalid_bounds
test_save_failure_leaves_previous_json_intact
test_provider_empty_result_is_not_provider_error
test_provider_failure_is_not_empty_success
test_incremental_range_starts_after_available_end
test_explicit_end_boundary_is_completion_time_based
test_fetch_completed_candles_filters_by_completion_time
test_fetch_latest_completed_selects_max_completion_time
test_fetch_current_ignores_completed_records
test_successful_live_refresh_without_current_clears_stale_snapshot
test_provider_failure_preserves_previous_persisted_state
test_decimal_persistence_is_plain_string
test_decimal_persistence_round_half_even
test_json_bounds_match_completed_series
test_timeframe_update_has_no_direct_file_side_effect
```

Provider-dependent tests must use provider test doubles/mocks; core tests must not require live provider access. Core normalization, merge, retention and persistence tests must not require live provider access.

---

# 23. DEVELOPER-AGENT RULES

Before implementation, treat the existing `smc_mapper_specification.md` as the mapper-facing market-data boundary and this file as the detailed `market_data.py` implementation contract.

Do not:

- redefine canonical SMC rules;
- change the mapper JSON contract;
- invent new mapper CLI options;
- add price-basis configuration;
- add candle-level exclusive `volume_method`;
- silently downgrade unavailable provider data;
- fabricate candles;
- overwrite persisted completed candle identity/content silently;
- use current candles in structural analysis;
- introduce runtime dependency on legacy files.

When an implementation decision is not specified here, choose the smallest direct implementation that preserves the existing external contract and document the decision in `AGENT_REVIEW.md`.

After implementation, update `AGENT_REVIEW.md` with the completed audit/test result before committing.

---

# 24. NORMATIVE RUNTIME FLOW

The complete V1 execution flow is:

```text
CLI
 ↓
MarketDataRequest
 ↓
validate input
 ↓
create provider
 ↓
resolve <DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json
  ↓
load symbol-scoped market-data document
 ↓
for each requested timeframe
   ↓
   resolve acquisition range
   ↓
   provider fetch
   ↓
   completion classification
   ↓
   normalization
   ↓
   validation
   ↓
   completed/current split
   ↓
   merge + deduplicate
   ↓
   retention
   ↓
   availability bounds
 ↓
persist complete symbol document atomically
 ↓
exit
```

For `--current`, current-snapshot refresh is independent of completed-candle acquisition. In current-only mode it is the current-data operation; with `--lastclosed` it runs alongside the exact latest-completed-candle acquisition.

For `--lastclosed`, the completed-candle acquisition branch returns exactly one latest completed candle per requested timeframe.

The output of this process is only the normalized market-data JSON state. Canonical SMC analysis begins downstream in `smc_mapper.py`.

---

# 25. DEFINITION OF DONE

`market_data.py` is implementation-complete when:

- the documented CLI exactly matches implementation;
- all requested timeframes are stored in one symbol JSON file under `<DATA_ROOT>/<SYMBOL>/`;
- completed candles and current snapshots are strictly separated;
- provider-specific data does not leak into normalized semantics;
- UTC timestamps and completion boundaries are deterministic;
- OHLC values and supported volume values use deterministic Decimal handling;
- repeated acquisition is idempotent;
- conflicting persisted candle identity is detected rather than silently overwritten;
- retention is bounded per timeframe;
- missing historical ranges can be reacquired;
- JSON persistence is atomic;
- normal runtime is silent;
- debug output is stderr-only;
- no legacy runtime dependency exists;
- unit tests cover the module boundaries;
- the resulting JSON is directly consumable by `smc_mapper.py` without adapter logic inside the mapper;
- every acquisition mode follows the documented decision table;
- no incomplete candle can enter `candles[]`;
- no completed candle can coexist with the same candle ID in `current`;
- a failed multi-timeframe update cannot leave a partially persisted symbol document;
- repeated provider acquisition is idempotent;
- completed candle conflicts fail closed;
- explicit historical reacquisition remains retained through the current processing transaction;
- `available_start/end` represent completed-candle bounds only;
- provider errors, malformed records, and malformed persisted JSON remain distinguishable failure classes.

# 21. IMPLEMENTATION MODULE DECOMPOSITION

The implementation is split by functional ownership while preserving market_data.py as the root CLI entry point.

Module tree:

market_data.py -> MARKET_DATA/cli.py -> models.py, provider.py, normalization.py, persistence.py, service.py

No provider cache file is part of the permanent repository structure. Provider request-local/in-memory state is an implementation optimization only. The canonical mapper-facing document remains <DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json.

## 21.1 Module ownership

| Module | Ownership |
|---|---|
| market_data.py | root executable entry point only |
| MARKET_DATA/models.py | domain models and provider-neutral constants |
| MARKET_DATA/provider.py | provider abstraction and Yahoo transport |
| MARKET_DATA/normalization.py | UTC conversion, completion, Decimal conversion, validation and identity |
| MARKET_DATA/persistence.py | symbol paths, JSON validation, serialization and atomic save |
| MARKET_DATA/service.py | acquisition planning, merge, retention and timeframe/symbol orchestration |
| MARKET_DATA/cli.py | argparse, request parsing, validation and process execution |
| provider-local request state | transient provider optimization; never the canonical mapper document |

## 21.2 UML-style component relationship

market_data.py -> cli.py -> service.py -> provider.py
                              -> normalization.py
                              -> persistence.py
                              -> models.py
provider.py -> external provider API and transient request-local provider state
persistence.py -> <DATA_ROOT>/<SYMBOL>/<SYMBOL>_marketdata.json

Dependency direction is one-way: CLI -> service -> provider/normalization/persistence/models. Provider and normalization must not import service or CLI. Persistence must not perform acquisition or SMC interpretation.

## 21.3 Variable naming contract

| Variable | Meaning |
|---|---|
| request | validated MarketDataRequest |
| symbol | normalized instrument identity |
| timeframe | canonical timeframe identifier |
| start_time / end_time | canonical UTC boundaries |
| provider | selected MarketDataProvider |
| provider_candle | provider record before normalization |
| normalized_candle | validated NormalizedCandle |
| incoming_candles | newly acquired completed candles |
| existing_candles | persisted completed candle records |
| market_data | complete symbol document |
| timeframe_state | one timeframe persisted state |
| acquisition_start / acquisition_end | resolved acquisition boundaries |
| retention_limit | completed-candle storage limit |
| current_snapshot | persisted in-progress candle |
| data_directory | common data root |
| market_data_path | canonical symbol JSON path |
| changed | whether resulting state differs from original |

Do not use opaque domain-state names such as data, item, obj, tmp, helper or result2.

## 21.4 Function ownership matrix

| Function | Owner | Responsibility |
|---|---|---|
| build_argument_parser | cli.py | construct CLI |
| parse_market_data_request | cli.py | parse request |
| validate_request | cli.py | request invariants |
| normalize_symbol | cli.py | symbol normalization |
| normalize_timeframe | cli.py | timeframe normalization |
| parse_calendar_point | cli.py | UTC timestamp parsing |
| create_provider | provider.py | provider selection |
| fetch_range | provider.py | provider range acquisition |
| fetch_latest_completed | provider.py | latest provider record |
| fetch_current | provider.py | current provider record |
| derive_completion_time | normalization.py | interval boundary |
| is_candle_complete | normalization.py | completion classification |
| build_candle_id | normalization.py | stable identity |
| normalize_provider_candle | normalization.py | provider-to-domain conversion |
| normalize_provider_candles | normalization.py | batch conversion |
| validate_normalized_candle | normalization.py | integrity validation |
| deduplicate_candles | service.py | identity deduplication |
| sort_candles | service.py | chronological ordering |
| merge_completed_candles | service.py | immutable idempotent merge |
| apply_candle_retention | service.py | bounded retention |
| resolve_acquisition_range | service.py | request-mode planning |
| fetch_completed_candles | service.py | completed acquisition path |
| fetch_latest_completed_candle | service.py | latest completed path |
| fetch_current_candle | service.py | current path |
| build_current_snapshot | service.py | current serialization |
| clear_completed_current_snapshot | service.py | current/completed separation |
| ensure_timeframe_state | persistence.py | timeframe initialization |
| update_available_bounds | persistence.py | completed-only bounds |
| create_empty_market_data | persistence.py | empty document |
| get_symbol_data_directory | persistence.py | symbol directory |
| get_market_data_path | persistence.py | canonical output path |
| load_market_data | persistence.py | load and validate |
| serialize_decimal | persistence.py | deterministic Decimal string |
| serialize_market_data | persistence.py | deterministic JSON |
| save_market_data_atomic | persistence.py | atomic write |
| update_timeframe | service.py | one-timeframe transaction |
| update_market_data | service.py | symbol transaction |
| run | cli.py | process execution |
| main | market_data.py | root entry point |

## 21.5 State-flow UML

MarketDataRequest -> resolve_acquisition_range -> provider acquisition -> normalization/validation -> merge/current -> retention -> availability -> symbol validation -> atomic save or no-op.

## 21.6 Structural implementation rule

Any implementation change affecting interfaces, fields, paths, state transitions, CLI options or ownership boundaries must update this specification in the same iteration before implementation is accepted.

## 13.1.1 Open-start `--range -END`

The open-start Market Data range uses the latest retained completed candle as its lower boundary for each
requested timeframe.

Examples:

    python market_data.py --symbol EURUSD --timeframes M1 M5 --range -2026.10.20
    python market_data.py --symbol EURUSD --timeframes M1 M5 --range -2026.10.10@05:00
    python market_data.py --symbol EURUSD --timeframes M1 M5 --range -2026.10.10@05.00

For each timeframe:
- `available_end` is the latest persisted completed-candle timestamp and becomes the resolved start;
- the explicit END is converted to the existing canonical exclusive range boundary;
- the latest persisted candle may be fetched again at the inclusive lower boundary and deduplicated by candle ID;
- no start point is fabricated when the timeframe has no retained completed history;
- this mode is historical acquisition and is not equivalent to `--current`.

