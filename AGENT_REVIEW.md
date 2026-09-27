# CURRENT TASK
Phase 5c: Direct validator reconciliation of the canonical SMC documentation against the newer 2026 market-structure sources.

# DEVELOPER REPORT
**Current Repository State:**
* **Branch:** main
* **HEAD before latest correction sync:** 97fe112e145cce29dc6e26f6c419921294a8bf3a
* **Repository writes:** completed through GitHub; documentation-only commits.
* **Knowledgebase:** untouched.
* **Runtime Python files / analyzed JSON:** untouched.

**Implementation decisions:**
- **2026 Layer 3 ordering corrected:** the canonical lifecycle now treats `IDM_TAKEN` as confirming the relevant `CONFIRMED_STRUCTURAL_SWING`; retracement-depth/candle-structure qualification is a later prerequisite for the continuation `VALID_BOS`.
- **Insufficient retracement behavior clarified:** an attempted continuation break without the stored qualification is not `VALID_BOS`; the newer retracement/pullback reference becomes the basis for the next attempt.
- **`04_BOS_mechanics.md` synchronized:** BOS mechanics now consume the IDM-confirmed swing before the stored Layer 3 retracement qualification.
- **`06_execution.md` synchronized:** Decisional POI execution explicitly occurs downstream of active IDM takeout; Rejection Block's Extreme-POI role and Engineering Liquidity extension are marked as project-composed execution representation rather than source-direct ontology.
- **`08_implementation.md` synchronized:** structural lifecycle, Decisional POI prerequisites, and configurable RR gating were corrected; the stale universal minimum 1:2 RR requirement was removed.
- **`source_reconciliation.md` synchronized:** C9 records the IDM-takeout prerequisite for Decisional POI execution; the Rejection Block Extreme role remains an execution-layer composition.
- **`full_methodology_gap_audit.md` synchronized:** the 2026 ordering correction and current LTF-CHoCH canonicalization status are recorded.
- The latest correction reopens and canonicalizes the LTF-CHoCH route in `05_CHOCH_mechanics.md`, `08_implementation.md`, and `source_reconciliation.md`; no runtime Python, analyzed JSON, or knowledgebase file is modified.

# VALIDATION REPORT
Targeted repository validation after the edits confirms:
- `03_structural_semantic_authority.md` contains no `SWING_CANDIDATE` terminology and uses `IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING → STRUCTURAL RETRACEMENT QUALIFICATION FOR BOS`.
- `04_BOS_mechanics.md` uses IDM-takeout prerequisite wording rather than the obsolete swing-candidate wording.
- `08_implementation.md` no longer contains the stale universal “minimum 1:2 RR” rule.
- Decisional POI execution and governance traceability contain the IDM-takeout prerequisite.
- `knowledgebase/` and runtime files remain untouched.
- Tests: N/A — documentation-only reconciliation.

# REQUIRED CORRECTIONS
See the latest DIRECT VALIDATOR RE-AUDIT section below. Eight canonical issues were identified and corrected.

# HISTORICAL SPECIFICATION GAPS — CLOSED / SUPERSEDED
- Target selection priority and countertrend target-coordinate selection are downstream implementation/trading-policy decisions, not canonical methodology gaps.
- Fixed-R target generation and break-even/profit-lock/trailing are downstream implementation/trade-management decisions, not canonical methodology gaps.
- Premium/discount semantic gate is canonicalized; any residual issue is source traceability only.
- `POI_FAILURE` provenance, Rejection Block separation, and Engineering Liquidity derivation are canonicalized; no active reconciliation gap remains there.
- The runtime `smc_analyzer.py` remains incomplete relative to the canonical structural engine; this is the principal strategy-runtime implementation gap.

# IMPLEMENTATION STATUS
Phase 5c documentation reconciliation is complete.

# COMMITS
COMMIT: 3f25488
FILES: .agents/skills/smc/04_BOS_mechanics.md
PURPOSE: Clarify BOS IDM prerequisite wording after the 2026 lifecycle reconciliation.

PRIOR COMMITS:
- e8e7923 — Layer 3 swing-confirmation lifecycle reconciliation.
- 67f6dbd — BOS lifecycle synchronization.
- 03d6b4a — POI provenance and Decisional POI entry-gate reconciliation.
- a0bf61a — Implementation mapping synchronization.
- 3ba449d — 2026 reconciliation recorded in full methodology gap audit.
- 3484fe8 — Source-reconciliation governance update.

# NOTE
The canonical source policy remains unchanged: `.agents/skills/smc/` is the methodology authority; `knowledgebase/` is source evidence and was not modified.


## DIRECT VALIDATOR IMPLEMENTATION — 2026-09-25

The target-resolution architecture was re-audited and implemented in the canonical skill.

### Implemented
- `.agents/skills/smc/07_risk.md`: configurable Target Plan / multi-leg management, separation of target achievement from profit protection, and current notification-only target contract.
- `.agents/skills/smc/08_implementation.md`: Target Discovery → valid target candidates → configurable Target Plan → leg assignment → notification-only monitor mapping; target provenance and non-structural fixed-R policy separation; no implicit universal target winner.
- `.agents/skills/smc/source_reconciliation.md`: C11 reconciled so the source gap is no longer treated as a missing universal target-priority algorithm; remaining universal countertrend single-coordinate resolver is explicitly source-under-specified.
- `.agents/skills/smc/reconciliation/full_methodology_gap_audit.md`: target-plan architecture and controlled remaining source gaps recorded.

### Current monitor contract
The monitor may emit a `TARGET_REACHED` / target notification when price reaches an active configured target. It must not claim position closure, partial closure, stop movement, or broker fill. Actual trade management remains future scope.

### Audit disposition
- No `knowledgebase/` files were modified by this implementation.
- No runtime Python or analyzed JSON files were modified.
- No universal target-priority, fixed-R, or break-even methodology rule was invented.
- Three-leg / multi-leg allocation is configurable policy, not a methodology constant.
- `BREAK_EVEN` is treated as future stop-management behavior, not a fallback target.

### AUDIT PART 1 DISPOSITION — CLOSED
The first audit part is considered resolved and does not require further canonical SMC-methodology changes.

The following are implementation-plan / architecture concerns, not missing methodology rules:
- Target Discovery component and valid-target-candidate collection.
- Configurable Target Plan and multi-leg target allocation.
- Target-to-leg assignment and target provenance propagation.
- Notification-only `TARGET_REACHED` monitor behavior.
- Separation of `TARGET_REACHED` from `POSITION_CLOSED`, `LEG_CLOSED`, `STOP_MOVED`, and `BROKER_FILL`.
- Future BE/profit-lock/trailing behavior as separate trade-management policy, not as canonical target semantics.

Canonical methodology remains responsible only for defining which structural/liquidity destinations constitute valid target candidates. No universal target-priority, universal countertrend coordinate, or universal RR-derived target is to be invented.

**Next audit work must therefore continue from the remaining implementation/specification gaps rather than reopening this closed target-architecture point.**

## AUDIT PART 2 — REMAINING GAPS DISPOSITION — 2026-09-25

The remaining implementation/specification gaps were re-audited after the target-architecture closure.

### Findings
- **No unresolved canonical SMC-methodology contradiction was found.** No new methodology rule should be added from this pass.
- **POI Failure provenance:** closed/canonicalized. `POI_FAILURE` consumes canonical CHoCH/control-shift state rather than a raw zone breach.
- **Rejection Block / Engineering Liquidity:** closed/canonicalized. Engineering Liquidity is derived only from the valid pullback immediately preceding active Extreme OF/Extreme OB; RB remains a separate PD-array concept.
- **Reversal predicates:** closed at the current boundary. Exact OHLC predicates are explicitly project-derived deterministic formalizations; qualitative morphology remains non-binary.
- **Premium/discount gate:** semantically canonicalized. Any residual issue is source-traceability/provenance, not a missing semantic gate.
- **Target selection/use:** implementation scope, not canonical SMC methodology. Chart analysis supplies the structural/liquidity levels that can serve as target inputs.
- **LTF target selection priority:** implementation/trading-policy decision; not a canonical gap.
- **Universal countertrend target coordinate:** implementation/trading-policy decision; not a canonical gap.
- **Fixed-R target:** implementation/trading-policy decision; not canonical SMC methodology.
- **BE / profit-lock / trailing:** downstream trade-management implementation; not canonical target semantics.
- **Target Plan / multi-leg management:** implementation architecture; leg count/allocation is configurable and not methodology.

### Runtime / platform gaps
- `smc_analyzer.py` remains materially incomplete versus the canonical structural engine and still contains legacy `SWING_CANDIDATE` representation that must eventually be synchronized with the canonical lifecycle.
- Platform-specific broker/exchange integration, venue constraints, order-type behavior, pending-order lifecycle, fills/slippage, reconciliation, and executable backtest simulation remain implementation work under `platform_execution.md`.

### Audit disposition
**AUDIT PART 2 = SUPERSEDED.** The previous completion disposition was invalidated by the direct validator re-audit recorded below. Target-choice/trade-management scope remains implementation work, but the canonical documentation required the eight-item correction pass documented below.


## DIRECT VALIDATOR RE-AUDIT — EIGHT-ITEM CANONICAL CORRECTION PASS — 2026-09-25

The previous AUDIT PART 2 = COMPLETE disposition is superseded. A direct validator audit against the indexed knowledgebase evidence found eight remaining documentation issues. The canonical skill was corrected without modifying runtime implementation.

### Eight-item disposition

1. **Layer-2 / Layer-3 IDM ordering — CLOSED / CANONICALIZED**
   - Layer 2 now ends the initial pullback path at Verified Pullback Extreme and Pullback-Derived Liquidity Reference.
   - Layer 3 consumes that reference for IDM classification.
   - Structural Retracement Qualification is later, after CONFIRMED_STRUCTURAL_SWING, as a continuation-BOS gate.

2. **Premium/Discount hard gate — CLOSED / CANONICALIZED**
   - BUY → DISCOUNT.
   - SELL → PREMIUM.
   - This remains a hard execution eligibility gate, not a score/preference.
   - Existing canonical normalized-location wording was retained because it already uses the canonical dealing-range model; no fallback rule was introduced.

3. **OB/FVG validation — CLOSED / CANONICALIZED**
   - Pillar 3 now requires an associated FVG/imbalance that exists and has not been completely filled/consumed.
   - Completely untouched/unmitigated FVG status is not required.
   - Standalone FVG remains non-POI and non-entry.

4. **OB → next FVG candle shift — CLOSED / CANONICALIZED**
   - A candidate OB candle lacking the required FVG association is rejected.
   - Selection shifts to the next eligible candle in the relevant source-defined sequence.
   - FVG association is evaluated again.
   - The selected candle must independently satisfy all OB validation pillars.

5. **Extreme OB lineage — CLOSED / CANONICALIZED**
   - Extreme OF is resolved first.
   - Extreme OB is the furthest unmitigated valid OB inside the active Extreme OF lineage.
   - Global origin-side OB search is not canonical.
   - Origin OB remains a separate latent reserve.

6. **1-candle reduced retracement — CLOSED / VERIFIED**
   - Positive reduced-retracement qualification requires exactly two candles.
   - One-candle Layer-2 Candle-Level Valid Pullback remains valid.
   - No global one-candle prohibition exists.

7. **Rule-of-Two minimum-one — CLOSED / CANONICALIZED**
   - In an applicable Rule-of-Two dealing-range execution context, active canonical tradable POIs have cardinality 1..2.
   - No valid POI means fail-closed NO_EVIDENCE / no executable POI.
   - No synthetic POI is created.
   - Decisional and Extreme remain the canonical active roles.
   - Origin OB is latent; Rejection Block is separately typed.

8. **IMPULSE_EXTENSION — CLOSED / VERIFIED**
   - IMPULSE_EXTENSION remains a classification outcome of EXT_CONT_BREAK when continuation-BOS qualification is insufficient.
   - It is not an eighth event class.

### Canonical lifecycle verified

Candle-Level Valid Pullback
→ Verified Pullback Extreme
→ Pullback-Derived Liquidity Reference
→ IDM
→ IDM_TAKEN
→ CONFIRMED_STRUCTURAL_SWING
→ Structural Retracement Qualification
→ Structural Swing Break
→ VALID_BOS

### Files changed in this correction pass

