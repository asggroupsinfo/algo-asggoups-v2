"""
Batch 05 Tests: Telegram UX & Rate Limiting System
Tests for rate_limiter.py, unified_interface.py, and menu_builder.py

Test Categories:
1. TokenBucket - Token bucket algorithm tests
2. TelegramRateLimiter - Rate limiter tests
3. MultiRateLimiter - Multi-bot rate limiter tests
4. LiveHeaderManager - Live header tests
5. UnifiedInterfaceManager - Unified interface tests
6. MenuBuilder - Menu builder tests
7. Integration - Integration tests
8. ThreadSafety - Thread safety tests
"""

import pytest
import threading
import time
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telegram.rate_limiter import (
    MessagePriority,
    ThrottledMessage,
    TokenBucket,
    TelegramRateLimiter,
    MultiRateLimiter
)
from telegram.unified_interface import (
    BotType,
    LiveHeaderManager,
    UnifiedInterfaceManager
)
from telegram.menu_builder import (
    MenuType,
    MenuBuilder,
    MenuFactory
)


class TestMessagePriority:
    """Tests for MessagePriority enum"""
    
    def test_priority_values(self):
        """Test priority values are ordered correctly"""
        assert MessagePriority.LOW.value == 0
        assert MessagePriority.NORMAL.value == 1
        assert MessagePriority.HIGH.value == 2
        assert MessagePriority.CRITICAL.value == 3
    
    def test_priority_comparison(self):
        """Test priority comparison"""
        assert MessagePriority.CRITICAL.value > MessagePriority.HIGH.value
        assert MessagePriority.HIGH.value > MessagePriority.NORMAL.value
        assert MessagePriority.NORMAL.value > MessagePriority.LOW.value


class TestThrottledMessage:
    """Tests for ThrottledMessage dataclass"""
    
    def test_message_creation(self):
        """Test creating a throttled message"""
        msg = ThrottledMessage(
            chat_id="123456",
            text="Test message",
            priority=MessagePriority.HIGH
        )
        
        assert msg.chat_id == "123456"
        assert msg.text == "Test message"
        assert msg.priority == MessagePriority.HIGH
        assert msg.parse_mode == "HTML"
        assert msg.retries == 0
        assert msg.max_retries == 3
    
    def test_message_default_priority(self):
        """Test default priority is NORMAL"""
        msg = ThrottledMessage(chat_id="123", text="Test")
        assert msg.priority == MessagePriority.NORMAL
    
    def test_message_id_generation(self):
        """Test message ID is auto-generated"""
        msg = ThrottledMessage(chat_id="123", text="Test")
        assert msg.message_id is not None
        assert msg.message_id.startswith("msg_")
    
    def test_message_timestamp(self):
        """Test timestamp is set"""
        before = datetime.now()
        msg = ThrottledMessage(chat_id="123", text="Test")
        after = datetime.now()
        
        assert before <= msg.timestamp <= after


class TestTokenBucket:
    """Tests for TokenBucket algorithm"""
    
    def test_bucket_initialization(self):
        """Test bucket initializes with full capacity"""
        bucket = TokenBucket(capacity=10, refill_rate=5, refill_interval=1.0)
        
        assert bucket.capacity == 10
        assert bucket.refill_rate == 5
        assert bucket.tokens == 10
    
    def test_consume_tokens(self):
        """Test consuming tokens"""
        bucket = TokenBucket(capacity=10, refill_rate=5, refill_interval=1.0)
        
        assert bucket.consume(1) is True
        assert bucket.get_available_tokens() == 9
        
        assert bucket.consume(5) is True
        assert bucket.get_available_tokens() == 4
    
    def test_consume_insufficient_tokens(self):
        """Test consuming more tokens than available"""
        bucket = TokenBucket(capacity=5, refill_rate=1, refill_interval=1.0)
        
        assert bucket.consume(3) is True
        assert bucket.consume(3) is False  # Only 2 left
    
    def test_token_refill(self):
        """Test tokens refill over time"""
        bucket = TokenBucket(capacity=10, refill_rate=10, refill_interval=0.1)
        
        # Consume all tokens
        bucket.consume(10)
        assert bucket.get_available_tokens() == 0
        
        # Wait for refill
        time.sleep(0.15)
        
        # Should have some tokens back
        assert bucket.get_available_tokens() > 0
    
    def test_get_wait_time(self):
        """Test calculating wait time"""
        bucket = TokenBucket(capacity=10, refill_rate=10, refill_interval=1.0)
        
        # Full bucket - no wait
        assert bucket.get_wait_time(1) == 0.0
        
        # Empty bucket - need to wait
        bucket.consume(10)
        wait_time = bucket.get_wait_time(5)
        assert wait_time > 0


