# SMC_mapper

Clean rebuild of the legacy `true_smc_scanner` implementation using the reusable `ai-dev-AG` development plugin and the canonical True SMC methodology.

## Current status

Part 2 — project scaffold and structural engine foundation.

The repository now contains the clean-rebuild engine, data-provider abstraction, regression suite, and the project-specific True SMC methodology skill. Further work is incremental and methodology-driven.

## Architecture

```text
ai-dev-AG plugin
    = HOW TO DEVELOP

True SMC Skill (`.agents/skills/smc`)
    = WHAT TRUE SMC IS

old true_smc_scanner.py
    = IMPLEMENTATION BASELINE

test_smc.py
    = REGRESSION BASELINE

data_provider.py
    = DATA LAYER

SMC_mapper.py
    = CLEAN REBUILD
```

## Development contract

The generic development workflow is supplied by the reusable `ai-dev-AG` Antigravity plugin. This repository keeps only the project-specific `smc` skill locally.

Every implementation change follows:

```text
INSPECT
  ↓
SMALL CHANGE
  ↓
TEST
  ↓
NEXT SMALL CHANGE
  ↓
REVIEW
```

The legacy scanner is a behavioral baseline, not the final implementation. Canonical True SMC methodology takes precedence over accidental legacy behavior.

## Skill separation

- `ai-dev-AG` defines **HOW** development work is performed.
- `.agents/skills/smc/SKILL.md` defines **WHAT** canonical True SMC means.
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
