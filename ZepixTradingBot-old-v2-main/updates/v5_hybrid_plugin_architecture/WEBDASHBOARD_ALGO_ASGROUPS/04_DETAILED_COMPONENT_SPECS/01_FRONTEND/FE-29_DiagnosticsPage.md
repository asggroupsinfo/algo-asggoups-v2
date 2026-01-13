# FE-29: DIAGNOSTICS PAGE
**Component ID:** FE-29  
**Route:** `/settings/diagnostics`  
**Purpose:** System Health, Logs & Debug Tools (8 Commands Mapped)

---

## 1. 📋 Telegram Commands Covered
- `/ping` (Latency check)
- `/system_health` (CPU/RAM/Disk stats)
- `/view_logs` (Last N lines)
- `/clear_logs` (Truncate logs)
- `/test_notification` (Verify Telegram/Webhook)
- `/db_stats` (Row counts, size)
- `/active_connections` (WS/DB/API)
- `/debug_mode` (Toggle verbose logging)

## 2. 🖼️ Page Layout

```
┌─────────────────────────────────────────────────────────┐
│ System Diagnostics                                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────┐  ┌──────────────────────┐     │
│  │  SYSTEM HEALTH       │  │  CONNECTIVITY        │     │
│  │  CPU: [|||  ] 24%    │  │  Telegram: ✅ OK     │     │
│  │  RAM: [|||||] 45%    │  │  Database: ✅ OK     │     │
│  │  Disk: 12GB Free     │  │  MT5 Bridge: ✅ OK   │     │
│  │  Uptime: 4d 12h      │  │  Websocket:  ✅ OK   │     │
│  └──────────────────────┘  └──────────────────────┘     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  DEBUG CONTROLS                                  │   │
│  │  [Toggle] Debug Mode (Verbose Logging)           │   │
│  │  [Test Notification] [Check Latency]             │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  LIVE LOGS (Tail -f)               [Clear Logs]  │   │
│  │  [INFO] 12:00:01 - Signal received XAUUSD        │   │
│  │  [INFO] 12:00:02 - Order entry validated         │   │
│  │  [WARN] 12:05:00 - High latency detected (150ms) │   │
│  │  ...                                             │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 3. 🧬 React Implementation

```tsx
import { useState, useEffect, useRef } from 'react';
import { Switch } from '@headlessui/react';

export default function DiagnosticsPage() {
  const [health, setHealth] = useState({ cpu: 0, ram: 0, disk: '', uptime: '' });
  const [connections, setConnections] = useState({ telegram: true, db: true, mt5: true, ws: true });
  const [logs, setLogs] = useState([]);
  const [debugMode, setDebugMode] = useState(false);
  const logEndRef = useRef(null);

  useEffect(() => {
    // Initial fetch
    fetchHealth();
    
    // WS subscription for live logs would go here
    const mockInterval = setInterval(() => {
      setLogs(prev => [...prev.slice(-99), `[INFO] ${new Date().toLocaleTimeString()} - Heartbeat check OK`]);
    }, 5000);

    return () => clearInterval(mockInterval);
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const fetchHealth = async () => {
    const res = await fetch('/api/diagnostics/health');
    const data = await res.json();
    setHealth(data.health);
    setConnections(data.connections);
    setDebugMode(data.debug_mode);
  };

  const toggleDebug = async (val) => {
    await fetch('/api/diagnostics/debug', {
      method: 'POST',
      body: JSON.stringify({ enabled: val })
    });
    setDebugMode(val);
  };

  const testNotify = async () => {
    const res = await fetch('/api/diagnostics/test-notification', { method: 'POST' });
    alert(await res.text());
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white mb-6">🩺 System Diagnostics</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* System Health */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">🖥️ Server Health</h3>
          <div className="space-y-4">
            <ProgressBar label="CPU Usage" value={health.cpu} color="bg-blue-500" />
            <ProgressBar label="RAM Usage" value={health.ram} color="bg-purple-500" />
            <div className="flex justify-between text-sm mt-2">
              <span className="text-text-secondary">Disk Free: <span className="text-white">{health.disk}</span></span>
              <span className="text-text-secondary">Uptime: <span className="text-white">{health.uptime}</span></span>
            </div>
          </div>
        </div>

        {/* Connections */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">🔗 Connectivity Status</h3>
          <div className="grid grid-cols-2 gap-4">
            <StatusBadge label="Telegram API" status={connections.telegram} />
            <StatusBadge label="Database" status={connections.db} />
            <StatusBadge label="MT5 Bridge" status={connections.mt5} />
            <StatusBadge label="WebSocket" status={connections.ws} />
          </div>
        </div>
      </div>

      {/* Debug Controls */}
      <div className="glass-panel p-4 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-white font-bold">Debug Mode</span>
          <Switch checked={debugMode} onChange={toggleDebug} className={`${debugMode ? 'bg-warning' : 'bg-dark-800'} toggle-switch`} />
        </div>
        <div className="flex gap-3">
          <button onClick={testNotify} className="btn btn-outline text-sm">🔔 Test Notification</button>
          <button className="btn btn-outline text-sm">⏱️ Check Latency</button>
        </div>
      </div>

      {/* Live Logs */}
      <div className="glass-panel p-0 rounded-xl overflow-hidden flex flex-col h-[400px]">
        <div className="bg-dark-800 p-3 border-b border-glass-border flex justify-between items-center">
          <h3 className="text-sm font-bold text-white">📜 System Logs (Live)</h3>
          <button onClick={() => setLogs([])} className="text-xs text-red-400 hover:text-red-300">Clear Output</button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-1 bg-black/50">
          {logs.map((log, i) => (
            <div key={i} className={log.includes('[ERROR]') ? 'text-status-loss' : log.includes('[WARN]') ? 'text-warning' : 'text-text-secondary'}>
              {log}
            </div>
          ))}
          <div ref={logEndRef} />
        </div>
      </div>
    </div>
  );
}

const ProgressBar = ({ label, value, color }) => (
  <div>
    <div className="flex justify-between mb-1">
      <span className="text-xs text-text-secondary">{label}</span>
      <span className="text-xs font-bold text-white">{value}%</span>
    </div>
    <div className="h-2 bg-dark-800 rounded-full overflow-hidden">
      <div className={`h-full ${color} transition-all duration-500`} style={{ width: `${value}%` }} />
    </div>
  </div>
);

const StatusBadge = ({ label, status }) => (
  <div className="flex items-center gap-2 p-2 rounded-lg bg-dark-800/50">
    <div className={`w-3 h-3 rounded-full ${status ? 'bg-status-profit shadow-glow-green' : 'bg-status-loss animate-pulse'}`} />
    <span className="text-sm text-white">{label}</span>
  </div>
);
```


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

