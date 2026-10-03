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

## 1.1 V1 single-file structure

V1 is one executable file:

```text
market_data.py
```

Keep the implementation internally modular by code sections and small single-purpose functions.

Implementation source order:

```text
1. module docstring
2. standard-library imports
3. optional typing imports
4. module constants
5. data models / classes
6. CLI argument construction
7. input parsing + validation
8. provider abstraction
9. concrete provider adapter(s)
10. timestamp/completion helpers
11. normalization helpers
12. candle validation helpers
13. merge/deduplication helpers
14. retention helpers
15. JSON load/save helpers
16. update orchestration
17. CLI entrypoint
18. __main__ guard
```

Do not split into multiple modules in V1 unless implementation complexity genuinely requires it. The internal boundaries must already make a later split mechanical.

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
    last_candle_only: bool
    live: bool
    debug: bool
```

Variable name: `request`.

## 3.2 Provider candle

Use `ProviderCandle`.

Provider-facing state may contain provider-specific types/metadata. Required conceptual fields are:

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

Core processing uses the explicit domain models above. Persistence helpers may use plain Python dictionaries/lists while translating to and from the approved JSON schema.

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
parse_iso8601
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
--starttime ISO8601
--endtime ISO8601
--lastcandle
--live
--debug
--help
```

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

- parse CLI arguments;
- normalize primitive input forms;
- construct `MarketDataRequest`.

Rules:

- at least one timeframe is required;
- duplicate timeframes must be rejected or deterministically normalized once;
- unsupported timeframes must fail explicitly;
- `--lastcandle` is mutually exclusive with `--starttime`;
- `--lastcandle` is mutually exclusive with `--endtime`;
- `--lastcandle --live` is valid;
- `--starttime` and `--endtime` may be used together for historical range acquisition;
- invalid temporal ordering must fail explicitly;
- do not silently infer a different symbol or timeframe.

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
- validate membership in `SUPPORTED_TIMEFRAMES`;
- return one canonical timeframe string.

## 5.5 parse_iso8601

Signature:

```python
def parse_iso8601(value: str) -> datetime:
    ...
```

Rules:

- return timezone-aware UTC datetime;
- reject malformed or ambiguous timestamps;
- normalize explicit offsets to UTC;
- never return a naive datetime.

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
- use the approved timeframe duration map;
- do not depend on local timezone;
- do not use wall-clock time to alter historical completion boundaries.

## 7.3 Current snapshot separation

Completed candles and current snapshot are separate stores.

Rules:

```text
completed -> candles[]
in-progress -> current
```

A current snapshot:

- may change on repeated `--live` executions;
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
- when `protected_end` is supplied, only candles at or before that boundary are protected by the requested range;
- when `protected_start` is supplied and `protected_end` is absent, protection extends through the newest currently available completed candle;
- protected candles are retained even when this temporarily exceeds `retention_limit`;
- once the protected range is no longer requested, normal rolling retention may evict old candles;
- retention is operational storage policy only.

The function must be pure with respect to its inputs.

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

Each completed candle contains candle_id, timestamp, completion_time, open, high, low, close and the volume object defined in Section 3.8. Timestamp and completion_time are UTC ISO-8601 values. Persisted numeric price and volume values use the deterministic decimal-compatible string representation.

The current field uses the same serialized candle shape when present, but it is an in-progress runtime snapshot. It does not contribute to available_start/available_end and is never a completed-candle substitute.

The mapper may deserialize this schema into its own read-only view model. It must not import Market Data domain classes merely to read the JSON boundary.

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
- `end_time` only: use the persisted `available_start` for the timeframe as the acquisition start; if no persisted completed range exists, fail explicitly and require `--starttime`;
- honor requested boundaries;
- do not invent candles outside requested scope.

### Live-only current refresh

When `live=True`, `last_candle_only=False`, and neither `start_time` nor `end_time` is supplied:

- fetch the latest provider candle needed for the current snapshot for each requested timeframe;
- persist it under the timeframe's `current` field while incomplete;
- if it is already completed when evaluated, route it through the completed-candle path and clear the matching current snapshot;
- do not fabricate or infer a historical acquisition range;
- do not require a new completed candle for the invocation to be valid.

### Last-candle mode

When `last_candle_only=True`:

- retrieve exactly the latest completed candle for the timeframe;
- do not treat `current` as the result;
- do not retrieve an arbitrary recent window.

### Incremental mode

When neither historical boundaries nor `--lastcandle` apply and `live=False`:

- if the timeframe has persisted completed candles, acquire only newly completed candles after the persisted `available_end`;
- if the timeframe has no persisted completed candles, acquire exactly the latest completed candle;
- preserve chronological order;
- allow multiple newly completed candles when execution was missed.

This function plans provider acquisition only. It does not manipulate mapper checkpoints.

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

1. provider `fetch_range`;
2. provider records normalized;
3. completion filtered/validated;
4. normalized candles validated;
5. deterministic chronology returned.

The function returns only completed canonical market-data candles.

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

## 15.2 No-op behavior

No new completed candle and no changed current snapshot:

```text
update_market_data(...) -> False
```

No unnecessary file rewrite is required.

A current-snapshot change with no new completed candle still counts as a market-data file change when `--live` is active.

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

At minimum distinguish:

```text
CLI/input error
provider acquisition error
provider normalization error
completion-state error
data integrity error
JSON persistence error
atomic-write/retry failure
```

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
last_candle_only
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
parse_iso8601
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
parse_iso8601
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
lastcandle
lastcandle + live
live-only current refresh
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

The developer agent must add focused tests around the module boundaries.

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

For `--live`, current-snapshot refresh is independent of completed-candle acquisition. In live-only mode it is the current-data operation; with `--lastcandle` it runs alongside the exact latest-completed-candle acquisition.

For `--lastcandle`, the completed-candle acquisition branch returns exactly one latest completed candle per requested timeframe.

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
- the resulting JSON is directly consumable by `smc_mapper.py` without adapter logic inside the mapper.
