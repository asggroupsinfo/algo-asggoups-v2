"""
Re-Entry Interface for Plugins
Defines how plugins interact with the Re-Entry System

Part of Plan 03: Re-Entry System Integration
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class ReentryType(Enum):
    """Types of re-entry"""
    SL_HUNT = "sl_hunt"           # SL hit, monitoring for recovery
    TP_CONTINUATION = "tp_cont"   # TP hit, continuing with reduced SL
    EXIT_CONTINUATION = "exit_cont"  # Manual exit, monitoring for continuation


@dataclass
class ReentryEvent:
    """Event data for re-entry triggers"""
    trade_id: str
    plugin_id: str
    symbol: str
    reentry_type: ReentryType
    entry_price: float
    exit_price: float
    sl_price: float
    direction: str  # 'BUY' or 'SELL'
    chain_level: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'trade_id': self.trade_id,
            'plugin_id': self.plugin_id,
            'symbol': self.symbol,
            'reentry_type': self.reentry_type.value,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'sl_price': self.sl_price,
            'direction': self.direction,
            'chain_level': self.chain_level,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReentryEvent':
        """Create from dictionary"""
        return cls(
            trade_id=data['trade_id'],
            plugin_id=data['plugin_id'],
            symbol=data['symbol'],
            reentry_type=ReentryType(data['reentry_type']),
            entry_price=data['entry_price'],
            exit_price=data['exit_price'],
            sl_price=data['sl_price'],
            direction=data['direction'],
            chain_level=data.get('chain_level', 0),
            metadata=data.get('metadata', {}),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.now()
        )


class IReentryCapable(ABC):
    """Interface for plugins that support re-entry"""
    
    @abstractmethod
    async def on_sl_hit(self, event: ReentryEvent) -> bool:
        """
        Called when SL is hit. Plugin should:
        1. Check if SL Hunt Recovery is enabled
        2. Start Recovery Window Monitor
        3. Return True if recovery monitoring started
        
        Args:
            event: ReentryEvent with trade details
            
        Returns:
            True if recovery monitoring started, False otherwise
        """
        pass
    
    @abstractmethod
    async def on_tp_hit(self, event: ReentryEvent) -> bool:
        """
        Called when TP is hit. Plugin should:
        1. Check if TP Continuation is enabled
        2. Calculate reduced SL for next entry
        3. Return True if continuation started
        
        Args:
            event: ReentryEvent with trade details
            
        Returns:
            True if continuation started, False otherwise
        """
        pass
    
    @abstractmethod
    async def on_exit(self, event: ReentryEvent) -> bool:
        """
        Called on manual/reversal exit. Plugin should:
        1. Check if Exit Continuation is enabled
        2. Start Exit Continuation Monitor
        3. Return True if monitoring started
        
        Args:
            event: ReentryEvent with trade details
            
        Returns:
            True if monitoring started, False otherwise
        """
        pass
    
    @abstractmethod
    async def on_recovery_signal(self, event: ReentryEvent) -> bool:
        """
        Called when recovery conditions are met. Plugin should:
        1. Execute re-entry order
        2. Increment chain level
        3. Return True if re-entry executed
        
        Args:
            event: ReentryEvent with recovery details
            
        Returns:
            True if re-entry executed, False otherwise
        """
        pass
    
    @abstractmethod
    def get_chain_level(self, trade_id: str) -> int:
        """
        Get current chain level for a trade.
        
        Args:
            trade_id: Trade identifier
            
        Returns:
            Current chain level (0 if not in chain)
        """
        pass
    
    @abstractmethod
    def get_max_chain_level(self) -> int:
        """
        Get maximum allowed chain level for this plugin.
        
        Returns:
            Maximum chain level
        """
        pass
    
    def is_reentry_enabled(self) -> bool:
        """
        Check if re-entry is enabled for this plugin.
        Default implementation returns True.
        
        Returns:
            True if re-entry is enabled
        """
        return True
    
    def get_reentry_config(self) -> Dict[str, Any]:
        """
        Get re-entry configuration for this plugin.
        Default implementation returns empty dict.
        
        Returns:
            Re-entry configuration dictionary
        """
        return {}
