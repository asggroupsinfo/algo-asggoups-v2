"""
Documentation Testing: 12_PLUGIN_INTERFACES.md
Tests all verifiable claims in 12_PLUGIN_INTERFACES.md

Total Claims: 30
Verifiable Claims: 20
Test Cases: 20
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/12_PLUGIN_INTERFACES.md"


class Test12PluginInterfaces:
    """Test suite for 12_PLUGIN_INTERFACES.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_12_001_base_plugin_file_exists(self):
        """
        DOC CLAIM: "src/core/plugin_system/base_plugin.py"
        DOC LOCATION: Line 272
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_12_002_plugin_registry_file_exists(self):
        """
        DOC CLAIM: "src/core/plugin_system/plugin_registry.py"
        DOC LOCATION: Line 273
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_12_003_v3_combined_plugin_file_exists(self):
        """
        DOC CLAIM: "src/logic_plugins/v3_combined/plugin.py"
        DOC LOCATION: Line 274
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "logic_plugins" / "v3_combined" / "plugin.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== INTERFACE EXISTENCE TESTS ====================
    
    def test_12_004_isignal_processor_interface_exists(self):
        """
        DOC CLAIM: "class ISignalProcessor(ABC):"
        DOC LOCATION: Line 30
        TEST TYPE: Interface Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "ISignalProcessor" in content, "ISignalProcessor interface not found"
    
    def test_12_005_iorder_executor_interface_exists(self):
        """
        DOC CLAIM: "class IOrderExecutor(ABC):"
        DOC LOCATION: Line 59
        TEST TYPE: Interface Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "IOrderExecutor" in content, "IOrderExecutor interface not found"
    
    def test_12_006_ireentry_capable_interface_exists(self):
        """
        DOC CLAIM: "class IReentryCapable(ABC):"
        DOC LOCATION: Line 83
        TEST TYPE: Interface Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "IReentryCapable" in content, "IReentryCapable interface not found"
    
    def test_12_007_idual_order_capable_interface_exists(self):
        """
        DOC CLAIM: "class IDualOrderCapable(ABC):"
        DOC LOCATION: Line 117
        TEST TYPE: Interface Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "IDualOrderCapable" in content, "IDualOrderCapable interface not found"
    
    def test_12_008_iprofit_booking_capable_interface_exists(self):
        """
        DOC CLAIM: "class IProfitBookingCapable(ABC):"
        DOC LOCATION: Line 151
        TEST TYPE: Interface Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "IProfitBookingCapable" in content, "IProfitBookingCapable interface not found"
    
    def test_12_009_iautonomous_capable_interface_exists(self):
        """
        DOC CLAIM: "class IAutonomousCapable(ABC):"
        DOC LOCATION: Line 185
        TEST TYPE: Interface Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "IAutonomousCapable" in content, "IAutonomousCapable interface not found"
    
    def test_12_010_idatabase_capable_interface_exists(self):
        """
        DOC CLAIM: "class IDatabaseCapable(ABC):"
        DOC LOCATION: Line 214
        TEST TYPE: Interface Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "IDatabaseCapable" in content, "IDatabaseCapable interface not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_12_011_process_signal_method_documented(self):
        """
        DOC CLAIM: "process_signal()" method in ISignalProcessor
        DOC LOCATION: Line 49
        TEST TYPE: Method Documentation
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "process_signal" in content, "process_signal method not found"
    
    def test_12_012_execute_order_method_documented(self):
        """
        DOC CLAIM: "execute_order()" method in IOrderExecutor
        DOC LOCATION: Line 63
        TEST TYPE: Method Documentation
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "execute_order" in content, "execute_order method not found"
    
    def test_12_013_on_sl_hit_method_documented(self):
        """
        DOC CLAIM: "on_sl_hit()" method in IReentryCapable
        DOC LOCATION: Line 87
        TEST TYPE: Method Documentation
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "on_sl_hit" in content, "on_sl_hit method not found"
    
    def test_12_014_on_tp_hit_method_documented(self):
        """
        DOC CLAIM: "on_tp_hit()" method in IReentryCapable
        DOC LOCATION: Line 92
        TEST TYPE: Method Documentation
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "on_tp_hit" in content, "on_tp_hit method not found"
    
    def test_12_015_create_dual_orders_method_documented(self):
        """
        DOC CLAIM: "create_dual_orders()" method in IDualOrderCapable
        DOC LOCATION: Line 121
        TEST TYPE: Method Documentation
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "create_dual_orders" in content, "create_dual_orders method not found"
    
    def test_12_016_create_profit_chain_method_documented(self):
        """
        DOC CLAIM: "create_profit_chain()" method in IProfitBookingCapable
        DOC LOCATION: Line 155
        TEST TYPE: Method Documentation
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "create_profit_chain" in content, "create_profit_chain method not found"
    
    def test_12_017_check_recovery_allowed_method_documented(self):
        """
        DOC CLAIM: "check_recovery_allowed()" method in IAutonomousCapable
        DOC LOCATION: Line 189
        TEST TYPE: Method Documentation
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_recovery_allowed" in content, "check_recovery_allowed method not found"
    
    def test_12_018_save_trade_method_documented(self):
        """
        DOC CLAIM: "save_trade()" method in IDatabaseCapable
        DOC LOCATION: Line 218
        TEST TYPE: Method Documentation
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "save_trade" in content, "save_trade method not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_12_019_abc_import_exists(self):
        """
        DOC CLAIM: Interfaces use ABC
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "ABC" in content or "abc" in content, "ABC import not found"
    
    def test_12_020_abstractmethod_import_exists(self):
        """
        DOC CLAIM: Interfaces use abstractmethod
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "base_plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "abstractmethod" in content, "abstractmethod import not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
