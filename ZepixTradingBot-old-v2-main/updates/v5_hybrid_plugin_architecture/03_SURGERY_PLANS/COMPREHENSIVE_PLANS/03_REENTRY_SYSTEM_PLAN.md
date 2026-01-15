# PLAN 03: RE-ENTRY SYSTEM INTEGRATION

**Date:** 2026-01-15
**Priority:** P0 (Critical)
**Estimated Time:** 4-5 days
**Dependencies:** Plan 01 (Core Cleanup), Plan 02 (Webhook Routing)

---

## 1. OBJECTIVE

Integrate the complete Re-Entry System into the plugin architecture. This is one of the most critical plans because the Re-Entry System is the bot's core recovery mechanism. After this plan, plugins will properly trigger and manage:

1. **SL Hunt Recovery** - 70% price recovery threshold monitoring
2. **TP Continuation** - Progressive SL reduction after TP hit
3. **Exit Continuation** - 60-second monitoring after manual/reversal exit

**Current Problem (from Study Report 04, GAP-1 & Discoveries 1-4):**
- Plugins exist but NEVER call ReentryManager
- Plugins don't trigger SL Hunt Recovery
- Plugins don't use TP Continuation logic
- Plugins don't monitor Exit Continuation
- Recovery Window Monitor (626 lines) is never used by plugins
- Exit Continuation Monitor (523 lines) is never used by plugins

**Target State:**
- Plugins call ReentryManager for all recovery operations
- SL Hunt Recovery triggers automatically on SL hit
- TP Continuation activates on TP hit
- Exit Continuation monitors after exits
- All recovery windows are plugin-aware

---

## 2. SCOPE

### In-Scope:
- Wire plugins to ReentryManager
- Wire plugins to AutonomousSystemManager (for recovery limits)
- Implement SL Hunt Recovery in plugin lifecycle
- Implement TP Continuation in plugin lifecycle
- Implement Exit Continuation in plugin lifecycle
- Wire Recovery Window Monitor to plugins
- Implement chain level tracking per plugin
- Preserve symbol-specific recovery windows (10-50 minutes)

### Out-of-Scope:
- Dual Order System (Plan 04)
- Profit Booking chains (Plan 05)
- Autonomous System limits (Plan 06)
- Telegram notifications (Plan 07)

---

## 3. CURRENT STATE ANALYSIS

### File: `src/managers/reentry_manager.py`

**Current Structure (from Study Report 01, Feature 3.1-3.7):**
- Lines 1-100: Imports, class definition, initialization
- Lines 101-200: SL Hunt Recovery logic (70% threshold)
- Lines 201-300: TP Continuation logic (progressive SL reduction)
- Lines 301-400: Exit Continuation logic (60-second window)
- Lines 401-500: Recovery window management
- Lines 501-600: Chain level tracking
- Lines 601-700: Symbol-specific configurations

**Key Methods:**
```python
class ReentryManager:
    async def check_sl_hunt_recovery(self, trade_id: str, symbol: str) -> bool
    async def start_tp_continuation(self, trade_id: str, symbol: str) -> None
    async def start_exit_continuation(self, trade_id: str, symbol: str) -> None
    async def get_recovery_window(self, symbol: str) -> int  # minutes
    async def get_chain_level(self, trade_id: str) -> int
    async def increment_chain_level(self, trade_id: str) -> int
```

### File: `src/managers/recovery_window_monitor.py` (626 lines)

**Current Structure (Discovery 2):**
- Real-time 1-second price monitoring
- Checks if price recovers 70% of SL distance
- Symbol-specific windows (EURUSD: 30min, GBPUSD: 20min, etc.)
- Triggers re-entry signal on recovery

**Key Methods:**
```python
class RecoveryWindowMonitor:
    async def start_monitoring(self, trade_id: str, symbol: str, sl_price: float) -> None
    async def stop_monitoring(self, trade_id: str) -> None
    async def check_recovery(self, trade_id: str) -> bool
    def get_recovery_threshold(self, symbol: str) -> float  # 0.70 = 70%
```

### File: `src/managers/exit_continuation_monitor.py` (523 lines)

**Current Structure (Discovery 3):**
- 60-second monitoring after manual/reversal exit
- Checks for price gap opportunities
- Triggers continuation signal if conditions met

**Key Methods:**
```python
class ExitContinuationMonitor:
    async def start_monitoring(self, trade_id: str, exit_price: float) -> None
    async def stop_monitoring(self, trade_id: str) -> None
    async def check_continuation(self, trade_id: str) -> bool
```

### File: `src/logic_plugins/combined_v3/plugin.py`

**Current Problem:**
- `process_signal()` executes orders but NEVER calls ReentryManager
- No SL Hunt Recovery trigger on SL hit
- No TP Continuation trigger on TP hit
- No Exit Continuation trigger on exit

