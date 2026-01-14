# MASTER IMPLEMENTATION PLAN - Part 1 (V5 Hybrid Plugin Architecture)

**Start Date:** 2026-01-14  
**Target Completion:** 2026-02-28 (5-7 weeks)  
**Current Phase:** PART-1 COMPLETE (Master Audit Passed)  
**Document Version:** 3.0

---

## Implementation Progress Overview

| Batch | Name | Status | Impl. | Test | Report | Improvements |
|-------|------|--------|-------|------|--------|--------------|
| 01 | Core Plugin System Foundation | PASSED | [x] | [x] | [x] | [x] |
| 02 | Multi-Database Schema Design | PASSED | [x] | [x] | [x] | [x] |
| 03 | ServiceAPI Implementation | PASSED | [x] | [x] | [x] | [x] |
| 04 | 3-Bot Telegram Architecture | PASSED | [x] | [x] | [x] | [x] |
| 05 | Telegram UX & Rate Limiting | PASSED | [x] | [x] | [x] | [x] |
| 06 | Sticky Header & Notification Router | PASSED | [x] | [x] | [x] | [x] |
| 07 | Shared Service API Layer | PASSED | [x] | [x] | [x] | [x] |
| 08 | V3 Combined Logic Plugin | PASSED | [x] | [x] | [x] | [x] |
| 09 | Config Hot-Reload & DB Isolation | PASSED | [x] | [x] | [x] | [x] |
| 10 | V6 Price Action Plugin Foundation | PASSED | [x] | [x] | [x] | [x] |
| 11 | Plugin Health & Versioning | PASSED | [x] | [x] | [x] | [x] |
| 12 | Data Migration & Developer Docs | PASSED | [x] | [x] | [x] | [x] |
| 13 | Code Quality & User Docs | PASSED | [x] | [x] | [x] | [x] |
| 14 | Master Audit (Dashboard Deferred) | PASSED | [x] | [x] | [x] | [x] |

**Legend:**
- PENDING: Not started
- IN_PROGRESS: Currently being implemented
- TESTING: Implementation complete, testing in progress
- PASSED: All tests passed, ready for next batch
- FAILED: Tests failed, needs fixes
- BLOCKED: Waiting on dependency or external factor

---

## Batch Details

### Batch 01: Core Plugin System Foundation
**Documents:** `01_PROJECT_OVERVIEW.md`, `02_PHASE_1_PLAN.md`  
**Duration:** 3-4 days  
**Risk:** HIGH  
**Dependencies:** None

**Files to Create:**
- `src/core/base_logic_plugin.py` - BaseLogicPlugin abstract class
- `src/core/plugin_registry.py` - PluginRegistry for plugin management
- `src/core/service_api.py` - ServiceAPI facade
- `src/core/plugin_loader.py` - Dynamic plugin loading
- `src/core/plugin_config.py` - Plugin configuration management
- `src/core/plugin_lifecycle.py` - Plugin lifecycle hooks
- `src/core/__init__.py` - Core module exports

**Tests Required:**
- Unit tests for BaseLogicPlugin
- Unit tests for PluginRegistry
- Integration test for plugin loading
- Lifecycle hook tests

**Validation Checklist:**
- [x] BaseLogicPlugin has all required abstract methods
- [x] PluginRegistry can register/unregister plugins
- [x] ServiceAPI provides access to all services
- [x] Plugin lifecycle hooks work correctly
- [x] No impact on existing bot functionality

**Implementation Notes (Batch 01 - COMPLETED 2026-01-14):**
- Plugin system was ALREADY IMPLEMENTED in codebase
- Files exist at: `src/core/plugin_system/` (base_plugin.py, plugin_registry.py, service_api.py)
- Template plugin exists at: `src/logic_plugins/_template/`
- Integration in TradingEngine confirmed (lines 23-24, 106-111, 128-131, 189-202)
- Config has plugin_system section enabled
- Created comprehensive unit tests: `tests/test_plugin_system.py` (39 tests, all passing)
- Test script `scripts/test_plugin.py` verified working

---

### Batch 02: Multi-Database Schema Design
**Documents:** `09_DATABASE_SCHEMA_DESIGNS.md`, `11_CONFIGURATION_TEMPLATES.md`  
**Duration:** 2-3 days  
**Risk:** MEDIUM  
**Dependencies:** Batch 01

**Files to Create:**
- `data/schemas/combined_v3_schema.sql` - V3 database schema
- `data/schemas/price_action_v6_schema.sql` - V6 database schema
- `data/schemas/central_system_schema.sql` - Central database schema
- `config/plugins/combined_v3_config.json` - V3 plugin config
- `config/plugins/price_action_1m_config.json` - V6 1M config
- `config/plugins/price_action_5m_config.json` - V6 5M config
- `config/plugins/price_action_15m_config.json` - V6 15M config
- `config/plugins/price_action_1h_config.json` - V6 1H config

**Tests Required:**
- Schema creation tests
- Config validation tests
- Database isolation tests

**Validation Checklist:**
- [x] All 3 databases can be created independently
- [x] Config templates are valid JSON
- [x] Schemas match planning document specifications
- [x] No conflicts between databases

**Implementation Notes (Batch 02 - COMPLETED 2026-01-14):**
- Created 3 SQL schema files in `data/schemas/`:
  - `combined_v3_schema.sql` - V3 Combined Logic DB (4 tables: combined_v3_trades, v3_profit_bookings, v3_signals_log, v3_daily_stats)
  - `price_action_v6_schema.sql` - V6 Price Action DB (7 tables: price_action_1m/5m/15m/1h_trades, market_trends, v6_signals_log, v6_daily_stats)
  - `central_system_schema.sql` - Central System DB (5 tables: plugins_registry, aggregated_trades, system_config, system_events, sync_status)
- Created 5 JSON config files in `config/plugins/`:
  - `combined_v3_config.json` - V3 plugin with dual order system, MTF 4-pillar, 12 signal types
  - `price_action_1m_config.json` - ORDER_B_ONLY, ADX 20, confidence 80
  - `price_action_5m_config.json` - DUAL_ORDERS, ADX 25, confidence 70
  - `price_action_15m_config.json` - ORDER_A_ONLY, ADX 22, confidence 65
  - `price_action_1h_config.json` - ORDER_A_ONLY, confidence 60
- Created comprehensive unit tests: `tests/test_batch_02_schemas.py` (25 tests, all passing)
- Database isolation verified: V3 and V6 have NO shared application tables
- Central DB pre-populated with 5 plugin entries

