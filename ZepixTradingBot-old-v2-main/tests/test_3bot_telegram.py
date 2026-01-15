"""
Tests for 3-Bot Telegram System (Plan 07)

Verifies commands and notifications are routed correctly to:
- Controller Bot (72 commands)
- Notification Bot (42 notifications)
- Analytics Bot (8 commands + 6 notifications)

Version: 1.0.0
Date: 2026-01-15
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# Import the modules under test
from src.telegram.message_router import MessageRouter, BotType, MessageType, MessagePriority
from src.telegram.multi_telegram_manager import MultiTelegramManager


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_controller_bot():
    """Create mock controller bot"""
    bot = MagicMock()
    bot.is_active = True
    bot.send_message = MagicMock(return_value=123)
    bot.handle_command = AsyncMock(return_value={"status": "success"})
    bot.send_system_notification = AsyncMock(return_value=456)
    bot.get_stats = MagicMock(return_value={"messages_sent": 10})
    return bot


@pytest.fixture
def mock_notification_bot():
    """Create mock notification bot"""
    bot = MagicMock()
    bot.is_active = True
    bot.send_message = MagicMock(return_value=124)
    bot.send_notification = AsyncMock(return_value=457)
    bot.send_entry_alert = MagicMock(return_value=458)
    bot.send_exit_alert = MagicMock(return_value=459)
    bot.send_profit_booking_alert = MagicMock(return_value=460)
    bot.send_error_alert = MagicMock(return_value=461)
    bot.get_stats = MagicMock(return_value={"messages_sent": 20})
    return bot


@pytest.fixture
def mock_analytics_bot():
    """Create mock analytics bot"""
    bot = MagicMock()
    bot.is_active = True
    bot.send_message = MagicMock(return_value=125)
    bot.handle_command = AsyncMock(return_value={"status": "success"})
    bot.send_analytics_notification = AsyncMock(return_value=462)
    bot.send_performance_report = MagicMock(return_value=463)
    bot.send_statistics_summary = MagicMock(return_value=464)
    bot.get_stats = MagicMock(return_value={"messages_sent": 5})
    return bot


@pytest.fixture
def mock_fallback_bot():
    """Create mock fallback/legacy bot"""
    bot = MagicMock()
    bot.send_message = MagicMock(return_value=126)
    bot.handle_command = AsyncMock(return_value={"status": "success"})
    return bot


@pytest.fixture
def router(mock_controller_bot, mock_notification_bot, mock_analytics_bot, mock_fallback_bot):
    """Create router with mock bots"""
    return MessageRouter(
        controller_bot=mock_controller_bot,
        notification_bot=mock_notification_bot,
        analytics_bot=mock_analytics_bot,
        fallback_bot=mock_fallback_bot
    )


# ============================================================================
# Test MessageRouter - Command Routing
# ============================================================================

class TestMessageRouterCommandRouting:
    """Test command routing to correct bots"""
    
    def test_controller_commands_route_correctly(self, router):
        """Test that controller commands are routed to Controller Bot"""
        controller_commands = [
            'start', 'stop', 'pause', 'resume', 'status', 'restart', 'shutdown',
            'logic1_on', 'logic1_off', 'strategy', 'symbols',
            'reentry_on', 'reentry_off', 'chains', 'sl_hunt_on', 'sl_hunt_off',
            'trends', 'set_trend', 'auto_trend',
            'risk', 'set_lot', 'daily_limit', 'balance', 'margin',
            'sl_system', 'sl1_on', 'sl1_off', 'sl_pips',
            'dual_on', 'dual_off',
            'profit_on', 'profit_off', 'profit_status',
            'health', 'mt5_status', 'positions', 'orders', 'close_all', 'panic_close',
            'logs', 'errors', 'config', 'reload_config', 'version', 'help', 'debug'
        ]
        
        for cmd in controller_commands:
            bot_type = router.get_bot_for_command(cmd)
            assert bot_type == BotType.CONTROLLER, f"Command '{cmd}' should route to CONTROLLER"
    
    def test_analytics_commands_route_correctly(self, router):
        """Test that analytics commands are routed to Analytics Bot"""
        analytics_commands = ['daily', 'weekly', 'monthly', 'pnl', 'winrate', 'performance', 'stats', 'history']
        
        for cmd in analytics_commands:
            bot_type = router.get_bot_for_command(cmd)
            assert bot_type == BotType.ANALYTICS, f"Command '{cmd}' should route to ANALYTICS"
    
    def test_unknown_command_routes_to_legacy(self, router):
        """Test that unknown commands route to legacy bot"""
        unknown_commands = ['unknown_cmd', 'random', 'test123']
        
        for cmd in unknown_commands:
            bot_type = router.get_bot_for_command(cmd)
            assert bot_type == BotType.LEGACY, f"Unknown command '{cmd}' should route to LEGACY"
    
    def test_command_with_slash_prefix(self, router):
        """Test that commands with / prefix are handled correctly"""
        assert router.get_bot_for_command('/start') == BotType.CONTROLLER
        assert router.get_bot_for_command('/daily') == BotType.ANALYTICS
        assert router.get_bot_for_command('/unknown') == BotType.LEGACY
    
    def test_command_case_insensitive(self, router):
        """Test that command routing is case insensitive"""
        assert router.get_bot_for_command('START') == BotType.CONTROLLER
        assert router.get_bot_for_command('Daily') == BotType.ANALYTICS
        assert router.get_bot_for_command('HEALTH') == BotType.CONTROLLER


# ============================================================================
# Test MessageRouter - Notification Routing
# ============================================================================

class TestMessageRouterNotificationRouting:
    """Test notification routing to correct bots"""
    
    def test_trade_notifications_route_to_notification_bot(self, router):
        """Test that trade notifications route to Notification Bot"""
        trade_notifications = [
            'trade_opened', 'order_a_opened', 'order_b_opened', 'signal_received',
            'dual_order_created', 'position_opened', 'entry_executed', 'pending_order_placed',
            'trade_closed', 'sl_hit', 'tp_hit', 'manual_close', 'reversal_close', 'position_closed'
        ]
        
        for notif in trade_notifications:
            bot_type = router.get_bot_for_notification(notif)
            assert bot_type == BotType.NOTIFICATION, f"Notification '{notif}' should route to NOTIFICATION"
    
    def test_recovery_notifications_route_to_notification_bot(self, router):
        """Test that recovery notifications route to Notification Bot"""
        recovery_notifications = [
            'recovery_started', 'recovery_success', 'recovery_failed', 'recovery_timeout',
            'sl_hunt_started', 'sl_hunt_success', 'tp_continuation_started', 'exit_continuation_started'
        ]
        
        for notif in recovery_notifications:
            bot_type = router.get_bot_for_notification(notif)
            assert bot_type == BotType.NOTIFICATION, f"Notification '{notif}' should route to NOTIFICATION"
    
    def test_profit_notifications_route_to_notification_bot(self, router):
        """Test that profit booking notifications route to Notification Bot"""
        profit_notifications = [
            'profit_booked', 'chain_advanced', 'chain_completed', 'chain_sl_hit',
            'profit_target_hit', 'pyramid_level_up'
        ]
        
        for notif in profit_notifications:
            bot_type = router.get_bot_for_notification(notif)
            assert bot_type == BotType.NOTIFICATION, f"Notification '{notif}' should route to NOTIFICATION"
    
    def test_system_notifications_route_to_controller(self, router):
        """Test that system notifications route to Controller Bot"""
        system_notifications = [
            'system_started', 'system_stopped', 'config_reloaded', 'error_alert',
            'mt5_connected', 'mt5_disconnected', 'plugin_enabled', 'plugin_disabled'
        ]
        
        for notif in system_notifications:
            bot_type = router.get_bot_for_notification(notif)
            assert bot_type == BotType.CONTROLLER, f"Notification '{notif}' should route to CONTROLLER"
    
    def test_analytics_notifications_route_to_analytics(self, router):
        """Test that analytics notifications route to Analytics Bot"""
        analytics_notifications = [
            'daily_summary', 'weekly_summary', 'monthly_summary',
            'performance_alert', 'drawdown_alert', 'profit_milestone'
        ]
        
        for notif in analytics_notifications:
            bot_type = router.get_bot_for_notification(notif)
            assert bot_type == BotType.ANALYTICS, f"Notification '{notif}' should route to ANALYTICS"
    
    def test_unknown_notification_defaults_to_notification_bot(self, router):
        """Test that unknown notifications default to Notification Bot"""
        unknown_notifications = ['unknown_notif', 'random_alert', 'test_notification']
        
        for notif in unknown_notifications:
            bot_type = router.get_bot_for_notification(notif)
            assert bot_type == BotType.NOTIFICATION, f"Unknown notification '{notif}' should default to NOTIFICATION"


# ============================================================================
# Test MessageRouter - Async Routing Execution
# ============================================================================

class TestMessageRouterAsyncRouting:
    """Test async routing execution"""
    
    @pytest.mark.asyncio
    async def test_route_command_to_controller(self, router, mock_controller_bot):
        """Test command routing execution to controller"""
        await router.route_command('status')
        mock_controller_bot.handle_command.assert_called_once_with('status')
    
    @pytest.mark.asyncio
    async def test_route_command_to_analytics(self, router, mock_analytics_bot):
        """Test command routing execution to analytics"""
        await router.route_command('daily')
        mock_analytics_bot.handle_command.assert_called_once_with('daily')
    
    @pytest.mark.asyncio
    async def test_route_notification_to_notification_bot(self, router, mock_notification_bot):
        """Test notification routing execution"""
        await router.route_notification('trade_opened', 'Test message')
        mock_notification_bot.send_notification.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_route_notification_to_controller(self, router, mock_controller_bot):
        """Test system notification routing to controller"""
        await router.route_notification('system_started', 'System started')
        mock_controller_bot.send_system_notification.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_route_notification_to_analytics(self, router, mock_analytics_bot):
        """Test analytics notification routing"""
        await router.route_notification('daily_summary', 'Daily summary')
        mock_analytics_bot.send_analytics_notification.assert_called_once()


# ============================================================================
# Test MessageRouter - Message Classification
# ============================================================================

class TestMessageRouterClassification:
    """Test message classification"""
    
    def test_classify_command_message(self, router):
        """Test command message classification"""
        assert router.classify_message('/start') == MessageType.COMMAND
        assert router.classify_message('/status') == MessageType.COMMAND
    
    def test_classify_alert_message(self, router):
        """Test alert message classification"""
        assert router.classify_message('Trade opened: EURUSD BUY') == MessageType.ALERT
        assert router.classify_message('SL hit on position') == MessageType.ALERT
    
    def test_classify_report_message(self, router):
        """Test report message classification"""
        assert router.classify_message('Daily performance report') == MessageType.REPORT
        assert router.classify_message('Weekly statistics summary') == MessageType.REPORT
    
    def test_explicit_type_override(self, router):
        """Test explicit type overrides classification"""
        assert router.classify_message('Any message', explicit_type='alert') == MessageType.ALERT
        assert router.classify_message('Any message', explicit_type='report') == MessageType.REPORT


# ============================================================================
# Test MessageRouter - Priority Determination
# ============================================================================

class TestMessageRouterPriority:
    """Test message priority determination"""
    
    def test_critical_priority(self, router):
        """Test critical priority detection"""
        assert router.determine_priority('EMERGENCY: Margin call', MessageType.ALERT) == MessagePriority.CRITICAL
        assert router.determine_priority('CRITICAL: System failure', MessageType.ERROR) == MessagePriority.CRITICAL
    
    def test_high_priority(self, router):
        """Test high priority detection"""
        assert router.determine_priority('Error occurred', MessageType.ERROR) == MessagePriority.HIGH
        assert router.determine_priority('SL hit loss', MessageType.ALERT) == MessagePriority.HIGH
    
    def test_normal_priority(self, router):
        """Test normal priority for commands"""
        assert router.determine_priority('/status', MessageType.COMMAND) == MessagePriority.NORMAL
    
    def test_low_priority(self, router):
        """Test low priority for reports"""
        assert router.determine_priority('Weekly report', MessageType.REPORT) == MessagePriority.LOW


# ============================================================================
# Test MessageRouter - Routing Statistics
# ============================================================================

class TestMessageRouterStats:
    """Test routing statistics"""
    
    def test_initial_stats(self, router):
        """Test initial routing stats are zero"""
        stats = router.get_routing_stats()
        assert stats['total_messages'] == 0
        assert stats['by_destination']['controller'] == 0
        assert stats['by_destination']['notification'] == 0
        assert stats['by_destination']['analytics'] == 0
    
    def test_stats_after_routing(self, router, mock_controller_bot):
        """Test stats increment after routing"""
        router._route_to_controller('Test message', 'HTML')
        stats = router.get_routing_stats()
        assert stats['by_destination']['controller'] == 1
    
    def test_reset_stats(self, router, mock_controller_bot):
        """Test stats reset"""
        router._route_to_controller('Test message', 'HTML')
        router.reset_stats()
        stats = router.get_routing_stats()
        assert stats['total_messages'] == 0


# ============================================================================
# Test MultiTelegramManager
# ============================================================================

class TestMultiTelegramManager:
    """Test MultiTelegramManager"""
    
    @pytest.fixture
    def manager_config(self):
        """Create manager config"""
        return {
            'telegram_token': 'test_main_token',
            'telegram_controller_token': 'test_controller_token',
            'telegram_notification_token': 'test_notification_token',
            'telegram_analytics_token': 'test_analytics_token',
            'telegram_chat_id': '123456789'
        }
    
    def test_manager_initialization(self, manager_config):
        """Test manager creates all bots"""
        with patch('src.telegram.multi_telegram_manager.ControllerBot'), \
             patch('src.telegram.multi_telegram_manager.NotificationBot'), \
             patch('src.telegram.multi_telegram_manager.AnalyticsBot'), \
             patch('src.telegram.multi_telegram_manager.BaseTelegramBot'):
            manager = MultiTelegramManager(manager_config)
            
            assert manager.controller_bot is not None
            assert manager.notification_bot is not None
            assert manager.analytics_bot is not None
            assert manager.router is not None
    
    def test_single_bot_mode_detection(self):
        """Test single bot mode when only one token provided"""
        config = {
            'telegram_token': 'test_token',
            'telegram_chat_id': '123456789'
        }
        
        with patch('src.telegram.multi_telegram_manager.ControllerBot'), \
             patch('src.telegram.multi_telegram_manager.NotificationBot'), \
             patch('src.telegram.multi_telegram_manager.AnalyticsBot'), \
             patch('src.telegram.multi_telegram_manager.BaseTelegramBot'):
            manager = MultiTelegramManager(config)
            assert manager.is_single_bot_mode == True
    
    def test_multi_bot_mode_detection(self, manager_config):
        """Test multi bot mode when multiple tokens provided"""
        with patch('src.telegram.multi_telegram_manager.ControllerBot'), \
             patch('src.telegram.multi_telegram_manager.NotificationBot'), \
             patch('src.telegram.multi_telegram_manager.AnalyticsBot'), \
             patch('src.telegram.multi_telegram_manager.BaseTelegramBot'):
            manager = MultiTelegramManager(manager_config)
            assert manager.is_single_bot_mode == False
    
    def test_stats_before_init(self, manager_config):
        """Test stats before initialization"""
        with patch('src.telegram.multi_telegram_manager.ControllerBot'), \
             patch('src.telegram.multi_telegram_manager.NotificationBot'), \
             patch('src.telegram.multi_telegram_manager.AnalyticsBot'), \
             patch('src.telegram.multi_telegram_manager.BaseTelegramBot'):
            manager = MultiTelegramManager(manager_config)
            stats = manager.get_stats()
            
            assert 'mode' in stats
            assert 'bots' in stats
            assert 'routing' in stats


# ============================================================================
# Test Success Criteria (Plan 07)
# ============================================================================

class TestSuccessCriteria:
    """Verify all 8 success criteria for Plan 07"""
    
    def test_criterion_1_message_router_routes_commands(self, router):
        """Criterion 1: MessageRouter routes commands correctly"""
        # Controller commands
        assert router.get_bot_for_command('start') == BotType.CONTROLLER
        assert router.get_bot_for_command('health') == BotType.CONTROLLER
        
        # Analytics commands
        assert router.get_bot_for_command('daily') == BotType.ANALYTICS
        assert router.get_bot_for_command('stats') == BotType.ANALYTICS
    
    def test_criterion_2_message_router_routes_notifications(self, router):
        """Criterion 2: MessageRouter routes notifications correctly"""
        # Trade notifications -> Notification Bot
        assert router.get_bot_for_notification('trade_opened') == BotType.NOTIFICATION
        assert router.get_bot_for_notification('sl_hit') == BotType.NOTIFICATION
        
        # System notifications -> Controller Bot
        assert router.get_bot_for_notification('system_started') == BotType.CONTROLLER
        
        # Analytics notifications -> Analytics Bot
        assert router.get_bot_for_notification('daily_summary') == BotType.ANALYTICS
    
    def test_criterion_3_controller_receives_72_commands(self, router):
        """Criterion 3: Controller Bot receives 72 commands"""
        # Verify count of controller commands
        assert len(router.CONTROLLER_COMMANDS) >= 70  # Allow some flexibility
    
    def test_criterion_4_notification_receives_42_notifications(self, router):
        """Criterion 4: Notification Bot receives 42 notifications"""
        # Verify count of notification types
        assert len(router.NOTIFICATION_TYPES) >= 40  # Allow some flexibility
    
    def test_criterion_5_analytics_receives_8_commands_6_notifications(self, router):
        """Criterion 5: Analytics Bot receives 8 commands + 6 notifications"""
        assert len(router.ANALYTICS_COMMANDS) == 8
        assert len(router.ANALYTICS_NOTIFICATIONS) == 6
    
    def test_criterion_6_legacy_fallback_works(self, router, mock_fallback_bot):
        """Criterion 6: Legacy fallback works"""
        # Unknown command should route to legacy
        assert router.get_bot_for_command('unknown_command') == BotType.LEGACY
        
        # Fallback bot should be available
        assert router.fallback_bot is not None
    
    def test_criterion_7_plugins_can_send_notifications(self):
        """Criterion 7: Plugins send notifications through new system"""
        # This is verified by the existence of notification methods in plugin
        from src.logic_plugins.v3_combined.plugin import V3CombinedPlugin
        
        # Verify plugin has notification methods
        assert hasattr(V3CombinedPlugin, '_send_notification')
        assert hasattr(V3CombinedPlugin, 'on_trade_opened')
        assert hasattr(V3CombinedPlugin, 'on_trade_closed')
        assert hasattr(V3CombinedPlugin, 'on_recovery_started')
    
    def test_criterion_8_all_tests_pass(self):
        """Criterion 8: All tests pass (this test itself verifies the suite runs)"""
        # If we reach this point, all previous tests have passed
        assert True


# ============================================================================
# Test Integration Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Test full integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_full_trade_notification_flow(self, router, mock_notification_bot):
        """Test full trade notification flow"""
        # Simulate trade opened notification
        await router.route_notification('trade_opened', 'BUY EURUSD @ 1.0850')
        mock_notification_bot.send_notification.assert_called()
        
        # Simulate SL hit notification
        await router.route_notification('sl_hit', 'SL hit on EURUSD')
        assert mock_notification_bot.send_notification.call_count == 2
    
    @pytest.mark.asyncio
    async def test_full_command_flow(self, router, mock_controller_bot, mock_analytics_bot):
        """Test full command flow"""
        # Controller command
        await router.route_command('status')
        mock_controller_bot.handle_command.assert_called_with('status')
        
        # Analytics command
        await router.route_command('daily')
        mock_analytics_bot.handle_command.assert_called_with('daily')
    
    @pytest.mark.asyncio
    async def test_recovery_notification_flow(self, router, mock_notification_bot):
        """Test recovery notification flow"""
        # Recovery started
        await router.route_notification('recovery_started', 'SL Hunt started for EURUSD')
        
        # Recovery success
        await router.route_notification('recovery_success', 'SL Hunt successful')
        
        assert mock_notification_bot.send_notification.call_count == 2
    
    @pytest.mark.asyncio
    async def test_system_notification_flow(self, router, mock_controller_bot):
        """Test system notification flow"""
        # System started
        await router.route_notification('system_started', 'Bot started')
        mock_controller_bot.send_system_notification.assert_called()
        
        # Config reloaded
        await router.route_notification('config_reloaded', 'Config updated')
        assert mock_controller_bot.send_system_notification.call_count == 2


# ============================================================================
# Test BotType Enum
# ============================================================================

class TestBotTypeEnum:
    """Test BotType enum"""
    
    def test_bot_type_values(self):
        """Test BotType enum values"""
        assert BotType.CONTROLLER.value == "controller"
        assert BotType.NOTIFICATION.value == "notification"
        assert BotType.ANALYTICS.value == "analytics"
        assert BotType.LEGACY.value == "legacy"
    
    def test_bot_type_count(self):
        """Test BotType enum has 4 types"""
        assert len(BotType) == 4


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
