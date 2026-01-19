# 📨 NOTIFICATION SYSTEMS - COMPLETE DOCUMENTATION

**Generated:** January 19, 2026  
**Bot Version:** V5 Hybrid Plugin Architecture  
**Total Notification Types:** 50+  
**Systems:** Legacy | V5 Plugin | V6 Price Action

---

## 📊 NOTIFICATION SYSTEMS OVERVIEW

| System | Types | Status | Implementation |
|--------|-------|--------|----------------|
| 🔷 Legacy (V3) | 25 | ✅ Working | 100% |
| 🔶 V5 Plugin System | 15 | ✅ Working | 100% |
| 🎯 V6 Price Action | 10 | ❌ Missing | 0% |

---

## 🏗️ ARCHITECTURE

### Current 3-Bot Architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOTIFICATION FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌─────────────────────┐                   │
│  │ Trading      │───▶│ NotificationRouter  │                   │
│  │ Engine       │    │ (notification_      │                   │
│  └──────────────┘    │  router.py)         │                   │
│                      └─────────┬───────────┘                   │
│                                │                               │
│                    ┌───────────┼───────────┐                   │
│                    │           │           │                   │
│               ▼           ▼           ▼                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ CONTROLLER   │  │ NOTIFICATION │  │ ANALYTICS    │          │
│  │ BOT          │  │ BOT          │  │ BOT          │          │
│  │              │  │              │  │              │          │
│  │ • Commands   │  │ • Trades     │  │ • Reports    │          │
│  │ • Menus      │  │ • Alerts     │  │ • Summaries  │          │
│  │ • Settings   │  │ • Signals    │  │ • Analytics  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Notification Router Flow:

```python
# File: src/telegram/notification_router.py

class NotificationRouter:
    """Routes notifications to appropriate bot based on type"""
    
    def __init__(self, controller_bot, notification_bot, analytics_bot):
        self.controller = controller_bot
        self.notification = notification_bot
        self.analytics = analytics_bot
        
        # Routing rules
        self.routing_table = {
            # Controller Bot
            NotificationType.BOT_STARTED: self.controller,
            NotificationType.BOT_STOPPED: self.controller,
            NotificationType.EMERGENCY_STOP: self.controller,
            NotificationType.COMMAND_RESPONSE: self.controller,
            NotificationType.MENU_UPDATE: self.controller,
            
            # Notification Bot
            NotificationType.ENTRY: self.notification,
            NotificationType.EXIT: self.notification,
            NotificationType.TP_HIT: self.notification,
            NotificationType.SL_HIT: self.notification,
            NotificationType.PROFIT_BOOKING: self.notification,
            NotificationType.SL_MODIFIED: self.notification,
            NotificationType.BREAKEVEN: self.notification,
            NotificationType.SIGNAL_RECEIVED: self.notification,
            
            # Analytics Bot
            NotificationType.DAILY_SUMMARY: self.analytics,
            NotificationType.WEEKLY_SUMMARY: self.analytics,
            NotificationType.PERFORMANCE_REPORT: self.analytics,
            NotificationType.RISK_ALERT: self.analytics,
        }
```

---

## 🔷 SECTION 1: LEGACY NOTIFICATION TYPES (25 Types)

### Trading Notifications

| Type | Priority | Bot | Template | Status |
|------|----------|-----|----------|--------|
| `ENTRY` | HIGH | Notification | Trade Entry Card | ✅ |
| `EXIT` | HIGH | Notification | Trade Exit Card | ✅ |
| `TP_HIT` | MEDIUM | Notification | TP Hit Message | ✅ |
| `SL_HIT` | MEDIUM | Notification | SL Hit Message | ✅ |
| `BREAKEVEN` | LOW | Notification | BE Move Alert | ✅ |
| `SL_MODIFIED` | LOW | Notification | SL Change Alert | ✅ |
| `PARTIAL_CLOSE` | MEDIUM | Notification | Partial Close | ✅ |

### Signal Notifications

