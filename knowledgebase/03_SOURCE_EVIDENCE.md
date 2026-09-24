# Source Evidence Anchors

This file is the compact evidence layer for the categorized knowledgebase. It records **verified transcript anchors** from the original files without duplicating the full corpus.

## 1. Candle semantics / valid pullback

### TrueSMC123
- `true_smc123.txt`, 00:00:25–00:01:19: bullish valid pullback requires a break below the previous candle low; wick or close qualifies.
- 00:02:45–00:03:31: equal highs cause the second candle to become the active reference; its low may then be broken by wick or close.
- 00:04:49–00:05:19: candle color does not determine validity.
- 00:07:26–00:09:27: the same wick/body and reference rules are reiterated for the six scenarios.

## 2. Market structure / IDM / BOS

### TrueSMC123
- `true_smc123.txt`, Part 2 beginning 00:00:30: valid BOS is introduced after valid pullbacks and an inducement takeout; the recent pullback is the relevant reference.

### Market Structure Mapping Updated
- `market_structure_mapping_update.txt`, 00:00:21–00:02:19: consecutive valid pullbacks establish the context; the recent liquidity is inducement; once inducement is taken, the swing point is confirmed and a later break can confirm BOS.
- 00:02:54–00:05:48: inducement is tied to the recent valid pullback and can shift when a newer valid pullback forms.
- The same source distinguishes minor inducement formed before BOS from major inducement formed after BOS.

### Major vs Minor Inducement
- `major_minor_inducement.txt`, 00:00:18–00:02:01: IDM is liquidity below the recent valid pullback in bullish context and above it in bearish context.
- 00:00:42–00:01:07: IDM takeout confirms the swing point; a later break of that swing point confirms BOS.

### Order Flow / Inducement Update
- `use_of_orderblock_and_ordeflow.txt`, 00:00:14–00:01:59: major/minor IDM timing is explicitly tied to whether the valid pullback occurs after or before BOS; order flows are mapped on the impulsive move.

## 3. Wick BOS / CHoCH boundary

### Is a Wick Break a Valid BOS?
- `is_wick_a_bos.txt`, 00:01:05–00:02:34: an external high/low broken by wick can qualify as valid BOS unless the tested external level represents major inducement.
- 00:05:49–00:06:12: a wick through an external level with major-inducement provenance is treated as CHoCH in the demonstrated context.
- 00:07:21–00:08:46: a wick through a major inducement is treated as an inducement sweep rather than CHoCH.

## 4. Retracement qualification

### Market-structure missing-piece source
- `smc_trader_another_missing_piece.txt`, 00:02:00–00:02:32: the demonstrated BOS qualification uses a 50% dealing-range retracement after IDM takeout.
- This source therefore supports the 50% normal-path evidence recorded in `reference/03_pullback_retracement.md`.
- Any 38.2% exception remains governed by the canonical skill owner rather than being inferred from this single example.

## 5. POI / Order Block / Rejection Block

### Rejection Block
- `How to Identify Rejection Blocks.txt`, 00:00:23–00:01:54: the rejection block is the wick of the candle that takes the prior candle extreme; it is described as part of an order block in the demonstrated setup, but not identical to the whole order block.
- 00:02:06–00:03:07: the rejection block is demonstrated at the extreme/origin of the dealing range.

### POI failure
- `How to Know When a POI Has Failed.txt`, 00:00:24–00:02:31: HTF POI interaction is followed by LTF structure analysis; the example distinguishes mitigated/available POIs and identifies a decisional order block by the break it caused.

### Decisional Order Block update
- `use_of_orderblock.txt`, 00:02:24 onward: the source explicitly describes an updated treatment of the decisional order block after IDM takeout. This must be read with the later canonical reconciliation rather than copied as an independent implementation rule.

## 6. Execution / same-timeframe

### Same-timeframe entry
- `Best_Way_to_Enter_Trades_Within_the_Same_Timeframe_True_SMC.md`, 00:00–01:48: the source presents same-timeframe execution after POI mitigation and discusses the limitations of entering solely from a reversal pattern.
- `one timeframe is all you need.txt`, 00:00–02:41: one-timeframe execution is demonstrated; the example uses IDM/POI/engineering-liquidity context and a confirmation candle.

## 7. Multi-timeframe / countertrend

### Countertrend
- `How_To_Trade_AGAINST_The_Trend.md`, 00:00–01:40: a countertrend setup is introduced from an HTF structure break followed by retracement; the source explicitly treats this as a separate countertrend route.

## 8. Risk / trading policy

### Trading system
- `everything_behind_the_trading_system.txt`, 00:01:20–00:03:08: the author presents fixed per-position risk, maximum concurrent/session exposure and a maximum daily loss as his own trading-system policy.
- 00:03:08 onward: the source describes a top-down timeframe route and named entry modules.

**Important:** These numerical risk values are source-specific trading-policy examples. They are not promoted here to universal SMC constants.

## Evidence-handling rule

These anchors are evidence pointers, not a replacement for the original transcripts. Where a source example conflicts with or is less precise than the canonical `.agents/skills/smc/` specification, the skill remains authoritative for implementation.

The categorized reference files should summarize and cross-link evidence; they must not silently convert an example into a universal deterministic rule.
