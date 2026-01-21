"""
Position Flow - Zero-Typing Position Management

Implements wizards for closing and modifying positions.
1. Close Selection (Partial/Full)
2. Modify SL/TP

Version: 1.1.0 (Global Breadcrumb Integration)
Created: 2026-01-21
Part of: TELEGRAM_V5_ZERO_TYPING_UI
"""

from telegram import Update
from telegram.ext import ContextTypes
from .base_flow import BaseFlow

class PositionFlow(BaseFlow):

    @property
    def flow_name(self) -> str:
        return "position_flow"

    async def start_close(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        state = self.state_manager.start_flow(chat_id, self.flow_name)
        state.add_data("action", "CLOSE")
        state.step = 0
        await self.show_step(update, context, 0)

    async def show_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
        breadcrumb = self._format_breadcrumb(["Select", "Confirm"], step)
        text = f"{breadcrumb}\n\nSelect position to close (Placeholder)"
        keyboard = [[self.btn.create_button("Cancel", "flow_pos_cancel")]]

        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=self.btn.create_confirmation_menu("flow_pos_confirm", "flow_pos_cancel"))

    async def process_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state):
        query = update.callback_query
        data = query.data
        if "flow_pos_confirm" in data:
            await query.edit_message_text("Position closed.")
            self.state_manager.clear_state(update.effective_chat.id)
        elif "flow_pos_cancel" in data:
            await self.cancel(update, context)