| Type | Priority | Bot | Template | Status |
|------|----------|-----|----------|--------|
| `SIGNAL_RECEIVED` | HIGH | Notification | Signal Card | ✅ |
| `SIGNAL_IGNORED` | INFO | Notification | Ignored Signal | ✅ |
| `SIGNAL_FILTERED` | INFO | Notification | Filtered Signal | ✅ |
| `TREND_CHANGED` | HIGH | Notification | Trend Alert | ✅ |
| `TREND_MANUAL_SET` | MEDIUM | Controller | Trend Set | ✅ |

### Re-entry Notifications

| Type | Priority | Bot | Template | Status |
|------|----------|-----|----------|--------|
| `TP_REENTRY_STARTED` | MEDIUM | Notification | Chain Start | ✅ |
| `TP_REENTRY_EXECUTED` | HIGH | Notification | Re-entry Execute | ✅ |
| `TP_REENTRY_COMPLETED` | MEDIUM | Notification | Chain Complete | ✅ |
| `SL_HUNT_STARTED` | MEDIUM | Notification | Hunt Start | ✅ |
| `SL_HUNT_RECOVERY` | HIGH | Notification | Recovery Execute | ✅ |
| `EXIT_CONTINUATION` | HIGH | Notification | Continuation | ✅ |

### System Notifications

| Type | Priority | Bot | Template | Status |
|------|----------|-----|----------|--------|
| `BOT_STARTED` | CRITICAL | Controller | Bot Start | ✅ |
| `BOT_STOPPED` | CRITICAL | Controller | Bot Stop | ✅ |
| `EMERGENCY_STOP` | CRITICAL | Controller | Emergency | ✅ |
| `MT5_CONNECTED` | HIGH | Controller | MT5 Connect | ✅ |
| `MT5_DISCONNECTED` | CRITICAL | Controller | MT5 Disconnect | ✅ |
| `MT5_RECONNECT` | HIGH | Controller | MT5 Reconnect | ✅ |

### Analytics Notifications

| Type | Priority | Bot | Template | Status |
|------|----------|-----|----------|--------|
| `DAILY_SUMMARY` | LOW | Analytics | Daily Report | ✅ |
| `WEEKLY_SUMMARY` | LOW | Analytics | Weekly Report | ⚠️ Partial |

---

## 🔶 SECTION 2: V5 PLUGIN NOTIFICATION TYPES (15 Types)

### Plugin Lifecycle Notifications

| Type | Priority | Bot | Template | Status |
|------|----------|-----|----------|--------|
| `PLUGIN_ENABLED` | MEDIUM | Controller | Plugin Enable | ✅ |
| `PLUGIN_DISABLED` | MEDIUM | Controller | Plugin Disable | ✅ |
| `PLUGIN_ERROR` | CRITICAL | Controller | Plugin Error | ✅ |
| `PLUGIN_CONFIG_CHANGED` | LOW | Controller | Config Change | ✅ |
| `PLUGIN_RELOADED` | MEDIUM | Controller | Plugin Reload | ✅ |

### V5 Trading Notifications (Enhanced)

| Type | Priority | Bot | Template | Status |
|------|----------|-----|----------|--------|
| `PLUGIN_SIGNAL` | HIGH | Notification | Plugin Signal | ✅ |
| `PLUGIN_ENTRY` | HIGH | Notification | Plugin Entry | ✅ |
| `PLUGIN_EXIT` | HIGH | Notification | Plugin Exit | ✅ |
| `PLUGIN_TP` | MEDIUM | Notification | Plugin TP | ✅ |
| `PLUGIN_SL` | MEDIUM | Notification | Plugin SL | ✅ |

### V5 Performance Notifications

| Type | Priority | Bot | Template | Status |
|------|----------|-----|----------|--------|
| `PLUGIN_PERFORMANCE` | LOW | Analytics | Plugin Stats | ✅ |
| `PLUGIN_DAILY_SUMMARY` | LOW | Analytics | Plugin Daily | ✅ |
| `PLUGIN_COMPARISON` | LOW | Analytics | Plugin Compare | ⚠️ Partial |

### V5 Service API Integration

