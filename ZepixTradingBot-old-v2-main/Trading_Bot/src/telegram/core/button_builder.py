"""
Button Builder - Standardized Button Creation Utility

Ensures all buttons follow size guidelines and callback naming conventions.
Supports pagination and grid layouts.

Version: 1.0.0
Created: 2026-01-21
Part of: TELEGRAM_V5_ZERO_TYPING_UI
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Union, Optional
import logging

logger = logging.getLogger(__name__)

class ButtonBuilder:
    """Utility for creating standardized inline keyboards"""

    @staticmethod
    def create_button(text: str, callback_data: str) -> InlineKeyboardButton:
        """Create a single button with validation"""
        if len(callback_data.encode('utf-8')) > 64:
            logger.warning(f"Callback data too long: {callback_data} ({len(callback_data)} bytes)")
            # Truncate or warn? Warn for now.

        return InlineKeyboardButton(text, callback_data=callback_data)

    @staticmethod
    def build_menu(buttons: List[InlineKeyboardButton], n_cols: int = 2) -> List[List[InlineKeyboardButton]]:
        """
        Arrange buttons into a grid menu.

        Args:
            buttons: List of buttons
            n_cols: Number of columns

        Returns:
            List of button rows
        """
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        return menu

    @staticmethod
    def add_navigation(menu: List[List[InlineKeyboardButton]],
                      back_callback: str = "nav_back",
                      home_callback: str = "nav_main_menu") -> List[List[InlineKeyboardButton]]:
        """Add standard Back/Home navigation row"""
        nav_row = [
            InlineKeyboardButton("⬅️ Back", callback_data=back_callback),
            InlineKeyboardButton("🏠 Main Menu", callback_data=home_callback)
        ]
        menu.append(nav_row)
        return menu

    @staticmethod
    def create_paginated_menu(
        items: List[Dict[str, str]],
        page: int = 0,
        callback_prefix: str = "item",
        items_per_page: int = 10,
        n_cols: int = 2
    ) -> InlineKeyboardMarkup:
        """
        Create a paginated menu from a list of items.

        Args:
            items: List of dicts {'text': 'Label', 'id': 'value'}
            page: Current page index (0-based)
            callback_prefix: Prefix for item callbacks (e.g. 'symbol_select')
            items_per_page: Max items per page
            n_cols: Columns per row

        Returns:
            InlineKeyboardMarkup
        """
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_items = items[start_idx:end_idx]

        buttons = []
        for item in page_items:
            # item is expected to have 'text' and 'id'
            # callback format: {prefix}_{id}
            cb_data = f"{callback_prefix}_{item['id']}"
            buttons.append(InlineKeyboardButton(item['text'], callback_data=cb_data))

        menu = ButtonBuilder.build_menu(buttons, n_cols)

        # Pagination Controls
        pagination_row = []
        if page > 0:
            pagination_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{callback_prefix}_page_{page-1}"))

        if end_idx < len(items):
            pagination_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"{callback_prefix}_page_{page+1}"))

        if pagination_row:
            menu.append(pagination_row)

        # Add standard navigation
        menu = ButtonBuilder.add_navigation(menu)

        return InlineKeyboardMarkup(menu)

    @staticmethod
    def create_confirmation_menu(confirm_callback: str, cancel_callback: str = "nav_back") -> InlineKeyboardMarkup:
        """Create standard confirmation menu"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=confirm_callback),
                InlineKeyboardButton("❌ Cancel", callback_data=cancel_callback)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
