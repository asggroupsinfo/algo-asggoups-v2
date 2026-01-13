# FE-30: SESSION MANAGEMENT PAGE
**Component ID:** FE-30  
**Route:** `/settings/sessions`  
**Purpose:** Trading Session Hours & Auto-Pause (5 Commands Mapped)

---

## 1. 📋 Telegram Commands Covered
- `/session_config` (View current hours)
- `/set_session` (Define hours for London/NY/Asia)
- `/auto_pause` (Enable/Disable session logic)
- `/set_weekend_mode` (Block weekend trading)
- `/timezone_offset` (Server UTC offset)

## 2. 🖼️ Page Layout

```
┌─────────────────────────────────────────────────────────┐
│ Trading Sessions & Schedule                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  GLOBAL CONTROLS                                │  │
│  │  [Toggle ON] Enforce Session Times              │  │
│  │  [Toggle ON] Block Weekend Trading              │  │
│  │  Server Time Zone: [UTC +0]                     │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  SESSION SCHEDULE (24h Format)                  │  │
│  │  Current Time: 14:30 (Matches: London, NY)      │  │
│  │                                                 │  │
│  │  🌏 ASIAN SESSION                               │  │
│  │  Start: [ 00:00 ]   End: [ 08:00 ]   [Active]   │  │
│  │                                                 │  │
│  │  🌍 LONDON SESSION                              │  │
│  │  Start: [ 07:00 ]   End: [ 16:00 ]   [Active]   │  │
│  │                                                 │  │
│  │  🌎 NEW YORK SESSION                            │  │
│  │  Start: [ 13:00 ]   End: [ 22:00 ]   [Active]   │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [Save Schedule]    [Reset Standard Hours]            │
└─────────────────────────────────────────────────────────┘
```

## 3. 🧬 React Implementation

```tsx
import { useState, useEffect } from 'react';
import { Switch } from '@headlessui/react';

export default function SessionManagementPage() {
  const [sessionLogic, setSessionLogic] = useState(true);
  const [weekendBlock, setWeekendBlock] = useState(true);
  const [timezone, setTimezone] = useState(0);
  const [sessions, setSessions] = useState({
    asian: { start: '00:00', end: '08:00', active: true },
    london: { start: '07:00', end: '16:00', active: true },
    newyork: { start: '13:00', end: '22:00', active: true }
  });

  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    // Update server time simulation
    const timer = setInterval(() => {
      const now = new Date();
      now.setHours(now.getHours() + timezone);
      setCurrentTime(now.toTimeString().slice(0, 5));
    }, 1000);
    return () => clearInterval(timer);
  }, [timezone]);

  const updateSession = (key, field, val) => {
    setSessions(prev => ({
      ...prev,
      [key]: { ...prev[key], [field]: val }
    }));
  };

  const handleSave = async () => {
    await fetch('/api/settings/sessions', {
      method: 'PUT',
      body: JSON.stringify({
        enabled: sessionLogic,
        weekend_mode: weekendBlock,
        timezone,
        sessions
      })
    });
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white mb-6">📅 Trading Sessions</h1>

      {/* Global Controls */}
      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">🌍 Global Controls</h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-white font-medium">Enforce Session Logic</div>
              <div className="text-xs text-text-secondary">Only trade during active sessions below</div>
            </div>
            <Switch checked={sessionLogic} onChange={setSessionLogic} className={`${sessionLogic ? 'bg-brand-primary' : 'bg-dark-800'} toggle-switch`} />
          </div>

          <div className="flex justify-between items-center">
            <div>
              <div className="text-white font-medium">Block Weekends</div>
              <div className="text-xs text-text-secondary">Pause bot Sat 00:00 - Sun 23:59</div>
            </div>
            <Switch checked={weekendBlock} onChange={setWeekendBlock} className={`${weekendBlock ? 'bg-brand-primary' : 'bg-dark-800'} toggle-switch`} />
          </div>

          <div className="flex items-center gap-4 pt-2">
            <label className="text-text-secondary">Server Timezone Offset (UTC):</label>
            <select 
              value={timezone} 
              onChange={(e) => setTimezone(Number(e.target.value))}
              className="bg-dark-800 border border-glass-border rounded px-3 py-1 text-white"
            >
              {Array.from({length: 25}, (_, i) => i - 12).map(gym => (
                <option key={gym} value={gym}>UTC {gym >= 0 ? '+' : ''}{gym}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Session Schedule */}
      <div className={`glass-panel p-6 rounded-xl transition-opacity ${sessionLogic ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-white">🕒 Session Schedule</h3>
          <div className="px-3 py-1 bg-dark-900 rounded border border-glass-border font-mono text-brand-primary">
            Server Time: {currentTime}
          </div>
        </div>

        <div className="space-y-6">
          {Object.entries(sessions).map(([key, data]) => (
            <div key={key} className="flex items-center gap-4 bg-dark-800/30 p-4 rounded-lg border border-glass-border">
              <div className="w-12 h-12 rounded-full bg-dark-800 flex items-center justify-center text-xl">
                {key === 'asian' ? '🌏' : key === 'london' ? '🌍' : '🌎'}
              </div>
              <div className="flex-1">
                <div className="flex justify-between mb-2">
                  <h4 className="font-bold text-white capitalize">{key} Session</h4>
                  <Switch 
                    checked={data.active} 
                    onChange={(v) => updateSession(key, 'active', v)} 
                    className={`${data.active ? 'bg-accent-teal' : 'bg-dark-700'} relative inline-flex h-5 w-9 items-center rounded-full`} 
                  >
                    <span className={`${data.active ? 'translate-x-4' : 'translate-x-1'} inline-block h-3 w-3 transform rounded-full bg-white transition-transform`} />
                  </Switch>
                </div>
                <div className="flex gap-4">
                  <div className="flex-1">
                    <label className="text-xs text-text-secondary block mb-1">Start</label>
                    <input 
                      type="time" 
                      value={data.start} 
                      onChange={(e) => updateSession(key, 'start', e.target.value)}
                      className="w-full bg-dark-900 border border-glass-border rounded px-2 py-1 text-white text-sm"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="text-xs text-text-secondary block mb-1">End</label>
                    <input 
                      type="time" 
                      value={data.end} 
                      onChange={(e) => updateSession(key, 'end', e.target.value)}
                      className="w-full bg-dark-900 border border-glass-border rounded px-2 py-1 text-white text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end gap-4">
        <button className="btn btn-ghost">Reset Standard Hours</button>
        <button onClick={handleSave} className="btn btn-primary px-8">Save Schedule</button>
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

