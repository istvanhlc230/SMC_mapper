---
name: smc-creator
description: Controlled source-to-canonical reconciliation workflow for evolving the existing True SMC skill from main/knowledgebase without inventing methodology.
---

# SMC Skill Creator

This skill governs controlled evolution of the existing .agents/skills/smc/ skill.

## Authority
- Source material: main/knowledgebase/
- Active development branch: docs/smc-microstructure-phase1
- Existing canonical skill: .agents/skills/smc/
- Phase 1 semantic owner: .agents/skills/smc/01_micro_structure.md
- Never modify main/knowledgebase/.

## Operating model
SOURCE MATERIAL → SOURCE ANALYSIS → CANONICAL COMPARISON → CONTRACT RECONCILIATION → HUMAN APPROVAL → IMPLEMENTATION → INDEPENDENT VALIDATION → ACCEPTANCE

## Required roles
1. Source Analyst — extracts and classifies source claims.
2. Canonical Rule Auditor — compares claims with the current semantic owner and detects conflicts and boundaries.
3. Implementer — changes only the approved change set.
4. Independent Validator — independently verifies semantic, boundary, determinism, and regression correctness.

No role may silently perform another role's decision authority.

## Phase 1 scope
Own only candle-level microstructure: Candle Extreme Breach; Candle Extreme Protection; Inside Bar; Outside Bar; Equal High (EQH); Equal Low (EQL); Equal Extreme Reference Transfer; Candle Internal Sequence; Candlestick-Based Trend.

Do not promote Structural Swing Break, BOS, CHoCH, IDM, pullback qualification, macro qualification, execution, risk, or POI logic into Layer 1.

## Mandatory invariants
- Candle Extreme Breach is not a Structural Swing Break, BOS, CHoCH, or IDM.
- Outside Bar does not determine Candle Internal Sequence by itself.
- EQH/EQL do not create IDM or structural state.
- Candle Internal Sequence does not create pullback or structural state.
- Candlestick-Based Trend is not Structural Trend.
- OHLC does not reveal whether the intrabar path was OHLC or OLHC when both are possible.
- Numerical conflicts between source transcripts must be preserved as conflicts until reconciled.
- No new canonical rule is promoted without source evidence, semantic ownership, explicit conditions, boundaries, determinism, and validation.

## Human gate
Implementation is blocked until the proposed change set is explicitly approved.
Approval states: APPROVED, REJECTED, REQUESTED_REVISION.
Unresolved source ambiguity or competing interpretations require human review.

## Required artifacts
- Source Map
- Contract Ledger
- Change Set
- Validation Report

Use the detailed workflow and artifact templates in the sibling files.