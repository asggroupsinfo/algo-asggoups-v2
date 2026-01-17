"""
Intelligent Trade Manager - Complete Bot Intelligence System

Implements Mandate 23 requirements:
1. Intelligent Entry (Order A + Order B with Pine TP/SL)
2. TP Management (TP1/TP2/TP3 intelligent profit booking)
3. SL Hunting with 70% recovery re-entry
4. Exit Signal Intelligence
5. Smart Lot Sizing

Version: 1.0.0
Date: 2026-01-17
"""

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class TradeState(Enum):
    """Trade lifecycle states"""
    PENDING = "pending"
    ACTIVE = "active"
    TP1_HIT = "tp1_hit"
    TP2_HIT = "tp2_hit"
    TP3_HIT = "tp3_hit"
    SL_HIT = "sl_hit"
    SL_HUNTING = "sl_hunting"
    RECOVERY_ACTIVE = "recovery_active"
    CLOSED = "closed"


class OrderType(Enum):
    """Order types for dual order system"""
    ORDER_A = "order_a"  # Main position targeting TP3
    ORDER_B = "order_b"  # Quick profit at TP1


@dataclass
class TradeContext:
    """Complete trade context for intelligent management"""
    trade_id: str
    symbol: str
    direction: str  # BUY or SELL
    entry_price: float
    sl_price: float
    tp1_price: float
    tp2_price: float
    tp3_price: float
    order_a_id: Optional[str] = None
    order_b_id: Optional[str] = None
    order_a_lot: float = 0.0
    order_b_lot: float = 0.0
    state: TradeState = TradeState.PENDING
    order_a_state: TradeState = TradeState.PENDING
    order_b_state: TradeState = TradeState.PENDING
    partial_closes: List[Dict] = field(default_factory=list)
    sl_hunt_active: bool = False
    recovery_price: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PineUpdate:
    """Real-time Pine Script update data"""
    trend: str  # BULLISH, BEARISH, NEUTRAL
    adx: float
    confidence: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_strong(self) -> bool:
        """Check if conditions are strong for holding position"""
        return self.adx >= 25 and self.confidence >= 70
    
    def is_aligned(self, direction: str) -> bool:
        """Check if trend is aligned with trade direction"""
        if direction.upper() == "BUY":
            return self.trend.upper() in ["BULLISH", "TRENDING_BULLISH"]
        else:
            return self.trend.upper() in ["BEARISH", "TRENDING_BEARISH"]


@dataclass
class SmartLotResult:
    """Result of smart lot calculation"""
    lot_size: float
    risk_amount: float
    sl_pips: float
    risk_percent: float
    capped: bool = False
    cap_reason: str = ""


