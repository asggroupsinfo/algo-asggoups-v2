# BE-04: BOT CONTROL API SPECIFICATION
**Component ID:** BE-04  
**Layer:** API Endpoint  
**Path:** `/api/bot`
**Auth:** Editor/Admin

---

## 1. 📝 Overview
Direct interface to control the Python trading subprocess/service.

## 2. 🛣️ Endpoints

### 2.1 Get Bot Status
**GET** `/api/bot/status`
- **Response (200 OK):**
  ```json
  {
    "status": "running", // running, stopped, error, starting
    "pid": 1234,
    "uptime_seconds": 3600,
    "active_config": "v5_hybrid_v1",
    "cpu_usage": 1.2, // percent
    "memory_usage": 45 // MB
  }
  ```

### 2.2 Start Bot
**POST** `/api/bot/start`
- **Logic:**
  1. Check if already running.
  2. Load latest configuration from DB.
  3. Spawn process `python main.py`.
  4. Update `bot_state` table to `is_running=true`.
  5. Broadcast "STARTED" event via WebSocket.

### 2.3 Stop Bot
**POST** `/api/bot/stop`
- **Body:** `{"force": false}`
- **Logic:**
  1. Send `SIGTERM` signal to process.
  2. Wait for graceful shutdown (save state, close DB connections).
  3. If `force=true` (Emergency), send `SIGKILL`.
  4. Update `bot_state` table.

## 3. 🧠 Coexistence Logic (Telegram Sync)
- When **Start** is called via API:
  - Check `bot_lock` in DB.
  - If locked by Telegram command, return `409 Conflict`.
- When **Stop** is called:
  - Notify Telegram users: "⚠️ Bot stopped by Admin via Dashboard".


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

