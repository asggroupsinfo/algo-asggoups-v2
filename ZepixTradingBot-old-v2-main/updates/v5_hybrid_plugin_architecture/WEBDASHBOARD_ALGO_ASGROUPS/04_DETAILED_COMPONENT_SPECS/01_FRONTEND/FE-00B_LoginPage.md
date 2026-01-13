# FE-00B: LOGIN PAGE SPECIFICATION
**Component ID:** FE-00B  
**Context:** Authentication Gate  
**Source Prototype:** `PROTOTYPE_DASHBOARD.html` (View 2)

---

## 1. 🎯 Objective
Provide a secure, aesthetically pleasing entry point to the dashboard. The design uses a "Glass Card" centered on a rich gradient background to create depth and focus.

## 2. 📐 Layout Structure
*   **Container:** Full Screen (`100vh`), Flex Center Alignment.
*   **Background:** Radial Gradient (`radial-gradient(circle at center, rgba(64, 86, 235, 0.15) 0%, var(--bg-deep) 70%)`).
*   **Card:** Centered Glass Panel (400px width).

---

## 3. 🧩 Component Details

### 3.1 Login Card (`.login-card`)
*   **Style:** Heavy Blur (`backdrop-filter: blur(16px)`), Strong Border (`1px solid rgba(64, 86, 235, 0.2)`).
*   **Animation:** `fade-in` on appearance.

### 3.2 Form Elements
*   **Header:** Large Icon (`fa-shield-alt`) with gradient fill. Title "Secure Access".
*   **Inputs:**
    *   Dark background (`rgba(0,0,0,0.3)`).
    *   Focus state: Border glow (`--brand-primary`) + Shadow ring.
    *   Labels: Uppercase, small text (`--text-secondary`).
*   **Button:** Full width, Gradient Background, Icon (`fa-arrow-right`).

### 3.3 Error Handling
*   **Validation:** Client-side check for empty fields.
*   **Error Message:** Red text (`--loss`), initially hidden. Shown on failed auth.

---

## 4. 🔐 Logic Requirements
*   **Default Credentials (Prototype):** `admin` / `password`.
*   **Success Action:**
    1.  Hide Login View.
    2.  Show Dashboard View (`FE-01`).
    3.  Trigger Dashboard Initialization (Chart render, WebSocket connect).
*   **Failure Action:** Show error message, shake animation (optional).

---

## ✅ Implementation Checklist
- [ ] Create Full-screen Gradient Container.
- [ ] Build Centered Glass Login Card.
- [ ] Implement Input Focus States.
- [ ] Wire up "Log In" button verification logic.
- [ ] Ensure smooth fade transition to Dashboard.
