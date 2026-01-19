# PHASE 1: V6 NOTIFICATION SYSTEM

**Phase:** 1 of 6  
**Priority:** CRITICAL  
**Timeline:** Week 1-2 (16 hours)  
**Status:** Planning  
**Dependencies:** None

---

## OBJECTIVE

Implement V6-specific notifications that allow users to:
1. Identify which V6 timeframe (15M/30M/1H/4H) triggered a trade
2. Distinguish V6 trades from V3 trades visually
3. See Price Action pattern details
4. Receive Trend Pulse detection alerts
5. Track shadow mode trades separately

---

## CURRENT STATE

### What Exists ✅

**File:** `Trading_Bot/src/telegram/notification_bot.py` (370 lines)

**Implemented Methods:**
1. `send_entry_alert(trade_data)` - Generic entry notification
2. `send_exit_alert(trade_data)` - Generic exit notification
3. `send_profit_booking_alert(booking_data)` - Profit booking notification
4. `send_error_alert(error_data)` - Error notification
5. `send_daily_summary(summary_data)` - Daily summary
6. `send_notification(type, message)` - Async router handler

**Current Entry Alert Format:**
```
🔔 NEW TRADE ENTRY

Plugin: V6 Price Action
Symbol: EURUSD
Direction: BUY
Entry: 1.08450

Order A:
├─ Lot: 0.01
├─ SL: 1.08350 (-10.0 pips)
└─ TP: 1.08650 (+20.0 pips)

Signal: BULLISH_REVERSAL
Timeframe: 1H
Logic: LOGIC1
```

**Problems with Current Format:**
- ❌ Timeframe shows "1H" but doesn't indicate it's V6-specific
- ❌ Signal type "BULLISH_REVERSAL" doesn't show Price Action pattern
- ❌ No indication of which V6 plugin (v6_price_action_1h)
- ❌ No Trend Pulse information
- ❌ No shadow mode flag
- ❌ Looks identical to V3 alerts

### What's Missing ❌

**V6-Specific Notifications:**
1. ✗ V6 entry alert with timeframe identification
2. ✗ V6 exit alert with pattern details
3. ✗ Trend Pulse detection notification
4. ✗ Shadow mode trade alerts
5. ✗ Price Action pattern breakdown
6. ✗ Higher timeframe trend context
7. ✗ V6 vs V3 visual distinction

---

## PROPOSED SOLUTION

### 1. V6 Entry Alert Enhancement

**New Method:** `send_v6_entry_alert(trade_data)`

**Required Fields in trade_data:**
```python
{
    'plugin_name': 'v6_price_action_1h',  # Identifies V6 plugin
    'timeframe': '1H',  # 15M, 30M, 1H, 4H
    'symbol': 'EURUSD',
    'direction': 'BUY',
    'entry_price': 1.08450,
    
    # V6-Specific Fields:
    'signal_type': 'TREND_PULSE',  # New V6 signal types
    'price_action_pattern': 'BULLISH_ENGULFING',  # Pattern name
    'trend_pulse_strength': 8,  # 1-10 scale
    'higher_tf_trend': 'BULLISH',  # From 4H trend
    'is_shadow_mode': False,  # Shadow flag
    
    # Standard Fields:
    'order_a_lot': 0.01,
    'order_a_sl': 1.08350,
    'order_a_tp': 1.08650,
    'order_b_lot': 0.01,  # If dual order
    'order_b_sl': 1.08300,
    'order_b_tp': 1.08750,
    
    # Metadata:
    'ticket_a': 123456,
    'ticket_b': 123457,
    'timestamp': '2026-01-19 14:30:00'
}
```

**Proposed Alert Format:**
```
🟢 V6 PRICE ACTION ENTRY [1H]

📍 Symbol: EURUSD
📊 Direction: BUY @ 1.08450
⏰ Time: 14:30:00 UTC

🎯 SIGNAL ANALYSIS
├─ Pattern: Bullish Engulfing
├─ Trend Pulse: ████████░░ (8/10)
├─ Higher TF: 🟢 Bullish
└─ Trigger: TREND_PULSE

💼 ORDER DETAILS
┌─ Order A (Main)
│  ├─ Lot: 0.01
│  ├─ SL: 1.08350 (-10.0 pips)
│  └─ TP: 1.08650 (+20.0 pips)
└─ Order B (Runner)
   ├─ Lot: 0.01
   ├─ SL: 1.08300 (-15.0 pips)
   └─ TP: 1.08750 (+30.0 pips)

🎫 Tickets: #123456 | #123457
🔖 Plugin: V6-1H | Logic: Price Action
```

