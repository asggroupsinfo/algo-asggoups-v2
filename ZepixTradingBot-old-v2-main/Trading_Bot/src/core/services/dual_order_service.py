"""
Dual Order Service
Plan 04: Dual Order System Integration

Provides dual order functionality to plugins via ServiceAPI.
Handles Order A (TP_TRAIL) and Order B (PROFIT_TRAIL) creation and management.
"""
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging

from src.core.plugin_system.dual_order_interface import (
    OrderConfig, DualOrderResult, OrderType, SLType
)

logger = logging.getLogger(__name__)


class DualOrderService:
    """
    Service layer for dual order operations.
    Plugins use this instead of calling managers directly.
    
    Features:
    - Creates Order A with V3 Smart SL (trailing)
    - Creates Order B with fixed $10 risk SL
    - Applies smart lot adjustment based on daily P&L
    - Tracks orders by plugin for proper lifecycle management
    - Tags all orders with plugin_id for tracking
    """
    
    def __init__(
        self,
        dual_order_manager: Optional[Any] = None,
        risk_manager: Optional[Any] = None
    ):
        """
        Initialize DualOrderService.
        
        Args:
            dual_order_manager: DualOrderManager instance (optional)
            risk_manager: RiskManager instance (optional)
        """
        self.dual_order_manager = dual_order_manager
        self.risk_manager = risk_manager
        
        # Track orders by plugin: plugin_id -> {order_id: order_type}
        self._plugin_orders: Dict[str, Dict[str, str]] = {}
        
        # Order close callbacks: order_id -> callback
        self._close_callbacks: Dict[str, Callable] = {}
        
        # Statistics
        self._stats = {
            'total_order_a_created': 0,
            'total_order_b_created': 0,
            'total_dual_orders_created': 0,
            'failed_creations': 0,
            'blocked_by_limits': 0
        }
        self._last_reset = datetime.now()
    
    def set_managers(
        self,
        dual_order_manager: Any = None,
        risk_manager: Any = None
    ):
        """Set manager instances after initialization"""
        if dual_order_manager:
            self.dual_order_manager = dual_order_manager
        if risk_manager:
            self.risk_manager = risk_manager
    
    async def create_dual_orders(
        self,
        signal: Dict[str, Any],
        order_a_config: OrderConfig,
        order_b_config: OrderConfig
    ) -> DualOrderResult:
        """
        Create both Order A and Order B.
        
        Args:
            signal: Trading signal with symbol, direction, etc.
            order_a_config: Configuration for Order A (TP_TRAIL)
            order_b_config: Configuration for Order B (PROFIT_TRAIL)
        
        Returns:
            DualOrderResult with both order IDs and status
        """
        result = DualOrderResult()
        
        # Check risk limits first
        if self.risk_manager and not self._check_daily_limit():
            result.error = "Daily loss limit reached"
            self._stats['blocked_by_limits'] += 1
            logger.warning(result.error)
            return result
        
        # Apply smart lot adjustment
        adjusted_lot_a = self._apply_smart_lot(order_a_config.lot_size)
        adjusted_lot_b = self._apply_smart_lot(order_b_config.lot_size)
        
        # Create Order A (TP_TRAIL with V3 Smart SL)
        try:
            order_a = await self._create_order_a(signal, order_a_config, adjusted_lot_a)
            if order_a:
                result.order_a_id = order_a.get('order_id', str(order_a.get('ticket', '')))
                result.order_a_status = "executed"
                self._track_order(order_a_config.plugin_id, result.order_a_id, 'order_a')
                self._stats['total_order_a_created'] += 1
                logger.info(f"Order A created: {result.order_a_id} for plugin {order_a_config.plugin_id}")
        except Exception as e:
            result.order_a_status = f"failed: {e}"
            self._stats['failed_creations'] += 1
            logger.error(f"Order A creation failed: {e}")
        
        # Create Order B (PROFIT_TRAIL with fixed risk SL)
        try:
            order_b = await self._create_order_b(signal, order_b_config, adjusted_lot_b)
            if order_b:
                result.order_b_id = order_b.get('order_id', str(order_b.get('ticket', '')))
                result.order_b_status = "executed"
                self._track_order(order_b_config.plugin_id, result.order_b_id, 'order_b')
                self._stats['total_order_b_created'] += 1
                logger.info(f"Order B created: {result.order_b_id} for plugin {order_b_config.plugin_id}")
        except Exception as e:
            result.order_b_status = f"failed: {e}"
            self._stats['failed_creations'] += 1
            logger.error(f"Order B creation failed: {e}")
        
        result.total_lot_size = adjusted_lot_a + adjusted_lot_b
        
        if result.order_a_id or result.order_b_id:
            self._stats['total_dual_orders_created'] += 1
        
        return result
    
    async def _create_order_a(
        self,
        signal: Dict[str, Any],
        config: OrderConfig,
        lot_size: float
    ) -> Optional[Dict[str, Any]]:
        """
        Create Order A with V3 Smart SL.
        
        Order A characteristics:
        - Uses V3 Smart SL with progressive trailing
        - Has TP target (typically 2:1 RR)
        - Trailing starts at 50% of SL in profit
        - Trails in 25% steps
        """
        order_params = {
            'symbol': signal.get('symbol'),
            'direction': signal.get('signal_type'),
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
        
        if self.dual_order_manager:
            try:
                return await self.dual_order_manager.create_order_a(order_params)
            except (TypeError, AttributeError) as e:
                logger.debug(f"DualOrderManager.create_order_a not available: {e}")
        
        # Return mock order if no manager
        return {
            'order_id': f"order_a_{datetime.now().timestamp()}",
            'ticket': int(datetime.now().timestamp()),
            'status': 'simulated',
            **order_params
        }
    
    async def _create_order_b(
        self,
        signal: Dict[str, Any],
        config: OrderConfig,
        lot_size: float
    ) -> Optional[Dict[str, Any]]:
        """
        Create Order B with fixed risk SL.
        
        Order B characteristics:
        - Uses fixed $10 risk SL
        - No TP target (uses profit booking)
        - Creates profit booking chains
        """
        # Calculate SL based on fixed risk amount
        sl_pips = self._calculate_fixed_risk_sl(
            signal.get('symbol', 'EURUSD'),
            lot_size,
            config.risk_amount
        )
        
        order_params = {
            'symbol': signal.get('symbol'),
            'direction': signal.get('signal_type'),
            'lot_size': lot_size,
            'sl_pips': sl_pips,
            'tp_pips': None,  # Order B uses profit booking, not TP
            'order_type': 'ORDER_B',
            'sl_management': 'FIXED_RISK_SL',
            'risk_amount': config.risk_amount,
            'plugin_id': config.plugin_id,
            'metadata': config.metadata or {}
        }
        
        if self.dual_order_manager:
            try:
                return await self.dual_order_manager.create_order_b(order_params)
            except (TypeError, AttributeError) as e:
                logger.debug(f"DualOrderManager.create_order_b not available: {e}")
        
        # Return mock order if no manager
        return {
            'order_id': f"order_b_{datetime.now().timestamp()}",
            'ticket': int(datetime.now().timestamp()),
            'status': 'simulated',
            **order_params
        }
    
    def _check_daily_limit(self) -> bool:
        """Check if daily limit allows trading"""
        if not self.risk_manager:
            return True
        try:
            return self.risk_manager.check_daily_limit()
        except (AttributeError, TypeError):
            return True
    
    def _apply_smart_lot(self, base_lot: float) -> float:
        """
        Apply smart lot adjustment based on daily P&L.
        
        Discovery 6: Reduces lot when near daily limit:
        - >50% remaining: 100% of base lot
        - 25-50% remaining: 75% of base lot
        - <25% remaining: 50% of base lot
        
        Args:
            base_lot: Base lot size
            
        Returns:
            Adjusted lot size
        """
        if not self.risk_manager:
            return base_lot
        
        try:
            daily_pnl = self.risk_manager.get_daily_pnl()
            daily_limit = self.risk_manager.get_daily_limit()
        except (AttributeError, TypeError):
            return base_lot
        
        # Calculate how close we are to daily limit
        remaining = daily_limit - abs(daily_pnl)
        limit_ratio = remaining / daily_limit if daily_limit > 0 else 1.0
        
        # Reduce lot size as we approach limit
        if limit_ratio < 0.25:  # Less than 25% remaining
            adjustment = 0.50  # 50% of base lot
        elif limit_ratio < 0.50:  # Less than 50% remaining
            adjustment = 0.75  # 75% of base lot
        else:
            adjustment = 1.0  # Full lot
        
        adjusted_lot = base_lot * adjustment
        
        if adjustment < 1.0:
            logger.info(
                f"Smart lot adjustment: {base_lot} -> {adjusted_lot} "
                f"(limit ratio: {limit_ratio:.2f})"
            )
        
        return adjusted_lot
    
    def _calculate_fixed_risk_sl(
        self,
        symbol: str,
        lot_size: float,
        risk_amount: float
    ) -> float:
        """
        Calculate SL pips for fixed risk amount.
        
        For Order B: Fixed $10 risk by default.
        
        Args:
            symbol: Trading symbol
            lot_size: Lot size
            risk_amount: Fixed risk amount in USD
            
        Returns:
            SL in pips
        """
        # Get pip value for symbol
        pip_value = self._get_pip_value(symbol, lot_size)
        
        # Calculate SL pips: risk_amount / pip_value
        sl_pips = risk_amount / pip_value if pip_value > 0 else 15
        
        return round(sl_pips, 1)
    
    def _get_pip_value(self, symbol: str, lot_size: float) -> float:
        """
        Get pip value for a symbol and lot size.
        
        Args:
            symbol: Trading symbol
            lot_size: Lot size
            
        Returns:
            Pip value in USD
        """
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
        """
        Track order ownership by plugin.
        
        Args:
            plugin_id: Plugin identifier
            order_id: Order identifier
            order_type: 'order_a' or 'order_b'
        """
        if plugin_id not in self._plugin_orders:
            self._plugin_orders[plugin_id] = {}
        self._plugin_orders[plugin_id][order_id] = order_type
        logger.debug(f"Tracking order {order_id} ({order_type}) for plugin {plugin_id}")
    
    def _untrack_order(self, order_id: str) -> Optional[str]:
        """
        Remove order from tracking.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Plugin ID that owned the order, or None
        """
        for plugin_id, orders in self._plugin_orders.items():
            if order_id in orders:
                del orders[order_id]
                return plugin_id
        return None
    
    def get_plugin_orders(self, plugin_id: str) -> Dict[str, str]:
        """
        Get all orders for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Dict of order_id -> order_type
        """
        return self._plugin_orders.get(plugin_id, {}).copy()
    
    def get_order_type(self, order_id: str) -> Optional[str]:
        """
        Get order type (order_a or order_b) for an order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            'order_a', 'order_b', or None
        """
        for plugin_orders in self._plugin_orders.values():
            if order_id in plugin_orders:
                return plugin_orders[order_id]
        return None
    
    def get_order_plugin(self, order_id: str) -> Optional[str]:
        """
        Get plugin ID for an order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Plugin ID or None
        """
        for plugin_id, orders in self._plugin_orders.items():
            if order_id in orders:
                return plugin_id
        return None
    
    def register_close_callback(self, order_id: str, callback: Callable):
        """
        Register a callback for order close events.
        
        Args:
            order_id: Order identifier
            callback: Async callback function
        """
        self._close_callbacks[order_id] = callback
    
    async def on_order_closed(self, order_id: str, reason: str, close_price: float):
        """
        Handle order close event.
        
        Args:
            order_id: Order identifier
            reason: Close reason
            close_price: Price at close
        """
        callback = self._close_callbacks.pop(order_id, None)
        if callback:
            try:
                await callback(order_id, reason, close_price)
            except Exception as e:
                logger.error(f"Order close callback error: {e}")
        
        self._untrack_order(order_id)
    
    async def modify_order_sl(self, order_id: str, new_sl_pips: float) -> bool:
        """
        Modify order SL.
        
        Args:
            order_id: Order identifier
            new_sl_pips: New SL in pips
            
        Returns:
            True if successful
        """
        if self.dual_order_manager:
            try:
                return await self.dual_order_manager.modify_order_sl(order_id, new_sl_pips)
            except (TypeError, AttributeError):
                pass
        return False
    
    async def close_order(self, order_id: str, reason: str) -> bool:
        """
        Close an order.
        
        Args:
            order_id: Order identifier
            reason: Close reason
            
        Returns:
            True if successful
        """
        if self.dual_order_manager:
            try:
                return await self.dual_order_manager.close_order(order_id, reason)
            except (TypeError, AttributeError):
                pass
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            **self._stats,
            'active_orders': sum(len(orders) for orders in self._plugin_orders.values()),
            'plugins_with_orders': len(self._plugin_orders),
            'last_reset': self._last_reset.isoformat()
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self._stats = {
            'total_order_a_created': 0,
            'total_order_b_created': 0,
            'total_dual_orders_created': 0,
            'failed_creations': 0,
            'blocked_by_limits': 0
        }
        self._last_reset = datetime.now()


# Singleton instance
_dual_order_service: Optional[DualOrderService] = None


def get_dual_order_service() -> DualOrderService:
    """Get or create the singleton DualOrderService instance"""
    global _dual_order_service
    if _dual_order_service is None:
        _dual_order_service = DualOrderService()
    return _dual_order_service


def reset_dual_order_service():
    """Reset the singleton instance (for testing)"""
    global _dual_order_service
    _dual_order_service = None
