"""
Positions Handler - Manage Active Trades

Display active positions with filtering by plugin/strategy.
Migrates logic from legacy handle_trades.

Version: 1.0.0
Created: 2026-01-21
Part of: TELEGRAM_V5_CORE
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...core.base_command_handler import BaseCommandHandler

class PositionsHandler(BaseCommandHandler):

    def __init__(self, bot):
        super().__init__(bot)
        self.command_name = "positions"
        self.requires_plugin_selection = False # Allow viewing all by default

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Fetch and display open positions"""

        # 1. Get Context (Optional filtering)
        chat_id = update.effective_chat.id
        plugin_filter = self.plugin_context.get_plugin_context(chat_id)

        # 2. Fetch Trades
        if not self.bot.db:
            await self.send_error_message(update, "Database not available")
            return

        trades = self.bot.db.get_open_trades()
        if not trades:
            await self.send_message_with_header(chat_id, "ℹ️ **NO ACTIVE TRADES**\n\nYour portfolio is currently empty.")
            return

        # 3. Filter Trades
        filtered_trades = []
        for t in trades:
            # Assume trade object has 'magic' or 'comment' to identify plugin
            # Logic: V3 (Magic < 6000?), V6 (Magic >= 6000?) - Just an example assumption
            # For now, show all.
            filtered_trades.append(t)

        # 4. Build Display
        total_pnl = sum(t.pnl for t in filtered_trades)
        count = len(filtered_trades)

        text = (
            f"📈 **ACTIVE POSITIONS ({count})**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )

        for t in filtered_trades:
            # Emoji based on PnL
            emoji = "🟢" if t.pnl >= 0 else "🔴"
            text += (
                f"{emoji} **{t.symbol}** {t.direction.upper()}\n"
                f"   L: {t.lots} | Entry: {t.open_price}\n"
                f"   PnL: **${t.pnl:.2f}**\n\n"
            )

        text += f"━━━━━━━━━━━━━━━━━━━━━━━━\n💰 **Total PnL: ${total_pnl:.2f}**"

        # 5. Actions Menu
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="trading_positions"),
                InlineKeyboardButton("❌ Close All", callback_data="trading_closeall")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="menu_trading")
            ]
        ]

        # 6. Send/Edit
        await self.edit_message_with_header(update, text, keyboard)
