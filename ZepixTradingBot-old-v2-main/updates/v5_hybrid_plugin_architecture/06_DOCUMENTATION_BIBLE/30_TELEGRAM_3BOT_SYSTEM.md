# TELEGRAM 3-BOT SYSTEM

**File:** `src/telegram/multi_telegram_manager.py`  
**Lines:** 477  
**Purpose:** Orchestrates 3-bot Telegram system for specialized functions

---

## OVERVIEW

The 3-Bot Telegram System splits bot functionality into three specialized bots:

1. **Controller Bot:** Commands and Admin operations
2. **Notification Bot:** Trade alerts and notifications
3. **Analytics Bot:** Reports and statistics

This architecture provides:
- Better rate limit management
- Specialized message routing
- Graceful degradation to single bot mode
- Backward compatibility with existing system

---

## BOT ROLES

### Controller Bot

| Responsibility | Examples |
|----------------|----------|
| Admin Commands | `/start`, `/help`, `/status` |
| Trading Commands | `/trade`, `/close`, `/modify` |
| Configuration | `/config`, `/set`, `/get` |
| System Control | `/pause`, `/resume`, `/restart` |

### Notification Bot

| Responsibility | Examples |
|----------------|----------|
| Trade Alerts | Entry, Exit, SL Hit, TP Hit |
| Price Alerts | Target reached, Breakout |
| System Alerts | Connection, Error, Warning |
| Recovery Alerts | SL Hunt, TP Continuation |

### Analytics Bot

| Responsibility | Examples |
|----------------|----------|
| Daily Reports | P&L, Win rate, Trade count |
| Weekly Reports | Performance summary |
| Statistics | Symbol stats, Strategy stats |
| Exports | Trade history, Reports |

---

## CLASS STRUCTURE

### Definition (Lines 32-79)

```python
class MultiTelegramManager:
    """
    Manages multiple Telegram bots for specialized functions:
    1. Controller Bot: Commands and Admin
    2. Notification Bot: Trade Alerts
    3. Analytics Bot: Reports
    
    Features:
    - Intelligent message routing based on content type
    - Graceful degradation to single bot mode
    - Backward compatibility with existing telegram_bot_fixed.py
    - Voice alert integration support
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Bot instances
        self.controller_bot = None
        self.notification_bot = None
        self.analytics_bot = None
        
        # Fallback single bot
        self.fallback_bot = None
        
        # Mode
        self.multi_bot_mode = False
        
        # Message queue for rate limiting
        self.message_queue = asyncio.Queue()
        
        # Initialize bots
        self._initialize_bots()
```

### Bot Initialization (Lines 81-150)

```python
def _initialize_bots(self):
    """Initialize all bots based on configuration"""
    
    # Check for multi-bot tokens
    controller_token = self.config.get("telegram_controller_token")
    notification_token = self.config.get("telegram_notification_token")
    analytics_token = self.config.get("telegram_analytics_token")
    
    # Check if multi-bot mode is possible
    if controller_token and notification_token:
        self.multi_bot_mode = True
        
        # Initialize Controller Bot
        self.controller_bot = ControllerBot(
            token=controller_token,
            chat_id=self.config.get("telegram_chat_id"),
            config=self.config
        )
        
        # Initialize Notification Bot
        self.notification_bot = NotificationBot(
            token=notification_token,
            chat_id=self.config.get("telegram_chat_id"),
            config=self.config
        )
        
        # Initialize Analytics Bot (optional)
        if analytics_token:
            self.analytics_bot = AnalyticsBot(
                token=analytics_token,
                chat_id=self.config.get("telegram_chat_id"),
                config=self.config
            )
        
        self.logger.info("Multi-bot mode initialized")
    else:
        # Fallback to single bot mode
        self.multi_bot_mode = False
        
        fallback_token = self.config.get("telegram_token")
        if fallback_token:
            self.fallback_bot = TelegramBot(
                token=fallback_token,
                chat_id=self.config.get("telegram_chat_id"),
                config=self.config
            )
            self.logger.info("Single bot mode initialized (fallback)")
        else:
            self.logger.warning("No Telegram tokens configured")
```

---

## MESSAGE ROUTING

### Send Notification (Lines 152-230)

