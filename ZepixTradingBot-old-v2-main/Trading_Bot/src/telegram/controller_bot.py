"""
Controller Bot - Handles system commands and admin functions

This bot handles all slash commands and system control.
NOW WIRED to CommandRegistry for 95+ command handling (not delegation).

Version: 2.0.0
Date: 2026-01-15

Updates:
- v2.0.0: Wired to CommandRegistry with actual handler implementations
- v1.1.0: Added /health and /version commands for plugin monitoring
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import sys
import os

# Ensure src is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from .base_telegram_bot import BaseTelegramBot
try:
    from src.menu.menu_manager import MenuManager
except ImportError:
    MenuManager = None

logger = logging.getLogger(__name__)


class ControllerBot(BaseTelegramBot):
    """
    Controller Bot for system commands and admin functions.
    
    NOW WIRED to CommandRegistry for 95+ command handling.
    """
    
    def __init__(self, token: str, chat_id: str = None):
        super().__init__(token, chat_id, bot_name="ControllerBot")
        
        self._command_handlers: Dict[str, Callable] = {}
        self._callback_handlers: Dict[str, Callable] = {} # Add callback handlers dict
        self._trading_engine = None
        self._risk_manager = None
        self._legacy_bot = None
        
        # Menu Manager Integration
        self._menu_manager = None
        if MenuManager:
            try:
                self._menu_manager = MenuManager(self)
                logger.info("[ControllerBot] MenuManager initialized")
            except Exception as e:
                logger.error(f"[ControllerBot] Failed to init MenuManager: {e}")
        
        # Health monitoring and versioning (Batch 11)
        self._health_monitor = None
        self._version_registry = None
        
        # Command Registry integration (v2.0.0)
        self._command_registry = None
        self._plugin_control_menu = None
        
        # Bot state
        self._is_paused = False
        self._startup_time = datetime.now()
        
        # Wire default handlers
        self._wire_default_handlers()
        
        logger.info("[ControllerBot] Initialized with CommandRegistry integration")
    
    def set_dependencies(
        self,
        trading_engine=None,
        risk_manager=None,
        legacy_bot=None,
        health_monitor=None,
        version_registry=None
    ):
        """
        Set dependencies for command handling
        
        Args:
            trading_engine: TradingEngine instance
            risk_manager: RiskManager instance
            legacy_bot: Legacy TelegramBot instance for command delegation
            health_monitor: PluginHealthMonitor instance (Batch 11)
            version_registry: VersionedPluginRegistry instance (Batch 11)
        """
        self._trading_engine = trading_engine
        self._risk_manager = risk_manager
        self._legacy_bot = legacy_bot
        self._health_monitor = health_monitor
        self._version_registry = version_registry
        
        if legacy_bot:
            logger.info("[ControllerBot] Legacy bot connected for command delegation")
        
        if health_monitor:
            logger.info("[ControllerBot] Health monitor connected")
        
        if version_registry:
            logger.info("[ControllerBot] Version registry connected")
    
    def register_command(self, command: str, handler: Callable):
        """
        Register a command handler
        
        Args:
            command: Command string (e.g., '/status')
            handler: Handler function
        """
        self._command_handlers[command] = handler
        logger.debug(f"[ControllerBot] Registered command: {command}")
    
    def handle_command(self, command: str, message: Dict) -> bool:
        """
        Handle an incoming command
        
        Args:
            command: Command string
            message: Full message dict from Telegram
        
        Returns:
            True if command was handled
        """
        if self._legacy_bot and hasattr(self._legacy_bot, 'command_handlers'):
            if command in self._legacy_bot.command_handlers:
                try:
                    self._legacy_bot.command_handlers[command](message)
                    return True
                except Exception as e:
                    logger.error(f"[ControllerBot] Legacy handler error for {command}: {e}")
                    return False
        
        if command in self._command_handlers:
            try:
                self._command_handlers[command](message)
                return True
            except Exception as e:
                logger.error(f"[ControllerBot] Handler error for {command}: {e}")
                return False
        
        logger.warning(f"[ControllerBot] Unknown command: {command}")
        return False
    
    def send_status_response(self, status_data: Dict) -> Optional[int]:
        """
        Send formatted status response
        
        Args:
            status_data: Dict with status information
        
        Returns:
            Message ID if successful
        """
        message = self._format_status_message(status_data)
        return self.send_message(message)
    
    def _format_status_message(self, status_data: Dict) -> str:
        """Format status data into readable message"""
        bot_status = "🟢 Active" if status_data.get("is_active", False) else "🔴 Paused"
        
        return (
            f"🤖 <b>BOT STATUS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Status: {bot_status}\n"
            f"Uptime: {status_data.get('uptime', 'N/A')}\n"
            f"Active Plugins: {status_data.get('active_plugins', 0)}\n"
            f"Open Trades: {status_data.get('open_trades', 0)}\n"
            f"Today's P&L: ${status_data.get('daily_pnl', 0):.2f}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Last Update: {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def send_command_response(self, response_text: str, keyboard: Dict = None) -> Optional[int]:
        """
        Send a command response with optional keyboard
        
        Args:
            response_text: Response message
            keyboard: Optional inline keyboard
        
        Returns:
            Message ID if successful
        """
        reply_markup = None
        if keyboard:
            reply_markup = {"inline_keyboard": keyboard}
        
        return self.send_message(response_text, reply_markup=reply_markup)
    
    def send_error_response(self, error_message: str) -> Optional[int]:
        """
        Send an error response
        
        Args:
            error_message: Error description
        
        Returns:
            Message ID if successful
        """
        formatted = f"❌ <b>Error</b>\n\n{error_message}"
        return self.send_message(formatted)
    
    def send_confirmation_request(
        self,
        action: str,
        confirm_callback: str,
        cancel_callback: str = "menu_main"
    ) -> Optional[int]:
        """
        Send a confirmation request with Yes/No buttons
        
        Args:
            action: Action description
            confirm_callback: Callback data for confirmation
            cancel_callback: Callback data for cancellation
        
        Returns:
            Message ID if successful
        """
        keyboard = [
            [
                {"text": "✅ YES", "callback_data": confirm_callback},
                {"text": "❌ CANCEL", "callback_data": cancel_callback}
            ]
        ]
        
        message = (
            f"⚠️ <b>Confirmation Required</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{action}\n\n"
            f"<b>Are you sure?</b>"
        )
        
        return self.send_message(message, reply_markup={"inline_keyboard": keyboard})
    
    # ========================================
    # Health Monitoring Commands (Batch 11)
    # ========================================
    
    def handle_health_command(self, message: Dict = None) -> Optional[int]:
        """
        Handle /health command - Show plugin health dashboard
        
        Args:
            message: Telegram message dict (optional)
        
        Returns:
            Message ID if successful
        """
        if not self._health_monitor:
            return self.send_message(
                "🏥 <b>Health Monitor</b>\n\n"
                "Health monitoring is not configured.\n"
                "Please initialize PluginHealthMonitor first."
            )
        
        try:
            # Get formatted health dashboard
            dashboard_text = self._health_monitor.format_health_dashboard()
            return self.send_message(dashboard_text)
            
        except Exception as e:
            logger.error(f"[ControllerBot] Health command error: {e}")
            return self.send_error_response(f"Failed to get health status: {str(e)}")
    
    def handle_version_command(self, message: Dict = None) -> Optional[int]:
        """
        Handle /version command - Show active plugin versions
        
        Args:
            message: Telegram message dict (optional)
        
        Returns:
            Message ID if successful
        """
        if not self._version_registry:
            return self.send_message(
                "📦 <b>Version Registry</b>\n\n"
                "Version registry is not configured.\n"
                "Please initialize VersionedPluginRegistry first."
            )
        
        try:
            # Get formatted version dashboard
            version_text = self._version_registry.format_version_dashboard()
            return self.send_message(version_text)
            
        except Exception as e:
            logger.error(f"[ControllerBot] Version command error: {e}")
            return self.send_error_response(f"Failed to get version info: {str(e)}")
    
    def handle_upgrade_command(self, message: Dict, args: List[str] = None) -> Optional[int]:
        """
        Handle /upgrade command - Upgrade plugin to specific version
        
        Usage: /upgrade <plugin_id> <version>
        Example: /upgrade combined_v3 3.2.0
        
        Args:
            message: Telegram message dict
            args: Command arguments [plugin_id, version]
        
        Returns:
            Message ID if successful
        """
        if not self._version_registry:
            return self.send_error_response("Version registry not configured")
        
        if not args or len(args) != 2:
            return self.send_message(
                "📦 <b>Upgrade Plugin</b>\n\n"
                "Usage: <code>/upgrade &lt;plugin_id&gt; &lt;version&gt;</code>\n"
                "Example: <code>/upgrade combined_v3 3.2.0</code>"
            )
        
        plugin_id = args[0]
        target_version = args[1]
        
        try:
            success, result_message = self._version_registry.upgrade_plugin(plugin_id, target_version)
            
            if success:
                return self.send_message(f"✅ {result_message}")
            else:
                return self.send_error_response(result_message)
                
        except Exception as e:
            logger.error(f"[ControllerBot] Upgrade command error: {e}")
            return self.send_error_response(f"Upgrade failed: {str(e)}")
    
    def handle_rollback_command(self, message: Dict, args: List[str] = None) -> Optional[int]:
        """
        Handle /rollback command - Rollback plugin to previous version
        
        Usage: /rollback <plugin_id>
        Example: /rollback combined_v3
        
        Args:
            message: Telegram message dict
            args: Command arguments [plugin_id]
        
        Returns:
            Message ID if successful
        """
        if not self._version_registry:
            return self.send_error_response("Version registry not configured")
        
        if not args or len(args) != 1:
            return self.send_message(
                "📦 <b>Rollback Plugin</b>\n\n"
                "Usage: <code>/rollback &lt;plugin_id&gt;</code>\n"
                "Example: <code>/rollback combined_v3</code>"
            )
        
        plugin_id = args[0]
        
        try:
            success, result_message = self._version_registry.rollback_plugin(plugin_id)
            
            if success:
                return self.send_message(f"✅ {result_message}")
            else:
                return self.send_error_response(result_message)
                
        except Exception as e:
            logger.error(f"[ControllerBot] Rollback command error: {e}")
            return self.send_error_response(f"Rollback failed: {str(e)}")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get health summary data (for programmatic access)
        
        Returns:
            Dict with health summary or empty dict if not configured
        """
        if not self._health_monitor:
            return {}
        
        try:
            return self._health_monitor.get_health_summary()
        except Exception as e:
            logger.error(f"[ControllerBot] Get health summary error: {e}")
            return {}
    
    def get_version_summary(self) -> Dict[str, Any]:
        """
        Get version summary data (for programmatic access)
        
        Returns:
            Dict with version summary or empty dict if not configured
        """
        if not self._version_registry:
            return {}
        
        try:
            return self._version_registry.get_version_summary()
        except Exception as e:
            logger.error(f"[ControllerBot] Get version summary error: {e}")
            return {}
    
    # ========================================
    # CommandRegistry Integration (v2.0.0)
    # ========================================
    
    def _wire_default_handlers(self):
        """Wire default command handlers to CommandRegistry"""
        # System commands
        self._command_handlers["/start"] = self.handle_start
        self._command_handlers["/status"] = self.handle_status
        self._command_handlers["/pause"] = self.handle_pause
        self._command_handlers["/resume"] = self.handle_resume
        self._command_handlers["/help"] = self.handle_help
        self._command_handlers["/health"] = self.handle_health_command
        self._command_handlers["/version"] = self.handle_version_command
        self._command_handlers["/config"] = self.handle_config
        
        # Plugin commands
        self._command_handlers["/plugin"] = self.handle_plugin_menu
        self._command_handlers["/plugins"] = self.handle_plugins
        self._command_handlers["/enable"] = self.handle_enable
        self._command_handlers["/disable"] = self.handle_disable
        
        # Trading commands
        self._command_handlers["/positions"] = self.handle_positions
        self._command_handlers["/pnl"] = self.handle_pnl
        self._command_handlers["/balance"] = self.handle_balance
        
        logger.info(f"[ControllerBot] Wired {len(self._command_handlers)} default handlers")
    
    def wire_command_registry(self, registry):
        """
        Wire CommandRegistry to this bot.
        
        Args:
            registry: CommandRegistry instance
        """
        self._command_registry = registry
        registry.set_dependencies(controller_bot=self, trading_engine=self._trading_engine)
        
        # Register all handlers with registry
        for cmd, handler in self._command_handlers.items():
            registry.register_command_handler(cmd, handler)
        
        logger.info("[ControllerBot] CommandRegistry wired")
    
    def wire_plugin_control_menu(self, menu):
        """
        Wire PluginControlMenu to this bot.
        
        Args:
            menu: PluginControlMenu instance
        """
        self._plugin_control_menu = menu
        menu.set_dependencies(trading_engine=self._trading_engine, telegram_bot=self)
        
        # Register plugin callbacks
        for callback_data, handler in menu.get_callbacks().items():
            if self._command_registry:
                self._command_registry.register_callback_handler(callback_data, handler)
        
        logger.info("[ControllerBot] PluginControlMenu wired")
    
    # ========================================
    # Actual Command Handler Implementations
    # ========================================
    
    def handle_start(self, message: Dict = None) -> Optional[int]:
        """Handle /start command - Show main menu via MenuManager"""
        chat_id = self.chat_id
        if message and 'chat' in message:
            chat_id = message['chat'].get('id', self.chat_id)
            
        if self._menu_manager:
            return self._menu_manager.show_main_menu(chat_id)
            
        # Fallback if MenuManager not available
        keyboard = [
            [{"text": "📊 Dashboard", "callback_data": "action_dashboard"}],
            [{"text": "🔌 Plugin Control", "callback_data": "plugin_menu"}],
            [{"text": "📈 Status", "callback_data": "action_status"}],
            [{"text": "⚙️ Settings", "callback_data": "menu_settings"}],
            [{"text": "❓ Help", "callback_data": "action_help"}]
        ]
        
        uptime = datetime.now() - self._startup_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        text = (
            "🤖 <b>ZEPIX TRADING BOT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Status:</b> {'🟢 Active' if not self._is_paused else '🔴 Paused'}\n"
            f"<b>Uptime:</b> {hours}h {minutes}m {seconds}s\n"
            f"<b>Version:</b> V5 Hybrid Architecture\n"
            f"<b>Menu:</b> Fallback Mode (Manager missing)\n\n"
            "<i>Select an option below:</i>"
        )
        
        return self.send_message(text, reply_markup={"inline_keyboard": keyboard})
    
    def handle_status(self, message: Dict = None) -> Optional[int]:
        """Handle /status command - Show bot status"""
        uptime = datetime.now() - self._startup_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Get plugin status
        v3_enabled = True
        v6_enabled = True
        if self._trading_engine:
            if hasattr(self._trading_engine, 'is_plugin_enabled'):
                v3_enabled = self._trading_engine.is_plugin_enabled("v3_combined")
                v6_enabled = self._trading_engine.is_plugin_enabled("v6_price_action")
        
        status_data = {
            "is_active": not self._is_paused,
            "uptime": f"{hours}h {minutes}m {seconds}s",
            "active_plugins": int(v3_enabled) + int(v6_enabled),
            "open_trades": 0,
            "daily_pnl": 0.0
        }
        
        # Try to get real data from trading engine
        if self._trading_engine:
            if hasattr(self._trading_engine, 'get_open_positions'):
                try:
                    positions = self._trading_engine.get_open_positions()
                    status_data["open_trades"] = len(positions) if positions else 0
                except Exception:
                    pass
            if hasattr(self._trading_engine, 'get_daily_pnl'):
                try:
                    status_data["daily_pnl"] = self._trading_engine.get_daily_pnl()
                except Exception:
                    pass
        
        return self.send_status_response(status_data)
    
    def handle_pause(self, message: Dict = None) -> Optional[int]:
        """Handle /pause command - Pause trading"""
        if self._is_paused:
            return self.send_message("⚠️ Trading is already paused.")
        
        return self.send_confirmation_request(
            "Are you sure you want to <b>PAUSE</b> all trading?",
            "confirm_pause",
            "menu_main"
        )
    
    def handle_resume(self, message: Dict = None) -> Optional[int]:
        """Handle /resume command - Resume trading"""
        if not self._is_paused:
            return self.send_message("✅ Trading is already active.")
        
        self._is_paused = False
        if self._trading_engine and hasattr(self._trading_engine, 'resume_trading'):
            self._trading_engine.resume_trading()
        
        return self.send_message(
            "✅ <b>TRADING RESUMED</b>\n\n"
            "Bot is now actively processing signals."
        )
    
    def handle_help(self, message: Dict = None) -> Optional[int]:
        """Handle /help command - Show help menu"""
        if self._command_registry:
            help_text = self._command_registry.generate_help_text()
            keyboard = self._command_registry.generate_category_menu()
            return self.send_message(help_text, reply_markup={"inline_keyboard": keyboard})
        
        # Fallback help
        text = (
            "📚 <b>HELP MENU</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>System Commands:</b>\n"
            "/start - Show main menu\n"
            "/status - Show bot status\n"
            "/pause - Pause trading\n"
            "/resume - Resume trading\n"
            "/health - Plugin health\n"
            "/version - Plugin versions\n\n"
            "<b>Plugin Commands:</b>\n"
            "/plugin - Plugin control menu\n"
            "/plugins - List all plugins\n"
            "/enable - Enable plugin\n"
            "/disable - Disable plugin\n"
        )
        return self.send_message(text)
    
    def handle_config(self, message: Dict = None) -> Optional[int]:
        """Handle /config command - Show configuration"""
        text = (
            "⚙️ <b>CONFIGURATION</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>Architecture:</b> V5 Hybrid\n"
            "<b>Plugins:</b> V3 Combined, V6 Price Action\n"
            "<b>Mode:</b> Production\n"
            "<b>Shadow Mode:</b> Enabled for V6\n\n"
            "<i>Use /plugin to manage plugins</i>"
        )
        return self.send_message(text)
    
    def handle_plugin_menu(self, message: Dict = None) -> Optional[int]:
        """Handle /plugin command - Show plugin control menu"""
        if self._plugin_control_menu:
            chat_id = self.chat_id
            if message and 'chat' in message:
                chat_id = message['chat'].get('id', self.chat_id)
            return self._plugin_control_menu.show_plugin_menu(chat_id)
        
        # Fallback
        return self.send_message(
            "🔌 <b>PLUGIN CONTROL</b>\n\n"
            "Plugin control menu not configured.\n"
            "Please initialize PluginControlMenu first."
        )
    
    def handle_plugins(self, message: Dict = None) -> Optional[int]:
        """Handle /plugins command - List all plugins"""
        v3_enabled = True
        v6_enabled = True
        
        if self._trading_engine:
            if hasattr(self._trading_engine, 'is_plugin_enabled'):
                v3_enabled = self._trading_engine.is_plugin_enabled("v3_combined")
                v6_enabled = self._trading_engine.is_plugin_enabled("v6_price_action")
        
        v3_emoji = "🟢" if v3_enabled else "🔴"
        v6_emoji = "🟢" if v6_enabled else "🔴"
        
        text = (
            "📦 <b>INSTALLED PLUGINS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"1. {v3_emoji} <b>V3 Combined Logic</b>\n"
            f"   └─ Status: {'ENABLED' if v3_enabled else 'DISABLED'}\n\n"
            f"2. {v6_emoji} <b>V6 Price Action</b>\n"
            f"   └─ Status: {'ENABLED' if v6_enabled else 'DISABLED'}\n\n"
            f"<i>Total: 2 plugins ({int(v3_enabled) + int(v6_enabled)} active)</i>"
        )
        return self.send_message(text)
    
    def handle_enable(self, message: Dict = None) -> Optional[int]:
        """Handle /enable command - Enable plugin"""
        keyboard = [
            [{"text": "🟢 Enable V3", "callback_data": "plugin_v3_enable"}],
            [{"text": "🟢 Enable V6", "callback_data": "plugin_v6_enable"}],
            [{"text": "🔙 Back", "callback_data": "plugin_menu"}]
        ]
        return self.send_message(
            "🟢 <b>ENABLE PLUGIN</b>\n\n"
            "Select a plugin to enable:",
            reply_markup={"inline_keyboard": keyboard}
        )
    
    def handle_disable(self, message: Dict = None) -> Optional[int]:
        """Handle /disable command - Disable plugin"""
        keyboard = [
            [{"text": "🔴 Disable V3", "callback_data": "plugin_v3_disable"}],
            [{"text": "🔴 Disable V6", "callback_data": "plugin_v6_disable"}],
            [{"text": "🔙 Back", "callback_data": "plugin_menu"}]
        ]
        return self.send_message(
            "🔴 <b>DISABLE PLUGIN</b>\n\n"
            "Select a plugin to disable:",
            reply_markup={"inline_keyboard": keyboard}
        )
    
    def handle_positions(self, message: Dict = None) -> Optional[int]:
        """Handle /positions command - Show open positions"""
        positions = []
        if self._trading_engine and hasattr(self._trading_engine, 'get_open_positions'):
            try:
                positions = self._trading_engine.get_open_positions() or []
            except Exception:
                pass
        
        if not positions:
            return self.send_message(
                "📊 <b>OPEN POSITIONS</b>\n\n"
                "No open positions."
            )
        
        text = "📊 <b>OPEN POSITIONS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, pos in enumerate(positions[:10], 1):
            symbol = pos.get('symbol', 'N/A')
            side = pos.get('side', 'N/A')
            pnl = pos.get('pnl', 0)
            text += f"{i}. {symbol} {side} | P&L: ${pnl:.2f}\n"
        
        return self.send_message(text)
    
    def handle_pnl(self, message: Dict = None) -> Optional[int]:
        """Handle /pnl command - Show P&L summary"""
        daily_pnl = 0.0
        if self._trading_engine and hasattr(self._trading_engine, 'get_daily_pnl'):
            try:
                daily_pnl = self._trading_engine.get_daily_pnl()
            except Exception:
                pass
        
        emoji = "🟢" if daily_pnl >= 0 else "🔴"
        
        return self.send_message(
            f"💰 <b>P&L SUMMARY</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Today:</b> {emoji} ${daily_pnl:.2f}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def handle_balance(self, message: Dict = None) -> Optional[int]:
        """Handle /balance command - Show account balance"""
        balance = 0.0
        equity = 0.0
        
        if self._trading_engine:
            if hasattr(self._trading_engine, 'get_account_balance'):
                try:
                    balance = self._trading_engine.get_account_balance()
                except Exception:
                    pass
            if hasattr(self._trading_engine, 'get_account_equity'):
                try:
                    equity = self._trading_engine.get_account_equity()
                except Exception:
                    pass
        
        return self.send_message(
            f"💵 <b>ACCOUNT BALANCE</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Balance:</b> ${balance:.2f}\n"
            f"<b>Equity:</b> ${equity:.2f}\n"
            f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    
    # ========================================
    # Callback Handlers
    # ========================================
    
    def confirm_pause_trading(self, chat_id: int = None):
        """Confirm pause trading action"""
        self._is_paused = True
        if self._trading_engine and hasattr(self._trading_engine, 'pause_trading'):
            self._trading_engine.pause_trading()
        
        self.send_message(
            "🔴 <b>TRADING PAUSED</b>\n\n"
            "Bot will not process any new signals.\n"
            "Use /resume to continue trading."
        )
    
    def show_main_menu(self, chat_id: int = None):
        """Show main menu (callback handler)"""
        self.handle_start()
    
    def show_plugin_menu(self, chat_id: int = None):
        """Show plugin menu (callback handler)"""
        if self._plugin_control_menu:
            self._plugin_control_menu.show_plugin_menu(chat_id or self.chat_id)
        else:
            self.handle_plugin_menu()
    
    def toggle_pause_resume(self, chat_id: int = None):
        """Toggle pause/resume (callback handler)"""
        if self._is_paused:
            self.handle_resume()
        else:
            self.handle_pause()
    
    def show_dashboard(self, chat_id: int = None):
        """Show dashboard (callback handler)"""
        self.handle_status()
    
    def no_operation(self, chat_id: int = None):
        """No operation (callback handler)"""
        pass

    # ========================================
    # Menu Manager Delegators (Additions)
    # ========================================

    def _show_menu_generic(self, category: str, chat_id: int = None):
        """Generic helper to show a category menu"""
        if not self._menu_manager:
            self.send_message("❌ Menu Manager not initialized.")
            return
        
        # Message ID is needed for edit_message. 
        # In a real callback flow, we usually have access to the message_id from the update.
        # But here 'chat_id' is passed. The architecture of ControllerBot.handle_callback needs inspection.
        # Assuming for now we can't edit without tracking current message ID, so we might send new.
        # However, MenuManager supports message_id=None to send new.
        # Ideally, we should capture message_id from the callback update.
        
        # For this fix, we'll try to use the last known message ID if available or send new.
        self._menu_manager.show_category_menu(chat_id or self.chat_id, category, message_id=None)

    def show_main_menu(self, chat_id: int = None):
        if self._menu_manager:
            self._menu_manager.show_main_menu(chat_id or self.chat_id, message_id=None)
        else:
            self.handle_start()

    def show_trading_menu(self, chat_id: int = None):
        self._show_menu_generic("trading", chat_id)

    def show_risk_menu(self, chat_id: int = None):
        self._show_menu_generic("risk", chat_id)

    def show_strategy_menu(self, chat_id: int = None):
        self._show_menu_generic("strategy", chat_id)

    def show_timeframe_menu(self, chat_id: int = None):
        # Timeframe menu has specific handler in MenuManager usually, but let's try generic
        if self._menu_manager:
             self._menu_manager.show_timeframe_menu(chat_id or self.chat_id, message_id=None)

    def show_reentry_menu(self, chat_id: int = None):
        """Show Re-entry System menu via MenuManager (Telegram V5 Upgrade)"""
        if self._menu_manager and hasattr(self._menu_manager, 'show_reentry_menu'):
            self._menu_manager.show_reentry_menu(chat_id or self.chat_id, message_id=None)
        else:
            self._show_menu_generic("reentry", chat_id)

    def show_profit_menu(self, chat_id: int = None):
        self._show_menu_generic("profit", chat_id)

    def show_analytics_menu(self, chat_id: int = None):
        """Show Analytics menu via MenuManager (Telegram V5 Upgrade)"""
        if self._menu_manager and hasattr(self._menu_manager, 'show_analytics_menu'):
            self._menu_manager.show_analytics_menu(chat_id or self.chat_id, message_id=None)
        else:
            self._show_menu_generic("performance", chat_id)

    def show_session_menu(self, chat_id: int = None):
        # Session menu might not be a simple category, let's assume generic for now or custom
        # MenuManager.show_main_menu has "session_dashboard".
        # Let's map it to placeholder generic or implement specifics later.
        self.send_message("Sessions menu under construction.")

    def show_voice_menu(self, chat_id: int = None):
        self._show_menu_generic("voice", chat_id)

    def show_sl_system_menu(self, chat_id: int = None):
        self._show_menu_generic("sl_system", chat_id)

    def show_fine_tune_menu(self, chat_id: int = None):
        self._show_menu_generic("fine_tune", chat_id)

    def show_diagnostics_menu(self, chat_id: int = None):
        self._show_menu_generic("diagnostics", chat_id)

    def show_trends_menu(self, chat_id: int = None):
        self._show_menu_generic("trends", chat_id)
        
    def show_orders_menu(self, chat_id: int = None):
        self._show_menu_generic("orders", chat_id)
    
    def show_settings_menu(self, chat_id: int = None):
        self._show_menu_generic("settings", chat_id)

    def navigate_back(self, chat_id: int = None):
        """Navigate back handler"""
        self.show_main_menu(chat_id)
    
    # ========================================
    # V5 Upgrade Menu Methods (Telegram V5 Upgrade)
    # ========================================
    
    def show_v6_control_menu(self, chat_id: int = None):
        """Show V6 Price Action control menu via MenuManager (Telegram V5 Upgrade)"""
        if self._menu_manager and hasattr(self._menu_manager, 'show_v6_menu'):
            self._menu_manager.show_v6_menu(chat_id or self.chat_id, message_id=None)
        else:
            self.send_message("V6 Price Action menu under construction.")
    
    def show_dual_order_menu(self, chat_id: int = None):
        """Show Dual Order System menu via MenuManager (Telegram V5 Upgrade)"""
        if self._menu_manager and hasattr(self._menu_manager, 'show_dual_order_menu'):
            self._menu_manager.show_dual_order_menu(chat_id or self.chat_id, message_id=None)
        else:
            self.send_message("Dual Order System menu under construction.")
    
    def handle_v6_callback(self, callback_data: str, chat_id: int = None, message_id: int = None) -> bool:
        """Handle V6 menu callback via MenuManager (Telegram V5 Upgrade)"""
        if self._menu_manager and hasattr(self._menu_manager, 'handle_v6_callback'):
            return self._menu_manager.handle_v6_callback(callback_data, chat_id or self.chat_id, message_id)
        return False
    
    def handle_analytics_callback(self, callback_data: str, chat_id: int = None, message_id: int = None) -> bool:
        """Handle Analytics menu callback via MenuManager (Telegram V5 Upgrade)"""
        if self._menu_manager and hasattr(self._menu_manager, 'handle_analytics_callback'):
            return self._menu_manager.handle_analytics_callback(callback_data, chat_id or self.chat_id, message_id)
        return False
    
    def handle_dual_order_callback(self, callback_data: str, chat_id: int = None, message_id: int = None) -> bool:
        """Handle Dual Order menu callback via MenuManager (Telegram V5 Upgrade)"""
        if self._menu_manager and hasattr(self._menu_manager, 'handle_dual_order_callback'):
            return self._menu_manager.handle_dual_order_callback(callback_data, chat_id or self.chat_id, message_id)
        return False
    
    def handle_reentry_callback(self, callback_data: str, chat_id: int = None, message_id: int = None) -> bool:
        """Handle Re-entry menu callback via MenuManager (Telegram V5 Upgrade)"""
        if self._menu_manager and hasattr(self._menu_manager, 'handle_reentry_callback'):
            return self._menu_manager.handle_reentry_callback(callback_data, chat_id or self.chat_id, message_id)
        return False

