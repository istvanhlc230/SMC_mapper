---
name: true-smc
description: Governs and validates the canonical True SMC methodology and scanner implementation. Use for True SMC audits, walkthroughs, implementation plans, code changes, regression validation, and methodology validation.
---

# TRUE SMC — CANONICAL STRUCTURAL RULESET

**Status:** Authoritative
**Purpose:** Source-code validation contract for True SMC Scanner v2.

## 1. Scope and authority

This document defines the canonical True SMC methodology for market structure, candle relationships, Valid Pullbacks, structural qualification, liquidity, IDM, swing confirmation, BOS, CHoCH, Trading Range, Major/Minor IDM lifecycle, bootstrap/genesis behavior, and dependent scanner state.

Do not introduce generic SMC rules that are not supported by this methodology. Configuration, scoring, visualization, and implementation convenience must never redefine structural meaning.

## 2. Canonical hierarchy

```text
RAW OHLC
  ↓
CANDLE RELATIONSHIPS
  ↓
CANDLE-LEVEL MINOR STRUCTURE
  ↓
CANDLE-LEVEL VALID PULLBACK
  ↓
STRUCTURAL RETRACEMENT QUALIFICATION
  ↓
STRUCTURALLY VALID PULLBACK
  ↓
VERIFIED PULLBACK EXTREME
  ↓
BSL / SSL LIQUIDITY
  ↓
ACTIVE PULLBACK POINTER
  ↓
IDM ELIGIBILITY
  ↓
ACTIVE/MINOR IDM
  ↓
IDM LIQUIDITY TAKEOUT
  ↓
SWING CONFIRMATION
  ↓
CONFIRMED STRUCTURAL SWING
  ↓
PHYSICAL STRUCTURAL BREAK
  ↓
BREAK ACCEPTANCE
  ↓
BOS
  ↓
NEW TRADING RANGE
```

CHoCH is a separate regime transition:

```text
CURRENT TRADING RANGE
  ↓
GOVERNING RANGE BOUNDARY VIOLATION
  ↓
CHoCH
  ↓
NEW TREND
  ↓
CHoCH-CAUSING LEG = INITIAL ACTIVE IMPULSIVE LEG
  ↓
NEW STRUCTURALLY VALID PULLBACK
  ↓
ACTIVE/MINOR IDM
  ↓
IDM SWEEP
  ↓
CONFIRMED SWING
  ↓
BOS
```

Every higher-level event must consume a previously validated lower-level event. No stage may be skipped.

## 3. Mandatory non-equivalences

```text
NEW MINOR HIGH/LOW           ≠ CONFIRMED STRUCTURAL SWING
CANDLE-LEVEL VALID PULLBACK  ≠ STRUCTURALLY VALID PULLBACK
CANDLE-LEVEL VALID PULLBACK  ≠ IDM
STRUCTURALLY VALID PULLBACK  ≠ IDM
PULLBACK EXTREME             ≠ AUTOMATIC IDM
LOCAL/PIVOT EXTREME          ≠ CONFIRMED SWING
3 CANDLES                    ≠ IDM
38.2%                        ≠ IDM
REFERENCE TRANSFER           ≠ VALID PULLBACK
INSIDE-BAR BREAK             ≠ VALID PULLBACK
INSIDE-BAR LIQUIDITY         ≠ IDM
IDM SWEEP                    ≠ BOS
IDM SWEEP                    ≠ CHoCH
LIQUIDITY TAKEOUT            ≠ STRUCTURAL BREAK
LIQUIDITY                    ≠ STRUCTURE
CHoCH                        ≠ BOS
CHoCH                        ≠ IDM
CHoCH-CAUSING LEG            ≠ AUTOMATIC PULLBACK
CHoCH-CAUSING LEG            ≠ AUTOMATIC IDM
DEEP RETRACEMENT             ≠ AUTOMATIC STRUCTURAL RESET
PROTECTED SWING              ≠ TRADING RANGE BOUNDARY
NEW MINOR HIGH/LOW           ≠ NEW TRADING RANGE
HISTORICAL STRUCTURE         ≠ CURRENT GOVERNING STRUCTURE
IDM                          ≠ POI
ORDER FLOW                   ≠ ORDER BLOCK
DISPLACEMENT                 ≠ BOS
POI                          ≠ ENTRY EXECUTION
CONFIGURATION OPTION         ≠ CANONICAL METHODOLOGY RULE
```

## 4. Candle-level Valid Pullback

Day 1 defines candle-level pullback identification only. It must not be conflated with structural qualification, IDM, BOS, CHoCH, or Trading Range logic.

### Bullish

A bullish candle-level Valid Pullback requires:

1. A reference high exists.
2. Price breaks the reference high.
3. Price subsequently breaches the reference low.
4. The breach may be wick or body.
5. Candle color is irrelevant.
6. Price subsequently breaks the relevant continuation/reference high.
7. The full sequence establishes the candle-level Valid Pullback.

