# INDEPENDENT TRUE SMC ARCHITECTURAL / THEORETICAL VALIDATOR HANDOFF

## 0. Mission

You are an independent, strict theoretical and architectural validator. You receive the **current category-based True SMC Skill and the current SMC_Mapper implementation logic** so that you can compare implementation against the canonical methodology without redesigning it.

Your task is to determine whether the implementation:

1. preserves the canonical ontology of every True SMC object;
2. preserves provenance and prerequisite chains;
3. preserves Structural → Execution → Risk decoupling;
4. implements deterministic event/state transitions;
5. keeps fallback, minor, and real IDM lineages distinct;
6. avoids generic ICT/SMC contamination where it materially changes behavior;
7. does not silently replace a canonical rule with implementation convenience.

**Do not redesign the methodology.** Do not repair contradictions by inventing a new rule. Report the discrepancy and classify it.

## 0.1 Authority hierarchy

Use this hierarchy when resolving conflicts:

```text
CURRENT EXPLICITLY VALIDATED TRUE SMC RULE
        >
CURRENT SEMANTIC OWNER
        >
OLDER CONFLICTING WORDING
        >
VALIDATOR ASSUMPTION
        >
GENERIC ICT / SMC KNOWLEDGE
```

Classify findings as:

```text
ACCEPT
ACCEPT WITH CLARIFICATION
CONFLICT
LOGICALLY INVALID
SOURCE-PENDING
DUPLICATE / ALREADY COVERED
FALSE POSITIVE / SOURCE MISMATCH
TEST_FAILURE
HUMAN_REVIEW_REQUIRED
```

Never invent a numerical threshold or structural identity because a generic SMC convention would normally use one.

---

# 1. SYSTEM ARCHITECTURE / DECOUPLING

The system is conceptually divided into:

```text
STRUCTURAL ENGINE
        ↓
EXECUTION ENGINE
        ↓
RISK ENGINE
```

### Structural Engine owns

```text
CANDLE RELATIONSHIPS
CANDLE-LEVEL VALID PULLBACK
STRUCTURALLY VALID PULLBACK
VERIFIED PULLBACK EXTREME
LIQUIDITY
ACTIVE PULLBACK POINTER
MINOR IDM
REAL MAJOR IDM
FALLBACK MAJOR IDM
IDM SWEEP
SWING CONFIRMATION GATE
CONFIRMED SWING
PROTECTED STRUCTURAL EXTREME
TRADING RANGE
PHYSICAL EXTERNAL BREAK
BOS
CHoCH
STRUCTURAL REGIME
```

### Execution Engine owns

```text
VALID OF
VALID OB
POI REGISTRY / POI LIFECYCLE
IDM SWEEP EXECUTION MODULE
DECISIONAL POI MITIGATION
ENGINEERING LIQUIDITY SWEEP
EXTREME POI MITIGATION
CANDLE REVERSAL CONFIRMATION
ENTRY TRIGGER
```

### Risk Engine owns

```text
SCORING
STOP POLICY
TARGET POLICY
RR GATING
PENDING ORDER LIFECYCLE
OPEN POSITION LIFECYCLE
EXECUTION STOP
```

Absolute boundaries:

```text
EXECUTION MUST NEVER CREATE OR MODIFY:
BOS
CHoCH
CONFIRMED SWING
TRADING RANGE
PROTECTED STRUCTURAL EXTREME
MINOR IDM
REAL MAJOR IDM
FALLBACK MAJOR IDM

RISK MUST NEVER CREATE OR VALIDATE STRUCTURE.
```

Execution may consume a structural event and produce an execution event. Risk may consume structural/execution state and produce a risk event. Neither downstream layer may redefine structural truth.

---

# 2. LAYER 1 — CANDLE-LEVEL FOUNDATION

Source: `01_candle_level_foundation.md`.

## 2.1 Raw OHLC boundary

```text
RAW OHLC
  ↓
CANDLE RELATIONSHIPS
  ↓
CANDLE-LEVEL VALID PULLBACK
  ↓
LAYER 2
```

Candle relationships are observations. They do not automatically create Valid Pullback, SVP, IDM, Swing, BOS, CHoCH, or Trading Range.

Required non-equivalences:

```text
CANDLE RELATIONSHIP ≠ VALID PULLBACK
CANDLE RELATIONSHIP ≠ STRUCTURALLY VALID PULLBACK
CANDLE RELATIONSHIP ≠ IDM
CANDLE RELATIONSHIP ≠ CONFIRMED SWING
CANDLE RELATIONSHIP ≠ BOS
CANDLE RELATIONSHIP ≠ CHoCH
LIQUIDITY ≠ STRUCTURE
CANDLE REVERSAL ≠ STRUCTURE
CONFIGURATION ≠ CANONICAL METHODOLOGY
```

## 2.2 EQH / EQL reference transfer

Bullish EQH sequence:

```text
1. two consecutive candles have equal highs
2. shared high = EQH
3. second candle becomes active reference
4. break below second candle Low
5. break above shared High
6. candle-level Valid Pullback completed
```

Bearish EQL mirror:

```text
1. two consecutive candles have equal lows
2. shared low = EQL
3. second candle becomes active reference
4. break above second candle High
5. break below shared Low
6. candle-level Valid Pullback completed
```

Reference transfer does not itself create structure.

## 2.3 Strict Inside Bar

```text
current.High < mother.High
AND
current.Low  > mother.Low
```

Equality does not qualify.

The inside bar cannot independently establish a structural sweep or liquidity extreme. If an execution-layer Order Block refinement uses an inside-bar base, the Mother Bar owns the sweep and the inside bar only narrows execution coordinates.

## 2.4 Outside Bar

A single outside bar cannot activate both directional branches.

Canonical sequencing:

```text
Bullish context → LOW → HIGH
Bearish context → HIGH → LOW
```

The outside-bar relationship remains a candle-level observation until the higher structural gates are satisfied.

## 2.5 Candle-level Valid Pullback

### Bullish

```text
valid reference High exists
→ price breaks reference High
→ price subsequently breaches reference Low
→ wick or body breach is valid
→ candle color is irrelevant
→ price subsequently breaks continuation/reference High
→ Valid Pullback
```

### Bearish

```text
valid reference Low exists
→ price breaks reference Low
→ price subsequently breaches reference High
→ wick or body breach is valid
→ candle color is irrelevant
→ price subsequently breaks continuation/reference Low
→ Valid Pullback
```

A single previous-candle low/high breach is not enough.

## 2.6 Reversal pattern observations

The six canonical execution observations are:

```text
Long Wick Rejection
Multiple Wick Rejection
Engulfing / Outside-Bar Reversal
Momentum Candle
Morning / Evening Star
Shrinking Candles
```

They never manufacture structure.

Long Wick execution polarity:

```text
bullish → Close > Open
bearish → Close < Open
```

Engulfing:

```text
Bullish:
Low_t < Low_(t-1)
AND Close_t > max(Open_(t-1), Close_(t-1))
AND Close_t > Open_t

Bearish:
High_t > High_(t-1)
AND Close_t < min(Open_(t-1), Close_(t-1))
AND Close_t < Open_t
```

Morning Star / Evening Star:

```text
Bullish:
Close_(t-2) < Open_(t-2)
Close_t > Open_t
Close_t > (Open_(t-2) + Close_(t-2))/2

Bearish:
Close_(t-2) > Open_(t-2)
Close_t < Open_t
Close_t < (Open_(t-2) + Close_(t-2))/2
```

The `t-1` small-body condition is qualitative. Momentum and Shrinking Candle morphology are qualitative unless independently quantified by an authoritative source.

---

# 3. LAYER 2 — MINOR STRUCTURE / PULLBACK / LIQUIDITY / IDM

Source: `02_minor_structure.md`.

## 3.1 Dependency chain

```text
RAW OHLC
 ↓
CANDLE RELATIONSHIPS
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
ACTIVE / MINOR IDM
 ↓
LAYER 3
```

No stage may be skipped.

## 3.2 Verified Pullback Extreme

```text
Bullish → Pullback Low
Bearish → Pullback High
```

It is a candidate liquidity reference, not automatic IDM.

## 3.3 Structural retracement qualification

### Standard

```text
>= 3 opposing candles
AND
>= configured minimum retracement depth
```

Canonical default minimum: `38.2%`.

### Exactly-two-candle exception

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

No automatic one-candle exception.

High momentum is qualitative/source-pending. Do not invent ATR/body-ratio/volatility thresholds.

If insufficient:

```text
IMPULSE_EXTENSION
```

not structural reset, protected extreme, or range rollover.

## 3.4 Active pullback pointer

Only the newest Structurally Valid Pullback remains the active pointer for the active leg.

```text
NEW SVP
 ↓
ACTIVE PULLBACK POINTER TRANSFER
 ↓
ACTIVE/MINOR IDM TARGET TRANSFER
```

Historical IDM may remain historical but cannot remain a competing active target.

## 3.5 IDM ontology

IDM is liquidity beyond the most recent Structurally Valid Pullback on the active impulsive leg.

Therefore:

```text
SVP
→ Verified Pullback Extreme
→ Liquidity
→ IDM Eligibility
→ ACTIVE/MINOR IDM
```

Not IDM:

```text
random bar
arbitrary pivot
inside bar
arbitrary local high/low
Fibonacci level
visible liquidity pool without provenance
```

Minor IDM is internal liquidity and is not Confirmed Swing, Protected Extreme, BOS, CHoCH, or Trading Range.

## 3.6 IDM takeout

Qualified IDM can be taken by wick or body. A body close is not required.

```text
QUALIFIED IDM
→ WICK OR BODY TAKEOUT
→ IDM SWEEP
```

An arbitrary level cannot become IDM merely because price touches it.

---

