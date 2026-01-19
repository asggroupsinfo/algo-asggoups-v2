"""
Dual Order & Re-entry Menu Handler - Telegram V5 Upgrade

This module provides menu handlers for Dual Order System and Re-entry System
per-plugin configuration via Telegram menu interface.

Features:
- Per-plugin Dual Order configuration (Order A, Order B, Both)
- Per-plugin Re-entry configuration (TP Continuation, SL Hunt Recovery, Exit Continuation)
- Enable/disable per-plugin settings
- Parameter adjustment for each system

Version: 1.0.0
Date: 2026-01-19
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DualOrderMenuHandler:
    """
    Menu Handler for Dual Order System per-plugin configuration.
    
    Provides:
    - Order A / Order B / Both selection per plugin
    - Lot size configuration for each order type
    - TP/SL configuration for each order type
    """
    
    # Order modes
    ORDER_MODES = ["order_a", "order_b", "both"]
    ORDER_MODE_LABELS = {
        "order_a": "Order A Only",
        "order_b": "Order B Only",
        "both": "Both Orders"
    }
    
    def __init__(self, telegram_bot, config: Dict[str, Any] = None):
        """
        Initialize DualOrderMenuHandler.
        
        Args:
            telegram_bot: Telegram bot instance
            config: Bot configuration dictionary
        """
        self._bot = telegram_bot
        self._config = config or {}
        logger.info("[DualOrderMenuHandler] Initialized")
    
    def set_config(self, config: Dict[str, Any]):
        """Update configuration reference"""
        self._config = config
    
    def _get_dual_order_config(self, plugin: str = None) -> Dict[str, Any]:
        """Get dual order configuration for a plugin"""
        dual_config = self._config.get("dual_order_system", {})
        if plugin:
            return dual_config.get("plugins", {}).get(plugin, {
                "enabled": False,
                "mode": "both",
                "order_a": {"lot_multiplier": 1.0, "tp_pips": 20, "sl_pips": 15},
                "order_b": {"lot_multiplier": 0.5, "tp_pips": 40, "sl_pips": 15}
            })
        return dual_config
    
    def _send_message(self, text: str, reply_markup: Dict = None, message_id: int = None):
        """Send or edit message"""
        try:
            if message_id and hasattr(self._bot, 'edit_message'):
                self._bot.edit_message(text, message_id, reply_markup)
            elif hasattr(self._bot, 'send_message_with_keyboard') and reply_markup:
                self._bot.send_message_with_keyboard(text, reply_markup)
            elif hasattr(self._bot, 'send_message'):
                self._bot.send_message(text)
        except Exception as e:
            logger.error(f"[DualOrderMenuHandler] Error sending message: {e}")
    
    # =========================================================================
    # MAIN DUAL ORDER MENU
    # =========================================================================
    
    def show_dual_order_menu(self, user_id: int, message_id: int = None):
        """Show main dual order configuration menu"""
        logger.info(f"[DualOrderMenuHandler] Showing dual order menu for user {user_id}")
        
        dual_config = self._get_dual_order_config()
        system_enabled = dual_config.get("enabled", False)
        
        text = f"""💎 <b>DUAL ORDER SYSTEM</b>
━━━━━━━━━━━━━━━━━━━━━━━━

🔌 <b>System Status:</b> {'✅ ENABLED' if system_enabled else '❌ DISABLED'}

📊 <b>Description:</b>
The Dual Order System allows placing two orders
simultaneously with different TP targets:
• <b>Order A:</b> Quick profit (smaller TP)
• <b>Order B:</b> Extended profit (larger TP)

