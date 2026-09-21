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
LIQUIDITY
  ↓
IDM ELIGIBILITY
  ↓
ACTIVE / MINOR IDM
  ↓
IDM LIQUIDITY TAKEOUT
  ↓
SWING CONFIRMATION GATE
  ↓
CONFIRMED_STRUCTURAL_SWING
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

A governing Trading Range does not exist merely because an impulse has occurred. It becomes formally established only when a qualified IDM liquidity takeout unlocks the SWING_CONFIRMATION_GATE **and the subsequent canonical confirmation prerequisites establish a CONFIRMED_STRUCTURAL_SWING**. A liquidity sweep alone never establishes the range.

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
SWING_CONFIRMATION_GATE UNLOCKED
    ↓
CONFIRMED_STRUCTURAL_SWING (Swing confirmed ONLY; not BOS, not CHoCH, no range rollover)
    ↓
CONSUME STORED MAJOR-RETRACEMENT QUALIFICATION
    ├─ NOT QUALIFIED → Break of Swing is IMPULSE_EXTENSION (Range remains open)
    └─ QUALIFIED
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
SWING CONFIRMATION GATE
~~~

This section owns the IDM semantic object and lifecycle. BOS and CHoCH modules consume the resulting IDM state and takeout status; they must not redefine IDM.

---

## 3.3 — Confirmed Swing & Protected Structural Extreme Lifecycle

### 3.3.1 — Ontological Asymmetry

```text
CONFIRMED_STRUCTURAL_SWING
        ≠
PROTECTED STRUCTURAL EXTREME
```

A provisional Expansion Extreme becomes a **CONFIRMED_STRUCTURAL_SWING** when and only when the active IDM is taken out (`IDM_TAKEN = TRUE`). Wick or body penetration of the IDM level exclusively opens the `SWING_CONFIRMATION_GATE` and is sufficient to trigger IDM takeout; a candle body close beyond IDM is NOT required.

A CONFIRMED_STRUCTURAL_SWING records the current expansion extreme and serves as the external structural landmark for the active lifecycle. It is not automatically protected.

Crucially:
- IDM takeout confirms the swing ONLY.
- IDM takeout does NOT create a new Dealing Range.
- IDM takeout does NOT flip trend.
- IDM takeout is NEVER a CHoCH.
- IDM takeout does NOT create VALID_BOS.
- IDM takeout does NOT roll the dealing range.
- `CONFIRMED_STRUCTURAL_SWING ≠ VALID_BOS`. Having a CONFIRMED_STRUCTURAL_SWING is a necessary prerequisite for BOS, NOT BOS itself.

A **Protected Structural Extreme** is a later lifecycle state created by valid BOS. It becomes the governing trend anchor for the resulting structural lifecycle.

### 3.3.2 — Major Structural Retracement Qualification

This section is the single semantic owner of the major structural qualification rule. Other documents may consume or reference the result but must not redefine the criteria.

The corrective extreme is tracked dynamically across the complete corrective window from swing confirmation until BOS. This section is the canonical semantic owner of **major structural retracement qualification**. Layer 2 produces the candle-level Valid Pullback and verified pullback extreme; Layer 3 determines whether that retracement is structurally qualified.

Bullish lifecycle:

```text
E_retrace(t) = min(Low_k)
```

Bearish lifecycle:

```text
E_retrace(t) = max(High_k)
```

The tracked extreme must not be frozen prematurely at a local pivot, IDM-sweeping candle, or internal microstructure point.

**Opposing Candle Definition**

An "opposing candle" is defined strictly by candle direction / body direction relative to the active trend / dominant impulse:
- In a bullish trend (dominant upward impulse): an opposing candle is a bearish candle (`Close < Open`).
- In a bearish trend (dominant downward impulse): an opposing candle is a bullish candle (`Close > Open`).

Do NOT define opposing candles by displacement, directional movement, higher/lower extremes, or candle ranges. Candle color / body direction is the definitive criterion.

**Mandatory Macro BOS Retracement Gate (38.2%)**

