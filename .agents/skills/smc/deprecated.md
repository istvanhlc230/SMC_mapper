# DEPRECATED

**Role:** Historical rules retained only for traceability. Deprecated rules must not drive canonical validation or implementation semantics.

## 43. Obsolete retracement variant

The historical sub-38.2% Fibonacci bootstrap variant is obsolete and must not exist in canonical methodology or implementation semantics.

Do not retain the obsolete variant as:

- a scoring-only concept;
- a historical or informational concept;
- a compatibility mode;
- a test or fixture concept;
- a logging/state-name concept;
- an entry/setup classification.

The canonical minimum retracement default remains 38.2%, with the separately defined exact 2-candle momentum exception. No obsolete numeric alias may be used to create a distinct structural state.

## Superseded BOS / CHoCH compatibility wording

The following historical formulations are explicitly superseded by the validated lifecycle rules in `true_smc_structural_lifecycle.md`:

1. Any rule requiring a later body close to validate an otherwise eligible external Wick-BOS.
2. Any rule treating an external wick breach of an eligible non-fallback Confirmed Continuation Swing as automatically a liquidity sweep rather than a valid Wick-BOS.
3. Any rule allowing a Fallback Major IDM wick breach to become BOS or CHoCH.
4. Any rule allowing `MAJOR_IDM_SWEEP` to directly create `CONFIRMED_SWING_POINT` rather than only unlock the Swing Confirmation Gate.
5. Any rule treating a post-break SVP as automatically identical to Real Major IDM without the `Verified Pullback Extreme → Major IDM Eligibility` chain.
6. Any rule treating a body close beyond the governing opposing boundary as sufficient by itself to declare `VALID_CHoCH`.
7. Any rule allowing a later candle to retroactively rewrite an earlier structural classification.
8. Any rule allowing fallback-proxy wick interaction to roll the Trading Range or lock the Protected Structural Extreme.

The authoritative replacement is:

```text
true_smc_structural_lifecycle.md
  3.3.3
  3.4.1–3.4.5
  3.5.1
```

These deprecated formulations may be retained for historical traceability only. They are not alternative canonical paths.

## Legacy BOS compatibility

Any historical-close Wick-BOS compatibility option is not part of the canonical methodology. If retained, it is legacy compatibility only and must never override the canonical external Wick BOS rules.

## Deprecated handling rule

Deprecated content is retained for traceability only. It must not be used as an active methodology rule, implementation shortcut, scoring rule, or execution rule.
