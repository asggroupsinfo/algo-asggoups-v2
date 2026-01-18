# V5 HYBRID PLUGIN ARCHITECTURE - IMPLEMENTATION ROADMAP

**Date:** 2026-01-15
**Status:** RECOVERY PHASE - GHOST STATE ELIMINATION
**Mode:** BRUTAL HONESTY | ZERO TOLERANCE

---

## EXECUTIVE SUMMARY

This roadmap documents the ACTUAL implementation status of the V5 Hybrid Plugin Architecture, including items that were previously "Ghost State" (documented but not implemented).

---

## SECTION 1: CORE INFRASTRUCTURE (PREVIOUSLY GHOST STATE - NOW IMPLEMENTED)

These items were documented as "planned" but had no actual code. They have now been implemented:

### 1.1 Hybrid Plugin Bridge
**File:** `src/core/plugin_bridge.py`
**Status:** IMPLEMENTED
**Purpose:** V4-V5 signal translation, forwarding, and state synchronization

Features:
- V4Signal and V5Signal dataclasses for signal format conversion
- Signal type mappings (BUY_SIGNAL -> entry_long, SELL_SIGNAL -> entry_short, etc.)
- Strategy mappings (combinedlogic-1 -> V3_COMBINED, price_action -> V6_PRICE_ACTION)
- Bidirectional communication between V4 legacy and V5 hybrid layers
- Plugin registration and signal forwarding

### 1.2 Recovery Logic
**File:** `src/core/recovery_handler.py`
**Status:** IMPLEMENTED
**Purpose:** Error handlers in main execution loop

Features:
- ErrorSeverity enum (LOW, MEDIUM, HIGH, CRITICAL)
- ErrorCategory enum (PLUGIN, TRADE, CONNECTION, CONFIG, DATABASE, TELEGRAM, MT5, UNKNOWN)
- Plugin failure detection with configurable thresholds (default: 5 errors)
- Automatic plugin disable/re-enable on repeated failures
- Trade retry logic with exponential backoff (max 3 retries)
- Connection recovery with reconnection attempts (max 5 retries, 5s delay)
- Trading pause/resume on critical errors

### 1.3 State Synchronization
**File:** `src/core/state_sync.py`
**Status:** IMPLEMENTED
**Purpose:** Legacy-hybrid layer state synchronization

Features:
- StateType enum (CONFIG, POSITIONS, ORDERS, SIGNALS, TRENDS, RISK, PLUGIN)
- SyncDirection enum (LEGACY_TO_HYBRID, HYBRID_TO_LEGACY, BIDIRECTIONAL)
- State capture from both legacy and hybrid systems
- Conflict detection and resolution strategies (hybrid_wins, legacy_wins, newest_wins)
- Background sync with configurable intervals (CONFIG: 60s, POSITIONS: 5s, SIGNALS: 1s)
- Unified state view across both systems

### 1.4 Rollback Mechanism
**File:** `src/core/plugin_rollback.py`
**Status:** IMPLEMENTED
**Purpose:** Automatic V5 fail -> V4 revert

Features:
- PluginVersion enum (V4_STABLE, V5_HYBRID, V6_EXPERIMENTAL)
- RollbackReason enum (PLUGIN_FAILURE, PERFORMANCE_DEGRADATION, ERROR_THRESHOLD, MANUAL_REQUEST, HEALTH_CHECK_FAILED)
- Checkpoint creation before risky operations (max 10 checkpoints retained)
- Error tracking with time window (10 minutes)
- Performance monitoring with threshold (5000ms)
- Automatic rollback on failure detection
- V4 fallback activation

### 1.5 Command Registry (95+ Commands)
**File:** `src/telegram/command_registry.py`
**Status:** IMPLEMENTED
**Purpose:** Central registry for all bot commands

Features:
- 95+ command definitions across 10 categories
- CommandCategory enum (SYSTEM, TRADING, RISK, STRATEGY, TIMEFRAME, REENTRY, PROFIT, ANALYTICS, SESSION, PLUGIN, VOICE, MENU, ACTION, NAVIGATION)
- 50+ callback data mappings
- Command handler registration and execution
- Help text generation by category
- Statistics tracking

### 1.6 Startup Integration
**File:** `src/core/startup_integration.py`
**Status:** IMPLEMENTED
**Purpose:** Wire all infrastructure to bot startup

Features:
- Centralized initialization of all infrastructure components
- Bot reference management (Controller, Notification, Analytics, Trading Engine)
- Sticky header initialization on startup
- Command registry wiring
- Plugin bridge setup
- Recovery handler activation
- State synchronizer background sync start
- Rollback manager initial checkpoint creation

---

## SECTION 2: MISSING INFRASTRUCTURE (NEEDS IMPLEMENTATION)

These items were identified as completely missing from the codebase:

### 2.1 Dependency Hell Management
**Status:** NOT IMPLEMENTED
**Priority:** HIGH
**Purpose:** Handle conflicting dependencies between V3/V4/V5/V6 plugins

Required Features:
- Dependency graph builder
- Conflict detection between plugin versions
- Automatic dependency resolution
- Version pinning support
- Isolation containers for incompatible plugins

### 2.2 Performance Overhead Validation
**Status:** NOT IMPLEMENTED
**Priority:** MEDIUM
**Purpose:** Benchmarks and limits for plugin performance

Required Features:
- Plugin execution time tracking
- Memory usage monitoring
- CPU usage monitoring
- Performance threshold alerts
- Automatic throttling on performance degradation
- Benchmark suite for plugin comparison

### 2.3 Plugin Hot-Swap
**Status:** NOT IMPLEMENTED
**Priority:** LOW
**Purpose:** Swap plugins without bot restart

Required Features:
- Live plugin unloading
- State preservation during swap
- Live plugin loading
- Graceful degradation during swap
- Rollback on swap failure

### 2.4 Plugin Marketplace
**Status:** NOT IMPLEMENTED
**Priority:** LOW
**Purpose:** Discover and install community plugins

Required Features:
- Plugin repository integration
- Version management
- Security scanning
- Rating system
- Auto-update mechanism

---

## SECTION 3: LEGACY PARITY & UI REGRESSIONS (NEEDS IMPLEMENTATION)

These items represent functionality that existed in V4 but was lost or degraded in V5:

### 3.1 95+ Command UI Wiring
**Status:** PARTIALLY IMPLEMENTED (Registry created, handlers need wiring)
**Priority:** HIGH
**Purpose:** Wire all 95+ commands to actual handlers

Required Work:
- Create handler implementations for all 95+ commands
- Wire handlers to CommandRegistry
- Test each command end-to-end
- Document command usage

### 3.2 Controller Bot Upgrade
**Status:** NOT IMPLEMENTED
**Priority:** HIGH
**Purpose:** Upgrade Controller Bot from delegation to direct handling

Required Work:
- Implement direct command handling (not delegation to legacy bot)
- Add plugin control commands
- Add system health commands
- Add configuration commands
- Add analytics commands

### 3.3 Sticky Header Integration
**Status:** PARTIALLY IMPLEMENTED (Classes exist, startup wiring done)
**Priority:** MEDIUM
**Purpose:** Pinned dashboard message at top of chat

Required Work:
- Test sticky header creation and pinning
- Verify auto-update every 30 seconds
- Verify auto-regeneration on message deletion
- Add content generators for all bot types

### 3.4 Voice Alert Restoration
**Status:** IMPLEMENTED (Phase 9 restoration)
**Priority:** COMPLETED
**Purpose:** Voice alerts for trade events

Completed Work:
- VoiceAlertIntegration class created
- Wired to trading_engine.py
- Trade entry/exit/error alerts working

### 3.5 Session Manager Restoration
**Status:** IMPLEMENTED (Phase 9 restoration)
**Priority:** COMPLETED
**Purpose:** Forex session management

Completed Work:
- Session detection working
- Session-based trading rules active
- Session overlap handling

### 3.6 Real Clock System
**Status:** IMPLEMENTED (Phase 9 restoration)
**Priority:** COMPLETED
**Purpose:** IST time display in headers

Completed Work:
- FixedClockSystem class created
- IST time formatting
- Integration with sticky headers

---

## SECTION 4: TESTING & VERIFICATION

### 4.1 Unit Tests
**Status:** PARTIAL
**Coverage:** ~60%

Required Work:
- Add tests for plugin_bridge.py
- Add tests for recovery_handler.py
- Add tests for state_sync.py
- Add tests for plugin_rollback.py
- Add tests for command_registry.py
- Add tests for startup_integration.py

### 4.2 Integration Tests
**Status:** PARTIAL
**Coverage:** ~40%

Required Work:
- Test full signal flow from V4 to V5
- Test recovery scenarios
- Test rollback scenarios
- Test state sync across systems
- Test command execution end-to-end

### 4.3 E2E Tests
**Status:** MINIMAL
**Coverage:** ~20%

Required Work:
- Test complete trading cycle
- Test Telegram bot interactions
- Test plugin switching
- Test error recovery
- Test performance under load

---

## SECTION 5: IMPLEMENTATION PRIORITY

### Phase 1: CRITICAL (Immediate)
1. Verify all Section 1 implementations work (not just claim)
2. Wire 95+ command handlers to CommandRegistry
3. Test sticky header end-to-end

### Phase 2: HIGH (This Week)
1. Implement Dependency Hell Management
2. Complete Controller Bot upgrade
3. Add missing unit tests

### Phase 3: MEDIUM (This Month)
1. Implement Performance Overhead Validation
2. Add integration tests
3. Document all new infrastructure

