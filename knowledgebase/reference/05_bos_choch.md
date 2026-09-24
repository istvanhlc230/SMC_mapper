# BOS and CHoCH

## Primary paired sources

- ../true_smc123.txt
- ../true_smc_21dayBootCamp.txt
- ../truesmc2026.txt
- ../Become-a-TRUE-Forex-Trader-Become-a-TRUE-Forex-Trader_text_format.txt

## Supplementary sources

- ../is_wick_a_bos.txt
- ../advanced_market_structure_mapping.txt
- ../market_structure_mapping_update.txt
- ../Best_Way_to_Enter_Trades_Within_the_Same_Timeframe_True_SMC.md
- ../How to Know When a POI Has Failed.txt

## Current reconciled boundaries

BOS and CHoCH classification are distinct from lower-level candle observations and from execution authorization.

A wick-path CHoCH may be eligible when an external wick breaks the tested external level, except where that tested external level has Major IDM provenance. A Major IDM wick takeout is excluded from CHoCH.

POI failure consumes canonical CHoCH/control-shift confirmation rather than treating any generic BOS-or-CHoCH label as sufficient.

## LTF route

The source corpus describes an HTF POI or core-liquidity interaction followed by LTF execution. The recently formed relevant LTF valid-pullback or inducement reference becomes important for the lower-timeframe confirmation route.

The canonical deterministic form lives in .agents/skills/smc/.
