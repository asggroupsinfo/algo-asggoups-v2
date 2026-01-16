# BRUTAL TRUTH WIRING AUDIT - V5 Hybrid Plugin Architecture

**Audit Date:** 2026-01-14  
**Auditor:** Devin AI  
**Audit Type:** Deep Forensic Scan - Zero Tolerance  
**Verdict:** CRITICAL FAILURE - WIRING IS MISSING

---

## EXECUTIVE SUMMARY

**THE USER IS 100% CORRECT.**

The V5 Hybrid Plugin Architecture is **GHOST CODE**. The plugins exist, they load, but they are **NEVER ACTUALLY USED** for trading decisions. The core `trading_engine.py` still contains ALL the hardcoded V3 logic and processes signals directly.

**Implementation Status:** SUPERFICIAL UPDATE (Files exist but are not wired)

---

## PART 1: THE "LEGACY CODE" FINDINGS

### 1.1 trading_engine.py - STILL CONTAINS HARDCODED V3 LOGIC

**File:** `src/core/trading_engine.py` (2072 lines)

| Line Range | Function | Status | Evidence |
|------------|----------|--------|----------|
| 208-233 | process_alert() | HARDCODED | Directly calls `execute_v3_entry()` instead of plugin |
| 236-242 | process_alert() | HARDCODED | Directly calls `handle_v3_exit()` instead of plugin |
| 244-253 | process_alert() | HARDCODED | Directly handles squeeze_v3 |
| 255-259 | process_alert() | HARDCODED | Directly handles trend_pulse_v3 |
| 367-431 | execute_v3_entry() | HARDCODED | Complete V3 entry logic (should be in plugin) |
| 433-452 | _route_v3_to_logic() | HARDCODED | Routing logic (duplicated in plugin) |
| 454-463 | _get_logic_multiplier() | HARDCODED | Multiplier logic (duplicated in plugin) |
| 465-696 | _place_hybrid_dual_orders_v3() | HARDCODED | Dual order placement (duplicated in plugin) |
| 698-837 | handle_v3_exit() | HARDCODED | Exit handling (should be in plugin) |
| 839-985 | handle_v3_reversal() | HARDCODED | Reversal handling (should be in plugin) |

**SMOKING GUN - Line 232:**
```python
# WHAT THE CODE DOES:
if alert_type == "entry_v3":
    result = await self.execute_v3_entry(v3_alert)  # HARDCODED!
    return result.get("status") == "success"

# WHAT IT SHOULD DO:
if alert_type == "entry_v3":
    result = await self.plugin_registry.route_alert_to_plugin(v3_alert, "combined_v3")
    return result.get("status") == "success"
```

### 1.2 alert_processor.py - ALSO CONTAINS HARDCODED LOGIC

**File:** `src/processors/alert_processor.py` (266 lines)

| Line Range | Function | Status | Evidence |
|------------|----------|--------|----------|
| 15-94 | process_mtf_trends() | HARDCODED | MTF trend processing (should be in plugin) |
| 96-134 | validate_v3_alert() | HARDCODED | V3 validation (should be in plugin) |
| 136-150 | validate_alert() | HARDCODED | Alert routing (should delegate to plugin) |

### 1.3 Logic Control Flags - STILL IN CORE

**File:** `src/core/trading_engine.py` (Lines 101-104)
```python
# Logic control flags - SHOULD BE IN PLUGIN CONFIG
self.combinedlogic_1_enabled = True
self.combinedlogic_2_enabled = True
self.combinedlogic_3_enabled = True
```

---

## PART 2: THE LOGIC MATCH REPORT

### 2.1 V3 Pine Script vs Plugin Code

**Source:** `ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine`

