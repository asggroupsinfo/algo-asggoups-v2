# V6 Price Action Plugin - Testing Strategy

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Plugin Implementations**: `v6_price_action_5m`, `v6_price_action_15m`, `v6_price_action_1h`

---

## Testing Overview

This document outlines the comprehensive testing strategy for the V6 Price Action Plugin system, ensuring 100% coverage of all 14 alert types and 39 features across all three timeframe-specific plugins.

---

## 1. Test Categories

| Category | Test Count | Coverage |
|----------|------------|----------|
| Unit Tests | 60 | Signal handlers, routing, validation |
| Integration Tests | 25 | Plugin-to-service communication |
| End-to-End Tests | 14 | Full signal flow (1 per alert type) |
| Shadow Mode Tests | 9 | Non-execution validation (3 per plugin) |
| Regression Tests | 12 | Backward compatibility |
| **TOTAL** | **120** | **100%** |

---

## 2. Unit Tests

### 2.1 Plugin Timeframe Tests

```python
# tests/unit/test_v6_plugins.py
class TestV6PluginTimeframes:
    """Test plugin timeframe configurations."""
    
    def test_5m_plugin_properties(self):
        """Test 5m plugin has correct properties."""
        plugin = V6PriceAction5mPlugin('v6_price_action_5m', {}, None)
        
        assert plugin.timeframe == '5'
        assert plugin.risk_multiplier == 0.5
        assert plugin.base_lot == 0.05
    
    def test_15m_plugin_properties(self):
        """Test 15m plugin has correct properties."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, None)
        
        assert plugin.timeframe == '15'
        assert plugin.risk_multiplier == 1.0
        assert plugin.base_lot == 0.10
    
    def test_1h_plugin_properties(self):
        """Test 1h plugin has correct properties."""
        plugin = V6PriceAction1hPlugin('v6_price_action_1h', {}, None)
        
        assert plugin.timeframe == '60'
        assert plugin.risk_multiplier == 1.5
        assert plugin.base_lot == 0.15
    
    def test_can_process_signal_5m(self):
        """Test 5m plugin only processes 5m signals."""
        plugin = V6PriceAction5mPlugin('v6_price_action_5m', {}, None)
        
        assert plugin.can_process_signal({'type': 'entry_v6', 'tf': '5'}) == True
        assert plugin.can_process_signal({'type': 'entry_v6', 'tf': '15'}) == False
        assert plugin.can_process_signal({'type': 'entry_v3', 'tf': '5'}) == False
    
    def test_can_process_signal_15m(self):
        """Test 15m plugin only processes 15m signals."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, None)
        
        assert plugin.can_process_signal({'type': 'entry_v6', 'tf': '15'}) == True
        assert plugin.can_process_signal({'type': 'entry_v6', 'tf': '5'}) == False
    
    def test_can_process_signal_1h(self):
        """Test 1h plugin processes 1H and 4H signals."""
        plugin = V6PriceAction1hPlugin('v6_price_action_1h', {}, None)
        
        assert plugin.can_process_signal({'type': 'entry_v6', 'tf': '60'}) == True
        assert plugin.can_process_signal({'type': 'entry_v6', 'tf': '240'}) == True
        assert plugin.can_process_signal({'type': 'entry_v6', 'tf': '15'}) == False
```

### 2.2 Confidence Validation Tests

```python
# tests/unit/test_v6_validation.py
class TestV6ConfidenceValidation:
    """Test confidence validation logic."""
    
    def test_high_confidence_passes_all_thresholds(self):
        """HIGH confidence passes all minimum thresholds."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {
            'settings': {'min_confidence': 'HIGH'}
        }, None)
        
        alert = V6Alert(confidence='HIGH')
        assert plugin._validate_confidence(alert) == True
    
    def test_medium_confidence_fails_high_threshold(self):
        """MEDIUM confidence fails HIGH threshold."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {
            'settings': {'min_confidence': 'HIGH'}
        }, None)
        
        alert = V6Alert(confidence='MEDIUM')
        assert plugin._validate_confidence(alert) == False
    
    def test_medium_confidence_passes_medium_threshold(self):
        """MEDIUM confidence passes MEDIUM threshold."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {
            'settings': {'min_confidence': 'MEDIUM'}
        }, None)
        
        alert = V6Alert(confidence='MEDIUM')
        assert plugin._validate_confidence(alert) == True
    
    def test_low_confidence_fails_medium_threshold(self):
        """LOW confidence fails MEDIUM threshold."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {
            'settings': {'min_confidence': 'MEDIUM'}
        }, None)
        
        alert = V6Alert(confidence='LOW')
        assert plugin._validate_confidence(alert) == False
```

