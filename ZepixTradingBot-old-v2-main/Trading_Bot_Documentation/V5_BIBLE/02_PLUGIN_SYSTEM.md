# PLUGIN SYSTEM

**Files:**
- `src/core/plugin_system/plugin_registry.py` (468 lines)
- `src/core/plugin_system/base_plugin.py` (121 lines)
- `src/core/plugin_router.py` (286 lines)

**Purpose:** Plugin discovery, loading, routing, and management

---

## OVERVIEW

The Plugin System is the foundation of the V5 Hybrid Architecture. It enables modular trading logic that can be developed, tested, and deployed independently.

### Key Components

1. **PluginRegistry:** Central registry for all plugins
2. **BaseLogicPlugin:** Abstract base class for all plugins
3. **PluginRouter:** Routes signals to appropriate plugins
4. **Plugin Interfaces:** Contracts that plugins must implement

---

## PLUGIN REGISTRY

### File: `src/core/plugin_system/plugin_registry.py`

### Available Plugins Configuration (Lines 23-66)

```python
AVAILABLE_PLUGINS = {
    # V3 Plugins
    'v3_combined': {
        'class': 'V3CombinedPlugin',
        'module': 'src.logic_plugins.v3_combined.plugin',
        'description': 'V3 Combined Logic (multi-timeframe)',
        'strategy': 'V3_COMBINED',
        'timeframes': ['5m', '15m', '1h'],
        'enabled': True
    },
    
    # V6 Plugins
    'v6_price_action_1m': {
        'class': 'V6PriceAction1mPlugin',
        'module': 'src.logic_plugins.v6_price_action_1m.plugin',
        'description': 'V6 Price Action 1-minute scalping',
        'strategy': 'V6_PRICE_ACTION',
        'timeframe': '1m',
        'enabled': True
    },
    'v6_price_action_5m': {
        'class': 'V6PriceAction5mPlugin',
        'module': 'src.logic_plugins.v6_price_action_5m.plugin',
        'description': 'V6 Price Action 5-minute momentum',
        'strategy': 'V6_PRICE_ACTION',
        'timeframe': '5m',
        'enabled': True
    },
    'v6_price_action_15m': {
        'class': 'V6PriceAction15mPlugin',
        'module': 'src.logic_plugins.v6_price_action_15m.plugin',
        'description': 'V6 Price Action 15-minute swing',
        'strategy': 'V6_PRICE_ACTION',
        'timeframe': '15m',
        'enabled': True
    },
    'v6_price_action_1h': {
        'class': 'V6PriceAction1hPlugin',
        'module': 'src.logic_plugins.v6_price_action_1h.plugin',
        'description': 'V6 Price Action 1-hour position',
        'strategy': 'V6_PRICE_ACTION',
        'timeframe': '1h',
        'enabled': True
    }
}
```

### Class Definition (Lines 70-150)

```python
class PluginRegistry:
    """
    Central registry for all trading logic plugins.
    
    Responsibilities:
    - Plugin discovery and loading
    - Plugin lifecycle management
    - Signal-to-plugin routing
    - Plugin health monitoring
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.plugins: Dict[str, BaseLogicPlugin] = {}
        self.plugin_configs: Dict[str, Dict] = {}
        self._load_plugins()
    
    def _load_plugins(self):
        """Load all enabled plugins from AVAILABLE_PLUGINS"""
        for plugin_id, plugin_info in AVAILABLE_PLUGINS.items():
            if not plugin_info.get('enabled', True):
                continue
            
            try:
                # Dynamic import
                module = importlib.import_module(plugin_info['module'])
                plugin_class = getattr(module, plugin_info['class'])
                
                # Get plugin-specific config
                plugin_config = self.config.get('plugins', {}).get(plugin_id, {})
                
                # Instantiate plugin
                plugin = plugin_class(
                    plugin_id=plugin_id,
                    config=plugin_config,
                    service_api=None  # Injected later
                )
                
                self.plugins[plugin_id] = plugin
                self.plugin_configs[plugin_id] = plugin_info
                
                logger.info(f"Plugin loaded: {plugin_id}")
                
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_id}: {e}")
```

### Signal Routing (Lines 207-242)

**CRITICAL:** This is the primary method for finding the right plugin for a signal.

