# 🔌 SERVICEAPI DOCUMENTATION - COMPLETE REFERENCE

**Created:** January 19, 2026  
**Bot Version:** V5 Hybrid Plugin Architecture  
**API Version:** 3.0.0  
**Scope:** All ServiceAPI endpoints, methods, and usage examples

---

## 📑 TABLE OF CONTENTS

1. [ServiceAPI Overview](#serviceapi-overview)
2. [Initialization](#initialization)
3. [Service Registration](#service-registration)
4. [Market Data Methods](#market-data-methods)
5. [Order Execution Methods](#order-execution-methods)
6. [Risk Management Methods](#risk-management-methods)
7. [Trend Management Methods](#trend-management-methods)
8. [Communication Methods](#communication-methods)
9. [Configuration Methods](#configuration-methods)
10. [Service Metrics](#service-metrics)

---

## 📊 SERVICEAPI OVERVIEW

### **What is ServiceAPI?**

ServiceAPI is the **UNIFIED FACADE** over all core services in the V5 Hybrid Plugin Architecture. It provides:

- **Single entry point** for all plugin operations
- **Plugin isolation** - plugins only talk to ServiceAPI
- **Service discovery** - find and call registered services
- **Metrics tracking** - monitor service performance
- **Health checks** - verify service availability

### **Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                         PLUGINS                                  │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │ V3 Combined   │  │  V6 15M       │  │  V6 30M       │       │
│  │ Logic 1/2/3   │  │  Plugin       │  │  Plugin       │       │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘       │
│          │                  │                  │                 │
│          └──────────────────┼──────────────────┘                │
│                             │                                    │
│                    ┌────────▼────────┐                          │
│                    │   ServiceAPI    │  ◄── Single Entry Point  │
│                    │    (Facade)     │                          │
│                    └────────┬────────┘                          │
│                             │                                    │
│    ┌───────────────────────┼───────────────────────┐            │
│    │                       │                       │            │
│    ▼                       ▼                       ▼            │
│ ┌──────────┐       ┌──────────┐           ┌──────────┐         │
│ │ MT5      │       │ Risk     │           │ Telegram │         │
│ │ Client   │       │ Manager  │           │ Bot      │         │
│ └──────────┘       └──────────┘           └──────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### **Why Use ServiceAPI?**

| Without ServiceAPI | With ServiceAPI |
|-------------------|-----------------|
| Plugin calls MT5 directly | Plugin calls api.get_price() |
| Plugin manages risk calculations | Plugin calls api.calculate_lot_size() |
| Plugin sends Telegram directly | Plugin calls api.send_notification() |
| Plugin reads config files | Plugin calls api.get_config() |
| No tracking | Metrics automatically tracked |
| No isolation | Plugin errors don't crash bot |

---

## 🚀 INITIALIZATION

### **Creating ServiceAPI Instance**

```python
# For plugins (with plugin_id)
from src.core.plugin_system.service_api import ServiceAPI

api = ServiceAPI(trading_engine, plugin_id="combinedlogic-1")

# For core bot (backward compatible)
api = ServiceAPI(trading_engine)  # plugin_id defaults to "core"
```

### **Factory Function**

```python
from src.core.plugin_system.service_api import create_service_api

api = create_service_api(trading_engine, plugin_id="v6_15m")
```

### **ServiceAPI Properties**

```python
# Get plugin ID
plugin_id = api.plugin_id  # "combinedlogic-1"

# Check if services available
if api.services_available:
    # Full service functionality
else:
    # Fallback mode
```

---

## 📋 SERVICE REGISTRATION

### **Register Service**

```python
def register_service(
    self,
    name: str,           # Service name
    service: Any,        # Service instance
    health_check: Callable = None  # Optional health check function
) -> None
```

**Example:**
```python
# Register re-entry service
api.register_service(
    name='reentry',
    service=reentry_service,
    health_check=lambda: reentry_service.is_healthy()
)
```

### **Get Service**

```python
def get_service(self, name: str) -> Optional[Any]
```

**Example:**
```python
reentry = api.get_service('reentry')
if reentry:
    await reentry.start_tp_continuation(trade_id)
```

### **Check Service Exists**

```python
def has_service(self, name: str) -> bool
```

**Example:**
```python
if api.has_service('profit_booking'):
    await api.profit_booking_service.create_chain(...)
```

### **List All Services**

```python
def list_services(self) -> List[str]
```

**Example:**
```python
services = api.list_services()
# ['reentry', 'dual_order', 'profit_booking', 'autonomous', 'telegram', 'database']
```

### **Discover Services**

```python
def discover_services(self) -> Dict[str, Dict[str, Any]]
```

**Example:**
```python
info = api.discover_services()
# {
#     'reentry': {'name': 'reentry', 'is_healthy': True, 'registered_at': '...'},
#     'dual_order': {'name': 'dual_order', 'is_healthy': True, ...},
# }
```

### **Convenience Properties**

```python
# Quick access to registered services
api.reentry_service         # Plan 03: Re-entry service
api.dual_order_service      # Plan 04: Dual order service
api.profit_booking_service  # Plan 05: Profit booking service
api.autonomous_service      # Plan 06: Autonomous service
api.telegram_service        # Plan 07: Telegram service
api.database_service        # Plan 09: Database service
```

---

## 📈 MARKET DATA METHODS

### **get_price()**

Get current price for a symbol.

```python
def get_price(self, symbol: str) -> float
```

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| symbol | str | Trading symbol (e.g., "XAUUSD") |

**Returns:** Current bid price or 0.0

**Example:**
```python
price = api.get_price("XAUUSD")
# 2050.50
```

---

### **get_symbol_info()**

Get symbol validation info.

```python
def get_symbol_info(self, symbol: str) -> Dict
```

**Returns:**
```python
{
    'name': 'XAUUSD',
    'digits': 2,
    'point': 0.01,
    'volume_min': 0.01,
    'volume_max': 100.0,
    'trade_mode': 'full',
    'visible': True
}
```

---

### **get_current_spread() (async)**

Get current spread in pips.

```python
async def get_current_spread(self, symbol: str) -> float
```

**Example:**
```python
spread = await api.get_current_spread("XAUUSD")
# 3.5 (pips)
```

---

### **check_spread_acceptable() (async)**

Check if spread is within acceptable range.

```python
async def check_spread_acceptable(
    self,
    symbol: str,
    max_spread_pips: float
) -> bool
```

**Example:**
```python
# Only trade if spread < 5 pips
if await api.check_spread_acceptable("XAUUSD", 5.0):
    await api.place_order_async(...)
```

---

### **get_current_price_data() (async)**

Get comprehensive price data.

```python
async def get_current_price_data(self, symbol: str) -> Optional[Dict[str, Any]]
```

**Returns:**
```python
{
    'bid': 2050.50,
    'ask': 2050.70,
    'spread_pips': 2.0,
    'timestamp': '2026-01-19T10:30:00'
}
```

---

### **get_volatility_state() (async)**

Get current volatility state.

```python
async def get_volatility_state(
    self,
    symbol: str,
    timeframe: str = '15m'
) -> Dict[str, Any]
```

**Returns:**
```python
{
    'state': 'MODERATE',  # 'HIGH', 'MODERATE', 'LOW'
    'atr': 15.5,
    'atr_percentage': 0.75
}
```

---

### **is_market_open() (async)**

Check if market is currently open.

```python
async def is_market_open(self, symbol: str) -> bool
```

**Example:**
```python
if await api.is_market_open("XAUUSD"):
    # Market is open, proceed with trading
    pass
```

---

### **get_atr() (async)**

Get ATR (Average True Range) for a symbol.

```python
async def get_atr(
    self,
    symbol: str,
    period: int = 14,
    timeframe: str = '1H'
) -> float
```

**Example:**
```python
atr = await api.get_atr("XAUUSD", period=14, timeframe='4H')
# 18.5 (ATR value)
```

---

## 📊 ACCOUNT METHODS

### **get_balance()**

Get current account balance.

```python
def get_balance(self) -> float
```

**Example:**
```python
balance = api.get_balance()
# 10532.50
```

---

### **get_equity()**

Get current account equity.

```python
def get_equity(self) -> float
```

**Example:**
```python
equity = api.get_equity()
# 10650.30
```

---

## 📝 ORDER EXECUTION METHODS

### **place_order() (sync, backward compatible)**

Place a new market order.

```python
def place_order(
    self,
    symbol: str,
    direction: str,      # "BUY" or "SELL"
    lot_size: float,
    sl_price: float = 0.0,
    tp_price: float = 0.0,
    comment: str = ""
) -> Optional[int]
```

**Returns:** MT5 ticket number or None

**Example:**
```python
ticket = api.place_order(
    symbol="XAUUSD",
    direction="BUY",
    lot_size=0.1,
    sl_price=2040.00,
    tp_price=2070.00,
    comment="LOGIC1_ENTRY"
)
```

---

### **place_order_async() (async)**

Place order asynchronously.

```python
async def place_order_async(
    self,
    symbol: str,
    direction: str,
    lot_size: float,
    entry_price: float = 0.0,
    sl_price: float = 0.0,
    tp_price: float = 0.0,
    comment: str = "",
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]
```

**Returns:**
```python
{"success": True, "trade_id": 123456789}
# or
{"success": False, "error": "Trading is paused"}
```

---

### **place_dual_orders_v3() (async)**

Place V3 hybrid SL dual order system.

```python
async def place_dual_orders_v3(
    self,
    symbol: str,
    direction: str,
    lot_size_total: float,    # Split 50/50
    order_a_sl: float,        # Smart SL for Order A
    order_a_tp: float,        # TP2 (extended) for Order A
    order_b_sl: float,        # Fixed $10 SL for Order B
    order_b_tp: float,        # TP1 (quick) for Order B
    logic_route: str          # 'LOGIC1', 'LOGIC2', 'LOGIC3'
) -> Tuple[Optional[int], Optional[int]]
```

**V3 Dual Order Characteristics:**
- Order A: Smart SL (from Pine Script), extended TP
- Order B: Fixed $10 SL (different from A), quick TP

**Returns:** (order_a_ticket, order_b_ticket)

**Example:**
```python
ticket_a, ticket_b = await api.place_dual_orders_v3(
    symbol="XAUUSD",
    direction="BUY",
    lot_size_total=0.2,  # Each order gets 0.1
    order_a_sl=2040.00,  # Smart SL
    order_a_tp=2080.00,  # TP2
    order_b_sl=2045.00,  # Fixed $10 SL
    order_b_tp=2060.00,  # TP1
    logic_route='LOGIC1'
)
```

---

### **place_dual_orders_v6() (async)**

Place V6 dual orders (same SL for both).

```python
async def place_dual_orders_v6(
    self,
    symbol: str,
    direction: str,
    lot_size_total: float,
    sl_price: float,          # Same SL for both
    tp1_price: float,         # Order B target (quick)
    tp2_price: float          # Order A target (extended)
) -> Tuple[Optional[int], Optional[int]]
```

**V6 Dual Order Characteristics:**
- Order A: Extended TP (TP2)
- Order B: Quick TP (TP1)
- Both orders have SAME SL

---

### **place_single_order_a() (async)**

Place Order A only (for 15M/1H V6 plugins).

```python
async def place_single_order_a(
    self,
    symbol: str,
    direction: str,
    lot_size: float,
    sl_price: float,
    tp_price: float,          # TP2
    comment: str = 'ORDER_A'
) -> Optional[int]
```

---

### **place_single_order_b() (async)**

Place Order B only (for 1M V6 plugin - scalping).

```python
async def place_single_order_b(
    self,
    symbol: str,
    direction: str,
    lot_size: float,
    sl_price: float,
    tp_price: float,          # TP1 (quick exit)
    comment: str = 'ORDER_B'
) -> Optional[int]
```

---

### **close_trade() (sync)**

Close an existing trade.

```python
def close_trade(self, trade_id: int) -> bool
```

---

### **close_position() (async)**

Close entire position with tracking.

```python
async def close_position(
    self,
    order_id: int,
    reason: str = 'Manual'
) -> Dict[str, Any]
```

**Returns:**
```python
{"success": True, "order_id": 123456789, "reason": "Manual"}
```

---

### **close_position_partial() (async)**

Close partial position (for TP1/TP2/TP3).

```python
async def close_position_partial(
    self,
    order_id: int,
    percentage: float    # 25.0 = close 25%
) -> Dict[str, Any]
```

**Returns:**
```python
{"success": True, "closed_volume": 0.025, "remaining_volume": 0.075}
```

---

### **close_positions() (async)**

Close multiple positions based on filters.

```python
async def close_positions(
    self,
    symbol: str = None,
    direction: str = None
) -> List[Dict[str, Any]]
```

**Example:**
```python
# Close all BUY positions for XAUUSD
results = await api.close_positions(symbol="XAUUSD", direction="buy")
```

---

### **close_positions_by_direction() (async)**

Close all positions for a symbol in a specific direction.

```python
async def close_positions_by_direction(
    self,
    symbol: str,
    direction: str
) -> Dict[str, Any]
```

**Use Case:** V3 aggressive reversal (close opposite positions)

---

### **modify_order() (sync)**

Modify SL/TP of a trade.

```python
def modify_order(
    self,
    trade_id: int,
    sl: float = 0.0,
    tp: float = 0.0
) -> bool
```

---

### **modify_order_async() (async)**

Modify existing order SL/TP asynchronously.

```python
async def modify_order_async(
    self,
    order_id: int,
    new_sl: float = None,    # None to keep current
    new_tp: float = None
) -> bool
```

---

### **get_open_trades()**

Get list of all open trades.

```python
def get_open_trades(self) -> List[Any]
```

---

### **get_plugin_orders() (async)**

Get all open orders for THIS plugin only.

```python
async def get_plugin_orders(self, symbol: str = None) -> List[Dict]
```

---

## 🛡️ RISK MANAGEMENT METHODS

### **calculate_lot_size() (sync)**

Calculate recommended lot size.

```python
def calculate_lot_size(
    self,
    symbol: str = None,
    stop_loss_pips: float = 0.0
) -> Dict[str, Any]
```

**Returns:**
```python
{"lot_size": 0.1, "balance": 10532.50}
```

---

### **calculate_lot_size_async() (async)**

Calculate safe lot size based on risk parameters.

```python
async def calculate_lot_size_async(
    self,
    symbol: str,
    risk_percentage: float,     # e.g., 1.5 = 1.5%
    stop_loss_pips: float,
    account_balance: float = None  # Auto-fetch if None
) -> float
```

**Example:**
```python
lot = await api.calculate_lot_size_async(
    symbol="XAUUSD",
    risk_percentage=1.5,
    stop_loss_pips=50
)
# 0.1
```

---

### **calculate_sl_price() (async)**

Calculate stop loss price based on risk parameters.

```python
async def calculate_sl_price(
    self,
    price: float,
    direction: str,
    lot_size: float
) -> Dict[str, Any]
```

**Returns:**
```python
{"sl_price": 2040.00, "sl_pips": 50}
```

---

### **calculate_atr_sl() (async)**

Calculate ATR-based dynamic stop loss.

```python
async def calculate_atr_sl(
    self,
    symbol: str,
    direction: str,
    entry_price: float,
    atr_value: float,
    atr_multiplier: float = 1.5
) -> float
```

---

### **calculate_atr_tp() (async)**

Calculate ATR-based dynamic take profit.

```python
async def calculate_atr_tp(
    self,
    symbol: str,
    direction: str,
    entry_price: float,
    atr_value: float,
    atr_multiplier: float = 2.0
) -> float
```

---

### **check_daily_limit() (async)**

Check if daily loss limit reached.

```python
async def check_daily_limit(self) -> Dict[str, Any]
```

**Returns:**
```python
{
    "can_trade": True,
    "daily_loss": 150.0,
    "daily_limit": 500.0
}
# or
{
    "can_trade": False,
    "daily_loss": 520.0,
    "daily_limit": 500.0
}
```

---

### **check_lifetime_limit() (async)**

Check if lifetime loss limit reached.

```python
async def check_lifetime_limit(self) -> Dict[str, Any]
```

---

### **check_risk_limits() (async)**

Check if trade meets all risk limits.

```python
async def check_risk_limits(
    self,
    symbol: str,
    lot_size: float,
    direction: str
) -> Dict[str, Any]
```

**Returns:**
```python
{
    'allowed': True,
    'violations': [],
    'daily_limit_ok': True,
    'lot_size_ok': True,
    'margin_ok': True
}
# or
{
    'allowed': False,
    'violations': ['Daily loss limit exceeded', 'Lot size exceeds max'],
    'daily_limit_ok': False,
    'lot_size_ok': False,
    'margin_ok': True
}
```

---

### **validate_trade_risk() (async)**

Validate if a trade meets risk requirements.

```python
async def validate_trade_risk(
    self,
    symbol: str,
    lot_size: float,
    sl_pips: float
) -> Dict[str, Any]
```

---

### **get_fixed_lot_size() (async)**

Get fixed lot size based on account tier.

```python
async def get_fixed_lot_size(
    self,
    account_balance: float = None
) -> float
```

---

### **get_spread() (async)**

Get current spread in pips (alias for get_current_spread).

```python
async def get_spread(self, symbol: str) -> float
```

---

## 📈 TREND MANAGEMENT METHODS

### **get_timeframe_trend() (async)**

Get V3 4-pillar MTF trend for a specific timeframe.

```python
async def get_timeframe_trend(
    self,
    symbol: str,
    timeframe: str    # '15m', '1h', '4h', '1d' ONLY
) -> Dict[str, Any]
```

**Returns:**
```python
{
    'direction': 'bullish',   # 'bullish', 'bearish', 'neutral'
    'value': 1,               # 1 (bullish), -1 (bearish), 0 (neutral)
    'timeframe': '15m'
}
```

---

### **get_mtf_trends() (async)**

Get ALL 4-pillar trends at once.

```python
async def get_mtf_trends(self, symbol: str) -> Dict[str, int]
```

**Returns:**
```python
{
    "15m": 1,   # Bullish
    "1h": 1,    # Bullish
    "4h": -1,   # Bearish
    "1d": 1     # Bullish
}
```

---

### **validate_v3_trend_alignment() (async)**

Check if signal aligns with V3 4-pillar system.

```python
async def validate_v3_trend_alignment(
    self,
    symbol: str,
    direction: str,
    min_aligned: int = 3    # Minimum pillars that must align
) -> bool
```

**Example:**
```python
# Check if BUY signal aligns with at least 3 of 4 pillars
if await api.validate_v3_trend_alignment("XAUUSD", "BUY", min_aligned=3):
    # Proceed with trade
    pass
```

---

### **check_logic_alignment() (async)**

Check if signal aligns with specific logic requirements.

```python
async def check_logic_alignment(
    self,
    symbol: str,
    logic: str,       # 'combinedlogic-1', 'combinedlogic-2', 'combinedlogic-3'
    direction: str
) -> Dict[str, Any]
```

**Returns:**
```python
{"aligned": True, "logic": "combinedlogic-1"}
```

---

### **update_trend_pulse() (async)**

Update market_trends table with Trend Pulse alert data (V6).

```python
async def update_trend_pulse(
    self,
    symbol: str,
    timeframe: str,
    bull_count: int,
    bear_count: int,
    market_state: str,
    changes: str
) -> None
```

---

### **get_market_state() (async)**

Get current market state for symbol (V6).

```python
async def get_market_state(self, symbol: str) -> str
```

**Returns:** 'TRENDING_BULLISH', 'TRENDING_BEARISH', 'SIDEWAYS', 'UNKNOWN'

---

### **check_pulse_alignment() (async)**

Check if signal aligns with Trend Pulse counts (V6).

```python
async def check_pulse_alignment(
    self,
    symbol: str,
    direction: str
) -> bool
```

---

### **get_pulse_data() (async)**

Get raw Trend Pulse counts.

```python
async def get_pulse_data(
    self,
    symbol: str,
    timeframe: str = None
) -> Dict[str, Dict[str, int]]
```

**Returns:**
```python
{
    "5": {"bull_count": 4, "bear_count": 2},
    "15": {"bull_count": 5, "bear_count": 1},
    "60": {"bull_count": 3, "bear_count": 3}
}
```

---

### **check_higher_tf_trend() (async)**

Check if signal aligns with higher timeframe trend.

```python
async def check_higher_tf_trend(
    self,
    symbol: str,
    signal_tf: str,     # "1", "5", "15", "60", "240"
    direction: str
) -> Dict[str, Any]
```

**V6 Timeframe Hierarchy:**
- 1M entry → Check 5M trend
- 5M entry → Check 15M trend
- 15M entry → Check 1H trend
- 1H entry → Check 4H trend
- 4H entry → No higher TF (approved by default)

**Returns:**
```python
{
    "aligned": True,
    "higher_tf": "60",
    "bull_count": 4,
    "bear_count": 2,
    "reason": "60m trend: Bull=4 > Bear=2"
}
```

---

### **update_trend() (async)**

Update trend for a specific symbol and timeframe.

```python
async def update_trend(
    self,
    symbol: str,
    timeframe: str,
    signal: str,    # 'bull', 'bear', 'buy', 'sell'
    mode: str = "AUTO"
) -> bool
```

---

## 📣 COMMUNICATION METHODS

### **send_notification() (sync)**

Send message via Telegram.

```python
def send_notification(
    self,
    message: str,
    priority: str = "normal"    # "normal", "high", "low"
)
```

---

### **send_notification_async() (async)**

Send message via Telegram asynchronously.

```python
async def send_notification_async(
    self,
    message: str,
    priority: str = "normal"
) -> bool
```

---

### **log()**

Log message with plugin context.

```python
def log(self, message: str, level: str = "info")
```

**Levels:** "info", "warning", "error", "debug"

**Example:**
```python
api.log("Signal received", level="info")
# Logs: [combinedlogic-1] Signal received
```

---

## ⚙️ CONFIGURATION METHODS

### **get_config()**

Get a configuration value.

```python
def get_config(self, key: str, default: Any = None) -> Any
```

**Example:**
```python
daily_limit = api.get_config('risk_config.daily_loss_limit', default=500)
```

---

### **get_plugin_config()**

Get plugin-specific configuration value.

```python
def get_plugin_config(self, key: str, default: Any = None) -> Any
```

**Example:**
```python
# Gets config from plugins.combinedlogic-1.risk_percentage
risk_pct = api.get_plugin_config('risk_percentage', default=1.5)
```

---

## 📊 SERVICE METRICS

### **Get All Metrics**

```python
def get_metrics(self) -> Dict[str, Dict[str, Any]]
```

**Returns:**
```python
{
    "reentry": {
        "calls": 150,
        "errors": 2,
        "avg_time_ms": 45.5,
        "error_rate": 1.33,
        "last_call": "2026-01-19T10:30:00",
        "last_error": None
    },
    "dual_order": {
        "calls": 80,
        "errors": 0,
        "avg_time_ms": 120.5,
        ...
    }
}
```

---

### **Get Service Metrics**

```python
def get_service_metrics(self, service_name: str) -> Optional[Dict[str, Any]]
```

---

### **Reset Metrics**

```python
def reset_metrics(self, service_name: str = None) -> None
```

**Example:**
```python
# Reset specific service
api.reset_metrics('reentry')

# Reset all services
api.reset_metrics()
```

---

### **Health Checks**

```python
async def check_health(self) -> Dict[str, bool]
```

**Returns:**
```python
{
    "reentry": True,
    "dual_order": True,
    "profit_booking": True,
    "autonomous": False,   # Unhealthy!
    "telegram": True
}
```

---

### **Get Service Status**

```python
def get_service_status(self) -> Dict[str, bool]
```

---

## 📝 COMPLETE USAGE EXAMPLE

```python
from src.core.plugin_system.service_api import ServiceAPI

class V3CombinedPlugin:
    def __init__(self, trading_engine):
        # Initialize with plugin_id
        self.api = ServiceAPI(trading_engine, plugin_id="combinedlogic-1")
    
    async def process_signal(self, signal: dict):
        """Process incoming signal"""
        symbol = signal['symbol']
        direction = signal['direction']
        
        # 1. Check market conditions
        if not await self.api.is_market_open(symbol):
            self.api.log("Market closed", level="warning")
            return {"success": False, "error": "Market closed"}
        
        # 2. Check spread
        if not await self.api.check_spread_acceptable(symbol, max_spread_pips=5.0):
            self.api.log("Spread too high", level="warning")
            return {"success": False, "error": "Spread too high"}
        
        # 3. Check risk limits
        risk_check = await self.api.check_risk_limits(symbol, 0.1, direction)
        if not risk_check['allowed']:
            self.api.log(f"Risk limit: {risk_check['violations']}", level="warning")
            return {"success": False, "error": str(risk_check['violations'])}
        
        # 4. Validate trend alignment
        if not await self.api.validate_v3_trend_alignment(symbol, direction, min_aligned=3):
            self.api.log("Trend misaligned", level="info")
            return {"success": False, "error": "Trend misaligned"}
        
        # 5. Calculate lot size
        lot = await self.api.calculate_lot_size_async(
            symbol=symbol,
            risk_percentage=1.5,
            stop_loss_pips=signal.get('sl_pips', 50)
        )
        
        # 6. Place dual orders
        ticket_a, ticket_b = await self.api.place_dual_orders_v3(
            symbol=symbol,
            direction=direction,
            lot_size_total=lot * 2,
            order_a_sl=signal['sl_price'],
            order_a_tp=signal['tp2_price'],
            order_b_sl=signal['fixed_sl_price'],
            order_b_tp=signal['tp1_price'],
            logic_route='LOGIC1'
        )
        
        if ticket_a and ticket_b:
            # 7. Send notification
            await self.api.send_notification_async(
                f"✅ V3 Dual Orders Placed\n"
                f"Symbol: {symbol}\n"
                f"Direction: {direction}\n"
                f"Order A: #{ticket_a}\n"
                f"Order B: #{ticket_b}"
            )
            
            return {"success": True, "tickets": [ticket_a, ticket_b]}
        
        return {"success": False, "error": "Order placement failed"}
```

---

**Document Created:** January 19, 2026  
**API Version:** 3.0.0  
**Total Methods:** 50+  
**Categories:** 9  
**Status:** COMPLETE ✅

---

## ⚠️ DEVELOPER NOTE - IMPORTANT

**Bot Source Code Location:**  
`C:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-New-v1\ZepixTradingBot-old-v2-main\Trading_Bot`

### Implementation Guidelines:

> ⚠️ **This is a Planning & Research Document - DO NOT Apply Blindly!**

**Implementation Process:**

1. **First, Complete Scan of the Bot**
   - Analyze the complete bot code
   - Understand the current architecture
   - Review existing implementations

2. **Map Ideas According to the Bot**
   - Check how the ideas given here will be implemented in the bot
   - Identify dependencies
   - Look for conflicts

3. **Create New Plan According to the Bot**
   - Create a new implementation plan according to the bot's current state
   - Adapt ideas that don't directly fit

4. **Make Improvements (Full Freedom)**
   - You have full freedom to improve the ideas
   - Use a better approach if available
   - Optimize according to the bot's architecture

5. **Then Implement**
   - Implement only after planning is complete

### Critical Rules:

| Rule | Description |
|------|-------------|
| ✅ **Idea Must Be Fully Implemented** | The core idea/concept must be fully implemented |
| ✅ **Improvements Allowed** | You can improve the implementation |
| ❌ **Idea Should Not Change** | The core concept of the idea must remain the same |
| ❌ **Do Not Apply Blindly** | First scan, plan, then implement |

**Remember:** This document provides ideas & possibilities - the final implementation will depend on the bot's actual architecture.

---

**END OF DOCUMENT**