---

### Batch 03: ServiceAPI Implementation
**Documents:** `10_API_SPECIFICATIONS.md`, `21_MARKET_DATA_SERVICE_SPECIFICATION.md`  
**Duration:** 3-4 days  
**Risk:** HIGH  
**Dependencies:** Batch 01, Batch 02

**Files to Create/Modify:**
- `src/core/services/order_execution_service.py`
- `src/core/services/risk_management_service.py`
- `src/core/services/trend_management_service.py`
- `src/core/services/profit_booking_service.py`
- `src/core/services/market_data_service.py`

**Tests Required:**
- Unit tests for each service
- Mock MT5 integration tests
- Service API facade tests

**Validation Checklist:**
- [x] OrderExecutionService handles V3 dual orders
- [x] OrderExecutionService handles V6 conditional orders
- [x] MarketDataService provides spread checks
- [x] All services are stateless
- [x] Services integrate with existing bot components

**Implementation Notes (Batch 03 - COMPLETED 2026-01-14):**
- Created 4 stateless service files in `src/core/services/`:
  - `order_execution_service.py` - V3 dual orders (different SLs), V6 conditional orders (Order A/B), V6 dual orders (same SL)
  - `risk_management_service.py` - Lot size calculation, ATR-based SL/TP, daily/lifetime limit checks, trade risk validation
  - `trend_management_service.py` - V3 4-pillar MTF trends, V6 Trend Pulse system, logic alignment validation
  - `market_data_service.py` - Spread checks (critical for V6 1M), price data, volatility analysis, symbol info
- Created `src/core/services/__init__.py` for module exports
- All services are STATELESS - they use passed parameters and external managers for state
- Services wrap existing bot functionality (RiskManager, TimeframeTrendManager, MT5Client)
- Created comprehensive unit tests: `tests/test_batch_03_services.py` (34 tests, all passing)
- Test categories: OrderExecutionService (7), RiskManagementService (7), TrendManagementService (8), MarketDataService (8), Statelessness (4)

---

### Batch 04: 3-Bot Telegram Architecture
**Documents:** `04_PHASE_2_DETAILED_PLAN.md`, `18_TELEGRAM_SYSTEM_ARCHITECTURE.md`  
**Duration:** 3-4 days  
**Risk:** MEDIUM  
**Dependencies:** Batch 01

**Files to Create:**
- `src/telegram/multi_telegram_manager.py`
- `src/telegram/controller_bot.py`
- `src/telegram/notification_bot.py`
- `src/telegram/analytics_bot.py`
- `src/telegram/message_router.py`

**Tests Required:**
- Multi-bot initialization tests
- Message routing tests
- Bot isolation tests

**Validation Checklist:**
- [x] All 3 bots can be initialized
- [x] Messages route to correct bot
- [x] Existing Controller Bot functionality preserved
- [x] No Telegram API rate limit violations

**Implementation Notes (Batch 04 - COMPLETED 2026-01-14):**
- Created 5 new files in `src/telegram/`:
  - `base_telegram_bot.py` - Lightweight base class with send_message, edit_message, send_voice, get_stats
  - `controller_bot.py` - Handles commands, status responses, confirmation requests, legacy bot delegation
  - `notification_bot.py` - Entry/exit alerts, profit booking, error alerts, daily summaries, voice alert integration
  - `analytics_bot.py` - Performance reports, statistics summaries, trade history, trend analysis, plugin performance
  - `message_router.py` - Intelligent routing based on content type, priority detection, fallback handling
- Refactored `multi_telegram_manager.py` (v2.0.0):
  - Fixed broken import from non-existent `src/modules/telegram_bot`
  - Integrated with new specialized bot classes
  - Added graceful degradation to single bot mode
  - Added backward compatibility with existing telegram_bot_fixed.py
  - Added voice alert system integration
  - Added comprehensive stats and monitoring
- Key Features Implemented:
  - 3-Bot System: Controller (commands), Notification (alerts), Analytics (reports)
  - Single Bot Mode: Automatic fallback if only 1 token provided
  - Multi-Bot Mode: Intelligent routing based on message type
  - Message Classification: Commands, alerts, reports, broadcasts
  - Priority Detection: Critical, high, normal, low
  - Backward Compatibility: Legacy bot delegation for existing command handlers
- Created comprehensive unit tests: `tests/test_batch_04_telegram.py` (48 tests, all passing)
- Test categories: BaseTelegramBot (6), ControllerBot (4), NotificationBot (6), AnalyticsBot (5), MessageRouter (11), MultiTelegramManager (8), Integration (4), BackwardCompatibility (4)

---

### Batch 05: Telegram UX & Rate Limiting
**Documents:** `20_TELEGRAM_UNIFIED_INTERFACE_ADDENDUM.md`, `22_TELEGRAM_RATE_LIMITING_SYSTEM.md`  
**Duration:** 2-3 days  
**Risk:** MEDIUM  
**Dependencies:** Batch 04

**Files to Create:**
- `src/telegram/rate_limiter.py`
- `src/telegram/unified_interface.py`
- `src/telegram/menu_builder.py`

**Tests Required:**
- Rate limiting tests
- Queue overflow tests
- Menu synchronization tests

**Validation Checklist:**
- [x] Rate limiter enforces 20 msg/min per bot
- [x] Priority queue works correctly
- [x] Same menus work in all 3 bots
- [x] Zero-typing UI functional

**Implementation Notes (Batch 05 - COMPLETED 2026-01-14):**
- Created 3 new files in `src/telegram/`:
  - `rate_limiter.py` - Token Bucket algorithm with priority queue (CRITICAL > HIGH > NORMAL > LOW)
    - Thread-safe implementation using threading.Lock
    - 20 msg/min per bot, 30 msg/sec hard limit
    - Queue overflow handling (drops LOW priority first)
    - MultiRateLimiter for managing all 3 bots
    - Statistics tracking and health monitoring
  - `unified_interface.py` - Zero-Typing navigation and Live Sticky Headers
    - UnifiedInterfaceManager with REPLY_MENU_MAP for button-to-callback mapping
    - LiveHeaderManager for pinned status messages (updates every 60 seconds)
    - Bot-specific header content (Controller, Notification, Analytics)
    - PANIC CLOSE confirmation flow
    - Data providers for dynamic header content
  - `menu_builder.py` - Dynamic inline keyboard generator
    - MenuBuilder class with navigation stack and context management
    - Pagination support for long lists
    - Parameter selection menus with current value highlighting
    - Toggle menus for on/off features
    - MenuFactory for common menu configurations
