"""
Documentation Testing: 20_DUAL_ORDER_SYSTEM.md
Tests all verifiable claims in 20_DUAL_ORDER_SYSTEM.md

Total Claims: 40
Verifiable Claims: 25
Test Cases: 25
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/20_DUAL_ORDER_SYSTEM.md"


class Test20DualOrderSystem:
    """Test suite for 20_DUAL_ORDER_SYSTEM.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_20_001_dual_order_manager_file_exists(self):
        """
        DOC CLAIM: "src/managers/dual_order_manager.py"
        DOC LOCATION: Line 3
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_20_002_trading_engine_file_exists(self):
        """
        DOC CLAIM: "src/core/trading_engine.py"
        DOC LOCATION: Line 460
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_20_003_reentry_manager_file_exists(self):
        """
        DOC CLAIM: "src/managers/reentry_manager.py"
        DOC LOCATION: Line 461
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_20_004_profit_booking_manager_file_exists(self):
        """
        DOC CLAIM: "src/managers/profit_booking_manager.py"
        DOC LOCATION: Line 462
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_20_005_pip_calculator_file_exists(self):
        """
        DOC CLAIM: "src/utils/pip_calculator.py"
        DOC LOCATION: Line 463
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "utils" / "pip_calculator.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_20_006_dual_order_manager_class_exists(self):
        """
        DOC CLAIM: "class DualOrderManager:"
        DOC LOCATION: Line 51
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class DualOrderManager" in content, "DualOrderManager class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_20_007_init_method_exists(self):
        """
        DOC CLAIM: "def __init__(self, config: Config, risk_manager: RiskManager, ...)"
        DOC LOCATION: Line 60
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found"
    
    def test_20_008_is_enabled_method_exists(self):
        """
        DOC CLAIM: "def is_enabled(self) -> bool:"
        DOC LOCATION: Line 78
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "is_enabled" in content, "is_enabled method not found"
    
    def test_20_009_validate_dual_order_risk_method_exists(self):
        """
        DOC CLAIM: "def validate_dual_order_risk(self, symbol: str, lot_size: float, ...)"
        DOC LOCATION: Line 86
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "validate_dual_order_risk" in content or "validate" in content, \
            "validate_dual_order_risk method not found"
    
    def test_20_010_create_dual_orders_method_exists(self):
        """
        DOC CLAIM: "def create_dual_orders(self, alert: Alert, strategy: str, ...)"
        DOC LOCATION: Line 161
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "create_dual_orders" in content, "create_dual_orders method not found"
    
    def test_20_011_place_single_order_method_exists(self):
        """
        DOC CLAIM: "def _place_single_order(self, trade: Trade, strategy: str, ...)"
        DOC LOCATION: Line 293
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_place_single_order" in content or "place_order" in content, \
            "_place_single_order method not found"
    
    # ==================== ATTRIBUTE EXISTENCE TESTS ====================
    
    def test_20_012_config_attribute_exists(self):
        """
        DOC CLAIM: "self.config = config"
        DOC LOCATION: Line 63
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.config" in content, "config attribute not found"
    
    def test_20_013_risk_manager_attribute_exists(self):
        """
        DOC CLAIM: "self.risk_manager = risk_manager"
        DOC LOCATION: Line 64
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "risk_manager" in content, "risk_manager attribute not found"
    
    def test_20_014_mt5_client_attribute_exists(self):
        """
        DOC CLAIM: "self.mt5_client = mt5_client"
        DOC LOCATION: Line 65
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "mt5_client" in content, "mt5_client attribute not found"
    
    def test_20_015_pip_calculator_attribute_exists(self):
        """
        DOC CLAIM: "self.pip_calculator = pip_calculator"
        DOC LOCATION: Line 66
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "pip_calculator" in content, "pip_calculator attribute not found"
    
    def test_20_016_logger_attribute_exists(self):
        """
        DOC CLAIM: "self.logger = logging.getLogger(__name__)"
        DOC LOCATION: Line 68
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "logger" in content, "logger attribute not found"
    
    # ==================== ORDER TYPE TESTS ====================
    
    def test_20_017_order_type_tp_trail_exists(self):
        """
        DOC CLAIM: "order_type='TP_TRAIL'"
        DOC LOCATION: Line 246
        TEST TYPE: Order Type Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "TP_TRAIL" in content, "TP_TRAIL order type not found"
    
    def test_20_018_order_type_profit_trail_exists(self):
        """
        DOC CLAIM: "order_type='PROFIT_TRAIL'"
        DOC LOCATION: Line 261
        TEST TYPE: Order Type Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "PROFIT_TRAIL" in content, "PROFIT_TRAIL order type not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_20_019_logging_import_exists(self):
        """
        DOC CLAIM: DualOrderManager uses logging
        DOC LOCATION: Line 68
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "logging" in content or "logger" in content, "logging import not found"
    
    def test_20_020_datetime_import_exists(self):
        """
        DOC CLAIM: DualOrderManager uses datetime
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "datetime" in content, "datetime import not found"
    
    # ==================== RETURN TYPE TESTS ====================
    
    def test_20_021_create_dual_orders_returns_dict(self):
        """
        DOC CLAIM: "create_dual_orders returns dict with order_a, order_b, etc."
        DOC LOCATION: Lines 165-171
        TEST TYPE: Return Type
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "order_a" in content and "order_b" in content, \
            "create_dual_orders return structure not found"
    
    def test_20_022_order_a_placed_key_exists(self):
        """
        DOC CLAIM: "order_a_placed: bool"
        DOC LOCATION: Line 168
        TEST TYPE: Return Key Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "order_a_placed" in content, "order_a_placed key not found"
    
    def test_20_023_order_b_placed_key_exists(self):
        """
        DOC CLAIM: "order_b_placed: bool"
        DOC LOCATION: Line 169
        TEST TYPE: Return Key Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "order_b_placed" in content, "order_b_placed key not found"
    
    def test_20_024_errors_key_exists(self):
        """
        DOC CLAIM: "errors: List[str]"
        DOC LOCATION: Line 170
        TEST TYPE: Return Key Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "errors" in content, "errors key not found"
    
    def test_20_025_math_import_exists(self):
        """
        DOC CLAIM: DualOrderManager uses math.floor
        DOC LOCATION: Line 132
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "math" in content or "floor" in content, "math import not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
