# 🤖 DEVIN AI - TELEGRAM V5 UPGRADE IMPLEMENTATION PROMPT

**Generated:** January 20, 2026  
**Prompt Version:** 1.0  
**Project:** ZepixTradingBot V5 - Telegram System Complete Upgrade  
**Repository:** https://gitlab.com/asggroupsinfo/algo-asggoups-v1

---

## 📋 TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [Your Role & Responsibilities](#your-role--responsibilities)
3. [Pre-Implementation Checklist](#pre-implementation-checklist)
4. [Implementation Phases](#implementation-phases)
5. [Master Progress Tracker](#master-progress-tracker)
6. [Testing Requirements](#testing-requirements)
7. [Documentation Requirements](#documentation-requirements)
8. [Acceptance Criteria](#acceptance-criteria)
9. [Global Non-Negotiable Rules](#global-non-negotiable-rules)

---

## 🎯 PROJECT OVERVIEW

### Context

ZepixTradingBot V5 introduced a **Hybrid Plugin Architecture** combining:
- **V3 Combined Logic:** 4-Pillar trend strategy with LOGIC1/2/3 (5m, 15m, 1h)
- **V6 Price Action:** 4 timeframe plugins (15M, 30M, 1H, 4H)

However, the **Telegram interface was NOT properly upgraded**. Users cannot:
- Identify which V6 timeframe (15M/30M/1H/4H) triggered trades
- Control individual V6 plugins via Telegram
- See V3 vs V6 performance comparison
- Configure V6 settings without editing config files
- Filter notifications by plugin type

### Documentation Location

All planning documentation is in:
```
Updates/telegram_updates/
├── 00_MASTER_PLAN.md                        # Complete project overview
├── 01_COMPLETE_COMMAND_INVENTORY.md         # 95+ commands with wiring code
├── 01_V6_NOTIFICATION_SYSTEM_PLAN.md        # Phase 1 detailed specs
├── 02_NOTIFICATION_SYSTEMS_COMPLETE.md      # Notification types & templates
├── 02_V6_TIMEFRAME_MENU_PLAN.md             # Phase 2 detailed specs
├── 03_MENU_SYSTEMS_ARCHITECTURE.md          # Menu system design
├── 03_PRIORITY_COMMAND_HANDLERS_PLAN.md     # Phase 3 detailed specs
├── 04_ANALYTICS_CAPABILITIES.md             # Analytics features
├── 04_PHASES_4_5_6_SUMMARY.md               # Phases 4-6 specs
├── 05_IMPLEMENTATION_ROADMAP.md             # Week-by-week plan
├── 05_V5_PLUGIN_INTEGRATION.md              # Plugin integration guide
├── 06_V6_PRICE_ACTION_TELEGRAM.md           # V6 requirements
├── 07_IMPROVEMENT_ROADMAP.md                # Future improvements
├── 08_TESTING_DOCUMENTATION.md              # 45+ test cases
├── 09_ERROR_HANDLING_GUIDE.md               # Error codes & handling
├── 10_DATABASE_SCHEMA.md                    # Database structure
├── 11_SERVICEAPI_DOCUMENTATION.md           # 50+ API methods
├── 12_VISUAL_CAPABILITIES_GUIDE.md          # Visual features
└── ... (other supporting docs)
```

### Goal

Implement ALL features documented in `Updates/telegram_updates/` folder to achieve:
- **Command Coverage:** 29% → 100% (67 missing commands)
- **Notification Coverage:** 14% → 100% (43 missing types)
- **V6 Feature Parity:** 5% → 100%
- **Test Coverage:** >80%

---

## 👨‍💻 YOUR ROLE & RESPONSIBILITIES

### What You Must Do

1. **SCAN** - First, completely scan the entire bot codebase to understand architecture
2. **READ** - Read ALL 24 documentation files in `Updates/telegram_updates/`
3. **PLAN** - Create your own implementation plan in `/devin_plans/telegram_upgrade/`
4. **IMPLEMENT** - Implement each phase with your own logic and understanding
5. **TEST** - Write and run tests for every feature
6. **DOCUMENT** - Create completion reports with proof
7. **TRACK** - Update master progress tracker after each phase

### What You Must NOT Do

❌ DO NOT blindly copy code from documentation  
❌ DO NOT skip testing any feature  
❌ DO NOT mark anything complete without proof  
❌ DO NOT proceed to next phase without completing current  
❌ DO NOT delete or overwrite existing working code  
❌ DO NOT create a new project from scratch  

---

## ✅ PRE-IMPLEMENTATION CHECKLIST

Before writing ANY code, you MUST complete these steps:

### Step 1: Repository Scan (Mandatory)

```
[ ] Clone repository: git clone https://gitlab.com/asggroupsinfo/algo-asggoups-v1
[ ] Read Trading_Bot/README.md
[ ] Read Trading_Bot/ROADMAP.md
[ ] Scan src/ folder structure
[ ] Understand plugin architecture (src/core/plugin_system/)
[ ] Understand Telegram architecture (src/telegram/)
[ ] Identify all existing command handlers
[ ] Identify all existing notification methods
```

### Step 2: Documentation Review (Mandatory)

Read these files in ORDER:
```
[ ] 00_MASTER_PLAN.md - Understand full scope
[ ] COMPLETE_TELEGRAM_DOCUMENTATION_INDEX.md - Index of all docs
[ ] 01_COMPLETE_COMMAND_INVENTORY.md - All 95+ commands
[ ] 02_NOTIFICATION_SYSTEMS_COMPLETE.md - All notification types
[ ] 03_MENU_SYSTEMS_ARCHITECTURE.md - Menu system design
[ ] 05_IMPLEMENTATION_ROADMAP.md - Week-by-week timeline
[ ] 08_TESTING_DOCUMENTATION.md - Test cases to implement
```

### Step 3: Create Planning Documents

Create these files BEFORE coding:
```
/devin_plans/telegram_upgrade/
├── architecture_summary.md      # Your understanding of current architecture
├── risk_assessment.md           # What could go wrong
├── implementation_plan.md       # Your detailed plan (not copy of docs)
├── testing_strategy.md          # How you will test
└── rollback_plan.md             # How to undo if things break
```

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: V6 Notification System (16 hours)

**Goal:** Users can identify V6 trades by timeframe

**Documentation:** `01_V6_NOTIFICATION_SYSTEM_PLAN.md`

**Tasks:**
```
[ ] 1.1 Read existing notification_bot.py and understand structure
[ ] 1.2 Implement send_v6_entry_alert() method
[ ] 1.3 Implement send_v6_exit_alert() method
[ ] 1.4 Implement send_trend_pulse_alert() method
[ ] 1.5 Add timeframe identification in all V6 alerts
[ ] 1.6 Add visual distinction (🟢 for V6, 🔵 for V3)
[ ] 1.7 Add shadow mode flag in notifications
[ ] 1.8 Write unit tests (11 test cases from 08_TESTING_DOCUMENTATION.md)
[ ] 1.9 Run integration tests
[ ] 1.10 Update progress tracker
```

**Files to Modify:**
- `src/telegram/notification_bot.py`
- `src/telegram/notification_router.py`

**Files to Create:**
- `tests/telegram/test_notification_bot_v6.py`

**Acceptance Criteria:**
- [ ] V6 entry alerts show timeframe (15M/30M/1H/4H)
- [ ] V6 alerts visually distinct from V3
- [ ] Shadow mode trades flagged
- [ ] All 11 unit tests pass
- [ ] Integration with existing notification system works

---

### Phase 2: V6 Timeframe Menu (20 hours)

**Goal:** Users can control individual V6 timeframe plugins

**Documentation:** `02_V6_TIMEFRAME_MENU_PLAN.md`

**Tasks:**
```
[ ] 2.1 Read existing plugin_control_menu.py
[ ] 2.2 Create v6_timeframe_menu_builder.py (new file)
[ ] 2.3 Implement V6 submenu showing 4 timeframes
[ ] 2.4 Implement individual enable/disable toggles
[ ] 2.5 Implement per-timeframe configuration menus
[ ] 2.6 Implement performance comparison view
[ ] 2.7 Add bulk actions (Enable All, Disable All)
[ ] 2.8 Fix menu_v6_settings callback
[ ] 2.9 Write unit tests (12 test cases)
[ ] 2.10 Test menu navigation flow
[ ] 2.11 Update progress tracker
```

**Files to Modify:**
- `src/telegram/plugin_control_menu.py`

**Files to Create:**
- `src/telegram/v6_timeframe_menu_builder.py`
- `tests/telegram/test_v6_timeframe_menu.py`

**Acceptance Criteria:**
- [ ] Can enable/disable each V6 timeframe independently
- [ ] Per-timeframe performance metrics displayed
- [ ] Configuration persists across restarts
- [ ] All 12 unit tests pass

---

### Phase 3: Priority Command Handlers (32 hours)

**Goal:** Top 20 most-critical commands functional

**Documentation:** `03_PRIORITY_COMMAND_HANDLERS_PLAN.md`

**Tasks (Tier 1 - Week 3):**
```
[ ] 3.1 Enhance /status with V3 vs V6 breakdown
[ ] 3.2 Implement plugin-aware /positions
[ ] 3.3 Implement per-plugin /pnl
[ ] 3.4 Implement /chains (re-entry status)
[ ] 3.5 Implement /daily (trigger daily report)
[ ] 3.6 Implement /weekly (trigger weekly report)
[ ] 3.7 Implement /compare (V3 vs V6 comparison)
[ ] 3.8 Implement /setlot (lot size control)
[ ] 3.9 Implement /risktier (risk tier selection)
[ ] 3.10 Implement /autonomous (re-entry toggle)
```

**Tasks (Tier 2 - Week 4):**
```
[ ] 3.11 Implement /tf15m, /tf30m, /tf1h, /tf4h toggles
[ ] 3.12 Implement /slhunt (SL Hunt status)
[ ] 3.13 Implement /tpcontinue (TP Continuation status)
[ ] 3.14 Implement /reentry (overview)
[ ] 3.15 Implement /levels (profit booking status)
[ ] 3.16 Implement /shadow (shadow mode comparison)
[ ] 3.17 Implement /trends (multi-timeframe trends)
[ ] 3.18 Write unit tests (50+ test cases)
[ ] 3.19 Run full command test suite
[ ] 3.20 Update progress tracker
```

**Files to Modify:**
- `src/telegram/controller_bot.py`
- `src/telegram/command_registry.py`

**Files to Create:**
- `tests/telegram/test_priority_commands.py`

**Acceptance Criteria:**
- [ ] All 20 priority commands functional
- [ ] Commands are plugin-aware (filter V3/V6)
- [ ] All 50 unit tests pass

---

### Phase 4: Analytics Command Interface (24 hours)

**Goal:** On-demand analytics via commands

**Documentation:** `04_PHASES_4_5_6_SUMMARY.md` (Phase 4 section)

**Tasks:**
```
[ ] 4.1 Wire /performance to Analytics Bot
[ ] 4.2 Wire /daily, /weekly commands
[ ] 4.3 Wire /compare command
[ ] 4.4 Implement date range selection menu
[ ] 4.5 Implement plugin filtering (V3/V6)
[ ] 4.6 Implement symbol filtering
[ ] 4.7 Implement CSV export
[ ] 4.8 Add V6 timeframe breakdown in reports
[ ] 4.9 Write unit tests
[ ] 4.10 Update progress tracker
```

**Files to Modify:**
- `src/telegram/analytics_bot.py`
- `src/telegram/command_registry.py`

**Files to Create:**
- `src/telegram/analytics_menu_builder.py`
- `tests/telegram/test_analytics_commands.py`

**Acceptance Criteria:**
- [ ] On-demand analytics work
- [ ] Date range selection functional
- [ ] V6 timeframe breakdown shown
- [ ] CSV export works

---

### Phase 5: Notification Filtering System (28 hours)

**Goal:** Users can customize notifications

**Documentation:** `04_PHASES_4_5_6_SUMMARY.md` (Phase 5 section)

**Tasks:**
```
[ ] 5.1 Create notification_preferences_menu.py
[ ] 5.2 Implement per-type notification toggles (50+ types)
[ ] 5.3 Implement per-plugin filtering (V3/V6)
[ ] 5.4 Implement quiet hours
[ ] 5.5 Implement priority levels
[ ] 5.6 Implement /notifications command
[ ] 5.7 Add quick presets (All On, Critical Only)
[ ] 5.8 Implement notification bundling
[ ] 5.9 Create notification_preferences.json
[ ] 5.10 Write unit tests
[ ] 5.11 Update progress tracker
```

**Files to Create:**
- `src/telegram/notification_preferences_menu.py`
- `config/notification_preferences.json`
- `tests/telegram/test_notification_filtering.py`

**Files to Modify:**
- `src/telegram/notification_router.py`

**Acceptance Criteria:**
- [ ] Users can toggle each notification type
- [ ] Plugin filtering works
- [ ] Quiet hours functional
- [ ] Settings persist

---

### Phase 6: Menu Callback Wiring (20 hours)

**Goal:** All menu buttons work

**Documentation:** `04_PHASES_4_5_6_SUMMARY.md` (Phase 6 section)

**Tasks:**
```
[ ] 6.1 Audit all menu callbacks for broken handlers
[ ] 6.2 Wire session menu callbacks
[ ] 6.3 Wire re-entry menu callbacks
[ ] 6.4 Wire fine-tune menu callbacks
[ ] 6.5 Fix all dead-end buttons
[ ] 6.6 Add "Back" navigation to all menus
[ ] 6.7 Test complete menu flow
[ ] 6.8 Write integration tests
[ ] 6.9 Update progress tracker
[ ] 6.10 Final verification
```

**Files to Modify:**
- `src/telegram/controller_bot.py`
- `src/telegram/session_menu_handler.py`
- `src/telegram/menu_builder.py`

**Acceptance Criteria:**
- [ ] All menu buttons functional
- [ ] No dead-end menus
- [ ] Complete navigation flow works

---

## 📊 MASTER PROGRESS TRACKER

**File Location:** `Updates/telegram_updates/DEVIN_MASTER_PROGRESS.md`

Create and maintain this file to track your progress:

```markdown
# 🎯 DEVIN IMPLEMENTATION PROGRESS TRACKER

**Last Updated:** [DATE]
**Current Phase:** [PHASE NUMBER]
**Overall Progress:** [X/6 phases complete]

---

## ✅ COMPLETED PHASES

### Phase 1: V6 Notification System
- **Status:** ✅ COMPLETE / ⏳ IN PROGRESS / ❌ NOT STARTED
- **Started:** [DATE]
- **Completed:** [DATE]
- **Tests Passed:** [X/11]
- **Proof:** [Link to test output / screenshot]
- **Commit:** [COMMIT_HASH]
- **Notes:** [Any issues faced]

### Phase 2: V6 Timeframe Menu
- **Status:** ❌ NOT STARTED
- **Tests Passed:** [0/12]
- **Proof:** 
- **Commit:**

### Phase 3: Priority Command Handlers
- **Status:** ❌ NOT STARTED
- **Tests Passed:** [0/50]
- **Proof:**
- **Commit:**

### Phase 4: Analytics Command Interface
- **Status:** ❌ NOT STARTED
- **Proof:**
- **Commit:**

### Phase 5: Notification Filtering System
- **Status:** ❌ NOT STARTED
- **Proof:**
- **Commit:**

### Phase 6: Menu Callback Wiring
- **Status:** ❌ NOT STARTED
- **Proof:**
- **Commit:**

---

## 📋 DAILY LOG

### [DATE]
- **Phase:** [X]
- **Tasks Completed:**
  - [Task 1]
  - [Task 2]
- **Tests Run:** [X passed, Y failed]
- **Issues:** [Any blockers]
- **Next:** [What to do tomorrow]

---

## 🧪 TEST RESULTS SUMMARY

| Phase | Tests | Passed | Failed | Coverage |
|-------|-------|--------|--------|----------|
| 1     | 11    | ?      | ?      | ?%       |
| 2     | 12    | ?      | ?      | ?%       |
| 3     | 50    | ?      | ?      | ?%       |
| 4     | ?     | ?      | ?      | ?%       |
| 5     | ?     | ?      | ?      | ?%       |
| 6     | ?     | ?      | ?      | ?%       |

---

## 📦 FILES CREATED

| File | Phase | Status |
|------|-------|--------|
| src/telegram/v6_timeframe_menu_builder.py | 2 | ❌ |
| src/telegram/analytics_menu_builder.py | 4 | ❌ |
| src/telegram/notification_preferences_menu.py | 5 | ❌ |
| tests/telegram/test_notification_bot_v6.py | 1 | ❌ |
| tests/telegram/test_v6_timeframe_menu.py | 2 | ❌ |
| tests/telegram/test_priority_commands.py | 3 | ❌ |
| tests/telegram/test_analytics_commands.py | 4 | ❌ |
| tests/telegram/test_notification_filtering.py | 5 | ❌ |

---

## 📦 FILES MODIFIED

| File | Phases | Changes |
|------|--------|---------|
| src/telegram/notification_bot.py | 1 | Add V6 methods |
| src/telegram/controller_bot.py | 3, 6 | Add command handlers |
| ... | ... | ... |
```

---

## 🧪 TESTING REQUIREMENTS

### Mandatory Testing

1. **Unit Tests:** Every new method must have unit tests
2. **Integration Tests:** Every phase must have integration tests
3. **Regression Tests:** Existing features must still work
4. **Manual Tests:** Commands must work via actual Telegram

### Test Execution

After each phase:
```bash
# Run unit tests
pytest tests/telegram/test_*.py -v

# Run with coverage
pytest tests/telegram/ --cov=src/telegram --cov-report=html

# Output must show >80% coverage
```

### Test Proof

For each phase, provide:
1. Test output log (copy/paste)
2. Coverage report screenshot
3. Manual test screenshots from Telegram

---

## 📝 DOCUMENTATION REQUIREMENTS

### Per-Phase Documentation

Create in `/devin_reports/telegram_upgrade/phase_X/`:
```
phase_X/
├── changes.md          # What was changed
├── implementation.md   # How it was implemented
├── test_results.md     # Test outputs
├── screenshots/        # Manual test proof
└── lessons_learned.md  # Issues faced
```

### Final Documentation

After ALL phases complete:
```
/devin_reports/telegram_upgrade/
├── FINAL_REPORT.md     # Complete summary
├── TEST_EVIDENCE.md    # All test proofs
├── BEFORE_AFTER.md     # Comparison screenshots
└── HANDOVER.md         # For maintenance
```

---

## ✅ ACCEPTANCE CRITERIA

### Phase Completion Checklist

A phase is ONLY complete when:
```
[ ] All tasks in phase checklist are done
[ ] All unit tests pass
[ ] All integration tests pass
[ ] Manual Telegram testing verified
[ ] Test proof screenshots captured
[ ] Progress tracker updated
[ ] Commit pushed with proper message
```

### Project Completion Checklist

Project is ONLY complete when:
```
[ ] All 6 phases marked complete
[ ] >80% test coverage achieved
[ ] All 95+ commands functional (verify with test)
[ ] All menu buttons work (verify with flow test)
[ ] V6 notifications distinguish timeframes
[ ] Notification filtering works
[ ] Final documentation complete
[ ] All commits pushed to GitLab
```

---

## 🔴 GLOBAL NON-NEGOTIABLE RULES

**YOU MUST FOLLOW THESE RULES WITHOUT EXCEPTION:**

### Rule 1: Existing Production Bot
This is an **EXISTING PRODUCTION BOT** with real users. The GitLab repository is the **SINGLE SOURCE OF TRUTH**.

### Rule 2: Forbidden Actions
❌ **DO NOT** delete any files or folders  
❌ **DO NOT** overwrite base logic without reason  
❌ **DO NOT** create a fresh project from scratch  
❌ **DO NOT** treat this as a new repository  
❌ **DO NOT** skip scanning the existing codebase  
❌ **DO NOT** ignore existing patterns and architecture  

### Rule 3: Required Actions
✅ **DO** work only on top of existing code  
✅ **DO** preserve all legacy behavior  
✅ **DO** one plan = one commit (don't mix features)  
✅ **DO** write tests for every feature  
✅ **DO** document every change  
✅ **DO** push immediately after each phase  

### Rule 4: Before Writing Any Code
```
Step 1: Full repo scan + architecture summary
Step 2: Create plan documents in /devin_plans/
Step 3: Get understanding of existing patterns
```

### Rule 5: Implementation Process
```
Step 1: Implement features minimally and safely
Step 2: Reuse existing patterns and modules
Step 3: Write tests in /tests/plan_<NUMBER>/
Step 4: Ensure old features still pass
```

### Rule 6: Documentation Process
```
Step 1: Document in /devin_reports/telegram_upgrade/
Step 2: Include changes.md, test_results.md, screenshots
Step 3: Create legacy_check.md confirming old features work
```

### Rule 7: Before Every Commit
Verify:
```
[ ] Legacy features still work (run existing tests)
[ ] New phase features complete
[ ] Tests pass (unit + integration)
[ ] Documentation done
[ ] No unrelated changes in commit
```

### Rule 8: Commit Format
```
Phase <NUMBER>: <Short description>

- Added: [list new files]
- Modified: [list modified files]  
- Tests: [X tests added, all passing]
- Coverage: [X%]
```

### Rule 9: After Every Commit
```
[ ] Push to GitLab immediately
[ ] Update DEVIN_MASTER_PROGRESS.md
[ ] Explicitly confirm: "Phase X complete. Legacy intact. Tests pass."
```

### Rule 10: Safety Confirmation
After EVERY phase, you MUST write:
```
✅ SAFETY CONFIRMATION - Phase X
- Legacy features verified: YES
- New features tested: YES  
- All tests passing: YES
- Documentation complete: YES
- Pushed to GitLab: YES
```

---

## 🚀 START HERE

1. Clone the repository
2. Read this entire document
3. Read all 24 files in `Updates/telegram_updates/`
4. Create your planning documents
5. Update `DEVIN_MASTER_PROGRESS.md` with "Phase 0: Planning - IN PROGRESS"
6. Begin Phase 1 implementation

**Good luck! Build something amazing.** 🎯
