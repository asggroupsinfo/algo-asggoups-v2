# FE-06: LIVE STATUS FEED
**Component ID:** FE-06  
**Layer:** Component (Widget)  
**Data Source:** WebSocket (`ws://api/live-logs`)

---

## 1. 🏗️ Layout & Behavior
A scrollable notification feed showing real-time system events, trade updates, and alerts.

- **Height:** Flexible or fixed height (`h-fit` or `max-h-400px`).
- **Scroll:** Auto-scrolls to top (newest first) or bottom depending on implementation.
- **Updates:** Real-time injection of new event cards.

## 2. 🎨 Visual Style
- **Container:** Glassmorphism card (`bg-glass`).
- **Items:** Distinct cards with icon, title, message, and timestamp.
- **Animation:** `fade-in` for new items.

### Notification Types
- **TP Hit:** `border-profit`, Green Icon.
- **New Entry:** `border-accent-teal`, Blue Icon.
- **Alert:** `border-warning`, Orange/Yellow Icon.
- **Analysis:** `border-gray-500`, Gray Icon.

## 3. 🧩 Functionality

### Auto-Scroll Logic
Must detect if user is actively scrolling up. If they are, pause auto-scroll. If they are at bottom, resume auto-scroll.

```tsx
const logsEndRef = useRef<HTMLDivElement>(null);

const scrollToBottom = () => {
  logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
};

// Example useEffect for auto-scrolling (placeholder, needs full implementation)
useEffect(() => {
  // Logic to check if auto-scroll is enabled and scroll to bottom
  // if (isAutoScrollEnabled) {
  //   scrollToBottom();
  // }
}, [/* logs, isAutoScrollEnabled */]);
```

### Component Structure
```tsx
export default function LiveStatusFeed({ logs }) {
  return (
    <div className="h-full bg-glass border border-glass-border rounded-2xl p-6 shadow-glass">
      
      {/* Header */}
      <div className="flex justify-between items-center mb-5">
        <h3 className="text-lg font-bold text-white">Live Notifications</h3>
        <div className="flex items-center gap-2">
           <div className="w-2 h-2 bg-profit rounded-full animate-pulse shadow-[0_0_10px_#00D1A7]" />
        </div>
      </div>

      {/* Feed Area */}
      <div className="flex-1 overflow-y-auto space-y-3 custom-scrollbar pr-2" style={{maxHeight: '400px'}}>
        {logs.map((log) => (
          <div key={log.id} className="flex gap-3 p-3 rounded-lg bg-black/20 border-l-4 border-accent-teal animate-fade-in hover:bg-black/30 transition-colors">
            {/* Icon */}
            <div className="mt-1 text-accent-teal">
                <i className={`fas ${getIcon(log.type)}`}></i>
            </div>
            
            {/* Content */}
            <div className="flex-1">
                <div className="font-semibold text-white text-sm">{log.title}</div>
                <div className="text-xs text-gray-400 mt-1">{log.message}</div>
                <div className="text-[10px] text-gray-500 mt-1">{log.timestamp}</div>
            </div>
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>

    </div>
  );
}
```

## 4. 🔗 Styling Props
- **Scrollbar:** Custom thin styling via CSS.
  ```css
  .custom-scrollbar::-webkit-scrollbar { width: 6px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
  ```


---

## IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

