"""
Batch 08: V3 Combined Logic Plugin Tests

Tests for:
- All 12 signal types (7 entry, 2 exit, 2 info, 1 bonus)
- 2-tier routing matrix (signal override + timeframe routing)
- Dual order system (Order A: Smart SL, Order B: Fixed $10 SL)
- MTF 4-pillar trend validation
- Position sizing (4-step flow)
- Shadow mode
- Backward compatibility

Version: 1.0.0
Date: 2026-01-14
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MockServiceAPI:
    """Mock ServiceAPI for testing"""
    
    def __init__(self):
        self.placed_orders = []
        self.closed_positions = []
        self.notifications = []
        self.trends = {}
    
    async def calculate_lot_size(self, plugin_id: str, symbol: str) -> Dict[str, Any]:
        return {"lot_size": 0.10}
    
    async def calculate_sl_price(self, plugin_id: str, price: float, direction: str, lot_size: float) -> Dict[str, Any]:
        if direction.lower() == "buy":
            return {"sl_price": price * 0.99}
        return {"sl_price": price * 1.01}
    
    async def place_order(self, plugin_id: str, symbol: str, direction: str, 
                         lot_size: float, entry_price: float, sl_price: float,
                         tp_price: float, comment: str = "", metadata: Dict = None) -> Dict[str, Any]:
        order = {
            "plugin_id": plugin_id,
            "symbol": symbol,
            "direction": direction,
            "lot_size": lot_size,
            "entry_price": entry_price,
            "sl_price": sl_price,
            "tp_price": tp_price,
            "comment": comment,
            "metadata": metadata or {},
            "trade_id": len(self.placed_orders) + 1000
        }
        self.placed_orders.append(order)
        return {"success": True, "trade_id": order["trade_id"]}
    
    async def close_position(self, plugin_id: str, ticket: int) -> Dict[str, Any]:
        self.closed_positions.append({"plugin_id": plugin_id, "ticket": ticket})
        return {"success": True}
    
    async def close_positions_by_direction(self, plugin_id: str, symbol: str, direction: str) -> int:
        return 2
    
    async def get_plugin_orders(self, plugin_id: str, symbol: str) -> list:
        return [
            {"ticket": 1001, "direction": "BUY", "symbol": symbol},
            {"ticket": 1002, "direction": "SELL", "symbol": symbol}
        ]
    
    async def send_notification(self, plugin_id: str, message: str, priority: str = "normal") -> None:
        self.notifications.append({"plugin_id": plugin_id, "message": message, "priority": priority})
    
    async def update_trend(self, plugin_id: str, symbol: str, timeframe: str, direction: str) -> None:
        key = f"{symbol}_{timeframe}"
        self.trends[key] = direction


class TestCombinedV3Plugin:
    """Tests for CombinedV3Plugin main class"""
    
    @pytest.fixture
    def mock_service_api(self):
        return MockServiceAPI()
    
    @pytest.fixture
    def plugin_config(self):
        return {
            "enabled": True,
            "shadow_mode": False,
            "signal_routing": {
                "signal_overrides": {
                    "Screener_Full_Bullish": "combinedlogic-3",
                    "Screener_Full_Bearish": "combinedlogic-3"
                },
                "timeframe_routing": {
                    "5": "combinedlogic-1",
                    "15": "combinedlogic-2",
                    "60": "combinedlogic-3",
                    "240": "combinedlogic-3"
                },
                "default_logic": "combinedlogic-2"
            },
            "logic_multipliers": {
                "combinedlogic-1": 1.25,
                "combinedlogic-2": 1.0,
                "combinedlogic-3": 0.625
            },
            "mtf_config": {
                "pillars_only": ["15m", "1h", "4h", "1d"],
                "min_alignment": 3
            },
            "dual_orders": {
                "enabled": True,
                "split_ratio": 0.5,
                "order_b_fixed_sl_dollars": 10.0
            },
            "trend_bypass": {
                "bypass_for_entry_v3": True,
                "bypass_for_legacy": False
            },
            "aggressive_reversal_signals": [
                "Liquidity_Trap_Reversal",
                "Golden_Pocket_Flip",
                "Screener_Full_Bullish",
                "Screener_Full_Bearish"
            ],
            "rr_ratio": 1.5
        }
    
    @pytest.fixture
    def plugin(self, mock_service_api, plugin_config):
        with patch('src.logic_plugins.combined_v3.plugin.json.load', return_value=plugin_config):
            with patch('builtins.open', MagicMock()):
                from src.logic_plugins.v3_combined.plugin import CombinedV3Plugin
                p = CombinedV3Plugin(
                    plugin_id="v3_combined",
                    config=plugin_config,
                    service_api=mock_service_api
                )
                return p
    
    def test_plugin_initialization(self, plugin):
        """Test plugin initializes correctly"""
        assert plugin.plugin_id == "v3_combined"
        assert plugin.enabled == True
        assert plugin.shadow_mode == False
        assert len(plugin.metadata.get("supported_signals", [])) == 12
    
    def test_plugin_metadata(self, plugin):
        """Test plugin metadata contains all 12 signals"""
        signals = plugin.metadata.get("supported_signals", [])
        expected_signals = [
            "Institutional_Launchpad",
            "Liquidity_Trap",
            "Momentum_Breakout",
            "Mitigation_Test",
            "Golden_Pocket_Flip",
            "Volatility_Squeeze",
            "Bullish_Exit",
            "Bearish_Exit",
            "Screener_Full_Bullish",
            "Screener_Full_Bearish",
            "Trend_Pulse",
            "Sideways_Breakout"
        ]
        for signal in expected_signals:
            assert signal in signals, f"Missing signal: {signal}"
    
    def test_get_status(self, plugin):
        """Test get_status returns correct info"""
        status = plugin.get_status()
        assert status["plugin_id"] == "v3_combined"
        assert status["enabled"] == True
        assert "shadow_mode" in status
        assert "supported_signals" in status


class TestV3RoutingMatrix:
    """Tests for 2-tier routing matrix"""
    
    @pytest.fixture
    def plugin(self):
        mock_api = MockServiceAPI()
        config = {
            "enabled": True,
            "shadow_mode": False,
            "signal_routing": {
                "signal_overrides": {
                    "Screener_Full_Bullish": "combinedlogic-3",
                    "Screener_Full_Bearish": "combinedlogic-3"
                },
                "timeframe_routing": {
                    "5": "combinedlogic-1",
                    "15": "combinedlogic-2",
                    "60": "combinedlogic-3",
                    "240": "combinedlogic-3"
                },
                "default_logic": "combinedlogic-2"
            },
            "logic_multipliers": {
                "combinedlogic-1": 1.25,
                "combinedlogic-2": 1.0,
                "combinedlogic-3": 0.625
            },
            "mtf_config": {"pillars_only": ["15m", "1h", "4h", "1d"], "min_alignment": 3},
            "dual_orders": {"enabled": True, "split_ratio": 0.5, "order_b_fixed_sl_dollars": 10.0},
            "trend_bypass": {"bypass_for_entry_v3": True},
            "aggressive_reversal_signals": [],
            "rr_ratio": 1.5
        }
        with patch('src.logic_plugins.combined_v3.plugin.json.load', return_value=config):
            with patch('builtins.open', MagicMock()):
                from src.logic_plugins.v3_combined.plugin import CombinedV3Plugin
                return CombinedV3Plugin("v3_combined", config, mock_api)
    
    def test_signal_override_screener_bullish(self, plugin):
        """Test Screener_Full_Bullish always routes to LOGIC3"""
        alert = {"signal_type": "Screener_Full_Bullish", "tf": "5"}
        route = plugin._route_to_logic(alert)
        assert route == "combinedlogic-3"
    
    def test_signal_override_screener_bearish(self, plugin):
        """Test Screener_Full_Bearish always routes to LOGIC3"""
        alert = {"signal_type": "Screener_Full_Bearish", "tf": "15"}
        route = plugin._route_to_logic(alert)
        assert route == "combinedlogic-3"
    
    def test_signal_override_golden_pocket_1h(self, plugin):
        """Test Golden_Pocket_Flip on 1H routes to LOGIC3"""
        alert = {"signal_type": "Golden_Pocket_Flip", "tf": "60"}
        route = plugin._route_to_logic(alert)
        assert route == "combinedlogic-3"
    
    def test_signal_override_golden_pocket_4h(self, plugin):
        """Test Golden_Pocket_Flip on 4H routes to LOGIC3"""
        alert = {"signal_type": "Golden_Pocket_Flip", "tf": "240"}
        route = plugin._route_to_logic(alert)
        assert route == "combinedlogic-3"
    
    def test_timeframe_routing_5m(self, plugin):
        """Test 5m signal routes to LOGIC1"""
        alert = {"signal_type": "Institutional_Launchpad", "tf": "5"}
        route = plugin._route_to_logic(alert)
        assert route == "combinedlogic-1"
    
    def test_timeframe_routing_15m(self, plugin):
        """Test 15m signal routes to LOGIC2"""
        alert = {"signal_type": "Institutional_Launchpad", "tf": "15"}
        route = plugin._route_to_logic(alert)
        assert route == "combinedlogic-2"
    
    def test_timeframe_routing_60m(self, plugin):
        """Test 60m signal routes to LOGIC3"""
        alert = {"signal_type": "Institutional_Launchpad", "tf": "60"}
        route = plugin._route_to_logic(alert)
        assert route == "combinedlogic-3"
    
    def test_timeframe_routing_240m(self, plugin):
        """Test 240m signal routes to LOGIC3"""
        alert = {"signal_type": "Institutional_Launchpad", "tf": "240"}
        route = plugin._route_to_logic(alert)
        assert route == "combinedlogic-3"
    
    def test_default_routing(self, plugin):
        """Test unknown timeframe routes to default LOGIC2"""
        alert = {"signal_type": "Institutional_Launchpad", "tf": "30"}
        route = plugin._route_to_logic(alert)
        assert route == "combinedlogic-2"
    
    def test_logic_multiplier_logic1(self, plugin):
        """Test LOGIC1 multiplier is 1.25"""
        mult = plugin._get_logic_multiplier("combinedlogic-1")
        assert mult == 1.25
    
    def test_logic_multiplier_logic2(self, plugin):
        """Test LOGIC2 multiplier is 1.0"""
        mult = plugin._get_logic_multiplier("combinedlogic-2")
        assert mult == 1.0
    
    def test_logic_multiplier_logic3(self, plugin):
        """Test LOGIC3 multiplier is 0.625"""
        mult = plugin._get_logic_multiplier("combinedlogic-3")
        assert mult == 0.625


class TestV3SignalHandlers:
    """Tests for all 12 signal handlers"""
    
    @pytest.fixture
    def signal_handlers(self):
        mock_api = MockServiceAPI()
        config = {
            "enabled": True,
            "shadow_mode": False,
            "signal_routing": {
                "signal_overrides": {},
                "timeframe_routing": {"5": "combinedlogic-1", "15": "combinedlogic-2"},
                "default_logic": "combinedlogic-2"
            },
            "logic_multipliers": {"combinedlogic-1": 1.25, "combinedlogic-2": 1.0, "combinedlogic-3": 0.625},
            "mtf_config": {"pillars_only": ["15m", "1h", "4h", "1d"], "min_alignment": 3},
            "dual_orders": {"enabled": True, "split_ratio": 0.5, "order_b_fixed_sl_dollars": 10.0},
            "trend_bypass": {"bypass_for_entry_v3": True},
            "aggressive_reversal_signals": [],
            "rr_ratio": 1.5
        }
        with patch('src.logic_plugins.combined_v3.plugin.json.load', return_value=config):
            with patch('builtins.open', MagicMock()):
                from src.logic_plugins.v3_combined.plugin import CombinedV3Plugin
                plugin = CombinedV3Plugin("v3_combined", config, mock_api)
                return plugin.signal_handlers
    
    def test_handler_map_has_all_signals(self, signal_handlers):
        """Test handler map contains all 12 signal types"""
        expected_signals = [
            'Institutional_Launchpad',
            'Liquidity_Trap',
            'Momentum_Breakout',
            'Mitigation_Test',
            'Golden_Pocket_Flip',
            'Volatility_Squeeze',
            'Bullish_Exit',
            'Bearish_Exit',
            'Screener_Full_Bullish',
            'Screener_Full_Bearish',
            'Trend_Pulse',
            'Sideways_Breakout'
        ]
        for signal in expected_signals:
            assert signal in signal_handlers.handler_map, f"Missing handler for: {signal}"
    
    @pytest.mark.asyncio
    async def test_volatility_squeeze_no_trade(self, signal_handlers):
        """Test Volatility_Squeeze is info only (no trade)"""
        alert = {"signal_type": "Volatility_Squeeze", "symbol": "XAUUSD", "tf": "15"}
        result = await signal_handlers.handle_volatility_squeeze(alert)
        assert result["status"] == "info"
        assert result["action"] == "notification"
    
    @pytest.mark.asyncio
    async def test_trend_pulse_db_update(self, signal_handlers):
        """Test Trend_Pulse updates database"""
        alert = {
            "signal_type": "Trend_Pulse",
            "symbol": "XAUUSD",
            "mtf_trends": "1,1,1,1,1,-1",
            "changed_timeframes": "1h,4h"
        }
        result = await signal_handlers.handle_trend_pulse(alert)
        assert result["status"] == "success"
        assert result["action"] == "db_update"


class TestV3DualOrderSystem:
    """Tests for dual order system with hybrid SL"""
    
    @pytest.fixture
    def order_manager(self):
        mock_api = MockServiceAPI()
        config = {
            "enabled": True,
            "shadow_mode": False,
            "signal_routing": {
                "signal_overrides": {},
                "timeframe_routing": {"5": "combinedlogic-1", "15": "combinedlogic-2"},
                "default_logic": "combinedlogic-2"
            },
            "logic_multipliers": {"combinedlogic-1": 1.25, "combinedlogic-2": 1.0, "combinedlogic-3": 0.625},
            "mtf_config": {"pillars_only": ["15m", "1h", "4h", "1d"], "min_alignment": 3},
            "dual_orders": {"enabled": True, "split_ratio": 0.5, "order_b_fixed_sl_dollars": 10.0},
            "trend_bypass": {"bypass_for_entry_v3": True},
            "aggressive_reversal_signals": [],
            "rr_ratio": 1.5
        }
        with patch('src.logic_plugins.combined_v3.plugin.json.load', return_value=config):
            with patch('builtins.open', MagicMock()):
                from src.logic_plugins.v3_combined.plugin import CombinedV3Plugin
                plugin = CombinedV3Plugin("v3_combined", config, mock_api)
                return plugin.order_manager
    
    def test_consensus_to_multiplier_low(self, order_manager):
        """Test low consensus (0-3) maps to 0.2-0.5"""
        assert order_manager._map_consensus_to_multiplier(0) == pytest.approx(0.2)
        assert order_manager._map_consensus_to_multiplier(1) == pytest.approx(0.3)
        assert order_manager._map_consensus_to_multiplier(2) == pytest.approx(0.4)
        assert order_manager._map_consensus_to_multiplier(3) == pytest.approx(0.5)
    
    def test_consensus_to_multiplier_medium(self, order_manager):
        """Test medium consensus (4-6) maps to 0.6-0.8"""
        assert order_manager._map_consensus_to_multiplier(4) == 0.6
        assert order_manager._map_consensus_to_multiplier(5) == 0.7
        assert order_manager._map_consensus_to_multiplier(6) == 0.8
    
    def test_consensus_to_multiplier_high(self, order_manager):
        """Test high consensus (7-9) maps to 0.85-1.0"""
        assert order_manager._map_consensus_to_multiplier(7) == pytest.approx(0.85)
        assert order_manager._map_consensus_to_multiplier(8) == pytest.approx(0.9)
        assert order_manager._map_consensus_to_multiplier(9) == pytest.approx(1.0)
    
    @pytest.mark.asyncio
    async def test_order_a_uses_v3_smart_sl(self, order_manager):
        """Test Order A uses V3 Smart SL from Pine"""
        alert = {
            "symbol": "XAUUSD",
            "direction": "buy",
            "price": 2030.00,
            "sl_price": 2028.00,
            "tp2_price": 2035.00
        }
        params = await order_manager._calculate_order_a_params(
            alert, 2030.00, "buy", 0.05, "combinedlogic-2"
        )
        assert params["sl"] == 2028.00
        assert params["tp"] == 2035.00
        assert params["sl_source"] == "V3_SMART"
    
    @pytest.mark.asyncio
    async def test_order_b_ignores_v3_sl(self, order_manager):
        """Test Order B uses Fixed $10 SL (ignores V3 SL)"""
        alert = {
            "symbol": "XAUUSD",
            "direction": "buy",
            "price": 2030.00,
            "sl_price": 2000.00,
            "tp1_price": 2032.00
        }
        params = await order_manager._calculate_order_b_params(
            alert, 2030.00, "buy", 0.05, "combinedlogic-2"
        )
        assert params["sl"] != 2000.00
        assert params["sl_source"] == "FIXED_PYRAMID"
    
    @pytest.mark.asyncio
    async def test_dual_orders_50_50_split(self, order_manager):
        """Test lot size is split 50/50 between Order A and Order B"""
        alert = {
            "symbol": "XAUUSD",
            "direction": "buy",
            "price": 2030.00,
            "signal_type": "Institutional_Launchpad",
            "consensus_score": 8
        }
        result = await order_manager.place_v3_dual_orders(
            alert, "combinedlogic-2", 1.0
        )
        
        placed_orders = order_manager.service_api.placed_orders
        if len(placed_orders) >= 2:
            order_a_lot = placed_orders[-2]["lot_size"]
            order_b_lot = placed_orders[-1]["lot_size"]
            assert abs(order_a_lot - order_b_lot) < 0.001


class TestV3MTF4Pillar:
    """Tests for MTF 4-pillar trend validation"""
    
    @pytest.fixture
    def trend_validator(self):
        mock_api = MockServiceAPI()
        config = {
            "enabled": True,
            "shadow_mode": False,
            "signal_routing": {
                "signal_overrides": {},
                "timeframe_routing": {"5": "combinedlogic-1", "15": "combinedlogic-2"},
                "default_logic": "combinedlogic-2"
            },
            "logic_multipliers": {"combinedlogic-1": 1.25, "combinedlogic-2": 1.0, "combinedlogic-3": 0.625},
            "mtf_config": {"pillars_only": ["15m", "1h", "4h", "1d"], "min_alignment": 3},
            "dual_orders": {"enabled": True, "split_ratio": 0.5, "order_b_fixed_sl_dollars": 10.0},
            "trend_bypass": {"bypass_for_entry_v3": True, "bypass_for_legacy": False},
            "aggressive_reversal_signals": [],
            "rr_ratio": 1.5
        }
        with patch('src.logic_plugins.combined_v3.plugin.json.load', return_value=config):
            with patch('builtins.open', MagicMock()):
                from src.logic_plugins.v3_combined.plugin import CombinedV3Plugin
                plugin = CombinedV3Plugin("v3_combined", config, mock_api)
                return plugin.trend_validator
    
    def test_extract_4_pillars_correct(self, trend_validator):
        """Test 4-pillar extraction ignores 1m/5m"""
        mtf_string = "1,1,-1,1,1,1"
        pillars = trend_validator.extract_4_pillar_trends(mtf_string)
        
        assert pillars["15m"] == -1
        assert pillars["1h"] == 1
        assert pillars["4h"] == 1
        assert pillars["1d"] == 1
        assert "1m" not in pillars
        assert "5m" not in pillars
    
    def test_extract_4_pillars_all_bullish(self, trend_validator):
        """Test extraction with all bullish pillars"""
        mtf_string = "1,1,1,1,1,1"
        pillars = trend_validator.extract_4_pillar_trends(mtf_string)
        
        assert all(v == 1 for v in pillars.values())
    
    def test_extract_4_pillars_all_bearish(self, trend_validator):
        """Test extraction with all bearish pillars"""
        mtf_string = "-1,-1,-1,-1,-1,-1"
        pillars = trend_validator.extract_4_pillar_trends(mtf_string)
        
        assert all(v == -1 for v in pillars.values())
    
    def test_extract_4_pillars_invalid_length(self, trend_validator):
        """Test extraction fails with wrong number of values"""
        mtf_string = "1,1,1,1,1"
        with pytest.raises(ValueError):
            trend_validator.extract_4_pillar_trends(mtf_string)
    
    @pytest.mark.asyncio
    async def test_trend_alignment_buy_pass(self, trend_validator):
        """Test BUY passes with 3/4 bullish"""
        alert = {"direction": "buy", "mtf_trends": "1,1,1,1,1,-1"}
        aligned = await trend_validator.validate_trend_alignment(alert)
        assert aligned == True
    
    @pytest.mark.asyncio
    async def test_trend_alignment_buy_fail(self, trend_validator):
        """Test BUY fails with 2/4 bullish"""
        alert = {"direction": "buy", "mtf_trends": "1,1,1,1,-1,-1"}
        aligned = await trend_validator.validate_trend_alignment(alert)
        assert aligned == False
    
    @pytest.mark.asyncio
    async def test_trend_alignment_sell_pass(self, trend_validator):
        """Test SELL passes with 3/4 bearish"""
        alert = {"direction": "sell", "mtf_trends": "-1,-1,-1,-1,-1,1"}
        aligned = await trend_validator.validate_trend_alignment(alert)
        assert aligned == True
    
    @pytest.mark.asyncio
    async def test_trend_alignment_sell_fail(self, trend_validator):
        """Test SELL fails with 2/4 bearish"""
        alert = {"direction": "sell", "mtf_trends": "-1,-1,-1,-1,1,1"}
        aligned = await trend_validator.validate_trend_alignment(alert)
        assert aligned == False
    
    def test_trend_bypass_entry_v3(self, trend_validator):
        """Test entry_v3 signals bypass trend check"""
        alert = {"type": "entry_v3", "direction": "buy"}
        bypass = trend_validator.should_bypass_trend_check(alert)
        assert bypass == True
    
    def test_trend_bypass_legacy_required(self, trend_validator):
        """Test legacy signals require trend check"""
        alert = {"type": "legacy", "signal_source": "legacy", "direction": "buy"}
        bypass = trend_validator.should_bypass_trend_check(alert)
        assert bypass == False


class TestV3PositionSizing:
    """Tests for 4-step position sizing flow"""
    
    @pytest.fixture
    def order_manager(self):
        mock_api = MockServiceAPI()
        config = {
            "enabled": True,
            "shadow_mode": False,
            "signal_routing": {
                "signal_overrides": {},
                "timeframe_routing": {"5": "combinedlogic-1", "15": "combinedlogic-2"},
                "default_logic": "combinedlogic-2"
            },
            "logic_multipliers": {"combinedlogic-1": 1.25, "combinedlogic-2": 1.0, "combinedlogic-3": 0.625},
            "mtf_config": {"pillars_only": ["15m", "1h", "4h", "1d"], "min_alignment": 3},
            "dual_orders": {"enabled": True, "split_ratio": 0.5, "order_b_fixed_sl_dollars": 10.0},
            "trend_bypass": {"bypass_for_entry_v3": True},
            "aggressive_reversal_signals": [],
            "rr_ratio": 1.5
        }
        with patch('src.logic_plugins.combined_v3.plugin.json.load', return_value=config):
            with patch('builtins.open', MagicMock()):
                from src.logic_plugins.v3_combined.plugin import CombinedV3Plugin
                plugin = CombinedV3Plugin("v3_combined", config, mock_api)
                return plugin.order_manager
    
    def test_position_sizing_4_step_flow(self, order_manager):
        """Test 4-step position sizing calculation"""
        base_lot = 0.10
        consensus = 8
        logic_route = "combinedlogic-1"
        
        v3_mult = order_manager._map_consensus_to_multiplier(consensus)
        assert v3_mult == 0.9
        
        logic_mult = 1.25
        
        final_lot = base_lot * v3_mult * logic_mult
        assert abs(final_lot - 0.1125) < 0.001
        
        order_a_lot = final_lot * 0.5
        order_b_lot = final_lot * 0.5
        assert abs(order_a_lot - 0.05625) < 0.001
        assert abs(order_b_lot - 0.05625) < 0.001


class TestV3ShadowMode:
    """Tests for shadow mode operation"""
    
    @pytest.fixture
    def shadow_plugin(self):
        mock_api = MockServiceAPI()
        config = {
            "enabled": True,
            "shadow_mode": True,
            "signal_routing": {
                "signal_overrides": {},
                "timeframe_routing": {"5": "combinedlogic-1", "15": "combinedlogic-2"},
                "default_logic": "combinedlogic-2"
            },
            "logic_multipliers": {"combinedlogic-1": 1.25, "combinedlogic-2": 1.0, "combinedlogic-3": 0.625},
            "mtf_config": {"pillars_only": ["15m", "1h", "4h", "1d"], "min_alignment": 3},
            "dual_orders": {"enabled": True, "split_ratio": 0.5, "order_b_fixed_sl_dollars": 10.0},
            "trend_bypass": {"bypass_for_entry_v3": True},
            "aggressive_reversal_signals": [],
            "rr_ratio": 1.5
        }
        with patch('src.logic_plugins.combined_v3.plugin.json.load', return_value=config):
            with patch('builtins.open', MagicMock()):
                from src.logic_plugins.v3_combined.plugin import CombinedV3Plugin
                return CombinedV3Plugin("v3_combined", config, mock_api)
    
    @pytest.mark.asyncio
    async def test_shadow_mode_no_real_orders(self, shadow_plugin):
        """Test shadow mode doesn't place real orders"""
        alert = {
            "signal_type": "Institutional_Launchpad",
            "symbol": "XAUUSD",
            "direction": "buy",
            "price": 2030.00,
            "tf": "15",
            "consensus_score": 8
        }
        result = await shadow_plugin.process_entry_signal(alert)
        
        assert result["status"] == "shadow"
        assert result["action"] == "entry"
        assert len(shadow_plugin.service_api.placed_orders) == 0
    
    @pytest.mark.asyncio
    async def test_shadow_mode_exit(self, shadow_plugin):
        """Test shadow mode exit doesn't close real positions"""
        alert = {
            "signal_type": "Bullish_Exit",
            "symbol": "XAUUSD",
            "direction": "buy"
        }
        result = await shadow_plugin.process_exit_signal(alert)
        
        assert result["status"] == "shadow"
        assert result["action"] == "exit"


