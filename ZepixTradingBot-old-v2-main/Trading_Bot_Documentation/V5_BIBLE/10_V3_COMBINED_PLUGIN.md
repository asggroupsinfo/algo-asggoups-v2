# V3 COMBINED LOGIC PLUGIN

**File:** `src/logic_plugins/v3_combined/plugin.py`  
**Lines:** 1951  
**Purpose:** V3 Combined Logic Plugin implementing all 12 V3 signal types

**Last Updated:** 2026-01-16 (MTF Parsing Fix + Score Validation)

---

## OVERVIEW

The V3 Combined Plugin handles all V3 signal types from the TradingView Pine Script indicator. It implements the complete V3 trading logic with dual order support, re-entry capabilities, and profit booking integration.

### CRITICAL: Pine Script Compatibility

The plugin now correctly handles TWO different MTF string formats from Pine Script:

**FORMAT A (5 values, REVERSE order) - Entry Signals:**
- Pine: `mtfString = htfTrend5,htfTrend4,htfTrend3,htfTrend2,htfTrend1`
- Meaning: `1D,4H,1H,15m,5m` (e.g., "1,1,-1,1,1")
- Index mapping: [0]=1D, [1]=4H, [2]=1H, [3]=15m, [4]=5m

**FORMAT B (6 values, FORWARD order) - Trend Pulse:**
- Pine: `currentTrendString = htfTrend0,htfTrend1,htfTrend2,htfTrend3,htfTrend4,htfTrend5`
- Meaning: `1m,5m,15m,1H,4H,1D` (e.g., "1,1,-1,1,1,1")
- Index mapping: [0]=1m, [1]=5m, [2]=15m, [3]=1H, [4]=4H, [5]=1D

### Supported Signal Types

| Category | Signal Types |
|----------|--------------|
| Entry (7) | Institutional_Launchpad, Liquidity_Trap, Momentum_Breakout, Mitigation_Test, Golden_Pocket_Flip, Screener_Full_Bullish, Screener_Full_Bearish |
| Exit (2) | Bullish_Exit, Bearish_Exit |
| Info (2) | Volatility_Squeeze, Trend_Pulse |
| Bonus (1) | Sideways_Breakout |

---

## CLASS STRUCTURE

### Definition (Lines 46-103)

```python
class V3CombinedPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor, 
                       IReentryCapable, IDualOrderCapable, IProfitBookingCapable, 
                       IAutonomousCapable, IDatabaseCapable):
    """
    V3 Combined Logic Plugin - Handles all 12 V3 signal types.
    
    This plugin migrates the V3 logic from trading_engine.py into a
    plugin-based architecture while maintaining 100% backward compatibility.
    
    Implements ISignalProcessor and IOrderExecutor interfaces for
    TradingEngine delegation system.
    
    Signal Types:
    - Entry (7): Institutional_Launchpad, Liquidity_Trap, Momentum_Breakout,
                 Mitigation_Test, Golden_Pocket_Flip, Screener_Full_Bullish/Bearish
    - Exit (2): Bullish_Exit, Bearish_Exit
    - Info (2): Volatility_Squeeze, Trend_Pulse
    - Bonus (1): Sideways_Breakout
    """
```

### Initialization (Lines 105-180)

```python
def __init__(self, plugin_id: str, config: Dict[str, Any], service_api=None):
    super().__init__(plugin_id, config, service_api)
    
    self.plugin_id = plugin_id
    self.config = config
    self.service_api = service_api
    
    # Supported strategies
    self.supported_strategies = ["V3_COMBINED", "V3"]
    self.supported_timeframes = ["5m", "15m", "1h"]
    
    # Signal type mappings
    self.entry_signals = [
        "Institutional_Launchpad", "Liquidity_Trap", "Momentum_Breakout",
        "Mitigation_Test", "Golden_Pocket_Flip", 
        "Screener_Full_Bullish", "Screener_Full_Bearish"
    ]
    
    self.exit_signals = ["Bullish_Exit", "Bearish_Exit"]
    
    self.info_signals = ["Volatility_Squeeze", "Trend_Pulse"]
    
    self.bonus_signals = ["Sideways_Breakout"]
    
    # Plugin metadata
    self._metadata = {
        "version": "3.0.0",
        "author": "Zepix Team",
        "description": "V3 Combined Logic Plugin",
        "capabilities": [
            "signal_processing", "order_execution", "reentry",
            "dual_orders", "profit_booking", "autonomous"
        ]
    }
```

