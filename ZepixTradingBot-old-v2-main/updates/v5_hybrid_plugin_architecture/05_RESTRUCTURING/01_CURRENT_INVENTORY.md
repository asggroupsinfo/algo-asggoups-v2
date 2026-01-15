# PROJECT CURRENT INVENTORY

**Date:** 2026-01-15
**Scanned By:** Devin
**Purpose:** Document current project structure before restructuring

---

## 1. PROJECT STATISTICS

| Metric | Count |
|--------|-------|
| **Total Python Files** | 311 |
| **Total Directories** | 139 |
| **Markdown Files** | 522 |
| **JSON Files** | 18 |
| **SQL Files** | 3 |
| **Root Level Files** | 13 |

---

## 2. DIRECTORY SIZE ANALYSIS

| Directory | Size | Purpose |
|-----------|------|---------|
| `docs/` | 9.4M | Documentation (largest) |
| `src/` | 4.7M | Source code |
| `tests/` | 4.0M | Test files |
| `updates/` | 2.8M | V5 migration docs |
| `archive/` | 2.1M | Archived files |
| `assets/` | 1.9M | Static assets |
| `data/` | 508K | Data files |
| `scripts/` | 372K | Utility scripts |
| `DOCUMENTATION/` | 308K | Legacy docs |
| `PLAN/` | 228K | Legacy plans |
| `_devin_reports/` | 152K | Devin audit reports |
| `config/` | 120K | Configuration |
| `logs/` | 4.0K | Log files |

---

## 3. ROOT LEVEL FILES (13 files)

| File | Type | Status |
|------|------|--------|
| `.env.example` | Config | KEEP |
| `.gitignore` | Config | KEEP |
| `.pre-commit-config.yaml` | Config | KEEP |
| `DEEPSEEK_AUDIT_FINAL.md` | Doc | ARCHIVE |
| `DEEPSEEK_DEEP_REASONING_AUDIT_REPORT.md` | Doc | ARCHIVE |
| `PINE_BOT_AUTONOMOUS_AUDIT.md` | Doc | ARCHIVE |
| `PROJECT_MEMORY_RESTORED.md` | Doc | ARCHIVE |
| `PROJECT_SCAN_REPORT_DEEPSEEK_V2.md` | Doc | ARCHIVE |
| `README.md` | Doc | KEEP |
| `START_BOT.bat` | Script | KEEP |
| `bot_debug.log` | Log | DELETE |
| `pyproject.toml` | Config | KEEP |
| `requirements.txt` | Config | KEEP |

---

## 4. TOP-LEVEL DIRECTORIES

### 4.1 CORE DIRECTORIES (KEEP)

| Directory | Files | Purpose | Status |
|-----------|-------|---------|--------|
| `src/` | 85 | Main source code | KEEP - Core |
| `tests/` | 89 | Test files | KEEP - Cleanup needed |
| `config/` | 5 | Configuration files | KEEP |
| `data/` | 12 | Data storage | KEEP |
| `scripts/` | 53 | Utility scripts | KEEP - Cleanup needed |
| `logs/` | 1 | Log files | KEEP |

### 4.2 DOCUMENTATION DIRECTORIES (CONSOLIDATE)

| Directory | Files | Purpose | Status |
|-----------|-------|---------|--------|
| `docs/` | 200+ | Main documentation | KEEP - Primary |
| `DOCUMENTATION/` | 15 | Legacy docs | ARCHIVE |
| `PLAN/` | 10 | Legacy plans | ARCHIVE |
| `updates/` | 100+ | V5 migration docs | KEEP - Important |
| `_devin_reports/` | 20 | Audit reports | ARCHIVE |

### 4.3 ARCHIVE DIRECTORIES (CLEANUP)

| Directory | Files | Purpose | Status |
|-----------|-------|---------|--------|
| `archive/` | 30+ | Old files | REVIEW |
| `assets/` | 50+ | Static assets | REVIEW |

---

## 5. SOURCE CODE STRUCTURE (`src/`)

### 5.1 Core Modules

| Directory | Files | Purpose |
|-----------|-------|---------|
| `src/core/` | 15 | Core trading engine, plugin system |
| `src/core/plugin_system/` | 10 | Plugin interfaces and registry |
| `src/core/services/` | 7 | Service layer (orders, profits, etc.) |

### 5.2 Logic Plugins

| Directory | Files | Purpose |
|-----------|-------|---------|
| `src/logic_plugins/v3_combined/` | 6 | V3 Combined Logic plugin |
| `src/logic_plugins/v6_price_action_1m/` | 2 | V6 1-minute plugin |
| `src/logic_plugins/v6_price_action_5m/` | 2 | V6 5-minute plugin |
| `src/logic_plugins/v6_price_action_15m/` | 2 | V6 15-minute plugin |
| `src/logic_plugins/v6_price_action_1h/` | 2 | V6 1-hour plugin |
| `src/logic_plugins/_template/` | 1 | Plugin template |

