# PLAN 05: PROFIT BOOKING INTEGRATION

**Date:** 2026-01-15
**Priority:** P0 (Critical)
**Estimated Time:** 3-4 days
**Dependencies:** Plan 04 (Dual Order System)

---

## 1. OBJECTIVE

Integrate the Profit Booking System into the plugin architecture. The bot uses a 5-level pyramid system for Order B profit booking. After this plan, plugins will properly create and manage:

1. **5-Level Pyramid** - Level 0: 1 order, Level 1: 2 orders, Level 2: 4 orders, Level 3: 8 orders, Level 4: 16 orders
2. **Individual Order Booking** - $7 profit target per order
3. **Chain Progression** - Automatic level advancement
4. **Profit Booking SL Hunt** - Recovery after profit booking SL hit

**Current Problem (from Study Report 04, GAP-4):**
- Plugins exist but NEVER call ProfitBookingManager
- Order B doesn't create profit chains
- 5-level pyramid not implemented in plugins
- Chain level tracking not connected to profit booking

**Target State:**
- Plugins call ProfitBookingManager for Order B
- Order B creates profit booking chains
- 5-level pyramid progression works
- Profit Booking SL Hunt triggers on SL hit

---

## 2. SCOPE

### In-Scope:
- Wire plugins to ProfitBookingManager
- Implement 5-level pyramid in plugin Order B lifecycle
- Implement $7 profit target per order
- Implement chain progression logic
- Implement Profit Booking SL Hunt
- Track chain levels per plugin

### Out-of-Scope:
- Order A management (Plan 04)
- Re-entry system (Plan 03)
- Telegram notifications (Plan 07)

---

## 3. CURRENT STATE ANALYSIS

### File: `src/managers/profit_booking_manager.py`

**Current Structure (from Study Report 01, Feature 4.1-4.6):**
- Lines 1-100: Imports, class definition, pyramid configuration
- Lines 101-200: Chain creation and management
- Lines 201-300: Individual order booking ($7 target)
- Lines 301-400: Chain progression logic
- Lines 401-500: Strict mode implementation
- Lines 501-600: Profit Booking SL Hunt

**Key Methods:**
```python
class ProfitBookingManager:
    # Pyramid configuration
    PYRAMID_LEVELS = {
        0: 1,   # Level 0: 1 order
        1: 2,   # Level 1: 2 orders
        2: 4,   # Level 2: 4 orders
        3: 8,   # Level 3: 8 orders
        4: 16   # Level 4: 16 orders
    }
    PROFIT_TARGET = 7.0  # $7 per order
    
    async def create_profit_chain(self, order_b_id: str, symbol: str) -> str
    async def book_profit(self, chain_id: str, order_id: str) -> bool
    async def advance_chain_level(self, chain_id: str) -> int
    async def get_chain_status(self, chain_id: str) -> Dict
    async def start_profit_sl_hunt(self, chain_id: str) -> bool
```

### File: `src/logic_plugins/combined_v3/plugin.py`

**Current Problem:**
- `on_order_b_closed()` doesn't create profit chains
- No pyramid level tracking
- No profit booking integration

---

## 4. GAPS ADDRESSED

| Gap/Discovery | Description | How Addressed |
|---------------|-------------|---------------|
| GAP-4 | Profit Booking Integration | Wire plugins to ProfitBookingManager |
| Discovery 8 | Chain Level Tracking | Track per plugin |

---

## 5. IMPLEMENTATION STEPS

### Step 1: Create Profit Booking Interface for Plugins

**File:** `src/core/plugin_system/profit_booking_interface.py` (NEW)

