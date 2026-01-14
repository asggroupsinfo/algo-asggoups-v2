# CORE CLEANUP PLAN - Remove ALL Hardcoded Business Logic

**Objective:** Remove ALL hardcoded trading logic from Core files. Core should ONLY route data and execute plugin decisions.

**Files to Modify:**
1. `src/core/trading_engine.py` (2072 lines)
2. `src/processors/alert_processor.py` (266 lines)

**Estimated Effort:** 8-10 hours

---

## PART 1: trading_engine.py CLEANUP

### 1.1 Functions to DELETE (Complete Removal)

| Function | Lines | Reason for Deletion |
|----------|-------|---------------------|
| `execute_v3_entry()` | 367-431 | Duplicated in combined_v3/plugin.py |
| `_route_v3_to_logic()` | 433-452 | Duplicated in combined_v3/plugin.py |
| `_get_logic_multiplier()` | 454-463 | Duplicated in combined_v3/plugin.py |
| `_place_hybrid_dual_orders_v3()` | 465-696 | Duplicated in combined_v3/order_manager.py |
| `handle_v3_exit()` | 698-837 | Duplicated in combined_v3/signal_handlers.py |
| `handle_v3_reversal()` | 839-985 | Duplicated in combined_v3/signal_handlers.py |

**Total Lines to Delete:** ~620 lines

### 1.2 Functions to MODIFY

#### 1.2.1 `__init__()` (Lines 29-111)

**Current Code (Lines 101-104):**
```python
# Logic control flags
self.combinedlogic_1_enabled = True
self.combinedlogic_2_enabled = True
self.combinedlogic_3_enabled = True
```

**Action:** DELETE these lines. Logic flags should be in plugin config.

**Current Code (Lines 106-111):**
```python
# Initialize Plugin System
self.service_api = ServiceAPI(self)
self.plugin_registry = PluginRegistry(
    config=self.config,
    service_api=self.service_api
)
```

**Action:** KEEP but enhance with plugin_id tracking.

#### 1.2.2 `process_alert()` (Lines 184-365)

**Current Code (Lines 208-233) - V3 ENTRY:**
```python
if alert_type == "entry_v3":
    logger.info("🚀 V3 Entry Signal - BYPASSING Trend Manager")
    logger.info("   Reason: V3 has pre-validated 5-layer confluence")
    
    v3_alert = ZepixV3Alert(**data)
    
    # Update MTF trends in background
    if v3_alert.mtf_trends:
        self.alert_processor.process_mtf_trends(v3_alert.mtf_trends, v3_alert.symbol)
    
    # Check if this is an aggressive reversal signal
    AGGRESSIVE_SIGNALS = [...]
    
    if v3_alert.signal_type in AGGRESSIVE_SIGNALS or v3_alert.consensus_score >= 7:
        reversal_result = await self.handle_v3_reversal(v3_alert)
        logger.info(f"Reversal result: {reversal_result.get('status')}")
    
    # Execute WITHOUT checking trend alignment
    result = await self.execute_v3_entry(v3_alert)
    return result.get("status") == "success"
```

**New Code:**
```python
if alert_type == "entry_v3":
    logger.info("🚀 V3 Entry Signal - Routing to Plugin")
    v3_alert = ZepixV3Alert(**data)
    
    # Determine which V3 plugin to use based on timeframe
    plugin_id = self._get_v3_plugin_for_timeframe(v3_alert.tf)
    
    # Route to plugin
    result = await self.plugin_registry.route_alert_to_plugin(v3_alert, plugin_id)
    return result.get("status") == "success"
```

**Current Code (Lines 236-242) - V3 EXIT:**
```python
elif alert_type == "exit_v3":
    v3_alert = ZepixV3Alert(**data)
    logger.info(f"🚨 V3 Exit signal received: {v3_alert.signal_type}")
    
    # Call dedicated exit handler
    result = await self.handle_v3_exit(v3_alert)
    return result.get("status") == "success"
```

**New Code:**
```python
elif alert_type == "exit_v3":
    logger.info("🚨 V3 Exit Signal - Routing to Plugin")
    v3_alert = ZepixV3Alert(**data)
    
    # Route to V3 plugin for exit handling
    plugin_id = self._get_v3_plugin_for_timeframe(v3_alert.tf)
    result = await self.plugin_registry.route_alert_to_plugin(v3_alert, plugin_id)
    return result.get("status") == "success"
```

**Current Code (Lines 244-259) - V3 SQUEEZE & TREND PULSE:**
```python
elif alert_type == "squeeze_v3":
    v3_alert = ZepixV3Alert(**data)
    self.telegram_bot.send_message(...)
    return True

elif alert_type == "trend_pulse_v3":
    v3_alert = ZepixV3Alert(**data)
    logger.info(f"Trend Pulse: {v3_alert.changed_timeframes}")
    return True
```

**New Code:**
```python
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
```

#### 1.2.3 NEW HELPER METHODS to ADD

**Add after line 182:**
```python
def _get_v3_plugin_for_timeframe(self, timeframe: str) -> str:
    """
    Map V3 timeframe to plugin ID.
    
    Args:
        timeframe: Timeframe string ('5', '15', '60', '240')
    
    Returns:
        Plugin ID string
    """
    # User-defined naming schema
    tf_to_plugin = {
        '5': 'v3-logic-01-5min',      # Scalping
        '15': 'v3-logic-02-15min',    # Intraday
        '60': 'v3-logic-03-1h',       # Swing
        '240': 'v3-logic-03-1h',      # Swing (4H uses 1H plugin)
    }
    return tf_to_plugin.get(timeframe, 'v3-logic-02-15min')  # Default to intraday

def _get_v6_plugin_for_timeframe(self, timeframe: str) -> str:
    """
    Map V6 timeframe to plugin ID.
    
    Args:
        timeframe: Timeframe string ('1', '5', '15', '60')
    
    Returns:
        Plugin ID string
    """
    # User-defined naming schema
    tf_to_plugin = {
        '1': 'v6-logic-01-1min',      # Scalping
        '5': 'v6-logic-02-5min',      # Momentum
        '15': 'v6-logic-03-15min',    # Intraday
        '60': 'v6-logic-04-1h',       # Swing
    }
    return tf_to_plugin.get(timeframe, 'v6-logic-02-5min')  # Default to momentum
```

