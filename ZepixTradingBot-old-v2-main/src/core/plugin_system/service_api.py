"""
ServiceAPI - Unified Service Layer for V5 Hybrid Plugin Architecture

This module provides a unified facade over all core services, allowing plugins
to access bot functionality through a single, controlled interface.

The ServiceAPI is the SINGLE point of entry for plugins. Plugins should ONLY
talk to ServiceAPI, never directly to MT5, RiskManager, or other managers.

Version: 2.0.0 (Batch 07 - Full Service Integration)
Date: 2026-01-14

Services Integrated:
- OrderExecutionService: V3 dual orders, V6 conditional orders
- RiskManagementService: Lot size calculation, ATR-based SL/TP, daily limits
- TrendManagementService: V3 4-pillar trends, V6 Trend Pulse
- MarketDataService: Spread checks, price data, volatility analysis
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


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
        api = ServiceAPI(trading_engine, plugin_id="combined_v3")
        lot = await api.calculate_lot_size(symbol="XAUUSD", risk_pct=1.5, sl_pips=50)
        
        # For core bot (backward compatible)
        api = ServiceAPI(trading_engine)
        price = api.get_price("XAUUSD")
    """
    
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
        self._mt5 = trading_engine.mt5_client
        self._risk = trading_engine.risk_manager
        self._telegram = trading_engine.telegram_bot
        self._logger = logger
        
        self._order_service = None
        self._risk_service = None
        self._trend_service = None
        self._market_service = None
        
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
                   comment: str = "") -> Optional[int]:
        """
        Place a new order (backward compatible).
        
        Args:
            symbol: Trading symbol
            direction: "BUY" or "SELL"
            lot_size: Position size
            sl_price: Stop loss price
            tp_price: Take profit price
            comment: Order comment
        
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

    def calculate_lot_size(self, symbol: str, stop_loss_pips: float = 0.0) -> float:
        """
        Calculate recommended lot size (backward compatible).
        
        Args:
            symbol: Trading symbol
            stop_loss_pips: Stop loss in pips
        
        Returns:
            Calculated lot size
        """
        balance = self.get_balance()
        if hasattr(self._risk, 'calculate_lot_size') and stop_loss_pips > 0:
            return self._risk.calculate_lot_size(balance, stop_loss_pips)
        return self._risk.get_fixed_lot_size(balance)
    
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

    def send_notification(self, message: str):
        """Send message via Telegram (backward compatible)"""
        self._telegram.send_message(message)

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
