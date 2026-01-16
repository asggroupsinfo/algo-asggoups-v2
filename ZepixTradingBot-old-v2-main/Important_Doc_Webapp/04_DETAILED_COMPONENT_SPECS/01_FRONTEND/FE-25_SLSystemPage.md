# FE-25: SL SYSTEM PAGE
**Component ID:** FE-25  
**Route:** `/settings/sl-system`  
**Purpose:** Advanced Stop Loss & Trailing Configuration (8 Commands Mapped)

---

## 1. 📋 Telegram Commands Covered
- `/sl_system` (on/off/status)
- `/set_sl` (Base SL pips)
- `/set_trailing_sl` (Trailing Step pips)
- `/set_breakeven` (Breakeven Trigger pips)
- `/set_sl_buffer` (Buffer for volatile markets)
- `/trailing_mode` (Dynamic/Fixed)
- `/view_sl_stats` (Hit rate/slippage stats)
- `/reset_sl_config` (Reset to safe defaults)

## 2. 🖼️ Page Layout

```
┌─────────────────────────────────────────────────────────┐
│ Stop Loss Configuration                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  MASTER SWITCH                                  │  │
│  │  [Toggle ON] Stop Loss System Active            │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────┐  ┌─────────────────────┐    │
│  │  BASE SETTINGS      │  │  TRAILING LOGIC     │    │
│  │                     │  │                     │    │
│  │  Initial SL (Pips): │  │  Mode: [Dynamic ▼]  │    │
│  │  [Slider] 30        │  │                     │    │
│  │                     │  │  Trailing Step:     │    │
│  │  SL Buffer (Pips):  │  │  [Slider] 10 pips   │    │
│  │  [Slider] 5         │  │                     │    │
│  └─────────────────────┘  └─────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  BREAKEVEN SETTINGS                             │  │
│  │  [Toggle ON] Enable Auto-Breakeven              │  │
│  │                                                 │  │
│  │  Trigger at Profit (Pips): [Slider] 15          │  │
│  │  Offset (Lock Profit):     [Slider] 1 pip       │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  SL STATISTICS                                  │  │
│  │  • Avg Slippage: 0.2 pips                       │  │
│  │  • SL Hit Rate:  12% (Last 24h)                 │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [Save Config]    [Reset Defaults]                    │
└─────────────────────────────────────────────────────────┘
```

## 3. 🧬 React Implementation

```tsx
import { useState } from 'react';
import { Switch, RadioGroup } from '@headlessui/react';

export default function SLSystemPage() {
  const [slActive, setSlActive] = useState(true);
  const [baseSL, setBaseSL] = useState(30);
  const [slBuffer, setSlBuffer] = useState(5);
  const [trailingMode, setTrailingMode] = useState('dynamic');
  const [trailingStep, setTrailingStep] = useState(10);
  const [breakevenActive, setBreakevenActive] = useState(true);
  const [beTrigger, setBeTrigger] = useState(15);
  const [beOffset, setBeOffset] = useState(1);

  const handleSave = async () => {
    // API Call payload
    const config = {
      is_active: slActive,
      base_sl: baseSL,
      sl_buffer: slBuffer,
      trailing_mode: trailingMode,
      trailing_step: trailingStep,
      breakeven_enabled: breakevenActive,
      be_trigger: beTrigger,
      be_offset: beOffset
    };
    await fetch('/api/settings/sl', { method: 'PUT', body: JSON.stringify(config) });
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white mb-6">⚙️ SL System</h1>

      {/* Master Toggle */}
      <div className="glass-panel p-4 rounded-xl flex justify-between items-center border-l-4 border-l-brand-primary">
        <div>
          <h3 className="text-lg font-bold text-white">Master Switch</h3>
          <p className="text-sm text-text-secondary">Enable/Disable all Stop Loss logic</p>
        </div>
        <Switch
          checked={slActive}
          onChange={setSlActive}
          className={`${slActive ? 'bg-brand-primary' : 'bg-dark-800'} relative inline-flex h-8 w-14 items-center rounded-full transition-colors`}
        >
          <span className={`${slActive ? 'translate-x-7' : 'translate-x-1'} inline-block h-6 w-6 transform rounded-full bg-white transition-transform`} />
        </Switch>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Base Settings */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">🛡️ Base Parameters</h3>
          <div className="space-y-6">
            <SliderControl 
              label="Initial SL (Stop Loss)" 
              value={baseSL} 
              onChange={setBaseSL} 
              min={10} max={100} step={5} unit=" pips" 
            />
            <SliderControl 
              label="SL Buffer (Volatility)" 
              value={slBuffer} 
              onChange={setSlBuffer} 
              min={0} max={20} step={1} unit=" pips" 
            />
          </div>
        </div>

        {/* Trailing Logic */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">🎢 Trailing Logic</h3>
          <div className="mb-4">
            <label className="text-sm text-text-secondary mb-2 block">Trailing Mode</label>
            <div className="flex bg-dark-800 p-1 rounded-lg">
              {['dynamic', 'fixed'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setTrailingMode(mode)}
                  className={`flex-1 py-1 px-3 text-sm rounded ${
                    trailingMode === mode ? 'bg-brand-secondary text-white' : 'text-text-muted hover:text-white'
                  }`}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <SliderControl 
            label="Trailing Step" 
            value={trailingStep} 
            onChange={setTrailingStep} 
            min={5} max={50} step={5} unit=" pips" 
          />
        </div>
      </div>

      {/* Breakeven Settings */}
      <div className="glass-panel p-6 rounded-xl">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-white">⚖️ Auto-Breakeven</h3>
          <Switch
            checked={breakevenActive}
            onChange={setBreakevenActive}
            className={`${breakevenActive ? 'bg-accent-teal' : 'bg-dark-800'} relative inline-flex h-6 w-11 items-center rounded-full`}
          >
            <span className={`${breakevenActive ? 'translate-x-6' : 'translate-x-1'} inline-block h-4 w-4 transform rounded-full bg-white transition-transform`} />
          </Switch>
        </div>
        <div className={`space-y-6 transition-opacity ${breakevenActive ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
          <SliderControl 
            label="Trigger at Profit" 
            value={beTrigger} 
            onChange={setBeTrigger} 
            min={5} max={50} step={1} unit=" pips" 
          />
          <SliderControl 
            label="Lock Offset (Secure Profit)" 
            value={beOffset} 
            onChange={setBeOffset} 
            min={0} max={10} step={0.5} unit=" pips" 
          />
        </div>
      </div>

      {/* Save Actions */}
      <div className="flex justify-end gap-4 pt-4 border-t border-glass-border">
        <button className="btn btn-ghost text-red-400">Reset Defaults</button>
        <button onClick={handleSave} className="btn btn-primary px-8">Save Configuration</button>
      </div>
    </div>
  );
}

const SliderControl = ({ label, value, onChange, min, max, step, unit }) => (
  <div>
    <div className="flex justify-between mb-2">
      <span className="text-sm text-text-secondary">{label}</span>
      <span className="text-sm font-bold text-white">{value}{unit}</span>
    </div>
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      className="w-full h-2 bg-dark-800 rounded-lg appearance-none cursor-pointer slider-thumb-brand"
    />
  </div>
);
```


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

