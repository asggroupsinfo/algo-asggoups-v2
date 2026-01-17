import importlib
import importlib.util
import asyncio
import os
from typing import Dict, Optional, List, Any
import logging

from .base_plugin import BaseLogicPlugin
from .plugin_interface import ISignalProcessor

logger = logging.getLogger(__name__)

# Backward compatibility mapping for legacy plugin names
LEGACY_PLUGIN_NAMES = {
    'combined_v3': 'v3_combined',
    'price_action_1m': 'v6_price_action_1m',
    'price_action_5m': 'v6_price_action_5m',
    'price_action_15m': 'v6_price_action_15m',
    'price_action_1h': 'v6_price_action_1h',
}

# Plugin definitions with new naming convention
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
        'description': 'V6 Price Action 5-minute scalping',
        'strategy': 'V6_PRICE_ACTION',
        'timeframe': '5m',
        'enabled': True
    },
    'v6_price_action_15m': {
        'class': 'V6PriceAction15mPlugin',
        'module': 'src.logic_plugins.v6_price_action_15m.plugin',
        'description': 'V6 Price Action 15-minute intraday',
        'strategy': 'V6_PRICE_ACTION',
        'timeframe': '15m',
        'enabled': True
    },
    'v6_price_action_1h': {
        'class': 'V6PriceAction1hPlugin',
        'module': 'src.logic_plugins.v6_price_action_1h.plugin',
        'description': 'V6 Price Action 1-hour swing',
        'strategy': 'V6_PRICE_ACTION',
        'timeframe': '1h',
        'enabled': True
    }
}


