# Risk, Stops, Targets and Trading Policy

## Primary paired sources

- ../true_smc123.txt
- ../true_smc_21dayBootCamp.txt
- ../truesmc2026.txt
- ../Become-a-TRUE-Forex-Trader-Become-a-TRUE-Forex-Trader_text_format.txt

## Supplementary sources

- ../everything_behind_the_trading_system.txt
- ../smc_trader_missing_piece.txt
- ../smc_trader_another_missing_piece.txt
- ../How to Know When a POI Has Failed.txt

## Risk model

The reconciliation records:
- position size is calculated only after canonical entry and stop resolution;
- risk amount = account balance × configured risk percentage;
- position size uses exact stop distance and instrument pip/tick value;
- example percentages are configurable trading-policy values, not universal SMC constants;
- policy state must persist and reconcile with account/broker history.

## Stop anchors

Current reconciled anchors:
- IDM Sweep → sweep extreme;
- Decisional POI → confirmation/reversal-pattern extreme;
- ENG LQD Sweep → validated sweep/confirmation extreme;
- Extreme POI → confirmation/reversal-pattern extreme.

The numeric buffer remains configurable because the source language does not establish one universal value.

## Targets

The pro-trend target path is canonicalized around the current confirmed external extreme or external liquidity.

Exact LTF and universal countertrend target hierarchies remain partially open.

RR consumes a resolved target; RR must not invent one.

## Trading policy

The source corpus also contains configurable session windows, high-impact news avoidance, daily/concurrent risk limits and trade-journal requirements. These are policy/platform controls rather than universal structural definitions.