- Key Features Implemented:
  - Token Bucket Algorithm: Smooth rate limiting with burst support
  - Priority Queue: 4 levels (CRITICAL, HIGH, NORMAL, LOW)
  - Thread Safety: All operations protected by locks
  - Live Headers: Auto-updating pinned messages with real-time status
  - Zero-Typing UI: All interactions via buttons (no manual typing)
  - Menu Synchronization: Same menus work in all 3 bots
  - Backward Compatibility: Existing REPLY_MENU_MAP patterns preserved
- Created comprehensive unit tests: `tests/test_batch_05_ux.py` (61 tests, all passing)
- Test categories: MessagePriority (2), ThrottledMessage (4), TokenBucket (5), TelegramRateLimiter (7), MultiRateLimiter (4), BotType (1), LiveHeaderManager (6), UnifiedInterfaceManager (11), MenuBuilder (8), MenuFactory (4), ThreadSafety (2), Integration (4), BackwardCompatibility (3)

---

### Batch 06: Sticky Header & Notification Router
**Documents:** `24_STICKY_HEADER_IMPLEMENTATION_GUIDE.md`, `19_NOTIFICATION_SYSTEM_SPECIFICATION.md`  
**Duration:** 2-3 days  
**Risk:** LOW  
**Dependencies:** Batch 04, Batch 05

**Files to Create:**
- `src/telegram/sticky_headers.py`
- `src/telegram/notification_router.py`
- `src/telegram/voice_alert_integration.py`

**Tests Required:**
- Pinned message tests
- Auto-refresh tests
- Notification priority tests
- Voice alert tests

**Validation Checklist:**
- [x] Sticky headers pin correctly
- [x] Dashboard auto-refreshes every 30s
- [x] Notifications route to correct bot
- [x] Voice alerts trigger on HIGH priority

**Implementation Notes (Batch 06 - COMPLETED 2026-01-14):**
- Created 3 new files in `src/telegram/`:
  - `sticky_headers.py` - Sticky header management with auto-regeneration
    - StickyHeader class with pinning logic and auto-update loop (30s interval)
    - StickyHeaderState enum (INACTIVE, CREATING, ACTIVE, UPDATING, REGENERATING, ERROR)
    - Auto-regenerate when pinned message deleted by user
    - StickyHeaderManager for managing multiple headers across chats
    - HybridStickySystem combining Reply keyboard + Pinned inline menu
    - Content generators for Controller, Notification, and Analytics bots
  - `notification_router.py` - Smart notification routing system
    - NotificationPriority enum (CRITICAL=5, HIGH=4, MEDIUM=3, LOW=2, INFO=1)
    - NotificationType enum with 30+ event types (trade, system, plugin, analytics)
    - TargetBot enum (CONTROLLER, NOTIFICATION, ANALYTICS, ALL)
    - NotificationRouter with priority-based routing rules
    - Mute/unmute functionality per notification type and global
    - CRITICAL priority always broadcasts to ALL bots (never muted)
    - NotificationFormatter with standard formatters for entry, exit, daily summary, emergency, error
    - Statistics tracking (by type, priority, target)
  - `voice_alert_integration.py` - Bridge to existing VoiceAlertSystem
    - VoiceAlertConfig with default voice triggers per notification type
    - VoiceTextGenerator for voice-friendly text generation
    - VoiceAlertIntegration class bridging NotificationRouter and VoiceAlertSystem
    - Enable/disable voice per notification type
    - CRITICAL priority always triggers voice (even if type disabled)
    - Priority mapping to existing AlertPriority enum
- Key Features Implemented:
  - Sticky Headers: Pinned messages with auto-refresh and auto-regenerate
  - Hybrid Approach: Reply keyboard (bottom) + Pinned inline menu (top)
  - Priority Routing: CRITICAL → ALL, HIGH → Notification, MEDIUM → Notification, LOW → Analytics, INFO → Controller
  - Mute/Unmute: Per-type and global mute (CRITICAL never muted)
  - Voice Integration: Bridges to existing VoiceAlertSystem with configurable triggers
  - Backward Compatibility: Works with existing voice_alert_system.py
- Created comprehensive unit tests: `tests/test_batch_06_notifications.py` (97 tests, all passing)
- Test categories: StickyHeader (12), StickyHeaderManager (7), HybridStickySystem (4), ContentGenerators (3), NotificationPriority (2), NotificationType (2), Notification (2), DefaultRoutingRules (3), NotificationRouter (20), NotificationFormatter (5), CreateDefaultRouter (1), VoiceAlertConfig (2), VoiceTextGenerator (10), VoiceAlertIntegration (14), CreateVoiceIntegration (2), IntegrateWithRouter (1), FullIntegration (5), BackwardCompatibility (3)

---

### Batch 07: Shared Service API Layer
**Documents:** `05_PHASE_3_DETAILED_PLAN.md`, `03_PHASES_2-6_CONSOLIDATED_PLAN.md`  
**Duration:** 2-3 days  
**Risk:** MEDIUM  
**Dependencies:** Batch 03

**Files to Modify:**
- `src/core/plugin_system/service_api.py` - Complete integration
- `src/core/services/__init__.py` - Service exports

**Tests Required:**
- Service integration tests
- Plugin-to-service communication tests
- End-to-end service flow tests

**Validation Checklist:**
- [x] All services accessible via ServiceAPI
- [x] Plugins can call services correctly
- [x] Service responses match specifications
- [x] No circular dependencies

**Implementation Notes (Batch 07 - COMPLETED 2026-01-14):**
- Refactored `src/core/plugin_system/service_api.py` (v2.0.0 - Full Service Integration):
  - ServiceAPI is now the SINGLE point of entry for all plugin operations
  - Integrates all 4 services from Batch 03: OrderExecutionService, RiskManagementService, TrendManagementService, MarketDataService
  - Plugin-specific initialization with plugin_id parameter
  - Lazy service initialization to avoid circular dependencies
  - Fallback to direct calls if services unavailable
  - Default pip calculator if none exists in trading engine
