# IMPLEMENTATION

**Role:** How the mapper represents and transitions canonical methodology objects.

**Authority boundary:** Implementation follows methodology. Implementation convenience must never redefine methodology.

## Canonical structural type boundary

The implementation domain must preserve the semantic layers explicitly. Generic objects such as Swing, Break, or Structure are insufficient when a value participates in a canonical structural rule.

Use layer-specific representations equivalent to:
- MicroBreach / CandleExtremeBreach
- MinorStructuralSwing
- MinorIDM
- ConfirmedStructuralSwing
- ProtectedExternalBoundary / ProtectedStructuralExtreme
- MajorIDM
- StructuralSwingBreak
- ExternalBOS / VALID_BOS

These are representations of existing canonical semantics, not new ontology classes. Existing canonical event names remain authoritative.

The implementation must never infer a higher-layer object merely because a lower-layer geometric relation exists.

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

Functions equivalent to `detect_idm_sweep()` must operate on the active qualified IDM and emit the canonical `IDM_TAKEN` result when the IDM reference is physically taken. The structural lifecycle then consumes `IDM_TAKEN` to establish the swing-point candidate / provisional structural extreme; macro retracement qualification promotes that candidate to `CONFIRMED_STRUCTURAL_SWING`. The sweep detector must not itself declare `VALID_BOS` or `CHoCH_CONFIRMED`; those classifications remain subject to their complete downstream gates.

Functions equivalent to `detect_bos()` must require:

1. eligible CONFIRMED_STRUCTURAL_SWING;
2. `MAJOR_RETRACEMENT_QUALIFIED == TRUE`, supplied by Layer 3;
3. physical external break (`STRUCTURAL_SWING_BREAK` via wick or body);
4. `IDM_TAKEN == True`;
5. continuation-BOS reference is not an IDM reference.

A Major IDM wick penetration must terminate as `MAJOR_IDM_SWEEP`; that sweep is consumed as the IDM takeout (`IDM_TAKEN`) and therefore confirms the associated structural swing, but it is not BOS.

Functions equivalent to `detect_choch()` must use the governing opposing Protected Structural Extreme / Trading Range boundary and must enforce the complete CHoCH prerequisites. A body close beyond the boundary is not, by itself, sufficient to declare `CHoCH_CONFIRMED`.

### 45.0 Order Flow / SMT implementation mapping

The implementation must preserve the canonical distinction between Order Flow observations, eligible Order Flow, SMT exclusions, and POI selection.

```text
ORDER_FLOW_CANDIDATE
    ↓
ELIGIBILITY
    ├─ PRE-IDM → SMT / INDUCEMENT_TRAP
    ├─ MITIGATED → INVALID_FOR_EXECUTION
    └─ ELIGIBLE + UNMITIGATED → ELIGIBLE_ORDER_FLOW
```

Required representation:

- `ORDER_FLOW_CANDIDATE` stores the whole relevant opposing corrective move, including multiple internal legs while its protected endpoint remains intact;
- `ELIGIBLE_ORDER_FLOW` requires canonical eligibility conditions and unmitigated status;
- `SMT / INDUCEMENT_TRAP` is a non-tradable contextual exclusion and must not be emitted as a Eligible Order Flow;
- touching an OF does not mark it mitigated unless a canonical Valid Pullback confirms the mitigation;
- `DECISIONAL_ORDER_FLOW` is selected from the eligible Order Flow lineage associated with the displacement that causes `VALID_BOS`;
- `EXTREME_ORDER_FLOW` is the furthest unmitigated eligible OF at the origin of the active dealing range;
- when the current Extreme Order Flow is mitigated, selection shifts to the next furthest eligible unmitigated OF;
- a Decisional or Extreme Order Flow remains a POI candidate only after the POI ontology and Rule-of-Two constraints are satisfied.

Forbidden shortcuts:

```text
PRE-IDM FORMATION → ELIGIBLE_ORDER_FLOW
ORDER FLOW TOUCH → ORDER_FLOW_MITIGATED
ARBITRARY LOCAL MOVE → ELIGIBLE_ORDER_FLOW
ELIGIBLE_ORDER_FLOW → VALID_BOS
ELIGIBLE_ORDER_FLOW → IDM
SMT → POI
```

### 45.0.1 Engineering Liquidity implementation mapping

The implementation resolves Engineering Liquidity only for a canonical `EXTREME_ORDER_FLOW` or `EXTREME_ORDER_BLOCK`.

