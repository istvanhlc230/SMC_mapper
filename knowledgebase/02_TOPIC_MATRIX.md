# TRUE SMC Topic Matrix

This is the retrieval map for the knowledgebase. The four primary source families are paired for every core methodology topic. Supplementary documents are attached where they add a narrower or updated treatment.

| Topic | TrueSMC123 | 21-Day | TrueSMC 2026 | Book | Supplementary |
|---|---|---|---|---|---|
| Candle anatomy / internal path | ✓ | ✓ | ✓ | Foundation context | is_wick_a_bos; market_structure_mapping_update |
| Valid pullback | ✓ | Day 1+ | Part 1+ | Ch.2 | smc_trader_another_missing_piece; advanced_market_structure_mapping |
| Market structure / trend | ✓ | ✓ | ✓ | Ch.2 | advanced_market_structure_mapping; market_structure_mapping_made_simple; market_structure_mapping_update |
| IDM / inducement | ✓ | ✓ | ✓ | Ch.2 | major_minor_inducement; smc_trader_missing_piece; smc_trader_another_missing_piece |
| Order Flow / Order Block | ✓ | ✓ | ✓ | Ch.2 | use_of_orderblock; use_of_orderblock_and_ordeflow |
| POI | ✓ | ✓ | ✓ | Ch.2 | How to Know When a POI Has Failed |
| Engineering Liquidity | ✓ | ✓ | ✓ | Ch.2 | smc_trader_missing_piece; smc_trader_another_missing_piece |
| BOS / CHoCH | ✓ | ✓ | ✓ | structure/entry material | is_wick_a_bos; market_structure_mapping_update |
| Rejection Block | ✓/context | ✓/context | ✓/context | execution context | How to Identify Rejection Blocks |
| Entry / execution | ✓ | ✓ | ✓ | Ch.2 | Best_Way_to_Enter_Trades_Within_the_Same_Timeframe_True_SMC; one timeframe is all you need |
| HTF → LTF | ✓ | ✓ | ✓ | Ch.2 | same-timeframe entry material |
| Countertrend | ✓ | ✓ | ✓ | Ch.2 | How_To_Trade_AGAINST_The_Trend; Learn My A+ Countertrend Setup |
| Risk management | ✓ | ✓ | ✓ | Ch.3 | everything_behind_the_trading_system |
| Stops / targets / RR | ✓ | ✓ | ✓ | Ch.3 | How to Know When a POI Has Failed |

## Primary-source pairing rule

For a core topic, read the four primary families as one comparison set:

1. TrueSMC123
2. 21-Day Bootcamp
3. TrueSMC 2026
4. Become a TRUE Forex Trader

Do not assume that the newest or shortest document automatically overrides another source. Differences must be recorded as source differences and then reconciled through the canonical .agents/skills/smc/ process.

## Retrieval order

1. Start with the relevant reference/*.md file.
2. Follow its primary-source links.
3. Consult listed supplementary files for narrower topics.
4. If implementation semantics are needed, use .agents/skills/smc/ as the canonical specification.
5. If the reference layer and a source appear inconsistent, return to the original source before changing the reference summary.

## Efficiency principle

The source corpus is more than 1.5M characters. Duplicating the full transcripts into multiple topic files would make auditing slower and create synchronization problems. This layer therefore uses topic summaries plus direct source pointers, while the original transcripts remain intact.

## Boundary

This layer does not delete or rewrite transcripts, does not treat every source statement as a universal rule, does not replace the canonical SMC skill, and does not invent missing deterministic rules.