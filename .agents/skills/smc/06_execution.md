# EXECUTION

**Role:** Trading/execution-layer rules built on validated structural facts.

**Boundary:** Execution consumes structure; execution must never manufacture structural truth.

## 36. POI ontology — canonical tradable POIs

The canonical POI ontology is a closed set. A tradable Point of Interest may be either **Valid Order Flow (OF_CONFIRMED)** or **Valid Order Block (Valid OB)**. No third POI entity may be introduced by generic SMC convention or implementation convenience.

```text
OF_CONFIRMED
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

### Rule of Two POIs (Structural Constraint & Origin OB)

An active dealing range may contain a MINIMUM of one and a MAXIMUM of two actively tradable POIs:
1. **Decisional POI** (must reside in Discount for Buys, Premium for Sells)
2. **Extreme POI** (Extreme OF / Extreme OB)

```text
DECISIONAL POI
      +
 EXTREME POI
```

Everything outside the active one-or-two-POI structure is non-tradable/SMT unless a canonical rule explicitly promotes it. Multiple arbitrary POIs must not be created merely because multiple zones are visually present. Any logic that permits three simultaneously active POIs in the scanner is strictly forbidden.

### Origin OB Rule

Origin OB is a **LATENT reserve POI, NOT a third active POI**. It sits at the absolute origin of the dealing range. It becomes actively tradable IF AND ONLY IF Extreme Order Flow was mitigated AND Extreme Order Block fails, without price producing a CHoCH.

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
POI ∈ {OF_CONFIRMED, VALID_OB}
STANDALONE_FVG → NOT_POI
IDM → NOT_POI
LIQUIDITY → NOT_POI
POI → NOT_STRUCTURE
POI → NOT_BOS
POI → NOT_CHoCH
POI → NOT_AUTOMATIC_ENTRY
FVG → OB_VALIDATOR_ONLY
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

The Extreme POI must still be an OF_CONFIRMED or Valid OB. It is not an arbitrary fallback to any visually convenient zone.

### Origin OB (Latent POI)

An Origin OB is a canonical absolute range-origin Order Block acting as a latent reserve POI. It becomes actively tradable if and only if Extreme Order Flow was mitigated and Extreme Order Block fails, without price producing a CHoCH. It is not required to disappear merely because its parent Valid Order Flow has been mitigated. Its validity must be evaluated according to the OB validation rules rather than by inheritance from the current OF state.

## 37.5 Order Flow Identification and Selection

Order Flow is a canonical execution-location precursor. It is not synonymous with an Order Block, POI, IDM, or liquidity level.

### Order Flow candidate

An `OF_CANDIDATE` is the **last opposing move** that occurs before price continues or displaces in the dominant direction on the active impulsive leg.

```text
OPPOSING MOVE
    ↓
CONTINUATION / DISPLACEMENT
    ↓
OF_CANDIDATE
```

When the corrective move contains multiple internal legs and its protected endpoint remains intact, the Order Flow represents the **whole corrective move**, not merely its final internal sub-leg.

### Valid / unmitigated Order Flow

An OF candidate is execution-eligible only when it remains unmitigated under the canonical pullback-based mitigation rule and it is not excluded by the active inducement boundary.

```text
OF_CANDIDATE
   ├─ MITIGATED → INVALID_FOR_EXECUTION
   ├─ BEFORE_ACTIVE_INDUCEMENT → SMT / INDUCEMENT_TRAP
   └─ UNMITIGATED + ELIGIBLE → OF_CONFIRMED
```

A physical touch or penetration alone does **not** confirm OF mitigation. The mitigation state is confirmed only through a canonical Valid Pullback interaction. If the interaction is not validated by a Valid Pullback, the OF remains unmitigated.

### SMT / pre-inducement exclusion

For the active dealing-range execution process, an Order Flow or equivalent formation that occurs **before the active inducement** is classified as an `SMT / INDUCEMENT_TRAP` observation and is not eligible to become a tradable OF.

Pre-inducement status is contextual to the active dealing range and inducement lifecycle. It must not be inferred from candle appearance alone.

```text
PRE-IDM FORMATION
    ↓
