# IMPLEMENTATION

**Role:** How the mapper represents and transitions canonical methodology objects.

**Authority boundary:** Implementation follows methodology. Implementation convenience must never redefine methodology.

## Canonical lifecycle source

The validated structural lifecycle rules are defined in `true_smc_structural_lifecycle.md` and are part of the canonical methodology authority.

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
