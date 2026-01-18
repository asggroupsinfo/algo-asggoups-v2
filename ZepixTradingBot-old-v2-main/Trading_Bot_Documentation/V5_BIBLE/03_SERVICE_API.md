# SERVICE API

**File:** `src/core/plugin_system/service_api.py`  
**Lines:** 1716  
**Purpose:** Unified service layer providing single point of entry for all plugin operations

---

## OVERVIEW

The ServiceAPI is the facade layer that provides plugins with access to all core services. Plugins should ONLY interact with this class, never directly with MT5, RiskManager, or other managers.

### Key Principles

1. **Single Point of Entry:** All plugin operations go through ServiceAPI
2. **Abstraction:** Plugins don't need to know about underlying implementations
3. **Consistency:** Uniform interface across all services
4. **Safety:** Built-in validation and error handling

---

## CLASS STRUCTURE

### Definition (Lines 94-115)

```python
class ServiceAPI:
    """
    Unified Service API - Single point of entry for all plugin operations.
    
    This class acts as a facade over all core services, providing:
    - Order execution (V3 dual orders, V6 conditional orders)
    - Risk management (lot sizing, daily limits, ATR-based SL/TP)
    - Trend analysis (V3 4-pillar, V6 Trend Pulse)
    - Market data (spread, price, volatility)
    
    Plugins should ONLY interact with this class, never directly with
    MT5, RiskManager, or other managers.
    """
    
    def __init__(self, config: Dict[str, Any], mt5_client, db):
        self.config = config
        self.mt5_client = mt5_client
        self.db = db
        
        # Initialize services
        self._init_services()
```

### Service Initialization (Lines 120-180)

```python
    def _init_services(self):
        """Initialize all core services"""
        # Order Execution Service
        self.order_service = OrderExecutionService(
            self.config, self.mt5_client
        )
        
        # Risk Management Service
        self.risk_service = RiskManagementService(self.config)
        
        # Trend Management Service
        self.trend_service = TrendManagementService(
            self.config, self.mt5_client
        )
        
        # Market Data Service
        self.market_service = MarketDataService(
            self.config, self.mt5_client
        )
        
        # Re-entry Service
        self.reentry_service = ReentryService(self.config)
        
        # Dual Order Service
        self.dual_order_service = DualOrderService(
            self.config, self.mt5_client
        )
        
        # Profit Booking Service
        self.profit_booking_service = ProfitBookingService(
            self.config, self.mt5_client, self.db
        )
        
        # Autonomous Service
        self.autonomous_service = AutonomousService(self.config)
```

---

## ORDER EXECUTION METHODS

### Place Single Order A (Lines 200-280)

```python
async def place_single_order_a(
    self,
    plugin_id: str,
    symbol: str,
    direction: str,
    lot_size: float,
    sl_price: float,
    tp_price: float,
    comment: str = ""
) -> Optional[int]:
    """
    Place Order A (TP Trail) via MT5.
    
    Order A characteristics:
    - Uses V3 Smart SL with progressive trailing
    - Has TP target
    - Triggers SL Hunt on SL hit
    
    Args:
        plugin_id: ID of calling plugin
        symbol: Trading symbol
        direction: 'BUY' or 'SELL'
        lot_size: Position size
        sl_price: Stop loss price
        tp_price: Take profit price
        comment: Order comment
        
    Returns:
        int: Order ticket if successful, None otherwise
    """
    # Validate inputs
    if not self._validate_order_params(symbol, direction, lot_size, sl_price, tp_price):
        return None
    
    # Check risk limits
    if not await self.check_risk_limits(plugin_id, symbol, lot_size):
        return None
    
    # Place order
    ticket = await self.order_service.place_order(
        symbol=symbol,
        direction=direction,
        lot_size=lot_size,
        sl=sl_price,
        tp=tp_price,
        comment=f"{plugin_id}_order_a_{comment}"
    )
    
    if ticket:
        logger.info(f"[ServiceAPI] Order A placed: #{ticket} {symbol} {direction}")
    
    return ticket
```

### Place Single Order B (Lines 285-360)

