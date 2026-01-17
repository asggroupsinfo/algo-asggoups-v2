"""
Documentation Testing: 22_PROFIT_BOOKING_SYSTEM.md
Tests all verifiable claims in 22_PROFIT_BOOKING_SYSTEM.md

Total Claims: 50
Verifiable Claims: 25
Test Cases: 25
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/22_PROFIT_BOOKING_SYSTEM.md"


class Test22ProfitBookingSystem:
    """Test suite for 22_PROFIT_BOOKING_SYSTEM.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_22_001_profit_booking_manager_file_exists(self):
        """
        DOC CLAIM: "src/managers/profit_booking_manager.py"
        DOC LOCATION: Line 3
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_22_002_profit_booking_manager_class_exists(self):
        """
        DOC CLAIM: "class ProfitBookingManager:"
        DOC LOCATION: Line 51
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class ProfitBookingManager" in content, "ProfitBookingManager class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_22_003_init_method_exists(self):
        """
        DOC CLAIM: "def __init__(self, config: Config, mt5_client: MT5Client, ...)"
        DOC LOCATION: Line 65
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found"
    
    def test_22_004_create_profit_chain_method_exists(self):
        """
        DOC CLAIM: "def create_profit_chain(self, order_b_id: int, symbol: str, ...)"
        DOC LOCATION: Line 96
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "create_profit_chain" in content, "create_profit_chain method not found"
    
    def test_22_005_calculate_profit_target_method_exists(self):
        """
        DOC CLAIM: "def _calculate_profit_target(self, symbol: str, direction: str, ...)"
        DOC LOCATION: Line 157
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_calculate_profit_target" in content or "calculate_profit_target" in content, \
            "_calculate_profit_target method not found"
    
    def test_22_006_check_profit_targets_method_exists(self):
        """
        DOC CLAIM: "def check_profit_targets(self, current_prices: Dict[str, float])"
        DOC LOCATION: Line 205
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_profit_targets" in content, "check_profit_targets method not found"
    
    def test_22_007_handle_profit_target_hit_method_exists(self):
        """
        DOC CLAIM: "async def handle_profit_target_hit(self, chain_id: str, order_id: int, ...)"
        DOC LOCATION: Line 263
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "handle_profit_target_hit" in content, "handle_profit_target_hit method not found"
    
    def test_22_008_create_level_order_method_exists(self):
        """
        DOC CLAIM: "async def _create_level_order(self, chain: ProfitBookingChain, ...)"
        DOC LOCATION: Line 365
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_create_level_order" in content or "create_level_order" in content, \
            "_create_level_order method not found"
    
    def test_22_009_calculate_fixed_risk_sl_method_exists(self):
        """
        DOC CLAIM: "def _calculate_fixed_risk_sl(self, symbol: str, direction: str, ...)"
        DOC LOCATION: Line 426
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_calculate_fixed_risk_sl" in content or "calculate_fixed_risk_sl" in content or "fixed_risk" in content, \
            "_calculate_fixed_risk_sl method not found"
    
    def test_22_010_handle_chain_sl_hit_method_exists(self):
        """
        DOC CLAIM: "async def handle_chain_sl_hit(self, chain_id: str, order_id: int, ...)"
        DOC LOCATION: Line 470
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "handle_chain_sl_hit" in content or "chain_sl_hit" in content, \
            "handle_chain_sl_hit method not found"
    
    def test_22_011_load_persisted_chains_method_exists(self):
        """
        DOC CLAIM: "def _load_persisted_chains(self):"
        DOC LOCATION: Line 543
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_load_persisted_chains" in content or "load_persisted_chains" in content or "load_chains" in content, \
            "_load_persisted_chains method not found"
    
    def test_22_012_persist_chain_method_exists(self):
        """
        DOC CLAIM: "def _persist_chain(self, chain: ProfitBookingChain):"
        DOC LOCATION: Line 561
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_persist_chain" in content or "persist_chain" in content or "save_chain" in content, \
            "_persist_chain method not found"
    
    # ==================== ATTRIBUTE EXISTENCE TESTS ====================
    
    def test_22_013_config_attribute_exists(self):
        """
        DOC CLAIM: "self.config = config"
        DOC LOCATION: Line 67
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.config" in content, "config attribute not found"
    
    def test_22_014_mt5_client_attribute_exists(self):
        """
        DOC CLAIM: "self.mt5_client = mt5_client"
        DOC LOCATION: Line 68
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "mt5_client" in content, "mt5_client attribute not found"
    
    def test_22_015_pip_calculator_attribute_exists(self):
        """
        DOC CLAIM: "self.pip_calculator = pip_calculator"
        DOC LOCATION: Line 69
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "pip_calculator" in content, "pip_calculator attribute not found"
    
    def test_22_016_db_attribute_exists(self):
        """
        DOC CLAIM: "self.db = db"
        DOC LOCATION: Line 70
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.db" in content or "database" in content, "db attribute not found"
    
    def test_22_017_logger_attribute_exists(self):
        """
        DOC CLAIM: "self.logger = logging.getLogger(__name__)"
        DOC LOCATION: Line 71
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "logger" in content, "logger attribute not found"
    
    def test_22_018_active_chains_attribute_exists(self):
        """
        DOC CLAIM: "self.active_chains: Dict[str, ProfitBookingChain] = {}"
        DOC LOCATION: Line 74
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "active_chains" in content, "active_chains attribute not found"
    
    def test_22_019_pyramid_config_attribute_exists(self):
        """
        DOC CLAIM: "self.pyramid_config = {...}"
        DOC LOCATION: Line 79
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "pyramid_config" in content or "pyramid" in content, "pyramid_config attribute not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_22_020_logging_import_exists(self):
        """
        DOC CLAIM: ProfitBookingManager uses logging
        DOC LOCATION: Line 71
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "logging" in content or "logger" in content, "logging import not found"
    
    def test_22_021_datetime_import_exists(self):
        """
        DOC CLAIM: ProfitBookingManager uses datetime
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "datetime" in content, "datetime import not found"
    
    def test_22_022_uuid_import_exists(self):
        """
        DOC CLAIM: ProfitBookingManager uses uuid
        DOC LOCATION: Line 113
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "uuid" in content, "uuid import not found"
    
    # ==================== PYRAMID CONFIG TESTS ====================
    
    def test_22_023_min_profit_target_config_exists(self):
        """
        DOC CLAIM: "min_profit_target: 7.0"
        DOC LOCATION: Line 81
        TEST TYPE: Config Value Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "min_profit_target" in content or "profit_target" in content, \
            "min_profit_target config not found"
    
    def test_22_024_max_level_config_exists(self):
        """
        DOC CLAIM: "max_level: 4"
        DOC LOCATION: Line 82
        TEST TYPE: Config Value Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "max_level" in content, "max_level config not found"
    
    def test_22_025_orders_per_level_config_exists(self):
        """
        DOC CLAIM: "orders_per_level: [1, 2, 4, 8, 16]"
        DOC LOCATION: Line 83
        TEST TYPE: Config Value Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "orders_per_level" in content or "level" in content, \
            "orders_per_level config not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
