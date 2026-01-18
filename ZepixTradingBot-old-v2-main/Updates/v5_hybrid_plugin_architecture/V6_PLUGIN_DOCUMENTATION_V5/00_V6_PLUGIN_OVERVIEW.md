# V6 Price Action Plugin - V5 Architecture Overview

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Pine Script Source**: `Signals_and_Overlays_V6_Enhanced_Build.pine` (1683 lines)  
**Plugin Implementations**: `v6_price_action_5m`, `v6_price_action_15m`, `v6_price_action_1h`

---

## Executive Summary

The V6 Price Action Plugin system implements the Signals and Overlays V6 Enhanced trading system within the V5 Hybrid Plugin Architecture. Unlike V3's single combined plugin, V6 uses three timeframe-specific plugins (5m, 15m, 1H) that each specialize in momentum-based price action trading with trendline confirmation.

### Key Characteristics

| Attribute | Value |
|-----------|-------|
| Pine Script Version | v6 (indicator) |
| Total Lines | 1683 |
| Alert Types | 14 (entry, exit, trend pulse, momentum) |
| Plugin Count | 3 (5m, 15m, 1H) |
| Multi-Timeframe Support | 6 timeframes (1m, 5m, 15m, 1H, 4H, 1D) |
| Order System | Dual Orders (Order A + Order B) |

---

## 1. Pine Script Architecture Overview

### 1.1 Core Components

The V6 Pine Script is organized into distinct feature groups:

```pine
// GROUP 1: TRENDLINE INTEGRATION (Lines 56-62)
// GROUP 2: TREND PULSE (MULTI-TIMEFRAME ANALYSIS) (Lines 64-72)
// GROUP 3: ADX MOMENTUM FILTER (Lines 74-82)
// GROUP 4: CONFIDENCE SCORING (Lines 84-92)
// GROUP 5: BREAKOUT/BREAKDOWN DETECTION (Lines 94-102)
// GROUP 6: SCREENER INTEGRATION (Lines 104-112)
```

### 1.2 Feature Groups

**Group 1: Trendline Integration**
- Pivot-based trendline detection
- Trendline breakout confirmation
- Retest type (Wicks/Body)
- Projection sensitivity (25/50/75)

**Group 2: Trend Pulse (MTF Analysis)**
- 6-timeframe trend tracking
- Trend change detection
- Alignment scoring
- Change detail reporting

**Group 3: ADX Momentum Filter**
- ADX-based momentum confirmation
- Trend strength validation
- Entry filtering

**Group 4: Confidence Scoring**
- Multi-factor confidence calculation
- HIGH/MEDIUM/LOW classification
- Timeframe alignment weighting

**Group 5: Breakout/Breakdown Detection**
- Price action breakout detection
- Volume confirmation
- Momentum validation

**Group 6: Screener Integration**
- Full bullish/bearish alignment
- Multi-indicator confirmation
- Signal aggregation

---

## 2. V5 Plugin Architecture Integration

### 2.1 Three-Plugin Structure

Unlike V3's single combined plugin, V6 uses three specialized plugins:

```
V6 Plugin System
├── v6_price_action_5m   (Scalping - LOGIC1)
├── v6_price_action_15m  (Intraday - LOGIC2)
└── v6_price_action_1h   (Swing - LOGIC3)
```

### 2.2 Plugin Class Structure

```python
class V6PriceAction5mPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    V6 5-Minute Momentum Plugin
    
    Strategy Profile:
    - Type: Momentum Trading
    - Goal: Catch intraday breakouts and rapid moves
    - Risk Multiplier: 0.5x (conservative for scalping)
    """

class V6PriceAction15mPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    V6 15-Minute Intraday Plugin
    
    Strategy Profile:
    - Type: Intraday Momentum
    - Goal: Capture medium-term price action moves
    - Risk Multiplier: 1.0x (standard)
    """

class V6PriceAction1hPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    V6 1-Hour Swing Plugin
    
    Strategy Profile:
    - Type: Swing Trading
    - Goal: Ride larger trend moves
    - Risk Multiplier: 1.5x (higher conviction)
    """
```

### 2.3 Interface Implementations

| Interface | Purpose | Key Methods |
|-----------|---------|-------------|
| `ISignalProcessor` | Process incoming alerts | `process_signal()`, `can_process_signal()` |
| `IOrderExecutor` | Execute trade orders | `execute_order()`, `modify_order()`, `close_order()` |

### 2.4 ServiceAPI Integration

