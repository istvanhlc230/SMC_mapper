# IMPLEMENTATION

**Role:** How the mapper represents and transitions canonical methodology objects.

**Authority boundary:** Implementation follows methodology. Implementation convenience must never redefine methodology.

## Canonical lifecycle source

The validated structural lifecycle rules are defined in `03_structural_lifecycle.md`, with detailed BOS mechanics in `03_structural_lifecycle_bos.md` and detailed CHoCH mechanics in `03_structural_lifecycle_choch.md`.

The mapper must implement those rules without inventing alternative BOS or CHoCH semantics.

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
CONFIRMED_STRUCTURAL_SWING
PROTECTED STRUCTURAL EXTREME
PHYSICAL EXTERNAL BREAK
VALID_BOS
CHoCH_CONFIRMED
TRADING RANGE
```

Functions equivalent to `finish_pullback()` must not promote a candle-level pullback directly to IDM.

Functions equivalent to `detect_idm_sweep()` must operate on the active qualified IDM and must not themselves declare VALID_BOS, CHoCH_CONFIRMED, or CONFIRMED_STRUCTURAL_SWING without the remaining canonical prerequisites.

Functions equivalent to `detect_bos()` must require:

1. eligible CONFIRMED_STRUCTURAL_SWING;
2. retracement sufficiency (`RETRACEMENT_DEPTH >= 0.382`);
3. physical external break (`STRUCTURAL_SWING_BREAK` via wick or body);
4. `IDM_TAKEN == True`;
5. exclusion of the FALLBACK_MAJOR_IDM exception.

A Fallback Major IDM wick penetration must terminate as `MAJOR_IDM_SWEEP`, not BOS.

Functions equivalent to `detect_choch()` must use the governing opposing Protected Structural Extreme / Trading Range boundary and must enforce the complete CHoCH prerequisites. A body close beyond the boundary is not, by itself, sufficient to declare `CHoCH_CONFIRMED`.

### 45.1 Entity lifecycle schemas

Liquidity levels and protected structural boundaries are different ontology classes. Their lifecycle semantics must not be collapsed into one undifferentiated state enum.

#### LiquidityState

Applies to liquidity entities such as Minor IDM, Real Major IDM, and Engineering Liquidity:

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
Real Major IDM     = 80
Fallback Major IDM = 40
```

These values are scoring outputs applied to already-established methodology state.

### Boundary

```
05_risk.md
    → semantic risk policy

06_implementation.md
    → executable scoring representation

SMC_mapper.py
    → actual calculation
```

Therefore, a future change to the executable risk formula must first be classified as an implementation change and must not silently become a new methodology rule.

## 46. Structural state machine

The mapper is a state machine. Each event must be evaluated against current structural state, not only against the current candle.

### BOS path

```text
OBSERVATION
 ↓
CANDLE-LEVEL VALID PULLBACK
 ↓
STRUCTURAL QUALIFICATION
 ↓
STRUCTURALLY VALID PULLBACK
 ↓
VERIFIED PULLBACK EXTREME
 ↓
LIQUIDITY
 ↓
ACTIVE IDM
 ↓
IDM SWEEP
 ↓
SWING CONFIRMATION GATE
 ↓
CONFIRMED SWING
 ↓
RETRACEMENT SUFFICIENCY
 ↓
PHYSICAL EXTERNAL BREAK
 ↓
BREAK CLASSIFICATION
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

The canonical BOS predicate:

```text
VALID_BOS ⇔
    IDM_TAKEN
    AND RETRACEMENT_DEPTH >= 0.382
    AND STRUCTURAL_SWING_BREAK
```

If any prerequisite is missing, the break cannot produce `VALID_BOS`.

**VALID_BOS**

If the BOS gate is satisfied, the dealing range rolls over and the Protected Structural Extreme locks.

**IMPULSE_EXTENSION**

If qualification is not satisfied, the break is classified as `IMPULSE_EXTENSION`.

No rollover occurs, and no Protected Structural Extreme is locked.

---

## 6.X — Fallback Major IDM Interaction (Opposing Boundary Only)

Fallback Major IDM is never part of continuation BOS provenance.

It appears only on the opposing boundary when no post-BOS structurally valid pullback exists.

### Fallback Interaction Rules

```text
FALLBACK_MAJOR_IDM + wick breach
→ MAJOR_IDM_SWEEP

