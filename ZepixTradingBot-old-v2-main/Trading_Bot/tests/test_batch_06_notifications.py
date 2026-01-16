"""
Test Suite for Batch 06: Sticky Headers & Notification Router

Tests cover:
1. StickyHeader - Pinning logic, auto-regenerate
2. StickyHeaderManager - Multiple header management
3. HybridStickySystem - Reply keyboard + Pinned inline
4. NotificationRouter - Priority-based routing, mute/unmute
5. NotificationFormatter - Message formatting
6. VoiceAlertIntegration - Voice trigger logic
7. Integration tests - Full system integration

Version: 1.0.0
Date: 2026-01-14
"""

import pytest
import threading
import time
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, AsyncMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telegram.sticky_headers import (
    StickyHeader,
    StickyHeaderState,
    StickyHeaderManager,
    HybridStickySystem,
    create_controller_content_generator,
    create_notification_content_generator,
    create_analytics_content_generator
)

from telegram.notification_router import (
    NotificationPriority,
    NotificationType,
    TargetBot,
    Notification,
    NotificationRouter,
    NotificationFormatter,
    DEFAULT_ROUTING_RULES,
    create_default_router
)

from telegram.voice_alert_integration import (
    VoiceAlertConfig,
    VoiceTextGenerator,
    VoiceAlertIntegration,
    create_voice_integration,
    integrate_with_router
)


# ============================================================================
# STICKY HEADER TESTS
# ============================================================================

class TestStickyHeader:
    """Tests for StickyHeader class"""
    
    def test_init_default_values(self):
        """Test StickyHeader initialization with default values"""
        header = StickyHeader(chat_id="123456")
        
        assert header.chat_id == "123456"
        assert header.header_type == "dashboard"
        assert header.update_interval == 30
        assert header.message_id is None
        assert header.state == StickyHeaderState.INACTIVE
        assert header._running is False
    
    def test_init_custom_values(self):
        """Test StickyHeader initialization with custom values"""
        header = StickyHeader(
            chat_id="123456",
            header_type="status",
            update_interval=60
        )
        
        assert header.header_type == "status"
        assert header.update_interval == 60
    
    def test_set_inline_keyboard(self):
        """Test setting inline keyboard"""
        header = StickyHeader(chat_id="123456")
        keyboard = {"inline_keyboard": [[{"text": "Test", "callback_data": "test"}]]}
        
        header.set_inline_keyboard(keyboard)
        
        assert header.inline_keyboard == keyboard
    
    def test_set_content_generator(self):
        """Test setting content generator"""
        header = StickyHeader(chat_id="123456")
        generator = lambda: "Test content"
        
        header.set_content_generator(generator)
        
        assert header.content_generator == generator
    
    def test_get_content_with_generator(self):
        """Test content generation with custom generator"""
        header = StickyHeader(chat_id="123456")
        header.content_generator = lambda: "Custom content"
        
        content = header._get_content()
        
        assert content == "Custom content"
    
    def test_get_content_default(self):
        """Test default content generation"""
        header = StickyHeader(chat_id="123456")
        
        content = header._get_content()
        
        assert "ZEPIX TRADING BOT" in content
        assert datetime.now().strftime("%d-%m-%Y") in content
    
    def test_create_and_pin_success(self):
        """Test successful header creation and pinning"""
        send_callback = Mock(return_value=12345)
        pin_callback = Mock()
        
        header = StickyHeader(
            chat_id="123456",
            send_callback=send_callback,
            pin_callback=pin_callback
        )
        
        result = header._create_and_pin()
        
        assert result is True
        assert header.message_id == 12345
        assert header.state == StickyHeaderState.ACTIVE
        send_callback.assert_called_once()
        pin_callback.assert_called_once()
    
    def test_create_and_pin_no_callback(self):
        """Test header creation without send callback"""
        header = StickyHeader(chat_id="123456")
        
        result = header._create_and_pin()
        
        assert result is False
    
    def test_update_header_success(self):
        """Test successful header update"""
        edit_callback = Mock()
        
        header = StickyHeader(
            chat_id="123456",
            edit_callback=edit_callback
        )
        header.message_id = 12345
        
        result = header._update_header()
        
        assert result is True
        assert header.stats["update_count"] == 1
        edit_callback.assert_called_once()
    
    def test_update_header_message_deleted(self):
        """Test header update when message was deleted (triggers regenerate)"""
        edit_callback = Mock(side_effect=Exception("message to edit not found"))
        send_callback = Mock(return_value=99999)
        pin_callback = Mock()
        
        header = StickyHeader(
            chat_id="123456",
            edit_callback=edit_callback,
            send_callback=send_callback,
            pin_callback=pin_callback
        )
        header.message_id = 12345
        
        result = header._update_header()
        
        # Should regenerate
        assert header.stats["regenerate_count"] == 1
        assert header.message_id == 99999
    
    def test_regenerate(self):
        """Test header regeneration"""
        send_callback = Mock(return_value=99999)
        pin_callback = Mock()
        
        header = StickyHeader(
            chat_id="123456",
            send_callback=send_callback,
            pin_callback=pin_callback
        )
        header.message_id = 12345
        
        result = header._regenerate()
        
        assert result is True
        assert header.stats["regenerate_count"] == 1
        assert header.message_id == 99999
    
    def test_get_status(self):
        """Test getting header status"""
        header = StickyHeader(chat_id="123456", header_type="dashboard")
        header.message_id = 12345
        header.state = StickyHeaderState.ACTIVE
        
        status = header.get_status()
        
        assert status["header_type"] == "dashboard"
        assert status["chat_id"] == "123456"
        assert status["message_id"] == 12345
        assert status["state"] == "active"


