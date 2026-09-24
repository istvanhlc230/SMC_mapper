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
[Awaiting Independent Validation Agent]

# REQUIRED CORRECTIONS
[None]

# OPEN SPECIFICATION GAPS
See Developer Report Section 7.

# IMPLEMENTATION STATUS
Phase 2 Pre-implementation Design complete. Awaiting validation.

# COMMITS

COMMIT: 1f4fc8c
FILES: AGENT_REVIEW.md
PURPOSE: Initial creation of AGENT_REVIEW.md containing Phase 2 pre-implementation artifacts.
TESTS: N/A
