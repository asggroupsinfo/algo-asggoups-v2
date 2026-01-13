# FE-09: STRATEGY SELECTOR SPECIFICATION
**Component ID:** FE-09  
**Layer:** Component (Form Control)  
**Use Case:** Selecting active trading logic (V3, V6, Hybrid)

---

## 1. 🖼️ Visual Design
A visual grid of selectable cards, rather than a simple dropdown.

### Card State
- **Inactive:** `bg-dark-800`, `border-transparent`, `opacity-60`.
- **Selected:** `bg-primary-600/20`, `border-primary-500`, `opacity-100`.
- **Hover:** `bg-dark-700`.

### Layout
Grid layout: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`.

## 2. 🧩 Functionality
- **Selection Mode:** Single Select or Multi Select (depending on bot capability).
- **Badge:** Shows "Recommended" or "High Risk" tags on specific strategies.

## 3. 🧪 React Implementation
```tsx
const strategies = [
  { id: 'v3_combined', name: 'V3 Combined', desc: 'Conservative trend following', tag: 'Safe' },
  { id: 'v6_scalp', name: 'V6 Scalp', desc: 'High frequency 1m chart', tag: 'High Risk' },
];

export default function StrategySelector({ selectedId, onSelect }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {strategies.map((strat) => (
        <button
          key={strat.id}
          onClick={() => onSelect(strat.id)}
          className={`
            relative p-4 rounded-xl text-left border transition-all duration-200
            ${selectedId === strat.id 
              ? 'bg-primary-900/20 border-primary-500 ring-1 ring-primary-500/50' 
              : 'bg-dark-800 border-dark-700 hover:border-dark-600'}
          `}
        >
          <div className="flex justify-between items-start mb-2">
            <h4 className={`font-bold ${selectedId === strat.id ? 'text-primary-400' : 'text-gray-200'}`}>
              {strat.name}
            </h4>
            {selectedId === strat.id && (
              <div className="w-4 h-4 rounded-full bg-primary-500 flex items-center justify-center">
                <CheckIcon className="w-3 h-3 text-white" />
              </div>
            )}
          </div>
          
          <p className="text-xs text-gray-500">{strat.desc}</p>
          
           {/* Badge */}
           <span className="absolute top-4 right-4 text-[10px] uppercase font-bold tracking-wider text-gray-600">
             {strat.tag}
           </span>
        </button>
      ))}
    </div>
  );
}
```


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

