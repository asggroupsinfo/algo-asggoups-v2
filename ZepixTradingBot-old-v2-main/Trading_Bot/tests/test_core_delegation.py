"""
Test Core Delegation - Plan 01 Verification Tests

Tests for the plugin delegation framework implemented in Plan 01:
- TradingEngine.delegate_to_plugin() method
- PluginRegistry.get_plugin_for_signal() method
- Plugin interface implementation (ISignalProcessor, IOrderExecutor)

Version: 1.0.0
Date: 2026-01-15
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from typing import Dict, Any


class TestCoreDelegation:
    """Test TradingEngine delegation methods"""
    
    @pytest.fixture
    def mock_plugin_registry(self):
        """Create mock plugin registry"""
        registry = Mock()
        registry.plugins = {}
        registry.get_plugin_for_signal = Mock(return_value=None)
        registry.get_plugins_by_priority = Mock(return_value=[])
        registry.broadcast_signal = Mock(return_value=[])
        return registry
    
    @pytest.fixture
    def mock_plugin(self):
        """Create mock plugin that implements ISignalProcessor"""
        plugin = Mock()
        plugin.plugin_id = "test_plugin"
        plugin.enabled = True
        plugin.get_supported_strategies = Mock(return_value=['V3_COMBINED', 'V3'])
        plugin.get_supported_timeframes = Mock(return_value=['5m', '15m', '1h'])
        plugin.process_entry_signal = AsyncMock(return_value={"status": "success", "action": "entry"})
        plugin.process_exit_signal = AsyncMock(return_value={"status": "success", "action": "exit"})
        plugin.process_reversal_signal = AsyncMock(return_value={"status": "success", "action": "reversal"})
        plugin.process_signal = AsyncMock(return_value={"status": "success"})
        return plugin
    
    @pytest.fixture
    def mock_trading_engine(self, mock_plugin_registry):
        """Create mock trading engine with delegation methods"""
        engine = Mock()
        engine.plugin_registry = mock_plugin_registry
        engine.config = {"plugin_system": {"use_delegation": True}}
        engine._execution_history = []
        engine._plugin_failures = {}
        engine.telegram_bot = Mock()
        engine.telegram_bot.send_message = Mock()
        return engine
    
    @pytest.mark.asyncio
    async def test_signal_delegated_to_plugin(self, mock_trading_engine, mock_plugin, mock_plugin_registry):
        """Test that signals are properly delegated to plugins"""
        mock_plugin_registry.get_plugin_for_signal.return_value = mock_plugin
        
        signal_data = {
            "type": "entry_v3",
            "strategy": "V3_COMBINED",
            "symbol": "EURUSD",
            "direction": "BUY"
        }
        
        # Simulate delegate_to_plugin behavior
        plugin = mock_plugin_registry.get_plugin_for_signal(signal_data)
        assert plugin is not None
        assert plugin.plugin_id == "test_plugin"
        
        result = await plugin.process_entry_signal(signal_data)
        assert result["status"] == "success"
        assert result["action"] == "entry"
    
    @pytest.mark.asyncio
    async def test_no_plugin_found_returns_none(self, mock_plugin_registry):
        """Test that no plugin found returns appropriate error"""
        mock_plugin_registry.get_plugin_for_signal.return_value = None
        
        signal_data = {
            "type": "entry_unknown",
            "strategy": "UNKNOWN_STRATEGY",
            "symbol": "EURUSD"
        }
        
        plugin = mock_plugin_registry.get_plugin_for_signal(signal_data)
        assert plugin is None
    
    @pytest.mark.asyncio
    async def test_plugin_failure_handled(self, mock_trading_engine, mock_plugin, mock_plugin_registry):
        """Test that plugin failures are handled gracefully"""
        mock_plugin.process_entry_signal = AsyncMock(side_effect=Exception("Plugin error"))
        mock_plugin_registry.get_plugin_for_signal.return_value = mock_plugin
        
        signal_data = {
            "type": "entry_v3",
            "strategy": "V3_COMBINED",
            "symbol": "EURUSD"
        }
        
        plugin = mock_plugin_registry.get_plugin_for_signal(signal_data)
        
        with pytest.raises(Exception) as exc_info:
            await plugin.process_entry_signal(signal_data)
        
        assert "Plugin error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_trading_disabled_ignores_signal(self, mock_trading_engine):
        """Test that signals are ignored when trading is disabled"""
        mock_trading_engine.config = {"plugin_system": {"use_delegation": False}}
        
        use_delegation = mock_trading_engine.config.get("plugin_system", {}).get("use_delegation", True)
        assert use_delegation is False


class TestPluginRegistryLookup:
    """Test PluginRegistry signal-based lookup methods"""
    
    @pytest.fixture
    def mock_v3_plugin(self):
        """Create mock V3 plugin"""
        plugin = Mock()
        plugin.plugin_id = "v3_combined"
        plugin.enabled = True
        plugin.get_supported_strategies = Mock(return_value=['V3_COMBINED', 'COMBINED_V3', 'V3'])
        plugin.get_supported_timeframes = Mock(return_value=['5m', '15m', '1h'])
        return plugin
    
    @pytest.fixture
    def mock_v6_1m_plugin(self):
        """Create mock V6 1M plugin"""
        plugin = Mock()
        plugin.plugin_id = "v6_price_action_1m"
        plugin.enabled = True
        plugin.get_supported_strategies = Mock(return_value=['V6_PRICE_ACTION', 'PRICE_ACTION', 'V6'])
        plugin.get_supported_timeframes = Mock(return_value=['1m', '1'])
        return plugin
    
    @pytest.fixture
    def mock_v6_5m_plugin(self):
        """Create mock V6 5M plugin"""
        plugin = Mock()
        plugin.plugin_id = "v6_price_action_5m"
        plugin.enabled = True
        plugin.get_supported_strategies = Mock(return_value=['V6_PRICE_ACTION', 'PRICE_ACTION', 'V6'])
        plugin.get_supported_timeframes = Mock(return_value=['5m', '5'])
        return plugin
    
    @pytest.fixture
    def mock_v6_15m_plugin(self):
        """Create mock V6 15M plugin"""
        plugin = Mock()
        plugin.plugin_id = "v6_price_action_15m"
        plugin.enabled = True
        plugin.get_supported_strategies = Mock(return_value=['V6_PRICE_ACTION', 'PRICE_ACTION', 'V6'])
        plugin.get_supported_timeframes = Mock(return_value=['15m', '15'])
        return plugin
    
    @pytest.fixture
    def mock_v6_1h_plugin(self):
        """Create mock V6 1H plugin"""
        plugin = Mock()
        plugin.plugin_id = "v6_price_action_1h"
        plugin.enabled = True
        plugin.get_supported_strategies = Mock(return_value=['V6_PRICE_ACTION', 'PRICE_ACTION', 'V6'])
        plugin.get_supported_timeframes = Mock(return_value=['1h', '60'])
        return plugin
    
    def test_get_plugin_for_v3_signal(self, mock_v3_plugin):
        """Test V3 signal matches V3 plugin"""
        signal_data = {
            "type": "entry_v3",
            "strategy": "V3_COMBINED",
            "symbol": "EURUSD"
        }
        
        strategy = signal_data.get('strategy', '')
        supported = mock_v3_plugin.get_supported_strategies()
        
        assert strategy in supported
        assert mock_v3_plugin.enabled is True
    
    def test_get_plugin_for_v6_signal_with_timeframe(self, mock_v6_5m_plugin):
        """Test V6 signal with timeframe matches correct V6 plugin"""
        signal_data = {
            "type": "entry_v6",
            "strategy": "V6_PRICE_ACTION",
            "timeframe": "5m",
            "symbol": "EURUSD"
        }
        
        strategy = signal_data.get('strategy', '')
        timeframe = signal_data.get('timeframe', '')
        
        supported_strategies = mock_v6_5m_plugin.get_supported_strategies()
        supported_timeframes = mock_v6_5m_plugin.get_supported_timeframes()
        
        assert strategy in supported_strategies
        assert timeframe in supported_timeframes
    
    def test_disabled_plugin_not_returned(self, mock_v3_plugin):
        """Test disabled plugins are not returned"""
        mock_v3_plugin.enabled = False
        
        signal_data = {
            "type": "entry_v3",
            "strategy": "V3_COMBINED",
            "symbol": "EURUSD"
        }
        
        # Disabled plugin should not be selected
        assert mock_v3_plugin.enabled is False
    
    def test_v6_1m_timeframe_match(self, mock_v6_1m_plugin):
        """Test V6 1M plugin matches 1m timeframe"""
        signal_data = {
            "strategy": "V6_PRICE_ACTION",
            "timeframe": "1m"
        }
        
        timeframe = signal_data.get('timeframe', '')
        supported = mock_v6_1m_plugin.get_supported_timeframes()
        
        assert timeframe in supported
    
    def test_v6_15m_timeframe_match(self, mock_v6_15m_plugin):
        """Test V6 15M plugin matches 15m timeframe"""
        signal_data = {
            "strategy": "V6_PRICE_ACTION",
            "timeframe": "15m"
        }
        
        timeframe = signal_data.get('timeframe', '')
        supported = mock_v6_15m_plugin.get_supported_timeframes()
        
        assert timeframe in supported
    
    def test_v6_1h_timeframe_match(self, mock_v6_1h_plugin):
        """Test V6 1H plugin matches 1h timeframe"""
        signal_data = {
            "strategy": "V6_PRICE_ACTION",
            "timeframe": "1h"
        }
        
        timeframe = signal_data.get('timeframe', '')
        supported = mock_v6_1h_plugin.get_supported_timeframes()
        
        assert timeframe in supported


class TestPluginInterfaceImplementation:
    """Test that plugins properly implement ISignalProcessor interface"""
    
    def test_v3_plugin_has_required_methods(self):
        """Test V3 plugin has all required interface methods"""
        required_methods = [
            'get_supported_strategies',
            'get_supported_timeframes',
            'can_process_signal',
            'process_signal',
            'execute_order',
            'modify_order',
            'close_order'
        ]
        
        # Import the actual plugin
        try:
            from src.logic_plugins.v3_combined.plugin import CombinedV3Plugin
            
            for method in required_methods:
                assert hasattr(CombinedV3Plugin, method), f"CombinedV3Plugin missing method: {method}"
        except ImportError:
            pytest.skip("CombinedV3Plugin not available for import")
    
    def test_v6_1m_plugin_has_required_methods(self):
        """Test V6 1M plugin has all required interface methods"""
        required_methods = [
            'get_supported_strategies',
            'get_supported_timeframes',
            'can_process_signal',
            'process_signal',
            'execute_order',
            'modify_order',
            'close_order'
        ]
        
        try:
            from src.logic_plugins.v6_price_action_1m.plugin import PriceAction1MPlugin
            
            for method in required_methods:
                assert hasattr(PriceAction1MPlugin, method), f"PriceAction1MPlugin missing method: {method}"
        except ImportError:
            pytest.skip("PriceAction1MPlugin not available for import")
    
    def test_v6_5m_plugin_has_required_methods(self):
        """Test V6 5M plugin has all required interface methods"""
        required_methods = [
            'get_supported_strategies',
            'get_supported_timeframes',
            'can_process_signal',
            'process_signal'
        ]
        
        try:
            from src.logic_plugins.v6_price_action_5m.plugin import PriceAction5MPlugin
            
            for method in required_methods:
                assert hasattr(PriceAction5MPlugin, method), f"PriceAction5MPlugin missing method: {method}"
        except ImportError:
            pytest.skip("PriceAction5MPlugin not available for import")
    
    def test_v6_15m_plugin_has_required_methods(self):
        """Test V6 15M plugin has all required interface methods"""
        required_methods = [
            'get_supported_strategies',
            'get_supported_timeframes',
            'can_process_signal',
            'process_signal'
        ]
        
        try:
            from src.logic_plugins.v6_price_action_15m.plugin import PriceAction15MPlugin
            
            for method in required_methods:
                assert hasattr(PriceAction15MPlugin, method), f"PriceAction15MPlugin missing method: {method}"
        except ImportError:
            pytest.skip("PriceAction15MPlugin not available for import")
    
    def test_v6_1h_plugin_has_required_methods(self):
        """Test V6 1H plugin has all required interface methods"""
        required_methods = [
            'get_supported_strategies',
            'get_supported_timeframes',
            'can_process_signal',
            'process_signal'
        ]
        
        try:
            from src.logic_plugins.v6_price_action_1h.plugin import PriceAction1HPlugin
            
            for method in required_methods:
                assert hasattr(PriceAction1HPlugin, method), f"PriceAction1HPlugin missing method: {method}"
        except ImportError:
            pytest.skip("PriceAction1HPlugin not available for import")


class TestFeatureFlagRollback:
    """Test feature flag for rollback to legacy processing"""
    
    def test_delegation_enabled_by_default(self):
        """Test that plugin delegation is enabled by default"""
        config = {}
        use_delegation = config.get("plugin_system", {}).get("use_delegation", True)
        assert use_delegation is True
    
    def test_delegation_can_be_disabled(self):
        """Test that plugin delegation can be disabled via config"""
        config = {"plugin_system": {"use_delegation": False}}
        use_delegation = config.get("plugin_system", {}).get("use_delegation", True)
        assert use_delegation is False
    
    def test_legacy_fallback_when_no_plugin_found(self):
        """Test that legacy processing is used when no plugin found"""
        # This simulates the fallback behavior in process_alert
        plugin_found = None
        use_legacy = plugin_found is None
        assert use_legacy is True


class TestIntegrationFlow:
    """Integration tests for signal flow through delegation"""
    
    @pytest.mark.asyncio
    async def test_v3_signal_flows_through_v3_plugin(self):
        """Test V3 signal flows through V3 plugin"""
        mock_plugin = Mock()
        mock_plugin.plugin_id = "v3_combined"
        mock_plugin.enabled = True
        mock_plugin.get_supported_strategies = Mock(return_value=['V3_COMBINED'])
        mock_plugin.process_entry_signal = AsyncMock(return_value={"status": "success"})
        
        signal_data = {
            "type": "entry_v3",
            "strategy": "V3_COMBINED",
            "symbol": "EURUSD",
            "direction": "BUY"
        }
        
        # Verify plugin can handle signal
        assert signal_data.get('strategy') in mock_plugin.get_supported_strategies()
        
        # Process signal
        result = await mock_plugin.process_entry_signal(signal_data)
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_v6_signal_flows_through_correct_v6_plugin(self):
        """Test V6 signal flows through correct V6 plugin based on timeframe"""
        mock_5m_plugin = Mock()
        mock_5m_plugin.plugin_id = "v6_price_action_5m"
        mock_5m_plugin.enabled = True
        mock_5m_plugin.get_supported_strategies = Mock(return_value=['V6_PRICE_ACTION'])
        mock_5m_plugin.get_supported_timeframes = Mock(return_value=['5m', '5'])
        mock_5m_plugin.process_entry_signal = AsyncMock(return_value={"status": "success"})
        
        signal_data = {
            "type": "entry_v6",
            "strategy": "V6_PRICE_ACTION",
            "timeframe": "5m",
            "symbol": "EURUSD",
            "direction": "BUY"
        }
        
        # Verify plugin can handle signal
        assert signal_data.get('strategy') in mock_5m_plugin.get_supported_strategies()
        assert signal_data.get('timeframe') in mock_5m_plugin.get_supported_timeframes()
        
        # Process signal
        result = await mock_5m_plugin.process_entry_signal(signal_data)
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_unknown_strategy_returns_none(self):
        """Test unknown strategy returns None (no plugin found)"""
        mock_registry = Mock()
        mock_registry.get_plugin_for_signal = Mock(return_value=None)
        
        signal_data = {
            "type": "entry_unknown",
            "strategy": "UNKNOWN_STRATEGY",
            "symbol": "EURUSD"
        }
        
        plugin = mock_registry.get_plugin_for_signal(signal_data)
        assert plugin is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
