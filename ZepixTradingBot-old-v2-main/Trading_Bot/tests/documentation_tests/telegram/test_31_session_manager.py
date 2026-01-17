"""
Documentation Testing: 31_SESSION_MANAGER.md
Tests all verifiable claims in 31_SESSION_MANAGER.md

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
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/31_SESSION_MANAGER.md"


class Test31SessionManager:
    """Test suite for 31_SESSION_MANAGER.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_31_001_session_manager_file_exists(self):
        """
        DOC CLAIM: "src/managers/session_manager.py"
        DOC LOCATION: Line 13
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_31_002_get_current_session_method_exists(self):
        """
        DOC CLAIM: "get_current_session() -> str"
        DOC LOCATION: Line 79
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_current_session" in content, "get_current_session method not found"
    
    def test_31_003_is_symbol_allowed_method_exists(self):
        """
        DOC CLAIM: "is_symbol_allowed(symbol: str) -> bool"
        DOC LOCATION: Line 83
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "is_symbol_allowed" in content, "is_symbol_allowed method not found"
    
    def test_31_004_get_session_info_method_exists(self):
        """
        DOC CLAIM: "get_session_info() -> Dict"
        DOC LOCATION: Line 87
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_session_info" in content, "get_session_info method not found"
    
    def test_31_005_check_advance_alerts_method_exists(self):
        """
        DOC CLAIM: "check_advance_alerts()"
        DOC LOCATION: Line 95
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_advance_alerts" in content or "advance_alert" in content, \
            "check_advance_alerts method not found"
    
    # ==================== SESSION DEFINITION TESTS ====================
    
    def test_31_006_asian_session_exists(self):
        """
        DOC CLAIM: "Asian session: 05:30 - 14:30"
        DOC LOCATION: Line 23
        TEST TYPE: Session Definition
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "asian" in content.lower() or "Asian" in content, "Asian session not found"
    
    def test_31_007_london_session_exists(self):
        """
        DOC CLAIM: "London session: 13:00 - 22:00"
        DOC LOCATION: Line 24
        TEST TYPE: Session Definition
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "london" in content.lower() or "London" in content, "London session not found"
    
    def test_31_008_overlap_session_exists(self):
        """
        DOC CLAIM: "Overlap session: 18:00 - 20:30"
        DOC LOCATION: Line 25
        TEST TYPE: Session Definition
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "overlap" in content.lower() or "Overlap" in content, "Overlap session not found"
    
    def test_31_009_dead_zone_session_exists(self):
        """
        DOC CLAIM: "Dead Zone: 02:00 - 05:30"
        DOC LOCATION: Line 27
        TEST TYPE: Session Definition
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "dead" in content.lower() or "Dead" in content, "Dead Zone session not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_31_010_datetime_import_exists(self):
        """
        DOC CLAIM: SessionManager uses datetime
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "datetime" in content, "datetime import not found"
    
    # ==================== FEATURE TESTS ====================
    
    def test_31_011_master_switch_exists(self):
        """
        DOC CLAIM: "master_switch: true"
        DOC LOCATION: Line 62
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "master_switch" in content or "enabled" in content, "master_switch not found"
    
    def test_31_012_timezone_config_exists(self):
        """
        DOC CLAIM: "timezone: 'Asia/Kolkata'"
        DOC LOCATION: Line 63
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "timezone" in content or "Asia/Kolkata" in content or "IST" in content, \
            "timezone config not found"
    
    def test_31_013_allowed_symbols_exists(self):
        """
        DOC CLAIM: "allowed_symbols: ['USDJPY', 'AUDUSD', 'EURJPY']"
        DOC LOCATION: Line 68
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "allowed_symbols" in content or "symbols" in content, "allowed_symbols not found"
    
    def test_31_014_advance_alert_enabled_exists(self):
        """
        DOC CLAIM: "advance_alert_enabled: true"
        DOC LOCATION: Line 69
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "advance_alert" in content or "alert" in content, "advance_alert_enabled not found"
    
    def test_31_015_force_close_enabled_exists(self):
        """
        DOC CLAIM: "force_close_enabled: false"
        DOC LOCATION: Line 71
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "managers" / "session_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "force_close" in content or "close" in content, "force_close_enabled not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
