# 05 — RISK

**Role:** Risk, scoring, position sizing, trade management, and execution-lifecycle policy.

**Authority boundary:** Risk is downstream from canonical structural validation. It consumes canonical structural/execution state and must never create, validate, reinterpret, or redefine structural truth.

**Scoring boundary:** The methodology defines the risk concepts and gating semantics. The concrete risk_quality calculation and final weighted score are implementation behavior owned by the mapper implementation and documented in 08_implementation.md. This document must not invent a competing scoring formula.

## 5.1 Structural Stop-Loss Placement

### Tier 1 — Structural / Zone Boundary Stop

Conservative stop placement is beyond the furthest relevant boundary of the parent OF_CONFIRMED / Valid Order Block according to the applicable execution module.

A stop placement or stop touch does not itself create structural truth:

```
EXECUTION_STOPPED_OUT ≠ ORDER_FLOW_FAILED
EXECUTION_STOPPED_OUT ≠ ORDER_BLOCK_FAILED
EXECUTION_STOPPED_OUT ≠ VALID_BOS
EXECUTION_STOPPED_OUT ≠ CHoCH_CONFIRMED
```

### Tier 2 — Refined Pattern Extreme Stop

Tier 2 is optional and available only after a deterministic canonical candlestick reversal has actually triggered the entry.

Bullish:

```
SL = min(Low_pattern_candles) - P
```

Bearish:

```
SL = max(High_pattern_candles) + P
```

P is a downstream/configurable buffer. The methodology does not define a universal pip/tick or Spread + Minimum Tick value.

Tier 2 is not available for a direct limit entry without deterministic candle confirmation, and qualitative-only Momentum/Shrinking filters cannot authorize it.

### 5.1.1 Canonical Stop Anchors by Entry Module

The stop-loss anchor is determined by the canonical execution context. The stop buffer is a separate platform configuration and must never be guessed.

#### IDM Sweep

```text
IDM_SWEEP_ENTRY
    ↓
SWEEPING_CANDLE_EXTREME
    ↓
SL anchor = sweep extreme
```

Source examples support either the sweeping-candle extreme itself or a conservative buffer beyond it. The aggressive/conservative choice is execution policy; the structural anchor remains the sweep extreme.

#### Decisional POI Mitigation

```text
DECISIONAL_POI_MITIGATION
    ↓
CONFIRMATION_PATTERN
    ↓
PATTERN_EXTREME
    ↓
SL anchor = pattern extreme
```

The source examples place the stop a few pips beyond the confirming/reversal pattern extreme. The exact buffer is not canonically specified.

#### Engineering Liquidity Sweep

```text
ENG_LQD_SWEEP
    ↓
SWEEP / CONFIRMATION STRUCTURE
    ↓
SWEEP_OR_CONFIRMATION_EXTREME
    ↓
SL anchor = validated sweep/confirmation extreme
```

The source examples consistently place the stop beyond the relevant sweep/confirmation low or high. The exact buffer remains configurable.

#### Extreme POI Mitigation

```text
EXTREME_POI_MITIGATION
    ↓
CONFIRMATION_PATTERN
    ↓
PATTERN_EXTREME
    ↓
SL anchor = pattern extreme
```

The source examples place the stop a few pips beyond the confirmation/rejection extreme. The exact buffer remains configurable.

### 5.1.2 Stop Buffer Contract

`P` is a required downstream execution parameter:

```text
STOP_PRICE = SL_ANCHOR ± P
```

`P` must be explicitly supplied by the platform execution configuration. It must not be silently defaulted to an invented number. The True SMC knowledgebase does not define one universal pip/tick value for all instruments or modules.

If `P` is unavailable, the setup may be analyzed and scored but an automatic broker order must not be submitted.

### Tier-2 stop-out semantics

```
Price <= Tier-2 bullish SL
OR
Price >= Tier-2 bearish SL
        ↓
EXECUTION_STOPPED_OUT
```

