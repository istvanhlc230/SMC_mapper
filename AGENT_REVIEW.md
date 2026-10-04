# AGENT_REVIEW.md

Status: FIXED_CI_PENDING_LIVE_SMOKE

## Change
The Windows live smoke showed that ForexFactory acquisition succeeds, but most events persisted
with `impact=UNKNOWN`. After the first normalization fix, one real HIGH event was correctly
classified, proving the normalizer was active.

Root cause of the remaining issue: the actual structured ForexFactory event objects expose
`impactTitle` (for example `High Impact Expected` / `Low Impact Expected`) and compact
`impactClass` icon forms such as `icon--ff-impact-yel`. The implementation previously looked
for `impactName` first and did not recognize these actual fields/forms.

Calendar implementation version: 2.2.8
Persistent schema: 2

The fix:
- reads explicit `impactTitle` first, with `impactName` and direct `impact` as compatibility forms;
- recognizes explicit color/icon impactClass tokens, including the short provider forms;
- never infers impact from event title or other unrelated data.

## Validation
Regression tests cover:
- impactTitle: High, Med, Low, Non-Economic;
- impactName compatibility forms;
- impactClass color/icon forms, including `icon--ff-impact-yel`;
- existing rendered HTML impact parsing.

A fresh CI result and a clean Windows live smoke remain required. The live smoke must explicitly
remove the existing COMPLETE coverage before reacquiring the same interval, because Calendar
intentionally does not refetch already complete coverage.

Acceptance target: real ForexFactory events persist explicit HIGH/MEDIUM/LOW/HOLIDAY values instead
of UNKNOWN whenever the provider supplies explicit impact metadata.
