# V3 Combined Logic Plugin - 39 Features Complete Mapping

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Pine Script Source**: `ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine` (1934 lines)  
**Plugin Implementation**: `src/logic_plugins/v3_combined/plugin.py`

---

## Feature Categories Overview

| Category | Feature Count | Coverage |
|----------|---------------|----------|
| Signal Processing | 12 | 100% |
| SMC Analysis | 6 | 100% |
| Consensus Engine | 5 | 100% |
| Risk Management | 6 | 100% |
| Order Execution | 4 | 100% |
| Telegram Integration | 4 | 100% |
| Database & Logging | 2 | 100% |
| **TOTAL** | **39** | **100%** |

---

## Category 1: Signal Processing (12 Features)

### Feature 1: Institutional Launchpad Signal
**Pine Script Lines**: 1204-1208  
**Bot Implementation**: `signal_handlers.py` → `handle_institutional_launchpad()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Buy/Sell |
| Priority | 4 (High) |
| Trigger | SMC + Consensus + Breakout alignment |

**Trigger Conditions**:
- `priceInBullOB == true` (Price in bullish Order Block)
- `consensusScore >= 7` (Strong bullish consensus)
- `bullishBreakout OR trendLongBreak` (Breakout confirmed)
- `marketTrend == 1` (Overall market bullish)
- `volumeOK == true` (Volume above average)
- `bullishSignalAllowed == true` (Cooldown passed)

**Bot Routing**: LOGIC1 (5m), LOGIC2 (15m), LOGIC3 (1H/4H)

---

### Feature 2: Liquidity Trap Reversal Signal
**Pine Script Lines**: 1210-1214  
**Bot Implementation**: `signal_handlers.py` → `handle_liquidity_trap()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Buy/Sell |
| Priority | 2 (Medium) |
| Trigger | Sweep + OB + Volume confirmation |

**Trigger Conditions**:
- `bullSweep == true` (Liquidity sweep detected)
- `priceInBullOB == true` (Price returned to OB)
- `volumeOK == true` (Volume confirmation)
- `marketTrend == 1 OR adxValue > 25` (Trend or momentum)

**Bot Routing**: Standard timeframe routing

---

### Feature 3: Momentum Breakout Signal
**Pine Script Lines**: 1216-1220  
**Bot Implementation**: `signal_handlers.py` → `handle_momentum_breakout()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Buy/Sell |
| Priority | 2 (Medium) |
| Trigger | Trend break + Volume + ADX > 25 |

**Trigger Conditions**:
- `bullishBreakout == true` (Price broke above resistance)
- `adxValue > 25` (Strong momentum confirmed)
- `volumeOK == true` (Volume above average)

**Bot Routing**: Standard timeframe routing

---

### Feature 4: Mitigation Test Entry Signal
**Pine Script Lines**: 1222-1226  
**Bot Implementation**: `signal_handlers.py` → `handle_mitigation_test()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Buy/Sell |
| Priority | 1 (Low) |
| Trigger | Price in OB + Consensus alignment |

**Trigger Conditions**:
- `priceInBullOB == true` (Price testing OB)
- `consensusScore >= 5` (Moderate bullish consensus)
- `marketTrend == 1` (Overall market bullish)

**Bot Routing**: Standard timeframe routing

---

### Feature 5: Bullish Exit Signal
**Pine Script Lines**: 1228-1230  
**Bot Implementation**: `signal_handlers.py` → `handle_exit_signal()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Exit |
| Direction | Close Long |
| Priority | N/A |
| Trigger | Consensus flip + Volume divergence |

**Trigger Conditions**:
- `consensusScore <= 3` (Consensus turned bearish)
- `consensusScore[1] >= 5` (Was bullish before)
- `volumeOK == true` (Volume confirmation)

**Bot Action**: Close all long positions for symbol

---

### Feature 6: Bearish Exit Signal
**Pine Script Lines**: 1230-1232  
**Bot Implementation**: `signal_handlers.py` → `handle_exit_signal()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Exit |
| Direction | Close Short |
| Priority | N/A |
| Trigger | Consensus flip + Volume divergence |

