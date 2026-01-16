"""
Voice Alert Integration - Bridge between NotificationRouter and VoiceAlertSystem

Integrates the existing VoiceAlertSystem with the new notification routing system.

Features:
- Maps notification types to voice triggers
- Configurable voice enable/disable per notification type
- Priority-based voice alert handling
- Voice text generation for different notification types

Version: 1.0.0
Date: 2026-01-14
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable, Set
from enum import Enum

from .notification_router import NotificationPriority, NotificationType

logger = logging.getLogger(__name__)


class VoiceAlertConfig:
    """Configuration for voice alerts"""
    
    # Default voice triggers by notification type
    DEFAULT_VOICE_TRIGGERS = {
        # Trade Events - Voice enabled
        NotificationType.ENTRY: True,
        NotificationType.EXIT: True,
        NotificationType.TP_HIT: True,
        NotificationType.SL_HIT: True,
        NotificationType.PROFIT_BOOKING: False,
        NotificationType.SL_MODIFIED: False,
        NotificationType.BREAKEVEN: False,
        
        # System Events
        NotificationType.BOT_STARTED: True,
        NotificationType.BOT_STOPPED: True,
        NotificationType.EMERGENCY_STOP: True,
        NotificationType.MT5_DISCONNECT: True,
        NotificationType.MT5_RECONNECT: False,
        NotificationType.DAILY_LOSS_LIMIT: True,
        
        # Plugin Events
        NotificationType.PLUGIN_LOADED: False,
        NotificationType.PLUGIN_ERROR: False,
        NotificationType.CONFIG_RELOAD: False,
        
        # Alert Events
        NotificationType.ALERT_RECEIVED: False,
        NotificationType.ALERT_PROCESSED: False,
        NotificationType.ALERT_IGNORED: False,
        NotificationType.ALERT_ERROR: False,
        
        # Analytics Events
        NotificationType.DAILY_SUMMARY: False,
        NotificationType.WEEKLY_SUMMARY: False,
        NotificationType.PERFORMANCE_REPORT: False,
        NotificationType.RISK_ALERT: True,
        
        # Generic
        NotificationType.INFO: False,
        NotificationType.WARNING: False,
        NotificationType.ERROR: False,
    }
    
    # Priority to AlertPriority mapping (for VoiceAlertSystem)
    PRIORITY_MAPPING = {
        NotificationPriority.CRITICAL: "CRITICAL",
        NotificationPriority.HIGH: "HIGH",
        NotificationPriority.MEDIUM: "MEDIUM",
        NotificationPriority.LOW: "LOW",
        NotificationPriority.INFO: "LOW",
    }


class VoiceTextGenerator:
    """
    Generates voice-friendly text for different notification types.
    
    Voice text should be:
    - Short and concise
    - Easy to understand when spoken
    - Include key information only
    """
    
    @staticmethod
    def generate_entry_voice(data: Dict) -> str:
        """Generate voice text for entry notification"""
        direction = data.get("direction", "trade")
        symbol = data.get("symbol", "unknown")
        entry_price = data.get("entry_price", 0)
        signal_type = data.get("signal_type", "")
        
        text = f"New {direction} trade on {symbol} at {entry_price}."
        if signal_type:
            text += f" Signal: {signal_type}."
        
        return text
    
    @staticmethod
    def generate_exit_voice(data: Dict) -> str:
        """Generate voice text for exit notification"""
        direction = data.get("direction", "trade")
        symbol = data.get("symbol", "unknown")
        profit = data.get("profit", 0)
        
        if profit >= 0:
            return f"{direction} trade on {symbol} closed with profit of {abs(profit):.0f} dollars."
        else:
            return f"{direction} trade on {symbol} closed with loss of {abs(profit):.0f} dollars."
    
    @staticmethod
    def generate_tp_hit_voice(data: Dict) -> str:
        """Generate voice text for TP hit notification"""
        tp_level = data.get("tp_level", 1)
        profit = data.get("profit", 0)
        symbol = data.get("symbol", "")
        
        text = f"Take profit {tp_level} hit"
        if symbol:
            text += f" on {symbol}"
        text += f". Profit: {abs(profit):.0f} dollars."
        
        return text
    
    @staticmethod
    def generate_sl_hit_voice(data: Dict) -> str:
        """Generate voice text for SL hit notification"""
        symbol = data.get("symbol", "unknown")
        loss = abs(data.get("profit", 0))
        
        return f"Stop loss hit on {symbol}. Loss: {loss:.0f} dollars."
    
    @staticmethod
    def generate_emergency_voice(data: Dict) -> str:
        """Generate voice text for emergency notification"""
        reason = data.get("reason", "Emergency alert")
        return f"Emergency alert. {reason}. Immediate attention required."
    
    @staticmethod
    def generate_bot_started_voice(data: Dict) -> str:
        """Generate voice text for bot started notification"""
        return "Zepix Trading Bot has started successfully."
    
    @staticmethod
    def generate_bot_stopped_voice(data: Dict) -> str:
        """Generate voice text for bot stopped notification"""
        reason = data.get("reason", "")
        if reason:
            return f"Zepix Trading Bot has stopped. Reason: {reason}."
        return "Zepix Trading Bot has stopped."
    
    @staticmethod
    def generate_mt5_disconnect_voice(data: Dict) -> str:
        """Generate voice text for MT5 disconnect notification"""
        return "Warning. MetaTrader 5 connection lost. Please check immediately."
    
    @staticmethod
    def generate_daily_loss_limit_voice(data: Dict) -> str:
        """Generate voice text for daily loss limit notification"""
        loss = abs(data.get("loss", 0))
        return f"Daily loss limit reached. Total loss: {loss:.0f} dollars. Trading paused."
    
    @staticmethod
    def generate_risk_alert_voice(data: Dict) -> str:
        """Generate voice text for risk alert notification"""
        message = data.get("message", "Risk threshold exceeded")
        return f"Risk alert. {message}."
    
    @staticmethod
    def generate_generic_voice(data: Dict) -> str:
        """Generate generic voice text"""
        message = data.get("message", "")
        if message:
            # Truncate long messages
            if len(message) > 100:
                message = message[:100] + "..."
            return message
        return "New notification received."


class VoiceAlertIntegration:
    """
    Integrates voice alerts with the notification system.
    
    Acts as a bridge between NotificationRouter and VoiceAlertSystem.
    """
    
    def __init__(self, voice_alert_system=None):
        """
        Initialize VoiceAlertIntegration.
        
        Args:
            voice_alert_system: Instance of VoiceAlertSystem from src/modules/voice_alert_system.py
        """
        self.voice_system = voice_alert_system
        
        # Voice triggers configuration
        self.voice_triggers = VoiceAlertConfig.DEFAULT_VOICE_TRIGGERS.copy()
        
        # Disabled notification types
        self.disabled_types: Set[NotificationType] = set()
        
        # Global voice enable/disable
        self.voice_enabled = True
        
        # Voice text generators
        self.text_generators: Dict[NotificationType, Callable] = {
            NotificationType.ENTRY: VoiceTextGenerator.generate_entry_voice,
            NotificationType.EXIT: VoiceTextGenerator.generate_exit_voice,
            NotificationType.TP_HIT: VoiceTextGenerator.generate_tp_hit_voice,
            NotificationType.SL_HIT: VoiceTextGenerator.generate_sl_hit_voice,
            NotificationType.EMERGENCY_STOP: VoiceTextGenerator.generate_emergency_voice,
            NotificationType.BOT_STARTED: VoiceTextGenerator.generate_bot_started_voice,
            NotificationType.BOT_STOPPED: VoiceTextGenerator.generate_bot_stopped_voice,
            NotificationType.MT5_DISCONNECT: VoiceTextGenerator.generate_mt5_disconnect_voice,
            NotificationType.DAILY_LOSS_LIMIT: VoiceTextGenerator.generate_daily_loss_limit_voice,
            NotificationType.RISK_ALERT: VoiceTextGenerator.generate_risk_alert_voice,
        }
        
        # Statistics
        self.stats = {
            "total_voice_alerts": 0,
            "by_type": {},
            "by_priority": {},
            "skipped_disabled": 0,
            "skipped_no_trigger": 0,
            "errors": 0
        }
    
    def set_voice_system(self, voice_system):
        """
        Set the voice alert system.
        
        Args:
            voice_system: Instance of VoiceAlertSystem
        """
        self.voice_system = voice_system
        logger.info("Voice alert system connected")
    
    def enable_voice(self):
        """Enable voice alerts globally"""
        self.voice_enabled = True
        logger.info("Voice alerts enabled")
    
    def disable_voice(self):
        """Disable voice alerts globally"""
        self.voice_enabled = False
        logger.info("Voice alerts disabled")
    
    def enable_type(self, notification_type: NotificationType):
        """Enable voice for a specific notification type"""
        self.voice_triggers[notification_type] = True
        self.disabled_types.discard(notification_type)
        logger.info(f"Voice enabled for: {notification_type.value}")
    
    def disable_type(self, notification_type: NotificationType):
        """Disable voice for a specific notification type"""
        self.voice_triggers[notification_type] = False
        self.disabled_types.add(notification_type)
        logger.info(f"Voice disabled for: {notification_type.value}")
    
    def register_text_generator(self, notification_type: NotificationType, generator: Callable):
        """
        Register a custom voice text generator.
        
        Args:
            notification_type: Type of notification
            generator: Function that takes data dict and returns voice text
        """
        self.text_generators[notification_type] = generator
    
    def should_trigger_voice(
        self,
        notification_type: NotificationType,
        priority: NotificationPriority
    ) -> bool:
        """
        Check if voice should be triggered for this notification.
        
        Args:
            notification_type: Type of notification
            priority: Priority level
            
        Returns:
            True if voice should be triggered
        """
        # Check global enable
        if not self.voice_enabled:
            return False
        
        # Check if voice system is available
        if not self.voice_system:
            return False
        
        # CRITICAL priority always triggers voice
        if priority == NotificationPriority.CRITICAL:
            return True
        
        # Check if type is disabled
        if notification_type in self.disabled_types:
            return False
        
        # Check voice trigger configuration
        return self.voice_triggers.get(notification_type, False)
    
    def generate_voice_text(
        self,
        notification_type: NotificationType,
        data: Dict
    ) -> str:
        """
        Generate voice text for a notification.
        
        Args:
            notification_type: Type of notification
            data: Notification data
            
        Returns:
            Voice-friendly text string
        """
        generator = self.text_generators.get(notification_type)
        
        if generator:
            try:
                return generator(data)
            except Exception as e:
                logger.error(f"Voice text generator error: {e}")
        
        # Fallback to generic generator
        return VoiceTextGenerator.generate_generic_voice(data)
    
    def trigger_voice_alert(
        self,
        notification_type: NotificationType,
        priority: NotificationPriority,
        data: Dict,
        custom_text: Optional[str] = None
    ) -> bool:
        """
        Trigger a voice alert.
        
        Args:
            notification_type: Type of notification
            priority: Priority level
            data: Notification data
            custom_text: Optional custom voice text
            
        Returns:
            True if voice alert was triggered
        """
        # Check if should trigger
        if not self.should_trigger_voice(notification_type, priority):
            if notification_type in self.disabled_types:
                self.stats["skipped_disabled"] += 1
            else:
                self.stats["skipped_no_trigger"] += 1
            return False
        
        # Generate voice text
        voice_text = custom_text or self.generate_voice_text(notification_type, data)
        
        # Map priority to VoiceAlertSystem priority
        alert_priority = VoiceAlertConfig.PRIORITY_MAPPING.get(priority, "MEDIUM")
        
        try:
            # Import AlertPriority from voice_alert_system
            # This is done dynamically to avoid circular imports
            from src.modules.voice_alert_system import AlertPriority
            
            # Convert string to AlertPriority enum
            voice_priority = AlertPriority(alert_priority)
            
            # Send voice alert
            import asyncio
            
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                # We're in async context, create task
                asyncio.create_task(
                    self.voice_system.send_voice_alert(voice_text, voice_priority)
                )
            except RuntimeError:
                # No running loop, run synchronously
                asyncio.run(
                    self.voice_system.send_voice_alert(voice_text, voice_priority)
                )
            
            # Update statistics
            self._update_stats(notification_type, priority)
            
            logger.info(f"Voice alert triggered: {notification_type.value} ({priority.name})")
            return True
            
        except ImportError:
            logger.warning("VoiceAlertSystem not available, using fallback")
            return self._fallback_voice_alert(voice_text)
        except Exception as e:
            logger.error(f"Voice alert error: {e}")
            self.stats["errors"] += 1
            return False
    
    def _fallback_voice_alert(self, text: str) -> bool:
        """
        Fallback voice alert using simple print/log.
        
        Args:
            text: Voice text
            
        Returns:
            True (always succeeds as fallback)
        """
        logger.info(f"[VOICE FALLBACK] {text}")
        return True
    
    def _update_stats(self, notification_type: NotificationType, priority: NotificationPriority):
        """Update statistics"""
        self.stats["total_voice_alerts"] += 1
        
        # By type
        type_key = notification_type.value
        self.stats["by_type"][type_key] = self.stats["by_type"].get(type_key, 0) + 1
        
        # By priority
        priority_key = priority.name
        self.stats["by_priority"][priority_key] = self.stats["by_priority"].get(priority_key, 0) + 1
    
    def get_stats(self) -> Dict:
        """Get voice alert statistics"""
        return {
            "enabled": self.voice_enabled,
            "voice_system_connected": self.voice_system is not None,
            "stats": self.stats.copy(),
            "disabled_types": [t.value for t in self.disabled_types],
            "enabled_types": [
                t.value for t, enabled in self.voice_triggers.items()
                if enabled and t not in self.disabled_types
            ]
        }
    
    def get_voice_callback(self) -> Callable:
        """
        Get a callback function for use with NotificationRouter.
        
        Returns:
            Callback function that triggers voice alerts
        """
        def voice_callback(message: str, priority: NotificationPriority):
            """Voice callback for NotificationRouter"""
            # Use generic notification type for direct message calls
            self.trigger_voice_alert(
                NotificationType.INFO,
                priority,
                {"message": message},
                custom_text=message
            )
        
        return voice_callback


def create_voice_integration(voice_alert_system=None) -> VoiceAlertIntegration:
    """
    Create a VoiceAlertIntegration instance.
    
    Args:
        voice_alert_system: Optional VoiceAlertSystem instance
        
    Returns:
        Configured VoiceAlertIntegration
    """
    integration = VoiceAlertIntegration(voice_alert_system)
    
    logger.info("Voice alert integration created")
    return integration


def integrate_with_router(
    router,
    voice_alert_system=None
) -> VoiceAlertIntegration:
    """
    Integrate voice alerts with a NotificationRouter.
    
    Args:
        router: NotificationRouter instance
        voice_alert_system: Optional VoiceAlertSystem instance
        
    Returns:
        VoiceAlertIntegration instance
    """
    integration = create_voice_integration(voice_alert_system)
    
    # Set the voice callback on the router
    router.voice_callback = integration.get_voice_callback()
    
    logger.info("Voice integration connected to notification router")
    return integration
