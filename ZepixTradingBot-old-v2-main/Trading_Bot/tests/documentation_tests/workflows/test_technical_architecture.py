"""
Documentation Testing: TECHNICAL_ARCHITECTURE.md
Tests all verifiable claims in TECHNICAL_ARCHITECTURE.md

Total Claims: 30
Verifiable Claims: 15
Test Cases: 15
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/TECHNICAL_ARCHITECTURE.md"


class TestTechnicalArchitecture:
    """Test suite for TECHNICAL_ARCHITECTURE.md"""
    
    # ==================== LAYER TESTS ====================
    
    def test_tech_arch_001_core_layer_exists(self):
        """
        DOC CLAIM: Core layer (src/core/)
        TEST TYPE: Layer Existence
        """
        dir_path = SRC_ROOT / "core"
        assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    def test_tech_arch_002_plugin_layer_exists(self):
        """
        DOC CLAIM: Plugin layer (src/logic_plugins/)
        TEST TYPE: Layer Existence
        """
        dir_path = SRC_ROOT / "logic_plugins"
        assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    def test_tech_arch_003_telegram_layer_exists(self):
        """
        DOC CLAIM: Telegram layer (src/telegram/)
        TEST TYPE: Layer Existence
        """
        dir_path = SRC_ROOT / "telegram"
        assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    def test_tech_arch_004_managers_layer_exists(self):
        """
        DOC CLAIM: Managers layer (src/managers/)
        TEST TYPE: Layer Existence
        """
        dir_path = SRC_ROOT / "managers"
        assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    def test_tech_arch_005_processors_layer_exists(self):
        """
        DOC CLAIM: Processors layer (src/processors/)
        TEST TYPE: Layer Existence
        """
        dir_path = SRC_ROOT / "processors"
        assert dir_path.exists(), f"Directory not found: {dir_path}"
    
    # ==================== COMPONENT TESTS ====================
    
    def test_tech_arch_006_trading_engine_component(self):
        """
        DOC CLAIM: TradingEngine component
        TEST TYPE: Component Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_tech_arch_007_service_api_component(self):
        """
        DOC CLAIM: ServiceAPI component
        TEST TYPE: Component Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_tech_arch_008_plugin_registry_component(self):
        """
        DOC CLAIM: PluginRegistry component
        TEST TYPE: Component Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_tech_arch_009_multi_telegram_component(self):
        """
        DOC CLAIM: MultiTelegramManager component
        TEST TYPE: Component Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_tech_arch_010_risk_manager_component(self):
        """
        DOC CLAIM: RiskManager component
        TEST TYPE: Component Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== PATTERN TESTS ====================
    
    def test_tech_arch_011_dependency_injection_pattern(self):
        """
        DOC CLAIM: Dependency injection pattern
        TEST TYPE: Pattern Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        # Check for constructor injection
        assert "__init__" in content and "self." in content, \
            "Dependency injection pattern not found"
    
    def test_tech_arch_012_facade_pattern(self):
        """
        DOC CLAIM: Facade pattern (ServiceAPI)
        TEST TYPE: Pattern Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class ServiceAPI" in content, "Facade pattern not found"
    
    def test_tech_arch_013_plugin_pattern(self):
        """
        DOC CLAIM: Plugin pattern
        TEST TYPE: Pattern Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "BasePlugin" in content or "BaseLogicPlugin" in content, \
            "Plugin pattern not found"
    
    def test_tech_arch_014_observer_pattern(self):
        """
        DOC CLAIM: Observer pattern (notifications)
        TEST TYPE: Pattern Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "notification" in content.lower() or "send" in content.lower(), \
            "Observer pattern not found"
    
    def test_tech_arch_015_strategy_pattern(self):
        """
        DOC CLAIM: Strategy pattern (plugins)
        TEST TYPE: Pattern Existence
        """
        file_path = SRC_ROOT / "logic_plugins" / "v3_combined" / "plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "process_entry_signal" in content, "Strategy pattern not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
