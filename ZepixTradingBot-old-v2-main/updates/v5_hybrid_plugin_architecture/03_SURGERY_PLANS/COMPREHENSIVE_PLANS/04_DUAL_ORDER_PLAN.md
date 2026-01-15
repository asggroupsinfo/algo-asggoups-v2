# PLAN 04: DUAL ORDER SYSTEM INTEGRATION

**Date:** 2026-01-15
**Priority:** P0 (Critical)
**Estimated Time:** 3-4 days
**Dependencies:** Plan 02 (Webhook Routing)

---

## 1. OBJECTIVE

Integrate the Dual Order System into the plugin architecture. The bot executes TWO orders per signal with different SL management strategies. After this plan, plugins will properly create and manage:

1. **Order A (TP_TRAIL)** - Uses V3 Smart SL with progressive trailing
2. **Order B (PROFIT_TRAIL)** - Uses fixed $10 risk SL, creates profit booking chains

**Current Problem (from Study Report 04, GAP-2):**
- Plugins exist but NEVER call DualOrderManager
- Order A and Order B have different lifecycles - not handled
- Smart Lot Adjustment (Discovery 6) not used by plugins
- Order tagging for tracking not implemented

**Target State:**
- Plugins call DualOrderManager for all order execution
- Order A uses V3 Smart SL with trailing
- Order B uses fixed risk SL and creates profit chains
- Smart Lot Adjustment reduces lot when near daily limit
- All orders tagged with plugin_id for tracking

---

## 2. SCOPE

### In-Scope:
- Wire plugins to DualOrderManager
- Implement Order A lifecycle (TP_TRAIL + V3 Smart SL)
- Implement Order B lifecycle (PROFIT_TRAIL + fixed SL)
- Implement Smart Lot Adjustment
- Implement order tagging with plugin_id
- Wire to RiskManager for lot sizing

### Out-of-Scope:
- Profit Booking chains (Plan 05)
- Re-entry system (Plan 03)
- Telegram notifications (Plan 07)

---

## 3. CURRENT STATE ANALYSIS

### File: `src/managers/dual_order_manager.py`

**Current Structure (from Study Report 01, Feature 2.1-2.5):**
- Lines 1-80: Imports, class definition
- Lines 81-150: Order A creation (TP_TRAIL)
- Lines 151-220: Order B creation (PROFIT_TRAIL)
- Lines 221-300: Smart Lot Adjustment logic
- Lines 301-380: Independent execution handling
- Lines 381-450: Order modification methods
- Lines 451-520: Order close methods

**Key Methods:**
```python
class DualOrderManager:
    async def create_dual_orders(self, signal: Dict) -> Tuple[Order, Order]
    async def create_order_a(self, signal: Dict, lot_size: float) -> Order
    async def create_order_b(self, signal: Dict, lot_size: float) -> Order
    async def modify_order_sl(self, order_id: str, new_sl: float) -> bool
    async def close_order(self, order_id: str, reason: str) -> bool
    def calculate_smart_lot(self, base_lot: float, daily_pnl: float) -> float
```

### File: `src/managers/risk_manager.py`

**Current Structure (from Study Report 01, Feature 5.1-5.6):**
- Account tier system (Tier 1-5)
- Daily loss limit tracking
- Lifetime loss limit tracking
- Fixed lot sizing per tier
- Logic-based lot sizing (LOGIC1, LOGIC2, LOGIC3 have different lots)

**Key Methods:**
```python
class RiskManager:
    def get_lot_size(self, logic: str, tier: int) -> float
    def check_daily_limit(self) -> bool
    def check_lifetime_limit(self) -> bool
    def get_current_tier(self) -> int
```

### File: `src/logic_plugins/combined_v3/plugin.py`

**Current Problem:**
- `process_signal()` doesn't call DualOrderManager
- No Order A/B differentiation
- No Smart Lot Adjustment
- No order tagging

---

## 4. GAPS ADDRESSED

| Gap/Discovery | Description | How Addressed |
|---------------|-------------|---------------|
| GAP-2 | Dual Order System Integration | Wire plugins to DualOrderManager |
| REQ-2.4 | Plugin Order Tagging | Tag orders with plugin_id |
| Discovery 6 | Smart Lot Adjustment | Implement in plugin order flow |

