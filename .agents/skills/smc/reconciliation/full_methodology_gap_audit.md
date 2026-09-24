# TRUE SMC — Full Methodology / Platform Gap Audit

Status: **AUDIT IN PROGRESS — FULL PLATFORM SPECIFICATION NOT COMPLETE**

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

It is **not yet sufficient as a deterministic specification for a complete live trading platform**.

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

### 3.1 LTF-CHoCH after HTF POI / core-liquidity interaction — HIGH PRIORITY

Source:
- `knowledgebase/Become-a-TRUE-Forex-Trader-Become-a-TRUE-Forex-Trader_text_format.txt`
- multi-timeframe section;
- the source explains that after HTF POI/core-liquidity interaction, execution can shift to LTF and the most recently formed LTF valid pullback/inducement becomes the key reference; a break beyond that LTF inducement can confirm the directional change earlier than the HTF external boundary.
- `knowledgebase/true_smc123.txt`, Top-Down / LTF sections provide concrete LTF mapping examples.

Current skill:
- `05_CHOCH_mechanics.md` does not contain this explicit LTF-specific confirmation route.
- `08_implementation.md` does not contain this route as a deterministic event/state rule.

Classification:
**NEW_CANONICAL_CANDIDATE / SOURCE-DIRECT**.

Required reconciliation:
- exact precondition for switching from HTF to LTF confirmation;
- exact identity of the LTF reference;
- whether the LTF break is wick/body/close;
- interaction with the existing Real/Fallback Major IDM lineage;
- whether this is a CHoCH variant or a lower-timeframe representation of the same CHoCH.

Do not silently infer this route from generic CHoCH rules.

### 3.2 Order Flow identification and SMT exclusion — HIGH PRIORITY

Sources:
- `knowledgebase/truesmc2026.txt`, Part 4 — OrderFlow Identification;
- Part 6 — POI Identification Secret;
- Part 8 — Entry Modules;
- `knowledgebase/use_of_orderblock_and_ordeflow.txt`;
- `knowledgebase/true_smc123.txt`, Parts 4–6 and 8–11.

Source scenarios include:
- order flows before inducement can be treated as SMT / inducement traps;
- the decisional order flow is tied to the swing that caused BOS;
- the extreme order flow is the furthest unmitigated relevant order flow;
- some intermediate order flows/blocks are weak or invalid;
- later source updates change how certain order blocks are treated even when an order flow remains unmitigated;
- valid Order Flow mitigation is associated with a valid pullback, not arbitrary wick interaction.

Current skill:
- `06_execution.md` contains an OF lifecycle but not the complete deterministic source-driven OF identification/selection algorithm.
- SMT appears only as a boundary idea, not as a complete canonical entity/selection rule.

Classification:
**NEW_CANONICAL_CANDIDATE / SOURCE-DIRECT + SOURCE-DERIVED FORMALIZATION NEEDED**.

Required reconciliation:
- deterministic OF start/end geometry;
- OF validity/mitigation predicate;
- SMT exclusion rule;
- decisional versus extreme OF selection priority;
- what happens when multiple valid OFs coexist;
- how source updates interact with earlier examples.

### 3.3 Engineering Liquidity definition and selection — HIGH PRIORITY

Sources:
- `knowledgebase/truesmc2026.txt`, Part 7;
- `knowledgebase/true_smc123.txt`, Part 7;
- `knowledgebase/true_smc_21dayBootCamp.txt`, Day 8.

Source definition:
Engineering Liquidity is liquidity above/below the high/low of the valid pullback immediately preceding the Extreme POI.

Source scenarios further state that:
- it is a core-liquidity layer similar to IDM;
- it depends on the presence/mitigation state of order flows and POIs;
- it may be the next liquidity target when inducement does not immediately produce reversal;
- the relevant pullback must actually be valid.

Current skill:
- `06_execution.md` has an Engineering Liquidity lifecycle and entry module.
- It does not fully own the source-backed identification/selection algorithm or its relationship to decisional/extreme OF/OB availability.

Classification:
**PARTIALLY CANONICAL / NEEDS DETERMINISTIC FORMALIZATION**.

### 3.4 POI selection priority and weak-zone/SMT handling — HIGH PRIORITY

Sources:
- `knowledgebase/truesmc2026.txt`, Part 6;
- `knowledgebase/use_of_orderblock.txt`;
- `knowledgebase/use_of_orderblock_and_ordeflow.txt`;
- `knowledgebase/true_smc123.txt`, Parts 5–6.

Source-backed scenarios include:
- maximum two active tradable POIs;
- Decisional + Extreme;
- pre-inducement formations may be traps/weak zones;
- decisional and extreme POIs are selected from relevant valid OF/OB lineage;
- some order blocks remain valid despite surrounding OF state after later methodology updates.

Current skill:
- Rule of Two and POI classes are covered.
- The precise selection algorithm across competing OF/OB candidates is not fully deterministic.

Classification:
**PARTIALLY CANONICAL / NEEDS SOURCE RECONCILIATION**.

### 3.5 Entry order-type and exact entry-price semantics — HIGH PRIORITY

Sources:
- `knowledgebase/true_smc123.txt`, Parts 8–11 and LTF sections;
- `knowledgebase/truesmc2026.txt`, Part 8;
- `knowledgebase/Become-a-TRUE-Forex-Trader-Become-a-TRUE-Forex-Trader_text_format.txt`, Entry Modules and Multi-Timeframe Entry sections.

