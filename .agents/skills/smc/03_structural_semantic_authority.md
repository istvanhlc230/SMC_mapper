# TRUE SMC — STRUCTURAL SEMANTIC AUTHORITY

**Role:** Canonical Layer 3 Structural Lifecycle authority for Major Structure, Genesis, Confirmed Swing / Protected Structural Extreme, BOS, and CHoCH.

**Authority:** This document owns the high-level Structural Lifecycle, Sections 3.1–3.5. Detailed BOS mechanics are maintained in `04_BOS_mechanics.md`. Detailed CHoCH mechanics are maintained in `05_CHOCH_mechanics.md`. Those modules are subordinate to this document and do not create competing lifecycle authorities.

## Structural semantic authority invariant

This document is the owner of Major / External Structure. Its structural namespace is distinct from Layer-1 Microstructure and Layer-2 Minor Structure.

Canonical Layer-3 objects include:
- CONFIRMED_STRUCTURAL_SWING;
- Protected External Boundary / Protected Structural Extreme;
- MAJOR_IDM;
- structural retracement qualification.

A Minor Structural Swing, candle-level Extreme, or generic local Swing is not automatically a Layer-3 structural object. Layer 3 promotes only through its explicit canonical lifecycle and qualification gates.



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
PULLBACK-DERIVED LIQUIDITY REFERENCE
  ↓
IDM GOVERNANCE / ACTIVE IDM HANDOFF
  ↓
IDM LIQUIDITY TAKEOUT
  ↓
CONFIRMED_STRUCTURAL_SWING
  ↓
STRUCTURAL RETRACEMENT QUALIFICATION FOR BOS
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

A governing Trading Range does not exist merely because an impulse has occurred. The lifecycle first requires IDM takeout to establish the relevant swing-point candidate. Structural retracement qualification then promotes that candidate to a `CONFIRMED_STRUCTURAL_SWING`, which is subsequently tested for continuation BOS. The confirmed swing object and the validity of the eventual BOS are distinct semantic decisions; IDM takeout does not by itself create `VALID_BOS`, `PROTECTED_STRUCTURAL_EXTREME`, or roll the Trading Range.

### 3.2.1 — Genesis / Bootstrap

Prior to the first confirmed IDM sweep, including chart inception or the initial active impulse following a valid CHoCH_CONFIRMED, the market resides in an unconfirmed expansion state such as `BOOTSTRAP_EXPANSION`.

In bootstrap:

- candle-level minor structures may form;
- candidate IDM structures may form;
- no governing dealing range is fabricated;
- no CONFIRMED_STRUCTURAL_SWING is manufactured without the required confirmation lifecycle.

Bootstrap must remain distinguishable from organically confirmed structure.

### 3.2.1A — Canonical Bootstrap Initialization for the First BOS

The indexed source corpus does not provide a deterministic first-BOS retracement baseline. This is a genuine source gap. The project resolves that gap with an isolated **Bootstrap Initialization** process whose sole purpose is to provide a deterministic measurement anchor for first-BOS qualification without fabricating ordinary Major / External Structure.

### Mapping-origin axiom

The mapper is a chronological causal engine. On an initial boot of a mapping domain, the first eligible completed candle is `C0` and is the **mapping-origin candle**.

`C0` is not an arbitrary placeholder. It is the first causal reference of the mapping state machine. Every subsequent eligible candle is processed strictly forward from `C0`, bar-by-bar; higher-layer state cannot be manufactured before its lower-layer evidence exists.

For the mapping domain, `C0` is therefore the initial impulse-origin reference. This means the mapped structure is causally constructed from `C0`; it does not mean that the financial market itself began at `C0` or that candles outside the mapping domain did not exist.

A later incremental invocation does not redefine `C0`; it resumes from persisted canonical state and continues the same chronology.

### Bootstrap Reversal — Dedicated Local Initialization Transition