| V3 Feature | Pine Script | Plugin Code | Core Code | Actually Used |
|------------|-------------|-------------|-----------|---------------|
| 12 Signal Types | YES | YES (plugin.py:93-106) | YES (trading_engine.py) | CORE |
| 2-Tier Routing | YES | YES (plugin.py:253-290) | YES (trading_engine.py:433-452) | CORE |
| Dual Orders | YES | YES (order_manager.py) | YES (trading_engine.py:465-696) | CORE |
| MTF 4-Pillar | YES | YES (trend_validator.py) | YES (alert_processor.py:15-94) | CORE |
| Logic Multipliers | YES | YES (plugin.py:292-303) | YES (trading_engine.py:454-463) | CORE |

**VERDICT:** The plugin code is a DUPLICATE of the core code. Both exist, but only the CORE version is actually executed.

### 2.2 V6 Pine Script vs Plugin Code

**Source:** `Signals_and_Overlays_V6_Enhanced_Build.pine`

| V6 Feature | Pine Script | Plugin Code | Core Code | Actually Used |
|------------|-------------|-------------|-----------|---------------|
| V6 Alert Parsing | YES | YES (zepix_v6_alert.py) | NO | NEVER |
| Trend Pulse | YES | YES (trend_pulse_manager.py) | NO | NEVER |
| ADX Filters | YES | YES (price_action_*.py) | NO | NEVER |
| Spread Checks | YES | YES (price_action_*.py) | NO | NEVER |
| Conditional Orders | YES | YES (price_action_*.py) | NO | NEVER |

**VERDICT:** V6 plugins exist but are COMPLETELY UNUSED. The core has NO V6 handling code, and the plugins are never called.

---

## PART 3: THE CONNECTION TEST

### 3.1 Data Flow Analysis

**Expected Flow (Plugin Architecture):**
```
Webhook -> process_alert() -> plugin_registry.route_alert_to_plugin() -> Plugin.process_entry_signal() -> ServiceAPI -> MT5
```

**Actual Flow (Current Implementation):**
```
Webhook -> process_alert() -> execute_v3_entry() [HARDCODED] -> MT5
                           -> plugin_registry.execute_hook() [ONLY MODIFIES DATA, DOESN'T PROCESS]
```

### 3.2 Plugin Hook Analysis

**File:** `src/core/trading_engine.py` (Lines 187-202)

```python
# PLUGIN HOOK: on_signal_received
# Allow plugins to modify or reject the signal
if self.config.get("plugin_system", {}).get("enabled", True):
    modified_data = await self.plugin_registry.execute_hook("signal_received", data)
    if modified_data is False:
        logger.info("Signal rejected by a plugin hook 'on_signal_received'.")
        return False
    if modified_data and isinstance(modified_data, dict):
        data = modified_data

# AFTER THIS, THE CORE STILL PROCESSES THE SIGNAL DIRECTLY!
# The plugin hook only allows modification, NOT execution.
```

**VERDICT:** The plugin hook is a FILTER, not a PROCESSOR. The actual trading logic is still hardcoded in the core.

### 3.3 Plugin Registry Analysis

**File:** `src/core/plugin_system/plugin_registry.py`

| Method | Purpose | Called From Core? |
|--------|---------|-------------------|
| discover_plugins() | Find plugins | YES (initialize) |
| load_all_plugins() | Load plugins | YES (initialize) |
| execute_hook() | Run hooks | YES (process_alert) |
| route_alert_to_plugin() | Delegate to plugin | **NO - NEVER CALLED** |

**SMOKING GUN:** The `route_alert_to_plugin()` method exists (lines 132-171) but is **NEVER CALLED** from trading_engine.py.

---

## PART 4: NAMING PROPOSAL

### 4.1 Current Names (Confusing)

```
src/logic_plugins/
  combined_v3/          # What does "combined" mean?
  price_action_1m/      # V6? Not clear
  price_action_5m/      # V6? Not clear
  price_action_15m/     # V6? Not clear
  price_action_1h/      # V6? Not clear
```

### 4.2 Proposed New Names (Clear)

**Structure:** `{pine_version}_{logic_type}_{sequence}`

