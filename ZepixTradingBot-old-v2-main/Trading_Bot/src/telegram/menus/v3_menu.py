"""
V3 Strategies Menu - Level 1 Navigation

Implements the V3 Strategy Control submenu.
src/telegram/menus/v3_menu.py
"""

from telegram import InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class V3StrategiesMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the V3 Strategy Control menu"""

        buttons = [
            Btn.create_button("🔵 V3 Status", "v3_status"),
            Btn.create_button("⚡ Toggle V3", "v3_toggle"),
            Btn.create_button("1️⃣ Logic 1 On", "v3_logic1_on"),
            Btn.create_button("1️⃣ Logic 1 Off", "v3_logic1_off"),
            Btn.create_button("2️⃣ Logic 2 On", "v3_logic2_on"),
            Btn.create_button("2️⃣ Logic 2 Off", "v3_logic2_off"),
            Btn.create_button("3️⃣ Logic 3 On", "v3_logic3_on"),
            Btn.create_button("3️⃣ Logic 3 Off", "v3_logic3_off"),
            Btn.create_button("⚙️ Config", "v3_config"),
            Btn.create_button("📊 Performance", "v3_perf")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "🔵 **V3 STRATEGIES**\n━━━━━━━━━━━━━━━━━━━━━━━━\nManage Logic 1, 2, and 3:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
