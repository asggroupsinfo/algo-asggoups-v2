"""
Unified Notification Router - Central notification routing system

This module provides a single entry point for all notifications,
routing them to the appropriate bot based on notification type.

Features:
- Single entry point for all notifications
- Type-based routing to correct bot
- Fallback mode for single-bot configuration
- Priority system (CRITICAL/HIGH/MEDIUM/LOW)
- Mute/unmute support for specific notification types
- Notification formatting for all 50+ types

Version: 1.0.0
Date: 2026-01-15
"""

import logging
from typing import Dict, Any, Optional, Set, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Priority levels for notifications"""
    CRITICAL = "CRITICAL"   # Must be delivered immediately
    HIGH = "HIGH"           # Important, deliver soon
    MEDIUM = "MEDIUM"       # Normal priority
    LOW = "LOW"             # Can be delayed or batched


class NotificationBot(Enum):
    """Target bot for notification"""
    CONTROLLER = "controller"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"


@dataclass
class NotificationConfig:
    """Configuration for a notification type"""
    bot: NotificationBot
    priority: NotificationPriority
    formatter: Optional[str] = None  # Name of formatter method


class UnifiedNotificationRouter:
    """
    Central router for all notifications.
    
    Routes notifications to appropriate bot based on type,
    with fallback to single bot if 3-bot not configured.
    """
    
    # Notification type configurations
    NOTIFICATION_TYPES: Dict[str, NotificationConfig] = {
        # Trading notifications -> NotificationBot
        "trade_entry": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.HIGH),
        "trade_exit": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.HIGH),
        "tp_hit": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.HIGH),
        "sl_hit": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.HIGH),
        "profit_booking": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM),
        "partial_close": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM),
        "sl_modified": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.LOW),
        "tp_modified": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.LOW),
        
        # Autonomous system -> NotificationBot
        "tp_continuation": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM),
        "sl_hunt_activated": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.HIGH),
        "sl_hunt_monitoring": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM),
        "recovery_success": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM),
        "recovery_failed": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.HIGH),
        "chain_resume": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM),
        "chain_complete": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM),
        "profit_order_sl_hunt": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.HIGH),
        
        # Re-entry system -> NotificationBot
        "reentry_triggered": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM),
        "reentry_config_changed": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.LOW),
        "cooldown_active": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.LOW),
        "recovery_window_timeout": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM),
        
        # Risk alerts -> NotificationBot (HIGH priority)
        "daily_limit_warning": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.HIGH),
        "daily_limit_hit": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.CRITICAL),
        "lifetime_limit_hit": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.CRITICAL),
        "profit_protection_blocked": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM),
        "daily_recovery_limit": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.HIGH),
        
        # Trend & signal -> NotificationBot
        "trend_updated": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.LOW),
        "trend_locked": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.LOW),
        "signal_received": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM),
        "signal_filtered": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.LOW),
        "signal_duplicate": NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.LOW),
        
        # Analytics -> AnalyticsBot
        "performance_report": NotificationConfig(NotificationBot.ANALYTICS, NotificationPriority.LOW),
        "daily_summary": NotificationConfig(NotificationBot.ANALYTICS, NotificationPriority.LOW),
        "weekly_summary": NotificationConfig(NotificationBot.ANALYTICS, NotificationPriority.LOW),
        "monthly_summary": NotificationConfig(NotificationBot.ANALYTICS, NotificationPriority.LOW),
        "trade_history": NotificationConfig(NotificationBot.ANALYTICS, NotificationPriority.LOW),
        "plugin_performance": NotificationConfig(NotificationBot.ANALYTICS, NotificationPriority.LOW),
        "trend_analysis": NotificationConfig(NotificationBot.ANALYTICS, NotificationPriority.LOW),
        "statistics_summary": NotificationConfig(NotificationBot.ANALYTICS, NotificationPriority.LOW),
        
        # System -> ControllerBot
        "bot_startup": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.MEDIUM),
        "bot_shutdown": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.MEDIUM),
        "config_changed": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.LOW),
        "plugin_enabled": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.MEDIUM),
        "plugin_disabled": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.MEDIUM),
        "error_alert": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.HIGH),
        "mt5_connected": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.MEDIUM),
        "mt5_disconnected": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.CRITICAL),
        "health_check": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.LOW),
        
        # Config changes -> ControllerBot
        "sl_system_changed": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.LOW),
        "risk_tier_changed": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.MEDIUM),
        "logic_enabled": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.MEDIUM),
        "logic_disabled": NotificationConfig(NotificationBot.CONTROLLER, NotificationPriority.MEDIUM),
    }
    
    def __init__(
        self,
        controller_bot=None,
        notification_bot=None,
        analytics_bot=None,
        fallback_bot=None,
        chat_id: int = None
    ):
        """
        Initialize UnifiedNotificationRouter.
        
        Args:
            controller_bot: ControllerBot instance
            notification_bot: NotificationBot instance
            analytics_bot: AnalyticsBot instance
            fallback_bot: Fallback bot for single-bot mode
            chat_id: Default chat ID for notifications
        """
        self._bots = {
            NotificationBot.CONTROLLER: controller_bot,
            NotificationBot.NOTIFICATION: notification_bot,
            NotificationBot.ANALYTICS: analytics_bot,
        }
        self._fallback_bot = fallback_bot
        self._chat_id = chat_id
        
        self._muted_types: Set[str] = set()
        self._muted_priorities: Set[NotificationPriority] = set()
        
        # Determine mode
        has_all_bots = all(self._bots.values())
        self._mode = "MULTI_BOT" if has_all_bots else "SINGLE_BOT"
        
        # Statistics
        self._stats = {
            "total_sent": 0,
            "total_muted": 0,
            "by_type": {},
            "by_bot": {b.value: 0 for b in NotificationBot},
        }
        
        logger.info(f"[UnifiedNotificationRouter] Initialized in {self._mode} mode")
    
    def set_bots(
        self,
        controller_bot=None,
        notification_bot=None,
        analytics_bot=None,
        fallback_bot=None
    ):
        """Update bot instances"""
        if controller_bot:
            self._bots[NotificationBot.CONTROLLER] = controller_bot
        if notification_bot:
            self._bots[NotificationBot.NOTIFICATION] = notification_bot
        if analytics_bot:
            self._bots[NotificationBot.ANALYTICS] = analytics_bot
        if fallback_bot:
            self._fallback_bot = fallback_bot
        
        # Re-determine mode
        has_all_bots = all(self._bots.values())
        self._mode = "MULTI_BOT" if has_all_bots else "SINGLE_BOT"
        
        logger.info(f"[UnifiedNotificationRouter] Bots updated, mode: {self._mode}")
    
    def set_chat_id(self, chat_id: int):
        """Set default chat ID"""
        self._chat_id = chat_id
    
    def send(
        self,
        notification_type: str,
        data: Dict[str, Any],
        chat_id: int = None
    ) -> bool:
        """
        Send a notification.
        
        Args:
            notification_type: Type of notification
            data: Notification data
            chat_id: Optional chat ID override
        
        Returns:
            True if notification was sent successfully
        """
        # Check if muted
        if notification_type in self._muted_types:
            self._stats["total_muted"] += 1
            logger.debug(f"[UnifiedNotificationRouter] Muted: {notification_type}")
            return False
        
        # Get configuration
        config = self.NOTIFICATION_TYPES.get(
            notification_type,
            NotificationConfig(NotificationBot.NOTIFICATION, NotificationPriority.MEDIUM)
        )
        
        # Check priority muting
        if config.priority in self._muted_priorities:
            self._stats["total_muted"] += 1
            logger.debug(f"[UnifiedNotificationRouter] Priority muted: {notification_type}")
            return False
        
        # Get appropriate bot
        if self._mode == "MULTI_BOT":
            bot = self._bots.get(config.bot)
        else:
            bot = self._fallback_bot or self._bots.get(NotificationBot.CONTROLLER)
        
        if not bot:
            logger.error(f"[UnifiedNotificationRouter] No bot available for {notification_type}")
            return False
        
        # Format message
        message = self._format_notification(notification_type, data)
        
        # Send
        target_chat_id = chat_id or self._chat_id
        try:
            if hasattr(bot, 'send_message'):
                result = bot.send_message(message, chat_id=target_chat_id)
            else:
                logger.error(f"[UnifiedNotificationRouter] Bot has no send_message method")
                return False
            
            if result:
                self._stats["total_sent"] += 1
                self._stats["by_type"][notification_type] = self._stats["by_type"].get(notification_type, 0) + 1
                self._stats["by_bot"][config.bot.value] += 1
                logger.debug(f"[UnifiedNotificationRouter] Sent: {notification_type}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[UnifiedNotificationRouter] Send error: {e}")
            return False
    
    def _format_notification(self, notification_type: str, data: Dict[str, Any]) -> str:
        """
        Format notification based on type.
        
        Args:
            notification_type: Type of notification
            data: Notification data
        
        Returns:
            Formatted message string
        """
        formatters = {
            "trade_entry": self._format_trade_entry,
            "trade_exit": self._format_trade_exit,
            "tp_hit": self._format_tp_hit,
            "sl_hit": self._format_sl_hit,
            "profit_booking": self._format_profit_booking,
            "tp_continuation": self._format_tp_continuation,
            "sl_hunt_activated": self._format_sl_hunt_activated,
            "recovery_success": self._format_recovery_success,
            "recovery_failed": self._format_recovery_failed,
            "daily_limit_warning": self._format_daily_limit_warning,
            "daily_limit_hit": self._format_daily_limit_hit,
            "lifetime_limit_hit": self._format_lifetime_limit_hit,
            "bot_startup": self._format_bot_startup,
            "error_alert": self._format_error_alert,
            "plugin_enabled": self._format_plugin_enabled,
            "plugin_disabled": self._format_plugin_disabled,
            "config_changed": self._format_config_changed,
        }
        
        formatter = formatters.get(notification_type, self._format_generic)
        return formatter(data)
    
    # ========================================
    # Notification Formatters
    # ========================================
    
    def _format_generic(self, data: Dict[str, Any]) -> str:
        """Generic notification formatter"""
        title = data.get("title", "Notification")
        message = data.get("message", "")
        
        return (
            f"📢 <b>{title}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{message}\n\n"
            f"<i>Time: {datetime.now().strftime('%H:%M:%S')}</i>"
        )
    
    def _format_trade_entry(self, data: Dict[str, Any]) -> str:
        """Format trade entry notification"""
        symbol = data.get("symbol", "N/A")
        direction = data.get("direction", "N/A")
        entry_price = data.get("entry_price", 0)
        plugin = data.get("plugin_name", "Unknown")
        
        return (
            f"🟢 <b>ENTRY ALERT</b> | {plugin}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Direction:</b> {direction}\n"
            f"<b>Entry:</b> {entry_price}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_trade_exit(self, data: Dict[str, Any]) -> str:
        """Format trade exit notification"""
        symbol = data.get("symbol", "N/A")
        profit = data.get("profit", 0)
        reason = data.get("reason", "N/A")
        
        emoji = "🟢" if profit >= 0 else "🔴"
        
        return (
            f"{emoji} <b>EXIT ALERT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>P&L:</b> ${profit:+.2f}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_tp_hit(self, data: Dict[str, Any]) -> str:
        """Format TP hit notification"""
        symbol = data.get("symbol", "N/A")
        profit = data.get("profit", 0)
        
        return (
            f"🎯 <b>TAKE PROFIT HIT!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Profit:</b> +${profit:.2f}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_sl_hit(self, data: Dict[str, Any]) -> str:
        """Format SL hit notification"""
        symbol = data.get("symbol", "N/A")
        loss = data.get("loss", 0)
        
        return (
            f"🛑 <b>STOP LOSS HIT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Loss:</b> -${abs(loss):.2f}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_profit_booking(self, data: Dict[str, Any]) -> str:
        """Format profit booking notification"""
        symbol = data.get("symbol", "N/A")
        level = data.get("level", 0)
        profit = data.get("profit", 0)
        
        return (
            f"💰 <b>PROFIT BOOKED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Level:</b> {level}\n"
            f"<b>Profit:</b> +${profit:.2f}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_tp_continuation(self, data: Dict[str, Any]) -> str:
        """Format TP continuation notification"""
        symbol = data.get("symbol", "N/A")
        level = data.get("level", 0)
        direction = data.get("direction", "N/A")
        
        return (
            f"🚀 <b>AUTONOMOUS RE-ENTRY</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Symbol:</b> {symbol} ({direction})\n"
            f"<b>Type:</b> TP Continuation\n"
            f"<b>Level:</b> {level}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_sl_hunt_activated(self, data: Dict[str, Any]) -> str:
        """Format SL hunt activation notification"""
        symbol = data.get("symbol", "N/A")
        sl_price = data.get("sl_price", 0)
        
        return (
            f"🛡️ <b>SL HUNT ACTIVATED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>SL Price:</b> {sl_price}\n"
            f"<b>Status:</b> Monitoring...\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_recovery_success(self, data: Dict[str, Any]) -> str:
        """Format recovery success notification"""
        chain_id = data.get("chain_id", "N/A")
        level = data.get("level", 0)
        
        return (
            f"🎉 <b>RECOVERY SUCCESS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Chain:</b> {chain_id}\n"
            f"<b>Resumed to Level:</b> {level}\n"
            f"<b>Status:</b> ACTIVE ✅\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_recovery_failed(self, data: Dict[str, Any]) -> str:
        """Format recovery failed notification"""
        chain_id = data.get("chain_id", "N/A")
        reason = data.get("reason", "Unknown")
        
        return (
            f"💀 <b>RECOVERY FAILED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Chain:</b> {chain_id}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Status:</b> STOPPED ❌\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_daily_limit_warning(self, data: Dict[str, Any]) -> str:
        """Format daily limit warning notification"""
        current_loss = data.get("current_loss", 0)
        limit = data.get("limit", 0)
        remaining = data.get("remaining", 0)
        
        return (
            f"⚠️ <b>DAILY LOSS WARNING</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Current Loss:</b> ${current_loss:.2f}\n"
            f"<b>Daily Limit:</b> ${limit:.2f}\n"
            f"<b>Remaining:</b> ${remaining:.2f}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"⚠️ <i>Trade cautiously!</i>"
        )
    
    def _format_daily_limit_hit(self, data: Dict[str, Any]) -> str:
        """Format daily limit hit notification"""
        loss = data.get("loss", 0)
        limit = data.get("limit", 0)
        
        return (
            f"🛑 <b>DAILY LOSS LIMIT REACHED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Loss Today:</b> ${loss:.2f}\n"
            f"<b>Limit:</b> ${limit:.2f}\n\n"
            f"✋ <b>TRADING PAUSED AUTOMATICALLY</b>\n"
            f"<b>Reset Time:</b> 03:35 UTC"
        )
    
    def _format_lifetime_limit_hit(self, data: Dict[str, Any]) -> str:
        """Format lifetime limit hit notification"""
        loss = data.get("loss", 0)
        limit = data.get("limit", 0)
        
        return (
            f"🚨 <b>LIFETIME LOSS LIMIT REACHED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Total Loss:</b> ${loss:.2f}\n"
            f"<b>Limit:</b> ${limit:.2f}\n\n"
            f"🛑 <b>TRADING STOPPED</b>\n"
            f"<i>Manual intervention required</i>"
        )
    
    def _format_bot_startup(self, data: Dict[str, Any]) -> str:
        """Format bot startup notification"""
        mode = data.get("mode", "UNKNOWN")
        version = data.get("version", "2.0")
        
        return (
            f"🤖 <b>ZEPIX BOT STARTED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Version:</b> {version}\n"
            f"<b>Mode:</b> {mode}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"🚀 <b>Bot is ready to trade!</b>"
        )
    
    def _format_error_alert(self, data: Dict[str, Any]) -> str:
        """Format error alert notification"""
        error_type = data.get("error_type", "Unknown")
        details = data.get("details", "No details")
        severity = data.get("severity", "MEDIUM")
        
        severity_emoji = "🔴" if severity == "HIGH" else ("🟡" if severity == "MEDIUM" else "🟢")
        
        return (
            f"❌ <b>ERROR ALERT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Type:</b> {error_type}\n"
            f"<b>Severity:</b> {severity_emoji} {severity}\n"
            f"<b>Details:</b> {details}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_plugin_enabled(self, data: Dict[str, Any]) -> str:
        """Format plugin enabled notification"""
        plugin_name = data.get("plugin_name", "Unknown")
        
        return (
            f"✅ <b>PLUGIN ENABLED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Plugin:</b> {plugin_name}\n"
            f"<b>Status:</b> ACTIVE 🟢\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_plugin_disabled(self, data: Dict[str, Any]) -> str:
        """Format plugin disabled notification"""
        plugin_name = data.get("plugin_name", "Unknown")
        
        return (
            f"🔴 <b>PLUGIN DISABLED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Plugin:</b> {plugin_name}\n"
            f"<b>Status:</b> INACTIVE 🔴\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _format_config_changed(self, data: Dict[str, Any]) -> str:
        """Format config changed notification"""
        setting = data.get("setting", "Unknown")
        old_value = data.get("old_value", "N/A")
        new_value = data.get("new_value", "N/A")
        
        return (
            f"⚙️ <b>CONFIG CHANGED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Setting:</b> {setting}\n"
            f"<b>Old:</b> {old_value}\n"
            f"<b>New:</b> {new_value}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    # ========================================
    # Mute/Unmute Methods
    # ========================================
    
    def mute(self, notification_type: str):
        """Mute a notification type"""
        self._muted_types.add(notification_type)
        logger.info(f"[UnifiedNotificationRouter] Muted: {notification_type}")
    
    def unmute(self, notification_type: str):
        """Unmute a notification type"""
        self._muted_types.discard(notification_type)
        logger.info(f"[UnifiedNotificationRouter] Unmuted: {notification_type}")
    
    def mute_priority(self, priority: NotificationPriority):
        """Mute all notifications of a priority level"""
        self._muted_priorities.add(priority)
        logger.info(f"[UnifiedNotificationRouter] Muted priority: {priority.value}")
    
    def unmute_priority(self, priority: NotificationPriority):
        """Unmute all notifications of a priority level"""
        self._muted_priorities.discard(priority)
        logger.info(f"[UnifiedNotificationRouter] Unmuted priority: {priority.value}")
    
    def mute_all(self):
        """Mute all notifications (Do Not Disturb)"""
        self._muted_types = set(self.NOTIFICATION_TYPES.keys())
        logger.info("[UnifiedNotificationRouter] All notifications muted")
    
    def unmute_all(self):
        """Unmute all notifications"""
        self._muted_types.clear()
        self._muted_priorities.clear()
        logger.info("[UnifiedNotificationRouter] All notifications unmuted")
    
    # ========================================
    # Statistics
    # ========================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        return self._stats.copy()
    
    def reset_stats(self):
        """Reset statistics"""
        self._stats = {
            "total_sent": 0,
            "total_muted": 0,
            "by_type": {},
            "by_bot": {b.value: 0 for b in NotificationBot},
        }


# Singleton instance
_notification_router: Optional[UnifiedNotificationRouter] = None


def get_notification_router() -> UnifiedNotificationRouter:
    """Get or create singleton UnifiedNotificationRouter instance"""
    global _notification_router
    if _notification_router is None:
        _notification_router = UnifiedNotificationRouter()
    return _notification_router


def init_notification_router(
    controller_bot=None,
    notification_bot=None,
    analytics_bot=None,
    fallback_bot=None,
    chat_id: int = None
) -> UnifiedNotificationRouter:
    """Initialize UnifiedNotificationRouter with dependencies"""
    global _notification_router
    _notification_router = UnifiedNotificationRouter(
        controller_bot=controller_bot,
        notification_bot=notification_bot,
        analytics_bot=analytics_bot,
        fallback_bot=fallback_bot,
        chat_id=chat_id
    )
    return _notification_router
