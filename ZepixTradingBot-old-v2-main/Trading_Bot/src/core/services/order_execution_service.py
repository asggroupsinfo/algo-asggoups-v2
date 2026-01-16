"""
Order Execution Service - Stateless service for order management

Provides V3 Dual Order and V6 Conditional Order methods.
All methods are stateless - they use passed parameters and database for state.

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, Tuple, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OrderExecutionService:
    """
    Stateless service for order execution.
    Wraps MT5 client and provides V3/V6 specific order methods.
    """
    
    def __init__(self, mt5_client, config, pip_calculator):
        self._mt5 = mt5_client
        self._config = config
        self._pip_calculator = pip_calculator
    
    async def place_dual_orders_v3(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        lot_size_total: float,
        order_a_sl: float,
        order_a_tp: float,
        order_b_sl: float,
        order_b_tp: float,
        logic_route: str
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Place V3 hybrid SL dual order system (Order A + Order B)
        
        V3 uses DIFFERENT SL for each order:
        - Order A: Smart SL from Pine Script
        - Order B: Fixed $10 SL (different from Order A)
        
        Args:
            plugin_id: Plugin identifier for tracking
            symbol: Trading symbol (e.g., 'XAUUSD')
            direction: 'BUY' or 'SELL'
            lot_size_total: Total lot size (will be split 50/50)
            order_a_sl: Smart SL price for Order A
            order_a_tp: TP2 (extended target) for Order A
            order_b_sl: Fixed $10 SL price for Order B (DIFFERENT from order_a)
            order_b_tp: TP1 (closer target) for Order B
            logic_route: 'LOGIC1', 'LOGIC2', or 'LOGIC3'
        
        Returns:
            Tuple of (order_a_ticket, order_b_ticket)
        """
        try:
            order_a_lot = lot_size_total / 2
            order_b_lot = lot_size_total / 2
            
            order_a_lot = max(0.01, round(order_a_lot, 2))
            order_b_lot = max(0.01, round(order_b_lot, 2))
            
            logger.info(
                f"[V3_DUAL] Placing dual orders for {plugin_id}: "
                f"{symbol} {direction} | A={order_a_lot} B={order_b_lot} | Route={logic_route}"
            )
            
            order_a_ticket = self._mt5.place_order(
                symbol=symbol,
                order_type=direction,
                lot_size=order_a_lot,
                price=0.0,
                sl=order_a_sl,
                tp=order_a_tp,
                comment=f"V3_A_{plugin_id}_{logic_route}"
            )
            
            order_b_ticket = self._mt5.place_order(
                symbol=symbol,
                order_type=direction,
                lot_size=order_b_lot,
                price=0.0,
                sl=order_b_sl,
                tp=order_b_tp,
                comment=f"V3_B_{plugin_id}_{logic_route}"
            )
            
            logger.info(
                f"[V3_DUAL] Orders placed: A={order_a_ticket} B={order_b_ticket}"
            )
            
            return (order_a_ticket, order_b_ticket)
            
        except Exception as e:
            logger.error(f"[V3_DUAL] Error placing dual orders: {e}")
            return (None, None)
    
    async def place_single_order_a(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        comment: str = 'ORDER_A'
    ) -> Optional[int]:
        """
        Place Order A ONLY (for 15M/1H V6 plugins)
        
        Order A characteristics:
        - Extended TP target (TP2)
        - Smart SL
        - Used for longer timeframe trades
        
        Args:
            plugin_id: Plugin identifier
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            lot_size: Lot size for the order
            sl_price: Stop loss price
            tp_price: Take profit price (TP2)
            comment: Order comment
        
        Returns:
            MT5 ticket number or None on failure
        """
        try:
            lot_size = max(0.01, round(lot_size, 2))
            
            logger.info(
                f"[V6_ORDER_A] Placing Order A for {plugin_id}: "
                f"{symbol} {direction} {lot_size} lots"
            )
            
            ticket = self._mt5.place_order(
                symbol=symbol,
                order_type=direction,
                lot_size=lot_size,
                price=0.0,
                sl=sl_price,
                tp=tp_price,
                comment=f"V6_A_{plugin_id}_{comment}"
            )
            
            logger.info(f"[V6_ORDER_A] Order placed: {ticket}")
            return ticket
            
        except Exception as e:
            logger.error(f"[V6_ORDER_A] Error placing order: {e}")
            return None
    
    async def place_single_order_b(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        comment: str = 'ORDER_B'
    ) -> Optional[int]:
        """
        Place Order B ONLY (for 1M V6 plugin - scalping)
        
        Order B characteristics:
        - Quick TP target (TP1)
        - Tighter SL
        - Used for scalping/quick exits
        
        Args:
            plugin_id: Plugin identifier
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            lot_size: Lot size for the order
            sl_price: Stop loss price
            tp_price: Take profit price (TP1 - quick exit)
            comment: Order comment
        
        Returns:
            MT5 ticket number or None on failure
        """
        try:
            lot_size = max(0.01, round(lot_size, 2))
            
            logger.info(
                f"[V6_ORDER_B] Placing Order B for {plugin_id}: "
                f"{symbol} {direction} {lot_size} lots"
            )
            
            ticket = self._mt5.place_order(
                symbol=symbol,
                order_type=direction,
                lot_size=lot_size,
                price=0.0,
                sl=sl_price,
                tp=tp_price,
                comment=f"V6_B_{plugin_id}_{comment}"
            )
            
            logger.info(f"[V6_ORDER_B] Order placed: {ticket}")
            return ticket
            
        except Exception as e:
            logger.error(f"[V6_ORDER_B] Error placing order: {e}")
            return None
    
    async def place_dual_orders_v6(
        self,
        plugin_id: str,
        symbol: str,
        direction: str,
        lot_size_total: float,
        sl_price: float,
        tp1_price: float,
        tp2_price: float
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Place DUAL orders for 5M V6 plugin
        
        V6 dual orders use SAME SL for both orders (different from V3):
        - Order A: Extended TP (TP2)
        - Order B: Quick TP (TP1)
        
        Args:
            plugin_id: Plugin identifier
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            lot_size_total: Total lot size (split 50/50)
            sl_price: Same SL for both orders
            tp1_price: Order B target (quick exit)
            tp2_price: Order A target (extended)
        
        Returns:
            Tuple of (order_a_ticket, order_b_ticket)
        """
        try:
            order_a_lot = lot_size_total / 2
            order_b_lot = lot_size_total / 2
            
            order_a_lot = max(0.01, round(order_a_lot, 2))
            order_b_lot = max(0.01, round(order_b_lot, 2))
            
            logger.info(
                f"[V6_DUAL] Placing dual orders for {plugin_id}: "
                f"{symbol} {direction} | A={order_a_lot} B={order_b_lot}"
            )
            
            order_a_ticket = self._mt5.place_order(
                symbol=symbol,
                order_type=direction,
                lot_size=order_a_lot,
                price=0.0,
                sl=sl_price,
                tp=tp2_price,
                comment=f"V6_A_{plugin_id}_DUAL"
            )
            
            order_b_ticket = self._mt5.place_order(
                symbol=symbol,
                order_type=direction,
                lot_size=order_b_lot,
                price=0.0,
                sl=sl_price,
                tp=tp1_price,
                comment=f"V6_B_{plugin_id}_DUAL"
            )
            
            logger.info(
                f"[V6_DUAL] Orders placed: A={order_a_ticket} B={order_b_ticket}"
            )
            
            return (order_a_ticket, order_b_ticket)
            
        except Exception as e:
            logger.error(f"[V6_DUAL] Error placing dual orders: {e}")
            return (None, None)
    
    async def modify_order(
        self,
        plugin_id: str,
        order_id: int,
        new_sl: float = None,
        new_tp: float = None
    ) -> bool:
        """
        Modify existing order SL/TP
        
        Args:
            plugin_id: Plugin identifier for logging
            order_id: MT5 ticket number
            new_sl: New stop loss price (None to keep current)
            new_tp: New take profit price (None to keep current)
        
        Returns:
            True if modification successful
        """
        try:
            logger.info(
                f"[MODIFY] {plugin_id} modifying order {order_id}: "
                f"SL={new_sl} TP={new_tp}"
            )
            
            result = self._mt5.modify_position(
                order_id,
                sl=new_sl or 0.0,
                tp=new_tp or 0.0
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[MODIFY] Error modifying order {order_id}: {e}")
            return False
    
    async def close_position(
        self,
        plugin_id: str,
        order_id: int,
        reason: str = 'Manual'
    ) -> Dict[str, Any]:
        """
        Close entire position
        
        Args:
            plugin_id: Plugin identifier
            order_id: MT5 ticket number
            reason: Close reason for logging
        
        Returns:
            Dict with success status and profit info
        """
        try:
            logger.info(
                f"[CLOSE] {plugin_id} closing position {order_id}: {reason}"
            )
            
            success = self._mt5.close_position(order_id)
            
            return {
                "success": success,
                "order_id": order_id,
                "reason": reason,
                "closed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[CLOSE] Error closing position {order_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def close_position_partial(
        self,
        plugin_id: str,
        order_id: int,
        percentage: float
    ) -> Dict[str, Any]:
        """
        Close partial position (for TP1/TP2/TP3)
        
        Args:
            plugin_id: Plugin identifier
            order_id: MT5 ticket number
            percentage: Percentage to close (25.0 = close 25%)
        
        Returns:
            Dict with closed volume and remaining info
        """
        try:
            logger.info(
                f"[PARTIAL_CLOSE] {plugin_id} closing {percentage}% of {order_id}"
            )
            
            result = self._mt5.close_position_partial(order_id, percentage / 100.0)
            
            return {
                "success": result is not None,
                "order_id": order_id,
                "percentage_closed": percentage
            }
            
        except Exception as e:
            logger.error(f"[PARTIAL_CLOSE] Error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_open_orders(
        self,
        plugin_id: str,
        symbol: str = None
    ) -> List[Dict]:
        """
        Get all open orders for this plugin
        
        Args:
            plugin_id: Plugin identifier (used for filtering by comment)
            symbol: Optional symbol filter
        
        Returns:
            List of open order dictionaries
        """
        try:
            all_positions = self._mt5.get_positions()
            
            if all_positions is None:
                return []
            
            filtered = []
            for pos in all_positions:
                comment = getattr(pos, 'comment', '') or ''
                if plugin_id in comment:
                    if symbol is None or getattr(pos, 'symbol', '') == symbol:
                        filtered.append({
                            "ticket": pos.ticket,
                            "symbol": pos.symbol,
                            "type": "BUY" if pos.type == 0 else "SELL",
                            "volume": pos.volume,
                            "price_open": pos.price_open,
                            "sl": pos.sl,
                            "tp": pos.tp,
                            "profit": pos.profit,
                            "comment": comment
                        })
            
            return filtered
            
        except Exception as e:
            logger.error(f"[GET_ORDERS] Error getting orders for {plugin_id}: {e}")
            return []
