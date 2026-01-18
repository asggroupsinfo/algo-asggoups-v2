# AUTONOMOUS SYSTEM

**File:** `src/managers/autonomous_system_manager.py`  
**Lines:** 1551  
**Purpose:** Central manager for all autonomous trading operations

---

## OVERVIEW

The Autonomous System Manager coordinates all automated trading operations including:

1. **TP Continuation:** Continue trades after TP hit
2. **SL Hunt Recovery:** Recover from SL hits
3. **Profit Booking SL Hunt:** Recovery for Order B chains
4. **Exit Continuation:** Re-enter after exit signals
5. **Safety Checks:** Enforce daily limits and protections
6. **Reverse Shield:** Protection against trend reversals

---

## AUTONOMOUS OPERATIONS

### Operation Types

| Operation | Trigger | Action |
|-----------|---------|--------|
| TP Continuation | TP hit on Order A | Open new trade in same direction |
| SL Hunt Recovery | SL hit on Order A | Monitor for 70% recovery |
| Profit Booking SL Hunt | SL hit on Order B | Monitor for recovery |
| Exit Continuation | Exit signal | Re-enter when trend resumes |
| Reverse Shield | Trend reversal detected | Close positions, block new entries |

---

## CLASS STRUCTURE

### Definition (Lines 17-78)

```python
class AutonomousSystemManager:
    """
    Central manager for all autonomous trading operations
    Coordinates re-entry, SL hunt, and profit booking systems
    """
    
    def __init__(self, config: Config, reentry_manager: ReEntryManager,
                 profit_booking_manager: ProfitBookingManager,
                 mt5_client: MT5Client, db: TradeDatabase = None):
        self.config = config
        self.reentry_manager = reentry_manager
        self.profit_booking_manager = profit_booking_manager
        self.mt5_client = mt5_client
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Active recovery operations
        self.active_recoveries: Dict[str, Dict] = {}
        
        # Safety statistics
        self.daily_stats = {
            "recovery_attempts": 0,
            "recovery_successes": 0,
            "recovery_failures": 0,
            "profit_booked": 0.0,
            "losses_from_recovery": 0.0
        }
        
        # Reverse shield state
        self.reverse_shields: Dict[str, Dict] = {}
        
        # Load config
        self.autonomous_config = config.get("re_entry_config", {}).get("autonomous_config", {})
```

---

## MAIN AUTONOMOUS LOOP

### Run Autonomous Checks (Lines 80-180)

```python
async def run_autonomous_checks(self, open_trades: List[Trade], 
                               trading_engine) -> Dict[str, Any]:
    """
    Main autonomous operations loop - called by TradingEngine.
    
    Checks:
    1. Profit booking targets
    2. SL hunt recovery opportunities
    3. TP continuation opportunities
    4. Exit continuation opportunities
    5. Reverse shield triggers
    
    Args:
        open_trades: List of currently open trades
        trading_engine: Reference to TradingEngine for order execution
        
    Returns:
        dict: Summary of actions taken
    """
    results = {
        "profit_targets_hit": [],
        "recoveries_triggered": [],
        "continuations_triggered": [],
        "reverse_shields_activated": [],
        "errors": []
    }
    
    try:
        # Get current prices
        symbols = set(t.symbol for t in open_trades)
        current_prices = {}
        for symbol in symbols:
            current_prices[symbol] = self.mt5_client.get_current_price(symbol)
        
        # 1. Check profit booking targets
        profit_hits = self.profit_booking_manager.check_profit_targets(current_prices)
        for hit in profit_hits:
            result = await self.profit_booking_manager.handle_profit_target_hit(
                hit["chain_id"], hit["order_id"], hit["current_price"]
            )
            if result["success"]:
                results["profit_targets_hit"].append(hit)
                self.daily_stats["profit_booked"] += result.get("profit_booked", 0)
        
        # 2. Check SL hunt recovery opportunities
        recovery_chains = self.reentry_manager.get_chains_in_recovery_mode()
        for chain in recovery_chains:
            current_price = current_prices.get(chain.symbol)
            if current_price:
                recovery_result = self.reentry_manager.check_sl_hunt_recovery(
                    chain, current_price
                )
                if recovery_result["eligible"]:
                    # Execute recovery trade
                    trade_result = await self._execute_recovery_trade(
                        chain, recovery_result, trading_engine
                    )
                    if trade_result["success"]:
                        results["recoveries_triggered"].append({
                            "chain_id": chain.chain_id,
                            "level": recovery_result["next_level_on_success"]
                        })
        
        # 3. Check TP continuation opportunities
        tp_chains = self.reentry_manager.get_chains_awaiting_continuation()
        for chain in tp_chains:
            current_price = current_prices.get(chain.symbol)
            if current_price:
                continuation_result = await self._check_tp_continuation(
                    chain, current_price, trading_engine
                )
                if continuation_result["triggered"]:
                    results["continuations_triggered"].append({
                        "chain_id": chain.chain_id,
                        "type": "tp_continuation"
                    })
        
        # 4. Check reverse shield triggers
        for symbol, price in current_prices.items():
            shield_result = await self._check_reverse_shield(symbol, price, open_trades)
            if shield_result["activated"]:
                results["reverse_shields_activated"].append({
                    "symbol": symbol,
                    "reason": shield_result["reason"]
                })
        
    except Exception as e:
        self.logger.error(f"Autonomous check error: {e}")
        results["errors"].append(str(e))
    
    return results
```