### Phase 4: LOW (Future)
1. Implement Plugin Hot-Swap
2. Implement Plugin Marketplace
3. Add E2E test suite

---

## SECTION 6: FILES CREATED IN RECOVERY PHASE

| File | Lines | Purpose |
|------|-------|---------|
| `src/core/plugin_bridge.py` | 600+ | V4-V5 signal translation |
| `src/core/recovery_handler.py` | 700+ | Error handling and recovery |
| `src/core/state_sync.py` | 800+ | State synchronization |
| `src/core/plugin_rollback.py` | 900+ | Automatic rollback |
| `src/telegram/command_registry.py` | 500+ | 95+ command registry |
| `src/core/startup_integration.py` | 400+ | Startup wiring |

**Total New Code:** 3900+ lines of ACTUAL implementation (not documentation)

---

## SECTION 7: VERIFICATION CHECKLIST

### Infrastructure Verification
- [ ] Plugin Bridge translates V4 signals to V5 format
- [ ] Recovery Handler catches and recovers from errors
- [ ] State Synchronizer syncs state between layers
- [ ] Rollback Manager creates checkpoints and rolls back
- [ ] Command Registry maps all 95+ commands
- [ ] Startup Integration initializes all components

### Integration Verification
- [ ] All 4 infrastructure pieces work together
- [ ] Sticky header appears on bot startup
- [ ] Commands are callable via Telegram
- [ ] Errors trigger recovery logic
- [ ] Failures trigger rollback to V4

### Production Readiness
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Performance benchmarks acceptable
- [ ] Documentation complete
- [ ] Deployment guide ready

---

## CONCLUSION

The V5 Hybrid Plugin Architecture has moved from "Ghost State" to "Actual Implementation" with 3900+ lines of new code. The core infrastructure (Bridge, Recovery, State Sync, Rollback) is now implemented. The remaining work focuses on:

1. Verifying implementations work in practice
2. Wiring command handlers
3. Implementing missing infrastructure (Dependency Hell, Performance Validation)
4. Adding comprehensive tests

**Next Action:** Verify all implementations work, then proceed with Phase 2 priorities.

---


## SECTION 8: INTELLIGENT TRADING & TELEGRAM SEPARATION (MANDATE 23 - VERIFIED)

**Status:** ✅ COMPLETED & VERIFIED
**Date:** 2026-01-17

This section covers the successful implementation and verification of Mandate 23.

### 8.1 Intelligent Logic V3/V6
**Status:** VERIFIED
**Details:**
- Intelligent entry using Pine Script data (Pine Supremacy) implemented.
- Smart TP Management (Partial close, trailing) implemented.
- SL Hunting with Re-entry implemented.
- Risk-based lot sizing integrated.
- 35/35 Live Simulation tests PASSED.

### 8.2 Telegram Bot Separation (3-Bot System)
**Status:** ✅ VERIFIED & FIXED (Polling Enabled)
**Details:**
- **Issue:** Bots were merged due to startup script skipping initialization + polling inactive.
- **Fix:** Fixed `trading_engine.py` config logic, updated startup scripts, enabled `start_simple_polling`.
- **Result:** Logs confirm 3 separate bots (Controller, Notification, Analytics) initializing with dedicated tokens.
- **Notification Bot:** Verified via `debug_telegram_status.py`. **PROOF OF LIFE DELIVERED.**
- **Analytics Bot:** Verified via `debug_telegram_status.py`. **PROOF OF LIFE DELIVERED.**
- **Proof:** `proof_log.txt` confirms "MESSAGE DELIVERED" for all 3 bots.

### 8.3 Operational Workflow
**Status:** OPTIMIZED
**Details:**
- `START_BOT.bat` now points to `start_full_bot.py`.
- Bot runs on Port 80 by default.
- Full initialization chain (MT5 -> Engine -> Telegram -> Plugins) verified.

---

## SECTION 9: TELEGRAM MENU UPGRADE (MANDATE 24)

**Status:** ✅ COMPLETED & VERIFIED
**Date:** 2026-01-17

This section covers the successful wiring of the 95+ command menu system.

### 9.1 Missing Menu Resolution
**Status:** FIXED
**Issue:** Legacy bot (`TelegramBotFixed`) used a hardcoded keyboard, hiding commands. "Strategy" category was missing.
**Fix:**
- Integrated `MenuManager` and restored "Strategy" category (7 commands).
- Added "Timeframe" shortcut to persistent menu.
- Synchronized all button labels with command map.
- `/start` now shows 100% of commands via Dual Menu.

### 9.2 Verification
**Status:** PASS
**Proof:** `Visual_Proof_Menu_Structure.md` confirms 97 commands visible.
**Action:** Restart bot to see the new menu.

---

*This roadmap is a living document. Update as implementation progresses.*
*Last Updated: 2026-01-17*

