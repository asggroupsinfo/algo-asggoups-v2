# FE-18: MODAL DIALOGS SPECIFICATION
**Component ID:** FE-18  
**Layer:** System UI  
**Lib:** Headless UI (`Dialog`)

---

## 1. 🖼️ Visual Context
Used for disrupting actions that require explicit confirmation or complex inputs.

- **Overlay:** `bg-black/80 backdrop-blur-sm` (Focus mechanism).
- **Panel:** Centered, `bg-dark-900 border border-dark-700`, `rounded-2xl`.
- **Animation:** Scale up + Fade in (`ease-out duration-300`).

## 2. 🧩 Common Modals

### A. Confirmation Modal (Danger)
- **Title:** "Stop Trading Bot?"
- **Body:** "This will cancel all open orders and close positions. Are you sure?"
- **Actions:** [Cancel] [Stop Bot (Red)]

### B. Configuration Modal (Form)
- **Title:** "Edit V3 Logic Parameters"
- **Body:** Contains `FE-12` Inputs and `FE-10` Sliders.
- **Actions:** [Cancel] [Save Changes]

## 3. 🧬 React Implementation template

```tsx
import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';

export default function ConfirmModal({ isOpen, onClose, onConfirm, title, message }) {
  return (
    <Transition show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        
        {/* Backdrop */}
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" />
        </Transition.Child>

        {/* Panel */}
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-dark-900 border border-dark-700 p-6 text-left align-middle shadow-xl transition-all">
              
              <Dialog.Title as="h3" className="text-lg font-bold leading-6 text-white">
                {title}
              </Dialog.Title>
              
              <div className="mt-2">
                <p className="text-sm text-gray-400">
                  {message}
                </p>
              </div>

              <div className="mt-6 flex justify-end gap-3">
                <button
                  type="button"
                  className="px-4 py-2 rounded-lg bg-dark-800 text-gray-300 hover:bg-dark-700"
                  onClick={onClose}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="px-4 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600"
                  onClick={onConfirm}
                >
                  Confirm
                </button>
              </div>
            </Dialog.Panel>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition>
  );
}
```


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