A **Bootstrap Reversal** is a project-canonical local initialization transition used only while the mapping is still in bootstrap and no canonical Dealing Range / Protected Structural Extreme exists.

The physical trigger is:

```text
BOOTSTRAP state
    +
price physically penetrates BOOTSTRAP_ORIGIN_ANCHOR
    (Wick OR Body)
    ↓
BOOTSTRAP_ANCHOR_BREAK
    ↓
BOOTSTRAP_REVERSAL
```

This event is **not** an external structural break. It must never be emitted as `VALID_BOS`, `CHoCH_CONFIRMED`, `MAJOR_IDM_SWEEP`, or `PROTECTED_STRUCTURAL_EXTREME` creation.

The transition is deterministic:

1. Record `BOOTSTRAP_ANCHOR_BREAK` as an immutable historical local event.
2. Terminate the pre-reversal bootstrap lineage at the event time. Any pre-reversal `SWING_CANDIDATE`, provisional extreme, active IDM, or transient bootstrap measurement state is retired from the active lineage and is not retroactively promoted.
3. Reverse the active mapping direction.
4. The actual reversal/break candle becomes the `EXPLICIT_ACTIVE_IMPULSE_ORIGIN` for the new bootstrap lineage; its provenance records `BOOTSTRAP_REVERSAL` as the reason for the new origin.
5. Re-derive `BOOTSTRAP_ORIGIN_ANCHOR` from that actual reversal candle using the new direction: bullish → reversal-candle `LOW`; bearish → reversal-candle `HIGH`.
6. The reversal candle remains part of the same immutable chronological history and serves as the new Layer-1 active reference. Subsequent eligible candles are processed strictly forward from it; the mapper never rewinds to `C0` and never fabricates a synthetic candle.
7. Begin a fresh Layer-1 → Layer-2 construction for the new active direction. The new lineage must independently form `CANDLE_LEVEL_VALID_PULLBACK → VERIFIED_PULLBACK_EXTREME → MINOR_IDM` before any new IDM takeout can create a new swing candidate.

The original `C0` remains the mapping-origin of the overall mapping domain. Bootstrap reversal changes the **active lineage**, not the historical origin or chronology.

This transition is intentionally outside the normal BOS/CHoCH pipelines:

```text
BOOTSTRAP_ANCHOR_BREAK
        ↓
BOOTSTRAP_REVERSAL
        ↓
NEW ACTIVE BOOTSTRAP LINEAGE
        ↓
LAYER 1 → LAYER 2
        ↓
MINOR IDM
        ↓
NEW IDM_TAKEN
        ↓
NEW SWING CANDIDATE
        ↓
...
```

A bootstrap-origin break therefore never receives structural significance merely because it reverses the initial mapping direction. Structural BOS/CHoCH classification becomes available only after their independent canonical prerequisites exist.
### Bootstrap authority boundary

The bootstrap policy is explicitly **project-canonical**, not source-direct:

- The source corpus supports retracement measurement against an already identified trading/dealing range.
- The source corpus supports tracking the lowest/highest point reached by the active retracement as it progresses.
- The source corpus does **not** define how the first such measurement range is initialized before the first `VALID_BOS`.
- Therefore `BOOTSTRAP_ORIGIN_ANCHOR` is a temporary process object for initialization measurement, not a source-defined Protected Structural Extreme.

The canonical process is:

1. **Bootstrap origin anchoring**
   - On initial mapping boot, `BOOTSTRAP_ORIGIN_ANCHOR` is derived directly from `C0`.
   - Bullish mapping → `C0.LOW`; bearish mapping → `C0.HIGH`.
   - After `CHoCH_CONFIRMED`, the new active impulse must provide an explicit origin candle; missing origin provenance fails closed.
   - Provenance is represented as either `CHART_INCEPTION_ANCHOR` or `EXPLICIT_ACTIVE_IMPULSE_ORIGIN`.
   - The bootstrap anchor is an initialization reference only; it is not a `PROTECTED_STRUCTURAL_EXTREME`, Trading Range boundary, or CHoCH boundary.