This remains an execution/risk event and is not POI failure, structural invalidation, BOS, CHoCH, or IDM creation.

## 5.2 Target Source / Implementation Boundary

Canonical SMC methodology does not prescribe target selection or trade-management behavior. It provides structural/liquidity chart facts that downstream implementation may use as target inputs.

LTF target selection priority, countertrend target-coordinate selection, fixed-R target generation, multi-leg allocation, and break-even/profit-lock/trailing actions are implementation/trading-policy concerns, not canonical SMC rules.

### Primary pro-trend chart-analysis target input

The primary pro-trend target candidate is the current Trading Range confirmed external extreme where the applicable execution module requires it:

```
bullish → Confirmed_Swing_High
bearish → Confirmed_Swing_Low
```

A downstream target may be an execution/risk object derived from chart-analysis inputs. It does not validate BOS.

```
TARGET_HIT ≠ VALID_BOS
```

When VALID_BOS occurs, the previous range-dependent external target candidate expires and the new Trading Range external extreme becomes an active structural target candidate.

When CHoCH_CONFIRMED occurs, targets belonging exclusively to the invalidated structural regime become invalid as an execution/risk lifecycle consequence. This does not manufacture a structural event.

### 5.2.1 Source-Backed Target Inputs by Execution Context

Downstream implementation may resolve a target from structural/liquidity chart provenance. The methodology does not prescribe a universal target-selection algorithm. A target must not be invented merely to satisfy an RR calculation.

#### Direct same-timeframe pro-trend execution

```text
ACTIVE TRADING RANGE
        ↓
CONFIRMED EXTERNAL EXTREME / EXTERNAL LIQUIDITY
        ↓
PRIMARY TARGET
```

The source repeatedly uses the external liquidity / external range extreme as the final pro-trend target for direct execution.

#### LTF execution

The source contains more than one target convention for LTF execution: some examples target the higher-timeframe external liquidity, while others use a lower-timeframe structural/BOS destination. Therefore the platform must expose an explicit target-policy selection for LTF execution rather than infer one silently.

```text
LTF EXECUTION
    ├─ HTF_EXTERNAL_TARGET
    └─ LTF_STRUCTURAL_TARGET
```

No automatic LTF target may be submitted until the target policy is explicitly selected.

#### Countertrend execution

Countertrend source scenarios target the next canonical destination in the opposite direction of the prevailing move, such as the next valid POI, inducement, Engineering Liquidity, or external liquidity level depending on the named setup.

The current source material does not establish one universal numeric TP coordinate for all countertrend setups. Therefore countertrend target resolution remains a setup-specific target-policy input until separately canonicalized.

#### Target invariants

```text
TARGET ≠ STRUCTURAL_VALIDATION
TARGET_HIT ≠ VALID_BOS
TARGET_HIT ≠ CHoCH
RR_CALCULATION ≠ TARGET_CREATION
NO_CANONICAL_TARGET → NO_AUTOMATIC_TP_SUBMISSION
```

### 5.2.2 Downstream Target Plan / Multi-Leg Management

The target system does **not** require the analyzer to predict one universally correct final price. The analyzer first identifies currently valid, source-backed structural/liquidity destination candidates. A downstream configurable Target Plan may associate multiple trade legs with different valid targets.

This is a **project execution architecture**, not a new universal True SMC target-selection rule. The source does not define one deterministic priority among all simultaneously valid target candidates, so the system must not invent one.

```text
STRUCTURAL / LIQUIDITY ANALYSIS
        ↓
VALID TARGET CANDIDATES
        ↓
CONFIGURABLE TARGET PLAN
        ├─ T1 → Trade Leg 1
        ├─ T2 → Trade Leg 2
        └─ T3 → Trade Leg 3
```

A Target Plan may contain any number of configured legs supported by the platform. A common three-leg configuration is illustrative only:

```text
Leg 1 → T1
Leg 2 → T2
Leg 3 → T3
```

The plan must preserve target provenance. It must never turn an arbitrary price, a fixed-R calculation, or a risk threshold into a canonical structural target.

Each configured leg must resolve to a target input produced by chart analysis or to an explicitly configured non-structural policy target, where the applicable trading policy permits it.

If no valid target can be resolved for a leg, that leg is not automatically submitted.

### 5.2.3 Downstream Target-Reached and Profit-Protection Separation

Target achievement and position protection are separate lifecycle concepts.

```text
TARGET_REACHED
    ↓
NOTIFICATION / ALERT
    ↓
USER OR FUTURE POSITION MANAGER
```

The current monitor phase is notification-only. `TARGET_REACHED` does not imply that a position was closed, partially closed, or that a stop was moved.

Future trade-management policies may react to a reached target, for example:

```text
T1_REACHED
    ├─ close Leg 1
    └─ protect remaining legs

T2_REACHED
    ├─ close Leg 2
    └─ protect remaining runner
```

Such actions are configuration/execution-policy concerns, not canonical structural semantics.

A future profit-protection policy may define transitions such as:

```text
BREAK_EVEN
PROFIT_LOCK_AT_PREVIOUS_TARGET
TRAILING_PROTECTION
```

No one of these is currently a universal methodology rule. In particular, `BREAK_EVEN` must not be treated as a canonical fallback target. It is a stop-management action.

### 5.2.4 Downstream Target Notification Contract — Current Phase

The monitor may emit a notification when the market price reaches a configured active target:

```text
ACTIVE TARGET
    ↓
PRICE REACHES TARGET
    ↓
TARGET_REACHED
    ↓
TARGET_NOTIFICATION_SENT
```

The notification should identify at minimum:

- symbol/instrument;
- direction;
- target identifier;
- target type/provenance;
- target price;
- event timestamp.

The monitor must not claim `POSITION_CLOSED` unless a later platform component has independently verified that broker/user action.

The target event is mechanical/execution observability and must not manufacture BOS, CHoCH, POI failure, or any structural state.

### RR gating

Where required by the configurable execution layer policy:

```text
Projected_RR_to_Primary_Target >= Configured_Minimum_RR
```

RR gating is a configurable trading policy, not a universal structural requirement. This is an entry/setup gate, not a target-location rule.

### Counter-trend / pullback execution

Counter-trend execution may use IDM/Engineering Liquidity sweep + valid POI + closed canonical reversal. Its expected structural destination may be an unmitigated parent Decisional POI / Extreme POI (OF_CONFIRMED / Valid OB), but no universal hard TP coordinate is canonicalized here.

IRL is not a canonical TP category. Internal liquidity, Engineering Liquidity, internal OF/OB, and Minor IDM remain context/execution objects rather than mandatory TP coordinates.

No fixed partial-TP percentage, break-even trigger, or trailing algorithm is canonicalized here.

## 5.3 Pending-Order and Open-Position Lifecycle

### 5.3.1 Pending Order Invalidation

```
ORDER_FLOW_FAILED / ORDER_BLOCK_FAILED
        ↓
associated pending order
        ↓
PENDING_ORDER_CANCELLED
```

```
VALID_BOS
        ↓
previous Trading Range dependent orders
        ↓
EXPIRED_CANCELLED
```

```
CHoCH_CONFIRMED
        ↓
pending orders dependent on invalidated regime
        ↓
PENDING_ORDER_CANCELLED
```

CHoCH_ELIGIBLE alone does not automatically cancel pending orders.

A historical Origin OB (latent POI) may remain as a historical object after a parent OF lifecycle transition when its own validity remains canonical.

### 5.3.2 Zone Failure

Bullish zone failure:

```
Close < lower_zone_boundary
```

Bearish zone failure:

```
Close > upper_zone_boundary
```