━━━━━━━━━━━━━━━━━━━━━━━━
<i>Select a plugin to configure:</i>"""
        
        # Build keyboard with plugin options
        keyboard = [
            # System toggle
            [
                {"text": f"{'✅' if system_enabled else '❌'} Toggle System", "callback_data": "dual_toggle_system"}
            ],
            # V3 Plugins
            [
                {"text": "🧠 V3 Logic 1 (5m)", "callback_data": "dual_config_v3_logic1"},
                {"text": "🧠 V3 Logic 2 (15m)", "callback_data": "dual_config_v3_logic2"}
            ],
            [
                {"text": "🧠 V3 Logic 3 (1h)", "callback_data": "dual_config_v3_logic3"}
            ],
            # V6 Plugins
            [
                {"text": "📊 V6 15M", "callback_data": "dual_config_v6_15m"},
                {"text": "📊 V6 30M", "callback_data": "dual_config_v6_30m"}
            ],
            [
                {"text": "📊 V6 1H", "callback_data": "dual_config_v6_1h"},
                {"text": "📊 V6 4H", "callback_data": "dual_config_v6_4h"}
            ],
            # Navigation
            [
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    def show_plugin_dual_order_config(self, plugin: str, user_id: int, message_id: int = None):
        """Show dual order configuration for a specific plugin"""
        logger.info(f"[DualOrderMenuHandler] Showing config for plugin {plugin}")
        
        plugin_config = self._get_dual_order_config(plugin)
        enabled = plugin_config.get("enabled", False)
        mode = plugin_config.get("mode", "both")
        order_a = plugin_config.get("order_a", {})
        order_b = plugin_config.get("order_b", {})
        
        # Format plugin name
        plugin_names = {
            "v3_logic1": "V3 Logic 1 (5m)",
            "v3_logic2": "V3 Logic 2 (15m)",
            "v3_logic3": "V3 Logic 3 (1h)",
            "v6_15m": "V6 15M",
            "v6_30m": "V6 30M",
            "v6_1h": "V6 1H",
            "v6_4h": "V6 4H"
        }
        plugin_name = plugin_names.get(plugin, plugin)
        
        text = f"""💎 <b>DUAL ORDER: {plugin_name}</b>
━━━━━━━━━━━━━━━━━━━━━━━━

🔌 <b>Status:</b> {'✅ ENABLED' if enabled else '❌ DISABLED'}
📋 <b>Mode:</b> {self.ORDER_MODE_LABELS.get(mode, mode)}

📊 <b>Order A Configuration:</b>
  • Lot Multiplier: {order_a.get('lot_multiplier', 1.0)}x
  • TP: {order_a.get('tp_pips', 20)} pips
  • SL: {order_a.get('sl_pips', 15)} pips

📊 <b>Order B Configuration:</b>
  • Lot Multiplier: {order_b.get('lot_multiplier', 0.5)}x
  • TP: {order_b.get('tp_pips', 40)} pips
  • SL: {order_b.get('sl_pips', 15)} pips

