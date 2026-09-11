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
CONFIRMED SWING
PROTECTED STRUCTURAL EXTREME
PHYSICAL EXTERNAL BREAK
BOS
CHoCH
TRADING RANGE
```

Functions equivalent to `finish_pullback()` must not promote a candle-level pullback directly to IDM.

Functions equivalent to `detect_idm_sweep()` must operate on the active qualified IDM and must not themselves declare BOS, CHoCH, or Confirmed Swing without the remaining canonical prerequisites.

Functions equivalent to `detect_bos()` must require:

1. eligible Confirmed Continuation Swing;
2. retracement sufficiency;
3. physical external break;
4. canonical Body-Close or Wick-Break classification;
5. exclusion of the Fallback Major IDM / Range-Boundary Proxy exception.

A Fallback Major IDM wick penetration must terminate as `MAJOR_IDM_SWEEP`, not BOS.

Functions equivalent to `detect_choch()` must use the governing opposing Protected Structural Extreme / Trading Range boundary and must enforce the complete CHoCH prerequisites. A body close beyond the boundary is not, by itself, sufficient to declare `VALID_CHoCH`.

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

The break-classification branch is:

```text
PHYSICAL EXTERNAL BREAK
        ↓
     LEVEL IDENTITY
        │
   ┌────┴─────────────┐
   │                  │
NON-FALLBACK        FALLBACK PROXY
   │                  │
   ├─ Body Close      ├─ Wick Breach
   │    ↓              │    ↓
   │ VALID_BOS         │ MAJOR_IDM_SWEEP
   │                   │    ↓
   └─ Wick Break       │ Gate unlocked only
        ↓              │
    VALID_BOS          └─ Body Close through
                           opposing boundary
                              ↓
                         CHoCH eligibility
```

Wick-BOS is immediate for an eligible non-fallback external continuation level. It is not delayed waiting for a later body close.

### CHoCH path

```text
CURRENT RANGE
 ↓
GOVERNING OPPOSING PROTECTED EXTREME
 ↓
PHYSICAL BOUNDARY VIOLATION
 ↓
CHoCH STRUCTURAL PREREQUISITES
 ↓
VALID_CHoCH
 ↓
NEW TREND
 ↓
CHoCH-CAUSING LEG = INITIAL ACTIVE IMPULSE
 ↓
NEW STRUCTURALLY VALID PULLBACK
 ↓
NEW ACTIVE/MINOR IDM
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
24. A fallback proxy wick causes Trading Range rollover.
25. Genesis manufactures IDM or protected structure.
26. The obsolete sub-38.2% Fibonacci variant remains anywhere in methodology semantics.
27. Scoring creates structural validity.
28. Historical liquidity remains active merely because it exists in history.
29. One outside bar activates both directional branches.
30. Inside-bar breaks are treated as independent pullbacks.
31. Structural engine directly deletes or mutates POI registry state on range rollover.
32. POIs from a closed Trading Range remain tradable after `TRADING_RANGE_ROLLED_OVER`.

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
- correct Real Major IDM lifecycle after BOS;
- CHoCH does not automatically apply the BOS Major IDM lifecycle;
- historical IDM is not an active competing target;
- IDM wick takeout;
- IDM body takeout.

### Swing / Protected Extreme
- qualified IDM sweep unlocks the Swing Confirmation Gate;
- qualified IDM sweep does not automatically create Confirmed Swing;
- dynamic absolute retracement extreme tracking;
- standard retracement sufficiency;
- exact 2-candle exception;
- insufficient retracement remains `IMPULSE_EXTENSION`;
- Protected Extreme locks only at valid BOS;
- fallback proxy wick does not lock Protected Extreme.

### BOS
- BOS requires eligible Confirmed Continuation Swing;
- BOS requires retracement sufficiency;
- physical external break is distinct from BOS;
- external Body-Close BOS;
- external Wick-Break BOS;
- wick-BOS does not require a later body close;
- close exactly at the broken level remains valid Wick-BOS;
- fallback proxy wick is `MAJOR_IDM_SWEEP`;
- fallback proxy wick is not BOS;
- fallback proxy wick is not CHoCH;
- fallback proxy wick does not roll the Trading Range;
- fallback proxy body close is only CHoCH-eligible pending 3.5 prerequisites;
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
- CHoCH creates new trend lifecycle;
- CHoCH-causing leg becomes initial active impulse;
- CHoCH does not create a Protected Structural Extreme automatically;
- fallback proxy exception remains distinct from normal CHoCH qualification.

