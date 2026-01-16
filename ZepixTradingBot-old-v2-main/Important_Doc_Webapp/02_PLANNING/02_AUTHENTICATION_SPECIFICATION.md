# AUTHENTICATION & AUTHORIZATION SPECIFICATION - algo.asgroups

**Date:** 2026-01-13  
**Project:** algo.asgroups Web Dashboard  
**Auth Method:** Simple Username/Password (User-specified)  
**Status:** Planning Complete  

---

## 🔐 AUTHENTICATION OVERVIEW

### Authentication Method
**Type:** Simple Username/Password  
**Token Standard:** JWT (JSON Web Tokens)  
**Storage:** HTTP-only cookies (secure)  
**Session Duration:** 1 hour (with refresh token)

### User Preference
- ❌ OAuth (Google/GitHub) - Not required
- ✅ Simple username/password - User preference
- ✅ Easy setup and management
- ✅ No third-party dependencies

---

## 👤 USER MANAGEMENT

### User Roles
1. **Admin** (Full access)
   - Control bot (start/stop/restart)
   - Modify configuration
   - View all analytics
   - Manage users
   - Access all features

2. **Viewer** (Read-only)
   - View dashboard
   - View analytics
   - View trade history
   - Cannot modify settings
   - Cannot control bot

### Initial Setup
- **Default Admin User:** Created during installation
- **Username:** Set by user during deployment
- **Password:** Strong password (minimum 12 characters)
- **Additional Users:** Created by admin via dashboard

---

## 🔑 PASSWORD SECURITY

### Password Requirements
```plaintext
Minimum Length: 12 characters
Must Include:
- At least 1 uppercase letter (A-Z)
- At least 1 lowercase letter (a-z)
- At least 1 number (0-9)
- At least 1 special character (!@#$%^&*)

Examples:
✅ MyBot@2026Pass
✅ Trading$ecure123
❌ password123 (too weak)
❌ 12345678 (no letters)
```

### Password Storage
- **Hashing Algorithm:** bcrypt (cost factor: 12)
- **Salt:** Unique per user (automatic)
- **Storage:** Never store plain text passwords
- **Comparison:** Always use bcrypt.compare()

```python
# Example password hashing
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("user_password")

# Verify password
is_valid = pwd_context.verify("user_password", hashed)
```

---

## 🎫 JWT TOKEN SYSTEM

### Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "username": "admin",
    "role": "admin",
    "exp": 1705123456,
    "iat": 1705119856
  },
  "signature": "..." 
}
```

### Token Types

#### 1. Access Token
- **Purpose:** Authenticate API requests
- **Duration:** 1 hour
- **Storage:** HTTP-only cookie
- **Refresh:** Automatic via refresh token

#### 2. Refresh Token
- **Purpose:** Renew access token
- **Duration:** 7 days
- **Storage:** HTTP-only cookie (separate)
- **Usage:** Exchange for new access token

### Token Configuration
```python
# JWT Settings
SECRET_KEY = "your-secret-key-256-bits"  # From .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 7      # 7 days
```

---

## 🚪 AUTHENTICATION FLOW

### Login Flow
```
1. User enters username + password
   ↓
2. Frontend sends POST /api/auth/login
   {
     "username": "admin",
     "password": "MyBot@2026Pass"
   }
   ↓
3. Backend validates credentials
   - Check username exists
   - Verify password with bcrypt
   ↓
4. If valid: Generate JWT tokens
   - Create access token (1h)
   - Create refresh token (7d)
   ↓
5. Send tokens as HTTP-only cookies
   Set-Cookie: access_token=...
   Set-Cookie: refresh_token=...
   ↓
6. Return user info to frontend
   {
     "username": "admin",
     "role": "admin",
     "message": "Login successful"
   }
   ↓
7. Frontend redirects to dashboard
```

### Logout Flow
```
1. User clicks "Logout"
   ↓
2. Frontend sends POST /api/auth/logout
   ↓
3. Backend clears cookies
   Set-Cookie: access_token=; Max-Age=0
   Set-Cookie: refresh_token=; Max-Age=0
   ↓
4. Frontend redirects to login page
```

### Token Refresh Flow
```
1. Access token expires (after 1 hour)
   ↓
2. Frontend receives 401 Unauthorized
   ↓
3. Frontend sends POST /api/auth/refresh
   (with refresh_token cookie)
   ↓
4. Backend validates refresh token
   ↓
5. If valid: Generate new access token
   Set-Cookie: access_token=new_token
   ↓
6. Frontend retries original request
   (with new access token)