**Code:**
```python
"""
Profit Booking Interface for Plugins
Defines how plugins interact with the Profit Booking System
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class ChainStatus(Enum):
    """Status of a profit booking chain"""
    ACTIVE = "active"
    COMPLETED = "completed"
    SL_HUNT = "sl_hunt"
    CANCELLED = "cancelled"

@dataclass
class ProfitChain:
    """Represents a profit booking chain"""
    chain_id: str
    plugin_id: str
    symbol: str
    direction: str
    level: int  # 0-4
    orders_in_level: int  # How many orders at current level
    orders_booked: int  # How many orders have hit profit target
    total_profit: float
    status: ChainStatus
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BookingResult:
    """Result of a profit booking operation"""
    success: bool
    order_id: str
    profit_amount: float
    chain_advanced: bool
    new_level: int
    error: Optional[str] = None

class IProfitBookingCapable(ABC):
    """Interface for plugins that use profit booking"""
    
    @abstractmethod
    async def create_profit_chain(self, order_b_id: str, signal: Dict[str, Any]) -> Optional[ProfitChain]:
        """
        Create a new profit booking chain for Order B.
        Called when Order B is created.
        """
        pass
    
    @abstractmethod
    async def on_profit_target_hit(self, chain_id: str, order_id: str) -> BookingResult:
        """
        Called when an order hits its $7 profit target.
        Books profit and potentially advances chain level.
        """
        pass
    
    @abstractmethod
    async def on_chain_sl_hit(self, chain_id: str) -> bool:
        """
        Called when chain SL is hit.
        Triggers Profit Booking SL Hunt.
        """
        pass
    
    @abstractmethod
    async def get_active_chains(self) -> List[ProfitChain]:
        """Get all active profit chains for this plugin"""
        pass
    
    @abstractmethod
    def get_pyramid_config(self) -> Dict[int, int]:
        """Get pyramid level configuration"""
        pass
```

**Reason:** Defines clear contract for profit booking operations.

---

### Step 2: Create Profit Booking Service for Plugins

**File:** `src/core/services/profit_booking_service.py` (NEW)

