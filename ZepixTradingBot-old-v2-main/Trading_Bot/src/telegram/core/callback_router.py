"""
Callback Router - Central Dispatcher for Button Clicks

Routes callback queries to appropriate handlers based on prefix conventions.
Prevents "Unknown Callback" errors.

Version: 1.2.0 (V5 Menu System Complete)
Created: 2026-01-21
Part of: TELEGRAM_V5_CORE
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class CallbackRouter:
    """Central router for all callback queries"""

    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.handlers = {} # Map prefix -> handler function
        self.menus = {}    # Map name -> Menu Instance

        # Register standard prefixes
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default routing table"""
        # System
        self.register_handler("system", self._route_system)

        # Navigation
        self.register_handler("nav", self._route_navigation)

        # Plugin Selection (Special logic)
        self.register_handler("plugin", self._route_plugin_selection)

        # Menu Navigation
        self.register_handler("menu", self._route_menu)

        # Domain Routes
        self.register_handler("trading", self._route_domain)
        self.register_handler("risk", self._route_domain)
        self.register_handler("v3", self._route_domain)
        self.register_handler("v6", self._route_domain)
        self.register_handler("analytics", self._route_domain)
        self.register_handler("reentry", self._route_domain)
        self.register_handler("profit", self._route_domain)
        self.register_handler("session", self._route_domain)
        self.register_handler("voice", self._route_domain)
        self.register_handler("settings", self._route_domain)

    def register_handler(self, prefix: str, handler_func):
        """Register a handler for a callback prefix"""
        self.handlers[prefix] = handler_func

    def register_menu(self, name: str, menu_instance):
        """Register a menu instance for routing"""
        self.menus[name] = menu_instance
        logger.info(f"[CallbackRouter] Registered menu: {name}")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Main entry point for callback routing.
        Returns True if handled, False otherwise.
        """
        query = update.callback_query
        data = query.data
        parts = data.split('_')

        if len(parts) < 2:
            return False

        prefix = parts[0]

        if prefix in self.handlers:
            try:
                # Always answer first
                try:
                    await query.answer()
                except:
                    pass

                await self.handlers[prefix](update, context)
                return True
            except Exception as e:
                logger.error(f"Error handling callback {data}: {e}", exc_info=True)
                return True

        return False

    # --- Routing Logic ---

    async def _route_system(self, update, context):
        data = update.callback_query.data
        action = data.replace("system_", "")

        handler_name = f"handle_system_{action}"
        if hasattr(self.bot, handler_name):
             await getattr(self.bot, handler_name)(update, context)
        else:
             # Fallback
             await self.bot.handle_status(update, context)

    async def _route_navigation(self, update, context):
        query = update.callback_query
        data = query.data

        if data == "nav_main_menu":
            if "main" in self.menus:
                await self.menus["main"].send_menu(update, context)
            else:
                await self.bot.handle_start(update, context)
        elif data == "nav_back":
            if "main" in self.menus:
                await self.menus["main"].send_menu(update, context)

    async def _route_plugin_selection(self, update, context):
        """Handle plugin selection callbacks (plugin_select_TYPE_COMMAND)"""
        query = update.callback_query
        data = query.data
        parts = data.split('_')

        # Check if it's actually a plugin menu command (plugin_status, etc)
        # The PluginMenu uses prefix 'plugin_'
        # Selection uses 'plugin_select_'

        if parts[1] != 'select':
            # It's a standard plugin command like plugin_status
            await self._route_domain(update, context)
            return

        if len(parts) < 4:
            return

        plugin_type = parts[2] # v3, v6, both
        command_name = "_".join(parts[3:]) # rest is command

        chat_id = update.effective_chat.id

        # Set context
        try:
            from ..interceptors.plugin_context_manager import set_user_plugin
            set_user_plugin(chat_id, plugin_type, command_name)
        except ImportError:
            pass

        # Execute command
        handler_name = f"handle_{command_name}"
        if hasattr(self.bot, handler_name):
            logger.info(f"Context set to {plugin_type}, executing {handler_name}")
            await getattr(self.bot, handler_name)(update, context)
        else:
            await query.edit_message_text(f"❌ Command handler not found: {command_name}")

    async def _route_menu(self, update, context):
        """Handle menu navigation (menu_trading, menu_risk, etc.)"""
        query = update.callback_query
        data = query.data
        if "_" not in data: return

        category = data.split('_')[1]

        if category in self.menus:
            await self.menus[category].send_menu(update, context)
        else:
            logger.warning(f"Menu category not found: {category}")
            await query.edit_message_text(f"⚠️ Menu not available: {category}")

    async def _route_domain(self, update, context):
        """Generic router for domain prefixes (trading_*, risk_*, v3_*)"""
        data = update.callback_query.data
        # data = prefix_action
        # we want to call handle_prefix_action

        # But some legacy handlers are named handle_action (e.g. handle_status)
        # New standard: handle_prefix_action (e.g. handle_trading_positions)

        parts = data.split('_', 1)
        if len(parts) < 2: return

        prefix = parts[0]
        action = parts[1]

        # 1. Try specific handler: handle_prefix_action
        handler_name = f"handle_{data}"
        if hasattr(self.bot, handler_name):
            await getattr(self.bot, handler_name)(update, context)
            return

        # 2. Try generic handler: handle_action (Legacy compatibility)
        handler_name_legacy = f"handle_{action}"
        if hasattr(self.bot, handler_name_legacy):
            await getattr(self.bot, handler_name_legacy)(update, context)
            return

        # 3. Try domain handler: handle_prefix_command
        # e.g. handle_trading_command(action) - not standard in python-telegram-bot

        await update.callback_query.edit_message_text(f"🛠️ {data} not implemented yet.")