```text
ACTIVE EXTREME_ORDER_FLOW / EXTREME_ORDER_BLOCK
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
- when the active Extreme POI changes between canonical `EXTREME_ORDER_FLOW` and `EXTREME_ORDER_BLOCK` provenance, the Engineering Liquidity reference is recomputed for the new provenance;
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
### 45.1 — Entity lifecycle schemas

Liquidity levels and protected structural boundaries are different ontology classes. Their lifecycle semantics must not be collapsed into one undifferentiated state enum.

#### 45.1.1 — LiquidityState

Applies to liquidity entities such as Minor IDM, Major IDM, and Engineering Liquidity:

- `ACTIVE` — live liquidity level that has not yet been swept.
- `SWEPT` — liquidity level has been taken out by the applicable wick/body event.
- `SUPERSEDED` — a newer valid pullback or later structural lifecycle has replaced the level's active role.
- `HISTORICAL` — archived liquidity belonging to a closed structural regime or Dealing Range.

#### 45.1.2 — StructuralBoundaryState

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

## 45.2 — Intrabar Sequence Evidence

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

## 46.1 — Canonical BOS Execution Model

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

## 46.2 — Major IDM Interaction (Opposing Boundary)

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

## 46.3 — Deterministic Invariants

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
OPPOSING STRUCTURAL BOUNDARY VIOLATION (Wick OR Body)
        ↓
CHoCH CLASSIFICATION GATE
        ↓
CHoCH_ELIGIBLE
        ↓
CHoCH_CONFIRMED (only if all prerequisites pass)
        ↓
OLD TREND TERMINATED + INITIAL ACTIVE IMPULSE INITIALIZED
```

The engine must not skip prerequisites because a later price movement appears visually obvious.

#### Classification Gate Rules:
- **Body Close:** A candle close beyond the eligible opposing protected boundary enters the CHoCH gate and produces `CHoCH_ELIGIBLE`.
- **Wick Breach:** A wick penetration of the eligible opposing protected boundary produces `CHoCH_ELIGIBLE`, PROVIDED the tested level does not carry Major IDM provenance.
- **Major IDM Provenance Exception:** If the breached level carries Major IDM provenance, a wick breach produces `MAJOR_IDM_SWEEP` (trend unchanged, not CHoCH); only a body close beyond the Major IDM boundary is `CHoCH_ELIGIBLE`, pending all canonical CHoCH prerequisites.

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

This is the source-defined **LTF Structural Glitch** route. The normal LTF external boundary is temporarily replaced by the most recently formed valid LTF pullback / inducement reference.

The implementation must then resolve the break mode from the LTF IDM classification:

```text
LTF STRUCTURAL GLITCH
        ↓
MOST RECENT VALID LTF PULLBACK / IDM REFERENCE
        ↓
IDM TYPE
   ├─ MAJOR IDM
   │    ↓
   │  WICK BREACH MAY ENTER CHoCH GATE
   │
   └─ MINOR IDM ONLY
        ↓
     BODY CLOSE BEYOND ACTIVE LTF REFERENCE
        ↓
     CHoCH_ELIGIBLE
```

When the active LTF range contains only Minor IDM, its external protected boundary functions as the Major IDM. A wick penetration of that external Major IDM is classified as `MAJOR_IDM_SWEEP`; it does not become CHoCH merely because the Structural Glitch context is active.

A body close is therefore **not** a universal LTF requirement. It is mandatory only for the Minor-Inducement case defined above. A Major-Inducement LTF CHoCH can be confirmed through the applicable wick-break path, subject to the complete CHoCH prerequisites.

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
LTF STRUCTURAL GLITCH ≠ UNIVERSAL BODY-CLOSE RULE
LTF CHoCH CONFIRMATION MODE = IDM-TYPE DEPENDENT
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

A qualifying sweep of the applicable IDM lineage unlocks the Confirmation Gate. IDM takeout establishes `IDM_TAKEN = TRUE`, which creates the swing-point candidate / provisional structural extreme; macro retracement qualification is the promotion gate for the canonical `CONFIRMED_STRUCTURAL_SWING`; it does NOT by itself create a new Dealing Range, trend flip, `CHoCH_CONFIRMED`, `VALID_BOS`, or Trading Range rollover. `CONFIRMATION GATE UNLOCKED` is a process condition, not a new lifecycle state enum.

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
5. A 38.2% retracement qualification is not itself an IDM.
6. An unvalidated candle-level pullback becomes IDM without the canonical Layer-2 Valid Pullback qualification.
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
28. Historical liquidity remains active merely because it exists in history.
29. One outside bar activates both directional branches.
30. Inside bars remain governed by their mother-candle reference and are not treated as independent pullback references.
31. Structural engine directly deletes or mutates POI registry state on range rollover.
32. POIs from a closed Trading Range remain tradable after `TRADING_RANGE_ROLLED_OVER`.
33. `BROKEN` is applied to a liquidity entity.
34. A liquidity `SWEPT` event is misclassified as a structural `BROKEN` event.
35. `CONFIRMATION GATE UNLOCKED` is introduced as a new lifecycle state enum.
36. `MAJOR_IDM + BODY CLOSE` is treated as `CHoCH_ELIGIBLE` only; `CHoCH_CONFIRMED` requires all applicable CHoCH prerequisites.
37. Confirmed Swing is treated as automatic `VALID_BOS` without `MAJOR_RETRACEMENT_QUALIFIED`.
38. A continuation break is classified as `VALID_BOS` without the complete Layer 3 qualification result (must remain non-BOS / `IMPULSE_EXTENSION` as applicable).
39. Any heuristic/safe mode is used to substitute for the canonical Layer 3 qualification result.
40. A normal retracement with **>= 3 opposing closing candles** may enter the standard qualification path. A 2-candle retracement is permitted only through the documented reduced-candle displacement exception, while the one-candle displacement outlier is an explicit separate exception requiring **>= `MIN_OUTLIER_EXTREMES_TAKEN`** preceding bodies/extremes and all other canonical qualification conditions; candle count alone never establishes qualification.

