# 📈 TRENDLINE BREAK INTEGRATION

**File:** `09_TRENDLINE_BREAK_INTEGRATION.md`  
**Date:** 2026-01-14 13:00 IST  
**Alerts:** `TRENDLINE_BULLISH_BREAK`, `TRENDLINE_BEARISH_BREAK`  
**Type:** Entry Signal Enhancement  
**Pine Script Source:** Lines 814-826

---

## 1. PURPOSE

Trendline breaks are powerful technical signals that indicate potential trend reversals or continuations. When price breaks through a significant support or resistance trendline, it often signals the start of a new directional move.

This module documents how the bot should handle trendline break alerts from the V6 Pine Script.

---

## 2. PINE SCRIPT LOGIC

### 2.1 Trendline Bullish Break (Lines 814-819)

```pine
// Signal 13: Trendline Bullish Break
if trendlineBullishBreak and enableTrendline
    string tlBullMsg = "TRENDLINE_BULLISH_BREAK|" + syminfo.ticker + "|" + timeframe.period + "|" + 
                      str.tostring(close, "#.#####") + "|" + str.tostring(trendlineUpdatedSLPLow, "#.#####") + "|" + 
                      str.tostring(bar_index - trendlineUpdatedXLow)
    alert(tlBullMsg, alert.freq_once_per_bar)
```

**Trigger Condition:** `trendlineBullishBreak and enableTrendline`
- Price breaks above a downward-sloping resistance trendline
- Trendline feature must be enabled in Pine Script settings

### 2.2 Trendline Bearish Break (Lines 821-826)

```pine
// Signal 14: Trendline Bearish Break
if trendlineBearishBreak and enableTrendline
    string tlBearMsg = "TRENDLINE_BEARISH_BREAK|" + syminfo.ticker + "|" + timeframe.period + "|" + 
                      str.tostring(close, "#.#####") + "|" + str.tostring(trendlineUpdatedSLP, "#.#####") + "|" + 
                      str.tostring(bar_index - trendlineUpdatedX)
    alert(tlBearMsg, alert.freq_once_per_bar)
```

**Trigger Condition:** `trendlineBearishBreak and enableTrendline`
- Price breaks below an upward-sloping support trendline
- Trendline feature must be enabled in Pine Script settings

---

## 3. ALERT PAYLOAD SPECIFICATION

### 3.1 Bullish Break Payload

```
TRENDLINE_BULLISH_BREAK|EURUSD|15|1.08500|0.00025|45
```

| Index | Field | Type | Description | Example |
|-------|-------|------|-------------|---------|
| 0 | TYPE | string | Alert type identifier | `TRENDLINE_BULLISH_BREAK` |
| 1 | SYMBOL | string | Trading symbol | `EURUSD` |
| 2 | TF | string | Timeframe | `15` (15 minutes) |
| 3 | PRICE | float | Current close price | `1.08500` |
| 4 | SLOPE | float | Trendline slope value | `0.00025` |
| 5 | AGE | int | Bars since trendline start | `45` |

### 3.2 Bearish Break Payload

```
TRENDLINE_BEARISH_BREAK|GBPUSD|60|1.26500|-0.00030|60
```

| Index | Field | Type | Description | Example |
|-------|-------|------|-------------|---------|
| 0 | TYPE | string | Alert type identifier | `TRENDLINE_BEARISH_BREAK` |
| 1 | SYMBOL | string | Trading symbol | `GBPUSD` |
| 2 | TF | string | Timeframe | `60` (1 hour) |
| 3 | PRICE | float | Current close price | `1.26500` |
| 4 | SLOPE | float | Trendline slope value | `-0.00030` |
| 5 | AGE | int | Bars since trendline start | `60` |

---

## 4. PAYLOAD PARSING (PYTHON)

```python
class TrendlineBreakAlert:
    """
    Parser for TRENDLINE_BULLISH_BREAK and TRENDLINE_BEARISH_BREAK alerts
    """
    
    def __init__(self, raw_payload: str):
        parts = raw_payload.split("|")
        
        self.type = parts[0]           # TRENDLINE_BULLISH_BREAK or TRENDLINE_BEARISH_BREAK
        self.symbol = parts[1]         # e.g., EURUSD
        self.tf = parts[2]             # e.g., 15
        self.price = float(parts[3])   # e.g., 1.08500
        self.slope = float(parts[4])   # e.g., 0.00025
        self.age = int(parts[5])       # e.g., 45
        
        # Derived fields
        self.direction = "BUY" if "BULLISH" in self.type else "SELL"
        self.is_bullish = "BULLISH" in self.type
        
    def is_significant_break(self) -> bool:
        """
        Check if trendline break is significant based on age
        Older trendlines (more bars) are more significant
        """
        return self.age >= 30  # Minimum 30 bars for significance
        
    def get_slope_strength(self) -> str:
        """
        Classify slope strength
        """
        abs_slope = abs(self.slope)
        if abs_slope > 0.0005:
            return "STEEP"
        elif abs_slope > 0.0002:
            return "MODERATE"
        else:
            return "SHALLOW"
```

