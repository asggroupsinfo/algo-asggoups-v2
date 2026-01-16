# V6 PRICE ACTION PLUGINS - DEEP DIVE

## Source Files
- `src/logic_plugins/v6_price_action_1m/plugin.py`
- `src/logic_plugins/v6_price_action_5m/plugin.py` (524 lines)
- `src/logic_plugins/v6_price_action_15m/plugin.py`
- `src/logic_plugins/v6_price_action_1h/plugin.py`

## Overview
The V6 Price Action system consists of 4 timeframe-specific plugins, each optimized for different trading styles. All plugins share a common architecture but have unique entry filters and risk parameters.

## Class Definition (5M Example)
```python
class V6PriceAction5mPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    V6 5-Minute Momentum Plugin
    
    Strategy Profile:
    - Type: Momentum Trading
    - Goal: Catch intraday breakouts and rapid moves
    - Risk Multiplier: 1.0x
    - Order Routing: DUAL ORDERS (Order A + Order B)
    """
```

## Plugin Comparison Matrix

| Plugin | Timeframe | Strategy | ADX Threshold | Confidence | Alignment | Risk Multiplier |
|--------|-----------|----------|---------------|------------|-----------|-----------------|
| 1M | 1 minute | Scalping | >= 30 | >= 80 | 5M | 0.5x |
| 5M | 5 minutes | Momentum | >= 25 | >= 70 | 15M | 1.0x |
| 15M | 15 minutes | Swing | >= 20 | >= 65 | 1H | 1.2x |
| 1H | 1 hour | Position | >= 15 | >= 60 | 4H | 1.5x |

## 5M Momentum Plugin (Detailed)

### Class Constants
```python
class V6PriceAction5mPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    TIMEFRAME = "5"
    ORDER_ROUTING = "DUAL_ORDERS"
    RISK_MULTIPLIER = 1.0
    
    ADX_THRESHOLD = 25
    CONFIDENCE_THRESHOLD = 70
    REQUIRE_15M_ALIGNMENT = True
```

### Entry Validation
```python
async def _validate_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
    # Filter 1: ADX Check
    if alert.adx is None or alert.adx < self.ADX_THRESHOLD:
        return {"valid": False, "reason": "adx_low"}
    
    # Filter 2: Confidence Check
    if alert.conf_score < self.CONFIDENCE_THRESHOLD:
        return {"valid": False, "reason": "confidence_low"}
    
    # Filter 3: 15M Alignment Check
    if self.REQUIRE_15M_ALIGNMENT:
        is_aligned = await self.service_api.check_pulse_alignment(
            symbol=alert.ticker,
            direction=alert.direction
        )
        if not is_aligned:
            return {"valid": False, "reason": "alignment_failed"}
    
    return {"valid": True, "reason": None}
```

### Lot Size Calculation
```python
async def _calculate_lot_size(self, alert: ZepixV6Alert) -> float:
    base_lot = await self.service_api.calculate_lot_size_async(
        plugin_id=self.plugin_id,
        symbol=alert.ticker,
        sl_price=alert.sl,
        entry_price=alert.price
    )
    
    final_lot = base_lot * self.RISK_MULTIPLIER
    
    # Apply max lot limit
    max_lot = self.plugin_config.get("settings", {}).get(
        "risk_management", {}
    ).get("max_lot_size", 0.20)
    
    return min(final_lot, max_lot)
```

### Dual Order Placement
```python
async def _place_dual_orders(self, alert: ZepixV6Alert, lot_size: float) -> Dict:
    lot_a = lot_size * 0.5
    lot_b = lot_size * 0.5
    
    # Order A: Targets TP2 (larger move)
    ticket_a = await self.service_api.place_single_order_a(
        plugin_id=self.plugin_id,
        symbol=alert.ticker,
        direction=alert.direction,
        lot_size=lot_a,
        sl_price=alert.sl,
        tp_price=alert.tp2,
        comment=f"{self.plugin_id}_5m_order_a"
    )
    
    # Order B: Targets TP1 (quick profit)
    ticket_b = await self.service_api.place_single_order_b(
        plugin_id=self.plugin_id,
        symbol=alert.ticker,
        direction=alert.direction,
        lot_size=lot_b,
        sl_price=alert.sl,
        tp_price=alert.tp1,
        comment=f"{self.plugin_id}_5m_order_b"
    )
    
    return {
        "status": "success",
        "order_type": "DUAL_ORDERS",
        "ticket_a": ticket_a,
        "ticket_b": ticket_b
    }
```

## ZepixV6Alert Structure

The V6 plugins parse alerts using the `ZepixV6Alert` dataclass:

```python
@dataclass
class ZepixV6Alert:
    ticker: str          # Trading symbol (e.g., "XAUUSD")
    tf: str              # Timeframe (e.g., "5", "15", "60")
    type: str            # Alert type (e.g., "BULLISH_ENTRY")
    direction: str       # Trade direction ("BUY" or "SELL")
    price: float         # Entry price
    sl: float            # Stop loss price
    tp1: float           # Take profit 1 (conservative)
    tp2: float           # Take profit 2 (aggressive)
    adx: Optional[float] # ADX value for momentum filter
    conf_score: int      # Confidence score (0-100)
    trend_pulse: str     # Trend pulse state
```

## Signal Types

### Entry Signals
| Signal | Description |
|--------|-------------|
| `BULLISH_ENTRY` | Long entry signal |
| `BEARISH_ENTRY` | Short entry signal |