# 4. LAYER 3 — MAJOR STRUCTURE / GENESIS / SWING / BOS / CHoCH

Sources: `03_structural_lifecycle.md`, `03_structural_lifecycle_bos.md`, `03_structural_lifecycle_choch.md`.

## 4.1 Major Structure

Major Structure is governed by the active Trading Range and canonical external boundaries.

```text
Minor Structure / IDM / internal liquidity
        ≠
Major Structure / external range boundary
```

## 4.2 Genesis / Bootstrap

Before first confirmed IDM sweep / confirmation cycle, use an unconfirmed expansion state such as `BOOTSTRAP_EXPANSION`.

Bootstrap may detect candidates but must not fabricate Confirmed Swing, Protected Structural Extreme, or normal confirmed range.

## 4.3 Swing Confirmation Gate

Canonical conceptual path:

```text
Qualified IDM
 ↓
IDM Takeout
 ↓
Swing Confirmation Gate UNLOCKED
 ↓
Remaining swing prerequisites
 ↓
CONFIRMED SWING
```

A Major IDM sweep, Minor IDM sweep, or fallback sweep does not automatically equal Confirmed Swing.

## 4.4 Confirmed Swing vs Protected Structural Extreme

```text
CONFIRMED SWING ≠ PROTECTED STRUCTURAL EXTREME
```

Protected Structural Extreme is created/locked by valid BOS, not merely by swing confirmation.

## 4.5 Dynamic retracement extreme

Bullish:

```text
E_retrace(t) = min(Low_k)
```

Bearish:

```text
E_retrace(t) = max(High_k)
```

The extreme remains dynamic until valid BOS.

## 4.6 BOS reference and physical break

BOS reference must be an eligible Confirmed Structural Swing:

```text
bullish → Confirmed Swing High
bearish → Confirmed Swing Low
```

Physical break:

```text
bullish: High_t > Confirmed_Swing_High
bearish: Low_t < Confirmed_Swing_Low
```

Physical break is not automatically BOS.

## 4.7 BOS classification

Standard gates:

```text
ELIGIBLE CONFIRMED SWING
+
RETRACEMENT SUFFICIENCY
+
PHYSICAL EXTERNAL BREAK
+
CORRECT PROVENANCE
+
NON-FALLBACK FINAL CLASSIFICATION
→ VALID_BOS
```

Body-close BOS:

```text
bullish: Close_t > Confirmed_Swing_High
bearish: Close_t < Confirmed_Swing_Low
```

Wick-BOS:

```text
bullish: High_t > Confirmed_Swing_High AND Close_t <= Confirmed_Swing_High
bearish: Low_t < Confirmed_Swing_Low AND Close_t >= Confirmed_Swing_Low
```

Equality at the broken level is valid in the wick-BOS branch.

Wick-BOS is immediate; it does not wait for a later close.

## 4.8 Fallback Major IDM

Fallback Major IDM is an external Range-Boundary Proxy, not Real Major IDM and not internal liquidity.

Fallback wick:

```text
bullish: High_t > Level AND Close_t <= Level
bearish: Low_t < Level AND Close_t >= Level
→ MAJOR_IDM_SWEEP
```

Fallback wick is not:

```text
VALID_BOS
VALID_CHoCH
TRADING_RANGE_ROLLOVER
PROTECTED_EXTREME_LOCK
```

It unlocks the Swing Confirmation Gate but does not automatically create Confirmed Swing.

Fallback body close through opposing boundary is only CHoCH-eligible pending the complete CHoCH prerequisite gate.

Fallback does not directly become Real Major IDM.

Real Major IDM lineage:

```text
VALID_BOS
→ FIRST QUALIFYING POST-BOS SVP
→ VERIFIED PULLBACK EXTREME
→ MAJOR IDM ELIGIBILITY
→ REAL_MAJOR_IDM
→ FALLBACK SUPERSEDED
```

## 4.9 Protected Extreme / range rollover

```text
VALID_BOS
→ E_retrace LOCKED
→ PROTECTED STRUCTURAL EXTREME
→ PREVIOUS RANGE CLOSED
→ NEW RANGE ACTIVE
```

Only valid BOS rolls the Trading Range.

---

# 5. POST-CHoCH DUAL-LINEAGE

This is a critical locked architecture rule.

A valid CHoCH creates a new trend but not an immediately confirmed normal range.

```text
VALID_CHoCH
 ↓
OLD TREND TERMINATED
 ↓
NEW TREND
 ↓
INITIAL_ACTIVE_IMPULSE
 ↓
CONFIRMATION_LOCKED
```

The new regime has two parallel provenance branches:

```text
VALID_CHoCH
├─ MINOR IDM LINEAGE
│  └─ FIRST_POST_CHOCH_SVP
│     → VERIFIED_PULLBACK_EXTREME
│     → IDM ELIGIBILITY
│     → FIRST_POST_CHOCH_MINOR_IDM
│     → MINOR_IDM_SWEEP
│     → SWING CONFIRMATION GATE
│     → CONFIRMED SWING
│     → FIRST VALID BOS
│
└─ FALLBACK PROXY LINEAGE
   └─ EXTERNAL PREVIOUS PROTECTED / RANGE BOUNDARY
      → FALLBACK_MAJOR_IDM
```