**Visual Distinction from V3:**
- V6: 🟢 Green circle icon
- V3: 🔵 Blue circle icon
- Timeframe in header: `[1H]`, `[15M]`, etc.
- Pattern details (V3 doesn't have)
- "V6-1H" plugin tag

---

### 2. V6 Exit Alert Enhancement

**New Method:** `send_v6_exit_alert(trade_data)`

**Required Fields in trade_data:**
```python
{
    'plugin_name': 'v6_price_action_1h',
    'timeframe': '1H',
    'symbol': 'EURUSD',
    'direction': 'BUY',
    'entry_price': 1.08450,
    'exit_price': 1.08650,
    'exit_type': 'TP_HIT',  # TP_HIT, SL_HIT, MANUAL, REVERSAL
    
    # V6-Specific:
    'entry_pattern': 'BULLISH_ENGULFING',
    'exit_reason_detail': 'Target reached, trend pulse weakening',
    'duration_minutes': 45,
    'is_shadow_mode': False,
    
    # P&L:
    'pnl_usd': 20.00,
    'pnl_pips': 20.0,
    'pnl_percentage': 2.0,
    
    # Orders:
    'orders': [
        {'ticket': 123456, 'lot': 0.01, 'exit_price': 1.08650, 'pnl': 20.00},
        {'ticket': 123457, 'lot': 0.01, 'exit_price': 1.08650, 'pnl': 20.00}
    ]
}
```

**Proposed Alert Format:**
```
🟢 V6 PRICE ACTION EXIT [1H]

📍 Symbol: EURUSD | ✅ TP HIT
📊 Direction: BUY
🎯 Entry Pattern: Bullish Engulfing

💰 PROFIT & LOSS
├─ P&L: +$40.00
├─ Pips: +20.0 pips
├─ ROI: +2.0%
└─ Duration: 45 minutes

📈 TRADE SUMMARY
├─ Entry: 1.08450
├─ Exit: 1.08650
└─ Reason: Target reached, trend pulse weakening

📋 CLOSED ORDERS
├─ #123456: 0.01 lots → +$20.00
└─ #123457: 0.01 lots → +$20.00

🔖 Plugin: V6-1H | Total: +40.0 pips
```

**Exit Type Emojis:**
- TP Hit: ✅
- SL Hit: ❌
- Manual Exit: 👤
- Reversal Exit: 🔄

---

### 3. Trend Pulse Detection Alert

**New Method:** `send_trend_pulse_alert(pulse_data)`

**When to Send:**
- When Trend Pulse Manager detects pulse signal
- Before trade entry (as confirmation)
- Can be standalone if entry conditions not met

**Required Fields in pulse_data:**
```python
{
    'plugin_name': 'v6_price_action_1h',
    'timeframe': '1H',
    'symbol': 'EURUSD',
    'trend_direction': 'BULLISH',  # BULLISH, BEARISH, NEUTRAL
    'pulse_strength': 8,  # 1-10
    'higher_tf_trend': 'BULLISH',
    'higher_tf': '4H',
    'confirmation_level': 'HIGH',  # LOW, MEDIUM, HIGH
    'price_action_aligned': True,
    'timestamp': '2026-01-19 14:25:00'
}
```

**Proposed Alert Format:**
```
🌊 TREND PULSE DETECTED [1H]

📍 Symbol: EURUSD
📊 Direction: 🟢 BULLISH

🎯 PULSE ANALYSIS
├─ Strength: ████████░░ (8/10)
├─ Confirmation: 🔴 HIGH
├─ Higher TF (4H): 🟢 Aligned
└─ Price Action: ✅ Confirmed

⏰ Detected: 14:25:00 UTC
🔖 Plugin: V6-1H

💡 ACTION: Watch for entry setup
```

**Strength Bar:**
- 1-3: ███░░░░░░░ (Weak)
- 4-6: ██████░░░░ (Medium)
- 7-10: █████████░ (Strong)

**Confirmation Level Colors:**
- LOW: 🟡 Yellow
- MEDIUM: 🟠 Orange
- HIGH: 🔴 Red

---

### 4. Shadow Mode Trade Alert

**New Method:** `send_shadow_trade_alert(trade_data)`

**When to Send:**
- When V6 plugin is in shadow mode
- Trade would have been placed in live mode
- Uses same data as entry alert

**Proposed Alert Format:**
```
👻 SHADOW MODE TRADE [1H]

⚠️ THIS IS A SIMULATED TRADE - NO REAL ORDER PLACED

📍 Symbol: EURUSD
📊 Direction: BUY @ 1.08450
⏰ Time: 14:30:00 UTC

🎯 SIGNAL ANALYSIS
├─ Pattern: Bullish Engulfing
├─ Trend Pulse: ████████░░ (8/10)
└─ Higher TF: 🟢 Bullish

💼 WOULD-BE ORDER DETAILS
├─ Order A: 0.01 lots
│  ├─ SL: 1.08350 (-10.0 pips)
│  └─ TP: 1.08650 (+20.0 pips)
└─ Order B: 0.01 lots
   ├─ SL: 1.08300 (-15.0 pips)
   └─ TP: 1.08750 (+30.0 pips)

🔖 Plugin: V6-1H | Mode: SHADOW
📊 Track Performance: /shadow
```

**Visual Distinction:**
- 👻 Ghost icon for shadow trades
- "SHADOW MODE" in header
- Yellow warning banner
- "WOULD-BE ORDER" instead of "ORDER"
- Link to `/shadow` command for comparison

---

### 5. Price Action Pattern Notification

**New Method:** `send_price_action_pattern_alert(pattern_data)`

**When to Send:**
- When significant Price Action pattern detected
- May or may not lead to trade entry
- Educational/informational alert

**Required Fields in pattern_data:**
```python
{
    'plugin_name': 'v6_price_action_1h',
    'timeframe': '1H',
    'symbol': 'EURUSD',
    'pattern_name': 'BULLISH_ENGULFING',
    'pattern_quality': 'HIGH',  # LOW, MEDIUM, HIGH
    'candles_involved': 2,
    'price_range': {'high': 1.08500, 'low': 1.08400},
    'trend_alignment': True,
    'entry_potential': 'STRONG',  # WEAK, MODERATE, STRONG
    'timestamp': '2026-01-19 14:20:00'
}
```

**Proposed Alert Format:**
```
📊 PRICE ACTION PATTERN [1H]

📍 Symbol: EURUSD
🎨 Pattern: Bullish Engulfing
⭐ Quality: 🔴 HIGH

📈 PATTERN DETAILS
├─ Candles: 2 (14:00 - 15:00)
├─ Range: 1.08400 - 1.08500
├─ Trend Aligned: ✅ Yes
└─ Entry Potential: 🟢 STRONG

⏰ Detected: 14:20:00 UTC
🔖 Plugin: V6-1H

💡 Watch for Trend Pulse confirmation
```

---

## IMPLEMENTATION DETAILS

### File Structure

**Primary File:** `Trading_Bot/src/telegram/notification_bot.py`

**New Methods to Add:**
```python
class NotificationBot(BaseTelegramBot):
    # ... existing methods ...
    
    # NEW V6 METHODS:
    def send_v6_entry_alert(self, trade_data: Dict) -> Optional[int]:
        """Send V6-specific entry notification"""
        pass
    
    def send_v6_exit_alert(self, trade_data: Dict) -> Optional[int]:
        """Send V6-specific exit notification"""
        pass
    
    def send_trend_pulse_alert(self, pulse_data: Dict) -> Optional[int]:
        """Send Trend Pulse detection notification"""
        pass
    
    def send_shadow_trade_alert(self, trade_data: Dict) -> Optional[int]:
        """Send shadow mode trade notification"""
        pass
    
    def send_price_action_pattern_alert(self, pattern_data: Dict) -> Optional[int]:
        """Send Price Action pattern notification"""
        pass
    
    # HELPER METHODS:
    def _format_v6_entry_message(self, trade_data: Dict) -> str:
        """Format V6 entry alert message"""
        pass
    
    def _format_v6_exit_message(self, trade_data: Dict) -> str:
        """Format V6 exit alert message"""
        pass
    
    def _format_trend_pulse_message(self, pulse_data: Dict) -> str:
        """Format Trend Pulse alert message"""
        pass
    
    def _format_shadow_trade_message(self, trade_data: Dict) -> str:
        """Format shadow mode trade message"""
        pass
    
    def _format_price_action_pattern_message(self, pattern_data: Dict) -> str:
        """Format Price Action pattern message"""
        pass
    
    def _get_plugin_emoji(self, plugin_name: str) -> str:
        """Get emoji for plugin (V3: 🔵, V6: 🟢)"""
        pass
    
    def _get_timeframe_tag(self, timeframe: str) -> str:
        """Get formatted timeframe tag [15M], [1H], etc."""
        pass
    
    def _format_trend_pulse_bar(self, strength: int) -> str:
        """Format visual strength bar (█████░░░░░)"""
        pass
    
    def _get_confirmation_emoji(self, level: str) -> str:
        """Get confirmation level emoji (🟡🟠🔴)"""
        pass
```

### Message Formatting Guidelines

**HTML Formatting:**
- Use `<b>` for headers
- Use `<code>` for numeric values
- Use tree characters: `├─`, `└─`, `│`, `┌─`
- Emojis before section headers

**Emoji Conventions:**
- V3 Plugin: 🔵 Blue circle
- V6 Plugin: 🟢 Green circle
- Bullish: 🟢 Green
- Bearish: 🔴 Red
- Neutral: 🟡 Yellow
- TP Hit: ✅ Green check
- SL Hit: ❌ Red X
- Manual Exit: 👤 User icon
- Shadow Mode: 👻 Ghost
- Trend Pulse: 🌊 Wave
- Pattern: 📊 Chart
- Alert: 🔔 Bell
- Warning: ⚠️ Warning
- Analysis: 🎯 Target

**Consistency Rules:**
1. Always include plugin identification
2. Always include timeframe in header
3. Always include timestamp
4. Use consistent section headers
5. Align numeric values
6. Use tree structure for nested info

### Notification Router Integration

**File:** `Trading_Bot/src/telegram/notification_router.py`

**Required Changes:**
```python
# Add V6 notification type routing:

NOTIFICATION_TYPE_MAP = {
    # ... existing V3 mappings ...
    
    # V6 MAPPINGS:
    'v6_trade_opened': NotificationBot.send_v6_entry_alert,
    'v6_trade_closed': NotificationBot.send_v6_exit_alert,
    'v6_trend_pulse': NotificationBot.send_trend_pulse_alert,
    'v6_shadow_trade': NotificationBot.send_shadow_trade_alert,
    'v6_price_action_pattern': NotificationBot.send_price_action_pattern_alert,
}

# Auto-detect V6 vs V3 from trade_data:
def route_notification(notification_type, data):
    plugin_name = data.get('plugin_name', '')
    
    # V6 Detection:
    if 'v6_price_action' in plugin_name:
        if notification_type == 'trade_opened':
            return 'v6_trade_opened'
        elif notification_type == 'trade_closed':
            return 'v6_trade_closed'
    
    # V3 Detection:
    elif 'v3_combined' in plugin_name:
        return notification_type  # Use standard V3 notifications
    
    # Fallback:
    return notification_type
```

---

## TESTING PLAN

### Unit Tests

**Test File:** `tests/telegram/test_notification_bot_v6.py`

**Test Cases:**
1. `test_send_v6_entry_alert_15m()` - V6 15M entry alert
2. `test_send_v6_entry_alert_1h()` - V6 1H entry alert
3. `test_send_v6_exit_alert_tp_hit()` - V6 TP hit exit
4. `test_send_v6_exit_alert_sl_hit()` - V6 SL hit exit
5. `test_send_trend_pulse_alert_high()` - High strength pulse
6. `test_send_trend_pulse_alert_low()` - Low strength pulse
7. `test_send_shadow_trade_alert()` - Shadow mode trade
8. `test_send_price_action_pattern_alert()` - Pattern detection
9. `test_format_trend_pulse_bar()` - Visual strength bar
10. `test_get_plugin_emoji()` - V3 vs V6 emoji
11. `test_notification_router_v6_detection()` - Auto-routing

**Mocks Required:**
- Mock Telegram API
- Mock trade_data dictionaries
- Mock notification router

### Integration Tests

**Test Scenarios:**
1. V6 15M plugin sends entry → Correct notification format
2. V6 1H plugin sends exit → Correct P&L display
3. Trend Pulse Manager triggers alert → User receives pulse notification
4. Shadow mode enabled → Ghost icon trades sent
5. Both V3 and V6 active → Distinct notifications for each

**End-to-End Test:**
```
1. Enable V6 1H plugin
2. Send mock Pine Script V6 alert
3. Verify Trend Pulse notification received
4. Verify V6 entry alert received
5. Send mock exit signal
6. Verify V6 exit alert received
7. Check all fields are correct
8. Verify visual distinction from V3
```

### Manual Testing Checklist

- [ ] V6 entry alert shows timeframe tag
- [ ] V6 entry alert shows Price Action pattern
- [ ] V6 entry alert shows Trend Pulse strength bar
- [ ] V6 exit alert shows exit reason detail
- [ ] Trend Pulse alert shows higher TF alignment
- [ ] Shadow mode alert has ghost icon
- [ ] Shadow mode alert has warning banner
- [ ] All V6 alerts use green circle (🟢)
- [ ] All V3 alerts use blue circle (🔵)
- [ ] Notification router auto-detects V6 vs V3

---

## EDGE CASES & ERROR HANDLING

### Edge Case 1: Missing V6-Specific Fields
**Scenario:** `price_action_pattern` field missing from trade_data  
**Handling:** Fall back to generic "Price Action Signal"  
**User Impact:** Still receives notification, less detail

### Edge Case 2: Invalid Timeframe
**Scenario:** Timeframe is "2H" (not in 15M/30M/1H/4H)  
**Handling:** Use provided timeframe, log warning  
**User Impact:** Notification shows unusual timeframe

### Edge Case 3: Trend Pulse Strength Out of Range
**Scenario:** `pulse_strength` is 15 (should be 1-10)  
**Handling:** Clamp to 10, log error  
**User Impact:** Shows max strength (10)

### Edge Case 4: Shadow Mode Flag Missing
**Scenario:** `is_shadow_mode` field not in trade_data  
**Handling:** Default to False (live mode)  
**User Impact:** Might send live notification for shadow trade

### Edge Case 5: Both Orders Missing
**Scenario:** No `order_a` or `order_b` data  
**Handling:** Send minimal notification with error flag  
**User Impact:** Knows trade happened, limited details

### Edge Case 6: Telegram API Failure
**Scenario:** Telegram send_message fails  
**Handling:** Retry 3 times, log to database, send to fallback bot  
**User Impact:** Slight delay, but receives notification

---

## ROLLOUT STRATEGY

### Week 1: Development & Unit Testing
**Days 1-2:** Implement V6 entry alert
**Days 3-4:** Implement V6 exit alert & Trend Pulse alert
**Day 5:** Implement shadow mode & pattern alerts
**Days 6-7:** Unit testing & bug fixes

### Week 2: Integration & User Testing
**Days 1-2:** Integration testing with notification router
**Days 3-4:** End-to-end testing with mock Pine Script alerts
**Day 5:** Manual testing by developer
**Days 6-7:** Beta user testing (2-3 users)

### Deployment
**Phase 1:** Shadow mode only (read-only notifications)
**Phase 2:** Enable for beta users (V6 alerts active)
**Phase 3:** Enable for all users

**Rollback Plan:**
- If error rate >5%, disable V6 notifications
- Route all V6 trades to generic notification
- Fix bugs, redeploy

---

## SUCCESS CRITERIA

### Must Have ✅
- [ ] V6 entry alerts show timeframe (15M/30M/1H/4H)
- [ ] V6 entry alerts show Price Action pattern
- [ ] V6 entry alerts visually distinct from V3
- [ ] V6 exit alerts show exit reason detail
- [ ] Trend Pulse alerts sent before entry
- [ ] Shadow mode alerts clearly marked
- [ ] Notification router auto-detects V6 vs V3
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] No errors in production

