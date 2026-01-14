# 🔥 SCREENER FULL INTEGRATION

**File:** `10_SCREENER_FULL_INTEGRATION.md`  
**Date:** 2026-01-14 13:05 IST  
**Alerts:** `SCREENER_FULL_BULLISH`, `SCREENER_FULL_BEARISH`  
**Type:** High-Confidence Entry Signal  
**Pine Script Source:** Lines 1660-1668

---

## 1. PURPOSE

The Screener Full signals are the highest-confidence signals in the V6 system. They fire when ALL 9 technical indicators align in the same direction, indicating extremely strong market momentum.

This module documents how the bot should handle screener full alerts from the V6 Pine Script.

---

## 2. PINE SCRIPT LOGIC

### 2.1 Full Bullish Detection (Lines 1634, 1660-1663)

```pine
// Global Scope Definition (Line 1634)
bool fullBullish = rsiLabelCell == #089981 and mfiLabelCell == #089981 and 
    fisherLabelCell == #089981 and dmiLabelCell == #089981 and momLabelCell == #089981 and 
    psarLabelCell == #089981 and macdLabel == #089981 and stochLabel == #089981 and vortexLabel == #089981

// Alert Generation (Lines 1660-1663)
// Signal 11: Screener Full Bullish
if fullBullish
    string scrBullMsg = "SCREENER_FULL_BULLISH|" + syminfo.ticker + "|" + timeframe.period + "|9|MACD,STOCH,VORTEX,MOMENTUM,RSI,PSAR,DMI,MFI,FISHER"
    alert(scrBullMsg, alert.freq_once_per_bar)
```

