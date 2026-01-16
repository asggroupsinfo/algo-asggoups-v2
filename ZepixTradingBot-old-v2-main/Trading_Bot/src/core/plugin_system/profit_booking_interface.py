"""
Profit Booking Interface for Plugins
Plan 05: Profit Booking Integration

Defines how plugins interact with the Profit Booking System:
- 5-Level Pyramid: Level 0: 1 order, Level 1: 2 orders, Level 2: 4 orders, Level 3: 8 orders, Level 4: 16 orders
- Individual Order Booking: $7 profit target per order
- Chain Progression: Automatic level advancement
- Profit Booking SL Hunt: Recovery after profit booking SL hit
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ChainStatus(Enum):
    """Status of a profit booking chain"""
    ACTIVE = "active"          # Chain is actively trading
    COMPLETED = "completed"    # All levels completed successfully
    SL_HUNT = "sl_hunt"        # SL hit, in recovery mode
    CANCELLED = "cancelled"    # Chain cancelled manually or due to error


@dataclass
class ProfitChain:
    """
    Represents a profit booking chain.
    
    A chain tracks the 5-level pyramid progression for Order B:
    - Level 0: 1 order ($7 target)
    - Level 1: 2 orders ($14 total)
    - Level 2: 4 orders ($28 total)
    - Level 3: 8 orders ($56 total)
    - Level 4: 16 orders ($112 total)
    
    Total potential profit: $217 per chain
    """
    chain_id: str
    plugin_id: str
    symbol: str
    direction: str
    level: int  # 0-4
    orders_in_level: int  # How many orders at current level
    orders_booked: int  # How many orders have hit profit target
    total_profit: float
    status: ChainStatus
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BookingResult:
    """Result of a profit booking operation"""
    success: bool
    order_id: str
    profit_amount: float
    chain_advanced: bool
    new_level: int
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class IProfitBookingCapable(ABC):
    """
    Interface for plugins that use profit booking.
    
    Plugins implementing this interface can:
    - Create profit booking chains for Order B
    - Track 5-level pyramid progression
    - Handle profit target hits ($7 per order)
    - Trigger Profit Booking SL Hunt on SL hit
    """
    
    @abstractmethod
    async def create_profit_chain(
        self,
        order_b_id: str,
        signal: Dict[str, Any]
    ) -> Optional[ProfitChain]:
        """
        Create a new profit booking chain for Order B.
        
        Called when Order B is created. Initializes the chain at Level 0
        with 1 order and $7 profit target.
        
        Args:
            order_b_id: Order B identifier
            signal: Original trading signal
            
        Returns:
            ProfitChain if created successfully, None otherwise
        """
        pass
    
    @abstractmethod
    async def on_profit_target_hit(
        self,
        chain_id: str,
        order_id: str
    ) -> BookingResult:
        """
        Called when an order hits its $7 profit target.
        
        Books profit and potentially advances chain level:
        - Level 0: 1 order → advance to Level 1
        - Level 1: 2 orders → advance to Level 2
        - Level 2: 4 orders → advance to Level 3
        - Level 3: 8 orders → advance to Level 4
        - Level 4: 16 orders → chain complete
        
        Args:
            chain_id: Chain identifier
            order_id: Order that hit profit target
            
        Returns:
            BookingResult with profit amount and level info
        """
        pass
    
    @abstractmethod
    async def on_chain_sl_hit(self, chain_id: str) -> bool:
        """
        Called when chain SL is hit.
        
        Triggers Profit Booking SL Hunt to recover the chain.
        
        Args:
            chain_id: Chain identifier
            
        Returns:
            True if SL Hunt started successfully
        """
        pass
    
    @abstractmethod
    async def get_active_chains(self) -> List[ProfitChain]:
        """
        Get all active profit chains for this plugin.
        
        Returns:
            List of active ProfitChain objects
        """
        pass
    
    @abstractmethod
    def get_pyramid_config(self) -> Dict[int, int]:
        """
        Get pyramid level configuration.
        
        Returns:
            Dict mapping level (0-4) to number of orders
        """
        pass


# Pyramid configuration constants
PYRAMID_LEVELS = {
    0: 1,   # Level 0: 1 order
    1: 2,   # Level 1: 2 orders
    2: 4,   # Level 2: 4 orders
    3: 8,   # Level 3: 8 orders
    4: 16   # Level 4: 16 orders
}

MAX_PYRAMID_LEVEL = 4
PROFIT_TARGET_PER_ORDER = 7.0  # $7 per order

# Total orders in full pyramid: 1+2+4+8+16 = 31
TOTAL_ORDERS_IN_PYRAMID = sum(PYRAMID_LEVELS.values())

# Total potential profit: 31 * $7 = $217
TOTAL_POTENTIAL_PROFIT = TOTAL_ORDERS_IN_PYRAMID * PROFIT_TARGET_PER_ORDER
