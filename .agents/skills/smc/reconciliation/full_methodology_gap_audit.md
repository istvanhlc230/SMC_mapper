# TRUE SMC — Full Methodology / Platform Gap Audit

Status: **CANONICALIZATION PHASE COMPLETE — C1–C15 RECONCILED AT THE CURRENT SEMANTIC BOUNDARY; CONTROLLED IMPLEMENTATION/POLICY GAPS REMAIN**

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
- structural swing confirmation after IDM takeout;
- 50% standard retracement as a later BOS qualification gate;
- explicit 2-candle reduced-candle path;
- conditional 38.2%–<50% immediate-HTF valid-pullback path;
- BOS and CHoCH lifecycle boundaries;
- POI ontology;
- OB/FVG relationships;
- four execution modules;
- reversal-trigger semantics;
- structural/zone stop concepts;
- target configuration and RR policy gating;
- execution/risk separation.

It is **not by itself a broker-specific live trading platform specification**. The SMC methodology, execution authorization, trading policy, countertrend scenarios, and generic platform execution boundary are now canonicalized; venue-specific implementation still requires broker/exchange contracts and infrastructure.

The remaining uncertainty is deliberately bounded. The canonical skill now covers the current structural/execution semantics and the configurable Target Plan architecture. What remains is either (a) implementation/policy behavior that the sources do not universally fix, such as target choice among simultaneous candidates, or (b) venue-specific infrastructure contracts. These must remain outside canonical methodology unless source evidence later supplies a deterministic rule.

A complete platform also requires non-SMC infrastructure specifications that are not methodology semantics: broker/exchange order handling, bid/ask and spread behavior, slippage, fills, margin/leverage, contract specifications, position sizing mechanics, session/news data, persistence, monitoring, backtesting, and operational failure handling.

## 2. Current canonical coverage

| Area | Current status | Assessment |
|---|---|---|
| Layer 1 candle semantics | Canonical | Covered |
| Layer 2 pullback / verified extreme | Canonical | Covered |
| IDM definition / lifecycle | Canonical | Covered |
| Structural qualification | Canonical | Covered; `IDM_TAKEN` establishes the candidate/provisional stage, and structural retracement qualification promotes it to `CONFIRMED_STRUCTURAL_SWING` before the later BOS gate |
| BOS | Canonical | Covered |
| CHoCH | Canonical | Covered, including the source-backed LTF context route |
| POI ontology | Canonical | Covered; RB remains a separately typed PD-array |
| OB validation | Canonical | Covered at current semantic boundary; venue/execution details remain platform policy |
| FVG | Canonical property/validator | Covered |
| Four entry modules | Canonical | Covered at authorization/reference-price boundary; order lifecycle remains platform policy |
| Reversal triggers | Canonical | Covered at current deterministic/qualitative boundary |
| Stop loss | Canonical concept | Semantic anchors covered; numeric buffer remains configurable |
| Target | Canonical concept | Covered as candidate discovery + configurable Target Plan; universal priority/countertrend coordinate intentionally remains a policy choice for automatic TP |
| RR | Configurable trading policy | Covered |
| Position sizing | Configurable trading policy | Canonicalized |
| Session windows | Configurable trading policy | Canonicalized |
| News filter | Configurable trading policy | Canonicalized with external-data dependency |
| Daily/concurrent risk controls | Configurable trading policy | Canonicalized |
| Trade logging | Platform auditability policy | Canonicalized |
| Backtesting/fill simulation | Platform requirement | Contract defined; venue-specific fill assumptions remain configuration |
| Broker/exchange execution | Platform requirement | Boundary defined; venue-specific contract remains external |

## 3. Source-backed scenarios not yet deterministically represented

### 3.1 Status update — LTF-CHoCH after HTF POI / core-liquidity interaction

Source:
- `knowledgebase/Become-a-TRUE-Forex-Trader-Become-a-TRUE-Forex-Trader_text_format.txt`
- multi-timeframe section;
- the source explains that after HTF POI/core-liquidity interaction, execution can shift to LTF and the most recently formed LTF valid pullback/inducement becomes the key reference; a break beyond that LTF inducement can confirm the directional change earlier than the HTF external boundary.
- `knowledgebase/true_smc123.txt`, Top-Down / LTF sections provide concrete LTF mapping examples.

