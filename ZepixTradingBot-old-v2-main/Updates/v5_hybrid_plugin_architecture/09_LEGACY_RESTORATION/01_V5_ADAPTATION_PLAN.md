# V5 LEGACY RESTORATION & ADAPTATION PLAN

**Date:** 2026-01-15  
**Source:** V4 Forex Session System Documentation  
**Target:** V5 Hybrid Plugin Architecture  
**Status:** PLANNING COMPLETE - READY FOR IMPLEMENTATION

---

## EXECUTIVE SUMMARY

This plan adapts the V4 legacy features to the V5 3-Bot Telegram Architecture:

| V4 Feature | V5 Target | Integration Point |
|------------|-----------|-------------------|
| Real Clock System | Controller Bot | Sticky Header |
| Forex Session Manager | Controller Bot | Trade Filtering |
| Voice Alert System | Notification Bot | Trade Events |
| Calendar Display | Controller Bot | Sticky Header |

---

## PART 1: REAL CLOCK SYSTEM RESTORATION

### V4 Original Design (from `00_PROJECT_BRIEF.md`)

**Purpose:** Display real-time IST clock and calendar in Telegram with fixed positioning.

**V4 Features:**
- Timezone: `Asia/Kolkata` (IST)
- Display format: `HH:MM:SS IST`
- Date format: `DD MMM YYYY (Day)`
- Update frequency: Every second
- Telegram integration: Pinned message

### V5 Adaptation Strategy

**Target Location:** `src/modules/fixed_clock_system.py` (currently EMPTY)

**V5 Integration Points:**
1. **Controller Bot** - Owns the clock display
2. **Sticky Header** - Clock integrated into `src/telegram/sticky_headers.py`
3. **Session Manager** - Clock provides time for session checks

### V5 Implementation Plan

#### Step 1: Implement `src/modules/fixed_clock_system.py`

```python
"""
Fixed Clock & Calendar Display System V5
Provides real-time IST time and date for V5 3-Bot Architecture
"""

import asyncio
from datetime import datetime
import pytz
from typing import Optional
import logging

class FixedClockSystem:
    """Real-time IST clock for V5 Telegram system."""
    
    def __init__(self):
        self.timezone = pytz.timezone('Asia/Kolkata')
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self._callbacks = []
    
    def get_current_ist_time(self) -> datetime:
        """Get current time in IST timezone"""
        return datetime.now(self.timezone)
    
    def format_time_string(self) -> str:
        """Format time as HH:MM:SS IST"""
        current_time = self.get_current_ist_time()
        return current_time.strftime("%H:%M:%S IST")
    
    def format_date_string(self) -> str:
        """Format date as DD MMM YYYY (Day)"""
        current_time = self.get_current_ist_time()
        return current_time.strftime("%d %b %Y (%A)")
    
    def format_clock_message(self) -> str:
        """Format combined clock and calendar message"""
        time_str = self.format_time_string()
        date_str = self.format_date_string()
        return f"🕐 {time_str} | 📅 {date_str}"
    
    def register_callback(self, callback):
        """Register callback for clock updates"""
        self._callbacks.append(callback)
    
    async def start_clock_loop(self, update_interval: int = 1):
        """Start the clock update loop"""
        self.is_running = True
        self.logger.info("Starting fixed clock loop...")
        
        while self.is_running:
            try:
                for callback in self._callbacks:
                    await callback(self.format_clock_message())
                await asyncio.sleep(update_interval)
            except Exception as e:
                self.logger.error(f"Clock loop error: {e}")
                await asyncio.sleep(5)
    
    def stop_clock(self):
        """Stop the clock loop"""
        self.is_running = False
        self.logger.info("Clock loop stopped")
```

#### Step 2: Integrate with Sticky Header

**File:** `src/telegram/sticky_headers.py`

**Current State:** Sticky header exists but doesn't include clock.

**Modification:**
```python
# Add clock to sticky header format
def format_sticky_header(self) -> str:
    """Format sticky header with clock, session, and status"""
    clock_str = self.clock_system.format_clock_message()
    session_str = self.session_manager.get_session_status_text()
    
    return f"""
{clock_str}
{session_str}
━━━━━━━━━━━━━━━━
"""
```

#### Step 3: Wire into Controller Bot

**File:** `src/telegram/controller_bot.py`

**Integration:**
```python
# In ControllerBot.__init__
from src.modules.fixed_clock_system import FixedClockSystem
self.clock_system = FixedClockSystem()

# In start method
asyncio.create_task(self.clock_system.start_clock_loop())
```

---

## PART 2: FOREX SESSION MANAGER INTEGRATION

### V4 Original Design (from `01_IMPLEMENTATION_PLAN.md`)

**Purpose:** Manage Forex session timings, symbol filtering, and trade permissions.

