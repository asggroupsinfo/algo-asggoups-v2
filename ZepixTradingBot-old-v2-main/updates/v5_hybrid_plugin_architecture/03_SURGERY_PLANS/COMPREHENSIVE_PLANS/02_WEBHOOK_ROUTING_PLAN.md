# PLAN 02: WEBHOOK ROUTING & SIGNAL PROCESSING

**Date:** 2026-01-15
**Priority:** P0 (Critical)
**Estimated Time:** 2-3 days
**Dependencies:** Plan 01 (Core Cleanup)

---

## 1. OBJECTIVE

Implement proper webhook-to-plugin routing so that incoming TradingView alerts are correctly parsed, validated, and routed to the appropriate plugin. After this plan, the complete signal flow will be:

```
TradingView Alert → Webhook Endpoint → Signal Parser → Plugin Router → Plugin.process_signal()
```

**Current Problem (from Study Report 04, GAP-1):**
- Webhook receives alerts but routes directly to hardcoded handlers
- No plugin-aware routing exists
- Signal parsing doesn't extract plugin-relevant metadata

**Target State:**
- Webhook extracts strategy, timeframe, and plugin hints from alert
- Router finds correct plugin using Plan 01's delegation framework
- Plugin receives fully parsed signal with all metadata

---

## 2. SCOPE

### In-Scope:
- Update webhook endpoint to extract plugin metadata
- Create signal parser for V3 and V6 alert formats
- Create plugin router that uses PluginRegistry
- Implement signal validation before routing
- Handle unknown signals gracefully
- Add routing metrics and logging

### Out-of-Scope:
- Re-entry system integration (Plan 03)
- Dual order execution (Plan 04)
- Telegram notifications (Plan 07)
- Database operations (Plan 09)

---

## 3. CURRENT STATE ANALYSIS

### File: `src/api/webhook_handler.py`

**Current Structure (from Study Report 01):**
- Lines 1-30: Imports and FastAPI setup
- Lines 31-80: `/webhook` endpoint definition
- Lines 81-120: Alert parsing (basic)
- Lines 121-180: Direct call to TradingEngine (bypasses plugins)
- Lines 181-220: Error handling

**Problem Areas:**
1. Line 95: `signal_type = alert.get('type', 'unknown')` - No strategy extraction
2. Line 110: `await trading_engine.process_signal(alert)` - Direct call, no routing
3. No timeframe extraction from alert
4. No plugin metadata in parsed signal

### File: `src/utils/signal_parser.py` (if exists)

**Current Structure:**
- Basic alert parsing
- No V3/V6 specific parsing
- No plugin hint extraction

### TradingView Alert Formats (from Pine Script docs):

**V3 Combined Alert Format:**
```json
{
  "strategy": "V3_COMBINED",
  "signal": "BUY" | "SELL" | "CLOSE",
  "symbol": "EURUSD",
  "timeframe": "5m" | "15m" | "1h",
  "logic": "LOGIC1" | "LOGIC2" | "LOGIC3",
  "price": 1.0850,
  "sl_pips": 15,
  "trend": "BULLISH" | "BEARISH",
  "timestamp": "2026-01-15T10:00:00Z"
}
```

**V6 Price Action Alert Format:**
```json
{
  "strategy": "V6_PRICE_ACTION",
  "signal": "TRENDLINE_BREAK" | "MOMENTUM_SHIFT" | "CONDITIONAL",
  "symbol": "EURUSD",
  "timeframe": "1m" | "5m" | "15m" | "1h",
  "price": 1.0850,
  "trend_pulse": "STRONG_UP" | "WEAK_UP" | "NEUTRAL" | "WEAK_DOWN" | "STRONG_DOWN",
  "conditions": {...},
  "timestamp": "2026-01-15T10:00:00Z"
}
```

---

## 4. GAPS ADDRESSED

| Gap | Description | How Addressed |
|-----|-------------|---------------|
| GAP-1 | Plugin Wiring to Core | Complete webhook → plugin routing |
| REQ-2.2 | Webhook → Plugin Routing | Implement signal router |
| REQ-2.3 | Plugin Signal Handler Registration | Plugins register supported signals |
| REQ-2.6 | Plugin Priority System | Router respects plugin priority |

