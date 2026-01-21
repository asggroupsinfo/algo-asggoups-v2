"""
Sessions Menu - Level 1 Navigation

Implements the Trading Sessions submenu.
src/telegram/menus/sessions_menu.py
"""

from telegram import InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class SessionsMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the Sessions menu"""

        buttons = [
            Btn.create_button("🕐 Status", "session_status"),
            Btn.create_button("🌏 Asian", "session_asian"),
            Btn.create_button("🇬🇧 London", "session_london"),
            Btn.create_button("🇺🇸 New York", "session_newyork"),
            Btn.create_button("🔄 Overlaps", "session_overlaps"),
            Btn.create_button("⚙️ Config", "session_config")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "🕐 **TRADING SESSIONS**\n━━━━━━━━━━━━━━━━━━━━━━━━\nManage Active Hours:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