- .agents/skills/smc/02_minor_structure.md
- .agents/skills/smc/03_structural_semantic_authority.md
- .agents/skills/smc/06_execution.md
- .agents/skills/smc/08_implementation.md
- .agents/skills/smc/source_reconciliation.md
- .agents/skills/smc/reconciliation/full_methodology_gap_audit.md
- AGENT_REVIEW.md

04_BOS_mechanics.md required no edit after verification.

### Stale-wording search

Post-edit search across the canonical skill confirmed:

- no fully unmitigated FVG;
- no fully unmitigated imbalance;
- no furthest valid origin-side OB;
- no stale zero, one, or two Rule-of-Two formulation;
- no canonical use of IMPULSE_EXTENSION as an event class;
- no Layer-2 requirement that structural retracement qualification precede the initial IDM reference;
- one-candle occurrences are confined to the valid Layer-2 pullback boundary; no one-candle positive reduced-retracement rule remains;
- remaining STRUCTURALLY VALID PULLBACK occurrences are post-BOS/Layer-3 lifecycle uses and do not reintroduce the initial IDM prerequisite;
- Extreme OB references are lineage-qualified.

### Knowledgebase evidence used

- knowledgebase/00_INDEX.md
- knowledgebase/03_SOURCE_EVIDENCE.md
- knowledgebase/reference/03_pullback_retracement.md
- knowledgebase/reference/06_poi_ob_fvg_rejection.md

The knowledgebase was used only as source evidence. .agents/skills/smc/ remains canonical authority.

### Runtime / data integrity

Confirmed untouched:

- smc_analyzer.py
- smc_htf_ltf_monitor.py
- zones.json
- knowledgebase/

This was a canonical-documentation-only correction pass.

### Last substantive documentation commit before this ledger update

e0593a49f0d6799422b0516408649ff83c1d31af

### Remaining genuine source gaps

No unresolved contradiction from the eight-item validator set remains. Exact boundaries that are not deterministically specified by the underlying source remain under-specified implementation/documentation boundaries and were not converted into invented numeric rules.

### Final disposition

The eight-item correction set is CLOSED / CANONICALIZED or CLOSED / VERIFIED as listed above. The prior AUDIT PART 2 completion statement is superseded by this evidence-backed correction record.

## DIRECT VALIDATOR RE-AUDIT — MAJOR IDM CONTINUITY CORRECTION — 2026-09-25

The previous fallback-IDM finding was re-audited against the primary knowledgebase sources after the explicit clarification that, after BOS, a post-BOS sequence may create only Minor IDM. In that case the previous Protected Low (bullish) or Protected High (bearish) remains the Major IDM reference.

### Source-backed finding

The following source evidence was rechecked:
- `knowledgebase/sources/truesmc2026.txt`
- `knowledgebase/sources/market_structure_mapping_update.txt`
- `knowledgebase/sources/major_minor_inducement.txt`
- `knowledgebase/sources/true_smc123.txt`

The sources explicitly support the external-boundary Major IDM case when a range contains a Minor IDM but no separately formed Major IDM. They also support shifting the Major IDM when a newer valid Major-Inducement pullback is formed.

### Canonical correction

The previous `FALLBACK_MAJOR_IDM` / `REAL_MAJOR_IDM` distinction was too elaborate and incorrectly promoted a project-composed lifecycle representation into a separate ontology.

Canonical rule now:

```text
VALID_BOS
    ↓
POST-BOS PRICE ACTION
    ├─ NEW MAJOR IDM QUALIFIED
    │      ↓
    │   NEW MAJOR IDM becomes active
    │
    └─ MINOR IDM ONLY / NO NEW MAJOR IDM
           ↓
    PREVIOUS PROTECTED EXTERNAL BOUNDARY
           ↓
       REMAINS MAJOR IDM
```

Bullish: previous Protected Low remains Major IDM.
Bearish: previous Protected High remains Major IDM.

A new Major IDM supersedes the prior Major IDM only when it independently qualifies. Minor IDM alone does not replace it.

### Files corrected

- `.agents/skills/smc/03_structural_semantic_authority.md`
- `.agents/skills/smc/04_BOS_mechanics.md`
- `.agents/skills/smc/05_CHOCH_mechanics.md`
- `.agents/skills/smc/08_implementation.md`
- `.agents/skills/smc/source_reconciliation.md`
- `.agents/skills/smc/reconciliation/full_methodology_gap_audit.md`

Runtime/data files were not modified:
- `smc_analyzer.py`
- `smc_htf_ltf_monitor.py`
- `zones.json`
- `knowledgebase/`

### Validation status

The obsolete `FALLBACK_MAJOR_IDM` and `REAL_MAJOR_IDM` lifecycle model has been removed from the canonical implementation contract. Remaining occurrences, if any, are only explicit historical/audit wording documenting the correction; they are not active canonical rules or event classes.

**MAJOR IDM CORRECTION STATUS: CLOSED / VERIFIED.** Cross-skill stale-reference verification found no active `FALLBACK_MAJOR_IDM`, `REAL_MAJOR_IDM`, `FALLBACK_EVENT`, or `REAL_MAJOR_IDM_EVENT` implementation rule. Remaining token occurrences are historical audit statements explicitly documenting the removed model.

**OVERALL FULL-SKILL AUDIT STATUS: CLOSED — items 1–7 resolved.** This closure applies only to the Major IDM continuity issue; it does not constitute a claim that the entire skill has no further source-backed discrepancies.


## FULL-SKILL AUDIT — PERSISTENT CORRECTION LEDGER — 2026-09-25

The latest full source-by-source audit produced seven follow-up items. This ledger remains OPEN until every item is either source-backed and corrected or explicitly resolved by user decision. No item may be silently dropped.

### Closed in current correction pass

1. **Stale Major IDM reference in skill index — CLOSED**
   - Removed the obsolete “Fallback Major IDM / Major IDM Sweep distinctions” wording from .agents/skills/smc/skill.md.
   - The index now references the canonical Major IDM / Major IDM Sweep interaction and lifecycle.

2. **Incorrect event-class count — CLOSED**
   - .agents/skills/smc/08_implementation.md now defines six disjoint event classes, matching the actual six-item enumeration.
   - The explanatory diagram and event-detection statement were synchronized to six.

3. **Duplicate MAJOR_IDM_EVENT precedence entry — CLOSED**
   - Removed the duplicated MAJOR_IDM_EVENT entry from event-detection precedence.

4. **Stale “real Major IDM” terminology — CLOSED**
   - Replaced the obsolete wording with the single canonical Major IDM semantic class plus explicit provenance.

5. **Stale “fallback provenance” terminology — CLOSED**
   - Replaced it with traceable Major IDM provenance and explicitly removed the notion of a separate fallback Major IDM ontology/provenance class.

### CLOSED — user decisions reconciled and re-audited

6. **LTF-CHoCH trigger / Structural Glitch — CLOSED / VERIFIED**
   - The prior universal completed-LTF-close rule is withdrawn.
   - The 2026 source explicitly defines the post-HTF-interaction LTF **Structural Glitch**: the most recently formed valid LTF pullback/inducement becomes the operative CHoCH reference instead of the ordinary LTF external boundary.
   - Break confirmation remains IDM-dependent. A Major-Inducement LTF path may use the canonical wick-break CHoCH route. When only Minor IDM exists, the external protected boundary functions as Major IDM; a wick is `MAJOR_IDM_SWEEP`, and CHoCH requires a completed body close beyond the applicable LTF reference.
   - Therefore `completed LTF candle CLOSE` is not a universal condition and the term/concept `LTF Structural Glitch` remains canonical.

7. **Reduced-candle extreme-taking threshold — CLOSED / VERIFIED**
   - The canonical project decision remains `>= 5` prior extremes.
   - The earlier source-wording ambiguity was explicitly resolved by user decision and is not reopened by this CHoCH correction.

### Rule for continuation

Items 6–7 are now closed after source reconciliation. Future audits must preserve the IDM-dependent LTF CHoCH rule and must not reintroduce a universal LTF body-close requirement.


## FOLLOW-UP — FINAL AUDIT CORRECTION — 2026-09-25

The full-skill audit identified exactly two stale wording defects in `.agents/skills/smc/04_BOS_mechanics.md`. Only those audited defects were corrected:

1. Replaced the obsolete “Major IDM is a proxy” wording with the canonical single Major IDM semantic class plus provenance.
2. Replaced the obsolete “Real IDM lifecycle” wording with the canonical post-BOS Major IDM qualification/supersession lifecycle.

No other skill, knowledgebase, runtime Python file, or analyzed JSON was modified in this correction. Post-edit stale-term validation found no active `REAL_IDM`, `REAL_MAJOR_IDM`, `FALLBACK_MAJOR_IDM`, or proxy-Major-IDM wording in `04_BOS_mechanics.md`.

**FINAL AUDIT CORRECTION: CLOSED / VERIFIED.**
 
## LATEST DIRECT VALIDATOR CORRECTION — LTF STRUCTURAL GLITCH + IDM-DEPENDENT CHoCH — 2026-09-25

The previous canonical LTF body-close-only rule is superseded by the source-reconciled fractal CHoCH model.

### Source-backed correction

`knowledgebase/sources/truesmc2026.txt` Part 5 explicitly describes the LTF **small glitch in the structure cycle** after HTF POI/core-liquidity interaction. The source states that the CHoCH reference can be the most recently formed valid LTF pullback/inducement rather than the ordinary LTF external boundary.

The same source set also documents the Major-Inducement CHoCH distinction: when the trading range involves a Major IDM, the external break may be by wick or body; when the external boundary functions as Major IDM because only Minor IDM exists, a wick is a sweep and body confirmation is required.

### Canonical rule

```text
HTF POI / CORE-LIQUIDITY INTERACTION
        ↓
LTF STRUCTURAL GLITCH
        ↓
MOST RECENT VALID LTF PULLBACK / IDM
        ↓
IDM-TYPE BREAK MODE
   ├─ MAJOR IDM → wick path may confirm CHoCH
   └─ MINOR IDM ONLY → body close required
```

The LTF route remains the ordinary CHoCH concept applied fractally in an HTF→LTF execution context. The Structural Glitch changes the governing reference; it does not create a new lifecycle state.

### Documentation/consistency corrections included in this pass

- `.agents/skills/smc/05_CHOCH_mechanics.md`: removed universal LTF body-close requirement; restored canonical Structural Glitch terminology and IDM-dependent validation.
- `.agents/skills/smc/08_implementation.md`: execution contract now resolves LTF CHoCH wick/body mode from IDM classification.
- `.agents/skills/smc/source_reconciliation.md`: C6 now records the source-direct Structural Glitch and the reconciled IDM-dependent break rule.
- `.agents/skills/smc/reconciliation/full_methodology_gap_audit.md`: stale close-only canonicalization replaced with the reconciled rule.
- `.agents/skills/smc/04_BOS_mechanics.md`: removed the stale claim that equality at the broken level is itself a valid break.
- `.agents/skills/smc/countertrend_scenarios.md`: removed the stale open-specification-gap wording for countertrend target-coordinate resolution; it remains downstream implementation/trading-policy scope.

Runtime and knowledgebase integrity:
- `smc_analyzer.py` untouched.
- `smc_htf_ltf_monitor.py` untouched.
- `zones.json` untouched.
- `knowledgebase/` untouched.

**LATEST CHoCH / CONSISTENCY CORRECTION: IMPLEMENTED; FINAL VALIDATION PASSED.**

 
### Final validation — 2026-09-25

Validation completed after the six canonical-document updates plus this review record:
- no stale universal LTF body-close formulation remains in the affected canonical documents;
- LTF Structural Glitch terminology and reference-substitution rule are present;
- LTF CHoCH break mode is explicitly IDM-type dependent;
- the 04_BOS equality wording now requires physical penetration beyond the level;
- countertrend target coordinate resolution is no longer described as an unresolved methodology gap;
- runtime Python, analyzed JSON, and knowledgebase files remain untouched.

FINAL VALIDATION STATUS: PASS.


## LATEST DIRECT VALIDATOR CORRECTION — DISPLACEMENT OUTLIER + POI RANGE EXPIRATION — 2026-09-25

The latest source-precedence audit identified and corrected two canonical documentation gaps plus one implementation consistency defect.

### Canonical corrections

