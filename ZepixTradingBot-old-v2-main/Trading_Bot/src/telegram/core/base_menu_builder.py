"""
Base Menu Builder - Abstract Base Class for Menus

Version: 1.1.0
Created: 2026-01-21
Part of: TELEGRAM_V5_CORE
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from .button_builder import ButtonBuilder

class BaseMenuBuilder(ABC):
    """Base class for all menu builders"""

    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.btn = ButtonBuilder

    @abstractmethod
    def build_menu(self, *args, **kwargs) -> Dict:
        """
        Build the menu.
        Returns dict with 'text' and 'reply_markup'
        """
        pass

    async def send_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Standard method to send/edit menu with sticky header"""
        menu_data = self.build_menu(**kwargs)

        if update.callback_query:
            await self.bot.edit_message_with_header(
                update,
                menu_data["text"],
                menu_data["reply_markup"]
            )
        else:
            # Command trigger (/start)
            # Construct header manually since we're sending a new message
            header = self.bot.sticky_header.build_header(
                bot_status="🟢 Active" if not self.bot.is_paused else "🔴 Paused",
                account_info=f"Risk: {self.bot._get_risk_usage()}%"
            )
            full_text = f"{header}\n{menu_data['text']}"
            await self.bot.send_message(full_text, menu_data["reply_markup"])

    def build_plugin_selection_menu(self, command: str) -> List[List[InlineKeyboardButton]]:
        """Standard plugin selection menu"""
        buttons = [
            self.btn.create_button("🔵 V3 Only", f"plugin_select_v3_{command}"),
            self.btn.create_button("🟢 V6 Only", f"plugin_select_v6_{command}"),
            self.btn.create_button("🔷 Both Plugins", f"plugin_select_both_{command}")
        ]

        menu = self.btn.build_menu(buttons, n_cols=2) # 2 cols: V3, V6 on top row, Both on next

        # Adjust layout: V3, V6 on row 1; Both on row 2
        menu = [
            [buttons[0], buttons[1]],
            [buttons[2]]
        ]

        return self.btn.add_navigation(menu, back_callback="nav_main_menu")
