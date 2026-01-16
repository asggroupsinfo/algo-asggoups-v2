# BE-08: TRADE MANAGEMENT API (WRITE)
**Component ID:** BE-08  
**Layer:** API Endpoint  
**Path:** `/api/trades`  
**Auth:** Editor/Admin

---

## 1. 📝 Overview
Endpoints to manually intervene in trading operations (Close, Force Exit, Edit).

## 2. 🛣️ Endpoints

### 2.1 Close Position
**POST** `/api/trades/{trade_id}/close`
- **Purpose:** Manually trigger a market sell/buy to close a specific position.
- **Body:** `{"reason": "Manual Close via Dashboard"}`
- **Logic:**
  1. Retrieve trade info.
  2. Send Market Order to Exchange.
  3. Update DB status to `CLOSED`.
  4. Broadcast `TRADE_UPDATE` event.

### 2.2 Force Exit (Emergency)
**POST** `/api/trades/{trade_id}/force-exit`
- **Purpose:** Mark a trade as closed in DB *without* sending exchange orders (Ghost kill).
- **Use Case:** Position already closed on exchange but stuck in DB.

### 2.3 Edit Parameters
**PUT** `/api/trades/{trade_id}`
- **Body:** `{"take_profit": 45000, "stop_loss": 41000}`
- **Logic:**
  1. Update DB values.
  2. If order is live on exchange (Limit Order), cancel and replace.

## 3. 🛡️ Safety Checks
- Cannot close an already `CLOSED` trade.
- Check user permissions (Viewer cannot execute).
- Verify exchange connection before attempting close.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

