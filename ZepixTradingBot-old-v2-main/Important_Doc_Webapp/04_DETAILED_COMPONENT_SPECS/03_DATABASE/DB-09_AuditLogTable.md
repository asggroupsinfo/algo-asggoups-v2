# DB-09: AUDIT LOG TABLE SPECIFICATION
**Component ID:** DB-09  
**Layer:** Database Schema  
**Table Name:** `audit_logs`

---

## 1. 📝 Overview
Security requirement. Tracks "Who did what". Essential for team environments.

## 2. 🏛️ Schema Definition

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50), -- 'LOGIN', 'STOP_BOT', 'UPDATE_CONFIG'
    ip_address VARCHAR(45),
    details TEXT, -- e.g. "Changed SL from 2% to 3%"
    status VARCHAR(20) -- 'SUCCESS', 'FAILURE'
);
```

## 3. 🛡️ Usage
- **Admin Panel:** "Activity Log" view shows which user stopped the bot or changed API keys.
- **Security:** Detects unauthorized access attempts (Repeated LOGIN FAILURE).


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