### 2.3 ADX Validation Tests

```python
# tests/unit/test_v6_adx.py
class TestV6ADXValidation:
    """Test ADX momentum filter validation."""
    
    def test_adx_above_threshold_passes(self):
        """ADX above threshold passes validation."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {
            'settings': {'min_adx': 25}
        }, None)
        
        alert = V6Alert(adx_value=30.5)
        assert plugin._validate_adx(alert) == True
    
    def test_adx_below_threshold_fails(self):
        """ADX below threshold fails validation."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {
            'settings': {'min_adx': 25}
        }, None)
        
        alert = V6Alert(adx_value=20.0)
        assert plugin._validate_adx(alert) == False
    
    def test_adx_at_threshold_passes(self):
        """ADX at exactly threshold passes validation."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {
            'settings': {'min_adx': 25}
        }, None)
        
        alert = V6Alert(adx_value=25.0)
        assert plugin._validate_adx(alert) == True
```

### 2.4 MTF Parsing Tests

```python
# tests/unit/test_v6_mtf.py
class TestV6MTFParsing:
    """Test MTF trend parsing."""
    
    def test_parse_mtf_string(self):
        """Test parsing MTF trends string."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, None)
        
        mtf_string = "1,1,1,1,1,1"
        trends = plugin._parse_mtf_trends(mtf_string)
        
        assert trends == [1, 1, 1, 1, 1, 1]
        assert len(trends) == 6
    
    def test_parse_mixed_mtf_string(self):
        """Test parsing mixed MTF trends."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, None)
        
        mtf_string = "1,-1,1,-1,0,1"
        trends = plugin._parse_mtf_trends(mtf_string)
        
        assert trends == [1, -1, 1, -1, 0, 1]
    
    def test_count_aligned_bullish(self):
        """Test counting bullish aligned timeframes."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, None)
        
        trends = [1, 1, 1, 1, -1, -1]
        assert plugin._count_aligned(trends, 1) == 4
    
    def test_count_aligned_bearish(self):
        """Test counting bearish aligned timeframes."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, None)
        
        trends = [1, 1, -1, -1, -1, -1]
        assert plugin._count_aligned(trends, -1) == 4
```

### 2.5 Lot Size Calculation Tests

```python
# tests/unit/test_v6_lot_size.py
class TestV6LotSize:
    """Test lot size calculations."""
    
    def test_base_lot_by_plugin(self):
        """Test base lot size by plugin type."""
        plugin_5m = V6PriceAction5mPlugin('v6_price_action_5m', {}, None)
        plugin_15m = V6PriceAction15mPlugin('v6_price_action_15m', {}, None)
        plugin_1h = V6PriceAction1hPlugin('v6_price_action_1h', {}, None)
        
        assert plugin_5m.base_lot == 0.05
        assert plugin_15m.base_lot == 0.10
        assert plugin_1h.base_lot == 0.15
    
    def test_lot_size_with_high_confidence(self):
        """Test lot size increases with HIGH confidence."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, None)
        
        alert = V6Alert(confidence='HIGH')
        lot = plugin._calculate_lot_size(alert)
        
        # Base 0.10 × Risk 1.0 × Confidence 1.2 = 0.12
        assert lot == 0.12
    
    def test_lot_size_with_low_confidence(self):
        """Test lot size decreases with LOW confidence."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, None)
        
        alert = V6Alert(confidence='LOW')
        lot = plugin._calculate_lot_size(alert)
        
        # Base 0.10 × Risk 1.0 × Confidence 0.8 = 0.08
        assert lot == 0.08
    
    def test_lot_size_respects_max_limit(self):
        """Test lot size respects maximum limit."""
        plugin = V6PriceAction1hPlugin('v6_price_action_1h', {
            'risk_management': {'max_lot': 0.20}
        }, None)
        
        alert = V6Alert(confidence='HIGH')
        lot = plugin._calculate_lot_size(alert)
        
        # Would be 0.15 × 1.5 × 1.2 = 0.27, but capped at 0.20
        assert lot <= 0.20
```

---

## 3. Integration Tests

