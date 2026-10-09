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

## IDM reconciliation — Major IDM continuity after BOS

The source set distinguishes Minor IDM from Major IDM and explicitly supports the external-boundary case: when a trading range contains only a Minor IDM and no newly formed Major IDM, the governing external liquidity / prior protected boundary serves as the Major Inducement. After BOS, if price creates only Minor IDM and does not establish a new Major IDM, the previous Protected Low in a bullish range or Protected High in a bearish range therefore remains the active Major IDM reference.

Canonical consequence:
- `MAJOR_IDM` is a single semantic class.
- A post-BOS valid pullback may establish a new Major IDM.
- Minor IDM alone does not replace the prior Major IDM.
- No `FALLBACK_MAJOR_IDM` or `REAL_MAJOR_IDM` ontology class is required.
- Major IDM provenance may be pullback-derived or protected-boundary-derived.

This is source reconciliation, not a new implementation heuristic.

## First-BOS bootstrap baseline — source gap and project-canonical resolution

### Active first-BOS bootstrap process boundary

For each newly initialized structural regime, including chart inception and the post-CHoCH regime, the first-BOS bootstrap process remains active until that regime's first `VALID_BOS`. It may coexist with runtime process states `BOOTSTRAP`, `CONFIRMATION_LOCKED`, and `POST_CHOCH`.

While this process condition is active, `BOOTSTRAP_ORIGIN_ANCHOR` penetration has precedence over ordinary BOS/CHoCH classification and routes to `BOOTSTRAP_ANCHOR_BREAK → BOOTSTRAP_REVERSAL`.


The indexed source corpus was reviewed for an explicit first-BOS retracement baseline. The reconciliation result is intentionally split into **source evidence** and **project-canonical policy**.

### Source-supported findings

The source material repeatedly supports the sequence:

```text
VALID PULLBACK
    ↓
IDM TAKEOUT
    ↓
CONFIRMED STRUCTURAL SWING
    ↓
RETRACEMENT MEASURED
    ↓
STRUCTURAL SWING BREAK
    ↓
VALID_BOS
```

The source material also supports that the relevant retracement extreme is the lowest/highest point reached by the active retracement as it progresses, and that the active pullback/extreme can shift when a continuation attempt is insufficient.

The source corpus does **not** provide a deterministic first-BOS baseline before the first canonical Dealing Range exists.

### Project-canonical resolution

The project resolves the gap with an isolated `BOOTSTRAP_ORIGIN_ANCHOR` and transient `BOOTSTRAP_RANGE`.

This policy is explicitly **not source-direct**:

- `BOOTSTRAP_ORIGIN_ANCHOR` is a temporary initialization measurement anchor backed by an actual completed candle;
- chart inception uses the first effective completed candle as `C0`, the causal mapping-origin candle of the mapping domain. The initial direction is then resolved by the explicit project-canonical bootstrap-direction rule above. This does not make a claim about market history outside the mapping domain;
- post-CHoCH initialization requires explicit active-impulse origin provenance;
- `BOOTSTRAP_RANGE` exists only for first-BOS retracement qualification;
- the bootstrap anchor/range are never canonical Protected Structural Extreme or governing Dealing Range state;
- `dynamic_retracement_extreme` remains dynamic until the structural break and locks only when `VALID_BOS` occurs;
- under aggregate OHLC, the break/BOS candle is excluded from the pre-break retracement-extreme observation window;
- missing required provenance fails closed.

### Reconciliation status

```text
SOURCE GAP
    ↓
EXPLICIT PROJECT-CANONICAL POLICY
    ↓
TRACEABLE IMPLEMENTATION CONTRACT
```

The bootstrap policy must never be described as if it were directly defined by the source corpus. Future source material may supersede the gap only through the normal reconciliation and human-approval workflow.
### Bootstrap reversal reconciliation

The bootstrap-reversal rule applies throughout the active first-BOS process for a newly initialized regime, not only while the runtime state enum is `BOOTSTRAP`. Therefore anchor-break preclassification remains effective during `CONFIRMATION_LOCKED` and post-CHoCH first-BOS processing.

