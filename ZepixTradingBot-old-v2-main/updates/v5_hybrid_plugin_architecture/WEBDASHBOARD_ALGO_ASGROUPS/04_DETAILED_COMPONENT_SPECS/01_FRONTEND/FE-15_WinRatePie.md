# FE-15: WIN RATE PIE CHART SPECIFICATION
**Component ID:** FE-15  
**Layer:** Component (Viz)  
**Lib:** Recharts (PieChart)

---

## 1. 🖼️ Visual Design
A visual breakdown of Wins vs. Losses.

- **Type:** Donut Chart (Inner R > 0).
- **Colors:**
  - **Wins:** `#10B981` (Emerald).
  - **Losses:** `#EF4444` (Red).
  - **Breakeven:** `#6B7280` (Gray).
- **Center Text:** Displays the "Win Rate %" in large typography.

## 2. 🧩 React Implementation

```tsx
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export default function WinRateChart({ wins, losses, breakeven }) {
  const data = [
    { name: 'Wins', value: wins },
    { name: 'Losses', value: losses },
    { name: 'Breakeven', value: breakeven },
  ];
  
  const COLORS = ['#10B981', '#EF4444', '#6B7280'];
  const total = wins + losses + breakeven;
  const winRate = total > 0 ? ((wins / total) * 100).toFixed(1) : 0;

  return (
    <div className="relative h-64 w-full bg-dark-900 border border-dark-700 rounded-2xl p-6 flex flex-col items-center">
      <h3 className="text-sm font-semibold text-gray-400 w-full text-left mb-4">Win / Loss Ratio</h3>
      
      <div className="relative w-full h-full">
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data}
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
        
        {/* Center Text Overlay */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-3xl font-bold text-white">{winRate}%</span>
          <span className="text-xs text-gray-500 uppercase tracking-wide">Win Rate</span>
        </div>
      </div>
      
      {/* Legend */}
      <div className="flex gap-4 mt-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500" /> Wins ({wins})
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" /> Losses ({losses})
        </div>
      </div>
    </div>
  );
}
```

## 3. 🎨 Design Details
- **Padding Angle:** `5px` to separate slices cleanly.
- **Stroke:** `none` (removes default white border).


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