FALLBACK_MAJOR_IDM + body close
→ CHoCH_ELIGIBLE
→ CHoCH_CONFIRMED (only if all CHoCH prerequisites pass)
```

`MAJOR_IDM_SWEEP` never produces `VALID_BOS`.

`MAJOR_IDM_SWEEP` never produces `CHoCH_CONFIRMED`.

`MAJOR_IDM_SWEEP` never rolls over the dealing range.

`MAJOR_IDM_SWEEP` never locks a Protected Structural Extreme.

When the first valid post-BOS pullback forms:

```text
REAL_MAJOR_IDM is created
FALLBACK_MAJOR_IDM is permanently superseded
```

---

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
              FALLBACK_MAJOR_IDM
```

The two lineages are not interchangeable:

```text
FIRST_POST_CHOCH_SVP ≠ FIRST_POST_CHOCH_MINOR_IDM
FALLBACK_MAJOR_IDM ≠ REAL_MAJOR_IDM
```

A qualifying sweep of the applicable IDM lineage unlocks the Confirmation Gate. IDM takeout exclusively opens the `SWING_CONFIRMATION_GATE` and confirms the provisional swing only (`IDM_TAKEN = TRUE`); it does NOT create a new Dealing Range, does NOT flip trend, is NEVER a CHoCH, does NOT create `VALID_BOS`, and does NOT roll the dealing range (`CONFIRMED_STRUCTURAL_SWING ≠ VALID_BOS`). `CONFIRMATION GATE UNLOCKED` is a process condition, not a new state enum such as `non-canonical pending-range state`.

```text
CONFIRMATION_LOCKED
        │
        ├─ FIRST_POST_CHOCH_MINOR_IDM sweep
        │
        └─ FALLBACK_MAJOR_IDM sweep
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
          REAL_MAJOR_IDM
                 ↓
       FALLBACK → SUPERSEDED
```

Fallback boundary classification remains provenance-sensitive:

```text
FALLBACK_MAJOR_IDM + WICK BREACH
→ MAJOR_IDM_SWEEP
→ trend unchanged
→ no BOS
→ no CHoCH
→ no Trading Range rollover
→ Gate may unlock, subject to remaining swing prerequisites

FALLBACK_MAJOR_IDM + BODY CLOSE
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
18. Fallback Major IDM is treated as a real Major IDM.
19. Fallback Major IDM wick penetration becomes BOS or CHoCH.
20. `MAJOR_IDM_SWEEP` automatically confirms a swing instead of only unlocking the Swing Confirmation Gate.
21. A body close beyond the opposing boundary is treated as CHoCH without all CHoCH prerequisites.
22. A later candle retroactively rewrites an earlier `MAJOR_IDM_SWEEP` or BOS classification.
23. A `VALID_BOS` is delayed pending a later body close when the wick-BOS path is already valid.
24. A FALLBACK_MAJOR_IDM wick causes Trading Range rollover.
25. Genesis manufactures IDM or protected structure.
26. The obsolete sub-38.2% Fibonacci variant remains anywhere in methodology semantics.
27. Scoring creates structural validity.
28. Historical liquidity remains active merely because it exists in history.
29. One outside bar activates both directional branches.
30. Inside-bar breaks are treated as independent pullbacks.
31. Structural engine directly deletes or mutates POI registry state on range rollover.
32. POIs from a closed Trading Range remain tradable after `TRADING_RANGE_ROLLED_OVER`.
33. `BROKEN` is applied to a liquidity entity.
34. A liquidity `SWEPT` event is misclassified as a structural `BROKEN` event.
35. `CONFIRMATION GATE UNLOCKED` is introduced as a new lifecycle state enum.
36. `FALLBACK_MAJOR_IDM + BODY CLOSE` is treated as automatic `CHoCH_CONFIRMED`.
37. Confirmed Swing is treated as automatic `VALID_BOS` without retracement sufficiency (>= 38.2%).
38. Break of Confirmed Swing is classified as `VALID_BOS` when retracement depth < 38.2% (must be `IMPULSE_EXTENSION`).
39. Any heuristic/safe mode is used to substitute for mandatory 38.2% depth.
40. A 1-candle retracement is permitted to qualify for macro BOS under any circumstances.

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
- standard >=3-candle qualification;
- configurable minimum retracement (canonical default 38.2%);
- exact 2-candle + depth >= 38.2% exception;
- candle count sweep must NOT qualify without >= 38.2% depth;
- sub-38.2% break with IDM taken is classified as IMPULSE_EXTENSION (not VALID_BOS);
- one candle does not automatically qualify (1 opposing candle never qualifies macro BOS).

### IDM
- candle-level pullback does not create IDM;
- structurally valid pullback can create IDM;
- newest valid pullback replaces old active IDM;
- only one active minor IDM;
- real versus fallback Major IDM;
- correct Real Major IDM lifecycle after BOS;
- CHoCH does not automatically apply the BOS Major IDM lifecycle;
- historical IDM is not an active competing target;
- IDM wick takeout;
- IDM body takeout;
- fallback provenance remains distinct from Real Major IDM provenance.

### Entity lifecycle ontology
- liquidity entity can transition `ACTIVE → SWEPT`;
- newer valid pullback can supersede active liquidity;
- historical liquidity is not active merely because it remains in history;
- structural boundary can transition to `BROKEN` only through the applicable structural break lifecycle;
- liquidity entity can never receive `BROKEN` semantics;
- `BROKEN` and `SWEPT` remain semantically distinct even if an implementation shares a technical field.

### Swing / Protected Extreme
- qualified IDM sweep unlocks the Swing Confirmation Gate;
- qualified IDM sweep does not automatically create Confirmed Swing;
- dynamic absolute retracement extreme tracking;
- standard retracement sufficiency;
- exact 2-candle exception;
- insufficient retracement remains `IMPULSE_EXTENSION`;
- Protected Structural Extreme locks only at valid BOS;
- FALLBACK_MAJOR_IDM wick does not lock Protected Structural Extreme.

### BOS
- BOS requires eligible Confirmed Continuation Swing;
- BOS requires retracement sufficiency;
- physical external break is distinct from BOS;
- external Body-Close BOS;
- external Wick-Break BOS;
- wick-BOS does not require a later body close;
- close exactly at the broken level remains valid Wick-BOS;
- FALLBACK_MAJOR_IDM wick is `MAJOR_IDM_SWEEP`;
- FALLBACK_MAJOR_IDM wick is not BOS;
- FALLBACK_MAJOR_IDM wick is not CHoCH;
- FALLBACK_MAJOR_IDM wick does not roll the Trading Range;
- FALLBACK_MAJOR_IDM body close is only CHoCH-eligible pending prerequisites;
- later candles cannot retroactively rewrite an earlier classification.

### BOS downstream lifecycle
- `VALID_BOS` closes the previous Trading Range;
- `VALID_BOS` locks `E_retrace` as Protected Structural Extreme when sufficiency is satisfied;
- `VALID_BOS` emits `TRADING_RANGE_ROLLED_OVER`;
- previous-range POIs transition to `EXPIRED_HISTORICAL` through the POI lifecycle subsystem;
- expired historical POIs are non-tradable;
- new range initializes Fallback Major IDM until a Real Major IDM is independently qualified;
- first post-break SVP does not directly equal Real Major IDM; the full eligibility chain is required.

### CHoCH
- correct governing opposing Protected Structural Extreme is used;
- Minor Structure takeout does not create CHoCH;
- IDM sweep does not create CHoCH;
- continuation swing break follows BOS path, not CHoCH;
- physical opposing-boundary violation only opens CHoCH eligibility;
- body close beyond boundary is not sufficient without full CHoCH prerequisites;
- fallback boundary body close is `CHoCH_ELIGIBLE`, not automatic CHoCH confirmation;
- CHoCH creates new trend lifecycle;
- CHoCH-causing leg becomes initial active impulse;
- CHoCH does not create a Protected Structural Extreme automatically;
- first post-CHoCH SVP and first post-CHoCH Minor IDM remain distinct lineage objects;
- FALLBACK_MAJOR_IDM lineage remains distinct from internal Minor IDM lineage;
- confirmation gate unlock is a process condition, not a new state enum;
- FALLBACK_MAJOR_IDM exception remains distinct from normal CHoCH qualification.

### Trading Range
- bullish/bearish BOS establishes the new range;
- internal fluctuations do not shift the primary boundary;
- minor high/low does not create a new range;
- deep retracement does not automatically reset range;
- FALLBACK_MAJOR_IDM wick does not roll the range.

### POI / Entry
- POI ontology accepts only Valid OF or Valid OB;
- Rule of Two limits canonical tradable POIs to Decisional POI and Extreme POI;
- Origin OB is a latent reserve POI (mitigation transfer target when Extreme POI is mitigated), never a 3rd active POI;
- scanner must never permit 3 simultaneously active POIs;
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
- minimum 1:2 RR is enforced for executable setups;
- closed-range POIs become non-tradable after lifecycle expiration.

### Genesis
- no fabricated IDM;
- no fabricated protected swing;
- no fabricated BOS.

### Obsolete concepts
- no obsolete sub-38.2% Fibonacci state, alias, or setup classification.

## 49. State-Transition Coverage & Determinism

The structural state machine is formally separated into three deterministic layers. A candle must not directly manufacture a state transition.

### 49.1 Three-layer deterministic pipeline

```text
┌───────────────────────────────────────────────────────────────┐
│ 1. EVENT DETECTION                                            │
│                                                               │
│ Physical OHLC/level relations select exactly ONE of the       │
│ seven disjoint event classes.                                 │
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

