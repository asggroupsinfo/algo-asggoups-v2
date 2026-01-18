# V6 Price Action Plugin - 39 Features Complete Mapping

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Pine Script Source**: `Signals_and_Overlays_V6_Enhanced_Build.pine` (1683 lines)  
**Plugin Implementations**: `v6_price_action_5m`, `v6_price_action_15m`, `v6_price_action_1h`

---

## Feature Categories Overview

| Category | Feature Count | Coverage |
|----------|---------------|----------|
| Signal Processing | 14 | 100% |
| Trendline System | 5 | 100% |
| MTF Analysis | 5 | 100% |
| Confidence Scoring | 4 | 100% |
| Risk Management | 5 | 100% |
| Order Execution | 3 | 100% |
| Telegram Integration | 2 | 100% |
| Database & Logging | 1 | 100% |
| **TOTAL** | **39** | **100%** |

---

## Category 1: Signal Processing (14 Features)

### Feature 1: Breakout Entry Bull Signal
**Pine Script Lines**: 955-1000  
**Bot Implementation**: `plugin.py` → `handle_breakout_entry()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Buy |
| Trigger | Trendline break + Volume + ADX |

**Trigger Conditions**:
- `breakoutBull OR trendlineBreakBull == true`
- `alignedBullish >= 3`
- `confidenceMeetsMinimum == true`
- `adxValue > adxThreshold`

---

### Feature 2: Breakout Entry Bear Signal
**Pine Script Lines**: 955-1000  
**Bot Implementation**: `plugin.py` → `handle_breakout_entry()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Sell |
| Trigger | Trendline break + Volume + ADX |

**Trigger Conditions**:
- `breakoutBear OR trendlineBreakBear == true`
- `alignedBearish >= 3`
- `confidenceMeetsMinimum == true`
- `adxValue > adxThreshold`

---

### Feature 3: Momentum Entry Bull Signal
**Pine Script Lines**: 1005-1050  
**Bot Implementation**: `plugin.py` → `handle_momentum_entry()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Buy |
| Trigger | ADX + EMA + MACD alignment |

**Trigger Conditions**:
- `adxValue > adxThreshold`
- `adxBullish == true`
- `emaTrendBull == true`
- `macdBullish == true`
- `volumeOK == true`
- `confidenceMeetsMinimum == true`

---

### Feature 4: Momentum Entry Bear Signal
**Pine Script Lines**: 1005-1050  
**Bot Implementation**: `plugin.py` → `handle_momentum_entry()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Sell |
| Trigger | ADX + EMA + MACD alignment |

**Trigger Conditions**:
- `adxValue > adxThreshold`
- `adxBearish == true`
- `emaTrendBear == true`
- `macdBearish == true`
- `volumeOK == true`
- `confidenceMeetsMinimum == true`

---

### Feature 5: Screener Full Bullish Signal
**Pine Script Lines**: 905-940  
**Bot Implementation**: `plugin.py` → `handle_screener_full()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Buy |
| Trigger | All indicators aligned bullish |

**Trigger Conditions**:
- `bullishIndicators >= screenerIndicatorCount`
- `alignedBullish >= minTFAlignment`
- `confidenceMeetsMinimum == true`

---

### Feature 6: Screener Full Bearish Signal
**Pine Script Lines**: 905-940  
**Bot Implementation**: `plugin.py` → `handle_screener_full()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Sell |
| Trigger | All indicators aligned bearish |

**Trigger Conditions**:
- `bearishIndicators >= screenerIndicatorCount`
- `alignedBearish >= minTFAlignment`
- `confidenceMeetsMinimum == true`

---

### Feature 7: Bullish Exit Signal
**Pine Script Lines**: 1105-1150  
**Bot Implementation**: `plugin.py` → `handle_exit_signal()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Exit |
| Direction | Close Long |
| Trigger | Trend reversal + Momentum loss |

**Trigger Conditions**:
- `macdCrossDown AND rsiOverbought` OR
- `emaTrendBear AND adxValue > adxThreshold` OR
- `stochOverbought AND macdBearish`

---

### Feature 8: Bearish Exit Signal
**Pine Script Lines**: 1105-1150  
**Bot Implementation**: `plugin.py` → `handle_exit_signal()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Exit |
| Direction | Close Short |
| Trigger | Trend reversal + Momentum gain |

**Trigger Conditions**:
- `macdCrossUp AND rsiOversold` OR
- `emaTrendBull AND adxValue > adxThreshold` OR
- `stochOversold AND macdBullish`

---

