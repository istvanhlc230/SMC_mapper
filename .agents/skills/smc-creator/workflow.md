# SMC Skill Creator — Executable Workflow

## 0. Preconditions
Verify current branch is docs/smc-microstructure-phase1; main/knowledgebase/ exists; .agents/skills/smc/ exists; .agents/skills/smc/01_micro_structure.md exists; no source files under main/knowledgebase/ are modified; unrelated working-tree changes are preserved and not overwritten.
If a precondition fails: BLOCK and report it.

## 1. Source Analyst
Read relevant source files from main/knowledgebase/. For each relevant claim produce: source_id, source_file, source_location, source_text, concept, statement_type, confidence.
Classify claims as DEFINITION, RULE, CONDITION, EXCEPTION, BOUNDARY, EXAMPLE, INTERPRETATION, PROCEDURAL_GUIDANCE, or NUMERICAL_PARAMETER.
Examples and narrative explanations are evidence, not automatic canonical rules.
Output: Source Map.

## 2. Canonical Rule Auditor
Read the current semantic owner before reading cross-references. For Phase 1 the primary owner is .agents/skills/smc/01_micro_structure.md.
Classify each source claim as EXISTING_CANONICAL_RULE, SUPPORTING_EVIDENCE, NEW_CANONICAL_CANDIDATE, OUT_OF_SCOPE, AMBIGUOUS_SOURCE, or CONFLICTING_SOURCE.
For every candidate or conflict create a Contract Ledger entry containing concept, source_reference, source_claim, current_canonical_claim, relationship, semantic_difference, boundary_difference, determinism_issue, proposed_resolution, affected_documents, affected_tests, and status.
Do not edit canonical files in this phase.

## 3. Boundary and determinism gate
Reject any proposed change that collapses distinct concepts.
Required separations: Candle Extreme Breach ≠ Structural Swing Break; Candle Extreme Breach ≠ VALID BOS; Candle Extreme Breach ≠ CHoCH; Candle Extreme Breach ≠ IDM; Outside Bar ≠ BOS; EQH/EQL ≠ IDM; Equal Extreme Reference Transfer ≠ Swing Formation; Candle Internal Sequence ≠ Pullback Formation; Candlestick-Based Trend ≠ Structural Trend.
OHLC = Open → High → Low → Close. OLHC = Open → Low → High → Close. If OHLC data permits multiple paths, do not infer one.

## 4. Source conflict gate
When sources disagree, determine whether the difference is caused by different concepts, conditions, context/timeframe, example versus definition, methodology version, or numerical parameter versus semantic rule.
If evidence cannot resolve the difference, status must be UNRESOLVED_SOURCE_AMBIGUITY and implementation is blocked.
Never silently select a source because it is newer, longer, or more convenient.

## 5. Four open contracts
Treat the four already-identified open contractual/definition points in 01_micro_structure.md as explicit audit items. Do not invent their contents.
For each record: OPEN_CONTRACT_ID, CURRENT_STATE, SOURCE_EVIDENCE, CANONICAL_IMPLICATION, DETERMINISM_IMPLICATION, BOUNDARY_IMPLICATION, TEST_IMPLICATION, PROPOSED_RESOLUTION, STATUS.
Phase 1 cannot close while any item remains OPEN, CONFLICTING, or HUMAN_REVIEW_REQUIRED.

## 6. Change Set
Only after reconciliation produce: changed_file, current_rule, proposed_rule, reason, source_reference, semantic_impact, boundary_impact, determinism_impact, test_impact, approval_status.
No implementation before explicit human approval.

## 7. Human approval
APPROVED → implementation may start. REJECTED → preserve current canonical state. REQUESTED_REVISION → return to reconciliation. Approval is not inferred from silence.

## 8. Implementer
Implement exactly the approved Change Set.
May edit approved canonical documentation, add/update focused tests, and update directly affected implementation representation only when explicitly included in the change set.
May not invent methodology, resolve unresolved source conflict, broaden scope, rewrite unrelated canonical documents, or modify main/knowledgebase/.
If a new semantic issue appears: STOP and return to reconciliation.

## 9. Independent Validator
The validator receives Source Map, Contract Ledger, approved Change Set, resulting diff, and tests.
Independently check semantic correctness, source traceability, semantic ownership, boundary preservation, OHLC/OLHC determinism, regression safety, and test adequacy.
Do not treat the implementer's explanation as evidence.

## 10. Failure classification
Use exactly one primary classification per failure: SOURCE_INTERPRETATION_ERROR, CANONICAL_RULE_ERROR, IMPLEMENTATION_ERROR, TEST_ERROR, BOUNDARY_ERROR, SEMANTIC_OWNERSHIP_ERROR, DETERMINISM_ERROR, or UNRESOLVED_SOURCE_AMBIGUITY.
Return to the phase that owns the defect.

## 11. Acceptance
Complete only when source mapping is complete; canonical comparison is complete; the four open contracts are resolved; no unresolved source conflicts remain; semantic ownership is preserved; determinism checks pass; approved changes are implemented; independent validation passes; and affected tests pass.
Otherwise status is INCOMPLETE.

## 12. Stop conditions
BLOCK immediately when source branch is modified; target branch is wrong; semantic owner is unclear; source conflict cannot be reconciled; implementation would require inventing methodology; deterministic behavior cannot be established; human approval is missing; or validator cannot independently reproduce the result.