The indexed source corpus does not define a deterministic first-BOS bootstrap-reversal state machine. It contains descriptive examples of directional/bias shifts, but no source-owned rule that turns a pre-structure bootstrap anchor break into a CHoCH or defines the required downstream restart semantics.

The project therefore resolves this separately and explicitly:

```text
BOOTSTRAP_ORIGIN_ANCHOR physical break
        ↓
BOOTSTRAP_ANCHOR_BREAK
        ↓
BOOTSTRAP_REVERSAL
        ↓
new active bootstrap lineage
        ↓
new Layer-1 / Layer-2 construction
```

This is project-canonical composition, not a source quotation.

The reconciliation boundary is strict:

- `BOOTSTRAP_ANCHOR_BREAK` is a physical initialization event, not an external structural break.
- `BOOTSTRAP_REVERSAL` is not `CHoCH_CONFIRMED`, `VALID_BOS`, `MAJOR_IDM_SWEEP`, or `PROTECTED_STRUCTURAL_EXTREME`.
- The reversal candle is a real OHLC candle and becomes the explicit active-impulse origin for the new bootstrap lineage; no synthetic candle or historical rewind is permitted.
- The new direction re-derives its `BOOTSTRAP_ORIGIN_ANCHOR` from that actual candle.
- Pre-reversal bootstrap candidates, provisional/confirmed swing state, macro-qualification state, dynamic retracement state, active IDM/reference, and transient bootstrap measurement state are retired forward-only without retroactive reclassification.
- Structural BOS/CHoCH pipelines remain unavailable until their independent canonical prerequisites are satisfied.
## Mapping-origin and swing-promotion reconciliation

### Initial bootstrap direction reconciliation

The indexed source corpus does not define a deterministic chart-inception direction-selection rule for the first mapping candle. The project therefore makes the initialization rule explicit rather than implying it is source-direct:

```text
C0.Close > C0.Open → INITIAL_BOOTSTRAP_DIRECTION = BULLISH
C0.Close < C0.Open → INITIAL_BOOTSTRAP_DIRECTION = BEARISH
C0.Close = C0.Open → UNRESOLVED
```

A non-directional `C0` cannot justify a guessed direction. The first later eligible completed non-doji candle resolves the initialization direction, after which the anchor is still derived from the original `C0`. This is project-canonical startup policy only.


The project-canonical mapping model treats the first eligible completed candle of an initial mapping domain as `C0`, the mapping-origin candle and causal state-machine anchor. This is not an arbitrary bootstrap placeholder: the mapping is defined to begin there and to construct higher-layer state chronologically from lower-layer evidence. A later `BOOTSTRAP_REVERSAL` does not redefine `C0`; it starts a new active lineage from the actual reversal candle while preserving the original mapping chronology.

The indexed source evidence describes IDM takeout as acquiring/confirming a swing point and then separately evaluates retracement depth and the later swing break. The canonical state representation therefore distinguishes the source-described swing point from the BOS-eligible structural object: `IDM_TAKEN → SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME → MACRO RETRACEMENT QUALIFICATION → CONFIRMED_STRUCTURAL_SWING → STRUCTURAL_SWING_BREAK → VALID_BOS`.
For the bootstrap case, the candidate must exist before macro qualification because its structural price is an endpoint of the first-BOS measurement baseline: `BOOTSTRAP_ORIGIN_ANCHOR → SWING_CANDIDATE → BOOTSTRAP_RANGE → MACRO RETRACEMENT QUALIFICATION → CONFIRMED_STRUCTURAL_SWING`.

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
- [SOURCE_DIRECT] the 2026 source explicitly calls this the LTF structure-cycle “glitch”: after HTF POI/core-liquidity interaction, the inducement pullback can be the CHoCH reference before the ordinary LTF external boundary is broken;
- [SOURCE_DIRECT] arbitrary local pivots and invalid pullbacks cannot replace the reference;
- [SOURCE_RECONCILED] the break mode is inherited from the active LTF IDM classification: Major IDM permits the normal wick-break CHoCH path; when only Minor IDM exists, the external protected boundary functions as Major IDM, a wick is `MAJOR_IDM_SWEEP`, and CHoCH requires a completed body close beyond the applicable LTF reference;
- [SOURCE_DIRECT] the route must not independently alter the HTF bias;
- [SOURCE_DIRECT] confirmation still requires the applicable CHoCH prerequisite gate;
- [SOURCE_COMPOSED / PROJECT_CANONICAL] the LTF reference must not be reclassified as a Major IDM merely because it participates in the LTF-CHoCH route;
- [SOURCE_COMPOSED / PROJECT_CANONICAL] the implementation must not generalize the Minor-Inducement body-close condition to every LTF CHoCH.

