"""
Combined V3 Logic Plugin - Main Entry Point

This plugin implements the V3 Combined Logic system with:
- 12 signal types (7 entry, 2 exit, 2 info, 1 bonus)
- 2-tier routing matrix (signal override + timeframe routing)
- Dual order system (Order A: Smart SL, Order B: Fixed $10 SL)
- MTF 4-pillar trend validation
- Shadow mode support

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, Optional, List
import logging
import json
import os

from src.core.plugin_system.base_plugin import BaseLogicPlugin
from src.core.plugin_system.plugin_interface import ISignalProcessor, IOrderExecutor
from src.core.plugin_system.reentry_interface import IReentryCapable, ReentryEvent, ReentryType
from src.core.plugin_system.dual_order_interface import (
    IDualOrderCapable, OrderConfig, DualOrderResult, OrderType, SLType
)
from src.core.plugin_system.profit_booking_interface import (
    IProfitBookingCapable, ProfitChain, BookingResult, ChainStatus, PYRAMID_LEVELS
)
from src.core.plugin_system.autonomous_interface import (
    IAutonomousCapable, SafetyCheckResult, ReverseShieldStatus
)
from src.core.plugin_system.database_interface import (
    IDatabaseCapable, DatabaseConfig
)
from src.core.services.reentry_service import ReentryService
from src.core.services.dual_order_service import DualOrderService
from src.core.services.profit_booking_service import ProfitBookingService
from src.core.services.autonomous_service import AutonomousService
from .signal_handlers import V3SignalHandlers
from .order_manager import V3OrderManager
from .trend_validator import V3TrendValidator

logger = logging.getLogger(__name__)


class V3CombinedPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor, IReentryCapable, IDualOrderCapable, IProfitBookingCapable, IAutonomousCapable, IDatabaseCapable):
    """
    V3 Combined Logic Plugin - Handles all 12 V3 signal types.
    
    This plugin migrates the V3 logic from trading_engine.py into a
    plugin-based architecture while maintaining 100% backward compatibility.
    
    Implements ISignalProcessor and IOrderExecutor interfaces for
    TradingEngine delegation system.
    
    Signal Types:
    - Entry (7): Institutional_Launchpad, Liquidity_Trap, Momentum_Breakout,
                 Mitigation_Test, Golden_Pocket_Flip, Screener_Full_Bullish/Bearish
    - Exit (2): Bullish_Exit, Bearish_Exit
    - Info (2): Volatility_Squeeze, Trend_Pulse
    - Bonus (1): Sideways_Breakout
    """
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        """
        Initialize the Combined V3 Plugin.
        
        Args:
            plugin_id: Unique identifier for this plugin
            config: Plugin-specific configuration
            service_api: Access to shared services (ServiceAPI)
        """
        super().__init__(plugin_id, config, service_api)
        
        self._load_plugin_config()
        
        self.signal_handlers = V3SignalHandlers(self)
        self.order_manager = V3OrderManager(self, service_api)
        self.trend_validator = V3TrendValidator(self)
        
        self.shadow_mode = self.plugin_config.get("shadow_mode", False)
        
        # Signal type definitions
        self.entry_signals = [
            'Institutional_Launchpad', 'Liquidity_Trap', 'Momentum_Breakout',
            'Mitigation_Test', 'Golden_Pocket_Flip', 'Screener_Full_Bullish', 'Screener_Full_Bearish'
        ]
        self.exit_signals = ['Bullish_Exit', 'Bearish_Exit']
        self.info_signals = ['Volatility_Squeeze', 'Trend_Pulse']
        
        # Re-entry system support (Plan 03)
        self._chain_levels: Dict[str, int] = {}  # trade_id -> chain_level
        self._reentry_service: Optional[ReentryService] = None
        
        # Dual order system support (Plan 04)
        self._dual_order_service: Optional[DualOrderService] = None
        self._active_orders: Dict[str, Dict[str, Any]] = {}  # order_id -> order_info
        
        # Profit booking system support (Plan 05)
        self._profit_booking_service: Optional[ProfitBookingService] = None
        self._order_to_chain: Dict[str, str] = {}  # order_b_id -> chain_id
        
        # Autonomous system support (Plan 06)
        self._autonomous_service: Optional[AutonomousService] = None
        self._active_shields: Dict[str, ReverseShieldStatus] = {}  # trade_id -> shield_status
        
        self.logger.info(
            f"V3CombinedPlugin initialized | "
            f"Shadow Mode: {self.shadow_mode} | "
            f"12 signals ready | Re-entry enabled | Dual orders enabled | Profit booking enabled"
        )
    
    def set_reentry_service(self, service: ReentryService):
        """
        Inject re-entry service for recovery operations.
        
        Args:
            service: ReentryService instance
        """
        self._reentry_service = service
        # Register callback for recovery events
        service.register_recovery_callback(self.plugin_id, self._on_recovery_callback)
        self.logger.info(f"ReentryService injected into {self.plugin_id}")
    
    async def _on_recovery_callback(self, event: ReentryEvent):
        """Callback when recovery is detected by ReentryService"""
        self.logger.info(f"Recovery callback received for {event.trade_id}")
        await self.on_recovery_signal(event)
    
    def set_dual_order_service(self, service: DualOrderService):
        """
        Inject dual order service for order operations.
        
        Args:
            service: DualOrderService instance
        """
        self._dual_order_service = service
        self.logger.info(f"DualOrderService injected into {self.plugin_id}")
    
    def set_profit_booking_service(self, service: ProfitBookingService):
        """
        Inject profit booking service for chain operations.
        
        Args:
            service: ProfitBookingService instance
        """
        self._profit_booking_service = service
        self.logger.info(f"ProfitBookingService injected into {self.plugin_id}")
    
    def set_autonomous_service(self, service: AutonomousService):
        """
        Inject autonomous service for safety operations.
        
        Args:
            service: AutonomousService instance
        """
        self._autonomous_service = service
        self.logger.info(f"AutonomousService injected into {self.plugin_id}")
    
    # ==================== Plan 08: ServiceAPI Integration ====================
    
    def set_service_api(self, service_api) -> None:
        """
        Inject ServiceAPI - the UNIFIED way to access all core services.
        
        This method replaces individual service setters by providing
        access to all services through a single ServiceAPI instance.
        Plugins should use ServiceAPI for ALL operations.
        
        Args:
            service_api: ServiceAPI instance with all services registered
        """
        self._service_api = service_api
        
        # Also set individual services for backward compatibility
        if service_api.reentry_service:
            self._reentry_service = service_api.reentry_service
            if hasattr(service_api.reentry_service, 'register_recovery_callback'):
                service_api.reentry_service.register_recovery_callback(
                    self.plugin_id, self._on_recovery_callback
                )
        
        if service_api.dual_order_service:
            self._dual_order_service = service_api.dual_order_service
        
        if service_api.profit_booking_service:
            self._profit_booking_service = service_api.profit_booking_service
        
        if service_api.autonomous_service:
            self._autonomous_service = service_api.autonomous_service
        
        self.logger.info(f"ServiceAPI injected into {self.plugin_id} (Plan 08)")
    
    async def process_signal_via_service_api(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process signal using ServiceAPI exclusively (Plan 08).
        
        This method demonstrates the recommended way to process signals
        using ServiceAPI for all operations.
        
        Args:
            signal: Trading signal dictionary
            
        Returns:
            Result dictionary or None if processing failed
        """
        if not hasattr(self, '_service_api') or not self._service_api:
            self.logger.error("ServiceAPI not initialized")
            return None
        
        # Check safety via ServiceAPI
        safety_check = await self._service_api.check_safety(self.plugin_id)
        if safety_check and hasattr(safety_check, 'allowed') and not safety_check.allowed:
            self.logger.info(f"Signal blocked by safety check: {getattr(safety_check, 'reason', 'Unknown')}")
            return None
        
        # Create dual orders via ServiceAPI
        order_a_config = await self.get_order_a_config(signal)
        order_b_config = await self.get_order_b_config(signal)
        
        result = await self._service_api.create_dual_orders(
            signal, order_a_config, order_b_config
        )
        
        if result and hasattr(result, 'error') and result.error:
            self.logger.error(f"Order creation failed: {result.error}")
            return None
        
        # Create profit chain via ServiceAPI
        if result and hasattr(result, 'order_b_id') and result.order_b_id:
            await self._service_api.create_profit_chain(
                self.plugin_id,
                result.order_b_id,
                signal.get('symbol', ''),
                signal.get('signal_type', '')
            )
        
        # Send notification via ServiceAPI
        await self._service_api.send_telegram_notification(
            'trade_opened',
            f"Trade opened: {signal.get('symbol', '')} {signal.get('signal_type', '')}",
            order_a_id=getattr(result, 'order_a_id', None) if result else None,
            order_b_id=getattr(result, 'order_b_id', None) if result else None
        )
        
        return {
            'status': 'executed',
            'order_a_id': getattr(result, 'order_a_id', None) if result else None,
            'order_b_id': getattr(result, 'order_b_id', None) if result else None
        }
    
    async def on_sl_hit_via_service_api(self, event: ReentryEvent) -> bool:
        """
        Handle SL hit via ServiceAPI (Plan 08).
        
        Args:
            event: ReentryEvent with trade details
            
        Returns:
            True if recovery started successfully
        """
        if not hasattr(self, '_service_api') or not self._service_api:
            return False
        
        # Check safety via ServiceAPI
        safety_check = await self._service_api.check_safety(self.plugin_id)
        if safety_check and hasattr(safety_check, 'allowed') and not safety_check.allowed:
            return False
        
        # Start recovery via ServiceAPI
        return await self._service_api.start_recovery(event)
    
    # ==================== IDualOrderCapable Implementation (Plan 04) ====================
    
    async def create_dual_orders(self, signal: Dict[str, Any]) -> DualOrderResult:
        """
        Create both Order A and Order B for a signal.
        
        Order A: TP_TRAIL with V3 Smart SL (progressive trailing)
        Order B: PROFIT_TRAIL with fixed $10 risk SL
        
        Args:
            signal: Trading signal with symbol, direction, etc.
            
        Returns:
            DualOrderResult with both order IDs and status
        """
        if not self._dual_order_service:
            self.logger.warning("DualOrderService not available")
            return DualOrderResult(error="Service not available")
        
        # Get configurations for both orders
        order_a_config = await self.get_order_a_config(signal)
        order_b_config = await self.get_order_b_config(signal)
        
        # Create dual orders via service
        result = await self._dual_order_service.create_dual_orders(
            signal, order_a_config, order_b_config
        )
        
        # Track orders locally
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
        
        self.logger.info(f"Dual orders created: A={result.order_a_id}, B={result.order_b_id}")
        
        # Create profit chain for Order B (Plan 05)
        if result.order_b_id and not signal.get('is_profit_chain_order'):
            await self.create_profit_chain(result.order_b_id, signal)
        
        return result
    
    async def get_order_a_config(self, signal: Dict[str, Any], defined_sl: Optional[float] = None) -> OrderConfig:
        """
        Get Order A configuration (TP_TRAIL with V3 Smart SL).
        
        Order A characteristics:
        - Uses V3 Smart SL with progressive trailing
        - Trailing starts at 50% of SL in profit
        - Trails in 25% steps
        - Has TP target (2:1 RR)
        - CRITICAL: Uses Pine Script SL when provided (defined_sl)
        
        Args:
            signal: Trading signal
            defined_sl: Optional SL price from Pine Script alert
            
        Returns:
            OrderConfig for Order A
        """
        logic = signal.get('logic', 'LOGIC1')
        base_lot = self._get_base_lot(logic)
        smart_lot = self.get_smart_lot_size(base_lot)
        
        # USE PINE SL IF PROVIDED, OTHERWISE CALCULATE
        if defined_sl:
            sl_price = defined_sl
            # Calculate pips from price difference
            current_price = signal.get('price', 0)
            sl_pips = abs(current_price - sl_price) * 10000  # For forex pairs
            self.logger.info(f"[Order A] Using Pine Script SL: {sl_price} ({sl_pips:.1f} pips)")
        else:
            sl_pips = self._get_sl_pips(signal.get('symbol', 'EURUSD'), logic)
            sl_price = None  # Will be calculated by order service
            self.logger.info(f"[Order A] Using calculated SL: {sl_pips} pips")
        
        tp_pips = sl_pips * 2  # 2:1 RR for Order A
        
        return OrderConfig(
            order_type=OrderType.ORDER_A,
            sl_type=SLType.V3_SMART_SL,
            lot_size=smart_lot,
            sl_pips=sl_pips,
            sl_price=sl_price,  # Pass Pine SL price if available
            tp_pips=tp_pips,
            trailing_enabled=True,
            trailing_start_pips=sl_pips * 0.5,  # Start trailing at 50% of SL
            trailing_step_pips=sl_pips * 0.25,  # Trail in 25% steps
            plugin_id=self.plugin_id,
            metadata={
                'logic': logic,
                'original_sl': sl_pips,
                'pine_sl_used': defined_sl is not None
            }
        )
    
    async def get_order_b_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """
        Get Order B configuration (PROFIT_TRAIL with fixed $10 risk).
        
        Order B characteristics:
        - Uses fixed $10 risk SL
        - No TP target (uses profit booking)
        - Creates profit booking chains
        
        Args:
            signal: Trading signal
            
        Returns:
            OrderConfig for Order B
        """
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
        """
        Handle Order A closure.
        
        If closed by SL, may trigger SL Hunt Recovery.
        If closed by TP, trade is complete.
        
        Args:
            order_id: Order identifier
            reason: Close reason (SL_HIT, TP_HIT, MANUAL, etc.)
        """
        self.logger.info(f"Order A closed: {order_id}, reason: {reason}")
        
        order_info = self._active_orders.pop(order_id, None)
        if not order_info:
            return
        
        # If SL hit, trigger re-entry via IReentryCapable
        if reason == 'SL_HIT':
            signal = order_info.get('signal', {})
            event = ReentryEvent(
                trade_id=order_id,
                plugin_id=self.plugin_id,
                symbol=signal.get('symbol', ''),
                reentry_type=ReentryType.SL_HUNT,
                entry_price=signal.get('price', 0),
                exit_price=0,  # Will be filled by monitor
                sl_price=0,
                direction=signal.get('signal_type', ''),
                chain_level=self.get_chain_level(order_id)
            )
            await self.on_sl_hit(event)
    
    async def on_order_b_closed(self, order_id: str, reason: str) -> None:
        """
        Handle Order B closure - triggers profit booking.
        
        Args:
            order_id: Order identifier
            reason: Close reason (SL_HIT, TP_HIT, PROFIT_TARGET, etc.)
        """
        self.logger.info(f"Order B closed: {order_id}, reason: {reason}")
        
        order_info = self._active_orders.pop(order_id, None)
        if not order_info:
            return
        
        # Get chain for this order
        chain_id = self._order_to_chain.get(order_id)
        if not chain_id:
            self.logger.warning(f"No chain found for Order B: {order_id}")
            return
        
        # Handle based on close reason
        if reason == 'PROFIT_TARGET':
            # Book profit via IProfitBookingCapable
            result = await self.on_profit_target_hit(chain_id, order_id)
            self.logger.info(f"Profit booked: ${result.profit_amount:.2f}")
        elif reason == 'SL_HIT':
            # Start Profit Booking SL Hunt
            await self.on_chain_sl_hit(chain_id)
    
    # ==================== IProfitBookingCapable Implementation (Plan 05) ====================
    
    async def create_profit_chain(
        self,
        order_b_id: str,
        signal: Dict[str, Any]
    ) -> Optional[ProfitChain]:
        """
        Create a new profit booking chain for Order B.
        
        Called when Order B is created. Initializes chain at Level 0
        with 1 order and $7 profit target.
        
        Args:
            order_b_id: Order B identifier
            signal: Original trading signal
            
        Returns:
            ProfitChain if created successfully
        """
        if not self._profit_booking_service:
            self.logger.warning("ProfitBookingService not available")
            return None
        
        chain = await self._profit_booking_service.create_chain(
            plugin_id=self.plugin_id,
            order_b_id=order_b_id,
            symbol=signal.get('symbol', ''),
            direction=signal.get('signal_type', ''),
            metadata={
                'logic': signal.get('logic', 'LOGIC1'),
                'original_signal': signal
            }
        )
        
        if chain:
            self._order_to_chain[order_b_id] = chain.chain_id
            self.logger.info(f"Profit chain created for Order B: {order_b_id} -> {chain.chain_id}")
        
        return chain
    
    async def on_profit_target_hit(
        self,
        chain_id: str,
        order_id: str
    ) -> BookingResult:
        """
        Called when an order hits its $7 profit target.
        
        Books profit and potentially advances chain level.
        
        Args:
            chain_id: Chain identifier
            order_id: Order that hit profit target
            
        Returns:
            BookingResult with profit and level info
        """
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
            self.logger.info(f"Chain {chain_id} advanced to level {result.new_level}")
            # Create new orders for the new level
            await self._create_level_orders(chain_id, result.new_level)
        
        return result
    
    async def on_chain_sl_hit(self, chain_id: str) -> bool:
        """
        Called when chain SL is hit.
        
        Triggers Profit Booking SL Hunt to recover the chain.
        
        Args:
            chain_id: Chain identifier
            
        Returns:
            True if SL Hunt started successfully
        """
        if not self._profit_booking_service:
            return False
        
        success = await self._profit_booking_service.start_sl_hunt(chain_id)
        if success:
            self.logger.info(f"Profit Booking SL Hunt started for chain {chain_id}")
        return success
    
    async def get_active_chains(self) -> List[ProfitChain]:
        """
        Get all active profit chains for this plugin.
        
        Returns:
            List of active ProfitChain objects
        """
        if not self._profit_booking_service:
            return []
        return self._profit_booking_service.get_active_chains(self.plugin_id)
    
    def get_pyramid_config(self) -> Dict[int, int]:
        """
        Get pyramid level configuration.
        
        Returns:
            Dict mapping level (0-4) to number of orders
        """
        return PYRAMID_LEVELS.copy()
    
    # ==================== IAutonomousCapable Implementation (Plan 06) ====================
    
    async def check_recovery_allowed(self) -> SafetyCheckResult:
        """
        Check if recovery is allowed based on all safety limits.
        
        Checks daily limit, concurrent limit, and profit protection
        before allowing any recovery operation.
        
        Returns:
            SafetyCheckResult with allowed=True if all checks pass
        """
        if not self._autonomous_service:
            self.logger.warning("AutonomousService not available for safety check")
            return SafetyCheckResult(
                allowed=False,
                reason="AutonomousService not available",
                daily_count=0,
                daily_limit=0,
                concurrent_count=0,
                concurrent_limit=0,
                current_profit=0,
                profit_threshold=0
            )
        
        return await self._autonomous_service.check_recovery_allowed(self.plugin_id)
    
    async def activate_reverse_shield(
        self,
        trade_id: str,
        symbol: str,
        direction: str
    ) -> ReverseShieldStatus:
        """
        Activate Reverse Shield for a trade during recovery.
        
        Creates hedge position to protect during recovery window.
        Shield A: Recovery hedge with TP at 1:1
        Shield B: Profit booking hedge
        
        Args:
            trade_id: ID of the trade being protected
            symbol: Trading symbol
            direction: Original trade direction
            
        Returns:
            ReverseShieldStatus with shield details
        """
        if not self._autonomous_service:
            self.logger.warning("AutonomousService not available for Reverse Shield")
            return ReverseShieldStatus(
                active=False,
                shield_id=None,
                symbol=symbol,
                direction=direction,
                hedge_order_id=None,
                error="AutonomousService not available"
            )
        
        # Check if Reverse Shield is enabled in config
        rs_enabled = self.plugin_config.get("reverse_shield_enabled", True)
        if not rs_enabled:
            self.logger.info(f"Reverse Shield disabled for {self.plugin_id}")
            return ReverseShieldStatus(
                active=False,
                shield_id=None,
                symbol=symbol,
                direction=direction,
                hedge_order_id=None,
                error="Reverse Shield disabled in config"
            )
        
        # Activate shield via service
        status = await self._autonomous_service.activate_reverse_shield(
            plugin_id=self.plugin_id,
            trade_id=trade_id,
            symbol=symbol,
            direction=direction
        )
        
        if status.active:
            self._active_shields[trade_id] = status
            self.logger.info(f"Reverse Shield activated for {trade_id}: {status.shield_id}")
        
        return status
    
    async def deactivate_reverse_shield(self, trade_id: str) -> bool:
        """
        Deactivate Reverse Shield after recovery completes or fails.
        
        Args:
            trade_id: ID of the trade whose shield should be deactivated
            
        Returns:
            True if shield was successfully deactivated
        """
        if not self._autonomous_service:
            return False
        
        # Get and remove shield from tracking
        status = self._active_shields.pop(trade_id, None)
        if not status or not status.active:
            return False
        
        # Deactivate via service
        success = await self._autonomous_service.deactivate_reverse_shield(
            plugin_id=self.plugin_id,
            trade_id=trade_id
        )
        
        if success:
            self.logger.info(f"Reverse Shield deactivated for {trade_id}")
        
        return success
    
    async def increment_recovery_count(self) -> int:
        """
        Increment daily recovery count.
        
        Called when a recovery operation starts.
        
        Returns:
            New daily recovery count
        """
        if not self._autonomous_service:
            return 0
        
        return await self._autonomous_service.increment_recovery_count(self.plugin_id)
    
    async def get_safety_stats(self) -> Dict[str, Any]:
        """
        Get current safety statistics for this plugin.
        
        Returns:
            Dict with recovery stats, shield stats, etc.
        """
        if not self._autonomous_service:
            return {}
        
        return self._autonomous_service.get_plugin_stats(self.plugin_id)
    
    def should_protect_profit(self, current_profit: float) -> bool:
        """
        Check if current profit should be protected.
        
        Args:
            current_profit: Current session profit in dollars
            
        Returns:
            True if profit should be protected (recovery should be skipped)
        """
        if not self._autonomous_service:
            return False
        
        return self._autonomous_service.should_protect_profit(current_profit)
    
    def get_active_shields(self) -> List[ReverseShieldStatus]:
        """
        Get all active Reverse Shields for this plugin.
        
        Returns:
            List of active ReverseShieldStatus objects
        """
        return list(self._active_shields.values())
    
    # ==================== Plan 07: Notification Methods ====================
    
    async def _send_notification(self, notification_type: str, message: str, **kwargs):
        """
        Send notification through ServiceAPI to 3-bot Telegram system.
        
        Args:
            notification_type: Type of notification (e.g., 'trade_opened', 'sl_hit')
            message: Notification message
            **kwargs: Additional arguments
        """
        if hasattr(self, '_service_api') and self._service_api:
            try:
                await self._service_api.send_notification(notification_type, message, **kwargs)
            except Exception as e:
                self.logger.warning(f"Failed to send notification: {e}")
    
    async def on_trade_opened(self, order_id: str, order_type: str, details: Dict[str, Any]):
        """
        Notify when trade is opened through 3-bot system.
        
        Args:
            order_id: MT5 order ID
            order_type: 'order_a' or 'order_b'
            details: Trade details (symbol, direction, price, etc.)
        """
        notification_type = 'order_a_opened' if order_type == 'order_a' else 'order_b_opened'
        message = f"{order_type.upper()} opened: {details.get('symbol')} {details.get('direction')}"
        await self._send_notification(notification_type, message, order_id=order_id, **details)
    
    async def on_trade_closed(self, order_id: str, reason: str, details: Dict[str, Any]):
        """
        Notify when trade is closed through 3-bot system.
        
        Args:
            order_id: MT5 order ID
            reason: Close reason (SL_HIT, TP_HIT, MANUAL, etc.)
            details: Trade details including profit
        """
        notification_type = 'sl_hit' if reason == 'SL_HIT' else 'tp_hit' if reason == 'TP_HIT' else 'trade_closed'
        message = f"Trade closed ({reason}): {details.get('symbol')} P/L: ${details.get('profit', 0):.2f}"
        await self._send_notification(notification_type, message, order_id=order_id, reason=reason, **details)
    
    async def on_recovery_started(self, trade_id: str, recovery_type: str, details: Dict[str, Any]):
        """
        Notify when recovery starts through 3-bot system.
        
        Args:
            trade_id: Original trade ID
            recovery_type: Type of recovery (sl_hunt, tp_continuation, etc.)
            details: Recovery details
        """
        notification_type = f'{recovery_type}_started'
        message = f"Recovery started: {recovery_type} for {details.get('symbol')}"
        await self._send_notification(notification_type, message, trade_id=trade_id, **details)
    
    async def on_recovery_completed(self, trade_id: str, recovery_type: str, success: bool, details: Dict[str, Any]):
        """
        Notify when recovery completes through 3-bot system.
        
        Args:
            trade_id: Original trade ID
            recovery_type: Type of recovery
            success: Whether recovery was successful
            details: Recovery result details
        """
        notification_type = f'{recovery_type}_success' if success else f'{recovery_type}_failed'
        status = "SUCCESS" if success else "FAILED"
        message = f"Recovery {status}: {recovery_type} for {details.get('symbol')}"
        await self._send_notification(notification_type, message, trade_id=trade_id, success=success, **details)
    
    # ==================== End Plan 07 Notification Methods ====================
    
    async def _create_level_orders(self, chain_id: str, level: int):
        """
        Create orders for a new pyramid level.
        
        Args:
            chain_id: Chain identifier
            level: New pyramid level (1-4)
        """
        if not self._profit_booking_service:
            return
        
        chain = self._profit_booking_service._get_chain_by_id(chain_id)
        if not chain:
            return
        
        num_orders = self.get_pyramid_config().get(level, 0)
        self.logger.info(f"Creating {num_orders} orders for chain {chain_id} level {level}")
        
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
            if self._dual_order_service:
                order_b_config = await self.get_order_b_config(signal)
                # Track order to chain mapping
                # Note: Actual order creation would go through dual order service
                self.logger.debug(f"Would create profit chain order {i+1}/{num_orders} for level {level}")
    
    def get_smart_lot_size(self, base_lot: float) -> float:
        """
        Calculate smart lot based on daily P&L.
        
        Discovery 6: Reduces lot when approaching daily limit:
        - >50% remaining: 100% of base lot
        - 25-50% remaining: 75% of base lot
        - <25% remaining: 50% of base lot
        
        Args:
            base_lot: Base lot size for the logic
            
        Returns:
            Adjusted lot size
        """
        if not self._dual_order_service:
            return base_lot
        return self._dual_order_service._apply_smart_lot(base_lot)
    
    def _get_base_lot(self, logic: str) -> float:
        """
        Get base lot size for logic.
        
        Args:
            logic: Logic route (LOGIC1, LOGIC2, LOGIC3)
            
        Returns:
            Base lot size
        """
        lot_sizes = {
            'LOGIC1': 0.01,  # 5m scalping - smallest
            'LOGIC2': 0.02,  # 15m intraday - medium
            'LOGIC3': 0.03   # 1h swing - largest
        }
        return lot_sizes.get(logic, 0.01)
    
    def _get_sl_pips(self, symbol: str, logic: str) -> float:
        """
        Get SL pips based on symbol and logic.
        
        Args:
            symbol: Trading symbol
            logic: Logic route
            
        Returns:
            SL in pips
        """
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
    
    def _load_plugin_config(self):
        """Load plugin configuration from config.json"""
        config_path = os.path.join(
            os.path.dirname(__file__), "config.json"
        )
        
        try:
            with open(config_path, 'r') as f:
                self.plugin_config = json.load(f)
        except FileNotFoundError:
            self.logger.warning("config.json not found, using defaults")
            self.plugin_config = self.config
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid config.json: {e}")
            self.plugin_config = self.config
        
        if self.config:
            self.plugin_config.update(self.config)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load plugin metadata"""
        return {
            "version": "1.0.0",
            "author": "Zepix Team",
            "description": "V3 Combined Logic - 12 Signals with Dual Orders",
            "supported_signals": [
                "Institutional_Launchpad",
                "Liquidity_Trap",
                "Momentum_Breakout",
                "Mitigation_Test",
                "Golden_Pocket_Flip",
                "Volatility_Squeeze",
                "Bullish_Exit",
                "Bearish_Exit",
                "Screener_Full_Bullish",
                "Screener_Full_Bearish",
                "Trend_Pulse",
                "Sideways_Breakout"
            ]
        }
    
    async def process_entry_signal(self, alert) -> Dict[str, Any]:
        """
        Process V3 entry signal and execute trade.
        
        This method handles all 7 entry signal types plus the bonus signal:
        - Institutional_Launchpad
        - Liquidity_Trap
        - Momentum_Breakout
        - Mitigation_Test
        - Golden_Pocket_Flip
        - Screener_Full_Bullish/Bearish
        - Sideways_Breakout (bonus)
        
        V3 entries BYPASS trend check because Pine Script has already
        performed 5-layer pre-validation. Re-entries and autonomous
        actions still REQUIRE trend check.
        
        Args:
            alert: ZepixV3Alert or dict with signal data
            
        Returns:
            dict: Execution result with trade details
        """
        try:
            signal_type = self._get_signal_type(alert)
            symbol = self._get_symbol(alert)
            direction = self._get_direction(alert)
            
            self.logger.info(
                f"[V3 Entry] Signal: {signal_type} | "
                f"Symbol: {symbol} | Direction: {direction}"
            )
            
            # Step 1: Validate consensus score threshold
            if not self._validate_score_thresholds(alert):
                return {
                    "status": "rejected",
                    "reason": "low_consensus_score",
                    "signal_type": signal_type,
                    "symbol": symbol
                }
            
            # Step 2: Extract all alert data (including Pine Script SL/TP)
            alert_data = self._extract_alert_data(alert)
            self.logger.debug(f"[V3 Entry] Extracted alert data: {alert_data}")
            
            if self._is_aggressive_reversal_signal(alert):
                reversal_result = await self._handle_aggressive_reversal(alert)
                self.logger.info(f"Reversal result: {reversal_result.get('status')}")
            
            logic_route = self._route_to_logic(alert)
            logic_multiplier = self._get_logic_multiplier(logic_route)
            
            self.logger.debug(
                f"[V3 Routing] Signal: {signal_type} | "
                f"Route: {logic_route} | Multiplier: {logic_multiplier}"
            )
            
            if self.shadow_mode:
                return await self._process_shadow_entry(alert, logic_route, logic_multiplier)
            
            result = await self.order_manager.place_v3_dual_orders(
                alert=alert,
                logic_route=logic_route,
                logic_multiplier=logic_multiplier
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"[V3 Entry Error] {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    async def process_exit_signal(self, alert) -> Dict[str, Any]:
        """
        Process V3 exit signal and close trades.
        
        Handles:
        - Bullish_Exit: Close all SELL positions
        - Bearish_Exit: Close all BUY positions
        
        Args:
            alert: Exit alert data
            
        Returns:
            dict: Exit execution result
        """
        try:
            signal_type = self._get_signal_type(alert)
            symbol = self._get_symbol(alert)
            
            self.logger.info(f"[V3 Exit] Signal: {signal_type} | Symbol: {symbol}")
            
            if self.shadow_mode:
                return await self._process_shadow_exit(alert)
            
            result = await self.signal_handlers.handle_exit_signal(alert)
            
            return result
            
        except Exception as e:
            self.logger.error(f"[V3 Exit Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_reversal_signal(self, alert) -> Dict[str, Any]:
        """
        Process V3 reversal signal (close + opposite entry).
        
        Aggressive reversal signals:
        - Liquidity_Trap_Reversal
        - Golden_Pocket_Flip
        - Screener_Full_Bullish/Bearish
        - Any signal with consensus_score >= 7
        
        Args:
            alert: Reversal alert data
            
        Returns:
            dict: Reversal execution result
        """
        try:
            signal_type = self._get_signal_type(alert)
            symbol = self._get_symbol(alert)
            
            self.logger.info(f"[V3 Reversal] Signal: {signal_type} | Symbol: {symbol}")
            
            if self.shadow_mode:
                return await self._process_shadow_reversal(alert)
            
            result = await self.signal_handlers.handle_reversal_signal(alert)
            
            return result
            
        except Exception as e:
            self.logger.error(f"[V3 Reversal Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def on_signal_received(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Hook called when any signal is received.
        
        Routes signal to appropriate handler based on signal_type.
        
        Args:
            signal_data: Raw signal data from TradingView
            
        Returns:
            Modified signal data or None to reject
        """
        signal_type = signal_data.get("signal_type", "")
        alert_type = signal_data.get("type", "")
        
        if alert_type not in ["entry_v3", "exit_v3", "squeeze_v3", "trend_pulse_v3"]:
            return signal_data
        
        self.logger.debug(f"[V3 Hook] Signal received: {signal_type}")
        
        return signal_data
    
    def _route_to_logic(self, alert) -> str:
        """
        Route signal to Logic1/2/3 based on 2-tier routing matrix.
        
        Priority 1: Signal type overrides
        Priority 2: Timeframe routing
        Default: combinedlogic-2
        
        Args:
            alert: Alert data
            
        Returns:
            str: Logic route (combinedlogic-1, combinedlogic-2, combinedlogic-3)
        """
        signal_type = self._get_signal_type(alert)
        tf = self._get_timeframe(alert)
        
        overrides = self.plugin_config.get("signal_routing", {}).get("signal_overrides", {})
        if signal_type in overrides:
            route = overrides[signal_type]
            self.logger.debug(f"Signal override: {signal_type} -> {route}")
            return route
        
        if signal_type in ["Screener_Full_Bullish", "Screener_Full_Bearish"]:
            return "combinedlogic-3"
        
        if signal_type == "Golden_Pocket_Flip" and tf in ["60", "240"]:
            return "combinedlogic-3"
        
        tf_routing = self.plugin_config.get("signal_routing", {}).get("timeframe_routing", {})
        if tf in tf_routing:
            route = tf_routing[tf]
            self.logger.debug(f"TF routing: {tf}m -> {route}")
            return route
        
        default = self.plugin_config.get("signal_routing", {}).get("default_logic", "combinedlogic-2")
        self.logger.debug(f"Default routing -> {default}")
        return default
    
    def _get_logic_multiplier(self, logic_route: str) -> float:
        """
        Get lot multiplier for given logic route.
        
        Args:
            logic_route: Logic route (combinedlogic-1, combinedlogic-2, combinedlogic-3)
            
        Returns:
            float: Lot multiplier (1.25, 1.0, or 0.625)
        """
        multipliers = self.plugin_config.get("logic_multipliers", {})
        return multipliers.get(logic_route, 1.0)
    
    def _is_aggressive_reversal_signal(self, alert) -> bool:
        """
        Check if signal should trigger aggressive reversal (close + reverse).
        
        Args:
            alert: Alert data
            
        Returns:
            bool: True if aggressive reversal
        """
        signal_type = self._get_signal_type(alert)
        consensus_score = self._get_consensus_score(alert)
        
        aggressive_signals = self.plugin_config.get("aggressive_reversal_signals", [
            "Liquidity_Trap_Reversal",
            "Golden_Pocket_Flip",
            "Screener_Full_Bullish",
            "Screener_Full_Bearish"
        ])
        
        return signal_type in aggressive_signals or consensus_score >= 7
    
    async def _handle_aggressive_reversal(self, alert) -> Dict[str, Any]:
        """
        Handle aggressive reversal by closing conflicting positions.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Reversal result
        """
        symbol = self._get_symbol(alert)
        direction = self._get_direction(alert)
        
        close_direction = "SELL" if direction == "buy" else "BUY"
        
        self.logger.info(
            f"[V3 Aggressive Reversal] Closing {close_direction} positions on {symbol}"
        )
        
        try:
            result = await self.service_api.close_positions_by_direction(
                plugin_id=self.plugin_id,
                symbol=symbol,
                direction=close_direction
            )
            return {"status": "success", "closed": result}
        except Exception as e:
            self.logger.error(f"Reversal close error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _process_shadow_entry(self, alert, logic_route: str, logic_multiplier: float) -> Dict[str, Any]:
        """
        Process entry in shadow mode (no real orders).
        
        Args:
            alert: Alert data
            logic_route: Determined logic route
            logic_multiplier: Lot multiplier
            
        Returns:
            dict: Shadow mode result
        """
        signal_type = self._get_signal_type(alert)
        symbol = self._get_symbol(alert)
        direction = self._get_direction(alert)
        
        self.logger.info(
            f"[V3 SHADOW] Entry: {signal_type} | {symbol} {direction} | "
            f"Route: {logic_route} | Mult: {logic_multiplier}"
        )
        
        return {
            "status": "shadow",
            "action": "entry",
            "signal_type": signal_type,
            "symbol": symbol,
            "direction": direction,
            "logic_route": logic_route,
            "logic_multiplier": logic_multiplier,
            "message": "Shadow mode - no real orders placed"
        }
    
    async def _process_shadow_exit(self, alert) -> Dict[str, Any]:
        """Process exit in shadow mode"""
        signal_type = self._get_signal_type(alert)
        symbol = self._get_symbol(alert)
        
        self.logger.info(f"[V3 SHADOW] Exit: {signal_type} | {symbol}")
        
        return {
            "status": "shadow",
            "action": "exit",
            "signal_type": signal_type,
            "symbol": symbol,
            "message": "Shadow mode - no real exits"
        }
    
    async def _process_shadow_reversal(self, alert) -> Dict[str, Any]:
        """Process reversal in shadow mode"""
        signal_type = self._get_signal_type(alert)
        symbol = self._get_symbol(alert)
        
        self.logger.info(f"[V3 SHADOW] Reversal: {signal_type} | {symbol}")
        
        return {
            "status": "shadow",
            "action": "reversal",
            "signal_type": signal_type,
            "symbol": symbol,
            "message": "Shadow mode - no real reversals"
        }
    
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
    
    def _get_timeframe(self, alert) -> str:
        """Extract timeframe from alert"""
        if hasattr(alert, 'tf'):
            return str(alert.tf)
        if isinstance(alert, dict):
            return str(alert.get('tf', ''))
        return ''
    
    def _get_consensus_score(self, alert) -> int:
        """Extract consensus_score from alert"""
        if hasattr(alert, 'consensus_score'):
            return alert.consensus_score
        if isinstance(alert, dict):
            return alert.get('consensus_score', 0)
        return 0
    
    def _validate_score_thresholds(self, alert) -> bool:
        """
        Validate consensus score meets minimum threshold.
        
        Pine Script consensus_score range: 0-9
        - 0-4: Low confidence (REJECT)
        - 5-6: Medium confidence (ACCEPT)
        - 7-9: High confidence (ACCEPT with priority)
        
        Special Rules:
        - Institutional_Launchpad BUY: Requires score >= 7
        - All other signals: Requires score >= 5 (configurable)
        
        Args:
            alert: Alert data (dict or ZepixV3Alert)
            
        Returns:
            bool: True if score meets threshold, False to reject
        """
        score = self._get_consensus_score(alert)
        signal_type = self._get_signal_type(alert)
        direction = self._get_direction(alert)
        
        # Special threshold for Institutional Launchpad BUY
        if "Institutional_Launchpad" in signal_type and direction == "buy":
            if score < 7:
                self.logger.warning(
                    f"[V3 Score Filter] Launchpad BUY REJECTED: score {score} < 7"
                )
                return False
            self.logger.info(f"[V3 Score Filter] Launchpad BUY ACCEPTED: score {score} >= 7")
            return True
        
        # Global minimum threshold
        min_score = self.plugin_config.get('min_consensus_score', 5)
        
        if score < min_score:
            self.logger.warning(
                f"[V3 Score Filter] Signal REJECTED: consensus_score {score} < min {min_score}"
            )
            return False
        
        self.logger.debug(f"[V3 Score Filter] Score {score} >= min {min_score} - ACCEPTED")
        return True
    
    def _extract_alert_data(self, alert) -> Dict[str, Any]:
        """
        Extract and validate all alert data from Pine Script signal.
        
        CRITICAL: alert.sl_price MUST override internal calculation for Order A.
        Order B uses fixed $10 risk SL regardless of alert.sl_price.
        
        Args:
            alert: Alert data (dict or ZepixV3Alert)
            
        Returns:
            dict: Normalized alert data with all fields
        """
        # Handle both dict and object formats
        if hasattr(alert, 'symbol'):
            # ZepixV3Alert object
            return {
                'symbol': alert.symbol,
                'direction': alert.direction,
                'price': alert.price,
                'signal_type': alert.signal_type,
                'tf': str(alert.tf),
                'consensus_score': alert.consensus_score,
                'position_multiplier': getattr(alert, 'position_multiplier', 1.0),
                
                # CRITICAL: SL/TP from Pine Script
                'sl_price': getattr(alert, 'sl_price', None),  # Order A uses this
                'tp1_price': getattr(alert, 'tp1_price', None),  # Order B target
                'tp2_price': getattr(alert, 'tp2_price', None),  # Order A target
                
                # MTF trends (handles both 5 and 6 value formats)
                'mtf_trends': getattr(alert, 'mtf_trends', ''),
                'market_trend': getattr(alert, 'market_trend', 0),
                
                # Extra Pine Script fields
                'fib_level': getattr(alert, 'fib_level', None),
                'adx_value': getattr(alert, 'adx_value', None),
                'confidence': getattr(alert, 'confidence', None),
                'full_alignment': getattr(alert, 'full_alignment', None),
                'volume_delta_ratio': getattr(alert, 'volume_delta_ratio', None),
                'price_in_ob': getattr(alert, 'price_in_ob', None),
                
                # V3 Enhanced Pine Script fields
                'volume_profile': getattr(alert, 'volume_profile', None),
                'order_block_strength': getattr(alert, 'order_block_strength', None),
                'liquidity_zone_distance': getattr(alert, 'liquidity_zone_distance', None),
                'smart_money_flow': getattr(alert, 'smart_money_flow', None),
                'institutional_footprint': getattr(alert, 'institutional_footprint', None),
            }
        else:
            # Dict format
            return {
                'symbol': alert.get('symbol', ''),
                'direction': alert.get('direction', ''),
                'price': alert.get('price', 0.0),
                'signal_type': alert.get('signal_type', ''),
                'tf': str(alert.get('tf', '15')),
                'consensus_score': alert.get('consensus_score', 0),
                'position_multiplier': alert.get('position_multiplier', 1.0),
                
                # CRITICAL: SL/TP from Pine Script
                'sl_price': alert.get('sl_price'),  # Order A uses this
                'tp1_price': alert.get('tp1_price'),  # Order B target
                'tp2_price': alert.get('tp2_price'),  # Order A target
                
                # MTF trends (handles both 5 and 6 value formats)
                'mtf_trends': alert.get('mtf_trends', ''),
                'market_trend': alert.get('market_trend', 0),
                
                # Extra Pine Script fields
                'fib_level': alert.get('fib_level'),
                'adx_value': alert.get('adx_value'),
                'confidence': alert.get('confidence'),
                'full_alignment': alert.get('full_alignment'),
                'volume_delta_ratio': alert.get('volume_delta_ratio'),
                'price_in_ob': alert.get('price_in_ob'),
                
                # V3 Enhanced Pine Script fields
                'volume_profile': alert.get('volume_profile'),
                'order_block_strength': alert.get('order_block_strength'),
                'liquidity_zone_distance': alert.get('liquidity_zone_distance'),
                'smart_money_flow': alert.get('smart_money_flow'),
                'institutional_footprint': alert.get('institutional_footprint'),
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status"""
        base_status = super().get_status()
        base_status.update({
            "shadow_mode": self.shadow_mode,
            "supported_signals": self.metadata.get("supported_signals", []),
            "logic_multipliers": self.plugin_config.get("logic_multipliers", {})
        })
        return base_status

    # ========== ISignalProcessor Interface Implementation ==========
    
    def _check_v3_trend_alignment(self, signal: Dict[str, Any]) -> bool:
        """
        Check V3 trend alignment using MTF 4-pillar validation.
        
        Args:
            signal: Trading signal with timeframe and direction info
            
        Returns:
            True if trend is aligned across timeframes
        """
        if not self.trend_validator:
            return True
        
        symbol = signal.get('symbol', 'EURUSD')
        direction = signal.get('direction', signal.get('signal_type', ''))
        timeframe = signal.get('timeframe', signal.get('tf', '15m'))
        
        # Use trend validator for MTF alignment check
        try:
            alignment = self.trend_validator.validate_mtf_alignment(
                symbol=symbol,
                direction=direction,
                entry_timeframe=timeframe
            )
            return alignment.get('aligned', True)
        except Exception as e:
            self.logger.warning(f"Trend alignment check failed: {e}")
            return True  # Default to allowing trade if check fails
    
    def get_supported_strategies(self) -> List[str]:
        """
        Return list of strategy names this plugin supports.
        Used by PluginRegistry for signal-based plugin lookup.
        """
        return ['V3_COMBINED', 'COMBINED_V3', 'V3']
    
    def get_supported_timeframes(self) -> List[str]:
        """
        Return list of timeframes this plugin supports.
        V3 Combined supports all standard timeframes.
        """
        return ['5m', '15m', '1h', '5', '15', '60']
    
    async def can_process_signal(self, signal_data: Dict[str, Any]) -> bool:
        """
        Check if this plugin can process the given signal.
        
        Args:
            signal_data: Signal data dictionary
            
        Returns:
            bool: True if this plugin can handle the signal
        """
        strategy = signal_data.get('strategy', '')
        alert_type = signal_data.get('type', '')
        
        # Check if strategy matches
        if strategy in self.get_supported_strategies():
            return True
        
        # Check if alert type is V3
        if 'v3' in alert_type.lower():
            return True
        
        return False
    
    async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process the signal and return result.
        Routes to appropriate handler based on signal type.
        
        Args:
            signal_data: Signal data dictionary
            
        Returns:
            dict: Execution result
        """
        alert_type = signal_data.get('type', '')
        
        if 'entry' in alert_type.lower():
            return await self.process_entry_signal(signal_data)
        elif 'exit' in alert_type.lower():
            return await self.process_exit_signal(signal_data)
        elif 'reversal' in alert_type.lower():
            return await self.process_reversal_signal(signal_data)
        else:
            # Default to entry processing
            return await self.process_entry_signal(signal_data)

    # ========== IOrderExecutor Interface Implementation ==========
    
    async def execute_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute an order and return result.
        Delegates to order_manager for actual execution.
        
        Args:
            order_data: Order parameters
            
        Returns:
            dict: Order execution result
        """
        try:
            return await self.order_manager.execute_order(order_data)
        except Exception as e:
            self.logger.error(f"Order execution failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> bool:
        """
        Modify an existing order.
        
        Args:
            order_id: MT5 order/position ID
            modifications: Fields to modify
            
        Returns:
            bool: True if modification successful
        """
        try:
            return await self.order_manager.modify_order(order_id, modifications)
        except Exception as e:
            self.logger.error(f"Order modification failed: {e}")
            return False
    
    async def close_order(self, order_id: str, reason: str) -> bool:
        """
        Close an existing order.
        
        Args:
            order_id: MT5 order/position ID
            reason: Reason for closing
            
        Returns:
            bool: True if close successful
        """
        try:
            return await self.order_manager.close_order(order_id, reason)
        except Exception as e:
            self.logger.error(f"Order close failed: {e}")
            return False
    
    # =========================================================================
    # IReentryCapable Interface Implementation (Plan 03)
    # =========================================================================
    
    async def on_sl_hit(self, event: ReentryEvent) -> bool:
        """
        Handle SL hit event - start SL Hunt Recovery if enabled.
        
        SL Hunt Recovery monitors price for 70% recovery within symbol-specific
        window (EURUSD: 30min, GBPUSD: 20min, etc.).
        
        Now includes safety checks (Plan 06):
        - Daily recovery limit check
        - Concurrent recovery limit check
        - Profit protection check
        - Reverse Shield activation
        
        Args:
            event: ReentryEvent with trade details
            
        Returns:
            bool: True if recovery started successfully
        """
        if not self._reentry_service:
            self.logger.warning("ReentryService not available for SL Hunt")
            return False
        
        # Check if SL Hunt is enabled in config
        sl_hunt_enabled = self.plugin_config.get("sl_hunt_recovery", {}).get("enabled", True)
        if not sl_hunt_enabled:
            self.logger.info(f"SL Hunt disabled for {event.trade_id}")
            return False
        
        # Check chain level limit (V3 max = 5)
        current_level = self.get_chain_level(event.trade_id)
        if current_level >= self.get_max_chain_level():
            self.logger.warning(
                f"Max chain level reached for {event.trade_id}: {current_level}/{self.get_max_chain_level()}"
            )
            return False
        
        # ==================== Plan 06: Safety Checks ====================
        # Check if recovery is allowed (daily/concurrent limits, profit protection)
        safety_check = await self.check_recovery_allowed()
        if not safety_check.allowed:
            self.logger.info(f"Recovery blocked for {event.trade_id}: {safety_check.reason}")
            return False
        
        # Activate Reverse Shield if enabled
        rs_enabled = self.plugin_config.get("reverse_shield_enabled", True)
        if rs_enabled:
            shield_status = await self.activate_reverse_shield(
                trade_id=event.trade_id,
                symbol=event.symbol,
                direction=event.direction
            )
            if shield_status.active:
                self.logger.info(f"Reverse Shield activated for {event.trade_id}")
                # Store recovery level in event metadata for shield monitoring
                event.metadata = event.metadata or {}
                event.metadata['recovery_70_level'] = shield_status.recovery_70_level
                event.metadata['shield_id'] = shield_status.shield_id
        
        # Increment recovery count
        await self.increment_recovery_count()
        # ==================== End Plan 06 ====================
        
        # Update event with current chain level
        event.chain_level = current_level
        
        self.logger.info(
            f"SL Hunt Recovery starting for {event.trade_id} | "
            f"Symbol: {event.symbol} | Chain: {current_level}"
        )
        
        # Start SL Hunt Recovery via ReentryService
        success = await self._reentry_service.start_sl_hunt_recovery(event)
        
        if success:
            # Increment chain level
            self._chain_levels[event.trade_id] = current_level + 1
            self.logger.info(f"SL Hunt Recovery started for {event.trade_id}")
        
        return success
    
    async def on_tp_hit(self, event: ReentryEvent) -> bool:
        """
        Handle TP hit event - start TP Continuation.
        
        TP Continuation reduces SL by 10% per chain level (min 50%)
        and continues trading in the same direction.
        
        Args:
            event: ReentryEvent with trade details
            
        Returns:
            bool: True if continuation started successfully
        """
        if not self._reentry_service:
            self.logger.warning("ReentryService not available for TP Continuation")
            return False
        
        # Check if TP Continuation is enabled
        tp_cont_enabled = self.plugin_config.get("tp_continuation", {}).get("enabled", True)
        if not tp_cont_enabled:
            self.logger.info(f"TP Continuation disabled for {event.trade_id}")
            return False
        
        # Check chain level limit
        current_level = self.get_chain_level(event.trade_id)
        if current_level >= self.get_max_chain_level():
            self.logger.warning(
                f"Max chain level reached for TP Continuation: {current_level}/{self.get_max_chain_level()}"
            )
            return False
        
        event.chain_level = current_level
        
        self.logger.info(
            f"TP Continuation starting for {event.trade_id} | "
            f"Symbol: {event.symbol} | Chain: {current_level}"
        )
        
        # Start TP Continuation via ReentryService
        success = await self._reentry_service.start_tp_continuation(event)
        
        if success:
            self._chain_levels[event.trade_id] = current_level + 1
            self.logger.info(f"TP Continuation started for {event.trade_id}")
        
        return success
    
    async def on_exit(self, event: ReentryEvent) -> bool:
        """
        Handle exit event - start Exit Continuation monitoring.
        
        Exit Continuation monitors for 60 seconds after manual/reversal exit
        to detect continuation opportunities.
        
        Args:
            event: ReentryEvent with trade details
            
        Returns:
            bool: True if monitoring started successfully
        """
        if not self._reentry_service:
            self.logger.warning("ReentryService not available for Exit Continuation")
            return False
        
        # Check if Exit Continuation is enabled
        exit_cont_enabled = self.plugin_config.get("exit_continuation", {}).get("enabled", True)
        if not exit_cont_enabled:
            self.logger.info(f"Exit Continuation disabled for {event.trade_id}")
            return False
        
        event.chain_level = self.get_chain_level(event.trade_id)
        
        self.logger.info(
            f"Exit Continuation monitoring starting for {event.trade_id} | "
            f"Symbol: {event.symbol}"
        )
        
        # Start Exit Continuation via ReentryService
        success = await self._reentry_service.start_exit_continuation(event)
        
        if success:
            self.logger.info(f"Exit Continuation monitoring started for {event.trade_id}")
        
        return success
    
    async def on_recovery_signal(self, event: ReentryEvent) -> bool:
        """
        Handle recovery signal - execute re-entry order.
        
        Called when ReentryService detects a recovery opportunity
        (70% price recovery for SL Hunt, continuation signal for TP/Exit).
        
        Now includes Reverse Shield deactivation (Plan 06).
        
        Args:
            event: ReentryEvent with recovery details
            
        Returns:
            bool: True if re-entry order executed successfully
        """
        self.logger.info(
            f"Recovery signal received for {event.trade_id} | "
            f"Type: {event.reentry_type.value} | Chain: {event.chain_level}"
        )
        
        # ==================== Plan 06: Deactivate Reverse Shield ====================
        # Deactivate shield since recovery is being executed
        if event.trade_id in self._active_shields:
            await self.deactivate_reverse_shield(event.trade_id)
            self.logger.info(f"Reverse Shield deactivated for recovery: {event.trade_id}")
        # ==================== End Plan 06 ====================
        
        # Build re-entry signal based on recovery type
        reentry_signal = {
            "signal_type": "recovery_entry",
            "symbol": event.symbol,
            "direction": event.direction,
            "entry_price": event.entry_price,
            "sl_price": event.sl_price,
            "chain_level": event.chain_level,
            "recovery_type": event.reentry_type.value,
            "original_trade_id": event.trade_id,
            "metadata": event.metadata
        }
        
        # Calculate reduced SL for TP Continuation
        if event.reentry_type == ReentryType.TP_CONTINUATION:
            # 10% reduction per chain level, min 50%
            reduction = min(0.1 * event.chain_level, 0.5)
            original_sl_distance = abs(event.entry_price - event.sl_price)
            reduced_sl_distance = original_sl_distance * (1 - reduction)
            
            if event.direction.upper() == "BUY":
                reentry_signal["sl_price"] = event.entry_price - reduced_sl_distance
            else:
                reentry_signal["sl_price"] = event.entry_price + reduced_sl_distance
            
            self.logger.info(
                f"TP Continuation SL reduced by {reduction*100}% | "
                f"New SL: {reentry_signal['sl_price']}"
            )
        
        # Execute re-entry via order manager
        try:
            result = await self.order_manager.execute_recovery_order(reentry_signal)
            
            if result:
                self.logger.info(f"Re-entry order executed for {event.trade_id}")
                return True
            else:
                self.logger.warning(f"Re-entry order failed for {event.trade_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Re-entry execution error: {e}")
            return False
    
    def get_chain_level(self, trade_id: str) -> int:
        """
        Get current chain level for a trade.
        
        Args:
            trade_id: Trade identifier
            
        Returns:
            int: Current chain level (0 = original trade)
        """
        return self._chain_levels.get(trade_id, 0)
    
    def get_max_chain_level(self) -> int:
        """
        Get maximum allowed chain level for V3 plugin.
        
        V3 plugins allow up to 5 chain levels (more aggressive).
        V6 plugins allow up to 3 chain levels (more conservative).
        
        Returns:
            int: Maximum chain level (5 for V3)
        """
        return self.plugin_config.get("max_chain_level", 5)
    
    # ==================== IDatabaseCapable Implementation (Plan 09) ====================
    
    def get_database_config(self) -> DatabaseConfig:
        """
        Get database configuration for V3 plugin.
        
        V3 plugin uses isolated database: data/zepix_combined_v3.db
        
        Returns:
            DatabaseConfig with V3 database settings
        """
        return DatabaseConfig(
            plugin_id=self.plugin_id,
            db_path='data/zepix_combined_v3.db',
            schema_version='1.0.0',
            tables=['combined_v3_trades', 'v3_profit_bookings', 'v3_signals_log', 'v3_daily_stats']
        )
    
    async def initialize_database(self) -> bool:
        """
        Initialize V3 plugin's database with schema.
        
        Creates tables if they don't exist using the V3 schema file.
        
        Returns:
            True if initialization successful
        """
        if not hasattr(self, '_service_api') or not self._service_api:
            self.logger.warning("ServiceAPI not available for database initialization")
            return False
        
        try:
            db_service = self._service_api.database_service
            if db_service:
                return await db_service.initialize_database(self.plugin_id)
            return False
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Execute a query on V3 plugin's database.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result rows as dictionaries
        """
        if not hasattr(self, '_service_api') or not self._service_api:
            return []
        
        try:
            db_service = self._service_api.database_service
            if db_service:
                return await db_service.execute_query(self.plugin_id, query, params)
            return []
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return []
    
    async def insert_record(self, table: str, data: Dict[str, Any]) -> int:
        """
        Insert a record into V3 plugin's database.
        
        Args:
            table: Table name
            data: Record data as dictionary
            
        Returns:
            ID of inserted record
        """
        if not hasattr(self, '_service_api') or not self._service_api:
            return -1
        
        try:
            db_service = self._service_api.database_service
            if db_service:
                return await db_service.insert_record(self.plugin_id, table, data)
            return -1
        except Exception as e:
            self.logger.error(f"Insert failed: {e}")
            return -1
    
    async def update_record(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """
        Update records in V3 plugin's database.
        
        Args:
            table: Table name
            data: Fields to update
            where: Conditions for update
            
        Returns:
            Number of records updated
        """
        if not hasattr(self, '_service_api') or not self._service_api:
            return 0
        
        try:
            db_service = self._service_api.database_service
            if db_service:
                return await db_service.update_record(self.plugin_id, table, data, where)
            return 0
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
            return 0
    
    async def save_trade(self, trade_data: Dict[str, Any]) -> int:
        """
        Save a trade to V3 database.
        
        Convenience method for saving trades with proper field mapping.
        
        Args:
            trade_data: Trade data dictionary
            
        Returns:
            ID of saved trade
        """
        return await self.insert_record('combined_v3_trades', trade_data)
    
    async def get_trades(self, status: str = None) -> List[Dict]:
        """
        Get trades from V3 database.
        
        Args:
            status: Optional status filter (OPEN, PARTIAL, CLOSED)
            
        Returns:
            List of trade records
        """
        if status:
            return await self.execute_query(
                "SELECT * FROM combined_v3_trades WHERE status = ?",
                (status,)
            )
        return await self.execute_query("SELECT * FROM combined_v3_trades")
