"""
Documentation Testing: PROJECT_OVERVIEW.md
Tests all verifiable claims in PROJECT_OVERVIEW.md

Total Claims: 25
Verifiable Claims: 12
Test Cases: 12
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/PROJECT_OVERVIEW.md"


class TestProjectOverview:
    """Test suite for PROJECT_OVERVIEW.md"""
    
    # ==================== DIRECTORY STRUCTURE TESTS ====================
    
    def test_overview_001_src_directory_exists(self):
        """
        DOC CLAIM: src/ directory structure
        TEST TYPE: Directory Existence
        """
        assert SRC_ROOT.exists(), f"Directory not found: {SRC_ROOT}"
    
    def test_overview_002_core_directory_exists(self):
        """
        DOC CLAIM: src/core/ directory
        TEST TYPE: Directory Existence
        """
        dir_path = SRC_ROOT / "core"
        assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    def test_overview_003_telegram_directory_exists(self):
        """
        DOC CLAIM: src/telegram/ directory
        TEST TYPE: Directory Existence
        """
        dir_path = SRC_ROOT / "telegram"
        assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    def test_overview_004_managers_directory_exists(self):
        """
        DOC CLAIM: src/managers/ directory
        TEST TYPE: Directory Existence
        """
        dir_path = SRC_ROOT / "managers"
        assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    def test_overview_005_logic_plugins_directory_exists(self):
        """
        DOC CLAIM: src/logic_plugins/ directory
        TEST TYPE: Directory Existence
        """
        dir_path = SRC_ROOT / "logic_plugins"
        assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    def test_overview_006_processors_directory_exists(self):
        """
        DOC CLAIM: src/processors/ directory
        TEST TYPE: Directory Existence
        """
        dir_path = SRC_ROOT / "processors"
        assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    # ==================== KEY FILE TESTS ====================
    
    def test_overview_007_main_file_exists(self):
        """
        DOC CLAIM: main.py entry point
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "main.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_overview_008_config_file_exists(self):
        """
        DOC CLAIM: config.json configuration
        TEST TYPE: File Existence
        """
        file_path = TRADING_BOT_ROOT / "config" / "config.json"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_overview_009_trading_engine_file_exists(self):
        """
        DOC CLAIM: trading_engine.py core orchestrator
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_overview_010_database_file_exists(self):
        """
        DOC CLAIM: database.py data persistence
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "database.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== PLUGIN STRUCTURE TESTS ====================
    
    def test_overview_011_v3_plugin_directory_exists(self):
        """
        DOC CLAIM: V3 Combined plugin directory
        TEST TYPE: Directory Existence
        """
        dir_path = SRC_ROOT / "logic_plugins" / "v3_combined"
        assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    def test_overview_012_v6_plugin_directories_exist(self):
        """
        DOC CLAIM: V6 Price Action plugin directories
        TEST TYPE: Directory Existence
        """
        v6_dirs = [
            SRC_ROOT / "logic_plugins" / "v6_price_action_1m",
            SRC_ROOT / "logic_plugins" / "v6_price_action_5m",
            SRC_ROOT / "logic_plugins" / "v6_price_action_15m",
            SRC_ROOT / "logic_plugins" / "v6_price_action_1h"
        ]
        found = sum(1 for d in v6_dirs if d.exists())
        assert found >= 1, "No V6 plugin directories found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