Do not reduce this to “previous candle low breach”.

### Bearish

Mirror:

1. A reference low exists.
2. Price breaks the reference low.
3. Price subsequently breaches the reference high.
4. Wick or body is acceptable.
5. Candle color is irrelevant.
6. Price subsequently breaks the relevant continuation/reference low.
7. The full sequence establishes the candle-level Valid Pullback.

Do not reduce this to “previous candle high breach”.

## 5. Equal High / Equal Low reference rules

If two consecutive candles have equal highs, the second candle becomes the active reference. A Valid Pullback requires price to break below the second candle low and later break above the shared high.

If two consecutive candles have equal lows, the second candle becomes the active reference. A Valid Pullback requires price to break above the second candle high and later break below the shared low.

## 6. Inside bars

A strict inside bar is:

```text
current.high < mother.high
AND
current.low  > mother.low
```

A strict inside bar does not independently create a Valid Pullback, structurally valid pullback, IDM, confirmed swing, BOS, or CHoCH. A break of an inside-bar relationship requires independent structural validation.

## 7. Outside bars

A single outside bar must not activate both directional branches.

Canonical candle-level sequencing:

```text
Bullish outside-bar sequence = LOW → HIGH
Bearish outside-bar sequence = HIGH → LOW
```

This rule exists to preserve deterministic and timeframe-invariant interpretation.

## 8. Verified pullback extreme

After a candle-level Valid Pullback:

```text
Bullish: verified pullback extreme = Pullback Low
Bearish: verified pullback extreme = Pullback High
```

This extreme is a candidate liquidity reference, not automatic IDM.

Correct chain:

```text
Candle-Level Valid Pullback
  ↓
Verified Pullback Extreme
  ↓
Structural Qualification
  ↓
Structurally Valid Pullback
  ↓
IDM Eligibility
```

## 9. Structural retracement qualification

A previous strict rule of “at least 3 opposing candles AND 38.2%” is no longer absolute. There are two qualification paths.

### Standard path

```text
>= 3 opposing candles
AND
>= configured minimum retracement depth
```

The canonical default minimum is 38.2%, exposed as a configurable engine parameter where applicable.

The implementation may expose `BOS_MIN_RETRACEMENT_PCT` with canonical default 38.2%.

Changing the configured value changes the threshold, not the semantic definition of Valid Pullback or IDM.

Do not encode the numeric default into semantic state names when the state really means “structurally valid pullback”.

### Momentum / candle-size exception

Exactly 2 opposing candles may qualify when:

```text
EXACTLY 2 OPPOSING CANDLES
AND
LARGE / HIGH-MOMENTUM PRICE ACTION
AND
(
    >= 5 PRIOR CANDLE EXTREMES SWEPT/ENGULFED
    OR
    RETRACEMENT DEPTH >= 38.2%
)
```

Important constraints:

- The verified exception is for exactly 2 candles.
- Do not automatically extend it to 1 candle.
- “Large/high momentum” remains qualitative unless independently verified source material provides a quantitative threshold.
- Do not invent ATR, body-ratio, volatility, or standard-deviation thresholds and present them as canonical methodology.
- Implementation thresholds may be configurable, but must be clearly treated as implementation parameters.

## 10. Structurally Valid Pullback

A candle-level Valid Pullback becomes a Structurally Valid Pullback only after structural retracement qualification.

Only a Structurally Valid Pullback can become the basis for active/minor IDM.

A candle-level pullback must never directly create IDM.

## 11. Liquidity taxonomy

For the active structural leg:

```text
Uptrend pullback low   → Sell-Side Liquidity (SSL)
Downtrend pullback high → Buy-Side Liquidity (BSL)
```

Every structurally valid pullback extreme may represent liquidity, but not every liquidity node is IDM.

## 12. Single active pullback pointer

The engine must track one active pullback pointer for the active expansion/impulsive leg: the most recent Structurally Valid Pullback.

If a newer Structurally Valid Pullback forms before the previous active target is swept, immediately replace the active pointer with the newer pullback.

Do not keep multiple competing minor IDM targets active simultaneously.

This does not mean deleting historical structure. Maintain these separately:

```text
ACTIVE PULLBACK POINTER
≠ MINOR IDM STATE
≠ MAJOR IDM STATE
≠ CONFIRMED SWING
≠ TRADING RANGE
≠ HISTORICAL STRUCTURE
```

## 13. IDM definition

IDM is liquidity resting beyond the most recent Structurally Valid Pullback on the active impulsive leg.

Therefore IDM must be:

1. derived from a Structurally Valid Pullback,
2. on the active impulsive leg,
3. the most recent qualifying pullback,
4. represented by its relevant liquidity extreme.

Random bars, arbitrary pivots, inside bars, generic local highs/lows, Fibonacci levels, or every liquidity node are not IDM.

