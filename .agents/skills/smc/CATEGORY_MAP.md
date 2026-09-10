# TRUE SMC — METHODOLOGY CATEGORY MAP

**Status:** Classification layer for the reorganized True SMC skill
**Purpose:** Classify the existing rules without deleting, weakening, or silently changing any rule in the preserved baseline `skill_old.md`.

> This file is a taxonomy and audit ledger, not a replacement for the category documents. The category documents contain the migrated rule bodies; `skill_old.md` remains the immutable completeness baseline until final audit sign-off.

---

## 1. Category model

Every rule in the True SMC skill belongs to one primary authority category.

| Category | Meaning | Validation role |
|---|---|---|
| `STANDARD_SMC` | Broad SMC/ICT concept that is commonly recognized independently of this repository's implementation | Methodology baseline |
| `TRUE_SMC_CANONICAL` | Rule explicitly belonging to the project's canonical True SMC methodology | Highest methodology authority |
| `METHODOLOGY_PARAMETER` | Numeric/threshold/configurable parameter used by the methodology | Must not redefine object semantics |
| `IMPLEMENTATION` | Mapper/state-machine/data-model behavior required to implement the methodology | Code-contract layer |
| `EXECUTION` | Trading/execution interpretation built on top of structural facts | Must not redefine structure |
| `RISK` | Risk, position sizing, trade-management, or scoring policy | Separate from structural truth |
| `UNVERIFIED` | Rule or claim lacking sufficient provenance/verification to call it universal or canonical | Must not be promoted silently |
| `DEPRECATED` | Historical rule retained for traceability but no longer active | Must not drive validation |

### Authority rule

A rule being present in a category does **not** automatically make it a universal SMC rule. The category records what kind of authority the rule has.

Classification does not delete or weaken the underlying rule.

---

## 2. Core structural ontology

These concepts form the structural core and should remain independent of execution, scoring, or UI concerns.

| Concept | Primary category | Current interpretation |
|---|---|---|
| Raw OHLC | `STANDARD_SMC` | Primitive market data |
| Candle relationships | `STANDARD_SMC` | Price relationship primitives used to derive higher-level structure |
| Candle-level Minor Structure | `TRUE_SMC_CANONICAL` | Repository-specific structural precursor layer |
| Candle-level Valid Pullback | `TRUE_SMC_CANONICAL` | Formal multi-step pullback sequence defined by the canonical rules |
| Equal High / Equal Low reference handling | `TRUE_SMC_CANONICAL` | Deterministic reference-transfer behavior |
| Inside-bar handling | `TRUE_SMC_CANONICAL` | Inside bars do not independently create structural objects |
| Outside-bar directional sequencing | `TRUE_SMC_CANONICAL` | LOW → HIGH bullish and HIGH → LOW bearish sequencing |
| Verified Pullback Extreme | `TRUE_SMC_CANONICAL` | Pullback-derived candidate liquidity reference |
| Structural Retracement Qualification | `TRUE_SMC_CANONICAL` | Qualification layer between candle-level pullback and structural pullback |
| 3-opposing-candle rule | `TRUE_SMC_CANONICAL` | Current methodology rule; not to be presented as universal SMC without provenance |
| 38.2% default | `METHODOLOGY_PARAMETER` | Current canonical default threshold; numeric value is parameterized |
| Exactly-2-candle momentum exception | `TRUE_SMC_CANONICAL` | Current methodology exception |
| Large/high-momentum condition | `UNVERIFIED` | Qualitative in current skill until an authoritative quantitative definition exists |
| Structurally Valid Pullback | `TRUE_SMC_CANONICAL` | Structurally qualified pullback capable of becoming IDM source |
| BSL / SSL liquidity | `STANDARD_SMC` | Directional liquidity taxonomy |
| Active Pullback Pointer | `IMPLEMENTATION` | Single active reference required by the mapper state model |
| IDM | `TRUE_SMC_CANONICAL` | Liquidity derived from the most recent structurally valid pullback on the active impulsive leg |
| Minor / Active IDM lifecycle | `TRUE_SMC_CANONICAL` | Newest qualifying pullback replaces the active minor IDM |
| Major IDM | `TRUE_SMC_CANONICAL` | Separate lifecycle from Minor IDM |
| Real Major IDM | `TRUE_SMC_CANONICAL` | Post-BOS, structurally-valid-pullback-derived Major IDM |
| Fallback Major IDM | `TRUE_SMC_CANONICAL` | Distinct fallback inducement lifecycle |
| IDM sweep | `STANDARD_SMC` + `TRUE_SMC_CANONICAL` | Liquidity event; exact lifecycle semantics are project-specific |
| Swing candidate | `STANDARD_SMC` | Candidate structure before canonical confirmation |
| Swing confirmation / Range-Lock | `TRUE_SMC_CANONICAL` | Required IDM/liquidity sequence for structural confirmation |
| Confirmed Structural Swing | `TRUE_SMC_CANONICAL` | Confirmed range-side structural object |
| Protected / Strong Swing | `TRUE_SMC_CANONICAL` | Locked only by the required later BOS sequence |
| Physical Structural Break | `TRUE_SMC_CANONICAL` | Actual high/low breach of the governing reference |
| Break Acceptance | `TRUE_SMC_CANONICAL` | Acceptance test following the physical break |
| BOS | `STANDARD_SMC` + `TRUE_SMC_CANONICAL` | Standard concept with project-specific qualification semantics |
| CHoCH | `STANDARD_SMC` + `TRUE_SMC_CANONICAL` | Standard regime-transition concept with project-specific lifecycle |
| Trading Range | `TRUE_SMC_CANONICAL` | Governing structural regime object |
| Genesis / bootstrap | `TRUE_SMC_CANONICAL` + `IMPLEMENTATION` | Initialization constraints preventing fabricated historical structure |

