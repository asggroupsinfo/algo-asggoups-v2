"""
Unit tests for Batch 02: Multi-Database Schema Design & Configuration Templates

Tests:
- SQL schema files can create databases without errors
- JSON config files are valid and parseable
- Database isolation (V3 and V6 have separate tables)
- Schema completeness (all required tables exist)
"""

import pytest
import sqlite3
import json
import os
import tempfile
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
SCHEMAS_DIR = PROJECT_ROOT / "data" / "schemas"
PLUGINS_CONFIG_DIR = PROJECT_ROOT / "config" / "plugins"


class TestSQLSchemas:
    """Tests for SQL schema files"""
    
    def test_combined_v3_schema_exists(self):
        """Test V3 schema file exists"""
        schema_path = SCHEMAS_DIR / "combined_v3_schema.sql"
        assert schema_path.exists(), f"V3 schema not found at {schema_path}"
    
    def test_price_action_v6_schema_exists(self):
        """Test V6 schema file exists"""
        schema_path = SCHEMAS_DIR / "price_action_v6_schema.sql"
        assert schema_path.exists(), f"V6 schema not found at {schema_path}"
    
    def test_central_system_schema_exists(self):
        """Test Central schema file exists"""
        schema_path = SCHEMAS_DIR / "central_system_schema.sql"
        assert schema_path.exists(), f"Central schema not found at {schema_path}"
    
    def test_combined_v3_schema_creates_database(self):
        """Test V3 schema can create a database without errors"""
        schema_path = SCHEMAS_DIR / "combined_v3_schema.sql"
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            conn = sqlite3.connect(tmp_path)
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()
            
            # Verify tables were created
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'combined_v3_trades' in tables
            assert 'v3_profit_bookings' in tables
            assert 'v3_signals_log' in tables
            assert 'v3_daily_stats' in tables
            
            conn.close()
        finally:
            os.unlink(tmp_path)
    
    def test_price_action_v6_schema_creates_database(self):
        """Test V6 schema can create a database without errors"""
        schema_path = SCHEMAS_DIR / "price_action_v6_schema.sql"
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            conn = sqlite3.connect(tmp_path)
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()
            
            # Verify tables were created
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'price_action_1m_trades' in tables
            assert 'price_action_5m_trades' in tables
            assert 'price_action_15m_trades' in tables
            assert 'price_action_1h_trades' in tables
            assert 'market_trends' in tables
            assert 'v6_signals_log' in tables
            assert 'v6_daily_stats' in tables
            
            conn.close()
        finally:
            os.unlink(tmp_path)
    
    def test_central_system_schema_creates_database(self):
        """Test Central schema can create a database without errors"""
        schema_path = SCHEMAS_DIR / "central_system_schema.sql"
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            conn = sqlite3.connect(tmp_path)
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()
            
            # Verify tables were created
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'plugins_registry' in tables
            assert 'aggregated_trades' in tables
            assert 'system_config' in tables
            assert 'system_events' in tables
            
            conn.close()
        finally:
            os.unlink(tmp_path)
    
    def test_v3_and_v6_schemas_are_isolated(self):
        """Test V3 and V6 schemas have no shared tables"""
        v3_schema_path = SCHEMAS_DIR / "combined_v3_schema.sql"
        v6_schema_path = SCHEMAS_DIR / "price_action_v6_schema.sql"
        
        # Create V3 database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            v3_db_path = tmp.name
        
        # Create V6 database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            v6_db_path = tmp.name
        
        try:
            # Create V3 DB
            v3_conn = sqlite3.connect(v3_db_path)
            with open(v3_schema_path, 'r') as f:
                v3_conn.executescript(f.read())
            v3_conn.commit()
            
            # Create V6 DB
            v6_conn = sqlite3.connect(v6_db_path)
            with open(v6_schema_path, 'r') as f:
                v6_conn.executescript(f.read())
            v6_conn.commit()
            
            # Get V3 tables (exclude internal SQLite tables)
            v3_cursor = v3_conn.cursor()
            v3_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            v3_tables = set(row[0] for row in v3_cursor.fetchall())
            
            # Get V6 tables (exclude internal SQLite tables)
            v6_cursor = v6_conn.cursor()
            v6_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            v6_tables = set(row[0] for row in v6_cursor.fetchall())
            
            # Check no overlap (application tables only)
            shared_tables = v3_tables.intersection(v6_tables)
            assert len(shared_tables) == 0, f"V3 and V6 share application tables: {shared_tables}"
            
            v3_conn.close()
            v6_conn.close()
        finally:
            os.unlink(v3_db_path)
            os.unlink(v6_db_path)
    
    def test_central_schema_has_plugin_registry_data(self):
        """Test Central schema pre-populates plugin registry"""
        schema_path = SCHEMAS_DIR / "central_system_schema.sql"
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            conn = sqlite3.connect(tmp_path)
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
            conn.commit()
            
            cursor = conn.cursor()
            cursor.execute("SELECT plugin_id FROM plugins_registry")
            plugins = [row[0] for row in cursor.fetchall()]
            
            assert 'v3_combined' in plugins
            assert 'v6_price_action_1m' in plugins
            assert 'v6_price_action_5m' in plugins
            assert 'v6_price_action_15m' in plugins
            assert 'v6_price_action_1h' in plugins
            
            conn.close()
        finally:
            os.unlink(tmp_path)