---

## SIGNAL PROCESSING

### Process Signal (Lines 182-280)

```python
async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Main entry point for signal processing.
    Routes to appropriate handler based on signal type.
    
    Args:
        signal_data: Signal data from TradingEngine
        
    Returns:
        dict: Processing result or None
    """
    signal_type = signal_data.get("signal_type", "")
    
    # Determine signal category
    if signal_type in self.entry_signals:
        return await self.process_entry_signal(signal_data)
    elif signal_type in self.exit_signals:
        return await self.process_exit_signal(signal_data)
    elif signal_type in self.info_signals:
        return await self._process_info_signal(signal_data)
    elif signal_type in self.bonus_signals:
        return await self._process_bonus_signal(signal_data)
    else:
        self.logger.warning(f"Unknown signal type: {signal_type}")
        return {"status": "skipped", "reason": "unknown_signal_type"}
```

### Process Entry Signal (Lines 955-1028)

```python
async def process_entry_signal(self, alert) -> Dict[str, Any]:
    """
    Process entry signal and execute trade.
    
    Entry flow:
    1. Validate consensus score threshold (NEW)
    2. Extract alert data including Pine Script SL/TP (NEW)
    3. Check for aggressive reversal
    4. Route to appropriate logic (LOGIC1/2/3)
    5. Create dual orders (Order A + Order B)
    
    V3 entries BYPASS trend check because Pine Script has already
    performed 5-layer pre-validation. Re-entries and autonomous
    actions still REQUIRE trend check.
    
    Args:
        alert: Alert data (dict or typed alert object)
        
    Returns:
        dict: Execution result with status, order_id, etc.
    """
    result = {
        "status": "pending",
        "action": "entry",
        "order_a_id": None,
        "order_b_id": None,
        "chain_id": None,
        "profit_chain_id": None
    }
    
    try:
        # Extract alert data
        if isinstance(alert, dict):
            symbol = alert.get("ticker", alert.get("symbol"))
            direction = alert.get("signal", alert.get("direction"))
            price = alert.get("price", alert.get("entry"))
            signal_type = alert.get("signal_type", "")
        else:
            symbol = alert.ticker
            direction = alert.signal
            price = alert.price
            signal_type = alert.signal_type
        
        # Validate signal
        validation = await self._validate_entry_signal(symbol, direction, signal_type)
        if not validation["valid"]:
            result["status"] = "rejected"
            result["reason"] = validation["reason"]
            return result
        
        # Check 4-pillar trend alignment
        trend_aligned = await self._check_v3_trend_alignment(symbol, direction)
        if not trend_aligned:
            result["status"] = "skipped"
            result["reason"] = "trend_not_aligned"
            return result
        
        # Calculate lot size via ServiceAPI
        lot_size = await self.service_api.calculate_lot_size_async(
            plugin_id=self.plugin_id,
            symbol=symbol,
            sl_price=self._calculate_sl_price(symbol, direction, price),
            entry_price=price
        )
        
        # Create dual orders via ServiceAPI
        order_a_config = self._get_order_a_config(symbol, direction, price, lot_size)
        order_b_config = self._get_order_b_config(symbol, direction, price, lot_size)
        
        dual_result = await self.service_api.create_dual_orders(
            signal={"symbol": symbol, "direction": direction, "price": price},
            order_a_config=order_a_config,
            order_b_config=order_b_config
        )
        
        if dual_result.order_a_placed:
            result["order_a_id"] = dual_result.order_a_id
        
        if dual_result.order_b_placed:
            result["order_b_id"] = dual_result.order_b_id
            
            # Create profit chain for Order B
            profit_chain_id = await self.service_api.create_profit_chain(
                plugin_id=self.plugin_id,
                order_b_id=dual_result.order_b_id,
                symbol=symbol,
                signal_type=signal_type
            )
            result["profit_chain_id"] = profit_chain_id
        
        # Create re-entry chain
        if dual_result.order_a_placed:
            chain_id = await self._create_reentry_chain(
                dual_result.order_a_id, symbol, direction, price, lot_size
            )
            result["chain_id"] = chain_id
        
        result["status"] = "success"
        
    except Exception as e:
        self.logger.error(f"Entry signal processing error: {e}")
        result["status"] = "error"
        result["error"] = str(e)
    
    return result
```

