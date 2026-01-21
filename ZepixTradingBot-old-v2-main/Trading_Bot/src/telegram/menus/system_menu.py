"""
System Menu - Level 1 Navigation

Implements the System Control submenu.
src/telegram/menus/system_menu.py
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class SystemMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the System Control menu"""

        buttons = [
            Btn.create_button("ℹ️ Status", "system_status"),
            Btn.create_button("⏸️ Pause", "system_pause"),
            Btn.create_button("▶️ Resume", "system_resume"),
            Btn.create_button("🔄 Restart", "system_restart"),
            Btn.create_button("⛔ Shutdown", "system_shutdown"),
            Btn.create_button("❓ Help", "system_help"),
            Btn.create_button("⚙️ Config", "system_config"),
            Btn.create_button("🏥 Health", "system_health"),
            Btn.create_button("📋 Version", "system_version")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "🎛️ **SYSTEM CONTROL**\n━━━━━━━━━━━━━━━━━━━━━━━━\nSelect an action:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