2. **Layer-1 / Layer-2 causal construction**
   - After `C0`, eligible candles are processed chronologically, one candle at a time.
   - The engine cannot promote a higher-layer object before the required lower-layer evidence exists.
   - Inside bars do not become a special structural reference under the canonical Layer-1 / Layer-2 rules.
   - The canonical valid-pullback sequence remains reference break → reference breach → continuation → `CANDLE_LEVEL_VALID_PULLBACK`.

3. **IDM_TAKEN → swing-point candidate**
   - The most recently formed valid-pullback extreme supplies the active `MINOR_IDM` under Layer 2.
   - Physical takeout of that active IDM produces `IDM_TAKEN = TRUE`.
   - `IDM_TAKEN` promotes the preceding expansion extreme to `SWING_CANDIDATE` / `PROVISIONAL_STRUCTURAL_EXTREME`.
   - This candidate is the swing-point reference that the following retracement will qualify. The source material commonly calls the takeout an acquisition/confirmation of a swing point; the project state machine retains an explicit provisional stage until macro qualification makes it BOS-eligible.
   - `IDM_TAKEN` does not create a Protected Structural Extreme and does not create a canonical Dealing Range.

4. **Bootstrap measurement range for candidate qualification**
   - As soon as the swing candidate exists, the transient `BOOTSTRAP_RANGE` is formed between `BOOTSTRAP_ORIGIN_ANCHOR` and the candidate structural extreme.
   - This step is required **before** macro retracement qualification because the candidate-to-anchor span is the first-BOS measurement baseline supplied to the existing Layer-3 qualification logic.
   - `BOOTSTRAP_RANGE` is measurement-only. It is not a governing Dealing Range, Trading Range boundary, Protected Structural Extreme, or CHoCH boundary.
   - Its activation provenance is the `SWING_CANDIDATE` establishment event. The candidate's source candle remains separately traceable as object provenance.

5. **Dynamic retracement + macro qualification**
   - From the candidate stage onward, the active retracement is processed chronologically and its corrective extreme is tracked dynamically.
   - Bullish → lowest relevant completed-candle LOW reached by the retracement.
   - Bearish → highest relevant completed-candle HIGH reached by the retracement.
   - Retracement qualification uses the existing Layer-3 rules: standard 50% equilibrium path, or the documented 38.2% conditional HTF-valid-pullback path, with the existing candle/displacement gates.
   - When macro qualification succeeds, the `SWING_CANDIDATE` / `PROVISIONAL_STRUCTURAL_EXTREME` is promoted to `CONFIRMED_STRUCTURAL_SWING`.
   - Qualification does not freeze `dynamic_retracement_extreme`; the corrective extreme remains mutable until the physical structural break.

6. **Strict pre-BOS observation boundary**
   - The `VALID_BOS` lock candidate is the `dynamic_retracement_extreme` that exists immediately before the structural break.
   - Under aggregate completed-candle OHLC, the break/BOS candle is excluded from the pre-BOS corrective-extreme calculation.
   - Final OHLC does not prove whether a same-candle opposite wick occurred before or after the structural break.
   - Independent intrabar sequence evidence may be recorded separately, but cannot be fabricated from candle color or final OHLC.

7. **VALID_BOS → Protected Structural Extreme → Dealing Range**
   - A continuation break is `VALID_BOS` only when the canonical gates pass: `IDM_TAKEN + MAJOR_RETRACEMENT_QUALIFIED + STRUCTURAL_SWING_BREAK`.
   - The break can only be a BOS reference after `CONFIRMED_STRUCTURAL_SWING` exists.
   - At the physical break event, lock the current pre-break `dynamic_retracement_extreme` as `PROTECTED_STRUCTURAL_EXTREME`.
   - Preserve the actual retracement source-candle provenance of that locked extreme.
   - Destroy the transient bootstrap objects.
   - Establish the new canonical Dealing Range only after the Protected Structural Extreme lock.