```python
def get_plugin_for_signal(self, signal_data: Dict[str, Any]) -> Optional[BaseLogicPlugin]:
    """
    Find the appropriate plugin for a given signal.
    Uses strategy name and timeframe to match.
    
    This is the primary method for signal-based plugin delegation.
    
    Args:
        signal_data: Signal data containing 'strategy', 'timeframe', etc.
        
    Returns:
        BaseLogicPlugin: Matching plugin or None if no match found
    """
    strategy = signal_data.get('strategy', '')
    timeframe = signal_data.get('timeframe', signal_data.get('tf', ''))
    
    # First try: Exact match on strategy + timeframe
    for plugin_id, plugin_info in self.plugin_configs.items():
        if plugin_info.get('strategy') == strategy:
            plugin_tf = plugin_info.get('timeframe', '')
            plugin_tfs = plugin_info.get('timeframes', [])
            
            if timeframe == plugin_tf or timeframe in plugin_tfs:
                return self.plugins.get(plugin_id)
    
    # Second try: Strategy-only match
    for plugin_id, plugin_info in self.plugin_configs.items():
        if plugin_info.get('strategy') == strategy:
            return self.plugins.get(plugin_id)
    
    # No match found
    return None
```

### Plugin Management Methods (Lines 250-375)

```python
def get_plugin(self, plugin_id: str) -> Optional[BaseLogicPlugin]:
    """Get plugin by ID"""
    return self.plugins.get(plugin_id)

def get_all_plugins(self) -> Dict[str, BaseLogicPlugin]:
    """Get all loaded plugins"""
    return self.plugins.copy()

def enable_plugin(self, plugin_id: str) -> bool:
    """Enable a plugin"""
    if plugin_id in AVAILABLE_PLUGINS:
        AVAILABLE_PLUGINS[plugin_id]['enabled'] = True
        self._load_single_plugin(plugin_id)
        return True
    return False

def disable_plugin(self, plugin_id: str) -> bool:
    """Disable a plugin"""
    if plugin_id in self.plugins:
        del self.plugins[plugin_id]
        if plugin_id in AVAILABLE_PLUGINS:
            AVAILABLE_PLUGINS[plugin_id]['enabled'] = False
        return True
    return False

def get_plugin_status(self) -> Dict[str, Any]:
    """Get status of all plugins"""
    status = {}
    for plugin_id, plugin in self.plugins.items():
        status[plugin_id] = {
            'enabled': True,
            'status': plugin.get_status(),
            'config': self.plugin_configs.get(plugin_id, {})
        }
    return status
```

---

## BASE LOGIC PLUGIN

### File: `src/core/plugin_system/base_plugin.py`

### Abstract Base Class (Lines 7-79)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseLogicPlugin(ABC):
    """
    Base class for all trading logic plugins.
    
    Plugins must implement:
    - process_entry_signal()
    - process_exit_signal()
    - process_reversal_signal()
    
    Optional implementations:
    - on_sl_hit()
    - on_tp_hit()
    - on_recovery_signal()
    """
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        """
        Initialize base plugin.
        
        Args:
            plugin_id: Unique identifier for this plugin
            config: Plugin-specific configuration
            service_api: ServiceAPI instance for core operations
        """
        self.plugin_id = plugin_id
        self.config = config
        self.service_api = service_api
        self.logger = logging.getLogger(f"plugin.{plugin_id}")
        
        self._metadata = self._load_metadata()
    
    @abstractmethod
    async def process_entry_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process entry signal and execute trade.
        
        Args:
            alert: Alert data (dict or typed alert object)
            
        Returns:
            dict: Execution result with status, order_id, etc.
        """
        pass
    
    @abstractmethod
    async def process_exit_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process exit signal and close trades.
        
        Args:
            alert: Exit alert data
            
        Returns:
            dict: Exit result with closed positions
        """
        pass
    
    @abstractmethod
    async def process_reversal_signal(self, alert: Any) -> Dict[str, Any]:
        """
        Process reversal signal (close + opposite entry).
        
        Args:
            alert: Reversal alert data
            
        Returns:
            dict: Reversal result with exit and entry details
        """
        pass
