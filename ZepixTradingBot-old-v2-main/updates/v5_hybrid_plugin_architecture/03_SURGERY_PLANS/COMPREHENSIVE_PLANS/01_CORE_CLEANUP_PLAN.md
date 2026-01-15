# PLAN 01: CORE CLEANUP & PLUGIN DELEGATION

**Date:** 2026-01-15
**Priority:** P0 (Critical)
**Estimated Time:** 3-4 days
**Dependencies:** None (First Plan)

---

## 1. OBJECTIVE

Remove ALL hardcoded V3/V6 trading logic from `trading_engine.py` and establish a clean plugin delegation framework. After this plan, the TradingEngine will be a thin orchestrator that delegates ALL trading decisions to registered plugins.

**Current Problem (from Study Report 04, GAP-1):**
```python
# trading_engine.py Line 232 - THE SMOKING GUN
async def process_signal(self, signal_data):
    # HARDCODED V3 LOGIC - Plugins are NEVER called!
    if signal_data.get('strategy') == 'V3_COMBINED':
        await self._process_v3_signal(signal_data)  # Direct processing
    elif signal_data.get('strategy') == 'V6_PRICE_ACTION':
        await self._process_v6_signal(signal_data)  # Direct processing
```

**Target State:**
```python
# trading_engine.py - AFTER SURGERY
async def process_signal(self, signal_data):
    # DELEGATE TO PLUGINS - No hardcoded logic!
    plugin = self.plugin_registry.get_plugin_for_signal(signal_data)
    if plugin:
        await plugin.process_signal(signal_data)
    else:
        logger.warning(f"No plugin registered for signal: {signal_data}")
```

---

## 2. SCOPE

### In-Scope:
- Remove hardcoded V3 logic from `trading_engine.py`
- Remove hardcoded V6 logic from `trading_engine.py`
- Create plugin delegation methods in TradingEngine
- Update PluginRegistry to support signal-based plugin lookup
- Create plugin interface for signal processing
- Preserve ALL existing functionality (via plugins)

### Out-of-Scope:
- Webhook routing (Plan 02)
- Re-entry system integration (Plan 03)
- Dual order system integration (Plan 04)
- Telegram integration (Plan 07)
- Database changes (Plan 09)

---

## 3. CURRENT STATE ANALYSIS

### File: `src/core/trading_engine.py`

**Current Structure (from Study Report 01):**
- Lines 1-50: Imports and class definition
- Lines 51-100: Initialization with hardcoded manager references
- Lines 101-200: Signal processing with hardcoded strategy detection
- Lines 201-300: V3-specific processing methods
- Lines 301-400: V6-specific processing methods
- Lines 401-500: Order execution (calls managers directly)
- Lines 501-600: Position management
- Lines 601-700: Error handling and cleanup

**Hardcoded Logic Locations:**
1. `_process_v3_signal()` - Lines 201-250
2. `_process_v6_signal()` - Lines 301-350
3. `_execute_v3_order()` - Lines 251-280
4. `_execute_v6_order()` - Lines 351-380
5. Strategy detection in `process_signal()` - Lines 232-245

### File: `src/core/plugin_system/plugin_registry.py`

**Current Structure:**
- Plugin registration works
- Plugin lifecycle management works
- **MISSING:** Signal-based plugin lookup
- **MISSING:** Plugin delegation interface

### File: `src/logic_plugins/combined_v3/plugin.py`

**Current Structure:**
- Plugin class exists
- `process_signal()` method exists
- **PROBLEM:** Never called by TradingEngine

---

## 4. GAPS ADDRESSED

| Gap | Description | How Addressed |
|-----|-------------|---------------|
| GAP-1 | Plugin Wiring to Core | Create delegation framework in TradingEngine |

**Partial Resolution:** This plan creates the delegation framework. Plan 02 completes the wiring with webhook routing.

---

## 5. IMPLEMENTATION STEPS

### Step 1: Create Plugin Delegation Interface

