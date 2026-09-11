# TRUE_SMC_CANONICAL

**Role:** Project-specific canonical True SMC methodology.

**Authority:** Authoritative for project-specific True SMC structural semantics. Generic SMC/ICT terminology cannot override this category.

## 1. Scope and authority

This category defines the canonical True SMC methodology for market structure, candle relationships, Valid Pullbacks, structural qualification, liquidity, IDM, swing confirmation, BOS, CHoCH, Trading Range, Major/Minor IDM lifecycle, and genesis behavior.

Configuration, scoring, visualization, and implementation convenience must never redefine structural meaning.

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

### Candle-level Minor Structure

Minor Structure consists of internal candle-level structural price action that does not define or alter the governing external Trading Range. Within an established Trading Range, minor structure exists inside the governing external boundaries. Minor structural levels may provide liquidity references and may participate in IDM formation only when the independent IDM prerequisites are satisfied.

```text
Minor Structure
≠ Major Structure
≠ Liquidity
≠ IDM
≠ BOS
≠ CHoCH
```

### Candle-level Valid Pullback — Unit of Origin

The unit of origin for a candle-level Valid Pullback is a reference-candle relationship. Candle color and body size do not independently determine whether a sequence is valid.

A candle-level Valid Pullback is not created by a single reference-level breach. The complete directional sequence must be satisfied.

For a bullish sequence:

1. A valid reference high exists.
2. Price breaks the reference high.
3. Price subsequently breaches the reference low.
4. Price subsequently breaks the applicable continuation/reference high.
5. The completed sequence constitutes the candle-level Valid Pullback.

For a bearish sequence, the sequence is mirrored:

1. A valid reference low exists.
2. Price breaks the reference low.
3. Price subsequently breaches the reference high.
4. Price subsequently breaks the applicable continuation/reference low.
5. The completed sequence constitutes the candle-level Valid Pullback.

Strict inside bars cannot independently establish a candle-level Valid Pullback. Their presence does not create a separate structural state and does not by itself establish a Structurally Valid Pullback, IDM, Swing, BOS, or CHoCH.

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

Equal High / Equal Low is a candle-level relationship. It participates in reference transfer only within the applicable directional candle context; it is not a directionless structural or IDM event.

### Bullish context

When two consecutive candles have equal highs:

1. The shared high forms the Equal High relationship.
2. The **second candle becomes the active reference**.
3. Price must subsequently break below the **second candle low**.
4. Price must then break above the **shared high**.
5. This completes the applicable candle-level Valid Pullback sequence.

### Bearish context

When two consecutive candles have equal lows:

1. The shared low forms the Equal Low relationship.
2. The **second candle becomes the active reference**.
3. Price must subsequently break above the **second candle high**.
4. Price must then break below the **shared low**.
5. This completes the applicable candle-level Valid Pullback sequence.

Reference transfer is directional and belongs to candle-level Valid Pullback construction. It does not by itself create a Structurally Valid Pullback, IDM, confirmed swing, BOS, or CHoCH.

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

## 42. Genesis / bootstrap

Genesis is a special initialization condition. It must not manufacture historical structure.

Genesis must not invent IDM, confirmed swing, BOS, Major IDM, or protected structure.

Bootstrap behavior may exist where explicitly established by the methodology, but must remain distinguishable from organically confirmed structural state.

No bootstrap shortcut may silently bypass the canonical lifecycle after normal structure exists.

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
