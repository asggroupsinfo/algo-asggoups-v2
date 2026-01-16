# V6 INTEGRATION PLAN - Make V6 Plugins Functional

**Objective:** Integrate V6 signals so they are actually processed and trades are executed. Currently V6 code exists but is NEVER called.

**Estimated Effort:** 6-8 hours

---

## PART 1: CURRENT PROBLEM

### 1.1 V6 Code Exists But Is Never Called

| Component | Location | Status |
|-----------|----------|--------|
| V6 Alert Model | `src/core/zepix_v6_alert.py` | EXISTS (538 lines) - NEVER IMPORTED |
| V6 1M Plugin | `src/logic_plugins/price_action_1m/` | EXISTS - NEVER LOADED |
| V6 5M Plugin | `src/logic_plugins/price_action_5m/` | EXISTS - NEVER LOADED |
| V6 15M Plugin | `src/logic_plugins/price_action_15m/` | EXISTS - NEVER LOADED |
| V6 1H Plugin | `src/logic_plugins/price_action_1h/` | EXISTS - NEVER LOADED |
| Trend Pulse Manager | `src/core/trend_pulse_manager.py` | EXISTS (482 lines) - NEVER USED |

### 1.2 Root Cause

`trading_engine.py` `process_alert()` method only handles V3 alert types:
- `entry_v3`
- `exit_v3`
- `squeeze_v3`
- `trend_pulse_v3`

There is NO handling for V6 alert types:
- `entry_v6` - NOT HANDLED
- `exit_v6` - NOT HANDLED
- `trend_pulse_v6` - NOT HANDLED
- `state_change_v6` - NOT HANDLED

---

## PART 2: V6 ALERT TYPES TO ADD

### 2.1 V6 Alert Types (From Pine Script V6 Documentation)

| Alert Type | Pine Lines | Purpose |
|------------|------------|---------|
| `entry_v6` | 780-813 | Entry signal with Order A or Order B |
| `exit_v6` | 820-850 | Exit signal |
| `trend_pulse_v6` | 700-750 | Trend Pulse alignment update |
| `state_change_v6` | 859-865 | Market state change notification |
| `trendline_break_v6` | 814-819 | Trendline break signal |
| `screener_v6` | 830-840 | Full screener signal |

### 2.2 V6 Alert Payload Structure

```json
{
  "type": "entry_v6",
  "symbol": "XAUUSD",
  "tf": "5",
  "direction": "buy",
  "signal_type": "MOMENTUM_ENTRY",
  "order_type": "ORDER_A",
  "entry_price": 2650.50,
  "sl_price": 2645.00,
  "tp1_price": 2660.00,
  "tp2_price": 2670.00,
  "adx_value": 28.5,
  "spread_pips": 1.2,
  "trend_pulse": {
    "bull_count": 4,
    "bear_count": 1,
    "market_state": "TRENDING_BULLISH"
  },
  "timestamp": "2026-01-14T23:00:00Z"
}
```

---

## PART 3: IMPLEMENTATION STEPS

### 3.1 Step 1: Import V6 Alert Model

**File:** `src/core/trading_engine.py`

**Add at line 6 (after V3 import):**
```python
from src.core.zepix_v6_alert import ZepixV6Alert
```

### 3.2 Step 2: Add V6 Alert Handling in process_alert()

**File:** `src/core/trading_engine.py`

**Add after V3 handling (after line 259):**

