# TRUE SMC — STRUCTURAL SEMANTIC AUTHORITY

**Role:** Canonical Layer 3 Structural Lifecycle authority for Major Structure, Genesis, Confirmed Swing / Protected Structural Extreme, BOS, and CHoCH.

**Authority:** This document owns the high-level Structural Lifecycle, Sections 3.1–3.5. Detailed BOS mechanics are maintained in `04_BOS_mechanics.md`. Detailed CHoCH mechanics are maintained in `05_CHOCH_mechanics.md`. Those modules are subordinate to this document and do not create competing lifecycle authorities.

## Structural semantic authority invariant

This document is the shared Layer 3 semantic authority consumed by the dedicated BOS and CHoCH mechanics modules. It owns Major Structure ontology, structural qualification, swing/protection lifecycle, and shared invariants; it does not duplicate event-specific BOS or CHoCH mechanics.

Higher-level structural events may consume lower-level validated state, but no stage may be skipped or manufactured by configuration, scoring, visualization, or implementation convenience.

```text
RAW OHLC
  ↓
CANDLE RELATIONSHIPS
  ↓
MINOR STRUCTURE
  ↓
CANDLE-LEVEL VALID PULLBACK
  ↓
VERIFIED PULLBACK EXTREME
  ↓
STRUCTURAL RETRACEMENT QUALIFICATION
  ↓
STRUCTURALLY VALID PULLBACK
  ↓
PULLBACK-DERIVED LIQUIDITY REFERENCE
  ↓
IDM DEFINITION / CLASSIFICATION
  ↓
ACTIVE IDM
  ↓
IDM LIQUIDITY TAKEOUT
  ↓
SWING_CANDIDATE
  ↓
STRUCTURAL RETRACEMENT EVALUATION
  ├── QUALIFIED → CONFIRMED_STRUCTURAL_SWING
  └── NOT QUALIFIED → SWING_REVOKED + PULLBACK_REFERENCE_SHIFT
  ↓
PHYSICAL EXTERNAL BREAK
  ↓
BREAK CLASSIFICATION
  ↓
VALID_BOS / CHoCH_CONFIRMED
```

Layer 1 and Layer 2 semantic foundations are owned by:

- `01_micro_structure.md`
- `02_minor_structure.md`

The Structural Lifecycle begins once those validated prerequisites are available and owns the external structural state machine from Major Structure through CHoCH and post-regime initialization.

---

## 3.1 — Major Structure: Definition & Scope

Major Structure is the governing external structural framework defined strictly by the active Trading Range and its canonical external boundaries.

The governing range boundaries are derived from canonical external structural events and confirmed swing context. Internal Minor Structure, arbitrary local highs/lows, liquidity nodes, or IDM events cannot independently redefine the governing Trading Range.

A CONFIRMED_STRUCTURAL_SWING does not automatically become a Trading Range Boundary. A Protected Structural Extreme is a distinct structural state established through the canonical swing and break lifecycle.

```text
Major Structure
    ↓
Governing Trading Range
    ↓
External Structural Boundaries

Minor Structure / IDM / Internal Liquidity
    ≠
Governing Range Boundary
```

### Mandatory identity separation

```text
CONFIRMED_STRUCTURAL_SWING
≠ TRADING RANGE BOUNDARY

PROTECTED STRUCTURAL EXTREME
≠ ARBITRARY CONFIRMED_STRUCTURAL_SWING

MINOR STRUCTURE
≠ MAJOR STRUCTURE

IDM
≠ MAJOR STRUCTURE
```

---

## 3.2 — Genesis & Structural Unit of Origin

The unit of origin for Major Structure is not an isolated candlestick, fractal pivot, or raw price extreme. Major Structure originates from the complete **Confirmed Dealing Range Cycle**, anchored by liquidity-validated structural extremes.

A governing Trading Range does not exist merely because an impulse has occurred. The lifecycle must first progress from IDM takeout to a SWING_CANDIDATE and then through canonical structural retracement qualification to establish a CONFIRMED_STRUCTURAL_SWING. The confirmation gate is a process condition within that lifecycle; an IDM liquidity takeout alone never establishes the range.

### 3.2.1 — Genesis / Bootstrap

Prior to the first confirmed IDM sweep, including chart inception or the initial active impulse following a valid CHoCH_CONFIRMED, the market resides in an unconfirmed expansion state such as `BOOTSTRAP_EXPANSION`.

