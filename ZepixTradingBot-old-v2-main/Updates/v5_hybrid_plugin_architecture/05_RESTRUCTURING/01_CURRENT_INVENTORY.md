# CURRENT PROJECT INVENTORY (SCANNED)

**Date:** 2026-01-16
**Status:** UPDATED
**Scanner:** Devin (Agent)

---

## 1. ROOT DIRECTORY (`ZepixTradingBot-old-v2-main`)

| Type | Name | Description | Status |
|------|------|-------------|--------|
| 📁 | `src` | **CORE CODE**. Contains `core`, `plugins`, `telegram`. | **KEEP -> Move to Trading_Bot** |
| 📁 | `config` | **CONFIG**. Contains `config.json`. | **KEEP -> Move to Trading_Bot** |
| 📁 | `docs` | **DOCS MESS**. Contains 300+ files. | **SORT -> Move to Important_Doc_Trading_Bot** |
| 📁 | `updates` | **HISTORY**. Contains V5 updates. | **KEEP -> Move to Updates** |
| 📁 | `PLAN` | **LEGACY**. Old plans. | **ARCHIVE -> Move to Important_Doc_Trading_Bot** |
| 📁 | `_devin_reports` | **REPORTS**. AI logs. | **ARCHIVE -> Move to Important_Doc_Trading_Bot** |
| 📁 | `scripts` | **TOOLS**. Start/Run scripts. | **KEEP -> Move to Trading_Bot** |
| 📁 | `tests` | **TESTS**. Pytest files. | **KEEP -> Move to Trading_Bot** |
| 📁 | `archive` | **OLD**. Previous archive. | **ARCHIVE -> Move to Important_Doc_Trading_Bot** |
| 📁 | `data` | **DB**. Databases. | **KEEP -> Move to Trading_Bot** |
| 📁 | `logs` | **LOGS**. Log files. | **KEEP -> Move to Trading_Bot** |
| 📁 | `assets` | **ASSETS**. Static files. | **KEEP -> Move to Trading_Bot** |
| 📄 | `START_BOT.bat` | Entry Script. | **KEEP -> Move to Trading_Bot** |
| 📄 | `README.md` | Readme. | **KEEP -> Move to Trading_Bot** |
| 📄 | `requirements.txt`| Dependencies. | **KEEP -> Move to Trading_Bot** |

---

## 2. DETAIL: `src/` (The Brain)
*   `core/`
*   `logic_plugins/`
*   `telegram/`
*   `clients/`
*   `api/`
*   `managers/`
*   `models.py` / `v3_alert_models.py` (Need consolidation)

## 3. DETAIL: `updates/` (The History)
*   `v5_hybrid_plugin_architecture/` (Active)
    *   `WEBDASHBOARD_ALGO_ASGROUPS` (Web Plans) -> **Move to Important_Doc_Webapp**

## 4. JUNK (TO DELETE)
*   `bot_debug.log`
*   `archive/temp_scripts`
*   `docs/log *-12-25/`
*   System caches

---

**VERDICT:**
The structure is currently flat and messy. The 7-folder plan will organize this perfectly.
