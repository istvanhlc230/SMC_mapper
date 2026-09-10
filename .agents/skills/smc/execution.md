# EXECUTION

**Role:** Trading/execution-layer rules built on validated structural facts.

**Boundary:** Execution consumes structure; execution must never manufacture structural truth.

## Canonical POI ontology

Tradable POIs are limited to:

```text
VALID ORDER FLOW (OF)
VALID ORDER BLOCK (OB)
```

Rule of Two permits the canonical Decisional POI and Extreme POI within the dealing-range framework.

The following must not silently become tradable POIs:

- standalone FVG / imbalance;
- Breaker Block;
- Mitigation Block;
- Liquidity Void;
- arbitrary liquidity pool;
- IDM;
- generic displacement zone.

## POI separation

```text
IDM          ≠ POI
LIQUIDITY    ≠ POI
FVG          ≠ POI
DISPLACEMENT ≠ POI
POI          ≠ ENTRY EXECUTION
```

### Decisional POI

- BUY: normalized location must be in discount (`< 0.50`).
- SELL: normalized location must be in premium (`> 0.50`).

A valid underlying zone outside the required side is not a valid Decisional POI.

### Extreme POI

Extreme POI is the secondary/fallback execution location. It must independently be a Valid OF or Valid OB. Fallback execution does not relax POI validation.

### Origin OB

An Origin OB is a canonical absolute range-origin Order Block. Its validity is evaluated by OB rules and is not automatically removed when a parent Valid OF is mitigated.

## Order Block validation

Valid OB requires all three pillars:

1. Origin of impulsive displacement causing structural BOS.
2. Candle sweeps the previous candle's extreme.
3. Active, fully unmitigated adjacent FVG/imbalance.

The referenced BOS must be independently canonical.

## FVG / imbalance

FVG is a validator/property, primarily participating as the OB-validation pillar. It is never a standalone tradable POI or direct entry trigger.

Forbidden shortcuts:

```text
FVG → POI
FVG → ENTRY
FVG TOUCH → ENTRY
FVG BREAK → BOS
FVG → CHoCH
```

## Canonical entry modules

1. IDM Sweep
2. Decisional POI Mitigation
3. Engineering Liquidity Sweep
4. Extreme POI Mitigation

These modules may consume validated IDM, liquidity, structural, and POI state, but must never manufacture IDM, BOS, CHoCH, or Trading Range state.

## Execution failure boundaries

```text
EXECUTION PRIORITY ≠ STRUCTURAL VALIDATION
ORDER FLOW FAILED ≠ BOS
ORDER FLOW FAILED ≠ CHoCH
POI FAILURE ≠ STRUCTURAL FAILURE
```

Do not fail over from Valid OF to Extreme POI solely because price wicked into or through the OF. The canonical execution failure condition must be independently satisfied.

## Risk/reward execution gate

A canonical executable setup requires minimum risk/reward of `1:2`. Risk management consumes structural state and must not redefine it.

## Source of truth

The complete existing execution rules remain in `skill.md` during the migration phase. This file is the separated execution view; no existing rule is deleted by this step.
