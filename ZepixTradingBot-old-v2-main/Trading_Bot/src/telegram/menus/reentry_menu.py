"""
Re-Entry Menu - Level 1 Navigation

Implements the Re-Entry System submenu.
src/telegram/menus/reentry_menu.py
"""

from telegram import InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class ReEntryMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the Re-Entry menu"""

        buttons = [
            Btn.create_button("🔄 Status", "reentry_status"),
            Btn.create_button("⚡ Toggle", "reentry_toggle"),
            Btn.create_button("🤖 Autonomous", "reentry_autonomous"),
            Btn.create_button("⛓️ Chains", "reentry_chains"),
            Btn.create_button("🎯 TP Cont.", "reentry_tp_cont"),
            Btn.create_button("🛡️ SL Hunt", "reentry_sl_hunt"),
            Btn.create_button("📊 Stats", "reentry_recovery_stats"),
            Btn.create_button("⚙️ Config", "reentry_config")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "🔄 **RE-ENTRY SYSTEM**\n━━━━━━━━━━━━━━━━━━━━━━━━\nManage Recovery & Continuity:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