1. **Impulsive-leg scope** is explicit in Layers 1–3: structural mapping, IDM identification and POI-relevant structural context follow the active impulsive leg; corrective-leg internal complexity is not independently promoted.
2. **One-candle displacement outlier** is canonical as an explicit exception to the normal >=2 opposing-candle qualification gate. One exceptional candle may qualify when it takes >=5 preceding bodies/extremes and satisfies the required retracement depth and all other structural gates.
3. **POI range expiration** is owned by Layer 6: when a new VALID_BOS establishes a new Dealing Range, all unmitigated POIs originating from the previous range leave the active tradable set and become historical/reaction-only. Layer 8 consumes this lifecycle state.
4. **08 implementation equality defect** is corrected: equality at the broken level is not physical penetration and therefore is not Wick-BOS.
5. **Policy boundary preserved:** 0.5% risk and break-even restrictions remain trading-policy controls, not structural methodology rules.

### Validation scope

Canonical chapters rechecked: 01, 02, 03, 04, 05, 06, 07, 08, methodology_parameters, trading_policy, countertrend_scenarios, source_reconciliation and the persistent audit ledger.

Runtime Python, analyzed JSON and knowledgebase source files remain untouched.

**LATEST SOURCE-PRECEDENCE CORRECTION: IMPLEMENTED; FINAL VALIDATION PASSED.**


## LAYER 1 IMPLEMENTATION — 2026-09-26

### Audit disposition

The canonical Layer 1 boundary was re-audited before implementation.

**Layer 1 owns only:**
- validated OHLC candle primitives;
- deterministic physical/wick/body/close breach relations;
- exact equality relations;
- strict Inside Bar geometry and mother-candle identity;
- Outside Bar geometry;
- independent high/low reference identity transfer;
- candle-internal sequence observability;
- candle-level directional observation;
- immutable, content-addressed evidence and fail-closed validation.

**Layer 1 explicitly does not own:**
- Pullback formation;
- IDM classification/lifecycle;
- structural swing qualification;
- BOS;
- CHoCH;
- POI/OB/FVG;
- risk/target/trade management;
- Trading Range or higher-layer lifecycle semantics.

This matches the canonical ownership chain in `.agents/skills/smc/01_micro_structure.md` and `02_minor_structure.md`: Layer 1 emits candle observations; Layer 2 assembles them into sequential/minor structure.

### Implementation

Implemented on `main` without a feature branch:

- `microstructure_engine.py`
- `tests/test_microstructure_engine.py`

The implementation provides:
- strict finite `Decimal` normalization; native float inputs are rejected;
- equality as a non-break condition;
- deterministic breach classification without inferring intrabar traversal;
- strict Inside Bar and Outside Bar geometry;
- Outside Bar sequence evidence defaulting to `UNAVAILABLE` when aggregate OHLC cannot expose the path;
- exact EQH/EQL comparison;
- independent high/low reference transfer;
- source-candle provenance on breach/reference evidence;
- deeply immutable dataclass/tuple evidence objects;
- deterministic SHA-256 content identity;
- fail-closed quarantine via `QuarantineError`;
- positive AST import allowlist plus downstream-vocabulary isolation test.

### Validation

Local validation completed successfully:

```
12 passed in 0.05s
```

The test suite covers numeric integrity, equality semantics, breach taxonomy, Inside/Outside Bar behavior, unavailable sequence evidence, provenance, independent reference transfer, exact EQH/EQL, immutability, deterministic evidence IDs, quarantine behavior, candle-level trend, and AST isolation.

### Integration boundary

No existing runtime integration was performed.

Untouched:
- `smc_analyzer.py`
- `smc_htf_ltf_monitor.py`
- `zones.json`
- `knowledgebase/`
- canonical skill documents

Layer 1 is implemented as an independently reviewable component. Mapper integration remains a later phase after approval.

### Audit conclusion

**LAYER 1 IMPLEMENTATION STATUS: READY FOR REVIEW**

The implementation intentionally does not implement pullbacks or any Layer 2+ semantic object. No branch was created; the changes are committed directly to `main`.


## LAYER IMPLEMENTATION TRACK — 2026-09-26

### Layer 1 audit disposition

Layer 1 `microstructure_engine.py` was re-audited against `.agents/skills/smc/01_micro_structure.md` and the previously frozen technical contract.

A concrete Contract issue was found and corrected: aggregate-OHLC Outside Bar construction can no longer accept injected/observed intrabar ordering. `outside_bar()` now deterministically emits `SequenceStatus.UNAVAILABLE`, and `OutsideBarObservation` rejects any non-UNAVAILABLE sequence. A regression test was added.

Layer 1 remains hermetically isolated and continues to own only OHLC primitives. No Mapper/analyzer/monitor integration was performed.

### Layer 2 implementation

Implemented on `main` as `minor_structure_engine.py` with `tests/test_minor_structure_engine.py`.

Layer 2 owns only:
- Candle-Level Valid Pullback formation;
- Verified Pullback Extreme;
- Pullback-Derived Liquidity Reference;
- Active Pullback Pointer.

Layer 2 consumes Layer 1 breach and candle-trend semantics and does not implement IDM, BOS, CHoCH, POI, or structural retracement.

Aggregate-OHLC Outside Bars with unavailable intrabar order cannot independently confirm a same-candle takeout/completion sequence; the engine therefore fails closed and waits for a later observable completion.

### Integration boundary

`smc_analyzer.py`, `smc_htf_ltf_monitor.py`, and `zones.json` remain untouched. Layer implementations are being built and reviewed independently first. Mapper integration is deferred until the relevant layer is explicitly approved.

### Current status

Layer 1: **AUDIT CORRECTED — READY FOR FINAL REVIEW**.

Layer 2: **IMPLEMENTED — READY FOR REVIEW**. Runtime test execution must be confirmed before formal approval.

### Commits

- 20ea91c — Layer 1 Outside Bar observability contract correction
- 5066e0a — Layer 1 Outside Bar regression test
- 4b6a56b — Layer 2 minor-structure engine initial implementation
- 94cc456 — Layer 2 pullback tests
- 077a0e5 — Layer 2 consumes Layer 1 breach semantics
- 2ac7d5b — Layer 2 boundary test correction
- 474dca1 — Layer 2 syntax/state cleanup
- dbabcde — Layer 2 generated-newline correction
- 34c5467 — Layer 2 consumes Layer 1 candle-trend semantics


## LAYER 2 DIRECT AUDIT CORRECTION — 2026-09-26

### Finding

Layer 2 was audited against .agents/skills/smc/01_micro_structure.md and .agents/skills/smc/02_minor_structure.md.

A concrete observability defect was found: the initial implementation blocked an aggregate-OHLC Outside Bar only when it attempted to start the pullback, but could still accept a later Outside Bar as the completion candle. That would infer the required takeout → reversal → completion order from unavailable intrabar evidence.

### Correction

minor_structure_engine.py now consumes the Layer 1 outside_bar() observation and explicitly checks SequenceStatus.UNAVAILABLE.

For both bullish and bearish pullbacks:
- an ambiguous Outside Bar cannot independently start a same-candle takeout/completion sequence;
- an ambiguous Outside Bar cannot independently complete an already-open pullback;
- the candidate remains open and the engine waits for a later candle whose required completion relation is observable from the available OHLC evidence;
- no synthetic intrabar order is created.

### Regression coverage

tests/test_minor_structure_engine.py now includes:
- same-candle Outside Bar rejection;
- later Outside Bar completion rejection;
- successful completion after an ambiguous Outside Bar when a subsequent observable candle provides the completion.

### Current commits

- 04c7316b — Layer 2 fail-closed Outside Bar completion correction
- 2969f803 — Layer 2 regression tests for unavailable completion
- 9ca87ffe — Layer 2 consumes explicit Layer 1 SequenceStatus.UNAVAILABLE

### Validation limitation

No GitHub Actions workflow is configured for the correction commits, and this environment cannot execute the repository checkout remotely. Therefore the new test suite has been statically reviewed but runtime PASS has not yet been independently confirmed.

### Status

Layer 2 remains IMPLEMENTED — READY FOR REVIEW, but NOT APPROVED until runtime tests are executed successfully and the remaining Layer 2 semantic audit is closed.

Mapper/analyzer/monitor integration remains forbidden at this stage.


## LAYER 2 DIRECT AUDIT + CORRECTION — 2026-09-26

### Audit finding
The initial Layer 2 implementation was semantically too permissive in three areas:
1. it selected pullback references by scanning arbitrary candle/reference pairs instead of maintaining the canonical previous bullish/bearish reference sequence;
2. it could silently discard an unresolved Outside Bar intrabar-order dependency;
3. it did not expose the distinction between no pullback and a pullback candidate whose required sequence evidence is unavailable.

### Corrections implemented on main
- `minor_structure_engine.py` now uses a stateful Layer-2 reference/pullback sequence.
- Pullback formation requires:
  - an applicable previous bullish/bearish reference candle;
  - reference-extreme takeout;
  - the same reference extreme to be broken after pullback initiation;
  - equality/touch is never treated as break.
- Inside Bars remain governed by the mother-candle reference and do not become independent pullback references.
- Aggregate-OHLC Outside Bar ordering remains `UNAVAILABLE`; no LOW_FIRST/HIGH_FIRST path is fabricated.
- New explicit implementation state:
  - `NONE`
  - `CONFIRMED`
  - `PENDING_UNAVAILABLE_SEQUENCE`
- `PendingPullback` preserves the reference/start provenance when sequence ordering cannot be established.
- A later independently observable completion may resolve the pending candidate.
- Verified pullback extreme provenance remains tied to the exact candle creating the extreme.
- Layer 2 remains hermetically downstream of Layer 1 and does not define IDM/BOS/CHoCH/POI.

### Canonical documentation synchronized
- `.agents/skills/smc/02_minor_structure.md`
- `.agents/skills/smc/08_implementation.md`

The stale implementation rule treating inside-bar breaks as independent pullbacks was replaced with mother-candle reference semantics.

### Tests
- `tests/test_minor_structure_engine.py` expanded with explicit unavailable-sequence, pending-resolution, state-reference, and no-event coverage.
- Current Layer-2 test file contains 11 test functions.
- Runtime test execution could not be run from the validator environment because external GitHub network access is unavailable. The repository code and fixtures were therefore statically reconciled; no claim of executed PASS is made here.

### Scope
- `smc_analyzer.py`, `smc_htf_ltf_monitor.py`, `zones.json`, and `knowledgebase/` remain untouched.
- No mapper integration was performed.
- No branch was created; all Layer-2 corrections were committed directly to `main`.

### Commits
- `ac4e5f4` — Layer-2 pullback state machine and unavailable-sequence handling
- `525121f` — Layer-2 regression tests
- `7287a63` — Layer-2 canonical documentation pending contract
- `cc89340` — implementation-contract synchronization
- `a256022` — continuation-reference semantic tightening
- `205f551` — unavailable-sequence test assertions
- `2ec6ff8` — strict-reference test fixture corrections

### Final code inspection
The final Layer-2 source was re-read after the corrections; the state machine, explicit pending resolution, strict reference break semantics, and downstream boundary are internally consistent. The obsolete pending-flag assignment was removed in the final cleanup commit.


- `adc1dfafb58f86104b21281bfba24d5b0b58d01c` — removed obsolete internal Layer-2 pending-flag assignment after final code inspection.

### Status
**LAYER 2 = CORRECTED / READY FOR FINAL TEST EXECUTION AND VALIDATOR REVIEW.**

Integration into SMC Mapper remains blocked until Layer 2 receives explicit approval.


## LAYER 2 AUDIT — 2026-09-26

### Audit result
Layer 2 was re-audited against:
- .agents/skills/smc/01_micro_structure.md
- .agents/skills/smc/02_minor_structure.md
- .agents/skills/smc/08_implementation.md
- knowledgebase/reference/03_pullback_retracement.md
- knowledgebase/03_SOURCE_EVIDENCE.md
- primary valid-pullback / market-structure source evidence

### Findings and corrections
1. **EQH/EQL reference transfer gap — CORRECTED**
   - The implementation previously failed to consume Layer-1 Equal Extreme Reference Transfer when a later candle shared the active high/low.
   - Layer 2 now consumes Layer-1 equality observations before evaluating pullback takeout, so the later equal-extreme candle becomes the applicable reference.
   - This preserves the canonical source rule that the second candle becomes the active reference in the equal-high/equal-low case.