### C7 — Order Flow / SMT identification and selection

Canonicalize the source-defined distinction between Order Flow candidate moves, valid/unmitigated Order Flow, pre-inducement SMT/inducement traps, Decisional Order Flow, and Extreme Order Flow.

Required outcome:
- [SOURCE_DIRECT] the Order Flow candidate is the last opposing move before dominant continuation/displacement on the active impulsive leg;
- [SOURCE_COMPOSED] a multi-leg corrective move is represented as the whole relevant corrective leg while its protected endpoint remains intact;
- [SOURCE_DIRECT] a physical touch does not by itself establish OF mitigation;
- [SOURCE_DIRECT] ordinary pre-inducement and other unselected range formations are execution-excluded SMT/inducement traps; the source expressly distinguishes the Origin OB reserve;
- [SOURCE_RECONCILED] the physical takeout boundary includes ordinary formations created between active IDM formation and `IDM_TAKEN`, so the classification contract does not stop at the narrower phrase “pre-IDM”;
- [SOURCE_DIRECT] Decisional OF is selected from the eligible OF lineage associated with the displacement causing canonical VALID_BOS;
- [SOURCE_DIRECT] Extreme OF is the furthest unmitigated eligible OF at the origin and shifts to the next such OF when mitigated;
- [SOURCE_DIRECT] SMT and OF remain distinct ontology classes.

#### POI Identification Secret — `IDM_TAKEN` gate and Origin OB reserve exception

Primary source: `knowledgebase/sources/truesmc2026.txt`, **Part 6 | POI Identification Secret**.

Source evidence and authority labels:
- [SOURCE_DIRECT] At **00:00:42–00:01:33**, Part 6 states that a dealing range has at most two POIs—the Decisional and Extreme POIs—and excludes other OF/OB formations as SMT/inducement traps except for the Origin OB.
- [SOURCE_DIRECT] At **00:03:29–00:04:09**, Part 6 identifies the Origin OB as the furthest unmitigated OB at the dealing-range origin, says its validity is independent of parent-OF mitigation, and names it the last line of defense when the applicable Extreme OB fails.
- [SOURCE_DIRECT] At **00:09:06–00:09:33**, the worked example again classifies other range formations as traps/weak OBs rather than valid reversal zones.
- [SOURCE_RECONCILED] The implementation's `IDM_TAKEN` event formalizes the physical inducement-takeout boundary for the active lineage. The ordinary-candidate exclusion therefore covers formations created both before active IDM formation and between IDM formation and takeout. This temporal wording is the canonical event contract; it should not be misrepresented as a literal transcript token.

Canonical interpretation owned by `.agents/skills/smc/06_execution.md`:
- The active canonical tradable POI set contains at most two slots: Decisional POI and Extreme POI. Origin OB never adds a third simultaneous active slot.
- An ordinary OF/OB formed before the applicable active IDM is taken out is `SMT / INDUCEMENT_TRAP`, whether the formation predates IDM formation or lies between formation and takeout. It remains non-tradable for the active lineage after a later takeout; there is no retrospective promotion.
- Trap observations may be retained for provenance, auditability, and history, and may be displayed when useful with clear trap/exclusion status. Storage or display is not activation, tradability, or entry authorization.
- Origin OB is the one named latent-reserve exception to the ordinary formation-time rule, not a general historical-candidate escape hatch. It must remain non-active until the active IDM/takeout gate and its existing canonical validity/fallback activation conditions pass. When it becomes applicable, it occupies the Extreme slot. Its activation must not be equated with, or cause, the CHoCH-based canonical `POI_FAILURE` lifecycle state.
- For ordinary post-takeout OF/OB formations, `IDM_TAKEN` only opens the remaining canonical validation path; it does not itself validate or activate a POI, satisfy Rule of Two, or authorize entry.

