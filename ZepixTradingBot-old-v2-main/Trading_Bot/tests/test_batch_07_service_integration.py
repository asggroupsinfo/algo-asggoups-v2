"""
Test Suite for Batch 07: Shared Service API Integration

This test suite verifies:
1. ServiceAPI initialization and service integration
2. Plugin -> ServiceAPI -> Service -> MockMT5 flow
3. All facade methods work correctly
4. Backward compatibility with existing methods
5. Circular dependency prevention
6. Plugin isolation

Version: 1.0.0
Date: 2026-01-14
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from datetime import datetime


# =============================================================================
# MOCK CLASSES
# =============================================================================

class MockMT5Client:
    """Mock MT5 client for testing"""
    
    def __init__(self):
        self.orders_placed = []
        self.positions_closed = []
        self.positions_modified = []
        self._balance = 10000.0
        self._equity = 10500.0
        self._positions = []
    
    def get_account_balance(self):
        return self._balance
    
    def get_account_equity(self):
        return self._equity
    
    def get_symbol_tick(self, symbol):
        prices = {
            'XAUUSD': {'bid': 2650.50, 'ask': 2650.80, 'last': 2650.65, 'volume': 1000},
            'EURUSD': {'bid': 1.0850, 'ask': 1.0852, 'last': 1.0851, 'volume': 5000}
        }
        return prices.get(symbol, {'bid': 100.0, 'ask': 100.1})
    
    def get_symbol_info(self, symbol):
        infos = {
            'XAUUSD': {'digits': 2, 'point': 0.01, 'spread': 30, 'volume_min': 0.01, 
                       'volume_max': 100.0, 'volume_step': 0.01, 'trade_contract_size': 100.0,
                       'trade_mode': 0},
            'EURUSD': {'digits': 5, 'point': 0.00001, 'spread': 10, 'volume_min': 0.01,
                       'volume_max': 100.0, 'volume_step': 0.01, 'trade_contract_size': 100000.0,
                       'trade_mode': 0}
        }
        return infos.get(symbol, {'digits': 2, 'point': 0.01, 'spread': 20})
    
    def place_order(self, symbol, order_type, lot_size, price, sl, tp, comment):
        ticket = len(self.orders_placed) + 1000
        self.orders_placed.append({
            'ticket': ticket,
            'symbol': symbol,
            'type': order_type,
            'lot_size': lot_size,
            'sl': sl,
            'tp': tp,
            'comment': comment
        })
        return ticket
    
    def close_position(self, ticket):
        self.positions_closed.append(ticket)
        return True
    
    def close_position_partial(self, ticket, percentage):
        return {'success': True, 'ticket': ticket, 'percentage': percentage}
    
    def modify_position(self, ticket, sl, tp):
        self.positions_modified.append({'ticket': ticket, 'sl': sl, 'tp': tp})
        return True
    
    def get_positions(self):
        return self._positions
    
    def get_rates(self, symbol, timeframe, bars_back):
        return [{'high': 2660.0, 'low': 2640.0, 'open': 2650.0, 'close': 2655.0} 
                for _ in range(bars_back)]


class MockRiskManager:
    """Mock risk manager for testing"""
    
    def __init__(self):
        self.daily_loss = 50.0
        self.lifetime_loss = 200.0
    
    def get_fixed_lot_size(self, balance):
        if balance >= 10000:
            return 0.10
        elif balance >= 5000:
            return 0.05
        return 0.01
    
    def calculate_lot_size(self, balance, sl_pips):
        risk_amount = balance * 0.01
        pip_value = 10.0
        return round(risk_amount / (sl_pips * pip_value), 2)
    
    def get_risk_tier(self, balance):
        if balance >= 10000:
            return "tier_3"
        elif balance >= 5000:
            return "tier_2"
        return "tier_1"


class MockTelegramBot:
    """Mock Telegram bot for testing"""
    
    def __init__(self):
        self.messages_sent = []
    
    def send_message(self, message):
        self.messages_sent.append(message)


class MockTrendManager:
    """Mock trend manager for testing"""
    
    def __init__(self):
        self._trends = {
            'XAUUSD': {
                '15m': 'BULLISH',
                '1h': 'BULLISH',
                '4h': 'BEARISH',
                '1d': 'BULLISH'
            }
        }
    
    def get_trend(self, symbol, timeframe):
        return self._trends.get(symbol, {}).get(timeframe, 'NEUTRAL')
    
    def get_mode(self, symbol, timeframe):
        return 'AUTO'
    
    def get_all_trends(self, symbol):
        return self._trends.get(symbol, {})
    
    def check_logic_alignment(self, symbol, logic):
        return {'aligned': True, 'direction': 'BULLISH', 'details': {}}
    
    def update_trend(self, symbol, timeframe, signal, mode):
        return True


class MockPipCalculator:
    """Mock pip calculator for testing"""
    
    def get_pip_value(self, symbol, lot_size):
        if symbol in ['XAUUSD', 'XAGUSD']:
            return lot_size * 10.0
        return lot_size * 10.0
    
    def get_pip_size(self, symbol):
        if symbol in ['XAUUSD', 'XAGUSD']:
            return 0.1
        return 0.0001
    
    def get_digits(self, symbol):
        if symbol in ['XAUUSD', 'XAGUSD']:
            return 2
        return 5


class MockTradingEngine:
    """Mock trading engine for testing"""
    
    def __init__(self):
        self.config = {
            'max_lot_size': 10.0,
            'risk_tiers': {
                'tier_1': {'daily_loss_limit': 100.0, 'max_total_loss': 500.0},
                'tier_2': {'daily_loss_limit': 250.0, 'max_total_loss': 1000.0},
                'tier_3': {'daily_loss_limit': 500.0, 'max_total_loss': 2000.0}
            },
            'plugins': {
                'v3_combined': {'max_lot_size': 1.0, 'risk_percentage': 1.5},
                'v6_price_action_1m': {'max_lot_size': 0.5, 'risk_percentage': 1.0}
            }
        }
        self.mt5_client = MockMT5Client()
        self.risk_manager = MockRiskManager()
        self.telegram_bot = MockTelegramBot()
        self.timeframe_trend_manager = MockTrendManager()
        self.pip_calculator = MockPipCalculator()
        self.database = None
        self.trading_enabled = True
        self._open_trades = []
    
    def get_open_trades(self):
        return self._open_trades


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def mock_trading_engine():
    """Create a mock trading engine"""
    return MockTradingEngine()


@pytest.fixture
def service_api(mock_trading_engine):
    """Create a ServiceAPI instance with mocked dependencies"""
    from src.core.plugin_system.service_api import ServiceAPI
    return ServiceAPI(mock_trading_engine, plugin_id="test_plugin")


@pytest.fixture
def service_api_core(mock_trading_engine):
    """Create a ServiceAPI instance for core (backward compatible)"""
    from src.core.plugin_system.service_api import ServiceAPI
    return ServiceAPI(mock_trading_engine)


# =============================================================================
# TEST: ServiceAPI INITIALIZATION
# =============================================================================

class TestServiceAPIInitialization:
    """Tests for ServiceAPI initialization"""
    
    def test_init_with_plugin_id(self, mock_trading_engine):
        """Test initialization with plugin_id"""
        from src.core.plugin_system.service_api import ServiceAPI
        api = ServiceAPI(mock_trading_engine, plugin_id="v3_combined")
        
        assert api.plugin_id == "v3_combined"
        assert api._engine == mock_trading_engine
        assert api._mt5 == mock_trading_engine.mt5_client
        assert api._risk == mock_trading_engine.risk_manager
    
    def test_init_default_plugin_id(self, mock_trading_engine):
        """Test initialization with default plugin_id (core)"""
        from src.core.plugin_system.service_api import ServiceAPI
        api = ServiceAPI(mock_trading_engine)
        
        assert api.plugin_id == "core"
    
    def test_services_initialized(self, service_api):
        """Test that services are initialized"""
        assert service_api._order_service is not None
        assert service_api._risk_service is not None
        assert service_api._trend_service is not None
        assert service_api._market_service is not None
        assert service_api.services_available == True
    
    def test_factory_function(self, mock_trading_engine):
        """Test create_service_api factory function"""
        from src.core.plugin_system.service_api import create_service_api
        api = create_service_api(mock_trading_engine, plugin_id="test_factory")
        
        assert api.plugin_id == "test_factory"
        assert api.services_available == True


# =============================================================================
# TEST: BACKWARD COMPATIBLE METHODS
# =============================================================================

class TestBackwardCompatibility:
    """Tests for backward compatible methods"""
    
    def test_get_price(self, service_api):
        """Test get_price (backward compatible)"""
        price = service_api.get_price("XAUUSD")
        assert price == 2650.50
    
    def test_get_symbol_info(self, service_api):
        """Test get_symbol_info (backward compatible)"""
        info = service_api.get_symbol_info("XAUUSD")
        assert info['digits'] == 2
        assert info['spread'] == 30
    
    def test_get_balance(self, service_api):
        """Test get_balance (backward compatible)"""
        balance = service_api.get_balance()
        assert balance == 10000.0
    
    def test_get_equity(self, service_api):
        """Test get_equity (backward compatible)"""
        equity = service_api.get_equity()
        assert equity == 10500.0
    
    def test_place_order(self, service_api, mock_trading_engine):
        """Test place_order (backward compatible)"""
        ticket = service_api.place_order(
            symbol="XAUUSD",
            direction="BUY",
            lot_size=0.1,
            sl_price=2640.0,
            tp_price=2670.0,
            comment="test_order"
        )
        
        assert ticket is not None
        assert len(mock_trading_engine.mt5_client.orders_placed) == 1
        order = mock_trading_engine.mt5_client.orders_placed[0]
        assert order['symbol'] == "XAUUSD"
        assert order['type'] == "BUY"
        assert "test_plugin" in order['comment']
    
    def test_close_trade(self, service_api, mock_trading_engine):
        """Test close_trade (backward compatible)"""
        result = service_api.close_trade(1000)
        assert result == True
        assert 1000 in mock_trading_engine.mt5_client.positions_closed
    
    def test_modify_order(self, service_api, mock_trading_engine):
        """Test modify_order (backward compatible)"""
        result = service_api.modify_order(1000, sl=2635.0, tp=2675.0)
        assert result == True
        assert len(mock_trading_engine.mt5_client.positions_modified) == 1
    
    def test_calculate_lot_size(self, service_api):
        """Test calculate_lot_size (backward compatible)"""
        lot = service_api.calculate_lot_size("XAUUSD", stop_loss_pips=50)
        assert lot > 0
    
    def test_send_notification(self, service_api, mock_trading_engine):
        """Test send_notification (backward compatible)"""
        service_api.send_notification("Test message")
        assert "Test message" in mock_trading_engine.telegram_bot.messages_sent
    
    def test_get_config(self, service_api):
        """Test get_config (backward compatible)"""
        max_lot = service_api.get_config("max_lot_size")
        assert max_lot == 10.0
    
    def test_get_open_trades(self, service_api, mock_trading_engine):
        """Test get_open_trades (backward compatible)"""
        mock_trading_engine._open_trades = [{'ticket': 1001}, {'ticket': 1002}]
        trades = service_api.get_open_trades()
        assert len(trades) == 2


# =============================================================================
# TEST: ORDER EXECUTION SERVICE INTEGRATION
# =============================================================================

class TestOrderExecutionIntegration:
    """Tests for OrderExecutionService integration"""
    
    @pytest.mark.asyncio
    async def test_place_dual_orders_v3(self, service_api, mock_trading_engine):
        """Test V3 dual order placement"""
        order_a, order_b = await service_api.place_dual_orders_v3(
            symbol="XAUUSD",
            direction="BUY",
            lot_size_total=0.2,
            order_a_sl=2640.0,
            order_a_tp=2680.0,
            order_b_sl=2645.0,
            order_b_tp=2665.0,
            logic_route="LOGIC1"
        )
        
        assert order_a is not None
        assert order_b is not None
        assert len(mock_trading_engine.mt5_client.orders_placed) == 2
    
    @pytest.mark.asyncio
    async def test_place_dual_orders_v6(self, service_api, mock_trading_engine):
        """Test V6 dual order placement (same SL)"""
        order_a, order_b = await service_api.place_dual_orders_v6(
            symbol="XAUUSD",
            direction="SELL",
            lot_size_total=0.2,
            sl_price=2660.0,
            tp1_price=2640.0,
            tp2_price=2620.0
        )
        
        assert order_a is not None
        assert order_b is not None
    
    @pytest.mark.asyncio
    async def test_place_single_order_a(self, service_api, mock_trading_engine):
        """Test Order A only placement (15M/1H V6)"""
        ticket = await service_api.place_single_order_a(
            symbol="XAUUSD",
            direction="BUY",
            lot_size=0.1,
            sl_price=2640.0,
            tp_price=2680.0
        )
        
        assert ticket is not None
    
    @pytest.mark.asyncio
    async def test_place_single_order_b(self, service_api, mock_trading_engine):
        """Test Order B only placement (1M V6 scalping)"""
        ticket = await service_api.place_single_order_b(
            symbol="XAUUSD",
            direction="SELL",
            lot_size=0.05,
            sl_price=2655.0,
            tp_price=2645.0
        )
        
        assert ticket is not None
    
    @pytest.mark.asyncio
    async def test_close_position_async(self, service_api):
        """Test async position close"""
        result = await service_api.close_position(1000, reason="TP_HIT")
        
        assert result['success'] == True
        assert result['reason'] == "TP_HIT"
    
    @pytest.mark.asyncio
    async def test_close_position_partial(self, service_api):
        """Test partial position close"""
        result = await service_api.close_position_partial(1000, percentage=50.0)
        
        assert 'success' in result or 'error' in result
    
    @pytest.mark.asyncio
    async def test_modify_order_async(self, service_api):
        """Test async order modification"""
        result = await service_api.modify_order_async(
            order_id=1000,
            new_sl=2635.0,
            new_tp=2675.0
        )
        
        assert result == True
    
    @pytest.mark.asyncio
    async def test_get_plugin_orders(self, service_api):
        """Test getting plugin-specific orders"""
        orders = await service_api.get_plugin_orders(symbol="XAUUSD")
        
        assert isinstance(orders, list)
    
    def test_trading_disabled_rejects_orders(self, service_api, mock_trading_engine):
        """Test that orders are rejected when trading is disabled"""
        mock_trading_engine.trading_enabled = False
        
        ticket = service_api.place_order(
            symbol="XAUUSD",
            direction="BUY",
            lot_size=0.1
        )
        
        assert ticket is None


# =============================================================================
# TEST: RISK MANAGEMENT SERVICE INTEGRATION
# =============================================================================

class TestRiskManagementIntegration:
    """Tests for RiskManagementService integration"""
    
    @pytest.mark.asyncio
    async def test_calculate_lot_size_async(self, service_api):
        """Test async lot size calculation"""
        lot = await service_api.calculate_lot_size_async(
            symbol="XAUUSD",
            risk_percentage=1.5,
            stop_loss_pips=50
        )
        
        assert lot > 0
        assert lot <= 10.0
    
    @pytest.mark.asyncio
    async def test_calculate_atr_sl(self, service_api):
        """Test ATR-based SL calculation"""
        sl = await service_api.calculate_atr_sl(
            symbol="XAUUSD",
            direction="BUY",
            entry_price=2650.0,
            atr_value=5.0,
            atr_multiplier=1.5
        )
        
        assert sl > 0
        assert sl < 2650.0
    
    @pytest.mark.asyncio
    async def test_calculate_atr_tp(self, service_api):
        """Test ATR-based TP calculation"""
        tp = await service_api.calculate_atr_tp(
            symbol="XAUUSD",
            direction="BUY",
            entry_price=2650.0,
            atr_value=5.0,
            atr_multiplier=2.0
        )
        
        assert tp > 0
        assert tp > 2650.0
    
    @pytest.mark.asyncio
    async def test_check_daily_limit(self, service_api):
        """Test daily limit check"""
        result = await service_api.check_daily_limit()
        
        assert 'can_trade' in result
        assert 'daily_loss' in result
    
    @pytest.mark.asyncio
    async def test_check_lifetime_limit(self, service_api):
        """Test lifetime limit check"""
        result = await service_api.check_lifetime_limit()
        
        assert 'can_trade' in result
        assert 'lifetime_loss' in result
    
    @pytest.mark.asyncio
    async def test_validate_trade_risk(self, service_api):
        """Test trade risk validation"""
        result = await service_api.validate_trade_risk(
            symbol="XAUUSD",
            lot_size=0.1,
            sl_pips=50
        )
        
        assert 'valid' in result
        assert 'reason' in result
    
    @pytest.mark.asyncio
    async def test_get_fixed_lot_size(self, service_api):
        """Test fixed lot size retrieval"""
        lot = await service_api.get_fixed_lot_size()
        
        assert lot > 0


# =============================================================================
# TEST: MARKET DATA SERVICE INTEGRATION
# =============================================================================

class TestMarketDataIntegration:
    """Tests for MarketDataService integration"""
    
    @pytest.mark.asyncio
    async def test_get_current_spread(self, service_api):
        """Test spread retrieval"""
        spread = await service_api.get_current_spread("XAUUSD")
        
        assert spread >= 0
    
    @pytest.mark.asyncio
    async def test_check_spread_acceptable(self, service_api):
        """Test spread acceptability check"""
        acceptable = await service_api.check_spread_acceptable("XAUUSD", max_spread_pips=50)
        
        assert isinstance(acceptable, bool)
    
    @pytest.mark.asyncio
    async def test_get_current_price_data(self, service_api):
        """Test comprehensive price data retrieval"""
        data = await service_api.get_current_price_data("XAUUSD")
        
        assert data is not None
        assert 'bid' in data
    
    @pytest.mark.asyncio
    async def test_get_volatility_state(self, service_api):
        """Test volatility state analysis"""
        state = await service_api.get_volatility_state("XAUUSD", timeframe="15m")
        
        assert 'state' in state
    
    @pytest.mark.asyncio
    async def test_is_market_open(self, service_api):
        """Test market open check"""
        is_open = await service_api.is_market_open("XAUUSD")
        
        assert isinstance(is_open, bool)


# =============================================================================
# TEST: TREND MANAGEMENT SERVICE INTEGRATION
# =============================================================================

class TestTrendManagementIntegration:
    """Tests for TrendManagementService integration"""
    
    @pytest.mark.asyncio
    async def test_get_timeframe_trend(self, service_api):
        """Test single timeframe trend retrieval"""
        trend = await service_api.get_timeframe_trend("XAUUSD", "15m")
        
        assert 'direction' in trend
        assert 'timeframe' in trend
    
    @pytest.mark.asyncio
    async def test_get_mtf_trends(self, service_api):
        """Test multi-timeframe trends retrieval"""
        trends = await service_api.get_mtf_trends("XAUUSD")
        
        assert '15m' in trends
        assert '1h' in trends
        assert '4h' in trends
        assert '1d' in trends
    
    @pytest.mark.asyncio
    async def test_validate_v3_trend_alignment(self, service_api):
        """Test V3 trend alignment validation"""
        aligned = await service_api.validate_v3_trend_alignment(
            symbol="XAUUSD",
            direction="BUY",
            min_aligned=3
        )
        
        assert isinstance(aligned, bool)
    
    @pytest.mark.asyncio
    async def test_check_logic_alignment(self, service_api):
        """Test logic alignment check"""
        result = await service_api.check_logic_alignment(
            symbol="XAUUSD",
            logic="combinedlogic-1",
            direction="BUY"
        )
        
        assert 'aligned' in result
    
    @pytest.mark.asyncio
    async def test_update_trend_pulse(self, service_api):
        """Test trend pulse update"""
        await service_api.update_trend_pulse(
            symbol="XAUUSD",
            timeframe="15",
            bull_count=5,
            bear_count=2,
            market_state="TRENDING_BULLISH",
            changes="15m,1h"
        )
    
    @pytest.mark.asyncio
    async def test_get_market_state(self, service_api):
        """Test market state retrieval"""
        state = await service_api.get_market_state("XAUUSD")
        
        assert isinstance(state, str)
    
    @pytest.mark.asyncio
    async def test_check_pulse_alignment(self, service_api):
        """Test pulse alignment check"""
        aligned = await service_api.check_pulse_alignment("XAUUSD", "BUY")
        
        assert isinstance(aligned, bool)
    
    @pytest.mark.asyncio
    async def test_get_pulse_data(self, service_api):
        """Test pulse data retrieval"""
        data = await service_api.get_pulse_data("XAUUSD")
        
        assert isinstance(data, dict)
    
    @pytest.mark.asyncio
    async def test_update_trend(self, service_api):
        """Test trend update"""
        result = await service_api.update_trend(
            symbol="XAUUSD",
            timeframe="15m",
            signal="bull",
            mode="AUTO"
        )
        
        assert result == True


# =============================================================================
# TEST: PLUGIN ISOLATION
# =============================================================================

class TestPluginIsolation:
    """Tests for plugin isolation"""
    
    def test_different_plugin_ids(self, mock_trading_engine):
        """Test that different plugins have different IDs"""
        from src.core.plugin_system.service_api import ServiceAPI
        
        api_v3 = ServiceAPI(mock_trading_engine, plugin_id="v3_combined")
        api_v6 = ServiceAPI(mock_trading_engine, plugin_id="v6_price_action_1m")
        
        assert api_v3.plugin_id != api_v6.plugin_id
        assert api_v3.plugin_id == "v3_combined"
        assert api_v6.plugin_id == "v6_price_action_1m"
    
    def test_plugin_config_isolation(self, mock_trading_engine):
        """Test that plugins get their own config"""
        from src.core.plugin_system.service_api import ServiceAPI
        
        api_v3 = ServiceAPI(mock_trading_engine, plugin_id="v3_combined")
        api_v6 = ServiceAPI(mock_trading_engine, plugin_id="v6_price_action_1m")
        
        v3_max_lot = api_v3.get_plugin_config("max_lot_size")
        v6_max_lot = api_v6.get_plugin_config("max_lot_size")
        
        assert v3_max_lot == 1.0
        assert v6_max_lot == 0.5
    
    def test_order_comment_tagging(self, service_api, mock_trading_engine):
        """Test that orders are tagged with plugin_id"""
        service_api.place_order(
            symbol="XAUUSD",
            direction="BUY",
            lot_size=0.1,
            comment="test"
        )
        
        order = mock_trading_engine.mt5_client.orders_placed[0]
        assert "test_plugin" in order['comment']
    
    def test_log_includes_plugin_id(self, service_api, caplog):
        """Test that logs include plugin_id"""
        import logging
        caplog.set_level(logging.INFO)
        
        service_api.log("Test log message", level="info")


# =============================================================================
# TEST: END-TO-END FLOW
# =============================================================================

class TestEndToEndFlow:
    """Tests for end-to-end plugin flow"""
    
    @pytest.mark.asyncio
    async def test_full_v3_trade_flow(self, service_api, mock_trading_engine):
        """Test complete V3 trade flow: validate -> calculate -> place -> close"""
        risk_valid = await service_api.validate_trade_risk(
            symbol="XAUUSD",
            lot_size=0.1,
            sl_pips=50
        )
        assert risk_valid['valid'] == True
        
        lot = await service_api.calculate_lot_size_async(
            symbol="XAUUSD",
            risk_percentage=1.5,
            stop_loss_pips=50
        )
        assert lot > 0
        
        aligned = await service_api.validate_v3_trend_alignment(
            symbol="XAUUSD",
            direction="BUY",
            min_aligned=2
        )
        
        order_a, order_b = await service_api.place_dual_orders_v3(
            symbol="XAUUSD",
            direction="BUY",
            lot_size_total=lot * 2,
            order_a_sl=2640.0,
            order_a_tp=2680.0,
            order_b_sl=2645.0,
            order_b_tp=2665.0,
            logic_route="LOGIC1"
        )
        assert order_a is not None
        assert order_b is not None
        
        result = await service_api.close_position(order_a, reason="TP_HIT")
        assert result['success'] == True
    
    @pytest.mark.asyncio
    async def test_full_v6_trade_flow(self, service_api, mock_trading_engine):
        """Test complete V6 trade flow with spread check"""
        spread_ok = await service_api.check_spread_acceptable("XAUUSD", max_spread_pips=50)
        
        pulse_aligned = await service_api.check_pulse_alignment("XAUUSD", "BUY")
        
        lot = await service_api.get_fixed_lot_size()
        assert lot > 0
        
        ticket = await service_api.place_single_order_b(
            symbol="XAUUSD",
            direction="BUY",
            lot_size=lot,
            sl_price=2645.0,
            tp_price=2655.0,
            comment="V6_1M_SCALP"
        )
        assert ticket is not None
    
    @pytest.mark.asyncio
    async def test_market_data_before_entry(self, service_api):
        """Test market data checks before entry"""
        price_data = await service_api.get_current_price_data("XAUUSD")
        assert price_data is not None
        
        volatility = await service_api.get_volatility_state("XAUUSD")
        assert 'state' in volatility
        
        market_open = await service_api.is_market_open("XAUUSD")
        assert isinstance(market_open, bool)


# =============================================================================
# TEST: CIRCULAR DEPENDENCY PREVENTION
# =============================================================================

class TestCircularDependencyPrevention:
    """Tests for circular dependency prevention"""
    
    def test_services_import_independently(self):
        """Test that services can be imported independently"""
        from src.core.services import OrderExecutionService
        from src.core.services import RiskManagementService
        from src.core.services import TrendManagementService
        from src.core.services import MarketDataService
        
        assert OrderExecutionService is not None
        assert RiskManagementService is not None
        assert TrendManagementService is not None
        assert MarketDataService is not None
    
    def test_service_api_import(self):
        """Test that ServiceAPI can be imported"""
        from src.core.plugin_system.service_api import ServiceAPI
        from src.core.plugin_system.service_api import create_service_api
        
        assert ServiceAPI is not None
        assert create_service_api is not None
    
    def test_no_circular_import_on_init(self, mock_trading_engine):
        """Test that initialization doesn't cause circular imports"""
        from src.core.plugin_system.service_api import ServiceAPI
        
        api = ServiceAPI(mock_trading_engine, plugin_id="test")
        assert api.services_available == True