**V4 Sessions:**
| Session | Start (IST) | End (IST) | Symbols |
|---------|-------------|-----------|---------|
| Asian | 05:30 | 14:30 | USDJPY, AUDUSD, EURJPY |
| London | 13:00 | 22:00 | GBPUSD, EURUSD, GBPJPY |
| Overlap | 18:00 | 20:30 | All major pairs |
| NY Late | 22:00 | 02:00 | USDCAD, EURUSD |
| Dead Zone | 02:00 | 05:30 | None |

### V5 Current State

**File:** `src/modules/session_manager.py` (529 lines - FULLY IMPLEMENTED)

**Status:** CODE EXISTS but needs V5 integration verification.

### V5 Adaptation Strategy

The Session Manager is already implemented. We need to:

1. **Verify wiring** to trading_engine.py
2. **Add to Controller Bot** for Telegram menu access
3. **Integrate with Sticky Header** for session display
4. **Wire to Notification Bot** for session transition alerts

#### Step 1: Verify Trading Engine Integration

**File:** `src/core/trading_engine.py`

**Current State (verified in Phase 8 audit):**
```python
# Line 1273-1274: Session check before trade
if hasattr(self.telegram_bot, 'session_manager'):
    session_check = self.telegram_bot.session_manager.check_trade_allowed(symbol)
```

**Status:** ALREADY WIRED - No changes needed.

#### Step 2: Add Session Menu to Controller Bot

**File:** `src/telegram/controller_bot.py`

**Add handler:**
```python
# Register session menu handler
from src.telegram.session_menu_handler import SessionMenuHandler
self.session_menu = SessionMenuHandler(self.session_manager)
self.register_handler("session_dashboard", self.session_menu.show_dashboard)
```

#### Step 3: Integrate with Sticky Header

**File:** `src/telegram/sticky_headers.py`

**Add session info:**
```python
def get_session_info(self) -> str:
    """Get current session info for header"""
    session = self.session_manager.get_current_session()
    if session == "none":
        return "🔴 Dead Zone (No Trading)"
    
    session_data = self.session_manager.config['sessions'][session]
    symbols = session_data.get('allowed_symbols', [])
    return f"🟢 {session_data['name']} | ✅ {', '.join(symbols[:3])}..."
```

#### Step 4: Wire Session Alerts to Notification Bot

**File:** `src/telegram/notification_bot.py`

**Add session transition handler:**
```python
async def send_session_alert(self, session_name: str, alert_type: str):
    """Send session transition alert"""
    if alert_type == "starting":
        message = f"🔔 {session_name} starting in 30 minutes"
    elif alert_type == "started":
        message = f"🟢 {session_name} has started"
    elif alert_type == "ending":
        message = f"⚠️ {session_name} ending soon"
    
    await self.send_notification("session_alert", message)
```

---

## PART 3: VOICE ALERT SYSTEM WIRING

### V4 Original Design (from `10_VOICE_NOTIFICATION_FINAL_IMPLEMENTATION_PLAN.md`)

**Purpose:** Multi-channel alert delivery with Windows TTS and Telegram notifications.

**V4 Channels:**
1. **Windows Speaker** - Direct TTS via pyttsx3
2. **Telegram Text** - With notification sound
3. **SMS** - Emergency fallback

**V4 Priority Levels:**
| Priority | Channels | Use Case |
|----------|----------|----------|
| CRITICAL | Windows + Text + SMS | System crashes, major losses |
| HIGH | Windows + Text | Order execution |
| MEDIUM | Windows + Text | SL/TP hits |
| LOW | Text only | Session alerts |

### V5 Current State

**Files:**
- `src/modules/voice_alert_system.py` (429 lines - FULLY IMPLEMENTED)
- `src/modules/windows_audio_player.py` (EXISTS)
- `src/telegram/voice_alert_integration.py` (EXISTS)

**Status:** CODE EXISTS but NOT wired to trading_engine.py.

### V5 Adaptation Strategy

Wire Voice Alerts to:
1. **Trading Engine** - Trade events (open, close, SL, TP)
2. **Notification Bot** - Route voice alerts through notification system
3. **Plugin System** - Allow plugins to trigger voice alerts

#### Step 1: Wire to Trading Engine

**File:** `src/core/trading_engine.py`

**Add import:**
```python
from src.modules.voice_alert_system import VoiceAlertSystem, AlertPriority
```

**Add initialization:**
```python
# In __init__
self.voice_alerts = VoiceAlertSystem(
    bot=self.telegram_bot.bot,
    chat_id=self.config.get('telegram_chat_id')
)
```

**Add trade event triggers:**
```python
# After trade opened
async def _on_trade_opened(self, trade):
    await self.voice_alerts.send_voice_alert(
        f"Trade opened. {trade.direction} {trade.symbol} at {trade.entry_price}",
        priority=AlertPriority.HIGH
    )

# After SL hit
async def _on_sl_hit(self, trade):
    await self.voice_alerts.send_voice_alert(
        f"Stop loss hit. {trade.symbol} closed with {trade.pnl} dollars",
        priority=AlertPriority.MEDIUM
    )

# After TP hit
async def _on_tp_hit(self, trade):
    await self.voice_alerts.send_voice_alert(
        f"Take profit reached. {trade.symbol} closed with {trade.pnl} dollars profit",
        priority=AlertPriority.MEDIUM
    )
```

