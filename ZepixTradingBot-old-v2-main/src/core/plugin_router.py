"""
Plugin Router
Routes parsed signals to appropriate plugins

Part of Plan 02: Webhook Routing & Signal Processing
"""
from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class PluginRouter:
    """Routes signals to appropriate plugins"""
    
    def __init__(self, plugin_registry):
        """
        Initialize the plugin router.
        
        Args:
            plugin_registry: PluginRegistry instance for plugin lookup
        """
        self.registry = plugin_registry
        self._routing_stats = {
            'total_routed': 0,
            'successful': 0,
            'failed': 0,
            'no_plugin_found': 0,
            'by_strategy': {},
            'by_plugin': {}
        }
        self._last_reset = datetime.now()
    
    async def route_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Route signal to appropriate plugin and return result.
        
        Routing priority:
        1. Explicit plugin_hint in signal
        2. Strategy + timeframe match
        3. Strategy-only match
        4. Broadcast to all capable plugins (shadow mode)
        
        Args:
            signal: Parsed signal dictionary
            
        Returns:
            Result from plugin processing, or None if no plugin found
        """
        self._routing_stats['total_routed'] += 1
        strategy = signal.get('strategy', 'UNKNOWN')
        
        # Track by strategy
        if strategy not in self._routing_stats['by_strategy']:
            self._routing_stats['by_strategy'][strategy] = 0
        self._routing_stats['by_strategy'][strategy] += 1
        
        # Try explicit plugin hint first
        plugin_hint = signal.get('plugin_hint')
        if plugin_hint:
            plugin = self.registry.get_plugin(plugin_hint)
            if plugin and plugin.enabled:
                logger.info(f"Routing to hinted plugin: {plugin_hint}")
                return await self._execute_plugin(plugin, signal)
        
        # Try strategy + timeframe match using Plan 01's get_plugin_for_signal
        plugin = self.registry.get_plugin_for_signal(signal)
        if plugin:
            logger.info(f"Routing to matched plugin: {plugin.plugin_id}")
            return await self._execute_plugin(plugin, signal)
        
        # No plugin found
        self._routing_stats['no_plugin_found'] += 1
        logger.warning(f"No plugin found for signal: {strategy}/{signal.get('timeframe')}")
        return None
    
    async def _execute_plugin(self, plugin, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute plugin and track result.
        
        Args:
            plugin: Plugin instance to execute
            signal: Signal data to process
            
        Returns:
            Result from plugin processing
        """
        plugin_id = plugin.plugin_id
        
        # Track by plugin
        if plugin_id not in self._routing_stats['by_plugin']:
            self._routing_stats['by_plugin'][plugin_id] = {'success': 0, 'failed': 0}
        
        try:
            # Check if plugin implements process_signal (ISignalProcessor interface)
            if hasattr(plugin, 'process_signal'):
                result = await plugin.process_signal(signal)
            else:
                # Fallback to legacy processing
                logger.warning(f"Plugin {plugin_id} does not implement process_signal, using legacy")
                result = await self._legacy_process(plugin, signal)
            
            self._routing_stats['successful'] += 1
            self._routing_stats['by_plugin'][plugin_id]['success'] += 1
            
            logger.info(f"Plugin {plugin_id} processed signal successfully")
            return result
            
        except Exception as e:
            self._routing_stats['failed'] += 1
            self._routing_stats['by_plugin'][plugin_id]['failed'] += 1
            logger.error(f"Plugin {plugin_id} failed: {e}")
            return {'status': 'error', 'message': str(e), 'plugin_id': plugin_id}
    
    async def _legacy_process(self, plugin, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Legacy processing for plugins that don't implement ISignalProcessor.
        
        Args:
            plugin: Plugin instance
            signal: Signal data
            
        Returns:
            Result from legacy processing
        """
        alert_type = signal.get('type', '')
        
        if 'entry' in alert_type.lower():
            if hasattr(plugin, 'process_entry_signal'):
                return await plugin.process_entry_signal(signal)
        elif 'exit' in alert_type.lower():
            if hasattr(plugin, 'process_exit_signal'):
                return await plugin.process_exit_signal(signal)
        
        logger.warning(f"No suitable method found in plugin for signal type: {alert_type}")
        return None
    
    async def broadcast_signal(self, signal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Broadcast signal to ALL capable plugins.
        Used for shadow mode comparison.
        
        Args:
            signal: Signal data to broadcast
            
        Returns:
            List of results from all plugins
        """
        results = []
        matching_plugins = self.registry.broadcast_signal(signal)
        
        for plugin in matching_plugins:
            try:
                if hasattr(plugin, 'process_signal'):
                    result = await plugin.process_signal(signal)
                else:
                    result = await self._legacy_process(plugin, signal)
                    
                results.append({
                    'plugin_id': plugin.plugin_id,
                    'result': result,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'plugin_id': plugin.plugin_id,
                    'error': str(e),
                    'status': 'error'
                })
        
        return results
    
    async def route_with_fallback(self, signal: Dict[str, Any], fallback_handler) -> Optional[Dict[str, Any]]:
        """
        Route signal with fallback to legacy handler if no plugin found.
        
        Args:
            signal: Signal data
            fallback_handler: Async function to call if no plugin found
            
        Returns:
            Result from plugin or fallback handler
        """
        result = await self.route_signal(signal)
        
        if result is None and fallback_handler:
            logger.info("No plugin found, using fallback handler")
            return await fallback_handler(signal)
        
        return result
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """
        Return routing statistics.
        
        Returns:
            Dictionary with routing statistics
        """
        stats = self._routing_stats.copy()
        stats['last_reset'] = self._last_reset.isoformat()
        
        # Calculate success rate
        total = stats['total_routed']
        if total > 0:
            stats['success_rate'] = round((stats['successful'] / total) * 100, 2)
            stats['failure_rate'] = round((stats['failed'] / total) * 100, 2)
            stats['no_plugin_rate'] = round((stats['no_plugin_found'] / total) * 100, 2)
        else:
            stats['success_rate'] = 0
            stats['failure_rate'] = 0
            stats['no_plugin_rate'] = 0
        
        return stats
    
    def reset_stats(self):
        """Reset routing statistics"""
        self._routing_stats = {
            'total_routed': 0,
            'successful': 0,
            'failed': 0,
            'no_plugin_found': 0,
            'by_strategy': {},
            'by_plugin': {}
        }
        self._last_reset = datetime.now()
        logger.info("Routing statistics reset")
    
    def get_available_routes(self) -> List[Dict[str, Any]]:
        """
        Get list of all available routes (plugins that can process signals).
        
        Returns:
            List of plugin routing information
        """
        routes = []
        
        for plugin_id, plugin in self.registry._plugins.items():
            route_info = {
                'plugin_id': plugin_id,
                'enabled': plugin.enabled,
                'strategies': [],
                'timeframes': []
            }
            
            if hasattr(plugin, 'get_supported_strategies'):
                route_info['strategies'] = plugin.get_supported_strategies()
            if hasattr(plugin, 'get_supported_timeframes'):
                route_info['timeframes'] = plugin.get_supported_timeframes()
            
            routes.append(route_info)
        
        return routes


# Singleton instance
_router_instance = None


def get_plugin_router(plugin_registry=None) -> PluginRouter:
    """
    Get or create PluginRouter singleton.
    
    Args:
        plugin_registry: PluginRegistry instance (required on first call)
        
    Returns:
        PluginRouter singleton instance
    """
    global _router_instance
    
    if _router_instance is None:
        if plugin_registry is None:
            raise ValueError("plugin_registry required for first initialization")
        _router_instance = PluginRouter(plugin_registry)
        logger.info("PluginRouter singleton created")
    
    return _router_instance


def reset_plugin_router():
    """Reset the singleton instance (for testing)"""
    global _router_instance
    _router_instance = None
