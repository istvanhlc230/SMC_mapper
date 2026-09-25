# TRUE SMC — SOURCE RECONCILIATION WORKFLOW

**Role:** Controlled governance workflow for evolving the existing canonical SMC skill from the authoritative source material in `main/knowledgebase/`.

**Authority boundary:** This document defines the change-control process. It does not define SMC methodology and must never become a second methodology source.

## 1. Authority model

```
main/knowledgebase/
        ↓
SOURCE ANALYSIS
        ↓
CANONICAL COMPARISON
        ↓
CONTRACT RECONCILIATION
        ↓
HUMAN APPROVAL
        ↓
IMPLEMENTATION
        ↓
INDEPENDENT VALIDATION
        ↓
ACCEPTANCE
```

- `main/knowledgebase/` is source material, not canonical truth by itself.
- `.agents/skills/smc/` contains the project's canonical methodology.
- Each concept has one primary semantic owner.
- `01_micro_structure.md` owns Phase 1 candle-level microstructure semantics.
- `skill.md` is an index only.
- `main/knowledgebase/` must never be modified by this workflow.
- Generic SMC knowledge must not silently override project source evidence or canonical rules.

## 2. Scope

This workflow currently audits methodology layers across both the structural and execution domains. It tracks explicit contracts (C1–C15) corresponding to structural components, execution modules, and risk policies.

Source material is used to detect boundary violations, and higher-layer rules are routed to their existing semantic owners.

## 3. Contracts under reconciliation

The reconciliation workflow tracks the following structural and execution contracts (C1–C15). They must not be silently closed by implementation:

### C1 — Candle Extreme Breach deterministic OHLC model

Define exactly which OHLC predicates constitute a breach, including the distinction between wick and body breach, without conflating candle breach with structural break.

Required outcome:
- deterministic predicate;
- explicit reference extreme;
- explicit breach mode;
- no structural interpretation.

### C2 — Candle Extreme Protection + Equal Extreme Reference Transfer

Define the relationship between the protected candle extreme and the active equal-extreme reference, including when reference transfer occurs and what remains protected.

Required outcome:
- deterministic state transition;
- explicit predecessor/reference;
- no promotion to structural protection or swing state.

### C3 — Outside Bar internal sequence / state-transition contract

An Outside Bar proves both extremes were exceeded, but OHLC alone does not establish whether the intrabar path was `OHLC` or `OLHC` when both are compatible.

Required outcome:
- preserve the Outside Bar relationship;
- represent internal sequence only when evidence establishes it;
- never infer OHLC vs OLHC from final OHLC alone;
- no fabricated event ordering.

### C4 — Reversal formations ownership and layer boundary

Define the boundary between candle-level anatomy and execution-layer eligibility for reversal formations.

Required outcome:
- Layer 1 may define deterministic candle anatomy/relationships;
- `06_execution.md` owns execution eligibility, POI/liquidity gating, trigger timing, and entry authorization;
- qualitative source language must not silently become numeric methodology.

### C5 — Methodology semantics vs historical observability

Define the epistemic boundary between the canonical methodology formation model and what aggregate historical OHLC data can actually establish.

Required outcome:
- methodology formation semantics may be recorded as methodology assumptions;
- historical observability must be represented separately in implementation-owned state;
- `METHODOLOGY_ASSUMED` must never be treated as `OBSERVED`;
- `UNAVAILABLE` must never be silently promoted to `OBSERVED`;
- absence of intrabar evidence must not manufacture an event sequence.

### C6 — LTF-CHoCH context after HTF interaction

Canonicalize the source-defined lower-timeframe CHoCH route used after an HTF Point of Interest interaction or canonical core-liquidity takeout.

Required outcome:
- [SOURCE_DIRECT] activation is a context condition, not a new lifecycle state;
- [SOURCE_DIRECT] the most recently formed valid LTF pullback / verified extreme supplies the governing LTF inducement reference;
- [SOURCE_DIRECT] arbitrary local pivots and invalid pullbacks cannot replace the reference;
- [PROJECT_CANONICAL / SOURCE_COMPOSED] the deterministic trigger is a completed LTF candle close beyond the governing LTF reference (the source establishes the LTF structural requirement, while the strict close-only trigger is project-composed for determinism);
- [SOURCE_DIRECT] the route must not independently alter the HTF bias;
- [SOURCE_DIRECT] confirmation still requires the applicable CHoCH prerequisite gate;
- [SOURCE_COMPOSED / PROJECT_CANONICAL] the LTF reference must not be reclassified as a Real Major IDM.

### C7 — Order Flow / SMT identification and selection

Canonicalize the source-defined distinction between Order Flow candidate moves, valid/unmitigated Order Flow, pre-inducement SMT/inducement traps, Decisional Order Flow, and Extreme Order Flow.