In bootstrap:

- candle-level minor structures may form;
- candidate IDM structures may form;
- no governing dealing range is fabricated;
- no CONFIRMED_STRUCTURAL_SWING is manufactured without the required confirmation lifecycle.

Bootstrap must remain distinguishable from organically confirmed structure.

### 3.2.2 — Impulse Origin vs Protected Structural Extreme

An impulse origin is the physical price/time anchor where an expansion began. It does not automatically constitute a Protected Structural Extreme.

A Protected Structural Extreme is a later macro-state created and locked through valid BOS.

```text
QUALIFIED IDM
    ↓
IDM SWEEP (Wick or Body: IDM_TAKEN = TRUE)
    ↓
SWING_CANDIDATE
    ↓
STRUCTURAL RETRACEMENT EVALUATION
    ├─ NOT QUALIFIED → SWING_REVOKED + PULLBACK_REFERENCE_SHIFT
    │                   (Range remains unexpanded)
    └─ QUALIFIED
            ↓
       CONFIRMED_STRUCTURAL_SWING
            ↓
       STRUCTURAL_SWING_BREAK (Wick or Body)
            ↓
        VALID_BOS
            ↓
PROTECTED_STRUCTURAL_EXTREME_LOCK + TRADING_RANGE_ROLLOVER
```

---

## 3.2.3 — Inducement Semantic Authority

Layer 3 is the single semantic owner of Inducement (IDM). Layer 2 supplies the validated pullback and pullback-derived liquidity reference; Layer 3 determines whether that reference constitutes IDM and which IDM class is active.

For a bullish active impulsive leg, inducement is the liquidity resting below the low of the most recently formed valid pullback relevant to that leg. For a bearish active impulsive leg, inducement is the liquidity resting above the high of the most recently formed valid pullback.

### IDM Provenance and Composition

The IDM lifecycle architecture distinguishes source-backed methodology from the project's internal execution representation.

**Source-backed semantics:**
- The most recent valid pullback supplies IDM liquidity.
- A newer valid pullback shifts the IDM reference.
- Minor IDM occurs before BOS.
- Major IDM occurs after BOS.

**Project-canonical / Composed representation:**
- Historical IDM objects are immutable once formed.
- The active IDM is represented via an active-pointer reference.
- The `FALLBACK_MAJOR_IDM` lifecycle proxy is a deterministic structural engine state.
- The detailed post-CHoCH dual-lineage state model is a composed tracking architecture.

These project-composed tracking mechanisms must not be rewritten as direct knowledgebase quotations, but they remain canonical for this implementation.

~~~text
LAYER 2
VERIFIED PULLBACK EXTREME
        ↓
PULLBACK-DERIVED LIQUIDITY REFERENCE
        ↓
LAYER 3
IDM CLASSIFICATION
~~~

### Minor vs Major IDM

The IDM class is determined by the structural lifecycle:

~~~text
BEFORE VALID BOS
        ↓
MINOR_IDM

AFTER VALID BOS
        ↓
MAJOR_IDM
~~~

The classification is structural, not a separate candle-pattern definition. A newly formed valid pullback can supersede the current IDM reference when the lifecycle rules identify that newer pullback as the active reference. Historical IDM objects remain part of structural history and are not retroactively rewritten.

### Real Major IDM and fallback proxy

After a valid BOS, the first independently qualified post-BOS Structurally Valid Pullback can establish the REAL_MAJOR_IDM from its verified pullback extreme. Until that real post-BOS IDM exists, the lifecycle may expose a FALLBACK_MAJOR_IDM as an opposing-boundary proxy.

~~~text
VALID_BOS
    ↓
NEW STRUCTURAL LIFECYCLE
    ↓
POST-BOS STRUCTURALLY VALID PULLBACK
    ↓
VERIFIED PULLBACK EXTREME
    ↓
REAL_MAJOR_IDM
    ↓
FALLBACK_MAJOR_IDM → SUPERSEDED
~~~

### Canonical Inducement Ontology & Lifecycle Proxy

1. **Single Semantic Definition:** Inducement (IDM) is defined solely as the liquidity resting beyond the extreme of the most recently formed valid pullback.
   - `MINOR_IDM`: A valid pullback formed prior to structural BOS.
   - `REAL_MAJOR_IDM`: A validated pullback formed after structural BOS.

