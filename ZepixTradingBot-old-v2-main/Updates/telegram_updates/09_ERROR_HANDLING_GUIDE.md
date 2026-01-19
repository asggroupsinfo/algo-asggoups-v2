# 🚨 ERROR HANDLING GUIDE - COMPLETE DOCUMENTATION

**Created:** January 19, 2026  
**Bot Version:** V5 Hybrid Plugin Architecture  
**Scope:** All error scenarios, error codes, solutions, and error handling implementation

---

## 📑 TABLE OF CONTENTS

1. [Error Categories](#error-categories)
2. [Telegram API Errors](#telegram-api-errors)
3. [MT5 Connection Errors](#mt5-connection-errors)
4. [Database Errors](#database-errors)
5. [Plugin System Errors](#plugin-system-errors)
6. [Trading Engine Errors](#trading-engine-errors)
7. [Notification Errors](#notification-errors)
8. [Menu System Errors](#menu-system-errors)
9. [Error Recovery Procedures](#error-recovery-procedures)
10. [Error Logging](#error-logging)

---

## 🏷️ ERROR CATEGORIES

### **Error Classification Matrix**

| Category | Severity | Auto-Recovery | User Action Required |
|----------|----------|---------------|---------------------|
| **CRITICAL** | 🔴 High | No | Yes - Immediate |
| **MAJOR** | 🟠 Medium | Partial | Yes - Soon |
| **MINOR** | 🟡 Low | Yes | No |
| **INFO** | 🟢 None | N/A | No |

### **Error Code Prefixes**

```
TG-XXX  : Telegram API errors
MT-XXX  : MetaTrader 5 errors
DB-XXX  : Database errors
PL-XXX  : Plugin system errors
TE-XXX  : Trading engine errors
NF-XXX  : Notification errors
MN-XXX  : Menu system errors
```

---

## 📱 TELEGRAM API ERRORS

### **TG-001: HTTP 409 Conflict**

| Error Code | TG-001 |
|------------|--------|
| **Description** | Telegram polling conflict |
| **Severity** | 🔴 CRITICAL |
| **Message** | `Conflict: terminated by other getUpdates request` |
| **Cause** | Multiple bot instances running |
| **Impact** | Bot stops receiving updates |

**Solution:**
```python
# Error handling code
async def handle_409_error(self):
    """Handle HTTP 409 Conflict"""
    self.http409_count += 1
    
    if self.http409_count >= 3:
        logger.critical("TG-001: Multiple 409 errors - stopping polling")
        await self.stop_polling()
        await asyncio.sleep(5)
        await self.safe_polling_restart()
        self.http409_count = 0
```

**User Action:**
1. Stop all other bot instances
2. Check for duplicate START_BOT.bat running
3. Restart the single instance

---

### **TG-002: Rate Limit Exceeded**

| Error Code | TG-002 |
|------------|--------|
| **Description** | Too many requests to Telegram API |
| **Severity** | 🟠 MAJOR |
| **Message** | `RetryAfter: Flood control exceeded. Retry in X seconds` |
| **Cause** | Sending too many messages |
| **Impact** | Messages delayed |

**Solution:**
```python
async def handle_rate_limit(self, retry_after: int):
    """Handle Telegram rate limit"""
    logger.warning(f"TG-002: Rate limited, waiting {retry_after}s")
    
    # Exponential backoff
    await asyncio.sleep(retry_after)
    
    # Reduce message frequency
    self.message_queue_delay = max(self.message_queue_delay * 1.5, 2.0)
```

**Prevention:**
- Batch notifications (max 20/minute)
- Use message queue
- Edit messages instead of sending new ones

---

### **TG-003: Invalid Token**

| Error Code | TG-003 |
|------------|--------|
| **Description** | Bot token invalid or revoked |
| **Severity** | 🔴 CRITICAL |
| **Message** | `Unauthorized: Invalid token` |
| **Cause** | Token changed or revoked |
| **Impact** | Bot cannot connect |

**Solution:**
1. Get new token from @BotFather
2. Update `config/config.json`:
```json
{
    "telegram": {
        "bot_token": "NEW_TOKEN_HERE"
    }
}
```
3. Restart bot

---

### **TG-004: Chat Not Found**

| Error Code | TG-004 |
|------------|--------|
| **Description** | Target chat ID invalid |
| **Severity** | 🟠 MAJOR |
| **Message** | `Bad Request: chat not found` |
| **Cause** | User blocked bot or wrong chat ID |
| **Impact** | Cannot send notifications |

**Solution:**
```python
async def handle_chat_not_found(self, chat_id: int):
    """Handle missing chat"""
    logger.error(f"TG-004: Chat {chat_id} not found")
    
    # Remove from notification list
    if chat_id in self.notification_chat_ids:
        self.notification_chat_ids.remove(chat_id)
    
    # Notify admin
    await self.notify_admin(f"Chat {chat_id} no longer reachable")
```

---

### **TG-005: Message Too Long**

| Error Code | TG-005 |
|------------|--------|
| **Description** | Message exceeds 4096 character limit |
| **Severity** | 🟡 MINOR |
| **Message** | `Bad Request: message is too long` |
| **Cause** | Notification content too large |
| **Impact** | Message not sent |

**Solution:**
```python
async def send_long_message(self, chat_id: int, message: str):
    """Split and send long messages"""
    MAX_LENGTH = 4096
    
    if len(message) <= MAX_LENGTH:
        await self.bot.send_message(chat_id, message)
    else:
        # Split into chunks
        chunks = [message[i:i+MAX_LENGTH] for i in range(0, len(message), MAX_LENGTH)]
        for i, chunk in enumerate(chunks):
            await self.bot.send_message(chat_id, f"({i+1}/{len(chunks)})\n{chunk}")
            await asyncio.sleep(0.5)  # Rate limit protection
```

---

### **TG-006: Callback Query Expired**

| Error Code | TG-006 |
|------------|--------|
| **Description** | Button clicked after message expired |
| **Severity** | 🟡 MINOR |
| **Message** | `Bad Request: query is too old` |
| **Cause** | User clicked button on old message |
| **Impact** | Button action fails |

**Solution:**
```python
async def handle_callback_query(self, query):
    """Handle callback with expiry check"""
    try:
        # Process callback
        await self.process_callback(query)
    except telegram.error.BadRequest as e:
        if "query is too old" in str(e):
            logger.info("TG-006: Expired callback, sending fresh menu")
            await query.message.reply_text(
                "⚠️ This menu has expired. Here's a fresh one:",
                reply_markup=self.build_main_menu()
            )
```

---

## 🖥️ MT5 CONNECTION ERRORS

### **MT-001: Connection Failed**

| Error Code | MT-001 |
|------------|--------|
| **Description** | Cannot connect to MT5 terminal |
| **Severity** | 🔴 CRITICAL |
| **Message** | `MT5 connection failed` |
| **Cause** | MT5 terminal not running |
| **Impact** | Trading disabled |

**Solution:**
```python
async def handle_mt5_disconnect(self):
    """Handle MT5 connection failure"""
    logger.critical("MT-001: MT5 connection lost")
    
    # Pause trading
    self.trading_enabled = False
    
    # Notify user
    await self.telegram.send_message(
        "🚨 MT5 DISCONNECTED\n\n"
        "Trading has been paused.\n"
        "Please check MT5 terminal.\n\n"
        "Bot will auto-reconnect when MT5 is available."
    )
    
    # Attempt reconnection
    for attempt in range(5):
        await asyncio.sleep(10)
        if self.mt5_client.connect():
            logger.info("MT-001: MT5 reconnected")
            await self.telegram.send_message("✅ MT5 Reconnected!")
            return True
    
    return False
```

**User Action:**
1. Open MetaTrader 5 terminal
2. Login to account
3. Wait for auto-reconnect or restart bot

---

### **MT-002: Order Failed**

| Error Code | MT-002 |
|------------|--------|
| **Description** | Order execution failed |
| **Severity** | 🟠 MAJOR |
| **MT5 Error Codes** | 10004, 10006, 10009, 10010, 10014, 10015 |
| **Cause** | Various (see sub-codes) |

**MT5 Error Code Reference:**
```python
MT5_ERROR_CODES = {
    10004: "Requote - price changed",
    10006: "Request rejected",
    10009: "Invalid request",
    10010: "Invalid price",
    10014: "Invalid volume",
    10015: "Invalid stops",
    10016: "Trade disabled",
    10017: "Market closed",
    10018: "Insufficient funds",
    10019: "Prices changed",
    10020: "No quotes",
    10021: "Invalid expiration",
    10022: "Order changed",
    10023: "Too many requests",
    10024: "No changes",
    10025: "Autotrading disabled by server",
    10026: "Autotrading disabled by client terminal",
    10027: "Request locked",
    10028: "Order or position frozen",
    10029: "Invalid order filling type",
    10030: "No connection to trade server",
    10031: "Operation not allowed in demo",
    10032: "Order limit exceeded",
    10033: "Margin requirement exceeded"
}
```

**Error Handling:**
```python
async def handle_order_error(self, error_code: int, symbol: str, direction: str):
    """Handle MT5 order errors"""
    error_msg = MT5_ERROR_CODES.get(error_code, f"Unknown error {error_code}")
    logger.error(f"MT-002: Order failed - {error_msg}")
    
    # Notify user
    await self.telegram.send_message(
        f"❌ ORDER FAILED\n\n"
        f"Symbol: {symbol}\n"
        f"Direction: {direction}\n"
        f"Error: {error_msg}\n"
        f"Code: {error_code}"
    )
    
    # Specific handling
    if error_code in [10018, 10033]:  # Insufficient funds
        await self.handle_insufficient_funds()
    elif error_code == 10017:  # Market closed
        await self.handle_market_closed(symbol)
    elif error_code == 10016:  # Trade disabled
        await self.handle_trading_disabled()
```

---

### **MT-003: Invalid Symbol**

| Error Code | MT-003 |
|------------|--------|
| **Description** | Symbol not available |
| **Severity** | 🟠 MAJOR |
| **Message** | `Symbol XXXXX not found` |
| **Cause** | Symbol not in market watch |

**Solution:**
```python
async def validate_symbol(self, symbol: str) -> bool:
    """Validate symbol before trading"""
    symbol_info = self.mt5_client.get_symbol_info(symbol)
    
    if symbol_info is None:
        logger.error(f"MT-003: Symbol {symbol} not found")
        await self.telegram.send_message(
            f"⚠️ Symbol {symbol} not available.\n"
            f"Please add it to Market Watch in MT5."
        )
        return False
    
    if not symbol_info.get('visible'):
        logger.warning(f"MT-003: Symbol {symbol} not visible")
        # Try to add to market watch
        self.mt5_client.symbol_select(symbol, True)
    
    return True
```

---

## 💾 DATABASE ERRORS

### **DB-001: Connection Lost**

| Error Code | DB-001 |
|------------|--------|
| **Description** | SQLite database connection lost |
| **Severity** | 🟠 MAJOR |
| **Message** | `database is locked` or `disk I/O error` |
| **Cause** | File locked or corrupted |

**Solution:**
```python
def handle_db_connection_error(self):
    """Handle database connection errors"""
    logger.error("DB-001: Database connection error")
    
    try:
        # Close existing connection
        if self.conn:
            self.conn.close()
        
        # Reconnect
        self.conn = sqlite3.connect(
            'data/trading_bot.db',
            check_same_thread=False,
            timeout=30.0  # Increased timeout
        )
        
        # Enable WAL mode for better concurrency
        self.conn.execute("PRAGMA journal_mode=WAL")
        
        logger.info("DB-001: Database reconnected")
        return True
    except Exception as e:
        logger.critical(f"DB-001: Cannot reconnect - {e}")
        return False
```

---

### **DB-002: Table Not Found**

| Error Code | DB-002 |
|------------|--------|
| **Description** | Required table missing |
| **Severity** | 🟠 MAJOR |
| **Message** | `no such table: XXX` |
| **Cause** | Database not initialized |

**Solution:**
```python
def ensure_tables_exist(self):
    """Create tables if missing"""
    required_tables = [
        'trades',
        'reentry_chains',
        'sl_events',
        'tp_reentry_events',
        'profit_booking_chains',
        'profit_booking_orders',
        'profit_booking_events',
        'trading_sessions',
        'system_state'
    ]
    
    cursor = self.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing = [row[0] for row in cursor.fetchall()]
    
    for table in required_tables:
        if table not in existing:
            logger.warning(f"DB-002: Table {table} missing, creating...")
            self.create_tables()
            break
```

---

### **DB-003: Data Integrity Error**

| Error Code | DB-003 |
|------------|--------|
| **Description** | Data constraint violated |
| **Severity** | 🟡 MINOR |
| **Message** | `UNIQUE constraint failed` |
| **Cause** | Duplicate entry |

**Solution:**
```python
def save_trade_safe(self, trade):
    """Save trade with conflict handling"""
    try:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO trades (...)
            VALUES (...)
        """, trade_values)
        self.conn.commit()
    except sqlite3.IntegrityError as e:
        logger.warning(f"DB-003: Integrity error - {e}")
        # Update existing record instead
        cursor.execute("""
            UPDATE trades SET ... WHERE trade_id = ?
        """, (trade.trade_id,))
        self.conn.commit()
```

---

## 🔌 PLUGIN SYSTEM ERRORS

### **PL-001: Plugin Load Failed**

| Error Code | PL-001 |
|------------|--------|
| **Description** | Cannot load plugin |
| **Severity** | 🟠 MAJOR |
| **Message** | `Failed to load plugin: XXX` |
| **Cause** | Import error or missing dependency |

**Solution:**
```python
def load_plugin_safe(self, plugin_id: str):
    """Load plugin with error handling"""
    try:
        plugin_module = importlib.import_module(f"src.logic_plugins.{plugin_id}")
        plugin_class = getattr(plugin_module, 'Plugin')
        plugin = plugin_class(self.service_api)
        
        self.plugins[plugin_id] = plugin
        logger.info(f"Plugin loaded: {plugin_id}")
        return True
        
    except ImportError as e:
        logger.error(f"PL-001: Import error for {plugin_id}: {e}")
        self.plugin_errors[plugin_id] = f"Import failed: {e}"
        return False
        
    except AttributeError as e:
        logger.error(f"PL-001: Plugin class not found in {plugin_id}: {e}")
        self.plugin_errors[plugin_id] = f"Invalid plugin structure: {e}"
        return False
        
    except Exception as e:
        logger.error(f"PL-001: Unknown error loading {plugin_id}: {e}")
        self.plugin_errors[plugin_id] = str(e)
        return False
```

---

### **PL-002: Plugin Process Error**

| Error Code | PL-002 |
|------------|--------|
| **Description** | Plugin crashed during signal processing |
| **Severity** | 🟠 MAJOR |
| **Message** | `Plugin XXX crashed: Exception` |
| **Cause** | Bug in plugin code |

**Solution:**
```python
async def process_signal_safe(self, plugin_id: str, signal: dict):
    """Process signal with error isolation"""
    plugin = self.plugins.get(plugin_id)
    if not plugin:
        logger.error(f"PL-002: Plugin {plugin_id} not found")
        return None
    
    try:
        return await asyncio.wait_for(
            plugin.process_signal(signal),
            timeout=30.0  # 30 second timeout
        )
    except asyncio.TimeoutError:
        logger.error(f"PL-002: Plugin {plugin_id} timed out")
        await self.telegram.send_message(
            f"⚠️ Plugin {plugin_id} timeout\n"
            f"Signal processing exceeded 30s limit"
        )
        return None
    except Exception as e:
        logger.error(f"PL-002: Plugin {plugin_id} error: {e}")
        await self.telegram.send_message(
            f"❌ Plugin Error\n\n"
            f"Plugin: {plugin_id}\n"
            f"Error: {str(e)[:200]}"
        )
        return None
```

---

### **PL-003: Plugin Config Error**

| Error Code | PL-003 |
|------------|--------|
| **Description** | Invalid plugin configuration |
| **Severity** | 🟡 MINOR |
| **Message** | `Invalid config for plugin XXX` |
| **Cause** | Missing or invalid config values |

**Solution:**
```python
def validate_plugin_config(self, plugin_id: str, config: dict) -> bool:
    """Validate plugin configuration"""
    required_fields = {
        'combinedlogic-1': ['enabled', 'risk_percentage'],
        'combinedlogic-2': ['enabled', 'risk_percentage'],
        'combinedlogic-3': ['enabled', 'risk_percentage'],
        'v6_15m': ['enabled', 'timeframe'],
        'v6_30m': ['enabled', 'timeframe'],
        'v6_1h': ['enabled', 'timeframe'],
        'v6_4h': ['enabled', 'timeframe'],
    }
    
    fields = required_fields.get(plugin_id, ['enabled'])
    
    for field in fields:
        if field not in config:
            logger.warning(f"PL-003: Missing {field} in {plugin_id} config")
            config[field] = self.get_default_value(field)
    
    return True
```

---

## ⚙️ TRADING ENGINE ERRORS

### **TE-001: Signal Validation Failed**

| Error Code | TE-001 |
|------------|--------|
| **Description** | Invalid signal received |
| **Severity** | 🟡 MINOR |
| **Message** | `Invalid signal: missing required fields` |
| **Cause** | Malformed TradingView alert |

**Required Signal Fields:**
```python
REQUIRED_SIGNAL_FIELDS = [
    'symbol',      # e.g., "XAUUSD"
    'direction',   # "BUY" or "SELL"
    'entry',       # Entry price
]

OPTIONAL_SIGNAL_FIELDS = [
    'sl',          # Stop loss price
    'tp',          # Take profit price
    'logic',       # Logic route (LOGIC1/2/3)
    'timeframe',   # Timeframe (1M/5M/15M/etc)
]
```

**Validation Code:**
```python
def validate_signal(self, signal: dict) -> Tuple[bool, str]:
    """Validate incoming signal"""
    errors = []
    
    # Check required fields
    for field in REQUIRED_SIGNAL_FIELDS:
        if field not in signal or signal[field] is None:
            errors.append(f"Missing {field}")
    
    # Validate direction
    direction = signal.get('direction', '').upper()
    if direction not in ['BUY', 'SELL']:
        errors.append(f"Invalid direction: {direction}")
    
    # Validate symbol
    symbol = signal.get('symbol', '')
    if not self.is_valid_symbol(symbol):
        errors.append(f"Invalid symbol: {symbol}")
    
    if errors:
        logger.warning(f"TE-001: Signal validation failed - {errors}")
        return False, ", ".join(errors)
    
    return True, ""
```

---

### **TE-002: Risk Limit Exceeded**

| Error Code | TE-002 |
|------------|--------|
| **Description** | Trade rejected due to risk limits |
| **Severity** | 🟡 MINOR |
| **Message** | `Risk limit exceeded` |
| **Cause** | Daily/lifetime loss limit reached |

**Solution:**
```python
async def check_risk_limits(self, symbol: str, lot_size: float) -> dict:
    """Check all risk limits before trading"""
    result = {
        'allowed': True,
        'violations': []
    }
    
    # Daily loss limit
    daily_pnl = await self.database.get_daily_pnl()
    daily_limit = self.config.get('risk_config', {}).get('daily_loss_limit', 500)
    
    if daily_pnl <= -daily_limit:
        result['allowed'] = False
        result['violations'].append(f"Daily loss limit ({daily_limit}) reached")
        logger.warning(f"TE-002: Daily loss limit reached: {daily_pnl}")
    
    # Lifetime loss limit
    lifetime_loss = await self.database.get_lifetime_loss()
    lifetime_limit = self.config.get('risk_config', {}).get('lifetime_loss_limit', 5000)
    
    if lifetime_loss >= lifetime_limit:
        result['allowed'] = False
        result['violations'].append(f"Lifetime loss limit ({lifetime_limit}) reached")
        logger.critical(f"TE-002: Lifetime loss limit reached: {lifetime_loss}")
    
    # Notify if blocked
    if not result['allowed']:
        await self.telegram.send_message(
            f"🛑 TRADE BLOCKED\n\n"
            f"Reasons:\n" + "\n".join(f"• {v}" for v in result['violations'])
        )
    
    return result
```

---

### **TE-003: Duplicate Trade Blocked**

| Error Code | TE-003 |
|------------|--------|
| **Description** | Same signal processed twice |
| **Severity** | 🟡 MINOR |
| **Message** | `Duplicate signal blocked` |
| **Cause** | Webhook sent multiple times |

**Solution:**
```python
class SignalDeduplicator:
    def __init__(self, ttl_seconds: int = 60):
        self.recent_signals = {}
        self.ttl = ttl_seconds
    
    def is_duplicate(self, signal: dict) -> bool:
        """Check if signal is duplicate"""
        # Create unique key
        key = f"{signal.get('symbol')}_{signal.get('direction')}_{signal.get('entry')}"
        
        # Check cache
        if key in self.recent_signals:
            last_time = self.recent_signals[key]
            if (datetime.now() - last_time).seconds < self.ttl:
                logger.info(f"TE-003: Duplicate signal blocked: {key}")
                return True
        
        # Store signal
        self.recent_signals[key] = datetime.now()
        self._cleanup_old_signals()
        return False
    
    def _cleanup_old_signals(self):
        """Remove expired signals"""
        cutoff = datetime.now() - timedelta(seconds=self.ttl * 2)
        self.recent_signals = {
            k: v for k, v in self.recent_signals.items()
            if v > cutoff
        }
```

---

## 🔔 NOTIFICATION ERRORS

### **NF-001: Notification Queue Full**

| Error Code | NF-001 |
|------------|--------|
| **Description** | Too many pending notifications |
| **Severity** | 🟡 MINOR |
| **Message** | `Notification queue full` |
| **Cause** | Rapid trade activity |

**Solution:**
```python
class NotificationQueue:
    MAX_QUEUE_SIZE = 100
    
    async def enqueue(self, notification: dict):
        """Add notification with overflow handling"""
        if len(self.queue) >= self.MAX_QUEUE_SIZE:
            logger.warning("NF-001: Queue full, dropping oldest")
            # Remove oldest 10%
            self.queue = self.queue[10:]
        
        self.queue.append(notification)
    
    async def process_batch(self):
        """Process notifications in batches"""
        batch_size = 10
        batch = self.queue[:batch_size]
        self.queue = self.queue[batch_size:]
        
        for notification in batch:
            try:
                await self.send_notification(notification)
                await asyncio.sleep(0.5)  # Rate limit
            except Exception as e:
                logger.error(f"NF-001: Send failed - {e}")
```

---

### **NF-002: Voice Alert Failed**

| Error Code | NF-002 |
|------------|--------|
| **Description** | TTS or audio send failed |
| **Severity** | 🟡 MINOR |
| **Message** | `Voice alert generation failed` |
| **Cause** | TTS engine error or file too large |

**Solution:**
```python
async def send_voice_alert_safe(self, text: str):
    """Send voice alert with fallback"""
    try:
        # Generate TTS
        audio_path = await self.generate_tts(text)
        
        # Check file size (Telegram limit: 50MB)
        file_size = os.path.getsize(audio_path)
        if file_size > 50 * 1024 * 1024:
            raise ValueError("Audio file too large")
        
        # Send
        await self.bot.send_voice(self.chat_id, open(audio_path, 'rb'))
        
    except Exception as e:
        logger.warning(f"NF-002: Voice alert failed - {e}")
        # Fallback to text
        await self.bot.send_message(self.chat_id, f"🔊 {text}")
    
    finally:
        # Cleanup temp file
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
```

---

## 📱 MENU SYSTEM ERRORS

### **MN-001: Callback Handler Not Found**

| Error Code | MN-001 |
|------------|--------|
| **Description** | No handler for callback data |
| **Severity** | 🟡 MINOR |
| **Message** | `Unknown callback: XXX` |
| **Cause** | Handler not registered |

**Solution:**
```python
async def handle_callback(self, query):
    """Handle callback with fallback"""
    callback_data = query.data
    
    # Find handler
    handler = self.callback_handlers.get(callback_data)
    
    if handler is None:
        # Check partial matches
        for pattern, handler in self.callback_patterns.items():
            if callback_data.startswith(pattern):
                await handler(query, callback_data)
                return
        
        # No handler found
        logger.warning(f"MN-001: Unknown callback: {callback_data}")
        await query.answer("⚠️ This action is not available", show_alert=True)
        return
    
    await handler(query)
```

---

### **MN-002: Menu Build Error**

| Error Code | MN-002 |
|------------|--------|
| **Description** | Cannot build menu keyboard |
| **Severity** | 🟡 MINOR |
| **Message** | `Menu build failed` |
| **Cause** | Invalid button configuration |

**Solution:**
```python
def build_menu_safe(self, buttons: list) -> InlineKeyboardMarkup:
    """Build menu with validation"""
    try:
        keyboard = []
        
        for row in buttons:
            keyboard_row = []
            for button in row:
                # Validate button
                if 'text' not in button:
                    logger.warning("MN-002: Button missing text")
                    continue
                
                # Truncate long text
                text = button['text'][:64]
                
                # Create button
                if 'callback_data' in button:
                    # Truncate callback data (64 byte limit)
                    cb_data = button['callback_data'][:64]
                    keyboard_row.append(
                        InlineKeyboardButton(text, callback_data=cb_data)
                    )
                elif 'url' in button:
                    keyboard_row.append(
                        InlineKeyboardButton(text, url=button['url'])
                    )
            
            if keyboard_row:
                keyboard.append(keyboard_row)
        
        return InlineKeyboardMarkup(keyboard)
        
    except Exception as e:
        logger.error(f"MN-002: Menu build error - {e}")
        # Return simple fallback menu
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Main Menu", callback_data="menu_main")
        ]])
```

---

## 🔄 ERROR RECOVERY PROCEDURES

### **Auto-Recovery Matrix**

| Error | Auto-Recovery | Recovery Method |
|-------|---------------|-----------------|
| TG-001 (409) | Yes | Restart polling |
| TG-002 (Rate limit) | Yes | Wait and retry |
| TG-003 (Invalid token) | No | Manual fix required |
| MT-001 (Disconnect) | Yes | Auto reconnect loop |
| MT-002 (Order failed) | Partial | Retry with backoff |
| DB-001 (Connection) | Yes | Reconnect |
| PL-002 (Plugin crash) | Yes | Isolate and continue |
| TE-002 (Risk limit) | No | Wait for reset |

### **Recovery Code Template**

```python
async def auto_recovery_loop(self):
    """Main recovery loop"""
    while self.running:
        try:
            # Check MT5 connection
            if not self.mt5_client.is_connected():
                await self.recover_mt5_connection()
            
            # Check database
            if not self.database.test_connection():
                await self.recover_database_connection()
            
            # Check Telegram
            if not await self.telegram.is_healthy():
                await self.recover_telegram_connection()
            
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Recovery loop error: {e}")
            await asyncio.sleep(10)
```

---

## 📊 ERROR LOGGING

### **Log Format**

```python
# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)

# Error-specific logger
error_logger = logging.getLogger('errors')
error_handler = logging.FileHandler('logs/errors.log')
error_handler.setLevel(logging.ERROR)
error_logger.addHandler(error_handler)
```

### **Error Log Entry Format**

```
2026-01-19 10:30:45 | ERROR    | telegram | TG-001: HTTP 409 Conflict detected
2026-01-19 10:30:45 | ERROR    | telegram | Stack trace: ...
2026-01-19 10:30:45 | INFO     | telegram | Auto-recovery initiated
2026-01-19 10:30:50 | INFO     | telegram | Polling restarted successfully
```

### **Error Notification to Admin**

```python
async def notify_admin_error(self, error_code: str, error_msg: str, severity: str):
    """Send error notification to admin"""
    severity_emoji = {
        'CRITICAL': '🔴',
        'MAJOR': '🟠',
        'MINOR': '🟡',
        'INFO': '🟢'
    }
    
    message = (
        f"{severity_emoji.get(severity, '⚪')} <b>ERROR ALERT</b>\n\n"
        f"<b>Code:</b> <code>{error_code}</code>\n"
        f"<b>Severity:</b> {severity}\n"
        f"<b>Message:</b> {error_msg}\n"
        f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await self.bot.send_message(
        self.admin_chat_id,
        message,
        parse_mode='HTML'
    )
```

---

**Document Created:** January 19, 2026  
**Total Error Codes:** 25+  
**Categories:** 7  
**Status:** COMPLETE ✅

---

## ⚠️ DEVELOPER NOTE - IMPORTANT

**Bot Source Code Location:**  
`C:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-New-v1\ZepixTradingBot-old-v2-main\Trading_Bot`

### Implementation Guidelines:

> ⚠️ **This is a Planning & Research Document - DO NOT Apply Blindly!**

**Implementation Process:**

1. **First, Complete Scan of the Bot**
   - Analyze the complete bot code
   - Understand the current architecture
   - Review existing implementations

2. **Map Ideas According to the Bot**
   - Check how the ideas given here will be implemented in the bot
   - Identify dependencies
   - Look for conflicts

3. **Create New Plan According to the Bot**
   - Create a new implementation plan according to the bot's current state
   - Adapt ideas that don't directly fit

4. **Make Improvements (Full Freedom)**
   - You have full freedom to improve the ideas
   - Use a better approach if available
   - Optimize according to the bot's architecture

5. **Then Implement**
   - Implement only after planning is complete

### Critical Rules:

| Rule | Description |
|------|-------------|
| ✅ **Idea Must Be Fully Implemented** | The core idea/concept must be fully implemented |
| ✅ **Improvements Allowed** | You can improve the implementation |
| ❌ **Idea Should Not Change** | The core concept of the idea must remain the same |
| ❌ **Do Not Apply Blindly** | First scan, plan, then implement |

**Remember:** This document provides ideas & possibilities - the final implementation will depend on the bot's actual architecture.

---

**END OF DOCUMENT**