class TestJSONConfigs:
    """Tests for JSON configuration files"""
    
    def test_combined_v3_config_exists(self):
        """Test V3 config file exists"""
        config_path = PLUGINS_CONFIG_DIR / "combined_v3_config.json"
        assert config_path.exists(), f"V3 config not found at {config_path}"
    
    def test_price_action_1m_config_exists(self):
        """Test 1M config file exists"""
        config_path = PLUGINS_CONFIG_DIR / "price_action_1m_config.json"
        assert config_path.exists(), f"1M config not found at {config_path}"
    
    def test_price_action_5m_config_exists(self):
        """Test 5M config file exists"""
        config_path = PLUGINS_CONFIG_DIR / "price_action_5m_config.json"
        assert config_path.exists(), f"5M config not found at {config_path}"
    
    def test_price_action_15m_config_exists(self):
        """Test 15M config file exists"""
        config_path = PLUGINS_CONFIG_DIR / "price_action_15m_config.json"
        assert config_path.exists(), f"15M config not found at {config_path}"
    
    def test_price_action_1h_config_exists(self):
        """Test 1H config file exists"""
        config_path = PLUGINS_CONFIG_DIR / "price_action_1h_config.json"
        assert config_path.exists(), f"1H config not found at {config_path}"
    
    def test_combined_v3_config_is_valid_json(self):
        """Test V3 config is valid JSON"""
        config_path = PLUGINS_CONFIG_DIR / "combined_v3_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert config['plugin_id'] == 'v3_combined'
        assert config['metadata']['category'] == 'V3_COMBINED'
        assert 'settings' in config
        assert 'database' in config
    
    def test_price_action_1m_config_is_valid_json(self):
        """Test 1M config is valid JSON"""
        config_path = PLUGINS_CONFIG_DIR / "price_action_1m_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert config['plugin_id'] == 'v6_price_action_1m'
        assert config['metadata']['category'] == 'V6_PRICE_ACTION'
        assert config['settings']['order_routing'] == 'ORDER_B_ONLY'
    
    def test_price_action_5m_config_is_valid_json(self):
        """Test 5M config is valid JSON"""
        config_path = PLUGINS_CONFIG_DIR / "price_action_5m_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert config['plugin_id'] == 'v6_price_action_5m'
        assert config['settings']['order_routing'] == 'DUAL_ORDERS'
    
    def test_price_action_15m_config_is_valid_json(self):
        """Test 15M config is valid JSON"""
        config_path = PLUGINS_CONFIG_DIR / "price_action_15m_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert config['plugin_id'] == 'v6_price_action_15m'
        assert config['settings']['order_routing'] == 'ORDER_A_ONLY'
    
    def test_price_action_1h_config_is_valid_json(self):
        """Test 1H config is valid JSON"""
        config_path = PLUGINS_CONFIG_DIR / "price_action_1h_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert config['plugin_id'] == 'v6_price_action_1h'
        assert config['settings']['order_routing'] == 'ORDER_A_ONLY'
    
    def test_all_configs_have_required_fields(self):
        """Test all configs have required fields"""
        required_fields = ['plugin_id', 'version', 'enabled', 'metadata', 'settings', 'database']
        
        config_files = [
            'combined_v3_config.json',
            'price_action_1m_config.json',
            'price_action_5m_config.json',
            'price_action_15m_config.json',
            'price_action_1h_config.json'
        ]
        
        for config_file in config_files:
            config_path = PLUGINS_CONFIG_DIR / config_file
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            for field in required_fields:
                assert field in config, f"Missing field '{field}' in {config_file}"
    
    def test_v3_config_has_dual_order_settings(self):
        """Test V3 config has dual order system settings"""
        config_path = PLUGINS_CONFIG_DIR / "combined_v3_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert 'dual_order_system' in config['settings']
        assert config['settings']['dual_order_system']['enabled'] == True
        assert 'order_a_settings' in config['settings']['dual_order_system']
        assert 'order_b_settings' in config['settings']['dual_order_system']
    
    def test_v3_config_has_mtf_4_pillar_settings(self):
        """Test V3 config has MTF 4-pillar system settings"""
        config_path = PLUGINS_CONFIG_DIR / "combined_v3_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert 'mtf_4_pillar_system' in config['settings']
        assert config['settings']['mtf_4_pillar_system']['enabled'] == True
        assert config['settings']['mtf_4_pillar_system']['pillars'] == ['15m', '1h', '4h', '1d']
    
    def test_v6_configs_have_trend_pulse_settings(self):
        """Test V6 configs have trend pulse integration settings"""
        v6_configs = [
            'price_action_1m_config.json',
            'price_action_5m_config.json',
            'price_action_15m_config.json',
            'price_action_1h_config.json'
        ]
        
        for config_file in v6_configs:
            config_path = PLUGINS_CONFIG_DIR / config_file
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            assert 'trend_pulse_integration' in config['settings'], f"Missing trend_pulse_integration in {config_file}"


