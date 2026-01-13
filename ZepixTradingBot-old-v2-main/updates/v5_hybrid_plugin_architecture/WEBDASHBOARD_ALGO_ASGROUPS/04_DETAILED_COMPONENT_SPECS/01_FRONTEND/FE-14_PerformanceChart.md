# FE-14: PERFORMANCE CHART SPECIFICATION
# FE-14: PERFORMANCE CHART SPECIFICATION
**Component ID:** FE-14  
**Layer:** Component (Viz)  
**Lib:** Recharts (Advanced)

---

## 1. 🖼️ Visual Design
Glassmorphism Card containing an interactive chart (Bar or Area).

- **Header:** "Performance Analytics" with Dropdown filter.
- **Style:** `glass-card` styling.
- **Colors:** Gradient bars/areas (Blue/Profit/Loss).
- **Control:** Timeframe selector (7 Days, 30 Days).

## 2. 🧩 Data Structure
```typescript
interface ChartData {
  timestamp: string; // ISO Date
  balance: number;   // Total Equity
  pnl: number;       // Daily PnL
}
```

## 3. 🧬 React Implementation

```tsx
import { BarChart, Bar, AreaChart, Area, XAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function PerformanceChart({ data, type = 'bar' }) {
  return (
    <div className="glass-card">
      <div className="flex justify-between items-center mb-5">
        <h3 className="text-lg font-bold text-white">Performance Analytics</h3>
        <select className="bg-black/30 border border-white/10 rounded-lg px-3 py-1 text-sm text-gray-300 outline-none focus:border-profit">
          <option>Last 7 Days</option>
          <option>Last 30 Days</option>
          <option>All Time</option>
        </select>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          {type === 'bar' ? (
             <BarChart data={data}>
               <Bar dataKey="value" fill="url(#gradientBar)" radius={[4, 4, 0, 0]} />
             </BarChart>
          ) : (
             <AreaChart data={data}>
                <Area type="monotone" dataKey="value" stroke="#4056EB" fill="url(#gradientArea)" />
             </AreaChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
```

## 4. 🎨 Styling Details
- **Grid Lines:** Very subtle `stroke="#1f2937"` (gray-800).
- **Axis Text:** Small `text-xs text-gray-500`.
- **Curve:** `monotone` interpolation for smooth lines.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

