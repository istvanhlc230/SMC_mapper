# IMPLEMENTATION

**Role:** How the mapper represents and transitions canonical methodology objects.

**Authority boundary:** Implementation follows methodology. Implementation convenience must never redefine methodology.

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

The mapper is a state machine. Each event must be evaluated against current state, not only against the current candle.

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

## Implementation boundary

The following must remain separate state objects or semantically equivalent state representations:

```text
ACTIVE PULLBACK POINTER
≠ MINOR IDM STATE
≠ MAJOR IDM STATE
≠ FALLBACK MAJOR IDM STATE
≠ CONFIRMED SWING
≠ TRADING RANGE
≠ HISTORICAL STRUCTURE
```

Configuration may alter parameters but cannot manufacture structural truth. Scoring evaluates validated structural state and cannot create or validate structure.
