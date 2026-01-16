# Voice Alert System Documentation

**Version:** 1.0.0  
**Date:** 2026-01-15  
**Phase:** 9 - Legacy Restoration  

## Overview

The Voice Alert System provides multi-channel audio notifications for critical trading events. It supports Windows TTS, Telegram text alerts, and SMS delivery with priority-based routing.

## File Location

`src/modules/voice_alert_system.py`

## Core Features

### 1. Alert Priority Levels

| Priority | Use Case | Delivery Channels |
|----------|----------|-------------------|
| CRITICAL | Emergency stop, major loss | All channels + repeat |
| HIGH | Trade opened, session change | TTS + Telegram |
| MEDIUM | SL/TP hit, trade closed | Telegram only |
| LOW | Status updates | Telegram (batched) |

### 2. Delivery Channels

**Windows TTS (Text-to-Speech)**
- Uses `pyttsx3` library
- Speaks alerts audibly on Windows machines
- Configurable voice and rate

**Telegram Text**
- Sends formatted text messages
- Routed through Notification Bot
- Supports HTML formatting

**SMS (Optional)**
- For CRITICAL alerts only
- Requires Twilio configuration
- Fallback when Telegram unavailable

### 3. Alert Types

| Event | Priority | Message Template |
|-------|----------|------------------|
| Trade Opened | HIGH | "Trade opened. {direction} {symbol} at {price}" |
| SL Hit | MEDIUM | "Stop loss hit. {symbol} closed with {profit} dollars" |
| TP Hit | MEDIUM | "Take profit reached. {symbol} closed with {profit} dollars profit" |
| Trade Closed | MEDIUM | "Trade closed. {symbol} with {profit} dollars" |
| Session Start | HIGH | "{session} session starting now" |
| Session End | MEDIUM | "{session} session ending" |
| Emergency | CRITICAL | "Emergency stop activated. All trades closed." |

## Configuration

Configuration in `config/voice_alerts.json`:

```json
{
  "enabled": true,
  "channels": {
    "tts": {
      "enabled": true,
      "voice": "default",
      "rate": 150
    },
    "telegram": {
      "enabled": true,
      "chat_id": "YOUR_CHAT_ID"
    },
    "sms": {
      "enabled": false,
      "phone": "+1234567890"
    }
  },
  "priority_routing": {
    "CRITICAL": ["tts", "telegram", "sms"],
    "HIGH": ["tts", "telegram"],
    "MEDIUM": ["telegram"],
    "LOW": ["telegram"]
  }
}
```

## Key Classes

### `AlertPriority` (Enum)

```python
class AlertPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### `VoiceAlertSystem`

Main class for managing voice alerts.

**Constructor:**
```python
def __init__(self, bot=None, chat_id: str = ""):
    """
    Initialize Voice Alert System.
    
    Args:
        bot: Telegram bot instance
        chat_id: Default chat ID for alerts
    """
```

**Key Methods:**

```python
async def send_voice_alert(self, message: str, priority: AlertPriority = AlertPriority.MEDIUM):
    """Send alert through configured channels based on priority"""

def speak_alert(self, message: str):
    """Speak alert using Windows TTS"""

async def send_telegram_alert(self, message: str):
    """Send alert via Telegram"""
```

## Trading Engine Integration

Voice alerts are wired into the trading engine at key events:

### Trade Opened
```python
async def on_trade_opened(self, trade_data: Dict[str, Any]):
    # ... existing notification code ...
    
    # Phase 9: Send voice alert
    voice_message = f"Trade opened. {direction} {symbol} at {price:.5f}"
    await self.send_voice_alert(voice_message, AlertPriority.HIGH)
```

### Trade Closed
```python
async def on_trade_closed(self, trade_data: Dict[str, Any]):
    # ... existing notification code ...
    
    # Phase 9: Send voice alert based on close reason
    if 'sl' in reason.lower() or 'stop' in reason.lower():
        voice_message = f"Stop loss hit. {symbol} closed with {profit:.2f} dollars"
        await self.send_voice_alert(voice_message, AlertPriority.MEDIUM)
    elif 'tp' in reason.lower() or 'profit' in reason.lower():
        voice_message = f"Take profit reached. {symbol} closed with {profit:.2f} dollars profit"
        await self.send_voice_alert(voice_message, AlertPriority.MEDIUM)
```

## V5 Architecture Mapping

| V4 Feature | V5 Component |
|------------|--------------|
| Voice alerts | VoiceAlertSystem class |
| Alert routing | Notification Bot |
| Trade event triggers | Trading Engine callbacks |
| Priority handling | AlertPriority enum |

## Notification Bot Integration

Voice alerts are routed through the Notification Bot for Telegram delivery:

```
Trading Engine
    |
    v
VoiceAlertSystem.send_voice_alert()
    |
    +---> Windows TTS (local)
    |
    +---> Notification Bot ---> Telegram
    |
    +---> SMS Gateway (optional)
```

## Testing

To test voice alerts:

1. Enable TTS in configuration
2. Trigger a test trade
3. Verify audio plays on Windows
4. Check Telegram receives message
5. Test priority routing by changing alert levels

## Error Handling

The system gracefully handles failures:

- TTS unavailable: Falls back to Telegram only
- Telegram offline: Logs error, continues operation
- SMS failure: Logs error, alerts via other channels

## Related Documentation

- `01_CORE_TRADING_ENGINE.md` - Trade event callbacks
- `30_TELEGRAM_3BOT_SYSTEM.md` - Notification Bot routing
- `31_SESSION_MANAGER.md` - Session alerts
- `33_REAL_CLOCK_SYSTEM.md` - Time-based alerts
