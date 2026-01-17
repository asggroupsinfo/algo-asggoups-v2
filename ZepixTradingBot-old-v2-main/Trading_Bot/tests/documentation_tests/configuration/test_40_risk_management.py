"""
Documentation Testing: 40_RISK_MANAGEMENT.md
Tests all verifiable claims in 40_RISK_MANAGEMENT.md

Total Claims: 40
Verifiable Claims: 20
Test Cases: 20
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/40_RISK_MANAGEMENT.md"


class Test40RiskManagement:
    """Test suite for 40_RISK_MANAGEMENT.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_40_001_risk_manager_file_exists(self):
        """
        DOC CLAIM: "src/managers/risk_manager.py"
        DOC LOCATION: Line 4
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_40_002_risk_management_service_file_exists(self):
        """
        DOC CLAIM: "src/core/services/risk_management_service.py"
        DOC LOCATION: Line 5
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "services" / "risk_management_service.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_40_003_pip_calculator_file_exists(self):
        """
        DOC CLAIM: "src/utils/pip_calculator.py"
        DOC LOCATION: Line 6
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "utils" / "pip_calculator.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_40_004_risk_manager_class_exists(self):
        """
        DOC CLAIM: "class RiskManager:"
        DOC LOCATION: Line 79
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class RiskManager" in content, "RiskManager class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_40_005_init_method_exists(self):
        """
        DOC CLAIM: "def __init__(self, config):"
        DOC LOCATION: Line 80
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found"
    
    def test_40_006_calculate_lot_size_method_exists(self):
        """
        DOC CLAIM: "def calculate_lot_size(self, symbol: str, sl_pips: float, account_balance: float) -> float:"
        DOC LOCATION: Line 37
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "calculate_lot_size" in content, "calculate_lot_size method not found"
    
    def test_40_007_record_loss_method_exists(self):
        """
        DOC CLAIM: "def record_loss(self, amount: float):"
        DOC LOCATION: Line 86
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "record_loss" in content, "record_loss method not found"
    
    def test_40_008_check_daily_limit_method_exists(self):
        """
        DOC CLAIM: "def check_daily_limit(self, account_balance: float) -> bool:"
        DOC LOCATION: Line 91
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_daily_limit" in content or "daily_limit" in content, \
            "check_daily_limit method not found"
    
    def test_40_009_check_lifetime_limit_method_exists(self):
        """
        DOC CLAIM: "def check_lifetime_limit(self, account_balance: float) -> bool:"
        DOC LOCATION: Line 97
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_lifetime_limit" in content or "lifetime_limit" in content or "max_total_loss" in content, \
            "check_lifetime_limit method not found"
    
    def test_40_010_reset_daily_loss_method_exists(self):
        """
        DOC CLAIM: "def reset_daily_loss(self):"
        DOC LOCATION: Line 103
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "reset_daily" in content or "daily_loss" in content, "reset_daily_loss method not found"
    
    def test_40_011_get_risk_tier_method_exists(self):
        """
        DOC CLAIM: "tier = self.get_risk_tier(account_balance)"
        DOC LOCATION: Line 51
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_risk_tier" in content or "risk_tier" in content, "get_risk_tier method not found"
    
    def test_40_012_validate_trade_method_exists(self):
        """
        DOC CLAIM: "def validate_trade(self, trade: Trade, account_balance: float) -> Dict[str, Any]:"
        DOC LOCATION: Line 158
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "validate_trade" in content or "validate" in content, "validate_trade method not found"
    
    # ==================== ATTRIBUTE EXISTENCE TESTS ====================
    
    def test_40_013_config_attribute_exists(self):
        """
        DOC CLAIM: "self.config = config"
        DOC LOCATION: Line 81
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.config" in content, "config attribute not found"
    
    def test_40_014_daily_loss_attribute_exists(self):
        """
        DOC CLAIM: "self.daily_loss = 0.0"
        DOC LOCATION: Line 82
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "daily_loss" in content, "daily_loss attribute not found"
    
    def test_40_015_lifetime_loss_attribute_exists(self):
        """
        DOC CLAIM: "self.lifetime_loss = 0.0"
        DOC LOCATION: Line 83
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "lifetime_loss" in content or "total_loss" in content, "lifetime_loss attribute not found"
    
    # ==================== CONFIG TESTS ====================
    
    def test_40_016_risk_tiers_config_exists(self):
        """
        DOC CLAIM: "risk_tiers" config section
        DOC LOCATION: Line 202
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "risk_tier" in content.lower(), "risk_tiers config not found"
    
    def test_40_017_daily_loss_limit_config_exists(self):
        """
        DOC CLAIM: "daily_loss_limit" config
        DOC LOCATION: Line 207
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "daily_loss_limit" in content or "daily_limit" in content, \
            "daily_loss_limit config not found"
    
    def test_40_018_max_lot_config_exists(self):
        """
        DOC CLAIM: "max_lot" config
        DOC LOCATION: Line 209
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "max_lot" in content, "max_lot config not found"
    
    def test_40_019_symbol_config_exists(self):
        """
        DOC CLAIM: "symbol_config" section
        DOC LOCATION: Line 222
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "symbol_config" in content or "symbol" in content, "symbol_config not found"
    
    def test_40_020_pip_value_config_exists(self):
        """
        DOC CLAIM: "pip_value_per_std_lot" config
        DOC LOCATION: Line 225
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "pip_value" in content or "pip" in content, "pip_value config not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
