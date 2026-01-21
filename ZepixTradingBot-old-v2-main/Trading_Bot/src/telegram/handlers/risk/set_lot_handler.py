"""
Set Lot Handler - Change Lot Size

Handles lot size modification.

Version: 1.0.0
Created: 2026-01-21
Part of: TELEGRAM_V5_CORE
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...core.base_command_handler import BaseCommandHandler

class SetLotHandler(BaseCommandHandler):

    def __init__(self, bot):
        super().__init__(bot)
        self.command_name = "setlot"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        text = (
            "📏 **SET LOT SIZE**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Current: `0.01`\n\n"
            "Select new lot size:"
        )

        keyboard = [
            [
                InlineKeyboardButton("0.01", callback_data="risk_setlot_0.01"),
                InlineKeyboardButton("0.02", callback_data="risk_setlot_0.02"),
                InlineKeyboardButton("0.05", callback_data="risk_setlot_0.05")
            ],
            [
                InlineKeyboardButton("0.10", callback_data="risk_setlot_0.10"),
                InlineKeyboardButton("0.20", callback_data="risk_setlot_0.20"),
                InlineKeyboardButton("0.50", callback_data="risk_setlot_0.50")
            ],
            [
                InlineKeyboardButton("📝 Custom Input", callback_data="risk_setlot_custom"),
                InlineKeyboardButton("⬅️ Back", callback_data="menu_risk")
            ]
        ]

        await self.edit_message_with_header(update, text, keyboard)