class TestStickyHeaderManager:
    """Tests for StickyHeaderManager class"""
    
    def test_init(self):
        """Test StickyHeaderManager initialization"""
        manager = StickyHeaderManager()
        
        assert len(manager.headers) == 0
        assert manager.global_stats["total_headers"] == 0
    
    def test_create_header(self):
        """Test creating a header"""
        manager = StickyHeaderManager()
        
        header = manager.create_header(
            header_id="test_header",
            chat_id="123456",
            header_type="dashboard"
        )
        
        assert header is not None
        assert "test_header" in manager.headers
        assert manager.global_stats["total_headers"] == 1
    
    def test_create_header_duplicate(self):
        """Test creating duplicate header returns existing"""
        manager = StickyHeaderManager()
        
        header1 = manager.create_header(header_id="test", chat_id="123456")
        header2 = manager.create_header(header_id="test", chat_id="123456")
        
        assert header1 is header2
        assert manager.global_stats["total_headers"] == 1
    
    def test_get_header(self):
        """Test getting a header by ID"""
        manager = StickyHeaderManager()
        manager.create_header(header_id="test", chat_id="123456")
        
        header = manager.get_header("test")
        
        assert header is not None
        assert header.chat_id == "123456"
    
    def test_get_header_not_found(self):
        """Test getting non-existent header"""
        manager = StickyHeaderManager()
        
        header = manager.get_header("nonexistent")
        
        assert header is None
    
    def test_remove_header(self):
        """Test removing a header"""
        manager = StickyHeaderManager()
        manager.create_header(header_id="test", chat_id="123456")
        
        result = manager.remove_header("test")
        
        assert result is True
        assert "test" not in manager.headers
        assert manager.global_stats["total_headers"] == 0
    
    def test_get_stats(self):
        """Test getting manager statistics"""
        manager = StickyHeaderManager()
        manager.create_header(header_id="test1", chat_id="123456")
        manager.create_header(header_id="test2", chat_id="789012")
        
        stats = manager.get_stats()
        
        assert stats["global"]["total_headers"] == 2
        assert "test1" in stats["headers"]
        assert "test2" in stats["headers"]


class TestHybridStickySystem:
    """Tests for HybridStickySystem class"""
    
    def test_init(self):
        """Test HybridStickySystem initialization"""
        system = HybridStickySystem(chat_id="123456")
        
        assert system.chat_id == "123456"
        assert system.reply_keyboard_active is False
        assert system.pinned_header_active is False
    
    def test_set_reply_keyboard(self):
        """Test setting custom reply keyboard"""
        system = HybridStickySystem(chat_id="123456")
        custom_keyboard = {"keyboard": [["Button1", "Button2"]]}
        
        system.set_reply_keyboard(custom_keyboard)
        
        assert system.reply_keyboard == custom_keyboard
    
    def test_set_inline_keyboard(self):
        """Test setting custom inline keyboard"""
        system = HybridStickySystem(chat_id="123456")
        custom_keyboard = {"inline_keyboard": [[{"text": "Test", "callback_data": "test"}]]}
        
        system.set_inline_keyboard(custom_keyboard)
        
        assert system.inline_keyboard == custom_keyboard
    
    def test_get_status(self):
        """Test getting system status"""
        system = HybridStickySystem(chat_id="123456")
        
        status = system.get_status()
        
        assert status["chat_id"] == "123456"
        assert "reply_keyboard_active" in status
        assert "pinned_header_active" in status


