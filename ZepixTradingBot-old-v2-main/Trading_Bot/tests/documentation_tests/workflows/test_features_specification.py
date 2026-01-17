"""
Documentation Testing: FEATURES_SPECIFICATION.md
Tests all verifiable claims in FEATURES_SPECIFICATION.md

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
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/FEATURES_SPECIFICATION.md"


class TestFeaturesSpecification:
    """Test suite for FEATURES_SPECIFICATION.md"""
    
    # ==================== CORE FEATURE TESTS ====================
    
    def test_features_001_dual_order_system_exists(self):
        """
        DOC CLAIM: Dual Order System feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "managers" / "dual_order_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_features_002_reentry_system_exists(self):
        """
        DOC CLAIM: Re-Entry System feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "managers" / "reentry_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_features_003_profit_booking_system_exists(self):
        """
        DOC CLAIM: Profit Booking System feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "managers" / "profit_booking_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_features_004_risk_management_exists(self):
        """
        DOC CLAIM: Risk Management feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "managers" / "risk_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_features_005_telegram_integration_exists(self):
        """
        DOC CLAIM: Telegram Integration feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "telegram" / "multi_telegram_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== PLUGIN FEATURE TESTS ====================
    
    def test_features_006_v3_plugin_exists(self):
        """
        DOC CLAIM: V3 Combined Plugin feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "logic_plugins" / "v3_combined" / "plugin.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_features_007_v6_plugins_exist(self):
        """
        DOC CLAIM: V6 Price Action Plugins feature
        TEST TYPE: Feature Existence
        """
        v6_dirs = [
            SRC_ROOT / "logic_plugins" / "v6_price_action_1m",
            SRC_ROOT / "logic_plugins" / "v6_price_action_5m",
            SRC_ROOT / "logic_plugins" / "v6_price_action_15m",
            SRC_ROOT / "logic_plugins" / "v6_price_action_1h"
        ]
        found = sum(1 for d in v6_dirs if d.exists())
        assert found >= 1, "No V6 plugins found"
    
    def test_features_008_shadow_mode_exists(self):
        """
        DOC CLAIM: Shadow Mode feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "core" / "shadow_mode_manager.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== SYSTEM FEATURE TESTS ====================
    
    def test_features_009_voice_alerts_exist(self):
        """
        DOC CLAIM: Voice Alerts feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "modules" / "voice_alert_system.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_features_010_config_hot_reload_exists(self):
        """
        DOC CLAIM: Config Hot-Reload feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "core" / "config_manager.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "reload" in content.lower() or "watch" in content.lower(), \
            "Config hot-reload not found"
    
    def test_features_011_database_isolation_exists(self):
        """
        DOC CLAIM: Database Isolation feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "database.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== INTEGRATION FEATURE TESTS ====================
    
    def test_features_012_mt5_integration_exists(self):
        """
        DOC CLAIM: MT5 Integration feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "core" / "trading_engine.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "mt5" in content.lower(), "MT5 integration not found"
    
    def test_features_013_tradingview_integration_exists(self):
        """
        DOC CLAIM: TradingView Integration feature
        TEST TYPE: Feature Existence
        """
        file_path = API_ROOT / "webhook_handler.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "webhook" in content.lower(), "TradingView integration not found"
    
    def test_features_014_service_api_exists(self):
        """
        DOC CLAIM: ServiceAPI feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    def test_features_015_plugin_registry_exists(self):
        """
        DOC CLAIM: Plugin Registry feature
        TEST TYPE: Feature Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "plugin_registry.py"
        assert file_path.exists(), f"File not found: {file_path}"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