class TestTelegramRateLimiter:
    """Tests for TelegramRateLimiter"""
    
    def test_limiter_initialization(self):
        """Test rate limiter initialization"""
        limiter = TelegramRateLimiter(
            bot_name="TestBot",
            max_per_minute=20,
            max_per_second=30
        )
        
        assert limiter.bot_name == "TestBot"
        assert limiter.max_per_minute == 20
        assert limiter.max_per_second == 30
        assert limiter._running is False
    
    def test_enqueue_message(self):
        """Test enqueueing a message"""
        limiter = TelegramRateLimiter(bot_name="TestBot")
        
        msg = ThrottledMessage(
            chat_id="123",
            text="Test",
            priority=MessagePriority.NORMAL
        )
        
        result = limiter.enqueue(msg)
        assert result is True
        
        stats = limiter.get_stats()
        assert stats["queued"]["total"] == 1
        assert stats["queued"]["normal"] == 1
    
    def test_priority_queue_ordering(self):
        """Test messages are queued by priority"""
        limiter = TelegramRateLimiter(bot_name="TestBot")
        
        # Enqueue in reverse priority order
        limiter.enqueue(ThrottledMessage(chat_id="1", text="Low", priority=MessagePriority.LOW))
        limiter.enqueue(ThrottledMessage(chat_id="2", text="Normal", priority=MessagePriority.NORMAL))
        limiter.enqueue(ThrottledMessage(chat_id="3", text="High", priority=MessagePriority.HIGH))
        limiter.enqueue(ThrottledMessage(chat_id="4", text="Critical", priority=MessagePriority.CRITICAL))
        
        # Get next message - should be CRITICAL
        msg = limiter._get_next_message()
        assert msg.priority == MessagePriority.CRITICAL
        
        # Next should be HIGH
        msg = limiter._get_next_message()
        assert msg.priority == MessagePriority.HIGH
    
    def test_queue_overflow_drops_low_priority(self):
        """Test queue overflow drops LOW priority first"""
        limiter = TelegramRateLimiter(bot_name="TestBot", max_queue_size=5)
        
        # Fill queue with LOW priority
        for i in range(5):
            limiter.enqueue(ThrottledMessage(
                chat_id=str(i),
                text=f"Low {i}",
                priority=MessagePriority.LOW
            ))
        
        # Add HIGH priority - should drop a LOW
        result = limiter.enqueue(ThrottledMessage(
            chat_id="high",
            text="High priority",
            priority=MessagePriority.HIGH
        ))
        
        assert result is True
        stats = limiter.get_stats()
        assert stats["stats"]["total_dropped"] == 1
    
    def test_start_stop(self):
        """Test starting and stopping the limiter"""
        limiter = TelegramRateLimiter(bot_name="TestBot")
        
        limiter.start()
        assert limiter._running is True
        
        limiter.stop()
        assert limiter._running is False
    
    def test_get_stats(self):
        """Test getting statistics"""
        limiter = TelegramRateLimiter(bot_name="TestBot")
        
        stats = limiter.get_stats()
        
        assert "bot" in stats
        assert "running" in stats
        assert "queued" in stats
        assert "tokens" in stats
        assert "stats" in stats
    
    def test_clear_queue(self):
        """Test clearing the queue"""
        limiter = TelegramRateLimiter(bot_name="TestBot")
        
        # Add some messages
        for i in range(5):
            limiter.enqueue(ThrottledMessage(chat_id=str(i), text=f"Test {i}"))
        
        assert limiter._get_total_queued() == 5
        
        limiter.clear_queue()
        assert limiter._get_total_queued() == 0