- Key Features Implemented:
  - Market Data Methods: get_current_spread, check_spread_acceptable, get_current_price_data, get_volatility_state, is_market_open
  - Order Execution Methods: place_dual_orders_v3, place_dual_orders_v6, place_single_order_a, place_single_order_b, close_position, close_position_partial, modify_order_async, get_plugin_orders
  - Risk Management Methods: calculate_lot_size_async, calculate_atr_sl, calculate_atr_tp, check_daily_limit, check_lifetime_limit, validate_trade_risk, get_fixed_lot_size
  - Trend Management Methods: get_timeframe_trend, get_mtf_trends, validate_v3_trend_alignment, check_logic_alignment, update_trend_pulse, get_market_state, check_pulse_alignment, get_pulse_data, update_trend
  - Configuration Methods: get_config, get_plugin_config
  - Factory function: create_service_api()
- Backward Compatibility:
  - All existing methods preserved (get_price, get_balance, place_order, close_trade, modify_order, calculate_lot_size, send_notification, log, get_config)
  - Default plugin_id="core" for legacy usage
  - Graceful degradation when services unavailable
- Plugin Isolation:
  - Each plugin gets its own ServiceAPI instance with unique plugin_id
  - Order comments tagged with plugin_id for tracking
  - Plugin-specific configuration via get_plugin_config()
  - Logs include plugin context
- Created comprehensive unit tests: `tests/test_batch_07_service_integration.py` (62 tests, all passing)
- Test categories: ServiceAPIInitialization (4), BackwardCompatibility (11), OrderExecutionIntegration (9), RiskManagementIntegration (7), MarketDataIntegration (5), TrendManagementIntegration (9), PluginIsolation (4), EndToEndFlow (3), CircularDependencyPrevention (3), ErrorHandling (3), Configuration (4)

---

### Batch 08: V3 Combined Logic Plugin
**Documents:** `06_PHASE_4_DETAILED_PLAN.md`, `12_TESTING_CHECKLISTS.md`  
**Duration:** 4-5 days  
**Risk:** HIGH  
**Dependencies:** Batch 01, Batch 02, Batch 03

**Files to Create:**
- `src/logic_plugins/combined_v3/plugin.py`
- `src/logic_plugins/combined_v3/signal_handlers.py`
- `src/logic_plugins/combined_v3/order_manager.py`
- `src/logic_plugins/combined_v3/trend_validator.py`
- `src/logic_plugins/combined_v3/__init__.py`

**Tests Required:**
- All 12 signal type tests
- Dual order placement tests
- MTF trend validation tests
- Routing matrix tests
- Shadow mode tests

**Validation Checklist:**
- [x] All 12 V3 signals handled correctly
- [x] Dual orders (A+B) placed correctly
- [x] 4-pillar trend validation works
- [x] LOGIC1/2/3 routing correct
- [x] Legacy behavior 100% preserved

**Implementation Notes (Batch 08 - COMPLETED 2026-01-14):**
- Created 5 new files in `src/logic_plugins/combined_v3/`:
  - `__init__.py` - Module documentation and exports
  - `config.json` - Plugin configuration with 12 signal types, routing matrix, dual order settings
  - `plugin.py` - CombinedV3Plugin class (600+ lines) extending BaseLogicPlugin
    - Implements all required hooks: on_alert, on_tick, on_trade_update, on_config_change
    - 2-tier routing matrix: Signal Override (Priority 1) → Timeframe Routing (Priority 2)
    - Shadow mode support for testing without real orders
    - Plugin status and statistics tracking
  - `signal_handlers.py` - V3SignalHandlers class (400+ lines)
    - Handles all 12 signal types: institutional_launchpad, liquidity_trap, momentum_breakout, mitigation_test, golden_pocket_flip, volatility_squeeze, bullish_exit, bearish_exit, screener_full_bullish, screener_full_bearish, trend_pulse, sideways_breakout
    - Signal-specific routing logic (screener → LOGIC3, golden_pocket → LOGIC2)
    - Info-only signals (volatility_squeeze) don't place orders
    - DB update signals (trend_pulse) update market_trends table
  - `order_manager.py` - V3OrderManager class (620 lines)
    - Dual order system: Order A (V3 Smart SL) + Order B (Fixed $10 SL)
    - Consensus-to-multiplier mapping (0-9 → 0.2-1.0)
    - 4-step position sizing: base lot → V3 multiplier → logic multiplier → 50/50 split
    - Aggressive reversal detection for exit signals
  - `trend_validator.py` - V3TrendValidator class (400+ lines)
    - MTF 4-pillar extraction: indices [2:6] from 6-value trend string (ignores 1m/5m noise)
    - Trend alignment validation: requires 3/4 pillars aligned with direction
    - Bypass logic for entry_v3 signals (always bypass trend check)
    - Market trends database updates
- Key Features Implemented:
  - 12 Signal Types: All V3 signals from Pine Script fully supported
  - 2-Tier Routing: Signal override takes priority, then timeframe routing
  - Dual Order System: Order A uses V3 Smart SL, Order B uses Fixed $10 SL (IGNORES V3 SL)
  - 4-Pillar MTF: Extracts 15m, 1h, 4h, Daily trends (ignores 1m/5m noise)
  - Position Sizing: 4-step flow with consensus multiplier and logic multiplier
  - Shadow Mode: Plugin can run without placing real orders for testing
  - Zero Regression: V3 behavior 100% preserved from existing trading_engine.py
- Backward Compatibility:
  - Routing logic matches existing _route_v3_to_logic() in trading_engine.py
  - Multipliers match existing LOGIC_MULTIPLIERS dictionary
  - Dual order parameters match existing _place_hybrid_dual_orders_v3()
  - MTF extraction matches existing ZepixV3Alert.get_mtf_pillars()
- Created comprehensive unit tests: `tests/test_batch_08_v3_plugin.py` (42 tests, all passing)
- Test categories: CombinedV3Plugin (3), V3RoutingMatrix (12), V3SignalHandlers (3), V3DualOrderSystem (6), V3MTF4Pillar (10), V3PositionSizing (1), V3ShadowMode (2), V3BackwardCompatibility (3), V3Integration (2)

---

### Batch 09: Config Hot-Reload & DB Isolation
**Documents:** `07_PHASE_5_DETAILED_PLAN.md`, `23_DATABASE_SYNC_ERROR_RECOVERY.md`  
**Duration:** 2-3 days  
**Risk:** MEDIUM  
**Dependencies:** Batch 02, Batch 08

**Files to Create:**
- `src/core/config_manager.py`
- `src/core/plugin_database.py`
- `src/core/database_sync_manager.py`

**Tests Required:**
- Config hot-reload tests
- Database isolation tests
- Sync error recovery tests
- Manual sync trigger tests

**Validation Checklist:**
- [x] Config changes apply without restart
- [x] Each plugin uses isolated database
- [x] Sync retries on failure
- [x] /sync_manual command works