2. **Structural Engine Lifecycle Proxy:** `FALLBACK_MAJOR_IDM` is **NOT** an alternative or secondary IDM definition. It is strictly a temporary lifecycle proxy state used by the structural engine to maintain dealing range bounds following a BOS until a verified post-BOS `REAL_MAJOR_IDM` is printed by price action. Once a valid pullback forms on the new impulsive leg, `FALLBACK_MAJOR_IDM` is immediately superseded.
FALLBACK_MAJOR_IDM is a lifecycle proxy and is not the same semantic object as REAL_MAJOR_IDM.

### IDM takeout

IDM_TAKEN = TRUE when price physically takes the active IDM reference according to the applicable directional level. Wick or body penetration is sufficient for IDM takeout; a candle close beyond IDM is not required.

IDM takeout is a structural lifecycle event that can unlock the Swing Confirmation Gate. It does not by itself create VALID_BOS, roll the Trading Range, or lock the Protected Structural Extreme.

~~~text
ACTIVE IDM
    ↓
PHYSICAL IDM TAKEOUT
    ↓
IDM_TAKEN = TRUE
    ↓
SWING_CANDIDATE
    ↓
STRUCTURAL_RETRACEMENT_EVALUATION
~~~

This section owns the IDM semantic object and lifecycle. BOS and CHoCH modules consume the resulting IDM state and takeout status; they must not redefine IDM.

---

## 3.3 — Confirmed Swing & Protected Structural Extreme Lifecycle

### Structural Lifecycle State Machine

The confirmation of structural swings and the lifecycle of the dealing range strictly follow this sequential state machine:

1. **IDM_TAKEN:** Price sweeps or closes beyond the active Inducement (most recent valid pullback).

2. **SWING_CANDIDATE:** The external extreme of the dealing range is marked as a candidate structural swing point (Swing High in uptrends, Swing Low in downtrends).

3. **STRUCTURAL_RETRACEMENT_EVALUATION:** The market evaluates the depth, candle structure, and HTF representation of the retracement wave.

   - **If QUALIFIED:**
     - State transitions to `CONFIRMED_STRUCTURAL_SWING`.
     - Emits `MAJOR_RETRACEMENT_QUALIFIED = TRUE`.
     - Awaits `STRUCTURAL_SWING_BREAK` by price (downstream Layer 4 BOS).

   - **If NOT QUALIFIED (Shallow Retracement Failure):**
     - State transitions to `SWING_REVOKED`.
     - Emits `MAJOR_RETRACEMENT_QUALIFIED = FALSE`.
     - Dealing range remains unexpanded (single impulsive leg).
     - `PULLBACK_REFERENCE_SHIFT`: The extreme reached by the shallow retracement becomes the new active Inducement reference.
     - Awaits the next qualification attempt.

This separation is mandatory: `IDM_TAKEN` creates a `SWING_CANDIDATE`; it does not manufacture a `CONFIRMED_STRUCTURAL_SWING` before retracement qualification succeeds.
### Major Retracement Qualification Architecture

Layer 3 is the sole semantic owner of structural qualification. A retracement wave is evaluated through the following hierarchical gates:

#### Gate 1: Equilibrium Retracement (Standard Path)

- **Condition:** `RetracementDepth >= 50%` of the active dealing range.
- **Structural Validation:**
  - **Normal Case:** Requires `>= 3` opposing closing candles within the retracement leg.
  - **Reduced-Candle Displacement Exception:** If **exactly 2 opposing candles** form the retracement, qualification may occur only under the rare source-described displacement case: the reduced-candle retracement contains unusually large candle(s) that collectively take the bodies/extremes of `>= 5` preceding candles and produce the required retracement depth. The knowledgebase explicitly discusses a 2-candle case as potentially reasonable when these size/extreme-taking conditions are met. This exception does not make a short candle sequence automatically valid.
- **Output:** `MAJOR_RETRACEMENT_QUALIFIED = TRUE`.

#### Gate 2: HTF-Represented Retracement (Conditional Path)

- **Condition:** `38.2% <= RetracementDepth < 50%` of the active dealing range.
- **HTF Evidence Gate:**
  - Depth between 38.2% and 49.9% is **never sufficient on its own**.
  - It is qualified **if and only if** the entire retracement move constitutes a single valid pullback event on the applicable immediate Higher Timeframe (`HTF_VALID_PULLBACK == TRUE`).
  - **Axiom:** “A higher timeframe valid pullback is a lower timeframe complete structure.”
  - If the HTF displays an inside bar or an invalid pullback: `MAJOR_RETRACEMENT_QUALIFIED = FALSE`.