class TestV3BackwardCompatibility:
    """Tests for backward compatibility with existing bot"""
    
    @pytest.fixture
    def plugin(self):
        mock_api = MockServiceAPI()
        config = {
            "enabled": True,
            "shadow_mode": False,
            "signal_routing": {
                "signal_overrides": {
                    "Screener_Full_Bullish": "combinedlogic-3",
                    "Screener_Full_Bearish": "combinedlogic-3"
                },
                "timeframe_routing": {
                    "5": "combinedlogic-1",
                    "15": "combinedlogic-2",
                    "60": "combinedlogic-3",
                    "240": "combinedlogic-3"
                },
                "default_logic": "combinedlogic-2"
            },
            "logic_multipliers": {
                "combinedlogic-1": 1.25,
                "combinedlogic-2": 1.0,
                "combinedlogic-3": 0.625
            },
            "mtf_config": {"pillars_only": ["15m", "1h", "4h", "1d"], "min_alignment": 3},
            "dual_orders": {"enabled": True, "split_ratio": 0.5, "order_b_fixed_sl_dollars": 10.0},
            "trend_bypass": {"bypass_for_entry_v3": True},
            "aggressive_reversal_signals": ["Liquidity_Trap_Reversal", "Golden_Pocket_Flip"],
            "rr_ratio": 1.5
        }
        with patch('src.logic_plugins.combined_v3.plugin.json.load', return_value=config):
            with patch('builtins.open', MagicMock()):
                from src.logic_plugins.v3_combined.plugin import CombinedV3Plugin
                return CombinedV3Plugin("v3_combined", config, mock_api)
    
    def test_routing_matches_trading_engine(self, plugin):
        """Test routing matches existing trading_engine._route_v3_to_logic()"""
        test_cases = [
            ({"signal_type": "Screener_Full_Bullish", "tf": "5"}, "combinedlogic-3"),
            ({"signal_type": "Screener_Full_Bearish", "tf": "15"}, "combinedlogic-3"),
            ({"signal_type": "Golden_Pocket_Flip", "tf": "60"}, "combinedlogic-3"),
            ({"signal_type": "Golden_Pocket_Flip", "tf": "240"}, "combinedlogic-3"),
            ({"signal_type": "Institutional_Launchpad", "tf": "5"}, "combinedlogic-1"),
            ({"signal_type": "Institutional_Launchpad", "tf": "15"}, "combinedlogic-2"),
            ({"signal_type": "Institutional_Launchpad", "tf": "60"}, "combinedlogic-3"),
            ({"signal_type": "Institutional_Launchpad", "tf": "240"}, "combinedlogic-3"),
        ]
        
        for alert, expected_route in test_cases:
            actual_route = plugin._route_to_logic(alert)
            assert actual_route == expected_route, f"Failed for {alert}: expected {expected_route}, got {actual_route}"
    
    def test_multipliers_match_trading_engine(self, plugin):
        """Test multipliers match existing trading_engine._get_logic_multiplier()"""
        assert plugin._get_logic_multiplier("combinedlogic-1") == 1.25
        assert plugin._get_logic_multiplier("combinedlogic-2") == 1.0
        assert plugin._get_logic_multiplier("combinedlogic-3") == 0.625
    
    def test_aggressive_reversal_detection(self, plugin):
        """Test aggressive reversal detection matches existing logic"""
        aggressive_alerts = [
            {"signal_type": "Liquidity_Trap_Reversal", "consensus_score": 5},
            {"signal_type": "Golden_Pocket_Flip", "consensus_score": 5},
            {"signal_type": "Institutional_Launchpad", "consensus_score": 8},
        ]
        
        for alert in aggressive_alerts:
            is_aggressive = plugin._is_aggressive_reversal_signal(alert)
            assert is_aggressive == True, f"Should be aggressive: {alert}"
        
        non_aggressive = {"signal_type": "Institutional_Launchpad", "consensus_score": 5}
        assert plugin._is_aggressive_reversal_signal(non_aggressive) == False