---

## 5. IMPLEMENTATION STEPS

### Step 1: Create Dual Order Interface for Plugins

**File:** `src/core/plugin_system/dual_order_interface.py` (NEW)

**Code:**
```python
"""
Dual Order Interface for Plugins
Defines how plugins interact with the Dual Order System
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class OrderType(Enum):
    """Order types in dual order system"""
    ORDER_A = "order_a"  # TP_TRAIL with V3 Smart SL
    ORDER_B = "order_b"  # PROFIT_TRAIL with fixed $10 risk SL

class SLType(Enum):
    """SL management types"""
    V3_SMART_SL = "v3_smart_sl"      # Progressive trailing for Order A
    FIXED_RISK_SL = "fixed_risk_sl"  # Fixed $10 risk for Order B

@dataclass
class OrderConfig:
    """Configuration for an order"""
    order_type: OrderType
    sl_type: SLType
    lot_size: float
    sl_pips: float
    tp_pips: Optional[float] = None
    trailing_enabled: bool = False
    trailing_start_pips: float = 0
    trailing_step_pips: float = 0
    risk_amount: float = 10.0  # For Order B fixed risk
    plugin_id: str = ""
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DualOrderResult:
    """Result of dual order creation"""
    order_a_id: Optional[str] = None
    order_b_id: Optional[str] = None
    order_a_status: str = "pending"
    order_b_status: str = "pending"
    total_lot_size: float = 0.0
    error: Optional[str] = None

class IDualOrderCapable(ABC):
    """Interface for plugins that use dual orders"""
    
    @abstractmethod
    async def create_dual_orders(self, signal: Dict[str, Any]) -> DualOrderResult:
        """
        Create both Order A and Order B for a signal.
        Returns result with both order IDs.
        """
        pass
    
    @abstractmethod
    async def get_order_a_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """
        Get configuration for Order A (TP_TRAIL).
        Uses V3 Smart SL with progressive trailing.
        """
        pass
    
    @abstractmethod
    async def get_order_b_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """
        Get configuration for Order B (PROFIT_TRAIL).
        Uses fixed $10 risk SL.
        """
        pass
    
    @abstractmethod
    async def on_order_a_closed(self, order_id: str, reason: str) -> None:
        """Called when Order A is closed"""
        pass
    
    @abstractmethod
    async def on_order_b_closed(self, order_id: str, reason: str) -> None:
        """Called when Order B is closed - may trigger profit booking"""
        pass
    
    @abstractmethod
    def get_smart_lot_size(self, base_lot: float) -> float:
        """
        Calculate smart lot size based on daily P&L.
        Reduces lot when approaching daily limit.
        """
        pass
```

**Reason:** Defines clear contract for dual order operations.

---

### Step 2: Create Dual Order Service for Plugins

**File:** `src/core/services/dual_order_service.py` (NEW)

