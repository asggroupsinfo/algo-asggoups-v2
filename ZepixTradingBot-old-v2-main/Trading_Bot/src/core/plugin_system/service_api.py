"""
ServiceAPI - Unified Service Layer for V5 Hybrid Plugin Architecture

This module provides a unified facade over all core services, allowing plugins
to access bot functionality through a single, controlled interface.

The ServiceAPI is the SINGLE point of entry for plugins. Plugins should ONLY
talk to ServiceAPI, never directly to MT5, RiskManager, or other managers.

Plan 08: Service API Integration
- All services registered with ServiceAPI
- Plugins use ServiceAPI exclusively
- Service discovery works
- Service metrics collected
- Service health checks work

Version: 3.0.0 (Plan 08 - Complete Service Integration)
Date: 2026-01-15

Services Integrated:
- OrderExecutionService: V3 dual orders, V6 conditional orders
- RiskManagementService: Lot size calculation, ATR-based SL/TP, daily limits
- TrendManagementService: V3 4-pillar trends, V6 Trend Pulse
- MarketDataService: Spread checks, price data, volatility analysis
- ReentryService: SL Hunt, TP Continuation, Exit Continuation (Plan 03)
- DualOrderService: Order A/B management (Plan 04)
- ProfitBookingService: Profit chains, pyramid levels (Plan 05)
- AutonomousService: Safety checks, Reverse Shield (Plan 06)
- TelegramService: 3-Bot notification routing (Plan 07)
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
import logging
import asyncio
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ==================== Plan 08: Service Metrics ====================

@dataclass
class ServiceMetrics:
    """Metrics for tracking service calls"""
    calls: int = 0
    errors: int = 0
    total_time_ms: float = 0.0
    last_call: Optional[datetime] = None
    last_error: Optional[str] = None
    
    @property
    def avg_time_ms(self) -> float:
        """Calculate average call time"""
        return self.total_time_ms / self.calls if self.calls > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage"""
        return (self.errors / self.calls * 100) if self.calls > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'calls': self.calls,
            'errors': self.errors,
            'avg_time_ms': self.avg_time_ms,
            'error_rate': self.error_rate,
            'last_call': self.last_call.isoformat() if self.last_call else None,
            'last_error': self.last_error
        }


@dataclass
class ServiceRegistration:
    """Service registration info"""
    name: str
    service: Any
    health_check: Optional[Callable] = None
    is_healthy: bool = True
    registered_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'is_healthy': self.is_healthy,
            'registered_at': self.registered_at.isoformat()
        }

# ==================== End Plan 08: Service Metrics ====================


