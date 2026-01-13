# FE-17: NOTIFICATION TOAST SYSTEM
**Component ID:** FE-17  
**Layer:** System UI  
**Lib:** `sonner` or `react-hot-toast`

---

## 1. 🖼️ Visual Design
Toasts should be sleek, stackable, and consistent with the dark theme.

- **Position:** Bottom-Right.
- **Background:** `bg-dark-900`.
- **Border:** `border-l-4` (Color coded by type).
- **Shadow:** `shadow-xl`.

## 2. 🎨 Variants

| Type | Icon | Border Color | Title Example |
| :--- | :--- | :--- | :--- |
| **Success** | `CheckCircle` (Green) | `border-emerald-500` | "Bot Started Successfully" |
| **Error** | `XCircle` (Red) | `border-red-500` | "Failed to Connect" |
| **Warning** | `AlertTriangle` (Amber) | `border-amber-500` | "High Latency Detected" |
| **Trade** | `TrendingUp` (Blue) | `border-primary-500` | "Long Entry: BTC/USDT" |

## 3. 🧩 Implementation (Sonner Wrapper)

```tsx
import { Toaster as Sonner, toast } from 'sonner';

export const Toaster = () => {
  return (
    <Sonner 
      theme="dark"
      className="toaster group"
      toastOptions={{
        classNames: {
          toast: 'group toast group-[.toaster]:bg-dark-900 group-[.toaster]:text-white group-[.toaster]:border-dark-700 group-[.toaster]:shadow-lg',
          description: 'group-[.toast]:text-gray-400',
          actionButton: 'group-[.toast]:bg-primary-500 group-[.toast]:text-white',
          cancelButton: 'group-[.toast]:bg-dark-800 group-[.toast]:text-gray-400',
        },
      }}
    />
  );
};

// Usage Utility
export const showTradeToast = (symbol, side, price) => {
  toast.custom((t) => (
    <div className="w-full p-4 rounded-xl bg-dark-900 border-l-4 border-primary-500 shadow-xl flex items-center gap-4">
      <div className="p-2 bg-primary-500/10 rounded-lg">
        <TrendingUp className="w-6 h-6 text-primary-500" />
      </div>
      <div>
        <h4 className="font-bold text-white">{side} {symbol}</h4>
        <p className="text-sm text-gray-400">Filled at ${price}</p>
      </div>
    </div>
  ));
};
```

## 4. ⚙️ Configuration
- **Duration:** 4000ms standard, 8000ms for errors.
- **Dismissible:** User can swipe or click 'X'.
- **Max Stack:** 3 visible at a time.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