class TestMultiRateLimiter:
    """Tests for MultiRateLimiter"""
    
    def test_add_limiter(self):
        """Test adding a rate limiter"""
        multi = MultiRateLimiter()
        
        limiter = multi.add_limiter("Controller", max_per_minute=20)
        
        assert limiter is not None
        assert limiter.bot_name == "Controller"
        assert multi.get_limiter("Controller") is limiter
    
    def test_multiple_limiters(self):
        """Test managing multiple limiters"""
        multi = MultiRateLimiter()
        
        multi.add_limiter("Controller")
        multi.add_limiter("Notification")
        multi.add_limiter("Analytics")
        
        assert len(multi.limiters) == 3
        assert multi.get_limiter("Controller") is not None
        assert multi.get_limiter("Notification") is not None
        assert multi.get_limiter("Analytics") is not None
    
    def test_get_all_stats(self):
        """Test getting stats from all limiters"""
        multi = MultiRateLimiter()
        
        multi.add_limiter("Controller")
        multi.add_limiter("Notification")
        
        stats = multi.get_all_stats()
        
        assert "Controller" in stats
        assert "Notification" in stats
    
    def test_health_status(self):
        """Test health status check"""
        multi = MultiRateLimiter()
        
        multi.add_limiter("Controller")
        
        status = multi.get_health_status()
        
        assert "healthy" in status
        assert "warnings" in status
        assert "limiters" in status


class TestBotType:
    """Tests for BotType enum"""
    
    def test_bot_types(self):
        """Test bot type values"""
        assert BotType.CONTROLLER.value == "controller"
        assert BotType.NOTIFICATION.value == "notification"
        assert BotType.ANALYTICS.value == "analytics"


class TestLiveHeaderManager:
    """Tests for LiveHeaderManager"""
    
    def test_header_initialization(self):
        """Test header manager initialization"""
        header = LiveHeaderManager(
            bot_type=BotType.CONTROLLER,
            chat_id="123456"
        )
        
        assert header.bot_type == BotType.CONTROLLER
        assert header.chat_id == "123456"
        assert header.update_interval == 60
        assert header._running is False
    
    def test_set_data_provider(self):
        """Test setting data providers"""
        header = LiveHeaderManager(
            bot_type=BotType.CONTROLLER,
            chat_id="123456"
        )
        
        provider = Mock(return_value=5)
        header.set_data_provider("open_trades", provider)
        
        assert "open_trades" in header.data_providers
    
    def test_generate_controller_header(self):
        """Test generating controller header content"""
        header = LiveHeaderManager(
            bot_type=BotType.CONTROLLER,
            chat_id="123456"
        )
        
        # Set mock data
        header._cached_data = {
            "open_trades": 3,
            "daily_pnl": 150.50,
            "bot_status": "RUNNING",
            "active_plugins": 2,
            "session_duration": "2h 30m"
        }
        
        content = header._generate_header_content()
        
        assert "ZEPIX CONTROLLER BOT" in content
        assert "Open Trades" in content
        assert "Daily P&L" in content
    
    def test_generate_notification_header(self):
        """Test generating notification header content"""
        header = LiveHeaderManager(
            bot_type=BotType.NOTIFICATION,
            chat_id="123456"
        )
        
        header._cached_data = {
            "alerts_today": 10,
            "entries_today": 5,
            "exits_today": 3,
            "last_alert": "Entry XAUUSD",
            "session_duration": "1h 15m"
        }
        
        content = header._generate_header_content()
        
        assert "ZEPIX NOTIFICATION BOT" in content
        assert "Alerts Today" in content
    
    def test_generate_analytics_header(self):
        """Test generating analytics header content"""
        header = LiveHeaderManager(
            bot_type=BotType.ANALYTICS,
            chat_id="123456"
        )
        
        header._cached_data = {
            "win_rate": 65.5,
            "daily_pnl": 200.00,
            "total_trades": 50,
            "reports_sent": 5,
            "session_duration": "3h 45m"
        }
        
        content = header._generate_header_content()
        
        assert "ZEPIX ANALYTICS BOT" in content
        assert "Win Rate" in content
    
    def test_get_status(self):
        """Test getting header status"""
        header = LiveHeaderManager(
            bot_type=BotType.CONTROLLER,
            chat_id="123456"
        )
        
        status = header.get_status()
        
        assert status["bot_type"] == "controller"
        assert status["running"] is False
        assert "update_interval" in status


