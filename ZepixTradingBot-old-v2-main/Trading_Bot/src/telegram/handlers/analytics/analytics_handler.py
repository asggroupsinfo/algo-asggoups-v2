"""
Analytics Handler - Performance & Reporting

Implements all analytics commands: daily, weekly, compare, export.

Version: 1.1.0 (Logic Integration)
Created: 2026-01-21
Part of: TELEGRAM_V5_CORE
"""

from telegram import Update
from telegram.ext import ContextTypes
from ...core.base_command_handler import BaseCommandHandler

class AnalyticsHandler(BaseCommandHandler):

    def __init__(self, bot):
        super().__init__(bot)
        self.command_name = "analytics"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if hasattr(self.bot, 'handle_analytics_menu'):
            await self.bot.handle_analytics_menu(update, context)

    async def handle_daily(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if hasattr(self.bot, 'handle_daily'):
            await self.bot.handle_daily(update, context)

    async def handle_weekly(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if hasattr(self.bot, 'handle_weekly'):
            await self.bot.handle_weekly(update, context)

    async def handle_compare(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if hasattr(self.bot, 'handle_compare'):
            await self.bot.handle_compare(update, context)

    async def handle_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if hasattr(self.bot, 'handle_export'):
            await self.bot.handle_export(update, context)
