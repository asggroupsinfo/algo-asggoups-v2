# FE-20: THEME CONFIGURATION (UPDATED)
**Component ID:** FE-20  
**Context:** Global Design Tokens  
**Source:** 
> 
> **MANDATORY DESIGN SOURCE FILES:**
> 1. `WEBDASHBOARD_ALGO_ASGROUPS/03_COLOR_DESIGN/BRAND WEBSITE COLOR AND PROTOTYPE.HTML`
> 2. `WEBDASHBOARD_ALGO_ASGROUPS/03_COLOR_DESIGN/COLOR_PREVIEW AND PROTOTYPE.html`
>
> *Developers must strictly follow the CSS variables, layout, and visual interactions defined in these HTML files.*

---

## 1. 🎨 Color Palette (Tailwind Config)

```javascript
// tailwind.config.ts extension
colors: {
  // Core Backgrounds
  dark: {
    950: '#0B0B15', // --bg-deep
    900: '#131622', // --bg-card
    800: '#1A1D2D', // Lighter card/hover
  },
  
  // Brand Gradients (Use as bg-gradient-to-r)
  brand: {
    primary: '#4056EB',   // --brand-primary
    secondary: '#763CED', // --brand-secondary
    accent: '#22D3EE',    // --accent-teal
  },
  
  // Status Colors
  status: {
    profit: '#00D1A7',      // --profit
    profitGlow: 'rgba(0, 209, 167, 0.3)',
    loss: '#F75555',        // --loss
    lossGlow: 'rgba(247, 85, 85, 0.3)',
    warning: '#FFB443',     // --warning
  },
  
  // Text
  text: {
    primary: '#FFFFFF',
    secondary: '#A0AEC0',
    muted: '#718096',
  }
}
```

## 2. ✨ Glassmorphism Utilities

```css
/* Globals.css */
.glass-panel {
  background: rgba(19, 22, 34, 0.7); /* --glass-bg */
  backdrop-filter: blur(12px);
  border: 1px solid rgba(64, 86, 235, 0.2); /* --glass-border */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37); /* --glass-shadow */
}

.glass-panel:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  border-color: #4056EB; /* Brand Primary */
}
```

## 3. 🖋️ Typography
**Font Family:** `Segoe UI`, `system-ui`, `-apple-system`, `sans-serif` (Matching prototype).

- **H1:** `text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400`.
- **Label:** `text-sm font-semibold text-secondary uppercase tracking-wider`.

## 4. 🌀 Animations
- **Pulse:** `animate-pulse` (Custom: Shadow glow pulse).
- **FadeIn:** `transition-opacity duration-300`.
- **Hover:** `transition-all duration-200 ease-out`.

## 5. 🧩 Common Patterns
- **Buttons:** Gradient background `bg-gradient-to-r from-brand-primary to-brand-secondary`.
- **Tags:** Pill shape with `bg-opacity-10` background and matching text color.
- **Charts:** Use `Chart.js` or `Recharts` with custom Grid colors (`rgba(255,255,255,0.05)`).


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