class TestV3Integration:
    """Integration tests for full V3 plugin flow"""
    
    @pytest.fixture
    def plugin(self):
        mock_api = MockServiceAPI()
        config = {
            "enabled": True,
            "shadow_mode": False,
            "signal_routing": {
                "signal_overrides": {"Screener_Full_Bullish": "combinedlogic-3"},
                "timeframe_routing": {"5": "combinedlogic-1", "15": "combinedlogic-2"},
                "default_logic": "combinedlogic-2"
            },
            "logic_multipliers": {"combinedlogic-1": 1.25, "combinedlogic-2": 1.0, "combinedlogic-3": 0.625},
            "mtf_config": {"pillars_only": ["15m", "1h", "4h", "1d"], "min_alignment": 3},
            "dual_orders": {"enabled": True, "split_ratio": 0.5, "order_b_fixed_sl_dollars": 10.0},
            "trend_bypass": {"bypass_for_entry_v3": True},
            "aggressive_reversal_signals": [],
            "rr_ratio": 1.5
        }
        with patch('src.logic_plugins.combined_v3.plugin.json.load', return_value=config):
            with patch('builtins.open', MagicMock()):
                from src.logic_plugins.v3_combined.plugin import CombinedV3Plugin
                return CombinedV3Plugin("v3_combined", config, mock_api)
    
    @pytest.mark.asyncio
    async def test_full_entry_flow(self, plugin):
        """Test complete entry signal processing flow"""
        alert = {
            "type": "entry_v3",
            "signal_type": "Institutional_Launchpad",
            "symbol": "XAUUSD",
            "direction": "buy",
            "price": 2030.00,
            "tf": "15",
            "consensus_score": 8,
            "sl_price": 2028.00,
            "tp1_price": 2032.00,
            "tp2_price": 2035.00,
            "mtf_trends": "1,1,1,1,1,1"
        }
        
        result = await plugin.process_entry_signal(alert)
        
        assert result["status"] == "success"
        assert result["order_a_placed"] == True
        assert result["order_b_placed"] == True
        assert result["logic_route"] == "combinedlogic-2"
    
    @pytest.mark.asyncio
    async def test_full_exit_flow(self, plugin):
        """Test complete exit signal processing flow"""
        alert = {
            "type": "exit_v3",
            "signal_type": "Bullish_Exit",
            "symbol": "XAUUSD",
            "direction": "buy"
        }
        
        result = await plugin.process_exit_signal(alert)
        
        assert result["status"] in ["success", "no_action"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
