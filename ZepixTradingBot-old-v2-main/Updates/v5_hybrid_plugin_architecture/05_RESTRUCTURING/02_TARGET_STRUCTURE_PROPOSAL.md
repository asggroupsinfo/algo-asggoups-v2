# TARGET STRUCTURE PROPOSAL (USER DEFINED)

**Date:** 2026-01-16
**Status:** UPDATED BY USER REQUEST
**Purpose:** Create a Human-Readable, Developer-Friendly 7-Folder Structure.

---

## 1. DESIGN PHILOSOPHY
The user wants a structure where **Folder Names describe contents clearly**. Only 7 main folders.
- **Spaces to Underscores:** We will use underscores (`Trading_Bot`) instead of spaces (`Trading Bot`) to ensure Python Code runs without errors.
- **Junk Removal:** All junk identified by Devin will be deleted.

---

## 2. THE 7-FOLDER STRUCTURE (ROOT)

We will transform `ZepixTradingBot-old-v2-main` into this clean layout:

### 📁 1. Trading_Bot (THE CODE)
*Contains ONLY the executable bot. No clutter.*
```
Trading_Bot/
├── src/                  # The Brain (Core, Plugins, Telegram)
├── config/               # config.json
├── data/                 # Databases
├── logs/                 # Active logs
├── scripts/              # run.bat, tools
├── tests/                # Verification tests
├── .env                  # Secrets
└── main.py               # Entry point
```

### 📁 2. Trading_Bot_Documentation (THE GUIDE)
*Contains ONLY the Best, Verified Documentation (V5 Bible).*
```
Trading_Bot_Documentation/
└── V5_BIBLE/             # The "True" documentation
    ├── MANUALS/
    └── GUIDES/
```

### 📁 3. Important_Doc_Trading_Bot (THE LIBRARY)
*Contains ALL other documents, sorted and organized (No mess).*
```
Important_Doc_Trading_Bot/
├── 01_Plans/             # From 'PLAN/'
├── 02_Reports/           # From '_devin_reports/'
├── 03_Legacy_Docs/       # From 'DOCUMENTATION/'
├── 04_Audit_Records/     # Root audit files
└── 05_Unsorted/          # Any other helpful text files
```
*Action:* We will read every widely scattered file in `docs/` and sort them into these subfolders.

### 📁 4. Web_Application (THE UI)
*Contains the Dashboard Code.*
```
Web_Application/
└── (Content moved from 'webapplication/')
```

### 📁 5. Web_Application_Documentation
*Placeholder for Future Web Docs.*
```
Web_Application_Documentation/
└── README.md (Future use)
```

### 📁 6. Important_Doc_Webapp
*Contains specific Web Plans.*
```
Important_Doc_Webapp/
└── (Content moved from 'updates/v5.../WEBDASHBOARD_ALGO_ASGROUPS')
```

### 📁 7. Updates (HISTORY)
*Contains the update history.*
```
Updates/
└── (Existing 'updates/' folder content)
```

---

## 3. CLEANUP (DELETE LIST)
These files will be **PERMANENTLY DELETED** (Junk):
1.  ❌ `bot_debug.log`
2.  ❌ `archive/temp_scripts/`
3.  ❌ `docs/log *-12-25/` (Old December Logs)
4.  ❌ `__pycache__/` and `.pytest_cache/`
5.  ❌ `archive/` (The old junk folder - unless it has important data, we will move it to 'Important_Doc_Trading_Bot/06_Old_Archive' to be safe)

---

## 4. EXECUTION PLAN

### Phase 1: Safety First
1.  Verify `git` status.
2.  Create the 7 Top-Level Folders.

### Phase 2: The Great Move
1.  Move **Code** `src`, `config`, etc. -> `Trading_Bot/`
    *   *Critical:* Update imports if necessary (though relative imports inside `src` are safe).
2.  Move **Bible** -> `Trading_Bot_Documentation/`
3.  Move **Web** -> `Web_Application/`
4.  Move **Web Docs** -> `Important_Doc_Webapp/`

### Phase 3: The Great Sort (Sorting the Mess)
1.  Scan `docs/` (300+ files).
2.  Sort them into `Important_Doc_Trading_Bot/` subfolders based on filename/content.
    *   Plan-related -> `01_Plans`
    *   Report-related -> `02_Reports`
3.  Move `PLAN/`, `DOCUMENTATION/` -> `Important_Doc_Trading_Bot/`.

### Phase 4: Final Verification
1.  Test Bot from new `Trading_Bot/` folder.
2.  Verify Web App files.
3.  Confirm Root is clean (Only 7 folders visible).

---

## 5. USER APPROVAL
**Current Status:** FLAGGED FOR USER APPROVAL.
**Next Step:** Execute this restructuring upon 'YES'.
