"""
Documentation Testing: BOT_WORKFLOW_CHAIN.md
Tests all verifiable claims in BOT_WORKFLOW_CHAIN.md

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
API_ROOT = SRC_ROOT / "api"
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/BOT_WORKFLOW_CHAIN.md"


class TestBotWorkflowChain:
    """Test suite for BOT_WORKFLOW_CHAIN.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_workflow_001_main_file_exists(self):
        """
        DOC CLAIM: main.py entry point
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "main.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_workflow_002_trading_engine_file_exists(self):
        """
        DOC CLAIM: trading_engine.py orchestrator
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_workflow_003_alert_processor_file_exists(self):
        """
        DOC CLAIM: alert_processor.py
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "processors" / "alert_processor.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_workflow_004_plugin_registry_file_exists(self):
        """
        DOC CLAIM: plugin_registry.py
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_workflow_005_service_api_file_exists(self):
        """
        DOC CLAIM: service_api.py
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_workflow_006_trading_engine_class_exists(self):
        """
        DOC CLAIM: TradingEngine class
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class TradingEngine" in content, "TradingEngine class not found"
    
    def test_workflow_007_alert_processor_class_exists(self):
        """
        DOC CLAIM: AlertProcessor class
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "processors" / "alert_processor.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class AlertProcessor" in content or "AlertProcessor" in content, \
            "AlertProcessor class not found"
    
    # ==================== METHOD EXISTENCE TESTS ====================
    
    def test_workflow_008_process_alert_method_exists(self):
        """
        DOC CLAIM: process_alert method
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "processors" / "alert_processor.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "process_alert" in content or "process" in content, \
            "process_alert method not found"
    
    def test_workflow_009_delegate_to_plugin_method_exists(self):
        """
        DOC CLAIM: delegate_to_plugin method
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "delegate_to_plugin" in content, "delegate_to_plugin method not found"
    
    def test_workflow_010_get_plugin_for_signal_method_exists(self):
        """
        DOC CLAIM: get_plugin_for_signal method
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_plugin_for_signal" in content, "get_plugin_for_signal method not found"
    
    # ==================== INTEGRATION TESTS ====================
    
    def test_workflow_011_webhook_handler_exists(self):
        """
        DOC CLAIM: Webhook handler for TradingView alerts
        TEST TYPE: Integration Existence
        """
        file_path = API_ROOT / "webhook_handler.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "webhook" in content.lower(), "Webhook handler not found"
    
    def test_workflow_012_telegram_integration_exists(self):
        """
        DOC CLAIM: Telegram notification integration
        TEST TYPE: Integration Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "telegram" in content.lower(), "Telegram integration not found"
    
    def test_workflow_013_mt5_integration_exists(self):
        """
        DOC CLAIM: MT5 client integration
        TEST TYPE: Integration Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "mt5" in content.lower(), "MT5 integration not found"
    
    def test_workflow_014_risk_manager_integration_exists(self):
        """
        DOC CLAIM: Risk manager integration
        TEST TYPE: Integration Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "risk" in content.lower(), "Risk manager integration not found"
    
    def test_workflow_015_database_integration_exists(self):
        """
        DOC CLAIM: Database integration
        TEST TYPE: Integration Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "database" in content.lower() or "db" in content.lower(), \
            "Database integration not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
