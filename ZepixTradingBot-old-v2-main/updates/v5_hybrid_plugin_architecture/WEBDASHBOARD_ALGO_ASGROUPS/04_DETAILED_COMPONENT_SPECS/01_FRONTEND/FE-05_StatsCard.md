# FE-05: STATS CARD SPECIFICATION
**Component ID:** FE-05  
**Layer:** Component (Widget)  
**Usage:** Dashboard Home, Analytics Page
# FE-05: STATS CARD SPECIFICATION
**Component ID:** FE-05  
**Layer:** Component (Widget)  
**Usage:** Dashboard Home, Analytics Page

---

## 1. 🖼️ Visual Structure
A rectangular card displaying a single key metric with context.

### Layout
```
┌────────────────────────────────────────┐
│  LABEL (Uppercased, Muted)             │
│                                        │
│  VALUE (32px, Bold, Colored)           │
│                                        │
│  +8.5% vs last week (Small text)       │
└────────────────────────────────────────┘
```

- **Container:** `glass-card` (`backdrop-filter: blur`, `border-glass`).
- **Typography:** Value is `text-3xl font-bold`. Label is `text-sm uppercase text-secondary`.
- **Interaction:** Hover lift effect.



## 2. 🎨 Variants

### Variant A: Primary (Balance/Profit)
- **Icon Color:** Electric Blue or Emerald Green.
- **Value Details:** Formatting currency (e.g., `$1,240.50`).

### Variant B: Danger (Drawdown)
- **Icon Color:** Red.
- **Value Details:** Percentage format (`-5.2%`).

## 3. 🧩 React Interface

```tsx
interface StatsCardProps {
  label: string;
  value: string;
  subValue?: string;
  trend?: 'profit' | 'loss' | 'neutral';
}

export default function StatsCard({ label, value, subValue, trend = 'neutral' }: StatsCardProps) {
  return (
    <div className="glass-card hover:-translate-y-1 transition-transform duration-300">
      <div className="text-secondary text-sm uppercase tracking-wide mb-2">{label}</div>
      <div className={`text-3xl font-bold mb-2 ${trend === 'profit' ? 'text-profit' : trend === 'loss' ? 'text-loss' : 'text-white'}`}>
        {value}
      </div>
      {subValue && (
        <div className="text-xs text-secondary">
          <span className={`${trend === 'profit' ? 'text-profit' : trend === 'loss' ? 'text-loss' : 'text-white'}`}>
            {subValue.split(' ')[0]} 
          </span>
          {' ' + subValue.split(' ').slice(1).join(' ')}
        </div>
      )}
    </div>
  );
}
```

## 4. 📐 Responsive Behavior
- **Grid:** Typically used in a `grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6`.
- **Mobile:** Full width card.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