Required outcome:
- [SOURCE_DIRECT] the Order Flow candidate is the last opposing move before dominant continuation/displacement on the active impulsive leg;
- [SOURCE_COMPOSED] a multi-leg corrective move is represented as the whole relevant corrective leg while its protected endpoint remains intact;
- [SOURCE_DIRECT] a physical touch does not by itself establish OF mitigation;
- [SOURCE_DIRECT] pre-inducement formations are execution-excluded SMT/inducement traps;
- [SOURCE_DIRECT] Decisional OF is selected from the eligible OF lineage associated with the displacement causing canonical VALID_BOS;
- [SOURCE_DIRECT] Extreme OF is the furthest unmitigated eligible OF at the origin and shifts to the next such OF when mitigated;
- [SOURCE_DIRECT] SMT and OF remain distinct ontology classes.

### C8 — Engineering Liquidity identification and lifecycle

Canonicalize Engineering Liquidity as a core-liquidity reference derived from the valid pullback immediately preceding the active Extreme OF or Extreme OB.

Required outcome:
- [SOURCE_DIRECT] the active Extreme OF or Extreme OB must be established first;
- [SOURCE_DIRECT] Rejection Block is a separately typed PD-array/execution concept; source examples may use POI as a broad execution-location term, but RB is not an OF/OB-equivalent Extreme POI or an Engineering Liquidity dependency;
- [SOURCE_DIRECT] the reference pullback is the most recently formed valid pullback immediately preceding that active Extreme POI;
- [SOURCE_DIRECT] bullish ENG_LQD is liquidity below that pullback low;
- [SOURCE_DIRECT] bearish ENG_LQD is liquidity above that pullback high;
- [SOURCE_DIRECT] no valid pullback before the active Extreme OF/Extreme OB means no ENG_LQD reference;
- [SOURCE_COMPOSED] changing Extreme OF/Extreme OB provenance requires recomputing the active ENG_LQD reference;
- [SOURCE_DIRECT] ENG_LQD is distinct from IDM, POI, BOS, CHoCH, and Extreme POI mitigation;
- [SOURCE_COMPOSED] ENG_LQD may be coincident in price with IDM while retaining separate provenance.

### C9 — Entry authorization, price reference, and platform-order boundary

Canonicalize the distinction between True SMC entry authorization and broker/exchange order submission.

Required outcome:
- [SOURCE_DIRECT] each of the four entry modules has an explicit structural/execution prerequisite chain;
- [SOURCE_DIRECT] a sweep or mitigation alone never authorizes an entry;
- [SOURCE_DIRECT] the Decisional POI execution route is downstream of active IDM takeout; IDM_TAKEN must precede Decisional POI mitigation/confirmation in the canonical route;
- [SOURCE_COMPOSED] direct candle-confirmation entries use the completed confirmation-candle close as the methodology price reference;
- [SOURCE_DIRECT] Decisional and Extreme POI entries require independent execution confirmation after mitigation;
- [IMPLEMENTATION_POLICY] broker order type (market/limit/stop) is not a methodology fact unless a separate canonical trading-plan rule explicitly fixes it;
- [IMPLEMENTATION_POLICY] order submission, fill, and open-position state remain distinct from entry authorization;
- [IMPLEMENTATION_POLICY] pending-order expiry/cancellation/re-entry are handled by the separate order-lifecycle policy.

### C10 — Stop-loss anchor and buffer contract

Canonicalize the source-backed stop-loss anchor for each entry module while keeping the unspecified buffer as a separate execution configuration.

Required outcome:
- [SOURCE_DIRECT] IDM Sweep -> sweeping-candle extreme;
- [SOURCE_DIRECT] Decisional POI Mitigation -> confirming/reversal-pattern extreme;
- [SOURCE_DIRECT] Engineering Liquidity Sweep -> validated sweep/confirmation extreme;
- [SOURCE_DIRECT] Extreme POI Mitigation -> confirming/reversal-pattern extreme;
- [IMPLEMENTATION_POLICY] `P` (buffer) is an explicit downstream execution parameter;
- [SOURCE_GAP] the knowledgebase does not define one universal numeric pip/tick buffer;
- [IMPLEMENTATION_POLICY] missing `P` must block automatic order submission rather than invent a default.

### C11 — Target resolution and configurable Target Plan (RECONCILED — CONTROLLED POLICY CHOICES REMAIN)

Chart analysis identifies structural/liquidity destination levels that can be consumed downstream as target inputs. The source material does not define a universal target-selection priority because target use is an implementation/trading-policy concern.