#### Step 2: Integrate with Notification Bot

**File:** `src/telegram/notification_bot.py`

**Add voice alert bridge:**
```python
def set_voice_alert_system(self, voice_system):
    """Set voice alert system reference"""
    self.voice_alerts = voice_system

async def send_trade_notification_with_voice(self, trade_data: Dict):
    """Send trade notification with voice alert"""
    # Send text notification
    await self.send_trade_notification(trade_data)
    
    # Trigger voice alert
    if self.voice_alerts:
        message = self._format_voice_message(trade_data)
        priority = self._get_voice_priority(trade_data['type'])
        await self.voice_alerts.send_voice_alert(message, priority)
```

#### Step 3: Add to ServiceAPI for Plugin Access

**File:** `src/core/plugin_system/service_api.py`

**Add voice alert method:**
```python
def send_voice_alert(self, message: str, priority: str = "MEDIUM"):
    """Send voice alert from plugin"""
    if hasattr(self, 'voice_alerts') and self.voice_alerts:
        priority_enum = AlertPriority[priority]
        asyncio.create_task(
            self.voice_alerts.send_voice_alert(message, priority_enum)
        )
```

---

## PART 4: CALENDAR DISPLAY INTEGRATION

### V4 Original Design

**Purpose:** Show current date and day alongside the clock.

**V4 Format:** `DD MMM YYYY (Day)` - Example: `11 Jan 2026 (Saturday)`

### V5 Adaptation Strategy

Calendar is part of the Fixed Clock System (Part 1). No separate implementation needed.

**Integration:** Already included in `format_clock_message()`:
```python
def format_clock_message(self) -> str:
    time_str = self.format_time_string()  # 22:15:30 IST
    date_str = self.format_date_string()  # 15 Jan 2026 (Wednesday)
    return f"🕐 {time_str} | 📅 {date_str}"
```

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Real Clock System
- [ ] Implement `src/modules/fixed_clock_system.py` (currently empty)
- [ ] Add clock to `src/telegram/sticky_headers.py`
- [ ] Wire clock to Controller Bot
- [ ] Test clock display in Telegram

### Phase 2: Session Manager Integration
- [ ] Verify trading_engine.py wiring (already done)
- [ ] Add session menu to Controller Bot
- [ ] Add session info to Sticky Header
- [ ] Wire session alerts to Notification Bot
- [ ] Test session filtering

### Phase 3: Voice Alert Wiring
- [ ] Wire VoiceAlertSystem to trading_engine.py
- [ ] Add voice bridge to Notification Bot
- [ ] Add voice alert to ServiceAPI for plugins
- [ ] Test voice alerts on trade events

### Phase 4: Documentation
- [ ] Create `06_DOCUMENTATION_BIBLE/31_SESSION_MANAGER.md`
- [ ] Create `06_DOCUMENTATION_BIBLE/32_VOICE_ALERT_SYSTEM.md`
- [ ] Create `06_DOCUMENTATION_BIBLE/33_REAL_CLOCK_SYSTEM.md`

---

## FILE CHANGES SUMMARY

| File | Action | Description |
|------|--------|-------------|
| `src/modules/fixed_clock_system.py` | IMPLEMENT | Full clock system (currently empty) |
| `src/telegram/sticky_headers.py` | MODIFY | Add clock and session info |
| `src/telegram/controller_bot.py` | MODIFY | Wire clock and session menu |
| `src/telegram/notification_bot.py` | MODIFY | Add voice alert bridge |
| `src/core/trading_engine.py` | MODIFY | Wire voice alerts to trade events |
| `src/core/plugin_system/service_api.py` | MODIFY | Add voice alert method |

---

## SUCCESS CRITERIA

| Feature | Verification |
|---------|--------------|
| Real Clock | Clock displays in Telegram sticky header |
| Calendar | Date displays alongside clock |
| Session Manager | Trades filtered by session rules |
| Session Alerts | 30-min advance alerts fire |
| Voice Alerts | Windows speaker plays on trade events |
| Telegram Sound | Phone notification sound on alerts |

---

## ESTIMATED TIMELINE

- **Phase 1 (Clock):** 30 minutes
- **Phase 2 (Session):** 30 minutes
- **Phase 3 (Voice):** 45 minutes
- **Phase 4 (Docs):** 30 minutes

**Total:** ~2.5 hours

---

**Plan Status:** READY FOR IMPLEMENTATION  
**Approval Required:** User approval before code changes

---

**Report Generated:** 2026-01-15 18:25 UTC  
**Devin Session:** https://app.devin.ai/sessions/4b58f5ede2b9495d874258f2c0f230e5