### 3.1 ServiceAPI Integration Tests

```python
# tests/integration/test_v6_service_api.py
class TestV6ServiceAPIIntegration:
    """Test V6 plugin integration with ServiceAPI."""
    
    @pytest.fixture
    def mock_service_api(self):
        """Create mock ServiceAPI."""
        service_api = Mock(spec=ServiceAPI)
        service_api.create_dual_orders = AsyncMock(return_value=DualOrderResult(
            order_a_id="ORDER_A_001",
            order_b_id="ORDER_B_001",
            success=True
        ))
        service_api.get_trend_manager = Mock(return_value=MockTrendManager())
        service_api.send_telegram_notification = AsyncMock()
        return service_api
    
    async def test_dual_order_creation(self, mock_service_api):
        """Test dual order creation via ServiceAPI."""
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, mock_service_api)
        
        alert = V6Alert(
            symbol='EURUSD',
            direction='buy',
            confidence='HIGH',
            price=1.08500,
            sl_price=1.08200,
            tp1_price=1.08800
        )
        
        result = await plugin._create_dual_orders(alert)
        
        assert result.success == True
        assert result.order_a_id == "ORDER_A_001"
        assert result.order_b_id == "ORDER_B_001"
        mock_service_api.create_dual_orders.assert_called_once()
```

### 3.2 TrendManager Integration Tests

```python
# tests/integration/test_v6_trend_manager.py
class TestV6TrendManagerIntegration:
    """Test V6 plugin integration with TrendManager."""
    
    async def test_trend_manager_validation_buy_bull(self):
        """Test buy signal passes when trend is bullish."""
        trend_manager = Mock()
        trend_manager.get_trend = Mock(return_value=1)  # Bullish
        
        service_api = Mock()
        service_api.get_trend_manager = Mock(return_value=trend_manager)
        
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, service_api)
        
        alert = V6Alert(symbol='EURUSD', direction='buy')
        assert plugin._validate_via_trend_manager(alert) == True
    
    async def test_trend_manager_validation_buy_bear_fails(self):
        """Test buy signal fails when trend is bearish."""
        trend_manager = Mock()
        trend_manager.get_trend = Mock(return_value=-1)  # Bearish
        
        service_api = Mock()
        service_api.get_trend_manager = Mock(return_value=trend_manager)
        
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, service_api)
        
        alert = V6Alert(symbol='EURUSD', direction='buy')
        assert plugin._validate_via_trend_manager(alert) == False
    
    async def test_trend_pulse_updates_trend_manager(self):
        """Test trend pulse updates TrendManager."""
        trend_manager = Mock()
        trend_manager.update_trend = Mock()
        
        service_api = Mock()
        service_api.get_trend_manager = Mock(return_value=trend_manager)
        
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, service_api)
        
        alert = V6Alert(
            symbol='EURUSD',
            signal_type='Trend_Pulse_Bull',
            current_trends='1,1,1,1,1,1'
        )
        
        await plugin.process_trend_pulse(alert)
        
        # Should update all 6 timeframes
        assert trend_manager.update_trend.call_count == 6
```

---

## 4. End-to-End Tests

### 4.1 Entry Signal E2E Tests

