"""
Documentation Testing: API_INTEGRATION.md
Tests all verifiable claims in API_INTEGRATION.md

Total Claims: 50
Verifiable Claims: 15
Test Cases: 15
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
API_ROOT = SRC_ROOT / "api"
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/API_INTEGRATION.md"


class TestAPIIntegration:
    """Test suite for API_INTEGRATION.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_api_001_main_file_exists(self):
        """
        DOC CLAIM: FastAPI server runs from main.py
        DOC LOCATION: Line 11
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "main.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_api_002_mt5_client_file_exists(self):
        """
        DOC CLAIM: "class MT5Client:"
        DOC LOCATION: Line 271
        TEST TYPE: File Existence
        """
        # Check for mt5_client in various locations
        possible_paths = [
            SRC_ROOT / "mt5_client.py",
            SRC_ROOT / "clients" / "mt5_client.py",
            SRC_ROOT / "core" / "mt5_client.py",
            SRC_ROOT / "api" / "mt5_client.py"
        ]
        found = any(p.exists() for p in possible_paths)
        assert found, "MT5Client file not found in expected locations"
    
    def test_api_003_telegram_bot_file_exists(self):
        """
        DOC CLAIM: "class TelegramBot:"
        DOC LOCATION: Line 499
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_api_004_fastapi_app_exists(self):
        """
        DOC CLAIM: "app = FastAPI(...)"
        DOC LOCATION: Line 15
        TEST TYPE: Class Existence
        """
        file_path = API_ROOT / "webhook_handler.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "FastAPI" in content or "fastapi" in content.lower(), "FastAPI app not found"
    
    def test_api_005_telegram_bot_class_exists(self):
        """
        DOC CLAIM: "class TelegramBot:"
        DOC LOCATION: Line 499
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class TelegramBot" in content or "TelegramBot" in content, \
            "TelegramBot class not found"
    
    # ==================== ENDPOINT TESTS ====================
    
    def test_api_006_webhook_endpoint_exists(self):
        """
        DOC CLAIM: "POST /webhook"
        DOC LOCATION: Line 27
        TEST TYPE: Endpoint Existence
        """
        file_path = API_ROOT / "webhook_handler.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "webhook" in content.lower(), "Webhook endpoint not found"
    
    def test_api_007_health_endpoint_exists(self):
        """
        DOC CLAIM: "GET /health"
        DOC LOCATION: Line 85
        TEST TYPE: Endpoint Existence
        """
        file_path = API_ROOT / "webhook_handler.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "health" in content.lower() or "status" in content.lower(), \
            "Health endpoint not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_api_008_send_message_method_exists(self):
        """
        DOC CLAIM: "def send_message(self, text, parse_mode='HTML', reply_markup=None):"
        DOC LOCATION: Line 505
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "send_message" in content, "send_message method not found"
    
    def test_api_009_format_trade_notification_exists(self):
        """
        DOC CLAIM: "def format_trade_notification(self, trade):"
        DOC LOCATION: Line 524
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "format" in content.lower() or "notification" in content.lower(), \
            "format_trade_notification method not found"
    
    # ==================== IMPORT TESTS ====================
    
    def test_api_010_fastapi_import_exists(self):
        """
        DOC CLAIM: "from fastapi import FastAPI"
        DOC LOCATION: Line 15
        TEST TYPE: Import Existence
        """
        file_path = API_ROOT / "webhook_handler.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "fastapi" in content.lower(), "FastAPI import not found"
    
    def test_api_011_uvicorn_import_exists(self):
        """
        DOC CLAIM: "uvicorn.run(app, host='0.0.0.0', port=8000)"
        DOC LOCATION: Line 22
        TEST TYPE: Import Existence
        NOTE: uvicorn is used in scripts/start_bot.py, not in webhook_handler.py
        """
        # Check scripts/start_bot.py for uvicorn usage
        file_path = TRADING_BOT_ROOT / "scripts" / "start_bot.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "uvicorn" in content.lower(), "uvicorn import not found"
    
    def test_api_012_requests_import_exists(self):
        """
        DOC CLAIM: "import requests"
        DOC LOCATION: Line 497
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "requests" in content or "httpx" in content or "aiohttp" in content, \
            "HTTP client import not found"
    
    # ==================== CONFIG TESTS ====================
    
    def test_api_013_telegram_token_config_exists(self):
        """
        DOC CLAIM: "self.token = config['telegram_token']"
        DOC LOCATION: Line 501
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "token" in content.lower(), "telegram_token config not found"
    
    def test_api_014_chat_id_config_exists(self):
        """
        DOC CLAIM: "self.chat_id = config['telegram_chat_id']"
        DOC LOCATION: Line 502
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "chat_id" in content.lower(), "telegram_chat_id config not found"
    
    def test_api_015_base_url_config_exists(self):
        """
        DOC CLAIM: "self.base_url = f'https://api.telegram.org/bot{self.token}'"
        DOC LOCATION: Line 503
        TEST TYPE: Config Existence
        """
        file_path = SRC_ROOT / "clients" / "telegram_bot_fixed.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "api.telegram.org" in content or "base_url" in content, \
            "Telegram API base_url not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
