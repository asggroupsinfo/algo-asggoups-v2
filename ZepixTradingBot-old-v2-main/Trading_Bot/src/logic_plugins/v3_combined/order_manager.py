"""
V3 Order Manager - Dual Order System with Hybrid SL

Implements the V3 dual order system:
- Order A (TP Trail): Uses V3 Smart SL from Pine Script, TP2 (extended target)
- Order B (Profit Trail): Uses Fixed $10 SL (IGNORES Pine SL), TP1 (closer target)
- 50/50 lot split between Order A and Order B

CRITICAL RULE: Order B MUST use pyramid fixed $10 SL, NOT smart SL

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING
import logging
import uuid
from datetime import datetime

from src.core.plugin_system.reentry_interface import ReentryEvent, ReentryType

if TYPE_CHECKING:
    from .plugin import CombinedV3Plugin

logger = logging.getLogger(__name__)


class V3OrderManager:
    """
    Manages V3 dual order placement with hybrid SL strategy.
    
    Order A (TP Trail):
    - Uses V3 Smart SL from Pine Script (order block based)
    - Uses TP2 (extended target)
    - Registered for SL hunt re-entry
    
    Order B (Profit Trail):
    - Uses Fixed $10 SL (IGNORES Pine SL to preserve pyramid)
    - Uses TP1 (closer target)
    - Registered for profit chain
    """
    
    def __init__(self, plugin: 'CombinedV3Plugin', service_api):
        """
        Initialize order manager.
        
        Args:
            plugin: Parent CombinedV3Plugin instance
            service_api: ServiceAPI for order placement
        """
        self.plugin = plugin
        self.service_api = service_api
        self.logger = logging.getLogger(f"plugin.{plugin.plugin_id}.orders")
        
        self.dual_config = plugin.plugin_config.get("dual_orders", {})
        self.split_ratio = self.dual_config.get("split_ratio", 0.5)
        self.fixed_sl_dollars = self.dual_config.get("order_b_fixed_sl_dollars", 10.0)
    
    async def place_v3_dual_orders(
        self,
        alert,
        logic_route: str,
        logic_multiplier: float
    ) -> Dict[str, Any]:
        """
        Place dual orders with HYBRID SL strategy.
        
        4-Step Position Sizing Flow:
        1. Get base lot from account tier
        2. Apply V3 consensus multiplier (0.2 to 1.0)
        3. Apply logic multiplier (1.25, 1.0, or 0.625)
        4. Split 50/50 between Order A and Order B
        
        Args:
            alert: Alert data (ZepixV3Alert or dict)
            logic_route: Logic route (combinedlogic-1, combinedlogic-2, combinedlogic-3)
            logic_multiplier: Lot multiplier for logic route
            
        Returns:
            dict: Dual order placement result
        """
        try:
            symbol = self._get_symbol(alert)
            direction = self._get_direction(alert)
            price = self._get_price(alert)
            signal_type = self._get_signal_type(alert)
            consensus_score = self._get_consensus_score(alert)
            
            chain_id = f"{symbol}_{uuid.uuid4().hex[:8]}"
            
            base_lot = await self._get_base_lot(symbol)
            
            v3_multiplier = self._map_consensus_to_multiplier(consensus_score)
            
            final_lot = base_lot * v3_multiplier * logic_multiplier
            
            order_a_lot = final_lot * self.split_ratio
            order_b_lot = final_lot * (1 - self.split_ratio)
            
            self.logger.info(
                f"V3 Position Sizing:\n"
                f"  Base Lot: {base_lot:.4f}\n"
                f"  V3 Multiplier (consensus {consensus_score}): {v3_multiplier}\n"
                f"  Logic Multiplier ({logic_route}): {logic_multiplier}\n"
                f"  Final Lot: {final_lot:.4f}\n"
                f"  Order A: {order_a_lot:.4f} | Order B: {order_b_lot:.4f}"
            )
            
            order_a_params = await self._calculate_order_a_params(
                alert, price, direction, order_a_lot, logic_route
            )
            
            order_b_params = await self._calculate_order_b_params(
                alert, price, direction, order_b_lot, logic_route
            )
            
            order_a_result = await self._place_order_a(
                symbol, direction, order_a_params, logic_route, chain_id, alert
            )
            
            order_b_result = await self._place_order_b(
                symbol, direction, order_b_params, logic_route, chain_id, alert
            )
            
            await self._send_dual_order_notification(
                alert, order_a_result, order_b_result, logic_route
            )
            
            return {
                "status": "success" if (order_a_result.get("placed") or order_b_result.get("placed")) else "error",
                "order_a_placed": order_a_result.get("placed", False),
                "order_b_placed": order_b_result.get("placed", False),
                "order_a_id": order_a_result.get("trade_id"),
                "order_b_id": order_b_result.get("trade_id"),
                "logic_route": logic_route,
                "chain_id": chain_id,
                "order_a_params": order_a_params,
                "order_b_params": order_b_params
            }
            
        except Exception as e:
            self.logger.error(f"V3 Dual Order Error: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    async def _get_base_lot(self, symbol: str) -> float:
        """
        Get base lot size from account tier.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            float: Base lot size
        """
        try:
            lot_info = self.service_api.calculate_lot_size(
                symbol=symbol
            )
            return lot_info.get("lot_size", 0.01)
        except Exception as e:
            self.logger.warning(f"Failed to get base lot, using default: {e}")
            return 0.01
    
    def _map_consensus_to_multiplier(self, consensus_score: int) -> float:
        """
        Map consensus score (0-9) to lot multiplier.
        
        Mapping:
        - 0-3: 0.2 to 0.5 (low confidence)
        - 4-6: 0.6 to 0.8 (medium confidence)
        - 7-9: 0.9 to 1.0 (high confidence)
        
        Args:
            consensus_score: Consensus score from Pine (0-9)
            
        Returns:
            float: Lot multiplier (0.2 to 1.0)
        """
        if consensus_score <= 0:
            return 0.2
        elif consensus_score <= 3:
            return 0.2 + (consensus_score * 0.1)
        elif consensus_score <= 6:
            return 0.5 + ((consensus_score - 3) * 0.1)
        elif consensus_score <= 8:
            return 0.8 + ((consensus_score - 6) * 0.05)
        else:
            return 1.0
    
    async def _calculate_order_a_params(
        self,
        alert,
        price: float,
        direction: str,
        lot_size: float,
        logic_route: str
    ) -> Dict[str, Any]:
        """
        Calculate Order A parameters (TP Trail - Smart SL).
        
        Order A uses:
        - V3 Smart SL from Pine Script (if provided)
        - TP2 (extended target)
        
        Args:
            alert: Alert data
            price: Entry price
            direction: Trade direction
            lot_size: Lot size for Order A
            logic_route: Logic route
            
        Returns:
            dict: Order A parameters
        """
        sl_price = self._get_sl_price(alert)
        tp2_price = self._get_tp2_price(alert)
        
        if sl_price:
            self.logger.info(f"Order A: Using V3 Smart SL = {sl_price:.5f}")
        else:
            sl_price = await self._calculate_fallback_sl(price, direction, lot_size, logic_route)
            self.logger.warning(f"Order A: V3 SL missing, using bot SL = {sl_price:.5f}")
        
        if tp2_price:
            self.logger.info(f"Order A: Using V3 Extended TP = {tp2_price:.5f}")
        else:
            rr_ratio = self.plugin.plugin_config.get("rr_ratio", 1.5)
            sl_distance = abs(price - sl_price)
            if direction.lower() == "buy":
                tp2_price = price + (sl_distance * rr_ratio)
            else:
                tp2_price = price - (sl_distance * rr_ratio)
            self.logger.warning(f"Order A: V3 TP missing, using bot TP = {tp2_price:.5f}")
        
        return {
            "entry": price,
            "sl": sl_price,
            "tp": tp2_price,
            "lot_size": lot_size,
            "order_type": "TP_TRAIL",
            "sl_source": "V3_SMART"
        }
    
    async def _calculate_order_b_params(
        self,
        alert,
        price: float,
        direction: str,
        lot_size: float,
        logic_route: str
    ) -> Dict[str, Any]:
        """
        Calculate Order B parameters (Profit Trail - Fixed $10 SL).
        
        CRITICAL: Order B IGNORES V3 SL and uses Fixed $10 SL
        to preserve pyramid system.
        
        Order B uses:
        - Fixed $10 SL (calculated from price)
        - TP1 (closer target)
        
        Args:
            alert: Alert data
            price: Entry price
            direction: Trade direction
            lot_size: Lot size for Order B
            logic_route: Logic route
            
        Returns:
            dict: Order B parameters
        """
        v3_sl = self._get_sl_price(alert)
        tp1_price = self._get_tp1_price(alert)
        
        sl_price = await self._calculate_fixed_dollar_sl(price, direction, lot_size)
        
        if v3_sl:
            self.logger.info(
                f"Order B: Using Fixed $10 SL = {sl_price:.5f} "
                f"(IGNORED V3 SL = {v3_sl:.5f} to preserve pyramid)"
            )
        else:
            self.logger.info(f"Order B: Using Fixed $10 SL = {sl_price:.5f}")
        
        if tp1_price:
            self.logger.info(f"Order B: Using V3 Closer TP = {tp1_price:.5f}")
        else:
            sl_distance = abs(price - sl_price)
            if direction.lower() == "buy":
                tp1_price = price + sl_distance
            else:
                tp1_price = price - sl_distance
            self.logger.warning(f"Order B: V3 TP missing, using bot TP = {tp1_price:.5f}")
        
        return {
            "entry": price,
            "sl": sl_price,
            "tp": tp1_price,
            "lot_size": lot_size,
            "order_type": "PROFIT_TRAIL",
            "sl_source": "FIXED_PYRAMID"
        }
    
    async def _calculate_fallback_sl(
        self,
        price: float,
        direction: str,
        lot_size: float,
        logic_route: str
    ) -> float:
        """
        Calculate fallback SL when V3 SL is not provided.
        
        Args:
            price: Entry price
            direction: Trade direction
            lot_size: Lot size
            logic_route: Logic route
            
        Returns:
            float: Calculated SL price
        """
        try:
            sl_info = await self.service_api.calculate_sl_price(
                plugin_id=self.plugin.plugin_id,
                price=price,
                direction=direction,
                lot_size=lot_size
            )
            return sl_info.get("sl_price", price * 0.99 if direction.lower() == "buy" else price * 1.01)
        except Exception as e:
            self.logger.warning(f"Fallback SL calculation failed: {e}")
            if direction.lower() == "buy":
                return price * 0.99
            else:
                return price * 1.01
    
    async def _calculate_fixed_dollar_sl(
        self,
        price: float,
        direction: str,
        lot_size: float
    ) -> float:
        """
        Calculate fixed $10 SL for Order B.
        
        Formula: SL distance = $10 / (lot_size * pip_value)
        
        Args:
            price: Entry price
            direction: Trade direction
            lot_size: Lot size
            
        Returns:
            float: Fixed $10 SL price
        """
        try:
            pip_value = 10.0
            
            sl_distance_pips = self.fixed_sl_dollars / (lot_size * pip_value)
            
            point_value = 0.01 if price > 100 else 0.0001
            sl_distance = sl_distance_pips * point_value * 10
            
            if direction.lower() == "buy":
                return price - sl_distance
            else:
                return price + sl_distance
                
        except Exception as e:
            self.logger.warning(f"Fixed SL calculation failed: {e}")
            if direction.lower() == "buy":
                return price * 0.995
            else:
                return price * 1.005
    
    async def _place_order_a(
        self,
        symbol: str,
        direction: str,
        params: Dict[str, Any],
        logic_route: str,
        chain_id: str,
        alert
    ) -> Dict[str, Any]:
        """
        Place Order A (TP Trail - Smart SL).
        
        Args:
            symbol: Trading symbol
            direction: Trade direction
            params: Order parameters
            logic_route: Logic route
            chain_id: Shared chain ID
            alert: Original alert
            
        Returns:
            dict: Order placement result
        """
        try:
            if self.plugin.shadow_mode:
                self.logger.info(f"[SHADOW] Order A would be placed: {params}")
                return {"placed": False, "shadow": True}
            
            result = await self.service_api.place_order_async(
                symbol=symbol,
                direction=direction,
                lot_size=params["lot_size"],
                entry_price=params["entry"],
                sl_price=params["sl"],
                tp_price=params["tp"],
                comment=f"{logic_route}_V3_A",
                metadata={
                    "order_type": "TP_TRAIL",
                    "chain_id": chain_id,
                    "sl_source": "V3_SMART",
                    "signal_type": self._get_signal_type(alert),
                    "consensus_score": self._get_consensus_score(alert)
                }
            )
            
            if result.get("success"):
                self.logger.info(f"Order A placed: {result.get('trade_id')}")
                return {"placed": True, "trade_id": result.get("trade_id")}
            else:
                self.logger.error(f"Order A failed: {result.get('error')}")
                return {"placed": False, "error": result.get("error")}
                
        except Exception as e:
            self.logger.error(f"Order A placement error: {e}")
            return {"placed": False, "error": str(e)}
    
    async def _place_order_b(
        self,
        symbol: str,
        direction: str,
        params: Dict[str, Any],
        logic_route: str,
        chain_id: str,
        alert
    ) -> Dict[str, Any]:
        """
        Place Order B (Profit Trail - Fixed $10 SL).
        
        Args:
            symbol: Trading symbol
            direction: Trade direction
            params: Order parameters
            logic_route: Logic route
            chain_id: Shared chain ID
            alert: Original alert
            
        Returns:
            dict: Order placement result
        """
        try:
            if self.plugin.shadow_mode:
                self.logger.info(f"[SHADOW] Order B would be placed: {params}")
                return {"placed": False, "shadow": True}
            
            result = await self.service_api.place_order_async(
                symbol=symbol,
                direction=direction,
                lot_size=params["lot_size"],
                entry_price=params["entry"],
                sl_price=params["sl"],
                tp_price=params["tp"],
                comment=f"{logic_route}_V3_B",
                metadata={
                    "order_type": "PROFIT_TRAIL",
                    "chain_id": chain_id,
                    "sl_source": "FIXED_PYRAMID",
                    "signal_type": self._get_signal_type(alert),
                    "consensus_score": self._get_consensus_score(alert)
                }
            )
            
            if result.get("success"):
                self.logger.info(f"Order B placed: {result.get('trade_id')}")
                return {"placed": True, "trade_id": result.get("trade_id")}
            else:
                self.logger.error(f"Order B failed: {result.get('error')}")
                return {"placed": False, "error": result.get("error")}
                
        except Exception as e:
            self.logger.error(f"Order B placement error: {e}")
            return {"placed": False, "error": str(e)}
    
    async def _send_dual_order_notification(
        self,
        alert,
        order_a_result: Dict[str, Any],
        order_b_result: Dict[str, Any],
        logic_route: str
    ) -> None:
        """
        Send notification about dual order placement.
        
        Args:
            alert: Original alert
            order_a_result: Order A result
            order_b_result: Order B result
            logic_route: Logic route
        """
        try:
            signal_type = self._get_signal_type(alert)
            symbol = self._get_symbol(alert)
            direction = self._get_direction(alert)
            consensus = self._get_consensus_score(alert)
            
            order_a_placed = order_a_result.get("placed", False)
            order_b_placed = order_b_result.get("placed", False)
            
            if order_a_placed and order_b_placed:
                message = (
                    f"V3 DUAL ORDER PLACED\n"
                    f"Signal: {signal_type}\n"
                    f"Score: {consensus}/9\n"
                    f"Logic: {logic_route}\n"
                    f"Symbol: {symbol}\n"
                    f"Direction: {direction.upper()}\n\n"
                    f"Order A (TP Trail - V3 Smart SL): PLACED\n"
                    f"Order B (Profit Trail - Fixed SL): PLACED"
                )
                priority = "high"
            elif order_a_placed:
                message = (
                    f"V3 Order: Only Order A placed (Order B failed)\n"
                    f"Signal: {signal_type}"
                )
                priority = "medium"
            elif order_b_placed:
                message = (
                    f"V3 Order: Only Order B placed (Order A failed)\n"
                    f"Signal: {signal_type}"
                )
                priority = "medium"
            else:
                message = (
                    f"V3 Order: Both orders failed\n"
                    f"Signal: {signal_type}"
                )
                priority = "critical"
            
            self.service_api.send_notification(
                message=message,
                priority=priority
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to send notification: {e}")
    
    def _get_signal_type(self, alert) -> str:
        """Extract signal_type from alert"""
        if hasattr(alert, 'signal_type'):
            return alert.signal_type
        if isinstance(alert, dict):
            return alert.get('signal_type', '')
        return ''
    
    def _get_symbol(self, alert) -> str:
        """Extract symbol from alert"""
        if hasattr(alert, 'symbol'):
            return alert.symbol
        if isinstance(alert, dict):
            return alert.get('symbol', '')
        return ''
    
    def _get_direction(self, alert) -> str:
        """Extract direction from alert"""
        if hasattr(alert, 'direction'):
            return alert.direction
        if isinstance(alert, dict):
            return alert.get('direction', '')
        return ''
    
    def _get_price(self, alert) -> float:
        """Extract price from alert"""
        if hasattr(alert, 'price'):
            return float(alert.price)
        if isinstance(alert, dict):
            return float(alert.get('price', 0))
        return 0.0
    
    def _get_consensus_score(self, alert) -> int:
        """Extract consensus_score from alert"""
        if hasattr(alert, 'consensus_score'):
            return int(alert.consensus_score)
        if isinstance(alert, dict):
            return int(alert.get('consensus_score', 0))
        return 0
    
    def _get_sl_price(self, alert) -> Optional[float]:
        """Extract sl_price from alert"""
        if hasattr(alert, 'sl_price') and alert.sl_price:
            return float(alert.sl_price)
        if isinstance(alert, dict) and alert.get('sl_price'):
            return float(alert.get('sl_price'))
        return None
    
    def _get_tp1_price(self, alert) -> Optional[float]:
        """Extract tp1_price from alert"""
        if hasattr(alert, 'tp1_price') and alert.tp1_price:
            return float(alert.tp1_price)
        if isinstance(alert, dict) and alert.get('tp1_price'):
            return float(alert.get('tp1_price'))
        return None
    
    def _get_tp2_price(self, alert) -> Optional[float]:
        """Extract tp2_price from alert"""
        if hasattr(alert, 'tp2_price') and alert.tp2_price:
            return float(alert.tp2_price)
        if isinstance(alert, dict) and alert.get('tp2_price'):
            return float(alert.get('tp2_price'))
        return None
    
    # =========================================================================
    # Re-Entry Event Triggers (Plan 03 - Step 4)
    # =========================================================================
    
    async def on_order_closed(
        self,
        order_id: str,
        close_reason: str,
        close_price: float,
        order_metadata: Dict[str, Any]
    ) -> None:
        """
        Handle order close event and trigger appropriate re-entry.
        
        This method is called when an order is closed (SL hit, TP hit, manual exit).
        It creates a ReentryEvent and triggers the appropriate plugin method.
        
        Args:
            order_id: MT5 order/position ID
            close_reason: Reason for close (sl_hit, tp_hit, manual_exit, reversal_exit)
            close_price: Price at which order was closed
            order_metadata: Order metadata including symbol, direction, entry_price, etc.
        """
        self.logger.info(
            f"Order closed: {order_id} | Reason: {close_reason} | Price: {close_price}"
        )
        
        # Extract order details from metadata
        symbol = order_metadata.get("symbol", "")
        direction = order_metadata.get("direction", "")
        entry_price = order_metadata.get("entry_price", 0.0)
        sl_price = order_metadata.get("sl_price", 0.0)
        chain_id = order_metadata.get("chain_id", "")
        order_type = order_metadata.get("order_type", "")
        
        # Determine re-entry type based on close reason
        if close_reason == "sl_hit":
            reentry_type = ReentryType.SL_HUNT
        elif close_reason == "tp_hit":
            reentry_type = ReentryType.TP_CONTINUATION
        elif close_reason in ("manual_exit", "reversal_exit"):
            reentry_type = ReentryType.EXIT_CONTINUATION
        else:
            self.logger.info(f"No re-entry for close reason: {close_reason}")
            return
        
        # Create ReentryEvent
        event = ReentryEvent(
            trade_id=order_id,
            plugin_id=self.plugin.plugin_id,
            symbol=symbol,
            reentry_type=reentry_type,
            entry_price=entry_price,
            exit_price=close_price,
            sl_price=sl_price,
            direction=direction,
            chain_level=self.plugin.get_chain_level(chain_id),
            metadata={
                "chain_id": chain_id,
                "order_type": order_type,
                "close_reason": close_reason,
                **order_metadata
            }
        )
        
        # Trigger appropriate plugin method
        try:
            if reentry_type == ReentryType.SL_HUNT:
                await self.plugin.on_sl_hit(event)
            elif reentry_type == ReentryType.TP_CONTINUATION:
                await self.plugin.on_tp_hit(event)
            elif reentry_type == ReentryType.EXIT_CONTINUATION:
                await self.plugin.on_exit(event)
        except Exception as e:
            self.logger.error(f"Re-entry trigger failed: {e}")
    
    async def execute_recovery_order(self, signal: Dict[str, Any]) -> bool:
        """
        Execute a recovery re-entry order.
        
        Called by plugin.on_recovery_signal when recovery is detected.
        
        Args:
            signal: Recovery signal with entry details
            
        Returns:
            bool: True if order placed successfully
        """
        try:
            symbol = signal.get("symbol", "")
            direction = signal.get("direction", "")
            entry_price = signal.get("entry_price", 0.0)
            sl_price = signal.get("sl_price", 0.0)
            chain_level = signal.get("chain_level", 0)
            recovery_type = signal.get("recovery_type", "")
            original_trade_id = signal.get("original_trade_id", "")
            
            # Calculate lot size for recovery (may be reduced based on chain level)
            base_lot = await self._get_base_lot(symbol)
            
            # Reduce lot size for higher chain levels (10% reduction per level)
            lot_reduction = 1.0 - (0.1 * chain_level)
            lot_reduction = max(lot_reduction, 0.5)  # Min 50% of original
            recovery_lot = base_lot * lot_reduction
            
            # Calculate TP based on recovery type
            sl_distance = abs(entry_price - sl_price)
            if direction.lower() == "buy":
                tp_price = entry_price + (sl_distance * 1.5)  # 1.5 RR for recovery
            else:
                tp_price = entry_price - (sl_distance * 1.5)
            
            self.logger.info(
                f"Executing recovery order:\n"
                f"  Type: {recovery_type}\n"
                f"  Symbol: {symbol}\n"
                f"  Direction: {direction}\n"
                f"  Entry: {entry_price}\n"
                f"  SL: {sl_price}\n"
                f"  TP: {tp_price}\n"
                f"  Lot: {recovery_lot} (chain level {chain_level})"
            )
            
            if self.plugin.shadow_mode:
                self.logger.info(f"[SHADOW] Recovery order would be placed")
                return True
            
            # Place recovery order
            result = await self.service_api.place_order_async(
                symbol=symbol,
                direction=direction,
                lot_size=recovery_lot,
                entry_price=entry_price,
                sl_price=sl_price,
                tp_price=tp_price,
                comment=f"RECOVERY_{recovery_type}_{chain_level}",
                metadata={
                    "order_type": "RECOVERY",
                    "recovery_type": recovery_type,
                    "chain_level": chain_level,
                    "original_trade_id": original_trade_id,
                    **signal.get("metadata", {})
                }
            )
            
            if result.get("success"):
                self.logger.info(f"Recovery order placed: {result.get('trade_id')}")
                
                # Send notification
                self.service_api.send_notification(
                    message=(
                        f"RECOVERY ORDER PLACED\n"
                        f"Type: {recovery_type}\n"
                        f"Symbol: {symbol}\n"
                        f"Direction: {direction.upper()}\n"
                        f"Chain Level: {chain_level}"
                    ),
                    priority="high"
                )
                return True
            else:
                self.logger.error(f"Recovery order failed: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Recovery order execution error: {e}")
            return False
    
    async def close_order(self, order_id: str, reason: str) -> bool:
        """
        Close an order and trigger re-entry if applicable.
        
        Args:
            order_id: MT5 order/position ID
            reason: Reason for closing
            
        Returns:
            bool: True if close successful
        """
        try:
            # Get order details before closing
            order_info = await self.service_api.get_order_info(
                plugin_id=self.plugin.plugin_id,
                order_id=order_id
            )
            
            if not order_info:
                self.logger.warning(f"Order {order_id} not found")
                return False
            
            # Close the order
            result = await self.service_api.close_order(
                plugin_id=self.plugin.plugin_id,
                order_id=order_id,
                reason=reason
            )
            
            if result.get("success"):
                close_price = result.get("close_price", order_info.get("current_price", 0))
                
                # Trigger re-entry event
                await self.on_order_closed(
                    order_id=order_id,
                    close_reason=reason,
                    close_price=close_price,
                    order_metadata=order_info
                )
                
                return True
            else:
                self.logger.error(f"Order close failed: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Order close error: {e}")
            return False
