# BE-02: USER MANAGEMENT API SPECIFICATION
**Component ID:** BE-02  
**Layer:** API Endpoint  
**Path:** `/api/users`  
**Auth:** Admin Only (except Profile update)

---

## 1. 📝 Overview
Manages user accounts, roles, and password updates.

## 2. 🛣️ Endpoints

### 2.1 List Users
**GET** `/api/users`
- **Auth:** Admin
- **Response (200 OK):**
  ```json
  [
    {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "is_active": true,
      "created_at": "2026-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "username": "viewer1",
      "role": "viewer",
      "is_active": true
    }
  ]
  ```

### 2.2 Create User
**POST** `/api/users`
- **Auth:** Admin
- **Body:**
  ```json
  {
    "username": "new_trader",
    "password": "SecretPassword123!",
    "role": "editor" // admin, editor, viewer
  }
  ```
- **Validation:** Username unique check, Password complexity check.

### 2.3 Update Profile (Self)
**PUT** `/api/users/me`
- **Auth:** Any Authenticated User
- **Body:**
  ```json
  {
    "password_current": "OldPass",
    "password_new": "NewPass"
  }
  ```

### 2.4 Delete User
**DELETE** `/api/users/{user_id}`
- **Auth:** Admin
- **Constraint:** Cannot delete self (Admin cannot delete the last Admin).

## 3. 🧪 Logic Rules
- **Role Hierarchy:**
  - `admin`: Can modify everything.
  - `editor`: Can modify bot config, cannot manage users.
  - `viewer`: Read-only access.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