class TestContentGenerators:
    """Tests for content generator functions"""
    
    def test_controller_content_generator(self):
        """Test controller bot content generator"""
        data_providers = {
            "open_trades": lambda: 5,
            "daily_pnl": lambda: 150.50,
            "bot_status": lambda: "RUNNING",
            "active_plugins": lambda: 2
        }
        
        generator = create_controller_content_generator(data_providers)
        content = generator()
        
        assert "ZEPIX CONTROLLER BOT" in content
        assert "5" in content  # open_trades
        assert "150.50" in content  # daily_pnl
        assert "RUNNING" in content
    
    def test_notification_content_generator(self):
        """Test notification bot content generator"""
        data_providers = {
            "alerts_today": lambda: 10,
            "entries_today": lambda: 3,
            "exits_today": lambda: 2,
            "last_alert": lambda: "EURUSD Entry"
        }
        
        generator = create_notification_content_generator(data_providers)
        content = generator()
        
        assert "ZEPIX NOTIFICATION BOT" in content
        assert "10" in content  # alerts_today
        assert "3" in content  # entries_today
    
    def test_analytics_content_generator(self):
        """Test analytics bot content generator"""
        data_providers = {
            "win_rate": lambda: 65.5,
            "daily_pnl": lambda: 200.00,
            "total_trades": lambda: 15,
            "reports_sent": lambda: 3
        }
        
        generator = create_analytics_content_generator(data_providers)
        content = generator()
        
        assert "ZEPIX ANALYTICS BOT" in content
        assert "65.5" in content  # win_rate
        assert "15" in content  # total_trades


# ============================================================================
# NOTIFICATION ROUTER TESTS
# ============================================================================

class TestNotificationPriority:
    """Tests for NotificationPriority enum"""
    
    def test_priority_values(self):
        """Test priority values are correct"""
        assert NotificationPriority.CRITICAL.value == 5
        assert NotificationPriority.HIGH.value == 4
        assert NotificationPriority.MEDIUM.value == 3
        assert NotificationPriority.LOW.value == 2
        assert NotificationPriority.INFO.value == 1
    
    def test_priority_comparison(self):
        """Test priority comparison"""
        assert NotificationPriority.CRITICAL.value > NotificationPriority.HIGH.value
        assert NotificationPriority.HIGH.value > NotificationPriority.MEDIUM.value


class TestNotificationType:
    """Tests for NotificationType enum"""
    
    def test_trade_event_types(self):
        """Test trade event notification types"""
        assert NotificationType.ENTRY.value == "entry"
        assert NotificationType.EXIT.value == "exit"
        assert NotificationType.TP_HIT.value == "tp_hit"
        assert NotificationType.SL_HIT.value == "sl_hit"
    
    def test_system_event_types(self):
        """Test system event notification types"""
        assert NotificationType.BOT_STARTED.value == "bot_started"
        assert NotificationType.EMERGENCY_STOP.value == "emergency_stop"
        assert NotificationType.MT5_DISCONNECT.value == "mt5_disconnect"


class TestNotification:
    """Tests for Notification dataclass"""
    
    def test_notification_creation(self):
        """Test creating a notification"""
        notification = Notification(
            notification_type=NotificationType.ENTRY,
            priority=NotificationPriority.HIGH,
            message="Test entry"
        )
        
        assert notification.notification_type == NotificationType.ENTRY
        assert notification.priority == NotificationPriority.HIGH
        assert notification.message == "Test entry"
        assert notification.notification_id is not None
    
    def test_notification_with_data(self):
        """Test notification with additional data"""
        notification = Notification(
            notification_type=NotificationType.EXIT,
            priority=NotificationPriority.HIGH,
            message="Test exit",
            data={"symbol": "EURUSD", "profit": 50.0}
        )
        
        assert notification.data["symbol"] == "EURUSD"
        assert notification.data["profit"] == 50.0


class TestDefaultRoutingRules:
    """Tests for default routing rules"""
    
    def test_entry_routing(self):
        """Test entry notification routing"""
        rule = DEFAULT_ROUTING_RULES[NotificationType.ENTRY]
        
        assert rule["target"] == TargetBot.NOTIFICATION
        assert rule["priority"] == NotificationPriority.HIGH
        assert rule["voice"] is True
    
    def test_emergency_routing(self):
        """Test emergency notification routing"""
        rule = DEFAULT_ROUTING_RULES[NotificationType.EMERGENCY_STOP]
        
        assert rule["target"] == TargetBot.ALL
        assert rule["priority"] == NotificationPriority.CRITICAL
        assert rule["voice"] is True
    
    def test_daily_summary_routing(self):
        """Test daily summary routing"""
        rule = DEFAULT_ROUTING_RULES[NotificationType.DAILY_SUMMARY]
        
        assert rule["target"] == TargetBot.ANALYTICS
        assert rule["priority"] == NotificationPriority.LOW
        assert rule["voice"] is False


