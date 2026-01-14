"""
V6 Price Action 15M Plugin - Intraday Logic

15-Minute Intraday Strategy:
- Core intraday trading for 50-100 pip moves
- ORDER A ONLY (main order targeting TP2)
- Requires Market State check (avoid CHOPPY/SIDEWAYS)
- Requires Trend Pulse alignment
- Risk Multiplier: 1.0x (standard size)

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


class PriceAction15MPlugin(BaseLogicPlugin):
    """
    V6 15-Minute Intraday Plugin
    
    Strategy Profile:
    - Type: Intraday Trading
    - Goal: Capture 50-100 pip intraday moves
    - Risk Multiplier: 1.0x
    - Order Routing: ORDER A ONLY
    
    Entry Filters:
    - Market State check (avoid CHOPPY/SIDEWAYS)
    - Trend Pulse alignment required
    - Confidence >= 60 (standard threshold)
    """
    
    TIMEFRAME = "15"
    ORDER_ROUTING = "ORDER_A_ONLY"
    RISK_MULTIPLIER = 1.0
    
    CONFIDENCE_THRESHOLD = 60
    REQUIRE_PULSE_ALIGNMENT = True
    AVOID_MARKET_STATES = ["CHOPPY", "SIDEWAYS"]
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        """Initialize the 15M Intraday Plugin"""
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
            f"PriceAction15MPlugin initialized | "
            f"Shadow Mode: {self.shadow_mode} | "
            f"Order Routing: {self.ORDER_ROUTING}"
        )
    
    def _load_plugin_config(self):
        """Load plugin configuration"""
        config_paths = [
            os.path.join(os.path.dirname(__file__), "config.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "plugins", "price_action_15m_config.json")
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
        self.REQUIRE_PULSE_ALIGNMENT = entry_conditions.get("require_pulse_alignment", self.REQUIRE_PULSE_ALIGNMENT)
        self.RISK_MULTIPLIER = risk_mgmt.get("risk_multiplier", self.RISK_MULTIPLIER)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load plugin metadata"""
        return {
            "version": "1.0.0",
            "author": "Zepix Team",
            "description": "V6 15M Intraday - ORDER A ONLY with Pulse alignment",
            "timeframe": "15m",
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
        Process V6 15M entry signal.
        
        Flow:
        1. Parse alert to ZepixV6Alert
        2. Validate timeframe (must be "15")
        3. Check Market State (avoid CHOPPY/SIDEWAYS)
        4. Check Trend Pulse alignment
        5. Calculate lot size (1.0x multiplier)
        6. Place ORDER A ONLY
        
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
            self.logger.error(f"[15M Entry Error] {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    async def process_exit_signal(self, alert) -> Dict[str, Any]:
        """
        Process V6 15M exit signal.
        
        15M exits close all positions for the symbol.
        
        Args:
            alert: Exit alert data
        
        Returns:
            dict: Exit execution result
        """
        try:
            v6_alert = self._parse_alert(alert)
            
            if v6_alert.tf != self.TIMEFRAME:
                return self._skip_result("wrong_timeframe", f"Expected {self.TIMEFRAME}, got {v6_alert.tf}")
            
            self.logger.info(f"[15M Exit] {v6_alert.type} | {v6_alert.ticker}")
            
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
            self.logger.error(f"[15M Exit Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_reversal_signal(self, alert) -> Dict[str, Any]:
        """
        Process V6 15M reversal signal.
        
        Args:
            alert: Reversal alert data
        
        Returns:
            dict: Reversal execution result
        """
        try:
            v6_alert = self._parse_alert(alert)
            
            if v6_alert.tf != self.TIMEFRAME:
                return self._skip_result("wrong_timeframe", f"Expected {self.TIMEFRAME}, got {v6_alert.tf}")
            
            self.logger.info(f"[15M Reversal] {v6_alert.type} | {v6_alert.ticker}")
            
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
            self.logger.error(f"[15M Reversal Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def _validate_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """
        Validate entry conditions for 15M intraday.
        
        Filters:
        1. Market State check (avoid CHOPPY/SIDEWAYS)
        2. Trend Pulse alignment required
        3. Confidence >= 60 (standard threshold)
        
        Args:
            alert: ZepixV6Alert to validate
        
        Returns:
            dict: Validation result with reason if failed
        """
        if alert.conf_score < self.CONFIDENCE_THRESHOLD:
            self.logger.info(f"[15M Skip] Confidence {alert.conf_score} < {self.CONFIDENCE_THRESHOLD}")
            return {"valid": False, "reason": "confidence_low"}
        
        try:
            market_state = await self.service_api.get_market_state(alert.ticker)
            if market_state and market_state.upper() in self.AVOID_MARKET_STATES:
                self.logger.info(f"[15M Skip] Market state {market_state} is unfavorable")
                return {"valid": False, "reason": "market_state_unfavorable"}
        except Exception as e:
            self.logger.debug(f"[15M] Market state check skipped: {e}")
        
        if self.REQUIRE_PULSE_ALIGNMENT:
            try:
                is_aligned = await self.service_api.check_pulse_alignment(
                    symbol=alert.ticker,
                    direction=alert.direction
                )
                if not is_aligned:
                    self.logger.info(f"[15M Skip] Trend Pulse alignment failed for {alert.direction}")
                    return {"valid": False, "reason": "pulse_alignment_failed"}
            except Exception as e:
                self.logger.debug(f"[15M] Pulse alignment check skipped: {e}")
        
        self.logger.info(
            f"[15M Valid] Conf={alert.conf_score}, Direction={alert.direction}"
        )
        
        return {"valid": True, "reason": None}
    
    async def _calculate_lot_size(self, alert: ZepixV6Alert) -> float:
        """
        Calculate lot size for 15M intraday.
        
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
            
            self.logger.debug(f"[15M Lot] Base={base_lot:.2f}, Final={final_lot:.2f}")
            
            return final_lot
            
        except Exception as e:
            self.logger.error(f"[15M Lot Error] {e}")
            return 0.02
    
    async def _place_order_a(self, alert: ZepixV6Alert, lot_size: float) -> Dict[str, Any]:
        """
        Place ORDER A ONLY for 15M intraday.
        
        Order A targets TP2 for larger intraday moves.
        
        Args:
            alert: ZepixV6Alert with trade details
            lot_size: Calculated lot size
        
        Returns:
            dict: Order execution result
        """
        try:
            ticket = await self.service_api.place_single_order_a(
                plugin_id=self.plugin_id,
                symbol=alert.ticker,
                direction=alert.direction,
                lot_size=lot_size,
                sl_price=alert.sl,
                tp_price=alert.tp2,
                comment=f"{self.plugin_id}_15m_intraday"
            )
            
            self.logger.info(
                f"[15M ORDER A] #{ticket} | {alert.ticker} {alert.direction} | "
                f"Lot={lot_size:.2f} | SL={alert.sl} | TP2={alert.tp2}"
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
                "tp": alert.tp2
            }
            
        except Exception as e:
            self.logger.error(f"[15M Order Error] {e}")
            return {"status": "error", "message": str(e)}
    
    async def _process_shadow_entry(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """Process entry in shadow mode"""
        self.logger.info(
            f"[15M SHADOW] Entry: {alert.type} | {alert.ticker} {alert.direction} | "
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
        self.logger.info(f"[15M SHADOW] Exit: {alert.type} | {alert.ticker}")
        
        return {
            "status": "shadow",
            "action": "exit",
            "symbol": alert.ticker,
            "message": "Shadow mode - no real exits"
        }
    
    async def _process_shadow_reversal(self, alert: ZepixV6Alert) -> Dict[str, Any]:
        """Process reversal in shadow mode"""
        self.logger.info(f"[15M SHADOW] Reversal: {alert.type} | {alert.ticker}")
        
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
                "require_pulse_alignment": self.REQUIRE_PULSE_ALIGNMENT,
                "avoid_market_states": self.AVOID_MARKET_STATES
            },
            "stats": self._stats
        })
        return base_status
