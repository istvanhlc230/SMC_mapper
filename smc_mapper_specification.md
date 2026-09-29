# SMC Mapper Specification

**Status:** Working specification. Sections are approved incrementally.  
**Scope:** Functional and implementation specification for the future `smc_mapper.py`.  
**Canonical authority:** `.agents/skills/smc/` remains the sole authority for canonical SMC semantics. This document does not redefine those rules.

---

# A. INPUT / ORCHESTRATION

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

When both are supplied:

`HTF >= LTF`

An invalid relationship is an input error.

The mapper must never silently swap or otherwise correct the supplied timeframes.

---

## A5. HTF Pullback Validation

HTF pullback validation is enabled only when **both HTF and LTF are explicitly supplied**.

### Both supplied

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

The mapper must never automatically select or invent an HTF when only one timeframe is supplied.

---

## A6. Analysis order

When both timeframes are supplied:

`HTF -> LTF`

The HTF analysis is completed first.

The LTF analysis may consume HTF structural context where required, but the LTF analysis must never modify the HTF result.

When only one timeframe is supplied, only that timeframe is analyzed.

---

## A7. Start time

`--starttime` defines the requested start of the analysis window.

It may be specified as:

- a date, or
- an exact datetime.

Examples:

`--starttime 2026-09-01`

`--starttime 2026-09-01T09:30:00`

Earlier candles may be fetched when required for structural bootstrap/warm-up.

The mapper must distinguish:

- `requested_start`
- `effective_start`

If the requested history is unavailable, the mapper starts from the earliest available candle and reports this explicitly.

Missing historical data must never be fabricated.

---

## A8. End time

`--endtime` is optional.

It may be specified as:

- a date, or
- an exact datetime.

Examples:

`--endtime 2026-09-29`

`--endtime 2026-09-29T15:30:00`

If omitted, use the latest available completed candle at or before the current time.

If supplied, use the latest completed candle whose timestamp is less than or equal to the requested end time.

An incomplete/current candle must never enter canonical analysis.

---

## A9. Independent history per timeframe

HTF and LTF may have different available history ranges.

Each timeframe is bootstrapped from its own earliest available data.

Example:

- HTF: `2026-06-01 -> 2026-09-29`
- LTF: `2026-01-01 -> 2026-09-29`

The longer LTF history must not be truncated merely because the HTF history is shorter.

The absence of HTF data before its available start does not imply that HTF structure did not exist.

---

## A10. Missing HTF context

When an LTF canonical rule requires HTF pullback validation but the required HTF historical context is unavailable, represent the condition explicitly as:

`HTF_CONTEXT_UNAVAILABLE`

Do not convert it to:

`HTF_VALID_PULLBACK = FALSE`

Therefore:

`HTF_CONTEXT_UNAVAILABLE != HTF_VALID_PULLBACK_FALSE`

If a canonical decision depends on unavailable HTF context, the decision must remain unresolved / fail closed.

---

## A11. history_no

`history_no` specifies the maximum number of most recent **structurally distinct state snapshots** retained per timeframe.

History is rotating:

- newest snapshot is inserted at index `0`;
- existing snapshots shift toward higher indexes;
- when capacity N is exceeded, the oldest snapshot is removed.

The retention model is therefore **first-in, last-out** for the retained snapshot window.

Example with `history_no = 3`:

```
S1        -> [S1]

S2        -> [S2, S1]

S3        -> [S3, S2, S1]

S4        -> [S4, S3, S2]
                         S1 removed
```

A repeated mapper execution that produces no structural change must not create a duplicate snapshot.

---

## A12. Structural snapshot identity

Each stored structural snapshot should contain:

- `structure_id`
- `structure_hash`
- `formation_time`

`formation_time` identifies when the complete structural state was formed.

`structure_hash` is a deterministic fingerprint of the relevant complete structural state and is used for structural change detection.

The history index is positional only and is not the permanent identity of the snapshot.

The exact `structure_id` generation rule remains to be finalized.

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

---

## A14. Stored state

The mapper JSON stores **structural analysis only**.

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
- structural history;
- structure identity/change metadata.

The mapper must not persist dynamic monitoring or trade state such as:

- current market price;
- active trade/order state;
- stop state;
- break-even state;
- trailing state;
- target-hit state.

Those are owned by the monitor.

---

## A15. Input validation

Before analysis, validate at minimum:

- symbol;
- timeframe values;
- HTF/LTF relationship;
- start/end values;
- `starttime < endtime` when both are specified;
- `history_no`;
- timestamp ordering;
- duplicate timestamps;
- timezone validity;
- completed-candle status;
- OHLC integrity;
- required timeframe data availability.

Invalid input must fail explicitly.

---

## A16. Data provider abstraction

The mapper must consume market data through an abstract provider interface.

Initial implementation:

`Yahoo Charts`

The provider layer must be replaceable without changing canonical SMC logic.

Future adapters are expected to include:

- Pine Script;
- MetaTrader.

Provider-specific API details must remain outside the canonical SMC engine.

The canonical engine consumes normalized candle data only.

---

## A17. Bootstrap

Structural state must be constructed by processing candles chronologically:

`earliest effective candle -> latest effective candle`

The mapper must not use a latest-window shortcut that bypasses required structural bootstrap.

---

## A18. Monitor boundary

The monitor consumes mapper JSON and owns dynamic monitoring functions, including:

- current-price monitoring;
- execution monitoring;
- target monitoring;
- alerts/notifications;
- determining when a new mapper analysis is required.

The monitor must not redefine canonical SMC semantics.

When re-analysis is required, the monitor may invoke the mapper for the relevant symbol and timeframe configuration.

---

## A19. Configuration

No separate mapper configuration file is required.

Mapper behavior is controlled by:

- CLI parameters;
- explicit defaults;
- provider implementation;
- canonical SMC skill.

No mapper configuration file is to be introduced for timeframe selection, history retention or analysis window.

---

# B. CANDLE / MARKET DATA NORMALIZATION

## B1. Provider boundary

The provider layer receives provider-specific market data and converts it into a provider-independent normalized candle series.

```
Provider-specific data
        ↓
Market Data Normalization
        ↓
Normalized Candle Series
        ↓
Canonical SMC Engine
```

Canonical SMC logic must consume only normalized candle data.

---

## B2. Normalized candle representation

Each normalized candle must contain at minimum:

- `candle_id`
- `timestamp`
- `open`
- `high`
- `low`
- `close`

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

An incomplete/current candle must be excluded from the canonical analysis series.

---

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

The provider/normalization layer must expose the actual available temporal range of each timeframe.

At minimum:

- `available_start`
- `available_end`

This is required because HTF and LTF may have different available history.

The mapper must distinguish:

```
requested time range
effective available time range
```

rather than silently treating unavailable data as absent structure.

---

## B14. Data clipping

After all required bootstrap/warm-up history has been supplied, the mapper determines the effective analysis interval from the requested start/end constraints.

The provider must not prematurely clip away candles required for structural bootstrap.

---

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