Current skill:
- `05_CHOCH_mechanics.md` contains the explicit LTF-specific confirmation route.
- `08_implementation.md` contains the deterministic execution representation.

Classification:
**CLOSED / VERIFIED — POST-HTF-INTERACTION LTF-CHOCH CONTEXT + VALID-PULLBACK REFERENCE SUBSTITUTION + IDM-DEPENDENT CHoCH GATE**.

Resolved canonicalization:
- HTF POI/core-liquidity interaction activates the LTF-CHoCH context;
- the 2026 source informally describes this as a “small glitch in the structure cycle”; the canonical context name is LTF-CHoCH Context After HTF Interaction, and the valid pullback/inducement replacing the ordinary LTF external boundary is the Valid-Pullback Reference Substitution mechanism;
- arbitrary local pivots and invalid pullbacks cannot replace that reference;
- the LTF break mode depends on both active-range IDM context and the exact tested-level provenance: a wick through the active Major IDM level is `MAJOR_IDM_SWEEP`, not CHoCH; a wick may enter `CHoCH_ELIGIBLE` only when the tested LTF structural reference is eligible and demonstrably distinct from an active Major IDM level; when only Minor IDM is available, the prior protected external boundary remains the active Major IDM reference, a wick through that boundary is `MAJOR_IDM_SWEEP`, a wick through the substituted LTF Minor IDM is an LTF inducement sweep / `IDM_TAKEN` rather than CHoCH, and a completed body close beyond the active LTF CHoCH reference is required for `CHoCH_ELIGIBLE`;
- the body-close condition is therefore not universal across all LTF CHoCH events;
- the route remains the same CHoCH concept represented in an HTF→LTF execution context, not a new lifecycle state;
- the LTF reference is not reclassified as Major IDM merely because it is used by the LTF-CHoCH route.

Source reconciliation basis:
- `knowledgebase/sources/truesmc2026.txt`, Part 5 lower-timeframe example, approximately 00:08:47–00:10:36 and 00:13:13–00:13:31, for Valid-Pullback Reference Substitution;
- `knowledgebase/sources/truesmc2026.txt` CHoCH example around 00:12:18–00:12:33, for the Major-Inducement wick/body distinction.

Do not silently infer the LTF-CHoCH Context Route from generic CHoCH rules, and do not generalize the Minor-Inducement body-close condition to every LTF CHoCH.

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
- Extreme OF lineage is resolved first; Extreme OB = furthest unmitigated valid OB within the active Extreme OF lineage; global origin-side OB search is not canonical;
- OB FVG association is a validation/selection property: if a candidate candle lacks the required FVG association, selection shifts to the next eligible source-defined candle and the FVG association is re-evaluated; the selected candle must independently satisfy all OB pillars;
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
### 3.7 Status update — Target source and downstream target-use boundary

Chart analysis identifies structural/liquidity destination levels that may be used as target inputs. Selection and use of those levels are downstream implementation/trading-policy concerns, not canonical SMC methodology.

Canonical result:
- direct same-timeframe pro-trend -> current confirmed external extreme/external liquidity is a valid target candidate;
- LTF execution supports source-backed HTF external and LTF structural/BOS target candidates, but the source does not define one universal priority between them;
- countertrend target candidates are setup-specific; a universal single-coordinate resolver remains source-under-specified and is not invented;
- the analyzer must preserve target provenance and may emit multiple valid candidates rather than manufacturing one universal winner;
- a configurable Target Plan may assign different valid targets to multiple trade legs; leg count and allocation are configuration, not methodology constants;
- fixed-R, where permitted by policy, remains a non-structural policy target;
- RR consumes an already resolved target and never creates one;
- the current monitor phase is notification-only: `TARGET_REACHED` produces an alert/notification and does not imply position closure, partial closure, stop movement, or broker fill;
- `BREAK_EVEN` is a future stop-management action, not a fallback target.

Classification: **IMPLEMENTATION SCOPE — no universal target-priority or universal countertrend coordinate is required by the canonical methodology.**


