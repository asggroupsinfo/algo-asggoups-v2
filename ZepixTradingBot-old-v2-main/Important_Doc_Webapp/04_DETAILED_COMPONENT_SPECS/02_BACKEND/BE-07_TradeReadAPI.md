# BE-07: TRADE DATA READ API
**Component ID:** BE-07  
**Layer:** API Endpoint  
**Path:** `/api/trades`  
**Auth:** Authenticated

---

## 1. 📝 Overview
Advanced data retrieval endpoint for trade history with filtering, sorting, and pagination.

## 2. 🛣️ Endpoints

### 2.1 List Trades
**GET** `/api/trades`
- **Query Params:**
  - `page`: 1 (default)
  - `limit`: 20 (default)
  - `symbol`: "BTC/USDT" (optional)
  - `status`: "OPEN", "CLOSED", "ERROR"
  - `strategy`: "v3_combined", "v6_scalp"
  - `date_from`: ISO Date
  - `date_to`: ISO Date
  - `sort_by`: "entry_time", "pnl"
  - `order`: "asc", "desc"

- **Response (200 OK):**
  ```json
  {
    "data": [
      {
        "id": 105,
        "symbol": "BTC/USDT",
        "side": "LONG",
        "status": "OPEN",
        "entry_price": 42100.50,
        "current_price": 42150.00,
        "pnl_unrealized": 12.50,
        "entry_time": "2026-01-13T10:00:00Z",
        "strategy": "v3_combined"
      }
    ],
    "meta": {
      "total": 150,
      "page": 1,
      "limit": 20,
      "total_pages": 8
    }
  }
  ```

### 2.2 Get Trade Details
**GET** `/api/trades/{trade_id}`
- **Response:** Full details including order logs, raw signals, and error history for that specific trade.

## 3. 🧪 Performance Logic
- Uses **Keyset Pagination** (Cursor-based) for high performance if `limit > 1000`.
- Uses `SQLAlchemy` async select with dynamic `.where()` clauses based on filters.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