class PluginRegistry:
    """
    Central registry for all trading logic plugins.
    
    Responsibilities:
    - Discover plugins from plugin directory
    - Load and initialize plugins
    - Route alerts to correct plugin
    - Manage plugin lifecycle
    """
    
    def __init__(self, config: Dict, service_api):
        """
        Initialize plugin registry.
        
        Args:
            config: Bot configuration
            service_api: Shared services API
        """
        self.config = config
        self.service_api = service_api
        self.plugins: Dict[str, BaseLogicPlugin] = {}
        
        self.plugin_dir = config.get("plugin_system", {}).get("plugin_dir", "src/logic_plugins")
        
        logger.info("Plugin registry initialized")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in plugin directory.
        
        Returns:
            list: Plugin directory names
        """
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            return []
        
        plugins = []
        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            
            # Check if it's a valid plugin directory
            if os.path.isdir(plugin_path) and not item.startswith("_"):
                if os.path.exists(os.path.join(plugin_path, "plugin.py")):
                    plugins.append(item)
        
        logger.info(f"Discovered {len(plugins)} plugins: {plugins}")
        return plugins
    
    def load_plugin(self, plugin_id: str) -> bool:
        """
        Load and register a single plugin.
        
        Args:
            plugin_id: Plugin identifier (directory name)
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            # Handle legacy plugin names
            original_id = plugin_id
            if plugin_id in LEGACY_PLUGIN_NAMES:
                plugin_id = LEGACY_PLUGIN_NAMES[plugin_id]
                logger.warning(f"Using legacy plugin name '{original_id}', please update to: {plugin_id}")
            
            # Import plugin module
            # plugin_dir could be relative, e.g. "src/logic_plugins"
            # We need to turn this into a package path: "src.logic_plugins"
            package_path = self.plugin_dir.replace('/', '.').replace('\\', '.')
            module_path = f"{package_path}.{plugin_id}.plugin"
            
            plugin_module = importlib.import_module(module_path)
            
            # Get plugin class from AVAILABLE_PLUGINS if defined, otherwise construct
            if plugin_id in AVAILABLE_PLUGINS:
                class_name = AVAILABLE_PLUGINS[plugin_id]['class']
            else:
                # Fallback: Construct expected class name: "my_plugin" -> "MyPluginPlugin"
                class_name = f"{plugin_id.title().replace('_', '')}Plugin"
            plugin_class = getattr(plugin_module, class_name)
            
            # Load plugin config
            plugin_config = self.config.get("plugins", {}).get(plugin_id, {})
            
            # Instantiate plugin
            plugin_instance = plugin_class(
                plugin_id=plugin_id,
                config=plugin_config,
                service_api=self.service_api
            )
            
            # Register
            self.plugins[plugin_id] = plugin_instance
            
            logger.info(f"Loaded plugin: {plugin_id}")
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import plugin module {plugin_id}: {e}")
            return False
        except AttributeError as e:
            logger.error(f"Plugin class not found in {plugin_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return False
    
    def load_all_plugins(self):
        """Discover and load all available plugins"""
        plugins = self.discover_plugins()
        
        for plugin_id in plugins:
            self.load_plugin(plugin_id)
        
        logger.info(f"Loaded {len(self.plugins)} plugins")
    
    def get_plugin(self, plugin_id: str) -> Optional[BaseLogicPlugin]:
        """
        Get plugin instance by ID.
        
        Supports legacy plugin names for backward compatibility.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            BaseLogicPlugin or None
        """
        # Handle legacy plugin names
        if plugin_id in LEGACY_PLUGIN_NAMES:
            new_id = LEGACY_PLUGIN_NAMES[plugin_id]
            logger.warning(f"Using legacy plugin name '{plugin_id}', please update to: {new_id}")
            plugin_id = new_id
        
        return self.plugins.get(plugin_id)
    
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
        
        for plugin_id, plugin in self.plugins.items():
            if not plugin.enabled:
                continue
            
            # Check if plugin supports this strategy
            if hasattr(plugin, 'get_supported_strategies'):
                supported_strategies = plugin.get_supported_strategies()
                if strategy in supported_strategies:
                    # Check timeframe if specified
                    if timeframe and hasattr(plugin, 'get_supported_timeframes'):
                        supported_timeframes = plugin.get_supported_timeframes()
                        if timeframe in supported_timeframes:
                            logger.debug(f"Signal matched to plugin: {plugin_id} (strategy={strategy}, tf={timeframe})")
                            return plugin
                    else:
                        logger.debug(f"Signal matched to plugin: {plugin_id} (strategy={strategy})")
                        return plugin
        
        logger.warning(f"No plugin found for signal: strategy={strategy}, timeframe={timeframe}")
        return None
    
    def get_plugins_by_priority(self) -> List[BaseLogicPlugin]:
        """
        Return all enabled plugins sorted by priority.
        Higher priority plugins are returned first.
        
        Returns:
            list: Enabled plugins sorted by priority (descending)
        """
        enabled_plugins = [p for p in self.plugins.values() if p.enabled]
        return sorted(enabled_plugins, key=lambda p: getattr(p, 'priority', 0), reverse=True)
    
    def broadcast_signal(self, signal_data: Dict[str, Any]) -> List[BaseLogicPlugin]:
        """
        Find ALL plugins that can process a signal.
        Used for shadow mode comparison.
        
        Args:
            signal_data: Signal data
            
        Returns:
            list: All plugins that can handle this signal
        """
        matching_plugins = []
        for plugin_id, plugin in self.plugins.items():
            if not plugin.enabled:
                continue
            if hasattr(plugin, 'can_process_signal'):
                # can_process_signal might be async, handle sync check
                try:
                    if asyncio.iscoroutinefunction(plugin.can_process_signal):
                        # For sync context, check via get_supported_strategies instead
                        if hasattr(plugin, 'get_supported_strategies'):
                            strategy = signal_data.get('strategy', '')
                            if strategy in plugin.get_supported_strategies():
                                matching_plugins.append(plugin)
                    else:
                        if plugin.can_process_signal(signal_data):
                            matching_plugins.append(plugin)
                except Exception as e:
                    logger.error(f"Error checking plugin {plugin_id}: {e}")
        return matching_plugins
    
    async def route_alert_to_plugin(self, alert, plugin_id: str) -> Dict[str, Any]:
        """
        Route alert to specified plugin.
        
        Args:
            alert: Alert data
            plugin_id: Target plugin ID
            
        Returns:
            dict: Execution result from plugin
        """
        plugin = self.get_plugin(plugin_id)
        
        if not plugin:
            # Instead of raising, return error dict to avoid crashing caller
            logger.error(f"Plugin not found: {plugin_id}")
            return {"error": "plugin_not_found"}
        
        if not plugin.enabled:
            logger.warning(f"Plugin {plugin_id} is disabled, skipping alert")
            return {"skipped": True, "reason": "plugin_disabled"}
        
        # Route based on alert type - assume alert object has signal_type
        signal_type = getattr(alert, "signal_type", None)
        if not signal_type and isinstance(alert, dict):
             signal_type = alert.get("signal_type")

        if not signal_type:
             logger.warning("Alert missing signal_type")
             return {"error": "missing_signal_type"}

        if "entry" in signal_type.lower():
            return await plugin.process_entry_signal(alert)
        elif "exit" in signal_type.lower():
            return await plugin.process_exit_signal(alert)
        elif "reversal" in signal_type.lower():
            return await plugin.process_reversal_signal(alert)
        else:
            logger.warning(f"Unknown signal type: {signal_type}")
            return {"error": "unknown_signal_type"}
    
    async def execute_hook(self, hook_name: str, data: Any) -> Any:
        """
        Execute a hook across all enabled plugins.
        
        Args:
            hook_name: Name of hook event (e.g., 'signal_received')
            data: Data to pass to hook
            
        Returns:
            Modified data (pipe-and-filter style) or original if no modifications
        """
        result = data
        
        for plugin_id, plugin in self.plugins.items():
            if not plugin.enabled:
                continue
            
            # Check if plugin has hook handler
            handler_name = f"on_{hook_name}"
            if hasattr(plugin, handler_name):
                try:
                    handler = getattr(plugin, handler_name)
                    
                    # Support both sync and async hooks
                    if importlib.util.find_spec("asyncio") and asyncio.iscoroutinefunction(handler):
                        modified = await handler(result)
                    else:
                        modified = handler(result)
                        
                    if modified is not None:
                        result = modified
                        
                    # If result explicitly set to None/False by plugin?
                    # We assume handler returns modified data object.
                    
                except Exception as e:
                    logger.error(f"Error in plugin {plugin_id} hook {hook_name}: {e}")
        
        return result
    
    def get_all_plugins(self) -> Dict[str, BaseLogicPlugin]:
        """Get all registered plugins"""
        return self.plugins
    
    def get_plugin_status(self, plugin_id: str) -> Optional[Dict]:
        """Get status of specific plugin"""
        plugin = self.get_plugin(plugin_id)
        return plugin.get_status() if plugin else None
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """
        Enable a plugin by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if plugin was enabled successfully
        """
        plugin = self.get_plugin(plugin_id)
        if plugin:
            plugin.enabled = True
            logger.info(f"Plugin enabled: {plugin_id}")
            return True
        logger.warning(f"Plugin not found: {plugin_id}")
        return False
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """
        Disable a plugin by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if plugin was disabled successfully
        """
        plugin = self.get_plugin(plugin_id)
        if plugin:
            plugin.enabled = False
            logger.info(f"Plugin disabled: {plugin_id}")
            return True
        logger.warning(f"Plugin not found: {plugin_id}")
        return False
    
    async def on_sl_hit(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle stop loss hit event across all enabled plugins.
        
        Args:
            trade_data: Trade data including symbol, direction, profit, etc.
            
        Returns:
            Dict with results from all plugins
        """
        results = {}
        for plugin_id, plugin in self.plugins.items():
            if not plugin.enabled:
                continue
            
            if hasattr(plugin, 'on_sl_hit'):
                try:
                    handler = getattr(plugin, 'on_sl_hit')
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(trade_data)
                    else:
                        result = handler(trade_data)
                    results[plugin_id] = result
                except Exception as e:
                    logger.error(f"Error in plugin {plugin_id} on_sl_hit: {e}")
                    results[plugin_id] = {"error": str(e)}
        
        return results
    
    async def on_tp_hit(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle take profit hit event across all enabled plugins.
        
        Args:
            trade_data: Trade data including symbol, direction, profit, etc.
            
        Returns:
            Dict with results from all plugins
        """
        results = {}
        for plugin_id, plugin in self.plugins.items():
            if not plugin.enabled:
                continue
            
            if hasattr(plugin, 'on_tp_hit'):
                try:
                    handler = getattr(plugin, 'on_tp_hit')
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(trade_data)
                    else:
                        result = handler(trade_data)
                    results[plugin_id] = result
                except Exception as e:
                    logger.error(f"Error in plugin {plugin_id} on_tp_hit: {e}")
                    results[plugin_id] = {"error": str(e)}
        
        return results
