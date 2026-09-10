# RISK

**Role:** Risk, scoring, position-sizing, and trade-management policy.

**Authority boundary:** Risk and scoring are downstream policy layers, not structural truth. They consume canonical structural state and cannot create or validate it.

## 41. Execution, structural validation, and risk

Execution priority and structural validation are separate domains.

```text
EXECUTION PRIORITY ≠ STRUCTURAL VALIDATION
ORDER FLOW FAILED ≠ BOS
ORDER FLOW FAILED ≠ CHoCH
POI FAILURE ≠ STRUCTURAL FAILURE
```

A failed execution condition must not be converted into a structural event. Likewise, a structurally valid event does not automatically authorize execution.

## 44. Scoring

Existing scoring weights:

```text
Structure = 25%
Setup     = 30%
Location  = 20%
Liquidity = 15%
Risk      = 10%
```

Quality tiers:

```text
HIGH   >= 70
MEDIUM >= 55
LOW    >= 40
WATCH  < 40
```

Liquidity quality:

```text
Real Major IDM     = 80
Fallback Major IDM = 40
```

Risk penalties:

```text
Retracement > 78.6% → -25
Retracement > 90.0% → -20
```

Scoring evaluates canonical structural state. Scoring must never create or validate structure.

## Risk/reward

A canonical executable setup must satisfy a minimum risk/reward of **1:2** where required by the canonical execution layer. Risk management consumes structural state; it must not redefine structure.

## Risk boundaries

- Scoring evaluates canonical structural state.
- Position sizing must not validate or invalidate structural objects.
- Risk management must consume structural state rather than redefine it.
- Configuration switches must not silently redefine canonical semantics.
- Risk policy is downstream from structural validation.

## Migration status

The scoring and risk rules from the preserved pre-reorganization ruleset are migrated here. The immutable baseline remains `.agents/skills/smc/skill_old.md` until the complete rule-by-rule audit is finished.