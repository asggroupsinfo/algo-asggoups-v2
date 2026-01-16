"""
Trend Pulse Manager - V6 Price Action Trend System

Manages the V6 Trend Pulse alerts which track bull/bear counts across timeframes.
This is separate from the V3 Traditional Trend Manager.

Key Features:
- Store and calculate Trend Pulse metrics
- Validate Bull/Bear counts for trade alignment
- Track market state (TRENDING_BULLISH, TRENDING_BEARISH, SIDEWAYS)
- Database persistence for trend data

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import threading

logger = logging.getLogger(__name__)


class MarketState(Enum):
    """Market state classifications based on Trend Pulse"""
    TRENDING_BULLISH = "TRENDING_BULLISH"
    TRENDING_BEARISH = "TRENDING_BEARISH"
    SIDEWAYS = "SIDEWAYS"
    CHOPPY = "CHOPPY"
    UNKNOWN = "UNKNOWN"


@dataclass
class TrendPulseData:
    """Data class for Trend Pulse information"""
    symbol: str
    timeframe: str
    bull_count: int
    bear_count: int
    market_state: str
    changes: str = ""
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def net_direction(self) -> int:
        """Returns 1 for bullish bias, -1 for bearish bias, 0 for neutral"""
        if self.bull_count > self.bear_count:
            return 1
        elif self.bear_count > self.bull_count:
            return -1
        return 0
    
    @property
    def strength(self) -> float:
        """Returns strength of trend (0.0 to 1.0)"""
        total = self.bull_count + self.bear_count
        if total == 0:
            return 0.0
        return abs(self.bull_count - self.bear_count) / total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "bull_count": self.bull_count,
            "bear_count": self.bear_count,
            "market_state": self.market_state,
            "changes": self.changes,
            "last_updated": self.last_updated.isoformat(),
            "net_direction": self.net_direction,
            "strength": self.strength
        }


class TrendPulseManager:
    """
    Manages V6 Trend Pulse alerts and market state tracking.
    
    The Trend Pulse system tracks bull/bear counts across multiple timeframes
    to determine overall market direction and strength.
    
    Usage:
        manager = TrendPulseManager(database)
        await manager.update_pulse(symbol, tf, bull_count, bear_count, state)
        is_aligned = await manager.check_pulse_alignment(symbol, "BUY")
    """
    
    def __init__(self, database=None):
        """
        Initialize TrendPulseManager.
        
        Args:
            database: Optional database connection for persistence
        """
        self._db = database
        self._pulse_cache: Dict[str, TrendPulseData] = {}
        self._lock = threading.RLock()
        
        self._ensure_table_exists()
        
        logger.info("[TREND_PULSE] TrendPulseManager initialized")
    
    def _ensure_table_exists(self):
        """Create market_trends table if it doesn't exist"""
        if not self._db:
            return
            
        try:
            if hasattr(self._db, 'conn'):
                cursor = self._db.conn.cursor()
            elif hasattr(self._db, 'execute'):
                cursor = self._db
            else:
                return
                
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_trends (
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    bull_count INTEGER DEFAULT 0,
                    bear_count INTEGER DEFAULT 0,
                    market_state TEXT DEFAULT 'UNKNOWN',
                    changes TEXT DEFAULT '',
                    last_updated TEXT,
                    PRIMARY KEY (symbol, timeframe)
                )
            ''')
            
            if hasattr(self._db, 'conn'):
                self._db.conn.commit()
                
            logger.debug("[TREND_PULSE] market_trends table ensured")
            
        except Exception as e:
            logger.debug(f"[TREND_PULSE] Table creation skipped: {e}")
    
    async def update_pulse(
        self,
        symbol: str,
        timeframe: str,
        bull_count: int,
        bear_count: int,
        market_state: str,
        changes: str = ""
    ) -> TrendPulseData:
        """
        Update market_trends with Trend Pulse alert data.
        
        Args:
            symbol: Trading symbol (e.g., "XAUUSD")
            timeframe: Timeframe string (e.g., "5", "15", "60")
            bull_count: Number of bullish indicators
            bear_count: Number of bearish indicators
            market_state: Current market state string
            changes: Which timeframes changed (comma-separated)
        
        Returns:
            TrendPulseData: Updated pulse data
        """
        with self._lock:
            pulse_data = TrendPulseData(
                symbol=symbol,
                timeframe=timeframe,
                bull_count=bull_count,
                bear_count=bear_count,
                market_state=market_state,
                changes=changes,
                last_updated=datetime.now()
            )
            
            cache_key = f"{symbol}_{timeframe}"
            self._pulse_cache[cache_key] = pulse_data
            
            if self._db:
                try:
                    if hasattr(self._db, 'conn'):
                        cursor = self._db.conn.cursor()
                        cursor.execute('''
                            INSERT OR REPLACE INTO market_trends 
                            (symbol, timeframe, bull_count, bear_count, market_state, changes, last_updated)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            symbol, timeframe, bull_count, bear_count,
                            market_state, changes, pulse_data.last_updated.isoformat()
                        ))
                        self._db.conn.commit()
                except Exception as db_error:
                    logger.debug(f"[TREND_PULSE] DB update skipped: {db_error}")
            
            logger.info(
                f"[TREND_PULSE] Updated {symbol} {timeframe}m: "
                f"Bull={bull_count}, Bear={bear_count}, State={market_state}"
            )
            
            return pulse_data
    
    async def get_pulse(
        self,
        symbol: str,
        timeframe: str = None
    ) -> Optional[TrendPulseData]:
        """
        Get Trend Pulse data for a symbol.
        
        Args:
            symbol: Trading symbol
            timeframe: Optional specific timeframe
        
        Returns:
            TrendPulseData or None if not found
        """
        with self._lock:
            if timeframe:
                cache_key = f"{symbol}_{timeframe}"
                return self._pulse_cache.get(cache_key)
            
            for tf in ["15", "60", "5", "1"]:
                cache_key = f"{symbol}_{tf}"
                if cache_key in self._pulse_cache:
                    return self._pulse_cache[cache_key]
            
            return None
    
    async def get_market_state(self, symbol: str) -> str:
        """
        Get current market state for symbol.
        
        Aggregates across timeframes to determine overall state.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Market state string: 'TRENDING_BULLISH', 'TRENDING_BEARISH', 'SIDEWAYS', etc.
        """
        with self._lock:
            for tf in ["15", "60", "5"]:
                cache_key = f"{symbol}_{tf}"
                if cache_key in self._pulse_cache:
                    return self._pulse_cache[cache_key].market_state
            
            if self._db:
                try:
                    if hasattr(self._db, 'conn'):
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
            
            return MarketState.UNKNOWN.value
    
    async def check_pulse_alignment(
        self,
        symbol: str,
        direction: str,
        min_count_diff: int = 1
    ) -> bool:
        """
        Check if signal aligns with Trend Pulse counts.
        
        Logic:
        - For BUY: bull_count > bear_count (by min_count_diff)
        - For SELL: bear_count > bull_count (by min_count_diff)
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            min_count_diff: Minimum difference required (default 1)
        
        Returns:
            True if pulse counts align with direction
        """
        with self._lock:
            total_bull = 0
            total_bear = 0
            
            for tf in ["5", "15", "60"]:
                cache_key = f"{symbol}_{tf}"
                if cache_key in self._pulse_cache:
                    data = self._pulse_cache[cache_key]
                    total_bull += data.bull_count
                    total_bear += data.bear_count
            
            if direction.upper() == 'BUY':
                aligned = (total_bull - total_bear) >= min_count_diff
            else:
                aligned = (total_bear - total_bull) >= min_count_diff
            
            logger.info(
                f"[PULSE_ALIGNMENT] {symbol} {direction}: "
                f"Bull={total_bull}, Bear={total_bear}, "
                f"Diff={abs(total_bull - total_bear)}. "
                f"Result: {'PASS' if aligned else 'FAIL'}"
            )
            
            return aligned
    
    async def get_pulse_counts(self, symbol: str) -> Tuple[int, int]:
        """
        Get aggregated bull/bear counts for a symbol.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Tuple of (total_bull_count, total_bear_count)
        """
        with self._lock:
            total_bull = 0
            total_bear = 0
            
            for tf in ["5", "15", "60"]:
                cache_key = f"{symbol}_{tf}"
                if cache_key in self._pulse_cache:
                    data = self._pulse_cache[cache_key]
                    total_bull += data.bull_count
                    total_bear += data.bear_count
            
            return total_bull, total_bear
    
    async def get_all_pulse_data(self, symbol: str) -> Dict[str, TrendPulseData]:
        """
        Get all Trend Pulse data for a symbol across timeframes.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Dict mapping timeframe to TrendPulseData
        """
        with self._lock:
            result = {}
            
            for tf in ["1", "5", "15", "60"]:
                cache_key = f"{symbol}_{tf}"
                if cache_key in self._pulse_cache:
                    result[tf] = self._pulse_cache[cache_key]
            
            return result
    
    async def validate_for_entry(
        self,
        symbol: str,
        direction: str,
        timeframe: str,
        require_alignment: bool = True
    ) -> Dict[str, Any]:
        """
        Validate if entry is allowed based on Trend Pulse.
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            timeframe: Signal timeframe
            require_alignment: Whether to require pulse alignment
        
        Returns:
            Dict with validation result and details
        """
        result = {
            "valid": True,
            "reason": None,
            "market_state": await self.get_market_state(symbol),
            "pulse_aligned": False,
            "bull_count": 0,
            "bear_count": 0
        }
        
        bull_count, bear_count = await self.get_pulse_counts(symbol)
        result["bull_count"] = bull_count
        result["bear_count"] = bear_count
        
        if require_alignment:
            result["pulse_aligned"] = await self.check_pulse_alignment(symbol, direction)
            
            if not result["pulse_aligned"]:
                result["valid"] = False
                result["reason"] = f"Pulse not aligned: Bull={bull_count}, Bear={bear_count}"
        else:
            result["pulse_aligned"] = True
        
        market_state = result["market_state"]
        if direction.upper() == "BUY" and "BEARISH" in market_state:
            result["valid"] = False
            result["reason"] = f"Market state {market_state} conflicts with BUY"
        elif direction.upper() == "SELL" and "BULLISH" in market_state:
            result["valid"] = False
            result["reason"] = f"Market state {market_state} conflicts with SELL"
        
        return result
    
    async def get_timeframe_alignment(
        self,
        symbol: str,
        signal_tf: str,
        check_tf: str
    ) -> bool:
        """
        Check if signal timeframe aligns with a higher timeframe.
        
        Used for 5M requiring 15M alignment, etc.
        
        Args:
            symbol: Trading symbol
            signal_tf: Signal timeframe (e.g., "5")
            check_tf: Timeframe to check against (e.g., "15")
        
        Returns:
            True if timeframes are aligned
        """
        signal_pulse = await self.get_pulse(symbol, signal_tf)
        check_pulse = await self.get_pulse(symbol, check_tf)
        
        if not signal_pulse or not check_pulse:
            logger.debug(f"[TF_ALIGNMENT] Missing pulse data for {symbol}")
            return True
        
        aligned = signal_pulse.net_direction == check_pulse.net_direction
        
        logger.info(
            f"[TF_ALIGNMENT] {symbol} {signal_tf}m vs {check_tf}m: "
            f"Signal={signal_pulse.net_direction}, Check={check_pulse.net_direction}. "
            f"Result: {'ALIGNED' if aligned else 'MISALIGNED'}"
        )
        
        return aligned
    
    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        with self._lock:
            symbols = set()
            for key in self._pulse_cache:
                symbol = key.rsplit("_", 1)[0]
                symbols.add(symbol)
            
            return {
                "cached_entries": len(self._pulse_cache),
                "tracked_symbols": list(symbols),
                "database_connected": self._db is not None
            }
    
    def clear_cache(self, symbol: str = None):
        """
        Clear cached pulse data.
        
        Args:
            symbol: Optional symbol to clear (clears all if None)
        """
        with self._lock:
            if symbol:
                keys_to_remove = [k for k in self._pulse_cache if k.startswith(f"{symbol}_")]
                for key in keys_to_remove:
                    del self._pulse_cache[key]
                logger.info(f"[TREND_PULSE] Cleared cache for {symbol}")
            else:
                self._pulse_cache.clear()
                logger.info("[TREND_PULSE] Cleared all cache")


def create_trend_pulse_manager(database=None) -> TrendPulseManager:
    """
    Factory function to create TrendPulseManager.
    
    Args:
        database: Optional database connection
    
    Returns:
        TrendPulseManager instance
    """
    return TrendPulseManager(database)
