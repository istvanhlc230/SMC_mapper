# SMC_mapper

Clean rebuild of the legacy `true_smc_scanner` implementation using the reusable `ai-dev-AG` development plugin and the canonical True SMC methodology.

## Current status

Part 2 — project scaffold and structural engine foundation.

The repository contains the clean-rebuild engine, data-provider abstraction, regression suite, and the project-specific True SMC methodology skill. Further work is incremental and methodology-driven.

## Architecture

```text
ai-dev-AG plugin
    = HOW TO DEVELOP

True SMC Skill (`.agents/skills/smc`)
    = WHAT TRUE SMC IS

AGENTS.md
    = PROJECT-SPECIFIC ANTIGRAVITY CONTRACT

old true_smc_scanner.py
    = IMPLEMENTATION BASELINE

test_smc.py
    = REGRESSION BASELINE

data_provider.py
    = DATA LAYER

SMC_mapper.py
    = CLEAN REBUILD
```

## Antigravity control-plane model

The repository is designed to be operated by the native Antigravity `ai-dev-AG` plugin. The plugin owns orchestration and runtime agent communication; this repository supplies project-specific methodology, implementation, tests, and evidence.

```text
Antigravity orchestrator
        │
        ├── invoke_subagent
        ▼
ai-dev-implementation
        │
        ├── inspect
        ├── smallest implementation change
        └── run tests
        │
        ▼
IMPLEMENTATION_READY
        │
        ▼
external-validator MCP
        │
        ▼
PASS / CONDITIONAL / FAIL
        │
        ├── PASS → ACCEPTED
        ├── CONDITIONAL → HUMAN REVIEW
        └── FAIL → CORRECT → TEST → VALIDATE
```

Runtime communication is intentionally not implemented through GitHub commits, branches, PR comments, repository files, polling, or GitHub Actions. Git/GitHub is source control and delivery infrastructure only. The external validator is an independent validation authority and does not own repository changes.

## Development contract

The generic development workflow is supplied by the reusable `ai-dev-AG` Antigravity plugin. The repository keeps project-specific constraints in `AGENTS.md` and the canonical `smc` skill in `.agents/skills/smc/skill.md`.

Every implementation change follows:

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
```

Acceptance requires a fresh external `PASS` whenever the task is subject to the validation gate. An implementation agent's own assessment is never the acceptance authority.

## Skill separation

- `ai-dev-AG` defines **HOW** development work is performed.
- `AGENTS.md` defines **HOW THIS PROJECT** is operated under Antigravity.
- `.agents/skills/smc/skill.md` defines **WHAT** canonical True SMC means.
- The implementation must reconcile behavior against the SMC skill rather than inventing domain rules.

`true-smc` is reference material only and is not the active development target.

## Configuration

`config.json` contains non-secret runtime configuration only. External provider credentials must be supplied through environment variables or a local `.env` file. A safe template is provided as `config.example.json`.

## Planned build order

1. Project scaffold
2. Canonical data/state model
3. Candle-level pullback engine
4. Structural qualification
5. Minor IDM lifecycle
6. Swing confirmation
7. BOS
8. CHoCH + Trading Range
9. Major / Fallback IDM
10. POI / execution
11. Scoring
12. Regression reconciliation
13. Final review
