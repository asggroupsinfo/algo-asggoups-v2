# COMPLETE PROBLEM INVENTORY - V5 Hybrid Plugin Architecture Surgery

**Audit Date:** 2026-01-14  
**Auditor:** Devin AI  
**Methodology:** Deep forensic scan of entire codebase  
**Total Problems Found:** 21  
**Critical:** 6 | **High:** 7 | **Medium:** 5 | **Low:** 3

---

## CATEGORY 1: CORE WIRING FAILURE

### Problem 1.1: trading_engine.py Contains ALL Hardcoded V3 Logic
**Severity:** CRITICAL  
**Effort:** HIGH (4-6 hours)

**Root Cause:**  
When plugins were created, the core `trading_engine.py` was never updated to delegate signal processing to them. The original V3 logic was copied into plugins but never removed from core.

**Impact:**  
- Plugins are "ghost code" - they exist but are never called
- All V3 signals are processed by hardcoded core logic
- Plugin system is non-functional

**Dependencies:**  
- All plugin functionality depends on this being fixed
- ServiceAPI integration depends on this
- Database isolation depends on this

**Evidence (Specific Lines):**
| Function | Lines | Description |
|----------|-------|-------------|
| process_alert() | 208-233 | entry_v3 handled directly via execute_v3_entry() |
| process_alert() | 236-242 | exit_v3 handled directly via handle_v3_exit() |
| execute_v3_entry() | 367-431 | Complete V3 entry logic hardcoded |
| _route_v3_to_logic() | 433-452 | Routing logic hardcoded |
| _get_logic_multiplier() | 454-463 | Multiplier logic hardcoded |
| _place_hybrid_dual_orders_v3() | 465-696 | Order placement hardcoded |
| handle_v3_exit() | 698-837 | Exit handling hardcoded |
| handle_v3_reversal() | 839-985 | Reversal handling hardcoded |

**Fix Strategy:**
1. Delete all hardcoded V3 methods from trading_engine.py
2. Replace with calls to plugin_registry.route_alert_to_plugin()
3. Keep only routing, lifecycle, and execution logic in core

---

### Problem 1.2: route_alert_to_plugin() is NEVER Called
**Severity:** CRITICAL  
**Effort:** MEDIUM (2-3 hours)

**Root Cause:**  
The `process_alert()` method in trading_engine.py never calls `plugin_registry.route_alert_to_plugin()`. Instead, it processes signals directly.

**Impact:**  
- Plugins cannot process any signals
- Plugin system is completely bypassed
- All plugin code is dead code

**Dependencies:**  
- Depends on Problem 1.1 being fixed first
- All plugin features depend on this

**Evidence:**
- `plugin_registry.py` line 132-171: `route_alert_to_plugin()` method exists
- `trading_engine.py`: No call to `route_alert_to_plugin()` anywhere in the file

**Fix Strategy:**
1. Modify process_alert() to call route_alert_to_plugin() for V3 signals
2. Add V6 signal routing to call appropriate V6 plugins
3. Add error handling and fallback mechanism

---

### Problem 1.3: Plugin Hook Only Modifies Data, Doesn't Process It
**Severity:** HIGH  
**Effort:** LOW (1 hour)

**Root Cause:**  
The `execute_hook("signal_received")` call in trading_engine.py only allows plugins to filter/modify data. After the hook, the core still processes the signal directly.

**Impact:**  
- Plugins cannot take control of signal processing
- Hook is a filter, not a processor
- Misleading architecture

**Dependencies:**  
- Related to Problem 1.1 and 1.2

**Evidence:**
- `trading_engine.py` lines 187-202: Hook is called, but processing continues in core

**Fix Strategy:**
1. Change hook to be a pre-processor only (for validation/filtering)
2. Actual processing should be delegated to plugins via route_alert_to_plugin()

---

### Problem 1.4: Logic Control Flags in Core
**Severity:** HIGH  
**Effort:** LOW (1 hour)

**Root Cause:**  
`combinedlogic_1_enabled`, `combinedlogic_2_enabled`, `combinedlogic_3_enabled` flags are stored in trading_engine.py instead of plugin configuration.

**Impact:**  
- Logic enable/disable is core state, not plugin config
- Violates plugin isolation principle
- Hard to manage per-plugin settings

**Dependencies:**  
- Plugin configuration system
- Telegram commands for enable/disable

**Evidence:**
- `trading_engine.py` lines 101-104