```python
async def place_single_order_b(
    self,
    plugin_id: str,
    symbol: str,
    direction: str,
    lot_size: float,
    sl_price: float,
    tp_price: float,
    comment: str = ""
) -> Optional[int]:
    """
    Place Order B (Profit Trail) via MT5.
    
    Order B characteristics:
    - Uses fixed $10 risk SL
    - Creates profit booking chain
    - No TP target (uses profit booking)
    
    Args:
        plugin_id: ID of calling plugin
        symbol: Trading symbol
        direction: 'BUY' or 'SELL'
        lot_size: Position size
        sl_price: Stop loss price
        tp_price: Take profit price (for initial setup)
        comment: Order comment
        
    Returns:
        int: Order ticket if successful, None otherwise
    """
    # Validate inputs
    if not self._validate_order_params(symbol, direction, lot_size, sl_price, tp_price):
        return None
    
    # Check risk limits
    if not await self.check_risk_limits(plugin_id, symbol, lot_size):
        return None
    
    # Place order
    ticket = await self.order_service.place_order(
        symbol=symbol,
        direction=direction,
        lot_size=lot_size,
        sl=sl_price,
        tp=tp_price,
        comment=f"{plugin_id}_order_b_{comment}"
    )
    
    if ticket:
        logger.info(f"[ServiceAPI] Order B placed: #{ticket} {symbol} {direction}")
        
        # Create profit chain for Order B
        await self.profit_booking_service.create_chain(
            plugin_id=plugin_id,
            order_id=ticket,
            symbol=symbol,
            direction=direction
        )
    
    return ticket
```

### Create Dual Orders (Lines 365-450)

```python
async def create_dual_orders(
    self,
    signal: Dict[str, Any],
    order_a_config: OrderConfig,
    order_b_config: OrderConfig
) -> DualOrderResult:
    """
    Create both Order A and Order B for a signal.
    
    This is the recommended method for placing trades as it:
    - Handles both orders atomically
    - Creates profit chain for Order B
    - Tracks order relationships
    
    Args:
        signal: Trading signal data
        order_a_config: Configuration for Order A
        order_b_config: Configuration for Order B
        
    Returns:
        DualOrderResult: Result with both order IDs
    """
    result = DualOrderResult()
    
    # Place Order A
    ticket_a = await self.place_single_order_a(
        plugin_id=order_a_config.plugin_id,
        symbol=signal.get('symbol'),
        direction=signal.get('direction'),
        lot_size=order_a_config.lot_size,
        sl_price=order_a_config.sl_price,
        tp_price=order_a_config.tp_price,
        comment="dual_order_a"
    )
    
    if ticket_a:
        result.order_a_id = ticket_a
        result.order_a_placed = True
    
    # Place Order B (independent of Order A result)
    ticket_b = await self.place_single_order_b(
        plugin_id=order_b_config.plugin_id,
        symbol=signal.get('symbol'),
        direction=signal.get('direction'),
        lot_size=order_b_config.lot_size,
        sl_price=order_b_config.sl_price,
        tp_price=order_b_config.tp_price,
        comment="dual_order_b"
    )
    
    if ticket_b:
        result.order_b_id = ticket_b
        result.order_b_placed = True
    
    return result
```

### Close Positions (Lines 455-520)

```python
async def close_positions_by_direction(
    self,
    plugin_id: str,
    symbol: str,
    direction: str
) -> List[Dict[str, Any]]:
    """
    Close all positions for a symbol in a specific direction.
    
    Args:
        plugin_id: ID of calling plugin
        symbol: Trading symbol
        direction: Direction to close ('BUY' or 'SELL')
        
    Returns:
        list: List of closed position results
    """
    closed = []
    
    positions = self.mt5_client.get_positions_by_symbol(symbol)
    
    for pos in positions:
        if pos.direction == direction:
            result = await self.order_service.close_position(pos.ticket)
            if result:
                closed.append({
                    'ticket': pos.ticket,
                    'profit': result.get('profit', 0)
                })
    
    return closed
```

---

## RISK MANAGEMENT METHODS

### Calculate Lot Size (Lines 550-620)

