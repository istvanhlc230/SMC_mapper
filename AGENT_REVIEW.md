# CURRENT TASK
Phase 2 Pre-implementation Design: Canonical mapping, data contracts, and test strategy for `smc_analyzer.py`.

# DEVELOPER REPORT
**Current Repository State:**
* **Branch:** main
* **HEAD:** e09e0b9
* **Working-tree status:** clean
* **Implementation decisions:** Revised Phase 2 design artifacts to finalize explicit target RR behavior and persistent lifecycle execution paths. No code implemented yet.
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
- [x] **Persistent Lifecycle Chain:** Explicit chain defined (IDM_TAKEN to VALID_BOS) where each stage persists its state to be consumed sequentially. No opaque multi-stage collapse.
- [x] **Target/RR Contract Fixed:** Fixed wording regarding RR evaluability. Target is unresolved, therefore RR is NOT_EVALUABLE. No executable setup is permitted.

| Rule Concept | Canonical Source | Key Constraints |
|---|---|---|
| Microstructure | `01_micro_structure.md` | 4 deterministic breach levels. Outside bar intrabar sequence is `UNAVAILABLE` unless proven. |
| Pullback | `02_minor_structure.md` | Minor structure, does not automatically create IDM or Major Swings. |
| Structural Qualification | `03_structural_semantic_authority.md` | Gate 1 (>=50%): normally >=3 opposing candles, or displacement outlier sweeping >=5 candles if <3. Gate 2 (38.2%<=depth<50%): requires HTF valid pullback. Gate 3 (<38.2%): disqualified. |
| Major IDM | `03_structural_semantic_authority.md` | First validated pullback post-BOS. Fallback IDM is a temporary proxy and does not roll trading range. |
| BOS | `04_BOS_mechanics.md` | BOS consumes stored `MAJOR_RETRACEMENT_QUALIFIED` state. Does not reimplement logic. |
| CHoCH | `05_CHOCH_mechanics.md` | Body close beyond opposing protected extreme -> `CHoCH_ELIGIBLE`. Requires full canonical gate. Fallback IDM wick = `MAJOR_IDM_SWEEP` (not BOS/CHoCH). |
| POIs | `06_execution.md` | Tradable POI Class: `OF_CONFIRMED` or `VALID_OB`. Execution Role: `DECISIONAL` (premium/discount) or `EXTREME`. Origin OB is latent reserve. |

## 2. Structural State Machine & Persistent Prerequisites
**Determinism Claim:** `EVENT DETECTION → exactly ONE event`. `EVENT CLASSIFICATION → exactly ONE outcome`. `STATE TRANSITION → exactly ONE next state`. 

**A. LIFECYCLE STATE (The only 5 enums representing macro range state):**
- `BOOTSTRAP`
- `CONFIRMATION_LOCKED`
- `CONFIRMED_RANGE`
- `POST_BOS`
- `POST_CHOCH`

**B. PERSISTENT LIFECYCLE CHAIN (Execution Pipeline)**
The analyzer MUST NOT implement one candle/event by silently advancing through canonical stages opaquely. Each prerequisite must be persisted in the canonical structural state and consumed by the next stage:

`IDM_TAKEN`
→ `SWING_CANDIDATE`
→ `STRUCTURAL_RETRACEMENT_EVALUATION`
→ `QUALIFIED / NOT_QUALIFIED`
→ `CONFIRMED_STRUCTURAL_SWING` OR `SWING_REVOKED`
→ `STRUCTURAL_SWING_BREAK`
→ `VALID_BOS` / `IMPULSE_EXTENSION`

**Strict Process Constraints:**
- `IDM_TAKEN` does NOT create a confirmed swing.
- `SWING_CANDIDATE` does NOT imply retracement qualification.
- Retracement evaluation produces an explicit qualification result.
- Failed qualification produces `SWING_REVOKED` + `PULLBACK_REFERENCE_SHIFT`.
- Successful qualification produces `CONFIRMED_STRUCTURAL_SWING` + `MAJOR_RETRACEMENT_QUALIFIED`.
- Only a later structural swing break can consume that qualification for BOS.
- Physical break, structural swing break, and `VALID_BOS` remain distinct.
- Later candles may advance the lifecycle but may NOT retroactively rewrite an already classified event.
- These intermediate facts/conditions do NOT become artificial lifecycle enums.

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

## 4. Analyzer Output Contract (Target / RR)
The contract for executable outputs is explicitly restricted until target calculation logic is defined.
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
    target: Optional[Decimal] = None
    is_executable: bool = False
```
**Exact Target/RR Semantic Behavior:**
- `target=None` means target derivation is unresolved.
- Executable RR status MUST be `NOT_EVALUABLE` / `UNKNOWN`.
- The analyzer MUST NOT claim that the 1:2 RR requirement is satisfied when target is unresolved.
- The analyzer MUST NOT invent or synthesize a fallback target.
- A `StructuralPOICandidate` may exist with `is_executable=False`.
- An executable setup may be emitted ONLY when a canonical target exists and the 1:2 RR calculation can actually be evaluated.
- Therefore, the current implementation phase MUST NOT produce a fully executable setup merely because a POI is structurally valid.
- Target derivation explicitly remains an **OPEN specification gap**.

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
* **CANONICAL SOURCE CHECKED:** `06_execution.md` (Section 41)
* **DESCRIPTION:** The rule mandates minimum 1:2 RR and states the primary target is the "confirmed external range extreme where the applicable entry module requires it." It does not explicitly define target behavior when multiple valid target candidates exist or when the external extreme does not satisfy 1:2 RR.
* **RESOLUTION:** EXPLICITLY OPEN. `target` output is `None`. Target derivation is unresolved, and executable RR remains NOT_EVALUABLE until the formula is supplied. No invented fallback target is permitted.

# VALIDATION REPORT
[Awaiting Independent Validation Agent]

# REQUIRED CORRECTIONS
[None]

# OPEN SPECIFICATION GAPS
See Developer Report Section 7.

# IMPLEMENTATION STATUS
Phase 3 (Implementation) in progress.
- [x] Step 1: Normalized data model + deterministic event/state architecture and tests.
- [ ] Step 2: Micro/Minor structure layer (Candle relationships, Pullback, IDM detection).
- [ ] Step 3: Major structure layer (Swing Confirmation, BOS, CHoCH gating).
- [ ] Step 4: POI Identification (Decisional/Extreme rule of two).
- [ ] Step 5: JSON execution output projection (with `target=None`).

# COMMITS
COMMIT: [Will append commit SHA after review]
FILES: smc_analyzer.py, tests/test_smc_analyzer.py, AGENT_REVIEW.md
PURPOSE: Step 1: Implement canonical enums (LifecycleState, DetectionEvent, ProcessCondition, etc.) and MarketDataNormalizer with Decimal precision and strictly ordered UTC checks.
TESTS: pytest tests/test_smc_analyzer.py (8 passed)
