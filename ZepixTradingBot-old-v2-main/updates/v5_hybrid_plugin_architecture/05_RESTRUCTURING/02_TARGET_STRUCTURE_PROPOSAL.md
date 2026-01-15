# TARGET STRUCTURE PROPOSAL

**Date:** 2026-01-15
**Created By:** Devin
**Purpose:** Propose clean, professional project structure

---

## 1. DESIGN PRINCIPLES

1. **Python Best Practices** - Follow standard Python project layout
2. **Clear Separation** - Source, tests, docs, config clearly separated
3. **No Duplicates** - Single source of truth for each component
4. **Archive Old** - Move legacy files to archive, don't delete
5. **Preserve Functionality** - All imports must still work
6. **Git-Friendly** - Use git mv to preserve history

---

## 2. PROPOSED STRUCTURE

```
ZepixTradingBot/
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── requirements.txt
├── README.md
├── START_BOT.bat
│
├── src/                          # Source code (UNCHANGED)
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   │
│   ├── api/                      # Webhook API
│   │   ├── __init__.py
│   │   ├── webhook_handler.py
│   │   └── middleware/
│   │
│   ├── clients/                  # External clients
│   │   ├── __init__.py
│   │   ├── mt5_client.py
│   │   ├── telegram_bot.py
│   │   └── telegram_bot_fixed.py
│   │
│   ├── core/                     # Core trading engine
│   │   ├── __init__.py
│   │   ├── trading_engine.py
│   │   ├── config_manager.py
│   │   ├── shadow_mode_manager.py
│   │   ├── plugin_router.py
│   │   │
│   │   ├── plugin_system/        # Plugin architecture
│   │   │   ├── __init__.py
│   │   │   ├── base_plugin.py
│   │   │   ├── plugin_registry.py
│   │   │   ├── service_api.py
│   │   │   └── *_interface.py
│   │   │
│   │   └── services/             # Service layer
│   │       ├── __init__.py
│   │       ├── dual_order_service.py
│   │       ├── profit_booking_service.py
│   │       └── ...
│   │
│   ├── logic_plugins/            # Trading logic plugins
│   │   ├── _template/
│   │   ├── v3_combined/
│   │   ├── v6_price_action_1m/
│   │   ├── v6_price_action_5m/
│   │   ├── v6_price_action_15m/
│   │   └── v6_price_action_1h/
│   │
│   ├── managers/                 # Business logic managers
│   │   ├── __init__.py
│   │   └── ...
│   │
│   ├── telegram/                 # 3-Bot Telegram system
│   │   ├── __init__.py
│   │   ├── base_telegram_bot.py
│   │   ├── controller_bot.py
│   │   ├── notification_bot.py
│   │   ├── analytics_bot.py
│   │   └── ...
│   │
│   ├── menu/                     # Menu system
│   ├── models/                   # Data models (CONSOLIDATED)
│   ├── modules/                  # Voice alerts, sessions
│   ├── monitoring/               # Health monitoring
│   ├── processors/               # Alert processing
│   ├── services/                 # Analytics, price monitor
│   └── utils/                    # Utilities
│
├── tests/                        # Test files (CLEANED UP)
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   │
│   ├── unit/                     # Unit tests (NEW)
│   │   └── ...
│   │
│   ├── integration/              # Integration tests (NEW)
│   │   ├── test_core_delegation.py
│   │   ├── test_webhook_routing.py
│   │   ├── test_reentry_integration.py
│   │   ├── test_dual_order_integration.py
│   │   ├── test_profit_booking_integration.py
│   │   ├── test_autonomous_integration.py
│   │   ├── test_3bot_telegram.py
│   │   ├── test_service_api_integration.py
│   │   ├── test_database_isolation.py
│   │   ├── test_plugin_naming.py
│   │   └── test_shadow_mode.py
│   │
│   ├── batch/                    # Batch tests (NEW)
│   │   ├── test_batch_02_schemas.py
│   │   ├── test_batch_03_services.py
│   │   └── ...
│   │
│   └── _archive/                 # Archived tests (NEW)
│       ├── test_menu_live_unicode_safe.py
│       ├── test_session_menu_handler.py
│       └── ...
│
├── config/                       # Configuration (UNCHANGED)
│   ├── plugins/
│   └── ...
│
├── data/                         # Data storage (UNCHANGED)
│   ├── schemas/
│   ├── backups/
│   └── ...
│
├── scripts/                      # Utility scripts (CLEANED UP)
│   ├── start_bot.py
│   ├── run_bot.py
│   ├── run_all_tests.py
│   ├── deploy/                   # Deployment scripts (NEW)
│   │   ├── DEPLOY_AND_TEST_BOT.py
│   │   └── deploy_bot_permanent.py
│   │
│   └── _archive/                 # Archived scripts (NEW)
│       ├── fix_*.py
│       ├── patch_*.py
│       └── deepseek_*.py
│
├── docs/                         # Documentation (CONSOLIDATED)
│   ├── README.md
│   ├── api/
│   ├── guides/
│   ├── developer/                # Developer docs (RENAMED)
│   ├── implementation/
│   ├── testing/
│   ├── tradingview/
│   ├── setup/                    # Setup files (RENAMED)
│   │
│   └── _archive/                 # Archived docs (NEW)
│       ├── debug_reports/
│       ├── verification-reports/
│       ├── V3_FINAL_REPORTS/
│       └── old_logs/
│
├── logs/                         # Log files (UNCHANGED)
│
├── assets/                       # Static assets (UNCHANGED)
│
└── _archive/                     # Project archive (CONSOLIDATED)
    ├── legacy_docs/              # From DOCUMENTATION/, PLAN/
    ├── devin_reports/            # From _devin_reports/
    ├── root_audits/              # Root level audit files
    ├── old_archive/              # From archive/
    └── temp_scripts/             # Temporary scripts
```

