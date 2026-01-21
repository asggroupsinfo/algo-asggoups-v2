"""
Multi-Bot Manager - Orchestrator for V6 Telegram Architecture
Version: 3.0.0
Date: 2026-01-20

Manages lifecycle (Init, Start, Stop) of all 3 bots.
"""

import logging
import asyncio
from typing import Dict, Any

# Import new components
from ..bots.controller_bot import ControllerBot
from ..bots.notification_bot import NotificationBot
from ..bots.analytics_bot import AnalyticsBot
from .token_manager import TokenManager
from .message_router import MessageRouter

logger = logging.getLogger(__name__)

class MultiBotManager:
    """
    Main entry point for Telegram System.
    Initializes 3 independent bots based on TokenManager configuration.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config_dict = config  # Store raw dict
        # Create a Config-like object for menu handlers
        from src.config import Config
        self.config = Config()  # This will load from config.json
        
        self.token_manager = TokenManager(config)
        self.chat_id = config.get("telegram", {}).get("chat_id")
        
        self.controller_bot = None
        self.notification_bot = None
        self.analytics_bot = None
        self.router = None
        
        self._initialize_bots()
        
    def _initialize_bots(self):
        """Create bot instances based on tokens"""
        
        if self.token_manager.mode == "MULTI_BOT":
            # Initialize independent bots (Controller is mandatory)
            self.controller_bot = ControllerBot(
                token=self.token_manager.get_token("CONTROLLER"), 
                chat_id=self.chat_id,
                config=self.config_dict
            )
            
            # Notification Bot (Optional)
            n_token = self.token_manager.get_token("NOTIFICATION")
            if n_token:
                self.notification_bot = NotificationBot(
                    token=n_token,
                    chat_id=self.chat_id,
                    config=self.config_dict
                )
            
            # Analytics Bot (Optional)
            a_token = self.token_manager.get_token("ANALYTICS")
            if a_token:
                self.analytics_bot = AnalyticsBot(
                    token=a_token,
                    chat_id=self.chat_id,
                    config=self.config_dict
                )
            
        else: # SINGLE_BOT mode
            main_token = self.token_manager.get_token("MAIN")
            if not main_token:
                logger.error("[MultiBotManager] No tokens found! Bot will be offline.")
                return

            # Same bot instance serves all roles (internally routed)
            shared_bot = ControllerBot(main_token, self.chat_id, config=self.config_dict)
            
            self.controller_bot = shared_bot
            self.notification_bot = shared_bot 
            self.analytics_bot = shared_bot
                
        # 4. Router
        self.router = MessageRouter(
            self.controller_bot,
            self.notification_bot,
            self.analytics_bot
        )
        
    async def start(self):
        """Start all active bots"""
        logger.info("[MultiBotManager] Starting bots...")
        
        if self.controller_bot:
            await self.controller_bot.initialize()
            
        if self.notification_bot:
            await self.notification_bot.initialize()
            
        if self.analytics_bot:
            await self.analytics_bot.initialize()
            
    async def stop(self):
        """Stop all active bots"""
        logger.info("[MultiBotManager] Stopping bots...")
        
        if self.controller_bot:
            await self.controller_bot.stop()
            
        if self.notification_bot:
            await self.notification_bot.stop()
            
        if self.analytics_bot:
            await self.analytics_bot.stop()

    def set_dependencies(self, trading_engine):
        """Inject dependencies into bots"""
        if self.controller_bot:
            self.controller_bot.set_dependencies(trading_engine)
    
    def set_trend_manager(self, trend_manager):
        """Set trend manager for compatibility"""
        # Store reference for potential future use
        self.trend_manager = trend_manager
    
    async def send_message(self, message: str, reply_markup: dict = None, parse_mode: str = "HTML"):
        """Async send_message wrapper for proper async support"""
        if self.controller_bot:
            return await self.controller_bot.send_message(message, reply_markup=reply_markup, parse_mode=parse_mode)
        return False

    def send_message_sync(self, message: str, reply_markup: dict = None, parse_mode: str = "HTML"):
        """Synchronous send_message wrapper for Legacy/MenuManager compatibility"""
        if self.controller_bot:
            # Use controller bot's send_message_sync method
            if hasattr(self.controller_bot, 'send_message_sync'):
                return self.controller_bot.send_message_sync(message, reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                # Fallback: run async version as task (fire and forget)
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.controller_bot.send_message(message, reply_markup=reply_markup))
        return True
    
    def send_message_with_keyboard(self, message: str, reply_markup: dict):
        """Send message with keyboard for MenuManager compatibility"""
        return self.send_message_sync(message, reply_markup=reply_markup)
    
    def edit_message(self, text: str, message_id: int, reply_markup: dict = None):
        """Edit message for MenuManager compatibility"""
        if self.controller_bot:
            if hasattr(self.controller_bot, 'edit_message_sync'):
                return self.controller_bot.edit_message_sync(text, message_id, reply_markup)

            # Fallback
            loop = asyncio.get_event_loop()
            if loop.is_running():
                if hasattr(self.controller_bot, 'edit_message'):
                    asyncio.create_task(self.controller_bot.edit_message(text, message_id, reply_markup))
        return True
            
    async def send_alert(self, message: str):
        """Public API: Send Alert"""
        await self.router.route_alert(message)