---

## 5. IMPLEMENTATION STEPS

### Step 1: Create Enhanced Signal Parser

**File:** `src/utils/signal_parser.py` (CREATE or UPDATE)

**Code:**
```python
"""
Enhanced Signal Parser for V3 and V6 Alerts
Extracts all metadata needed for plugin routing
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SignalParser:
    """Parse TradingView alerts into standardized signal format"""
    
    # V3 Signal Types
    V3_SIGNALS = ['BUY', 'SELL', 'CLOSE', 'MODIFY_SL', 'MODIFY_TP']
    V3_LOGICS = ['LOGIC1', 'LOGIC2', 'LOGIC3']
    V3_TIMEFRAMES = {'LOGIC1': '5m', 'LOGIC2': '15m', 'LOGIC3': '1h'}
    
    # V6 Signal Types
    V6_SIGNALS = ['TRENDLINE_BREAK', 'MOMENTUM_SHIFT', 'CONDITIONAL', 
                  'TREND_PULSE_CHANGE', 'PRICE_ACTION_ENTRY']
    V6_TIMEFRAMES = ['1m', '5m', '15m', '1h']
    
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
        
        return None
    
    @classmethod
    def _parse_v3_alert(cls, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Parse V3 Combined alert"""
        logic = alert.get('logic', 'LOGIC1')
        timeframe = cls.V3_TIMEFRAMES.get(logic, '5m')
        
        return {
            # Core fields
            'strategy': 'V3_COMBINED',
            'signal_type': alert.get('signal', 'BUY').upper(),
            'symbol': alert.get('symbol', '').upper(),
            'timeframe': alert.get('timeframe', timeframe),
            
            # V3 specific
            'logic': logic,
            'price': float(alert.get('price', 0)),
            'sl_pips': int(alert.get('sl_pips', 15)),
            'trend': alert.get('trend', 'NEUTRAL').upper(),
            
            # Metadata
            'timestamp': alert.get('timestamp', datetime.now().isoformat()),
            'raw_alert': alert,
            
            # Plugin routing hints
            'plugin_hint': 'combined_v3',
            'requires_dual_order': True,
            'requires_reentry': True,
        }
    
    @classmethod
    def _parse_v6_alert(cls, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Parse V6 Price Action alert"""
        timeframe = alert.get('timeframe', '5m')
        
        return {
            # Core fields
            'strategy': 'V6_PRICE_ACTION',
            'signal_type': alert.get('signal', 'PRICE_ACTION_ENTRY').upper(),
            'symbol': alert.get('symbol', '').upper(),
            'timeframe': timeframe,
            
            # V6 specific
            'trend_pulse': alert.get('trend_pulse', 'NEUTRAL'),
            'conditions': alert.get('conditions', {}),
            'price': float(alert.get('price', 0)),
            
            # Metadata
            'timestamp': alert.get('timestamp', datetime.now().isoformat()),
            'raw_alert': alert,
            
            # Plugin routing hints
            'plugin_hint': f'price_action_{timeframe}',
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
```

**Reason:** Standardizes alert parsing and extracts all metadata needed for plugin routing.

---

### Step 2: Create Plugin Router

**File:** `src/core/plugin_router.py` (NEW)

