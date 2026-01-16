# FE-22: RE-ENTRY SETTINGS PAGE
**Component ID:** FE-22  
**Route:** `/settings/reentry`  
**Purpose:** Complete Re-entry System Configuration (12 Telegram Commands Mapped)

---

## 1. 📋 Telegram Commands Covered
- `/tp_system` (on/off/status)
- `/sl_hunt` (on/off/status)
- `/exit_continuation` (on/off/status)
- `/set_monitor_interval` (30-600s)
- `/set_sl_offset` (1-5 pips)
- `/set_cooldown` (30-600s)
- `/set_recovery_time` (1-15 min)
- `/set_max_levels` (1-5)
- `/set_sl_reduction` (0.3-0.7)
- `/tp_report` (View Stats)
- `/reentry_config` (View All)
- `/reset_reentry_config` (Reset Defaults)

## 2. 🖼️ Page Layout

```
┌─────────────────────────────────────────────────────────┐
│ Re-entry System Configuration                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐  ┌─────────────────┐            │
│  │  TP SYSTEM      │  │  SL HUNT        │            │
│  │  [Toggle ON]    │  │  [Toggle OFF]   │            │
│  │  Status: Active │  │  Status: Off    │            │
│  └─────────────────┘  └─────────────────┘            │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  EXIT CONTINUATION                              │  │
│  │  [Toggle ON]                                    │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  TIMING CONTROLS                                │  │
│  │  • Monitor Interval:    [Slider] 60s           │  │
│  │  • Cooldown Period:     [Slider] 120s          │  │
│  │  • Recovery Window:     [Slider] 5 min         │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  CHAIN PARAMETERS                               │  │
│  │  • Max Chain Levels:    [▼ Dropdown] 3         │  │
│  │  • SL Offset (Pips):    [Slider] 2             │  │
│  │  • SL Reduction Factor: [Slider] 0.5 (50%)     │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [View TP Report]  [Reset to Defaults]                │
└─────────────────────────────────────────────────────────┘
```

## 3. 🧬 React Implementation

```tsx
import { useState } from 'react';
import { Switch } from '@headlessui/react';

export default function ReentrySettingsPage() {
  const [tpSystem, setTpSystem] = useState(true);
  const [slHunt, setSlHunt] = useState(false);
  const [exitContinuation, setExitContinuation] = useState(true);
  const [monitorInterval, setMonitorInterval] = useState(60);
  const [cooldown, setCooldown] = useState(120);
  const [recoveryTime, setRecoveryTime] = useState(5);
  const [maxLevels, setMaxLevels] = useState(3);
  const [slOffset, setSlOffset] = useState(2);
  const [slReduction, setSlReduction] = useState(0.5);

  const handleSave = async () => {
    const payload = {
      tp_system: tpSystem,
      sl_hunt: slHunt,
      exit_continuation: exitContinuation,
      monitor_interval: monitorInterval,
      cooldown: cooldown,
      recovery_time: recoveryTime * 60,
      max_levels: maxLevels,
      sl_offset: slOffset,
      sl_reduction: slReduction
    };
    await fetch('/api/settings/reentry', {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white mb-6">Re-entry System</h1>
      
      {/* Quick Toggles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ToggleCard title="TP System" enabled={tpSystem} onChange={setTpSystem} />
        <ToggleCard title="SL Hunt" enabled={slHunt} onChange={setSlHunt} />
        <ToggleCard title="Exit Continuation" enabled={exitContinuation} onChange={setExitContinuation} />
      </div>

      {/* Timing Controls */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">⏱️ Timing Controls</h3>
        <div className="space-y-4">
          <SliderControl 
            label="Monitor Interval" 
            value={monitorInterval} 
            onChange={setMonitorInterval}
            min={30} max={600} step={30} unit="s"
          />
          <SliderControl 
            label="Cooldown Period" 
            value={cooldown} 
            onChange={setCooldown}
            min={30} max={600} step={30} unit="s"
          />
          <SliderControl 
            label="Recovery Window" 
            value={recoveryTime} 
            onChange={setRecoveryTime}
            min={1} max={15} step={1} unit=" min"
          />
        </div>
      </div>

      {/* Chain Parameters */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">🔗 Chain Parameters</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-text-secondary mb-2">Max Chain Levels</label>
            <select 
              value={maxLevels} 
              onChange={(e) => setMaxLevels(Number(e.target.value))}
              className="w-full bg-dark-800 border border-glass-border rounded-lg px-4 py-2 text-white"
            >
              {[1,2,3,4,5].map(n => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>
          <SliderControl 
            label="SL Offset" 
            value={slOffset} 
            onChange={setSlOffset}
            min={1} max={5} step={1} unit=" pips"
          />
          <SliderControl 
            label="SL Reduction Factor" 
            value={slReduction} 
            onChange={setSlReduction}
            min={0.3} max={0.7} step={0.1} 
            formatter={(v) => `${(v*100).toFixed(0)}%`}
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-4">
        <button onClick={handleSave} className="btn btn-primary">
          💾 Save Changes
        </button>
        <button className="btn btn-outline">
          📊 View TP Report
        </button>
        <button className="btn btn-outline text-red-400 border-red-500">
          🔄 Reset to Defaults
        </button>
      </div>
    </div>
  );
}

// Helper Components
const ToggleCard = ({ title, enabled, onChange }) => (
  <div className="glass-panel p-4 rounded-xl">
    <div className="flex justify-between items-center">
      <h4 className="font-semibold text-white">{title}</h4>
      <Switch
        checked={enabled}
        onChange={onChange}
        className={`${enabled ? 'bg-gradient-to-r from-brand-primary to-brand-secondary' : 'bg-dark-800'} 
          relative inline-flex h-6 w-11 items-center rounded-full transition-colors`}
      >
        <span className={`${enabled ? 'translate-x-6' : 'translate-x-1'} 
          inline-block h-4 w-4 transform rounded-full bg-white transition-transform`} />
      </Switch>
    </div>
    <p className={`text-xs mt-2 ${enabled ? 'text-status-profit' : 'text-text-muted'}`}>
      {enabled ? 'Active' : 'Disabled'}
    </p>
  </div>
);

const SliderControl = ({ label, value, onChange, min, max, step, unit = '', formatter }) => (
  <div>
    <div className="flex justify-between mb-2">
      <label className="text-sm text-text-secondary">{label}</label>
      <span className="text-sm font-mono text-white">
        {formatter ? formatter(value) : `${value}${unit}`}
      </span>
    </div>
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      className="w-full h-2 bg-dark-800 rounded-lg appearance-none cursor-pointer slider-thumb-primary"
    />
  </div>
);
```

## 4. 🔌 API Integration
- **GET** `/api/settings/reentry` → Load current config
- **PUT** `/api/settings/reentry` → Save changes
- **GET** `/api/reentry/report` → TP Report stats
- **POST** `/api/settings/reentry/reset` → Reset defaults


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

