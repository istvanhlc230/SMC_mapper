# CURRENT TASK
Phase 2 Pre-implementation Design: Canonical mapping, data contracts, and test strategy for `smc_analyzer.py`.

# DEVELOPER REPORT
**Current Repository State:**
* **Branch:** main
* **HEAD:** 14b581f
* **Working-tree status:** clean
* **Implementation decisions:** Revised Phase 2 design artifacts based on final Validator feedback (categorizing semantic types, separating process stages from lifecycle, and enforcing exact Target/RR eligibility contracts). No code implemented yet.
* **Exact smc_skill files relied upon:** 
  - `01_micro_structure.md`
  - `02_minor_structure.md`
  - `03_structural_semantic_authority.md`
  - `04_BOS_mechanics.md`
  - `05_CHOCH_mechanics.md`
  - `06_execution.md`
  - `08_implementation.md`

## 1. Canonical Rule Matrix & Resolution Checklist
- [x] **Categorization Fixed:** Explicit distinction between `LIFECYCLE STATE`, `STRUCTURAL OBJECT/FACT`, `PROCESS CONDITION`, `EVENT DETECTION`, and `CLASSIFICATION OUTCOME`.
- [x] **Target/RR Contract Fixed:** Target remains `None`, RR remains `NOT_EVALUABLE`. Invented targets are strictly forbidden. Non-evaluable POIs are output as `StructuralPOICandidate`, not executable setups.

| Rule Concept | Canonical Source | Key Constraints |
|---|---|---|
| Microstructure | `01_micro_structure.md` | 4 deterministic breach levels. Outside bar intrabar sequence is `UNAVAILABLE` unless proven. |
| Pullback | `02_minor_structure.md` | Minor structure, does not automatically create IDM or Major Swings. |
| Structural Qualification | `03_structural_semantic_authority.md` | Gate 1 (>=50%): normally >=3 opposing candles, or displacement outlier sweeping >=5 candles if <3. Gate 2 (38.2%<=depth<50%): requires HTF valid pullback. Gate 3 (<38.2%): disqualified. |
| Major IDM | `03_structural_semantic_authority.md` | First validated pullback post-BOS. Fallback IDM is a temporary proxy and does not roll trading range. |
| BOS | `04_BOS_mechanics.md` | BOS consumes stored `MAJOR_RETRACEMENT_QUALIFIED` state. Does not reimplement logic. |
| CHoCH | `05_CHOCH_mechanics.md` | Body close beyond opposing protected extreme -> `CHoCH_ELIGIBLE`. Requires full canonical gate. Fallback IDM wick = `MAJOR_IDM_SWEEP` (not BOS/CHoCH). |
| POIs | `06_execution.md` | Tradable POI Class: `OF_CONFIRMED` or `VALID_OB`. Execution Role: `DECISIONAL` (premium/discount) or `EXTREME`. Origin OB is latent reserve. |

## 2. Structural State Machine & Semantic Categorization
To prevent silent opaque advancements, the engine strictly categorizes components. The analyzer must persist prerequisites in the canonical structural state and consume them stage by stage.

**A. LIFECYCLE STATE (The only 5 enums representing macro range state):**
- `BOOTSTRAP`
- `CONFIRMATION_LOCKED`
- `CONFIRMED_RANGE`
- `POST_BOS`
- `POST_CHOCH`

**B. EVENT DETECTION (Exactly 7 classes representing physical OHLC observation):**
`NO_EVENT / INTERNAL_PB`, `MINOR_IDM_EVENT`, `EXT_CONT_BREAK`, `EXT_OPP_BREAK`, `FALLBACK_EVENT`, `REAL_MAJOR_IDM_EVENT`, `NEW_SVP_QUALIFIED`.

**C. PROCESS CONDITION (Intermediate logic gating):**
- `IDM_TAKEN`
- `STRUCTURAL_RETRACEMENT_EVALUATION`
- `CONFIRMATION GATE UNLOCKED`

**D. STRUCTURAL OBJECT/FACT (Persisted physical or conceptual anchor points):**
- `SWING_CANDIDATE`
- `CONFIRMED_STRUCTURAL_SWING`
- `STRUCTURAL_SWING_BREAK`

**E. CLASSIFICATION OUTCOME (The deterministic result of applying a Process Condition to an Event):**
- `VALID_BOS`
- `IMPULSE_EXTENSION`
- `MAJOR_IDM_SWEEP`
- `CHoCH_ELIGIBLE`
- `CHoCH_CONFIRMED`

*Implementation Contract:* A single event like `NEW_SVP_QUALIFIED` does not jump through the pipeline. It produces facts/conditions (e.g., `ACTIVE IDM`), which sit in memory until a later event (`IDM_TAKEN`) produces the next fact (`SWING_CANDIDATE`). 

