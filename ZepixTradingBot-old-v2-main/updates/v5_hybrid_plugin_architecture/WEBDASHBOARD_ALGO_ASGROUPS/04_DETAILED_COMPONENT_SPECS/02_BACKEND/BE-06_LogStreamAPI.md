# BE-06: LOG STREAM API SPECIFICATION
**Component ID:** BE-06  
**Layer:** API Endpoint / WebSocket
**Path:** `/api/logs`

---

## 1. 📝 Overview
Provides access to historical logs and real-time log streaming.

## 2. 🛣️ Endpoints

### 2.1 Get Historical Logs
**GET** `/api/logs`
- **Query Params:**
  - `limit`: 50 (default)
  - `level`: INFO, WARN, ERROR, TRADE
  - `source`: SYSTEM, STRATEGY, EXCHANGE
- **Response:**
  ```json
  {
    "logs": [
      { "id": 105, "ts": "...", "level": "TRADE", "msg": "Buy Signal BTC..." },
      { "id": 104, "ts": "...", "level": "INFO", "msg": "Syncing..." }
    ]
  }
  ```

### 2.2 Real-time Log Stream
handled via **WebSocket Hub (BE-10)** but logic resides within Logging Service.

- **Channel:** `logs`
- **Event:** `new_log`
- **Payload:** Log Object

## 3. 📄 Log Storage Strategy
- **Database:** Recent logs (last 7 days or 10,000 entries) kept in PostgreSQL for fast search.
- **File System:** All logs archived to daily files (`logs/2026-01-13.log`) for long-term storage.
- **Rotation:** Daily rotation, keep 30 days.

## 4. 🧹 Cleanup Job
A background task runs daily to:
1. Delete DB logs older than 7 days.
2. Compress old file logs (`.gz`).


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

