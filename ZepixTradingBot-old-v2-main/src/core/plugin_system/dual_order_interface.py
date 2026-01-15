"""
Dual Order Interface for Plugins
Plan 04: Dual Order System Integration

Defines how plugins interact with the Dual Order System:
- Order A (TP_TRAIL): Uses V3 Smart SL with progressive trailing
- Order B (PROFIT_TRAIL): Uses fixed $10 risk SL, creates profit booking chains
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


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
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DualOrderResult:
    """Result of dual order creation"""
    order_a_id: Optional[str] = None
    order_b_id: Optional[str] = None
    order_a_status: str = "pending"
    order_b_status: str = "pending"
    total_lot_size: float = 0.0
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class IDualOrderCapable(ABC):
    """
    Interface for plugins that use dual orders.
    
    Plugins implementing this interface can:
    - Create both Order A and Order B for signals
    - Configure different SL strategies per order type
    - Handle order lifecycle events
    - Use smart lot adjustment based on daily P&L
    """
    
    @abstractmethod
    async def create_dual_orders(self, signal: Dict[str, Any]) -> DualOrderResult:
        """
        Create both Order A and Order B for a signal.
        
        Args:
            signal: Trading signal with symbol, direction, etc.
            
        Returns:
            DualOrderResult with both order IDs and status
        """
        pass
    
    @abstractmethod
    async def get_order_a_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """
        Get configuration for Order A (TP_TRAIL).
        
        Order A uses V3 Smart SL with progressive trailing:
        - Trailing starts at 50% of SL in profit
        - Trails in 25% steps
        - Has TP target (2:1 RR)
        
        Args:
            signal: Trading signal
            
        Returns:
            OrderConfig for Order A
        """
        pass
    
    @abstractmethod
    async def get_order_b_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """
        Get configuration for Order B (PROFIT_TRAIL).
        
        Order B uses fixed $10 risk SL:
        - No TP target (uses profit booking)
        - SL calculated from fixed risk amount
        - Creates profit booking chains
        
        Args:
            signal: Trading signal
            
        Returns:
            OrderConfig for Order B
        """
        pass
    
    @abstractmethod
    async def on_order_a_closed(self, order_id: str, reason: str) -> None:
        """
        Called when Order A is closed.
        
        If closed by SL, may trigger SL Hunt Recovery.
        If closed by TP, trade is complete.
        
        Args:
            order_id: Order identifier
            reason: Close reason (SL_HIT, TP_HIT, MANUAL, etc.)
        """
        pass
    
    @abstractmethod
    async def on_order_b_closed(self, order_id: str, reason: str) -> None:
        """
        Called when Order B is closed.
        
        May trigger profit booking chain (Plan 05).
        
        Args:
            order_id: Order identifier
            reason: Close reason (SL_HIT, TP_HIT, PROFIT_BOOKED, etc.)
        """
        pass
    
    @abstractmethod
    def get_smart_lot_size(self, base_lot: float) -> float:
        """
        Calculate smart lot size based on daily P&L.
        
        Discovery 6: Reduces lot when approaching daily limit:
        - >50% remaining: 100% of base lot
        - 25-50% remaining: 75% of base lot
        - <25% remaining: 50% of base lot
        
        Args:
            base_lot: Base lot size for the logic
            
        Returns:
            Adjusted lot size
        """
        pass
