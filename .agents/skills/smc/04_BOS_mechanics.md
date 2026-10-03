# TRUE SMC — BOS MECHANICS

**Role:** Detailed Section 3.4 BOS mechanics module under the canonical Layer 3 Structural Lifecycle authority.

**Authority:** `03_structural_semantic_authority.md` remains the Layer 3 lifecycle authority. This document owns the detailed mechanics of Section 3.4 only. It is subordinate to Layer 3 and must not create a competing structural-lifecycle category.

## 3.4 — Break of Structure (BOS) Mechanics

### Structural namespace boundary

Layer 4 consumes Major/External structural qualification from Layer 3. Therefore:
- STRUCTURAL_SWING_BREAK is a break of the Layer-3-confirmed structural swing/reference; it is not a generic candle break.
- VALID_BOS is the fully qualified external/major structural break.
- A Minor Structural Swing break, Candle Extreme Breach, liquidity sweep, or IDM takeout is not automatically BOS.
- Layer 4 must consume the canonical CONFIRMED_STRUCTURAL_SWING and Layer-3 retracement qualification rather than introducing a generic `Swing` or `Break` type.

The word “break” may appear in descriptive mechanics, but normative predicates use the specific canonical break object/event.



BOS is a Major / External structural continuation event. It is not a local candle pattern, arbitrary liquidity takeout, IDM sweep, or internal structural break.

### Canonical BOS Lifecycle

```text
PHYSICAL EXTERNAL BREAK (Wick OR Body)
        ↓
STRUCTURAL_SWING_BREAK
        ↓
CONSUME STORED MAJOR-RETRACEMENT QUALIFICATION FROM LAYER 3
        ↓
COMPLETE BOS GATE SATISFIED
        ↓
VALID_BOS
        ↓
PROTECTED_STRUCTURAL_EXTREME_LOCK + TRADING_RANGE_ROLLOVER
```

### 3.4.1 — BOS Reference Identity

`BOOTSTRAP_ORIGIN_ANCHOR` and a bootstrap anchor break are never continuation-BOS references. While the mapper is still in bootstrap, an anchor penetration is routed to `BOOTSTRAP_ANCHOR_BREAK → BOOTSTRAP_REVERSAL` and is not evaluated by the BOS pipeline.


The only legitimate continuation-BOS reference object is an eligible **CONFIRMED_STRUCTURAL_SWING** of the active lifecycle:

- bullish lifecycle → Confirmed Swing High;
- bearish lifecycle → Confirmed Swing Low.

The following are not continuation-BOS references:

- Minor Structure;
- provisional swings;
- IDM;
- liquidity pools;
- arbitrary local highs/lows;
- Protected Opposing Extremes.

If no eligible confirmed external swing exists, BOS evaluation is blocked.

```text
CONFIRMED_STRUCTURAL_SWING
        ↓
Eligible BOS Reference
```

### 3.4.2 — Physical External Break

A Physical External Break occurs when price physically penetrates the governing external level of an eligible CONFIRMED_STRUCTURAL_SWING.

Bullish:

```text
High_t > Confirmed_Swing_High
```

Bearish:

```text
Low_t < Confirmed_Swing_Low
```

The penetration may occur through wick/shadow or candle body. Both physical wick breach and physical body close beyond `CONFIRMED_STRUCTURAL_SWING` satisfy `STRUCTURAL_SWING_BREAK`; merely touching/equaling the reference level does not.

A physical external break does **not** itself establish `VALID_BOS`, Trading Range rollover, or Protected Structural Extreme locking. It opens the break-classification path.

Mandatory prerequisites remain:

1. Layer 3 has produced a qualified major-retracement result;
2. `IDM_TAKEN == True` (the Layer 3 IDM-takeout prerequisite is established);
3. the reference has correct external structural identity;
4. the final break classification satisfies 3.4.3.

For an eligible continuation external level that is not functioning as Major IDM, if the break occurs before the Layer 3 qualification result is satisfied or before `IDM_TAKEN == True`:

```text
EXT_CONT_BREAK
+
RETRACEMENT_SUFFICIENCY = NOT_SATISFIED (or IDM_TAKEN == False)
        ↓
IMPULSE_EXTENSION
```

No `VALID_BOS` is created and the current structural lifecycle remains active (no rollover, no protected extreme lock).

### 3.4.3 — Qualification Phase vs Execution Phase

The structural lifecycle explicitly separates the temporal **Qualification Phase** from the **Execution Phase**.

#### 1. Qualification Phase

Qualification occurs *before* price returns to the BOS level. Layer 3 dynamically evaluates the major retracement and structural qualification using its canonical semantic owner rules.

