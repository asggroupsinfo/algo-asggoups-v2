# FE-31: SHIELD PROTECTION PAGE (Reverse Shield v3.0)
**Component ID:** FE-31  
**Route:** `/settings/shield`  
**Purpose:** Reverse Shield System v3.0 Configuration (Mapped to `/shield`)

---

## 1. 📋 Telegram Commands Covered
- `/shield` (Show status/menu)
- `/shield on` (Enable System)
- `/shield off` (Disable System)
- `/shield status` (Detailed Metrics)
- *Implicit:* Smart Risk Integration, Recovery Thresholds

## 2. 🖼️ Page Layout

```
┌─────────────────────────────────────────────────────────┐
│ 🛡️ REVERSE SHIELD SYSTEM v3.0                           │
│ Status: ✅ ACTIVE | Recovery Mode: 🟢 STANDBY           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  MASTER CONTROL                                 │  │
│  │  [Toggle ON] Enable Reverse Shield Protection   │  │
│  │  "Automatically hedges positions in drawdown"   │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  TRIGGER PARAMETERS                             │  │
│  │                                                 │  │
│  │  🛡️ Recovery Threshold: [Slider] 70%            │  │
│  │  (Trigger shield when trade hits 70% of SL)     │  │
│  │                                                 │  │
│  │  ⚔️ Lot Size Multiplier: [Slider] 0.5x           │  │
│  │  (Hedge trade size relative to original)        │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  ADVANCED LOGIC                                 │  │
│  │                                                 │  │
│  │  🧠 Smart Risk Adjustment: [Toggle ON]          │  │
│  │  (Auto-reduce risk on volatile pairs)           │  │
│  │                                                 │  │
│  │  🔄 Max Recovery Attempts: [Dropdown] 3         │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  ACTIVE SHIELDS (Live Monitoring)               │  │
│  │  • XAUUSD #1234: 🛡️ Shielded (+$12.50)          │  │
│  │  • EURUSD #5678: 🟢 Monitoring                  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [Save Shield Config]                                 │
└─────────────────────────────────────────────────────────┘
```

## 3. 🧬 React Implementation

```tsx
import { useState, useEffect } from 'react';
import { Switch } from '@headlessui/react';

export default function ShieldProtectionPage() {
  const [enabled, setEnabled] = useState(false);
  const [threshold, setThreshold] = useState(0.7);
  const [multiplier, setMultiplier] = useState(0.5);
  const [smartRisk, setSmartRisk] = useState(true);
  const [maxAttempts, setMaxAttempts] = useState(3);
  const [activeShields, setActiveShields] = useState([]);

  useEffect(() => {
    // Mock Fetch
    setActiveShields([
      { id: 1234, symbol: 'XAUUSD', status: 'SHIELDED', profit: 12.50 },
      { id: 5678, symbol: 'EURUSD', status: 'MONITORING', profit: 0 }
    ]);
  }, []);

  const handleSave = async () => {
    await fetch('/api/settings/shield', {
      method: 'PUT',
      body: JSON.stringify({
        enabled,
        recovery_threshold: threshold,
        lot_multiplier: multiplier,
        smart_risk: smartRisk,
        max_attempts: maxAttempts
      })
    });
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🛡️</span>
        <h1 className="text-2xl font-bold text-white bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
          Reverse Shield v3.0
        </h1>
      </div>

      {/* Master Switch */}
      <div className={`glass-panel p-6 rounded-xl border-l-4 ${enabled ? 'border-status-profit' : 'border-text-muted'}`}>
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-xl font-bold text-white">System Status</h3>
            <p className="text-sm text-text-secondary">
              {enabled ? 'Active - Protecting open positions' : 'Disabled - Standard SL only'}
            </p>
          </div>
          <Switch
            checked={enabled}
            onChange={setEnabled}
            className={`${enabled ? 'bg-status-profit' : 'bg-dark-800'} relative inline-flex h-8 w-14 items-center rounded-full transition-colors`}
          >
            <span className={`${enabled ? 'translate-x-7' : 'translate-x-1'} inline-block h-6 w-6 transform rounded-full bg-white transition-transform`} />
          </Switch>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Trigger Parameters */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">🎯 Trigger Parameters</h3>
          <div className="space-y-6">
            <div>
              <div className="flex justify-between mb-2">
                <label className="text-sm text-text-secondary">Recovery Threshold (% of SL)</label>
                <span className="text-white font-mono font-bold">{(threshold * 100).toFixed(0)}%</span>
              </div>
              <input 
                type="range" min="0.5" max="0.95" step="0.05"
                value={threshold} onChange={(e) => setThreshold(Number(e.target.value))}
                className="w-full h-2 bg-dark-800 rounded-lg slider-thumb-brand"
              />
              <p className="text-xs text-text-muted mt-1">Triggers when trade hits {(threshold * 100)}% of Stop Loss distance.</p>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <label className="text-sm text-text-secondary">Hedge Lot Multiplier</label>
                <span className="text-white font-mono font-bold">{multiplier}x</span>
              </div>
              <input 
                type="range" min="0.1" max="2.0" step="0.1"
                value={multiplier} onChange={(e) => setMultiplier(Number(e.target.value))}
                className="w-full h-2 bg-dark-800 rounded-lg slider-thumb-brand"
              />
            </div>
          </div>
        </div>

        {/* Advanced Logic */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">🧠 Intelligence</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-dark-800/50 rounded-lg">
              <div>
                <div className="text-white font-medium">Smart Risk</div>
                <div className="text-xs text-text-secondary">Auto-adjust usage based on volatility</div>
              </div>
              <Switch checked={smartRisk} onChange={setSmartRisk} className={`${smartRisk ? 'bg-brand-secondary' : 'bg-dark-700'} toggle-switch`} />
            </div>

            <div>
              <label className="text-sm text-text-secondary block mb-2">Max Recovery Attempts</label>
              <select 
                value={maxAttempts} 
                onChange={(e) => setMaxAttempts(Number(e.target.value))}
                className="w-full bg-dark-800 border border-glass-border rounded px-3 py-2 text-white"
              >
                {[1, 2, 3, 4, 5].map(n => <option key={n} value={n}>{n} Attempts</option>)}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Active Shields */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">📡 Live Monitoring</h3>
        {activeShields.length === 0 ? (
          <div className="text-text-muted text-center py-4">No active trades under monitoring</div>
        ) : (
          <div className="space-y-2">
            {activeShields.map(shield => (
              <div key={shield.id} className="flex justify-between items-center p-3 bg-dark-800/30 rounded-lg border border-glass-border">
                <div className="font-mono text-white">{shield.symbol} <span className="text-text-secondary text-xs">#{shield.id}</span></div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-1 rounded ${shield.status === 'SHIELDED' ? 'bg-brand-primary/20 text-brand-primary' : 'bg-dark-700 text-text-secondary'}`}>
                    {shield.status}
                  </span>
                  {shield.profit !== 0 && (
                    <span className="text-status-profit font-bold text-sm">+${shield.profit}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <button onClick={handleSave} className="btn btn-primary w-full md:w-auto px-8">
        Save Shield Configuration
      </button>
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

