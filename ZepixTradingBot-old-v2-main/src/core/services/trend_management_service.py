"""
Trend Management Service - Stateless service for trend data

Provides V3 4-Pillar Trend Logic and V6 Trend Pulse Logic.
All methods are stateless - they use passed parameters and database for state.

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TrendManagementService:
    """
    Stateless service for trend management.
    Wraps TimeframeTrendManager and provides V3/V6 specific trend methods.
    """
    
    def __init__(self, trend_manager, db=None):
        self._trend_manager = trend_manager
        self._db = db
        self._pulse_cache = {}
    
    async def get_timeframe_trend(
        self,
        symbol: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """
        Get V3 4-pillar MTF trend for a specific timeframe
        
        Args:
            symbol: Trading symbol
            timeframe: '15m', '1h', '4h', '1d' ONLY
        
        Returns:
            Dict with trend direction and metadata
        """
        try:
            trend = self._trend_manager.get_trend(symbol, timeframe)
            mode = self._trend_manager.get_mode(symbol, timeframe)
            
            direction = trend.lower() if trend else "neutral"
            value = 1 if direction == "bullish" else (-1 if direction == "bearish" else 0)
            
            return {
                "timeframe": timeframe,
                "direction": direction,
                "value": value,
                "mode": mode,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
        except Exception as e:
            logger.error(f"[TREND] Error getting trend for {symbol} {timeframe}: {e}")
            return {
                "timeframe": timeframe,
                "direction": "neutral",
                "value": 0,
                "mode": "AUTO",
                "last_updated": None
            }
    
    async def get_mtf_trends(self, symbol: str) -> Dict[str, int]:
        """
        Get ALL 4-pillar trends at once
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Dict with trend values for each timeframe
            {
                "15m": 1,   # bullish
                "1h": 1,    # bullish
                "4h": -1,   # bearish
                "1d": 1     # bullish
            }
        """
        try:
            all_trends = self._trend_manager.get_all_trends(symbol)
            
            result = {}
            for tf in ["15m", "1h", "4h", "1d"]:
                trend = all_trends.get(tf, "NEUTRAL")
                if trend == "BULLISH":
                    result[tf] = 1
                elif trend == "BEARISH":
                    result[tf] = -1
                else:
                    result[tf] = 0
            
            return result
            
        except Exception as e:
            logger.error(f"[MTF_TRENDS] Error getting MTF trends for {symbol}: {e}")
            return {"15m": 0, "1h": 0, "4h": 0, "1d": 0}
    
    async def validate_v3_trend_alignment(
        self,
        symbol: str,
        direction: str,
        min_aligned: int = 3
    ) -> bool:
        """
        Check if signal aligns with V3 4-pillar system
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            min_aligned: Minimum pillars that must align (default 3/4)
        
        Returns:
            True if enough pillars align with direction
        """
        try:
            mtf_trends = await self.get_mtf_trends(symbol)
            
            if direction.upper() == 'BUY':
                aligned_count = sum(1 for v in mtf_trends.values() if v == 1)
            else:
                aligned_count = sum(1 for v in mtf_trends.values() if v == -1)
            
            is_aligned = aligned_count >= min_aligned
            
            logger.info(
                f"[V3_ALIGNMENT] {symbol} {direction}: "
                f"{aligned_count}/4 pillars aligned (need {min_aligned}). "
                f"Result: {'PASS' if is_aligned else 'FAIL'}"
            )
            
            return is_aligned
            
        except Exception as e:
            logger.error(f"[V3_ALIGNMENT] Error validating alignment: {e}")
            return False
    
    async def check_logic_alignment(
        self,
        symbol: str,
        logic: str,
        direction: str
    ) -> Dict[str, Any]:
        """
        Check if signal aligns with specific logic requirements
        
        Args:
            symbol: Trading symbol
            logic: 'combinedlogic-1', 'combinedlogic-2', 'combinedlogic-3'
            direction: 'BUY' or 'SELL'
        
        Returns:
            Dict with alignment status and details
        """
        try:
            result = self._trend_manager.check_logic_alignment(symbol, logic)
            
            if result.get("aligned", False):
                trend_direction = result.get("direction", "NEUTRAL")
                expected = "BULLISH" if direction.upper() == "BUY" else "BEARISH"
                
                if trend_direction == expected:
                    return {
                        "aligned": True,
                        "direction": trend_direction,
                        "details": result.get("details", {}),
                        "logic": logic
                    }
                else:
                    return {
                        "aligned": False,
                        "reason": f"Trend direction {trend_direction} != signal direction {expected}",
                        "details": result.get("details", {}),
                        "logic": logic
                    }
            else:
                return {
                    "aligned": False,
                    "reason": result.get("failure_reason", "Unknown"),
                    "details": result.get("details", {}),
                    "logic": logic
                }
                
        except Exception as e:
            logger.error(f"[LOGIC_ALIGNMENT] Error checking alignment: {e}")
            return {
                "aligned": False,
                "reason": str(e),
                "details": {},
                "logic": logic
            }
    
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
        Update market_trends table with Trend Pulse alert data (V6)
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe string
            bull_count: Number of bullish indicators
            bear_count: Number of bearish indicators
            market_state: Current market state string
            changes: Which timeframes changed
        """
        try:
            cache_key = f"{symbol}_{timeframe}"
            self._pulse_cache[cache_key] = {
                "bull_count": bull_count,
                "bear_count": bear_count,
                "market_state": market_state,
                "changes": changes,
                "last_updated": datetime.now().isoformat()
            }
            
            if self._db:
                try:
                    cursor = self._db.conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO market_trends 
                        (symbol, timeframe, bull_count, bear_count, market_state, changes, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (symbol, timeframe, bull_count, bear_count, market_state, changes, datetime.now().isoformat()))
                    self._db.conn.commit()
                except Exception as db_error:
                    logger.debug(f"[TREND_PULSE] DB update skipped (table may not exist): {db_error}")
            
            logger.info(
                f"[TREND_PULSE] Updated {symbol} {timeframe}: "
                f"Bull={bull_count}, Bear={bear_count}, State={market_state}"
            )
            
        except Exception as e:
            logger.error(f"[TREND_PULSE] Error updating trend pulse: {e}")
    
    async def get_market_state(self, symbol: str) -> str:
        """
        Get current market state for symbol (V6)
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Market state string: 'TRENDING_BULLISH', 'TRENDING_BEARISH', 'SIDEWAYS', etc.
        """
        try:
            for tf in ["15", "60", "5"]:
                cache_key = f"{symbol}_{tf}"
                if cache_key in self._pulse_cache:
                    return self._pulse_cache[cache_key].get("market_state", "UNKNOWN")
            
            if self._db:
                try:
                    cursor = self._db.conn.cursor()
                    cursor.execute('''
                        SELECT market_state FROM market_trends 
                        WHERE symbol = ? 
                        ORDER BY last_updated DESC LIMIT 1
                    ''', (symbol,))
                    row = cursor.fetchone()
                    if row:
                        return row[0]
                except Exception as db_error:
                    logger.debug(f"[MARKET_STATE] DB query skipped: {db_error}")
            
            return "UNKNOWN"
            
        except Exception as e:
            logger.error(f"[MARKET_STATE] Error getting market state: {e}")
            return "UNKNOWN"
    
    async def check_pulse_alignment(
        self,
        symbol: str,
        direction: str
    ) -> bool:
        """
        Check if signal aligns with Trend Pulse counts (V6)
        
        Logic:
        - For BUY: bull_count > bear_count
        - For SELL: bear_count > bull_count
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
        
        Returns:
            True if pulse counts align with direction
        """
        try:
            pulse_data = await self.get_pulse_data(symbol)
            
            total_bull = 0
            total_bear = 0
            
            for tf_data in pulse_data.values():
                total_bull += tf_data.get("bull_count", 0)
                total_bear += tf_data.get("bear_count", 0)
            
            if direction.upper() == 'BUY':
                aligned = total_bull > total_bear
            else:
                aligned = total_bear > total_bull
            
            logger.info(
                f"[PULSE_ALIGNMENT] {symbol} {direction}: "
                f"Bull={total_bull}, Bear={total_bear}. "
                f"Result: {'PASS' if aligned else 'FAIL'}"
            )
            
            return aligned
            
        except Exception as e:
            logger.error(f"[PULSE_ALIGNMENT] Error checking pulse alignment: {e}")
            return False
    
    async def get_pulse_data(
        self,
        symbol: str,
        timeframe: str = None
    ) -> Dict[str, Dict[str, int]]:
        """
        Get raw Trend Pulse counts
        
        Args:
            symbol: Trading symbol
            timeframe: Optional specific timeframe
        
        Returns:
            Dict with pulse data per timeframe
            {
                "5": {"bull_count": 4, "bear_count": 2},
                "15": {"bull_count": 5, "bear_count": 1},
                "60": {"bull_count": 3, "bear_count": 3}
            }
        """
        try:
            result = {}
            
            for tf in ["5", "15", "60"]:
                if timeframe and tf != timeframe:
                    continue
                    
                cache_key = f"{symbol}_{tf}"
                if cache_key in self._pulse_cache:
                    data = self._pulse_cache[cache_key]
                    result[tf] = {
                        "bull_count": data.get("bull_count", 0),
                        "bear_count": data.get("bear_count", 0)
                    }
                else:
                    result[tf] = {"bull_count": 0, "bear_count": 0}
            
            if self._db and not result:
                try:
                    cursor = self._db.conn.cursor()
                    cursor.execute('''
                        SELECT timeframe, bull_count, bear_count 
                        FROM market_trends 
                        WHERE symbol = ?
                    ''', (symbol,))
                    for row in cursor.fetchall():
                        result[row[0]] = {
                            "bull_count": row[1],
                            "bear_count": row[2]
                        }
                except Exception as db_error:
                    logger.debug(f"[PULSE_DATA] DB query skipped: {db_error}")
            
            return result
            
        except Exception as e:
            logger.error(f"[PULSE_DATA] Error getting pulse data: {e}")
            return {}
    
    async def update_trend(
        self,
        symbol: str,
        timeframe: str,
        signal: str,
        mode: str = "AUTO"
    ) -> bool:
        """
        Update trend for a specific symbol and timeframe
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe string
            signal: 'bull', 'bear', 'buy', 'sell', etc.
            mode: 'AUTO' or 'MANUAL'
        
        Returns:
            True if update successful
        """
        try:
            result = self._trend_manager.update_trend(symbol, timeframe, signal, mode)
            return result if result is not None else True
        except Exception as e:
            logger.error(f"[UPDATE_TREND] Error updating trend: {e}")
            return False