```python
async def process_signal_via_service_api(self, signal: Dict[str, Any]):
    # Validate via TrendManager (Pine Supremacy)
    if not self._validate_via_trend_manager(signal):
        return None
    
    # Create dual orders via ServiceAPI
    result = await self._service_api.create_dual_orders(
        signal, order_a_config, order_b_config
    )
    
    # Send notification via ServiceAPI
    await self._service_api.send_telegram_notification(...)
```

---

## 3. Alert Types Summary

### 3.1 Entry Alerts (6)

| # | Alert Type | Pine Script Lines | Trigger Conditions |
|---|------------|-------------------|-------------------|
| 1 | Breakout Entry | 800-850 | Trendline break + Volume + ADX |
| 2 | Breakdown Entry | 855-905 | Trendline break + Volume + ADX |
| 3 | Momentum Entry Bull | 910-960 | ADX > 25 + Trend alignment |
| 4 | Momentum Entry Bear | 965-1015 | ADX > 25 + Trend alignment |
| 5 | Screener Full Bull | 1020-1070 | All indicators aligned bullish |
| 6 | Screener Full Bear | 1075-1125 | All indicators aligned bearish |

### 3.2 Exit Alerts (2)

| # | Alert Type | Pine Script Lines | Trigger Conditions |
|---|------------|-------------------|-------------------|
| 7 | Bullish Exit | 1130-1160 | Trend reversal + Momentum loss |
| 8 | Bearish Exit | 1165-1195 | Trend reversal + Momentum loss |

### 3.3 Trend Pulse Alerts (4)

| # | Alert Type | Pine Script Lines | Purpose |
|---|------------|-------------------|---------|
| 9 | Trend Pulse Bull | 1200-1250 | MTF trend change to bullish |
| 10 | Trend Pulse Bear | 1255-1305 | MTF trend change to bearish |
| 11 | Trend Pulse Mixed | 1310-1360 | Partial MTF alignment |
| 12 | Trend Pulse Neutral | 1365-1415 | No clear trend |

### 3.4 Momentum Alerts (2)

| # | Alert Type | Pine Script Lines | Purpose |
|---|------------|-------------------|---------|
| 13 | Momentum Surge | 1420-1470 | Strong momentum detected |
| 14 | Momentum Fade | 1475-1525 | Momentum weakening |

---

## 4. Alert Payload Format

### 4.1 Entry Alert JSON Structure

```json
{
  "type": "entry_v6",
  "signal_type": "Breakout_Entry",
  "symbol": "EURUSD",
  "direction": "buy",
  "tf": "15",
  "price": 1.08500,
  "confidence": "HIGH",
  "adx_value": 32.5,
  "trendline_break": true,
  "mtf_trends": "1,1,1,1,1,1",
  "aligned_count": 6,
  "sl_price": 1.08200,
  "tp1_price": 1.08800,
  "tp2_price": 1.09100,
  "volume_confirmed": true
}
```

### 4.2 Trend Pulse Alert JSON Structure

```json
{
  "type": "trend_pulse_v6",
  "signal_type": "Trend_Pulse_Bull",
  "symbol": "EURUSD",
  "tf": "15",
  "price": 1.08500,
  "current_trends": "1,1,1,1,1,1",
  "previous_trends": "1,1,1,-1,-1,-1",
  "changed_timeframes": "1H,4H,1D",
  "change_details": "1H: BEAR→BULL, 4H: BEAR→BULL, 1D: BEAR→BULL",
  "aligned_count": 6,
  "confidence": "HIGH",
  "message": "Bullish trend alignment on 6/6 timeframes"
}
```

---

## 5. Plugin Routing Logic

### 5.1 Timeframe-to-Plugin Routing

```python
# src/core/plugin_router.py
def _get_v6_plugin_for_timeframe(self, tf: str) -> str:
    """Route V6 alert to appropriate plugin based on timeframe."""
    if tf == "5":
        return "v6_price_action_5m"
    elif tf == "15":
        return "v6_price_action_15m"
    elif tf in ["60", "240"]:
        return "v6_price_action_1h"
    else:
        return "v6_price_action_15m"  # Default
```

### 5.2 Plugin Risk Profiles

| Plugin | Timeframe | Risk Multiplier | Base Lot |
|--------|-----------|-----------------|----------|
| v6_price_action_5m | 5m | 0.5x | 0.05 |
| v6_price_action_15m | 15m | 1.0x | 0.10 |
| v6_price_action_1h | 1H/4H | 1.5x | 0.15 |

---

## 6. Trendline Integration

### 6.1 Trendline Detection (Lines 56-62)

```pine
enableTrendline = input.bool(true, "Enable Trendline Confirmation")
trendlinePeriod = input.int(10, "Trendline Period", minval=5, maxval=50)
trendlineRetestType = input.string("Wicks", "Retest Type", options=["Wicks", "Body"])
trendlineSensitivity = input.string("25", "Trendline Projection Sensitivity", options=["25", "50", "75"])
```

