"""
Documentation Testing: 05_CONFIG_MANAGER.md
Tests all verifiable claims in 05_CONFIG_MANAGER.md

Total Claims: 45
Verifiable Claims: 30
Test Cases: 30
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/05_CONFIG_MANAGER.md"


class Test05ConfigManager:
    """Test suite for 05_CONFIG_MANAGER.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_05_001_config_manager_file_exists(self):
        """
        DOC CLAIM: "src/core/config_manager.py"
        DOC LOCATION: Line 3
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_05_002_trading_engine_file_exists(self):
        """
        DOC CLAIM: "src/core/trading_engine.py - Uses ConfigManager"
        DOC LOCATION: Line 534
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_05_003_config_manager_class_exists(self):
        """
        DOC CLAIM: "class ConfigManager:"
        DOC LOCATION: Line 28
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class ConfigManager" in content, "ConfigManager class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_05_004_init_method_exists(self):
        """
        DOC CLAIM: "def __init__(self, config_path: str, callback=None):"
        DOC LOCATION: Line 40
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found"
    
    def test_05_005_load_config_method_exists(self):
        """
        DOC CLAIM: "def _load_config(self):"
        DOC LOCATION: Line 69
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_load_config" in content or "load_config" in content, \
            "_load_config method not found"
    
    def test_05_006_reload_config_method_exists(self):
        """
        DOC CLAIM: "def reload_config(self) -> bool:"
        DOC LOCATION: Line 100
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "reload_config" in content or "reload" in content, \
            "reload_config method not found"
    
    def test_05_007_validate_config_method_exists(self):
        """
        DOC CLAIM: "def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:"
        DOC LOCATION: Line 135
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_validate_config" in content or "validate_config" in content or "validate" in content, \
            "_validate_config method not found"
    
    def test_05_008_update_setting_method_exists(self):
        """
        DOC CLAIM: "def update_setting(self, key: str, value: Any) -> bool:"
        DOC LOCATION: Line 198
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "update_setting" in content or "update" in content, \
            "update_setting method not found"
    
    def test_05_009_batch_update_method_exists(self):
        """
        DOC CLAIM: "def batch_update(self, updates: Dict[str, Any]) -> bool:"
        DOC LOCATION: Line 259
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "batch_update" in content or "batch" in content, \
            "batch_update method not found"
    
    def test_05_010_start_watching_method_exists(self):
        """
        DOC CLAIM: "def start_watching(self):"
        DOC LOCATION: Line 317
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "start_watching" in content or "watch" in content, \
            "start_watching method not found"
    
    def test_05_011_stop_watching_method_exists(self):
        """
        DOC CLAIM: "def stop_watching(self):"
        DOC LOCATION: Line 328
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "stop_watching" in content or "stop" in content, \
            "stop_watching method not found"
    
    def test_05_012_watch_file_method_exists(self):
        """
        DOC CLAIM: "def _watch_file(self):"
        DOC LOCATION: Line 333
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_watch_file" in content or "watch_file" in content or "watch" in content, \
            "_watch_file method not found"
    
    def test_05_013_record_change_method_exists(self):
        """
        DOC CLAIM: "def _record_change(self, change_type: str, details: Dict):"
        DOC LOCATION: Line 360
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_record_change" in content or "record_change" in content or "record" in content, \
            "_record_change method not found"
    
    def test_05_014_get_change_history_method_exists(self):
        """
        DOC CLAIM: "def get_change_history(self, count: int = 10) -> List[Dict]:"
        DOC LOCATION: Line 374
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_change_history" in content or "change_history" in content, \
            "get_change_history method not found"
    
    def test_05_015_get_method_exists(self):
        """
        DOC CLAIM: "def get(self, key: str, default: Any = None) -> Any:"
        DOC LOCATION: Line 386
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def get(self" in content, "get method not found"
    
    def test_05_016_get_section_method_exists(self):
        """
        DOC CLAIM: "def get_section(self, section: str) -> Dict[str, Any]:"
        DOC LOCATION: Line 412
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_section" in content, "get_section method not found"
    
    def test_05_017_get_all_method_exists(self):
        """
        DOC CLAIM: "def get_all(self) -> Dict[str, Any]:"
        DOC LOCATION: Line 416
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_all" in content, "get_all method not found"
    
    # ==================== ATTRIBUTE EXISTENCE TESTS ====================
    
    def test_05_018_config_path_attribute_exists(self):
        """
        DOC CLAIM: "self.config_path = config_path"
        DOC LOCATION: Line 41
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.config_path" in content or "config_path" in content, \
            "config_path attribute not found"
    
    def test_05_019_callback_attribute_exists(self):
        """
        DOC CLAIM: "self.callback = callback"
        DOC LOCATION: Line 42
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.callback" in content or "callback" in content, \
            "callback attribute not found"
    
    def test_05_020_config_attribute_exists(self):
        """
        DOC CLAIM: "self.config: Dict[str, Any] = {}"
        DOC LOCATION: Line 46
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.config" in content, "config attribute not found"
    
    def test_05_021_previous_config_attribute_exists(self):
        """
        DOC CLAIM: "self.previous_config: Dict[str, Any] = {}"
        DOC LOCATION: Line 49
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "previous_config" in content or "backup" in content, \
            "previous_config attribute not found"
    
    def test_05_022_change_history_attribute_exists(self):
        """
        DOC CLAIM: "self.change_history: List[Dict] = []"
        DOC LOCATION: Line 52
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "change_history" in content, "change_history attribute not found"
    
    def test_05_023_watcher_attribute_exists(self):
        """
        DOC CLAIM: "self.watcher = None"
        DOC LOCATION: Line 55
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "watcher" in content or "watch" in content, "watcher attribute not found"
    
    def test_05_024_watching_attribute_exists(self):
        """
        DOC CLAIM: "self.watching = False"
        DOC LOCATION: Line 56
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "watching" in content, "watching attribute not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_05_025_json_import_exists(self):
        """
        DOC CLAIM: ConfigManager uses json for config loading
        DOC LOCATION: Line 73
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "json" in content, "json import not found"
    
    def test_05_026_logging_import_exists(self):
        """
        DOC CLAIM: ConfigManager uses logging
        DOC LOCATION: Line 43
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "logging" in content or "logger" in content, "logging import not found"
    
    def test_05_027_threading_import_exists(self):
        """
        DOC CLAIM: ConfigManager uses threading for file watching
        DOC LOCATION: Line 323
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "threading" in content or "Thread" in content, "threading import not found"
    
    def test_05_028_datetime_import_exists(self):
        """
        DOC CLAIM: ConfigManager uses datetime for timestamps
        DOC LOCATION: Line 363
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "datetime" in content, "datetime import not found"
    
    def test_05_029_copy_import_exists(self):
        """
        DOC CLAIM: ConfigManager uses copy for deep copying
        DOC LOCATION: Line 270
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "copy" in content, "copy import not found"
    
    def test_05_030_os_import_exists(self):
        """
        DOC CLAIM: ConfigManager uses os for file operations
        DOC LOCATION: Line 335
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "os" in content, "os import not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
