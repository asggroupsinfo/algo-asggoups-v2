"""
Batch 03 Tests: ServiceAPI Layer Implementation

Tests for:
- OrderExecutionService (V3 Dual Order + V6 Conditional)
- RiskManagementService (SL/TP, ATR, Max Daily Loss)
- TrendManagementService (4-Pillar + Trend Pulse)
- MarketDataService (Price, Spread, Filter)

All services must be STATELESS.
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.services.order_execution_service import OrderExecutionService
from src.core.services.risk_management_service import RiskManagementService
from src.core.services.trend_management_service import TrendManagementService
from src.core.services.market_data_service import MarketDataService


class TestOrderExecutionService:
    """Tests for OrderExecutionService"""
    
    @pytest.fixture
    def mock_mt5(self):
        mt5 = Mock()
        mt5.place_order = Mock(return_value=12345)
        mt5.modify_position = Mock(return_value=True)
        mt5.close_position = Mock(return_value=True)
        mt5.close_position_partial = Mock(return_value=True)
        mt5.get_positions = Mock(return_value=[])
        return mt5
    
    @pytest.fixture
    def mock_config(self):
        return {"max_lot_size": 10.0}
    
    @pytest.fixture
    def mock_pip_calculator(self):
        pip_calc = Mock()
        pip_calc.get_pip_size = Mock(return_value=0.1)
        pip_calc.get_pip_value = Mock(return_value=10.0)
        return pip_calc
    
    @pytest.fixture
    def service(self, mock_mt5, mock_config, mock_pip_calculator):
        return OrderExecutionService(mock_mt5, mock_config, mock_pip_calculator)
    
    @pytest.mark.asyncio
    async def test_place_dual_orders_v3(self, service, mock_mt5):
        """Test V3 dual order placement with different SLs"""
        order_a, order_b = await service.place_dual_orders_v3(
            plugin_id='v3_combined',
            symbol='XAUUSD',
            direction='BUY',
            lot_size_total=0.10,
            order_a_sl=2028.00,
            order_a_tp=2035.00,
            order_b_sl=2029.50,
            order_b_tp=2032.00,
            logic_route='LOGIC2'
        )
        
        assert order_a == 12345
        assert order_b == 12345
        assert mock_mt5.place_order.call_count == 2
        
        calls = mock_mt5.place_order.call_args_list
        assert calls[0][1]['sl'] == 2028.00
        assert calls[1][1]['sl'] == 2029.50
    
    @pytest.mark.asyncio
    async def test_place_single_order_a(self, service, mock_mt5):
        """Test V6 Order A placement (15M/1H plugins)"""
        ticket = await service.place_single_order_a(
            plugin_id='v6_price_action_15m',
            symbol='XAUUSD',
            direction='BUY',
            lot_size=0.10,
            sl_price=2028.00,
            tp_price=2035.00
        )
        
        assert ticket == 12345
        assert mock_mt5.place_order.call_count == 1
        assert 'V6_A_' in mock_mt5.place_order.call_args[1]['comment']
    
    @pytest.mark.asyncio
    async def test_place_single_order_b(self, service, mock_mt5):
        """Test V6 Order B placement (1M plugin - scalping)"""
        ticket = await service.place_single_order_b(
            plugin_id='v6_price_action_1m',
            symbol='XAUUSD',
            direction='BUY',
            lot_size=0.05,
            sl_price=2029.00,
            tp_price=2031.00
        )
        
        assert ticket == 12345
        assert mock_mt5.place_order.call_count == 1
        assert 'V6_B_' in mock_mt5.place_order.call_args[1]['comment']
    
    @pytest.mark.asyncio
    async def test_place_dual_orders_v6(self, service, mock_mt5):
        """Test V6 dual order placement with same SL"""
        order_a, order_b = await service.place_dual_orders_v6(
            plugin_id='v6_price_action_5m',
            symbol='XAUUSD',
            direction='BUY',
            lot_size_total=0.10,
            sl_price=2028.00,
            tp1_price=2032.00,
            tp2_price=2035.00
        )
        
        assert order_a == 12345
        assert order_b == 12345
        assert mock_mt5.place_order.call_count == 2
        
        calls = mock_mt5.place_order.call_args_list
        assert calls[0][1]['sl'] == 2028.00
        assert calls[1][1]['sl'] == 2028.00
    
    @pytest.mark.asyncio
    async def test_modify_order(self, service, mock_mt5):
        """Test order modification"""
        result = await service.modify_order(
            plugin_id='v3_combined',
            order_id=12345,
            new_sl=2029.00,
            new_tp=2036.00
        )
        
        assert result is True
        mock_mt5.modify_position.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_position(self, service, mock_mt5):
        """Test position close"""
        result = await service.close_position(
            plugin_id='v3_combined',
            order_id=12345,
            reason='TP Hit'
        )
        
        assert result['success'] is True
        mock_mt5.close_position.assert_called_once_with(12345)
    
    @pytest.mark.asyncio
    async def test_lot_size_minimum(self, service, mock_mt5):
        """Test minimum lot size enforcement"""
        await service.place_single_order_a(
            plugin_id='test',
            symbol='XAUUSD',
            direction='BUY',
            lot_size=0.001,
            sl_price=2028.00,
            tp_price=2035.00
        )
        
        assert mock_mt5.place_order.call_args[1]['lot_size'] >= 0.01


class TestRiskManagementService:
    """Tests for RiskManagementService"""
    
    @pytest.fixture
    def mock_risk_manager(self):
        rm = Mock()
        rm.daily_loss = 100.0
        rm.lifetime_loss = 500.0
        rm.get_risk_tier = Mock(return_value="10000")
        rm.get_fixed_lot_size = Mock(return_value=0.10)
        return rm
    
    @pytest.fixture
    def mock_config(self):
        return {
            "risk_tiers": {
                "10000": {
                    "daily_loss_limit": 500.0,
                    "max_total_loss": 2000.0
                }
            },
            "max_lot_size": 10.0
        }
    
    @pytest.fixture
    def mock_mt5(self):
        mt5 = Mock()
        mt5.get_account_balance = Mock(return_value=10000.0)
        return mt5
    
    @pytest.fixture
    def mock_pip_calculator(self):
        pip_calc = Mock()
        pip_calc.get_pip_size = Mock(return_value=0.1)
        pip_calc.get_pip_value = Mock(return_value=10.0)
        pip_calc.get_digits = Mock(return_value=2)
        return pip_calc
    
    @pytest.fixture
    def service(self, mock_risk_manager, mock_config, mock_mt5, mock_pip_calculator):
        return RiskManagementService(mock_risk_manager, mock_config, mock_mt5, mock_pip_calculator)
    
    @pytest.mark.asyncio
    async def test_calculate_lot_size(self, service):
        """Test lot size calculation based on risk"""
        lot = await service.calculate_lot_size(
            plugin_id='test',
            symbol='XAUUSD',
            risk_percentage=1.5,
            stop_loss_pips=30.0
        )
        
        assert lot >= 0.01
        assert lot <= 10.0
    
    @pytest.mark.asyncio
    async def test_check_daily_limit(self, service):
        """Test daily loss limit check"""
        result = await service.check_daily_limit('test_plugin')
        
        assert 'daily_loss' in result
        assert 'daily_limit' in result
        assert 'remaining' in result
        assert 'can_trade' in result
        assert result['daily_loss'] == 100.0
        assert result['daily_limit'] == 500.0
        assert result['remaining'] == 400.0
        assert result['can_trade'] is True
    
    @pytest.mark.asyncio
    async def test_check_lifetime_limit(self, service):
        """Test lifetime loss limit check"""
        result = await service.check_lifetime_limit('test_plugin')
        
        assert 'lifetime_loss' in result
        assert 'lifetime_limit' in result
        assert result['lifetime_loss'] == 500.0
        assert result['lifetime_limit'] == 2000.0
        assert result['can_trade'] is True
    
    @pytest.mark.asyncio
    async def test_calculate_atr_sl_buy(self, service):
        """Test ATR-based SL calculation for BUY"""
        sl = await service.calculate_atr_sl(
            symbol='XAUUSD',
            direction='BUY',
            entry_price=2030.00,
            atr_value=5.0,
            atr_multiplier=1.5
        )
        
        assert sl == 2022.50
    
    @pytest.mark.asyncio
    async def test_calculate_atr_sl_sell(self, service):
        """Test ATR-based SL calculation for SELL"""
        sl = await service.calculate_atr_sl(
            symbol='XAUUSD',
            direction='SELL',
            entry_price=2030.00,
            atr_value=5.0,
            atr_multiplier=1.5
        )
        
        assert sl == 2037.50
    
    @pytest.mark.asyncio
    async def test_validate_trade_risk_pass(self, service):
        """Test trade risk validation - should pass"""
        result = await service.validate_trade_risk(
            plugin_id='test',
            symbol='XAUUSD',
            lot_size=0.10,
            sl_pips=30.0
        )
        
        assert result['valid'] is True
    
    @pytest.mark.asyncio
    async def test_get_fixed_lot_size(self, service):
        """Test fixed lot size retrieval"""
        lot = await service.get_fixed_lot_size('test_plugin')
        
        assert lot == 0.10


class TestTrendManagementService:
    """Tests for TrendManagementService"""
    
    @pytest.fixture
    def mock_trend_manager(self):
        tm = Mock()
        tm.get_trend = Mock(return_value="BULLISH")
        tm.get_mode = Mock(return_value="AUTO")
        tm.get_all_trends = Mock(return_value={
            "15m": "BULLISH",
            "1h": "BULLISH",
            "4h": "BEARISH",
            "1d": "BULLISH"
        })
        tm.check_logic_alignment = Mock(return_value={
            "aligned": True,
            "direction": "BULLISH",
            "details": {"1h": "BULLISH", "15m": "BULLISH"}
        })
        tm.update_trend = Mock(return_value=True)
        return tm
    
    @pytest.fixture
    def service(self, mock_trend_manager):
        return TrendManagementService(mock_trend_manager)
    
    @pytest.mark.asyncio
    async def test_get_timeframe_trend(self, service):
        """Test getting trend for specific timeframe"""
        result = await service.get_timeframe_trend('XAUUSD', '15m')
        
        assert result['timeframe'] == '15m'
        assert result['direction'] == 'bullish'
        assert result['value'] == 1
    
    @pytest.mark.asyncio
    async def test_get_mtf_trends(self, service):
        """Test getting all 4-pillar trends"""
        result = await service.get_mtf_trends('XAUUSD')
        
        assert result['15m'] == 1
        assert result['1h'] == 1
        assert result['4h'] == -1
        assert result['1d'] == 1
    
    @pytest.mark.asyncio
    async def test_validate_v3_trend_alignment_pass(self, service):
        """Test V3 trend alignment - should pass with 3/4 bullish"""
        result = await service.validate_v3_trend_alignment(
            symbol='XAUUSD',
            direction='BUY',
            min_aligned=3
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_v3_trend_alignment_fail(self, service):
        """Test V3 trend alignment - should fail for SELL"""
        result = await service.validate_v3_trend_alignment(
            symbol='XAUUSD',
            direction='SELL',
            min_aligned=3
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_logic_alignment(self, service):
        """Test logic alignment check"""
        result = await service.check_logic_alignment(
            symbol='XAUUSD',
            logic='combinedlogic-1',
            direction='BUY'
        )
        
        assert result['aligned'] is True
        assert result['direction'] == 'BULLISH'
    
    @pytest.mark.asyncio
    async def test_update_trend_pulse(self, service):
        """Test trend pulse update"""
        await service.update_trend_pulse(
            symbol='XAUUSD',
            timeframe='15',
            bull_count=5,
            bear_count=1,
            market_state='TRENDING_BULLISH',
            changes='15m,1h'
        )
        
        state = await service.get_market_state('XAUUSD')
        assert state == 'TRENDING_BULLISH'
    
    @pytest.mark.asyncio
    async def test_check_pulse_alignment_buy(self, service):
        """Test pulse alignment for BUY"""
        await service.update_trend_pulse(
            symbol='XAUUSD',
            timeframe='15',
            bull_count=5,
            bear_count=1,
            market_state='TRENDING_BULLISH',
            changes='15m'
        )
        
        result = await service.check_pulse_alignment('XAUUSD', 'BUY')
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_pulse_data(self, service):
        """Test getting pulse data"""
        await service.update_trend_pulse(
            symbol='XAUUSD',
            timeframe='15',
            bull_count=5,
            bear_count=1,
            market_state='TRENDING_BULLISH',
            changes='15m'
        )
        
        result = await service.get_pulse_data('XAUUSD')
        assert '15' in result
        assert result['15']['bull_count'] == 5


class TestMarketDataService:
    """Tests for MarketDataService"""
    
    @pytest.fixture
    def mock_mt5(self):
        mt5 = Mock()
        mt5.get_symbol_info = Mock(return_value={
            'spread': 15,
            'point': 0.01,
            'digits': 2,
            'volume_min': 0.01,
            'volume_max': 100.0,
            'volume_step': 0.01,
            'trade_contract_size': 100.0,
            'trade_mode': 0
        })
        mt5.get_symbol_tick = Mock(return_value={
            'bid': 2030.45,
            'ask': 2030.55,
            'last': 2030.50,
            'volume': 1000
        })
        mt5.get_rates = Mock(return_value=[
            {'high': 2035.0, 'low': 2028.0},
            {'high': 2033.0, 'low': 2029.0},
            {'high': 2034.0, 'low': 2030.0}
        ])
        return mt5
    
    @pytest.fixture
    def mock_config(self):
        return {}
    
    @pytest.fixture
    def mock_pip_calculator(self):
        pip_calc = Mock()
        pip_calc.get_pip_size = Mock(return_value=0.1)
        pip_calc.get_pip_value = Mock(return_value=10.0)
        return pip_calc
    
    @pytest.fixture
    def service(self, mock_mt5, mock_config, mock_pip_calculator):
        return MarketDataService(mock_mt5, mock_config, mock_pip_calculator)
    
    @pytest.mark.asyncio
    async def test_get_current_spread_xauusd(self, service):
        """Test spread calculation for XAUUSD"""
        spread = await service.get_current_spread('XAUUSD')
        
        assert spread == 1.5
    
    @pytest.mark.asyncio
    async def test_check_spread_acceptable_pass(self, service):
        """Test spread filtering - should pass"""
        result = await service.check_spread_acceptable('XAUUSD', 2.0)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_spread_acceptable_fail(self, service):
        """Test spread filtering - should fail"""
        result = await service.check_spread_acceptable('XAUUSD', 1.0)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_current_price(self, service):
        """Test price data retrieval"""
        price = await service.get_current_price('XAUUSD')
        
        assert price['bid'] == 2030.45
        assert price['ask'] == 2030.55
        assert price['spread_pips'] == 1.5
    
    @pytest.mark.asyncio
    async def test_get_price_range(self, service):
        """Test price range calculation"""
        result = await service.get_price_range('XAUUSD', '15m', 3)
        
        assert result is not None
        assert result['high'] == 2035.0
        assert result['low'] == 2028.0
        assert result['bars_analyzed'] == 3
    
    @pytest.mark.asyncio
    async def test_is_market_open(self, service):
        """Test market open check"""
        result = await service.is_market_open('XAUUSD')
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_symbol_info(self, service):
        """Test symbol info retrieval"""
        info = await service.get_symbol_info('XAUUSD')
        
        assert info is not None
        assert info['digits'] == 2
        assert info['min_lot'] == 0.01
    
    @pytest.mark.asyncio
    async def test_get_volatility_state(self, service):
        """Test volatility state analysis"""
        result = await service.get_volatility_state('XAUUSD', '15m')
        
        assert 'state' in result
        assert result['state'] in ['HIGH', 'MODERATE', 'LOW', 'UNKNOWN']


class TestServiceStatelessness:
    """Tests to verify services are stateless"""
    
    @pytest.mark.asyncio
    async def test_order_service_no_internal_state(self):
        """Verify OrderExecutionService doesn't store trade state"""
        mt5 = Mock()
        mt5.place_order = Mock(return_value=12345)
        
        service = OrderExecutionService(mt5, {}, Mock())
        
        assert not hasattr(service, 'open_orders')
        assert not hasattr(service, 'trade_history')
        assert not hasattr(service, '_orders')
    
    @pytest.mark.asyncio
    async def test_risk_service_uses_external_state(self):
        """Verify RiskManagementService uses external risk_manager state"""
        rm = Mock()
        rm.daily_loss = 100.0
        rm.get_risk_tier = Mock(return_value="10000")
        
        config = {"risk_tiers": {"10000": {"daily_loss_limit": 500.0, "max_total_loss": 2000.0}}}
        mt5 = Mock()
        mt5.get_account_balance = Mock(return_value=10000.0)
        
        service = RiskManagementService(rm, config, mt5, Mock())
        
        assert not hasattr(service, 'daily_loss')
        assert not hasattr(service, '_daily_loss')
        
        result = await service.check_daily_limit('test')
        assert result['daily_loss'] == 100.0
    
    @pytest.mark.asyncio
    async def test_trend_service_uses_external_manager(self):
        """Verify TrendManagementService uses external trend_manager"""
        tm = Mock()
        tm.get_trend = Mock(return_value="BULLISH")
        tm.get_mode = Mock(return_value="AUTO")
        
        service = TrendManagementService(tm)
        
        assert not hasattr(service, 'trends')
        assert not hasattr(service, '_trends')
        
        result = await service.get_timeframe_trend('XAUUSD', '15m')
        tm.get_trend.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_market_service_cache_is_temporary(self):
        """Verify MarketDataService cache is for performance only"""
        mt5 = Mock()
        mt5.get_symbol_info = Mock(return_value={'spread': 15, 'point': 0.01})
        
        service = MarketDataService(mt5, {}, Mock())
        
        assert hasattr(service, '_cache')
        assert service._cache_ttl == 1.0
        
        service.clear_cache()
        assert service._cache == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