### 6.2 Trendline Breakout Confirmation

```pine
// Bullish trendline breakout
bool trendlineBreakBull = enableTrendline and 
    close > upperTrendline and 
    close[1] <= upperTrendline[1] and
    volume > ta.sma(volume, 20)

// Bearish trendline breakdown
bool trendlineBreakBear = enableTrendline and 
    close < lowerTrendline and 
    close[1] >= lowerTrendline[1] and
    volume > ta.sma(volume, 20)
```

---

## 7. Confidence Scoring System

### 7.1 Confidence Calculation

```pine
// Calculate confidence based on multiple factors
getConfidence(alignedCount, adxValue, volumeOK) =>
    score = 0
    
    // MTF Alignment (max 40 points)
    score += alignedCount * 6.67  // 6 TFs × 6.67 = 40
    
    // ADX Strength (max 30 points)
    if adxValue > 40
        score += 30
    else if adxValue > 30
        score += 20
    else if adxValue > 25
        score += 10
    
    // Volume Confirmation (max 30 points)
    if volumeOK
        score += 30
    
    // Classify
    if score >= 70
        "HIGH"
    else if score >= 40
        "MEDIUM"
    else
        "LOW"
```

### 7.2 Confidence Thresholds

| Confidence | Score Range | Entry Allowed |
|------------|-------------|---------------|
| HIGH | 70-100 | Yes (full position) |
| MEDIUM | 40-69 | Yes (reduced position) |
| LOW | 0-39 | No (filtered out) |

---

## 8. Dual Order System

### 8.1 Order A Configuration

- **SL Type**: V6 Calculated SL (from Pine Script)
- **Trailing**: Enabled (starts at 50% of SL in profit)
- **TP Target**: 2:1 Risk-Reward ratio
- **Lot Split**: 50% of total position

### 8.2 Order B Configuration

- **SL Type**: Fixed $10 Risk SL
- **Trailing**: Disabled
- **TP Target**: None (uses profit booking chain)
- **Lot Split**: 50% of total position

---

## 9. Configuration Parameters

### 9.1 Plugin Configuration (5m)

```json
{
  "plugin_id": "v6_price_action_5m",
  "enabled": true,
  "shadow_mode": true,
  "settings": {
    "min_confidence": "MEDIUM",
    "min_adx": 25,
    "require_trendline_break": true,
    "require_volume_confirmation": true
  },
  "risk_management": {
    "risk_multiplier": 0.5,
    "base_lot": 0.05,
    "max_lot": 0.10
  }
}
```

### 9.2 Plugin Configuration (15m)

```json
{
  "plugin_id": "v6_price_action_15m",
  "enabled": true,
  "shadow_mode": false,
  "settings": {
    "min_confidence": "MEDIUM",
    "min_adx": 25,
    "require_trendline_break": true,
    "require_volume_confirmation": true
  },
  "risk_management": {
    "risk_multiplier": 1.0,
    "base_lot": 0.10,
    "max_lot": 0.20
  }
}
```

### 9.3 Plugin Configuration (1H)

```json
{
  "plugin_id": "v6_price_action_1h",
  "enabled": true,
  "shadow_mode": false,
  "settings": {
    "min_confidence": "MEDIUM",
    "min_adx": 20,
    "require_trendline_break": false,
    "require_volume_confirmation": true
  },
  "risk_management": {
    "risk_multiplier": 1.5,
    "base_lot": 0.15,
    "max_lot": 0.30
  }
}
```

---

## 10. Related Documentation

| Document | Description |
|----------|-------------|
| `01_V6_PINE_LOGIC_BREAKDOWN.md` | Complete Pine Script analysis |
| `02_V6_BOT_FEATURES_39.md` | All 39 features mapped |
| `03_V6_PLUGIN_IMPLEMENTATION_PLAN.md` | Implementation guide |
| `04_V6_ALERT_PROCESSING.md` | Alert flow documentation |
| `05_V6_TESTING_STRATEGY.md` | Testing approach |
| `06_V6_CONFLICT_RESOLUTION.md` | Conflict handling |
| `07_V6_DEPLOYMENT_GUIDE.md` | Deployment instructions |
| `08_V6_CROSS_VERIFICATION_REPORT.md` | Accuracy verification |

---

## 11. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-18 | Initial V5-aligned documentation |

---

**Document Status**: COMPLETE  
**Pine Script Coverage**: 100%  
**V5 Architecture Compliance**: VERIFIED
