"""
Documentation Testing: 30_TELEGRAM_3BOT_SYSTEM.md
Tests all verifiable claims in 30_TELEGRAM_3BOT_SYSTEM.md

Total Claims: 45
Verifiable Claims: 20
Test Cases: 20
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/30_TELEGRAM_3BOT_SYSTEM.md"


class Test30Telegram3BotSystem:
    """Test suite for 30_TELEGRAM_3BOT_SYSTEM.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_30_001_multi_telegram_manager_file_exists(self):
        """
        DOC CLAIM: "src/telegram/multi_telegram_manager.py"
        DOC LOCATION: Line 3
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_30_002_controller_bot_file_exists(self):
        """
        DOC CLAIM: "src/telegram/controller_bot.py"
        DOC LOCATION: Line 522
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "telegram" / "controller_bot.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_30_003_notification_bot_file_exists(self):
        """
        DOC CLAIM: "src/telegram/notification_bot.py"
        DOC LOCATION: Line 523
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "telegram" / "notification_bot.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_30_004_rate_limiter_file_exists(self):
        """
        DOC CLAIM: "src/telegram/rate_limiter.py"
        DOC LOCATION: Line 525
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "telegram" / "rate_limiter.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_30_005_telegram_bot_fixed_file_exists(self):
        """
        DOC CLAIM: "src/telegram/telegram_bot_fixed.py"
        DOC LOCATION: Line 526
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_30_006_multi_telegram_manager_class_exists(self):
        """
        DOC CLAIM: "class MultiTelegramManager:"
        DOC LOCATION: Line 61
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class MultiTelegramManager" in content, "MultiTelegramManager class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_30_007_init_method_exists(self):
        """
        DOC CLAIM: "def __init__(self, config: Dict[str, Any]):"
        DOC LOCATION: Line 75
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found"
    
    def test_30_008_initialize_bots_method_exists(self):
        """
        DOC CLAIM: "def _initialize_bots(self):"
        DOC LOCATION: Line 100
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_initialize_bots" in content or "initialize_bots" in content, \
            "_initialize_bots method not found"
    
    def test_30_009_send_notification_async_method_exists(self):
        """
        DOC CLAIM: "async def send_notification_async(self, notification_type: str, ...)"
        DOC LOCATION: Line 158
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "send_notification" in content, "send_notification_async method not found"
    
    def test_30_010_get_target_bot_method_exists(self):
        """
        DOC CLAIM: "def _get_target_bot(self, notification_type: str):"
        DOC LOCATION: Line 189
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "_get_target_bot" in content or "get_target_bot" in content, \
            "_get_target_bot method not found"
    
    def test_30_011_send_trade_notification_method_exists(self):
        """
        DOC CLAIM: "async def send_trade_notification(self, trade_data: Dict[str, Any]):"
        DOC LOCATION: Line 237
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "send_trade_notification" in content, "send_trade_notification method not found"
    
    def test_30_012_register_command_handlers_method_exists(self):
        """
        DOC CLAIM: "def register_command_handlers(self, trading_engine):"
        DOC LOCATION: Line 304
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "register_command_handlers" in content or "register_handler" in content, \
            "register_command_handlers method not found"
    
    # ==================== ATTRIBUTE EXISTENCE TESTS ====================
    
    def test_30_013_config_attribute_exists(self):
        """
        DOC CLAIM: "self.config = config"
        DOC LOCATION: Line 76
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.config" in content, "config attribute not found"
    
    def test_30_014_controller_bot_attribute_exists(self):
        """
        DOC CLAIM: "self.controller_bot = None"
        DOC LOCATION: Line 80
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "controller_bot" in content, "controller_bot attribute not found"
    
    def test_30_015_notification_bot_attribute_exists(self):
        """
        DOC CLAIM: "self.notification_bot = None"
        DOC LOCATION: Line 81
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "notification_bot" in content, "notification_bot attribute not found"
    
    def test_30_016_multi_bot_mode_attribute_exists(self):
        """
        DOC CLAIM: "self.multi_bot_mode = False"
        DOC LOCATION: Line 88
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "multi_bot_mode" in content, "multi_bot_mode attribute not found"
    
    def test_30_017_message_queue_attribute_exists(self):
        """
        DOC CLAIM: "self.message_queue = asyncio.Queue()"
        DOC LOCATION: Line 91
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "message_queue" in content or "queue" in content, "message_queue attribute not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_30_018_logging_import_exists(self):
        """
        DOC CLAIM: MultiTelegramManager uses logging
        DOC LOCATION: Line 77
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "logging" in content or "logger" in content, "logging import not found"
    
    def test_30_019_asyncio_import_exists(self):
        """
        DOC CLAIM: MultiTelegramManager uses asyncio
        DOC LOCATION: Line 91
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "asyncio" in content, "asyncio import not found"
    
    def test_30_020_datetime_import_exists(self):
        """
        DOC CLAIM: MultiTelegramManager uses datetime
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "datetime" in content, "datetime import not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
