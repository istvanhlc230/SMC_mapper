# CURRENT TASK
Phase 2 Pre-implementation Design: Canonical mapping, data contracts, and test strategy for `smc_analyzer.py`.

# DEVELOPER REPORT
**Current Repository State:**
* **Branch:** main
* **HEAD:** ac89026 (Validator update)
* **Working-tree status:** clean
* **Implementation decisions:** Revised Phase 2 design artifacts based on Validator feedback.
* **Exact smc_skill files relied upon:** 
  - `01_micro_structure.md`
  - `02_minor_structure.md`
  - `03_structural_semantic_authority.md` (Semantic Owner for Qualification)
  - `04_BOS_mechanics.md`
  - `05_CHOCH_mechanics.md`
  - `06_execution.md`
  - `08_implementation.md`

## 1. Canonical Rule Matrix
| Rule Concept | Canonical Source | Key Constraints |
|---|---|---|
| Microstructure | `01_micro_structure.md` | 4 deterministic breach levels. Outside bar intrabar sequence is `UNAVAILABLE` unless proven. |
| Pullback | `02_minor_structure.md` | Minor structure, does not automatically create IDM or Major Swings. |
| Structural Qualification | `03_structural_semantic_authority.md` | Gate 1 (>=50%): normally >=3 opposing candles. If <3, requires displacement outlier sweeping >=5 preceding candles. Gate 2 (38.2%<=depth<50%): requires HTF valid pullback. Gate 3 (<38.2%): disqualified. |
| Major IDM | `03_structural_semantic_authority.md` | First validated pullback post-BOS. Fallback IDM is a temporary proxy and does not roll trading range. |
| BOS | `04_BOS_mechanics.md` | Physical external break (wick is sufficient) + consumed stored qualification (depth >=38.2% + IDM taken). Does not require body close. |
| CHoCH | `05_CHOCH_mechanics.md` | Body close beyond opposing protected extreme -> `CHoCH_ELIGIBLE`. Requires full canonical gate. Fallback IDM wick = `MAJOR_IDM_SWEEP` (not BOS/CHoCH). |
| POIs | `06_execution.md` | Tradable POI Class: `OF_CONFIRMED` or `VALID_OB`. Execution Role: `DECISIONAL` (premium/discount) or `EXTREME`. Origin OB is latent reserve, NOT an active 3rd POI. FVG is not a POI. |

## 2. Structural State Machine
Based on `08_implementation.md`, using exactly the canonical definitions:

**1. Event Detection (exactly 7 classes):**
`NO_EVENT / INTERNAL_PB`, `MINOR_IDM_EVENT`, `EXT_CONT_BREAK`, `EXT_OPP_BREAK`, `FALLBACK_EVENT`, `REAL_MAJOR_IDM_EVENT`, `NEW_SVP_QUALIFIED`.

**2. Event Classification:**
Evaluates detection events against rules. E.g., `EXT_CONT_BREAK` -> evaluates stored qualification -> classification outcome is `VALID_BOS` or `IMPULSE_EXTENSION`. (These are NOT event classes or lifecycle states).

**3. State Transition (Lifecycle States):** 
- `BOOTSTRAP`
- `CONFIRMATION_LOCKED`
- `CONFIRMED_RANGE`
- `POST_BOS`
- `POST_CHOCH`

## 3. Normalized OHLC Data Contract
To preserve observability, identity, and explicit intrabar evidence:
```python
@dataclass
class Candle:
    index: int                  # Deterministic provider order
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    is_completed: bool          # Unconfirmed/live candles excluded from historical mapping
    intrabar_sequence_evidence: str = "UNAVAILABLE" # "OBSERVED" | "METHODOLOGY_ASSUMED" | "UNAVAILABLE"
```
Aggregate OHLC will NOT be silently promoted to observed sequence evidence.

## 4. Analyzer Output Contract
Setup output separates POI Semantic Class from Execution Role, strictly forbidding Origin OB as a third active setup.
```python
@dataclass
class ValidSetup:
    ticker: str
    direction: str # "BUY" | "SELL"
    poi_top: float
    poi_bottom: float
    target: float  # Unresolved gap (see Specification Gaps)
    poi_class: str # "OF_CONFIRMED" | "VALID_OB"
    execution_role: str # "DECISIONAL" | "EXTREME"
```