## 14. Minor / active IDM lifecycle

The active/minor IDM shifts immediately to the newest Structurally Valid Pullback on the same active impulsive leg.

Historical IDM may remain in history but must not remain an active competing target.

## 15. Major IDM lifecycle

Major IDM is a separate lifecycle and must not be overwritten whenever Minor IDM changes.

Canonical real Major IDM lifecycle:

```text
BOS
 ↓
New Trading Range
 ↓
First real post-BOS Structurally Valid Pullback
 ↓
Major IDM
```

This BOS lifecycle rule must not be automatically applied to CHoCH.

```text
BOS lifecycle ≠ CHoCH lifecycle
```

## 16. Fallback Major IDM

If a BOS establishes a new structural lifecycle but no real post-BOS Valid-Pullback-derived Major IDM exists, the previously established protected major structural level may remain as Fallback Major IDM according to the existing engine lifecycle.

Fallback Major IDM is not equivalent to a real post-BOS Major IDM.

```text
Real Major IDM     = post-BOS structurally valid pullback-derived IDM
Fallback Major IDM = previous protected major structural reference used as fallback inducement
```

A fallback level may simultaneously function as protected structural reference, inducement liquidity, and liquidity target. These roles must remain semantically distinct.

## 17. IDM liquidity sweep

Bullish active IDM is normally SSL / pullback low. Bearish active IDM is normally BSL / pullback high.

The active IDM may be swept by wick or body.

The sweep is a liquidity event. It is not automatically BOS or CHoCH.

## 18. Swing confirmation and BOS are separate

```text
ACTIVE IDM LIQUIDITY SWEEP
  ↓
SWING LOCK-IN / CONFIRMATION
  ↓
CONFIRMED STRUCTURAL SWING
  ↓
BODY-CLOSE STRUCTURAL BREAK
  ↓
BOS
```

An IDM sweep must not be implemented as a compound BOS event.

## 19. Swing confirmation

A tentative structural swing may form while price expands. The canonical asymmetric Range-Lock model applies.

Bullish: a candidate high forms, the most recent valid pullback low / active IDM is swept by wick or body, and the prior high becomes the Confirmed Range High. The retracement must satisfy the configured minimum depth (default 38.2%). The retracement low remains floating/provisional; track the minimum Low across the entire retracement. Only a later valid BOS above the Confirmed High locks that absolute lowest retracement point as the Protected/Strong Low.

Bearish: a candidate low forms, the most recent valid pullback high / active IDM is swept by wick or body, and the prior low becomes the Confirmed Range Low. The retracement high remains floating/provisional; track the maximum High across the entire retracement. Only a later valid BOS below the Confirmed Low locks that absolute highest retracement point as the Protected/Strong High.

The IDM sweep confirms the opposite/top-side structural extreme; it does not directly confirm the retracement/protected side.

This confirmation is not BOS.

A local pivot or fractal detector may support candidate identification but cannot independently confirm True SMC structure without the required IDM/liquidity sequence.

## 20. Deep retracement after swing confirmation

After swing confirmation, price may retrace deeply, sweep older second/third pullbacks, or interact with FVGs, Imbalances, Order Blocks, and other POIs.

These events do not automatically invalidate the confirmed swing.

Canonical separation:

```text
Active IDM → determines swing confirmation
Trading Range Boundary → determines trend health / regime validity
```

Deep retracement alone must not reset structure or re-anchor a confirmed swing.

## 21. BOS canonical qualification

Canonical external BOS requires appropriate structural context, the required IDM liquidity takeout, a confirmed structural swing / confirmed range boundary, a physical break of the actual reference High/Low, canonical break acceptance, and compliance with the active-Major-IDM gate.

### Bullish external break

```text
Physical break: Breaking.High > Ref.High
Acceptance:     Breaking.Close > max(Ref.Open, Ref.Close)
```

The breaking candle's color is irrelevant. Do not require `Breaking.Close > Breaking.Open`. If the physical high is breached and acceptance succeeds while the close remains at or below `Ref.High`, this is canonical external Wick BOS. If `Breaking.Close > Ref.High`, this is full Body-Close BOS. If `Breaking.High > Ref.High` but `Breaking.Close <= max(Ref.Open, Ref.Close)`, this is a sweep/rejection, not BOS.

### Bearish external break

```text
Physical break: Breaking.Low < Ref.Low
Acceptance:     Breaking.Close < min(Ref.Open, Ref.Close)
```

The breaking candle's color is irrelevant. If `Breaking.Close < Ref.Low`, this is full Body-Close BOS. If the physical low is breached but acceptance fails, the move is a sweep/rejection, not BOS.

### Active Major IDM gate

