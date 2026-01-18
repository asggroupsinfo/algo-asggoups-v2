# V3 Combined Logic Plugin - Implementation Plan

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Plugin Implementation**: `src/logic_plugins/v3_combined/plugin.py`

---

## Implementation Overview

This document provides a step-by-step implementation guide for the V3 Combined Logic Plugin within the V5 Hybrid Plugin Architecture.

---

## Phase 1: Plugin Foundation

### 1.1 Create Plugin Directory Structure

```
src/logic_plugins/v3_combined/
├── __init__.py
├── plugin.py              # Main plugin class
├── signal_handlers.py     # Signal processing logic
├── order_manager.py       # Order execution logic
├── trend_validator.py     # MTF trend validation
└── config.json            # Plugin configuration
```

### 1.2 Implement Base Plugin Class

```python
# plugin.py
class V3CombinedPlugin(
    BaseLogicPlugin,
    ISignalProcessor,
    IOrderExecutor,
    IReentryCapable,
    IDualOrderCapable,
    IProfitBookingCapable,
    IAutonomousCapable,
    IDatabaseCapable
):
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        super().__init__(plugin_id, config, service_api)
        
        self._load_plugin_config()
        
        self.signal_handlers = V3SignalHandlers(self)
        self.order_manager = V3OrderManager(self, service_api)
        self.trend_validator = V3TrendValidator(self)
        
        self.shadow_mode = self.plugin_config.get("shadow_mode", False)
        
        # Signal type definitions
        self.entry_signals = [
            'Institutional_Launchpad', 'Liquidity_Trap', 'Momentum_Breakout',
            'Mitigation_Test', 'Golden_Pocket_Flip', 'Screener_Full_Bullish', 
            'Screener_Full_Bearish'
        ]
        self.exit_signals = ['Bullish_Exit', 'Bearish_Exit']
        self.info_signals = ['Volatility_Squeeze', 'Trend_Pulse']
```

### 1.3 Create Plugin Configuration

```json
{
  "plugin_id": "v3_combined",
  "enabled": true,
  "shadow_mode": false,
  "settings": {
    "bypass_trend_check_for_v3_entries": true,
    "mtf_pillars_only": ["15m", "1h", "4h", "1d"],
    "min_consensus_score": 5,
    "aggressive_reversal_signals": [
      "Liquidity_Trap_Reversal",
      "Screener_Full_Bullish",
      "Screener_Full_Bearish"
    ],
    "conservative_exit_signals": [
      "Bullish_Exit",
      "Bearish_Exit"
    ]
  },
  "risk_management": {
    "logic1_multiplier": 0.5,
    "logic2_multiplier": 1.0,
    "logic3_multiplier": 1.5,
    "max_position_multiplier": 1.0
  }
}
```

---

## Phase 2: Signal Processing Implementation

### 2.1 Implement ISignalProcessor Interface

```python
# Required methods
async def can_process_signal(self, signal_data: Dict[str, Any]) -> bool:
    """Check if this plugin can process the given signal."""
    signal_type = signal_data.get('type', '')
    return signal_type in ['entry_v3', 'exit_v3', 'trend_pulse_v3']

async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process the signal and return result."""
    alert_type = signal_data.get('type', '')
    
    if alert_type == 'entry_v3':
        return await self.process_entry_signal(signal_data)
    elif alert_type == 'exit_v3':
        return await self.process_exit_signal(signal_data)
    elif alert_type == 'trend_pulse_v3':
        return await self.process_trend_pulse(signal_data)
    
    return None
```

### 2.2 Implement Signal Handlers

```python
# signal_handlers.py
class V3SignalHandlers:
    def __init__(self, plugin):
        self.plugin = plugin
        self.logger = logging.getLogger(__name__)
    
    async def handle_entry_signal(self, alert: ZepixV3Alert) -> Dict[str, Any]:
        """Handle entry signals (1-4, 7, 9-10, 12)"""
        # Validate signal
        if not self._validate_entry(alert):
            return {"status": "rejected", "reason": "validation_failed"}
        
        # Route to appropriate logic
        logic = self.plugin._route_to_logic(alert)
        
        # Calculate lot size
        lot_size = self.plugin.get_smart_lot_size(
            self.plugin._get_base_lot(logic)
        )
        
        # Create dual orders
        result = await self.plugin.create_dual_orders({
            'symbol': alert.symbol,
            'direction': alert.direction,
            'logic': logic,
            'price': alert.price,
            'sl_price': alert.sl_price,
            'tp1_price': alert.tp1_price,
            'tp2_price': alert.tp2_price
        })
        
        return result
```

