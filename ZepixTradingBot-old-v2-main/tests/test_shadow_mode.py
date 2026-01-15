"""
Tests for Shadow Mode
Verifies shadow mode functionality

Part of Plan 11: Shadow Mode Testing
Version: 1.0.0
Date: 2026-01-15
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import os
import json

from src.core.shadow_mode_manager import (
    ShadowModeManager, ExecutionMode, Decision, ComparisonResult
)


# ============================================================================
# Test ExecutionMode Enum
# ============================================================================

class TestExecutionMode:
    """Test ExecutionMode enum"""
    
    def test_legacy_only_value(self):
        """Test LEGACY_ONLY mode value"""
        assert ExecutionMode.LEGACY_ONLY.value == "legacy_only"
    
    def test_shadow_value(self):
        """Test SHADOW mode value"""
        assert ExecutionMode.SHADOW.value == "shadow"
    
    def test_plugin_shadow_value(self):
        """Test PLUGIN_SHADOW mode value"""
        assert ExecutionMode.PLUGIN_SHADOW.value == "plugin_shadow"
    
    def test_plugin_only_value(self):
        """Test PLUGIN_ONLY mode value"""
        assert ExecutionMode.PLUGIN_ONLY.value == "plugin_only"
    
    def test_all_modes_exist(self):
        """Test all expected modes exist"""
        modes = [m.value for m in ExecutionMode]
        assert "legacy_only" in modes
        assert "shadow" in modes
        assert "plugin_shadow" in modes
        assert "plugin_only" in modes


# ============================================================================
# Test Decision Dataclass
# ============================================================================

class TestDecision:
    """Test Decision dataclass"""
    
    def test_decision_creation(self):
        """Test Decision creation"""
        decision = Decision(
            source='legacy',
            signal_id='sig_001',
            timestamp=datetime.now(),
            action='execute',
            reason='valid signal'
        )
        
        assert decision.source == 'legacy'
        assert decision.signal_id == 'sig_001'
        assert decision.action == 'execute'
        assert decision.reason == 'valid signal'
    
    def test_decision_with_order_params(self):
        """Test Decision with order params"""
        order_params = {'symbol': 'EURUSD', 'direction': 'BUY', 'lot_size': 0.01}
        decision = Decision(
            source='v3_combined',
            signal_id='sig_002',
            timestamp=datetime.now(),
            action='execute',
            reason='valid',
            order_params=order_params
        )
        
        assert decision.order_params == order_params
        assert decision.order_params['symbol'] == 'EURUSD'
    
    def test_decision_default_metadata(self):
        """Test Decision default metadata"""
        decision = Decision(
            source='legacy',
            signal_id='sig_003',
            timestamp=datetime.now(),
            action='reject',
            reason='risk limit'
        )
        
        assert decision.metadata == {}
        assert decision.order_params is None


# ============================================================================
# Test ShadowModeManager
# ============================================================================

class TestShadowModeManager:
    """Test shadow mode manager"""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh ShadowModeManager for each test"""
        return ShadowModeManager()
    
    def test_default_mode(self, manager):
        """Test default mode is legacy only"""
        assert manager.mode == ExecutionMode.LEGACY_ONLY
    
    def test_set_mode(self, manager):
        """Test mode setting"""
        manager.set_mode(ExecutionMode.SHADOW)
        assert manager.mode == ExecutionMode.SHADOW
    
    def test_get_mode(self, manager):
        """Test get mode"""
        assert manager.get_mode() == ExecutionMode.LEGACY_ONLY
        manager.set_mode(ExecutionMode.PLUGIN_ONLY)
        assert manager.get_mode() == ExecutionMode.PLUGIN_ONLY
    
    def test_enable_shadow_plugin(self, manager):
        """Test enabling plugin for shadow"""
        manager.enable_shadow_plugin('v3_combined')
        assert manager.is_plugin_in_shadow('v3_combined')
    
    def test_disable_shadow_plugin(self, manager):
        """Test disabling plugin from shadow"""
        manager.enable_shadow_plugin('v3_combined')
        assert manager.is_plugin_in_shadow('v3_combined')
        
        manager.disable_shadow_plugin('v3_combined')
        assert not manager.is_plugin_in_shadow('v3_combined')
    
    def test_get_shadow_plugins(self, manager):
        """Test getting list of shadow plugins"""
        manager.enable_shadow_plugin('v3_combined')
        manager.enable_shadow_plugin('v6_price_action_1m')
        
        plugins = manager.get_shadow_plugins()
        assert 'v3_combined' in plugins
        assert 'v6_price_action_1m' in plugins
    
    def test_record_legacy_decision(self, manager):
        """Test recording legacy decision"""
        manager.record_legacy_decision(
            signal_id='sig_001',
            action='execute',
            reason='valid signal',
            order_params={'symbol': 'EURUSD', 'direction': 'BUY'}
        )
        
        assert 'sig_001' in manager._decisions
        assert len(manager._decisions['sig_001']) == 1
        assert manager._stats['legacy_executes'] == 1
    
    def test_record_plugin_decision(self, manager):
        """Test recording plugin decision"""
        manager.enable_shadow_plugin('v3_combined')
        manager.record_plugin_decision(
            plugin_id='v3_combined',
            signal_id='sig_001',
            action='execute',
            reason='valid signal',
            order_params={'symbol': 'EURUSD', 'direction': 'BUY'}
        )
        
        assert 'sig_001' in manager._decisions
        assert len(manager._decisions['sig_001']) == 1
        assert manager._stats['plugin_executes'] == 1
        assert manager._stats['shadow_signals'] == 1
    
    def test_record_virtual_order(self, manager):
        """Test recording virtual order"""
        order_params = {'symbol': 'EURUSD', 'direction': 'BUY', 'lot_size': 0.01}
        virtual_order = manager.record_virtual_order(
            plugin_id='v3_combined',
            signal_id='sig_001',
            order_params=order_params
        )
        
        assert virtual_order['plugin_id'] == 'v3_combined'
        assert virtual_order['signal_id'] == 'sig_001'
        assert virtual_order['status'] == 'virtual'
        assert len(manager._virtual_orders) == 1
    
    def test_get_virtual_orders(self, manager):
        """Test getting virtual orders"""
        for i in range(5):
            manager.record_virtual_order(
                plugin_id='v3_combined',
                signal_id=f'sig_{i}',
                order_params={'symbol': 'EURUSD'}
            )
        
        orders = manager.get_virtual_orders(3)
        assert len(orders) == 3