### Exit Signals
| Signal | Description |
|--------|-------------|
| `EXIT_BULLISH` | Close long positions |
| `EXIT_BEARISH` | Close short positions |

### Reversal Signals
| Signal | Description |
|--------|-------------|
| `REVERSAL_BULLISH` | Close shorts, open longs |
| `REVERSAL_BEARISH` | Close longs, open shorts |

## Entry Processing Flow

```
1. Receive Alert
   |
2. Parse to ZepixV6Alert
   |
3. Validate Timeframe
   |
4. Apply Entry Filters
   |-- ADX Check
   |-- Confidence Check
   |-- Alignment Check
   |
5. Calculate Lot Size
   |
6. Place Dual Orders
   |-- Order A (TP2)
   |-- Order B (TP1)
   |
7. Return Result
```

## Exit Processing

```python
async def process_exit_signal(self, alert) -> Dict[str, Any]:
    v6_alert = self._parse_alert(alert)
    
    # Validate timeframe
    if v6_alert.tf != self.TIMEFRAME:
        return self._skip_result("wrong_timeframe", f"Expected {self.TIMEFRAME}")
    
    # Determine close direction
    close_direction = "SELL" if "BULLISH" in v6_alert.type else "BUY"
    
    # Close positions via ServiceAPI
    result = await self.service_api.close_positions_by_direction(
        plugin_id=self.plugin_id,
        symbol=v6_alert.ticker,
        direction=close_direction
    )
    
    return {
        "status": "success",
        "action": "exit",
        "closed_positions": result
    }
```

## Reversal Processing

```python
async def process_reversal_signal(self, alert) -> Dict[str, Any]:
    v6_alert = self._parse_alert(alert)
    
    # Step 1: Exit existing positions
    exit_result = await self.process_exit_signal(alert)
    
    # Step 2: Enter new position
    entry_result = await self.process_entry_signal(alert)
    
    return {
        "status": "success",
        "action": "reversal",
        "exit_result": exit_result,
        "entry_result": entry_result
    }
```

## Shadow Mode

All V6 plugins support shadow mode for paper trading:

```python
async def _process_shadow_entry(self, alert: ZepixV6Alert) -> Dict:
    self.logger.info(
        f"[5M SHADOW] Entry: {alert.type} | {alert.ticker} {alert.direction} | "
        f"ADX={alert.adx} | Conf={alert.conf_score}"
    )
    
    return {
        "status": "shadow",
        "action": "entry",
        "order_type": "DUAL_ORDERS",
        "symbol": alert.ticker,
        "direction": alert.direction,
        "message": "Shadow mode - no real orders placed"
    }
```

## Statistics Tracking

Each plugin tracks execution statistics:

```python
self._stats = {
    "signals_received": 0,
    "signals_filtered": 0,
    "trades_placed": 0,
    "trades_closed": 0,
    "filter_reasons": {}  # Tracks why signals were filtered
}
```

## Configuration

### Plugin Config (config.json)
```json
{
    "v6_price_action_5m": {
        "enabled": true,
        "shadow_mode": true,
        "settings": {
            "entry_conditions": {
                "adx_threshold": 25,
                "confidence_threshold": 70,
                "require_15m_alignment": true
            },
            "risk_management": {
                "risk_multiplier": 1.0,
                "max_lot_size": 0.20
            }
        }
    }
}
```

## Interface Implementation

### ISignalProcessor
```python
def get_supported_strategies(self) -> List[str]:
    return ['V6_PRICE_ACTION', 'PRICE_ACTION', 'V6']

def get_supported_timeframes(self) -> List[str]:
    return ['5m', '5']

async def can_process_signal(self, signal_data: Dict) -> bool:
    strategy = signal_data.get('strategy', '')
    timeframe = signal_data.get('timeframe', signal_data.get('tf', ''))
    
    if strategy in self.get_supported_strategies():
        if timeframe in self.get_supported_timeframes():
            return True
    return False
```

### IOrderExecutor
```python
async def execute_order(self, order_data: Dict) -> Optional[Dict]:
    return await self._place_dual_orders(
        self._parse_alert(order_data),
        order_data.get('lot_size', 0.02)
    )

async def modify_order(self, order_id: str, modifications: Dict) -> bool:
    return await self.service_api.modify_order_async(order_id, modifications)

async def close_order(self, order_id: str, reason: str = "manual") -> bool:
    return await self.service_api.close_position(order_id)
```

## Key Differences Between Timeframes

### 1M Scalping Plugin
- Highest ADX requirement (30)
- Highest confidence requirement (80)
- Lowest risk multiplier (0.5x)
- Spread filter enabled
- Requires 5M alignment

### 5M Momentum Plugin
- Standard ADX requirement (25)
- Standard confidence requirement (70)
- Standard risk multiplier (1.0x)
- Requires 15M alignment

### 15M Swing Plugin
- Lower ADX requirement (20)
- Lower confidence requirement (65)
- Higher risk multiplier (1.2x)
- Requires 1H alignment

### 1H Position Plugin
- Lowest ADX requirement (15)
- Lowest confidence requirement (60)
- Highest risk multiplier (1.5x)
- Requires 4H alignment

## Version History
- v1.0.0 (2026-01-14): Initial V5 plugin implementation
- Migrated from monolithic V6 logic
- Added ServiceAPI integration
- Added shadow mode support
