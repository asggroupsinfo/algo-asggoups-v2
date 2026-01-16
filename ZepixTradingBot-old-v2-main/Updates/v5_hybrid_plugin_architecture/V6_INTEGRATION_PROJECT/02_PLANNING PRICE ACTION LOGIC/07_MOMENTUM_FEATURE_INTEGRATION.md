# 🎳 MOMENTUM MONITORING & STATE INTEGRATION

**File:** `07_MOMENTUM_FEATURE_INTEGRATION.md`  
**Date:** 2026-01-11 04:50 IST  
**Alert:** `MOMENTUM_CHANGE`  
**Type:** Real-Time Monitoring

---

## 1. PURPOSE
Unlike "ADX Filters" (which filter entries), this module **Monitors** the market's horsepower.
It answers: *"Is the trend accelerating or dying?"*

---

## 2. ALERT PAYLOAD PARSING
**Source:** `02_ALERT_JSON_PAYLOADS.md` (Index 3)

```python
# Payload Indices
TYPE = 0            # MOMENTUM_CHANGE
SYMBOL = 1
TF = 2
ADX_CURR = 3        # Float
ADX_STR_CURR = 4    # STRONG, MODERATE, WEAK
ADX_PREV = 5
ADX_STR_PREV = 6
DIRECTION = 7       # INCREASING, DECREASING
```

---

## 3. STATE UPDATE LOGIC (THE "DYNO")

We need a `MomentumState` class in the bot's memory.

```python
class MomentumState:
    def __init__(self):
        # Store by Symbol + TF
        self.states = {} 
        
    def update(self, symbol, tf, data):
        key = f"{symbol}_{tf}"
        self.states[key] = {
            "value": float(data['adx_curr']),
            "strength": data['adx_str_curr'],
            "direction": data['direction'],
            "last_updated": datetime.now()
        }
```

---

## 4. TRADING IMPLICATIONS

### **A. Entry Modification**
When `PriceActionLogic` requests entry, it checks `MomentumState`:
-   **If INCREASING:** Normal Execution.
-   **If DECREASING:** Warning! 
    -   *Logic:* "Trend is losing steam."
    -   *Action:* Reduce Lot Size by 25%.

### **B. Active Trade Management**
When `MOMENTUM_CHANGE` alert arrives:
-   **If Trend was STRONG -> Now WEAK:**
    -   *Action:* **Tighten Stop Loss** (Move to Trailing).
    -   *Reason:* The push is over. Protect profits.

---

## 5. SCENARIO

**Scenario:** Long EURUSD (5m) is open.
1.  **Alert:** `MOMENTUM_CHANGE|EURUSD|5|...|DECREASING` received.
2.  **Bot Action:** 
    -   Detects open Long.
    -   Sees momentum fading.
    -   **Triggers:** `update_sl_to_breakeven()` or `tighten_trailing_stop()`.

**STATUS: PLANNED**

---

## 6. STATE_CHANGE ALERT INTEGRATION

**Alert:** `STATE_CHANGE`  
**Pine Script Source:** Lines 859-865  
**Type:** Real-Time Market State Monitoring

### 6.1 Pine Script Logic

```pine
// 2. STATE_CHANGE Logic (Lines 859-865)
if enableTrendPulse
    if marketState != check_prev_mkt_state
        cond_state_change := true
        stateMsg_global := "STATE_CHANGE|" + syminfo.ticker + "|" + timeframe.period + "|" + 
                          marketState + "|" + check_prev_mkt_state + "|" + 
                          str.tostring(bullishAlignment) + "/" + str.tostring(bearishAlignment)
```

**Trigger Condition:** `marketState != check_prev_mkt_state`
- Fires when market state changes (e.g., BULLISH -> NEUTRAL, NEUTRAL -> BEARISH)
- Requires Trend Pulse feature to be enabled

### 6.2 Alert Payload Specification

```
STATE_CHANGE|EURUSD|15|BULLISH|NEUTRAL|4/2
```

