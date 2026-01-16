# FE-26: PROFIT MANAGEMENT PAGE
**Component ID:** FE-26  
**Route:** `/settings/profit`  
**Purpose:** Take Profit Targets & Partial Close (6 Commands Mapped)

---

## 1. 📋 Telegram Commands Covered
- `/set_tp` (TP1, TP2, TP3 pips)
- `/set_partial_close` (% to close at TP1/TP2)
- `/tp_mode` (Fixed Pips / ATR Based / Risk Multiplier)
- `/view_tp_config` (Current levels)
- `/set_min_profit` (Minimum $ to book)
- `/profit_stats` (Avg Profit per trade)

## 2. 🖼️ Page Layout

```
┌─────────────────────────────────────────────────────────┐
│ Profit Management                                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  CALCULATION MODE                               │  │
│  │  [ Fixed Pips ]  [ ATR Based ]  [ Risk Ratio ]  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────┐  ┌───────┐  ┌───────┐                    │
│  │  TP 1 │  │  TP 2 │  │  TP 3 │                    │
│  │       │  │       │  │       │                    │
│  │ Pips: │  │ Pips: │  │ Pips: │                    │
│  │ [ 20 ]│  │ [ 50 ]│  │ [100 ]│                    │
│  │       │  │       │  │       │                    │
│  │ Close:│  │ Close:│  │ Close:│                    │
│  │ [ 50%]│  │ [ 30%]│  │ [100%]│ <- (Remainder)     │
│  └───────┘  └───────┘  └───────┘                    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  SAFETY SETTINGS                                │  │
│  │  • Minimum Profit ($): [Input] $5.00            │  │
│  │  • Force Close at EOD: [Toggle] OFF             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [Apply Changes]                                      │
└─────────────────────────────────────────────────────────┘
```

## 3. 🧬 React Implementation

```tsx
import { useState } from 'react';

export default function ProfitManagementPage() {
  const [mode, setMode] = useState('fixed'); // fixed, atr, risk
  const [targets, setTargets] = useState({
    tp1: { value: 20, closePct: 50 },
    tp2: { value: 50, closePct: 30 },
    tp3: { value: 100, closePct: 100 } // tp3 closes remaining
  });
  const [minProfit, setMinProfit] = useState(5);

  const getLabel = () => {
    if (mode === 'fixed') return 'Pips';
    if (mode === 'atr') return 'ATR x';
    if (mode === 'risk') return 'R:R';
  };

  const handleTargetChange = (level, field, val) => {
    setTargets(prev => ({
      ...prev,
      [level]: { ...prev[level], [field]: Number(val) }
    }));
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white mb-6">💰 Profit Management</h1>

      {/* Mode Selection */}
      <div className="glass-panel p-2 rounded-xl inline-flex bg-dark-800">
        {['fixed', 'atr', 'risk'].map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${
              mode === m 
                ? 'bg-status-profit text-dark-900 shadow-glow-green' 
                : 'text-text-secondary hover:text-white'
            }`}
          >
            {m === 'fixed' ? 'Fixed Pips' : m === 'atr' ? 'ATR Dynamic' : 'Risk Ratio'}
          </button>
        ))}
      </div>

      {/* Target Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {['tp1', 'tp2', 'tp3'].map((level, idx) => (
          <div key={level} className="glass-panel p-6 rounded-xl border-t-4 border-t-status-profit">
            <h3 className="text-xl font-bold text-white mb-4">Target {idx + 1}</h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-xs text-text-secondary uppercase font-bold">{getLabel()}</label>
                <input
                  type="number"
                  value={targets[level].value}
                  onChange={(e) => handleTargetChange(level, 'value', e.target.value)}
                  className="w-full mt-1 bg-dark-800 border border-glass-border rounded p-2 text-white font-mono text-lg focus:border-status-profit outline-none"
                />
              </div>

              <div>
                <label className="text-xs text-text-secondary uppercase font-bold">Close % (Partial)</label>
                <div className="relative pt-1">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={targets[level].closePct}
                    disabled={level === 'tp3'} // TP3 always closes remainder logically or explicitly
                    onChange={(e) => handleTargetChange(level, 'closePct', e.target.value)}
                    className="w-full h-2 bg-dark-800 rounded-lg appearance-none cursor-pointer slider-thumb-green"
                  />
                  <div className="text-right text-status-profit font-bold mt-1">
                    {level === 'tp3' ? 'Remainder' : `${targets[level].closePct}%`}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Safety Settings */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">🛡️ Safety Guards</h3>
        <div className="flex items-center gap-4">
          <label className="text-text-secondary">Minimum Net Profit ($):</label>
          <div className="relative">
            <span className="absolute left-3 top-2 text-text-muted">$</span>
            <input 
              type="number" 
              value={minProfit} 
              onChange={(e) => setMinProfit(e.target.value)}
              className="pl-6 pr-4 py-2 bg-dark-800 border border-glass-border rounded text-white w-32"
            />
          </div>
        </div>
      </div>

      <button className="btn btn-primary w-full md:w-auto px-8">Apply Profit Settings</button>
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