```python
# =====================================================
# V6 SIGNALS - Route to V6 Plugins
# =====================================================

elif alert_type == "entry_v6":
    logger.info("🚀 V6 Entry Signal - Routing to Plugin")
    v6_alert = ZepixV6Alert(**data)
    
    # Determine plugin based on timeframe
    plugin_id = self._get_v6_plugin_for_timeframe(v6_alert.tf)
    
    # Route to plugin
    result = await self.plugin_registry.route_alert_to_plugin(v6_alert, plugin_id)
    
    if result.get("error"):
        logger.error(f"V6 Plugin error: {result.get('error')}")
        return False
    
    return result.get("status") == "success"

elif alert_type == "exit_v6":
    logger.info("🚨 V6 Exit Signal - Routing to Plugin")
    v6_alert = ZepixV6Alert(**data)
    
    plugin_id = self._get_v6_plugin_for_timeframe(v6_alert.tf)
    result = await self.plugin_registry.route_alert_to_plugin(v6_alert, plugin_id)
    
    return result.get("status") == "success"

elif alert_type == "trend_pulse_v6":
    logger.info("📊 V6 Trend Pulse - Routing to Plugin")
    v6_alert = ZepixV6Alert(**data)
    
    plugin_id = self._get_v6_plugin_for_timeframe(v6_alert.tf)
    result = await self.plugin_registry.route_alert_to_plugin(v6_alert, plugin_id)
    
    return result.get("status") != "error"

elif alert_type == "state_change_v6":
    logger.info("🔄 V6 State Change - Routing to Plugin")
    v6_alert = ZepixV6Alert(**data)
    
    plugin_id = self._get_v6_plugin_for_timeframe(v6_alert.tf)
    result = await self.plugin_registry.route_alert_to_plugin(v6_alert, plugin_id)
    
    return result.get("status") != "error"

elif alert_type == "trendline_break_v6":
    logger.info("📈 V6 Trendline Break - Routing to Plugin")
    v6_alert = ZepixV6Alert(**data)
    
    plugin_id = self._get_v6_plugin_for_timeframe(v6_alert.tf)
    result = await self.plugin_registry.route_alert_to_plugin(v6_alert, plugin_id)
    
    return result.get("status") == "success"

elif alert_type == "screener_v6":
    logger.info("🔍 V6 Screener Signal - Routing to Plugin")
    v6_alert = ZepixV6Alert(**data)
    
    plugin_id = self._get_v6_plugin_for_timeframe(v6_alert.tf)
    result = await self.plugin_registry.route_alert_to_plugin(v6_alert, plugin_id)
    
    return result.get("status") == "success"
```

### 3.3 Step 3: Add V6 Timeframe-to-Plugin Mapping

**File:** `src/core/trading_engine.py`

**Add helper method:**

```python
def _get_v6_plugin_for_timeframe(self, timeframe: str) -> str:
    """
    Map V6 timeframe to plugin ID.
    
    Args:
        timeframe: Timeframe string ('1', '5', '15', '60')
    
    Returns:
        Plugin ID string (user-defined naming schema)
    """
    tf_to_plugin = {
        '1': 'v6-logic-01-1min',      # Scalping
        '5': 'v6-logic-02-5min',      # Momentum
        '15': 'v6-logic-03-15min',    # Intraday
        '60': 'v6-logic-04-1h',       # Swing
    }
    return tf_to_plugin.get(str(timeframe), 'v6-logic-02-5min')  # Default to momentum
```

### 3.4 Step 4: Update Plugin Loading

**File:** `src/core/trading_engine.py` `initialize()` method

**Current Code (lines 128-131):**
```python
if self.config.get("plugin_system", {}).get("enabled", True):
    self.plugin_registry.discover_plugins()
    self.plugin_registry.load_all_plugins()
```

**Enhanced Code:**
```python
if self.config.get("plugin_system", {}).get("enabled", True):
    self.plugin_registry.discover_plugins()
    self.plugin_registry.load_all_plugins()
    
    # Log loaded plugins
    loaded = self.plugin_registry.get_all_plugins()
    logger.info(f"Loaded {len(loaded)} plugins: {list(loaded.keys())}")
    
    # Verify V6 plugins are loaded
    v6_plugins = [p for p in loaded.keys() if 'v6' in p.lower()]
    if v6_plugins:
        logger.info(f"V6 Plugins ready: {v6_plugins}")
    else:
        logger.warning("No V6 plugins loaded - V6 signals will fail")
```

---

## PART 4: V6 PLUGIN SELECTION LOGIC

### 4.1 Timeframe-Based Selection

| Timeframe | Plugin ID | Order Type | Strategy |
|-----------|-----------|------------|----------|
| 1 minute | v6-logic-01-1min | ORDER_B only | Scalping |
| 5 minute | v6-logic-02-5min | Dual (A+B) | Momentum |
| 15 minute | v6-logic-03-15min | ORDER_A only | Intraday |
| 1 hour | v6-logic-04-1h | ORDER_A only | Swing |

### 4.2 Order Type Logic (From Pine Script V6)

**1M Plugin (Scalping):**
- Uses ORDER_B ONLY (quick TP1)
- Spread filter: Max 2.0 pips
- ADX filter: > 20
- No Trend Pulse alignment required

**5M Plugin (Momentum):**
- Uses DUAL ORDERS (A + B)
- Same SL for both orders
- Order A: Extended TP (TP2)
- Order B: Quick TP (TP1)
- Trend Pulse alignment: 3/5 required

