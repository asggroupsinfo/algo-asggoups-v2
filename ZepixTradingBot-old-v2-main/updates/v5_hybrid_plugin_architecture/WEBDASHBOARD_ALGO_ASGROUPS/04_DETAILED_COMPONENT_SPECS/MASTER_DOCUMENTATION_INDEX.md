# MASTER DOCUMENTATION INDEX - algo.asgroups

**Project:** algo.asgroups Web Dashboard  
**Design Reference:** abhibots.com/dashboard  
**Total Documents:** 45+ Detailed Specifications  
**Status:** Architecture Definition

---

## 📂 01_FRONTEND (UI/UX Components)
*Detailed React/Next.js Component Specifications with Tailwind Classes & Logic*

> **⚠️ MANDATORY DESIGN SOURCES:**
> 1. `WEBDASHBOARD_ALGO_ASGROUPS/03_COLOR_DESIGN/BRAND WEBSITE COLOR AND PROTOTYPE.HTML`
> 2. `WEBDASHBOARD_ALGO_ASGROUPS/03_COLOR_DESIGN/COLOR_PREVIEW AND PROTOTYPE.html`

### 1.0 Public & Auth Pages (Entry Points)
- `FE-00A_LandingPage.md`: Brand Website Spec (Navbar, Hero, Features)
- `FE-00B_LoginPage.md`: Glassmorphism Login Screen Spec (Auth Gate)

### 1.1 Layout System
- `FE-01_MainLayout.md`: Sidebar, Header, Content Area Grid (CSS Grid/Flexbox specs)
- `FE-02_Sidebar.md`: Navigation items, active states, collapse logic, icons
- `FE-03_Header.md`: Glassmorphism header, profile dropdown, notifications bell
- `FE-04_MobileNav.md`: Hamburger menu, off-canvas transitions for mobile

### 1.2 Dashboard Widgets (Home)
- `FE-05_StatsCard.md`: Small card with icon, value, trend indicator (green/red)
- `FE-06_LiveStatusFeed.md`: Real-time scrolling log component (WebSocket connected)
- `FE-07_MiniCharts.md`: Sparkline charts for quick P&L visualization
- `FE-08_ActiveBotCard.md`: Main status card showing bot health & active logic

### 1.3 Trading Interface (Controls)
- `FE-09_StrategySelector.md`: Grid-based toggle for V3/V6 logic selection
- `FE-10_ParameterSliders.md`: Risk management sliders (SL/TP %)
- `FE-11_ActionButtons.md`: Start/Stop/Emergency gradient buttons with loading states
- `FE-12_InputForms.md`: Configuration inputs with validation and error states

### 1.4 Data Visualization (Analytics)
- `FE-13_TradeHistoryTable.md`: Advanced data table with sorting, filtering, pagination
- `FE-14_PerformanceChart.md`: Large interactive area/line chart (Recharts/TradingView)
- `FE-15_WinRatePie.md`: Donut chart for win/loss ratio visualization
- `FE-16_DrawdownGraph.md`: Specialized chart for drawdown analysis

### 1.5 Advanced Features (AI & Shield)
- `FE-31_ShieldProtectionPage.md`: Reverse Shield v3.0 configuration & status
- `FE-32_AutonomousDashboard.md`: AI logic monitor (Fine-Tune & Recoveries)

### 1.6 System UI
- `FE-17_NotificationToast.md`: Toast system for alerts (Success, Error, Info)
- `FE-18_ModalDialogs.md`: Confirmation modals (Stop Bot, Delete Config)
- `FE-19_LoaderStates.md`: Skeleton screens and spinner animations
- `FE-20_ThemeConfig.md`: Tailwind configuration file reference (Colors, Fonts)

---

## 📂 02_BACKEND (API & Logic)
*FastAPI Endpoint Specifications, Request/Response Examples & Logic Flow*

### 2.1 Authentication & User
- `BE-01_AuthAPI.md`: Login, Refresh Token, Logout endpoints
- `BE-02_UserAPI.md`: Profile management, Password change endpoints
- `BE-03_MiddlewareSpecs.md`: JWT validation, Rate limiting, CORS logic

### 2.2 Bot Control Engine
- `BE-04_BotControlAPI.md`: Start/Stop/Restart logic & state persistence
- `BE-05_ConfigAPI.md`: Get/Update bot configuration (JSON validation)
- `BE-06_LogStreamAPI.md`: Real-time log streaming logic

### 2.3 Trading Data
- `BE-07_TradeReadAPI.md`: Fetching trade history with complex filters
- `BE-08_TradeWriteAPI.md`: Manual trade closure/modification endpoints
- `BE-09_AnalyticsEngine.md`: Calculation logic for P&L, Win Rate, Drawdown

### 2.4 Real-time System
- `BE-10_WebSocketHub.md`: Connection logic, event broadcasting types
- `BE-11_TelegramSync.md`: Logic for syncing state between Web & Telegram bots
- `BE-12_NotificationService.md`: Routing alerts to DB, WebSocket, and Telegram

### 2.5 System Management
- `BE-13_HealthCheckAPI.md`: System status monitoring endpoints
- `BE-14_BackupRestoreAPI.md`: Database backup trigger endpoints
- `BE-15_ErrorHandling.md`: Global exception handler specifications

---

## 📂 03_DATABASE (Schema & Data)
*PostgreSQL Schema Definitions, Relationships & Indexing Strategy*

### 3.1 Core Schema
- `DB-01_UsersTable.md`: User credentials, roles, preferences
- `DB-02_BotStateTable.md`: Singleton table for global bot status & locks
- `DB-03_ConfigurationTable.md`: Versioned configuration storage (JSONB)

### 3.2 Trading Data
- `DB-04_TradesTable.md`: Main trade record schema (Entries, Exits, P&L)
- `DB-05_SignalsTable.md`: Raw signals received from TradingView/Logic
- `DB-06_OrdersTable.md`: Exchange order execution details

### 3.3 Analytics & Logs
- `DB-07_DailyStatsTable.md`: Aggregated daily performance metrics
- `DB-08_SystemLogsTable.md`: Application event logs structure
- `DB-09_AuditLogTable.md`: User action tracking (who changed what)

### 3.4 Optimization
- `DB-10_IndexingStrategy.md`: Performance indexes for high-speed queries
- `DB-11_TimescaleConfig.md`: TimescaleDB hypertables setup (if used)

---

## 📂 04_WORKFLOWS (Process Flows)
*Sequence Diagrams & User Flow Documentation*

- `WF-01_LoginFlow.md`: Detailed login sequence (Frontend <-> Backend <-> DB)
- `WF-02_BotStartFlow.md`: Sequence for starting the bot safely
- `WF-03_LiveAlertFlow.md`: Path of a signal from TradingView to Dashboard
- `WF-04_ConfigUpdateFlow.md`: Process for updating settings without restart
- `WF-05_EmergencyStopFlow.md`: Critical path for emergency shutdown

---

**Total Planned Documents:** 55 Files  
**Next Step:** Begin generating spec files batch by batch (starting with Frontend).


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

