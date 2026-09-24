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
