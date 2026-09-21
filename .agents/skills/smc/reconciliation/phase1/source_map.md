# Phase 1 Source Map — Initial Reconciliation Run

Status: **ANALYSIS COMPLETE / NO CANONICAL CHANGE APPROVED**

## Scope
Phase 1 concepts: Candle Extreme Breach, Candle Extreme Protection, Inside Bar, Outside Bar, EQH, EQL, Equal Extreme Reference Transfer, Candle Internal Sequence, Candlestick-Based Trend.

## Sources inspected

| Source | Relevant finding | Phase 1 classification |
|---|---|---|
| `advanced_market_structure_mapping.txt` | Discusses inducement, valid pullback, BOS, timeframe hierarchy, order flow, POIs and execution examples. | OUT_OF_SCOPE for Phase 1 semantic definitions |
| `is_wick_a_bos.txt` | States that a wick break of an external high/low can qualify as structural break unless that extreme is a major inducement; discusses BOS/CHoCH conditions. | OUT_OF_SCOPE / boundary evidence |
| `major_minor_inducement.txt` | Defines IDM around recently formed valid pullbacks and major/minor inducement. | OUT_OF_SCOPE / boundary evidence |
| `market_structure_mapping_made_simple.txt` | Source material contains valid-pullback, inducement and structure mapping explanations. | OUT_OF_SCOPE / boundary evidence |
| `market_structure_mapping_update.txt` | Source material contains market-structure qualification/update rules. | OUT_OF_SCOPE / boundary evidence |
| `smc_trader_missing_piece.txt` | Contains structural mapping and retracement qualification material. | OUT_OF_SCOPE / boundary evidence |
| `smc_trader_another_missing_piece.txt` | Contains BOS qualification, 50% baseline and 38.2% higher-timeframe exception. | OUT_OF_SCOPE / boundary evidence; conflict candidate for higher-layer methodology |

## Direct Phase 1 evidence

No inspected knowledgebase passage supplied a deterministic definition for C1–C3 (candle extreme breach/protection, equal-extreme transfer, or OHLC/OLHC internal sequence).

The inspected sources also did not provide a sufficiently explicit Phase 1 canonical definition for C4. Reversal-pattern language appears in higher-layer execution/structure contexts and must not be promoted into Layer 1.

## Important source conflict captured

`smc_trader_another_missing_piece.txt` presents 50% as the normal deep-retracement criterion and 38.2% as an exception when a higher-timeframe valid pullback corresponds to lower-timeframe complete structure. `advanced_market_structure_mapping.txt` uses at least 38.2% in its BOS qualification discussion.

This is **not a Phase 1 candle-level rule**. It remains a higher-layer reconciliation item and must not be copied into `01_micro_structure.md`.

## Negative evidence rule

Absence of a Phase 1 definition in the inspected transcripts is not evidence that the canonical rule is wrong. It means the source set inspected here does not independently establish that rule.