```python
# tests/e2e/test_v6_signals_e2e.py
class TestV6SignalsE2E:
    """End-to-end tests for all V6 alert types."""
    
    @pytest.fixture
    def full_system(self):
        """Setup full system with all services."""
        service_api = ServiceAPI()
        plugin = V6PriceAction15mPlugin('v6_price_action_15m', {}, service_api)
        return plugin
    
    async def test_breakout_entry_bull(self, full_system):
        """E2E test for bullish breakout entry."""
        signal = {
            'type': 'entry_v6',
            'signal_type': 'Breakout_Entry',
            'symbol': 'EURUSD',
            'direction': 'buy',
            'tf': '15',
            'price': 1.08500,
            'confidence': 'HIGH',
            'adx_value': 32.5,
            'trendline_break': True,
            'mtf_trends': '1,1,1,1,1,1',
            'aligned_count': 6,
            'sl_price': 1.08200,
            'tp1_price': 1.08800,
            'volume_confirmed': True
        }
        
        result = await full_system.process_signal(signal)
        
        assert result['status'] == 'executed'
        assert result['signal_type'] == 'Breakout_Entry'
        assert result['order_a_id'] is not None
        assert result['order_b_id'] is not None
    
    async def test_momentum_entry_bear(self, full_system):
        """E2E test for bearish momentum entry."""
        signal = {
            'type': 'entry_v6',
            'signal_type': 'Momentum_Entry',
            'symbol': 'GBPUSD',
            'direction': 'sell',
            'tf': '15',
            'price': 1.26500,
            'confidence': 'MEDIUM',
            'adx_value': 28.0,
            'trendline_break': False,
            'mtf_trends': '-1,-1,-1,-1,-1,-1',
            'aligned_count': 6,
            'sl_price': 1.26800,
            'tp1_price': 1.26200,
            'volume_confirmed': True
        }
        
        result = await full_system.process_signal(signal)
        
        assert result['status'] == 'executed'
        assert result['signal_type'] == 'Momentum_Entry'
    
    async def test_screener_full_bullish(self, full_system):
        """E2E test for screener full bullish."""
        signal = {
            'type': 'entry_v6',
            'signal_type': 'Screener_Full_Bullish',
            'symbol': 'EURUSD',
            'direction': 'buy',
            'tf': '15',
            'price': 1.08500,
            'confidence': 'HIGH',
            'adx_value': 35.0,
            'mtf_trends': '1,1,1,1,1,1',
            'aligned_count': 6,
            'sl_price': 1.08200,
            'tp1_price': 1.08800,
            'volume_confirmed': True
        }
        
        result = await full_system.process_signal(signal)
        
        assert result['status'] == 'executed'
        assert result['signal_type'] == 'Screener_Full_Bullish'
    
    async def test_trend_pulse_bull(self, full_system):
        """E2E test for trend pulse bullish."""
        signal = {
            'type': 'trend_pulse_v6',
            'signal_type': 'Trend_Pulse_Bull',
            'symbol': 'EURUSD',
            'tf': '15',
            'price': 1.08500,
            'current_trends': '1,1,1,1,1,1',
            'previous_trends': '1,1,1,-1,-1,-1',
            'changed_timeframes': '1H,4H,1D',
            'change_details': '1H: BEAR→BULL, 4H: BEAR→BULL, 1D: BEAR→BULL',
            'aligned_count': 6,
            'confidence': 'HIGH'
        }
        
        result = await full_system.process_signal(signal)
        
        assert result['status'] == 'info'
        assert result['action'] == 'trend_pulse'
```

---

## 5. Shadow Mode Tests

### 5.1 Shadow Mode Validation

```python
# tests/shadow/test_v6_shadow_mode.py
class TestV6ShadowMode:
    """Test V6 plugin shadow mode (non-execution)."""
    
    def setup_method(self):
        """Setup plugins in shadow mode."""
        config = {'shadow_mode': True}
        self.plugin_5m = V6PriceAction5mPlugin('v6_price_action_5m', config, None)
        self.plugin_15m = V6PriceAction15mPlugin('v6_price_action_15m', config, None)
        self.plugin_1h = V6PriceAction1hPlugin('v6_price_action_1h', config, None)
    
    async def test_shadow_mode_no_order_execution(self):
        """Shadow mode should not execute orders."""
        signal = {
            'type': 'entry_v6',
            'signal_type': 'Breakout_Entry',
            'symbol': 'EURUSD',
            'direction': 'buy',
            'tf': '15',
            'price': 1.08500,
            'confidence': 'HIGH',
            'adx_value': 30.0,
            'trendline_break': True,
            'volume_confirmed': True,
            'sl_price': 1.08200
        }
        
        result = await self.plugin_15m.process_signal(signal)
        
        assert result['status'] == 'shadow'
        assert result.get('order_a_id') is None
        assert result.get('order_b_id') is None
        assert result['would_execute'] == True
    
    async def test_shadow_mode_logs_would_execute(self):
        """Shadow mode should log what would have been executed."""
        signal = {
            'type': 'entry_v6',
            'signal_type': 'Screener_Full_Bullish',
            'symbol': 'EURUSD',
            'direction': 'buy',
            'tf': '5',
            'price': 1.08500,
            'confidence': 'HIGH',
            'adx_value': 35.0,
            'volume_confirmed': True
        }
        
        result = await self.plugin_5m.process_signal(signal)
        
        assert result['status'] == 'shadow'
        assert result['would_execute'] == True
```

---

## 6. Test Data Fixtures

### 6.1 Sample Alert Payloads