### 3.8 Status update — Position sizing and risk-budget controls canonicalized

The source-backed position-sizing and risk-budget rules are now canonicalized in `trading_policy.md`.

Canonical result:
- position size is calculated only after canonical entry and stop resolution;
- risk amount = account balance × configured risk percentage;
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

### 3.11 Status update — 2026 market-structure ordering reconciliation

The 2026 market-structure source was reconciled into the canonical Layer 3 lifecycle with the following explicit ordering:

- The indexed source corpus may describe the IDM takeout as acquiring/confirming a swing point in source terminology.
- In the project-canonical state machine, `IDM_TAKEN` establishes `SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME`; it does **not** directly establish `CONFIRMED_STRUCTURAL_SWING`.
- The applicable structural retracement qualification is the promotion gate and is evaluated **after candidate establishment but before `CONFIRMED_STRUCTURAL_SWING`**.
- An insufficient retracement leaves the historical IDM-takeout evidence intact but prevents promotion of that candidate to `CONFIRMED_STRUCTURAL_SWING`; the active pullback/IDM reference then advances according to the owning Layer-2/Layer-3 forward-only lifecycle.
- The sequence `IDM_TAKEN → provisional swing state → retracement qualification → CONFIRMED_STRUCTURAL_SWING` is therefore **the current project-canonical ordering**.

Classification: **RECONCILED — SOURCE-DIRECT LANGUAGE PRESERVED; PROJECT-CANONICAL PROMOTION LIFECYCLE FORMALIZED**.

## 3.12 Status update — Backtesting / replay / historical observability

The methodology observability boundary is already canonicalized. The platform execution contract now defines the deterministic backtest/replay boundary: no lookahead, explicit spread/slippage/fill assumptions, LTF/tick evidence where needed, explicit session/news replay, and account/risk evolution from simulated fills.

Classification: **CANONICALIZED PLATFORM EXECUTION CONTRACT; VENUE-SPECIFIC FILL DATA/ASSUMPTIONS REMAIN CONFIGURATION**.

## 3.13 Latest direct source-reconciliation pass

The latest full knowledgebase re-audit identified and corrected the following canonical documentation conflicts:

1. **Rejection Block ontology:** RB is now represented as a separately typed PD-array/execution-location concept. The source's ordinary use of “POI” for a Rejection Block is preserved as broad execution-location language, while the canonical typed model does not make RB an OF/OB-equivalent POI class or an automatic Rule-of-Two slot.
2. **Engineering Liquidity:** ENG_LQD is now explicitly derived from the valid pullback immediately preceding the active Extreme OF or Extreme OB. The earlier project-composed extension to a Rejection Block Extreme role has been removed.
3. **Wick-path CHoCH:** Major IDM is not a positive prerequisite. The source-backed rule is an external wick break that is CHoCH-eligible unless the tested external level has Major IDM provenance; a Major IDM wick takeout is excluded from CHoCH.
4. **POI failure:** the execution failure transition now consumes CHoCH/control-shift confirmation rather than treating a generic BOS-or-CHoCH classification as sufficient.
5. **Position sizing basis:** the risk formula now uses Account Balance, matching the explicit source position-sizing example. The risk percentage and risk-budget values remain configurable trading-policy values rather than universal SMC constants.
6. **Reversal predicates:** exact OHLC inequalities are now explicitly documented as deterministic formalizations of source-described reversal patterns; qualitative morphology remains a non-binary filter and no unsupported numeric threshold is introduced.

Post-fix validation:
- no remaining obsolete provisional-swing terminology in the canonical methodology documents;
- no remaining canonical Major-IDM + OPPOSING WICK BREAK positive gate;
- no remaining Rejection Block → Engineering Liquidity dependency;
- no remaining Rejection Block-as-OF/OB-equivalent POI statement in the implementation mapping;
- POI failure is CHoCH/control-shift based;
- position sizing uses Account Balance.

The remaining items are **source-under-specified implementation choices**, not identified source contradictions: exact LTF target-selection hierarchy, universal countertrend target coordinate, and platform-specific execution contracts. The deterministic candle-pattern predicates are retained only as explicitly source-derived formalizations, with qualitative morphology kept non-binary.
## 3.14 Remaining-gap audit — current disposition

