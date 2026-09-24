# CURRENT TASK
Phase 5: Major/Minor IDM semantic reconciliation

# DEVELOPER REPORT
**Current Repository State:**
* **Branch:** main
* **HEAD:** 3bfb9cd
* **Working-tree status:** clean (after committing IDM semantic reconciliations)
* **Implementation decisions:** 
  - **Prerequisite Chain Enforcement:** Updated `02_minor_structure.md` and `03_structural_semantic_authority.md` to strictly distinguish `CANDLE-LEVEL VALID PULLBACK` from `STRUCTURALLY VALID PULLBACK` (SVP). Layer 2 evaluates candle-level logic and hands off to Layer 3 for structural qualification, establishing the SVP and its verified extreme.
  - **Deterministic IDM Classification:** Defined that IDM is determined strictly at the time a pullback becomes structurally valid. Before `VALID_BOS`, it is `MINOR_IDM`. After `VALID_BOS`, it is `REAL_MAJOR_IDM`.
  - **Active IDM vs Historical IDM:** Explicitly defined the `ACTIVE IDM REFERENCE SHIFT` lifecycle in Layer 3. When a newer `STRUCTURALLY VALID PULLBACK` forms on the active leg, the active IDM pointer shifts, while the older IDM becomes immutable history. IDM properties are never retroactively rewritten.
  - **IDM Takeout vs Creation:** Clarified that physical `IDM_TAKEN` does not create a new IDM. A new IDM is created only when a newer SVP forms.
  - **Fallback Proxy Lifecycle:** Clarified the lifecycle of `FALLBACK_MAJOR_IDM` as a temporary proxy boundary following a BOS. Once the first post-BOS SVP forms, it establishes `REAL_MAJOR_IDM`, and the fallback proxy is permanently superseded.
  - **Post-CHoCH Reconciliation:** Maintained alignment with `05_CHOCH_mechanics.md` so that the first post-CHoCH SVP produces the first post-CHoCH `MINOR_IDM`, not a `REAL_MAJOR_IDM`.
  - **Downstream Alignment:** Updated `04_BOS_mechanics.md` to specify that `IDM_TAKEN` must be satisfied strictly by the **active IDM reference** at the time of the event, not by historical IDM objects.
  - No new files were created. Python files remain completely untouched.

## Semantic Ownership Verification
- `02_minor_structure.md` fully owns `CANDLE-LEVEL VALID PULLBACK`, `VERIFIED PULLBACK EXTREME`, `PULLBACK-DERIVED LIQUIDITY REFERENCE`, and the `ACTIVE PULLBACK POINTER`.
- `03_structural_semantic_authority.md` fully owns the IDM definition, classification (`MINOR_IDM`, `REAL_MAJOR_IDM`, `FALLBACK_MAJOR_IDM`), and the `ACTIVE IDM REFERENCE SHIFT` lifecycle.
- `04_BOS_mechanics.md` and `05_CHOCH_mechanics.md` accurately consume the active IDM state.

# VALIDATION REPORT
Phase 5 (Major/Minor IDM Semantic Reconciliation) is fully complete.
The IDM prerequisites and active-reference lifecycle were audited across Layer 2 and Layer 3 owners, eliminating ambiguity between candidate pullbacks, active IDM, historical IDM, and post-break lifecycle proxies. The explicit IDM invariants requested in the task have been successfully added to the semantic authority.

# REQUIRED CORRECTIONS
[None active]

# OPEN SPECIFICATION GAPS
- Target Price Derivation remains OPEN.

# IMPLEMENTATION STATUS
Phase 5 (IDM Semantics) is completed.
- [x] Phase 5: Established exact IDM prerequisite chain (Candle-Level VP -> SVP -> IDM).
- [x] Phase 5: Made Minor vs Major IDM classification deterministic based on structural event state.
- [x] Phase 5: Defined Active IDM reference vs Historical IDM objects.
- [x] Phase 5: Standardized "Most Recent Structurally Valid Pullback" terminology.
- [x] Phase 5: Clarified IDM_TAKEN vs Active IDM Reference Shift.
- [x] Phase 5: Reconciled Real Major IDM vs Fallback proxy and post-CHoCH lifecycles.
- [x] Phase 5: Added explicit IDM invariants to `03_structural_semantic_authority.md`.

# COMMITS
COMMIT: 3bfb9cd
FILES: .agents/skills/smc/02_minor_structure.md, .agents/skills/smc/03_structural_semantic_authority.md, .agents/skills/smc/04_BOS_mechanics.md, AGENT_REVIEW.md
PURPOSE: Reconcile Major/Minor IDM semantics, exact prerequisite chain, and active-reference lifecycle across semantic owners.
TESTS: N/A (Documentation update only)