**Code:**
```python
"""
Profit Booking Service
Provides profit booking functionality to plugins via ServiceAPI
"""
from typing import Dict, Any, Optional, List
import logging
from src.managers.profit_booking_manager import ProfitBookingManager
from src.core.plugin_system.profit_booking_interface import (
    ProfitChain, BookingResult, ChainStatus
)

logger = logging.getLogger(__name__)

class ProfitBookingService:
    """
    Service layer for profit booking operations.
    Plugins use this instead of calling managers directly.
    """
    
    # Pyramid configuration
    PYRAMID_LEVELS = {
        0: 1,   # Level 0: 1 order
        1: 2,   # Level 1: 2 orders
        2: 4,   # Level 2: 4 orders
        3: 8,   # Level 3: 8 orders
        4: 16   # Level 4: 16 orders
    }
    MAX_LEVEL = 4
    PROFIT_TARGET = 7.0  # $7 per order
    
    def __init__(self, profit_booking_manager: ProfitBookingManager):
        self.manager = profit_booking_manager
        
        # Track chains by plugin
        self._plugin_chains: Dict[str, Dict[str, ProfitChain]] = {}
    
    async def create_chain(
        self,
        plugin_id: str,
        order_b_id: str,
        symbol: str,
        direction: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ProfitChain]:
        """
        Create a new profit booking chain.
        Called when Order B is created.
        """
        # Create chain in manager
        chain_id = await self.manager.create_profit_chain(order_b_id, symbol)
        if not chain_id:
            logger.error(f"Failed to create profit chain for {order_b_id}")
            return None
        
        # Create chain object
        chain = ProfitChain(
            chain_id=chain_id,
            plugin_id=plugin_id,
            symbol=symbol,
            direction=direction,
            level=0,
            orders_in_level=1,
            orders_booked=0,
            total_profit=0.0,
            status=ChainStatus.ACTIVE,
            metadata=metadata or {}
        )
        
        # Track chain
        self._track_chain(plugin_id, chain)
        
        logger.info(f"Profit chain created: {chain_id} for plugin {plugin_id}")
        return chain
    
    async def book_profit(
        self,
        chain_id: str,
        order_id: str,
        profit_amount: float
    ) -> BookingResult:
        """
        Book profit for an order in a chain.
        Called when order hits $7 target.
        """
        chain = self._get_chain_by_id(chain_id)
        if not chain:
            return BookingResult(
                success=False,
                order_id=order_id,
                profit_amount=0,
                chain_advanced=False,
                new_level=0,
                error="Chain not found"
            )
        
        # Book profit in manager
        success = await self.manager.book_profit(chain_id, order_id)
        if not success:
            return BookingResult(
                success=False,
                order_id=order_id,
                profit_amount=0,
                chain_advanced=False,
                new_level=chain.level,
                error="Booking failed"
            )
        
        # Update chain state
        chain.orders_booked += 1
        chain.total_profit += profit_amount
        
        # Check if level should advance
        chain_advanced = False
        if chain.orders_booked >= self.PYRAMID_LEVELS[chain.level]:
            chain_advanced = await self._advance_level(chain)
        
        logger.info(f"Profit booked: {order_id} in chain {chain_id}, total: ${chain.total_profit:.2f}")
        
        return BookingResult(
            success=True,
            order_id=order_id,
            profit_amount=profit_amount,
            chain_advanced=chain_advanced,
            new_level=chain.level
        )
    
    async def _advance_level(self, chain: ProfitChain) -> bool:
        """Advance chain to next pyramid level"""
        if chain.level >= self.MAX_LEVEL:
            logger.info(f"Chain {chain.chain_id} at max level")
            chain.status = ChainStatus.COMPLETED
            return False
        
        # Advance level
        old_level = chain.level
        chain.level += 1
        chain.orders_in_level = self.PYRAMID_LEVELS[chain.level]
        chain.orders_booked = 0  # Reset for new level
        
        # Advance in manager
        await self.manager.advance_chain_level(chain.chain_id)
        
        logger.info(f"Chain {chain.chain_id} advanced: Level {old_level} -> {chain.level}")
        return True
    
    async def start_sl_hunt(self, chain_id: str) -> bool:
        """
        Start Profit Booking SL Hunt.
        Called when chain SL is hit.
        """
        chain = self._get_chain_by_id(chain_id)
        if not chain:
            return False
        
        chain.status = ChainStatus.SL_HUNT
        
        # Start SL hunt in manager
        success = await self.manager.start_profit_sl_hunt(chain_id)
        
        logger.info(f"Profit Booking SL Hunt started for chain {chain_id}")
        return success
    
    def _track_chain(self, plugin_id: str, chain: ProfitChain):
        """Track chain ownership by plugin"""
        if plugin_id not in self._plugin_chains:
            self._plugin_chains[plugin_id] = {}
        self._plugin_chains[plugin_id][chain.chain_id] = chain
    
    def _get_chain_by_id(self, chain_id: str) -> Optional[ProfitChain]:
        """Find chain by ID across all plugins"""
        for plugin_chains in self._plugin_chains.values():
            if chain_id in plugin_chains:
                return plugin_chains[chain_id]
        return None
    
    def get_plugin_chains(self, plugin_id: str) -> List[ProfitChain]:
        """Get all chains for a plugin"""
        return list(self._plugin_chains.get(plugin_id, {}).values())
    
    def get_active_chains(self, plugin_id: str) -> List[ProfitChain]:
        """Get active chains for a plugin"""
        chains = self.get_plugin_chains(plugin_id)
        return [c for c in chains if c.status == ChainStatus.ACTIVE]
    
    def get_chain_stats(self, plugin_id: str) -> Dict[str, Any]:
        """Get profit booking statistics for a plugin"""
        chains = self.get_plugin_chains(plugin_id)
        
        return {
            'total_chains': len(chains),
            'active_chains': len([c for c in chains if c.status == ChainStatus.ACTIVE]),
            'completed_chains': len([c for c in chains if c.status == ChainStatus.COMPLETED]),
            'total_profit': sum(c.total_profit for c in chains),
            'chains_by_level': {
                level: len([c for c in chains if c.level == level])
                for level in range(self.MAX_LEVEL + 1)
            }
        }
```

**Reason:** Provides clean service interface for profit booking operations.

---

### Step 3: Update Combined V3 Plugin with Profit Booking Support