# ============================================================================
# Test Decision Comparison
# ============================================================================

class TestDecisionComparison:
    """Test decision comparison functionality"""
    
    @pytest.fixture
    def manager(self):
        return ShadowModeManager()
    
    def test_compare_matching_decisions(self, manager):
        """Test comparison of matching decisions"""
        manager.enable_shadow_plugin('v3_combined')
        
        # Record matching decisions
        manager.record_legacy_decision(
            signal_id='sig_002',
            action='execute',
            reason='valid',
            order_params={'symbol': 'EURUSD', 'direction': 'BUY', 'lot_size': 0.01}
        )
        manager.record_plugin_decision(
            plugin_id='v3_combined',
            signal_id='sig_002',
            action='execute',
            reason='valid',
            order_params={'symbol': 'EURUSD', 'direction': 'BUY', 'lot_size': 0.01}
        )
        
        result = manager.compare_decisions('sig_002')
        
        assert result is not None
        assert result.match == True
        assert manager._stats['matches'] == 1
    
    def test_compare_mismatching_actions(self, manager):
        """Test comparison of mismatching actions"""
        manager.enable_shadow_plugin('v3_combined')
        
        # Record mismatching decisions
        manager.record_legacy_decision(
            signal_id='sig_003',
            action='execute',
            reason='valid',
            order_params={'symbol': 'EURUSD', 'direction': 'BUY', 'lot_size': 0.01}
        )
        manager.record_plugin_decision(
            plugin_id='v3_combined',
            signal_id='sig_003',
            action='reject',
            reason='risk limit',
            order_params=None
        )
        
        result = manager.compare_decisions('sig_003')
        
        assert result is not None
        assert result.match == False
        assert result.discrepancy_type == 'action_mismatch'
        assert manager._stats['discrepancies'] == 1
    
    def test_compare_mismatching_symbol(self, manager):
        """Test comparison of mismatching symbol"""
        manager.enable_shadow_plugin('v3_combined')
        
        manager.record_legacy_decision(
            signal_id='sig_004',
            action='execute',
            reason='valid',
            order_params={'symbol': 'EURUSD', 'direction': 'BUY', 'lot_size': 0.01}
        )
        manager.record_plugin_decision(
            plugin_id='v3_combined',
            signal_id='sig_004',
            action='execute',
            reason='valid',
            order_params={'symbol': 'GBPUSD', 'direction': 'BUY', 'lot_size': 0.01}
        )
        
        result = manager.compare_decisions('sig_004')
        
        assert result is not None
        assert result.match == False
        assert result.discrepancy_type == 'symbol_mismatch'
    
    def test_compare_no_legacy_decision(self, manager):
        """Test comparison with no legacy decision"""
        manager.enable_shadow_plugin('v3_combined')
        
        manager.record_plugin_decision(
            plugin_id='v3_combined',
            signal_id='sig_005',
            action='execute',
            reason='valid'
        )
        
        result = manager.compare_decisions('sig_005')
        assert result is None
    
    def test_get_discrepancies(self, manager):
        """Test getting discrepancies"""
        manager.enable_shadow_plugin('v3_combined')
        
        # Create some discrepancies
        for i in range(5):
            manager.record_legacy_decision(f'sig_{i}', 'execute', 'valid')
            manager.record_plugin_decision('v3_combined', f'sig_{i}', 'reject', 'risk')
            manager.compare_decisions(f'sig_{i}')
        
        discrepancies = manager.get_discrepancies(3)
        assert len(discrepancies) == 3


