# V3 Combined Logic Plugin - V5 Architecture Overview

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Pine Script Source**: `ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine` (1934 lines)  
**Plugin Implementation**: `src/logic_plugins/v3_combined/plugin.py`

---

## Executive Summary

The V3 Combined Logic Plugin implements the complete ZEPIX ULTIMATE BOT v3.0 trading system within the V5 Hybrid Plugin Architecture. This plugin processes 12 distinct signal types from TradingView Pine Script alerts and executes trades through a sophisticated 5-layer decision framework.

### Key Characteristics

| Attribute | Value |
|-----------|-------|
| Pine Script Version | v6 (indicator) |
| Total Lines | 1934 |
| Signal Types | 12 (7 entry, 2 exit, 2 info, 1 bonus) |
| Architecture Layers | 5 (SMC 40%, Consensus 25%, Breakout 20%, Risk 10%, Conflict 5%) |
| Multi-Timeframe Support | 6 timeframes (1m, 5m, 15m, 1H, 4H, 1D) |
| Order System | Dual Orders (Order A + Order B) |

---

## 1. Pine Script Architecture Overview

### 1.1 5-Layer Weighted Architecture

The V3 Pine Script implements a 5-layer decision system with explicit weights defined at lines 28-32:

```pine
// Weight Constants for 5-Layer Architecture (Lines 28-32)
float WEIGHT_SMC = 0.40        // Smart Money Structure (40%)
float WEIGHT_CONSENSUS = 0.25  // Consensus Engine (25%)
float WEIGHT_BREAKOUT = 0.20   // Breakout System (20%)
float WEIGHT_RISK = 0.10       // Risk Management (10%)
float WEIGHT_CONFLICT = 0.05   // Conflict Resolution (5%)
```

### 1.2 Layer Responsibilities

**Layer 1: Smart Money Concepts (SMC) - 40%**
- Order Block Detection (Bullish/Bearish)
- Fair Value Gap (FVG) Identification
- Liquidity Sweep Detection
- Equal Highs/Lows Analysis
- Break of Structure (BOS) Detection

**Layer 2: Consensus Engine - 25%**
- 9-Indicator Voting System
- ZLEMA + VIDYA Hybrid Calculation
- Consensus Score (0-9 scale)
- Trend Direction Confirmation

**Layer 3: Breakout System - 20%**
- Trend Line Break Detection
- Consolidation Breakout
- Volume Confirmation
- ADX Momentum Filter

**Layer 4: Risk Management - 10%**
- Position Sizing (0.2x - 1.0x multiplier)
- Smart Stop Loss Calculation
- Take Profit Targets (TP1, TP2)
- ATR-Based Volatility Adjustment

**Layer 5: Conflict Resolution - 5%**
- Signal Priority Matrix
- Cooldown Period Management
- Duplicate Signal Prevention
- Multi-Timeframe Alignment Check

---

## 2. V5 Plugin Architecture Integration

### 2.1 Plugin Class Structure

```python
class V3CombinedPlugin(
    BaseLogicPlugin,
    ISignalProcessor,
    IOrderExecutor,
    IReentryCapable,
    IDualOrderCapable,
    IProfitBookingCapable,
    IAutonomousCapable,
    IDatabaseCapable
):
```

### 2.2 Interface Implementations

| Interface | Purpose | Key Methods |
|-----------|---------|-------------|
| `ISignalProcessor` | Process incoming alerts | `process_signal()`, `can_process_signal()` |
| `IOrderExecutor` | Execute trade orders | `execute_order()`, `modify_order()`, `close_order()` |
| `IReentryCapable` | SL Hunt Recovery | `on_sl_hit()`, `on_recovery_signal()` |
| `IDualOrderCapable` | Dual Order System | `create_dual_orders()`, `get_order_a_config()` |
| `IProfitBookingCapable` | Profit Chain Management | `create_profit_chain()`, `on_profit_target_hit()` |
| `IAutonomousCapable` | Safety & Protection | `check_recovery_allowed()`, `activate_reverse_shield()` |
| `IDatabaseCapable` | Trade Persistence | `save_trade()`, `get_trades()` |

### 2.3 ServiceAPI Integration

The plugin uses ServiceAPI for all core operations:

```python
async def process_signal_via_service_api(self, signal: Dict[str, Any]):
    # Check safety via ServiceAPI
    safety_check = await self._service_api.check_safety(self.plugin_id)
    
    # Create dual orders via ServiceAPI
    result = await self._service_api.create_dual_orders(
        signal, order_a_config, order_b_config
    )
    
    # Create profit chain via ServiceAPI
    await self._service_api.create_profit_chain(...)
    
    # Send notification via ServiceAPI
    await self._service_api.send_telegram_notification(...)
```

---

## 3. Signal Types Summary

### 3.1 Entry Signals (7)

| # | Signal Name | Pine Script Lines | Trigger Conditions |
|---|-------------|-------------------|-------------------|
| 1 | Institutional Launchpad | 1204-1208 | SMC + Consensus + Breakout alignment |
| 2 | Liquidity Trap Reversal | 1210-1214 | Sweep + OB + Volume confirmation |
| 3 | Momentum Breakout | 1216-1220 | Trend break + Volume + ADX > 25 |
| 4 | Mitigation Test Entry | 1222-1226 | Price in OB + Consensus alignment |
| 7 | Golden Pocket Flip | 1234-1238 | Fib retracement + OB confluence |
| 9 | Screener Full Bullish | 1242-1244 | All 9 indicators bullish |
| 10 | Screener Full Bearish | 1246-1248 | All 9 indicators bearish |

