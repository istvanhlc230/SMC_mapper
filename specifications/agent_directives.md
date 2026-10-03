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

- `ai-dev-orchestrator` owns task lifecycle, delegation, evidence collection, validation gatekeeping, correction loops, and acceptance.
- `ai-dev-implementation` owns focused production-code and test changes via native `invoke_subagent`.
- `ai-dev-validator` is an independent, read-only validation subagent invoked via native `invoke_subagent` without write or execution tools.
- Validation results are parsed and enforced by `validator_contract.py` and `workflow_guard.py`.
- Validation is independent of the implementation agent's self-assessment; implementation claims never constitute acceptance.
- The validation token is an internal control-plane credential: never passed to the validator prompt, never recorded in validator transcripts, and redacted from reports.
- Timeout, crash, or malformed validator output is fail-safe and never yields `PASS`.
- Terminal escalation (`HUMAN_REVIEW_REQUIRED`) halts automated correction loops.
- Runtime communication between agents uses Antigravity-native agent collaboration mechanisms (`invoke_subagent`, `send_message`). Do not use Git commits, branches, PR comments, repository files, polling, or GitHub Actions as an inter-agent message bus.
- Git/GitHub is source control and delivery infrastructure only.


## Required script design before implementation

For every new script and every substantial modification to an existing script, the developer agent must design the script's operation before writing the implementation.

The design step must, at minimum:

1. identify the script's responsibility, inputs, outputs, side effects, dependencies, and ownership boundaries;
2. describe the main execution flow and important state transitions;
3. create a compact UML-style design when it materially improves clarity. Use the appropriate diagram for the problem, such as:
   - sequence diagram for process/API interaction;
   - state diagram for lifecycle/state-machine behavior;
   - class/data model diagram for domain structures;
   - activity/flow diagram for algorithmic control flow.
   A concise textual design is acceptable when a diagram would add no useful information, but the design must still be explicit and reviewable;
4. define the domain variables, interfaces, classes/types, and functions that the implementation will use;
5. document each defined variable, interface, class/type, and function briefly in clear language, including its responsibility and important inputs/outputs;
6. verify naming, ownership, portability, and dependency direction against the owning specification before implementation starts;
7. keep the design synchronized with the implementation. When implementation changes materially, update the affected design documentation rather than allowing the documented design to become stale.

The design artifacts must be concise and implementation-oriented. Do not create diagrams or documentation merely for appearance; every artifact must help verify behavior, data ownership, interfaces, or state transitions before code is written.

## Local/online repository synchronization

The online GitHub repository is the authoritative shared repository state for development handoff.

Before starting each implementation, correction, review-follow-up, or validation iteration, the developer agent must synchronize its local checkout with the current remote state so that it does not work from a stale snapshot.

- First verify the working tree state and preserve any legitimate uncommitted work.
- When the working tree is clean, pull the current target branch before beginning the iteration (prefer fast-forward-only synchronization).
- When uncommitted work exists, do not discard it and do not blindly overwrite it; first reconcile the local state with the remote changes, then continue.
- Any file modified externally in the online repository by the auditor/orchestrator must therefore be pulled into the local checkout before implementation continues.
- Treat the following as the minimum handoff rule: **online change → commit on remote → developer pulls → local implementation continues**.
- After implementation, the developer agent must commit and push the resulting synchronized snapshot, including `AGENT_REVIEW.md` when that file is part of the same iteration's deliverables.

This rule exists to prevent divergence between the online repository audited by the auditor and the offline/local repository used by the developer agent.

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

Safety limits are strictly enforced:
- `MAX_CORRECTIONS = 3`
- `MAX_WORKFLOW_TIME = 900`
- `MAX_VALIDATOR_TIME = 300`
- `MAX_IDENTICAL_FAILURES = 2`

## SMC-specific rules

