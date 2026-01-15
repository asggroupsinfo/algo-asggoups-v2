"""
V3 Signal Handlers - Handles all 12 V3 signal types

Signal Types:
- Entry (7): Institutional_Launchpad, Liquidity_Trap, Momentum_Breakout,
             Mitigation_Test, Golden_Pocket_Flip, Screener_Full_Bullish/Bearish
- Exit (2): Bullish_Exit, Bearish_Exit
- Info (2): Volatility_Squeeze, Trend_Pulse
- Bonus (1): Sideways_Breakout

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from .plugin import CombinedV3Plugin

logger = logging.getLogger(__name__)


class V3SignalHandlers:
    """
    Handles all 12 V3 signal types with appropriate routing and processing.
    
    Signal Handler Map:
    - Institutional_Launchpad -> handle_institutional_launchpad
    - Liquidity_Trap -> handle_liquidity_trap
    - Momentum_Breakout -> handle_momentum_breakout
    - Mitigation_Test -> handle_mitigation_test
    - Golden_Pocket_Flip -> handle_golden_pocket_flip
    - Volatility_Squeeze -> handle_volatility_squeeze (info only)
    - Bullish_Exit -> handle_bullish_exit
    - Bearish_Exit -> handle_bearish_exit
    - Screener_Full_Bullish -> handle_screener_full
    - Screener_Full_Bearish -> handle_screener_full
    - Trend_Pulse -> handle_trend_pulse (DB update)
    - Sideways_Breakout -> handle_sideways_breakout (bonus)
    """
    
    def __init__(self, plugin: 'CombinedV3Plugin'):
        """
        Initialize signal handlers.
        
        Args:
            plugin: Parent CombinedV3Plugin instance
        """
        self.plugin = plugin
        self.service_api = plugin.service_api
        self.logger = logging.getLogger(f"plugin.{plugin.plugin_id}.signals")
        
        self.handler_map = {
            'Institutional_Launchpad': self.handle_institutional_launchpad,
            'Liquidity_Trap': self.handle_liquidity_trap,
            'Liquidity_Trap_Reversal': self.handle_liquidity_trap,
            'Momentum_Breakout': self.handle_momentum_breakout,
            'Momentum_Ignition': self.handle_momentum_breakout,
            'Mitigation_Test': self.handle_mitigation_test,
            'Mitigation_Block': self.handle_mitigation_test,
            'Golden_Pocket_Flip': self.handle_golden_pocket_flip,
            'Volatility_Squeeze': self.handle_volatility_squeeze,
            'Bullish_Exit': self.handle_bullish_exit,
            'Bearish_Exit': self.handle_bearish_exit,
            'Screener_Full_Bullish': self.handle_screener_full,
            'Screener_Full_Bearish': self.handle_screener_full,
            'Trend_Pulse': self.handle_trend_pulse,
            'Sideways_Breakout': self.handle_sideways_breakout
        }
    
    async def route_signal(self, alert) -> Optional[Dict[str, Any]]:
        """
        Route signal to appropriate handler based on signal_type.
        
        Args:
            alert: Alert data (ZepixV3Alert or dict)
            
        Returns:
            dict: Handler result or None if no handler found
        """
        signal_type = self._get_signal_type(alert)
        
        handler = self.handler_map.get(signal_type)
        if handler:
            return await handler(alert)
        
        self.logger.warning(f"Unknown V3 signal type: {signal_type}")
        return None
    
    async def handle_institutional_launchpad(self, alert) -> Dict[str, Any]:
        """
        Signal 1: Institutional Launchpad Entry
        
        High-probability entry based on institutional order flow.
        Routes based on timeframe (5m->LOGIC1, 15m->LOGIC2, etc.)
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_symbol(alert)
        direction = self._get_direction(alert)
        
        self.logger.info(
            f"Signal 1: Institutional Launchpad | {symbol} {direction}"
        )
        
        return await self._process_entry_signal(alert, signal_type='inst_launchpad')
    
    async def handle_liquidity_trap(self, alert) -> Dict[str, Any]:
        """
        Signal 2: Liquidity Trap Entry
        
        Entry after liquidity sweep (stop hunt reversal).
        Can trigger aggressive reversal if consensus >= 7.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_symbol(alert)
        direction = self._get_direction(alert)
        
        self.logger.info(
            f"Signal 2: Liquidity Trap | {symbol} {direction}"
        )
        
        return await self._process_entry_signal(alert, signal_type='liq_trap')
    
    async def handle_momentum_breakout(self, alert) -> Dict[str, Any]:
        """
        Signal 3: Momentum Breakout Entry
        
        Entry on strong momentum breakout with volume confirmation.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_symbol(alert)
        direction = self._get_direction(alert)
        
        self.logger.info(
            f"Signal 3: Momentum Breakout | {symbol} {direction}"
        )
        
        return await self._process_entry_signal(alert, signal_type='momentum')
    
    async def handle_mitigation_test(self, alert) -> Dict[str, Any]:
        """
        Signal 4: Mitigation Test Entry
        
        Entry on order block mitigation test.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_symbol(alert)
        direction = self._get_direction(alert)
        
        self.logger.info(
            f"Signal 4: Mitigation Test | {symbol} {direction}"
        )
        
        return await self._process_entry_signal(alert, signal_type='mitigation')
    
    async def handle_golden_pocket_flip(self, alert) -> Dict[str, Any]:
        """
        Signal 5: Golden Pocket Flip Entry
        
        Entry on Fibonacci golden pocket (0.618-0.786) flip.
        Routes to LOGIC3 for 1H/4H timeframes (signal override).
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_symbol(alert)
        direction = self._get_direction(alert)
        tf = self._get_timeframe(alert)
        
        self.logger.info(
            f"Signal 5: Golden Pocket Flip | {symbol} {direction} | TF: {tf}m"
        )
        
        return await self._process_entry_signal(alert, signal_type='golden_pocket')
    
    async def handle_volatility_squeeze(self, alert) -> Dict[str, Any]:
        """
        Signal 6: Volatility Squeeze (Info Only)
        
        Notification signal - no trade placement.
        Indicates upcoming volatility expansion.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Info result (no trade)
        """
        symbol = self._get_symbol(alert)
        tf = self._get_timeframe(alert)
        
        self.logger.info(
            f"Signal 6: Volatility Squeeze | {symbol} | TF: {tf}m"
        )
        
        try:
            await self.service_api.send_notification(
                plugin_id=self.plugin.plugin_id,
                message=(
                    f"Volatility Squeeze Detected\n"
                    f"Symbol: {symbol}\n"
                    f"Timeframe: {tf}m\n"
                    f"Big move expected - prepare for breakout!"
                ),
                priority="medium"
            )
        except Exception as e:
            self.logger.warning(f"Failed to send squeeze notification: {e}")
        
        return {
            "status": "info",
            "action": "notification",
            "signal_type": "Volatility_Squeeze",
            "symbol": symbol,
            "message": "Squeeze alert sent - no trade placed"
        }
    
    async def handle_bullish_exit(self, alert) -> Dict[str, Any]:
        """
        Signal 7: Bullish Exit
        
        Close all SELL positions on the symbol.
        Conservative exit - close only, no reverse.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Exit result
        """
        symbol = self._get_symbol(alert)
        
        self.logger.info(f"Signal 7: Bullish Exit | {symbol} | Closing SELL positions")
        
        return await self._process_exit_signal(alert, close_direction="SELL")
    
    async def handle_bearish_exit(self, alert) -> Dict[str, Any]:
        """
        Signal 8: Bearish Exit
        
        Close all BUY positions on the symbol.
        Conservative exit - close only, no reverse.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Exit result
        """
        symbol = self._get_symbol(alert)
        
        self.logger.info(f"Signal 8: Bearish Exit | {symbol} | Closing BUY positions")
        
        return await self._process_exit_signal(alert, close_direction="BUY")
    
    async def handle_screener_full(self, alert) -> Dict[str, Any]:
        """
        Signal 9/10: Screener Full Bullish/Bearish
        
        Full screener alignment signal.
        ALWAYS routes to LOGIC3 (signal override).
        Can trigger aggressive reversal.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Entry result
        """
        signal_type = self._get_signal_type(alert)
        symbol = self._get_symbol(alert)
        direction = self._get_direction(alert)
        
        self.logger.info(
            f"Signal 9/10: {signal_type} | {symbol} {direction} | Route: LOGIC3"
        )
        
        return await self._process_entry_signal(alert, signal_type='screener_full')
    
    async def handle_trend_pulse(self, alert) -> Dict[str, Any]:
        """
        Signal 11: Trend Pulse (DB Update)
        
        Updates MTF trend database with current trend state.
        No trade placement - info signal only.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Update result
        """
        symbol = self._get_symbol(alert)
        
        changed_timeframes = ""
        if hasattr(alert, 'changed_timeframes'):
            changed_timeframes = alert.changed_timeframes
        elif isinstance(alert, dict):
            changed_timeframes = alert.get('changed_timeframes', '')
        
        self.logger.info(
            f"Signal 11: Trend Pulse | {symbol} | Changes: {changed_timeframes}"
        )
        
        try:
            await self.plugin.trend_validator.update_trend_database(alert)
            
            return {
                "status": "success",
                "action": "db_update",
                "signal_type": "Trend_Pulse",
                "symbol": symbol,
                "changed_timeframes": changed_timeframes,
                "message": "MTF trends updated"
            }
        except Exception as e:
            self.logger.error(f"Trend Pulse update error: {e}")
            return {
                "status": "error",
                "signal_type": "Trend_Pulse",
                "message": str(e)
            }
    
    async def handle_sideways_breakout(self, alert) -> Dict[str, Any]:
        """
        Signal 12: Sideways Breakout (BONUS)
        
        Entry on breakout from sideways consolidation.
        Standard routing based on timeframe.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Entry result
        """
        symbol = self._get_symbol(alert)
        direction = self._get_direction(alert)
        
        self.logger.info(
            f"Signal 12: Sideways Breakout | {symbol} {direction}"
        )
        
        return await self._process_entry_signal(alert, signal_type='sideways_breakout')
    
    async def handle_exit_signal(self, alert) -> Dict[str, Any]:
        """
        Generic exit signal handler.
        
        Routes to appropriate exit handler based on signal_type.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Exit result
        """
        signal_type = self._get_signal_type(alert)
        
        if signal_type == "Bullish_Exit":
            return await self.handle_bullish_exit(alert)
        elif signal_type == "Bearish_Exit":
            return await self.handle_bearish_exit(alert)
        else:
            self.logger.warning(f"Unknown exit signal type: {signal_type}")
            return {"status": "error", "message": f"Unknown exit type: {signal_type}"}
    
    async def handle_reversal_signal(self, alert) -> Dict[str, Any]:
        """
        Generic reversal signal handler.
        
        Closes conflicting positions then enters opposite direction.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Reversal result
        """
        symbol = self._get_symbol(alert)
        direction = self._get_direction(alert)
        
        close_direction = "SELL" if direction == "buy" else "BUY"
        
        self.logger.info(
            f"Reversal: Closing {close_direction} positions on {symbol}"
        )
        
        exit_result = await self._process_exit_signal(alert, close_direction=close_direction)
        
        entry_result = await self._process_entry_signal(alert, signal_type='reversal')
        
        return {
            "status": "success",
            "action": "reversal",
            "exit_result": exit_result,
            "entry_result": entry_result
        }
    
    async def _process_entry_signal(self, alert, signal_type: str) -> Dict[str, Any]:
        """
        Common entry processing pipeline.
        
        Args:
            alert: Alert data
            signal_type: Type of signal for logging
            
        Returns:
            dict: Entry result
        """
        return await self.plugin.order_manager.place_v3_dual_orders(
            alert=alert,
            logic_route=self.plugin._route_to_logic(alert),
            logic_multiplier=self.plugin._get_logic_multiplier(
                self.plugin._route_to_logic(alert)
            )
        )
    
    async def _process_exit_signal(self, alert, close_direction: str) -> Dict[str, Any]:
        """
        Common exit processing pipeline.
        
        Args:
            alert: Alert data
            close_direction: Direction to close (BUY or SELL)
            
        Returns:
            dict: Exit result
        """
        symbol = self._get_symbol(alert)
        
        try:
            positions = await self.service_api.get_plugin_orders(
                plugin_id=self.plugin.plugin_id,
                symbol=symbol
            )
            
            positions_to_close = [
                p for p in positions
                if p.get('direction', '').upper() == close_direction
            ]
            
            if not positions_to_close:
                self.logger.info(f"No {close_direction} positions to close on {symbol}")
                return {
                    "status": "no_action",
                    "message": f"No {close_direction} positions open"
                }
            
            closed_count = 0
            for position in positions_to_close:
                try:
                    result = await self.service_api.close_position(
                        plugin_id=self.plugin.plugin_id,
                        ticket=position.get('ticket')
                    )
                    if result.get('success'):
                        closed_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to close position: {e}")
            
            return {
                "status": "success",
                "action": "exit",
                "closed_count": closed_count,
                "close_direction": close_direction,
                "symbol": symbol
            }
            
        except Exception as e:
            self.logger.error(f"Exit processing error: {e}")
            return {"status": "error", "message": str(e)}
    
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