```
src/logic_plugins/
  # V3 Group (Pine Script V3 - Combined Logics)
  v3_combined/          # Main V3 plugin (all 12 signals)
  
  # V6 Group (Pine Script V6 - Price Action)
  v6_scalp_1m/          # 1-Minute Scalping (ORDER_B_ONLY)
  v6_momentum_5m/       # 5-Minute Momentum (DUAL_ORDERS)
  v6_intraday_15m/      # 15-Minute Intraday (ORDER_A_ONLY)
  v6_swing_1h/          # 1-Hour Swing (ORDER_A_ONLY)
```

**Alternative (Sequential Numbering):**

```
src/logic_plugins/
  # V3 Group
  v3_logic_01/          # Combined V3 (all signals)
  
  # V6 Group
  v6_logic_01_1m/       # Scalping
  v6_logic_02_5m/       # Momentum
  v6_logic_03_15m/      # Intraday
  v6_logic_04_1h/       # Swing
```

---

## PART 5: REQUIRED FIXES

### 5.1 Critical Fixes (Must Do)

1. **Remove hardcoded V3 logic from trading_engine.py:**
   - Delete `execute_v3_entry()` (lines 367-431)
   - Delete `_route_v3_to_logic()` (lines 433-452)
   - Delete `_get_logic_multiplier()` (lines 454-463)
   - Delete `_place_hybrid_dual_orders_v3()` (lines 465-696)
   - Delete `handle_v3_exit()` (lines 698-837)
   - Delete `handle_v3_reversal()` (lines 839-985)

2. **Wire process_alert() to plugins:**
   ```python
   # Replace hardcoded logic with plugin delegation:
   if alert_type == "entry_v3":
       result = await self.plugin_registry.route_alert_to_plugin(v3_alert, "combined_v3")
       return result.get("status") == "success"
   ```

3. **Add V6 routing to process_alert():**
   ```python
   if alert_type == "entry_v6":
       # Determine which V6 plugin based on timeframe
       plugin_id = self._get_v6_plugin_for_timeframe(alert.tf)
       result = await self.plugin_registry.route_alert_to_plugin(alert, plugin_id)
       return result.get("status") == "success"
   ```

4. **Remove hardcoded MTF logic from alert_processor.py:**
   - Move `process_mtf_trends()` to plugin
   - Move `validate_v3_alert()` to plugin

### 5.2 Architecture Principle

**The Core Should:**
- Route data to plugins
- Execute plugin decisions
- Manage lifecycle

**The Core Should NOT:**
- Contain trading logic
- Make routing decisions based on signal type
- Calculate lot sizes or SL/TP

---

## FINAL VERDICT

### Status: CRITICAL FAILURE

| Criteria | Expected | Actual | Status |
|----------|----------|--------|--------|
| Core contains ZERO business logic | YES | NO | FAIL |
| Plugins process all signals | YES | NO | FAIL |
| route_alert_to_plugin() is called | YES | NO | FAIL |
| V6 signals are handled | YES | NO | FAIL |
| Data flows through plugins | YES | NO | FAIL |

### The User's Suspicion is CONFIRMED

The V5 Hybrid Plugin Architecture update was a **SUPERFICIAL UPDATE**:
- New plugin files were created
- But the core was NOT updated to use them
- The "wiring" is completely missing
- The plugins are "ghost code" sitting unused

### Recommendation

**DO NOT deploy this as-is.** The plugin system is non-functional. A complete rewiring of `trading_engine.py` is required to actually delegate signal processing to the plugins.

---

## AUDIT CERTIFICATION

I certify that this audit was conducted with ZERO TOLERANCE for assumptions. Every finding is backed by specific file paths and line numbers. The user's suspicion about "missing wiring" is 100% CONFIRMED.

**Auditor:** Devin AI  
**Date:** 2026-01-14  
**Methodology:** Deep forensic scan of all core files and plugin system
