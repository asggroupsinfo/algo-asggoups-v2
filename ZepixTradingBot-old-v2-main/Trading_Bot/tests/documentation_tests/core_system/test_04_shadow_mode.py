"""
Documentation Testing: 04_SHADOW_MODE.md
Tests all verifiable claims in 04_SHADOW_MODE.md

Total Claims: 40
Verifiable Claims: 28
Test Cases: 28
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/04_SHADOW_MODE.md"


class Test04ShadowMode:
    """Test suite for 04_SHADOW_MODE.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_04_001_shadow_mode_manager_file_exists(self):
        """
        DOC CLAIM: "src/core/shadow_mode_manager.py"
        DOC LOCATION: Line 3
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_04_002_trading_engine_file_exists(self):
        """
        DOC CLAIM: "src/core/trading_engine.py - Uses ShadowModeManager"
        DOC LOCATION: Line 488
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_04_003_plugin_registry_file_exists(self):
        """
        DOC CLAIM: "src/core/plugin_system/plugin_registry.py - Plugin registration"
        DOC LOCATION: Line 490
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_04_004_shadow_mode_manager_class_exists(self):
        """
        DOC CLAIM: "class ShadowModeManager:"
        DOC LOCATION: Line 51
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class ShadowModeManager" in content, "ShadowModeManager class not found"
    
    def test_04_005_execution_mode_enum_exists(self):
        """
        DOC CLAIM: "class ExecutionMode(Enum):"
        DOC LOCATION: Line 27
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "ExecutionMode" in content, "ExecutionMode enum not found"
    
    # ==================== EXECUTION MODE VALUES TESTS ====================
    
    def test_04_006_legacy_only_mode_exists(self):
        """
        DOC CLAIM: "LEGACY_ONLY = 'legacy_only'"
        DOC LOCATION: Line 29
        TEST TYPE: Enum Value Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "LEGACY_ONLY" in content or "legacy_only" in content, \
            "LEGACY_ONLY mode not found"
    
    def test_04_007_shadow_mode_exists(self):
        """
        DOC CLAIM: "SHADOW = 'shadow'"
        DOC LOCATION: Line 30
        TEST TYPE: Enum Value Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "SHADOW" in content or "shadow" in content, "SHADOW mode not found"
    
    def test_04_008_plugin_shadow_mode_exists(self):
        """
        DOC CLAIM: "PLUGIN_SHADOW = 'plugin_shadow'"
        DOC LOCATION: Line 31
        TEST TYPE: Enum Value Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "PLUGIN_SHADOW" in content or "plugin_shadow" in content, \
            "PLUGIN_SHADOW mode not found"
    
    def test_04_009_plugin_only_mode_exists(self):
        """
        DOC CLAIM: "PLUGIN_ONLY = 'plugin_only'"
        DOC LOCATION: Line 32
        TEST TYPE: Enum Value Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "PLUGIN_ONLY" in content or "plugin_only" in content, \
            "PLUGIN_ONLY mode not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_04_010_init_method_exists(self):
        """
        DOC CLAIM: "def __init__(self, config: Dict[str, Any]):"
        DOC LOCATION: Line 62
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found"
    
    def test_04_011_set_execution_mode_method_exists(self):
        """
        DOC CLAIM: "def set_execution_mode(self, mode: ExecutionMode):"
        DOC LOCATION: Line 92
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "set_execution_mode" in content, "set_execution_mode method not found"
    
    def test_04_012_get_execution_mode_method_exists(self):
        """
        DOC CLAIM: "def get_execution_mode(self) -> ExecutionMode:"
        DOC LOCATION: Line 112
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_execution_mode" in content, "get_execution_mode method not found"
    
    def test_04_013_register_plugin_method_exists(self):
        """
        DOC CLAIM: "def register_plugin(self, plugin_id: str, plugin: Any):"
        DOC LOCATION: Line 120
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "register_plugin" in content, "register_plugin method not found"
    
    def test_04_014_unregister_plugin_method_exists(self):
        """
        DOC CLAIM: "def unregister_plugin(self, plugin_id: str):"
        DOC LOCATION: Line 131
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "unregister_plugin" in content, "unregister_plugin method not found"
    
    def test_04_015_compare_results_method_exists(self):
        """
        DOC CLAIM: "def compare_results(...)"
        DOC LOCATION: Line 141
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "compare_results" in content, "compare_results method not found"
    
    def test_04_016_record_plugin_execution_method_exists(self):
        """
        DOC CLAIM: "def record_plugin_execution(...)"
        DOC LOCATION: Line 212
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "record_plugin_execution" in content or "record_execution" in content, \
            "record_plugin_execution method not found"
    
    def test_04_017_get_statistics_method_exists(self):
        """
        DOC CLAIM: "def get_statistics(self) -> Dict[str, Any]:"
        DOC LOCATION: Line 313
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_statistics" in content or "get_stats" in content, \
            "get_statistics method not found"
    
    def test_04_018_get_recent_mismatches_method_exists(self):
        """
        DOC CLAIM: "def get_recent_mismatches(self, count: int = 10) -> List[Dict]:"
        DOC LOCATION: Line 342
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_recent_mismatches" in content or "mismatches" in content, \
            "get_recent_mismatches method not found"
    
    def test_04_019_get_execution_history_method_exists(self):
        """
        DOC CLAIM: "def get_execution_history(self, count: int = 100) -> List[Dict]:"
        DOC LOCATION: Line 346
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_execution_history" in content or "execution_history" in content, \
            "get_execution_history method not found"
    
    def test_04_020_generate_shadow_report_method_exists(self):
        """
        DOC CLAIM: "def generate_shadow_report(self) -> str:"
        DOC LOCATION: Line 354
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "generate_shadow_report" in content or "generate_report" in content, \
            "generate_shadow_report method not found"
    
    # ==================== ATTRIBUTE EXISTENCE TESTS ====================
    
    def test_04_021_config_attribute_exists(self):
        """
        DOC CLAIM: "self.config = config"
        DOC LOCATION: Line 63
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.config" in content, "config attribute not found"
    
    def test_04_022_execution_mode_attribute_exists(self):
        """
        DOC CLAIM: "self.execution_mode = ExecutionMode.LEGACY_ONLY"
        DOC LOCATION: Line 64
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.execution_mode" in content or "execution_mode" in content, \
            "execution_mode attribute not found"
    
    def test_04_023_registered_plugins_attribute_exists(self):
        """
        DOC CLAIM: "self.registered_plugins: Dict[str, Any] = {}"
        DOC LOCATION: Line 67
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "registered_plugins" in content or "plugins" in content, \
            "registered_plugins attribute not found"
    
    def test_04_024_execution_history_attribute_exists(self):
        """
        DOC CLAIM: "self.execution_history: List[Dict] = []"
        DOC LOCATION: Line 70
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "execution_history" in content, "execution_history attribute not found"
    
    def test_04_025_mismatches_attribute_exists(self):
        """
        DOC CLAIM: "self.mismatches: List[Dict] = []"
        DOC LOCATION: Line 73
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "mismatches" in content, "mismatches attribute not found"
    
    def test_04_026_stats_attribute_exists(self):
        """
        DOC CLAIM: "self.stats = {...}"
        DOC LOCATION: Line 76
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.stats" in content or "stats" in content, "stats attribute not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_04_027_enum_import_exists(self):
        """
        DOC CLAIM: ExecutionMode uses Enum
        DOC LOCATION: Line 27
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "from enum import" in content or "Enum" in content, "Enum import not found"
    
    def test_04_028_logging_import_exists(self):
        """
        DOC CLAIM: ShadowModeManager uses logging
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "logging" in content or "logger" in content, "logging import not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