8. **Insufficient continuation / extension**
   - A structural break attempt before macro qualification is not `VALID_BOS`.
   - Classify it through the canonical `IMPULSE_EXTENSION` path.
   - The newer valid pullback/extreme may replace the candidate/reference according to the existing forward-only lifecycle.
   - No Protected Structural Extreme lock and no Dealing Range rollover occur.

Canonical causal chain:

```text
C0 / MAPPING-ORIGIN CANDLE
        ↓
LAYER 1 REFERENCE LIFECYCLE
        ↓
CANDLE_LEVEL_VALID_PULLBACK
        ↓
VERIFIED_PULLBACK_EXTREME
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
lock pre-break dynamic_retracement_extreme
        ↓
PROTECTED_STRUCTURAL_EXTREME
        ↓
NEW CONFIRMED DEALING RANGE
```

**Non-contamination invariants:**

```text
C0 = FIRST ELIGIBLE CANDLE OF INITIAL MAPPING DOMAIN
C0 → CAUSAL START OF STATE MACHINE

IDM_TAKEN ≠ PROTECTED_STRUCTURAL_EXTREME
SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME ≠ CONFIRMED_STRUCTURAL_SWING
BOOTSTRAP_ORIGIN_ANCHOR ≠ PROTECTED_STRUCTURAL_EXTREME
BOOTSTRAP_RANGE ≠ GOVERNING_DEALING_RANGE
BOOTSTRAP_RANGE ACTIVATION = SWING_CANDIDATE ESTABLISHMENT
QUALIFICATION_TIME ≠ dynamic_retracement_extreme LOCK TIME
BREAK_CANDLE ∉ PRE-BOS RETRACEMENT EXTREME WINDOW
VALID_BOS = STRUCTURAL LOCK POINT
```
### 3.2.2 — Impulse Origin vs Protected Structural Extreme

An impulse origin is the physical price/time anchor where an expansion began. It does not automatically constitute a Protected Structural Extreme.

A Protected Structural Extreme is a later Major / External structural state created and locked through valid BOS.

```text
QUALIFIED IDM
    ↓
IDM SWEEP (Wick or Body: IDM_TAKEN = TRUE)
    ↓
SWING_CANDIDATE / PROVISIONAL_STRUCTURAL_EXTREME
    ↓
STRUCTURAL RETRACEMENT QUALIFICATION FOR BOS
    ↓
CONFIRMED_STRUCTURAL_SWING
    ├─ QUALIFIED
    │      ↓
    │  STRUCTURAL_SWING_BREAK (Wick or Body)
    │      ↓
    │   VALID_BOS
    │
    └─ INSUFFICIENT AT ATTEMPTED BREAK
           ↓
    REFERENCE SHIFT / SWING REPLACEMENT
    (Range remains unexpanded)
           ↓
    CONTINUE CURRENT LIFECYCLE
    (No Protected Structural Extreme Lock,
     No Trading Range Rollover)
```

---

## 3.2.3 — Inducement Semantic Authority

Layer 3 is the semantic owner of Major IDM governance and the cross-layer IDM takeout / external structural lifecycle. Layer 2 is the semantic owner of Minor IDM formation from the active valid pullback. Layer 3 consumes the Layer-2 Minor IDM and determines the governing Major IDM role and downstream structural consequences. Layer 3 does not redefine or recreate the Layer-2 Minor IDM definition.

For a bullish active impulsive leg, inducement is the liquidity resting below the low of the most recently formed valid pullback relevant to that leg. For a bearish active impulsive leg, inducement is the liquidity resting above the high of the most recently formed valid pullback.

### IDM Provenance and Composition

The IDM lifecycle architecture distinguishes source-backed methodology from the project's internal execution representation.

