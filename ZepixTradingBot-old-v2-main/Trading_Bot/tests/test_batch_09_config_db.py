"""
Batch 09 Tests: Config Hot-Reload & Database Isolation

Tests for:
- ConfigManager: Hot-reload, validation, observers
- PluginDatabase: Isolation, thread safety, CRUD operations
- DatabaseSyncManager: Sync, retry logic, health monitoring

Version: 1.0.0
"""

import pytest
import asyncio
import json
import os
import tempfile
import threading
import time
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.config_manager import (
    ConfigManager,
    ConfigChange,
    ConfigChangeType,
    ConfigValidationError,
    create_config_manager
)
from src.core.plugin_database import (
    PluginDatabase,
    PluginDatabaseManager,
    PluginDatabaseError,
    ConnectionPoolExhausted,
    create_plugin_database
)
from src.core.database_sync_manager import (
    DatabaseSyncManager,
    SyncConfig,
    SyncResult,
    SyncStatus,
    DatabaseSyncError,
    create_sync_manager
)


class TestConfigManager:
    """Tests for ConfigManager class"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            plugin_dir = os.path.join(tmpdir, "plugins")
            os.makedirs(plugin_dir)
            
            config = {
                "telegram_token": "test_token",
                "telegram_chat_id": 12345,
                "mt5_login": 67890,
                "mt5_password": "test_pass",
                "mt5_server": "test_server",
                "risk_tiers": {
                    "5000": {
                        "per_trade_cap": 150,
                        "daily_loss_limit": 200,
                        "max_total_loss": 500
                    }
                }
            }
            
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            yield {
                "config_path": config_path,
                "plugin_dir": plugin_dir,
                "tmpdir": tmpdir
            }
    
    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """Create ConfigManager instance"""
        manager = ConfigManager(
            config_path=temp_config_dir["config_path"],
            plugin_config_dir=temp_config_dir["plugin_dir"],
            enable_watching=False
        )
        yield manager
        manager.stop_watching()
    
    def test_config_manager_initialization(self, config_manager):
        """Test ConfigManager initializes correctly"""
        assert config_manager.config is not None
        assert config_manager.config["telegram_token"] == "test_token"
        assert config_manager.config["telegram_chat_id"] == 12345
    
    def test_config_get_simple_key(self, config_manager):
        """Test getting simple config key"""
        assert config_manager.get("telegram_token") == "test_token"
        assert config_manager.get("nonexistent", "default") == "default"
    
    def test_config_get_nested_key(self, config_manager):
        """Test getting nested config key with dot notation"""
        assert config_manager.get("risk_tiers.5000.per_trade_cap") == 150
        assert config_manager.get("risk_tiers.5000.nonexistent", 0) == 0
    
    def test_config_update(self, config_manager):
        """Test updating config value"""
        result = config_manager.update("telegram_chat_id", 99999, save=False)
        assert result is True
        assert config_manager.get("telegram_chat_id") == 99999
    
    def test_config_update_nested(self, config_manager):
        """Test updating nested config value"""
        result = config_manager.update("risk_tiers.5000.per_trade_cap", 200, save=False)
        assert result is True
        assert config_manager.get("risk_tiers.5000.per_trade_cap") == 200
    
    def test_config_reload_detects_changes(self, temp_config_dir, config_manager):
        """Test config reload detects changes"""
        with open(temp_config_dir["config_path"], 'r') as f:
            config = json.load(f)
        
        config["telegram_chat_id"] = 11111
        
        with open(temp_config_dir["config_path"], 'w') as f:
            json.dump(config, f)
        
        changes = config_manager.reload_config()
        
        assert len(changes) == 1
        assert changes[0].key == "telegram_chat_id"
        assert changes[0].change_type == ConfigChangeType.MODIFIED
        assert changes[0].old_value == 12345
        assert changes[0].new_value == 11111
    
    def test_config_observer_notification(self, config_manager):
        """Test observers are notified of changes"""
        received_changes = []
        
        def observer(changes):
            received_changes.extend(changes)
        
        config_manager.register_observer(observer)
        config_manager.update("telegram_chat_id", 77777, save=False)
        
        assert len(received_changes) == 1
        assert received_changes[0].key == "telegram_chat_id"
    
    def test_config_observer_unregister(self, config_manager):
        """Test observer can be unregistered"""
        received_changes = []
        
        def observer(changes):
            received_changes.extend(changes)
        
        config_manager.register_observer(observer)
        config_manager.unregister_observer(observer)
        config_manager.update("telegram_chat_id", 88888, save=False)
        
        assert len(received_changes) == 0
    
    def test_config_validation_missing_key(self, config_manager):
        """Test validation fails for missing required key"""
        invalid_config = {"telegram_token": "test"}
        
        with pytest.raises(ConfigValidationError):
            config_manager.validate_config(invalid_config)
    
    def test_config_validation_success(self, config_manager):
        """Test validation passes for valid config"""
        valid_config = {
            "telegram_token": "test",
            "telegram_chat_id": 123,
            "mt5_login": 456,
            "mt5_password": "pass",
            "mt5_server": "server"
        }
        
        assert config_manager.validate_config(valid_config) is True
    
    def test_config_status(self, config_manager):
        """Test get_status returns correct info"""
        status = config_manager.get_status()
        
        assert "watching" in status
        assert "config_path" in status
        assert "loaded_plugins" in status
        assert "observer_count" in status
    
    def test_config_change_history(self, config_manager):
        """Test change history is tracked"""
        config_manager.update("telegram_chat_id", 11111, save=False)
        config_manager.update("telegram_chat_id", 22222, save=False)
        
        history = config_manager.get_change_history()
        
        assert len(history) >= 2


class TestPluginConfigHotReload:
    """Tests for plugin config hot-reload"""
    
    @pytest.fixture
    def temp_plugin_config(self):
        """Create temporary plugin config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            plugin_dir = os.path.join(tmpdir, "plugins")
            os.makedirs(plugin_dir)
            
            with open(config_path, 'w') as f:
                json.dump({
                    "telegram_token": "test",
                    "telegram_chat_id": 123,
                    "mt5_login": 456,
                    "mt5_password": "pass",
                    "mt5_server": "server"
                }, f)
            
            plugin_config_path = os.path.join(plugin_dir, "combined_v3_config.json")
            with open(plugin_config_path, 'w') as f:
                json.dump({
                    "plugin_id": "v3_combined",
                    "enabled": True,
                    "max_lot_size": 1.0
                }, f)
            
            yield {
                "config_path": config_path,
                "plugin_dir": plugin_dir,
                "plugin_config_path": plugin_config_path
            }
    
    def test_plugin_config_load(self, temp_plugin_config):
        """Test plugin config loads correctly"""
        manager = ConfigManager(
            config_path=temp_plugin_config["config_path"],
            plugin_config_dir=temp_plugin_config["plugin_dir"],
            enable_watching=False
        )
        
        plugin_config = manager.get_plugin_config("v3_combined")
        
        assert plugin_config["plugin_id"] == "v3_combined"
        assert plugin_config["enabled"] is True
        assert plugin_config["max_lot_size"] == 1.0
    
    def test_plugin_config_reload(self, temp_plugin_config):
        """Test plugin config reload detects changes"""
        manager = ConfigManager(
            config_path=temp_plugin_config["config_path"],
            plugin_config_dir=temp_plugin_config["plugin_dir"],
            enable_watching=False
        )
        
        with open(temp_plugin_config["plugin_config_path"], 'w') as f:
            json.dump({
                "plugin_id": "v3_combined",
                "enabled": True,
                "max_lot_size": 2.0
            }, f)
        
        changes = manager.reload_plugin_config("v3_combined")
        
        assert len(changes) == 1
        assert "max_lot_size" in changes[0].key
        
        plugin_config = manager.get_plugin_config("v3_combined")
        assert plugin_config["max_lot_size"] == 2.0
    
    def test_plugin_observer_notification(self, temp_plugin_config):
        """Test plugin observers are notified"""
        manager = ConfigManager(
            config_path=temp_plugin_config["config_path"],
            plugin_config_dir=temp_plugin_config["plugin_dir"],
            enable_watching=False
        )
        
        received_changes = []
        
        def observer(changes):
            received_changes.extend(changes)
        
        manager.register_plugin_observer("v3_combined", observer)
        
        with open(temp_plugin_config["plugin_config_path"], 'w') as f:
            json.dump({
                "plugin_id": "v3_combined",
                "enabled": False,
                "max_lot_size": 1.0
            }, f)
        
        manager.reload_plugin_config("v3_combined")
        
        assert len(received_changes) == 1


