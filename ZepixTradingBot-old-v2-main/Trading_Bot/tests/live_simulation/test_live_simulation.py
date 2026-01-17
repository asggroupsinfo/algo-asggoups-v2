"""
Live Simulation Test Suite - Mandate 23

Comprehensive tests for:
1. Entry → TP1 → TP2 → TP3 (Full Win)
2. Entry → SL Hit → 70% Recovery → Re-entry
3. Entry → TP1 → Weak Conditions → Exit
4. Exit Signal Intelligence
5. Telegram Bot Separation

ALL TESTS MUST PASS 100%

Version: 1.0.0
Date: 2026-01-17
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.services.intelligent_trade_manager import (
    IntelligentTradeManager,
    TradeContext,
    TradeState,
    OrderType,
    PineUpdate,
    SmartLotResult
)


class TestSmartLotSizing:
    """Test smart lot calculation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = IntelligentTradeManager(service_api=None, config={
            "risk_percent": 1.0,
            "max_lot_size": 0.15,
            "min_lot_size": 0.01
        })
    
    def test_smart_lot_basic_calculation(self):
        """Test basic smart lot calculation"""
        result = self.manager.calculate_smart_lot(
            entry_price=1.1000,
            sl_price=1.0950,
            symbol="EURUSD",
            account_balance=10000.0,
            risk_percent=1.0
        )
        
        assert isinstance(result, SmartLotResult)
        assert result.lot_size > 0
        assert result.risk_amount == 100.0  # 1% of 10000
        assert abs(result.sl_pips - 50.0) < 0.01  # 50 pips SL (with floating point tolerance)
    
    def test_smart_lot_max_cap(self):
        """Test lot size is capped at max"""
        result = self.manager.calculate_smart_lot(
            entry_price=1.1000,
            sl_price=1.0999,  # Very tight SL = large lot
            symbol="EURUSD",
            account_balance=100000.0,
            risk_percent=5.0
        )
        
        assert result.lot_size <= self.manager.max_lot_size
        assert result.capped == True
    
    def test_smart_lot_min_floor(self):
        """Test lot size is raised to min"""
        result = self.manager.calculate_smart_lot(
            entry_price=1.1000,
            sl_price=1.0000,  # Very wide SL = small lot
            symbol="EURUSD",
            account_balance=100.0,
            risk_percent=0.1
        )
        
        assert result.lot_size >= self.manager.min_lot_size
        assert result.capped == True
    
    def test_smart_lot_jpy_pair(self):
        """Test lot calculation for JPY pairs"""
        result = self.manager.calculate_smart_lot(
            entry_price=150.00,
            sl_price=149.50,
            symbol="USDJPY",
            account_balance=10000.0,
            risk_percent=1.0
        )
        
        assert isinstance(result, SmartLotResult)
        assert result.lot_size > 0