**Source-backed semantics:**
- The most recently formed valid pullback supplies the ordinary IDM liquidity reference.
- A newer valid pullback supersedes the previous active IDM reference.
- Minor IDM is the internal inducement role.
- Major IDM is the governing major-liquidity reference.
- After BOS, a newly formed **Layer-2 Candle-Level Valid Pullback** establishes the new Major IDM from its verified pullback extreme. The qualification is the combination of the post-BOS lifecycle context and the already-defined Layer-2 valid-pullback / verified-extreme states; Layer 3 does not invent a second candle-count, depth, or heuristic test for Major IDM.
- If a range contains only a Minor IDM and no newly formed Major IDM, the governing external boundary/liquidity — the prior protected low in a bullish range or prior protected high in a bearish range — serves as the Major IDM.

**Project-canonical / Composed representation:**
- Historical IDM objects are immutable once formed.
- The active IDM is represented via an active-pointer reference.
- Major IDM provenance may therefore be either pullback-derived or governing-external-boundary-derived.
- The detailed post-CHoCH dual-lineage state model is a composed tracking architecture.

These project-composed tracking mechanisms must not be rewritten as direct knowledgebase quotations, but they remain canonical for this implementation.

~~~text
LAYER 2
VERIFIED PULLBACK EXTREME
        ↓
PULLBACK-DERIVED LIQUIDITY REFERENCE
        ↓
MINOR_IDM
        ↓
LAYER 3
IDM_TAKEN / MAJOR_IDM GOVERNANCE
~~~

### Minor vs Major IDM

Major/Minor classification is determined by structural role: a pre-BOS active valid pullback supplies the Layer-2 Minor IDM, while a validated **post-`VALID_BOS` Layer-2 Candle-Level Valid Pullback → Verified Pullback Extreme** establishes the new Layer-3 Major IDM.

```text
INTERNAL / PRE-BOS VALID PULLBACK
        ↓
MINOR_IDM

VALID_BOS
        ↓
POST-BOS LAYER-2 VALID PULLBACK
        ↓
VERIFIED PULLBACK EXTREME
        ↓
MAJOR_IDM becomes active

If no new post-BOS valid pullback / verified extreme exists:
        ↓
PRIOR PROTECTED EXTERNAL BOUNDARY
        ↓
REMAINS MAJOR IDM
```

In a bullish range, the protected external boundary is the prior protected low; in a bearish range it is the prior protected high. The associated external liquidity serves as the governing Major IDM reference while no newer Major IDM has been established.

A newly formed valid pullback immediately supersedes the Layer-2 active Minor IDM / pullback-derived reference under Layer-2 ownership. **After `VALID_BOS`, that validated post-BOS pullback is the Major IDM qualification event** and its verified pullback extreme becomes the active Layer-3 Major IDM reference. Historical IDM objects remain immutable.

### Major IDM lifecycle

After a valid BOS, a **Layer-2 Candle-Level Valid Pullback → Verified Pullback Extreme** in the new lifecycle establishes the new Major IDM from that verified pullback extreme. No additional Major-IDM threshold is applied at Layer 3.

If the post-BOS price action has not yet produced a new Layer-2 valid pullback / verified pullback extreme, the previous protected external boundary remains the active Major IDM reference. No separate fallback IDM object or ontology is created.

```text
VALID_BOS
    ↓
NEW STRUCTURAL LIFECYCLE
    ↓
POST-BOS PRICE ACTION
    ├─ NEW MAJOR IDM QUALIFIED
    │      ↓
    │   NEW MAJOR IDM becomes active
    │
    └─ MINOR IDM ONLY
           ↓
    PREVIOUS PROTECTED EXTERNAL BOUNDARY
           ↓
       REMAINS MAJOR IDM
```

### Canonical Inducement Ontology

