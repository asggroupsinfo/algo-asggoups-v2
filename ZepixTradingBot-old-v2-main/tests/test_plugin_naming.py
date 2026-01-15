"""
Tests for Plugin Naming Convention - Plan 10

Verifies all plugins follow the new naming convention:
- V3 plugins: v3_{strategy}
- V6 plugins: v6_{strategy}_{timeframe}

Version: 1.0.0
Date: 2026-01-15
"""
import pytest
import re
import json
from pathlib import Path


class TestPluginNaming:
    """Test plugin naming convention"""
    
    VALID_PATTERN = r'^v[36]_[a-z_]+(_\d+[mh])?$'
    
    LEGACY_NAMES = ['combined_v3', 'price_action_1m', 'price_action_5m', 
                   'price_action_15m', 'price_action_1h']
    
    EXPECTED_V3_PLUGINS = ['v3_combined']
    
    EXPECTED_V6_PLUGINS = ['v6_price_action_1m', 'v6_price_action_5m', 
                          'v6_price_action_15m', 'v6_price_action_1h']
    
    @pytest.fixture
    def plugins_path(self):
        return Path('src/logic_plugins')
    
    def test_all_plugins_follow_convention(self, plugins_path):
        """Test all plugin folders follow naming convention"""
        for folder in plugins_path.iterdir():
            if folder.is_dir() and not folder.name.startswith('_'):
                assert re.match(self.VALID_PATTERN, folder.name), \
                    f"Plugin {folder.name} doesn't follow naming convention (expected v3_* or v6_*)"
    
    def test_no_legacy_names_in_folders(self, plugins_path):
        """Test no legacy names exist"""
        for folder in plugins_path.iterdir():
            assert folder.name not in self.LEGACY_NAMES, \
                f"Legacy plugin name still exists: {folder.name}"
    
    def test_plugin_id_matches_folder(self, plugins_path):
        """Test plugin_id in config matches folder name"""
        for folder in plugins_path.iterdir():
            if folder.is_dir() and not folder.name.startswith('_'):
                config_file = folder / 'config.json'
                if config_file.exists():
                    config = json.loads(config_file.read_text())
                    assert config.get('plugin_id') == folder.name, \
                        f"Plugin ID mismatch in {folder.name}: expected {folder.name}, got {config.get('plugin_id')}"
    
    def test_v3_plugins_exist(self, plugins_path):
        """Test V3 plugins exist with correct names"""
        for plugin in self.EXPECTED_V3_PLUGINS:
            plugin_path = plugins_path / plugin
            assert plugin_path.exists(), f"V3 plugin missing: {plugin}"
            assert (plugin_path / 'plugin.py').exists(), f"V3 plugin {plugin} missing plugin.py"
    
    def test_v6_plugins_exist(self, plugins_path):
        """Test V6 plugins exist with correct names"""
        for plugin in self.EXPECTED_V6_PLUGINS:
            plugin_path = plugins_path / plugin
            assert plugin_path.exists(), f"V6 plugin missing: {plugin}"
            assert (plugin_path / 'plugin.py').exists(), f"V6 plugin {plugin} missing plugin.py"
    
    def test_v3_plugin_class_name(self, plugins_path):
        """Test V3 plugin has correct class name"""
        v3_plugin_file = plugins_path / 'v3_combined' / 'plugin.py'
        if v3_plugin_file.exists():
            content = v3_plugin_file.read_text()
            assert 'class V3CombinedPlugin' in content, \
                "V3 plugin class should be named V3CombinedPlugin"
    
    def test_v6_plugin_class_names(self, plugins_path):
        """Test V6 plugins have correct class names"""
        expected_classes = {
            'v6_price_action_1m': 'V6PriceAction1mPlugin',
            'v6_price_action_5m': 'V6PriceAction5mPlugin',
            'v6_price_action_15m': 'V6PriceAction15mPlugin',
            'v6_price_action_1h': 'V6PriceAction1hPlugin',
        }
        
        for plugin_name, expected_class in expected_classes.items():
            plugin_file = plugins_path / plugin_name / 'plugin.py'
            if plugin_file.exists():
                content = plugin_file.read_text()
                assert f'class {expected_class}' in content, \
                    f"Plugin {plugin_name} should have class {expected_class}"


