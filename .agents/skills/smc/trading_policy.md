# TRUE SMC — TRADING POLICY

**Role:** Configurable trading-plan and account-risk policy derived from the documented trading-plan examples in `main/knowledgebase/`.

**Authority boundary:** This document does not redefine True SMC market structure, IDM, BOS, CHoCH, POI, or entry-module semantics. It governs whether an already canonicalized setup is permitted to be executed under the configured trading plan.

## 1. Policy versus methodology

The knowledgebase contains a concrete example trading plan, including fixed per-trade risk, running-risk limits, trade-count limits, daily loss limits, session windows, news avoidance, and trade logging. These values are treated as **configurable trading-policy parameters**, not universal structural SMC constants.

## 1.5 Timeframe Execution Route

The source material supports both direct same-timeframe execution and optional Higher Timeframe → Lower Timeframe refinement.

```text
DIRECT ROUTE
ANALYSIS TIMEFRAME = EXECUTION TIMEFRAME

MULTI-TIMEFRAME ROUTE
HTF → narrative / structure / POI / liquidity
LTF → execution refinement
```

The platform must explicitly configure the active route. It must not require LTF execution for every setup.

When the multi-timeframe route is active:
- HTF defines the directional narrative and canonical structural context;
- LTF refines execution only;
- LTF may expose internal structure and activate the canonical LTF-CHoCH context when its prerequisites pass;
- LTF must not silently redefine the HTF structural narrative.

The source provides example timeframe pairings for different trading styles, but these are examples rather than universal SMC constants. A deployment must store an explicit HTF/LTF pair when using the multi-timeframe route.

## 2. Position sizing

Position sizing is determined only after the canonical entry and stop are resolved.

```text
RISK_AMOUNT = ACCOUNT_EQUITY × RISK_PERCENT

POSITION_SIZE = RISK_AMOUNT ÷ (STOP_DISTANCE_PIPS × PIP_VALUE_PER_POSITION_UNIT)
```

Required inputs:
- current account/equity value;
- configured risk percentage;
- exact entry/reference price;
- exact stop price;
- instrument pip/tick specification;
- broker/exchange volume constraints;
- applicable pip/tick value in the account currency.

The stop is placed to represent trade invalidation; position size is then adjusted to respect the configured monetary risk. The platform must not enlarge or move the stop merely to fit a desired position size.

## 3. Source-backed example risk policy

The documented trading-plan example specifies:

```text
FIXED_RISK_PER_POSITION = 0.5%
MAX_RUNNING_RISK = 0.5%
MAX_ONE_TRADE_PER_SESSION = 1
MAX_TWO_TRADES_PER_DAY = 2
MAX_DAILY_LOSS = 1.0%
```

These are the source trading-plan example values. They are not universal True SMC ontology. A deployment must explicitly configure whether these values are active.

## 4. Session policy

The source trading-plan example uses:

```text
LONDON_WINDOW = 08:00–11:00 UK local time
NEW_YORK_WINDOW = 13:00–16:00 UK local time
```

Session windows must be evaluated using a timezone database with UK daylight-saving rules. The platform must not hard-code a permanent UTC offset for UK time.

Entry eligibility is false outside configured trading windows.

## 5. News policy

The source trading-plan example prohibits execution during high-impact news affecting GBP or USD for the documented GBPUSD plan.

```text
HIGH_IMPACT_NEWS_FOR_EXPOSED_CURRENCY
        ↓
TRADING_DISABLED
```

A live platform therefore requires an external economic-calendar source and explicit blackout-window configuration. A missing or stale news feed must fail closed for a deployment that enables the news gate; it must not silently assume that no news exists.

## 6. Trade-count and daily-loss lifecycle

Trade-count and loss budgets are account/session policy state, not structural state.

```text
SESSION TRADE COUNT >= LIMIT → NO NEW ENTRY
DAILY TRADE COUNT >= LIMIT   → NO NEW ENTRY
DAILY LOSS >= LIMIT           → NO NEW ENTRY
RUNNING RISK >= LIMIT         → NO NEW ENTRY
```

Policy counters must survive process restarts and must be reconciled from broker/account history rather than maintained only in volatile memory.

## 7. Logging (Implementation Policy)

Every executed or rejected candidate trade should retain at minimum:

- timestamp;
- instrument;
- direction;
- setup/module;
- structural context identifiers;
- entry authorization reason;
- entry/reference price;
- stop anchor and exact stop price;
- target policy and target price;
- risk configuration;
- session/window;
- news-gate result;
- final order/fill/position outcome.

Logging is an engineering auditability requirement (Implementation Policy) and does not alter structural truth.

## 8. Fail-safe and Engineering Policies (Implementation Policy)

Missing account data, pip/tick value, volume constraints, configured risk limits, or required session/news data must prevent automatic order submission when the corresponding policy is enabled.

```text
INCOMPLETE RISK/EXECUTION INPUT
        ↓
NO AUTOMATIC ORDER SUBMISSION
```

Engineering requirements such as:
- stale/missing news feed → fail closed;
- persistent counters;
- broker reconciliation;
- restart recovery;
- logging requirements;
are strictly **Implementation/Platform Policy**. They are required for robust automated execution but are not source-derived SMC methodology.
