# PHASE 2: V6 TIMEFRAME PLUGIN MENU

**Phase:** 2 of 6  
**Priority:** CRITICAL  
**Timeline:** Week 2-3 (20 hours)  
**Status:** Planning  
**Dependencies:** Phase 1 (V6 Notifications for testing)

---

## OBJECTIVE

Create interactive menu system for V6 Price Action plugins that allows users to:
1. View all 4 V6 timeframe plugins (15M, 30M, 1H, 4H) individually
2. Enable/disable each timeframe plugin independently
3. See per-timeframe status and performance metrics
4. Configure timeframe-specific settings
5. Switch between timeframes without restarting bot

---

## CURRENT STATE

### What Exists ✅

**File:** `Trading_Bot/src/telegram/plugin_control_menu.py`

**Current Plugin Menu:**
```
🔌 PLUGIN CONTROL

┌─ V3 Combined Logic
│  Status: ✅ Enabled
│  Trades Today: 5
│  [V3 Settings] [Disable]
│
└─ V6 Price Action
   Status: ✅ Enabled
   Trades Today: 8
   [V6 Settings] [Disable]

[Refresh] [Back to Menu]
```

**Problems:**
- ❌ V6 shown as single plugin
- ❌ Cannot control individual timeframes (15M, 30M, 1H, 4H)
- ❌ "V6 Settings" button callback not implemented (`menu_v6_settings`)
- ❌ No per-timeframe performance metrics
- ❌ All-or-nothing approach (all V6 timeframes on/off together)
- ❌ Cannot optimize by disabling underperforming timeframes

### What's Missing ❌

**V6 Timeframe Selection:**
1. ✗ Submenu showing 4 timeframe plugins
2. ✗ Individual enable/disable toggles
3. ✗ Per-timeframe status indicators
4. ✗ Per-timeframe performance metrics (win rate, P&L)
5. ✗ Timeframe-specific configuration
6. ✗ Quick timeframe switching
7. ✗ Bulk actions (Enable All, Disable All)

---

## PROPOSED SOLUTION

### 1. V6 Submenu Structure

**Entry Point:** Main Plugin Menu → "V6 Settings" button

**V6 Submenu Level 1 - Overview:**
```
🟢 V6 PRICE ACTION PLUGINS

📊 Overall Performance (Today)
├─ Total Trades: 12
├─ Win Rate: 66.7%
└─ P&L: +$45.00 (+22.5 pips)

⏱️ ACTIVE TIMEFRAMES

┌─ 15M (v6_price_action_15m)
│  Status: ✅ Enabled | Trades: 4 | Win: 75%
│  [Configure] [Disable]
│
├─ 30M (v6_price_action_30m)
│  Status: ✅ Enabled | Trades: 3 | Win: 66%
│  [Configure] [Disable]
│
├─ 1H (v6_price_action_1h)
│  Status: ✅ Enabled | Trades: 3 | Win: 66%
│  [Configure] [Disable]
│
└─ 4H (v6_price_action_4h)
│  Status: ❌ Disabled | Trades: 2 | Win: 50%
│  [Configure] [Enable]

[Enable All] [Disable All] [Performance Report]
[Back to Plugin Menu]
```

**Key Features:**
- Overall V6 performance at top
- Individual status for each timeframe
- Quick enable/disable per timeframe
- Configure button for each timeframe
- Bulk actions (Enable All / Disable All)
- Performance report link

---

### 2. Individual Timeframe Configuration

**Entry Point:** V6 Submenu → "Configure" button for specific timeframe

**Example: 1H Configuration:**
```
⚙️ V6 PRICE ACTION - 1H CONFIG

📊 PERFORMANCE (Last 7 Days)
├─ Total Trades: 18
├─ Win Rate: 72.2%
├─ Total P&L: +$120.00
├─ Avg Pips: +6.7 pips
├─ Best Trade: +$25.00
└─ Worst Trade: -$8.00

🎯 SIGNAL SETTINGS
├─ Trend Pulse Threshold: 7/10
│  [Increase] [Decrease]
├─ Pattern Quality: MEDIUM+
│  [Low] [Medium] [High] [Any]
└─ Higher TF Alignment: Required
   [Required] [Preferred] [Ignored]

💼 RISK SETTINGS
├─ Lot Size: 0.01
│  [Increase] [Decrease]
├─ SL Distance: 10 pips
│  [Tighter] [Wider]
└─ TP Distance: 20 pips
   [Shorter] [Longer]

🔔 NOTIFICATION SETTINGS
├─ Entry Alerts: ✅ Enabled
│  [Toggle]
├─ Trend Pulse Alerts: ✅ Enabled
│  [Toggle]
└─ Pattern Alerts: ❌ Disabled
   [Toggle]

⚡ QUICK ACTIONS
[Shadow Mode] [Reset to Default] [Disable Plugin]

[Save Changes] [Cancel] [Back]
```