Mandatory distinctions:

```text
FIRST_POST_CHOCH_SVP ≠ FIRST_POST_CHOCH_MINOR_IDM
FIRST_POST_CHOCH_MINOR_IDM ≠ FALLBACK_MAJOR_IDM
FALLBACK_MAJOR_IDM ≠ REAL_MAJOR_IDM
```

Fallback wick is `MAJOR_IDM_SWEEP`. Minor IDM sweep and fallback sweep may unlock the confirmation gate but do not automatically create Confirmed Swing.

The first valid BOS after CHoCH completes the normal structural confirmation lifecycle.

---

# 6. LAYER 3 STATE MACHINE

## 6.1 Canonical states

```text
BOOTSTRAP
CONFIRMATION_LOCKED
CONFIRMED_RANGE
POST_BOS
POST_CHOCH
```

## 6.2 Event classes

Exactly one event class must be detected for a structural evaluation:

```text
NO_EVENT / INTERNAL_PB
MINOR_IDM_EVENT
EXT_CONT_BREAK
EXT_OPP_BREAK
FALLBACK_EVENT
REAL_MAJOR_IDM_EVENT
NEW_SVP_QUALIFIED
```

Detection precedence:

```text
EXT_OPP_BREAK
>
EXT_CONT_BREAK
>
FALLBACK_EVENT
>
REAL_MAJOR_IDM_EVENT
>
MINOR_IDM_EVENT
>
NEW_SVP_QUALIFIED
>
NO_EVENT / INTERNAL_PB
```

This is **classification/detection precedence**, not intrabar chronology.

```text
OHLC ≠ INTRABAR_SEQUENCE
```

## 6.3 Continuation path

```text
CANDLE PULLBACK
→ SVP
→ Verified Extreme
→ IDM
→ IDM Sweep
→ Swing Confirmation
→ Confirmed Swing
→ Retracement Sufficiency
→ External Break
→ BOS Classification
→ VALID_BOS
→ Protected Extreme Lock
→ Range Rollover
→ POST_BOS
```

## 6.4 Opposing path

```text
Protected Opposing Extreme
→ Physical Opposing Break
→ CHoCH Eligibility
→ all prerequisites
→ VALID_CHoCH
→ NEW TREND
→ INITIAL_ACTIVE_IMPULSE
→ CONFIRMATION_LOCKED
```

## 6.5 Fallback path

```text
Fallback Proxy
→ Wick Breach
→ MAJOR_IDM_SWEEP
→ Gate Unlock
→ remaining Swing prerequisites
```

Never:

```text
Fallback Wick → BOS
Fallback Wick → CHoCH
Fallback Wick → Range Rollover
Fallback Wick → Protected Extreme
```

---

# 7. CURRENT IMPLEMENTATION LOGIC TO AUDIT

The following describes the implementation currently present in `SMC_mapper.py` on this branch. Treat this section as **implementation evidence**, not as canonical authority. Where implementation contradicts Sections 1–6, report the contradiction.

## 7.1 Configuration

`SMC_mapper.py` loads `config.json` and requires the `mapper` section. Relevant settings include:

```text
TICKERS
INTERVAL
BAR_COUNT
HISTORY_SIZE
EQUAL_LEVEL_TOLERANCE
DEBUG
BOS_MIN_RETRACEMENT_PCT
```

`BOS_MIN_RETRACEMENT_PCT` defaults to `0.382` in code.

## 7.2 Actual state representation

`EngineState` currently contains:

```text
trend
implied_trend
bias_source
protected_high
protected_low
weak_high
weak_low
candidate_high
candidate_low
dealing_range
reference_index
reference_high
reference_low
pullback
minor_idm
major_idm
mother_bar_index
eqh_history
eql_history
last_swept_idm_price
last_swept_idm_time
last_swept_idm_type
current_leg_id
last_valid_idm_sweep_leg_id
liquidity
bos
choch
range_has_bos
last_pullback_depth
structure_history
debug_log
```

There is no explicit authoritative enum field named `POST_CHOCH` or `TRANSITION_REGIME` in the current `EngineState`; this must be audited against the canonical confirmation-lock requirement.

`IDMState` distinguishes:

```text
major: bool
fallback: bool
active: bool
swept: bool
liquidity: bool
leg_id
```

## 7.3 Swing detection implementation

`get_swings()` detects pivots using:

```text
pivot high:
High_i >= High_(i-1)
AND
High_i > High_(i+1)

pivot low:
Low_i <= Low_(i-1)
AND
Low_i < Low_(i+1)
```

It is used to bootstrap initial context.

