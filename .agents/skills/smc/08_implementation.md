# IMPLEMENTATION

**Role:** How the mapper represents and transitions canonical methodology objects.

**Authority boundary:** Implementation follows methodology. Implementation convenience must never redefine methodology.

## Canonical lifecycle source

The validated structural lifecycle rules are defined in `03_structural_semantic_authority.md`, with detailed BOS mechanics in `04_BOS_mechanics.md` and detailed CHoCH mechanics in `05_CHOCH_mechanics.md`.

The mapper must implement those rules without inventing alternative BOS or CHoCH semantics.

## 45. Implementation mapping

The structural engine must conceptually separate:

```text
CANDLE-LEVEL PULLBACK
VERIFIED PULLBACK EXTREME
PULLBACK-DERIVED LIQUIDITY REFERENCE
ACTIVE LIQUIDITY POINTER
ACTIVE/MINOR IDM
MAJOR IDM
IDM SWEEP
CONFIRMED_STRUCTURAL_SWING
PROTECTED STRUCTURAL EXTREME
PHYSICAL EXTERNAL BREAK
VALID_BOS
CHoCH_CONFIRMED
TRADING RANGE
```

Functions equivalent to `finish_pullback()` must not promote a candle-level pullback directly to IDM.

Functions equivalent to `detect_idm_sweep()` must operate on the active qualified IDM and emit the canonical `IDM_TAKEN` result when the IDM reference is physically taken. The structural lifecycle then consumes `IDM_TAKEN` to establish `CONFIRMED_STRUCTURAL_SWING`. The sweep detector must not itself declare `VALID_BOS` or `CHoCH_CONFIRMED`; those classifications remain subject to their complete downstream gates.

Functions equivalent to `detect_bos()` must require:

1. eligible CONFIRMED_STRUCTURAL_SWING;
2. `MAJOR_RETRACEMENT_QUALIFIED == TRUE`, supplied by Layer 3;
3. physical external break (`STRUCTURAL_SWING_BREAK` via wick or body);
4. `IDM_TAKEN == True`;
5. continuation-BOS reference is not an IDM reference.

A Major IDM wick penetration must terminate as `MAJOR_IDM_SWEEP`, not BOS.

Functions equivalent to `detect_choch()` must use the governing opposing Protected Structural Extreme / Trading Range boundary and must enforce the complete CHoCH prerequisites. A body close beyond the boundary is not, by itself, sufficient to declare `CHoCH_CONFIRMED`.

### 45.0 Order Flow / SMT implementation mapping

The implementation must preserve the canonical distinction between Order Flow observations, eligible Order Flow, SMT exclusions, and POI selection.

```text
OF_CANDIDATE
    ↓
ELIGIBILITY
    ├─ PRE-IDM → SMT / INDUCEMENT_TRAP
    ├─ MITIGATED → INVALID_FOR_EXECUTION
    └─ ELIGIBLE + UNMITIGATED → OF_CONFIRMED
```

Required representation:

- `OF_CANDIDATE` stores the whole relevant opposing corrective move, including multiple internal legs while its protected endpoint remains intact;
- `OF_CONFIRMED` requires canonical eligibility conditions and unmitigated status;
- `SMT / INDUCEMENT_TRAP` is a non-tradable contextual exclusion and must not be emitted as a Valid OF;
- touching an OF does not mark it mitigated unless a canonical Valid Pullback confirms the mitigation;
- `DECISIONAL_OF` is selected from the valid OF lineage associated with the displacement that causes `VALID_BOS`;
- `EXTREME_OF` is the furthest unmitigated eligible OF at the origin of the active dealing range;
- when the current Extreme OF is mitigated, selection shifts to the next furthest eligible unmitigated OF;
- a Decisional or Extreme OF remains a POI candidate only after the POI ontology and Rule-of-Two constraints are satisfied.

Forbidden shortcuts:

```text
PRE-IDM FORMATION → OF_CONFIRMED
OF TOUCH → OF_MITIGATED
ARBITRARY LOCAL MOVE → OF_CONFIRMED
OF_CONFIRMED → VALID_BOS
OF_CONFIRMED → IDM
SMT → POI
```

### 45.0.1 Engineering Liquidity implementation mapping

The implementation resolves Engineering Liquidity only for a canonical `EXTREME_OF` or `EXTREME_OB`.

```text
ACTIVE EXTREME_OF / EXTREME_OB
    ↓
MOST RECENT VALID PULLBACK IMMEDIATELY BEFORE IT
    ↓
PULLBACK EXTREME
    ↓
ENG_LQD_REFERENCE
```

Required representation:
- bullish: liquidity below the valid pullback low immediately preceding the active Extreme POI;
- bearish: liquidity above the valid pullback high immediately preceding the active Extreme POI;
- no valid pullback before the active Extreme POI -> no Engineering Liquidity reference;
- invalid pullbacks, SMTs, arbitrary pivots, and generic equal highs/lows cannot manufacture ENG_LQD;
- when the active Extreme POI changes between canonical `EXTREME_OF` and `EXTREME_OB` provenance, the Engineering Liquidity reference is recomputed for the new provenance;
- historical ENG_LQD references remain immutable observations;
- ENG_LQD sweep is distinct from IDM sweep, Extreme POI mitigation, BOS, and CHoCH;
- if IDM and ENG_LQD occupy the same numeric price, preserve the distinct semantic roles rather than collapsing provenance.

Deterministic lifecycle:

```text
ENG_LQD_REFERENCE
        ↓
ENG_LQD_CONFIRMED
        ↓
ENG_LQD_SWEEP (optional)
```
### 45.1 Entity lifecycle schemas

Liquidity levels and protected structural boundaries are different ontology classes. Their lifecycle semantics must not be collapsed into one undifferentiated state enum.

#### LiquidityState

Applies to liquidity entities such as Minor IDM, Major IDM, and Engineering Liquidity:

- `ACTIVE` — live liquidity level that has not yet been swept.
- `SWEPT` — liquidity level has been taken out by the applicable wick/body event.
- `SUPERSEDED` — a newer valid pullback or later structural lifecycle has replaced the level's active role.
- `HISTORICAL` — archived liquidity belonging to a closed structural regime or Dealing Range.

#### StructuralBoundaryState

Applies to structural boundaries such as Protected Structural Extremes and Governing Range Boundaries:

- `ACTIVE` — currently governing and protected structural level.
- `BROKEN` — structurally broken boundary after the applicable CHoCH conditions have been satisfied.
- `SUPERSEDED` — replaced by a newly established governing range boundary.
- `HISTORICAL` — boundary belonging to a closed historical structural regime.

**Ontology invariant:**

```text
BROKEN
→ StructuralBoundary only

BROKEN
≠ LiquidityState

LiquidityEntity
→ ACTIVE / SWEPT / SUPERSEDED / HISTORICAL

StructuralBoundary
→ ACTIVE / BROKEN / SUPERSEDED / HISTORICAL
```

If an implementation uses a technically shared field, the semantic restriction remains mandatory: `BROKEN` is valid only for `StructuralBoundary` entities. A liquidity entity must never be classified as `BROKEN`, and a structural boundary break must not be reduced to the liquidity-only state `SWEPT`.

## 45.1 Risk and scoring implementation mapping

The mapper's concrete risk calculation is implementation-owned. The risk methodology document defines the semantic risk boundaries; this section records how the current engine represents those boundaries so documentation does not compete with executable behavior.

### Weighted final score

```
Structure = 25%
Setup     = 30%
Location  = 20%
Liquidity = 15%
Risk      = 10%
```

Quality tiers:

```
HIGH   >= 70
MEDIUM >= 55
LOW    >= 40
WATCH  < 40
```

### Current mapper risk-quality calculation

The current implementation starts risk quality at 80 when a confirmed dealing range exists.

Retracement-depth handling:

```
retracement > 100.0%
    → depth_penalty = 80
    → setup invalidated

78.6% < retracement <= 90.0%
    → depth_penalty = 25

90.0% < retracement <= 100.0%
    → depth_penalty = 45
```

Protected-level proximity handling:

```
invalidation distance < 10% of range
    → prox_penalty = 25

invalidation distance < 3% of range
    → prox_penalty = 45
```

The implementation bounds these two penalty families with:

```
risk_penalty = max(depth_penalty, prox_penalty)
risk_quality = 80 - risk_penalty
```

Additional directional risk adjustment:

```
bullish + PREMIUM → -15
bearish + DISCOUNT → -15
no BOS            → -10
```

Risk quality is bounded to 0–100.

These are implementation facts, not additional structural SMC rules. They must not be used to manufacture IDM, swing confirmation, BOS, CHoCH, or any other structural state.

### Liquidity-quality implementation values

```
Major IDM = 80
```

These values are scoring outputs applied to already-established methodology state.

### Boundary

```
07_risk.md
    → semantic risk policy

08_implementation.md
    → executable scoring representation

the mapper implementation
    → actual calculation
```

Therefore, a future change to the executable risk formula must first be classified as an implementation change and must not silently become a new methodology rule.

## 45.2. Intrabar Sequence Evidence

INTRABAR_SEQUENCE_EVIDENCE is an implementation/data-model state. It does not redefine the Layer 1 methodology model.

Allowed states:

~~~text
OBSERVED
    → sequence verified from sub-timeframe, tick, replay, or equivalent historical evidence.

METHODOLOGY_ASSUMED
    → sequence represented using the canonical True SMC OLHC/OHLC methodology model
      when implementation explicitly needs a modeled path.

UNAVAILABLE
    → aggregate OHLC does not expose sufficient historical evidence to establish
      the intrabar order.
~~~

For an Outside Bar derived from a single aggregate timeframe, the default evidence state is:

~~~text
OUTSIDE_BAR = TRUE
INTRABAR_SEQUENCE_EVIDENCE = UNAVAILABLE
~~~

The implementation must never infer LOW_FIRST or HIGH_FIRST from the completed candle's open/close color alone.

Mandatory invariants:

~~~text
METHODOLOGY_ASSUMED ≠ OBSERVED
UNAVAILABLE ≠ OBSERVED
UNAVAILABLE MUST NOT BE AUTO-PROMOTED TO OBSERVED
~~~

If stronger sequence evidence later becomes available, the implementation may replace UNAVAILABLE with OBSERVED only on the basis of that evidence. The methodology model may not be used as retrospective proof.

## 46. Structural state machine

The mapper is a state machine. Each event must be evaluated against current structural state, not only against the current candle.

### BOS path

```text
OBSERVATION
 ↓
CANDLE-LEVEL VALID PULLBACK
 ↓
VERIFIED PULLBACK EXTREME
 ↓
PULLBACK-DERIVED LIQUIDITY REFERENCE
 ↓
ACTIVE IDM
 ↓
IDM_TAKEN
 ↓
CONFIRMED_STRUCTURAL_SWING
 ↓
LAYER 3 RETRACEMENT QUALIFICATION
 ├─ NOT QUALIFIED AT ATTEMPTED BREAK → REFERENCE_SHIFT / SWING_REPLACEMENT
 └─ QUALIFIED
      ↓
   PHYSICAL_EXTERNAL_BREAK
      ↓
   STRUCTURAL_SWING_BREAK
      ↓
   COMPLETE BOS GATE
      ↓
   VALID_BOS
      ↓
   TRADING_RANGE_ROLLOVER
```

## 6.X — Canonical BOS Execution Model

The BOS execution model strictly consumes a previously established qualification state.
Execution never recalculates BOS eligibility and never bypasses the qualification gate.

### Canonical BOS Lifecycle (Execution Phase)

```text
PHYSICAL_EXTERNAL_BREAK (wick or body)
        ↓
STRUCTURAL_SWING_BREAK
        ↓
CONSUME STORED QUALIFICATION
        ↓
COMPLETE BOS GATE
        ↓
VALID_BOS
   or
IMPULSE_EXTENSION
```

### Execution Rules

**PHYSICAL_EXTERNAL_BREAK**

A wick or body breach of the eligible continuation external boundary.
This event does not determine BOS classification.

**STRUCTURAL_SWING_BREAK**

The wick/body breach satisfies the structural break condition.
It is not `VALID_BOS` by itself.

**CONSUME STORED QUALIFICATION**

`is_bos_qualified` is the stored result of the qualification phase.

Execution does not recalculate:

* opposing-candle count
* retracement depth
* IDM prerequisites

The physical break supplies `STRUCTURAL_SWING_BREAK`; the stored qualification is then consumed by the canonical BOS gate.

**COMPLETE BOS GATE**

The implementation consumes the canonical Layer 3 qualification result rather than evaluating retracement thresholds locally:

