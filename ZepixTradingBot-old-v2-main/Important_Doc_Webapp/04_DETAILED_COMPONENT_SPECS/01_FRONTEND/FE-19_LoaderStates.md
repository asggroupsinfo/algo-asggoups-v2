# FE-19: LOADER STATES SPECIFICATION
**Component ID:** FE-19  
**Layer:** System UI  
**Use Case:** Initial Load, Data Fetching, Action Processing

---

## 1. 💀 Skeleton Loading (Data Fetching)
Instead of a generic spinner, replicate the component layout with pulsing gray blocks.

### Component Map
- **Stats Card:** Square block + Text line.
- **Table:** 5 rows of gray lines.
- **Chart:** Large rectangular block.

### Implementation (Tailwind)
```tsx
const Skeleton = ({ className }) => (
  <div className={`animate-pulse bg-dark-800 rounded-lg ${className}`} />
);

// usage
<Skeleton className="h-32 w-full" /> // For Card
<Skeleton className="h-8 w-3/4" />   // For Text
```

## 2. 🌀 Spinner (Action Processing)
Used inside buttons or overlays when submitting forms.

### Design
- **Icon:** `Loader2` from Lucide.
- **Animation:** `animate-spin` (Tailwind).
- **Color:** `text-primary-500` or `text-white` (if on colored button).

## 3. 📟 Full Screen Loader (Initial App Load)
Used when Next.js is hydrating or verifying session.

### Layout
- **Background:** `bg-dark-950`.
- **Center:** Logo Icon + "Initializing..." text.
- **Effect:** Logo pulses opacity.

```tsx
export default function SplashLoader() {
  return (
    <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-dark-950">
      <img src="/logo.svg" className="w-16 h-16 animate-pulse" />
      <span className="mt-4 text-sm font-medium text-gray-500 tracking-widest uppercase">
        Algo.AsGroups
      </span>
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