Required outcome:
- [SOURCE_DIRECT] direct same-timeframe pro-trend uses the current confirmed external extreme / external liquidity as a canonical target candidate;
- [SOURCE_DIRECT] LTF execution may use the source-supported higher-timeframe external target or lower-timeframe structural/BOS destination, but the source does not define one universal priority between them;
- [SOURCE_COMPOSED] countertrend target candidates are setup-specific and may resolve to inducement, Engineering Liquidity, external liquidity, or the next canonical POI/destination according to the active scenario;
- [SOURCE_GAP / CONTROLLED POLICY] a universal countertrend single-coordinate resolver is not source-defined; this remains a setup-specific implementation/policy choice and must not be invented as methodology;
- [IMPLEMENTATION] downstream Target Discovery may collect structural/liquidity chart levels as target inputs while preserving provenance;
- [IMPLEMENTATION_POLICY] a configurable Target Plan may assign collected target inputs to separate trade legs (for example T1/T2/T3). Leg count and allocation are configurable and are not methodology constants;
- [IMPLEMENTATION_POLICY] fixed-R, where permitted by the applicable trading policy, is a non-structural policy mechanism and must not be mislabeled as canonical SMC provenance;
- [IMPLEMENTATION_POLICY] RR is evaluated against an already selected implementation target and must not create a canonical SMC target;
- [IMPLEMENTATION_POLICY] absence of a resolvable target for a configured leg blocks automatic TP submission for that leg;
- [IMPLEMENTATION_POLICY] current monitor behavior is notification-only: target reach emits an alert/notification and does not claim position closure, partial closure, stop movement, or broker fill.

### C12 — Trading policy: position sizing, risk budget, sessions, news, and logging

Canonicalize the source-backed trading-plan rules as a separate configurable policy layer.

Required outcome:
- [IMPLEMENTATION_POLICY] position size is calculated only after canonical entry and stop resolution;
- [IMPLEMENTATION_POLICY] risk amount is account balance multiplied by configured risk percentage;
- [IMPLEMENTATION_POLICY] position size uses exact stop distance and instrument pip/tick value;
- [IMPLEMENTATION_POLICY] source example values (0.5% fixed risk, 0.5% max running risk, one trade/session, two trades/day, 1.0% daily loss) are configurable policy values, not universal SMC structure;
- [IMPLEMENTATION_POLICY] session windows use UK local time with DST-aware timezone handling;
- [IMPLEMENTATION_POLICY] high-impact GBP/USD news avoidance is a configurable news gate for the documented GBPUSD plan;
- [IMPLEMENTATION_POLICY] policy state survives restarts and is reconciled with account/broker history;
- [IMPLEMENTATION_POLICY] missing required policy inputs fail closed for automatic order submission;
- [IMPLEMENTATION_POLICY] trade logging does not alter structural truth.

### C13 — Countertrend scenario composition

Canonicalize the three source-defined countertrend scenarios as composition contracts without redefining their underlying structural semantics.

Required outcome:
- [SOURCE_COMPOSED] Internal Structure Toward Inducement Takeout consumes the prevailing HTF context, active IDM, LTF internal structure, and pre-IDM SMT exclusion;
- [SOURCE_COMPOSED] Inducement Liquidity Run consumes IDM_TAKEN and permits continued delivery toward additional canonical liquidity/POI before reversal;
- [SOURCE_COMPOSED] Core Liquidity Sweep Failure / POI Failure consumes initial liquidity interaction, reaction failure, deeper canonical POI/core-liquidity delivery, and the existing CHoCH route when its prerequisites pass;
- [SOURCE_COMPOSED] countertrend scenarios use existing entry modules and target/risk policies;
- [SOURCE_DIRECT] no scenario creates an alternate IDM, POI, BOS, CHoCH, or broker-order definition.

### C14 — Updated Decisional / Extreme Order Block selection

Canonicalize the later source update that supersedes the earlier "first valid OB after inducement" shortcut.

Required outcome:
- [SOURCE_DIRECT] Decisional OB = valid Order Block that actually causes the canonical BOS;
- [SOURCE_DIRECT] selection is tied to causal BOS provenance, not merely timing after inducement;
- [SOURCE_DIRECT] Extreme OF is resolved first; Extreme OB is the furthest unmitigated valid Order Block within the active Extreme OF lineage; a global search across all origin-side OBs is not canonical;
- [SOURCE_DIRECT] if a candidate OB candle lacks the required FVG association, selection shifts to the next eligible candle in the relevant source-defined sequence and FVG association is evaluated again; the selected candle must independently satisfy all OB validation pillars;
- [SOURCE_DIRECT] Order Block validity is based on its own validation pillars and is not automatically invalidated by an unmitigated/failed Order Flow;
- [SOURCE_DIRECT] a valid Decisional OB may be used while the associated OF remains unmitigated, provided Rule-of-Two and execution gates remain satisfied;
- [PROJECT_CANONICAL] historical Decisional OB identity is immutable once tied to the causal BOS event.

### C15 — Timeframe execution route