Observed source behaviors include:
- direct same-timeframe entries after rejection/confirmation;
- limit-order examples;
- LTF execution to refine entries;
- entry from Decisional POI;
- entry after IDM sweep;
- entry after Engineering Liquidity sweep;
- entry from Extreme POI;
- different entry/confirmation timing depending on route.

Current skill:
- Four entry modules are named and context-gated.
- Candle-pattern close-only execution is defined.
- Exact order type and price coordinate are not deterministically specified for every module.

Missing deterministic contract:
- market versus limit versus stop order per module;
- exact price coordinate for each order type;
- whether entry is at POI edge, sweep price, pattern close, midpoint, or another source-defined coordinate;
- expiration of unfilled limit orders;
- re-entry after missed trigger;
- cancellation priority when another structural event appears.

Classification:
**IMPLEMENTATION-BLOCKING EXECUTION CONTRACT GAP**.

### 3.6 Stop-loss exact placement — HIGH PRIORITY

Sources:
- `knowledgebase/Become-a-TRUE-Forex-Trader-Become-a-TRUE-Forex-Trader_text_format.txt`;
- `knowledgebase/true_smc123.txt`;
- `knowledgebase/truesmc2026.txt`;
- `knowledgebase/advanced_market_structure_mapping.txt`.

Source examples use:
- a few pips beyond the sweep;
- beyond a pattern/sweeping candle high/low;
- beyond a structural/zone boundary;
- external structural invalidation.

Current skill:
- Tier 1 and Tier 2 stop concepts exist.
- A configurable buffer `P` exists conceptually.

Missing:
- exact canonical buffer semantics;
- whether buffer is fixed pips, ticks, spread-adjusted, ATR-like, or broker minimum-distance based;
- exact stop anchor for each of the four entry modules;
- exact stop anchor for each reversal pattern;
- what happens when a valid stop would make RR < 1:2.

Classification:
**SOURCE-BACKED BUT UNDER-SPECIFIED**.

A platform cannot calculate a deterministic executable SL from the current skill alone.

### 3.7 Target hierarchy — MEDIUM/HIGH PRIORITY

Sources repeatedly target:
- current external structural liquidity;
- external high/low;
- next liquidity layer;
- POI destination in countertrend scenarios;
- sometimes slightly beyond an external liquidity level.

Current skill:
- Pro-trend primary target is reasonably defined.
- Countertrend target policy explicitly avoids a universal hard coordinate.

Missing:
- deterministic TP selection hierarchy for each entry module;
- whether TP is exact external extreme, liquidity level, POI, or offset beyond;
- behavior when multiple candidate targets have equal provenance;
- partial TP / breakeven / trailing policy if intended for a platform.

Classification:
**PARTIAL CANONICAL COVERAGE**.

### 3.8 Position sizing and risk-budget controls — HIGH PRIORITY for live trading

Source:
`knowledgebase/Become-a-TRUE-Forex-Trader-Become-a-TRUE-Forex-Trader_text_format.txt` contains explicit position-sizing methodology:
- fixed risk approximately 0.5% per trade in the example trading plan;
- risk amount = account balance × risk percentage;
- position size = risk amount ÷ (stop-loss pips × pip value);
- stop distance determines position size, not vice versa.

The same source's example trading plan contains:
- maximum running risk: 0.5%;
- maximum one trade per session;
- maximum two trades per day;
- maximum daily loss: 1.0%;
- record/log every trade.

Current skill:
- 1:2 RR and risk boundaries exist;
- the actual position-sizing algorithm and account-level risk budget do not.

Classification:
**SOURCE-BACKED TRADING-PLAN CONTRACT, NOT CURRENT CORE SMC SEMANTIC OWNERSHIP**.

Important:
The source material provides a concrete example plan. It should not automatically be hard-coded as universal SMC methodology. It should become an explicit configurable trading-policy layer if the platform is intended to reproduce this exact plan.

### 3.9 Session and news filters — HIGH PRIORITY for reproducing the documented plan

Source:
`knowledgebase/everything_behind_the_trading_system.txt` and the book's Trading Plan specify:
- London window;
- New York window;
- one trade per session;
- two trades per day;
- high-impact GBP/USD news avoidance;
- entries confined to the chosen execution timeframe.

Current skill:
- no session policy;
- no economic-calendar/news gate;
- no session-aware order cancellation/expiry.

Classification:
**SOURCE-BACKED TRADING-PLAN CONTRACT**.

Additional external platform knowledge required:
- authoritative economic-calendar feed;
- timezone/DST handling;
- release timestamps and pre/post news blackout windows;
- symbol/currency exposure mapping.

### 3.10 Performance logging / trade journal — MEDIUM PRIORITY

The source trading plan explicitly requires every trade to be recorded/logged and describes fields such as:
- date;
- asset;
- direction;
- setup;
- session/key window;
- rule adherence.

Current skill:
- no canonical trade-journal schema.

Classification:
**SOURCE-BACKED PLATFORM REQUIREMENT**.

### 3.11 Backtesting / replay / historical observability — HIGH PRIORITY

The source repeatedly relies on replay/front-test examples and lower-timeframe structural reconstruction.

Current implementation correctly distinguishes:
- `OBSERVED`;
- `METHODOLOGY_ASSUMED`;
- `UNAVAILABLE`.

But a complete backtester still needs:
- deterministic bar-close model;
- lower-timeframe/tick reconstruction when needed;
- spread/bid/ask model;
- slippage;
- order-fill rules;
- intrabar ordering policy;
- no-lookahead constraints;
- session/news data replay;
- cancellation/expiry model;
- position sizing over time;
- account equity/margin simulation.

These are not presently specified.

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