The remaining items were re-audited against the current canonical skill and implementation boundary.

| Item | Current disposition | Meaning |
|---|---|---|
| POI Failure provenance | **CLOSED / CANONICALIZED** | `POI_FAILURE` now consumes canonical CHoCH/control-shift state and is not reduced to a raw zone breach. |
| Rejection Block → Engineering Liquidity | **CLOSED / CANONICALIZED** | Engineering Liquidity is derived only from the valid pullback immediately preceding active Extreme OF/Extreme OB; RB is separate. |
| Reversal predicates | **CLOSED at current boundary** | Deterministic OHLC predicates are explicitly project-derived formalizations; qualitative morphology remains non-binary and no unsupported numeric threshold is invented. |
| Premium/discount gate | **SEMANTICALLY CANONICALIZED** | Directional Decisional-POI location is explicit. Any remaining provenance uncertainty concerns source traceability, not a missing implementation rule. |
| Target selection/use | **IMPLEMENTATION SCOPE** | Chart analysis supplies structural/liquidity destination inputs; implementation decides which are used as targets. |
| LTF target selection priority | **IMPLEMENTATION / TRADING POLICY** | Multiple source-supported target conventions exist; no canonical priority is required. |
| Universal countertrend target coordinate | **IMPLEMENTATION / TRADING POLICY** | No universal numeric TP is required by canonical methodology. |
| Fixed-R target | **IMPLEMENTATION / TRADING POLICY** | Non-structural policy mechanism, outside canonical target provenance. |
| BE / profit lock / trailing | **TRADE-MANAGEMENT IMPLEMENTATION** | Post-target management actions, outside canonical target semantics. |
| Broker order-type / pending-order lifecycle details | **PLATFORM IMPLEMENTATION GAP** | The platform contract defines the boundary; venue-specific order semantics, cancellation/expiry/re-entry policy, and broker integration still require implementation/configuration. |
| `smc_analyzer.py` runtime | **IMPLEMENTATION GAP** | The file contains foundational models but not the full canonical structural detector/classifier/state-transition engine. This is a runtime implementation task, not a methodology gap. |

The audit therefore finds **no unresolved canonical-methodology contradiction requiring new SMC rules at this time**. Target selection/use and trade-management behavior are implementation concerns built on chart-analysis outputs, not missing canonical SMC rules.

## 4. Current repository/runtime synchronization status

This section was rechecked against the current `main` tree on 2026-10-09. The earlier runtime inventory below has been superseded because those historical filenames are not present in the current tree.

### Verified repository facts

- `smc_analyzer.py` is not present in the current tracked `main` tree.
- `smc_htf_ltf_monitor.py` is not present in the current tracked `main` tree.
- `tests/test_smc_htf_ltf_monitor.py` is not present in the current tracked `main` tree.
- The canonical SMC semantic-owner documents remain present under `.agents/skills/smc/`.
- The tracked `CALENDAR/` and `MARKET_DATA/` packages are data-service components; their presence does not establish that the structural mapper runtime is implemented.

### Current disposition

**RUNTIME-TO-SKILL SYNCHRONIZATION = NOT VERIFIED.** The prior claim that `smc_analyzer.py` is the current runtime owner is stale and must not be used as a current repository fact. A current structural runtime entry point and its tests must be identified from files actually present in `main` before runtime equivalence can be audited.

The methodology specification remains separately auditable: absence of a runtime file does not invalidate or alter canonical SMC semantics. Conversely, the canonical skill's completeness does not establish that those rules are implemented in executable code.

## 5. Full-platform sufficiency assessment

### Signal / structure engine

**Canonical specification: sufficient at the current methodology boundary. Runtime: incomplete.**

The structural backbone, BOS/CHoCH lifecycle, POI/OF/OB/RB boundaries, and retracement gates are sufficiently specified for implementation. The analyzer runtime is not yet equivalent to that specification.

### Entry engine

**Canonical authorization: covered. Platform execution: implementation remains.**

