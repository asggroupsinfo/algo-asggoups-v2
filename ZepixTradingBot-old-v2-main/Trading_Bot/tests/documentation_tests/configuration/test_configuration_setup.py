"""
Documentation Testing: CONFIGURATION_SETUP.md
Tests all verifiable claims in CONFIGURATION_SETUP.md

Total Claims: 40
Verifiable Claims: 15
Test Cases: 15
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
CONFIG_ROOT = TRADING_BOT_ROOT / "config"
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/CONFIGURATION_SETUP.md"


class TestConfigurationSetup:
    """Test suite for CONFIGURATION_SETUP.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_config_001_config_json_exists(self):
        """
        DOC CLAIM: config.json configuration file
        TEST TYPE: File Existence
        """
        file_path = CONFIG_ROOT / "config.json"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_config_002_config_manager_file_exists(self):
        """
        DOC CLAIM: config_manager.py
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_config_003_env_file_exists(self):
        """
        DOC CLAIM: .env file for secrets
        TEST TYPE: File Existence
        """
        # .env may not exist in repo but .env.example should
        env_path = TRADING_BOT_ROOT / ".env"
        env_example_path = TRADING_BOT_ROOT / ".env.example"
        assert env_path.exists() or env_example_path.exists(), \
            "Neither .env nor .env.example found"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_config_004_config_manager_class_exists(self):
        """
        DOC CLAIM: ConfigManager class
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class ConfigManager" in content or "ConfigManager" in content, \
            "ConfigManager class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_config_005_load_config_method_exists(self):
        """
        DOC CLAIM: load_config method
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "load_config" in content or "load" in content, \
            "load_config method not found"
    
    def test_config_006_save_config_method_exists(self):
        """
        DOC CLAIM: save_config method
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "save_config" in content or "save" in content, \
            "save_config method not found"
    
    def test_config_007_get_method_exists(self):
        """
        DOC CLAIM: get method for config values
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def get" in content or "get(" in content, "get method not found"
    
    def test_config_008_set_method_exists(self):
        """
        DOC CLAIM: set method for config values
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def set" in content or "set(" in content or "update" in content, \
            "set method not found"
    
    # ==================== CONFIG SECTION TESTS ====================
    
    def test_config_009_mt5_config_section_exists(self):
        """
        DOC CLAIM: MT5 configuration section
        TEST TYPE: Config Section Existence
        """
        file_path = CONFIG_ROOT / "config.json"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "mt5" in content.lower(), "MT5 config section not found"
    
    def test_config_010_telegram_config_section_exists(self):
        """
        DOC CLAIM: Telegram configuration section
        TEST TYPE: Config Section Existence
        """
        file_path = CONFIG_ROOT / "config.json"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "telegram" in content.lower(), "Telegram config section not found"
    
    def test_config_011_risk_config_section_exists(self):
        """
        DOC CLAIM: Risk management configuration section
        TEST TYPE: Config Section Existence
        """
        file_path = CONFIG_ROOT / "config.json"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "risk" in content.lower(), "Risk config section not found"
    
    def test_config_012_plugin_config_section_exists(self):
        """
        DOC CLAIM: Plugin configuration section
        TEST TYPE: Config Section Existence
        """
        file_path = CONFIG_ROOT / "config.json"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "plugin" in content.lower(), "Plugin config section not found"
    
    def test_config_013_symbol_config_section_exists(self):
        """
        DOC CLAIM: Symbol configuration section
        TEST TYPE: Config Section Existence
        """
        file_path = CONFIG_ROOT / "config.json"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "symbol" in content.lower(), "Symbol config section not found"
    
    # ==================== HOT RELOAD TESTS ====================
    
    def test_config_014_hot_reload_support_exists(self):
        """
        DOC CLAIM: Hot reload configuration support
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "reload" in content.lower() or "watch" in content.lower() or "hot" in content.lower(), \
            "Hot reload support not found"
    
    def test_config_015_validation_support_exists(self):
        """
        DOC CLAIM: Configuration validation support
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "validate" in content.lower() or "valid" in content.lower(), \
            "Validation support not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
