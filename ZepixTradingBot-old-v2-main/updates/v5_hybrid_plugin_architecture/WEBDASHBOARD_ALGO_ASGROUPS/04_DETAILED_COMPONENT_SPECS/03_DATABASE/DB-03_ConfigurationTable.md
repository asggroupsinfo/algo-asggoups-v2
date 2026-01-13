# DB-03: CONFIGURATION TABLE SPECIFICATION
**Component ID:** DB-03  
**Layer:** Database Schema  
**Table Name:** `configurations`

---

## 1. 📝 Overview
Stores versioned JSON configurations for the trading engine. Allows rollback to previous settings.

## 2. 🏛️ Schema Definition

```sql
CREATE TABLE configurations (
    id SERIAL PRIMARY KEY,
    version_tag VARCHAR(50) NOT NULL, -- e.g., 'v1.0.0', 'stable-2026'
    config_json JSONB NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
```

## 3. 📝 JSON Structure (config_json)
The `config_json` column stores the entire bot settings:
```json
{
  "exchange": {
    "name": "binance",
    "api_key_enc": "...", 
    "secret_key_enc": "..."
  },
  "strategies": {
    "v3": { "enabled": true, "leverage": 5 },
    "v6": { "enabled": false }
  },
  "risk": {
    "daily_loss_limit": 50
  }
}
```

## 4. 🔑 Indexes
- `idx_config_active`: `is_active` (To quickly fetch current config).
- `idx_config_json`: GIN Index on `config_json` (For querying inside JSON).


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

