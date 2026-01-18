# CORE TRADING ENGINE

**File:** `src/core/trading_engine.py`  
**Lines:** 2439  
**Purpose:** Central orchestration hub for all trading operations

---

## OVERVIEW

The TradingEngine is the heart of the Zepix V5 system. It coordinates all trading operations, delegates signals to plugins, manages the shadow mode system, and integrates with the 3-bot Telegram architecture.

### Key Responsibilities

1. **Signal Processing:** Receives alerts from TradingView and routes them to appropriate plugins
2. **Plugin Delegation:** Delegates ALL signal processing to registered plugins
3. **Shadow Mode Management:** Coordinates parallel execution of legacy and plugin systems
4. **Order Management:** Tracks all open trades and manages their lifecycle
5. **Telegram Integration:** Sends notifications through the 3-bot system
6. **Autonomous Operations:** Coordinates re-entry, profit booking, and recovery systems

---

## CLASS STRUCTURE

```python
class TradingEngine:
    """
    Central trading orchestration engine.
    
    Attributes:
        config: Configuration dictionary
        mt5_client: MT5Client for broker operations
        plugin_registry: PluginRegistry for plugin management
        service_api: ServiceAPI for unified service access
        shadow_mode_manager: ShadowModeManager for testing
        multi_telegram_manager: MultiTelegramManager for notifications
        risk_manager: RiskManager for risk calculations
        reentry_manager: ReEntryManager for recovery operations
        dual_order_manager: DualOrderManager for dual orders
        profit_booking_manager: ProfitBookingManager for profit chains
        autonomous_system_manager: AutonomousSystemManager for autonomous ops
    """
```

---

## INITIALIZATION

### Constructor (Lines 27-150)

```python
def __init__(self, config: Dict[str, Any]):
    """
    Initialize TradingEngine with all dependencies.
    
    Args:
        config: Configuration dictionary with all settings
    """
    self.config = config
    
    # Core clients
    self.mt5_client = MT5Client(config)
    self.db = TradeDatabase()
    
    # Plugin system
    self.plugin_registry = PluginRegistry(config)
    self.service_api = ServiceAPI(config, self.mt5_client, self.db)
    
    # Shadow mode
    self.shadow_mode_manager = ShadowModeManager(config)
    
    # Telegram (3-bot system)
    self.multi_telegram_manager = MultiTelegramManager(config)
    
    # Managers
    self.risk_manager = RiskManager(config)
    self.pip_calculator = PipCalculator(config)
    self.reentry_manager = ReEntryManager(config, self.mt5_client)
    self.dual_order_manager = DualOrderManager(...)
    self.profit_booking_manager = ProfitBookingManager(...)
    self.autonomous_system_manager = AutonomousSystemManager(...)
    
    # Initialize plugins
    self._initialize_plugins()
```

### Plugin Initialization (Lines 152-200)

```python
def _initialize_plugins(self):
    """
    Initialize all registered plugins with ServiceAPI.
    
    This method:
    1. Loads all enabled plugins from registry
    2. Injects ServiceAPI into each plugin
    3. Registers plugins with shadow mode manager
    """
    for plugin_id, plugin in self.plugin_registry.get_all_plugins().items():
        plugin.set_service_api(self.service_api)
        self.shadow_mode_manager.register_plugin(plugin_id, plugin)
        logger.info(f"Plugin initialized: {plugin_id}")
```

---

## SIGNAL PROCESSING

### Main Entry Point (Lines 250-310)

```python
async def process_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for processing TradingView alerts.
    
    Flow:
    1. Parse alert data
    2. Validate signal
    3. Check execution mode (shadow/plugin)
    4. Delegate to appropriate handler
    5. Return result
    
    Args:
        alert_data: Raw alert data from TradingView
        
    Returns:
        dict: Processing result with status and details
    """
    # Parse alert
    parsed = self.alert_processor.parse_alert(alert_data)
    
    # Check execution mode
    mode = self.shadow_mode_manager.get_execution_mode()
    
    if mode == ExecutionMode.LEGACY_ONLY:
        return await self._process_legacy(parsed)
    elif mode == ExecutionMode.SHADOW:
        # Run both, only legacy executes
        legacy_result = await self._process_legacy(parsed)
        plugin_result = await self.delegate_to_plugin(parsed)
        self.shadow_mode_manager.compare_results(legacy_result, plugin_result)
        return legacy_result
    elif mode == ExecutionMode.PLUGIN_SHADOW:
        # Run both, only plugins execute
        legacy_result = await self._process_legacy_shadow(parsed)
        plugin_result = await self.delegate_to_plugin(parsed)
        self.shadow_mode_manager.compare_results(legacy_result, plugin_result)
        return plugin_result
    else:  # PLUGIN_ONLY
        return await self.delegate_to_plugin(parsed)
```

### Plugin Delegation (Lines 315-365)

**CRITICAL:** This is the ONLY entry point for plugin-based signal processing.