class TestDatabaseIsolation:
    """Tests for database isolation between V3 and V6"""
    
    def test_v3_database_path_is_unique(self):
        """Test V3 config points to unique database"""
        config_path = PLUGINS_CONFIG_DIR / "combined_v3_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert config['database']['path'] == 'data/zepix_combined.db'
    
    def test_v6_databases_share_same_path(self):
        """Test all V6 configs point to same database"""
        v6_configs = [
            'price_action_1m_config.json',
            'price_action_5m_config.json',
            'price_action_15m_config.json',
            'price_action_1h_config.json'
        ]
        
        db_paths = set()
        for config_file in v6_configs:
            config_path = PLUGINS_CONFIG_DIR / config_file
            with open(config_path, 'r') as f:
                config = json.load(f)
            db_paths.add(config['database']['path'])
        
        assert len(db_paths) == 1
        assert 'data/zepix_price_action.db' in db_paths
    
    def test_v3_and_v6_use_different_databases(self):
        """Test V3 and V6 use different database files"""
        v3_config_path = PLUGINS_CONFIG_DIR / "combined_v3_config.json"
        v6_config_path = PLUGINS_CONFIG_DIR / "price_action_1m_config.json"
        
        with open(v3_config_path, 'r') as f:
            v3_config = json.load(f)
        
        with open(v6_config_path, 'r') as f:
            v6_config = json.load(f)
        
        assert v3_config['database']['path'] != v6_config['database']['path']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