SMT / INDUCEMENT_TRAP
    ↓
NOT A TRADABLE OF
```

This exclusion preserves the source-defined distinction between liquidity delivery toward inducement and post-inducement executable order flow.

### Decisional Order Flow

A `DECISIONAL_OF` is the canonical Order Flow associated with the structural continuation that produces `VALID_BOS`: it is the relevant last opposing move/corrective leg before the reversal displacement that causes the canonical BOS.

```text
LAST OPPOSING OF
      ↓
REVERSAL DISPLACEMENT
      ↓
STRUCTURAL SWING BREAK
      ↓
VALID_BOS
```

The Decisional Order Flow is selected from the already eligible/unmitigated OF lineage. It must not be manufactured merely because a candle appears strong.

### Extreme Order Flow

An `EXTREME_OF` is the **furthest unmitigated eligible Order Flow at the origin of the active dealing range**.

If the current origin OF becomes mitigated, the Extreme OF reference shifts to the next furthest unmitigated eligible OF in the same dealing-range lineage.

```text
ORIGIN OF
   ├─ UNMITIGATED → EXTREME_OF
   └─ MITIGATED
          ↓
NEXT FURTHEST ELIGIBLE UNMITIGATED OF
```

An Extreme OF is not automatically valid merely because it is geometrically furthest; it must remain an eligible, unmitigated OF in the active lifecycle.

### OF / SMT non-equivalences

```text
OF_CANDIDATE ≠ VALID_OB
OF_CONFIRMED ≠ IDM
OF_CONFIRMED ≠ LIQUIDITY
OF_CONFIRMED ≠ VALID_BOS
SMT ≠ OF_CONFIRMED
PRE-IDM OF ≠ TRADABLE_POI
OF TOUCH ≠ OF_MITIGATED
```
## 37.6 Engineering Liquidity Identification and Lifecycle

Engineering Liquidity (`ENG_LQD`) is a canonical **core-liquidity reference**, distinct from IDM and distinct from POI.

### Source-defined origin

Engineering Liquidity is the liquidity resting beyond the relevant extreme of the **most recently formed valid pullback immediately preceding the active Extreme POI**.

```text
VALID PULLBACK
      ↓
EXTREME OF / EXTREME OB
      ↓
LIQUIDITY BEYOND THE PULLBACK EXTREME
      ↓
ENG_LQD_REFERENCE
```

For bullish structure:

```text
VALID_PULLBACK_LOW_BEFORE_EXTREME_POI
        ↓
liquidity below that low
        ↓
ENG_LQD_REFERENCE (SELL-SIDE)
```

For bearish structure:

```text
VALID_PULLBACK_HIGH_BEFORE_EXTREME_POI
        ↓
liquidity above that high
        ↓
ENG_LQD_REFERENCE (BUY-SIDE)
```

The reference pullback must be canonical and valid. An invalid pullback, arbitrary local pivot, SMT, or visually convenient extreme cannot create Engineering Liquidity.

If no valid pullback immediately preceding the active Extreme POI exists, no Engineering Liquidity reference is created.

### Extreme POI dependency

The active Extreme POI may be an `EXTREME_OF` or an `EXTREME_OB` according to the canonical POI/OB lifecycle. Engineering Liquidity is therefore resolved **after** the active Extreme POI identity is established.

When the active Extreme POI identity changes, the Engineering Liquidity reference must be recomputed from the corresponding valid-pullback-before-Extreme-POI relation. Historical references remain historical and are not silently rewritten.

### Core-liquidity lifecycle

```text
ENG_LQD_REFERENCE
        ↓
ENG_LQD_CONFIRMED
        ↓
