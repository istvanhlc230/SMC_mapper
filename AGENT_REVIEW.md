# CURRENT TASK
Phase 2 Pre-implementation Design: Canonical mapping, data contracts, and test strategy for `smc_analyzer.py`.

# DEVELOPER REPORT
**Current Repository State:**
* **Branch:** main
* **HEAD:** 0fb14d6 Add files via upload
* **Working-tree status:** clean
* **Files modified:** None
* **Files created:** AGENT_REVIEW.md
* **Tests executed:** N/A (No tests written yet)
* **Test results:** N/A
* **Implementation decisions:** No code implemented yet. Awaiting validation of the 7 Phase 2 artifacts below.
* **Exact smc_skill files relied upon:** 
  - `01_micro_structure.md`
  - `02_minor_structure.md`
  - `03_structural_semantic_authority.md`
  - `04_BOS_mechanics.md`
  - `05_CHOCH_mechanics.md`
  - `06_execution.md`
  - `08_implementation.md`

## 1. Canonical Rule Matrix
| Rule Concept | Canonical Source | Key Constraints |
|---|---|---|
| Microstructure | `01_micro_structure.md` | 4 deterministic breach levels. Outside bar intrabar sequence is `UNAVAILABLE` unless proven. |
| Pullback | `02_minor_structure.md` | Minor structure, does not automatically create IDM or Major Swings. |
| Structural Qualification | `03_structural_semantic_authority.md` | >= 3 opposing candles AND >= 50% retracement (or conditional 38.2%). Exception: 2 candles + outlier sweep. |
| Major IDM | `03_structural_semantic_authority.md` | First validated pullback post-BOS. Fallback IDM is a temporary proxy and does not roll trading range. |
| BOS | `04_BOS_mechanics.md` | Requires eligible confirmed continuation swing, >= 38.2% retracement, physical break, and active IDM taken. |
| CHoCH | `05_CHOCH_mechanics.md` | Requires body close beyond governing opposing protected extreme + all prerequisites. Does not automatically happen on break. |
| POIs | `06_execution.md` | Rule of Two: Decisional (must be discount/premium) and Extreme. Origin OB is latent reserve. FVG is not a POI. |

## 2. Structural State Machine
Based on `08_implementation.md`, the engine will use a 3-layer deterministic pipeline:
1. **Event Detection:** E.g., `EXT_CONT_BREAK`, `EXT_OPP_BREAK`, `MINOR_IDM_EVENT`, `REAL_MAJOR_IDM_EVENT`.
2. **Event Classification:** E.g., Depth >= 38.2% + IDM Taken = `VALID_BOS`. Depth < 38.2% = `IMPULSE_EXTENSION`.
3. **State Transition:** 
   - `BOOTSTRAP`
   - `CONFIRMATION_LOCKED`
   - `CONFIRMED_RANGE`
   - `POST_BOS`
   - `POST_CHOCH`

## 3. Normalized OHLC Data Contract
The internal analyzer will operate on a standard dataclass strictly decoupled from the provider (`yfinance`):
```python
@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
```
No computed indicators will be passed. The structural analyzer derives relationships purely from this sequence.

## 4. Analyzer Output Contract
The analyzer will output a list of valid setups. A setup is only valid if it meets the `06_execution.md` POI ontology (Decisional or Extreme OB/OF).
```python
@dataclass
class ValidSetup:
    ticker: str
    direction: str # "BUY" | "SELL"
    poi_top: float
    poi_bottom: float
    target: float
    htf: str
    ltf: str
    poi_type: str # "DECISIONAL" | "EXTREME" | "ORIGIN_RESERVE"
```

## 5. Proposed zones.json schema change
To support the existing monitor while enabling structural change detection, the analyzer will preserve existing keys and append metadata:
```json
{
  "analysis_timestamp": "2026-09-24T12:00:00Z",
  "latest_analyzed_candle_time": "2026-09-24T11:00:00Z",
  "structural_hash": "a1b2c3d4",
  "setups": [
    {
      "ticker": "CCCC",
      "name": "CCCC D1 Decisional",
      "direction": "BUY",
      "htf": "1h",
      "ltf": "15m",
      "top_price": 3.30,
      "bottom_price": 3.05,
      "target": 4.38,
      "probability_pct": 55,
      "metadata": {
        "poi_type": "DECISIONAL",
        "provenance": "VALID_BOS"
      }
    }
  ]
}
```

