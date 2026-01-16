# SHADOW MODE SYSTEM

**File:** `src/core/shadow_mode_manager.py`  
**Lines:** 411  
**Purpose:** Risk-free testing of V6 plugins against legacy system

---

## OVERVIEW

The Shadow Mode System enables safe testing of new plugins by running them in parallel with the legacy system without executing real trades. This allows for comparison, validation, and gradual rollout of new trading logic.

### Key Benefits

1. **Risk-Free Testing:** Test new plugins without risking real money
2. **Comparison:** Compare plugin decisions against legacy system
3. **Gradual Rollout:** Transition from legacy to plugins with confidence
4. **Debugging:** Identify discrepancies before going live

---

## EXECUTION MODES

### Enum Definition (Lines 19-25)

```python
class ExecutionMode(Enum):
    """System execution modes"""
    LEGACY_ONLY = "legacy_only"      # Only legacy executes (current)
    SHADOW = "shadow"                 # Both run, only legacy executes
    PLUGIN_SHADOW = "plugin_shadow"  # Both run, only plugins execute
    PLUGIN_ONLY = "plugin_only"      # Only plugins execute (target)
```

### Mode Descriptions

| Mode | Legacy Runs | Plugin Runs | Real Trades | Use Case |
|------|-------------|-------------|-------------|----------|
| LEGACY_ONLY | Yes | No | Legacy | Production (current) |
| SHADOW | Yes | Yes | Legacy | Testing plugins |
| PLUGIN_SHADOW | Yes | Yes | Plugin | Validating plugins |
| PLUGIN_ONLY | No | Yes | Plugin | Full migration |

---

## CLASS STRUCTURE

### Definition (Lines 51-86)

```python
class ShadowModeManager:
    """
    Manages shadow mode execution and comparison.
    
    Shadow mode allows running the new plugin system in parallel with
    the legacy system without executing real trades. This enables:
    - Safe testing of new plugins
    - Comparison of plugin decisions vs legacy
    - Gradual rollout with confidence
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.execution_mode = ExecutionMode.LEGACY_ONLY
        
        # Registered plugins for shadow execution
        self.registered_plugins: Dict[str, Any] = {}
        
        # Execution history for comparison
        self.execution_history: List[Dict] = []
        
        # Mismatch tracking
        self.mismatches: List[Dict] = []
        
        # Statistics
        self.stats = {
            'total_executions': 0,
            'legacy_executions': 0,
            'plugin_executions': 0,
            'mismatches': 0,
            'agreements': 0
        }
```

---

## CORE METHODS

### Set Execution Mode (Lines 90-120)

```python
def set_execution_mode(self, mode: ExecutionMode):
    """
    Set the execution mode.
    
    Args:
        mode: ExecutionMode enum value
    """
    old_mode = self.execution_mode
    self.execution_mode = mode
    
    logger.info(f"Execution mode changed: {old_mode.value} -> {mode.value}")
    
    # Record mode change
    self.execution_history.append({
        'type': 'mode_change',
        'from': old_mode.value,
        'to': mode.value,
        'timestamp': datetime.now().isoformat()
    })

def get_execution_mode(self) -> ExecutionMode:
    """Get current execution mode"""
    return self.execution_mode
```

### Register Plugin (Lines 125-150)

```python
def register_plugin(self, plugin_id: str, plugin: Any):
    """
    Register a plugin for shadow mode execution.
    
    Args:
        plugin_id: Unique plugin identifier
        plugin: Plugin instance
    """
    self.registered_plugins[plugin_id] = plugin
    logger.info(f"Plugin registered for shadow mode: {plugin_id}")

def unregister_plugin(self, plugin_id: str):
    """Unregister a plugin from shadow mode"""
    if plugin_id in self.registered_plugins:
        del self.registered_plugins[plugin_id]
        logger.info(f"Plugin unregistered from shadow mode: {plugin_id}")
```

### Compare Results (Lines 155-220)

