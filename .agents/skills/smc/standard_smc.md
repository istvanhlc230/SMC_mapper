# STANDARD_SMC

**Role:** General SMC/ICT concepts used as the methodology baseline.

**Authority boundary:** This file does not override the canonical True SMC definitions in `skill.md`. Where the project defines stricter semantics, `true_smc_canonical.md` governs.

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

## Source of truth

The complete existing canonical rules remain in `skill.md` during the migration phase. This file is an organizational category view; no rule is deleted by its existence.
