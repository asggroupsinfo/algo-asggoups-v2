# DB-10: INDEXING STRATEGY
**Component ID:** DB-10  
**Layer:** Database Optimization  
**Target:** PostgreSQL

---

## 1. 🚀 Performance Goals
- **Dashboard Load:** < 200ms.
- **Trade History Sorting:** Instant for < 100k rows.
- **Search:** fast lookup by Symbol.

## 2. 📋 Critical Indexes

| Table | Column(s) | Type | Purpose |
| :--- | :--- | :--- | :--- |
| `trades` | `(status, entry_time)` | B-Tree | Fast "Active Trades" query |
| `trades` | `symbol` | Hash | Precise Symbol lookup |
| `system_logs` | `timestamp` | B-Tree | "Live Feed" pagination |
| `signals` | `received_at` | B-Tree | Debugging timeout signals |
| `users` | `username` | Unique | Login lookup |

## 3. 📄 SQL Implementation

```sql
-- Trades
CREATE INDEX idx_trades_composite ON trades(status, entry_time DESC);
CREATE INDEX idx_trades_symbol ON trades USING HASH (symbol);

-- Logs
CREATE INDEX idx_logs_timestamp ON system_logs(timestamp DESC);

-- Signals
CREATE INDEX idx_signals_time ON signals(received_at DESC);
```

## 4. 🧹 Maintenance
- **Vacuum:** Auto-vacuum enabled.
- **Reindex:** Scheduled monthly during maintenance window.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

