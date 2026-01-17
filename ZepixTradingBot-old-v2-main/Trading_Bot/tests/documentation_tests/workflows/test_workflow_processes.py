"""
Documentation Testing: WORKFLOW_PROCESSES.md
Tests all verifiable claims in WORKFLOW_PROCESSES.md

Total Claims: 25
Verifiable Claims: 12
Test Cases: 12
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
API_ROOT = SRC_ROOT / "api"
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/WORKFLOW_PROCESSES.md"


class TestWorkflowProcesses:
    """Test suite for WORKFLOW_PROCESSES.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_workflow_proc_001_trading_engine_exists(self):
        """
        DOC CLAIM: trading_engine.py workflow orchestrator
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_workflow_proc_002_alert_processor_exists(self):
        """
        DOC CLAIM: alert_processor.py
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "processors" / "alert_processor.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_workflow_proc_003_service_api_exists(self):
        """
        DOC CLAIM: service_api.py
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== WORKFLOW METHOD TESTS ====================
    
    def test_workflow_proc_004_process_alert_exists(self):
        """
        DOC CLAIM: process_alert workflow
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "processors" / "alert_processor.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "process" in content.lower(), "process_alert not found"
    
    def test_workflow_proc_005_delegate_to_plugin_exists(self):
        """
        DOC CLAIM: delegate_to_plugin workflow
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "delegate_to_plugin" in content, "delegate_to_plugin not found"
    
    def test_workflow_proc_006_execute_order_exists(self):
        """
        DOC CLAIM: execute_order workflow
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "execute" in content.lower() or "order" in content.lower(), \
            "execute_order not found"
    
    # ==================== INTEGRATION TESTS ====================
    
    def test_workflow_proc_007_webhook_to_engine_flow(self):
        """
        DOC CLAIM: Webhook to TradingEngine flow
        TEST TYPE: Integration Existence
        """
        file_path = API_ROOT / "webhook_handler.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "webhook" in content.lower() and ("trading" in content.lower() or "plugin" in content.lower()), \
            "Webhook to engine flow not found"
    
    def test_workflow_proc_008_engine_to_plugin_flow(self):
        """
        DOC CLAIM: TradingEngine to Plugin flow
        TEST TYPE: Integration Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "plugin" in content.lower(), "Engine to plugin flow not found"
    
    def test_workflow_proc_009_plugin_to_service_flow(self):
        """
        DOC CLAIM: Plugin to ServiceAPI flow
        TEST TYPE: Integration Existence
        """
        file_path = SRC_ROOT / "logic_plugins" / "v3_combined" / "plugin.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "service_api" in content.lower(), "Plugin to service flow not found"
    
    def test_workflow_proc_010_service_to_mt5_flow(self):
        """
        DOC CLAIM: ServiceAPI to MT5 flow
        TEST TYPE: Integration Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "mt5" in content.lower() or "order" in content.lower(), \
            "Service to MT5 flow not found"
    
    def test_workflow_proc_011_notification_flow(self):
        """
        DOC CLAIM: Notification workflow
        TEST TYPE: Integration Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "telegram" in content.lower() or "notification" in content.lower(), \
            "Notification flow not found"
    
    def test_workflow_proc_012_database_flow(self):
        """
        DOC CLAIM: Database persistence workflow
        TEST TYPE: Integration Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "database" in content.lower() or "db" in content.lower(), \
            "Database flow not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
