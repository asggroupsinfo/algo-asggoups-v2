"""
Base Flow - Abstract Base Class for Conversation Flows

Version: 1.1.0 (Standardized Breadcrumbs)
Created: 2026-01-21
Part of: TELEGRAM_V5_ZERO_TYPING_UI
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..core.conversation_state_manager import state_manager
from ..core.button_builder import ButtonBuilder
from ..core.sticky_header_builder import StickyHeaderBuilder

class BaseFlow(ABC):
    """Base class for multi-step conversation flows"""

    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.state_manager = state_manager
        self.btn = ButtonBuilder

        if hasattr(self.bot, 'sticky_header'):
            self.header = self.bot.sticky_header
        else:
            self.header = StickyHeaderBuilder()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the flow"""
        chat_id = update.effective_chat.id
        self.state_manager.start_flow(chat_id, self.flow_name)
        await self.show_step(update, context, 0)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle flow callback"""
        chat_id = update.effective_chat.id
        state = self.state_manager.get_state(chat_id)

        if state.command != self.flow_name:
            return False

        await self.process_step(update, context, state)
        return True

    def _format_breadcrumb(self, steps: list, current: int) -> str:
        """
        Generate standardized breadcrumb trail.
        Example: ✅ Symbol → ▶️ Lot → ⏸️ Confirm
        """
        crumbs = []
        for i, label in enumerate(steps):
            if i < current:
                crumbs.append(f"✅ {label}")
            elif i == current:
                crumbs.append(f"▶️ {label}")
            else:
                crumbs.append(f"⏸️ {label}")
        return " → ".join(crumbs)

    @abstractmethod
    async def show_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
        """Show the current step UI"""
        pass

    @abstractmethod
    async def process_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state):
        """Process input for current step"""
        pass

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel flow"""
        chat_id = update.effective_chat.id
        self.state_manager.clear_state(chat_id)
        await self.bot.handle_start(update, context)

    @property
    @abstractmethod
    def flow_name(self) -> str:
        pass
