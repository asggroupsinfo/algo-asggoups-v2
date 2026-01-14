# PLUGIN WIRING PLAN - Connect Core to Plugins

**Objective:** Wire Core to Plugins with CORRECT data flow. Make `route_alert_to_plugin()` the PRIMARY method for all signal processing.

**Files to Modify:**
1. `src/core/trading_engine.py`
2. `src/core/plugin_system/plugin_registry.py`
3. `src/core/plugin_system/service_api.py`

**Estimated Effort:** 2-3 hours

---

## PART 1: UPDATE process_alert() in trading_engine.py

### 1.1 Current Data Flow (BROKEN)

```
Webhook -> process_alert() -> execute_v3_entry() [HARDCODED] -> MT5
                           -> plugin_registry.execute_hook() [ONLY MODIFIES DATA]
```

### 1.2 New Data Flow (CORRECT)

```
Webhook -> process_alert() -> plugin_registry.route_alert_to_plugin() -> Plugin.process_entry_signal() -> ServiceAPI -> MT5
```

### 1.3 New process_alert() Implementation

**Location:** `src/core/trading_engine.py` lines 184-365

**Replace entire method with:**

```python
async def process_alert(self, data: Dict[str, Any]) -> bool:
    """
    Enhanced alert router - ALL signals go through plugins.
    
    Data Flow:
    1. Parse incoming data
    2. Determine alert type (V3 or V6)
    3. Route to appropriate plugin via plugin_registry
    4. Plugin processes and returns result
    5. Core executes plugin decision
    
    Args:
        data: Alert data from webhook
        
    Returns:
        bool: True if processed successfully
    """
    
    # Step 1: Ensure data is dict
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            logger.error("Failed to parse alert data as JSON")
            return False
    
    # Step 2: PLUGIN HOOK - Allow plugins to modify/reject signal
    if self.config.get("plugin_system", {}).get("enabled", True):
        modified_data = await self.plugin_registry.execute_hook("signal_received", data)
        if modified_data is False:
            logger.info("Signal rejected by plugin hook 'on_signal_received'")
            return False
        if modified_data and isinstance(modified_data, dict):
            data = modified_data
    
    try:
        alert_type = data.get('type')
        
        # =====================================================
        # V3 SIGNALS - Route to V3 Plugins
        # =====================================================
        
        if alert_type == "entry_v3":
            logger.info("🚀 V3 Entry Signal - Routing to Plugin")
            v3_alert = ZepixV3Alert(**data)
            
            # Determine plugin based on timeframe
            plugin_id = self._get_v3_plugin_for_timeframe(v3_alert.tf)
            
            # Route to plugin - plugin handles ALL logic
            result = await self.plugin_registry.route_alert_to_plugin(v3_alert, plugin_id)
            
            if result.get("error"):
                logger.error(f"Plugin error: {result.get('error')}")
                return False
            
            return result.get("status") == "success"
        
        elif alert_type == "exit_v3":
            logger.info("🚨 V3 Exit Signal - Routing to Plugin")
            v3_alert = ZepixV3Alert(**data)
            
            plugin_id = self._get_v3_plugin_for_timeframe(v3_alert.tf)
            result = await self.plugin_registry.route_alert_to_plugin(v3_alert, plugin_id)
            
            return result.get("status") == "success"
        
        elif alert_type == "squeeze_v3":
            logger.info("🔔 V3 Squeeze Signal - Routing to Plugin")
            v3_alert = ZepixV3Alert(**data)
            
            plugin_id = self._get_v3_plugin_for_timeframe(v3_alert.tf)
            result = await self.plugin_registry.route_alert_to_plugin(v3_alert, plugin_id)
            
            return result.get("status") != "error"
        
        elif alert_type == "trend_pulse_v3":
            logger.info("📊 V3 Trend Pulse - Routing to Plugin")
            v3_alert = ZepixV3Alert(**data)
            
            plugin_id = self._get_v3_plugin_for_timeframe(v3_alert.tf)
            result = await self.plugin_registry.route_alert_to_plugin(v3_alert, plugin_id)
            
            return result.get("status") != "error"
        
        # =====================================================
        # V6 SIGNALS - Route to V6 Plugins
        # =====================================================
        
        elif alert_type == "entry_v6":
            logger.info("🚀 V6 Entry Signal - Routing to Plugin")
            from src.core.zepix_v6_alert import ZepixV6Alert
            v6_alert = ZepixV6Alert(**data)
            
            # Determine plugin based on timeframe
            plugin_id = self._get_v6_plugin_for_timeframe(v6_alert.tf)
            
            result = await self.plugin_registry.route_alert_to_plugin(v6_alert, plugin_id)
            
            return result.get("status") == "success"
        
        elif alert_type == "exit_v6":
            logger.info("🚨 V6 Exit Signal - Routing to Plugin")
            from src.core.zepix_v6_alert import ZepixV6Alert
            v6_alert = ZepixV6Alert(**data)
            
            plugin_id = self._get_v6_plugin_for_timeframe(v6_alert.tf)
            result = await self.plugin_registry.route_alert_to_plugin(v6_alert, plugin_id)
            
            return result.get("status") == "success"
        
        elif alert_type == "trend_pulse_v6":
            logger.info("📊 V6 Trend Pulse - Routing to Plugin")
            from src.core.zepix_v6_alert import ZepixV6Alert
            v6_alert = ZepixV6Alert(**data)
            
            plugin_id = self._get_v6_plugin_for_timeframe(v6_alert.tf)
            result = await self.plugin_registry.route_alert_to_plugin(v6_alert, plugin_id)
            
            return result.get("status") != "error"
        
        # =====================================================
        # LEGACY ALERTS - Keep for backward compatibility
        # =====================================================
        
        else:
            # Legacy alert handling (bias, trend, entry, reversal, exit)
            alert = Alert(**data)
            symbol = alert.symbol
            
            self.initialize_symbol_signals(symbol)
            
            # Handle legacy alerts directly (no plugin for these yet)
            if alert.type == 'bias':
                return await self._handle_legacy_bias(alert)
            elif alert.type == 'trend':
                return await self._handle_legacy_trend(alert)
            elif alert.type == 'entry':
                return await self._handle_legacy_entry(alert)
            elif alert.type == 'reversal':
                return await self._handle_legacy_reversal(alert)
            elif alert.type == 'exit':
                return await self._handle_legacy_exit(alert)
            else:
                logger.warning(f"Unknown alert type: {alert.type}")
                return False
        
    except Exception as e:
        error_msg = f"Alert processing error: {str(e)}"
        self.telegram_bot.send_message(f"❌ {error_msg}")
        logger.error(error_msg)
        import traceback
        traceback.print_exc()
        return False
```