---

## 4. GAPS ADDRESSED

| Gap/Discovery | Description | How Addressed |
|---------------|-------------|---------------|
| GAP-1 | Plugin Wiring to Core | Wire plugins to ReentryManager |
| Discovery 1 | Reverse Shield System | Integrate with recovery logic |
| Discovery 2 | Recovery Window Monitor | Wire to plugin SL events |
| Discovery 3 | Exit Continuation Monitor | Wire to plugin exit events |
| Discovery 7 | Symbol-Specific Recovery Windows | Use in plugin recovery |
| Discovery 8 | Chain Level Tracking | Track per plugin |

---

## 5. IMPLEMENTATION STEPS

### Step 1: Create Re-Entry Interface for Plugins

**File:** `src/core/plugin_system/reentry_interface.py` (NEW)

**Code:**
```python
"""
Re-Entry Interface for Plugins
Defines how plugins interact with the Re-Entry System
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

class ReentryType(Enum):
    """Types of re-entry"""
    SL_HUNT = "sl_hunt"           # SL hit, monitoring for recovery
    TP_CONTINUATION = "tp_cont"   # TP hit, continuing with reduced SL
    EXIT_CONTINUATION = "exit_cont"  # Manual exit, monitoring for continuation

class ReentryEvent:
    """Event data for re-entry triggers"""
    def __init__(
        self,
        trade_id: str,
        plugin_id: str,
        symbol: str,
        reentry_type: ReentryType,
        entry_price: float,
        exit_price: float,
        sl_price: float,
        direction: str,  # 'BUY' or 'SELL'
        chain_level: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.trade_id = trade_id
        self.plugin_id = plugin_id
        self.symbol = symbol
        self.reentry_type = reentry_type
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.sl_price = sl_price
        self.direction = direction
        self.chain_level = chain_level
        self.metadata = metadata or {}

class IReentryCapable(ABC):
    """Interface for plugins that support re-entry"""
    
    @abstractmethod
    async def on_sl_hit(self, event: ReentryEvent) -> bool:
        """
        Called when SL is hit. Plugin should:
        1. Check if SL Hunt Recovery is enabled
        2. Start Recovery Window Monitor
        3. Return True if recovery monitoring started
        """
        pass
    
    @abstractmethod
    async def on_tp_hit(self, event: ReentryEvent) -> bool:
        """
        Called when TP is hit. Plugin should:
        1. Check if TP Continuation is enabled
        2. Calculate reduced SL for next entry
        3. Return True if continuation started
        """
        pass
    
    @abstractmethod
    async def on_exit(self, event: ReentryEvent) -> bool:
        """
        Called on manual/reversal exit. Plugin should:
        1. Check if Exit Continuation is enabled
        2. Start Exit Continuation Monitor
        3. Return True if monitoring started
        """
        pass
    
    @abstractmethod
    async def on_recovery_signal(self, event: ReentryEvent) -> bool:
        """
        Called when recovery conditions are met. Plugin should:
        1. Execute re-entry order
        2. Increment chain level
        3. Return True if re-entry executed
        """
        pass
    
    @abstractmethod
    def get_chain_level(self, trade_id: str) -> int:
        """Get current chain level for a trade"""
        pass
    
    @abstractmethod
    def get_max_chain_level(self) -> int:
        """Get maximum allowed chain level"""
        pass
```

**Reason:** Defines clear contract for how plugins interact with re-entry system.

---

### Step 2: Create Re-Entry Service for Plugins

**File:** `src/core/services/reentry_service.py` (NEW)

