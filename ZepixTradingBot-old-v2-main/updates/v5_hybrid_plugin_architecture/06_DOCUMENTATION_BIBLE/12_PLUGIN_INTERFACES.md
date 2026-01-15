# PLUGIN INTERFACES

**Purpose:** Contract definitions that plugins must implement

---

## OVERVIEW

Plugin interfaces define the contracts that plugins must implement to integrate with the V5 Hybrid Plugin Architecture. Each interface represents a specific capability.

---

## INTERFACE SUMMARY

| Interface | Purpose | Required Methods |
|-----------|---------|------------------|
| ISignalProcessor | Signal processing | `process_signal()`, `can_process_signal()` |
| IOrderExecutor | Order execution | `execute_order()`, `modify_order()`, `close_order()` |
| IReentryCapable | Re-entry support | `on_sl_hit()`, `on_tp_hit()`, `on_recovery_signal()` |
| IDualOrderCapable | Dual order support | `create_dual_orders()`, `get_order_a_config()`, `get_order_b_config()` |
| IProfitBookingCapable | Profit booking | `create_profit_chain()`, `on_profit_target_hit()` |
| IAutonomousCapable | Autonomous ops | `check_recovery_allowed()`, `activate_reverse_shield()` |
| IDatabaseCapable | Database access | `save_trade()`, `load_trades()`, `update_trade()` |

---

## ISignalProcessor

```python
class ISignalProcessor(ABC):
    """Interface for signal processing capability"""
    
    @abstractmethod
    def get_supported_strategies(self) -> List[str]:
        """Return list of strategy names this plugin supports."""
        pass
    
    @abstractmethod
    def get_supported_timeframes(self) -> List[str]:
        """Return list of timeframes this plugin supports."""
        pass
    
    @abstractmethod
    async def can_process_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Check if this plugin can process the given signal."""
        pass
    
    @abstractmethod
    async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process the signal and return result."""
        pass
```

---

## IOrderExecutor

```python
class IOrderExecutor(ABC):
    """Interface for order execution capability"""
    
    @abstractmethod
    async def execute_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an order and return result."""
        pass
    
    @abstractmethod
    async def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> bool:
        """Modify an existing order."""
        pass
    
    @abstractmethod
    async def close_order(self, order_id: str, reason: str) -> bool:
        """Close an existing order."""
        pass
```

---

## IReentryCapable

```python
class IReentryCapable(ABC):
    """Interface for re-entry capability"""
    
    @abstractmethod
    async def on_sl_hit(self, event: ReentryEvent) -> bool:
        """Handle SL hit for potential recovery."""
        pass
    
    @abstractmethod
    async def on_tp_hit(self, event: ReentryEvent) -> bool:
        """Handle TP hit for potential continuation."""
        pass
    
    @abstractmethod
    async def on_recovery_signal(self, event: ReentryEvent) -> Dict[str, Any]:
        """Process recovery signal."""
        pass
    
    @abstractmethod
    def get_chain_level(self, trade_id: str) -> int:
        """Get current chain level for a trade."""
        pass
    
    @abstractmethod
    def get_max_chain_level(self) -> int:
        """Get maximum allowed chain level."""
        pass
```

---

## IDualOrderCapable

```python
class IDualOrderCapable(ABC):
    """Interface for dual order capability"""
    
    @abstractmethod
    async def create_dual_orders(self, signal: Dict[str, Any]) -> DualOrderResult:
        """Create both Order A and Order B."""
        pass
    
    @abstractmethod
    async def get_order_a_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """Get Order A configuration."""
        pass
    
    @abstractmethod
    async def get_order_b_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """Get Order B configuration."""
        pass
    
    @abstractmethod
    async def on_order_a_closed(self, order_id: str, reason: str) -> None:
        """Handle Order A closure."""
        pass
    
    @abstractmethod
    async def on_order_b_closed(self, order_id: str, reason: str) -> None:
        """Handle Order B closure."""
        pass
```

---

## IProfitBookingCapable

```python
class IProfitBookingCapable(ABC):
    """Interface for profit booking capability"""
    
    @abstractmethod
    async def create_profit_chain(self, order_b_id: str, signal: Dict[str, Any]) -> Optional[ProfitChain]:
        """Create a new profit booking chain."""
        pass
    
    @abstractmethod
    async def on_profit_target_hit(self, chain_id: str, order_id: str) -> BookingResult:
        """Handle profit target hit."""
        pass
    
    @abstractmethod
    async def on_chain_sl_hit(self, chain_id: str) -> None:
        """Handle chain SL hit."""
        pass
    
    @abstractmethod
    def get_active_chains(self) -> Dict[str, ProfitChain]:
        """Get all active profit chains."""
        pass
    
    @abstractmethod
    def get_pyramid_config(self) -> Dict[str, Any]:
        """Get pyramid configuration."""
        pass
```

---

## IAutonomousCapable

```python
class IAutonomousCapable(ABC):
    """Interface for autonomous operations capability"""
    
    @abstractmethod
    async def check_recovery_allowed(self, trade_id: str) -> SafetyCheckResult:
        """Check if recovery is allowed for a trade."""
        pass
    
    @abstractmethod
    async def activate_reverse_shield(self, trade: Any) -> Dict[str, Any]:
        """Activate reverse shield protection."""
        pass
    
    @abstractmethod
    async def deactivate_reverse_shield(self, shield_id: str) -> bool:
        """Deactivate reverse shield."""
        pass
    
    @abstractmethod
    def get_safety_stats(self) -> Dict[str, Any]:
        """Get safety statistics."""
        pass
```

---

## IDatabaseCapable

```python
class IDatabaseCapable(ABC):
    """Interface for database access capability"""
    
    @abstractmethod
    async def save_trade(self, trade: Trade) -> bool:
        """Save trade to database."""
        pass
    
    @abstractmethod
    async def load_trades(self, filters: Dict[str, Any]) -> List[Trade]:
        """Load trades from database."""
        pass
    
    @abstractmethod
    async def update_trade(self, trade_id: str, updates: Dict[str, Any]) -> bool:
        """Update trade in database."""
        pass
```

---

## IMPLEMENTATION EXAMPLE

```python
class V3CombinedPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor, 
                       IReentryCapable, IDualOrderCapable, IProfitBookingCapable):
    """
    V3 Combined Plugin implementing multiple interfaces.
    """
    
    # ISignalProcessor
    def get_supported_strategies(self) -> List[str]:
        return ["V3_COMBINED", "V3"]
    
    def get_supported_timeframes(self) -> List[str]:
        return ["5m", "15m", "1h"]
    
    async def can_process_signal(self, signal_data: Dict[str, Any]) -> bool:
        strategy = signal_data.get("strategy", "")
        return strategy in self.get_supported_strategies()
    
    async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Implementation
        pass
    
    # IOrderExecutor
    async def execute_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.service_api.place_single_order_a(...)
    
    # IDualOrderCapable
    async def create_dual_orders(self, signal: Dict[str, Any]) -> DualOrderResult:
        return await self.service_api.create_dual_orders(...)
```

---

## RELATED FILES

- `src/core/plugin_system/base_plugin.py` - Base plugin class
- `src/core/plugin_system/plugin_registry.py` - Plugin registration
- `src/logic_plugins/v3_combined/plugin.py` - V3 implementation
- `src/logic_plugins/v6_price_action_*/plugin.py` - V6 implementations