1. **Minor IDM ownership:** Layer 2 owns formation and active-pointer lifecycle of the Minor IDM derived from the active valid pullback.
2. **Layer 3 IDM lifecycle:** Layer 3 consumes Minor IDM evidence for IDM_TAKEN and owns Major IDM governance and external structural consequences.
3. **Major IDM:** governing major-liquidity reference. It is established from a validated post-`VALID_BOS` Layer-2 Candle-Level Valid Pullback → Verified Pullback Extreme, or, when no new post-BOS valid pullback has yet established one, from the prior protected external boundary/liquidity.
4. A newer valid pullback may shift the Layer-2 Minor IDM pointer under Layer-2 ownership; after `VALID_BOS`, the active Layer-3 Major IDM reference changes when the new pullback reaches the already-defined Layer-2 Valid Pullback → Verified Pullback Extreme state.
5. There is no separate legacy/proxy Major IDM ontology class; Major IDM remains one semantic class with traceable provenance.
6. Historical IDM objects remain immutable; active-pointer changes are forward-only and event-time provenance is preserved.

### IDM takeout

IDM_TAKEN = TRUE when price physically takes the active IDM reference according to the applicable directional level. Wick or body penetration is sufficient for IDM takeout; a candle close beyond IDM is not required.

IDM takeout is the structural lifecycle event that confirms the relevant swing point. It does not by itself create VALID_BOS, roll the Trading Range, or lock the Protected Structural Extreme.

~~~text
ACTIVE IDM
    ↓
PHYSICAL IDM TAKEOUT
    ↓
IDM_TAKEN = TRUE
    ↓
CONFIRMED_STRUCTURAL_SWING
    ↓
STRUCTURAL_RETRACEMENT_EVALUATION
~~~

This section owns the IDM semantic object and lifecycle. BOS and CHoCH modules consume the resulting IDM state and takeout status; they must not redefine IDM.

---

## 3.3 — Confirmed Swing & Protected Structural Extreme Lifecycle

### Structural Lifecycle State Machine

The confirmation of a structural swing point and the qualification of the later continuation BOS are separate sequential decisions. The 2026 market-structure source treats IDM takeout as the event that confirms the swing point; retracement depth and candle structure then determine whether a later break of that swing can qualify as a valid BOS.

1. **IDM_TAKEN:** Price physically takes the active IDM reference supplied by the applicable upstream IDM lifecycle. The reference may be the Layer-2 pullback-derived Minor IDM or the Layer-3 governed Major IDM.

2. **CONFIRMED_STRUCTURAL_SWING:** The external extreme associated with the taken IDM is confirmed as the structural swing point for the active lifecycle.

3. **STRUCTURAL_RETRACEMENT_QUALIFICATION:** The subsequent retracement is evaluated for continuation-BOS sufficiency.

   - **If QUALIFIED:**
     - `MAJOR_RETRACEMENT_QUALIFIED = TRUE`.
     - The existing `CONFIRMED_STRUCTURAL_SWING` remains the eligible continuation-BOS reference.
     - The engine awaits `STRUCTURAL_SWING_BREAK`.

   - **If an attempted external break occurs before retracement qualification succeeds:**
     - the break is not `VALID_BOS`;
     - the shallow retracement extreme becomes the newer active pullback/reference;
     - the prior swing is no longer the current eligible BOS reference for that failed continuation attempt;
     - the active IDM/pullback reference shifts accordingly.

This preserves the source distinction between swing confirmation after IDM takeout and later BOS qualification after sufficient retracement.

### Impulsive-leg structural scope

Structural qualification, IDM-derived mapping, and POI-relevant structural context are evaluated on the active **impulsive leg**. Internal complexity that belongs only to the corrective leg is not promoted into separate structural candidates.

### Reduced-candle displacement outlier exception

The normal reduced-candle gate must not reject a source-defined one-candle displacement outlier. A **single exceptional displacement candle** may constitute the complete qualifying retracement / structural leg when it takes the bodies or extremes of **at least 5 preceding candles** and reaches the otherwise applicable structural retracement requirement.