**Code:**
```python
"""
Re-Entry Service
Provides re-entry functionality to plugins via ServiceAPI
"""
from typing import Dict, Any, Optional
import logging
from src.managers.reentry_manager import ReentryManager
from src.managers.recovery_window_monitor import RecoveryWindowMonitor
from src.managers.exit_continuation_monitor import ExitContinuationMonitor
from src.managers.autonomous_system_manager import AutonomousSystemManager
from src.core.plugin_system.reentry_interface import ReentryEvent, ReentryType

logger = logging.getLogger(__name__)

class ReentryService:
    """
    Service layer for re-entry operations.
    Plugins use this instead of calling managers directly.
    """
    
    def __init__(
        self,
        reentry_manager: ReentryManager,
        recovery_monitor: RecoveryWindowMonitor,
        exit_monitor: ExitContinuationMonitor,
        autonomous_manager: AutonomousSystemManager
    ):
        self.reentry_manager = reentry_manager
        self.recovery_monitor = recovery_monitor
        self.exit_monitor = exit_monitor
        self.autonomous_manager = autonomous_manager
        
        # Track active recoveries per plugin
        self._active_recoveries: Dict[str, Dict[str, ReentryEvent]] = {}
    
    async def start_sl_hunt_recovery(self, event: ReentryEvent) -> bool:
        """
        Start SL Hunt Recovery monitoring.
        Called by plugin when SL is hit.
        """
        # Check if recovery is allowed
        if not await self._can_start_recovery(event):
            logger.info(f"Recovery not allowed for {event.trade_id}")
            return False
        
        # Get symbol-specific recovery window
        recovery_window = await self.reentry_manager.get_recovery_window(event.symbol)
        
        # Start monitoring
        await self.recovery_monitor.start_monitoring(
            trade_id=event.trade_id,
            symbol=event.symbol,
            sl_price=event.sl_price,
            entry_price=event.entry_price,
            direction=event.direction,
            recovery_window_minutes=recovery_window,
            callback=lambda: self._on_recovery_detected(event)
        )
        
        # Track active recovery
        self._track_recovery(event)
        
        logger.info(f"SL Hunt Recovery started for {event.trade_id}, window: {recovery_window}min")
        return True
    
    async def start_tp_continuation(self, event: ReentryEvent) -> bool:
        """
        Start TP Continuation.
        Called by plugin when TP is hit.
        """
        # Check chain level
        if event.chain_level >= self.get_max_chain_level(event.plugin_id):
            logger.info(f"Max chain level reached for {event.trade_id}")
            return False
        
        # Calculate reduced SL for next entry
        reduced_sl = await self._calculate_reduced_sl(event)
        
        # Start continuation
        await self.reentry_manager.start_tp_continuation(
            trade_id=event.trade_id,
            symbol=event.symbol,
            new_sl_pips=reduced_sl,
            chain_level=event.chain_level + 1
        )
        
        logger.info(f"TP Continuation started for {event.trade_id}, reduced SL: {reduced_sl} pips")
        return True
    
    async def start_exit_continuation(self, event: ReentryEvent) -> bool:
        """
        Start Exit Continuation monitoring.
        Called by plugin on manual/reversal exit.
        """
        # Check if exit continuation is enabled
        if not self.reentry_manager.exit_continuation_enabled:
            return False
        
        # Start 60-second monitoring
        await self.exit_monitor.start_monitoring(
            trade_id=event.trade_id,
            exit_price=event.exit_price,
            symbol=event.symbol,
            direction=event.direction,
            callback=lambda: self._on_continuation_detected(event)
        )
        
        logger.info(f"Exit Continuation started for {event.trade_id}")
        return True
    
    async def _can_start_recovery(self, event: ReentryEvent) -> bool:
        """Check if recovery is allowed based on limits"""
        # Check daily recovery limit
        daily_count = await self.autonomous_manager.get_daily_recovery_count()
        daily_limit = self.autonomous_manager.daily_recovery_limit
        if daily_count >= daily_limit:
            logger.warning(f"Daily recovery limit reached: {daily_count}/{daily_limit}")
            return False
        
        # Check concurrent recovery limit
        concurrent_count = self._get_concurrent_recovery_count(event.plugin_id)
        concurrent_limit = self.autonomous_manager.concurrent_recovery_limit
        if concurrent_count >= concurrent_limit:
            logger.warning(f"Concurrent recovery limit reached: {concurrent_count}/{concurrent_limit}")
            return False
        
        # Check profit protection (Discovery 4)
        if await self._should_protect_profit(event):
            logger.info(f"Profit protection active, skipping recovery for {event.trade_id}")
            return False
        
        return True
    
    async def _should_protect_profit(self, event: ReentryEvent) -> bool:
        """
        Check if existing profit should be protected.
        Discovery 4: Skip recovery if existing profit too valuable.
        """
        current_profit = await self.autonomous_manager.get_current_session_profit()
        protection_threshold = self.autonomous_manager.profit_protection_threshold
        
        return current_profit >= protection_threshold
    
    async def _calculate_reduced_sl(self, event: ReentryEvent) -> float:
        """
        Calculate reduced SL for TP Continuation.
        Progressive reduction based on chain level.
        """
        base_sl = event.metadata.get('original_sl_pips', 15)
        chain_level = event.chain_level
        
        # Reduction formula: 10% reduction per chain level
        reduction_factor = 1 - (chain_level * 0.10)
        reduction_factor = max(reduction_factor, 0.50)  # Minimum 50% of original
        
        return base_sl * reduction_factor
    
    def _track_recovery(self, event: ReentryEvent):
        """Track active recovery"""
        if event.plugin_id not in self._active_recoveries:
            self._active_recoveries[event.plugin_id] = {}
        self._active_recoveries[event.plugin_id][event.trade_id] = event
    
    def _untrack_recovery(self, plugin_id: str, trade_id: str):
        """Remove recovery from tracking"""
        if plugin_id in self._active_recoveries:
            self._active_recoveries[plugin_id].pop(trade_id, None)
    
    def _get_concurrent_recovery_count(self, plugin_id: str) -> int:
        """Get count of concurrent recoveries for a plugin"""
        if plugin_id not in self._active_recoveries:
            return 0
        return len(self._active_recoveries[plugin_id])
    
    async def _on_recovery_detected(self, event: ReentryEvent):
        """Callback when recovery conditions are met"""
        logger.info(f"Recovery detected for {event.trade_id}")
        # This will be called by RecoveryWindowMonitor
        # Plugin will handle the actual re-entry
        pass
    
    async def _on_continuation_detected(self, event: ReentryEvent):
        """Callback when continuation conditions are met"""
        logger.info(f"Continuation detected for {event.trade_id}")
        # This will be called by ExitContinuationMonitor
        # Plugin will handle the actual continuation
        pass
    
    def get_max_chain_level(self, plugin_id: str) -> int:
        """Get max chain level for a plugin"""
        # V3 plugins have higher chain limits
        if 'v3' in plugin_id.lower():
            return 5
        # V6 plugins have lower chain limits
        return 3
    
    def get_active_recoveries(self, plugin_id: str) -> Dict[str, ReentryEvent]:
        """Get all active recoveries for a plugin"""
        return self._active_recoveries.get(plugin_id, {}).copy()
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        total_active = sum(len(r) for r in self._active_recoveries.values())
        return {
            'total_active_recoveries': total_active,
            'recoveries_by_plugin': {
                pid: len(recoveries) 
                for pid, recoveries in self._active_recoveries.items()
            }
        }
```

