# MASTER IMPLEMENTATION PLAN - Part 1 (V5 Hybrid Plugin Architecture)

**Start Date:** 2026-01-14  
**Target Completion:** 2026-02-28 (5-7 weeks)  
**Current Phase:** Pre-Implementation (Batch Structure Ready)  
**Document Version:** 2.0

---

## Implementation Progress Overview

| Batch | Name | Status | Impl. | Test | Report | Improvements |
|-------|------|--------|-------|------|--------|--------------|
| 01 | Core Plugin System Foundation | PASSED | [x] | [x] | [x] | [x] |
| 02 | Multi-Database Schema Design | PASSED | [x] | [x] | [x] | [x] |
| 03 | ServiceAPI Implementation | PASSED | [x] | [x] | [x] | [x] |
| 04 | 3-Bot Telegram Architecture | PENDING | [ ] | [ ] | [ ] | [ ] |
| 05 | Telegram UX & Rate Limiting | PENDING | [ ] | [ ] | [ ] | [ ] |
| 06 | Sticky Header & Notification Router | PENDING | [ ] | [ ] | [ ] | [ ] |
| 07 | Shared Service API Layer | PENDING | [ ] | [ ] | [ ] | [ ] |
| 08 | V3 Combined Logic Plugin | PENDING | [ ] | [ ] | [ ] | [ ] |
| 09 | Config Hot-Reload & DB Isolation | PENDING | [ ] | [ ] | [ ] | [ ] |
| 10 | V6 Price Action Plugin Foundation | PENDING | [ ] | [ ] | [ ] | [ ] |
| 11 | Plugin Health & Versioning | PENDING | [ ] | [ ] | [ ] | [ ] |
| 12 | Data Migration & Developer Docs | PENDING | [ ] | [ ] | [ ] | [ ] |
| 13 | Code Quality & User Docs | PENDING | [ ] | [ ] | [ ] | [ ] |
| 14 | Dashboard Specification (Optional) | PENDING | [ ] | [ ] | [ ] | [ ] |

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
- [ ] All 3 bots can be initialized
- [ ] Messages route to correct bot
- [ ] Existing Controller Bot functionality preserved
- [ ] No Telegram API rate limit violations

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
- [ ] Rate limiter enforces 20 msg/min per bot
- [ ] Priority queue works correctly
- [ ] Same menus work in all 3 bots
- [ ] Zero-typing UI functional

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
- [ ] Sticky headers pin correctly
- [ ] Dashboard auto-refreshes every 30s
- [ ] Notifications route to correct bot
- [ ] Voice alerts trigger on HIGH priority

---

### Batch 07: Shared Service API Layer
**Documents:** `05_PHASE_3_DETAILED_PLAN.md`, `03_PHASES_2-6_CONSOLIDATED_PLAN.md`  
**Duration:** 2-3 days  
**Risk:** MEDIUM  
**Dependencies:** Batch 03

**Files to Modify:**
- `src/core/service_api.py` - Complete integration
- `src/core/services/__init__.py` - Service exports

**Tests Required:**
- Service integration tests
- Plugin-to-service communication tests
- End-to-end service flow tests

**Validation Checklist:**
- [ ] All services accessible via ServiceAPI
- [ ] Plugins can call services correctly
- [ ] Service responses match specifications
- [ ] No circular dependencies

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
- [ ] All 12 V3 signals handled correctly
- [ ] Dual orders (A+B) placed correctly
- [ ] 4-pillar trend validation works
- [ ] LOGIC1/2/3 routing correct
- [ ] Legacy behavior 100% preserved

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
- [ ] Config changes apply without restart
- [ ] Each plugin uses isolated database
- [ ] Sync retries on failure
- [ ] /sync_manual command works

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
- [ ] All 4 V6 plugins load correctly
- [ ] TrendPulseManager works
- [ ] Spread filtering prevents bad entries
- [ ] Order B conditional logic correct
- [ ] No conflicts with V3 plugin

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
- [ ] Health metrics collected every 30s
- [ ] Alerts trigger on threshold breach
- [ ] Version compatibility checks work
- [ ] /health and /version commands work

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
- [ ] Migrations apply cleanly
- [ ] Rollbacks work correctly
- [ ] Developer guide is complete
- [ ] /migration_status command works

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
- [ ] All code review guidelines documented
- [ ] User guide covers all features
- [ ] All Telegram commands documented
- [ ] Troubleshooting guide complete

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
