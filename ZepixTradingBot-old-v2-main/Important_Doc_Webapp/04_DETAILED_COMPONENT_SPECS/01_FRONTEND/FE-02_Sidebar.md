# FE-02: SIDEBAR SPECIFICATION
**Component ID:** FE-02  
**Layer:** Navigation  
**Reference:** `PROTOTYPE_DASHBOARD.html`

---

## 1. 🏗️ Layout & Dimensions
- **Width:** `w-64` (260px) fixed.
- **Height:** `h-screen` (100vh).
- **Background:** `bg-[#131622]` (Dark Card) with `backdrop-filter: blur(12px)`.
- **Border:** Right border `1px solid rgba(64, 86, 235, 0.2)`.
- **Z-Index:** 100 (Fixed).

## 2. 🧭 Navigation Structure

### Section 1: Brand (Top)
- **Container:** `padding: 0 24px 32px`.
- **Border:** Bottom border `1px solid rgba(64, 86, 235, 0.2)`.
- **Logo:** `text-2xl font-extrabold` with Gradient Text (`--brand-gradient`). Icon (`fa-robot`).

### Section 2: Main Navigation (Middle)
Vertical list of navigation items.

| Icon (FontAwesome) | Label | Route |
| :--- | :--- | :--- |
| `fa-chart-line` | Dashboard | `/` |
| `fa-cogs` | Bot Control | `/bot-control` |
| `fa-chart-bar` | Analytics | `/analytics` |
| `fa-bolt` | Live Trading | `/live` |
| `fa-shield-alt` | Risk Manager | `/risk` |

### Section 3: Footer (Bottom)
- **Container:** `padding: 24px`.
- **Logout Button:** Full width, outline style (`bg-white/5`, `border-glass`).

## 3. 🎨 NavItem Component Design

### Default State (Inactive)
- **Background:** Transparent.
- **Text:** `--text-secondary` (#A0AEC0).
- **Border:** Left border `3px solid transparent`.
- **Hover:** `bg-glass`, Text White, Border `--brand-primary`.

### Active State (Selected)
- **Background:** `var(--glass-bg)`.
- **Text:** White (`--text-primary`).
- **Border:** Left border `3px solid var(--brand-primary)`.

### Code Spec (NavItem)
```tsx
const NavItem = ({ icon, label, isActive, onClick }) => (
  <div 
    onClick={onClick}
    className={`
      flex items-center gap-3 px-6 py-3.5 cursor-pointer transition-all duration-300 border-l-4
      ${isActive 
        ? 'bg-white/5 text-white border-primary-500' 
        : 'text-gray-400 border-transparent hover:bg-white/5 hover:text-white hover:border-primary-500'}
    `}
  >
    <i className={`fas ${icon} w-5 text-center`}></i>
    <span className="font-medium">{label}</span>
  </div>
);
```

## 4. 📱 Mobile Behavior
- **Sidebar:** Hidden by default.
- **Trigger:** Hamburger menu in Header toggles `display: flex`.
- **Overlay:** Backrop blur overlay.

## 5. 💡 Implementation Details
- Strictly use `PROTOTYPE_DASHBOARD.html` CSS classes (`.nav-item`, `.sidebar`).
- Icons: FontAwesome 6.4.0.
