"""
Signal Validation Middleware
Validates signals before routing to plugins

Part of Plan 02: Webhook Routing & Signal Processing
"""
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class SignalValidator:
    """Validates trading signals"""
    
    # Valid symbols (from bot config)
    VALID_SYMBOLS = [
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD',
        'NZDUSD', 'EURGBP', 'EURJPY', 'GBPJPY', 'XAUUSD', 'XAGUSD',
        'AUDJPY', 'CADJPY', 'CHFJPY', 'NZDJPY', 'EURAUD', 'GBPAUD'
    ]
    
    # Valid timeframes
    VALID_TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d']
    
    # Valid signal types per strategy
    VALID_SIGNALS = {
        'V3_COMBINED': ['BUY', 'SELL', 'CLOSE', 'MODIFY_SL', 'MODIFY_TP'],
        'V6_PRICE_ACTION': ['TRENDLINE_BREAK', 'MOMENTUM_SHIFT', 'CONDITIONAL',
                           'TREND_PULSE_CHANGE', 'PRICE_ACTION_ENTRY', 'BUY', 'SELL']
    }
    
    # Valid alert types
    VALID_ALERT_TYPES = {
        'V3_COMBINED': ['entry_v3', 'exit_v3', 'squeeze_v3', 'trend_pulse_v3'],
        'V6_PRICE_ACTION': ['entry_v6', 'exit_v6', 'trendline_v6', 'momentum_v6']
    }
    
    @classmethod
    def validate(cls, signal: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate signal and return (is_valid, errors).
        
        Args:
            signal: Parsed signal dictionary
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check required fields
        required = ['strategy', 'signal_type', 'symbol', 'timeframe']
        for field in required:
            if field not in signal:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate symbol
        symbol = signal['symbol'].upper()
        if symbol not in cls.VALID_SYMBOLS:
            errors.append(f"Invalid symbol: {symbol}")
        
        # Validate timeframe
        timeframe = signal['timeframe']
        if timeframe not in cls.VALID_TIMEFRAMES:
            errors.append(f"Invalid timeframe: {timeframe}")
        
        # Validate signal type for strategy
        strategy = signal['strategy']
        signal_type = signal['signal_type']
        if strategy in cls.VALID_SIGNALS:
            if signal_type not in cls.VALID_SIGNALS[strategy]:
                errors.append(f"Invalid signal type {signal_type} for strategy {strategy}")
        
        # Validate price if present
        if 'price' in signal:
            try:
                price = float(signal['price'])
                if price < 0:
                    errors.append(f"Invalid price: {price}")
            except (ValueError, TypeError):
                errors.append("Price must be a number")
        
        # Validate consensus_score for V3
        if strategy == 'V3_COMBINED' and 'consensus_score' in signal:
            try:
                score = int(signal['consensus_score'])
                if score < 0 or score > 10:
                    errors.append(f"Invalid consensus_score: {score} (must be 0-10)")
            except (ValueError, TypeError):
                errors.append("consensus_score must be an integer")
        
        # Validate sl_pips for V3
        if strategy == 'V3_COMBINED' and 'sl_pips' in signal:
            try:
                sl_pips = int(signal['sl_pips'])
                if sl_pips < 0 or sl_pips > 500:
                    errors.append(f"Invalid sl_pips: {sl_pips} (must be 0-500)")
            except (ValueError, TypeError):
                errors.append("sl_pips must be an integer")
        
        return len(errors) == 0, errors
    
    @classmethod
    def sanitize(cls, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize signal values.
        
        Args:
            signal: Signal dictionary to sanitize
            
        Returns:
            Sanitized signal dictionary
        """
        sanitized = signal.copy()
        
        # Uppercase string fields
        if 'symbol' in sanitized:
            sanitized['symbol'] = sanitized['symbol'].upper()
        if 'signal_type' in sanitized:
            sanitized['signal_type'] = sanitized['signal_type'].upper()
        if 'strategy' in sanitized:
            sanitized['strategy'] = sanitized['strategy'].upper()
        if 'trend' in sanitized:
            sanitized['trend'] = sanitized['trend'].upper()
        
        # Ensure numeric fields
        if 'price' in sanitized:
            try:
                sanitized['price'] = float(sanitized['price'])
            except (ValueError, TypeError):
                sanitized['price'] = 0.0
                
        if 'sl_pips' in sanitized:
            try:
                sanitized['sl_pips'] = int(sanitized['sl_pips'])
            except (ValueError, TypeError):
                sanitized['sl_pips'] = 15
                
        if 'consensus_score' in sanitized:
            try:
                sanitized['consensus_score'] = int(sanitized['consensus_score'])
            except (ValueError, TypeError):
                sanitized['consensus_score'] = 0
        
        return sanitized
    
    @classmethod
    def validate_and_sanitize(cls, signal: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Validate and sanitize signal in one call.
        
        Args:
            signal: Signal dictionary
            
        Returns:
            Tuple of (is_valid, sanitized_signal, errors)
        """
        sanitized = cls.sanitize(signal)
        is_valid, errors = cls.validate(sanitized)
        return is_valid, sanitized, errors
    
    @classmethod
    def is_valid_symbol(cls, symbol: str) -> bool:
        """
        Check if symbol is valid.
        
        Args:
            symbol: Symbol to check
            
        Returns:
            True if valid, False otherwise
        """
        return symbol.upper() in cls.VALID_SYMBOLS
    
    @classmethod
    def is_valid_timeframe(cls, timeframe: str) -> bool:
        """
        Check if timeframe is valid.
        
        Args:
            timeframe: Timeframe to check
            
        Returns:
            True if valid, False otherwise
        """
        return timeframe in cls.VALID_TIMEFRAMES
    
    @classmethod
    def get_valid_symbols(cls) -> List[str]:
        """Get list of valid symbols"""
        return cls.VALID_SYMBOLS.copy()
    
    @classmethod
    def get_valid_timeframes(cls) -> List[str]:
        """Get list of valid timeframes"""
        return cls.VALID_TIMEFRAMES.copy()
    
    @classmethod
    def add_valid_symbol(cls, symbol: str) -> None:
        """
        Add a symbol to the valid symbols list.
        
        Args:
            symbol: Symbol to add
        """
        symbol = symbol.upper()
        if symbol not in cls.VALID_SYMBOLS:
            cls.VALID_SYMBOLS.append(symbol)
            logger.info(f"Added valid symbol: {symbol}")