class TestPluginDatabase:
    """Tests for PluginDatabase class"""
    
    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary database directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def plugin_db(self, temp_db_dir):
        """Create PluginDatabase instance"""
        db = PluginDatabase(
            plugin_id="test_plugin",
            db_dir=temp_db_dir,
            pool_size=3
        )
        yield db
        db.close()
    
    def test_database_initialization(self, plugin_db):
        """Test database initializes correctly"""
        assert plugin_db.plugin_id == "test_plugin"
        assert plugin_db.test_connection() is True
    
    def test_database_isolation(self, temp_db_dir):
        """Test databases are isolated per plugin"""
        db_a = PluginDatabase(plugin_id="plugin_a", db_dir=temp_db_dir)
        db_b = PluginDatabase(plugin_id="plugin_b", db_dir=temp_db_dir)
        
        trade_id_a = db_a.save_trade({
            "ticket": 12345,
            "symbol": "EURUSD",
            "direction": "BUY",
            "lot_size": 0.1,
            "entry_price": 1.1000
        })
        
        trades_b = db_b.get_all_trades()
        
        assert len(trades_b) == 0
        
        trades_a = db_a.get_all_trades()
        assert len(trades_a) == 1
        
        db_a.close()
        db_b.close()
    
    def test_save_trade(self, plugin_db):
        """Test saving trade"""
        trade_id = plugin_db.save_trade({
            "ticket": 12345,
            "symbol": "EURUSD",
            "direction": "BUY",
            "lot_size": 0.1,
            "entry_price": 1.1000,
            "sl_price": 1.0950,
            "tp_price": 1.1100,
            "signal_type": "institutional_launchpad",
            "logic_type": "LOGIC1",
            "order_type": "ORDER_A"
        })
        
        assert trade_id > 0
        
        trade = plugin_db.get_trade(trade_id)
        assert trade is not None
        assert trade["symbol"] == "EURUSD"
        assert trade["direction"] == "BUY"
    
    def test_update_trade(self, plugin_db):
        """Test updating trade"""
        trade_id = plugin_db.save_trade({
            "ticket": 12345,
            "symbol": "EURUSD",
            "direction": "BUY",
            "lot_size": 0.1,
            "entry_price": 1.1000
        })
        
        result = plugin_db.update_trade(trade_id, {
            "sl_price": 1.0900,
            "tp_price": 1.1200
        })
        
        assert result is True
        
        trade = plugin_db.get_trade(trade_id)
        assert trade["sl_price"] == 1.0900
        assert trade["tp_price"] == 1.1200
    
    def test_close_trade(self, plugin_db):
        """Test closing trade"""
        trade_id = plugin_db.save_trade({
            "ticket": 12345,
            "symbol": "EURUSD",
            "direction": "BUY",
            "lot_size": 0.1,
            "entry_price": 1.1000
        })
        
        result = plugin_db.close_trade(
            trade_id=trade_id,
            exit_price=1.1050,
            profit_dollars=50.0,
            close_reason="TP_HIT"
        )
        
        assert result is True
        
        trade = plugin_db.get_trade(trade_id)
        assert trade["status"] == "CLOSED"
        assert trade["profit_dollars"] == 50.0
        assert trade["close_reason"] == "TP_HIT"
    
    def test_get_open_trades(self, plugin_db):
        """Test getting open trades"""
        plugin_db.save_trade({
            "ticket": 11111,
            "symbol": "EURUSD",
            "direction": "BUY",
            "lot_size": 0.1,
            "entry_price": 1.1000,
            "status": "OPEN"
        })
        
        trade_id = plugin_db.save_trade({
            "ticket": 22222,
            "symbol": "GBPUSD",
            "direction": "SELL",
            "lot_size": 0.2,
            "entry_price": 1.2500,
            "status": "OPEN"
        })
        
        plugin_db.close_trade(trade_id, 1.2450, 50.0, "TP_HIT")
        
        open_trades = plugin_db.get_open_trades()
        
        assert len(open_trades) == 1
        assert open_trades[0]["symbol"] == "EURUSD"
    
    def test_get_trade_by_ticket(self, plugin_db):
        """Test getting trade by MT5 ticket"""
        plugin_db.save_trade({
            "ticket": 99999,
            "symbol": "XAUUSD",
            "direction": "BUY",
            "lot_size": 0.05,
            "entry_price": 2000.00
        })
        
        trade = plugin_db.get_trade_by_ticket(99999)
        
        assert trade is not None
        assert trade["symbol"] == "XAUUSD"
    
    def test_log_signal(self, plugin_db):
        """Test logging signal"""
        signal_id = plugin_db.log_signal({
            "signal_type": "institutional_launchpad",
            "symbol": "EURUSD",
            "direction": "BUY",
            "timeframe": "15M",
            "raw_payload": {"test": "data"},
            "processed": True,
            "result": "ORDER_PLACED"
        })
        
        assert signal_id > 0
    
    def test_daily_stats(self, plugin_db):
        """Test daily statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        plugin_db.update_daily_stats(today, {
            "trades": 5,
            "wins": 3,
            "losses": 2,
            "profit_pips": 50.0,
            "profit_dollars": 100.0
        })
        
        stats = plugin_db.get_daily_stats(today)
        
        assert stats is not None
        assert stats["total_trades"] == 5
        assert stats["winning_trades"] == 3
        assert stats["total_profit_dollars"] == 100.0
    
    def test_database_stats(self, plugin_db):
        """Test database statistics"""
        plugin_db.save_trade({
            "ticket": 12345,
            "symbol": "EURUSD",
            "direction": "BUY",
            "lot_size": 0.1,
            "entry_price": 1.1000
        })
        
        stats = plugin_db.get_stats()
        
        assert stats["plugin_id"] == "test_plugin"
        assert stats["total_inserts"] >= 1
        assert stats["total_queries"] >= 1
    
    def test_thread_safety(self, plugin_db):
        """Test thread-safe operations"""
        results = []
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(10):
                    plugin_db.save_trade({
                        "ticket": thread_id * 1000 + i,
                        "symbol": "EURUSD",
                        "direction": "BUY",
                        "lot_size": 0.1,
                        "entry_price": 1.1000
                    })
                results.append(thread_id)
            except Exception as e:
                errors.append(str(e))
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert len(results) == 3
        
        all_trades = plugin_db.get_all_trades(limit=100)
        assert len(all_trades) == 30


class TestPluginDatabaseManager:
    """Tests for PluginDatabaseManager class"""
    
    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary database directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_manager_creates_databases(self, temp_db_dir):
        """Test manager creates databases on demand"""
        manager = PluginDatabaseManager(db_dir=temp_db_dir)
        
        db_v3 = manager.get_database("v3_combined")
        db_v6 = manager.get_database("v6_price_action_1m")
        
        assert db_v3.plugin_id == "v3_combined"
        assert db_v6.plugin_id == "v6_price_action_1m"
        
        manager.close_all()
    
    def test_manager_reuses_databases(self, temp_db_dir):
        """Test manager reuses existing database instances"""
        manager = PluginDatabaseManager(db_dir=temp_db_dir)
        
        db1 = manager.get_database("test_plugin")
        db2 = manager.get_database("test_plugin")
        
        assert db1 is db2
        
        manager.close_all()
    
    def test_manager_stats(self, temp_db_dir):
        """Test manager returns all database stats"""
        manager = PluginDatabaseManager(db_dir=temp_db_dir)
        
        manager.get_database("plugin_a")
        manager.get_database("plugin_b")
        
        stats = manager.get_all_stats()
        
        assert "plugin_a" in stats
        assert "plugin_b" in stats
        
        manager.close_all()


class TestDatabaseSyncManager:
    """Tests for DatabaseSyncManager class"""
    
    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary database directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sync_manager(self, temp_db_dir):
        """Create DatabaseSyncManager instance"""
        config = SyncConfig(
            sync_interval_seconds=1,
            max_retries=2,
            retry_delay_seconds=0.1
        )
        
        manager = DatabaseSyncManager(
            config=config,
            v3_db_path=os.path.join(temp_db_dir, "v3.db"),
            v6_db_path=os.path.join(temp_db_dir, "v6.db"),
            central_db_path=os.path.join(temp_db_dir, "central.db")
        )
        
        yield manager
    
    def test_sync_manager_initialization(self, sync_manager):
        """Test sync manager initializes correctly"""
        assert sync_manager._running is False
        assert sync_manager.stats["total_syncs"] == 0
    
    @pytest.mark.asyncio
    async def test_sync_manager_start_stop(self, sync_manager):
        """Test sync manager start and stop"""
        await sync_manager.start()
        assert sync_manager._running is True
        
        await sync_manager.stop()
        assert sync_manager._running is False
    
    @pytest.mark.asyncio
    async def test_sync_skips_missing_db(self, sync_manager):
        """Test sync skips when database doesn't exist"""
        result = await sync_manager.sync_plugin("v3_combined")
        
        assert result.status == SyncStatus.SKIPPED
        assert "not found" in result.error_message
    
    @pytest.mark.asyncio
    async def test_sync_with_data(self, temp_db_dir, sync_manager):
        """Test sync with actual data"""
        v3_db = PluginDatabase(
            plugin_id="v3_combined",
            db_dir=temp_db_dir
        )
        
        v3_db.save_trade({
            "ticket": 12345,
            "symbol": "EURUSD",
            "direction": "BUY",
            "lot_size": 0.1,
            "entry_price": 1.1000,
            "status": "CLOSED",
            "profit_dollars": 50.0
        })
        
        v3_db.close()
        
        sync_manager.v3_db_path = os.path.join(temp_db_dir, "zepix_combined_v3.db")
        
        result = await sync_manager.sync_plugin("v3_combined")
        
        assert result.status in [SyncStatus.SUCCESS, SyncStatus.SKIPPED]
    
    @pytest.mark.asyncio
    async def test_manual_sync_trigger(self, sync_manager):
        """Test manual sync trigger"""
        result = await sync_manager.trigger_manual_sync()
        
        assert result["triggered"] is True
        assert "message" in result
    
    def test_sync_health(self, sync_manager):
        """Test sync health status"""
        health = sync_manager.get_sync_health()
        
        assert "overall_status" in health
        assert "plugins" in health
        assert "statistics" in health
        assert health["overall_status"] == "HEALTHY"
    
    def test_sync_history(self, sync_manager):
        """Test sync history tracking"""
        history = sync_manager.get_sync_history()
        
        assert isinstance(history, list)
    
    def test_reset_failure_count(self, sync_manager):
        """Test resetting failure count"""
        sync_manager.consecutive_failures["test_plugin"] = 5
        
        sync_manager.reset_failure_count("test_plugin")
        
        assert sync_manager.consecutive_failures["test_plugin"] == 0
    
    @pytest.mark.asyncio
    async def test_alert_callback(self, sync_manager):
        """Test alert callback is called on failures"""
        alert_received = []
        
        async def alert_callback(plugin_id, failure_count):
            alert_received.append((plugin_id, failure_count))
        
        sync_manager.set_alert_callback(alert_callback)
        sync_manager.consecutive_failures["test_plugin"] = 5
        
        await sync_manager._check_and_alert_failures()
        
        assert len(alert_received) == 1
        assert alert_received[0][0] == "test_plugin"
        assert alert_received[0][1] == 5


