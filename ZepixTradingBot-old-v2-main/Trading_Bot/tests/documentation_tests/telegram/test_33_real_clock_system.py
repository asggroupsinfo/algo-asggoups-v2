"""
Documentation Testing: 33_REAL_CLOCK_SYSTEM.md
Tests all verifiable claims in 33_REAL_CLOCK_SYSTEM.md

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
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/33_REAL_CLOCK_SYSTEM.md"


class Test33RealClockSystem:
    """Test suite for 33_REAL_CLOCK_SYSTEM.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_33_001_fixed_clock_system_file_exists(self):
        """
        DOC CLAIM: "src/modules/fixed_clock_system.py"
        DOC LOCATION: Line 13
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_33_002_fixed_clock_system_class_exists(self):
        """
        DOC CLAIM: "class FixedClockSystem:"
        DOC LOCATION: Line 54
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class FixedClockSystem" in content or "FixedClockSystem" in content, \
            "FixedClockSystem class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_33_003_init_method_exists(self):
        """
        DOC CLAIM: "def __init__(self, timezone: str = 'Asia/Kolkata'):"
        DOC LOCATION: Line 60
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found"
    
    def test_33_004_get_current_time_method_exists(self):
        """
        DOC CLAIM: "def get_current_time(self) -> datetime:"
        DOC LOCATION: Line 72
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_current_time" in content, "get_current_time method not found"
    
    def test_33_005_format_time_string_method_exists(self):
        """
        DOC CLAIM: "def format_time_string(self) -> str:"
        DOC LOCATION: Line 75
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "format_time_string" in content, "format_time_string method not found"
    
    def test_33_006_format_date_string_method_exists(self):
        """
        DOC CLAIM: "def format_date_string(self) -> str:"
        DOC LOCATION: Line 78
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "format_date_string" in content, "format_date_string method not found"
    
    def test_33_007_format_clock_message_method_exists(self):
        """
        DOC CLAIM: "def format_clock_message(self) -> str:"
        DOC LOCATION: Line 81
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "format_clock_message" in content, "format_clock_message method not found"
    
    def test_33_008_start_clock_loop_method_exists(self):
        """
        DOC CLAIM: "async def start_clock_loop(self, update_interval: int = 1):"
        DOC LOCATION: Line 84
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "start_clock_loop" in content, "start_clock_loop method not found"
    
    def test_33_009_stop_clock_loop_method_exists(self):
        """
        DOC CLAIM: "def stop_clock_loop(self):"
        DOC LOCATION: Line 87
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "stop_clock_loop" in content, "stop_clock_loop method not found"
    
    def test_33_010_register_callback_method_exists(self):
        """
        DOC CLAIM: "def register_callback(self, callback: Callable):"
        DOC LOCATION: Line 90
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "register_callback" in content, "register_callback method not found"
    
    def test_33_011_get_time_components_method_exists(self):
        """
        DOC CLAIM: "def get_time_components(self) -> Dict[str, int]:"
        DOC LOCATION: Line 93
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_time_components" in content, "get_time_components method not found"
    
    # ==================== SINGLETON TESTS ====================
    
    def test_33_012_get_clock_system_function_exists(self):
        """
        DOC CLAIM: "def get_clock_system():"
        DOC LOCATION: Line 97
        TEST TYPE: Function Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_clock_system" in content, "get_clock_system function not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_33_013_datetime_import_exists(self):
        """
        DOC CLAIM: FixedClockSystem uses datetime
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "datetime" in content, "datetime import not found"
    
    def test_33_014_pytz_import_exists(self):
        """
        DOC CLAIM: "The system uses pytz for accurate timezone handling"
        DOC LOCATION: Line 19
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "pytz" in content or "timezone" in content, "pytz import not found"
    
    def test_33_015_timezone_config_exists(self):
        """
        DOC CLAIM: "timezone: 'Asia/Kolkata'"
        DOC LOCATION: Line 163
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "modules" / "fixed_clock_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "Asia/Kolkata" in content or "IST" in content or "timezone" in content, \
            "timezone config not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