## 3. Normalized OHLC Data Contract
To preserve exact determinism, float arithmetic is strictly forbidden. 
```python
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Candle:
    index: int                  # Deterministic provider ordering index
    timestamp: datetime         # Canonical timezone-aware (UTC required)
    open: Decimal               # Exact deterministic decimal
    high: Decimal
    low: Decimal
    close: Decimal
    is_completed: bool          # Unconfirmed/live candles EXCLUDED from historical mapping
    intrabar_sequence_evidence: str = "UNAVAILABLE" # "OBSERVED" | "METHODOLOGY_ASSUMED" | "UNAVAILABLE"
```
**Data Policies:**
- **Deterministic Order & Timezone:** Must be strictly ordered by UTC timestamp.
- **Duplicate Timestamps:** Hard error; execution halts to prevent corrupted sequences.
- **Invalid OHLC / Missing Bars:** Hard error if high < low; missing bars are treated as gaps, but structural relationships rely purely on the available ordered `Candle` array.
- **Completed Eligibility:** The most recent live candle is strictly excluded until provider marks it closed.
- **Adjusted vs Unadjusted:** Unadjusted OHLC must be used to preserve exact structural price bounds.
- **Insufficient History:** Analyzer halts with specific `INSUFFICIENT_HISTORY` code.
- **Intrabar Sequence:** Never silently inferred. Defaults to `UNAVAILABLE`.

## 4. Analyzer Output Contract & Target/RR Rule
Since target derivation is unresolved, 1:2 RR is `NOT_EVALUABLE`. Therefore, no POI can claim to be a fully qualified executable setup yet. It must be emitted as a non-executable structural candidate.
```python
from typing import Optional

@dataclass
class StructuralPOICandidate:
    ticker: str
    direction: str # "BUY" | "SELL"
    poi_top: Decimal
    poi_bottom: Decimal
    poi_class: str # "OF_CONFIRMED" | "VALID_OB"
    execution_role: str # "DECISIONAL" | "EXTREME"
    target: Optional[Decimal] = None # Unresolved gap.
    is_executable: bool = False # False because RR = NOT_EVALUABLE due to target=None
```
**Constraints:**
- If `target = None`, executable RR is `UNKNOWN / NOT_EVALUABLE`.
- The analyzer MUST NOT claim the 1:2 RR requirement is satisfied.
- The analyzer MUST NOT invent a target merely to make the RR pass.

## 5. Proposed zones.json schema change
**Status:** Blocked/Deferred. No changes until structural mapping is validated and implementation is complete.

## 6. Expanded Test Matrix
| Test Category | Target | Description |
|---|---|---|
| Determinism | OHLC Data | Asserts exact `Decimal` arithmetic, timezone handling, missing/duplicate data halts, incomplete candle exclusion, and `UNAVAILABLE` sequence inference. |
| Semantic | Component Separation | Asserts intermediate process conditions (`IDM_TAKEN`, `SWING_CANDIDATE`) are persisted and consumed sequentially, not opaquely skipped. |
| Invariant | Lifecycle Sequencing | Asserts `IDM_TAKEN` creates `SWING_CANDIDATE` (process condition), NOT confirmed swing or `VALID_BOS`. |
| Invariant | Revoked Swings | Asserts failed retracement qualification revokes candidate and shifts the active pullback/IDM reference. |
| Invariant | BOS Encapsulation | Asserts BOS solely consumes stored `MAJOR_RETRACEMENT_QUALIFIED` state and does not duplicate retracement depth math. |
| Invariant | Fallback Wick | Asserts fallback wick = `MAJOR_IDM_SWEEP`. It does not roll the range. |
| Invariant | Real Major IDM | Asserts Real Major IDM requires the independent post-BOS lifecycle; `NEW_SVP` does not automatically equal Real Major IDM. |
| Invariant | Anti-Retroactive | Asserts later candles cannot rewrite earlier classification of `MAJOR_IDM_SWEEP` or `VALID_BOS`. |

## 7. Specification Gaps
**SPECIFICATION GAP 1: Target Price Derivation**
* **DESCRIPTION:** The rule mandates minimum 1:2 RR and states the primary target is the "confirmed external range extreme where the applicable entry module requires it." It does not explicitly define behavior when multiple valid target candidates exist or when the external extreme does not satisfy 1:2 RR. 
* **RESOLUTION:** EXPLICITLY OPEN. `target` output is `None`. Consequently, setups are currently emitted as non-executable `StructuralPOICandidate` objects because the 1:2 RR check cannot be mathematically evaluated.

# VALIDATION REPORT
[Awaiting Independent Validation Agent]

# REQUIRED CORRECTIONS
[None]

# OPEN SPECIFICATION GAPS
See Developer Report Section 7.

# IMPLEMENTATION STATUS
Phase 2 Pre-implementation Design revised based on validator feedback. Awaiting validation.

# COMMITS
[Will append commit SHA after review]
