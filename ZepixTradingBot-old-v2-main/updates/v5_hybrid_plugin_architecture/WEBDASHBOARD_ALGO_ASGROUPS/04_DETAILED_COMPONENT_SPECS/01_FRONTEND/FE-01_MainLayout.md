# FE-01: MAIN LAYOUT SPECIFICATION
**Component ID:** FE-01  
**Layer:** Layout  
**Tech Stack:** Next.js 14, Tailwind CSS

---

## 1. �️ User Journey (Mandatory Flow)
The application MUST follow this strict sequence:
1.  **Step 1: Landing Page (`FE-00A`)** - Public Brand Website.
2.  **Step 2: Login Page (`FE-00B`)** - Authentication Gate.
3.  **Step 3: Dashboard Layout (`FE-01`)** - The main application view described below.

---

## 2. �📐 Layout Architecture
The dashboard uses a **Fixed Sidebar + Fluid Content** layout pattern.

### Structure Diagram
```
┌─────────────────┬───────────────────────────────────────────────┐
│                 │  HEADER (Fixed / Sticky)                      │
│    SIDEBAR      ├──────────────────────┬────────────────────────┤
│    (Fixed)      │                      │                        │
│    w-64         │  MAIN CONTROLS       │  NOTIFICATIONS         │
│    (256px)      │  (Charts & Bots)     │  (Live Feed)           │
│                 │  Width: ~66%         │  Width: ~33%           │
│                 │                      │                        │
└─────────────────┴──────────────────────┴────────────────────────┘
```

## 3. 🖥️ Desktop Layout
- **Sidebar:** Fixed width `w-64` (256px), 100vh height.
- **Main Wrapper:** `ml-64` to push content right.
- **Inner Content Grid:**
    - **Row 1:** Metrics Grid (4 columns).
    - **Row 2:** Split View (2 columns) - Left: Charts/Controls, Right: Notification Panel.
- **Background:** `bg-dark-950` (#050507).

## 4. 📱 Mobile Layout (< 1024px)
- **Sidebar:** Hidden by default (`hidden`).
- **Main Wrapper:** No margin (`ml-0`).
- **Header:** Contains "Hamburger" menu button to trigger Off-Canvas Sidebar.
- **Off-Canvas:** Slide-over sidebar with backdrop overlay (`z-50`).

## 4. 🧩 React Implementation

### Component Structure
```tsx
// src/components/layout/DashboardLayout.tsx

import Sidebar from './Sidebar';
          {children}
        </main>

      </div>
      
    </div>
  );
}
```

## 5. 🎨 Styling Specifications
- **Z-Index Strategy:**
  - Sidebar: `z-40`
  - Header: `z-30`
  - Modals/Overlays: `z-50`
  - Toast Notifications: `z-[60]`
- **Scroll Behavior:**
  - Sidebar: Internal scroll if items overflow (`overflow-y-auto`).
  - Main Layout: Window scroll.
  - Scrollbar Style: Thin, customized thumb color (`bg-dark-700`).

## 6. 🔗 Integration Notes
- This layout wraps all protected pages (dashboard, settings, logs).
- Authentication pages (Login/Register) use a separate `AuthLayout`.
- Add `supense` fallback for page transitions.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