**Code:**
```python
"""
Dual Order Service
Provides dual order functionality to plugins via ServiceAPI
"""
from typing import Dict, Any, Optional, Tuple
import logging
from src.managers.dual_order_manager import DualOrderManager
from src.managers.risk_manager import RiskManager
from src.core.plugin_system.dual_order_interface import (
    OrderConfig, DualOrderResult, OrderType, SLType
)

logger = logging.getLogger(__name__)

class DualOrderService:
    """
    Service layer for dual order operations.
    Plugins use this instead of calling managers directly.
    """
    
    def __init__(
        self,
        dual_order_manager: DualOrderManager,
        risk_manager: RiskManager
    ):
        self.dual_order_manager = dual_order_manager
        self.risk_manager = risk_manager
        
        # Track orders by plugin
        self._plugin_orders: Dict[str, Dict[str, str]] = {}  # plugin_id -> {order_id: order_type}
    
    async def create_dual_orders(
        self,
        signal: Dict[str, Any],
        order_a_config: OrderConfig,
        order_b_config: OrderConfig
    ) -> DualOrderResult:
        """
        Create both Order A and Order B.
        
        Args:
            signal: Trading signal
            order_a_config: Configuration for Order A
            order_b_config: Configuration for Order B
        
        Returns:
            DualOrderResult with both order IDs
        """
        result = DualOrderResult()
        
        # Check risk limits first
        if not self.risk_manager.check_daily_limit():
            result.error = "Daily loss limit reached"
            logger.warning(result.error)
            return result
        
        # Apply smart lot adjustment
        adjusted_lot_a = self._apply_smart_lot(order_a_config.lot_size)
        adjusted_lot_b = self._apply_smart_lot(order_b_config.lot_size)
        
        # Create Order A (TP_TRAIL)
        try:
            order_a = await self._create_order_a(signal, order_a_config, adjusted_lot_a)
            if order_a:
                result.order_a_id = order_a['order_id']
                result.order_a_status = "executed"
                self._track_order(order_a_config.plugin_id, order_a['order_id'], 'order_a')
                logger.info(f"Order A created: {result.order_a_id}")
        except Exception as e:
            result.order_a_status = f"failed: {e}"
            logger.error(f"Order A creation failed: {e}")
        
        # Create Order B (PROFIT_TRAIL)
        try:
            order_b = await self._create_order_b(signal, order_b_config, adjusted_lot_b)
            if order_b:
                result.order_b_id = order_b['order_id']
                result.order_b_status = "executed"
                self._track_order(order_b_config.plugin_id, order_b['order_id'], 'order_b')
                logger.info(f"Order B created: {result.order_b_id}")
        except Exception as e:
            result.order_b_status = f"failed: {e}"
            logger.error(f"Order B creation failed: {e}")
        
        result.total_lot_size = adjusted_lot_a + adjusted_lot_b
        return result
    
    async def _create_order_a(
        self,
        signal: Dict[str, Any],
        config: OrderConfig,
        lot_size: float
    ) -> Optional[Dict[str, Any]]:
        """Create Order A with V3 Smart SL"""
        order_params = {
            'symbol': signal['symbol'],
            'direction': signal['signal_type'],
            'lot_size': lot_size,
            'sl_pips': config.sl_pips,
            'tp_pips': config.tp_pips,
            'order_type': 'ORDER_A',
            'sl_management': 'V3_SMART_SL',
            'trailing_enabled': config.trailing_enabled,
            'trailing_start': config.trailing_start_pips,
            'trailing_step': config.trailing_step_pips,
            'plugin_id': config.plugin_id,
            'metadata': config.metadata or {}
        }
        
        return await self.dual_order_manager.create_order_a(order_params)
    
    async def _create_order_b(
        self,
        signal: Dict[str, Any],
        config: OrderConfig,
        lot_size: float
    ) -> Optional[Dict[str, Any]]:
        """Create Order B with fixed risk SL"""
        # Calculate SL based on fixed risk amount
        sl_pips = self._calculate_fixed_risk_sl(
            signal['symbol'],
            lot_size,
            config.risk_amount
        )
        
        order_params = {
            'symbol': signal['symbol'],
            'direction': signal['signal_type'],
            'lot_size': lot_size,
            'sl_pips': sl_pips,
            'tp_pips': None,  # Order B uses profit booking, not TP
            'order_type': 'ORDER_B',
            'sl_management': 'FIXED_RISK_SL',
            'risk_amount': config.risk_amount,
            'plugin_id': config.plugin_id,
            'metadata': config.metadata or {}
        }
        
        return await self.dual_order_manager.create_order_b(order_params)
    
    def _apply_smart_lot(self, base_lot: float) -> float:
        """
        Apply smart lot adjustment based on daily P&L.
        Discovery 6: Reduces lot when near daily limit.
        """
        daily_pnl = self.risk_manager.get_daily_pnl()
        daily_limit = self.risk_manager.get_daily_limit()
        
        # Calculate how close we are to daily limit
        remaining = daily_limit - abs(daily_pnl)
        limit_ratio = remaining / daily_limit
        
        # Reduce lot size as we approach limit
        if limit_ratio < 0.25:  # Less than 25% remaining
            adjustment = 0.50  # 50% of base lot
        elif limit_ratio < 0.50:  # Less than 50% remaining
            adjustment = 0.75  # 75% of base lot
        else:
            adjustment = 1.0  # Full lot
        
        adjusted_lot = base_lot * adjustment
        
        if adjustment < 1.0:
            logger.info(f"Smart lot adjustment: {base_lot} -> {adjusted_lot} (limit ratio: {limit_ratio:.2f})")
        
        return adjusted_lot
    
    def _calculate_fixed_risk_sl(
        self,
        symbol: str,
        lot_size: float,
        risk_amount: float
    ) -> float:
        """
        Calculate SL pips for fixed risk amount.
        For Order B: Fixed $10 risk.
        """
        # Get pip value for symbol
        pip_value = self._get_pip_value(symbol, lot_size)
        
        # Calculate SL pips: risk_amount / pip_value
        sl_pips = risk_amount / pip_value if pip_value > 0 else 15
        
        return round(sl_pips, 1)
    
    def _get_pip_value(self, symbol: str, lot_size: float) -> float:
        """Get pip value for a symbol and lot size"""
        # Standard pip values (per 0.01 lot)
        pip_values = {
            'EURUSD': 0.10,
            'GBPUSD': 0.10,
            'USDJPY': 0.09,
            'USDCHF': 0.10,
            'AUDUSD': 0.10,
            'USDCAD': 0.10,
            'NZDUSD': 0.10,
            'XAUUSD': 0.10,
        }
        
        base_pip_value = pip_values.get(symbol, 0.10)
        return base_pip_value * (lot_size / 0.01)
    
    def _track_order(self, plugin_id: str, order_id: str, order_type: str):
        """Track order ownership by plugin"""
        if plugin_id not in self._plugin_orders:
            self._plugin_orders[plugin_id] = {}
        self._plugin_orders[plugin_id][order_id] = order_type
    
    def get_plugin_orders(self, plugin_id: str) -> Dict[str, str]:
        """Get all orders for a plugin"""
        return self._plugin_orders.get(plugin_id, {}).copy()
    
    def get_order_type(self, order_id: str) -> Optional[str]:
        """Get order type (order_a or order_b) for an order"""
        for plugin_orders in self._plugin_orders.values():
            if order_id in plugin_orders:
                return plugin_orders[order_id]
        return None
    
    async def modify_order_sl(self, order_id: str, new_sl_pips: float) -> bool:
        """Modify order SL"""
        return await self.dual_order_manager.modify_order_sl(order_id, new_sl_pips)
    
    async def close_order(self, order_id: str, reason: str) -> bool:
        """Close an order"""
        return await self.dual_order_manager.close_order(order_id, reason)
```