```python
async def calculate_lot_size_async(
    self,
    plugin_id: str,
    symbol: str,
    sl_price: float,
    entry_price: float
) -> float:
    """
    Calculate appropriate lot size based on risk parameters.
    
    Uses:
    - Account balance
    - Risk percentage per trade
    - SL distance
    - Symbol pip value
    
    Args:
        plugin_id: ID of calling plugin
        symbol: Trading symbol
        sl_price: Stop loss price
        entry_price: Entry price
        
    Returns:
        float: Calculated lot size
    """
    return await self.risk_service.calculate_lot_size(
        symbol=symbol,
        sl_price=sl_price,
        entry_price=entry_price
    )

def calculate_lot_size(
    self,
    plugin_id: str,
    symbol: str,
    sl_price: float,
    entry_price: float
) -> float:
    """Synchronous version of calculate_lot_size_async"""
    return self.risk_service.calculate_lot_size_sync(
        symbol=symbol,
        sl_price=sl_price,
        entry_price=entry_price
    )
```

### Check Risk Limits (Lines 625-700)

```python
async def check_risk_limits(
    self,
    plugin_id: str,
    symbol: str,
    lot_size: float
) -> bool:
    """
    Check if trade passes all risk limits.
    
    Checks:
    - Daily loss limit
    - Lifetime loss limit
    - Max concurrent trades
    - Symbol exposure limit
    
    Args:
        plugin_id: ID of calling plugin
        symbol: Trading symbol
        lot_size: Proposed lot size
        
    Returns:
        bool: True if trade is allowed
    """
    return await self.risk_service.check_limits(
        symbol=symbol,
        lot_size=lot_size
    )
```

### Check Safety (Lines 705-750)

```python
async def check_safety(self, plugin_id: str) -> SafetyCheckResult:
    """
    Check if plugin operations are safe to proceed.
    
    Checks:
    - Daily recovery limits
    - Concurrent recovery limits
    - Profit protection thresholds
    
    Args:
        plugin_id: ID of calling plugin
        
    Returns:
        SafetyCheckResult: Result with allowed flag and reason
    """
    return await self.autonomous_service.check_safety(plugin_id)
```

---

## TREND ANALYSIS METHODS

### Check Pulse Alignment (Lines 800-860)

```python
async def check_pulse_alignment(
    self,
    symbol: str,
    direction: str
) -> bool:
    """
    Check if direction aligns with V6 Trend Pulse.
    
    Trend Pulse aggregates:
    - 5M trend
    - 15M trend
    - 1H trend
    - 4H trend
    
    Args:
        symbol: Trading symbol
        direction: Proposed direction
        
    Returns:
        bool: True if aligned
    """
    return await self.trend_service.check_pulse_alignment(
        symbol=symbol,
        direction=direction
    )
```

### Get V3 4-Pillar Trend (Lines 865-920)

```python
async def get_v3_trend(
    self,
    symbol: str,
    timeframe: str
) -> Dict[str, Any]:
    """
    Get V3 4-pillar trend analysis.
    
    4 Pillars:
    1. EMA alignment (8/21/50/200)
    2. RSI position
    3. MACD direction
    4. Volume confirmation
    
    Args:
        symbol: Trading symbol
        timeframe: Analysis timeframe
        
    Returns:
        dict: Trend analysis result
    """
    return await self.trend_service.get_v3_trend(
        symbol=symbol,
        timeframe=timeframe
    )
```

---

## MARKET DATA METHODS

### Get Current Price (Lines 950-980)

```python
def get_current_price(self, symbol: str) -> float:
    """
    Get current market price for symbol.
    
    Args:
        symbol: Trading symbol
        
    Returns:
        float: Current price (mid-point of bid/ask)
    """
    return self.market_service.get_current_price(symbol)
```

### Get Spread (Lines 985-1010)

```python
def get_spread(self, symbol: str) -> float:
    """
    Get current spread for symbol in pips.
    
    Args:
        symbol: Trading symbol
        
    Returns:
        float: Current spread in pips
    """
    return self.market_service.get_spread(symbol)
```

### Get ATR (Lines 1015-1050)

```python
async def get_atr(
    self,
    symbol: str,
    timeframe: str,
    period: int = 14
) -> float:
    """
    Get Average True Range for symbol.
    
    Args:
        symbol: Trading symbol
        timeframe: Calculation timeframe
        period: ATR period (default 14)
        
    Returns:
        float: ATR value
    """
    return await self.market_service.get_atr(
        symbol=symbol,
        timeframe=timeframe,
        period=period
    )
```