The four entry modules, prerequisites, and methodology reference-price rules are canonicalized. Broker order type, pending-order cancellation/expiry/re-entry behavior, and venue integration remain platform-policy/implementation concerns.

### Stop engine

**Canonical anchors: covered. Numeric buffer/platform constraints: configurable implementation.**

The four module-specific anchors are canonicalized. No universal numeric buffer is invented; platform-specific tick/pip/contract constraints remain required for live execution.

### Target engine

**Canonical architecture: covered with intentionally controlled policy choices.**

Target candidate discovery and the configurable multi-leg Target Plan are canonicalized as project architecture. No universal priority among simultaneous LTF candidates and no universal countertrend coordinate is specified because the sources do not establish one.

### Position sizing / risk engine

**Canonical trading policy: covered. Runtime/platform integration: implementation remains.**

Risk percentage, account-balance basis, sizing inputs, trade/session/daily limits, news/session gates, and fail-closed policy boundaries are represented as configurable policy. Actual account/instrument/broker integration remains implementation work.

### Live broker platform

**Generic contract: defined. Venue integration: not implemented.**

The platform contract defines order states, quotes, order types, fills, slippage, position reconciliation, and backtest boundaries. A real venue still requires broker/exchange-specific API, contract, and operational implementation.

### Backtester

**Generic contract: defined. Execution simulator: not implemented.**

The no-lookahead, completed-candle, intrabar-evidence, spread/slippage, fill, and risk-evolution boundaries are specified. A trustworthy backtester still requires the executable simulation layer and explicit venue/data assumptions.

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

1. Preserve the current Layer 1–3, BOS/CHoCH, POI/OF/OB/RB, Engineering Liquidity, entry, stop, target-plan, and trading-policy ownership boundaries.
2. Resolve only source-backed deterministic gaps when evidence becomes sufficient; do not invent a universal target priority or universal countertrend target coordinate.
3. Keep venue-specific broker/exchange, fill, quote, spread, slippage, margin, and backtest assumptions outside True SMC semantic ownership.
4. Keep runtime synchronization separate from methodology canonicalization.

## 8. Audit disposition

No knowledgebase file was modified.

No runtime production file was modified. The reconciliation changed only canonical skill documentation and its audit ledger.

The findings classified as **NEW_CANONICAL_CANDIDATE** or **SOURCE-BACKED BUT UNDER-SPECIFIED** must not be silently promoted to canonical methodology. The currently known target-choice items are intentionally retained as controlled policy/implementation choices because no universal deterministic source rule has been established.

The normal retracement parameterization is canonicalized elsewhere:
- `MIN_RETRACEMENT_CANDLE_COUNT = 2` for the normal path;
- `NORMAL_RETRACEMENT_CANDLE_COUNT = 3`;
- the one-candle displacement outlier is an explicit exception when it takes `>=5` preceding bodies/extremes and passes all other qualification gates;
- two-candle reduced retracements remain source-supported through the displacement/extreme-taking exception;
- 38.2%–<50% remains a separate immediate-HTF valid-pullback path.



## Addendum A — Direct validator re-audit of the eight remaining canonical issues

The previous AUDIT PART 2 = COMPLETE disposition was superseded by a direct validator re-audit against the indexed knowledgebase evidence.

Current canonical disposition:

