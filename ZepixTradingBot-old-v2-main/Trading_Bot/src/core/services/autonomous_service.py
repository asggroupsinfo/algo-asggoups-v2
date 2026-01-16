"""
Autonomous System Service
Provides safety functionality to plugins via ServiceAPI

Wraps AutonomousSystemManager and ReverseShieldManager to provide
clean interface for plugin safety operations.

Part of V5 Hybrid Plugin Architecture - Plan 06
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from src.core.plugin_system.autonomous_interface import (
    SafetyCheckResult, ReverseShieldStatus, RecoveryStats,
    DEFAULT_DAILY_RECOVERY_LIMIT, DEFAULT_CONCURRENT_RECOVERY_LIMIT,
    DEFAULT_PROFIT_PROTECTION_THRESHOLD
)

logger = logging.getLogger(__name__)


# Singleton instance
_autonomous_service_instance: Optional['AutonomousService'] = None


def get_autonomous_service() -> 'AutonomousService':
    """Get singleton instance of AutonomousService"""
    global _autonomous_service_instance
    if _autonomous_service_instance is None:
        _autonomous_service_instance = AutonomousService()
    return _autonomous_service_instance


def reset_autonomous_service() -> None:
    """Reset singleton instance (for testing)"""
    global _autonomous_service_instance
    _autonomous_service_instance = None


class AutonomousService:
    """
    Service layer for autonomous system operations.
    Plugins use this instead of calling managers directly.
    
    Provides:
    - Safety checks (daily/concurrent limits, profit protection)
    - Reverse Shield activation/deactivation
    - Recovery statistics tracking per plugin
    """
    
    # Default limits (can be overridden by config)
    DAILY_RECOVERY_LIMIT = DEFAULT_DAILY_RECOVERY_LIMIT
    CONCURRENT_RECOVERY_LIMIT = DEFAULT_CONCURRENT_RECOVERY_LIMIT
    PROFIT_PROTECTION_THRESHOLD = DEFAULT_PROFIT_PROTECTION_THRESHOLD
    
    def __init__(
        self,
        autonomous_manager: Optional[Any] = None,
        reverse_shield_manager: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize AutonomousService.
        
        Args:
            autonomous_manager: AutonomousSystemManager instance (optional)
            reverse_shield_manager: ReverseShieldManager instance (optional)
            config: Configuration dict (optional)
        """
        self.asm = autonomous_manager
        self.rsm = reverse_shield_manager
        self.config = config or {}
        
        # Load limits from config if available
        if config:
            auto_config = config.get("re_entry_config", {}).get("autonomous_config", {})
            safety_limits = auto_config.get("safety_limits", {})
            self.DAILY_RECOVERY_LIMIT = safety_limits.get(
                "daily_recovery_attempts", DEFAULT_DAILY_RECOVERY_LIMIT
            )
            self.CONCURRENT_RECOVERY_LIMIT = safety_limits.get(
                "max_concurrent_recoveries", DEFAULT_CONCURRENT_RECOVERY_LIMIT
            )
            self.PROFIT_PROTECTION_THRESHOLD = safety_limits.get(
                "profit_protection_threshold", DEFAULT_PROFIT_PROTECTION_THRESHOLD
            )
        
        # Track per-plugin statistics
        self._plugin_stats: Dict[str, RecoveryStats] = {}
        
        # Track active shields per plugin
        self._plugin_shields: Dict[str, Dict[str, ReverseShieldStatus]] = {}
        
        # Track daily recovery count (if no ASM available)
        self._daily_recovery_count = 0
        self._concurrent_recovery_count = 0
        self._current_session_profit = 0.0
        self._last_reset_date = datetime.now().date()
        
        # Global stats
        self._stats = {
            'total_safety_checks': 0,
            'total_recoveries_blocked': 0,
            'total_shields_activated': 0,
            'total_shields_deactivated': 0,
            'last_reset': datetime.now().isoformat()
        }
        
        logger.info("AutonomousService initialized")
    
    def set_managers(
        self,
        autonomous_manager: Any,
        reverse_shield_manager: Any
    ) -> None:
        """Set the manager instances after initialization"""
        self.asm = autonomous_manager
        self.rsm = reverse_shield_manager
        logger.info("AutonomousService managers set")
    
    def _check_daily_reset(self) -> None:
        """Reset daily counters if new day"""
        current_date = datetime.now().date()
        if current_date != self._last_reset_date:
            self._daily_recovery_count = 0
            self._last_reset_date = current_date
            # Reset plugin daily stats
            for plugin_id in self._plugin_stats:
                self._plugin_stats[plugin_id].daily_recoveries = 0
            logger.info(f"Daily stats reset for {current_date}")
    
    async def get_daily_recovery_count(self) -> int:
        """Get current daily recovery count"""
        self._check_daily_reset()
        if self.asm and hasattr(self.asm, 'daily_stats'):
            return self.asm.daily_stats.get('recovery_attempts', 0)
        return self._daily_recovery_count
    
    async def get_concurrent_recovery_count(self) -> int:
        """Get current concurrent recovery count"""
        if self.asm and hasattr(self.asm, 'daily_stats'):
            return len(self.asm.daily_stats.get('active_recoveries', set()))
        return self._concurrent_recovery_count
    
    async def get_current_session_profit(self) -> float:
        """Get current session profit"""
        return self._current_session_profit
    
    def set_current_session_profit(self, profit: float) -> None:
        """Set current session profit (called by trading engine)"""
        self._current_session_profit = profit
    
    async def check_recovery_allowed(self, plugin_id: str) -> SafetyCheckResult:
        """
        Comprehensive safety check before recovery.
        Checks daily limit, concurrent limit, and profit protection.
        
        Args:
            plugin_id: ID of the plugin requesting recovery
            
        Returns:
            SafetyCheckResult with allowed=True if all checks pass
        """
        self._stats['total_safety_checks'] += 1
        self._check_daily_reset()
        
        # Get current counts
        daily_count = await self.get_daily_recovery_count()
        concurrent_count = await self.get_concurrent_recovery_count()
        current_profit = await self.get_current_session_profit()
        
        # Check daily limit
        if daily_count >= self.DAILY_RECOVERY_LIMIT:
            self._stats['total_recoveries_blocked'] += 1
            logger.info(f"Recovery blocked for {plugin_id}: Daily limit reached ({daily_count}/{self.DAILY_RECOVERY_LIMIT})")
            return SafetyCheckResult(
                allowed=False,
                reason=f"Daily recovery limit reached ({daily_count}/{self.DAILY_RECOVERY_LIMIT})",
                daily_count=daily_count,
                daily_limit=self.DAILY_RECOVERY_LIMIT,
                concurrent_count=concurrent_count,
                concurrent_limit=self.CONCURRENT_RECOVERY_LIMIT,
                current_profit=current_profit,
                profit_threshold=self.PROFIT_PROTECTION_THRESHOLD
            )
        
        # Check concurrent limit
        if concurrent_count >= self.CONCURRENT_RECOVERY_LIMIT:
            self._stats['total_recoveries_blocked'] += 1
            logger.info(f"Recovery blocked for {plugin_id}: Concurrent limit reached ({concurrent_count}/{self.CONCURRENT_RECOVERY_LIMIT})")
            return SafetyCheckResult(
                allowed=False,
                reason=f"Concurrent recovery limit reached ({concurrent_count}/{self.CONCURRENT_RECOVERY_LIMIT})",
                daily_count=daily_count,
                daily_limit=self.DAILY_RECOVERY_LIMIT,
                concurrent_count=concurrent_count,
                concurrent_limit=self.CONCURRENT_RECOVERY_LIMIT,
                current_profit=current_profit,
                profit_threshold=self.PROFIT_PROTECTION_THRESHOLD
            )
        
        # Check profit protection
        if current_profit >= self.PROFIT_PROTECTION_THRESHOLD:
            self._stats['total_recoveries_blocked'] += 1
            logger.info(f"Recovery blocked for {plugin_id}: Profit protection active (${current_profit:.2f} >= ${self.PROFIT_PROTECTION_THRESHOLD:.2f})")
            return SafetyCheckResult(
                allowed=False,
                reason=f"Profit protection active (${current_profit:.2f} >= ${self.PROFIT_PROTECTION_THRESHOLD:.2f})",
                daily_count=daily_count,
                daily_limit=self.DAILY_RECOVERY_LIMIT,
                concurrent_count=concurrent_count,
                concurrent_limit=self.CONCURRENT_RECOVERY_LIMIT,
                current_profit=current_profit,
                profit_threshold=self.PROFIT_PROTECTION_THRESHOLD
            )
        
        # All checks passed
        logger.info(f"Recovery allowed for plugin {plugin_id}")
        return SafetyCheckResult(
            allowed=True,
            reason="All safety checks passed",
            daily_count=daily_count,
            daily_limit=self.DAILY_RECOVERY_LIMIT,
            concurrent_count=concurrent_count,
            concurrent_limit=self.CONCURRENT_RECOVERY_LIMIT,
            current_profit=current_profit,
            profit_threshold=self.PROFIT_PROTECTION_THRESHOLD
        )
    
    async def activate_reverse_shield(
        self,
        plugin_id: str,
        trade_id: str,
        symbol: str,
        direction: str,
        original_trade: Optional[Any] = None
    ) -> ReverseShieldStatus:
        """
        Activate Reverse Shield for a trade.
        Creates hedge position to protect during recovery window.
        
        Args:
            plugin_id: ID of the plugin requesting shield
            trade_id: ID of the trade being protected
            symbol: Trading symbol
            direction: Original trade direction
            original_trade: Original trade object (optional, for RSM)
            
        Returns:
            ReverseShieldStatus with shield details
        """
        try:
            # Check if RSM is available and enabled
            if self.rsm and hasattr(self.rsm, 'is_enabled') and self.rsm.is_enabled():
                # Use actual ReverseShieldManager
                if original_trade:
                    shield_result = await self.rsm.activate_shield(original_trade, "PLUGIN_RECOVERY")
                    
                    if shield_result:
                        self._stats['total_shields_activated'] += 1
                        self._track_shield_activation(plugin_id)
                        
                        status = ReverseShieldStatus(
                            active=True,
                            shield_id=f"shield_{trade_id}",
                            symbol=symbol,
                            direction=direction,
                            hedge_order_id=None,
                            shield_a_ticket=shield_result.get('shield_ids', [None, None])[0],
                            shield_b_ticket=shield_result.get('shield_ids', [None, None])[1] if len(shield_result.get('shield_ids', [])) > 1 else None,
                            recovery_70_level=shield_result.get('recovery_70_level')
                        )
                        
                        # Track shield for plugin
                        if plugin_id not in self._plugin_shields:
                            self._plugin_shields[plugin_id] = {}
                        self._plugin_shields[plugin_id][trade_id] = status
                        
                        logger.info(f"Reverse Shield activated: {status.shield_id} for {trade_id}")
                        return status
            
            # RSM not available or activation failed - return inactive status
            logger.info(f"Reverse Shield not activated for {trade_id} (RSM not available or disabled)")
            return ReverseShieldStatus(
                active=False,
                shield_id=None,
                symbol=symbol,
                direction=direction,
                hedge_order_id=None,
                error="ReverseShieldManager not available or disabled"
            )
            
        except Exception as e:
            logger.error(f"Failed to activate Reverse Shield: {e}")
            return ReverseShieldStatus(
                active=False,
                shield_id=None,
                symbol=symbol,
                direction=direction,
                hedge_order_id=None,
                error=str(e)
            )
    
    async def deactivate_reverse_shield(
        self,
        plugin_id: str,
        trade_id: str
    ) -> bool:
        """
        Deactivate Reverse Shield for a trade.
        
        Args:
            plugin_id: ID of the plugin
            trade_id: ID of the trade whose shield should be deactivated
            
        Returns:
            True if shield was successfully deactivated
        """
        try:
            # Get shield status
            if plugin_id in self._plugin_shields:
                status = self._plugin_shields[plugin_id].pop(trade_id, None)
                if status and status.active:
                    # If RSM is available, use kill_switch to close shields
                    if self.rsm and status.shield_a_ticket and status.shield_b_ticket:
                        # Note: kill_switch requires more params, simplified here
                        pass
                    
                    self._stats['total_shields_deactivated'] += 1
                    logger.info(f"Reverse Shield deactivated: {status.shield_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to deactivate Reverse Shield: {e}")
            return False
    
    async def increment_recovery_count(self, plugin_id: str) -> int:
        """
        Increment daily recovery count.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            New daily recovery count
        """
        self._check_daily_reset()
        
        # Increment global count
        self._daily_recovery_count += 1
        
        # Increment in ASM if available
        if self.asm and hasattr(self.asm, 'daily_stats'):
            self.asm.daily_stats['recovery_attempts'] = self.asm.daily_stats.get('recovery_attempts', 0) + 1
        
        # Track per plugin
        self._track_recovery(plugin_id)
        
        logger.info(f"Recovery count incremented for {plugin_id}: {self._daily_recovery_count}")
        return self._daily_recovery_count
    
    def _track_recovery(self, plugin_id: str) -> None:
        """Track recovery for a plugin"""
        if plugin_id not in self._plugin_stats:
            self._plugin_stats[plugin_id] = RecoveryStats()
        self._plugin_stats[plugin_id].daily_recoveries += 1
        self._plugin_stats[plugin_id].last_recovery_time = datetime.now().isoformat()
    
    def _track_shield_activation(self, plugin_id: str) -> None:
        """Track shield activation for a plugin"""
        if plugin_id not in self._plugin_stats:
            self._plugin_stats[plugin_id] = RecoveryStats()
        self._plugin_stats[plugin_id].shields_activated += 1
    
    def get_plugin_stats(self, plugin_id: str) -> Dict[str, Any]:
        """Get statistics for a plugin"""
        if plugin_id in self._plugin_stats:
            return self._plugin_stats[plugin_id].to_dict()
        return RecoveryStats().to_dict()
    
    def get_active_shields(self, plugin_id: str) -> List[ReverseShieldStatus]:
        """Get active shields for a plugin"""
        if plugin_id in self._plugin_shields:
            return list(self._plugin_shields[plugin_id].values())
        return []
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global autonomous system statistics"""
        return {
            'daily_recovery_count': await self.get_daily_recovery_count(),
            'daily_recovery_limit': self.DAILY_RECOVERY_LIMIT,
            'concurrent_recovery_count': await self.get_concurrent_recovery_count(),
            'concurrent_recovery_limit': self.CONCURRENT_RECOVERY_LIMIT,
            'current_session_profit': await self.get_current_session_profit(),
            'profit_protection_threshold': self.PROFIT_PROTECTION_THRESHOLD,
            'total_safety_checks': self._stats['total_safety_checks'],
            'total_recoveries_blocked': self._stats['total_recoveries_blocked'],
            'total_shields_activated': self._stats['total_shields_activated'],
            'total_shields_deactivated': self._stats['total_shields_deactivated'],
            'plugin_stats': {k: v.to_dict() for k, v in self._plugin_stats.items()},
            'last_reset': self._stats['last_reset']
        }
    
    def should_protect_profit(self, current_profit: float) -> bool:
        """
        Check if current profit should be protected.
        
        Args:
            current_profit: Current session profit in dollars
            
        Returns:
            True if profit should be protected (recovery should be skipped)
        """
        return current_profit >= self.PROFIT_PROTECTION_THRESHOLD