**Configurable Parameters:**
1. Trend Pulse threshold (1-10)
2. Pattern quality filter (Low/Medium/High/Any)
3. Higher TF alignment requirement
4. Lot size
5. SL/TP distances
6. Notification preferences
7. Shadow mode toggle

---

### 3. Performance Comparison View

**Entry Point:** V6 Submenu → "Performance Report" button

```
📊 V6 TIMEFRAME COMPARISON

Period: Last 7 Days

┌─ 15M Plugin
│  ├─ Trades: 28 | Win Rate: 75.0%
│  ├─ P&L: +$210.00 (+105 pips)
│  ├─ Avg per Trade: +$7.50
│  └─ Best Day: +$45.00 (Jan 17)
│
├─ 30M Plugin
│  ├─ Trades: 18 | Win Rate: 66.7%
│  ├─ P&L: +$90.00 (+45 pips)
│  ├─ Avg per Trade: +$5.00
│  └─ Best Day: +$30.00 (Jan 18)
│
├─ 1H Plugin
│  ├─ Trades: 12 | Win Rate: 83.3%
│  ├─ P&L: +$120.00 (+60 pips)
│  ├─ Avg per Trade: +$10.00 🏆 BEST
│  └─ Best Day: +$50.00 (Jan 19) 🏆
│
└─ 4H Plugin
   ├─ Trades: 4 | Win Rate: 50.0%
   ├─ P&L: -$10.00 (-5 pips) ⚠️
   ├─ Avg per Trade: -$2.50
   └─ Best Day: +$15.00 (Jan 16)

💡 RECOMMENDATION
Best Performer: 1H (83.3% win rate)
Consider Disabling: 4H (negative P&L)

[View Details] [Export CSV] [Back]
```

**Key Metrics:**
- Trades count
- Win rate
- Total P&L
- Average per trade
- Best day
- Highlight best/worst performers
- AI recommendation

---

### 4. Bulk Actions

**Enable All Timeframes:**
```
⚡ ENABLE ALL V6 TIMEFRAMES?

This will activate:
✅ 15M Price Action
✅ 30M Price Action
✅ 1H Price Action
✅ 4H Price Action

⚠️ Warning: Running all timeframes increases
trade frequency and requires more monitoring.

💰 Risk Impact:
├─ Estimated Trades/Day: 15-25
├─ Max Concurrent Trades: 8-12
└─ Recommended Capital: $1000+

[Confirm Enable All] [Cancel]
```

**Disable All Timeframes:**
```
⛔ DISABLE ALL V6 TIMEFRAMES?

This will deactivate:
❌ 15M Price Action (Currently: 2 open trades)
❌ 30M Price Action (Currently: 1 open trade)
❌ 1H Price Action (Currently: 0 open trades)
❌ 4H Price Action (Currently: 0 open trades)

⚠️ Warning: Open trades will remain active.
Only new entries will be prevented.

Options:
[Disable All + Close Trades] [Disable All Only]
[Cancel]
```

---

### 5. Quick Timeframe Switching

**Scenario:** User wants to test only 1H timeframe

**Current Workflow (Manual):**
1. Edit config.json
2. Find V6 plugin section
3. Set enabled=false for 15M, 30M, 4H
4. Set enabled=true for 1H
5. Restart bot
6. Hope it works

**New Workflow (Menu-based):**
1. Open V6 Submenu
2. Click "Disable All"
3. Click "Enable" on 1H
4. Done (no restart needed)

**Time Saved:** 5 minutes → 10 seconds  
**Errors Prevented:** JSON syntax errors, typos

---

## IMPLEMENTATION DETAILS

### File Structure

**New File:** `Trading_Bot/src/telegram/v6_timeframe_menu_builder.py`