class ServiceAPI:
    """
    Unified Service API - Single point of entry for all plugin operations.
    
    This class acts as a facade over all core services, providing:
    - Order execution (V3 dual orders, V6 conditional orders)
    - Risk management (lot sizing, daily limits, ATR-based SL/TP)
    - Trend analysis (V3 4-pillar, V6 Trend Pulse)
    - Market data (spread, price, volatility)
    
    Plugins should ONLY interact with this class, never directly with
    MT5, RiskManager, or other managers.
    
    Usage:
        # For plugins (with plugin_id)
        api = ServiceAPI(trading_engine, plugin_id="v3_combined")
        lot = await api.calculate_lot_size(symbol="XAUUSD", risk_pct=1.5, sl_pips=50)
        
        # For core bot (backward compatible)
        api = ServiceAPI(trading_engine)
        price = api.get_price("XAUUSD")
    """
    
    VERSION = "3.0.0"
    
    def __init__(self, trading_engine, plugin_id: str = "core"):
        """
        Initialize ServiceAPI with trading engine and optional plugin_id.
        
        Args:
            trading_engine: The main TradingEngine instance
            plugin_id: Plugin identifier for tracking (default: "core" for legacy)
        """
        self._engine = trading_engine
        self._plugin_id = plugin_id
        self._config = trading_engine.config
        self.config = trading_engine.config  # Alias for compatibility
        self._mt5 = trading_engine.mt5_client
        self._risk = trading_engine.risk_manager
        self._telegram = trading_engine.telegram_bot
        self._logger = logger
        
        self._order_service = None
        self._risk_service = None
        self._trend_service = None
        self._market_service = None
        
        # Plan 08: Service Registry
        self._service_registry: Dict[str, ServiceRegistration] = {}
        self._service_metrics: Dict[str, ServiceMetrics] = {}
        
        self._services_initialized = False
        self._init_services()
    
    def _init_services(self):
        """
        Initialize all services from Batch 03.
        
        Services are lazily initialized to avoid circular dependencies.
        If services cannot be imported, the API falls back to direct calls.
        """
        try:
            from src.core.services import (
                OrderExecutionService,
                RiskManagementService,
                TrendManagementService,
                MarketDataService
            )
            
            pip_calculator = getattr(self._engine, 'pip_calculator', None)
            if pip_calculator is None:
                pip_calculator = self._create_default_pip_calculator()
            
            trend_manager = getattr(self._engine, 'timeframe_trend_manager', None)
            if trend_manager is None:
                trend_manager = getattr(self._engine, 'trend_manager', None)
            
            self._order_service = OrderExecutionService(
                mt5_client=self._mt5,
                config=self._config,
                pip_calculator=pip_calculator
            )
            
            self._risk_service = RiskManagementService(
                risk_manager=self._risk,
                config=self._config,
                mt5_client=self._mt5,
                pip_calculator=pip_calculator
            )
            
            self._trend_service = TrendManagementService(
                trend_manager=trend_manager,
                db=getattr(self._engine, 'database', None)
            )
            
            self._market_service = MarketDataService(
                mt5_client=self._mt5,
                config=self._config,
                pip_calculator=pip_calculator
            )
            
            self._services_initialized = True
            self._logger.info(f"[ServiceAPI] Services initialized for plugin: {self._plugin_id}")
            
        except ImportError as e:
            self._logger.warning(f"[ServiceAPI] Services not available, using fallback: {e}")
            self._services_initialized = False
        except Exception as e:
            self._logger.error(f"[ServiceAPI] Error initializing services: {e}")
            self._services_initialized = False
    
    def _create_default_pip_calculator(self):
        """Create a default pip calculator if none exists"""
        class DefaultPipCalculator:
            def get_pip_value(self, symbol: str, lot_size: float) -> float:
                if symbol in ['XAUUSD', 'XAGUSD']:
                    return lot_size * 10.0
                return lot_size * 10.0
            
            def get_pip_size(self, symbol: str) -> float:
                if symbol in ['XAUUSD', 'XAGUSD']:
                    return 0.1
                return 0.0001
            
            def get_digits(self, symbol: str) -> int:
                if symbol in ['XAUUSD', 'XAGUSD']:
                    return 2
                return 5
        
        return DefaultPipCalculator()
    
    @property
    def plugin_id(self) -> str:
        """Get the plugin ID for this API instance"""
        return self._plugin_id
    
    @property
    def services_available(self) -> bool:
        """Check if services are properly initialized"""
        return self._services_initialized

    # =========================================================================
    # PLAN 08: SERVICE REGISTRATION & DISCOVERY
    # =========================================================================
    
    def register_service(self, name: str, service: Any, health_check: Optional[Callable] = None) -> None:
        """
        Register a service with the API.
        
        Args:
            name: Service name (e.g., 'order_execution', 'reentry', 'dual_order')
            service: Service instance
            health_check: Optional health check function
        """
        registration = ServiceRegistration(
            name=name,
            service=service,
            health_check=health_check
        )
        self._service_registry[name] = registration
        self._service_metrics[name] = ServiceMetrics()
        self._logger.info(f"[ServiceAPI] Service registered: {name}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """
        Get a registered service by name.
        
        Args:
            name: Service name
        
        Returns:
            Service instance or None if not found
        """
        registration = self._service_registry.get(name)
        return registration.service if registration else None
    
    def has_service(self, name: str) -> bool:
        """Check if a service is registered"""
        return name in self._service_registry
    
    def list_services(self) -> List[str]:
        """List all registered service names"""
        return list(self._service_registry.keys())
    
    def discover_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all registered services with their info.
        
        Returns:
            Dict of service name -> service info
        """
        return {
            name: reg.to_dict()
            for name, reg in self._service_registry.items()
        }
    
    # =========================================================================
    # PLAN 08: SERVICE PROPERTIES (Convenience Access)
    # =========================================================================
    
    @property
    def reentry_service(self):
        """Get re-entry service (Plan 03)"""
        return self.get_service('reentry')
    
    @property
    def dual_order_service(self):
        """Get dual order service (Plan 04)"""
        return self.get_service('dual_order')
    
    @property
    def profit_booking_service(self):
        """Get profit booking service (Plan 05)"""
        return self.get_service('profit_booking')
    
    @property
    def autonomous_service(self):
        """Get autonomous service (Plan 06)"""
        return self.get_service('autonomous')
    
    @property
    def telegram_service(self):
        """Get telegram service (Plan 07)"""
        return self.get_service('telegram')
    
    @property
    def database_service(self):
        """Get database service (Plan 09)"""
        return self.get_service('database')
    
    # =========================================================================
    # PLAN 08: SERVICE CALL WRAPPER WITH METRICS
    # =========================================================================
    
    async def call_service(self, service_name: str, method_name: str, *args, **kwargs) -> Any:
        """
        Call a service method with metrics tracking.
        
        Args:
            service_name: Name of the registered service
            method_name: Method to call on the service
            *args, **kwargs: Arguments to pass to the method
        
        Returns:
            Result from the service method
        """
        service = self.get_service(service_name)
        if not service:
            self._logger.error(f"[ServiceAPI] Service not found: {service_name}")
            return None
        
        method = getattr(service, method_name, None)
        if not method:
            self._logger.error(f"[ServiceAPI] Method not found: {service_name}.{method_name}")
            return None
        
        # Track metrics
        metrics = self._service_metrics.get(service_name)
        if metrics:
            metrics.calls += 1
            metrics.last_call = datetime.now()
        
        start_time = datetime.now()
        try:
            if asyncio.iscoroutinefunction(method):
                result = await method(*args, **kwargs)
            else:
                result = method(*args, **kwargs)
            
            if metrics:
                elapsed = (datetime.now() - start_time).total_seconds() * 1000
                metrics.total_time_ms += elapsed
            
            return result
        except Exception as e:
            if metrics:
                metrics.errors += 1
                metrics.last_error = str(e)
            self._logger.error(f"[ServiceAPI] Service call failed: {service_name}.{method_name}: {e}")
            raise
    
    # =========================================================================
    # PLAN 08: SERVICE HEALTH CHECKS
    # =========================================================================
    
    async def check_health(self) -> Dict[str, bool]:
        """
        Check health of all registered services.
        
        Returns:
            Dict of service name -> health status
        """
        results = {}
        
        for name, registration in self._service_registry.items():
            if registration.health_check:
                try:
                    if asyncio.iscoroutinefunction(registration.health_check):
                        results[name] = await registration.health_check()
                    else:
                        results[name] = registration.health_check()
                    registration.is_healthy = results[name]
                except Exception as e:
                    self._logger.error(f"[ServiceAPI] Health check failed for {name}: {e}")
                    results[name] = False
                    registration.is_healthy = False
            else:
                # No health check defined, assume healthy
                results[name] = True
        
        return results
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get health status of all services"""
        return {
            name: reg.is_healthy
            for name, reg in self._service_registry.items()
        }
    
    # =========================================================================
    # PLAN 08: SERVICE METRICS
    # =========================================================================
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all services.
        
        Returns:
            Dict of service name -> metrics dict
        """
        return {
            name: metrics.to_dict()
            for name, metrics in self._service_metrics.items()
        }
    
    def get_service_metrics(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific service"""
        metrics = self._service_metrics.get(service_name)
        return metrics.to_dict() if metrics else None
    
    def reset_metrics(self, service_name: str = None) -> None:
        """
        Reset metrics for a service or all services.
        
        Args:
            service_name: Service to reset, or None for all
        """
        if service_name:
            if service_name in self._service_metrics:
                self._service_metrics[service_name] = ServiceMetrics()
        else:
            for name in self._service_metrics:
                self._service_metrics[name] = ServiceMetrics()
    
    # =========================================================================
    # PLAN 08: SERVICE OPERATIONS (Via ServiceAPI)
    # =========================================================================
    
    async def execute_order(self, order_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an order through order service"""
        return await self.call_service('order_execution', 'execute_order', order_params)
    
    async def start_recovery(self, event: Any) -> bool:
        """Start recovery through reentry service"""
        return await self.call_service('reentry', 'start_sl_hunt_recovery', event)
    
    async def create_dual_orders(self, signal: Dict, config_a: Any, config_b: Any) -> Any:
        """Create dual orders through dual order service"""
        return await self.call_service('dual_order', 'create_dual_orders', signal, config_a, config_b)
    
    async def create_profit_chain(self, plugin_id: str, order_b_id: str, symbol: str, direction: str) -> Any:
        """Create profit chain through profit booking service"""
        return await self.call_service('profit_booking', 'create_chain', plugin_id, order_b_id, symbol, direction)
    
    async def check_safety(self, plugin_id: str) -> Any:
        """Check safety through autonomous service"""
        return await self.call_service('autonomous', 'check_recovery_allowed', plugin_id)
    
    async def send_telegram_notification(self, notification_type: str, message: str, **kwargs) -> Any:
        """Send notification through telegram service"""
        return await self.call_service('telegram', 'send_notification', notification_type, message, **kwargs)

    # =========================================================================
    # MARKET DATA METHODS (MarketDataService)
    # =========================================================================

    def get_price(self, symbol: str) -> float:
        """
        Get current price for a symbol (backward compatible).
        
        Args:
            symbol: Trading symbol (e.g., 'XAUUSD')
        
        Returns:
            Current bid price or 0.0 if unavailable
        """
        tick = self._mt5.get_symbol_tick(symbol)
        if tick:
            return tick.get('bid', 0.0)
        return 0.0

    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Get symbol validation info (backward compatible).
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Dict with symbol information
        """
        return self._mt5.get_symbol_info(symbol)
    
    async def get_current_spread(self, symbol: str) -> float:
        """
        Get current spread in pips (via MarketDataService).
        
        Critical for V6 1M plugin spread filtering.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Spread in pips
        """
        if self._market_service:
            return await self._market_service.get_current_spread(symbol)
        return 999.9
    
    async def check_spread_acceptable(self, symbol: str, max_spread_pips: float) -> bool:
        """
        Check if spread is within acceptable range.
        
        Args:
            symbol: Trading symbol
            max_spread_pips: Maximum acceptable spread
        
        Returns:
            True if spread is acceptable
        """
        if self._market_service:
            return await self._market_service.check_spread_acceptable(symbol, max_spread_pips)
        return True
    
    async def get_current_price_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive current price data.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Dict with bid, ask, spread, timestamp
        """
        if self._market_service:
            return await self._market_service.get_current_price(symbol)
        return {"bid": self.get_price(symbol), "ask": 0.0, "spread_pips": 0.0}
    
    async def get_volatility_state(self, symbol: str, timeframe: str = '15m') -> Dict[str, Any]:
        """
        Get current volatility state.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe for analysis
        
        Returns:
            Dict with state (HIGH/MODERATE/LOW), ATR values
        """
        if self._market_service:
            return await self._market_service.get_volatility_state(symbol, timeframe)
        return {"state": "UNKNOWN"}
    
    async def is_market_open(self, symbol: str) -> bool:
        """
        Check if market is currently open.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            True if market is open
        """
        if self._market_service:
            return await self._market_service.is_market_open(symbol)
        return True

    # =========================================================================
    # ACCOUNT INFO METHODS
    # =========================================================================

    def get_balance(self) -> float:
        """Get current account balance (backward compatible)"""
        return self._mt5.get_account_balance()
    
    def get_equity(self) -> float:
        """Get current account equity (backward compatible)"""
        return self._mt5.get_account_equity()

    # =========================================================================
    # ORDER EXECUTION METHODS (OrderExecutionService)
    # =========================================================================

    def place_order(self, symbol: str, direction: str, lot_size: float, 
                   sl_price: float = 0.0, tp_price: float = 0.0, 
                   comment: str = "", **kwargs) -> Optional[int]:
        """
        Place a new order (backward compatible).
        
        Args:
            symbol: Trading symbol
            direction: "BUY" or "SELL"
            lot_size: Position size
            sl_price: Stop loss price
            tp_price: Take profit price
            comment: Order comment
            **kwargs: Additional arguments (plugin_id, entry_price, metadata) - ignored for backward compatibility
        
        Returns:
            MT5 ticket number or None
        """
        if not self._engine.trading_enabled:
            self._logger.warning("Trading is paused. Order rejected.")
            return None

        return self._mt5.place_order(
            symbol=symbol,
            order_type=direction.upper(),
            lot_size=lot_size,
            price=0.0,
            sl=sl_price,
            tp=tp_price,
            comment=f"{self._plugin_id}|{comment}" if comment else self._plugin_id
        )
    
    async def place_order_async(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        entry_price: float = 0.0,
        sl_price: float = 0.0,
        tp_price: float = 0.0,
        comment: str = "",
        metadata: Dict[str, Any] = None,
        plugin_id: str = None
    ) -> Dict[str, Any]:
        """
        Place a new order (async version for V3 plugin).
        
        Args:
            symbol: Trading symbol
            direction: "BUY" or "SELL"
            lot_size: Position size
            entry_price: Entry price (0 for market order)
            sl_price: Stop loss price
            tp_price: Take profit price
            comment: Order comment
            metadata: Additional order metadata
            plugin_id: Plugin ID (ignored - uses self._plugin_id)
        
        Returns:
            Dict with success status and trade_id or error
        """
        if not self._engine.trading_enabled:
            self._logger.warning("Trading is paused. Order rejected.")
            return {"success": False, "error": "Trading is paused"}

        try:
            ticket = self._mt5.place_order(
                symbol=symbol,
                order_type=direction.upper(),
                lot_size=lot_size,
                price=entry_price,
                sl=sl_price,
                tp=tp_price,
                comment=f"{self._plugin_id}|{comment}" if comment else self._plugin_id
            )
            
            if ticket:
                self._logger.info(f"[ServiceAPI] Order placed: {ticket} | {symbol} {direction} {lot_size}")
                return {"success": True, "trade_id": ticket}
            else:
                return {"success": False, "error": "Order placement failed"}
        except Exception as e:
            self._logger.error(f"[ServiceAPI] Order placement error: {e}")
            return {"success": False, "error": str(e)}
    
    async def place_dual_orders_v3(
        self,
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
        Place V3 hybrid SL dual order system (Order A + Order B).
        
        V3 uses DIFFERENT SL for each order:
        - Order A: Smart SL from Pine Script
        - Order B: Fixed $10 SL (different from Order A)
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            lot_size_total: Total lot size (split 50/50)
            order_a_sl: Smart SL price for Order A
            order_a_tp: TP2 (extended target) for Order A
            order_b_sl: Fixed $10 SL price for Order B
            order_b_tp: TP1 (closer target) for Order B
            logic_route: 'LOGIC1', 'LOGIC2', or 'LOGIC3'
        
        Returns:
            Tuple of (order_a_ticket, order_b_ticket)
        """
        if not self._engine.trading_enabled:
            self._logger.warning("Trading is paused. Dual orders rejected.")
            return (None, None)
        
        if self._order_service:
            return await self._order_service.place_dual_orders_v3(
                plugin_id=self._plugin_id,
                symbol=symbol,
                direction=direction,
                lot_size_total=lot_size_total,
                order_a_sl=order_a_sl,
                order_a_tp=order_a_tp,
                order_b_sl=order_b_sl,
                order_b_tp=order_b_tp,
                logic_route=logic_route
            )
        
        self._logger.warning("[ServiceAPI] OrderService not available, using fallback")
        return (None, None)
    
    async def place_dual_orders_v6(
        self,
        symbol: str,
        direction: str,
        lot_size_total: float,
        sl_price: float,
        tp1_price: float,
        tp2_price: float
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Place V6 dual orders (5M plugin).
        
        V6 dual orders use SAME SL for both orders:
        - Order A: Extended TP (TP2)
        - Order B: Quick TP (TP1)
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            lot_size_total: Total lot size (split 50/50)
            sl_price: Same SL for both orders
            tp1_price: Order B target (quick exit)
            tp2_price: Order A target (extended)
        
        Returns:
            Tuple of (order_a_ticket, order_b_ticket)
        """
        if not self._engine.trading_enabled:
            self._logger.warning("Trading is paused. V6 dual orders rejected.")
            return (None, None)
        
        if self._order_service:
            return await self._order_service.place_dual_orders_v6(
                plugin_id=self._plugin_id,
                symbol=symbol,
                direction=direction,
                lot_size_total=lot_size_total,
                sl_price=sl_price,
                tp1_price=tp1_price,
                tp2_price=tp2_price
            )
        
        return (None, None)
    
    async def place_single_order_a(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        comment: str = 'ORDER_A'
    ) -> Optional[int]:
        """
        Place Order A ONLY (for 15M/1H V6 plugins).
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            lot_size: Lot size
            sl_price: Stop loss price
            tp_price: Take profit price (TP2)
            comment: Order comment
        
        Returns:
            MT5 ticket number or None
        """
        if not self._engine.trading_enabled:
            return None
        
        if self._order_service:
            return await self._order_service.place_single_order_a(
                plugin_id=self._plugin_id,
                symbol=symbol,
                direction=direction,
                lot_size=lot_size,
                sl_price=sl_price,
                tp_price=tp_price,
                comment=comment
            )
        
        return self.place_order(symbol, direction, lot_size, sl_price, tp_price, comment)
    
    async def place_single_order_b(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_price: float,
        tp_price: float,
        comment: str = 'ORDER_B'
    ) -> Optional[int]:
        """
        Place Order B ONLY (for 1M V6 plugin - scalping).
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            lot_size: Lot size
            sl_price: Stop loss price
            tp_price: Take profit price (TP1 - quick exit)
            comment: Order comment
        
        Returns:
            MT5 ticket number or None
        """
        if not self._engine.trading_enabled:
            return None
        
        if self._order_service:
            return await self._order_service.place_single_order_b(
                plugin_id=self._plugin_id,
                symbol=symbol,
                direction=direction,
                lot_size=lot_size,
                sl_price=sl_price,
                tp_price=tp_price,
                comment=comment
            )
        
        return self.place_order(symbol, direction, lot_size, sl_price, tp_price, comment)

    def close_trade(self, trade_id: int) -> bool:
        """Close an existing trade (backward compatible)"""
        return self._mt5.close_position(trade_id)
    
    async def close_positions(self, symbol: str = None, direction: str = None) -> List[Dict[str, Any]]:
        """
        Close multiple positions based on filters.
        
        Args:
            symbol: Optional symbol filter
            direction: Optional direction filter ('buy' or 'sell')
        
        Returns:
            List of closed position results
        """
        results = []
        positions = self._mt5.get_positions()
        
        for pos in positions:
            if symbol and pos.get('symbol') != symbol:
                continue
            if direction and pos.get('type', '').lower() != direction.lower():
                continue
            
            result = self._mt5.close_position(pos.get('ticket'))
            results.append({
                'ticket': pos.get('ticket'),
                'symbol': pos.get('symbol'),
                'closed': result
            })
        
        return results
    
    async def close_positions_by_direction(
        self,
        symbol: str,
        direction: str,
        plugin_id: str = None
    ) -> Dict[str, Any]:
        """
        Close all positions for a symbol in a specific direction.
        
        Used by V3 plugin for aggressive reversal (close opposite positions).
        
        Args:
            symbol: Trading symbol
            direction: Direction to close ('buy' or 'sell')
            plugin_id: Plugin ID (ignored - uses self._plugin_id)
        
        Returns:
            Dict with closed positions count and details
        """
        try:
            results = await self.close_positions(symbol=symbol, direction=direction)
            closed_count = sum(1 for r in results if r.get('closed'))
            
            self._logger.info(
                f"[ServiceAPI] Closed {closed_count} {direction.upper()} positions for {symbol}"
            )
            
            return {
                "success": True,
                "closed_count": closed_count,
                "results": results
            }
        except Exception as e:
            self._logger.error(f"[ServiceAPI] close_positions_by_direction error: {e}")
            return {"success": False, "error": str(e), "closed_count": 0}
    
    async def close_position(self, order_id: int, reason: str = 'Manual') -> Dict[str, Any]:
        """
        Close entire position with tracking.
        
        Args:
            order_id: MT5 ticket number
            reason: Close reason for logging
        
        Returns:
            Dict with success status and profit info
        """
        if self._order_service:
            return await self._order_service.close_position(
                plugin_id=self._plugin_id,
                order_id=order_id,
                reason=reason
            )
        
        success = self.close_trade(order_id)
        return {"success": success, "order_id": order_id, "reason": reason}
    
    async def close_position_partial(self, order_id: int, percentage: float) -> Dict[str, Any]:
        """
        Close partial position (for TP1/TP2/TP3).
        
        Args:
            order_id: MT5 ticket number
            percentage: Percentage to close (25.0 = close 25%)
        
        Returns:
            Dict with closed volume and remaining info
        """
        if self._order_service:
            return await self._order_service.close_position_partial(
                plugin_id=self._plugin_id,
                order_id=order_id,
                percentage=percentage
            )
        
        return {"success": False, "error": "Service not available"}

    def modify_order(self, trade_id: int, sl: float = 0.0, tp: float = 0.0) -> bool:
        """Modify SL/TP of a trade (backward compatible)"""
        return self._mt5.modify_position(trade_id, sl, tp)
    
    async def modify_order_async(
        self,
        order_id: int,
        new_sl: float = None,
        new_tp: float = None
    ) -> bool:
        """
        Modify existing order SL/TP (async version).
        
        Args:
            order_id: MT5 ticket number
            new_sl: New stop loss price (None to keep current)
            new_tp: New take profit price (None to keep current)
        
        Returns:
            True if modification successful
        """
        if self._order_service:
            return await self._order_service.modify_order(
                plugin_id=self._plugin_id,
                order_id=order_id,
                new_sl=new_sl,
                new_tp=new_tp
            )
        
        return self.modify_order(order_id, new_sl or 0.0, new_tp or 0.0)
    
    def get_open_trades(self) -> List[Any]:
        """Get list of ALL open trades (backward compatible)"""
        return self._engine.get_open_trades()
    
    async def get_plugin_orders(self, symbol: str = None) -> List[Dict]:
        """
        Get all open orders for THIS plugin only.
        
        Args:
            symbol: Optional symbol filter
        
        Returns:
            List of open order dictionaries
        """
        if self._order_service:
            return await self._order_service.get_open_orders(
                plugin_id=self._plugin_id,
                symbol=symbol
            )
        
        return []

    # =========================================================================
    # RISK MANAGEMENT METHODS (RiskManagementService)
    # =========================================================================

    def calculate_lot_size(self, symbol: str = None, stop_loss_pips: float = 0.0, plugin_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Calculate recommended lot size (backward compatible).
        
        Args:
            symbol: Trading symbol
            stop_loss_pips: Stop loss in pips
            plugin_id: Plugin ID (ignored - uses self._plugin_id)
            **kwargs: Additional arguments (ignored for backward compatibility)
        
        Returns:
            Dict with lot_size or float for backward compatibility
        """
        balance = self.get_balance()
        if hasattr(self._risk, 'calculate_lot_size') and stop_loss_pips > 0:
            lot_size = self._risk.calculate_lot_size(balance, stop_loss_pips)
        else:
            lot_size = self._risk.get_fixed_lot_size(balance)
        
        return {"lot_size": lot_size, "balance": balance}
    
    async def calculate_sl_price(
        self,
        price: float,
        direction: str,
        lot_size: float,
        plugin_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate stop loss price based on risk parameters.
        
        Used by V3 plugin for fallback SL calculation when Pine SL is not provided.
        
        Args:
            price: Entry price
            direction: Trade direction ('buy' or 'sell')
            lot_size: Lot size
            plugin_id: Plugin ID (ignored - uses self._plugin_id)
            **kwargs: Additional arguments
        
        Returns:
            Dict with sl_price
        """
        try:
            risk_config = self._config.get('risk_config', {})
            default_sl_pips = risk_config.get('default_sl_pips', 50)
            
            point_value = 0.01 if price > 100 else 0.0001
            sl_distance = default_sl_pips * point_value
            
            if direction.lower() == 'buy':
                sl_price = price - sl_distance
            else:
                sl_price = price + sl_distance
            
            return {"sl_price": sl_price, "sl_pips": default_sl_pips}
        except Exception as e:
            self._logger.error(f"[ServiceAPI] calculate_sl_price error: {e}")
            if direction.lower() == 'buy':
                return {"sl_price": price * 0.99, "sl_pips": 0}
            else:
                return {"sl_price": price * 1.01, "sl_pips": 0}
    
    async def calculate_lot_size_async(
        self,
        symbol: str,
        risk_percentage: float,
        stop_loss_pips: float,
        account_balance: float = None
    ) -> float:
        """
        Calculate safe lot size based on risk parameters (async version).
        
        Args:
            symbol: Trading symbol
            risk_percentage: Risk per trade (e.g., 1.5 = 1.5%)
            stop_loss_pips: Stop loss distance in pips
            account_balance: Account balance (auto-fetch if None)
        
        Returns:
            Calculated lot size
        """
        if self._risk_service:
            return await self._risk_service.calculate_lot_size(
                plugin_id=self._plugin_id,
                symbol=symbol,
                risk_percentage=risk_percentage,
                stop_loss_pips=stop_loss_pips,
                account_balance=account_balance
            )
        
        return self.calculate_lot_size(symbol, stop_loss_pips)
    
    async def calculate_atr_sl(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        atr_value: float,
        atr_multiplier: float = 1.5
    ) -> float:
        """
        Calculate ATR-based dynamic stop loss price.
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            entry_price: Entry price
            atr_value: Current ATR value
            atr_multiplier: Multiplier for ATR (default 1.5)
        
        Returns:
            Calculated SL price
        """
        if self._risk_service:
            return await self._risk_service.calculate_atr_sl(
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                atr_value=atr_value,
                atr_multiplier=atr_multiplier
            )
        return 0.0
    
    async def calculate_atr_tp(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        atr_value: float,
        atr_multiplier: float = 2.0
    ) -> float:
        """
        Calculate ATR-based dynamic take profit price.
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            entry_price: Entry price
            atr_value: Current ATR value
            atr_multiplier: Multiplier for ATR (default 2.0)
        
        Returns:
            Calculated TP price
        """
        if self._risk_service:
            return await self._risk_service.calculate_atr_tp(
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                atr_value=atr_value,
                atr_multiplier=atr_multiplier
            )
        return 0.0
    
    async def check_daily_limit(self) -> Dict[str, Any]:
        """
        Check if daily loss limit reached.
        
        Returns:
            Dict with daily loss info and can_trade status
        """
        if self._risk_service:
            return await self._risk_service.check_daily_limit(self._plugin_id)
        return {"can_trade": True, "daily_loss": 0.0, "daily_limit": 0.0}
    
    async def check_risk_limits(self, symbol: str, lot_size: float, direction: str) -> Dict[str, Any]:
        """
        Check if trade meets all risk limits.
        
        Args:
            symbol: Trading symbol
            lot_size: Proposed lot size
            direction: Trade direction ('buy' or 'sell')
        
        Returns:
            Dict with allowed status and any limit violations
        """
        result = {
            'allowed': True,
            'violations': [],
            'daily_limit_ok': True,
            'lot_size_ok': True,
            'margin_ok': True
        }
        
        # Check daily limit
        daily_check = await self.check_daily_limit()
        if not daily_check.get('can_trade', True):
            result['allowed'] = False
            result['daily_limit_ok'] = False
            result['violations'].append('Daily loss limit exceeded')
        
        # Check lot size limits
        max_lot = self._config.get('risk_config', {}).get('max_lot_size', 10.0)
        if lot_size > max_lot:
            result['allowed'] = False
            result['lot_size_ok'] = False
            result['violations'].append(f'Lot size {lot_size} exceeds max {max_lot}')
        
        return result
    
    async def get_spread(self, symbol: str) -> float:
        """
        Get current spread for a symbol in pips.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Spread in pips
        """
        return await self.get_current_spread(symbol)
    
    async def get_atr(self, symbol: str, period: int = 14, timeframe: str = '1H') -> float:
        """
        Get ATR (Average True Range) for a symbol.
        
        Args:
            symbol: Trading symbol
            period: ATR period (default 14)
            timeframe: Timeframe for ATR calculation
        
        Returns:
            ATR value in price units
        """
        if self._market_service:
            return await self._market_service.get_atr(symbol, period, timeframe)
        
        # Fallback: estimate ATR based on symbol
        if symbol in ['XAUUSD', 'XAGUSD']:
            return 15.0  # Gold/Silver typical ATR
        return 0.0015  # Forex typical ATR
    
    def _validate_order_params(self, order_params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate order parameters before execution.
        
        Args:
            order_params: Order parameters dict
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['symbol', 'direction', 'lot_size']
        
        for field in required_fields:
            if field not in order_params:
                return False, f"Missing required field: {field}"
        
        # Validate direction
        direction = order_params.get('direction', '').upper()
        if direction not in ['BUY', 'SELL']:
            return False, f"Invalid direction: {direction}"
        
        # Validate lot size
        lot_size = order_params.get('lot_size', 0)
        if lot_size <= 0:
            return False, f"Invalid lot size: {lot_size}"
        
        max_lot = self._config.get('risk_config', {}).get('max_lot_size', 10.0)
        if lot_size > max_lot:
            return False, f"Lot size {lot_size} exceeds max {max_lot}"
        
        return True, ""
    
    async def check_lifetime_limit(self) -> Dict[str, Any]:
        """
        Check if lifetime loss limit reached.
        
        Returns:
            Dict with lifetime loss info and can_trade status
        """
        if self._risk_service:
            return await self._risk_service.check_lifetime_limit(self._plugin_id)
        return {"can_trade": True, "lifetime_loss": 0.0, "lifetime_limit": 0.0}
    
    async def validate_trade_risk(
        self,
        symbol: str,
        lot_size: float,
        sl_pips: float
    ) -> Dict[str, Any]:
        """
        Validate if a trade meets risk requirements.
        
        Args:
            symbol: Trading symbol
            lot_size: Proposed lot size
            sl_pips: Stop loss in pips
        
        Returns:
            Dict with validation result and details
        """
        if self._risk_service:
            return await self._risk_service.validate_trade_risk(
                plugin_id=self._plugin_id,
                symbol=symbol,
                lot_size=lot_size,
                sl_pips=sl_pips
            )
        return {"valid": True, "reason": "Validation skipped"}
    
    async def get_fixed_lot_size(self, account_balance: float = None) -> float:
        """
        Get fixed lot size based on account tier.
        
        Args:
            account_balance: Account balance (auto-fetch if None)
        
        Returns:
            Fixed lot size for current tier
        """
        if self._risk_service:
            return await self._risk_service.get_fixed_lot_size(
                plugin_id=self._plugin_id,
                account_balance=account_balance
            )
        return self._risk.get_fixed_lot_size(account_balance or self.get_balance())

    # =========================================================================
    # TREND MANAGEMENT METHODS (TrendManagementService)
    # =========================================================================
    
    async def get_timeframe_trend(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Get V3 4-pillar MTF trend for a specific timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe: '15m', '1h', '4h', '1d' ONLY
        
        Returns:
            Dict with trend direction and metadata
        """
        if self._trend_service:
            return await self._trend_service.get_timeframe_trend(symbol, timeframe)
        return {"direction": "neutral", "value": 0, "timeframe": timeframe}
    
    async def get_mtf_trends(self, symbol: str) -> Dict[str, int]:
        """
        Get ALL 4-pillar trends at once.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Dict with trend values for each timeframe
            {"15m": 1, "1h": 1, "4h": -1, "1d": 1}
        """
        if self._trend_service:
            return await self._trend_service.get_mtf_trends(symbol)
        return {"15m": 0, "1h": 0, "4h": 0, "1d": 0}
    
    async def validate_v3_trend_alignment(
        self,
        symbol: str,
        direction: str,
        min_aligned: int = 3
    ) -> bool:
        """
        Check if signal aligns with V3 4-pillar system.
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            min_aligned: Minimum pillars that must align (default 3/4)
        
        Returns:
            True if enough pillars align with direction
        """
        if self._trend_service:
            return await self._trend_service.validate_v3_trend_alignment(
                symbol=symbol,
                direction=direction,
                min_aligned=min_aligned
            )
        return True
    
    async def check_logic_alignment(
        self,
        symbol: str,
        logic: str,
        direction: str
    ) -> Dict[str, Any]:
        """
        Check if signal aligns with specific logic requirements.
        
        Args:
            symbol: Trading symbol
            logic: 'combinedlogic-1', 'combinedlogic-2', 'combinedlogic-3'
            direction: 'BUY' or 'SELL'
        
        Returns:
            Dict with alignment status and details
        """
        if self._trend_service:
            return await self._trend_service.check_logic_alignment(
                symbol=symbol,
                logic=logic,
                direction=direction
            )
        return {"aligned": True, "logic": logic}
    
    async def update_trend_pulse(
        self,
        symbol: str,
        timeframe: str,
        bull_count: int,
        bear_count: int,
        market_state: str,
        changes: str
    ) -> None:
        """
        Update market_trends table with Trend Pulse alert data (V6).
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe string
            bull_count: Number of bullish indicators
            bear_count: Number of bearish indicators
            market_state: Current market state string
            changes: Which timeframes changed
        """
        if self._trend_service:
            await self._trend_service.update_trend_pulse(
                symbol=symbol,
                timeframe=timeframe,
                bull_count=bull_count,
                bear_count=bear_count,
                market_state=market_state,
                changes=changes
            )
    
    async def get_market_state(self, symbol: str) -> str:
        """
        Get current market state for symbol (V6).
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Market state string: 'TRENDING_BULLISH', 'TRENDING_BEARISH', 'SIDEWAYS', etc.
        """
        if self._trend_service:
            return await self._trend_service.get_market_state(symbol)
        return "UNKNOWN"
    
    async def check_pulse_alignment(self, symbol: str, direction: str) -> bool:
        """
        Check if signal aligns with Trend Pulse counts (V6).
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
        
        Returns:
            True if pulse counts align with direction
        """
        if self._trend_service:
            return await self._trend_service.check_pulse_alignment(symbol, direction)
        return True
    
    async def get_pulse_data(self, symbol: str, timeframe: str = None) -> Dict[str, Dict[str, int]]:
        """
        Get raw Trend Pulse counts.
        
        Args:
            symbol: Trading symbol
            timeframe: Optional specific timeframe
        
        Returns:
            Dict with pulse data per timeframe
        """
        if self._trend_service:
            return await self._trend_service.get_pulse_data(symbol, timeframe)
        return {}
    
    async def check_higher_tf_trend(
        self,
        symbol: str,
        signal_tf: str,
        direction: str
    ) -> Dict[str, Any]:
        """
        Check if signal aligns with higher timeframe trend from database.
        
        V6 Timeframe Hierarchy:
        - 1M entry → Check 5M trend
        - 5M entry → Check 15M trend
        - 15M entry → Check 1H (60M) trend
        - 1H entry → Check 4H (240M) trend
        - 4H entry → No higher TF (approved by default)
        
        Args:
            symbol: Trading symbol (e.g., "XAUUSD")
            signal_tf: Signal timeframe ("1", "5", "15", "60", "240")
            direction: Trade direction ("BUY" or "SELL")
        
        Returns:
            Dict with:
                - aligned: bool - True if higher TF supports direction
                - higher_tf: str - The higher timeframe checked
                - bull_count: int - Bull count from higher TF
                - bear_count: int - Bear count from higher TF
                - reason: str - Explanation of result
        """
        HIGHER_TF_MAP = {
            "1": "5",
            "5": "15",
            "15": "60",
            "60": "240",
            "240": None
        }
        
        higher_tf = HIGHER_TF_MAP.get(signal_tf)
        
        if higher_tf is None:
            return {
                "aligned": True,
                "higher_tf": None,
                "bull_count": 0,
                "bear_count": 0,
                "reason": f"{signal_tf}m is highest TF - no higher TF check needed"
            }
        
        try:
            if hasattr(self._engine, 'trend_pulse_manager') and self._engine.trend_pulse_manager:
                pulse_data = await self._engine.trend_pulse_manager.get_pulse(symbol, higher_tf)
                
                if pulse_data is None:
                    return {
                        "aligned": True,
                        "higher_tf": higher_tf,
                        "bull_count": 0,
                        "bear_count": 0,
                        "reason": f"No {higher_tf}m trend data available - proceeding with caution"
                    }
                
                bull_count = pulse_data.bull_count
                bear_count = pulse_data.bear_count
                
                if direction.upper() == "BUY":
                    is_aligned = bull_count > bear_count
                    reason = f"{higher_tf}m trend: Bull={bull_count} > Bear={bear_count}" if is_aligned else f"{higher_tf}m trend: Bull={bull_count} <= Bear={bear_count}"
                else:
                    is_aligned = bear_count > bull_count
                    reason = f"{higher_tf}m trend: Bear={bear_count} > Bull={bull_count}" if is_aligned else f"{higher_tf}m trend: Bear={bear_count} <= Bull={bull_count}"
                
                self._logger.info(
                    f"[HIGHER_TF_CHECK] {symbol} {signal_tf}m {direction}: "
                    f"Checking {higher_tf}m - {reason} - {'ALIGNED' if is_aligned else 'MISALIGNED'}"
                )
                
                return {
                    "aligned": is_aligned,
                    "higher_tf": higher_tf,
                    "bull_count": bull_count,
                    "bear_count": bear_count,
                    "reason": reason
                }
            else:
                self._logger.warning("[HIGHER_TF_CHECK] TrendPulseManager not available")
                return {
                    "aligned": True,
                    "higher_tf": higher_tf,
                    "bull_count": 0,
                    "bear_count": 0,
                    "reason": "TrendPulseManager not initialized - proceeding with caution"
                }
                
        except Exception as e:
            self._logger.error(f"[HIGHER_TF_CHECK] Error: {e}")
            return {
                "aligned": True,
                "higher_tf": higher_tf,
                "bull_count": 0,
                "bear_count": 0,
                "reason": f"Error checking higher TF: {e}"
            }
    
    async def update_trend(
        self,
        symbol: str,
        timeframe: str,
        signal: str,
        mode: str = "AUTO"
    ) -> bool:
        """
        Update trend for a specific symbol and timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe string
            signal: 'bull', 'bear', 'buy', 'sell', etc.
            mode: 'AUTO' or 'MANUAL'
        
        Returns:
            True if update successful
        """
        if self._trend_service:
            return await self._trend_service.update_trend(symbol, timeframe, signal, mode)
        return True

    # =========================================================================
    # COMMUNICATION METHODS
    # =========================================================================

    def send_notification(self, message: str, plugin_id: str = None, priority: str = "normal", **kwargs):
        """
        Send message via Telegram (backward compatible).
        
        Args:
            message: Message to send
            plugin_id: Plugin ID (ignored - uses self._plugin_id)
            priority: Message priority (normal, high, low)
            **kwargs: Additional arguments (ignored for backward compatibility)
        """
        self._telegram.send_message(message)
    
    async def send_notification_async(
        self,
        message: str,
        plugin_id: str = None,
        priority: str = "normal",
        **kwargs
    ) -> bool:
        """
        Send message via Telegram (async version).
        
        Args:
            message: Message to send
            plugin_id: Plugin ID (ignored - uses self._plugin_id)
            priority: Message priority (normal, high, low)
            **kwargs: Additional arguments
        
        Returns:
            True if sent successfully
        """
        try:
            self._telegram.send_message(message)
            return True
        except Exception as e:
            self._logger.error(f"[ServiceAPI] Notification error: {e}")
            return False

    def log(self, message: str, level: str = "info"):
        """Log message with plugin context"""
        log_msg = f"[{self._plugin_id}] {message}"
        if level.lower() == "error":
            self._logger.error(log_msg)
        elif level.lower() == "warning":
            self._logger.warning(log_msg)
        elif level.lower() == "debug":
            self._logger.debug(log_msg)
        else:
            self._logger.info(log_msg)
    
    # =========================================================================
    # V6 NOTIFICATION METHODS (NEW - Telegram V5 Upgrade)
    # =========================================================================
    
    async def send_v6_entry_notification(
        self,
        timeframe: str,
        symbol: str,
        direction: str,
        entry_price: float,
        sl: float = None,
        tp: float = None,
        lot_size: float = None,
        pattern: str = None
    ) -> bool:
        """
        Send V6 entry notification with timeframe badge.
        
        Args:
            timeframe: Timeframe (15m, 30m, 1h, 4h)
            symbol: Trading symbol
            direction: BUY or SELL
            entry_price: Entry price
            sl: Stop loss price
            tp: Take profit price
            lot_size: Lot size
            pattern: Price action pattern name
        
        Returns:
            True if sent successfully
        """
        try:
            # Map timeframe to notification type
            tf_map = {
                "15m": "v6_entry_15m",
                "30m": "v6_entry_30m",
                "1h": "v6_entry_1h",
                "4h": "v6_entry_4h"
            }
            notification_type = tf_map.get(timeframe.lower(), "v6_entry_15m")
            
            data = {
                "timeframe": timeframe,
                "symbol": symbol,
                "direction": direction,
                "entry_price": entry_price,
                "sl": sl,
                "tp": tp,
                "lot_size": lot_size,
                "pattern": pattern
            }
            
            return await self.send_telegram_notification(notification_type, "", trade_data=data)
        except Exception as e:
            self._logger.error(f"[ServiceAPI] V6 entry notification error: {e}")
            return False
    
    async def send_v6_exit_notification(
        self,
        timeframe: str,
        symbol: str,
        direction: str,
        entry_price: float,
        exit_price: float,
        pnl: float,
        exit_reason: str,
        duration: str = None,
        pips: float = None
    ) -> bool:
        """
        Send V6 exit notification.
        
        Args:
            timeframe: Timeframe (15m, 30m, 1h, 4h)
            symbol: Trading symbol
            direction: BUY or SELL
            entry_price: Entry price
            exit_price: Exit price
            pnl: Profit/loss amount
            exit_reason: Reason for exit (TP, SL, Manual, etc.)
            duration: Trade duration
            pips: Pips gained/lost
        
        Returns:
            True if sent successfully
        """
        try:
            data = {
                "timeframe": timeframe,
                "symbol": symbol,
                "direction": direction,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl": pnl,
                "exit_reason": exit_reason,
                "duration": duration,
                "pips": pips
            }
            
            return await self.send_telegram_notification("v6_exit", "", trade_data=data)
        except Exception as e:
            self._logger.error(f"[ServiceAPI] V6 exit notification error: {e}")
            return False
    
    async def send_v6_tp_notification(
        self,
        timeframe: str,
        symbol: str,
        pnl: float,
        tp_level: int = 1,
        pips: float = None
    ) -> bool:
        """
        Send V6 take profit hit notification.
        
        Args:
            timeframe: Timeframe (15m, 30m, 1h, 4h)
            symbol: Trading symbol
            pnl: Profit amount
            tp_level: TP level (1, 2, 3)
            pips: Pips gained
        
        Returns:
            True if sent successfully
        """
        try:
            data = {
                "timeframe": timeframe,
                "symbol": symbol,
                "pnl": pnl,
                "tp_level": tp_level,
                "pips": pips
            }
            
            return await self.send_telegram_notification("v6_tp_hit", "", trade_data=data)
        except Exception as e:
            self._logger.error(f"[ServiceAPI] V6 TP notification error: {e}")
            return False
    
    async def send_v6_sl_notification(
        self,
        timeframe: str,
        symbol: str,
        pnl: float,
        pips: float = None
    ) -> bool:
        """
        Send V6 stop loss hit notification.
        
        Args:
            timeframe: Timeframe (15m, 30m, 1h, 4h)
            symbol: Trading symbol
            pnl: Loss amount (negative)
            pips: Pips lost
        
        Returns:
            True if sent successfully
        """
        try:
            data = {
                "timeframe": timeframe,
                "symbol": symbol,
                "pnl": pnl,
                "pips": pips
            }
            
            return await self.send_telegram_notification("v6_sl_hit", "", trade_data=data)
        except Exception as e:
            self._logger.error(f"[ServiceAPI] V6 SL notification error: {e}")
            return False
    
    async def send_v6_timeframe_toggle_notification(
        self,
        timeframe: str,
        enabled: bool
    ) -> bool:
        """
        Send V6 timeframe enabled/disabled notification.
        
        Args:
            timeframe: Timeframe (15m, 30m, 1h, 4h)
            enabled: True if enabled, False if disabled
        
        Returns:
            True if sent successfully
        """
        try:
            notification_type = "v6_timeframe_enabled" if enabled else "v6_timeframe_disabled"
            data = {
                "timeframe": timeframe,
                "enabled": enabled
            }
            
            return await self.send_telegram_notification(notification_type, "", trade_data=data)
        except Exception as e:
            self._logger.error(f"[ServiceAPI] V6 timeframe toggle notification error: {e}")
            return False
    
    async def send_v6_daily_summary(
        self,
        summary_data: Dict[str, Any]
    ) -> bool:
        """
        Send V6 daily summary notification.
        
        Args:
            summary_data: Dict with per-timeframe stats:
                - 15m: {trades, pnl, win_rate}
                - 30m: {trades, pnl, win_rate}
                - 1h: {trades, pnl, win_rate}
                - 4h: {trades, pnl, win_rate}
                - total_trades, total_pnl, total_win_rate
        
        Returns:
            True if sent successfully
        """
        try:
            return await self.send_telegram_notification("v6_daily_summary", "", trade_data=summary_data)
        except Exception as e:
            self._logger.error(f"[ServiceAPI] V6 daily summary notification error: {e}")
            return False
    
    async def send_v6_signal_notification(
        self,
        timeframe: str,
        symbol: str,
        direction: str,
        pattern: str,
        entry: float = None,
        sl: float = None,
        tp: float = None
    ) -> bool:
        """
        Send V6 signal received notification.
        
        Args:
            timeframe: Timeframe (15m, 30m, 1h, 4h)
            symbol: Trading symbol
            direction: BUY or SELL
            pattern: Price action pattern name
            entry: Suggested entry price
            sl: Suggested stop loss
            tp: Suggested take profit
        
        Returns:
            True if sent successfully
        """
        try:
            data = {
                "timeframe": timeframe,
                "symbol": symbol,
                "direction": direction,
                "pattern": pattern,
                "entry": entry,
                "sl": sl,
                "tp": tp
            }
            
            return await self.send_telegram_notification("v6_signal", "", trade_data=data)
        except Exception as e:
            self._logger.error(f"[ServiceAPI] V6 signal notification error: {e}")
            return False
    
    # =========================================================================
    # CONFIGURATION METHODS
    # =========================================================================
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value (backward compatible)"""
        return self._config.get(key, default)
    
    def get_plugin_config(self, key: str, default: Any = None) -> Any:
        """
        Get plugin-specific configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
        
        Returns:
            Configuration value
        """
        plugins_config = self._config.get("plugins", {})
        plugin_config = plugins_config.get(self._plugin_id, {})
        return plugin_config.get(key, default)


def create_service_api(trading_engine, plugin_id: str = "core") -> ServiceAPI:
    """
    Factory function to create a ServiceAPI instance.
    
    Args:
        trading_engine: The main TradingEngine instance
        plugin_id: Plugin identifier
    
    Returns:
        Configured ServiceAPI instance
    """
    return ServiceAPI(trading_engine, plugin_id)