class TestNotificationRouter:
    """Tests for NotificationRouter class"""
    
    def test_init(self):
        """Test NotificationRouter initialization"""
        router = NotificationRouter()
        
        assert router.global_mute is False
        assert router.voice_mute is False
        assert len(router.muted_types) == 0
    
    def test_init_with_callbacks(self):
        """Test initialization with callbacks"""
        controller = Mock()
        notification = Mock()
        analytics = Mock()
        
        router = NotificationRouter(
            controller_callback=controller,
            notification_callback=notification,
            analytics_callback=analytics
        )
        
        assert router.controller_callback == controller
        assert router.notification_callback == notification
        assert router.analytics_callback == analytics
    
    def test_mute_type(self):
        """Test muting a notification type"""
        router = NotificationRouter()
        
        router.mute(NotificationType.ENTRY)
        
        assert NotificationType.ENTRY in router.muted_types
    
    def test_unmute_type(self):
        """Test unmuting a notification type"""
        router = NotificationRouter()
        router.mute(NotificationType.ENTRY)
        
        router.unmute(NotificationType.ENTRY)
        
        assert NotificationType.ENTRY not in router.muted_types
    
    def test_mute_all(self):
        """Test global mute"""
        router = NotificationRouter()
        
        router.mute_all()
        
        assert router.global_mute is True
    
    def test_unmute_all(self):
        """Test unmuting all"""
        router = NotificationRouter()
        router.mute_all()
        router.mute(NotificationType.ENTRY)
        
        router.unmute_all()
        
        assert router.global_mute is False
        assert len(router.muted_types) == 0
    
    def test_is_muted_global(self):
        """Test is_muted with global mute"""
        router = NotificationRouter()
        router.mute_all()
        
        assert router.is_muted(NotificationType.ENTRY, NotificationPriority.HIGH) is True
    
    def test_is_muted_critical_never_muted(self):
        """Test CRITICAL priority is never muted"""
        router = NotificationRouter()
        router.mute_all()
        
        assert router.is_muted(NotificationType.EMERGENCY_STOP, NotificationPriority.CRITICAL) is False
    
    def test_is_muted_specific_type(self):
        """Test is_muted with specific type muted"""
        router = NotificationRouter()
        router.mute(NotificationType.ENTRY)
        
        assert router.is_muted(NotificationType.ENTRY, NotificationPriority.HIGH) is True
        assert router.is_muted(NotificationType.EXIT, NotificationPriority.HIGH) is False
    
    def test_send_to_notification_bot(self):
        """Test sending to notification bot"""
        notification_callback = Mock(return_value=12345)
        
        router = NotificationRouter(notification_callback=notification_callback)
        
        result = router.send(
            NotificationType.ENTRY,
            "Test entry message"
        )
        
        assert result is True
        notification_callback.assert_called_once()
    
    def test_send_to_controller_bot(self):
        """Test sending to controller bot"""
        controller_callback = Mock(return_value=12345)
        
        router = NotificationRouter(controller_callback=controller_callback)
        
        result = router.send(
            NotificationType.BOT_STARTED,
            "Bot started"
        )
        
        assert result is True
        controller_callback.assert_called_once()
    
    def test_send_to_analytics_bot(self):
        """Test sending to analytics bot"""
        analytics_callback = Mock(return_value=12345)
        
        router = NotificationRouter(analytics_callback=analytics_callback)
        
        result = router.send(
            NotificationType.DAILY_SUMMARY,
            "Daily summary"
        )
        
        assert result is True
        analytics_callback.assert_called_once()
    
    def test_send_broadcast_critical(self):
        """Test CRITICAL priority broadcasts to all"""
        controller = Mock(return_value=1)
        notification = Mock(return_value=2)
        analytics = Mock(return_value=3)
        
        router = NotificationRouter(
            controller_callback=controller,
            notification_callback=notification,
            analytics_callback=analytics
        )
        
        result = router.send(
            NotificationType.EMERGENCY_STOP,
            "Emergency!",
            priority=NotificationPriority.CRITICAL
        )
        
        assert result is True
        controller.assert_called_once()
        notification.assert_called_once()
        analytics.assert_called_once()
    
    def test_send_muted_notification(self):
        """Test sending muted notification"""
        notification_callback = Mock()
        
        router = NotificationRouter(notification_callback=notification_callback)
        router.mute(NotificationType.ENTRY)
        
        result = router.send(NotificationType.ENTRY, "Test")
        
        assert result is False
        notification_callback.assert_not_called()
        assert router.stats["muted_notifications"] == 1
    
    def test_send_with_voice(self):
        """Test sending with voice callback"""
        notification_callback = Mock(return_value=12345)
        voice_callback = Mock()
        
        router = NotificationRouter(
            notification_callback=notification_callback,
            voice_callback=voice_callback
        )
        
        router.send(
            NotificationType.ENTRY,
            "Test entry",
            voice_override=True
        )
        
        voice_callback.assert_called_once()
        assert router.stats["voice_alerts_sent"] == 1
    
    def test_send_voice_muted(self):
        """Test voice is not triggered when muted"""
        notification_callback = Mock(return_value=12345)
        voice_callback = Mock()
        
        router = NotificationRouter(
            notification_callback=notification_callback,
            voice_callback=voice_callback
        )
        router.mute_voice()
        
        router.send(
            NotificationType.ENTRY,
            "Test entry",
            voice_override=True
        )
        
        voice_callback.assert_not_called()
    
    def test_register_formatter(self):
        """Test registering custom formatter"""
        router = NotificationRouter()
        formatter = lambda data: f"Custom: {data.get('symbol')}"
        
        router.register_formatter(NotificationType.ENTRY, formatter)
        
        assert NotificationType.ENTRY in router.formatters
    
    def test_set_routing_rule(self):
        """Test setting custom routing rule"""
        router = NotificationRouter()
        
        router.set_routing_rule(
            NotificationType.INFO,
            TargetBot.ANALYTICS,
            NotificationPriority.MEDIUM,
            voice=True
        )
        
        rule = router.routing_rules[NotificationType.INFO]
        assert rule["target"] == TargetBot.ANALYTICS
        assert rule["priority"] == NotificationPriority.MEDIUM
        assert rule["voice"] is True
    
    def test_get_stats(self):
        """Test getting router statistics"""
        router = NotificationRouter()
        
        stats = router.get_stats()
        
        assert "stats" in stats
        assert "muted_types" in stats
        assert "global_mute" in stats
        assert "voice_mute" in stats
    
    def test_get_muted_types(self):
        """Test getting muted types list"""
        router = NotificationRouter()
        router.mute(NotificationType.ENTRY)
        router.mute(NotificationType.EXIT)
        
        muted = router.get_muted_types()
        
        assert "entry" in muted
        assert "exit" in muted