**15M Plugin (Intraday):**
- Uses ORDER_A ONLY (extended TP)
- Trend Pulse alignment: 4/5 required
- ADX filter: > 25

**1H Plugin (Swing):**
- Uses ORDER_A ONLY (extended TP)
- Trend Pulse alignment: 4/5 required
- ADX filter: > 30

---

## PART 5: V6 SPECIFIC FEATURES TO IMPLEMENT

### 5.1 Trend Pulse Alignment Checks

**Add to V6 plugins:**

```python
async def check_trend_pulse_alignment(self, alert: ZepixV6Alert) -> bool:
    """
    Check if signal aligns with Trend Pulse counts.
    
    Args:
        alert: V6 alert with trend_pulse data
        
    Returns:
        bool: True if aligned
    """
    if not alert.trend_pulse:
        return True  # No pulse data, allow trade
    
    bull_count = alert.trend_pulse.get('bull_count', 0)
    bear_count = alert.trend_pulse.get('bear_count', 0)
    
    # Get required alignment from config
    required = self.config.get('trend_pulse_required', 3)
    
    if alert.direction == 'buy':
        return bull_count >= required
    else:
        return bear_count >= required
```

### 5.2 ADX Filter

**Add to V6 plugins:**

```python
async def check_adx_filter(self, alert: ZepixV6Alert) -> bool:
    """
    Check if ADX meets minimum threshold.
    
    Args:
        alert: V6 alert with adx_value
        
    Returns:
        bool: True if ADX is acceptable
    """
    adx_value = alert.adx_value or 0
    min_adx = self.config.get('min_adx', 20)
    
    return adx_value >= min_adx
```

### 5.3 Spread Verification

**Add to V6 plugins:**

```python
async def check_spread_acceptable(self, alert: ZepixV6Alert) -> bool:
    """
    Check if spread is within acceptable range.
    
    Args:
        alert: V6 alert with spread_pips
        
    Returns:
        bool: True if spread is acceptable
    """
    spread = alert.spread_pips or 0
    max_spread = self.config.get('max_spread_pips', 3.0)
    
    return spread <= max_spread
```

### 5.4 Conditional Order Placement (Order A vs Order B)

**Add to V6 plugins:**

```python
async def place_conditional_order(self, alert: ZepixV6Alert) -> Dict[str, Any]:
    """
    Place Order A or Order B based on alert.order_type.
    
    Order A: Extended TP (TP2), larger position
    Order B: Quick TP (TP1), smaller position
    
    Args:
        alert: V6 alert with order_type
        
    Returns:
        dict: Order result
    """
    order_type = alert.order_type or self.config.get('default_order_type', 'ORDER_A')
    
    if order_type == 'ORDER_A':
        # Extended TP order
        return await self.service_api.place_single_order_a(
            symbol=alert.symbol,
            direction=alert.direction.upper(),
            lot_size=self._calculate_lot_size(alert),
            sl_price=alert.sl_price,
            tp_price=alert.tp2_price,
            comment=f"V6_{self.plugin_id}_ORDER_A"
        )
    elif order_type == 'ORDER_B':
        # Quick TP order
        return await self.service_api.place_single_order_b(
            symbol=alert.symbol,
            direction=alert.direction.upper(),
            lot_size=self._calculate_lot_size(alert),
            sl_price=alert.sl_price,
            tp_price=alert.tp1_price,
            comment=f"V6_{self.plugin_id}_ORDER_B"
        )
    elif order_type == 'DUAL':
        # Both orders
        return await self.service_api.place_dual_orders_v6(
            symbol=alert.symbol,
            direction=alert.direction.upper(),
            lot_size_total=self._calculate_lot_size(alert),
            sl_price=alert.sl_price,
            tp1_price=alert.tp1_price,
            tp2_price=alert.tp2_price
        )
```

---

## PART 6: V6 PLUGIN PROCESS_ENTRY_SIGNAL IMPLEMENTATION

### 6.1 Complete Entry Signal Handler

**Add to each V6 plugin's plugin.py:**