### Should Have 📋
- [ ] Trend Pulse strength bar displays correctly
- [ ] Higher TF trend alignment shown
- [ ] Price Action pattern quality indicated
- [ ] Exit type emojis consistent
- [ ] Timestamps formatted correctly
- [ ] Plugin tags clear and readable
- [ ] User can distinguish V6 from V3 at a glance

### Nice to Have 🎁
- [ ] Voice alerts for Trend Pulse (if voice system ready)
- [ ] Pattern quality explanation
- [ ] Link to `/shadow` command in shadow alerts
- [ ] Notification delivery metrics logged
- [ ] A/B testing different formats

---

## DEPENDENCIES

**Internal:**
- ✅ NotificationBot infrastructure exists
- ✅ Notification router exists
- ⚠️ V6 plugins must send correct payload format
- ⚠️ Trend Pulse Manager must be integrated

**External:**
- ✅ Telegram Bot API (no changes needed)
- ⚠️ Pine Script V6 must send `price_action_pattern` field
- ⚠️ Database must store V6-specific fields

**Blocking Issues:**
- None (can implement independently)

**Unblocks:**
- Phase 2: V6 Timeframe Menu (needs notifications for testing)
- Phase 5: Notification Filtering (needs V6 notifications to exist)

---

## DOCUMENT VERSION

**Version:** 1.0  
**Created:** January 19, 2026  
**Last Updated:** January 19, 2026  
**Status:** Ready for Implementation  
**Approved By:** Pending

---

**Next Document:** [02_V6_TIMEFRAME_MENU_PLAN.md](02_V6_TIMEFRAME_MENU_PLAN.md)

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