#### 1.2.4 `enable_logic()` and `disable_logic()` (Lines 2030-2044)

**Current Code:**
```python
def enable_logic(self, logic_name: str):
    """Enable a specific logic"""
    if logic_name == "combinedlogic-1":
        self.combinedlogic_1_enabled = True
    # ... etc

def disable_logic(self, logic_name: str):
    """Disable a specific logic"""
    if logic_name == "combinedlogic-1":
        self.combinedlogic_1_enabled = False
    # ... etc
```

**New Code:**
```python
def enable_logic(self, plugin_id: str):
    """Enable a specific plugin"""
    plugin = self.plugin_registry.get_plugin(plugin_id)
    if plugin:
        plugin.enable()
        logger.info(f"Plugin {plugin_id} enabled")
        return True
    logger.warning(f"Plugin {plugin_id} not found")
    return False

def disable_logic(self, plugin_id: str):
    """Disable a specific plugin"""
    plugin = self.plugin_registry.get_plugin(plugin_id)
    if plugin:
        plugin.disable()
        logger.info(f"Plugin {plugin_id} disabled")
        return True
    logger.warning(f"Plugin {plugin_id} not found")
    return False

def get_logic_status(self) -> Dict[str, bool]:
    """Get status of all plugins"""
    status = {}
    for plugin_id, plugin in self.plugin_registry.get_all_plugins().items():
        status[plugin_id] = plugin.enabled
    return status
```

---

## PART 2: alert_processor.py CLEANUP

### 2.1 Functions to MOVE (Not Delete)

#### 2.1.1 `process_mtf_trends()` (Lines 15-94)

**Action:** Move to `src/logic_plugins/combined_v3/trend_validator.py`

**Reason:** MTF trend processing is V3-specific logic and should be in the V3 plugin.

**Current Location:** `alert_processor.py` lines 15-94
**New Location:** `combined_v3/trend_validator.py`

**In alert_processor.py, replace with:**
```python
def process_mtf_trends(self, trend_string: str, symbol: str) -> None:
    """
    Process MTF trends - DELEGATED TO PLUGIN.
    
    This method is kept for backward compatibility but delegates
    to the appropriate plugin for actual processing.
    """
    # Delegate to trend manager directly (plugins will handle via ServiceAPI)
    if self.trend_manager:
        try:
            trends = trend_string.split(',')
            trends = [t.strip() for t in trends]
            
            if len(trends) < 6:
                print(f"ERROR: Incomplete MTF data for {symbol}: {trend_string}")
                return
            
            def to_direction(value: str) -> str:
                if value == "1":
                    return "BULLISH"
                elif value == "-1":
                    return "BEARISH"
                else:
                    return "NEUTRAL"
            
            # Update only 4 pillars (15m, 1H, 4H, 1D)
            self.trend_manager.update_trend(symbol, "15m", to_direction(trends[2]), "AUTO")
            self.trend_manager.update_trend(symbol, "1h", to_direction(trends[3]), "AUTO")
            self.trend_manager.update_trend(symbol, "4h", to_direction(trends[4]), "AUTO")
            self.trend_manager.update_trend(symbol, "1d", to_direction(trends[5]), "AUTO")
            
        except Exception as e:
            print(f"ERROR: MTF Parsing Error [{symbol}]: {e}")
```

### 2.2 Functions to KEEP (No Changes)

| Function | Lines | Reason |
|----------|-------|--------|
| `__init__()` | 8-13 | Core initialization |
| `validate_alert()` | 136-150 | Alert routing (keep for now) |
| `is_duplicate_alert()` | 153-204 | Duplicate detection |
| `is_valid_symbol()` | 206-210 | Symbol validation |
| `clean_old_alerts()` | 212-237 | Alert cleanup |
| `get_recent_alerts()` | 239-252 | Alert retrieval |
| `store_entry_alert()` | 254-265 | Alert storage |

---

## PART 3: VERIFICATION CHECKLIST

After cleanup, verify:

- [ ] trading_engine.py has NO hardcoded V3 logic
- [ ] trading_engine.py has NO hardcoded V6 logic
- [ ] trading_engine.py ONLY routes to plugins
- [ ] alert_processor.py has NO business logic
- [ ] Logic flags are in plugin configs, not core
- [ ] enable_logic() uses plugin registry
- [ ] disable_logic() uses plugin registry
- [ ] All deleted functions exist in plugins

---

## PART 4: ROLLBACK PLAN

If cleanup causes issues:

1. **Git Revert:** All changes will be in a single commit, can be reverted
2. **Backup:** Original trading_engine.py saved as trading_engine.py.backup
3. **Feature Flag:** Add `use_plugin_routing` config flag to switch between old and new

---

## SUCCESS CRITERIA

Core files contain ZERO trading decisions:
- No lot size calculations
- No SL/TP calculations
- No routing logic (Logic1/2/3)
- No order placement logic
- No exit handling logic
- No reversal handling logic

Core files ONLY:
- Parse incoming alerts
- Route to correct plugin
- Execute plugin decisions
- Manage lifecycle
