# 🦅 PRICE ACTION LOGIC: 15M (INTRADAY)

**File:** `04_PRICE_ACTION_LOGIC_15M.md`  
**Date:** 2026-01-11 04:35 IST  
**Timeframe:** 15 Minutes  
**Class:** `PriceActionLogic15M`

---

## 1. STRATEGY PROFILE
-   **Type:** Day Trading Anchor.
-   **Goal:** Capture the primary move of the session.
-   **Risk Multiplier:** 1.0x (Standard).
-   **Routing Key:** `tf="15"`
-   **Routing Rule:** **ORDER A ONLY** (Refill prohibited).

---

## 2. ENTRY CONDITIONS

### **A. Primary Trigger**
-   Alert: `BULLISH_ENTRY` / `BEARISH_ENTRY`.
-   Timeframe: `15`.

### **B. Filters (Market Structure Rules)**
| Filter | Condition | Action if Fail | Reason |
| :--- | :--- | :--- | :--- |
| **Market State** | Match Signal | **SKIP** | Only trade WITH the Global Market State. |
| **Pulse Alignment** | `Bull Count > Bear Count` (for Buy) | **SKIP** | Majority of TFs must agree. |
| **ADX** | `adx > 20` | **WARNING** | If < 20, reduce risk 50%. |

---

## 3. EXIT STRATEGY

### **A. Signal Exit**
-   Trigger: `EXIT_BULLISH` / `EXIT_BEARISH`.
-   Action: Close 100%. Don't hold intraday against separation signals.

### **B. Target Exit**
-   **TP1:** Close 40%.
-   **TP2:** Close 40%.
-   **TP3:** Close 20% (Trailing).

---

## 4. LOGIC IMPLEMENTATION (PYTHON)

```python
class PriceActionLogic15M:
    """
    15-Minute Intraday Logic
    Relies on Pulse Alignment from PAYLOAD
    
    PINE SCRIPT SUPREMACY: Uses alert.alignment from payload
    instead of TrendManager for fresh entry validation.
    """
    
    def validate_entry(self, alert: ZepixV6Alert) -> bool:
        # Rule 1: Pulse Alignment from PAYLOAD (Pine Script Supremacy)
        # alert.alignment format: "bull_count/bear_count" (e.g., "3/0")
        bull_count, bear_count = alert.get_pulse_counts()
        
        # Handle missing alignment data
        if alert.alignment == "0/0" or (bull_count == 0 and bear_count == 0):
            logger.warning("[15M] No MTF alignment data in payload, proceeding with caution")
            return True
        
        # For 15M, require 3+ alignment
        if alert.direction.upper() == "BUY":
            is_aligned = bull_count >= 3
        else:
            is_aligned = bear_count >= 3
        
        if not is_aligned:
            logger.info(f"[15M Skip] Payload alignment weak: {alert.alignment} (need 3+)")
            return False
             
        return True

    def calculate_lots(self, base_lot: float) -> float:
        return base_lot 
        
    def get_order_config(self):
        return {
            "order_type": "market",
            "use_hybrid_sl": True,
            "trailing_stop": True
        }
```

---

**STATUS: DEFINED & READY**