### 49.2 Seven disjoint event classes

Exactly one event class is emitted by Event Detection:

```text
1. NO_EVENT / INTERNAL_PB
2. MINOR_IDM_EVENT
3. EXT_CONT_BREAK
4. EXT_OPP_BREAK
5. FALLBACK_EVENT
6. REAL_MAJOR_IDM_EVENT
7. NEW_SVP_QUALIFIED
```

Detection precedence is:

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

The precedence applies only to **event detection**. It does not directly declare a structural outcome or next state.

Where multiple physical relationships appear possible, the event is resolved using the canonical structural identity and active lifecycle of the referenced level. Geometry alone must not manufacture a competing event class.

### 49.3 Event classification rules

#### `EXT_CONT_BREAK`

```text
EXT_CONT_BREAK DETECTED
        ↓
CONSUME STORED QUALIFICATION (Depth >= 38.2% AND >= 3 opposing candles [or 2-candle exception])
        ├─ DISQUALIFIED (Depth < 38.2% or Opposing Candles Insufficient)
        │      ↓
        │  OUTCOME = IMPULSE_EXTENSION (Dealing range remains open, no new protected extreme)
        │
        └─ QUALIFIED (IDM_TAKEN = TRUE AND Depth >= 38.2% AND Opposing Candles Satisfied)
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
        │  ALL CHoCH PREREQUISITES
        │      ├─ PASS → CHoCH_CONFIRMED
        │      └─ FAIL → REJECTION / REMAIN
        │
        └─ WICK BREACH
               ↓
        LEVEL PROVENANCE
          ├─ FALLBACK
          │    ↓
          │  MAJOR_IDM_SWEEP
          │
          └─ REAL
               ↓
        REAL_MAJOR_IDM?
          ├─ NO → NO_CHoCH_BREAK / REMAIN
          └─ YES
               ↓
        CHoCH_ELIGIBLE
               ↓
        ALL CHoCH PREREQUISITES
          ├─ PASS → CHoCH_CONFIRMED
          └─ FAIL → REJECTION / REMAIN
```

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

The seven detected event classes are:

```text
NO_EVENT / INTERNAL_PB
MINOR_IDM_EVENT
EXT_CONT_BREAK
EXT_OPP_BREAK
FALLBACK_EVENT
REAL_MAJOR_IDM_EVENT
NEW_SVP_QUALIFIED
```

The transition matrix is exhaustive and deterministic:

| Current State | NO_EVENT / INTERNAL_PB | MINOR_IDM_EVENT | EXT_CONT_BREAK | EXT_OPP_BREAK | FALLBACK_EVENT | REAL_MAJOR_IDM_EVENT | NEW_SVP_QUALIFIED |
|---|---|---|---|---|---|---|---|
| **BOOTSTRAP** | REMAIN; update provisional extremes/internal sequence | REMAIN; no confirmed range | DISQUALIFIED; no confirmed swing, therefore no BOS | DISQUALIFIED; no protected boundary, therefore no CHoCH | NOT_APPLICABLE; no fallback level | NOT_APPLICABLE; no Real Major IDM | SVP → Verified Extreme → IDM → Sweep → Gate → **CONFIRMED_RANGE** |
| **CONFIRMATION_LOCKED** | REMAIN; track active expansion/retrace state | Gate UNLOCKED; remaining prerequisites required before **CONFIRMED_RANGE** | DISQUALIFIED; BOS prohibited while confirmation is locked | CHoCH pipeline; qualifying break + all prerequisites → **POST_CHOCH**, otherwise REMAIN | REMAIN; FALLBACK_MAJOR_IDM wick → `MAJOR_IDM_SWEEP`, Gate UNLOCKED, no automatic swing | NOT_APPLICABLE; no Real Major IDM in this phase | FIRST_POST_CHOCH_SVP → Verified Extreme → FIRST_POST_CHOCH_MINOR_IDM; remain confirmation-locked until applicable sweep/gate prerequisites complete |
| **CONFIRMED_RANGE** | REMAIN; dynamic `E_retrace` tracking | REMAIN; Minor IDM sweep unlocks gate, trend/range remain active | `IMPULSE_EXTENSION` → REMAIN; `VALID_BOS` → **POST_BOS** | `CHoCH_CONFIRMED` → **POST_CHOCH**; `MAJOR_IDM_SWEEP` → REMAIN; `NO_CHoCH_BREAK` → REMAIN | REMAIN; FALLBACK_MAJOR_IDM wick → `MAJOR_IDM_SWEEP`, no CHoCH | REMAIN; Real Major IDM sweep unlocks/updates the applicable gate state | REMAIN; new SVP supersedes the previous active pullback reference where canonical lifecycle rules require it |
| **POST_BOS** | REMAIN; new expansion tracked, closed-range POIs expire through POI lifecycle | NOT_APPLICABLE until a qualifying post-BOS SVP creates the new Minor IDM lifecycle | DISQUALIFIED; another BOS is not interpreted until the new swing lifecycle is established | CHoCH classification pipeline; qualifying opposing break + all prerequisites → **POST_CHOCH**, otherwise REMAIN | REMAIN; FALLBACK_MAJOR_IDM wick → `MAJOR_IDM_SWEEP`, Gate UNLOCKED | NOT_APPLICABLE until the post-BOS SVP → Extreme → Eligibility pipeline exists | SVP → Verified Extreme → Major IDM Eligibility → **REAL_MAJOR_IDM** → FALLBACK_MAJOR_IDM superseded → **CONFIRMED_RANGE** |
| **POST_CHOCH** | remain in `CONFIRMATION_LOCKED` | first post-CHoCH Minor IDM pipeline; no automatic state promotion | BOS prohibited while confirmation remains locked | body close → `CHoCH_ELIGIBLE` pending prerequisites; FALLBACK_MAJOR_IDM wick → `MAJOR_IDM_SWEEP`; Real Major IDM + qualifying opposing wick → CHoCH pipeline | FALLBACK_MAJOR_IDM wick → `MAJOR_IDM_SWEEP`, Gate UNLOCKED, trend unchanged | NOT_APPLICABLE until independent post-BOS Real Major IDM lifecycle | FIRST_POST_CHOCH_SVP → Verified Extreme → FIRST_POST_CHOCH_MINOR_IDM; remain `CONFIRMATION_LOCKED` until applicable sweep/gate prerequisites complete |

The `POST_CHOCH` row is intentionally not a blanket `CONFIRMATION_LOCKED` transition for every event. The state remains `CONFIRMATION_LOCKED`, while the event-specific lineage and gate logic determine the next process step.

### 49.5 Determinism invariants

The following are mandatory:

```text
EVENT DETECTION
→ exactly ONE of 7 event classes

EVENT CLASSIFICATION
→ exactly ONE structural outcome for the detected event

STATE TRANSITION
→ exactly ONE next state for Current State + Outcome
```

Additional invariants:

```text
NO_REAL_MAJOR_IDM ≠ FALLBACK
MINOR_IDM_SWEEP ≠ AUTOMATIC CONFIRMED_SWING
MAJOR_IDM_SWEEP ≠ AUTOMATIC CONFIRMED_SWING
NEW_SVP ≠ AUTOMATIC REAL_MAJOR_IDM
EXT_CONT_BREAK ≠ AUTOMATIC VALID_BOS
EXT_OPP_BREAK ≠ AUTOMATIC CHoCH_CONFIRMED
FALLBACK_MAJOR_IDM + WICK ≠ CHoCH
FALLBACK_MAJOR_IDM + BODY CLOSE ≠ AUTOMATIC CHoCH_CONFIRMED
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

  IF IDM_TAKEN AND RETRACEMENT_DEPTH >= 0.382:
      classify as VALID_BOS
      lock Protected Structural Extreme
      perform Trading Range Rollover
  ELSE:
      classify according to existing insufficient-gate / IMPULSE_EXTENSION logic

  (Do NOT require body close to establish STRUCTURAL_SWING_BREAK in this continuation case)

IF breached level == OPPOSING_PROTECTED_BOUNDARY
  AND REAL_MAJOR_IDM independently exists
THEN:
  wick breach → CHoCH_ELIGIBLE

IF breached level == FALLBACK_MAJOR_IDM
  AND REAL_MAJOR_IDM does not yet exist
THEN:
  wick breach → MAJOR_IDM_SWEEP
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
≠ FALLBACK MAJOR IDM STATE
≠ CONFIRMED SWING
≠ PROTECTED STRUCTURAL EXTREME
≠ TRADING RANGE
≠ HISTORICAL STRUCTURE
≠ POI LIFECYCLE STATE
```

The structural engine may emit lifecycle events such as `TRADING_RANGE_ROLLED_OVER`, but the POI lifecycle subsystem owns POI state mutation.

Configuration may alter parameters but cannot manufacture structural truth. Scoring evaluates validated structural state and cannot create or validate structure.