## 48. Testing requirements

Regression tests must cover:

### Pullback
- bullish candle-level Valid Pullback;
- bearish candle-level Valid Pullback;
- equal-high reference transfer;
- equal-low reference transfer;
- strict inside-bar exclusion;
- explicit Layer-2 terminal invalidation for Outside Bar ordering that is unavailable;
- later independently observable candles cannot retroactively resolve an invalidated pullback candidate;
- outside-bar LOW→HIGH sequencing;
- outside-bar HIGH→LOW sequencing.

### Structural qualification
- standard `NORMAL_RETRACEMENT_CANDLE_COUNT`-opposing-closing-candle qualification on the `STANDARD_EQUILIBRIUM_THRESHOLD` path;
- a normal retracement requires >=3 opposing closing candles for the standard qualification path; a 2-candle retracement is eligible only through the documented reduced-candle displacement exception, and the one-candle displacement outlier bypasses the normal count gate only through its explicit rare displacement/extreme-taking exception and all other canonical gates;
- reduced-candle qualification is not limited to two candles: the source-defined one-candle displacement outlier is also permitted when it takes >= `MIN_OUTLIER_EXTREMES_TAKEN` preceding bodies/extremes and all other canonical gates pass;
- `HTF_CONDITIONAL_THRESHOLD`–<`STANDARD_EQUILIBRIUM_THRESHOLD` qualifies only through a valid single pullback event on the applicable immediate Higher Timeframe;
- HTF inside-bar or invalid-pullback representation does not qualify;
- below `HTF_CONDITIONAL_THRESHOLD` does not qualify;
- a continuation break without stored `MAJOR_RETRACEMENT_QUALIFIED` remains non-BOS / `IMPULSE_EXTENSION` as applicable.

### IDM
- Layer 2 establishes the Minor IDM from the verified extreme and pullback-derived liquidity reference of a Candle-Level Valid Pullback; Layer 3 consumes that Minor IDM for IDM_TAKEN and Major IDM governance;
- structural retracement qualification is a later continuation-BOS gate after `CONFIRMED_STRUCTURAL_SWING`, not an initial IDM prerequisite;
- newest valid pullback replaces the old active Minor IDM; Layer 3 consumes the resulting active Minor IDM for IDM_TAKEN and downstream Major IDM governance;
- only one active minor IDM;
- Major IDM provenance: post-BOS pullback-derived or prior-protected-boundary-derived;
- correct Major IDM lifecycle after BOS;
- CHoCH does not automatically apply the BOS Major IDM lifecycle;
- historical IDM is not an active competing target;
- IDM wick takeout;
- IDM body takeout;
- Major IDM provenance remains traceable; there is no separate Major IDM subtype or proxy ontology; when no new Major IDM qualifies, the prior protected external boundary remains the active Major IDM reference.

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
- reduced-candle qualification may use the documented rare displacement case, including the explicit one-candle outlier; the normal case remains >=3 opposing closing candles, while the 2-candle and one-candle branches are explicit reduced-candle exceptions requiring their applicable displacement/extreme-taking conditions and all other canonical gates;
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
- close exactly at the broken level does **not** constitute a physical break; actual penetration beyond the reference is required;
- MAJOR_IDM wick is `MAJOR_IDM_SWEEP`;
- MAJOR_IDM wick is not BOS;
- MAJOR_IDM wick is not CHoCH;
- MAJOR_IDM wick does not roll the Trading Range;
- MAJOR_IDM body close is only CHoCH-eligible pending prerequisites;
- later candles cannot retroactively rewrite an earlier classification.

### BOS downstream lifecycle
- `VALID_BOS` closes the previous Trading Range;
- `VALID_BOS` locks the current `dynamic_retracement_extreme` as the Protected Structural Extreme when sufficiency is satisfied (`dynamic_retracement_extreme` is the implementation-facing state);
- `VALID_BOS` emits `TRADING_RANGE_ROLLED_OVER`;
- previous-range POIs transition to `EXPIRED_HISTORICAL` through the **Layer-6 POI lifecycle subsystem** when a new Dealing Range is established by VALID_BOS;
- expired historical POIs are non-tradable and may remain only as historical/reaction-zone records; Layer 8 consumes the Layer-6 state and does not independently create expiration decisions;
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
ENTRY_AUTHORIZED → ORDER_FILLED
POI_TOUCH → ENTRY_AUTHORIZED
IDM_SWEEP → ENTRY_AUTHORIZED (without confirmation)
ENG_LQD_SWEEP → ENTRY_AUTHORIZED (without confirmation)
POI_MITIGATION → ENTRY_AUTHORIZED (without confirmation)
```

### Target Resolution implementation mapping

Target resolution must produce canonical target candidates before any downstream TP handling. Canonical True SMC does NOT define a universal target-selection algorithm or a universal target-selection winner.

```text
CANONICAL STRUCTURAL / LIQUIDITY TARGET CANDIDATES
        ↓