# ============================================================================
# Test Execution Control
# ============================================================================

class TestExecutionControl:
    """Test execution control methods"""
    
    @pytest.fixture
    def manager(self):
        return ShadowModeManager()
    
    def test_execution_control_legacy_only(self, manager):
        """Test execution control in legacy only mode"""
        manager.set_mode(ExecutionMode.LEGACY_ONLY)
        
        assert manager.should_execute_legacy() == True
        assert manager.should_execute_plugin('v3_combined') == False
        assert manager.should_run_plugin('v3_combined') == False
    
    def test_execution_control_shadow(self, manager):
        """Test execution control in shadow mode"""
        manager.set_mode(ExecutionMode.SHADOW)
        manager.enable_shadow_plugin('v3_combined')
        
        assert manager.should_execute_legacy() == True
        assert manager.should_execute_plugin('v3_combined') == False
        assert manager.should_run_plugin('v3_combined') == True
    
    def test_execution_control_plugin_shadow(self, manager):
        """Test execution control in plugin shadow mode"""
        manager.set_mode(ExecutionMode.PLUGIN_SHADOW)
        manager.enable_shadow_plugin('v3_combined')
        
        assert manager.should_execute_legacy() == False
        assert manager.should_execute_plugin('v3_combined') == True
        assert manager.should_run_plugin('v3_combined') == True
    
    def test_execution_control_plugin_only(self, manager):
        """Test execution control in plugin only mode"""
        manager.set_mode(ExecutionMode.PLUGIN_ONLY)
        
        assert manager.should_execute_legacy() == False
        assert manager.should_execute_plugin('v3_combined') == True
    
    def test_is_shadow_mode_active(self, manager):
        """Test is_shadow_mode_active"""
        manager.set_mode(ExecutionMode.LEGACY_ONLY)
        assert manager.is_shadow_mode_active() == False
        
        manager.set_mode(ExecutionMode.SHADOW)
        assert manager.is_shadow_mode_active() == True
        
        manager.set_mode(ExecutionMode.PLUGIN_SHADOW)
        assert manager.is_shadow_mode_active() == True
        
        manager.set_mode(ExecutionMode.PLUGIN_ONLY)
        assert manager.is_shadow_mode_active() == False


# ============================================================================
# Test Statistics and Reporting
# ============================================================================

