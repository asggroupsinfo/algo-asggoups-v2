"""
Documentation Testing: 23_AUTONOMOUS_SYSTEM.md
Tests all verifiable claims in 23_AUTONOMOUS_SYSTEM.md

Total Claims: 55
Verifiable Claims: 25
Test Cases: 25
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/23_AUTONOMOUS_SYSTEM.md"


class Test23AutonomousSystem:
    """Test suite for 23_AUTONOMOUS_SYSTEM.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_23_001_autonomous_system_manager_file_exists(self):
        """
        DOC CLAIM: "src/managers/autonomous_system_manager.py"
        DOC LOCATION: Line 3
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_23_002_autonomous_system_manager_class_exists(self):
        """
        DOC CLAIM: "class AutonomousSystemManager:"
        DOC LOCATION: Line 41
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class AutonomousSystemManager" in content, "AutonomousSystemManager class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_23_003_init_method_exists(self):
        """
        DOC CLAIM: "def __init__(self, config: Config, reentry_manager: ReEntryManager, ...)"
        DOC LOCATION: Line 47
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found"
    
    def test_23_004_run_autonomous_checks_method_exists(self):
        """
        DOC CLAIM: "async def run_autonomous_checks(self, open_trades: List[Trade], ...)"
        DOC LOCATION: Line 83
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "run_autonomous_checks" in content, "run_autonomous_checks method not found"
    
    def test_23_005_execute_recovery_trade_method_exists(self):
        """
        DOC CLAIM: "async def _execute_recovery_trade(self, chain, recovery_result: Dict, ...)"
        DOC LOCATION: Line 183
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_execute_recovery_trade" in content or "execute_recovery_trade" in content, \
            "_execute_recovery_trade method not found"
    
    def test_23_006_check_safety_limits_method_exists(self):
        """
        DOC CLAIM: "async def check_safety_limits(self) -> Dict[str, Any]:"
        DOC LOCATION: Line 264
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_safety_limits" in content, "check_safety_limits method not found"
    
    def test_23_007_check_daily_limits_method_exists(self):
        """
        DOC CLAIM: "def check_daily_limits(self) -> bool:"
        DOC LOCATION: Line 320
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_daily_limits" in content, "check_daily_limits method not found"
    
    def test_23_008_check_reverse_shield_method_exists(self):
        """
        DOC CLAIM: "async def _check_reverse_shield(self, symbol: str, current_price: float, ...)"
        DOC LOCATION: Line 347
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_check_reverse_shield" in content or "check_reverse_shield" in content or "reverse_shield" in content, \
            "_check_reverse_shield method not found"
    
    def test_23_009_detect_reversal_method_exists(self):
        """
        DOC CLAIM: "async def _detect_reversal(self, symbol: str, current_price: float, ...)"
        DOC LOCATION: Line 414
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_detect_reversal" in content or "detect_reversal" in content or "reversal" in content, \
            "_detect_reversal method not found"
    
    def test_23_010_deactivate_reverse_shield_method_exists(self):
        """
        DOC CLAIM: "def deactivate_reverse_shield(self, symbol: str) -> bool:"
        DOC LOCATION: Line 459
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "deactivate_reverse_shield" in content, "deactivate_reverse_shield method not found"
    
    def test_23_011_is_direction_blocked_method_exists(self):
        """
        DOC CLAIM: "def is_direction_blocked(self, symbol: str, direction: str) -> bool:"
        DOC LOCATION: Line 479
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "is_direction_blocked" in content, "is_direction_blocked method not found"
    
    def test_23_012_register_sl_recovery_method_exists(self):
        """
        DOC CLAIM: "def register_sl_recovery(self, trade: Trade, strategy: str):"
        DOC LOCATION: Line 505
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "register_sl_recovery" in content, "register_sl_recovery method not found"
    
    def test_23_013_register_tp_continuation_method_exists(self):
        """
        DOC CLAIM: "def register_tp_continuation(self, trade: Trade, tp_price: float):"
        DOC LOCATION: Line 534
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "register_tp_continuation" in content, "register_tp_continuation method not found"
    
    def test_23_014_get_safety_stats_method_exists(self):
        """
        DOC CLAIM: "def get_safety_stats(self) -> Dict[str, Any]:"
        DOC LOCATION: Line 565
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_safety_stats" in content, "get_safety_stats method not found"
    
    # ==================== ATTRIBUTE EXISTENCE TESTS ====================
    
    def test_23_015_config_attribute_exists(self):
        """
        DOC CLAIM: "self.config = config"
        DOC LOCATION: Line 50
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.config" in content, "config attribute not found"
    
    def test_23_016_reentry_manager_attribute_exists(self):
        """
        DOC CLAIM: "self.reentry_manager = reentry_manager"
        DOC LOCATION: Line 51
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "reentry_manager" in content, "reentry_manager attribute not found"
    
    def test_23_017_profit_booking_manager_attribute_exists(self):
        """
        DOC CLAIM: "self.profit_booking_manager = profit_booking_manager"
        DOC LOCATION: Line 52
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "profit_booking_manager" in content, "profit_booking_manager attribute not found"
    
    def test_23_018_mt5_client_attribute_exists(self):
        """
        DOC CLAIM: "self.mt5_client = mt5_client"
        DOC LOCATION: Line 53
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "mt5_client" in content, "mt5_client attribute not found"
    
    def test_23_019_active_recoveries_attribute_exists(self):
        """
        DOC CLAIM: "self.active_recoveries: Dict[str, Dict] = {}"
        DOC LOCATION: Line 58
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "active_recoveries" in content, "active_recoveries attribute not found"
    
    def test_23_020_daily_stats_attribute_exists(self):
        """
        DOC CLAIM: "self.daily_stats = {...}"
        DOC LOCATION: Line 61
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "daily_stats" in content, "daily_stats attribute not found"
    
    def test_23_021_reverse_shields_attribute_exists(self):
        """
        DOC CLAIM: "self.reverse_shields: Dict[str, Dict] = {}"
        DOC LOCATION: Line 70
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "reverse_shields" in content, "reverse_shields attribute not found"
    
    def test_23_022_autonomous_config_attribute_exists(self):
        """
        DOC CLAIM: "self.autonomous_config = config.get('re_entry_config', {}).get('autonomous_config', {})"
        DOC LOCATION: Line 73
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "autonomous_config" in content, "autonomous_config attribute not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_23_023_logging_import_exists(self):
        """
        DOC CLAIM: AutonomousSystemManager uses logging
        DOC LOCATION: Line 55
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "logging" in content or "logger" in content, "logging import not found"
    
    def test_23_024_datetime_import_exists(self):
        """
        DOC CLAIM: AutonomousSystemManager uses datetime
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "datetime" in content, "datetime import not found"
    
    def test_23_025_typing_import_exists(self):
        """
        DOC CLAIM: AutonomousSystemManager uses typing
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "from typing import" in content or "Dict" in content, "typing import not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