**Implementation Notes (Batch 09 - COMPLETED 2026-01-14):**
- Created 3 new files in `src/core/`:
  - `config_manager.py` - Dynamic configuration hot-reload system (600+ lines)
    - ConfigManager class with file watching (polling-based, 2s interval)
    - JSON schema validation before applying changes
    - Observer pattern for notifying plugins of config changes
    - Thread-safe config access with RLock
    - Atomic config updates using temp file + rename
    - Dot notation support for nested config access (e.g., "risk_tiers.5000.per_trade_cap")
    - Plugin-specific config loading from config/plugins/ directory
    - Change history tracking (last 100 changes)
    - ConfigChange dataclass with key, change_type, old_value, new_value, timestamp
  - `plugin_database.py` - Isolated SQLite database for each plugin (650+ lines)
    - PluginDatabase class with connection pooling (default 5 connections)
    - Thread-safe operations using Queue-based pool
    - WAL mode for better concurrency
    - Automatic schema creation (plugin_info, trades, daily_stats, signals_log tables)
    - CRUD operations: save_trade, update_trade, close_trade, get_trade, get_open_trades
    - Signal logging and daily statistics tracking
    - PluginDatabaseManager for managing multiple plugin databases
    - Database statistics tracking (queries, inserts, updates, errors)
  - `database_sync_manager.py` - Synchronization with error recovery (700+ lines)
    - DatabaseSyncManager class with automatic sync every 5 minutes
    - Retry logic with exponential backoff (5s, 10s, 20s) and max 3 retries
    - Manual sync trigger via trigger_manual_sync() for /sync_manual command
    - Health monitoring with get_sync_health() method
    - Alert callback for persistent failures (threshold: 3 consecutive)
    - Syncs trades from plugin DBs (V3/V6) to central aggregated_trades table
    - SyncResult dataclass with status, records_synced, error_message, duration_ms
    - SyncConfig for customizable sync parameters
- Key Features Implemented:
  - Config Hot-Reload: File watching with automatic reload on changes
  - Observer Pattern: Plugins notified of config changes via callbacks
  - Database Isolation: Each plugin gets its own SQLite database (zepix_{plugin_id}.db)
  - Connection Pooling: Thread-safe database access with configurable pool size
  - Sync with Retry: Exponential backoff retry logic for failed syncs
  - Health Monitoring: Track consecutive failures and alert on threshold
  - Manual Sync: Trigger immediate sync bypassing interval wait
- Backward Compatibility:
  - Existing config.py and database.py files NOT modified
  - New system works alongside existing infrastructure
  - Plugins can opt-in to new config/database system
- Created comprehensive unit tests: `tests/test_batch_09_config_db.py` (45 tests, all passing)
- Test categories: ConfigManager (12), PluginConfigHotReload (3), PluginDatabase (11), PluginDatabaseManager (3), DatabaseSyncManager (9), SyncRetryLogic (2), Integration (2), FactoryFunctions (3)

---

### Batch 10: V6 Price Action Plugin Foundation
**Documents:** `16_PHASE_7_V6_INTEGRATION_PLAN.md`, `08_PHASE_6_DETAILED_PLAN.md`  
**Duration:** 4-5 days  
**Risk:** HIGH  
**Dependencies:** Batch 01, Batch 02, Batch 03, Batch 08

**Files to Create:**
- `src/logic_plugins/price_action_1m/plugin.py`
- `src/logic_plugins/price_action_5m/plugin.py`
- `src/logic_plugins/price_action_15m/plugin.py`
- `src/logic_plugins/price_action_1h/plugin.py`
- `src/core/trend_pulse_manager.py`
- `src/core/zepix_v6_alert.py`

**Tests Required:**
- V6 alert parsing tests
- Spread check tests
- ADX threshold tests
- Confidence score tests
- Conditional order tests

**Validation Checklist:**
- [x] All 4 V6 plugins load correctly
- [x] TrendPulseManager works
- [x] Spread filtering prevents bad entries
- [x] Order B conditional logic correct
- [x] No conflicts with V3 plugin

**Implementation Notes (Batch 10 - COMPLETED 2026-01-14):**
- Created 2 new core files in `src/core/`:
  - `trend_pulse_manager.py` - Trend Pulse tracking system (482 lines)
    - TrendPulseData dataclass with bull_count, bear_count, market_state, timestamp
    - MarketState enum: TRENDING_BULLISH, TRENDING_BEARISH, SIDEWAYS, CHOPPY, UNKNOWN
    - TrendPulseManager class with async methods for pulse updates and alignment checks
    - net_direction property returns int (1 for bullish, -1 for bearish, 0 for neutral)
    - strength property returns float (0.0 to 1.0) representing trend strength
    - Database integration for market_trends table updates
    - Caching with _pulse_cache for performance
  - `zepix_v6_alert.py` - V6 Alert parsing system (538 lines)
    - V6AlertType enum: BULLISH_ENTRY, BEARISH_ENTRY, EXIT_BULLISH, EXIT_BEARISH, TREND_PULSE, etc.
    - ADXStrength enum: STRONG, MODERATE, WEAK, NONE
    - ConfidenceLevel enum: HIGH, MODERATE, LOW
    - ZepixV6Alert dataclass with all V6 alert fields (default conf_score=50)
    - TrendPulseAlert dataclass with tf field for timeframe
    - parse_v6_from_dict(), parse_v6_payload(), parse_trend_pulse() functions
    - validate_v6_alert() returns dict with valid flag and issues list
    - V6AlertFactory class for creating alerts programmatically
- Created 4 V6 Price Action plugins in `src/logic_plugins/`:
  - `price_action_1m/plugin.py` - 1M Scalping Logic (600+ lines)
    - ORDER_B_ONLY routing targeting TP1
    - RISK_MULTIPLIER: 0.5x (conservative for scalping)
    - Filters: ADX > 20, Confidence >= 80, Spread < 2 pips
    - Shadow mode enabled by default
  - `price_action_5m/plugin.py` - 5M Momentum Logic (600+ lines)
    - DUAL_ORDERS routing (Order A targets TP2, Order B targets TP1)
    - RISK_MULTIPLIER: 1.0x (standard)
    - Filters: ADX >= 25, Confidence >= 70, 15M Alignment required
    - Shadow mode enabled by default
  - `price_action_15m/plugin.py` - 15M Intraday Logic (600+ lines)
    - ORDER_A_ONLY routing targeting TP2
    - RISK_MULTIPLIER: 1.0x class default (config can override to 1.25)
    - Filters: Market State check, Trend Pulse alignment, Confidence >= 60
    - Shadow mode enabled by default
  - `price_action_1h/plugin.py` - 1H Swing Logic (600+ lines)
    - ORDER_A_ONLY routing targeting TP3 or TP2
    - RISK_MULTIPLIER: 0.6x class default (config can override to 1.5)
    - Filters: 4H Alignment required, Confidence >= 60
    - Shadow mode enabled by default