This is an explicit exception to the normal candle-count gate, not a general one-candle qualification rule:

```text
NORMAL PATH
>= 3 opposing closing candles
        ↓
qualification gates

REDUCED-CANDLE EXCEPTION
2 opposing candles
        ↓
documented displacement / extreme-taking conditions
        ↓
qualification gates

OUTLIER EXCEPTION
1 exceptional displacement candle
        ↓
takes >= 5 preceding bodies/extremes
        ↓
required retracement depth / structural conditions
        ↓
qualification may proceed
```

The one-candle outlier must independently satisfy all other applicable structural prerequisites. Candle count alone never establishes qualification.

### Major Retracement Qualification Architecture

Layer 3 is the sole semantic owner of structural qualification. A retracement wave is evaluated through the following hierarchical gates:

#### Gate 1: Equilibrium Retracement (Standard Path)

- **Condition:** `RetracementDepth >= STANDARD_EQUILIBRIUM_THRESHOLD` of the active dealing range, where `STANDARD_EQUILIBRIUM_THRESHOLD` is owned by `methodology_parameters.md`.
- **Structural Validation:**
  - **Normal Case:** Requires `>= NORMAL_RETRACEMENT_CANDLE_COUNT` opposing closing candles within the retracement leg. With the canonical parameter value `NORMAL_RETRACEMENT_CANDLE_COUNT = 3`, the normal path therefore requires at least **3 opposing closing candles**.
  - **Reduced-Candle Displacement Exception:** A reduced-candle retracement may qualify through the rare source-described displacement case. The documented exception includes the explicit one-candle displacement outlier: one candle may qualify when it takes `>= MIN_OUTLIER_EXTREMES_TAKEN` preceding bodies/extremes and reaches the required retracement depth. A two-candle reduced retracement may qualify under the same source-supported displacement/extreme-taking conditions. This exception does not make a short candle sequence automatically valid.
- **Output:** `MAJOR_RETRACEMENT_QUALIFIED = TRUE`.

#### Gate 2: HTF-Represented Retracement (Conditional Path)

- **Condition:** `HTF_CONDITIONAL_THRESHOLD <= RetracementDepth < STANDARD_EQUILIBRIUM_THRESHOLD` of the active dealing range. `HTF_CONDITIONAL_THRESHOLD` and `STANDARD_EQUILIBRIUM_THRESHOLD` are owned by `methodology_parameters.md`.
- **HTF Evidence Gate:**
  - Depth between 38.2% and 49.9% is **never sufficient on its own**.
  - It is qualified **if and only if** the entire retracement move constitutes a single valid pullback event on the applicable immediate Higher Timeframe (`HTF_VALID_PULLBACK == TRUE`).
  - **Axiom:** “A higher timeframe valid pullback is a lower timeframe complete structure.”
  - If the HTF displays an inside bar or an invalid pullback: `MAJOR_RETRACEMENT_QUALIFIED = FALSE`.

#### Gate 3: Insufficient Retracement

- **Condition:** `RetracementDepth < HTF_CONDITIONAL_THRESHOLD`.
- **Output:** `MAJOR_RETRACEMENT_QUALIFIED = FALSE`.

The gates are hierarchical and mutually exclusive by depth. Gate 2 is the only qualification path below 50%; Gate 3 cannot qualify. Qualification is evaluated before the structural swing break and is stored for downstream Layer 4 consumption.
### 3.3.3 — Protected Structural Extreme Lock

The absolute corrective extreme remains dynamically tracked until the structural event that produces `VALID_BOS`.

```text
RETRACEMENT QUALIFICATION
        ↓
dynamic_retracement_extreme
        ↓
PRE-BREAK STRUCTURAL SWING BREAK
        ↓
VALID_BOS
        ↓
PROTECTED_STRUCTURAL_EXTREME_LOCK
```

For bullish structure, `dynamic_retracement_extreme` is the lowest relevant completed-candle LOW observed during the active retracement. For bearish structure, it is the highest relevant completed-candle HIGH.

