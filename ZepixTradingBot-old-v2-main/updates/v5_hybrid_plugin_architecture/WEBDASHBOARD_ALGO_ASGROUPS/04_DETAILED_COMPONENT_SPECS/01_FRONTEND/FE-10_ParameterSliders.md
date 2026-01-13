# FE-10: PARAMETER SLIDERS SPECIFICATION
**Component ID:** FE-10  
**Layer:** Component (Form Control)  
**Use Case:** Setting Risk Parameters (Stop Loss %, Take Profit %, Leverage)

---

## 1. 🏗️ UX Design pattern
A slider combined with a numeric input field for precision.

### Elements
1. **Label:** "Stop Loss (%)"
2. **Track:** Gray background line.
3. **Fill:** Gradient colored line indicating value.
4. **Thumb:** Circular handle, drag target.
5. **Input Box:** Number field on the right for manual typing.

## 2. 🎨 Visual Style
- **Fill Color:** Matches the context (e.g., Red for Stop Loss, Green for Take Profit).
- **Height:** Track is usually `h-2` (8px). Thumb is `w-5 h-5`.

## 3. 🧩 React Implementation (Radix UI / Headless UI)
Using standard HTML range input customized with Tailwind.

```tsx
interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (val: number) => void;
  color?: 'primary' | 'danger' | 'success'; 
}

export default function ParameterSlider({ label, value, min, max, step, onChange, color = 'primary' }: SliderProps) {
  
  const percentage = ((value - min) / (max - min)) * 100;
  
  const colorClass = {
    primary: 'bg-primary-500',
    danger: 'bg-red-500',
    success: 'bg-emerald-500',
  }[color];

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium text-gray-400">{label}</label>
        <div className="px-2 py-1 bg-dark-800 rounded-md border border-dark-700 min-w-[3rem] text-center">
          <span className="text-sm font-bold text-white">{value}</span>
        </div>
      </div>

      <div className="relative h-2 w-full bg-dark-800 rounded-full">
        {/* Track Fill */}
        <div 
          className={`absolute h-full rounded-full ${colorClass}`} 
          style={{ width: `${percentage}%` }}
        />
        
        {/* Native Range Input (Transparent overlay) */}
        <input 
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
        />
        
        {/* Custom Thumb (Visual Only - positioned via calc) */}
        <div 
            className={`absolute top-1/2 -mt-2.5 w-5 h-5 bg-white rounded-full shadow-lg border-2 border-${color}-500 pointer-events-none transition-all`}
            style={{ left: `calc(${percentage}% - 10px)` }}
        />
      </div>
      
      <div className="flex justify-between text-xs text-dark-500">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}
```

## 4. 💡 User Behavior
- **Debouncing:** When dragging, update local state instantly, but only trigger API update `onMouseUp` to prevent flooding the server.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