---

## RECOVERY EXECUTION

### Execute Recovery Trade (Lines 182-280)

```python
async def _execute_recovery_trade(self, chain, recovery_result: Dict,
                                 trading_engine) -> Dict[str, Any]:
    """
    Execute a recovery trade for SL hunt.
    
    Args:
        chain: ReEntryChain in recovery mode
        recovery_result: Result from check_sl_hunt_recovery
        trading_engine: Reference to TradingEngine
        
    Returns:
        dict: Execution result
    """
    result = {"success": False}
    
    # Safety check
    safety_result = await self.check_safety_limits()
    if not safety_result["allowed"]:
        result["error"] = f"Safety check failed: {safety_result['reason']}"
        return result
    
    try:
        # Get lot size from chain metadata
        lot_size = chain.metadata.get("actual_lot_size", 0.01)
        
        # Create recovery trade
        trade = Trade(
            symbol=chain.symbol,
            entry=recovery_result["entry_price"],
            sl=recovery_result["tight_sl_price"],
            tp=None,  # Will be calculated
            lot_size=lot_size,
            direction=chain.direction,
            strategy=chain.metadata.get("logic", "V3_COMBINED"),
            open_time=datetime.now().isoformat(),
            order_type="SL_HUNT_RECOVERY"
        )
        
        # Calculate TP
        sl_distance = abs(trade.entry - trade.sl)
        rr_ratio = self.config.get("rr_ratio", 2.0)
        
        if chain.direction.lower() in ["buy", "bull"]:
            trade.tp = trade.entry + (sl_distance * rr_ratio)
        else:
            trade.tp = trade.entry - (sl_distance * rr_ratio)
        
        # Place order
        trade_id = await trading_engine.open_trade(trade)
        
        if trade_id:
            # Update chain
            chain.current_level = recovery_result["next_level_on_success"]
            chain.status = "active"
            chain.trades.append(trade_id)
            chain.last_update = datetime.now().isoformat()
            
            # Update stats
            self.daily_stats["recovery_attempts"] += 1
            
            result["success"] = True
            result["trade_id"] = trade_id
            
            self.logger.info(f"Recovery trade placed: #{trade_id} for chain {chain.chain_id}")
        else:
            result["error"] = "Failed to place recovery trade"
            
    except Exception as e:
        result["error"] = str(e)
        self.logger.error(f"Recovery execution error: {e}")
    
    return result
```

---

## SAFETY CHECKS

### Check Safety Limits (Lines 350-450)