---

## 3. Structural rule provenance

### 3.1 Broad SMC/ICT concepts

These are concepts that can be discussed as general SMC/ICT ideas, while the exact implementation remains project-specific:

- liquidity
- BSL / SSL
- swing highs / swing lows
- BOS
- CHoCH
- displacement
- Fair Value Gap / imbalance
- Order Block
- protected structural levels
- inducement as a structural/liquidity concept

The canonical category must define the project's exact semantics where those semantics differ from generic usage.

### 3.2 True SMC canonical rules

The following are project methodology rather than assumed universal SMC facts:

- the exact candle-level Valid Pullback sequence
- Equal High / Equal Low reference transfer
- strict inside-bar behavior
- outside-bar LOW → HIGH / HIGH → LOW sequencing
- the verified pullback extreme chain
- structural qualification requirements
- the >=3 opposing candle standard path
- the exactly-2-candle momentum exception
- the >=5 prior candle extremes condition in that exception
- the single active pullback pointer
- the exact IDM derivation from the most recent Structurally Valid Pullback
- Minor IDM replacement lifecycle
- Real Major IDM lifecycle
- Fallback Major IDM lifecycle
- asymmetric Range-Lock swing confirmation
- deep-retracement non-reset behavior
- the exact active-Major-IDM BOS gate
- the exact CHoCH → new impulsive-leg lifecycle
- genesis restrictions

Classification prevents these rules from being mislabeled as generic SMC axioms.

---

## 4. Parameter category

Numeric thresholds must be separated from semantic definitions.

### Current methodology parameters

- `38.2%` minimum retracement default
- any configurable minimum retracement value
- any implementation-configured candle-size/momentum threshold introduced later

### Parameter rule

A parameter may change a threshold, but must not change the identity of the object it qualifies.

For example:

```text
changing retracement threshold
        ≠
changing the definition of IDM
```

No new ATR, body-ratio, volatility, or standard-deviation threshold should be promoted to canonical methodology without independent verification.

---

## 5. Implementation category