If the broken structural level is currently the active Major IDM, external Wick BOS is disabled. A physical wick through the active Major IDM is a liquidity sweep only. Bullish BOS requires `Close > Active_Major_IDM`; bearish BOS requires `Close < Active_Major_IDM`. This is object-identity based, not fallback-specific.

Wick BOS is canonical for eligible external structural levels; it is not a legacy compatibility mode.

```text
IDM SWEEP
  ↓
CONFIRMED SWING / RANGE SIDE
  ↓
PHYSICAL STRUCTURAL BREAK
  ↓
BREAK ACCEPTANCE
  ↓
BOS
```

## 22. Breaker reference

Maintain the existing canonical body-reference rule:

```text
Bullish:
  bullish reference candle → close
  otherwise → open

Bearish:
  bearish reference candle → close
  otherwise → open
```

This is the `breaker_reference` used for body-close structural qualification.

## 23. Non-canonical legacy compatibility

Any historical-close Wick-BOS compatibility option is not part of the canonical methodology. If retained, it is legacy compatibility only and must never override the canonical external Wick BOS rules in Section 21.

## 24. Bullish BOS sequence

```text
UPWARD EXPANSION
 ↓
STRUCTURALLY VALID PULLBACK
 ↓
PULLBACK LOW = SSL
 ↓
ACTIVE MINOR IDM
 ↓
MOST RECENT IDM SWEPT
 ↓
SWING LOW CONFIRMED
 ↓
PRICE BREAKS PREVIOUS CONFIRMED SWING HIGH
 ↓
BODY CLOSE
 ↓
BULLISH BOS
 ↓
NEW TRADING RANGE
```

Multiple older pullbacks may be swept, but the most recent active IDM is the governing target.

## 25. Bearish BOS sequence

```text
DOWNWARD EXPANSION
 ↓
STRUCTURALLY VALID PULLBACK
 ↓
PULLBACK HIGH = BSL
 ↓
ACTIVE MINOR IDM
 ↓
MOST RECENT IDM SWEPT
 ↓
SWING HIGH CONFIRMED
 ↓
PRICE BREAKS PREVIOUS CONFIRMED SWING LOW
 ↓
BODY CLOSE
 ↓
BEARISH BOS
 ↓
NEW TRADING RANGE
```

## 26. Minor IDM takeout is not BOS

A Minor IDM takeout is first a liquidity event.

```text
Minor IDM
 ↓
Minor IDM liquidity takeout
 ↓
possibly subsequent Valid Pullback
 ↓
independent structural evaluation
```

A subsequent Valid Pullback must be independently validated. Minimum retracement qualification may be relevant to subsequent BOS/setup evaluation, but neither event alone creates BOS.

## 27. Fallback Major IDM takeout

Fallback Major IDM interaction is a liquidity event unless the complete structural break prerequisites are satisfied.

Therefore:

```text
Fallback Major IDM sweep ≠ BOS
Fallback Major IDM sweep ≠ CHoCH
Wick through fallback level ≠ automatic structural break
```

The Fallback Major IDM does not create a separate BOS qualification rule. Fallback status neither weakens nor strengthens canonical break acceptance. If the broken level is represented as the active Major IDM object, the active-Major-IDM gate applies regardless of whether that object is real or fallback.

Fallback status does not weaken, replace, or bypass the canonical BOS sequence:

```text
IDM SWEEP
 ↓
CONFIRMED SWING
 ↓
STRUCTURAL BREAK
 ↓
BODY CLOSE
 ↓
BOS
```

This rule is specific to BOS qualification and must not be applied to CHoCH. CHoCH is determined by violation of the governing Trading Range boundary.

## 28. Fallback Major IDM setup condition

The following can form a setup qualification, but not automatically a structural break:

```text
Minor IDM established
 ↓
Minor IDM takeout
 ↓
New Structurally Valid Pullback
 ↓
Configured minimum retracement reached
 ↓
Fallback Major IDM reached/interacted with
```

Keep separate states for Valid Pullback, IDM takeout, minimum retracement, fallback interaction, structural break, and BOS.

## 29. CHoCH definition

CHoCH occurs when price violates the governing opposing Trading Range boundary.

Example:

```text
BEARISH RANGE
 ↓
ACTIVE/GOVERNING RANGE HIGH VIOLATED
 ↓
CHoCH
 ↓
BULLISH REGIME
```

Mirror for bullish-to-bearish:

```text
BULLISH RANGE
 ↓
ACTIVE/GOVERNING RANGE LOW VIOLATED
 ↓
CHoCH
 ↓
BEARISH REGIME
```

CHoCH is not an IDM sweep, BOS, local pivot break, or generic displacement event.

## 30. CHoCH-causing leg becomes the initial active impulse

When CHoCH occurs, the price leg that caused the CHoCH becomes the initial active impulsive leg of the new trend.

Do not reset the new trend into an empty state waiting for another independent impulse.

The next Structurally Valid Pullback formed on that active leg can become the new active/minor IDM.