## 6. Test Matrix
| Test Category | Target | Description |
|---|---|---|
| Unit | Microstructure | Verify inside/outside bars, and 4-tier breach taxonomy. |
| Unit | Retracement Math | Validate 50% and 38.2% calculations against precise OHLC extremes. |
| Fixture | BOS vs Extension | Feed mock candles where retracement is 35% -> expect `IMPULSE_EXTENSION`. Feed 40% -> expect `VALID_BOS`. |
| Fixture | CHoCH Gate | Feed mock candles sweeping Fallback IDM with wick -> expect `MAJOR_IDM_SWEEP` (no CHoCH). Feed body close beyond protected extreme -> expect `CHoCH_ELIGIBLE`. |
| Integration | POI Derivation | End-to-end test mimicking current `zones.json` setups to ensure derived POIs match expected bounds. |

## 7. Specification Gaps

**SPECIFICATION GAP 1: Target Price Derivation**
* **CANONICAL SOURCE CHECKED:** `06_execution.md` (Section 41)
* **DESCRIPTION:** The rule states "The primary target is the confirmed external range extreme where the applicable entry module requires it." It also mandates a minimum 1:2 RR. However, it does not explicitly specify how the JSON `target` field is mathematically calculated if the external extreme yields > 1:2 RR, or if multiple structural targets exist.
* **PROPOSED OPTIONS:** 
  1. Always set `target` to the exact price of the confirmed external range extreme (Protected High for buys, Protected Low for sells).
  2. Await validation agent clarification.

**SPECIFICATION GAP 2: Qualitative Filters (Momentum & Shrinking Candles)**
* **CANONICAL SOURCE CHECKED:** `06_execution.md` (Section 40.5, Patterns 4 & 6)
* **DESCRIPTION:** Momentum Candle and Shrinking Candles are defined as Qualitative Filters. `08_implementation.md` states we must not invent ATR or body-ratio formulas. 
* **PROPOSED OPTIONS:** 
  1. The analyzer will strictly ignore these qualitative filters for automated structural mapping and execution bounds, unless an explicit quantifiable rule is provided.

# VALIDATION REPORT

**Independent validation status: NOT APPROVED FOR IMPLEMENTATION**

I re-checked the Phase 2 artifacts against the current canonical `.agents/skills/smc/` files on `main`.

### Confirmed

- The canonical source file list is correct: `01_micro_structure.md`, `02_minor_structure.md`, `03_structural_semantic_authority.md`, `04_BOS_mechanics.md`, `05_CHOCH_mechanics.md`, `06_execution.md`, `08_implementation.md`.
- The analyzer/monitor separation is directionally correct.
- The three-layer architecture is required and correctly identified.
- Outside-bar historical intrabar evidence must remain explicit; `UNAVAILABLE` cannot be silently promoted to observed sequence evidence.
- IDM, swing, BOS, CHoCH, fallback IDM, POI, and execution semantics must remain distinct.
- Target derivation is genuinely not fully specified for every executable-module case; this remains an implementation-contract gap rather than something the analyzer may invent.

### Corrections required before coding

**1. Rule Matrix: retracement qualification is oversimplified.**

The matrix must state the actual hierarchical gates from `03_structural_semantic_authority.md`: `>=50%` standard equilibrium path; normally `>=3` opposing closing candles; fewer than 3 requires the documented displacement-outlier condition; `38.2% <= depth < 50%` qualifies only through the applicable immediate-HTF valid-pullback evidence gate; `<38.2%` is not qualified.

Do not describe this generically as a “2-candle + 38.2% exception” unless the exact canonical source language is identified and reconciled. The current skill text contains both the standard/outlier formulation and a testing bullet mentioning a 2-candle exception; this must be resolved explicitly rather than silently choosing one interpretation.

**2. Analyzer output contract is internally contradictory.**

The report says a valid setup is only Decisional or Extreme, but the proposed `poi_type` includes `ORIGIN_RESERVE`. Canonical `06_execution.md` says Origin OB is a latent reserve POI, not a third active tradable POI.

Executable setup output must not represent Origin Reserve as an active setup. Distinguish POI semantic class (`OF_CONFIRMED` / `VALID_OB`) from execution role (`DECISIONAL` / `EXTREME`). Represent Origin OB separately as latent/reserve state if it is emitted at all. Never let the output contract imply a third active POI.

**3. POI ontology must be represented explicitly.**

The proposed output contract currently conflates “POI type” with execution role. Canonical ontology is: tradable POI class = `OF_CONFIRMED` or `VALID_OB`; execution role = Decisional or Extreme; Origin OB = latent reserve, not an active third POI.

**4. Event-class matrix must use the exact canonical seven detection classes.**

`08_implementation.md` defines exactly: `NO_EVENT / INTERNAL_PB`, `MINOR_IDM_EVENT`, `EXT_CONT_BREAK`, `EXT_OPP_BREAK`, `FALLBACK_EVENT`, `REAL_MAJOR_IDM_EVENT`, `NEW_SVP_QUALIFIED`.

