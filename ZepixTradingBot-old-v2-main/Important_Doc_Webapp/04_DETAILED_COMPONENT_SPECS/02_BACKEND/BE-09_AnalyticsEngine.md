# BE-09: ANALYTICS ENGINE SPECIFICATION
**Component ID:** BE-09  
**Layer:** Service / Logic  
**Path:** `/api/analytics`

---

## 1. 📝 Overview
Calculates performance metrics on-the-fly or via cached aggregation for the dashboard.

## 2. 🛣️ Endpoints

### 2.1 Dashboard Stats
**GET** `/api/analytics/stats`
- **Response:**
  ```json
  {
    "total_pnl": 1250.50,
    "active_trades": 3,
    "win_rate": 68.5, // percent
    "total_trades": 150,
    "best_pair": "BTC/USDT"
  }
  ```

### 2.2 Equity Curve
**GET** `/api/analytics/equity`
- **Query:** `range=30d` (7d, 30d, all)
- **Response:** Array of `{ "date": "2026-01-01", "balance": 10500 }`.

### 2.3 Drawdown Analysis
**GET** `/api/analytics/drawdown`
- **Response:** Max drawdown percentage and duration.

## 3. 🧠 Calculation Logic

### Win Rate Calculation
```python
wins = count(pnl > 0)
losses = count(pnl < 0)
total = wins + losses
win_rate = (wins / total) * 100
```

### Performance Optimization
- **Caching:** Expensive aggregations (e.g., All Time PnL) are cached in Redis/Memory for 5 minutes.
- **Daily Aggregation:** A background job summarizes trades into `daily_stats` table to avoid querying raw trade history every time.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