**Reason:** Provides a clean service interface for plugins to use re-entry functionality.

---

### Step 3: Update Combined V3 Plugin with Re-Entry Support

**File:** `src/logic_plugins/combined_v3/plugin.py`

**Changes - Add Re-Entry Interface:**
```python
# ADD imports
from src.core.plugin_system.reentry_interface import IReentryCapable, ReentryEvent, ReentryType
from src.core.services.reentry_service import ReentryService

# UPDATE class definition
class CombinedV3Plugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor, IReentryCapable):
    """
    Combined V3 Logic Plugin with Re-Entry Support
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._chain_levels: Dict[str, int] = {}  # trade_id -> chain_level
        self._reentry_service: Optional[ReentryService] = None
    
    def set_reentry_service(self, service: ReentryService):
        """Inject re-entry service"""
        self._reentry_service = service
    
    # ==================== IReentryCapable Implementation ====================
    
    async def on_sl_hit(self, event: ReentryEvent) -> bool:
        """Handle SL hit - start SL Hunt Recovery"""
        if not self._reentry_service:
            logger.warning("ReentryService not available")
            return False
        
        # Check if SL Hunt is enabled in config
        if not self.config.get('sl_hunt_enabled', True):
            logger.info(f"SL Hunt disabled for {self.plugin_id}")
            return False
        
        # Start SL Hunt Recovery
        return await self._reentry_service.start_sl_hunt_recovery(event)
    
    async def on_tp_hit(self, event: ReentryEvent) -> bool:
        """Handle TP hit - start TP Continuation"""
        if not self._reentry_service:
            logger.warning("ReentryService not available")
            return False
        
        # Check if TP Continuation is enabled
        if not self.config.get('tp_continuation_enabled', True):
            logger.info(f"TP Continuation disabled for {self.plugin_id}")
            return False
        
        # Start TP Continuation
        return await self._reentry_service.start_tp_continuation(event)
    
    async def on_exit(self, event: ReentryEvent) -> bool:
        """Handle exit - start Exit Continuation"""
        if not self._reentry_service:
            logger.warning("ReentryService not available")
            return False
        
        # Check if Exit Continuation is enabled
        if not self.config.get('exit_continuation_enabled', True):
            logger.info(f"Exit Continuation disabled for {self.plugin_id}")
            return False
        
        # Start Exit Continuation
        return await self._reentry_service.start_exit_continuation(event)
    
    async def on_recovery_signal(self, event: ReentryEvent) -> bool:
        """Handle recovery signal - execute re-entry"""
        logger.info(f"Recovery signal received for {event.trade_id}")
        
        # Increment chain level
        new_level = self.increment_chain_level(event.trade_id)
        
        # Check max chain level
        if new_level > self.get_max_chain_level():
            logger.info(f"Max chain level reached for {event.trade_id}")
            return False
        
        # Execute re-entry order
        reentry_signal = {
            'strategy': 'V3_COMBINED',
            'signal_type': event.direction,
            'symbol': event.symbol,
            'timeframe': self.config.get('timeframe', '5m'),
            'is_reentry': True,
            'chain_level': new_level,
            'original_trade_id': event.trade_id,
            'reentry_type': event.reentry_type.value
        }
        
        result = await self.process_signal(reentry_signal)
        return result is not None
    
    def get_chain_level(self, trade_id: str) -> int:
        """Get current chain level"""
        return self._chain_levels.get(trade_id, 0)
    
    def increment_chain_level(self, trade_id: str) -> int:
        """Increment and return new chain level"""
        current = self._chain_levels.get(trade_id, 0)
        self._chain_levels[trade_id] = current + 1
        return self._chain_levels[trade_id]
    
    def get_max_chain_level(self) -> int:
        """Get max chain level from config"""
        return self.config.get('max_chain_level', 5)
```