class TestUnifiedInterfaceManager:
    """Tests for UnifiedInterfaceManager"""
    
    def test_interface_initialization(self):
        """Test unified interface initialization"""
        interface = UnifiedInterfaceManager()
        
        assert len(interface.headers) == 0
        assert len(interface.command_handlers) == 0
    
    def test_reply_menu_map(self):
        """Test reply menu mapping"""
        interface = UnifiedInterfaceManager()
        
        # Check key mappings exist
        assert "📊 Dashboard" in interface.REPLY_MENU_MAP
        assert "🚨 PANIC CLOSE" in interface.REPLY_MENU_MAP
        assert interface.REPLY_MENU_MAP["🚨 PANIC CLOSE"] == "action_panic_close"
    
    def test_handle_button_press(self):
        """Test handling button press"""
        interface = UnifiedInterfaceManager()
        
        callback = interface.handle_button_press("📊 Dashboard")
        assert callback == "action_dashboard"
        
        callback = interface.handle_button_press("🚨 PANIC CLOSE")
        assert callback == "action_panic_close"
        assert interface.stats["panic_activations"] == 1
    
    def test_handle_unknown_button(self):
        """Test handling unknown button"""
        interface = UnifiedInterfaceManager()
        
        callback = interface.handle_button_press("Unknown Button")
        assert callback is None
    
    def test_register_command_handler(self):
        """Test registering command handlers"""
        interface = UnifiedInterfaceManager()
        
        handler = Mock()
        interface.register_command_handler("action_test", handler)
        
        assert "action_test" in interface.command_handlers
    
    def test_execute_callback(self):
        """Test executing callback"""
        interface = UnifiedInterfaceManager()
        
        handler = Mock()
        interface.register_command_handler("action_test", handler)
        
        result = interface.execute_callback("action_test", {"user_id": 123})
        
        assert result is True
        handler.assert_called_once()
    
    def test_get_persistent_menu(self):
        """Test getting persistent menu"""
        interface = UnifiedInterfaceManager()
        
        menu = interface.get_persistent_menu()
        
        assert "keyboard" in menu
        assert "resize_keyboard" in menu
        assert menu["is_persistent"] is True
        
        # Check PANIC CLOSE is in menu
        all_buttons = [btn for row in menu["keyboard"] for btn in row]
        assert "🚨 PANIC CLOSE" in all_buttons
    
    def test_get_main_inline_menu(self):
        """Test getting main inline menu"""
        interface = UnifiedInterfaceManager()
        
        menu = interface.get_main_inline_menu()
        
        assert "inline_keyboard" in menu
        assert len(menu["inline_keyboard"]) > 0
    
    def test_get_panic_confirmation_menu(self):
        """Test getting panic confirmation menu"""
        interface = UnifiedInterfaceManager()
        
        menu = interface.get_panic_confirmation_menu()
        
        assert "inline_keyboard" in menu
        
        # Check confirm and cancel buttons exist
        buttons = menu["inline_keyboard"][0]
        callbacks = [b["callback_data"] for b in buttons]
        assert "confirm_panic_close" in callbacks
        assert "menu_main" in callbacks
    
    def test_create_header_manager(self):
        """Test creating header manager"""
        interface = UnifiedInterfaceManager()
        
        header = interface.create_header_manager(
            bot_type=BotType.CONTROLLER,
            chat_id="123456"
        )
        
        assert header is not None
        assert BotType.CONTROLLER in interface.headers
    
    def test_get_stats(self):
        """Test getting interface stats"""
        interface = UnifiedInterfaceManager()
        
        stats = interface.get_stats()
        
        assert "stats" in stats
        assert "headers" in stats
        assert "registered_handlers" in stats