2. **Stale broken reference reuse — CORRECTED**
   - After a pullback completes, a non-directional completion candle cannot leave the already-broken reference active.
   - Layer 2 now clears that reference and waits for a new Layer-1 directional continuation/equal-extreme reference.
3. **Outside Bar / UNAVAILABLE — VERIFIED**
   - Aggregate-OHLC Outside Bars remain UNAVAILABLE.
   - Layer 2 does not reinterpret UNAVAILABLE as observed ordering.
   - An unresolved candidate remains explicitly pending and may only resolve on later independently observable evidence.

### Canonical boundary
Layer 2 remains limited to:
- Candle-Level Valid Pullback
- Verified Pullback Extreme
- Pullback-Derived Liquidity Reference
- Active Pullback Pointer
- explicit pending-unavailable state

Layer 2 does not implement IDM, BOS, CHoCH, POI, structural retracement, RR, or trade management.

### Tests / validation
- Regression coverage added for EQH reference transfer, EQL reference transfer, and stale-reference reuse.
- Runtime execution could not be independently performed from the validator environment because repository checkout/network execution is unavailable.
- Therefore no runtime PASS claim is made.

### Integration
Untouched:
- smc_analyzer.py
- smc_htf_ltf_monitor.py
- zones.json
- knowledgebase/

No branch was created. All corrections were committed directly to main.

### Current status
**LAYER 2 = AUDIT-CORRECTED / READY FOR RUNTIME TEST EXECUTION AND FINAL APPROVAL.**

Commits:
- 5dc4b12 — Layer-2 equal-extreme reference transfer and stale-reference lifecycle correction
- 5498edd — Layer-2 regression tests
- 016acbf — Layer-2 EQH/EQL fixture correction
- 6909e89 — Layer-2 canonical documentation synchronization


### Final edge-case correction — 2026-09-26
A final Layer-2 audit pass identified one same-candle boundary condition in EQH/EQL transfer:
- the candle that receives the new Layer-1 high/low reference cannot simultaneously be treated as taking its own newly established reference extreme;
- pullback takeout evaluation therefore begins on the following candle.

Implemented and regression-tested for both bullish EQH and bearish EQL paths.

Additional commits:
- 34644bf — same-candle self-takeout prevention in Layer 2
- d67d5ac — EQH/EQL same-candle regression tests
- 88e60d5 — canonical Layer-2 documentation synchronization


## LAYER 2 SEMANTIC-OWNER CORRECTION — 2026-09-26

### Audit finding
A final Layer-2 implementation audit found one architecture-level inconsistency: the engine claimed to consume Layer-1 breach/candle-trend semantics, but its continuation, takeout, and completion predicates still duplicated raw OHLC comparisons locally.

### Correction
`minor_structure_engine.py` now delegates:
- directional continuation detection to Layer-1 `candle_trend()`;
- reference-high/reference-low breach detection to Layer-1 `classify_breach()`;
- equality/break semantics therefore remain owned exclusively by `microstructure_engine.py`.

Layer 2 still owns the sequential state machine, pullback window, verified extreme, liquidity-reference derivation, and unavailable-sequence pending state. It does not redefine Layer-1 geometry.

### Validation boundary
- `microstructure_engine.py` unchanged.
- `minor_structure_engine.py` corrected on `main`.
- `smc_analyzer.py`, `smc_htf_ltf_monitor.py`, `zones.json`, and `knowledgebase/` remain untouched.
- No Mapper integration performed.
- Runtime execution remains unavailable in this validator environment because repository checkout/network access is unavailable.

### Commit
- `017296f` — Layer-2 consume Layer-1 breach and trend semantics

### Status
**LAYER 2 = SEMANTICALLY CORRECTED / READY FOR RUNTIME TEST EXECUTION AND FINAL APPROVAL.**

Formal Layer-2 approval remains blocked until the repository test suite is actually executed successfully.

## LAYER 2 FINAL AUDIT CORRECTION — 2026-09-26

### Finding
A final semantic audit identified a state-reporting defect in MinorStructureAnalysis.resolution: when historical completed pullbacks existed alongside a newer unresolved PENDING_UNAVAILABLE_SEQUENCE candidate, the property returned CONFIRMED because historical completion was checked first.

### Correction
resolution now gives precedence to the latest unresolved pending state:
- PENDING_UNAVAILABLE_SEQUENCE when an unresolved pending candidate exists;
- otherwise CONFIRMED when completed pullbacks exist;
- otherwise NONE.

This does not alter historical pullback records or the active completed-pullback pointer. It only makes the aggregate resolution state reflect the unresolved current condition.

### Regression
Added test_pending_latest_state_overrides_historical_confirmation() covering:
- one previously confirmed pullback;
- a later Outside Bar with unavailable intrabar sequence;
- preserved historical active pullback;
- explicit pending resolution taking precedence.

### Scope
- minor_structure_engine.py corrected.
- tests/test_minor_structure_engine.py updated.
- microstructure_engine.py unchanged.
- smc_analyzer.py, smc_htf_ltf_monitor.py, zones.json, and knowledgebase/ untouched.
- No Mapper integration performed.
- No branch created; changes committed directly to main.

### Validation boundary
The validator environment cannot execute the repository checkout/test suite because repository runtime/network execution is unavailable. Therefore this correction is statically audited and regression-covered, but no runtime PASS claim is made until the repository test suite is executed in an environment with the checkout available.

### Commits
- 28d35a6 — Fix Layer-2 pending resolution precedence
- 09293b6 — Add Layer-2 pending-resolution regression

### Current status
**LAYER 2 = AUDIT-CORRECTED / READY FOR RUNTIME TEST EXECUTION AND FINAL APPROVAL.**


## TEST EXECUTION POLICY — 2026-09-26

The repository now has a persistent GitHub Actions test gate:

- Workflow: `.github/workflows/tests.yml`
- Trigger: every push to `main`
- Manual trigger: `workflow_dispatch`
- Python: 3.11
- Test command: `python -m pytest -q`
- Scope: full repository test suite, not only the active layer.

This test policy remains active until explicitly revoked by the user.

Current independently implemented layer coverage:
- Layer 1: `tests/test_microstructure_engine.py` — 12 test functions.
- Layer 2: `tests/test_minor_structure_engine.py` — 18 test functions.
- Current known total: 30 test functions.

Approval rule:
- A layer is not formally APPROVED merely because tests are present.
- The relevant GitHub Actions runtime result must be successful, together with the semantic audit.
- If the workflow fails, the failing implementation/tests must be corrected and the suite rerun before approval.
- Mapper/analyzer/monitor integration remains blocked until the applicable layer is explicitly approved.

No feature branch is used; layer implementations continue directly on `main` as requested.


## LAYER 3 IMPLEMENTATION — 2026-09-26

Implemented directly on `main` (no feature branch, per user decision):
- `structural_engine.py`
- `tests/test_structural_engine.py`

Scope:
- Layer 2 `MinorStructureAnalysis` is the only minor-structure input contract.
- IDM is owned/classified in Layer 3.
- IDM takeout consumes Layer 1 physical breach semantics; equality/touch is not takeout.
- IDM takeout confirms `CONFIRMED_STRUCTURAL_SWING`; it does not create BOS.
- Structural retracement qualification is separate and precedes any downstream BOS consumer.
- 50% standard gate, 38.2%-<50% explicit HTF evidence gate, and below-38.2% rejection are implemented.
- Normal >=3 opposing-candle path and source-defined reduced/outlier exception are separated.
- Layer 3 does not implement BOS, CHoCH, POI, RR, mapper integration, or target management.
- Missing dealing-range boundaries prevent retracement qualification rather than being inferred.

Current review state: **LAYER 3 IMPLEMENTED / RUNTIME TEST GATE PENDING / NOT APPROVED**.
The persistent GitHub Actions policy in `.github/workflows/tests.yml` remains the required runtime approval gate.


## LAYER 3 VALIDATOR AUDIT — 2026-09-26

### Verification
- Current main includes Layer 3 implementation and the latest Layer-2 fixture corrections through commit 74bf30b1edb743324ba6cdf8a7ec69e1176f38c2.
- No feature branch was used.
- Canonical authority checked: .agents/skills/smc/03_structural_semantic_authority.md and .agents/skills/smc/04_BOS_mechanics.md.
- Knowledgebase evidence checked: knowledgebase/sources/truesmc2026.txt, knowledgebase/sources/market_structure_mapping_update.txt, knowledgebase/sources/major_minor_inducement.txt, and knowledgebase/reference/03_pullback_retracement.md.

### Finding — BLOCKER
The current Layer-3 API exposes `post_bos_pullback_ids` as a caller-supplied authority for MAJOR_IDM classification. This violates the semantic-owner rule: Layer 3 owns IDM classification/lifecycle and must not accept an arbitrary external set that directly decides which pullback is Major IDM.

The canonical lifecycle requires:
- after VALID_BOS, a qualifying post-BOS valid pullback can establish the active MAJOR_IDM;
- if only Minor IDM exists and no new Major IDM qualifies, the prior protected external boundary remains the active MAJOR_IDM;
- a newer qualifying Major IDM supersedes the prior one;
- no fallback/real/proxy IDM ontology is introduced.

The current implementation does not model that lifecycle autonomously and therefore cannot yet be approved as the complete Layer-3 IDM owner. The issue must be corrected in the Layer-3 contract/engine before Layer-3 approval.

### Test status
The persistent GitHub Actions gate remains configured in .github/workflows/tests.yml and runs `python -m pytest -q` on pushes to main. The validator environment cannot directly execute a repository checkout, and the GitHub connector currently exposes no push-triggered run listing for this repository, so no runtime PASS claim is made here.

### Disposition
**LAYER 3 = NOT APPROVED / CORRECTION REQUIRED.**
Layer 2 remains audit-corrected and pending runtime PASS plus final approval. Mapper/analyzer integration remains blocked.


## LAYER 3 IDM LIFECYCLE CORRECTION — 2026-09-26

### Audit finding
The validator identified a blocker in the initial Layer-3 implementation: `classify_idm()` accepted caller-supplied `post_bos_pullback_ids`, allowing an arbitrary external set to directly select which pullback became Major IDM. This violated Layer-3 semantic ownership.

### Correction implemented directly on main
- Removed `post_bos_pullback_ids` from the Layer-3 API.
- Added Layer-3-owned `IDMLifecycleContext` and explicit `ProtectedExternalBoundary` representation.
- Added explicit IDM origin typing: pullback-derived vs protected-external-boundary.
- Before VALID_BOS, pullback-derived IDM remains Minor IDM.
- After an explicit VALID_BOS lifecycle transition, the newest qualifying Layer-2 pullback becomes Major IDM without caller-selected IDs.
- If no new post-BOS pullback exists, the previous Major IDM remains active; if none exists, the protected external boundary becomes Major IDM.
- No fallback/real/proxy IDM ontology was introduced.
- IDM takeout continues to consume Layer-1 breach semantics; Layer 3 still does not implement BOS/CHoCH/POI/RR.

### Regression tests
Added coverage for:
- rejection of the removed caller-selected Major-IDM mechanism;
- post-BOS newest-pullback Major IDM selection;
- persistence of the previous Major IDM when no new post-BOS pullback exists;
- protected-boundary Major IDM creation when no prior Major IDM exists.

### Commits
- 1431ff1 — Fix Layer-3 IDM semantic ownership and lifecycle
- 075ae61 — Add Layer-3 IDM lifecycle ownership regression tests

### Current status
**LAYER 3 = CORRECTED / READY FOR RUNTIME TEST EXECUTION AND FINAL SEMANTIC AUDIT.**

Runtime PASS is still pending the GitHub Actions test gate. Mapper/analyzer/monitor integration remains blocked until Layer 3 is explicitly approved.


## LAYER 3 POST-BOS IDM FALLBACK PRECISION — 2026-09-26

### Final semantic correction
A follow-up audit found that preserving an arbitrary previous Major IDM object after BOS would still be broader than the canonical rule. The canonical fallback is specifically the **prior protected external boundary** (Protected Low in bullish context / Protected High in bearish context) when no new post-BOS Major IDM qualifies.