class IntelligentTradeManager:
    """
    Manages intelligent trade execution and monitoring.
    
    Features:
    - Dual order placement (Order A + Order B)
    - Intelligent TP management with Pine data
    - SL Hunting with 70% recovery
    - Exit signal intelligence
    - Smart lot sizing
    """
    
    def __init__(self, service_api, config: Dict[str, Any] = None):
        """
        Initialize Intelligent Trade Manager.
        
        Args:
            service_api: ServiceAPI for order operations
            config: Configuration dict
        """
        self.service_api = service_api
        self.config = config or {}
        self.logger = logging.getLogger("IntelligentTradeManager")
        
        # Active trade contexts
        self._trade_contexts: Dict[str, TradeContext] = {}
        
        # SL Hunt monitors
        self._sl_hunt_monitors: Dict[str, Dict] = {}
        
        # Configuration
        self.risk_percent = self.config.get("risk_percent", 1.0)
        self.max_lot_size = self.config.get("max_lot_size", 0.15)
        self.min_lot_size = self.config.get("min_lot_size", 0.01)
        self.recovery_percent = self.config.get("recovery_percent", 70)  # 70% recovery
        
        # TP management thresholds
        self.tp1_partial_close_percent = 50  # Close 50% at TP1 if conditions weak
        self.tp2_partial_close_percent = 40  # Close 40% at TP2
        
        # ADX/Confidence thresholds for decisions
        self.adx_strong_threshold = 25
        self.confidence_strong_threshold = 70
        
        self.logger.info("IntelligentTradeManager initialized")
    
    # ==================== SMART LOT SIZING ====================
    
    def calculate_smart_lot(
        self,
        entry_price: float,
        sl_price: float,
        symbol: str = "EURUSD",
        account_balance: float = 10000.0,
        risk_percent: float = None
    ) -> SmartLotResult:
        """
        Calculate risk-based lot size.
        
        Formula: lot_size = risk_amount / (sl_pips * pip_value)
        
        Args:
            entry_price: Entry price
            sl_price: Stop loss price
            symbol: Trading symbol
            account_balance: Account balance
            risk_percent: Risk percentage (default from config)
            
        Returns:
            SmartLotResult with calculated lot size
        """
        risk_pct = risk_percent or self.risk_percent
        risk_amount = account_balance * (risk_pct / 100)
        
        # Calculate SL distance in pips
        pip_value = self._get_pip_value(symbol)
        sl_pips = abs(entry_price - sl_price) / pip_value
        
        if sl_pips <= 0:
            sl_pips = 10  # Default 10 pips if calculation fails
        
        # Calculate lot size
        pip_dollar_value = self._get_pip_dollar_value(symbol)
        lot_size = risk_amount / (sl_pips * pip_dollar_value)
        
        # Apply limits
        capped = False
        cap_reason = ""
        
        if lot_size > self.max_lot_size:
            lot_size = self.max_lot_size
            capped = True
            cap_reason = f"Capped at max lot {self.max_lot_size}"
        elif lot_size < self.min_lot_size:
            lot_size = self.min_lot_size
            capped = True
            cap_reason = f"Raised to min lot {self.min_lot_size}"
        
        # Round to 2 decimal places
        lot_size = round(lot_size, 2)
        
        self.logger.info(
            f"Smart Lot: {lot_size} | Risk: ${risk_amount:.2f} ({risk_pct}%) | "
            f"SL: {sl_pips:.1f} pips | {cap_reason if capped else 'No cap'}"
        )
        
        return SmartLotResult(
            lot_size=lot_size,
            risk_amount=risk_amount,
            sl_pips=sl_pips,
            risk_percent=risk_pct,
            capped=capped,
            cap_reason=cap_reason
        )
    
    def _get_pip_value(self, symbol: str) -> float:
        """Get pip value for symbol"""
        # JPY pairs have different pip value
        if "JPY" in symbol.upper():
            return 0.01
        return 0.0001
    
    def _get_pip_dollar_value(self, symbol: str) -> float:
        """Get dollar value per pip per lot"""
        # Standard lot pip value (approximate)
        if "JPY" in symbol.upper():
            return 10.0  # $10 per pip per lot for JPY pairs
        return 10.0  # $10 per pip per lot for most pairs
    
    # ==================== INTELLIGENT ENTRY ====================
    
    async def process_entry_signal(
        self,
        alert: Dict[str, Any],
        account_balance: float = 10000.0
    ) -> Dict[str, Any]:
        """
        Process entry signal with intelligent dual order placement.
        
        Places:
        - Order A: Main position targeting TP3
        - Order B: Quick profit at TP1 (50% of Order A lot)
        
        Args:
            alert: Alert data with TP1, TP2, TP3, SL from Pine
            account_balance: Account balance for lot calculation
            
        Returns:
            dict: Execution result with order IDs
        """
        try:
            # Extract Pine data
            symbol = alert.get("ticker", alert.get("symbol", "EURUSD"))
            direction = alert.get("direction", "BUY")
            entry_price = alert.get("price", 0)
            sl_price = alert.get("sl", 0)
            tp1_price = alert.get("tp1", 0)
            tp2_price = alert.get("tp2", 0)
            tp3_price = alert.get("tp3", 0)
            
            # Validate required fields
            if not all([entry_price, sl_price, tp1_price]):
                return {"status": "error", "message": "Missing required price data"}
            
            # Calculate smart lot size
            lot_result = self.calculate_smart_lot(
                entry_price=entry_price,
                sl_price=sl_price,
                symbol=symbol,
                account_balance=account_balance
            )
            
            base_lot = lot_result.lot_size
            
            # Order A: Full lot, targets TP3
            order_a_lot = base_lot
            
            # Order B: 50% of Order A, targets TP1
            order_b_lot = round(base_lot * 0.5, 2)
            if order_b_lot < self.min_lot_size:
                order_b_lot = self.min_lot_size
            
            # Create trade context
            trade_id = f"{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            context = TradeContext(
                trade_id=trade_id,
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                sl_price=sl_price,
                tp1_price=tp1_price,
                tp2_price=tp2_price or tp1_price * 1.5,  # Default TP2 if not provided
                tp3_price=tp3_price or tp1_price * 2.0,  # Default TP3 if not provided
                order_a_lot=order_a_lot,
                order_b_lot=order_b_lot,
                state=TradeState.ACTIVE
            )
            
            # Place Order A (Main - targets TP3)
            order_a_result = await self._place_order_a(context)
            if order_a_result.get("success"):
                context.order_a_id = order_a_result.get("order_id")
                context.order_a_state = TradeState.ACTIVE
            
            # Place Order B (Quick profit - targets TP1)
            order_b_result = await self._place_order_b(context)
            if order_b_result.get("success"):
                context.order_b_id = order_b_result.get("order_id")
                context.order_b_state = TradeState.ACTIVE
            
            # Store context
            self._trade_contexts[trade_id] = context
            
            self.logger.info(
                f"Entry Processed: {symbol} {direction}\n"
                f"  Order A: {order_a_lot} lots, TP={tp3_price}, SL={sl_price}\n"
                f"  Order B: {order_b_lot} lots, TP={tp1_price}, SL={sl_price}"
            )
            
            return {
                "status": "success",
                "trade_id": trade_id,
                "order_a_id": context.order_a_id,
                "order_b_id": context.order_b_id,
                "order_a_lot": order_a_lot,
                "order_b_lot": order_b_lot,
                "entry_price": entry_price,
                "sl_price": sl_price,
                "tp1_price": tp1_price,
                "tp2_price": context.tp2_price,
                "tp3_price": context.tp3_price
            }
            
        except Exception as e:
            self.logger.error(f"Entry processing error: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    async def _place_order_a(self, context: TradeContext) -> Dict[str, Any]:
        """Place Order A (Main position targeting TP3)"""
        try:
            if self.service_api:
                result = await self.service_api.place_order_async(
                    symbol=context.symbol,
                    direction=context.direction,
                    lot_size=context.order_a_lot,
                    entry_price=context.entry_price,
                    sl_price=context.sl_price,
                    tp_price=context.tp3_price,
                    comment=f"OrderA_{context.trade_id}",
                    metadata={
                        "order_type": "ORDER_A",
                        "trade_id": context.trade_id,
                        "target": "TP3"
                    }
                )
                return {"success": result.get("success", False), "order_id": result.get("trade_id")}
            else:
                # Simulation mode
                order_id = f"A_{context.trade_id}"
                self.logger.info(f"[SIM] Order A placed: {order_id}")
                return {"success": True, "order_id": order_id}
        except Exception as e:
            self.logger.error(f"Order A placement error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _place_order_b(self, context: TradeContext) -> Dict[str, Any]:
        """Place Order B (Quick profit at TP1)"""
        try:
            if self.service_api:
                result = await self.service_api.place_order_async(
                    symbol=context.symbol,
                    direction=context.direction,
                    lot_size=context.order_b_lot,
                    entry_price=context.entry_price,
                    sl_price=context.sl_price,
                    tp_price=context.tp1_price,
                    comment=f"OrderB_{context.trade_id}",
                    metadata={
                        "order_type": "ORDER_B",
                        "trade_id": context.trade_id,
                        "target": "TP1"
                    }
                )
                return {"success": result.get("success", False), "order_id": result.get("trade_id")}
            else:
                # Simulation mode
                order_id = f"B_{context.trade_id}"
                self.logger.info(f"[SIM] Order B placed: {order_id}")
                return {"success": True, "order_id": order_id}
        except Exception as e:
            self.logger.error(f"Order B placement error: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== TP MANAGEMENT ====================
    
    async def monitor_tp_levels(
        self,
        trade_id: str,
        current_price: float,
        pine_update: PineUpdate
    ) -> Dict[str, Any]:
        """
        Monitor TP levels with intelligent decision making.
        
        IMPORTANT: Check from highest TP to lowest to handle price jumps correctly.
        
        TP3 Hit Logic:
        - Close all remaining
        
        TP2 Hit Logic:
        - Close 40% of Order A
        - Trail SL to TP1
        
        TP1 Hit Logic:
        - If conditions strong (ADX >= 25, Confidence >= 70, Trend aligned) → Hold for TP2
        - If conditions weak → Close 50% of Order A
        
        Args:
            trade_id: Trade identifier
            current_price: Current market price
            pine_update: Latest Pine Script data
            
        Returns:
            dict: Action taken
        """
        context = self._trade_contexts.get(trade_id)
        if not context:
            return {"action": "none", "reason": "trade_not_found"}
        
        direction = context.direction.upper()
        
        # Check TP3 FIRST (highest level)
        if self._is_tp_hit(current_price, context.tp3_price, direction):
            self.logger.info(f"[{trade_id}] TP3 hit, closing all remaining")
            await self._close_all(context)
            context.state = TradeState.TP3_HIT
            return {"action": "close_all", "reason": "tp3_hit"}
        
        # Check TP2 (middle level)
        if self._is_tp_hit(current_price, context.tp2_price, direction):
            if context.order_a_state == TradeState.ACTIVE or context.state == TradeState.TP1_HIT:
                self.logger.info(f"[{trade_id}] TP2 hit, closing 40%, trailing SL to TP1")
                
                # Close 40%
                await self._close_partial(context, percent=self.tp2_partial_close_percent)
                
                # Trail SL to TP1
                await self._trail_sl_to_tp1(context)
                
                context.state = TradeState.TP2_HIT
                return {"action": "partial_close_and_trail", "percent": 40, "new_sl": context.tp1_price}
        
        # Check TP1 LAST (lowest level)
        if self._is_tp_hit(current_price, context.tp1_price, direction):
            if context.order_a_state == TradeState.ACTIVE and context.state != TradeState.TP1_HIT:
                # Order B should have closed at TP1
                context.order_b_state = TradeState.TP1_HIT
                
                # Intelligent decision for Order A
                if self._should_hold_for_tp2(pine_update, direction):
                    self.logger.info(f"[{trade_id}] TP1 hit, conditions strong, holding for TP2")
                    context.state = TradeState.TP1_HIT
                    return {"action": "hold", "reason": "conditions_strong", "target": "TP2"}
                else:
                    # Close 50% of Order A
                    self.logger.info(f"[{trade_id}] TP1 hit, conditions weak, closing 50%")
                    await self._close_partial(context, percent=self.tp1_partial_close_percent)
                    context.state = TradeState.TP1_HIT
                    return {"action": "partial_close", "percent": 50, "reason": "conditions_weak"}
        
        return {"action": "none", "reason": "no_tp_hit"}
    
    def _is_tp_hit(self, current_price: float, tp_price: float, direction: str) -> bool:
        """Check if TP level is hit"""
        if direction == "BUY":
            return current_price >= tp_price
        else:
            return current_price <= tp_price
    
    def _should_hold_for_tp2(self, pine_update: PineUpdate, direction: str) -> bool:
        """
        Determine if conditions are favorable to hold for TP2.
        
        Conditions:
        - ADX >= 25 (strong momentum)
        - Confidence >= 70 (high confidence)
        - Trend aligned with direction
        """
        if not pine_update:
            return False
        
        return (
            pine_update.is_strong() and
            pine_update.is_aligned(direction)
        )
    
    async def _close_partial(self, context: TradeContext, percent: int) -> Dict[str, Any]:
        """Close partial position"""
        try:
            close_lot = round(context.order_a_lot * (percent / 100), 2)
            
            if self.service_api and context.order_a_id:
                result = await self.service_api.close_partial_position(
                    order_id=context.order_a_id,
                    percent=percent
                )
                context.partial_closes.append({
                    "percent": percent,
                    "lot": close_lot,
                    "timestamp": datetime.now()
                })
                return result
            else:
                # Simulation mode
                context.partial_closes.append({
                    "percent": percent,
                    "lot": close_lot,
                    "timestamp": datetime.now()
                })
                self.logger.info(f"[SIM] Partial close: {percent}% ({close_lot} lots)")
                return {"success": True, "closed_lot": close_lot}
        except Exception as e:
            self.logger.error(f"Partial close error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _trail_sl_to_tp1(self, context: TradeContext) -> Dict[str, Any]:
        """Trail SL to TP1 level"""
        try:
            if self.service_api and context.order_a_id:
                result = await self.service_api.modify_sl(
                    order_id=context.order_a_id,
                    new_sl=context.tp1_price
                )
                self.logger.info(f"SL trailed to TP1: {context.tp1_price}")
                return result
            else:
                # Simulation mode
                self.logger.info(f"[SIM] SL trailed to TP1: {context.tp1_price}")
                return {"success": True, "new_sl": context.tp1_price}
        except Exception as e:
            self.logger.error(f"Trail SL error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _close_all(self, context: TradeContext) -> Dict[str, Any]:
        """Close all remaining positions"""
        try:
            results = []
            
            if context.order_a_id and context.order_a_state == TradeState.ACTIVE:
                if self.service_api:
                    result = await self.service_api.close_position(context.order_a_id)
                    results.append(result)
                context.order_a_state = TradeState.CLOSED
            
            if context.order_b_id and context.order_b_state == TradeState.ACTIVE:
                if self.service_api:
                    result = await self.service_api.close_position(context.order_b_id)
                    results.append(result)
                context.order_b_state = TradeState.CLOSED
            
            context.state = TradeState.CLOSED
            self.logger.info(f"[{context.trade_id}] All positions closed")
            return {"success": True, "results": results}
        except Exception as e:
            self.logger.error(f"Close all error: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== SL HUNTING & RE-ENTRY ====================
    
    async def handle_sl_hit(
        self,
        trade_id: str,
        order_type: OrderType,
        exit_price: float
    ) -> Dict[str, Any]:
        """
        Handle SL hit and activate SL Hunting.
        
        Calculates 70% recovery level and starts monitoring.
        
        Args:
            trade_id: Trade identifier
            order_type: ORDER_A or ORDER_B
            exit_price: Price at which SL was hit
            
        Returns:
            dict: SL hunting activation result
        """
        context = self._trade_contexts.get(trade_id)
        if not context:
            return {"action": "none", "reason": "trade_not_found"}
        
        # Calculate 70% recovery price
        recovery_price = self._calculate_recovery_price(
            entry=context.entry_price,
            sl=context.sl_price,
            direction=context.direction
        )
        
        # Update context
        context.sl_hunt_active = True
        context.recovery_price = recovery_price
        
        if order_type == OrderType.ORDER_A:
            context.order_a_state = TradeState.SL_HUNTING
        else:
            context.order_b_state = TradeState.SL_HUNTING
        
        # Store hunt data
        hunt_id = f"{trade_id}_{order_type.value}"
        self._sl_hunt_monitors[hunt_id] = {
            "trade_id": trade_id,
            "order_type": order_type,
            "recovery_price": recovery_price,
            "exit_price": exit_price,
            "original_lot": context.order_a_lot if order_type == OrderType.ORDER_A else context.order_b_lot,
            "original_tp": context.tp3_price if order_type == OrderType.ORDER_A else context.tp1_price,
            "activated_at": datetime.now()
        }
        
        self.logger.info(
            f"[{trade_id}] SL Hunting activated for {order_type.value}\n"
            f"  Entry: {context.entry_price}, SL: {context.sl_price}\n"
            f"  Recovery Price (70%): {recovery_price}"
        )
        
        return {
            "action": "sl_hunting_activated",
            "hunt_id": hunt_id,
            "recovery_price": recovery_price,
            "order_type": order_type.value
        }
    
    def _calculate_recovery_price(
        self,
        entry: float,
        sl: float,
        direction: str
    ) -> float:
        """
        Calculate 70% recovery price.
        
        Formula: recovery_price = sl + (entry - sl) * 0.70
        
        For BUY: recovery is above SL
        For SELL: recovery is below SL
        """
        distance = abs(entry - sl)
        recovery_distance = distance * (self.recovery_percent / 100)
        
        if direction.upper() == "BUY":
            # For BUY, SL is below entry, recovery is above SL
            return sl + recovery_distance
        else:
            # For SELL, SL is above entry, recovery is below SL
            return sl - recovery_distance
    
    async def check_sl_recovery(
        self,
        hunt_id: str,
        current_price: float,
        pine_update: PineUpdate
    ) -> Dict[str, Any]:
        """
        Check if price has recovered to 70% level and conditions are favorable.
        
        Re-entry conditions:
        - Price recovered to 70% level
        - Trend still aligned
        - ADX still strong
        - Confidence still acceptable
        
        Args:
            hunt_id: SL hunt identifier
            current_price: Current market price
            pine_update: Latest Pine Script data
            
        Returns:
            dict: Re-entry decision
        """
        hunt_data = self._sl_hunt_monitors.get(hunt_id)
        if not hunt_data:
            return {"action": "none", "reason": "hunt_not_found"}
        
        trade_id = hunt_data["trade_id"]
        context = self._trade_contexts.get(trade_id)
        if not context:
            return {"action": "none", "reason": "trade_not_found"}
        
        direction = context.direction.upper()
        recovery_price = hunt_data["recovery_price"]
        
        # Check if price recovered
        if self._is_price_recovered(current_price, recovery_price, direction):
            # Check Pine conditions
            if self._should_reenter(pine_update, direction):
                self.logger.info(
                    f"[{trade_id}] 70% recovery + conditions met, executing re-entry"
                )
                
                # Execute re-entry
                result = await self._execute_reentry(hunt_data, context)
                
                # Clean up hunt monitor
                del self._sl_hunt_monitors[hunt_id]
                
                return {
                    "action": "reentry_executed",
                    "result": result
                }
            else:
                self.logger.info(
                    f"[{trade_id}] 70% recovery but conditions weak, skipping re-entry"
                )
                return {
                    "action": "reentry_skipped",
                    "reason": "conditions_weak",
                    "pine_data": {
                        "trend": pine_update.trend if pine_update else "N/A",
                        "adx": pine_update.adx if pine_update else 0,
                        "confidence": pine_update.confidence if pine_update else 0
                    }
                }
        
        return {"action": "monitoring", "recovery_price": recovery_price, "current_price": current_price}
    
    def _is_price_recovered(self, current_price: float, recovery_price: float, direction: str) -> bool:
        """Check if price has recovered to 70% level"""
        if direction == "BUY":
            return current_price >= recovery_price
        else:
            return current_price <= recovery_price
    
    def _should_reenter(self, pine_update: PineUpdate, direction: str) -> bool:
        """Check if conditions are favorable for re-entry"""
        if not pine_update:
            return False
        
        return (
            pine_update.adx >= self.adx_strong_threshold and
            pine_update.confidence >= self.confidence_strong_threshold and
            pine_update.is_aligned(direction)
        )
    
    async def _execute_reentry(
        self,
        hunt_data: Dict,
        context: TradeContext
    ) -> Dict[str, Any]:
        """Execute re-entry order"""
        try:
            order_type = hunt_data["order_type"]
            lot_size = hunt_data["original_lot"]
            tp_price = hunt_data["original_tp"]
            
            if self.service_api:
                result = await self.service_api.place_order_async(
                    symbol=context.symbol,
                    direction=context.direction,
                    lot_size=lot_size,
                    entry_price=context.recovery_price,
                    sl_price=context.sl_price,
                    tp_price=tp_price,
                    comment=f"Reentry_{order_type.value}_{context.trade_id}",
                    metadata={
                        "order_type": f"REENTRY_{order_type.value}",
                        "trade_id": context.trade_id,
                        "original_hunt_id": f"{context.trade_id}_{order_type.value}"
                    }
                )
                
                # Update context
                if order_type == OrderType.ORDER_A:
                    context.order_a_state = TradeState.RECOVERY_ACTIVE
                    context.order_a_id = result.get("trade_id")
                else:
                    context.order_b_state = TradeState.RECOVERY_ACTIVE
                    context.order_b_id = result.get("trade_id")
                
                context.sl_hunt_active = False
                
                return {"success": True, "order_id": result.get("trade_id")}
            else:
                # Simulation mode
                order_id = f"RE_{order_type.value}_{context.trade_id}"
                self.logger.info(f"[SIM] Re-entry placed: {order_id}")
                
                if order_type == OrderType.ORDER_A:
                    context.order_a_state = TradeState.RECOVERY_ACTIVE
                    context.order_a_id = order_id
                else:
                    context.order_b_state = TradeState.RECOVERY_ACTIVE
                    context.order_b_id = order_id
                
                context.sl_hunt_active = False
                
                return {"success": True, "order_id": order_id}
                
        except Exception as e:
            self.logger.error(f"Re-entry execution error: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== EXIT SIGNAL INTELLIGENCE ====================
    
    async def process_exit_signal(
        self,
        trade_id: str,
        current_price: float,
        pine_update: PineUpdate
    ) -> Dict[str, Any]:
        """
        Process exit signal with intelligent decision making.
        
        Decision logic:
        - Big profit (>50 pips) + strong trend → Hold position
        - Small profit (<10 pips) + weak trend → Close immediately
        - Medium profit + deteriorating conditions → Close 50%, trail SL
        
        Args:
            trade_id: Trade identifier
            current_price: Current market price
            pine_update: Latest Pine Script data
            
        Returns:
            dict: Exit decision and action taken
        """
        context = self._trade_contexts.get(trade_id)
        if not context:
            return {"action": "none", "reason": "trade_not_found"}
        
        # Calculate current profit in pips
        profit_pips = self._calculate_profit_pips(
            entry=context.entry_price,
            current=current_price,
            direction=context.direction
        )
        
        direction = context.direction.upper()
        
        # Decision logic
        if profit_pips > 50 and pine_update and pine_update.is_strong() and pine_update.is_aligned(direction):
            # Big profit + strong trend → Hold
            self.logger.info(
                f"[{trade_id}] Exit signal but strong trend ({profit_pips:.1f} pips profit), holding"
            )
            return {
                "action": "hold",
                "reason": "strong_trend_big_profit",
                "profit_pips": profit_pips,
                "pine_data": {
                    "trend": pine_update.trend,
                    "adx": pine_update.adx,
                    "confidence": pine_update.confidence
                }
            }
        
        elif profit_pips < 10:
            # Small profit → Close immediately
            self.logger.info(
                f"[{trade_id}] Exit signal + small profit ({profit_pips:.1f} pips), closing immediately"
            )
            await self._close_all(context)
            return {
                "action": "close_all",
                "reason": "small_profit",
                "profit_pips": profit_pips
            }
        
        else:
            # Medium profit → Close 50%, protect rest
            self.logger.info(
                f"[{trade_id}] Exit signal + moderate profit ({profit_pips:.1f} pips), closing 50%"
            )
            await self._close_partial(context, percent=50)
            
            # Trail SL to breakeven
            await self._trail_sl_to_breakeven(context)
            
            return {
                "action": "partial_close_and_protect",
                "percent": 50,
                "reason": "moderate_profit",
                "profit_pips": profit_pips
            }
    
    def _calculate_profit_pips(self, entry: float, current: float, direction: str) -> float:
        """Calculate profit in pips"""
        pip_value = 0.0001 if entry < 100 else 0.01  # Forex vs JPY/indices
        
        if direction.upper() == "BUY":
            return (current - entry) / pip_value
        else:
            return (entry - current) / pip_value
    
    async def _trail_sl_to_breakeven(self, context: TradeContext) -> Dict[str, Any]:
        """Trail SL to breakeven (entry + small buffer)"""
        try:
            # Add 5 pips buffer
            pip_value = 0.0001 if context.entry_price < 100 else 0.01
            buffer = 5 * pip_value
            
            if context.direction.upper() == "BUY":
                breakeven_sl = context.entry_price + buffer
            else:
                breakeven_sl = context.entry_price - buffer
            
            if self.service_api and context.order_a_id:
                result = await self.service_api.modify_sl(
                    order_id=context.order_a_id,
                    new_sl=breakeven_sl
                )
                self.logger.info(f"SL trailed to breakeven: {breakeven_sl}")
                return result
            else:
                self.logger.info(f"[SIM] SL trailed to breakeven: {breakeven_sl}")
                return {"success": True, "new_sl": breakeven_sl}
        except Exception as e:
            self.logger.error(f"Trail SL to breakeven error: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== UTILITY METHODS ====================
    
    def get_trade_context(self, trade_id: str) -> Optional[TradeContext]:
        """Get trade context by ID"""
        return self._trade_contexts.get(trade_id)
    
    def get_all_active_trades(self) -> List[TradeContext]:
        """Get all active trade contexts"""
        return [
            ctx for ctx in self._trade_contexts.values()
            if ctx.state not in [TradeState.CLOSED, TradeState.TP3_HIT]
        ]
    
    def get_active_sl_hunts(self) -> Dict[str, Dict]:
        """Get all active SL hunt monitors"""
        return self._sl_hunt_monitors.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        active_trades = len([
            ctx for ctx in self._trade_contexts.values()
            if ctx.state not in [TradeState.CLOSED, TradeState.TP3_HIT]
        ])
        
        return {
            "total_trades": len(self._trade_contexts),
            "active_trades": active_trades,
            "active_sl_hunts": len(self._sl_hunt_monitors),
            "config": {
                "risk_percent": self.risk_percent,
                "max_lot": self.max_lot_size,
                "min_lot": self.min_lot_size,
                "recovery_percent": self.recovery_percent
            }
        }