```text
VALID_BOS ⇔
    IDM_TAKEN
    AND MAJOR_RETRACEMENT_QUALIFIED
    AND STRUCTURAL_SWING_BREAK
```

Layer 3 owns whether qualification was established through the standard 50% path or the conditional 38.2%–<50% immediate-HTF valid-pullback path. If any prerequisite is missing, the break cannot produce `VALID_BOS`.

**VALID_BOS**

If the BOS gate is satisfied, the dealing range rolls over and the Protected Structural Extreme locks.

**IMPULSE_EXTENSION**

If qualification is not satisfied, the break is classified as `IMPULSE_EXTENSION`.

No rollover occurs, and no Protected Structural Extreme is locked.

---

## 6.X — Major IDM Interaction (Opposing Boundary)

Major IDM is never part of continuation BOS provenance.

When no newly qualified post-BOS Major IDM exists, the prior protected external boundary remains the active Major IDM reference.

### Major IDM interaction rules

```text
MAJOR_IDM + wick breach
→ MAJOR_IDM_SWEEP

MAJOR_IDM + body close
→ CHoCH_ELIGIBLE
→ CHoCH_CONFIRMED only if all CHoCH prerequisites pass
```

`MAJOR_IDM_SWEEP` never produces `VALID_BOS`, `CHoCH_CONFIRMED`, Trading Range rollover, or Protected Structural Extreme lock.

When a new post-BOS Major IDM is independently qualified, it supersedes the previous active Major IDM from that point forward. Historical IDM provenance is immutable.

## 6.X — Deterministic Invariants

The following invariants must be preserved:

```text
PHYSICAL_EXTERNAL_BREAK ≠ STRUCTURAL_SWING_BREAK ≠ VALID_BOS

MAJOR_IDM_SWEEP ≠ VALID_BOS ≠ CHoCH_CONFIRMED

Later candles may advance state but may not rewrite previously classified events.
```

---

### CHoCH path

```text
CURRENT RANGE
 ↓
GOVERNING OPPOSING PROTECTED EXTREME
 ↓
OPPOSING STRUCTURAL BOUNDARY VIOLATION (Body Close)
        ↓
CHoCH_ELIGIBLE
        ↓
CHoCH_CONFIRMED
        ↓
OLD TREND TERMINATED + INITIAL ACTIVE IMPULSE INITIALIZED
```

The engine must not skip prerequisites because a later price movement appears visually obvious.

### LTF-CHoCH Context Route

The implementation must support the source-defined LTF CHoCH route without creating a sixth lifecycle state.

Activation:
```text
ACTIVE HTF DIRECTIONAL NARRATIVE
        AND
HTF POI INTERACTION
        OR
HTF CORE-LIQUIDITY TAKEOUT
        ↓
LTF_CHoCH_CONTEXT_ACTIVE
```

While active, the governing opposing reference for the LTF route is the most recently formed **valid LTF pullback**, represented by its verified pullback extreme / active inducement reference. Invalid pullbacks, arbitrary local pivots, SMT levels, and non-validated extremes must not be substituted.

```text
MOST_RECENT_VALID_LTF_PULLBACK
        ↓
VERIFIED_PULLBACK_EXTREME
        ↓
LTF_ACTIVE_INDUCEMENT_REFERENCE
        ↓
LTF CHoCH REFERENCE
```

The source-aligned execution representation uses a completed LTF candle close beyond that reference:

```text
BULLISH HTF CONTEXT
Close_LTF < LTF_Inducement_Low
        ↓
LTF_CHoCH_ELIGIBLE

BEARISH HTF CONTEXT
Close_LTF > LTF_Inducement_High
        ↓
LTF_CHoCH_ELIGIBLE
```

Wick-only penetration of this LTF reference does not confirm the special LTF route.

```text
LTF_CHoCH_ELIGIBLE
        ↓
ALL APPLICABLE CHoCH PREREQUISITES
        ├─ FAIL → REMAIN / CONTEXT CONTINUES
        └─ PASS → CHoCH_CONFIRMED
```

`LTF_CHoCH_CONTEXT_ACTIVE` is a process/context condition, not a lifecycle state enum. It expires when `CHoCH_CONFIRMED` occurs or when its qualifying HTF interaction context is no longer the active execution context.

Non-equivalences:
```text
HTF POI INTERACTION ≠ CHoCH
HTF CORE-LIQUIDITY TAKEOUT ≠ CHoCH
LTF VALID PULLBACK ≠ CHoCH
LTF INDUCEMENT SWEEP ≠ CHoCH
LTF_CHoCH_CONTEXT_ACTIVE ≠ NEW STATE ENUM
LTF CHoCH REFERENCE ≠ MAJOR_IDM
```
### Post-CHoCH dual lineage

`CHoCH_CONFIRMED` initializes the new regime without inventing a new lifecycle enum. The new trend remains in `CONFIRMATION_LOCKED` while candidate detection is allowed and confirmation is gated.

```text
CHoCH_CONFIRMED
    │
    ├── STRUCTURAL REGIME FLIP
    │      ├── previous range archived
    │      ├── new trend fixed
    │      └── INITIAL_ACTIVE_IMPULSE begins
    │
    ├── INTERNAL LINEAGE
    │      └── FIRST_POST_CHOCH_SVP
    │             ↓
    │         VERIFIED_PULLBACK_EXTREME
    │             ↓
    │         FIRST_POST_CHOCH_MINOR_IDM
    │
    └── EXTERNAL PROXY LINEAGE
           └── GOVERNING OPPOSING RANGE BOUNDARY
                  ↓
              MAJOR_IDM
```

The two lineages are not interchangeable:

```text
FIRST_POST_CHOCH_SVP ≠ FIRST_POST_CHOCH_MINOR_IDM
Major IDM provenance ≠ Minor IDM provenance
```

A qualifying sweep of the applicable IDM lineage unlocks the Confirmation Gate. IDM takeout establishes `IDM_TAKEN = TRUE`, which is the prerequisite for the canonical `CONFIRMED_STRUCTURAL_SWING` confirmation path; it does NOT by itself create a new Dealing Range, trend flip, `CHoCH_CONFIRMED`, `VALID_BOS`, or Trading Range rollover. `CONFIRMATION GATE UNLOCKED` is a process condition, not a new lifecycle state enum.

