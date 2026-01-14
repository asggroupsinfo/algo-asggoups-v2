"""
V6 Price Action 1M Plugin - Scalping Logic

1-Minute Scalping Strategy:
- Ultra-fast scalping for quick 10-20 pip moves
- ORDER B ONLY (no main orders)
- Strict filters: ADX > 20, Confidence >= 80, Spread < 2 pips
- Risk Multiplier: 0.5x (half size due to noise)
- Trend Pulse: IGNORED (1m too fast for alignment)

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, Optional
import logging
import json
import os

from src.core.plugin_system.base_plugin import BaseLogicPlugin
from src.core.zepix_v6_alert import ZepixV6Alert, parse_v6_from_dict

logger = logging.getLogger(__name__)


class PriceAction1MPlugin(BaseLogicPlugin):
    """
    V6 1-Minute Scalping Plugin
    
    Strategy Profile:
    - Type: Hyper-Scalping
    - Goal: Capture quick 10-20 pip moves
    - Risk Multiplier: 0.5x
    - Order Routing: ORDER B ONLY
    
    Entry Filters:
    - ADX > 20 (avoid choppy markets)
    - Confidence >= 80 (high confidence required for 1m noise)
    - Spread < 2 pips (spread kills scalping profit)
    - Trend Pulse: IGNORED (1m too fast)
    """
    
    TIMEFRAME = "1"
    ORDER_ROUTING = "ORDER_B_ONLY"
    RISK_MULTIPLIER = 0.5
    
    ADX_THRESHOLD = 20
    CONFIDENCE_THRESHOLD = 80
    MAX_SPREAD_PIPS = 2.0
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        """Initialize the 1M Scalping Plugin"""
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
            f"PriceAction1MPlugin initialized | "
            f"Shadow Mode: {self.shadow_mode} | "
            f"Order Routing: {self.ORDER_ROUTING}"
        )
    
    def _load_plugin_config(self):
        """Load plugin configuration from config.json or config/plugins/"""
        config_paths = [
            os.path.join(os.path.dirname(__file__), "config.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "plugins", "price_action_1m_config.json")
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
        self.MAX_SPREAD_PIPS = entry_conditions.get("max_spread_pips", self.MAX_SPREAD_PIPS)
        self.RISK_MULTIPLIER = risk_mgmt.get("risk_multiplier", self.RISK_MULTIPLIER)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load plugin metadata"""
        return {
            "version": "1.0.0",
            "author": "Zepix Team",
            "description": "V6 1M Scalping - ORDER B ONLY with strict filters",
            "timeframe": "1m",
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
        Process V6 1M entry signal.
        
        Flow:
        1. Parse alert to ZepixV6Alert
        2. Validate timeframe (must be "1")
        3. Apply filters (ADX, Confidence, Spread)
        4. Calculate lot size (0.5x multiplier)
        5. Place ORDER B ONLY
        
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
            
            result = await self._place_order_b(v6_alert, lot_size)
            
            if result.get("status") == "success":
                self._stats["trades_placed"] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"[1M Entry Error] {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    async def process_exit_signal(self, alert) -> Dict[str, Any]:
        """
        Process V6 1M exit signal.
        
        1M exits are IMMEDIATE - close all positions fast.
        
        Args:
            alert: Exit alert data
        
        Returns:
            dict: Exit execution result
        """
        try:
            v6_alert = self._parse_alert(alert)
            
            if v6_alert.tf != self.TIMEFRAME:
                return self._skip_result("wrong_timeframe", f"Expected {self.TIMEFRAME}, got {v6_alert.tf}")
            
            self.logger.info(f"[1M Exit] {v6_alert.type} | {v6_alert.ticker}")
            
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
            self.logger.error(f"[1M Exit Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_reversal_signal(self, alert) -> Dict[str, Any]:
        """
        Process V6 1M reversal signal.
        
        For 1M scalping, reversals are rare but handled as:
        1. Close all opposite positions
        2. Enter new direction
        
        Args:
            alert: Reversal alert data
        
        Returns:
            dict: Reversal execution result
        """
        try:
            v6_alert = self._parse_alert(alert)
            
            if v6_alert.tf != self.TIMEFRAME:
                return self._skip_result("wrong_timeframe", f"Expected {self.TIMEFRAME}, got {v6_alert.tf}")
            
            self.logger.info(f"[1M Reversal] {v6_alert.type} | {v6_alert.ticker}")
            
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
            self.logger.error(f"[1M Reversal Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def _validate_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """
        Validate entry conditions for 1M scalping.
        
        Filters:
        1. ADX > 20 (avoid choppy markets)
        2. Confidence >= 80 (high confidence for 1m noise)
        3. Spread < 2 pips (spread kills scalping profit)
        
        Note: Trend Pulse is IGNORED for 1M (too fast)
        
        Args:
            alert: ZepixV6Alert to validate
        
        Returns:
            dict: Validation result with reason if failed
        """
        if alert.adx is None or alert.adx < self.ADX_THRESHOLD:
            adx_val = alert.adx if alert.adx is not None else "NA"
            self.logger.info(f"[1M Skip] ADX {adx_val} < {self.ADX_THRESHOLD} (choppy market)")
            return {"valid": False, "reason": "adx_low"}
        
        if alert.conf_score < self.CONFIDENCE_THRESHOLD:
            self.logger.info(f"[1M Skip] Confidence {alert.conf_score} < {self.CONFIDENCE_THRESHOLD}")
            return {"valid": False, "reason": "confidence_low"}
        
        try:
            spread = await self.service_api.get_current_spread(alert.ticker)
            if spread is not None and spread > self.MAX_SPREAD_PIPS:
                self.logger.info(f"[1M Skip] Spread {spread:.2f} > {self.MAX_SPREAD_PIPS} pips")
                return {"valid": False, "reason": "spread_high"}
        except Exception as e:
            self.logger.debug(f"[1M] Spread check skipped: {e}")
        
        self.logger.info(
            f"[1M Valid] ADX={alert.adx:.1f}, Conf={alert.conf_score}, "
            f"Direction={alert.direction}"
        )
        
        return {"valid": True, "reason": None}
    
    async def _calculate_lot_size(self, alert: ZepixV6Alert) -> float:
        """
        Calculate lot size for 1M scalping.
        
        Uses 0.5x risk multiplier due to 1M noise.
        
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
            max_lot = risk_mgmt.get("max_lot_size", 0.10)
            
            final_lot = min(final_lot, max_lot)
            
            self.logger.debug(f"[1M Lot] Base={base_lot:.2f}, Final={final_lot:.2f} (0.5x)")
            
            return final_lot
            
        except Exception as e:
            self.logger.error(f"[1M Lot Error] {e}")
            return 0.01
    
    async def _place_order_b(self, alert: ZepixV6Alert, lot_size: float) -> Dict[str, Any]:
        """
        Place ORDER B ONLY for 1M scalping.
        
        1M uses only Order B (quick exit order) targeting TP1.
        
        Args:
            alert: ZepixV6Alert with trade details
            lot_size: Calculated lot size
        
        Returns:
            dict: Order execution result
        """
        try:
            ticket = await self.service_api.place_single_order_b(
                plugin_id=self.plugin_id,
                symbol=alert.ticker,
                direction=alert.direction,
                lot_size=lot_size,
                sl_price=alert.sl,
                tp_price=alert.tp1,
                comment=f"{self.plugin_id}_1m_scalp"
            )
            
            self.logger.info(
                f"[1M ORDER B] #{ticket} | {alert.ticker} {alert.direction} | "
                f"Lot={lot_size:.2f} | SL={alert.sl} | TP1={alert.tp1}"
            )
            
            return {
                "status": "success",
                "action": "entry",
                "order_type": "ORDER_B_ONLY",
                "ticket": ticket,
                "symbol": alert.ticker,
                "direction": alert.direction,
                "lot_size": lot_size,
                "sl": alert.sl,
                "tp": alert.tp1
            }
            
        except Exception as e:
            self.logger.error(f"[1M Order Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def _process_shadow_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """Process entry in shadow mode (no real orders)"""
        self.logger.info(
            f"[1M SHADOW] Entry: {alert.type} | {alert.ticker} {alert.direction} | "
            f"ADX={alert.adx} | Conf={alert.conf_score}"
        )
        
        return {
            "status": "shadow",
            "action": "entry",
            "order_type": "ORDER_B_ONLY",
            "symbol": alert.ticker,
            "direction": alert.direction,
            "adx": alert.adx,
            "confidence": alert.conf_score,
            "message": "Shadow mode - no real orders placed"
        }
    
    async def _process_shadow_exit(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """Process exit in shadow mode"""
        self.logger.info(f"[1M SHADOW] Exit: {alert.type} | {alert.ticker}")
        
        return {
            "status": "shadow",
            "action": "exit",
            "symbol": alert.ticker,
            "message": "Shadow mode - no real exits"
        }
    
    async def _process_shadow_reversal(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """Process reversal in shadow mode"""
        self.logger.info(f"[1M SHADOW] Reversal: {alert.type} | {alert.ticker}")
        
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
                "max_spread_pips": self.MAX_SPREAD_PIPS
            },
            "stats": self._stats
        })
        return base_status
