# AGENT_REVIEW.md

Status: FIXED_CI_PENDING_LIVE_SMOKE

## Change
The Windows live smoke showed ForexFactory events successfully acquired for
2026.10.04-2026.10.30, but the persisted FF impact field remained UNKNOWN.

Root cause: the normal acquisition path uses the structured ForexFactory `days` payload.
The previous normalizer expected exact canonical `impactName` tokens, while the provider can supply
descriptive impactName labels such as `High Impact Expected` and `Med Impact Expected`, plus
provider-specific impactClass color/icon representations.

Calendar implementation version: 2.2.7
Persistent schema: 2

The fix normalizes explicit ForexFactory `impactName`, `impactClass`, and direct `impact` values
to HIGH/MEDIUM/LOW/HOLIDAY. Severity is never inferred from event titles or unrelated fields.

The rendered HTML fallback remains separately covered.

## Validation
Deterministic regression tests now cover:
- High/Med/Medium/Low/Non-Economic impactName forms;
- red/orange/yellow/green/grey impactClass forms;
- existing rendered HTML HIGH/MEDIUM impact parsing.

A fresh CI run is required. After CI succeeds, repeat the Windows live query against the same
interval only after explicitly deleting/resetting the existing COMPLETE coverage, because cached
coverage is intentionally not refetched automatically.

Acceptance target: real ForexFactory events persist known HIGH/MEDIUM/LOW/HOLIDAY values rather than
UNKNOWN whenever ForexFactory supplies explicit impact metadata.
