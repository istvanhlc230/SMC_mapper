# TRUE SMC — Full Methodology / Platform Gap Audit

Status: **CANONICALIZATION PHASE COMPLETE — C6–C15 CLOSED; PLATFORM-SPECIFIC IMPLEMENTATION REMAINS**

Scope:
- canonical SMC skill under `.agents/skills/smc/`;
- all current `main/knowledgebase/` source material;
- current `main` runtime files;
- identification of source-backed scenarios not yet represented deterministically in the canonical skill;
- assessment of whether the current skill is sufficient to implement a complete trading platform.

Source protection:
- `main/knowledgebase/` was read-only during this audit.
- Runtime/mapper production code was not modified by this audit.

## 1. Executive conclusion

The current skill is sufficient to specify a substantial **market-structure and execution-signal domain model**, including:
- candle-level semantics;
- valid pullbacks and verified pullback extremes;
- IDM lifecycle and classification;
- structural swing qualification;
- 50% standard retracement;
- explicit 2-candle reduced-candle path;
- conditional 38.2%–<50% immediate-HTF valid-pullback path;
- BOS and CHoCH lifecycle boundaries;
- POI ontology;
- OB/FVG relationships;
- four execution modules;
- reversal-trigger semantics;
- structural/zone stop concepts;
- target and 1:2 RR gating;
- execution/risk separation.

It is **not by itself a broker-specific live trading platform specification**. The SMC methodology, execution authorization, trading policy, countertrend scenarios, and generic platform execution boundary are now canonicalized; venue-specific implementation still requires broker/exchange contracts and infrastructure.

The main reason is not lack of source material. The knowledgebase contains most of the additional concepts needed for the strategy. The gap is that several source scenarios are still expressed as examples, qualitative guidance, or trader-plan rules and have not yet been reconciled into deterministic contracts.

A complete platform also requires non-SMC infrastructure specifications that are not methodology semantics: broker/exchange order handling, bid/ask and spread behavior, slippage, fills, margin/leverage, contract specifications, position sizing mechanics, session/news data, persistence, monitoring, backtesting, and operational failure handling.

## 2. Current canonical coverage

| Area | Current status | Assessment |
|---|---|---|
| Layer 1 candle semantics | Canonical | Covered |
| Layer 2 pullback / verified extreme | Canonical | Covered |
| IDM definition / lifecycle | Canonical | Covered |
| Structural qualification | Canonical | Covered, including explicit 2-candle path |
| BOS | Canonical | Covered |
| CHoCH | Canonical | Covered for standard lifecycle; LTF-specific exception is missing |
| POI ontology | Canonical | Covered |
| OB validation | Canonical | Partially executable; source contains further selection/refinement cases |
| FVG | Canonical property/validator | Covered |
| Four entry modules | Canonical | Module existence covered; exact order/price semantics are incomplete |
| Reversal triggers | Canonical | Covered at current deterministic/qualitative boundary |
| Stop loss | Canonical concept | Exact platform placement rules incomplete |
| Target | Canonical concept | Pro-trend path clearer than countertrend path |
| RR | Canonical 1:2 gate | Covered |
| Position sizing | Source-backed | Not represented in current risk skill |
| Session windows | Source-backed trading-plan rule | Not represented in current skill |
| News filter | Source-backed trading-plan rule | Not represented in current skill |
| Daily/concurrent risk controls | Source-backed trading-plan rule | Not represented in current skill |
| Trade logging | Source-backed | Not represented as platform contract |
| Backtesting/fill simulation | Source-backed need, but not methodology specification | Missing |
| Broker/exchange execution | Platform requirement | Missing |

## 3. Source-backed scenarios not yet deterministically represented

### 3.1 Status update — LTF-CHoCH after HTF POI / core-liquidity interaction

Source:
- `knowledgebase/Become-a-TRUE-Forex-Trader-Become-a-TRUE-Forex-Trader_text_format.txt`
- multi-timeframe section;
- the source explains that after HTF POI/core-liquidity interaction, execution can shift to LTF and the most recently formed LTF valid pullback/inducement becomes the key reference; a break beyond that LTF inducement can confirm the directional change earlier than the HTF external boundary.
- `knowledgebase/true_smc123.txt`, Top-Down / LTF sections provide concrete LTF mapping examples.

