"""
Market Data Service - Stateless service for market data access

Provides real-time market data access for all plugins with spread checks,
price validation, and market condition analysis.

Critical for V6 1M Plugin: Spread filtering before scalp entries

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Stateless service for market data access.
    Provides spread checks, price data, and volatility analysis.
    """
    
    def __init__(self, mt5_client, config, pip_calculator):
        self._mt5 = mt5_client
        self._config = config
        self._pip_calculator = pip_calculator
        self._cache = {}
        self._cache_ttl = 1.0
    
    async def get_current_spread(self, symbol: str) -> float:
        """
        Get current spread in PIPS
        
        Critical for V6 1M plugin spread filtering.
        
        Args:
            symbol: Symbol name (e.g., 'XAUUSD')
        
        Returns:
            Spread in pips (e.g., 1.5)
        """
        try:
            symbol_info = self._mt5.get_symbol_info(symbol)
            if symbol_info is None:
                logger.warning(f"[SPREAD] Symbol {symbol} not found")
                return 999.9
            
            spread_points = symbol_info.get('spread', 0)
            point_value = symbol_info.get('point', 0.01)
            
            if symbol in ['XAUUSD', 'XAGUSD']:
                spread_pips = (spread_points * point_value) * 10
            else:
                spread_pips = spread_points / 10.0
            
            return round(spread_pips, 1)
            
        except Exception as e:
            logger.error(f"[SPREAD] Failed to get spread for {symbol}: {e}")
            return 999.9
    
    async def check_spread_acceptable(
        self,
        symbol: str,
        max_spread_pips: float
    ) -> bool:
        """
        Check if spread is within acceptable range
        
        Args:
            symbol: Symbol name
            max_spread_pips: Maximum acceptable spread
        
        Returns:
            True if spread <= max_spread_pips
        """
        current_spread = await self.get_current_spread(symbol)
        acceptable = current_spread <= max_spread_pips
        
        if not acceptable:
            logger.info(
                f"[SPREAD_CHECK] {symbol}: Spread {current_spread} > {max_spread_pips} - REJECTED"
            )
        
        return acceptable
    
    async def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current bid/ask prices
        
        Args:
            symbol: Symbol name
        
        Returns:
            Dict with bid, ask, spread, and timestamp
        """
        try:
            tick = self._mt5.get_symbol_tick(symbol)
            if tick is None:
                logger.warning(f"[PRICE] No tick data for {symbol}")
                return None
            
            spread = await self.get_current_spread(symbol)
            
            return {
                "bid": tick.get('bid', 0.0),
                "ask": tick.get('ask', 0.0),
                "spread_pips": spread,
                "last": tick.get('last', 0.0),
                "volume": tick.get('volume', 0),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"[PRICE] Failed to get price for {symbol}: {e}")
            return None
    
    async def get_price_range(
        self,
        symbol: str,
        timeframe: str,
        bars_back: int = 20
    ) -> Optional[Dict[str, Any]]:
        """
        Get price range (high/low) for recent bars
        
        Args:
            symbol: Symbol name
            timeframe: '1m', '5m', '15m', '1h'
            bars_back: Number of bars to analyze
        
        Returns:
            Dict with high, low, range_pips, and atr_estimate
        """
        try:
            rates = self._mt5.get_rates(symbol, timeframe, bars_back)
            if rates is None or len(rates) == 0:
                logger.warning(f"[PRICE_RANGE] No data for {symbol} {timeframe}")
                return None
            
            high = max(r.get('high', 0) for r in rates)
            low = min(r.get('low', 0) for r in rates)
            
            if symbol in ['XAUUSD', 'XAGUSD']:
                range_pips = (high - low) * 10
            else:
                range_pips = (high - low) * 10000
            
            ranges = [(r.get('high', 0) - r.get('low', 0)) for r in rates]
            atr = sum(ranges) / len(ranges) if ranges else 0
            if symbol in ['XAUUSD', 'XAGUSD']:
                atr_pips = atr * 10
            else:
                atr_pips = atr * 10000
            
            return {
                "high": high,
                "low": low,
                "range_pips": round(range_pips, 1),
                "atr_estimate": round(atr_pips, 1),
                "bars_analyzed": len(rates)
            }
            
        except Exception as e:
            logger.error(f"[PRICE_RANGE] Failed to get price range for {symbol}: {e}")
            return None
    
    async def is_market_open(self, symbol: str) -> bool:
        """
        Check if market is currently open for trading
        
        Args:
            symbol: Symbol name
        
        Returns:
            True if market is open
        """
        try:
            symbol_info = self._mt5.get_symbol_info(symbol)
            if symbol_info is None:
                return False
            
            trade_mode = symbol_info.get('trade_mode', 0)
            return trade_mode in [0, 1, 2]
            
        except Exception as e:
            logger.error(f"[MARKET_OPEN] Failed to check market status for {symbol}: {e}")
            return False
    
    async def get_trading_hours(self, symbol: str) -> Dict[str, Any]:
        """
        Get trading hours for symbol
        
        Args:
            symbol: Symbol name
        
        Returns:
            Dict with is_open, session_start, session_end
        """
        is_open = await self.is_market_open(symbol)
        
        return {
            "is_open": is_open,
            "session_start": "00:00",
            "session_end": "23:59",
            "next_session_start": "Monday 00:00" if not is_open else "N/A"
        }
    
    async def get_volatility_state(
        self,
        symbol: str,
        timeframe: str = '15m'
    ) -> Dict[str, Any]:
        """
        Analyze current volatility state
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe for analysis
        
        Returns:
            Dict with state (HIGH/MODERATE/LOW), ATR values, and ratio
        """
        try:
            range_data = await self.get_price_range(symbol, timeframe, 20)
            if not range_data:
                return {"state": "UNKNOWN"}
            
            current_atr = range_data['atr_estimate']
            
            long_term_data = await self.get_price_range(symbol, timeframe, 100)
            avg_atr = long_term_data['atr_estimate'] if long_term_data else current_atr
            
            vol_ratio = current_atr / avg_atr if avg_atr > 0 else 1.0
            
            if vol_ratio > 1.5:
                state = "HIGH"
            elif vol_ratio > 0.8:
                state = "MODERATE"
            else:
                state = "LOW"
            
            return {
                "state": state,
                "atr_current": round(current_atr, 1),
                "atr_average": round(avg_atr, 1),
                "volatility_ratio": round(vol_ratio, 2)
            }
            
        except Exception as e:
            logger.error(f"[VOLATILITY] Failed to analyze volatility for {symbol}: {e}")
            return {"state": "UNKNOWN"}
    
    async def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive symbol information
        
        Args:
            symbol: Symbol name
        
        Returns:
            Dict with digits, point, lot sizes, contract size
        """
        try:
            info = self._mt5.get_symbol_info(symbol)
            if info is None:
                logger.warning(f"[SYMBOL_INFO] Symbol {symbol} not found")
                return None
            
            return {
                "digits": info.get('digits', 2),
                "point": info.get('point', 0.01),
                "pip_value_per_std_lot": 1.0,
                "min_lot": info.get('volume_min', 0.01),
                "max_lot": info.get('volume_max', 100.0),
                "lot_step": info.get('volume_step', 0.01),
                "contract_size": info.get('trade_contract_size', 100.0),
                "trade_mode": info.get('trade_mode', 0)
            }
            
        except Exception as e:
            logger.error(f"[SYMBOL_INFO] Failed to get symbol info for {symbol}: {e}")
            return None
    
    async def calculate_pip_value(
        self,
        symbol: str,
        lot_size: float
    ) -> float:
        """
        Calculate pip value for a given lot size
        
        Args:
            symbol: Symbol name
            lot_size: Lot size
        
        Returns:
            Pip value in account currency
        """
        try:
            return self._pip_calculator.get_pip_value(symbol, lot_size)
        except Exception as e:
            logger.error(f"[PIP_VALUE] Error calculating pip value: {e}")
            return 0.0
    
    async def get_pip_size(self, symbol: str) -> float:
        """
        Get pip size for symbol
        
        Args:
            symbol: Symbol name
        
        Returns:
            Pip size (e.g., 0.1 for XAUUSD, 0.0001 for EURUSD)
        """
        try:
            return self._pip_calculator.get_pip_size(symbol)
        except Exception as e:
            logger.error(f"[PIP_SIZE] Error getting pip size: {e}")
            return 0.0001
    
    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached data if still valid"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            age = (datetime.now() - timestamp).total_seconds()
            if age < self._cache_ttl:
                return data
        return None
    
    def _set_cached(self, key: str, data: Dict):
        """Cache data with timestamp"""
        self._cache[key] = (data, datetime.now())
    
    def clear_cache(self):
        """Clear all cached data (call on new session)"""
        self._cache = {}