### Feature 9: Trend Pulse Bull Alert
**Pine Script Lines**: 1205-1250  
**Bot Implementation**: `plugin.py` → `handle_trend_pulse()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Info |
| Direction | N/A |
| Trigger | MTF trend change to bullish |

**Trigger Conditions**:
- `trendPulseTriggered == true`
- `alignedBullish >= minTFAlignment`

---

### Feature 10: Trend Pulse Bear Alert
**Pine Script Lines**: 1205-1250  
**Bot Implementation**: `plugin.py` → `handle_trend_pulse()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Info |
| Direction | N/A |
| Trigger | MTF trend change to bearish |

**Trigger Conditions**:
- `trendPulseTriggered == true`
- `alignedBearish >= minTFAlignment`

---

### Feature 11: Trend Pulse Mixed Alert
**Pine Script Lines**: 1205-1250  
**Bot Implementation**: `plugin.py` → `handle_trend_pulse()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Info |
| Direction | N/A |
| Trigger | Partial MTF alignment |

---

### Feature 12: Trend Pulse Neutral Alert
**Pine Script Lines**: 1205-1250  
**Bot Implementation**: `plugin.py` → `handle_trend_pulse()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Info |
| Direction | N/A |
| Trigger | No clear trend |

---

### Feature 13: Momentum Surge Alert
**Pine Script Lines**: 1455-1490  
**Bot Implementation**: `plugin.py` → `handle_momentum_alert()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Info |
| Direction | N/A |
| Trigger | Strong momentum increase |

**Trigger Conditions**:
- `adxValue > adxValue[1] * 1.2`
- `adxValue > adxThreshold`
- `volumeStrong == true`

---

### Feature 14: Momentum Fade Alert
**Pine Script Lines**: 1455-1490  
**Bot Implementation**: `plugin.py` → `handle_momentum_alert()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Info |
| Direction | N/A |
| Trigger | Momentum weakening |

**Trigger Conditions**:
- `adxValue < adxValue[1] * 0.8`
- `adxValue[1] > adxThreshold`

---

## Category 2: Trendline System (5 Features)

### Feature 15: Pivot Detection
**Pine Script Lines**: 305-340  
**Bot Implementation**: Parsed from `trendline_break` field

| Attribute | Value |
|-----------|-------|
| Period | Configurable (default 10) |
| Type | High/Low pivots |

---

### Feature 16: Trendline Calculation
**Pine Script Lines**: 345-400  
**Bot Implementation**: Calculated in Pine, used for SL adjustment

| Attribute | Value |
|-----------|-------|
| Upper | Connects pivot highs |
| Lower | Connects pivot lows |
| Projection | 25/50/75 sensitivity |

---

### Feature 17: Trendline Breakout Detection
**Pine Script Lines**: 405-450  
**Bot Implementation**: `trendline_break` field in alert

| Attribute | Value |
|-----------|-------|
| Bullish | Close above upper trendline |
| Bearish | Close below lower trendline |
| Confirmation | Volume above average |

---

### Feature 18: Trendline Retest Detection
**Pine Script Lines**: 405-450  
**Bot Implementation**: Part of entry validation

| Attribute | Value |
|-----------|-------|
| Type | Wicks or Body |
| Confirmation | Price returns to trendline |

---

### Feature 19: Trendline Visual Display
**Pine Script Lines**: 56-62  
**Bot Implementation**: N/A (chart only)

| Attribute | Value |
|-----------|-------|
| Show | Configurable |
| Fill Color | Configurable |

---

## Category 3: MTF Analysis (5 Features)

### Feature 20: 6-Timeframe Trend Tracking
**Pine Script Lines**: 505-530  
**Bot Implementation**: `mtf_trends` field parsing

| Timeframe | Index |
|-----------|-------|
| 1m | 0 |
| 5m | 1 |
| 15m | 2 |
| 1H | 3 |
| 4H | 4 |
| 1D | 5 |

---

### Feature 21: Trend Change Detection
**Pine Script Lines**: 585-630  
**Bot Implementation**: `changed_timeframes` field

| Attribute | Value |
|-----------|-------|
| Detection | Compare current vs previous |
| Output | Changed TF list |

---

### Feature 22: Alignment Counting
**Pine Script Lines**: 585-630  
**Bot Implementation**: `aligned_count` field

| Attribute | Value |
|-----------|-------|
| Bullish | Count of TFs with trend = 1 |
| Bearish | Count of TFs with trend = -1 |

---

### Feature 23: Minimum Alignment Threshold
**Pine Script Lines**: 64-72  
**Bot Implementation**: Plugin config `min_tf_alignment`

| Attribute | Value |
|-----------|-------|
| Default | 4 of 6 |
| Range | 2-6 |

---