1. **Layer-2 / Layer-3 IDM ordering — CLOSED / CANONICALIZED.** Candle-Level Valid Pullback → Verified Pullback Extreme → Pullback-Derived Liquidity Reference → Layer-3 IDM classification → `IDM_TAKEN` → `SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME` → applicable structural retracement qualification → `CONFIRMED_STRUCTURAL_SWING`. The qualification gate is required for promotion to the confirmed swing and therefore precedes the confirmed state.
2. **Premium/Discount hard gate — CLOSED / CANONICALIZED.** Decisional BUY requires Discount and SELL requires Premium. The gate is execution eligibility, not scoring; canonical Dealing Range provenance remains required and no lowest-low/highest-high or OTE/Fibonacci fallback is authorized.
3. **OB/FVG validation — CLOSED / CANONICALIZED.** The required associated FVG/imbalance must exist and must not have been completely filled/consumed; complete non-mitigation is not required.
4. **OB → next FVG candle shift — CLOSED / CANONICALIZED.** A candidate candle lacking the required FVG association is rejected and selection shifts to the next eligible source-defined candle; the new candle is independently re-evaluated against all OB pillars.
5. **Extreme OB lineage — CLOSED / CANONICALIZED.** Extreme OF is resolved first; Extreme OB is the furthest unmitigated valid OB inside that active Extreme OF lineage. Origin OB remains a separate latent reserve.
6. **1-candle displacement outlier — CLOSED / VERIFIED.** The normal positive reduced-retracement path requires >=2 opposing candles, but the source-defined one-candle displacement outlier is an explicit exception when it takes >=5 preceding bodies/extremes and satisfies all other canonical qualification gates. A one-candle Layer-2 Candle-Level Valid Pullback remains valid independently.
7. **Rule-of-Two minimum-one — CLOSED / CANONICALIZED.** In an applicable Rule-of-Two execution context, active canonical tradable POIs have cardinality 1..2. No valid POI results in fail-closed NO_EVIDENCE; no synthetic POI is created. Origin OB is latent and Rejection Block is separately typed.
8. **IMPULSE_EXTENSION — CLOSED / VERIFIED.** IMPULSE_EXTENSION remains a classification outcome of EXT_CONT_BREAK when continuation-BOS qualification is insufficient; it is not an event class.

The project-canonical lifecycle is:

Candle-Level Valid Pullback
→ Verified Pullback Extreme
→ Pullback-Derived Liquidity Reference
→ IDM
→ IDM_TAKEN
→ SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME
→ applicable Structural Retracement Qualification
→ CONFIRMED_STRUCTURAL_SWING
→ Structural Swing Break
→ VALID_BOS

For first-BOS bootstrap, the transient `BOOTSTRAP_RANGE` is inserted between candidate establishment and structural retracement qualification.

### Knowledgebase evidence used

- knowledgebase/00_INDEX.md
- knowledgebase/03_SOURCE_EVIDENCE.md
- knowledgebase/reference/03_pullback_retracement.md
- knowledgebase/reference/06_poi_ob_fvg_rejection.md

The knowledgebase remains evidence only; .agents/skills/smc/ remains canonical authority.

### Remaining genuine source gaps

No remaining contradiction from the eight-item validator set is left open. Any exact source-sequence boundary not explicitly deterministic in the underlying source remains an implementation/documentation boundary rather than an invented numeric rule.


## Addendum B — Major IDM continuity after BOS — corrected

A direct source re-audit identified a semantic error in the previous canonical representation of post-BOS Major IDM lifecycle. The skill previously modeled the prior protected external boundary as a `FALLBACK_MAJOR_IDM` proxy and treated a later post-BOS pullback as a separate `REAL_MAJOR_IDM` object.

The source-backed rule is simpler: Major IDM remains one semantic class. If post-BOS price action creates only Minor IDM and no new Major IDM, the prior Protected Low in a bullish range or Protected High in a bearish range remains the Major IDM reference. When a new valid post-BOS pullback independently qualifies as Major IDM, it supersedes that prior reference from that point forward.

Evidence was rechecked in:
- `knowledgebase/sources/truesmc2026.txt`
- `knowledgebase/sources/market_structure_mapping_update.txt`
- `knowledgebase/sources/major_minor_inducement.txt`
- `knowledgebase/sources/true_smc123.txt`

The previous `FALLBACK_MAJOR_IDM` / `REAL_MAJOR_IDM` distinction was therefore removed from the canonical semantic and implementation contracts. The distinction was a project-composed lifecycle representation that had crossed the boundary into an unnecessary ontology distinction.

Validation requirement: no remaining canonical rule may treat `FALLBACK_MAJOR_IDM` as an event class, score category, CHoCH exception, or independent IDM type.


## Addendum C — Post-BOS Major IDM re-audit — 2026-09-27

The previously recorded "open source-definition gap" for post-BOS Major IDM qualification was re-audited against the complete categorized knowledgebase and the current canonical layers.

### Finding

The gap was **false / caused by incomplete source retrieval in the prior audit**.

