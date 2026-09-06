# SMC_mapper — Antigravity Project Contract

## Project purpose

`SMC_mapper` is the clean rebuild of the legacy `true_smc_scanner` implementation. The implementation must follow the canonical True SMC methodology in `.agents/skills/smc/skill.md`.

## Authority hierarchy

1. `.agents/skills/smc/skill.md` — authoritative definition of True SMC behavior.
2. Existing regression tests — evidence of already-accepted behavior, unless they conflict with the canonical methodology and the task explicitly requires reconciliation.
3. Legacy `true_smc_scanner` behavior — implementation baseline/reference only; accidental legacy behavior must not redefine methodology.
4. Configuration and scoring — implementation concerns; they must not redefine structural meaning.

## Antigravity development model

This repository is operated under the reusable `ai-dev-AG` Antigravity plugin.

- `ai-dev-orchestrator` owns task lifecycle, delegation, evidence collection, external validation, correction loops, and acceptance.
- `ai-dev-implementation` owns focused production-code and test changes.
- The external validator MCP is independent validation authority and is read-only with respect to this repository.
- Runtime communication between agents uses Antigravity-native agent collaboration mechanisms. Do not use Git commits, branches, PR comments, repository files, polling, or GitHub Actions as an inter-agent message bus.
- Git/GitHub is source control and delivery infrastructure only.

## Required implementation loop

```text
INSPECT
  ↓
PLAN
  ↓
SMALL CHANGE
  ↓
TEST
  ↓
IMPLEMENTATION_READY
  ↓
INDEPENDENT VALIDATION
  ├─ PASS → ACCEPTED
  ├─ CONDITIONAL → HUMAN_REVIEW_REQUIRED
  └─ FAIL → CORRECT → TEST → VALIDATE
```

A change is not accepted merely because the implementation agent reports success. Acceptance requires a fresh independent external validation result of `PASS` when the workflow requires validation.

## SMC-specific rules

- Do not invent, generalize, or weaken True SMC structural rules.
- Treat IDM as structurally derived from a valid pullback; do not substitute arbitrary local highs/lows as IDM.
- Preserve candle-level sequencing and outside-bar inference rules defined by the canonical skill.
- Preserve lifecycle/provenance of Minor IDM, Major IDM, fallback Major IDM, BOS, CHoCH, protected/weak structure, and Trading Range state.
- When a source-code change appears to conflict with the canonical skill, stop and resolve the methodology conflict before implementation.
- Prefer the smallest change that satisfies the requested methodology and preserves unrelated accepted behavior.

## Testing and evidence

Before `IMPLEMENTATION_READY`, the implementation agent must:

1. run the narrowest relevant test(s);
2. run the regression suite when structural behavior is affected;
3. report exact commands and pass/fail evidence;
4. identify remaining risks or untested areas;
5. avoid claiming tests were run when they were not.

## Repository hygiene

Do not create compatibility layers, duplicate communication systems, orchestration databases, queues, session stores, or provider registries unless a future task explicitly requires them. Keep the mapper focused on market-structure computation and deterministic evidence production.