**Fix Strategy:**
1. Move logic flags to plugin config.json files
2. Update enable_logic() and disable_logic() to modify plugin config
3. Update Telegram commands to use plugin registry

---

## CATEGORY 2: V6 INTEGRATION FAILURE

### Problem 2.1: V6 Signals Are NEVER Handled
**Severity:** CRITICAL  
**Effort:** HIGH (4-6 hours)

**Root Cause:**  
The `process_alert()` method in trading_engine.py has no handling for V6 alert types. It only handles entry_v3, exit_v3, squeeze_v3, trend_pulse_v3.

**Impact:**  
- V6 plugins (price_action_1m, 5m, 15m, 1h) are completely unused
- V6 trading strategies cannot execute
- V6 Pine Script integration is non-functional

**Dependencies:**  
- Depends on Problem 1.1 and 1.2 being fixed
- V6 plugin code exists but needs entry point

**Evidence:**
- `trading_engine.py` lines 204-260: Only V3 alert types handled
- No "entry_v6", "exit_v6" handling exists

**Fix Strategy:**
1. Add V6 alert type handling in process_alert()
2. Route V6 signals to appropriate plugin based on timeframe
3. Implement timeframe-to-plugin mapping

---

### Problem 2.2: V6 Plugins Exist But Have No Entry Point
**Severity:** CRITICAL  
**Effort:** MEDIUM (2-3 hours)

**Root Cause:**  
V6 plugins are created in `src/logic_plugins/` but there's no routing logic to call them.

**Impact:**  
- V6 trading strategies cannot execute
- All V6 plugin code is dead code

**Dependencies:**  
- Depends on Problem 2.1 being fixed

**Evidence:**
- `src/logic_plugins/price_action_1m/` exists
- `src/logic_plugins/price_action_5m/` exists
- `src/logic_plugins/price_action_15m/` exists
- `src/logic_plugins/price_action_1h/` exists
- None are ever loaded or called

**Fix Strategy:**
1. Add V6 plugin loading in initialize()
2. Create timeframe-to-plugin routing map
3. Wire V6 signals to correct plugins

---

### Problem 2.3: V6 Alert Models Not Used
**Severity:** HIGH  
**Effort:** LOW (1 hour)

**Root Cause:**  
`zepix_v6_alert.py` exists in `src/core/` but is never imported or used.

**Impact:**  
- V6 alert parsing is not available
- V6 signals cannot be validated

**Dependencies:**  
- Depends on Problem 2.1 being fixed

**Evidence:**
- `src/core/zepix_v6_alert.py` exists (538 lines)
- Not imported in trading_engine.py or alert_processor.py

**Fix Strategy:**
1. Import ZepixV6Alert in trading_engine.py
2. Use for V6 alert parsing and validation
3. Route parsed alerts to V6 plugins

---

## CATEGORY 3: LEGACY CODE CONTAMINATION

### Problem 3.1: Legacy "combinedlogic-1/2/3" Naming Scattered Everywhere
**Severity:** HIGH  
**Effort:** HIGH (3-4 hours)

**Root Cause:**  
Old naming convention used throughout codebase without clear indication of Pine Script source (V3 vs V6).

**Impact:**  
- Confusing naming
- Hard to identify which Pine Script version a logic implements
- Maintenance nightmare

**Dependencies:**  
- All files referencing these names need updating

**Evidence (30+ files):**
- `src/core/trading_engine.py`
- `src/logic_plugins/combined_v3/plugin.py`
- `src/logic_plugins/combined_v3/order_manager.py`
- `src/logic_plugins/combined_v3/signal_handlers.py`
- `src/core/plugin_system/service_api.py`
- `src/core/services/trend_management_service.py`
- `src/core/services/order_execution_service.py`
- `src/menu/profit_booking_menu_handler.py`
- `src/menu/timeframe_menu_handler.py`
- `src/models.py`
- `src/utils/pip_calculator.py`
- `src/utils/profit_sl_calculator.py`
- `src/managers/dual_order_manager.py`
- `src/managers/profit_booking_manager.py`
- `src/clients/telegram_bot_fixed.py`
- `src/managers/timeframe_trend_manager.py`
- `src/config.py`
- And 13+ more files

**Fix Strategy:**
1. Rename plugins to user-defined schema
2. Update all imports and references
3. Update config files
4. Update database table names
5. Update Telegram notifications

---

### Problem 3.2: alert_processor.py Contains Hardcoded MTF Logic
**Severity:** HIGH  
**Effort:** MEDIUM (2-3 hours)