Current skill:
- `05_CHOCH_mechanics.md` does not contain this explicit LTF-specific confirmation route.
- `08_implementation.md` does not contain this route as a deterministic event/state rule.

Classification:
**CANONICALIZED — SOURCE-DIRECT + SOURCE-DERIVED FORMALIZATION**.

Required reconciliation:
- exact precondition for switching from HTF to LTF confirmation;
- exact identity of the LTF reference;
- whether the LTF break is wick/body/close;
- interaction with the existing Real/Fallback Major IDM lineage;
- whether this is a CHoCH variant or a lower-timeframe representation of the same CHoCH.

Do not silently infer this route from generic CHoCH rules.

### 3.2 Status update — Order Flow / SMT

The Order Flow / SMT gap is now canonicalized in `06_execution.md` and mapped in `08_implementation.md`.

Canonical result:
- OF candidate = last opposing move before dominant continuation/displacement;
- multi-leg correction is represented as the whole relevant corrective move while its protected endpoint remains intact;
- pre-inducement formations are contextual SMT / inducement traps and are execution-excluded;
- touch or penetration alone does not establish mitigation;
- Decisional OF is selected from the eligible OF lineage associated with the displacement causing canonical VALID_BOS;
- Extreme OF is the furthest unmitigated eligible OF at the origin, shifting to the next eligible OF after mitigation.

Classification: **CANONICALIZED — SOURCE-DIRECT + SOURCE-DERIVED FORMALIZATION**.

### 3.3 Status update — Engineering Liquidity canonicalized

Engineering Liquidity is now canonicalized in `06_execution.md` and mapped in `08_implementation.md`.

Canonical result:
- core-liquidity reference, not IDM or POI;
- derived from the most recent valid pullback immediately preceding the active Extreme POI;
- invalid pullback/arbitrary pivot cannot create ENG_LQD;
- recomputed when Extreme POI provenance changes;
- sweep does not itself create reversal, BOS, or CHoCH.

Classification: **CANONICALIZED — SOURCE-DIRECT + SOURCE-DERIVED FORMALIZATION**.
### 3.4 Status update — POI / Order Block selection canonicalized

The later source update is now canonicalized in `06_execution.md` and `08_implementation.md`.

Canonical result:
- Decisional OB = valid OB that actually causes canonical VALID_BOS;
- the earlier “first valid OB after inducement” shortcut is superseded;
- Extreme OB = furthest valid origin-side OB;
- OB validity is based on its own pillars;
- OF state does not automatically invalidate a valid OB;
- a valid Decisional OB may be used while associated OF remains unmitigated, subject to Rule-of-Two and execution gates.

Classification: **CANONICALIZED — SOURCE-DIRECT + SOURCE-DERIVED FORMALIZATION**.
### 3.5 Status update — Entry authorization canonicalized; broker order type remains platform policy

Entry authorization and methodology price reference are now canonicalized in `06_execution.md` and `08_implementation.md`.

Canonical result:
- all four entry modules have explicit prerequisite chains;
- direct candle confirmation uses the completed confirmation-candle close as the methodology reference price;
- sweep/mitigation alone is insufficient;
- broker order type remains a platform-order policy, not an inferred methodology fact;
- authorization, submission, fill, and open-position state remain distinct.

Classification: **CANONICALIZED — SOURCE-DIRECT + PLATFORM-BOUNDARY FORMALIZATION**.
### 3.6 Status update — Stop anchor canonicalized; numeric buffer remains configurable

Stop anchors are now canonicalized in `07_risk.md` and mapped in `08_implementation.md`.

Canonical result:
- IDM Sweep -> sweep extreme;
- Decisional POI -> confirmation/reversal pattern extreme;
- ENG LQD Sweep -> validated sweep/confirmation extreme;
- Extreme POI -> confirmation/reversal pattern extreme;
- exact numeric buffer remains explicit configuration because the source says “few pips” rather than one universal value;
- missing buffer blocks automatic broker submission.