**Code:**
```python
"""
Plugin Router
Routes parsed signals to appropriate plugins
"""
from typing import Dict, Any, Optional, List
import logging
from src.core.plugin_system.plugin_registry import PluginRegistry

logger = logging.getLogger(__name__)

class PluginRouter:
    """Routes signals to appropriate plugins"""
    
    def __init__(self, plugin_registry: PluginRegistry):
        self.registry = plugin_registry
        self._routing_stats = {
            'total_routed': 0,
            'successful': 0,
            'failed': 0,
            'no_plugin_found': 0
        }
    
    async def route_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Route signal to appropriate plugin and return result.
        
        Routing priority:
        1. Explicit plugin_hint in signal
        2. Strategy + timeframe match
        3. Strategy-only match
        4. Broadcast to all capable plugins (shadow mode)
        """
        self._routing_stats['total_routed'] += 1
        
        # Try explicit plugin hint first
        plugin_hint = signal.get('plugin_hint')
        if plugin_hint:
            plugin = self.registry.get_plugin(plugin_hint)
            if plugin and plugin.enabled:
                logger.info(f"Routing to hinted plugin: {plugin_hint}")
                return await self._execute_plugin(plugin, signal)
        
        # Try strategy + timeframe match
        plugin = self.registry.get_plugin_for_signal(signal)
        if plugin:
            logger.info(f"Routing to matched plugin: {plugin.plugin_id}")
            return await self._execute_plugin(plugin, signal)
        
        # No plugin found
        self._routing_stats['no_plugin_found'] += 1
        logger.warning(f"No plugin found for signal: {signal.get('strategy')}/{signal.get('timeframe')}")
        return None
    
    async def _execute_plugin(self, plugin, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute plugin and track result"""
        try:
            result = await plugin.process_signal(signal)
            self._routing_stats['successful'] += 1
            return result
        except Exception as e:
            self._routing_stats['failed'] += 1
            logger.error(f"Plugin {plugin.plugin_id} failed: {e}")
            return None
    
    async def broadcast_signal(self, signal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Broadcast signal to ALL capable plugins.
        Used for shadow mode comparison.
        """
        results = []
        matching_plugins = self.registry.broadcast_signal(signal)
        
        for plugin in matching_plugins:
            try:
                result = await plugin.process_signal(signal)
                results.append({
                    'plugin_id': plugin.plugin_id,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'plugin_id': plugin.plugin_id,
                    'error': str(e)
                })
        
        return results
    
    def get_routing_stats(self) -> Dict[str, int]:
        """Return routing statistics"""
        return self._routing_stats.copy()
    
    def reset_stats(self):
        """Reset routing statistics"""
        self._routing_stats = {
            'total_routed': 0,
            'successful': 0,
            'failed': 0,
            'no_plugin_found': 0
        }
```

**Reason:** Centralizes routing logic and provides statistics for monitoring.

---

### Step 3: Update Webhook Handler

**File:** `src/api/webhook_handler.py`

**Changes:**
```python
# ADD imports
from src.utils.signal_parser import SignalParser
from src.core.plugin_router import PluginRouter

# UPDATE webhook endpoint
@app.post("/webhook")
async def webhook_endpoint(request: Request):
    """
    Receive TradingView alerts and route to appropriate plugin.
    
    Flow:
    1. Receive raw alert
    2. Parse into standardized signal
    3. Validate signal
    4. Route to plugin
    5. Return result
    """
    try:
        # Get raw alert
        raw_alert = await request.json()
        logger.info(f"Received webhook alert: {raw_alert.get('strategy', 'unknown')}")
        
        # Parse alert
        signal = SignalParser.parse(raw_alert)
        if not signal:
            logger.warning("Failed to parse alert")
            return {"status": "error", "message": "Invalid alert format"}
        
        # Validate signal
        if not SignalParser.validate(signal):
            logger.warning("Signal validation failed")
            return {"status": "error", "message": "Signal validation failed"}
        
        # Route to plugin
        router = get_plugin_router()  # Singleton
        result = await router.route_signal(signal)
        
        if result:
            logger.info(f"Signal processed successfully: {result.get('status', 'unknown')}")
            return {"status": "success", "result": result}
        else:
            logger.warning("No plugin processed the signal")
            return {"status": "warning", "message": "No plugin available for this signal"}
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

# ADD singleton getter
_plugin_router = None

def get_plugin_router() -> PluginRouter:
    """Get or create PluginRouter singleton"""
    global _plugin_router
    if _plugin_router is None:
        from src.core.plugin_system.plugin_registry import PluginRegistry
        registry = PluginRegistry.get_instance()  # Assuming singleton
        _plugin_router = PluginRouter(registry)
    return _plugin_router
```

**Reason:** Updates webhook to use the new parsing and routing system.

---

### Step 4: Add Signal Validation Middleware

**File:** `src/api/middleware/signal_validator.py` (NEW)