class TestNotificationFormatter:
    """Tests for NotificationFormatter class"""
    
    def test_format_entry(self):
        """Test entry message formatting"""
        data = {
            "plugin_name": "CombinedV3",
            "symbol": "EURUSD",
            "direction": "BUY",
            "entry_price": 1.0850,
            "order_a_lot": 0.1,
            "order_a_sl": 1.0800,
            "order_a_tp": 1.0900
        }
        
        message = NotificationFormatter.format_entry(data)
        
        assert "ENTRY ALERT" in message
        assert "CombinedV3" in message
        assert "EURUSD" in message
        assert "BUY" in message
    
    def test_format_exit(self):
        """Test exit message formatting"""
        data = {
            "plugin_name": "CombinedV3",
            "symbol": "EURUSD",
            "direction": "BUY",
            "profit": 50.0,
            "entry_price": 1.0850,
            "exit_price": 1.0900,
            "hold_time": "2h 30m",
            "reason": "TP Hit"
        }
        
        message = NotificationFormatter.format_exit(data)
        
        assert "EXIT ALERT" in message
        assert "EURUSD" in message
        assert "50.00" in message
    
    def test_format_daily_summary(self):
        """Test daily summary formatting"""
        data = {
            "date": "2026-01-14",
            "total_trades": 10,
            "winners": 7,
            "losers": 3,
            "win_rate": 70.0,
            "net_pnl": 250.0,
            "gross_profit": 350.0,
            "gross_loss": 100.0
        }
        
        message = NotificationFormatter.format_daily_summary(data)
        
        assert "DAILY SUMMARY" in message
        assert "2026-01-14" in message
        assert "70.0%" in message
    
    def test_format_emergency(self):
        """Test emergency message formatting"""
        data = {
            "reason": "Daily loss limit reached",
            "details": "Total loss: $500"
        }
        
        message = NotificationFormatter.format_emergency(data)
        
        assert "EMERGENCY ALERT" in message
        assert "Daily loss limit reached" in message
    
    def test_format_error(self):
        """Test error message formatting"""
        data = {
            "error_type": "MT5 Connection",
            "severity": "HIGH",
            "details": "Connection timeout"
        }
        
        message = NotificationFormatter.format_error(data)
        
        assert "ERROR ALERT" in message
        assert "MT5 Connection" in message
        assert "HIGH" in message


class TestCreateDefaultRouter:
    """Tests for create_default_router function"""
    
    def test_create_default_router(self):
        """Test creating router with default formatters"""
        router = create_default_router()
        
        assert NotificationType.ENTRY in router.formatters
        assert NotificationType.EXIT in router.formatters
        assert NotificationType.DAILY_SUMMARY in router.formatters
        assert NotificationType.EMERGENCY_STOP in router.formatters
        assert NotificationType.ERROR in router.formatters


# ============================================================================
# VOICE ALERT INTEGRATION TESTS
# ============================================================================

