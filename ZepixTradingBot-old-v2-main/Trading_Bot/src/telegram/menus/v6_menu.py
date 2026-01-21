"""
V6 Frames Menu - Level 1 Navigation

Implements the V6 Price Action Control submenu.
src/telegram/menus/v6_menu.py
"""

from telegram import InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class V6FramesMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the V6 Frames Control menu"""

        buttons = [
            Btn.create_button("🟢 V6 Status", "v6_status"),
            Btn.create_button("⚡ Toggle All", "v6_toggle"),
            Btn.create_button("⏱️ 15M On", "v6_tf15m_on"),
            Btn.create_button("⏱️ 15M Off", "v6_tf15m_off"),
            Btn.create_button("⏱️ 30M On", "v6_tf30m_on"),
            Btn.create_button("⏱️ 30M Off", "v6_tf30m_off"),
            Btn.create_button("🕐 1H On", "v6_tf1h_on"),
            Btn.create_button("🕐 1H Off", "v6_tf1h_off"),
            Btn.create_button("🕓 4H On", "v6_tf4h_on"),
            Btn.create_button("🕓 4H Off", "v6_tf4h_off"),
            Btn.create_button("⚙️ Config", "v6_config"),
            Btn.create_button("📊 Performance", "v6_performance")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "🟢 **V6 PRICE ACTION**\n━━━━━━━━━━━━━━━━━━━━━━━━\nManage Timeframes:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