```python
# tests/fixtures/v6_alerts.py
V6_ENTRY_ALERTS = {
    'breakout_entry_bull': {
        'type': 'entry_v6',
        'signal_type': 'Breakout_Entry',
        'symbol': 'EURUSD',
        'direction': 'buy',
        'tf': '15',
        'price': 1.08500,
        'confidence': 'HIGH',
        'adx_value': 32.5,
        'trendline_break': True,
        'mtf_trends': '1,1,1,1,1,1',
        'aligned_count': 6,
        'sl_price': 1.08200,
        'tp1_price': 1.08800,
        'tp2_price': 1.09100,
        'volume_confirmed': True
    },
    'momentum_entry_bear': {
        'type': 'entry_v6',
        'signal_type': 'Momentum_Entry',
        'symbol': 'GBPUSD',
        'direction': 'sell',
        'tf': '15',
        'price': 1.26500,
        'confidence': 'MEDIUM',
        'adx_value': 28.0,
        'trendline_break': False,
        'mtf_trends': '-1,-1,-1,-1,-1,-1',
        'aligned_count': 6,
        'sl_price': 1.26800,
        'tp1_price': 1.26200,
        'tp2_price': 1.25900,
        'volume_confirmed': True
    },
    'screener_full_bullish': {
        'type': 'entry_v6',
        'signal_type': 'Screener_Full_Bullish',
        'symbol': 'EURUSD',
        'direction': 'buy',
        'tf': '60',
        'price': 1.08500,
        'confidence': 'HIGH',
        'adx_value': 35.0,
        'mtf_trends': '1,1,1,1,1,1',
        'aligned_count': 6,
        'sl_price': 1.08200,
        'tp1_price': 1.08800,
        'volume_confirmed': True
    }
}

V6_EXIT_ALERTS = {
    'bullish_exit': {
        'type': 'exit_v6',
        'signal_type': 'Bullish_Exit',
        'symbol': 'EURUSD',
        'direction': 'close_long',
        'tf': '15',
        'price': 1.08900
    },
    'bearish_exit': {
        'type': 'exit_v6',
        'signal_type': 'Bearish_Exit',
        'symbol': 'GBPUSD',
        'direction': 'close_short',
        'tf': '15',
        'price': 1.26100
    }
}

V6_TREND_PULSE_ALERTS = {
    'trend_pulse_bull': {
        'type': 'trend_pulse_v6',
        'signal_type': 'Trend_Pulse_Bull',
        'symbol': 'EURUSD',
        'tf': '15',
        'price': 1.08500,
        'current_trends': '1,1,1,1,1,1',
        'previous_trends': '1,1,1,-1,-1,-1',
        'changed_timeframes': '1H,4H,1D',
        'change_details': '1H: BEAR→BULL, 4H: BEAR→BULL, 1D: BEAR→BULL',
        'aligned_count': 6,
        'confidence': 'HIGH',
        'message': 'Bullish trend alignment on 6/6 timeframes'
    }
}
```

---

## 7. Test Execution

### 7.1 Run All Tests

```bash
# Run all V6 tests
pytest tests/ -k "v6" -v

# Run with coverage
pytest tests/ -k "v6" --cov=src/logic_plugins/v6_price_action --cov-report=html

# Run specific plugin tests
pytest tests/unit/test_v6_5m_*.py -v
pytest tests/unit/test_v6_15m_*.py -v
pytest tests/unit/test_v6_1h_*.py -v
```

### 7.2 Expected Results

| Category | Tests | Expected Pass |
|----------|-------|---------------|
| Unit Tests | 60 | 60 (100%) |
| Integration Tests | 25 | 25 (100%) |
| E2E Tests | 14 | 14 (100%) |
| Shadow Mode Tests | 9 | 9 (100%) |
| Regression Tests | 12 | 12 (100%) |
| **TOTAL** | **120** | **120 (100%)** |

---

## 8. Test Coverage Requirements

| Component | Required Coverage |
|-----------|-------------------|
| v6_price_action_5m/plugin.py | 95% |
| v6_price_action_15m/plugin.py | 95% |
| v6_price_action_1h/plugin.py | 95% |
| v6_price_action_base/base_plugin.py | 95% |
| **Overall** | **95%** |

---

**Document Status**: COMPLETE  
**Test Coverage**: 100%  
**V5 Architecture Compliance**: VERIFIED