━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        # Build keyboard
        keyboard = [
            # Toggle and mode
            [
                {"text": f"{'✅' if enabled else '❌'} Toggle", "callback_data": f"dual_toggle_{plugin}"},
                {"text": "📋 Change Mode", "callback_data": f"dual_mode_{plugin}"}
            ],
            # Order A config
            [
                {"text": "⚙️ Order A Settings", "callback_data": f"dual_order_a_{plugin}"}
            ],
            # Order B config
            [
                {"text": "⚙️ Order B Settings", "callback_data": f"dual_order_b_{plugin}"}
            ],
            # Navigation
            [
                {"text": "◀️ Back", "callback_data": "menu_dual_order"},
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    def show_mode_selection(self, plugin: str, user_id: int, message_id: int = None):
        """Show mode selection for a plugin"""
        plugin_config = self._get_dual_order_config(plugin)
        current_mode = plugin_config.get("mode", "both")
        
        text = f"""📋 <b>SELECT ORDER MODE</b>
━━━━━━━━━━━━━━━━━━━━━━━━

Current Mode: <b>{self.ORDER_MODE_LABELS.get(current_mode, current_mode)}</b>

Select new mode:"""
        
        keyboard = []
        for mode in self.ORDER_MODES:
            is_current = mode == current_mode
            label = self.ORDER_MODE_LABELS.get(mode, mode)
            emoji = "✅" if is_current else "⚪"
            keyboard.append([{"text": f"{emoji} {label}", "callback_data": f"dual_set_mode_{plugin}_{mode}"}])
        
        keyboard.append([
            {"text": "◀️ Back", "callback_data": f"dual_config_{plugin}"},
            {"text": "🏠 Main Menu", "callback_data": "menu_main"}
        ])
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    # =========================================================================
    # CALLBACK HANDLER
    # =========================================================================
    
    def handle_callback(self, callback_data: str, user_id: int, message_id: int = None) -> bool:
        """Handle dual order menu callback"""
        logger.info(f"[DualOrderMenuHandler] Handling callback: {callback_data}")
        
        if callback_data == "menu_dual_order":
            self.show_dual_order_menu(user_id, message_id)
            return True
        
        if callback_data.startswith("dual_config_"):
            plugin = callback_data.replace("dual_config_", "")
            self.show_plugin_dual_order_config(plugin, user_id, message_id)
            return True
        
        if callback_data.startswith("dual_mode_"):
            plugin = callback_data.replace("dual_mode_", "")
            self.show_mode_selection(plugin, user_id, message_id)
            return True
        
        if callback_data.startswith("dual_toggle_"):
            plugin = callback_data.replace("dual_toggle_", "")
            self._toggle_plugin(plugin)
            if plugin == "system":
                self.show_dual_order_menu(user_id, message_id)
            else:
                self.show_plugin_dual_order_config(plugin, user_id, message_id)
            return True
        
        if callback_data.startswith("dual_set_mode_"):
            parts = callback_data.replace("dual_set_mode_", "").rsplit("_", 1)
            if len(parts) == 2:
                plugin, mode = parts
                self._set_mode(plugin, mode)
                self.show_plugin_dual_order_config(plugin, user_id, message_id)
            return True
        
        return False
    
    def _toggle_plugin(self, plugin: str):
        """Toggle plugin enabled state"""
        if plugin == "system":
            if "dual_order_system" not in self._config:
                self._config["dual_order_system"] = {"enabled": False, "plugins": {}}
            current = self._config["dual_order_system"].get("enabled", False)
            self._config["dual_order_system"]["enabled"] = not current
        else:
            if "dual_order_system" not in self._config:
                self._config["dual_order_system"] = {"enabled": True, "plugins": {}}
            if "plugins" not in self._config["dual_order_system"]:
                self._config["dual_order_system"]["plugins"] = {}
            if plugin not in self._config["dual_order_system"]["plugins"]:
                self._config["dual_order_system"]["plugins"][plugin] = {"enabled": False}
            current = self._config["dual_order_system"]["plugins"][plugin].get("enabled", False)
            self._config["dual_order_system"]["plugins"][plugin]["enabled"] = not current
    
    def _set_mode(self, plugin: str, mode: str):
        """Set order mode for a plugin"""
        if "dual_order_system" not in self._config:
            self._config["dual_order_system"] = {"enabled": True, "plugins": {}}
        if "plugins" not in self._config["dual_order_system"]:
            self._config["dual_order_system"]["plugins"] = {}
        if plugin not in self._config["dual_order_system"]["plugins"]:
            self._config["dual_order_system"]["plugins"][plugin] = {"enabled": True}
        self._config["dual_order_system"]["plugins"][plugin]["mode"] = mode


class ReentryMenuHandler:
    """
    Menu Handler for Re-entry System per-plugin configuration.
    
    Provides:
    - TP Continuation configuration per plugin
    - SL Hunt Recovery configuration per plugin
    - Exit Continuation configuration per plugin
    - Cooldown and chain limit settings
    """
    
    # Re-entry types
    REENTRY_TYPES = ["tp_continuation", "sl_hunt_recovery", "exit_continuation"]
    REENTRY_TYPE_LABELS = {
        "tp_continuation": "TP Continuation",
        "sl_hunt_recovery": "SL Hunt Recovery",
        "exit_continuation": "Exit Continuation"
    }
    
    def __init__(self, telegram_bot, config: Dict[str, Any] = None):
        """
        Initialize ReentryMenuHandler.
        
        Args:
            telegram_bot: Telegram bot instance
            config: Bot configuration dictionary
        """
        self._bot = telegram_bot
        self._config = config or {}
        logger.info("[ReentryMenuHandler] Initialized")
    
    def set_config(self, config: Dict[str, Any]):
        """Update configuration reference"""
        self._config = config
    
    def _get_reentry_config(self, plugin: str = None) -> Dict[str, Any]:
        """Get re-entry configuration for a plugin"""
        reentry_config = self._config.get("reentry_system", {})
        if plugin:
            return reentry_config.get("plugins", {}).get(plugin, {
                "enabled": False,
                "tp_continuation": {"enabled": True, "max_levels": 3, "cooldown_seconds": 60},
                "sl_hunt_recovery": {"enabled": True, "max_levels": 2, "cooldown_seconds": 120},
                "exit_continuation": {"enabled": False, "max_levels": 1, "cooldown_seconds": 180}
            })
        return reentry_config
    
    def _send_message(self, text: str, reply_markup: Dict = None, message_id: int = None):
        """Send or edit message"""
        try:
            if message_id and hasattr(self._bot, 'edit_message'):
                self._bot.edit_message(text, message_id, reply_markup)
            elif hasattr(self._bot, 'send_message_with_keyboard') and reply_markup:
                self._bot.send_message_with_keyboard(text, reply_markup)
            elif hasattr(self._bot, 'send_message'):
                self._bot.send_message(text)
        except Exception as e:
            logger.error(f"[ReentryMenuHandler] Error sending message: {e}")
    
    # =========================================================================
    # MAIN RE-ENTRY MENU
    # =========================================================================
    
    def show_reentry_menu(self, user_id: int, message_id: int = None):
        """Show main re-entry configuration menu"""
        logger.info(f"[ReentryMenuHandler] Showing re-entry menu for user {user_id}")
        
        reentry_config = self._get_reentry_config()
        system_enabled = reentry_config.get("enabled", False)
        
        text = f"""🔄 <b>RE-ENTRY SYSTEM</b>
━━━━━━━━━━━━━━━━━━━━━━━━

🔌 <b>System Status:</b> {'✅ ENABLED' if system_enabled else '❌ DISABLED'}

📊 <b>Re-entry Types:</b>
• <b>TP Continuation:</b> Re-enter after TP hit in same direction
• <b>SL Hunt Recovery:</b> Re-enter after SL hit if trend continues
• <b>Exit Continuation:</b> Re-enter after manual exit

━━━━━━━━━━━━━━━━━━━━━━━━
<i>Select a plugin to configure:</i>"""
        
        # Build keyboard with plugin options
        keyboard = [
            # System toggle
            [
                {"text": f"{'✅' if system_enabled else '❌'} Toggle System", "callback_data": "reentry_toggle_system"}
            ],
            # V3 Plugins
            [
                {"text": "🧠 V3 Logic 1 (5m)", "callback_data": "reentry_config_v3_logic1"},
                {"text": "🧠 V3 Logic 2 (15m)", "callback_data": "reentry_config_v3_logic2"}
            ],
            [
                {"text": "🧠 V3 Logic 3 (1h)", "callback_data": "reentry_config_v3_logic3"}
            ],
            # V6 Plugins
            [
                {"text": "📊 V6 15M", "callback_data": "reentry_config_v6_15m"},
                {"text": "📊 V6 30M", "callback_data": "reentry_config_v6_30m"}
            ],
            [
                {"text": "📊 V6 1H", "callback_data": "reentry_config_v6_1h"},
                {"text": "📊 V6 4H", "callback_data": "reentry_config_v6_4h"}
            ],
            # Navigation
            [
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    def show_plugin_reentry_config(self, plugin: str, user_id: int, message_id: int = None):
        """Show re-entry configuration for a specific plugin"""
        logger.info(f"[ReentryMenuHandler] Showing config for plugin {plugin}")
        
        plugin_config = self._get_reentry_config(plugin)
        enabled = plugin_config.get("enabled", False)
        tp_cont = plugin_config.get("tp_continuation", {})
        sl_hunt = plugin_config.get("sl_hunt_recovery", {})
        exit_cont = plugin_config.get("exit_continuation", {})
        
        # Format plugin name
        plugin_names = {
            "v3_logic1": "V3 Logic 1 (5m)",
            "v3_logic2": "V3 Logic 2 (15m)",
            "v3_logic3": "V3 Logic 3 (1h)",
            "v6_15m": "V6 15M",
            "v6_30m": "V6 30M",
            "v6_1h": "V6 1H",
            "v6_4h": "V6 4H"
        }
        plugin_name = plugin_names.get(plugin, plugin)
        
        text = f"""🔄 <b>RE-ENTRY: {plugin_name}</b>
━━━━━━━━━━━━━━━━━━━━━━━━

🔌 <b>Status:</b> {'✅ ENABLED' if enabled else '❌ DISABLED'}

📊 <b>TP Continuation:</b> {'✅' if tp_cont.get('enabled', False) else '❌'}
  • Max Levels: {tp_cont.get('max_levels', 3)}
  • Cooldown: {tp_cont.get('cooldown_seconds', 60)}s

📊 <b>SL Hunt Recovery:</b> {'✅' if sl_hunt.get('enabled', False) else '❌'}
  • Max Levels: {sl_hunt.get('max_levels', 2)}
  • Cooldown: {sl_hunt.get('cooldown_seconds', 120)}s

📊 <b>Exit Continuation:</b> {'✅' if exit_cont.get('enabled', False) else '❌'}
  • Max Levels: {exit_cont.get('max_levels', 1)}
  • Cooldown: {exit_cont.get('cooldown_seconds', 180)}s

━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        # Build keyboard
        keyboard = [
            # Toggle
            [
                {"text": f"{'✅' if enabled else '❌'} Toggle Plugin", "callback_data": f"reentry_toggle_{plugin}"}
            ],
            # Re-entry type configs
            [
                {"text": f"{'✅' if tp_cont.get('enabled', False) else '❌'} TP Continuation", "callback_data": f"reentry_tp_{plugin}"}
            ],
            [
                {"text": f"{'✅' if sl_hunt.get('enabled', False) else '❌'} SL Hunt Recovery", "callback_data": f"reentry_sl_{plugin}"}
            ],
            [
                {"text": f"{'✅' if exit_cont.get('enabled', False) else '❌'} Exit Continuation", "callback_data": f"reentry_exit_{plugin}"}
            ],
            # Navigation
            [
                {"text": "◀️ Back", "callback_data": "menu_reentry"},
                {"text": "🏠 Main Menu", "callback_data": "menu_main"}
            ]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        self._send_message(text, reply_markup, message_id)
    
    # =========================================================================
    # CALLBACK HANDLER
    # =========================================================================
    
    def handle_callback(self, callback_data: str, user_id: int, message_id: int = None) -> bool:
        """Handle re-entry menu callback"""
        logger.info(f"[ReentryMenuHandler] Handling callback: {callback_data}")
        
        if callback_data == "menu_reentry":
            self.show_reentry_menu(user_id, message_id)
            return True
        
        if callback_data.startswith("reentry_config_"):
            plugin = callback_data.replace("reentry_config_", "")
            self.show_plugin_reentry_config(plugin, user_id, message_id)
            return True
        
        if callback_data.startswith("reentry_toggle_"):
            plugin = callback_data.replace("reentry_toggle_", "")
            self._toggle_plugin(plugin)
            if plugin == "system":
                self.show_reentry_menu(user_id, message_id)
            else:
                self.show_plugin_reentry_config(plugin, user_id, message_id)
            return True
        
        if callback_data.startswith("reentry_tp_"):
            plugin = callback_data.replace("reentry_tp_", "")
            self._toggle_reentry_type(plugin, "tp_continuation")
            self.show_plugin_reentry_config(plugin, user_id, message_id)
            return True
        
        if callback_data.startswith("reentry_sl_"):
            plugin = callback_data.replace("reentry_sl_", "")
            self._toggle_reentry_type(plugin, "sl_hunt_recovery")
            self.show_plugin_reentry_config(plugin, user_id, message_id)
            return True
        
        if callback_data.startswith("reentry_exit_"):
            plugin = callback_data.replace("reentry_exit_", "")
            self._toggle_reentry_type(plugin, "exit_continuation")
            self.show_plugin_reentry_config(plugin, user_id, message_id)
            return True
        
        return False
    
    def _toggle_plugin(self, plugin: str):
        """Toggle plugin enabled state"""
        if plugin == "system":
            if "reentry_system" not in self._config:
                self._config["reentry_system"] = {"enabled": False, "plugins": {}}
            current = self._config["reentry_system"].get("enabled", False)
            self._config["reentry_system"]["enabled"] = not current
        else:
            if "reentry_system" not in self._config:
                self._config["reentry_system"] = {"enabled": True, "plugins": {}}
            if "plugins" not in self._config["reentry_system"]:
                self._config["reentry_system"]["plugins"] = {}
            if plugin not in self._config["reentry_system"]["plugins"]:
                self._config["reentry_system"]["plugins"][plugin] = {"enabled": False}
            current = self._config["reentry_system"]["plugins"][plugin].get("enabled", False)
            self._config["reentry_system"]["plugins"][plugin]["enabled"] = not current
    
    def _toggle_reentry_type(self, plugin: str, reentry_type: str):
        """Toggle a specific re-entry type for a plugin"""
        if "reentry_system" not in self._config:
            self._config["reentry_system"] = {"enabled": True, "plugins": {}}
        if "plugins" not in self._config["reentry_system"]:
            self._config["reentry_system"]["plugins"] = {}
        if plugin not in self._config["reentry_system"]["plugins"]:
            self._config["reentry_system"]["plugins"][plugin] = {"enabled": True}
        if reentry_type not in self._config["reentry_system"]["plugins"][plugin]:
            self._config["reentry_system"]["plugins"][plugin][reentry_type] = {"enabled": False}
        current = self._config["reentry_system"]["plugins"][plugin][reentry_type].get("enabled", False)
        self._config["reentry_system"]["plugins"][plugin][reentry_type]["enabled"] = not current