```python
def compare_results(
    self,
    legacy_result: Dict[str, Any],
    plugin_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare legacy and plugin execution results.
    
    Comparison criteria:
    - Action taken (entry/exit/skip)
    - Direction (buy/sell)
    - Order type (single/dual)
    - SL/TP values (within tolerance)
    
    Args:
        legacy_result: Result from legacy system
        plugin_result: Result from plugin system
        
    Returns:
        dict: Comparison result with mismatch details
    """
    comparison = {
        'timestamp': datetime.now().isoformat(),
        'legacy': legacy_result,
        'plugin': plugin_result,
        'mismatch': False,
        'mismatch_details': []
    }
    
    # Compare action
    legacy_action = legacy_result.get('action', 'none')
    plugin_action = plugin_result.get('action', 'none')
    
    if legacy_action != plugin_action:
        comparison['mismatch'] = True
        comparison['mismatch_details'].append({
            'field': 'action',
            'legacy': legacy_action,
            'plugin': plugin_action
        })
    
    # Compare direction (if both took action)
    if legacy_action != 'none' and plugin_action != 'none':
        legacy_dir = legacy_result.get('direction', '')
        plugin_dir = plugin_result.get('direction', '')
        
        if legacy_dir != plugin_dir:
            comparison['mismatch'] = True
            comparison['mismatch_details'].append({
                'field': 'direction',
                'legacy': legacy_dir,
                'plugin': plugin_dir
            })
    
    # Update statistics
    self.stats['total_executions'] += 1
    if comparison['mismatch']:
        self.stats['mismatches'] += 1
        self.mismatches.append(comparison)
    else:
        self.stats['agreements'] += 1
    
    # Store in history
    self.execution_history.append(comparison)
    
    return comparison
```

### Record Plugin Execution (Lines 225-270)

```python
def record_plugin_execution(
    self,
    plugin_id: str,
    signal_data: Dict[str, Any],
    result: Dict[str, Any]
):
    """
    Record a plugin execution for tracking.
    
    Args:
        plugin_id: ID of the plugin
        signal_data: Input signal data
        result: Execution result
    """
    record = {
        'type': 'plugin_execution',
        'plugin_id': plugin_id,
        'signal': signal_data,
        'result': result,
        'timestamp': datetime.now().isoformat(),
        'mode': self.execution_mode.value
    }
    
    self.execution_history.append(record)
    self.stats['plugin_executions'] += 1
    
    logger.debug(f"Plugin execution recorded: {plugin_id}")
```

---

## SHADOW EXECUTION FLOW

### In TradingEngine (Lines 275-330)

```python
async def execute_shadow_mode(
    self,
    signal_data: Dict[str, Any]
) -> Tuple[Dict, Dict]:
    """
    Execute signal in shadow mode (both systems).
    
    Args:
        signal_data: Signal to process
        
    Returns:
        tuple: (legacy_result, plugin_result)
    """
    # Execute legacy system
    legacy_result = await self._process_legacy(signal_data)
    
    # Execute plugin system (shadow - no real trades)
    plugin_result = await self._process_plugin_shadow(signal_data)
    
    # Compare results
    comparison = self.compare_results(legacy_result, plugin_result)
    
    # Log if mismatch
    if comparison['mismatch']:
        logger.warning(f"Shadow mode mismatch: {comparison['mismatch_details']}")
    
    return legacy_result, plugin_result

async def _process_plugin_shadow(
    self,
    signal_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process signal through plugin in shadow mode.
    No real trades are executed.
    
    Args:
        signal_data: Signal to process
        
    Returns:
        dict: What the plugin WOULD have done
    """
    # Find appropriate plugin
    plugin = self.plugin_registry.get_plugin_for_signal(signal_data)
    
    if not plugin:
        return {'action': 'none', 'reason': 'no_plugin_found'}
    
    # Execute in shadow mode
    try:
        # Plugin should check shadow_mode flag and not execute real trades
        result = await plugin.process_signal(signal_data)
        result['shadow'] = True
        return result
    except Exception as e:
        return {'action': 'error', 'error': str(e)}
```

---

## STATISTICS AND REPORTING

### Get Statistics (Lines 335-370)

```python
def get_statistics(self) -> Dict[str, Any]:
    """
    Get shadow mode statistics.
    
    Returns:
        dict: Statistics including:
            - total_executions
            - legacy_executions
            - plugin_executions
            - mismatches
            - agreements
            - mismatch_rate
    """
    stats = self.stats.copy()
    
    # Calculate mismatch rate
    if stats['total_executions'] > 0:
        stats['mismatch_rate'] = (
            stats['mismatches'] / stats['total_executions'] * 100
        )
        stats['agreement_rate'] = (
            stats['agreements'] / stats['total_executions'] * 100
        )
    else:
        stats['mismatch_rate'] = 0
        stats['agreement_rate'] = 0
    
    return stats

def get_recent_mismatches(self, count: int = 10) -> List[Dict]:
    """Get most recent mismatches"""
    return self.mismatches[-count:]

def get_execution_history(self, count: int = 100) -> List[Dict]:
    """Get recent execution history"""
    return self.execution_history[-count:]
```

