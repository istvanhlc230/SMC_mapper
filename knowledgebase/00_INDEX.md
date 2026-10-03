# TRUE SMC Knowledgebase Index

The original knowledgebase files remain the **source-evidence corpus**. The categorized layer groups related material so the four primary source families and supplementary material can be compared efficiently without duplicating the full transcripts.

## Source hierarchy

1. `knowledgebase/` — original source evidence.
2. `knowledgebase/reference/` — categorized retrieval and reconciliation notes.
3. `knowledgebase/03_SOURCE_EVIDENCE.md` — verified timestamped evidence anchors.
4. `.agents/skills/smc/` — canonical implementation authority.

The knowledgebase does not override the canonical skill.

## Primary source families

Every core topic should be compared across:

- `true_smc123.txt`
- `true_smc_21dayBootCamp.txt`
- `truesmc2026.txt`
- `Become-a-TRUE-Forex-Trader-Become-a-TRUE-Forex-Trader_text_format.txt`

## Categorized reference map

- `01_source_catalog.md` — source inventory and classification.
- `02_TOPIC_MATRIX.md` — topic → primary families → supplementary mapping.
- `03_SOURCE_EVIDENCE.md` — verified source/timestamp evidence anchors.
- `reference/01_candle_semantics.md` — candle semantics.
- `reference/02_market_structure.md` — market structure.
- `reference/03_pullback_retracement.md` — pullback/retracement.
- `reference/04_idm_inducement_liquidity.md` — IDM/inducement/liquidity.
- `reference/05_bos_choch.md` — BOS/CHoCH.
- `reference/06_poi_ob_fvg_rejection.md` — POI/OB/FVG/Rejection Block.
- `reference/07_execution_entries.md` — execution/entries.
- `reference/08_risk_targets_policy.md` — risk/stops/targets/policy.
- `reference/09_multitimeframe_countertrend.md` — HTF/LTF/countertrend.

## Retrieval workflow

1. Start with the relevant categorized reference.
2. Check `03_SOURCE_EVIDENCE.md` for verified anchors.
3. Compare the four primary source families.
4. Read listed supplementary material for narrower or updated treatments.
5. For implementation semantics, use `.agents/skills/smc/` as the authority.
6. If a discrepancy remains, return to the original source; do not invent a rule.

## Design rule

**Define once at semantic owner → downstream reference → downstream consumption.**

The categorized layer is a retrieval/evidence aid, not a second canonical specification. It must not introduce synthetic evidence, implementation-only state, or fallback rules that are absent from the canonical skill.


## Project-canonical resolution of the First-BOS baseline gap

The source corpus does not provide a deterministic first-BOS retracement baseline. The project therefore defines an isolated Bootstrap Initialization process to supply the required measurement context without fabricating a normal Dealing Range or Protected Structural Extreme.

- Canonical semantic owner: `.agents/skills/smc/03_structural_semantic_authority.md`
- Canonical implementation representation: `.agents/skills/smc/08_implementation.md`
- Source evidence remains historical evidence only; the bootstrap process is a project-canonical resolution, not a transcript quotation.
- Implementation-facing terminology: `E_retrace(t)` = `dynamic_retracement_extreme` until it is locked as `PROTECTED_STRUCTURAL_EXTREME` at the actual `VALID_BOS` candle.


## 10. Project-canonical divergence ledger for future audits

The following items are intentionally **not source-corpus rewrites**. They record project-canonical resolutions that differ from, refine, or formalize wording found in the indexed source material. During future audits, these must not be reported as unexplained knowledgebase-vs-skill contradictions.

### IDM takeout vs. structural swing confirmation

Some source transcripts use language such as “IDM takeout confirms/acquires the swing point.” This is retained as **source terminology**.

The current project-canonical state machine deliberately represents the lifecycle as:

```text
IDM_TAKEN
→ SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME
→ applicable STRUCTURAL_RETRACEMENT_QUALIFICATION
→ CONFIRMED_STRUCTURAL_SWING
```

Therefore, a source statement that uses “confirmed swing” immediately after IDM takeout must not be translated into a direct project-canonical `IDM_TAKEN → CONFIRMED_STRUCTURAL_SWING` transition.

### First-BOS bootstrap

The source corpus does not deterministically define the first-BOS retracement baseline. `BOOTSTRAP_ORIGIN_ANCHOR` and the transient `BOOTSTRAP_RANGE` are **project-canonical resolutions**, not source quotations.

The bootstrap anchor is initialization evidence only. It is not a Protected Structural Extreme, governing Dealing Range boundary, BOS reference, or ordinary CHoCH reference. The first canonical Protected Structural Extreme is locked from the live `dynamic_retracement_extreme` at `VALID_BOS`.

### Order Block Inside-Bar exclusion

The project has an explicit canonical rule that a strict `Inside Bar` is **excluded from Order Block candidate selection**. It cannot become an `ORDER_BLOCK_CANDIDATE`, `VALIDATED_ORDER_BLOCK`, Decisional OB, or Extreme OB, and mother-candle OB provenance is not transferred into it.

This is a project-canonical selection rule. It must not be invented retroactively as a universal transcript quotation merely because source material discusses Inside Bars in other candle/pullback contexts.

### Order Block FVG fallback

Source wording may describe advancing to the “next eligible” candle when the required FVG association is missing. The project-canonical deterministic resolution is the **immediately next chronological candle**, followed by independent re-evaluation. No arbitrary forward skipping is permitted.

### Audit precedence

For future reconciliation:

```text
ORIGINAL SOURCE
    ↓
SOURCE EVIDENCE / REFERENCE NOTES
    ↓
PROJECT-CANONICAL RESOLUTION RECORDED HERE
    ↓
.agents/skills/smc/  ← implementation authority
```

When one of the above canonical resolutions is encountered, auditors should verify that the distinction is preserved rather than treating the canonical resolution itself as a contradiction to the unchanged source corpus.
