# 🚀 LIVE SYSTEM ACTIVATION MANDATE

**Mandate ID:** 15_LIVE_SYSTEM_ACTIVATION_MANDATE
**Date:** 2026-01-17
**Priority:** 🟢 **HIGH - EXECUTION PHASE**
**Status:** **PENDING START**

---

## 🎯 OBJECTIVE: TURN THE KEY (MAKE IT WORK)
The Codebase is 100% Compliant with Documentation. Now we must **ACTIVATE** the system.
We need to prove the bot actually RUNS, connects to Telegram, and executes Trades.

## 🛠️ TASKS FOR DEVIN

### PHASE 1: STARTUP INTEGRITY CHECK
**.** Run the bot locally and verify clean startup.
- **Command:** `python main.py`
- **Success Criteria:**
  - No Python Crashes/Tracebacks.
  - Logs show: `✅ Zepix Trading Bot V5 Started`.
  - Logs show: `🔌 V3 Plugin Loaded`.
  - Logs show: `📡 Telegram Bot Connected`.

### PHASE 2: TELEGRAM INTERFACE VERIFICATION
**.** Interact with the running bot via Telegram (Mock or Real).
- **Test:** Send `/start` command.
- **Verify:** Bot replies with the **Main Menu** (Dashboard, Settings, Reports).
- **Test:** Click **"Status"** button.
- **Verify:** Bot replies with System Status (CPU, RAM, Active Session).

### PHASE 3: SHADOW MODE TRADE TEST (The "Hello World")
**.** Inject a fake V3 Alert and verify proper routing.
- **Action:** Create a simplified script `tests/live_activation/inject_test_signal.py`.
- **Payload:**
  ```json
  {
    "symbol": "EURUSD",
    "signal": "BULLISH",
    "score": 10,
    "mtf_trends": "1,1,1,1,1,1",
    "logic": "combinedlogic-1"
  }
  ```
- **Verify:**
  1. Signal received by `WebhookHandler`.
  2. Routed to `V3Plugin`.
  3. `SessionManager` creates a session.
  4. `TradingEngine` places a **SHADOW ORDER** (Paper Trade).
  5. Telegram sends: "🚨 **ENTRY ALERT**" notification.

---

## 📝 DELIVERABLES
1. **Startup Log:** Copy of the terminal output showing clean start.
2. **Screenshot/Log:** Evidence of Telegram interaction.
3. **Trade Log:** Evidence of the Test Signal turning into a Trade.

---

**⚠️ RULE:** DO NOT CHANGE CODE STRUCTURE. Only fix runtime bugs if found.
**GOAL:** Prove it works end-to-end.
