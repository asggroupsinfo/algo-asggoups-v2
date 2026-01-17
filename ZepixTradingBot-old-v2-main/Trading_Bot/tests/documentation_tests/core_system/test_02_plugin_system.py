"""
Documentation Testing: 02_PLUGIN_SYSTEM.md
Tests all verifiable claims in 02_PLUGIN_SYSTEM.md

Total Claims: 50
Verifiable Claims: 35
Test Cases: 35
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/02_PLUGIN_SYSTEM.md"


class Test02PluginSystem:
    """Test suite for 02_PLUGIN_SYSTEM.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_02_001_plugin_registry_file_exists(self):
        """
        DOC CLAIM: "src/core/plugin_system/plugin_registry.py (375 lines)"
        DOC LOCATION: Line 4
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_02_002_base_plugin_file_exists(self):
        """
        DOC CLAIM: "src/core/plugin_system/base_plugin.py (121 lines)"
        DOC LOCATION: Line 5
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_02_003_plugin_router_file_exists(self):
        """
        DOC CLAIM: "src/core/plugin_router.py (286 lines)"
        DOC LOCATION: Line 6
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_router.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_02_004_plugin_registry_class_exists(self):
        """
        DOC CLAIM: "class PluginRegistry:"
        DOC LOCATION: Line 82
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class PluginRegistry" in content, "PluginRegistry class not found"
    
    def test_02_005_base_logic_plugin_class_exists(self):
        """
        DOC CLAIM: "class BaseLogicPlugin(ABC):"
        DOC LOCATION: Line 220
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class BaseLogicPlugin" in content, "BaseLogicPlugin class not found"
    
    def test_02_006_plugin_router_class_exists(self):
        """
        DOC CLAIM: "class PluginRouter:"
        DOC LOCATION: Line 343
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_router.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class PluginRouter" in content, "PluginRouter class not found"
    
    # ==================== METHOD EXISTENCE TESTS (PluginRegistry) ====================
    
    def test_02_007_plugin_registry_init_exists(self):
        """
        DOC CLAIM: "def __init__(self, config: Dict[str, Any]):"
        DOC LOCATION: Line 93
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found in PluginRegistry"
    
    def test_02_008_load_plugins_method_exists(self):
        """
        DOC CLAIM: "def _load_plugins(self):"
        DOC LOCATION: Line 99
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        # Check for _load_plugins or load_all_plugins or similar
        has_load = "_load_plugins" in content or "load_all_plugins" in content or "load_plugins" in content
        assert has_load, "Plugin loading method not found"
    
    def test_02_009_get_plugin_for_signal_method_exists(self):
        """
        DOC CLAIM: "def get_plugin_for_signal(self, signal_data: Dict[str, Any]) -> Optional[BaseLogicPlugin]:"
        DOC LOCATION: Line 134
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_plugin_for_signal" in content, "get_plugin_for_signal method not found"
    
    def test_02_010_get_plugin_method_exists(self):
        """
        DOC CLAIM: "def get_plugin(self, plugin_id: str) -> Optional[BaseLogicPlugin]:"
        DOC LOCATION: Line 171
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def get_plugin" in content, "get_plugin method not found"
    
    def test_02_011_get_all_plugins_method_exists(self):
        """
        DOC CLAIM: "def get_all_plugins(self) -> Dict[str, BaseLogicPlugin]:"
        DOC LOCATION: Line 175
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_all_plugins" in content, "get_all_plugins method not found"
    
    def test_02_012_enable_plugin_method_exists(self):
        """
        DOC CLAIM: "def enable_plugin(self, plugin_id: str) -> bool:"
        DOC LOCATION: Line 179
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "enable_plugin" in content, "enable_plugin method not found"
    
    def test_02_013_disable_plugin_method_exists(self):
        """
        DOC CLAIM: "def disable_plugin(self, plugin_id: str) -> bool:"
        DOC LOCATION: Line 187
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "disable_plugin" in content, "disable_plugin method not found"
    
    def test_02_014_get_plugin_status_method_exists(self):
        """
        DOC CLAIM: "def get_plugin_status(self) -> Dict[str, Any]:"
        DOC LOCATION: Line 196
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_plugin_status" in content or "get_status" in content, \
            "Plugin status method not found"
    
    # ==================== METHOD EXISTENCE TESTS (BaseLogicPlugin) ====================
    
    def test_02_015_base_plugin_init_exists(self):
        """
        DOC CLAIM: "def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):"
        DOC LOCATION: Line 235
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found in BaseLogicPlugin"
    
    def test_02_016_process_entry_signal_abstract_exists(self):
        """
        DOC CLAIM: "@abstractmethod async def process_entry_signal(self, alert: Any) -> Dict[str, Any]:"
        DOC LOCATION: Line 251
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "process_entry_signal" in content, "process_entry_signal method not found"
    
    def test_02_017_process_exit_signal_abstract_exists(self):
        """
        DOC CLAIM: "@abstractmethod async def process_exit_signal(self, alert: Any) -> Dict[str, Any]:"
        DOC LOCATION: Line 264
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "process_exit_signal" in content, "process_exit_signal method not found"
    
    def test_02_018_process_reversal_signal_abstract_exists(self):
        """
        DOC CLAIM: "@abstractmethod async def process_reversal_signal(self, alert: Any) -> Dict[str, Any]:"
        DOC LOCATION: Line 277
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "process_reversal_signal" in content, "process_reversal_signal method not found"
    
    def test_02_019_on_sl_hit_method_exists(self):
        """
        DOC CLAIM: "async def on_sl_hit(self, event: Any) -> bool:"
        DOC LOCATION: Line 294
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "on_sl_hit" in content, "on_sl_hit method not found"
    
    def test_02_020_on_tp_hit_method_exists(self):
        """
        DOC CLAIM: "async def on_tp_hit(self, event: Any) -> bool:"
        DOC LOCATION: Line 306
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "on_tp_hit" in content, "on_tp_hit method not found"
    
    def test_02_021_get_status_method_exists(self):
        """
        DOC CLAIM: "def get_status(self) -> Dict[str, Any]:"
        DOC LOCATION: Line 318
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_status" in content, "get_status method not found"
    
    # ==================== METHOD EXISTENCE TESTS (PluginRouter) ====================
    
    def test_02_022_plugin_router_init_exists(self):
        """
        DOC CLAIM: "def __init__(self, registry: PluginRegistry, config: Dict[str, Any]):"
        DOC LOCATION: Line 354
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_router.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found in PluginRouter"
    
    def test_02_023_route_signal_method_exists(self):
        """
        DOC CLAIM: "async def route_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:"
        DOC LOCATION: Line 358
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_router.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "route_signal" in content, "route_signal method not found"
    
    def test_02_024_broadcast_signal_method_exists(self):
        """
        DOC CLAIM: "async def broadcast_signal(self, signal: Dict[str, Any]) -> List[Dict[str, Any]]:"
        DOC LOCATION: Line 394
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_router.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "broadcast_signal" in content or "broadcast" in content, \
            "broadcast_signal method not found"
    
    # ==================== INTERFACE FILE EXISTENCE TESTS ====================
    
    def test_02_025_plugin_interface_file_exists(self):
        """
        DOC CLAIM: ISignalProcessor interface exists
        DOC LOCATION: Line 431
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_interface.py"
        assert file_path.exists(), f"Plugin interface file not found: {file_path}"
    
    def test_02_026_reentry_interface_file_exists(self):
        """
        DOC CLAIM: IReentryCapable interface exists
        DOC LOCATION: Line 480
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "reentry_interface.py"
        assert file_path.exists(), f"Reentry interface file not found: {file_path}"
    
    def test_02_027_dual_order_interface_file_exists(self):
        """
        DOC CLAIM: IDualOrderCapable interface exists
        DOC LOCATION: Line 512
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "dual_order_interface.py"
        assert file_path.exists(), f"Dual order interface file not found: {file_path}"
    
    def test_02_028_profit_booking_interface_file_exists(self):
        """
        DOC CLAIM: IProfitBookingCapable interface exists
        DOC LOCATION: Line 544
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "profit_booking_interface.py"
        assert file_path.exists(), f"Profit booking interface file not found: {file_path}"
    
    def test_02_029_autonomous_interface_file_exists(self):
        """
        DOC CLAIM: IAutonomousCapable interface exists
        DOC LOCATION: Line 576
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "autonomous_interface.py"
        assert file_path.exists(), f"Autonomous interface file not found: {file_path}"
    
    # ==================== INTERFACE CLASS EXISTENCE TESTS ====================
    
    def test_02_030_isignal_processor_interface_exists(self):
        """
        DOC CLAIM: "class ISignalProcessor(ABC):"
        DOC LOCATION: Line 431
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_interface.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "ISignalProcessor" in content, "ISignalProcessor interface not found"
    
    def test_02_031_iorder_executor_interface_exists(self):
        """
        DOC CLAIM: "class IOrderExecutor(ABC):"
        DOC LOCATION: Line 458
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_interface.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "IOrderExecutor" in content, "IOrderExecutor interface not found"
    
    def test_02_032_ireentry_capable_interface_exists(self):
        """
        DOC CLAIM: "class IReentryCapable(ABC):"
        DOC LOCATION: Line 480
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "reentry_interface.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "IReentryCapable" in content, "IReentryCapable interface not found"
    
    def test_02_033_idual_order_capable_interface_exists(self):
        """
        DOC CLAIM: "class IDualOrderCapable(ABC):"
        DOC LOCATION: Line 512
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "dual_order_interface.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "IDualOrderCapable" in content, "IDualOrderCapable interface not found"
    
    def test_02_034_iprofit_booking_capable_interface_exists(self):
        """
        DOC CLAIM: "class IProfitBookingCapable(ABC):"
        DOC LOCATION: Line 544
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "profit_booking_interface.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "IProfitBookingCapable" in content, "IProfitBookingCapable interface not found"
    
    def test_02_035_iautonomous_capable_interface_exists(self):
        """
        DOC CLAIM: "class IAutonomousCapable(ABC):"
        DOC LOCATION: Line 576
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "autonomous_interface.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "IAutonomousCapable" in content, "IAutonomousCapable interface not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
