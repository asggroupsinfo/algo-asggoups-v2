# BE-13: SYSTEM HEALTH CHECK API
**Component ID:** BE-13  
**Layer:** API Endpoint  
**Path:** `/api/health`

---

## 1. 📝 Overview
Endpoints used by Docker Healthcheck, Uptime Monitors, and the Dashboard footer to verify system sizing.

## 2. 🛣️ Endpoints

### 2.1 Public Health (Simple)
**GET** `/api/health`
- **Auth:** None (Public)
- **Response:** `{"status": "ok", "timestamp": "..."}`
- **Usage:** Load Balancers / Docker Healthcheck.

### 2.2 Deep Diagnostic (Admin)
**GET** `/api/health/diagnostic`
- **Auth:** Admin
- **Checks:**
  1. **DB:** Try `SELECT 1`.
  2. **Redis:** Ping (if used).
  3. **Exchange:** Test connectivity to Binance/Bybit API (Latency check).
  4. **Disk:** Check free space.
- **Response:**
  ```json
  {
    "database": "connected",
    "exchange_latency_ms": 120,
    "disk_free_gb": 45,
    "version": "1.0.0"
  }
  ```

## 3. 🛡️ Failure Strategy
- If DB is down, `/api/health` returns 503.
- Docker Auto-heal will restart the backend container if 503 persists for > 1 minute.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