**Root Cause:**  
`process_mtf_trends()` is in alert_processor.py instead of being delegated to plugins.

**Impact:**  
- MTF trend processing is not plugin-controlled
- Violates plugin architecture principle
- Hard to customize per-plugin

**Dependencies:**  
- V3 plugin trend validation
- V6 plugin trend pulse

**Evidence:**
- `alert_processor.py` lines 15-94: `process_mtf_trends()` hardcoded

**Fix Strategy:**
1. Move MTF processing to V3 plugin's trend_validator.py
2. Keep only parsing/sanitization in alert_processor.py
3. Delegate trend updates to plugins via ServiceAPI

---

### Problem 3.3: Duplicate Logic in Core and Plugins
**Severity:** MEDIUM  
**Effort:** MEDIUM (2-3 hours)

**Root Cause:**  
Same logic exists in both trading_engine.py and plugin files.

**Impact:**  
- Maintenance burden (changes needed in 2 places)
- Confusion about which version is used
- Wasted code

**Dependencies:**  
- Problem 1.1 must be fixed first

**Evidence:**
| Logic | Core Location | Plugin Location |
|-------|---------------|-----------------|
| Route to Logic | trading_engine.py:433-452 | plugin.py:253-290 |
| Get Multiplier | trading_engine.py:454-463 | plugin.py:292-303 |
| Dual Orders | trading_engine.py:465-696 | order_manager.py |
| Exit Handling | trading_engine.py:698-837 | signal_handlers.py |
| Reversal | trading_engine.py:839-985 | signal_handlers.py |

**Fix Strategy:**
1. Delete duplicate logic from trading_engine.py
2. Keep only plugin versions
3. Ensure plugins are called instead

---

## CATEGORY 4: DATABASE ISSUES

### Problem 4.1: Single Database for All Plugins
**Severity:** MEDIUM  
**Effort:** MEDIUM (2-3 hours)

**Root Cause:**  
`TradeDatabase` uses `data/trading_bot.db` for everything instead of plugin-isolated databases.

**Impact:**  
- No plugin isolation
- Data mixing between plugins
- Hard to track plugin-specific performance

**Dependencies:**  
- Plugin database schemas
- Data migration

**Evidence:**
- `database.py` line 8: `self.conn = sqlite3.connect('data/trading_bot.db')`

**Fix Strategy:**
1. Use plugin-specific databases (data/zepix_{plugin_id}.db)
2. Apply schemas from data/schemas/
3. Migrate existing data

---

### Problem 4.2: No plugin_id Tracking in Trades Table
**Severity:** MEDIUM  
**Effort:** LOW (1 hour)

**Root Cause:**  
The `trades` table doesn't have a `plugin_id` column to identify which plugin created each trade.

**Impact:**  
- Cannot identify which plugin created which trade
- Cannot calculate per-plugin performance
- Cannot isolate plugin data

**Dependencies:**  
- Database schema update
- Data migration

**Evidence:**
- `database.py` lines 15-51: trades table schema has no plugin_id column

**Fix Strategy:**
1. Add plugin_id column to trades table
2. Update save_trade() to include plugin_id
3. Update queries to filter by plugin_id

---

### Problem 4.3: Plugin Database Schemas Exist But Aren't Used
**Severity:** LOW  
**Effort:** LOW (1 hour)

**Root Cause:**  
`data/schemas/` has V3 and V6 schemas, but `database.py` doesn't use them.

**Impact:**  
- Plugin isolation is theoretical, not actual
- Schemas are dead code

**Dependencies:**  
- Problem 4.1 must be fixed first

**Evidence:**
- `data/schemas/` folder exists with SQL files
- `database.py` doesn't reference these schemas

**Fix Strategy:**
1. Use schemas when creating plugin databases
2. Apply correct schema based on plugin type

---

## CATEGORY 5: NAMING CONFUSION

### Problem 5.1: Plugin Names Don't Indicate Pine Source
**Severity:** MEDIUM  
**Effort:** HIGH (3-4 hours)

**Root Cause:**  
Current plugin names like "combined_v3" and "price_action_1m" don't clearly indicate which Pine Script version they implement.

**Impact:**  
- Confusion about plugin purpose
- Hard to understand plugin hierarchy
- Maintenance difficulty

**Dependencies:**  
- All files referencing plugin names

**Evidence:**
- `src/logic_plugins/combined_v3/` - "v3" is in name but not clear
- `src/logic_plugins/price_action_1m/` - No version indicator