However:

```text
CHoCH-causing leg ≠ automatic pullback
CHoCH-causing leg ≠ automatic IDM
CHoCH ≠ BOS
```

## 31. CHoCH and protected swing state

CHoCH establishes the new trend regime but does not automatically create a new protected swing.

The new trend may therefore have:

```text
NEW TREND
+
INITIAL ACTIVE IMPULSIVE LEG
+
NO NEW PROTECTED SWING UNTIL VALID STRUCTURAL CONFIRMATION/BOS
```

Do not fabricate protected structure merely because CHoCH occurred.

## 32. Asymmetric Range-Lock

Confirmed Range High/Low and Protected High/Low are separate lifecycle states.

Bullish: candidate High → retracement → active IDM/pullback Low sweep → Confirmed Range High → minimum retracement (default 38.2%) → floating retracement Low tracking → valid BOS above Confirmed High → absolute lowest retracement Low becomes Protected/Strong Low.

Bearish: candidate Low → retracement → active IDM/pullback High sweep → Confirmed Range Low → minimum retracement → floating retracement High tracking → valid BOS below Confirmed Low → absolute highest retracement High becomes Protected/Strong High.

Deep retracement does not automatically invalidate the confirmed range-side. The IDM sweep confirms the opposite/top-side extreme; BOS locks the protected retracement extreme.

## 33. Trading Range

Trading Range is a separate structural state from Active/Minor IDM, Major IDM, Fallback Major IDM, confirmed swing, weak swing, local pivot, and POI.

BOS establishes a new Trading Range.

### Bearish BOS

New Range High is the absolute highest apex reached during the relevant retracement.

### Bullish BOS

New Range Low is the absolute lowest trough reached during the relevant retracement.

Internal fluctuations do not continuously shift the primary range boundary.

## 34. Trading Range stability

The primary Trading Range remains static until an official structural transition.

The following do not automatically create a new Trading Range:

- new minor high/low,
- internal pullback,
- liquidity sweep,
- FVG interaction,
- Order Block interaction,
- local pivot,
- displacement.

## 35. Trading Range versus IDM

```text
ACTIVE IDM
  → short-term liquidity / swing-confirmation mechanism

TRADING RANGE BOUNDARY
  → regime / structural-health mechanism
```

Deep historical liquidity interaction does not itself invalidate the range.

## 36. POI ontology — canonical tradable POIs

The canonical POI ontology is a closed set. A tradable Point of Interest may be either **Valid Order Flow (OF)** or **Valid Order Block (OB)**. No third POI entity may be introduced by generic SMC convention or implementation convenience.

```text
VALID ORDER FLOW (OF)
VALID ORDER BLOCK (OB)
        ↓
   CANONICAL POI
```

The following are not canonical POI entities:

- standalone FVG / imbalance;
- Breaker Block;
- Mitigation Block;
- Liquidity Void;
- arbitrary liquidity pool;
- IDM;
- generic displacement zone.

These concepts may exist as structural observations, validators, liquidity, or historical annotations where separately defined, but they must not silently become tradable POIs.

### Rule of Two

For a canonical dealing range, there may be one or two tradable POIs:

```text
DECISIONAL POI
      +
EXTREME POI
```

Everything outside the active one-or-two-POI structure is non-tradable/SMT unless a canonical rule explicitly promotes it. Multiple arbitrary POIs must not be created merely because multiple zones are visually present.

### POI semantic separation

```text
IDM              ≠ POI
LIQUIDITY        ≠ POI
FVG              ≠ POI
DISPLACEMENT     ≠ POI
POI              ≠ ENTRY EXECUTION
```

A POI is a validated execution-location object. Its existence must never alter structural validation of IDM, swing, BOS, CHoCH, or Trading Range.

### POI and execution invariants

The following invariants are mandatory:

```text
POI ∈ {VALID_OF, VALID_OB}
STANDALONE_FVG → NOT_POI
IDM → NOT_POI
LIQUIDITY → NOT_POI
POI → NOT_STRUCTURE
POI → NOT_BOS
POI → NOT_CHoCH
POI → NOT_AUTOMATIC_ENTRY
FVG → OB_VALIDATOR_ONLY
```

Representative linter violations:

```text
register_poi(fvg)              → ERR-POI-FVG-01
price_enters_fvg → entry       → ERR-EXEC-FVG-01
price.breaks_fvg → BOS         → ERR-STRUCT-FVG-01
register_poi(idm)               → ERR-POI-IDM-01
```

A code path that violates these invariants is non-canonical even if its output appears visually plausible.

## 37. Decisional and Extreme POI

The canonical dealing-range POI model distinguishes the **Decisional POI** from the **Extreme POI**.

### Decisional POI

The Decisional POI is the primary execution location. Its directional location is mandatory:

```text
BUY → POI must be in DISCOUNT
      normalized location < 0.50

SELL → POI must be in PREMIUM
       normalized location > 0.50
```

A Decisional POI outside its required premium/discount side is not a valid Decisional POI and must not be promoted to a canonical entry merely because the underlying zone is otherwise valid.

### Extreme POI

The Extreme POI is the secondary/fallback execution location of the same dealing-range framework. It is used when the Decisional POI is unavailable, fails its execution conditions, or is otherwise not the applicable module according to the canonical entry sequence.

The Extreme POI must still be a Valid OF or Valid OB. It is not an arbitrary fallback to any visually convenient zone.

### Origin OB

An Origin OB is a canonical absolute range-origin Order Block. It is not required to disappear merely because its parent Valid Order Flow has been mitigated. Its validity must be evaluated according to the OB validation rules rather than by inheritance from the current OF state.

## 38. Order Block validation

A candle/zone may be treated as a Valid Order Block only when the canonical three-pillar validation is satisfied.

```text
PILLAR 1
Origin of impulsive displacement that causes structural BOS
        +
PILLAR 2
Candle sweeps previous candle's extreme
        +
PILLAR 3
Active, fully unmitigated FVG/imbalance adjacent to the candle
        ↓
VALID ORDER BLOCK
        ↓
POI ELIGIBILITY
```

All three pillars are required. A visually strong candle, displacement alone, or an FVG alone must not create an OB.

The structural BOS referenced by Pillar 1 must be independently canonical. An implementation must not manufacture BOS merely to validate an OB.

### Valid Order Flow

Valid OF is a canonical POI class distinct from OB. OF and OB must not be conflated into a single generic zone type merely for implementation convenience.

### OB mitigation

Mitigation changes execution eligibility; it does not rewrite historical structural meaning. A mitigated OF does not automatically invalidate a separately valid Origin OB. A failed Decisional POI does not authorize arbitrary zone substitution; the canonical Extreme POI must be used when its own validity conditions are satisfied.

## 39. FVG / imbalance ontology

FVG exists in the canonical methodology, but it is **strictly a validator/property and never a standalone tradable POI**.

```text
FVG
 ↓
OB VALIDATION
 ↓
VALID OB
 ↓
POI
 ↓
ENTRY MODULE
```

The following are forbidden semantic shortcuts:

```text
FVG → POI
FVG → ENTRY
FVG TOUCH → ENTRY
FVG BREAK → BOS
FVG → CHoCH
```

A standalone FVG must not:

- create a tradable zone;
- create an entry signal;
- create a limit order;
- create or invalidate a POI;
- confirm a structural swing;
- create BOS or CHoCH.

An FVG may participate as Pillar 3 of OB validation. It remains ontologically distinct from IDM, liquidity, POI, and execution.

## 40. Canonical entry modules

The canonical execution layer contains four entry modules:

1. **IDM Sweep**
2. **Decisional POI Mitigation**
3. **Engineering Liquidity Sweep**
4. **Extreme POI Mitigation**

These are execution mechanisms, not alternative definitions of market structure. An entry module may consume canonical structural state, liquidity state, and validated POI state, but it must never manufacture IDM, BOS, CHoCH, or a Trading Range.

### Module 1 — IDM Sweep

The IDM Sweep module requires a canonically active IDM and its qualifying liquidity interaction. IDM sweep remains a liquidity/execution event and is not itself BOS or CHoCH.

### Module 2 — Decisional POI Mitigation

The Decisional POI must be a valid OF or OB, must satisfy the directional premium/discount gate, and must meet the independent execution conditions of the module. POI mitigation does not create structural validity.

### Module 3 — Engineering Liquidity Sweep

Engineering liquidity is an execution-layer liquidity event. It must not be promoted to structural liquidity, IDM, BOS, or CHoCH merely because price sweeps the engineered level.

### Module 4 — Extreme POI Mitigation

The Extreme POI module is the canonical fallback execution mechanism when the Decisional POI is not the applicable execution location. The Extreme POI must independently satisfy OF/OB validity; fallback execution does not relax POI validation.

## 41. Execution, structural validation, and risk

Execution priority and structural validation are separate domains.

```text
EXECUTION PRIORITY ≠ STRUCTURAL VALIDATION
ORDER FLOW FAILED ≠ BOS
ORDER FLOW FAILED ≠ CHoCH
POI FAILURE ≠ STRUCTURAL FAILURE
```

A failed execution condition must not be converted into a structural event. Likewise, a structurally valid event does not automatically authorize execution.

### Order Flow failure / Extreme fallback

Do not fail over from Valid OF to Extreme OB solely because price wicked into or through the OF. The exact failure condition must be independently satisfied by the canonical execution module. A wick touch alone is insufficient to invent an execution-state transition.

### Risk and RR

A canonical executable setup must satisfy a minimum risk/reward of **1:2**. The primary target is the confirmed external range extreme where the applicable entry module requires it. Risk management must consume structural state; it must not redefine structure.

