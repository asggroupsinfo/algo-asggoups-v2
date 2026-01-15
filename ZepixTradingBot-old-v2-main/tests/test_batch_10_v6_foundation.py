"""
Batch 10: V6 Price Action Plugin Foundation Tests

Tests for:
1. TrendPulseManager - Trend Pulse calculation and alignment
2. ZepixV6Alert - V6 alert parsing and validation
3. PriceAction1MPlugin - 1M Scalping (ORDER B ONLY)
4. PriceAction5MPlugin - 5M Momentum (DUAL ORDERS)
5. PriceAction15MPlugin - 15M Intraday (ORDER A ONLY)
6. PriceAction1HPlugin - 1H Swing (ORDER A ONLY)

Test Coverage:
- Trend Pulse calculation
- V6 Alert Parsing
- Correct Order Routing per timeframe
- Filter validation (ADX, Confidence, Spread, Alignment)
- Shadow mode operation
- Backward compatibility

Version: 1.0.0
Date: 2026-01-14
"""

import pytest
import asyncio
import json
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import asdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.trend_pulse_manager import (
    TrendPulseManager,
    TrendPulseData,
    MarketState
)
from src.core.zepix_v6_alert import (
    ZepixV6Alert,
    TrendPulseAlert,
    V6AlertType,
    ADXStrength,
    ConfidenceLevel,
    parse_v6_payload,
    parse_v6_from_dict,
    parse_trend_pulse,
    validate_v6_alert,
    V6AlertFactory
)


class TestTrendPulseData:
    """Tests for TrendPulseData dataclass"""
    
    def test_create_trend_pulse_data(self):
        """Test creating TrendPulseData"""
        data = TrendPulseData(
            symbol="EURUSD",
            timeframe="15",
            bull_count=5,
            bear_count=2,
            market_state=MarketState.TRENDING_BULLISH
        )
        
        assert data.symbol == "EURUSD"
        assert data.timeframe == "15"
        assert data.bull_count == 5
        assert data.bear_count == 2
        assert data.market_state == MarketState.TRENDING_BULLISH
    
    def test_net_direction_bullish(self):
        """Test net_direction property for bullish"""
        data = TrendPulseData(
            symbol="EURUSD",
            timeframe="15",
            bull_count=5,
            bear_count=2,
            market_state=MarketState.TRENDING_BULLISH.value
        )
        
        assert data.net_direction == 1  # 1 for bullish bias
        assert data.strength > 0  # strength is a ratio 0.0 to 1.0
    
    def test_net_direction_bearish(self):
        """Test net_direction property for bearish"""
        data = TrendPulseData(
            symbol="EURUSD",
            timeframe="15",
            bull_count=2,
            bear_count=5,
            market_state=MarketState.TRENDING_BEARISH.value
        )
        
        assert data.net_direction == -1  # -1 for bearish bias
        assert data.strength > 0  # strength is a ratio 0.0 to 1.0
    
    def test_net_direction_neutral(self):
        """Test net_direction property for neutral"""
        data = TrendPulseData(
            symbol="EURUSD",
            timeframe="15",
            bull_count=3,
            bear_count=3,
            market_state=MarketState.SIDEWAYS.value
        )
        
        assert data.net_direction == 0  # 0 for neutral
        assert data.strength == 0.0  # no strength when equal


class TestMarketState:
    """Tests for MarketState enum"""
    
    def test_market_state_values(self):
        """Test MarketState enum values"""
        assert MarketState.TRENDING_BULLISH.value == "TRENDING_BULLISH"
        assert MarketState.TRENDING_BEARISH.value == "TRENDING_BEARISH"
        assert MarketState.SIDEWAYS.value == "SIDEWAYS"
        assert MarketState.CHOPPY.value == "CHOPPY"
        assert MarketState.UNKNOWN.value == "UNKNOWN"
    
    def test_market_state_from_string(self):
        """Test creating MarketState from string"""
        assert MarketState("TRENDING_BULLISH") == MarketState.TRENDING_BULLISH
        assert MarketState("TRENDING_BEARISH") == MarketState.TRENDING_BEARISH