**File:** `src/core/plugin_system/plugin_interface.py` (NEW)

**Code:**
```python
"""
Plugin Interface for Signal Processing
Defines the contract between TradingEngine and Plugins
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class ISignalProcessor(ABC):
    """Interface for plugins that process trading signals"""
    
    @abstractmethod
    async def can_process_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Check if this plugin can process the given signal"""
        pass
    
    @abstractmethod
    async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process the signal and return result"""
        pass
    
    @abstractmethod
    def get_supported_strategies(self) -> List[str]:
        """Return list of strategy names this plugin supports"""
        pass
    
    @abstractmethod
    def get_supported_timeframes(self) -> List[str]:
        """Return list of timeframes this plugin supports"""
        pass

class IOrderExecutor(ABC):
    """Interface for plugins that execute orders"""
    
    @abstractmethod
    async def execute_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an order and return result"""
        pass
    
    @abstractmethod
    async def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> bool:
        """Modify an existing order"""
        pass
    
    @abstractmethod
    async def close_order(self, order_id: str, reason: str) -> bool:
        """Close an existing order"""
        pass
```

**Reason:** Defines clear contract for plugin-core communication. All plugins must implement these interfaces.

---

### Step 2: Update Plugin Registry for Signal Lookup

**File:** `src/core/plugin_system/plugin_registry.py`

**Changes:**
```python
# ADD to PluginRegistry class

def get_plugin_for_signal(self, signal_data: Dict[str, Any]) -> Optional[BaseLogicPlugin]:
    """
    Find the appropriate plugin for a given signal.
    Uses strategy name and timeframe to match.
    """
    strategy = signal_data.get('strategy', '')
    timeframe = signal_data.get('timeframe', '')
    
    for plugin_id, plugin in self._plugins.items():
        if not plugin.enabled:
            continue
        
        # Check if plugin supports this strategy
        if hasattr(plugin, 'get_supported_strategies'):
            supported_strategies = plugin.get_supported_strategies()
            if strategy in supported_strategies:
                # Check timeframe if specified
                if timeframe and hasattr(plugin, 'get_supported_timeframes'):
                    supported_timeframes = plugin.get_supported_timeframes()
                    if timeframe in supported_timeframes:
                        return plugin
                else:
                    return plugin
    
    return None

def get_plugins_by_priority(self) -> List[BaseLogicPlugin]:
    """
    Return all enabled plugins sorted by priority.
    Higher priority plugins are returned first.
    """
    enabled_plugins = [p for p in self._plugins.values() if p.enabled]
    return sorted(enabled_plugins, key=lambda p: getattr(p, 'priority', 0), reverse=True)

def broadcast_signal(self, signal_data: Dict[str, Any]) -> List[BaseLogicPlugin]:
    """
    Find ALL plugins that can process a signal.
    Used for shadow mode comparison.
    """
    matching_plugins = []
    for plugin_id, plugin in self._plugins.items():
        if not plugin.enabled:
            continue
        if hasattr(plugin, 'can_process_signal'):
            if plugin.can_process_signal(signal_data):
                matching_plugins.append(plugin)
    return matching_plugins
```

**Reason:** Enables TradingEngine to find the right plugin for each signal without hardcoding.

---

### Step 3: Create TradingEngine Delegation Methods

**File:** `src/core/trading_engine.py`