**Code:**
```python
"""
Signal Validation Middleware
Validates signals before routing to plugins
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SignalValidator:
    """Validates trading signals"""
    
    # Valid symbols (from bot config)
    VALID_SYMBOLS = [
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD',
        'NZDUSD', 'EURGBP', 'EURJPY', 'GBPJPY', 'XAUUSD', 'XAGUSD'
    ]
    
    # Valid timeframes
    VALID_TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d']
    
    # Valid signal types per strategy
    VALID_SIGNALS = {
        'V3_COMBINED': ['BUY', 'SELL', 'CLOSE', 'MODIFY_SL', 'MODIFY_TP'],
        'V6_PRICE_ACTION': ['TRENDLINE_BREAK', 'MOMENTUM_SHIFT', 'CONDITIONAL',
                           'TREND_PULSE_CHANGE', 'PRICE_ACTION_ENTRY']
    }
    
    @classmethod
    def validate(cls, signal: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate signal and return (is_valid, errors).
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
                if price <= 0:
                    errors.append(f"Invalid price: {price}")
            except (ValueError, TypeError):
                errors.append(f"Price must be a number")
        
        return len(errors) == 0, errors
    
    @classmethod
    def sanitize(cls, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize signal values"""
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
            sanitized['price'] = float(sanitized['price'])
        if 'sl_pips' in sanitized:
            sanitized['sl_pips'] = int(sanitized['sl_pips'])
        
        return sanitized
```

**Reason:** Ensures only valid signals reach plugins, preventing errors.

---

### Step 5: Add Routing Metrics Endpoint

**File:** `src/api/webhook_handler.py`

**Add Endpoint:**
```python
@app.get("/routing/stats")
async def routing_stats():
    """Get plugin routing statistics"""
    router = get_plugin_router()
    stats = router.get_routing_stats()
    
    return {
        "status": "success",
        "stats": stats,
        "success_rate": (stats['successful'] / stats['total_routed'] * 100) 
                        if stats['total_routed'] > 0 else 0
    }

@app.post("/routing/reset")
async def reset_routing_stats():
    """Reset routing statistics"""
    router = get_plugin_router()
    router.reset_stats()
    return {"status": "success", "message": "Stats reset"}

@app.get("/routing/plugins")
async def list_routing_plugins():
    """List all plugins available for routing"""
    from src.core.plugin_system.plugin_registry import PluginRegistry
    registry = PluginRegistry.get_instance()
    
    plugins = []
    for plugin_id, plugin in registry._plugins.items():
        plugins.append({
            'plugin_id': plugin_id,
            'enabled': plugin.enabled,
            'strategies': plugin.get_supported_strategies() if hasattr(plugin, 'get_supported_strategies') else [],
            'timeframes': plugin.get_supported_timeframes() if hasattr(plugin, 'get_supported_timeframes') else []
        })
    
    return {"status": "success", "plugins": plugins}
```

**Reason:** Provides visibility into routing behavior for debugging and monitoring.

---

### Step 6: Create Webhook Routing Tests

**File:** `tests/test_webhook_routing.py` (NEW)

