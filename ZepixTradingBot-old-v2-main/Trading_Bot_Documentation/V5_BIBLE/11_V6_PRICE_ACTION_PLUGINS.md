# V6 PRICE ACTION PLUGINS

**Files:**
- `src/logic_plugins/v6_price_action_1m/plugin.py` - 1-minute scalping
- `src/logic_plugins/v6_price_action_5m/plugin.py` (524 lines) - 5-minute momentum
- `src/logic_plugins/v6_price_action_15m/plugin.py` - 15-minute swing
- `src/logic_plugins/v6_price_action_1h/plugin.py` - 1-hour position

**Purpose:** V6 Price Action plugins for multi-timeframe trading

---

## OVERVIEW

The V6 Price Action plugins implement timeframe-specific trading strategies based on price action analysis. Each plugin is optimized for its timeframe with specific entry filters, risk parameters, and alignment requirements.

### Plugin Comparison

| Plugin | Timeframe | Type | Risk Multiplier | Alignment Required |
|--------|-----------|------|-----------------|-------------------|
| V6 1M | 1 minute | Scalping | 0.5x | 5M alignment |
| V6 5M | 5 minutes | Momentum | 1.0x | 15M alignment |
| V6 15M | 15 minutes | Swing | 1.5x | 1H alignment |
| V6 1H | 1 hour | Position | 2.0x | 4H alignment |

---

## V6 5-MINUTE MOMENTUM PLUGIN

### Class Definition (Lines 27-72)

```python
class V6PriceAction5mPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    V6 5-Minute Momentum Plugin
    
    Strategy Profile:
    - Type: Momentum Trading
    - Goal: Catch intraday breakouts and rapid moves
    - Risk Multiplier: 1.0x
    - Order Routing: DUAL ORDERS (Order A + Order B)
    
    Entry Filters:
    - ADX >= 25 (need proven momentum)
    - Confidence >= 70 (standard threshold)
    - 15M Alignment required (must align with immediate higher TF)
    - Trend Pulse alignment checked
    """
```

### Initialization (Lines 74-130)

```python
def __init__(self, plugin_id: str, config: Dict[str, Any], service_api=None):
    super().__init__(plugin_id, config, service_api)
    
    self.plugin_id = plugin_id
    self.config = config
    self.service_api = service_api
    
    # Strategy parameters
    self.timeframe = "5m"
    self.strategy_type = "momentum"
    self.risk_multiplier = 1.0
    
    # Entry filters
    self.adx_threshold = 25
    self.confidence_threshold = 70
    self.require_15m_alignment = True
    
    # Supported strategies
    self.supported_strategies = ["V6_PRICE_ACTION", "V6_5M"]
    self.supported_timeframes = ["5m"]
    
    # Plugin metadata
    self._metadata = {
        "version": "6.0.0",
        "author": "Zepix Team",
        "description": "V6 5-Minute Momentum Plugin",
        "timeframe": "5m",
        "strategy_type": "momentum"
    }
```

### Process Entry Signal (Lines 132-250)