### Correction
- Removed previous-Major-IDM fallback from `IDMLifecycleContext`.
- Post-BOS lifecycle now requires explicit protected external boundary provenance.
- New qualifying post-BOS Layer-2 pullback supersedes the boundary as active Major IDM.
- Without a new post-BOS pullback, the protected external boundary is the active Major IDM.
- Missing protected-boundary evidence is fail-closed.

### Commits
- 435876a — Align post-BOS Major IDM fallback with protected boundary
- 84f28a6 — Tighten Layer-3 post-BOS Major IDM regression coverage

### Validation
Static semantic review completed. GitHub Actions is configured to run the full pytest suite on every push to main, but the current GitHub connector exposes no push-triggered run listing for this repository; therefore runtime PASS is not claimed yet.

**Layer 3 remains CORRECTED / READY FOR RUNTIME TEST EXECUTION AND FINAL AUDIT.**


## LAYER 2 OUTSIDE BAR TEMPORAL INVALIDATION CORRECTION — 2026-09-26

### Final audit finding
The previous Layer-2 contract still allowed an Outside Bar with SequenceStatus.UNAVAILABLE to remain a live pending candidate. A later observable candle could therefore complete that historical candidate, which would retroactively infer the missing intrabar order.

This violates:
- Layer-1 observability preservation;
- zero-fabrication;
- fail-closed sequencing;
- temporal causality of historical evidence.

### Correction implemented directly on main
- An unavailable Outside Bar that is required to establish a pullback start is now terminally invalidated.
- An unavailable Outside Bar that is required to complete an open pullback is now terminally invalidated.
- The invalidated candidate is never placed into PENDING_UNAVAILABLE_SEQUENCE.
- start_index is cleared immediately, so no later candle can complete the invalidated candidate.
- A later candle may only begin a new pullback candidate with a new observable start; it cannot supply missing historical intrabar evidence for the old candidate.
- Added InvalidatedPullback and INVALIDATED_UNAVAILABLE_SEQUENCE for explicit provenance and deterministic reporting.

### Regression coverage
Updated tests/test_minor_structure_engine.py to verify:
- same-candle Outside Bar remains invalidated;
- a later Outside Bar cannot complete an already-open candidate;
- a later clean candle cannot revive an Outside Bar candidate whose start sequence was unavailable.

### Scope protection
- microstructure_engine.py unchanged.
- smc_analyzer.py unchanged.
- smc_htf_ltf_monitor.py unchanged.
- zones.json unchanged.
- knowledgebase/ unchanged.
- No Mapper integration.
- No branch created; changes committed directly to main.

### Commits
- 75378ec — Layer-2 Outside Bar temporal invalidation implementation
- 4ae4c95 — Layer-2 regression tests
- 4454067 — Layer-2 canonical documentation synchronization

### Runtime validation
The repository persistent .github/workflows/tests.yml gate is configured to run python -m pytest -q on every push to main. The GitHub connector available to the validator exposes only PR-triggered workflow-run lookup, not push-triggered run listing/dispatch for this repository. Therefore runtime PASS is not claimed until the GitHub Actions result is independently visible.

### Status
**LAYER 2 = CORRECTED / AWAITING RUNTIME TEST RESULT / NOT YET APPROVED.**


## LAYER 2 FINAL OUTSIDE BAR AUDIT — 2026-09-26

### Final correction
The terminal-invalidating Outside Bar model was re-audited after implementation. One reporting inconsistency was found and corrected: InvalidatedPullback existed, but MinorStructureAnalysis.resolution did not reliably propagate the latest invalidated state when historical confirmed pullbacks were also present.

### Final implementation state
- INVALIDATED_UNAVAILABLE_SEQUENCE is now a terminal Layer-2 resolution.
- latest_resolution records the most recent state transition deterministically.
- An unavailable Outside Bar at pullback start invalidates that candidate immediately.
- An unavailable Outside Bar at pullback completion invalidates that candidate immediately.
- start_index is cleared on invalidation.
- Later candles cannot complete or revive that candidate.
- A later observable candle can only form a new candidate from a new observable pullback start.
- PENDING_UNAVAILABLE_SEQUENCE is no longer used for this Outside Bar failure mode.
- Layer-2 documentation and implementation mapping are synchronized.

### Regression coverage
Layer-2 test file now contains 19 test functions, including:
- same-candle Outside Bar invalidation;
- unavailable completion invalidation;
- later-candle non-revival;
- invalidation overriding historical confirmation in aggregate resolution;
- existing EQH/EQL, Inside Bar, equality, provenance, and lifecycle regressions.

### GitHub verification
Latest main HEAD: 0171e3430abfac068903ca431903856e690184b3.

Compared with 84f28a6, the final correction set touches only:
- minor_structure_engine.py
- tests/test_minor_structure_engine.py
- .agents/skills/smc/02_minor_structure.md
- .agents/skills/smc/08_implementation.md
- AGENT_REVIEW.md

No microstructure_engine.py, smc_analyzer.py, smc_htf_ltf_monitor.py, zones.json, or knowledgebase file was changed.

The GitHub connector reports no visible workflow run and no status check for the latest push. Therefore runtime pytest PASS is not claimed.

### Final disposition
**LAYER 2 = AUDIT-CORRECTED / RUNTIME TEST RESULT PENDING / NOT APPROVED.**
Mapper integration remains blocked until the persistent GitHub Actions test gate reports success and the Layer-2 semantic audit is formally closed.


## LAYER 3 AUDIT CORRECTION — 2026-09-26

### Findings
1. **Post-BOS Major IDM promotion was too broad.**
   The previous implementation promoted the newest Layer-2 pullback whenever `after_valid_bos=True`, without proving that the pullback itself formed after the explicit VALID_BOS event.
2. **Standard vs reduced/outlier retracement paths were unnecessarily conflated.**
   The reduced branch could be reached for a two-candle case already covered by the normal gate, weakening the intended gate separation.
3. **VALID_BOS provenance required stronger runtime validation.**
   A post-BOS lifecycle must reference a concrete Layer-1 candle present in the ordered input sequence.

### Corrections
- Added explicit `valid_bos_candle_id` to the Layer-3 lifecycle context.
- Post-BOS Major IDM selection now requires both the pullback start and completion to occur after the VALID_BOS candle.
- If no genuinely post-BOS valid pullback exists, the prior protected external boundary remains the sole active Major IDM.
- Missing VALID_BOS candle provenance or absence from the Layer-1 sequence is fail-closed.
- Standard equilibrium qualification is evaluated first with the normal opposing-candle gate.
- The reduced/outlier path is now a true exception and only bypasses the normal count for the explicit one-candle displacement-outlier case.
- Added regression coverage for pre-BOS pullback non-promotion, genuine post-BOS promotion, missing BOS provenance, and one-candle outlier gating.

### Scope
- `structural_engine.py` only for Layer-3 implementation changes.
- `tests/test_structural_engine.py` updated with regression coverage.
- `microstructure_engine.py`, `minor_structure_engine.py`, `smc_analyzer.py`, `smc_htf_ltf_monitor.py`, `zones.json`, and `knowledgebase/` were not modified by this correction.
- No branch created; all changes were committed directly to `main`.

### Runtime validation
The persistent GitHub Actions test gate remains configured to run `python -m pytest -q` on every push to `main`. The GitHub connector currently reports no status checks for the latest correction commit, so runtime PASS is not claimed.

### Current disposition
**LAYER 3 = AUDIT-CORRECTED / RUNTIME TEST RESULT PENDING / NOT APPROVED.**


## LAYER 3 IMPLEMENTATION CORRECTION — 2026-09-26

### Audit finding
The initial Layer 3 runtime implementation contained two material semantic defects:
1. After VALID_BOS it automatically promoted the newest post-BOS Layer-2 pullback to MAJOR_IDM. This violated the canonical distinction between **NEW MAJOR IDM QUALIFIED** and **MINOR IDM ONLY**.
2. The retracement reduced-candle exception accepted only a one-candle path, while the canonical implementation contract also permits the documented two-candle reduced-displacement exception when its >=5 preceding-body/extreme condition and all other gates are satisfied.

### Correction
- `structural_engine.py` now keeps post-BOS pullbacks as MINOR_IDM unless explicit `MajorIDMQualificationEvidence` positively identifies a qualifying post-BOS pullback.
- Without positive qualification evidence, the prior protected external boundary remains the active MAJOR_IDM.
- Invalid qualification provenance is fail-closed.
- The reduced-candle displacement exception now accepts 1- or 2-candle windows; normal >=2 opposing-candle evidence remains the primary path and is evaluated first.
- No Layer 1 or Layer 2 runtime semantics were modified.
- Mapper integration remains deferred.

### Regression tests
- `tests/test_structural_engine.py` was synchronized with the corrected Major IDM lifecycle.
- Existing GitHub Actions workflow `.github/workflows/tests.yml` runs `python -m pytest -q` on every push to `main` and via manual dispatch.

### Commits
- `ed29213c6e9dcfeeea3547b1828a7ce39a7ca1a1` — Layer 3 implementation correction.
- `a8006206bd29fb4496d8f758abbf09d367483fa9` — Layer 3 regression-test synchronization.

### Current status
**LAYER 3: CORRECTION IMPLEMENTED — TEST EXECUTION PENDING EXTERNAL VALIDATION.**

The semantic audit must be repeated after the test suite reports green. Layer 4/BOS integration remains blocked until Layer 3 is approved.


## LAYER 3 FOLLOW-UP VALIDATION NOTE — 2026-09-26

A second code audit found and corrected a regression-test fixture issue: the reduced-candle tests were not constraining the retracement window to the intended one- or two-candle exception. The fixtures now place the required >=5 preceding candles before the confirmed swing and explicitly bound the evaluation with `attempt_end_candle_id`.

Current implementation commits:
- `ed29213c6e9dcfeeea3547b1828a7ce39a7ca1a1` — Major IDM / reduced-retracement correction.
- `a8006206bd29fb4496d8f758abbf09d367483fa9` — Major IDM regression-test synchronization.
- `85dacd17b55f17e1fe717f9444ad94e1925f5b91` — qualification semantics clarification.
- `8b6e66682bec8de4b52a2d27c885b03ce1e3aa0c` — two-candle regression test.
- `ad105798c0e9d2593a240b2dd1af9b1490741d94` — implementation-contract guard.
- `c7bcb6f340751dcd1cedf39058e21d70fe242fa0` — corrected reduced-retracement fixtures.

GitHub Actions workflow is present and configured to run the full `pytest` suite on every push to `main`. The GitHub connector currently reports no workflow-run record for the latest commit, so test execution is not yet independently evidenced here.

**LAYER 3 STATUS: IMPLEMENTED / AUDIT-PASSING STATICALLY / AWAITING GREEN TEST RUN.**

Layer 4/BOS remains blocked until this Layer 3 test gate is green and the semantic audit is formally approved.


## LAYER 4 BOS AUDIT — 2026-09-26

### Audit finding
A Layer 3 / Layer 4 semantic-boundary contradiction was identified in `.agents/skills/smc/04_BOS_mechanics.md`:

- Layer 3 canonically defines `IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING` as the sufficient Layer 3 swing-confirmation transition.
- Layer 4 incorrectly stated that `MAJOR_IDM_SWEEP` only "unlocks" the swing-confirmation gate and does not automatically create `CONFIRMED_STRUCTURAL_SWING`.

### Correction applied
`.agents/skills/smc/04_BOS_mechanics.md` was corrected so that:

```
MAJOR_IDM + physical wick penetration
        ↓
MAJOR_IDM_SWEEP
        ↓
IDM_TAKEN
        ↓
CONFIRMED_STRUCTURAL_SWING
```

Retracement qualification remains a later Layer 3 prerequisite for `VALID_BOS`. The correction does not make `MAJOR_IDM_SWEEP` a BOS, does not roll the Trading Range, and does not lock the Protected Structural Extreme.

### Post-fix audit
- stale "does not automatically create CONFIRMED_STRUCTURAL_SWING" wording: absent
- stale "unless all remaining prerequisites" wording: absent
- Layer 4 remains downstream consumer of Layer 3 retracement qualification
- Layer 4 does not redefine Fibonacci depth, candle-count, displacement, or HTF qualification
- `VALID_BOS` still requires `IDM_TAKEN + MAJOR_RETRACEMENT_QUALIFIED + STRUCTURAL_SWING_BREAK`
- `MAJOR_IDM_SWEEP ≠ VALID_BOS`
- only `VALID_BOS` rolls the Trading Range and locks the Protected Structural Extreme

