# EXECUTION

**Role:** Trading/execution-layer rules built on validated structural facts.

**Boundary:** Execution consumes structure; execution must never manufacture structural truth.

## 36. POI ontology — canonical tradable POIs

The canonical POI ontology is a closed set. A tradable Point of Interest may be either **Valid Order Flow (OF)** or **Valid Order Block (OB)**. No third POI entity may be introduced by generic SMC convention or implementation convenience.

```text
VALID ORDER FLOW (OF)
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

### Rule of Two

For a canonical dealing range, there may be one or two tradable POIs:

```text
DECISIONAL POI
      +
EXTREME POI
```

Everything outside the active one-or-two-POI structure is non-tradable/SMT unless a canonical rule explicitly promotes it. Multiple arbitrary POIs must not be created merely because multiple zones are visually present.

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
POI ∈ {VALID_OF, VALID_OB}
STANDALONE_FVG → NOT_POI
IDM → NOT_POI
LIQUIDITY → NOT_POI
POI → NOT_STRUCTURE
POI → NOT_BOS
POI → NOT_CHoCH
POI → NOT_AUTOMATIC_ENTRY
FVG → OB_VALIDATOR_ONLY
```

Representative linter violations:

```text
register_poi(fvg)              → ERR-POI-FVG-01
price_enters_fvg → entry       → ERR-EXEC-FVG-01
price.breaks_fvg → BOS         → ERR-STRUCT-FVG-01
register_poi(idm)               → ERR-POI-IDM-01
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

The Extreme POI must still be a Valid OF or Valid OB. It is not an arbitrary fallback to any visually convenient zone.

### Origin OB

An Origin OB is a canonical absolute range-origin Order Block. It is not required to disappear merely because its parent Valid Order Flow has been mitigated. Its validity must be evaluated according to the OB validation rules rather than by inheritance from the current OF state.

## 38. Order Block validation

A candle/zone may be treated as a Valid Order Block only when the canonical three-pillar validation is satisfied.

```text
PILLAR 1
Origin of impulsive displacement that causes structural BOS
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

### Valid Order Flow

Valid OF is a canonical POI class distinct from OB. OF and OB must not be conflated into a single generic zone type merely for implementation convenience.

### OB mitigation

Mitigation changes execution eligibility; it does not rewrite historical structural meaning. A mitigated OF does not automatically invalidate a separately valid Origin OB. A failed Decisional POI does not authorize arbitrary zone substitution; the canonical Extreme POI must be used when its own validity conditions are satisfied.

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

The IDM Sweep module requires a canonically active IDM and its qualifying liquidity interaction. IDM sweep remains a liquidity/execution event and is not itself BOS or CHoCH.

### Module 2 — Decisional POI Mitigation

The Decisional POI must be a valid OF or OB, must satisfy the directional premium/discount gate, and must meet the independent execution conditions of the module. POI mitigation does not create structural validity.

### Module 3 — Engineering Liquidity Sweep

Engineering liquidity is an execution-layer liquidity event. It must not be promoted to structural liquidity, IDM, BOS, or CHoCH merely because price sweeps the engineered level.

### Module 4 — Extreme POI Mitigation

The Extreme POI module is the canonical fallback execution mechanism when the Decisional POI is not the applicable execution location. The Extreme POI must independently satisfy OF/OB validity; fallback execution does not relax POI validation.

## 41. Execution, structural validation, and risk

Execution priority and structural validation are separate domains.

```text
EXECUTION PRIORITY ≠ STRUCTURAL VALIDATION
ORDER FLOW FAILED ≠ BOS
ORDER FLOW FAILED ≠ CHoCH
POI FAILURE ≠ STRUCTURAL FAILURE
```

A failed execution condition must not be converted into a structural event. Likewise, a structurally valid event does not automatically authorize execution.

### Order Flow failure / Extreme fallback

Do not fail over from Valid OF to Extreme OB solely because price wicked into or through the OF. The exact failure condition must be independently satisfied by the canonical execution module. A wick touch alone is insufficient to invent an execution-state transition.

### Risk and RR

A canonical executable setup must satisfy a minimum risk/reward of **1:2**. The primary target is the confirmed external range extreme where the applicable entry module requires it. Risk management must consume structural state; it must not redefine structure.
