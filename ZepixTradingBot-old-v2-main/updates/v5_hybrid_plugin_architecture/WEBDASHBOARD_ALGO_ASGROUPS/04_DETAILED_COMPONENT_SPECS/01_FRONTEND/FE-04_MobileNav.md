# FE-04: MOBILE NAVIGATION & OFF-CANVAS
**Component ID:** FE-04  
**Layer:** Navigation  
**Target:** Mobile Devices (< 1024px)

---

## 1. 🏗️ Behavior Logic
Since dashboard tables are complex, mobile navigation must remain unobtrusive (Off-Canvas).

- **Interaction:** Triggered by "Hamburger" icon in Header.
- **Transition:** 
  - Backdrop fades in (`opacity-0` -> `opacity-100`).
  - Drawer slides in from left (`-translate-x-full` -> `translate-x-0`).
- **Performance:** Use `framer-motion` for smooth GPU-accelerated 60fps animations, or Tailwind transitions.

## 2. 🧩 UI Composition
The Mobile Nav essentially wraps the `FE-02 Sidebar` component but adds the overlay logic.

```tsx
import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { X } from 'lucide-react';
import SidebarContent from './SidebarContent'; // Visuals from FE-02

export default function MobileSidebar({ isOpen, onClose }) {
  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50 lg:hidden" onClose={onClose}>
        
        {/* Backdrop Overlay */}
        <Transition.Child
          enter="transition-opacity ease-linear duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="transition-opacity ease-linear duration-300"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" />
        </Transition.Child>

        {/* Sliding Panel */}
        <div className="fixed inset-0 flex">
          <Transition.Child
            enter="transition ease-in-out duration-300 transform"
            enterFrom="-translate-x-full"
            enterTo="translate-x-0"
            leave="transition ease-in-out duration-300 transform"
            leaveFrom="translate-x-0"
            leaveTo="-translate-x-full"
          >
            <Dialog.Panel className="relative flex w-full max-w-xs flex-1 flex-col bg-dark-900 pb-4 pt-5 shadow-2xl">
              
              {/* Close Button Details */}
              <div className="absolute top-0 right-0 -mr-12 pt-2">
                <button
                  type="button"
                  className="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                  onClick={onClose}
                >
                  <span className="sr-only">Close sidebar</span>
                  <X className="h-6 w-6 text-white" aria-hidden="true" />
                </button>
              </div>

              {/* Sidebar Content (Reusing FE-02 Logic) */}
              <div className="mt-5 h-full overflow-y-auto px-4">
                 <SidebarContent /> 
              </div>

            </Dialog.Panel>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition.Root>
  );
}
```

## 3. 📱 UX Considerations
- **Touch Targets:** Links should be at least `44px` tall for easy tapping.
- **Scroll Lock:** When menu is open, body scroll must be disabled (Handled by HeadlessUI Dialog).
- **Auto-Close:** Navigating to a new route must auto-close the drawer.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

