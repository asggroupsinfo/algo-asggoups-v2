from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


# ==================== Interface Definitions ====================
# These interfaces define the contracts for plugin capabilities

class ISignalProcessor(ABC):
    """Interface for plugins that process trading signals."""
    
    @abstractmethod
    async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a trading signal and return result."""
        pass
    
    @abstractmethod
    def get_supported_strategies(self) -> List[str]:
        """Return list of strategy names this plugin supports."""
        pass


class IOrderExecutor(ABC):
    """Interface for plugins that execute orders."""
    
    @abstractmethod
    async def execute_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an order and return result."""
        pass


class IReentryCapable(ABC):
    """Interface for plugins that support re-entry on SL/TP hit."""
    
    @abstractmethod
    async def on_sl_hit(self, event: Any) -> bool:
        """Handle stop loss hit event."""
        pass
    
    @abstractmethod
    async def on_tp_hit(self, event: Any) -> bool:
        """Handle take profit hit event."""
        pass


class IDualOrderCapable(ABC):
    """Interface for plugins that support dual order system."""
    
    @abstractmethod
    async def create_dual_orders(self, signal: Dict[str, Any]) -> Any:
        """Create both Order A and Order B for a signal."""
        pass


class IProfitBookingCapable(ABC):
    """Interface for plugins that support profit booking chains."""
    
    @abstractmethod
    async def create_profit_chain(self, order_b_id: str, signal: Dict[str, Any]) -> Any:
        """Create a profit booking chain for Order B."""
        pass


class IAutonomousCapable(ABC):
    """Interface for plugins that support autonomous safety features."""
    
    @abstractmethod
    async def check_recovery_allowed(self, trade_id: str) -> bool:
        """Check if recovery is allowed for a trade."""
        pass


class IDatabaseCapable(ABC):
    """Interface for plugins that support database operations."""
    
    @abstractmethod
    async def save_trade(self, trade_data: Dict[str, Any]) -> bool:
        """Save trade data to database."""
        pass


class BaseLogicPlugin(ABC):
    """
    Base class for all trading logic plugins.
    
    Plugins must implement:
    - process_entry_signal()
    - process_exit_signal()
    - process_reversal_signal()
    """
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        """
        Initialize plugin instance.
        
        Args:
            plugin_id: Unique identifier for this plugin
            config: Plugin-specific configuration
            service_api: Access to shared services
        """
        self.plugin_id = plugin_id
        self.config = config
        self.service_api = service_api
        self.logger = logging.getLogger(f"plugin.{plugin_id}")
        
        # Plugin metadata
        self.metadata = self._load_metadata()
        
        # Plugin state
        self.enabled = config.get("enabled", True)
        
        # Database connection (plugin-specific)
        self.db_path = f"data/zepix_{plugin_id}.db"
        
        self.logger.info(f"Initialized plugin: {plugin_id}")
    
    @abstractmethod
    async def process_entry_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process entry signal and execute trade.
        
        Args:
            alert: Alert data (ZepixV3Alert or similar)
            
        Returns:
            dict: Execution result with trade details
        """
        pass
    
    @abstractmethod
    async def process_exit_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process exit signal and close trades.
        
        Args:
            alert: Exit alert data
            
        Returns:
            dict: Exit execution result
        """
        pass
    
    @abstractmethod
    async def process_reversal_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process reversal signal (close + opposite entry).
        
        Args:
            alert: Reversal alert data
            
        Returns:
            dict: Reversal execution result
        """
        pass
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load plugin metadata"""
        return {
            "version": "1.0.0",
            "author": "Zepix Team",
            "description": "Base plugin",
            "supported_signals": []
        }
    
    def validate_alert(self, alert: Any) -> bool:
        """
        Validate alert before processing.
        
        Override for custom validation logic.
        """
        return True
    
    def get_database_connection(self):
        """Get plugin's isolated database connection"""
        import sqlite3
        return sqlite3.connect(self.db_path)
    
    def enable(self):
        """Enable this plugin"""
        self.enabled = True
        self.logger.info(f"Plugin {self.plugin_id} enabled")
    
    def disable(self):
        """Disable this plugin"""
        self.enabled = False
        self.logger.info(f"Plugin {self.plugin_id} disabled")
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status"""
        return {
            "plugin_id": self.plugin_id,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "database": self.db_path
        }