### Status
**LAYER 4 DOCUMENTATION AUDIT: CORRECTED / READY FOR CONTRACT SPECIFICATION**

COMMIT: 0542c75bbe97a846fa7bdf213644ccd41e3f4aa7


## GLOBAL STRUCTURAL TERMINOLOGY AUDIT — 2026-09-26

### Finding
The canonical skill did not contain a sufficiently explicit namespace contract separating Microstructure, Minor Structure, and Major/External Structure. The existing semantic owners were correct, but generic terms such as structure, swing, and break could be interpreted without an explicit layer qualifier.

### Correction implemented directly on main
The canonical documentation now explicitly defines:
- Microstructure → OHLC/candle geometry and observations.
- Minor Structure → Candle-Level Valid Pullback, Minor Structural Swing, and Minor IDM context.
- Major/External Structure → CONFIRMED_STRUCTURAL_SWING, Protected External Boundary / Protected Structural Extreme, and Major IDM.
- External structural break → STRUCTURAL_SWING_BREAK / VALID_BOS.
- CHoCH remains a structural lifecycle transition and does not promote an LTF Minor reference into Major Structure.
- Generic implementation types Swing / Break / Structure are prohibited where a canonical layer-specific semantic type is required.
- Existing canonical event/object names remain authoritative; no parallel ontology was introduced.

### Files synchronized
- .agents/skills/smc/skill.md
- .agents/skills/smc/01_micro_structure.md
- .agents/skills/smc/02_minor_structure.md
- .agents/skills/smc/03_structural_semantic_authority.md
- .agents/skills/smc/04_BOS_mechanics.md
- .agents/skills/smc/05_CHOCH_mechanics.md
- .agents/skills/smc/06_execution.md
- .agents/skills/smc/08_implementation.md

### Scope protection
No runtime mapper/analyzer/monitor code, zones.json, or knowledgebase content was modified. No new methodology rule was invented; this is a terminology/semantic-boundary clarification.

### Current HEAD
2e5b8edbf09a5621e63c5f8d93bd995915722665

### Disposition
GLOBAL TERMINOLOGY AUDIT = CORRECTED / READY FOR FINAL CROSS-SKILL CONSISTENCY CHECK.


## DIRECT VALIDATOR RE-AUDIT — GLOBAL STRUCTURAL TERMINOLOGY / IDM OWNERSHIP — 2026-09-26

The 01–08 canonical skill was re-audited against the current main branch and the primary knowledgebase evidence.

### Finding and correction

A real semantic ownership inconsistency was found:
- `skill.md` and the global terminology map placed Minor IDM under Layer 2.
- `02_minor_structure.md` still stated that Layer 3 owned Minor IDM classification.
- `03_structural_semantic_authority.md` consequently described Layer 3 as the single owner of all IDM classification.

The knowledgebase evidence supports the corrected hierarchy:
- a valid pullback produces the pullback-derived liquidity identified as Minor Inducement;
- after BOS, a newly qualified post-BOS pullback can establish Major Inducement;
- when only Minor Inducement exists, the governing external liquidity/boundary serves as Major IDM.

Canonical ownership is now:
```
Layer 1
  OHLC / candle geometry / breach observations
        ↓
Layer 2
  Candle-Level Valid Pullback
  → Verified Pullback Extreme
  → Pullback-Derived Liquidity Reference
  → MINOR_IDM
        ↓
Layer 3
  IDM_TAKEN lifecycle consequence
  → MAJOR_IDM governance
  → CONFIRMED_STRUCTURAL_SWING
  → structural retracement qualification
        ↓
Layer 4
  STRUCTURAL_SWING_BREAK
  → VALID_BOS
```

### Files corrected
- `.agents/skills/smc/02_minor_structure.md`
- `.agents/skills/smc/03_structural_semantic_authority.md`
- `.agents/skills/smc/08_implementation.md`

Remaining legacy IDM terminology is retained only where explicitly needed as historical audit evidence, not as canonical ontology.

### GitHub test status

GitHub Actions workflow `.github/workflows/tests.yml` is active on pushes to `main`.

The latest runs for the terminology/ownership commits failed in the existing Python test suite:
- 36 passed, 25 failed.
- The dominant failure is `TypeError: MinorStructureAnalysis.__init__() takes from 3 to 5 positional arguments but 6 were given` in `minor_structure_engine.py`.
- Additional structural tests fail with `QuarantineError` due to missing Layer-1 sequence evidence in post-BOS tests.

These failures are runtime implementation/test-suite synchronization issues, not documentation-only terminology failures. The canonical skill audit does not mark the methodology APPROVED for runtime implementation until those implementation tests are separately corrected and rerun.

### Audit disposition

**CANONICAL SKILL: TERMINOLOGY/OWNERSHIP CORRECTION APPLIED.**
**RUNTIME TEST SUITE: RED — CORRECTION REQUIRED.**


## FULL 01–08 SKILL CROSS-LAYER AUDIT — 2026-09-26

A full semantic-owner / downstream-consumer audit was performed against the current canonical SMC skill.

### Corrections applied
- Removed obsolete Layer-2 pending-state terminology for unavailable Outside-Bar sequence failure.
- Removed duplicated IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING transitions from the Layer-2 lifecycle diagram.
- Clarified Layer-3 IDM wording so Layer-2 owns the Minor IDM pointer while Layer 3 owns Major IDM governance; a newer valid pullback does not automatically replace Major IDM.
- Clarified the Layer-3 IDM_TAKEN definition to consume the active IDM reference rather than equating IDM with the most recent valid pullback.
- Corrected the Layer-8 determinism invariants so MAJOR_IDM_SWEEP / MINOR_IDM_SWEEP are explicitly distinct from VALID_BOS, while IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING remains the canonical structural confirmation chain.

### Cross-layer result
01 Microstructure → 02 Minor Structure → 03 Structural Semantic Authority → 04 BOS → 05 CHoCH → 06 Execution → 07 Risk → 08 Implementation is now semantically consistent on the audited IDM, pullback, swing-confirmation, BOS, and observability boundaries.

No runtime mapper/analyzer/monitor integration was performed.

### Current runtime note
The previously recorded GitHub test-suite failures remain implementation/test synchronization issues and were not silently treated as resolved by this documentation audit.

### Repository state
Direct commits were made on main only. No new branch was created.


## FULL 01–08 CANONICAL SKILL AUDIT — 2026-09-26

A fresh full-layer audit was performed against the current `.agents/skills/smc/` authority, with the canonical ownership rule enforced as:
`Define once at semantic owner → downstream reference → downstream consumption`.

### Corrections applied directly to main

1. `03_structural_semantic_authority.md`
   - Tightened post-BOS Major IDM creation: a post-BOS pullback establishes Major IDM only when it independently satisfies the canonical Major-IDM qualification.
   - Separated Layer-2 active Minor IDM / pullback-derived pointer movement from Layer-3 active Major IDM governance.
   - Clarified that a newer valid pullback immediately supersedes the Layer-2 Minor IDM reference, while Layer-3 Major IDM changes only after independent Major-IDM qualification.
   - Removed ambiguous `Structurally Valid Pullback` wording from the Major-IDM creation rule in favor of the explicit post-BOS Major-IDM qualification.
   - Removed the typo `A A Major IDM`.

2. `04_BOS_mechanics.md`
   - Layer 4 no longer describes itself as mutating the upstream pullback/IDM reference after an insufficient continuation break.
   - Layer 4 now classifies the failed continuation as `IMPULSE_EXTENSION` and explicitly delegates any later reference shift to Layer-2/Layer-3 ownership.

### Cross-layer audit result

- Layer 1: Microstructure-only OHLC/geometry/observability ownership preserved.
- Layer 2: Candle-Level Valid Pullback, Verified Pullback Extreme, active Minor IDM/pullback-derived reference ownership preserved.
- Layer 3: Major/External Structure, Major IDM governance, Confirmed Structural Swing, retracement qualification ownership preserved.
- Layer 4: BOS is a downstream consumer of Layer-3 qualification; no raw retracement/Fibonacci recomputation or upstream mutation.
- Layer 5: CHoCH remains fractal/context-dependent; LTF Structural Glitch changes reference location, not ontology.
- Layer 6: execution/POI modules consume structural outputs and do not redefine BOS/CHoCH/IDM.
- Layer 7: target/trade-management policy remains separate from canonical structural truth; BE remains stop management, not target semantics.
- Layer 8: implementation contract reflects the layer boundaries and fail-closed/zero-fabrication requirements.

### Terminology audit

The canonical skill contains no active `FALLBACK_MAJOR_IDM` / `REAL_MAJOR_IDM` ontology. Remaining occurrences are explicitly historical reconciliation documentation describing the removed model. No generic canonical `Swing` or `Break` domain object/type is defined.

### Validation

Post-edit GitHub re-read confirms both modified files are present on `main`, and the cross-layer invariant checks pass. No runtime Python, `zones.json`, or `knowledgebase/` files were modified.

STATUS: **01–08 CANONICAL SKILL AUDIT = APPROVED / CORRECTIONS APPLIED**


## DIRECT VALIDATOR — FULL 01–08 SKILL RE-AUDIT — 2026-09-26

Audit scope: all canonical skill layers 01–08 and cross-layer semantic ownership, using `.agents/skills/smc/` as the canonical authority.

### Findings
- Layer 1 Microstructure boundary: consistent. No Layer-2+ semantic ownership leakage found in normative implementation rules.
- Layer 2 Minor Structure: consistent. Candle-Level Valid Pullback, Verified Pullback Extreme, active pullback pointer and Minor IDM ownership are separated from Layer 3 Major IDM governance. Outside-Bar unavailable sequence handling is terminal for the affected candidate and cannot be resolved retroactively.
- Layer 3 Structural Semantic Authority: consistent. IDM_TAKEN confirms the relevant CONFIRMED_STRUCTURAL_SWING; retracement qualification remains a later continuation-BOS gate. Major IDM continuity preserves the prior protected external boundary when only Minor IDM exists. No fallback/real Major IDM ontology remains.
- Layer 4 BOS: consistent. Layer 4 consumes stored Layer-3 qualification and does not recalculate retracement/HTF logic. VALID_BOS requires IDM_TAKEN + MAJOR_RETRACEMENT_QUALIFIED + STRUCTURAL_SWING_BREAK.
- Layer 5 CHoCH: one cross-layer contradiction found and corrected. The Major-IDM wick-sweep paragraph incorrectly said the sweep did not automatically create CONFIRMED_STRUCTURAL_SWING. It now explicitly consumes IDM_TAKEN and immediately confirms the associated CONFIRMED_STRUCTURAL_SWING, while remaining non-BOS/non-CHoCH and not rolling the range.
- Layer 6 Execution: consistent. POI/OB/FVG/Engineering Liquidity/Rejection Block remain execution-owned and do not manufacture structure.
- Layer 7 Risk/Targets: consistent. Target selection, fixed-R, BE, profit-lock and trailing remain policy/implementation scope; TARGET_REACHED remains distinct from closure/stop movement/broker fill.
- Layer 8 Implementation: consistent with Layers 1–7. Generic Swing/Break/Structure objects remain prohibited where canonical semantic types are required; canonical lifecycle and CHoCH/BOS gates are consumed downstream.

### Documentation cleanup
- Fixed duplicate section numbering in `.agents/skills/smc/skill.md` (Documentation authority is now Section 6).

### Validation
- Re-audit found no additional canonical contradiction requiring a methodology change.
- Runtime files and `knowledgebase/` were not modified.
- The legacy feature branch `feature/upstream-structural-evidence-contract-v1` is an ancestor of current `main` (0 commits ahead, 118 behind), so it contains no unique work relative to main. The available GitHub connector has no branch-delete operation, therefore branch deletion could not be performed from this session.

### Status
**FULL 01–08 CANONICAL SKILL AUDIT: PASS after correction.**

The corrected Layer-5 wording is committed directly to `main`; no separate feature branch is required.


## FULL 01–08 SKILL AUDIT — TERMINOLOGY / SEMANTIC CONSISTENCY PASS — 2026-09-26

