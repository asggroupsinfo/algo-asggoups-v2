"""
Unit tests for the Plugin System (Phase 1 - Core Plugin System Foundation)

Tests:
- BaseLogicPlugin instantiation and methods
- PluginRegistry discovery, loading, and routing
- ServiceAPI facade methods
- Plugin lifecycle (enable/disable)
- Hook execution
"""

import pytest
import asyncio
import os
import sys
from typing import Dict, Any
from unittest.mock import Mock, MagicMock, AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.plugin_system.base_plugin import BaseLogicPlugin
from src.core.plugin_system.plugin_registry import PluginRegistry
from src.core.plugin_system.service_api import ServiceAPI


class DummyPlugin(BaseLogicPlugin):
    """Dummy plugin for testing BaseLogicPlugin"""
    
    async def process_entry_signal(self, alert) -> Dict[str, Any]:
        return {"success": True, "type": "entry", "plugin_id": self.plugin_id}
    
    async def process_exit_signal(self, alert) -> Dict[str, Any]:
        return {"success": True, "type": "exit", "plugin_id": self.plugin_id}
    
    async def process_reversal_signal(self, alert) -> Dict[str, Any]:
        return {"success": True, "type": "reversal", "plugin_id": self.plugin_id}


class DummyPluginWithHook(BaseLogicPlugin):
    """Dummy plugin with hook handler for testing"""
    
    async def process_entry_signal(self, alert) -> Dict[str, Any]:
        return {"success": True}
    
    async def process_exit_signal(self, alert) -> Dict[str, Any]:
        return {"success": True}
    
    async def process_reversal_signal(self, alert) -> Dict[str, Any]:
        return {"success": True}
    
    async def on_signal_received(self, data):
        """Hook handler that modifies signal data"""
        if isinstance(data, dict):
            data["modified_by_plugin"] = self.plugin_id
        return data


class MockAlert:
    """Mock alert for testing"""
    def __init__(self, symbol: str, signal_type: str, direction: str = "BUY"):
        self.symbol = symbol
        self.signal_type = signal_type
        self.direction = direction


class TestBaseLogicPlugin:
    """Tests for BaseLogicPlugin class"""
    
    def test_plugin_instantiation(self):
        """Test BaseLogicPlugin can be instantiated via subclass"""
        plugin = DummyPlugin("test_plugin", {}, None)
        
        assert plugin.plugin_id == "test_plugin"
        assert plugin.enabled == True
        assert plugin.db_path == "data/zepix_test_plugin.db"
    
    def test_plugin_with_config(self):
        """Test plugin respects config values"""
        config = {"enabled": False, "custom_setting": "value"}
        plugin = DummyPlugin("test_plugin", config, None)
        
        assert plugin.enabled == False
        assert plugin.config.get("custom_setting") == "value"
    
    def test_plugin_enable_disable(self):
        """Test plugin enable/disable methods"""
        plugin = DummyPlugin("test", {}, None)
        
        assert plugin.enabled == True
        
        plugin.disable()
        assert plugin.enabled == False
        
        plugin.enable()
        assert plugin.enabled == True
    
    def test_plugin_get_status(self):
        """Test plugin status reporting"""
        plugin = DummyPlugin("test_plugin", {}, None)
        status = plugin.get_status()
        
        assert status["plugin_id"] == "test_plugin"
        assert status["enabled"] == True
        assert "metadata" in status
        assert "database" in status
    
    def test_plugin_metadata(self):
        """Test plugin metadata loading"""
        plugin = DummyPlugin("test_plugin", {}, None)
        
        assert "version" in plugin.metadata
        assert "author" in plugin.metadata
        assert "description" in plugin.metadata
    
    def test_plugin_validate_alert_default(self):
        """Test default alert validation returns True"""
        plugin = DummyPlugin("test_plugin", {}, None)
        alert = MockAlert("XAUUSD", "entry")
        
        assert plugin.validate_alert(alert) == True
    
    @pytest.mark.asyncio
    async def test_process_entry_signal(self):
        """Test entry signal processing"""
        plugin = DummyPlugin("test_plugin", {}, None)
        alert = MockAlert("XAUUSD", "entry")
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["success"] == True
        assert result["type"] == "entry"
        assert result["plugin_id"] == "test_plugin"
    
    @pytest.mark.asyncio
    async def test_process_exit_signal(self):
        """Test exit signal processing"""
        plugin = DummyPlugin("test_plugin", {}, None)
        alert = MockAlert("XAUUSD", "exit")
        
        result = await plugin.process_exit_signal(alert)
        
        assert result["success"] == True
        assert result["type"] == "exit"
    
    @pytest.mark.asyncio
    async def test_process_reversal_signal(self):
        """Test reversal signal processing"""
        plugin = DummyPlugin("test_plugin", {}, None)
        alert = MockAlert("XAUUSD", "reversal")
        
        result = await plugin.process_reversal_signal(alert)
        
        assert result["success"] == True
        assert result["type"] == "reversal"


