"""
Batch 04: Multi-Telegram System Architecture Tests

Tests for:
- BaseTelegramBot initialization and methods
- ControllerBot command handling
- NotificationBot alert formatting
- AnalyticsBot report formatting
- MessageRouter routing logic
- MultiTelegramManager orchestration
- Single bot mode fallback
- Multi-bot mode routing

Version: 1.0.0
Date: 2026-01-14
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telegram.base_telegram_bot import BaseTelegramBot
from telegram.controller_bot import ControllerBot
from telegram.notification_bot import NotificationBot
from telegram.analytics_bot import AnalyticsBot
from telegram.message_router import MessageRouter, MessageType, MessagePriority
from telegram.multi_telegram_manager import MultiTelegramManager


class TestBaseTelegramBot:
    """Tests for BaseTelegramBot class"""
    
    def test_init_with_token(self):
        """Test initialization with valid token"""
        bot = BaseTelegramBot("test_token", "123456", "TestBot")
        
        assert bot.token == "test_token"
        assert bot.chat_id == "123456"
        assert bot.bot_name == "TestBot"
        assert bot.is_active is True
        assert bot._message_count == 0
    
    def test_init_without_token(self):
        """Test initialization without token"""
        bot = BaseTelegramBot(None, "123456", "TestBot")
        
        assert bot.is_active is False
        assert bot.token is None
    
    def test_is_active_property(self):
        """Test is_active property"""
        active_bot = BaseTelegramBot("token", "123")
        inactive_bot = BaseTelegramBot(None, "123")
        
        assert active_bot.is_active is True
        assert inactive_bot.is_active is False
    
    def test_get_stats(self):
        """Test get_stats method"""
        bot = BaseTelegramBot("token", "123", "TestBot")
        stats = bot.get_stats()
        
        assert stats["bot_name"] == "TestBot"
        assert stats["is_active"] is True
        assert stats["message_count"] == 0
        assert stats["last_message_time"] is None
    
    @patch('telegram.base_telegram_bot.requests.Session')
    def test_send_message_inactive_bot(self, mock_session):
        """Test send_message on inactive bot"""
        bot = BaseTelegramBot(None, "123")
        result = bot.send_message("test message")
        
        assert result is None
    
    @patch('telegram.base_telegram_bot.requests.Session')
    def test_send_message_no_chat_id(self, mock_session):
        """Test send_message without chat_id"""
        bot = BaseTelegramBot("token", None)
        result = bot.send_message("test message")
        
        assert result is None


class TestControllerBot:
    """Tests for ControllerBot class"""
    
    def test_init(self):
        """Test ControllerBot initialization"""
        bot = ControllerBot("test_token", "123456")
        
        assert bot.bot_name == "ControllerBot"
        assert bot.is_active is True
        assert bot._command_handlers == {}
    
    def test_register_command(self):
        """Test command registration"""
        bot = ControllerBot("token", "123")
        handler = Mock()
        
        bot.register_command("/test", handler)
        
        assert "/test" in bot._command_handlers
        assert bot._command_handlers["/test"] == handler
    
    def test_set_dependencies(self):
        """Test setting dependencies"""
        bot = ControllerBot("token", "123")
        mock_engine = Mock()
        mock_risk = Mock()
        mock_legacy = Mock()
        
        bot.set_dependencies(
            trading_engine=mock_engine,
            risk_manager=mock_risk,
            legacy_bot=mock_legacy
        )
        
        assert bot._trading_engine == mock_engine
        assert bot._risk_manager == mock_risk
        assert bot._legacy_bot == mock_legacy
    
    def test_format_status_message(self):
        """Test status message formatting"""
        bot = ControllerBot("token", "123")
        
        status_data = {
            "is_active": True,
            "uptime": "5h 30m",
            "active_plugins": 2,
            "open_trades": 3,
            "daily_pnl": 150.50
        }
        
        message = bot._format_status_message(status_data)
        
        assert "BOT STATUS" in message
        assert "Active" in message
        assert "5h 30m" in message
        assert "$150.50" in message


class TestNotificationBot:
    """Tests for NotificationBot class"""
    
    def test_init(self):
        """Test NotificationBot initialization"""
        bot = NotificationBot("test_token", "123456")
        
        assert bot.bot_name == "NotificationBot"
        assert bot.is_active is True
        assert bot._voice_alerts_enabled is False
    
    def test_set_voice_alert_system(self):
        """Test voice alert system setup"""
        bot = NotificationBot("token", "123")
        mock_voice = Mock()
        
        bot.set_voice_alert_system(mock_voice)
        
        assert bot._voice_alerts_enabled is True
        assert bot._voice_alert_system == mock_voice
    
    def test_format_entry_message(self):
        """Test entry message formatting"""
        bot = NotificationBot("token", "123")
        
        trade_data = {
            "plugin_name": "V3_Combined",
            "symbol": "EURUSD",
            "direction": "BUY",
            "entry_price": 1.0850,
            "order_a_lot": 0.1,
            "order_a_sl": 1.0800,
            "order_a_tp": 1.0900,
            "signal_type": "SCREENER_BULLISH",
            "timeframe": "M15",
            "logic_route": "LOGIC1",
            "ticket_a": 12345
        }
        
        message = bot._format_entry_message(trade_data)
        
        assert "ENTRY ALERT" in message
        assert "V3_Combined" in message
        assert "EURUSD" in message
        assert "BUY" in message
        assert "1.085" in message
        assert "#12345" in message
    
    def test_format_exit_message(self):
        """Test exit message formatting"""
        bot = NotificationBot("token", "123")
        
        trade_data = {
            "plugin_name": "V3_Combined",
            "symbol": "EURUSD",
            "direction": "BUY",
            "entry_price": 1.0850,
            "exit_price": 1.0900,
            "hold_time": "2h 15m",
            "order_a_profit": 50.00,
            "order_a_pips": 50.0,
            "total_profit": 50.00,
            "total_pips": 50.0,
            "commission": 2.00,
            "reason": "TP Hit"
        }
        
        message = bot._format_exit_message(trade_data)
        
        assert "EXIT ALERT" in message
        assert "EURUSD" in message
        assert "$50.00" in message or "$+50.00" in message
        assert "TP Hit" in message
    
    def test_format_profit_booking_message(self):
        """Test profit booking message formatting"""
        bot = NotificationBot("token", "123")
        
        booking_data = {
            "plugin_name": "V3_Combined",
            "symbol": "EURUSD",
            "direction": "BUY",
            "ticket": 12345,
            "closed_percentage": 50,
            "closed_lots": 0.05,
            "remaining_lots": 0.05,
            "booking_profit": 25.00,
            "booking_pips": 25.0,
            "total_profit": 50.00,
            "action": "TP1 Hit",
            "next_target": "TP2"
        }
        
        message = bot._format_profit_booking_message(booking_data)
        
        assert "PROFIT BOOKED" in message
        assert "50%" in message
        assert "#12345" in message
    
    def test_format_error_message(self):
        """Test error message formatting"""
        bot = NotificationBot("token", "123")
        
        error_data = {
            "error_type": "Connection Error",
            "severity": "HIGH",
            "details": "MT5 connection lost",
            "status": "Reconnecting",
            "action_required": True
        }
        
        message = bot._format_error_message(error_data)
        
        assert "ERROR ALERT" in message
        assert "Connection Error" in message
        assert "HIGH" in message
        assert "Manual Action Required" in message


class TestAnalyticsBot:
    """Tests for AnalyticsBot class"""
    
    def test_init(self):
        """Test AnalyticsBot initialization"""
        bot = AnalyticsBot("test_token", "123456")
        
        assert bot.bot_name == "AnalyticsBot"
        assert bot.is_active is True
        assert bot._report_cache == {}
    
    def test_format_performance_report(self):
        """Test performance report formatting"""
        bot = AnalyticsBot("token", "123")
        
        report_data = {
            "period": "weekly",
            "start_date": "2026-01-07",
            "end_date": "2026-01-14",
            "total_trades": 25,
            "winning_trades": 18,
            "losing_trades": 7,
            "win_rate": 72.0,
            "total_profit": 500.00,
            "total_pips": 250.0,
            "avg_profit_per_trade": 20.00,
            "profit_factor": 2.5,
            "max_drawdown": 100.00,
            "best_day": 150.00,
            "worst_day": -50.00
        }
        
        message = bot._format_performance_report(report_data)
        
        assert "PERFORMANCE REPORT" in message
        assert "WEEKLY" in message
        assert "25" in message
        assert "72.0%" in message
        assert "$500.00" in message or "$+500.00" in message
    
    def test_format_statistics_summary(self):
        """Test statistics summary formatting"""
        bot = AnalyticsBot("token", "123")
        
        stats_data = {
            "account_balance": 10000.00,
            "account_equity": 10500.00,
            "open_positions": 2,
            "open_profit": 500.00,
            "today_profit": 150.00,
            "today_trades": 5,
            "week_profit": 500.00,
            "month_profit": 1500.00,
            "all_time_profit": 5000.00,
            "active_plugins": ["V3_Combined", "V6_1M"]
        }
        
        message = bot._format_statistics_summary(stats_data)
        
        assert "STATISTICS SUMMARY" in message
        assert "$10,000.00" in message
        assert "V3_Combined" in message
    
    def test_format_trend_analysis(self):
        """Test trend analysis formatting"""
        bot = AnalyticsBot("token", "123")
        
        trend_data = {
            "symbol": "EURUSD",
            "overall_bias": "BULLISH",
            "strength": 75,
            "timeframes": {
                "M1": "BULLISH",
                "M5": "BULLISH",
                "M15": "NEUTRAL",
                "H1": "BULLISH"
            },
            "key_levels": {
                "resistance": 1.0900,
                "support": 1.0800,
                "pivot": 1.0850
            },
            "recommendation": "Look for BUY entries"
        }
        
        message = bot._format_trend_analysis(trend_data)
        
        assert "TREND ANALYSIS" in message
        assert "EURUSD" in message
        assert "BULLISH" in message
        assert "75%" in message
    
    def test_format_plugin_performance(self):
        """Test plugin performance formatting"""
        bot = AnalyticsBot("token", "123")
        
        plugin_data = {
            "plugin_name": "V3_Combined",
            "plugin_version": "1.0.0",
            "status": "Active",
            "total_trades": 100,
            "win_rate": 68.0,
            "total_profit": 2500.00,
            "avg_trade_duration": "45m",
            "best_trade": 150.00,
            "worst_trade": -75.00,
            "signals_processed": 500,
            "signals_executed": 100
        }
        
        message = bot._format_plugin_performance(plugin_data)
        
        assert "PLUGIN PERFORMANCE" in message
        assert "V3_Combined" in message
        assert "Active" in message
        assert "68.0%" in message


class TestMessageRouter:
    """Tests for MessageRouter class"""
    
    def test_init_multi_bot_mode(self):
        """Test initialization in multi-bot mode"""
        controller = Mock(spec=ControllerBot)
        controller.is_active = True
        notification = Mock(spec=NotificationBot)
        notification.is_active = True
        analytics = Mock(spec=AnalyticsBot)
        analytics.is_active = True
        
        router = MessageRouter(
            controller_bot=controller,
            notification_bot=notification,
            analytics_bot=analytics
        )
        
        assert router._single_bot_mode is False
    
    def test_init_single_bot_mode(self):
        """Test initialization in single-bot mode"""
        controller = Mock(spec=ControllerBot)
        controller.is_active = True
        
        router = MessageRouter(
            controller_bot=controller,
            notification_bot=None,
            analytics_bot=None
        )
        
        assert router._single_bot_mode is True
    
    def test_classify_message_command(self):
        """Test message classification for commands"""
        router = MessageRouter()
        
        assert router.classify_message("/status") == MessageType.COMMAND
        assert router.classify_message("/start") == MessageType.COMMAND
    
    def test_classify_message_alert(self):
        """Test message classification for alerts"""
        router = MessageRouter()
        
        assert router.classify_message("New trade entry on EURUSD") == MessageType.ALERT
        assert router.classify_message("Position closed with profit") == MessageType.ALERT
        assert router.classify_message("SL hit on order") == MessageType.ALERT
    
    def test_classify_message_report(self):
        """Test message classification for reports"""
        router = MessageRouter()
        
        assert router.classify_message("Weekly performance report") == MessageType.REPORT
        assert router.classify_message("Statistics summary") == MessageType.REPORT
        assert router.classify_message("Daily analysis") == MessageType.REPORT
    
    def test_classify_message_explicit_type(self):
        """Test message classification with explicit type"""
        router = MessageRouter()
        
        assert router.classify_message("test", explicit_type="alert") == MessageType.ALERT
        assert router.classify_message("test", explicit_type="report") == MessageType.REPORT
        assert router.classify_message("test", explicit_type="command") == MessageType.COMMAND
    
    def test_determine_priority_critical(self):
        """Test priority determination for critical messages"""
        router = MessageRouter()
        
        priority = router.determine_priority("EMERGENCY: Margin call!", MessageType.ALERT)
        assert priority == MessagePriority.CRITICAL
    
    def test_determine_priority_high(self):
        """Test priority determination for high priority messages"""
        router = MessageRouter()
        
        priority = router.determine_priority("Error: Connection failed", MessageType.ALERT)
        assert priority == MessagePriority.HIGH
    
    def test_determine_priority_normal(self):
        """Test priority determination for normal messages"""
        router = MessageRouter()
        
        priority = router.determine_priority("Status update", MessageType.COMMAND)
        assert priority == MessagePriority.NORMAL
    
    def test_get_routing_stats(self):
        """Test routing statistics"""
        router = MessageRouter()
        stats = router.get_routing_stats()
        
        assert "mode" in stats
        assert "total_messages" in stats
        assert "by_destination" in stats
        assert "success_rate" in stats
        assert "bots_active" in stats
    
    def test_reset_stats(self):
        """Test statistics reset"""
        router = MessageRouter()
        router._routing_stats["controller"] = 10
        router._routing_stats["notification"] = 5
        
        router.reset_stats()
        
        assert router._routing_stats["controller"] == 0
        assert router._routing_stats["notification"] == 0


class TestMultiTelegramManager:
    """Tests for MultiTelegramManager class"""
    
    def test_init_single_bot_mode(self):
        """Test initialization with single token (single bot mode)"""
        config = {
            "telegram_token": "main_token",
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        
        assert manager.is_single_bot_mode is True
        assert manager.main_bot is not None
        assert manager.controller_bot is not None
        assert manager.notification_bot is not None
        assert manager.analytics_bot is not None
    
    def test_init_multi_bot_mode(self):
        """Test initialization with multiple tokens (multi-bot mode)"""
        config = {
            "telegram_token": "main_token",
            "telegram_controller_token": "controller_token",
            "telegram_notification_token": "notification_token",
            "telegram_analytics_token": "analytics_token",
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        
        assert manager.is_single_bot_mode is False
        assert manager.active_bots_count == 3
    
    def test_init_partial_tokens(self):
        """Test initialization with partial tokens"""
        config = {
            "telegram_token": "main_token",
            "telegram_notification_token": "notification_token",
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        
        assert manager.notification_bot is not None
        assert manager.controller_bot is not None
    
    def test_init_no_tokens(self):
        """Test initialization without any tokens"""
        config = {
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        
        assert manager.main_bot is None
        assert manager.controller_bot is None
    
    def test_set_legacy_bot(self):
        """Test setting legacy bot"""
        config = {
            "telegram_token": "main_token",
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        mock_legacy = Mock()
        
        manager.set_legacy_bot(mock_legacy)
        
        assert manager._legacy_bot == mock_legacy
    
    def test_set_voice_alert_system(self):
        """Test setting voice alert system"""
        config = {
            "telegram_token": "main_token",
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        mock_voice = Mock()
        
        manager.set_voice_alert_system(mock_voice)
        
        assert manager.notification_bot._voice_alerts_enabled is True
    
    def test_get_stats(self):
        """Test getting manager statistics"""
        config = {
            "telegram_token": "main_token",
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        stats = manager.get_stats()
        
        assert "mode" in stats
        assert "bots" in stats
        assert "routing" in stats
        assert "legacy_bot_connected" in stats
    
    def test_active_bots_count_property(self):
        """Test active_bots_count property"""
        config = {
            "telegram_token": "main_token",
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        
        assert manager.active_bots_count == 3


class TestMessageRoutingIntegration:
    """Integration tests for message routing"""
    
    def test_alert_routes_to_notification_bot(self):
        """Test that alerts route to notification bot"""
        controller = Mock(spec=ControllerBot)
        controller.is_active = True
        controller.send_message = Mock(return_value=1)
        
        notification = Mock(spec=NotificationBot)
        notification.is_active = True
        notification.send_message = Mock(return_value=2)
        
        analytics = Mock(spec=AnalyticsBot)
        analytics.is_active = True
        analytics.send_message = Mock(return_value=3)
        
        router = MessageRouter(
            controller_bot=controller,
            notification_bot=notification,
            analytics_bot=analytics
        )
        
        result = router.send_alert("Trade entry alert")
        
        notification.send_message.assert_called()
        assert result == 2
    
    def test_report_routes_to_analytics_bot(self):
        """Test that reports route to analytics bot"""
        controller = Mock(spec=ControllerBot)
        controller.is_active = True
        controller.send_message = Mock(return_value=1)
        
        notification = Mock(spec=NotificationBot)
        notification.is_active = True
        notification.send_message = Mock(return_value=2)
        
        analytics = Mock(spec=AnalyticsBot)
        analytics.is_active = True
        analytics.send_message = Mock(return_value=3)
        
        router = MessageRouter(
            controller_bot=controller,
            notification_bot=notification,
            analytics_bot=analytics
        )
        
        result = router.send_report("Performance report")
        
        analytics.send_message.assert_called()
        assert result == 3
    
    def test_command_routes_to_controller_bot(self):
        """Test that commands route to controller bot"""
        controller = Mock(spec=ControllerBot)
        controller.is_active = True
        controller.send_message = Mock(return_value=1)
        
        notification = Mock(spec=NotificationBot)
        notification.is_active = True
        notification.send_message = Mock(return_value=2)
        
        analytics = Mock(spec=AnalyticsBot)
        analytics.is_active = True
        analytics.send_message = Mock(return_value=3)
        
        router = MessageRouter(
            controller_bot=controller,
            notification_bot=notification,
            analytics_bot=analytics
        )
        
        result = router.send_command_response("/status response")
        
        controller.send_message.assert_called()
        assert result == 1
    
    def test_fallback_when_bot_unavailable(self):
        """Test fallback to main bot when specialized bot unavailable"""
        controller = Mock(spec=ControllerBot)
        controller.is_active = False
        
        fallback = Mock(spec=BaseTelegramBot)
        fallback.send_message = Mock(return_value=99)
        
        router = MessageRouter(
            controller_bot=controller,
            notification_bot=None,
            analytics_bot=None,
            fallback_bot=fallback
        )
        
        result = router.route_message("test message", message_type="command")
        
        fallback.send_message.assert_called()
        assert result == 99


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing system"""
    
    def test_route_message_signature_compatible(self):
        """Test that route_message has compatible signature"""
        config = {
            "telegram_token": "main_token",
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        
        result = manager.route_message("alert", "Test message")
        
    def test_send_alert_signature_compatible(self):
        """Test that send_alert has compatible signature"""
        config = {
            "telegram_token": "main_token",
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        
        result = manager.send_alert("Test alert")
    
    def test_send_report_signature_compatible(self):
        """Test that send_report has compatible signature"""
        config = {
            "telegram_token": "main_token",
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        
        result = manager.send_report("Test report")
    
    def test_send_admin_message_signature_compatible(self):
        """Test that send_admin_message has compatible signature"""
        config = {
            "telegram_token": "main_token",
            "telegram_chat_id": "123456"
        }
        
        manager = MultiTelegramManager(config)
        
        result = manager.send_admin_message("Test admin message")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
