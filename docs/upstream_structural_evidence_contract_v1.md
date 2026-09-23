# Upstream Structural Evidence Contract v1

**Status:** implemented as an interface-validation layer. The HTF/LTF monitor is not modified by this change.

## Purpose

This contract defines the strict boundary between the canonical upstream structural engine and execution/observation consumers.

The consumer may validate and consume structural evidence. It must never manufacture missing IDM, swing, BOS, CHoCH, or protected-boundary state from raw OHLC heuristics.

## Canonical dependency chain

```
RAW OHLC
  -> CANDLE-LEVEL VALID PULLBACK
  -> VERIFIED PULLBACK EXTREME
  -> STRUCTURAL QUALIFICATION
  -> STRUCTURALLY VALID PULLBACK
  -> ACTIVE/MINOR IDM
  -> IDM_TAKEN
  -> CONFIRMED_STRUCTURAL_SWING
  -> PHYSICAL_EXTERNAL_BREAK
  -> VALID_BOS / CHoCH classification
  -> PROTECTED STRUCTURAL EXTREME / TRADING RANGE
```

The dependency order is consumed from the repository's canonical SMC skill. This implementation does not redefine those semantic objects.

## Evidence envelope

Every evidence object carries:

- `evidence_id`
- `workflow_id`
- `symbol`
- `timeframe`
- timezone-aware `event_timestamp`
- `producer`
- `methodology_version`
- `object_type`
- `object_id`
- `parent_evidence_ids`
- `source_candle_ids`
- optional lifecycle `state`
- `provenance`
- object-specific `payload`

The validator enforces duplicate-ID rejection, parent existence, workflow/symbol/timeframe isolation, and causal parent-to-child timestamp ordering.

## Structural invariants

### SVP / IDM

`STRUCTURALLY_VALID_PULLBACK` must reference `VERIFIED_PULLBACK_EXTREME` and carry explicit qualification evidence.

`MINOR_IDM` must reference both the structurally valid pullback and verified pullback extreme. No adapter may promote an unqualified pullback into IDM.

### IDM takeout / swing

`IDM_TAKEN` must reference an established IDM and identify wick/body interaction.

`CONFIRMED_STRUCTURAL_SWING` must reference `IDM_TAKEN`.

IDM takeout does not become BOS, CHoCH, or range rollover by itself.

### BOS

`VALID_BOS` must reference a confirmed swing, IDM takeout, physical external break, and stored structural qualification.

The evidence must state `retracement_depth >= 0.382` and a successful BOS gate.

A protected structural extreme must reference a `VALID_BOS`.

### CHoCH

`CHoCH_ELIGIBLE` must reference the governing protected opposing boundary and physical break.

Wick classification additionally requires an independently formed `REAL_MAJOR_IDM` lineage.

`FALLBACK_MAJOR_IDM` is distinct from `REAL_MAJOR_IDM`. A fallback wick sweep is represented as `MAJOR_IDM_SWEEP`, not CHoCH confirmation.

## Failure behavior

Invalid or incomplete evidence raises `StructuralEvidenceError`. There is no inference fallback.

The intended monitor behavior for missing or invalid upstream truth is:

```
OPEN CANONICAL GAP
NO CODE-LEVEL STRUCTURAL INFERENCE
NO DATA FABRICATION
SETUP REMAINS QUARANTINED
```

## Deliberate non-goals

- No changes to `SMC_mapper.py` in this phase.
- No changes to the frozen 28-test monitor regression baseline.
- No synthetic Layer 2/Layer 3 structural engine inside the monitor.
- No conversion of self-attested flags into structural truth.
- No automatic promotion of fallback Major IDM to Real Major IDM.
