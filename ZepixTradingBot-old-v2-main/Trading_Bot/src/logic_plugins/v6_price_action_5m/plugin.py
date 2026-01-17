"""
V6 Price Action 5M Plugin - Momentum Logic

5-Minute Momentum Strategy:
- Catch intraday breakouts and rapid moves
- DUAL ORDERS (Order A + Order B)
- Filters: ADX >= 25, Confidence >= 70, 15M Alignment
- Risk Multiplier: 1.0x (standard size)
- Requires 15M timeframe alignment

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, Optional, List
import logging
import json
import os

from src.core.plugin_system.base_plugin import BaseLogicPlugin
from src.core.plugin_system.plugin_interface import ISignalProcessor, IOrderExecutor
from src.core.zepix_v6_alert import ZepixV6Alert, parse_v6_from_dict

logger = logging.getLogger(__name__)


class V6PriceAction5mPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    V6 5-Minute Momentum Plugin
    
    Strategy Profile:
    - Type: Momentum Trading
    - Goal: Catch intraday breakouts and rapid moves
    - Risk Multiplier: 1.0x
    - Order Routing: DUAL ORDERS (Order A + Order B)
    
    Entry Filters:
    - ADX >= 25 (need proven momentum)
    - Confidence >= 70 (standard threshold)
    - 15M Alignment required (must align with immediate higher TF)
    - Trend Pulse alignment checked
    """
    
    TIMEFRAME = "5"
    ORDER_ROUTING = "DUAL_ORDERS"
    RISK_MULTIPLIER = 1.0
    
    ADX_THRESHOLD = 25
    CONFIDENCE_THRESHOLD = 70
    REQUIRE_15M_ALIGNMENT = True
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        """Initialize the 5M Momentum Plugin"""
        super().__init__(plugin_id, config, service_api)
        
        self._load_plugin_config()
        
        self.shadow_mode = self.plugin_config.get("shadow_mode", True)
        
        self._stats = {
            "signals_received": 0,
            "signals_filtered": 0,
            "trades_placed": 0,
            "trades_closed": 0,
            "filter_reasons": {}
        }
        
        self.logger.info(
            f"V6PriceAction5mPlugin initialized | "
            f"Shadow Mode: {self.shadow_mode} | "
            f"Order Routing: {self.ORDER_ROUTING}"
        )
    
    def _load_plugin_config(self):
        """Load plugin configuration"""
        config_paths = [
            os.path.join(os.path.dirname(__file__), "config.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "plugins", "price_action_5m_config.json")
        ]
        
        self.plugin_config = {}
        
        for config_path in config_paths:
            try:
                with open(config_path, 'r') as f:
                    self.plugin_config = json.load(f)
                    break
            except (FileNotFoundError, json.JSONDecodeError):
                continue
        
        if self.config:
            self.plugin_config.update(self.config)
        
        settings = self.plugin_config.get("settings", {})
        entry_conditions = settings.get("entry_conditions", {})
        risk_mgmt = settings.get("risk_management", {})
        
        self.ADX_THRESHOLD = entry_conditions.get("adx_threshold", self.ADX_THRESHOLD)
        self.CONFIDENCE_THRESHOLD = entry_conditions.get("confidence_threshold", self.CONFIDENCE_THRESHOLD)
        self.REQUIRE_15M_ALIGNMENT = entry_conditions.get("require_15m_alignment", self.REQUIRE_15M_ALIGNMENT)
        self.RISK_MULTIPLIER = risk_mgmt.get("risk_multiplier", self.RISK_MULTIPLIER)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load plugin metadata"""
        return {
            "version": "1.0.0",
            "author": "Zepix Team",
            "description": "V6 5M Momentum - DUAL ORDERS with 15M alignment",
            "timeframe": "5m",
            "order_routing": self.ORDER_ROUTING,
            "supported_signals": [
                "BULLISH_ENTRY",
                "BEARISH_ENTRY",
                "EXIT_BULLISH",
                "EXIT_BEARISH"
            ]
        }
    
    async def process_entry_signal(self, alert) -> Dict[str, Any]:
        """
        Process V6 5M entry signal.
        
        Flow:
        1. Parse alert to ZepixV6Alert
        2. Validate timeframe (must be "5")
        3. Apply filters (ADX, Confidence, 15M Alignment)
        4. Calculate lot size (1.0x multiplier)
        5. Place DUAL ORDERS (Order A + Order B)
        
        Args:
            alert: Alert data (dict or ZepixV6Alert)
        
        Returns:
            dict: Execution result
        """
        self._stats["signals_received"] += 1
        
        try:
            v6_alert = self._parse_alert(alert)
            
            if v6_alert.tf != self.TIMEFRAME:
                return self._skip_result("wrong_timeframe", f"Expected {self.TIMEFRAME}, got {v6_alert.tf}")
            
            validation = await self._validate_entry(v6_alert)
            if not validation["valid"]:
                self._stats["signals_filtered"] += 1
                reason = validation["reason"]
                self._stats["filter_reasons"][reason] = self._stats["filter_reasons"].get(reason, 0) + 1
                return self._skip_result("filter_failed", validation["reason"])
            
            if self.shadow_mode:
                return await self._process_shadow_entry(v6_alert)
            
            lot_size = await self._calculate_lot_size(v6_alert)
            
            result = await self._place_dual_orders(v6_alert, lot_size)
            
            if result.get("status") == "success":
                self._stats["trades_placed"] += 2
            
            return result
            
        except Exception as e:
            self.logger.error(f"[5M Entry Error] {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    async def process_exit_signal(self, alert) -> Dict[str, Any]:
        """
        Process V6 5M exit signal.
        
        5M exits close 80%, leave 20% runner if in profit.
        
        Args:
            alert: Exit alert data
        
        Returns:
            dict: Exit execution result
        """
        try:
            v6_alert = self._parse_alert(alert)
            
            if v6_alert.tf != self.TIMEFRAME:
                return self._skip_result("wrong_timeframe", f"Expected {self.TIMEFRAME}, got {v6_alert.tf}")
            
            self.logger.info(f"[5M Exit] {v6_alert.type} | {v6_alert.ticker}")
            
            if self.shadow_mode:
                return await self._process_shadow_exit(v6_alert)
            
            close_direction = "SELL" if "BULLISH" in v6_alert.type else "BUY"
            
            result = await self.service_api.close_positions_by_direction(
                plugin_id=self.plugin_id,
                symbol=v6_alert.ticker,
                direction=close_direction
            )
            
            self._stats["trades_closed"] += 1
            
            return {
                "status": "success",
                "action": "exit",
                "symbol": v6_alert.ticker,
                "closed_positions": result
            }
            
        except Exception as e:
            self.logger.error(f"[5M Exit Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_reversal_signal(self, alert) -> Dict[str, Any]:
        """
        Process V6 5M reversal signal.
        
        Args:
            alert: Reversal alert data
        
        Returns:
            dict: Reversal execution result
        """
        try:
            v6_alert = self._parse_alert(alert)
            
            if v6_alert.tf != self.TIMEFRAME:
                return self._skip_result("wrong_timeframe", f"Expected {self.TIMEFRAME}, got {v6_alert.tf}")
            
            self.logger.info(f"[5M Reversal] {v6_alert.type} | {v6_alert.ticker}")
            
            if self.shadow_mode:
                return await self._process_shadow_reversal(v6_alert)
            
            exit_result = await self.process_exit_signal(alert)
            entry_result = await self.process_entry_signal(alert)
            
            return {
                "status": "success",
                "action": "reversal",
                "exit_result": exit_result,
                "entry_result": entry_result
            }
            
        except Exception as e:
            self.logger.error(f"[5M Reversal Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def _validate_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """
        Validate entry conditions for 5M momentum.
        
        Filters:
        1. ADX >= 25 (need proven momentum)
        2. Confidence >= 70 (standard threshold)
        3. 15M Alignment (must align with immediate higher TF)
        
        Args:
            alert: ZepixV6Alert to validate
        
        Returns:
            dict: Validation result with reason if failed
        """
        if alert.adx is None or alert.adx < self.ADX_THRESHOLD:
            adx_val = alert.adx if alert.adx is not None else "NA"
            self.logger.info(f"[5M Skip] ADX {adx_val} < {self.ADX_THRESHOLD} (low momentum)")
            return {"valid": False, "reason": "adx_low"}
        
        if alert.conf_score < self.CONFIDENCE_THRESHOLD:
            self.logger.info(f"[5M Skip] Confidence {alert.conf_score} < {self.CONFIDENCE_THRESHOLD}")
            return {"valid": False, "reason": "confidence_low"}
        
        if self.REQUIRE_15M_ALIGNMENT:
            bull_count, bear_count = alert.get_pulse_counts()
            
            if alert.alignment == "0/0" or (bull_count == 0 and bear_count == 0):
                self.logger.warning(f"[5M] No MTF alignment data in payload, proceeding with caution")
            else:
                if alert.direction.upper() == "BUY":
                    is_aligned = bull_count >= 3
                else:
                    is_aligned = bear_count >= 3
                
                if not is_aligned:
                    self.logger.info(
                        f"[5M Skip] Payload alignment weak: {alert.alignment} "
                        f"(need 3+ for {alert.direction})"
                    )
                    return {"valid": False, "reason": "alignment_weak"}
                
                self.logger.debug(
                    f"[5M] Using payload alignment: {alert.alignment} "
                    f"(Bull={bull_count}, Bear={bear_count})"
                )
        
        self.logger.info(
            f"[5M Valid] ADX={alert.adx:.1f}, Conf={alert.conf_score}, "
            f"Direction={alert.direction}"
        )
        
        return {"valid": True, "reason": None}
    
    async def _calculate_lot_size(self, alert: ZepixV6Alert) -> float:
        """
        Calculate lot size for 5M momentum.
        
        Uses 1.0x risk multiplier (standard size).
        
        Args:
            alert: ZepixV6Alert with trade details
        
        Returns:
            float: Calculated lot size
        """
        try:
            base_lot = await self.service_api.calculate_lot_size_async(
                plugin_id=self.plugin_id,
                symbol=alert.ticker,
                sl_price=alert.sl,
                entry_price=alert.price
            )
            
            final_lot = base_lot * self.RISK_MULTIPLIER
            
            settings = self.plugin_config.get("settings", {})
            risk_mgmt = settings.get("risk_management", {})
            max_lot = risk_mgmt.get("max_lot_size", 0.20)
            
            final_lot = min(final_lot, max_lot)
            
            self.logger.debug(f"[5M Lot] Base={base_lot:.2f}, Final={final_lot:.2f}")
            
            return final_lot
            
        except Exception as e:
            self.logger.error(f"[5M Lot Error] {e}")
            return 0.02
    
    async def _place_dual_orders(self, alert: ZepixV6Alert, lot_size: float) -> Dict[str, Any]:
        """
        Place DUAL ORDERS for 5M momentum.
        
        Order A: Targets TP2 (larger move)
        Order B: Targets TP1 (quick profit)
        Both use same SL.
        
        Args:
            alert: ZepixV6Alert with trade details
            lot_size: Total lot size (split 50/50)
        
        Returns:
            dict: Order execution result
        """
        try:
            lot_a = lot_size * 0.5
            lot_b = lot_size * 0.5
            
            ticket_a = await self.service_api.place_single_order_a(
                plugin_id=self.plugin_id,
                symbol=alert.ticker,
                direction=alert.direction,
                lot_size=lot_a,
                sl_price=alert.sl,
                tp_price=alert.tp2,
                comment=f"{self.plugin_id}_5m_order_a"
            )
            
            ticket_b = await self.service_api.place_single_order_b(
                plugin_id=self.plugin_id,
                symbol=alert.ticker,
                direction=alert.direction,
                lot_size=lot_b,
                sl_price=alert.sl,
                tp_price=alert.tp1,
                comment=f"{self.plugin_id}_5m_order_b"
            )
            
            self.logger.info(
                f"[5M DUAL] A#{ticket_a} B#{ticket_b} | {alert.ticker} {alert.direction} | "
                f"Lot A={lot_a:.2f} B={lot_b:.2f} | SL={alert.sl}"
            )
            
            return {
                "status": "success",
                "action": "entry",
                "order_type": "DUAL_ORDERS",
                "ticket_a": ticket_a,
                "ticket_b": ticket_b,
                "symbol": alert.ticker,
                "direction": alert.direction,
                "lot_a": lot_a,
                "lot_b": lot_b,
                "sl": alert.sl,
                "tp_a": alert.tp2,
                "tp_b": alert.tp1
            }
            
        except Exception as e:
            self.logger.error(f"[5M Order Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def _process_shadow_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """Process entry in shadow mode"""
        self.logger.info(
            f"[5M SHADOW] Entry: {alert.type} | {alert.ticker} {alert.direction} | "
            f"ADX={alert.adx} | Conf={alert.conf_score}"
        )
        
        return {
            "status": "shadow",
            "action": "entry",
            "order_type": "DUAL_ORDERS",
            "symbol": alert.ticker,
            "direction": alert.direction,
            "adx": alert.adx,
            "confidence": alert.conf_score,
            "message": "Shadow mode - no real orders placed"
        }
    
    async def _process_shadow_exit(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """Process exit in shadow mode"""
        self.logger.info(f"[5M SHADOW] Exit: {alert.type} | {alert.ticker}")
        
        return {
            "status": "shadow",
            "action": "exit",
            "symbol": alert.ticker,
            "message": "Shadow mode - no real exits"
        }
    
    async def _process_shadow_reversal(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """Process reversal in shadow mode"""
        self.logger.info(f"[5M SHADOW] Reversal: {alert.type} | {alert.ticker}")
        
        return {
            "status": "shadow",
            "action": "reversal",
            "symbol": alert.ticker,
            "message": "Shadow mode - no real reversals"
        }
    
    def _parse_alert(self, alert) -> ZepixV6Alert:
        """Parse alert to ZepixV6Alert"""
        if isinstance(alert, ZepixV6Alert):
            return alert
        if isinstance(alert, dict):
            return parse_v6_from_dict(alert)
        raise ValueError(f"Unknown alert type: {type(alert)}")
    
    def _skip_result(self, reason: str, message: str) -> Dict[str, Any]:
        """Create skip result"""
        return {
            "status": "skipped",
            "reason": reason,
            "message": message
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status"""
        base_status = super().get_status()
        base_status.update({
            "shadow_mode": self.shadow_mode,
            "timeframe": self.TIMEFRAME,
            "order_routing": self.ORDER_ROUTING,
            "risk_multiplier": self.RISK_MULTIPLIER,
            "filters": {
                "adx_threshold": self.ADX_THRESHOLD,
                "confidence_threshold": self.CONFIDENCE_THRESHOLD,
                "require_15m_alignment": self.REQUIRE_15M_ALIGNMENT
            },
            "stats": self._stats
        })
        return base_status

    # ========== ISignalProcessor Interface Implementation ==========
    
    def get_supported_strategies(self) -> List[str]:
        """Return list of strategy names this plugin supports."""
        return ['V6_PRICE_ACTION', 'PRICE_ACTION', 'V6']
    
    def get_supported_timeframes(self) -> List[str]:
        """Return list of timeframes this plugin supports."""
        return ['5m', '5']
    
    async def can_process_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Check if this plugin can process the given signal."""
        strategy = signal_data.get('strategy', '')
        timeframe = signal_data.get('timeframe', signal_data.get('tf', ''))
        
        if strategy in self.get_supported_strategies():
            if timeframe in self.get_supported_timeframes():
                return True
        return False
    
    async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process the signal and return result."""
        alert_type = signal_data.get('type', '')
        
        if 'entry' in alert_type.lower():
            return await self.process_entry_signal(signal_data)
        elif 'exit' in alert_type.lower():
            return await self.process_exit_signal(signal_data)
        elif 'reversal' in alert_type.lower():
            return await self.process_reversal_signal(signal_data)
        else:
            return await self.process_entry_signal(signal_data)

    # ========== IOrderExecutor Interface Implementation ==========
    
    async def execute_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an order and return result."""
        try:
            return await self._place_dual_orders(
                self._parse_alert(order_data),
                order_data.get('lot_size', 0.02)
            )
        except Exception as e:
            self.logger.error(f"Order execution failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> bool:
        """Modify an existing order."""
        try:
            return await self.service_api.modify_order(order_id, modifications)
        except Exception as e:
            self.logger.error(f"Order modification failed: {e}")
            return False
    
    async def close_order(self, order_id: str, reason: str) -> bool:
        """Close an existing order."""
        try:
            return await self.service_api.close_order(order_id, reason)
        except Exception as e:
            self.logger.error(f"Order close failed: {e}")
            return False
