"""
Message Router - Intelligent routing logic for multi-bot system

Routes messages to the appropriate bot based on message type and content.
Supports graceful degradation to single bot mode.

Version: 1.0.0
Date: 2026-01-14
"""

import logging
import re
from typing import Dict, Any, Optional, TYPE_CHECKING
from enum import Enum
from datetime import datetime

if TYPE_CHECKING:
    from .controller_bot import ControllerBot
    from .notification_bot import NotificationBot
    from .analytics_bot import AnalyticsBot

logger = logging.getLogger(__name__)


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
    """
    
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
