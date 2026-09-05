---
name: true-smc

description: Governs and validates the canonical True SMC methodology for the SMC_mapper rebuild. Use when implementing, reviewing, testing, or validating True SMC structure, pullbacks, IDM, swings, BOS, CHoCH, trading ranges, POIs, execution, or scoring.
---

# True SMC Methodology Contract

This skill is the authoritative methodology contract for `SMC_mapper`.

## Development rule

The SMC_mapper implementation is a clean rebuild of the legacy `true_smc_scanner.py`. The legacy implementation is a behavioral reference only. Do not copy accidental behavior merely because it exists in the old engine.

Preserve the canonical methodology. Never weaken a structural rule to make an implementation or regression test pass.

## Structural hierarchy

Reason about market structure in this order:

```text
RAW OHLC
→ candle relationships
→ candle-level valid pullback
→ structural qualification
→ structurally valid pullback
→ verified pullback extreme
→ liquidity
→ active pullback pointer
→ IDM
→ IDM sweep
→ swing confirmation
→ structural swing
→ physical break
→ break acceptance
→ BOS
→ new trading range
```

Do not collapse these concepts into one generic high/low or signal flag.

## Mandatory non-equivalences

- local high/low != confirmed swing
- candle-level valid pullback != structurally valid pullback
- pullback != IDM
- 38.2% != IDM
- IDM sweep != BOS/CHoCH
- liquidity takeout != structural break
- FVG != standalone POI
- IDM != POI

## Valid pullback

Bullish candle-level valid pullback:

```text
reference high break
→ reference low breach
→ continuation/reference high break
```

Bearish is the exact directional mirror.

Equal highs/lows: the second candle becomes the active reference.

A strict inside bar does not independently create structure.

Outside bars are resolved by candle direction/body sequence:

- bullish outside bar: LOW → HIGH
- bearish outside bar: HIGH → LOW

An outside bar must not activate both directional branches merely because both extremes were exceeded.

## Structural retracement

A standard structurally valid pullback requires at least three opposing candles and the configured minimum retracement depth. Canonical default depth is 38.2%.

A two-candle momentum exception is allowed only when the movement qualifies as large/high-momentum and either:

- at least five prior extremes were swept/engulfed, or
- retracement reaches at least 38.2%.

Do not invent ATR, body-ratio, or other thresholds not defined by the methodology.

## Pullback, liquidity and IDM

Only a structurally valid pullback can create IDM.

The verified pullback extreme is candidate liquidity, not automatically IDM.

Maintain one active pullback pointer. A newer structurally valid pullback replaces the previous active pointer.

IDM is liquidity resting beyond the most recently formed structurally valid pullback on the active impulsive leg.

Minor IDM and Major IDM have separate lifecycles.

## Major IDM

Real Major IDM lifecycle:

```text
BOS
→ new trading range
→ first real post-BOS structurally valid pullback
→ Major IDM
```

Fallback Major IDM is a distinct state and must never be treated as equivalent to a real Major IDM.

## Sweeps, swings and breaks

An IDM sweep is a liquidity event. It is not automatically BOS or CHoCH.

Swing confirmation is separate from BOS.

For the active Major IDM gate, if the broken structural level is the active Major IDM, external Wick BOS is disabled:

- bullish acceptance requires Close > active Major IDM
- bearish acceptance requires Close < active Major IDM

Canonical external break:

- bullish physical break: High > Ref.High
- bullish acceptance: Close > max(Ref.Open, Ref.Close)
- bearish physical break: Low < Ref.Low
- bearish acceptance: Close < min(Ref.Open, Ref.Close)

Historical-close Wick BOS compatibility is not canonical.

## CHoCH and Trading Range

CHoCH is a regime transition through the governing Trading Range boundary.

The CHoCH-causing leg becomes the initial active impulsive leg, but is not automatically a pullback, IDM, or protected swing.

Trading Range state remains stable until an official transition occurs.

Range-lock behavior is asymmetric and must follow the canonical methodology.

## POI and execution ontology

POI ontology is closed:

- Valid Order Flow
- Valid Order Block

Standalone FVG is a validator/property only. It is never a standalone POI or entry signal.

Order Block requires all three pillars:

1. origin of impulsive displacement causing structural BOS
2. candle sweeps previous candle extreme
3. active fully unmitigated adjacent FVG

## Entry modules

Supported entry modules:

1. IDM Sweep
2. Decisional POI Mitigation
3. Engineering Liquidity Sweep
4. Extreme POI Mitigation

Minimum executable risk/reward is 1:2.

## Genesis

Genesis must not fabricate:

- IDM
- swing
- BOS
- Major IDM
- protected structure

## Obsolete behavior

The obsolete sub-38.2 Fibonacci bootstrap variant must not exist anywhere in canonical implementation semantics.

## Scoring

Scoring consumes structural evidence. It never defines structure.

Weights:

- Structure: 25%
- Setup: 30%
- Location: 20%
- Liquidity: 15%
- Risk: 10%

Quality tiers:

- HIGH >= 70
- MEDIUM >= 55
- LOW >= 40
- WATCH < 40

Liquidity quality:

- Real Major IDM: 80
- Fallback Major IDM: 40

Risk penalties:

- retracement > 78.6%: -25
- retracement > 90%: -20

## Implementation mapping

Keep these concepts explicitly distinguishable in the implementation:

- candle-level pullback
- structurally valid pullback
- verified pullback extreme
- active liquidity pointer
- active/minor IDM
- real Major IDM
- fallback Major IDM
- IDM sweep
- tentative swing
- confirmed swing
- BOS
- CHoCH
- Trading Range