| Index | Field | Type | Description | Example |
|-------|-------|------|-------------|---------|
| 0 | TYPE | string | Alert type identifier | `STATE_CHANGE` |
| 1 | SYMBOL | string | Trading symbol | `EURUSD` |
| 2 | TF | string | Timeframe | `15` (15 minutes) |
| 3 | CURRENT_STATE | string | New market state | `BULLISH`, `BEARISH`, `NEUTRAL` |
| 4 | PREVIOUS_STATE | string | Previous market state | `BULLISH`, `BEARISH`, `NEUTRAL` |
| 5 | ALIGNMENT | string | Bullish/Bearish TF alignment | `4/2` (4 bullish, 2 bearish) |

### 6.3 Payload Parsing (Python)

```python
class StateChangeAlert:
    """
    Parser for STATE_CHANGE alerts
    """
    
    def __init__(self, raw_payload: str):
        parts = raw_payload.split("|")
        
        self.type = parts[0]              # STATE_CHANGE
        self.symbol = parts[1]            # e.g., EURUSD
        self.tf = parts[2]                # e.g., 15
        self.current_state = parts[3]     # BULLISH, BEARISH, NEUTRAL
        self.previous_state = parts[4]    # BULLISH, BEARISH, NEUTRAL
        
        # Parse alignment (e.g., "4/2" -> bullish=4, bearish=2)
        alignment_parts = parts[5].split("/")
        self.bullish_alignment = int(alignment_parts[0])
        self.bearish_alignment = int(alignment_parts[1])
        
    def is_bullish_shift(self) -> bool:
        """Check if state shifted toward bullish"""
        state_order = {"BEARISH": 0, "NEUTRAL": 1, "BULLISH": 2}
        return state_order[self.current_state] > state_order[self.previous_state]
        
    def is_bearish_shift(self) -> bool:
        """Check if state shifted toward bearish"""
        state_order = {"BEARISH": 0, "NEUTRAL": 1, "BULLISH": 2}
        return state_order[self.current_state] < state_order[self.previous_state]
        
    def get_alignment_ratio(self) -> float:
        """Get bullish/bearish alignment ratio"""
        total = self.bullish_alignment + self.bearish_alignment
        if total == 0:
            return 0.5
        return self.bullish_alignment / total
```

### 6.4 State Update Logic

```python
class MarketStateManager:
    """
    Track market state changes across symbols and timeframes
    """
    
    def __init__(self):
        self.states = {}  # symbol_tf -> state data
        
    def update(self, alert: StateChangeAlert):
        key = f"{alert.symbol}_{alert.tf}"
        self.states[key] = {
            "current_state": alert.current_state,
            "previous_state": alert.previous_state,
            "bullish_alignment": alert.bullish_alignment,
            "bearish_alignment": alert.bearish_alignment,
            "last_updated": datetime.now()
        }
        
    def get_state(self, symbol: str, tf: str) -> dict:
        key = f"{symbol}_{tf}"
        return self.states.get(key, None)
        
    def is_trending(self, symbol: str, tf: str) -> bool:
        """Check if market is in trending state (not neutral)"""
        state = self.get_state(symbol, tf)
        if state is None:
            return False
        return state["current_state"] != "NEUTRAL"
```

### 6.5 Trading Implications

#### A. Entry Modification

When `PriceActionLogic` requests entry, check `MarketStateManager`:

| State Change | Action | Reason |
|--------------|--------|--------|
| NEUTRAL -> BULLISH | Allow LONG entries | Trend starting |
| NEUTRAL -> BEARISH | Allow SHORT entries | Trend starting |
| BULLISH -> NEUTRAL | Reduce LONG size by 50% | Trend weakening |
| BEARISH -> NEUTRAL | Reduce SHORT size by 50% | Trend weakening |
| BULLISH -> BEARISH | Close LONGs, allow SHORTs | Trend reversal |
| BEARISH -> BULLISH | Close SHORTs, allow LONGs | Trend reversal |

#### B. Active Trade Management