The knowledgebase explicitly provides the missing qualification semantics:
- market_structure_mapping_update.txt: after BOS, the recent **valid pullback** becomes the Major Inducement; the source explicitly ties the Major-Inducement designation to the fact that it occurs after the break of structure.
- advanced_market_structure_mapping.txt: after a structural break, a new valid pullback becomes the new inducement; the source also distinguishes the post-break major role from other timeframe contexts.
- true_smc123.txt: the inducement is the liquidity resting below/above the **recently formed valid pullback**; the source repeatedly shows that when the current continuation does not satisfy the three-opposing-candle BOS requirement, the Major Inducement shifts to the newly formed valid pullback.
- true_smc_21dayBootCamp.txt: the normal retracement requires at least three retracing candles, while the explicitly demonstrated reduced-candle displacement case can qualify when the move is exceptionally large and takes at least five prior candle extremes.
- knowledgebase/03_SOURCE_EVIDENCE.md: major/minor IDM timing is explicitly tied to whether the valid pullback occurs before or after BOS.

### Canonical interpretation

The deterministic post-BOS Major IDM qualification is not a second hidden threshold or heuristic.

VALID_BOS
→ post-BOS lifecycle
→ **Layer-2 Candle-Level Valid Pullback**
→ **Verified Pullback Extreme**
→ Major IDM becomes active from that verified pullback extreme.

A mere SVP, newest-candidate pointer, or caller-selected pullback is not sufficient. Layer 3 consumes the already-defined Layer-2 states; it does not invent an additional Major-IDM candle-count or retracement-depth rule.

When no new post-BOS valid pullback / verified pullback extreme has established the next Major IDM, the prior protected external boundary remains the active Major IDM reference.

### Corrections applied

- Layer 3 now defines the qualification chain explicitly at the semantic owner.
- Layer 4, Layer 5, and Layer 8 now reference that owner-defined chain instead of implying an undefined hidden predicate.
- No new methodology threshold or heuristic was invented.
- The earlier "open gap" status is closed.

### Status

**POST-BOS MAJOR IDM SOURCE GAP = CLOSED.**

The prior audit statement claiming that the authoritative source material did not define the qualification predicate is superseded by this re-audit.

## Addendum D — Current clarification — LTF CHoCH reference and Major IDM provenance

The apparent conflict between `05_CHOCH_mechanics.md` §§3.5.3A and 3.5.4 is resolved by explicitly separating the active LTF range's IDM context from the provenance of the specific price level being tested. The distinction must use existing canonical terminology; it does not introduce `REAL_MAJOR_IDM` or `FALLBACK_MAJOR_IDM` object classes.

Canonical implementation rules:
- Major IDM provenance may be pullback-derived or governing-external-boundary-derived, under `03_structural_semantic_authority.md`.
- A wick through the exact level carrying active Major IDM provenance is `MAJOR_IDM_SWEEP`, not `CHoCH_ELIGIBLE` or `CHoCH_CONFIRMED`.
- A wick may enter `CHoCH_ELIGIBLE` only when the tested opposing/LTF structural reference is eligible and its level is demonstrably distinct from the active Major IDM reference; all remaining CHoCH prerequisites still apply.
- When only Minor IDM is available and no newer pullback-derived Major IDM has qualified, the prior protected external boundary remains the active Major IDM reference. A wick through that boundary is `MAJOR_IDM_SWEEP`. A wick through the substituted LTF Minor IDM is an LTF inducement sweep / `IDM_TAKEN`, not CHoCH and not automatically a Major IDM sweep; completed body close beyond the active LTF CHoCH reference is required to enter `CHoCH_ELIGIBLE`.
- If tested-level provenance is unavailable or ambiguous, block CHoCH structural classification and do not infer either CHoCH or `MAJOR_IDM_SWEEP` from geometry alone.
- `CHoCH_ELIGIBLE` remains distinct from `CHoCH_CONFIRMED`; eligibility never bypasses the complete CHoCH prerequisite gate.

This clarification refines the provenance boundary in the prior LTF-CHoCH reconciliation; it does not change the ordinary external-boundary rule or create a new lifecycle state.


## Current skill defragmentation and layer-by-layer verification — 2026-10-09