**Trigger Conditions**:
- `consensusScore >= 6` (Consensus turned bullish)
- `consensusScore[1] <= 4` (Was bearish before)
- `volumeOK == true` (Volume confirmation)

**Bot Action**: Close all short positions for symbol

---

### Feature 7: Golden Pocket Flip Signal
**Pine Script Lines**: 1234-1238  
**Bot Implementation**: `signal_handlers.py` → `handle_golden_pocket()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Buy/Sell |
| Priority | 3 (Medium-High) |
| Trigger | Fib retracement + OB confluence |

**Trigger Conditions**:
- `priceInBullOB == true` (Price in OB at Fib level)
- `consensusScore >= 6` (Strong consensus)
- `bullishBOS == true` (Break of structure confirmed)

**Bot Routing**: Force LOGIC3 for 1H/4H timeframes

---

### Feature 8: Volatility Squeeze Alert
**Pine Script Lines**: 1240-1241  
**Bot Implementation**: `signal_handlers.py` → `handle_info_signal()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Info |
| Direction | N/A |
| Priority | N/A |
| Trigger | Low volatility period |

**Trigger Conditions**:
- `inConsolidation == true` (Low ADX, narrow range)
- `adxValue < 20` (Weak trend)
- `rangePercent < 2` (Tight price range)

**Bot Action**: Notification only, no trade

---

### Feature 9: Screener Full Bullish Signal
**Pine Script Lines**: 1242-1244  
**Bot Implementation**: `signal_handlers.py` → `handle_screener_full()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Buy |
| Priority | 5 (Highest) |
| Trigger | All 9 indicators bullish |

**Trigger Conditions**:
- `macdBullish == true`
- `rsiBullish == true`
- `stochBullish == true`
- `emaBullish == true`
- `adxBullish == true`
- `stBullish == true`
- `volumeOK == true`
- `obvBullish == true`
- `mfiBullish == true`

**Bot Routing**: Force LOGIC3 (Swing) regardless of timeframe

---

### Feature 10: Screener Full Bearish Signal
**Pine Script Lines**: 1246-1248  
**Bot Implementation**: `signal_handlers.py` → `handle_screener_full()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Sell |
| Priority | 5 (Highest) |
| Trigger | All 9 indicators bearish |

**Trigger Conditions**:
- All 9 indicators in bearish state

**Bot Routing**: Force LOGIC3 (Swing) regardless of timeframe

---