```text
CONFIRMATION_LOCKED
        │
        ├─ FIRST_POST_CHOCH_MINOR_IDM sweep
        │
        └─ MAJOR_IDM sweep
                 ↓
       CONFIRMATION GATE UNLOCKED
                 ↓
      CONFIRMED_STRUCTURAL_SWING QUALIFICATION
                 ↓
             FIRST BOS
                 ↓
        NEW CONFIRMED DEALING RANGE
                 ↓
             POST-BOS SVP
                 ↓
          MAJOR_IDM
                 ↓
       NEW MAJOR IDM supersedes prior reference
```

Major IDM boundary classification remains provenance-sensitive:

```text
MAJOR_IDM + WICK BREACH
→ MAJOR_IDM_SWEEP
→ trend unchanged
→ no BOS
→ no CHoCH
→ no Trading Range rollover
→ Gate may unlock, subject to remaining swing prerequisites

MAJOR_IDM + BODY CLOSE
→ CHoCH_ELIGIBLE
→ NOT AUTOMATIC CHoCH_CONFIRMED
→ full CHoCH prerequisite gate required
```

A later candle may advance the lifecycle but may not retroactively rewrite the earlier classification.

## 47. Error conditions that must be prevented

1. Random local low becomes bullish IDM.
2. Random local high becomes bearish IDM.
3. Inside bar becomes IDM.
4. Three candles automatically become IDM.
5. 38.2% automatically becomes IDM.
6. Candle-level pullback becomes IDM without structural qualification.
7. Old active IDM remains after a newer valid pullback forms.
8. Multiple active minor IDM targets remain simultaneously.
9. IDM sweep becomes BOS without the canonical swing and break prerequisites.
10. IDM sweep becomes CHoCH.
11. A physical external break becomes BOS without retracement sufficiency and canonical break classification.
12. Local pivot break becomes CHoCH.
13. Deep retracement invalidates confirmed swing without governing range violation.
14. New minor high/low creates a new Trading Range.
15. CHoCH resets the new trend to an empty state.
16. CHoCH creates a Protected Structural Extreme automatically.
17. CHoCH-causing leg is ignored as the initial active impulse.
18. Major IDM remains one canonical semantic class; its provenance may be pullback-derived or prior-protected-boundary-derived.
19. Major IDM wick penetration becomes BOS or CHoCH.
20. `MAJOR_IDM_SWEEP` must be handled as an IDM-takeout lifecycle event; it may confirm the relevant swing reference but does not itself create VALID_BOS, range rollover, or protected-extreme lock.
21. A body close beyond the opposing boundary is treated as CHoCH without all CHoCH prerequisites.
22. A later candle retroactively rewrites an earlier `MAJOR_IDM_SWEEP` or BOS classification.
23. A `VALID_BOS` is delayed pending a later body close when the wick-BOS path is already valid.
24. A MAJOR_IDM wick causes Trading Range rollover.
25. Genesis manufactures IDM or protected structure.
26. A retracement below the canonical qualification floor must never produce VALID_BOS.
27. Scoring creates structural validity.
28. Historical liquidity remains active merely because it exists in history.
29. One outside bar activates both directional branches.
30. Inside-bar breaks are treated as independent pullbacks.
31. Structural engine directly deletes or mutates POI registry state on range rollover.
32. POIs from a closed Trading Range remain tradable after `TRADING_RANGE_ROLLED_OVER`.
33. `BROKEN` is applied to a liquidity entity.
34. A liquidity `SWEPT` event is misclassified as a structural `BROKEN` event.
35. `CONFIRMATION GATE UNLOCKED` is introduced as a new lifecycle state enum.
36. `MAJOR_IDM + BODY CLOSE` is treated as automatic `CHoCH_CONFIRMED`.
37. Confirmed Swing is treated as automatic `VALID_BOS` without `MAJOR_RETRACEMENT_QUALIFIED`.
38. A continuation break is classified as `VALID_BOS` without the complete Layer 3 qualification result (must remain non-BOS / `IMPULSE_EXTENSION` as applicable).
39. Any heuristic/safe mode is used to substitute for the canonical Layer 3 qualification result.
40. A retracement with **>= `MIN_RETRACEMENT_CANDLE_COUNT` opposing candles** may enter qualification evaluation. The **`MIN_RETRACEMENT_CANDLE_COUNT`-candle case** may qualify only through the documented rare displacement/extreme-taking exception; **`NORMAL_RETRACEMENT_CANDLE_COUNT` or more** remains the normal-case count, and candle count alone never establishes qualification.

## 48. Testing requirements

Regression tests must cover:

### Pullback
- bullish candle-level Valid Pullback;
- bearish candle-level Valid Pullback;
- equal-high reference transfer;
- equal-low reference transfer;
- strict inside-bar exclusion;
- outside-bar LOW→HIGH sequencing;
- outside-bar HIGH→LOW sequencing.

### Structural qualification
- standard `NORMAL_RETRACEMENT_CANDLE_COUNT`-opposing-closing-candle qualification on the `STANDARD_EQUILIBRIUM_THRESHOLD` path;
- a `MIN_RETRACEMENT_CANDLE_COUNT` retracement is permitted only through the documented rare reduced-candle displacement case: unusually large retracement candle(s) collectively taking >= `MIN_OUTLIER_EXTREMES_TAKEN` preceding bodies/extremes and reaching the required retracement depth;
- reduced-candle qualification is an **exactly 2-candle** exception only; a 1-candle retracement is not a positive reduced-candle qualification path;
- `HTF_CONDITIONAL_THRESHOLD`–<`STANDARD_EQUILIBRIUM_THRESHOLD` qualifies only through a valid single pullback event on the applicable immediate Higher Timeframe;
- HTF inside-bar or invalid-pullback representation does not qualify;
- below `HTF_CONDITIONAL_THRESHOLD` does not qualify;
- a continuation break without stored `MAJOR_RETRACEMENT_QUALIFIED` remains non-BOS / `IMPULSE_EXTENSION` as applicable.

### IDM
- the verified extreme and pullback-derived liquidity reference from a Candle-Level Valid Pullback are consumed by Layer 3 for IDM classification;
- structural retracement qualification is a later continuation-BOS gate after `CONFIRMED_STRUCTURAL_SWING`, not an initial IDM prerequisite;
- newest valid pullback replaces old active IDM;
- only one active minor IDM;
- Major IDM provenance: post-BOS pullback-derived or prior-protected-boundary-derived;
- correct Major IDM lifecycle after BOS;
- CHoCH does not automatically apply the BOS Major IDM lifecycle;
- historical IDM is not an active competing target;
- IDM wick takeout;
- IDM body takeout;
- Major IDM provenance remains traceable; there is no separate fallback Major IDM ontology or provenance class.