```python
async def process_entry_signal(self, alert) -> Dict[str, Any]:
    """
    Process V6 5M entry signal.
    
    Entry flow:
    1. Validate ADX >= 25
    2. Validate Confidence >= 70
    3. Check 15M alignment
    4. Check Trend Pulse alignment
    5. Calculate lot size with 1.0x multiplier
    6. Create dual orders
    
    Args:
        alert: Alert data
        
    Returns:
        dict: Execution result
    """
    result = {
        "status": "pending",
        "action": "entry",
        "order_a_id": None,
        "order_b_id": None
    }
    
    try:
        # Extract alert data
        symbol = alert.get("ticker") if isinstance(alert, dict) else alert.ticker
        direction = alert.get("signal") if isinstance(alert, dict) else alert.signal
        price = alert.get("price") if isinstance(alert, dict) else alert.price
        adx = alert.get("adx", 0) if isinstance(alert, dict) else getattr(alert, "adx", 0)
        confidence = alert.get("confidence", 0) if isinstance(alert, dict) else getattr(alert, "confidence", 0)
        
        # Filter 1: ADX check
        if adx < self.adx_threshold:
            result["status"] = "skipped"
            result["reason"] = f"ADX too low: {adx} < {self.adx_threshold}"
            return result
        
        # Filter 2: Confidence check
        if confidence < self.confidence_threshold:
            result["status"] = "skipped"
            result["reason"] = f"Confidence too low: {confidence} < {self.confidence_threshold}"
            return result
        
        # Filter 3: 15M alignment check
        if self.require_15m_alignment:
            is_aligned = await self._check_15m_alignment(symbol, direction)
            if not is_aligned:
                result["status"] = "skipped"
                result["reason"] = "15M alignment failed"
                return result
        
        # Filter 4: Trend Pulse alignment
        pulse_aligned = await self.service_api.check_pulse_alignment(symbol, direction)
        if not pulse_aligned:
            result["status"] = "skipped"
            result["reason"] = "Trend Pulse not aligned"
            return result
        
        # Calculate lot size with risk multiplier
        base_lot = await self.service_api.calculate_lot_size_async(
            plugin_id=self.plugin_id,
            symbol=symbol,
            sl_price=self._calculate_sl_price(symbol, direction, price),
            entry_price=price
        )
        lot_size = base_lot * self.risk_multiplier
        
        # Create dual orders
        order_a_config = self._get_order_a_config(symbol, direction, price, lot_size)
        order_b_config = self._get_order_b_config(symbol, direction, price, lot_size)
        
        dual_result = await self.service_api.create_dual_orders(
            signal={"symbol": symbol, "direction": direction, "price": price},
            order_a_config=order_a_config,
            order_b_config=order_b_config
        )
        
        result["order_a_id"] = dual_result.order_a_id
        result["order_b_id"] = dual_result.order_b_id
        result["status"] = "success"
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result
```

### 15M Alignment Check (Lines 252-300)

```python
async def _check_15m_alignment(self, symbol: str, direction: str) -> bool:
    """
    Check if 5M signal aligns with 15M trend.
    
    Alignment criteria:
    - 15M EMA alignment matches direction
    - 15M RSI supports direction
    - 15M MACD histogram supports direction
    
    Args:
        symbol: Trading symbol
        direction: Proposed direction
        
    Returns:
        bool: True if aligned
    """
    if not self.service_api:
        return True
    
    try:
        trend_data = await self.service_api.get_v3_trend(symbol, "15m")
        
        # Check EMA alignment
        ema_direction = trend_data.get("ema_direction", "")
        if ema_direction.lower() != direction.lower():
            return False
        
        # Check RSI
        rsi = trend_data.get("rsi", 50)
        if direction.lower() in ["buy", "bull"] and rsi < 45:
            return False
        if direction.lower() in ["sell", "bear"] and rsi > 55:
            return False
        
        # Check MACD
        macd = trend_data.get("macd_histogram", 0)
        if direction.lower() in ["buy", "bull"] and macd < 0:
            return False
        if direction.lower() in ["sell", "bear"] and macd > 0:
            return False
        
        return True
        
    except Exception as e:
        self.logger.warning(f"15M alignment check failed: {e}")
        return True
```

---

## V6 1-MINUTE SCALPING PLUGIN

### Strategy Profile

```python
class V6PriceAction1mPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    V6 1-Minute Scalping Plugin
    
    Strategy Profile:
    - Type: Scalping
    - Goal: Quick in-and-out trades on micro moves
    - Risk Multiplier: 0.5x (reduced risk for scalping)
    - Order Routing: SINGLE ORDER (no dual orders for scalping)
    
    Entry Filters:
    - ADX >= 20 (lower threshold for scalping)
    - Confidence >= 80 (higher confidence required)
    - 5M Alignment required
    - Spread check (must be low)
    """
```

### Key Differences from 5M

| Aspect | 1M Scalping | 5M Momentum |
|--------|-------------|-------------|
| Risk Multiplier | 0.5x | 1.0x |
| ADX Threshold | 20 | 25 |
| Confidence Threshold | 80 | 70 |
| Alignment Required | 5M | 15M |
| Order Type | Single | Dual |
| Spread Check | Required | Optional |

---

## V6 15-MINUTE SWING PLUGIN

### Strategy Profile

```python
class V6PriceAction15mPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    V6 15-Minute Swing Plugin
    
    Strategy Profile:
    - Type: Swing Trading
    - Goal: Capture medium-term moves
    - Risk Multiplier: 1.5x (increased for swing trades)
    - Order Routing: DUAL ORDERS
    
    Entry Filters:
    - ADX >= 25 (standard momentum)
    - Confidence >= 65 (slightly lower for swing)
    - 1H Alignment required
    - Support/Resistance check
    """
```