CONFIGURED TARGET POLICY
        ↓
RESOLVED TARGET
        ↓
RR EVALUATION
```

Required mappings:
- direct same-timeframe pro-trend -> current confirmed external extreme / external liquidity candidate;
- LTF execution -> explicit policy selecting `HTF_EXTERNAL_TARGET` or `LTF_STRUCTURAL_TARGET`; no implicit default;
- countertrend -> setup-specific next canonical destination candidate, such as the next valid POI, IDM, Engineering Liquidity, or external liquidity, according to the active setup contract;
- the source does not define one universal priority among all simultaneously valid target candidates;
- therefore the analyzer must not imply that Canonical SMC yields a universal target-selection winner, and must not manufacture a single universal winner target merely to satisfy an RR calculation;
- the RR gate may consume a resolved target ONLY after the configured target policy has resolved one (`RESOLVED TARGET`);
- if no valid target is resolved:
  ```text
  NO_RESOLVED_TARGET
      ↓
  NO_AUTOMATIC_TP_SUBMISSION
  ```
- under no circumstances may an implementation manufacture a target merely to satisfy the RR gate;
- a downstream configurable Target Plan may assign multiple valid target candidates to separate trade legs;
- target-leg allocation is configurable execution/trading policy and is not a new SMC structural rule;
- fixed-R targets, where permitted by the applicable policy, remain non-structural policy targets and must not be mislabeled as canonical liquidity/structure targets;
- RR calculation consumes an already resolved target; it must never create a target;
- absent resolved target -> no automatic TP submission.

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

### Order Block implementation mapping

An `ORDER_BLOCK_CANDIDATE` is evaluated against the canonical three-pillar validation before it can become a `VALIDATED_ORDER_BLOCK`. A candidate that fails validation is not promoted to a validated Order Block.

### Decisional / Extreme Order Block selection implementation mapping

Required implementation behavior:
- `DECISIONAL_ORDER_BLOCK` is the validated Order Block that actually causes the canonical `VALID_BOS` event; it is not selected solely because it is the first validated Order Block after inducement;
- the earlier `first validated Order Block after inducement` shortcut is superseded;
- `EXTREME_ORDER_BLOCK` is selected as the furthest unmitigated validated Order Block within the active `EXTREME_ORDER_FLOW` lineage; it is not selected by a global search across all origin-side Order Blocks;
- OB validity is evaluated from the canonical OB validation pillars independently of parent Order Flow mitigation/failure state;
- a valid Decisional Order Block may remain executable even while its associated Order Flow is unmitigated, subject to Rule-of-Two and all execution gates;
- later OF mitigation/failure must not retroactively rewrite the causal Decisional Order Block identity.

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
- POI ontology accepts Eligible Order Flow and Validated Order Block;
- Rejection Block is a separately typed PD-array/execution concept; source examples may use POI as a broad execution-location term, but RB is not an OF/OB-equivalent POI class or an automatic Rule-of-Two slot;
- Rule of Two limits canonical tradable POIs to Decisional POI and Extreme POI (Extreme Order Flow / Extreme Order Block);
- Origin Order Block is a latent reserve POI (mitigation transfer target when Extreme POI is mitigated), never a 3rd active POI;
- when an applicable Rule-of-Two dealing-range execution context exists, the active canonical tradable POI set has cardinality 1..2; if no valid canonical POI exists, execution fails closed with no executable POI / `NO_EVIDENCE`; no synthetic POI is created;
- Decisional buy POI is in discount, and Decisional sell POI is in premium as a hard execution eligibility gate;
- Decisional sell POI is in premium;
- Origin Order Block remains independently valid after parent OF mitigation when its own pillars remain valid;
- all three OB validation pillars are required;
- standalone FVG never becomes POI;
- standalone FVG never creates entry;
- FVG break never creates BOS/CHoCH;
- IDM never becomes POI;
- OF failure does not automatically promote Extreme POI;
- all four entry modules remain execution-layer mechanisms;
- executable setups are gated by `Projected_RR_to_Resolved_Target >= Configured_Minimum_RR` when the configured trading policy requires an RR gate; here `Resolved Target` is strictly a downstream resolved target-policy object, NOT a universal canonical SMC target; if no target is resolved (`NO_RESOLVED_TARGET`), no automatic TP submission occurs and no synthetic target may be manufactured to satisfy the RR gate;
- closed-range POIs become non-tradable after lifecycle expiration.

### Genesis
- no fabricated IDM;
- no fabricated protected swing;
- no fabricated BOS.

### CLI contract
- every documented CLI option is parsed and functionally applied;
- every CLI exposes an English --help path that succeeds without other required arguments;
- unsupported or incompatible option combinations fail explicitly;
- mapper --volume-method accepts exactly NONE, OHLC, ORDERFLOW, BOTH, with default BOTH;
- market-data --lastcandle is mutually exclusive with --starttime and --endtime;
- monitor --rr is optional and has no default;
- normal runtime remains user-silent except required errors; --debug diagnostics are emitted to stderr only.

## 49. State-Transition Coverage & Determinism

The implementation separates the structural process into three deterministic layers once the required canonical inputs exist. A candle must not directly manufacture a state transition.

### 49.1 Three-layer deterministic pipeline

```text
┌───────────────────────────────────────────────────────────────┐
│ 1. EVENT DETECTION                                            │
│                                                               │
│ Physical OHLC/level relations select exactly ONE event class  │
│ ONLY ONCE REQUIRED CANONICAL INPUTS EXIST.                    │
└───────────────────────────────┬───────────────────────────────┘
                                ↓
