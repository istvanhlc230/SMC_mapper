# TRUE SMC — PLATFORM EXECUTION CONTRACT

**Role:** Broker/exchange execution, order lifecycle, fill semantics, account reconciliation, and backtest execution contract.

**Authority boundary:** This document does **not** define True SMC market structure or trading-policy meaning. It defines how an already canonicalized execution decision is translated into an external trading venue or deterministic backtest.

## 1. Separation of responsibilities

The platform must keep these layers separate:

```text
SMC STRUCTURAL TRUTH
        ↓
EXECUTION AUTHORIZATION
        ↓
TRADING POLICY
        ↓
PLATFORM ORDER POLICY
        ↓
BROKER / EXCHANGE
        ↓
ORDER / FILL / POSITION STATE
```

An order, fill, or broker-side position state must never manufacture SMC structural truth.

## 2. Required order lifecycle

```text
ENTRY_AUTHORIZED
      ↓
ORDER_SUBMITTED
      ↓
ORDER_ACCEPTED / REJECTED
      ↓
PARTIALLY_FILLED / FILLED
      ↓
POSITION_OPEN
      ↓
POSITION_CLOSED
```

Cancellation and expiration remain explicit terminal order states:

```text
ORDER_SUBMITTED
   ├─ CANCELLED
   ├─ EXPIRED
   ├─ REJECTED
   └─ FILLED
```

No implementation may collapse submission, acceptance, fill, and open-position state into one boolean.

## 3. Quote and price model

A live platform must retain the venue's quote model explicitly:

- bid;
- ask;
- spread;
- timestamp/source of quote;
- tick size;
- minimum price increment;
- contract size;
- pip/tick value;
- volume unit and step;
- minimum/maximum order volume.

Buy and sell execution prices must be evaluated against the correct side of the quote. The midpoint is not a substitute for the executable bid/ask price.

## 4. Order-type boundary

The canonical SMC layer emits an entry authorization and reference price. A separate platform-order policy selects:

- market order;
- limit order;
- stop order;
- stop-limit or venue-specific equivalent.

The selected order type must be recorded with the entry authorization. The platform must not silently convert an authorized entry into another order type without an explicit policy.

## 5. Fill and slippage semantics

The execution layer must record:

- requested order price;
- accepted order price, if provided;
- actual fill price;
- filled quantity;
- remaining quantity;
- execution timestamp;
- slippage relative to the requested reference;
- broker/exchange order identifier.

Partial fills must remain partial. A partial fill must not be treated as a full position unless the filled quantity actually reaches the intended position size.

## 6. Stop and target submission

An executable setup requires:

```text
CANONICAL ENTRY_REFERENCE_PRICE
+
EXACT STOP PRICE
+
CANONICAL TARGET
+
VALID RISK POLICY
+
VALID PLATFORM CONSTRAINTS
```

The platform must reject automatic submission when any required value is unavailable or violates venue constraints.

## 7. Position-size conversion

The trading-policy layer provides monetary risk and desired position size. The platform converts that size to venue-supported units using:

- contract specifications;
- account currency;
- quote/base currency relationships;
- pip/tick value;
- minimum/maximum quantity;
- quantity step;
- margin requirements.

Rounding must be conservative and must not increase configured monetary risk.

## 8. Pending-order lifecycle

A pending order must retain its provenance:

```text
ENTRY_AUTHORIZATION_ID
STRUCTURAL_CONTEXT_ID
ENTRY_MODULE
ENTRY_REFERENCE_PRICE
STOP_ANCHOR
STOP_PRICE
TARGET_POLICY
TARGET_PRICE
POLICY_VERSION
TIMESTAMP
```

When structural/execution state invalidates the order, the platform cancels it according to the active order-lifecycle policy and records the reason. Historical authorization remains immutable.

## 9. Open-position reconciliation

Broker/exchange state is authoritative for actual order and position status.

After startup, reconnect, timeout, or transport failure:

```text
LOCAL STATE
   ↓
BROKER / EXCHANGE QUERY
   ↓
RECONCILIATION
   ↓
CANONICAL LOCAL EXECUTION STATE
```

The platform must not assume that an order submitted before a disconnect was filled.

Duplicate submission protection must use venue order identifiers and deterministic client identifiers where supported.

## 10. Backtest / replay contract

A backtest must use the same canonical decision interfaces as live execution.

Required constraints:

- no lookahead;
- completed-candle rules remain identical to live logic;
- lower-timeframe/tick evidence is used whenever the methodology requires intrabar ordering;
- bid/ask and spread assumptions are explicit;
- slippage assumptions are explicit;
- fills obey the selected order-type semantics;
- partial fills are modeled when the venue policy requires them;
- session/news policy is replayed using timestamped data;
- account equity and risk budgets evolve from actual simulated fills;
- all order/position state transitions are event-ordered and deterministic.

An OHLC-only backtest must not claim exact intrabar ordering when the source data cannot establish it.

## 11. Failure handling

The platform must fail closed for automatic trading when a required dependency is unavailable:

```text
STALE / MISSING QUOTE
STALE / MISSING ACCOUNT STATE
STALE / MISSING CONTRACT SPECIFICATION
STALE / MISSING NEWS DATA WHEN ENABLED
STALE / MISSING POLICY CONFIGURATION
        ↓
NO AUTOMATIC ORDER SUBMISSION
```

Alerts may continue, but signal observation and broker execution are separate permissions.

## 12. Auditability

Every order lifecycle transition must be attributable to:

- canonical entry authorization;
- trading-policy decision;
- platform-order policy decision;
- external venue response.

No platform execution state may overwrite or mutate historical structural facts.
