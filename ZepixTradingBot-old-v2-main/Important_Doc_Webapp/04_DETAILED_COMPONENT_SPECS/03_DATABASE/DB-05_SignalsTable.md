# DB-05: SIGNALS TABLE SPECIFICATION
**Component ID:** DB-05  
**Layer:** Database Schema  
**Table Name:** `signals`

---

## 1. 📝 Overview
Stores raw signals received from TradingView via Webhook before they become trades. Essential for debugging logic.

## 2. 🏛️ Schema Definition

```sql
CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50), -- 'TradingView', 'Internal_Logic'
    symbol VARCHAR(20),
    signal_type VARCHAR(20), -- 'BUY', 'SELL', 'CLOSE_ALL'
    price DECIMAL(20, 8),
    
    -- Payload
    raw_payload JSONB, -- Full webhook body
    
    -- Result
    processed BOOLEAN DEFAULT FALSE,
    trade_id INTEGER REFERENCES trades(id), -- Linked if trade executed
    processing_error TEXT
);
```

## 3. 🔍 Usage
- **Audit:** "Why did the bot buy BTC at 10:00?" -> Check `signals` table for incoming webhook.
- **Latency:** Compare `received_at` vs `trades.entry_time` to measure execution speed.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

