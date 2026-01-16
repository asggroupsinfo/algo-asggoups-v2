# FE-24: RISK MANAGEMENT PAGE
**Component ID:** FE-24  
**Route:** `/settings/risk`  
**Purpose:** Risk Tiers & Loss Caps (11 Commands Mapped)

---

## 1. 📋 Telegram Commands Covered
- `/view_risk_caps` → Display tiers
- `/view_risk_status` → Active tier + current loss
- `/switch_tier` → Quick tier switch (5k, 10k, 25k, 50k, 100k)
- `/set_daily_cap` → Daily $ limit
- `/set_lifetime_cap` → Lifetime $ limit
- `/set_risk_tier` → Custom tier config
- `/set_lot_size` → Tier-specific lot override
- `/lot_size_status` → Show all tier lots
- `/clear_daily_loss` → Reset daily counter
- `/clear_loss_data` → Reset lifetime
- `/reset_risk_settings` → Factory defaults

## 2. 🖼️ Visual: Tier Cards

```
┌─────────────────────────────────────────────────────────┐
│ Risk Management                                         │
│ Current Loss:  Daily: -$45 / $100  |  Lifetime: -$350 / $500 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ $5,000 ✅│  │ $10,000  │  │ $25,000  │             │
│  │──────────│  │──────────│  │──────────│             │
│  │ Daily:   │  │ Daily:   │  │ Daily:   │             │
│  │ $100     │  │ $200     │  │ $500     │             │
│  │ Lifetime:│  │ Lifetime:│  │ Lifetime:│             │
│  │ $500     │  │ $1,000   │  │ $2,500   │             │
│  │ Lot: 0.01│  │ Lot: 0.05│  │ Lot: 0.1 │             │
│  │          │  │          │  │          │             │
│  │ [ACTIVE] │  │[Activate]│  │[Activate]│             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                         │
│  ┌──────────┐  ┌──────────┐                           │
│  │ $50,000  │  │ $100,000 │                           │
│  │──────────│  │──────────│                           │
│  │ Daily:   │  │ Daily:   │                           │
│  │ $1,000   │  │ $2,000   │                           │
│  │ Lifetime:│  │ Lifetime:│                           │
│  │ $5,000   │  │ $10,000  │                           │
│  │ Lot: 0.2 │  │ Lot: 0.5 │                           │
│  │          │  │          │                           │
│  │[Activate]│  │[Activate]│                           │
│  └──────────┘  └──────────┘                           │
│                                                         │
│  [✏️ Edit Tier]  [🗑️ Clear Daily]  [🔄 Reset All]     │
└─────────────────────────────────────────────────────────┘
```

## 3. 🧬 React Implementation

```tsx
import { useState } from 'react';

const DEFAULT_TIERS = {
  5000: { daily: 100, lifetime: 500, lot: 0.01 },
  10000: { daily: 200, lifetime: 1000, lot: 0.05 },
  25000: { daily: 500, lifetime: 2500, lot: 0.1 },
  50000: { daily: 1000, lifetime: 5000, lot: 0.2 },
  100000: { daily: 2000, lifetime: 10000, lot: 0.5 },
};

export default function RiskManagementPage() {
  const [activeTier, setActiveTier] = useState(5000);
  const [tiers, setTiers] = useState(DEFAULT_TIERS);
  const [currentLoss, setCurrentLoss] = useState({ daily: 45, lifetime: 350 });

  const switchTier = async (tierBalance) => {
    await fetch('/api/settings/risk/switch', {
      method: 'POST',
      body: JSON.stringify({ tier: tierBalance })
    });
    setActiveTier(tierBalance);
  };

  const clearDaily = async () => {
    await fetch('/api/settings/risk/clear-daily', { method: 'POST' });
    setCurrentLoss(prev => ({ ...prev, daily: 0 }));
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white">Risk Management</h1>

      {/* Current Status */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">📊 Current Loss Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <LossProgressBar 
            label="Daily Loss"
            current={currentLoss.daily}
            max={tiers[activeTier].daily}
          />
          <LossProgressBar 
            label="Lifetime Loss"
            current={currentLoss.lifetime}
            max={tiers[activeTier].lifetime}
          />
        </div>
      </div>

      {/* Tier Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {Object.keys(DEFAULT_TIERS).map(balance => {
          const tier = tiers[balance];
          const isActive = Number(balance) === activeTier;
          
          return (
            <div key={balance} className={`glass-panel p-4 rounded-xl relative overflow-hidden
              ${isActive ? 'border-2 border-brand-primary' : 'border border-glass-border'}`}>
              {isActive && (
                <div className="absolute top-2 right-2 bg-status-profit text-white text-xs px-2 py-1 rounded-full font-bold">
                  ✅ ACTIVE
                </div>
              )}
              
              <div className="mb-4">
                <h3 className="text-xl font-bold text-white">${(Number(balance) / 1000).toFixed(0)}k</h3>
                <p className="text-xs text-text-secondary">Balance Tier</p>
              </div>

              <div className="space-y-2 text-sm mb-4">
                <div className="flex justify-between">
                  <span className="text-text-secondary">Daily Cap:</span>
                  <span className="text-white font-mono">${tier.daily}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Lifetime Cap:</span>
                  <span className="text-white font-mono">${tier.lifetime}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Lot Size:</span>
                  <span className="text-white font-mono">{tier.lot.toFixed(2)}</span>
                </div>
              </div>

              {!isActive && (
                <button 
                  onClick={() => switchTier(balance)}
                  className="w-full btn btn-outline text-sm py-2"
                >
                  Activate
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Actions */}
      <div className="flex gap-3 flex-wrap">
        <button className="btn btn-outline">
          ✏️ Edit Active Tier
        </button>
        <button onClick={clearDaily} className="btn btn-outline">
          🗑️ Clear Daily Loss
        </button>
        <button className="btn btn-outline text-red-400 border-red-500">
          🔄 Reset All Tiers
        </button>
      </div>
    </div>
  );
}

const LossProgressBar = ({ label, current, max }) => {
  const percentage = (current / max) * 100;
  const color = percentage > 80 ? 'bg-status-loss' : percentage > 50 ? 'bg-warning' : 'bg-status-profit';
  
  return (
    <div>
      <div className="flex justify-between mb-2">
        <span className="text-sm text-text-secondary">{label}</span>
        <span className="text-sm font-mono text-white">${current} / ${max}</span>
      </div>
      <div className="h-3 bg-dark-800 rounded-full overflow-hidden">
        <div className={`h-full ${color} transition-all duration-300`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
};
```


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