- Do not invent, generalize, or weaken True SMC structural rules.
- Treat IDM as structurally derived from a valid pullback; do not substitute arbitrary local highs/lows as IDM.
- Preserve candle-level sequencing and outside-bar inference rules defined by the canonical skill.
- Preserve lifecycle/provenance of Minor IDM, Major IDM, BOS, CHoCH, protected/weak structure, and Trading Range state.
- When a source-code change appears to conflict with the canonical skill, stop and resolve the methodology conflict before implementation.
- Prefer the smallest change that satisfies the requested methodology and preserves unrelated accepted behavior.

## Developer-agent coding and prompt discipline

The active developer agent must use:

- descriptive, semantically meaningful variable names;
- descriptive interface, class, type, and function names that reveal their responsibility;
- stable domain terminology consistent with the owning specification;
- explicit state fields and explicit ownership rather than opaque dictionaries or positional tuples for domain state;
- no cryptic abbreviations except universally conventional local names whose meaning is immediate.

Python-specific convenience is allowed internally, but domain data structures and public contracts must remain directly portable to MQL4/MQL5-style statically structured code. Do not make correctness depend on Python-only reflection, generators, dynamic attributes, properties, metaclasses, or advanced container semantics that cannot be represented naturally in the target language.

Developer-agent prompts are a scarce resource and must be optimized. The orchestrating/auditing agent must issue one consolidated prompt per implementation iteration whenever the issues are related. Prompts to the developer agent should be in English. Each prompt should contain only the necessary context: exact scope, affected files/sections, concrete changes, acceptance criteria, and the required test command. Reference existing specifications by exact file/section instead of copying large unchanged text into the prompt. Do not issue multiple overlapping prompts that restate the same context. New findings discovered during one audit iteration should be accumulated into the next single corrective prompt unless separation is required by independent ownership or safety boundaries.

## Testing and evidence

Before `IMPLEMENTATION_READY`, the implementation agent must:

1. run the narrowest relevant validation command;
2. run the relevant regression/verification suite when one exists and the task requires it;
3. report exact commands and pass/fail evidence;
4. identify remaining risks or unverified areas;
5. avoid claiming validation was performed when it was not.

## Repository hygiene

Do not create compatibility layers, duplicate communication systems, orchestration databases, queues, session stores, or provider registries unless a future task explicitly requires them. Keep the mapper focused on market-structure computation and deterministic evidence production.



### Temporary development artifacts

The repository root must not be used as scratch space.

All temporary, intermediate, debug, generated, downloaded, or otherwise non-source development artifacts created during implementation or testing must be placed under:

```text
dev_tmp/
```

This includes, for example:

- temporary JSON/HTML/XML payloads;
- downloaded provider responses;
- debug dumps and ad-hoc logs;
- intermediate generated files;
- scratch scripts or one-off helper files;
- temporary patches or analysis outputs;
- temporary local fixtures used only during development.

Keep permanent source code, required design/specification files, and other intentional repository artifacts in their defined locations. Do not leave temporary artifacts scattered through the repository root or unrelated source directories.

The `dev_tmp/` directory is development scratch space only and must not become a substitute for required source or documentation locations. Do not treat files under `dev_tmp/` as implementation deliverables unless the owning task explicitly promotes a file into a permanent repository location.

## Canonical Order Flow / Order Block terminology

Use these exact canonical semantic identifiers in active implementation and specifications:

```
ORDER_FLOW_CANDIDATE
ELIGIBLE_ORDER_FLOW
DECISIONAL_ORDER_FLOW
EXTREME_ORDER_FLOW

ORDER_BLOCK_CANDIDATE
VALIDATED_ORDER_BLOCK
DECISIONAL_ORDER_BLOCK
EXTREME_ORDER_BLOCK
ORIGIN_ORDER_BLOCK
```

Do not introduce abbreviated aliases such as OF_CONFIRMED, VALID_OB, OF_CANDIDATE, DECISIONAL_OF, EXTREME_OF, DECISIONAL_OB, EXTREME_OB, ORIGIN_OB, or ORIGIN_RESERVE. Rejection Block remains a separate execution/PD-array concept.
