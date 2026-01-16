# FE-12: INPUT FORMS SPECIFICATION
**Component ID:** FE-12  
**Layer:** Component (Form)  
**Lib:** React Hook Form + Zod Validation

---

## 1. 🖼️ Visual Style
Inputs designed to look integrated into the dark theme, "sinking" into the card.

- **Background:** `bg-dark-950` (Darker than the card `bg-dark-900`).
- **Border:** `border-dark-700`.
- **Focus:** `ring-2 ring-primary-500/50 border-primary-500`.
- **Text:** White.
- **Placeholder:** `text-dark-500`.

## 2. 🧩 Form Group Structure
Standard vertical layout for configuration forms.

```
Label [?] Tooltip
[ INPUT FIELD ______________ ]
Error Message (Red text)
```

## 3. 🧬 React Implementation

### Text Input
```tsx
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, ...props }, ref) => (
    <div className="space-y-1.5">
      {label && <label className="text-sm font-medium text-gray-400">{label}</label>}
      <input
        ref={ref}
        className={`
          w-full px-4 py-2.5 rounded-lg bg-dark-950 border 
          text-white placeholder-gray-600 focus:outline-none focus:ring-2 transition-all
          ${error 
            ? 'border-red-500/50 focus:ring-red-500/20' 
            : 'border-dark-700 focus:border-primary-500 focus:ring-primary-500/20'}
        `}
        {...props}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  )
);
```

### Toggle Switch
Used for booleans (e.g., "Enable Trailing Stop").

```tsx
export function Toggle({ label, checked, onChange }) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-dark-800 border border-dark-700">
      <span className="text-sm font-medium text-gray-300">{label}</span>
      <button
        onClick={() => onChange(!checked)}
        className={`relative w-11 h-6 rounded-full transition-colors ${checked ? 'bg-primary-600' : 'bg-dark-600'}`}
      >
        <span className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${checked ? 'translate-x-5' : 'translate-x-0'}`} />
      </button>
    </div>
  );
}
```

## 4. 🛡️ Validation Rules (Zod Schema)
- **API Keys:** Regex check for alphanumeric + length.
- **Percentages:** Min 0, Max 100.
- **Amounts:** Must be positive numbers.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

