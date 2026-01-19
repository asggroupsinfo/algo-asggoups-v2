# Batch 2 Implementation Plan: Menu & Priority Systems

**Batch:** 2 of 5
**Status:** In Progress
**Date:** 2026-01-19

---

## Documents Reviewed

1. **03_MENU_SYSTEMS_ARCHITECTURE.md** - Menu handlers overview, callback flow, menu structure
2. **03_PRIORITY_COMMAND_HANDLERS_PLAN.md** - Priority command handlers (20 Tier 1 + Tier 2 commands)
3. **04_ANALYTICS_CAPABILITIES.md** - Analytics features, reports, V6 analytics
4. **04_PHASES_4_5_6_SUMMARY.md** - Phases 4-6 summary, analytics interface, notification filtering
5. **05_IMPLEMENTATION_ROADMAP.md** - 10-week implementation timeline

---

## Features from Documents

### From 03_MENU_SYSTEMS_ARCHITECTURE.md:
- MenuManager central orchestration
- V6 Control Menu Handler
- Analytics Menu Handler
- Menu callback routing
- Main menu structure with all categories

### From 03_PRIORITY_COMMAND_HANDLERS_PLAN.md:
- Tier 1 Commands (10): /status, /positions, /pnl, /chains, /daily, /weekly, /compare, /setlot, /risktier, /autonomous
- Tier 2 Commands (10): /tf15m, /tf30m, /tf1h, /tf4h, /slhunt, /tpcontinue, /reentry, /levels, /shadow, /trends
- Plugin-aware command responses
- V3 vs V6 breakdown in status/positions/pnl

### From 04_ANALYTICS_CAPABILITIES.md:
- Daily/Weekly/Monthly reports
- V6 timeframe performance
- V3 vs V6 comparison
- Export to CSV
- By-pair and by-logic analytics

### From 04_PHASES_4_5_6_SUMMARY.md:
- Analytics command interface
- Date range selection
- Plugin filtering in reports
- Symbol filtering

### From 05_IMPLEMENTATION_ROADMAP.md:
- Week-by-week breakdown
- Testing requirements
- Success criteria

---

## Already Implemented (Verified in Code)

### Menu Handlers:
1. **V6ControlMenuHandler** (`src/menu/v6_control_menu_handler.py` - 674 lines)
   - show_v6_main_menu()
   - handle_toggle_system()
   - handle_toggle_timeframe()
   - handle_enable_all()
   - handle_disable_all()
   - show_v6_stats_menu()
   - show_v6_configure_menu()
   - show_timeframe_config()
   - handle_callback()

2. **AnalyticsMenuHandler** (`src/menu/analytics_menu_handler.py` - 572 lines)
   - show_analytics_menu()
   - show_daily_analytics()
   - show_weekly_analytics()
   - show_monthly_analytics()
   - show_analytics_by_pair()
   - show_analytics_by_logic()
   - export_analytics()
   - handle_export_csv()
   - handle_callback()

3. **CommandRegistry** (`src/telegram/command_registry.py` - 573 lines)
   - 95+ commands registered
   - V6 timeframe commands (/tf15m_on, /tf15m_off, etc.)
   - Analytics commands (/daily, /weekly, /monthly, /compare)
   - Re-entry commands (/chains, /autonomous, /reentry)
   - Risk commands (/setlot, /risktier)
   - V6 control callbacks registered

### Integration in MenuManager:
- V6ControlMenuHandler integrated
- AnalyticsMenuHandler integrated
- DualOrderMenuHandler integrated
- ReentryMenuHandler integrated
- NotificationPreferencesMenuHandler integrated (Batch 1)

---

## Missing Features to Implement

### 1. Priority Command Handlers in Controller Bot
The commands are registered in CommandRegistry but need actual handler implementations in controller_bot.py:

**Missing Handlers:**
- handle_compare() - V3 vs V6 comparison
- handle_chains() - Re-entry chain status
- handle_autonomous() - Autonomous system toggle
- handle_setlot() - Set lot size
- handle_risktier() - Set risk tier

### 2. V3 vs V6 Comparison Menu
Need to add a comparison view that shows side-by-side V3 vs V6 performance.

### 3. Tests for Batch 2 Features
Need to add tests for:
- V6ControlMenuHandler
- AnalyticsMenuHandler
- Priority command handlers

---

## Implementation Tasks

### Task 1: Add Priority Command Handlers to Controller Bot
**File:** `src/telegram/controller_bot.py`
**Methods to add:**
- handle_compare() - Compare V3 vs V6 performance
- handle_chains() - Show active re-entry chains
- handle_autonomous() - Toggle autonomous re-entry system

### Task 2: Add V3 vs V6 Comparison View
**File:** `src/menu/analytics_menu_handler.py`
**Method to add:**
- show_v3_v6_comparison() - Side-by-side comparison view

### Task 3: Add Tests for Batch 2 Features
**File:** `tests/test_telegram_v5_upgrade.py`
**Test classes to add:**
- TestV6ControlMenuHandler
- TestAnalyticsMenuHandler
- TestPriorityCommandHandlers

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| src/telegram/controller_bot.py | MODIFY | Add priority command handlers |
| src/menu/analytics_menu_handler.py | MODIFY | Add V3 vs V6 comparison view |
| tests/test_telegram_v5_upgrade.py | MODIFY | Add Batch 2 tests |

---

## Testing Requirements

1. All existing tests must pass
2. New tests for V6ControlMenuHandler
3. New tests for AnalyticsMenuHandler
4. New tests for priority command handlers
5. Target: >80% coverage

---

## Success Criteria

- [ ] Priority command handlers implemented
- [ ] V3 vs V6 comparison view working
- [ ] All tests passing
- [ ] No regression in existing functionality
- [ ] Pushed to GitLab

---

## Notes

Most of Batch 2 features are already implemented from previous work:
- V6ControlMenuHandler is complete
- AnalyticsMenuHandler is complete
- CommandRegistry has all commands registered

The main gaps are:
1. Some priority command handlers need implementation in controller_bot.py
2. V3 vs V6 comparison view needs to be added
3. Tests need to be added for Batch 2 features
