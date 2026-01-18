#!/usr/bin/env python3
"""
V5 Database Creation Tests

Tests for verifying the 3-database V5 architecture:
1. zepix_combined_v3.db - V3 Combined Logic database
2. zepix_price_action.db - V6 Price Action database
3. zepix_bot.db - Central System database

Version: 1.0.0
Date: 2026-01-18
"""

import os
import sys
import sqlite3
import pytest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_trading_bot_path() -> Path:
    """Get the Trading_Bot directory path"""
    return Path(__file__).parent.parent


class TestV5DatabaseExistence:
    """Test that all 3 V5 databases exist"""
    
    def test_v3_database_exists(self):
        """Test that V3 Combined Logic database exists"""
        db_path = get_trading_bot_path() / 'data' / 'zepix_combined_v3.db'
        assert db_path.exists(), f"V3 database not found: {db_path}"
    
    def test_v6_database_exists(self):
        """Test that V6 Price Action database exists"""
        db_path = get_trading_bot_path() / 'data' / 'zepix_price_action.db'
        assert db_path.exists(), f"V6 database not found: {db_path}"
    
    def test_central_database_exists(self):
        """Test that Central System database exists"""
        db_path = get_trading_bot_path() / 'data' / 'zepix_bot.db'
        assert db_path.exists(), f"Central database not found: {db_path}"
    
    def test_legacy_database_preserved(self):
        """Test that legacy trading_bot.db is preserved (not deleted)"""
        db_path = get_trading_bot_path() / 'data' / 'trading_bot.db'
        assert db_path.exists(), f"Legacy database was deleted: {db_path}"


class TestV3DatabaseSchema:
    """Test V3 Combined Logic database schema"""
    
    @pytest.fixture
    def v3_connection(self):
        """Get connection to V3 database"""
        db_path = get_trading_bot_path() / 'data' / 'zepix_combined_v3.db'
        conn = sqlite3.connect(str(db_path))
        yield conn
        conn.close()
    
    def test_v3_tables_exist(self, v3_connection):
        """Test that all V3 tables exist"""
        cursor = v3_connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'combined_v3_trades',
            'v3_daily_stats',
            'v3_profit_bookings',
            'v3_signals_log'
        ]
        
        for table in expected_tables:
            assert table in tables, f"V3 table missing: {table}"
    
    def test_v3_trades_table_columns(self, v3_connection):
        """Test that combined_v3_trades has required columns"""
        cursor = v3_connection.cursor()
        cursor.execute("PRAGMA table_info(combined_v3_trades)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            'id', 'order_a_ticket', 'order_b_ticket', 'symbol', 'direction',
            'entry_price', 'signal_type', 'consensus_score', 'logic_route'
        ]
        
        for col in required_columns:
            assert col in columns, f"V3 trades column missing: {col}"
    
    def test_v3_database_queryable(self, v3_connection):
        """Test that V3 database is queryable"""
        cursor = v3_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM combined_v3_trades")
        count = cursor.fetchone()[0]
        assert count >= 0, "V3 database not queryable"


