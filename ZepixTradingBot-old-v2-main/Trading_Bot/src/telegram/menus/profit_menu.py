"""
Profit Menu - Level 1 Navigation

Implements the Profit & Dual Order submenu.
src/telegram/menus/profit_menu.py
"""

from telegram import InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class ProfitMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the Profit menu"""

        buttons = [
            Btn.create_button("💎 Dual Orders", "profit_dualorder"),
            Btn.create_button("📦 Order A", "profit_ordera"),
            Btn.create_button("📦 Order B", "profit_orderb"),
            Btn.create_button("🔒 Lock Profit", "profit_lock"),
            Btn.create_button("📉 Trailing", "profit_trailing"),
            Btn.create_button("🎯 Targets", "profit_targets"),
            Btn.create_button("📊 Stats", "profit_stats")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "💰 **PROFIT MANAGEMENT**\n━━━━━━━━━━━━━━━━━━━━━━━━\nDual Orders & Booking:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
