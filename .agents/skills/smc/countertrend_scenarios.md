# TRUE SMC — COUNTERTREND SCENARIOS

**Role:** Canonical scenario composition for the three countertrend setups described in the authoritative knowledgebase.

**Authority boundary:** This document composes existing canonical structural, liquidity, POI, CHoCH, entry, and risk rules. It does not redefine those underlying semantics.

## 1. Scenario architecture

Countertrend scenarios are not a fourth structural regime. They are execution scenarios that operate against the currently prevailing HTF direction while consuming canonical lower-timeframe structure and liquidity.

All three scenarios must use existing canonical entry modules and must not create alternate IDM, POI, BOS, or CHoCH definitions.

## 2. Scenario CT1 — Internal Structure Toward Inducement Takeout

Source concept:
- while the prevailing HTF trend remains active;
- price has not yet taken the active inducement;
- pre-inducement Order Flow / Order Block formations are not tradable POIs in the countertrend path;
- lower-timeframe internal structure is followed toward the inducement.

Canonical flow:

```text
PREVAILING HTF DIRECTION
        ↓
ACTIVE INDUCEMENT EXISTS
        ↓
LTF INTERNAL STRUCTURE DEVELOPS TOWARD IDM
        ↓
PRE-IDM OF/OB
        ↓
SMT / INDUCEMENT-TRAP EXCLUSION
        ↓
IDM / CORE-LIQUIDITY DESTINATION
        ↓
EXISTING ENTRY MODULE
```

The countertrend position is an execution opportunity toward the canonical inducement target. The LTF structure does not alter the HTF bias merely by forming.

No arbitrary pre-inducement POI may be used as the countertrend entry location.

## 3. Scenario CT2 — Inducement Liquidity Run

Source concept:
- price takes the initial inducement;
- the expected reversal does not have to occur immediately;
- price may continue against the prevailing trend toward the next canonical liquidity layer or valid POI;
- the lower timeframe can expose the internal structure of this extended delivery.

Canonical flow:

```text
IDM_TAKEN
    ↓
INITIAL COUNTERTREND DELIVERY
    ↓
ADDITIONAL CANONICAL LIQUIDITY / VALID POI
    ├─ ENGINEERING LIQUIDITY
    └─ VALID DECISIONAL / EXTREME POI
    ↓
EXISTING ENTRY MODULE
    ↓
COUNTERTREND EXECUTION
```

The existence of an initial IDM sweep does not force an immediate reversal entry. The scenario remains active while additional canonical liquidity delivery is occurring.

## 4. Scenario CT3 — Core Liquidity Sweep Failure / POI Failure

Source concept:
- price first sweeps an inducement and can show an initial reaction;
- that reaction can fail;
- price can continue toward a deeper canonical POI;
- a second dealing-range failure can produce CHoCH;
- LTF structure provides the execution representation of the countertrend move.

Canonical flow:

```text
IDM / CORE-LIQUIDITY SWEEP
        ↓
INITIAL REACTION
        ↓
REACTION HOLDS?
   ├─ YES → existing pro-trend continuation logic remains available
   └─ NO
       ↓
DEEPER CANONICAL POI / CORE LIQUIDITY
       ↓
LTF STRUCTURAL RE-EVALUATION
       ↓
CHoCH ROUTE WHEN ITS PREREQUISITES PASS
       ↓
EXISTING ENTRY MODULE
```

A POI failure is an execution/scenario observation and does not itself create CHoCH. The CHoCH event remains governed by `05_CHOCH_mechanics.md`, including its LTF-CHoCH context when applicable.

## 5. Multi-timeframe rule

For countertrend scenarios:

```text
HTF
→ narrative / prevailing direction / canonical POIs / core liquidity

LTF
→ internal structure / execution refinement / LTF-CHoCH context
```

The LTF must not silently redefine HTF structure. When the source-defined HTF-interaction condition activates the LTF-CHoCH context, the dedicated LTF-CHoCH contract applies.

## 6. Entry composition

Countertrend scenarios do not introduce new entry mechanics.

Eligible execution remains limited to the canonical entry-layer mechanisms:

- IDM Sweep;
- Decisional POI Mitigation;
- Engineering Liquidity Sweep;
- Extreme POI Mitigation.

The scenario determines **why and where the countertrend opportunity exists**. The entry module determines **how execution is authorized**.

## 7. Target composition

Countertrend target resolution is delegated to the canonical target-policy contract.

The scenario may identify the next canonical destination, but the exact target coordinate must come from the applicable target policy. No countertrend scenario may invent an arbitrary TP coordinate.

## 8. Invariants

```text
COUNTERTREND SCENARIO ≠ NEW STRUCTURAL REGIME ENUM

PRE-IDM OF/OB ≠ TRADABLE POI

IDM_TAKEN ≠ AUTOMATIC COUNTERTREND ENTRY

POI_FAILURE ≠ AUTOMATIC CHoCH

LTF INTERNAL STRUCTURE ≠ HTF BIAS CHANGE

LTF CHoCH CONTEXT ≠ NEW LIFECYCLE STATE

SCENARIO ≠ ENTRY MODULE

SCENARIO ≠ BROKER ORDER TYPE
```