class TestIntelligentEntry:
    """Test intelligent entry with dual orders"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = IntelligentTradeManager(service_api=None, config={
            "risk_percent": 1.0,
            "max_lot_size": 0.15,
            "min_lot_size": 0.01
        })
    
    @pytest.mark.asyncio
    async def test_entry_creates_dual_orders(self):
        """Test entry creates Order A and Order B"""
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        
        result = await self.manager.process_entry_signal(alert, account_balance=10000.0)
        
        assert result["status"] == "success"
        assert result["order_a_id"] is not None
        assert result["order_b_id"] is not None
        assert result["order_a_lot"] > 0
        assert result["order_b_lot"] > 0
        assert result["order_b_lot"] == round(result["order_a_lot"] * 0.5, 2) or result["order_b_lot"] == 0.01
    
    @pytest.mark.asyncio
    async def test_entry_uses_pine_tp_sl(self):
        """Test entry uses TP/SL from Pine payload"""
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        
        result = await self.manager.process_entry_signal(alert)
        
        assert result["sl_price"] == 1.0950
        assert result["tp1_price"] == 1.1050
        assert result["tp2_price"] == 1.1100
        assert result["tp3_price"] == 1.1150
    
    @pytest.mark.asyncio
    async def test_entry_stores_trade_context(self):
        """Test entry stores trade context for monitoring"""
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        
        result = await self.manager.process_entry_signal(alert)
        trade_id = result["trade_id"]
        
        context = self.manager.get_trade_context(trade_id)
        
        assert context is not None
        assert context.symbol == "EURUSD"
        assert context.direction == "BUY"
        assert context.state == TradeState.ACTIVE
    
    @pytest.mark.asyncio
    async def test_entry_missing_data_returns_error(self):
        """Test entry with missing data returns error"""
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY"
            # Missing price, sl, tp1
        }
        
        result = await self.manager.process_entry_signal(alert)
        
        assert result["status"] == "error"


class TestTPManagement:
    """Test TP1/TP2/TP3 intelligent profit booking"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = IntelligentTradeManager(service_api=None)
    
    @pytest.mark.asyncio
    async def test_tp1_strong_conditions_hold(self):
        """Test TP1 hit with strong conditions holds for TP2"""
        # Create trade
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        # Strong Pine update
        pine_update = PineUpdate(
            trend="BULLISH",
            adx=30.0,
            confidence=80
        )
        
        # Price hits TP1
        result = await self.manager.monitor_tp_levels(
            trade_id=trade_id,
            current_price=1.1050,
            pine_update=pine_update
        )
        
        assert result["action"] == "hold"
        assert result["reason"] == "conditions_strong"
        assert result["target"] == "TP2"
    
    @pytest.mark.asyncio
    async def test_tp1_weak_conditions_partial_close(self):
        """Test TP1 hit with weak conditions closes 50%"""
        # Create trade
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        # Weak Pine update
        pine_update = PineUpdate(
            trend="BEARISH",  # Opposite direction
            adx=15.0,  # Low ADX
            confidence=50  # Low confidence
        )
        
        # Price hits TP1
        result = await self.manager.monitor_tp_levels(
            trade_id=trade_id,
            current_price=1.1050,
            pine_update=pine_update
        )
        
        assert result["action"] == "partial_close"
        assert result["percent"] == 50
        assert result["reason"] == "conditions_weak"
    
    @pytest.mark.asyncio
    async def test_tp2_partial_close_and_trail(self):
        """Test TP2 hit closes 40% and trails SL to TP1"""
        # Create trade
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        pine_update = PineUpdate(trend="BULLISH", adx=30.0, confidence=80)
        
        # Price hits TP2
        result = await self.manager.monitor_tp_levels(
            trade_id=trade_id,
            current_price=1.1100,
            pine_update=pine_update
        )
        
        assert result["action"] == "partial_close_and_trail"
        assert result["percent"] == 40
        assert result["new_sl"] == 1.1050  # TP1 level
    
    @pytest.mark.asyncio
    async def test_tp3_close_all(self):
        """Test TP3 hit closes all remaining"""
        # Create trade
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        pine_update = PineUpdate(trend="BULLISH", adx=30.0, confidence=80)
        
        # Price hits TP3
        result = await self.manager.monitor_tp_levels(
            trade_id=trade_id,
            current_price=1.1150,
            pine_update=pine_update
        )
        
        assert result["action"] == "close_all"
        assert result["reason"] == "tp3_hit"
        
        # Verify trade state
        context = self.manager.get_trade_context(trade_id)
        assert context.state == TradeState.TP3_HIT