The report's illustrative event names are acceptable only if they map exactly to these canonical classes. Do not introduce competing event classes or use classification outcomes as event classes.

**5. State machine wording must distinguish lifecycle states from process conditions and outcomes.**

Canonical lifecycle states are `BOOTSTRAP`, `CONFIRMATION_LOCKED`, `CONFIRMED_RANGE`, `POST_BOS`, `POST_CHOCH`. `CONFIRMATION GATE UNLOCKED`, `VALID_BOS`, `IMPULSE_EXTENSION`, and `CHoCH_CONFIRMED` are not additional lifecycle-state enums.

**6. BOS contract must not be simplified to body close.**

Canonical implementation rules permit continuation external wick-BOS when all BOS prerequisites are satisfied. A later body close must not be required for a valid continuation BOS. Preserve `PHYSICAL_EXTERNAL_BREAK != STRUCTURAL_SWING_BREAK != VALID_BOS` and consume stored qualification at the break event.

**7. CHoCH must remain prerequisite-gated.**

A body close beyond the opposing protected boundary creates `CHoCH_ELIGIBLE`, not automatic `CHoCH_CONFIRMED`. Fallback IDM wick is `MAJOR_IDM_SWEEP`, not BOS/CHoCH/range rollover. Fallback IDM body close is `CHoCH_ELIGIBLE`, then the full canonical gate.

**8. Data contract needs evidence/provenance fields.**

The proposed Candle dataclass is too thin for the canonical observability model. Preserve candle identity/order, completed versus unconfirmed status, intrabar sequence evidence (`OBSERVED`, `METHODOLOGY_ASSUMED`, `UNAVAILABLE`), and deterministic provider normalization/order. Never infer historical OLHC/OHLC path from aggregate OHLC alone.

**9. JSON proposal is premature.**

Do not modify `zones.json` or the monitor yet. Proposed timestamps/hash may be useful provenance/cache metadata, but they are not canonical structural facts and must remain separate from executable setup semantics.

**10. Historical `zones.json` must not be a correctness oracle.**

Regression fixtures may preserve historical examples, but correctness must be asserted against canonical invariants from `smc_skill`, not reproduction of current hardcoded zones.

**11. Qualitative filters must remain SOURCE-PENDING.**

`06_execution.md` explicitly keeps Momentum Candle qualitative/SOURCE-PENDING and Shrinking Candles as an approach filter, not an entry trigger. Do not invent ATR/body-ratio formulas or use these as structural validity gates.

**12. Target is still a specification gap.**

`06_execution.md` states minimum RR 1:2 and says the primary target is the confirmed external range extreme where the applicable entry module requires it. Do not invent a universal target formula, alternative target, or fallback target.

Before executable `target` output is frozen, document which entry modules require the primary target, which confirmed external extreme is used for BUY/SELL in that module, behavior with multiple valid target candidates, and behavior when the external extreme does not satisfy 1:2.

### Gate decision

**STOP before implementation.** The developer must revise `AGENT_REVIEW.md` so the Rule Matrix, State Machine, Data Contract, Output Contract, JSON proposal, and Test Matrix are internally consistent with the canonical skill. Only after these corrections are resolved should implementation begin.

# REQUIRED CORRECTIONS

1. Correct retracement qualification hierarchy and explicitly reconcile the 2-candle/outlier wording conflict in the current skill.
2. Remove `ORIGIN_RESERVE` from the active ValidSetup enum; separate POI class from execution role and latent Origin OB state.
3. Use exact seven event-detection classes and keep classification outcomes/state enums separate.
4. Expand normalized candle/data contract to preserve observability and deterministic identity.
5. Keep JSON/monitor changes blocked until semantic contracts are approved.
6. Treat target derivation as an unresolved specification gap; no invented fallback.
7. Keep qualitative Momentum/Shrinking semantics non-invented and execution-only where applicable.
8. Add canonical negative/invariant tests from `03`/`08`/`06`, especially anti-retroactive classification, fallback-vs-real IDM, wick-BOS, CHoCH gating, POI ontology, and Rule-of-Two.

# OPEN SPECIFICATION GAPS

- Target derivation/output behavior remains open.
- The current canonical skill text itself contains a reconciliation point between the standard “<3 opposing candles + displacement outlier” wording and the testing requirement referring to an “exact 2-candle exception”; the developer must cite the exact governing subsection/precedence before encoding this as a test or rule.

# IMPLEMENTATION STATUS

Phase 2 design **rejected for implementation pending correction**.

# COMMITS

VALIDATOR UPDATE: current remote canonical validation appended to `AGENT_REVIEW.md`.
FILES: AGENT_REVIEW.md
PURPOSE: Independent validation of developer Phase 2 artifacts against `.agents/skills/smc/`.
TESTS: N/A — design validation only.
