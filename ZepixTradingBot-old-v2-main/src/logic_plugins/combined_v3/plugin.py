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
from src.core.services.reentry_service import ReentryService
from src.core.services.dual_order_service import DualOrderService
from .signal_handlers import V3SignalHandlers
from .order_manager import V3OrderManager
from .trend_validator import V3TrendValidator

logger = logging.getLogger(__name__)


class CombinedV3Plugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor, IReentryCapable, IDualOrderCapable):
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
        
        # Re-entry system support (Plan 03)
        self._chain_levels: Dict[str, int] = {}  # trade_id -> chain_level
        self._reentry_service: Optional[ReentryService] = None
        
        # Dual order system support (Plan 04)
        self._dual_order_service: Optional[DualOrderService] = None
        self._active_orders: Dict[str, Dict[str, Any]] = {}  # order_id -> order_info
        
        self.logger.info(
            f"CombinedV3Plugin initialized | "
            f"Shadow Mode: {self.shadow_mode} | "
            f"12 signals ready | Re-entry enabled | Dual orders enabled"
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
        return result
    
    async def get_order_a_config(self, signal: Dict[str, Any]) -> OrderConfig:
        """
        Get Order A configuration (TP_TRAIL with V3 Smart SL).
        
        Order A characteristics:
        - Uses V3 Smart SL with progressive trailing
        - Trailing starts at 50% of SL in profit
        - Trails in 25% steps
        - Has TP target (2:1 RR)
        
        Args:
            signal: Trading signal
            
        Returns:
            OrderConfig for Order A
        """
        logic = signal.get('logic', 'LOGIC1')
        base_lot = self._get_base_lot(logic)
        smart_lot = self.get_smart_lot_size(base_lot)
        
        # V3 Smart SL configuration
        sl_pips = self._get_sl_pips(signal.get('symbol', 'EURUSD'), logic)
        tp_pips = sl_pips * 2  # 2:1 RR for Order A
        
        return OrderConfig(
            order_type=OrderType.ORDER_A,
            sl_type=SLType.V3_SMART_SL,
            lot_size=smart_lot,
            sl_pips=sl_pips,
            tp_pips=tp_pips,
            trailing_enabled=True,
            trailing_start_pips=sl_pips * 0.5,  # Start trailing at 50% of SL
            trailing_step_pips=sl_pips * 0.25,  # Trail in 25% steps
            plugin_id=self.plugin_id,
            metadata={
                'logic': logic,
                'original_sl': sl_pips
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
        Handle Order B closure - may trigger profit booking.
        
        Args:
            order_id: Order identifier
            reason: Close reason (SL_HIT, TP_HIT, PROFIT_BOOKED, etc.)
        """
        self.logger.info(f"Order B closed: {order_id}, reason: {reason}")
        
        order_info = self._active_orders.pop(order_id, None)
        if not order_info:
            return
        
        # Order B closure triggers profit booking chain (Plan 05)
        # For now, just log
        if reason == 'TP_HIT' or reason == 'PROFIT_BOOKED':
            self.logger.info(f"Order B profit booked: {order_id}")
    
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
        
        Args:
            event: ReentryEvent with recovery details
            
        Returns:
            bool: True if re-entry order executed successfully
        """
        self.logger.info(
            f"Recovery signal received for {event.trade_id} | "
            f"Type: {event.reentry_type.value} | Chain: {event.chain_level}"
        )
        
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