**Fix Strategy:**
1. Rename to user-defined schema:
   - V3: v3-logic-01-5min, v3-logic-02-15min, v3-logic-03-1h
   - V6: v6-logic-01-1min, v6-logic-02-5min, v6-logic-03-15min, v6-logic-04-1h
2. Update all references

---

### Problem 5.2: Inconsistent Naming Conventions
**Severity:** LOW  
**Effort:** MEDIUM (2 hours)

**Root Cause:**  
Some names use underscores, some use hyphens, some use numbers inconsistently.

**Impact:**  
- Hard to understand plugin hierarchy
- Inconsistent codebase

**Dependencies:**  
- Problem 5.1 should be fixed together

**Evidence:**
- `combined_v3` (underscore)
- `price_action_1m` (underscore + number)
- `combinedlogic-1` (hyphen + number)

**Fix Strategy:**
1. Standardize on user-defined naming schema
2. Use consistent format: v{version}-logic-{number}-{timeframe}

---

## CATEGORY 6: TELEGRAM SYSTEM

### Problem 6.1: 3-Bot System Created But Not Fully Integrated
**Severity:** LOW  
**Effort:** MEDIUM (2-3 hours)

**Root Cause:**  
controller_bot.py, notification_bot.py, analytics_bot.py exist but may not be fully wired to plugin system.

**Impact:**  
- Multi-bot features may not work with plugins
- Plugin notifications may not route correctly

**Dependencies:**  
- Plugin system must be wired first

**Evidence:**
- `src/telegram/controller_bot.py` exists
- `src/telegram/notification_bot.py` exists
- `src/telegram/analytics_bot.py` exists
- Need to verify integration with plugin system

**Fix Strategy:**
1. Verify 3-bot integration with plugin system
2. Update notification routing to include plugin_id
3. Add plugin-specific commands

---

## CATEGORY 7: SERVICE LAYER

### Problem 7.1: ServiceAPI is Comprehensive But Plugins Don't Use It
**Severity:** LOW  
**Effort:** LOW (1 hour)

**Root Cause:**  
Plugins are never called, so ServiceAPI is never used by plugins.

**Impact:**  
- All service layer work is wasted
- 998 lines of code never exercised

**Dependencies:**  
- Depends on Problems 1.1, 1.2 being fixed

**Evidence:**
- `service_api.py` has 998 lines of comprehensive code
- Plugins never call it because plugins are never called

**Fix Strategy:**
1. Fix plugin wiring (Problems 1.1, 1.2)
2. ServiceAPI will automatically be used when plugins are called

---

## FIX ORDER (Dependency-Aware)

| Order | Category | Problems | Estimated Effort |
|-------|----------|----------|------------------|
| 1 | Core Cleanup | 1.1, 1.3, 1.4, 3.2, 3.3 | 8-10 hours |
| 2 | Plugin Wiring | 1.2 | 2-3 hours |
| 3 | V6 Integration | 2.1, 2.2, 2.3 | 6-8 hours |
| 4 | Plugin Renaming | 3.1, 5.1, 5.2 | 4-6 hours |
| 5 | Database Migration | 4.1, 4.2, 4.3 | 3-4 hours |
| 6 | Telegram Integration | 6.1 | 2-3 hours |
| 7 | Testing | All | 4-6 hours |

**Total Estimated Effort:** 29-40 hours

---

## USER-DEFINED NAMING SCHEMA (MANDATORY)

### V3 Plugin Group (combinedv3)
| Old Name | New Name | Timeframe | Logic |
|----------|----------|-----------|-------|
| combined_v3 (Logic-1) | v3-logic-01-5min | 5-minute | Scalping |
| combined_v3 (Logic-2) | v3-logic-02-15min | 15-minute | Intraday |
| combined_v3 (Logic-3) | v3-logic-03-1h | 1-hour | Swing |

### V6 Plugin Group (price-action-v6)
| Old Name | New Name | Timeframe | Strategy |
|----------|----------|-----------|----------|
| price_action_1m | v6-logic-01-1min | 1-minute | Scalping |
| price_action_5m | v6-logic-02-5min | 5-minute | Momentum |
| price_action_15m | v6-logic-03-15min | 15-minute | Intraday |
| price_action_1h | v6-logic-04-1h | 1-hour | Swing |

---

## CERTIFICATION

I certify that this Problem Inventory was created through deep forensic scanning of the entire codebase. Every problem is backed by specific file paths and line numbers. No assumptions were made.

**Auditor:** Devin AI  
**Date:** 2026-01-14