```python
async def check_safety_limits(self) -> Dict[str, Any]:
    """
    Check if autonomous operations are safe to proceed.
    
    Checks:
    1. Daily recovery attempt limit
    2. Daily recovery loss limit
    3. Concurrent recovery limit
    4. Profit protection threshold
    
    Returns:
        dict: {"allowed": bool, "reason": str}
    """
    result = {"allowed": True, "reason": ""}
    
    safety_config = self.autonomous_config.get("safety_limits", {})
    
    # Check daily recovery attempts
    max_daily_attempts = safety_config.get("daily_recovery_attempts", 10)
    if self.daily_stats["recovery_attempts"] >= max_daily_attempts:
        result["allowed"] = False
        result["reason"] = f"Daily recovery limit reached ({max_daily_attempts})"
        return result
    
    # Check daily recovery losses
    max_daily_losses = safety_config.get("daily_recovery_losses", 5)
    if self.daily_stats["recovery_failures"] >= max_daily_losses:
        result["allowed"] = False
        result["reason"] = f"Daily recovery loss limit reached ({max_daily_losses})"
        return result
    
    # Check concurrent recoveries
    max_concurrent = safety_config.get("max_concurrent_recoveries", 3)
    active_count = len([r for r in self.active_recoveries.values() if r["status"] == "active"])
    if active_count >= max_concurrent:
        result["allowed"] = False
        result["reason"] = f"Max concurrent recoveries reached ({max_concurrent})"
        return result
    
    # Check profit protection
    profit_protection = safety_config.get("profit_protection", {})
    if profit_protection.get("enabled", False):
        daily_profit = self.daily_stats["profit_booked"]
        threshold = profit_protection.get("threshold", 100)
        
        if daily_profit >= threshold:
            result["allowed"] = False
            result["reason"] = f"Profit protection active (${daily_profit:.2f} >= ${threshold})"
            return result
    
    return result
```

### Check Daily Limits (Lines 452-500)

```python
def check_daily_limits(self) -> bool:
    """
    Quick check if daily limits allow more operations.
    
    Returns:
        bool: True if operations allowed
    """
    safety_config = self.autonomous_config.get("safety_limits", {})
    
    # Check attempts
    if self.daily_stats["recovery_attempts"] >= safety_config.get("daily_recovery_attempts", 10):
        return False
    
    # Check losses
    if self.daily_stats["recovery_failures"] >= safety_config.get("daily_recovery_losses", 5):
        return False
    
    return True
```

---

## REVERSE SHIELD

### Check Reverse Shield (Lines 550-650)

```python
async def _check_reverse_shield(self, symbol: str, current_price: float,
                               open_trades: List[Trade]) -> Dict[str, Any]:
    """
    Check if reverse shield should be activated.
    
    Reverse shield protects against trend reversals by:
    1. Detecting strong reversal signals
    2. Closing all positions in affected direction
    3. Blocking new entries until reversal completes
    
    Args:
        symbol: Trading symbol
        current_price: Current price
        open_trades: List of open trades
        
    Returns:
        dict: {"activated": bool, "reason": str}
    """
    result = {"activated": False, "reason": ""}
    
    shield_config = self.autonomous_config.get("reverse_shield", {})
    if not shield_config.get("enabled", False):
        return result
    
    # Check if shield already active for this symbol
    if symbol in self.reverse_shields:
        shield = self.reverse_shields[symbol]
        if shield["status"] == "active":
            return result
    
    # Get symbol trades
    symbol_trades = [t for t in open_trades if t.symbol == symbol]
    if not symbol_trades:
        return result
    
    # Check for reversal conditions
    reversal_detected = await self._detect_reversal(symbol, current_price, symbol_trades)
    
    if reversal_detected["is_reversal"]:
        # Activate reverse shield
        self.reverse_shields[symbol] = {
            "status": "active",
            "direction_blocked": reversal_detected["blocked_direction"],
            "activated_at": datetime.now().isoformat(),
            "reason": reversal_detected["reason"],
            "trades_closed": []
        }
        
        # Close affected trades
        for trade in symbol_trades:
            if trade.direction == reversal_detected["blocked_direction"]:
                # Close trade
                close_result = self.mt5_client.close_position(trade.trade_id)
                if close_result:
                    self.reverse_shields[symbol]["trades_closed"].append(trade.trade_id)
        
        result["activated"] = True
        result["reason"] = reversal_detected["reason"]
        
        self.logger.warning(f"Reverse Shield ACTIVATED for {symbol}: {reversal_detected['reason']}")
    
    return result
```

### Detect Reversal (Lines 652-720)