```

### Optional Methods (Lines 80-121)

```python
    async def on_sl_hit(self, event: Any) -> bool:
        """
        Handle SL hit event. Override for custom recovery logic.
        
        Args:
            event: SL hit event data
            
        Returns:
            bool: True if recovery started
        """
        return False
    
    async def on_tp_hit(self, event: Any) -> bool:
        """
        Handle TP hit event. Override for continuation logic.
        
        Args:
            event: TP hit event data
            
        Returns:
            bool: True if continuation started
        """
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status"""
        return {
            'plugin_id': self.plugin_id,
            'enabled': True,
            'metadata': self._metadata
        }
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load plugin metadata. Override in subclasses."""
        return {
            'version': '1.0.0',
            'author': 'Zepix Team'
        }
```

---

## PLUGIN ROUTER

### File: `src/core/plugin_router.py`

### Routing Logic (Lines 36-77)

```python
class PluginRouter:
    """
    Routes parsed signals to appropriate plugins.
    
    Routing Priority:
    1. Explicit plugin_hint in signal
    2. Strategy + timeframe match
    3. Strategy-only match
    4. Broadcast to all capable plugins (shadow mode)
    """
    
    def __init__(self, registry: PluginRegistry, config: Dict[str, Any]):
        self.registry = registry
        self.config = config
    
    async def route_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Route signal to appropriate plugin and return result.
        
        Routing priority:
        1. Explicit plugin_hint in signal
        2. Strategy + timeframe match
        3. Strategy-only match
        4. Broadcast to all capable plugins (shadow mode)
        
        Args:
            signal: Parsed signal data
            
        Returns:
            dict: Plugin execution result or None
        """
        # Check for explicit plugin hint
        plugin_hint = signal.get('plugin_hint')
        if plugin_hint:
            plugin = self.registry.get_plugin(plugin_hint)
            if plugin:
                return await plugin.process_signal(signal)
        
        # Use registry's routing logic
        plugin = self.registry.get_plugin_for_signal(signal)
        if plugin:
            return await plugin.process_signal(signal)
        
        # No plugin found
        logger.warning(f"No plugin found for signal: {signal}")
        return None
```

### Broadcast Mode (Lines 100-150)

```python
    async def broadcast_signal(self, signal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Broadcast signal to all capable plugins.
        Used in shadow mode for comparison.
        
        Args:
            signal: Signal to broadcast
            
        Returns:
            list: Results from all plugins
        """
        results = []
        
        for plugin_id, plugin in self.registry.get_all_plugins().items():
            if await plugin.can_process_signal(signal):
                try:
                    result = await plugin.process_signal(signal)
                    results.append({
                        'plugin_id': plugin_id,
                        'result': result
                    })
                except Exception as e:
                    results.append({
                        'plugin_id': plugin_id,
                        'error': str(e)
                    })
        
        return results
```

---

## PLUGIN INTERFACES

### ISignalProcessor Interface

```python
class ISignalProcessor(ABC):
    """Interface for signal processing capability"""
    
    @abstractmethod
    def get_supported_strategies(self) -> List[str]:
        """Return list of strategy names this plugin supports."""
        pass
    
    @abstractmethod
    def get_supported_timeframes(self) -> List[str]:
        """Return list of timeframes this plugin supports."""
        pass
    
    @abstractmethod
    async def can_process_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Check if this plugin can process the given signal."""
        pass
    
    @abstractmethod
    async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process the signal and return result."""
        pass