When `STATE_CHANGE` alert arrives with open positions:

```python
def handle_state_change_for_trades(self, alert: StateChangeAlert):
    """
    Manage open trades based on state change
    """
    open_trades = self.get_open_trades(alert.symbol)
    
    for trade in open_trades:
        # Check if state change is adverse to trade direction
        if trade.direction == "LONG" and alert.is_bearish_shift():
            if alert.current_state == "BEARISH":
                # Full reversal - close trade
                self.close_trade(trade, reason="State reversed to BEARISH")
            elif alert.current_state == "NEUTRAL":
                # Weakening - tighten stop
                self.tighten_stop_loss(trade)
                
        elif trade.direction == "SHORT" and alert.is_bullish_shift():
            if alert.current_state == "BULLISH":
                # Full reversal - close trade
                self.close_trade(trade, reason="State reversed to BULLISH")
            elif alert.current_state == "NEUTRAL":
                # Weakening - tighten stop
                self.tighten_stop_loss(trade)
```

### 6.6 Scenario Simulations

**Scenario 1:** Long EURUSD (15m) is open, state changes BULLISH -> NEUTRAL

1. **Alert:** `STATE_CHANGE|EURUSD|15|NEUTRAL|BULLISH|3/3` received
2. **Analysis:** Bullish trend weakening (now 50/50 alignment)
3. **Bot Action:**
   - Detects open Long
   - Sees state weakened to NEUTRAL
   - **Triggers:** `tighten_stop_loss()` - Move SL to breakeven or trailing

**Scenario 2:** No position, state changes NEUTRAL -> BULLISH

1. **Alert:** `STATE_CHANGE|GBPUSD|60|BULLISH|NEUTRAL|5/1` received
2. **Analysis:** New bullish trend starting (5 bullish, 1 bearish alignment)
3. **Bot Action:**
   - No immediate action (STATE_CHANGE is informational)
   - Updates `MarketStateManager`
   - Next BULLISH_ENTRY signal will be allowed with full size

**Scenario 3:** Short USDJPY (5m) is open, state changes BEARISH -> BULLISH

1. **Alert:** `STATE_CHANGE|USDJPY|5|BULLISH|BEARISH|4/2` received
2. **Analysis:** Full trend reversal!
3. **Bot Action:**
   - Detects open Short
   - Sees state fully reversed to BULLISH
   - **Triggers:** `close_trade(reason="State reversed to BULLISH")`

---

## 7. COMBINED MONITORING ARCHITECTURE

Both `MOMENTUM_CHANGE` and `STATE_CHANGE` alerts work together:

```python
class RealTimeMonitor:
    """
    Combined monitoring for momentum and state changes
    """
    
    def __init__(self):
        self.momentum_state = MomentumState()
        self.market_state = MarketStateManager()
        
    def process_alert(self, raw_payload: str):
        alert_type = raw_payload.split("|")[0]
        
        if alert_type == "MOMENTUM_CHANGE":
            alert = MomentumChangeAlert(raw_payload)
            self.momentum_state.update(alert.symbol, alert.tf, alert.__dict__)
            self.handle_momentum_change(alert)
            
        elif alert_type == "STATE_CHANGE":
            alert = StateChangeAlert(raw_payload)
            self.market_state.update(alert)
            self.handle_state_change(alert)
            
    def get_market_condition(self, symbol: str, tf: str) -> dict:
        """
        Get combined market condition for trading decisions
        """
        momentum = self.momentum_state.states.get(f"{symbol}_{tf}", {})
        state = self.market_state.get_state(symbol, tf)
        
        return {
            "momentum_direction": momentum.get("direction", "UNKNOWN"),
            "momentum_strength": momentum.get("strength", "UNKNOWN"),
            "market_state": state["current_state"] if state else "UNKNOWN",
            "alignment_ratio": state["bullish_alignment"] / (state["bullish_alignment"] + state["bearish_alignment"]) if state else 0.5
        }
```

---

**STATUS: DEFINED & READY FOR IMPLEMENTATION**