```text
IDM_TAKEN
→ SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME
→ APPLICABLE RETRACEMENT BASELINE
→ LAYER 3 RETRACEMENT / STRUCTURAL QUALIFICATION
→ CONFIRMED_STRUCTURAL_SWING
→ STORED QUALIFICATION RESULT
```

The canonical qualification rules are defined once in 03_structural_semantic_authority.md. This module consumes the stored result and does not reproduce the opposing-candle, displacement-outlier, higher-timeframe, or retracement-depth rules.

The qualification result (`is_bos_qualified`) is stored state. It is **not** a new BOS predicate. It is strictly the result of the preceding qualification phase.

#### 2. Execution Phase

Execution occurs when price later returns to the structural level. The engine does *not* recompute the opposing-candle qualification from scratch at the physical break moment. It evaluates the already established stored qualification.

```text
price returns to structural level
→ PHYSICAL_EXTERNAL_BREAK (Wick OR Body)
→ STRUCTURAL_SWING_BREAK
→ CONSUME STORED LAYER 3 QUALIFICATION
→
    ├── COMPLETE BOS GATE SATISFIED → VALID_BOS → PROTECTED_STRUCTURAL_EXTREME_LOCK + TRADING_RANGE_ROLLOVER
    └── DISQUALIFIED → IMPULSE_EXTENSION
```

Only `VALID_BOS` triggers Protected Structural Extreme Lock and Trading Range Rollover.

### 3.4.4 — Canonical Break Classification

`EXT_CONT_BREAK` exclusively represents a confirmed continuation swing break. Major IDM is a liquidity reference and is not a continuation-BOS reference.

The validated continuation pipeline is:

```text
EXT_CONT_BREAK
        ↓
STORED LAYER 3 QUALIFICATION
        ├── NOT QUALIFIED
        │       ↓
        │  IMPULSE_EXTENSION (Dealing range remains open)
        │
        └── QUALIFIED
                ↓
           VALID_BOS (Dealing range rolls over, Protected Structural Extreme locks)
```


### 3.4.4.1 — CONFIRMED_STRUCTURAL_SWING ≠ VALID_BOS

IDM takeout (`IDM_TAKEN = TRUE`) establishes the relevant swing-point candidate / provisional structural extreme. The later Layer 3 macro retracement qualification promotes that candidate to `CONFIRMED_STRUCTURAL_SWING`, after which a subsequent structural break can qualify as `VALID_BOS`. `CONFIRMED_STRUCTURAL_SWING` is a prerequisite for BOS, not BOS itself.

`VALID_BOS` requires ALL of:
1. `IDM_TAKEN = TRUE` (the Layer 3 swing-confirmation prerequisite is satisfied by wick or body takeout)
2. `MAJOR_RETRACEMENT_QUALIFIED = TRUE` (Layer 3 stored qualification result)
3. `STRUCTURAL_SWING_BREAK` (physical wick breach or body close beyond CONFIRMED_STRUCTURAL_SWING)

If IDM is taken out but Layer 3 has not yet produced `MAJOR_RETRACEMENT_QUALIFIED`:
- The IDM takeout leaves the external swing as `SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME` until Layer 3 completes macro retracement qualification.
- The later external break cannot be `VALID_BOS` until `CONFIRMED_STRUCTURAL_SWING` and the stored retracement qualification both exist.
- If an attempted break occurs on an insufficient retracement, the break is classified as `IMPULSE_EXTENSION` and the dealing range remains unexpanded. Layer 4 does not mutate or manufacture the upstream pullback/IDM reference; the Layer-2/Layer-3 lifecycle handles any subsequent reference shift according to its canonical ownership rules.

Therefore:

```text
EXT_CONT_BREAK ≠ VALID_BOS
MAJOR_IDM_SWEEP ≠ VALID_BOS
```

The classification is based on structural role and provenance, not geometry alone.

### 3.4.5 — Structural BOS Validation Gate

Layer 4 is the mechanical consumer of Layer 3 authority. Layer 4 does not perform Fibonacci depth calculations, candle counting, displacement evaluation, or HTF pullback verification.

A Break of Structure (BOS) is confirmed **if and only if** all three of the following predicates are satisfied simultaneously:

```text
VALID_BOS <=> (IDM_TAKEN == TRUE)
          AND (MAJOR_RETRACEMENT_QUALIFIED == TRUE)
          AND (STRUCTURAL_SWING_BREAK == TRUE)
```

Where:

