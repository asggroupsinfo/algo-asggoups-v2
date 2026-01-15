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
from .signal_handlers import V3SignalHandlers
from .order_manager import V3OrderManager
from .trend_validator import V3TrendValidator

logger = logging.getLogger(__name__)


class CombinedV3Plugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
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
        
        self.logger.info(
            f"CombinedV3Plugin initialized | "
            f"Shadow Mode: {self.shadow_mode} | "
            f"12 signals ready"
        )
    
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