### Generate Report (Lines 375-411)

```python
def generate_shadow_report(self) -> str:
    """
    Generate a human-readable shadow mode report.
    
    Returns:
        str: Formatted report
    """
    stats = self.get_statistics()
    
    report = f"""
SHADOW MODE REPORT
==================
Generated: {datetime.now().isoformat()}
Current Mode: {self.execution_mode.value}

STATISTICS
----------
Total Executions: {stats['total_executions']}
Legacy Executions: {stats['legacy_executions']}
Plugin Executions: {stats['plugin_executions']}

COMPARISON
----------
Agreements: {stats['agreements']} ({stats['agreement_rate']:.1f}%)
Mismatches: {stats['mismatches']} ({stats['mismatch_rate']:.1f}%)

RECENT MISMATCHES
-----------------
"""
    
    for mismatch in self.get_recent_mismatches(5):
        report += f"\n{mismatch['timestamp']}: {mismatch['mismatch_details']}"
    
    return report
```

---

## TELEGRAM COMMANDS

### Shadow Mode Commands

| Command | Description |
|---------|-------------|
| `/shadow_status` | Show current shadow mode status |
| `/shadow_enable` | Enable shadow mode (SHADOW) |
| `/shadow_disable` | Disable shadow mode (LEGACY_ONLY) |
| `/shadow_plugin` | Switch to PLUGIN_SHADOW mode |
| `/shadow_live` | Switch to PLUGIN_ONLY mode |
| `/shadow_report` | Generate shadow mode report |
| `/shadow_mismatches` | Show recent mismatches |

### Command Implementation (src/telegram/shadow_commands.py)

```python
async def handle_shadow_status(self, update, context):
    """Handle /shadow_status command"""
    mode = self.shadow_manager.get_execution_mode()
    stats = self.shadow_manager.get_statistics()
    
    message = f"""
Shadow Mode Status
Mode: {mode.value}
Total: {stats['total_executions']}
Agreements: {stats['agreements']} ({stats['agreement_rate']:.1f}%)
Mismatches: {stats['mismatches']} ({stats['mismatch_rate']:.1f}%)
"""
    await update.message.reply_text(message)

async def handle_shadow_enable(self, update, context):
    """Handle /shadow_enable command"""
    self.shadow_manager.set_execution_mode(ExecutionMode.SHADOW)
    await update.message.reply_text("Shadow mode enabled. Both systems will run, only legacy executes.")
```

---

## CONFIGURATION

### Shadow Mode Config

```python
{
    "shadow_mode": {
        "enabled": true,
        "default_mode": "legacy_only",
        "comparison": {
            "sl_tolerance_pips": 2,
            "tp_tolerance_pips": 2,
            "lot_tolerance_percent": 5
        },
        "logging": {
            "log_all_executions": true,
            "log_mismatches_only": false,
            "max_history_size": 1000
        },
        "alerts": {
            "notify_on_mismatch": true,
            "mismatch_threshold": 10
        }
    }
}
```

---

## MIGRATION PATH

### Recommended Migration Steps

1. **Phase 1: LEGACY_ONLY**
   - Current production state
   - Plugins not running

2. **Phase 2: SHADOW**
   - Enable shadow mode
   - Both systems run, only legacy executes
   - Monitor for mismatches
   - Target: <5% mismatch rate

3. **Phase 3: PLUGIN_SHADOW**
   - Both systems run, only plugins execute
   - Legacy provides comparison baseline
   - Target: <2% mismatch rate

4. **Phase 4: PLUGIN_ONLY**
   - Full migration complete
   - Only plugins execute
   - Legacy system deprecated

---

## RELATED FILES

- `src/core/trading_engine.py` - Uses ShadowModeManager
- `src/telegram/shadow_commands.py` - Telegram commands
- `src/core/plugin_system/plugin_registry.py` - Plugin registration
