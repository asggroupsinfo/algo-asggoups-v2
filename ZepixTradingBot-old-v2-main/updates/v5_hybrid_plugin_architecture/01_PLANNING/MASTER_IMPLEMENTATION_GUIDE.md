> **IMPLEMENTATION REMINDER (READ THIS BEFORE IMPLEMENTING)**
>
> DO NOT IMPLEMENT THIS DOCUMENT AS-IS WITHOUT VALIDATION
>
> Before implementing anything from this document:
> 1. Cross-reference with actual bot code in `src/`
> 2. Check current bot documentation in `docs/`
> 3. Validate against current Telegram docs (just updated)
> 4. Use your reasoning: Does this make sense for the actual bot?
> 5. Identify gaps: What's missing that should be here?
> 6. Improve if needed: Add missing features, correct errors
> 7. Create YOUR implementation plan based on validated requirements
>
> This document is a GUIDE, not a COMMAND. Think critically.

---


# MASTER IMPLEMENTATION GUIDE: Zepix Web Dashboard (v5 Hybrid)
**Status:** 🚀 READY FOR EXECUTION  
**Version:** 1.0  
**Date:** 2026-01-13  
**Objective:** Step-by-step roadmap to build the Web Dashboard with 100% Telegram parity.

---

## 🏗️ PHASE 1: BACKEND FOUNDATION (Weeks 1-2)
*Goal: Functional API capable of reading bot state and updating config, FULLY ISOLATED in `/webapplication`.*

### 🟢 Step 1.0: Architecture Setup (Strict Isolation)
- [ ] **Create Directory Structure:**
  - Create folder: `/webapplication`
  - Create subfolders: `/webapplication/backend`, `/webapplication/frontend`, `/webapplication/database`
- [ ] **Review Rules:** Read `00_ISOLATED_ARCHITECTURE_STRUCTURE.md` to ensure zero code mixing.

### 🟢 Step 1.1: Database Schema & Environment
*Goal: Create the PostgreSQL tables required for the bot.*

- [ ] **Establish Database Connection:**
  - Install `asyncpg` and `sqlalchemy` in `webapplication/backend/venv`.
  - Configure connection string in `.env`.
- [ ] **Implement Core Schemas (Schema Definition):**
  - **Location:** `webapplication/database/models/`
  - [ ] **Users Table:** Implement `DB-01_UsersTable.md` (id, username, password_hash, role).
  - [ ] **Bot State Table:** Implement `DB-02_BotStateTable.md` (singleton status, locks).
  - [ ] **Configuration Table:** Implement `DB-03_ConfigurationTable.md` (versioned JSONB).
  - [ ] **Trading Tables:** Implement `DB-04`, `DB-05`, `DB-06` (Trades, Signals, Orders).
- [ ] **Run Migrations:**
  - Create `init_db.py` script to creating tables if they don't exist.
  - Verify tables in pgAdmin/dbeaver.

### 🟢 Step 1.2: Core API Endpoints
- [ ] **Authentication Module:**
  - Build `BE-01_AuthAPI.md` (Login, Token, Refresh)
  - Implement `BE-03_MiddlewareSpecs.md` (JWT Guard)
  - *Verify:* Test login via Postman.
- [ ] **Config Management:**
  - Build `BE-05_ConfigAPI.md` (GET/PUT config)
  - *Verify:* Can read/write `config.json` via API.
- [ ] **Bot Control:**
  - Build `BE-04_BotControlAPI.md` (Start/Stop/Panic)
  - Connect to `BotControlService` (Python).

### 🟢 Step 1.3: Real-Time Layer (WebSocket)
- [ ] **WebSocket Hub:**
  - Implement `BE-10_WebSocketHub.md` (Connection Manager)
  - Create broadcast channels: `logs`, `status`, `market_data`
- [ ] **Log Streaming:**
  - Implement `BE-06_LogStreamAPI.md`
  - Connect Python `logging` handler to WebSocket.

---

## 🎨 PHASE 2: FRONTEND SHELL & DESIGN (Week 3)
*Goal: A working visual shell that matches the HTML Prototypes perfectly.*