ENG_LQD_SWEEP (optional)
```

A sweep of Engineering Liquidity is a liquidity/execution event. It does not by itself create IDM, BOS, CHoCH, a structural swing, or a Trading Range rollover. Reversal remains a separate execution/structural decision.

Engineering Liquidity and IDM can exist as distinct role objects even when their physical price levels coincide. Provenance must not be collapsed merely because the numeric level is equal.

### Engineering Liquidity non-equivalences

```text
ENG_LQD ≠ IDM
ENG_LQD ≠ POI
ENG_LQD ≠ VALID_BOS
ENG_LQD ≠ CHoCH
ENG_LQD_SWEEP ≠ AUTOMATIC_REVERSAL
ENG_LQD_SWEEP ≠ EXTREME_POI_MITIGATION
NO_VALID_PULLBACK_BEFORE_EXTREME_POI → NO ENG_LQD
```
## 38. Order Block validation


A candle/zone may be treated as a Valid Order Block only when the canonical three-pillar validation is satisfied.

```text
PILLAR 1
Origin of impulsive displacement that causes structural VALID_BOS
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

### Valid Order Flow Lifecycle

```text
PULLBACK_CANDIDATE
        ↓
VALID_PULLBACK
        ↓
IDM_TAKEN
        ↓
OF_ELIGIBLE
        ↓
ENGULF_CHECK_PASSED
        ↓
OF_CONFIRMED
```

Valid OF (`OF_CONFIRMED`) is a canonical POI class distinct from OB. OF and OB must not be conflated into a single generic zone type merely for implementation convenience.

### 38.1 Decisional / Extreme Order Block Selection Update

The current source update supersedes the earlier shortcut that treated the first valid Order Block formed immediately after inducement as the Decisional Order Block.

#### Decisional Order Block

A `DECISIONAL_OB` is the valid Order Block that **causes the canonical structural break / VALID_BOS**. It is selected from the impulse-side Order Block lineage associated with the canonical Decisional Order Flow and the displacement that actually produces the BOS.

```text
VALID ORDER BLOCK CANDIDATE
        ↓
CAUSAL DISPLACEMENT
        ↓
STRUCTURAL SWING BREAK
        ↓
VALID_BOS
        ↓
DECISIONAL_OB = OB THAT CAUSED THE BOS
```

The Decisional OB is therefore **not defined by temporal proximity to inducement alone**. The earlier rule "first valid OB after inducement" is superseded and must not be implemented as a canonical shortcut.

Once canonicalized, the Decisional OB identity remains tied to the causal BOS event. A later mitigation or failure of another Order Flow does not retroactively change the Decisional OB identity.

#### Extreme Order Block

An `EXTREME_OB` is selected from the furthest canonical Order Block at the origin-side extreme of the active dealing-range impulse, subject to its own OB validity and mitigation state.

#### Independent OB validity

Order Block validity is determined by its own canonical validation pillars. It is not automatically invalidated merely because the parent/containing Order Flow is unmitigated or because another Order Flow has failed.

```text
OB_PILLARS_VALID → OB_VALID
OF_STATE_CHANGE ↛ AUTOMATIC OB INVALIDATION
OF_UNMITIGATED ↛ OB_INVALID
OF_FAILURE ↛ OB_INVALID
```

The source update explicitly permits use of a valid Decisional OB even while the associated Order Flow remains unmitigated. This does not remove the Rule-of-Two constraint or create additional active POIs.

#### OF / OB selection priority

The source describes Order Flow as the primary selection context and Order Block as the secondary refinement/selection context, but this is **not** a validity dependency.

```text
OF_PRIMARY_CONTEXT ≠ OB_INVALID_WHEN_OF_EXISTS
OB_VALIDITY = INDEPENDENT
RULE_OF_TWO → selects active tradable POIs
```
### OB mitigation

Mitigation changes execution eligibility; it does not rewrite historical structural meaning. A mitigated OF does not automatically invalidate a separately valid Origin OB. A failed Decisional POI does not authorize arbitrary zone substitution; the canonical Extreme POI must be used when its own validity conditions are satisfied.

### OB refinement — Wick-Only and Inside-Bar bases