### Entity lifecycle ontology
- liquidity entity can transition `ACTIVE → SWEPT`;
- newer valid pullback can supersede active liquidity;
- historical liquidity is not active merely because it remains in history;
- structural boundary can transition to `BROKEN` only through the applicable structural break lifecycle;
- liquidity entity can never receive `BROKEN` semantics;
- `BROKEN` and `SWEPT` remain semantically distinct even if an implementation shares a technical field.

### Swing / Protected Extreme
- qualified IDM sweep confirms the relevant `CONFIRMED_STRUCTURAL_SWING`;
- retracement qualification is evaluated separately as the prerequisite for a subsequent continuation BOS;
- dynamic absolute retracement extreme tracking;
- `STANDARD_EQUILIBRIUM_THRESHOLD` standard qualification with the normal `NORMAL_RETRACEMENT_CANDLE_COUNT`-candle rule;
- reduced-candle qualification only through the documented rare displacement case taking >= `MIN_OUTLIER_EXTREMES_TAKEN` preceding bodies/extremes; the reduced-candle branch is explicitly the **`MIN_RETRACEMENT_CANDLE_COUNT`-candle case**, while **`NORMAL_RETRACEMENT_CANDLE_COUNT` or more** remains the normal-case count; candle count alone never establishes qualification;
- 38.2%–<50% qualification only through the applicable immediate-HTF valid-pullback path;
- below 38.2% does not qualify;
- shallow qualification failure revokes the candidate and shifts the active pullback/IDM reference;
- Protected Structural Extreme locks only at valid BOS;
- MAJOR_IDM wick does not lock Protected Structural Extreme.

### BOS
- BOS requires eligible Confirmed Continuation Swing;
- BOS requires retracement sufficiency;
- physical external break is distinct from BOS;
- external Body-Close BOS;
- external Wick-Break BOS;
- wick-BOS does not require a later body close;
- close exactly at the broken level remains valid Wick-BOS;
- MAJOR_IDM wick is `MAJOR_IDM_SWEEP`;
- MAJOR_IDM wick is not BOS;
- MAJOR_IDM wick is not CHoCH;
- MAJOR_IDM wick does not roll the Trading Range;
- MAJOR_IDM body close is only CHoCH-eligible pending prerequisites;
- later candles cannot retroactively rewrite an earlier classification.

### BOS downstream lifecycle
- `VALID_BOS` closes the previous Trading Range;
- `VALID_BOS` locks `E_retrace` as Protected Structural Extreme when sufficiency is satisfied;
- `VALID_BOS` emits `TRADING_RANGE_ROLLED_OVER`;
- previous-range POIs transition to `EXPIRED_HISTORICAL` through the POI lifecycle subsystem;
- expired historical POIs are non-tradable;
- new range retains the prior protected external boundary as Major IDM until a new Major IDM is independently qualified;
- first post-break SVP does not directly equal Major IDM; the full eligibility chain is required.

### CHoCH
- correct governing opposing Protected Structural Extreme is used;
- Minor Structure takeout does not create CHoCH;
- IDM sweep does not create CHoCH;
- continuation swing break follows BOS path, not CHoCH;
- physical opposing-boundary violation only opens CHoCH eligibility;
- body close beyond boundary is not sufficient without full CHoCH prerequisites;
- Major IDM boundary body close is `CHoCH_ELIGIBLE`, not automatic CHoCH confirmation;
- CHoCH creates new trend lifecycle;
- CHoCH-causing leg becomes initial active impulse;
- CHoCH does not create a Protected Structural Extreme automatically;
- first post-CHoCH SVP and first post-CHoCH Minor IDM remain distinct lineage objects;
- MAJOR_IDM lineage remains distinct from internal Minor IDM lineage;
- confirmation gate unlock is a process condition, not a new state enum;
- MAJOR_IDM exception remains distinct from normal CHoCH qualification.

### Trading Range
- bullish/bearish BOS establishes the new range;
- internal fluctuations do not shift the primary boundary;
- minor high/low does not create a new range;
- deep retracement does not automatically reset range;
- MAJOR_IDM wick does not roll the range.

### Entry Authorization / Execution Order Mapping

The implementation must separate canonical entry authorization from broker/exchange order submission and fill state.

```text
ENTRY_CONTEXT_VALID
        ↓
ENTRY_AUTHORIZED
        ↓
ENTRY_REFERENCE_PRICE
        ↓
EXECUTION POLICY
        ↓
ORDER_SUBMITTED
        ↓
ORDER_FILLED
        ↓
POSITION_OPEN
```

Required mappings:
- IDM Sweep: active IDM + IDM_TAKEN + reversal/directional confirmation -> ENTRY_AUTHORIZED; direct confirmation price reference = completed confirmation-candle close;
- Decisional POI Mitigation: active IDM + `IDM_TAKEN` + valid Decisional POI + mitigation + independent reversal/directional confirmation -> ENTRY_AUTHORIZED; direct confirmation price reference = completed confirmation-candle close;
- Engineering Liquidity Sweep: confirmed ENG_LQD + sweep + directional confirmation -> ENTRY_AUTHORIZED; direct confirmation price reference = completed confirmation-candle close;
- Extreme POI Mitigation: valid Extreme POI + mitigation + reversal/directional confirmation -> ENTRY_AUTHORIZED; direct confirmation price reference = completed confirmation-candle close;
- broker order type is not a True SMC semantic fact unless a separate canonical trading-plan rule specifies it;
- an entry authorization must never be treated as an order fill or open position;
- pending-order expiry, cancellation, replacement, and re-entry belong to the order-lifecycle policy and must not rewrite historical entry authorization.

Forbidden shortcuts:
```text
ENTRY_AUTHORIZED → POSITION_OPEN
ENTRY_CONTEXT_VALID → ORDER_FILLED
POI_TOUCH → ENTRY_AUTHORIZED
IDM_SWEEP → ENTRY_AUTHORIZED (without confirmation)
ENG_LQD_SWEEP → ENTRY_AUTHORIZED (without confirmation)
POI_MITIGATION → ENTRY_AUTHORIZED (without confirmation)
```

### Target Resolution implementation mapping