The 38.2% retracement threshold is anchored strictly to the active Major Structure Dealing Range:
- **Bullish trend**: Dealing range from Protected Swing Low ($ProtectedLow$, impulse origin) to provisional Expansion High ($ExpansionHigh$, CONFIRMED_STRUCTURAL_SWING):
  $$\text{Retracement depth } R = \frac{ExpansionHigh - RetracementLow}{ExpansionHigh - ProtectedLow}$$
  $$\text{Threshold level } P_{38.2} = ExpansionHigh - 0.382 \times (ExpansionHigh - ProtectedLow)$$
  $$\text{Condition: } RetracementLow \le P_{38.2} \iff R \ge 0.382$$
- **Bearish trend**: Dealing range from Protected Swing High ($ProtectedHigh$, impulse origin) to provisional Expansion Low ($ExpansionLow$, CONFIRMED_STRUCTURAL_SWING):
  $$\text{Retracement depth } R = \frac{RetracementHigh - ExpansionLow}{ProtectedHigh - ExpansionLow}$$
  $$\text{Threshold level } P_{38.2} = ExpansionLow + 0.382 \times (ProtectedHigh - ExpansionLow)$$
  $$\text{Condition: } RetracementHigh \ge P_{38.2} \iff R \ge 0.382$$

Retracement depth $\ge 38.2\%$ is a **MANDATORY** gate for macro BOS. Without $\ge 38.2\%$ depth ($R \ge 0.382$), NO break of the expansion extreme can be classified as `VALID_BOS`.

**Standard qualification path**

```text
>= 3 OPPOSING CANDLES
AND
RETRACEMENT DEPTH >= 38.2% (R >= 0.382)
```

The canonical minimum retracement depth is **38.2%**. A retracement reaching 50% is a deeper instance of the same qualified depth condition; this document does not define a separate 50% pass/fail gate.

**Reduced-candle displacement exception**

The source material also recognizes rare retracements that contain fewer than three opposing candles when the retracement candles are exceptionally large and represent significant displacement. A source-backed displacement-outlier qualification may be used when:

1. the retracement depth reaches the canonical 38.2% minimum; and
2. the displacement retracement takes at least five previous candle extremes in the retracement direction.

A single exceptionally large retracement candle can satisfy the displacement-outlier condition when it independently meets these source-backed criteria. The exception is a structural qualification path, not a Layer 2 pullback rule.

**Higher-timeframe structural qualification**

A Higher-Timeframe Valid Pullback may correspond to a complete lower-timeframe structure. This is a hierarchy relationship used by the structural qualification process: a validated HTF pullback can be represented by its lower-timeframe completed structure when the applicable multi-timeframe context is in force.

HTF representation does not redefine the Layer 2 Candle-Level Valid Pullback and does not remove the mandatory macro retracement-depth gate for continuation BOS.

**Qualification integrity**

No heuristic or configuration mode may substitute for the canonical retracement-depth requirement. The displacement-outlier condition is evaluated only through the source-backed exceptional path above.

**CONFIRMED_STRUCTURAL_SWING → VALID_BOS qualification:**
VALID_BOS requires ALL of:
1. `IDM_TAKEN = TRUE` (swing confirmation prerequisite satisfied)
2. `MAJOR_RETRACEMENT_QUALIFIED = TRUE` (the canonical Layer 3 qualification defined above is satisfied)
3. `STRUCTURAL_SWING_BREAK` (wick breach or body close beyond CONFIRMED_STRUCTURAL_SWING)

If IDM is taken out (`IDM_TAKEN = TRUE`), the provisional expansion extreme becomes a CONFIRMED_STRUCTURAL_SWING. However, if MAJOR_RETRACEMENT_QUALIFIED is false:
- The swing remains confirmed.
- Macro retracement qualification is not satisfied.
- Any subsequent break of the CONFIRMED_STRUCTURAL_SWING is classified as IMPULSE_EXTENSION, not VALID_BOS.
- The dealing range remains OPEN (does not roll over).
- No new Protected Structural Extreme is established.

The detailed BOS break-classification mechanics are owned by `04_BOS_mechanics.md`. That module consumes the structural qualification defined here and must not redefine its semantic criteria.

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
7. One candle alone does not establish retracement validity; a reduced-candle retracement may qualify only when the canonical depth and source-supported displacement/extreme-taking conditions are satisfied.
8. Canonical default retracement depth is 38.2%.
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