```python
"""
V6 Timeframe Menu Builder

Handles V6 Price Action timeframe plugin menu system:
- Individual timeframe control (15M, 30M, 1H, 4H)
- Per-timeframe configuration
- Performance comparison
- Bulk actions
"""

class V6TimeframeMenuBuilder:
    """Build V6 timeframe plugin menus"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.trading_engine = None
        self.plugin_manager = None
    
    def build_v6_submenu(self) -> Dict:
        """
        Build V6 timeframe overview submenu
        
        Returns:
            Dict with message text and inline_keyboard
        """
        pass
    
    def build_timeframe_config_menu(self, timeframe: str) -> Dict:
        """
        Build configuration menu for specific timeframe
        
        Args:
            timeframe: '15M', '30M', '1H', '4H'
        
        Returns:
            Dict with message text and inline_keyboard
        """
        pass
    
    def build_performance_comparison(self, days: int = 7) -> Dict:
        """
        Build performance comparison view
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dict with message text and inline_keyboard
        """
        pass
    
    def handle_enable_timeframe(self, timeframe: str, chat_id: int) -> bool:
        """Enable specific V6 timeframe plugin"""
        pass
    
    def handle_disable_timeframe(self, timeframe: str, chat_id: int) -> bool:
        """Disable specific V6 timeframe plugin"""
        pass
    
    def handle_enable_all_timeframes(self, chat_id: int) -> bool:
        """Enable all V6 timeframe plugins"""
        pass
    
    def handle_disable_all_timeframes(self, chat_id: int, close_trades: bool = False) -> bool:
        """Disable all V6 timeframe plugins"""
        pass
    
    def handle_update_timeframe_config(self, timeframe: str, param: str, value: Any) -> bool:
        """Update specific configuration parameter for timeframe"""
        pass
    
    def get_timeframe_performance(self, timeframe: str, days: int = 7) -> Dict:
        """Get performance metrics for specific timeframe"""
        pass
    
    def get_all_timeframe_status(self) -> Dict:
        """Get status of all V6 timeframe plugins"""
        pass
```

### Integration with Existing Plugin Control Menu

**File:** `Trading_Bot/src/telegram/plugin_control_menu.py`

**Modification Needed:**

```python
# Around line 150 (where V6 button is created):

# OLD (broken callback):
callback_data = "menu_v6_settings"  # Not implemented

# NEW (wire to V6 timeframe menu):
callback_data = "menu_v6_timeframes"  # New callback

# In callback handler (around line 400):
def handle_callback(self, callback_data: str, chat_id: int) -> bool:
    # ... existing code ...
    
    # NEW HANDLER:
    if callback_data == "menu_v6_timeframes":
        return self._show_v6_timeframe_menu(chat_id)
    
    elif callback_data.startswith("v6_enable_"):
        timeframe = callback_data.replace("v6_enable_", "")
        return self.v6_menu_builder.handle_enable_timeframe(timeframe, chat_id)
    
    elif callback_data.startswith("v6_disable_"):
        timeframe = callback_data.replace("v6_disable_", "")
        return self.v6_menu_builder.handle_disable_timeframe(timeframe, chat_id)
    
    elif callback_data == "v6_enable_all":
        return self.v6_menu_builder.handle_enable_all_timeframes(chat_id)
    
    elif callback_data == "v6_disable_all":
        # Show confirmation first
        return self._show_disable_all_confirmation(chat_id)
    
    elif callback_data.startswith("v6_config_"):
        timeframe = callback_data.replace("v6_config_", "")
        return self._show_timeframe_config(timeframe, chat_id)
    
    # ... rest of handlers ...

def _show_v6_timeframe_menu(self, chat_id: int) -> bool:
    """Show V6 timeframe submenu"""
    menu_data = self.v6_menu_builder.build_v6_submenu()
    return self.bot.send_message(
        menu_data['text'],
        reply_markup=menu_data['inline_keyboard']
    )
```

### Callback Data Structure

**Naming Convention:**
```
v6_enable_15m       → Enable 15M plugin
v6_enable_30m       → Enable 30M plugin
v6_enable_1h        → Enable 1H plugin
v6_enable_4h        → Enable 4H plugin
v6_disable_15m      → Disable 15M plugin
v6_disable_30m      → Disable 30M plugin
v6_disable_1h       → Disable 1H plugin
v6_disable_4h       → Disable 4H plugin
v6_enable_all       → Enable all timeframes
v6_disable_all      → Disable all timeframes
v6_config_15m       → Configure 15M plugin
v6_config_30m       → Configure 30M plugin
v6_config_1h        → Configure 1H plugin
v6_config_4h        → Configure 4H plugin
v6_performance      → Show performance comparison
v6_param_<tf>_<param>_<val>  → Update parameter
```