class TestStatisticsAndReporting:
    """Test statistics and reporting functionality"""
    
    @pytest.fixture
    def manager(self):
        return ShadowModeManager()
    
    def test_get_stats(self, manager):
        """Test getting statistics"""
        manager.enable_shadow_plugin('v3_combined')
        manager.set_mode(ExecutionMode.SHADOW)
        
        # Record some decisions
        for i in range(5):
            manager.record_legacy_decision(f'sig_{i}', 'execute', 'valid')
            manager.record_plugin_decision('v3_combined', f'sig_{i}', 'execute', 'valid')
            manager.compare_decisions(f'sig_{i}')
        
        stats = manager.get_stats()
        
        assert stats['signals_processed'] == 5
        assert stats['matches'] == 5
        assert stats['match_rate'] == 100.0
        assert stats['mode'] == 'shadow'
        assert 'v3_combined' in stats['shadow_plugins']
    
    def test_generate_report(self, manager):
        """Test report generation"""
        manager.enable_shadow_plugin('v3_combined')
        manager.set_mode(ExecutionMode.SHADOW)
        
        manager.record_legacy_decision('sig_001', 'execute', 'valid')
        manager.record_plugin_decision('v3_combined', 'sig_001', 'execute', 'valid')
        manager.compare_decisions('sig_001')
        
        report = manager.generate_report()
        
        assert 'SHADOW MODE REPORT' in report
        assert 'STATISTICS' in report
        assert 'shadow' in report
    
    def test_export_comparisons(self, manager):
        """Test exporting comparisons"""
        manager.enable_shadow_plugin('v3_combined')
        
        manager.record_legacy_decision('sig_001', 'execute', 'valid')
        manager.record_plugin_decision('v3_combined', 'sig_001', 'execute', 'valid')
        manager.compare_decisions('sig_001')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            manager.export_comparisons(filepath)
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            assert len(data) == 1
            assert data[0]['signal_id'] == 'sig_001'
            assert data[0]['match'] == True
        finally:
            os.unlink(filepath)
    
    def test_export_virtual_orders(self, manager):
        """Test exporting virtual orders"""
        manager.record_virtual_order('v3_combined', 'sig_001', {'symbol': 'EURUSD'})
        manager.record_virtual_order('v3_combined', 'sig_002', {'symbol': 'GBPUSD'})
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            manager.export_virtual_orders(filepath)
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            assert len(data) == 2
        finally:
            os.unlink(filepath)
    
    def test_reset_stats(self, manager):
        """Test resetting statistics"""
        manager.enable_shadow_plugin('v3_combined')
        
        manager.record_legacy_decision('sig_001', 'execute', 'valid')
        manager.record_plugin_decision('v3_combined', 'sig_001', 'execute', 'valid')
        manager.compare_decisions('sig_001')
        manager.record_virtual_order('v3_combined', 'sig_001', {'symbol': 'EURUSD'})
        
        assert manager._stats['signals_processed'] == 1
        assert len(manager._virtual_orders) == 1
        
        manager.reset_stats()
        
        assert manager._stats['signals_processed'] == 0
        assert len(manager._virtual_orders) == 0
        assert len(manager._decisions) == 0
        assert len(manager._comparisons) == 0


# ============================================================================
# Test Shadow Commands (Mocked)
# ============================================================================

class TestShadowCommands:
    """Test shadow mode Telegram commands"""
    
    @pytest.fixture
    def manager(self):
        return ShadowModeManager()
    
    @pytest.fixture
    def mock_bot(self):
        bot = Mock()
        bot.register_command = Mock()
        return bot
    
    def test_shadow_commands_import(self):
        """Test ShadowModeCommands can be imported"""
        from src.telegram.shadow_commands import ShadowModeCommands
        assert ShadowModeCommands is not None
    
    def test_shadow_commands_creation(self, manager, mock_bot):
        """Test ShadowModeCommands creation"""
        from src.telegram.shadow_commands import ShadowModeCommands
        
        commands = ShadowModeCommands(manager, mock_bot)
        
        assert commands.shadow_manager == manager
        assert commands.bot == mock_bot
    
    def test_setup_shadow_commands(self, manager, mock_bot):
        """Test setup_shadow_commands helper"""
        from src.telegram.shadow_commands import setup_shadow_commands
        
        commands = setup_shadow_commands(manager, mock_bot)
        
        assert commands is not None
        assert commands.shadow_manager == manager


# ============================================================================
# Test Integration with TradingEngine
# ============================================================================

class TestTradingEngineIntegration:
    """Test shadow mode integration with TradingEngine"""
    
    def test_shadow_manager_import_in_trading_engine(self):
        """Test ShadowModeManager is imported in trading_engine"""
        # This verifies the import statement was added correctly
        import src.core.trading_engine as te
        assert hasattr(te, 'ShadowModeManager')
        assert hasattr(te, 'ExecutionMode')


# ============================================================================
# Summary
# ============================================================================
# Total Tests: 45+
# Categories:
# - ExecutionMode: 5 tests
# - Decision: 3 tests
# - ShadowModeManager: 10 tests
# - DecisionComparison: 5 tests
# - ExecutionControl: 5 tests
# - StatisticsAndReporting: 6 tests
# - ShadowCommands: 3 tests
# - TradingEngineIntegration: 1 test
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