---

## 3. CHANGES SUMMARY

### 3.1 Source Code (`src/`)

| Change | Reason |
|--------|--------|
| **NO CHANGES** | Source code structure is already clean |
| Consolidate model files | Remove duplicates |

**Model Consolidation:**
- KEEP: `src/models/v3_alert.py`
- ARCHIVE: `src/models.py` (if duplicate)
- ARCHIVE: `src/v3_alert_models.py` (if duplicate)
- ARCHIVE: `src/minimal_app.py` (if unused)

### 3.2 Tests (`tests/`)

| Change | Reason |
|--------|--------|
| Create `tests/unit/` | Organize unit tests |
| Create `tests/integration/` | Organize integration tests |
| Create `tests/batch/` | Organize batch tests |
| Create `tests/_archive/` | Archive broken tests |
| Add `conftest.py` | Pytest configuration |

**Files to Move to `tests/integration/`:**
- `test_core_delegation.py`
- `test_webhook_routing.py`
- `test_reentry_integration.py`
- `test_dual_order_integration.py`
- `test_profit_booking_integration.py`
- `test_autonomous_integration.py`
- `test_3bot_telegram.py`
- `test_service_api_integration.py`
- `test_database_isolation.py`
- `test_plugin_naming.py`
- `test_shadow_mode.py`

**Files to Move to `tests/batch/`:**
- `test_batch_*.py` (all batch tests)

**Files to Move to `tests/_archive/`:**
- `test_menu_live_unicode_safe.py`
- `test_menu_live.py`
- `test_menu_handler*.py`
- `test_session_menu_handler.py`
- `test_ui_integration.py`
- `test_voice_alert_system.py`
- `v3_all_10_symbols_test.py`
- All files in `tests/audits/`
- All files in `tests/bible_suite/`
- All files in `tests/simulations/`

### 3.3 Scripts (`scripts/`)

| Change | Reason |
|--------|--------|
| Create `scripts/deploy/` | Organize deployment scripts |
| Create `scripts/_archive/` | Archive old fix scripts |

**Files to Keep in `scripts/`:**
- `start_bot.py`
- `run_bot.py`
- `run_all_tests.py`
- `rename_plugins.py`
- `reset_stats.py`

**Files to Move to `scripts/deploy/`:**
- `DEPLOY_AND_TEST_BOT.py`
- `deploy_bot_permanent.py`
- `auto_deploy_and_test.py`

**Files to Move to `scripts/_archive/`:**
- `fix_*.py` (all fix scripts)
- `patch_*.py` (all patch scripts)
- `deepseek_*.py` (all deepseek scripts)
- `verify_*.py` (verification scripts)

### 3.4 Documentation (`docs/`)

| Change | Reason |
|--------|--------|
| Rename `developer_notes/` to `developer/` | Cleaner name |
| Rename `Zepix Setup Files/` to `setup/` | No spaces |
| Create `docs/_archive/` | Archive old docs |
| Move `DOCUMENTATION/` contents | Consolidate |
| Move `PLAN/` contents | Consolidate |
| Move `_devin_reports/` contents | Consolidate |

**Files to Move to `docs/_archive/`:**
- `docs/debug_reports/`
- `docs/verification-reports/`
- `docs/V3_FINAL_REPORTS/`
- `docs/log *-12-25/` directories

