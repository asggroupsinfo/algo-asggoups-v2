# DB-06: ORDERS TABLE SPECIFICATION
**Component ID:** DB-06  
**Layer:** Database Schema  
**Table Name:** `orders`

---

## 1. 📝 Overview
Tracks individual exchange orders. One "Trade" (Position) may consist of multiple "Orders" (e.g., 1 Entry, 3 partial Take Profits).

## 2. 🏛️ Schema Definition

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER REFERENCES trades(id),
    exchange_order_id VARCHAR(100),
    
    order_type VARCHAR(20), -- 'MARKET', 'LIMIT', 'STOP_MARKET'
    side VARCHAR(10), -- 'BUY', 'SELL'
    
    quantity DECIMAL(20, 8),
    price DECIMAL(20, 8),
    stop_price DECIMAL(20, 8), -- For Stop orders
    
    status VARCHAR(20), -- 'NEW', 'FILLED', 'CANCELED', 'REJECTED'
    
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 3. 🔗 Relationship
- **Trades vs Orders:** `Trades` tracks the *Position* logic. `Orders` tracks the *Execution* mechanics.
- A single `trade_id` will link to:
  - 1 Entry Order
  - 1 or more Exit Orders (TP/SL)


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