**Reason:** Provides clean service interface for dual order operations.

---

### Step 3: Update Combined V3 Plugin with Dual Order Support

**File:** `src/logic_plugins/combined_v3/plugin.py`

**Changes - Add Dual Order Interface:**
```python
# ADD imports
from src.core.plugin_system.dual_order_interface import (
    IDualOrderCapable, OrderConfig, DualOrderResult, OrderType, SLType
)
from src.core.services.dual_order_service import DualOrderService

# UPDATE class definition
class CombinedV3Plugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor, 
                       IReentryCapable, IDualOrderCapable):
    """
    Combined V3 Logic Plugin with Dual Order Support
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._dual_order_service: Optional[DualOrderService] = None
        self._active_orders: Dict[str, Dict[str, Any]] = {}  # order_id -> order_info
    
    def set_dual_order_service(self, service: DualOrderService):
        """Inject dual order service"""
        self._dual_order_service = service
    
    # ==================== IDualOrderCapable Implementation ====================
    
    async def create_dual_orders(self, signal: Dict[str, Any]) -> DualOrderResult:
        """Create both Order A and Order B"""
        if not self._dual_order_service:
            logger.warning("DualOrderService not available")
            return DualOrderResult(error="Service not available")
        
        # Get configurations for both orders
        order_a_config = await self.get_order_a_config(signal)
        order_b_config = await self.get_order_b_config(signal)
        
        # Create dual orders
        result = await self._dual_order_service.create_dual_orders(
            signal, order_a_config, order_b_config
        )
        
        # Track orders
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
        
        logger.info(f"Dual orders created: A={result.order_a_id}, B={result.order_b_id}")
        return result
    
    async def get_order_a_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """Get Order A configuration (TP_TRAIL with V3 Smart SL)"""
        logic = signal.get('logic', 'LOGIC1')
        base_lot = self._get_base_lot(logic)
        smart_lot = self.get_smart_lot_size(base_lot)
        
        # V3 Smart SL configuration
        sl_pips = self._get_sl_pips(signal['symbol'], logic)
        tp_pips = sl_pips * 2  # 2:1 RR for Order A
        
        return OrderConfig(
            order_type=OrderType.ORDER_A,
            sl_type=SLType.V3_SMART_SL,
            lot_size=smart_lot,
            sl_pips=sl_pips,
            tp_pips=tp_pips,
            trailing_enabled=True,
            trailing_start_pips=sl_pips * 0.5,  # Start trailing at 50% of SL
            trailing_step_pips=sl_pips * 0.25,  # Trail in 25% steps
            plugin_id=self.plugin_id,
            metadata={
                'logic': logic,
                'original_sl': sl_pips
            }
        )
    
    async def get_order_b_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """Get Order B configuration (PROFIT_TRAIL with fixed $10 risk)"""
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
            plugin_id=self.plugin_id,
            metadata={
                'logic': logic,
                'creates_profit_chain': True
            }
        )
    
    async def on_order_a_closed(self, order_id: str, reason: str) -> None:
        """Handle Order A closure"""
        logger.info(f"Order A closed: {order_id}, reason: {reason}")
        
        order_info = self._active_orders.pop(order_id, None)
        if not order_info:
            return
        
        # If SL hit, trigger re-entry
        if reason == 'SL_HIT':
            signal = order_info['signal']
            event = ReentryEvent(
                trade_id=order_id,
                plugin_id=self.plugin_id,
                symbol=signal['symbol'],
                reentry_type=ReentryType.SL_HUNT,
                entry_price=signal.get('price', 0),
                exit_price=0,  # Will be filled by monitor
                sl_price=0,
                direction=signal['signal_type'],
                chain_level=self.get_chain_level(order_id)
            )
            await self.on_sl_hit(event)
    
    async def on_order_b_closed(self, order_id: str, reason: str) -> None:
        """Handle Order B closure - may trigger profit booking"""
        logger.info(f"Order B closed: {order_id}, reason: {reason}")
        
        order_info = self._active_orders.pop(order_id, None)
        if not order_info:
            return
        
        # Order B closure triggers profit booking chain (Plan 05)
        # For now, just log
        if reason == 'TP_HIT' or reason == 'PROFIT_BOOKED':
            logger.info(f"Order B profit booked: {order_id}")
    
    def get_smart_lot_size(self, base_lot: float) -> float:
        """Calculate smart lot based on daily P&L"""
        if not self._dual_order_service:
            return base_lot
        return self._dual_order_service._apply_smart_lot(base_lot)
    
    def _get_base_lot(self, logic: str) -> float:
        """Get base lot size for logic"""
        lot_sizes = {
            'LOGIC1': 0.01,  # 5m scalping - smallest
            'LOGIC2': 0.02,  # 15m intraday - medium
            'LOGIC3': 0.03   # 1h swing - largest
        }
        return lot_sizes.get(logic, 0.01)
    
    def _get_sl_pips(self, symbol: str, logic: str) -> float:
        """Get SL pips based on symbol and logic"""
        # Symbol-specific base SL
        symbol_sl = {
            'EURUSD': 15,
            'GBPUSD': 18,
            'USDJPY': 15,
            'XAUUSD': 30,
        }
        base_sl = symbol_sl.get(symbol, 15)
        
        # Logic multiplier
        logic_multiplier = {
            'LOGIC1': 1.0,   # 5m - standard
            'LOGIC2': 1.5,   # 15m - wider
            'LOGIC3': 2.0    # 1h - widest
        }
        multiplier = logic_multiplier.get(logic, 1.0)
        
        return base_sl * multiplier
    
    # ==================== Update process_signal to use dual orders ====================
    
    async def process_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process signal using dual order system"""
        logger.info(f"Processing V3 signal: {signal.get('signal_type')} {signal.get('symbol')}")
        
        # Validate signal
        if not self._validate_signal(signal):
            return None
        
        # Check if this is a re-entry signal
        if signal.get('is_reentry'):
            return await self._process_reentry_signal(signal)
        
        # Create dual orders for new signal
        result = await self.create_dual_orders(signal)
        
        if result.error:
            logger.error(f"Dual order creation failed: {result.error}")
            return None
        
        return {
            'status': 'executed',
            'order_a_id': result.order_a_id,
            'order_b_id': result.order_b_id,
            'total_lot': result.total_lot_size
        }
```

