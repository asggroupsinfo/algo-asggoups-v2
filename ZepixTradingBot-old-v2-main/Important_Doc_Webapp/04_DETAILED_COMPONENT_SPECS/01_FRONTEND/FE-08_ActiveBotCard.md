# FE-08: ACTIVE BOT CARD SPECIFICATION
**Component ID:** FE-08  
**Layer:** Component (Widget)  
**Reference:** abhibots.com "Active Tool" Card
# FE-08: ACTIVE BOT CARD SPECIFICATION
**Component ID:** FE-08  
**Layer:** Component (Widget)  
**Reference:** abhibots.com "Active Tool" Card

---

## 1. 🖼️ Visual Structure
The most prominent card on the Dashboard, summarizing the core bot state.

### Layout
```
┌────────────────────────────────────────────────────────┐
│  Active Bots                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Gold Scalper V3                  [Config] [Stop]│  │
│  │  XAUUSD • 15min                                  │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Euro Swing                       [Config] [Stop]│  │
│  │  EURUSD • 1H                                     │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

- **Container:** Glass Card.
- **List Item:** `bg-black/20`, rounded, Left border color indicates status (Green=Running).
- **Actions:** Small, outlined buttons.

## 2. 🧩 Features

### 2.1 Status Pill
- **Running:** Green pill with scaling pulse animation.
- **Stopped:** Gray/Red pill.
- **Error:** Red pill with alert icon.

### 2.2 Uptime Counter
- Shows format `XXd XXh XXm`.
- Logic: `CurrentTime - StartTime`.

### 2.3 Quick Actions (Top Right)
- **Stop Button:** Only visible if Running.
- **Restart Button:** Visible if Error/Stopped.
- Button Style: Small, Outline, `text-xs`.

## 3. 🧬 React Implementation

```tsx
interface Bot {
  name: string;
  pair: string;
  timeframe: string;
  status: 'running' | 'stopped' | 'error';
}

export default function ActiveBotCard({ bots }) {
  return (
    <div className="glass-card">
      <h3 className="mb-5 text-lg font-bold text-white">Active Bots</h3>
      <div className="flex flex-col gap-4">
        {bots.map((bot, idx) => (
          <div key={idx} className="flex justify-between items-center p-4 rounded-xl bg-black/20 border-l-4 border-profit">
            <div>
              <div className="font-semibold text-white">{bot.name}</div>
              <div className="text-xs text-secondary">{bot.pair} • {bot.timeframe}</div>
            </div>
            <div className="flex gap-2">
              <button className="px-3 py-1.5 text-xs font-semibold text-white bg-white/10 border border-white/20 rounded-md hover:bg-white/20 transition">
                Config
              </button>
              <button className="px-3 py-1.5 text-xs font-semibold text-loss bg-loss/20 border border-loss rounded-md hover:bg-loss/30 transition">
                Stop
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 4. 🔗 Styling Notes
- Use `relative` positioning to contain absolute background blur circles.
- `font-mono` for the Uptime counter gives a technical feel.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