class TestSLHuntingRecovery:
    """Test SL Hunting with 70% recovery re-entry"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = IntelligentTradeManager(service_api=None, config={
            "recovery_percent": 70
        })
    
    @pytest.mark.asyncio
    async def test_sl_hit_activates_hunting(self):
        """Test SL hit activates SL Hunting mode"""
        # Create trade
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        # SL hit
        result = await self.manager.handle_sl_hit(
            trade_id=trade_id,
            order_type=OrderType.ORDER_A,
            exit_price=1.0950
        )
        
        assert result["action"] == "sl_hunting_activated"
        assert result["hunt_id"] is not None
        assert result["recovery_price"] > 0
    
    def test_70_percent_recovery_calculation(self):
        """Test 70% recovery price calculation"""
        # For BUY: entry=1.1000, sl=1.0950
        # Distance = 50 pips, 70% = 35 pips
        # Recovery = 1.0950 + 0.0035 = 1.0985
        
        recovery = self.manager._calculate_recovery_price(
            entry=1.1000,
            sl=1.0950,
            direction="BUY"
        )
        
        expected = 1.0950 + (1.1000 - 1.0950) * 0.70
        assert abs(recovery - expected) < 0.0001
    
    def test_70_percent_recovery_calculation_sell(self):
        """Test 70% recovery for SELL direction"""
        # For SELL: entry=1.1000, sl=1.1050
        # Distance = 50 pips, 70% = 35 pips
        # Recovery = 1.1050 - 0.0035 = 1.1015
        
        recovery = self.manager._calculate_recovery_price(
            entry=1.1000,
            sl=1.1050,
            direction="SELL"
        )
        
        expected = 1.1050 - (1.1050 - 1.1000) * 0.70
        assert abs(recovery - expected) < 0.0001
    
    @pytest.mark.asyncio
    async def test_recovery_with_good_conditions_reentry(self):
        """Test 70% recovery + good conditions executes re-entry"""
        # Create trade and trigger SL hunt
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        # Trigger SL hunt
        sl_result = await self.manager.handle_sl_hit(
            trade_id=trade_id,
            order_type=OrderType.ORDER_A,
            exit_price=1.0950
        )
        hunt_id = sl_result["hunt_id"]
        recovery_price = sl_result["recovery_price"]
        
        # Good Pine conditions
        pine_update = PineUpdate(
            trend="BULLISH",
            adx=30.0,
            confidence=80
        )
        
        # Price recovers to 70% level
        result = await self.manager.check_sl_recovery(
            hunt_id=hunt_id,
            current_price=recovery_price + 0.0001,  # Just above recovery
            pine_update=pine_update
        )
        
        assert result["action"] == "reentry_executed"
        assert result["result"]["success"] == True
    
    @pytest.mark.asyncio
    async def test_recovery_with_weak_conditions_skip(self):
        """Test 70% recovery + weak conditions skips re-entry"""
        # Create trade and trigger SL hunt
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        # Trigger SL hunt
        sl_result = await self.manager.handle_sl_hit(
            trade_id=trade_id,
            order_type=OrderType.ORDER_A,
            exit_price=1.0950
        )
        hunt_id = sl_result["hunt_id"]
        recovery_price = sl_result["recovery_price"]
        
        # Weak Pine conditions
        pine_update = PineUpdate(
            trend="BEARISH",  # Opposite direction
            adx=15.0,  # Low ADX
            confidence=50  # Low confidence
        )
        
        # Price recovers to 70% level
        result = await self.manager.check_sl_recovery(
            hunt_id=hunt_id,
            current_price=recovery_price + 0.0001,
            pine_update=pine_update
        )
        
        assert result["action"] == "reentry_skipped"
        assert result["reason"] == "conditions_weak"


class TestExitSignalIntelligence:
    """Test exit signal intelligence"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = IntelligentTradeManager(service_api=None)
    
    @pytest.mark.asyncio
    async def test_exit_big_profit_strong_trend_hold(self):
        """Test exit signal with big profit + strong trend holds position"""
        # Create trade
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        # Strong Pine update
        pine_update = PineUpdate(
            trend="BULLISH",
            adx=30.0,
            confidence=80
        )
        
        # Big profit (60 pips)
        current_price = 1.1060
        
        result = await self.manager.process_exit_signal(
            trade_id=trade_id,
            current_price=current_price,
            pine_update=pine_update
        )
        
        assert result["action"] == "hold"
        assert result["reason"] == "strong_trend_big_profit"
        assert result["profit_pips"] > 50
    
    @pytest.mark.asyncio
    async def test_exit_small_profit_close_immediately(self):
        """Test exit signal with small profit closes immediately"""
        # Create trade
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        pine_update = PineUpdate(trend="NEUTRAL", adx=20.0, confidence=60)
        
        # Small profit (5 pips)
        current_price = 1.1005
        
        result = await self.manager.process_exit_signal(
            trade_id=trade_id,
            current_price=current_price,
            pine_update=pine_update
        )
        
        assert result["action"] == "close_all"
        assert result["reason"] == "small_profit"
        assert result["profit_pips"] < 10
    
    @pytest.mark.asyncio
    async def test_exit_moderate_profit_partial_close(self):
        """Test exit signal with moderate profit closes 50%"""
        # Create trade
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        pine_update = PineUpdate(trend="NEUTRAL", adx=20.0, confidence=60)
        
        # Moderate profit (25 pips)
        current_price = 1.1025
        
        result = await self.manager.process_exit_signal(
            trade_id=trade_id,
            current_price=current_price,
            pine_update=pine_update
        )
        
        assert result["action"] == "partial_close_and_protect"
        assert result["percent"] == 50
        assert result["reason"] == "moderate_profit"