```python
async def send_notification_async(self, notification_type: str, 
                                 message: str, **kwargs):
    """
    Send notification through appropriate bot.
    
    Routing logic:
    - Trade notifications -> Notification Bot
    - Reports/Stats -> Analytics Bot
    - Admin messages -> Controller Bot
    - Unknown -> Notification Bot (default)
    
    Args:
        notification_type: Type of notification
        message: Message content
        **kwargs: Additional arguments
    """
    # Determine target bot
    target_bot = self._get_target_bot(notification_type)
    
    if target_bot:
        try:
            await target_bot.send_message(message, **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            
            # Try fallback
            if self.fallback_bot and target_bot != self.fallback_bot:
                await self.fallback_bot.send_message(message, **kwargs)
    else:
        self.logger.warning(f"No bot available for notification: {notification_type}")

def _get_target_bot(self, notification_type: str):
    """
    Get the appropriate bot for a notification type.
    
    Args:
        notification_type: Type of notification
        
    Returns:
        Bot instance or None
    """
    if not self.multi_bot_mode:
        return self.fallback_bot
    
    # Trade notifications
    trade_types = [
        "trade_opened", "trade_closed", "sl_hit", "tp_hit",
        "entry_signal", "exit_signal", "recovery_started",
        "profit_booked", "chain_advanced"
    ]
    
    if notification_type in trade_types:
        return self.notification_bot
    
    # Analytics notifications
    analytics_types = [
        "daily_report", "weekly_report", "monthly_report",
        "statistics", "performance", "export"
    ]
    
    if notification_type in analytics_types:
        return self.analytics_bot or self.notification_bot
    
    # Admin notifications
    admin_types = [
        "system_status", "error", "warning", "config_change",
        "mode_change", "connection_status"
    ]
    
    if notification_type in admin_types:
        return self.controller_bot
    
    # Default to notification bot
    return self.notification_bot
```

### Send Trade Notification (Lines 232-300)

```python
async def send_trade_notification(self, trade_data: Dict[str, Any]):
    """
    Send formatted trade notification.
    
    Args:
        trade_data: Trade information dictionary
    """
    notification_type = trade_data.get("type", "trade_opened")
    
    # Format message based on type
    if notification_type == "trade_opened":
        message = self._format_trade_opened(trade_data)
    elif notification_type == "trade_closed":
        message = self._format_trade_closed(trade_data)
    elif notification_type == "sl_hit":
        message = self._format_sl_hit(trade_data)
    elif notification_type == "tp_hit":
        message = self._format_tp_hit(trade_data)
    else:
        message = str(trade_data)
    
    await self.send_notification_async(notification_type, message)

def _format_trade_opened(self, data: Dict) -> str:
    """Format trade opened notification"""
    symbol = data.get("symbol", "UNKNOWN")
    direction = data.get("direction", "").upper()
    price = data.get("price", 0)
    order_type = data.get("order_type", "")
    
    emoji = "🟢" if direction == "BUY" else "🔴"
    
    return f"""
{emoji} TRADE OPENED
Symbol: {symbol}
Direction: {direction}
Entry: {price:.5f}
Order Type: {order_type}
Time: {datetime.now().strftime('%H:%M:%S')}
"""

def _format_trade_closed(self, data: Dict) -> str:
    """Format trade closed notification"""
    symbol = data.get("symbol", "UNKNOWN")
    direction = data.get("direction", "").upper()
    profit = data.get("profit", 0)
    reason = data.get("reason", "")
    
    emoji = "💰" if profit > 0 else "💸"
    
    return f"""
{emoji} TRADE CLOSED
Symbol: {symbol}
Direction: {direction}
Profit: ${profit:.2f}
Reason: {reason}
Time: {datetime.now().strftime('%H:%M:%S')}
"""
```

---

## COMMAND HANDLING

### Register Command Handlers (Lines 302-380)

```python
def register_command_handlers(self, trading_engine):
    """
    Register command handlers with Controller Bot.
    
    Args:
        trading_engine: Reference to TradingEngine
    """
    if not self.controller_bot:
        return
    
    # Trading commands
    self.controller_bot.register_handler("trade", self._handle_trade_command)
    self.controller_bot.register_handler("close", self._handle_close_command)
    self.controller_bot.register_handler("modify", self._handle_modify_command)
    
    # Status commands
    self.controller_bot.register_handler("status", self._handle_status_command)
    self.controller_bot.register_handler("positions", self._handle_positions_command)
    self.controller_bot.register_handler("balance", self._handle_balance_command)
    
    # Config commands
    self.controller_bot.register_handler("config", self._handle_config_command)
    self.controller_bot.register_handler("set", self._handle_set_command)
    
    # System commands
    self.controller_bot.register_handler("pause", self._handle_pause_command)
    self.controller_bot.register_handler("resume", self._handle_resume_command)
    
    # Shadow mode commands
    self.controller_bot.register_handler("shadow_status", self._handle_shadow_status)
    self.controller_bot.register_handler("shadow_enable", self._handle_shadow_enable)
    self.controller_bot.register_handler("shadow_disable", self._handle_shadow_disable)
    
    # Store trading engine reference
    self.trading_engine = trading_engine
    
    self.logger.info("Command handlers registered")
```