**Reason:** Implements re-entry interface in V3 plugin.

---

### Step 4: Add Re-Entry Event Triggers to Order Lifecycle

**File:** `src/logic_plugins/combined_v3/order_manager.py`

**Changes - Add Event Triggers:**
```python
# ADD to V3OrderManager class

async def on_order_closed(self, order_id: str, close_reason: str, close_price: float):
    """
    Called when an order is closed.
    Triggers appropriate re-entry event based on close reason.
    """
    order = self._get_order(order_id)
    if not order:
        return
    
    # Create re-entry event
    event = ReentryEvent(
        trade_id=order['trade_id'],
        plugin_id=self.plugin.plugin_id,
        symbol=order['symbol'],
        reentry_type=self._get_reentry_type(close_reason),
        entry_price=order['entry_price'],
        exit_price=close_price,
        sl_price=order['sl_price'],
        direction=order['direction'],
        chain_level=self.plugin.get_chain_level(order['trade_id']),
        metadata={
            'original_sl_pips': order.get('sl_pips', 15),
            'close_reason': close_reason
        }
    )
    
    # Trigger appropriate event
    if close_reason == 'SL_HIT':
        await self.plugin.on_sl_hit(event)
    elif close_reason == 'TP_HIT':
        await self.plugin.on_tp_hit(event)
    elif close_reason in ['MANUAL_CLOSE', 'REVERSAL']:
        await self.plugin.on_exit(event)
    
    logger.info(f"Re-entry event triggered: {close_reason} for {order_id}")

def _get_reentry_type(self, close_reason: str) -> ReentryType:
    """Map close reason to re-entry type"""
    mapping = {
        'SL_HIT': ReentryType.SL_HUNT,
        'TP_HIT': ReentryType.TP_CONTINUATION,
        'MANUAL_CLOSE': ReentryType.EXIT_CONTINUATION,
        'REVERSAL': ReentryType.EXIT_CONTINUATION
    }
    return mapping.get(close_reason, ReentryType.SL_HUNT)
```

**Reason:** Automatically triggers re-entry events when orders close.

---

### Step 5: Wire Recovery Window Monitor to Plugins

**File:** `src/managers/recovery_window_monitor.py`

**Changes - Add Plugin Callback:**
```python
# UPDATE RecoveryWindowMonitor class

async def start_monitoring(
    self,
    trade_id: str,
    symbol: str,
    sl_price: float,
    entry_price: float,
    direction: str,
    recovery_window_minutes: int,
    callback: Optional[Callable] = None,
    plugin_id: Optional[str] = None  # NEW: Track which plugin owns this
):
    """
    Start monitoring for price recovery.
    
    Args:
        trade_id: Trade identifier
        symbol: Trading symbol
        sl_price: Stop loss price that was hit
        entry_price: Original entry price
        direction: 'BUY' or 'SELL'
        recovery_window_minutes: How long to monitor
        callback: Function to call when recovery detected
        plugin_id: Plugin that owns this recovery
    """
    # Store monitoring data
    self._monitors[trade_id] = {
        'symbol': symbol,
        'sl_price': sl_price,
        'entry_price': entry_price,
        'direction': direction,
        'recovery_threshold': self.get_recovery_threshold(symbol),  # 70%
        'window_end': datetime.now() + timedelta(minutes=recovery_window_minutes),
        'callback': callback,
        'plugin_id': plugin_id,
        'status': 'monitoring'
    }
    
    # Start monitoring task
    asyncio.create_task(self._monitor_loop(trade_id))
    
    logger.info(f"Recovery monitoring started for {trade_id}, plugin: {plugin_id}")

async def _monitor_loop(self, trade_id: str):
    """Monitor price for recovery"""
    monitor = self._monitors.get(trade_id)
    if not monitor:
        return
    
    while datetime.now() < monitor['window_end']:
        # Check if recovery detected
        if await self._check_recovery_condition(trade_id):
            logger.info(f"Recovery detected for {trade_id}")
            monitor['status'] = 'recovered'
            
            # Call callback if provided
            if monitor['callback']:
                await monitor['callback']()
            
            # Notify plugin via event system
            await self._notify_plugin_recovery(trade_id, monitor)
            break
        
        # Wait 1 second before next check
        await asyncio.sleep(1)
    
    # Window expired without recovery
    if monitor['status'] == 'monitoring':
        monitor['status'] = 'expired'
        logger.info(f"Recovery window expired for {trade_id}")

async def _notify_plugin_recovery(self, trade_id: str, monitor: Dict):
    """Notify plugin that recovery was detected"""
    plugin_id = monitor.get('plugin_id')
    if not plugin_id:
        return
    
    # Get plugin from registry
    from src.core.plugin_system.plugin_registry import PluginRegistry
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin(plugin_id)
    
    if plugin and hasattr(plugin, 'on_recovery_signal'):
        event = ReentryEvent(
            trade_id=trade_id,
            plugin_id=plugin_id,
            symbol=monitor['symbol'],
            reentry_type=ReentryType.SL_HUNT,
            entry_price=monitor['entry_price'],
            exit_price=monitor['sl_price'],
            sl_price=monitor['sl_price'],
            direction=monitor['direction']
        )
        await plugin.on_recovery_signal(event)
```