Qualification does not freeze the state. A later valid retracement candle may replace the current corrective extreme until the physical structural break.

The lock value is the dynamic extreme that exists **immediately before the structural break**. Under the aggregate completed-candle OHLC contract:

```text
BREAK_CANDLE ∉ PRE-BOS RETRACEMENT EXTREME WINDOW
```

The break candle may provide the physical wick/body break, but aggregate OHLC does not establish the intrabar ordering of that break and the candle's opposite extreme. The break candle therefore cannot retroactively redefine the pre-break corrective state.

A valid wick BOS locks the current pre-break `dynamic_retracement_extreme` immediately. No later body close is required.

If the penetrated external level carries Major IDM provenance, the wick event is instead `MAJOR_IDM_SWEEP`; it is not BOS and does not lock `dynamic_retracement_extreme`.

Detailed BOS locking mechanics are owned by `04_BOS_mechanics.md`. The full structural ontology and bootstrap origin policy remain owned by this document.

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

Post-BOS retracement, internal liquidity collection, Major IDM updates, and subsequent displacement belong to the new lifecycle. A later event must not be interpreted as delayed acceptance of the preceding BOS.

POI expiration is handled through the separate POI lifecycle; the structural engine must not silently delete POI history.

---


## Canonical Layer 3 Invariants

1. Layer 3 consumes validated Layer 1 and Layer 2 prerequisites; it does not redefine them.
2. Major Structure is governed by the active Trading Range and canonical external boundaries.
3. Minor Structure, IDM, arbitrary liquidity, and local extrema do not independently redefine Major Structure.
4. CONFIRMED_STRUCTURAL_SWING and Protected Structural Extreme are distinct lifecycle states.
5. Protected Structural Extreme is created by valid BOS, not by impulse origin or arbitrary swing confirmation.
6. Retracement sufficiency is mandatory before continuation BOS.
7. A normal retracement must contain **at least 3 opposing closing candles** to enter the standard positive qualification path. A **2-candle retracement** is eligible only through the documented reduced-candle displacement exception, and a **1-candle displacement outlier is an explicit additional exception** when it takes `>= MIN_OUTLIER_EXTREMES_TAKEN` preceding bodies/extremes and all other canonical conditions pass.
8. The standard equilibrium retracement threshold is 50%; the 38.2% threshold is conditional and may qualify only through the applicable immediate Higher Timeframe valid-pullback path.
9. IDM takeout confirms the relevant `CONFIRMED_STRUCTURAL_SWING`. Retracement qualification determines whether a subsequent external break can be classified as `VALID_BOS`; it does not retrospectively create the swing point.
10. Physical external break does not automatically equal VALID_BOS or CHoCH_CONFIRMED.
11. `MAJOR_IDM_SWEEP` is not VALID_BOS and not CHoCH_CONFIRMED.
12. Major IDM may be pullback-derived or the prior protected external boundary when only Minor IDM exists; it is never arbitrary internal liquidity.
13. A Major IDM takeout may confirm the corresponding swing reference, but it does not by itself create VALID_BOS, Trading Range rollover, or Protected Structural Extreme lock.
14. `NEW_SVP` does not automatically create Major IDM.
15. Only `VALID_BOS` rolls the Trading Range and locks the Protected Structural Extreme.
16. `CHoCH_CONFIRMED` initializes a new regime but does not itself create a new CONFIRMED_STRUCTURAL_SWING or VALID_BOS.
17. First post-CHoCH SVP and first post-CHoCH Minor IDM are distinct lifecycle states.
18. Structural event classification is anti-retroactive.
19. Detailed BOS mechanics are owned by `04_BOS_mechanics.md`.
20. Detailed CHoCH mechanics are owned by `05_CHOCH_mechanics.md`.
21. This document remains the single high-level Layer 3 Structural Lifecycle authority.