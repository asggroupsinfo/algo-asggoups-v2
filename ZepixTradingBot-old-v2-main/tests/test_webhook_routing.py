"""
Tests for Webhook Routing
Verifies signals are correctly parsed and routed to plugins

Part of Plan 02: Webhook Routing & Signal Processing
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Import the modules we're testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.signal_parser import SignalParser
from src.core.plugin_router import PluginRouter, reset_plugin_router
from src.api.middleware.signal_validator import SignalValidator


class TestSignalParser:
    """Test signal parsing"""
    
    def test_parse_v3_alert_with_strategy(self):
        """Test V3 alert parsing with explicit strategy"""
        alert = {
            'strategy': 'V3_COMBINED',
            'signal': 'BUY',
            'symbol': 'EURUSD',
            'logic': 'LOGIC1',
            'price': 1.0850,
            'sl_pips': 15,
            'trend': 'BULLISH'
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['strategy'] == 'V3_COMBINED'
        assert signal['signal_type'] == 'BUY'
        assert signal['symbol'] == 'EURUSD'
        assert signal['timeframe'] == '5m'  # LOGIC1 = 5m
        assert signal['plugin_hint'] == 'v3_combined'
        assert signal['requires_dual_order'] == True
    
    def test_parse_v3_alert_with_type(self):
        """Test V3 alert parsing with alert type"""
        alert = {
            'type': 'entry_v3',
            'signal': 'SELL',
            'symbol': 'GBPUSD',
            'logic': 'LOGIC2',
            'consensus_score': 7
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['strategy'] == 'V3_COMBINED'
        assert signal['signal_type'] == 'SELL'
        assert signal['timeframe'] == '15m'  # LOGIC2 = 15m
        assert signal['consensus_score'] == 7
    
    def test_parse_v6_alert(self):
        """Test V6 alert parsing"""
        alert = {
            'strategy': 'V6_PRICE_ACTION',
            'signal': 'TRENDLINE_BREAK',
            'symbol': 'GBPUSD',
            'timeframe': '15m',
            'trend_pulse': 'STRONG_UP',
            'price': 1.2650
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['strategy'] == 'V6_PRICE_ACTION'
        assert signal['signal_type'] == 'TRENDLINE_BREAK'
        assert signal['symbol'] == 'GBPUSD'
        assert signal['timeframe'] == '15m'
        assert signal['plugin_hint'] == 'v6_price_action_15m'
        assert signal['requires_dual_order'] == False
    
    def test_parse_v6_alert_with_type(self):
        """Test V6 alert parsing with alert type"""
        alert = {
            'type': 'entry_v6',
            'signal': 'MOMENTUM_SHIFT',
            'symbol': 'USDJPY',
            'timeframe': '1m',
            'trend_pulse': 'WEAK_DOWN'
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['strategy'] == 'V6_PRICE_ACTION'
        assert signal['timeframe'] == '1m'
        assert signal['plugin_hint'] == 'v6_price_action_1m'
    
    def test_detect_v3_from_logic(self):
        """Test V3 detection from logic field"""
        alert = {
            'signal': 'BUY',
            'symbol': 'EURUSD',
            'logic': 'LOGIC2'
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['strategy'] == 'V3_COMBINED'
        assert signal['timeframe'] == '15m'  # LOGIC2 = 15m
    
    def test_detect_v3_from_consensus_score(self):
        """Test V3 detection from consensus_score field"""
        alert = {
            'signal': 'BUY',
            'symbol': 'EURUSD',
            'consensus_score': 8
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['strategy'] == 'V3_COMBINED'
    
    def test_detect_v6_from_trend_pulse(self):
        """Test V6 detection from trend_pulse field"""
        alert = {
            'signal': 'PRICE_ACTION_ENTRY',
            'symbol': 'EURUSD',
            'timeframe': '1m',
            'trend_pulse': 'WEAK_DOWN'
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['strategy'] == 'V6_PRICE_ACTION'
    
    def test_invalid_alert_returns_none(self):
        """Test invalid alert returns None"""
        alert = {'random': 'data'}
        
        signal = SignalParser.parse(alert)
        
        assert signal is None
    
    def test_validate_valid_signal(self):
        """Test validation of valid signal"""
        signal = {
            'strategy': 'V3_COMBINED',
            'signal_type': 'BUY',
            'symbol': 'EURUSD',
            'timeframe': '5m'
        }
        
        assert SignalParser.validate(signal) == True
    
    def test_validate_missing_field(self):
        """Test validation fails with missing field"""
        signal = {
            'strategy': 'V3_COMBINED',
            'signal_type': 'BUY',
            # Missing symbol and timeframe
        }
        
        assert SignalParser.validate(signal) == False
    
    def test_get_routing_key(self):
        """Test routing key generation"""
        signal = {
            'strategy': 'V3_COMBINED',
            'timeframe': '5m'
        }
        
        key = SignalParser.get_routing_key(signal)
        
        assert key == 'V3_COMBINED:5m'
    
    def test_timeframe_normalization_v6(self):
        """Test V6 timeframe normalization"""
        alert = {
            'strategy': 'V6_PRICE_ACTION',
            'signal': 'BUY',
            'symbol': 'EURUSD',
            'timeframe': '60'  # Should normalize to '1h'
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['timeframe'] == '1h'


class TestPluginRouter:
    """Test plugin routing"""
    
    @pytest.fixture(autouse=True)
    def reset_router(self):
        """Reset router singleton before each test"""
        reset_plugin_router()
        yield
        reset_plugin_router()
    
    @pytest.fixture
    def mock_registry(self):
        """Create mock registry"""
        registry = MagicMock()
        registry._plugins = {}
        return registry
    
    @pytest.fixture
    def router(self, mock_registry):
        """Create router with mock registry"""
        return PluginRouter(mock_registry)
    
    @pytest.mark.asyncio
    async def test_route_by_plugin_hint(self, router, mock_registry):
        """Test routing by explicit plugin hint"""
        mock_plugin = MagicMock()
        mock_plugin.enabled = True
        mock_plugin.plugin_id = 'v3_combined'
        mock_plugin.process_signal = AsyncMock(return_value={'status': 'success'})
        mock_registry.get_plugin.return_value = mock_plugin
        
        signal = {'strategy': 'V3_COMBINED', 'plugin_hint': 'v3_combined'}
        result = await router.route_signal(signal)
        
        mock_registry.get_plugin.assert_called_with('v3_combined')
        mock_plugin.process_signal.assert_called_once_with(signal)
        assert result == {'status': 'success'}
    
    @pytest.mark.asyncio
    async def test_route_by_strategy_match(self, router, mock_registry):
        """Test routing by strategy match"""
        mock_plugin = MagicMock()
        mock_plugin.plugin_id = 'v3_combined'
        mock_plugin.process_signal = AsyncMock(return_value={'status': 'success'})
        mock_registry.get_plugin.return_value = None  # No hint match
        mock_registry.get_plugin_for_signal.return_value = mock_plugin
        
        signal = {'strategy': 'V3_COMBINED', 'timeframe': '5m'}
        result = await router.route_signal(signal)
        
        mock_registry.get_plugin_for_signal.assert_called_with(signal)
        assert result == {'status': 'success'}
    
    @pytest.mark.asyncio
    async def test_no_plugin_found(self, router, mock_registry):
        """Test handling when no plugin found"""
        mock_registry.get_plugin.return_value = None
        mock_registry.get_plugin_for_signal.return_value = None
        
        signal = {'strategy': 'UNKNOWN'}
        result = await router.route_signal(signal)
        
        assert result is None
        assert router.get_routing_stats()['no_plugin_found'] == 1
    
    @pytest.mark.asyncio
    async def test_plugin_failure_tracked(self, router, mock_registry):
        """Test plugin failure is tracked"""
        mock_plugin = MagicMock()
        mock_plugin.enabled = True
        mock_plugin.plugin_id = 'v3_combined'
        mock_plugin.process_signal = AsyncMock(side_effect=Exception("Test error"))
        mock_registry.get_plugin.return_value = mock_plugin
        
        signal = {'strategy': 'V3_COMBINED', 'plugin_hint': 'v3_combined'}
        result = await router.route_signal(signal)
        
        assert result['status'] == 'error'
        assert router.get_routing_stats()['failed'] == 1
    
    @pytest.mark.asyncio
    async def test_broadcast_signal(self, router, mock_registry):
        """Test broadcasting signal to multiple plugins"""
        mock_plugin1 = MagicMock()
        mock_plugin1.plugin_id = 'plugin1'
        mock_plugin1.process_signal = AsyncMock(return_value={'status': 'success'})
        
        mock_plugin2 = MagicMock()
        mock_plugin2.plugin_id = 'plugin2'
        mock_plugin2.process_signal = AsyncMock(return_value={'status': 'success'})
        
        mock_registry.broadcast_signal.return_value = [mock_plugin1, mock_plugin2]
        
        signal = {'strategy': 'V3_COMBINED'}
        results = await router.broadcast_signal(signal)
        
        assert len(results) == 2
        assert results[0]['plugin_id'] == 'plugin1'
        assert results[1]['plugin_id'] == 'plugin2'
    
    def test_routing_stats(self, router):
        """Test routing statistics"""
        stats = router.get_routing_stats()
        
        assert 'total_routed' in stats
        assert 'successful' in stats
        assert 'failed' in stats
        assert 'no_plugin_found' in stats
        assert 'success_rate' in stats
    
    def test_reset_stats(self, router):
        """Test resetting statistics"""
        router._routing_stats['total_routed'] = 100
        router.reset_stats()
        
        assert router.get_routing_stats()['total_routed'] == 0
    
    @pytest.mark.asyncio
    async def test_route_with_fallback(self, router, mock_registry):
        """Test routing with fallback handler"""
        mock_registry.get_plugin.return_value = None
        mock_registry.get_plugin_for_signal.return_value = None
        
        fallback_called = False
        async def fallback_handler(signal):
            nonlocal fallback_called
            fallback_called = True
            return {'status': 'fallback'}
        
        signal = {'strategy': 'UNKNOWN'}
        result = await router.route_with_fallback(signal, fallback_handler)
        
        assert fallback_called
        assert result == {'status': 'fallback'}
    
    def test_get_available_routes(self, router, mock_registry):
        """Test getting available routes"""
        mock_plugin = MagicMock()
        mock_plugin.enabled = True
        mock_plugin.get_supported_strategies.return_value = ['V3_COMBINED']
        mock_plugin.get_supported_timeframes.return_value = ['5m', '15m']
        
        mock_registry._plugins = {'v3_combined': mock_plugin}
        
        routes = router.get_available_routes()
        
        assert len(routes) == 1
        assert routes[0]['plugin_id'] == 'v3_combined'
        assert routes[0]['strategies'] == ['V3_COMBINED']


class TestSignalValidator:
    """Test signal validation"""
    
    def test_validate_valid_v3_signal(self):
        """Test validation of valid V3 signal"""
        signal = {
            'strategy': 'V3_COMBINED',
            'signal_type': 'BUY',
            'symbol': 'EURUSD',
            'timeframe': '5m',
            'price': 1.0850,
            'sl_pips': 15,
            'consensus_score': 7
        }
        
        is_valid, errors = SignalValidator.validate(signal)
        
        assert is_valid == True
        assert len(errors) == 0
    
    def test_validate_valid_v6_signal(self):
        """Test validation of valid V6 signal"""
        signal = {
            'strategy': 'V6_PRICE_ACTION',
            'signal_type': 'TRENDLINE_BREAK',
            'symbol': 'GBPUSD',
            'timeframe': '15m',
            'price': 1.2650
        }
        
        is_valid, errors = SignalValidator.validate(signal)
        
        assert is_valid == True
        assert len(errors) == 0
    
    def test_validate_missing_required_field(self):
        """Test validation fails with missing required field"""
        signal = {
            'strategy': 'V3_COMBINED',
            'signal_type': 'BUY',
            # Missing symbol and timeframe
        }
        
        is_valid, errors = SignalValidator.validate(signal)
        
        assert is_valid == False
        assert len(errors) > 0
    
    def test_validate_invalid_symbol(self):
        """Test validation fails with invalid symbol"""
        signal = {
            'strategy': 'V3_COMBINED',
            'signal_type': 'BUY',
            'symbol': 'INVALID',
            'timeframe': '5m'
        }
        
        is_valid, errors = SignalValidator.validate(signal)
        
        assert is_valid == False
        assert any('Invalid symbol' in e for e in errors)
    
    def test_validate_invalid_timeframe(self):
        """Test validation fails with invalid timeframe"""
        signal = {
            'strategy': 'V3_COMBINED',
            'signal_type': 'BUY',
            'symbol': 'EURUSD',
            'timeframe': '2m'  # Invalid
        }
        
        is_valid, errors = SignalValidator.validate(signal)
        
        assert is_valid == False
        assert any('Invalid timeframe' in e for e in errors)
    
    def test_validate_invalid_consensus_score(self):
        """Test validation fails with invalid consensus_score"""
        signal = {
            'strategy': 'V3_COMBINED',
            'signal_type': 'BUY',
            'symbol': 'EURUSD',
            'timeframe': '5m',
            'consensus_score': 15  # Invalid (must be 0-10)
        }
        
        is_valid, errors = SignalValidator.validate(signal)
        
        assert is_valid == False
        assert any('consensus_score' in e for e in errors)
    
    def test_sanitize_signal(self):
        """Test signal sanitization"""
        signal = {
            'symbol': 'eurusd',  # lowercase
            'signal_type': 'buy',  # lowercase
            'strategy': 'v3_combined',  # lowercase
            'price': '1.0850',  # string
            'sl_pips': '15'  # string
        }
        
        sanitized = SignalValidator.sanitize(signal)
        
        assert sanitized['symbol'] == 'EURUSD'
        assert sanitized['signal_type'] == 'BUY'
        assert sanitized['strategy'] == 'V3_COMBINED'
        assert sanitized['price'] == 1.0850
        assert sanitized['sl_pips'] == 15
    
    def test_validate_and_sanitize(self):
        """Test combined validation and sanitization"""
        signal = {
            'strategy': 'v3_combined',
            'signal_type': 'buy',
            'symbol': 'eurusd',
            'timeframe': '5m'
        }
        
        is_valid, sanitized, errors = SignalValidator.validate_and_sanitize(signal)
        
        assert is_valid == True
        assert sanitized['symbol'] == 'EURUSD'
    
    def test_is_valid_symbol(self):
        """Test symbol validation helper"""
        assert SignalValidator.is_valid_symbol('EURUSD') == True
        assert SignalValidator.is_valid_symbol('eurusd') == True
        assert SignalValidator.is_valid_symbol('INVALID') == False
    
    def test_is_valid_timeframe(self):
        """Test timeframe validation helper"""
        assert SignalValidator.is_valid_timeframe('5m') == True
        assert SignalValidator.is_valid_timeframe('1h') == True
        assert SignalValidator.is_valid_timeframe('2m') == False
    
    def test_get_valid_symbols(self):
        """Test getting valid symbols list"""
        symbols = SignalValidator.get_valid_symbols()
        
        assert 'EURUSD' in symbols
        assert 'GBPUSD' in symbols
        assert 'XAUUSD' in symbols


class TestIntegrationFlow:
    """Test complete signal flow"""
    
    @pytest.fixture(autouse=True)
    def reset_router(self):
        """Reset router singleton before each test"""
        reset_plugin_router()
        yield
        reset_plugin_router()
    
    def test_v3_signal_flow(self):
        """Test V3 signal parsing and validation flow"""
        # Raw alert from TradingView
        raw_alert = {
            'type': 'entry_v3',
            'signal': 'BUY',
            'symbol': 'EURUSD',
            'logic': 'LOGIC1',
            'price': 1.0850,
            'sl_pips': 15,
            'consensus_score': 7
        }
        
        # Parse
        signal = SignalParser.parse(raw_alert)
        assert signal is not None
        assert signal['strategy'] == 'V3_COMBINED'
        
        # Validate
        is_valid, errors = SignalValidator.validate(signal)
        assert is_valid == True
        
        # Check routing key
        routing_key = SignalParser.get_routing_key(signal)
        assert routing_key == 'V3_COMBINED:5m'
    
    def test_v6_signal_flow(self):
        """Test V6 signal parsing and validation flow"""
        # Raw alert from TradingView
        raw_alert = {
            'type': 'entry_v6',
            'signal': 'TRENDLINE_BREAK',
            'symbol': 'GBPUSD',
            'timeframe': '15m',
            'trend_pulse': 'STRONG_UP',
            'price': 1.2650
        }
        
        # Parse
        signal = SignalParser.parse(raw_alert)
        assert signal is not None
        assert signal['strategy'] == 'V6_PRICE_ACTION'
        
        # Validate
        is_valid, errors = SignalValidator.validate(signal)
        assert is_valid == True
        
        # Check routing key
        routing_key = SignalParser.get_routing_key(signal)
        assert routing_key == 'V6_PRICE_ACTION:15m'
    
    def test_invalid_signal_rejected(self):
        """Test invalid signal is rejected"""
        raw_alert = {
            'random': 'data',
            'no_strategy': True
        }
        
        signal = SignalParser.parse(raw_alert)
        assert signal is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
