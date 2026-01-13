# FE-11: ACTION BUTTONS SPECIFICATION
**Component ID:** FE-11  
**Layer:** Component (Atom)  
**Style:** Gradient / Glass / Outline

---

## 1. 🎨 Button Variants

### Primary (Gradient)
Used for main actions like "Save Config" or "Connect".
- **Background:** `bg-gradient-to-r from-primary-600 to-secondary-600`.
- **Hover:** Brightness up, `shadow-lg shadow-primary-500/20`.
- **Text:** White, Bold.

### Danger (Action)
Used for critical actions like "Stop Bot" or "Emergency Exit".
- **Background:** `bg-red-500/10`.
- **Border:** `border border-red-500/50`.
- **Text:** `text-red-400`.
- **Hover:** `bg-red-500 text-white`.

### Ghost (Icon Only)
Used for toolbar actions (Refresh, Edit).
- **Background:** Transparent.
- **Hover:** `bg-white/5`.

## 2. 🧩 Functionality

### Loading State
- **Visual:** Replaces icon/text with a spinner.
- **Interaction:** Button becomes `disabled`.
- **Opacity:** Reduced to `0.7`.

### Code Spec
```tsx
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'danger' | 'ghost' | 'outline';
  isLoading?: boolean;
  icon?: React.ElementType;
}

export default function Button({ children, variant = 'primary', isLoading, icon: Icon, className, ...props }: ButtonProps) {
  
  const baseStyles = "relative flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variants = {
    primary: "bg-gradient-to-r from-primary-600 to-secondary-600 text-white hover:shadow-[0_0_20px_-5px_rgba(59,130,246,0.4)] border border-transparent",
    danger: "bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500 hover:text-white",
    outline: "bg-transparent border border-gray-600 text-gray-300 hover:border-gray-400 hover:text-white",
    ghost: "bg-transparent text-gray-400 hover:text-white hover:bg-white/5 px-3",
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${className}`} 
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-5 h-5 animate-spin" />
      ) : (
        <>
          {Icon && <Icon className="w-5 h-5" />}
          {children}
        </>
      )}
      
      {/* Shine Effect Overlay for Primary */}
      {variant === 'primary' && !isLoading && (
        <div className="absolute inset-0 rounded-xl ring-1 ring-inset ring-white/10" />
      )}
    </button>
  );
}
```

## 3. 🛡️ Usage Rules
- **Stop Bot:** Must trigger a confirmation modal (FE-18) before executing function.
- **Save Config:** Must show loading state until backend confirms write success.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

