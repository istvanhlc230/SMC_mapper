# Phase 1 Source Map — Targeted C1–C4 Investigation

Status: **SOURCE INVESTIGATION COMPLETE / C1–C5 IMPLEMENTATION ALIGNED**

## Scope
Phase 1 concepts: Candle Extreme Breach, Candle Extreme Protection, Inside Bar, Outside Bar, EQH, EQL, Equal Extreme Reference Transfer, Candle Internal Sequence, Candlestick-Based Trend.

## Targeted sources inspected

The second pass extended the initial seven-file review to the remaining known knowledgebase transcripts:

- `true_smc123.txt`
- `true_smc_21dayBootCamp.txt`
- `truesmc2026.txt`
- `everything_behind_the_trading_system.txt`
- `use_of_orderblock.txt`
- `use_of_orderblock_and_ordeflow.txt`

## Source-backed findings

| Contract / concept | Source | Direct evidence | Classification |
|---|---|---|---|
| C1 — Candle Extreme Breach | `true_smc123.txt` | Valid pullback qualification explicitly accepts a break of the previous candle extreme by **wick or candle close**; candle color does not matter. | DIRECT SOURCE EVIDENCE |
| C1 — Candle Extreme Protection | `true_smc_21dayBootCamp.txt`, `truesmc2026.txt` | Bullish candle-level sequence breaks the previous bullish candle high while protecting its low; bearish sequence is the inverse. | DIRECT SOURCE EVIDENCE |
| C2 — Equal Extreme Reference Transfer | `true_smc123.txt`, `true_smc_21dayBootCamp.txt` | When consecutive relevant highs/lows are equal, the source explicitly says to ignore the first candle and use the **second candle** as the active reference. | DIRECT SOURCE EVIDENCE |
| C2 — Protection after transfer | `true_smc_21dayBootCamp.txt` | After equal lows, the second candle's high becomes the protected reference in the bearish example. | DIRECT SOURCE EVIDENCE |
| C3 — Candle Internal Sequence | `truesmc2026.txt` | The source explains bullish candle formation as Open → Low → High → Close and bearish candle formation as Open → High → Low → Close. | DIRECT SOURCE EVIDENCE, methodology model |
| C3 — Outside Bar-specific sequence | All targeted files | No sufficiently explicit statement was found that names an Outside Bar and independently specifies its intrabar sequence. | PARTIAL / UNRESOLVED |
| C4 — Reversal formation boundary | `true_smc_21dayBootCamp.txt`, `truesmc2026.txt` | Reversal patterns (e.g. pin bars / morning-evening star) are discussed as reversal/trade observations, while structure qualification remains a separate process. | BOUNDARY EVIDENCE |
| C4 — deterministic Layer 1 anatomy | All targeted files | No complete deterministic canonical predicate set for all listed reversal observations was found. | UNRESOLVED |

## Additional source evidence

`truesmc2026.txt` also states that an Inside Bar receives little separate attention in the valid-pullback explanation and that the mother candle is used for the relevant interpretation. This supports keeping Inside Bar distinct rather than promoting it to a structural event.

The source material continues to distinguish valid pullback / BOS / inducement / order-flow concepts from candle-level observations. These remain higher-layer concepts.

## Important higher-layer conflict

`smc_trader_another_missing_piece.txt` presents 50% as the normal deep-retracement criterion and 38.2% as an exception when a higher-timeframe valid pullback corresponds to lower-timeframe complete structure. `advanced_market_structure_mapping.txt` also uses at least 38.2% in BOS qualification.

This remains a **higher-layer** reconciliation item. It must not be copied into `01_micro_structure.md`.

## Interpretation rule

The targeted investigation found real source evidence for C1, C2, and the general candle-path model underlying C3. That evidence is **supporting evidence for the existing canonical Layer 1 definitions**, not automatic authorization to change them.

Absence of an explicit Outside-Bar sequence contract and absence of a complete deterministic reversal-anatomy contract mean C3 and C4 cannot be declared fully closed.

## Implementation alignment

The approved C1–C5 interpretation has now been reflected in the canonical documents and implementation boundary. Source material remains unchanged.

## Negative evidence rule

Absence of a Phase 1 definition in a transcript is not evidence that the canonical rule is wrong. It means the inspected source set does not independently establish that rule.
