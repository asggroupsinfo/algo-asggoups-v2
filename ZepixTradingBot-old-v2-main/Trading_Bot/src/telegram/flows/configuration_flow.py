"""
Configuration Flow - Zero-Typing Settings Wizard

Implements wizards for multi-step configuration.

Version: 1.1.0 (Global Breadcrumb Integration)
Created: 2026-01-21
Part of: TELEGRAM_V5_ZERO_TYPING_UI
"""

from telegram import Update
from telegram.ext import ContextTypes
from .base_flow import BaseFlow

class ConfigurationFlow(BaseFlow):

    @property
    def flow_name(self) -> str:
        return "config_flow"

    async def start_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        state = self.state_manager.start_flow(chat_id, self.flow_name)
        state.step = 0
        await self.show_step(update, context, 0)

    async def show_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
        breadcrumb = self._format_breadcrumb(["Setting", "Value", "Confirm"], step)
        text = f"{breadcrumb}\n\nConfiguration Wizard (Placeholder)"
        keyboard = [[self.btn.create_button("Cancel", "flow_config_cancel")]]

        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=self.btn.create_confirmation_menu("flow_config_confirm", "flow_config_cancel"))

    async def process_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state):
        query = update.callback_query
        data = query.data
        if "flow_config_confirm" in data:
            await query.edit_message_text("Configuration saved.")
            self.state_manager.clear_state(update.effective_chat.id)
        elif "flow_config_cancel" in data:
            await self.cancel(update, context)