### Process Exit Signal (Lines 452-550)

```python
async def process_exit_signal(self, alert) -> Dict[str, Any]:
    """
    Process exit signal and close trades.
    
    Exit flow:
    1. Identify positions to close
    2. Close positions in opposite direction
    3. Update re-entry chains
    4. Register for exit continuation (if enabled)
    
    Args:
        alert: Exit alert data
        
    Returns:
        dict: Exit result with closed positions
    """
    result = {
        "status": "pending",
        "action": "exit",
        "positions_closed": [],
        "total_profit": 0.0
    }
    
    try:
        # Extract alert data
        if isinstance(alert, dict):
            symbol = alert.get("ticker", alert.get("symbol"))
            signal_type = alert.get("signal_type", "")
        else:
            symbol = alert.ticker
            signal_type = alert.signal_type
        
        # Determine direction to close
        if signal_type == "Bullish_Exit":
            direction_to_close = "SELL"  # Close shorts on bullish exit
        else:  # Bearish_Exit
            direction_to_close = "BUY"  # Close longs on bearish exit
        
        # Close positions via ServiceAPI
        closed = await self.service_api.close_positions_by_direction(
            plugin_id=self.plugin_id,
            symbol=symbol,
            direction=direction_to_close
        )
        
        for pos in closed:
            result["positions_closed"].append(pos["ticket"])
            result["total_profit"] += pos.get("profit", 0)
        
        result["status"] = "success"
        
    except Exception as e:
        self.logger.error(f"Exit signal processing error: {e}")
        result["status"] = "error"
        result["error"] = str(e)
    
    return result
```

---

## V3 4-PILLAR TREND ANALYSIS

### Check Trend Alignment (Lines 600-700)

```python
async def _check_v3_trend_alignment(self, symbol: str, direction: str) -> bool:
    """
    Check if direction aligns with V3 4-pillar trend analysis.
    
    4 Pillars:
    1. EMA Alignment (8/21/50/200)
    2. RSI Position (above/below 50)
    3. MACD Direction (histogram positive/negative)
    4. Volume Confirmation (above average)
    
    Args:
        symbol: Trading symbol
        direction: Proposed direction
        
    Returns:
        bool: True if aligned with at least 3 pillars
    """
    if not self.service_api:
        return True  # Skip check if no service API
    
    try:
        trend_data = await self.service_api.get_v3_trend(symbol, "15m")
        
        pillars_aligned = 0
        
        # Pillar 1: EMA Alignment
        ema_aligned = trend_data.get("ema_aligned", False)
        ema_direction = trend_data.get("ema_direction", "")
        if ema_aligned and ema_direction.lower() == direction.lower():
            pillars_aligned += 1
        
        # Pillar 2: RSI Position
        rsi = trend_data.get("rsi", 50)
        if direction.lower() in ["buy", "bull"] and rsi > 50:
            pillars_aligned += 1
        elif direction.lower() in ["sell", "bear"] and rsi < 50:
            pillars_aligned += 1
        
        # Pillar 3: MACD Direction
        macd_histogram = trend_data.get("macd_histogram", 0)
        if direction.lower() in ["buy", "bull"] and macd_histogram > 0:
            pillars_aligned += 1
        elif direction.lower() in ["sell", "bear"] and macd_histogram < 0:
            pillars_aligned += 1
        
        # Pillar 4: Volume Confirmation
        volume_above_avg = trend_data.get("volume_above_average", False)
        if volume_above_avg:
            pillars_aligned += 1
        
        # Require at least 3 pillars aligned
        return pillars_aligned >= 3
        
    except Exception as e:
        self.logger.warning(f"Trend alignment check failed: {e}")
        return True  # Allow trade on error
```