**Reason:** Implements dual order interface in V3 plugin.

---

### Step 4: Create Order Event Handler

**File:** `src/logic_plugins/combined_v3/order_events.py` (NEW)

**Code:**
```python
"""
Order Event Handler for V3 Plugin
Handles order lifecycle events and triggers appropriate actions
"""
from typing import Dict, Any, Optional
import logging
from src.core.plugin_system.dual_order_interface import OrderType

logger = logging.getLogger(__name__)

class V3OrderEventHandler:
    """Handles order events for V3 plugin"""
    
    def __init__(self, plugin):
        self.plugin = plugin
    
    async def on_order_opened(self, order_id: str, order_type: str, details: Dict[str, Any]):
        """Called when an order is opened"""
        logger.info(f"Order opened: {order_id} ({order_type})")
        
        # Track in plugin
        self.plugin._active_orders[order_id] = {
            'type': order_type,
            'details': details,
            'status': 'open'
        }
    
    async def on_order_modified(self, order_id: str, modification: Dict[str, Any]):
        """Called when an order is modified (SL/TP change)"""
        logger.info(f"Order modified: {order_id} - {modification}")
        
        if order_id in self.plugin._active_orders:
            self.plugin._active_orders[order_id]['details'].update(modification)
    
    async def on_order_closed(self, order_id: str, close_reason: str, close_price: float):
        """Called when an order is closed"""
        logger.info(f"Order closed: {order_id}, reason: {close_reason}")
        
        order_info = self.plugin._active_orders.get(order_id)
        if not order_info:
            return
        
        order_type = order_info.get('type')
        
        # Route to appropriate handler
        if order_type == 'order_a':
            await self.plugin.on_order_a_closed(order_id, close_reason)
        elif order_type == 'order_b':
            await self.plugin.on_order_b_closed(order_id, close_reason)
    
    async def on_sl_hit(self, order_id: str, sl_price: float):
        """Called when SL is hit"""
        await self.on_order_closed(order_id, 'SL_HIT', sl_price)
    
    async def on_tp_hit(self, order_id: str, tp_price: float):
        """Called when TP is hit"""
        await self.on_order_closed(order_id, 'TP_HIT', tp_price)
    
    async def on_trailing_sl_updated(self, order_id: str, new_sl: float):
        """Called when trailing SL is updated"""
        logger.info(f"Trailing SL updated: {order_id} -> {new_sl}")
        await self.on_order_modified(order_id, {'sl_price': new_sl})
```

