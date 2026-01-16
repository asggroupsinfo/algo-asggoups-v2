# DB-02: BOT STATE TABLE SPECIFICATION
**Component ID:** DB-02  
**Layer:** Database Schema  
**Table Name:** `bot_state`

---

## 1. 📝 Overview
A "Singleton" table that stores the global runtime state of the trading engine. Used for synchronization between Web and Telegram.

## 2. 🏛️ Schema Definition

```sql
CREATE TABLE bot_state (
    id INTEGER PRIMARY KEY CHECK (id = 1), -- Enforce singleton row
    is_running BOOLEAN NOT NULL DEFAULT FALSE,
    current_status VARCHAR(50) DEFAULT 'STOPPED', -- 'RUNNING', 'STOPPED', 'ERROR', 'STARTING'
    active_config_version VARCHAR(50),
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    last_command_source VARCHAR(20), -- 'WEB', 'TELEGRAM', 'SYSTEM'
    error_message TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 3. 🧠 Coexistence Logic
- **Locking:** The backend checks `is_running` before issuing a start command.
- **Heartbeat:** The Python bot process updates `last_heartbeat` every 5 seconds. If `last_heartbeat` is > 1 min old, the Dashboard assumes the process crashed.

## 4. 🔄 Initial Data
```sql
INSERT INTO bot_state (id, is_running, current_status) VALUES (1, FALSE, 'STOPPED');
```


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