┌───────────────────────────────────────────────────────────────┐
│ 2. EVENT CLASSIFICATION                                       │
│                                                               │
│ Retracement sufficiency, level provenance, liquidity, and     │
│ structural prerequisite gates determine exactly ONE outcome   │
│ ONLY ONCE REQUIRED CANONICAL INPUTS EXIST.                    │
└───────────────────────────────┬───────────────────────────────┘
                                ↓
┌───────────────────────────────────────────────────────────────┐
│ 3. STATE TRANSITION                                           │
│                                                               │
│ Current State + Structural Outcome + all required canonical   │
│ process/context conditions determine exactly ONE next state   │
│ ONLY ONCE REQUIRED CANONICAL INPUTS EXIST.                    │
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

This is strictly an **implementation-level event-resolution precedence**, not a source-canonical True SMC methodology rule. It is used to deterministically resolve overlapping physical OHLC relationships and is not a new structural semantic rule, nor a basis for inventing new event classes or changing canonical event meaning.

The ownership model is expressed as:

```text
SOURCE-CANONICAL EVENT SEMANTICS
        ↓
CANONICAL STRUCTURAL IDENTITY / PROVENANCE
        ↓
IMPLEMENTATION EVENT-RESOLUTION PRECEDENCE
        ↓
ONE REPRESENTED EVENT
```

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

The classification of an opposing break consumes the context defined in `05_CHOCH_mechanics.md` and explicitly distinguishes between the **Ordinary CHoCH Route** and the **LTF Structural Glitch Route**:

```text
EXT_OPP_BREAK DETECTED
        ↓
OPERATIVE ROUTE CONTEXT
        ├─ ORDINARY CHoCH ROUTE
        │      ↓
        │  Governing Opposing Protected Structural Boundary
        │      ├─ BODY CLOSE
        │      │      ↓
        │      │  CHoCH_ELIGIBLE → ALL APPLICABLE PREREQUISITES → CHoCH_CONFIRMED / REMAIN
        │      │
        │      └─ WICK BREACH
        │             ↓
        │         LEVEL PROVENANCE
        │           ├─ MAJOR IDM PROVENANCE
        │           │    ↓
        │           │  MAJOR_IDM_SWEEP / NOT CHoCH (Trend unchanged)
        │           │
        │           └─ ELIGIBLE OPPOSING EXTERNAL BOUNDARY
        │                ↓
        │              CHoCH_ELIGIBLE → ALL APPLICABLE PREREQUISITES → CHoCH_CONFIRMED / REMAIN
        │
        └─ LTF STRUCTURAL GLITCH ROUTE (Context active per 05 §3.5.3A after HTF POI / Core Liquidity)
               ↓
           ACTIVE LTF CHoCH REFERENCE
           (Most recent valid LTF pullback / active LTF IDM reference; substituted, not promoted to Major Structure)
               ↓
           IDM PROVENANCE OF ACTIVE LTF RANGE
              ├─ MAJOR IDM PRESENT
              │    ↓
              │  Wick breach of active LTF reference may enter CHoCH qualification
              │  (CHoCH_ELIGIBLE → ALL APPLICABLE PREREQUISITES → CHoCH_CONFIRMED / REMAIN)
              │
              └─ MINOR IDM ONLY
                   ↓
                 Body close beyond active LTF reference required for CHoCH qualification
                 (CHoCH_ELIGIBLE → ALL APPLICABLE PREREQUISITES → CHoCH_CONFIRMED / REMAIN;
                  wick breach of external Major IDM remains MAJOR_IDM_SWEEP / NOT CHoCH)
```

**Context Rules:**
- **Ordinary CHoCH Route:** The governing reference is the active opposing Protected Structural Boundary / Trading Range boundary. A wick breach of a level carrying Major IDM provenance produces `MAJOR_IDM_SWEEP` (not CHoCH). A wick breach of an eligible opposing external boundary without Major IDM provenance enters the CHoCH prerequisite gate. A body close beyond the boundary enters the CHoCH gate (`CHoCH_ELIGIBLE`) and becomes `CHoCH_CONFIRMED` only when all canonical prerequisites pass.
- **LTF Structural Glitch Route:** Activated strictly after HTF POI interaction or HTF core-liquidity takeout per `05_CHOCH_mechanics.md` §3.5.3A. The reference is substituted by the most recent valid LTF pullback / active LTF IDM reference, but is **never promoted into Major Structure** and creates **no new lifecycle state**. The break mode is IDM-provenance dependent:
  - If Major IDM is present in the active LTF range, a wick breach of the active LTF reference may enter the CHoCH qualification path.
  - If only Minor IDM is present, the external protected swing functions as the Major IDM: a wick penetration of that external Major IDM remains `MAJOR_IDM_SWEEP` (not CHoCH), and CHoCH eligibility requires a completed body close beyond the active LTF CHoCH reference.
