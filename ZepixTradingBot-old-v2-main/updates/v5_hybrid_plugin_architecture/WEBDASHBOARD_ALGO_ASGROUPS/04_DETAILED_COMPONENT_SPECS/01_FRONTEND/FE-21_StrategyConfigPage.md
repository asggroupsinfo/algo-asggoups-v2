# FE-21: STRATEGY CONFIGURATION PAGE
**Component ID:** FE-21  
**Route:** `/settings/strategy`  
**Purpose:** Manage Logic States (1, 2, 3)

---

## 1. 🖼️ Visual Structure
A clean, card-based layout where each Strategy Logic is a distinct block.

- **Layout:** Grid `grid-cols-1 md:grid-cols-3 gap-6`.
- **Card Style:** `glass-panel` (from FE-20).

## 2. 🧩 Card Component Logic

### Header
- **Title:** "LOGIC 1" (Gradient Text).
- **Status Badge:**
  - Active: `bg-status-profit/10 text-status-profit` "ACTIVE".
  - Inactive: `bg-dark-800 text-text-muted` "DISABLED".

### Controls
- **Big Toggle Switch:**
  - **On Click:** POST `/api/bot/command` -> `handle_logic1_on`.
  - **Visual:** Smooth toggle with loading spinner state.

### Stats (Mini)
- Show small "Win Rate" or "Active Trades" for this specific logic if available.

## 3. 🧬 React Implementation

```tsx
export default function StrategyConfig() {
  const { logicStates, toggleLogic } = useBotStore();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-6">Strategy Configuration</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1, 2, 3].map(id => (
          <div key={id} className="glass-panel p-6 rounded-xl relative overflow-hidden group">
            {/* Background Gradient Glow */}
            <div className={`absolute top-0 right-0 w-32 h-32 bg-brand-primary/10 rounded-full blur-3xl 
              transition-opacity ${logicStates[id] ? 'opacity-100' : 'opacity-0'}`} />
            
            <div className="relative z-10 flex justify-between items-start">
              <div>
                <h3 className="text-xl font-bold text-white">LOGIC {id}</h3>
                <p className="text-text-secondary text-sm mt-1">Trend Following Engine</p>
              </div>
              <Switch 
                checked={logicStates[id]} 
                onChange={() => toggleLogic(id)}
                className={`${logicStates[id] ? 'bg-gradient-to-r from-brand-primary to-brand-secondary' : 'bg-dark-800'}
                  relative inline-flex h-8 w-14 shrink-0 cursor-pointer rounded-full transition-colors duration-200 ease-in-out`}
              >
                <span className={`${logicStates[id] ? 'translate-x-7' : 'translate-x-1'}
                  pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out mt-1`} 
                />
              </Switch>
            </div>
            
            <div className="mt-8 pt-6 border-t border-glass-border">
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Status</span>
                <span className={`font-mono font-bold ${logicStates[id] ? 'text-status-profit' : 'text-text-muted'}`}>
                  {logicStates[id] ? 'RUNNING' : 'STOPPED'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
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

