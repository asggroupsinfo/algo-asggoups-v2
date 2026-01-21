"""
Close Handler - Close Positions

Handles manual closure of trades.

Version: 1.0.0
Created: 2026-01-21
Part of: TELEGRAM_V5_CORE
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...core.base_command_handler import BaseCommandHandler

class CloseHandler(BaseCommandHandler):

    def __init__(self, bot):
        super().__init__(bot)
        self.command_name = "close"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Show options to close
        text = (
            "❌ **CLOSE POSITIONS**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Select closure type:"
        )

        keyboard = [
            [
                InlineKeyboardButton("🗑️ Close ALL", callback_data="trading_closeall_confirm"),
                InlineKeyboardButton("💰 Close Profit", callback_data="trading_closeprofit")
            ],
            [
                InlineKeyboardButton("📉 Close Loss", callback_data="trading_closeloss"),
                InlineKeyboardButton("⬅️ Back", callback_data="menu_trading")
            ]
        ]

        await self.edit_message_with_header(update, text, keyboard)