### Defragmentation changes

- `skill.md` is reduced to an index and semantic-owner map; methodology rules are not duplicated in the index.
- Layer 2 heading numbering is sequential through its validation and precedence sections.
- Layer 3 remains the sole semantic owner of Major IDM identity, provenance, lifecycle, `IDM_TAKEN`, and structural-candidate promotion.
- Layer 4 BOS mechanics now consumes the Layer-3 Major IDM lifecycle instead of repeating that lifecycle. Its section numbering is sequential (`3.4.1`–`3.4.14`).
- Layer 5 CHoCH mechanics now consumes Layer-3 IDM provenance and defines only the CHoCH-facing tested-level classification. The incorrect reference to the normal HTF external boundary was corrected to the normal LTF external boundary.
- Layer 6 no longer repeats the Extreme POI Mitigation module or the detailed target/RR policy. It supplies canonical execution inputs and delegates stop/target/RR ownership to the appropriate downstream documents.
- Layer 7's missing opening Markdown fence and non-sequential final heading number were corrected.
- Layer 8's §46 material is now a compact interface/guard. The detailed CHoCH decision matrix is concentrated in §49.3; §49.6 is a short invariant guard rather than a second decision tree.
- The stale runtime inventory was replaced by a verified current-tree status: the previously named structural runtime files are absent from current `main`; runtime-to-skill equivalence is therefore not claimed.
- Repeated `3.14` audit addenda were renamed as distinct addenda.

### Layer-by-layer acceptance matrix

| Boundary | Result | Verified contract |
|---|---|---|
| Layer 1 → Layer 2 | PASS | Layer 1 provides OHLC observations and evidence boundaries; Layer 2 creates sequential pullback semantics. |
| Layer 2 → Layer 3 | PASS | Valid pullback → verified extreme → pullback-derived liquidity reference → Minor IDM; Layer 3 consumes rather than redefines that chain. |
| Layer 3 → Layer 4 | PASS | Layer 3 owns swing promotion, retracement qualification, and Major IDM; Layer 4 consumes stored qualification for BOS. |
| Layer 3 / 5 CHoCH interaction | PASS | CHoCH uses the exact tested level's provenance; Major IDM wick = `MAJOR_IDM_SWEEP`; ambiguous provenance fails closed; eligibility does not equal confirmation. |
| Layer 5 → Layer 6 | PASS | POI failure consumes confirmed CHoCH/control shift and does not manufacture a structural event. |
| Layer 6 → Layer 7 | PASS | Entry authorization and structural/liquidity candidates flow downstream; stop, target-policy, RR, and position lifecycle ownership is downstream. |
| Layer 7 → Platform | PASS | Trading/account policy and venue order/fill/position lifecycle remain separate. |
| Canonical skill → implementation representation | PASS at documentation boundary | Layer 8 provides one detailed CHoCH decision matrix and cross-references semantic owners. Runtime implementation equivalence remains unverified because no current structural runtime entry point was identified. |

### Automated documentation checks

The 19 current SMC skill/reconciliation documents were fetched again after the edits. Checks performed:

- No outdated glitch-based CHoCH label remains as a normative term in the inspected skill/reconciliation documents.
- No duplicate Markdown heading text was found in the inspected documents.
- Fenced code blocks are balanced in every inspected document.
- Layer 2 and Layer 4 section-numbering gaps identified by this audit are fixed.
- The Major IDM wick/CHoCH decision matrix in Layer 8 matches the Layer 5 tested-level provenance contract.
- `REAL_MAJOR_IDM` / `FALLBACK_MAJOR_IDM` do not appear as live ontology classes in the Layer-4/Layer-5 rule-owner contracts.

### Disposition

**DOCUMENTATION DEFRAGMENTATION = PASS for the inspected SMC skill layer and ownership contracts.**

**EXECUTABLE RUNTIME CONFORMANCE = NOT VERIFIED.** No Python runtime implementation or test suite was changed in this pass. Do not infer that runtime behavior matches the canonical skill until the current structural runtime entry point is identified and tested against these contracts.

This audit is a documentation synchronization record. It does not add or change True SMC methodology rules.