```python
# File: src/core/plugin_system/service_api.py

class ServiceAPI:
    """API provided to plugins for Telegram notifications"""
    
    async def send_notification(
        self,
        notification_type: str,
        message: str,
        data: Dict[str, Any] = None,
        priority: str = "MEDIUM"
    ) -> bool:
        """Send notification via the unified notification system"""
        
        # Build notification payload
        payload = {
            "type": notification_type,
            "plugin_id": self.plugin_id,
            "message": message,
            "data": data or {},
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        
        # Route to NotificationRouter
        return await self.notification_router.route_notification(payload)
```

---

## 🎯 SECTION 3: V6 PRICE ACTION NOTIFICATIONS (❌ MISSING)

### Required V6 Notification Types (10 Types)

| Type | Priority | Bot | Template | Status |
|------|----------|-----|----------|--------|
| `V6_ENTRY_15M` | HIGH | Notification | V6 15M Entry | ❌ Missing |
| `V6_ENTRY_30M` | HIGH | Notification | V6 30M Entry | ❌ Missing |
| `V6_ENTRY_1H` | HIGH | Notification | V6 1H Entry | ❌ Missing |
| `V6_ENTRY_4H` | HIGH | Notification | V6 4H Entry | ❌ Missing |
| `V6_EXIT` | HIGH | Notification | V6 Exit | ❌ Missing |
| `V6_TP_HIT` | MEDIUM | Notification | V6 TP Hit | ❌ Missing |
| `V6_SL_HIT` | MEDIUM | Notification | V6 SL Hit | ❌ Missing |
| `V6_TIMEFRAME_ENABLED` | MEDIUM | Controller | V6 TF Enable | ❌ Missing |
| `V6_TIMEFRAME_DISABLED` | MEDIUM | Controller | V6 TF Disable | ❌ Missing |
| `V6_DAILY_SUMMARY` | LOW | Analytics | V6 Daily | ❌ Missing |

### V6 Notification Templates (TO IMPLEMENT)

```
━━━━━━━━━━━━━━━━━━━━━━━━
🎯 V6 ENTRY (15M)
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: EURUSD
Direction: 📈 BUY
Timeframe: ⏱️ 15M

Entry: 1.08500
SL: 1.08400 (10 pips)
TP: 1.08700 (20 pips)

Risk: 0.02 lot ($10)
R:R Ratio: 1:2

Logic: V6 Price Action
Time: 14:30 UTC

━━━━━━━━━━━━━━━━━━━━━━━━
```

### V6 Timeframe Identification:

```
CRITICAL FEATURE: Users need to know WHICH V6 timeframe generated a trade

Current Problem:
- V6 trades show as generic "v6_price_action"
- User cannot distinguish between 15M/30M/1H/4H trades
- No timeframe context in notifications

Solution:
- Include timeframe in all V6 notifications
- Use timeframe-specific emojis:
  - 15M: ⏱️15
  - 30M: ⏱️30
  - 1H: 🕐1H
  - 4H: 🕓4H
```

---

## 📱 SECTION 4: NOTIFICATION TEMPLATES

### Template Structure:

```python
# File: src/telegram/notification_templates.py

class NotificationTemplates:
    """All notification message templates"""
    
    # Trading Templates
    ENTRY_TEMPLATE = """
🟢 TRADE ENTRY
━━━━━━━━━━━━━━━━━━━━━━

Symbol: {symbol}
Direction: {direction_emoji} {direction}
{plugin_badge}

📍 Entry: {entry_price}
🛑 SL: {sl_price} ({sl_pips} pips)
🎯 TP: {tp_price} ({tp_pips} pips)

💰 Risk: {lot_size} lot (${risk_amount})
📊 R:R: 1:{risk_reward}

⏰ Time: {timestamp}
"""

    EXIT_TEMPLATE = """
{result_emoji} TRADE EXIT
━━━━━━━━━━━━━━━━━━━━━━

Symbol: {symbol}
{plugin_badge}

📍 Entry: {entry_price}
📍 Exit: {exit_price}

💰 Result: {result_emoji} {pnl_sign}${pnl:.2f}
📊 Pips: {pips_sign}{pips:.1f}
⏱️ Duration: {duration}

📈 Daily PnL: ${daily_pnl:.2f}
"""

    # V6-Specific Templates (NEW)
    V6_ENTRY_TEMPLATE = """
🎯 V6 ENTRY ({timeframe})
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: {symbol}
Direction: {direction_emoji} {direction}
Timeframe: {timeframe_emoji} {timeframe}

📍 Entry: {entry_price}
🛑 SL: {sl_price} ({sl_pips} pips)
🎯 TP: {tp_price} ({tp_pips} pips)

💰 Risk: {lot_size} lot
📊 R:R: 1:{risk_reward}

🔷 Logic: V6 Price Action
⏰ Time: {timestamp}
"""

    V6_EXIT_TEMPLATE = """
{result_emoji} V6 EXIT ({timeframe})
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: {symbol}
Timeframe: {timeframe_emoji} {timeframe}

📍 Entry: {entry_price}
📍 Exit: {exit_price}

💰 Result: {result_emoji} {pnl_sign}${pnl:.2f}
📊 Pips: {pips_sign}{pips:.1f}

🔷 V6 Stats:
  • Today: {v6_today_count} trades, ${v6_today_pnl:.2f}
"""
```

