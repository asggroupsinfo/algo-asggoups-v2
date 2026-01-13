# FE-32: AUTONOMOUS DASHBOARD
**Component ID:** FE-32  
**Route:** `/autonomous`  
**Purpose:** AI Logic Monitor & Autonomous Stats (Mapped to `/autonomous_dashboard` & `/fine_tune`)

---

## 1. 📋 Telegram Commands Covered
- `/autonomous_dashboard` (Main View)
- `/fine_tune` (Sub-menu access)
- `/profit_protection` (Sub-system status)
- `/sl_reduction` (Optimization status)
- `/recovery_windows` (Monitor status)
- `/autonomous_status` (Health check)

## 2. 🖼️ Page Layout

```
┌─────────────────────────────────────────────────────────┐
│ 🤖 AUTONOMOUS SYSTEM MONITOR                            │
│ Status: 🟢 RUNNING  |  Next Optimization: 14:00:00      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────┐  ┌──────────────────────┐     │
│  │  DAILY PERFORMANCE   │  │  ACTIVE MONITORS     │     │
│  │  Recoveries: [ 3/10 ]│  │  Trades Monitored: 5 │     │
│  │  Saved Value: +$450  │  │  Pending Actions:  2 │     │
│  │  Optimization: 98%   │  │  Window: ACTIVE      │     │
│  └──────────────────────┘  └──────────────────────┘     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SUB-SYSTEM HEALTH                               │   │
│  │                                                  │   │
│  │  🛡️ Profit Protection:  ✅ ACTIVE                │   │
│  │     (Trailing Profit Mode: Aggressive)           │   │
│  │                                                  │   │
│  │  ⚔️ SL Optimizer:       ✅ ACTIVE                │   │
│  │     (Reducing SL by 30% on weak trends)          │   │
│  │                                                  │   │
│  │  ⏳ Recovery Windows:   ✅ ACTIVE                │   │
│  │     (Scanning for re-entry zones)                │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  RECENT OPTIMIZATIONS                            │   │
│  │  [14:05] XAUUSD: Reduced SL (-10 pips)           │   │
│  │  [13:50] EURUSD: Profit Locked (+$25)            │   │
│  │  [13:10] GBPJPY: Recovery Attempt #1             │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  [Force Optimization Run]   [Disable Autonomous Mode]   │
└─────────────────────────────────────────────────────────┘
```

## 3. 🧬 React Implementation

```tsx
import { useState, useEffect } from 'react';

export default function AutonomousDashboard() {
  const [status, setStatus] = useState('RUNNING');
  const [stats, setStats] = useState({
    recoveries: 3,
    maxRecoveries: 10,
    savedValue: 450,
    monitors: 5
  });
  const [subSystems, setSubSystems] = useState({
    profitProtection: { active: true, mode: 'Aggressive' },
    slOptimizer: { active: true, desc: 'Reducing SL by 30%' },
    recoveryWindows: { active: true, status: 'Scanning' }
  });
  const [logs, setLogs] = useState([
    { time: '14:05', pair: 'XAUUSD', action: 'Reduced SL (-10 pips)' },
    { time: '13:50', pair: 'EURUSD', action: 'Profit Locked (+$25)' }
  ]);

  const toggleAutonomous = async () => {
    // API call to toggle
    setStatus(s => s === 'RUNNING' ? 'PAUSED' : 'RUNNING');
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          🤖 Autonomous System
          <span className={`text-sm px-3 py-1 rounded-full ${
            status === 'RUNNING' ? 'bg-status-profit/20 text-status-profit' : 'bg-status-loss/20 text-status-loss'
          }`}>
            {status}
          </span>
        </h1>
        <button onClick={toggleAutonomous} className="btn btn-outline text-sm">
          {status === 'RUNNING' ? '⏸️ Pause System' : '▶️ Resume System'}
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard label="Daily Recoveries" value={`${stats.recoveries}/${stats.maxRecoveries}`} icon="🔄" />
        <StatCard label="Value Saved" value={`+$${stats.savedValue}`} icon="💰" color="text-status-profit" />
        <StatCard label="Active Monitors" value={stats.monitors} icon="👁️" />
        <StatCard label="Efficiency" value="98%" icon="⚡" color="text-brand-primary" />
      </div>

      {/* Sub-Systems */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <SubSystemCard 
          title="Profit Protection" 
          icon="🛡️" 
          data={subSystems.profitProtection} 
        />
        <SubSystemCard 
          title="SL Optimizer" 
          icon="⚔️" 
          data={subSystems.slOptimizer} 
        />
        <SubSystemCard 
          title="Recovery Windows" 
          icon="⏳" 
          data={subSystems.recoveryWindows} 
        />
      </div>

      {/* Activity Log */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">📜 Recent AI Actions</h3>
        <div className="space-y-0">
          {logs.map((log, i) => (
            <div key={i} className="flex items-center p-3 border-b border-glass-border last:border-0 hover:bg-white/5 transition-colors">
              <span className="text-text-muted font-mono w-16">{log.time}</span>
              <span className="font-bold text-white w-20">{log.pair}</span>
              <span className="text-text-secondary flex-1">{log.action}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const StatCard = ({ label, value, icon, color = 'text-white' }) => (
  <div className="glass-panel p-4 rounded-xl flex items-center gap-4">
    <div className="text-2xl opacity-80">{icon}</div>
    <div>
      <div className="text-xs text-text-secondary uppercase tracking-wide">{label}</div>
      <div className={`text-xl font-bold ${color}`}>{value}</div>
    </div>
  </div>
);

const SubSystemCard = ({ title, icon, data }) => (
  <div className={`glass-panel p-5 rounded-xl border-t-2 ${data.active ? 'border-t-brand-primary' : 'border-t-gray-600'}`}>
    <div className="flex justify-between items-start mb-3">
      <div className="flex items-center gap-2">
        <span className="text-xl">{icon}</span>
        <h4 className="font-bold text-white">{title}</h4>
      </div>
      <div className={`w-3 h-3 rounded-full ${data.active ? 'bg-status-profit shadow-glow-green' : 'bg-gray-600'}`} />
    </div>
    <div className="text-sm text-text-secondary">
      {data.mode && <div>Mode: <span className="text-white">{data.mode}</span></div>}
      {data.desc && <div>{data.desc}</div>}
      {data.status && <div>Status: <span className="text-brand-accent">{data.status}</span></div>}
    </div>
  </div>
);
```


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

