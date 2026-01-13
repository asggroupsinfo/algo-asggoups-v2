# FE-00A: BRAND LANDING PAGE SPECIFICATION
**Component ID:** FE-00A  
**Context:** Public Facing Brand Website  
**Source Prototype:** `PROTOTYPE_DASHBOARD.html` (View 1)

---

## 1. 🎯 Objective
Create a high-impact, premium landing page to showcase the `algo.asggroups` platform. This page serves as the entry point and must strictly follow the "Dark Glassmorphism" aesthetic defined in the prototype.

## 2. 📐 Layout Structure
The page is divided into 4 main vertical sections:
1.  **Glass Navigation Bar** (Sticky Top)
2.  **Hero Section** (Center Impact)
3.  **Features Grid** (Value Props)
4.  **Footer** (Links & Info)

---

## 3. 🧩 Component Details

### 3.1 Navigation Bar (`.navbar`)
*   **Position:** Fixed Top, Z-Index 1000.
*   **Style:** Glassmorphism (`backdrop-filter: blur(12px)`, `border-bottom: 1px solid rgba(64, 86, 235, 0.2)`).
*   **Content:**
    *   **Logo:** Left-aligned, Gradient Text (`--brand-gradient`), Icon (`fa-robot`).
    *   **Links:** Center-aligned (Features, Strategies, Dashboard, Pricing).
    *   **CTA Button:** Right-aligned, "Launch Dashboard", Gradient Background.

### 3.2 Hero Section (`.hero`)
*   **Alignment:** Centered text and actions.
*   **Typography:**
    *   **H1:** Massive (3.5rem+), Gradient Text (`linear-gradient(90deg, #60A5FA, #22D3EE, #C084FC)`).
    *   **Subtitle:** Large, muted gray text (`--text-secondary`).
*   **Actions:** Two buttons ("Start Trading Now" - Primary, "Watch Demo" - Outline).
*   **Stats Row:** 4 columns showing:
    *   Active Bots (2,963)
    *   Total Volume ($12.4M+)
    *   Active Traders
    *   Win Rate (67.5%)

### 3.3 Features Grid (`.section`)
*   **Layout:** Responsive Grid (`grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))`).
*   **Cards:** Glass cards with hover lift effect (`transform: translateY(-8px)`).
*   **Icons:** Large, gradient-background icons for each feature.

---

## 4. 🎨 Visual Styles (Strict Adherence)
*   **Background:** Deep Navy (`#0B0B15`).
*   **Gradients:** Use `--brand-gradient` (#4056EB to #763CED).
*   **Animations:** Elements must `fade-in` on load (0.5s duration).

## 5. 🔗 Interaction Logic
*   **"Launch Dashboard" Button:** Triggers transition to **Login View** (`FE-00B`).
*   **"Start Trading" Button:** Triggers transition to **Login View** (`FE-00B`).

---

## ✅ Implementation Checklist
- [ ] Implement Sticky Glass Navbar.
- [ ] Create Gradient Text Utility class.
- [ ] Build Responsive Hero Section.
- [ ] Implement Stats Counter.
- [ ] Ensure "Launch" buttons route to Login Page.