**File:** `src/logic_plugins/combined_v3/plugin.py`

**Changes - Add Profit Booking Interface:**
```python
# ADD imports
from src.core.plugin_system.profit_booking_interface import (
    IProfitBookingCapable, ProfitChain, BookingResult, ChainStatus
)
from src.core.services.profit_booking_service import ProfitBookingService

# UPDATE class definition
class CombinedV3Plugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor, 
                       IReentryCapable, IDualOrderCapable, IProfitBookingCapable):
    """
    Combined V3 Logic Plugin with Profit Booking Support
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._profit_booking_service: Optional[ProfitBookingService] = None
        self._order_to_chain: Dict[str, str] = {}  # order_b_id -> chain_id
    
    def set_profit_booking_service(self, service: ProfitBookingService):
        """Inject profit booking service"""
        self._profit_booking_service = service
    
    # ==================== IProfitBookingCapable Implementation ====================
    
    async def create_profit_chain(self, order_b_id: str, signal: Dict[str, Any]) -> Optional[ProfitChain]:
        """Create profit chain for Order B"""
        if not self._profit_booking_service:
            logger.warning("ProfitBookingService not available")
            return None
        
        chain = await self._profit_booking_service.create_chain(
            plugin_id=self.plugin_id,
            order_b_id=order_b_id,
            symbol=signal['symbol'],
            direction=signal['signal_type'],
            metadata={
                'logic': signal.get('logic', 'LOGIC1'),
                'original_signal': signal
            }
        )
        
        if chain:
            self._order_to_chain[order_b_id] = chain.chain_id
            logger.info(f"Profit chain created for Order B: {order_b_id}")
        
        return chain
    
    async def on_profit_target_hit(self, chain_id: str, order_id: str) -> BookingResult:
        """Handle profit target hit"""
        if not self._profit_booking_service:
            return BookingResult(
                success=False,
                order_id=order_id,
                profit_amount=0,
                chain_advanced=False,
                new_level=0,
                error="Service not available"
            )
        
        result = await self._profit_booking_service.book_profit(
            chain_id=chain_id,
            order_id=order_id,
            profit_amount=self._profit_booking_service.PROFIT_TARGET
        )
        
        if result.chain_advanced:
            logger.info(f"Chain {chain_id} advanced to level {result.new_level}")
            # Create new orders for the new level
            await self._create_level_orders(chain_id, result.new_level)
        
        return result
    
    async def on_chain_sl_hit(self, chain_id: str) -> bool:
        """Handle chain SL hit - start Profit Booking SL Hunt"""
        if not self._profit_booking_service:
            return False
        
        return await self._profit_booking_service.start_sl_hunt(chain_id)
    
    async def get_active_chains(self) -> List[ProfitChain]:
        """Get active profit chains"""
        if not self._profit_booking_service:
            return []
        return self._profit_booking_service.get_active_chains(self.plugin_id)
    
    def get_pyramid_config(self) -> Dict[int, int]:
        """Get pyramid configuration"""
        return {
            0: 1,   # Level 0: 1 order
            1: 2,   # Level 1: 2 orders
            2: 4,   # Level 2: 4 orders
            3: 8,   # Level 3: 8 orders
            4: 16   # Level 4: 16 orders
        }
    
    async def _create_level_orders(self, chain_id: str, level: int):
        """Create orders for a new pyramid level"""
        chain = self._profit_booking_service._get_chain_by_id(chain_id)
        if not chain:
            return
        
        num_orders = self.get_pyramid_config()[level]
        logger.info(f"Creating {num_orders} orders for chain {chain_id} level {level}")
        
        # Create orders for the new level
        for i in range(num_orders):
            signal = {
                'strategy': 'V3_COMBINED',
                'signal_type': chain.direction,
                'symbol': chain.symbol,
                'logic': chain.metadata.get('logic', 'LOGIC1'),
                'is_profit_chain_order': True,
                'chain_id': chain_id,
                'chain_level': level,
                'order_index': i
            }
            
            # Create only Order B for profit chain orders
            order_b_config = await self.get_order_b_config(signal)
            # ... create order via dual order service
    
    # ==================== Update on_order_b_closed ====================
    
    async def on_order_b_closed(self, order_id: str, reason: str) -> None:
        """Handle Order B closure - triggers profit booking"""
        logger.info(f"Order B closed: {order_id}, reason: {reason}")
        
        # Get chain for this order
        chain_id = self._order_to_chain.get(order_id)
        if not chain_id:
            logger.warning(f"No chain found for Order B: {order_id}")
            return
        
        if reason == 'PROFIT_TARGET':
            # Book profit
            result = await self.on_profit_target_hit(chain_id, order_id)
            logger.info(f"Profit booked: ${result.profit_amount:.2f}")
        elif reason == 'SL_HIT':
            # Start Profit Booking SL Hunt
            await self.on_chain_sl_hit(chain_id)
    
    # ==================== Update create_dual_orders ====================
    
    async def create_dual_orders(self, signal: Dict[str, Any]) -> DualOrderResult:
        """Create dual orders and profit chain for Order B"""
        # Create dual orders (from Plan 04)
        result = await super().create_dual_orders(signal)
        
        # Create profit chain for Order B
        if result.order_b_id and not signal.get('is_profit_chain_order'):
            await self.create_profit_chain(result.order_b_id, signal)
        
        return result
```

