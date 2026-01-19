"""
Notification Preferences Menu Handler - Telegram V5 Upgrade

Allows users to configure notification preferences via Telegram menu:
- Per-type notification toggles
- Per-plugin filtering (V3 only / V6 only / Both)
- Quiet hours configuration
- Priority levels
- V6 timeframe filtering

Version: 1.0.0
Date: 2026-01-19
Part of Telegram V5 Upgrade - Batch 1
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationPreferencesMenuHandler:
    """
    Handles notification preferences configuration via Telegram menu.
    
    Provides:
    - Main preferences menu
    - Category toggles
    - Plugin filter selection
    - Quiet hours configuration
    - Priority level selection
    - V6 timeframe filter
    """
    
    CATEGORY_LABELS = {
        "trade_entry": "Trade Entry Alerts",
        "trade_exit": "Trade Exit Alerts",
        "tp_hit": "TP Hit Alerts",
        "sl_hit": "SL Hit Alerts",
        "profit_booking": "Profit Booking Alerts",
        "sl_modified": "SL Modified Alerts",
        "breakeven": "Breakeven Alerts",
        "daily_summary": "Daily Summary",
        "weekly_summary": "Weekly Summary",
        "trend_pulse": "Trend Pulse Alerts",
        "price_action": "Price Action Patterns",
        "shadow_trade": "Shadow Trade Alerts",
        "system_alert": "System Alerts",
        "error_alert": "Error Alerts",
        "plugin_status": "Plugin Status Alerts",
    }
    
    PLUGIN_FILTER_LABELS = {
        "all": "All Plugins",
        "v3_only": "V3 Only",
        "v6_only": "V6 Only",
        "none": "Mute All",
    }
    
    PRIORITY_LABELS = {
        "all": "All Priorities",
        "critical_only": "Critical Only",
        "high_and_above": "High & Above",
        "medium_and_above": "Medium & Above",
    }
    
    def __init__(self, telegram_bot):
        """
        Initialize NotificationPreferencesMenuHandler.
        
        Args:
            telegram_bot: The Telegram bot instance
        """
        self.bot = telegram_bot
        self._logger = logger
        self._preferences = None
    
    def _get_preferences(self):
        """Get notification preferences instance"""
        if self._preferences is None:
            try:
                from src.telegram.notification_preferences import NotificationPreferences
                self._preferences = NotificationPreferences()
            except ImportError:
                self._logger.error("[NotifPrefsMenu] Could not import NotificationPreferences")
                return None
        return self._preferences
    
    def show_main_menu(self, user_id: int, message_id: int = None):
        """
        Show main notification preferences menu.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit (optional)
        """
        prefs = self._get_preferences()
        if not prefs:
            self._send_error(user_id, "Notification preferences not available")
            return
        
        # Build status text
        global_enabled = prefs.is_enabled()
        plugin_filter = prefs.get_plugin_filter()
        priority_level = prefs.get_priority_level()
        quiet_hours = prefs.is_quiet_hours_enabled()
        
        enabled_count = len(prefs.get_enabled_categories())
        total_count = len(self.CATEGORY_LABELS)
        
        text = "🔔 <b>NOTIFICATION PREFERENCES</b>\n\n"
        text += f"📊 <b>Status:</b> {'✅ Enabled' if global_enabled else '❌ Disabled'}\n"
        text += f"📋 <b>Categories:</b> {enabled_count}/{total_count} enabled\n"
        text += f"🔌 <b>Plugin Filter:</b> {self.PLUGIN_FILTER_LABELS.get(plugin_filter, 'All')}\n"
        text += f"⚡ <b>Priority:</b> {self.PRIORITY_LABELS.get(priority_level, 'All')}\n"
        text += f"🌙 <b>Quiet Hours:</b> {'✅ On' if quiet_hours else '❌ Off'}\n"
        
        # Build keyboard
        keyboard = [
            [
                {"text": f"{'🔴 Disable' if global_enabled else '🟢 Enable'} All", 
                 "callback_data": "notif_toggle_global"}
            ],
            [
                {"text": "📋 Categories", "callback_data": "notif_categories"},
                {"text": "🔌 Plugin Filter", "callback_data": "notif_plugin_filter"}
            ],
            [
                {"text": "⚡ Priority Level", "callback_data": "notif_priority"},
                {"text": "🌙 Quiet Hours", "callback_data": "notif_quiet_hours"}
            ],
            [
                {"text": "🎯 V6 Timeframes", "callback_data": "notif_v6_timeframes"}
            ],
            [
                {"text": "🔄 Reset to Defaults", "callback_data": "notif_reset"}
            ],
            [
                {"text": "🔙 Back to Menu", "callback_data": "menu_main"}
            ]
        ]
        
        self._send_or_edit(user_id, message_id, text, keyboard)
    
    def show_categories_menu(self, user_id: int, message_id: int = None):
        """
        Show notification categories toggle menu.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit (optional)
        """
        prefs = self._get_preferences()
        if not prefs:
            self._send_error(user_id, "Notification preferences not available")
            return
        
        text = "📋 <b>NOTIFICATION CATEGORIES</b>\n\n"
        text += "Toggle which notification types you want to receive:\n\n"
        
        keyboard = []
        
        # Group categories
        trade_cats = ["trade_entry", "trade_exit", "tp_hit", "sl_hit", "profit_booking", "sl_modified", "breakeven"]
        summary_cats = ["daily_summary", "weekly_summary"]
        v6_cats = ["trend_pulse", "price_action", "shadow_trade"]
        system_cats = ["system_alert", "error_alert", "plugin_status"]
        
        # Trade categories
        text += "<b>📈 Trade Alerts:</b>\n"
        for cat in trade_cats:
            enabled = prefs.is_category_enabled(cat)
            status = "✅" if enabled else "❌"
            text += f"  {status} {self.CATEGORY_LABELS.get(cat, cat)}\n"
            keyboard.append([{
                "text": f"{status} {self.CATEGORY_LABELS.get(cat, cat)}",
                "callback_data": f"notif_cat_toggle_{cat}"
            }])
        
        text += "\n<b>📊 Summaries:</b>\n"
        for cat in summary_cats:
            enabled = prefs.is_category_enabled(cat)
            status = "✅" if enabled else "❌"
            text += f"  {status} {self.CATEGORY_LABELS.get(cat, cat)}\n"
        
        text += "\n<b>🎯 V6 Specific:</b>\n"
        for cat in v6_cats:
            enabled = prefs.is_category_enabled(cat)
            status = "✅" if enabled else "❌"
            text += f"  {status} {self.CATEGORY_LABELS.get(cat, cat)}\n"
        
        text += "\n<b>⚙️ System:</b>\n"
        for cat in system_cats:
            enabled = prefs.is_category_enabled(cat)
            status = "✅" if enabled else "❌"
            text += f"  {status} {self.CATEGORY_LABELS.get(cat, cat)}\n"
        
        # Simplified keyboard with grouped toggles
        keyboard = [
            [
                {"text": "✅ Enable All", "callback_data": "notif_cat_enable_all"},
                {"text": "❌ Disable All", "callback_data": "notif_cat_disable_all"}
            ],
            [
                {"text": "📈 Trade Alerts", "callback_data": "notif_cat_group_trade"}
            ],
            [
                {"text": "📊 Summaries", "callback_data": "notif_cat_group_summary"}
            ],
            [
                {"text": "🎯 V6 Specific", "callback_data": "notif_cat_group_v6"}
            ],
            [
                {"text": "⚙️ System", "callback_data": "notif_cat_group_system"}
            ],
            [
                {"text": "🔙 Back", "callback_data": "notif_main"}
            ]
        ]
        
        self._send_or_edit(user_id, message_id, text, keyboard)
    
    def show_plugin_filter_menu(self, user_id: int, message_id: int = None):
        """
        Show plugin filter selection menu.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit (optional)
        """
        prefs = self._get_preferences()
        if not prefs:
            self._send_error(user_id, "Notification preferences not available")
            return
        
        current_filter = prefs.get_plugin_filter()
        
        text = "🔌 <b>PLUGIN FILTER</b>\n\n"
        text += "Choose which plugins to receive notifications from:\n\n"
        
        for filter_key, label in self.PLUGIN_FILTER_LABELS.items():
            selected = "✅" if filter_key == current_filter else "⬜"
            text += f"{selected} <b>{label}</b>\n"
            if filter_key == "all":
                text += "   Receive from V3 Combined and V6 Price Action\n"
            elif filter_key == "v3_only":
                text += "   Only V3 Combined Logic notifications\n"
            elif filter_key == "v6_only":
                text += "   Only V6 Price Action notifications\n"
            elif filter_key == "none":
                text += "   Mute all plugin notifications\n"
            text += "\n"
        
        keyboard = [
            [
                {"text": f"{'✅' if current_filter == 'all' else '⬜'} All Plugins",
                 "callback_data": "notif_filter_all"}
            ],
            [
                {"text": f"{'✅' if current_filter == 'v3_only' else '⬜'} V3 Only",
                 "callback_data": "notif_filter_v3_only"},
                {"text": f"{'✅' if current_filter == 'v6_only' else '⬜'} V6 Only",
                 "callback_data": "notif_filter_v6_only"}
            ],
            [
                {"text": f"{'✅' if current_filter == 'none' else '⬜'} Mute All",
                 "callback_data": "notif_filter_none"}
            ],
            [
                {"text": "🔙 Back", "callback_data": "notif_main"}
            ]
        ]
        
        self._send_or_edit(user_id, message_id, text, keyboard)
    
    def show_priority_menu(self, user_id: int, message_id: int = None):
        """
        Show priority level selection menu.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit (optional)
        """
        prefs = self._get_preferences()
        if not prefs:
            self._send_error(user_id, "Notification preferences not available")
            return
        
        current_priority = prefs.get_priority_level()
        
        text = "⚡ <b>PRIORITY LEVEL</b>\n\n"
        text += "Filter notifications by priority:\n\n"
        
        priority_descriptions = {
            "all": "Receive all notifications regardless of priority",
            "critical_only": "Only emergency alerts (daily loss limit, MT5 disconnect)",
            "high_and_above": "Trade entries/exits and critical alerts",
            "medium_and_above": "Most alerts except low priority info",
        }
        
        for level_key, label in self.PRIORITY_LABELS.items():
            selected = "✅" if level_key == current_priority else "⬜"
            text += f"{selected} <b>{label}</b>\n"
            text += f"   {priority_descriptions.get(level_key, '')}\n\n"
        
        keyboard = [
            [
                {"text": f"{'✅' if current_priority == 'all' else '⬜'} All Priorities",
                 "callback_data": "notif_priority_all"}
            ],
            [
                {"text": f"{'✅' if current_priority == 'medium_and_above' else '⬜'} Medium & Above",
                 "callback_data": "notif_priority_medium_and_above"}
            ],
            [
                {"text": f"{'✅' if current_priority == 'high_and_above' else '⬜'} High & Above",
                 "callback_data": "notif_priority_high_and_above"}
            ],
            [
                {"text": f"{'✅' if current_priority == 'critical_only' else '⬜'} Critical Only",
                 "callback_data": "notif_priority_critical_only"}
            ],
            [
                {"text": "🔙 Back", "callback_data": "notif_main"}
            ]
        ]
        
        self._send_or_edit(user_id, message_id, text, keyboard)
    
    def show_quiet_hours_menu(self, user_id: int, message_id: int = None):
        """
        Show quiet hours configuration menu.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit (optional)
        """
        prefs = self._get_preferences()
        if not prefs:
            self._send_error(user_id, "Notification preferences not available")
            return
        
        all_prefs = prefs.get_all_preferences()
        quiet_hours = all_prefs.get("quiet_hours", {})
        enabled = quiet_hours.get("enabled", False)
        start = quiet_hours.get("start", "22:00")
        end = quiet_hours.get("end", "06:00")
        allow_critical = quiet_hours.get("allow_critical", True)
        
        text = "🌙 <b>QUIET HOURS</b>\n\n"
        text += f"<b>Status:</b> {'✅ Enabled' if enabled else '❌ Disabled'}\n\n"
        
        if enabled:
            text += f"<b>Schedule:</b> {start} - {end}\n"
            text += f"<b>Allow Critical:</b> {'✅ Yes' if allow_critical else '❌ No'}\n\n"
            text += "During quiet hours, only critical alerts will be sent "
            text += "(if enabled).\n"
        else:
            text += "Enable quiet hours to mute notifications during specific times.\n"
        
        keyboard = [
            [
                {"text": f"{'🔴 Disable' if enabled else '🟢 Enable'} Quiet Hours",
                 "callback_data": "notif_quiet_toggle"}
            ],
            [
                {"text": f"🕐 Start: {start}", "callback_data": "notif_quiet_start"},
                {"text": f"🕐 End: {end}", "callback_data": "notif_quiet_end"}
            ],
            [
                {"text": f"{'✅' if allow_critical else '❌'} Allow Critical Alerts",
                 "callback_data": "notif_quiet_critical"}
            ],
            [
                {"text": "🔙 Back", "callback_data": "notif_main"}
            ]
        ]
        
        self._send_or_edit(user_id, message_id, text, keyboard)
    
    def show_v6_timeframes_menu(self, user_id: int, message_id: int = None):
        """
        Show V6 timeframe filter menu.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to edit (optional)
        """
        prefs = self._get_preferences()
        if not prefs:
            self._send_error(user_id, "Notification preferences not available")
            return
        
        text = "🎯 <b>V6 TIMEFRAME FILTER</b>\n\n"
        text += "Choose which V6 timeframes to receive notifications from:\n\n"
        
        timeframes = ["15m", "30m", "1h", "4h"]
        keyboard = []
        
        for tf in timeframes:
            enabled = prefs.is_v6_timeframe_enabled(tf)
            status = "✅" if enabled else "❌"
            text += f"{status} <b>{tf.upper()}</b> Price Action\n"
            keyboard.append([{
                "text": f"{status} {tf.upper()}",
                "callback_data": f"notif_v6tf_toggle_{tf}"
            }])
        
        keyboard.append([
            {"text": "✅ Enable All", "callback_data": "notif_v6tf_enable_all"},
            {"text": "❌ Disable All", "callback_data": "notif_v6tf_disable_all"}
        ])
        keyboard.append([
            {"text": "🔙 Back", "callback_data": "notif_main"}
        ])
        
        self._send_or_edit(user_id, message_id, text, keyboard)
    
    def handle_callback(self, callback_data: str, user_id: int, message_id: int = None) -> bool:
        """
        Handle notification preferences callbacks.
        
        Args:
            callback_data: Callback data string
            user_id: Telegram user ID
            message_id: Message ID to edit
        
        Returns:
            True if callback was handled, False otherwise
        """
        prefs = self._get_preferences()
        if not prefs:
            return False
        
        try:
            # Main menu
            if callback_data == "notif_main" or callback_data == "menu_notifications":
                self.show_main_menu(user_id, message_id)
                return True
            
            # Global toggle
            elif callback_data == "notif_toggle_global":
                current = prefs.is_enabled()
                prefs.set_enabled(not current)
                self.show_main_menu(user_id, message_id)
                return True
            
            # Categories menu
            elif callback_data == "notif_categories":
                self.show_categories_menu(user_id, message_id)
                return True
            
            # Category enable/disable all
            elif callback_data == "notif_cat_enable_all":
                prefs.enable_all_categories()
                self.show_categories_menu(user_id, message_id)
                return True
            
            elif callback_data == "notif_cat_disable_all":
                prefs.disable_all_categories()
                self.show_categories_menu(user_id, message_id)
                return True
            
            # Category toggle
            elif callback_data.startswith("notif_cat_toggle_"):
                category = callback_data.replace("notif_cat_toggle_", "")
                prefs.toggle_category(category)
                self.show_categories_menu(user_id, message_id)
                return True
            
            # Plugin filter menu
            elif callback_data == "notif_plugin_filter":
                self.show_plugin_filter_menu(user_id, message_id)
                return True
            
            # Plugin filter selection
            elif callback_data.startswith("notif_filter_"):
                filter_type = callback_data.replace("notif_filter_", "")
                prefs.set_plugin_filter(filter_type)
                self.show_plugin_filter_menu(user_id, message_id)
                return True
            
            # Priority menu
            elif callback_data == "notif_priority":
                self.show_priority_menu(user_id, message_id)
                return True
            
            # Priority selection
            elif callback_data.startswith("notif_priority_"):
                level = callback_data.replace("notif_priority_", "")
                prefs.set_priority_level(level)
                self.show_priority_menu(user_id, message_id)
                return True
            
            # Quiet hours menu
            elif callback_data == "notif_quiet_hours":
                self.show_quiet_hours_menu(user_id, message_id)
                return True
            
            # Quiet hours toggle
            elif callback_data == "notif_quiet_toggle":
                current = prefs.is_quiet_hours_enabled()
                prefs.set_quiet_hours(not current)
                self.show_quiet_hours_menu(user_id, message_id)
                return True
            
            # Quiet hours critical toggle
            elif callback_data == "notif_quiet_critical":
                all_prefs = prefs.get_all_preferences()
                quiet_hours = all_prefs.get("quiet_hours", {})
                current = quiet_hours.get("allow_critical", True)
                prefs.set_quiet_hours(
                    quiet_hours.get("enabled", False),
                    quiet_hours.get("start"),
                    quiet_hours.get("end"),
                    not current
                )
                self.show_quiet_hours_menu(user_id, message_id)
                return True
            
            # V6 timeframes menu
            elif callback_data == "notif_v6_timeframes":
                self.show_v6_timeframes_menu(user_id, message_id)
                return True
            
            # V6 timeframe toggle
            elif callback_data.startswith("notif_v6tf_toggle_"):
                tf = callback_data.replace("notif_v6tf_toggle_", "")
                current = prefs.is_v6_timeframe_enabled(tf)
                prefs.set_v6_timeframe_enabled(tf, not current)
                self.show_v6_timeframes_menu(user_id, message_id)
                return True
            
            # V6 timeframe enable/disable all
            elif callback_data == "notif_v6tf_enable_all":
                for tf in ["15m", "30m", "1h", "4h"]:
                    prefs.set_v6_timeframe_enabled(tf, True)
                self.show_v6_timeframes_menu(user_id, message_id)
                return True
            
            elif callback_data == "notif_v6tf_disable_all":
                for tf in ["15m", "30m", "1h", "4h"]:
                    prefs.set_v6_timeframe_enabled(tf, False)
                self.show_v6_timeframes_menu(user_id, message_id)
                return True
            
            # Reset to defaults
            elif callback_data == "notif_reset":
                prefs.reset_to_defaults()
                self.show_main_menu(user_id, message_id)
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"[NotifPrefsMenu] Error handling callback {callback_data}: {e}")
            return False
    
    def _send_or_edit(self, user_id: int, message_id: int, text: str, keyboard: List):
        """Send new message or edit existing one"""
        try:
            if hasattr(self.bot, 'edit_message') and message_id:
                self.bot.edit_message(
                    chat_id=user_id,
                    message_id=message_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup={"inline_keyboard": keyboard}
                )
            elif hasattr(self.bot, 'send_message'):
                self.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup={"inline_keyboard": keyboard}
                )
        except Exception as e:
            self._logger.error(f"[NotifPrefsMenu] Error sending message: {e}")
    
    def _send_error(self, user_id: int, message: str):
        """Send error message"""
        try:
            if hasattr(self.bot, 'send_message'):
                self.bot.send_message(
                    chat_id=user_id,
                    text=f"❌ Error: {message}"
                )
        except Exception as e:
            self._logger.error(f"[NotifPrefsMenu] Error sending error message: {e}")