Classification: **CANONICALIZED — SOURCE-DIRECT + CONFIGURATION BOUNDARY**.
### 3.7 Status update — Target hierarchy canonicalized; LTF/countertrend target policy remains explicit

Target resolution is now canonicalized in `07_risk.md` and mapped in `08_implementation.md`.

Canonical result:
- direct same-timeframe pro-trend -> current confirmed external extreme/external liquidity;
- LTF -> explicit HTF-external versus LTF-structural target policy;
- countertrend -> setup-specific next canonical destination;
- RR consumes a resolved target and does not create one;
- no canonical target blocks automatic TP submission.

Classification: **CANONICALIZED — SOURCE-DIRECT + SOURCE-DERIVED FORMALIZATION**.
### 3.7.1 Status update — Target hierarchy canonicalized

The target hierarchy is now canonicalized in `07_risk.md` and `08_implementation.md`.

Canonical result:
- direct same-timeframe pro-trend -> confirmed external extreme/external liquidity;
- LTF -> explicit HTF-external or LTF-structural target policy;
- countertrend -> setup-specific next canonical destination;
- absent target prevents automatic TP submission.

Classification: **CANONICALIZED — SOURCE-DIRECT + SOURCE-DERIVED FORMALIZATION**.

### 3.8 Status update — Position sizing and risk-budget controls canonicalized

The source-backed position-sizing and risk-budget rules are now canonicalized in `trading_policy.md`.

Canonical result:
- position size is calculated only after canonical entry and stop resolution;
- risk amount = account equity × configured risk percentage;
- position size uses exact stop distance and instrument pip/tick value;
- source example values (0.5% fixed risk, 0.5% running risk, one trade/session, two trades/day, 1.0% daily loss) are configurable policy values;
- policy state must persist and reconcile with account/broker history.

Classification: **CANONICALIZED AS CONFIGURABLE TRADING POLICY**.

### 3.9 Status update — Session and news policy canonicalized

Session and high-impact news rules are now canonicalized in `trading_policy.md`.

Canonical result:
- same-timeframe and optional HTF→LTF routes are explicit;
- source example London/New York windows are configurable UK-local-time policy values;
- DST-aware timezone evaluation is required;
- high-impact GBP/USD news avoidance is a configurable gate;
- live news gating requires an external economic-calendar dependency and fails closed when enabled and required data is unavailable.

Classification: **CANONICALIZED AS CONFIGURABLE TRADING POLICY + EXTERNAL DATA DEPENDENCY**.

### 3.10 Status update — Performance logging / trade journal

The trade-journal requirement is now represented in `trading_policy.md`, including structural context, authorization, stop, target, risk, session, news, and final execution outcome.

Classification: **CANONICALIZED AS PLATFORM AUDITABILITY POLICY**.

### 3.11 Status update — Backtesting / replay / historical observability

The methodology observability boundary is already canonicalized. The platform execution contract now defines the deterministic backtest/replay boundary: no lookahead, explicit spread/slippage/fill assumptions, LTF/tick evidence where needed, explicit session/news replay, and account/risk evolution from simulated fills.

Classification: **CANONICALIZED PLATFORM EXECUTION CONTRACT; VENUE-SPECIFIC FILL DATA/ASSUMPTIONS REMAIN CONFIGURATION**.

## 4. Current runtime versus canonical skill

The current `main` runtime does not implement the full skill.

### `smc_analyzer.py`

Current content provides:
- OHLC normalization;
- completed-candle filtering;
- intrabar evidence state;
- lifecycle/event/outcome enums;
- a StructuralPOICandidate data class.

It does not currently contain the full structural detector/classifier/state-transition engine described by `03`/`04`/`05`/`08`.

### `smc_htf_ltf_monitor.py`

Current behavior is a simple manually configured zone monitor:
- loads zones from `zones.json`;
- fetches the latest candle from Yahoo Finance;
- detects zone touch;
- arms an LTF check;
- accepts a directional candle close relative to the zone midpoint;
- sets SL to the zone boundary;
- calculates RR against a manually configured target;
- raises a Termux alert.