class TestVoiceAlertConfig:
    """Tests for VoiceAlertConfig class"""
    
    def test_default_voice_triggers(self):
        """Test default voice triggers configuration"""
        triggers = VoiceAlertConfig.DEFAULT_VOICE_TRIGGERS
        
        # Trade events should have voice
        assert triggers[NotificationType.ENTRY] is True
        assert triggers[NotificationType.EXIT] is True
        
        # Info events should not have voice
        assert triggers[NotificationType.PLUGIN_LOADED] is False
        assert triggers[NotificationType.DAILY_SUMMARY] is False
    
    def test_priority_mapping(self):
        """Test priority mapping"""
        mapping = VoiceAlertConfig.PRIORITY_MAPPING
        
        assert mapping[NotificationPriority.CRITICAL] == "CRITICAL"
        assert mapping[NotificationPriority.HIGH] == "HIGH"
        assert mapping[NotificationPriority.INFO] == "LOW"


class TestVoiceTextGenerator:
    """Tests for VoiceTextGenerator class"""
    
    def test_generate_entry_voice(self):
        """Test entry voice text generation"""
        data = {
            "direction": "BUY",
            "symbol": "EURUSD",
            "entry_price": 1.0850,
            "signal_type": "SCREENER_BULLISH"
        }
        
        text = VoiceTextGenerator.generate_entry_voice(data)
        
        assert "BUY" in text
        assert "EURUSD" in text
        assert "1.085" in text
    
    def test_generate_exit_voice_profit(self):
        """Test exit voice text with profit"""
        data = {
            "direction": "BUY",
            "symbol": "EURUSD",
            "profit": 50.0
        }
        
        text = VoiceTextGenerator.generate_exit_voice(data)
        
        assert "profit" in text
        assert "50" in text
    
    def test_generate_exit_voice_loss(self):
        """Test exit voice text with loss"""
        data = {
            "direction": "SELL",
            "symbol": "GBPUSD",
            "profit": -30.0
        }
        
        text = VoiceTextGenerator.generate_exit_voice(data)
        
        assert "loss" in text
        assert "30" in text
    
    def test_generate_tp_hit_voice(self):
        """Test TP hit voice text"""
        data = {
            "tp_level": 2,
            "profit": 75.0,
            "symbol": "EURUSD"
        }
        
        text = VoiceTextGenerator.generate_tp_hit_voice(data)
        
        assert "Take profit 2" in text
        assert "75" in text
    
    def test_generate_sl_hit_voice(self):
        """Test SL hit voice text"""
        data = {
            "symbol": "EURUSD",
            "profit": -25.0
        }
        
        text = VoiceTextGenerator.generate_sl_hit_voice(data)
        
        assert "Stop loss" in text
        assert "EURUSD" in text
    
    def test_generate_emergency_voice(self):
        """Test emergency voice text"""
        data = {"reason": "Daily loss limit reached"}
        
        text = VoiceTextGenerator.generate_emergency_voice(data)
        
        assert "Emergency" in text
        assert "Daily loss limit" in text
    
    def test_generate_bot_started_voice(self):
        """Test bot started voice text"""
        text = VoiceTextGenerator.generate_bot_started_voice({})
        
        assert "started" in text
    
    def test_generate_mt5_disconnect_voice(self):
        """Test MT5 disconnect voice text"""
        text = VoiceTextGenerator.generate_mt5_disconnect_voice({})
        
        assert "MetaTrader" in text or "connection" in text
    
    def test_generate_generic_voice(self):
        """Test generic voice text"""
        data = {"message": "Test notification message"}
        
        text = VoiceTextGenerator.generate_generic_voice(data)
        
        assert "Test notification message" in text
    
    def test_generate_generic_voice_truncation(self):
        """Test generic voice text truncation for long messages"""
        long_message = "A" * 150
        data = {"message": long_message}
        
        text = VoiceTextGenerator.generate_generic_voice(data)
        
        assert len(text) <= 103  # 100 chars + "..."


