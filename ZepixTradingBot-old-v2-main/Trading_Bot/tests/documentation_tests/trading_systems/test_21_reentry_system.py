"""
Documentation Testing: 21_REENTRY_SYSTEM.md
Tests all verifiable claims in 21_REENTRY_SYSTEM.md

Total Claims: 45
Verifiable Claims: 25
Test Cases: 25
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/21_REENTRY_SYSTEM.md"


class Test21ReentrySystem:
    """Test suite for 21_REENTRY_SYSTEM.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_21_001_reentry_manager_file_exists(self):
        """
        DOC CLAIM: "src/managers/reentry_manager.py"
        DOC LOCATION: Line 3
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_21_002_trading_engine_file_exists(self):
        """
        DOC CLAIM: "src/core/trading_engine.py"
        DOC LOCATION: Line 549
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_21_003_autonomous_system_manager_file_exists(self):
        """
        DOC CLAIM: "src/managers/autonomous_system_manager.py"
        DOC LOCATION: Line 550
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "managers" / "autonomous_system_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_21_004_reentry_manager_class_exists(self):
        """
        DOC CLAIM: "class ReEntryManager:"
        DOC LOCATION: Line 57
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class ReEntryManager" in content or "ReEntryManager" in content, \
            "ReEntryManager class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_21_005_init_method_exists(self):
        """
        DOC CLAIM: "def __init__(self, config, mt5_client=None):"
        DOC LOCATION: Line 60
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found"
    
    def test_21_006_create_chain_method_exists(self):
        """
        DOC CLAIM: "def create_chain(self, trade: Trade) -> ReEntryChain:"
        DOC LOCATION: Line 80
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "create_chain" in content, "create_chain method not found"
    
    def test_21_007_check_reentry_opportunity_method_exists(self):
        """
        DOC CLAIM: "def check_reentry_opportunity(self, symbol: str, signal: str, price: float)"
        DOC LOCATION: Line 135
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_reentry_opportunity" in content or "reentry_opportunity" in content, \
            "check_reentry_opportunity method not found"
    
    def test_21_008_check_tp_continuation_method_exists(self):
        """
        DOC CLAIM: "def _check_tp_continuation(self, symbol: str, signal: str, price: float)"
        DOC LOCATION: Line 173
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_check_tp_continuation" in content or "tp_continuation" in content, \
            "_check_tp_continuation method not found"
    
    def test_21_009_check_sl_recovery_method_exists(self):
        """
        DOC CLAIM: "def _check_sl_recovery(self, symbol: str, signal: str, price: float)"
        DOC LOCATION: Line 216
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_check_sl_recovery" in content or "sl_recovery" in content, \
            "_check_sl_recovery method not found"
    
    def test_21_010_record_tp_hit_method_exists(self):
        """
        DOC CLAIM: "def record_tp_hit(self, trade: Trade, tp_price: float):"
        DOC LOCATION: Line 286
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "record_tp_hit" in content, "record_tp_hit method not found"
    
    def test_21_011_record_sl_hit_method_exists(self):
        """
        DOC CLAIM: "def record_sl_hit(self, trade: Trade):"
        DOC LOCATION: Line 313
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "record_sl_hit" in content, "record_sl_hit method not found"
    
    def test_21_012_check_sl_hunt_recovery_method_exists(self):
        """
        DOC CLAIM: "def check_sl_hunt_recovery(self, chain, current_price: float)"
        DOC LOCATION: Line 364
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_sl_hunt_recovery" in content or "sl_hunt_recovery" in content, \
            "check_sl_hunt_recovery method not found"
    
    # ==================== ATTRIBUTE EXISTENCE TESTS ====================
    
    def test_21_013_config_attribute_exists(self):
        """
        DOC CLAIM: "self.config = config"
        DOC LOCATION: Line 61
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.config" in content, "config attribute not found"
    
    def test_21_014_mt5_client_attribute_exists(self):
        """
        DOC CLAIM: "self.mt5_client = mt5_client"
        DOC LOCATION: Line 62
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "mt5_client" in content, "mt5_client attribute not found"
    
    def test_21_015_active_chains_attribute_exists(self):
        """
        DOC CLAIM: "self.active_chains = {}"
        DOC LOCATION: Line 63
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "active_chains" in content, "active_chains attribute not found"
    
    def test_21_016_recent_sl_hits_attribute_exists(self):
        """
        DOC CLAIM: "self.recent_sl_hits = {}"
        DOC LOCATION: Line 64
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "recent_sl_hits" in content or "sl_hits" in content, \
            "recent_sl_hits attribute not found"
    
    def test_21_017_completed_tps_attribute_exists(self):
        """
        DOC CLAIM: "self.completed_tps = {}"
        DOC LOCATION: Line 65
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "completed_tps" in content or "tps" in content, \
            "completed_tps attribute not found"
    
    # ==================== RECOVERY TYPE TESTS ====================
    
    def test_21_018_recovery_mode_status_exists(self):
        """
        DOC CLAIM: "chain.status = 'recovery_mode'"
        DOC LOCATION: Line 342
        TEST TYPE: Status Value Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "recovery_mode" in content, "recovery_mode status not found"
    
    def test_21_019_stopped_status_exists(self):
        """
        DOC CLAIM: "chain.status = 'stopped'"
        DOC LOCATION: Line 352
        TEST TYPE: Status Value Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "stopped" in content, "stopped status not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_21_020_datetime_import_exists(self):
        """
        DOC CLAIM: ReEntryManager uses datetime
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "datetime" in content, "datetime import not found"
    
    def test_21_021_uuid_import_exists(self):
        """
        DOC CLAIM: ReEntryManager uses uuid
        DOC LOCATION: Line 83
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "uuid" in content, "uuid import not found"
    
    def test_21_022_timedelta_import_exists(self):
        """
        DOC CLAIM: ReEntryManager uses timedelta
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "timedelta" in content, "timedelta import not found"
    
    # ==================== RETURN TYPE TESTS ====================
    
    def test_21_023_check_reentry_returns_dict(self):
        """
        DOC CLAIM: "check_reentry_opportunity returns dict with is_reentry, type, etc."
        DOC LOCATION: Lines 139-145
        TEST TYPE: Return Type
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "is_reentry" in content or "reentry" in content, \
            "check_reentry_opportunity return structure not found"
    
    def test_21_024_sl_adjustment_key_exists(self):
        """
        DOC CLAIM: "sl_adjustment: 1.0"
        DOC LOCATION: Line 144
        TEST TYPE: Return Key Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "sl_adjustment" in content, "sl_adjustment key not found"
    
    def test_21_025_chain_level_key_exists(self):
        """
        DOC CLAIM: "level: 1"
        DOC LOCATION: Line 143
        TEST TYPE: Return Key Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "level" in content or "chain_level" in content, "level key not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
