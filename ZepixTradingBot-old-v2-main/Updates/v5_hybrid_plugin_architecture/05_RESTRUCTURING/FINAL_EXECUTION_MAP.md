# FINAL EXECUTION MAP (USER DEFINED 7-FOLDER STRUCTURE)

**Date:** 2026-01-16  
**Created By:** Devin AI  
**Purpose:** Complete file mapping for USER-DEFINED 7-Folder restructuring  
**Status:** PLANNING ONLY - AWAITING GO SIGNAL

---

## 1. THE 7-FOLDER STRUCTURE (USER DEFINED)

| # | Folder Name | Purpose |
|---|-------------|---------|
| 1 | `Trading_Bot` | THE CODE - Executable bot only |
| 2 | `Trading_Bot_Documentation` | THE GUIDE - V5 Bible only |
| 3 | `Important_Doc_Trading_Bot` | THE LIBRARY - All other docs sorted |
| 4 | `Web_Application` | THE UI - Dashboard code |
| 5 | `Web_Application_Documentation` | Placeholder for future web docs |
| 6 | `Important_Doc_Webapp` | Web plans and specs |
| 7 | `Updates` | HISTORY - Update history |

---

## 2. COMPLETE FILE MAPPING

### 2.1 CODE -> Trading_Bot/

```
[OLD] ./src/                    --> [NEW] Trading_Bot/src/
[OLD] ./config/                 --> [NEW] Trading_Bot/config/
[OLD] ./data/                   --> [NEW] Trading_Bot/data/
[OLD] ./logs/                   --> [NEW] Trading_Bot/logs/
[OLD] ./scripts/                --> [NEW] Trading_Bot/scripts/
[OLD] ./tests/                  --> [NEW] Trading_Bot/tests/
[OLD] ./assets/                 --> [NEW] Trading_Bot/assets/
[OLD] ./.env.example            --> [NEW] Trading_Bot/.env.example
[OLD] ./.gitignore              --> [NEW] Trading_Bot/.gitignore
[OLD] ./.pre-commit-config.yaml --> [NEW] Trading_Bot/.pre-commit-config.yaml
[OLD] ./pyproject.toml          --> [NEW] Trading_Bot/pyproject.toml
[OLD] ./requirements.txt        --> [NEW] Trading_Bot/requirements.txt
[OLD] ./START_BOT.bat           --> [NEW] Trading_Bot/START_BOT.bat
[OLD] ./README.md               --> [NEW] Trading_Bot/README.md
[OLD] ./ROADMAP.md              --> [NEW] Trading_Bot/ROADMAP.md
```

### 2.2 BIBLE -> Trading_Bot_Documentation/

```
[OLD] ./docs/V5_BIBLE/          --> [NEW] Trading_Bot_Documentation/V5_BIBLE/
```

### 2.3 LIBRARY -> Important_Doc_Trading_Bot/

```
[OLD] ./PLAN/                   --> [NEW] Important_Doc_Trading_Bot/01_Plans/
[OLD] ./_devin_reports/         --> [NEW] Important_Doc_Trading_Bot/02_Reports/
[OLD] ./archive/documentation/  --> [NEW] Important_Doc_Trading_Bot/03_Legacy_Docs/
[OLD] ./DEEPSEEK_*.md           --> [NEW] Important_Doc_Trading_Bot/04_Audit_Records/
[OLD] ./PINE_BOT_*.md           --> [NEW] Important_Doc_Trading_Bot/04_Audit_Records/
[OLD] ./PROJECT_*.md            --> [NEW] Important_Doc_Trading_Bot/04_Audit_Records/
[OLD] ./docs/api/               --> [NEW] Important_Doc_Trading_Bot/05_Unsorted/api/
[OLD] ./docs/debug_reports/     --> [NEW] Important_Doc_Trading_Bot/02_Reports/debug_reports/
[OLD] ./docs/developer_notes/   --> [NEW] Important_Doc_Trading_Bot/05_Unsorted/developer_notes/
[OLD] ./docs/guides/            --> [NEW] Important_Doc_Trading_Bot/05_Unsorted/guides/
[OLD] ./docs/implementation/    --> [NEW] Important_Doc_Trading_Bot/05_Unsorted/implementation/
[OLD] ./docs/important/         --> [NEW] Important_Doc_Trading_Bot/05_Unsorted/important/
[OLD] ./docs/plans/             --> [NEW] Important_Doc_Trading_Bot/01_Plans/docs_plans/
[OLD] ./docs/reports/           --> [NEW] Important_Doc_Trading_Bot/02_Reports/docs_reports/
[OLD] ./docs/testing/           --> [NEW] Important_Doc_Trading_Bot/05_Unsorted/testing/
[OLD] ./docs/tradingview/       --> [NEW] Important_Doc_Trading_Bot/05_Unsorted/tradingview/
[OLD] ./docs/verification-reports/ --> [NEW] Important_Doc_Trading_Bot/02_Reports/
[OLD] ./docs/V3_FINAL_REPORTS/  --> [NEW] Important_Doc_Trading_Bot/02_Reports/
```

