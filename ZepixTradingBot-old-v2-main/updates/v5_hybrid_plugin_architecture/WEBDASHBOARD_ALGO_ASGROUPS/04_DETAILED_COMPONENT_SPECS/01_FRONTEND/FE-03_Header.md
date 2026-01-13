# FE-03: HEADER SPECIFICATION
**Component ID:** FE-03  
# FE-03: HEADER SPECIFICATION
**Component ID:** FE-03  
**Layer:** Layout  
**Style:** Glassmorphism

---

## 1. 🏗️ Layout & Dimensions
- **Position:** In-flow (Not fixed globally, part of `main-content`).
- **Padding:** `mb-8` (Bottom margin).
- **Flex:** `justify-between items-center`.

## 2. 🎨 Visual Style
- **Typography:** Page Title `text-3xl font-bold` (No gradient, typically white).
- **Subtext:** `text-sm text-secondary` ("Welcome back...").

## 3. 🧩 Component Slots

### Left Slot: Context/Breadcrumbs
- **Mobile:** Hamburger Menu Button (Visible only on lg:hidden).
- **Desktop:**
  - "Profile"
  - "Theme Settings" (if configurable)
  - "Logout"

### Code Spec (Header)
```tsx
export default function PageHeader({ title, subtitle, status }) {
  return (
    <header className="flex justify-between items-center mb-8">
      <div>
        <h1 className="text-3xl font-bold text-white">{title}</h1>
        <p className="text-secondary mt-1">{subtitle}</p>
      </div>
      
      {/* Status Pill */}
      <div className="flex items-center gap-3">
        <div className={`
          flex items-center gap-2 px-4 py-1.5 rounded-full border text-xs font-bold uppercase tracking-wide
          ${status === 'ONLINE' ? 'bg-profit/10 text-profit border-profit/20' : 'bg-loss/10 text-loss border-loss/20'}
        `}>
          <i className="fas fa-circle text-[8px]"></i>
          SYSTEM {status}
        </div>
      </div>
    </header>
  );
}
```

## 4. 🔗 Data Integration
- **Status Indicator:** Consumes `useBotStore` (Zustand) to check WebSocket `system_status` (RUNNING/STOPPED).
- **Notifications:** Connects to `useAlertStore` count.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