- `05_CHOCH_mechanics.md` remains the authoritative semantic owner of all CHoCH validation logic. Implementation-level classification represents and consumes these rules without redefining them.

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

The transition matrix is exhaustive and deterministic once the required canonical inputs and process/context conditions exist:

| Current State | NO_EVENT / INTERNAL_PB | MINOR_IDM_EVENT | EXT_CONT_BREAK | EXT_OPP_BREAK | MAJOR_IDM_EVENT | NEW_SVP_QUALIFIED |
|---|---|---|---|---|---|---|
| **BOOTSTRAP** | REMAIN; update provisional extremes/internal sequence | If the event physically takes the active IDM reference and thereby satisfies the L3 `IDM_TAKEN` condition: **IDM_TAKEN → SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME**; remain in the confirmation lifecycle until macro retracement qualification promotes it to **CONFIRMED_STRUCTURAL_SWING**. Otherwise (minor IDM activity that does not constitute physical takeout of the active reference): REMAIN; no confirmed range | DISQUALIFIED; no confirmed swing, therefore no BOS | DISQUALIFIED; no protected boundary, therefore no CHoCH | NOT_APPLICABLE; no active Major IDM | SVP → Verified Extreme → Minor IDM; remain BOOTSTRAP until IDM_TAKEN |
| **CONFIRMATION_LOCKED** | REMAIN; track active expansion/retrace state | **IDM_TAKEN → SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME**; macro retracement qualification → **CONFIRMED_STRUCTURAL_SWING**; remain `CONFIRMATION_LOCKED` while BOS prerequisites continue | While Gate is LOCKED: DISQUALIFIED; BOS prohibited. When Gate is UNLOCKED (via IDM_TAKEN): evaluate the transient `BOOTSTRAP_RANGE`; if `MAJOR_RETRACEMENT_QUALIFIED`: **FIRST BOS / VALID_BOS → POST_BOS**; else: **IMPULSE_EXTENSION → REMAIN** | CHoCH pipeline; qualifying break + all prerequisites → **POST_CHOCH**, otherwise REMAIN | REMAIN; Major IDM wick → `MAJOR_IDM_SWEEP`, Gate UNLOCKED, no automatic swing | FIRST_POST_CHOCH_SVP → Verified Extreme → FIRST_POST_CHOCH_MINOR_IDM; remain confirmation-locked until applicable sweep/gate prerequisites complete |
| **CONFIRMED_RANGE** | REMAIN; dynamic `dynamic_retracement_extreme` tracking | REMAIN; a later Minor IDM sweep updates the active IDM lifecycle; it does not retroactively alter an already confirmed swing | `IMPULSE_EXTENSION` → REMAIN; `VALID_BOS` → **POST_BOS** | `CHoCH_CONFIRMED` → **POST_CHOCH**; `MAJOR_IDM_SWEEP` → REMAIN; `NO_CHoCH_BREAK` → REMAIN | REMAIN; Major IDM wick → `MAJOR_IDM_SWEEP`, no CHoCH | REMAIN; new SVP supersedes the active pullback reference only when canonical IDM lifecycle requires it |
| **POST_BOS** | REMAIN; new expansion tracked, closed-range POIs expire through POI lifecycle | REMAIN; a Minor IDM does not replace the prior Major IDM | DISQUALIFIED; another BOS is not interpreted until the new swing lifecycle is established | CHoCH classification pipeline; qualifying opposing break + all prerequisites → **POST_CHOCH**, otherwise REMAIN | REMAIN; Major IDM wick → `MAJOR_IDM_SWEEP`, Gate UNLOCKED | SVP → Verified Extreme → IDM qualification; if Major IDM qualifies, it supersedes the prior Major IDM → **CONFIRMED_RANGE** |
| **POST_CHOCH** | remain in `CONFIRMATION_LOCKED` | first post-CHoCH Minor IDM pipeline; no automatic state promotion | While Gate is LOCKED: BOS prohibited. When Gate is UNLOCKED (via IDM_TAKEN): the runtime requires an explicit active-impulse origin candle to construct the transient `BOOTSTRAP_RANGE`; if origin evidence is missing, the process remains fail-closed. Otherwise, if `MAJOR_RETRACEMENT_QUALIFIED`: **FIRST BOS / VALID_BOS → POST_BOS**; else: **IMPULSE_EXTENSION → REMAIN** | body close → `CHoCH_ELIGIBLE` pending prerequisites; Major IDM wick → `MAJOR_IDM_SWEEP`; Major IDM body close enters CHoCH pipeline | Major IDM wick → `MAJOR_IDM_SWEEP`, Gate UNLOCKED, trend unchanged | FIRST_POST_CHOCH_SVP → Verified Extreme → FIRST_POST_CHOCH_MINOR_IDM; remain `CONFIRMATION_LOCKED` until applicable sweep/gate prerequisites complete |