---

## 5. BOT ACTION LOGIC

### 5.1 Standalone Entry (Primary Use)

Trendline breaks can trigger standalone entries when other conditions are met.

```python
class TrendlineBreakHandler:
    """
    Handler for trendline break signals
    """
    
    def validate_entry(self, alert: TrendlineBreakAlert) -> bool:
        """
        Validate if trendline break should trigger entry
        """
        # Rule 1: Trendline must be significant (old enough)
        if not alert.is_significant_break():
            logger.info(f"❌ Trendline too young: {alert.age} bars < 30 minimum")
            return False
            
        # Rule 2: Slope must be meaningful
        if alert.get_slope_strength() == "SHALLOW":
            logger.info(f"❌ Trendline slope too shallow: {alert.slope}")
            return False
            
        return True
        
    def execute_entry(self, alert: TrendlineBreakAlert) -> dict:
        """
        Execute trendline break entry
        """
        # Calculate lot size based on trendline age
        age_multiplier = min(alert.age / 50, 1.5)  # Max 1.5x for old trendlines
        
        return {
            "action": "ENTRY",
            "direction": alert.direction,
            "symbol": alert.symbol,
            "lot_multiplier": age_multiplier,
            "reason": f"Trendline break (age: {alert.age} bars)"
        }
```

### 5.2 Entry Signal Enhancement (Secondary Use)

Trendline breaks can enhance confidence of existing entry signals.

```python
def enhance_entry_confidence(entry_alert, trendline_alert: TrendlineBreakAlert) -> int:
    """
    Add confidence points if trendline break aligns with entry signal
    
    Returns: Additional confidence points (0-25)
    """
    bonus = 0
    
    # Check direction alignment
    if entry_alert.direction == trendline_alert.direction:
        # Base bonus for alignment
        bonus += 10
        
        # Additional bonus for significant trendline
        if trendline_alert.is_significant_break():
            bonus += 10
            
        # Additional bonus for steep slope
        if trendline_alert.get_slope_strength() == "STEEP":
            bonus += 5
            
    return bonus
```

---

## 6. INTEGRATION WITH ENTRY SIGNALS

### 6.1 Confidence Scoring Integration

When a `BULLISH_ENTRY` or `BEARISH_ENTRY` signal arrives, check for recent trendline breaks:

```python
def process_entry_with_trendline(self, entry_alert, recent_trendline_breaks: list):
    """
    Process entry signal with trendline break consideration
    """
    base_confidence = entry_alert.confidence_score
    
    # Check for aligned trendline breaks in last 5 bars
    for tl_break in recent_trendline_breaks:
        if tl_break.direction == entry_alert.direction:
            bonus = enhance_entry_confidence(entry_alert, tl_break)
            base_confidence += bonus
            logger.info(f"✅ Trendline break adds +{bonus} confidence")
            
    # Cap at 100
    final_confidence = min(base_confidence, 100)
    
    return final_confidence
```

### 6.2 Timeframe-Specific Rules

| Timeframe | Trendline Break Action | Lot Modifier |
|-----------|------------------------|--------------|
| 1M | IGNORE (too noisy) | N/A |
| 5M | Entry enhancement only | +0.25x if aligned |
| 15M | Standalone entry allowed | 1.0x base |
| 1H | Standalone entry allowed | 1.25x base |

---

## 7. ROUTING RULES

### 7.1 Order Routing Matrix

| Alert Type | Timeframe | Order Type | Routing |
|------------|-----------|------------|---------|
| TRENDLINE_BULLISH_BREAK | 1M | SKIP | No action |
| TRENDLINE_BULLISH_BREAK | 5M | ENHANCEMENT | Add to confidence |
| TRENDLINE_BULLISH_BREAK | 15M | ORDER A | Standard entry |
| TRENDLINE_BULLISH_BREAK | 1H | ORDER A | Standard entry |
| TRENDLINE_BEARISH_BREAK | 1M | SKIP | No action |
| TRENDLINE_BEARISH_BREAK | 5M | ENHANCEMENT | Add to confidence |
| TRENDLINE_BEARISH_BREAK | 15M | ORDER A | Standard entry |
| TRENDLINE_BEARISH_BREAK | 1H | ORDER A | Standard entry |