**Reason:** Implements profit booking interface in V3 plugin.

---

### Step 4: Create Profit Booking Integration Tests

**File:** `tests/test_profit_booking_integration.py` (NEW)

**Code:**
```python
"""
Tests for Profit Booking Integration
Verifies plugins properly create and manage profit chains
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.plugin_system.profit_booking_interface import (
    ProfitChain, BookingResult, ChainStatus
)
from src.core.services.profit_booking_service import ProfitBookingService

class TestProfitBookingService:
    """Test profit booking service"""
    
    @pytest.fixture
    def service(self):
        """Create service with mocks"""
        mock_manager = MagicMock()
        mock_manager.create_profit_chain = AsyncMock(return_value='chain_001')
        mock_manager.book_profit = AsyncMock(return_value=True)
        mock_manager.advance_chain_level = AsyncMock()
        mock_manager.start_profit_sl_hunt = AsyncMock(return_value=True)
        
        return ProfitBookingService(mock_manager)
    
    @pytest.mark.asyncio
    async def test_create_chain(self, service):
        """Test chain creation"""
        chain = await service.create_chain(
            plugin_id='combined_v3',
            order_b_id='order_b_001',
            symbol='EURUSD',
            direction='BUY'
        )
        
        assert chain is not None
        assert chain.chain_id == 'chain_001'
        assert chain.level == 0
        assert chain.orders_in_level == 1
        assert chain.status == ChainStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_book_profit_no_advance(self, service):
        """Test booking profit without level advance"""
        # Create chain first
        chain = await service.create_chain(
            plugin_id='combined_v3',
            order_b_id='order_b_001',
            symbol='EURUSD',
            direction='BUY'
        )
        
        # Book profit (level 0 has 1 order, so this should advance)
        result = await service.book_profit(
            chain_id=chain.chain_id,
            order_id='order_001',
            profit_amount=7.0
        )
        
        assert result.success == True
        assert result.profit_amount == 7.0
        assert result.chain_advanced == True
        assert result.new_level == 1
    
    @pytest.mark.asyncio
    async def test_pyramid_progression(self, service):
        """Test full pyramid progression"""
        # Create chain
        chain = await service.create_chain(
            plugin_id='combined_v3',
            order_b_id='order_b_001',
            symbol='EURUSD',
            direction='BUY'
        )
        
        # Level 0: 1 order
        await service.book_profit(chain.chain_id, 'order_0_0', 7.0)
        assert chain.level == 1
        
        # Level 1: 2 orders
        await service.book_profit(chain.chain_id, 'order_1_0', 7.0)
        assert chain.level == 1  # Not advanced yet
        await service.book_profit(chain.chain_id, 'order_1_1', 7.0)
        assert chain.level == 2
        
        # Level 2: 4 orders
        for i in range(4):
            await service.book_profit(chain.chain_id, f'order_2_{i}', 7.0)
        assert chain.level == 3
    
    @pytest.mark.asyncio
    async def test_sl_hunt_trigger(self, service):
        """Test SL hunt trigger"""
        chain = await service.create_chain(
            plugin_id='combined_v3',
            order_b_id='order_b_001',
            symbol='EURUSD',
            direction='BUY'
        )
        
        success = await service.start_sl_hunt(chain.chain_id)
        
        assert success == True
        assert chain.status == ChainStatus.SL_HUNT
    
    def test_pyramid_config(self, service):
        """Test pyramid level configuration"""
        assert service.PYRAMID_LEVELS[0] == 1
        assert service.PYRAMID_LEVELS[1] == 2
        assert service.PYRAMID_LEVELS[2] == 4
        assert service.PYRAMID_LEVELS[3] == 8
        assert service.PYRAMID_LEVELS[4] == 16
        
        # Total orders in full pyramid: 1+2+4+8+16 = 31
        total = sum(service.PYRAMID_LEVELS.values())
        assert total == 31
    
    def test_chain_stats(self, service):
        """Test chain statistics"""
        # Add some test chains
        service._plugin_chains['combined_v3'] = {
            'chain_1': ProfitChain(
                chain_id='chain_1',
                plugin_id='combined_v3',
                symbol='EURUSD',
                direction='BUY',
                level=2,
                orders_in_level=4,
                orders_booked=2,
                total_profit=21.0,
                status=ChainStatus.ACTIVE
            ),
            'chain_2': ProfitChain(
                chain_id='chain_2',
                plugin_id='combined_v3',
                symbol='GBPUSD',
                direction='SELL',
                level=4,
                orders_in_level=16,
                orders_booked=16,
                total_profit=217.0,
                status=ChainStatus.COMPLETED
            )
        }
        
        stats = service.get_chain_stats('combined_v3')
        
        assert stats['total_chains'] == 2
        assert stats['active_chains'] == 1
        assert stats['completed_chains'] == 1
        assert stats['total_profit'] == 238.0
```

