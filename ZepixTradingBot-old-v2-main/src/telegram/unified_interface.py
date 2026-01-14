"""
Unified Interface Manager - Consistent UI across all 3 bots
Implements Zero-Typing navigation and Live Sticky Headers

Features:
- Zero-Typing UI: All interactions via buttons (no manual typing)
- Live Sticky Header: Pinned message with real-time status
- Menu Synchronization: Same menus work in all 3 bots
- PANIC CLOSE: Emergency button with confirmation

Version: 1.0.0
"""

import threading
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

logger = logging.getLogger(__name__)


class BotType(Enum):
    """Types of bots in the 3-bot system"""
    CONTROLLER = "controller"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"


class LiveHeaderManager:
    """
    Manages live sticky header for a Telegram bot.
    Updates pinned message every 60 seconds with current status.
    """
    
    def __init__(
        self,
        bot_type: BotType,
        chat_id: str,
        send_callback: Optional[Callable] = None,
        edit_callback: Optional[Callable] = None,
        pin_callback: Optional[Callable] = None,
        update_interval: int = 60
    ):
        """
        Initialize LiveHeaderManager.
        
        Args:
            bot_type: Type of bot (CONTROLLER, NOTIFICATION, ANALYTICS)
            chat_id: Telegram chat ID
            send_callback: Function to send messages
            edit_callback: Function to edit messages
            pin_callback: Function to pin messages
            update_interval: Seconds between updates (default 60)
        """
        self.bot_type = bot_type
        self.chat_id = chat_id
        self.send_callback = send_callback
        self.edit_callback = edit_callback
        self.pin_callback = pin_callback
        self.update_interval = update_interval
        
        self.header_message_id: Optional[int] = None
        self._running = False
        self._update_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        
        # Data providers (set externally)
        self.data_providers: Dict[str, Callable] = {}
        
        # Cached data
        self._cached_data: Dict[str, Any] = {}
        self._last_update: Optional[datetime] = None
    
    def set_data_provider(self, key: str, provider: Callable):
        """
        Set a data provider function for header content.
        
        Args:
            key: Data key (e.g., 'open_trades', 'daily_pnl')
            provider: Function that returns the data
        """
        self.data_providers[key] = provider
    
    def start(self):
        """Start the live header update loop"""
        if self._running:
            logger.warning(f"{self.bot_type.value} header manager already running")
            return
        
        self._running = True
        self._stop_event.clear()
        
        # Create initial header
        self._create_header()
        
        # Start update thread
        self._update_thread = threading.Thread(
            target=self._update_loop,
            name=f"LiveHeader-{self.bot_type.value}",
            daemon=True
        )
        self._update_thread.start()
        logger.info(f"{self.bot_type.value} live header started")
    
    def stop(self, timeout: float = 5.0):
        """Stop the live header update loop"""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=timeout)
        
        logger.info(f"{self.bot_type.value} live header stopped")
    
    def _create_header(self):
        """Create and pin the initial header message"""
        if not self.send_callback:
            logger.warning("No send callback configured for header")
            return
        
        try:
            content = self._generate_header_content()
            result = self.send_callback(
                chat_id=self.chat_id,
                text=content,
                parse_mode="HTML"
            )
            
            if result:
                self.header_message_id = result
                
                # Pin the message
                if self.pin_callback:
                    self.pin_callback(
                        chat_id=self.chat_id,
                        message_id=self.header_message_id
                    )
                
                logger.info(f"{self.bot_type.value} header created: {self.header_message_id}")
        except Exception as e:
            logger.error(f"Failed to create header: {e}")
    
    def _update_header(self):
        """Update the existing header message"""
        if not self.header_message_id or not self.edit_callback:
            return
        
        try:
            content = self._generate_header_content()
            self.edit_callback(
                chat_id=self.chat_id,
                message_id=self.header_message_id,
                text=content,
                parse_mode="HTML"
            )
            self._last_update = datetime.now()
        except Exception as e:
            logger.error(f"Failed to update header: {e}")
    
    def _generate_header_content(self) -> str:
        """Generate header content based on bot type"""
        now = datetime.now()
        
        # Refresh cached data
        self._refresh_data()
        
        # Common header elements
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d-%m-%Y")
        
        # Calculate session duration (if available)
        session_duration = self._cached_data.get("session_duration", "N/A")
        
        # Bot-specific content
        if self.bot_type == BotType.CONTROLLER:
            return self._generate_controller_header(time_str, date_str, session_duration)
        elif self.bot_type == BotType.NOTIFICATION:
            return self._generate_notification_header(time_str, date_str, session_duration)
        elif self.bot_type == BotType.ANALYTICS:
            return self._generate_analytics_header(time_str, date_str, session_duration)
        else:
            return self._generate_default_header(time_str, date_str, session_duration)
    
    def _generate_controller_header(self, time_str: str, date_str: str, session_duration: str) -> str:
        """Generate header for Controller Bot"""
        open_trades = self._cached_data.get("open_trades", 0)
        daily_pnl = self._cached_data.get("daily_pnl", 0.0)
        bot_status = self._cached_data.get("bot_status", "UNKNOWN")
        active_plugins = self._cached_data.get("active_plugins", 0)
        
        pnl_emoji = "+" if daily_pnl >= 0 else ""
        status_emoji = "🟢" if bot_status == "RUNNING" else "🔴" if bot_status == "PAUSED" else "🟡"
        
        return (
            f"<b>ZEPIX CONTROLLER BOT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 <b>{time_str}</b> | 📅 {date_str}\n"
            f"⏱️ Session: {session_duration}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{status_emoji} Status: <b>{bot_status}</b>\n"
            f"📊 Open Trades: <b>{open_trades}</b>\n"
            f"💰 Daily P&L: <b>{pnl_emoji}${daily_pnl:.2f}</b>\n"
            f"🔌 Active Plugins: <b>{active_plugins}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    
    def _generate_notification_header(self, time_str: str, date_str: str, session_duration: str) -> str:
        """Generate header for Notification Bot"""
        alerts_today = self._cached_data.get("alerts_today", 0)
        entries_today = self._cached_data.get("entries_today", 0)
        exits_today = self._cached_data.get("exits_today", 0)
        last_alert = self._cached_data.get("last_alert", "None")
        
        return (
            f"<b>ZEPIX NOTIFICATION BOT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 <b>{time_str}</b> | 📅 {date_str}\n"
            f"⏱️ Session: {session_duration}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔔 Alerts Today: <b>{alerts_today}</b>\n"
            f"🟢 Entries: <b>{entries_today}</b>\n"
            f"🔴 Exits: <b>{exits_today}</b>\n"
            f"📨 Last Alert: {last_alert}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    
    def _generate_analytics_header(self, time_str: str, date_str: str, session_duration: str) -> str:
        """Generate header for Analytics Bot"""
        win_rate = self._cached_data.get("win_rate", 0.0)
        daily_pnl = self._cached_data.get("daily_pnl", 0.0)
        total_trades = self._cached_data.get("total_trades", 0)
        reports_sent = self._cached_data.get("reports_sent", 0)
        
        pnl_emoji = "+" if daily_pnl >= 0 else ""
        
        return (
            f"<b>ZEPIX ANALYTICS BOT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 <b>{time_str}</b> | 📅 {date_str}\n"
            f"⏱️ Session: {session_duration}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📈 Win Rate: <b>{win_rate:.1f}%</b>\n"
            f"💰 Daily P&L: <b>{pnl_emoji}${daily_pnl:.2f}</b>\n"
            f"📊 Total Trades: <b>{total_trades}</b>\n"
            f"📋 Reports Sent: <b>{reports_sent}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    
    def _generate_default_header(self, time_str: str, date_str: str, session_duration: str) -> str:
        """Generate default header"""
        return (
            f"<b>ZEPIX TRADING BOT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 <b>{time_str}</b> | 📅 {date_str}\n"
            f"⏱️ Session: {session_duration}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    
    def _refresh_data(self):
        """Refresh cached data from providers"""
        with self._lock:
            for key, provider in self.data_providers.items():
                try:
                    self._cached_data[key] = provider()
                except Exception as e:
                    logger.error(f"Data provider '{key}' error: {e}")
    
    def _update_loop(self):
        """Main update loop (runs in thread)"""
        while self._running and not self._stop_event.is_set():
            try:
                self._update_header()
            except Exception as e:
                logger.error(f"Header update error: {e}")
            
            # Wait for next update
            self._stop_event.wait(self.update_interval)
    
    def force_update(self):
        """Force an immediate header update"""
        self._update_header()
    
    def get_status(self) -> Dict:
        """Get header manager status"""
        return {
            "bot_type": self.bot_type.value,
            "running": self._running,
            "header_message_id": self.header_message_id,
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "update_interval": self.update_interval
        }


class UnifiedInterfaceManager:
    """
    Manages consistent interface across all 3 bots.
    Provides Zero-Typing navigation and synchronized menus.
    """
    
    # Reply Keyboard to Callback mapping (Zero-Typing UI)
    REPLY_MENU_MAP = {
        # Row 1: High Frequency
        "📊 Dashboard": "action_dashboard",
        "⏸️ Pause/Resume": "action_pause_resume",
        "🕒 Sessions": "session_dashboard",
        
        # Row 2: Management
        "📈 Active Trades": "action_trades",
        "🛡️ Risk": "menu_risk",
        "🎙️ Voice": "action_voice_test",
        
        # Row 3: Analysis
        "🔄 Re-entry": "menu_reentry",
        "⚙️ SL System": "menu_sl_system",
        "📍 Trends": "menu_trends",
        
        # Row 4: Info
        "📈 Profit": "menu_profit",
        "🆘 Help": "action_help",
        
        # Row 5: Safety (Full Width)
        "🚨 PANIC CLOSE": "action_panic_close",
        
        # Additional buttons
        "💰 Performance": "action_performance",
        "💱 Trading": "menu_trading",
        "⏱️ Timeframe": "menu_timeframe",
        "📦 Orders": "menu_orders",
        "⚙️ Settings": "menu_settings",
        "🔬 Diagnostics": "menu_diagnostics",
        "⚡ Fine-Tune": "menu_fine_tune",
        "🔄 Refresh": "menu_main",
        "⏰ Clock System": "action_clock_system",
        "🔊 Voice Test": "action_voice_test"
    }
    
    # Reverse mapping for validation
    CALLBACK_TO_BUTTON = {v: k for k, v in REPLY_MENU_MAP.items()}
    
    def __init__(self):
        """Initialize UnifiedInterfaceManager"""
        self.headers: Dict[BotType, LiveHeaderManager] = {}
        self.command_handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        
        # Statistics
        self.stats = {
            "button_presses": 0,
            "commands_executed": 0,
            "panic_activations": 0
        }
    
    def create_header_manager(
        self,
        bot_type: BotType,
        chat_id: str,
        send_callback: Optional[Callable] = None,
        edit_callback: Optional[Callable] = None,
        pin_callback: Optional[Callable] = None
    ) -> LiveHeaderManager:
        """
        Create a LiveHeaderManager for a bot.
        
        Args:
            bot_type: Type of bot
            chat_id: Telegram chat ID
            send_callback: Function to send messages
            edit_callback: Function to edit messages
            pin_callback: Function to pin messages
            
        Returns:
            LiveHeaderManager instance
        """
        header = LiveHeaderManager(
            bot_type=bot_type,
            chat_id=chat_id,
            send_callback=send_callback,
            edit_callback=edit_callback,
            pin_callback=pin_callback
        )
        self.headers[bot_type] = header
        return header
    
    def get_header_manager(self, bot_type: BotType) -> Optional[LiveHeaderManager]:
        """Get header manager for a bot type"""
        return self.headers.get(bot_type)
    
    def start_all_headers(self):
        """Start all header managers"""
        for header in self.headers.values():
            header.start()
        logger.info(f"Started {len(self.headers)} header managers")
    
    def stop_all_headers(self):
        """Stop all header managers"""
        for header in self.headers.values():
            header.stop()
        logger.info(f"Stopped {len(self.headers)} header managers")
    
    def register_command_handler(self, callback_data: str, handler: Callable):
        """
        Register a handler for a callback data.
        
        Args:
            callback_data: Callback data string
            handler: Function to handle the callback
        """
        self.command_handlers[callback_data] = handler
    
    def handle_button_press(self, button_text: str) -> Optional[str]:
        """
        Handle a reply keyboard button press.
        Maps button text to callback data.
        
        Args:
            button_text: Text of the pressed button
            
        Returns:
            Callback data string, or None if not found
        """
        self.stats["button_presses"] += 1
        
        callback_data = self.REPLY_MENU_MAP.get(button_text)
        
        if callback_data:
            # Track PANIC activations
            if callback_data == "action_panic_close":
                self.stats["panic_activations"] += 1
            
            return callback_data
        
        logger.warning(f"Unknown button pressed: {button_text}")
        return None
    
    def execute_callback(self, callback_data: str, context: Dict = None) -> bool:
        """
        Execute a callback handler.
        
        Args:
            callback_data: Callback data string
            context: Additional context for the handler
            
        Returns:
            True if handler executed, False if not found
        """
        handler = self.command_handlers.get(callback_data)
        
        if handler:
            try:
                handler(context or {})
                self.stats["commands_executed"] += 1
                return True
            except Exception as e:
                logger.error(f"Handler error for {callback_data}: {e}")
                return False
        
        return False
    
    def get_persistent_menu(self) -> Dict:
        """
        Get the persistent reply keyboard menu.
        Same menu for all 3 bots.
        
        Returns:
            Telegram ReplyKeyboardMarkup dict
        """
        return {
            "keyboard": [
                # Row 1: High Frequency
                ["📊 Dashboard", "⏸️ Pause/Resume", "🕒 Sessions"],
                # Row 2: Management
                ["📈 Active Trades", "🛡️ Risk", "🎙️ Voice"],
                # Row 3: Analysis
                ["🔄 Re-entry", "⚙️ SL System", "📍 Trends"],
                # Row 4: Info
                ["📈 Profit", "🆘 Help"],
                # Row 5: Safety (Full Width)
                ["🚨 PANIC CLOSE"]
            ],
            "resize_keyboard": True,
            "is_persistent": True,
            "one_time_keyboard": False
        }
    
    def get_main_inline_menu(self) -> Dict:
        """
        Get the main inline keyboard menu.
        
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        return {
            "inline_keyboard": [
                # Quick Actions Row 1
                [
                    {"text": "📊 Dashboard", "callback_data": "action_dashboard"},
                    {"text": "⏸️ Pause/Resume", "callback_data": "action_pause_resume"}
                ],
                # Quick Actions Row 2
                [
                    {"text": "🎙️ Voice Test", "callback_data": "action_voice_test"},
                    {"text": "⏰ Clock", "callback_data": "action_clock"}
                ],
                # Quick Actions Row 3
                [
                    {"text": "📈 Trades", "callback_data": "action_trades"},
                    {"text": "💰 Performance", "callback_data": "action_performance"}
                ],
                # Categories Row 1
                [
                    {"text": "🕒 Sessions", "callback_data": "session_dashboard"},
                    {"text": "💰 Trading", "callback_data": "menu_trading"}
                ],
                # Categories Row 2
                [
                    {"text": "⏱️ Timeframe", "callback_data": "menu_timeframe"},
                    {"text": "⚡ Performance", "callback_data": "menu_performance"}
                ],
                # Categories Row 3
                [
                    {"text": "🔄 Re-entry", "callback_data": "menu_reentry"},
                    {"text": "📍 Trends", "callback_data": "menu_trends"}
                ],
                # Categories Row 4
                [
                    {"text": "🛡️ Risk", "callback_data": "menu_risk"},
                    {"text": "⚙️ SL System", "callback_data": "menu_sl_system"}
                ],
                # Categories Row 5
                [
                    {"text": "💎 Orders", "callback_data": "menu_orders"},
                    {"text": "📈 Profit", "callback_data": "menu_profit"}
                ],
                # Categories Row 6
                [
                    {"text": "🔧 Settings", "callback_data": "menu_settings"},
                    {"text": "🔍 Diagnostics", "callback_data": "menu_diagnostics"}
                ],
                # Categories Row 7
                [
                    {"text": "⚡ Fine-Tune", "callback_data": "menu_fine_tune"}
                ],
                # Help and Refresh
                [
                    {"text": "🆘 Help", "callback_data": "action_help"},
                    {"text": "🔄 Refresh", "callback_data": "menu_main"}
                ]
            ]
        }
    
    def get_panic_confirmation_menu(self) -> Dict:
        """
        Get the PANIC CLOSE confirmation menu.
        
        Returns:
            Telegram InlineKeyboardMarkup dict
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "YES - CLOSE ALL", "callback_data": "confirm_panic_close"},
                    {"text": "CANCEL", "callback_data": "menu_main"}
                ]
            ]
        }
    
    def get_panic_warning_message(self) -> str:
        """Get the PANIC CLOSE warning message"""
        return (
            "<b>PANIC CLOSE CONFIRMATION</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "This will close ALL open trades <b>IMMEDIATELY</b>:\n\n"
            "- All positions will be closed at market price\n"
            "- No recovery attempts will be made\n"
            "- This action cannot be undone\n\n"
            "<b>Are you absolutely sure?</b>"
        )
    
    def get_stats(self) -> Dict:
        """Get interface statistics"""
        return {
            "stats": self.stats.copy(),
            "headers": {
                bt.value: h.get_status() 
                for bt, h in self.headers.items()
            },
            "registered_handlers": len(self.command_handlers)
        }
    
    def force_update_all_headers(self):
        """Force update all header managers"""
        for header in self.headers.values():
            header.force_update()
