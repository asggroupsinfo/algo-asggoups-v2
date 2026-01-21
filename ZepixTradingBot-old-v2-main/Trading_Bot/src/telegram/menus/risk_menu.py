"""
Risk Menu - Level 1 Navigation

Implements the Risk Management submenu.
src/telegram/menus/risk_menu.py
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class RiskMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the Risk Management menu"""

        buttons = [
            Btn.create_button("⚙️ Risk Menu", "risk_menu"),
            Btn.create_button("📊 Set Lot", "risk_setlot_start"),
            Btn.create_button("🛑 Set SL", "risk_setsl_start"),
            Btn.create_button("🎯 Set TP", "risk_settp_start"),
            Btn.create_button("📉 Daily Limit", "risk_dailylimit"),
            Btn.create_button("⛔ Max Loss", "risk_maxloss"),
            Btn.create_button("🎯 Max Profit", "risk_maxprofit"),
            Btn.create_button("🎚️ Risk Tier", "risk_risktier"),
            Btn.create_button("🛡️ SL System", "risk_slsystem"),
            Btn.create_button("📈 Trail SL", "risk_trailsl"),
            Btn.create_button("⚖️ Breakeven", "risk_breakeven"),
            Btn.create_button("🛡️ Protection", "risk_protection"),
            Btn.create_button("✖️ Multiplier", "risk_multiplier"),
            Btn.create_button("📊 Max Trades", "risk_maxtrades"),
            Btn.create_button("📉 Drawdown", "risk_drawdownlimit")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "🛡️ **RISK MANAGEMENT**\n━━━━━━━━━━━━━━━━━━━━━━━━\nSelect an action:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