### Configuration Parameter Updates

**Callback Pattern:**
```
v6_param_1h_pulse_threshold_8    → Set 1H pulse threshold to 8
v6_param_1h_pattern_quality_high → Set 1H pattern quality to high
v6_param_1h_lot_size_0.02        → Set 1H lot size to 0.02
v6_param_1h_sl_distance_15       → Set 1H SL distance to 15 pips
```

**Implementation:**
```python
def handle_parameter_update(self, callback_data: str, chat_id: int) -> bool:
    """Handle parameter update callback"""
    # Parse callback: v6_param_1h_pulse_threshold_8
    parts = callback_data.split('_')
    timeframe = parts[2]  # '1h'
    param = '_'.join(parts[3:-1])  # 'pulse_threshold'
    value = parts[-1]  # '8'
    
    # Update configuration
    success = self.update_timeframe_config(timeframe, param, value)
    
    # Refresh config menu
    menu_data = self.build_timeframe_config_menu(timeframe.upper())
    return self.bot.edit_message(
        chat_id,
        menu_data['text'],
        reply_markup=menu_data['inline_keyboard']
    )
```

---

## TESTING PLAN

### Unit Tests

**Test File:** `tests/telegram/test_v6_timeframe_menu.py`

**Test Cases:**
1. `test_build_v6_submenu()` - V6 submenu renders correctly
2. `test_build_timeframe_config_menu_15m()` - 15M config menu
3. `test_build_timeframe_config_menu_1h()` - 1H config menu
4. `test_enable_timeframe_15m()` - Enable 15M plugin
5. `test_disable_timeframe_1h()` - Disable 1H plugin
6. `test_enable_all_timeframes()` - Bulk enable
7. `test_disable_all_timeframes()` - Bulk disable
8. `test_get_timeframe_performance()` - Performance metrics
9. `test_performance_comparison()` - Comparison view
10. `test_update_pulse_threshold()` - Parameter update
11. `test_update_lot_size()` - Lot size update
12. `test_callback_parsing()` - Callback data parsing

### Integration Tests

**Test Scenarios:**
1. Click "V6 Settings" → V6 submenu appears
2. Enable 15M → 15M plugin activates, receives alerts
3. Disable 1H → 1H plugin deactivates, no new alerts
4. Enable All → All 4 plugins activate
5. Disable All → All 4 plugins deactivate
6. Update pulse threshold → Config saved, plugin reloaded
7. Performance comparison → Metrics from database displayed

**Mock Requirements:**
- Mock plugin manager (enable/disable)
- Mock database (performance queries)
- Mock config manager (save/load)
- Mock Telegram API (send/edit messages)

### End-to-End Test

```
1. User opens Plugin Menu
2. Clicks "V6 Settings"
3. Sees V6 submenu with 4 timeframes
4. Clicks "Configure" on 1H
5. Sees 1H configuration menu
6. Clicks "Increase" on pulse threshold
7. Threshold updates from 7 to 8
8. Clicks "Save Changes"
9. Config saved to database
10. 1H plugin reloaded with new config
11. User receives confirmation
12. Clicks "Back to V6 Menu"
13. Returns to V6 submenu
14. 1H shows updated config indicator
```

### Performance Testing

**Load Test:**
- Simulate 100 rapid button clicks
- Measure response time
- Check for race conditions
- Verify no duplicate enable/disable

**Database Test:**
- Query performance metrics for 30 days
- Measure query time (should be <500ms)
- Test with 1000+ trades
- Verify no timeouts

---

## EDGE CASES & ERROR HANDLING

### Edge Case 1: Plugin Already Enabled
**Scenario:** User clicks "Enable" on already-enabled plugin  
**Handling:** Show status message "Already enabled", no action  
**User Impact:** Clear feedback, no confusion

### Edge Case 2: Plugin Already Disabled
**Scenario:** User clicks "Disable" on already-disabled plugin  
**Handling:** Show status message "Already disabled", no action  
**User Impact:** Clear feedback

