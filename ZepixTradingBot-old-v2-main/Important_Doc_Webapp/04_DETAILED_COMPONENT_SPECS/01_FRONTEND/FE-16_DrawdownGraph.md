# FE-16: DRAWDOWN GRAPH SPECIFICATION
**Component ID:** FE-16  
**Layer:** Component (Viz)  
**Lib:** Recharts (ComposedChart / Area)

---

## 1. 🖼️ Visual Context
A specialized chart to visualize risk. It typically shows "distance from peak equity".

- **Y-Axis:** Represents percentage (0% to -100%).
- **Color:** Red Fill/Stroke (`#EF4444`).
- **Goal:** Show how deep the losses went.

## 2. 🧩 React Implementation

```tsx
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function DrawdownChart({ data }) {
  // data format: { time: '...', drawdown: -5.2 }
  
  return (
    <div className="w-full h-64 p-4 bg-dark-900 border border-dark-700 rounded-2xl">
      <h3 className="text-sm font-semibold text-gray-400 mb-4">Max Drawdown</h3>
      
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
            </linearGradient>
          </defs>
          
          <XAxis dataKey="time" hide />
          <YAxis stroke="#6b7280" unit="%" />
          <Tooltip 
             contentStyle={{ backgroundColor: '#0A0A0F', borderColor: '#EF4444' }}
             formatter={(val) => `${val}%`}
          />
          
          <Area 
            type="step" 
            dataKey="drawdown" 
            stroke="#EF4444" 
            fill="url(#colorDrawdown)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
```

## 3. 📉 Logic
- Drawdown is ALWAYS negative or zero.
- `0` means we are at All-Time High equity.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