Refinement narrows the execution geometry of an already qualified Order Block. Refinement does **not** replace or relax the canonical three-pillar OB validation.

#### Long-wick / Pinbar base — Wick-Only OB

Where the qualified base candle contains an extended wick that performs the preceding liquidity sweep, the refined Order Block is limited to the sweeping wick region between the swept extreme and the candle body boundary.

Bullish / Demand:

```text
OB_bottom = Low_base
OB_top    = max(Open_base, Close_base)
```

Bearish / Supply:

```text
OB_top    = High_base
OB_bottom = min(Open_base, Close_base)
```

This refinement does not create a sweep, IDM, BOS, CHoCH, or any other structural event.

#### Inside-Bar base

If the base candle is a strict inside bar, the **Mother Bar** performs the liquidity sweep. The inside bar does not independently sweep liquidity or create a structural extreme. The canonical refined geometry is:

Bullish / Demand:

```text
OB_bottom = Low_(t-1)   # Mother Bar Low
OB_top    = Low_t       # Inside Bar Low
```

Bearish / Supply:

```text
OB_top    = High_(t-1)  # Mother Bar High
OB_bottom = High_t      # Inside Bar High
```

No alternative geometry such as an unspecified “sweeping wick range” is permitted. The inside-bar refinement is an execution-coordinate refinement only.

## 38.5. POI Failure and Rejection Block semantics

### POI Interaction vs. Failure

The skill distinguishes distinct levels of POI interaction:

```text
POI TOUCH
POI INTERACTION
POI MITIGATION
POI FAILURE
POI INVALIDATION
```

- A physical wick **touch** alone must not be declared a POI failure.
- Physical **penetration** alone must not automatically be declared a POI failure.
- **Execution failure** and **structural failure** must remain separate.
- **POI failure** must not create BOS or CHoCH.
- A failed POI must not authorize arbitrary replacement zones.
- Fallback must follow the canonical POI hierarchy.

Where the source material requires an HTF→LTF structural response before declaring failure, that dependency must be explicitly satisfied; failure cannot be reduced to a simple zone-close test.

### Rejection Block Identification

A Rejection Block is the rejection wick of the candle that takes the liquidity of the previous candle's relevant high/low. The preceding liquidity take may occur by wick OR body.

- **Bearish context:** The candle takes the previous bullish candle high. The rejection wick is the relevant upper wick region. That rejection region is the bearish Rejection Block.
- **Bullish context:** The candle takes the previous bearish candle low. The rejection wick is the relevant lower wick region. That rejection region is the bullish Rejection Block.

A Rejection Block may be physically contained within an Order Block, but this is NOT guaranteed. It is independently identifiable. Do not require an FVG for Rejection Block identification (the FVG requirement belongs to OB validation). Identifying a Rejection Block does not create a new structural event and does not redefine IDM, BOS, CHoCH, swing, or Trading Range.

### Extreme OB → Rejection Block Transition

A Rejection Block is a PD-array/execution-location concept associated with the extreme/origin area of the dealing range. It becomes relevant as the next PD-array only after the applicable Extreme Order Block fails, according to the source-defined sequence.

```text
ACTIVE EXTREME OB
      ↓
EXTREME OB FAILURE
      ↓
REJECTION BLOCK BECOMES NEXT PD ARRAY
      ↓
mitigation / valid execution context
```

The Rejection Block must not be treated as an arbitrary third active POI. It remains subject to the existing Rule-of-Two POI architecture and execution eligibility rules. Do not create a generic "fallback to any rejection wick" rule. Do not convert this transition into a universal structural-failure rule; it is strictly an execution/PD-array transition. The applicable Rejection Block must already satisfy the canonical identification conditions.

### Negative Rules

The following non-equivalences are strictly enforced:

```text
REJECTION_BLOCK ≠ ORDER_BLOCK
REJECTION_BLOCK ≠ FVG
REJECTION_BLOCK ≠ IDM
REJECTION_BLOCK ≠ BOS
REJECTION_BLOCK ≠ CHoCH
REJECTION_BLOCK ≠ AUTOMATIC_ENTRY
POI_TOUCH ≠ POI_FAILURE
POI_MITIGATION ≠ POI_FAILURE
POI_FAILURE ≠ STRUCTURAL_FAILURE
FAILED_POI ≠ ARBITRARY_ZONE_SUBSTITUTION
```

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

The IDM Sweep module requires a canonically active IDM and its qualifying liquidity interaction (`IDM_TAKEN = TRUE`). IDM sweep remains a liquidity/execution event and is not itself BOS or CHoCH.

### Module 2 — Decisional POI Mitigation

The Decisional POI must be an OF_CONFIRMED or Valid OB, must satisfy the directional premium/discount gate, and must meet the independent execution conditions of the module. POI mitigation does not create structural validity.

### Module 3 — Engineering Liquidity Sweep

#### Engineering Liquidity Lifecycle

```text
EXPANSION_ACTIVE
        ↓
ENG_LQD_CANDIDATE
        ↓
WICK_BOUNDARY_INTACT
        ↓
ENG_LQD_CONFIRMED
        ↓
ENG_LQD_SWEEP (optional)
```

Engineering liquidity (`ENG_LQD_CONFIRMED`) is an execution-layer liquidity event. It must not be promoted to structural liquidity, IDM, BOS, or CHoCH merely because price sweeps the engineered level.

### 40.1 Entry Authorization and Price-Reference Contract

The methodology determines when an entry is **authorized** and which canonical market reference produced that authorization. It does not by itself mandate a broker/exchange order type.

```text
CANONICAL ENTRY CONTEXT
        ↓
ENTRY AUTHORIZED
        ↓
ENTRY_REFERENCE_PRICE
        ↓
PLATFORM EXECUTION POLICY
        ↓
MARKET / LIMIT / STOP ORDER
```

The broker order type is therefore an implementation/infrastructure choice unless a separate canonical trading-plan rule explicitly fixes it.

#### Module 1 — IDM Sweep entry

```text
ACTIVE IDM
   ↓
IDM_TAKEN = TRUE
   ↓
REVERSAL / DIRECTIONAL CONFIRMATION
   ↓
ENTRY_AUTHORIZED
```

A liquidity sweep alone is not an entry. When direct candle confirmation is used, the `ENTRY_REFERENCE_PRICE` is the close of the completed confirmation candle.

#### Module 2 — Decisional POI Mitigation entry

```text
VALID DECISIONAL POI
   ↓
POI MITIGATION
   ↓
REVERSAL / DIRECTIONAL CONFIRMATION
   ↓
ENTRY_AUTHORIZED
```

The Decisional POI may be `OF_CONFIRMED` or `VALID_OB`. Mitigation without an independent execution confirmation does not create an entry. With direct candle confirmation, the `ENTRY_REFERENCE_PRICE` is the completed confirmation-candle close.

#### Module 3 — Engineering Liquidity Sweep entry

```text
ENG_LQD_CONFIRMED
   ↓
ENG_LQD_SWEEP
   ↓
DIRECTIONAL CONFIRMATION
   ↓
ENTRY_AUTHORIZED
```

An Engineering Liquidity sweep does not itself create an entry. With direct candle confirmation, the `ENTRY_REFERENCE_PRICE` is the completed confirmation-candle close.

#### Module 4 — Extreme POI Mitigation entry

```text
VALID EXTREME POI
   ↓
POI MITIGATION
   ↓
REVERSAL / DIRECTIONAL CONFIRMATION
   ↓
ENTRY_AUTHORIZED
```

Extreme POI mitigation does not itself create an entry. The Extreme POI must remain canonical under the Rule-of-Two and its own OF/OB validity conditions. With direct candle confirmation, the `ENTRY_REFERENCE_PRICE` is the completed confirmation-candle close.

#### Unfilled orders, cancellation, and re-entry

