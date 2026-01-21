"""
Base Command Handler - Abstract Base Class for Command Handlers

Version: 1.2.0 (Header Refresh Integration)
Created: 2026-01-21
Part of: TELEGRAM_V5_CORE
"""

from abc import ABC, abstractmethod
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Optional, Dict, Any
import logging

from ..interceptors.plugin_context_manager import PluginContextManager
from .conversation_state_manager import state_manager
from .sticky_header_builder import StickyHeaderBuilder

logger = logging.getLogger(__name__)

class BaseCommandHandler(ABC):
    """Base class for all Telegram command handlers"""

    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.plugin_context = PluginContextManager
        self.state_manager = state_manager

        # Init header builder
        if hasattr(self.bot, 'sticky_header'):
            self.sticky_header = self.bot.sticky_header
        else:
            self.sticky_header = StickyHeaderBuilder(
                mt5_client=getattr(self.bot, 'mt5_client', None),
                trading_engine=getattr(self.bot, 'trading_engine', None)
            )

        # Handler Configuration
        self.command_name = None
        self.requires_plugin_selection = False
        self.auto_plugin_context = None

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Main handler method.
        Standardizes plugin selection flow.
        """
        chat_id = update.effective_chat.id

        try:
            # 1. Auto-set context if defined
            if self.auto_plugin_context:
                self.plugin_context.set_plugin_context(
                    chat_id,
                    self.auto_plugin_context,
                    self.command_name
                )

            # 2. Check plugin selection requirement
            elif self.requires_plugin_selection:
                if not self.plugin_context.has_active_context(chat_id):
                    await self.show_plugin_selection(update, context)
                    return

            # 3. Execute command logic
            await self.execute(update, context)

        except Exception as e:
            logger.error(f"Error in {self.command_name}: {e}", exc_info=True)
            await self.send_error_message(update, str(e))

    @abstractmethod
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute command logic."""
        pass

    async def show_plugin_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show standard plugin selection screen"""
        keyboard = [
            [
                InlineKeyboardButton("🔵 V3 Only", callback_data=f"plugin_select_v3_{self.command_name}"),
                InlineKeyboardButton("🟢 V6 Only", callback_data=f"plugin_select_v6_{self.command_name}"),
            ],
            [
                InlineKeyboardButton("🔷 Both Plugins", callback_data=f"plugin_select_both_{self.command_name}"),
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="nav_main_menu"),
            ]
        ]

        header = self.sticky_header.build_header(style='compact')
        text = (
            f"{header}\n"
            f"🔌 **SELECT PLUGIN FOR /{self.command_name.upper()}**\n\n"
            f"Please select which plugin context to use:"
        )

        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def send_message_with_header(self, chat_id: int, content: str, keyboard=None, header_style='full'):
        """Send message with sticky header and register for updates"""
        header = self.sticky_header.build_header(style=header_style)
        full_text = f"{header}\n{content}"

        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        msg = await self.bot.send_message(
            chat_id=chat_id,
            text=full_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

        # Register for refresh if manager exists
        if msg and hasattr(self.bot, 'header_refresh_manager'):
            self.bot.header_refresh_manager.register_message(chat_id, msg.message_id)

    async def edit_message_with_header(self, update: Update, content: str, keyboard=None, header_style='compact'):
        """Edit existing message with header"""
        header = self.sticky_header.build_header(style=header_style)
        full_text = f"{header}\n{content}"
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(
                    text=full_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                # Register for refresh
                if hasattr(self.bot, 'header_refresh_manager'):
                    self.bot.header_refresh_manager.register_message(
                        update.effective_chat.id,
                        update.callback_query.message.message_id
                    )
            except Exception as e:
                 logger.warning(f"Edit failed, sending new: {e}")
                 await self.send_message_with_header(
                     update.effective_chat.id, content, keyboard, header_style
                 )
        else:
            await self.send_message_with_header(
                update.effective_chat.id, content, keyboard, header_style
            )

    async def send_error_message(self, update: Update, error_text: str):
        """Send standardized error message"""
        text = f"🚨 **ERROR**\n\n{error_text}\n\nPlease try again."
        await update.message.reply_text(text, parse_mode='Markdown')
