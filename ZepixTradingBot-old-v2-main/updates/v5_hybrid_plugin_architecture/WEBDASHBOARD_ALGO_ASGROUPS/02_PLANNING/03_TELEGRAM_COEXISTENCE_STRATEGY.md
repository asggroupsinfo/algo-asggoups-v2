# TELEGRAM BOT COEXISTENCE STRATEGY - algo.asgroups

**Date:** 2026-01-13  
**Project:** algo.asgroups Web Dashboard  
**Status:** Planning Complete  
**Strategy:** Hybrid Operation (Web Dashboard + Telegram Bots)

---

## 🤝 COEXISTENCE OVERVIEW

### Core Philosophy
The Web Dashboard (`algo.asgroups`) and Telegram Bots will operate in **parallel**. The Dashboard becomes the **primary** control center for advanced management and analytics, while Telegram Bots serve as **secondary** interfaces for quick alerts and basic commands on the go.

### Unified State Management
Both interfaces will interact with the **Same Backend API** and **Same Database**.
- A command sent via Telegram updates the database.
- The Web Dashboard reflects this change instantly via WebSocket.
- A change on the Dashboard notifies the Telegram Bot to send an alert.

---

## 🔄 FUNCTIONAL SPLIT

| Feature | 🖥️ Web Dashboard (Primary) | 📱 Telegram Bots (Secondary) |
| :--- | :--- | :--- |
| **Status Monitoring** | Live visual feed, detailed logs | Instant alerts, `/status` summary |
| **Configuration** | Full visual editor, JSON validation | Limited `/config` commands |
| **Trading Logs** | Filterable, sortable, exportable history | Recent trades only (`/trades 5`) |
| **Analytics** | Interactive charts, Logic-wise performance | Daily P&L summary reports |
| **Emergency Control** | Stop/Start buttons, visual confirmation | Quick `/stop` or `/force_exit` |
| **Notifications** | Real-time browser notifications | Push notifications (High Priority) |

---

## 🛠️ TECHNICAL ARCHITECTURE FOR COEXISTENCE

### Shared Database Lock
To prevent conflicts (e.g., User stops bot on Web while Telegram tries to start it), we implement a **Database-level Lock** or **State Flag**.

1. **Bot State Table:**
   ```sql
   CREATE TABLE bot_state (
       id SERIAL PRIMARY KEY,
       is_running BOOLEAN DEFAULT FALSE,
       last_command_source VARCHAR(20), -- 'web' or 'telegram'
       updated_at TIMESTAMP DEFAULT NOW()
   );
   ```

2. **Conflict Resolution:**
   - **Scenario:** Web sends "STOP".
   - **Action:** Backend updates DB `is_running = False`.
   - **Result:** Bot process checks DB loop, stops trading.
   - **Notification:** Telegram Bot sends: "⚠️ Bot Stopped via Web Dashboard".

### Notification Synchronization
- **Event:** Trade Executed (Buy/Sell)
- **Action 1 (Web):** WebSocket pushes update → Dashboard Trade List updates instantly.
- **Action 2 (Telegram):** Notification Service sends msg → "🟢 BUY Order Executed on BTCUSDT".

---

## 📱 TELEGRAM BOT ROLES (REFINED)

Since the Web Dashboard handles heavy lifting, Telegram bots can be streamlined:

1.  **Control Bot (Admin):**
    *   **Keep:** `/start`, `/stop`, `/status`, `/balance`, `/emergency_exit`
    *   **Remove:** Complex config editing (direct user to Web Dashboard link).
    *   **New Feature:** "🌐 Open Dashboard" button (Login via token link).

2.  **Notification Bot:**
    *   **Focus:** Purely for alerts (Trade Open, Close, Error, P&L Daily).
    *   **Enhancement:** Links in alerts pointing to specific trade details on Dashboard.
        *   *Example:* "🟢 Bought BTC. [View on Dashboard](https://algo.asgroups/trades/123)"

3.  **Analytics Bot:**
    *   **Focus:** Periodic reports (4-hour, Daily, Weekly summaries).
    *   **Change:** Generate simple text summaries with a link to detailed charts on Web.

---

## 🔗 AUTHENTICATION BRIDGE (Future Feature)

**"Magic Link" Login:**
- User types `/login` in Telegram Control Bot.
- Bot generates a one-time secure link: `https://algo.asgroups/auth/magic?token=xyz...`
- User clicks link → Instantly logged into Web Dashboard without typing password.

---

## ⚠️ RISK MITIGATION

| Scenario | Handling |
| :--- | :--- |
| **Web Server Down** | Telegram Bot operates independently (Direct DB/Process access). |
| **Telegram API Down** | Web Dashboard operates independently. Full control remains. |
| **Simultaneous Commands** | Backend queues commands. First-come, first-served. Timestamped logs. |
| **Database Lock** | If DB fails, Bot defaults to "Safe Mode" (No new trades). |

---

## ✅ IMPLEMENTATION CHECKLIST

- [ ] Ensure Backend API supports "Source" field in commands (Web/Telegram).
- [ ] Update Telegram Bot code to check DB state before executing actions.
- [ ] Add "Open Dashboard" button to Telegram Bot menu.
- [ ] Configure Notification Service to broadcast to both WebSocket and Telegram API.
- [ ] Test race conditions (Spamming start/stop from both interfaces).

---

**Strategy Status:** ✅ **COMPLETE**  
**Approach:** Parallel Operation favoring Web for Control, Telegram for Alerts.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

