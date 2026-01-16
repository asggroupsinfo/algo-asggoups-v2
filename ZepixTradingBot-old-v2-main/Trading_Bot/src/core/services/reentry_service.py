"""
Re-Entry Service
Provides re-entry functionality to plugins via ServiceAPI

Part of Plan 03: Re-Entry System Integration
"""
from typing import Dict, Any, Optional, Callable
import logging
import asyncio
from datetime import datetime

from src.core.plugin_system.reentry_interface import ReentryEvent, ReentryType

logger = logging.getLogger(__name__)


class ReentryService:
    """
    Service layer for re-entry operations.
    Plugins use this instead of calling managers directly.
    """
    
    def __init__(
        self,
        reentry_manager=None,
        recovery_monitor=None,
        exit_monitor=None,
        autonomous_manager=None
    ):
        """
        Initialize the re-entry service.
        
        Args:
            reentry_manager: ReEntryManager instance
            recovery_monitor: RecoveryWindowMonitor instance
            exit_monitor: ExitContinuationMonitor instance
            autonomous_manager: AutonomousSystemManager instance
        """
        self.reentry_manager = reentry_manager
        self.recovery_monitor = recovery_monitor
        self.exit_monitor = exit_monitor
        self.autonomous_manager = autonomous_manager
        
        # Track active recoveries per plugin
        self._active_recoveries: Dict[str, Dict[str, ReentryEvent]] = {}
        
        # Recovery callbacks
        self._recovery_callbacks: Dict[str, Callable] = {}
        
        # Statistics
        self._stats = {
            'total_sl_hunts_started': 0,
            'total_tp_continuations_started': 0,
            'total_exit_continuations_started': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'blocked_by_limits': 0
        }
        
        self._last_reset = datetime.now()
    
    def set_managers(
        self,
        reentry_manager=None,
        recovery_monitor=None,
        exit_monitor=None,
        autonomous_manager=None
    ):
        """Set manager dependencies after initialization"""
        if reentry_manager:
            self.reentry_manager = reentry_manager
        if recovery_monitor:
            self.recovery_monitor = recovery_monitor
        if exit_monitor:
            self.exit_monitor = exit_monitor
        if autonomous_manager:
            self.autonomous_manager = autonomous_manager
    
    async def start_sl_hunt_recovery(self, event: ReentryEvent) -> bool:
        """
        Start SL Hunt Recovery monitoring.
        Called by plugin when SL is hit.
        
        Args:
            event: ReentryEvent with trade details
            
        Returns:
            True if recovery monitoring started
        """
        # Check if recovery is allowed
        if not await self._can_start_recovery(event):
            logger.info(f"Recovery not allowed for {event.trade_id}")
            self._stats['blocked_by_limits'] += 1
            return False
        
        # Get symbol-specific recovery window
        recovery_window = await self._get_recovery_window(event.symbol)
        
        # Start monitoring if recovery monitor is available
        if self.recovery_monitor:
            try:
                await self.recovery_monitor.start_monitoring(
                    trade_id=event.trade_id,
                    symbol=event.symbol,
                    sl_price=event.sl_price,
                    entry_price=event.entry_price,
                    direction=event.direction,
                    recovery_window_minutes=recovery_window,
                    callback=lambda: self._on_recovery_detected(event),
                    plugin_id=event.plugin_id
                )
            except TypeError:
                # Fallback for older monitor versions without all parameters
                await self.recovery_monitor.start_monitoring(
                    trade_id=event.trade_id,
                    symbol=event.symbol,
                    sl_price=event.sl_price
                )
        
        # Track active recovery
        self._track_recovery(event)
        self._stats['total_sl_hunts_started'] += 1
        
        logger.info(f"SL Hunt Recovery started for {event.trade_id}, window: {recovery_window}min")
        return True
    
    async def start_tp_continuation(self, event: ReentryEvent) -> bool:
        """
        Start TP Continuation.
        Called by plugin when TP is hit.
        
        Args:
            event: ReentryEvent with trade details
            
        Returns:
            True if continuation started
        """
        # Check chain level
        max_level = self.get_max_chain_level(event.plugin_id)
        if event.chain_level >= max_level:
            logger.info(f"Max chain level reached for {event.trade_id}")
            return False
        
        # Calculate reduced SL for next entry
        reduced_sl = await self._calculate_reduced_sl(event)
        
        # Start continuation via reentry manager
        if self.reentry_manager:
            try:
                await self.reentry_manager.start_tp_continuation(
                    trade_id=event.trade_id,
                    symbol=event.symbol,
                    new_sl_pips=reduced_sl,
                    chain_level=event.chain_level + 1
                )
            except (TypeError, AttributeError):
                # Manager may not have this method, log and continue
                logger.debug(f"ReentryManager.start_tp_continuation not available")
        
        self._stats['total_tp_continuations_started'] += 1
        logger.info(f"TP Continuation started for {event.trade_id}, reduced SL: {reduced_sl} pips")
        return True
    
    async def start_exit_continuation(self, event: ReentryEvent) -> bool:
        """
        Start Exit Continuation monitoring.
        Called by plugin on manual/reversal exit.
        
        Args:
            event: ReentryEvent with trade details
            
        Returns:
            True if monitoring started
        """
        # Check if exit continuation is enabled
        if self.reentry_manager and hasattr(self.reentry_manager, 'exit_continuation_enabled'):
            if not self.reentry_manager.exit_continuation_enabled:
                return False
        
        # Start 60-second monitoring
        if self.exit_monitor:
            try:
                await self.exit_monitor.start_monitoring(
                    trade_id=event.trade_id,
                    exit_price=event.exit_price,
                    symbol=event.symbol,
                    direction=event.direction,
                    callback=lambda: self._on_continuation_detected(event),
                    plugin_id=event.plugin_id
                )
            except TypeError:
                # Fallback for older monitor versions
                await self.exit_monitor.start_monitoring(
                    trade_id=event.trade_id,
                    exit_price=event.exit_price
                )
        
        self._stats['total_exit_continuations_started'] += 1
        logger.info(f"Exit Continuation started for {event.trade_id}")
        return True
    
    async def _can_start_recovery(self, event: ReentryEvent) -> bool:
        """Check if recovery is allowed based on limits"""
        if not self.autonomous_manager:
            return True  # No limits if no manager
        
        # Check daily recovery limit
        try:
            daily_count = await self.autonomous_manager.get_daily_recovery_count()
            daily_limit = getattr(self.autonomous_manager, 'daily_recovery_limit', 20)
            if daily_count >= daily_limit:
                logger.warning(f"Daily recovery limit reached: {daily_count}/{daily_limit}")
                return False
        except (AttributeError, TypeError):
            pass  # Method not available
        
        # Check concurrent recovery limit
        concurrent_count = self._get_concurrent_recovery_count(event.plugin_id)
        concurrent_limit = getattr(self.autonomous_manager, 'concurrent_recovery_limit', 3)
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
        if not self.autonomous_manager:
            return False
        
        try:
            current_profit = await self.autonomous_manager.get_current_session_profit()
            protection_threshold = getattr(self.autonomous_manager, 'profit_protection_threshold', 100)
            return current_profit >= protection_threshold
        except (AttributeError, TypeError):
            return False
    
    async def _get_recovery_window(self, symbol: str) -> int:
        """Get symbol-specific recovery window in minutes"""
        # Default windows by symbol (Discovery 7)
        default_windows = {
            'EURUSD': 30,
            'GBPUSD': 20,
            'USDJPY': 25,
            'XAUUSD': 15,
            'AUDUSD': 30,
            'USDCAD': 30
        }
        
        if self.reentry_manager:
            try:
                return await self.reentry_manager.get_recovery_window(symbol)
            except (AttributeError, TypeError):
                pass
        
        return default_windows.get(symbol, 30)
    
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
        self._stats['successful_recoveries'] += 1
        
        # Notify plugin via callback if registered
        callback = self._recovery_callbacks.get(event.plugin_id)
        if callback:
            try:
                await callback(event)
            except Exception as e:
                logger.error(f"Recovery callback error: {e}")
        
        # Untrack recovery
        self._untrack_recovery(event.plugin_id, event.trade_id)
    
    async def _on_continuation_detected(self, event: ReentryEvent):
        """Callback when continuation conditions are met"""
        logger.info(f"Continuation detected for {event.trade_id}")
        
        # Notify plugin via callback if registered
        callback = self._recovery_callbacks.get(event.plugin_id)
        if callback:
            try:
                await callback(event)
            except Exception as e:
                logger.error(f"Continuation callback error: {e}")
    
    def register_recovery_callback(self, plugin_id: str, callback: Callable):
        """Register a callback for recovery events"""
        self._recovery_callbacks[plugin_id] = callback
    
    def unregister_recovery_callback(self, plugin_id: str):
        """Unregister a recovery callback"""
        self._recovery_callbacks.pop(plugin_id, None)
    
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
    
    def get_all_active_recoveries(self) -> Dict[str, Dict[str, ReentryEvent]]:
        """Get all active recoveries across all plugins"""
        return {pid: recoveries.copy() for pid, recoveries in self._active_recoveries.items()}
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        total_active = sum(len(r) for r in self._active_recoveries.values())
        return {
            'total_active_recoveries': total_active,
            'recoveries_by_plugin': {
                pid: len(recoveries) 
                for pid, recoveries in self._active_recoveries.items()
            },
            'total_sl_hunts_started': self._stats['total_sl_hunts_started'],
            'total_tp_continuations_started': self._stats['total_tp_continuations_started'],
            'total_exit_continuations_started': self._stats['total_exit_continuations_started'],
            'successful_recoveries': self._stats['successful_recoveries'],
            'failed_recoveries': self._stats['failed_recoveries'],
            'blocked_by_limits': self._stats['blocked_by_limits'],
            'last_reset': self._last_reset.isoformat()
        }
    
    def reset_stats(self):
        """Reset recovery statistics"""
        self._stats = {
            'total_sl_hunts_started': 0,
            'total_tp_continuations_started': 0,
            'total_exit_continuations_started': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'blocked_by_limits': 0
        }
        self._last_reset = datetime.now()
        logger.info("Recovery stats reset")
    
    def stop_all_recoveries(self, plugin_id: Optional[str] = None):
        """Stop all active recoveries, optionally for a specific plugin"""
        if plugin_id:
            self._active_recoveries.pop(plugin_id, None)
            logger.info(f"Stopped all recoveries for plugin {plugin_id}")
        else:
            self._active_recoveries.clear()
            logger.info("Stopped all recoveries")


# Singleton instance
_reentry_service: Optional[ReentryService] = None


def get_reentry_service() -> ReentryService:
    """Get or create the singleton ReentryService instance"""
    global _reentry_service
    if _reentry_service is None:
        _reentry_service = ReentryService()
    return _reentry_service


def reset_reentry_service():
    """Reset the singleton instance (for testing)"""
    global _reentry_service
    _reentry_service = None
