"""
Voice Handler - Audio Alerts

Implements voice control: mute, unmute, test.

Version: 1.1.0 (Logic Integration)
Created: 2026-01-21
Part of: TELEGRAM_V5_CORE
"""

from telegram import Update
from telegram.ext import ContextTypes
from ...core.base_command_handler import BaseCommandHandler

class VoiceHandler(BaseCommandHandler):

    def __init__(self, bot):
        super().__init__(bot)
        self.command_name = "voice"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if hasattr(self.bot, 'handle_voice_menu'):
            await self.bot.handle_voice_menu(update, context)

    async def handle_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if hasattr(self.bot, 'handle_voice_test'):
            await self.bot.handle_voice_test(update, context)

    async def handle_mute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if hasattr(self.bot, 'handle_mute'):
            await self.bot.handle_mute(update, context)

    async def handle_unmute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if hasattr(self.bot, 'handle_unmute'):
            await self.bot.handle_unmute(update, context)
