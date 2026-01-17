# 🐋 PRICE ACTION LOGIC: 1H (SWING)

**File:** `05_PRICE_ACTION_LOGIC_1H.md`  
**Date:** 2026-01-11 04:40 IST  
**Timeframe:** 1 Hour (and 4H)  
**Class:** `PriceActionLogic1H`

---

## 1. STRATEGY PROFILE
-   **Type:** Swing Trading.
-   **Goal:** Capture multi-day trends.
-   **Risk Multiplier:** 0.6x (Reduced size for wider stops).
-   **Routing Key:** `tf="60"` or `tf="240"`
-   **Routing Rule:** **ORDER A ONLY** (Refill prohibited).

---

## 2. ENTRY CONDITIONS

### **A. Primary Trigger**
-   Alert: `BULLISH_ENTRY` / `BEARISH_ENTRY`.
-   Timeframe: `60` or `240`.

### **B. Filters (Swing Rules)**
| Filter | Condition | Action if Fail | Reason |
| :--- | :--- | :--- | :--- |
| **HTF Alignment** | Match `4H` Trend | **SKIP** | Never swim against the tide. |
| **Volatility** | Vix Fix Check | **WARNING** | If volatility extreme, reduce size. |
| **Logic** | Logic 3 (Legacy) | **REPLACE** | Replace old Logic 3 with this. |

---

## 3. EXIT STRATEGY

### **A. Signal Exit**
-   Trigger: `EXIT_BULLISH` / `EXIT_BEARISH`.
-   Action: Close 50%. Let 50% run until Trend Pulse Reversal.

### **B. Target Exit**
-   **TP1:** Close 20%.
-   **TP2:** Close 40%.
-   **TP3:** Close 40% (Targeting big moves).

---

## 4. LOGIC IMPLEMENTATION (PYTHON)

```python
class PriceActionLogic1H:
    """
    1H Swing Logic
    Patient, Trend-Following, Wide Stops
    
    PINE SCRIPT SUPREMACY: Uses alert.alignment from payload
    instead of TrendManager for fresh entry validation.
    """
    
    def validate_entry(self, alert: ZepixV6Alert) -> bool:
        # Rule 1: 4H Alignment from PAYLOAD (Pine Script Supremacy)
        # alert.alignment format: "bull_count/bear_count" (e.g., "4/0")
        bull_count, bear_count = alert.get_pulse_counts()
        
        # Handle missing alignment data
        if alert.alignment == "0/0" or (bull_count == 0 and bear_count == 0):
            logger.warning("[1H] No MTF alignment data in payload, proceeding with caution")
            return True
        
        # For 1H, require 4+ alignment (higher threshold for swing trades)
        if alert.direction.upper() == "BUY":
            is_aligned = bull_count >= 4
        else:
            is_aligned = bear_count >= 4
        
        if not is_aligned:
            logger.info(f"[1H Skip] Payload alignment weak: {alert.alignment} (need 4+)")
            return False
        
        return True

    def calculate_lots(self, base_lot: float) -> float:
        # Swing trades carry overnight risk, reduce size
        return base_lot * 0.6
        
    def get_order_config(self):
        return {
            "order_type": "market",
            "use_hybrid_sl": True,  # Uses the wider Swing SL from Pine
            "trailing_stop": False  # Give it room to breathe
        }
```

---

**STATUS: DEFINED & READY**