```

---

## 🛡️ SECURITY MEASURES

### Cookie Security
```python
# HTTP-only cookies (cannot be accessed by JavaScript)
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,       # Prevent XSS attacks
    secure=True,         # Only send over HTTPS
    samesite="strict",   # Prevent CSRF attacks
    max_age=3600,        # 1 hour
    path="/"
)
```

### CORS Configuration
```python
# Allow only frontend domain
ALLOWED_ORIGINS = [
    "https://algo.asgroups",
    "http://localhost:3000"  # Development only
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,  # Allow cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Rate Limiting
```python
# Login endpoint rate limiting
@limiter.limit("5 per minute")
@app.post("/api/auth/login")
async def login():
    ...
```

**Limits:**
- Login attempts: 5 per minute per IP
- API requests: 100 per minute per user
- Failed login lockout: 15 minutes after 5 failed attempts

---

## 📋 API ENDPOINTS

### Authentication Endpoints
```python
POST   /api/auth/login          # Login with username/password
POST   /api/auth/logout         # Logout and clear tokens
POST   /api/auth/refresh        # Refresh access token
GET    /api/auth/me             # Get current user info
POST   /api/auth/change-pass   # Change password
```

### User Management Endpoints (Admin only)
```python
GET    /api/users               # List all users
POST   /api/users               # Create new user
GET    /api/users/{id}          # Get user details
PUT    /api/users/{id}          # Update user
DELETE /api/users/{id}          # Delete user
PUT    /api/users/{id}/role     # Change user role
```

---

## 🔒 AUTHORIZATION MIDDLEWARE

### Protected Routes
```python
from fastapi import Depends, HTTPException
from app.auth.jwt import get_current_user

# Require authentication
@app.get("/api/bot/status")
async def get_bot_status(
    current_user: User = Depends(get_current_user)
):
    # Only accessible if valid token
    return {"status": "active"}

# Require admin role
@app.post("/api/bot/start")
async def start_bot(
    current_user: User = Depends(require_admin)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return {"message": "Bot started"}
```

### Role-Based Access Control
```python
# Permission matrix
PERMISSIONS = {
    "admin": [
        "bot:control",
        "bot:config",
        "trades:view",
        "trades:close",
        "analytics:view",
        "users:manage"
    ],
    "viewer": [
        "trades:view",
        "analytics:view"
    ]
}
```

---

## 🎨 LOGIN PAGE DESIGN

### Login UI Components
- **Logo:** algo.asgroups with gradient
- **Username Input:** Email or username
- **Password Input:** Masked with show/hide toggle
- **Remember Me:** Optional (extends refresh token)
- **Login Button:** Gradient button (abhibots.com style)
- **Error Messages:** Red alert for invalid credentials

### Login Page Features
- ✅ Glassmorphism background
- ✅ Gradient logo/heading
- ✅ Input validation (client-side)
- ✅ Loading state during login
- ✅ Error handling (server-side)
- ✅ Responsive design (mobile-friendly)
- ✅ Forgot password link (future feature)

---

## 🧪 TESTING AUTHENTICATION

### Manual Testing Checklist
- [ ] Login with valid credentials → Success
- [ ] Login with invalid username → Error
- [ ] Login with invalid password → Error
- [ ] Access protected route without token → 401
- [ ] Access protected route with valid token → Success
- [ ] Access admin route as viewer → 403
- [ ] Token refresh works → New access token
- [ ] Logout clears cookies → Redirect to login
- [ ] Rate limiting after 5 failed attempts → 429

### Test Credentials (Development)
```plaintext
Admin User:
  Username: admin
  Password: Admin@2026Testing

Viewer User:
  Username: viewer
  Password: Viewer@2026Testing
```

---

## 🔐 PASSWORD RESET (Future Feature)

### Planned Implementation
1. **Forgot Password Link** on login page
2. **Email Verification** (requires SMTP config)
3. **Reset Token** (expires in 15 minutes)
4. **New Password Form** with validation

**Status:** Not in initial release (Phase 1)  
**Priority:** Medium (can be added later)

---

## 📊 DATABASE SCHEMA

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Default admin user (created during setup)
INSERT INTO users (username, password_hash, role)
VALUES (
    'admin',
    '$2b$12$hashed_password_here',
    'admin'
);
```

### Sessions Table (Optional - for tracking)
```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    token_jti VARCHAR(255) UNIQUE,  -- JWT ID
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

---

## 🚀 SETUP INSTRUCTIONS

### Step 1: Create Admin User
```bash
# During deployment, run setup script
python scripts/create_admin.py

# Prompt:
# Enter admin username: admin
# Enter admin password: [strong password]
# Confirm password: [strong password]
```

### Step 2: Configure Environment
```bash
# Add to .env file
SECRET_KEY=your-256-bit-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Step 3: Test Login
```bash
# Test login endpoint
curl -X POST https://algo.asgroups/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'

# Expected response:
# {
#   "username": "admin",
#   "role": "admin",
#   "message": "Login successful"
# }
```

---

## ✅ AUTHENTICATION CHECKLIST

- [ ] Password hashing with bcrypt implemented
- [ ] JWT token generation working
- [ ] HTTP-only cookies configured
- [ ] Login endpoint functional
- [ ] Logout endpoint functional
- [ ] Token refresh endpoint functional
- [ ] Protected routes require authentication
- [ ] Admin-only routes check role
- [ ] Rate limiting enabled
- [ ] CORS configured correctly
- [ ] Login page UI designed
- [ ] Error messages user-friendly
- [ ] Database users table created
- [ ] Default admin user created
- [ ] Security headers configured

---

**Authentication Documentation Status:** ✅ **COMPLETE**  
**Auth Method:** Simple Username/Password (as per user preference)  
**Token Type:** JWT with HTTP-only cookies  
**Security:** bcrypt + rate limiting + CORS + HTTPS


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

