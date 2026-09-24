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

## 2. Phase 1 scope

This workflow currently audits only:

1. Candle Extreme Breach
2. Candle Extreme Protection
3. Inside Bar
4. Outside Bar
5. Equal High (EQH)
6. Equal Low (EQL)
7. Equal Extreme Reference Transfer
8. Candle Internal Sequence
9. Candlestick-Based Trend

Higher-layer concepts remain outside Phase 1 even when source transcripts discuss them:

- Pullback Formation / Candle-Level Valid Pullback
- Macro qualification
- Retracement-depth qualification
- IDM
- Confirmed Structural Swing
- BOS / CHoCH
- Order Flow / Order Block / POI
- Execution authorization
- Risk

Source material may be used to detect boundary violations, but higher-layer rules must be routed to their existing semantic owners.

## 3. Five Phase 1 contracts under reconciliation

The reconciliation workflow now tracks the Phase 1 contracts plus higher-layer contracts C6–C14. They must not be silently closed by implementation:

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
- activation is a context condition, not a new lifecycle state;
- the most recently formed valid LTF pullback / verified extreme supplies the governing LTF inducement reference;
- arbitrary local pivots and invalid pullbacks cannot replace the reference;
- the source-aligned deterministic trigger is a completed LTF candle close beyond the governing LTF reference;
- the route must not independently alter the HTF bias;
- confirmation still requires the applicable CHoCH prerequisite gate;
- the LTF reference must not be reclassified as a Real Major IDM.

### C7 — Order Flow / SMT identification and selection

Canonicalize the source-defined distinction between Order Flow candidate moves, valid/unmitigated Order Flow, pre-inducement SMT/inducement traps, Decisional Order Flow, and Extreme Order Flow.

Required outcome:
- the Order Flow candidate is the last opposing move before dominant continuation/displacement on the active impulsive leg;
- a multi-leg corrective move is represented as the whole relevant corrective leg while its protected endpoint remains intact;
- a physical touch does not by itself establish OF mitigation;
- pre-inducement formations are execution-excluded SMT/inducement traps;
- Decisional OF is selected from the eligible OF lineage associated with the displacement causing canonical VALID_BOS;
- Extreme OF is the furthest unmitigated eligible OF at the origin and shifts to the next such OF when mitigated;
- SMT and OF remain distinct ontology classes.

### C8 — Engineering Liquidity identification and lifecycle

Canonicalize Engineering Liquidity as a core-liquidity reference derived from the valid pullback immediately preceding the active Extreme POI.

Required outcome:
- the active Extreme POI must be established first;
- the reference pullback is the most recently formed valid pullback immediately preceding that active Extreme POI;
- bullish ENG_LQD is liquidity below that pullback low;
- bearish ENG_LQD is liquidity above that pullback high;
- no valid pullback before the active Extreme POI means no ENG_LQD reference;
- changing Extreme POI provenance requires recomputing the active ENG_LQD reference;
- ENG_LQD is distinct from IDM, POI, BOS, CHoCH, and Extreme POI mitigation;
- ENG_LQD may be coincident in price with IDM while retaining separate provenance.

### C9 — Entry authorization, price reference, and platform-order boundary

Canonicalize the distinction between True SMC entry authorization and broker/exchange order submission.

Required outcome:
- each of the four entry modules has an explicit structural/execution prerequisite chain;
- a sweep or mitigation alone never authorizes an entry;
- direct candle-confirmation entries use the completed confirmation-candle close as the methodology price reference;
- Decisional and Extreme POI entries require independent execution confirmation after mitigation;
- broker order type (market/limit/stop) is not a methodology fact unless a separate canonical trading-plan rule explicitly fixes it;
- order submission, fill, and open-position state remain distinct from entry authorization;
- pending-order expiry/cancellation/re-entry are handled by the separate order-lifecycle policy.

### C10 — Stop-loss anchor and buffer contract

Canonicalize the source-backed stop-loss anchor for each entry module while keeping the unspecified buffer as a separate execution configuration.

