"""
Main Menu - Level 0 Navigation

Implements the 12-category main menu structure.
src/telegram/menus/main_menu.py
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class MainMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the main menu with 12 categories"""

        # Row 1: System & Trading
        r1 = [
            Btn.create_button("🎛️ System", "menu_system"),
            Btn.create_button("📊 Trading", "menu_trading")
        ]

        # Row 2: Risk & V3
        r2 = [
            Btn.create_button("🛡️ Risk", "menu_risk"),
            Btn.create_button("🔵 V3 Strategies", "menu_v3")
        ]

        # Row 3: V6 & Analytics
        r3 = [
            Btn.create_button("🟢 V6 Frames", "menu_v6"),
            Btn.create_button("📈 Analytics", "menu_analytics")
        ]

        # Row 4: Re-Entry & Profit
        r4 = [
            Btn.create_button("🔄 Re-Entry", "menu_reentry"),
            Btn.create_button("💰 Profit", "menu_profit") # Dual Order & Profit
        ]

        # Row 5: Plugin & Sessions
        r5 = [
            Btn.create_button("🔌 Plugins", "menu_plugin"),
            Btn.create_button("🕐 Sessions", "menu_session")
        ]

        # Row 6: Voice & Settings
        r6 = [
            Btn.create_button("🔊 Voice", "menu_voice"),
            Btn.create_button("⚙️ Settings", "menu_settings")
        ]

        keyboard = [r1, r2, r3, r4, r5, r6]

        return {
            "text": "Please select a category:",
            "reply_markup": InlineKeyboardMarkup(keyboard)
        }
