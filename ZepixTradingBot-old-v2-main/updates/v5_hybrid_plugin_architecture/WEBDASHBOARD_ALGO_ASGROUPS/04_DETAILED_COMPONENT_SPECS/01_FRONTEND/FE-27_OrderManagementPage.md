# FE-27: ORDER MANAGEMENT PAGE
**Component ID:** FE-27  
**Route:** `/settings/orders`  
**Purpose:** Trade Execution Limits & Grid Grid (7 Commands Mapped)

---

## 1. 📋 Telegram Commands Covered
- `/max_orders` (Total allowed trades)
- `/max_symbols` (Concurrent symbols)
- `/set_hedging` (Allow opposing trades)
- `/grid_mode` (Enable/Disable Grid)
- `/grid_config` (Step, Levels, Multiplier)
- `/order_timeout` (Expiration in seconds)
- `/force_exit_all` (Panic button)

## 2. 🖼️ Page Layout

```
┌─────────────────────────────────────────────────────────┐
│ Order & Execution Settings                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────┐  ┌─────────────────────┐    │
│  │  LIMITS             │  │  HEDGING            │    │
│  │  Max Trades: [ 5 ]  │  │  Allow Hedging:     │    │
│  │  Max Symbols:[ 3 ]  │  │  [Toggle OFF]       │    │
│  └─────────────────────┘  └─────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  GRID SYSTEM CONFIGURATION                      │  │
│  │  [Toggle OFF] Enable Grid/Martingale            │  │
│  │                                                 │  │
│  │  Grid Step (Pips):  [ 20 ]                      │  │
│  │  Max Levels:        [  5 ]                      │  │
│  │  Lot Multiplier:    [ 1.5] (x base lot)         │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  EXECUTION SAFETY                               │  │
│  │  Pending Order Timeout: [ 600 ] seconds         │  │
│  │  Slippage Tolerance:    [   3 ] pips            │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [ 🚨 PANIC: FORCE CLOSE ALL TRADES ]                 │
└─────────────────────────────────────────────────────────┘
```

## 3. 🧬 React Implementation

```tsx
import { useState } from 'react';
import { Switch } from '@headlessui/react';

export default function OrderManagementPage() {
  const [maxOrders, setMaxOrders] = useState(5);
  const [maxSymbols, setMaxSymbols] = useState(3);
  const [hedging, setHedging] = useState(false);
  const [gridEnabled, setGridEnabled] = useState(false);
  const [gridStep, setGridStep] = useState(20);
  const [gridLevels, setGridLevels] = useState(5);
  const [gridMult, setGridMult] = useState(1.5);
  const [timeout, setTimeout] = useState(600);
  const [slippage, setSlippage] = useState(3);

  const handlePanic = () => {
    if(confirm("⚠️ ARE YOU SURE? This will close ALL active positions/orders immediately!")) {
      fetch('/api/orders/panic', { method: 'POST' });
    }
  };

  const handleSave = async () => {
    await fetch('/api/settings/orders', {
      method: 'PUT',
      body: JSON.stringify({
        max_orders: maxOrders,
        max_symbols: maxSymbols,
        hedging,
        grid: {
          enabled: gridEnabled,
          step: gridStep,
          levels: gridLevels,
          multiplier: gridMult
        },
        timeout,
        slippage
      })
    });
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white mb-6">📦 Order Management</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Limits */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">⛔ Limits & Capacity</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-text-secondary mb-1">Max Concurrent Trades</label>
              <input type="number" value={maxOrders} onChange={(e) => setMaxOrders(e.target.value)} 
                className="input-field w-full" />
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">Max Unique Symbols</label>
              <input type="number" value={maxSymbols} onChange={(e) => setMaxSymbols(e.target.value)} 
                className="input-field w-full" />
            </div>
            <div className="flex items-center justify-between pt-2">
              <span className="text-white">Allow Hedging</span>
              <Switch checked={hedging} onChange={setHedging} 
                className={`${hedging ? 'bg-brand-primary' : 'bg-dark-800'} toggle-switch`} />
            </div>
          </div>
        </div>

        {/* Grid System */}
        <div className="glass-panel p-6 rounded-xl border-t-2 border-t-purple-500">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">🕸️ Grid / Martingale</h3>
            <Switch checked={gridEnabled} onChange={setGridEnabled} 
              className={`${gridEnabled ? 'bg-purple-600' : 'bg-dark-800'} toggle-switch`} />
          </div>
          <div className={`space-y-4 transition-opacity ${gridEnabled ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label-text">Grid Step (Pips)</label>
                <input type="number" value={gridStep} onChange={(e)=>setGridStep(e.target.value)} className="input-field" />
              </div>
              <div>
                <label className="label-text">Max Levels</label>
                <input type="number" value={gridLevels} onChange={(e)=>setGridLevels(e.target.value)} className="input-field" />
              </div>
            </div>
            <div>
              <label className="label-text">Lot Multiplier</label>
              <input type="number" step="0.1" value={gridMult} onChange={(e)=>setGridMult(e.target.value)} className="input-field" />
              <p className="text-xs text-text-muted mt-1">Example: 1.5 = 0.01 → 0.015 → 0.02</p>
            </div>
          </div>
        </div>
      </div>

      {/* Execution Safety */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">⚡ Execution Safety</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <RangeInput label="Pending Order Timeout (sec)" value={timeout} onChange={setTimeout} min={60} max={3600} step={60} />
          <RangeInput label="Slippage Tolerance (pips)" value={slippage} onChange={setSlippage} min={1} max={10} step={1} />
        </div>
      </div>

      {/* Danger Zone */}
      <div className="pt-6 border-t border-glass-border flex justify-between items-center">
        <button onClick={handleSave} className="btn btn-primary px-8">Save Settings</button>
        <button onClick={handlePanic} className="btn bg-status-loss hover:bg-red-700 text-white animate-pulse font-bold px-6">
          🚨 FORCE CLOSE ALL
        </button>
      </div>
    </div>
  );
}

const RangeInput = ({ label, value, onChange, min, max, step }) => (
  <div>
    <div className="flex justify-between mb-1">
      <span className="text-sm text-text-secondary">{label}</span>
      <span className="text-sm font-mono text-white">{value}</span>
    </div>
    <input type="range" min={min} max={max} step={step} value={value} onChange={(e)=>onChange(Number(e.target.value))} 
      className="w-full h-2 bg-dark-800 rounded-lg cursor-pointer" />
  </div>
);
```


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

