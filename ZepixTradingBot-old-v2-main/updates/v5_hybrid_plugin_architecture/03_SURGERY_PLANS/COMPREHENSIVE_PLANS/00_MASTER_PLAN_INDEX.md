# MASTER PLAN INDEX: V5 HYBRID PLUGIN ARCHITECTURE SURGERY
## Complete Comprehensive Planning Document

**Date:** 2026-01-15
**Author:** Devin (Autonomous Planning Phase)
**Status:** COMPREHENSIVE PLANNING COMPLETE
**Total Plans:** 12 Comprehensive Surgery Plans

---

## EXECUTIVE SUMMARY

This Master Plan Index provides a complete roadmap for the V5 Hybrid Plugin Architecture surgery. It addresses ALL 10 critical gaps and ALL 8 hidden discoveries identified in the Study Phase. The plans are organized by functional area and sequenced for safe, incremental implementation.

**Key Metrics:**
- **Total Plans:** 12
- **Total Gaps Addressed:** 10/10 (100%)
- **Total Discoveries Addressed:** 8/8 (100%)
- **Total V5 Requirements Covered:** 78/78 (100%)
- **Total Original Features Preserved:** 47/47 (100%)
- **Estimated Implementation Time:** 4-5 weeks
- **Estimated Testing Time:** 1-2 weeks
- **Total Timeline:** 5-7 weeks

---

## PLAN SUMMARY TABLE

| Plan # | Plan Name | Priority | Est. Time | Dependencies | Gaps Addressed |
|--------|-----------|----------|-----------|--------------|----------------|
| 01 | Core Cleanup & Plugin Delegation | P0 | 3-4 days | None | GAP-1 (partial) |
| 02 | Webhook Routing & Signal Processing | P0 | 2-3 days | Plan 01 | GAP-1 (complete) |
| 03 | Re-Entry System Integration | P0 | 4-5 days | Plan 02 | GAP-1, Discovery 1-4 |
| 04 | Dual Order System Integration | P0 | 3-4 days | Plan 02 | GAP-2 |
| 05 | Profit Booking Integration | P0 | 3-4 days | Plan 04 | GAP-4 |
| 06 | Autonomous System Integration | P1 | 3-4 days | Plans 03-05 | GAP-5, Discovery 5-7 |
| 07 | 3-Bot Telegram Migration | P1 | 4-5 days | Plan 06 | GAP-3 |
| 08 | Service API Integration | P1 | 2-3 days | Plan 07 | GAP-6 |
| 09 | Database Isolation | P2 | 2-3 days | Plan 08 | GAP-8 |
| 10 | Plugin Renaming & Structure | P2 | 1-2 days | Plan 09 | GAP-9 |
| 11 | Shadow Mode Testing | P2 | 3-4 days | Plan 10 | GAP-7 |
| 12 | Integration & E2E Testing | P2 | 3-4 days | Plan 11 | GAP-10, Discovery 8 |

---