```python
async def process_entry_signal(self, alert: Any) -> Dict[str, Any]:
    """
    Process V6 entry signal.
    
    Flow:
    1. Validate alert
    2. Check Trend Pulse alignment
    3. Check ADX filter
    4. Check spread
    5. Calculate lot size
    6. Place order (A, B, or Dual)
    7. Send notification
    8. Log to database
    
    Args:
        alert: ZepixV6Alert object
        
    Returns:
        dict: Execution result
    """
    try:
        # Step 1: Validate
        if not self.validate_alert(alert):
            return {"status": "rejected", "reason": "validation_failed"}
        
        # Step 2: Check Trend Pulse alignment
        if not await self.check_trend_pulse_alignment(alert):
            self.logger.info(f"Trend Pulse not aligned for {alert.symbol}")
            return {"status": "rejected", "reason": "trend_pulse_not_aligned"}
        
        # Step 3: Check ADX
        if not await self.check_adx_filter(alert):
            self.logger.info(f"ADX too low for {alert.symbol}: {alert.adx_value}")
            return {"status": "rejected", "reason": "adx_too_low"}
        
        # Step 4: Check spread
        if not await self.check_spread_acceptable(alert):
            self.logger.info(f"Spread too high for {alert.symbol}: {alert.spread_pips}")
            return {"status": "rejected", "reason": "spread_too_high"}
        
        # Step 5: Place order
        result = await self.place_conditional_order(alert)
        
        if result.get("error"):
            return {"status": "error", "message": result.get("error")}
        
        # Step 6: Send notification
        self.service_api.send_notification(
            f"🎯 V6 ORDER PLACED\n"
            f"Plugin: {self.plugin_id}\n"
            f"Symbol: {alert.symbol}\n"
            f"Direction: {alert.direction.upper()}\n"
            f"Order Type: {alert.order_type}\n"
            f"Entry: {alert.entry_price}\n"
            f"SL: {alert.sl_price}\n"
            f"TP1: {alert.tp1_price}\n"
            f"TP2: {alert.tp2_price}"
        )
        
        # Step 7: Log to database
        await self._log_trade_to_db(alert, result)
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        self.logger.error(f"V6 Entry error: {e}")
        return {"status": "error", "message": str(e)}
```

---

## PART 7: VERIFICATION CHECKLIST

After V6 integration, verify:

- [ ] ZepixV6Alert is imported in trading_engine.py
- [ ] All V6 alert types are handled in process_alert()
- [ ] V6 plugins are loaded on startup
- [ ] Timeframe-to-plugin mapping works correctly
- [ ] Trend Pulse alignment checks work
- [ ] ADX filter works
- [ ] Spread filter works
- [ ] Order A placement works
- [ ] Order B placement works
- [ ] Dual order placement works
- [ ] Notifications are sent
- [ ] Trades are logged to database

---

## PART 8: TEST SCENARIOS

### 8.1 Manual Test: V6 1M Entry

```json
{
  "type": "entry_v6",
  "symbol": "XAUUSD",
  "tf": "1",
  "direction": "buy",
  "signal_type": "SCALP_ENTRY",
  "order_type": "ORDER_B",
  "entry_price": 2650.50,
  "sl_price": 2648.00,
  "tp1_price": 2653.00,
  "adx_value": 25,
  "spread_pips": 1.5
}
```

**Expected Result:**
- Routes to v6-logic-01-1min plugin
- Places ORDER_B only
- TP at 2653.00 (TP1)

### 8.2 Manual Test: V6 5M Entry

```json
{
  "type": "entry_v6",
  "symbol": "XAUUSD",
  "tf": "5",
  "direction": "sell",
  "signal_type": "MOMENTUM_ENTRY",
  "order_type": "DUAL",
  "entry_price": 2650.50,
  "sl_price": 2655.00,
  "tp1_price": 2645.00,
  "tp2_price": 2640.00,
  "adx_value": 30,
  "spread_pips": 1.2,
  "trend_pulse": {
    "bull_count": 1,
    "bear_count": 4
  }
}
```

**Expected Result:**
- Routes to v6-logic-02-5min plugin
- Checks Trend Pulse (4 bear >= 3 required) - PASS
- Places DUAL orders (A + B)
- Order A: TP at 2640.00 (TP2)
- Order B: TP at 2645.00 (TP1)

---

## SUCCESS CRITERIA

1. **V6 alerts are processed and trades are executed**
2. **Correct plugin is selected based on timeframe**
3. **Trend Pulse alignment is checked**
4. **ADX filter is applied**
5. **Spread filter is applied**
6. **Order A/B/Dual logic works correctly**
7. **Notifications are sent to Telegram**
8. **Trades are logged to V6 database**