### Feature 24: MTF String Format
**Pine Script Lines**: 585-630  
**Bot Implementation**: `_parse_mtf_trends()`

| Format | Example |
|--------|---------|
| String | "1,1,1,1,1,1" |
| Parsed | [1, 1, 1, 1, 1, 1] |

---

## Category 4: Confidence Scoring (4 Features)

### Feature 25: Confidence Score Calculation
**Pine Script Lines**: 655-700  
**Bot Implementation**: `confidence` field

| Factor | Max Points |
|--------|------------|
| MTF Alignment | 40 |
| ADX Strength | 30 |
| Volume | 30 |
| **Total** | **100** |

---

### Feature 26: Confidence Classification
**Pine Script Lines**: 705-730  
**Bot Implementation**: `_validate_confidence()`

| Level | Score Range |
|-------|-------------|
| HIGH | 70-100 |
| MEDIUM | 40-69 |
| LOW | 0-39 |

---

### Feature 27: Minimum Confidence Filter
**Pine Script Lines**: 84-92  
**Bot Implementation**: Plugin config `min_confidence`

| Setting | Allowed Entries |
|---------|-----------------|
| LOW | All |
| MEDIUM | MEDIUM + HIGH |
| HIGH | HIGH only |

---

### Feature 28: Confidence Label Display
**Pine Script Lines**: 84-92  
**Bot Implementation**: N/A (chart only)

---

## Category 5: Risk Management (5 Features)

### Feature 29: ATR-Based Stop Loss
**Pine Script Lines**: 1355-1390  
**Bot Implementation**: `sl_price` field

| Attribute | Value |
|-----------|-------|
| Period | 14 |
| Multiplier | 1.5 |

---

### Feature 30: Trendline-Adjusted SL
**Pine Script Lines**: 1355-1390  
**Bot Implementation**: Part of SL calculation

| Attribute | Value |
|-----------|-------|
| Adjustment | Nearest trendline - 0.2 ATR |

---

### Feature 31: Take Profit Calculation
**Pine Script Lines**: 1395-1430  
**Bot Implementation**: `tp1_price`, `tp2_price` fields

| Target | Calculation |
|--------|-------------|
| TP1 | SL Distance × 2.0 |
| TP2 | SL Distance × 3.0 |

---

### Feature 32: Volume Confirmation
**Pine Script Lines**: 185-210  
**Bot Implementation**: `volume_confirmed` field

| Level | Condition |
|-------|-----------|
| OK | Volume > SMA(20) |
| Strong | Volume > SMA(20) × 1.5 |

---

### Feature 33: ADX Momentum Filter
**Pine Script Lines**: 150-180  
**Bot Implementation**: `adx_value` field validation

| Threshold | Value |
|-----------|-------|
| Minimum | 25 |
| Strong | 40 |

---

## Category 6: Order Execution (3 Features)

### Feature 34: Dual Order System
**Bot Implementation**: `create_dual_orders()`

| Order | SL Type | TP Type |
|-------|---------|---------|
| Order A | V6 Calculated SL | 2:1 RR |
| Order B | Fixed $10 Risk | Profit Booking |

---

### Feature 35: Timeframe-Based Plugin Routing
**Bot Implementation**: `PluginRouter._get_v6_plugin_for_timeframe()`

| Timeframe | Plugin | Risk Multiplier |
|-----------|--------|-----------------|
| 5m | v6_price_action_5m | 0.5x |
| 15m | v6_price_action_15m | 1.0x |
| 1H/4H | v6_price_action_1h | 1.5x |

---

### Feature 36: Pine Supremacy Validation
**Bot Implementation**: `_validate_via_trend_manager()`

| Attribute | Value |
|-----------|-------|
| Source | Pine Script alert |
| Override | Never override Pine |
| Validation | Trust Pine calculations |

---

## Category 7: Telegram Integration (2 Features)

### Feature 37: Trade Entry Notification
**Bot Implementation**: `_send_notification()` → `trade_opened`

| Content | Source |
|---------|--------|
| Symbol | `alert.symbol` |
| Direction | `alert.direction` |
| Confidence | `alert.confidence` |
| Entry Price | `alert.price` |
| SL/TP | `alert.sl_price`, `alert.tp1_price` |

---

### Feature 38: Trend Pulse Notification
**Bot Implementation**: `handle_trend_pulse()`

| Content | Source |
|---------|--------|
| Changed TFs | `changed_timeframes` |
| Alignment | `aligned_count` |
| Confidence | `confidence` |

---

## Category 8: Database & Logging (1 Feature)

### Feature 39: Signal Logging
**Bot Implementation**: Logger throughout plugin