#### Gate 3: Insufficient Retracement

- **Condition:** `RetracementDepth < 38.2%`.
- **Output:** `MAJOR_RETRACEMENT_QUALIFIED = FALSE`.

The gates are hierarchical and mutually exclusive by depth. Gate 2 is the only qualification path below 50%; Gate 3 cannot qualify. Qualification is evaluated before the structural swing break and is stored for downstream Layer 4 consumption.
### 3.3.3 — Protected Structural Extreme Lock

The absolute corrective extreme remains dynamically tracked until the structural event that produces `VALID_BOS`.

```text
Retracement Sufficiency
        ↓
Dynamic E_retrace
        ↓
VALID_BOS
        ↓
PROTECTED_STRUCTURAL_EXTREME_LOCK (E_retrace LOCKED)
```

A valid wick BOS locks `E_retrace` immediately. No later body close is required.

If the penetrated external level is the FALLBACK_MAJOR_IDM, the wick event is instead `MAJOR_IDM_SWEEP`; it is not BOS and does not lock `E_retrace`.

Detailed BOS locking mechanics are owned by `04_BOS_mechanics.md`.

### 3.3.4 — Dealing Range Rollover & New Cycle

A valid BOS closes the previous governing Trading Range and starts a new structural lifecycle.

```text
VALID_BOS
   ↓
PREVIOUS RANGE CLOSED
   ↓
PROTECTED_STRUCTURAL_EXTREME_LOCK + TRADING_RANGE_ROLLOVER
   ↓
NEW RANGE ACTIVE
```

Post-BOS retracement, internal liquidity collection, fallback handling, and subsequent displacement belong to the new lifecycle. A later event must not be interpreted as delayed acceptance of the preceding BOS.

POI expiration is handled through the separate POI lifecycle; the structural engine must not silently delete POI history.

---


## Canonical Layer 3 Invariants

1. Layer 3 consumes validated Layer 1 and Layer 2 prerequisites; it does not redefine them.
2. Major Structure is governed by the active Trading Range and canonical external boundaries.
3. Minor Structure, IDM, arbitrary liquidity, and local extrema do not independently redefine Major Structure.
4. CONFIRMED_STRUCTURAL_SWING and Protected Structural Extreme are distinct lifecycle states.
5. Protected Structural Extreme is created by valid BOS, not by impulse origin or arbitrary swing confirmation.
6. Retracement sufficiency is mandatory before continuation BOS.
7. A retracement must contain **at least 2 opposing candles** to enter a positive qualification path. A **2-candle retracement** may qualify only when the canonical depth and source-supported displacement/extreme-taking conditions are satisfied; a 1-candle retracement does not qualify through the reduced-candle path.
8. The standard equilibrium retracement threshold is 50%; the 38.2% threshold is conditional and may qualify only through the applicable immediate Higher Timeframe valid-pullback path.
9. A `SWING_CANDIDATE` is not a `CONFIRMED_STRUCTURAL_SWING` until the canonical retracement qualification succeeds; failed shallow retracement revokes the candidate and shifts the active pullback/IDM reference.
10. Physical external break does not automatically equal VALID_BOS or CHoCH_CONFIRMED.
11. `MAJOR_IDM_SWEEP` is not VALID_BOS and not CHoCH_CONFIRMED.
12. Fallback Major IDM is an external range-boundary proxy, not Real Major IDM or arbitrary internal liquidity.
13. A fallback sweep unlocks the Swing Confirmation Gate but does not automatically create a CONFIRMED_STRUCTURAL_SWING.
14. `NEW_SVP` does not automatically create Real Major IDM.
15. Only `VALID_BOS` rolls the Trading Range and locks the Protected Structural Extreme.
16. `CHoCH_CONFIRMED` initializes a new regime but does not itself create a new CONFIRMED_STRUCTURAL_SWING or VALID_BOS.
17. First post-CHoCH SVP and first post-CHoCH Minor IDM are distinct lifecycle states.
18. Structural event classification is anti-retroactive.
19. Detailed BOS mechanics are owned by `04_BOS_mechanics.md`.
20. Detailed CHoCH mechanics are owned by `05_CHOCH_mechanics.md`.
21. This document remains the single high-level Layer 3 Structural Lifecycle authority.