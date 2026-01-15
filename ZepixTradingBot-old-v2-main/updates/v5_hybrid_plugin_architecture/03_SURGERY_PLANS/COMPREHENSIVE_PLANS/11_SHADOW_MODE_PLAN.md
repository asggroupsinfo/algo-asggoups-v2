# PLAN 11: SHADOW MODE TESTING

**Date:** 2026-01-15
**Priority:** P0 (Critical)
**Estimated Time:** 3-4 days
**Dependencies:** Plans 01-10

---

## 1. OBJECTIVE

Implement Shadow Mode to run the new plugin system in parallel with the legacy system without executing real trades. This allows validation of the new architecture before going live. After this plan:

1. **Parallel Execution** - New plugins run alongside legacy code
2. **No Real Trades** - Shadow mode logs decisions but doesn't execute
3. **Comparison Reports** - Compare plugin decisions vs legacy decisions
4. **Gradual Rollout** - Enable plugins one-by-one after validation

**Current Problem (from Study Report 04, GAP-7):**
- No way to test new plugin system safely
- No comparison mechanism
- No gradual rollout strategy
- Risk of breaking production

**Target State:**
- Shadow mode runs plugins without executing trades
- Decisions logged and compared to legacy
- Discrepancies flagged for review
- Safe gradual rollout path

---

## 2. SCOPE

### In-Scope:
- Implement shadow mode infrastructure
- Create decision logging system
- Create comparison engine
- Create discrepancy reports
- Implement gradual rollout controls
- Create shadow mode Telegram commands

