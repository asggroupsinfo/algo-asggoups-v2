"""
V6 Command Handlers - Telegram V5 Upgrade

This module provides command handlers for V6 Price Action plugin control.
Implements /tf15m_on, /tf30m_on, /tf1h_on, /tf4h_on, /v6_status, /v6_control commands.

Version: 1.0.0
Date: 2026-01-19
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class V6CommandHandlers:
    """
    Command handlers for V6 Price Action plugin control.
    
    Provides handlers for:
    - /v6_status: Show V6 system status
    - /v6_control: Show V6 control menu
    - /tf15m_on, /tf15m_off: Enable/disable 15M timeframe
    - /tf30m_on, /tf30m_off: Enable/disable 30M timeframe
    - /tf1h_on, /tf1h_off: Enable/disable 1H timeframe
    - /tf4h_on, /tf4h_off: Enable/disable 4H timeframe
    """
    
    # V6 Timeframes
    V6_TIMEFRAMES = ["15m", "30m", "1h", "4h"]
    
    def __init__(self, telegram_bot, config: Dict[str, Any] = None):
        """
        Initialize V6CommandHandlers.
        
        Args:
            telegram_bot: Telegram bot instance
            config: Bot configuration dictionary
        """
        self._bot = telegram_bot
        self._config = config or {}
        logger.info("[V6CommandHandlers] Initialized")
    
    def set_config(self, config: Dict[str, Any]):
        """Update configuration reference"""
        self._config = config
    
    def _get_v6_config(self) -> Dict[str, Any]:
        """Get V6 plugin configuration"""
        return self._config.get("v6_price_action", {})
    
    def _get_timeframe_config(self, timeframe: str) -> Dict[str, Any]:
        """Get configuration for a specific timeframe"""
        v6_config = self._get_v6_config()
        return v6_config.get("timeframes", {}).get(timeframe, {})
    
    def _is_v6_enabled(self) -> bool:
        """Check if V6 system is enabled"""
        v6_config = self._get_v6_config()
        return v6_config.get("enabled", False)
    
    def _is_timeframe_enabled(self, timeframe: str) -> bool:
        """Check if a specific timeframe is enabled"""
        tf_config = self._get_timeframe_config(timeframe)
        return tf_config.get("enabled", False)
    
    def _set_timeframe_enabled(self, timeframe: str, enabled: bool) -> bool:
        """
        Set timeframe enabled state.
        
        Args:
            timeframe: Timeframe to set (15m, 30m, 1h, 4h)
            enabled: True to enable, False to disable
        
        Returns:
            True if successful
        """
        try:
            # Ensure v6_price_action config exists
            if "v6_price_action" not in self._config:
                self._config["v6_price_action"] = {"enabled": True, "timeframes": {}}
            
            v6_config = self._config["v6_price_action"]
            
            # Ensure timeframes config exists
            if "timeframes" not in v6_config:
                v6_config["timeframes"] = {}
            
            # Ensure specific timeframe config exists
            if timeframe not in v6_config["timeframes"]:
                v6_config["timeframes"][timeframe] = {
                    "enabled": False,
                    "lot_multiplier": 1.0,
                    "sl_multiplier": 1.0,
                    "tp_multiplier": 1.0
                }
            
            # Set enabled state
            v6_config["timeframes"][timeframe]["enabled"] = enabled
            
            logger.info(f"[V6CommandHandlers] Timeframe {timeframe} {'enabled' if enabled else 'disabled'}")
            return True
        except Exception as e:
            logger.error(f"[V6CommandHandlers] Error setting timeframe {timeframe}: {e}")
            return False
    
    def _format_status_message(self) -> str:
        """Format V6 status message"""
        v6_config = self._get_v6_config()
        system_enabled = v6_config.get("enabled", False)
        
        # Build status message
        lines = [
            "📊 <b>V6 PRICE ACTION STATUS</b>",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            f"🔌 <b>System:</b> {'✅ ENABLED' if system_enabled else '❌ DISABLED'}",
            "",
            "⏱️ <b>Timeframes:</b>",
        ]
        
        # Add timeframe status
        for tf in self.V6_TIMEFRAMES:
            tf_config = self._get_timeframe_config(tf)
            enabled = tf_config.get("enabled", False)
            status = "✅" if enabled else "❌"
            
            # Get stats if available
            trades = tf_config.get("total_trades", 0)
            win_rate = tf_config.get("win_rate", 0)
            pnl = tf_config.get("total_pnl", 0)
            
            lines.append(f"  {status} <b>{tf.upper()}</b>: {trades} trades | {win_rate:.1f}% WR | ${pnl:.2f}")
        
        lines.extend([
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            f"<i>Updated: {datetime.now().strftime('%H:%M:%S')}</i>"
        ])
        
        return "\n".join(lines)
    
    def _send_response(self, text: str, message_id: int = None):
        """Send response message"""
        try:
            if message_id and hasattr(self._bot, 'edit_message'):
                self._bot.edit_message(text, message_id)
            elif hasattr(self._bot, 'send_message'):
                self._bot.send_message(text)
            else:
                logger.warning("[V6CommandHandlers] No send method available")
        except Exception as e:
            logger.error(f"[V6CommandHandlers] Error sending response: {e}")
    
    # =========================================================================
    # COMMAND HANDLERS
    # =========================================================================
    
    def handle_v6_status(self, message: Dict[str, Any] = None):
        """
        Handle /v6_status command.
        Shows current V6 system status.
        """
        logger.info("[V6CommandHandlers] Handling /v6_status")
        
        status_text = self._format_status_message()
        self._send_response(status_text)
    
    def handle_v6_control(self, message: Dict[str, Any] = None):
        """
        Handle /v6_control command.
        Shows V6 control menu.
        """
        logger.info("[V6CommandHandlers] Handling /v6_control")
        
        # Delegate to menu manager if available
        if hasattr(self._bot, 'menu_manager') and self._bot.menu_manager:
            user_id = message.get("from", {}).get("id") if message else None
            message_id = message.get("message_id") if message else None
            self._bot.menu_manager.show_v6_menu(user_id, message_id)
        else:
            # Fallback to status display
            self.handle_v6_status(message)
    
    def handle_v6_tf15m_on(self, message: Dict[str, Any] = None):
        """Handle /tf15m_on command - Enable V6 15M timeframe"""
        logger.info("[V6CommandHandlers] Handling /tf15m_on")
        
        if self._set_timeframe_enabled("15m", True):
            self._send_response("✅ <b>V6 15M Timeframe ENABLED</b>\n\nV6 Price Action will now analyze 15-minute charts.")
        else:
            self._send_response("❌ <b>Error enabling 15M timeframe</b>\n\nPlease try again.")
    
    def handle_v6_tf15m_off(self, message: Dict[str, Any] = None):
        """Handle /tf15m_off command - Disable V6 15M timeframe"""
        logger.info("[V6CommandHandlers] Handling /tf15m_off")
        
        if self._set_timeframe_enabled("15m", False):
            self._send_response("❌ <b>V6 15M Timeframe DISABLED</b>\n\nV6 Price Action will no longer analyze 15-minute charts.")
        else:
            self._send_response("❌ <b>Error disabling 15M timeframe</b>\n\nPlease try again.")
    
    def handle_v6_tf30m_on(self, message: Dict[str, Any] = None):
        """Handle /tf30m_on command - Enable V6 30M timeframe"""
        logger.info("[V6CommandHandlers] Handling /tf30m_on")
        
        if self._set_timeframe_enabled("30m", True):
            self._send_response("✅ <b>V6 30M Timeframe ENABLED</b>\n\nV6 Price Action will now analyze 30-minute charts.")
        else:
            self._send_response("❌ <b>Error enabling 30M timeframe</b>\n\nPlease try again.")
    
    def handle_v6_tf30m_off(self, message: Dict[str, Any] = None):
        """Handle /tf30m_off command - Disable V6 30M timeframe"""
        logger.info("[V6CommandHandlers] Handling /tf30m_off")
        
        if self._set_timeframe_enabled("30m", False):
            self._send_response("❌ <b>V6 30M Timeframe DISABLED</b>\n\nV6 Price Action will no longer analyze 30-minute charts.")
        else:
            self._send_response("❌ <b>Error disabling 30M timeframe</b>\n\nPlease try again.")
    
    def handle_v6_tf1h_on(self, message: Dict[str, Any] = None):
        """Handle /tf1h_on command - Enable V6 1H timeframe"""
        logger.info("[V6CommandHandlers] Handling /tf1h_on")
        
        if self._set_timeframe_enabled("1h", True):
            self._send_response("✅ <b>V6 1H Timeframe ENABLED</b>\n\nV6 Price Action will now analyze 1-hour charts.")
        else:
            self._send_response("❌ <b>Error enabling 1H timeframe</b>\n\nPlease try again.")
    
    def handle_v6_tf1h_off(self, message: Dict[str, Any] = None):
        """Handle /tf1h_off command - Disable V6 1H timeframe"""
        logger.info("[V6CommandHandlers] Handling /tf1h_off")
        
        if self._set_timeframe_enabled("1h", False):
            self._send_response("❌ <b>V6 1H Timeframe DISABLED</b>\n\nV6 Price Action will no longer analyze 1-hour charts.")
        else:
            self._send_response("❌ <b>Error disabling 1H timeframe</b>\n\nPlease try again.")
    
    def handle_v6_tf4h_on(self, message: Dict[str, Any] = None):
        """Handle /tf4h_on command - Enable V6 4H timeframe"""
        logger.info("[V6CommandHandlers] Handling /tf4h_on")
        
        if self._set_timeframe_enabled("4h", True):
            self._send_response("✅ <b>V6 4H Timeframe ENABLED</b>\n\nV6 Price Action will now analyze 4-hour charts.")
        else:
            self._send_response("❌ <b>Error enabling 4H timeframe</b>\n\nPlease try again.")
    
    def handle_v6_tf4h_off(self, message: Dict[str, Any] = None):
        """Handle /tf4h_off command - Disable V6 4H timeframe"""
        logger.info("[V6CommandHandlers] Handling /tf4h_off")
        
        if self._set_timeframe_enabled("4h", False):
            self._send_response("❌ <b>V6 4H Timeframe DISABLED</b>\n\nV6 Price Action will no longer analyze 4-hour charts.")
        else:
            self._send_response("❌ <b>Error disabling 4H timeframe</b>\n\nPlease try again.")
    
    # =========================================================================
    # CALLBACK HANDLERS
    # =========================================================================
    
    def show_v6_control_menu(self, chat_id: int = None):
        """Show V6 control menu (callback handler)"""
        logger.info("[V6CommandHandlers] Showing V6 control menu")
        
        if hasattr(self._bot, 'menu_manager') and self._bot.menu_manager:
            self._bot.menu_manager.show_v6_menu(chat_id, None)
        else:
            self.handle_v6_status()
    
    def toggle_v6_system(self, chat_id: int = None):
        """Toggle V6 system enabled/disabled"""
        logger.info("[V6CommandHandlers] Toggling V6 system")
        
        try:
            if "v6_price_action" not in self._config:
                self._config["v6_price_action"] = {"enabled": False, "timeframes": {}}
            
            current = self._config["v6_price_action"].get("enabled", False)
            self._config["v6_price_action"]["enabled"] = not current
            
            status = "ENABLED" if not current else "DISABLED"
            self._send_response(f"{'✅' if not current else '❌'} <b>V6 System {status}</b>")
        except Exception as e:
            logger.error(f"[V6CommandHandlers] Error toggling V6 system: {e}")
            self._send_response("❌ <b>Error toggling V6 system</b>")
    
    def toggle_v6_timeframe_15m(self, chat_id: int = None):
        """Toggle V6 15M timeframe"""
        current = self._is_timeframe_enabled("15m")
        self._set_timeframe_enabled("15m", not current)
        status = "DISABLED" if current else "ENABLED"
        self._send_response(f"{'❌' if current else '✅'} <b>V6 15M Timeframe {status}</b>")
    
    def toggle_v6_timeframe_30m(self, chat_id: int = None):
        """Toggle V6 30M timeframe"""
        current = self._is_timeframe_enabled("30m")
        self._set_timeframe_enabled("30m", not current)
        status = "DISABLED" if current else "ENABLED"
        self._send_response(f"{'❌' if current else '✅'} <b>V6 30M Timeframe {status}</b>")
    
    def toggle_v6_timeframe_1h(self, chat_id: int = None):
        """Toggle V6 1H timeframe"""
        current = self._is_timeframe_enabled("1h")
        self._set_timeframe_enabled("1h", not current)
        status = "DISABLED" if current else "ENABLED"
        self._send_response(f"{'❌' if current else '✅'} <b>V6 1H Timeframe {status}</b>")
    
    def toggle_v6_timeframe_4h(self, chat_id: int = None):
        """Toggle V6 4H timeframe"""
        current = self._is_timeframe_enabled("4h")
        self._set_timeframe_enabled("4h", not current)
        status = "DISABLED" if current else "ENABLED"
        self._send_response(f"{'❌' if current else '✅'} <b>V6 4H Timeframe {status}</b>")
    
    def enable_all_v6_timeframes(self, chat_id: int = None):
        """Enable all V6 timeframes"""
        logger.info("[V6CommandHandlers] Enabling all V6 timeframes")
        
        for tf in self.V6_TIMEFRAMES:
            self._set_timeframe_enabled(tf, True)
        
        self._send_response("✅ <b>All V6 Timeframes ENABLED</b>\n\n15M, 30M, 1H, 4H are now active.")
    
    def disable_all_v6_timeframes(self, chat_id: int = None):
        """Disable all V6 timeframes"""
        logger.info("[V6CommandHandlers] Disabling all V6 timeframes")
        
        for tf in self.V6_TIMEFRAMES:
            self._set_timeframe_enabled(tf, False)
        
        self._send_response("❌ <b>All V6 Timeframes DISABLED</b>\n\n15M, 30M, 1H, 4H are now inactive.")
    
    def show_v6_stats(self, chat_id: int = None):
        """Show V6 statistics"""
        logger.info("[V6CommandHandlers] Showing V6 stats")
        self.handle_v6_status()
    
    def show_v6_config_menu(self, chat_id: int = None):
        """Show V6 configuration menu"""
        logger.info("[V6CommandHandlers] Showing V6 config menu")
        
        if hasattr(self._bot, 'menu_manager') and self._bot.menu_manager:
            if hasattr(self._bot.menu_manager, '_v6_handler'):
                self._bot.menu_manager._v6_handler.show_v6_configure_menu(chat_id, None)
                return
        
        # Fallback
        self.handle_v6_status()
    
    def show_v6_config_15m(self, chat_id: int = None):
        """Show V6 15M configuration"""
        self._show_timeframe_config("15m", chat_id)
    
    def show_v6_config_30m(self, chat_id: int = None):
        """Show V6 30M configuration"""
        self._show_timeframe_config("30m", chat_id)
    
    def show_v6_config_1h(self, chat_id: int = None):
        """Show V6 1H configuration"""
        self._show_timeframe_config("1h", chat_id)
    
    def show_v6_config_4h(self, chat_id: int = None):
        """Show V6 4H configuration"""
        self._show_timeframe_config("4h", chat_id)
    
    def _show_timeframe_config(self, timeframe: str, chat_id: int = None):
        """Show configuration for a specific timeframe"""
        tf_config = self._get_timeframe_config(timeframe)
        
        enabled = tf_config.get("enabled", False)
        lot_mult = tf_config.get("lot_multiplier", 1.0)
        sl_mult = tf_config.get("sl_multiplier", 1.0)
        tp_mult = tf_config.get("tp_multiplier", 1.0)
        
        text = f"""⚙️ <b>V6 {timeframe.upper()} CONFIGURATION</b>
