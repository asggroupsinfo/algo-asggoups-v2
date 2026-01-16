# FE-23: TREND CONTROL PAGE  
**Component ID:** FE-23  
**Route:** `/settings/trends`  
**Purpose:** Manual Trend Override System (5 Commands Mapped)

---

## 1. 📋 Telegram Commands Covered
- `/show_trends` → Display grid
- `/trend_matrix` → Full matrix view
- `/set_trend` → Dropdown cell edit
- `/set_auto` → Batch auto-enable
- `/trend_mode` → Mode indicator (MANUAL/AUTO)

## 2. 🖼️ Visual Design: Interactive Matrix

```
┌──────────────────────────────────────────────────────────┐
│ Trend Control Matrix                      [🔄 Set All Auto] │
├──────────────────────────────────────────────────────────┤
│ Symbol    │  1m     │  5m     │  15m    │  1h     │  4h     │
├───────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ XAUUSD    │ 🟢 BULL │ 🟡 AUTO │ 🔴 BEAR │ 🟡 AUTO │ 🟡 AUTO │
│           │ MANUAL  │  AUTO   │ MANUAL  │  AUTO   │  AUTO   │
├───────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ EURUSD    │ 🟡 AUTO │ 🟡 AUTO │ 🟡 AUTO │ 🟡 AUTO │ 🟡 AUTO │
├───────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ GBPUSD    │ 🟡 AUTO │ 🟡 AUTO │ 🟡 AUTO │ 🟡 AUTO │ 🟡 AUTO │
└──────────────────────────────────────────────────────────┘

Click any cell to change:
[AUTO] [BULLISH] [BEARISH] [NEUTRAL]
```

## 3. 🧬 React Implementation

```tsx
import { useState, useEffect } from 'react';

const SYMBOLS = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD'];
const TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d'];
const TRENDS = ['AUTO', 'BULLISH', 'BEARISH', 'NEUTRAL'];

export default function TrendControlPage() {
  const [trendMatrix, setTrendMatrix] = useState({});

  useEffect(() => {
    fetchTrends();
  }, []);

  const fetchTrends = async () => {
    const res = await fetch('/api/settings/trend');
    const data = await res.json();
    setTrendMatrix(data);
  };

  const updateCell = async (symbol, tf, newTrend) => {
    await fetch('/api/settings/trend', {
      method: 'PUT',
      body: JSON.stringify({ symbol, timeframe: tf, trend: newTrend })
    });
    fetchTrends();
  };

  const setAllAuto = async () => {
    await fetch('/api/settings/trend/auto-all', { method: 'POST' });
    fetchTrends();
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-white">Trend Control Matrix</h1>
        <button onClick={setAllAuto} className="btn btn-outline">
          🔄 Set All Auto
        </button>
      </div>

      <div className="glass-panel rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-dark-800/50 border-b border-glass-border">
              <tr>
                <th className="px-6 py-3 text-xs font-semibold text-text-secondary uppercase">Symbol</th>
                {TIMEFRAMES.map(tf => (
                  <th key={tf} className="px-6 py-3 text-xs font-semibold text-text-secondary uppercase text-center">
                    {tf}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-700/50">
              {SYMBOLS.map(symbol => (
                <tr key={symbol} className="hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4 font-mono font-bold text-white">{symbol}</td>
                  {TIMEFRAMES.map(tf => {
                    const cell = trendMatrix[`${symbol}_${tf}`] || { trend: 'AUTO', mode: 'AUTO' };
                    return (
                      <td key={tf} className="px-6 py-4">
                        <TrendCell 
                          trend={cell.trend} 
                          mode={cell.mode}
                          onChange={(newTrend) => updateCell(symbol, tf, newTrend)}
                        />
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

const TrendCell = ({ trend, mode, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const getTrendColor = (t) => {
    if (t === 'BULLISH') return 'text-status-profit border-status-profit';
    if (t === 'BEARISH') return 'text-status-loss border-status-loss';
    if (t === 'AUTO') return 'text-accent-teal border-accent-teal';
    return 'text-text-muted border-text-muted';
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full px-3 py-2 rounded-lg border ${getTrendColor(trend)} 
          bg-dark-800/30 hover:bg-dark-800/50 transition-all text-center text-sm font-semibold`}
      >
        <div>{trend === 'BULLISH' ? '🟢' : trend === 'BEARISH' ? '🔴' : '🟡'} {trend}</div>
        <div className="text-xs opacity-70 mt-1">{mode}</div>
      </button>

      {isOpen && (
        <div className="absolute z-10 mt-2 w-full bg-dark-900 border border-glass-border rounded-lg shadow-xl p-2 space-y-1">
          {TRENDS.map(t => (
            <button
              key={t}
              onClick={() => { onChange(t); setIsOpen(false); }}
              className="w-full px-3 py-2 text-sm text-white hover:bg-brand-primary/20 rounded transition-colors text-left"
            >
              {t}
            </button>
          ))}
        </div>
      )}
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

