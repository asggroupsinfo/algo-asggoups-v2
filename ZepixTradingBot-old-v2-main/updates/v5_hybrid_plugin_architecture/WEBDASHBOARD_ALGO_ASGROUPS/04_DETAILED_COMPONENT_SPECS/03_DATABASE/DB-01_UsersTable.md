# DB-01: USERS TABLE SPECIFICATION
**Component ID:** DB-01  
**Layer:** Database Schema  
**Table Name:** `users`

---

## 1. 📝 Overview
Stores authentication credentials and profile information for dashboard access.

## 2. 🏛️ Schema Definition

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer', -- 'admin', 'editor', 'viewer'
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 3. 🔑 Indexes
- `idx_users_username` (Unique)
- `idx_users_role` (For filering user lists)

## 4. 🔗 Relationships
- **One-to-Many:** `users.id` -> `audit_logs.user_id` (Tracks who did what)
- **One-to-Many:** `users.id` -> `user_sessions.user_id` (Active sessions)

## 5. 🛡️ Data Guidelines
- **Password Hash:** Must use `bcrypt` format (starts with `$2b$`). NEVER plaintext.
- **Initial Seed:** Migration script creates default `admin` user if table is empty.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

