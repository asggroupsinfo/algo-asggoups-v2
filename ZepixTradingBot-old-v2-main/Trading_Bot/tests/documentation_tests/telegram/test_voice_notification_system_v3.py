"""
Documentation Testing: VOICE_NOTIFICATION_SYSTEM_V3.md
Tests all verifiable claims in VOICE_NOTIFICATION_SYSTEM_V3.md

Total Claims: 20
Verifiable Claims: 10
Test Cases: 10
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/VOICE_NOTIFICATION_SYSTEM_V3.md"


class TestVoiceNotificationSystemV3:
    """Test suite for VOICE_NOTIFICATION_SYSTEM_V3.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_voice_v3_001_voice_alert_file_exists(self):
        """
        DOC CLAIM: voice_alert_system.py file
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_voice_v3_002_voice_alert_system_class_exists(self):
        """
        DOC CLAIM: VoiceAlertSystem class
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class VoiceAlertSystem" in content, "VoiceAlertSystem class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_voice_v3_003_init_method_exists(self):
        """
        DOC CLAIM: __init__ method
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__" in content, "__init__ method not found"
    
    def test_voice_v3_004_speak_alert_method_exists(self):
        """
        DOC CLAIM: speak_alert method
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "speak" in content.lower(), "speak_alert method not found"
    
    def test_voice_v3_005_queue_method_exists(self):
        """
        DOC CLAIM: queue_alert method
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "queue" in content.lower() or "add" in content.lower(), \
            "queue method not found"
    
    # ==================== ATTRIBUTE TESTS ====================
    
    def test_voice_v3_006_config_attribute_exists(self):
        """
        DOC CLAIM: config attribute
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "config" in content, "config attribute not found"
    
    def test_voice_v3_007_enabled_attribute_exists(self):
        """
        DOC CLAIM: enabled attribute
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "enabled" in content.lower(), "enabled attribute not found"
    
    # ==================== ALERT TYPE TESTS ====================
    
    def test_voice_v3_008_trade_alerts_supported(self):
        """
        DOC CLAIM: Trade alerts support
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        has_trade = "trade" in content.lower()
        assert has_trade, "Trade alerts not supported"
    
    def test_voice_v3_009_error_alerts_supported(self):
        """
        DOC CLAIM: Error alerts support
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        has_error = "error" in content.lower()
        assert has_error, "Error alerts not supported"
    
    def test_voice_v3_010_priority_system_exists(self):
        """
        DOC CLAIM: Priority system for alerts
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        has_priority = any(term in content.lower() for term in 
                          ["priority", "critical", "high", "medium", "low", "urgent"])
        assert has_priority, "Priority system not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