### 2.3 Implement Signal Routing

```python
def _route_to_logic(self, alert: ZepixV3Alert) -> str:
    """Route signal to appropriate logic based on type and timeframe."""
    # PRIORITY 1: Signal type overrides
    if alert.signal_type in ["Screener_Full_Bullish", "Screener_Full_Bearish"]:
        return "LOGIC3"  # Always swing
    
    if alert.signal_type == "Golden_Pocket_Flip" and alert.tf in ["60", "240"]:
        return "LOGIC3"
    
    # PRIORITY 2: Timeframe routing
    if alert.tf == "5":
        return "LOGIC1"  # Scalping
    elif alert.tf == "15":
        return "LOGIC2"  # Intraday (Default)
    elif alert.tf in ["60", "240"]:
        return "LOGIC3"  # Swing
    
    return "LOGIC2"  # DEFAULT
```

---

## Phase 3: Order Execution Implementation

### 3.1 Implement IDualOrderCapable Interface

```python
async def create_dual_orders(self, signal: Dict[str, Any]) -> DualOrderResult:
    """Create both Order A and Order B for a signal."""
    # Get configurations for both orders
    order_a_config = await self.get_order_a_config(signal)
    order_b_config = await self.get_order_b_config(signal)
    
    # Create dual orders via service
    result = await self._dual_order_service.create_dual_orders(
        signal, order_a_config, order_b_config
    )
    
    # Track orders locally
    if result.order_a_id:
        self._active_orders[result.order_a_id] = {
            'type': 'order_a',
            'signal': signal,
            'config': order_a_config
        }
    if result.order_b_id:
        self._active_orders[result.order_b_id] = {
            'type': 'order_b',
            'signal': signal,
            'config': order_b_config
        }
    
    # Create profit chain for Order B
    if result.order_b_id:
        await self.create_profit_chain(result.order_b_id, signal)
    
    return result
```

### 3.2 Implement Order A Configuration

```python
async def get_order_a_config(self, signal: Dict[str, Any], defined_sl: Optional[float] = None) -> OrderConfig:
    """Get Order A configuration (TP_TRAIL with V3 Smart SL)."""
    logic = signal.get('logic', 'LOGIC1')
    base_lot = self._get_base_lot(logic)
    smart_lot = self.get_smart_lot_size(base_lot)
    
    # USE PINE SL IF PROVIDED
    if defined_sl:
        sl_price = defined_sl
        current_price = signal.get('price', 0)
        sl_pips = abs(current_price - sl_price) * 10000
    else:
        sl_pips = self._get_sl_pips(signal.get('symbol', 'EURUSD'), logic)
        sl_price = None
    
    tp_pips = sl_pips * 2  # 2:1 RR for Order A
    
    return OrderConfig(
        order_type=OrderType.ORDER_A,
        sl_type=SLType.V3_SMART_SL,
        lot_size=smart_lot,
        sl_pips=sl_pips,
        sl_price=sl_price,
        tp_pips=tp_pips,
        trailing_enabled=True,
        trailing_start_pips=sl_pips * 0.5,
        trailing_step_pips=sl_pips * 0.25,
        plugin_id=self.plugin_id
    )
```

### 3.3 Implement Order B Configuration

```python
async def get_order_b_config(self, signal: Dict[str, Any]) -> OrderConfig:
    """Get Order B configuration (PROFIT_TRAIL with fixed $10 risk)."""
    logic = signal.get('logic', 'LOGIC1')
    base_lot = self._get_base_lot(logic)
    smart_lot = self.get_smart_lot_size(base_lot)
    
    return OrderConfig(
        order_type=OrderType.ORDER_B,
        sl_type=SLType.FIXED_RISK_SL,
        lot_size=smart_lot,
        sl_pips=0,  # Will be calculated based on risk
        tp_pips=None,  # No TP - uses profit booking
        trailing_enabled=False,
        risk_amount=10.0,  # Fixed $10 risk
        plugin_id=self.plugin_id
    )
```

---

## Phase 4: Re-Entry System Implementation

### 4.1 Implement IReentryCapable Interface

