# TRUE SMC — RULE MIGRATION AUDIT

**Status:** Rule-level migration audit completed against `.agents/skills/smc/skill_old.md`.

**Baseline:** `skill_old.md` preserves the original pre-reorganization ruleset and remains immutable during this audit.

## Audit rule

Every original section must have an explicit destination in the new category model. A section may be split across categories where its content has different authority types, but no rule may be silently dropped, weakened, or converted into an optional behavior.

## Section mapping

| Original section | Primary destination | Secondary/reference destination | Status |
|---:|---|---|---|
| 1 | `true_smc_canonical.md` | `skill.md` | PASS |
| 2 | `true_smc_canonical.md` | `skill.md` | PASS |
| 3 | `true_smc_canonical.md` | `skill.md` | PASS |
| 4 | `true_smc_canonical.md` | `CATEGORY_MAP.md` | PASS |
| 5 | `true_smc_canonical.md` | `CATEGORY_MAP.md` | PASS |
| 6 | `true_smc_canonical.md` | `CATEGORY_MAP.md` | PASS |
| 7 | `true_smc_canonical.md` | `CATEGORY_MAP.md` | PASS |
| 8 | `true_smc_canonical.md` | `CATEGORY_MAP.md` | PASS |
| 9 | `true_smc_canonical.md` | `methodology_parameters.md` | PASS |
| 10 | `true_smc_canonical.md` | `CATEGORY_MAP.md` | PASS |
| 11 | `true_smc_canonical.md` | `standard_smc.md` | PASS |
| 12 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 13 | `true_smc_canonical.md` | `CATEGORY_MAP.md` | PASS |
| 14 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 15 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 16 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 17 | `true_smc_canonical.md` | `standard_smc.md` | PASS |
| 18 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 19 | `true_smc_canonical.md` | `methodology_parameters.md` | PASS |
| 20 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 21 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 22 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 23 | `deprecated.md` | `true_smc_canonical.md` | PASS |
| 24 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 25 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 26 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 27 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 28 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 29 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 30 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 31 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 32 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 33 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 34 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 35 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 36 | `execution.md` | `CATEGORY_MAP.md` | PASS |
| 37 | `execution.md` | `CATEGORY_MAP.md` | PASS |
| 38 | `execution.md` | `unverified.md` | PASS |
| 39 | `execution.md` | `standard_smc.md` | PASS |
| 40 | `execution.md` | `implementation.md` | PASS |
| 41 | `execution.md` + `risk.md` | `skill.md` | PASS |
| 42 | `true_smc_canonical.md` | `implementation.md` | PASS |
| 43 | `deprecated.md` | `methodology_parameters.md` | PASS |
| 44 | `risk.md` | `CATEGORY_MAP.md` | PASS |
| 45 | `implementation.md` | `skill.md` | PASS |
| 46 | `implementation.md` | `skill.md` | PASS |
| 47 | `implementation.md` | `CATEGORY_MAP.md` | PASS |
| 48 | `implementation.md` | test contract | PASS |
| 49 | `true_smc_canonical.md` | `skill.md` | PASS |

## Special classification cases

### Section 9 — structural retracement

The structural rule remains in `true_smc_canonical.md`. Numeric/configurable parameter semantics are additionally isolated in `methodology_parameters.md`. The parameter file does not redefine the structural rule.

### Section 41 — execution/risk boundary

The original section contains both execution-separation and risk/RR rules. Its execution portion is represented in `execution.md`; its risk boundary is represented in `risk.md`. No rule is removed by this split.

### Section 43 — obsolete retracement variant

The historical rule is represented in `deprecated.md`; parameter-facing handling is referenced from `methodology_parameters.md`. It remains explicitly non-canonical.

## Integrity checks

- Original baseline retained: YES
- Original `skill.md` ruleset deleted: NO
- Original rules silently weakened: NO identified
- Sections 1–49 represented: YES
- Canonical structural rules separated from execution/risk: YES
- Parameters separated from semantic object definitions: YES
- Implementation contract separated from methodology: YES
- Deprecated behavior explicitly isolated: YES
- Unverified claims explicitly isolated: YES
- Generic SMC terminology prevented from overriding True SMC: YES
- `mapper` used as the new canonical implementation term: YES in the new master/category architecture

## Remaining known issue

`CATEGORY_MAP.md` is a classification ledger rather than a verbatim copy of every rule. It is therefore not used as the completeness source. `skill_old.md` remains the preservation baseline and the category documents are the authoritative organized views.

## Acceptance decision

**MIGRATION STRUCTURE: ACCEPTED**

The original 49-section ruleset has an explicit destination in the new architecture. The baseline must remain until implementation-level regression validation is also completed against the reorganized skill structure.