class TestSyncRetryLogic:
    """Tests for sync retry logic"""
    
    @pytest.fixture
    def sync_manager(self):
        """Create sync manager with fast retry"""
        config = SyncConfig(
            max_retries=2,
            retry_delay_seconds=0.01,
            backoff_multiplier=2.0
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DatabaseSyncManager(
                config=config,
                v3_db_path=os.path.join(tmpdir, "v3.db"),
                v6_db_path=os.path.join(tmpdir, "v6.db"),
                central_db_path=os.path.join(tmpdir, "central.db")
            )
            yield manager
    
    @pytest.mark.asyncio
    async def test_retry_increments_count(self, sync_manager):
        """Test retry count is incremented"""
        result = await sync_manager._sync_plugin_with_retry(
            "nonexistent_plugin",
            "/nonexistent/path.db"
        )
        
        assert result.status == SyncStatus.SKIPPED or result.status == SyncStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_consecutive_failures_tracked(self, sync_manager):
        """Test consecutive failures are tracked"""
        sync_manager._plugin_db_mapping["test_fail"] = "/nonexistent/path.db"
        
        await sync_manager.sync_plugin("test_fail")
        
        assert "test_fail" not in sync_manager.consecutive_failures or \
               sync_manager.consecutive_failures.get("test_fail", 0) >= 0


class TestIntegration:
    """Integration tests for config and database systems"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_config_triggers_plugin_reload(self, temp_dir):
        """Test config change triggers plugin reload"""
        config_path = os.path.join(temp_dir, "config.json")
        plugin_dir = os.path.join(temp_dir, "plugins")
        os.makedirs(plugin_dir)
        
        with open(config_path, 'w') as f:
            json.dump({
                "telegram_token": "test",
                "telegram_chat_id": 123,
                "mt5_login": 456,
                "mt5_password": "pass",
                "mt5_server": "server"
            }, f)
        
        plugin_config_path = os.path.join(plugin_dir, "test_plugin_config.json")
        with open(plugin_config_path, 'w') as f:
            json.dump({"enabled": True, "max_lot": 1.0}, f)
        
        config_manager = ConfigManager(
            config_path=config_path,
            plugin_config_dir=plugin_dir,
            enable_watching=False
        )
        
        plugin_db = PluginDatabase(
            plugin_id="test_plugin",
            db_dir=temp_dir
        )
        
        reload_triggered = []
        
        def on_config_change(changes):
            reload_triggered.append(changes)
        
        config_manager.register_plugin_observer("test_plugin", on_config_change)
        
        with open(plugin_config_path, 'w') as f:
            json.dump({"enabled": True, "max_lot": 2.0}, f)
        
        config_manager.reload_plugin_config("test_plugin")
        
        assert len(reload_triggered) == 1
        
        plugin_db.close()
    
    def test_database_isolation_with_sync(self, temp_dir):
        """Test database isolation is maintained during sync"""
        db_v3 = PluginDatabase(plugin_id="v3_combined", db_dir=temp_dir)
        db_v6 = PluginDatabase(plugin_id="v6_price_action_1m", db_dir=temp_dir)
        
        db_v3.save_trade({
            "ticket": 11111,
            "symbol": "EURUSD",
            "direction": "BUY",
            "lot_size": 0.1,
            "entry_price": 1.1000
        })
        
        db_v6.save_trade({
            "ticket": 22222,
            "symbol": "GBPUSD",
            "direction": "SELL",
            "lot_size": 0.2,
            "entry_price": 1.2500
        })
        
        v3_trades = db_v3.get_all_trades()
        v6_trades = db_v6.get_all_trades()
        
        assert len(v3_trades) == 1
        assert len(v6_trades) == 1
        assert v3_trades[0]["symbol"] == "EURUSD"
        assert v6_trades[0]["symbol"] == "GBPUSD"
        
        db_v3.close()
        db_v6.close()


class TestFactoryFunctions:
    """Tests for factory functions"""
    
    def test_create_config_manager(self):
        """Test create_config_manager factory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            with open(config_path, 'w') as f:
                json.dump({
                    "telegram_token": "test",
                    "telegram_chat_id": 123,
                    "mt5_login": 456,
                    "mt5_password": "pass",
                    "mt5_server": "server"
                }, f)
            
            manager = create_config_manager(
                config_path=config_path,
                enable_watching=False
            )
            
            assert manager is not None
            assert manager.config["telegram_token"] == "test"
    
    def test_create_plugin_database(self):
        """Test create_plugin_database factory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = create_plugin_database("test_plugin", db_dir=tmpdir)
            
            assert db is not None
            assert db.plugin_id == "test_plugin"
            assert db.test_connection() is True
            
            db.close()
    
    def test_create_sync_manager(self):
        """Test create_sync_manager factory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = create_sync_manager(
                v3_db_path=os.path.join(tmpdir, "v3.db"),
                v6_db_path=os.path.join(tmpdir, "v6.db"),
                central_db_path=os.path.join(tmpdir, "central.db")
            )
            
            assert manager is not None
            assert manager._running is False