class TestVoiceAlertIntegration:
    """Tests for VoiceAlertIntegration class"""
    
    def test_init(self):
        """Test VoiceAlertIntegration initialization"""
        integration = VoiceAlertIntegration()
        
        assert integration.voice_enabled is True
        assert integration.voice_system is None
        assert len(integration.disabled_types) == 0
    
    def test_init_with_voice_system(self):
        """Test initialization with voice system"""
        mock_voice_system = Mock()
        
        integration = VoiceAlertIntegration(voice_alert_system=mock_voice_system)
        
        assert integration.voice_system == mock_voice_system
    
    def test_enable_disable_voice(self):
        """Test enabling/disabling voice globally"""
        integration = VoiceAlertIntegration()
        
        integration.disable_voice()
        assert integration.voice_enabled is False
        
        integration.enable_voice()
        assert integration.voice_enabled is True
    
    def test_enable_disable_type(self):
        """Test enabling/disabling voice for specific type"""
        integration = VoiceAlertIntegration()
        
        integration.disable_type(NotificationType.ENTRY)
        assert NotificationType.ENTRY in integration.disabled_types
        
        integration.enable_type(NotificationType.ENTRY)
        assert NotificationType.ENTRY not in integration.disabled_types
    
    def test_should_trigger_voice_enabled(self):
        """Test should_trigger_voice when enabled"""
        mock_voice_system = Mock()
        integration = VoiceAlertIntegration(voice_alert_system=mock_voice_system)
        
        result = integration.should_trigger_voice(
            NotificationType.ENTRY,
            NotificationPriority.HIGH
        )
        
        assert result is True
    
    def test_should_trigger_voice_disabled_globally(self):
        """Test should_trigger_voice when globally disabled"""
        mock_voice_system = Mock()
        integration = VoiceAlertIntegration(voice_alert_system=mock_voice_system)
        integration.disable_voice()
        
        result = integration.should_trigger_voice(
            NotificationType.ENTRY,
            NotificationPriority.HIGH
        )
        
        assert result is False
    
    def test_should_trigger_voice_disabled_type(self):
        """Test should_trigger_voice when type is disabled"""
        mock_voice_system = Mock()
        integration = VoiceAlertIntegration(voice_alert_system=mock_voice_system)
        integration.disable_type(NotificationType.ENTRY)
        
        result = integration.should_trigger_voice(
            NotificationType.ENTRY,
            NotificationPriority.HIGH
        )
        
        assert result is False
    
    def test_should_trigger_voice_critical_always(self):
        """Test CRITICAL priority always triggers voice"""
        mock_voice_system = Mock()
        integration = VoiceAlertIntegration(voice_alert_system=mock_voice_system)
        integration.disable_type(NotificationType.EMERGENCY_STOP)
        
        result = integration.should_trigger_voice(
            NotificationType.EMERGENCY_STOP,
            NotificationPriority.CRITICAL
        )
        
        assert result is True
    
    def test_should_trigger_voice_no_system(self):
        """Test should_trigger_voice without voice system"""
        integration = VoiceAlertIntegration()
        
        result = integration.should_trigger_voice(
            NotificationType.ENTRY,
            NotificationPriority.HIGH
        )
        
        assert result is False
    
    def test_generate_voice_text(self):
        """Test voice text generation"""
        integration = VoiceAlertIntegration()
        data = {
            "direction": "BUY",
            "symbol": "EURUSD",
            "entry_price": 1.0850
        }
        
        text = integration.generate_voice_text(NotificationType.ENTRY, data)
        
        assert "BUY" in text
        assert "EURUSD" in text
    
    def test_register_text_generator(self):
        """Test registering custom text generator"""
        integration = VoiceAlertIntegration()
        custom_generator = lambda data: "Custom voice text"
        
        integration.register_text_generator(NotificationType.INFO, custom_generator)
        
        text = integration.generate_voice_text(NotificationType.INFO, {})
        assert text == "Custom voice text"
    
    def test_get_stats(self):
        """Test getting voice alert statistics"""
        integration = VoiceAlertIntegration()
        integration.disable_type(NotificationType.ENTRY)
        
        stats = integration.get_stats()
        
        assert "enabled" in stats
        assert "voice_system_connected" in stats
        assert "disabled_types" in stats
        assert "entry" in stats["disabled_types"]
    
    def test_get_voice_callback(self):
        """Test getting voice callback function"""
        integration = VoiceAlertIntegration()
        
        callback = integration.get_voice_callback()
        
        assert callable(callback)


class TestCreateVoiceIntegration:
    """Tests for create_voice_integration function"""
    
    def test_create_voice_integration(self):
        """Test creating voice integration"""
        integration = create_voice_integration()
        
        assert integration is not None
        assert isinstance(integration, VoiceAlertIntegration)
    
    def test_create_voice_integration_with_system(self):
        """Test creating voice integration with voice system"""
        mock_voice_system = Mock()
        
        integration = create_voice_integration(voice_alert_system=mock_voice_system)
        
        assert integration.voice_system == mock_voice_system


