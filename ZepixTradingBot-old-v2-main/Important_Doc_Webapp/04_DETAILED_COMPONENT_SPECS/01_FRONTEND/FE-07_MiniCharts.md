# FE-07: MINI CHARTS (SPARKLINE)
**Component ID:** FE-07  
**Layer:** Component (Visualization)  
**Library:** Recharts (ResponsiveContainer, AreaChart)

---

## 1. 🖼️ Usage Context
Small charts embedded in specific cards (like a crypto asset card) to show the "Latest 1H Trend" or "24H P&L Trend" without taking up full screen space.

## 2. 🎨 Visual Configuration
Because these are "Mini" charts, axes and grids are stripped away.

- **Type:** Area Chart (Filled gradient below line).
- **Line Stroke:** `2px` width.
- **Dots:** Hidden (`r: 0`), visible only on hover.
- **Axes:** Hidden (`hide`).
- **Grid:** Hidden.

### Colors (Dynamic)
- **Profit (Up Trend):** Stroke `#10B981` (Emerald), Fill Gradient `Emerald -> Transparent`.
- **Loss (Down Trend):** Stroke `#EF4444` (Red), Fill Gradient `Red -> Transparent`.

## 3. 🧩 React Implementation

```tsx
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';

interface MiniChartProps {
  data: { value: number, time: string }[];
  isPositive: boolean;
}

export default function MiniChart({ data, isPositive }: MiniChartProps) {
  const color = isPositive ? '#10B981' : '#EF4444';
  const id = `gradient-${isPositive ? 'up' : 'down'}`;

  return (
    <div className="h-16 w-32">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={color} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <Tooltip cursor={false} content={<CustomTooltip />} />
          <Area 
            type="monotone" 
            dataKey="value" 
            stroke={color} 
            strokeWidth={2} 
            fillOpacity={1} 
            fill={`url(#${id})`} 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
```

## 4. 📄 Data Requirements
- Array of simple objects: `[{ time: '10:00', value: 100 }, { time: '10:05', value: 102 }]`.
- Needs at least 10-20 data points for a smooth curve.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