### Feature 11: Trend Pulse Notification
**Pine Script Lines**: 1802-1806  
**Bot Implementation**: `signal_handlers.py` → `handle_trend_pulse()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Info |
| Direction | N/A |
| Priority | N/A |
| Trigger | MTF trend change detected |

**Trigger Conditions**:
- Any of the 6 timeframes changed trend direction
- `changedTimeframes.length > 0`

**Bot Action**: Update MTF tracking, send notification

---

### Feature 12: Sideways Breakout Signal
**Pine Script Lines**: 1808-1818  
**Bot Implementation**: `signal_handlers.py` → `handle_sideways_breakout()`

| Attribute | Value |
|-----------|-------|
| Signal Type | Entry |
| Direction | Buy/Sell |
| Priority | 1 (Low) |
| Trigger | Squeeze exit + ZLEMA trend flip |

**Trigger Conditions**:
- `wasInSqueeze OR wasNeutral == true` (Was in consolidation)
- `trendStartBull == true` (ZLEMA flipped bullish)
- `volumeOK == true` (Volume confirmation)

**Bot Routing**: Standard timeframe routing

---

## Category 2: SMC Analysis (6 Features)

### Feature 13: Order Block Detection
**Pine Script Lines**: 310-380  
**Bot Implementation**: Parsed from `price_in_ob` field

| Attribute | Value |
|-----------|-------|
| Type | Bullish/Bearish |
| Detection | 3-candle pattern |
| Storage | Array (max 50) |

**Detection Logic**:
- Bearish candle → Bullish candle → Break above
- Volume above 20-period SMA

---

### Feature 14: Fair Value Gap Detection
**Pine Script Lines**: 385-430  
**Bot Implementation**: Parsed from alert payload

| Attribute | Value |
|-----------|-------|
| Type | Bullish/Bearish |
| Detection | Gap between candle 1 high and candle 3 low |
| Minimum Size | 0.5 × ATR(14) |

---

### Feature 15: Liquidity Sweep Detection
**Pine Script Lines**: 435-480  
**Bot Implementation**: Triggers Signal 2

| Attribute | Value |
|-----------|-------|
| Type | Bullish/Bearish |
| Detection | Price exceeds equal H/L then reverses |
| Lookback | 50 bars (configurable) |

---

### Feature 16: Equal Highs/Lows Detection
**Pine Script Lines**: 435-450  
**Bot Implementation**: Part of liquidity analysis

| Attribute | Value |
|-----------|-------|
| Detection | Multiple touches at same level |
| Threshold | 0.5% tolerance |

---

### Feature 17: Break of Structure Detection
**Pine Script Lines**: 535-570  
**Bot Implementation**: Triggers Signal 7

| Attribute | Value |
|-----------|-------|
| Type | Bullish/Bearish |
| Detection | Close above/below last swing point |

---

### Feature 18: Price in OB Check
**Pine Script Lines**: 485-500  
**Bot Implementation**: `price_in_ob` field in alert

| Attribute | Value |
|-----------|-------|
| Check | Real-time |
| Used By | Signals 1, 2, 4, 7 |

---

## Category 3: Consensus Engine (5 Features)

### Feature 19: ZLEMA Calculation
**Pine Script Lines**: 632-635  
**Bot Implementation**: Trend direction from alert

| Attribute | Value |
|-----------|-------|
| Period | `signalSensitivity` (default 20) |
| Lag | `(period - 1) / 2` |

---

### Feature 20: VIDYA Calculation
**Pine Script Lines**: 638-646  
**Bot Implementation**: Part of consensus

| Attribute | Value |
|-----------|-------|
| Length | Configurable |
| Momentum Period | Configurable |
| Smoothing | 15-period SMA |

---

### Feature 21: Nine-Indicator Voting System
**Pine Script Lines**: 648-750  
**Bot Implementation**: `consensus_score` field (0-9)

**Indicators**:
1. MACD (Weight 2)
2. RSI (Weight 2)
3. Stochastic (Weight 2)
4. EMA Cross (Weight 1)
5. ADX (Weight 1)
6. Supertrend (Weight 1)
7. Volume (Weight 1)
8. OBV (Weight 1)
9. MFI (Weight 1)

---

### Feature 22: Consensus Score Calculation
**Pine Script Lines**: 755-780  
**Bot Implementation**: `consensus_score` field

| Score | Interpretation |
|-------|----------------|
| 7-9 | Strong Bullish |
| 5-6 | Moderate Bullish |
| 3-4 | Neutral |
| 0-2 | Bearish |

---

### Feature 23: Trend Direction Confirmation
**Pine Script Lines**: 605-627  
**Bot Implementation**: `market_trend` field

| Value | Meaning |
|-------|---------|
| 1 | Bullish |
| 0 | Neutral |
| -1 | Bearish |

---

## Category 4: Risk Management (6 Features)

### Feature 24: Position Multiplier Calculation
**Pine Script Lines**: 955-1000  
**Bot Implementation**: `position_multiplier` field

| Consensus Score | Base Multiplier |
|-----------------|-----------------|
| 8-9 | 1.0x |
| 6-7 | 0.8x |
| 5 | 0.6x |
| <5 | 0.4x |

**MTF Adjustment**:
- 4 TFs aligned: 1.0x
- 3 TFs aligned: 0.8x
- <3 TFs aligned: 0.5x

---

### Feature 25: Smart Stop Loss Calculation
**Pine Script Lines**: 1005-1050  
**Bot Implementation**: `sl_price` field

| Attribute | Value |
|-----------|-------|
| Base | ATR(14) × SL Multiplier |
| Adjustment | Nearest structure level |

---

### Feature 26: Take Profit Calculation
**Pine Script Lines**: 1055-1080  
**Bot Implementation**: `tp1_price`, `tp2_price` fields

| Target | Calculation |
|--------|-------------|
| TP1 | SL Distance × RR Ratio |
| TP2 | SL Distance × RR Ratio × 1.5 |

---

### Feature 27: Volume Delta Ratio
**Pine Script Lines**: 1085-1100  
**Bot Implementation**: `volume_delta_ratio` field

| Attribute | Value |
|-----------|-------|
| Calculation | Buy Volume / Sell Volume |
| Threshold | > 1.0 for bullish |

---

### Feature 28: ATR-Based Volatility Adjustment
**Pine Script Lines**: 1005-1010  
**Bot Implementation**: Part of SL/TP calculation

| Attribute | Value |
|-----------|-------|
| Period | 14 |
| Multiplier | Configurable (default 1.5) |

---

### Feature 29: MTF Alignment Check
**Pine Script Lines**: 605-627  
**Bot Implementation**: `mtf_trends` field

| Attribute | Value |
|-----------|-------|
| Timeframes | 1m, 5m, 15m, 1H, 4H, 1D |
| Format | "1,1,1,1,1,1" (comma-separated) |

**Bot Usage**: MTF 4-Pillar System (indices 2-5 only)

---

## Category 5: Order Execution (4 Features)

### Feature 30: Dual Order System
**Bot Implementation**: `plugin.py` → `create_dual_orders()`

| Order | SL Type | TP Type |
|-------|---------|---------|
| Order A | V3 Smart SL | 2:1 RR |
| Order B | Fixed $10 Risk | Profit Booking |

---

### Feature 31: Order A - TP Trail
**Bot Implementation**: `get_order_a_config()`

| Attribute | Value |
|-----------|-------|
| SL Source | Pine Script `sl_price` |
| Trailing Start | 50% of SL in profit |
| Trailing Step | 25% of SL |

---

### Feature 32: Order B - Profit Trail
**Bot Implementation**: `get_order_b_config()`

| Attribute | Value |
|-----------|-------|
| SL Type | Fixed $10 Risk |
| TP | None (uses profit booking) |
| Chain | Creates profit chain |

---

### Feature 33: Signal-to-Logic Routing
**Bot Implementation**: `_route_to_logic()`

| Timeframe | Logic | Risk Multiplier |
|-----------|-------|-----------------|
| 5m | LOGIC1 | 0.5x |
| 15m | LOGIC2 | 1.0x |
| 1H/4H | LOGIC3 | 1.5x |

**Overrides**:
- Screener Full → Force LOGIC3
- Golden Pocket (1H/4H) → Force LOGIC3

---

## Category 6: Telegram Integration (4 Features)

### Feature 34: Trade Entry Notification
**Bot Implementation**: `_send_notification()` → `trade_opened`

| Content | Source |
|---------|--------|
| Symbol | `alert.symbol` |
| Direction | `alert.direction` |
| Entry Price | `alert.price` |
| SL Price | `alert.sl_price` |
| TP Prices | `alert.tp1_price`, `alert.tp2_price` |

---

### Feature 35: Trade Exit Notification
**Bot Implementation**: `_send_notification()` → `trade_closed`

| Content | Source |
|---------|--------|
| Symbol | Trade symbol |
| P/L | Calculated from entry/exit |
| Reason | SL/TP/Manual |

---

### Feature 36: Trend Pulse Notification
**Bot Implementation**: `handle_trend_pulse()`

| Content | Source |
|---------|--------|
| Changed TFs | `changed_timeframes` |
| Details | `change_details` |
| Current Trends | `current_trends` |

---

### Feature 37: Volatility Squeeze Alert
**Bot Implementation**: `handle_info_signal()`

| Content | Source |
|---------|--------|
| Symbol | `alert.symbol` |
| ADX Value | `alert.adx_value` |
| Range % | Calculated |

---

## Category 7: Database & Logging (2 Features)

### Feature 38: Trade Persistence
**Bot Implementation**: `save_trade()`, `get_trades()`

| Table | Fields |
|-------|--------|
| trades | id, plugin_id, symbol, direction, entry_price, sl_price, tp_price, status, created_at |

---

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
| 1 | Institutional Launchpad | Lines 1204-1208 | signal_handlers.py | IMPLEMENTED |
| 2 | Liquidity Trap Reversal | Lines 1210-1214 | signal_handlers.py | IMPLEMENTED |
| 3 | Momentum Breakout | Lines 1216-1220 | signal_handlers.py | IMPLEMENTED |
| 4 | Mitigation Test Entry | Lines 1222-1226 | signal_handlers.py | IMPLEMENTED |
| 5 | Bullish Exit | Lines 1228-1230 | signal_handlers.py | IMPLEMENTED |
| 6 | Bearish Exit | Lines 1230-1232 | signal_handlers.py | IMPLEMENTED |
| 7 | Golden Pocket Flip | Lines 1234-1238 | signal_handlers.py | IMPLEMENTED |
| 8 | Volatility Squeeze | Lines 1240-1241 | signal_handlers.py | IMPLEMENTED |
| 9 | Screener Full Bullish | Lines 1242-1244 | signal_handlers.py | IMPLEMENTED |
| 10 | Screener Full Bearish | Lines 1246-1248 | signal_handlers.py | IMPLEMENTED |
| 11 | Trend Pulse | Lines 1802-1806 | signal_handlers.py | IMPLEMENTED |
| 12 | Sideways Breakout | Lines 1808-1818 | signal_handlers.py | IMPLEMENTED |
| 13 | Order Block Detection | Lines 310-380 | Parsed from alert | IMPLEMENTED |
| 14 | FVG Detection | Lines 385-430 | Parsed from alert | IMPLEMENTED |
| 15 | Liquidity Sweep | Lines 435-480 | Triggers Signal 2 | IMPLEMENTED |
| 16 | Equal H/L Detection | Lines 435-450 | Part of liquidity | IMPLEMENTED |
| 17 | BOS Detection | Lines 535-570 | Triggers Signal 7 | IMPLEMENTED |
| 18 | Price in OB Check | Lines 485-500 | price_in_ob field | IMPLEMENTED |
| 19 | ZLEMA Calculation | Lines 632-635 | Trend from alert | IMPLEMENTED |
| 20 | VIDYA Calculation | Lines 638-646 | Part of consensus | IMPLEMENTED |
| 21 | 9-Indicator Voting | Lines 648-750 | consensus_score | IMPLEMENTED |
| 22 | Consensus Score | Lines 755-780 | consensus_score | IMPLEMENTED |
| 23 | Trend Confirmation | Lines 605-627 | market_trend | IMPLEMENTED |
| 24 | Position Multiplier | Lines 955-1000 | position_multiplier | IMPLEMENTED |
| 25 | Smart Stop Loss | Lines 1005-1050 | sl_price | IMPLEMENTED |
| 26 | Take Profit Calc | Lines 1055-1080 | tp1_price, tp2_price | IMPLEMENTED |
| 27 | Volume Delta Ratio | Lines 1085-1100 | volume_delta_ratio | IMPLEMENTED |
| 28 | ATR Volatility | Lines 1005-1010 | Part of SL/TP | IMPLEMENTED |
| 29 | MTF Alignment | Lines 605-627 | mtf_trends | IMPLEMENTED |
| 30 | Dual Order System | N/A | plugin.py | IMPLEMENTED |
| 31 | Order A - TP Trail | N/A | get_order_a_config | IMPLEMENTED |
| 32 | Order B - Profit Trail | N/A | get_order_b_config | IMPLEMENTED |
| 33 | Signal-to-Logic Routing | N/A | _route_to_logic | IMPLEMENTED |
| 34 | Trade Entry Notification | N/A | _send_notification | IMPLEMENTED |
| 35 | Trade Exit Notification | N/A | _send_notification | IMPLEMENTED |
| 36 | Trend Pulse Notification | N/A | handle_trend_pulse | IMPLEMENTED |
| 37 | Volatility Squeeze Alert | N/A | handle_info_signal | IMPLEMENTED |
| 38 | Trade Persistence | N/A | save_trade | IMPLEMENTED |
| 39 | Signal Logging | N/A | Logger | IMPLEMENTED |

---

## Summary

**Total Features**: 39  
**Implemented**: 39  
**Coverage**: 100%

**Pine Script Features**: 29 (Features 1-29)  
**Bot-Only Features**: 10 (Features 30-39)

---

**Document Status**: COMPLETE  
**Feature Coverage**: 100%  
**V5 Architecture Compliance**: VERIFIED