**Reason:** Centralizes order event handling for the plugin.

---

### Step 5: Create Dual Order Integration Tests

**File:** `tests/test_dual_order_integration.py` (NEW)

**Code:**
```python
"""
Tests for Dual Order System Integration
Verifies plugins properly create and manage dual orders
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.plugin_system.dual_order_interface import (
    OrderConfig, DualOrderResult, OrderType, SLType
)
from src.core.services.dual_order_service import DualOrderService
from src.logic_plugins.combined_v3.plugin import CombinedV3Plugin

class TestDualOrderInterface:
    """Test dual order interface implementation"""
    
    @pytest.fixture
    def v3_plugin(self):
        """Create V3 plugin with mock services"""
        config = {'max_chain_level': 5}
        plugin = CombinedV3Plugin(config)
        
        # Mock dual order service
        mock_service = MagicMock(spec=DualOrderService)
        mock_service.create_dual_orders = AsyncMock(return_value=DualOrderResult(
            order_a_id='order_a_001',
            order_b_id='order_b_001',
            order_a_status='executed',
            order_b_status='executed',
            total_lot_size=0.02
        ))
        mock_service._apply_smart_lot = MagicMock(return_value=0.01)
        plugin.set_dual_order_service(mock_service)
        
        return plugin
    
    @pytest.fixture
    def buy_signal(self):
        """Create buy signal"""
        return {
            'strategy': 'V3_COMBINED',
            'signal_type': 'BUY',
            'symbol': 'EURUSD',
            'logic': 'LOGIC1',
            'price': 1.0850
        }
    
    @pytest.mark.asyncio
    async def test_create_dual_orders(self, v3_plugin, buy_signal):
        """Test dual order creation"""
        result = await v3_plugin.create_dual_orders(buy_signal)
        
        assert result.order_a_id == 'order_a_001'
        assert result.order_b_id == 'order_b_001'
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_order_a_config(self, v3_plugin, buy_signal):
        """Test Order A configuration"""
        config = await v3_plugin.get_order_a_config(buy_signal)
        
        assert config.order_type == OrderType.ORDER_A
        assert config.sl_type == SLType.V3_SMART_SL
        assert config.trailing_enabled == True
        assert config.plugin_id == v3_plugin.plugin_id
    
    @pytest.mark.asyncio
    async def test_order_b_config(self, v3_plugin, buy_signal):
        """Test Order B configuration"""
        config = await v3_plugin.get_order_b_config(buy_signal)
        
        assert config.order_type == OrderType.ORDER_B
        assert config.sl_type == SLType.FIXED_RISK_SL
        assert config.risk_amount == 10.0
        assert config.tp_pips is None  # No TP for Order B
    
    @pytest.mark.asyncio
    async def test_process_signal_creates_dual_orders(self, v3_plugin, buy_signal):
        """Test process_signal uses dual orders"""
        result = await v3_plugin.process_signal(buy_signal)
        
        assert result is not None
        assert result['status'] == 'executed'
        assert result['order_a_id'] == 'order_a_001'
        assert result['order_b_id'] == 'order_b_001'

class TestDualOrderService:
    """Test dual order service"""
    
    @pytest.fixture
    def dual_order_service(self):
        """Create service with mocks"""
        mock_dual_mgr = MagicMock()
        mock_dual_mgr.create_order_a = AsyncMock(return_value={'order_id': 'a_001'})
        mock_dual_mgr.create_order_b = AsyncMock(return_value={'order_id': 'b_001'})
        
        mock_risk_mgr = MagicMock()
        mock_risk_mgr.check_daily_limit = MagicMock(return_value=True)
        mock_risk_mgr.get_daily_pnl = MagicMock(return_value=-50)
        mock_risk_mgr.get_daily_limit = MagicMock(return_value=200)
        
        return DualOrderService(mock_dual_mgr, mock_risk_mgr)
    
    def test_smart_lot_adjustment_full(self, dual_order_service):
        """Test smart lot at full capacity"""
        # 75% remaining (150/200)
        dual_order_service.risk_manager.get_daily_pnl = MagicMock(return_value=-50)
        
        adjusted = dual_order_service._apply_smart_lot(0.02)
        
        assert adjusted == 0.02  # Full lot
    
    def test_smart_lot_adjustment_reduced(self, dual_order_service):
        """Test smart lot reduction near limit"""
        # 25% remaining (50/200)
        dual_order_service.risk_manager.get_daily_pnl = MagicMock(return_value=-150)
        
        adjusted = dual_order_service._apply_smart_lot(0.02)
        
        assert adjusted == 0.015  # 75% of base
    
    def test_smart_lot_adjustment_critical(self, dual_order_service):
        """Test smart lot at critical level"""
        # 10% remaining (20/200)
        dual_order_service.risk_manager.get_daily_pnl = MagicMock(return_value=-180)
        
        adjusted = dual_order_service._apply_smart_lot(0.02)
        
        assert adjusted == 0.01  # 50% of base
    
    def test_fixed_risk_sl_calculation(self, dual_order_service):
        """Test fixed risk SL calculation"""
        # $10 risk with 0.01 lot on EURUSD
        sl_pips = dual_order_service._calculate_fixed_risk_sl('EURUSD', 0.01, 10.0)
        
        # pip_value = 0.10 * (0.01/0.01) = 0.10
        # sl_pips = 10 / 0.10 = 100 pips
        assert sl_pips == 100.0
    
    @pytest.mark.asyncio
    async def test_daily_limit_blocks_orders(self, dual_order_service):
        """Test daily limit prevents order creation"""
        dual_order_service.risk_manager.check_daily_limit = MagicMock(return_value=False)
        
        signal = {'symbol': 'EURUSD', 'signal_type': 'BUY'}
        order_a_config = OrderConfig(
            order_type=OrderType.ORDER_A,
            sl_type=SLType.V3_SMART_SL,
            lot_size=0.01,
            sl_pips=15,
            plugin_id='test'
        )
        order_b_config = OrderConfig(
            order_type=OrderType.ORDER_B,
            sl_type=SLType.FIXED_RISK_SL,
            lot_size=0.01,
            sl_pips=0,
            plugin_id='test'
        )
        
        result = await dual_order_service.create_dual_orders(signal, order_a_config, order_b_config)
        
        assert result.error == "Daily loss limit reached"
        assert result.order_a_id is None
        assert result.order_b_id is None
```