---

## PART 2: ENHANCE plugin_registry.py

### 2.1 Make route_alert_to_plugin() the PRIMARY Method

**Location:** `src/core/plugin_system/plugin_registry.py` lines 132-171

**Current Code:**
```python
async def route_alert_to_plugin(self, alert, plugin_id: str) -> Dict[str, Any]:
    """Route alert to specified plugin."""
    plugin = self.get_plugin(plugin_id)
    
    if not plugin:
        logger.error(f"Plugin not found: {plugin_id}")
        return {"error": "plugin_not_found"}
    
    if not plugin.enabled:
        logger.warning(f"Plugin {plugin_id} is disabled, skipping alert")
        return {"skipped": True, "reason": "plugin_disabled"}
    
    # Route based on alert type
    signal_type = getattr(alert, "signal_type", None)
    if not signal_type and isinstance(alert, dict):
        signal_type = alert.get("signal_type")
    
    if not signal_type:
        logger.warning("Alert missing signal_type")
        return {"error": "missing_signal_type"}
    
    if "entry" in signal_type.lower():
        return await plugin.process_entry_signal(alert)
    elif "exit" in signal_type.lower():
        return await plugin.process_exit_signal(alert)
    elif "reversal" in signal_type.lower():
        return await plugin.process_reversal_signal(alert)
    else:
        logger.warning(f"Unknown signal type: {signal_type}")
        return {"error": "unknown_signal_type"}
```