class TestPluginRegistryNaming:
    """Test plugin registry naming support"""
    
    def test_legacy_names_mapping_exists(self):
        """Test legacy names mapping is defined"""
        from src.core.plugin_system.plugin_registry import LEGACY_PLUGIN_NAMES
        
        expected_mappings = {
            'combined_v3': 'v3_combined',
            'price_action_1m': 'v6_price_action_1m',
            'price_action_5m': 'v6_price_action_5m',
            'price_action_15m': 'v6_price_action_15m',
            'price_action_1h': 'v6_price_action_1h',
        }
        
        for old_name, new_name in expected_mappings.items():
            assert old_name in LEGACY_PLUGIN_NAMES, \
                f"Legacy name {old_name} not in LEGACY_PLUGIN_NAMES"
            assert LEGACY_PLUGIN_NAMES[old_name] == new_name, \
                f"Legacy name {old_name} should map to {new_name}"
    
    def test_available_plugins_defined(self):
        """Test AVAILABLE_PLUGINS has all plugins"""
        from src.core.plugin_system.plugin_registry import AVAILABLE_PLUGINS
        
        expected_plugins = [
            'v3_combined',
            'v6_price_action_1m',
            'v6_price_action_5m',
            'v6_price_action_15m',
            'v6_price_action_1h',
        ]
        
        for plugin_id in expected_plugins:
            assert plugin_id in AVAILABLE_PLUGINS, \
                f"Plugin {plugin_id} not in AVAILABLE_PLUGINS"
            assert 'class' in AVAILABLE_PLUGINS[plugin_id], \
                f"Plugin {plugin_id} missing 'class' definition"
            assert 'module' in AVAILABLE_PLUGINS[plugin_id], \
                f"Plugin {plugin_id} missing 'module' definition"


class TestPluginImports:
    """Test plugin imports work with new names"""
    
    def test_v3_combined_import(self):
        """Test V3 combined plugin can be imported"""
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        assert V3CombinedPlugin is not None
    
    def test_v6_price_action_1m_import(self):
        """Test V6 1m plugin can be imported"""
        from src.logic_plugins.v6_price_action_1m.plugin import V6PriceAction1mPlugin
        assert V6PriceAction1mPlugin is not None
    
    def test_v6_price_action_5m_import(self):
        """Test V6 5m plugin can be imported"""
        from src.logic_plugins.v6_price_action_5m.plugin import V6PriceAction5mPlugin
        assert V6PriceAction5mPlugin is not None
    
    def test_v6_price_action_15m_import(self):
        """Test V6 15m plugin can be imported"""
        from src.logic_plugins.v6_price_action_15m.plugin import V6PriceAction15mPlugin
        assert V6PriceAction15mPlugin is not None
    
    def test_v6_price_action_1h_import(self):
        """Test V6 1h plugin can be imported"""
        from src.logic_plugins.v6_price_action_1h.plugin import V6PriceAction1hPlugin
        assert V6PriceAction1hPlugin is not None
    
    def test_v6_init_exports(self):
        """Test V6 __init__.py exports correct class"""
        from src.logic_plugins.v6_price_action_1m import V6PriceAction1mPlugin
        from src.logic_plugins.v6_price_action_5m import V6PriceAction5mPlugin
        from src.logic_plugins.v6_price_action_15m import V6PriceAction15mPlugin
        from src.logic_plugins.v6_price_action_1h import V6PriceAction1hPlugin
        
        assert V6PriceAction1mPlugin is not None
        assert V6PriceAction5mPlugin is not None
        assert V6PriceAction15mPlugin is not None
        assert V6PriceAction1hPlugin is not None