```python
async def delegate_to_plugin(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delegate signal processing to the appropriate plugin.
    This is the ONLY entry point for plugin-based signal processing.
    
    Args:
        signal_data: Signal data dictionary
        
    Returns:
        dict: Plugin execution result or error dict
    """
    # Find the right plugin
    plugin = self.plugin_registry.get_plugin_for_signal(signal_data)
    
    if not plugin:
        logger.warning(f"No plugin found for signal: {signal_data.get('strategy', 'unknown')}")
        return {"status": "error", "message": "no_plugin_found"}
    
    # Log delegation
    logger.info(f"Delegating signal to plugin: {plugin.plugin_id}")
    
    # Execute plugin
    try:
        result = await plugin.process_signal(signal_data)
        
        # Track execution
        self.shadow_mode_manager.record_plugin_execution(
            plugin.plugin_id, signal_data, result
        )
        
        return result
    except Exception as e:
        logger.error(f"Plugin execution error: {e}")
        return {"status": "error", "message": str(e)}
```

---

## ORDER MANAGEMENT

### Open Trade (Lines 400-500)

```python
async def open_trade(self, trade: Trade) -> Optional[int]:
    """
    Open a new trade via MT5.
    
    Args:
        trade: Trade object with all parameters
        
    Returns:
        int: Trade ID if successful, None otherwise
    """
    # Validate risk
    if not self.risk_manager.validate_trade(trade):
        logger.warning(f"Trade rejected by risk manager: {trade.symbol}")
        return None
    
    # Place order
    trade_id = self.mt5_client.place_order(
        symbol=trade.symbol,
        order_type=trade.direction,
        lot_size=trade.lot_size,
        price=trade.entry,
        sl=trade.sl,
        tp=trade.tp,
        comment=f"{trade.strategy}_{trade.order_type}"
    )
    
    if trade_id:
        trade.trade_id = trade_id
        self.open_trades[trade_id] = trade
        
        # Send notification
        await self.multi_telegram_manager.send_trade_notification({
            'type': 'trade_opened',
            'symbol': trade.symbol,
            'direction': trade.direction,
            'price': trade.entry,
            'order_type': trade.order_type
        })
    
    return trade_id
```

### Close Trade (Lines 505-600)

```python
async def close_trade(self, trade: Trade, reason: str, 
                      close_price: float = None) -> bool:
    """
    Close an existing trade.
    
    Args:
        trade: Trade object to close
        reason: Close reason (SL_HIT, TP_HIT, MANUAL, PROFIT_BOOKING, etc.)
        close_price: Optional close price (uses current if not provided)
        
    Returns:
        bool: True if closed successfully
    """
    if close_price is None:
        close_price = self.mt5_client.get_current_price(trade.symbol)
    
    # Close via MT5
    success = self.mt5_client.close_position(trade.trade_id)
    
    if success:
        # Calculate profit
        profit = self._calculate_profit(trade, close_price)
        
        # Update trade
        trade.status = "closed"
        trade.close_price = close_price
        trade.close_time = datetime.now().isoformat()
        trade.profit = profit
        
        # Remove from open trades
        self.open_trades.pop(trade.trade_id, None)
        
        # Handle based on reason
        if reason == "SL_HIT":
            await self._handle_sl_hit(trade)
        elif reason == "TP_HIT":
            await self._handle_tp_hit(trade)
        elif reason == "PROFIT_BOOKING":
            await self._handle_profit_booking(trade)
        
        # Send notification
        await self.multi_telegram_manager.send_trade_notification({
            'type': 'trade_closed',
            'symbol': trade.symbol,
            'direction': trade.direction,
            'profit': profit,
            'reason': reason
        })
        
        # Save to database
        self.db.save_trade(trade)
    
    return success
```

---

## AUTONOMOUS OPERATIONS

### Main Loop (Lines 700-800)

```python
async def run_autonomous_loop(self):
    """
    Main autonomous operations loop.
    
    Runs continuously and checks:
    1. Profit booking targets
    2. SL hunt recovery opportunities
    3. TP continuation opportunities
    4. Exit continuation opportunities
    """
    while self.running:
        try:
            # Get open trades
            open_trades = list(self.open_trades.values())
            
            # Run autonomous checks
            await self.autonomous_system_manager.run_autonomous_checks(
                open_trades, self
            )
            
            # Sleep before next iteration
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Autonomous loop error: {e}")
            await asyncio.sleep(5)
```

### SL Hit Handler (Lines 850-950)

```python
async def _handle_sl_hit(self, trade: Trade):
    """
    Handle SL hit event - triggers recovery system.
    
    Args:
        trade: Trade that hit SL
    """
    logger.info(f"SL Hit: {trade.symbol} {trade.direction}")
    
    # Record SL hit
    self.reentry_manager.record_sl_hit(trade)
    
    # Check if recovery is allowed
    if self.autonomous_system_manager.check_daily_limits():
        # Register for SL hunt recovery
        self.autonomous_system_manager.register_sl_recovery(
            trade, trade.strategy
        )
        
        logger.info(f"SL Hunt Recovery registered for {trade.trade_id}")
```