The `POST_CHOCH` row is intentionally not a blanket `CONFIRMATION_LOCKED` transition for every event. The state remains `CONFIRMATION_LOCKED`, while the event-specific lineage and gate logic determine the next process step.

### 49.4.1 Genesis & Post-CHoCH First BOS Bootstrap Lifecycle

The source corpus does not deterministically define the first-BOS retracement baseline. This remains a source-evidence gap, not an implementation default.

The implementation contract therefore requires an isolated `BOOTSTRAP_ORIGIN_ANCHOR` derived from `C0` on initial mapping boot.

#### Bootstrap origin anchor

`BOOTSTRAP_ORIGIN_ANCHOR` is an initialization measurement anchor derived from an actual completed candle.

Its provenance must distinguish:

```text
CHART_INCEPTION_ANCHOR
    = first effective completed candle used by project-canonical initialization policy

EXPLICIT_ACTIVE_IMPULSE_ORIGIN
    = explicitly identified origin candle after CHoCH_CONFIRMED
```

The chart-inception convention is deterministic initialization policy; it is not evidence that the first available candle is the historical impulse origin.

After `CHoCH_CONFIRMED`, an explicit active-impulse origin is required and becomes the origin of the new mapped regime. Missing origin provenance fails closed.

The anchor is never a `PROTECTED_STRUCTURAL_EXTREME`, governing Dealing Range boundary, or CHoCH boundary.

#### Bootstrap measurement lifecycle

```text
C0 / BOOTSTRAP_ORIGIN_ANCHOR
        ↓
LAYER 1 / LAYER 2
        ↓
MINOR_IDM
        ↓
IDM_TAKEN
        ↓
SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME
        ↓
BOOTSTRAP_RANGE
        ↓
DYNAMIC RETRACEMENT + MACRO QUALIFICATION
        ↓
CONFIRMED_STRUCTURAL_SWING
        ↓
STRUCTURAL_SWING_BREAK
        ↓
VALID_BOS
        ↓
PROTECTED_STRUCTURAL_EXTREME
        ↓
FIRST CONFIRMED DEALING RANGE
```

`BOOTSTRAP_RANGE` is measurement-only. It introduces no new retracement threshold, candle-count rule, displacement rule, or heuristic.

The bootstrap range is activated at `SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME` establishment because that candidate supplies the structural endpoint required to measure first-BOS retracement depth. Its source candle remains separate provenance for the candidate itself.

### 49.4.2 `dynamic_retracement_extreme` implementation contract

`dynamic_retracement_extreme` is the implementation-facing representation of the live corrective extreme.

Required provenance:

```text
direction
price
source_candle_id
observed_through_candle_id
```

For bullish structure, it is the lowest relevant completed-candle LOW observed in the active retracement. For bearish structure, it is the highest relevant completed-candle HIGH.

The observation horizon is strict. The dynamic corrective state begins with the active retracement after the swing-point candidate / provisional structural extreme has been established:

```text
SWING_CANDIDATE_ESTABLISHED
        ≤
OBSERVATION CANDLE
        <
STRUCTURAL BREAK CANDLE
```

When no structural break has occurred, `observed_through_candle_id` is the latest eligible completed candle in the active retracement attempt.

At `VALID_BOS`, the dynamic state is locked using the value that existed immediately before the physical structural break:

```text
dynamic_retracement_extreme
        ↓
LOCK
        ↓
PROTECTED_STRUCTURAL_EXTREME
```

After lock:

```text
dynamic_retracement_extreme = INACTIVE
PROTECTED_STRUCTURAL_EXTREME = PRESENT
```

The dynamic and protected representations must not coexist as simultaneously active lock-state objects for the same lifecycle point.

Aggregate OHLC alone must not be used to infer intrabar ordering. Any stronger sequence claim requires independent observability evidence and must remain separate from methodology state.

When the analysis is checkpointed before `VALID_BOS`, the bootstrap anchor, confirmation-boundary provenance, and current `dynamic_retracement_extreme` must either be persisted as explicit process state or be deterministically reconstructible from the same persisted canonical candle history. A resume operation must not silently reset the dynamic extreme, substitute a different bootstrap anchor, or move the observation boundary backward/forward.

### 49.4.3 Strict first-BOS lock boundary

```text
BREAK CANDLE ∉ PRE-BOS RETRACEMENT EXTREME CALCULATION
```

The break/BOS candle is excluded because its wick may be the physical break while the candle's opposite extreme may have occurred either before or after that break. Final OHLC does not establish that ordering.

This boundary applies to the first BOS and later continuation-BOS locks unless an explicitly supported observability contract provides stronger sequence evidence. Sequence must never be inferred from candle color or final OHLC geometry.

### 49.5 Determinism invariants

The following are deterministic **once the required canonical inputs exist**:

```text
EVENT DETECTION
→ exactly ONE of 6 event classes

EVENT CLASSIFICATION
→ exactly ONE structural outcome for the detected event

STATE TRANSITION
→ exactly ONE next state for a defined Current State + Structural Outcome + all required canonical process/context conditions
```

**First-BOS Bootstrap Determinism:**
The source corpus still contains a genuine evidence gap: it does not deterministically specify the first-BOS retracement baseline. The project-canonical bootstrap policy supplies that missing process input without fabricating normal structural ontology.

