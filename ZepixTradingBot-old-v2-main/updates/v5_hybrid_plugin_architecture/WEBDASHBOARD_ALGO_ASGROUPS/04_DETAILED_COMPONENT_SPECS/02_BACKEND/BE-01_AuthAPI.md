# BE-01: AUTHENTICATION API SPECIFICATION
**Component ID:** BE-01  
**Layer:** API Endpoint  
**Path:** `/api/auth`  
**Auth:** Public (None)

---

## 1. 📝 Overview
Handles user session creation, validation, and destruction using JWT stored in secure HTTP-only cookies.

## 2. 🛣️ Endpoints

### 2.1 Login
**POST** `/api/auth/login`
- **Purpose:** Authenticate user and issue cookies.
- **Request Body:** `application/x-www-form-urlencoded`
  ```json
  {
    "username": "admin",
    "password": "strong_password_123"
  }
  ```
- **Response (200 OK):**
  - **Headers:** 
    - `Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Strict; Max-Age=3600`
    - `Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=Strict; Max-Age=604800`
  - **Body:**
    ```json
    {
      "user": {
        "username": "admin",
        "role": "admin",
        "last_login": "2026-01-13T10:00:00Z"
      },
      "message": "Login successful"
    }
    ```
- **Error (401 Unauthorized):** Invalid credentials.
- **Error (429 Too Many Requests):** Rate limit exceeded (5 attempts/min).

### 2.2 Refresh Token
**POST** `/api/auth/refresh`
- **Purpose:** Get new access token using valid refresh token cookie.
- **Request:** Cookie `refresh_token` required.
- **Response (200 OK):** Updates `access_token` cookie.

### 2.3 Logout
**POST** `/api/auth/logout`
- **Purpose:** Invalidate session on client side.
- **Response (200 OK):** Clears both cookies (`Max-Age=0`).

### 2.4 Verify Session (Me)
**GET** `/api/auth/me`
- **Purpose:** Check if current user is logged in (used by Frontend AuthGuard).
- **Request:** Cookie `access_token` required.
- **Response (200 OK):** Returns user profile.
- **Error (401):** Not authenticated.

## 3. 🛡️ Security Implementation
- **Hashing:** `bcrypt` (passlib).
- **Token:** `PyJWT` (HS256).
- **Rate Limit:** `slowapi` implementation (Redis/Memory).


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