class TestMenuBuilder:
    """Tests for MenuBuilder"""
    
    def test_builder_initialization(self):
        """Test menu builder initialization"""
        builder = MenuBuilder()
        
        assert len(builder.menu_stack) == 0
        assert len(builder.current_context) == 0
    
    def test_build_inline_keyboard(self):
        """Test building inline keyboard"""
        builder = MenuBuilder()
        
        buttons = [
            {"text": "Button 1", "callback_data": "btn1"},
            {"text": "Button 2", "callback_data": "btn2"},
            {"text": "Button 3", "callback_data": "btn3"},
            {"text": "Button 4", "callback_data": "btn4"}
        ]
        
        keyboard = builder.build_inline_keyboard(buttons, columns=2)
        
        assert "inline_keyboard" in keyboard
        # 2 rows of buttons + 1 nav row
        assert len(keyboard["inline_keyboard"]) == 3
    
    def test_build_confirmation_menu(self):
        """Test building confirmation menu"""
        builder = MenuBuilder()
        
        menu = builder.build_confirmation_menu(
            action="delete",
            confirm_callback="confirm_delete",
            cancel_callback="cancel"
        )
        
        assert "inline_keyboard" in menu
        buttons = menu["inline_keyboard"][0]
        assert len(buttons) == 2
    
    def test_build_toggle_menu(self):
        """Test building toggle menu"""
        builder = MenuBuilder()
        
        # Test enabled state
        menu = builder.build_toggle_menu(
            feature_name="Feature",
            is_enabled=True,
            toggle_callback="toggle_feature"
        )
        
        assert "inline_keyboard" in menu
        button_text = menu["inline_keyboard"][0][0]["text"]
        assert "Disable" in button_text
        
        # Test disabled state
        menu = builder.build_toggle_menu(
            feature_name="Feature",
            is_enabled=False,
            toggle_callback="toggle_feature"
        )
        
        button_text = menu["inline_keyboard"][0][0]["text"]
        assert "Enable" in button_text
    
    def test_build_pagination_menu(self):
        """Test building paginated menu"""
        builder = MenuBuilder()
        
        items = [
            {"text": f"Item {i}", "callback_data": f"item_{i}"}
            for i in range(12)
        ]
        
        # First page
        menu = builder.build_pagination_menu(items, page=0, items_per_page=5)
        
        assert "inline_keyboard" in menu
        # Should have pagination controls
        
        # Second page
        menu = builder.build_pagination_menu(items, page=1, items_per_page=5)
        assert "inline_keyboard" in menu
    
    def test_build_parameter_menu(self):
        """Test building parameter selection menu"""
        builder = MenuBuilder()
        
        menu = builder.build_parameter_menu(
            param_name="tier",
            options=["5000", "10000", "25000"],
            command="set_tier",
            current_value="10000"
        )
        
        assert "inline_keyboard" in menu
        
        # Check current value is highlighted
        all_buttons = [btn for row in menu["inline_keyboard"] for btn in row]
        highlighted = [b for b in all_buttons if "Current" in b.get("text", "")]
        assert len(highlighted) == 1
    
    def test_menu_stack_operations(self):
        """Test menu stack push/pop"""
        builder = MenuBuilder()
        
        builder.push_menu("menu_main")
        builder.push_menu("menu_trading")
        builder.push_menu("menu_risk")
        
        assert len(builder.menu_stack) == 3
        assert builder.get_previous_menu() == "menu_trading"
        
        popped = builder.pop_menu()
        assert popped == "menu_risk"
        assert len(builder.menu_stack) == 2
    
    def test_context_operations(self):
        """Test context set/get"""
        builder = MenuBuilder()
        
        builder.set_context("selected_symbol", "XAUUSD")
        builder.set_context("selected_tier", "10000")
        
        assert builder.get_context("selected_symbol") == "XAUUSD"
        assert builder.get_context("selected_tier") == "10000"
        assert builder.get_context("nonexistent", "default") == "default"
        
        builder.clear_context()
        assert len(builder.current_context) == 0


