# IMPLEMENTATION

**Role:** How the mapper represents and transitions canonical methodology objects.

**Boundary:** Implementation must follow methodology. Implementation convenience must never redefine methodology.

## Required conceptual state separation

The mapper must distinguish:

```text
CANDLE-LEVEL PULLBACK
STRUCTURALLY VALID PULLBACK
VERIFIED PULLBACK EXTREME
ACTIVE LIQUIDITY POINTER
ACTIVE/MINOR IDM
REAL MAJOR IDM
FALLBACK MAJOR IDM
IDM SWEEP
TENTATIVE SWING
CONFIRMED SWING
BOS
CHoCH
TRADING RANGE
```

## Active pullback pointer

Track one active pullback pointer for the active expansion/impulsive leg: the most recent Structurally Valid Pullback.

A newer valid pullback replaces the active pointer. Historical structure remains separately retained.

## Object identity

Active Minor IDM, Major IDM, Fallback Major IDM, confirmed swings, Trading Range, and historical structure must remain semantically distinct. The active-Major-IDM BOS gate is object-identity based.

## Lifecycle ordering

Higher-level events must consume previously validated lower-level events. The mapper must not skip prerequisites because a later price movement appears visually obvious.

```text
CANDLE-LEVEL PULLBACK
→ STRUCTURAL QUALIFICATION
→ STRUCTURALLY VALID PULLBACK
→ LIQUIDITY
→ ACTIVE IDM
→ IDM SWEEP
→ CONFIRMED SWING
→ STRUCTURAL BREAK
→ BREAK ACCEPTANCE
→ BOS
→ NEW TRADING RANGE
```

CHoCH uses the governing Trading Range boundary and has its own lifecycle.

## Genesis / bootstrap

Initialization must not fabricate historical IDM, protected structure, confirmed swing, BOS, or Major IDM. Bootstrap state must remain distinguishable from organically confirmed state.

## Configuration and scoring boundary

Configuration may alter parameters but cannot manufacture structural truth. Scoring evaluates validated structural state and cannot create or validate structure.

## Implementation anti-patterns

- Promoting a candle-level pullback directly to IDM.
- Keeping multiple competing active Minor IDM targets.
- Using arbitrary local pivots as canonical CHoCH/BOS substitutes.
- Making IDM sweep detection declare BOS.
- Letting POI or FVG execution logic create structure.
- Allowing historical structure to silently become current governing structure.

## Source of truth

The complete existing implementation-contract rules remain in `skill.md` during the migration phase. This file is the separated implementation view; no existing rule is deleted by this step.