### Scope
- Audited the complete canonical .agents/skills/smc/ 01–08 layer set plus skill.md against the current canonical semantic-owner architecture.
- Canonical authority remains .agents/skills/smc/; knowledgebase remains source evidence and was not modified.
- Runtime files and analyzed data remain outside this phase.

### Audit result
- Layer 1 remains pure Microstructure/OHLC geometry and observation ownership; no Pullback/IDM/BOS/CHoCH ownership leakage found.
- Layer 2 remains the exclusive owner of Candle-Level Valid Pullback, Verified Pullback Extreme, active pullback state, Pullback-Derived Liquidity Reference, and Minor IDM formation. Outside-Bar UNAVAILABLE ordering is terminal for the affected candidate and cannot be retroactively completed.
- Layer 3 remains the exclusive Major / External Structure authority. IDM_TAKEN confirms CONFIRMED_STRUCTURAL_SWING; retracement qualification is a later continuation-BOS gate. Major IDM remains one semantic class; a post-BOS Minor IDM never replaces the prior protected external boundary unless a new Major IDM independently qualifies.
- Layer 3 retracement gates remain hierarchical: standard equilibrium path first; below-equilibrium HTF path only with the complete immediate-HTF valid-pullback condition; one-candle displacement is an explicit source-defined exception and not a general one-candle rule.
- Layer 4 consumes Layer-3 qualification and canonical CONFIRMED_STRUCTURAL_SWING; it does not recalculate retracement depth, candle count, displacement thresholds, or HTF validity.
- Layer 5 CHoCH remains context/fractal-based. LTF Structural Glitch substitutes the operative reference only within its context; IDM provenance controls wick/body mode. It does not promote Minor Structure into Major Structure.
- Layer 6 execution remains downstream-only. POI, OF/OB, Engineering Liquidity, Rejection Block, and entry modules do not manufacture structure. Decisional OB remains causally tied to VALID_BOS; Extreme OB remains lineage-scoped.
- Layer 7 contains no universal target winner, fixed-R, BE, profit-lock, or trailing methodology rule. Target Plan and trade management remain downstream policy/implementation concerns.
- Layer 8 remains implementation mapping only and preserves layer-specific semantic types; it does not redefine canonical methodology.

### Corrections applied
1. Replaced residual macro-state terminology in Layer 3 with canonical Major / External structural state.
2. Replaced residual macro structural continuation event in Layer 4 with Major / External structural continuation event.
3. Clarified Layer-4 generic-type wording so Swing/Break remain prohibited as unqualified semantic types while canonical names remain authoritative.
4. Removed obsolete fallback Major IDM terminology from the active Layer-8 contract; the model now describes one MajorIDM semantic class with traceable provenance and prior-protected-boundary continuity.
5. Replaced residual macro-BOS gates terminology with Major / External BOS gates.

### Post-edit stale-term audit
- No active FALLBACK_MAJOR_IDM, REAL_MAJOR_IDM, Real Major IDM, or fallback Major IDM terminology remains in 01–08/skill index.
- No residual macro namespace remains in the audited 01–08/skill index.
- No unqualified generic Swing/Break implementation type remains in the audited canonical contract wording.
- The one-candle displacement exception remains explicitly scoped to the canonical Layer-3 retracement exception and is not generalized.
- Outside-Bar UNAVAILABLE handling remains explicitly represented in Layer 1/2/8.

### Validation disposition
01–08 CANONICAL SKILL AUDIT = PASS after corrections.
No unresolved cross-layer semantic contradiction was identified in this pass.

### Repository state
- All changes were written directly to main; no feature branch was created.
- Existing legacy branch feature/upstream-structural-evidence-contract-v1 is still visible on GitHub, but the available GitHub connector exposes branch search/create only and no branch-delete operation. It therefore could not be deleted through the currently available interface.
- No runtime Mapper integration was performed.

### Next phase gate
The canonical skill is ready for the next isolated implementation phase. Continue with the next layer only after its implementation/tests pass and receive explicit approval. Mapper integration remains deferred until the layer stack is approved.


## FULL 01–08 SKILL AUDIT — FINAL CROSS-LAYER RECONCILIATION — 2026-09-26

A fresh audit was performed after the terminology/ownership corrections, using .agents/skills/smc/ as the canonical authority and enforcing the semantic-owner rule: Define once at semantic owner → downstream reference → downstream consumption.

### Findings and corrections
- Layer 1 remains Microstructure-only: OHLC geometry, breach/equality/reference observations, and observability boundary. No Layer-2+ semantic ownership leakage found.
- Layer 2 remains the sole owner of Candle-Level Valid Pullback, Verified Pullback Extreme, Pullback-Derived Liquidity Reference, and Minor IDM formation/active pointer.
- Corrected 02_minor_structure.md: removed a duplicated IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING chain from the Layer-2 lifecycle diagram; Layer 2 now hands off to Layer 3 once MINOR_IDM is established.
- Corrected 02_minor_structure.md: Layer-3 handoff now names MAJOR_IDM governance rather than MAJOR_IDM definition, preventing ownership ambiguity.
- Corrected 03_structural_semantic_authority.md: the lifecycle now says IDM GOVERNANCE / ACTIVE IDM HANDOFF, not IDM DEFINITION / CLASSIFICATION; Layer 3 explicitly consumes rather than recreates the Layer-2 Minor IDM definition.
- Layer 3 Major IDM continuity is consistent: one MAJOR_IDM semantic class; post-BOS Minor IDM alone never replaces the prior protected external boundary; a new Major IDM requires independent qualification.
- Layer 3 retracement qualification remains the later continuation-BOS gate; Layer 4 consumes it and does not recompute it.
- Layer 4 BOS remains IDM_TAKEN + MAJOR_RETRACEMENT_QUALIFIED + STRUCTURAL_SWING_BREAK; MAJOR_IDM_SWEEP is distinct from BOS.
- Layer 5 CHoCH remains context/fractal-based; LTF Structural Glitch changes the operative reference, not the ontology, and wick/body mode remains IDM-provenance dependent.
- Layer 6 execution does not manufacture structure; POI/OF/OB/RB/Engineering Liquidity boundaries remain downstream and typed.
- Layer 7 keeps target selection, fixed-R, BE, profit-lock, and trailing outside canonical structural methodology.
- Layer 8 preserves layer-specific implementation types and the canonical lifecycle; no fallback/real-Major-IDM ontology remains.

### Stale-term / consistency checks
- FALLBACK_MAJOR_IDM / REAL_MAJOR_IDM: none in active 01–08 canonical rules.
- residual macro namespace: none in active 01–08 skill documents.
- duplicate IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING chain in Layer 2: removed.
- UNAVAILABLE ↔ PENDING Outside-Bar candidate model: none in active canonical rules.
- no generic Swing / Break implementation class/object is defined.

### Commits
- 1dd29f3417d9fec92c83bd0206adf264a1ee0fe1 — Layer-2 lifecycle / ownership correction.
- 0d859a9a396d9ce1d884294dbd0862873dbfc9fa — Layer-3 IDM ownership wording correction.

### Validation disposition
FULL 01–08 CANONICAL SKILL AUDIT = PASS / CORRECTIONS APPLIED.
No unresolved cross-layer semantic contradiction was identified in this pass. Runtime mapper/analyzer/monitor integration remains intentionally deferred until the isolated layer stack is approved.


## FULL 01–08 CANONICAL SKILL AUDIT — 2026-09-27

A fresh cross-layer audit was performed against the current `.agents/skills/smc/` authority, enforcing:
`Define once at semantic owner → downstream reference → downstream consumption`.

### Findings
- Layer 1 Microstructure: OHLC/candle geometry, breach/equality/reference observations and observability boundary remain isolated; no downstream structural ownership leakage requiring correction was found.
- Layer 2 Minor Structure: Candle-Level Valid Pullback → Verified Pullback Extreme → Pullback-Derived Liquidity Reference → MINOR_IDM ownership is consistent. Outside-Bar `UNAVAILABLE` handling is terminal for the affected candidate and cannot be retroactively resolved.
- Layer 3 Major / External Structure: IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING → retracement qualification is consistent. Major IDM remains one semantic class; Minor IDM does not silently replace the active Major IDM reference.
- Layer 4 BOS: consumes stored Layer-3 qualification and does not recompute retracement/HTF rules. VALID_BOS requires IDM_TAKEN + MAJOR_RETRACEMENT_QUALIFIED + STRUCTURAL_SWING_BREAK.
- Layer 5 CHoCH: context/fractal routing, Major-IDM provenance and LTF Structural Glitch remain consistent. Minor LTF references are not promoted into Major Structure.
- Layer 6 Execution: POI/OF/OB/RB/Engineering Liquidity and entry modules remain downstream consumers and do not manufacture structural state.
- Layer 7 Risk/Targets: target selection, fixed-R, BE, profit-lock and trailing remain policy/implementation scope; TARGET_REACHED remains distinct from closure/fill/stop movement.
- Layer 8 Implementation: layer-specific semantic types, fail-closed behavior, canonical lifecycle consumption and target/notification separation remain consistent.

### Documentation defects corrected
1. `.agents/skills/smc/skill.md`: duplicate `## 6` section numbering corrected to `## 7` for Precedence and `## 8` for Canonical document set.
2. `.agents/skills/smc/05_CHOCH_mechanics.md`: duplicate `3.5` section numbering corrected; Canonical invariants is now `3.6`.

These were documentation-consistency defects only; no SMC methodology rule was changed.

### Cross-layer semantic checks
- No active FALLBACK_MAJOR_IDM / REAL_MAJOR_IDM ontology found in the canonical layer documents.
- No active macro namespace found in the canonical layer documents.
- Outside-Bar candidate `PENDING` is not an active canonical state; the Layer-2 rule explicitly rejects the affected candidate when required sequence evidence is unavailable.
- Generic Swing/Break are not defined as canonical implementation-domain objects.
- 38.2%–<50% remains conditional on the applicable immediate HTF valid-pullback evidence; it is not a standalone threshold.
- The one-candle displacement case remains an explicit exception and is not generalized to normal pullback qualification.

### Validation
GitHub re-read after both corrections found no duplicate numbered top-level section headings in the canonical index; the CHoCH duplicate numbering is also resolved. The semantic cross-layer audit found no remaining canonical contradiction requiring a methodology change.

### Status
**FULL 01–08 CANONICAL SKILL AUDIT = PASS / 2 DOCUMENTATION CORRECTIONS APPLIED.**

Runtime Mapper/analyzer/monitor integration remains intentionally deferred.


## DIRECT VALIDATOR — LAYER 1–4 RE-AUDIT AND CORRECTION — 2026-09-27

Scope: .agents/skills/smc/01_micro_structure.md through 04_BOS_mechanics.md, using .agents/skills/smc/ as canonical authority and enforcing: Define once at semantic owner → downstream reference → downstream consumption.

### Audit findings

- Layer 1 — PASS, no correction required. Microstructure remains limited to OHLC/candle geometry, breach/equality/reference observations, Inside/Outside Bar, candle-internal sequence and observability semantics. It does not own Pullback, IDM, BOS or CHoCH.
- Layer 2 — CORRECTED. The validation contract previously described the Active Pullback Pointer as following the “most recent structurally accepted pullback”. That wording imported a Layer-3 structural-acceptance concept into Layer-2 ownership. It now explicitly follows the most recent completed CANDLE-LEVEL VALID PULLBACK for the active impulsive leg; Layer 2 does not require Layer-3 acceptance to advance its pointer.
- Layer 3 — PASS, no correction required. Major/External Structure, Major IDM governance, IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING, and the later retracement qualification gate remain internally consistent. No fallback/real-Major-IDM ontology is present.
- Layer 4 — CORRECTED. The pre-qualification IMPULSE_EXTENSION branch was narrowed to eligible continuation external levels that are not functioning as Major IDM. A Major-IDM level remains on the separate MAJOR_IDM_SWEEP path and cannot be reclassified as IMPULSE_EXTENSION merely because BOS qualification is absent.

### Cross-layer verification