---

## 🔗 SECTION 5: COMPLETE WIRING INSTRUCTIONS

### Step 1: Add V6 NotificationTypes

```python
# File: src/telegram/notification_router.py

# Add to NotificationType enum:
class NotificationType(Enum):
    # ... existing types ...
    
    # V6 Price Action Types (NEW)
    V6_ENTRY_15M = "v6_entry_15m"
    V6_ENTRY_30M = "v6_entry_30m"
    V6_ENTRY_1H = "v6_entry_1h"
    V6_ENTRY_4H = "v6_entry_4h"
    V6_EXIT = "v6_exit"
    V6_TP_HIT = "v6_tp_hit"
    V6_SL_HIT = "v6_sl_hit"
    V6_TIMEFRAME_ENABLED = "v6_timeframe_enabled"
    V6_TIMEFRAME_DISABLED = "v6_timeframe_disabled"
    V6_DAILY_SUMMARY = "v6_daily_summary"
```

### Step 2: Add V6 Routing Rules

```python
# File: src/telegram/notification_router.py

# Add to routing_table in __init__:
self.routing_table.update({
    # V6 to Notification Bot
    NotificationType.V6_ENTRY_15M: self.notification,
    NotificationType.V6_ENTRY_30M: self.notification,
    NotificationType.V6_ENTRY_1H: self.notification,
    NotificationType.V6_ENTRY_4H: self.notification,
    NotificationType.V6_EXIT: self.notification,
    NotificationType.V6_TP_HIT: self.notification,
    NotificationType.V6_SL_HIT: self.notification,
    
    # V6 to Controller Bot
    NotificationType.V6_TIMEFRAME_ENABLED: self.controller,
    NotificationType.V6_TIMEFRAME_DISABLED: self.controller,
    
    # V6 to Analytics Bot
    NotificationType.V6_DAILY_SUMMARY: self.analytics,
})
```

### Step 3: Add V6 Templates

```python
# File: src/telegram/notification_templates.py

# Add V6 templates:
V6_TEMPLATES = {
    "v6_entry": V6_ENTRY_TEMPLATE,
    "v6_exit": V6_EXIT_TEMPLATE,
    "v6_tp_hit": V6_TP_HIT_TEMPLATE,
    "v6_sl_hit": V6_SL_HIT_TEMPLATE,
    "v6_timeframe_enabled": V6_TF_ENABLED_TEMPLATE,
    "v6_timeframe_disabled": V6_TF_DISABLED_TEMPLATE,
    "v6_daily_summary": V6_DAILY_SUMMARY_TEMPLATE,
}
```

### Step 4: Wire V6 Plugin to Notifications