### 7.2 Risk Management

```python
def calculate_trendline_sl(alert: TrendlineBreakAlert) -> float:
    """
    Calculate stop loss based on trendline break
    
    SL is placed just beyond the broken trendline
    """
    # Use ATR-based buffer
    atr_buffer = get_atr(alert.symbol, alert.tf) * 1.5
    
    if alert.is_bullish:
        # For bullish break, SL below the trendline
        sl_price = alert.price - atr_buffer
    else:
        # For bearish break, SL above the trendline
        sl_price = alert.price + atr_buffer
        
    return sl_price
```

---

## 8. SCENARIO SIMULATIONS

### Scenario 1: Strong Bullish Trendline Break

**Alert:** `TRENDLINE_BULLISH_BREAK|EURUSD|15|1.08500|0.00035|55`

**Analysis:**
- Symbol: EURUSD
- Timeframe: 15m (eligible for standalone entry)
- Price: 1.08500
- Slope: 0.00035 (MODERATE)
- Age: 55 bars (SIGNIFICANT)

**Bot Action:**
1. Validate: Age (55) >= 30 ✅, Slope (MODERATE) ✅
2. Execute: BUY order with 1.1x lot multiplier (55/50 = 1.1)
3. Set SL: 1.08500 - (ATR * 1.5)
4. Log: "✅ Trendline break entry: EURUSD BUY @ 1.08500"

### Scenario 2: Weak Trendline Break (Rejected)

**Alert:** `TRENDLINE_BEARISH_BREAK|GBPUSD|5|1.26500|0.00010|15`

**Analysis:**
- Symbol: GBPUSD
- Timeframe: 5m (enhancement only)
- Price: 1.26500
- Slope: 0.00010 (SHALLOW)
- Age: 15 bars (NOT SIGNIFICANT)

**Bot Action:**
1. Validate: Age (15) < 30 ❌
2. Result: **NO STANDALONE ENTRY**
3. Store for potential entry enhancement

### Scenario 3: Trendline Enhances Entry Signal

**Entry Alert:** `BEARISH_ENTRY|EURUSD|15|1.08500|SELL|MODERATE|70|...`
**Trendline Alert:** `TRENDLINE_BEARISH_BREAK|EURUSD|15|1.08500|-0.00040|50`

**Analysis:**
- Entry confidence: 70
- Trendline aligned: YES (both SELL)
- Trendline significant: YES (50 bars)
- Trendline slope: STEEP

**Bot Action:**
1. Base confidence: 70
2. Alignment bonus: +10
3. Significance bonus: +10
4. Steep slope bonus: +5
5. Final confidence: 95 (HIGH)
6. Execute with enhanced confidence

---

## 9. STATE MANAGEMENT

```python
class TrendlineBreakState:
    """
    Track recent trendline breaks for entry enhancement
    """
    
    def __init__(self, max_age_bars: int = 5):
        self.recent_breaks = {}  # symbol_tf -> list of breaks
        self.max_age_bars = max_age_bars
        
    def add_break(self, alert: TrendlineBreakAlert):
        key = f"{alert.symbol}_{alert.tf}"
        if key not in self.recent_breaks:
            self.recent_breaks[key] = []
        self.recent_breaks[key].append({
            "alert": alert,
            "bar_index": get_current_bar_index(),
            "timestamp": datetime.now()
        })
        
    def get_recent_breaks(self, symbol: str, tf: str) -> list:
        """
        Get trendline breaks within last N bars
        """
        key = f"{symbol}_{tf}"
        if key not in self.recent_breaks:
            return []
            
        current_bar = get_current_bar_index()
        return [
            b["alert"] for b in self.recent_breaks[key]
            if current_bar - b["bar_index"] <= self.max_age_bars
        ]
        
    def cleanup_old_breaks(self):
        """
        Remove breaks older than max_age_bars
        """
        current_bar = get_current_bar_index()
        for key in self.recent_breaks:
            self.recent_breaks[key] = [
                b for b in self.recent_breaks[key]
                if current_bar - b["bar_index"] <= self.max_age_bars
            ]
```

---

## 10. DIFFERENCE FROM V3

| Aspect | V3 (Combined Logic) | V6 (Price Action) |
|--------|---------------------|-------------------|
| Trendline Detection | Basic (breakout system) | Advanced (pivot-based) |
| Alert Format | JSON | Pipe-separated |
| Slope Data | Not included | Included in payload |
| Age Data | Not included | Included in payload |
| Standalone Entry | No | Yes (15m, 1H) |
| Enhancement Use | No | Yes (5m) |

---

**STATUS: DEFINED & READY FOR IMPLEMENTATION**