### 5.3 Managers

| Directory | Files | Purpose |
|-----------|-------|---------|
| `src/managers/` | 15 | Business logic managers |

### 5.4 Telegram

| Directory | Files | Purpose |
|-----------|-------|---------|
| `src/telegram/` | 15 | 3-Bot Telegram system |

### 5.5 Other Modules

| Directory | Files | Purpose |
|-----------|-------|---------|
| `src/api/` | 4 | Webhook API |
| `src/clients/` | 6 | MT5 and Telegram clients |
| `src/menu/` | 12 | Menu system |
| `src/models/` | 2 | Data models |
| `src/modules/` | 4 | Voice alerts, sessions |
| `src/monitoring/` | 2 | Health monitoring |
| `src/processors/` | 2 | Alert processing |
| `src/services/` | 5 | Analytics, price monitor |
| `src/utils/` | 12 | Utilities |

### 5.6 Root Level Files in `src/`

| File | Purpose | Status |
|------|---------|--------|
| `__init__.py` | Package init | KEEP |
| `config.py` | Configuration | KEEP |
| `database.py` | Database layer | KEEP |
| `main.py` | Entry point | KEEP |
| `minimal_app.py` | Minimal app | REVIEW |
| `models.py` | Models | REVIEW (duplicate?) |
| `v3_alert_models.py` | V3 models | REVIEW (duplicate?) |

---

## 6. TEST STRUCTURE (`tests/`)

### 6.1 V5 Architecture Tests (KEEP)

| File | Tests | Status |
|------|-------|--------|
| `test_core_delegation.py` | 21 | KEEP |
| `test_webhook_routing.py` | 45 | KEEP |
| `test_reentry_integration.py` | 40 | KEEP |
| `test_dual_order_integration.py` | 35 | KEEP |
| `test_profit_booking_integration.py` | 30 | KEEP |
| `test_autonomous_integration.py` | 35 | KEEP |
| `test_3bot_telegram.py` | 40 | KEEP |
| `test_service_api_integration.py` | 25 | KEEP |
| `test_database_isolation.py` | 20 | KEEP |
| `test_plugin_naming.py` | 15 | KEEP |
| `test_shadow_mode.py` | 37 | KEEP |

### 6.2 Batch Tests (KEEP)

| File | Purpose | Status |
|------|---------|--------|
| `test_batch_02_schemas.py` | Schema tests | KEEP |
| `test_batch_03_services.py` | Service tests | KEEP |
| `test_batch_04_telegram.py` | Telegram tests | KEEP |
| `test_batch_05_ux.py` | UX tests | KEEP |
| `test_batch_06_notifications.py` | Notification tests | KEEP |
| `test_batch_07_service_integration.py` | Integration tests | KEEP |
| `test_batch_08_v3_plugin.py` | V3 plugin tests | KEEP |
| `test_batch_09_config_db.py` | Config/DB tests | KEEP |
| `test_batch_10_v6_foundation.py` | V6 foundation tests | KEEP |
| `test_batch_11_health.py` | Health tests | KEEP |
| `test_batch_12_migration.py` | Migration tests | KEEP |
| `test_batch_13_quality.py` | Quality tests | KEEP |

### 6.3 Legacy Tests (REVIEW/ARCHIVE)

| File | Issue | Status |
|------|-------|--------|
| `test_menu_live_unicode_safe.py` | Import error | ARCHIVE |
| `test_menu_live.py` | Import error | ARCHIVE |
| `test_menu_handler*.py` | Import errors | ARCHIVE |
| `test_session_menu_handler.py` | Import error | ARCHIVE |
| `test_ui_integration.py` | Import error | ARCHIVE |
| `test_voice_alert_system.py` | Import error | ARCHIVE |
| `v3_all_10_symbols_test.py` | Import error | ARCHIVE |

### 6.4 Test Subdirectories

| Directory | Files | Status |
|-----------|-------|--------|
| `tests/audits/` | 17 | REVIEW |
| `tests/bible_suite/` | 1 | REVIEW |
| `tests/simulations/` | 1 | REVIEW |

---

## 7. SCRIPTS STRUCTURE (`scripts/`)

### 7.1 Essential Scripts (KEEP)

| File | Purpose |
|------|---------|
| `start_bot.py` | Start bot |
| `run_bot.py` | Run bot |
| `run_all_tests.py` | Run tests |
| `rename_plugins.py` | Plugin renaming |
| `reset_stats.py` | Reset statistics |

### 7.2 Deployment Scripts (KEEP)

| File | Purpose |
|------|---------|
| `DEPLOY_AND_TEST_BOT.py` | Deploy and test |
| `deploy_bot_permanent.py` | Permanent deploy |
| `auto_deploy_and_test.py` | Auto deploy |

