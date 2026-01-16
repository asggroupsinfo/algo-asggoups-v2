# 00_ISOLATED_ARCHITECTURE_STRUCTURE.md
**Project:** algo.asgroups Web Dashboard
**Constraint:** STRICT ISOLATION FROM BOT CORE
**Root Folder:** `/webapplication`

---

## 🏗️ DIRECTORY STRUCTURE MANDATE

All new development MUST occur **exclusively** within the `webapplication` folder. No files should be added to the main bot `src/` directory unless strictly necessary for API hooks.

```
ZepixTradingBot-New-v1/
├── src/                          # 🛑 EXISTING BOT CORE (Do NOT Touch logic here)
│   ├── clients/
│   ├── core/
│   └── strategies/
│
├── webapplication/               # 🟢 NEW ISOLATED ENVIRONMENT
│   │
│   ├── backend/                  # 🐍 Python FastAPI Service
│   │   ├── app/
│   │   ├── venv/                 # Dedicated Virtual Env
│   │   ├── requirements.txt      # Separate dependencies
│   │   └── main.py
│   │
│   ├── frontend/                 # ⚛️ Next.js + React Application
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── database/                 # 🗄️ Database Schemas & Migrations
│   │   ├── migrations/
│   │   ├── schema/
│   │   └── init_db.py
│   │
│   └── scripts/                  # 🛠️ Deployment & Startup Scripts
│       ├── start_web.sh
│       └── setup_env.sh
│
├── config/                       # ⚙️ Shared Config (Read-Only for Web)
└── logs/                         # 📄 Shared Logs (Read-Only for Web)
```

---

## 🔗 CONNECTION PROTOCOL (Loose Coupling)

The Web Application connects to the Bot **ONLY** through these interfaces:

### 1. Database (Shared State)
*   **Bot:** Writes trades, status, logs to PostgreSQL/SQLite.
*   **Web Backend:** Reads from Database to show dashboard. Writes specific `command_queue` entries for the bot.

### 2. Configuration File (JSON)
*   **Bot:** Reads `config.json` on startup/reload.
*   **Web Backend:** Reads `config.json` to display settings. Writes updates to `config.json` (triggering bot reload).

### 3. Internal API / Localhost (Control)
*   **Status Check:** Web Backend queries Bot's internal status port (if available).
*   **Process Control:** Web Backend manages the Bot process (Start/Stop/Restart) via OS-level commands (e.g., systemd or subprocess), keeping the code separate.

---

## 🚫 RESTRICTIONS
1.  **NO Shared Source Code:** Web Backend must NOT import modules directly from `src/core`. Copy necessary utility definitions or use shared libraries if absolutely needed.
2.  **Separate Dependencies:** `webapplication/backend` has its own `requirements.txt`. Do not mix with Bot's `requirements.txt`.
3.  **UI Isolation:** Frontend files must NEVER exist outside `webapplication/frontend`.

---

## ⚠️ IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full `ZepixTradingBot` codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.