### Edge Case 3: Open Trades When Disabling
**Scenario:** User disables plugin with 3 open trades  
**Handling:** Show warning, ask if should close trades or leave open  
**User Impact:** Informed decision, no surprise

### Edge Case 4: Configuration Update Failure
**Scenario:** Config save fails (disk full, permissions)  
**Handling:** Show error message, revert to previous config  
**User Impact:** Knows update failed, can retry

### Edge Case 5: No Performance Data
**Scenario:** New plugin, no trades yet  
**Handling:** Show "No data yet" message, suggest waiting  
**User Impact:** Understands why no metrics

### Edge Case 6: Database Query Timeout
**Scenario:** Performance query takes >30 seconds  
**Handling:** Show loading indicator, cancel after timeout, show cached data  
**User Impact:** Not stuck waiting, gets stale but usable data

### Edge Case 7: All Timeframes Disabled
**Scenario:** User disables all V6 timeframes  
**Handling:** Show warning "V6 completely disabled", suggest enabling at least one  
**User Impact:** Knows V6 is off, can re-enable

### Edge Case 8: Invalid Parameter Value
**Scenario:** Lot size set to 0 or negative  
**Handling:** Validate input, show error, don't save  
**User Impact:** Knows value is invalid, must correct

---

## ROLLOUT STRATEGY

### Week 2: Development
**Days 1-2:** Create `v6_timeframe_menu_builder.py`
**Days 3-4:** Implement submenu and config menus
**Day 5:** Wire callbacks to plugin_control_menu.py
**Days 6-7:** Unit testing

### Week 3: Integration & Testing
**Days 1-2:** Integration testing
**Days 3-4:** End-to-end testing
**Day 5:** Performance testing
**Days 6-7:** Beta user testing

### Deployment
**Phase 1:** Read-only mode (menus show but don't change config)
**Phase 2:** Enable for beta users (fully functional)
**Phase 3:** Enable for all users

**Rollback Plan:**
- If error rate >3%, disable V6 menus
- Route "V6 Settings" to "Coming Soon" message
- Fix bugs, redeploy

---

## SUCCESS CRITERIA

### Must Have ✅
- [ ] V6 submenu shows all 4 timeframes individually
- [ ] Can enable/disable each timeframe independently
- [ ] Per-timeframe status indicators working
- [ ] "V6 Settings" callback fixed and functional
- [ ] No bot restart needed for timeframe toggling
- [ ] Configuration changes save correctly
- [ ] Performance metrics display for each timeframe

### Should Have 📋
- [ ] Bulk enable/disable all timeframes
- [ ] Performance comparison view
- [ ] Per-timeframe configuration menus
- [ ] Parameter updates (pulse threshold, lot size, etc.)
- [ ] Notification preferences per timeframe
- [ ] Visual indicators for best/worst performers
- [ ] AI recommendations based on performance

### Nice to Have 🎁
- [ ] Export performance to CSV
- [ ] Scheduled performance reports
- [ ] Timeframe-specific backtesting
- [ ] Advanced parameter tuning
- [ ] A/B testing different configs

---

## DEPENDENCIES

**Internal:**
- ✅ Plugin Control Menu infrastructure exists
- ✅ Plugin Manager can enable/disable plugins
- ⚠️ Database must store per-plugin performance
- ⚠️ Config system must support per-timeframe settings
- ✅ Phase 1 (V6 Notifications) for testing

**External:**
- ✅ Telegram Bot API (no changes needed)
- ⚠️ Plugin Manager must expose enable/disable API
- ⚠️ Database schema must have plugin_name column

**Blocking Issues:**
- None (can implement independently)

**Unblocks:**
- Phase 3: Priority Commands (needs V6 timeframe toggles)
- Phase 4: Analytics (needs per-timeframe metrics)

---

## DOCUMENT VERSION

**Version:** 1.0  
**Created:** January 19, 2026  
**Last Updated:** January 19, 2026  
**Status:** Ready for Implementation  
**Approved By:** Pending

---

**Previous:** [01_V6_NOTIFICATION_SYSTEM_PLAN.md](01_V6_NOTIFICATION_SYSTEM_PLAN.md)  
**Next:** [03_PRIORITY_COMMAND_HANDLERS_PLAN.md](03_PRIORITY_COMMAND_HANDLERS_PLAN.md)

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