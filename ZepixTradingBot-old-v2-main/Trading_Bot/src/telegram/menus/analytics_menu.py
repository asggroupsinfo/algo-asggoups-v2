"""
Analytics Menu - Level 1 Navigation

Implements the Analytics submenu.
src/telegram/menus/analytics_menu.py
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class AnalyticsMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the Analytics menu"""

        buttons = [
            Btn.create_button("📅 Daily", "analytics_daily"),
            Btn.create_button("📅 Weekly", "analytics_weekly"),
            Btn.create_button("📅 Monthly", "analytics_monthly"),
            Btn.create_button("⚖️ Compare", "analytics_compare"),
            Btn.create_button("💱 Pairs", "analytics_pair_report"),
            Btn.create_button("♟️ Strategy", "analytics_strategy_report"),
            Btn.create_button("🎯 TP Stats", "analytics_tp_report"),
            Btn.create_button("💰 Profit", "analytics_profit_stats"),
            Btn.create_button("💾 Export", "analytics_export"),
            # New Commands
            Btn.create_button("🎯 Win Rate", "analytics_winrate"),
            Btn.create_button("💰 Avg Profit", "analytics_avgprofit"),
            Btn.create_button("📉 Avg Loss", "analytics_avgloss"),
            Btn.create_button("🏆 Best Day", "analytics_bestday"),
            Btn.create_button("❌ Worst Day", "analytics_worstday"),
            Btn.create_button("📊 Correlation", "analytics_correlation")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "📈 **ANALYTICS HUB**\n━━━━━━━━━━━━━━━━━━━━━━━━\nSelect Report:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
