# WF-02: BOT START SEQUENCE
**Component ID:** WF-02  
**Type:** Sequence Diagram  
**Actors:** Admin, API, Database, Bot Process

---

## 1. 📝 Description
Logic for safely starting the trading engine, ensuring no duplicates run.

## 2. 🌊 Sequence

```mermaid
sequenceDiagram
    participant Admin
    participant API
    participant DB
    participant BotProcess

    Admin->>API: Click "Start Bot"
    
    API->>DB: SELECT is_running FROM bot_state WHERE id=1 FOR UPDATE
    
    alt Is Already Running?
        DB-->>API: True
        API-->>Admin: Error: "Bot already running"
    else Is Stopped
        DB-->>API: False
        
        API->>DB: UPDATE bot_state SET is_running=TRUE, status='STARTING'
        API->>BotProcess: Spawn Subprocess (python main.py)
        
        BotProcess->>BotProcess: Initialize Strategies
        BotProcess->>DB: UPDATE bot_state SET status='RUNNING'
        
        BotProcess->>API: WebSocket Broadcast "SYSTEM_STARTED"
        API-->>Admin: Success Toast "Bot Started"
    end
```

## 3. 🔍 Safety
- **Row Lock:** `FOR UPDATE` prevents race condition if two admins click start simultaneously.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