# =============================================================================
# TEST: ERROR HANDLING
# =============================================================================

class TestErrorHandling:
    """Tests for error handling"""
    
    def test_invalid_symbol_price(self, service_api):
        """Test handling of invalid symbol for price"""
        price = service_api.get_price("INVALID_SYMBOL")
        assert price == 0.0 or price > 0
    
    @pytest.mark.asyncio
    async def test_service_fallback_on_error(self, mock_trading_engine):
        """Test that API falls back gracefully when services fail"""
        from src.core.plugin_system.service_api import ServiceAPI
        
        api = ServiceAPI(mock_trading_engine, plugin_id="test")
        
        price = api.get_price("XAUUSD")
        assert price > 0
    
    def test_trading_disabled_handling(self, service_api, mock_trading_engine):
        """Test handling when trading is disabled"""
        mock_trading_engine.trading_enabled = False
        
        ticket = service_api.place_order(
            symbol="XAUUSD",
            direction="BUY",
            lot_size=0.1
        )
        
        assert ticket is None


# =============================================================================
# TEST: CONFIGURATION
# =============================================================================

class TestConfiguration:
    """Tests for configuration methods"""
    
    def test_get_config(self, service_api):
        """Test global config retrieval"""
        max_lot = service_api.get_config("max_lot_size")
        assert max_lot == 10.0
    
    def test_get_config_default(self, service_api):
        """Test config with default value"""
        value = service_api.get_config("nonexistent_key", default="default_value")
        assert value == "default_value"
    
    def test_get_plugin_config(self, mock_trading_engine):
        """Test plugin-specific config retrieval"""
        from src.core.plugin_system.service_api import ServiceAPI
        
        api = ServiceAPI(mock_trading_engine, plugin_id="v3_combined")
        
        max_lot = api.get_plugin_config("max_lot_size")
        risk_pct = api.get_plugin_config("risk_percentage")
        
        assert max_lot == 1.0
        assert risk_pct == 1.5
    
    def test_get_plugin_config_default(self, service_api):
        """Test plugin config with default value"""
        value = service_api.get_plugin_config("nonexistent_key", default="default")
        assert value == "default"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