```python
async def on_sl_hit(self, event: ReentryEvent) -> bool:
    """Handle SL hit - trigger recovery if allowed."""
    # Check if recovery is allowed
    if not await self.check_recovery_allowed(event.trade_id):
        self.logger.info(f"Recovery not allowed for {event.trade_id}")
        return False
    
    # Check chain level
    chain_level = self.get_chain_level(event.trade_id)
    max_level = self.get_max_chain_level()
    
    if chain_level >= max_level:
        self.logger.info(f"Max chain level reached for {event.trade_id}")
        return False
    
    # Start recovery via service
    if self._reentry_service:
        return await self._reentry_service.start_recovery(event)
    
    return False
```

### 4.2 Implement Recovery Callback

```python
async def on_recovery_signal(self, event: ReentryEvent) -> Dict[str, Any]:
    """Handle recovery signal from ReentryService."""
    self.logger.info(f"Recovery signal received for {event.trade_id}")
    
    # Increment chain level
    new_level = self.get_chain_level(event.trade_id) + 1
    self._chain_levels[event.trade_id] = new_level
    
    # Create recovery order
    signal = {
        'symbol': event.symbol,
        'direction': event.direction,
        'price': event.entry_price,
        'is_recovery': True,
        'chain_level': new_level
    }
    
    result = await self.create_dual_orders(signal)
    
    return {
        'status': 'recovery_started',
        'chain_level': new_level,
        'order_a_id': result.order_a_id,
        'order_b_id': result.order_b_id
    }
```

---

## Phase 5: Profit Booking Implementation

### 5.1 Implement IProfitBookingCapable Interface

```python
async def create_profit_chain(
    self,
    order_b_id: str,
    signal: Dict[str, Any]
) -> Optional[ProfitChain]:
    """Create a new profit booking chain for Order B."""
    if not self._profit_booking_service:
        return None
    
    chain = await self._profit_booking_service.create_chain(
        plugin_id=self.plugin_id,
        order_id=order_b_id,
        symbol=signal.get('symbol', ''),
        signal_type=signal.get('signal_type', ''),
        initial_level=0
    )
    
    if chain:
        self._order_to_chain[order_b_id] = chain.chain_id
    
    return chain
```

### 5.2 Implement Profit Target Hit Handler

```python
async def on_profit_target_hit(
    self,
    chain_id: str,
    order_id: str
) -> BookingResult:
    """Handle profit target hit - book profit and create next level."""
    if not self._profit_booking_service:
        return BookingResult(error="Service not available")
    
    # Book profit at current level
    result = await self._profit_booking_service.book_profit(
        chain_id=chain_id,
        order_id=order_id
    )
    
    # Create next level order if chain continues
    if result.chain_continues:
        await self._create_level_orders(chain_id, result.next_level)
    
    return result
```

---

## Phase 6: Autonomous System Implementation

### 6.1 Implement IAutonomousCapable Interface

```python
async def check_recovery_allowed(self, trade_id: str) -> SafetyCheckResult:
    """Check if recovery is allowed for this trade."""
    if not self._autonomous_service:
        return SafetyCheckResult(allowed=True)
    
    return await self._autonomous_service.check_recovery_allowed(
        plugin_id=self.plugin_id,
        trade_id=trade_id
    )

async def activate_reverse_shield(
    self,
    trade_id: str,
    profit_amount: float
) -> ReverseShieldStatus:
    """Activate reverse shield to protect profits."""
    if not self._autonomous_service:
        return ReverseShieldStatus(active=False)
    
    status = await self._autonomous_service.activate_shield(
        plugin_id=self.plugin_id,
        trade_id=trade_id,
        profit_amount=profit_amount
    )
    
    self._active_shields[trade_id] = status
    return status
```

---

## Phase 7: ServiceAPI Integration

### 7.1 Implement ServiceAPI Injection

```python
def set_service_api(self, service_api) -> None:
    """Inject ServiceAPI - the UNIFIED way to access all core services."""
    self._service_api = service_api
    
    # Also set individual services for backward compatibility
    if service_api.reentry_service:
        self._reentry_service = service_api.reentry_service
        service_api.reentry_service.register_recovery_callback(
            self.plugin_id, self._on_recovery_callback
        )
    
    if service_api.dual_order_service:
        self._dual_order_service = service_api.dual_order_service
    
    if service_api.profit_booking_service:
        self._profit_booking_service = service_api.profit_booking_service
    
    if service_api.autonomous_service:
        self._autonomous_service = service_api.autonomous_service
```

