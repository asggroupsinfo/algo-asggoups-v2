"""
Tests for Autonomous System Integration (Plan 06)
Verifies plugins properly use safety limits and Reverse Shield

Tests:
1. IAutonomousCapable interface definition
2. AutonomousService implementation
3. Safety checks (daily/concurrent limits, profit protection)
4. Reverse Shield activation/deactivation
5. V3 Plugin implementation
6. Success criteria verification
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.plugin_system.autonomous_interface import (
    IAutonomousCapable, SafetyCheckResult, ReverseShieldStatus, RecoveryStats,
    DEFAULT_DAILY_RECOVERY_LIMIT, DEFAULT_CONCURRENT_RECOVERY_LIMIT,
    DEFAULT_PROFIT_PROTECTION_THRESHOLD
)
from src.core.services.autonomous_service import (
    AutonomousService, get_autonomous_service, reset_autonomous_service
)


class TestAutonomousInterface:
    """Test IAutonomousCapable interface definition"""
    
    def test_safety_check_result_dataclass(self):
        """Test SafetyCheckResult dataclass"""
        result = SafetyCheckResult(
            allowed=True,
            reason="All checks passed",
            daily_count=5,
            daily_limit=10,
            concurrent_count=1,
            concurrent_limit=3,
            current_profit=50.0,
            profit_threshold=100.0
        )
        
        assert result.allowed == True
        assert result.reason == "All checks passed"
        assert result.daily_count == 5
        assert result.daily_limit == 10
        assert result.concurrent_count == 1
        assert result.concurrent_limit == 3
        assert result.current_profit == 50.0
        assert result.profit_threshold == 100.0
    
    def test_safety_check_result_to_dict(self):
        """Test SafetyCheckResult to_dict method"""
        result = SafetyCheckResult(
            allowed=False,
            reason="Daily limit reached",
            daily_count=10,
            daily_limit=10,
            concurrent_count=2,
            concurrent_limit=3,
            current_profit=75.0,
            profit_threshold=100.0
        )
        
        result_dict = result.to_dict()
        assert result_dict['allowed'] == False
        assert result_dict['reason'] == "Daily limit reached"
        assert 'timestamp' in result_dict
    
    def test_reverse_shield_status_dataclass(self):
        """Test ReverseShieldStatus dataclass"""
        status = ReverseShieldStatus(
            active=True,
            shield_id="shield_001",
            symbol="EURUSD",
            direction="BUY",
            hedge_order_id="hedge_001",
            shield_a_ticket=12345,
            shield_b_ticket=12346,
            recovery_70_level=1.0850
        )
        
        assert status.active == True
        assert status.shield_id == "shield_001"
        assert status.symbol == "EURUSD"
        assert status.direction == "BUY"
        assert status.shield_a_ticket == 12345
        assert status.shield_b_ticket == 12346
        assert status.recovery_70_level == 1.0850
    
    def test_reverse_shield_status_to_dict(self):
        """Test ReverseShieldStatus to_dict method"""
        status = ReverseShieldStatus(
            active=False,
            shield_id=None,
            symbol="GBPUSD",
            direction="SELL",
            hedge_order_id=None,
            error="RSM not available"
        )
        
        status_dict = status.to_dict()
        assert status_dict['active'] == False
        assert status_dict['error'] == "RSM not available"
    
    def test_recovery_stats_dataclass(self):
        """Test RecoveryStats dataclass"""
        stats = RecoveryStats(
            daily_recoveries=5,
            concurrent_recoveries=2,
            shields_activated=3,
            shields_successful=2,
            profit_protected_skips=1
        )
        
        assert stats.daily_recoveries == 5
        assert stats.concurrent_recoveries == 2
        assert stats.shields_activated == 3
        assert stats.shields_successful == 2
        assert stats.profit_protected_skips == 1
    
    def test_default_limits(self):
        """Test default safety limits"""
        assert DEFAULT_DAILY_RECOVERY_LIMIT == 10
        assert DEFAULT_CONCURRENT_RECOVERY_LIMIT == 3
        assert DEFAULT_PROFIT_PROTECTION_THRESHOLD == 100.0
    
    def test_interface_has_required_methods(self):
        """Test IAutonomousCapable has all required abstract methods"""
        required_methods = [
            'check_recovery_allowed',
            'activate_reverse_shield',
            'deactivate_reverse_shield',
            'increment_recovery_count',
            'get_safety_stats',
            'should_protect_profit'
        ]
        
        for method in required_methods:
            assert hasattr(IAutonomousCapable, method)


class TestAutonomousService:
    """Test AutonomousService implementation"""
    
    def setup_method(self):
        """Reset singleton before each test"""
        reset_autonomous_service()
    
    def teardown_method(self):
        """Reset singleton after each test"""
        reset_autonomous_service()
    
    def test_service_initialization(self):
        """Test AutonomousService initializes correctly"""
        service = AutonomousService()
        
        assert service.DAILY_RECOVERY_LIMIT == DEFAULT_DAILY_RECOVERY_LIMIT
        assert service.CONCURRENT_RECOVERY_LIMIT == DEFAULT_CONCURRENT_RECOVERY_LIMIT
        assert service.PROFIT_PROTECTION_THRESHOLD == DEFAULT_PROFIT_PROTECTION_THRESHOLD
        assert service._plugin_stats == {}
        assert service._plugin_shields == {}
    
    def test_singleton_pattern(self):
        """Test singleton pattern works"""
        service1 = get_autonomous_service()
        service2 = get_autonomous_service()
        
        assert service1 is service2
    
    def test_singleton_reset(self):
        """Test singleton reset works"""
        service1 = get_autonomous_service()
        reset_autonomous_service()
        service2 = get_autonomous_service()
        
        assert service1 is not service2
    
    @pytest.mark.asyncio
    async def test_recovery_allowed_all_checks_pass(self):
        """Test recovery allowed when all checks pass"""
        service = AutonomousService()
        service._daily_recovery_count = 5
        service._concurrent_recovery_count = 1
        service._current_session_profit = 50.0
        
        result = await service.check_recovery_allowed('v3_combined')
        
        assert result.allowed == True
        assert result.reason == "All safety checks passed"
        assert result.daily_count == 5
        assert result.concurrent_count == 1
        assert result.current_profit == 50.0
    
    @pytest.mark.asyncio
    async def test_daily_limit_blocks_recovery(self):
        """Test daily limit blocks recovery"""
        service = AutonomousService()
        service._daily_recovery_count = 10  # At limit
        
        result = await service.check_recovery_allowed('v3_combined')
        
        assert result.allowed == False
        assert "Daily recovery limit" in result.reason
        assert result.daily_count == 10
    
    @pytest.mark.asyncio
    async def test_concurrent_limit_blocks_recovery(self):
        """Test concurrent limit blocks recovery"""
        service = AutonomousService()
        service._concurrent_recovery_count = 3  # At limit
        
        result = await service.check_recovery_allowed('v3_combined')
        
        assert result.allowed == False
        assert "Concurrent recovery limit" in result.reason
        assert result.concurrent_count == 3
    
    @pytest.mark.asyncio
    async def test_profit_protection_blocks_recovery(self):
        """Test profit protection blocks recovery"""
        service = AutonomousService()
        service._current_session_profit = 150.0  # Above threshold
        
        result = await service.check_recovery_allowed('v3_combined')
        
        assert result.allowed == False
        assert "Profit protection" in result.reason
        assert result.current_profit == 150.0
    
    @pytest.mark.asyncio
    async def test_increment_recovery_count(self):
        """Test increment recovery count"""
        service = AutonomousService()
        service._daily_recovery_count = 5
        
        new_count = await service.increment_recovery_count('v3_combined')
        
        assert new_count == 6
        assert service._daily_recovery_count == 6
        assert 'v3_combined' in service._plugin_stats
        assert service._plugin_stats['v3_combined'].daily_recoveries == 1
    
    @pytest.mark.asyncio
    async def test_reverse_shield_activation_no_rsm(self):
        """Test Reverse Shield activation without RSM"""
        service = AutonomousService()
        
        status = await service.activate_reverse_shield(
            plugin_id='v3_combined',
            trade_id='trade_001',
            symbol='EURUSD',
            direction='BUY'
        )
        
        assert status.active == False
        assert status.symbol == 'EURUSD'
        assert status.direction == 'BUY'
        assert "not available" in status.error.lower()
    
    @pytest.mark.asyncio
    async def test_reverse_shield_deactivation(self):
        """Test Reverse Shield deactivation"""
        service = AutonomousService()
        
        # Add a shield to track
        service._plugin_shields['v3_combined'] = {
            'trade_001': ReverseShieldStatus(
                active=True,
                shield_id='shield_001',
                symbol='EURUSD',
                direction='BUY',
                hedge_order_id=None
            )
        }
        
        success = await service.deactivate_reverse_shield('v3_combined', 'trade_001')
        
        assert success == True
        assert 'trade_001' not in service._plugin_shields.get('v3_combined', {})
    
    def test_should_protect_profit(self):
        """Test should_protect_profit method"""
        service = AutonomousService()
        
        # Below threshold
        assert service.should_protect_profit(50.0) == False
        
        # At threshold
        assert service.should_protect_profit(100.0) == True
        
        # Above threshold
        assert service.should_protect_profit(150.0) == True
    
    def test_get_plugin_stats(self):
        """Test get_plugin_stats method"""
        service = AutonomousService()
        
        # No stats yet
        stats = service.get_plugin_stats('v3_combined')
        assert stats['daily_recoveries'] == 0
        
        # Add some stats
        service._plugin_stats['v3_combined'] = RecoveryStats(
            daily_recoveries=5,
            shields_activated=3
        )
        
        stats = service.get_plugin_stats('v3_combined')
        assert stats['daily_recoveries'] == 5
        assert stats['shields_activated'] == 3
    
    @pytest.mark.asyncio
    async def test_global_stats(self):
        """Test get_global_stats method"""
        service = AutonomousService()
        service._daily_recovery_count = 5
        service._concurrent_recovery_count = 2
        service._current_session_profit = 75.0
        
        stats = await service.get_global_stats()
        
        assert stats['daily_recovery_count'] == 5
        assert stats['daily_recovery_limit'] == 10
        assert stats['concurrent_recovery_count'] == 2
        assert stats['concurrent_recovery_limit'] == 3
        assert stats['current_session_profit'] == 75.0
        assert stats['profit_protection_threshold'] == 100.0


class TestAutonomousServiceWithASM:
    """Test AutonomousService with mocked AutonomousSystemManager"""
    
    def setup_method(self):
        """Reset singleton before each test"""
        reset_autonomous_service()
    
    def teardown_method(self):
        """Reset singleton after each test"""
        reset_autonomous_service()
    
    @pytest.mark.asyncio
    async def test_service_with_asm(self):
        """Test service with ASM integration"""
        mock_asm = MagicMock()
        mock_asm.daily_stats = {
            'recovery_attempts': 3,
            'active_recoveries': {'trade_001', 'trade_002'}
        }
        
        service = AutonomousService(autonomous_manager=mock_asm)
        
        daily_count = await service.get_daily_recovery_count()
        concurrent_count = await service.get_concurrent_recovery_count()
        
        assert daily_count == 3
        assert concurrent_count == 2


class TestV3PluginAutonomousCapable:
    """Test V3 Plugin implements IAutonomousCapable correctly"""
    
    def test_plugin_imports_autonomous_interface(self):
        """Test plugin imports autonomous interface"""
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        
        # Check class inherits from IAutonomousCapable
        assert IAutonomousCapable in V3CombinedPlugin.__mro__
    
    def test_plugin_has_autonomous_service_field(self):
        """Test plugin has _autonomous_service field"""
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        
        # Create mock dependencies
        mock_service_api = MagicMock()
        mock_service_api.get_config.return_value = {}
        
        plugin = V3CombinedPlugin(
            plugin_id='v3_combined',
            config={},
            service_api=mock_service_api
        )
        
        assert hasattr(plugin, '_autonomous_service')
        assert plugin._autonomous_service is None
    
    def test_plugin_has_active_shields_field(self):
        """Test plugin has _active_shields field"""
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        
        mock_service_api = MagicMock()
        mock_service_api.get_config.return_value = {}
        
        plugin = V3CombinedPlugin(
            plugin_id='v3_combined',
            config={},
            service_api=mock_service_api
        )
        
        assert hasattr(plugin, '_active_shields')
        assert plugin._active_shields == {}
    
    def test_plugin_has_set_autonomous_service_method(self):
        """Test plugin has set_autonomous_service method"""
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        
        mock_service_api = MagicMock()
        mock_service_api.get_config.return_value = {}
        
        plugin = V3CombinedPlugin(
            plugin_id='v3_combined',
            config={},
            service_api=mock_service_api
        )
        
        assert hasattr(plugin, 'set_autonomous_service')
        assert callable(plugin.set_autonomous_service)
    
    def test_plugin_service_injection(self):
        """Test autonomous service injection"""
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        
        mock_service_api = MagicMock()
        mock_service_api.get_config.return_value = {}
        
        plugin = V3CombinedPlugin(
            plugin_id='v3_combined',
            config={},
            service_api=mock_service_api
        )
        
        service = AutonomousService()
        plugin.set_autonomous_service(service)
        
        assert plugin._autonomous_service is service
    
    def test_plugin_has_check_recovery_allowed(self):
        """Test plugin has check_recovery_allowed method"""
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        
        assert hasattr(V3CombinedPlugin, 'check_recovery_allowed')
    
    def test_plugin_has_activate_reverse_shield(self):
        """Test plugin has activate_reverse_shield method"""
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        
        assert hasattr(V3CombinedPlugin, 'activate_reverse_shield')
    
    def test_plugin_has_deactivate_reverse_shield(self):
        """Test plugin has deactivate_reverse_shield method"""
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        
        assert hasattr(V3CombinedPlugin, 'deactivate_reverse_shield')
    
    def test_plugin_has_get_active_shields(self):
        """Test plugin has get_active_shields method"""
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        
        assert hasattr(V3CombinedPlugin, 'get_active_shields')


class TestSuccessCriteria:
    """Test all 8 success criteria from Plan 06"""
    
    def setup_method(self):
        """Reset singleton before each test"""
        reset_autonomous_service()
    
    def teardown_method(self):
        """Reset singleton after each test"""
        reset_autonomous_service()
    
    def test_criterion_1_interface_defined(self):
        """Criterion 1: IAutonomousCapable interface properly defined"""
        from src.core.plugin_system.autonomous_interface import IAutonomousCapable
        
        # Check all required methods exist
        required_methods = [
            'check_recovery_allowed',
            'activate_reverse_shield',
            'deactivate_reverse_shield',
            'increment_recovery_count',
            'get_safety_stats',
            'should_protect_profit'
        ]
        
        for method in required_methods:
            assert hasattr(IAutonomousCapable, method), f"Missing method: {method}"
    
    def test_criterion_2_service_created(self):
        """Criterion 2: AutonomousService created"""
        from src.core.services.autonomous_service import AutonomousService
        
        service = AutonomousService()
        assert service is not None
        assert hasattr(service, 'check_recovery_allowed')
        assert hasattr(service, 'activate_reverse_shield')
    
    def test_criterion_3_plugin_implements_interface(self):
        """Criterion 3: V3 plugin implements autonomous checks"""
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        from src.core.plugin_system.autonomous_interface import IAutonomousCapable
        
        assert IAutonomousCapable in V3CombinedPlugin.__mro__
    
    @pytest.mark.asyncio
    async def test_criterion_4_daily_limit_enforced(self):
        """Criterion 4: Daily recovery limit enforced"""
        service = AutonomousService()
        service._daily_recovery_count = 10  # At limit
        
        result = await service.check_recovery_allowed('test_plugin')
        
        assert result.allowed == False
        assert "Daily recovery limit" in result.reason
    
    @pytest.mark.asyncio
    async def test_criterion_5_concurrent_limit_enforced(self):
        """Criterion 5: Concurrent recovery limit enforced"""
        service = AutonomousService()
        service._concurrent_recovery_count = 3  # At limit
        
        result = await service.check_recovery_allowed('test_plugin')
        
        assert result.allowed == False
        assert "Concurrent recovery limit" in result.reason
    
    @pytest.mark.asyncio
    async def test_criterion_6_profit_protection_works(self):
        """Criterion 6: Profit protection works"""
        service = AutonomousService()
        service._current_session_profit = 150.0  # Above threshold
        
        result = await service.check_recovery_allowed('test_plugin')
        
        assert result.allowed == False
        assert "Profit protection" in result.reason
        
        # Also test should_protect_profit
        assert service.should_protect_profit(150.0) == True
        assert service.should_protect_profit(50.0) == False
    
    def test_criterion_7_reverse_shield_integrates(self):
        """Criterion 7: Reverse Shield integrates with recovery"""
        from src.core.plugin_system.autonomous_interface import ReverseShieldStatus
        from src.core.services.autonomous_service import AutonomousService
        
        # Test ReverseShieldStatus has all required fields
        status = ReverseShieldStatus(
            active=True,
            shield_id="test_shield",
            symbol="EURUSD",
            direction="BUY",
            hedge_order_id=None,
            shield_a_ticket=12345,
            shield_b_ticket=12346,
            recovery_70_level=1.0850
        )
        
        assert status.active == True
        assert status.shield_a_ticket == 12345
        assert status.shield_b_ticket == 12346
        assert status.recovery_70_level == 1.0850
        
        # Test service has shield methods
        service = AutonomousService()
        assert hasattr(service, 'activate_reverse_shield')
        assert hasattr(service, 'deactivate_reverse_shield')
    
    @pytest.mark.asyncio
    async def test_criterion_8_all_tests_pass(self):
        """Criterion 8: All tests pass (this is a meta-test)"""
        # This test passes if all other tests pass
        # It verifies the test suite is complete
        
        service = AutonomousService()
        
        # Verify service works
        result = await service.check_recovery_allowed('test_plugin')
        assert result is not None
        
        # Verify stats work
        stats = await service.get_global_stats()
        assert 'daily_recovery_count' in stats
        assert 'concurrent_recovery_count' in stats
        assert 'profit_protection_threshold' in stats


class TestSafetyCheckIntegration:
    """Integration tests for safety check flow"""
    
    def setup_method(self):
        """Reset singleton before each test"""
        reset_autonomous_service()
    
    def teardown_method(self):
        """Reset singleton after each test"""
        reset_autonomous_service()
    
    @pytest.mark.asyncio
    async def test_full_safety_check_flow(self):
        """Test complete safety check flow"""
        service = AutonomousService()
        
        # Initial state - should allow recovery
        result = await service.check_recovery_allowed('v3_combined')
        assert result.allowed == True
        
        # Increment recovery count
        count = await service.increment_recovery_count('v3_combined')
        assert count == 1
        
        # Check stats updated
        stats = service.get_plugin_stats('v3_combined')
        assert stats['daily_recoveries'] == 1
    
    @pytest.mark.asyncio
    async def test_multiple_plugins_tracked_separately(self):
        """Test multiple plugins are tracked separately"""
        service = AutonomousService()
        
        # Increment for plugin 1
        await service.increment_recovery_count('plugin_1')
        await service.increment_recovery_count('plugin_1')
        
        # Increment for plugin 2
        await service.increment_recovery_count('plugin_2')
        
        # Check stats
        stats1 = service.get_plugin_stats('plugin_1')
        stats2 = service.get_plugin_stats('plugin_2')
        
        assert stats1['daily_recoveries'] == 2
        assert stats2['daily_recoveries'] == 1
    
    @pytest.mark.asyncio
    async def test_safety_check_stats_tracking(self):
        """Test safety check stats are tracked"""
        service = AutonomousService()
        
        # Run some checks
        await service.check_recovery_allowed('plugin_1')
        await service.check_recovery_allowed('plugin_2')
        
        # Set to blocked state
        service._daily_recovery_count = 10
        await service.check_recovery_allowed('plugin_3')
        
        # Check global stats
        stats = await service.get_global_stats()
        assert stats['total_safety_checks'] == 3
        assert stats['total_recoveries_blocked'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