```python
async def _detect_reversal(self, symbol: str, current_price: float,
                          trades: List[Trade]) -> Dict[str, Any]:
    """
    Detect if a trend reversal is occurring.
    
    Detection criteria:
    1. Price moved against position by > 2x SL distance
    2. Multiple consecutive candles against position
    3. Key support/resistance broken
    
    Args:
        symbol: Trading symbol
        current_price: Current price
        trades: Open trades for this symbol
        
    Returns:
        dict: {"is_reversal": bool, "blocked_direction": str, "reason": str}
    """
    result = {"is_reversal": False, "blocked_direction": "", "reason": ""}
    
    shield_config = self.autonomous_config.get("reverse_shield", {})
    reversal_threshold = shield_config.get("reversal_threshold_multiplier", 2.0)
    
    for trade in trades:
        # Calculate how far price has moved against position
        if trade.direction.lower() in ["buy", "bull"]:
            adverse_move = trade.entry - current_price
            sl_distance = trade.entry - trade.sl
        else:
            adverse_move = current_price - trade.entry
            sl_distance = trade.sl - trade.entry
        
        # Check if adverse move exceeds threshold
        if sl_distance > 0 and adverse_move > (sl_distance * reversal_threshold):
            result["is_reversal"] = True
            result["blocked_direction"] = trade.direction
            result["reason"] = f"Price moved {adverse_move/sl_distance:.1f}x SL distance against position"
            break
    
    return result
```

### Deactivate Reverse Shield (Lines 722-760)

```python
def deactivate_reverse_shield(self, symbol: str) -> bool:
    """
    Deactivate reverse shield for a symbol.
    
    Args:
        symbol: Trading symbol
        
    Returns:
        bool: True if deactivated
    """
    if symbol in self.reverse_shields:
        shield = self.reverse_shields[symbol]
        shield["status"] = "deactivated"
        shield["deactivated_at"] = datetime.now().isoformat()
        
        self.logger.info(f"Reverse Shield DEACTIVATED for {symbol}")
        return True
    
    return False

def is_direction_blocked(self, symbol: str, direction: str) -> bool:
    """
    Check if a direction is blocked by reverse shield.
    
    Args:
        symbol: Trading symbol
        direction: Trade direction
        
    Returns:
        bool: True if blocked
    """
    if symbol in self.reverse_shields:
        shield = self.reverse_shields[symbol]
        if shield["status"] == "active":
            return shield["blocked_direction"] == direction
    
    return False
```

---

## REGISTRATION METHODS

### Register SL Recovery (Lines 800-850)

```python
def register_sl_recovery(self, trade: Trade, strategy: str):
    """
    Register a trade for SL hunt recovery monitoring.
    
    Args:
        trade: Trade that hit SL
        strategy: Strategy name
    """
    recovery_id = f"SL_{trade.trade_id}_{datetime.now().timestamp()}"
    
    self.active_recoveries[recovery_id] = {
        "type": "sl_hunt",
        "trade_id": trade.trade_id,
        "chain_id": trade.chain_id,
        "symbol": trade.symbol,
        "direction": trade.direction,
        "sl_price": trade.sl,
        "original_entry": trade.original_entry or trade.entry,
        "strategy": strategy,
        "status": "monitoring",
        "registered_at": datetime.now().isoformat()
    }
    
    self.logger.info(f"SL Recovery registered: {recovery_id}")
```

### Register TP Continuation (Lines 852-900)

```python
def register_tp_continuation(self, trade: Trade, tp_price: float):
    """
    Register a trade for TP continuation monitoring.
    
    Args:
        trade: Trade that hit TP
        tp_price: TP price hit
    """
    continuation_id = f"TP_{trade.trade_id}_{datetime.now().timestamp()}"
    
    self.active_recoveries[continuation_id] = {
        "type": "tp_continuation",
        "trade_id": trade.trade_id,
        "chain_id": trade.chain_id,
        "symbol": trade.symbol,
        "direction": trade.direction,
        "tp_price": tp_price,
        "status": "awaiting_continuation",
        "registered_at": datetime.now().isoformat()
    }
    
    self.logger.info(f"TP Continuation registered: {continuation_id}")
```

---

## STATISTICS

### Get Safety Stats (Lines 950-1000)

```python
def get_safety_stats(self) -> Dict[str, Any]:
    """
    Get current safety statistics.
    
    Returns:
        dict: Safety statistics
    """
    safety_config = self.autonomous_config.get("safety_limits", {})
    
    return {
        "daily_stats": self.daily_stats.copy(),
        "limits": {
            "max_daily_attempts": safety_config.get("daily_recovery_attempts", 10),
            "max_daily_losses": safety_config.get("daily_recovery_losses", 5),
            "max_concurrent": safety_config.get("max_concurrent_recoveries", 3)
        },
        "active_recoveries": len(self.active_recoveries),
        "active_shields": len([s for s in self.reverse_shields.values() if s["status"] == "active"])
    }

def reset_daily_stats(self):
    """Reset daily statistics (called at day rollover)"""
    self.daily_stats = {
        "recovery_attempts": 0,
        "recovery_successes": 0,
        "recovery_failures": 0,
        "profit_booked": 0.0,
        "losses_from_recovery": 0.0
    }
    self.logger.info("Daily autonomous stats reset")
```