## 42. Genesis / bootstrap

Genesis is a special initialization condition. It must not manufacture historical structure.

Genesis must not invent IDM, confirmed swing, BOS, Major IDM, or protected structure.

Bootstrap behavior may exist where explicitly established by the methodology, but must remain distinguishable from organically confirmed structural state.

No bootstrap shortcut may silently bypass the canonical lifecycle after normal structure exists.

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

## 44. Scoring

Existing scoring weights:

```text
Structure = 25%
Setup     = 30%
Location  = 20%
Liquidity = 15%
Risk      = 10%
```

Quality tiers:

```text
HIGH   >= 70
MEDIUM >= 55
LOW    >= 40
WATCH  < 40
```

Liquidity quality:

```text
Real Major IDM     = 80
Fallback Major IDM = 40
```

Risk penalties:

```text
Retracement > 78.6% → -25
Retracement > 90.0% → -20
```

Scoring evaluates canonical structural state. Scoring must never create or validate structure.

## 45. Implementation mapping

The structural engine must conceptually separate:

```text
CANDLE-LEVEL PULLBACK
STRUCTURALLY VALID PULLBACK
VERIFIED PULLBACK EXTREME
ACTIVE LIQUIDITY POINTER
ACTIVE/MINOR IDM
REAL MAJOR IDM
FALLBACK MAJOR IDM
IDM SWEEP
TENTATIVE SWING
CONFIRMED SWING
BOS
CHoCH
TRADING RANGE
```

Functions equivalent to `finish_pullback()` must not promote a candle-level pullback directly to IDM.

Functions equivalent to `detect_idm_sweep()` must operate on the active IDM and must not themselves declare BOS.

Functions equivalent to `detect_bos()` must require the canonical IDM, confirmed-swing/range-side, physical-break, and break-acceptance prerequisites, plus the active-Major-IDM gate when applicable.

Functions equivalent to `detect_choch()` must use the governing Trading Range boundary and must not use an arbitrary local pivot or IDM sweep as a substitute.

## 46. Structural state machine

The scanner is a state machine. Each event must be evaluated against current state, not only against the current candle.

```text
OBSERVATION
 ↓
CANDLE-LEVEL VALID PULLBACK
 ↓
STRUCTURAL QUALIFICATION
 ↓
STRUCTURALLY VALID PULLBACK
 ↓
LIQUIDITY
 ↓
ACTIVE IDM
 ↓
IDM SWEEP
 ↓
CONFIRMED SWING
 ↓
BODY-CLOSE BREAK
 ↓
BOS
 ↓
NEW TRADING RANGE
```

CHoCH path:

```text
CURRENT RANGE
 ↓
RANGE BOUNDARY VIOLATION
 ↓
CHoCH
 ↓
NEW TREND
 ↓
CHoCH-CAUSING LEG = INITIAL ACTIVE IMPULSE
 ↓
NEW STRUCTURALLY VALID PULLBACK
 ↓
IDM
```

The engine must not skip prerequisites because a later price movement appears visually obvious.

## 47. Error conditions that must be prevented

1. Random local low becomes bullish IDM.
2. Random local high becomes bearish IDM.
3. Inside bar becomes IDM.
4. Three candles automatically become IDM.
5. 38.2% automatically becomes IDM.
6. Candle-level pullback becomes IDM without structural qualification.
7. Old active IDM remains after a newer valid pullback forms.
8. Multiple active minor IDM targets remain simultaneously.
9. IDM sweep becomes BOS without swing confirmation/body close.
10. IDM sweep becomes CHoCH.
11. A physical break becomes BOS without canonical break acceptance.
12. Local pivot break becomes CHoCH.
13. Deep retracement invalidates confirmed swing without governing range violation.
14. New minor high/low creates a new Trading Range.
15. CHoCH resets new trend to an empty state.
16. CHoCH creates a protected swing automatically.
17. CHoCH-causing leg is ignored as the initial active impulse.
18. Fallback Major IDM is treated as a real Major IDM.
19. Genesis manufactures IDM or protected structure.
20. The obsolete sub-38.2% Fibonacci variant remains anywhere in methodology semantics.
21. Scoring creates structural validity.
22. Historical liquidity remains active merely because it exists in history.
23. One outside bar activates both directional branches.
24. Inside-bar breaks are treated as independent pullbacks.

## 48. Testing requirements

Regression tests must cover:

### Pullback
- bullish candle-level Valid Pullback;
- bearish candle-level Valid Pullback;
- equal-high reference;
- equal-low reference;
- strict inside-bar exclusion;
- outside-bar LOW→HIGH sequencing;
- outside-bar HIGH→LOW sequencing.