Audit whether this pivot helper is being used only as a candidate/reference mechanism or is being allowed to manufacture canonical Confirmed Swing / Protected Structural Extreme state.

## 7.4 IDM implementation

`replace_minor_idm()` retires the previous active unswept Minor IDM to liquidity and creates a new active Minor IDM using the current active direction and current leg ID.

`replace_major_idm()` creates either:

```text
major=True, fallback=True
```

or:

```text
major=True, fallback=False
```

`retire_to_liquidity()` moves unswept IDMs into a liquidity list while retaining historical provenance.

`sweep_idms()` treats a Minor IDM or Major IDM as swept when:

```text
LOW IDM and candle.Low < IDM.price
OR
HIGH IDM and candle.High > IDM.price
```

No body-close requirement is applied to IDM takeout.

`has_taken_idm()` requires the latest swept IDM's `leg_id` to equal `current_leg_id`.

Audit whether this correctly distinguishes the canonical Swing Confirmation Gate and whether Major/Minor/Fallback provenance remains ontologically correct through all transitions.

## 7.5 Pullback implementation

`is_structurally_valid_pullback()` currently counts structural opposing movement rather than candle color:

Bullish opposing movement:

```text
candle.High < previous.High
OR
candle.Low < previous.Low
```

Bearish opposing movement:

```text
candle.High > previous.High
OR
candle.Low > previous.Low
```

Standard qualification:

```text
opposing_count >= 3
AND
retracement >= threshold
```

Two-candle exception:

```text
opposing_count == 2
AND
large_momentum == True
AND
(swept >= 5 OR depth_ok)
```

The implementation counts prior extremes in a bounded lookback of 20 bars. The canonical methodology does not authorize an arbitrary 20-bar universal lookback unless that parameter is explicitly canonicalized. Flag this if materially inconsistent with the authoritative source.

Important implementation detail: the code comments state that the engine does **not** invent an ATR/body-ratio definition for high momentum. However, the `large_momentum` argument must be traced to its actual callers; determine whether it can ever become true and whether the canonical two-candle exception is actually executable.

`finish_pullback()`:

```text
update_pullback_depth()
→ is_structurally_valid_pullback()
→ if fail: deactivate pullback
→ if pass: mark confirmed
→ replace_minor_idm()
→ if existing fallback Major IDM: retire fallback + create real Major IDM
→ if existing inactive Major IDM: create real Major IDM
```

This is an implementation-critical area. The canonical lifecycle says a fallback proxy is superseded by an independently qualified Real Major IDM after the post-break SVP → Verified Extreme → eligibility chain; do not describe the object operation as a semantic conversion unless the implementation actually preserves that distinction.

## 7.6 CHoCH implementation

`choch_qualified()` currently checks a body-oriented breaker reference against the protected/reference close and uses the active trend. In the current implementation:

```text
BULLISH opposing break:
level = protected_high.price OR dealing_range.high
candle.high must exceed level
breaker_reference(candle, BULLISH) > level_close

BEARISH opposing break:
level = protected_low.price OR dealing_range.low
candle.low must be below level
breaker_reference(candle, BEARISH) < level_close
```

Audit this against the canonical OHLC definition:

```text
Bullish trend CHoCH:
Low_t < Protected_Swing_Low

Bearish trend CHoCH:
High_t > Protected_Swing_High
```

with body-close vs wick classification and fallback provenance.

The current code path calls `reset_for_choch()` and then reconstructs a `dealing_range` immediately. The reset clears:

```text
major_idm = None
minor_idm = None
protected_high = None
protected_low = None
range_has_bos = False
pullback = None
```

It increments `current_leg_id`, changes trend/bias, and preserves retired liquidity/history.

After reset, the current implementation reconstructs a new `RangeState` and sets weak/candidate state around the CHoCH candle. Audit this against the canonical requirement that post-CHoCH confirmation remains locked until the first post-CHoCH SVP → Minor IDM → sweep → Swing Confirmation lifecycle completes.

## 7.7 BOS implementation

`bullish_break_qualified()` / `bearish_break_qualified()` require:

```text
physical break
AND
body-style breaker reference beyond weak.close
AND
has_taken_idm(state)
AND
retracement >= BOS threshold
```

This must be compared with the canonical separation of physical break, body-close BOS, and wick-BOS.

The current per-bar processor updates candidate extremes and may update `weak_high` / `weak_low` before BOS evaluation. Audit whether these candidate/weak levels can become BOS references without canonical Confirmed Swing provenance.

The current code also has a genesis BOS path when `trend == UNCONFIRMED` and an initial weak level is broken after an IDM sweep. Audit whether this creates Protected Structural Extreme / Trading Range state earlier than canonical genesis permits.

## 7.8 Outside-bar implementation

`_process_outside_bar()` treats a real outside bar as one state-machine event and uses candle body direction to determine physical sequencing:

```text
bullish candle → LOW → HIGH
bearish candle → HIGH → LOW
```

It avoids processing the same physical candle twice and defers structural confirmation to a later candle.