**Reason:** Connects Recovery Window Monitor to plugin system.

---

### Step 6: Wire Exit Continuation Monitor to Plugins

**File:** `src/managers/exit_continuation_monitor.py`

**Changes - Add Plugin Callback:**
```python
# UPDATE ExitContinuationMonitor class

async def start_monitoring(
    self,
    trade_id: str,
    exit_price: float,
    symbol: str,
    direction: str,
    callback: Optional[Callable] = None,
    plugin_id: Optional[str] = None
):
    """
    Start 60-second exit continuation monitoring.
    
    Args:
        trade_id: Trade identifier
        exit_price: Price at which trade was exited
        symbol: Trading symbol
        direction: Original direction ('BUY' or 'SELL')
        callback: Function to call when continuation detected
        plugin_id: Plugin that owns this monitoring
    """
    # Store monitoring data
    self._monitors[trade_id] = {
        'exit_price': exit_price,
        'symbol': symbol,
        'direction': direction,
        'window_end': datetime.now() + timedelta(seconds=60),
        'callback': callback,
        'plugin_id': plugin_id,
        'status': 'monitoring'
    }
    
    # Start monitoring task
    asyncio.create_task(self._monitor_loop(trade_id))
    
    logger.info(f"Exit continuation monitoring started for {trade_id}")

async def _monitor_loop(self, trade_id: str):
    """Monitor for continuation opportunity"""
    monitor = self._monitors.get(trade_id)
    if not monitor:
        return
    
    while datetime.now() < monitor['window_end']:
        # Check for price gap opportunity
        if await self._check_continuation_condition(trade_id):
            logger.info(f"Continuation opportunity detected for {trade_id}")
            monitor['status'] = 'continuation_detected'
            
            # Call callback
            if monitor['callback']:
                await monitor['callback']()
            
            # Notify plugin
            await self._notify_plugin_continuation(trade_id, monitor)
            break
        
        # Check every second
        await asyncio.sleep(1)
    
    # Window expired
    if monitor['status'] == 'monitoring':
        monitor['status'] = 'expired'
        logger.info(f"Exit continuation window expired for {trade_id}")

async def _notify_plugin_continuation(self, trade_id: str, monitor: Dict):
    """Notify plugin of continuation opportunity"""
    plugin_id = monitor.get('plugin_id')
    if not plugin_id:
        return
    
    from src.core.plugin_system.plugin_registry import PluginRegistry
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin(plugin_id)
    
    if plugin and hasattr(plugin, 'on_recovery_signal'):
        event = ReentryEvent(
            trade_id=trade_id,
            plugin_id=plugin_id,
            symbol=monitor['symbol'],
            reentry_type=ReentryType.EXIT_CONTINUATION,
            entry_price=monitor['exit_price'],
            exit_price=monitor['exit_price'],
            sl_price=0,  # Will be calculated
            direction=monitor['direction']
        )
        await plugin.on_recovery_signal(event)
```

**Reason:** Connects Exit Continuation Monitor to plugin system.

---

### Step 7: Create Re-Entry Integration Tests

**File:** `tests/test_reentry_integration.py` (NEW)