---

## DUAL ORDER CONFIGURATION

### Get Order A Config (Lines 750-820)

```python
def _get_order_a_config(self, symbol: str, direction: str, 
                       price: float, lot_size: float) -> OrderConfig:
    """
    Get Order A (TP Trail) configuration.
    
    Order A characteristics:
    - V3 Smart SL with progressive trailing
    - TP target at 2:1 RR
    - Triggers SL Hunt on SL hit
    - Triggers TP Continuation on TP hit
    
    Args:
        symbol: Trading symbol
        direction: Trade direction
        price: Entry price
        lot_size: Position size
        
    Returns:
        OrderConfig: Order A configuration
    """
    # Calculate SL using V3 Smart SL
    sl_price = self._calculate_sl_price(symbol, direction, price)
    
    # Calculate TP at 2:1 RR
    sl_distance = abs(price - sl_price)
    rr_ratio = self.config.get("rr_ratio", 2.0)
    
    if direction.lower() in ["buy", "bull"]:
        tp_price = price + (sl_distance * rr_ratio)
    else:
        tp_price = price - (sl_distance * rr_ratio)
    
    return OrderConfig(
        plugin_id=self.plugin_id,
        order_type="TP_TRAIL",
        lot_size=lot_size,
        sl_price=sl_price,
        tp_price=tp_price,
        trailing_enabled=True,
        trailing_start_percent=50,
        trailing_step_percent=25
    )
```

### Get Order B Config (Lines 822-890)

```python
def _get_order_b_config(self, symbol: str, direction: str,
                       price: float, lot_size: float) -> OrderConfig:
    """
    Get Order B (Profit Trail) configuration.
    
    Order B characteristics:
    - Fixed $10 risk SL
    - No TP target (uses profit booking)
    - Creates profit booking chain
    - $7 minimum profit target per order
    
    Args:
        symbol: Trading symbol
        direction: Trade direction
        price: Entry price
        lot_size: Position size
        
    Returns:
        OrderConfig: Order B configuration
    """
    # Calculate SL for fixed $10 risk
    sl_price = self._calculate_fixed_risk_sl(symbol, direction, price, lot_size)
    
    # No TP for Order B - uses profit booking
    tp_price = None
    
    return OrderConfig(
        plugin_id=self.plugin_id,
        order_type="PROFIT_TRAIL",
        lot_size=lot_size,
        sl_price=sl_price,
        tp_price=tp_price,
        trailing_enabled=False,
        profit_booking_enabled=True,
        min_profit_target=7.0
    )
```

---

## RE-ENTRY CAPABILITY

### On SL Hit (Lines 950-1020)

```python
async def on_sl_hit(self, event: ReentryEvent) -> bool:
    """
    Handle SL hit event for potential recovery.
    
    Args:
        event: SL hit event data
        
    Returns:
        bool: True if recovery started
    """
    # Check safety limits
    safety_result = await self.service_api.check_safety(self.plugin_id)
    if not safety_result.allowed:
        self.logger.info(f"Recovery blocked: {safety_result.reason}")
        return False
    
    # Start recovery via ServiceAPI
    return await self.service_api.start_recovery(event)

async def on_tp_hit(self, event: ReentryEvent) -> bool:
    """
    Handle TP hit event for potential continuation.
    
    Args:
        event: TP hit event data
        
    Returns:
        bool: True if continuation started
    """
    # Check if continuation is enabled
    if not self.config.get("tp_continuation_enabled", True):
        return False
    
    # Register for continuation monitoring
    # (Handled by AutonomousSystemManager)
    return True
```

---

## CONFIGURATION

### V3 Plugin Config

```python
{
    "plugins": {
        "v3_combined": {
            "enabled": true,
            "settings": {
                "entry_conditions": {
                    "require_trend_alignment": true,
                    "min_pillars_aligned": 3,
                    "require_volume_confirmation": true
                },
                "risk_management": {
                    "rr_ratio": 2.0,
                    "sl_type": "V3_SMART_SL",
                    "trailing_enabled": true
                },
                "dual_orders": {
                    "enabled": true,
                    "order_b_fixed_risk": 10.0,
                    "order_b_profit_target": 7.0
                },
                "reentry": {
                    "sl_hunt_enabled": true,
                    "tp_continuation_enabled": true,
                    "max_chain_levels": 3
                }
            }
        }
    }
}
```