**Changes - Add New Methods:**
```python
# ADD to TradingEngine class

async def delegate_to_plugin(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Delegate signal processing to the appropriate plugin.
    This is the ONLY entry point for signal processing.
    """
    # Find the right plugin
    plugin = self.plugin_registry.get_plugin_for_signal(signal_data)
    
    if not plugin:
        logger.warning(f"No plugin found for signal: {signal_data.get('strategy', 'unknown')}")
        return None
    
    # Log delegation
    logger.info(f"Delegating signal to plugin: {plugin.plugin_id}")
    
    # Process signal through plugin
    try:
        result = await plugin.process_signal(signal_data)
        
        # Track metrics
        self._track_plugin_execution(plugin.plugin_id, signal_data, result)
        
        return result
    except Exception as e:
        logger.error(f"Plugin {plugin.plugin_id} failed to process signal: {e}")
        self._handle_plugin_failure(plugin.plugin_id, e)
        return None

def _track_plugin_execution(self, plugin_id: str, signal_data: Dict, result: Optional[Dict]):
    """Track plugin execution for metrics and debugging"""
    execution_record = {
        'plugin_id': plugin_id,
        'signal': signal_data,
        'result': result,
        'timestamp': datetime.now().isoformat()
    }
    # Store in memory for recent executions
    if not hasattr(self, '_execution_history'):
        self._execution_history = []
    self._execution_history.append(execution_record)
    # Keep only last 100 executions
    if len(self._execution_history) > 100:
        self._execution_history = self._execution_history[-100:]

def _handle_plugin_failure(self, plugin_id: str, error: Exception):
    """Handle plugin failure - log, notify, potentially disable"""
    logger.error(f"Plugin failure: {plugin_id} - {error}")
    # Increment failure counter
    if not hasattr(self, '_plugin_failures'):
        self._plugin_failures = {}
    self._plugin_failures[plugin_id] = self._plugin_failures.get(plugin_id, 0) + 1
    
    # If too many failures, disable plugin
    if self._plugin_failures[plugin_id] >= 5:
        logger.critical(f"Disabling plugin {plugin_id} due to repeated failures")
        plugin = self.plugin_registry.get_plugin(plugin_id)
        if plugin:
            plugin.enabled = False
```

**Reason:** Creates clean delegation path from TradingEngine to plugins.

---

### Step 4: Remove Hardcoded V3 Logic

**File:** `src/core/trading_engine.py`

**Changes - Modify process_signal():**
```python
# BEFORE (hardcoded):
async def process_signal(self, signal_data):
    if signal_data.get('strategy') == 'V3_COMBINED':
        await self._process_v3_signal(signal_data)
    elif signal_data.get('strategy') == 'V6_PRICE_ACTION':
        await self._process_v6_signal(signal_data)

# AFTER (delegated):
async def process_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process incoming signal by delegating to appropriate plugin.
    NO hardcoded strategy logic - all handled by plugins.
    """
    # Validate signal
    if not self._validate_signal(signal_data):
        logger.warning(f"Invalid signal received: {signal_data}")
        return None
    
    # Check if trading is enabled
    if not self.trading_enabled:
        logger.info("Trading disabled, ignoring signal")
        return None
    
    # DELEGATE TO PLUGIN - No hardcoded logic!
    result = await self.delegate_to_plugin(signal_data)
    
    return result
```

**Reason:** Removes the hardcoded strategy detection that bypasses plugins.

---

### Step 5: Remove Hardcoded V3 Processing Methods

**File:** `src/core/trading_engine.py`

**Changes - Mark as Deprecated:**
```python
# BEFORE:
async def _process_v3_signal(self, signal_data):
    # 50 lines of V3-specific logic
    ...

# AFTER:
@deprecated("Use plugin delegation instead - see combined_v3 plugin")
async def _process_v3_signal(self, signal_data):
    """
    DEPRECATED: This method is kept for backward compatibility only.
    All V3 signal processing should go through the combined_v3 plugin.
    """
    logger.warning("DEPRECATED: _process_v3_signal called directly. Use plugin delegation.")
    # Redirect to plugin
    return await self.delegate_to_plugin(signal_data)
```

**Reason:** Maintains backward compatibility while redirecting to plugin system.

---

### Step 6: Remove Hardcoded V6 Processing Methods

**File:** `src/core/trading_engine.py`

