# SMC_Mapper Full Specification — Index

**Status:** Current specification index.  
**Purpose:** Navigate the V1 product specification set. This file is an index only; it does not redefine implementation rules, canonical SMC semantics, runtime contracts, or policy.

## 1. Authority hierarchy

| Authority / document | Role |
|---|---|
| `.agents/skills/smc/` | Canonical SMC semantics |
| `specifications/market_data_specification.md` | Market Data implementation contract |
| `specifications/smc_mapper_specification.md` | Mapper implementation and persistence contract |
| `specifications/smc_monitor_specification.md` | Monitor orchestration, target/RR and alert contract |
| `AGENT_REVIEW.md` | Historical audit/review record; not normative |

A more specific owner document takes precedence over this index for implementation details.

## 2. Specification map

### Market Data — `market_data_specification.md`

Owns:

- provider abstraction and acquisition;
- timestamp normalization and canonical completion;
- completed-candle/current-snapshot separation;
- normalized OHLC and volume data;
- `NONE | OHLC | ORDERFLOW | BOTH` volume-method source handling;
- merge, deduplication and retention;
- symbol-scoped market-data JSON;
- atomic persistence;
- acquisition planning and incremental updates;
- CLI, diagnostics, errors and Market Data tests.

See sections **0–25** of the Market Data specification.

### Mapper — `smc_mapper_specification.md`

Owns:

- Mapper CLI and timeframe relationship;
- analysis identity and requested/effective boundaries;
- consumption of persisted Market Data;
- candle eligibility and structural processing boundary;
- HTF/LTF synchronization and bootstrap;
- Dealing Range history;
- canonical POI storage representation;
- POI volume/delta analytics;
- Mapper/Monitor checkpoint boundary;
- structures JSON and atomic checkpoint persistence;
- Mapper implementation architecture, tests and completion criteria.

See sections **0–18** of the Mapper specification.

### Monitor — `smc_monitor_specification.md`

Owns:

- Monitor CLI and scheduling;
- persisted input discovery;
- Market Data/Mapper process orchestration;
- current market reference;
- canonical state consumption;
- target representation and runtime target resolution;
- target clearance;
- optional `--rr` policy;
- trading-session runtime context;
- alert eligibility and deduplication;
- symbol/analysis isolation;
- checkpoint consumption;
- fail-closed behavior;
- Monitor implementation, tests and completion criteria.

See sections **0–25** of the Monitor specification.

## 3. Shared architecture references

Persistent files are symbol-scoped:

```text
<DATA_ROOT>/<SYMBOL>/
    <SYMBOL>_marketdata.json
    <SYMBOL>_structures.json
```

File ownership and the machine-readable process boundary are defined by the owner specifications:

- Market Data → `*_marketdata.json`
- Mapper → `*_structures.json`
- Monitor → transient runtime state only

The canonical time-domain rules are owned by the Market Data and Mapper specifications, with Monitor consuming canonical UTC for scheduling and runtime evaluation.

The current-snapshot boundary is owned by Market Data and consumed by Monitor; the Mapper consumes completed candles only.

Target, RR, alert, and execution-notification behavior is owned by the Monitor specification, subject to canonical downstream SMC authority in Layer 7/8.

## 4. Change rule

When a new requirement belongs to one component, update that component's owner specification first. Update this file only when the specification map, authority hierarchy, or top-level architecture navigation changes.

**This file is intentionally non-normative and index-oriented.**
