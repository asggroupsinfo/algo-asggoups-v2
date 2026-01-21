"""
Settings Menu - Level 1 Navigation

Implements the General Settings submenu.
src/telegram/menus/settings_menu.py
"""

from telegram import InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class SettingsMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the Settings menu"""

        buttons = [
            Btn.create_button("🆔 Bot ID", "settings_botid"),
            Btn.create_button("📡 MT5", "settings_mt5"),
            Btn.create_button("💾 Database", "settings_db"),
            Btn.create_button("📝 Logs", "settings_logs"),
            Btn.create_button("🔔 Notifications", "settings_notifications"),
            Btn.create_button("🔐 Security", "settings_security"),
            Btn.create_button("🔄 Reset", "settings_reset")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "⚙️ **GENERAL SETTINGS**\n━━━━━━━━━━━━━━━━━━━━━━━━\nSystem Configuration:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
