# DB-07: DAILY STATS TABLE SPECIFICATION
**Component ID:** DB-07  
**Layer:** Database Schema (Analytics)  
**Table Name:** `daily_stats`

---

## 1. 📝 Overview
Pre-aggregated data table for fast charting. Updated by a daily cron job or trigger.

## 2. 🏛️ Schema Definition

```sql
CREATE TABLE daily_stats (
    date DATE PRIMARY KEY,
    
    total_trades INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    
    daily_pnl DECIMAL(20, 8) DEFAULT 0,
    cumulative_pnl DECIMAL(20, 8) DEFAULT 0,
    
    max_drawdown_pct DECIMAL(10, 4) DEFAULT 0,
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 3. 🚀 Performance Benefit
- **Without this:** Dashboard Equity Chart queries `trades` table (Thousands of rows) -> Slow.
- **With this:** Dashboard queries `daily_stats` (30 rows for a month) -> Instant.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