### 2.4 WEB -> Web_Application/

```
[OLD] ./updates/.../WEBDASHBOARD.../PROTOTYPE_DASHBOARD.html --> [NEW] Web_Application/
[OLD] ./updates/.../WEBDASHBOARD.../README.md --> [NEW] Web_Application/
```

### 2.5 WEB DOCS -> Important_Doc_Webapp/

```
[OLD] ./updates/.../WEBDASHBOARD.../01_PLANNING/  --> [NEW] Important_Doc_Webapp/
[OLD] ./updates/.../WEBDASHBOARD.../01_RESEARCH/  --> [NEW] Important_Doc_Webapp/
[OLD] ./updates/.../WEBDASHBOARD.../02_PLANNING/  --> [NEW] Important_Doc_Webapp/
[OLD] ./updates/.../WEBDASHBOARD.../03_COLOR_DESIGN/ --> [NEW] Important_Doc_Webapp/
[OLD] ./updates/.../WEBDASHBOARD.../04_DETAILED_COMPONENT_SPECS/ --> [NEW] Important_Doc_Webapp/
```

### 2.6 HISTORY -> Updates/

```
[OLD] ./updates/                --> [NEW] Updates/
```

---

## 3. DELETE LIST (JUNK)

```
[DELETE] ./bot_debug.log
[DELETE] ./.pytest_cache/
[DELETE] ./archive/temp_scripts/
[DELETE] ./docs/log 08-12-25/
[DELETE] ./archive/log */
[DELETE] ./archive/debug_files/
[DELETE] All __pycache__/
```

---

## 4. FINAL TREE STRUCTURE

```
ZepixTradingBot-old-v2-main/
|
+-- Trading_Bot/                    # 1. THE CODE
|   +-- src/
|   +-- config/
|   +-- data/
|   +-- logs/
|   +-- scripts/
|   +-- tests/
|   +-- assets/
|   +-- .env.example
|   +-- pyproject.toml
|   +-- requirements.txt
|   +-- README.md
|   +-- ROADMAP.md
|   +-- START_BOT.bat
|
+-- Trading_Bot_Documentation/      # 2. THE GUIDE
|   +-- V5_BIBLE/
|       +-- 00_INDEX.md
|       +-- 03_TELEGRAM/
|       +-- ... (40+ files)
|
+-- Important_Doc_Trading_Bot/      # 3. THE LIBRARY
|   +-- 01_Plans/
|   +-- 02_Reports/
|   +-- 03_Legacy_Docs/
|   +-- 04_Audit_Records/
|   +-- 05_Unsorted/
|   +-- 06_Old_Archive/
|
+-- Web_Application/                # 4. THE UI
|   +-- PROTOTYPE_DASHBOARD.html
|   +-- README.md
|
+-- Web_Application_Documentation/  # 5. FUTURE WEB DOCS
|   +-- README.md
|
+-- Important_Doc_Webapp/           # 6. WEB PLANS
|   +-- 01_PLANNING/
|   +-- 01_RESEARCH/
|   +-- 02_PLANNING/
|   +-- 03_COLOR_DESIGN/
|   +-- 04_DETAILED_COMPONENT_SPECS/
|
+-- Updates/                        # 7. HISTORY
    +-- v5_hybrid_plugin_architecture/
```

---

## 5. CONSTRAINTS VERIFIED

| Constraint | Status |
|------------|--------|
| Only 7 folders at root | VERIFIED |
| Underscores instead of spaces | VERIFIED |
| No source folder renaming | VERIFIED |
| Git history preserved | VERIFIED |
| Junk removed | VERIFIED |

---

## 6. LOST FILES CHECK

**RESULT: NO LOST FILES** - Every file mapped to destination.

---

**STATUS: AWAITING GO SIGNAL**

**DO NOT EXECUTE UNTIL USER APPROVES**