**Trigger Condition:** All 9 indicators show bullish (green color #089981)

### 2.2 Full Bearish Detection (Lines 1635, 1665-1668)

```pine
// Global Scope Definition (Line 1635)
bool fullBearish = rsiLabelCell == #ff1100 and mfiLabelCell == #ff1100 and 
    fisherLabelCell == #ff1100 and dmiLabelCell == #ff1100 and momLabelCell == #ff1100 and 
    psarLabelCell == #ff1100 and macdLabel == #ff1100 and stochLabel == #ff1100 and vortexLabel == #ff1100

// Alert Generation (Lines 1665-1668)
// Signal 12: Screener Full Bearish
if fullBearish
    string scrBearMsg = "SCREENER_FULL_BEARISH|" + syminfo.ticker + "|" + timeframe.period + "|9|MACD,STOCH,VORTEX,MOMENTUM,RSI,PSAR,DMI,MFI,FISHER"
    alert(scrBearMsg, alert.freq_once_per_bar)
```

**Trigger Condition:** All 9 indicators show bearish (red color #ff1100)

---

## 3. THE 9 INDICATORS

| # | Indicator | Bullish Condition | Bearish Condition |
|---|-----------|-------------------|-------------------|
| 1 | MACD | macdLine > signalLine | macdLine < signalLine |
| 2 | Stochastic RSI | k_val > dsc | k_val < dsc |
| 3 | Vortex | VIP > VIM | VIP < VIM |
| 4 | Momentum | mom_val > mom_val[1] | mom_val < mom_val[1] |
| 5 | RSI | rsi_val > rsi_val[1] | rsi_val < rsi_val[1] |
| 6 | PSAR | close > psar_val | close < psar_val |
| 7 | DMI | diplus > diminus | diplus < diminus |
| 8 | MFI | mfi_val > mfi_val[1] | mfi_val < mfi_val[1] |
| 9 | Fisher Transform | fish1 > fish2 | fish1 < fish2 |

---

## 4. ALERT PAYLOAD SPECIFICATION

### 4.1 Full Bullish Payload

```
SCREENER_FULL_BULLISH|EURUSD|15|9|MACD,STOCH,VORTEX,MOMENTUM,RSI,PSAR,DMI,MFI,FISHER
```

| Index | Field | Type | Description | Example |
|-------|-------|------|-------------|---------|
| 0 | TYPE | string | Alert type identifier | `SCREENER_FULL_BULLISH` |
| 1 | SYMBOL | string | Trading symbol | `EURUSD` |
| 2 | TF | string | Timeframe | `15` (15 minutes) |
| 3 | COUNT | int | Number of aligned indicators | `9` (always 9 for full) |
| 4 | INDICATORS | string | Comma-separated indicator list | `MACD,STOCH,VORTEX,...` |

### 4.2 Full Bearish Payload

```
SCREENER_FULL_BEARISH|GBPUSD|60|9|MACD,STOCH,VORTEX,MOMENTUM,RSI,PSAR,DMI,MFI,FISHER
```

| Index | Field | Type | Description | Example |
|-------|-------|------|-------------|---------|
| 0 | TYPE | string | Alert type identifier | `SCREENER_FULL_BEARISH` |
| 1 | SYMBOL | string | Trading symbol | `GBPUSD` |
| 2 | TF | string | Timeframe | `60` (1 hour) |
| 3 | COUNT | int | Number of aligned indicators | `9` (always 9 for full) |
| 4 | INDICATORS | string | Comma-separated indicator list | `MACD,STOCH,VORTEX,...` |

---

## 5. PAYLOAD PARSING (PYTHON)

```python
class ScreenerFullAlert:
    """
    Parser for SCREENER_FULL_BULLISH and SCREENER_FULL_BEARISH alerts
    """
    
    def __init__(self, raw_payload: str):
        parts = raw_payload.split("|")
        
        self.type = parts[0]           # SCREENER_FULL_BULLISH or SCREENER_FULL_BEARISH
        self.symbol = parts[1]         # e.g., EURUSD
        self.tf = parts[2]             # e.g., 15
        self.count = int(parts[3])     # e.g., 9
        self.indicators = parts[4].split(",")  # List of indicator names
        
        # Derived fields
        self.direction = "BUY" if "BULLISH" in self.type else "SELL"
        self.is_bullish = "BULLISH" in self.type
        self.confidence = 100  # Full alignment = maximum confidence
        
    def get_indicator_list(self) -> list:
        """
        Return list of aligned indicators
        """
        return self.indicators
        
    def is_full_alignment(self) -> bool:
        """
        Verify all 9 indicators are aligned
        """
        return self.count == 9 and len(self.indicators) == 9
```

---

## 6. DIFFERENCE FROM V3 SCREENER SIGNALS

### 6.1 V3 Screener (Signals 9 & 10)

**Pine Script V3 Logic:**
```pine
bool signal9_ScreenerFullBullish = (consensusEnabled and consensusScore == 9 
    and mtfBullishAligned and marketTrend == 1 
    and volumeDeltaRatio > 2.0 and not priceInBearOB and not isEQH)
```

**V3 Characteristics:**
- Alert Format: JSON (`{"type":"entry_v3","signal_type":"Screener_Full_Bullish",...}`)
- Additional Filters: MTF alignment, volume delta, OB check, equal H/L check
- Routing: Force to LOGIC3 (swing trading)
- Position Multiplier: 1.0 (full size)

### 6.2 V6 Screener (This Document)

**V6 Characteristics:**
- Alert Format: Pipe-separated (`SCREENER_FULL_BULLISH|...|9|...`)
- No Additional Filters: Pure indicator alignment
- Routing: Timeframe-based (see Section 7)
- Confidence: 100 (maximum)

### 6.3 Key Differences Summary

| Aspect | V3 Screener | V6 Screener |
|--------|-------------|-------------|
| Alert Format | JSON | Pipe-separated |
| MTF Filter | Required | Not included |
| Volume Filter | Required (>2.0) | Not included |
| OB Filter | Required (not in OB) | Not included |
| Equal H/L Filter | Required | Not included |
| Routing | Always LOGIC3 | Timeframe-based |
| Use Case | Swing trades only | All timeframes |

---

## 7. BOT ACTION LOGIC

### 7.1 Entry Validation

```python
class ScreenerFullHandler:
    """
    Handler for screener full signals
    """
    
    def validate_entry(self, alert: ScreenerFullAlert) -> bool:
        """
        Validate if screener full should trigger entry
        
        Note: Screener Full is already the highest confidence signal,
        so minimal additional validation is needed.
        """
        # Rule 1: Verify full alignment
        if not alert.is_full_alignment():
            logger.warning(f"❌ Screener not fully aligned: {alert.count}/9")
            return False
            
        # Rule 2: Check if symbol is tradeable
        if not is_symbol_tradeable(alert.symbol):
            logger.warning(f"❌ Symbol not tradeable: {alert.symbol}")
            return False
            
        return True
        
    def execute_entry(self, alert: ScreenerFullAlert) -> dict:
        """
        Execute screener full entry
        
        Note: This is a high-confidence signal, so we use larger position size.
        """
        # Screener Full gets 1.5x lot multiplier (high confidence)
        lot_multiplier = 1.5
        
        return {
            "action": "ENTRY",
            "direction": alert.direction,
            "symbol": alert.symbol,
            "lot_multiplier": lot_multiplier,
            "confidence": 100,
            "reason": f"Screener Full: All 9 indicators aligned {alert.direction}"
        }
```

### 7.2 Position Sizing

```python
def calculate_screener_full_lots(base_lot: float, tf: str) -> float:
    """
    Calculate lot size for screener full signal
    
    Screener Full is high confidence, so we use larger positions
    but still respect timeframe-based scaling.
    """
    # Base multiplier for screener full
    screener_multiplier = 1.5
    
    # Timeframe scaling
    tf_multipliers = {
        "1": 0.5,   # 1M: Half size (noise risk)
        "5": 0.75,  # 5M: 75% size
        "15": 1.0,  # 15M: Full size
        "60": 1.25, # 1H: 125% size (swing)
        "240": 1.5  # 4H: 150% size (position)
    }
    
    tf_mult = tf_multipliers.get(tf, 1.0)
    
    return base_lot * screener_multiplier * tf_mult
```

---

## 8. ROUTING RULES

### 8.1 Order Routing Matrix

| Alert Type | Timeframe | Order Type | Lot Multiplier | Notes |
|------------|-----------|------------|----------------|-------|
| SCREENER_FULL_BULLISH | 1M | ORDER B ONLY | 0.75x | High noise risk |
| SCREENER_FULL_BULLISH | 5M | DUAL ORDERS | 1.125x | Momentum trade |
| SCREENER_FULL_BULLISH | 15M | ORDER A ONLY | 1.5x | Standard entry |
| SCREENER_FULL_BULLISH | 1H | ORDER A ONLY | 1.875x | Swing trade |
| SCREENER_FULL_BEARISH | 1M | ORDER B ONLY | 0.75x | High noise risk |
| SCREENER_FULL_BEARISH | 5M | DUAL ORDERS | 1.125x | Momentum trade |
| SCREENER_FULL_BEARISH | 15M | ORDER A ONLY | 1.5x | Standard entry |
| SCREENER_FULL_BEARISH | 1H | ORDER A ONLY | 1.875x | Swing trade |

### 8.2 Risk Management

```python
def calculate_screener_full_sl(alert: ScreenerFullAlert) -> float:
    """
    Calculate stop loss for screener full signal
    
    Since all indicators are aligned, we can use tighter stops
    because the signal is high confidence.
    """
    atr = get_atr(alert.symbol, alert.tf)
    
    # Tighter SL for high-confidence signal (1.2x ATR vs normal 1.5x)
    sl_distance = atr * 1.2
    
    if alert.is_bullish:
        sl_price = get_current_price(alert.symbol) - sl_distance
    else:
        sl_price = get_current_price(alert.symbol) + sl_distance
        
    return sl_price

def calculate_screener_full_tp(alert: ScreenerFullAlert) -> tuple:
    """
    Calculate take profit levels for screener full signal
    
    Extended targets for high-confidence signal.
    """
    atr = get_atr(alert.symbol, alert.tf)
    price = get_current_price(alert.symbol)
    
    # Extended TP levels (2x, 3x, 4x ATR)
    if alert.is_bullish:
        tp1 = price + (atr * 2.0)
        tp2 = price + (atr * 3.0)
        tp3 = price + (atr * 4.0)
    else:
        tp1 = price - (atr * 2.0)
        tp2 = price - (atr * 3.0)
        tp3 = price - (atr * 4.0)
        
    return tp1, tp2, tp3
```

---

## 9. SCENARIO SIMULATIONS

### Scenario 1: 15M Full Bullish Signal

**Alert:** `SCREENER_FULL_BULLISH|EURUSD|15|9|MACD,STOCH,VORTEX,MOMENTUM,RSI,PSAR,DMI,MFI,FISHER`

**Analysis:**
- Symbol: EURUSD
- Timeframe: 15m
- All 9 indicators: BULLISH
- Confidence: 100

**Bot Action:**
1. Validate: Full alignment (9/9) ✅
2. Calculate lots: base_lot * 1.5 * 1.0 = 1.5x
3. Execute: BUY order via ORDER A
4. Set SL: Current price - (ATR * 1.2)
5. Set TP1/TP2/TP3: +2x/+3x/+4x ATR
6. Log: "✅ Screener Full Bullish: EURUSD BUY @ 1.08500 (9/9 indicators)"

### Scenario 2: 1M Full Bearish Signal (Reduced Size)

**Alert:** `SCREENER_FULL_BEARISH|GBPUSD|1|9|MACD,STOCH,VORTEX,MOMENTUM,RSI,PSAR,DMI,MFI,FISHER`

**Analysis:**
- Symbol: GBPUSD
- Timeframe: 1m (high noise)
- All 9 indicators: BEARISH
- Confidence: 100

**Bot Action:**
1. Validate: Full alignment (9/9) ✅
2. Calculate lots: base_lot * 1.5 * 0.5 = 0.75x (reduced for 1M)
3. Execute: SELL order via ORDER B ONLY
4. Set SL: Current price + (ATR * 1.2)
5. Set TP1/TP2/TP3: -2x/-3x/-4x ATR
6. Log: "✅ Screener Full Bearish: GBPUSD SELL @ 1.26500 (9/9 indicators, 1M reduced)"

### Scenario 3: Partial Alignment (Rejected)

**Alert:** `SCREENER_FULL_BULLISH|USDJPY|15|8|MACD,STOCH,VORTEX,MOMENTUM,RSI,PSAR,DMI,MFI`

**Analysis:**
- Count: 8 (not 9)
- Missing: FISHER

**Bot Action:**
1. Validate: Full alignment (8/9) ❌
2. Result: **NO ENTRY** - Not a true "Full" signal
3. Log: "❌ Screener not fully aligned: 8/9 indicators"

---

## 10. INTEGRATION WITH OTHER SIGNALS

### 10.1 Priority Over Other Signals

Screener Full signals have the highest priority:

```python
def get_signal_priority(alert_type: str) -> int:
    """
    Return signal priority (higher = more important)
    """
    priorities = {
        "SCREENER_FULL_BULLISH": 100,
        "SCREENER_FULL_BEARISH": 100,
        "BULLISH_ENTRY": 80,
        "BEARISH_ENTRY": 80,
        "TRENDLINE_BULLISH_BREAK": 70,
        "TRENDLINE_BEARISH_BREAK": 70,
        "BREAKOUT": 60,
        "BREAKDOWN": 60,
    }
    return priorities.get(alert_type, 50)
```

### 10.2 Conflict Resolution

If Screener Full conflicts with other signals:

```python
def resolve_signal_conflict(signals: list) -> dict:
    """
    Resolve conflicts between multiple signals
    
    Screener Full always wins due to highest confidence.
    """
    # Sort by priority
    sorted_signals = sorted(signals, key=lambda s: get_signal_priority(s.type), reverse=True)
    
    # Return highest priority signal
    return sorted_signals[0]
```

---

## 11. STATE MANAGEMENT

```python
class ScreenerFullState:
    """
    Track screener full signals for analysis
    """
    
    def __init__(self):
        self.last_full_signal = {}  # symbol_tf -> last signal
        self.signal_count = {}      # symbol_tf -> count today
        
    def record_signal(self, alert: ScreenerFullAlert):
        key = f"{alert.symbol}_{alert.tf}"
        self.last_full_signal[key] = {
            "alert": alert,
            "timestamp": datetime.now()
        }
        self.signal_count[key] = self.signal_count.get(key, 0) + 1
        
    def get_signal_frequency(self, symbol: str, tf: str) -> int:
        """
        Get how many screener full signals today
        
        Too many signals might indicate choppy market.
        """
        key = f"{symbol}_{tf}"
        return self.signal_count.get(key, 0)
        
    def is_signal_spam(self, symbol: str, tf: str) -> bool:
        """
        Check if too many signals (possible whipsaw)
        """
        return self.get_signal_frequency(symbol, tf) > 5
```

---

## 12. LOGGING AND MONITORING

```python
def log_screener_full_signal(alert: ScreenerFullAlert, action: str):
    """
    Log screener full signal for monitoring
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": alert.type,
        "symbol": alert.symbol,
        "tf": alert.tf,
        "direction": alert.direction,
        "indicators": alert.indicators,
        "action": action,
        "confidence": 100
    }
    
    logger.info(f"🔥 SCREENER FULL: {alert.symbol} {alert.direction} on {alert.tf}m")
    logger.info(f"   Indicators: {', '.join(alert.indicators)}")
    logger.info(f"   Action: {action}")
    
    # Store for analysis
    store_signal_log(log_entry)
```

---

**STATUS: DEFINED & READY FOR IMPLEMENTATION**