### Out-of-Scope:
- Actual trade execution (that's production mode)
- Performance optimization
- Load testing

---

## 3. CURRENT STATE ANALYSIS

### Current System:
- No shadow mode exists
- Legacy code executes trades directly
- No comparison mechanism
- No safe testing path

### Target System:
- Shadow mode intercepts signals
- Both legacy and plugins process signals
- Decisions compared and logged
- Discrepancies reported

---

## 4. GAPS ADDRESSED

| Gap | Description | How Addressed |
|-----|-------------|---------------|
| GAP-7 | Shadow Mode Testing | Complete implementation |
| REQ-6.1 | Parallel Execution | Run both systems |
| REQ-6.2 | Decision Logging | Log all decisions |
| REQ-6.3 | Comparison Engine | Compare decisions |
| REQ-6.4 | Gradual Rollout | Enable plugins safely |

---

## 5. IMPLEMENTATION STEPS

### Step 1: Create Shadow Mode Manager

**File:** `src/core/shadow_mode_manager.py` (NEW)

**Code:**
```python
"""
Shadow Mode Manager
Runs new plugin system in parallel with legacy without executing trades
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)

class ExecutionMode(Enum):
    """System execution modes"""
    LEGACY_ONLY = "legacy_only"      # Only legacy executes (current)
    SHADOW = "shadow"                 # Both run, only legacy executes
    PLUGIN_SHADOW = "plugin_shadow"  # Both run, only plugins execute
    PLUGIN_ONLY = "plugin_only"      # Only plugins execute (target)

@dataclass
class Decision:
    """Represents a trading decision"""
    source: str  # 'legacy' or plugin_id
    signal_id: str
    timestamp: datetime
    action: str  # 'execute', 'reject', 'skip'
    reason: str
    order_params: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComparisonResult:
    """Result of comparing legacy vs plugin decisions"""
    signal_id: str
    timestamp: datetime
    legacy_decision: Decision
    plugin_decision: Decision
    match: bool
    discrepancy_type: Optional[str] = None
    discrepancy_details: Optional[str] = None

class ShadowModeManager:
    """Manages shadow mode execution and comparison"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.mode = ExecutionMode.LEGACY_ONLY
        
        # Decision storage
        self._decisions: Dict[str, List[Decision]] = {}  # signal_id -> decisions
        self._comparisons: List[ComparisonResult] = []
        
        # Statistics
        self._stats = {
            'signals_processed': 0,
            'matches': 0,
            'discrepancies': 0,
            'legacy_executes': 0,
            'plugin_executes': 0
        }
        
        # Enabled plugins for shadow mode
        self._shadow_plugins: set = set()
    
    def set_mode(self, mode: ExecutionMode):
        """Set execution mode"""
        old_mode = self.mode
        self.mode = mode
        logger.info(f"Execution mode changed: {old_mode.value} -> {mode.value}")
    
    def enable_shadow_plugin(self, plugin_id: str):
        """Enable a plugin for shadow mode"""
        self._shadow_plugins.add(plugin_id)
        logger.info(f"Plugin enabled for shadow mode: {plugin_id}")
    
    def disable_shadow_plugin(self, plugin_id: str):
        """Disable a plugin from shadow mode"""
        self._shadow_plugins.discard(plugin_id)
        logger.info(f"Plugin disabled from shadow mode: {plugin_id}")
    
    def is_plugin_in_shadow(self, plugin_id: str) -> bool:
        """Check if plugin is in shadow mode"""
        return plugin_id in self._shadow_plugins
    
    # ==================== Decision Recording ====================
    
    def record_decision(self, decision: Decision):
        """Record a trading decision"""
        if decision.signal_id not in self._decisions:
            self._decisions[decision.signal_id] = []
        
        self._decisions[decision.signal_id].append(decision)
        logger.debug(f"Decision recorded: {decision.source} -> {decision.action}")
    
    def record_legacy_decision(
        self,
        signal_id: str,
        action: str,
        reason: str,
        order_params: Dict[str, Any] = None
    ):
        """Record a legacy system decision"""
        decision = Decision(
            source='legacy',
            signal_id=signal_id,
            timestamp=datetime.now(),
            action=action,
            reason=reason,
            order_params=order_params
        )
        self.record_decision(decision)
        
        if action == 'execute':
            self._stats['legacy_executes'] += 1
    
    def record_plugin_decision(
        self,
        plugin_id: str,
        signal_id: str,
        action: str,
        reason: str,
        order_params: Dict[str, Any] = None
    ):
        """Record a plugin decision"""
        decision = Decision(
            source=plugin_id,
            signal_id=signal_id,
            timestamp=datetime.now(),
            action=action,
            reason=reason,
            order_params=order_params
        )
        self.record_decision(decision)
        
        if action == 'execute':
            self._stats['plugin_executes'] += 1
    
    # ==================== Comparison ====================
    
    def compare_decisions(self, signal_id: str) -> Optional[ComparisonResult]:
        """Compare legacy and plugin decisions for a signal"""
        decisions = self._decisions.get(signal_id, [])
        
        legacy_decision = None
        plugin_decision = None
        
        for d in decisions:
            if d.source == 'legacy':
                legacy_decision = d
            elif d.source in self._shadow_plugins:
                plugin_decision = d
        
        if not legacy_decision or not plugin_decision:
            return None
        
        # Compare decisions
        match = self._decisions_match(legacy_decision, plugin_decision)
        
        result = ComparisonResult(
            signal_id=signal_id,
            timestamp=datetime.now(),
            legacy_decision=legacy_decision,
            plugin_decision=plugin_decision,
            match=match
        )
        
        if not match:
            result.discrepancy_type, result.discrepancy_details = \
                self._analyze_discrepancy(legacy_decision, plugin_decision)
            self._stats['discrepancies'] += 1
        else:
            self._stats['matches'] += 1
        
        self._comparisons.append(result)
        self._stats['signals_processed'] += 1
        
        return result
    
    def _decisions_match(self, legacy: Decision, plugin: Decision) -> bool:
        """Check if two decisions match"""
        # Same action?
        if legacy.action != plugin.action:
            return False
        
        # If both execute, check order params
        if legacy.action == 'execute' and plugin.action == 'execute':
            if legacy.order_params and plugin.order_params:
                # Check key parameters
                keys_to_check = ['symbol', 'direction', 'lot_size']
                for key in keys_to_check:
                    if legacy.order_params.get(key) != plugin.order_params.get(key):
                        return False
        
        return True
    
    def _analyze_discrepancy(
        self,
        legacy: Decision,
        plugin: Decision
    ) -> tuple:
        """Analyze why decisions don't match"""
        if legacy.action != plugin.action:
            return (
                'action_mismatch',
                f"Legacy: {legacy.action}, Plugin: {plugin.action}"
            )
        
        if legacy.order_params and plugin.order_params:
            for key in ['symbol', 'direction', 'lot_size', 'sl_pips', 'tp_pips']:
                if legacy.order_params.get(key) != plugin.order_params.get(key):
                    return (
                        f'{key}_mismatch',
                        f"Legacy: {legacy.order_params.get(key)}, Plugin: {plugin.order_params.get(key)}"
                    )
        
        return ('unknown', 'Could not determine discrepancy cause')
    
    # ==================== Execution Control ====================
    
    def should_execute_legacy(self) -> bool:
        """Check if legacy should execute trades"""
        return self.mode in [ExecutionMode.LEGACY_ONLY, ExecutionMode.SHADOW]
    
    def should_execute_plugin(self, plugin_id: str) -> bool:
        """Check if plugin should execute trades"""
        if self.mode == ExecutionMode.PLUGIN_ONLY:
            return True
        if self.mode == ExecutionMode.PLUGIN_SHADOW:
            return plugin_id in self._shadow_plugins
        return False
    
    def should_run_plugin(self, plugin_id: str) -> bool:
        """Check if plugin should run (even in shadow)"""
        if self.mode == ExecutionMode.LEGACY_ONLY:
            return False
        return True
    
    # ==================== Reporting ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get shadow mode statistics"""
        return {
            **self._stats,
            'mode': self.mode.value,
            'shadow_plugins': list(self._shadow_plugins),
            'match_rate': (
                self._stats['matches'] / self._stats['signals_processed'] * 100
                if self._stats['signals_processed'] > 0 else 0
            )
        }
    
    def get_discrepancies(self, limit: int = 100) -> List[ComparisonResult]:
        """Get recent discrepancies"""
        discrepancies = [c for c in self._comparisons if not c.match]
        return discrepancies[-limit:]
    
    def generate_report(self) -> str:
        """Generate shadow mode report"""
        stats = self.get_stats()
        discrepancies = self.get_discrepancies(10)
        
        report = f"""
=== SHADOW MODE REPORT ===
Generated: {datetime.now().isoformat()}
Mode: {stats['mode']}

=== STATISTICS ===
Signals Processed: {stats['signals_processed']}
Matches: {stats['matches']}
Discrepancies: {stats['discrepancies']}
Match Rate: {stats['match_rate']:.1f}%

Legacy Executes: {stats['legacy_executes']}
Plugin Executes: {stats['plugin_executes']}

Shadow Plugins: {', '.join(stats['shadow_plugins']) or 'None'}

=== RECENT DISCREPANCIES ===
"""
        for d in discrepancies:
            report += f"""
Signal: {d.signal_id}
Time: {d.timestamp.isoformat()}
Type: {d.discrepancy_type}
Details: {d.discrepancy_details}
Legacy: {d.legacy_decision.action} - {d.legacy_decision.reason}
Plugin: {d.plugin_decision.action} - {d.plugin_decision.reason}
---
"""
        
        return report
    
    def export_comparisons(self, filepath: str):
        """Export comparisons to JSON file"""
        data = []
        for c in self._comparisons:
            data.append({
                'signal_id': c.signal_id,
                'timestamp': c.timestamp.isoformat(),
                'match': c.match,
                'discrepancy_type': c.discrepancy_type,
                'discrepancy_details': c.discrepancy_details,
                'legacy': {
                    'action': c.legacy_decision.action,
                    'reason': c.legacy_decision.reason
                },
                'plugin': {
                    'source': c.plugin_decision.source,
                    'action': c.plugin_decision.action,
                    'reason': c.plugin_decision.reason
                }
            })
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported {len(data)} comparisons to {filepath}")
```

**Reason:** Core shadow mode infrastructure.

---

### Step 2: Integrate Shadow Mode with Trading Engine

**File:** `src/core/trading_engine.py`

**Changes:**
```python
# ADD shadow mode integration

from src.core.shadow_mode_manager import ShadowModeManager, ExecutionMode

class TradingEngine:
    def __init__(self, config: Dict[str, Any]):
        # ... existing init ...
        
        # Shadow mode
        self.shadow_manager = ShadowModeManager(config.get('shadow_mode', {}))
    
    async def process_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process signal with shadow mode support"""
        signal_id = signal.get('signal_id', str(uuid.uuid4()))
        
        # Run legacy if enabled
        legacy_result = None
        if self.shadow_manager.should_execute_legacy():
            legacy_result = await self._process_legacy(signal)
            self.shadow_manager.record_legacy_decision(
                signal_id=signal_id,
                action='execute' if legacy_result else 'reject',
                reason=legacy_result.get('reason', 'executed') if legacy_result else 'rejected',
                order_params=legacy_result
            )
        
        # Run plugins if enabled
        plugin_result = None
        for plugin_id in self.plugin_registry.get_enabled_plugins():
            if self.shadow_manager.should_run_plugin(plugin_id):
                plugin = self.plugin_registry.get_plugin(plugin_id)
                
                # Process signal in plugin
                result = await plugin.process_signal(signal)
                
                # Record decision
                self.shadow_manager.record_plugin_decision(
                    plugin_id=plugin_id,
                    signal_id=signal_id,
                    action='execute' if result else 'reject',
                    reason=result.get('reason', 'executed') if result else 'rejected',
                    order_params=result
                )
                
                # Execute if not in shadow
                if self.shadow_manager.should_execute_plugin(plugin_id):
                    plugin_result = result
        
        # Compare decisions
        comparison = self.shadow_manager.compare_decisions(signal_id)
        if comparison and not comparison.match:
            logger.warning(f"Decision discrepancy: {comparison.discrepancy_type}")
            await self._notify_discrepancy(comparison)
        
        # Return appropriate result based on mode
        if self.shadow_manager.mode == ExecutionMode.PLUGIN_ONLY:
            return plugin_result
        return legacy_result
    
    async def _notify_discrepancy(self, comparison):
        """Notify about decision discrepancy"""
        message = f"Shadow Mode Discrepancy: {comparison.discrepancy_type}\n"
        message += f"Signal: {comparison.signal_id}\n"
        message += f"Details: {comparison.discrepancy_details}"
        
        await self.telegram_manager.send_notification('shadow_discrepancy', message)
```

**Reason:** Integrates shadow mode with signal processing.

---

### Step 3: Create Shadow Mode Telegram Commands

**File:** `src/telegram/shadow_commands.py` (NEW)

**Code:**
```python
"""
Shadow Mode Telegram Commands
Commands for controlling and monitoring shadow mode
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ShadowModeCommands:
    """Telegram commands for shadow mode"""
    
    def __init__(self, shadow_manager, telegram_bot):
        self.shadow_manager = shadow_manager
        self.bot = telegram_bot
        
        # Register commands
        self._register_commands()
    
    def _register_commands(self):
        """Register shadow mode commands"""
        commands = {
            'shadow_status': self.cmd_shadow_status,
            'shadow_enable': self.cmd_shadow_enable,
            'shadow_disable': self.cmd_shadow_disable,
            'shadow_mode': self.cmd_shadow_mode,
            'shadow_report': self.cmd_shadow_report,
            'shadow_discrepancies': self.cmd_shadow_discrepancies,
            'shadow_plugin_on': self.cmd_shadow_plugin_on,
            'shadow_plugin_off': self.cmd_shadow_plugin_off,
            'shadow_export': self.cmd_shadow_export,
        }
        
        for cmd, handler in commands.items():
            self.bot.register_command(cmd, handler)
    
    async def cmd_shadow_status(self, update, context):
        """Show shadow mode status"""
        stats = self.shadow_manager.get_stats()
        
        message = f"""
🔍 Shadow Mode Status

Mode: {stats['mode']}
Signals Processed: {stats['signals_processed']}
Match Rate: {stats['match_rate']:.1f}%

Matches: {stats['matches']}
Discrepancies: {stats['discrepancies']}

Shadow Plugins: {', '.join(stats['shadow_plugins']) or 'None'}
"""
        await update.message.reply_text(message)
    
    async def cmd_shadow_enable(self, update, context):
        """Enable shadow mode"""
        from src.core.shadow_mode_manager import ExecutionMode
        self.shadow_manager.set_mode(ExecutionMode.SHADOW)
        await update.message.reply_text("Shadow mode ENABLED. Legacy executes, plugins shadow.")
    
    async def cmd_shadow_disable(self, update, context):
        """Disable shadow mode (legacy only)"""
        from src.core.shadow_mode_manager import ExecutionMode
        self.shadow_manager.set_mode(ExecutionMode.LEGACY_ONLY)
        await update.message.reply_text("Shadow mode DISABLED. Legacy only.")
    
    async def cmd_shadow_mode(self, update, context):
        """Set shadow mode"""
        from src.core.shadow_mode_manager import ExecutionMode
        
        if not context.args:
            modes = [m.value for m in ExecutionMode]
            await update.message.reply_text(f"Usage: /shadow_mode <mode>\nModes: {', '.join(modes)}")
            return
        
        mode_str = context.args[0].lower()
        try:
            mode = ExecutionMode(mode_str)
            self.shadow_manager.set_mode(mode)
            await update.message.reply_text(f"Shadow mode set to: {mode.value}")
        except ValueError:
            await update.message.reply_text(f"Invalid mode: {mode_str}")
    
    async def cmd_shadow_report(self, update, context):
        """Generate shadow mode report"""
        report = self.shadow_manager.generate_report()
        await update.message.reply_text(report)
    
    async def cmd_shadow_discrepancies(self, update, context):
        """Show recent discrepancies"""
        discrepancies = self.shadow_manager.get_discrepancies(5)
        
        if not discrepancies:
            await update.message.reply_text("No discrepancies found.")
            return
        
        message = "Recent Discrepancies:\n\n"
        for d in discrepancies:
            message += f"Signal: {d.signal_id}\n"
            message += f"Type: {d.discrepancy_type}\n"
            message += f"Details: {d.discrepancy_details}\n\n"
        
        await update.message.reply_text(message)
    
    async def cmd_shadow_plugin_on(self, update, context):
        """Enable plugin for shadow mode"""
        if not context.args:
            await update.message.reply_text("Usage: /shadow_plugin_on <plugin_id>")
            return
        
        plugin_id = context.args[0]
        self.shadow_manager.enable_shadow_plugin(plugin_id)
        await update.message.reply_text(f"Plugin {plugin_id} enabled for shadow mode.")
    
    async def cmd_shadow_plugin_off(self, update, context):
        """Disable plugin from shadow mode"""
        if not context.args:
            await update.message.reply_text("Usage: /shadow_plugin_off <plugin_id>")
            return
        
        plugin_id = context.args[0]
        self.shadow_manager.disable_shadow_plugin(plugin_id)
        await update.message.reply_text(f"Plugin {plugin_id} disabled from shadow mode.")
    
    async def cmd_shadow_export(self, update, context):
        """Export shadow mode data"""
        filepath = f"data/shadow_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.shadow_manager.export_comparisons(filepath)
        await update.message.reply_text(f"Shadow data exported to: {filepath}")
```

**Reason:** Telegram commands for shadow mode control.

---

### Step 4: Create Shadow Mode Tests

**File:** `tests/test_shadow_mode.py` (NEW)

**Code:**
```python
"""
Tests for Shadow Mode
Verifies shadow mode functionality
"""
import pytest
from datetime import datetime
from src.core.shadow_mode_manager import (
    ShadowModeManager, ExecutionMode, Decision, ComparisonResult
)

class TestShadowModeManager:
    """Test shadow mode manager"""
    
    @pytest.fixture
    def manager(self):
        return ShadowModeManager()
    
    def test_default_mode(self, manager):
        """Test default mode is legacy only"""
        assert manager.mode == ExecutionMode.LEGACY_ONLY
    
    def test_set_mode(self, manager):
        """Test mode setting"""
        manager.set_mode(ExecutionMode.SHADOW)
        assert manager.mode == ExecutionMode.SHADOW
    
    def test_enable_shadow_plugin(self, manager):
        """Test enabling plugin for shadow"""
        manager.enable_shadow_plugin('v3_combined')
        assert manager.is_plugin_in_shadow('v3_combined')
    
    def test_record_decisions(self, manager):
        """Test decision recording"""
        manager.record_legacy_decision(
            signal_id='sig_001',
            action='execute',
            reason='valid signal',
            order_params={'symbol': 'EURUSD', 'direction': 'BUY'}
        )
        
        assert 'sig_001' in manager._decisions
        assert len(manager._decisions['sig_001']) == 1
    
    def test_compare_matching_decisions(self, manager):
        """Test comparison of matching decisions"""
        manager.enable_shadow_plugin('v3_combined')
        
        # Record matching decisions
        manager.record_legacy_decision(
            signal_id='sig_002',
            action='execute',
            reason='valid',
            order_params={'symbol': 'EURUSD', 'direction': 'BUY', 'lot_size': 0.01}
        )
        manager.record_plugin_decision(
            plugin_id='v3_combined',
            signal_id='sig_002',
            action='execute',
            reason='valid',
            order_params={'symbol': 'EURUSD', 'direction': 'BUY', 'lot_size': 0.01}
        )
        
        result = manager.compare_decisions('sig_002')
        
        assert result is not None
        assert result.match == True
    
    def test_compare_mismatching_decisions(self, manager):
        """Test comparison of mismatching decisions"""
        manager.enable_shadow_plugin('v3_combined')
        
        # Record mismatching decisions
        manager.record_legacy_decision(
            signal_id='sig_003',
            action='execute',
            reason='valid',
            order_params={'symbol': 'EURUSD', 'direction': 'BUY', 'lot_size': 0.01}
        )
        manager.record_plugin_decision(
            plugin_id='v3_combined',
            signal_id='sig_003',
            action='reject',
            reason='risk limit',
            order_params=None
        )
        
        result = manager.compare_decisions('sig_003')
        
        assert result is not None
        assert result.match == False
        assert result.discrepancy_type == 'action_mismatch'
    
    def test_execution_control_legacy_only(self, manager):
        """Test execution control in legacy only mode"""
        manager.set_mode(ExecutionMode.LEGACY_ONLY)
        
        assert manager.should_execute_legacy() == True
        assert manager.should_execute_plugin('v3_combined') == False
        assert manager.should_run_plugin('v3_combined') == False
    
    def test_execution_control_shadow(self, manager):
        """Test execution control in shadow mode"""
        manager.set_mode(ExecutionMode.SHADOW)
        manager.enable_shadow_plugin('v3_combined')
        
        assert manager.should_execute_legacy() == True
        assert manager.should_execute_plugin('v3_combined') == False
        assert manager.should_run_plugin('v3_combined') == True
    
    def test_execution_control_plugin_only(self, manager):
        """Test execution control in plugin only mode"""
        manager.set_mode(ExecutionMode.PLUGIN_ONLY)
        
        assert manager.should_execute_legacy() == False
        assert manager.should_execute_plugin('v3_combined') == True
    
    def test_stats(self, manager):
        """Test statistics"""
        manager.enable_shadow_plugin('v3_combined')
        manager.set_mode(ExecutionMode.SHADOW)
        
        # Record some decisions
        for i in range(5):
            manager.record_legacy_decision(f'sig_{i}', 'execute', 'valid')
            manager.record_plugin_decision('v3_combined', f'sig_{i}', 'execute', 'valid')
            manager.compare_decisions(f'sig_{i}')
        
        stats = manager.get_stats()
        
        assert stats['signals_processed'] == 5
        assert stats['matches'] == 5
        assert stats['match_rate'] == 100.0
```

**Reason:** Verifies shadow mode functionality.

---

## 6. DEPENDENCIES

### Prerequisites:
- Plans 01-10 (All functionality implemented)

### Blocks:
- Plan 12 (E2E Testing) - Uses shadow mode for validation

---

## 7. FILES AFFECTED

| File | Action | Description |
|------|--------|-------------|
| `src/core/shadow_mode_manager.py` | CREATE | Shadow mode infrastructure |
| `src/core/trading_engine.py` | MODIFY | Integrate shadow mode |
| `src/telegram/shadow_commands.py` | CREATE | Telegram commands |
| `tests/test_shadow_mode.py` | CREATE | Tests |

---

## 8. SUCCESS CRITERIA

1. ✅ Shadow mode manager created
2. ✅ Decision recording works
3. ✅ Comparison engine works
4. ✅ Discrepancy detection works
5. ✅ Telegram commands work
6. ✅ Gradual rollout controls work
7. ✅ All tests pass

---

## 9. ROLLOUT PROCEDURE

### Phase 1: Enable Shadow Mode
```
/shadow_enable
```
- Legacy executes trades
- Plugins run in shadow (no execution)
- Decisions compared and logged

### Phase 2: Monitor for 1 Week
- Review discrepancy reports daily
- Fix any issues found
- Target: 95%+ match rate

### Phase 3: Enable Plugin Shadow
```
/shadow_mode plugin_shadow
/shadow_plugin_on v3_combined
```
- Plugins execute trades
- Legacy runs in shadow
- Compare results

### Phase 4: Plugin Only
```
/shadow_mode plugin_only
```
- Only plugins execute
- Legacy disabled
- Full migration complete

---

## 11. REFERENCES

- **Study Report 04:** GAP-7, REQ-6.1-6.4
- **Best Practice:** Shadow mode testing for critical systems

---

**END OF PLAN 11**