---

## CONFIGURATION

### Autonomous Config

```python
{
    "re_entry_config": {
        "autonomous_config": {
            "sl_hunt_recovery": {
                "enabled": true,
                "recovery_threshold_percent": 70,
                "tight_sl_multiplier": 0.5,
                "recovery_windows_by_symbol": {
                    "EURUSD": 30,
                    "GBPUSD": 25,
                    "XAUUSD": 20
                }
            },
            "tp_continuation": {
                "enabled": true,
                "continuation_window_minutes": 30
            },
            "safety_limits": {
                "daily_recovery_attempts": 10,
                "daily_recovery_losses": 5,
                "max_concurrent_recoveries": 3,
                "profit_protection": {
                    "enabled": true,
                    "threshold": 100
                }
            },
            "reverse_shield": {
                "enabled": true,
                "reversal_threshold_multiplier": 2.0,
                "auto_deactivate_minutes": 60
            }
        }
    }
}
```

---

## PLUGIN-SPECIFIC RE-ENTRY CHAIN METHODS (Lines 1360-1550)

### V5.1 Addition: Database-Isolated Re-Entry Chain Management

These methods provide plugin-specific database queries for re-entry chains, ensuring V3 and V6 plugins use their isolated databases.

### Get Re-Entry Chains by Plugin (Lines 1360-1409)

```python
async def get_reentry_chains_by_plugin(self, plugin_id: str) -> list:
    """
    Get active re-entry chains for a specific plugin from the appropriate database.
    
    V3 plugins query v3_reentry_chains from zepix_combined_v3.db
    V6 plugins query v6_reentry_chains from zepix_price_action.db
    
    Args:
        plugin_id: Plugin identifier (e.g., 'combined_v3', 'price_action_5m')
        
    Returns:
        List of active re-entry chain records
    """
    # Routes to correct database based on plugin_id
    if 'v3' in plugin_id.lower() or 'combined' in plugin_id.lower():
        db_path = 'data/zepix_combined_v3.db'
        table_name = 'v3_reentry_chains'
    else:
        db_path = 'data/zepix_price_action.db'
        table_name = 'v6_reentry_chains'
    
    # Query with plugin_id filter
    cursor.execute(f'''
        SELECT * FROM {table_name}
        WHERE plugin_id = ? AND status IN ('ACTIVE', 'RECOVERY_MODE')
        ORDER BY created_at DESC
    ''', (plugin_id,))
```

### Save Re-Entry Chain (Lines 1411-1482)

```python
async def save_reentry_chain(self, chain_data: dict) -> bool:
    """
    Save a re-entry chain to the appropriate plugin-specific database.
    
    Args:
        chain_data: Dictionary with chain details including plugin_id
        
    Returns:
        True if saved successfully
    """
    # Routes to correct database based on plugin_id
    # Inserts chain with all required fields
```

### Update Re-Entry Chain Status (Lines 1484-1546)

```python
async def update_reentry_chain_status(
    self, 
    chain_id: str, 
    plugin_id: str, 
    status: str,
    stop_reason: str = None
) -> bool:
    """
    Update the status of a re-entry chain.
    
    Args:
        chain_id: Chain identifier
        plugin_id: Plugin identifier
        status: New status ('ACTIVE', 'RECOVERY_MODE', 'STOPPED', 'COMPLETED')
        stop_reason: Optional reason for stopping
        
    Returns:
        True if updated successfully
    """
```

### Get Daily Recovery Count (Lines 1548-1550)

```python
async def get_daily_recovery_count(self) -> int:
    """Get the count of recovery attempts today"""
    return self.daily_stats.get("recovery_attempts", 0)
```

---

## RELATED FILES

- `src/core/trading_engine.py` - Uses AutonomousSystemManager
- `src/managers/reentry_manager.py` - Re-entry chain management
- `src/managers/profit_booking_manager.py` - Profit booking chains
- `src/managers/recovery_window_monitor.py` - Recovery monitoring
- `data/schemas/combined_v3_schema.sql` - V3 re-entry chains table
- `data/schemas/price_action_v6_schema.sql` - V6 re-entry chains table