━━━━━━━━━━━━━━━━━━━━━━━━

🔌 <b>Status:</b> {'✅ ENABLED' if enabled else '❌ DISABLED'}

📊 <b>Parameters:</b>
  • Lot Multiplier: {lot_mult}x
  • SL Multiplier: {sl_mult}x
  • TP Multiplier: {tp_mult}x

━━━━━━━━━━━━━━━━━━━━━━━━
<i>Use menu buttons to adjust</i>"""
        
        self._send_response(text)
    
    # =========================================================================
    # HANDLER REGISTRATION
    # =========================================================================
    
    def get_command_handlers(self) -> Dict[str, callable]:
        """Get all command handlers for registration"""
        return {
            "/v6_status": self.handle_v6_status,
            "/v6_control": self.handle_v6_control,
            "/tf15m_on": self.handle_v6_tf15m_on,
            "/tf15m_off": self.handle_v6_tf15m_off,
            "/tf30m_on": self.handle_v6_tf30m_on,
            "/tf30m_off": self.handle_v6_tf30m_off,
            "/tf1h_on": self.handle_v6_tf1h_on,
            "/tf1h_off": self.handle_v6_tf1h_off,
            "/tf4h_on": self.handle_v6_tf4h_on,
            "/tf4h_off": self.handle_v6_tf4h_off,
        }
    
    def get_callback_handlers(self) -> Dict[str, callable]:
        """Get all callback handlers for registration"""
        return {
            "menu_v6": self.show_v6_control_menu,
            "v6_toggle_system": self.toggle_v6_system,
            "v6_toggle_15m": self.toggle_v6_timeframe_15m,
            "v6_toggle_30m": self.toggle_v6_timeframe_30m,
            "v6_toggle_1h": self.toggle_v6_timeframe_1h,
            "v6_toggle_4h": self.toggle_v6_timeframe_4h,
            "v6_enable_all": self.enable_all_v6_timeframes,
            "v6_disable_all": self.disable_all_v6_timeframes,
            "v6_view_stats": self.show_v6_stats,
            "v6_config_menu": self.show_v6_config_menu,
            "v6_config_15m": self.show_v6_config_15m,
            "v6_config_30m": self.show_v6_config_30m,
            "v6_config_1h": self.show_v6_config_1h,
            "v6_config_4h": self.show_v6_config_4h,
        }
    
    def register_with_registry(self, registry):
        """
        Register all handlers with CommandRegistry.
        
        Args:
            registry: CommandRegistry instance
        """
        # Register command handlers
        for cmd, handler in self.get_command_handlers().items():
            registry.register_command_handler(cmd, handler)
        
        # Register callback handlers
        for callback, handler in self.get_callback_handlers().items():
            registry.register_callback_handler(callback, handler)
        
        logger.info("[V6CommandHandlers] Registered all handlers with CommandRegistry")