**Changes - Mark as Deprecated:**
```python
# BEFORE:
async def _process_v6_signal(self, signal_data):
    # 50 lines of V6-specific logic
    ...

# AFTER:
@deprecated("Use plugin delegation instead - see price_action plugins")
async def _process_v6_signal(self, signal_data):
    """
    DEPRECATED: This method is kept for backward compatibility only.
    All V6 signal processing should go through the price_action plugins.
    """
    logger.warning("DEPRECATED: _process_v6_signal called directly. Use plugin delegation.")
    # Redirect to plugin
    return await self.delegate_to_plugin(signal_data)
```

**Reason:** Maintains backward compatibility while redirecting to plugin system.

---

### Step 7: Update Combined V3 Plugin to Implement Interface

**File:** `src/logic_plugins/combined_v3/plugin.py`

**Changes:**
```python
# ADD imports
from src.core.plugin_system.plugin_interface import ISignalProcessor, IOrderExecutor

# UPDATE class definition
class CombinedV3Plugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    Combined V3 Logic Plugin
    Handles all V3 trading signals (LOGIC1, LOGIC2, LOGIC3)
    """
    
    def get_supported_strategies(self) -> List[str]:
        """Return strategies this plugin handles"""
        return ['V3_COMBINED', 'COMBINED_V3', 'V3']
    
    def get_supported_timeframes(self) -> List[str]:
        """Return timeframes this plugin handles"""
        return ['5m', '15m', '1h']  # LOGIC1, LOGIC2, LOGIC3
    
    async def can_process_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Check if this plugin can process the signal"""
        strategy = signal_data.get('strategy', '')
        return strategy in self.get_supported_strategies()
```

**Reason:** Makes V3 plugin discoverable by the new delegation system.

---

### Step 8: Update V6 Plugins to Implement Interface

**Files:** 
- `src/logic_plugins/price_action_1m/plugin.py`
- `src/logic_plugins/price_action_5m/plugin.py`
- `src/logic_plugins/price_action_15m/plugin.py`
- `src/logic_plugins/price_action_1h/plugin.py`

**Changes (same pattern for all):**
```python
# ADD imports
from src.core.plugin_system.plugin_interface import ISignalProcessor, IOrderExecutor

# UPDATE class definition
class PriceAction1mPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor):
    """
    V6 Price Action 1M Plugin
    Handles 1-minute timeframe price action signals
    """
    
    def get_supported_strategies(self) -> List[str]:
        """Return strategies this plugin handles"""
        return ['V6_PRICE_ACTION', 'PRICE_ACTION', 'V6']
    
    def get_supported_timeframes(self) -> List[str]:
        """Return timeframes this plugin handles"""
        return ['1m']
    
    async def can_process_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Check if this plugin can process the signal"""
        strategy = signal_data.get('strategy', '')
        timeframe = signal_data.get('timeframe', '')
        return strategy in self.get_supported_strategies() and timeframe == '1m'
```

**Reason:** Makes V6 plugins discoverable by the new delegation system.

---

### Step 9: Create Delegation Tests

**File:** `tests/test_core_delegation.py` (NEW)

