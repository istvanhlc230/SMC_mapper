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

## A11. Closed Dealing Range history and `history_no`

`history_no` specifies the maximum number of **CLOSED DEALING RANGES** retained per timeframe.

The history unit is the canonical closed Dealing Range, not a mapper-run snapshot and not a generic structural-state snapshot.

Only a Dealing Range that has been canonically closed may enter history. The currently open Dealing Range is never a history item.

Retention is newest-first storage with **oldest-first (FIFO) eviction** when capacity is exceeded.

Example with `history_no = 3`:

```
R1 -> [R1]

R2 -> [R2, R1]

R3 -> [R3, R2, R1]

R4 -> [R4, R3, R2]
               R1 evicted
```

Eviction is a storage-retention operation only. A range evicted because of `history_no` remains canonical historical structure; it is not invalidated, deleted semantically, or marked stale.

A repeated mapper execution must not create a duplicate closed range when the same range identity is already retained.

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
- retained closed Dealing Range history;
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
- required timeframe data availability;\n- two-timeframe HTF/LTF mode requirements.

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


---

# C. HTF / LTF CONTEXT & DEPENDENCY MODEL

## C1. Context dependency

Two-timeframe analysis has a strict dependency direction:

`HTF analysis -> HTF structural context -> LTF analysis`

The LTF analysis may consume HTF context.

The LTF analysis must never modify the HTF result.

---

## C2. Point-in-time HTF context

For every LTF evaluation that consumes HTF context, the mapper must use the latest applicable HTF structural snapshot known at or before the LTF evaluation time.

The rule is:

`HTF formation_time <= LTF evaluation_time`

A HTF state that forms later must never be used to evaluate an earlier LTF event.

This prevents future HTF information from leaking backward into historical LTF analysis.

---

## C3. HTF context snapshot reference

When HTF context is consumed by an LTF structural decision, the LTF result must retain sufficient provenance to identify the exact HTF context used.

At minimum, where applicable:

- `htf_context_structure_id`
- `htf_context_structure_hash`
- `htf_context_formation_time`

This creates deterministic HTF-to-LTF provenance.

---

## C4. Read-only context

HTF context supplied to the LTF engine is read-only.

The LTF engine must not:

- modify HTF structural state;
- create or replace HTF structural objects;
- reinterpret HTF canonical semantics;
- write changes into the HTF analysis history.

---

## C5. Context scope

The HTF context contract must expose only information required by canonical downstream rules.

The LTF implementation must not depend on arbitrary internal fields of the complete HTF runtime state.

The exact context fields must be defined by canonical consumer requirements rather than by implementation convenience.

---

## C6. HTF pullback validation states

When HTF pullback validation is not required:

`HTF_PULLBACK_CHECK = NOT_REQUIRED`

When required, the result must distinguish:

- `VALID` — the applicable HTF pullback is canonically valid;
- `INVALID` — sufficient HTF context exists and the applicable pullback is not valid;
- `UNAVAILABLE` — the required HTF historical/context data is unavailable.

`INVALID != UNAVAILABLE`

Missing data must never be converted into a negative structural observation.

---

## C7. HTF history shorter than LTF history

HTF and LTF may have different available history.

Example:

```
HTF: 2026-06-01 -> 2026-09-29
LTF: 2026-01-01 -> 2026-09-29
```

For LTF evaluation times before the first usable HTF context:

`HTF_CONTEXT_UNAVAILABLE`

The LTF analysis may continue through its own available history, but any canonical decision that specifically requires HTF validation must remain unresolved / fail closed until applicable HTF context exists.

---

## C8. HTF context transition

When a new HTF structural snapshot forms:

```
old HTF context
      ↓
new HTF structural snapshot
      ↓
subsequent LTF evaluations use the new context
```

A newly formed HTF snapshot does not retroactively change historical LTF decisions that were made using the previous HTF context.

---

## C9. Single-timeframe mode

When only one timeframe parameter is supplied, the internal representation may use:

`HTF = LTF = selected timeframe`

but no HTF-to-LTF dependency exists and `HTF_PULLBACK_CHECK = NOT_REQUIRED`.

The mapper must not evaluate the selected timeframe as its own Higher Timeframe for canonical Gate 2.

---

## C10. Two-timeframe chronological execution

When both timeframes are supplied:

1. Normalize and bootstrap the HTF series.
2. Analyze the HTF series chronologically.
3. Expose point-in-time HTF structural context.
4. Normalize/bootstrap the LTF series.
5. Analyze the LTF series chronologically.
6. For each LTF evaluation requiring HTF context, consume the applicable point-in-time HTF snapshot.

The mapper must not perform a complete future-aware HTF analysis and then apply its final state to all historical LTF candles.

---

## C11. HTF context provenance and retained history

Every historical LTF structural decision that consumes HTF context must retain sufficient provenance to identify the exact point-in-time HTF structural context used for that decision.

The HTF context provenance is independent of closed Dealing Range history retention.

If the referenced HTF structural context or its containing closed Dealing Range later falls outside the retained `history_no` window, the LTF historical decision must remain self-consistent through its stored provenance metadata. Retention eviction must never cause the mapper to rewrite, reinterpret, or retroactively re-evaluate that LTF decision.

The closed-range history identity:

```
timeframe + start_time + close_time
```

must not be substituted for the point-in-time HTF context provenance required by C2-C3.

---

## C12. Canonical ownership

HTF/LTF dependency handling is orchestration.

Canonical SMC meaning remains owned by the relevant canonical skill layers.

The mapper may transport and align canonical HTF context; it must not invent new HTF pullback, structural, BOS or CHoCH semantics.


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
