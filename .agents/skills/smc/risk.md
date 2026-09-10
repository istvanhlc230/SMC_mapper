# RISK

**Role:** Risk, scoring, position-sizing, and trade-management policy.

**Boundary:** Risk and scoring are downstream policy layers, not structural truth.

## Existing scoring weights

```text
Structure = 25%
Setup     = 30%
Location  = 20%
Liquidity = 15%
Risk      = 10%
```

## Quality tiers

```text
HIGH   >= 70
MEDIUM >= 55
LOW    >= 40
WATCH  < 40
```

## Liquidity quality

```text
Real Major IDM     = 80
Fallback Major IDM = 40
```

## Risk penalties

```text
Retracement > 78.6% → -25
Retracement > 90.0% → -20
```

## Mandatory boundaries

- Scoring evaluates canonical structural state.
- Scoring must never create or validate structure.
- Position sizing must not validate or invalidate structural objects.
- Risk management must consume structural state rather than redefine it.
- Configuration switches must not silently redefine canonical semantics.
- Minimum executable risk/reward is `1:2` where required by the canonical execution layer.

## Source of truth

The complete existing scoring and risk rules remain in `skill.md` during the migration phase. This file is the separated risk/scoring view; no existing rule is deleted by this step.