### TP Hit Handler (Lines 955-1050)

```python
async def _handle_tp_hit(self, trade: Trade):
    """
    Handle TP hit event - triggers continuation system.
    
    Args:
        trade: Trade that hit TP
    """
    logger.info(f"TP Hit: {trade.symbol} {trade.direction}")
    
    # Record TP hit
    self.reentry_manager.record_tp_hit(trade, trade.tp)
    
    # Check for TP continuation opportunity
    # (Handled by autonomous system manager)
```

---

## SHADOW MODE INTEGRATION

### Mode Switching (Lines 1100-1150)

```python
def set_execution_mode(self, mode: ExecutionMode):
    """
    Set the execution mode for the trading engine.
    
    Args:
        mode: ExecutionMode enum value
    """
    old_mode = self.shadow_mode_manager.get_execution_mode()
    self.shadow_mode_manager.set_execution_mode(mode)
    
    logger.info(f"Execution mode changed: {old_mode} -> {mode}")
    
    # Notify via Telegram
    self.multi_telegram_manager.send_admin_message(
        f"Execution mode changed to: {mode.value}"
    )
```

### Shadow Comparison (Lines 1155-1200)

```python
def _compare_shadow_results(self, legacy_result: Dict, plugin_result: Dict):
    """
    Compare legacy and plugin results in shadow mode.
    
    Args:
        legacy_result: Result from legacy system
        plugin_result: Result from plugin system
    """
    comparison = self.shadow_mode_manager.compare_results(
        legacy_result, plugin_result
    )
    
    if comparison['mismatch']:
        logger.warning(f"Shadow mode mismatch detected: {comparison}")
        
        # Send alert
        self.multi_telegram_manager.send_admin_message(
            f"Shadow Mode Mismatch:\n"
            f"Legacy: {legacy_result.get('action')}\n"
            f"Plugin: {plugin_result.get('action')}"
        )
```

---

## TELEGRAM INTEGRATION

### Notification Routing (Lines 1300-1400)

```python
async def send_notification(self, notification_type: str, message: str, **kwargs):
    """
    Send notification through 3-bot system.
    
    Args:
        notification_type: Type of notification
        message: Notification message
        **kwargs: Additional arguments
    """
    await self.multi_telegram_manager.send_notification_async(
        notification_type, message, **kwargs
    )
```

---

## CONFIGURATION

### Required Config Keys

```python
{
    # MT5 Settings
    "mt5_login": int,
    "mt5_password": str,
    "mt5_server": str,
    
    # Telegram Settings
    "telegram_token": str,
    "telegram_chat_id": str,
    "telegram_controller_token": str,  # Optional
    "telegram_notification_token": str,  # Optional
    "telegram_analytics_token": str,  # Optional
    
    # Trading Settings
    "symbol_config": Dict,
    "risk_tiers": Dict,
    "sl_systems": Dict,
    
    # Plugin Settings
    "plugins": Dict,
    "shadow_mode": Dict,
    
    # Re-entry Settings
    "re_entry_config": Dict,
    
    # Profit Booking Settings
    "profit_booking_config": Dict
}
```

---

## INTEGRATION POINTS

### Inbound

| Source | Method | Description |
|--------|--------|-------------|
| Webhook | `process_alert()` | TradingView alerts |
| Telegram | `handle_command()` | User commands |
| Timer | `run_autonomous_loop()` | Autonomous checks |

### Outbound

| Target | Method | Description |
|--------|--------|-------------|
| MT5 | `mt5_client.*` | Order execution |
| Telegram | `multi_telegram_manager.*` | Notifications |
| Database | `db.*` | Trade persistence |
| Plugins | `delegate_to_plugin()` | Signal processing |

---

## ERROR HANDLING

### Critical Errors

```python
try:
    result = await self.delegate_to_plugin(signal_data)
except PluginNotFoundError:
    logger.error("No plugin found for signal")
    return {"status": "error", "message": "no_plugin_found"}
except PluginExecutionError as e:
    logger.error(f"Plugin execution failed: {e}")
    return {"status": "error", "message": str(e)}
except MT5ConnectionError:
    logger.critical("MT5 connection lost")
    await self._handle_mt5_disconnect()
```

---

## PERFORMANCE CONSIDERATIONS

1. **Async Operations:** All I/O operations are async
2. **Connection Pooling:** MT5 client maintains connection pool
3. **Batch Processing:** Multiple signals can be processed in parallel
4. **Caching:** Frequently accessed data is cached

---

## RELATED FILES

- `src/core/plugin_system/plugin_registry.py` - Plugin management
- `src/core/plugin_system/service_api.py` - Service layer
- `src/core/shadow_mode_manager.py` - Shadow mode
- `src/telegram/multi_telegram_manager.py` - Telegram integration
