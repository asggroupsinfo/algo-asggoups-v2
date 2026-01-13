# BE-03: MIDDLEWARE SPECIFICATION
**Component ID:** BE-03  
**Layer:** Backend Architecture  
**Framework:** FastAPI Middleware

---

## 1. 🛡️ Authentication Middleware
**File:** `app/middleware/auth.py`

### Logic
1. Intercepts every request to protected routes.
2. Extracts `access_token` from Cookies.
3. Decodes JWT using `SECRET_KEY`.
4. Checks expiration (`exp`).
5. Injects `current_user` object into request scope.
6. **Failure:** Returns `401 Unauthorized`.

## 2. 🚦 Rate Limiting Middleware
**File:** `app/middleware/rate_limit.py`

### Configuration
- **Login:** 5 requests / minute / IP.
- **Public API:** 60 requests / minute / IP.
- **Authenticated API:** 300 requests / minute / User.

### Implementation
Uses `slowapi` library backed by in-memory storage (or Redis if available).

## 3. 🌐 CORS Middleware
**File:** `app/main.py`

### Configuration
- **Allow Origins:** `["https://algo.asgroups", "https://www.algo.asgroups"]`
- **Allow Credentials:** `True` (Essential for Cookies).
- **Allow Methods:** `["*"]`
- **Allow Headers:** `["*"]`

## 4. 📝 Request Logging (Audit)
**File:** `app/middleware/audit.py`

### Logic
- Logs every state-changing request (POST, PUT, DELETE).
- **Format:** `[TIMESTAMP] [USER_ID] [METHOD] [PATH] [STATUS]`
- **Storage:** Saved to `audit_logs` table in DB.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

