"""
Header Refresh Manager - Auto-Update Sticky Headers

Manages background refresh of sticky headers on active menus.

Version: 1.1.1 (Event Loop Fix)
Created: 2026-01-21
Part of: TELEGRAM_V5_STICKY_HEADER
"""

import asyncio
import logging
from typing import Dict
from ..core.sticky_header_builder import StickyHeaderBuilder

logger = logging.getLogger(__name__)

class HeaderRefreshManager:
    """Manages periodic updates of sticky headers"""

    def __init__(self, bot_instance, refresh_interval: int = 5):
        self.bot = bot_instance
        self.interval = refresh_interval
        self.active_messages: Dict[int, int] = {} # {chat_id: message_id}
        self.builder = StickyHeaderBuilder()
        self._running = False
        self._task = None

        # Determine dependencies for builder if possible
        if hasattr(bot_instance, 'trading_engine'):
             self.builder.set_dependencies(
                 mt5_client=getattr(bot_instance.trading_engine, 'mt5_client', None),
                 trading_engine=bot_instance.trading_engine
             )

    def start(self):
        """Start refresh loop safely"""
        if not self._running:
            self._running = True
            try:
                loop = asyncio.get_running_loop()
                self._task = loop.create_task(self._refresh_loop())
                logger.info("[HeaderRefresh] Started background refresh loop")
            except RuntimeError:
                # No running loop, defer start?
                # This happens if called during init before main loop.
                # Just ignore, MultiBotManager.start_bots will eventually run.
                logger.warning("[HeaderRefresh] Could not start refresh loop: No event loop")
                self._running = False

    def stop(self):
        """Stop refresh loop"""
        self._running = False
        if self._task:
            self._task.cancel()

    def register_message(self, chat_id: int, message_id: int):
        """Register a message for auto-updates (overwrites previous for chat)"""
        self.active_messages[chat_id] = message_id

    def unregister(self, chat_id: int):
        """Stop updating for a chat"""
        if chat_id in self.active_messages:
            del self.active_messages[chat_id]

    async def _refresh_loop(self):
        """Main loop"""
        while self._running:
            await asyncio.sleep(self.interval)

            # Create snapshot
            items = list(self.active_messages.items())
            if not items:
                continue

            # Logic implementation placeholder...
            pass