**Code:**
```python
"""
Tests for Core Delegation Framework
Verifies TradingEngine properly delegates to plugins
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.trading_engine import TradingEngine
from src.core.plugin_system.plugin_registry import PluginRegistry

class TestCoreDelegation:
    """Test suite for core delegation"""
    
    @pytest.fixture
    def trading_engine(self):
        """Create TradingEngine with mocked dependencies"""
        engine = TradingEngine()
        engine.plugin_registry = MagicMock(spec=PluginRegistry)
        engine.trading_enabled = True
        return engine
    
    @pytest.fixture
    def mock_plugin(self):
        """Create mock plugin"""
        plugin = MagicMock()
        plugin.plugin_id = 'test_plugin'
        plugin.enabled = True
        plugin.process_signal = AsyncMock(return_value={'status': 'success'})
        return plugin
    
    @pytest.mark.asyncio
    async def test_signal_delegated_to_plugin(self, trading_engine, mock_plugin):
        """Test that signals are delegated to plugins"""
        trading_engine.plugin_registry.get_plugin_for_signal.return_value = mock_plugin
        
        signal = {'strategy': 'V3_COMBINED', 'symbol': 'EURUSD'}
        result = await trading_engine.process_signal(signal)
        
        # Verify delegation
        trading_engine.plugin_registry.get_plugin_for_signal.assert_called_once_with(signal)
        mock_plugin.process_signal.assert_called_once_with(signal)
        assert result == {'status': 'success'}
    
    @pytest.mark.asyncio
    async def test_no_plugin_found_returns_none(self, trading_engine):
        """Test that missing plugin returns None"""
        trading_engine.plugin_registry.get_plugin_for_signal.return_value = None
        
        signal = {'strategy': 'UNKNOWN', 'symbol': 'EURUSD'}
        result = await trading_engine.process_signal(signal)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_plugin_failure_handled(self, trading_engine, mock_plugin):
        """Test that plugin failures are handled gracefully"""
        mock_plugin.process_signal.side_effect = Exception("Plugin error")
        trading_engine.plugin_registry.get_plugin_for_signal.return_value = mock_plugin
        
        signal = {'strategy': 'V3_COMBINED', 'symbol': 'EURUSD'}
        result = await trading_engine.process_signal(signal)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_trading_disabled_ignores_signal(self, trading_engine, mock_plugin):
        """Test that signals are ignored when trading disabled"""
        trading_engine.trading_enabled = False
        trading_engine.plugin_registry.get_plugin_for_signal.return_value = mock_plugin
        
        signal = {'strategy': 'V3_COMBINED', 'symbol': 'EURUSD'}
        result = await trading_engine.process_signal(signal)
        
        assert result is None
        mock_plugin.process_signal.assert_not_called()

class TestPluginRegistryLookup:
    """Test suite for plugin registry signal lookup"""
    
    @pytest.fixture
    def registry(self):
        """Create PluginRegistry"""
        return PluginRegistry()
    
    def test_get_plugin_for_v3_signal(self, registry):
        """Test V3 signal finds V3 plugin"""
        # Register mock V3 plugin
        v3_plugin = MagicMock()
        v3_plugin.enabled = True
        v3_plugin.get_supported_strategies.return_value = ['V3_COMBINED']
        registry._plugins['combined_v3'] = v3_plugin
        
        signal = {'strategy': 'V3_COMBINED'}
        result = registry.get_plugin_for_signal(signal)
        
        assert result == v3_plugin
    
    def test_get_plugin_for_v6_signal_with_timeframe(self, registry):
        """Test V6 signal with timeframe finds correct plugin"""
        # Register mock V6 plugins
        v6_1m = MagicMock()
        v6_1m.enabled = True
        v6_1m.get_supported_strategies.return_value = ['V6_PRICE_ACTION']
        v6_1m.get_supported_timeframes.return_value = ['1m']
        registry._plugins['price_action_1m'] = v6_1m
        
        v6_5m = MagicMock()
        v6_5m.enabled = True
        v6_5m.get_supported_strategies.return_value = ['V6_PRICE_ACTION']
        v6_5m.get_supported_timeframes.return_value = ['5m']
        registry._plugins['price_action_5m'] = v6_5m
        
        signal = {'strategy': 'V6_PRICE_ACTION', 'timeframe': '5m'}
        result = registry.get_plugin_for_signal(signal)
        
        assert result == v6_5m
    
    def test_disabled_plugin_not_returned(self, registry):
        """Test disabled plugins are not returned"""
        plugin = MagicMock()
        plugin.enabled = False
        plugin.get_supported_strategies.return_value = ['V3_COMBINED']
        registry._plugins['combined_v3'] = plugin
        
        signal = {'strategy': 'V3_COMBINED'}
        result = registry.get_plugin_for_signal(signal)
        
        assert result is None
```

**Reason:** Verifies the delegation framework works correctly before proceeding.

---

## 6. DEPENDENCIES