- Key Features Implemented:
  - Trend Pulse System: Separate from V3, tracks bull/bear counts across timeframes
  - Conditional Order Routing: Different order types per timeframe (ORDER A, ORDER B, DUAL ORDERS)
  - ADX Filters: Minimum ADX thresholds per timeframe (1M: 20, 5M: 25)
  - Spread Filters: Maximum spread constraints (1M: 2 pips critical for scalping)
  - Confidence Scoring: Minimum confidence levels per timeframe (1M: 80, 5M: 70, 15M/1H: 60)
  - Shadow Mode: All plugins run in shadow mode by default (no real orders until enabled)
  - Database Isolation: V6 plugins use zepix_price_action.db (separate from V3)
- Backward Compatibility:
  - V6 plugins run parallel to V3 Combined Logic plugin
  - No modifications to existing V3 plugin or trading_engine.py
  - V6 alerts use similar structure to V3 for consistency
  - All plugins inherit from BaseLogicPlugin
- Created comprehensive unit tests: `tests/test_batch_10_v6_foundation.py` (70 tests, all passing)
- Test categories: TrendPulseData (4), MarketState (2), TrendPulseManager (7), V6AlertType (2), ADXStrength (2), ConfidenceLevel (2), ZepixV6Alert (3), ParseV6FromDict (2), ParseV6Payload (2), ParseTrendPulse (1), ValidateV6Alert (2), V6AlertFactory (2), PriceAction1MPlugin (8), PriceAction5MPlugin (5), PriceAction15MPlugin (4), PriceAction1HPlugin (4), OrderRoutingMatrix (4), RiskMultipliers (4), TimeframeFilters (4), ShadowMode (2), BackwardCompatibility (2), Integration (2)

---

### Batch 11: Plugin Health & Versioning
**Documents:** `25_PLUGIN_HEALTH_MONITORING_SYSTEM.md`, `27_PLUGIN_VERSIONING_SYSTEM.md`  
**Duration:** 2-3 days  
**Risk:** LOW  
**Dependencies:** Batch 01

**Files to Create:**
- `src/monitoring/plugin_health_monitor.py`
- `src/core/plugin_version.py`
- `src/core/versioned_plugin_registry.py`

**Tests Required:**
- Health metric collection tests
- Anomaly detection tests
- Version compatibility tests
- Upgrade/rollback tests

**Validation Checklist:**
- [x] Health metrics collected every 30s
- [x] Alerts trigger on threshold breach
- [x] Version compatibility checks work
- [x] /health and /version commands work

**Implementation Notes (Batch 11 - COMPLETED 2026-01-14):**
- Created `src/monitoring/` module with 2 files:
  - `__init__.py` - Module exports for monitoring system
  - `plugin_health_monitor.py` - Core health monitoring system (1000+ lines)
    - HealthStatus enum: HEALTHY, STALE, HUNG, DEAD, UNKNOWN
    - AlertLevel enum: CRITICAL, HIGH, WARNING, INFO
    - PluginAvailabilityMetrics dataclass: is_running, is_responsive, last_heartbeat, uptime_seconds
    - PluginPerformanceMetrics dataclass: execution times, signals processed, win rate, record_execution_time()
    - PluginResourceMetrics dataclass: memory, CPU, DB connections
    - PluginErrorMetrics dataclass: error counts, error rate, record_error()
    - HealthSnapshot dataclass: combines all 4 metrics, health_status property, is_healthy property
    - HealthAlert dataclass: alert records with id, plugin_id, level, message, timestamp, resolved status
    - PluginHealthMonitor class with async monitoring loop (30s interval)
    - Metrics collection: availability, performance, resources, errors
    - Anomaly detection with configurable thresholds
    - Zombie plugin detection and auto-restart (max 3 attempts)
    - Alert throttling with 5-minute cooldown between identical alerts
    - Database persistence for snapshots and alerts (zepix_health.db)
    - Telegram integration for notifications
    - Callback system for alerts and restarts
    - Health dashboard formatting for Telegram display
    - Thread-safe operations using RLock
- Created `src/core/versioned_plugin_registry.py` - Semantic versioning system (700+ lines)
  - PluginVersion dataclass: plugin_id, major, minor, patch, build_date, commit_hash
  - version_string property returns "MAJOR.MINOR.PATCH" format
  - from_string() class method for parsing version strings
  - is_compatible_with() checks MAJOR version compatibility
  - is_newer_than() for version comparison
  - VersionHistoryEntry dataclass for tracking version activations
  - VersionedPluginRegistry class with database persistence (zepix_versions.db)
  - register_version() stores version in database
  - activate_plugin() with compatibility checking
  - upgrade_plugin() with MAJOR version compatibility enforcement
  - rollback_plugin() to previous stable version
  - deprecate_version() marks version as deprecated
  - get_version_history() returns activation history
  - format_version_dashboard() for Telegram display
  - create_default_plugin_versions() factory for V3 and V6 plugins
- Updated `src/telegram/controller_bot.py` (v1.1.0) with health and version commands:
  - Added _health_monitor and _version_registry dependencies
  - Updated set_dependencies() to accept health_monitor and version_registry
  - handle_health_command() - /health command shows plugin health dashboard
  - handle_version_command() - /version command shows active plugin versions
  - handle_upgrade_command() - /upgrade <plugin_id> <version> for upgrades
  - handle_rollback_command() - /rollback <plugin_id> for rollbacks
  - get_health_summary() and get_version_summary() for programmatic access
- Key Features Implemented:
  - Health Monitoring: 4 metrics dimensions (availability, performance, resources, errors)
  - Zombie Detection: Identify frozen/unresponsive plugins and auto-restart
  - Alert Throttling: 5-minute cooldown prevents alert spam
  - Auto-Restart: Automatic recovery of crashed plugins (max 3 attempts)
  - Semantic Versioning: MAJOR.MINOR.PATCH format with compatibility rules
  - Compatibility Checking: Same MAJOR version = compatible, different MAJOR = incompatible
  - Upgrade/Rollback: Safe version transitions with history tracking
  - Telegram Commands: /health, /version, /upgrade, /rollback