Required outcome:
- IDM Sweep -> sweeping-candle extreme;
- Decisional POI Mitigation -> confirming/reversal-pattern extreme;
- Engineering Liquidity Sweep -> validated sweep/confirmation extreme;
- Extreme POI Mitigation -> confirming/reversal-pattern extreme;
- `P` is an explicit downstream execution parameter;
- the knowledgebase does not define one universal numeric pip/tick buffer;
- missing `P` must block automatic order submission rather than invent a default.

### C11 — Target resolution hierarchy

Canonicalize target resolution separately for direct pro-trend, LTF, and countertrend execution.

Required outcome:
- direct same-timeframe pro-trend uses the current confirmed external extreme / external liquidity as primary target;
- LTF execution must explicitly select between the source-supported higher-timeframe external target and lower-timeframe structural/BOS destination;
- countertrend target is setup-specific and resolves to the next canonical destination defined by the active scenario;
- RR is evaluated against an already resolved target and must not create the target;
- absence of a canonical target blocks automatic TP submission.

### C12 — Trading policy: position sizing, risk budget, sessions, news, and logging

Canonicalize the source-backed trading-plan rules as a separate configurable policy layer.

Required outcome:
- position size is calculated only after canonical entry and stop resolution;
- risk amount is account equity multiplied by configured risk percentage;
- position size uses exact stop distance and instrument pip/tick value;
- source example values (0.5% fixed risk, 0.5% max running risk, one trade/session, two trades/day, 1.0% daily loss) are configurable policy values, not universal SMC structure;
- session windows use UK local time with DST-aware timezone handling;
- high-impact GBP/USD news avoidance is a configurable news gate for the documented GBPUSD plan;
- policy state survives restarts and is reconciled with account/broker history;
- missing required policy inputs fail closed for automatic order submission;
- trade logging does not alter structural truth.

### C13 — Countertrend scenario composition

Canonicalize the three source-defined countertrend scenarios as composition contracts without redefining their underlying structural semantics.

Required outcome:
- Internal Structure Toward Inducement Takeout consumes the prevailing HTF context, active IDM, LTF internal structure, and pre-IDM SMT exclusion;
- Inducement Liquidity Run consumes IDM_TAKEN and permits continued delivery toward additional canonical liquidity/POI before reversal;
- Core Liquidity Sweep Failure / POI Failure consumes initial liquidity interaction, reaction failure, deeper canonical POI/core-liquidity delivery, and the existing CHoCH route when its prerequisites pass;
- countertrend scenarios use existing entry modules and target/risk policies;
- no scenario creates an alternate IDM, POI, BOS, CHoCH, or broker-order definition.

### C14 — Updated Decisional / Extreme Order Block selection

Canonicalize the later source update that supersedes the earlier "first valid OB after inducement" shortcut.

Required outcome:
- Decisional OB = valid Order Block that actually causes the canonical BOS;
- selection is tied to causal BOS provenance, not merely timing after inducement;
- Extreme OB remains the furthest valid origin-side Order Block;
- Order Block validity is based on its own validation pillars and is not automatically invalidated by an unmitigated/failed Order Flow;
- a valid Decisional OB may be used while the associated OF remains unmitigated, provided Rule-of-Two and execution gates remain satisfied;
- historical Decisional OB identity is immutable once tied to the causal BOS event.

### C15 — Timeframe execution route

Canonicalize the source-supported choice between direct same-timeframe execution and optional HTF→LTF execution refinement.

Required outcome:
- direct same-timeframe execution remains valid;
- multi-timeframe execution is optional and explicitly configured;
- HTF supplies narrative, structure, POI, and liquidity context;
- LTF refines execution and may activate the canonical LTF-CHoCH route;
- LTF must not silently redefine the HTF narrative;
- source timeframe-pair tables are examples, not universal SMC constants.

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
Open/closed status of the four Phase 1 contracts and any newly discovered contractual issue.

### Change Set
Only the proposed canonical changes awaiting human approval.

### Validation Report
Independent validation evidence after implementation.

These are run artifacts. They are not additional competing methodology documents.

## 11. Acceptance criteria

A Phase 1 reconciliation run is complete only when:

- relevant source passages are mapped;
- canonical comparison is complete;
- C1–C5 are explicitly resolved or remain explicitly blocked;
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
