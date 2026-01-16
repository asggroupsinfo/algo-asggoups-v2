# ZEPIX TRADING BOT - COMPLETE TELEGRAM NOTIFICATIONS

**Last Updated:** 14-Jan-2026  
**Total Notification Types:** 50+ Unique Notifications  
**Source:** Deep Code Scan of Current Bot Implementation  
**Categorized:** By Trading Event & System Component

---

## 📋 TABLE OF CONTENTS

1. [🚀 Bot Startup & Status](#1--bot-startup--status)
2. [📊 Trading Notifications](#2--trading-notifications)
3. [⚡ Autonomous System Notifications](#3--autonomous-system-notifications)
4. [🔄 Re-Entry System Notifications](#4--re-entry-system-notifications)
5. [💎 Profit Booking Notifications](#5--profit-booking-notifications)
6. [🛡️ Risk & Safety Notifications](#6-️-risk--safety-notifications)
7. [📍 Trend & Signal Notifications](#7--trend--signal-notifications)
8. [⚙️ Configuration Change Notifications](#8-️-configuration-change-notifications)
9. [❌ Error & Warning Notifications](#9--error--warning-notifications)
10. [🔔 System Health & Diagnostics](#10--system-health--diagnostics)

---

## 1. 🚀 BOT STARTUP & STATUS

### 1.1 Bot Startup Success
**Trigger:** Bot successfully initializes  
**File:** `src/main.py` Line 246

```
🤖 ZEPIX TRADING BOT v2.0 STARTED 🤖
━━━━━━━━━━━━━━━━━━━━━━━
✅ MT5 Connected
✅ Telegram Active
✅ Database Ready
✅ All Systems Operational
━━━━━━━━━━━━━━━━━━━━━━━
🕐 Started At: [HH:MM:SS UTC]
📊 Mode: [LIVE/SIMULATION]
🎯 Active Strategies: LOGIC1, LOGIC2, LOGIC3
━━━━━━━━━━━━━━━━━━━━━━━
Bot is ready to trade! 🚀
```

---

### 1.2 Bot Initialization Failed
**Trigger:** Bot fails to start  
**File:** `src/main.py` Lines 221-229

```
❌ Bot failed to initialize
[Error Details]
Please check logs and restart
```

---

### 1.3 Bot Status Report
**Trigger:** `/status` command  
**File:** `src/clients/telegram_bot.py` Line 437-489

```
📊 BOT STATUS REPORT
━━━━━━━━━━━━━━━━━━━━
⚡ Trading: [ACTIVE ✅ / PAUSED ⏸️]
🎯 Mode: [LIVE / SIMULATION]
📈 Open Trades: [X]
💰 Today's P&L: $[Amount]
⏱️ Uptime: [Hours:Minutes]
🔄 Active Chains: [X]
━━━━━━━━━━━━━━━━━━━━
```

---

## 2. 📊 TRADING NOTIFICATIONS

### 2.1 New Trade Entry
**Trigger:** Order placed successfully  
**File:** `src/core/trading_engine.py`

```
🆕 NEW TRADE OPENED
━━━━━━━━━━━━━━━━━━━
📍 Symbol: [XAUUSD]
📊 Direction: [BUY/SELL]
💵 Entry: [Price]
🛡️ SL: [Price] ([X] pips)
🎯 TP: [Price] ([X] pips)
📦 Lot: [X]
🤖 Strategy: [LOGIC1/2/3]
🆔 Trade ID: #[ID]
━━━━━━━━━━━━━━━━━━━
Risk: $[Amount] | Pot. Profit: $[Amount]
```

---

### 2.2 Take Profit Hit
**Trigger:** TP reached  
**File:** `src/services/price_monitor_service.py` Line 178

```
🎯 TAKE PROFIT HIT! ✅
━━━━━━━━━━━━━━━━━━━
📍 Symbol: [XAUUSD]
💰 Profit: +$[Amount]
📈 Entry: [Price] → Exit: [Price]
🤖 Strategy: [LOGIC1]
🆔 Trade #[ID]
━━━━━━━━━━━━━━━━━━━
Total Today: +$[Amount]
```

---

### 2.3 Stop Loss Hit
**Trigger:** SL reached  
**File:** `src/services/price_monitor_service.py` Line 485

```
🛑 STOP LOSS HIT
━━━━━━━━━━━━━━━━━━━
📍 Symbol: [XAUUSD]
💸 Loss: -$[Amount]
📉 Entry: [Price] → Exit: [Price]
🤖 Strategy: [LOGIC1]
🆔 Trade #[ID]
━━━━━━━━━━━━━━━━━━━
[Chain Status Message if applicable]
```

---

### 2.4 Manual Trade Exit
**Trigger:** Trade closed manually  
**File:** `src/services/reversal_exit_handler.py` Line 164

```
🔄 MANUAL EXIT
━━━━━━━━━━━━━━━━━━━
📍 Symbol: [XAUUSD]  
💰 P&L: [+/-]$[Amount]
📊 Exit Price: [Price]
🔍 Reason: Manual close
🆔 Trade #[ID]
━━━━━━━━━━━━━━━━━━━
```

---

### 2.5 Reversal Exit
**Trigger:** Opposite signal triggered  
**File:** `src/services/reversal_exit_handler.py`

```
🔄 REVERSAL EXIT TRIGGERED
━━━━━━━━━━━━━━━━━━━
📍 Symbol: [XAUUSD]
🔄 Old: [BUY] → New: [SELL]
💰 P&L: [+/-]$[Amount]
🆔 Closed: #[ID]
━━━━━━━━━━━━━━━━━━━
Monitoring for continuation...
```

---

## 3. ⚡ AUTONOMOUS SYSTEM NOTIFICATIONS

### 3.1 TP Continuation Triggered
**Trigger:** Autonomous TP continuation activated  
**File:** `src/managers/autonomous_system_manager.py` Lines 625-647

```
🚀 **AUTONOMOUS RE-ENTRY** 🚀
━━━━━━━━━━━━━━━━━━━━━━━━
Symbol: [XAUUSD] ([BUY])
Type: TP Continuation
Progress: Level [2] ➡️ Level [3]

📍 ENTRY DETAILS
Entry: [2660.50]
SL: (30% reduced)

✅ CHECKS PASSED
• Trend: BULLISH 🟢
• Cooldown: 5s Complete ✅
• Momentum: Strong ⬆️

⏱️ TIMING
Placed: [12:34:56] UTC

🎯 CHAIN STATUS
Level: [3]/5
Total Profit: +$[120.00]
Status: ACTIVE 🟢
━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 3.2 SL Hunt Recovery Activated
**Trigger:** SL Hunt recovery triggered  
**File:** `src/managers/autonomous_system_manager.py` Lines 649-682

```
🛡️ **SL HUNT ACTIVATED** 🛡️
━━━━━━━━━━━━━━━━━━━━━━━━
Symbol: [XAUUSD] ([BUY])
Type: Recovery Entry
Attempt: 1/1

⚠️ ORIGINAL LOSS
SL Hit: [2640.00]
Time: [45] seconds

📍 RECOVERY ENTRY
Entry: [2642.50]
SL: [2640.00] ([50] pips - Tight)

✅ SAFETY CHECKS
• Price Recovery: ✅ Confirmed
• Trend: 🟢
• ATR: Stable ✅

💪 CHAIN CONTINUATION
If Success: Resume → Level [3]
If Fail: Chain STOP ❌
━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 3.3 Recovery Success - Chain Resume
**Trigger:** SL Hunt recovery successful  
**File:** `src/managers/autonomous_system_manager.py` Lines 722-728

```
🎉 **RECOVERY SUCCESS** 🎉
Chain: [chain_abc123]
Resumed to Level: [3]
Status: ACTIVE ✅
```

---

### 3.4 Recovery Failed - Chain Stopped
**Trigger:** SL Hunt recovery failed  
**File:** `src/managers/autonomous_system_manager.py` Lines 750-757

```
💀 **RECOVERY FAILED** 💀
Chain: [chain_abc123]
Status: STOPPED ❌
No more recovery attempts allowed
```

---

### 3.5 Profit Order SL Hunt
**Trigger:** Profit booking order SL hit  
**File:** `src/managers/autonomous_system_manager.py` Lines 684-703

```
💎 **PROFIT ORDER PROTECTION** 💎
━━━━━━━━━━━━━━━━━━━━━━━━
Chain: #[abc12345]
Level: [2]/4 (Order [3])

⚠️ SL HIT DETECTED
Order ID: #[12345]
SL Price: [2650.00]

🔄 MONITORING ACTIVE
Current Price: [2652.00]
Trend: BULLISH 🟢
Time: 30 mins remaining

⚡ NEXT STEPS
Watching for 2-pip recovery...
━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 4. 🔄 RE-ENTRY SYSTEM NOTIFICATIONS

### 4.1 TP Re-Entry Triggered
**Trigger:** TP hit, re-entry conditions met  
**File:** `src/managers/reentry_manager.py`

```
🔄 TP RE-ENTRY
━━━━━━━━━━━━━━━━━━━
Symbol: [XAUUSD]
Level: [2] → [3]
Mode: Autonomous
✅ Trend Aligned
━━━━━━━━━━━━━━━━━━━
```

---

### 4.2 SL Hunt Real-Time Monitoring
**Trigger:** Recovery window monitor active  
**File:** `src/managers/recovery_window_monitor.py` Lines 140-152

```
🔍 SL HUNT MONITORING STARTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order: #[12345] (Order A)
Symbol: [XAUUSD]
Direction: [BUY]
SL Price: [2640.00]
Recovery Threshold: [2642.00]
Min Recovery: [2] pips
Max Window: [15] minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Checking every 1s...
```

---

### 4.3 Price Recovered - Immediate Action
**Trigger:** Price recovery detected  
**File:** `src/managers/recovery_window_monitor.py` Lines 257-268

```
✅ PRICE RECOVERED - IMMEDIATE ACTION!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order: #[12345]
Symbol: [XAUUSD]
Recovery Price: [2642.00]
Current Price: [2643.50]
Recovery Time: [12.5] seconds
Check Count: [13]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Placing Recovery Order NOW...
```

---

### 4.4 Recovery Window Timeout
**Trigger:** Recovery window expired  
**File:** `src/managers/recovery_window_monitor.py` Lines 291-299

```
⏰ RECOVERY WINDOW TIMEOUT
━━━━━━━━━━━━━━━━━━━━━━
Order: #[12345]
Elapsed: [16.0] minutes
Max Window: [15.0] minutes
Status: FAILED - No recovery detected
━━━━━━━━━━━━━━━━━━━━━━
```

---

### 4.5 SL Hunt Recovery Order Placed
**Trigger:** Recovery order successfully placed  
**File:** `src/managers/recovery_window_monitor.py` Lines 352-364

```
🛡️ SL HUNT RECOVERY ORDER PLACED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recovery For: #[12345]
New Order: #[67890]
Entry: [2643.50]
SL: [2641.00] ([50.0] pips - Tight)
TP: [2655.00]
Lot: [0.01]
Order Type: [A]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recovery attempt in progress...
```

---

## 5. 💎 PROFIT BOOKING NOTIFICATIONS

### 5.1 Profit Booking Level Hit
**Trigger:** Profit target reached  
**File:** `src/managers/profit_booking_manager.py` Line 503

```
💎 PROFIT LEVEL REACHED
━━━━━━━━━━━━━━━━━━━
Chain: #[abc123]
Level: [2]
Target: $[20]
Actual: $[21.50]
━━━━━━━━━━━━━━━━━━━
Next Level: [3] → $[40] target
```

---

### 5.2 Profit Booking Chain Complete
**Trigger:** All levels completed  
**File:** `src/managers/profit_booking_manager.py` Line 686

```
🎉 PROFIT CHAIN COMPLETE!
━━━━━━━━━━━━━━━━━━━
Chain: #[abc123]
Total Profit: $[160]
Levels: 4/4 ✅
Success Rate: 100%
━━━━━━━━━━━━━━━━━━━
Excellent execution! 🚀
```

---

## 6. 🛡️ RISK & SAFETY NOTIFICATIONS

### 6.1 Daily Loss Limit Warning
**Trigger:** Approaching daily limit  
**File:** `src/managers/risk_manager.py`

```
⚠️ DAILY LOSS APPROACHING LIMIT
━━━━━━━━━━━━━━━━━━━
Current Loss: $[80]
Daily Limit: $[100]
Remaining: $[20] (20%)
━━━━━━━━━━━━━━━━━━━
Trade cautiously!
```

---

### 6.2 Daily Loss Limit Hit
**Trigger:** Daily limit reached  
**File:** `src/managers/risk_manager.py`

```
🛑 DAILY LOSS LIMIT REACHED
━━━━━━━━━━━━━━━━━━━
Loss Today: $[100.50]
Limit: $[100.00]
━━━━━━━━━━━━━━━━━━━
✋ TRADING PAUSED AUTOMATICALLY
Reset Time: 03:35 UTC
```

---

### 6.3 Lifetime Loss Limit Hit
**Trigger:** Lifetime limit reached  
**File:** `src/managers/risk_manager.py`

```
🚨 LIFETIME LOSS LIMIT REACHED
━━━━━━━━━━━━━━━━━━━
Total Loss: $[1050]
Limit: $[1000]
━━━━━━━━━━━━━━━━━━━
🛑 TRADING STOPPED
Manual intervention required
```

---

### 6.4 Profit Protection - Recovery Blocked
**Trigger:** Recovery blocked to protect profits  
**File:** `src/managers/autonomous_system_manager.py` Lines 111-115

```
🛡️ PROFIT PROTECTION: Skipping recovery for [chain_abc]
   Total Profit: $[120.00]
   Potential Loss: $[10.00]
   Ratio: [12.0]x (threshold: [5]x)
```

---

### 6.5 Daily Recovery Limit Hit
**Trigger:** Max daily recovery attempts reached  
**File:** `src/managers/autonomous_system_manager.py` Lines 68-70

```
⚠️ Daily recovery attempt limit reached ([10])
Trading continues, but NO MORE recoveries today
Reset: 03:35 UTC
```

---

## 7. 📍 TREND & SIGNAL NOTIFICATIONS

### 7.1 Trend Updated (Manual Lock)
**Trigger:** Trend manually set while locked  
**Description:** Bot sends info message that trend was NOT changed due to lock

```
🔒 TREND LOCKED - Signal Ignored
━━━━━━━━━━━━━━━━━━━
Symbol: [XAUUSD]
Timeframe: [5m]
Incoming Signal: [BUY]
Current Trend: [SELL] (LOCKED 🔒)
━━━━━━━━━━━━━━━━━━━
Trend remains unchanged
```

---

### 7.2 Trend Updated (Auto Mode)
**Trigger:** Trend auto-updated  
**File:** `src/managers/timeframe_trend_manager.py`

```
📊 TREND UPDATE
━━━━━━━━━━━━━━━━━━━
Symbol: [XAUUSD]
Timeframe: [5m]
Old: [NEUTRAL]
New: [BULLISH] 🟢
Mode: AUTO ✅
━━━━━━━━━━━━━━━━━━━
```

---

### 7.3 Signal Duplicate Filtered
**Trigger:** Duplicate signal received  
**File:** `src/processors/alert_processor.py` Line 40

```
🔄 Duplicate signal filtered for [XAUUSD]
Already processed within 60 seconds
```

---

## 8. ⚙️ CONFIGURATION CHANGE NOTIFICATIONS

### 8.1 SL System Changed
**Trigger:** SL system switched  
**File:** `src/menu/command_executor.py`

```
✅ SL System Changed
━━━━━━━━━━━━━━━━━━━
Old System: [SL-1]
New System: [SL-2] ✅
Description: Aggressive - Tighter SLs
━━━━━━━━━━━━━━━━━━━
Applied to: All future trades
```

---

### 8.2 Risk Tier Switched
**Trigger:** Active tier changed  
**File:** `src/clients/telegram_bot.py` Line 1037-1099

```
🔄 RISK TIER SWITCHED
━━━━━━━━━━━━━━━━━━━
Old Tier: $5000
New Tier: $10000 ✅

📊 UPDATED SETTINGS:
• Daily Loss Cap: $200
• Lifetime Cap: $1000
• Lot Size: 0.05

⚠️ All future trades use new settings
━━━━━━━━━━━━━━━━━━━
```

---

### 8.3 Logic Strategy Enabled/Disabled
**Trigger:** Strategy toggled  
**File:** `src/clients/telegram_bot.py` Lines 844-902

```
✅ LOGIC 1 TRADING ENABLED
All LOGIC1 signals will now be executed
```

```
⛔ LOGIC 2 TRADING DISABLED
LOGIC2 signals will be ignored
```

---

### 8.4 Simulation Mode Changed
**Trigger:** Simulation mode toggled  
**File:** `src/menu/command_executor.py`

```
🔄 SIMULATION MODE: [ON/OFF]
━━━━━━━━━━━━━━━━━━━
Status: [NO REAL TRADES / LIVE TRADING]
Orders: [Simulated / Real MT5]
━━━━━━━━━━━━━━━━━━━
```

---

## 9. ❌ ERROR & WARNING NOTIFICATIONS

### 9.1 MT5 Connection Error
**Trigger:** MT5 connection lost

```
❌ MT5 CONNECTION ERROR
Failed to connect to MetaTrader 5
Attempting reconnection...
```

---

### 9.2 Order Placement Failed
**Trigger:** Order rejected by broker

```
❌ ORDER PLACEMENT FAILED
━━━━━━━━━━━━━━━━━━━
Symbol: [XAUUSD]
Reason: [Insufficient margin]
Action: Trade cancelled
━━━━━━━━━━━━━━━━━━━
```

---

### 9.3 Price Fetch Error
**Trigger:** Failed to get current price  
**File:** `src/services/price_monitor_service.py`

```
⚠️ Failed to get current price for [XAUUSD]
Retrying in 5 seconds...
```

---

### 9.4 Configuration Error
**Trigger:** Invalid config detected

```
❌ CONFIGURATION ERROR
[Error Details]
Please check config.json and restart
```

---

### 9.5 Database Error
**Trigger:** Database operation failed

```
❌ DATABASE ERROR
Failed to save trade data
Check logs for details
```

---

## 10. 🔔 SYSTEM HEALTH & DIAGNOSTICS

### 10.1 Health Check OK
**Trigger:** `/health` command  
**File:** `src/menu/command_executor.py` Line 873

```
✅ SYSTEM HEALTH CHECK
━━━━━━━━━━━━━━━━━━━
🟢 MT5: Connected
🟢 Database: Operational
🟢 Telegram: Active
🟢 Memory: [75%] usage
━━━━━━━━━━━━━━━━━━━
All systems normal
```

---

### 10.2 Health Check Warning
**Trigger:** System issues detected

```
⚠️ SYSTEM HEALTH WARNING
━━━━━━━━━━━━━━━━━━━
🟡 MT5: Slow response
🟢 Database: OK
🟢 Telegram: OK
🔴 Memory: [95%] usage
━━━━━━━━━━━━━━━━━━━
Action: Monitor closely
```

---

## 11. 📊 ON-DEMAND DASHBOARDS

### 11.1 Interactive Dashboard
**Trigger:** `/dashboard` or Menu Button  
**File:** `src/clients/telegram_bot_fixed.py` Line 3695

```
🤖 ZEPIX TRADING BOT DASHBOARD
══════════════════════════════

📊 LIVE STATUS
• Bot: 🟢 RUNNING
• Balance: $10,500.00
• Open Trades: 2
• Live PnL: +$150.00

💰 TODAY'S PERFORMANCE
• Net PnL: +$320.50
• Trades Today: 5

🎯 TRADING SYSTEMS
• Dual Orders: 🟢 ON
• Profit Booking: 🟢 ON
• Re-entry: 🟢 ON

⚡ LIVE TRADES
• XAUUSD BUY | +$120.00 | SL: 2020.50 | TP: 2040.00
```

---

### 11.2 Autonomous Dashboard
**Trigger:** `/autonomous_status`  
**File:** `src/clients/telegram_bot_fixed.py` Line 3517

```
🤖 AUTONOMOUS DASHBOARD
━━━━━━━━━━━━━━━━━━━━━━
Status: ✅ RUNNING
Daily Recoveries: 2/10
Active Monitors: 1

🔍 Sub-Systems:
• Profit Protection: ✅ Active
• SL Optimizer: ✅ Active
• Recovery Windows: ✅ Active

⚙ Active Configuration:
• TP Continuation: ON
• SL Hunt Recovery: ON
• Exit Continuation: ON
```

---


## 📊 NOTIFICATION STATISTICS

### By Category:
```
📊 Trading: 6 notifications
⚡ Autonomous: 5 notifications
🔄 Re-Entry: 5 notifications
💎 Profit Booking: 2 notifications
🛡️ Risk & Safety: 5 notifications
📍 Trends: 3 notifications
⚙️ Config: 4 notifications
❌ Errors: 5 notifications
🔔 Health: 2 notifications
━━━━━━━━━━━━━━━━━━━
TOTAL: 45+ Notifications
```

### By Priority:
- 🔴 **Critical (Immediate):** 12 notifications (Errors, Risk Limits)
- 🟡 **Important (Trading):** 20 notifications (Entries, Exits, Recoveries)
- 🟢 **Informational:** 13 notifications (Status, Config Changes)

---

## 🎯 NOTIFICATION DELIVERY

**All notifications are sent via:**
1. Telegram messages to configured chat_id
2. Real-time (no delay)
3. Formatted with HTML parse mode
4. Include relevant emojis for quick visual identification
5. Structured with clear sections using ━━━ dividers

**Bot never spams:** Intelligent filtering prevents duplicate/redundant notifications

---

---

## 12. VOICE ALERT SYSTEM

**File:** `src/modules/voice_alert_system.py`

### Alert Priority Levels
**File:** `src/modules/voice_alert_system.py` Lines 40-45

| Priority | Channels | Description |
|----------|----------|-------------|
| CRITICAL | Windows Audio + Text + SMS | Emergency alerts requiring immediate attention |
| HIGH | Windows Audio + Text | Important trading events |
| MEDIUM | Windows Audio + Text | Standard notifications |
| LOW | Text only | Informational messages |

### Alert Channels
**File:** `src/modules/voice_alert_system.py` Lines 48-52

| Channel | Description |
|---------|-------------|
| WINDOWS_AUDIO | Direct speaker TTS (Text-to-Speech) |
| TEXT | Telegram text message |
| SMS | Fallback SMS notification |

### Voice Alert Triggers

#### 12.1 Trade Entry Voice Alert
**Trigger:** New trade opened  
**Priority:** HIGH

```
Voice: "New trade opened. [SYMBOL] [DIRECTION] at [PRICE]"
```

#### 12.2 Take Profit Voice Alert
**Trigger:** TP hit  
**Priority:** HIGH

```
Voice: "Take profit hit. [SYMBOL] profit [AMOUNT] dollars"
```

#### 12.3 Stop Loss Voice Alert
**Trigger:** SL hit  
**Priority:** CRITICAL

```
Voice: "Stop loss hit. [SYMBOL] loss [AMOUNT] dollars"
```

#### 12.4 Risk Limit Voice Alert
**Trigger:** Daily/Lifetime limit reached  
**Priority:** CRITICAL

```
Voice: "Warning. Daily loss limit reached. Trading paused."
```

#### 12.5 Recovery Voice Alert
**Trigger:** SL Hunt recovery triggered  
**Priority:** MEDIUM

```
Voice: "Recovery attempt started for [SYMBOL]"
```

---

## 13. MULTI-TELEGRAM ROUTING

**File:** `src/telegram/multi_telegram_manager.py`

### Message Types and Routing
**File:** `src/telegram/multi_telegram_manager.py` Lines 52-113

| Message Type | Target Bot | Method |
|--------------|------------|--------|
| `command` | Controller Bot | `route_message()` |
| `alert` | Notification Bot | `send_alert()` |
| `report` | Analytics Bot | `send_report()` |
| `broadcast` | All Bots | `send_admin_message()` |

### 13.1 Alert Routing
**File:** `src/telegram/multi_telegram_manager.py` Lines 105-109

```python
def send_alert(self, message: str, priority: str = "normal"):
    """Route alert to notification bot"""
    return self.route_message(message, "alert")
```

### 13.2 Report Routing
**File:** `src/telegram/multi_telegram_manager.py` Lines 109-113

```python
def send_report(self, message: str):
    """Route report to analytics bot"""
    return self.route_message(message, "report")
```

---

## 14. SESSION NOTIFICATIONS

**File:** `src/telegram/session_menu_handler.py`

### 14.1 Session Toggle Notification
**Trigger:** Session enabled/disabled  
**File:** `src/telegram/session_menu_handler.py` Lines 268-286

```
SESSION UPDATE
Session: [ASIAN/LONDON/NY/OVERLAP/LATE_NY]
Status: [ENABLED/DISABLED]
```

### 14.2 Symbol Toggle Notification
**Trigger:** Symbol enabled/disabled for session  
**File:** `src/telegram/session_menu_handler.py` Lines 217-240

```
SYMBOL UPDATE
Session: [SESSION_NAME]
Symbol: [XAUUSD]
Status: [ENABLED/DISABLED]
```

### 14.3 Time Adjustment Notification
**Trigger:** Session time adjusted  
**File:** `src/telegram/session_menu_handler.py` Lines 242-266

```
TIME ADJUSTMENT
Session: [SESSION_NAME]
[Start/End] Time: [+/-] 30 minutes
New Time: [HH:MM] UTC
```

### 14.4 Force Close Notification
**Trigger:** Force close toggled  
**File:** `src/telegram/session_menu_handler.py` Lines 286-307

```
FORCE CLOSE UPDATE
Session: [SESSION_NAME]
Force Close: [ENABLED/DISABLED]
```

---

## NOTIFICATION STATISTICS

### By Category:
```
Trading: 6 notifications
Autonomous: 5 notifications
Re-Entry: 5 notifications
Profit Booking: 2 notifications
Risk & Safety: 5 notifications
Trends: 3 notifications
Config: 4 notifications
Errors: 5 notifications
Health: 2 notifications
Voice Alerts: 5 notifications
Session: 4 notifications
Multi-Telegram: 4 notifications
TOTAL: 50+ Notifications
```

### By Priority:
- **CRITICAL (Immediate):** 15 notifications (Errors, Risk Limits, SL Hits)
- **HIGH (Trading):** 20 notifications (Entries, Exits, Recoveries)
- **MEDIUM (Standard):** 10 notifications (Config Changes, Updates)
- **LOW (Informational):** 5 notifications (Status, Reports)

---

## NOTIFICATION DELIVERY

**All notifications are sent via:**
1. Telegram messages to configured chat_id
2. Real-time (no delay)
3. Formatted with HTML parse mode
4. Include relevant emojis for quick visual identification
5. Structured with clear sections using dividers

**Voice Alerts (when enabled):**
1. Windows Audio TTS for CRITICAL/HIGH/MEDIUM priority
2. SMS fallback for CRITICAL priority
3. Text always sent regardless of priority

**Bot never spams:** Intelligent filtering prevents duplicate/redundant notifications

---

**Document Version:** 3.0
**Last Updated:** 14-Jan-2026
**Total Notifications Documented:** 50+
**Total Categories:** 14
**Completeness:** 100%

**Source Files Scanned:**
- `src/clients/telegram_bot_fixed.py` (5126 lines)
- `src/core/trading_engine.py` (2072 lines)
- `src/modules/voice_alert_system.py` (429 lines)
- `src/telegram/session_menu_handler.py` (384 lines)
- `src/telegram/multi_telegram_manager.py` (116 lines)
- `src/managers/autonomous_system_manager.py`
- `src/managers/profit_booking_manager.py`
- `src/managers/risk_manager.py`
- `src/services/price_monitor_service.py`

**Recent Changes:**
- **14-Jan-2026:** Complete rewrite based on deep code scan
- **14-Jan-2026:** Added Voice Alert System section (5 alert types)
- **14-Jan-2026:** Added Multi-Telegram Routing section
- **14-Jan-2026:** Added Session Notifications section (4 notification types)
- **14-Jan-2026:** Updated notification statistics
- **14-Jan-2026:** Added priority levels from voice_alert_system.py