---

## SIGNAL TYPE DETAILS

### Entry Signals

| Signal | Description | Conditions |
|--------|-------------|------------|
| Institutional_Launchpad | Strong institutional buying/selling | Volume spike + EMA alignment |
| Liquidity_Trap | False breakout reversal | Wick rejection + volume |
| Momentum_Breakout | Trend continuation | ADX > 25 + MACD crossover |
| Mitigation_Test | Support/resistance retest | Price at key level + rejection |
| Golden_Pocket_Flip | Fibonacci retracement | 61.8% level + reversal |
| Screener_Full_Bullish | All indicators bullish | 4 pillars aligned bullish |
| Screener_Full_Bearish | All indicators bearish | 4 pillars aligned bearish |

### Exit Signals

| Signal | Description | Action |
|--------|-------------|--------|
| Bullish_Exit | Bullish reversal detected | Close short positions |
| Bearish_Exit | Bearish reversal detected | Close long positions |

---

---

## MTF (Multi-Timeframe) Parsing

### Dual Format Support

The V3 Combined Plugin now handles **TWO** different MTF string formats from Pine Script:

#### Format A: 5-Value Reverse Order (Entry Signals)
- **Source:** Pine Script Line 1702 (`mtfString`)
- **Format:** `"1D,4H,1H,15m,5m"` (5 values, REVERSE order)
- **Example:** `"1,1,-1,1,1"`
- **Extraction:**
  - Index [0] = 1D trend
  - Index [1] = 4H trend
  - Index [2] = 1H trend
  - Index [3] = 15m trend
  - Index [4] = 5m trend (ignored - noise)

#### Format B: 6-Value Forward Order (Trend Pulse)
- **Source:** Pine Script Lines 1090-1092 (`currentTrendString`)
- **Format:** `"1m,5m,15m,1H,4H,1D"` (6 values, FORWARD order)
- **Example:** `"0,1,1,-1,1,1"`
- **Extraction:**
  - Index [0] = 1m trend (ignored - noise)
  - Index [1] = 5m trend (ignored - noise)
  - Index [2] = 15m trend
  - Index [3] = 1H trend
  - Index [4] = 4H trend
  - Index [5] = 1D trend

#### 4-Pillar Extraction
Regardless of format, the plugin extracts the **4 stable pillars**:
- 15m trend
- 1H trend
- 4H trend
- 1D trend

**Implementation:** `v3_alert_models.py` Lines 135-180

**Verification:** Test file `v5_integrity_check.py` Tests 1A & 1B (PASS)

---

## Consensus Score Filtering

### Score Validation Logic

The plugin validates consensus scores (0-9 scale) before executing trades:

#### Minimum Thresholds
- **Global Minimum:** 5 (configurable)
- **Institutional Launchpad BUY:** 7 (special threshold)
- **All Other Signals:** 5

#### Validation Flow
1. Extract `consensus_score` from alert
2. Check signal-specific thresholds
3. Check global minimum threshold
4. REJECT if below threshold
5. ACCEPT if meets/exceeds threshold

#### Score Ranges
- **0-4:** Low confidence → **REJECTED**
- **5-6:** Medium confidence → **ACCEPTED**
- **7-9:** High confidence → **ACCEPTED** (priority)

**Implementation:** `plugin.py` `_validate_score_thresholds()` method

**Verification:** Test file `v5_integrity_check.py` Tests 2A, 2B, 2C (PASS)

---

## Enhanced Pine Script Fields

### Additional Data Capture

The `ZepixV3Alert` model now captures **7 additional Pine Script fields** for enhanced decision-making:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `fib_level` | float | Fibonacci retracement level | 0.618 |
| `adx_value` | float | ADX trend strength | 28.5 |
| `volume_profile` | string | Volume profile zone | "high", "low", "poc" |
| `order_block_strength` | float | Order block strength (0-100) | 85.0 |
| `liquidity_zone_distance` | float | Distance to liquidity zone (pips) | 15.5 |
| `smart_money_flow` | float | Smart money indicator (-100 to +100) | 75.0 |
| `institutional_footprint` | int | Institutional activity score (0-10) | 9 |