**Code:**
```python
"""
Tests for Webhook Routing
Verifies signals are correctly parsed and routed to plugins
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from src.api.webhook_handler import app
from src.utils.signal_parser import SignalParser
from src.core.plugin_router import PluginRouter

class TestSignalParser:
    """Test signal parsing"""
    
    def test_parse_v3_alert(self):
        """Test V3 alert parsing"""
        alert = {
            'strategy': 'V3_COMBINED',
            'signal': 'BUY',
            'symbol': 'EURUSD',
            'logic': 'LOGIC1',
            'price': 1.0850,
            'sl_pips': 15,
            'trend': 'BULLISH'
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['strategy'] == 'V3_COMBINED'
        assert signal['signal_type'] == 'BUY'
        assert signal['symbol'] == 'EURUSD'
        assert signal['timeframe'] == '5m'  # LOGIC1 = 5m
        assert signal['plugin_hint'] == 'combined_v3'
        assert signal['requires_dual_order'] == True
    
    def test_parse_v6_alert(self):
        """Test V6 alert parsing"""
        alert = {
            'strategy': 'V6_PRICE_ACTION',
            'signal': 'TRENDLINE_BREAK',
            'symbol': 'GBPUSD',
            'timeframe': '15m',
            'trend_pulse': 'STRONG_UP',
            'price': 1.2650
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['strategy'] == 'V6_PRICE_ACTION'
        assert signal['signal_type'] == 'TRENDLINE_BREAK'
        assert signal['symbol'] == 'GBPUSD'
        assert signal['timeframe'] == '15m'
        assert signal['plugin_hint'] == 'price_action_15m'
        assert signal['requires_dual_order'] == False
    
    def test_detect_v3_from_logic(self):
        """Test V3 detection from logic field"""
        alert = {
            'signal': 'BUY',
            'symbol': 'EURUSD',
            'logic': 'LOGIC2'
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['strategy'] == 'V3_COMBINED'
        assert signal['timeframe'] == '15m'  # LOGIC2 = 15m
    
    def test_detect_v6_from_trend_pulse(self):
        """Test V6 detection from trend_pulse field"""
        alert = {
            'signal': 'PRICE_ACTION_ENTRY',
            'symbol': 'EURUSD',
            'timeframe': '1m',
            'trend_pulse': 'WEAK_DOWN'
        }
        
        signal = SignalParser.parse(alert)
        
        assert signal is not None
        assert signal['strategy'] == 'V6_PRICE_ACTION'
    
    def test_invalid_alert_returns_none(self):
        """Test invalid alert returns None"""
        alert = {'random': 'data'}
        
        signal = SignalParser.parse(alert)
        
        assert signal is None

class TestPluginRouter:
    """Test plugin routing"""
    
    @pytest.fixture
    def mock_registry(self):
        """Create mock registry"""
        registry = MagicMock()
        return registry
    
    @pytest.fixture
    def router(self, mock_registry):
        """Create router with mock registry"""
        return PluginRouter(mock_registry)
    
    @pytest.mark.asyncio
    async def test_route_by_plugin_hint(self, router, mock_registry):
        """Test routing by explicit plugin hint"""
        mock_plugin = MagicMock()
        mock_plugin.enabled = True
        mock_plugin.process_signal = AsyncMock(return_value={'status': 'success'})
        mock_registry.get_plugin.return_value = mock_plugin
        
        signal = {'strategy': 'V3_COMBINED', 'plugin_hint': 'combined_v3'}
        result = await router.route_signal(signal)
        
        mock_registry.get_plugin.assert_called_with('combined_v3')
        mock_plugin.process_signal.assert_called_once_with(signal)
        assert result == {'status': 'success'}
    
    @pytest.mark.asyncio
    async def test_route_by_strategy_match(self, router, mock_registry):
        """Test routing by strategy match"""
        mock_plugin = MagicMock()
        mock_plugin.plugin_id = 'combined_v3'
        mock_plugin.process_signal = AsyncMock(return_value={'status': 'success'})
        mock_registry.get_plugin.return_value = None  # No hint match
        mock_registry.get_plugin_for_signal.return_value = mock_plugin
        
        signal = {'strategy': 'V3_COMBINED', 'timeframe': '5m'}
        result = await router.route_signal(signal)
        
        mock_registry.get_plugin_for_signal.assert_called_with(signal)
        assert result == {'status': 'success'}
    
    @pytest.mark.asyncio
    async def test_no_plugin_found(self, router, mock_registry):
        """Test handling when no plugin found"""
        mock_registry.get_plugin.return_value = None
        mock_registry.get_plugin_for_signal.return_value = None
        
        signal = {'strategy': 'UNKNOWN'}
        result = await router.route_signal(signal)
        
        assert result is None
        assert router.get_routing_stats()['no_plugin_found'] == 1

class TestWebhookEndpoint:
    """Test webhook endpoint integration"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_webhook_v3_signal(self, client):
        """Test V3 signal through webhook"""
        with patch('src.api.webhook_handler.get_plugin_router') as mock_get_router:
            mock_router = MagicMock()
            mock_router.route_signal = AsyncMock(return_value={'status': 'executed'})
            mock_get_router.return_value = mock_router
            
            response = client.post("/webhook", json={
                'strategy': 'V3_COMBINED',
                'signal': 'BUY',
                'symbol': 'EURUSD',
                'logic': 'LOGIC1'
            })
            
            assert response.status_code == 200
            assert response.json()['status'] == 'success'
    
    def test_webhook_invalid_alert(self, client):
        """Test invalid alert handling"""
        response = client.post("/webhook", json={
            'random': 'data'
        })
        
        assert response.status_code == 200
        assert response.json()['status'] == 'error'
```

