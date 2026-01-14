"""
Controller Bot - Handles system commands and admin functions

This bot handles all slash commands and system control.
It delegates to the existing telegram_bot_fixed.py for command handling.

Version: 1.1.0
Date: 2026-01-14

Updates:
- v1.1.0: Added /health and /version commands for plugin monitoring
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

from .base_telegram_bot import BaseTelegramBot

logger = logging.getLogger(__name__)


class ControllerBot(BaseTelegramBot):
    """
    Controller Bot for system commands and admin functions.
    
    Responsibilities:
    - All slash commands (/start, /status, /pause, etc.)
    - Bot configuration
    - Emergency controls
    - System status queries
    - Manual trade placement
    """
    
    def __init__(self, token: str, chat_id: str = None):
        super().__init__(token, chat_id, bot_name="ControllerBot")
        
        self._command_handlers: Dict[str, Callable] = {}
        self._trading_engine = None
        self._risk_manager = None
        self._legacy_bot = None
        
        # Health monitoring and versioning (Batch 11)
        self._health_monitor = None
        self._version_registry = None
        
        logger.info("[ControllerBot] Initialized")
    
    def set_dependencies(
        self,
        trading_engine=None,
        risk_manager=None,
        legacy_bot=None,
        health_monitor=None,
        version_registry=None
    ):
        """
        Set dependencies for command handling
        
        Args:
            trading_engine: TradingEngine instance
            risk_manager: RiskManager instance
            legacy_bot: Legacy TelegramBot instance for command delegation
            health_monitor: PluginHealthMonitor instance (Batch 11)
            version_registry: VersionedPluginRegistry instance (Batch 11)
        """
        self._trading_engine = trading_engine
        self._risk_manager = risk_manager
        self._legacy_bot = legacy_bot
        self._health_monitor = health_monitor
        self._version_registry = version_registry
        
        if legacy_bot:
            logger.info("[ControllerBot] Legacy bot connected for command delegation")
        
        if health_monitor:
            logger.info("[ControllerBot] Health monitor connected")
        
        if version_registry:
            logger.info("[ControllerBot] Version registry connected")
    
    def register_command(self, command: str, handler: Callable):
        """
        Register a command handler
        
        Args:
            command: Command string (e.g., '/status')
            handler: Handler function
        """
        self._command_handlers[command] = handler
        logger.debug(f"[ControllerBot] Registered command: {command}")
    
    def handle_command(self, command: str, message: Dict) -> bool:
        """
        Handle an incoming command
        
        Args:
            command: Command string
            message: Full message dict from Telegram
        
        Returns:
            True if command was handled
        """
        if self._legacy_bot and hasattr(self._legacy_bot, 'command_handlers'):
            if command in self._legacy_bot.command_handlers:
                try:
                    self._legacy_bot.command_handlers[command](message)
                    return True
                except Exception as e:
                    logger.error(f"[ControllerBot] Legacy handler error for {command}: {e}")
                    return False
        
        if command in self._command_handlers:
            try:
                self._command_handlers[command](message)
                return True
            except Exception as e:
                logger.error(f"[ControllerBot] Handler error for {command}: {e}")
                return False
        
        logger.warning(f"[ControllerBot] Unknown command: {command}")
        return False
    
    def send_status_response(self, status_data: Dict) -> Optional[int]:
        """
        Send formatted status response
        
        Args:
            status_data: Dict with status information
        
        Returns:
            Message ID if successful
        """
        message = self._format_status_message(status_data)
        return self.send_message(message)
    
    def _format_status_message(self, status_data: Dict) -> str:
        """Format status data into readable message"""
        bot_status = "🟢 Active" if status_data.get("is_active", False) else "🔴 Paused"
        
        return (
            f"🤖 <b>BOT STATUS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Status: {bot_status}\n"
            f"Uptime: {status_data.get('uptime', 'N/A')}\n"
            f"Active Plugins: {status_data.get('active_plugins', 0)}\n"
            f"Open Trades: {status_data.get('open_trades', 0)}\n"
            f"Today's P&L: ${status_data.get('daily_pnl', 0):.2f}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Last Update: {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def send_command_response(self, response_text: str, keyboard: Dict = None) -> Optional[int]:
        """
        Send a command response with optional keyboard
        
        Args:
            response_text: Response message
            keyboard: Optional inline keyboard
        
        Returns:
            Message ID if successful
        """
        reply_markup = None
        if keyboard:
            reply_markup = {"inline_keyboard": keyboard}
        
        return self.send_message(response_text, reply_markup=reply_markup)
    
    def send_error_response(self, error_message: str) -> Optional[int]:
        """
        Send an error response
        
        Args:
            error_message: Error description
        
        Returns:
            Message ID if successful
        """
        formatted = f"❌ <b>Error</b>\n\n{error_message}"
        return self.send_message(formatted)
    
    def send_confirmation_request(
        self,
        action: str,
        confirm_callback: str,
        cancel_callback: str = "menu_main"
    ) -> Optional[int]:
        """
        Send a confirmation request with Yes/No buttons
        
        Args:
            action: Action description
            confirm_callback: Callback data for confirmation
            cancel_callback: Callback data for cancellation
        
        Returns:
            Message ID if successful
        """
        keyboard = [
            [
                {"text": "✅ YES", "callback_data": confirm_callback},
                {"text": "❌ CANCEL", "callback_data": cancel_callback}
            ]
        ]
        
        message = (
            f"⚠️ <b>Confirmation Required</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{action}\n\n"
            f"<b>Are you sure?</b>"
        )
        
        return self.send_message(message, reply_markup={"inline_keyboard": keyboard})
    
    # ========================================
    # Health Monitoring Commands (Batch 11)
    # ========================================
    
    def handle_health_command(self, message: Dict = None) -> Optional[int]:
        """
        Handle /health command - Show plugin health dashboard
        
        Args:
            message: Telegram message dict (optional)
        
        Returns:
            Message ID if successful
        """
        if not self._health_monitor:
            return self.send_message(
                "🏥 <b>Health Monitor</b>\n\n"
                "Health monitoring is not configured.\n"
                "Please initialize PluginHealthMonitor first."
            )
        
        try:
            # Get formatted health dashboard
            dashboard_text = self._health_monitor.format_health_dashboard()
            return self.send_message(dashboard_text)
            
        except Exception as e:
            logger.error(f"[ControllerBot] Health command error: {e}")
            return self.send_error_response(f"Failed to get health status: {str(e)}")
    
    def handle_version_command(self, message: Dict = None) -> Optional[int]:
        """
        Handle /version command - Show active plugin versions
        
        Args:
            message: Telegram message dict (optional)
        
        Returns:
            Message ID if successful
        """
        if not self._version_registry:
            return self.send_message(
                "📦 <b>Version Registry</b>\n\n"
                "Version registry is not configured.\n"
                "Please initialize VersionedPluginRegistry first."
            )
        
        try:
            # Get formatted version dashboard
            version_text = self._version_registry.format_version_dashboard()
            return self.send_message(version_text)
            
        except Exception as e:
            logger.error(f"[ControllerBot] Version command error: {e}")
            return self.send_error_response(f"Failed to get version info: {str(e)}")
    
    def handle_upgrade_command(self, message: Dict, args: List[str] = None) -> Optional[int]:
        """
        Handle /upgrade command - Upgrade plugin to specific version
        
        Usage: /upgrade <plugin_id> <version>
        Example: /upgrade combined_v3 3.2.0
        
        Args:
            message: Telegram message dict
            args: Command arguments [plugin_id, version]
        
        Returns:
            Message ID if successful
        """
        if not self._version_registry:
            return self.send_error_response("Version registry not configured")
        
        if not args or len(args) != 2:
            return self.send_message(
                "📦 <b>Upgrade Plugin</b>\n\n"
                "Usage: <code>/upgrade &lt;plugin_id&gt; &lt;version&gt;</code>\n"
                "Example: <code>/upgrade combined_v3 3.2.0</code>"
            )
        
        plugin_id = args[0]
        target_version = args[1]
        
        try:
            success, result_message = self._version_registry.upgrade_plugin(plugin_id, target_version)
            
            if success:
                return self.send_message(f"✅ {result_message}")
            else:
                return self.send_error_response(result_message)
                
        except Exception as e:
            logger.error(f"[ControllerBot] Upgrade command error: {e}")
            return self.send_error_response(f"Upgrade failed: {str(e)}")
    
    def handle_rollback_command(self, message: Dict, args: List[str] = None) -> Optional[int]:
        """
        Handle /rollback command - Rollback plugin to previous version
        
        Usage: /rollback <plugin_id>
        Example: /rollback combined_v3
        
        Args:
            message: Telegram message dict
            args: Command arguments [plugin_id]
        
        Returns:
            Message ID if successful
        """
        if not self._version_registry:
            return self.send_error_response("Version registry not configured")
        
        if not args or len(args) != 1:
            return self.send_message(
                "📦 <b>Rollback Plugin</b>\n\n"
                "Usage: <code>/rollback &lt;plugin_id&gt;</code>\n"
                "Example: <code>/rollback combined_v3</code>"
            )
        
        plugin_id = args[0]
        
        try:
            success, result_message = self._version_registry.rollback_plugin(plugin_id)
            
            if success:
                return self.send_message(f"✅ {result_message}")
            else:
                return self.send_error_response(result_message)
                
        except Exception as e:
            logger.error(f"[ControllerBot] Rollback command error: {e}")
            return self.send_error_response(f"Rollback failed: {str(e)}")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get health summary data (for programmatic access)
        
        Returns:
            Dict with health summary or empty dict if not configured
        """
        if not self._health_monitor:
            return {}
        
        try:
            return self._health_monitor.get_health_summary()
        except Exception as e:
            logger.error(f"[ControllerBot] Get health summary error: {e}")
            return {}
    
    def get_version_summary(self) -> Dict[str, Any]:
        """
        Get version summary data (for programmatic access)
        
        Returns:
            Dict with version summary or empty dict if not configured
        """
        if not self._version_registry:
            return {}
        
        try:
            return self._version_registry.get_version_summary()
        except Exception as e:
            logger.error(f"[ControllerBot] Get version summary error: {e}")
            return {}
