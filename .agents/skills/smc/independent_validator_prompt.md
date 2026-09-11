# Independent True SMC Architectural & Theoretical Validator

## Mission

Validate the current `SMC_Mapper` implementation and embedded True SMC methodology without redesigning it. Determine whether the repository preserves canonical ontology, provenance, structural/execution/risk separation, deterministic state transitions, and the absence of unsupported generic ICT/SMC contamination.

Do not silently fix discrepancies. Do not normalize contradictions in favor of implementation. Do not invent missing rules.

## Authority hierarchy

```text
CURRENT AUTHORITATIVE REPOSITORY SOURCE
        >
EXPLICIT LOCKED CANONICAL RULES
        >
VALIDATOR ASSUMPTIONS
        >
GENERIC SMC / ICT KNOWLEDGE
```

Classify disputes as `ACCEPT`, `ACCEPT WITH CLARIFICATION`, `CONFLICT`, `LOGICALLY INVALID`, `SOURCE-PENDING`, `DUPLICATE / ALREADY COVERED`, or `FALSE POSITIVE / SOURCE MISMATCH`.

## Current category-based source mapping

```text
Layer 1 → 01_candle_level_foundation.md
Layer 2 → 02_minor_structure.md
Layer 3 lifecycle → 03_structural_lifecycle.md
BOS detail → 03_structural_lifecycle_bos.md
CHoCH detail → 03_structural_lifecycle_choch.md
Execution → 04_execution.md
Risk → 05_risk.md
Implementation → 06_implementation.md
Post-CHoCH audit → cross_module_audit_post_choch.md
```

`skill.md` is the authoritative entry point. Do not create duplicate semantic categories merely because an earlier layout used different filenames.

## Architecture

```text
STRUCTURAL ENGINE
        ↓
EXECUTION ENGINE
        ↓
RISK ENGINE
```

Structural owns Valid Pullback, SVP, Verified Pullback Extreme, Liquidity, Minor/Real/Fallback IDM, Swing Confirmation, Protected Structural Extreme, BOS, CHoCH, Trading Range and structural regime state.

Execution consumes structural state and owns POI interaction, IDM/Engineering Liquidity sweeps, POI mitigation, candlestick confirmation and entry.

Risk consumes structural/execution state and owns stop, target, RR, pending-order invalidation and execution lifecycle.

Absolute invariants:

```text
EXECUTION DOES NOT CREATE STRUCTURE
RISK DOES NOT CREATE STRUCTURE
```

## Canonical structural checks

Validate the exact rules from the category files. At minimum:

- OHLC and candle relationships are observations, not automatic structure.
- Strict inside bar: `current.High < mother.High AND current.Low > mother.Low`.
- EQH/EQL reference transfer is directional and uses the second candle as active reference.
- Candle-level Valid Pullback must complete its full mirrored sequence.
- Standard structural retracement requires `>=3` opposing candles and configured minimum depth, default `38.2%`.
- Exactly-two-candle exception requires high momentum and either `>=5` prior extremes swept/engulfed or depth `>=38.2%`.
- No automatic one-candle exception.
- High momentum remains SOURCE-PENDING unless quantitatively authoritative.
- IDM requires SVP → Verified Pullback Extreme → Liquidity → IDM Eligibility.
- Minor IDM, Real Major IDM and Fallback Major IDM are distinct entities.
- Dynamic `E_retrace` is tracked until valid BOS.
- Physical external break is not automatically BOS.
- Valid wick-BOS is immediate and equality close at the broken level is valid where specified.
- Fallback wick breach is `MAJOR_IDM_SWEEP`, not BOS/CHoCH/range rollover/protected lock.
- Protected Structural Extreme is locked only by valid BOS.
- Normal CHoCH uses the governing opposing Protected Structural Extreme/range boundary.
- Body-close CHoCH is eligibility, not automatic validity; wick CHoCH requires the canonical Real Major IDM provenance.

## Post-CHoCH dual-lineage audit

A valid CHoCH creates two independent lineages:

```text
VALID_CHoCH
├─ MINOR IDM LINEAGE
│  └─ FIRST_POST_CHOCH_SVP
│     → VERIFIED_PULLBACK_EXTREME
│     → MINOR_IDM_ELIGIBILITY
│     → FIRST_POST_CHOCH_MINOR_IDM
│     → MINOR_IDM_SWEEP
│     → SWING_CONFIRMATION_GATE
│     → CONFIRMED_SWING
│     → FIRST_VALID_BOS
└─ FALLBACK PROXY LINEAGE
   └─ previous Protected Structural Extreme / external boundary
      → FALLBACK_MAJOR_IDM
```

Mandatory distinctions:

```text
FIRST_POST_CHOCH_SVP ≠ FIRST_POST_CHOCH_MINOR_IDM
FIRST_POST_CHOCH_MINOR_IDM ≠ FALLBACK_MAJOR_IDM
FALLBACK_MAJOR_IDM ≠ REAL_MAJOR_IDM
MINOR_IDM_SWEEP ≠ VALID_BOS
MAJOR_IDM_SWEEP ≠ VALID_BOS
MAJOR_IDM_SWEEP ≠ VALID_CHoCH
```

The implementation must enter `CONFIRMATION_LOCKED` after CHoCH. It must not immediately manufacture a normal confirmed Trading Range or Protected Structural Extreme. The fallback proxy must be initialized from the external boundary and remain distinct from internal Minor IDM lineage.

## Execution checks

Canonical tradable POIs are only Valid OF and Valid OB. Rule of Two applies. Standalone FVG, Breaker, Mitigation Block, Liquidity Void, IDM, arbitrary liquidity and generic displacement zones are not automatically tradable POIs.

OB validation requires all three canonical pillars. FVG is a validator/property, never a standalone POI.

Canonical direct-entry patterns are execution observations only. Validate exact formulas in `04_execution.md`; do not substitute generic candlestick definitions. Open-wick entries are forbidden where close confirmation is required. Shrinking Candles is an approach filter, not an independent trigger. Momentum remains SOURCE-PENDING when no authoritative quantitative threshold exists.

## Risk checks

Validate the canonical `05_risk.md`, including:

- Tier-1 zone/macro stop;
- optional deterministic Tier-2 pattern-extreme stop;
- downstream/configurable `P`;
- primary target = current confirmed external Trading Range extreme where applicable;
- minimum RR `1:2` where required;
- `TARGET_HIT ≠ VALID_BOS`;
- pending-order invalidation versus open-position lifecycle;
- zone failure versus risk stop versus structural invalidation;
- no mandatory market-close-on-CHoCH unless explicitly authorized;
- G1: `OHLC ≠ INTRABAR_SEQUENCE`.

## State-machine audit

Inspect actual implementation, not variable names. Map actual state to:

```text
BOOTSTRAP
CONFIRMATION_LOCKED
CONFIRMED_RANGE
POST_BOS
POST_CHOCH
```

Map actual event classes:

```text
NO_EVENT / INTERNAL_PB
MINOR_IDM_EVENT
EXT_CONT_BREAK
EXT_OPP_BREAK
FALLBACK_EVENT
REAL_MAJOR_IDM_EVENT
NEW_SVP_QUALIFIED
```

For every critical transition report:

```text
state → event → guard → transition → side effects
```

Do not infer intrabar chronology from OHLC.

## Provenance audit

Construct actual implementation provenance for every structural object and compare it with canonical lineage:

```text
SVP
← Structural Pullback Qualification
← Candle-Level Valid Pullback
← OHLC observations

Verified Pullback Extreme
← Structurally Valid Pullback

Minor IDM
← SVP
← Verified Pullback Extreme
← Liquidity

Real Major IDM
← VALID_BOS
← Post-BOS SVP
← Verified Pullback Extreme
← Major IDM eligibility

Fallback Major IDM
← External Protected Structural Extreme / External Range Boundary
```

## Adversarial checks

At minimum inspect:

```text
first post-CHoCH SVP without IDM
first post-CHoCH Minor IDM
fallback boundary wick
fallback boundary body close
Minor IDM sweep
Minor IDM sweep without remaining swing prerequisites
fallback proxy before first BOS
first BOS
first post-BOS SVP
Real Major IDM creation
fallback supersession
fallback accidentally promoted to Real Major IDM
Minor IDM accidentally classified as Major IDM
TARGET_HIT without BOS
POI failure without structural failure
CHoCH_ELIGIBLE without confirmed CHoCH
same-candle stop/target ambiguity
```

## Required final report

### A. Repository state
Report branch, HEAD, relevant commits, source mapping and changed files.

### B. Architecture verdict
`PASS`, `PASS WITH QUALIFICATIONS`, or `FAIL`.

### C. Layer verdict

| Layer | Verdict | Critical Findings |
|---|---|---|
| Layer 1 | | |
| Layer 2 | | |
| Layer 3 | | |
| Execution | | |
| Risk | | |
| Implementation | | |

### D. Ontology/provenance verdict
List every identity collapse, skipped prerequisite, or provenance leak.

### E. State-transition verdict
Report `state → event → guard → transition → side effects` for all critical paths.

### F. Generic contamination verdict
Only flag behaviorally material unsupported assumptions.

### G. Tests
Required failures remain `TEST_FAILURE`; validator PASS cannot override a failing implementation test.

### H. Remediation
Use `TEST_FAILURE → CORRECT/REMEDIATE → TEST`, or `HUMAN_REVIEW_REQUIRED` when remediation is outside validator scope.

## No-redesign rule

Do not redesign True SMC. Do not replace project-specific IDM, swing, BOS, CHoCH, POI, execution, or risk semantics with generic ICT/SMC conventions.