## DEPENDENCY GRAPH

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    PHASE 1: CORE                        │
                    │                                                         │
                    │   ┌──────────┐         ┌──────────┐                    │
                    │   │ Plan 01  │────────▶│ Plan 02  │                    │
                    │   │  Core    │         │ Webhook  │                    │
                    │   │ Cleanup  │         │ Routing  │                    │
                    │   └──────────┘         └────┬─────┘                    │
                    │                             │                          │
                    └─────────────────────────────┼──────────────────────────┘
                                                  │
                    ┌─────────────────────────────┼──────────────────────────┐
                    │                    PHASE 2: FEATURES                   │
                    │                             │                          │
                    │         ┌───────────────────┼───────────────────┐      │
                    │         │                   │                   │      │
                    │         ▼                   ▼                   ▼      │
                    │   ┌──────────┐        ┌──────────┐        ┌──────────┐ │
                    │   │ Plan 03  │        │ Plan 04  │        │ Plan 05  │ │
                    │   │ Re-Entry │        │  Dual    │───────▶│ Profit   │ │
                    │   │ System   │        │ Orders   │        │ Booking  │ │
                    │   └────┬─────┘        └────┬─────┘        └────┬─────┘ │
                    │        │                   │                   │      │
                    │        └───────────────────┼───────────────────┘      │
                    │                            │                          │
                    └────────────────────────────┼──────────────────────────┘
                                                 │
                    ┌────────────────────────────┼──────────────────────────┐
                    │                    PHASE 3: INTEGRATION               │
                    │                            │                          │
                    │                            ▼                          │
                    │                      ┌──────────┐                     │
                    │                      │ Plan 06  │                     │
                    │                      │Autonomous│                     │
                    │                      │ System   │                     │
                    │                      └────┬─────┘                     │
                    │                           │                           │
                    │                           ▼                           │
                    │                      ┌──────────┐                     │
                    │                      │ Plan 07  │                     │
                    │                      │ 3-Bot    │                     │
                    │                      │ Telegram │                     │
                    │                      └────┬─────┘                     │
                    │                           │                           │
                    │                           ▼                           │
                    │                      ┌──────────┐                     │
                    │                      │ Plan 08  │                     │
                    │                      │ Service  │                     │
                    │                      │   API    │                     │
                    │                      └────┬─────┘                     │
                    │                           │                           │
                    └───────────────────────────┼───────────────────────────┘
                                                │
                    ┌───────────────────────────┼───────────────────────────┐
                    │                    PHASE 4: FINALIZATION              │
                    │                           │                           │
                    │         ┌─────────────────┼─────────────────┐         │
                    │         │                 │                 │         │
                    │         ▼                 ▼                 ▼         │
                    │   ┌──────────┐      ┌──────────┐      ┌──────────┐   │
                    │   │ Plan 09  │─────▶│ Plan 10  │─────▶│ Plan 11  │   │
                    │   │ Database │      │ Renaming │      │ Shadow   │   │
                    │   │Isolation │      │          │      │  Mode    │   │
                    │   └──────────┘      └──────────┘      └────┬─────┘   │
                    │                                            │         │
                    │                                            ▼         │
                    │                                      ┌──────────┐    │
                    │                                      │ Plan 12  │    │
                    │                                      │  E2E     │    │
                    │                                      │ Testing  │    │
                    │                                      └──────────┘    │
                    │                                                      │
                    └──────────────────────────────────────────────────────┘