class TestTelegramBotSeparation:
    """Test Telegram bot separation (3 bots)"""
    
    def _import_telegram_module(self, module_name):
        """Import telegram module using importlib to avoid conflicts with telegram package"""
        import importlib.util
        import os
        
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        module_path = os.path.join(base_path, 'src', 'telegram', f'{module_name}.py')
        
        if not os.path.exists(module_path):
            return None
        
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def test_multi_telegram_manager_exists(self):
        """Test MultiTelegramManager class exists"""
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        module_path = os.path.join(base_path, 'src', 'telegram', 'multi_telegram_manager.py')
        assert os.path.exists(module_path), f"MultiTelegramManager file not found at {module_path}"
    
    def test_controller_bot_exists(self):
        """Test ControllerBot class exists"""
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        module_path = os.path.join(base_path, 'src', 'telegram', 'controller_bot.py')
        assert os.path.exists(module_path), f"ControllerBot file not found at {module_path}"
    
    def test_notification_bot_exists(self):
        """Test NotificationBot class exists"""
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        module_path = os.path.join(base_path, 'src', 'telegram', 'notification_bot.py')
        assert os.path.exists(module_path), f"NotificationBot file not found at {module_path}"
    
    def test_analytics_bot_exists(self):
        """Test AnalyticsBot class exists"""
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        module_path = os.path.join(base_path, 'src', 'telegram', 'analytics_bot.py')
        assert os.path.exists(module_path), f"AnalyticsBot file not found at {module_path}"
    
    def test_telegram_3_bot_architecture(self):
        """Test that 3-bot architecture files exist and have correct structure"""
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        telegram_path = os.path.join(base_path, 'src', 'telegram')
        
        # Required files for 3-bot architecture
        required_files = [
            'multi_telegram_manager.py',
            'controller_bot.py',
            'notification_bot.py',
            'analytics_bot.py',
            'base_telegram_bot.py',
            'message_router.py'
        ]
        
        for filename in required_files:
            filepath = os.path.join(telegram_path, filename)
            assert os.path.exists(filepath), f"Required file {filename} not found"
        
        # Verify multi_telegram_manager has 3-bot imports
        with open(os.path.join(telegram_path, 'multi_telegram_manager.py'), 'r') as f:
            content = f.read()
            assert 'ControllerBot' in content, "MultiTelegramManager should import ControllerBot"
            assert 'NotificationBot' in content, "MultiTelegramManager should import NotificationBot"
            assert 'AnalyticsBot' in content, "MultiTelegramManager should import AnalyticsBot"
    
    def test_message_routing_logic(self):
        """Test message routing logic exists in multi_telegram_manager"""
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        filepath = os.path.join(base_path, 'src', 'telegram', 'multi_telegram_manager.py')
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Verify routing methods exist
        assert '_get_target_bot' in content, "Should have _get_target_bot method"
        assert 'route_message' in content, "Should have route_message method"
        assert 'send_alert' in content, "Should have send_alert method"
        assert 'send_report' in content, "Should have send_report method"


