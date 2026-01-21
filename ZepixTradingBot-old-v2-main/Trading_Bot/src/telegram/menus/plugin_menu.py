"""
Plugin Menu - Level 1 Navigation

Implements the Plugin Management submenu.
src/telegram/menus/plugin_menu.py
"""

from telegram import InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class PluginMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the Plugin menu"""

        buttons = [
            Btn.create_button("🔌 Status", "plugin_status"),
            Btn.create_button("⚡ Toggle All", "plugin_toggle"),
            Btn.create_button("🔵 V3 Toggle", "plugin_v3_toggle"),
            Btn.create_button("🟢 V6 Toggle", "plugin_v6_toggle"),
            Btn.create_button("⚙️ Config", "plugin_config"),
            Btn.create_button("🔄 Reload", "plugin_reload")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "🔌 **PLUGIN MANAGER**\n━━━━━━━━━━━━━━━━━━━━━━━━\nManage Strategy Plugins:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