These are platform order-lifecycle policies rather than independent SMC semantic definitions. A pending order must never be assumed to be canonical merely because an entry context exists. Until the dedicated trading-plan/order-lifecycle contract is canonicalized, the implementation must preserve the distinction between:

```text
ENTRY_AUTHORIZED ≠ ORDER_SUBMITTED
ORDER_SUBMITTED ≠ ORDER_FILLED
ORDER_FILLED ≠ POSITION_OPEN
```

A later structural or execution event may invalidate a pending order according to the dedicated order-lifecycle policy; such invalidation must not rewrite the historical entry authorization event.
### Module 4 — Extreme POI Mitigation

The Extreme POI module is the canonical fallback execution mechanism when the Decisional POI is not the applicable execution location. The Extreme POI must independently satisfy OF_CONFIRMED or Valid OB validity; fallback execution does not relax POI validation.

## 40.5. Candlestick Reversal Triggers

Candlestick reversal patterns are **execution confirmation/trigger objects only**. They are downstream consumers of structural and execution eligibility and have zero structural authority.

Layer 6 may consume Layer 1 OUTSIDE_BAR state and its geometric metrics. It owns the semantic evaluation of OUTSIDE_BAR_REVERSAL; that state is never auto-derived merely because an Outside Bar exists.

~~~text
OUTSIDE_BAR
    ↓
LAYER 6 REVERSAL PREDICATE
    ↓
OUTSIDE_BAR_REVERSAL (only if Layer 6 conditions pass)
~~~

### Architectural gate

A candlestick reversal pattern may authorize a direct entry only when an existing canonical execution route is already eligible:

```text
DIRECT CANDLE ENTRY ELIGIBILITY
        ↓
    (POI MITIGATION)
          OR
    (CORE LIQUIDITY SWEEP)
        ↓
CANDLE REVERSAL CONFIRMATION
        ↓
CANDLE CLOSE
        ↓
DIRECT ENTRY
```

Eligible key areas are:

- mitigation of a qualified **Decisional POI or Extreme POI (OF_CONFIRMED / Valid OB)**;
- a direct sweep of active **IDM** (`IDM_TAKEN = TRUE`);
- a direct sweep of **Engineering Liquidity (ENG_LQD_CONFIRMED)**.

A standalone/unbacked FVG is not an eligible direct-entry location.

The candlestick pattern does not create the POI, IDM, ENG_LQD_CONFIRMED, or any structural condition. It only confirms an already eligible execution context.

### Close-only execution

Entry is permitted only on the **close of the completed pattern candle**.

```text
LIVE / UNCLOSED WICK → NO ENTRY
COMPLETED CANDLE CLOSE → ENTRY EVALUATION
```

A live wick cannot trigger a direct candle-pattern entry.

### Canonical pattern catalog

#### 1. Long Wick Rejection / Pinbar

Morphology:

- small body;
- minimal opposite shadow;
- extended rejection wick penetrating the eligible POI or sweeping the eligible liquidity reference.

Bullish direct-entry polarity:

```text
Close > Open
```

The bullish entry is evaluated at candle close. If `Close <= Open`, the bullish pattern does not qualify; a subsequent bullish close is required.

Bearish direct-entry polarity:

```text
Close < Open
```

If `Close >= Open`, the bearish pattern does not qualify; a subsequent bearish close is required.

#### 2. Multiple Wick Rejection

Two or more consecutive candles must penetrate the same eligible POI zone or swept-liquidity context and close without crossing the applicable execution-failure boundary.

For a bullish context:

```text
Low_(t-1) <= POI_top
Low_t     <= POI_top
Close_(t-1) >= POI_bottom
Close_t     >= POI_bottom
Close_t > Open_t
```

For a bearish context:

```text
High_(t-1) >= POI_bottom
High_t     >= POI_bottom
Close_(t-1) <= POI_top
Close_t     <= POI_top
Close_t < Open_t
```

No external tick-level tolerance is introduced. The previously validated POI geometry is authoritative.