class TestPluginRegistry:
    """Tests for PluginRegistry class"""
    
    def test_registry_initialization(self):
        """Test PluginRegistry initializes correctly"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {}
        }
        registry = PluginRegistry(config, None)
        
        assert registry.plugin_dir == "src/logic_plugins"
        assert len(registry.plugins) == 0
    
    def test_discover_plugins(self):
        """Test plugin discovery finds template plugin"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {}
        }
        registry = PluginRegistry(config, None)
        
        plugins = registry.discover_plugins()
        
        assert isinstance(plugins, list)
    
    def test_discover_plugins_nonexistent_dir(self):
        """Test plugin discovery handles nonexistent directory"""
        config = {
            "plugin_system": {"plugin_dir": "nonexistent/path"},
            "plugins": {}
        }
        registry = PluginRegistry(config, None)
        
        plugins = registry.discover_plugins()
        
        assert plugins == []
    
    def test_get_plugin_not_found(self):
        """Test getting nonexistent plugin returns None"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {}
        }
        registry = PluginRegistry(config, None)
        
        plugin = registry.get_plugin("nonexistent")
        
        assert plugin is None
    
    def test_get_all_plugins_empty(self):
        """Test getting all plugins when none loaded"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {}
        }
        registry = PluginRegistry(config, None)
        
        plugins = registry.get_all_plugins()
        
        assert plugins == {}
    
    def test_get_plugin_status_not_found(self):
        """Test getting status of nonexistent plugin"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {}
        }
        registry = PluginRegistry(config, None)
        
        status = registry.get_plugin_status("nonexistent")
        
        assert status is None
    
    @pytest.mark.asyncio
    async def test_route_alert_plugin_not_found(self):
        """Test routing alert to nonexistent plugin"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {}
        }
        registry = PluginRegistry(config, None)
        alert = MockAlert("XAUUSD", "entry")
        
        result = await registry.route_alert_to_plugin(alert, "nonexistent")
        
        assert result.get("error") == "plugin_not_found"
    
    @pytest.mark.asyncio
    async def test_route_alert_plugin_disabled(self):
        """Test routing alert to disabled plugin"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {"test": {"enabled": False}}
        }
        registry = PluginRegistry(config, None)
        
        plugin = DummyPlugin("test", {"enabled": False}, None)
        registry.plugins["test"] = plugin
        
        alert = MockAlert("XAUUSD", "entry")
        result = await registry.route_alert_to_plugin(alert, "test")
        
        assert result.get("skipped") == True
        assert result.get("reason") == "plugin_disabled"
    
    @pytest.mark.asyncio
    async def test_route_entry_alert(self):
        """Test routing entry alert to plugin"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {"test": {"enabled": True}}
        }
        registry = PluginRegistry(config, None)
        
        plugin = DummyPlugin("test", {"enabled": True}, None)
        registry.plugins["test"] = plugin
        
        alert = MockAlert("XAUUSD", "entry")
        result = await registry.route_alert_to_plugin(alert, "test")
        
        assert result.get("success") == True
        assert result.get("type") == "entry"
    
    @pytest.mark.asyncio
    async def test_route_exit_alert(self):
        """Test routing exit alert to plugin"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {"test": {"enabled": True}}
        }
        registry = PluginRegistry(config, None)
        
        plugin = DummyPlugin("test", {"enabled": True}, None)
        registry.plugins["test"] = plugin
        
        alert = MockAlert("XAUUSD", "exit")
        result = await registry.route_alert_to_plugin(alert, "test")
        
        assert result.get("success") == True
        assert result.get("type") == "exit"
    
    @pytest.mark.asyncio
    async def test_route_reversal_alert(self):
        """Test routing reversal alert to plugin"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {"test": {"enabled": True}}
        }
        registry = PluginRegistry(config, None)
        
        plugin = DummyPlugin("test", {"enabled": True}, None)
        registry.plugins["test"] = plugin
        
        alert = MockAlert("XAUUSD", "reversal")
        result = await registry.route_alert_to_plugin(alert, "test")
        
        assert result.get("success") == True
        assert result.get("type") == "reversal"
    
    @pytest.mark.asyncio
    async def test_execute_hook_no_plugins(self):
        """Test hook execution with no plugins"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {}
        }
        registry = PluginRegistry(config, None)
        
        data = {"test": "data"}
        result = await registry.execute_hook("signal_received", data)
        
        assert result == data
    
    @pytest.mark.asyncio
    async def test_execute_hook_with_plugin(self):
        """Test hook execution modifies data"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {"test": {"enabled": True}}
        }
        registry = PluginRegistry(config, None)
        
        plugin = DummyPluginWithHook("test", {"enabled": True}, None)
        registry.plugins["test"] = plugin
        
        data = {"test": "data"}
        result = await registry.execute_hook("signal_received", data)
        
        assert result.get("modified_by_plugin") == "test"
    
    @pytest.mark.asyncio
    async def test_execute_hook_disabled_plugin_skipped(self):
        """Test disabled plugins are skipped in hook execution"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {"test": {"enabled": False}}
        }
        registry = PluginRegistry(config, None)
        
        plugin = DummyPluginWithHook("test", {"enabled": False}, None)
        registry.plugins["test"] = plugin
        
        data = {"test": "data"}
        result = await registry.execute_hook("signal_received", data)
        
        assert "modified_by_plugin" not in result


class TestServiceAPI:
    """Tests for ServiceAPI class"""
    
    def setup_method(self):
        """Setup mock trading engine for each test"""
        self.mock_engine = Mock()
        self.mock_engine.config = {"test_key": "test_value"}
        self.mock_engine.mt5_client = Mock()
        self.mock_engine.risk_manager = Mock()
        self.mock_engine.telegram_bot = Mock()
        self.mock_engine.trading_enabled = True
        self.mock_engine.get_open_trades = Mock(return_value=[])
    
    def test_service_api_initialization(self):
        """Test ServiceAPI initializes with trading engine"""
        api = ServiceAPI(self.mock_engine)
        
        assert api._engine == self.mock_engine
        assert api._config == self.mock_engine.config
    
    def test_get_price(self):
        """Test get_price returns bid price"""
        self.mock_engine.mt5_client.get_symbol_tick.return_value = {"bid": 1950.50}
        api = ServiceAPI(self.mock_engine)
        
        price = api.get_price("XAUUSD")
        
        assert price == 1950.50
        self.mock_engine.mt5_client.get_symbol_tick.assert_called_with("XAUUSD")
    
    def test_get_price_no_tick(self):
        """Test get_price returns 0 when no tick data"""
        self.mock_engine.mt5_client.get_symbol_tick.return_value = None
        api = ServiceAPI(self.mock_engine)
        
        price = api.get_price("XAUUSD")
        
        assert price == 0.0
    
    def test_get_balance(self):
        """Test get_balance returns account balance"""
        self.mock_engine.mt5_client.get_account_balance.return_value = 10000.0
        api = ServiceAPI(self.mock_engine)
        
        balance = api.get_balance()
        
        assert balance == 10000.0
    
    def test_get_equity(self):
        """Test get_equity returns account equity"""
        self.mock_engine.mt5_client.get_account_equity.return_value = 10500.0
        api = ServiceAPI(self.mock_engine)
        
        equity = api.get_equity()
        
        assert equity == 10500.0
    
    def test_place_order_when_trading_enabled(self):
        """Test place_order works when trading is enabled"""
        self.mock_engine.mt5_client.place_order.return_value = 12345
        api = ServiceAPI(self.mock_engine)
        
        ticket = api.place_order("XAUUSD", "BUY", 0.1, sl_price=1940.0, tp_price=1960.0)
        
        assert ticket == 12345
        self.mock_engine.mt5_client.place_order.assert_called_once()
    
    def test_place_order_when_trading_disabled(self):
        """Test place_order rejected when trading is paused"""
        self.mock_engine.trading_enabled = False
        api = ServiceAPI(self.mock_engine)
        
        ticket = api.place_order("XAUUSD", "BUY", 0.1)
        
        assert ticket is None
    
    def test_close_trade(self):
        """Test close_trade calls MT5 client"""
        self.mock_engine.mt5_client.close_position.return_value = True
        api = ServiceAPI(self.mock_engine)
        
        result = api.close_trade(12345)
        
        assert result == True
        self.mock_engine.mt5_client.close_position.assert_called_with(12345)
    
    def test_modify_order(self):
        """Test modify_order calls MT5 client"""
        self.mock_engine.mt5_client.modify_position.return_value = True
        api = ServiceAPI(self.mock_engine)
        
        result = api.modify_order(12345, sl=1940.0, tp=1960.0)
        
        assert result == True
        self.mock_engine.mt5_client.modify_position.assert_called_with(12345, 1940.0, 1960.0)
    
    def test_get_open_trades(self):
        """Test get_open_trades returns engine's open trades"""
        mock_trades = [Mock(), Mock()]
        self.mock_engine.get_open_trades.return_value = mock_trades
        api = ServiceAPI(self.mock_engine)
        
        trades = api.get_open_trades()
        
        assert trades == mock_trades
    
    def test_calculate_lot_size(self):
        """Test calculate_lot_size uses risk manager"""
        self.mock_engine.mt5_client.get_account_balance.return_value = 10000.0
        self.mock_engine.risk_manager.get_fixed_lot_size.return_value = 0.1
        api = ServiceAPI(self.mock_engine)
        
        lot_size = api.calculate_lot_size("XAUUSD")
        
        assert lot_size == 0.1
    
    def test_send_notification(self):
        """Test send_notification calls telegram bot"""
        api = ServiceAPI(self.mock_engine)
        
        api.send_notification("Test message")
        
        self.mock_engine.telegram_bot.send_message.assert_called_with("Test message")
    
    def test_get_config(self):
        """Test get_config returns config value"""
        api = ServiceAPI(self.mock_engine)
        
        value = api.get_config("test_key")
        
        assert value == "test_value"
    
    def test_get_config_default(self):
        """Test get_config returns default for missing key"""
        api = ServiceAPI(self.mock_engine)
        
        value = api.get_config("nonexistent", default="default_value")
        
        assert value == "default_value"


