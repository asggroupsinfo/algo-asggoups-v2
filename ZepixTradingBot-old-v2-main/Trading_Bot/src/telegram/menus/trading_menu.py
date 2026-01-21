"""
Trading Menu - Level 1 Navigation

Implements the Trading Control submenu.
src/telegram/menus/trading_menu.py
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..core.base_menu_builder import BaseMenuBuilder
from ..core.button_builder import ButtonBuilder as Btn

class TradingMenu(BaseMenuBuilder):

    def build_menu(self) -> dict:
        """Build the Trading Control menu"""

        buttons = [
            Btn.create_button("📍 Positions", "trading_positions"),
            Btn.create_button("💰 P&L", "trading_pnl"),
            Btn.create_button("💵 Balance", "trading_balance"),
            Btn.create_button("💎 Equity", "trading_equity"),
            Btn.create_button("📊 Margin", "trading_margin"),
            Btn.create_button("🎯 Trades", "trading_trades"),
            Btn.create_button("🔺 Buy", "trading_buy_start"),
            Btn.create_button("🔻 Sell", "trading_sell_start"),
            Btn.create_button("❌ Close", "trading_close"),
            Btn.create_button("🗑️ Close All", "trading_closeall"),
            Btn.create_button("📋 Orders", "trading_orders"),
            Btn.create_button("📜 History", "trading_history"),
            Btn.create_button("💱 Symbols", "trading_symbols"),
            Btn.create_button("💲 Price", "trading_price"),
            Btn.create_button("📏 Spread", "trading_spread"),
            Btn.create_button("✂️ Partial", "trading_partial"),
            Btn.create_button("📡 Signals", "trading_signals"),
            Btn.create_button("🔍 Filters", "trading_filters")
        ]

        # Grid layout (2 cols)
        menu = Btn.build_menu(buttons, n_cols=2)

        # Add Navigation
        menu = Btn.add_navigation(menu)

        return {
            "text": "📊 **TRADING CONTROL**\n━━━━━━━━━━━━━━━━━━━━━━━━\nSelect an action:",
            "reply_markup": InlineKeyboardMarkup(menu)
        }
