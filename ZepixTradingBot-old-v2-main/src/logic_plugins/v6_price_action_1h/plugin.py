"""
V6 Price Action 1H Plugin - Swing Logic

1-Hour Swing Strategy:
- Swing trading for larger 100-200+ pip moves
- ORDER A ONLY (main order targeting TP3)
- Requires 4H alignment (must align with higher TF)
- Risk Multiplier: 0.6x (reduced due to wider stops)
- Longer hold times, fewer trades

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


class V6PriceAction1hPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    V6 1-Hour Swing Plugin
    
    Strategy Profile:
    - Type: Swing Trading
    - Goal: Capture larger 100-200+ pip moves
    - Risk Multiplier: 0.6x (reduced due to wider stops)
    - Order Routing: ORDER A ONLY
    
    Entry Filters:
    - 4H Alignment required (must align with higher TF)
    - Confidence >= 60 (standard threshold)
    - Trend Pulse alignment checked
    """
    
    TIMEFRAME = "60"
    ORDER_ROUTING = "ORDER_A_ONLY"
    RISK_MULTIPLIER = 0.6
    
    CONFIDENCE_THRESHOLD = 60
    REQUIRE_4H_ALIGNMENT = True
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        """Initialize the 1H Swing Plugin"""
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
            f"V6PriceAction1hPlugin initialized | "
            f"Shadow Mode: {self.shadow_mode} | "
            f"Order Routing: {self.ORDER_ROUTING}"
        )
    
    def _load_plugin_config(self):
        """Load plugin configuration"""
        config_paths = [
            os.path.join(os.path.dirname(__file__), "config.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "plugins", "price_action_1h_config.json")
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
        
        self.CONFIDENCE_THRESHOLD = entry_conditions.get("confidence_threshold", self.CONFIDENCE_THRESHOLD)
        self.REQUIRE_4H_ALIGNMENT = entry_conditions.get("require_4h_alignment", self.REQUIRE_4H_ALIGNMENT)
        self.RISK_MULTIPLIER = risk_mgmt.get("risk_multiplier", self.RISK_MULTIPLIER)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load plugin metadata"""
        return {
            "version": "1.0.0",
            "author": "Zepix Team",
            "description": "V6 1H Swing - ORDER A ONLY with 4H alignment",
            "timeframe": "1h",
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
        Process V6 1H entry signal.
        
        Flow:
        1. Parse alert to ZepixV6Alert
        2. Validate timeframe (must be "60")
        3. Check 4H alignment
        4. Calculate lot size (0.6x multiplier)
        5. Place ORDER A ONLY targeting TP3
        
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
            
            result = await self._place_order_a(v6_alert, lot_size)
            
            if result.get("status") == "success":
                self._stats["trades_placed"] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"[1H Entry Error] {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    async def process_exit_signal(self, alert) -> Dict[str, Any]:
        """
        Process V6 1H exit signal.
        
        1H exits are patient - close all positions for the symbol.
        
        Args:
            alert: Exit alert data
        
        Returns:
            dict: Exit execution result
        """
        try:
            v6_alert = self._parse_alert(alert)
            
            if v6_alert.tf != self.TIMEFRAME:
                return self._skip_result("wrong_timeframe", f"Expected {self.TIMEFRAME}, got {v6_alert.tf}")
            
            self.logger.info(f"[1H Exit] {v6_alert.type} | {v6_alert.ticker}")
            
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
            self.logger.error(f"[1H Exit Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_reversal_signal(self, alert) -> Dict[str, Any]:
        """
        Process V6 1H reversal signal.
        
        Args:
            alert: Reversal alert data
        
        Returns:
            dict: Reversal execution result
        """
        try:
            v6_alert = self._parse_alert(alert)
            
            if v6_alert.tf != self.TIMEFRAME:
                return self._skip_result("wrong_timeframe", f"Expected {self.TIMEFRAME}, got {v6_alert.tf}")
            
            self.logger.info(f"[1H Reversal] {v6_alert.type} | {v6_alert.ticker}")
            
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
            self.logger.error(f"[1H Reversal Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def _validate_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """
        Validate entry conditions for 1H swing.
        
        Filters:
        1. Confidence >= 60 (standard threshold)
        2. 4H Alignment required (must align with higher TF)
        
        Args:
            alert: ZepixV6Alert to validate
        
        Returns:
            dict: Validation result with reason if failed
        """
        if alert.conf_score < self.CONFIDENCE_THRESHOLD:
            self.logger.info(f"[1H Skip] Confidence {alert.conf_score} < {self.CONFIDENCE_THRESHOLD}")
            return {"valid": False, "reason": "confidence_low"}
        
        if self.REQUIRE_4H_ALIGNMENT:
            try:
                is_aligned = await self.service_api.check_timeframe_alignment(
                    symbol=alert.ticker,
                    direction=alert.direction,
                    higher_tf="240"
                )
                if not is_aligned:
                    self.logger.info(f"[1H Skip] 4H alignment failed for {alert.direction}")
                    return {"valid": False, "reason": "4h_alignment_failed"}
            except Exception as e:
                self.logger.debug(f"[1H] 4H alignment check skipped: {e}")
        
        self.logger.info(
            f"[1H Valid] Conf={alert.conf_score}, Direction={alert.direction}"
        )
        
        return {"valid": True, "reason": None}
    
    async def _calculate_lot_size(self, alert: ZepixV6Alert) -> float:
        """
        Calculate lot size for 1H swing.
        
        Uses 0.6x risk multiplier due to wider stops.
        
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
            max_lot = risk_mgmt.get("max_lot_size", 0.15)
            
            final_lot = min(final_lot, max_lot)
            
            self.logger.debug(f"[1H Lot] Base={base_lot:.2f}, Final={final_lot:.2f} (0.6x)")
            
            return final_lot
            
        except Exception as e:
            self.logger.error(f"[1H Lot Error] {e}")
            return 0.01
    
    async def _place_order_a(self, alert: ZepixV6Alert, lot_size: float) -> Dict[str, Any]:
        """
        Place ORDER A ONLY for 1H swing.
        
        Order A targets TP3 for larger swing moves.
        
        Args:
            alert: ZepixV6Alert with trade details
            lot_size: Calculated lot size
        
        Returns:
            dict: Order execution result
        """
        try:
            tp_target = alert.tp3 if alert.tp3 else alert.tp2
            
            ticket = await self.service_api.place_single_order_a(
                plugin_id=self.plugin_id,
                symbol=alert.ticker,
                direction=alert.direction,
                lot_size=lot_size,
                sl_price=alert.sl,
                tp_price=tp_target,
                comment=f"{self.plugin_id}_1h_swing"
            )
            
            self.logger.info(
                f"[1H ORDER A] #{ticket} | {alert.ticker} {alert.direction} | "
                f"Lot={lot_size:.2f} | SL={alert.sl} | TP3={tp_target}"
            )
            
            return {
                "status": "success",
                "action": "entry",
                "order_type": "ORDER_A_ONLY",
                "ticket": ticket,
                "symbol": alert.ticker,
                "direction": alert.direction,
                "lot_size": lot_size,
                "sl": alert.sl,
                "tp": tp_target
            }
            
        except Exception as e:
            self.logger.error(f"[1H Order Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def _process_shadow_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """Process entry in shadow mode"""
        self.logger.info(
            f"[1H SHADOW] Entry: {alert.type} | {alert.ticker} {alert.direction} | "
            f"Conf={alert.conf_score}"
        )
        
        return {
            "status": "shadow",
            "action": "entry",
            "order_type": "ORDER_A_ONLY",
            "symbol": alert.ticker,
            "direction": alert.direction,
            "confidence": alert.conf_score,
            "message": "Shadow mode - no real orders placed"
        }
    
    async def _process_shadow_exit(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """Process exit in shadow mode"""
        self.logger.info(f"[1H SHADOW] Exit: {alert.type} | {alert.ticker}")
        
        return {
            "status": "shadow",
            "action": "exit",
            "symbol": alert.ticker,
            "message": "Shadow mode - no real exits"
        }
    
    async def _process_shadow_reversal(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """Process reversal in shadow mode"""
        self.logger.info(f"[1H SHADOW] Reversal: {alert.type} | {alert.ticker}")
        
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
                "confidence_threshold": self.CONFIDENCE_THRESHOLD,
                "require_4h_alignment": self.REQUIRE_4H_ALIGNMENT
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
        return ['1h', '60']
    
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
            return await self._place_order_a(
                self._parse_alert(order_data),
                order_data.get('lot_size', 0.01)
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
