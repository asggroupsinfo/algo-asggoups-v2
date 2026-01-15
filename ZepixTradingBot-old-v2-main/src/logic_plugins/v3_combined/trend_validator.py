"""
V3 Trend Validator - MTF 4-Pillar System

Implements the V3 MTF (Multi-Timeframe) 4-Pillar trend validation:
- Pine sends 6 trends: [1m, 5m, 15m, 1H, 4H, 1D]
- Bot extracts indices [2:6] = [15m, 1H, 4H, 1D] (4 pillars)
- Bot ignores indices [0:2] = [1m, 5m] (too noisy)

Trend Alignment Rules:
- BUY requires 3/4 bullish pillars (min_alignment = 3)
- SELL requires 3/4 bearish pillars (min_alignment = 3)
- 2/4 alignment = REJECT entry

Trend Bypass Rules:
- entry_v3 signals BYPASS trend check (5-layer pre-validation trusted)
- Legacy entries REQUIRE trend check
- SL hunt re-entry REQUIRES trend check

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from .plugin import CombinedV3Plugin

logger = logging.getLogger(__name__)


class V3TrendValidator:
    """
    Validates MTF 4-pillar trend alignment for V3 entries.
    
    The 4-pillar system extracts only the meaningful timeframes
    (15m, 1H, 4H, 1D) and ignores noisy lower timeframes (1m, 5m).
    
    This ensures entries align with the broader market trend
    while filtering out short-term noise.
    """
    
    def __init__(self, plugin: 'CombinedV3Plugin'):
        """
        Initialize trend validator.
        
        Args:
            plugin: Parent CombinedV3Plugin instance
        """
        self.plugin = plugin
        self.service_api = plugin.service_api
        self.logger = logging.getLogger(f"plugin.{plugin.plugin_id}.trends")
        
        mtf_config = plugin.plugin_config.get("mtf_config", {})
        self.pillars_only = mtf_config.get("pillars_only", ["15m", "1h", "4h", "1d"])
        self.ignore_timeframes = mtf_config.get("ignore_timeframes", ["1m", "5m"])
        self.min_alignment = mtf_config.get("min_alignment", 3)
        
        self.bypass_config = plugin.plugin_config.get("trend_bypass", {})
    
    def extract_4_pillar_trends(self, mtf_string: str) -> Dict[str, int]:
        """
        Extract only 4-pillar trends, ignore 1m/5m.
        
        Input: "1,1,-1,1,1,1" (6 values: 1m,5m,15m,1H,4H,1D)
        Output: {"15m": -1, "1h": 1, "4h": 1, "1d": 1}
        
        Args:
            mtf_string: Comma-separated trend string from Pine
            
        Returns:
            dict: 4-pillar trends (15m, 1h, 4h, 1d)
            
        Raises:
            ValueError: If MTF string doesn't have 6 values
        """
        try:
            trends = [int(x.strip()) for x in mtf_string.split(',')]
            
            if len(trends) != 6:
                raise ValueError(f"Invalid MTF string: expected 6 values, got {len(trends)}")
            
            pillars = {
                "15m": trends[2],
                "1h": trends[3],
                "4h": trends[4],
                "1d": trends[5]
            }
            
            self.logger.debug(
                f"MTF Extraction: Raw={mtf_string} | "
                f"Ignored=[1m:{trends[0]}, 5m:{trends[1]}] | "
                f"Pillars={pillars}"
            )
            
            return pillars
            
        except (ValueError, IndexError) as e:
            self.logger.error(f"MTF extraction error: {e}")
            raise ValueError(f"Invalid MTF string format: {mtf_string}")
    
    async def validate_trend_alignment(self, alert) -> bool:
        """
        Check if signal aligns with current 4-pillar trends.
        
        Rules:
        - BUY requires at least 3/4 bullish pillars (value = 1)
        - SELL requires at least 3/4 bearish pillars (value = -1)
        - 2/4 alignment = REJECT entry
        
        Args:
            alert: Alert data with mtf_trends or market_trend
            
        Returns:
            bool: True if trend aligned, False otherwise
        """
        direction = self._get_direction(alert)
        
        mtf_string = self._get_mtf_trends(alert)
        
        if not mtf_string:
            self.logger.warning("No MTF trends available, allowing entry")
            return True
        
        try:
            pillars = self.extract_4_pillar_trends(mtf_string)
        except ValueError as e:
            self.logger.warning(f"MTF extraction failed: {e}, allowing entry")
            return True
        
        bullish_count = sum(1 for v in pillars.values() if v == 1)
        bearish_count = sum(1 for v in pillars.values() if v == -1)
        
        if direction.lower() == "buy":
            aligned = bullish_count >= self.min_alignment
            self.logger.info(
                f"Trend Check (BUY): {bullish_count}/4 bullish | "
                f"Required: {self.min_alignment}/4 | "
                f"Result: {'PASS' if aligned else 'FAIL'}"
            )
        else:
            aligned = bearish_count >= self.min_alignment
            self.logger.info(
                f"Trend Check (SELL): {bearish_count}/4 bearish | "
                f"Required: {self.min_alignment}/4 | "
                f"Result: {'PASS' if aligned else 'FAIL'}"
            )
        
        return aligned
    
    def should_bypass_trend_check(self, alert) -> bool:
        """
        Check if trend validation should be bypassed.
        
        Bypass Rules:
        - entry_v3 signals: BYPASS (5-layer pre-validation trusted)
        - Legacy entries: REQUIRE trend check
        - SL hunt re-entry: REQUIRE trend check
        
        Args:
            alert: Alert data
            
        Returns:
            bool: True if trend check should be bypassed
        """
        alert_type = self._get_alert_type(alert)
        signal_source = self._get_signal_source(alert)
        
        if alert_type == "entry_v3" and self.bypass_config.get("bypass_for_entry_v3", True):
            self.logger.debug("Trend bypass: entry_v3 signal (5-layer pre-validated)")
            return True
        
        if signal_source == "sl_hunt" and not self.bypass_config.get("bypass_for_sl_hunt", False):
            self.logger.debug("Trend check required: SL hunt re-entry")
            return False
        
        if signal_source == "legacy" and not self.bypass_config.get("bypass_for_legacy", False):
            self.logger.debug("Trend check required: Legacy entry")
            return False
        
        return False
    
    async def update_trend_database(self, alert) -> Dict[str, Any]:
        """
        Update market_trends table with 4-pillar data.
        
        Called when Trend_Pulse signal is received.
        
        Args:
            alert: Alert data with mtf_trends
            
        Returns:
            dict: Update result
        """
        symbol = self._get_symbol(alert)
        mtf_string = self._get_mtf_trends(alert)
        
        if not mtf_string:
            self.logger.warning("No MTF trends to update")
            return {"status": "no_data"}
        
        try:
            pillars = self.extract_4_pillar_trends(mtf_string)
            
            for tf, direction_value in pillars.items():
                direction = 'bullish' if direction_value == 1 else 'bearish'
                
                try:
                    await self.service_api.update_trend(
                        plugin_id=self.plugin.plugin_id,
                        symbol=symbol,
                        timeframe=tf,
                        direction=direction
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to update trend for {tf}: {e}")
            
            self.logger.info(f"MTF 4-Pillar updated: {pillars}")
            
            return {
                "status": "success",
                "symbol": symbol,
                "pillars": pillars
            }
            
        except ValueError as e:
            self.logger.error(f"Trend database update failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_trend_summary(self, mtf_string: str) -> Dict[str, Any]:
        """
        Get summary of trend alignment.
        
        Args:
            mtf_string: Comma-separated trend string
            
        Returns:
            dict: Trend summary with counts and recommendation
        """
        try:
            pillars = self.extract_4_pillar_trends(mtf_string)
            
            bullish_count = sum(1 for v in pillars.values() if v == 1)
            bearish_count = sum(1 for v in pillars.values() if v == -1)
            neutral_count = sum(1 for v in pillars.values() if v == 0)
            
            if bullish_count >= self.min_alignment:
                recommendation = "BUY"
                strength = "strong" if bullish_count == 4 else "moderate"
            elif bearish_count >= self.min_alignment:
                recommendation = "SELL"
                strength = "strong" if bearish_count == 4 else "moderate"
            else:
                recommendation = "NEUTRAL"
                strength = "weak"
            
            return {
                "pillars": pillars,
                "bullish_count": bullish_count,
                "bearish_count": bearish_count,
                "neutral_count": neutral_count,
                "recommendation": recommendation,
                "strength": strength,
                "min_alignment": self.min_alignment
            }
            
        except ValueError as e:
            return {
                "error": str(e),
                "recommendation": "UNKNOWN"
            }
    
    def validate_entry_conditions(self, alert) -> Dict[str, Any]:
        """
        Comprehensive entry validation including trend check.
        
        Args:
            alert: Alert data
            
        Returns:
            dict: Validation result with details
        """
        result = {
            "valid": True,
            "checks": [],
            "bypass_applied": False
        }
        
        if self.should_bypass_trend_check(alert):
            result["bypass_applied"] = True
            result["checks"].append({
                "check": "trend_alignment",
                "status": "bypassed",
                "reason": "entry_v3 signal (5-layer pre-validated)"
            })
            return result
        
        mtf_string = self._get_mtf_trends(alert)
        if mtf_string:
            try:
                summary = self.get_trend_summary(mtf_string)
                direction = self._get_direction(alert)
                
                if direction.lower() == "buy":
                    aligned = summary.get("bullish_count", 0) >= self.min_alignment
                else:
                    aligned = summary.get("bearish_count", 0) >= self.min_alignment
                
                result["checks"].append({
                    "check": "trend_alignment",
                    "status": "pass" if aligned else "fail",
                    "details": summary
                })
                
                if not aligned:
                    result["valid"] = False
                    
            except Exception as e:
                result["checks"].append({
                    "check": "trend_alignment",
                    "status": "error",
                    "error": str(e)
                })
        
        return result
    
    def _get_direction(self, alert) -> str:
        """Extract direction from alert"""
        if hasattr(alert, 'direction'):
            return alert.direction
        if isinstance(alert, dict):
            return alert.get('direction', '')
        return ''
    
    def _get_symbol(self, alert) -> str:
        """Extract symbol from alert"""
        if hasattr(alert, 'symbol'):
            return alert.symbol
        if isinstance(alert, dict):
            return alert.get('symbol', '')
        return ''
    
    def _get_mtf_trends(self, alert) -> Optional[str]:
        """Extract mtf_trends string from alert"""
        if hasattr(alert, 'mtf_trends') and alert.mtf_trends:
            return alert.mtf_trends
        if hasattr(alert, 'market_trend') and alert.market_trend:
            return alert.market_trend
        if isinstance(alert, dict):
            return alert.get('mtf_trends') or alert.get('market_trend')
        return None
    
    def _get_alert_type(self, alert) -> str:
        """Extract alert type from alert"""
        if hasattr(alert, 'type'):
            return alert.type
        if isinstance(alert, dict):
            return alert.get('type', '')
        return ''
    
    def _get_signal_source(self, alert) -> str:
        """Extract signal source from alert"""
        if hasattr(alert, 'signal_source'):
            return alert.signal_source
        if isinstance(alert, dict):
            return alert.get('signal_source', '')
        return ''