Wick penetration alone is not zone failure unless a canonical execution rule explicitly says otherwise.

### 5.3.3 Open Position Exit Separation

Broker-side stop and target events remain mechanical execution events:

```
OPEN POSITION
   ├── TARGET_HIT
   └── STOP_LOSS_TOUCH
```

Do not synthesize a market close merely because a POI failed, a zone failed, BOS occurred, or CHoCH occurred.

```
EXECUTION_STOPPED_OUT
≠ POI_FAILED
≠ ORDER_FLOW_FAILED
≠ ORDER_BLOCK_FAILED
≠ VALID_BOS
≠ CHoCH_CONFIRMED
```

### 5.3.4 Emergency Structural Kill-Switch

“Kill-Switch” is project execution-control terminology, not an independent structural entity.

```
CHoCH_CONFIRMED ↛ mandatory MARKET_CLOSE_ON_CHOCH
ORDER_FLOW_FAILED ↛ mandatory MARKET_CLOSE
ORDER_BLOCK_FAILED ↛ mandatory MARKET_CLOSE
```

No authoritative forced market-close behavior is canonicalized solely from these events.

### 5.3.5 Pending vs Open Position

Pending-order premise invalidation terminates the pending order. An already-open position continues its own execution lifecycle until a mechanical target/stop event or a separately authorized exit occurs.

```
PENDING ORDER INVALIDATION → CANCEL
OPEN POSITION → CONTINUE LIFECYCLE
```

### 5.3.6 G1 — OHLC vs Intrabar Sequence

Absolute invariant:

```
OHLC ≠ INTRABAR_SEQUENCE
```

Intrabar execution events may include:

```
ORDER_TRIGGERED
STOP_TOUCH
TARGET_TOUCH
```

Candle-close structural/execution events include:

```
ORDER_FLOW_FAILED
ORDER_BLOCK_FAILED
VALID_BOS
CHoCH_CONFIRMED
```

If STOP_TOUCH and TARGET_TOUCH are both reachable inside one OHLC candle, the methodology cannot deterministically establish which occurred first. That requires lower-timeframe/tick data or broker execution records. Do not invent microsequence from OHLC.

## 5.4 Risk Invariants

```
RISK CONSUMES STRUCTURE
RISK DOES NOT CREATE STRUCTURE

POI INVALIDATION ≠ STRUCTURAL INVALIDATION
STRUCTURAL INVALIDATION ≠ RISK STOP
RISK STOP ≠ EXECUTION_STOPPED_OUT
TARGET_HIT ≠ VALID_BOS
CHoCH_CONFIRMED ↛ mandatory MARKET_CLOSE_ON_CHOCH
```

## 5.5 Scoring boundary — IMPLEMENTATION-OWNED

The mapper exposes a weighted quality score, but the weights, tier thresholds, penalty arithmetic, and liquidity-quality values are implementation behavior rather than independent SMC methodology.

`07_risk.md` does not own those numeric values. The single detailed implementation mapping is maintained in `08_implementation.md`, alongside the executable risk-quality calculation.

This document therefore records only the ownership boundary:

```
RISK METHODOLOGY
    ↓
consumes canonical structural/execution state
    ↓
08_implementation.md / mapper implementation
    ↓
concrete scoring arithmetic
```

No risk score, tier, or implementation penalty may manufacture or validate IDM, CONFIRMED_STRUCTURAL_SWING, Protected Structural Extreme, VALID_BOS, CHoCH_CONFIRMED, Trading Range, or POI ontology.

## 5.6 Architectural Separation

Risk remains a downstream consumer of structural and execution state. No risk rule may manufacture IDM, CONFIRMED_STRUCTURAL_SWING, Protected Structural Extreme, VALID_BOS, CHoCH_CONFIRMED, Trading Range, or POI ontology.

The canonical separation:

```
STRUCTURE → EXECUTION → RISK
```