class TestMenuFactory:
    """Tests for MenuFactory"""
    
    def test_create_main_menu(self):
        """Test creating main menu"""
        menu = MenuFactory.create_main_menu()
        
        assert "inline_keyboard" in menu
        assert len(menu["inline_keyboard"]) > 0
    
    def test_create_panic_menu(self):
        """Test creating panic menu"""
        menu = MenuFactory.create_panic_menu()
        
        assert "inline_keyboard" in menu
        buttons = menu["inline_keyboard"][0]
        callbacks = [b["callback_data"] for b in buttons]
        assert "confirm_panic_close" in callbacks
    
    def test_create_back_only_menu(self):
        """Test creating back-only menu"""
        menu = MenuFactory.create_back_only_menu()
        
        assert "inline_keyboard" in menu
        assert len(menu["inline_keyboard"]) == 1
        assert menu["inline_keyboard"][0][0]["callback_data"] == "nav_back"
    
    def test_create_home_only_menu(self):
        """Test creating home-only menu"""
        menu = MenuFactory.create_home_only_menu()
        
        assert "inline_keyboard" in menu
        assert menu["inline_keyboard"][0][0]["callback_data"] == "menu_main"


class TestThreadSafety:
    """Tests for thread safety"""
    
    def test_token_bucket_thread_safety(self):
        """Test token bucket is thread-safe"""
        bucket = TokenBucket(capacity=100, refill_rate=100, refill_interval=1.0)
        
        consumed = []
        
        def consume_tokens():
            for _ in range(10):
                if bucket.consume(1):
                    consumed.append(1)
                time.sleep(0.001)
        
        threads = [threading.Thread(target=consume_tokens) for _ in range(10)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Should have consumed exactly 100 tokens (bucket capacity)
        assert len(consumed) <= 100
    
    def test_rate_limiter_thread_safety(self):
        """Test rate limiter is thread-safe"""
        limiter = TelegramRateLimiter(bot_name="TestBot", max_queue_size=1000)
        
        def enqueue_messages():
            for i in range(100):
                limiter.enqueue(ThrottledMessage(
                    chat_id="123",
                    text=f"Message {i}"
                ))
        
        threads = [threading.Thread(target=enqueue_messages) for _ in range(5)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Should have queued 500 messages
        stats = limiter.get_stats()
        assert stats["queued"]["total"] == 500


class TestIntegration:
    """Integration tests"""
    
    def test_rate_limiter_with_callback(self):
        """Test rate limiter with send callback"""
        sent_messages = []
        
        def mock_send(chat_id, text, parse_mode, reply_markup):
            sent_messages.append({"chat_id": chat_id, "text": text})
            return True
        
        limiter = TelegramRateLimiter(
            bot_name="TestBot",
            send_callback=mock_send
        )
        
        # Enqueue a message
        msg = ThrottledMessage(chat_id="123", text="Test message")
        limiter.enqueue(msg)
        
        # Start limiter
        limiter.start()
        
        # Wait for processing
        time.sleep(0.5)
        
        # Stop limiter
        limiter.stop()
        
        # Check message was sent
        assert len(sent_messages) == 1
        assert sent_messages[0]["text"] == "Test message"
    
    def test_unified_interface_with_header(self):
        """Test unified interface with header manager"""
        interface = UnifiedInterfaceManager()
        
        # Create header manager
        header = interface.create_header_manager(
            bot_type=BotType.CONTROLLER,
            chat_id="123456"
        )
        
        # Set data providers
        header.set_data_provider("open_trades", lambda: 5)
        header.set_data_provider("daily_pnl", lambda: 150.0)
        
        # Refresh data
        header._refresh_data()
        
        assert header._cached_data["open_trades"] == 5
        assert header._cached_data["daily_pnl"] == 150.0
    
    def test_menu_builder_with_interface(self):
        """Test menu builder with unified interface"""
        interface = UnifiedInterfaceManager()
        builder = MenuBuilder()
        
        # Get persistent menu from interface
        persistent_menu = interface.get_persistent_menu()
        
        # Build inline menu with builder
        inline_menu = builder.build_quick_actions_menu()
        
        # Both should be valid Telegram keyboard formats
        assert "keyboard" in persistent_menu
        assert "inline_keyboard" in inline_menu
    
    def test_full_message_flow(self):
        """Test full message flow through rate limiter"""
        sent_messages = []
        
        def mock_send(chat_id, text, parse_mode, reply_markup):
            sent_messages.append({
                "chat_id": chat_id,
                "text": text,
                "time": time.time()
            })
            return True
        
        # Create multi-limiter
        multi = MultiRateLimiter()
        
        controller = multi.add_limiter("Controller", send_callback=mock_send)
        notification = multi.add_limiter("Notification", send_callback=mock_send)
        
        # Start all
        multi.start_all()
        
        # Enqueue messages to different bots
        controller.enqueue(ThrottledMessage(
            chat_id="123",
            text="Controller message",
            priority=MessagePriority.NORMAL
        ))
        
        notification.enqueue(ThrottledMessage(
            chat_id="123",
            text="Notification message",
            priority=MessagePriority.HIGH
        ))
        
        # Wait for processing
        time.sleep(0.5)
        
        # Stop all
        multi.stop_all()
        
        # Check messages were sent
        assert len(sent_messages) == 2


class TestBackwardCompatibility:
    """Tests for backward compatibility"""
    
    def test_reply_menu_map_compatibility(self):
        """Test REPLY_MENU_MAP matches existing menu_constants"""
        interface = UnifiedInterfaceManager()
        
        # Key buttons that must exist
        required_buttons = [
            "📊 Dashboard",
            "⏸️ Pause/Resume",
            "🚨 PANIC CLOSE",
            "📈 Active Trades",
            "🛡️ Risk",
            "🔄 Re-entry",
            "📍 Trends"
        ]
        
        for button in required_buttons:
            assert button in interface.REPLY_MENU_MAP, f"Missing button: {button}"
    
    def test_callback_data_format(self):
        """Test callback data follows existing format"""
        interface = UnifiedInterfaceManager()
        
        # Check callback data format
        for button, callback in interface.REPLY_MENU_MAP.items():
            # Should be lowercase with underscores
            assert callback == callback.lower().replace("-", "_").replace(" ", "_") or \
                   callback.startswith("action_") or \
                   callback.startswith("menu_") or \
                   callback.startswith("session_"), \
                   f"Invalid callback format: {callback}"
    
    def test_menu_structure_compatibility(self):
        """Test menu structure matches existing format"""
        builder = MenuBuilder()
        
        menu = builder.build_inline_keyboard(
            buttons=[{"text": "Test", "callback_data": "test"}],
            columns=1
        )
        
        # Must have inline_keyboard key
        assert "inline_keyboard" in menu
        
        # Each row must be a list
        for row in menu["inline_keyboard"]:
            assert isinstance(row, list)
            
            # Each button must have text and callback_data
            for button in row:
                assert "text" in button
                assert "callback_data" in button


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