- VALID_BOS = IDM_TAKEN + MAJOR_RETRACEMENT_QUALIFIED + STRUCTURAL_SWING_BREAK remains intact.
- Layer 4 does not recompute Layer-3 retracement/Fibonacci/HTF logic.
- Major IDM sweep remains distinct from BOS and from impulse-extension classification.
- Outside-Bar unavailable ordering remains terminal for the affected Layer-2 candidate; no active PENDING state exists.
- No active FALLBACK_MAJOR_IDM, REAL_MAJOR_IDM, generic Swing/Break semantic type, or residual macro namespace was found in Layers 1–4.
- Knowledgebase and runtime Mapper/analyzer/monitor files remain untouched.

### Commits

- b73297ab6843038a81f70a8fdad249847bf2fcdf — Layer-2 active pullback ownership wording correction.
- b990a8868427b758c7f7fb7a62111e018c4347c4 — Layer-4 continuation-break / Major-IDM sweep boundary correction.

### Final status

LAYER 1–4 SKILL AUDIT = PASS / 2 TARGETED CORRECTIONS APPLIED.

Implementation/runtime tests were not changed by this pass. Mapper integration remains deferred until the isolated layer implementations are independently approved.


## DIRECT VALIDATOR — LAYER 1–4 FRESH AUDIT — 2026-09-27

Scope: current main, Layers 01–04 of the canonical SMC skill.

### Audit result

- Layer 1: PASS. Microstructure remains limited to OHLC/candle geometry, breach/equality/reference observations, Inside/Outside Bar, and observability. No downstream structural ownership leakage found.
- Layer 2: PASS. Candle-Level Valid Pullback, Verified Pullback Extreme, Pullback-Derived Liquidity Reference, and Minor IDM remain Layer-2-owned. Outside-Bar unavailable sequence is terminal for the affected candidate and cannot be completed retroactively.
- Layer 3: CORRECTED. The insufficient-retracement lifecycle diagram incorrectly connected the failed attempted-break/reference-shift branch to Protected Structural Extreme Lock + Trading Range Rollover. That rollover is valid only after VALID_BOS. The branch now explicitly continues the current lifecycle with no protected-extreme lock and no range rollover.
- Layer 4: PASS. BOS consumes Layer-3 stored qualification; it does not recompute retracement, HTF, or candle-count rules. MAJOR_IDM_SWEEP remains distinct from VALID_BOS, and insufficient continuation remains IMPULSE_EXTENSION without range rollover.

### Cross-layer invariants

- IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING → STRUCTURAL_RETRACEMENT_QUALIFICATION → STRUCTURAL_SWING_BREAK → VALID_BOS remains coherent.
- VALID_BOS is the sole trigger for Protected Structural Extreme Lock and Trading Range Rollover.
- Failed/insufficient continuation does not lock the protected extreme or roll the range.
- No active FALLBACK_MAJOR_IDM, REAL_MAJOR_IDM, SWING_CANDIDATE, or generic canonical Swing/Break object was reintroduced.

### Correction

- Commit: 31ce89db898da8479849a2321cb697f083cf98a6
- File: .agents/skills/smc/03_structural_semantic_authority.md
- Purpose: correct the insufficient-retracement lifecycle diagram.

### Status

**LAYER 1–4 FRESH AUDIT = PASS / 1 TARGETED CORRECTION APPLIED.**


## IMPLEMENTATION CORRECTION — LAYER 2 — 2026-09-27

The canonical skill was not modified.

### Finding
minor_structure_engine.py contained an invalid active-state model:
- MinorStructureAnalysis.resolution referenced an undeclared latest_resolution attribute.
- The implementation still exposed PENDING_UNAVAILABLE_SEQUENCE / PendingPullback despite the canonical Layer-2 rule that an Outside-Bar UNAVAILABLE sequence is terminal for the affected candidate and cannot remain pending or be resolved retroactively.

### Correction
- Removed the active PendingPullback representation.
- Removed PENDING_UNAVAILABLE_SEQUENCE.
- Made the latest Layer-2 resolution an explicit immutable resolution field.
- Preserved terminal INVALIDATED_UNAVAILABLE_SEQUENCE behavior.
- Updated Layer-2 tests to assert the absence of the obsolete pending state.

### Validation
- GitHub write completed directly on main.
- Canonical .agents/skills/smc/ files were not modified.
- GitHub Actions workflow exists at .github/workflows/tests.yml and runs python -m pytest -q on pushes to main, but the available connector returned no workflow run for the correction commit, so remote test execution could not be independently verified in this session.

### Commits
- 587691f658cf2359963647de0dc9654fdf515e66 — Layer-2 implementation correction.
- 3adf784330af3370ab9db1eff561813d7cf6827c — Layer-2 regression-test alignment.

### Status
Layer-2 implementation correction applied; formal approval remains subject to test execution and the next implementation audit.


## IMPLEMENTATION CORRECTION — LAYER 3 — 2026-09-27

The canonical skill was not modified.

### Finding
structural_engine.py validated attempt_end_candle_id after indexing it. A missing ID therefore raised a raw KeyError instead of the canonical fail-closed QuarantineError.

### Correction
- Validate attempt_end_candle_id membership before dictionary indexing.
- Added a regression test requiring QuarantineError for an unknown attempt-end candle.

### Commits
- c5cf9370c4fd53453acbc783f5db089e3df23cff — Layer-3 input-validation correction.
- bf7502384ad54ded23fe7452ee180122dd3b1f1b — Layer-3 regression test.

### Status
Layer-3 fail-closed input boundary corrected; formal approval remains subject to executable test results and the broader implementation audit.


## FULL 01–08 SKILL AUDIT — 2026-09-27

Direct audit of the current main branch against the canonical `.agents/skills/smc/` ownership model completed.

### Corrections applied
- `05_CHOCH_mechanics.md`: clarified that the ordinary CHoCH route uses the Protected Opposing Structural Extreme / Governing Opposing Range Boundary; the LTF Structural Glitch is the explicit reference-substitution exception and does not promote the Minor reference into Major Structure.
- `08_implementation.md`: corrected the lifecycle state-transition table so bootstrap/confirmation transitions explicitly follow `SVP → Verified Extreme → Minor IDM → IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING → CONFIRMED_RANGE`; retracement qualification and BOS remain later gates.

### Audit result
- 01 Microstructure: ownership and OHLC primitive boundary consistent.
- 02 Minor Structure: Candle-Level Valid Pullback → Verified Pullback Extreme → Pullback-Derived Liquidity Reference → Minor IDM ownership consistent.
- 03 Structural Semantic Authority: IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING → later retracement qualification → BOS lifecycle consistent.
- 04 BOS: downstream consumer of stored Layer-3 qualification; no raw retracement redefinition.
- 05 CHoCH: ordinary external route and LTF Structural Glitch route now explicitly reconciled.
- 06 Execution: POI/OF/OB/RB/ENG_LQD ownership remains downstream and structurally separated.
- 07 Risk: target/trade-management policy remains separated from canonical structural semantics.
- 08 Implementation: lifecycle table synchronized with canonical ownership and prerequisite order.

### Regression scan
Active skill files contain no stale `FALLBACK_MAJOR_IDM`, `REAL_MAJOR_IDM`, `SWING_CANDIDATE`, fully-unmitigated-FVG, or one-candle-positive-retracement canonical rules.

### GitHub Actions
Commit `572e963a53aa02797061ebb9a74430519b7c50eb` test run: 58 passed / 4 failed. Failures are Layer-2/3 runtime-test contract mismatches (Outside-Bar invalidation expectation and post-BOS IDM fixture assumptions), not documentation-only skill failures.
Commit `d6f2f5a9947e52e7bcf290accb5763bf49a46e8c` test run also completed with failure; runtime tests remain to be reconciled separately before implementation approval.

### Branch state
`feature/upstream-structural-evidence-contract-v1` still exists on GitHub. The available GitHub mutation interface in this session does not expose branch deletion, so it was not falsely claimed deleted.


## DIRECT VALIDATOR FULL-LAYER AUDIT — 2026-09-27

Full 01–08 canonical skill audit completed against the current `main` state and the established canonical ownership/lifecycle rules.

### Finding and correction
- Found one concrete Layer-8 state-machine contradiction: `IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING` was incorrectly shown transitioning directly to `CONFIRMED_RANGE` in the state-transition table.
- Canonical Layer-3 lifecycle requires `IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING → STRUCTURAL RETRACEMENT QUALIFICATION → STRUCTURAL_SWING_BREAK → VALID_BOS`; only `VALID_BOS` establishes/rolls the confirmed Trading Range and locks the Protected Structural Extreme.
- Corrected `.agents/skills/smc/08_implementation.md`: after IDM takeout the lifecycle remains `CONFIRMATION_LOCKED` until the downstream BOS gates are satisfied; no premature range confirmation occurs.
- Corrected one Layer-8 guard statement so only an **unvalidated** candle-level pullback is prohibited from becoming IDM; a canonical Layer-2 Candle-Level Valid Pullback does establish the Minor IDM input.

### Cross-layer post-fix checks
- 01–08: no remaining `FALLBACK_MAJOR_IDM`, `REAL_MAJOR_IDM`, or `SWING_CANDIDATE` terminology.
- 01–08: no remaining targeted contradiction where IDM takeout directly creates `CONFIRMED_RANGE`.
- Major IDM remains one semantic class.
- Layer-2 Minor IDM ownership remains separate from Layer-3 Major IDM governance.
- Layer-3 retracement qualification remains downstream of `CONFIRMED_STRUCTURAL_SWING` and upstream of continuation BOS.
- Layer-4 consumes stored qualification and does not recalculate raw retracement rules.
- Layer-5 CHoCH remains context/provenance dependent; Major-IDM wick is not CHoCH.
- Layer-6 execution remains downstream of structural authorization; RB remains separately typed and Engineering Liquidity remains Extreme-OF/Extreme-OB lineage based.
- Layer-7 target/risk/trade-management policy remains separate from canonical structural truth.
- Layer-8 remains implementation-only and must not manufacture upstream evidence.

### Status
**FULL 01–08 AUDIT: PASS after correction.**

Correction commit: `b44ddfc56fc394ea74bb5eb27c455f43b45b852e`.


## DIRECT VALIDATOR — FULL SKILL RE-AUDIT — 2026-09-27

A fresh audit was performed after the previous FULL 01–08 PASS, covering the complete canonical skill set and enforcing semantic ownership: Define once at semantic owner → downstream reference → downstream consumption.

### Findings
- Layers 01–04 remain semantically consistent: Micro → Minor → Major/External → BOS ownership is intact; Layer 4 consumes Layer-3 qualification and does not recompute it.
- Layer 5 contained one documentation invariant typo: `MAJOR_IDM ≠ MAJOR_IDM`. This was not a methodology contradiction but was logically invalid and could obscure the intended provenance boundary.
- The typo was corrected to an explicit invariant distinguishing Major-IDM provenance from CHoCH confirmation.
- Layers 06–08 remain consistent with structural ownership, POI/RB/Engineering-Liquidity separation, target-policy separation, and fail-closed implementation boundaries.
- Supporting canonical documents (`methodology_parameters.md`, `trading_policy.md`, `platform_execution.md`, `countertrend_scenarios.md`, `source_reconciliation.md`, and `reconciliation/full_methodology_gap_audit.md`) were cross-checked for competing structural definitions; no additional active contradiction was found.

### Regression / stale-term checks
- No active `FALLBACK_MAJOR_IDM`, `REAL_MAJOR_IDM`, `SWING_CANDIDATE`, or `PENDING_UNAVAILABLE_SEQUENCE` terminology remains in the canonical layer files.
- No duplicate top-level/subsection headings were found in Layers 01–08.
- No active `IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING → CONFIRMED_RANGE` premature-range transition was found.
- Outside-Bar `UNAVAILABLE` remains terminal for the affected Layer-2 candidate; later candles cannot retroactively complete it.
- 38.2%–<50% remains conditional on immediate-HTF valid-pullback evidence; the one-candle displacement case remains an explicit exception, not a general rule.
- Major IDM remains one semantic class; Minor IDM does not silently replace the active Major IDM reference.

### Correction
- `c9f7dd16965fa81852cf2b76f94a654cd9be53d1` — corrected the Layer-5 CHoCH invariant typo.

### Final disposition
**FULL 01–08 + SUPPORTING SKILL AUDIT = PASS / 1 DOCUMENTATION CORRECTION APPLIED.**

No further canonical methodology correction was identified in this pass. Runtime Mapper/analyzer/monitor integration remains intentionally deferred until isolated layer implementations are independently approved.