```python
# File: src/logic_plugins/v6_price_action_15m/plugin.py

class V6PriceAction15MPlugin:
    """V6 Price Action 15M Plugin with Telegram notifications"""
    
    async def on_trade_entry(self, trade: Trade):
        """Called when trade is placed"""
        
        # Send V6 entry notification
        await self.service_api.send_notification(
            notification_type="v6_entry_15m",
            message=f"V6 15M Entry: {trade.symbol} {trade.direction}",
            data={
                "symbol": trade.symbol,
                "direction": trade.direction,
                "entry_price": trade.entry_price,
                "sl": trade.sl,
                "tp": trade.tp,
                "lot_size": trade.lot_size,
                "timeframe": "15M",
            },
            priority="HIGH"
        )
    
    async def on_trade_exit(self, trade: Trade, result: TradeResult):
        """Called when trade is closed"""
        
        # Determine notification type based on exit reason
        if result.exit_reason == "tp_hit":
            notif_type = "v6_tp_hit"
        elif result.exit_reason == "sl_hit":
            notif_type = "v6_sl_hit"
        else:
            notif_type = "v6_exit"
        
        await self.service_api.send_notification(
            notification_type=notif_type,
            message=f"V6 15M Exit: {trade.symbol} {result.pnl:+.2f}",
            data={
                "symbol": trade.symbol,
                "entry_price": trade.entry_price,
                "exit_price": result.exit_price,
                "pnl": result.pnl,
                "pips": result.pips,
                "timeframe": "15M",
            },
            priority="HIGH" if abs(result.pnl) > 50 else "MEDIUM"
        )
```

### Step 5: Create UnifiedNotificationRouter Config

```python
# File: src/telegram/unified_notification_router.py

# Add V6 type configurations:
V6_TYPE_CONFIGS = {
    "v6_entry_15m": {
        "bot": "notification",
        "priority": "HIGH",
        "template": "v6_entry",
        "sound": True,
        "badge": "🎯 V6 15M",
    },
    "v6_entry_30m": {
        "bot": "notification",
        "priority": "HIGH",
        "template": "v6_entry",
        "sound": True,
        "badge": "🎯 V6 30M",
    },
    "v6_entry_1h": {
        "bot": "notification",
        "priority": "HIGH",
        "template": "v6_entry",
        "sound": True,
        "badge": "🎯 V6 1H",
    },
    "v6_entry_4h": {
        "bot": "notification",
        "priority": "HIGH",
        "template": "v6_entry",
        "sound": True,
        "badge": "🎯 V6 4H",
    },
    # ... other V6 types
}
```

---

## 📊 SECTION 6: NOTIFICATION PRIORITY SYSTEM

### Priority Levels:

| Priority | Use Case | Sound | Display |
|----------|----------|-------|---------|
| `CRITICAL` | Emergency, MT5 disconnect | 🔔 Alert | Immediate |
| `HIGH` | Trade entry/exit, signals | 🔔 Sound | Normal |
| `MEDIUM` | TP/SL hit, config changes | None | Normal |
| `LOW` | Stats, info, non-urgent | None | Silent |
| `INFO` | Debug, verbose | None | Silent |

### Priority Configuration:

```python
# File: src/telegram/notification_router.py

PRIORITY_CONFIG = {
    "CRITICAL": {
        "disable_notification": False,  # Force sound
        "protect_content": False,
        "delay": 0,  # Send immediately
    },
    "HIGH": {
        "disable_notification": False,
        "protect_content": False,
        "delay": 0,
    },
    "MEDIUM": {
        "disable_notification": True,  # No sound
        "protect_content": False,
        "delay": 0,
    },
    "LOW": {
        "disable_notification": True,
        "protect_content": False,
        "delay": 1,  # Slight delay to batch
    },
    "INFO": {
        "disable_notification": True,
        "protect_content": False,
        "delay": 5,  # Can be batched
    },
}
```

---

## 🎨 SECTION 7: ENHANCED VISUAL NOTIFICATIONS (Telegram Capabilities)

### Rich Notification Features (Currently NOT Used):

| Feature | Description | Current Use | Potential |
|---------|-------------|-------------|-----------|
| **Inline Keyboards** | Interactive buttons | ⚠️ Partial | ✅ High |
| **Progress Bars** | Visual progress | ❌ None | ✅ High |
| **Emojis** | Visual indicators | ✅ Basic | ✅ More |
| **Markdown** | Bold, italic, code | ✅ Some | ✅ More |
| **HTML** | Tables, structured | ❌ None | ✅ High |
| **Photo Messages** | Charts, screenshots | ❌ None | ⚠️ Medium |
| **Chat Actions** | "typing..." indicator | ❌ None | ✅ High |