Audit whether the implementation's sequencing convention is an allowed candle-level abstraction or whether it improperly infers intrabar chronology that the methodology says cannot be known from OHLC alone.

## 7.9 Main loop / EQH-EQL

`run_true_smc()`:

1. initializes from detected pivots;
2. processes each candle;
3. checks reference breaks;
4. when neither break occurs, checks EQH/EQL and transfers reference boundaries to the current candle;
5. performs IDM sweeps;
6. detects outside bars and processes them as one event;
7. otherwise calls `_process_bar()`.

The current implementation records equal-high/equal-low history and transfers reference boundaries to the EQ candle while preserving mother provenance in comments/history. Audit against the exact canonical EQH/EQL reference transfer rule.

## 7.10 Mapper/scoring implementation

`build_mapper_result()` currently computes:

```text
Structure Quality = 25%
Setup Quality     = 30%
Location Quality  = 20%
Liquidity Quality = 15%
Risk Quality      = 10%
```

It uses quality values including:

```text
Real Major IDM = 80
Fallback Major IDM = 40
```

and risk penalties including:

```text
retracement > 78.6% → -25
retracement > 90%   → stronger penalty
```

The implementation also contains Fibonacci display/diagnostic levels such as:

```text
23.6, 38.2, 50.0, 61.8, 68.0, 78.6, 88.6
```

Audit that these are presentation/scoring diagnostics only and that obsolete Fibonacci variants are not promoted to structural identity.

Location scoring currently uses:

```text
pct > 0.618 → PREMIUM
pct < 0.382 → DISCOUNT
else → EQUILIBRIUM
```

This must be compared with the execution-layer canonical equilibrium gate and must not silently redefine the required Decisional POI location rule.

---

# 8. EXECUTION ENGINE — POI / SMT / DIRECT ENTRY

Source: `04_execution.md`.

## 8.1 Closed binary POI set

Only:

```text
VALID_OF
VALID_OB
```

are tradable POIs.

Never promote these into standalone POIs:

```text
FVG
Breaker Block
Mitigation Block
Liquidity Void
arbitrary liquidity pool
IDM
generic displacement zone
```

FVG is an OB-validation property only.

## 8.2 Priority

Canonical priority:

```text
Decisional OF
→ Decisional OB
→ Extreme OF
→ Extreme OB
```

If an unmitigated valid OF is applicable, do not invent a separate competing OB merely because an OB-shaped candle is visually available.

OF touch may be tradable where the canonical module permits it.

## 8.3 Rule of Two

```text
DECISIONAL POI
+
EXTREME POI
```

Maximum two canonical tradable POIs per dealing-range lifecycle.

## 8.4 SMT filters

Audit:

```text
NO IDM → NO TRADE
```

where the applicable execution route requires core IDM eligibility.

Intermediate zones between Decisional and Extreme POI are deleted/excluded where the canonical SMT rule requires it.

Do not allow arbitrary additional visually attractive zones to survive as tradable POIs.

## 8.5 Equilibrium gating

```text
BUY DECISIONAL POI → DISCOUNT
SELL DECISIONAL POI → PREMIUM
```

The current execution file defines normalized boundaries as `< 0.50` and `> 0.50`. Audit implementation against that exact execution rule rather than the scoring layer's separate 0.382/0.618 quality bands.

## 8.6 Origin OB fallback

Origin OB remains an independently validated execution object. Mitigation of parent OF does not automatically destroy a valid Origin OB.

If all applicable OF are mitigated, the execution sequence may proceed to the canonical Extreme/Origin OB fallback only when that POI independently satisfies all validation pillars.

## 8.7 OB validation

All three are required:

```text
1. origin of impulsive displacement causing structural BOS
2. candle sweeps previous candle extreme
3. active fully unmitigated adjacent FVG
→ VALID_OB
```

No pillar may be inferred from generic SMC convention.

## 8.8 Refinement formulas

Wick-only bullish:

```text
OB_bottom = Low_base
OB_top = max(Open_base, Close_base)
```

Wick-only bearish:

```text
OB_top = High_base
OB_bottom = min(Open_base, Close_base)
```

Inside-bar bullish:

```text
OB_bottom = Low_(t-1)   # Mother Bar
OB_top = Low_t          # Inside Bar
```

Inside-bar bearish:

```text
OB_top = High_(t-1)     # Mother Bar
OB_bottom = High_t      # Inside Bar
```

These are coordinate refinements only; they do not relax OB validation.

## 8.9 Direct-entry gating

A candle reversal can authorize entry only after an eligible execution context exists:

```text
QUALIFIED DECISIONAL/EXTREME OF/OB MITIGATION
OR
CORE IDM SWEEP
OR
ENGINEERING LIQUIDITY SWEEP
        ↓
CANDLE REVERSAL
        ↓
CANDLE CLOSE
        ↓
DIRECT ENTRY
```

Open wick is never an entry trigger.

## 8.10 Six direct-entry patterns