**Enhanced Code:**
```python
async def route_alert_to_plugin(self, alert, plugin_id: str) -> Dict[str, Any]:
    """
    Route alert to specified plugin - PRIMARY ENTRY POINT.
    
    This method is the SINGLE point of entry for all signal processing.
    Core should ONLY call this method, never process signals directly.
    
    Args:
        alert: Alert object (ZepixV3Alert, ZepixV6Alert, or dict)
        plugin_id: Target plugin ID
        
    Returns:
        dict: Execution result from plugin
    """
    # Step 1: Get plugin
    plugin = self.get_plugin(plugin_id)
    
    if not plugin:
        logger.error(f"Plugin not found: {plugin_id}")
        # Try fallback plugin
        fallback_id = self._get_fallback_plugin(plugin_id)
        if fallback_id:
            plugin = self.get_plugin(fallback_id)
            logger.info(f"Using fallback plugin: {fallback_id}")
        else:
            return {"error": "plugin_not_found", "plugin_id": plugin_id}
    
    # Step 2: Check plugin health
    if not plugin.enabled:
        logger.warning(f"Plugin {plugin_id} is disabled")
        return {"skipped": True, "reason": "plugin_disabled", "plugin_id": plugin_id}
    
    # Step 3: Determine signal type
    alert_type = None
    signal_type = None
    
    # Get alert_type from alert object or dict
    if hasattr(alert, 'type'):
        alert_type = alert.type
    elif isinstance(alert, dict):
        alert_type = alert.get('type')
    
    # Get signal_type from alert object or dict
    if hasattr(alert, 'signal_type'):
        signal_type = alert.signal_type
    elif isinstance(alert, dict):
        signal_type = alert.get('signal_type')
    
    # Step 4: Route to appropriate handler
    try:
        if alert_type in ['entry_v3', 'entry_v6']:
            logger.info(f"[{plugin_id}] Processing entry signal: {signal_type}")
            return await plugin.process_entry_signal(alert)
        
        elif alert_type in ['exit_v3', 'exit_v6']:
            logger.info(f"[{plugin_id}] Processing exit signal: {signal_type}")
            return await plugin.process_exit_signal(alert)
        
        elif alert_type in ['squeeze_v3', 'squeeze_v6']:
            logger.info(f"[{plugin_id}] Processing squeeze signal")
            # Squeeze is info-only, delegate to plugin's info handler
            if hasattr(plugin, 'process_info_signal'):
                return await plugin.process_info_signal(alert)
            else:
                # Default: send notification
                self.service_api.send_notification(
                    f"🔔 Volatility Squeeze Detected\n"
                    f"Symbol: {getattr(alert, 'symbol', 'Unknown')}\n"
                    f"Timeframe: {getattr(alert, 'tf', 'Unknown')}"
                )
                return {"status": "info_sent"}
        
        elif alert_type in ['trend_pulse_v3', 'trend_pulse_v6']:
            logger.info(f"[{plugin_id}] Processing trend pulse")
            if hasattr(plugin, 'process_trend_pulse'):
                return await plugin.process_trend_pulse(alert)
            else:
                return {"status": "trend_pulse_received"}
        
        # Fallback: use signal_type to determine handler
        elif signal_type:
            signal_lower = signal_type.lower()
            if "entry" in signal_lower or "bullish" in signal_lower or "bearish" in signal_lower:
                return await plugin.process_entry_signal(alert)
            elif "exit" in signal_lower:
                return await plugin.process_exit_signal(alert)
            elif "reversal" in signal_lower:
                return await plugin.process_reversal_signal(alert)
        
        logger.warning(f"Unknown alert type: {alert_type}, signal_type: {signal_type}")
        return {"error": "unknown_signal_type", "alert_type": alert_type}
        
    except Exception as e:
        logger.error(f"Plugin {plugin_id} error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "plugin_id": plugin_id}

def _get_fallback_plugin(self, plugin_id: str) -> Optional[str]:
    """
    Get fallback plugin if primary not found.
    
    Args:
        plugin_id: Original plugin ID
        
    Returns:
        Fallback plugin ID or None
    """
    # V3 fallback: use v3-logic-02-15min (intraday) as default
    if plugin_id.startswith('v3-'):
        return 'v3-logic-02-15min'
    
    # V6 fallback: use v6-logic-02-5min (momentum) as default
    if plugin_id.startswith('v6-'):
        return 'v6-logic-02-5min'
    
    return None
```

### 2.2 Add Plugin Selection Logic

**Add new method after route_alert_to_plugin():**

