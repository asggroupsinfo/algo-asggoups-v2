"""
Message Router - Intelligent routing logic for multi-bot system

Routes messages to the appropriate bot based on message type and content.
Supports graceful degradation to single bot mode.

Plan 07: 3-Bot Telegram Migration
- Routes 72 commands to Controller Bot
- Routes 42 notifications to Notification Bot
- Routes 8 commands + 6 notifications to Analytics Bot
- Preserves legacy bot as fallback

Version: 2.0.0
Date: 2026-01-15
"""

import logging
import re
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from enum import Enum
from datetime import datetime

if TYPE_CHECKING:
    from .controller_bot import ControllerBot
    from .notification_bot import NotificationBot
    from .analytics_bot import AnalyticsBot

logger = logging.getLogger(__name__)


class BotType(Enum):
    """Bot types in 3-bot system"""
    CONTROLLER = "controller"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"
    LEGACY = "legacy"  # Fallback


class MessageType(Enum):
    """Message type classification"""
    COMMAND = "command"
    ALERT = "alert"
    REPORT = "report"
    BROADCAST = "broadcast"
    ERROR = "error"
    UNKNOWN = "unknown"


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class MessageRouter:
    """
    Intelligent message router for multi-bot system.
    
    Routes messages to appropriate bots based on:
    - Message type (command, alert, report, broadcast)
    - Message content analysis
    - Priority level
    - Bot availability
    
    Supports graceful degradation:
    - If specialized bot unavailable, routes to main bot
    - If all bots unavailable, logs error
    
    Plan 07: 3-Bot Telegram Migration
    - Controller Bot: 72 commands (system control)
    - Notification Bot: 42 notifications (trade alerts)
    - Analytics Bot: 8 commands + 6 notifications (reports)
    """
    
    # ==================== Plan 07: Command Routing Maps ====================
    
    # Controller Bot Commands (72 commands)
    CONTROLLER_COMMANDS = {
        # Category 1: Trading Control (7)
        'start', 'stop', 'pause', 'resume', 'status', 'restart', 'shutdown',
        # Category 3: Strategy Control (8)
        'logic1_on', 'logic1_off', 'logic2_on', 'logic2_off', 'logic3_on', 'logic3_off', 'strategy', 'symbols',
        # Category 4: Re-entry System (14)
        'reentry_on', 'reentry_off', 'reentry_status', 'chains', 'chain_info', 'sl_hunt_on', 'sl_hunt_off',
        'tp_cont_on', 'tp_cont_off', 'exit_cont_on', 'exit_cont_off', 'recovery_status', 'recovery_windows', 'autonomous_status',
        # Category 5: Trend Management (5)
        'trends', 'set_trend', 'auto_trend', 'trend_check', 'trend_history',
        # Category 6: Risk & Lot Management (11)
        'risk', 'set_lot', 'daily_limit', 'set_daily_limit', 'lifetime_limit', 'reset_daily', 'tier',
        'balance', 'margin', 'equity', 'risk_stats',
        # Category 7: SL System Control (8)
        'sl_system', 'sl1_on', 'sl1_off', 'sl2_on', 'sl2_off', 'sl_pips', 'set_sl_pips', 'sl_reduction',
        # Category 8: Dual Orders (2)
        'dual_on', 'dual_off',
        # Category 9: Profit Booking (16)
        'profit_on', 'profit_off', 'profit_status', 'profit_chains', 'profit_chain_info', 'profit_target',
        'set_profit_target', 'profit_levels', 'profit_multipliers', 'profit_strict_on', 'profit_strict_off',
        'profit_sl_hunt_on', 'profit_sl_hunt_off', 'profit_stats', 'profit_history', 'book_profit',
        # Category 10: Timeframe Logic (4)
        'timeframe', 'tf_multipliers', 'set_tf_multiplier', 'logic_alignment',
        # Category 11: Fine-Tune Settings (4)
        'finetune', 'set_recovery_window', 'set_profit_protection', 'set_concurrent_limit',
        # Category 12: Session Management (5)
        'sessions', 'session_on', 'session_off', 'overlap_on', 'overlap_off',
        # Category 13: Diagnostics & Health (15)
        'health', 'mt5_status', 'mt5_reconnect', 'positions', 'orders', 'close_all', 'close', 'panic_close',
        'logs', 'errors', 'config', 'reload_config', 'version', 'help', 'debug'
    }
    
    # Analytics Bot Commands (8 commands)
    ANALYTICS_COMMANDS = {
        'daily', 'weekly', 'monthly', 'pnl', 'winrate', 'performance', 'stats', 'history'
    }
    
    # ==================== Plan 07: Notification Routing Maps ====================
    
    # Notification Bot Notifications (42 notifications)
    NOTIFICATION_TYPES = {
        # Entry notifications (8)
        'trade_opened', 'order_a_opened', 'order_b_opened', 'signal_received',
        'dual_order_created', 'position_opened', 'entry_executed', 'pending_order_placed',
        # Exit notifications (6)
        'trade_closed', 'sl_hit', 'tp_hit', 'manual_close', 'reversal_close', 'position_closed',
        # Re-entry notifications (8)
        'recovery_started', 'recovery_success', 'recovery_failed', 'recovery_timeout',
        'sl_hunt_started', 'sl_hunt_success', 'tp_continuation_started', 'exit_continuation_started',
        # Profit booking notifications (6)
        'profit_booked', 'chain_advanced', 'chain_completed', 'chain_sl_hit',
        'profit_target_hit', 'pyramid_level_up',
        # Risk notifications (6)
        'daily_limit_warning', 'daily_limit_reached', 'lot_adjusted', 'tier_changed',
        'lifetime_limit_warning', 'margin_warning',
        # Trend notifications (4)
        'trend_changed', 'trend_aligned', 'trend_conflict', 'trend_pulse_update',
        # Shield notifications (4)
        'reverse_shield_activated', 'reverse_shield_deactivated', 'shield_a_hit', 'shield_b_hit'
    }
    
    # Controller Bot System Notifications (8 notifications)
    SYSTEM_NOTIFICATIONS = {
        'system_started', 'system_stopped', 'config_reloaded', 'error_alert',
        'mt5_connected', 'mt5_disconnected', 'plugin_enabled', 'plugin_disabled'
    }
    
    # Analytics Bot Notifications (6 notifications)
    ANALYTICS_NOTIFICATIONS = {
        'daily_summary', 'weekly_summary', 'monthly_summary',
        'performance_alert', 'drawdown_alert', 'profit_milestone'
    }
    
    # ==================== End Plan 07 Routing Maps ====================
    
    ALERT_KEYWORDS = [
        'entry', 'exit', 'trade', 'position', 'order',
        'profit', 'loss', 'sl', 'tp', 'stop', 'take',
        'booking', 'closed', 'opened', 'modified',
        'error', 'warning', 'alert'
    ]
    
    REPORT_KEYWORDS = [
        'report', 'summary', 'statistics', 'stats',
        'performance', 'analysis', 'history', 'trend',
        'weekly', 'daily', 'monthly', 'plugin'
    ]
    
    COMMAND_PATTERNS = [
        r'^/',
        r'command',
        r'status',
        r'config',
        r'settings'
    ]
    
    def __init__(
        self,
        controller_bot: Optional['ControllerBot'] = None,
        notification_bot: Optional['NotificationBot'] = None,
        analytics_bot: Optional['AnalyticsBot'] = None,
        fallback_bot: Optional[Any] = None
    ):
        """
        Initialize message router
        
        Args:
            controller_bot: Bot for commands
            notification_bot: Bot for alerts
            analytics_bot: Bot for reports
            fallback_bot: Fallback bot if specialized bots unavailable
        """
        self.controller_bot = controller_bot
        self.notification_bot = notification_bot
        self.analytics_bot = analytics_bot
        self.fallback_bot = fallback_bot
        
        self._routing_stats: Dict[str, int] = {
            "controller": 0,
            "notification": 0,
            "analytics": 0,
            "fallback": 0,
            "failed": 0
        }
        
        self._single_bot_mode = self._check_single_bot_mode()
        
        if self._single_bot_mode:
            logger.info("[MessageRouter] Running in SINGLE BOT MODE")
        else:
            logger.info("[MessageRouter] Running in MULTI-BOT MODE")
    
    def _check_single_bot_mode(self) -> bool:
        """Check if running in single bot mode"""
        active_bots = 0
        
        if self.controller_bot and self.controller_bot.is_active:
            active_bots += 1
        if self.notification_bot and self.notification_bot.is_active:
            active_bots += 1
        if self.analytics_bot and self.analytics_bot.is_active:
            active_bots += 1
        
        return active_bots <= 1
    
    # ==================== Plan 07: Bot Type Routing Methods ====================
    
    def get_bot_for_command(self, command: str) -> BotType:
        """
        Determine which bot should handle a command
        
        Args:
            command: Command name (with or without /)
            
        Returns:
            BotType enum indicating target bot
        """
        command = command.lower().strip('/')
        
        if command in self.CONTROLLER_COMMANDS:
            return BotType.CONTROLLER
        elif command in self.ANALYTICS_COMMANDS:
            return BotType.ANALYTICS
        else:
            logger.warning(f"Unknown command: {command}, using legacy")
            return BotType.LEGACY
    
    def get_bot_for_notification(self, notification_type: str) -> BotType:
        """
        Determine which bot should handle a notification
        
        Args:
            notification_type: Type of notification
            
        Returns:
            BotType enum indicating target bot
        """
        notification_type = notification_type.lower()
        
        if notification_type in self.NOTIFICATION_TYPES:
            return BotType.NOTIFICATION
        elif notification_type in self.SYSTEM_NOTIFICATIONS:
            return BotType.CONTROLLER
        elif notification_type in self.ANALYTICS_NOTIFICATIONS:
            return BotType.ANALYTICS
        else:
            logger.warning(f"Unknown notification type: {notification_type}, using notification bot")
            return BotType.NOTIFICATION
    
    async def route_command(self, command: str, *args, **kwargs):
        """
        Route a command to the appropriate bot (async)
        
        Args:
            command: Command name
            *args: Command arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Command result
        """
        bot_type = self.get_bot_for_command(command)
        self._routing_stats['commands_routed'] = self._routing_stats.get('commands_routed', 0) + 1
        
        try:
            if bot_type == BotType.CONTROLLER:
                if self.controller_bot and hasattr(self.controller_bot, 'handle_command'):
                    return await self.controller_bot.handle_command(command, *args, **kwargs)
            elif bot_type == BotType.ANALYTICS:
                if self.analytics_bot and hasattr(self.analytics_bot, 'handle_command'):
                    return await self.analytics_bot.handle_command(command, *args, **kwargs)
            elif bot_type == BotType.LEGACY and self.fallback_bot:
                self._routing_stats['fallback'] += 1
                if hasattr(self.fallback_bot, 'handle_command'):
                    return await self.fallback_bot.handle_command(command, *args, **kwargs)
        except Exception as e:
            logger.error(f"Command routing failed: {e}")
            if self.fallback_bot:
                self._routing_stats['fallback'] += 1
                if hasattr(self.fallback_bot, 'handle_command'):
                    return await self.fallback_bot.handle_command(command, *args, **kwargs)
            raise
    
    async def route_notification(self, notification_type: str, message: str, **kwargs):
        """
        Route a notification to the appropriate bot (async)
        
        Args:
            notification_type: Type of notification
            message: Notification message
            **kwargs: Additional keyword arguments
            
        Returns:
            Message ID if successful
        """
        bot_type = self.get_bot_for_notification(notification_type)
        self._routing_stats['notifications_routed'] = self._routing_stats.get('notifications_routed', 0) + 1
        
        try:
            if bot_type == BotType.NOTIFICATION:
                if self.notification_bot:
                    if hasattr(self.notification_bot, 'send_notification'):
                        return await self.notification_bot.send_notification(notification_type, message, **kwargs)
                    else:
                        return self.notification_bot.send_message(message)
            elif bot_type == BotType.CONTROLLER:
                if self.controller_bot:
                    if hasattr(self.controller_bot, 'send_system_notification'):
                        return await self.controller_bot.send_system_notification(notification_type, message, **kwargs)
                    else:
                        return self.controller_bot.send_message(message)
            elif bot_type == BotType.ANALYTICS:
                if self.analytics_bot:
                    if hasattr(self.analytics_bot, 'send_analytics_notification'):
                        return await self.analytics_bot.send_analytics_notification(notification_type, message, **kwargs)
                    else:
                        return self.analytics_bot.send_message(message)
        except Exception as e:
            logger.error(f"Notification routing failed: {e}")
            if self.fallback_bot:
                self._routing_stats['fallback'] += 1
                return self.fallback_bot.send_message(message)
            raise
    
    # ==================== End Plan 07 Bot Type Routing Methods ====================
    
    def classify_message(self, content: str, explicit_type: str = None) -> MessageType:
        """
        Classify message type based on content
        
        Args:
            content: Message content
            explicit_type: Explicitly specified type (overrides detection)
        
        Returns:
            MessageType enum value
        """
        if explicit_type:
            try:
                return MessageType(explicit_type.lower())
            except ValueError:
                pass
        
        content_lower = content.lower()
        
        for pattern in self.COMMAND_PATTERNS:
            if re.search(pattern, content_lower):
                return MessageType.COMMAND
        
        alert_score = sum(1 for kw in self.ALERT_KEYWORDS if kw in content_lower)
        report_score = sum(1 for kw in self.REPORT_KEYWORDS if kw in content_lower)
        
        if alert_score > report_score and alert_score > 0:
            return MessageType.ALERT
        elif report_score > alert_score and report_score > 0:
            return MessageType.REPORT
        
        if 'error' in content_lower or 'warning' in content_lower:
            return MessageType.ERROR
        
        return MessageType.UNKNOWN
    
    def determine_priority(self, content: str, message_type: MessageType) -> MessagePriority:
        """
        Determine message priority
        
        Args:
            content: Message content
            message_type: Classified message type
        
        Returns:
            MessagePriority enum value
        """
        content_lower = content.lower()
        
        critical_keywords = ['emergency', 'critical', 'urgent', 'margin call', 'liquidation']
        if any(kw in content_lower for kw in critical_keywords):
            return MessagePriority.CRITICAL
        
        high_keywords = ['error', 'failed', 'loss', 'stop loss', 'sl hit']
        if any(kw in content_lower for kw in high_keywords):
            return MessagePriority.HIGH
        
        if message_type == MessageType.ALERT:
            return MessagePriority.HIGH
        elif message_type == MessageType.COMMAND:
            return MessagePriority.NORMAL
        elif message_type == MessageType.REPORT:
            return MessagePriority.LOW
        
        return MessagePriority.NORMAL
    
    def route_message(
        self,
        content: str,
        message_type: str = None,
        parse_mode: str = "HTML",
        **kwargs
    ) -> Optional[int]:
        """
        Route message to appropriate bot
        
        Args:
            content: Message content
            message_type: Explicit message type (command, alert, report, broadcast)
            parse_mode: Telegram parse mode
            **kwargs: Additional arguments for send_message
        
        Returns:
            Message ID if successful, None otherwise
        """
        classified_type = self.classify_message(content, message_type)
        priority = self.determine_priority(content, classified_type)
        
        logger.debug(f"[MessageRouter] Routing {classified_type.value} message (priority: {priority.name})")
        
        if self._single_bot_mode:
            return self._route_single_bot(content, parse_mode, **kwargs)
        
        if classified_type == MessageType.COMMAND:
            return self._route_to_controller(content, parse_mode, **kwargs)
        elif classified_type == MessageType.ALERT or classified_type == MessageType.ERROR:
            return self._route_to_notification(content, parse_mode, **kwargs)
        elif classified_type == MessageType.REPORT:
            return self._route_to_analytics(content, parse_mode, **kwargs)
        elif classified_type == MessageType.BROADCAST:
            return self._broadcast_to_all(content, parse_mode, **kwargs)
        else:
            return self._route_to_fallback(content, parse_mode, **kwargs)
    
    def _route_single_bot(self, content: str, parse_mode: str, **kwargs) -> Optional[int]:
        """Route to single available bot"""
        bot = self.fallback_bot
        
        if self.controller_bot and self.controller_bot.is_active:
            bot = self.controller_bot
        elif self.notification_bot and self.notification_bot.is_active:
            bot = self.notification_bot
        elif self.analytics_bot and self.analytics_bot.is_active:
            bot = self.analytics_bot
        
        if bot:
            result = bot.send_message(content, parse_mode=parse_mode, **kwargs)
            if result:
                self._routing_stats["fallback"] += 1
            return result
        
        logger.error("[MessageRouter] No bot available for routing")
        self._routing_stats["failed"] += 1
        return None
    
    def _route_to_controller(self, content: str, parse_mode: str, **kwargs) -> Optional[int]:
        """Route to controller bot"""
        if self.controller_bot and self.controller_bot.is_active:
            result = self.controller_bot.send_message(content, parse_mode=parse_mode, **kwargs)
            if result:
                self._routing_stats["controller"] += 1
                return result
        
        return self._route_to_fallback(content, parse_mode, **kwargs)
    
    def _route_to_notification(self, content: str, parse_mode: str, **kwargs) -> Optional[int]:
        """Route to notification bot"""
        if self.notification_bot and self.notification_bot.is_active:
            result = self.notification_bot.send_message(content, parse_mode=parse_mode, **kwargs)
            if result:
                self._routing_stats["notification"] += 1
                return result
        
        return self._route_to_fallback(content, parse_mode, **kwargs)
    
    def _route_to_analytics(self, content: str, parse_mode: str, **kwargs) -> Optional[int]:
        """Route to analytics bot"""
        if self.analytics_bot and self.analytics_bot.is_active:
            result = self.analytics_bot.send_message(content, parse_mode=parse_mode, **kwargs)
            if result:
                self._routing_stats["analytics"] += 1
                return result
        
        return self._route_to_fallback(content, parse_mode, **kwargs)
    
    def _route_to_fallback(self, content: str, parse_mode: str, **kwargs) -> Optional[int]:
        """Route to fallback bot"""
        if self.fallback_bot:
            if hasattr(self.fallback_bot, 'send_message'):
                result = self.fallback_bot.send_message(content, parse_mode=parse_mode, **kwargs)
                if result:
                    self._routing_stats["fallback"] += 1
                    return result
        
        logger.error("[MessageRouter] No fallback bot available")
        self._routing_stats["failed"] += 1
        return None
    
    def _broadcast_to_all(self, content: str, parse_mode: str, **kwargs) -> Optional[int]:
        """Broadcast message to all active bots"""
        results = []
        
        if self.controller_bot and self.controller_bot.is_active:
            result = self.controller_bot.send_message(content, parse_mode=parse_mode, **kwargs)
            if result:
                results.append(result)
                self._routing_stats["controller"] += 1
        
        if self.notification_bot and self.notification_bot.is_active:
            result = self.notification_bot.send_message(content, parse_mode=parse_mode, **kwargs)
            if result:
                results.append(result)
                self._routing_stats["notification"] += 1
        
        if self.analytics_bot and self.analytics_bot.is_active:
            result = self.analytics_bot.send_message(content, parse_mode=parse_mode, **kwargs)
            if result:
                results.append(result)
                self._routing_stats["analytics"] += 1
        
        return results[0] if results else None
    
    def send_alert(self, message: str, **kwargs) -> Optional[int]:
        """Convenience method to send alert"""
        return self.route_message(message, message_type="alert", **kwargs)
    
    def send_report(self, message: str, **kwargs) -> Optional[int]:
        """Convenience method to send report"""
        return self.route_message(message, message_type="report", **kwargs)
    
    def send_command_response(self, message: str, **kwargs) -> Optional[int]:
        """Convenience method to send command response"""
        return self.route_message(message, message_type="command", **kwargs)
    
    def send_broadcast(self, message: str, **kwargs) -> Optional[int]:
        """Convenience method to broadcast to all bots"""
        return self.route_message(message, message_type="broadcast", **kwargs)
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        total = sum(self._routing_stats.values())
        
        return {
            "mode": "single_bot" if self._single_bot_mode else "multi_bot",
            "total_messages": total,
            "by_destination": self._routing_stats.copy(),
            "success_rate": ((total - self._routing_stats["failed"]) / total * 100) if total > 0 else 100,
            "bots_active": {
                "controller": self.controller_bot.is_active if self.controller_bot else False,
                "notification": self.notification_bot.is_active if self.notification_bot else False,
                "analytics": self.analytics_bot.is_active if self.analytics_bot else False,
                "fallback": self.fallback_bot is not None
            }
        }
    
    def reset_stats(self):
        """Reset routing statistics"""
        for key in self._routing_stats:
            self._routing_stats[key] = 0
