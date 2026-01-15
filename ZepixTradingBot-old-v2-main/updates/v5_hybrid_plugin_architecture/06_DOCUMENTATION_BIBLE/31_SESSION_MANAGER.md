# Session Manager Documentation

**Version:** 1.0.0  
**Date:** 2026-01-15  
**Phase:** 9 - Legacy Restoration  

## Overview

The Session Manager controls trading activity based on forex market sessions. It filters which symbols can be traded during specific time windows and provides advance alerts before session transitions.

## File Location

`src/managers/session_manager.py`

## Core Features

### 1. Session Definitions

The system supports 5 forex sessions with IST (India Standard Time) timings:

| Session | Start (IST) | End (IST) | Primary Symbols |
|---------|-------------|-----------|-----------------|
| Asian | 05:30 | 14:30 | USDJPY, AUDUSD, EURJPY |
| London | 13:00 | 22:00 | GBPUSD, EURUSD, GBPJPY |
| Overlap | 18:00 | 20:30 | All major pairs |
| NY Late | 22:00 | 02:00 | USDCAD, EURUSD |
| Dead Zone | 02:00 | 05:30 | None (no trading) |

### 2. Symbol Filtering

Each session has a whitelist of allowed symbols. When a trade signal arrives:

1. Session Manager checks current time
2. Determines active session
3. Validates if symbol is allowed in current session
4. Returns True/False for trade permission

### 3. Advance Alerts

The system sends alerts 30 minutes before session transitions:

- "Asian Session starting in 30 minutes"
- "London Session starting in 30 minutes"
- "Dead Zone approaching - consider closing positions"

### 4. Force Close Feature

Optional auto-close of all trades when entering Dead Zone:

- Configurable per session
- Default: Enabled for Dead Zone only
- Sends notification before closing

## Configuration

Configuration stored in `data/session_settings.json`:

```json
{
  "version": "1.0",
  "master_switch": true,
  "timezone": "Asia/Kolkata",
  "sessions": {
    "asian": {
      "name": "Asian Session",
      "start_time": "05:30",
      "end_time": "14:30",
      "allowed_symbols": ["USDJPY", "AUDUSD", "EURJPY"],
      "advance_alert_enabled": true,
      "advance_alert_minutes": 30,
      "force_close_enabled": false
    }
  }
}
```

## Key Methods

### `get_current_session() -> str`

Returns the name of the currently active session based on IST time.

### `is_symbol_allowed(symbol: str) -> bool`

Checks if a symbol can be traded in the current session.

### `get_session_info() -> Dict`

Returns detailed information about the current session including:
- Session name
- Time remaining
- Allowed symbols
- Next session

### `check_advance_alerts()`

Called periodically to check if any advance alerts should be sent.

## Integration Points

### Trading Engine Integration

The Session Manager is called from `trading_engine.py` before executing any trade:

```python
if not self.session_manager.is_symbol_allowed(symbol):
    logger.info(f"Symbol {symbol} not allowed in current session")
    return None
```

### Sticky Header Integration

Current session is displayed in the Controller Bot sticky header:

```python
current_session = data_providers.get("current_session", lambda: "Unknown")()
```

### Notification Bot Integration

Session alerts are routed through the Notification Bot for delivery.

## V5 Architecture Mapping

| V4 Feature | V5 Component |
|------------|--------------|
| Session filtering | Trading Engine pre-trade check |
| Session display | Controller Bot sticky header |
| Session alerts | Notification Bot routing |
| Force close | Trading Engine close_trade() |

## Testing

To test session filtering:

1. Set system time to different session periods
2. Attempt trades with various symbols
3. Verify only allowed symbols are executed
4. Check advance alerts are sent at correct times

## Related Documentation

- `01_CORE_TRADING_ENGINE.md` - Trade execution flow
- `30_TELEGRAM_3BOT_SYSTEM.md` - Notification routing
- `32_VOICE_ALERT_SYSTEM.md` - Voice alerts for sessions
- `33_REAL_CLOCK_SYSTEM.md` - IST time display