### Enhanced Trade Entry Notification (PROPOSED):

```python
# Current (Basic):
"""
🟢 Entry: EURUSD BUY @ 1.08500
SL: 1.08400, TP: 1.08700
"""

# Enhanced (Rich):
async def send_rich_entry_notification(self, trade: Trade):
    """Send enhanced entry notification with inline keyboard"""
    
    # Build message with rich formatting
    message = f"""
🟢 <b>NEW TRADE ENTRY</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Symbol:</b> {trade.symbol}
<b>Direction:</b> {'📈 BUY' if trade.direction == 'BUY' else '📉 SELL'}
<b>Plugin:</b> {self.get_plugin_badge(trade.plugin_id)}

📍 <b>Entry:</b> <code>{trade.entry_price}</code>
🛑 <b>SL:</b> <code>{trade.sl}</code> ({trade.sl_pips:.1f} pips)
🎯 <b>TP:</b> <code>{trade.tp}</code> ({trade.tp_pips:.1f} pips)

💰 <b>Risk:</b> {trade.lot_size} lot (${trade.risk_amount:.2f})
📊 <b>R:R:</b> 1:{trade.risk_reward:.1f}

━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    # Inline keyboard for quick actions
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🛑 Close Trade", "callback_data": f"close_trade_{trade.ticket}"},
                {"text": "📊 Details", "callback_data": f"trade_details_{trade.ticket}"}
            ],
            [
                {"text": "🎯 Modify TP", "callback_data": f"modify_tp_{trade.ticket}"},
                {"text": "🛑 Modify SL", "callback_data": f"modify_sl_{trade.ticket}"}
            ]
        ]
    }
    
    await self.bot.send_message(
        chat_id=self.notification_chat_id,
        text=message,
        parse_mode="HTML",
        reply_markup=keyboard,
        disable_notification=False  # Sound for entries
    )
```

### Progress Bars for Notifications:

```python
def create_progress_bar(current: float, target: float, width: int = 10) -> str:
    """Create visual progress bar using Unicode characters"""
    percentage = min(current / target, 1.0) if target > 0 else 0
    filled = int(percentage * width)
    empty = width - filled
    
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {percentage*100:.1f}%"

# Usage in TP progress notification:
"""
🎯 TP PROGRESS
━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: EURUSD
Current: 1.08650
Target TP: 1.08700

Progress: [████████░░] 80.0%
Pips: +16.0 / +20.0

━━━━━━━━━━━━━━━━━━━━━━━━
"""
```

---

## ✅ IMPLEMENTATION CHECKLIST

### V6 Notifications (CRITICAL):
- [ ] Add 10 V6 NotificationType enums
- [ ] Add V6 routing rules to routing_table
- [ ] Create V6 notification templates
- [ ] Wire V6 plugins to send notifications
- [ ] Add timeframe badges to V6 messages
- [ ] Test all V6 notification flows

### Enhanced Notifications (HIGH):
- [ ] Add inline keyboards to trade notifications
- [ ] Implement progress bar helper
- [ ] Add chat actions ("typing...")
- [ ] Improve message formatting (HTML/Markdown)
- [ ] Add quick action buttons

### Analytics Notifications (MEDIUM):
- [ ] Implement daily summary for V6
- [ ] Add plugin comparison notification
- [ ] Create weekly summary template
- [ ] Add export notification

---

## 🔧 FILES TO MODIFY

| File | Changes | Priority |
|------|---------|----------|
| `src/telegram/notification_router.py` | Add V6 types + routing | Critical |
| `src/telegram/notification_templates.py` | Add V6 templates | Critical |
| `src/telegram/unified_notification_router.py` | Add V6 configs | Critical |
| `src/logic_plugins/v6_*/plugin.py` | Wire notifications | Critical |
| `src/telegram/notification_bot.py` | Enhanced formatting | High |
| `src/clients/telegram_bot.py` | Callback handlers for quick actions | High |

---

**END OF NOTIFICATION SYSTEMS DOCUMENTATION**

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