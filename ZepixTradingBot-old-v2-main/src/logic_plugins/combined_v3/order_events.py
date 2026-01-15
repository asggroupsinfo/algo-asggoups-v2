"""
Order Event Handler for V3 Plugin
Plan 04: Dual Order System Integration

Handles order lifecycle events and triggers appropriate actions:
- Order opened events
- Order modified events (SL/TP changes)
- Order closed events (SL hit, TP hit, manual close)
- Trailing SL updates
"""
from typing import Dict, Any, Optional
import logging

from src.core.plugin_system.dual_order_interface import OrderType

logger = logging.getLogger(__name__)


class V3OrderEventHandler:
    """
    Handles order events for V3 plugin.
    
    This handler centralizes order lifecycle management and routes
    events to the appropriate plugin methods based on order type.
    """
    
    def __init__(self, plugin):
        """
        Initialize order event handler.
        
        Args:
            plugin: CombinedV3Plugin instance
        """
        self.plugin = plugin
    
    async def on_order_opened(
        self,
        order_id: str,
        order_type: str,
        details: Dict[str, Any]
    ):
        """
        Called when an order is opened.
        
        Args:
            order_id: Order identifier
            order_type: 'order_a' or 'order_b'
            details: Order details (symbol, direction, lot, sl, tp, etc.)
        """
        logger.info(f"Order opened: {order_id} ({order_type})")
        
        # Track in plugin's active orders
        self.plugin._active_orders[order_id] = {
            'type': order_type,
            'details': details,
            'status': 'open'
        }
    
    async def on_order_modified(
        self,
        order_id: str,
        modification: Dict[str, Any]
    ):
        """
        Called when an order is modified (SL/TP change).
        
        Args:
            order_id: Order identifier
            modification: Dict with modified fields (sl_price, tp_price, etc.)
        """
        logger.info(f"Order modified: {order_id} - {modification}")
        
        if order_id in self.plugin._active_orders:
            order_info = self.plugin._active_orders[order_id]
            if 'details' not in order_info:
                order_info['details'] = {}
            order_info['details'].update(modification)
    
    async def on_order_closed(
        self,
        order_id: str,
        close_reason: str,
        close_price: float
    ):
        """
        Called when an order is closed.
        
        Routes to appropriate handler based on order type:
        - Order A closure may trigger SL Hunt Recovery
        - Order B closure may trigger profit booking
        
        Args:
            order_id: Order identifier
            close_reason: Close reason (SL_HIT, TP_HIT, MANUAL, REVERSAL, etc.)
            close_price: Price at which order was closed
        """
        logger.info(f"Order closed: {order_id}, reason: {close_reason}, price: {close_price}")
        
        order_info = self.plugin._active_orders.get(order_id)
        if not order_info:
            logger.warning(f"Order {order_id} not found in active orders")
            return
        
        order_type = order_info.get('type')
        
        # Route to appropriate handler
        if order_type == 'order_a':
            await self.plugin.on_order_a_closed(order_id, close_reason)
        elif order_type == 'order_b':
            await self.plugin.on_order_b_closed(order_id, close_reason)
        else:
            logger.warning(f"Unknown order type: {order_type}")
    
    async def on_sl_hit(self, order_id: str, sl_price: float):
        """
        Called when SL is hit.
        
        Args:
            order_id: Order identifier
            sl_price: SL price that was hit
        """
        logger.info(f"SL hit: {order_id} at {sl_price}")
        await self.on_order_closed(order_id, 'SL_HIT', sl_price)
    
    async def on_tp_hit(self, order_id: str, tp_price: float):
        """
        Called when TP is hit.
        
        Args:
            order_id: Order identifier
            tp_price: TP price that was hit
        """
        logger.info(f"TP hit: {order_id} at {tp_price}")
        await self.on_order_closed(order_id, 'TP_HIT', tp_price)
    
    async def on_trailing_sl_updated(self, order_id: str, new_sl: float):
        """
        Called when trailing SL is updated.
        
        Only applies to Order A which uses V3 Smart SL with trailing.
        
        Args:
            order_id: Order identifier
            new_sl: New SL price
        """
        logger.info(f"Trailing SL updated: {order_id} -> {new_sl}")
        await self.on_order_modified(order_id, {'sl_price': new_sl, 'trailing_updated': True})
    
    async def on_partial_close(
        self,
        order_id: str,
        closed_lot: float,
        remaining_lot: float,
        close_price: float
    ):
        """
        Called when order is partially closed.
        
        Args:
            order_id: Order identifier
            closed_lot: Lot size that was closed
            remaining_lot: Remaining lot size
            close_price: Price at partial close
        """
        logger.info(
            f"Partial close: {order_id} - closed {closed_lot}, "
            f"remaining {remaining_lot} at {close_price}"
        )
        
        await self.on_order_modified(order_id, {
            'lot_size': remaining_lot,
            'partial_close_price': close_price,
            'partial_close_lot': closed_lot
        })
    
    def get_order_type(self, order_id: str) -> Optional[str]:
        """
        Get order type for an order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            'order_a', 'order_b', or None
        """
        order_info = self.plugin._active_orders.get(order_id)
        if order_info:
            return order_info.get('type')
        return None
    
    def get_order_details(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get order details.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order details dict or None
        """
        order_info = self.plugin._active_orders.get(order_id)
        if order_info:
            return order_info.get('details', {})
        return None
    
    def get_active_orders(self, order_type: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get all active orders, optionally filtered by type.
        
        Args:
            order_type: Filter by 'order_a' or 'order_b' (optional)
            
        Returns:
            Dict of order_id -> order_info
        """
        if order_type:
            return {
                oid: info for oid, info in self.plugin._active_orders.items()
                if info.get('type') == order_type
            }
        return self.plugin._active_orders.copy()
    
    def get_order_count(self) -> Dict[str, int]:
        """
        Get count of active orders by type.
        
        Returns:
            Dict with 'order_a', 'order_b', 'total' counts
        """
        order_a_count = sum(
            1 for info in self.plugin._active_orders.values()
            if info.get('type') == 'order_a'
        )
        order_b_count = sum(
            1 for info in self.plugin._active_orders.values()
            if info.get('type') == 'order_b'
        )
        
        return {
            'order_a': order_a_count,
            'order_b': order_b_count,
            'total': order_a_count + order_b_count
        }