### Long Wick Rejection

```text
small body
extended rejection wick
eligible POI/liquidity interaction
bullish: Close > Open
bearish: Close < Open
```

If polarity fails, wait for the required subsequent confirming candle.

### Multiple Wick Rejection

Two or more consecutive rejection candles interact with the same eligible execution context. The decisive rejecting candle must close with the required direction before entry.

### Shrinking Candles

Approach filter only:

```text
SHRINKING ≠ ENTRY
```

### Engulfing

Exact formulas as in Layer 1 above. Wick sweep is mandatory.

### Momentum

Immediate above-average full-bodied expansion with minimal opposing wick. Qualitative/source-pending unless authoritative quantitative criteria exist.

### Morning / Evening Star

Exact three-candle structure and 50% body-midpoint close condition from Layer 1 above.

Harami and Doji are indecision observations and cannot authorize direct entry without a separately canonical confirmation route.

## 8.11 Execution non-equivalences

```text
CANDLE_PATTERN ≠ POI
CANDLE_PATTERN ≠ IDM
CANDLE_PATTERN ≠ ENG_LQD
CANDLE_PATTERN ≠ SWING
CANDLE_PATTERN ≠ BOS
CANDLE_PATTERN ≠ CHoCH
CANDLE_PATTERN ≠ TRADING_RANGE
POI FAILURE ≠ STRUCTURAL FAILURE
```

---

# 9. RISK ENGINE

Source: `05_risk.md`.

## 9.1 Tier 1 stop

Zone/macro invalidation beyond the relevant parent Valid OF/OB boundary.

It is not automatically structural invalidation, BOS, CHoCH, IDM, or range failure.

## 9.2 Tier 2 pattern stop

Only after deterministic candle-confirmed entry:

```text
Bullish SL = min(Low_pattern_candles) - P
Bearish SL = max(High_pattern_candles) + P
```

`P` is downstream/configurable. Do not invent universal pip/tick or Spread+Tick values.

## 9.3 Target

Primary pro-trend target where applicable:

```text
bullish → current Confirmed_Swing_High
bearish → current Confirmed_Swing_Low
```

Minimum executable RR where required:

```text
Projected_RR_to_Primary_Target >= 1:2
```

The RR threshold is a gate, not a target location.

## 9.4 Target independence

```text
TARGET_HIT ≠ VALID_BOS
```

A profit-taking event does not validate a structural breakout.

## 9.5 Pending vs open position

Pending order invalidation:

```text
ORDER_FLOW_FAILED / ORDER_BLOCK_FAILED
→ PENDING_ORDER_CANCELLED
```

Range rollover:

```text
VALID_BOS
→ previous-range dependent pending orders expire/cancel
```

CHoCH:

```text
VALID_CHoCH
→ pending orders dependent on invalidated regime cancel
```

An already-open position is not automatically closed merely because POI/zone failure or CHoCH occurred.

## 9.6 Zone failure

Bullish:

```text
Close < lower_zone_boundary
```

Bearish:

```text
Close > upper_zone_boundary
```

Wick penetration alone is not zone failure unless an explicit canonical rule says so.

## 9.7 G1

```text
OHLC ≠ INTRABAR_SEQUENCE
```

If both STOP_TOUCH and TARGET_TOUCH are reachable within one OHLC candle, do not invent their order. Require lower-timeframe/tick/broker data.

## 9.8 Risk scoring

Canonical weights:

```text
Structure 25%
Setup 30%
Location 20%
Liquidity 15%
Risk 10%
```

Quality tiers:

```text
HIGH >= 70
MEDIUM >= 55
LOW >= 40
WATCH < 40
```

Risk/scoring remains downstream and cannot manufacture structure.

---

# 10. REQUIRED ONTOLOGY / PROVENANCE AUDIT

Construct actual provenance for each object:

```text
SVP
← Candle-Level Valid Pullback
← Structural Retracement Qualification

Verified Pullback Extreme
← Structurally Valid Pullback

Minor IDM
← SVP
← Verified Pullback Extreme
← Liquidity / IDM Eligibility

Real Major IDM
← VALID_BOS
← Post-BOS SVP
← Verified Pullback Extreme
← Major IDM Eligibility

Fallback Major IDM
← External Protected Structural Extreme / Range Boundary Proxy
```

Flag any implementation path where:

```text
Candle pattern → IDM
Liquidity → IDM without SVP
Minor IDM → Real Major IDM by age
Fallback → Real Major IDM by mutation rather than independent lifecycle
IDM → BOS
IDM → CHoCH
POI → structure
Risk score → structure
```

---

# 11. REQUIRED ADVERSARIAL TEST MATRIX

At minimum test:

```text
bullish Valid Pullback
bearish Valid Pullback
EQH reference transfer
EQL reference transfer
strict inside-bar exclusion
outside-bar LOW→HIGH
outside-bar HIGH→LOW
standard 3-candle retracement
2-candle high-momentum exception
2-candle >=38.2 exception
1-candle rejection
new SVP replacing old Minor IDM
Minor IDM wick sweep
Minor IDM body sweep
fallback wick sweep
fallback body close
fallback sweep without confirmed swing
first post-CHoCH SVP
first post-CHoCH Minor IDM
first post-CHoCH Minor IDM sweep
first valid post-CHoCH BOS
first post-BOS SVP
Real Major IDM creation
fallback supersession
physical external break without valid BOS
wick-BOS
body-close BOS
wick CHoCH with Real Major IDM
body-close CHoCH eligibility
fallback wick not CHoCH
TARGET_HIT without BOS
POI failure without structural failure
CHoCH_ELIGIBLE without VALID_CHoCH
same-candle STOP/TARGET ambiguity
standalone FVG
invalid OB missing one pillar
Rule of Two
Decisional premium/discount gate
Origin OB fallback
Harami/Doji direct-entry rejection
Shrinking Candle non-trigger
Momentum source-pending behavior
```

For every test report:

```text
INPUT STATE
INPUT EVENT
EXPECTED CLASSIFICATION
ACTUAL CLASSIFICATION
EXPECTED NEXT STATE
ACTUAL NEXT STATE
PROVENANCE
RESULT
```

---

# 12. IMPLEMENTATION FINDINGS MUST BE SEPARATE FROM METHODOLOGY FINDINGS

Do not mark the methodology invalid because implementation is wrong.

Use:

```text
METHODOLOGY: PASS / CONFLICT / SOURCE-PENDING
IMPLEMENTATION: PASS / FAIL / TEST_FAILURE
```

In particular, audit the known high-risk implementation boundaries:

1. `reset_for_choch()` currently clears `major_idm`, `minor_idm`, and protected levels.
2. The current CHoCH path reconstructs `dealing_range` immediately after reset.
3. The canonical post-CHoCH model requires confirmation lock and dual Minor/Fallback lineage.
4. Current `finish_pullback()` can create a Real Major IDM from an existing fallback Major IDM after SVP qualification; verify the semantic lifecycle and whether the implementation preserves “superseded” rather than silently mutating identity.
5. Current BOS qualification uses `has_taken_idm()` and body-style `breaker_reference`; compare it with the canonical physical-break / body-close / wick-BOS separation.
6. Current `choch_qualified()` uses a body-oriented breaker reference and may fall back to `dealing_range` boundaries; compare with the canonical protected opposing structural extreme and explicit wick/body rules.
7. Current initialization can create a provisional `dealing_range` from the earliest detected pivots before a canonical confirmation lifecycle; audit whether this is only bootstrap context or is exposed as confirmed structure.
8. Current location scoring uses 0.382/0.618 bands while execution Decisional POI gating uses `<0.50` / `>0.50`; these must remain separate semantics.
9. Current implementation has a 20-bar prior-extreme lookback for the two-candle exception; verify whether that is an authorized parameter or implementation invention.
10. Current outside-bar handling deliberately treats each real candle as one structural state-machine step; audit the distinction between candle-level directional convention and forbidden intrabar chronology inference.

---

# 13. FINAL REQUIRED OUTPUT

Return a rigorous audit, not a summary.

## A. Repository state

```text
Repository
Branch
HEAD
Relevant source files
Implementation revision
```

## B. Architecture verdict

```text
PASS
PASS WITH QUALIFICATIONS
FAIL
```

## C. Layer verdict table

| Layer | Verdict | Critical Findings |
|---|---|---|
| Layer 1 | | |
| Layer 2 | | |
| Layer 3 | | |
| Execution | | |
| Risk | | |
| Implementation | | |

## D. Ontology / provenance

List every identity collapse, skipped prerequisite, illegal mutation, and provenance leak.

## E. State transition audit

For every critical event report:

```text
CURRENT STATE
→ EVENT CLASS
→ GUARD
→ CLASSIFICATION
→ NEXT STATE
→ SIDE EFFECTS
```

## F. Generic ICT contamination

Only report unsupported generic behavior that materially changes ontology or execution. Do not reject terminology merely because it resembles generic ICT.

## G. Regression tests

Separate methodology failures from implementation test failures.

## H. Remediation

For each implementation failure:

```text
TEST_FAILURE
→ REQUIRED CORRECTION
→ REGRESSION TEST
```

If the correct behavior cannot be established from authoritative material:

```text
HUMAN_REVIEW_REQUIRED
```

## I. Final verdict

The final verdict must explicitly state:

```text
METHODOLOGY CONSISTENCY
ONTOLOGY CONSISTENCY
PROVENANCE CONSISTENCY
STATE-MACHINE CONSISTENCY
EXECUTION DECOUPLING
RISK DECOUPLING
GENERIC CONTAMINATION STATUS
IMPLEMENTATION COMPLIANCE
```

Never use a generic SMC interpretation to silently repair the implementation. The validator's role is independent verification, contradiction detection, and precise remediation guidance — not methodology redesign.