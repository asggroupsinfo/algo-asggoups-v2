# BATCH 1: Foundation & Core Planning - Implementation Plan

**Created:** January 19, 2026
**Status:** Analysis Complete

---

## Documents Analyzed

1. `00_MASTER_PLAN.md` - Overall architecture vision
2. `01_COMPLETE_COMMAND_INVENTORY.md` - All commands that need to exist
3. `01_V6_NOTIFICATION_SYSTEM_PLAN.md` - V6 notification requirements
4. `02_NOTIFICATION_SYSTEMS_COMPLETE.md` - Complete notification specs
5. `02_V6_TIMEFRAME_MENU_PLAN.md` - V6 timeframe menu requirements

---

## Features Extracted from Documents

### From 00_MASTER_PLAN.md:
- Phase 1: V6 Notification System (16 hours)
- Phase 2: V6 Timeframe Plugin Menu (20 hours)
- Phase 3: Priority Command Handlers (32 hours)
- Phase 4: Analytics Command Interface (24 hours)
- Phase 5: Notification Filtering System (28 hours)
- Phase 6: Menu Callback Wiring (20 hours)

### From 01_COMPLETE_COMMAND_INVENTORY.md:
- 95+ commands documented
- V6 timeframe commands: /tf15m_on, /tf15m_off, /tf30m_on, /tf30m_off, /tf1h_on, /tf1h_off, /tf4h_on, /tf4h_off
- V6 status commands: /v6_status, /v6_control
- Analytics commands: /daily, /weekly, /monthly, /compare, /export

### From 01_V6_NOTIFICATION_SYSTEM_PLAN.md:
- V6-specific entry alert method
- V6-specific exit alert method
- Trend Pulse detection notification
- Shadow mode trade alerts
- V6 vs V3 visual distinction in messages
- Timeframe identification in all V6 notifications

### From 02_NOTIFICATION_SYSTEMS_COMPLETE.md:
- V6 Notification Types: V6_ENTRY_15M, V6_ENTRY_30M, V6_ENTRY_1H, V6_ENTRY_4H
- V6_EXIT, V6_TP_HIT, V6_SL_HIT
- V6_TIMEFRAME_ENABLED, V6_TIMEFRAME_DISABLED
- V6_DAILY_SUMMARY
- Routing rules for V6 notifications
- V6 notification templates

### From 02_V6_TIMEFRAME_MENU_PLAN.md:
- V6 submenu showing 4 timeframes (15M, 30M, 1H, 4H)
- Individual enable/disable toggles
- Per-timeframe status display
- Per-timeframe performance metrics
- Enable All / Disable All buttons
- Timeframe-specific configuration

---

## Already Implemented (Check Existing Code)

### notification_router.py (882 lines):
- [x] NotificationType enum with V6 types (V6_ENTRY_15M, V6_ENTRY_30M, V6_ENTRY_1H, V6_ENTRY_4H, V6_EXIT, V6_TP_HIT, V6_SL_HIT, V6_TIMEFRAME_ENABLED, V6_TIMEFRAME_DISABLED, V6_DAILY_SUMMARY, V6_SIGNAL, V6_BREAKEVEN)
- [x] NotificationFormatter with V6 formatters (format_v6_entry, format_v6_exit, format_v6_tp_hit, format_v6_sl_hit, format_v6_timeframe_toggle, format_v6_daily_summary, format_v6_signal)
- [x] create_default_router() function

### v6_control_menu_handler.py (674 lines):
- [x] V6ControlMenuHandler class
- [x] show_v6_main_menu() - Main V6 control menu with timeframe toggles
- [x] handle_toggle_system() - Toggle entire V6 system
- [x] handle_toggle_timeframe() - Toggle individual timeframes
- [x] handle_enable_all() - Enable all timeframes
- [x] handle_disable_all() - Disable all timeframes
- [x] show_v6_stats_menu() - Per-timeframe stats
- [x] show_v6_configure_menu() - Configuration menu
- [x] show_timeframe_config() - Per-timeframe config
- [x] handle_callback() - Callback handler

### v6_command_handlers.py (exists):
- [x] V6CommandHandlers class
- [x] V6 timeframe commands (/tf15m_on, /tf15m_off, etc.)
- [x] /v6_status, /v6_control commands

### command_registry.py (exists):
- [x] V6 commands registered
- [x] V6 callbacks registered

### analytics_menu_handler.py (exists):
- [x] AnalyticsMenuHandler class
- [x] Daily/weekly/monthly views
- [x] Performance by pair/logic
- [x] Export functionality

### menu_manager.py (exists):
- [x] V6 handler integration
- [x] Analytics handler integration
- [x] Dual order handler integration
- [x] Re-entry handler integration

### controller_bot.py (exists):
- [x] V6 menu methods
- [x] Analytics menu methods
- [x] Dual order menu methods
- [x] Re-entry menu methods

---

## Missing Features (Need to Implement)

### 1. Notification Preferences Menu
- [ ] notification_preferences_menu.py - New file needed
- [ ] Per-type notification toggles
- [ ] Per-plugin filtering (V3 only / V6 only / Both)
- [ ] Quiet hours configuration
- [ ] Priority levels (Critical / Important / Info)
- [ ] /notifications command

### 2. Shadow Mode Notifications
- [ ] send_shadow_trade_alert() method in notification_bot.py
- [ ] Shadow mode visual distinction (ghost icon)
- [ ] /shadow command for tracking

### 3. Price Action Pattern Notifications
- [ ] send_price_action_pattern_alert() method
- [ ] Pattern quality indicators
- [ ] Entry potential indicators

### 4. Trend Pulse Detection Alerts
- [ ] send_trend_pulse_alert() method
- [ ] Pulse strength bar visualization
- [ ] Higher TF alignment indicators

### 5. Missing Analytics Commands
- [ ] /compare command (V3 vs V6 comparison)
- [ ] /export command (CSV/PDF export)

### 6. V6 Performance Comparison View
- [ ] Performance comparison across all 4 timeframes
- [ ] Best/worst performer highlighting
- [ ] AI recommendation

---

## Files to Create or Modify

### New Files:
1. `src/telegram/notification_preferences.py` - Notification filtering system
2. `src/menu/notification_preferences_menu.py` - Notification preferences menu

### Files to Modify:
1. `src/telegram/notification_bot.py` - Add shadow trade and trend pulse alerts
2. `src/telegram/controller_bot.py` - Add /compare, /export, /notifications commands
3. `src/telegram/command_registry.py` - Register new commands

---

## Testing Requirements

1. Run existing tests: `pytest tests/ -v`
2. Verify V6 notification types work
3. Verify V6 menu callbacks work
4. Verify analytics commands work
5. Test notification preferences (once implemented)

---

## Implementation Priority

1. **HIGH**: Notification preferences menu (missing)
2. **MEDIUM**: Shadow mode notifications (missing)
3. **MEDIUM**: Trend pulse alerts (missing)
4. **LOW**: /compare and /export commands (missing)

---

## Notes

Most of Batch 1 features are already implemented from previous Telegram V5 Upgrade work:
- V6 notification types and formatters: COMPLETE
- V6 timeframe menu: COMPLETE
- V6 command handlers: COMPLETE
- Analytics menu handler: COMPLETE
- Menu manager integration: COMPLETE

Remaining work focuses on:
- Notification preferences/filtering system
- Shadow mode and trend pulse notifications
- V3 vs V6 comparison command