### 7.2 Implement ServiceAPI-Based Processing

```python
async def process_signal_via_service_api(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process signal using ServiceAPI exclusively."""
    if not self._service_api:
        return None
    
    # Check safety via ServiceAPI
    safety_check = await self._service_api.check_safety(self.plugin_id)
    if safety_check and not safety_check.allowed:
        return None
    
    # Create dual orders via ServiceAPI
    order_a_config = await self.get_order_a_config(signal)
    order_b_config = await self.get_order_b_config(signal)
    
    result = await self._service_api.create_dual_orders(
        signal, order_a_config, order_b_config
    )
    
    # Create profit chain via ServiceAPI
    if result and result.order_b_id:
        await self._service_api.create_profit_chain(
            self.plugin_id,
            result.order_b_id,
            signal.get('symbol', ''),
            signal.get('signal_type', '')
        )
    
    # Send notification via ServiceAPI
    await self._service_api.send_telegram_notification(
        'trade_opened',
        f"Trade opened: {signal.get('symbol', '')} {signal.get('signal_type', '')}"
    )
    
    return {
        'status': 'executed',
        'order_a_id': result.order_a_id if result else None,
        'order_b_id': result.order_b_id if result else None
    }
```

---

## Phase 8: Testing & Validation

### 8.1 Unit Tests

```python
# tests/test_v3_plugin.py
class TestV3CombinedPlugin:
    def test_signal_routing(self):
        """Test signal-to-logic routing."""
        plugin = V3CombinedPlugin("v3_combined", {}, None)
        
        # Test Screener Full → LOGIC3
        alert = ZepixV3Alert(signal_type="Screener_Full_Bullish", tf="5")
        assert plugin._route_to_logic(alert) == "LOGIC3"
        
        # Test 5m → LOGIC1
        alert = ZepixV3Alert(signal_type="Momentum_Breakout", tf="5")
        assert plugin._route_to_logic(alert) == "LOGIC1"
        
        # Test 15m → LOGIC2
        alert = ZepixV3Alert(signal_type="Momentum_Breakout", tf="15")
        assert plugin._route_to_logic(alert) == "LOGIC2"
```

### 8.2 Integration Tests

```python
# tests/test_v3_integration.py
class TestV3Integration:
    async def test_full_signal_flow(self):
        """Test complete signal processing flow."""
        # Setup
        plugin = V3CombinedPlugin("v3_combined", {}, mock_service_api)
        
        # Process signal
        signal = {
            'type': 'entry_v3',
            'signal_type': 'Institutional_Launchpad',
            'symbol': 'EURUSD',
            'direction': 'buy',
            'tf': '15',
            'price': 1.08500,
            'consensus_score': 7,
            'sl_price': 1.08200
        }
        
        result = await plugin.process_signal(signal)
        
        # Verify
        assert result['status'] == 'executed'
        assert result['order_a_id'] is not None
        assert result['order_b_id'] is not None
```

---

## Implementation Checklist

| Phase | Task | Status |
|-------|------|--------|
| 1 | Create plugin directory structure | COMPLETE |
| 1 | Implement base plugin class | COMPLETE |
| 1 | Create plugin configuration | COMPLETE |
| 2 | Implement ISignalProcessor interface | COMPLETE |
| 2 | Implement signal handlers | COMPLETE |
| 2 | Implement signal routing | COMPLETE |
| 3 | Implement IDualOrderCapable interface | COMPLETE |
| 3 | Implement Order A configuration | COMPLETE |
| 3 | Implement Order B configuration | COMPLETE |
| 4 | Implement IReentryCapable interface | COMPLETE |
| 4 | Implement recovery callback | COMPLETE |
| 5 | Implement IProfitBookingCapable interface | COMPLETE |
| 5 | Implement profit target hit handler | COMPLETE |
| 6 | Implement IAutonomousCapable interface | COMPLETE |
| 7 | Implement ServiceAPI injection | COMPLETE |
| 7 | Implement ServiceAPI-based processing | COMPLETE |
| 8 | Create unit tests | COMPLETE |
| 8 | Create integration tests | COMPLETE |

---

**Document Status**: COMPLETE  
**Implementation Coverage**: 100%  
**V5 Architecture Compliance**: VERIFIED
