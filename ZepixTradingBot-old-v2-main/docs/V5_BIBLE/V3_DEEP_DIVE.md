# V3 COMBINED LOGIC - DEEP DIVE

## Source File
`src/logic_plugins/v3_combined/plugin.py` (1836 lines)

## Overview
The V3 Combined Logic Plugin is the primary trading strategy implementation. It processes 12 distinct signal types from TradingView Pine Script alerts and executes trades through a sophisticated dual-order system with re-entry and profit booking capabilities.

## Class Definition
```python
class V3CombinedPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor, 
                       IReentryCapable, IDualOrderCapable, IProfitBookingCapable, 
                       IAutonomousCapable, IDatabaseCapable):
```

## Interfaces Implemented

| Interface | Purpose |
|-----------|---------|
| `ISignalProcessor` | Process incoming trading signals |
| `IOrderExecutor` | Execute, modify, and close orders |
| `IReentryCapable` | Handle SL Hunt and TP Continuation recovery |
| `IDualOrderCapable` | Manage Order A and Order B system |
| `IProfitBookingCapable` | Handle profit booking chains |
| `IAutonomousCapable` | Safety checks and Reverse Shield |
| `IDatabaseCapable` | Plugin-isolated database operations |

## Signal Types (12 Total)

### Entry Signals (7)
| Signal | Description | Trigger |
|--------|-------------|---------|
| `Institutional_Launchpad` | Large institutional move detected | High volume + momentum |
| `Liquidity_Trap` | Liquidity sweep reversal | Stop hunt pattern |
| `Momentum_Breakout` | Strong directional breakout | ADX + price action |
| `Mitigation_Test` | Order block retest | Support/resistance test |
| `Golden_Pocket_Flip` | Fibonacci retracement entry | 61.8-78.6% zone |
| `Screener_Full_Bullish` | All indicators bullish | Multi-indicator alignment |
| `Screener_Full_Bearish` | All indicators bearish | Multi-indicator alignment |

### Exit Signals (2)
| Signal | Description | Action |
|--------|-------------|--------|
| `Bullish_Exit` | Exit long positions | Close BUY trades |
| `Bearish_Exit` | Exit short positions | Close SELL trades |

### Info Signals (2)
| Signal | Description | Usage |
|--------|-------------|-------|
| `Volatility_Squeeze` | Low volatility detected | Prepare for breakout |
| `Trend_Pulse` | Trend strength update | MTF alignment check |

### Bonus Signal (1)
| Signal | Description | Trigger |
|--------|-------------|---------|
| `Sideways_Breakout` | Range breakout | Consolidation exit |

## Dual Order System

### Order A: TP_TRAIL (Smart SL)
```python
async def get_order_a_config(self, signal: Dict[str, Any]) -> OrderConfig:
    return OrderConfig(
        order_type=OrderType.ORDER_A,
        sl_type=SLType.V3_SMART_SL,
        lot_size=smart_lot,
        sl_pips=sl_pips,
        tp_pips=sl_pips * 2,  # 2:1 RR
        trailing_enabled=True,
        trailing_start_pips=sl_pips * 0.5,  # Start at 50% of SL
        trailing_step_pips=sl_pips * 0.25   # Trail in 25% steps
    )
```

**Characteristics:**
- Uses V3 Smart SL with progressive trailing
- Trailing starts at 50% of SL in profit
- Trails in 25% steps
- Has TP target (2:1 RR)

### Order B: PROFIT_TRAIL (Fixed Risk)
```python
async def get_order_b_config(self, signal: Dict[str, Any]) -> OrderConfig:
    return OrderConfig(
        order_type=OrderType.ORDER_B,
        sl_type=SLType.FIXED_RISK_SL,
        lot_size=smart_lot,
        sl_pips=0,  # Calculated based on risk
        tp_pips=None,  # No TP - uses profit booking
        trailing_enabled=False,
        risk_amount=10.0  # Fixed $10 risk
    )
```

**Characteristics:**
- Uses fixed $10 risk SL
- No TP target (uses profit booking chains)
- Creates profit booking chains for pyramid scaling

## Re-Entry System

### SL Hunt Recovery
When Order A hits SL, the plugin can trigger SL Hunt Recovery:

```python
async def on_sl_hit(self, event: ReentryEvent) -> bool:
    # Check if recovery is allowed
    if not await self.check_recovery_allowed(event.trade_id):
        return False
    
    # Check chain level
    chain_level = self.get_chain_level(event.trade_id)
    if chain_level >= self.get_max_chain_level():
        return False
    
    # Activate Reverse Shield
    await self.activate_reverse_shield(event.trade_id, event.direction)
    
    # Start recovery via service
    if self._reentry_service:
        return await self._reentry_service.start_sl_hunt_recovery(event)
```

### TP Continuation
When Order A hits TP, the plugin can continue the trend:

```python
async def on_tp_hit(self, event: ReentryEvent) -> bool:
    # Check if continuation is allowed
    if not await self.check_recovery_allowed(event.trade_id):
        return False
    
    # Start TP continuation
    if self._reentry_service:
        return await self._reentry_service.start_tp_continuation(event)
```

## Profit Booking System

### Chain Creation
When Order B is created, a profit chain is initialized:

```python
async def create_profit_chain(self, order_b_id: str, signal: Dict) -> Optional[ProfitChain]:
    chain = await self._profit_booking_service.create_chain(
        plugin_id=self.plugin_id,
        order_b_id=order_b_id,
        symbol=signal.get('symbol', ''),
        direction=signal.get('signal_type', '')
    )
    
    if chain:
        self._order_to_chain[order_b_id] = chain.chain_id
```

### Pyramid Levels
```python
PYRAMID_LEVELS = {
    0: {"orders": 1, "profit_target": 7},   # Level 0: 1 order, $7 target
    1: {"orders": 2, "profit_target": 14},  # Level 1: 2 orders, $14 target
    2: {"orders": 3, "profit_target": 21},  # Level 2: 3 orders, $21 target
    3: {"orders": 4, "profit_target": 28},  # Level 3: 4 orders, $28 target
}
```

## Signal Routing

### 2-Tier Routing Matrix
1. **Signal Override:** Certain signals bypass timeframe routing
2. **Timeframe Routing:** Signals routed based on timeframe

```python
def _route_to_logic(self, signal: Dict) -> str:
    signal_type = signal.get('signal_type', '')
    timeframe = signal.get('timeframe', '15m')
    
    # Signal override (aggressive signals)
    if self._is_aggressive_reversal_signal(signal_type):
        return 'LOGIC3'  # Aggressive logic
    
    # Timeframe routing
    if timeframe in ['1m', '5m']:
        return 'LOGIC1'  # Scalping logic
    elif timeframe in ['15m', '30m']:
        return 'LOGIC2'  # Swing logic
    else:
        return 'LOGIC3'  # Position logic
```

## ServiceAPI Integration

The plugin uses ServiceAPI for all operations:

```python
async def process_signal_via_service_api(self, signal: Dict) -> Optional[Dict]:
    # Check safety
    safety_check = await self._service_api.check_safety(self.plugin_id)
    if not safety_check.allowed:
        return None
    
    # Create dual orders
    result = await self._service_api.create_dual_orders(
        signal, order_a_config, order_b_config
    )
    
    # Create profit chain
    if result.order_b_id:
        await self._service_api.create_profit_chain(
            self.plugin_id, result.order_b_id, symbol, signal_type
        )
    
    # Send notification
    await self._service_api.send_telegram_notification(
        'trade_opened', f"Trade opened: {symbol} {signal_type}"
    )
```

## Shadow Mode Support

The plugin supports shadow mode for paper trading:

```python
async def _process_shadow_entry(self, alert) -> Dict:
    self.logger.info(f"[V3 SHADOW] Entry: {alert.signal_type} | {alert.symbol}")
    return {
        "status": "shadow",
        "action": "entry",
        "symbol": alert.symbol,
        "message": "Shadow mode - no real orders placed"
    }
```

## Configuration

### Plugin Config (config.json)
```json
{
    "v3_combined": {
        "enabled": true,
        "shadow_mode": false,
        "settings": {
            "entry_conditions": {
                "min_confidence": 70,
                "require_mtf_alignment": true
            },
            "risk_management": {
                "max_lot_size": 0.20,
                "risk_per_trade": 1.5
            }
        }
    }
}
```

## Key Methods Summary

| Method | Purpose | Lines |
|--------|---------|-------|
| `process_entry_signal()` | Handle entry signals | 955-1011 |
| `process_exit_signal()` | Handle exit signals | 1013-1042 |
| `process_reversal_signal()` | Handle reversals | 1044-1075 |
| `create_dual_orders()` | Create Order A + B | 267-313 |
| `on_sl_hit()` | Handle SL hit recovery | 1434-1513 |
| `on_tp_hit()` | Handle TP continuation | 1515-1560 |
| `create_profit_chain()` | Initialize profit chain | 453-490 |

## Database Isolation

Each plugin has its own isolated database:
```python
def get_database_config(self) -> DatabaseConfig:
    return DatabaseConfig(
        db_path=f"data/zepix_{self.plugin_id}.db",
        table_prefix=self.plugin_id,
        isolation_level="SERIALIZABLE"
    )
```

## Autonomous Safety

The plugin implements safety checks:

```python
async def check_recovery_allowed(self, trade_id: str) -> bool:
    if not self._autonomous_service:
        return True
    
    result = await self._autonomous_service.check_recovery_allowed(
        plugin_id=self.plugin_id,
        trade_id=trade_id
    )
    
    return result.allowed if result else True
```

## Version History
- v1.0.0 (2026-01-14): Initial V5 plugin implementation
- Migrated from trading_engine.py monolithic code
- Added ServiceAPI integration
- Added all interface implementations