class TestV6DatabaseSchema:
    """Test V6 Price Action database schema"""
    
    @pytest.fixture
    def v6_connection(self):
        """Get connection to V6 database"""
        db_path = get_trading_bot_path() / 'data' / 'zepix_price_action.db'
        conn = sqlite3.connect(str(db_path))
        yield conn
        conn.close()
    
    def test_v6_tables_exist(self, v6_connection):
        """Test that all V6 tables exist"""
        cursor = v6_connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'price_action_1m_trades',
            'price_action_5m_trades',
            'price_action_15m_trades',
            'price_action_1h_trades',
            'market_trends',
            'v6_signals_log',
            'v6_daily_stats'
        ]
        
        for table in expected_tables:
            assert table in tables, f"V6 table missing: {table}"
    
    def test_v6_1m_trades_columns(self, v6_connection):
        """Test that price_action_1m_trades has required columns"""
        cursor = v6_connection.cursor()
        cursor.execute("PRAGMA table_info(price_action_1m_trades)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            'id', 'order_b_ticket', 'symbol', 'direction', 'lot_size',
            'entry_price', 'adx', 'confidence_score'
        ]
        
        for col in required_columns:
            assert col in columns, f"V6 1m trades column missing: {col}"
    
    def test_v6_5m_trades_columns(self, v6_connection):
        """Test that price_action_5m_trades has dual order columns"""
        cursor = v6_connection.cursor()
        cursor.execute("PRAGMA table_info(price_action_5m_trades)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            'order_a_ticket', 'order_b_ticket',
            'order_a_lot_size', 'order_b_lot_size'
        ]
        
        for col in required_columns:
            assert col in columns, f"V6 5m trades column missing: {col}"
    
    def test_v6_market_trends_table(self, v6_connection):
        """Test that market_trends table has correct structure"""
        cursor = v6_connection.cursor()
        cursor.execute("PRAGMA table_info(market_trends)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['symbol', 'timeframe', 'bull_count', 'bear_count', 'market_state']
        
        for col in required_columns:
            assert col in columns, f"market_trends column missing: {col}"
    
    def test_v6_database_queryable(self, v6_connection):
        """Test that V6 database is queryable"""
        cursor = v6_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM price_action_15m_trades")
        count = cursor.fetchone()[0]
        assert count >= 0, "V6 database not queryable"


class TestCentralDatabaseSchema:
    """Test Central System database schema"""
    
    @pytest.fixture
    def central_connection(self):
        """Get connection to Central database"""
        db_path = get_trading_bot_path() / 'data' / 'zepix_bot.db'
        conn = sqlite3.connect(str(db_path))
        yield conn
        conn.close()
    
    def test_central_tables_exist(self, central_connection):
        """Test that all Central tables exist"""
        cursor = central_connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'plugins_registry',
            'aggregated_trades',
            'system_config',
            'system_events',
            'sync_status'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Central table missing: {table}"
    
    def test_plugins_registry_populated(self, central_connection):
        """Test that plugins_registry has default plugins"""
        cursor = central_connection.cursor()
        cursor.execute("SELECT plugin_id FROM plugins_registry")
        plugins = [row[0] for row in cursor.fetchall()]
        
        expected_plugins = [
            'combined_v3',
            'price_action_1m',
            'price_action_5m',
            'price_action_15m',
            'price_action_1h'
        ]
        
        for plugin in expected_plugins:
            assert plugin in plugins, f"Plugin not registered: {plugin}"
    
    def test_system_config_populated(self, central_connection):
        """Test that system_config has default values"""
        cursor = central_connection.cursor()
        cursor.execute("SELECT key, value FROM system_config")
        config = {row[0]: row[1] for row in cursor.fetchall()}
        
        assert 'bot_version' in config, "bot_version not in system_config"
        assert 'v3_enabled' in config, "v3_enabled not in system_config"
        assert 'v6_enabled' in config, "v6_enabled not in system_config"
    
    def test_central_database_queryable(self, central_connection):
        """Test that Central database is queryable"""
        cursor = central_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM plugins_registry")
        count = cursor.fetchone()[0]
        assert count >= 5, f"Expected at least 5 plugins, got {count}"


class TestDatabaseServiceIntegration:
    """Test DatabaseService can connect to all 3 databases"""
    
    def test_database_service_v3_connection(self):
        """Test DatabaseService can connect to V3 database"""
        try:
            from src.core.services.database_service import DatabaseService
            
            base_path = get_trading_bot_path()
            service = DatabaseService(str(base_path))
            
            db_path = service._get_db_path('v3_combined')
            assert db_path.exists(), f"V3 database path not found: {db_path}"
            
        except ImportError:
            pytest.skip("DatabaseService not available")
    
    def test_database_service_v6_connection(self):
        """Test DatabaseService can connect to V6 databases"""
        try:
            from src.core.services.database_service import DatabaseService
            
            base_path = get_trading_bot_path()
            service = DatabaseService(str(base_path))
            
            for plugin_id in ['v6_price_action_1m', 'v6_price_action_5m', 'v6_price_action_15m', 'v6_price_action_1h']:
                db_path = service._get_db_path(plugin_id)
                assert db_path.exists(), f"V6 database path not found for {plugin_id}: {db_path}"
            
        except ImportError:
            pytest.skip("DatabaseService not available")
    
    def test_database_service_central_connection(self):
        """Test DatabaseService can connect to Central database"""
        try:
            from src.core.services.database_service import DatabaseService
            
            base_path = get_trading_bot_path()
            service = DatabaseService(str(base_path))
            
            db_path = service._get_db_path('central_system')
            assert db_path.exists(), f"Central database path not found: {db_path}"
            
        except ImportError:
            pytest.skip("DatabaseService not available")


class TestDatabaseIsolation:
    """Test that databases are properly isolated"""
    
    def test_no_cross_contamination(self):
        """Test that V3 tables are not in V6 database and vice versa"""
        base_path = get_trading_bot_path()
        
        # Check V3 database doesn't have V6 tables
        v3_conn = sqlite3.connect(str(base_path / 'data' / 'zepix_combined_v3.db'))
        v3_cursor = v3_conn.cursor()
        v3_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        v3_tables = [row[0] for row in v3_cursor.fetchall()]
        v3_conn.close()
        
        v6_specific_tables = ['price_action_1m_trades', 'price_action_5m_trades', 'market_trends']
        for table in v6_specific_tables:
            assert table not in v3_tables, f"V6 table {table} found in V3 database"
        
        # Check V6 database doesn't have V3 tables
        v6_conn = sqlite3.connect(str(base_path / 'data' / 'zepix_price_action.db'))
        v6_cursor = v6_conn.cursor()
        v6_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        v6_tables = [row[0] for row in v6_cursor.fetchall()]
        v6_conn.close()
        
        v3_specific_tables = ['combined_v3_trades', 'v3_profit_bookings', 'v3_signals_log']
        for table in v3_specific_tables:
            assert table not in v6_tables, f"V3 table {table} found in V6 database"
    
    def test_databases_are_separate_files(self):
        """Test that all 3 databases are separate files"""
        base_path = get_trading_bot_path()
        
        v3_path = base_path / 'data' / 'zepix_combined_v3.db'
        v6_path = base_path / 'data' / 'zepix_price_action.db'
        central_path = base_path / 'data' / 'zepix_bot.db'
        
        # All paths should be different
        assert v3_path != v6_path, "V3 and V6 paths are the same"
        assert v3_path != central_path, "V3 and Central paths are the same"
        assert v6_path != central_path, "V6 and Central paths are the same"
        
        # All files should exist
        assert v3_path.exists(), f"V3 database not found: {v3_path}"
        assert v6_path.exists(), f"V6 database not found: {v6_path}"
        assert central_path.exists(), f"Central database not found: {central_path}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