Target resolution must produce canonical target candidates before any downstream TP handling.

```text
EXECUTION CONTEXT
   ↓
TARGET DISCOVERY
   ↓
VALID TARGET CANDIDATES
   ↓
CONFIGURABLE TARGET PLAN
   ↓
TARGET LEG ASSIGNMENT
   ↓
NOTIFICATION-ONLY MONITOR (CURRENT PHASE)
```

Required mappings:
- direct same-timeframe pro-trend -> current confirmed external extreme / external liquidity;
- LTF execution -> explicit policy selecting `HTF_EXTERNAL_TARGET` or `LTF_STRUCTURAL_TARGET`; no implicit default;
- countertrend -> setup-specific next canonical destination, such as the next valid POI, IDM, Engineering Liquidity, or external liquidity, according to the active setup contract;
- the source does not define one universal priority among all simultaneously valid target candidates;
- therefore the analyzer must not manufacture a single universal winner target merely to satisfy an RR calculation;
- a downstream configurable Target Plan may assign multiple valid target candidates to separate trade legs;
- target-leg allocation is configurable execution/trading policy and is not a new SMC structural rule;
- fixed-R targets, where permitted by the applicable policy, remain non-structural policy targets and must not be mislabeled as canonical liquidity/structure targets;
- RR calculation consumes an already resolved target; it must never create a target;
- absent canonical target -> no automatic TP submission.

#### Target Plan representation

The implementation should preserve target provenance and leg assignment separately:

```text
TARGET_CANDIDATE
    ├─ target_id
    ├─ target_type
    ├─ price
    └─ provenance
          ↓
TARGET_PLAN
    ├─ leg_id
    ├─ target_id
    └─ allocation
```

A three-leg configuration is supported as a configurable example:

```text
LEG_1 → T1
LEG_2 → T2
LEG_3 → T3
```

The number of legs and their allocation are configuration, not methodology constants. The implementation must not assume 3 legs, equal allocation, or any fixed percentage.

A leg is executable/observable only when its assigned target resolves to a valid target candidate or to an explicitly permitted non-structural policy target.

#### Target lifecycle and notification mapping

The current platform phase is notification-only:

```text
TARGET_ACTIVE
    ↓
PRICE_REACHES_TARGET
    ↓
TARGET_REACHED
    ↓
TARGET_NOTIFICATION_SENT
```

`TARGET_REACHED` must not imply:

```text
TARGET_REACHED ≠ POSITION_CLOSED
TARGET_REACHED ≠ STOP_MOVED
TARGET_REACHED ≠ LEG_CLOSED
TARGET_REACHED ≠ BROKER_FILL
```

A future position-management component may consume `TARGET_REACHED` and apply a configured action such as partial close, break-even, previous-target profit lock, or trailing protection. Those actions are downstream execution/trading-policy behavior and are not currently implemented by the monitor.

`BREAK_EVEN` is a stop-management action, not a fallback target.

Notification payload should preserve at minimum:
- symbol/instrument;
- direction;
- target identifier;
- target type/provenance;
- target price;
- event timestamp.

The monitor must not emit `POSITION_CLOSED` unless an independent execution/account component verifies that outcome.

### Decisional / Extreme Order Block selection implementation mapping

Required implementation behavior:
- `DECISIONAL_OB` is the valid Order Block that actually causes the canonical `VALID_BOS` event; it is not selected solely because it is the first valid OB after inducement;
- the earlier `first valid OB after inducement` shortcut is superseded;
- `EXTREME_OB` is selected as the furthest unmitigated valid Order Block within the active `EXTREME_OF` lineage; it is not selected by a global search across all origin-side Order Blocks;
- OB validity is evaluated from the canonical OB validation pillars independently of parent Order Flow mitigation/failure state;
- a valid Decisional OB may remain executable even while its associated Order Flow is unmitigated, subject to Rule-of-Two and all execution gates;
- later OF mitigation/failure must not retroactively rewrite the causal Decisional OB identity.

### Stop Placement implementation mapping

Stop placement must be derived from the canonical entry-module anchor before position sizing or broker submission.

```text
ENTRY MODULE
   ↓
SL_ANCHOR
   ↓
CONFIGURED P
   ↓
EXACT STOP PRICE
```

Required anchors:
- IDM Sweep -> sweeping-candle extreme;
- Decisional POI Mitigation -> confirming/reversal-pattern extreme;
- Engineering Liquidity Sweep -> validated sweep/confirmation extreme;
- Extreme POI Mitigation -> confirming/reversal-pattern extreme.

Required invariants:
- `P` is explicit execution configuration, not an invented methodology constant;
- missing `P` prevents automatic broker order submission;
- stop placement must not create or validate structural state;
- stop touch remains an execution event;
- stop movement after entry belongs to a separate trade-management policy and must not rewrite the historical entry/SL anchor.

### POI / Entry
- POI ontology accepts Valid OF and Valid OB;
- Rejection Block is a separately typed PD-array/execution concept; source examples may use POI as a broad execution-location term, but RB is not an OF/OB-equivalent POI class or an automatic Rule-of-Two slot;
- Rule of Two limits canonical tradable POIs to Decisional POI and Extreme POI (Extreme OF / Extreme OB);
- Origin OB is a latent reserve POI (mitigation transfer target when Extreme POI is mitigated), never a 3rd active POI;
- when an applicable Rule-of-Two dealing-range execution context exists, the active canonical tradable POI set has cardinality 1..2; if no valid canonical POI exists, execution fails closed with no executable POI / `NO_EVIDENCE`; no synthetic POI is created;
- Decisional buy POI is in discount, and Decisional sell POI is in premium as a hard execution eligibility gate;
- Decisional sell POI is in premium;
- Origin OB remains independently valid after parent OF mitigation when its own pillars remain valid;
- all three OB validation pillars are required;
- standalone FVG never becomes POI;
- standalone FVG never creates entry;
- FVG break never creates BOS/CHoCH;
- IDM never becomes POI;
- OF failure does not automatically promote Extreme POI;
- all four entry modules remain execution-layer mechanisms;
- executable setups are gated by `Projected_RR_to_Primary_Target >= Configured_Minimum_RR` when the configured trading policy requires an RR gate;
- closed-range POIs become non-tradable after lifecycle expiration.

### Genesis
- no fabricated IDM;
- no fabricated protected swing;
- no fabricated BOS.

## 49. State-Transition Coverage & Determinism