```

### IOrderExecutor Interface

```python
class IOrderExecutor(ABC):
    """Interface for order execution capability"""
    
    @abstractmethod
    async def execute_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an order and return result."""
        pass
    
    @abstractmethod
    async def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> bool:
        """Modify an existing order."""
        pass
    
    @abstractmethod
    async def close_order(self, order_id: str, reason: str) -> bool:
        """Close an existing order."""
        pass
```

### IReentryCapable Interface

```python
class IReentryCapable(ABC):
    """Interface for re-entry capability"""
    
    @abstractmethod
    async def on_sl_hit(self, event: ReentryEvent) -> bool:
        """Handle SL hit for potential recovery."""
        pass
    
    @abstractmethod
    async def on_tp_hit(self, event: ReentryEvent) -> bool:
        """Handle TP hit for potential continuation."""
        pass
    
    @abstractmethod
    async def on_recovery_signal(self, event: ReentryEvent) -> Dict[str, Any]:
        """Process recovery signal."""
        pass
    
    @abstractmethod
    def get_chain_level(self, trade_id: str) -> int:
        """Get current chain level for a trade."""
        pass
    
    @abstractmethod
    def get_max_chain_level(self) -> int:
        """Get maximum allowed chain level."""
        pass
```

### IDualOrderCapable Interface

```python
class IDualOrderCapable(ABC):
    """Interface for dual order capability"""
    
    @abstractmethod
    async def create_dual_orders(self, signal: Dict[str, Any]) -> DualOrderResult:
        """Create both Order A and Order B."""
        pass
    
    @abstractmethod
    async def get_order_a_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """Get Order A configuration."""
        pass
    
    @abstractmethod
    async def get_order_b_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """Get Order B configuration."""
        pass
    
    @abstractmethod
    async def on_order_a_closed(self, order_id: str, reason: str) -> None:
        """Handle Order A closure."""
        pass
    
    @abstractmethod
    async def on_order_b_closed(self, order_id: str, reason: str) -> None:
        """Handle Order B closure."""
        pass
```

### IProfitBookingCapable Interface

```python
class IProfitBookingCapable(ABC):
    """Interface for profit booking capability"""
    
    @abstractmethod
    async def create_profit_chain(self, order_b_id: str, signal: Dict[str, Any]) -> Optional[ProfitChain]:
        """Create a new profit booking chain."""
        pass
    
    @abstractmethod
    async def on_profit_target_hit(self, chain_id: str, order_id: str) -> BookingResult:
        """Handle profit target hit."""
        pass
    
    @abstractmethod
    async def on_chain_sl_hit(self, chain_id: str) -> None:
        """Handle chain SL hit."""
        pass
    
    @abstractmethod
    def get_active_chains(self) -> Dict[str, ProfitChain]:
        """Get all active profit chains."""
        pass
    
    @abstractmethod
    def get_pyramid_config(self) -> Dict[str, Any]:
        """Get pyramid configuration."""
        pass
```

### IAutonomousCapable Interface

```python
class IAutonomousCapable(ABC):
    """Interface for autonomous operations capability"""
    
    @abstractmethod
    async def check_recovery_allowed(self, trade_id: str) -> SafetyCheckResult:
        """Check if recovery is allowed for a trade."""
        pass
    
    @abstractmethod
    async def activate_reverse_shield(self, trade: Any) -> Dict[str, Any]:
        """Activate reverse shield protection."""
        pass
    
    @abstractmethod
    async def deactivate_reverse_shield(self, shield_id: str) -> bool:
        """Deactivate reverse shield."""
        pass
    
    @abstractmethod
    def get_safety_stats(self) -> Dict[str, Any]:
        """Get safety statistics."""
        pass
```

---

## PLUGIN LIFECYCLE

### Loading

```
1. PluginRegistry.__init__()
2. _load_plugins() - Load all enabled plugins
3. Dynamic import of plugin module
4. Plugin class instantiation
5. Plugin registered in self.plugins dict
```

### Initialization

```
1. TradingEngine._initialize_plugins()
2. ServiceAPI injected into each plugin
3. Plugin registered with ShadowModeManager
4. Plugin ready for signal processing
```

### Execution

```
1. Signal received by TradingEngine
2. delegate_to_plugin() called
3. PluginRegistry.get_plugin_for_signal()
4. Plugin.process_signal() executed
5. Result returned to TradingEngine
```

### Shutdown

```
1. TradingEngine.shutdown()
2. Each plugin's cleanup method called
3. Plugins removed from registry
4. Resources released
```

---

## CONFIGURATION

### Plugin Configuration Structure

```python
{
    "plugins": {
        "v3_combined": {
            "enabled": true,
            "shadow_mode": false,
            "settings": {
                "entry_conditions": {...},
                "risk_management": {...}
            }
        },
        "v6_price_action_5m": {
            "enabled": true,
            "shadow_mode": true,
            "settings": {
                "adx_threshold": 25,
                "confidence_threshold": 70,
                "require_15m_alignment": true
            }
        }
    }
}
```

---

## RELATED FILES

- `src/core/trading_engine.py` - Uses PluginRegistry
- `src/core/plugin_system/service_api.py` - Injected into plugins
- `src/logic_plugins/v3_combined/plugin.py` - V3 implementation
- `src/logic_plugins/v6_price_action_*/plugin.py` - V6 implementations
