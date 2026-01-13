# DB-08: SYSTEM LOGS TABLE SPECIFICATION
**Component ID:** DB-08  
**Layer:** Database Schema  
**Table Name:** `system_logs`

---

## 1. 📝 Overview
Stores application logs for the "Live Status Feed" widget and debugging.

## 2. 🏛️ Schema Definition

```sql
CREATE TABLE system_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(10), -- 'INFO', 'WARN', 'ERROR', 'TRADE'
    source VARCHAR(50), -- 'Strategy', 'Exchange', 'System'
    message TEXT,
    metadata JSONB -- Optional stack trace or context
);
```

## 3. 🧹 Maintenance Strategy
- **Partitioning:** Partition by month to easily drop old data.
- **Retention:** Keep only last 30 days in DB. Archive older logs to CSV/Text files.
- **Usage:** Dashboard fetches `ORDER BY timestamp DESC LIMIT 50`.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