---

## RE-ENTRY METHODS

### Start Recovery (Lines 1100-1150)

```python
async def start_recovery(self, event: ReentryEvent) -> bool:
    """
    Start recovery process for a trade.
    
    Args:
        event: ReentryEvent with trade details
        
    Returns:
        bool: True if recovery started
    """
    return await self.reentry_service.start_recovery(event)
```

### Create Profit Chain (Lines 1155-1200)

```python
async def create_profit_chain(
    self,
    plugin_id: str,
    order_b_id: str,
    symbol: str,
    signal_type: str
) -> Optional[str]:
    """
    Create a new profit booking chain.
    
    Args:
        plugin_id: ID of calling plugin
        order_b_id: Order B ticket
        symbol: Trading symbol
        signal_type: Original signal type
        
    Returns:
        str: Chain ID if created
    """
    return await self.profit_booking_service.create_chain(
        plugin_id=plugin_id,
        order_id=order_b_id,
        symbol=symbol,
        direction=signal_type
    )
```

---

## TELEGRAM METHODS

### Send Notification (Lines 1250-1290)

```python
async def send_telegram_notification(
    self,
    notification_type: str,
    message: str,
    **kwargs
):
    """
    Send notification through Telegram system.
    
    Args:
        notification_type: Type of notification
        message: Notification message
        **kwargs: Additional arguments (order_a_id, order_b_id, etc.)
    """
    # This is typically called through TradingEngine
    # Plugins should use this for custom notifications
    pass
```

---

## VALIDATION METHODS

### Validate Order Parameters (Lines 1300-1312)

```python
def _validate_order_params(
    self,
    symbol: str,
    direction: str,
    lot_size: float,
    sl_price: float,
    tp_price: float
) -> bool:
    """
    Validate order parameters before execution.
    
    Checks:
    - Symbol is valid
    - Direction is valid
    - Lot size is positive
    - SL/TP prices are valid
    
    Returns:
        bool: True if all parameters are valid
    """
    if not symbol or symbol not in self.config.get('symbol_config', {}):
        return False
    
    if direction not in ['BUY', 'SELL', 'buy', 'sell']:
        return False
    
    if lot_size <= 0:
        return False
    
    if sl_price <= 0 or tp_price <= 0:
        return False
    
    return True
```

---

## USAGE EXAMPLE

### In Plugin

```python
class V6PriceAction5mPlugin(BaseLogicPlugin):
    
    async def process_entry_signal(self, alert) -> Dict[str, Any]:
        # Calculate lot size via ServiceAPI
        lot_size = await self.service_api.calculate_lot_size_async(
            plugin_id=self.plugin_id,
            symbol=alert.ticker,
            sl_price=alert.sl,
            entry_price=alert.price
        )
        
        # Check pulse alignment via ServiceAPI
        is_aligned = await self.service_api.check_pulse_alignment(
            symbol=alert.ticker,
            direction=alert.direction
        )
        
        if not is_aligned:
            return {"status": "skipped", "reason": "alignment_failed"}
        
        # Place dual orders via ServiceAPI
        result = await self.service_api.create_dual_orders(
            signal={'symbol': alert.ticker, 'direction': alert.direction},
            order_a_config=self._get_order_a_config(alert, lot_size),
            order_b_config=self._get_order_b_config(alert, lot_size)
        )
        
        return {
            "status": "success",
            "order_a_id": result.order_a_id,
            "order_b_id": result.order_b_id
        }
```

---

## RELATED FILES

- `src/core/services/order_execution_service.py` - Order execution
- `src/core/services/risk_management_service.py` - Risk management
- `src/core/services/trend_management_service.py` - Trend analysis
- `src/core/services/market_data_service.py` - Market data
- `src/core/services/reentry_service.py` - Re-entry operations
- `src/core/services/dual_order_service.py` - Dual order management
- `src/core/services/profit_booking_service.py` - Profit booking
- `src/core/services/autonomous_service.py` - Autonomous operations