**Reason:** Verifies dual order integration works correctly.

---

## 6. DEPENDENCIES

### Prerequisites:
- Plan 02 (Webhook Routing) - Signals reach plugins

### Blocks:
- Plan 05 (Profit Booking) - Needs Order B for chains
- Plan 03 (Re-Entry) - Needs Order A for SL Hunt

---

## 7. FILES AFFECTED

| File | Action | Description |
|------|--------|-------------|
| `src/core/plugin_system/dual_order_interface.py` | CREATE | Dual order interface |
| `src/core/services/dual_order_service.py` | CREATE | Dual order service |
| `src/logic_plugins/combined_v3/plugin.py` | MODIFY | Add IDualOrderCapable |
| `src/logic_plugins/combined_v3/order_events.py` | CREATE | Order event handler |
| `tests/test_dual_order_integration.py` | CREATE | Integration tests |

---

## 8. TESTING STRATEGY

### Unit Tests:
1. Test Order A config has V3 Smart SL
2. Test Order B config has fixed $10 risk
3. Test smart lot adjustment at various P&L levels
4. Test fixed risk SL calculation
5. Test daily limit blocks orders

### Integration Tests:
1. Full signal → dual order creation flow
2. Order A closure → re-entry trigger
3. Order B closure → profit booking trigger