Canonicalize the source-supported choice between direct same-timeframe execution and optional HTF→LTF execution refinement.

Required outcome:
- [SOURCE_DIRECT] direct same-timeframe execution remains valid;
- [IMPLEMENTATION_POLICY] multi-timeframe execution is optional and explicitly configured;
- [SOURCE_DIRECT] HTF supplies narrative, structure, POI, and liquidity context;
- [SOURCE_DIRECT] LTF refines execution and may activate the canonical LTF-CHoCH route;
- [SOURCE_DIRECT] LTF must not silently redefine the HTF narrative;
- [SOURCE_DIRECT] source timeframe-pair tables are examples, not universal SMC constants.

## 4. Source analysis

For every relevant source passage create a source record:

- `source_id`
- `source_file`
- `source_location`
- `source_text`
- `concept`
- `statement_type`
- `confidence`

Classify each passage as one of:

- `EXISTING_CANONICAL_RULE`
- `NEW_CANONICAL_CANDIDATE`
- `SUPPORTING_EVIDENCE`
- `OUT_OF_SCOPE`
- `AMBIGUOUS_SOURCE`
- `CONFLICTING_SOURCE`

Transcription errors must be treated as source uncertainty, not automatically promoted into methodology.

## 5. Canonical comparison

For each relevant source claim compare it against the current semantic owner.

Record:

- source claim;
- current canonical claim;
- relationship;
- semantic difference;
- boundary difference;
- determinism issue;
- affected documents;
- affected tests.

A source passage that merely uses different wording is not a new rule.

A source passage that introduces a different threshold, condition, sequence, or ownership is a potential contract change and requires reconciliation.

## 6. Conflict handling

Conflicts must remain explicit until resolved.

Examples include:
- 38.2% versus 50% retracement statements;
- wick versus body interpretation;
- major versus minor inducement qualification;
- competing definitions of a valid break.

Do not silently select one transcript because it appears more plausible.

When two source passages differ:
1. preserve both source references;
2. determine whether the difference is contextual, temporal, parameter-specific, or genuinely contradictory;
3. compare against the current semantic owner;
4. identify downstream consequences;
5. route unresolved conflicts to human review.

## 7. Change Set

No implementation may begin until a Change Set exists containing:

- affected concept;
- source evidence;
- current canonical rule;
- proposed canonical change;
- semantic owner;
- boundaries;
- deterministic conditions;
- affected documents;
- affected tests;
- unresolved questions;
- approval status.

Approval states:

```
APPROVED
REJECTED
REQUESTED_REVISION
```

Only `APPROVED` changes may be implemented.

## 8. Implementation rules

The Implementer:

- changes only the approved Change Set;
- modifies the existing semantic-owner document rather than creating a competing rule;
- preserves non-equivalences;
- does not move higher-layer semantics into Layer 1;
- does not invent missing thresholds;
- does not resolve ambiguous OHLC paths by assumption;
- updates references/tests required by the approved semantic change.

## 9. Independent validation

The Validator must not rely on the Implementer's interpretation alone.

Validation must check:

### Semantic
The implemented rule matches the approved canonical rule.

### Boundary
The rule does not create or alter higher-layer structural state.

### Determinism
Equivalent OHLC input produces the same result; insufficient information produces an explicit unknown/undetermined result rather than an invented sequence.

### Ownership
Each rule has one semantic owner.

### Regression
Existing canonical behavior outside the approved Change Set remains unchanged.

### Source fidelity
The implementation can be traced back to the approved source evidence.

## 10. Required artifacts

Each reconciliation run produces:

### Source Map
Traceability from source passages to concepts and classifications.

### Contract Ledger
Open/closed status of the tracked contracts (C1–C15) and any newly discovered contractual issue.

### Change Set
Only the proposed canonical changes awaiting human approval.

### Validation Report
Independent validation evidence after implementation.

These are run artifacts. They are not additional competing methodology documents.

## 11. Acceptance criteria

A reconciliation run is complete only when:

- relevant source passages are mapped;
- canonical comparison is complete;
- C1–C15 are explicitly resolved or remain explicitly blocked;
- unresolved source conflicts are not hidden;
- semantic ownership is preserved;
- deterministic behavior is validated;
- approved changes are implemented;
- independent validation passes;
- affected tests pass.

An unresolved contract is a controlled **not-ready** state, not permission to guess.

## 12. Required traceability

Every canonical rule changed by this workflow must remain traceable:

```
SOURCE PASSAGE
    ↓
SOURCE RECORD
    ↓
CONTRACT / CHANGE SET
    ↓
HUMAN APPROVAL
    ↓
CANONICAL DOCUMENT
    ↓
TEST / VALIDATION
```

This traceability is mandatory for future audits and prevents source transcript wording from silently becoming canonical methodology.