### Additional Context Fields
- `confidence`: Signal confidence level ("HIGH", "MEDIUM", "LOW")
- `full_alignment`: All indicators aligned (boolean)
- `reason`: Exit signal reason (string)
- `message`: Info signal message (string)
- `trend_labels`: Trend Pulse labels (string)

**Implementation:** `v3_alert_models.py` Lines 63-88

**Verification:** Test file `v5_integrity_check.py` Test 3B (PASS)

---

## Alert SL Price Enforcement

### Pine Script SL Override

When Pine Script provides an `sl_price` in the alert, the plugin **MUST** use it for Order A instead of internal calculation.

#### SL Priority
1. **First Priority:** Use `alert.sl_price` if provided
2. **Fallback:** Calculate SL based on logic config

#### Order A Configuration
```python
if alert.sl_price:
    # Use Pine Script SL
    order_a_sl = alert.sl_price
else:
    # Calculate internal SL
    order_a_sl = calculate_sl_from_config()
```

#### Order B Configuration
Order B **ALWAYS** uses fixed $10 risk SL, regardless of `alert.sl_price`.

**Implementation:** `plugin.py` `get_order_a_config()` method

**Verification:** Test file `v5_integrity_check.py` Test 3A (PASS)

---

## Signal Routing Matrix

### 2-Tier Routing System

The plugin routes signals to the appropriate logic handler using a 2-tier priority system:

#### Priority 1: Signal Type Overrides
These signals **ALWAYS** route to LOGIC3 (Swing), regardless of timeframe:
- `Screener_Full_Bullish`
- `Screener_Full_Bearish`
- `Golden_Pocket_Flip` (on 1H/4H only)

#### Priority 2: Timeframe-Based Routing
| Timeframe | Logic Handler | Strategy Type |
|-----------|---------------|---------------|
| 5m | combinedlogic-1 | Scalping |
| 15m | combinedlogic-2 | Intraday |
| 1H (60m) | combinedlogic-3 | Swing |
| 4H (240m) | combinedlogic-3 | Swing |
| 1D | combinedlogic-3 | Swing |

#### Default Routing
If timeframe doesn't match any rule: **combinedlogic-2** (Intraday)

**Implementation:** `plugin.py` `_route_logic_type()` method

**Verification:** Test file `v5_integrity_check.py` Tests 4A, 4B, 4C, 4D (PASS)

---

## Testing & Verification

### V5 Integrity Check Test Suite

**Test File:** `Trading_Bot/tests/v5_integrity_check.py`

#### Test Coverage
| Category | Tests | Status |
|----------|-------|--------|
| MTF Parsing | 4 | PASS |
| Score Filtering | 3 | PASS |
| Alert SL Enforcement | 2 | PASS |
| Logic Routing | 4 | PASS |
| **TOTAL** | **13** | **100% PASS** |

#### Running Tests
```bash
# Run all V5 integrity tests
python -m pytest Trading_Bot/tests/v5_integrity_check.py -v

# Expected output: 13 tests, 0 failures, 0 errors
```

#### Test Report
Full test results documented in:
- `Updates/v5_hybrid_plugin_architecture/V5_PLUGIN_AUDIT/08_FINAL_TEST_REPORT.md`

**Last Test Run:** 2026-01-16  
**Result:** 13/13 PASS (0.214s)

---

## RELATED FILES

- `src/core/trading_engine.py` - Delegates to this plugin
- `src/core/plugin_system/plugin_registry.py` - Plugin registration
- `src/core/plugin_system/service_api.py` - Service layer
- `src/managers/reentry_manager.py` - Re-entry chains
- `src/managers/profit_booking_manager.py` - Profit booking
- `src/v3_alert_models.py` - V3 Alert model with extra Pine fields
- `tests/v5_integrity_check.py` - V5 integrity test suite
