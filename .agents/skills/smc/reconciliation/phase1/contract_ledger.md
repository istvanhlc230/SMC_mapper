# Phase 1 Contract Ledger — Targeted C1–C4 Investigation

Status: **SOURCE EVIDENCE FOUND / CANONICAL ALIGNMENT REVIEW REQUIRED**

| Contract | Status | Source evidence | Current canonical alignment | Required next step |
|---|---|---|---|---|
| C1 — Candle Extreme Breach deterministic OHLC model | EVIDENCE FOUND / OPEN | `true_smc123.txt` states that the relevant previous candle extreme may be broken by wick or candle close; candle color does not matter. | Existing `01_micro_structure.md` defines wick/body breach modes and keeps the event separate from BOS/CHoCH/IDM. | Human approval to mark the contract closed against this source-backed interpretation, or request refinement of the breach predicate wording. |
| C2 — Candle Extreme Protection + Equal Extreme Reference Transfer | EVIDENCE FOUND / OPEN | `true_smc123.txt` and `true_smc_21dayBootCamp.txt` explicitly select the second candle when equal highs/lows occur; the second candle's opposite extreme becomes the applicable protected reference. | Existing `01_micro_structure.md` already defines second-candle reference transfer and keeps it separate from pullback/swing formation. | Human approval to close the contract as source-aligned. |
| C3 — Outside Bar internal sequence / state transition | PARTIAL EVIDENCE / OPEN | `truesmc2026.txt` provides the source's candle-path model: bullish O→L→H→C; bearish O→H→L→C. No explicit Outside-Bar-specific sequence contract was found. | Existing canonical rule correctly separates Outside Bar from Candle Internal Sequence and represents LOW→HIGH / HIGH→LOW without manufacturing structural events. | Decide whether the source candle-path model is authoritative enough to close C3 or whether Outside-Bar-specific evidence is required. |
| C4 — Reversal formations ownership / layer boundary | BOUNDARY EVIDENCE / OPEN | Bootcamp and 2026 material names reversal patterns and discusses reactions/trade initiation, but does not supply a complete deterministic Layer 1 predicate set. | Existing canonical document keeps reversal observations separate from structural objects and assigns execution gating to the execution layer. | Human approval of the ownership boundary; deterministic pattern predicates remain separate work if required. |

## Gate rule

A source-backed finding does not automatically modify the canonical semantic owner.

No contract is marked **CLOSED** until the evidence and the exact canonical wording have passed the human approval gate.

## Key conclusion

The targeted investigation materially changes the evidence state:

- C1 now has direct source support.
- C2 now has direct source support.
- C3 has direct support for the general candle-path model but not an Outside-Bar-specific contract.
- C4 has boundary evidence but not a complete deterministic anatomy contract.

The existing `01_micro_structure.md` is currently consistent with the source evidence identified in this pass. No source-driven canonical edit is authorized by this investigation alone.
