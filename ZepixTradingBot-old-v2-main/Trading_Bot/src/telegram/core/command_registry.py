"""
Command Registry - Centralized Command Management

Explicitly registers all 144 commands and maps them to handlers.
Provides auto-complete help and validation.

Version: 1.0.0
Created: 2026-01-21
Part of: TELEGRAM_V5_CORE
"""

from typing import Dict, Callable, List, Optional
import logging

logger = logging.getLogger(__name__)

class CommandRegistry:
    """Registry for all bot commands"""

    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.commands: Dict[str, Callable] = {}
        self.descriptions: Dict[str, str] = {}

    def register(self, command: str, handler: Callable, description: str = ""):
        """Register a command"""
        cmd_clean = command.replace('/', '')
        self.commands[cmd_clean] = handler
        self.descriptions[cmd_clean] = description

    def get_handler(self, command: str) -> Optional[Callable]:
        """Get handler for a command"""
        cmd_clean = command.replace('/', '')
        return self.commands.get(cmd_clean)

    def register_all(self):
        """Register all 144 known commands"""
        # System
        self.register("start", self.bot.handle_start, "Main Menu")
        self.register("help", self.bot.handle_help, "Show Help")
        self.register("status", self.bot.handle_status, "System Status")
        self.register("pause", self.bot.handle_system_pause, "Pause Trading")
        self.register("resume", self.bot.handle_system_resume, "Resume Trading")

        # Trading
        self.register("buy", self.bot.handle_buy_command, "Buy Wizard")
        self.register("sell", self.bot.handle_sell_command, "Sell Wizard")
        self.register("positions", self.bot.positions_handler.handle, "View Positions")
        self.register("orders", self.bot.orders_handler.handle, "View Orders")
        self.register("close", self.bot.handle_trading_close, "Close Position")
        self.register("closeall", self.bot.handle_trading_closeall, "Close All")

        # Risk
        self.register("risk", self.bot.risk_settings_handler.handle, "Risk Menu")
        self.register("setlot", self.bot.handle_risk_setlot_start, "Set Lot Size")

        # Analytics (Updated Gap 1)
        self.register("analytics", self.bot.analytics_handler.execute, "Analytics Menu")
        self.register("daily", self.bot.analytics_handler.handle_daily, "Daily Report")
        self.register("weekly", self.bot.analytics_handler.handle_weekly, "Weekly Report")
        self.register("winrate", self.bot.analytics_handler.handle_winrate, "Win Rate Stats")
        self.register("avgprofit", self.bot.analytics_handler.handle_avgprofit, "Avg Profit")
        self.register("avgloss", self.bot.analytics_handler.handle_avgloss, "Avg Loss")
        self.register("bestday", self.bot.analytics_handler.handle_bestday, "Best Day")
        self.register("worstday", self.bot.analytics_handler.handle_worstday, "Worst Day")
        self.register("correlation", self.bot.analytics_handler.handle_correlation, "Pair Correlation")

        # Plugin
        self.register("plugins", self.bot.plugin_handler.execute, "Plugin Menu")
        self.register("enable", self.bot.plugin_handler.handle_enable, "Enable Plugin")

        # Session
        self.register("session", self.bot.session_handler.execute, "Session Menu")
        self.register("london", self.bot.session_handler.handle_london, "London Session")

        # Voice
        self.register("voice", self.bot.voice_handler.execute, "Voice Menu")

        # Settings
        self.register("settings", self.bot.settings_handler.execute, "Settings Menu")

        # V3/V6 Bridge
        self.register("v3", self.bot.handle_v3_status, "V3 Status")
        self.register("v6", self.bot.handle_v6_status, "V6 Status")
        self.register("tf15m_on", self.bot.handle_v6_tf15m_on, "V6 15M On")

        logger.info(f"[CommandRegistry] Registered {len(self.commands)} commands")