**Code:**
```python
"""
Tests for Re-Entry System Integration
Verifies plugins properly trigger and handle re-entry events
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.plugin_system.reentry_interface import ReentryEvent, ReentryType
from src.core.services.reentry_service import ReentryService
from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin

class TestReentryInterface:
    """Test re-entry interface implementation"""
    
    @pytest.fixture
    def v3_plugin(self):
        """Create V3 plugin with mock services"""
        config = {
            'sl_hunt_enabled': True,
            'tp_continuation_enabled': True,
            'exit_continuation_enabled': True,
            'max_chain_level': 5
        }
        plugin = CombinedV3Plugin(config)
        
        # Mock re-entry service
        mock_service = MagicMock(spec=ReentryService)
        mock_service.start_sl_hunt_recovery = AsyncMock(return_value=True)
        mock_service.start_tp_continuation = AsyncMock(return_value=True)
        mock_service.start_exit_continuation = AsyncMock(return_value=True)
        plugin.set_reentry_service(mock_service)
        
        return plugin
    
    @pytest.fixture
    def sl_hit_event(self):
        """Create SL hit event"""
        return ReentryEvent(
            trade_id='trade_001',
            plugin_id='combined_v3',
            symbol='EURUSD',
            reentry_type=ReentryType.SL_HUNT,
            entry_price=1.0850,
            exit_price=1.0835,
            sl_price=1.0835,
            direction='BUY',
            chain_level=0
        )
    
    @pytest.mark.asyncio
    async def test_on_sl_hit_starts_recovery(self, v3_plugin, sl_hit_event):
        """Test SL hit triggers SL Hunt Recovery"""
        result = await v3_plugin.on_sl_hit(sl_hit_event)
        
        assert result == True
        v3_plugin._reentry_service.start_sl_hunt_recovery.assert_called_once_with(sl_hit_event)
    
    @pytest.mark.asyncio
    async def test_on_sl_hit_disabled(self, v3_plugin, sl_hit_event):
        """Test SL hit does nothing when disabled"""
        v3_plugin.config['sl_hunt_enabled'] = False
        
        result = await v3_plugin.on_sl_hit(sl_hit_event)
        
        assert result == False
        v3_plugin._reentry_service.start_sl_hunt_recovery.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_on_tp_hit_starts_continuation(self, v3_plugin):
        """Test TP hit triggers TP Continuation"""
        event = ReentryEvent(
            trade_id='trade_002',
            plugin_id='combined_v3',
            symbol='EURUSD',
            reentry_type=ReentryType.TP_CONTINUATION,
            entry_price=1.0850,
            exit_price=1.0880,
            sl_price=1.0835,
            direction='BUY',
            chain_level=1
        )
        
        result = await v3_plugin.on_tp_hit(event)
        
        assert result == True
        v3_plugin._reentry_service.start_tp_continuation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_on_exit_starts_monitoring(self, v3_plugin):
        """Test manual exit triggers Exit Continuation"""
        event = ReentryEvent(
            trade_id='trade_003',
            plugin_id='combined_v3',
            symbol='GBPUSD',
            reentry_type=ReentryType.EXIT_CONTINUATION,
            entry_price=1.2650,
            exit_price=1.2660,
            sl_price=1.2630,
            direction='BUY',
            chain_level=0
        )
        
        result = await v3_plugin.on_exit(event)
        
        assert result == True
        v3_plugin._reentry_service.start_exit_continuation.assert_called_once()
    
    def test_chain_level_tracking(self, v3_plugin):
        """Test chain level increments correctly"""
        trade_id = 'trade_004'
        
        assert v3_plugin.get_chain_level(trade_id) == 0
        
        level1 = v3_plugin.increment_chain_level(trade_id)
        assert level1 == 1
        
        level2 = v3_plugin.increment_chain_level(trade_id)
        assert level2 == 2
        
        assert v3_plugin.get_chain_level(trade_id) == 2

class TestReentryService:
    """Test re-entry service"""
    
    @pytest.fixture
    def reentry_service(self):
        """Create re-entry service with mocks"""
        mock_reentry_mgr = MagicMock()
        mock_reentry_mgr.get_recovery_window = AsyncMock(return_value=30)
        
        mock_recovery_monitor = MagicMock()
        mock_recovery_monitor.start_monitoring = AsyncMock()
        
        mock_exit_monitor = MagicMock()
        mock_exit_monitor.start_monitoring = AsyncMock()
        
        mock_autonomous_mgr = MagicMock()
        mock_autonomous_mgr.get_daily_recovery_count = AsyncMock(return_value=5)
        mock_autonomous_mgr.daily_recovery_limit = 20
        mock_autonomous_mgr.concurrent_recovery_limit = 3
        mock_autonomous_mgr.get_current_session_profit = AsyncMock(return_value=50)
        mock_autonomous_mgr.profit_protection_threshold = 100
        
        return ReentryService(
            mock_reentry_mgr,
            mock_recovery_monitor,
            mock_exit_monitor,
            mock_autonomous_mgr
        )
    
    @pytest.mark.asyncio
    async def test_start_sl_hunt_recovery(self, reentry_service):
        """Test SL Hunt Recovery starts correctly"""
        event = ReentryEvent(
            trade_id='trade_005',
            plugin_id='combined_v3',
            symbol='EURUSD',
            reentry_type=ReentryType.SL_HUNT,
            entry_price=1.0850,
            exit_price=1.0835,
            sl_price=1.0835,
            direction='BUY'
        )
        
        result = await reentry_service.start_sl_hunt_recovery(event)
        
        assert result == True
        reentry_service.recovery_monitor.start_monitoring.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_daily_limit_blocks_recovery(self, reentry_service):
        """Test daily limit prevents recovery"""
        reentry_service.autonomous_manager.get_daily_recovery_count = AsyncMock(return_value=20)
        
        event = ReentryEvent(
            trade_id='trade_006',
            plugin_id='combined_v3',
            symbol='EURUSD',
            reentry_type=ReentryType.SL_HUNT,
            entry_price=1.0850,
            exit_price=1.0835,
            sl_price=1.0835,
            direction='BUY'
        )
        
        result = await reentry_service.start_sl_hunt_recovery(event)
        
        assert result == False
    
    @pytest.mark.asyncio
    async def test_profit_protection_blocks_recovery(self, reentry_service):
        """Test profit protection prevents recovery"""
        reentry_service.autonomous_manager.get_current_session_profit = AsyncMock(return_value=150)
        
        event = ReentryEvent(
            trade_id='trade_007',
            plugin_id='combined_v3',
            symbol='EURUSD',
            reentry_type=ReentryType.SL_HUNT,
            entry_price=1.0850,
            exit_price=1.0835,
            sl_price=1.0835,
            direction='BUY'
        )
        
        result = await reentry_service.start_sl_hunt_recovery(event)
        
        assert result == False
```

