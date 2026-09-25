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