class TestIntegrateWithRouter:
    """Tests for integrate_with_router function"""
    
    def test_integrate_with_router(self):
        """Test integrating voice with router"""
        router = NotificationRouter()
        
        integration = integrate_with_router(router)
        
        assert integration is not None
        assert router.voice_callback is not None


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestFullIntegration:
    """Integration tests for the complete notification system"""
    
    def test_router_with_voice_integration(self):
        """Test router with voice integration"""
        controller = Mock(return_value=1)
        notification = Mock(return_value=2)
        analytics = Mock(return_value=3)
        
        router = create_default_router(
            controller_callback=controller,
            notification_callback=notification,
            analytics_callback=analytics
        )
        
        integration = integrate_with_router(router)
        
        # Send entry notification
        result = router.send(
            NotificationType.ENTRY,
            "Test entry",
            data={"symbol": "EURUSD", "direction": "BUY"}
        )
        
        assert result is True
        notification.assert_called_once()
    
    def test_sticky_header_with_notification_router(self):
        """Test sticky header manager with notification router"""
        send_callback = Mock(return_value=12345)
        edit_callback = Mock()
        pin_callback = Mock()
        
        # Create header manager
        header_manager = StickyHeaderManager()
        header = header_manager.create_header(
            header_id="test",
            chat_id="123456",
            send_callback=send_callback,
            edit_callback=edit_callback,
            pin_callback=pin_callback
        )
        
        # Create notification router
        router = NotificationRouter(
            notification_callback=lambda msg: send_callback(chat_id="123456", text=msg)
        )
        
        # Both should work independently
        assert header is not None
        assert router is not None
    
    def test_mute_unmute_flow(self):
        """Test complete mute/unmute flow"""
        notification = Mock(return_value=1)
        
        router = NotificationRouter(notification_callback=notification)
        
        # Send should work
        router.send(NotificationType.ENTRY, "Test 1")
        assert notification.call_count == 1
        
        # Mute entry
        router.mute(NotificationType.ENTRY)
        router.send(NotificationType.ENTRY, "Test 2")
        assert notification.call_count == 1  # Still 1, muted
        
        # Unmute entry
        router.unmute(NotificationType.ENTRY)
        router.send(NotificationType.ENTRY, "Test 3")
        assert notification.call_count == 2  # Now 2
    
    def test_priority_routing_flow(self):
        """Test priority-based routing flow"""
        controller = Mock(return_value=1)
        notification = Mock(return_value=2)
        analytics = Mock(return_value=3)
        
        router = NotificationRouter(
            controller_callback=controller,
            notification_callback=notification,
            analytics_callback=analytics
        )
        
        # INFO -> Controller
        router.send(NotificationType.BOT_STARTED, "Bot started")
        controller.assert_called()
        
        # HIGH -> Notification
        router.send(NotificationType.ENTRY, "Entry")
        notification.assert_called()
        
        # LOW -> Analytics
        router.send(NotificationType.DAILY_SUMMARY, "Summary")
        analytics.assert_called()
    
    def test_voice_trigger_conditions(self):
        """Test voice alert trigger conditions"""
        mock_voice_system = Mock()
        integration = VoiceAlertIntegration(voice_alert_system=mock_voice_system)
        
        # Entry should trigger voice
        assert integration.should_trigger_voice(
            NotificationType.ENTRY,
            NotificationPriority.HIGH
        ) is True
        
        # Daily summary should not trigger voice
        assert integration.should_trigger_voice(
            NotificationType.DAILY_SUMMARY,
            NotificationPriority.LOW
        ) is False
        
        # CRITICAL always triggers
        integration.disable_type(NotificationType.EMERGENCY_STOP)
        assert integration.should_trigger_voice(
            NotificationType.EMERGENCY_STOP,
            NotificationPriority.CRITICAL
        ) is True


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing systems"""
    
    def test_notification_router_with_existing_bot(self):
        """Test router works with existing bot send methods"""
        # Simulate existing bot's send_message method
        existing_bot_send = Mock(return_value=12345)
        
        router = NotificationRouter(
            notification_callback=existing_bot_send
        )
        
        result = router.send(NotificationType.ENTRY, "Test message")
        
        assert result is True
        existing_bot_send.assert_called_once()
    
    def test_voice_integration_with_existing_voice_system(self):
        """Test voice integration works with existing VoiceAlertSystem interface"""
        # Mock existing VoiceAlertSystem
        mock_voice_system = Mock()
        mock_voice_system.send_voice_alert = AsyncMock()
        
        integration = VoiceAlertIntegration(voice_alert_system=mock_voice_system)
        
        # Should be able to check trigger conditions
        assert integration.should_trigger_voice(
            NotificationType.ENTRY,
            NotificationPriority.HIGH
        ) is True
    
    def test_sticky_header_callback_interface(self):
        """Test sticky header works with standard callback interface"""
        # Standard Telegram bot interface
        send_message = Mock(return_value=12345)
        edit_message = Mock()
        pin_message = Mock()
        
        header = StickyHeader(
            chat_id="123456",
            send_callback=send_message,
            edit_callback=edit_message,
            pin_callback=pin_message
        )
        
        # Should work with standard callbacks
        result = header._create_and_pin()
        
        assert result is True
        send_message.assert_called_once()
        pin_message.assert_called_once()


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
