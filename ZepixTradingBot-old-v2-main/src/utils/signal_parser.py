"""
Enhanced Signal Parser for V3 and V6 Alerts
Extracts all metadata needed for plugin routing

Part of Plan 02: Webhook Routing & Signal Processing
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SignalParser:
    """Parse TradingView alerts into standardized signal format"""
    
    # V3 Signal Types
    V3_SIGNALS = ['BUY', 'SELL', 'CLOSE', 'MODIFY_SL', 'MODIFY_TP']
    V3_LOGICS = ['LOGIC1', 'LOGIC2', 'LOGIC3']
    V3_TIMEFRAMES = {'LOGIC1': '5m', 'LOGIC2': '15m', 'LOGIC3': '1h'}
    V3_ALERT_TYPES = ['entry_v3', 'exit_v3', 'squeeze_v3', 'trend_pulse_v3']
    
    # V6 Signal Types
    V6_SIGNALS = ['TRENDLINE_BREAK', 'MOMENTUM_SHIFT', 'CONDITIONAL', 
                  'TREND_PULSE_CHANGE', 'PRICE_ACTION_ENTRY']
    V6_TIMEFRAMES = ['1m', '5m', '15m', '1h']
    V6_ALERT_TYPES = ['entry_v6', 'exit_v6', 'trendline_v6', 'momentum_v6']
    
    @classmethod
    def parse(cls, raw_alert: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse raw alert into standardized signal format.
        Returns None if alert is invalid.
        """
        try:
            # Detect strategy type
            strategy = cls._detect_strategy(raw_alert)
            if not strategy:
                logger.warning(f"Could not detect strategy from alert: {raw_alert}")
                return None
            
            # Parse based on strategy
            if strategy == 'V3_COMBINED':
                return cls._parse_v3_alert(raw_alert)
            elif strategy == 'V6_PRICE_ACTION':
                return cls._parse_v6_alert(raw_alert)
            else:
                logger.warning(f"Unknown strategy: {strategy}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to parse alert: {e}")
            return None
    
    @classmethod
    def _detect_strategy(cls, alert: Dict[str, Any]) -> Optional[str]:
        """Detect strategy type from alert content"""
        # Check alert type first (most reliable)
        alert_type = alert.get('type', '').lower()
        if alert_type in cls.V3_ALERT_TYPES or 'v3' in alert_type:
            return 'V3_COMBINED'
        if alert_type in cls.V6_ALERT_TYPES or 'v6' in alert_type:
            return 'V6_PRICE_ACTION'
        
        # Explicit strategy field
        if 'strategy' in alert:
            strategy = alert['strategy'].upper()
            if 'V3' in strategy or 'COMBINED' in strategy:
                return 'V3_COMBINED'
            elif 'V6' in strategy or 'PRICE_ACTION' in strategy:
                return 'V6_PRICE_ACTION'
            return strategy
        
        # Detect from signal type
        signal = alert.get('signal', '').upper()
        if signal in cls.V3_SIGNALS:
            return 'V3_COMBINED'
        if signal in cls.V6_SIGNALS:
            return 'V6_PRICE_ACTION'
        
        # Detect from logic field (V3 specific)
        if 'logic' in alert and alert['logic'] in cls.V3_LOGICS:
            return 'V3_COMBINED'
        
        # Detect from trend_pulse field (V6 specific)
        if 'trend_pulse' in alert:
            return 'V6_PRICE_ACTION'
        
        # Detect from consensus_score (V3 specific)
        if 'consensus_score' in alert:
            return 'V3_COMBINED'
        
        # Detect from signal_type field
        signal_type = alert.get('signal_type', '').upper()
        if signal_type in cls.V3_SIGNALS:
            return 'V3_COMBINED'
        if signal_type in cls.V6_SIGNALS:
            return 'V6_PRICE_ACTION'
        
        return None
    
    @classmethod
    def _parse_v3_alert(cls, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Parse V3 Combined alert"""
        logic = alert.get('logic', 'LOGIC1')
        timeframe = cls.V3_TIMEFRAMES.get(logic, alert.get('timeframe', '5m'))
        
        # Get signal type from various possible fields
        signal_type = (
            alert.get('signal_type') or 
            alert.get('signal') or 
            alert.get('direction') or 
            'BUY'
        ).upper()
        
        return {
            # Core fields
            'strategy': 'V3_COMBINED',
            'signal_type': signal_type,
            'symbol': alert.get('symbol', '').upper(),
            'timeframe': timeframe,
            
            # V3 specific
            'logic': logic,
            'price': float(alert.get('price', 0)) if alert.get('price') else 0,
            'sl_pips': int(alert.get('sl_pips', 15)) if alert.get('sl_pips') else 15,
            'trend': alert.get('trend', 'NEUTRAL').upper() if alert.get('trend') else 'NEUTRAL',
            'consensus_score': int(alert.get('consensus_score', 0)) if alert.get('consensus_score') else 0,
            'mtf_trends': alert.get('mtf_trends', ''),
            
            # Alert type preservation
            'type': alert.get('type', 'entry_v3'),
            
            # Metadata
            'timestamp': alert.get('timestamp', datetime.now().isoformat()),
            'raw_alert': alert,
            
            # Plugin routing hints
            'plugin_hint': 'v3_combined',
            'requires_dual_order': True,
            'requires_reentry': True,
        }
    
    @classmethod
    def _parse_v6_alert(cls, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Parse V6 Price Action alert"""
        timeframe = alert.get('timeframe', alert.get('tf', '5m'))
        
        # Normalize timeframe
        if timeframe in ['1', '1min']:
            timeframe = '1m'
        elif timeframe in ['5', '5min']:
            timeframe = '5m'
        elif timeframe in ['15', '15min']:
            timeframe = '15m'
        elif timeframe in ['60', '1hour', '1hr']:
            timeframe = '1h'
        
        # Get signal type from various possible fields
        signal_type = (
            alert.get('signal_type') or 
            alert.get('signal') or 
            'PRICE_ACTION_ENTRY'
        ).upper()
        
        return {
            # Core fields
            'strategy': 'V6_PRICE_ACTION',
            'signal_type': signal_type,
            'symbol': alert.get('symbol', '').upper(),
            'timeframe': timeframe,
            
            # V6 specific
            'trend_pulse': alert.get('trend_pulse', 'NEUTRAL'),
            'conditions': alert.get('conditions', {}),
            'price': float(alert.get('price', 0)) if alert.get('price') else 0,
            
            # Alert type preservation
            'type': alert.get('type', 'entry_v6'),
            
            # Metadata
            'timestamp': alert.get('timestamp', datetime.now().isoformat()),
            'raw_alert': alert,
            
            # Plugin routing hints
            'plugin_hint': f'v6_price_action_{timeframe}',
            'requires_dual_order': False,
            'requires_reentry': False,
        }
    
    @classmethod
    def validate(cls, signal: Dict[str, Any]) -> bool:
        """Validate parsed signal has required fields"""
        required_fields = ['strategy', 'signal_type', 'symbol', 'timeframe']
        for field in required_fields:
            if field not in signal or not signal[field]:
                logger.warning(f"Signal missing required field: {field}")
                return False
        return True
    
    @classmethod
    def get_routing_key(cls, signal: Dict[str, Any]) -> str:
        """
        Generate a routing key for the signal.
        Used for plugin lookup and logging.
        """
        strategy = signal.get('strategy', 'UNKNOWN')
        timeframe = signal.get('timeframe', 'unknown')
        return f"{strategy}:{timeframe}"