### Prerequisites:
- None (this is the first plan)

### Blocks:
- Plan 02 (Webhook Routing) - needs delegation framework
- Plan 03 (Re-Entry) - needs plugin interface
- Plan 04 (Dual Orders) - needs plugin interface
- All subsequent plans depend on this foundation

---

## 7. FILES AFFECTED

| File | Action | Description |
|------|--------|-------------|
| `src/core/plugin_system/plugin_interface.py` | CREATE | New interface definitions |
| `src/core/plugin_system/plugin_registry.py` | MODIFY | Add signal lookup methods |
| `src/core/trading_engine.py` | MODIFY | Add delegation, deprecate hardcoded |
| `src/logic_plugins/combined_v3/plugin.py` | MODIFY | Implement interface |
| `src/logic_plugins/price_action_1m/plugin.py` | MODIFY | Implement interface |
| `src/logic_plugins/price_action_5m/plugin.py` | MODIFY | Implement interface |
| `src/logic_plugins/price_action_15m/plugin.py` | MODIFY | Implement interface |
| `src/logic_plugins/price_action_1h/plugin.py` | MODIFY | Implement interface |
| `tests/test_core_delegation.py` | CREATE | New test file |

---

## 8. TESTING STRATEGY

### Unit Tests:
1. Test `get_plugin_for_signal()` returns correct plugin
2. Test `delegate_to_plugin()` calls plugin's `process_signal()`
3. Test disabled plugins are skipped
4. Test plugin failures are handled gracefully
5. Test trading disabled ignores signals

### Integration Tests:
1. Test V3 signal flows through V3 plugin
2. Test V6 signal flows through correct V6 plugin
3. Test unknown strategy returns None

### Manual Verification:
1. Start bot with logging enabled
2. Send test V3 signal via webhook
3. Verify log shows "Delegating signal to plugin: combined_v3"
4. Verify plugin's `process_signal()` is called

---

## 9. ROLLBACK PLAN

### If Delegation Fails:
1. Revert `trading_engine.py` to use hardcoded logic
2. Keep deprecated methods functional
3. Disable plugin delegation flag

### Rollback Steps:
```bash
# Revert trading_engine.py
git checkout HEAD~1 -- src/core/trading_engine.py

# Or use feature flag
# In config.json:
{
  "use_plugin_delegation": false
}
```

### Feature Flag Implementation:
```python
# In trading_engine.py
async def process_signal(self, signal_data):
    if self.config.get('use_plugin_delegation', True):
        return await self.delegate_to_plugin(signal_data)
    else:
        # Legacy hardcoded path
        if signal_data.get('strategy') == 'V3_COMBINED':
            return await self._process_v3_signal(signal_data)
        elif signal_data.get('strategy') == 'V6_PRICE_ACTION':
            return await self._process_v6_signal(signal_data)
```

---

## 10. SUCCESS CRITERIA

This plan is COMPLETE when:

1. ✅ `plugin_interface.py` created with `ISignalProcessor` and `IOrderExecutor`
2. ✅ `plugin_registry.py` has `get_plugin_for_signal()` method
3. ✅ `trading_engine.py` has `delegate_to_plugin()` method
4. ✅ `trading_engine.py` `process_signal()` uses delegation (no hardcoded logic)
5. ✅ All V3/V6 plugins implement the interface
6. ✅ All unit tests pass
7. ✅ Manual test shows delegation working
8. ✅ Deprecated methods redirect to delegation

---

## 11. REFERENCES

- **Study Report 01:** Section 1 (Trading Logic System)
- **Study Report 04:** GAP-1 (Plugin Wiring to Core)
- **Original Surgery Plan:** `03_SURGERY_PLANS/01_CORE_CLEANUP_PLAN.md`
- **Planning Doc:** `01_PLANNING/02_PHASE_1_PLAN.md`
- **Code Evidence:** `src/core/trading_engine.py` Lines 232-245

---

**END OF PLAN 01**
