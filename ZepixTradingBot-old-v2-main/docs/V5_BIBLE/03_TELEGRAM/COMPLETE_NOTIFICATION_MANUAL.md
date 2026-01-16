# COMPLETE NOTIFICATION MANUAL

**Zepix Trading Bot V5 - Notification System Guide**  
**Version:** 1.0  
**Date:** 2026-01-16

---

## TABLE OF CONTENTS

1. [Overview](#1-overview)
2. [Notification Architecture](#2-notification-architecture)
3. [Trading Notifications](#3-trading-notifications)
4. [Autonomous System Notifications](#4-autonomous-system-notifications)
5. [Re-Entry System Notifications](#5-re-entry-system-notifications)
6. [Risk & Safety Notifications](#6-risk--safety-notifications)
7. [System Notifications](#7-system-notifications)
8. [Analytics Notifications](#8-analytics-notifications)
9. [Configuration Notifications](#9-configuration-notifications)
10. [Priority System](#10-priority-system)
11. [Mute/Unmute Controls](#11-muteunmute-controls)
12. [Voice Alert Integration](#12-voice-alert-integration)
13. [Quick Reference](#13-quick-reference)

---

## 1. OVERVIEW

The Zepix Trading Bot V5 notification system provides real-time alerts for all trading activities, system events, and configuration changes. The system uses a unified router that directs notifications to the appropriate bot based on type.

### Key Features

- 46 distinct notification types
- 3-bot routing (Controller, Notification, Analytics)
- 4 priority levels (CRITICAL, HIGH, MEDIUM, LOW)
- Mute/unmute controls for individual types or priorities
- Voice alert integration for critical events
- Statistics tracking for all notifications

### Source Files

| File | Purpose | Lines |
|------|---------|-------|
| `src/telegram/unified_notification_router.py` | Central routing | 646 |
| `src/telegram/notification_bot.py` | Trade alerts | 347 |
| `src/telegram/controller_bot.py` | Commands & system | 762 |
| `src/telegram/analytics_bot.py` | Reports | ~300 |

---

## 2. NOTIFICATION ARCHITECTURE

### 2.1 3-Bot System

The V5 architecture uses three specialized bots:

```
                    ┌─────────────────────┐
                    │ UnifiedNotification │
                    │       Router        │
                    └─────────┬───────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ ControllerBot │    │NotificationBot│    │ AnalyticsBot  │
│   (System)    │    │   (Trading)   │    │  (Reports)    │
└───────────────┘    └───────────────┘    └───────────────┘
```

### 2.2 Routing Rules

| Notification Category | Target Bot |
|----------------------|------------|
| Trade entries/exits | NotificationBot |
| TP/SL hits | NotificationBot |
| Recovery events | NotificationBot |
| Risk alerts | NotificationBot |
| System startup/shutdown | ControllerBot |
| Config changes | ControllerBot |
| Plugin events | ControllerBot |
| Errors | ControllerBot |
| Performance reports | AnalyticsBot |
| Daily/Weekly summaries | AnalyticsBot |

### 2.3 Fallback Mode

If only one bot is configured, all notifications route to that bot:

```python
# Single-bot mode
router = UnifiedNotificationRouter(fallback_bot=my_bot)
```

---

## 3. TRADING NOTIFICATIONS

### 3.1 Trade Entry (`trade_entry`)

**Trigger:** New trade opened  
**Priority:** HIGH  
**Target:** NotificationBot

```
🟢 ENTRY ALERT | V3_Combined_Logic
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: XAUUSD
Direction: BUY
Entry: 2650.50
Time: 14:32:15
```

**Data Fields:**
- `symbol` - Trading symbol
- `direction` - BUY or SELL
- `entry_price` - Entry price
- `plugin_name` - Plugin that placed trade

### 3.2 Trade Exit (`trade_exit`)

**Trigger:** Trade closed  
**Priority:** HIGH  
**Target:** NotificationBot

```
🟢 EXIT ALERT
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: XAUUSD
P&L: +$45.50
Reason: Take Profit
Time: 15:10:22
```

**Data Fields:**
- `symbol` - Trading symbol
- `profit` - Profit/loss amount
- `reason` - Close reason

### 3.3 Take Profit Hit (`tp_hit`)

**Trigger:** TP level reached  
**Priority:** HIGH  
**Target:** NotificationBot

```
🎯 TAKE PROFIT HIT!
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: XAUUSD
Profit: +$32.00
Time: 14:45:30
```

### 3.4 Stop Loss Hit (`sl_hit`)

**Trigger:** SL level reached  
**Priority:** HIGH  
**Target:** NotificationBot

```
🛑 STOP LOSS HIT
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: XAUUSD
Loss: -$15.00
Time: 14:50:12
```

### 3.5 Profit Booking (`profit_booking`)

**Trigger:** Partial profit taken  
**Priority:** MEDIUM  
**Target:** NotificationBot

```
💰 PROFIT BOOKED
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: XAUUSD
Level: 2
Profit: +$20.00
Time: 14:55:00
```

### 3.6 Additional Trading Types

| Type | Trigger | Priority |
|------|---------|----------|
| `partial_close` | Partial position closed | MEDIUM |
| `sl_modified` | Stop loss moved | LOW |
| `tp_modified` | Take profit moved | LOW |

---

## 4. AUTONOMOUS SYSTEM NOTIFICATIONS

### 4.1 TP Continuation (`tp_continuation`)

**Trigger:** Autonomous re-entry after TP  
**Priority:** MEDIUM  
**Target:** NotificationBot

```
🚀 AUTONOMOUS RE-ENTRY
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: XAUUSD (BUY)
Type: TP Continuation
Level: 3
Time: 15:00:00
```

### 4.2 SL Hunt Activated (`sl_hunt_activated`)

**Trigger:** Recovery attempt started  
**Priority:** HIGH  
**Target:** NotificationBot

```
🛡️ SL HUNT ACTIVATED
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: XAUUSD
SL Price: 2640.00
Status: Monitoring...
Time: 15:05:00
```

### 4.3 Recovery Success (`recovery_success`)

**Trigger:** SL Hunt recovery successful  
**Priority:** MEDIUM  
**Target:** NotificationBot

```
🎉 RECOVERY SUCCESS
━━━━━━━━━━━━━━━━━━━━━━━━

Chain: abc123
Resumed to Level: 3
Status: ACTIVE
Time: 15:10:00
```

### 4.4 Recovery Failed (`recovery_failed`)

**Trigger:** SL Hunt recovery failed  
**Priority:** HIGH  
**Target:** NotificationBot

```
💀 RECOVERY FAILED
━━━━━━━━━━━━━━━━━━━━━━━━

Chain: abc123
Reason: Price did not recover
Status: STOPPED
Time: 15:15:00
```

### 4.5 Additional Autonomous Types

| Type | Trigger | Priority |
|------|---------|----------|
| `sl_hunt_monitoring` | Monitoring active | MEDIUM |
| `chain_resume` | Chain resumed | MEDIUM |
| `chain_complete` | All levels done | MEDIUM |
| `profit_order_sl_hunt` | Profit order protection | HIGH |

---

## 5. RE-ENTRY SYSTEM NOTIFICATIONS

### 5.1 Re-Entry Triggered (`reentry_triggered`)

**Trigger:** Re-entry conditions met  
**Priority:** MEDIUM  
**Target:** NotificationBot

```
🔄 RE-ENTRY TRIGGERED
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: XAUUSD
Level: 2 → 3
Mode: Autonomous
Time: 15:20:00
```

### 5.2 Additional Re-Entry Types

| Type | Trigger | Priority |
|------|---------|----------|
| `reentry_config_changed` | Config updated | LOW |
| `cooldown_active` | Cooldown period | LOW |
| `recovery_window_timeout` | Window expired | MEDIUM |

---

## 6. RISK & SAFETY NOTIFICATIONS

### 6.1 Daily Limit Warning (`daily_limit_warning`)

**Trigger:** Approaching daily loss limit  
**Priority:** HIGH  
**Target:** NotificationBot

```
⚠️ DAILY LOSS WARNING
━━━━━━━━━━━━━━━━━━━━━━━━

Current Loss: $80.00
Daily Limit: $100.00
Remaining: $20.00
Time: 16:00:00

⚠️ Trade cautiously!
```

### 6.2 Daily Limit Hit (`daily_limit_hit`)

**Trigger:** Daily loss limit reached  
**Priority:** CRITICAL  
**Target:** NotificationBot

```
🛑 DAILY LOSS LIMIT REACHED
━━━━━━━━━━━━━━━━━━━━━━━━

Loss Today: $100.50
Limit: $100.00

✋ TRADING PAUSED AUTOMATICALLY
Reset Time: 03:35 UTC
```

### 6.3 Lifetime Limit Hit (`lifetime_limit_hit`)

**Trigger:** Lifetime loss limit reached  
**Priority:** CRITICAL  
**Target:** NotificationBot

```
🚨 LIFETIME LOSS LIMIT REACHED
━━━━━━━━━━━━━━━━━━━━━━━━

Total Loss: $1050.00
Limit: $1000.00

🛑 TRADING STOPPED
Manual intervention required
```

### 6.4 Additional Risk Types

| Type | Trigger | Priority |
|------|---------|----------|
| `profit_protection_blocked` | Recovery blocked | MEDIUM |
| `daily_recovery_limit` | Max recoveries reached | HIGH |

---

## 7. SYSTEM NOTIFICATIONS

### 7.1 Bot Startup (`bot_startup`)

**Trigger:** Bot initialized  
**Priority:** MEDIUM  
**Target:** ControllerBot

```
🤖 ZEPIX BOT STARTED
━━━━━━━━━━━━━━━━━━━━━━━━

Version: 2.0
Mode: LIVE
Time: 08:00:00

🚀 Bot is ready to trade!
```

### 7.2 Error Alert (`error_alert`)

**Trigger:** Error occurred  
**Priority:** HIGH  
**Target:** ControllerBot

```
❌ ERROR ALERT
━━━━━━━━━━━━━━━━━━━━━━━━

Type: Order Placement Failed
Severity: 🔴 HIGH
Details: Insufficient margin
Time: 16:30:00
```

### 7.3 Additional System Types

| Type | Trigger | Priority |
|------|---------|----------|
| `bot_shutdown` | Bot stopping | MEDIUM |
| `mt5_connected` | MT5 connected | MEDIUM |
| `mt5_disconnected` | MT5 lost | CRITICAL |
| `health_check` | Health status | LOW |

---

## 8. ANALYTICS NOTIFICATIONS

### 8.1 Daily Summary (`daily_summary`)

**Trigger:** End of day report  
**Priority:** LOW  
**Target:** AnalyticsBot

```
📊 DAILY SUMMARY | 2026-01-16
━━━━━━━━━━━━━━━━━━━━━━━━

Trades: 12 total
• ✅ Winning: 8
• ❌ Losing: 4
• 📈 Win Rate: 66.7%

P&L:
• 🟢 Total: +$125.50
• 🏆 Best: +$45.00
• 📉 Worst: -$15.00
```

### 8.2 All Analytics Types

| Type | Description | Priority |
|------|-------------|----------|
| `performance_report` | Performance metrics | LOW |
| `daily_summary` | Daily stats | LOW |
| `weekly_summary` | Weekly stats | LOW |
| `monthly_summary` | Monthly stats | LOW |
| `trade_history` | Trade log | LOW |
| `plugin_performance` | Plugin stats | LOW |
| `trend_analysis` | Trend report | LOW |
| `statistics_summary` | Overall stats | LOW |

---

## 9. CONFIGURATION NOTIFICATIONS

### 9.1 Plugin Enabled (`plugin_enabled`)

**Trigger:** Plugin activated  
**Priority:** MEDIUM  
**Target:** ControllerBot

```
✅ PLUGIN ENABLED
━━━━━━━━━━━━━━━━━━━━━━━━

Plugin: V3_Combined_Logic
Status: ACTIVE 🟢
Time: 09:00:00
```

### 9.2 Plugin Disabled (`plugin_disabled`)

**Trigger:** Plugin deactivated  
**Priority:** MEDIUM  
**Target:** ControllerBot

```
🔴 PLUGIN DISABLED
━━━━━━━━━━━━━━━━━━━━━━━━

Plugin: V6_Price_Action_5M
Status: INACTIVE 🔴
Time: 09:05:00
```

### 9.3 Config Changed (`config_changed`)

**Trigger:** Setting modified  
**Priority:** LOW  
**Target:** ControllerBot

```
⚙️ CONFIG CHANGED
━━━━━━━━━━━━━━━━━━━━━━━━

Setting: lot_size
Old: 0.02
New: 0.05
Time: 09:10:00
```

### 9.4 All Config Types

| Type | Trigger | Priority |
|------|---------|----------|
| `sl_system_changed` | SL system switched | LOW |
| `risk_tier_changed` | Risk tier changed | MEDIUM |
| `logic_enabled` | Logic strategy on | MEDIUM |
| `logic_disabled` | Logic strategy off | MEDIUM |

---

## 10. PRIORITY SYSTEM

### 10.1 Priority Levels

| Level | Description | Delivery |
|-------|-------------|----------|
| CRITICAL | Emergency - immediate action needed | Instant |
| HIGH | Important trading events | Instant |
| MEDIUM | Standard notifications | Normal |
| LOW | Informational, can be batched | Delayed OK |

### 10.2 Critical Notifications

These notifications are NEVER muted:

1. `daily_limit_hit` - Trading paused
2. `lifetime_limit_hit` - Trading stopped
3. `mt5_disconnected` - Cannot trade

### 10.3 Priority Distribution

```
CRITICAL:  3 types (6.5%)
HIGH:     10 types (21.7%)
MEDIUM:   15 types (32.6%)
LOW:      18 types (39.1%)
```

---

## 11. MUTE/UNMUTE CONTROLS

### 11.1 Mute Specific Type

```python
from src.telegram.unified_notification_router import get_notification_router

router = get_notification_router()

# Mute trade entries
router.mute("trade_entry")

# Unmute trade entries
router.unmute("trade_entry")
```

### 11.2 Mute by Priority

```python
from src.telegram.unified_notification_router import NotificationPriority

# Mute all LOW priority
router.mute_priority(NotificationPriority.LOW)

# Unmute LOW priority
router.unmute_priority(NotificationPriority.LOW)
```

### 11.3 Do Not Disturb Mode

```python
# Mute ALL notifications
router.mute_all()

# Restore all notifications
router.unmute_all()
```

### 11.4 Telegram Commands

| Command | Action |
|---------|--------|
| `/mute trade_entry` | Mute trade entries |
| `/unmute trade_entry` | Unmute trade entries |
| `/mute_all` | Do Not Disturb |
| `/unmute_all` | Restore all |

---

## 12. VOICE ALERT INTEGRATION

### 12.1 Voice Alert Setup

```python
from src.modules.voice_alert_system import VoiceAlertSystem

voice_system = VoiceAlertSystem()
notification_bot.set_voice_alert_system(voice_system)
```

### 12.2 Voice Alert Triggers

| Event | Voice Message | Priority |
|-------|---------------|----------|
| Trade Entry | "New BUY on XAUUSD at 2650" | HIGH |
| Trade Exit | "Trade closed on XAUUSD. Profit: 45 dollars" | HIGH |
| SL Hit | "Stop loss hit. XAUUSD loss 15 dollars" | CRITICAL |
| Daily Limit | "Warning. Daily loss limit reached. Trading paused." | CRITICAL |

### 12.3 Voice Priority Channels

| Priority | Channels |
|----------|----------|
| CRITICAL | Windows Audio + Text + SMS |
| HIGH | Windows Audio + Text |
| MEDIUM | Windows Audio + Text |
| LOW | Text only |

---

## 13. QUICK REFERENCE

### 13.1 All Notification Types

| Type | Priority | Bot |
|------|----------|-----|
| `trade_entry` | HIGH | Notification |
| `trade_exit` | HIGH | Notification |
| `tp_hit` | HIGH | Notification |
| `sl_hit` | HIGH | Notification |
| `profit_booking` | MEDIUM | Notification |
| `partial_close` | MEDIUM | Notification |
| `sl_modified` | LOW | Notification |
| `tp_modified` | LOW | Notification |
| `tp_continuation` | MEDIUM | Notification |
| `sl_hunt_activated` | HIGH | Notification |
| `sl_hunt_monitoring` | MEDIUM | Notification |
| `recovery_success` | MEDIUM | Notification |
| `recovery_failed` | HIGH | Notification |
| `chain_resume` | MEDIUM | Notification |
| `chain_complete` | MEDIUM | Notification |
| `profit_order_sl_hunt` | HIGH | Notification |
| `reentry_triggered` | MEDIUM | Notification |
| `reentry_config_changed` | LOW | Notification |
| `cooldown_active` | LOW | Notification |
| `recovery_window_timeout` | MEDIUM | Notification |
| `daily_limit_warning` | HIGH | Notification |
| `daily_limit_hit` | CRITICAL | Notification |
| `lifetime_limit_hit` | CRITICAL | Notification |
| `profit_protection_blocked` | MEDIUM | Notification |
| `daily_recovery_limit` | HIGH | Notification |
| `trend_updated` | LOW | Notification |
| `trend_locked` | LOW | Notification |
| `signal_received` | MEDIUM | Notification |
| `signal_filtered` | LOW | Notification |
| `signal_duplicate` | LOW | Notification |
| `performance_report` | LOW | Analytics |
| `daily_summary` | LOW | Analytics |
| `weekly_summary` | LOW | Analytics |
| `monthly_summary` | LOW | Analytics |
| `trade_history` | LOW | Analytics |
| `plugin_performance` | LOW | Analytics |
| `trend_analysis` | LOW | Analytics |
| `statistics_summary` | LOW | Analytics |
| `bot_startup` | MEDIUM | Controller |
| `bot_shutdown` | MEDIUM | Controller |
| `config_changed` | LOW | Controller |
| `plugin_enabled` | MEDIUM | Controller |
| `plugin_disabled` | MEDIUM | Controller |
| `error_alert` | HIGH | Controller |
| `mt5_connected` | MEDIUM | Controller |
| `mt5_disconnected` | CRITICAL | Controller |
| `health_check` | LOW | Controller |
| `sl_system_changed` | LOW | Controller |
| `risk_tier_changed` | MEDIUM | Controller |
| `logic_enabled` | MEDIUM | Controller |
| `logic_disabled` | MEDIUM | Controller |

### 13.2 Usage Example

```python
from src.telegram.unified_notification_router import get_notification_router

router = get_notification_router()

# Send a trade entry notification
router.send("trade_entry", {
    "symbol": "XAUUSD",
    "direction": "BUY",
    "entry_price": 2650.50,
    "plugin_name": "V3_Combined_Logic"
})

# Send an error alert
router.send("error_alert", {
    "error_type": "Order Placement Failed",
    "severity": "HIGH",
    "details": "Insufficient margin"
})

# Get notification statistics
stats = router.get_stats()
print(f"Total sent: {stats['total_sent']}")
print(f"Total muted: {stats['total_muted']}")
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-16  
**Total Notification Types:** 46  
**Total Categories:** 9