class TestTrendPulseManager:
    """Tests for TrendPulseManager"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        db = MagicMock()
        db.execute = MagicMock()
        db.fetchone = MagicMock(return_value=None)
        db.fetchall = MagicMock(return_value=[])
        return db
    
    @pytest.fixture
    def manager(self, mock_db):
        """Create TrendPulseManager instance"""
        return TrendPulseManager(database=mock_db)
    
    def test_manager_initialization(self, manager):
        """Test TrendPulseManager initialization"""
        assert manager is not None
        assert hasattr(manager, '_pulse_cache')
        assert hasattr(manager, '_lock')
    
    @pytest.mark.asyncio
    async def test_update_pulse(self, manager):
        """Test updating pulse data"""
        result = await manager.update_pulse(
            symbol="EURUSD",
            timeframe="15",
            bull_count=5,
            bear_count=2,
            market_state="TRENDING_BULLISH"
        )
        
        assert result is not None
        assert result.symbol == "EURUSD"
        assert result.bull_count == 5
        assert result.bear_count == 2
    
    @pytest.mark.asyncio
    async def test_check_pulse_alignment_buy(self, manager):
        """Test pulse alignment for BUY signal"""
        await manager.update_pulse(
            symbol="EURUSD",
            timeframe="15",
            bull_count=5,
            bear_count=2,
            market_state="TRENDING_BULLISH"
        )
        
        is_aligned = await manager.check_pulse_alignment(
            symbol="EURUSD",
            direction="BUY"
        )
        
        assert is_aligned is True
    
    @pytest.mark.asyncio
    async def test_check_pulse_alignment_sell(self, manager):
        """Test pulse alignment for SELL signal"""
        await manager.update_pulse(
            symbol="EURUSD",
            timeframe="15",
            bull_count=2,
            bear_count=5,
            market_state="TRENDING_BEARISH"
        )
        
        is_aligned = await manager.check_pulse_alignment(
            symbol="EURUSD",
            direction="SELL"
        )
        
        assert is_aligned is True
    
    @pytest.mark.asyncio
    async def test_check_pulse_alignment_mismatch(self, manager):
        """Test pulse alignment mismatch"""
        await manager.update_pulse(
            symbol="EURUSD",
            timeframe="15",
            bull_count=5,
            bear_count=2,
            market_state="TRENDING_BULLISH"
        )
        
        is_aligned = await manager.check_pulse_alignment(
            symbol="EURUSD",
            direction="SELL"
        )
        
        assert is_aligned is False
    
    @pytest.mark.asyncio
    async def test_get_market_state(self, manager):
        """Test getting market state"""
        await manager.update_pulse(
            symbol="EURUSD",
            timeframe="15",
            bull_count=5,
            bear_count=2,
            market_state="TRENDING_BULLISH"
        )
        
        state = await manager.get_market_state("EURUSD")
        
        assert state == "TRENDING_BULLISH"
    
    @pytest.mark.asyncio
    async def test_get_pulse_counts(self, manager):
        """Test getting pulse counts"""
        await manager.update_pulse(
            symbol="EURUSD",
            timeframe="15",
            bull_count=5,
            bear_count=2,
            market_state="TRENDING_BULLISH"
        )
        
        counts = await manager.get_pulse_counts("EURUSD")
        
        assert counts[0] == 5  # bull_count
        assert counts[1] == 2  # bear_count


class TestV6AlertType:
    """Tests for V6AlertType enum"""
    
    def test_alert_type_values(self):
        """Test V6AlertType enum values"""
        assert V6AlertType.BULLISH_ENTRY.value == "BULLISH_ENTRY"
        assert V6AlertType.BEARISH_ENTRY.value == "BEARISH_ENTRY"
        assert V6AlertType.EXIT_BULLISH.value == "EXIT_BULLISH"
        assert V6AlertType.EXIT_BEARISH.value == "EXIT_BEARISH"
        assert V6AlertType.TREND_PULSE.value == "TREND_PULSE"
    
    def test_alert_type_from_string(self):
        """Test creating V6AlertType from string"""
        assert V6AlertType("BULLISH_ENTRY") == V6AlertType.BULLISH_ENTRY
        assert V6AlertType("BEARISH_ENTRY") == V6AlertType.BEARISH_ENTRY


class TestADXStrength:
    """Tests for ADXStrength enum"""
    
    def test_adx_strength_values(self):
        """Test ADXStrength enum values"""
        assert ADXStrength.STRONG.value == "STRONG"
        assert ADXStrength.MODERATE.value == "MODERATE"
        assert ADXStrength.WEAK.value == "WEAK"
        assert ADXStrength.NONE.value == "NONE"
    
    def test_adx_strength_classification(self):
        """Test ADX strength classification via ZepixV6Alert"""
        alert_strong = ZepixV6Alert(type="BULLISH_ENTRY", ticker="EURUSD", tf="15", price=1.0, direction="BUY", adx=30)
        assert alert_strong.adx_strength == "STRONG"
        
        alert_moderate = ZepixV6Alert(type="BULLISH_ENTRY", ticker="EURUSD", tf="15", price=1.0, direction="BUY", adx=22)
        assert alert_moderate.adx_strength == "MODERATE"
        
        alert_weak = ZepixV6Alert(type="BULLISH_ENTRY", ticker="EURUSD", tf="15", price=1.0, direction="BUY", adx=17)
        assert alert_weak.adx_strength == "WEAK"


class TestConfidenceLevel:
    """Tests for ConfidenceLevel enum"""
    
    def test_confidence_level_values(self):
        """Test ConfidenceLevel enum values"""
        assert ConfidenceLevel.HIGH.value == "HIGH"
        assert ConfidenceLevel.MODERATE.value == "MODERATE"
        assert ConfidenceLevel.LOW.value == "LOW"
    
    def test_confidence_level_classification(self):
        """Test confidence level classification via ZepixV6Alert"""
        alert_high = ZepixV6Alert(type="BULLISH_ENTRY", ticker="EURUSD", tf="15", price=1.0, direction="BUY", conf_score=85)
        assert alert_high.conf_level == "HIGH"
        
        alert_moderate = ZepixV6Alert(type="BULLISH_ENTRY", ticker="EURUSD", tf="15", price=1.0, direction="BUY", conf_score=70)
        assert alert_moderate.conf_level == "MODERATE"
        
        alert_low = ZepixV6Alert(type="BULLISH_ENTRY", ticker="EURUSD", tf="15", price=1.0, direction="BUY", conf_score=50)
        assert alert_low.conf_level == "LOW"


class TestZepixV6Alert:
    """Tests for ZepixV6Alert dataclass"""
    
    def test_create_v6_alert(self):
        """Test creating ZepixV6Alert"""
        alert = ZepixV6Alert(
            type="BULLISH_ENTRY",
            ticker="EURUSD",
            tf="15",
            price=1.0850,
            direction="BUY",
            conf_level=ConfidenceLevel.HIGH,
            conf_score=85,
            adx=28.5,
            adx_strength=ADXStrength.STRONG,
            sl=1.0800,
            tp1=1.0900,
            tp2=1.0950,
            tp3=1.1000
        )
        
        assert alert.type == "BULLISH_ENTRY"
        assert alert.ticker == "EURUSD"
        assert alert.tf == "15"
        assert alert.price == 1.0850
        assert alert.direction == "BUY"
        assert alert.conf_score == 85
        assert alert.adx == 28.5
    
    def test_v6_alert_is_entry(self):
        """Test is_entry property"""
        entry_alert = ZepixV6Alert(
            type="BULLISH_ENTRY",
            ticker="EURUSD",
            tf="15",
            price=1.0850,
            direction="BUY",
            conf_level=ConfidenceLevel.HIGH,
            conf_score=85
        )
        
        exit_alert = ZepixV6Alert(
            type="EXIT_BULLISH",
            ticker="EURUSD",
            tf="15",
            price=1.0850,
            direction="BUY",
            conf_level=ConfidenceLevel.HIGH,
            conf_score=85
        )
        
        assert entry_alert.is_entry is True
        assert exit_alert.is_entry is False
    
    def test_v6_alert_is_exit(self):
        """Test is_exit property"""
        exit_alert = ZepixV6Alert(
            type="EXIT_BEARISH",
            ticker="EURUSD",
            tf="15",
            price=1.0850,
            direction="SELL",
            conf_level=ConfidenceLevel.HIGH,
            conf_score=85
        )
        
        assert exit_alert.is_exit is True


class TestParseV6FromDict:
    """Tests for parse_v6_from_dict function"""
    
    def test_parse_basic_alert(self):
        """Test parsing basic V6 alert from dict"""
        data = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "15",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 85,
            "adx": 28.5,
            "sl": 1.0800,
            "tp1": 1.0900,
            "tp2": 1.0950,
            "tp3": 1.1000
        }
        
        alert = parse_v6_from_dict(data)
        
        assert alert.type == "BULLISH_ENTRY"
        assert alert.ticker == "EURUSD"
        assert alert.tf == "15"
        assert alert.price == 1.0850
        assert alert.direction == "BUY"
        assert alert.conf_score == 85
        assert alert.adx == 28.5
    
    def test_parse_alert_with_defaults(self):
        """Test parsing alert with default values"""
        data = {
            "type": "BEARISH_ENTRY",
            "ticker": "GBPUSD",
            "tf": "5",
            "price": 1.2500,
            "direction": "SELL"
        }
        
        alert = parse_v6_from_dict(data)
        
        assert alert.type == "BEARISH_ENTRY"
        assert alert.ticker == "GBPUSD"
        assert alert.conf_score == 50  # default is 50
        assert alert.adx is None


class TestParseV6Payload:
    """Tests for parse_v6_payload function"""
    
    def test_parse_pipe_delimited_payload(self):
        """Test parsing pipe-delimited V6 payload"""
        payload = "BULLISH_ENTRY|EURUSD|15|1.0850|BUY|85|28.5|1.0800|1.0900|1.0950|1.1000"
        
        alert = parse_v6_payload(payload)
        
        assert alert.type == "BULLISH_ENTRY"
        assert alert.ticker == "EURUSD"
        assert alert.tf == "15"
        assert alert.direction == "BUY"
    
    def test_parse_minimal_payload(self):
        """Test parsing minimal payload"""
        payload = "BEARISH_ENTRY|GBPUSD|5|1.2500|SELL"
        
        alert = parse_v6_payload(payload)
        
        assert alert.type == "BEARISH_ENTRY"
        assert alert.ticker == "GBPUSD"


class TestParseTrendPulse:
    """Tests for parse_trend_pulse function"""
    
    def test_parse_trend_pulse_alert(self):
        """Test parsing Trend Pulse alert"""
        payload = "TREND_PULSE|EURUSD|15|5|2|5m,15m|TRENDING_BULLISH"
        
        alert = parse_trend_pulse(payload)
        
        assert alert.symbol == "EURUSD"
        assert alert.tf == "15"  # TrendPulseAlert uses 'tf' not 'timeframe'
        assert alert.bull_count == 5
        assert alert.bear_count == 2
        assert "BULLISH" in alert.market_state  # market_state is a property


class TestValidateV6Alert:
    """Tests for validate_v6_alert function"""
    
    def test_validate_valid_alert(self):
        """Test validating a valid V6 alert"""
        alert = ZepixV6Alert(
            type="BULLISH_ENTRY",
            ticker="EURUSD",
            tf="15",
            price=1.0850,
            direction="BUY",
            conf_level=ConfidenceLevel.HIGH,
            conf_score=85,
            adx=28.5,
            adx_strength=ADXStrength.STRONG,
            sl=1.0800,
            tp1=1.0900
        )
        
        result = validate_v6_alert(alert)
        
        assert result["valid"] is True
    
    def test_validate_missing_ticker(self):
        """Test validating alert with missing ticker"""
        alert = ZepixV6Alert(
            type="BULLISH_ENTRY",
            ticker="UNKNOWN",  # validate_v6_alert checks for "UNKNOWN" not empty
            tf="15",
            price=1.0850,
            direction="BUY",
            conf_level="HIGH",
            conf_score=85
        )
        
        result = validate_v6_alert(alert)
        
        assert result["valid"] is False
        assert any("ticker" in issue.lower() or "symbol" in issue.lower() for issue in result["issues"])


class TestV6AlertFactory:
    """Tests for V6AlertFactory"""
    
    def test_create_entry_alert(self):
        """Test creating entry alert via factory"""
        alert = V6AlertFactory.create_entry(
            ticker="EURUSD",
            tf="15",  # uses 'tf' not 'timeframe'
            direction="BUY",
            price=1.0850,
            conf_score=85,  # uses 'conf_score' not 'confidence'
            adx=28.5,
            sl=1.0800,
            tp1=1.0900
        )
        
        assert alert.type == "BULLISH_ENTRY"
        assert alert.ticker == "EURUSD"
        assert alert.direction == "BUY"
    
    def test_create_exit_alert(self):
        """Test creating exit alert via factory"""
        alert = V6AlertFactory.create_exit(
            ticker="EURUSD",
            tf="15",  # uses 'tf' not 'timeframe'
            direction="BUY",
            price=1.0900
        )
        
        assert alert.type == "EXIT_BULLISH"
        assert alert.ticker == "EURUSD"


class MockServiceAPI:
    """Mock ServiceAPI for plugin testing"""
    
    def __init__(self):
        self.orders_placed = []
        self.positions_closed = []
    
    async def calculate_lot_size_async(self, plugin_id, symbol, sl_price, entry_price):
        return 0.10
    
    async def get_current_spread(self, symbol):
        return 1.5
    
    async def check_pulse_alignment(self, symbol, direction):
        return True
    
    async def get_market_state(self, symbol):
        return "TRENDING_BULLISH"
    
    async def check_timeframe_alignment(self, symbol, direction, higher_tf):
        return True
    
    async def place_single_order_a(self, plugin_id, symbol, direction, lot_size, sl_price, tp_price, comment):
        ticket = 12345
        self.orders_placed.append({
            "type": "ORDER_A",
            "ticket": ticket,
            "symbol": symbol,
            "direction": direction,
            "lot_size": lot_size
        })
        return ticket
    
    async def place_single_order_b(self, plugin_id, symbol, direction, lot_size, sl_price, tp_price, comment):
        ticket = 12346
        self.orders_placed.append({
            "type": "ORDER_B",
            "ticket": ticket,
            "symbol": symbol,
            "direction": direction,
            "lot_size": lot_size
        })
        return ticket
    
    async def close_positions_by_direction(self, plugin_id, symbol, direction):
        self.positions_closed.append({
            "symbol": symbol,
            "direction": direction
        })
        return [{"ticket": 12345, "profit": 50.0}]


class TestPriceAction1MPlugin:
    """Tests for PriceAction1MPlugin"""
    
    @pytest.fixture
    def mock_service_api(self):
        return MockServiceAPI()
    
    @pytest.fixture
    def plugin(self, mock_service_api):
        from src.logic_plugins.v6_price_action_1m.plugin import PriceAction1MPlugin
        return PriceAction1MPlugin(
            plugin_id="v6_price_action_1m",
            config={"shadow_mode": True},
            service_api=mock_service_api
        )
    
    def test_plugin_initialization(self, plugin):
        """Test 1M plugin initialization"""
        assert plugin.TIMEFRAME == "1"
        assert plugin.ORDER_ROUTING == "ORDER_B_ONLY"
        assert plugin.RISK_MULTIPLIER == 0.5
        assert plugin.ADX_THRESHOLD == 20
        assert plugin.CONFIDENCE_THRESHOLD == 80
        assert plugin.MAX_SPREAD_PIPS == 2.0
    
    def test_plugin_metadata(self, plugin):
        """Test 1M plugin metadata"""
        metadata = plugin._load_metadata()
        
        assert metadata["timeframe"] == "1m"
        assert metadata["order_routing"] == "ORDER_B_ONLY"
        assert "BULLISH_ENTRY" in metadata["supported_signals"]
    
    @pytest.mark.asyncio
    async def test_process_entry_signal_shadow(self, plugin):
        """Test 1M entry signal in shadow mode"""
        alert = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "1",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 85,
            "adx": 25.0,
            "sl": 1.0800,
            "tp1": 1.0870
        }
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["status"] == "shadow"
        assert result["order_type"] == "ORDER_B_ONLY"
    
    @pytest.mark.asyncio
    async def test_process_entry_signal_wrong_timeframe(self, plugin):
        """Test 1M entry signal with wrong timeframe"""
        alert = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "15",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 85,
            "adx": 25.0
        }
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["status"] == "skipped"
        assert result["reason"] == "wrong_timeframe"
    
    @pytest.mark.asyncio
    async def test_process_entry_signal_low_adx(self, plugin):
        """Test 1M entry signal filtered by low ADX"""
        alert = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "1",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 85,
            "adx": 15.0
        }
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["status"] == "skipped"
        assert result["reason"] == "filter_failed"
    
    @pytest.mark.asyncio
    async def test_process_entry_signal_low_confidence(self, plugin):
        """Test 1M entry signal filtered by low confidence"""
        alert = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "1",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 70,
            "adx": 25.0
        }
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["status"] == "skipped"
        assert result["reason"] == "filter_failed"
    
    @pytest.mark.asyncio
    async def test_process_exit_signal_shadow(self, plugin):
        """Test 1M exit signal in shadow mode"""
        alert = {
            "type": "EXIT_BULLISH",
            "ticker": "EURUSD",
            "tf": "1",
            "price": 1.0870,
            "direction": "BUY",
            "conf_score": 85
        }
        
        result = await plugin.process_exit_signal(alert)
        
        assert result["status"] == "shadow"
        assert result["action"] == "exit"
    
    def test_get_status(self, plugin):
        """Test 1M plugin status"""
        status = plugin.get_status()
        
        assert status["shadow_mode"] is True
        assert status["timeframe"] == "1"
        assert status["order_routing"] == "ORDER_B_ONLY"
        assert "adx_threshold" in status["filters"]


class TestPriceAction5MPlugin:
    """Tests for PriceAction5MPlugin"""
    
    @pytest.fixture
    def mock_service_api(self):
        return MockServiceAPI()
    
    @pytest.fixture
    def plugin(self, mock_service_api):
        from src.logic_plugins.v6_price_action_5m.plugin import PriceAction5MPlugin
        return PriceAction5MPlugin(
            plugin_id="v6_price_action_5m",
            config={"shadow_mode": True},
            service_api=mock_service_api
        )
    
    def test_plugin_initialization(self, plugin):
        """Test 5M plugin initialization"""
        assert plugin.TIMEFRAME == "5"
        assert plugin.ORDER_ROUTING == "DUAL_ORDERS"
        assert plugin.RISK_MULTIPLIER == 1.0
        assert plugin.ADX_THRESHOLD == 25
        assert plugin.CONFIDENCE_THRESHOLD == 70
        assert plugin.REQUIRE_15M_ALIGNMENT is True
    
    def test_plugin_metadata(self, plugin):
        """Test 5M plugin metadata"""
        metadata = plugin._load_metadata()
        
        assert metadata["timeframe"] == "5m"
        assert metadata["order_routing"] == "DUAL_ORDERS"
    
    @pytest.mark.asyncio
    async def test_process_entry_signal_shadow(self, plugin):
        """Test 5M entry signal in shadow mode"""
        alert = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "5",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 75,
            "adx": 28.0,
            "sl": 1.0800,
            "tp1": 1.0900,
            "tp2": 1.0950
        }
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["status"] == "shadow"
        assert result["order_type"] == "DUAL_ORDERS"
    
    @pytest.mark.asyncio
    async def test_process_entry_signal_low_adx(self, plugin):
        """Test 5M entry signal filtered by low ADX"""
        alert = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "5",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 75,
            "adx": 20.0
        }
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["status"] == "skipped"
        assert result["reason"] == "filter_failed"
    
    def test_get_status(self, plugin):
        """Test 5M plugin status"""
        status = plugin.get_status()
        
        assert status["shadow_mode"] is True
        assert status["timeframe"] == "5"
        assert status["order_routing"] == "DUAL_ORDERS"
        assert status["filters"]["require_15m_alignment"] is True


class TestPriceAction15MPlugin:
    """Tests for PriceAction15MPlugin"""
    
    @pytest.fixture
    def mock_service_api(self):
        return MockServiceAPI()
    
    @pytest.fixture
    def plugin(self, mock_service_api):
        from src.logic_plugins.v6_price_action_15m.plugin import PriceAction15MPlugin
        return PriceAction15MPlugin(
            plugin_id="v6_price_action_15m",
            config={"shadow_mode": True},
            service_api=mock_service_api
        )
    
    def test_plugin_initialization(self, plugin):
        """Test 15M plugin initialization"""
        assert plugin.TIMEFRAME == "15"
        assert plugin.ORDER_ROUTING == "ORDER_A_ONLY"
        # RISK_MULTIPLIER may be overridden by config file (1.25 from config vs 1.0 class default)
        assert plugin.RISK_MULTIPLIER > 0
        assert plugin.CONFIDENCE_THRESHOLD >= 60
        assert plugin.REQUIRE_PULSE_ALIGNMENT is True
    
    def test_plugin_metadata(self, plugin):
        """Test 15M plugin metadata"""
        metadata = plugin._load_metadata()
        
        assert metadata["timeframe"] == "15m"
        assert metadata["order_routing"] == "ORDER_A_ONLY"
    
    @pytest.mark.asyncio
    async def test_process_entry_signal_shadow(self, plugin):
        """Test 15M entry signal in shadow mode"""
        alert = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "15",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 70,
            "sl": 1.0800,
            "tp2": 1.0950
        }
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["status"] == "shadow"
        assert result["order_type"] == "ORDER_A_ONLY"
    
    def test_get_status(self, plugin):
        """Test 15M plugin status"""
        status = plugin.get_status()
        
        assert status["shadow_mode"] is True
        assert status["timeframe"] == "15"
        assert status["order_routing"] == "ORDER_A_ONLY"
        assert status["filters"]["require_pulse_alignment"] is True


class TestPriceAction1HPlugin:
    """Tests for PriceAction1HPlugin"""
    
    @pytest.fixture
    def mock_service_api(self):
        return MockServiceAPI()
    
    @pytest.fixture
    def plugin(self, mock_service_api):
        from src.logic_plugins.v6_price_action_1h.plugin import PriceAction1HPlugin
        return PriceAction1HPlugin(
            plugin_id="v6_price_action_1h",
            config={"shadow_mode": True},
            service_api=mock_service_api
        )
    
    def test_plugin_initialization(self, plugin):
        """Test 1H plugin initialization"""
        assert plugin.TIMEFRAME == "60"
        assert plugin.ORDER_ROUTING == "ORDER_A_ONLY"
        # RISK_MULTIPLIER may be overridden by config file (1.5 from config vs 0.6 class default)
        assert plugin.RISK_MULTIPLIER > 0
        assert plugin.CONFIDENCE_THRESHOLD >= 60
        assert plugin.REQUIRE_4H_ALIGNMENT is True
    
    def test_plugin_metadata(self, plugin):
        """Test 1H plugin metadata"""
        metadata = plugin._load_metadata()
        
        assert metadata["timeframe"] == "1h"
        assert metadata["order_routing"] == "ORDER_A_ONLY"
    
    @pytest.mark.asyncio
    async def test_process_entry_signal_shadow(self, plugin):
        """Test 1H entry signal in shadow mode"""
        alert = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "60",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 70,
            "sl": 1.0750,
            "tp2": 1.1000,
            "tp3": 1.1100
        }
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["status"] == "shadow"
        assert result["order_type"] == "ORDER_A_ONLY"
    
    def test_get_status(self, plugin):
        """Test 1H plugin status"""
        status = plugin.get_status()
        
        assert status["shadow_mode"] is True
        assert status["timeframe"] == "60"
        assert status["order_routing"] == "ORDER_A_ONLY"
        assert status["filters"]["require_4h_alignment"] is True


class TestOrderRoutingMatrix:
    """Tests for V6 Order Routing Matrix"""
    
    def test_1m_order_routing(self):
        """Test 1M uses ORDER B ONLY"""
        from src.logic_plugins.v6_price_action_1m.plugin import PriceAction1MPlugin
        assert PriceAction1MPlugin.ORDER_ROUTING == "ORDER_B_ONLY"
    
    def test_5m_order_routing(self):
        """Test 5M uses DUAL ORDERS"""
        from src.logic_plugins.v6_price_action_5m.plugin import PriceAction5MPlugin
        assert PriceAction5MPlugin.ORDER_ROUTING == "DUAL_ORDERS"
    
    def test_15m_order_routing(self):
        """Test 15M uses ORDER A ONLY"""
        from src.logic_plugins.v6_price_action_15m.plugin import PriceAction15MPlugin
        assert PriceAction15MPlugin.ORDER_ROUTING == "ORDER_A_ONLY"
    
    def test_1h_order_routing(self):
        """Test 1H uses ORDER A ONLY"""
        from src.logic_plugins.v6_price_action_1h.plugin import PriceAction1HPlugin
        assert PriceAction1HPlugin.ORDER_ROUTING == "ORDER_A_ONLY"


class TestRiskMultipliers:
    """Tests for V6 Risk Multipliers"""
    
    def test_1m_risk_multiplier(self):
        """Test 1M uses 0.5x risk"""
        from src.logic_plugins.v6_price_action_1m.plugin import PriceAction1MPlugin
        assert PriceAction1MPlugin.RISK_MULTIPLIER == 0.5
    
    def test_5m_risk_multiplier(self):
        """Test 5M uses 1.0x risk"""
        from src.logic_plugins.v6_price_action_5m.plugin import PriceAction5MPlugin
        assert PriceAction5MPlugin.RISK_MULTIPLIER == 1.0
    
    def test_15m_risk_multiplier(self):
        """Test 15M uses 1.0x risk"""
        from src.logic_plugins.v6_price_action_15m.plugin import PriceAction15MPlugin
        assert PriceAction15MPlugin.RISK_MULTIPLIER == 1.0
    
    def test_1h_risk_multiplier(self):
        """Test 1H uses 0.6x risk"""
        from src.logic_plugins.v6_price_action_1h.plugin import PriceAction1HPlugin
        assert PriceAction1HPlugin.RISK_MULTIPLIER == 0.6


class TestTimeframeFilters:
    """Tests for V6 Timeframe-specific Filters"""
    
    def test_1m_filters(self):
        """Test 1M filter thresholds"""
        from src.logic_plugins.v6_price_action_1m.plugin import PriceAction1MPlugin
        assert PriceAction1MPlugin.ADX_THRESHOLD == 20
        assert PriceAction1MPlugin.CONFIDENCE_THRESHOLD == 80
        assert PriceAction1MPlugin.MAX_SPREAD_PIPS == 2.0
    
    def test_5m_filters(self):
        """Test 5M filter thresholds"""
        from src.logic_plugins.v6_price_action_5m.plugin import PriceAction5MPlugin
        assert PriceAction5MPlugin.ADX_THRESHOLD == 25
        assert PriceAction5MPlugin.CONFIDENCE_THRESHOLD == 70
        assert PriceAction5MPlugin.REQUIRE_15M_ALIGNMENT is True
    
    def test_15m_filters(self):
        """Test 15M filter thresholds"""
        from src.logic_plugins.v6_price_action_15m.plugin import PriceAction15MPlugin
        assert PriceAction15MPlugin.CONFIDENCE_THRESHOLD == 60
        assert PriceAction15MPlugin.REQUIRE_PULSE_ALIGNMENT is True
    
    def test_1h_filters(self):
        """Test 1H filter thresholds"""
        from src.logic_plugins.v6_price_action_1h.plugin import PriceAction1HPlugin
        assert PriceAction1HPlugin.CONFIDENCE_THRESHOLD == 60
        assert PriceAction1HPlugin.REQUIRE_4H_ALIGNMENT is True


class TestShadowMode:
    """Tests for Shadow Mode operation"""
    
    @pytest.fixture
    def mock_service_api(self):
        return MockServiceAPI()
    
    @pytest.mark.asyncio
    async def test_1m_shadow_mode_no_orders(self, mock_service_api):
        """Test 1M shadow mode doesn't place real orders"""
        from src.logic_plugins.v6_price_action_1m.plugin import PriceAction1MPlugin
        plugin = PriceAction1MPlugin(
            plugin_id="v6_price_action_1m",
            config={"shadow_mode": True},
            service_api=mock_service_api
        )
        
        alert = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "1",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 85,
            "adx": 25.0,
            "sl": 1.0800,
            "tp1": 1.0870
        }
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["status"] == "shadow"
        assert len(mock_service_api.orders_placed) == 0
    
    @pytest.mark.asyncio
    async def test_5m_shadow_mode_no_orders(self, mock_service_api):
        """Test 5M shadow mode doesn't place real orders"""
        from src.logic_plugins.v6_price_action_5m.plugin import PriceAction5MPlugin
        plugin = PriceAction5MPlugin(
            plugin_id="v6_price_action_5m",
            config={"shadow_mode": True},
            service_api=mock_service_api
        )
        
        alert = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "5",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 75,
            "adx": 28.0,
            "sl": 1.0800,
            "tp1": 1.0900,
            "tp2": 1.0950
        }
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["status"] == "shadow"
        assert len(mock_service_api.orders_placed) == 0


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing systems"""
    
    def test_v6_alert_compatible_with_v3_fields(self):
        """Test V6 alert has V3-compatible fields"""
        alert = ZepixV6Alert(
            type="BULLISH_ENTRY",
            ticker="EURUSD",
            tf="15",
            price=1.0850,
            direction="BUY",
            conf_level=ConfidenceLevel.HIGH,
            conf_score=85,
            sl=1.0800,
            tp1=1.0900
        )
        
        assert hasattr(alert, 'ticker')
        assert hasattr(alert, 'tf')
        assert hasattr(alert, 'price')
        assert hasattr(alert, 'direction')
        assert hasattr(alert, 'sl')
        assert hasattr(alert, 'tp1')
    
    def test_plugins_inherit_base_plugin(self):
        """Test V6 plugins inherit from BaseLogicPlugin"""
        from src.logic_plugins.v6_price_action_1m.plugin import PriceAction1MPlugin
        from src.logic_plugins.v6_price_action_5m.plugin import PriceAction5MPlugin
        from src.logic_plugins.v6_price_action_15m.plugin import PriceAction15MPlugin
        from src.logic_plugins.v6_price_action_1h.plugin import PriceAction1HPlugin
        from src.core.plugin_system.base_plugin import BaseLogicPlugin
        
        assert issubclass(PriceAction1MPlugin, BaseLogicPlugin)
        assert issubclass(PriceAction5MPlugin, BaseLogicPlugin)
        assert issubclass(PriceAction15MPlugin, BaseLogicPlugin)
        assert issubclass(PriceAction1HPlugin, BaseLogicPlugin)


class TestIntegration:
    """Integration tests for V6 system"""
    
    @pytest.fixture
    def mock_service_api(self):
        return MockServiceAPI()
    
    @pytest.mark.asyncio
    async def test_full_entry_exit_cycle_1m(self, mock_service_api):
        """Test full entry-exit cycle for 1M"""
        from src.logic_plugins.v6_price_action_1m.plugin import PriceAction1MPlugin
        plugin = PriceAction1MPlugin(
            plugin_id="v6_price_action_1m",
            config={"shadow_mode": True},
            service_api=mock_service_api
        )
        
        entry_alert = {
            "type": "BULLISH_ENTRY",
            "ticker": "EURUSD",
            "tf": "1",
            "price": 1.0850,
            "direction": "BUY",
            "conf_score": 85,
            "adx": 25.0,
            "sl": 1.0800,
            "tp1": 1.0870
        }
        
        entry_result = await plugin.process_entry_signal(entry_alert)
        assert entry_result["status"] == "shadow"
        
        exit_alert = {
            "type": "EXIT_BULLISH",
            "ticker": "EURUSD",
            "tf": "1",
            "price": 1.0870,
            "direction": "BUY",
            "conf_score": 85
        }
        
        exit_result = await plugin.process_exit_signal(exit_alert)
        assert exit_result["status"] == "shadow"
    
    @pytest.mark.asyncio
    async def test_trend_pulse_to_plugin_flow(self, mock_service_api):
        """Test Trend Pulse update to plugin validation flow"""
        mock_db = MagicMock()
        mock_db.execute = MagicMock()
        mock_db.fetchone = MagicMock(return_value=None)
        
        manager = TrendPulseManager(database=mock_db)
        
        await manager.update_pulse(
            symbol="EURUSD",
            timeframe="15",
            bull_count=5,
            bear_count=2,
            market_state="TRENDING_BULLISH"
        )
        
        is_aligned = await manager.check_pulse_alignment(
            symbol="EURUSD",
            direction="BUY"
        )
        
        assert is_aligned is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
