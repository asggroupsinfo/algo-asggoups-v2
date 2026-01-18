"""
Multi-Telegram Manager - Orchestrates multiple Telegram bots

Manages the 3-bot system:
1. Controller Bot: Commands and Admin (72 commands)
2. Notification Bot: Trade Alerts (42 notifications)
3. Analytics Bot: Reports (8 commands + 6 notifications)

Supports graceful degradation to single bot mode if only 1 token provided.

Plan 07: 3-Bot Telegram Migration
- Unified interface for all Telegram operations
- Async routing for commands and notifications
- Legacy bot preserved as fallback

Version: 3.0.0
Date: 2026-01-15
"""

from typing import Dict, Any, Optional
import logging
import asyncio
from datetime import datetime
from queue import Queue

from .base_telegram_bot import BaseTelegramBot
from .controller_bot import ControllerBot
from .notification_bot import NotificationBot
from .analytics_bot import AnalyticsBot
from .message_router import MessageRouter, MessageType

logger = logging.getLogger(__name__)


class MultiTelegramManager:
    """
    Manages multiple Telegram bots for specialized functions:
    1. Controller Bot: Commands and Admin
    2. Notification Bot: Trade Alerts
    3. Analytics Bot: Reports
    
    Features:
    - Intelligent message routing based on content type
    - Graceful degradation to single bot mode
    - Backward compatibility with existing telegram_bot_fixed.py
    - Voice alert integration support
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MultiTelegramManager
        
        Args:
            config: Configuration dict with keys:
                - telegram_token: Main bot token (required)
                - telegram_controller_token: Controller bot token (optional)
                - telegram_notification_token: Notification bot token (optional)
                - telegram_analytics_token: Analytics bot token (optional)
                - telegram_chat_id: Default chat ID
        """
        self.config = config
        
        self.main_token = config.get("telegram_token")
        self.controller_token = config.get("telegram_controller_token")
        self.notification_token = config.get("telegram_notification_token")
        self.analytics_token = config.get("telegram_analytics_token")
        
        self.chat_id = config.get("telegram_chat_id")
        
        self.main_bot: Optional[BaseTelegramBot] = None
        self.controller_bot: Optional[ControllerBot] = None
        self.notification_bot: Optional[NotificationBot] = None
        self.analytics_bot: Optional[AnalyticsBot] = None
        self.router: Optional[MessageRouter] = None
        
        self._legacy_bot = None
        self._single_bot_mode = False
        
        # Multi-bot mode flag (True when using multiple bot tokens)
        self.multi_bot_mode = False
        
        # Message queue for async message routing
        self.message_queue = asyncio.Queue()
        
        self._initialize_bots()
        self._initialize_router()
        
        logger.info("[MultiTelegramManager] Initialization complete")
    
    def _initialize_bots(self):
        """Initialize all bots with fallback logic"""
        if self.main_token:
            self.main_bot = BaseTelegramBot(self.main_token, self.chat_id, "MainBot")
        
        if self.controller_token:
            self.controller_bot = ControllerBot(self.controller_token, self.chat_id)
            logger.info("[MultiTelegramManager] Controller Bot: ACTIVE (dedicated token)")
        elif self.main_token:
            self.controller_bot = ControllerBot(self.main_token, self.chat_id)
            logger.info("[MultiTelegramManager] Controller Bot: FALLBACK (using main token)")
        
        if self.notification_token:
            self.notification_bot = NotificationBot(self.notification_token, self.chat_id)
            logger.info("[MultiTelegramManager] Notification Bot: ACTIVE (dedicated token)")
        elif self.main_token:
            self.notification_bot = NotificationBot(self.main_token, self.chat_id)
            logger.info("[MultiTelegramManager] Notification Bot: FALLBACK (using main token)")
        
        if self.analytics_token:
            self.analytics_bot = AnalyticsBot(self.analytics_token, self.chat_id)
            logger.info("[MultiTelegramManager] Analytics Bot: ACTIVE (dedicated token)")
        elif self.main_token:
            self.analytics_bot = AnalyticsBot(self.main_token, self.chat_id)
            logger.info("[MultiTelegramManager] Analytics Bot: FALLBACK (using main token)")
        
        unique_tokens = set(filter(None, [
            self.main_token,
            self.controller_token,
            self.notification_token,
            self.analytics_token
        ]))
        
        self._single_bot_mode = len(unique_tokens) <= 1
        
        if self._single_bot_mode:
            logger.info("[MultiTelegramManager] Running in SINGLE BOT MODE")
        else:
            logger.info(f"[MultiTelegramManager] Running in MULTI-BOT MODE ({len(unique_tokens)} unique tokens)")
            # Start simple polling for dedicated bots to handle /start
            if self.notification_token and self.notification_bot:
                self.notification_bot.start_simple_polling(
                    "🔔 <b>Notification Bot Active</b>\n\nI am purely for sending trade alerts. I do not accept commands."
                )
            if self.analytics_token and self.analytics_bot:
                self.analytics_bot.start_simple_polling(
                    "📊 <b>Analytics Bot Active</b>\n\nI provide reports and statistics. Use the Controller Bot for commands."
                )
    
    def _initialize_router(self):
        """Initialize message router"""
        self.router = MessageRouter(
            controller_bot=self.controller_bot,
            notification_bot=self.notification_bot,
            analytics_bot=self.analytics_bot,
            fallback_bot=self.main_bot
        )
    
    def _get_target_bot(self, notification_type: str):
        """
        Get the target bot for a notification type.
        
        Args:
            notification_type: Type of notification (e.g., 'trade', 'alert', 'report')
            
        Returns:
            The appropriate bot instance for the notification type
        """
        if notification_type in ['trade', 'alert', 'entry', 'exit', 'sl_hit', 'tp_hit']:
            return self.notification_bot or self.main_bot
        elif notification_type in ['report', 'summary', 'analytics', 'statistics']:
            return self.analytics_bot or self.main_bot
        elif notification_type in ['command', 'admin', 'control', 'status']:
            return self.controller_bot or self.main_bot
        else:
            return self.main_bot
    
    def register_command_handlers(self, trading_engine):
        """
        Register command handlers with the trading engine.
        
        Args:
            trading_engine: The trading engine instance to register handlers with
        """
        if self.controller_bot and hasattr(self.controller_bot, 'register_handlers'):
            self.controller_bot.register_handlers(trading_engine)
        
        if self._legacy_bot and hasattr(self._legacy_bot, 'register_command_handlers'):
            self._legacy_bot.register_command_handlers(trading_engine)
        
        logger.info("[MultiTelegramManager] Command handlers registered")
    
    def set_legacy_bot(self, legacy_bot):
        """
        Set legacy telegram_bot_fixed.py instance for command delegation
        
        Args:
            legacy_bot: Instance of TelegramBot from telegram_bot_fixed.py
        """
        self._legacy_bot = legacy_bot
        
        if self.controller_bot:
            self.controller_bot.set_dependencies(legacy_bot=legacy_bot)
        
        logger.info("[MultiTelegramManager] Legacy bot connected for backward compatibility")
    
    def set_voice_alert_system(self, voice_system):
        """
        Set voice alert system for audio notifications
        
        Args:
            voice_system: VoiceAlertSystem instance
        """
        if self.notification_bot:
            self.notification_bot.set_voice_alert_system(voice_system)

    def route_message(self, message_type: str, content: str, parse_mode: str = "HTML"):
        """
        Routes message to appropriate bot based on type.
        
        Args:
            message_type: 'command', 'alert', 'report', 'broadcast'
            content: Message text
            parse_mode: Telegram parse mode (HTML, Markdown)
        
        Returns:
            Message ID if successful, None otherwise
        """
        if not content:
            return None
        
        return self.router.route_message(content, message_type=message_type, parse_mode=parse_mode)
    
    def send_alert(self, message: str, **kwargs) -> Optional[int]:
        """
        Send trade alert via Notification Bot
        
        Args:
            message: Alert message
            **kwargs: Additional arguments
        
        Returns:
            Message ID if successful
        """
        return self.router.send_alert(message, **kwargs)
    
    def send_report(self, message: str, **kwargs) -> Optional[int]:
        """
        Send report via Analytics Bot
        
        Args:
            message: Report message
            **kwargs: Additional arguments
        
        Returns:
            Message ID if successful
        """
        return self.router.send_report(message, **kwargs)
    
    def send_admin_message(self, message: str, **kwargs) -> Optional[int]:
        """
        Send admin/system message via Controller Bot
        
        Args:
            message: Admin message
            **kwargs: Additional arguments
        
        Returns:
            Message ID if successful
        """
        return self.router.send_command_response(message, **kwargs)
    
    def send_broadcast(self, message: str, **kwargs) -> Optional[int]:
        """
        Broadcast message to all bots
        
        Args:
            message: Broadcast message
            **kwargs: Additional arguments
        
        Returns:
            Message ID if successful
        """
        return self.router.send_broadcast(message, **kwargs)
    
    def send_entry_alert(self, trade_data: Dict) -> Optional[int]:
        """
        Send entry notification for new trade
        
        Args:
            trade_data: Dict with trade details
        
        Returns:
            Message ID if successful
        """
        if self.notification_bot:
            return self.notification_bot.send_entry_alert(trade_data)
        return None
    
    def send_exit_alert(self, trade_data: Dict) -> Optional[int]:
        """
        Send exit notification for closed trade
        
        Args:
            trade_data: Dict with trade details
        
        Returns:
            Message ID if successful
        """
        if self.notification_bot:
            return self.notification_bot.send_exit_alert(trade_data)
        return None
    
    def send_profit_booking_alert(self, booking_data: Dict) -> Optional[int]:
        """
        Send partial profit booking notification
        
        Args:
            booking_data: Dict with booking details
        
        Returns:
            Message ID if successful
        """
        if self.notification_bot:
            return self.notification_bot.send_profit_booking_alert(booking_data)
        return None
    
    def send_error_alert(self, error_data: Dict) -> Optional[int]:
        """
        Send error notification
        
        Args:
            error_data: Dict with error details
        
        Returns:
            Message ID if successful
        """
        if self.notification_bot:
            return self.notification_bot.send_error_alert(error_data)
        return None
    
    def send_performance_report(self, report_data: Dict) -> Optional[int]:
        """
        Send performance report
        
        Args:
            report_data: Dict with performance metrics
        
        Returns:
            Message ID if successful
        """
        if self.analytics_bot:
            return self.analytics_bot.send_performance_report(report_data)
        return None
    
    def send_statistics_summary(self, stats_data: Dict) -> Optional[int]:
        """
        Send statistics summary
        
        Args:
            stats_data: Dict with statistics
        
        Returns:
            Message ID if successful
        """
        if self.analytics_bot:
            return self.analytics_bot.send_statistics_summary(stats_data)
        return None
    
    def send_status_response(self, status_data: Dict) -> Optional[int]:
        """
        Send status response via Controller Bot
        
        Args:
            status_data: Dict with status information
        
        Returns:
            Message ID if successful
        """
        if self.controller_bot:
            return self.controller_bot.send_status_response(status_data)
        return None
    
    # ==================== Plan 07: Async Routing Methods ====================
    
    async def initialize(self):
        """Initialize all bots (async)"""
        logger.info("Initializing 3-bot Telegram system...")
        
        if self.controller_bot and hasattr(self.controller_bot, 'initialize'):
            await self.controller_bot.initialize()
        if self.notification_bot and hasattr(self.notification_bot, 'initialize'):
            await self.notification_bot.initialize()
        if self.analytics_bot and hasattr(self.analytics_bot, 'initialize'):
            await self.analytics_bot.initialize()
        
        if self._legacy_bot and hasattr(self._legacy_bot, 'initialize'):
            await self._legacy_bot.initialize()
        
        logger.info("3-bot Telegram system initialized")
    
    async def shutdown(self):
        """Shutdown all bots (async)"""
        logger.info("Shutting down 3-bot Telegram system...")
        
        if self.controller_bot and hasattr(self.controller_bot, 'shutdown'):
            await self.controller_bot.shutdown()
        if self.notification_bot and hasattr(self.notification_bot, 'shutdown'):
            await self.notification_bot.shutdown()
        if self.analytics_bot and hasattr(self.analytics_bot, 'shutdown'):
            await self.analytics_bot.shutdown()
        
        if self._legacy_bot and hasattr(self._legacy_bot, 'shutdown'):
            await self._legacy_bot.shutdown()
        
        logger.info("3-bot Telegram system shutdown complete")
    
    async def send_notification_async(self, notification_type: str, message: str, **kwargs):
        """
        Send notification through router (async)
        
        Args:
            notification_type: Type of notification (e.g., 'trade_opened', 'sl_hit')
            message: Notification message
            **kwargs: Additional arguments
        """
        if self.router:
            return await self.router.route_notification(notification_type, message, **kwargs)
        return None
    
    async def handle_command_async(self, command: str, *args, **kwargs):
        """
        Handle command through router (async)
        
        Args:
            command: Command name
            *args: Command arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Command result
        """
        if self.router:
            return await self.router.route_command(command, *args, **kwargs)
        return None
    
    async def send_trade_notification(self, trade_data: Dict[str, Any]):
        """
        Send trade notification (async)
        
        Args:
            trade_data: Dict with trade details including 'type' key
        """
        notification_type = trade_data.get('type', 'trade_opened')
        message = self._format_trade_message(trade_data)
        await self.send_notification_async(notification_type, message, trade_data=trade_data)
    
    async def send_system_alert_async(self, alert_type: str, message: str):
        """
        Send system alert (async)
        
        Args:
            alert_type: Type of system alert
            message: Alert message
        """
        await self.send_notification_async(alert_type, message)
    
    async def send_daily_summary_async(self, summary_data: Dict[str, Any]):
        """
        Send daily summary (async)
        
        Args:
            summary_data: Dict with summary data
        """
        message = self._format_summary_message(summary_data)
        await self.send_notification_async('daily_summary', message, summary_data=summary_data)
    
    def _format_trade_message(self, trade_data: Dict[str, Any]) -> str:
        """Format trade notification message"""
        symbol = trade_data.get('symbol', 'UNKNOWN')
        direction = trade_data.get('direction', 'UNKNOWN')
        price = trade_data.get('price', 0)
        order_type = trade_data.get('order_type', '')
        profit = trade_data.get('profit', None)
        
        if profit is not None:
            return f"Trade: {direction} {symbol} @ {price} | P/L: ${profit:.2f}"
        elif order_type:
            return f"Trade: {order_type} {direction} {symbol} @ {price}"
        else:
            return f"Trade: {direction} {symbol} @ {price}"
    
    def _format_summary_message(self, summary_data: Dict[str, Any]) -> str:
        """Format summary message"""
        profit = summary_data.get('profit', 0)
        trades = summary_data.get('trades', 0)
        winrate = summary_data.get('winrate', 0)
        
        return f"Daily Summary: ${profit:.2f} | {trades} trades | {winrate:.1f}% winrate"
    
    # ==================== End Plan 07 Async Routing Methods ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get manager statistics
        
        Returns:
            Dict with stats from all bots and router
        """
        stats = {
            "mode": "single_bot" if self._single_bot_mode else "multi_bot",
            "bots": {
                "main": self.main_bot.get_stats() if self.main_bot else None,
                "controller": self.controller_bot.get_stats() if self.controller_bot else None,
                "notification": self.notification_bot.get_stats() if self.notification_bot else None,
                "analytics": self.analytics_bot.get_stats() if self.analytics_bot else None
            },
            "routing": self.router.get_routing_stats() if self.router else None,
            "legacy_bot_connected": self._legacy_bot is not None
        }
        
        return stats
    
    @property
    def is_single_bot_mode(self) -> bool:
        """Check if running in single bot mode"""
        return self._single_bot_mode
    
    @property
    def active_bots_count(self) -> int:
        """Get count of active bots"""
        count = 0
        if self.controller_bot and self.controller_bot.is_active:
            count += 1
        if self.notification_bot and self.notification_bot.is_active:
            count += 1
        if self.analytics_bot and self.analytics_bot.is_active:
            count += 1
        return count