```

---

## EXECUTION PHASES

### PHASE 1: CORE FOUNDATION (Week 1)
**Plans:** 01, 02
**Objective:** Remove hardcoded logic and establish plugin delegation

| Day | Plan | Tasks |
|-----|------|-------|
| 1-2 | 01 | Remove hardcoded V3 logic from trading_engine.py |
| 2-3 | 01 | Create plugin delegation framework |
| 3-4 | 02 | Implement webhook → plugin routing |
| 4-5 | 02 | Test signal flow through plugins |

**Milestone:** Plugins receive and process signals (no execution yet)

### PHASE 2: FEATURE INTEGRATION (Week 2-3)
**Plans:** 03, 04, 05
**Objective:** Wire plugins to all trading features

| Day | Plan | Tasks |
|-----|------|-------|
| 1-2 | 03 | Wire SL Hunt Recovery to plugins |
| 2-3 | 03 | Wire TP Continuation to plugins |
| 3-4 | 03 | Wire Exit Continuation to plugins |
| 4-5 | 04 | Wire Dual Order Manager to plugins |
| 5-6 | 04 | Implement Order A/B lifecycle |
| 6-7 | 05 | Wire Profit Booking to plugins |
| 7-8 | 05 | Implement chain creation for Order B |

**Milestone:** Plugins can execute full trading lifecycle

### PHASE 3: SYSTEM INTEGRATION (Week 3-4)
**Plans:** 06, 07, 08
**Objective:** Integrate autonomous systems and Telegram

| Day | Plan | Tasks |
|-----|------|-------|
| 1-2 | 06 | Wire Autonomous System Manager |
| 2-3 | 06 | Implement safety limits in plugins |
| 3-4 | 07 | Migrate commands to Controller Bot |
| 4-5 | 07 | Migrate notifications to Notification Bot |
| 5-6 | 07 | Migrate analytics to Analytics Bot |
| 6-7 | 08 | Update plugins to use ServiceAPI |
| 7-8 | 08 | Implement service metrics |

**Milestone:** Full system integration complete

### PHASE 4: FINALIZATION (Week 4-5)
**Plans:** 09, 10, 11, 12
**Objective:** Database isolation, cleanup, and testing

| Day | Plan | Tasks |
|-----|------|-------|
| 1-2 | 09 | Implement database isolation per plugin |
| 2-3 | 10 | Rename plugins to match convention |
| 3-4 | 11 | Implement shadow mode |
| 4-5 | 11 | Run shadow mode comparison |
| 5-6 | 12 | Create integration tests |
| 6-7 | 12 | Create E2E tests |
| 7-8 | 12 | Final verification |

**Milestone:** V5 Surgery Complete, Ready for Production

---

## COVERAGE MATRIX: GAPS

| Gap # | Gap Description | Addressed By | Status |
|-------|-----------------|--------------|--------|
| GAP-1 | Plugin Wiring to Core | Plans 01, 02 | PLANNED |
| GAP-2 | Dual Order System Integration | Plan 04 | PLANNED |
| GAP-3 | 3-Bot Telegram Integration | Plan 07 | PLANNED |
| GAP-4 | Profit Booking Integration | Plan 05 | PLANNED |
| GAP-5 | Autonomous System Integration | Plan 06 | PLANNED |
| GAP-6 | Service API Usage | Plan 08 | PLANNED |
| GAP-7 | Shadow Mode Testing | Plan 11 | PLANNED |
| GAP-8 | Plugin Isolation | Plan 09 | PLANNED |
| GAP-9 | Folder Structure Mismatch | Plan 10 | PLANNED |
| GAP-10 | Integration Testing | Plan 12 | PLANNED |

---

## COVERAGE MATRIX: DISCOVERIES

| Discovery # | Discovery Description | Addressed By | Status |
|-------------|----------------------|--------------|--------|
| Discovery 1 | Reverse Shield System (v3.0) | Plan 03, 06 | PLANNED |
| Discovery 2 | Recovery Window Monitor | Plan 03 | PLANNED |
| Discovery 3 | Exit Continuation Monitor | Plan 03 | PLANNED |
| Discovery 4 | Profit Protection Logic | Plan 06 | PLANNED |
| Discovery 5 | Daily/Concurrent Recovery Limits | Plan 06 | PLANNED |
| Discovery 6 | Smart Lot Adjustment | Plan 04 | PLANNED |
| Discovery 7 | Symbol-Specific Recovery Windows | Plan 03 | PLANNED |
| Discovery 8 | Chain Level Tracking | Plan 03, 05 | PLANNED |

---

## COVERAGE MATRIX: V5 REQUIREMENTS (78 Total)

### Category 1: Core Plugin System (8 Requirements)
| REQ # | Description | Plan | Status |
|-------|-------------|------|--------|
| REQ-1.1 | BaseLogicPlugin Abstract Class | Already Done | DONE |
| REQ-1.2 | Plugin Registry | Already Done | DONE |
| REQ-1.3 | Plugin Loader | Already Done | DONE |
| REQ-1.4 | Plugin Lifecycle Management | Already Done | DONE |
| REQ-1.5 | Plugin Configuration Isolation | Already Done | DONE |
| REQ-1.6 | Plugin Enable/Disable via Telegram | Plan 07 | PLANNED |
| REQ-1.7 | Plugin Hot-Reload | Already Done | DONE |
| REQ-1.8 | Plugin Versioning | Already Done | DONE |

### Category 2: Plugin Wiring (6 Requirements)
| REQ # | Description | Plan | Status |
|-------|-------------|------|--------|
| REQ-2.1 | TradingEngine Plugin Delegation | Plan 01 | PLANNED |
| REQ-2.2 | Webhook → Plugin Routing | Plan 02 | PLANNED |
| REQ-2.3 | Plugin Signal Handler Registration | Plan 02 | PLANNED |
| REQ-2.4 | Plugin Order Tagging | Plan 04 | PLANNED |
| REQ-2.5 | Plugin Isolation Guarantee | Plan 09 | PLANNED |
| REQ-2.6 | Plugin Priority System | Plan 02 | PLANNED |

### Category 3: Multi-Database (7 Requirements)
| REQ # | Description | Plan | Status |
|-------|-------------|------|--------|
| REQ-3.1 | Database Per Plugin | Plan 09 | PLANNED |
| REQ-3.2 | V3 Combined Schema | Already Done | DONE |
| REQ-3.3 | V6 Price Action Schema | Already Done | DONE |
| REQ-3.4 | Database Connection Manager | Already Done | DONE |
| REQ-3.5 | Database Sync Service | Already Done | DONE |
| REQ-3.6 | Trade Migration Tool | Already Done | DONE |
| REQ-3.7 | Database Isolation Verification | Plan 09 | PLANNED |

### Category 4: Service API (8 Requirements)
| REQ # | Description | Plan | Status |
|-------|-------------|------|--------|
| REQ-4.1 | ServiceAPI Singleton | Already Done | DONE |
| REQ-4.2 | Order Execution Service | Already Done | DONE |
| REQ-4.3 | Risk Management Service | Already Done | DONE |
| REQ-4.4 | Profit Booking Service | Already Done | DONE |
| REQ-4.5 | Trend Monitor Service | Already Done | DONE |
| REQ-4.6 | Service Registration with Plugins | Plan 08 | PLANNED |
| REQ-4.7 | Service Fallback to Legacy | Already Done | DONE |
| REQ-4.8 | Service Metrics Collection | Plan 08 | PLANNED |

### Category 5: 3-Bot Telegram (9 Requirements)
| REQ # | Description | Plan | Status |
|-------|-------------|------|--------|
| REQ-5.1 | Controller Bot | Already Done | DONE |
| REQ-5.2 | Notification Bot | Already Done | DONE |
| REQ-5.3 | Analytics Bot | Already Done | DONE |
| REQ-5.4 | Multi-Telegram Manager | Already Done | DONE |
| REQ-5.5 | Message Router | Already Done | DONE |
| REQ-5.6 | 3-Bot Integration with Core | Plan 07 | PLANNED |
| REQ-5.7 | Command Routing to Controller | Plan 07 | PLANNED |
| REQ-5.8 | Notification Routing | Plan 07 | PLANNED |
| REQ-5.9 | Analytics Routing | Plan 07 | PLANNED |

### Category 6-14: Remaining Requirements
(See individual plans for detailed coverage)

**Summary:**
- **Already Done:** 35 requirements (45%)
- **Planned:** 43 requirements (55%)
- **Total Coverage:** 78/78 (100%)

---

## FEATURE PRESERVATION MATRIX (47 Features)

All 47 original bot features from Study Report 01 will be preserved:

| Category | Features | Preservation Plan |
|----------|----------|-------------------|
| Trading Logic (8) | V3 Integration, Multi-TF Logic, etc. | Plans 01, 02 |
| Dual Order (5) | Order A, Order B, Smart Lot, etc. | Plan 04 |
| Re-Entry (7) | SL Hunt, TP Cont, Exit Cont, etc. | Plan 03 |
| Profit Booking (6) | 5-Level Pyramid, Chain Progression, etc. | Plan 05 |
| Risk Management (6) | Tiers, Daily Limit, Lifetime Limit, etc. | Plans 04, 06 |
| SL System (4) | Dual SL, Symbol-Specific, etc. | Plan 04 |
| Autonomous (5) | ASM, Daily Limits, Reverse Shield, etc. | Plan 06 |
| Telegram (6) | Commands, Menus, Voice, Notifications | Plan 07 |
| Database (4) | Trade DB, History, Chains, Stats | Plan 09 |
| Configuration (4) | Main Config, Env, Trends, Mapping | All Plans |
| Monitoring (3) | Health, Stats, Connection | Plan 12 |
| Safety (4) | Panic Close, Daily Reset, Logs, Sessions | Plan 07 |

---

## RISK ASSESSMENT

### High Risk Items
| Risk | Mitigation | Plan |
|------|------------|------|
| Breaking re-entry system | Shadow mode testing | Plan 11 |
| Breaking dual orders | Unit tests per order type | Plan 12 |
| Breaking profit chains | Chain state verification | Plan 12 |
| Telegram disruption | Gradual migration with fallback | Plan 07 |

### Medium Risk Items
| Risk | Mitigation | Plan |
|------|------------|------|
| Database corruption | Backup before migration | Plan 09 |
| Service API failures | Fallback to legacy managers | Plan 08 |
| Plugin isolation breach | Isolation tests | Plan 09 |

### Low Risk Items
| Risk | Mitigation | Plan |
|------|------------|------|
| Plugin renaming issues | Simple folder rename | Plan 10 |
| Config hot-reload | Already tested | N/A |

---

## TIMELINE SUMMARY

| Phase | Plans | Duration | Cumulative |
|-------|-------|----------|------------|
| Phase 1: Core | 01, 02 | 5-7 days | Week 1 |
| Phase 2: Features | 03, 04, 05 | 10-13 days | Week 2-3 |
| Phase 3: Integration | 06, 07, 08 | 9-12 days | Week 3-4 |
| Phase 4: Finalization | 09, 10, 11, 12 | 9-13 days | Week 4-5 |

**Total Estimated Time:** 33-45 days (5-7 weeks)

---

## SUCCESS CRITERIA

The V5 Surgery is COMPLETE when:

1. ✅ All 12 plans executed successfully
2. ✅ All 10 gaps addressed and verified
3. ✅ All 8 discoveries integrated
4. ✅ All 78 V5 requirements implemented
5. ✅ All 47 original features preserved
6. ✅ Shadow mode shows 100% behavior match
7. ✅ All integration tests passing
8. ✅ All E2E tests passing
9. ✅ 3-Bot Telegram system fully operational
10. ✅ User approval received

---

## PLAN FILE INDEX

| File | Description |
|------|-------------|
| `00_MASTER_PLAN_INDEX.md` | This file - Master index |
| `01_CORE_CLEANUP_PLAN.md` | Core cleanup and plugin delegation |
| `02_WEBHOOK_ROUTING_PLAN.md` | Webhook routing and signal processing |
| `03_REENTRY_SYSTEM_PLAN.md` | Re-entry system integration |
| `04_DUAL_ORDER_PLAN.md` | Dual order system integration |
| `05_PROFIT_BOOKING_PLAN.md` | Profit booking integration |
| `06_AUTONOMOUS_SYSTEM_PLAN.md` | Autonomous system integration |
| `07_3BOT_TELEGRAM_PLAN.md` | 3-Bot Telegram migration |
| `08_SERVICE_API_PLAN.md` | Service API integration |
| `09_DATABASE_ISOLATION_PLAN.md` | Database isolation |
| `10_PLUGIN_RENAMING_PLAN.md` | Plugin renaming and structure |
| `11_SHADOW_MODE_PLAN.md` | Shadow mode testing |
| `12_E2E_TESTING_PLAN.md` | Integration and E2E testing |

---

## REFERENCES

- **Study Report 01:** Original Bot Features (47 features)
- **Study Report 02:** V5 Planning Requirements (78 requirements)
- **Study Report 03:** Telegram System Audit (95+ commands, 50+ notifications)
- **Study Report 04:** Gap Analysis (10 gaps, 8 discoveries)
- **Original Surgery Plans:** 00-06 in `03_SURGERY_PLANS/`
- **V5 Planning Docs:** 01-28 in `01_PLANNING/`
- **Bot Documentation:** `DOCUMENTATION/` directory

---

**END OF MASTER PLAN INDEX**
