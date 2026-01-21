"""
Risk Settings Handler - View/Edit Risk

Displays current risk configuration.

Version: 1.0.0
Created: 2026-01-21
Part of: TELEGRAM_V5_CORE
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...core.base_command_handler import BaseCommandHandler

class RiskSettingsHandler(BaseCommandHandler):

    def __init__(self, bot):
        super().__init__(bot)
        self.command_name = "risk"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        # Mock Data
        lot_size = 0.01
        daily_limit = 500.0
        max_dd = 10.0

        if self.bot.risk_manager:
            # fetch real data if available
            pass

        text = (
            "⚠️ **RISK SETTINGS**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📏 **Lot Size:** `{lot_size}`\n"
            f"🛑 **Daily Limit:** `${daily_limit}`\n"
            f"📉 **Max Drawdown:** `{max_dd}%`\n\n"
            "Select setting to modify:"
        )

        keyboard = [
            [
                InlineKeyboardButton("📏 Change Lot", callback_data="risk_setlot_start"),
                InlineKeyboardButton("🛑 Set Limit", callback_data="risk_dailylimit")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="menu_risk")
            ]
        ]

        await self.edit_message_with_header(update, text, keyboard)