| Log Level | Content |
|-----------|---------|
| INFO | Signal received, trade executed |
| WARNING | Signal filtered, validation failed |
| ERROR | Execution errors |
| DEBUG | Detailed calculations |

---

## Feature Coverage Matrix

| Feature # | Feature Name | Pine Script | Bot Code | Status |
|-----------|--------------|-------------|----------|--------|
| 1 | Breakout Entry Bull | Lines 955-1000 | plugin.py | IMPLEMENTED |
| 2 | Breakout Entry Bear | Lines 955-1000 | plugin.py | IMPLEMENTED |
| 3 | Momentum Entry Bull | Lines 1005-1050 | plugin.py | IMPLEMENTED |
| 4 | Momentum Entry Bear | Lines 1005-1050 | plugin.py | IMPLEMENTED |
| 5 | Screener Full Bullish | Lines 905-940 | plugin.py | IMPLEMENTED |
| 6 | Screener Full Bearish | Lines 905-940 | plugin.py | IMPLEMENTED |
| 7 | Bullish Exit | Lines 1105-1150 | plugin.py | IMPLEMENTED |
| 8 | Bearish Exit | Lines 1105-1150 | plugin.py | IMPLEMENTED |
| 9 | Trend Pulse Bull | Lines 1205-1250 | plugin.py | IMPLEMENTED |
| 10 | Trend Pulse Bear | Lines 1205-1250 | plugin.py | IMPLEMENTED |
| 11 | Trend Pulse Mixed | Lines 1205-1250 | plugin.py | IMPLEMENTED |
| 12 | Trend Pulse Neutral | Lines 1205-1250 | plugin.py | IMPLEMENTED |
| 13 | Momentum Surge | Lines 1455-1490 | plugin.py | IMPLEMENTED |
| 14 | Momentum Fade | Lines 1455-1490 | plugin.py | IMPLEMENTED |
| 15 | Pivot Detection | Lines 305-340 | Parsed | IMPLEMENTED |
| 16 | Trendline Calculation | Lines 345-400 | Parsed | IMPLEMENTED |
| 17 | Trendline Breakout | Lines 405-450 | trendline_break | IMPLEMENTED |
| 18 | Trendline Retest | Lines 405-450 | Validation | IMPLEMENTED |
| 19 | Trendline Visual | Lines 56-62 | N/A | IMPLEMENTED |
| 20 | 6-TF Trend Tracking | Lines 505-530 | mtf_trends | IMPLEMENTED |
| 21 | Trend Change Detection | Lines 585-630 | changed_timeframes | IMPLEMENTED |
| 22 | Alignment Counting | Lines 585-630 | aligned_count | IMPLEMENTED |
| 23 | Min Alignment Threshold | Lines 64-72 | Config | IMPLEMENTED |
| 24 | MTF String Format | Lines 585-630 | Parser | IMPLEMENTED |
| 25 | Confidence Score | Lines 655-700 | confidence | IMPLEMENTED |
| 26 | Confidence Classification | Lines 705-730 | Validation | IMPLEMENTED |
| 27 | Min Confidence Filter | Lines 84-92 | Config | IMPLEMENTED |
| 28 | Confidence Label | Lines 84-92 | N/A | IMPLEMENTED |
| 29 | ATR-Based SL | Lines 1355-1390 | sl_price | IMPLEMENTED |
| 30 | Trendline-Adjusted SL | Lines 1355-1390 | sl_price | IMPLEMENTED |
| 31 | Take Profit Calc | Lines 1395-1430 | tp1_price, tp2_price | IMPLEMENTED |
| 32 | Volume Confirmation | Lines 185-210 | volume_confirmed | IMPLEMENTED |
| 33 | ADX Momentum Filter | Lines 150-180 | adx_value | IMPLEMENTED |
| 34 | Dual Order System | N/A | create_dual_orders | IMPLEMENTED |
| 35 | TF-Based Routing | N/A | PluginRouter | IMPLEMENTED |
| 36 | Pine Supremacy | N/A | TrendManager | IMPLEMENTED |
| 37 | Trade Entry Notification | N/A | _send_notification | IMPLEMENTED |
| 38 | Trend Pulse Notification | N/A | handle_trend_pulse | IMPLEMENTED |
| 39 | Signal Logging | N/A | Logger | IMPLEMENTED |

---

## Summary

**Total Features**: 39  
**Implemented**: 39  
**Coverage**: 100%

**Pine Script Features**: 33 (Features 1-33)  
**Bot-Only Features**: 6 (Features 34-39)

---

**Document Status**: COMPLETE  
**Feature Coverage**: 100%  
**V5 Architecture Compliance**: VERIFIED