**Reason:** Verifies profit booking integration works correctly.

---

## 6. DEPENDENCIES

### Prerequisites:
- Plan 04 (Dual Order System) - Order B creation

### Blocks:
- Plan 06 (Autonomous System) - Needs profit tracking

---

## 7. FILES AFFECTED

| File | Action | Description |
|------|--------|-------------|
| `src/core/plugin_system/profit_booking_interface.py` | CREATE | Interface |
| `src/core/services/profit_booking_service.py` | CREATE | Service |
| `src/logic_plugins/combined_v3/plugin.py` | MODIFY | Add IProfitBookingCapable |
| `tests/test_profit_booking_integration.py` | CREATE | Tests |

---

## 8. TESTING STRATEGY

### Unit Tests:
1. Test chain creation
2. Test profit booking
3. Test pyramid progression
4. Test SL hunt trigger
5. Test chain statistics

### Integration Tests:
1. Full Order B → Chain → Booking → Advance flow
2. Chain SL hit → SL Hunt flow

---

## 9. ROLLBACK PLAN

### Feature Flag:
```python
{
    "use_profit_booking": false  # Disable profit chains
}
```

---

## 10. SUCCESS CRITERIA

1. ✅ `IProfitBookingCapable` interface created
2. ✅ `ProfitBookingService` created
3. ✅ V3 plugin implements profit booking
4. ✅ 5-level pyramid works
5. ✅ $7 profit target per order
6. ✅ Chain progression works
7. ✅ Profit Booking SL Hunt triggers
8. ✅ All tests pass

---

## 11. REFERENCES

- **Study Report 01:** Section 4 (Profit Booking System - 6 features)
- **Study Report 04:** GAP-4, Discovery 8
- **Code Evidence:** `src/managers/profit_booking_manager.py`

---

**END OF PLAN 05**
