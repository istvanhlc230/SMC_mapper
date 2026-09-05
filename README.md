# SMC_mapper

Clean rebuild of the legacy `true_smc_scanner` implementation using the Antigravity development skill and the canonical True SMC methodology.

## Current status

Part 2 — project scaffold.

The implementation is intentionally built incrementally. No SMC engine logic is introduced in this scaffold.

## Architecture

```text
ai-dev-AG plugin
    = HOW TO DEVELOP

True SMC Skill
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

Every implementation change follows:

```text
INSPECT
  ↓
SMALL CHANGE
  ↓
TEST
  ↓
NEXT SMALL CHANGE
```

The legacy scanner is a behavioral baseline, not the final implementation. Canonical True SMC methodology takes precedence over accidental legacy behavior.

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
