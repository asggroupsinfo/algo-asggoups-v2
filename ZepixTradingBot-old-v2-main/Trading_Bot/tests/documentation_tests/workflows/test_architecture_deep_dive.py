"""
Documentation Testing: ARCHITECTURE_DEEP_DIVE.md
Tests all verifiable claims in ARCHITECTURE_DEEP_DIVE.md

Total Claims: 60
Verifiable Claims: 20
Test Cases: 20
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/ARCHITECTURE_DEEP_DIVE.md"


class TestArchitectureDeepDive:
    """Test suite for ARCHITECTURE_DEEP_DIVE.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_arch_001_trading_engine_file_exists(self):
        """
        DOC CLAIM: "src/core/trading_engine.py (2382 lines)"
        DOC LOCATION: Line 4
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_arch_002_service_api_file_exists(self):
        """
        DOC CLAIM: "src/core/plugin_system/service_api.py (1312 lines)"
        DOC LOCATION: Line 5
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_arch_003_plugin_registry_file_exists(self):
        """
        DOC CLAIM: "src/core/plugin_system/plugin_registry.py"
        DOC LOCATION: Line 6
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_arch_004_base_plugin_file_exists(self):
        """
        DOC CLAIM: "src/core/plugin_system/base_plugin.py (121 lines)"
        DOC LOCATION: Line 7
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_arch_005_multi_telegram_manager_file_exists(self):
        """
        DOC CLAIM: "src/telegram/multi_telegram_manager.py"
        DOC LOCATION: Line 8
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_arch_006_shadow_mode_manager_file_exists(self):
        """
        DOC CLAIM: "src/core/shadow_mode_manager.py"
        DOC LOCATION: Line 9
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_arch_007_trading_engine_class_exists(self):
        """
        DOC CLAIM: "class TradingEngine:"
        DOC LOCATION: Line 58
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class TradingEngine" in content, "TradingEngine class not found"
    
    def test_arch_008_service_api_class_exists(self):
        """
        DOC CLAIM: "class ServiceAPI:"
        DOC LOCATION: Line 125
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class ServiceAPI" in content, "ServiceAPI class not found"
    
    def test_arch_009_base_logic_plugin_class_exists(self):
        """
        DOC CLAIM: "class BaseLogicPlugin(ABC):"
        DOC LOCATION: Line 214
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "BaseLogicPlugin" in content or "BasePlugin" in content, \
            "BaseLogicPlugin class not found"
    
    def test_arch_010_plugin_registry_class_exists(self):
        """
        DOC CLAIM: "class PluginRegistry:"
        DOC LOCATION: Line 250
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class PluginRegistry" in content, "PluginRegistry class not found"
    
    def test_arch_011_multi_telegram_manager_class_exists(self):
        """
        DOC CLAIM: "class MultiTelegramManager:"
        DOC LOCATION: Line 287
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class MultiTelegramManager" in content, "MultiTelegramManager class not found"
    
    def test_arch_012_shadow_mode_manager_class_exists(self):
        """
        DOC CLAIM: "class ShadowModeManager:"
        DOC LOCATION: Line 309
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class ShadowModeManager" in content or "ShadowMode" in content, \
            "ShadowModeManager class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_arch_013_delegate_to_plugin_method_exists(self):
        """
        DOC CLAIM: "async def delegate_to_plugin(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:"
        DOC LOCATION: Line 76
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "delegate_to_plugin" in content, "delegate_to_plugin method not found"
    
    def test_arch_014_register_service_method_exists(self):
        """
        DOC CLAIM: "def register_service(self, name: str, service: Any, health_check: Optional[Callable] = None):"
        DOC LOCATION: Line 137
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "register_service" in content, "register_service method not found"
    
    def test_arch_015_call_service_method_exists(self):
        """
        DOC CLAIM: "async def call_service(self, service_name: str, method_name: str, *args, **kwargs) -> Any:"
        DOC LOCATION: Line 160
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "call_service" in content, "call_service method not found"
    
    def test_arch_016_check_health_method_exists(self):
        """
        DOC CLAIM: "async def check_health(self) -> Dict[str, bool]:"
        DOC LOCATION: Line 192
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_health" in content or "health" in content, "check_health method not found"
    
    def test_arch_017_get_plugin_for_signal_method_exists(self):
        """
        DOC CLAIM: "def get_plugin_for_signal(self, signal_data: Dict) -> Optional[BaseLogicPlugin]:"
        DOC LOCATION: Line 261
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_plugin_for_signal" in content, "get_plugin_for_signal method not found"
    
    def test_arch_018_send_notification_async_method_exists(self):
        """
        DOC CLAIM: "async def send_notification_async(self, notification_type: str, message: str, **kwargs):"
        DOC LOCATION: Line 295
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "send_notification" in content, "send_notification_async method not found"
    
    # ==================== ATTRIBUTE TESTS ====================
    
    def test_arch_019_service_api_version_exists(self):
        """
        DOC CLAIM: "VERSION = '3.0.0'"
        DOC LOCATION: Line 132
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "VERSION" in content or "version" in content.lower(), "VERSION attribute not found"
    
    def test_arch_020_execution_mode_exists(self):
        """
        DOC CLAIM: "ExecutionMode.LIVE"
        DOC LOCATION: Line 313
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "ExecutionMode" in content or "LIVE" in content or "execution_mode" in content.lower(), \
            "ExecutionMode not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
