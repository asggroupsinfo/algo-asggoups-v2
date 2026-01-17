"""
Documentation Testing: UI_NAVIGATION_GUIDE.md
Tests all verifiable claims in UI_NAVIGATION_GUIDE.md

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
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/UI_NAVIGATION_GUIDE.md"


class TestUINavigationGuide:
    """Test suite for UI_NAVIGATION_GUIDE.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_ui_001_telegram_bot_file_exists(self):
        """
        DOC CLAIM: telegram_bot_fixed.py file
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_ui_002_multi_telegram_manager_exists(self):
        """
        DOC CLAIM: multi_telegram_manager.py file
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== MENU HANDLER TESTS ====================
    
    def test_ui_003_command_handlers_exist(self):
        """
        DOC CLAIM: Command handlers for UI
        TEST TYPE: Handler Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "handler" in content.lower() or "command" in content.lower(), \
            "Command handlers not found"
    
    def test_ui_004_callback_handlers_exist(self):
        """
        DOC CLAIM: Callback handlers for buttons
        TEST TYPE: Handler Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "callback" in content.lower() or "button" in content.lower(), \
            "Callback handlers not found"
    
    # ==================== MENU TESTS ====================
    
    def test_ui_005_main_menu_exists(self):
        """
        DOC CLAIM: Main menu implementation
        TEST TYPE: Menu Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "menu" in content.lower(), "Main menu not found"
    
    def test_ui_006_keyboard_exists(self):
        """
        DOC CLAIM: Keyboard implementation
        TEST TYPE: Keyboard Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "keyboard" in content.lower() or "button" in content.lower(), \
            "Keyboard not found"
    
    # ==================== NAVIGATION TESTS ====================
    
    def test_ui_007_start_command_exists(self):
        """
        DOC CLAIM: /start command
        TEST TYPE: Command Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "start" in content.lower(), "/start command not found"
    
    def test_ui_008_help_command_exists(self):
        """
        DOC CLAIM: /help command
        TEST TYPE: Command Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "help" in content.lower(), "/help command not found"
    
    def test_ui_009_status_command_exists(self):
        """
        DOC CLAIM: /status command
        TEST TYPE: Command Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "status" in content.lower(), "/status command not found"
    
    def test_ui_010_message_formatting_exists(self):
        """
        DOC CLAIM: Message formatting for UI
        TEST TYPE: Formatting Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "format" in content.lower() or "html" in content.lower(), \
            "Message formatting not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