### 3.5 Root Level

| Change | Reason |
|--------|--------|
| Create `_archive/` | Consolidated archive |
| Move audit files | Clean root |
| Delete `bot_debug.log` | Temporary file |

**Files to Move to `_archive/root_audits/`:**
- `DEEPSEEK_AUDIT_FINAL.md`
- `DEEPSEEK_DEEP_REASONING_AUDIT_REPORT.md`
- `PINE_BOT_AUTONOMOUS_AUDIT.md`
- `PROJECT_MEMORY_RESTORED.md`
- `PROJECT_SCAN_REPORT_DEEPSEEK_V2.md`

**Directories to Move to `_archive/`:**
- `DOCUMENTATION/` → `_archive/legacy_docs/DOCUMENTATION/`
- `PLAN/` → `_archive/legacy_docs/PLAN/`
- `_devin_reports/` → `_archive/devin_reports/`
- `archive/` → `_archive/old_archive/`

---

## 4. MIGRATION PLAN

### Phase 1: Preparation (No File Moves)
1. Create all new directories
2. Create `tests/conftest.py`
3. Verify all tests still pass

### Phase 2: Test Reorganization
1. Move integration tests to `tests/integration/`
2. Move batch tests to `tests/batch/`
3. Move broken tests to `tests/_archive/`
4. Update import paths if needed
5. Verify all tests still pass

### Phase 3: Script Reorganization
1. Move deployment scripts to `scripts/deploy/`
2. Move archive scripts to `scripts/_archive/`
3. Verify scripts still work

### Phase 4: Documentation Consolidation
1. Move old docs to `docs/_archive/`
2. Rename directories (no spaces)
3. Move legacy doc directories to `_archive/`

### Phase 5: Root Cleanup
1. Create `_archive/` directory
2. Move root audit files
3. Move legacy directories
4. Delete temporary files

### Phase 6: Verification
1. Run full test suite
2. Verify bot starts
3. Verify all imports work
4. Update any broken paths

---

## 5. SAFETY MEASURES

### 5.1 Before Any Changes
- [ ] Create backup branch
- [ ] Run full test suite (baseline)
- [ ] Document current test count

### 5.2 During Migration
- [ ] Use `git mv` for all moves (preserve history)
- [ ] Commit after each phase
- [ ] Run tests after each phase
- [ ] Document any issues

### 5.3 After Migration
- [ ] Run full test suite
- [ ] Verify bot starts
- [ ] Update any documentation
- [ ] Create migration report

---

## 6. IMPORT PATH UPDATES

### 6.1 Test Imports
After moving tests to subdirectories, update imports:

```python
# Before (in tests/test_core_delegation.py)
from src.core.trading_engine import TradingEngine

# After (in tests/integration/test_core_delegation.py)
# No change needed - relative imports from project root
from src.core.trading_engine import TradingEngine
```

### 6.2 Script Imports
After moving scripts to subdirectories:

```python
# Before (in scripts/start_bot.py)
from src.main import main

# After (in scripts/deploy/DEPLOY_AND_TEST_BOT.py)
# May need sys.path adjustment
import sys
sys.path.insert(0, '../..')
from src.main import main
```

---

## 7. FILES TO DELETE

| File | Reason |
|------|--------|
| `bot_debug.log` | Temporary log file |
| `archive/temp_scripts/` | Temporary scripts |
| `docs/log *-12-25/` | Old log directories |
| `__pycache__/` directories | Python cache |
| `.pytest_cache/` | Pytest cache |

---

## 8. ESTIMATED IMPACT

| Metric | Before | After |
|--------|--------|-------|
| Root level files | 13 | 8 |
| Root level directories | 14 | 9 |
| Test organization | Flat | Hierarchical |
| Script organization | Flat | Hierarchical |
| Doc locations | 4 | 1 |
| Archive locations | 1 | 1 (consolidated) |

---

## 9. ROLLBACK PLAN

If issues occur:
1. `git checkout -b backup-before-restructure` (before starting)
2. `git reset --hard backup-before-restructure` (if needed)
3. All moves use `git mv` so history is preserved

---

## 10. APPROVAL REQUIRED

**Before proceeding, user must approve:**

1. [ ] Target structure is acceptable
2. [ ] Migration phases are acceptable
3. [ ] Files to archive are acceptable
4. [ ] Files to delete are acceptable

**DO NOT MOVE FILES UNTIL USER APPROVES THIS PROPOSAL**

---

**END OF PROPOSAL**
