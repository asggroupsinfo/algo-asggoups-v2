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
    
    # V6 Price Action Events (NEW - Telegram V5 Upgrade)
    V6_ENTRY_15M = "v6_entry_15m"
    V6_ENTRY_30M = "v6_entry_30m"
    V6_ENTRY_1H = "v6_entry_1h"
    V6_ENTRY_4H = "v6_entry_4h"
    V6_EXIT = "v6_exit"
    V6_TP_HIT = "v6_tp_hit"
    V6_SL_HIT = "v6_sl_hit"
    V6_TIMEFRAME_ENABLED = "v6_timeframe_enabled"
    V6_TIMEFRAME_DISABLED = "v6_timeframe_disabled"
    V6_DAILY_SUMMARY = "v6_daily_summary"
    V6_SIGNAL = "v6_signal"
    V6_BREAKEVEN = "v6_breakeven"
    
    # V3 Combined Events (for parity)
    V3_ENTRY = "v3_entry"
    V3_EXIT = "v3_exit"
    V3_TP_HIT = "v3_tp_hit"
    V3_SL_HIT = "v3_sl_hit"
    V3_LOGIC_TOGGLED = "v3_logic_toggled"
    
    # ==================== NEW NOTIFICATION TYPES (34 total) ====================
    
    # Autonomous System Events (5)
    TP_CONTINUATION = "tp_continuation"
    SL_HUNT_ACTIVATED = "sl_hunt_activated"
    RECOVERY_SUCCESS = "recovery_success"
    RECOVERY_FAILED = "recovery_failed"
    PROFIT_ORDER_PROTECTION = "profit_order_protection"
    
    # Re-entry System Events (5)
    TP_REENTRY_STARTED = "tp_reentry_started"
    TP_REENTRY_EXECUTED = "tp_reentry_executed"
    TP_REENTRY_COMPLETED = "tp_reentry_completed"
    SL_HUNT_RECOVERY = "sl_hunt_recovery"
    EXIT_CONTINUATION = "exit_continuation"
    
    # Signal Events (4)
    SIGNAL_RECEIVED = "signal_received"
    SIGNAL_IGNORED = "signal_ignored"
    SIGNAL_FILTERED = "signal_filtered"
    TREND_CHANGED = "trend_changed"
    
    # Trade Events (3)
    PARTIAL_CLOSE = "partial_close"
    MANUAL_EXIT = "manual_exit"
    REVERSAL_EXIT = "reversal_exit"
    
    # System Events (6)
    MT5_CONNECTED = "mt5_connected"
    LIFETIME_LOSS_LIMIT = "lifetime_loss_limit"
    DAILY_LOSS_WARNING = "daily_loss_warning"
    CONFIG_ERROR = "config_error"
    DATABASE_ERROR = "database_error"
    ORDER_FAILED = "order_failed"
    
    # Session Events (4)
    SESSION_TOGGLE = "session_toggle"
    SYMBOL_TOGGLE = "symbol_toggle"
    TIME_ADJUSTMENT = "time_adjustment"
    FORCE_CLOSE_TOGGLE = "force_close_toggle"
    
    # Voice Alert Events (5)
    VOICE_TRADE_ENTRY = "voice_trade_entry"
    VOICE_TP_HIT = "voice_tp_hit"
    VOICE_SL_HIT = "voice_sl_hit"
    VOICE_RISK_LIMIT = "voice_risk_limit"
    VOICE_RECOVERY = "voice_recovery"
    
    # Dashboard Events (2)
    DASHBOARD_UPDATE = "dashboard_update"
    AUTONOMOUS_DASHBOARD = "autonomous_dashboard"


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
    
    # V6 Price Action Events (NEW - Telegram V5 Upgrade)
    NotificationType.V6_ENTRY_15M: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.V6_ENTRY_30M: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.V6_ENTRY_1H: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.V6_ENTRY_4H: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.V6_EXIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.V6_TP_HIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.V6_SL_HIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.V6_TIMEFRAME_ENABLED: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.V6_TIMEFRAME_DISABLED: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.V6_DAILY_SUMMARY: {"target": TargetBot.ANALYTICS, "priority": NotificationPriority.LOW, "voice": False},
    NotificationType.V6_SIGNAL: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": False},
    NotificationType.V6_BREAKEVEN: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.MEDIUM, "voice": False},
    
    # V3 Combined Events (for parity)
    NotificationType.V3_ENTRY: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.V3_EXIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.V3_TP_HIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.V3_SL_HIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.V3_LOGIC_TOGGLED: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.MEDIUM, "voice": False},
    
    # ==================== NEW ROUTING RULES (34 total) ====================
    
    # Autonomous System Events (5) -> Notification Bot
    NotificationType.TP_CONTINUATION: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.SL_HUNT_ACTIVATED: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.RECOVERY_SUCCESS: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.RECOVERY_FAILED: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.PROFIT_ORDER_PROTECTION: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.MEDIUM, "voice": False},
    
    # Re-entry System Events (5) -> Notification Bot
    NotificationType.TP_REENTRY_STARTED: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.TP_REENTRY_EXECUTED: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.TP_REENTRY_COMPLETED: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.SL_HUNT_RECOVERY: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.EXIT_CONTINUATION: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    
    # Signal Events (4) -> Notification Bot
    NotificationType.SIGNAL_RECEIVED: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": False},
    NotificationType.SIGNAL_IGNORED: {"target": TargetBot.ANALYTICS, "priority": NotificationPriority.INFO, "voice": False},
    NotificationType.SIGNAL_FILTERED: {"target": TargetBot.ANALYTICS, "priority": NotificationPriority.INFO, "voice": False},
    NotificationType.TREND_CHANGED: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": False},
    
    # Trade Events (3) -> Notification Bot
    NotificationType.PARTIAL_CLOSE: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.MANUAL_EXIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.REVERSAL_EXIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    
    # System Events (6) -> Controller/All
    NotificationType.MT5_CONNECTED: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.HIGH, "voice": False},
    NotificationType.LIFETIME_LOSS_LIMIT: {"target": TargetBot.ALL, "priority": NotificationPriority.CRITICAL, "voice": True},
    NotificationType.DAILY_LOSS_WARNING: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.CONFIG_ERROR: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.HIGH, "voice": False},
    NotificationType.DATABASE_ERROR: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.HIGH, "voice": False},
    NotificationType.ORDER_FAILED: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    
    # Session Events (4) -> Controller Bot
    NotificationType.SESSION_TOGGLE: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.SYMBOL_TOGGLE: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.TIME_ADJUSTMENT: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.MEDIUM, "voice": False},
    NotificationType.FORCE_CLOSE_TOGGLE: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.MEDIUM, "voice": False},
    
    # Voice Alert Events (5) -> Notification Bot (voice always enabled)
    NotificationType.VOICE_TRADE_ENTRY: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.VOICE_TP_HIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.HIGH, "voice": True},
    NotificationType.VOICE_SL_HIT: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.CRITICAL, "voice": True},
    NotificationType.VOICE_RISK_LIMIT: {"target": TargetBot.ALL, "priority": NotificationPriority.CRITICAL, "voice": True},
    NotificationType.VOICE_RECOVERY: {"target": TargetBot.NOTIFICATION, "priority": NotificationPriority.MEDIUM, "voice": True},
    
    # Dashboard Events (2) -> Controller Bot
    NotificationType.DASHBOARD_UPDATE: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.LOW, "voice": False},
    NotificationType.AUTONOMOUS_DASHBOARD: {"target": TargetBot.CONTROLLER, "priority": NotificationPriority.LOW, "voice": False},
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
    
    # ========================================
    # V6 Price Action Formatters (NEW - Telegram V5 Upgrade)
    # ========================================
    
    @staticmethod
    def format_v6_entry(data: Dict) -> str:
        """Format V6 Price Action entry notification with timeframe badge"""
        timeframe = data.get("timeframe", "N/A")
        symbol = data.get("symbol", "N/A")
        direction = data.get("direction", "N/A")
        entry_price = data.get("entry_price", 0)
        
        # Timeframe-specific badges
        tf_badges = {
            "15m": "15M",
            "30m": "30M",
            "1h": "1H",
            "4h": "4H",
        }
        tf_badge = tf_badges.get(timeframe.lower(), timeframe.upper())
        
        direction_emoji = "" if direction.upper() == "BUY" else ""
        
        message = (
            f"{direction_emoji} <b>V6 ENTRY</b> | {tf_badge}\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Direction:</b> {direction}\n"
            f"<b>Entry Price:</b> {entry_price}\n"
            f"<b>Timeframe:</b> {tf_badge}\n"
        )
        
        if data.get("sl"):
            message += f"<b>Stop Loss:</b> {data.get('sl')}\n"
        if data.get("tp"):
            message += f"<b>Take Profit:</b> {data.get('tp')}\n"
        if data.get("lot_size"):
            message += f"<b>Lot Size:</b> {data.get('lot_size')}\n"
        if data.get("pattern"):
            message += f"<b>Pattern:</b> {data.get('pattern')}\n"
        
        message += f"\n<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        
        return message
    
    @staticmethod
    def format_v6_exit(data: Dict) -> str:
        """Format V6 Price Action exit notification"""
        timeframe = data.get("timeframe", "N/A")
        symbol = data.get("symbol", "N/A")
        direction = data.get("direction", "N/A")
        profit = data.get("pnl", data.get("profit", 0))
        exit_reason = data.get("exit_reason", "N/A")
        
        tf_badges = {"15m": "15M", "30m": "30M", "1h": "1H", "4h": "4H"}
        tf_badge = tf_badges.get(timeframe.lower(), timeframe.upper()) if timeframe else "V6"
        
        result_emoji = "" if profit >= 0 else ""
        
        message = (
            f"{result_emoji} <b>V6 EXIT</b> | {tf_badge}\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Direction:</b> {direction} -> CLOSED\n\n"
            f"<b>Entry:</b> {data.get('entry_price', 'N/A')}\n"
            f"<b>Exit:</b> {data.get('exit_price', 'N/A')}\n"
            f"<b>Hold Time:</b> {data.get('duration', data.get('hold_time', 'N/A'))}\n\n"
            f"<b>P&L:</b> ${profit:+.2f}"
        )
        
        if data.get("pips"):
            message += f" ({data.get('pips'):+.1f} pips)"
        
        message += (
            f"\n<b>Reason:</b> {exit_reason}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        
        return message
    
    @staticmethod
    def format_v6_tp_hit(data: Dict) -> str:
        """Format V6 take profit hit notification"""
        timeframe = data.get("timeframe", "N/A")
        symbol = data.get("symbol", "N/A")
        profit = data.get("pnl", data.get("profit", 0))
        tp_level = data.get("tp_level", 1)
        
        tf_badges = {"15m": "15M", "30m": "30M", "1h": "1H", "4h": "4H"}
        tf_badge = tf_badges.get(timeframe.lower(), timeframe.upper()) if timeframe else "V6"
        
        message = (
            f" <b>V6 TP{tp_level} HIT</b> | {tf_badge}\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>TP Level:</b> {tp_level}\n"
            f"<b>Profit:</b> ${profit:+.2f}\n"
        )
        
        if data.get("pips"):
            message += f"<b>Pips:</b> {data.get('pips'):+.1f}\n"
        
        message += f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        
        return message
    
    @staticmethod
    def format_v6_sl_hit(data: Dict) -> str:
        """Format V6 stop loss hit notification"""
        timeframe = data.get("timeframe", "N/A")
        symbol = data.get("symbol", "N/A")
        loss = data.get("pnl", data.get("loss", 0))
        
        tf_badges = {"15m": "15M", "30m": "30M", "1h": "1H", "4h": "4H"}
        tf_badge = tf_badges.get(timeframe.lower(), timeframe.upper()) if timeframe else "V6"
        
        message = (
            f" <b>V6 SL HIT</b> | {tf_badge}\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Loss:</b> ${loss:.2f}\n"
        )
        
        if data.get("pips"):
            message += f"<b>Pips:</b> {data.get('pips'):.1f}\n"
        
        message += f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        
        return message
    
    @staticmethod
    def format_v6_timeframe_toggle(data: Dict) -> str:
        """Format V6 timeframe enabled/disabled notification"""
        timeframe = data.get("timeframe", "N/A")
        enabled = data.get("enabled", False)
        
        tf_badges = {"15m": "15M", "30m": "30M", "1h": "1H", "4h": "4H"}
        tf_badge = tf_badges.get(timeframe.lower(), timeframe.upper()) if timeframe else timeframe
        
        status_emoji = "" if enabled else ""
        action = "ENABLED" if enabled else "DISABLED"
        
        message = (
            f"{status_emoji} <b>V6 {tf_badge} {action}</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Timeframe:</b> {tf_badge}\n"
            f"<b>Status:</b> {action}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        
        return message
    
    @staticmethod
    def format_v6_daily_summary(data: Dict) -> str:
        """Format V6 daily summary notification"""
        date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        message = (
            f" <b>V6 DAILY SUMMARY</b> | {date}\n"
            f"{'=' * 24}\n\n"
            f"<b>By Timeframe:</b>\n"
        )
        
        # Per-timeframe stats
        for tf in ["15m", "30m", "1h", "4h"]:
            tf_data = data.get(tf, {})
            trades = tf_data.get("trades", 0)
            pnl = tf_data.get("pnl", 0)
            win_rate = tf_data.get("win_rate", 0)
            
            if trades > 0:
                emoji = "" if pnl >= 0 else ""
                message += f"  {tf.upper()}: {trades} trades, {emoji}${pnl:+.2f} ({win_rate:.0f}% WR)\n"
            else:
                message += f"  {tf.upper()}: No trades\n"
        
        # Totals
        total_trades = data.get("total_trades", 0)
        total_pnl = data.get("total_pnl", 0)
        total_win_rate = data.get("total_win_rate", 0)
        
        total_emoji = "" if total_pnl >= 0 else ""
        
        message += (
            f"\n<b>V6 Total:</b>\n"
            f"  Trades: {total_trades}\n"
            f"  {total_emoji} P&L: ${total_pnl:+.2f}\n"
            f"  Win Rate: {total_win_rate:.1f}%"
        )
        
        return message
    
    @staticmethod
    def format_v6_signal(data: Dict) -> str:
        """Format V6 signal received notification"""
        timeframe = data.get("timeframe", "N/A")
        symbol = data.get("symbol", "N/A")
        direction = data.get("direction", "N/A")
        pattern = data.get("pattern", "N/A")
        
        tf_badges = {"15m": "15M", "30m": "30M", "1h": "1H", "4h": "4H"}
        tf_badge = tf_badges.get(timeframe.lower(), timeframe.upper()) if timeframe else "V6"
        
        direction_emoji = "" if direction.upper() == "BUY" else ""
        
        message = (
            f" <b>V6 SIGNAL</b> | {tf_badge}\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Direction:</b> {direction_emoji} {direction}\n"
            f"<b>Timeframe:</b> {tf_badge}\n"
            f"<b>Pattern:</b> {pattern}\n"
        )
        
        if data.get("entry"):
            message += f"<b>Entry:</b> {data.get('entry')}\n"
        if data.get("sl"):
            message += f"<b>SL:</b> {data.get('sl')}\n"
        if data.get("tp"):
            message += f"<b>TP:</b> {data.get('tp')}\n"
        
        message += f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        
        return message
    
    # ==================== NEW FORMATTERS (34 total) ====================
    
    # Autonomous System Formatters (5)
    @staticmethod
    def format_tp_continuation(data: Dict) -> str:
        """Format TP continuation notification"""
        symbol = data.get("symbol", "N/A")
        direction = data.get("direction", "N/A")
        level = data.get("level", 1)
        next_level = data.get("next_level", level + 1)
        entry = data.get("entry", "N/A")
        total_profit = data.get("total_profit", 0)
        
        message = (
            f"<b>AUTONOMOUS RE-ENTRY</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol} ({direction})\n"
            f"<b>Type:</b> TP Continuation\n"
            f"<b>Progress:</b> Level {level} -> Level {next_level}\n\n"
            f"<b>Entry:</b> {entry}\n"
            f"<b>Total Profit:</b> ${total_profit:+.2f}\n"
            f"<b>Status:</b> ACTIVE\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_sl_hunt_activated(data: Dict) -> str:
        """Format SL Hunt activated notification"""
        symbol = data.get("symbol", "N/A")
        direction = data.get("direction", "N/A")
        sl_price = data.get("sl_price", "N/A")
        recovery_entry = data.get("recovery_entry", "N/A")
        attempt = data.get("attempt", 1)
        
        message = (
            f"<b>SL HUNT ACTIVATED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol} ({direction})\n"
            f"<b>Type:</b> Recovery Entry\n"
            f"<b>Attempt:</b> {attempt}/1\n\n"
            f"<b>SL Hit:</b> {sl_price}\n"
            f"<b>Recovery Entry:</b> {recovery_entry}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_recovery_success(data: Dict) -> str:
        """Format recovery success notification"""
        chain_id = data.get("chain_id", "N/A")
        level = data.get("level", 1)
        
        message = (
            f"<b>RECOVERY SUCCESS</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Chain:</b> {chain_id}\n"
            f"<b>Resumed to Level:</b> {level}\n"
            f"<b>Status:</b> ACTIVE\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_recovery_failed(data: Dict) -> str:
        """Format recovery failed notification"""
        chain_id = data.get("chain_id", "N/A")
        reason = data.get("reason", "No more recovery attempts allowed")
        
        message = (
            f"<b>RECOVERY FAILED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Chain:</b> {chain_id}\n"
            f"<b>Status:</b> STOPPED\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_profit_order_protection(data: Dict) -> str:
        """Format profit order protection notification"""
        chain_id = data.get("chain_id", "N/A")
        level = data.get("level", 1)
        order_id = data.get("order_id", "N/A")
        sl_price = data.get("sl_price", "N/A")
        current_price = data.get("current_price", "N/A")
        
        message = (
            f"<b>PROFIT ORDER PROTECTION</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Chain:</b> #{chain_id}\n"
            f"<b>Level:</b> {level}\n"
            f"<b>Order ID:</b> #{order_id}\n"
            f"<b>SL Price:</b> {sl_price}\n"
            f"<b>Current Price:</b> {current_price}\n"
            f"<b>Status:</b> MONITORING ACTIVE\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    # Re-entry System Formatters (5)
    @staticmethod
    def format_tp_reentry_started(data: Dict) -> str:
        """Format TP re-entry started notification"""
        symbol = data.get("symbol", "N/A")
        level = data.get("level", 1)
        next_level = data.get("next_level", level + 1)
        mode = data.get("mode", "Autonomous")
        
        message = (
            f"<b>TP RE-ENTRY</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Level:</b> {level} -> {next_level}\n"
            f"<b>Mode:</b> {mode}\n"
            f"<b>Trend Aligned:</b> Yes\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_tp_reentry_executed(data: Dict) -> str:
        """Format TP re-entry executed notification"""
        symbol = data.get("symbol", "N/A")
        direction = data.get("direction", "N/A")
        entry = data.get("entry", "N/A")
        sl = data.get("sl", "N/A")
        tp = data.get("tp", "N/A")
        level = data.get("level", 1)
        
        direction_emoji = "" if direction.upper() == "BUY" else ""
        
        message = (
            f"{direction_emoji} <b>TP RE-ENTRY EXECUTED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Direction:</b> {direction}\n"
            f"<b>Level:</b> {level}\n\n"
            f"<b>Entry:</b> {entry}\n"
            f"<b>SL:</b> {sl}\n"
            f"<b>TP:</b> {tp}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_tp_reentry_completed(data: Dict) -> str:
        """Format TP re-entry chain completed notification"""
        chain_id = data.get("chain_id", "N/A")
        total_profit = data.get("total_profit", 0)
        levels_completed = data.get("levels_completed", 0)
        max_levels = data.get("max_levels", 5)
        
        message = (
            f"<b>PROFIT CHAIN COMPLETE!</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Chain:</b> #{chain_id}\n"
            f"<b>Total Profit:</b> ${total_profit:+.2f}\n"
            f"<b>Levels:</b> {levels_completed}/{max_levels}\n"
            f"<b>Success Rate:</b> 100%\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_sl_hunt_recovery(data: Dict) -> str:
        """Format SL Hunt recovery order placed notification"""
        recovery_for = data.get("recovery_for", "N/A")
        new_order = data.get("new_order", "N/A")
        entry = data.get("entry", "N/A")
        sl = data.get("sl", "N/A")
        tp = data.get("tp", "N/A")
        lot = data.get("lot", "N/A")
        
        message = (
            f"<b>SL HUNT RECOVERY ORDER PLACED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Recovery For:</b> #{recovery_for}\n"
            f"<b>New Order:</b> #{new_order}\n"
            f"<b>Entry:</b> {entry}\n"
            f"<b>SL:</b> {sl} (Tight)\n"
            f"<b>TP:</b> {tp}\n"
            f"<b>Lot:</b> {lot}\n"
            f"<b>Status:</b> Recovery attempt in progress...\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_exit_continuation(data: Dict) -> str:
        """Format exit continuation notification"""
        symbol = data.get("symbol", "N/A")
        old_direction = data.get("old_direction", "N/A")
        new_direction = data.get("new_direction", "N/A")
        pnl = data.get("pnl", 0)
        closed_id = data.get("closed_id", "N/A")
        
        message = (
            f"<b>REVERSAL EXIT TRIGGERED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Old:</b> {old_direction} -> <b>New:</b> {new_direction}\n"
            f"<b>P&L:</b> ${pnl:+.2f}\n"
            f"<b>Closed:</b> #{closed_id}\n"
            f"<b>Status:</b> Monitoring for continuation...\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    # Signal Event Formatters (4)
    @staticmethod
    def format_signal_received(data: Dict) -> str:
        """Format signal received notification"""
        symbol = data.get("symbol", "N/A")
        direction = data.get("direction", "N/A")
        strategy = data.get("strategy", "N/A")
        entry = data.get("entry", "N/A")
        
        direction_emoji = "" if direction.upper() == "BUY" else ""
        
        message = (
            f"{direction_emoji} <b>SIGNAL RECEIVED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Direction:</b> {direction}\n"
            f"<b>Strategy:</b> {strategy}\n"
            f"<b>Entry:</b> {entry}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_signal_ignored(data: Dict) -> str:
        """Format signal ignored notification"""
        symbol = data.get("symbol", "N/A")
        reason = data.get("reason", "N/A")
        
        message = (
            f"<b>SIGNAL IGNORED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_signal_filtered(data: Dict) -> str:
        """Format signal filtered notification"""
        symbol = data.get("symbol", "N/A")
        filter_type = data.get("filter_type", "Duplicate")
        
        message = (
            f"<b>SIGNAL FILTERED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Filter:</b> {filter_type}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_trend_changed(data: Dict) -> str:
        """Format trend changed notification"""
        symbol = data.get("symbol", "N/A")
        timeframe = data.get("timeframe", "N/A")
        old_trend = data.get("old_trend", "NEUTRAL")
        new_trend = data.get("new_trend", "N/A")
        mode = data.get("mode", "AUTO")
        
        trend_emoji = "" if new_trend.upper() == "BULLISH" else ("" if new_trend.upper() == "BEARISH" else "")
        
        message = (
            f"<b>TREND UPDATE</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Timeframe:</b> {timeframe}\n"
            f"<b>Old:</b> {old_trend}\n"
            f"<b>New:</b> {trend_emoji} {new_trend}\n"
            f"<b>Mode:</b> {mode}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    # Trade Event Formatters (3)
    @staticmethod
    def format_partial_close(data: Dict) -> str:
        """Format partial close notification"""
        symbol = data.get("symbol", "N/A")
        closed_lots = data.get("closed_lots", 0)
        remaining_lots = data.get("remaining_lots", 0)
        pnl = data.get("pnl", 0)
        
        message = (
            f"<b>PARTIAL CLOSE</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Closed:</b> {closed_lots} lots\n"
            f"<b>Remaining:</b> {remaining_lots} lots\n"
            f"<b>P&L:</b> ${pnl:+.2f}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_manual_exit(data: Dict) -> str:
        """Format manual exit notification"""
        symbol = data.get("symbol", "N/A")
        pnl = data.get("pnl", 0)
        exit_price = data.get("exit_price", "N/A")
        trade_id = data.get("trade_id", "N/A")
        
        emoji = "" if pnl >= 0 else ""
        
        message = (
            f"{emoji} <b>MANUAL EXIT</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>P&L:</b> ${pnl:+.2f}\n"
            f"<b>Exit Price:</b> {exit_price}\n"
            f"<b>Reason:</b> Manual close\n"
            f"<b>Trade #:</b> {trade_id}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_reversal_exit(data: Dict) -> str:
        """Format reversal exit notification"""
        symbol = data.get("symbol", "N/A")
        old_direction = data.get("old_direction", "N/A")
        new_direction = data.get("new_direction", "N/A")
        pnl = data.get("pnl", 0)
        closed_id = data.get("closed_id", "N/A")
        
        message = (
            f"<b>REVERSAL EXIT TRIGGERED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Old:</b> {old_direction} -> <b>New:</b> {new_direction}\n"
            f"<b>P&L:</b> ${pnl:+.2f}\n"
            f"<b>Closed:</b> #{closed_id}\n"
            f"<b>Status:</b> Monitoring for continuation...\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    # System Event Formatters (6)
    @staticmethod
    def format_mt5_connected(data: Dict) -> str:
        """Format MT5 connected notification"""
        account = data.get("account", "N/A")
        server = data.get("server", "N/A")
        
        message = (
            f"<b>MT5 CONNECTED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Account:</b> {account}\n"
            f"<b>Server:</b> {server}\n"
            f"<b>Status:</b> Connected\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_lifetime_loss_limit(data: Dict) -> str:
        """Format lifetime loss limit notification"""
        total_loss = data.get("total_loss", 0)
        limit = data.get("limit", 0)
        
        message = (
            f"<b>LIFETIME LOSS LIMIT REACHED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Total Loss:</b> ${total_loss:.2f}\n"
            f"<b>Limit:</b> ${limit:.2f}\n"
            f"<b>Status:</b> TRADING STOPPED\n"
            f"<b>Action:</b> Manual intervention required\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_daily_loss_warning(data: Dict) -> str:
        """Format daily loss warning notification"""
        current_loss = data.get("current_loss", 0)
        daily_limit = data.get("daily_limit", 0)
        remaining = data.get("remaining", 0)
        percentage = data.get("percentage", 0)
        
        message = (
            f"<b>DAILY LOSS APPROACHING LIMIT</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Current Loss:</b> ${current_loss:.2f}\n"
            f"<b>Daily Limit:</b> ${daily_limit:.2f}\n"
            f"<b>Remaining:</b> ${remaining:.2f} ({percentage:.0f}%)\n"
            f"<b>Warning:</b> Trade cautiously!\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_config_error(data: Dict) -> str:
        """Format config error notification"""
        error = data.get("error", "Unknown error")
        details = data.get("details", "No details available")
        
        message = (
            f"<b>CONFIGURATION ERROR</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Error:</b> {error}\n"
            f"<b>Details:</b> {details}\n"
            f"<b>Action:</b> Please check config.json and restart\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_database_error(data: Dict) -> str:
        """Format database error notification"""
        operation = data.get("operation", "Unknown")
        error = data.get("error", "Unknown error")
        
        message = (
            f"<b>DATABASE ERROR</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Operation:</b> {operation}\n"
            f"<b>Error:</b> {error}\n"
            f"<b>Action:</b> Check logs for details\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_order_failed(data: Dict) -> str:
        """Format order failed notification"""
        symbol = data.get("symbol", "N/A")
        reason = data.get("reason", "Unknown")
        
        message = (
            f"<b>ORDER PLACEMENT FAILED</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Action:</b> Trade cancelled\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    # Session Event Formatters (4)
    @staticmethod
    def format_session_toggle(data: Dict) -> str:
        """Format session toggle notification"""
        session = data.get("session", "N/A")
        enabled = data.get("enabled", False)
        status = "ENABLED" if enabled else "DISABLED"
        
        message = (
            f"<b>SESSION UPDATE</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Session:</b> {session}\n"
            f"<b>Status:</b> {status}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_symbol_toggle(data: Dict) -> str:
        """Format symbol toggle notification"""
        session = data.get("session", "N/A")
        symbol = data.get("symbol", "N/A")
        enabled = data.get("enabled", False)
        status = "ENABLED" if enabled else "DISABLED"
        
        message = (
            f"<b>SYMBOL UPDATE</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Session:</b> {session}\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Status:</b> {status}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_time_adjustment(data: Dict) -> str:
        """Format time adjustment notification"""
        session = data.get("session", "N/A")
        adjustment_type = data.get("type", "Start")
        adjustment = data.get("adjustment", "+30")
        new_time = data.get("new_time", "N/A")
        
        message = (
            f"<b>TIME ADJUSTMENT</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Session:</b> {session}\n"
            f"<b>{adjustment_type} Time:</b> {adjustment} minutes\n"
            f"<b>New Time:</b> {new_time} UTC\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_force_close_toggle(data: Dict) -> str:
        """Format force close toggle notification"""
        session = data.get("session", "N/A")
        enabled = data.get("enabled", False)
        status = "ENABLED" if enabled else "DISABLED"
        
        message = (
            f"<b>FORCE CLOSE UPDATE</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Session:</b> {session}\n"
            f"<b>Force Close:</b> {status}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    # Voice Alert Formatters (5)
    @staticmethod
    def format_voice_trade_entry(data: Dict) -> str:
        """Format voice trade entry notification"""
        symbol = data.get("symbol", "N/A")
        direction = data.get("direction", "N/A")
        price = data.get("price", "N/A")
        
        message = f"New trade opened. {symbol} {direction} at {price}"
        return message
    
    @staticmethod
    def format_voice_tp_hit(data: Dict) -> str:
        """Format voice TP hit notification"""
        symbol = data.get("symbol", "N/A")
        profit = data.get("profit", 0)
        
        message = f"Take profit hit. {symbol} profit {profit:.2f} dollars"
        return message
    
    @staticmethod
    def format_voice_sl_hit(data: Dict) -> str:
        """Format voice SL hit notification"""
        symbol = data.get("symbol", "N/A")
        loss = data.get("loss", 0)
        
        message = f"Stop loss hit. {symbol} loss {abs(loss):.2f} dollars"
        return message
    
    @staticmethod
    def format_voice_risk_limit(data: Dict) -> str:
        """Format voice risk limit notification"""
        limit_type = data.get("limit_type", "Daily")
        
        message = f"Warning. {limit_type} loss limit reached. Trading paused."
        return message
    
    @staticmethod
    def format_voice_recovery(data: Dict) -> str:
        """Format voice recovery notification"""
        symbol = data.get("symbol", "N/A")
        
        message = f"Recovery attempt started for {symbol}"
        return message
    
    # Dashboard Formatters (2)
    @staticmethod
    def format_dashboard_update(data: Dict) -> str:
        """Format dashboard update notification"""
        balance = data.get("balance", 0)
        open_trades = data.get("open_trades", 0)
        live_pnl = data.get("live_pnl", 0)
        today_pnl = data.get("today_pnl", 0)
        trades_today = data.get("trades_today", 0)
        
        pnl_emoji = "" if live_pnl >= 0 else ""
        
        message = (
            f"<b>ZEPIX TRADING BOT DASHBOARD</b>\n"
            f"{'=' * 30}\n\n"
            f"<b>LIVE STATUS</b>\n"
            f"  Bot: RUNNING\n"
            f"  Balance: ${balance:,.2f}\n"
            f"  Open Trades: {open_trades}\n"
            f"  Live PnL: {pnl_emoji}${live_pnl:+.2f}\n\n"
            f"<b>TODAY'S PERFORMANCE</b>\n"
            f"  Net PnL: ${today_pnl:+.2f}\n"
            f"  Trades Today: {trades_today}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        return message
    
    @staticmethod
    def format_autonomous_dashboard(data: Dict) -> str:
        """Format autonomous dashboard notification"""
        status = data.get("status", "RUNNING")
        daily_recoveries = data.get("daily_recoveries", 0)
        max_recoveries = data.get("max_recoveries", 10)
        active_monitors = data.get("active_monitors", 0)
        tp_continuation = data.get("tp_continuation", True)
        sl_hunt_recovery = data.get("sl_hunt_recovery", True)
        exit_continuation = data.get("exit_continuation", True)
        
        message = (
            f"<b>AUTONOMOUS DASHBOARD</b>\n"
            f"{'=' * 24}\n\n"
            f"<b>Status:</b> {status}\n"
            f"<b>Daily Recoveries:</b> {daily_recoveries}/{max_recoveries}\n"
            f"<b>Active Monitors:</b> {active_monitors}\n\n"
            f"<b>Sub-Systems:</b>\n"
            f"  Profit Protection: Active\n"
            f"  SL Optimizer: Active\n"
            f"  Recovery Windows: Active\n\n"
            f"<b>Active Configuration:</b>\n"
            f"  TP Continuation: {'ON' if tp_continuation else 'OFF'}\n"
            f"  SL Hunt Recovery: {'ON' if sl_hunt_recovery else 'OFF'}\n"
            f"  Exit Continuation: {'ON' if exit_continuation else 'OFF'}\n"
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
    
    # Register V6 formatters (NEW - Telegram V5 Upgrade)
    router.register_formatter(NotificationType.V6_ENTRY_15M, NotificationFormatter.format_v6_entry)
    router.register_formatter(NotificationType.V6_ENTRY_30M, NotificationFormatter.format_v6_entry)
    router.register_formatter(NotificationType.V6_ENTRY_1H, NotificationFormatter.format_v6_entry)
    router.register_formatter(NotificationType.V6_ENTRY_4H, NotificationFormatter.format_v6_entry)
    router.register_formatter(NotificationType.V6_EXIT, NotificationFormatter.format_v6_exit)
    router.register_formatter(NotificationType.V6_TP_HIT, NotificationFormatter.format_v6_tp_hit)
    router.register_formatter(NotificationType.V6_SL_HIT, NotificationFormatter.format_v6_sl_hit)
    router.register_formatter(NotificationType.V6_TIMEFRAME_ENABLED, NotificationFormatter.format_v6_timeframe_toggle)
    router.register_formatter(NotificationType.V6_TIMEFRAME_DISABLED, NotificationFormatter.format_v6_timeframe_toggle)
    router.register_formatter(NotificationType.V6_DAILY_SUMMARY, NotificationFormatter.format_v6_daily_summary)
    router.register_formatter(NotificationType.V6_SIGNAL, NotificationFormatter.format_v6_signal)
    
    # ==================== NEW FORMATTER REGISTRATIONS (34 total) ====================
    
    # Autonomous System Formatters (5)
    router.register_formatter(NotificationType.TP_CONTINUATION, NotificationFormatter.format_tp_continuation)
    router.register_formatter(NotificationType.SL_HUNT_ACTIVATED, NotificationFormatter.format_sl_hunt_activated)
    router.register_formatter(NotificationType.RECOVERY_SUCCESS, NotificationFormatter.format_recovery_success)
    router.register_formatter(NotificationType.RECOVERY_FAILED, NotificationFormatter.format_recovery_failed)
    router.register_formatter(NotificationType.PROFIT_ORDER_PROTECTION, NotificationFormatter.format_profit_order_protection)
    
    # Re-entry System Formatters (5)
    router.register_formatter(NotificationType.TP_REENTRY_STARTED, NotificationFormatter.format_tp_reentry_started)
    router.register_formatter(NotificationType.TP_REENTRY_EXECUTED, NotificationFormatter.format_tp_reentry_executed)
    router.register_formatter(NotificationType.TP_REENTRY_COMPLETED, NotificationFormatter.format_tp_reentry_completed)
    router.register_formatter(NotificationType.SL_HUNT_RECOVERY, NotificationFormatter.format_sl_hunt_recovery)
    router.register_formatter(NotificationType.EXIT_CONTINUATION, NotificationFormatter.format_exit_continuation)
    
    # Signal Event Formatters (4)
    router.register_formatter(NotificationType.SIGNAL_RECEIVED, NotificationFormatter.format_signal_received)
    router.register_formatter(NotificationType.SIGNAL_IGNORED, NotificationFormatter.format_signal_ignored)
    router.register_formatter(NotificationType.SIGNAL_FILTERED, NotificationFormatter.format_signal_filtered)
    router.register_formatter(NotificationType.TREND_CHANGED, NotificationFormatter.format_trend_changed)
    
    # Trade Event Formatters (3)
    router.register_formatter(NotificationType.PARTIAL_CLOSE, NotificationFormatter.format_partial_close)
    router.register_formatter(NotificationType.MANUAL_EXIT, NotificationFormatter.format_manual_exit)
    router.register_formatter(NotificationType.REVERSAL_EXIT, NotificationFormatter.format_reversal_exit)
    
    # System Event Formatters (6)
    router.register_formatter(NotificationType.MT5_CONNECTED, NotificationFormatter.format_mt5_connected)
    router.register_formatter(NotificationType.LIFETIME_LOSS_LIMIT, NotificationFormatter.format_lifetime_loss_limit)
    router.register_formatter(NotificationType.DAILY_LOSS_WARNING, NotificationFormatter.format_daily_loss_warning)
    router.register_formatter(NotificationType.CONFIG_ERROR, NotificationFormatter.format_config_error)
    router.register_formatter(NotificationType.DATABASE_ERROR, NotificationFormatter.format_database_error)
    router.register_formatter(NotificationType.ORDER_FAILED, NotificationFormatter.format_order_failed)
    
    # Session Event Formatters (4)
    router.register_formatter(NotificationType.SESSION_TOGGLE, NotificationFormatter.format_session_toggle)
    router.register_formatter(NotificationType.SYMBOL_TOGGLE, NotificationFormatter.format_symbol_toggle)
    router.register_formatter(NotificationType.TIME_ADJUSTMENT, NotificationFormatter.format_time_adjustment)
    router.register_formatter(NotificationType.FORCE_CLOSE_TOGGLE, NotificationFormatter.format_force_close_toggle)
    
    # Voice Alert Formatters (5)
    router.register_formatter(NotificationType.VOICE_TRADE_ENTRY, NotificationFormatter.format_voice_trade_entry)
    router.register_formatter(NotificationType.VOICE_TP_HIT, NotificationFormatter.format_voice_tp_hit)
    router.register_formatter(NotificationType.VOICE_SL_HIT, NotificationFormatter.format_voice_sl_hit)
    router.register_formatter(NotificationType.VOICE_RISK_LIMIT, NotificationFormatter.format_voice_risk_limit)
    router.register_formatter(NotificationType.VOICE_RECOVERY, NotificationFormatter.format_voice_recovery)
    
    # Dashboard Formatters (2)
    router.register_formatter(NotificationType.DASHBOARD_UPDATE, NotificationFormatter.format_dashboard_update)
    router.register_formatter(NotificationType.AUTONOMOUS_DASHBOARD, NotificationFormatter.format_autonomous_dashboard)
    
    return router