## 5. Proposed zones.json schema change
**Status:** Blocked/Deferred. 
We will NOT modify `zones.json` or the monitor until the semantic contracts and structural mapping are fully validated and approved. Any future additions (timestamps, structural_hash) will be metadata only. Historical `zones.json` setups will be used for execution output format reference only, NOT as correctness oracles.

## 6. Test Matrix
| Test Category | Target | Description |
|---|---|---|
| Unit | Microstructure | Verify inside/outside bars, 4-tier breach taxonomy, `UNAVAILABLE` intrabar state. |
| Unit | Structural Qualification | Assert standard >=50% vs conditional 38.2% paths, and the <3 candle displacement outlier rule. |
| Invariant | Fallback vs Real IDM | Asserts Fallback IDM wick = `MAJOR_IDM_SWEEP` (no range rollover). Asserts Real Major IDM replaces Fallback. |
| Invariant | Wick-BOS & CHoCH Gating | Asserts wick-BOS is valid without body close. Asserts body close is only `CHoCH_ELIGIBLE` and blocked if prerequisites fail. |
| Invariant | POI Ontology | Asserts `FVG` -> `NOT_POI`. Asserts `OF_FAILED` != `VALID_BOS`. Asserts Rule of Two (max 2 active POIs: Decisional/Extreme). |
| Invariant | Anti-Retroactive | Asserts later candles cannot rewrite earlier classification of `MAJOR_IDM_SWEEP` or `VALID_BOS`. |

## 7. Specification Gaps

**SPECIFICATION GAP 1: Target Price Derivation**
* **CANONICAL SOURCE CHECKED:** `06_execution.md` (Section 41)
* **DESCRIPTION:** The rule mandates minimum 1:2 RR and states the primary target is the "confirmed external range extreme where the applicable entry module requires it." It does not explicitly define behavior when multiple valid target candidates exist or when the external extreme does not satisfy 1:2 RR.
* **PROPOSED OPTIONS:** 
  - Treat as an unresolved specification gap. The analyzer will calculate the "confirmed external range extreme" price, but the exact mechanism for setting the final `target` output is pending further architectural definition or validator instruction.

**SPECIFICATION GAP 2: Precedence on Retracement Qualification Outliers**
* **CANONICAL SOURCE CHECKED:** `03_structural_semantic_authority.md` vs `08_implementation.md` (Testing Requirements)
* **DESCRIPTION:** `08_implementation.md` mentions an "exact 2-candle exception". `03_structural_semantic_authority.md` defines the outlier as "< 3 opposing candles exist ... if and only if a single candlestick displacement outlier sweeps ... >= 5 preceding candles". 
* **RESOLUTION:** According to the precedence rule in `skill.md`, `03_structural_semantic_authority.md` is the SEMANTIC OWNER. The analyzer will implement the semantic owner's rule ("< 3 opposing candles" sweeping ">= 5 preceding candles") rather than artificially restricting it strictly to "exactly 2 candles".

**SPECIFICATION GAP 3: Qualitative Filters (Momentum & Shrinking Candles)**
* **CANONICAL SOURCE CHECKED:** `06_execution.md` (Section 40.5, Patterns 4 & 6)
* **DESCRIPTION:** Momentum Candle and Shrinking Candles are qualitative/SOURCE-PENDING. 
* **RESOLUTION:** We will NOT invent ATR/body-ratio formulas. These remain execution-only qualitative filters and will not be used as binary structural validity gates in the analyzer.

# VALIDATION REPORT
[Awaiting Independent Validation Agent]

# REQUIRED CORRECTIONS
[None]

# OPEN SPECIFICATION GAPS
See Developer Report Section 7.

# IMPLEMENTATION STATUS
Phase 2 Pre-implementation Design revised based on corrections. Awaiting validation.

# COMMITS
[Will append commit SHA after review]
