# DB-04: TRADES TABLE SPECIFICATION
**Component ID:** DB-04  
**Layer:** Database Schema  
**Table Name:** `trades`

---

## 1. 📝 Overview
The core ledger of all trading activity. Records every position opened by the bot.

## 2. 🏛️ Schema Definition

```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    
    -- Trade Identity
    exchange_order_id VARCHAR(100),
    symbol VARCHAR(20) NOT NULL, -- 'BTC/USDT'
    side VARCHAR(10) NOT NULL,   -- 'LONG', 'SHORT'
    strategy VARCHAR(50) NOT NULL, -- 'v3_combined', 'v6_1m'
    
    -- Status
    status VARCHAR(20) NOT NULL, -- 'OPEN', 'CLOSED', 'CANCELED', 'ERROR'
    
    -- Entry Details
    entry_price DECIMAL(20, 8),
    entry_quantity DECIMAL(20, 8),
    entry_time TIMESTAMP WITH TIME ZONE,
    
    -- Exit Details
    exit_price DECIMAL(20, 8),
    exit_time TIMESTAMP WITH TIME ZONE,
    exit_reason VARCHAR(50), -- 'TP_HIT', 'SL_HIT', 'MANUAL', 'SIGNAL'
    
    -- Performance
    pnl_realized DECIMAL(20, 8),
    pnl_percentage DECIMAL(10, 4),
    fees DECIMAL(20, 8),
    
    -- Metadata
    raw_data JSONB -- Stores extra exchange info
);
```

## 3. 🔑 Indexes
- `idx_trades_status`: For filtering `OPEN` trades.
- `idx_trades_time`: For P&L charts (Range queries).
- `idx_trades_strategy`: For strategy performance analysis.

## 4. 🧮 Calculations
- **P&L:** Calculated as `(Exit Price - Entry Price) * Quantity` (Adjusted for Short).
- **Duration:** Calculated efficiently in app logic or view (`exit_time - entry_time`).


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