The trigger is the close of the second or later rejecting candle that satisfies the directional close condition.

#### 3. Engulfing / Outside-Bar Reversal

Bullish:

```text
Low_t < Low_(t-1)
AND
Close_t > max(Open_(t-1), Close_(t-1))
AND
Close_t > Open_t
```

Bearish:

```text
High_t > High_(t-1)
AND
Close_t < min(Open_(t-1), Close_(t-1))
AND
Close_t < Open_t
```

The wick sweep is mandatory. A body-only engulfing without the required sweep is not the canonical direct-entry trigger.

#### 4. Momentum Candle

A Momentum Candle is an immediate, above-average full-bodied expansion candle with minimal opposing wick emerging from an eligible execution reference.

Because the authoritative source provides no discrete numerical definition for “above-average” or “minimal wick”, this remains a **Qualitative Filter / SOURCE-PENDING** classification and is not an independent binary trigger.

#### 5. Morning Star / Evening Star

Three-candle sequence:

```text
t-2 = incoming trend candle
t-1 = small-bodied / indecision base in the eligible area
t   = reversal confirmation candle
```

The `t-1` small-body/indecision morphology is a **Qualitative Filter**, not a binary gate. At binary level, Candle `t-1` must physically interact with the eligible POI or swept-liquidity reference.

Bullish Morning Star:

```text
Close_(t-2) < Open_(t-2)
Close_t > Open_t
Close_t > (Open_(t-2) + Close_(t-2)) / 2
```

Bearish Evening Star:

```text
Close_(t-2) > Open_(t-2)
Close_t < Open_t
Close_t < (Open_(t-2) + Close_(t-2)) / 2
```

Entry is evaluated at the close of Candle `t`.

#### 6. Shrinking Candles

Progressive reduction in candle body size while approaching the eligible POI or liquidity reference is an **Approach Filter only**.

```text
SHRINKING CANDLES ≠ ENTRY TRIGGER
```

It cannot independently authorize a direct entry.

### Pattern non-equivalences

```text
CANDLE_PATTERN       ≠ POI
CANDLE_PATTERN       ≠ IDM
CANDLE_PATTERN       ≠ ENG_LQD_CONFIRMED
CANDLE_PATTERN       ≠ CONFIRMED_STRUCTURAL_SWING
CANDLE_PATTERN       ≠ VALID_BOS
CANDLE_PATTERN       ≠ CHoCH_CONFIRMED
CANDLE_PATTERN       ≠ TRADING_RANGE
CANDLE_PATTERN       ≠ STRUCTURAL_INVALIDATION
CANDLE_PATTERN       ≠ POI_CREATION
```

The candlestick trigger therefore follows this dependency:

```text
CANONICAL STRUCTURAL / EXECUTION ELIGIBILITY
        ↓
ELIGIBLE POI OR CORE LIQUIDITY CONTEXT
        ↓
CANDLE PATTERN OBSERVATION
        ↓
COMPLETED CANDLE CLOSE
        ↓
EXECUTION TRIGGER
```

It never runs in the reverse direction.

## 41. Execution, structural validation, and risk

Execution priority and structural validation are separate domains.

```text
EXECUTION PRIORITY ≠ STRUCTURAL VALIDATION
ORDER FLOW FAILED ≠ VALID_BOS
ORDER FLOW FAILED ≠ CHoCH_CONFIRMED
POI FAILURE ≠ STRUCTURAL FAILURE
```

A failed execution condition must not be converted into a structural event. Likewise, a structurally valid event does not automatically authorize execution.

### Order Flow failure / Extreme fallback

Do not fail over from OF_CONFIRMED to Extreme OB solely because price wicked into or through the OF. The exact failure condition must be independently satisfied by the canonical execution module. A wick touch alone is insufficient to invent an execution-state transition.

### Risk and RR

A canonical executable setup must satisfy a minimum risk/reward of **1:2**. The primary target is the confirmed external range extreme where the applicable entry module requires it. Risk management must consume structural state; it must not redefine structure.
