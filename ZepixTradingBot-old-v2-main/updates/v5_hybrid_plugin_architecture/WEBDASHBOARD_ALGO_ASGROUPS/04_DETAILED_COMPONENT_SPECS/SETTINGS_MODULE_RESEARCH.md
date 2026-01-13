# SETTINGS MODULE RESEARCH & MAPPING
**Source:** `TELEGRAM_COMMAND_STRUCTURE.md` (81 Commands)
**Target:** Web Dashboard Settings Module

---

## 1. 🗺️ High-Level Mapping
We will transform the linear Telegram Menu structure into a categorized Tab-based Web UI.

| Telegram Category | Web Settings Tab | Component ID |
| :--- | :--- | :--- |
| **Trading Control** | Dashboard Home (Quick Actions) | `FE-08`, `FE-11` |
| **Performance** | Analytics Page | `FE-14`, `BE-09` |
| **Strategy Control** | **Strategy Config** | `FE-21` |
| **Re-entry System** | **Re-entry Settings** | `FE-22` |
| **Trend Management** | **Trend Logic** | `FE-23` |
| **Risk & Lot** | **Risk Management** | `FE-24` |
| **SL System** | **Stop Loss Config** | `FE-25` |
| **Dual Orders** | **Dual Order Logic** | `FE-26` |
| **Profit Booking** | **Exit Strategy** | `FE-27` |
| **Diagnostics** | System Health (Footer/Admin) | `FE-06`, `BE-13` |

---

## 2. 🧩 Detailed Component Requirements

### ⚙️ FE-21: Strategy Config Page
**Goal:** Manage Logic 1, 2, 3 States.
- **UI:** Toggle Switches for LOGIC1, LOGIC2, LOGIC3.
- **Commands Mapped:**
  - `/logic_status` (Read State)
  - `/logic1_on`, `/logic1_off`
  - `/logic2_on`, `/logic2_off`
  - `/logic3_on`, `/logic3_off`

### 🔄 FE-22: Re-entry Settings Page
**Goal:** Configure aggressive recovery logic.
- **UI:** Form with Inputs & Selects.
- **Inputs:**
  - `Monitor Interval` (30s - 600s Slider)
  - `SL Offset` (1-5 Pips Slider)
  - `Cooldown` (Seconds Input)
  - `Recovery Time` (Minutes Input)
  - `Max Levels` (1-5 Input)
  - `SL Reduction` (0.3 - 0.7 Slider)
- **Toggles:** TP System, SL Hunt, Exit Continuation.
- **Actions:** "Reset Config" (Danger Button).

### 📈 FE-23: Trend Logic Page
**Goal:** Manual override of trend bias.
- **UI:** Data Grid / Matrix.
- **Rows:** Symbols (BTC, ETH, XAU).
- **Columns:** Timeframes (1m, 5m, 1h).
- **Cell:** Dropdown [AUTO, BULLISH, BEARISH].
- **Batch Actions:** "Set All Auto".

### 🛡️ FE-24: Risk Management Page
**Goal:** Capital safety logic.
- **UI:** Interactive Cards for Risk Tiers.
- **Active Tier:** Highlighted Card.
- **Edit Modal:** For Daily Cap, Lifetime Cap, Lot Size per tier.
- **Quick Switch:** "Activate Tier" button.
- **Actions:** "Clear Daily Loss", "Clear Lifetime Loss".

### 🛑 FE-25: Stop Loss Config Page
**Goal:** Fine-tune SL behavior.
- **UI:** Radio Group for System Selection (SL-1 vs SL-2).
- **Visual:** Chart showing "Conservative" vs "Aggressive" zones.
- **Status:** Active System Indicator.

### 💎 FE-26: Dual Orders & Profit Booking
**Goal:** Complex exit management.
- **UI:** Advanced Form.
- **Fields:**
  - `Secure Pips` (Input)
  - `Runner Pips` (Input)
  - `Break Even Offset` (Input)
- **Toggles:** Trailing Logic, Half-Close Logic.

---

## 3. 🕸️ API Requirements (Backend Expansion)
To support these new UIs, we need dedicated configuration endpoints (expanding `BE-05`).

- **GET /api/settings/reentry**
- **PUT /api/settings/reentry**
- **GET /api/settings/risk**
- **PUT /api/settings/risk**
- **POST /api/settings/risk/clear**
- **GET /api/settings/trend**
- **PUT /api/settings/trend**

## 4. 🎨 Design Principles (From HTML Prototype)
- **Forms:** Input fields with glass background (`bg-dark-800/50`).
- **Toggles:** Gradient track (`from-brand-primary to-brand-secondary`).
- **Cards:** Bordered glass cards (`border-glass-border`).
- **Typography:** `Inter` font, headers in gradient text.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