These rules describe how the mapper must represent or transition canonical objects.

### Current implementation-facing concepts

- one active pullback pointer
- separate active, historical, Minor IDM, and Major IDM state
- object identity for the active Major IDM gate
- explicit state transition ordering
- no stage skipping in the hierarchy
- candidate vs confirmed state separation
- provisional vs protected swing state separation
- historical structure separated from current governing structure
- genesis/bootstrapping without manufactured historical events
- scoring/configuration cannot create structural truth

### Implementation invariant

```text
IMPLEMENTATION MUST FOLLOW METHODOLOGY
METHODOLOGY MUST NOT BE REDEFINED BY IMPLEMENTATION CONVENIENCE
```

---

## 6. Execution category

Execution concepts must consume structural facts rather than create them.

| Concept | Category | Boundary |
|---|---|---|
| POI | `EXECUTION` | Entry-location framework; not structural truth |
| Order Flow | `EXECUTION` | Context/confirmation layer; not equivalent to Order Block |
| Order Block | `EXECUTION` / `STANDARD_SMC` | Structural/trading concept whose exact qualification is methodology-specific |
| FVG / Imbalance | `EXECUTION` / `STANDARD_SMC` | Price-inefficiency concept; must not manufacture BOS/IDM |
| Entry model | `EXECUTION` | Consumes validated structural/POI objects |
| Entry execution | `EXECUTION` | Must remain separate from POI identification |

### Execution boundary

```text
STRUCTURE → LIQUIDITY → IDM → SWING → BOS/CHoCH
                         ↓
                       POI
                         ↓
                       ENTRY
```

Execution logic must never retroactively validate an invalid structural object.

---

## 7. Risk and scoring category

Risk and scoring are policy layers, not structural truth.

| Concept | Category | Rule |
|---|---|---|
| Risk management | `RISK` | Must not redefine structure |
| Position sizing | `RISK` | Must not validate/invalid structural objects |
| Trade score | `RISK` | Score is an output/policy, not a structural prerequisite |
| Scoring weights | `RISK` | Implementation/execution policy, not universal SMC |
| Configuration switches | `IMPLEMENTATION` / `RISK` | Cannot silently redefine canonical semantics |

Any scoring model must remain downstream of validated methodology.

---

## 8. BOS classification boundary

BOS is a special case because the concept is broadly recognized while the exact acceptance semantics are project-specific.

### General concept

`STANDARD_SMC`

A structural break in the direction of the active trend/regime.

### True SMC qualification

`TRUE_SMC_CANONICAL`

The canonical rules define prerequisites including:

- required structural context
- IDM liquidity takeout
- confirmed structural swing / range side
- physical break of the actual reference
- break acceptance
- active Major IDM gate

### Required distinction

The canonical model contains both:

- **External Wick BOS** for eligible external structural levels
- **Full Body-Close BOS** when the close exceeds the reference extreme

This distinction must remain visible. It must not be silently collapsed into a generic “body close required” rule or silently removed.

---

## 9. CHoCH classification boundary

### General concept

`STANDARD_SMC`

A regime/trend transition against the previously governing structural direction.

### True SMC lifecycle

`TRUE_SMC_CANONICAL`

The canonical model treats CHoCH as a separate lifecycle:

```text
CURRENT RANGE
  ↓
GOVERNING RANGE BOUNDARY VIOLATION
  ↓
CHoCH
  ↓
NEW TREND
  ↓
CHoCH-CAUSING LEG = INITIAL ACTIVE IMPULSIVE LEG
```

This must not be replaced by the BOS lifecycle unless the methodology is explicitly changed and approved.

---

## 10. IDM classification boundary

IDM is a key project-specific concept and should have strong provenance discipline.

### General SMC layer

`STANDARD_SMC`

Inducement/liquidity concepts can be found in broader SMC/ICT terminology.

### True SMC layer

`TRUE_SMC_CANONICAL`

The project definition is:

```text
IDM = liquidity resting beyond the most recent
Structurally Valid Pullback on the active impulsive leg
```

Therefore:

```text
Structurally Valid Pullback
        ↓
Verified Pullback Extreme
        ↓
Liquidity
        ↓
IDM eligibility
        ↓
Active/Minor IDM
```

The following must not independently create IDM:

- arbitrary local highs/lows
- arbitrary pivots
- inside bars
- Fibonacci levels
- generic liquidity pools
- candle count alone
- a 38.2% level alone

---

## 11. Genesis / bootstrap classification

Genesis is partly methodology and partly implementation.

### Methodology authority

`TRUE_SMC_CANONICAL`

The mapper must not fabricate historical structure merely because initialization requires an object.

### Implementation authority

`IMPLEMENTATION`

Initialization must explicitly distinguish the absence of historical structure from the first validated structural state. Bootstrap state must remain distinguishable from organically confirmed structure.

---

## 12. Current unresolved / unverified classifications

These items remain explicitly marked rather than silently promoted.

### `UNVERIFIED`

- quantitative definition of “large/high-momentum” unless an authoritative source is established
- any newly invented volatility/body/ATR threshold
- claims that the exact 38.2% threshold is a universal SMC axiom
- claims that the exact >=3 candle rule is universal SMC
- claims that the exact >=5 prior extremes rule is universal SMC
- claims that the exact OB three-pillar model is universal SMC
- claims that repository scoring weights are methodology truth

### `METHODOLOGY_PARAMETER`

- 38.2% default retracement threshold
- future quantitative momentum thresholds, if explicitly approved

### `IMPLEMENTATION`

- state names
- pointer storage
- object identity checks
- configuration plumbing
- historical-state retention
- mapper lifecycle mechanics

---

## 13. Negative constraints vs positive invariants

The canonical rules contain strong anti-patterns. Validation must also use positive invariants.

### Positive structural invariants

1. Every IDM has a valid structural parent.
2. Every active Minor IDM derives from the newest eligible Structurally Valid Pullback on the active impulsive leg.
3. Every Real Major IDM derives from the required post-BOS structural lifecycle.
4. A confirmed swing has the required IDM/liquidity confirmation sequence.
5. BOS consumes an already validated structural reference.
6. CHoCH consumes a governing range-boundary violation.
7. Historical structure cannot silently become current governing structure.
8. Deep retracement alone cannot reset confirmed structure.
9. Configuration cannot create a structural event that methodology prerequisites do not permit.
10. Scoring cannot validate an otherwise invalid structural object.

These are validation invariants; they do not replace existing rules.

---

## 14. Current skill organization

```text
.agents/skills/smc/
├── skill.md
├── skill_old.md
├── standard_smc.md
├── true_smc_canonical.md
├── methodology_parameters.md
├── implementation.md
├── execution.md
├── risk.md
├── unverified.md
├── deprecated.md
└── CATEGORY_MAP.md
```

`skill.md` is the master entry point. The category documents contain the migrated rule bodies. `skill_old.md` is the immutable pre-reorganization baseline.

---

## 15. Rule for future edits

Before changing any existing rule, the change must answer:

1. **What category does the rule belong to?**
2. **What is the source/authority for the rule?**
3. **Is it universal SMC knowledge or True SMC-specific?**
4. **Is it methodology, parameter, implementation, execution, or risk?**
5. **What objects depend on it?**
6. **What existing tests depend on it?**
7. **Does the change alter semantics or only organization?**
8. **Has the methodology change been explicitly approved before implementation?**

No rule should be deleted merely because its category is unclear. Unclear rules should first be marked `UNVERIFIED` or otherwise classified pending verification.

## Migration audit status

Section-level migration is complete. Final rule-by-rule audit against `skill_old.md` remains the acceptance gate. Every original rule, invariant, test requirement, and anti-pattern must have a category owner and retain equivalent semantics before `skill_old.md` can be treated as archival-only.