The structural state machine is formally separated into three deterministic layers. A candle must not directly manufacture a state transition.

### 49.1 Three-layer deterministic pipeline

```text
┌───────────────────────────────────────────────────────────────┐
│ 1. EVENT DETECTION                                            │
│                                                               │
│ Physical OHLC/level relations select exactly ONE of the       │
│ six disjoint event classes.                                 │
└───────────────────────────────┬───────────────────────────────┘
                                ↓
┌───────────────────────────────────────────────────────────────┐
│ 2. EVENT CLASSIFICATION                                       │
│                                                               │
│ Retracement sufficiency, level provenance, liquidity, and    │
│ structural prerequisite gates determine the structural        │
│ outcome of the detected event.                                │
└───────────────────────────────┬───────────────────────────────┘
                                ↓
┌───────────────────────────────────────────────────────────────┐
│ 3. STATE TRANSITION                                           │
│                                                               │
│ Current State + Structural Outcome determine exactly ONE     │
│ next state.                                                   │
└───────────────────────────────────────────────────────────────┘
```

`IMPULSE_EXTENSION`, `VALID_BOS`, `CHoCH_CONFIRMED`, `MAJOR_IDM_SWEEP`, and `NO_CHoCH_BREAK` are **classification outcomes**, not additional event classes.

### 49.2 Six disjoint event classes

Exactly one of the six event classes is emitted by Event Detection:

```text
1. NO_EVENT / INTERNAL_PB
2. MINOR_IDM_EVENT
3. EXT_CONT_BREAK
4. EXT_OPP_BREAK
5. MAJOR_IDM_EVENT
6. NEW_SVP_QUALIFIED
```

Detection precedence is:

```text
EXT_OPP_BREAK
>
EXT_CONT_BREAK
 >
MAJOR_IDM_EVENT
>
MINOR_IDM_EVENT
>
NEW_SVP_QUALIFIED
>
NO_EVENT / INTERNAL_PB
```

The precedence applies only to **event detection**. It does not directly declare a structural outcome or next state.

Where multiple physical relationships appear possible, the event is resolved using the canonical structural identity and active lifecycle of the referenced level. Geometry alone must not manufacture a competing event class.

### 49.3 Event classification rules

#### `EXT_CONT_BREAK`

```text
EXT_CONT_BREAK DETECTED
        ↓
CONSUME STORED LAYER 3 QUALIFICATION
        ├─ MAJOR_RETRACEMENT_QUALIFIED = FALSE
        │      ↓
        │  OUTCOME = IMPULSE_EXTENSION (Dealing range remains open, no new protected extreme)
        │
        └─ MAJOR_RETRACEMENT_QUALIFIED = TRUE
               ↓
           OUTCOME = VALID_BOS (Dealing range rolls over, Protected Structural Extreme locks)
```

`IMPULSE_EXTENSION` therefore remains a classification outcome of `EXT_CONT_BREAK`; it is not an eighth event class.

#### `EXT_OPP_BREAK`

```text
EXT_OPP_BREAK DETECTED
        ↓
GEOMETRIC CLASSIFICATION
        ├─ BODY CLOSE
        │      ↓
        │  CHoCH_ELIGIBLE
        │      ↓
        │  ALL APPLICABLE CHoCH PREREQUISITES
        │      ├─ PASS → CHoCH_CONFIRMED
        │      └─ FAIL → REJECTION / REMAIN
        │
        └─ WICK BREACH
               ↓
        LEVEL PROVENANCE
          ├─ MAJOR IDM PROVENANCE
          │    ↓
          │  MAJOR_IDM_SWEEP / NOT CHoCH
          │
          └─ ELIGIBLE OPPOSING EXTERNAL BOUNDARY
               ↓
        CHoCH_ELIGIBLE
               ↓
        ALL APPLICABLE CHoCH PREREQUISITES
          ├─ PASS → CHoCH_CONFIRMED
          └─ FAIL → REJECTION / REMAIN
```

A Major IDM is not a positive prerequisite for the opposing-wick CHoCH path. The exclusion is provenance-based: if the tested external level itself carries Major IDM provenance, the wick is not CHoCH; otherwise an eligible opposing external-boundary wick may enter the CHoCH prerequisite gate.

A body close beyond the opposing boundary is never `CHoCH_CONFIRMED` by geometry alone. It first creates CHoCH eligibility and must pass the complete canonical prerequisite gate.

### 49.4 State-transition coverage

The five lifecycle states are:

```text
BOOTSTRAP
CONFIRMATION_LOCKED
CONFIRMED_RANGE
POST_BOS
POST_CHOCH
```

`CONFIRMATION GATE UNLOCKED` is not a sixth state. It is a process condition within the applicable lifecycle state.

The six detected event classes are:

```text
NO_EVENT / INTERNAL_PB
MINOR_IDM_EVENT
EXT_CONT_BREAK
EXT_OPP_BREAK
MAJOR_IDM_EVENT
NEW_SVP_QUALIFIED
```

The transition matrix is exhaustive and deterministic:

| Current State | NO_EVENT / INTERNAL_PB | MINOR_IDM_EVENT | EXT_CONT_BREAK | EXT_OPP_BREAK | MAJOR_IDM_EVENT | NEW_SVP_QUALIFIED |
|---|---|---|---|---|---|---|
| **BOOTSTRAP** | REMAIN; update provisional extremes/internal sequence | REMAIN; no confirmed range | DISQUALIFIED; no confirmed swing, therefore no BOS | DISQUALIFIED; no protected boundary, therefore no CHoCH | NOT_APPLICABLE; no active Major IDM | SVP → Verified Extreme → IDM → Sweep → Gate → **CONFIRMED_RANGE** |
| **CONFIRMATION_LOCKED** | REMAIN; track active expansion/retrace state | Gate UNLOCKED; remaining prerequisites required before **CONFIRMED_RANGE** | DISQUALIFIED; BOS prohibited while confirmation is locked | CHoCH pipeline; qualifying break + all prerequisites → **POST_CHOCH**, otherwise REMAIN | REMAIN; Major IDM wick → `MAJOR_IDM_SWEEP`, Gate UNLOCKED, no automatic swing | FIRST_POST_CHOCH_SVP → Verified Extreme → FIRST_POST_CHOCH_MINOR_IDM; remain confirmation-locked until applicable sweep/gate prerequisites complete |
| **CONFIRMED_RANGE** | REMAIN; dynamic `E_retrace` tracking | REMAIN; Minor IDM sweep unlocks gate, trend/range remain active | `IMPULSE_EXTENSION` → REMAIN; `VALID_BOS` → **POST_BOS** | `CHoCH_CONFIRMED` → **POST_CHOCH**; `MAJOR_IDM_SWEEP` → REMAIN; `NO_CHoCH_BREAK` → REMAIN | REMAIN; Major IDM wick → `MAJOR_IDM_SWEEP`, no CHoCH | REMAIN; new SVP supersedes the active pullback reference only when canonical IDM lifecycle requires it |
| **POST_BOS** | REMAIN; new expansion tracked, closed-range POIs expire through POI lifecycle | REMAIN; a Minor IDM does not replace the prior Major IDM | DISQUALIFIED; another BOS is not interpreted until the new swing lifecycle is established | CHoCH classification pipeline; qualifying opposing break + all prerequisites → **POST_CHOCH**, otherwise REMAIN | REMAIN; Major IDM wick → `MAJOR_IDM_SWEEP`, Gate UNLOCKED | SVP → Verified Extreme → IDM qualification; if Major IDM qualifies, it supersedes the prior Major IDM → **CONFIRMED_RANGE** |
| **POST_CHOCH** | remain in `CONFIRMATION_LOCKED` | first post-CHoCH Minor IDM pipeline; no automatic state promotion | BOS prohibited while confirmation remains locked | body close → `CHoCH_ELIGIBLE` pending prerequisites; Major IDM wick → `MAJOR_IDM_SWEEP`; Major IDM body close enters CHoCH pipeline | Major IDM wick → `MAJOR_IDM_SWEEP`, Gate UNLOCKED, trend unchanged | FIRST_POST_CHOCH_SVP → Verified Extreme → FIRST_POST_CHOCH_MINOR_IDM; remain `CONFIRMATION_LOCKED` until applicable sweep/gate prerequisites complete |

The `POST_CHOCH` row is intentionally not a blanket `CONFIRMATION_LOCKED` transition for every event. The state remains `CONFIRMATION_LOCKED`, while the event-specific lineage and gate logic determine the next process step.

### 49.5 Determinism invariants

The following are mandatory:

```text
EVENT DETECTION
→ exactly ONE of 6 event classes

EVENT CLASSIFICATION
→ exactly ONE structural outcome for the detected event

STATE TRANSITION
→ exactly ONE next state for Current State + Outcome
```

Additional invariants:

```text
NO_NEW_MAJOR_IDM → PRIOR_PROTECTED_BOUNDARY_REMAINS_MAJOR_IDM
MINOR_IDM_SWEEP ≠ AUTOMATIC CONFIRMED_SWING
MAJOR_IDM_SWEEP ≠ AUTOMATIC CONFIRMED_SWING
NEW_SVP ≠ AUTOMATIC MAJOR_IDM
EXT_CONT_BREAK ≠ AUTOMATIC VALID_BOS
EXT_OPP_BREAK ≠ AUTOMATIC CHoCH_CONFIRMED
MAJOR_IDM + WICK ≠ CHoCH
MAJOR_IDM + BODY CLOSE ≠ AUTOMATIC CHoCH_CONFIRMED
CONFIRMATION GATE UNLOCKED ≠ NEW STATE ENUM
BROKEN ≠ SWEPT
IMPULSE_EXTENSION ≠ EVENT CLASS
PHYSICAL_EXTERNAL_BREAK ≠ STRUCTURAL_SWING_BREAK ≠ VALID_BOS
MAJOR_IDM_SWEEP ≠ VALID_BOS ≠ CHoCH_CONFIRMED
```

The state machine must preserve provenance, prerequisite gates, and anti-retroactive event classification. A later candle may advance state but may not rewrite a previously classified event.

### 49.6 Context-Dependent Wick Disambiguation

**Wick breach is context-dependent and must not be globally classified as a sweep.** The parser MUST evaluate the structural role of the breached level before classifying a wick.

Required conceptual behavior:

```text
IF breached level == CONTINUATION_EXTERNAL_BOUNDARY
  AND level is a confirmed structural swing
  AND physical wick penetration occurs:

  STRUCTURAL_SWING_BREAK = TRUE

  IF IDM_TAKEN
  AND MAJOR_RETRACEMENT_QUALIFIED
  THEN:
      classify as VALID_BOS
      lock Protected Structural Extreme
      perform Trading Range Rollover
  ELSE:
      classify according to the canonical insufficient-gate / IMPULSE_EXTENSION logic

  (Do NOT require body close to establish STRUCTURAL_SWING_BREAK in this continuation case)

IF breached level == OPPOSING_PROTECTED_BOUNDARY
  AND the tested external level does NOT carry Major IDM provenance
THEN:
  wick breach → CHoCH_ELIGIBLE

IF breached level == MAJOR_IDM
  OR the tested external level otherwise carries Major IDM provenance
THEN:
  wick breach → MAJOR_IDM_SWEEP / NOT CHoCH
  trend remains unchanged

IF opposing protected boundary receives the required body close
THEN:
  CHoCH_ELIGIBLE
  (Only confirms CHoCH after all prerequisites pass)
```

### 49.7 Canonical Authority Hierarchy

For the canonical True SMC implementation, the implementation-level structural specification governs where it provides a more specific rule than earlier generic pedagogical formulations.

Therefore:
* earlier body-close-only BOS pedagogy is NOT a universal implementation rule;
* implementation-level Wick-BOS defines the valid STRUCTURAL_SWING_BREAK mechanism, while the complete VALID_BOS event still requires all canonical macro-BOS gates;
* continuation external wick-BOS is canonical for establishing the break;
* wick interpretation is structural-context dependent.

## Implementation boundary

The following must remain separate state objects or semantically equivalent state representations:

```text
ACTIVE PULLBACK POINTER
≠ MINOR IDM STATE
≠ MAJOR IDM STATE
≠ CONFIRMED SWING
≠ PROTECTED STRUCTURAL EXTREME
≠ TRADING RANGE
≠ HISTORICAL STRUCTURE
≠ POI LIFECYCLE STATE
```

The structural engine may emit lifecycle events such as `TRADING_RANGE_ROLLED_OVER`, but the POI lifecycle subsystem owns POI state mutation.

Configuration may alter parameters but cannot manufacture structural truth. Scoring evaluates validated structural state and cannot create or validate structure.