### Trading Range
- bullish/bearish BOS establishes the new range;
- internal fluctuations do not shift the primary boundary;
- minor high/low does not create a new range;
- deep retracement does not automatically reset range;
- fallback proxy wick does not roll the range.

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
- minimum 1:2 RR is enforced for executable setups;
- closed-range POIs become non-tradable after lifecycle expiration.

### Genesis
- no fabricated IDM;
- no fabricated protected swing;
- no fabricated BOS.

### Obsolete concepts
- no obsolete sub-38.2% Fibonacci state, alias, or setup classification.

## 49. State-Transition Coverage & Determinism — VALIDATED / CLOSED

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

`IMPULSE_EXTENSION`, `VALID_BOS`, `VALID_CHoCH`, `MAJOR_IDM_SWEEP`, and `NO_CHoCH_BREAK` are **classification outcomes**, not additional event classes.

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
RETRACEMENT SUFFICIENCY GATE
        ├─ NOT_SATISFIED
        │      ↓
        │  OUTCOME = IMPULSE_EXTENSION
        │
        └─ SATISFIED
               ↓
        LEVEL PROVENANCE
          ├─ REAL
          │   ↓
          │ OUTCOME = VALID_BOS
          │
          └─ FALLBACK
              ↓
          OUTCOME = MAJOR_IDM_SWEEP
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
        │      ├─ PASS → VALID_CHoCH
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
          ├─ PASS → VALID_CHoCH
          └─ FAIL → REJECTION / REMAIN
```

A body close beyond the opposing boundary is never `VALID_CHoCH` by geometry alone. It first creates CHoCH eligibility and must pass the complete canonical prerequisite gate.

### 49.4 State-transition coverage

The five lifecycle states are:

```text
BOOTSTRAP
CONFIRMATION_LOCKED
CONFIRMED_RANGE
POST_BOS
POST_CHOCH
```

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
| **CONFIRMATION_LOCKED** | REMAIN; track active expansion/retrace state | Gate UNLOCKED; remaining prerequisites required before **CONFIRMED_RANGE** | DISQUALIFIED; BOS prohibited while confirmation is locked | CHoCH pipeline; qualifying break + all prerequisites → **POST_CHOCH**, otherwise REMAIN | REMAIN; fallback wick → `MAJOR_IDM_SWEEP`, Gate UNLOCKED, no automatic swing | NOT_APPLICABLE; no Real Major IDM in this phase | REMAIN; first post-CHoCH SVP establishes the Minor IDM pipeline |
| **CONFIRMED_RANGE** | REMAIN; dynamic `E_retrace` tracking | REMAIN; Minor IDM sweep unlocks gate, trend/range remain active | `IMPULSE_EXTENSION` → REMAIN; `VALID_BOS` → **POST_BOS**; `MAJOR_IDM_SWEEP` → REMAIN | `VALID_CHoCH` → **POST_CHOCH**; `MAJOR_IDM_SWEEP` → REMAIN; `NO_CHoCH_BREAK` → REMAIN | REMAIN; fallback wick → `MAJOR_IDM_SWEEP`, no CHoCH | REMAIN; Real Major IDM sweep unlocks/updates the applicable gate state | REMAIN; new SVP supersedes the previous active pullback reference where canonical lifecycle rules require it |
| **POST_BOS** | REMAIN; new expansion tracked, closed-range POIs expire through POI lifecycle | NOT_APPLICABLE until a qualifying post-BOS SVP creates the new Minor IDM lifecycle | DISQUALIFIED; another BOS is not interpreted until the new swing lifecycle is established | CHoCH classification pipeline; qualifying opposing break + all prerequisites → **POST_CHOCH**, otherwise REMAIN | REMAIN; fallback proxy wick → `MAJOR_IDM_SWEEP`, Gate UNLOCKED | NOT_APPLICABLE until the post-BOS SVP → Extreme → Eligibility pipeline exists | REMAIN; SVP → Verified Extreme → Major IDM Eligibility → **REAL_MAJOR_IDM** → fallback superseded → **CONFIRMED_RANGE** |
| **POST_CHOCH** | → `CONFIRMATION_LOCKED` | → `CONFIRMATION_LOCKED` | → `CONFIRMATION_LOCKED` | → `CONFIRMATION_LOCKED` | → `CONFIRMATION_LOCKED` | → `CONFIRMATION_LOCKED` | → `CONFIRMATION_LOCKED` |

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
EXT_OPP_BREAK ≠ AUTOMATIC VALID_CHoCH
IMPULSE_EXTENSION ≠ EVENT CLASS
```

The state machine must preserve provenance, prerequisite gates, and anti-retroactive event classification. A later candle may advance state but may not rewrite a previously classified event.

**Verdict: PASS / CLOSED.**

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