Once the required origin provenance exists, the first-BOS pipeline is deterministic:

```text
C0 / BOOTSTRAP_ORIGIN_ANCHOR
→ IDM_TAKEN
→ SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME
→ MACRO RETRACEMENT QUALIFICATION
→ CONFIRMED_STRUCTURAL_SWING
→ BOOTSTRAP_RANGE
→ RETRACEMENT QUALIFICATION
→ dynamic_retracement_extreme
→ STRUCTURAL_SWING_BREAK
→ VALID_BOS
→ dynamic_retracement_extreme LOCKED
→ PROTECTED_STRUCTURAL_EXTREME
→ FIRST CONFIRMED DEALING RANGE
```

When origin provenance is missing:

```text
MISSING ORIGIN PROVENANCE
→ NO BOOTSTRAP_RANGE
→ FAIL CLOSED
→ NO VALID_BOS CLASSIFICATION
→ NO RANGE ROLLOVER
→ NO PROTECTED EXTREME LOCK
```

`first_bos_retracement_baseline_status` remains an implementation/process representation. `AVAILABLE` means the required bootstrap anchor/process input has been resolved; `UNSPECIFIED_CANONICAL_INPUT` remains a fail-closed guard when the required origin/process input is absent. It is never a structural outcome.

Additional invariants:

```text
NO_NEW_MAJOR_IDM → PRIOR_PROTECTED_BOUNDARY_REMAINS_MAJOR_IDM
MINOR_IDM_SWEEP ≠ VALID_BOS
MAJOR_IDM_SWEEP ≠ VALID_BOS
IDM_TAKEN → SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME → MACRO RETRACEMENT QUALIFICATION → CONFIRMED_STRUCTURAL_SWING
NEW_SVP ≠ AUTOMATIC MAJOR_IDM
EXT_CONT_BREAK ≠ AUTOMATIC VALID_BOS
EXT_OPP_BREAK ≠ AUTOMATIC CHoCH_CONFIRMED
GOVERNING_MAJOR_IDM_WICK_SWEEP ≠ CHoCH (Ordinary route; LTF Structural Glitch with Major IDM allows wick qualification per 05 §3.5.3A)
MAJOR_IDM + BODY CLOSE ≠ AUTOMATIC CHoCH_CONFIRMED
CONFIRMATION GATE UNLOCKED ≠ NEW STATE ENUM
BROKEN ≠ SWEPT
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

ORDINARY OPPOSING CHoCH ROUTE:
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

LTF STRUCTURAL GLITCH ROUTE (Active per 05 §3.5.3A after HTF POI / Core-Liquidity Interaction):
  Breached level is substituted by the Most Recent Valid LTF Pullback / Active LTF IDM Reference
  (Reference is NOT promoted into Major Structure; no new lifecycle state is created)

  IF Major IDM is present in active LTF range:
    wick breach of active LTF reference may enter CHoCH qualification (CHoCH_ELIGIBLE pending prerequisites)
  ELSE IF Minor IDM only is present:
    external protected swing functions as Major IDM; wick breach of external Major IDM → MAJOR_IDM_SWEEP / NOT CHoCH
    body close beyond active LTF reference required → CHoCH_ELIGIBLE (pending prerequisites)
```

### 49.7 Canonical Authority Hierarchy

For the canonical True SMC implementation, the implementation-level structural specification governs where it provides a more specific rule than earlier generic pedagogical formulations.

Therefore:
* earlier body-close-only BOS pedagogy is NOT a universal implementation rule;
* implementation-level Wick-BOS defines the valid STRUCTURAL_SWING_BREAK mechanism, while the complete VALID_BOS event still requires all canonical Major / External BOS gates;
* continuation external wick-BOS is canonical for establishing the break;
* wick interpretation is structural-context dependent.

### Layer 3 IDM implementation guard

The Layer 3 runtime MUST NOT promote a post-BOS Layer-2 pullback to `MAJOR_IDM` merely because it is the newest or because it occurs after `VALID_BOS`.

```text
VALID_BOS
  ↓
POST-BOS PRICE ACTION
  ↓
LAYER-2 CANDLE-LEVEL VALID PULLBACK
  ↓
VERIFIED PULLBACK EXTREME
  ├─ reached → MAJOR_IDM becomes active
  └─ not reached → prior protected external boundary remains MAJOR_IDM
```

A pullback-selection identifier supplied by a caller is not itself qualification evidence. The runtime must consume the canonical Layer-2 Valid Pullback → Verified Pullback Extreme state; caller selection alone cannot manufacture it. Until that state exists after `VALID_BOS`, the prior protected external boundary remains the active Major IDM.

### Layer 3 retracement implementation guard

The standard equilibrium path is evaluated first and requires the normal opposing-candle count. The reduced displacement exception is evaluated only when the standard path does not qualify and its explicit extreme-taking evidence is present.

The reduced exception may use the documented one- or two-candle displacement case. The implementation must not collapse the exception into the normal candle-count rule and must not treat candle count alone as qualification.

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

Configuration may alter parameters but cannot manufacture structural truth.