- Backward Compatibility:
  - New monitoring system works alongside existing infrastructure
  - Controller Bot maintains all existing functionality
  - Health monitor and version registry are optional dependencies
  - No modifications to existing plugin files
- Created comprehensive unit tests: `tests/test_batch_11_health.py` (60 tests, all passing)
- Test categories: PluginAvailabilityMetrics (5), PluginPerformanceMetrics (2), PluginResourceMetrics (1), PluginErrorMetrics (2), HealthSnapshot (1), HealthAlert (1), PluginHealthMonitor (9), HealthMonitorAsync (2), PluginVersion (9), VersionedPluginRegistry (9), VersionUpgradeRollback (4), VersionDeprecation (1), ControllerBotHealthCommands (8), ControllerBotDependencies (1), DefaultPluginVersions (1), Integration (2), BackwardCompatibility (2)

---

### Batch 12: Data Migration & Developer Docs
**Documents:** `26_DATA_MIGRATION_SCRIPTS.md`, `15_DEVELOPER_ONBOARDING.md`  
**Duration:** 2 days  
**Risk:** LOW  
**Dependencies:** Batch 02, Batch 09

**Files to Create:**
- `migrations/migration_manager.py`
- `migrations/combined_v3/001_initial_schema.sql`
- `migrations/price_action_v6/001_initial_schema.sql`
- `migrations/central_system/001_initial_schema.sql`
- `docs/developer/PLUGIN_DEVELOPMENT_GUIDE.md`

**Tests Required:**
- Migration apply tests
- Migration rollback tests
- Schema verification tests

**Validation Checklist:**
- [x] Migrations apply cleanly
- [x] Rollbacks work correctly
- [x] Developer guide is complete
- [x] /migration_status command works

**Implementation Notes (Batch 12 - COMPLETED 2026-01-14):**
- Created `src/utils/data_migration_tool.py` - Data migration from V4 to V5 (802 lines)
  - MigrationStatus enum: PENDING, IN_PROGRESS, COMPLETED, FAILED, ROLLED_BACK
  - MigrationResult dataclass: status, source_db, target_db, records_migrated/failed/skipped, P&L integrity
  - ColumnMapping dataclass: V4 to V5 column mapping with transforms and defaults
  - DataMigrationTool class with comprehensive migration functionality:
    - V4_TO_V5_COLUMN_MAPPING: 17 column mappings (trade_id→mt5_ticket, pnl→profit_dollars, etc.)
    - _transform_status(): Convert V4 status to V5 format
    - _map_v4_to_v5(): Full row transformation with signal_data JSON for legacy fields
    - _ensure_v5_schema(): Create V5 tables (plugin_info, trades, daily_stats, signals_log, migration_log)
    - get_v4_trades(): Retrieve trades with optional strategy filter
    - get_v4_summary(): Database summary with trade counts and P&L totals
    - migrate_to_plugin(): Core migration with dry_run support, backup creation, integrity checks
    - migrate_to_v3_plugin(): Convenience method for V3 Combined Logic
    - migrate_to_v6_plugin(): Convenience method for V6 Price Action (by timeframe)
    - verify_integrity(): Post-migration checks (record count, P&L match, no duplicates, required fields)
    - rollback_migration(): Remove migrated records by migrated_from='v4' marker
    - get_migration_history(): Track all migrations performed
    - format_migration_report(): Human-readable migration summary
  - create_migration_tool() factory function
- Created `src/utils/doc_generator.py` - Auto-generate API docs from docstrings (600+ lines)
  - DocstringParser class: Parse Google-style and NumPy-style docstrings
    - SECTIONS list: Args, Parameters, Returns, Raises, Examples, Notes, Attributes
    - parse(): Extract description, params, returns from docstring
    - _parse_params(): Parse parameter documentation
    - _parse_returns(): Parse return documentation
  - ParameterDoc, ReturnDoc, FunctionDoc, ClassDoc, ModuleDoc dataclasses
  - PythonDocExtractor class: Extract documentation from Python source files
    - extract_from_file(): Parse Python file using AST
    - _extract_class(): Extract class documentation with methods
    - _extract_function(): Extract function documentation with parameters and returns
    - _get_annotation_string(): Convert AST annotations to strings
    - _get_default_string(): Convert AST default values to strings
  - DocGenerator class: Generate Markdown documentation
    - generate_file(): Generate docs for single file
    - generate_directory(): Generate docs for all files in directory
    - generate_service_api_docs(): Generate combined service API documentation
    - generate_all(): Generate all documentation (services, core, utils, telegram)
    - _generate_header(), _generate_toc(), _generate_footer(): Formatting helpers
  - create_doc_generator() and generate_service_api_docs() factory functions
- Key Features Implemented:
  - V4 to V5 Migration: Safe migration from trading_bot.db to plugin-isolated databases
  - Schema Transformation: 17 column mappings with type conversion and defaults
  - Integrity Verification: P&L matching, duplicate detection, required field validation
  - Dry Run Mode: Simulate migration without writing to database
  - Rollback Support: Remove migrated records using marker field
  - Backup Creation: Automatic backup before migration
  - Migration History: Track all migrations with timestamps and results
  - API Documentation: Auto-generate Markdown from Python docstrings
  - Docstring Parsing: Support for Google-style and NumPy-style formats
  - AST-based Extraction: Parse Python source files for classes, functions, parameters
- Backward Compatibility:
  - Migration tool works with existing trading_bot.db schema
  - Doc generator works with existing service files
  - No modifications to existing database.py or plugin_database.py
  - All new files are additive (no existing files modified)
- Created comprehensive unit tests: `tests/test_batch_12_migration.py` (42 tests, all passing)
- Test categories: MigrationStatus (1), MigrationResult (3), ColumnMapping (2), DataMigrationTool (11), FactoryFunction (1), DocstringParser (3), ParameterDoc (1), ReturnDoc (1), FunctionDoc (2), ClassDoc (2), ModuleDoc (2), PythonDocExtractor (4), DocGenerator (4), DocGeneratorFactory (1), Integration (2), BackwardCompatibility (2)

---

### Batch 13: Code Quality & User Docs
**Documents:** `13_CODE_REVIEW_GUIDELINES.md`, `14_USER_DOCUMENTATION.md`  
**Duration:** 1-2 days  
**Risk:** LOW  
**Dependencies:** All previous batches