**Reason:** Verifies the complete webhook → plugin routing flow.

---

## 6. DEPENDENCIES

### Prerequisites:
- Plan 01 (Core Cleanup) - Provides plugin delegation framework
- PluginRegistry with `get_plugin_for_signal()` method

### Blocks:
- Plan 03 (Re-Entry) - Needs signal routing to work
- Plan 04 (Dual Orders) - Needs signal routing to work
- All feature plans depend on signals reaching plugins

---

## 7. FILES AFFECTED

| File | Action | Description |
|------|--------|-------------|
| `src/utils/signal_parser.py` | CREATE/UPDATE | Enhanced signal parsing |
| `src/core/plugin_router.py` | CREATE | New routing logic |
| `src/api/webhook_handler.py` | MODIFY | Use new parser and router |
| `src/api/middleware/signal_validator.py` | CREATE | Signal validation |
| `tests/test_webhook_routing.py` | CREATE | Routing tests |

---

## 8. TESTING STRATEGY

### Unit Tests:
1. Test V3 alert parsing extracts all fields
2. Test V6 alert parsing extracts all fields
3. Test strategy detection from various alert formats
4. Test routing by plugin hint
5. Test routing by strategy match
6. Test routing stats tracking

### Integration Tests:
1. Send V3 webhook → verify V3 plugin receives signal
2. Send V6 webhook → verify correct V6 plugin receives signal
3. Send invalid webhook → verify error response

### Manual Verification:
1. Start bot with logging
2. Send curl request to webhook:
   ```bash
   curl -X POST http://localhost:8000/webhook \
     -H "Content-Type: application/json" \
     -d '{"strategy": "V3_COMBINED", "signal": "BUY", "symbol": "EURUSD", "logic": "LOGIC1"}'
   ```
3. Verify logs show:
   - "Received webhook alert: V3_COMBINED"
   - "Routing to matched plugin: combined_v3"
   - Plugin's process_signal called

---

## 9. ROLLBACK PLAN

### If Routing Fails:
1. Revert webhook_handler.py to direct TradingEngine calls
2. Keep SignalParser for future use
3. Disable PluginRouter

### Rollback Steps:
```bash
# Revert webhook handler
git checkout HEAD~1 -- src/api/webhook_handler.py
```

### Feature Flag:
```python
# In webhook_handler.py
USE_PLUGIN_ROUTING = config.get('use_plugin_routing', True)

if USE_PLUGIN_ROUTING:
    result = await router.route_signal(signal)
else:
    result = await trading_engine.process_signal(raw_alert)  # Legacy
```

---

## 10. SUCCESS CRITERIA

This plan is COMPLETE when:

1. ✅ SignalParser correctly parses V3 and V6 alerts
2. ✅ PluginRouter routes signals to correct plugins
3. ✅ Webhook endpoint uses new parser and router
4. ✅ Routing stats endpoint works
5. ✅ All unit tests pass
6. ✅ Manual curl test shows signal reaching plugin
7. ✅ No regression in existing functionality

---

## 11. REFERENCES

- **Study Report 01:** Section 1.4 (Signal Processing)
- **Study Report 04:** GAP-1 (Plugin Wiring), REQ-2.2, REQ-2.3
- **Original Surgery Plan:** `03_SURGERY_PLANS/02_PLUGIN_WIRING_PLAN.md`
- **Planning Doc:** `01_PLANNING/03_WEBHOOK_INTEGRATION.md`
- **Pine Script Docs:** V3 and V6 alert formats

---

**END OF PLAN 02**
