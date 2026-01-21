"""
Controller Bot - Independent V6 Architecture
Version: 3.7.0 (Full Handler Coverage)
Date: 2026-01-21

Uses python-telegram-bot v20+ (Async)
Handles System Commands and Admin Functions.
Integrates V5 Menu System and Sticky Headers.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, date
import sys
import os
import csv
import io

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from .base_bot import BaseIndependentBot
from src.telegram.core.callback_router import CallbackRouter
from src.telegram.core.sticky_header_builder import StickyHeaderBuilder
from src.telegram.core.conversation_state_manager import state_manager
from src.telegram.core.plugin_interceptor import CommandInterceptor
from src.telegram.interceptors.plugin_context_manager import PluginContextManager
from src.telegram.core.header_manager import HeaderManager
from src.telegram.core.command_registry import CommandRegistry

# Import All Menus
from src.telegram.menus.main_menu import MainMenu
from src.telegram.menus.trading_menu import TradingMenu
from src.telegram.menus.risk_menu import RiskMenu
from src.telegram.menus.system_menu import SystemMenu
from src.telegram.menus.v3_menu import V3StrategiesMenu
from src.telegram.menus.v6_menu import V6FramesMenu
from src.telegram.menus.analytics_menu import AnalyticsMenu
from src.telegram.menus.reentry_menu import ReEntryMenu
from src.telegram.menus.profit_menu import ProfitMenu
from src.telegram.menus.plugin_menu import PluginMenu
from src.telegram.menus.sessions_menu import SessionsMenu
from src.telegram.menus.voice_menu import VoiceMenu
from src.telegram.menus.settings_menu import SettingsMenu

# Import Handlers
from src.telegram.handlers.trading.positions_handler import PositionsHandler
from src.telegram.handlers.trading.orders_handler import OrdersHandler
from src.telegram.handlers.trading.close_handler import CloseHandler
from src.telegram.handlers.risk.risk_settings_handler import RiskSettingsHandler
from src.telegram.handlers.risk.set_lot_handler import SetLotHandler
from src.telegram.handlers.analytics.analytics_handler import AnalyticsHandler
from src.telegram.handlers.plugins.plugin_handler import PluginHandler
from src.telegram.handlers.system.session_handler import SessionHandler
from src.telegram.handlers.system.voice_handler import VoiceHandler
from src.telegram.handlers.system.settings_handler import SettingsHandler

# Import Flows
from src.telegram.flows.trading_flow import TradingFlow
from src.telegram.flows.risk_flow import RiskFlow

logger = logging.getLogger(__name__)

class ControllerBot(BaseIndependentBot):
    """
    Independent Controller Bot for Zepix V6.
    Handles all slash commands and admin interaction asynchronously.
    """
    
    def __init__(self, token: str, chat_id: str = None, config: Dict = None):
        super().__init__(token, "ControllerBot")
        self.startup_time = datetime.now()
        self.trading_engine = None  # To be injected
        self.is_paused = False
        self.chat_id = chat_id
        self.config = config or {}
        
        # --- V5 Foundation Components ---
        self.sticky_header = StickyHeaderBuilder()
        self.callback_router = CallbackRouter(self)
        self.state_manager = state_manager
        self.header_refresh_manager = HeaderManager(self) # Phase 4
        self.command_registry = CommandRegistry(self) # Phase 5

        # --- Plugin Selection System (Phase 3) ---
        self.command_interceptor = CommandInterceptor(self)
        self.plugin_context_manager = PluginContextManager

        # Initialize Menus
        self.main_menu = MainMenu(self)
        self.trading_menu = TradingMenu(self)
        self.risk_menu = RiskMenu(self)
        self.system_menu = SystemMenu(self)
        self.v3_menu = V3StrategiesMenu(self)
        self.v6_menu = V6FramesMenu(self)
        self.analytics_menu = AnalyticsMenu(self)
        self.reentry_menu = ReEntryMenu(self)
        self.profit_menu = ProfitMenu(self)
        self.plugin_menu = PluginMenu(self)
        self.session_menu = SessionsMenu(self)
        self.voice_menu = VoiceMenu(self)
        self.settings_menu = SettingsMenu(self)

        # Initialize Handlers
        self.positions_handler = PositionsHandler(self)
        self.orders_handler = OrdersHandler(self)
        self.close_handler = CloseHandler(self)
        self.risk_settings_handler = RiskSettingsHandler(self)
        self.set_lot_handler = SetLotHandler(self)
        self.analytics_handler = AnalyticsHandler(self)
        self.plugin_handler = PluginHandler(self)
        self.session_handler = SessionHandler(self)
        self.voice_handler = VoiceHandler(self)
        self.settings_handler = SettingsHandler(self)

        # Initialize Flows
        self.trading_flow = TradingFlow(self)
        self.risk_flow = RiskFlow(self)

        # Register Menus with Router (Key matches 'menu_KEY' callback)
        self.callback_router.register_menu("main", self.main_menu)
        self.callback_router.register_menu("trading", self.trading_menu)
        self.callback_router.register_menu("risk", self.risk_menu)
        self.callback_router.register_menu("system", self.system_menu)
        self.callback_router.register_menu("v3", self.v3_menu)
        self.callback_router.register_menu("v6", self.v6_menu)
        self.callback_router.register_menu("analytics", self.analytics_menu)
        self.callback_router.register_menu("reentry", self.reentry_menu)
        self.callback_router.register_menu("profit", self.profit_menu)
        self.callback_router.register_menu("plugin", self.plugin_menu)
        self.callback_router.register_menu("session", self.session_menu)
        self.callback_router.register_menu("voice", self.voice_menu)
        self.callback_router.register_menu("settings", self.settings_menu)

        logger.info("[ControllerBot] V5 Architecture (Full Stack) initialized")

        # --- Legacy / V6 Components (Optional) ---
        self.v6_menu_builder = None
        try:
            from src.telegram.v6_timeframe_menu_builder import V6TimeframeMenuBuilder
            self.v6_menu_builder = V6TimeframeMenuBuilder(self)
        except Exception as e:
            logger.warning(f"[ControllerBot] V6TimeframeMenuBuilder init failed: {e}")
        
    def set_dependencies(self, trading_engine):
        """Inject trading engine and its sub-managers"""
        self.trading_engine = trading_engine
        
        # Start header refresh
        if self.header_refresh_manager:
            self.header_refresh_manager.start()

        # Expose sub-managers for Menu system compatibility
        if trading_engine:
            self.mt5_client = getattr(trading_engine, 'mt5_client', None)
            self.risk_manager = getattr(trading_engine, 'risk_manager', None)
            self.pip_calculator = getattr(trading_engine, 'pip_calculator', None)
            self.dual_order_manager = getattr(trading_engine, 'dual_order_manager', None)
            self.profit_booking_manager = getattr(trading_engine, 'profit_booking_manager', None)
            self.reentry_manager = getattr(trading_engine, 'reentry_manager', None)
            self.trend_pulse_manager = getattr(trading_engine, 'trend_pulse_manager', None)
            self.db = getattr(trading_engine, 'db', None)
            
            # Inject dependencies into V6 Menu Builder
            if self.v6_menu_builder:
                self.v6_menu_builder.set_dependencies(trading_engine)

            # Register all commands in registry (Phase 5)
            self.command_registry.register_all()
            
        logger.info("[ControllerBot] Dependencies injected and sub-managers exposed")

    def _register_handlers(self):
        """Register all command handlers"""
        if not self.app:
            return

        # System Commands
        self.app.add_handler(CommandHandler("start", self.handle_start))
        self.app.add_handler(CommandHandler("menu", self.handle_start))
        self.app.add_handler(CommandHandler("help", self.handle_help))
        self.app.add_handler(CommandHandler("status", self.handle_status))

        # Action Commands (Wiring to Flows)
        self.app.add_handler(CommandHandler("buy", self.handle_buy_command))
        self.app.add_handler(CommandHandler("sell", self.handle_sell_command))

        # Legacy/Extra Commands (Keeping for compatibility)
        self.app.add_handler(CommandHandler("settings", self.handle_settings))
        self.app.add_handler(CommandHandler("stop", self.handle_stop_bot))
        self.app.add_handler(CommandHandler("resume", self.handle_resume_bot))
        self.app.add_handler(CommandHandler("pause", self.handle_pause_bot))
        self.app.add_handler(CommandHandler("restart", self.handle_restart))
        self.app.add_handler(CommandHandler("info", self.handle_info))
        self.app.add_handler(CommandHandler("version", self.handle_version))
        self.app.add_handler(CommandHandler("dashboard", self.handle_dashboard))

        # V6 Commands
        self.app.add_handler(CommandHandler("v6_menu", self.handle_v6_menu))
        self.app.add_handler(CommandHandler("v6_status", self.handle_v6_status))
        
        # Callback Handler - Routes to V5 CallbackRouter
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        logger.info("[ControllerBot] Handlers registered")

    # =========================================================================
    # CORE HANDLERS
    # =========================================================================

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - Entry point to V5 Menu System"""
        user_id = update.effective_user.id
        logger.info(f"[ControllerBot] /start called by {user_id}")
        await self.main_menu.send_menu(update, context)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries via Router"""
        query = update.callback_query
        data = query.data
        logger.info(f"[ControllerBot] Callback: {data}")
        
        # 1. Intercept Plugin Selection (Phase 3)
        if data.startswith("plugin_select_"):
            result = await self.command_interceptor.handle_selection(update, context)
            if result:
                plugin_name = result['plugin'].upper()
                await query.edit_message_text(f"✅ Context set to **{plugin_name}**\n\nPlease retry your command.", parse_mode='Markdown')
            return

        # 2. Check for Active Flows (Doc 4 Priority)
        if data.startswith("flow_trade"):
            if await self.trading_flow.handle_callback(update, context):
                return
        if data.startswith("flow_risk"):
            if await self.risk_flow.handle_callback(update, context):
                return

        # 3. Try V5 Router
        if await self.callback_router.handle_callback(update, context):
            return

        # 4. Fallback to Legacy Handlers
        try:
            await query.answer()
        except:
            pass

        if data == "dashboard":
            await self.handle_dashboard(update, context)
        elif data == "settings":
            await self.handle_settings(update, context)
        elif data == "status":
            await self.handle_status(update, context)
        elif data == "help":
            await self.handle_help(update, context)

        # V6 Menu Fallback
        elif self.v6_menu_builder and (data.startswith("v6_") or data.startswith("tf")):
            await self._handle_v6_callback(update, context)

        else:
            await query.edit_message_text(f"❓ Unknown option: {data}")

    # =========================================================================
    # ACTION HANDLERS (Called by Router/Commands)
    # =========================================================================

    # --- Flow Triggers ---
    async def handle_buy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trigger Buy Wizard (Intercepted)"""
        # Phase 3: Intercept
        if await self.command_interceptor.intercept(update, context, "/buy"):
            return

        await self.trading_flow.start_buy(update, context)

    async def handle_sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trigger Sell Wizard (Intercepted)"""
        if await self.command_interceptor.intercept(update, context, "/sell"):
            return

        await self.trading_flow.start_sell(update, context)

    async def handle_trading_buy_start(self, update, context):
        """Callback Trigger for Buy Wizard"""
        # Callbacks also need interception if no context
        if await self.command_interceptor.intercept(update, context, "/buy"):
            return
        await self.trading_flow.start_buy(update, context)

    async def handle_trading_sell_start(self, update, context):
        """Callback Trigger for Sell Wizard"""
        if await self.command_interceptor.intercept(update, context, "/sell"):
            return
        await self.trading_flow.start_sell(update, context)

    async def handle_risk_setlot_start(self, update, context):
        """Callback Trigger for Lot Wizard"""
        if await self.command_interceptor.intercept(update, context, "/setlot"):
            return
        await self.risk_flow.start_set_lot(update, context)

    # --- Trading Handlers ---
    async def handle_trading_positions(self, update, context):
        await self.positions_handler.handle(update, context)

    async def handle_trading_orders(self, update, context):
        await self.orders_handler.handle(update, context)

    async def handle_trading_close(self, update, context):
        await self.close_handler.handle(update, context)

    async def handle_trading_closeall(self, update, context):
        await self.close_handler.handle(update, context)

    # --- Risk Handlers ---
    async def handle_risk_menu(self, update, context):
        await self.risk_settings_handler.handle(update, context)

    # --- Analytics Handlers ---
    async def handle_analytics_daily(self, update, context):
        await self.analytics_handler.handle_daily(update, context)

    async def handle_analytics_weekly(self, update, context):
        await self.analytics_handler.handle_weekly(update, context)

    async def handle_analytics_compare(self, update, context):
        await self.analytics_handler.handle_compare(update, context)

    async def handle_analytics_export(self, update, context):
        await self.analytics_handler.handle_export(update, context)

    async def handle_analytics_winrate(self, update, context):
        await self.analytics_handler.handle_winrate(update, context)

    async def handle_analytics_avgprofit(self, update, context):
        await self.analytics_handler.handle_avgprofit(update, context)

    async def handle_analytics_avgloss(self, update, context):
        await self.analytics_handler.handle_avgloss(update, context)

    async def handle_analytics_bestday(self, update, context):
        await self.analytics_handler.handle_bestday(update, context)

    async def handle_analytics_worstday(self, update, context):
        await self.analytics_handler.handle_worstday(update, context)

    async def handle_analytics_correlation(self, update, context):
        await self.analytics_handler.handle_correlation(update, context)

    # --- Plugin Handlers ---
    async def handle_plugin_enable(self, update, context):
        await self.plugin_handler.handle_enable(update, context)

    async def handle_plugin_disable(self, update, context):
        await self.plugin_handler.handle_disable(update, context)

    # --- Session Handlers ---
    async def handle_session_london(self, update, context):
        await self.session_handler.handle_london(update, context)

    async def handle_session_newyork(self, update, context):
        await self.session_handler.handle_newyork(update, context)

    async def handle_session_tokyo(self, update, context):
        await self.session_handler.handle_tokyo(update, context)

    # --- Voice Handlers ---
    async def handle_voice_test(self, update, context):
        await self.voice_handler.handle_test(update, context)

    async def handle_voice_mute(self, update, context):
        await self.voice_handler.handle_mute(update, context)

    async def handle_voice_unmute(self, update, context):
        await self.voice_handler.handle_unmute(update, context)
    
    # =========================================================================
    # RESTORED LEGACY HANDLERS (Bridge Strategy)
    # =========================================================================
    
    # --- V3 Logic Toggles ---
    async def handle_v3_logic1_on(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enable V3 Logic 1"""
        if self.trading_engine:
            self.trading_engine.enable_logic(1)
        await self.edit_message_with_header(update, "✅ <b>V3 LOGIC 1 ENABLED</b>", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_v3")]])

    async def handle_v3_logic1_off(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Disable V3 Logic 1"""
        if self.trading_engine:
            self.trading_engine.disable_logic(1)
        await self.edit_message_with_header(update, "❌ <b>V3 LOGIC 1 DISABLED</b>", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_v3")]])

    async def handle_v3_logic2_on(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enable V3 Logic 2"""
        if self.trading_engine:
            self.trading_engine.enable_logic(2)
        await self.edit_message_with_header(update, "✅ <b>V3 LOGIC 2 ENABLED</b>", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_v3")]])

    async def handle_v3_logic2_off(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Disable V3 Logic 2"""
        if self.trading_engine:
            self.trading_engine.disable_logic(2)
        await self.edit_message_with_header(update, "❌ <b>V3 LOGIC 2 DISABLED</b>", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_v3")]])

    async def handle_v3_logic3_on(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enable V3 Logic 3"""
        if self.trading_engine:
            self.trading_engine.enable_logic(3)
        await self.edit_message_with_header(update, "✅ <b>V3 LOGIC 3 ENABLED</b>", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_v3")]])

    async def handle_v3_logic3_off(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Disable V3 Logic 3"""
        if self.trading_engine:
            self.trading_engine.disable_logic(3)
        await self.edit_message_with_header(update, "❌ <b>V3 LOGIC 3 DISABLED</b>", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_v3")]])

    async def handle_v3_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show V3 Status"""
        # Logic to check status
        l1 = "✅" if self.trading_engine and self.trading_engine.logic_states.get(1, True) else "❌"
        l2 = "✅" if self.trading_engine and self.trading_engine.logic_states.get(2, True) else "❌"
        l3 = "✅" if self.trading_engine and self.trading_engine.logic_states.get(3, True) else "❌"

        text = (
            "🔵 <b>V3 STRATEGIES STATUS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Logic 1 (5m): {l1}\n"
            f"Logic 2 (15m): {l2}\n"
            f"Logic 3 (1h): {l3}"
        )
        await self.edit_message_with_header(update, text, [[InlineKeyboardButton("⬅️ Back", callback_data="menu_v3")]])

    async def handle_v3_toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle all V3"""
        # Placeholder
        await self.edit_message_with_header(update, "ℹ️ Use individual logic toggles.", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_v3")]])

    # --- V6 Toggles ---
    async def _toggle_v6(self, update, tf, enable):
        if self.trading_engine and hasattr(self.trading_engine, 'toggle_v6_timeframe'):
             self.trading_engine.toggle_v6_timeframe(tf, enable)
        status = "ENABLED" if enable else "DISABLED"
        emoji = "✅" if enable else "❌"
        await self.edit_message_with_header(
            update,
            f"{emoji} <b>V6 {tf.upper()} {status}</b>",
            [[InlineKeyboardButton("⬅️ Back", callback_data="menu_v6")]]
        )

    async def handle_v6_tf15m_on(self, u, c): await self._toggle_v6(u, '15m', True)
    async def handle_v6_tf15m_off(self, u, c): await self._toggle_v6(u, '15m', False)
    async def handle_v6_tf30m_on(self, u, c): await self._toggle_v6(u, '30m', True)
    async def handle_v6_tf30m_off(self, u, c): await self._toggle_v6(u, '30m', False)
    async def handle_v6_tf1h_on(self, u, c): await self._toggle_v6(u, '1h', True)
    async def handle_v6_tf1h_off(self, u, c): await self._toggle_v6(u, '1h', False)
    async def handle_v6_tf4h_on(self, u, c): await self._toggle_v6(u, '4h', True)
    async def handle_v6_tf4h_off(self, u, c): await self._toggle_v6(u, '4h', False)

    async def handle_v6_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = "🟢 <b>V6 PRICE ACTION STATUS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nCheck individual timeframes."
        await self.edit_message_with_header(update, text, [[InlineKeyboardButton("⬅️ Back", callback_data="menu_v6")]])

    # --- System Controls ---
    async def handle_system_pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.is_paused = True
        if self.trading_engine and hasattr(self.trading_engine, 'pause_trading'):
            self.trading_engine.pause_trading()
        await self.edit_message_with_header(update, "🔴 <b>SYSTEM PAUSED</b>", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_system")]])

    async def handle_system_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.is_paused = False
        if self.trading_engine and hasattr(self.trading_engine, 'resume_trading'):
            self.trading_engine.resume_trading()
        await self.edit_message_with_header(update, "🟢 <b>SYSTEM RESUMED</b>", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_system")]])

    async def handle_system_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.handle_status(update, context)

    # --- Analytics Placeholders ---
    # Moved to AnalyticsHandler logic where applicable

    # --- Plugin Placeholders ---
    async def handle_plugin_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.edit_message_with_header(update, "🔌 <b>PLUGIN STATUS</b>\n\nV3: Active\nV6: Active", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_plugin")]])

    # --- Session Placeholders ---
    async def handle_session_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.edit_message_with_header(update, "🕐 <b>SESSION STATUS</b>\n\nLondon: Open\nNew York: Open", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_session")]])

    # --- Voice Placeholders ---
    async def handle_voice_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.edit_message_with_header(update, "🔊 <b>VOICE STATUS</b>\n\nSystem: Ready", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_voice")]])

    async def handle_voice_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Trigger actual test if possible
        if self.trading_engine and hasattr(self.trading_engine, 'voice_system'):
             self.trading_engine.voice_system.speak("Voice test initiated.")
        await self.edit_message_with_header(update, "🔊 Test signal sent.", [[InlineKeyboardButton("⬅️ Back", callback_data="menu_voice")]])

    # =========================================================================
    # UTILS
    # =========================================================================

    async def edit_message_with_header(self, update: Update, text: str, reply_markup: InlineKeyboardMarkup):
        """
        Updates the message with a sticky header.
        Required by CallbackRouter/BaseMenuBuilder.
        """
        query = update.callback_query

        # Generate Header
        header = self.sticky_header.build_header(
            bot_status="🟢 Active" if not self.is_paused else "🔴 Paused",
            account_info=f"Risk: {self._get_risk_usage()}%"
        )

        full_text = f"{header}\n{text}"

        try:
            # Check if reply_markup is a list (from ButtonBuilder) or Markup object
            if isinstance(reply_markup, list):
                 reply_markup = InlineKeyboardMarkup(reply_markup)

            await query.edit_message_text(
                text=full_text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            # Register for refresh
            if self.header_refresh_manager:
                self.header_refresh_manager.register_message(update.effective_chat.id, query.message.message_id)
        except Exception as e:
            logger.error(f"[ControllerBot] Edit Error: {e}")
            if "message is not modified" not in str(e):
                await self.send_message(full_text, reply_markup=reply_markup)

    def _get_risk_usage(self) -> str:
        """Helper to get risk usage for header"""
        # Placeholder - fetch real risk from RiskManager
        return "2.5"

    # =========================================================================
    # SYNC/ASYNC COMPATIBILITY LAYERS
    # =========================================================================
    
    def send_message_sync(self, text: str, reply_markup: dict = None, parse_mode: str = "HTML"):
        """Synchronous wrapper for legacy calls"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.send_message(text, reply_markup, parse_mode))
        except:
            pass
        return True
    
    async def send_message(self, text: str, reply_markup: dict = None, parse_mode: str = "HTML", chat_id: str = None):
        """Async send message"""
        if not self.bot:
            return None
        target_chat = chat_id or self.chat_id
        if not target_chat:
            return None

        try:
            # Convert dict markup to InlineKeyboardMarkup if needed
            markup_obj = reply_markup
            if isinstance(reply_markup, dict) and "inline_keyboard" in reply_markup:
                markup_obj = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(**btn) for btn in row]
                        for row in reply_markup["inline_keyboard"]
                    ]
                )
            
            msg = await self.bot.send_message(
                chat_id=target_chat,
                text=text,
                reply_markup=markup_obj,
                parse_mode=parse_mode
            )

            # Register for refresh
            if msg and self.header_refresh_manager:
                self.header_refresh_manager.register_message(target_chat, msg.message_id)

            return msg
        except Exception as e:
            logger.error(f"[ControllerBot] Send Error: {e}")
            return None

    # =========================================================================
    # LEGACY COMMANDS (Simplified)
    # =========================================================================

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Use /start to open the main menu.")

    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uptime = datetime.now() - self.startup_time
        await update.message.reply_text(f"🟢 Active (Uptime: {str(uptime).split('.')[0]})")

    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Settings are now in the Main Menu > Settings.")

    async def handle_stop_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.is_paused = True
        await update.message.reply_text("🔴 Bot Paused.")

    async def handle_resume_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.is_paused = False
        await update.message.reply_text("🟢 Bot Resumed.")
        
    async def handle_pause_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.handle_stop_bot(update, context)

    async def handle_restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔄 Restarting...")

    async def handle_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("ZepixTradingBot V6 (V5 Foundation)")

    async def handle_version(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Version: 3.7.0")

    async def handle_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.handle_start(update, context)
        
    async def handle_v6_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.v6_menu_builder:
            menu_data = self.v6_menu_builder.build_v6_submenu()
            await update.message.reply_text(
                text=menu_data["text"],
                reply_markup=menu_data["reply_markup"],
                parse_mode=menu_data.get("parse_mode", "Markdown")
            )

    async def handle_v6_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("V6 Status: Active")

    async def _handle_v6_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Legacy V6 callback handling logic"""
        if not self.v6_menu_builder: return
        query = update.callback_query
        data = query.data

        if data == "v6_menu":
             menu_data = self.v6_menu_builder.build_v6_submenu()
             await query.edit_message_text(
                text=menu_data["text"],
                reply_markup=menu_data["reply_markup"],
                parse_mode="Markdown"
            )