**Reason:** Verifies re-entry integration works correctly.

---

## 6. DEPENDENCIES

### Prerequisites:
- Plan 01 (Core Cleanup) - Plugin delegation framework
- Plan 02 (Webhook Routing) - Signals reach plugins

### Blocks:
- Plan 04 (Dual Orders) - Needs re-entry for Order A
- Plan 05 (Profit Booking) - Needs chain tracking
- Plan 06 (Autonomous System) - Needs recovery limits integration

---

## 7. FILES AFFECTED

| File | Action | Description |
|------|--------|-------------|
| `src/core/plugin_system/reentry_interface.py` | CREATE | Re-entry interface |
| `src/core/services/reentry_service.py` | CREATE | Re-entry service |
| `src/logic_plugins/combined_v3/plugin.py` | MODIFY | Add IReentryCapable |
| `src/logic_plugins/combined_v3/order_manager.py` | MODIFY | Add event triggers |
| `src/managers/recovery_window_monitor.py` | MODIFY | Add plugin callbacks |
| `src/managers/exit_continuation_monitor.py` | MODIFY | Add plugin callbacks |
| `tests/test_reentry_integration.py` | CREATE | Integration tests |

---

## 8. TESTING STRATEGY

### Unit Tests:
1. Test `on_sl_hit()` triggers SL Hunt Recovery
2. Test `on_tp_hit()` triggers TP Continuation
3. Test `on_exit()` triggers Exit Continuation
4. Test chain level tracking
5. Test daily/concurrent limits block recovery
6. Test profit protection blocks recovery

### Integration Tests:
1. Full SL hit → Recovery Window → Re-entry flow
2. Full TP hit → Continuation → Reduced SL entry flow
3. Full Exit → 60s monitoring → Continuation flow

### Manual Verification:
1. Execute trade that hits SL
2. Verify Recovery Window Monitor starts
3. Verify 70% recovery triggers re-entry
4. Verify chain level increments

---

## 9. ROLLBACK PLAN

### If Re-Entry Integration Fails:
1. Revert plugin changes
2. Keep ReentryManager working independently
3. Disable plugin re-entry via config

### Feature Flag:
```python
# In plugin config
{
    "use_plugin_reentry": false  # Falls back to legacy
}
```

---

## 10. SUCCESS CRITERIA

This plan is COMPLETE when:

1. ✅ `IReentryCapable` interface created
2. ✅ `ReentryService` created and functional
3. ✅ V3 plugin implements `IReentryCapable`
4. ✅ SL hit triggers SL Hunt Recovery
5. ✅ TP hit triggers TP Continuation
6. ✅ Exit triggers Exit Continuation
7. ✅ Recovery Window Monitor notifies plugins
8. ✅ Exit Continuation Monitor notifies plugins
9. ✅ Chain levels tracked per plugin
10. ✅ All tests pass

---

## 11. REFERENCES

- **Study Report 01:** Section 3 (Re-Entry System - 7 features)
- **Study Report 04:** GAP-1, Discoveries 1-4, 7-8
- **Original Surgery Plan:** `03_SURGERY_PLANS/02_PLUGIN_WIRING_PLAN.md`
- **Code Evidence:** 
  - `src/managers/reentry_manager.py`
  - `src/managers/recovery_window_monitor.py` (626 lines)
  - `src/managers/exit_continuation_monitor.py` (523 lines)

---

**END OF PLAN 03**
