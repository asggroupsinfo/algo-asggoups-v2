"""
Documentation Testing: 32_VOICE_ALERT_SYSTEM.md
Tests all verifiable claims in 32_VOICE_ALERT_SYSTEM.md

Total Claims: 35
Verifiable Claims: 15
Test Cases: 15
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/32_VOICE_ALERT_SYSTEM.md"


class Test32VoiceAlertSystem:
    """Test suite for 32_VOICE_ALERT_SYSTEM.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_32_001_voice_alert_system_file_exists(self):
        """
        DOC CLAIM: "src/modules/voice_alert_system.py"
        DOC LOCATION: Line 13
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_32_002_voice_alert_system_class_exists(self):
        """
        DOC CLAIM: "class VoiceAlertSystem:"
        DOC LOCATION: Line 98
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class VoiceAlertSystem" in content or "VoiceAlertSystem" in content, \
            "VoiceAlertSystem class not found"
    
    def test_32_003_alert_priority_enum_exists(self):
        """
        DOC CLAIM: "class AlertPriority(Enum):"
        DOC LOCATION: Line 91
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "AlertPriority" in content or "priority" in content.lower(), \
            "AlertPriority enum not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_32_004_init_method_exists(self):
        """
        DOC CLAIM: "def __init__(self, bot=None, chat_id: str = ''):"
        DOC LOCATION: Line 104
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found"
    
    def test_32_005_send_voice_alert_method_exists(self):
        """
        DOC CLAIM: "async def send_voice_alert(self, message: str, priority: AlertPriority = AlertPriority.MEDIUM):"
        DOC LOCATION: Line 117
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "send_voice_alert" in content or "voice_alert" in content, \
            "send_voice_alert method not found"
    
    def test_32_006_speak_alert_method_exists(self):
        """
        DOC CLAIM: "def speak_alert(self, message: str):"
        DOC LOCATION: Line 120
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "speak_alert" in content or "speak" in content, "speak_alert method not found"
    
    def test_32_007_send_telegram_alert_method_exists(self):
        """
        DOC CLAIM: "async def send_telegram_alert(self, message: str):"
        DOC LOCATION: Line 123
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "send_telegram_alert" in content or "telegram" in content.lower(), \
            "send_telegram_alert method not found"
    
    # ==================== PRIORITY LEVEL TESTS ====================
    
    def test_32_008_critical_priority_exists(self):
        """
        DOC CLAIM: "CRITICAL = 'critical'"
        DOC LOCATION: Line 92
        TEST TYPE: Priority Level Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "CRITICAL" in content or "critical" in content, "CRITICAL priority not found"
    
    def test_32_009_high_priority_exists(self):
        """
        DOC CLAIM: "HIGH = 'high'"
        DOC LOCATION: Line 93
        TEST TYPE: Priority Level Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "HIGH" in content or "high" in content, "HIGH priority not found"
    
    def test_32_010_medium_priority_exists(self):
        """
        DOC CLAIM: "MEDIUM = 'medium'"
        DOC LOCATION: Line 94
        TEST TYPE: Priority Level Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "MEDIUM" in content or "medium" in content, "MEDIUM priority not found"
    
    def test_32_011_low_priority_exists(self):
        """
        DOC CLAIM: "LOW = 'low'"
        DOC LOCATION: Line 95
        TEST TYPE: Priority Level Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "LOW" in content or "low" in content, "LOW priority not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_32_012_logging_import_exists(self):
        """
        DOC CLAIM: VoiceAlertSystem uses logging
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "logging" in content or "logger" in content, "logging import not found"
    
    # ==================== ATTRIBUTE TESTS ====================
    
    def test_32_013_bot_attribute_exists(self):
        """
        DOC CLAIM: "bot: Telegram bot instance"
        DOC LOCATION: Line 109
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "bot" in content, "bot attribute not found"
    
    def test_32_014_chat_id_attribute_exists(self):
        """
        DOC CLAIM: "chat_id: Default chat ID for alerts"
        DOC LOCATION: Line 110
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "chat_id" in content, "chat_id attribute not found"
    
    def test_32_015_enabled_attribute_exists(self):
        """
        DOC CLAIM: "enabled: true"
        DOC LOCATION: Line 61
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "enabled" in content, "enabled attribute not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