This is materially different from canonical execution.

Examples of current non-canonical shortcuts:
- no IDM detection;
- no BOS detection;
- no CHoCH classification;
- no structural retracement qualification;
- no 2-candle reduced retracement handling;
- no OF/OB/FVG validation;
- no Engineering Liquidity identification;
- no Rule-of-Two selection engine;
- no canonical candle-pattern evaluator;
- no source-backed position sizing;
- no session/news gate;
- no broker execution;
- no real position/open-order lifecycle.

### Repository-level inconsistency

The current repository does **not** contain `SMC_mapper.py`, while `08_implementation.md` still refers to `SMC_mapper.py` as the executable implementation owner.

This is a documentation/runtime synchronization issue and should be resolved before implementation work is treated as complete.

## 5. Full-platform sufficiency assessment

### Signal / structure engine

**The skill is close, but not yet complete.**

The structural backbone is sufficiently specified for implementation, but LTF-CHoCH, OF/SMT selection, Engineering Liquidity selection, and some competing-zone cases need deterministic reconciliation.

### Entry engine

**Not yet complete.**

The four module taxonomy exists, but exact order-type, price-coordinate, cancellation, expiry, and re-entry semantics are still incomplete.

### Stop engine

**Not yet complete.**

The semantic anchors exist, but exact deterministic stop coordinates/buffer rules are not fully specified.

### Target engine

**Partially complete.**

Pro-trend targeting is clearer; countertrend targeting needs explicit deterministic hierarchy if the platform must automatically place exits.

### Position sizing / risk engine

**Not yet complete.**

The knowledgebase contains a usable source-backed position-sizing model and a concrete example risk plan, but the canonical skill has not yet represented them as an explicit configurable policy.

### Live broker platform

**No.**

The current skill does not by itself specify the broker/exchange integration layer, execution guarantees, fills, slippage, margin, contract specifications, or account reconciliation required for a complete live trading platform.

### Backtester

**No.**

The methodology can drive a backtester after the execution/fill/risk contracts are completed, but the current skill does not fully specify the market microstructure simulation required for trustworthy results.

## 6. Additional knowledge required outside the current SMC skill

The knowledgebase already contains enough source material to resolve many strategy-specific gaps. Additional external/platform knowledge is still required for:

1. Broker/exchange API and order semantics.
2. Bid/ask, spread, tick value, pip value, contract size, volume step and minimum order size.
3. Margin and leverage rules.
4. Slippage and partial-fill behavior.
5. Economic-calendar/news data and time-zone/DST handling.
6. Market holidays/session calendars.
7. Historical data quality and lower-timeframe/tick availability.
8. Backtest execution/fill assumptions.
9. Persistent order/position reconciliation after disconnects.
10. Account/equity/drawdown state management.
11. Operational monitoring, retries, alert delivery, and fail-safe behavior.

These are platform-engineering requirements, not replacements for the True SMC source.

## 7. Recommended canonicalization order

1. Resolve the LTF-CHoCH source scenario.
2. Formalize Order Flow + SMT + decisional/extreme selection.
3. Formalize Engineering Liquidity selection.
4. Formalize the exact four entry-module order/price/cancellation semantics.
5. Formalize stop anchors and buffer policy.
6. Formalize target hierarchy.
7. Add an explicit configurable trading-plan/risk-policy layer for position sizing, session limits, news filters, and daily risk budgets.
8. Define broker/backtest execution contracts separately from methodology.

## 8. Audit disposition

No knowledgebase file was modified.

No runtime production file was modified.

The findings classified as **NEW_CANONICAL_CANDIDATE** or **SOURCE-BACKED BUT UNDER-SPECIFIED** should not be silently promoted to canonical methodology until their source evidence is reconciled into deterministic contracts.

The 2-candle retracement correction is already canonicalized elsewhere:
- `MIN_RETRACEMENT_CANDLE_COUNT = 2`;
- `NORMAL_RETRACEMENT_CANDLE_COUNT = 3`;
- exactly 2 candles use the reduced-candle exception;
- 38.2%–<50% remains a separate immediate-HTF valid-pullback path.

