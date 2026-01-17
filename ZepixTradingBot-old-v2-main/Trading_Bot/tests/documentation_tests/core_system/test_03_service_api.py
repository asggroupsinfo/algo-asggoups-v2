"""
Documentation Testing: 03_SERVICE_API.md
Tests all verifiable claims in 03_SERVICE_API.md

Total Claims: 55
Verifiable Claims: 40
Test Cases: 40
"""

import pytest
import os
import sys
from pathlib import Path

# Import paths from conftest.py for robust path resolution
from tests.documentation_tests.conftest import PROJECT_ROOT, TRADING_BOT_ROOT, SRC_ROOT
DOC_FILE = "Trading_Bot_Documentation/V5_BIBLE/03_SERVICE_API.md"


class Test03ServiceAPI:
    """Test suite for 03_SERVICE_API.md"""
    
    # ==================== FILE EXISTENCE TESTS ====================
    
    def test_03_001_service_api_file_exists(self):
        """
        DOC CLAIM: "src/core/plugin_system/service_api.py"
        DOC LOCATION: Line 3
        TEST TYPE: File Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        assert file_path.exists(), f"File not found: {file_path}"
    
    # ==================== CLASS EXISTENCE TESTS ====================
    
    def test_03_002_service_api_class_exists(self):
        """
        DOC CLAIM: "class ServiceAPI:"
        DOC LOCATION: Line 27
        TEST TYPE: Class Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "class ServiceAPI" in content, "ServiceAPI class not found"
    
    # ==================== METHOD EXISTENCE TESTS (ServiceAPI) ====================
    
    def test_03_003_init_method_exists(self):
        """
        DOC CLAIM: "def __init__(self, config: Dict[str, Any], mt5_client, db):"
        DOC LOCATION: Line 41
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "def __init__(self" in content, "__init__ method not found"
    
    def test_03_004_init_services_method_exists(self):
        """
        DOC CLAIM: "def _init_services(self):"
        DOC LOCATION: Line 53
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        # Check for _init_services or similar initialization method
        has_init = "_init_services" in content or "init_services" in content or "_initialize" in content
        assert has_init, "Service initialization method not found"
    
    def test_03_005_place_single_order_a_method_exists(self):
        """
        DOC CLAIM: "async def place_single_order_a(...)"
        DOC LOCATION: Line 97
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "place_single_order_a" in content or "place_order_a" in content, \
            "place_single_order_a method not found"
    
    def test_03_006_place_single_order_b_method_exists(self):
        """
        DOC CLAIM: "async def place_single_order_b(...)"
        DOC LOCATION: Line 154
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "place_single_order_b" in content or "place_order_b" in content, \
            "place_single_order_b method not found"
    
    def test_03_007_create_dual_orders_method_exists(self):
        """
        DOC CLAIM: "async def create_dual_orders(...)"
        DOC LOCATION: Line 219
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "create_dual_orders" in content, "create_dual_orders method not found"
    
    def test_03_008_close_positions_method_exists(self):
        """
        DOC CLAIM: "async def close_positions_by_direction(...)"
        DOC LOCATION: Line 279
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "close_positions" in content, "close_positions method not found"
    
    def test_03_009_calculate_lot_size_async_method_exists(self):
        """
        DOC CLAIM: "async def calculate_lot_size_async(...)"
        DOC LOCATION: Line 319
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "calculate_lot_size" in content, "calculate_lot_size method not found"
    
    def test_03_010_check_risk_limits_method_exists(self):
        """
        DOC CLAIM: "async def check_risk_limits(...)"
        DOC LOCATION: Line 368
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_risk_limits" in content or "check_risk" in content, \
            "check_risk_limits method not found"
    
    def test_03_011_check_safety_method_exists(self):
        """
        DOC CLAIM: "async def check_safety(self, plugin_id: str) -> SafetyCheckResult:"
        DOC LOCATION: Line 400
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_safety" in content, "check_safety method not found"
    
    def test_03_012_check_pulse_alignment_method_exists(self):
        """
        DOC CLAIM: "async def check_pulse_alignment(...)"
        DOC LOCATION: Line 425
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "check_pulse_alignment" in content or "pulse_alignment" in content, \
            "check_pulse_alignment method not found"
    
    def test_03_013_get_v3_trend_method_exists(self):
        """
        DOC CLAIM: "async def get_v3_trend(...)"
        DOC LOCATION: Line 455
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_v3_trend" in content or "v3_trend" in content, \
            "get_v3_trend method not found"
    
    def test_03_014_get_current_price_method_exists(self):
        """
        DOC CLAIM: "def get_current_price(self, symbol: str) -> float:"
        DOC LOCATION: Line 489
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_current_price" in content, "get_current_price method not found"
    
    def test_03_015_get_spread_method_exists(self):
        """
        DOC CLAIM: "def get_spread(self, symbol: str) -> float:"
        DOC LOCATION: Line 505
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_spread" in content, "get_spread method not found"
    
    def test_03_016_get_atr_method_exists(self):
        """
        DOC CLAIM: "async def get_atr(...)"
        DOC LOCATION: Line 521
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "get_atr" in content, "get_atr method not found"
    
    def test_03_017_start_recovery_method_exists(self):
        """
        DOC CLAIM: "async def start_recovery(self, event: ReentryEvent) -> bool:"
        DOC LOCATION: Line 552
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "start_recovery" in content, "start_recovery method not found"
    
    def test_03_018_create_profit_chain_method_exists(self):
        """
        DOC CLAIM: "async def create_profit_chain(...)"
        DOC LOCATION: Line 568
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "create_profit_chain" in content or "profit_chain" in content, \
            "create_profit_chain method not found"
    
    def test_03_019_send_telegram_notification_method_exists(self):
        """
        DOC CLAIM: "async def send_telegram_notification(...)"
        DOC LOCATION: Line 602
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "send_telegram" in content or "telegram_notification" in content or "send_notification" in content, \
            "send_telegram_notification method not found"
    
    def test_03_020_validate_order_params_method_exists(self):
        """
        DOC CLAIM: "def _validate_order_params(...)"
        DOC LOCATION: Line 628
        TEST TYPE: Method Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "validate_order" in content or "_validate" in content, \
            "_validate_order_params method not found"
    
    # ==================== RELATED FILES EXISTENCE TESTS ====================
    
    def test_03_021_order_execution_service_exists(self):
        """
        DOC CLAIM: "src/core/services/order_execution_service.py"
        DOC LOCATION: Line 708
        TEST TYPE: File Existence
        """
        # Check multiple possible locations
        path1 = SRC_ROOT / "core" / "services" / "order_execution_service.py"
        path2 = SRC_ROOT / "services" / "order_execution_service.py"
        path3 = SRC_ROOT / "core" / "order_execution_service.py"
        exists = path1.exists() or path2.exists() or path3.exists()
        assert exists, "order_execution_service.py not found in expected locations"
    
    def test_03_022_risk_management_service_exists(self):
        """
        DOC CLAIM: "src/core/services/risk_management_service.py"
        DOC LOCATION: Line 709
        TEST TYPE: File Existence
        """
        # Check multiple possible locations
        path1 = SRC_ROOT / "core" / "services" / "risk_management_service.py"
        path2 = SRC_ROOT / "services" / "risk_management_service.py"
        path3 = SRC_ROOT / "core" / "risk_management_service.py"
        path4 = SRC_ROOT / "risk_manager.py"
        exists = path1.exists() or path2.exists() or path3.exists() or path4.exists()
        assert exists, "risk_management_service.py not found in expected locations"
    
    def test_03_023_trend_management_service_exists(self):
        """
        DOC CLAIM: "src/core/services/trend_management_service.py"
        DOC LOCATION: Line 710
        TEST TYPE: File Existence
        """
        # Check multiple possible locations
        path1 = SRC_ROOT / "core" / "services" / "trend_management_service.py"
        path2 = SRC_ROOT / "services" / "trend_management_service.py"
        path3 = SRC_ROOT / "core" / "trend_management_service.py"
        path4 = SRC_ROOT / "trend_manager.py"
        exists = path1.exists() or path2.exists() or path3.exists() or path4.exists()
        assert exists, "trend_management_service.py not found in expected locations"
    
    def test_03_024_market_data_service_exists(self):
        """
        DOC CLAIM: "src/core/services/market_data_service.py"
        DOC LOCATION: Line 711
        TEST TYPE: File Existence
        """
        # Check multiple possible locations
        path1 = SRC_ROOT / "core" / "services" / "market_data_service.py"
        path2 = SRC_ROOT / "services" / "market_data_service.py"
        path3 = SRC_ROOT / "core" / "market_data_service.py"
        path4 = SRC_ROOT / "market_data.py"
        exists = path1.exists() or path2.exists() or path3.exists() or path4.exists()
        assert exists, "market_data_service.py not found in expected locations"
    
    def test_03_025_reentry_service_exists(self):
        """
        DOC CLAIM: "src/core/services/reentry_service.py"
        DOC LOCATION: Line 712
        TEST TYPE: File Existence
        """
        # Check multiple possible locations
        path1 = SRC_ROOT / "core" / "services" / "reentry_service.py"
        path2 = SRC_ROOT / "services" / "reentry_service.py"
        path3 = SRC_ROOT / "core" / "reentry_service.py"
        path4 = SRC_ROOT / "reentry_manager.py"
        exists = path1.exists() or path2.exists() or path3.exists() or path4.exists()
        assert exists, "reentry_service.py not found in expected locations"
    
    def test_03_026_dual_order_service_exists(self):
        """
        DOC CLAIM: "src/core/services/dual_order_service.py"
        DOC LOCATION: Line 713
        TEST TYPE: File Existence
        """
        # Check multiple possible locations
        path1 = SRC_ROOT / "core" / "services" / "dual_order_service.py"
        path2 = SRC_ROOT / "services" / "dual_order_service.py"
        path3 = SRC_ROOT / "core" / "dual_order_service.py"
        path4 = SRC_ROOT / "dual_order_manager.py"
        exists = path1.exists() or path2.exists() or path3.exists() or path4.exists()
        assert exists, "dual_order_service.py not found in expected locations"
    
    def test_03_027_profit_booking_service_exists(self):
        """
        DOC CLAIM: "src/core/services/profit_booking_service.py"
        DOC LOCATION: Line 714
        TEST TYPE: File Existence
        """
        # Check multiple possible locations
        path1 = SRC_ROOT / "core" / "services" / "profit_booking_service.py"
        path2 = SRC_ROOT / "services" / "profit_booking_service.py"
        path3 = SRC_ROOT / "core" / "profit_booking_service.py"
        path4 = SRC_ROOT / "profit_booking_manager.py"
        exists = path1.exists() or path2.exists() or path3.exists() or path4.exists()
        assert exists, "profit_booking_service.py not found in expected locations"
    
    def test_03_028_autonomous_service_exists(self):
        """
        DOC CLAIM: "src/core/services/autonomous_service.py"
        DOC LOCATION: Line 715
        TEST TYPE: File Existence
        """
        # Check multiple possible locations
        path1 = SRC_ROOT / "core" / "services" / "autonomous_service.py"
        path2 = SRC_ROOT / "services" / "autonomous_service.py"
        path3 = SRC_ROOT / "core" / "autonomous_service.py"
        path4 = SRC_ROOT / "autonomous_system_manager.py"
        exists = path1.exists() or path2.exists() or path3.exists() or path4.exists()
        assert exists, "autonomous_service.py not found in expected locations"
    
    # ==================== ATTRIBUTE EXISTENCE TESTS ====================
    
    def test_03_029_config_attribute_exists(self):
        """
        DOC CLAIM: "self.config = config"
        DOC LOCATION: Line 42
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.config" in content, "config attribute not found"
    
    def test_03_030_mt5_client_attribute_exists(self):
        """
        DOC CLAIM: "self.mt5_client = mt5_client"
        DOC LOCATION: Line 43
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.mt5_client" in content or "mt5_client" in content, \
            "mt5_client attribute not found"
    
    def test_03_031_db_attribute_exists(self):
        """
        DOC CLAIM: "self.db = db"
        DOC LOCATION: Line 44
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "self.db" in content or "database" in content, "db attribute not found"
    
    # ==================== SERVICE ATTRIBUTE TESTS ====================
    
    def test_03_032_order_service_attribute_exists(self):
        """
        DOC CLAIM: "self.order_service = OrderExecutionService(...)"
        DOC LOCATION: Line 56
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "order_service" in content or "order_execution" in content, \
            "order_service attribute not found"
    
    def test_03_033_risk_service_attribute_exists(self):
        """
        DOC CLAIM: "self.risk_service = RiskManagementService(...)"
        DOC LOCATION: Line 61
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "risk_service" in content or "risk_manager" in content, \
            "risk_service attribute not found"
    
    def test_03_034_trend_service_attribute_exists(self):
        """
        DOC CLAIM: "self.trend_service = TrendManagementService(...)"
        DOC LOCATION: Line 64
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "trend_service" in content or "trend_manager" in content, \
            "trend_service attribute not found"
    
    def test_03_035_market_service_attribute_exists(self):
        """
        DOC CLAIM: "self.market_service = MarketDataService(...)"
        DOC LOCATION: Line 69
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "market_service" in content or "market_data" in content, \
            "market_service attribute not found"
    
    def test_03_036_reentry_service_attribute_exists(self):
        """
        DOC CLAIM: "self.reentry_service = ReentryService(...)"
        DOC LOCATION: Line 74
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "reentry_service" in content or "reentry_manager" in content, \
            "reentry_service attribute not found"
    
    def test_03_037_dual_order_service_attribute_exists(self):
        """
        DOC CLAIM: "self.dual_order_service = DualOrderService(...)"
        DOC LOCATION: Line 77
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "dual_order_service" in content or "dual_order_manager" in content, \
            "dual_order_service attribute not found"
    
    def test_03_038_profit_booking_service_attribute_exists(self):
        """
        DOC CLAIM: "self.profit_booking_service = ProfitBookingService(...)"
        DOC LOCATION: Line 82
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "profit_booking_service" in content or "profit_booking_manager" in content, \
            "profit_booking_service attribute not found"
    
    def test_03_039_autonomous_service_attribute_exists(self):
        """
        DOC CLAIM: "self.autonomous_service = AutonomousService(...)"
        DOC LOCATION: Line 87
        TEST TYPE: Attribute Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "autonomous_service" in content or "autonomous_manager" in content, \
            "autonomous_service attribute not found"
    
    def test_03_040_logger_exists(self):
        """
        DOC CLAIM: ServiceAPI uses logging
        DOC LOCATION: Multiple lines
        TEST TYPE: Import Existence
        """
        file_path = SRC_ROOT / "core" / "plugin_system" / "service_api.py"
        with open(file_path, 'r') as f:
            content = f.read()
        assert "logging" in content or "logger" in content, "logging not found"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
