"""
Notification Router - Smart routing of notifications to appropriate bots

Routes notifications based on:
- Priority level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Notification type (entry, exit, error, report, etc.)
- User preferences (mute/unmute)

Version: 1.0.0
Date: 2026-01-14
"""

import threading
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List, Set
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Notification priority levels"""
    CRITICAL = 5  # Emergency stop, daily loss limit, MT5 disconnect
    HIGH = 4      # Trade entry/exit, SL/TP hit
    MEDIUM = 3    # Partial profit, SL modification
    LOW = 2       # Daily summary, config reload
    INFO = 1      # Bot started, plugin loaded


class NotificationType(Enum):
    """Types of notifications"""
    # Trade Events
    ENTRY = "entry"
    EXIT = "exit"
    TP_HIT = "tp_hit"
    SL_HIT = "sl_hit"
    PROFIT_BOOKING = "profit_booking"
    SL_MODIFIED = "sl_modified"
    BREAKEVEN = "breakeven"
    
    # System Events
    BOT_STARTED = "bot_started"
    BOT_STOPPED = "bot_stopped"
    EMERGENCY_STOP = "emergency_stop"
    MT5_DISCONNECT = "mt5_disconnect"
    MT5_RECONNECT = "mt5_reconnect"
    DAILY_LOSS_LIMIT = "daily_loss_limit"
    
    # Plugin Events
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_ERROR = "plugin_error"
    CONFIG_RELOAD = "config_reload"
    
    # Alert Events
    ALERT_RECEIVED = "alert_received"
    ALERT_PROCESSED = "alert_processed"
    ALERT_IGNORED = "alert_ignored"
    ALERT_ERROR = "alert_error"
    
    # Analytics Events
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    PERFORMANCE_REPORT = "performance_report"
    RISK_ALERT = "risk_alert"
    
    # Generic
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class TargetBot(Enum):
    """Target bot for routing"""
    CONTROLLER = "controller"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"
    ALL = "all"  # Broadcast to all bots


@dataclass
class Notification:
    """Represents a notification to be routed"""
    notification_type: NotificationType
    priority: NotificationPriority
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    voice_enabled: bool = True
    notification_id: Optional[str] = None
    
    def __post_init__(self):
        if self.notification_id is None:
            self.notification_id = f"{self.notification_type.value}_{self.timestamp.timestamp()}"


# Default routing rules
DEFAULT_ROUTING_RULES: Dict[NotificationType, Dict] = {
    # Trade Events -> Notification Bot
    NotificationType.ENTRY: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.EXIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.TP_HIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.SL_HIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.PROFIT_BOOKING: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.SL_MODIFIED: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.BREAKEVEN: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.MEDIUM, "voice": False},
    
    # System Events
    NotificationType.BOT_STARTED: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.INFO, "voice": False},
    NotificationType.BOT_STOPPED: {"target": TargetBot.ALL, "priority": NotificationPriority.CRITICAL, "voice": True},
    NotificationType.EMERGENCY_STOP: {"target": TargetBot.ALL, "priority": NotificationPriority.CRITICAL, "voice": True},
    NotificationType.MT5_DISCONNECT: {"target": TargetBot.ALL, "priority": NotificationPriority.CRITICAL, "voice": True},
    NotificationType.MT5_RECONNECT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": False},
    NotificationType.DAILY_LOSS_LIMIT: {"target": TargetBot.ALL, "priority": NotificationPriority.CRITICAL, "voice": True},
    
    # Plugin Events
    NotificationType.PLUGIN_LOADED: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.INFO, "voice": False},
    NotificationType.PLUGIN_ERROR: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": False},
    NotificationType.CONFIG_RELOAD: {"target": TargetBot.ANALYTICS, "priority": NotificationPriority.LOW, "voice": False},
    
    # Alert Events
    NotificationType.ALERT_RECEIVED: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.INFO, "voice": False},
    NotificationType.ALERT_PROCESSED: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.ALERT_IGNORED: {"target": TargetBot.ANALYTICS, "priority": NotificationPriority.LOW, "voice": False},
    NotificationType.ALERT_ERROR: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": False},
    
    # Analytics Events
    NotificationType.DAILY_SUMMARY: {"target": TargetBot.ANALYTICS, "priority": NotificationPriority.LOW, "voice": False},
    NotificationType.WEEKLY_SUMMARY: {"target": TargetBot.ANALYTICS, "priority": NotificationPriority.LOW, "voice": False},
    NotificationType.PERFORMANCE_REPORT: {"target": TargetBot.ANALYTICS, "priority": NotificationPriority.LOW, "voice": False},
    NotificationType.RISK_ALERT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    
    # Generic
    NotificationType.INFO: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.INFO, "voice": False},
    NotificationType.WARNING: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.ERROR: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": False},
}


class NotificationRouter:
    """
    Routes notifications to appropriate Telegram bots based on type and priority.
    
    Features:
    - Priority-based routing (CRITICAL broadcasts to all)
    - Type-based routing (entries to Notification, reports to Analytics)
    - Mute/unmute functionality per notification type
    - Voice alert integration
    - Statistics tracking
    """
    
    def __init__(
        self,
        controller_callback: Optional[Callable] = None,
        notification_callback: Optional[Callable] = None,
        analytics_callback: Optional[Callable] = None,
        voice_callback: Optional[Callable] = None
    ):
        """
        Initialize NotificationRouter.
        
        Args:
            controller_callback: Function to send to Controller Bot
            notification_callback: Function to send to Notification Bot
            analytics_callback: Function to send to Analytics Bot
            voice_callback: Function to trigger voice alerts
        """
        self.controller_callback = controller_callback
        self.notification_callback = notification_callback
        self.analytics_callback = analytics_callback
        self.voice_callback = voice_callback
        
        # Routing rules (can be customized)
        self.routing_rules = DEFAULT_ROUTING_RULES.copy()
        
        # Muted notification types
        self.muted_types: Set[NotificationType] = set()
        
        # Global mute
        self.global_mute = False
        self.voice_mute = False
        
        # Statistics
        self.stats = {
            "total_sent": 0,
            "by_type": {},
            "by_priority": {},
            "by_target": {},
            "voice_alerts_sent": 0,
            "muted_notifications": 0,
            "failed_notifications": 0
        }
        
        self._lock = threading.Lock()
        
        # Custom formatters
        self.formatters: Dict[NotificationType, Callable] = {}
    
    def register_formatter(self, notification_type: NotificationType, formatter: Callable):
        """
        Register a custom formatter for a notification type.
        
        Args:
            notification_type: Type of notification
            formatter: Function that takes data dict and returns formatted message
        """
        self.formatters[notification_type] = formatter
    
    def set_routing_rule(
        self,
        notification_type: NotificationType,
        target: TargetBot,
        priority: NotificationPriority,
        voice: bool = False
    ):
        """
        Set or update a routing rule.
        
        Args:
            notification_type: Type of notification
            target: Target bot
            priority: Priority level
            voice: Whether to trigger voice alert
        """
        self.routing_rules[notification_type] = {
            "target": target,
            "priority": priority,
            "voice": voice
        }
    
    def mute(self, notification_type: NotificationType):
        """Mute a specific notification type"""
        self.muted_types.add(notification_type)
        logger.info(f"Muted notification type: {notification_type.value}")
    
    def unmute(self, notification_type: NotificationType):
        """Unmute a specific notification type"""
        self.muted_types.discard(notification_type)
        logger.info(f"Unmuted notification type: {notification_type.value}")
    
    def mute_all(self):
        """Mute all notifications (except CRITICAL)"""
        self.global_mute = True
        logger.info("Global mute enabled (CRITICAL notifications still active)")
    
    def unmute_all(self):
        """Unmute all notifications"""
        self.global_mute = False
        self.muted_types.clear()
        logger.info("All notifications unmuted")
    
    def mute_voice(self):
        """Mute voice alerts"""
        self.voice_mute = True
        logger.info("Voice alerts muted")
    
    def unmute_voice(self):
        """Unmute voice alerts"""
        self.voice_mute = False
        logger.info("Voice alerts unmuted")
    
    def is_muted(self, notification_type: NotificationType, priority: NotificationPriority) -> bool:
        """
        Check if a notification type is muted.
        
        Args:
            notification_type: Type of notification
            priority: Priority level
            
        Returns:
            True if muted, False otherwise
        """
        # CRITICAL notifications are never muted
        if priority == NotificationPriority.CRITICAL:
            return False
        
        # Check global mute
        if self.global_mute:
            return True
        
        # Check specific type mute
        return notification_type in self.muted_types
    
    def send(
        self,
        notification_type: NotificationType,
        message: str,
        data: Optional[Dict] = None,
        priority: Optional[NotificationPriority] = None,
        voice_override: Optional[bool] = None
    ) -> bool:
        """
        Send a notification through the router.
        
        Args:
            notification_type: Type of notification
            message: Notification message
            data: Additional data for formatting
            priority: Override priority (uses default if None)
            voice_override: Override voice setting
            
        Returns:
            True if sent successfully
        """
        data = data or {}
        
        # Get routing rule
        rule = self.routing_rules.get(notification_type, {
            "target": TargetBot.CONTROLLER,
            "priority": NotificationPriority.INFO,
            "voice": False
        })
        
        # Use provided priority or default from rule
        actual_priority = priority or rule["priority"]
        
        # Check if muted
        if self.is_muted(notification_type, actual_priority):
            self.stats["muted_notifications"] += 1
            logger.debug(f"Notification muted: {notification_type.value}")
            return False
        
        # Format message if formatter exists
        formatted_message = message
        if notification_type in self.formatters:
            try:
                formatted_message = self.formatters[notification_type](data)
            except Exception as e:
                logger.error(f"Formatter error for {notification_type.value}: {e}")
        
        # Determine target
        target = rule["target"]
        
        # Override target for CRITICAL priority
        if actual_priority == NotificationPriority.CRITICAL:
            target = TargetBot.ALL
        
        # Send to target(s)
        success = self._send_to_target(target, formatted_message, actual_priority)
        
        # Trigger voice alert if enabled
        voice_enabled = voice_override if voice_override is not None else rule.get("voice", False)
        if voice_enabled and not self.voice_mute and self.voice_callback:
            try:
                self.voice_callback(formatted_message, actual_priority)
                self.stats["voice_alerts_sent"] += 1
            except Exception as e:
                logger.error(f"Voice alert error: {e}")
        
        # Update statistics
        self._update_stats(notification_type, actual_priority, target, success)
        
        return success
    
    def _send_to_target(self, target: TargetBot, message: str, priority: NotificationPriority) -> bool:
        """Send message to target bot(s)"""
        success = False
        
        try:
            if target == TargetBot.ALL:
                # Broadcast to all bots
                results = []
                if self.controller_callback:
                    results.append(self._safe_send(self.controller_callback, message))
                if self.notification_callback:
                    results.append(self._safe_send(self.notification_callback, message))
                if self.analytics_callback:
                    results.append(self._safe_send(self.analytics_callback, message))
                success = any(results)
                
            elif target == TargetBot.CONTROLLER:
                if self.controller_callback:
                    success = self._safe_send(self.controller_callback, message)
                    
            elif target == TargetBot.NOTIFICATION:
                if self.notification_callback:
                    success = self._safe_send(self.notification_callback, message)
                    
            elif target == TargetBot.ANALYTICS:
                if self.analytics_callback:
                    success = self._safe_send(self.analytics_callback, message)
            
        except Exception as e:
            logger.error(f"Send to target error: {e}")
            success = False
        
        return success
    
    def _safe_send(self, callback: Callable, message: str) -> bool:
        """Safely send message via callback"""
        try:
            result = callback(message)
            return result is not None
        except Exception as e:
            logger.error(f"Callback error: {e}")
            return False
    
    def _update_stats(
        self,
        notification_type: NotificationType,
        priority: NotificationPriority,
        target: TargetBot,
        success: bool
    ):
        """Update statistics"""
        with self._lock:
            if success:
                self.stats["total_sent"] += 1
                
                # By type
                type_key = notification_type.value
                self.stats["by_type"][type_key] = self.stats["by_type"].get(type_key, 0) + 1
                
                # By priority
                priority_key = priority.name
                self.stats["by_priority"][priority_key] = self.stats["by_priority"].get(priority_key, 0) + 1
                
                # By target
                target_key = target.value
                self.stats["by_target"][target_key] = self.stats["by_target"].get(target_key, 0) + 1
            else:
                self.stats["failed_notifications"] += 1
    
    def get_stats(self) -> Dict:
        """Get router statistics"""
        with self._lock:
            return {
                "stats": self.stats.copy(),
                "muted_types": [t.value for t in self.muted_types],
                "global_mute": self.global_mute,
                "voice_mute": self.voice_mute
            }
    
    def get_muted_types(self) -> List[str]:
        """Get list of muted notification types"""
        return [t.value for t in self.muted_types]


class NotificationFormatter:
    """
    Provides standard formatters for different notification types.
    """
    
    @staticmethod
    def format_entry(data: Dict) -> str:
        """Format entry notification"""
        plugin_name = data.get("plugin_name", "Unknown")
        symbol = data.get("symbol", "N/A")
        direction = data.get("direction", "N/A")
        entry_price = data.get("entry_price", 0)
        
        message = (
            f"<b>ENTRY ALERT</b> | {plugin_name}\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Direction:</b> {direction}\n"
            f"<b>Entry Price:</b> {entry_price}\n"
        )
        
        if data.get("order_a_lot"):
            message += (
                f"\n<b>Order A:</b> {data.get('order_a_lot')} lots\n"
                f"  SL: {data.get('order_a_sl', 'N/A')}\n"
                f"  TP: {data.get('order_a_tp', 'N/A')}\n"
            )
        
        if data.get("order_b_lot"):
            message += (
                f"\n<b>Order B:</b> {data.get('order_b_lot')} lots\n"
                f"  SL: {data.get('order_b_sl', 'N/A')}\n"
                f"  TP: {data.get('order_b_tp', 'N/A')}\n"
            )
        
        message += f"\n<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        
        return message
    
    @staticmethod
    def format_exit(data: Dict) -> str:
        """Format exit notification"""
        plugin_name = data.get("plugin_name", "Unknown")
        symbol = data.get("symbol", "N/A")
        direction = data.get("direction", "N/A")
        profit = data.get("profit", 0)
        
        emoji = "" if profit >= 0 else ""
        
        message = (
            f"{emoji} <b>EXIT ALERT</b> | {plugin_name}\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Direction:</b> {direction} -> CLOSED\n\n"
            f"<b>Entry:</b> {data.get('entry_price', 'N/A')}\n"
            f"<b>Exit:</b> {data.get('exit_price', 'N/A')}\n"
            f"<b>Hold Time:</b> {data.get('hold_time', 'N/A')}\n\n"
            f"<b>P&L:</b> ${profit:+.2f}\n"
            f"<b>Reason:</b> {data.get('reason', 'N/A')}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        
        return message
    
    @staticmethod
    def format_daily_summary(data: Dict) -> str:
        """Format daily summary notification"""
        date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        total_trades = data.get("total_trades", 0)
        winners = data.get("winners", 0)
        losers = data.get("losers", 0)
        win_rate = data.get("win_rate", 0)
        net_pnl = data.get("net_pnl", 0)
        
        emoji = "" if net_pnl >= 0 else ""
        
        message = (
            f"<b>DAILY SUMMARY</b> | {date}\n"
            f"{'=' * 24}\n\n"
            f"<b>Performance:</b>\n"
            f"  Total Trades: {total_trades}\n"
            f"  Winners: {winners} ({win_rate:.1f}%)\n"
            f"  Losers: {losers}\n\n"
            f"<b>P&L:</b>\n"
            f"  Gross Profit: +${data.get('gross_profit', 0):.2f}\n"
            f"  Gross Loss: -${data.get('gross_loss', 0):.2f}\n"
            f"  {emoji} Net P&L: ${net_pnl:+.2f}"
        )
        
        return message
    
    @staticmethod
    def format_emergency(data: Dict) -> str:
        """Format emergency notification"""
        reason = data.get("reason", "Unknown")
        details = data.get("details", "No details available")
        
        message = (
            f"<b>EMERGENCY ALERT</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Details:</b> {details}\n\n"
            f"<b>Action Required:</b> Immediate attention needed\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        
        return message
    
    @staticmethod
    def format_error(data: Dict) -> str:
        """Format error notification"""
        error_type = data.get("error_type", "Unknown")
        severity = data.get("severity", "MEDIUM")
        details = data.get("details", "No details available")
        
        severity_emoji = "" if severity == "HIGH" else ("" if severity == "MEDIUM" else "")
        
        message = (
            f"<b>ERROR ALERT</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Error Type:</b> {error_type}\n"
            f"<b>Severity:</b> {severity_emoji} {severity}\n"
            f"<b>Details:</b> {details}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        
        return message


def create_default_router(
    controller_callback: Optional[Callable] = None,
    notification_callback: Optional[Callable] = None,
    analytics_callback: Optional[Callable] = None,
    voice_callback: Optional[Callable] = None
) -> NotificationRouter:
    """
    Create a NotificationRouter with default formatters registered.
    
    Args:
        controller_callback: Function to send to Controller Bot
        notification_callback: Function to send to Notification Bot
        analytics_callback: Function to send to Analytics Bot
        voice_callback: Function to trigger voice alerts
        
    Returns:
        Configured NotificationRouter
    """
    router = NotificationRouter(
        controller_callback=controller_callback,
        notification_callback=notification_callback,
        analytics_callback=analytics_callback,
        voice_callback=voice_callback
    )
    
    # Register default formatters
    router.register_formatter(NotificationType.ENTRY, NotificationFormatter.format_entry)
    router.register_formatter(NotificationType.EXIT, NotificationFormatter.format_exit)
    router.register_formatter(NotificationType.DAILY_SUMMARY, NotificationFormatter.format_daily_summary)
    router.register_formatter(NotificationType.EMERGENCY_STOP, NotificationFormatter.format_emergency)
    router.register_formatter(NotificationType.ERROR, NotificationFormatter.format_error)
    
    return router
