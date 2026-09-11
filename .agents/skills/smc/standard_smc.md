# STANDARD_SMC

**Role:** General SMC/ICT concepts used as baseline terminology.

**Authority boundary:** This file does not override the canonical True SMC definitions in the current Layer 1–3 methodology files. Where the project defines stricter semantics, the current True SMC semantic owner governs.

## Core concepts

- Raw OHLC
- Candle relationships
- Liquidity
- Buy-Side Liquidity (BSL)
- Sell-Side Liquidity (SSL)
- Swing highs / swing lows as candidate structural concepts
- Inducement / IDM as a general SMC liquidity concept
- Break of Structure (BOS) as a general structural-break concept
- Change of Character (CHoCH) as a general regime-transition concept
- Displacement
- Fair Value Gap (FVG) / imbalance
- Order Block (OB)
- Protected structural levels

## Boundary rules

General SMC terminology must not be used to replace project-specific True SMC semantics.

In particular:

- Generic IDM terminology does not permit arbitrary local highs/lows to become IDM.
- Generic BOS terminology does not replace the project's structural prerequisites and break-acceptance rules.
- Generic CHoCH terminology does not replace the governing Trading Range boundary rule.
- FVG, displacement, liquidity, and Order Block concepts do not independently create IDM, BOS, CHoCH, or a tradable POI.

## Provenance boundary

The presence of a concept in this category means it is recognized as general terminology only. It does not mean the project's exact thresholds, lifecycle, object identity, or qualification rules are universal SMC/ICT facts.

Project-specific semantics are authoritative in their current semantic-owner documents, with numeric/configurable parameters separated into `methodology_parameters.md`.

## Migration status

This category is terminology-only. It is not a fallback source of structural rules, and it must never be used to weaken the canonical True SMC rules.