class TestFullTradeLifecycle:
    """Test complete trade lifecycle scenarios"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = IntelligentTradeManager(service_api=None)
    
    @pytest.mark.asyncio
    async def test_full_win_entry_to_tp3(self):
        """Test 1: Entry → TP1 → TP2 → TP3 (Full Win)"""
        # Step 1: Entry
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        assert entry_result["status"] == "success"
        assert entry_result["order_a_id"] is not None
        assert entry_result["order_b_id"] is not None
        
        # Strong conditions throughout
        pine_update = PineUpdate(trend="BULLISH", adx=30.0, confidence=80)
        
        # Step 2: TP1 hit - Order B closes, Order A holds
        tp1_result = await self.manager.monitor_tp_levels(
            trade_id=trade_id,
            current_price=1.1050,
            pine_update=pine_update
        )
        assert tp1_result["action"] == "hold"
        
        # Step 3: TP2 hit - Partial close 40%, trail SL
        tp2_result = await self.manager.monitor_tp_levels(
            trade_id=trade_id,
            current_price=1.1100,
            pine_update=pine_update
        )
        assert tp2_result["action"] == "partial_close_and_trail"
        
        # Step 4: TP3 hit - Close all
        tp3_result = await self.manager.monitor_tp_levels(
            trade_id=trade_id,
            current_price=1.1150,
            pine_update=pine_update
        )
        assert tp3_result["action"] == "close_all"
        
        # Verify final state
        context = self.manager.get_trade_context(trade_id)
        assert context.state == TradeState.TP3_HIT
    
    @pytest.mark.asyncio
    async def test_sl_recovery_reentry(self):
        """Test 2: Entry → SL Hit → 70% Recovery → Re-entry"""
        # Step 1: Entry
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        # Step 2: SL hit
        sl_result = await self.manager.handle_sl_hit(
            trade_id=trade_id,
            order_type=OrderType.ORDER_A,
            exit_price=1.0950
        )
        assert sl_result["action"] == "sl_hunting_activated"
        hunt_id = sl_result["hunt_id"]
        recovery_price = sl_result["recovery_price"]
        
        # Step 3: 70% recovery with good conditions
        pine_update = PineUpdate(trend="BULLISH", adx=30.0, confidence=80)
        
        recovery_result = await self.manager.check_sl_recovery(
            hunt_id=hunt_id,
            current_price=recovery_price + 0.0001,
            pine_update=pine_update
        )
        assert recovery_result["action"] == "reentry_executed"
        
        # Verify re-entry
        context = self.manager.get_trade_context(trade_id)
        assert context.order_a_state == TradeState.RECOVERY_ACTIVE
    
    @pytest.mark.asyncio
    async def test_tp1_weak_conditions_profit_protection(self):
        """Test 3: Entry → TP1 → Weak Conditions → Exit"""
        # Step 1: Entry
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        # Step 2: TP1 hit with weak conditions
        weak_pine = PineUpdate(trend="BEARISH", adx=15.0, confidence=50)
        
        tp1_result = await self.manager.monitor_tp_levels(
            trade_id=trade_id,
            current_price=1.1050,
            pine_update=weak_pine
        )
        
        # Should close 50% for profit protection
        assert tp1_result["action"] == "partial_close"
        assert tp1_result["percent"] == 50
        assert tp1_result["reason"] == "conditions_weak"
    
    @pytest.mark.asyncio
    async def test_exit_signal_intelligence(self):
        """Test 4: Exit Signal Intelligence"""
        # Entry
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        entry_result = await self.manager.process_entry_signal(alert)
        trade_id = entry_result["trade_id"]
        
        # Exit signal with 60 pips profit + strong trend
        strong_pine = PineUpdate(trend="BULLISH", adx=30.0, confidence=80)
        
        exit_result = await self.manager.process_exit_signal(
            trade_id=trade_id,
            current_price=1.1060,  # 60 pips profit
            pine_update=strong_pine
        )
        
        # Should hold position
        assert exit_result["action"] == "hold"
        assert exit_result["reason"] == "strong_trend_big_profit"


class TestPineUpdateValidation:
    """Test Pine update data validation"""
    
    def test_pine_update_is_strong(self):
        """Test Pine update strength check"""
        strong = PineUpdate(trend="BULLISH", adx=30.0, confidence=80)
        weak = PineUpdate(trend="BULLISH", adx=15.0, confidence=50)
        
        assert strong.is_strong() == True
        assert weak.is_strong() == False
    
    def test_pine_update_is_aligned_buy(self):
        """Test Pine update alignment for BUY"""
        bullish = PineUpdate(trend="BULLISH", adx=30.0, confidence=80)
        bearish = PineUpdate(trend="BEARISH", adx=30.0, confidence=80)
        
        assert bullish.is_aligned("BUY") == True
        assert bearish.is_aligned("BUY") == False
    
    def test_pine_update_is_aligned_sell(self):
        """Test Pine update alignment for SELL"""
        bullish = PineUpdate(trend="BULLISH", adx=30.0, confidence=80)
        bearish = PineUpdate(trend="BEARISH", adx=30.0, confidence=80)
        
        assert bullish.is_aligned("SELL") == False
        assert bearish.is_aligned("SELL") == True


class TestManagerStats:
    """Test manager statistics"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = IntelligentTradeManager(service_api=None)
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting manager statistics"""
        # Create a trade
        alert = {
            "ticker": "EURUSD",
            "direction": "BUY",
            "price": 1.1000,
            "sl": 1.0950,
            "tp1": 1.1050,
            "tp2": 1.1100,
            "tp3": 1.1150
        }
        await self.manager.process_entry_signal(alert)
        
        stats = self.manager.get_stats()
        
        assert stats["total_trades"] == 1
        assert stats["active_trades"] == 1
        assert "config" in stats
    
    @pytest.mark.asyncio
    async def test_get_all_active_trades(self):
        """Test getting all active trades"""
        # Create multiple trades
        for i in range(3):
            alert = {
                "ticker": f"EURUSD{i}",
                "direction": "BUY",
                "price": 1.1000,
                "sl": 1.0950,
                "tp1": 1.1050,
                "tp2": 1.1100,
                "tp3": 1.1150
            }
            await self.manager.process_entry_signal(alert)
        
        active_trades = self.manager.get_all_active_trades()
        
        assert len(active_trades) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