- `IDM_TAKEN`: supplied exclusively by Layer 3.
- `MAJOR_RETRACEMENT_QUALIFIED`: supplied exclusively by Layer 3 and represents either the standard 50% equilibrium qualification path or the conditional 38.2%–<50% HTF-represented qualification path.
- `STRUCTURAL_SWING_BREAK`: evaluated by Layer 4 geometry when price breaks the `CONFIRMED_STRUCTURAL_SWING` level via wick or body, provided the level is not functioning as a Major Inducement.
- The Layer 3 qualification result is established before the continuation break is consumed; Layer 4 must not manufacture a confirmed swing or recompute qualification during break execution.

Layer 4 consumes these upstream outputs. It does not know or independently evaluate:

- 38.2% or 50% retracement depth;
- opposing-candle count;
- displacement-outlier thresholds;
- HTF pullback validity.

Those criteria are owned exclusively by Layer 3.
### 3.4.7 — Major IDM interaction

Major IDM is a liquidity reference, not a continuation-BOS reference. If the tested external level carries Major IDM provenance, a wick takeout is classified as `MAJOR_IDM_SWEEP`, not as a continuation BOS.

```text
MAJOR_IDM
+
WICK BREACH
    ↓
MAJOR_IDM_SWEEP
```

The sweep:
- is not `VALID_BOS`;
- does not roll the Trading Range;
- does not lock the Protected Structural Extreme;
- **does satisfy `IDM_TAKEN` when the active Major IDM reference is physically penetrated**;
- **the resulting `IDM_TAKEN` establishes the associated swing-point candidate / provisional structural extreme; macro retracement qualification is required before `CONFIRMED_STRUCTURAL_SWING` is established**;
- does not promote the swing candidate to `CONFIRMED_STRUCTURAL_SWING` until the applicable macro retracement qualification succeeds. That qualification is then the stored prerequisite for continuation `VALID_BOS`.

Major IDM remains a single canonical IDM class. It may be pullback-derived or the prior protected external boundary when only Minor IDM exists.
### 3.4.8 — Protected Structural Extreme Lock

The corrective extreme remains dynamic until `VALID_BOS`.

For the active retracement:

```text
BULLISH
→ dynamic_retracement_extreme = lowest relevant LOW observed so far

BEARISH
→ dynamic_retracement_extreme = highest relevant HIGH observed so far
```

The lock is point-in-time:

```text
CONFIRMED_STRUCTURAL_SWING
        ↓
completed retracement candles
        ↓
dynamic_retracement_extreme
        ↓
STRUCTURAL SWING BREAK
        ↓
VALID_BOS
        ↓
LOCK CURRENT PRE-BREAK EXTREME
        ↓
PROTECTED STRUCTURAL EXTREME
```

The break/BOS candle itself is excluded from the pre-BOS corrective-extreme window under the aggregate OHLC contract. A wick may establish the physical break, but final OHLC does not establish the intrabar ordering of that break versus the candle's opposite extreme. The break candle therefore must not retroactively redefine the corrective state that existed immediately before the break.

No later body close is required after a valid wick BOS.

A `MAJOR_IDM_SWEEP` does not lock the extreme because it is not a continuation `VALID_BOS`.

This module does not redefine the full `CONFIRMED_STRUCTURAL_SWING` / Protected Structural Extreme lifecycle; ownership remains in `03_structural_semantic_authority.md` Section 3.3 and the bootstrap lifecycle in Section 3.2.1A.
### 3.4.9 — Trading Range Rollover

Only `VALID_BOS` closes the previous governing Trading Range and starts the next structural lifecycle.

```text
VALID_BOS
   ↓
PREVIOUS RANGE CLOSED
   ↓
PROTECTED_STRUCTURAL_EXTREME_LOCK + TRADING_RANGE_ROLLOVER
   ↓
NEW RANGE ACTIVE
```

The following do not independently roll the range:

- physical external break;
- wick penetration;
- Minor IDM sweep;
- Major IDM sweep;
- insufficient-retracement impulse extension.

Post-BOS retracement and liquidity collection belong to the new range lifecycle.

### 3.4.10 — Post-BOS Major IDM continuity

After `VALID_BOS`, the new structural lifecycle consumes Layer-2 valid-pullback state directly.

```text
VALID_BOS
    ↓
NEW STRUCTURAL LIFECYCLE
    ↓
POST-BOS LAYER-2 VALID PULLBACK
    ↓
VERIFIED PULLBACK EXTREME
    ↓
MAJOR IDM ACTIVE
```

Every completed post-BOS Layer-2 Candle-Level Valid Pullback → Verified Pullback Extreme establishes a Major IDM event. The newest such event is the active Major IDM; earlier Major IDM events remain historical and immutable.

If no post-BOS valid pullback / verified pullback extreme exists, the prior protected low in a bullish range, or prior protected high in a bearish range, remains the Major IDM reference.

