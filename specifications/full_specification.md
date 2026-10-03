# SMC_Mapper Full Specification — Index

**Status:** Current specification index.  
**Purpose:** Navigation only. This file does not define implementation rules, runtime behavior, canonical SMC semantics, or trading policy.

## 1. Authority hierarchy

| Authority / document | Role |
|---|---|
| `.agents/skills/smc/` | Canonical SMC semantics |
| `specifications/market_data_specification.md` | Market Data implementation contract |
| `specifications/smc_mapper_specification.md` | Mapper implementation and persistence contract |
| `specifications/calendar_specification.md` | Economic calendar acquisition, parsing, normalization, single global `calendar.json`, symbol relevance queries and explicit deletion contract |
| `specifications/smc_monitor_specification.md` | Monitor orchestration, News warning, target/RR and alert contract |
| `AGENT_REVIEW.md` | Historical audit/review record; not normative |

The owning specification is authoritative for its component. This file must never become a second source of implementation truth.

## 2. Specification map

### Market Data — `market_data_specification.md`

Detailed contract: sections **0–25**.

Primary ownership:
- provider abstraction and acquisition;
- timestamp normalization and completion;
- completed/current separation;
- normalized OHLC and parallel volume branches;
- merge, deduplication and retention;
- symbol-scoped Market Data JSON;
- atomic persistence;
- CLI, errors, diagnostics and tests.

### Mapper — `smc_mapper_specification.md`

Detailed contract: sections **0–18**.

Primary ownership:
- Mapper CLI and timeframe modes;
- analysis identity and boundaries;
- persisted Market Data consumption;
- HTF/LTF synchronization and bootstrap;
- canonical processing orchestration;
- Dealing Range and POI structural state;
- POI volume/delta enrichment;
- structures JSON and checkpoint persistence;
- Mapper tests and definition of done.

### Calendar — `calendar_specification.md`

Detailed contract: sections **0–14**.

Primary ownership:
- ForexFactory acquisition and parsing;
- normalized CalendarEvent contract;
- canonical UTC event time;
- single global `calendar.json` persistence and coverage;
- symbol relevance filtering;
- local time-based query API;
- explicit deletion and no automatic retention;
- atomic Calendar persistence;
- Calendar error/test contract.

### Monitor — `smc_monitor_specification.md`

Detailed contract: sections **0–25**.

Primary ownership:
- Monitor CLI and scheduling;
- persisted analysis discovery;
- Market Data / Mapper orchestration;
- Calendar subprocess orchestration and News warning evaluation;
- current market reference;
- canonical state consumption;
- target representation, resolution and clearance;
- optional RR policy;
- sessions;
- alerts and deduplication;
- symbol/analysis isolation;
- fail-closed runtime behavior;
- Monitor tests and definition of done.

## 3. Cross-file navigation

Use these owner sections when implementing cross-component behavior:

| Concern | Owner section |
|---|---|
| Market Data JSON schema | Market Data §12 |
| Market Data acquisition/update flow | Market Data §§13–15 |
| Mapper input/time boundaries | Mapper §2 |
| Mapper analysis identity/state | Mapper §3 |
| Mapper/Monitor handoff | Mapper §10 and Monitor §§4–5 |
| Mapper checkpoint persistence | Mapper §16 and Monitor §14 |
| Current market reference | Monitor §7 |
| Canonical state consumption | Monitor §8 |
| Target / RR / alert behavior | Monitor §§9–12 |
| Runtime isolation / failure handling | Monitor §§13–16 |

## 4. Change rule

When a new requirement belongs to one component, change that component's owner specification first. Change this index only when the authority hierarchy, ownership map, or navigation changes.

**This file is intentionally non-normative and index-oriented.**