#### Hybrid Decisional zones, dual execution, and Origin OB fallback

Additional source evidence and canonical clarification from Part 6:

- [SOURCE_DIRECT] At **00:01:35–00:02:34**, Part 6 defines Decisional OF as the last opposing move before reversal displacement causing BOS and places the Decisional OB inside that Decisional OF. This is explicit parent-zone/refinement geometry, not two unrelated structural targets.
- [SOURCE_DIRECT] At **00:03:29–00:04:09**, Part 6 says Origin OB validity is independent of parent OF mitigation and identifies Origin OB as the last line of defense if the applicable Extreme OB fails.
- [SOURCE_DIRECT] At **00:07:43–00:09:04**, the bearish worked example identifies the Decisional OB inside the Decisional OF and the Extreme OB within its Extreme OF lineage.
- [SOURCE_DIRECT] At **00:10:35–00:11:25**, the execution example describes the Decisional OB failing and a later execution opportunity at Extreme OF without Extreme OB mitigation. This supports separate OF/OB mitigation states, but is not itself the exact parent-reaction-fails-before-child-reach scenario.
- [SOURCE_RECONCILED] The Rule of Two counts independent structural roles/targets, not nested zone outlines. Decisional OF plus its contained Decisional OB refinement share one Decisional slot; the Extreme zone is the second slot. Three visible outlines therefore do not imply three independent POI slots.
- [PROJECT_CANONICAL] If parent Decisional OF is canonically mitigated and its reaction fails before reaching the nested Decisional OB, the child OB remains executable only while its own OB validation, unmitigated state, identity, active-IDM/takeout gate, and all execution gates remain satisfied. Parent OF state does not automatically propagate into child OB state.
- [SOURCE_RECONCILED] Origin OB is a sequential last-resort stage after the applicable Extreme path fails; it does not coexist as a third independent active slot. It must remain independently valid/unmitigated, satisfy its FVG/imbalance and other OB pillars, and pass existing canonical activation gates.

Canonical interpretation owned by .agents/skills/smc/06_execution.md:
- Separate parent/child geometry from structural-slot count; do not suppress a valid inner Decisional OB merely because its parent OF was mitigated.
- Preserve the Rule of Two, pre-takeout trap gate, no-retrospective-promotion rule, and all OB pillars.
- Origin OB is sequential fallback, not nested Decisional refinement and not a third independent active target.

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
- [SOURCE_COMPOSED] Internal Structure Toward Inducement Takeout consumes the prevailing HTF context, active IDM, LTF internal structure, and ordinary pre-takeout SMT exclusion;
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
- [SOURCE_DIRECT] if a candidate OB candle lacks the required FVG association, the source reconciliation describes advancing to the next eligible candle and re-evaluating FVG association; the selected candle must independently satisfy all OB validation pillars;
- [PROJECT_CANONICAL] for this project, the fallback pointer is resolved deterministically to the immediately next chronological candle; no arbitrary forward skipping is permitted, and the next candle must independently satisfy the OB validation pillars;
- [SOURCE_DIRECT] Order Block validity is based on its own validation pillars and is not automatically invalidated by an unmitigated/failed parent Order Flow;
- [SOURCE_RECONCILED] parent OF mitigation/reaction failure does not automatically mitigate the contained child OB; child execution remains allowed only when its own mitigation/validity state and all canonical gates remain satisfied;
- [SOURCE_DIRECT] Origin OB is a separate latent reserve, independent of parent-OF mitigation, and the last line of defense when the applicable Extreme OB fails; it is not an ordinary SMT trap or a third active Rule-of-Two slot;
- [SOURCE_RECONCILED] Origin OB formation may predate `IDM_TAKEN`, but the reserve can be activated for trading only after the canonical active-IDM/takeout gate and existing Origin OB validity/fallback activation conditions pass;
- [SOURCE_RECONCILED] Extreme execution-location failure is distinct from canonical `POI_FAILURE`, which remains the separately defined CHoCH-based execution lifecycle state;
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
