"""
Autonomous System Interface for Plugins
Defines how plugins interact with safety systems (Daily Limits, Concurrent Limits, Profit Protection, Reverse Shield)

Part of V5 Hybrid Plugin Architecture - Plan 06
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SafetyCheckResult:
    """Result of a comprehensive safety check before recovery"""
    allowed: bool
    reason: str
    daily_count: int
    daily_limit: int
    concurrent_count: int
    concurrent_limit: int
    current_profit: float
    profit_threshold: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'allowed': self.allowed,
            'reason': self.reason,
            'daily_count': self.daily_count,
            'daily_limit': self.daily_limit,
            'concurrent_count': self.concurrent_count,
            'concurrent_limit': self.concurrent_limit,
            'current_profit': self.current_profit,
            'profit_threshold': self.profit_threshold,
            'timestamp': self.timestamp
        }


@dataclass
class ReverseShieldStatus:
    """Status of Reverse Shield activation"""
    active: bool
    shield_id: Optional[str]
    symbol: str
    direction: str
    hedge_order_id: Optional[str]
    shield_a_ticket: Optional[int] = None
    shield_b_ticket: Optional[int] = None
    recovery_70_level: Optional[float] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'active': self.active,
            'shield_id': self.shield_id,
            'symbol': self.symbol,
            'direction': self.direction,
            'hedge_order_id': self.hedge_order_id,
            'shield_a_ticket': self.shield_a_ticket,
            'shield_b_ticket': self.shield_b_ticket,
            'recovery_70_level': self.recovery_70_level,
            'error': self.error
        }


@dataclass
class RecoveryStats:
    """Statistics for recovery operations"""
    daily_recoveries: int = 0
    concurrent_recoveries: int = 0
    shields_activated: int = 0
    shields_successful: int = 0
    profit_protected_skips: int = 0
    last_recovery_time: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'daily_recoveries': self.daily_recoveries,
            'concurrent_recoveries': self.concurrent_recoveries,
            'shields_activated': self.shields_activated,
            'shields_successful': self.shields_successful,
            'profit_protected_skips': self.profit_protected_skips,
            'last_recovery_time': self.last_recovery_time
        }


# Default safety limits from config
DEFAULT_DAILY_RECOVERY_LIMIT = 10
DEFAULT_CONCURRENT_RECOVERY_LIMIT = 3
DEFAULT_PROFIT_PROTECTION_THRESHOLD = 100.0  # $100


class IAutonomousCapable(ABC):
    """
    Interface for plugins that use autonomous safety systems.
    
    Plugins implementing this interface can:
    1. Check if recovery is allowed (daily/concurrent limits, profit protection)
    2. Activate/deactivate Reverse Shield for trade protection
    3. Track recovery statistics
    """
    
    @abstractmethod
    async def check_recovery_allowed(self) -> SafetyCheckResult:
        """
        Check if recovery is allowed based on all safety limits.
        Must be called before starting any recovery operation.
        
        Checks:
        - Daily recovery limit (default: 10/day)
        - Concurrent recovery limit (default: 3 simultaneous)
        - Profit protection threshold (default: $100)
        
        Returns:
            SafetyCheckResult with allowed=True if all checks pass
        """
        pass
    
    @abstractmethod
    async def activate_reverse_shield(
        self,
        trade_id: str,
        symbol: str,
        direction: str
    ) -> ReverseShieldStatus:
        """
        Activate Reverse Shield for a trade during recovery.
        Creates hedge position to protect during recovery window.
        
        Args:
            trade_id: ID of the trade being protected
            symbol: Trading symbol (e.g., 'EURUSD')
            direction: Original trade direction ('BUY' or 'SELL')
            
        Returns:
            ReverseShieldStatus with shield details if activated
        """
        pass
    
    @abstractmethod
    async def deactivate_reverse_shield(self, trade_id: str) -> bool:
        """
        Deactivate Reverse Shield after recovery completes or fails.
        
        Args:
            trade_id: ID of the trade whose shield should be deactivated
            
        Returns:
            True if shield was successfully deactivated
        """
        pass
    
    @abstractmethod
    async def increment_recovery_count(self) -> int:
        """
        Increment daily recovery count and return new count.
        Called when a recovery operation starts.
        
        Returns:
            New daily recovery count
        """
        pass
    
    @abstractmethod
    async def get_safety_stats(self) -> Dict[str, Any]:
        """
        Get current safety statistics for this plugin.
        
        Returns:
            Dict with recovery stats, shield stats, etc.
        """
        pass
    
    @abstractmethod
    def should_protect_profit(self, current_profit: float) -> bool:
        """
        Check if current profit should be protected (skip recovery).
        
        Args:
            current_profit: Current session profit in dollars
            
        Returns:
            True if profit should be protected (recovery should be skipped)
        """
        pass