### Structural qualification
- standard >=3-candle qualification;
- configurable minimum retracement;
- exact 2-candle momentum exception;
- >=5 prior extreme sweep/engulfment exception;
- 2-candle >=38.2% exception;
- one candle does not automatically qualify.

### IDM
- candle-level pullback does not create IDM;
- structurally valid pullback can create IDM;
- newest valid pullback replaces old active IDM;
- only one active minor IDM;
- real versus fallback Major IDM;
- correct Major IDM lifecycle after BOS;
- CHoCH does not automatically apply BOS Major IDM promotion;
- historical IDM is not an active competing target.

### Swing/BOS
- IDM sweep confirms swing;
- wick IDM sweep;
- body IDM sweep;
- deep retracement does not invalidate confirmed swing;
- BOS requires IDM prerequisite;
- BOS requires confirmed swing;
- BOS requires canonical break acceptance;
- external Wick BOS is accepted when physical break + acceptance succeed;
- full Body-Close BOS is distinguished from external Wick BOS;
- failed acceptance is a sweep/rejection, not BOS;
- active Major IDM disables external Wick BOS and requires body close beyond the physical active Major IDM level;

### CHoCH
- correct Trading Range boundary violation;
- IDM sweep does not create CHoCH;
- local pivot break does not create CHoCH;
- CHoCH creates new trend;
- CHoCH-causing leg becomes initial active impulse;
- CHoCH does not create protected swing automatically;
- BOS body-close requirements are not incorrectly applied as CHoCH criteria.

### Trading Range
- bearish BOS Range High calculation;
- bullish BOS Range Low calculation;
- internal fluctuations do not shift primary boundary;
- minor high/low does not create a new range;
- deep retracement does not automatically reset range.

### POI / Entry
- POI ontology accepts only Valid OF or Valid OB;
- Rule of Two limits canonical tradable POIs to Decisional and Extreme;
- Decisional buy POI is in discount;
- Decisional sell POI is in premium;
- Origin OB remains independently valid after parent OF mitigation when its own pillars remain valid;
- all three OB validation pillars are required;
- standalone FVG never becomes POI;
- standalone FVG never creates entry;
- FVG break never creates BOS/CHoCH;
- IDM never becomes POI;
- OF failure does not automatically promote Extreme POI;
- all four entry modules remain execution-layer mechanisms;
- minimum 1:2 RR is enforced for executable setups.

### Genesis
- no fabricated IDM;
- no fabricated protected swing;
- no fabricated BOS.

### Obsolete concepts
- no obsolete sub-38.2% Fibonacci state, alias, or setup classification.

## 49. Final validation contract

A compliant True SMC implementation must answer “yes” to all of the following:

- Is every IDM derived from the correct Structurally Valid Pullback?
- Is only the newest valid pullback active for Minor IDM tracking?
- Are Minor and Major IDM lifecycles separate?
- Is fallback Major IDM explicitly distinguished from real Major IDM?
- Is IDM sweep separate from swing confirmation and BOS?
- Does BOS require the canonical IDM/swing context and physical structural break?
- Does external BOS apply canonical break acceptance?
- Is external Wick BOS accepted when eligible?
- Is full Body-Close BOS distinguished from external Wick BOS?
- Does an active Major IDM disable external Wick BOS and require body close beyond the physical active Major IDM level?
- Is there no fallback-specific BOS qualification rule?
- Is the BOS body-close requirement kept separate from CHoCH qualification?
- Is deep retracement prevented from arbitrarily resetting confirmed structure?
- Is CHoCH based on the governing Trading Range boundary?
- Does the CHoCH-causing leg become the initial active impulse of the new trend?
- Does CHoCH avoid fabricating a protected swing?
- Are Trading Range boundaries separate from active IDM?
- Are candle-level pullbacks separated from structural pullbacks?
- Is the 2-candle momentum exception handled without inventing a 1-candle exception?
- Is the obsolete sub-38.2% Fibonacci variant completely removed?
- Does scoring consume structural state instead of defining it?
- Are historical structures prevented from silently becoming current active structure?
- Is the tradable POI ontology closed to Valid OF and Valid OB?
- Is Rule of Two enforced for Decisional and Extreme POIs?
- Is Decisional POI location gated by discount for buys and premium for sells?
- Is Origin OB handled as a distinct canonical OB case?
- Does Valid OB require all three validation pillars?
- Is standalone FVG prohibited as a POI and entry trigger?
- Is FVG used only as an OB validator/property?
- Are all four canonical entry modules kept separate from structural validation?
- Is execution failure prevented from inventing BOS or CHoCH?
- Is Extreme fallback prevented from bypassing POI validation?
- Is minimum RR 1:2 enforced at execution qualification without redefining structure?
- Are IDM, liquidity, POI, FVG, and entry execution kept semantically distinct?

The final methodology must contain one coherent True SMC model. Contradictory legacy definitions must be removed or explicitly marked as non-canonical compatibility behavior.