### Key Differences from 5M

| Aspect | 15M Swing | 5M Momentum |
|--------|-----------|-------------|
| Risk Multiplier | 1.5x | 1.0x |
| ADX Threshold | 25 | 25 |
| Confidence Threshold | 65 | 70 |
| Alignment Required | 1H | 15M |
| S/R Check | Required | Optional |
| Hold Time | Hours | Minutes |

---

## V6 1-HOUR POSITION PLUGIN

### Strategy Profile

```python
class V6PriceAction1hPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    V6 1-Hour Position Plugin
    
    Strategy Profile:
    - Type: Position Trading
    - Goal: Capture major trend moves
    - Risk Multiplier: 2.0x (maximum for position trades)
    - Order Routing: DUAL ORDERS
    
    Entry Filters:
    - ADX >= 30 (strong trend required)
    - Confidence >= 60 (lower threshold for position)
    - 4H Alignment required
    - Daily trend check
    """
```

### Key Differences from 5M

| Aspect | 1H Position | 5M Momentum |
|--------|-------------|-------------|
| Risk Multiplier | 2.0x | 1.0x |
| ADX Threshold | 30 | 25 |
| Confidence Threshold | 60 | 70 |
| Alignment Required | 4H | 15M |
| Daily Check | Required | Optional |
| Hold Time | Days | Minutes |

---

## TREND PULSE INTEGRATION

### Trend Pulse Manager

All V6 plugins integrate with the Trend Pulse system for multi-timeframe alignment:

```python
async def check_pulse_alignment(self, symbol: str, direction: str) -> bool:
    """
    Check alignment with V6 Trend Pulse.
    
    Trend Pulse aggregates:
    - 5M trend weight: 1x
    - 15M trend weight: 2x
    - 1H trend weight: 3x
    - 4H trend weight: 4x
    
    Direction must align with weighted average.
    """
    pulse_data = await self.service_api.get_trend_pulse(symbol)
    
    weighted_score = (
        pulse_data["5m_trend"] * 1 +
        pulse_data["15m_trend"] * 2 +
        pulse_data["1h_trend"] * 3 +
        pulse_data["4h_trend"] * 4
    )
    
    if direction.lower() in ["buy", "bull"]:
        return weighted_score > 0
    else:
        return weighted_score < 0
```

---

## SHADOW MODE TESTING

All V6 plugins support shadow mode for risk-free testing:

```python
async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process signal with shadow mode support"""
    
    # Check if in shadow mode
    if signal_data.get("shadow_mode", False):
        # Process but don't execute real trades
        result = await self._simulate_entry(signal_data)
        result["shadow"] = True
        return result
    
    # Normal execution
    return await self.process_entry_signal(signal_data)
```

---

## CONFIGURATION

### V6 Plugin Config

```python
{
    "plugins": {
        "v6_price_action_1m": {
            "enabled": true,
            "settings": {
                "adx_threshold": 20,
                "confidence_threshold": 80,
                "risk_multiplier": 0.5,
                "require_5m_alignment": true,
                "spread_check": true,
                "max_spread_pips": 2
            }
        },
        "v6_price_action_5m": {
            "enabled": true,
            "settings": {
                "adx_threshold": 25,
                "confidence_threshold": 70,
                "risk_multiplier": 1.0,
                "require_15m_alignment": true
            }
        },
        "v6_price_action_15m": {
            "enabled": true,
            "settings": {
                "adx_threshold": 25,
                "confidence_threshold": 65,
                "risk_multiplier": 1.5,
                "require_1h_alignment": true,
                "sr_check": true
            }
        },
        "v6_price_action_1h": {
            "enabled": true,
            "settings": {
                "adx_threshold": 30,
                "confidence_threshold": 60,
                "risk_multiplier": 2.0,
                "require_4h_alignment": true,
                "daily_trend_check": true
            }
        }
    }
}
```

---

## RELATED FILES

- `src/core/plugin_system/plugin_registry.py` - Plugin registration
- `src/core/plugin_system/service_api.py` - Service layer
- `src/managers/trend_pulse_manager.py` - Trend Pulse system
- `src/core/shadow_mode_manager.py` - Shadow mode testing