class TestPluginSystemIntegration:
    """Integration tests for the plugin system"""
    
    @pytest.mark.asyncio
    async def test_full_plugin_lifecycle(self):
        """Test complete plugin lifecycle: load, route, disable, enable"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {"test": {"enabled": True}}
        }
        registry = PluginRegistry(config, None)
        
        plugin = DummyPlugin("test", {"enabled": True}, None)
        registry.plugins["test"] = plugin
        
        assert registry.get_plugin("test") is not None
        assert registry.get_plugin("test").enabled == True
        
        alert = MockAlert("XAUUSD", "entry")
        result = await registry.route_alert_to_plugin(alert, "test")
        assert result.get("success") == True
        
        plugin.disable()
        result = await registry.route_alert_to_plugin(alert, "test")
        assert result.get("skipped") == True
        
        plugin.enable()
        result = await registry.route_alert_to_plugin(alert, "test")
        assert result.get("success") == True
    
    @pytest.mark.asyncio
    async def test_multiple_plugins(self):
        """Test registry handles multiple plugins"""
        config = {
            "plugin_system": {"plugin_dir": "src/logic_plugins"},
            "plugins": {
                "plugin_a": {"enabled": True},
                "plugin_b": {"enabled": True}
            }
        }
        registry = PluginRegistry(config, None)
        
        plugin_a = DummyPlugin("plugin_a", {"enabled": True}, None)
        plugin_b = DummyPlugin("plugin_b", {"enabled": True}, None)
        registry.plugins["plugin_a"] = plugin_a
        registry.plugins["plugin_b"] = plugin_b
        
        assert len(registry.get_all_plugins()) == 2
        
        alert = MockAlert("XAUUSD", "entry")
        
        result_a = await registry.route_alert_to_plugin(alert, "plugin_a")
        assert result_a.get("plugin_id") == "plugin_a"
        
        result_b = await registry.route_alert_to_plugin(alert, "plugin_b")
        assert result_b.get("plugin_id") == "plugin_b"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
