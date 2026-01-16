# Real Clock System Documentation

**Version:** 1.0.0  
**Date:** 2026-01-15  
**Phase:** 9 - Legacy Restoration  

## Overview

The Real Clock System provides accurate IST (India Standard Time) display for the trading bot. It powers the sticky header time display and provides time utilities for session management.

## File Location

`src/modules/fixed_clock_system.py`

## Core Features

### 1. IST Timezone Support

The system uses `pytz` for accurate timezone handling:

- Default timezone: `Asia/Kolkata` (IST)
- Configurable via constructor
- Handles daylight saving automatically

### 2. Time Formatting

Multiple format options for different display contexts:

| Method | Output Example |
|--------|----------------|
| `format_time_string()` | "14:30:45 IST" |
| `format_date_string()` | "15 Jan 2026 (Wed)" |
| `format_clock_message()` | Combined time + date |

### 3. Callback System

Register callbacks to receive clock updates:

```python
clock = get_clock_system()
clock.register_callback(my_update_function)
```

### 4. Async Clock Loop

Background loop for real-time updates:

```python
await clock.start_clock_loop(update_interval=1)  # Updates every second
```

## Key Classes

### `FixedClockSystem`

Main class for clock functionality.

**Constructor:**
```python
def __init__(self, timezone: str = "Asia/Kolkata"):
    """
    Initialize the clock system.
    
    Args:
        timezone: Timezone string (default: Asia/Kolkata for IST)
    """
```

**Key Methods:**

```python
def get_current_time(self) -> datetime:
    """Get current time in configured timezone"""

def format_time_string(self) -> str:
    """Format time as HH:MM:SS IST"""

def format_date_string(self) -> str:
    """Format date as DD MMM YYYY (Day)"""

def format_clock_message(self) -> str:
    """Format combined clock and calendar message for sticky header"""

async def start_clock_loop(self, update_interval: int = 1):
    """Start the clock update loop"""

def stop_clock_loop(self):
    """Stop the clock update loop"""

def register_callback(self, callback: Callable):
    """Register callback for clock updates"""

def get_time_components(self) -> Dict[str, int]:
    """Get individual time components (hour, minute, second)"""
```

### `get_clock_system()` (Singleton)

Factory function that returns the global clock instance:

```python
from src.modules.fixed_clock_system import get_clock_system

clock = get_clock_system()
current_time = clock.format_time_string()
```

## Sticky Header Integration

The clock system is integrated with the Controller Bot sticky header:

```python
def create_controller_content_generator(data_providers: Dict[str, Callable]) -> Callable:
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
        
        return (
            f"<b>ZEPIX CONTROLLER BOT</b>\n"
            f"Time: <b>{time_str}</b>\n"
            f"Date: {date_str}\n"
            # ... rest of header
        )
    return generator
```

## Trading Engine Integration

The clock system is initialized in the trading engine:

```python
class TradingEngine:
    def __init__(self, ...):
        # ... other initialization ...
        
        # Phase 9: Initialize Clock System (Legacy Restoration)
        self.clock_system = get_clock_system()
```

## V5 Architecture Mapping

| V4 Feature | V5 Component |
|------------|--------------|
| Real clock display | FixedClockSystem class |
| Pinned message time | Controller Bot sticky header |
| Session time checks | Session Manager integration |
| Calendar display | format_date_string() method |

## Configuration

The clock system uses minimal configuration:

```python
# Default configuration
CLOCK_CONFIG = {
    "timezone": "Asia/Kolkata",
    "update_interval": 1,  # seconds
    "format_24h": True
}
```

## Time Components

For session management, the clock provides time components:

```python
components = clock.get_time_components()
# Returns: {"hour": 14, "minute": 30, "second": 45}

# Use for session checks
if components["hour"] >= 5 and components["hour"] < 14:
    current_session = "Asian"
```

## Testing

To test the clock system:

1. Import and get clock instance
2. Verify timezone is IST
3. Check time format matches expected output
4. Test callback registration
5. Verify async loop updates correctly

```python
# Test code
from src.modules.fixed_clock_system import get_clock_system

clock = get_clock_system()
print(f"Time: {clock.format_time_string()}")
print(f"Date: {clock.format_date_string()}")
print(f"Components: {clock.get_time_components()}")
```

## Error Handling

The system handles common errors:

- Missing pytz: Falls back to system timezone
- Invalid timezone: Uses default IST
- Callback errors: Logs and continues

## Related Documentation

- `01_CORE_TRADING_ENGINE.md` - Engine initialization
- `30_TELEGRAM_3BOT_SYSTEM.md` - Sticky header display
- `31_SESSION_MANAGER.md` - Session time checks
- `32_VOICE_ALERT_SYSTEM.md` - Time-based alerts