### Manual Verification:
1. Send V3 signal
2. Verify two orders created in MT5
3. Verify Order A has trailing SL
4. Verify Order B has fixed risk SL

---

## 9. ROLLBACK PLAN

### If Dual Order Integration Fails:
1. Revert plugin changes
2. Use single order mode
3. Disable dual orders via config

### Feature Flag:
```python
# In plugin config
{
    "use_dual_orders": false  # Falls back to single order
}
```

---

## 10. SUCCESS CRITERIA

This plan is COMPLETE when:

1. ✅ `IDualOrderCapable` interface created
2. ✅ `DualOrderService` created and functional
3. ✅ V3 plugin implements `IDualOrderCapable`
4. ✅ Order A uses V3 Smart SL with trailing
5. ✅ Order B uses fixed $10 risk SL
6. ✅ Smart Lot Adjustment works
7. ✅ Orders tagged with plugin_id
8. ✅ All tests pass

---

## 11. REFERENCES

- **Study Report 01:** Section 2 (Dual Order System - 5 features)
- **Study Report 04:** GAP-2, Discovery 6
- **Original Surgery Plan:** `03_SURGERY_PLANS/02_PLUGIN_WIRING_PLAN.md`
- **Code Evidence:** `src/managers/dual_order_manager.py`

---

**END OF PLAN 04**
