"""
Plugin Selection Menu - V5 Plugin Selection UI

Displays the plugin selection menu when intercepted.

Version: 1.0.0
Created: 2026-01-21
Part of: TELEGRAM_V5_PLUGIN_LAYER
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from .button_builder import ButtonBuilder
from .sticky_header_builder import StickyHeaderBuilder

class PluginSelectionMenu:

    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.btn = ButtonBuilder

        # Init header builder if not present
        if hasattr(self.bot, 'sticky_header'):
            self.header = self.bot.sticky_header
        else:
            self.header = StickyHeaderBuilder()

    async def show_selection_menu(self, update: Update, command: str, args: list = None):
        """Show the plugin selection menu"""
        chat_id = update.effective_chat.id

        # Clean command for callback (remove /)
        cmd_clean = command.replace('/', '')

        # Buttons
        buttons = [
            self.btn.create_button("🔵 V3 Combined", f"plugin_select_v3_{cmd_clean}"),
            self.btn.create_button("🟢 V6 Price Action", f"plugin_select_v6_{cmd_clean}"),
            self.btn.create_button("🔷 Both Plugins", f"plugin_select_both_{cmd_clean}")
        ]

        # Layout: V3 | V6 on row 1, Both on row 2
        keyboard = [
            [buttons[0], buttons[1]],
            [buttons[2]],
            [self.btn.create_button("❌ Cancel", "nav_main_menu")]
        ]

        # Header
        header_text = self.header.build_header(style='compact')

        text = (
            f"{header_text}\n"
            f"🔌 **SELECT PLUGIN CONTEXT**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Command: `/{cmd_clean.upper()}`\n\n"
            f"Please select which strategy plugin to apply this command to:"
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
        elif update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