**Files to Create:**
- `docs/CODE_REVIEW_CHECKLIST.md`
- `docs/USER_GUIDE.md`
- `docs/TELEGRAM_COMMANDS_REFERENCE.md`
- `docs/TROUBLESHOOTING.md`

**Tests Required:**
- Documentation completeness check
- Command reference accuracy check

**Validation Checklist:**
- [x] All code review guidelines documented
- [x] User guide covers all features
- [x] All Telegram commands documented
- [x] Troubleshooting guide complete

**Implementation Notes (Batch 13 - COMPLETED 2026-01-14):**
- Created `.pre-commit-config.yaml` - Pre-commit hooks configuration (110 lines)
  - Black formatter: line-length=100, target-version=py39
  - isort: profile=black, line-length=100
  - Flake8: max-line-length=100, extend-ignore=E203,E501,W503, max-complexity=15
  - MyPy: ignore-missing-imports, no-strict-optional, warn-unused-ignores
  - Bandit: security linter with medium/high severity only
  - General hooks: trailing-whitespace, end-of-file-fixer, check-yaml, check-json, detect-private-key
  - CI configuration for pre-commit.ci with weekly autoupdate
- Created `pyproject.toml` - Project configuration (200+ lines)
  - [project] section: name, version 5.0.0, description, dependencies
  - [tool.black]: line-length=100, target-version=['py39', 'py310', 'py311']
  - [tool.isort]: profile="black", line_length=100, known_first_party=["src"]
  - [tool.mypy]: python_version="3.9", warn_return_any=true, check_untyped_defs=true
  - [tool.pytest.ini_options]: testpaths=["tests"], markers for all 13 batches
  - [tool.coverage.run]: source=["src"], branch=true, fail_under=70
  - [tool.bandit]: exclude_dirs=["tests", "data", "logs"], targets=["src"]
- Created `docs/USER_GUIDE_V5.md` - Comprehensive user guide (600+ lines)
  - What's New in V5: Plugin architecture, isolated databases, health monitoring, hot-reload
  - Understanding Plugins: combined_v3, price_action_1m/5m/15m/1h explained
  - Telegram Commands: 7 categories with 30+ commands documented
  - Plugin Management: /plugins, /enable_plugin, /disable_plugin, /plugin_status
  - Configuration Guide: Plugin config files, common options, hot-reload
  - Notification Formats: Entry, exit, profit booking, health alerts
  - Safety Features: Daily loss limit, shadow mode, emergency stop
  - Performance Tracking: Daily/weekly reports, export trades
  - Troubleshooting: Common issues and solutions
  - FAQ: 6 frequently asked questions
- Created `docs/MIGRATION_GUIDE.md` - V4 to V5 migration guide (450+ lines)
  - Prerequisites: Backup, no open trades, Python 3.9+
  - 10-step migration process with detailed instructions
  - Configuration mapping: V4 settings to V5 locations
  - Migration tool usage with code examples
  - Rollback procedure for reverting to V4
  - Troubleshooting: Migration tool errors, bot startup errors, Telegram errors
  - Post-migration checklist
  - Database schema changes: V4 (32 columns) to V5 (75 columns)
  - Column mapping table
- Key Features Implemented:
  - Pre-commit Hooks: Automated code quality enforcement before commits
  - Tool Configuration: Black, isort, Flake8, MyPy, Bandit all configured
  - Line Length Standard: 100 characters across all tools
  - User Documentation: Complete guide for end-users with V5 features
  - Migration Documentation: Step-by-step upgrade path from V4
  - Backward Compatibility: requirements.txt preserved, pyproject.toml additive
- Created comprehensive unit tests: `tests/test_batch_13_quality.py` (51 tests, all passing)
- Test categories: PreCommitConfig (8), PyprojectToml (13), UserGuide (10), MigrationGuide (9), CodeQuality (4), DocumentationLinks (2), Integration (3), BackwardCompatibility (2)

---

### Batch 14: Dashboard Specification (Optional)
**Documents:** `17_DASHBOARD_TECHNICAL_SPECIFICATION.md`, `MASTER_IMPLEMENTATION_GUIDE.md`  
**Duration:** 1 day (documentation only)  
**Risk:** LOW  
**Dependencies:** All previous batches

**Files to Create:**
- `docs/DASHBOARD_API_SPEC.md`
- `docs/DASHBOARD_IMPLEMENTATION_ROADMAP.md`

**Tests Required:**
- None (documentation only)

**Validation Checklist:**
- [ ] Dashboard API endpoints documented
- [ ] Implementation roadmap clear
- [ ] Phase 6 deferred to Part-2

---

## Critical Reminders

### Before Starting ANY Batch:
1. Read the planning documents for that batch
2. Cross-reference with actual bot code in `src/`
3. Validate against current Telegram docs
4. Identify any gaps or missing features
5. Create YOUR implementation plan based on validated requirements

### During Implementation:
1. Modify only required files
2. Reuse existing utilities and patterns
3. Respect existing architecture
4. All changes must be incremental, not destructive
5. Test after each significant change

### After Each Batch:
1. Run all tests for that batch
2. Verify legacy behavior still works
3. Create test report in `04_TEST_REPORTS/`
4. Document any improvements made
5. Commit with message: `Batch XX: <description>`

### Git Discipline:
- One batch = one commit (or multiple small commits)
- Never force push
- Never skip hooks
- Never push directly to main

---

## Validation Checklist (Final)

Before marking Part-1 as complete:

- [ ] All 14 batches implemented
- [ ] All tests passing
- [ ] All test reports created
- [ ] Legacy V3 behavior 100% preserved
- [ ] V6 plugins functional (at least skeleton)
- [ ] Multi-Telegram system working
- [ ] No regressions in existing bot
- [ ] Documentation complete
- [ ] Code reviewed

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing bot | Shadow mode testing, incremental changes |
| Telegram rate limits | Rate limiter implementation in Batch 05 |
| Database conflicts | Isolated databases per plugin |
| Config corruption | Hot-reload with validation |
| Plugin crashes | Health monitoring in Batch 11 |

---

## Contact & Support

- **Implementation Lead:** Devin AI
- **Repository:** gitlab.com/asggroupsinfo/algo-asggoups-v1
- **Branch:** devin/1768392947-v5-audit-reports
- **PR:** https://gitlab.com/asggroupsinfo/algo-asggoups-v1/-/merge_requests/1

---

**Document Status:** READY FOR BATCH 01 IMPLEMENTATION ON USER APPROVAL
