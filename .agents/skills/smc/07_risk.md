# 07 — RISK

**Role:** Risk, position sizing, trade management, and execution-lifecycle policy.

**Authority boundary:** Risk is downstream from canonical structural validation. It consumes canonical structural/execution state and must never create, validate, reinterpret, or redefine structural truth.

## 5.1 Structural Stop-Loss Placement

### Tier 1 — Structural / Zone Boundary Stop

Conservative stop placement is beyond the furthest relevant boundary of the parent ELIGIBLE_ORDER_FLOW / Validated Order Block according to the applicable execution module.

A stop placement or stop touch does not itself create structural truth:

```
EXECUTION_STOPPED_OUT ≠ POI_PREMISE_INVALIDATED
EXECUTION_STOPPED_OUT ≠ ZONE_FAILURE
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

If `P` is unavailable, the setup may be analyzed, but an automatic broker order must not be submitted.

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

Canonical SMC methodology does not prescribe a universal target-selection priority or a universal target-selection winner. It provides structural/liquidity chart facts that downstream implementation may use as target inputs.

The risk and trade-management layer operates under the strict unidirectional pipeline:

```text
CANONICAL TARGET CANDIDATES
        OR
EXPLICIT NON-STRUCTURAL POLICY TARGET
        ↓
CONFIGURED TARGET POLICY
        ↓
RESOLVED TARGET
        ↓
RR EVALUATION
```

LTF target selection priority, countertrend target-coordinate selection, fixed-R target generation, multi-leg allocation, and break-even/profit-lock/trailing actions are implementation/trading-policy concerns, not canonical SMC rules.

### Pro-trend chart-analysis target candidates

The confirmed external range extreme is the canonical pro-trend target candidate / structural input where the applicable execution module requires it:

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
PRO-TREND TARGET CANDIDATE
        ↓
TARGET POLICY RESOLUTION
        ↓
RESOLVED TRADE TARGET
```

The source repeatedly uses the external liquidity / external range extreme as the final pro-trend target candidate for direct execution, resolved to a trade target by downstream policy.

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
NO_RESOLVED_TARGET → NO_SYNTHETIC_TARGET → NO_AUTOMATIC_TP_SUBMISSION
```

A setup with no canonical structural/liquidity target candidate may still resolve a valid trade target if an explicitly configured non-structural policy target (such as fixed-R, where permitted by trading policy) is defined. However, if no target can be resolved (`NO_RESOLVED_TARGET`), no synthetic target may be manufactured merely to satisfy an RR gate, and no automatic TP submission may occur.

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
Projected_RR_to_Resolved_Target >= Configured_Minimum_RR
```

RR gating is a configurable trading policy, not a universal structural requirement. This is an entry/setup gate, not a target-location rule. The RR gate consumes a resolved target object (`RESOLVED TARGET`) only after the configured target policy resolves one. If no valid target is resolved (`NO_RESOLVED_TARGET`), no target may be manufactured merely to satisfy the RR gate.

### Counter-trend / pullback execution

Counter-trend execution may use IDM/Engineering Liquidity sweep + valid POI + closed canonical reversal. Its expected structural destination may be an unmitigated parent Decisional POI / Extreme POI (ELIGIBLE_ORDER_FLOW / Validated Order Block), but no universal hard TP coordinate is canonicalized here.

IRL is not a canonical TP category. Internal liquidity, Engineering Liquidity, internal OF/OB, and Minor IDM remain context/execution objects rather than mandatory TP coordinates.

No fixed partial-TP percentage, break-even trigger, or trailing algorithm is canonicalized here.

## 5.3 Pending-Order and Open-Position Lifecycle

### 5.3.1 Pending Order Invalidation

```text
CANONICAL EXECUTION / POI PREMISE INVALIDATION
        ↓
ASSOCIATED PENDING ORDER
        ↓
PENDING_ORDER_CANCELLED
```

Pending-order premise invalidation occurs when the underlying execution setup condition or POI premise is invalidated. This is an execution/order-lifecycle consequence, not a new structural event.

```text
VALID_BOS
        ↓
previous Trading Range dependent orders
        ↓
EXPIRED_CANCELLED
```

```text
CHoCH_CONFIRMED
        ↓
pending orders dependent on invalidated regime
        ↓
PENDING_ORDER_CANCELLED
```

CHoCH_ELIGIBLE alone does not automatically cancel pending orders. `CHoCH_CONFIRMED` produces cancellation only for pending orders dependent on the invalidated regime.

A historical Origin Order Block (latent POI) may remain as a historical object after a parent OF lifecycle transition when its own validity remains canonical.

### 5.3.2 Zone Failure

Zone failure is strictly an execution/risk zone-failure rule, clearly separate from canonical POI failure, CHoCH, or structural break mechanics:

```text
ZONE_FAILURE
≠ POI_FAILURE
≠ STRUCTURAL_FAILURE
≠ BOS
≠ CHoCH
```

Bullish zone failure (execution/risk rule):

```text
Close < lower_zone_boundary
```

Bearish zone failure (execution/risk rule):

```text
Close > upper_zone_boundary
```

Wick penetration alone is not zone failure unless a canonical execution rule explicitly says otherwise. The exact candle-close boundary threshold is an execution/risk parameter and is not claimed as a separate canonical True SMC structural rule.

### 5.3.3 Open Position Exit Separation

Broker-side stop and target events remain mechanical execution events:

```text
OPEN POSITION
   ├── TARGET_HIT
   └── STOP_LOSS_TOUCH
```

Do not synthesize a market close merely because a POI failed, a zone failed, BOS occurred, or CHoCH occurred.

```text
EXECUTION_STOPPED_OUT
≠ POI_PREMISE_INVALIDATED
≠ ZONE_FAILURE
≠ VALID_BOS
≠ CHoCH_CONFIRMED
```

### 5.3.4 Emergency Structural Kill-Switch

“Kill-Switch” is project execution-control terminology, not an independent structural entity.

```text
CHoCH_CONFIRMED ↛ mandatory MARKET_CLOSE_ON_CHOCH
POI_PREMISE_INVALIDATED ↛ mandatory MARKET_CLOSE
ZONE_FAILURE ↛ mandatory MARKET_CLOSE
```

No authoritative forced market-close behavior is canonicalized solely from these events.

### 5.3.5 Pending vs Open Position

Pending-order premise invalidation terminates the pending order. An already-open position continues its own execution lifecycle until a mechanical target/stop event or a separately authorized exit occurs.

```text
PENDING ORDER INVALIDATION → CANCEL
OPEN POSITION → CONTINUE LIFECYCLE
```

### 5.3.6 G1 — OHLC vs Intrabar Sequence

Absolute invariant:

```text
OHLC ≠ INTRABAR_SEQUENCE
```

Intrabar execution events may include:

```text
ORDER_TRIGGERED
STOP_TOUCH
TARGET_TOUCH
```

Candle-close structural/execution events include:

```text
POI_PREMISE_INVALIDATION
ZONE_FAILURE
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

## 5.5 Architectural Separation

Risk remains a downstream consumer of structural and execution state. No risk rule may manufacture IDM, CONFIRMED_STRUCTURAL_SWING, Protected Structural Extreme, VALID_BOS, CHoCH_CONFIRMED, Trading Range, or POI ontology.

The canonical separation:

```
STRUCTURE → EXECUTION → RISK
```