### 3.2 Exit Signals (2)

| # | Signal Name | Pine Script Lines | Trigger Conditions |
|---|-------------|-------------------|-------------------|
| 5 | Bullish Exit | 1228-1230 | Consensus flip + Volume divergence |
| 6 | Bearish Exit | 1230-1232 | Consensus flip + Volume divergence |

### 3.3 Info Signals (2)

| # | Signal Name | Pine Script Lines | Purpose |
|---|-------------|-------------------|---------|
| 8 | Volatility Squeeze | 1240-1241 | Alert for low volatility period |
| 11 | Trend Pulse | 1802-1806 | MTF trend change notification |

### 3.4 Bonus Signal (1)

| # | Signal Name | Pine Script Lines | Trigger Conditions |
|---|-------------|-------------------|-------------------|
| 12 | Sideways Breakout | 1808-1818 | Squeeze exit + ZLEMA trend flip |

---

## 4. Alert Payload Format

### 4.1 Entry Alert JSON Structure

```json
{
  "type": "entry_v3",
  "signal_type": "Institutional_Launchpad",
  "symbol": "EURUSD",
  "direction": "buy",
  "tf": "15",
  "price": 1.08500,
  "consensus_score": 7,
  "sl_price": 1.08200,
  "tp1_price": 1.08800,
  "tp2_price": 1.09100,
  "mtf_trends": "1,1,1,1,1,1",
  "market_trend": 1,
  "volume_delta_ratio": 1.25,
  "price_in_ob": true,
  "full_alignment": true,
  "position_multiplier": 0.8
}
```

### 4.2 Trend Pulse Alert JSON Structure

```json
{
  "type": "trend_pulse_v3",
  "signal_type": "Trend_Pulse",
  "symbol": "EURUSD",
  "tf": "15",
  "price": 1.08500,
  "current_trends": "1,1,1,1,1,1",
  "previous_trends": "1,1,1,-1,-1,-1",
  "changed_timeframes": "1H,4H,1D",
  "change_details": "1H: BEAR→BULL, 4H: BEAR→BULL, 1D: BEAR→BULL",
  "trend_labels": "1m,5m,15m,1H,4H,1D",
  "market_trend": 1,
  "consensus_score": 7,
  "message": "Trend change detected on: 1H,4H,1D"
}
```

---

## 5. Bot Routing Logic

### 5.1 Signal-to-Logic Routing Matrix

```python
def _route_to_logic(self, alert: ZepixV3Alert) -> str:
    # PRIORITY 1: Signal type overrides
    if alert.signal_type in ["Screener_Full_Bullish", "Screener_Full_Bearish"]:
        return "LOGIC3"  # Always swing
    
    if alert.signal_type == "Golden_Pocket_Flip" and alert.tf in ["60", "240"]:
        return "LOGIC3"
    
    # PRIORITY 2: Timeframe routing
    if alert.tf == "5":
        return "LOGIC1"  # Scalping
    elif alert.tf == "15":
        return "LOGIC2"  # Intraday (Default)
    elif alert.tf in ["60", "240"]:
        return "LOGIC3"  # Swing
    
    return "LOGIC2"  # DEFAULT
```

### 5.2 Logic Multipliers

| Logic | Timeframe | Risk Multiplier |
|-------|-----------|-----------------|
| LOGIC1 | 5m | 0.5x |
| LOGIC2 | 15m | 1.0x |
| LOGIC3 | 1H/4H | 1.5x |

---

## 6. Dual Order System

### 6.1 Order A Configuration (TP Trail)

- **SL Type**: V3 Smart SL (from Pine Script)
- **Trailing**: Enabled (starts at 50% of SL in profit)
- **TP Target**: 2:1 Risk-Reward ratio
- **Lot Split**: 50% of total position

### 6.2 Order B Configuration (Profit Trail)

- **SL Type**: Fixed $10 Risk SL
- **Trailing**: Disabled
- **TP Target**: None (uses profit booking chain)
- **Lot Split**: 50% of total position

---

## 7. Configuration Parameters

### 7.1 Plugin Configuration

```json
{
  "plugin_id": "v3_combined",
  "enabled": true,
  "shadow_mode": false,
  "settings": {
    "bypass_trend_check_for_v3_entries": true,
    "mtf_pillars_only": ["15m", "1h", "4h", "1d"],
    "min_consensus_score": 5,
    "aggressive_reversal_signals": [
      "Liquidity_Trap_Reversal",
      "Screener_Full_Bullish",
      "Screener_Full_Bearish"
    ],
    "conservative_exit_signals": [
      "Bullish_Exit",
      "Bearish_Exit"
    ]
  }
}
```

---

## 8. Related Documentation

| Document | Description |
|----------|-------------|
| `01_V3_PINE_LOGIC_BREAKDOWN.md` | Complete Pine Script analysis |
| `02_V3_BOT_FEATURES_39.md` | All 39 features mapped |
| `03_V3_PLUGIN_IMPLEMENTATION_PLAN.md` | Implementation guide |
| `04_V3_ALERT_PROCESSING.md` | Alert flow documentation |
| `05_V3_TESTING_STRATEGY.md` | Testing approach |
| `06_V3_CONFLICT_RESOLUTION.md` | Conflict handling |
| `07_V3_DEPLOYMENT_GUIDE.md` | Deployment instructions |
| `08_V3_CROSS_VERIFICATION_REPORT.md` | Accuracy verification |

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-18 | Initial V5-aligned documentation |

---

**Document Status**: COMPLETE  
**Pine Script Coverage**: 100%  
**V5 Architecture Compliance**: VERIFIED