### 7.3 Legacy/Debug Scripts (ARCHIVE)

| File | Purpose | Status |
|------|---------|--------|
| `fix_*.py` | Various fixes | ARCHIVE |
| `patch_*.py` | Various patches | ARCHIVE |
| `test_*.py` | Test scripts | REVIEW |
| `verify_*.py` | Verification | REVIEW |
| `deepseek_*.py` | DeepSeek audit | ARCHIVE |

---

## 8. DOCUMENTATION STRUCTURE

### 8.1 `docs/` (Primary - 9.4M)

| Subdirectory | Purpose | Status |
|--------------|---------|--------|
| `api/` | API docs | KEEP |
| `debug_reports/` | Debug reports | ARCHIVE |
| `developer_notes/` | Dev notes | KEEP |
| `guides/` | User guides | KEEP |
| `implementation/` | Implementation docs | KEEP |
| `important/` | Important docs | KEEP |
| `plans/` | Plans | KEEP |
| `reports/` | Reports | REVIEW |
| `testing/` | Testing docs | KEEP |
| `tradingview/` | TradingView docs | KEEP |
| `verification-reports/` | Verification | ARCHIVE |
| `V3_FINAL_REPORTS/` | V3 reports | ARCHIVE |
| `Zepix Setup Files/` | Setup files | KEEP |
| `log *-12-25/` | Old logs | ARCHIVE |

### 8.2 `updates/` (V5 Migration - 2.8M)

| Subdirectory | Purpose | Status |
|--------------|---------|--------|
| `v3_legacy_removal/` | V3 removal | ARCHIVE |
| `v4_forex_session_system/` | V4 forex | ARCHIVE |
| `v5_hybrid_plugin_architecture/` | V5 migration | KEEP - Critical |

### 8.3 Legacy Doc Directories (ARCHIVE)

| Directory | Purpose | Status |
|-----------|---------|--------|
| `DOCUMENTATION/` | Legacy docs | ARCHIVE |
| `PLAN/` | Legacy plans | ARCHIVE |
| `_devin_reports/` | Audit reports | ARCHIVE |

---

## 9. DATA STRUCTURE (`data/`)

| File/Directory | Purpose | Status |
|----------------|---------|--------|
| `schemas/` | SQL schemas | KEEP |
| `backups/` | Backups | KEEP |
| `archive_logs/` | Archived logs | REVIEW |
| `test/` | Test data | REVIEW |
| `*.json` | Data files | KEEP |

---

## 10. ISSUES IDENTIFIED

### 10.1 Duplicate Files

| Issue | Files | Action |
|-------|-------|--------|
| Duplicate models | `src/models.py`, `src/models/v3_alert.py`, `src/v3_alert_models.py` | CONSOLIDATE |
| Multiple menu handlers | `test_menu_handler*.py` (7 versions) | ARCHIVE old versions |

### 10.2 Import Errors in Tests

| File | Error | Action |
|------|-------|--------|
| `test_menu_live_unicode_safe.py` | TelegramBot import | ARCHIVE |
| `test_session_menu_handler.py` | telegram.Update import | ARCHIVE |
| `test_ui_integration.py` | telegram.Update import | ARCHIVE |
| `test_voice_alert_system.py` | telegram.Bot import | ARCHIVE |
| `v3_all_10_symbols_test.py` | TelegramBot import | ARCHIVE |

### 10.3 Scattered Documentation

| Issue | Directories | Action |
|-------|-------------|--------|
| Multiple doc locations | `docs/`, `DOCUMENTATION/`, `PLAN/`, `_devin_reports/` | CONSOLIDATE |
| Old audit files | Root level `*_AUDIT*.md` | ARCHIVE |

### 10.4 Archive Candidates

| Directory | Reason | Action |
|-----------|--------|--------|
| `archive/` | Already archived | REVIEW |
| `archive/temp_scripts/` | Temporary scripts | DELETE |
| `docs/log *-12-25/` | Old logs | DELETE |

---

## 11. SUMMARY

### Files to KEEP (Core)
- `src/` - All source code
- `tests/` - V5 architecture tests and batch tests
- `config/` - Configuration
- `data/` - Data files
- `scripts/` - Essential scripts
- `updates/v5_hybrid_plugin_architecture/` - V5 migration docs

### Files to ARCHIVE
- Root level audit files
- `DOCUMENTATION/`, `PLAN/`, `_devin_reports/`
- Legacy test files with import errors
- Old fix/patch scripts

### Files to DELETE
- `bot_debug.log`
- `archive/temp_scripts/`
- Old log directories

### Files to CONSOLIDATE
- Multiple model files
- Multiple documentation locations

---

**END OF INVENTORY**
