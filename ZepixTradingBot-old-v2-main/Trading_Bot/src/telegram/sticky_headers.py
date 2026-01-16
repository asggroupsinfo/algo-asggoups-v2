"""
Sticky Headers - Persistent pinned messages for Telegram bots

Implements sticky headers that:
- Pin messages at the top of chat
- Auto-update content every 30 seconds
- Auto-regenerate if message deleted by user
- Support hybrid approach (Reply keyboard + Pinned inline)

Version: 1.0.0
Date: 2026-01-14
"""

import threading
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

# Phase 9: Import clock system for IST time display
try:
    from src.modules.fixed_clock_system import get_clock_system
    CLOCK_AVAILABLE = True
except ImportError:
    CLOCK_AVAILABLE = False

logger = logging.getLogger(__name__)


class StickyHeaderState(Enum):
    """State of a sticky header"""
    INACTIVE = "inactive"
    CREATING = "creating"
    ACTIVE = "active"
    UPDATING = "updating"
    REGENERATING = "regenerating"
    ERROR = "error"


class StickyHeader:
    """
    Manages a single sticky header (pinned message) for a Telegram chat.
    
    Features:
    - Creates and pins a message at the top of chat
    - Auto-updates content at configurable interval
    - Auto-regenerates if message is deleted by user
    - Tracks update statistics
    """
    
    def __init__(
        self,
        chat_id: str,
        header_type: str = "dashboard",
        update_interval: int = 30,
        send_callback: Optional[Callable] = None,
        edit_callback: Optional[Callable] = None,
        pin_callback: Optional[Callable] = None,
        unpin_callback: Optional[Callable] = None,
        content_generator: Optional[Callable] = None
    ):
        """
        Initialize StickyHeader.
        
        Args:
            chat_id: Telegram chat ID
            header_type: Type of header (dashboard, status, etc.)
            update_interval: Seconds between updates (default 30)
            send_callback: Function to send messages
            edit_callback: Function to edit messages
            pin_callback: Function to pin messages
            unpin_callback: Function to unpin messages
            content_generator: Function that returns header content
        """
        self.chat_id = chat_id
        self.header_type = header_type
        self.update_interval = update_interval
        
        # Callbacks
        self.send_callback = send_callback
        self.edit_callback = edit_callback
        self.pin_callback = pin_callback
        self.unpin_callback = unpin_callback
        self.content_generator = content_generator
        
        # State
        self.message_id: Optional[int] = None
        self.state = StickyHeaderState.INACTIVE
        self._running = False
        self._update_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        
        # Statistics
        self.stats = {
            "created_at": None,
            "last_update": None,
            "update_count": 0,
            "regenerate_count": 0,
            "error_count": 0
        }
        
        # Inline keyboard for the header
        self.inline_keyboard: Optional[Dict] = None
    
    def set_inline_keyboard(self, keyboard: Dict):
        """
        Set inline keyboard to attach to the header.
        
        Args:
            keyboard: Telegram InlineKeyboardMarkup dict
        """
        self.inline_keyboard = keyboard
    
    def set_content_generator(self, generator: Callable):
        """
        Set the content generator function.
        
        Args:
            generator: Function that returns header content string
        """
        self.content_generator = generator
    
    def start(self):
        """Start the sticky header (create, pin, and begin updates)"""
        if self._running:
            logger.warning(f"Sticky header {self.header_type} already running")
            return
        
        self._running = True
        self._stop_event.clear()
        
        # Create initial header
        success = self._create_and_pin()
        
        if success:
            # Start update thread
            self._update_thread = threading.Thread(
                target=self._update_loop,
                name=f"StickyHeader-{self.header_type}",
                daemon=True
            )
            self._update_thread.start()
            logger.info(f"Sticky header {self.header_type} started")
        else:
            self._running = False
            logger.error(f"Failed to start sticky header {self.header_type}")
    
    def stop(self, timeout: float = 5.0):
        """Stop the sticky header updates"""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=timeout)
        
        self.state = StickyHeaderState.INACTIVE
        logger.info(f"Sticky header {self.header_type} stopped")
    
    def _create_and_pin(self) -> bool:
        """Create the header message and pin it"""
        if not self.send_callback:
            logger.error("No send callback configured")
            return False
        
        self.state = StickyHeaderState.CREATING
        
        try:
            # Generate content
            content = self._get_content()
            
            # Build message kwargs
            kwargs = {
                "chat_id": self.chat_id,
                "text": content,
                "parse_mode": "HTML"
            }
            
            if self.inline_keyboard:
                kwargs["reply_markup"] = self.inline_keyboard
            
            # Send message
            result = self.send_callback(**kwargs)
            
            if result:
                self.message_id = result
                self.stats["created_at"] = datetime.now().isoformat()
                
                # Pin the message
                if self.pin_callback:
                    try:
                        self.pin_callback(
                            chat_id=self.chat_id,
                            message_id=self.message_id,
                            disable_notification=True
                        )
                        logger.info(f"Header {self.header_type} pinned: {self.message_id}")
                    except Exception as e:
                        logger.warning(f"Failed to pin header: {e}")
                
                self.state = StickyHeaderState.ACTIVE
                return True
            else:
                self.state = StickyHeaderState.ERROR
                self.stats["error_count"] += 1
                return False
                
        except Exception as e:
            logger.error(f"Failed to create header: {e}")
            self.state = StickyHeaderState.ERROR
            self.stats["error_count"] += 1
            return False
    
    def _update_header(self) -> bool:
        """Update the existing header message"""
        if not self.message_id or not self.edit_callback:
            return False
        
        self.state = StickyHeaderState.UPDATING
        
        try:
            content = self._get_content()
            
            kwargs = {
                "chat_id": self.chat_id,
                "message_id": self.message_id,
                "text": content,
                "parse_mode": "HTML"
            }
            
            if self.inline_keyboard:
                kwargs["reply_markup"] = self.inline_keyboard
            
            self.edit_callback(**kwargs)
            
            self.stats["last_update"] = datetime.now().isoformat()
            self.stats["update_count"] += 1
            self.state = StickyHeaderState.ACTIVE
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if message was deleted
            if "message to edit not found" in error_msg or "message not found" in error_msg:
                logger.warning(f"Header message deleted, regenerating...")
                return self._regenerate()
            
            logger.error(f"Failed to update header: {e}")
            self.stats["error_count"] += 1
            return False
    
    def _regenerate(self) -> bool:
        """Regenerate the header if it was deleted"""
        self.state = StickyHeaderState.REGENERATING
        self.stats["regenerate_count"] += 1
        
        logger.info(f"Regenerating sticky header {self.header_type}")
        
        # Clear old message ID
        self.message_id = None
        
        # Create new header
        return self._create_and_pin()
    
    def _get_content(self) -> str:
        """Get header content from generator or default"""
        if self.content_generator:
            try:
                return self.content_generator()
            except Exception as e:
                logger.error(f"Content generator error: {e}")
        
        # Default content
        now = datetime.now()
        return (
            f"<b>ZEPIX TRADING BOT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Time: {now.strftime('%H:%M:%S')}\n"
            f"Date: {now.strftime('%d-%m-%Y')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    
    def _update_loop(self):
        """Main update loop (runs in thread)"""
        while self._running and not self._stop_event.is_set():
            try:
                self._update_header()
            except Exception as e:
                logger.error(f"Header update loop error: {e}")
            
            # Wait for next update
            self._stop_event.wait(self.update_interval)
    
    def force_update(self):
        """Force an immediate header update"""
        with self._lock:
            self._update_header()
    
    def get_status(self) -> Dict:
        """Get header status"""
        return {
            "header_type": self.header_type,
            "chat_id": self.chat_id,
            "message_id": self.message_id,
            "state": self.state.value,
            "running": self._running,
            "update_interval": self.update_interval,
            "stats": self.stats.copy()
        }


class StickyHeaderManager:
    """
    Manages multiple sticky headers across different chats and bots.
    
    Features:
    - Manages headers for all 3 bots (Controller, Notification, Analytics)
    - Ensures only ONE pinned message per chat
    - Provides unified interface for header management
    - Tracks statistics across all headers
    """
    
    # Default inline keyboard for dashboard header
    DEFAULT_DASHBOARD_KEYBOARD = {
        "inline_keyboard": [
            [
                {"text": "Dashboard", "callback_data": "dash_home"},
                {"text": "Live Stats", "callback_data": "dash_stats"}
            ],
            [
                {"text": "V3 Status", "callback_data": "plugin_v3"},
                {"text": "V6 Status", "callback_data": "plugin_v6"}
            ],
            [
                {"text": "Settings", "callback_data": "settings"},
                {"text": "Reports", "callback_data": "reports"}
            ],
            [
                {"text": "Refresh", "callback_data": "refresh"},
                {"text": "Emergency Stop", "callback_data": "emergency_stop"}
            ]
        ]
    }
    
    def __init__(self):
        """Initialize StickyHeaderManager"""
        self.headers: Dict[str, StickyHeader] = {}
        self._lock = threading.Lock()
        
        # Global statistics
        self.global_stats = {
            "total_headers": 0,
            "active_headers": 0,
            "total_updates": 0,
            "total_regenerations": 0
        }
    
    def create_header(
        self,
        header_id: str,
        chat_id: str,
        header_type: str = "dashboard",
        update_interval: int = 30,
        send_callback: Optional[Callable] = None,
        edit_callback: Optional[Callable] = None,
        pin_callback: Optional[Callable] = None,
        unpin_callback: Optional[Callable] = None,
        content_generator: Optional[Callable] = None,
        inline_keyboard: Optional[Dict] = None
    ) -> StickyHeader:
        """
        Create a new sticky header.
        
        Args:
            header_id: Unique identifier for the header
            chat_id: Telegram chat ID
            header_type: Type of header
            update_interval: Seconds between updates
            send_callback: Function to send messages
            edit_callback: Function to edit messages
            pin_callback: Function to pin messages
            unpin_callback: Function to unpin messages
            content_generator: Function that returns header content
            inline_keyboard: Optional inline keyboard
            
        Returns:
            StickyHeader instance
        """
        with self._lock:
            # Check if header already exists
            if header_id in self.headers:
                logger.warning(f"Header {header_id} already exists, returning existing")
                return self.headers[header_id]
            
            # Create new header
            header = StickyHeader(
                chat_id=chat_id,
                header_type=header_type,
                update_interval=update_interval,
                send_callback=send_callback,
                edit_callback=edit_callback,
                pin_callback=pin_callback,
                unpin_callback=unpin_callback,
                content_generator=content_generator
            )
            
            # Set inline keyboard
            if inline_keyboard:
                header.set_inline_keyboard(inline_keyboard)
            elif header_type == "dashboard":
                header.set_inline_keyboard(self.DEFAULT_DASHBOARD_KEYBOARD)
            
            self.headers[header_id] = header
            self.global_stats["total_headers"] += 1
            
            logger.info(f"Created sticky header: {header_id}")
            return header
    
    def get_header(self, header_id: str) -> Optional[StickyHeader]:
        """Get a header by ID"""
        return self.headers.get(header_id)
    
    def start_header(self, header_id: str) -> bool:
        """Start a specific header"""
        header = self.headers.get(header_id)
        if header:
            header.start()
            self.global_stats["active_headers"] += 1
            return True
        return False
    
    def stop_header(self, header_id: str) -> bool:
        """Stop a specific header"""
        header = self.headers.get(header_id)
        if header:
            header.stop()
            self.global_stats["active_headers"] = max(0, self.global_stats["active_headers"] - 1)
            return True
        return False
    
    def start_all(self):
        """Start all headers"""
        for header_id, header in self.headers.items():
            if not header._running:
                header.start()
                self.global_stats["active_headers"] += 1
        logger.info(f"Started {len(self.headers)} sticky headers")
    
    def stop_all(self):
        """Stop all headers"""
        for header in self.headers.values():
            header.stop()
        self.global_stats["active_headers"] = 0
        logger.info(f"Stopped {len(self.headers)} sticky headers")
    
    def remove_header(self, header_id: str) -> bool:
        """Remove a header"""
        with self._lock:
            if header_id in self.headers:
                header = self.headers[header_id]
                header.stop()
                del self.headers[header_id]
                self.global_stats["total_headers"] -= 1
                logger.info(f"Removed sticky header: {header_id}")
                return True
            return False
    
    def force_update_all(self):
        """Force update all headers"""
        for header in self.headers.values():
            if header._running:
                header.force_update()
    
    def get_stats(self) -> Dict:
        """Get manager statistics"""
        # Update totals from individual headers
        total_updates = 0
        total_regenerations = 0
        
        for header in self.headers.values():
            total_updates += header.stats["update_count"]
            total_regenerations += header.stats["regenerate_count"]
        
        self.global_stats["total_updates"] = total_updates
        self.global_stats["total_regenerations"] = total_regenerations
        
        return {
            "global": self.global_stats.copy(),
            "headers": {
                header_id: header.get_status()
                for header_id, header in self.headers.items()
            }
        }


class HybridStickySystem:
    """
    Implements hybrid sticky header approach:
    - Reply keyboard (always visible at bottom)
    - Pinned inline menu (at top of chat)
    
    Best of both worlds for mobile and desktop users.
    """
    
    # Default reply keyboard layout
    DEFAULT_REPLY_KEYBOARD = {
        "keyboard": [
            ["Menu", "Status"],
            ["Settings", "Analytics"]
        ],
        "resize_keyboard": True,
        "is_persistent": True,
        "one_time_keyboard": False
    }
    
    def __init__(
        self,
        chat_id: str,
        send_callback: Optional[Callable] = None,
        edit_callback: Optional[Callable] = None,
        pin_callback: Optional[Callable] = None
    ):
        """
        Initialize HybridStickySystem.
        
        Args:
            chat_id: Telegram chat ID
            send_callback: Function to send messages
            edit_callback: Function to edit messages
            pin_callback: Function to pin messages
        """
        self.chat_id = chat_id
        self.send_callback = send_callback
        self.edit_callback = edit_callback
        self.pin_callback = pin_callback
        
        # Header manager for pinned message
        self.header_manager = StickyHeaderManager()
        
        # State
        self.reply_keyboard_active = False
        self.pinned_header_active = False
        
        # Custom keyboards
        self.reply_keyboard = self.DEFAULT_REPLY_KEYBOARD.copy()
        self.inline_keyboard = StickyHeaderManager.DEFAULT_DASHBOARD_KEYBOARD.copy()
    
    def set_reply_keyboard(self, keyboard: Dict):
        """Set custom reply keyboard"""
        self.reply_keyboard = keyboard
    
    def set_inline_keyboard(self, keyboard: Dict):
        """Set custom inline keyboard for pinned header"""
        self.inline_keyboard = keyboard
    
    def setup(
        self,
        content_generator: Optional[Callable] = None,
        update_interval: int = 30
    ) -> bool:
        """
        Setup the hybrid sticky system.
        
        Args:
            content_generator: Function that returns header content
            update_interval: Seconds between header updates
            
        Returns:
            True if setup successful
        """
        success = True
        
        # Step 1: Setup reply keyboard
        if self.send_callback:
            try:
                self.send_callback(
                    chat_id=self.chat_id,
                    text="<b>Zepix Trading Bot - Control Panel Active</b>\n\n"
                         "Quick access buttons appear below\n"
                         "Advanced menu is pinned at top",
                    parse_mode="HTML",
                    reply_markup=self.reply_keyboard
                )
                self.reply_keyboard_active = True
                logger.info("Reply keyboard activated")
            except Exception as e:
                logger.error(f"Failed to setup reply keyboard: {e}")
                success = False
        
        # Step 2: Setup pinned header
        header = self.header_manager.create_header(
            header_id=f"hybrid_{self.chat_id}",
            chat_id=self.chat_id,
            header_type="dashboard",
            update_interval=update_interval,
            send_callback=self.send_callback,
            edit_callback=self.edit_callback,
            pin_callback=self.pin_callback,
            content_generator=content_generator,
            inline_keyboard=self.inline_keyboard
        )
        
        header.start()
        self.pinned_header_active = header._running
        
        return success and self.pinned_header_active
    
    def stop(self):
        """Stop the hybrid system"""
        self.header_manager.stop_all()
        self.pinned_header_active = False
        logger.info("Hybrid sticky system stopped")
    
    def get_status(self) -> Dict:
        """Get system status"""
        return {
            "chat_id": self.chat_id,
            "reply_keyboard_active": self.reply_keyboard_active,
            "pinned_header_active": self.pinned_header_active,
            "header_stats": self.header_manager.get_stats()
        }


# Content generators for different bot types

def create_controller_content_generator(data_providers: Dict[str, Callable]) -> Callable:
    """
    Create content generator for Controller Bot header.
    
    Phase 9: Integrated with FixedClockSystem for IST time display
    
    Args:
        data_providers: Dict of data provider functions
        
    Returns:
        Content generator function
    """
    def generator() -> str:
        # Phase 9: Use FixedClockSystem for IST time if available
        if CLOCK_AVAILABLE:
            clock = get_clock_system()
            time_str = clock.format_time_string()
            date_str = clock.format_date_string()
        else:
            now = datetime.now()
            time_str = now.strftime('%H:%M:%S')
            date_str = now.strftime('%d %b %Y (%a)')
        
        # Get data from providers
        open_trades = data_providers.get("open_trades", lambda: 0)()
        daily_pnl = data_providers.get("daily_pnl", lambda: 0.0)()
        bot_status = data_providers.get("bot_status", lambda: "UNKNOWN")()
        active_plugins = data_providers.get("active_plugins", lambda: 0)()
        
        # Phase 9: Get session info if available
        current_session = data_providers.get("current_session", lambda: "Unknown")()
        
        pnl_emoji = "+" if daily_pnl >= 0 else ""
        status_emoji = "" if bot_status == "RUNNING" else "" if bot_status == "PAUSED" else ""
        
        return (
            f"<b>ZEPIX CONTROLLER BOT</b>\n"
            f"{'=' * 24}\n"
            f"Time: <b>{time_str}</b>\n"
            f"Date: {date_str}\n"
            f"Session: <b>{current_session}</b>\n"
            f"{'=' * 24}\n"
            f"{status_emoji} Status: <b>{bot_status}</b>\n"
            f"Open Trades: <b>{open_trades}</b>\n"
            f"Daily P&L: <b>{pnl_emoji}${daily_pnl:.2f}</b>\n"
            f"Active Plugins: <b>{active_plugins}</b>\n"
            f"{'=' * 24}"
        )
    
    return generator


def create_notification_content_generator(data_providers: Dict[str, Callable]) -> Callable:
    """
    Create content generator for Notification Bot header.
    
    Args:
        data_providers: Dict of data provider functions
        
    Returns:
        Content generator function
    """
    def generator() -> str:
        now = datetime.now()
        
        alerts_today = data_providers.get("alerts_today", lambda: 0)()
        entries_today = data_providers.get("entries_today", lambda: 0)()
        exits_today = data_providers.get("exits_today", lambda: 0)()
        last_alert = data_providers.get("last_alert", lambda: "None")()
        
        return (
            f"<b>ZEPIX NOTIFICATION BOT</b>\n"
            f"{'=' * 24}\n"
            f"Time: <b>{now.strftime('%H:%M:%S')}</b> | Date: {now.strftime('%d-%m-%Y')}\n"
            f"{'=' * 24}\n"
            f"Alerts Today: <b>{alerts_today}</b>\n"
            f"Entries: <b>{entries_today}</b>\n"
            f"Exits: <b>{exits_today}</b>\n"
            f"Last Alert: {last_alert}\n"
            f"{'=' * 24}"
        )
    
    return generator


def create_analytics_content_generator(data_providers: Dict[str, Callable]) -> Callable:
    """
    Create content generator for Analytics Bot header.
    
    Args:
        data_providers: Dict of data provider functions
        
    Returns:
        Content generator function
    """
    def generator() -> str:
        now = datetime.now()
        
        win_rate = data_providers.get("win_rate", lambda: 0.0)()
        daily_pnl = data_providers.get("daily_pnl", lambda: 0.0)()
        total_trades = data_providers.get("total_trades", lambda: 0)()
        reports_sent = data_providers.get("reports_sent", lambda: 0)()
        
        pnl_emoji = "+" if daily_pnl >= 0 else ""
        
        return (
            f"<b>ZEPIX ANALYTICS BOT</b>\n"
            f"{'=' * 24}\n"
            f"Time: <b>{now.strftime('%H:%M:%S')}</b> | Date: {now.strftime('%d-%m-%Y')}\n"
            f"{'=' * 24}\n"
            f"Win Rate: <b>{win_rate:.1f}%</b>\n"
            f"Daily P&L: <b>{pnl_emoji}${daily_pnl:.2f}</b>\n"
            f"Total Trades: <b>{total_trades}</b>\n"
            f"Reports Sent: <b>{reports_sent}</b>\n"
            f"{'=' * 24}"
        )
    
    return generator