`NEW_SVP` does not itself equal `MAJOR_IDM`; the Layer-2 valid-pullback / verified-extreme state is the qualification chain.

### 3.4.11 — POI Lifecycle Boundary

BOS closes a Trading Range, but the structural engine does not directly delete POIs.

```text
VALID_BOS
    ↓
TRADING_RANGE_ROLLED_OVER
    ↓
POI LIFECYCLE SUBSYSTEM
```

Historical POI expiration is owned by the separate POI lifecycle/execution semantics. Structural BOS methodology must not silently redefine POI registry behavior.

### 3.4.12 — Anti-Retroactive and Exclusivity Invariants

```text
MAJOR_IDM_SWEEP
≠ VALID_BOS
```

```text
IMPULSE_EXTENSION
≠ VALID_BOS
```

```text
MAJOR_IDM_SWEEP
≠ CHoCH_CONFIRMED
```

```text
A past event classification is immutable.
```

If `t1` is classified as `MAJOR_IDM_SWEEP`, later candles cannot rewrite `t1` as BOS. Each event is evaluated against the structural state and provenance active at its own event time.

### 3.4.13 — BOS State-Transition Contract

`EXT_CONT_BREAK` applies exclusively to continuation boundaries.

```text
EXT_CONT_BREAK
        ↓
evaluate stored qualification
        ├── DISQUALIFIED → IMPULSE_EXTENSION (current lifecycle remains active)
        └── QUALIFIED    → VALID_BOS (POST_BOS / new range lifecycle)
```

The transition outcome is deterministic once event identity, retracement qualification, and level provenance are known.

### 3.4.14 — BOS / CHoCH Boundary

BOS and CHoCH are mutually exclusive structural outcomes for the same evaluated external event.

```text
CONTINUATION EXTERNAL BREAK
        ↓
BOS PIPELINE (VALID_BOS)

OPPOSING EXTERNAL BREAK
        ↓
CHoCH PIPELINE (CHoCH_CONFIRMED)
```

A MAJOR_IDM event can produce `MAJOR_IDM_SWEEP`; it cannot be simultaneously classified as `VALID_BOS` or `CHoCH_CONFIRMED`. A bootstrap anchor break is outside both structural pipelines and is classified only as `BOOTSTRAP_REVERSAL` while the mapping remains in bootstrap.

### 3.4.15 — Canonical Authority Hierarchy (MC-01)

For the canonical True SMC implementation, the implementation-level structural specification governs where it provides a more specific rule than earlier generic pedagogical formulations.

Therefore:
* earlier body-close-only BOS pedagogy is NOT a universal implementation rule;
* implementation-level Wick-BOS defines the valid STRUCTURAL_SWING_BREAK mechanism, while the complete VALID_BOS event still requires all canonical Major / External BOS gates;
* continuation external wick-BOS is canonical for establishing the break;
* wick interpretation is structural-context dependent.

## Canonical BOS Invariants

1. BOS requires an eligible CONFIRMED_STRUCTURAL_SWING reference.
2. Physical break does not equal `VALID_BOS`.
3. Retracement sufficiency is a prerequisite to continuation BOS.
4. Major retracement qualification is produced by Layer 3 and consumed here as stored state.
5. Layer 3 owns the canonical retracement qualification thresholds: 50% standard equilibrium and the conditional 38.2%–<50% HTF-represented path.
6. Reduced-candle displacement and higher-timeframe qualification are evaluated by Layer 3 and are not redefined here.
7. Wick-BOS is immediate once price physically penetrates beyond the reference; equality at the level alone is not a break.
8. Major IDM is the single canonical Major IDM semantic class; provenance does not create a separate Major IDM ontology.
9. MAJOR_IDM wick breach is `MAJOR_IDM_SWEEP`, not VALID_BOS or CHoCH_CONFIRMED.
10. `MAJOR_IDM_SWEEP` satisfies `IDM_TAKEN`; the Layer 3 owner therefore establishes the associated swing-point candidate / provisional structural extreme. Macro retracement qualification is still required before `CONFIRMED_STRUCTURAL_SWING` is established. The event does not by itself create `VALID_BOS`, roll the Trading Range, or lock the Protected Structural Extreme.
11. `NEW_SVP` does not automatically create Major IDM.
12. A new Major IDM supersedes the active Major IDM when the post-BOS Layer-2 **Candle-Level Valid Pullback → Verified Pullback Extreme** state is reached and consumed by Layer 3 as the Major IDM qualification event.
13. Only `VALID_BOS` rolls the Trading Range and locks the Protected Structural Extreme.
14. BOS event classification is anti-retroactive.
15. BOS mechanics are subordinate to `03_structural_semantic_authority.md` and must not create a competing Layer 3 authority.