### 🔵 Step 2.1: Project Initialization
- [ ] **Initialize Next.js Project:**
  - `npx create-next-app@latest` (TypeScript, Tailwind, ESLint)
  - Install dependencies: `headlessui`, `framer-motion`, `recharts`, `lucide-react`.
- [ ] **Apply Design System (CRITICAL):**
  - **Copy CSS Variables** from `FE-20_ThemeConfig.md` & `BRAND WEBSITE...HTML`.
  - Configure `tailwind.config.ts` with brand colors (`bg-deep`, `profit`, `loss`).
  - create `components/ui/` folder with reusable glassmorphism primitives.

### 🔵 Step 2.2: Layout & Navigation
- [ ] **App Shell:**
  - Build `FE-01_MainLayout.md` (Grid structure).
  - Build `FE-02_Sidebar.md` (Navigation links, active states).
  - Build `FE-03_Header.md` (Profile, Notifications).
- [ ] **Auth Pages:**
  - Build Login Page (matches design prototype).
  - Integrate with `BE-01` Auth API.

---

## ⚙️ PHASE 3: SETTINGS MODULE IMPLEMENTATION (Weeks 4-5)
*Goal: 100% Feature Parity with Telegram Bot.*
*Order of implementation based on usage frequency.*

### 🟣 Step 3.1: Core Controls
- [ ] **Strategy Page (`FE-21`):** Logic Selector, Leverage, Mode.
- [ ] **Risk Manager (`FE-24`):** Tier selection, Daily Caps.
- [ ] **Session Manager (`FE-30`):** Trade hours setup in UI.

### 🟣 Step 3.2: Trading Logic Configuration
- [ ] **SL System (`FE-25`):** StopLoss, Trailing, Breakeven controls.
- [ ] **Profit Manager (`FE-26`):** TP Targets, Partial Close sliders.
- [ ] **Re-Entry System (`FE-22`):** Recovery mode, cooldowns.

### 🟣 Step 3.3: Advanced Controls
- [ ] **Trend Control (`FE-23`):** Manual Trend Matrix grid.
- [ ] **Order Limits (`FE-27`):** Max orders, Grid config.
- [ ] **Timeframes (`FE-28`):** Weight sliders.

### 🟣 Step 3.4: Intelligence Layer
- [ ] **Shield Page (`FE-31`):** Reverse shield v3.0 logic UI.
- [ ] **Autonomous Dash (`FE-32`):** AI monitoring logic UI.

---

## 📊 PHASE 4: DASHBOARD & ANALYTICS (Week 6)
*Goal: Visualization of bot performance.*

### 🟠 Step 4.1: Home Dashboard (`FE-01`)
- [ ] **Live Status Feed (`FE-06`):** Connect to WebSocket stream.
- [ ] **Stats Cards (`FE-05`):** P&L, Active Trades, Win Rate.
- [ ] **Mini Charts (`FE-07`):** Sparklines for daily performance.

### 🟠 Step 4.2: Data Visualization
- [ ] **Trade History (`FE-13`):** Data table with filters.
- [ ] **Performance Chart (`FE-14`):** Big interactive graph (Recharts).
- [ ] **Diagnostics (`FE-29`):** System health, Log viewer.

---

## 🧪 PHASE 5: VERIFICATION & LAUNCH (Week 7)
*Goal: Production readiness.*

### 🔴 Step 5.1: Integration Testing
- [ ] **Command verification:**
  - Test EVERY setting in Web UI -> Verify update in `config.json`.
  - Verify Telegram Bot reflects the changes immediately (Sync).
- [ ] **Panic Button Test:**
  - Click Panic in Web -> Ensure Bot triggers `close_all`.

### 🔴 Step 5.2: Final Design Polish
- [ ] **Design Audit:** Compare Web App screens against `COLOR_PREVIEW AND PROTOTYPE.html`.
- [ ] **Mobile Responsiveness Check:** Verify Sidebar collapse and table scrolling on mobile.

---

## 📝 EXECUTION CHECKLIST FOR DEVELOPER

**Start Here:**
1. Go to `PHASE 1: BACKEND FOUNDATION`.
2. Execute `Step 1.1`.
3. Mark done.
4. Move to `Step 1.2`.

*Use this document as your daily roadmap.*

---

## ⚠️ IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full `ZepixTradingBot` codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.
