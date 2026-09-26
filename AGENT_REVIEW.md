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