---

## RATE LIMITING

### Rate Limiter Integration (Lines 382-420)

```python
async def _send_with_rate_limit(self, bot, message: str, **kwargs):
    """
    Send message with rate limiting.
    
    Telegram limits:
    - 30 messages per second to same chat
    - 20 messages per minute to same chat (for groups)
    
    Args:
        bot: Target bot instance
        message: Message to send
        **kwargs: Additional arguments
    """
    # Add to queue
    await self.message_queue.put({
        "bot": bot,
        "message": message,
        "kwargs": kwargs,
        "timestamp": datetime.now()
    })
    
    # Process queue
    await self._process_message_queue()

async def _process_message_queue(self):
    """Process message queue with rate limiting"""
    while not self.message_queue.empty():
        item = await self.message_queue.get()
        
        # Check rate limit
        # (Implementation depends on rate_limiter.py)
        
        try:
            await item["bot"].send_message(item["message"], **item["kwargs"])
        except Exception as e:
            self.logger.error(f"Failed to send queued message: {e}")
        
        # Small delay between messages
        await asyncio.sleep(0.05)
```

---

## GRACEFUL DEGRADATION

### Fallback Logic (Lines 422-460)

```python
async def _send_with_fallback(self, primary_bot, message: str, **kwargs):
    """
    Send message with fallback to other bots.
    
    Fallback order:
    1. Primary bot
    2. Notification bot
    3. Controller bot
    4. Fallback single bot
    
    Args:
        primary_bot: Primary target bot
        message: Message to send
        **kwargs: Additional arguments
    """
    bots_to_try = [
        primary_bot,
        self.notification_bot,
        self.controller_bot,
        self.fallback_bot
    ]
    
    for bot in bots_to_try:
        if bot:
            try:
                await bot.send_message(message, **kwargs)
                return True
            except Exception as e:
                self.logger.warning(f"Bot failed, trying next: {e}")
                continue
    
    self.logger.error("All bots failed to send message")
    return False
```

---

## VOICE ALERT INTEGRATION

### Voice Alert Bridge (Lines 462-477)

```python
def trigger_voice_alert(self, alert_type: str, data: Dict[str, Any]):
    """
    Trigger voice alert through VoiceAlertSystem.
    
    Args:
        alert_type: Type of alert
        data: Alert data
    """
    if hasattr(self, 'voice_alert_system') and self.voice_alert_system:
        try:
            self.voice_alert_system.play_alert(alert_type, data)
        except Exception as e:
            self.logger.error(f"Voice alert failed: {e}")

def set_voice_alert_system(self, voice_system):
    """Set voice alert system reference"""
    self.voice_alert_system = voice_system
```

---

## CONFIGURATION

### Multi-Bot Config

```python
{
    # Single bot (fallback)
    "telegram_token": "BOT_TOKEN",
    "telegram_chat_id": "CHAT_ID",
    
    # Multi-bot tokens (optional)
    "telegram_controller_token": "CONTROLLER_BOT_TOKEN",
    "telegram_notification_token": "NOTIFICATION_BOT_TOKEN",
    "telegram_analytics_token": "ANALYTICS_BOT_TOKEN",
    
    # Rate limiting
    "telegram_rate_limit": {
        "messages_per_second": 30,
        "messages_per_minute": 20
    }
}
```

---

## MESSAGE FLOW

```
Event Occurs
     |
     v
+------------------+
| MultiTelegram    |
| Manager          |
+------------------+
     |
     +---> Determine notification type
     |
     +---> Route to appropriate bot
     |
     v
+------------------+     +------------------+     +------------------+
| Controller Bot   |     | Notification Bot |     | Analytics Bot    |
| (Commands/Admin) |     | (Trade Alerts)   |     | (Reports/Stats)  |
+------------------+     +------------------+     +------------------+
     |                        |                        |
     v                        v                        v
+------------------+     +------------------+     +------------------+
| Rate Limiter     |     | Rate Limiter     |     | Rate Limiter     |
+------------------+     +------------------+     +------------------+
     |                        |                        |
     v                        v                        v
+------------------------------------------------------------------+
|                        Telegram API                               |
+------------------------------------------------------------------+
```

---

## RELATED FILES

- `src/telegram/controller_bot.py` - Controller bot implementation
- `src/telegram/notification_bot.py` - Notification bot implementation
- `src/telegram/analytics_bot.py` - Analytics bot implementation
- `src/telegram/rate_limiter.py` - Rate limiting
- `src/telegram/telegram_bot_fixed.py` - Legacy single bot (fallback)
- `src/modules/voice_alert_system.py` - Voice alerts
