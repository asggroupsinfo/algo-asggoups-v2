"""
Plugin Interface for Signal Processing
Defines the contract between TradingEngine and Plugins

This module provides interfaces that plugins must implement to be
discoverable and usable by the TradingEngine delegation system.

Version: 1.0.0
Date: 2026-01-15
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class ISignalProcessor(ABC):
    """
    Interface for plugins that process trading signals.
    
    Plugins implementing this interface can be automatically discovered
    and used by TradingEngine for signal delegation.
    """
    
    @abstractmethod
    async def can_process_signal(self, signal_data: Dict[str, Any]) -> bool:
        """
        Check if this plugin can process the given signal.
        
        Args:
            signal_data: Signal data dictionary containing strategy, symbol, etc.
            
        Returns:
            bool: True if this plugin can handle the signal
        """
        pass
    
    @abstractmethod
    async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process the signal and return result.
        
        This is the main entry point for signal processing. The plugin
        should handle the signal according to its strategy and return
        the execution result.
        
        Args:
            signal_data: Signal data dictionary
            
        Returns:
            dict: Execution result with status, order details, etc.
                  Returns None if processing failed.
        """
        pass
    
    @abstractmethod
    def get_supported_strategies(self) -> List[str]:
        """
        Return list of strategy names this plugin supports.
        
        Used by PluginRegistry to match signals to plugins.
        
        Returns:
            list: Strategy names (e.g., ['V3_COMBINED', 'COMBINED_V3'])
        """
        pass
    
    @abstractmethod
    def get_supported_timeframes(self) -> List[str]:
        """
        Return list of timeframes this plugin supports.
        
        Used for more granular plugin matching (e.g., V6 plugins
        are timeframe-specific).
        
        Returns:
            list: Timeframe strings (e.g., ['5m', '15m', '1h'])
        """
        pass


class IOrderExecutor(ABC):
    """
    Interface for plugins that execute orders.
    
    Plugins implementing this interface can execute, modify, and
    close orders through the MT5 client.
    """
    
    @abstractmethod
    async def execute_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute an order and return result.
        
        Args:
            order_data: Order parameters (symbol, direction, lot_size, sl, tp, etc.)
            
        Returns:
            dict: Order execution result with order_id, status, etc.
        """
        pass
    
    @abstractmethod
    async def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> bool:
        """
        Modify an existing order.
        
        Args:
            order_id: MT5 order/position ID
            modifications: Fields to modify (sl, tp, etc.)
            
        Returns:
            bool: True if modification successful
        """
        pass
    
    @abstractmethod
    async def close_order(self, order_id: str, reason: str) -> bool:
        """
        Close an existing order.
        
        Args:
            order_id: MT5 order/position ID
            reason: Reason for closing (e.g., 'SL_HIT', 'TP_HIT', 'MANUAL')
            
        Returns:
            bool: True if close successful
        """
        pass


class IPluginLifecycle(ABC):
    """
    Interface for plugin lifecycle management.
    
    Optional interface for plugins that need initialization
    and cleanup hooks.
    """
    
    @abstractmethod
    async def on_initialize(self) -> bool:
        """
        Called when plugin is first loaded.
        
        Returns:
            bool: True if initialization successful
        """
        pass
    
    @abstractmethod
    async def on_shutdown(self) -> None:
        """
        Called when plugin is being unloaded.
        
        Use for cleanup (close connections, save state, etc.)
        """
        pass
    
    @abstractmethod
    async def on_enable(self) -> None:
        """Called when plugin is enabled"""
        pass
    
    @abstractmethod
    async def on_disable(self) -> None:
        """Called when plugin is disabled"""
        pass