```python
def get_plugin_for_alert(self, alert) -> Optional[str]:
    """
    Automatically determine which plugin should handle an alert.
    
    Args:
        alert: Alert object or dict
        
    Returns:
        Plugin ID string or None
    """
    # Get alert type
    alert_type = None
    if hasattr(alert, 'type'):
        alert_type = alert.type
    elif isinstance(alert, dict):
        alert_type = alert.get('type')
    
    # Get timeframe
    tf = None
    if hasattr(alert, 'tf'):
        tf = str(alert.tf)
    elif isinstance(alert, dict):
        tf = str(alert.get('tf', ''))
    
    # V3 alerts
    if alert_type and 'v3' in alert_type:
        tf_to_plugin = {
            '5': 'v3-logic-01-5min',
            '15': 'v3-logic-02-15min',
            '60': 'v3-logic-03-1h',
            '240': 'v3-logic-03-1h',
        }
        return tf_to_plugin.get(tf, 'v3-logic-02-15min')
    
    # V6 alerts
    if alert_type and 'v6' in alert_type:
        tf_to_plugin = {
            '1': 'v6-logic-01-1min',
            '5': 'v6-logic-02-5min',
            '15': 'v6-logic-03-15min',
            '60': 'v6-logic-04-1h',
        }
        return tf_to_plugin.get(tf, 'v6-logic-02-5min')
    
    return None
```

### 2.3 Add Plugin Health Checks

**Add new method:**

```python
def check_plugin_health(self, plugin_id: str) -> Dict[str, Any]:
    """
    Check if plugin is healthy and ready to process signals.
    
    Args:
        plugin_id: Plugin ID to check
        
    Returns:
        dict with health status
    """
    plugin = self.get_plugin(plugin_id)
    
    if not plugin:
        return {"healthy": False, "reason": "not_found"}
    
    if not plugin.enabled:
        return {"healthy": False, "reason": "disabled"}
    
    # Check if plugin has required methods
    required_methods = ['process_entry_signal', 'process_exit_signal']
    for method in required_methods:
        if not hasattr(plugin, method):
            return {"healthy": False, "reason": f"missing_{method}"}
    
    return {"healthy": True, "plugin_id": plugin_id, "enabled": plugin.enabled}
```

---

## PART 3: VERIFY ServiceAPI METHODS

### 3.1 Required Methods for Plugins

Verify these methods exist in `service_api.py`:

| Method | Purpose | Status |
|--------|---------|--------|
| `place_order()` | Place single order | EXISTS (line 282) |
| `place_dual_orders_v3()` | V3 dual orders | EXISTS (line 313) |
| `place_dual_orders_v6()` | V6 dual orders | EXISTS (line 364) |
| `close_position()` | Close position | EXISTS (line 490) |
| `calculate_lot_size()` | Lot calculation | EXISTS (line 588) |
| `get_timeframe_trend()` | Get trend | EXISTS (line 765) |
| `send_notification()` | Telegram message | EXISTS (line 946) |

### 3.2 Missing Methods to Add

**Add to service_api.py:**

```python
async def close_positions_by_direction(
    self,
    plugin_id: str,
    symbol: str,
    direction: str
) -> List[Dict[str, Any]]:
    """
    Close all positions for a symbol in a specific direction.
    
    Used for aggressive reversal signals.
    
    Args:
        plugin_id: Plugin requesting the close
        symbol: Trading symbol
        direction: 'BUY' or 'SELL' - positions in this direction will be closed
        
    Returns:
        List of closed position results
    """
    closed = []
    
    for trade in self._engine.open_trades:
        if trade.symbol == symbol and trade.direction == direction:
            result = await self.close_position(trade.trade_id, f"Reversal by {plugin_id}")
            closed.append(result)
    
    return closed
```

---

## PART 4: VERIFICATION CHECKLIST

After wiring, verify:

- [ ] `route_alert_to_plugin()` is called for EVERY V3 signal
- [ ] `route_alert_to_plugin()` is called for EVERY V6 signal
- [ ] Plugins process 100% of trading decisions
- [ ] Core ONLY executes plugin decisions
- [ ] Fallback mechanism works when plugin not found
- [ ] Health checks prevent routing to unhealthy plugins
- [ ] ServiceAPI has all required methods

---

## SUCCESS CRITERIA

1. **route_alert_to_plugin() is called for EVERY signal**
2. **Plugins process 100% of trading decisions**
3. **Core ONLY executes plugin decisions**
4. **No hardcoded trading logic in Core**
