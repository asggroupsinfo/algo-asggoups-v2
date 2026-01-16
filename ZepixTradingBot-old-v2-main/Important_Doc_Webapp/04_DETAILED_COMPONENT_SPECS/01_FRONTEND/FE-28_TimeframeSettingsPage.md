# FE-28: TIMEFRAME SETTINGS PAGE
**Component ID:** FE-28  
**Route:** `/settings/timeframes`  
**Purpose:** Multi-Timeframe Analysis Configuration (5 Commands Mapped)

---

## 1. 📋 Telegram Commands Covered
- `/set_tf_weights` (Weightage for 1m, 5m, 15m, 1h, 4h)
- `/set_confluence_threshold` (Min score 0-100)
- `/tf_mode` (Conservative/Aggressive)
- `/view_tf_config` (Current weights)
- `/reset_tf_config` (Default weights)

## 2. 🖼️ Page Layout

```
┌─────────────────────────────────────────────────────────┐
│ Timeframe Analysis Configuration                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  ANALYSIS MODE                                  │  │
│  │  [ Conservative ]  [ Balanced ]  [ Aggressive ] │  │
│  │  (Requires higher  (Default mix) (Lower thresh) │  │
│  │   confluence)                                   │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  TIMEFRAME WEIGHTS (Total must be 100%)         │  │
│  │                                                 │  │
│  │  1m:   [Slider] 10%                             │  │
│  │  5m:   [Slider] 20%                             │  │
│  │  15m:  [Slider] 30%                             │  │
│  │  1h:   [Slider] 25%                             │  │
│  │  4h:   [Slider] 15%                             │  │
│  │                                                 │  │
│  │  TOTAL: 100% ✅                                 │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  ENTRY THRESHOLD                                │  │
│  │  Minimum Confluence Score: [ 75 ] / 100         │  │
│  │  (Signal triggers only if weighted score > X)   │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [Save Configuration]    [Reset Defaults]             │
└─────────────────────────────────────────────────────────┘
```

## 3. 🧬 React Implementation

```tsx
import { useState, useEffect } from 'react';

const PRESETS = {
  conservative: { weights: { '1m': 5, '5m': 10, '15m': 30, '1h': 35, '4h': 20 }, threshold: 80 },
  balanced:     { weights: { '1m': 10, '5m': 20, '15m': 30, '1h': 25, '4h': 15 }, threshold: 70 },
  aggressive:   { weights: { '1m': 20, '5m': 30, '15m': 25, '1h': 15, '4h': 10 }, threshold: 60 }
};

export default function TimeframeSettingsPage() {
  const [mode, setMode] = useState('balanced');
  const [weights, setWeights] = useState(PRESETS.balanced.weights);
  const [threshold, setThreshold] = useState(PRESETS.balanced.threshold);

  // Calculate total whenever weights change
  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);
  const isValid = totalWeight === 100;

  const handleModeSelect = (m) => {
    setMode(m);
    setWeights(PRESETS[m].weights);
    setThreshold(PRESETS[m].threshold);
  };

  const updateWeight = (tf, val) => {
    setWeights(prev => ({ ...prev, [tf]: Number(val) }));
    setMode('custom'); // Switch to custom if manually edited
  };

  const handleSave = async () => {
    if (!isValid) return alert("Total weight must be exactly 100%");
    await fetch('/api/settings/timeframes', {
      method: 'PUT',
      body: JSON.stringify({ weights, threshold })
    });
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white mb-6">⏳ Timeframe Analysis</h1>

      {/* Mode Selection */}
      <div className="glass-panel p-4 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">Analysis Strategy</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.keys(PRESETS).map(m => (
            <button
              key={m}
              onClick={() => handleModeSelect(m)}
              className={`p-4 rounded-lg border text-left transition-all ${
                mode === m 
                  ? 'bg-brand-primary/20 border-brand-primary' 
                  : 'bg-dark-800 border-glass-border hover:bg-dark-700'
              }`}
            >
              <div className="font-bold text-white capitalize mb-1">{m}</div>
              <div className="text-xs text-text-secondary">
                {m === 'conservative' ? 'Higher timeframe bias, fewer signals' : 
                 m === 'aggressive' ? 'Lower timeframe bias, more signals' : 'Balanced approach'}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Weight Sliders */}
      <div className="glass-panel p-6 rounded-xl">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-white">Timeframe Weights</h3>
          <div className={`px-4 py-1 rounded-full text-sm font-bold ${
            isValid ? 'bg-status-profit/20 text-status-profit' : 'bg-status-loss/20 text-status-loss'
          }`}>
            Total: {totalWeight}%
          </div>
        </div>

        <div className="space-y-6">
          {['1m', '5m', '15m', '1h', '4h'].map(tf => (
            <div key={tf}>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-mono text-text-secondary">{tf.toUpperCase()}</span>
                <span className="text-sm font-bold text-white">{weights[tf]}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weights[tf]}
                onChange={(e) => updateWeight(tf, e.target.value)}
                className="w-full h-2 bg-dark-800 rounded-lg slider-thumb-brand"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Threshold */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">Signal Threshold</h3>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="50"
            max="95"
            step="5"
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            className="flex-1 h-2 bg-dark-800 rounded-lg slider-thumb-teal"
          />
          <div className="text-xl font-bold text-accent-teal w-16 text-right">
            {threshold}
          </div>
        </div>
        <p className="text-xs text-text-secondary mt-2">
          Only signals with a calculated confluence score above {threshold} will trigger trades.
        </p>
      </div>

      <button 
        onClick={handleSave} 
        disabled={!isValid}
        className={`btn w-full md:w-auto px-8 ${isValid ? 'btn-primary' : 'btn-disabled bg-dark-700 text-text-muted'}`}
      >
        Save Configuration
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

