"""
Shadow Mode Manager
Runs new plugin system in parallel with legacy without executing trades

Part of Plan 11: Shadow Mode Testing
Version: 1.0.0
Date: 2026-01-15
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
    """
    Manages shadow mode execution and comparison.
    
    Shadow mode allows running the new plugin system in parallel with
    the legacy system without executing real trades. This enables:
    - Safe testing of new plugins
    - Comparison of plugin decisions vs legacy
    - Gradual rollout with confidence
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.mode = ExecutionMode.LEGACY_ONLY
        self.execution_mode = ExecutionMode.LEGACY_ONLY  # Alias for compatibility
        
        # Decision storage
        self._decisions: Dict[str, List[Decision]] = {}  # signal_id -> decisions
        self._comparisons: List[ComparisonResult] = []
        
        # Statistics
        self._stats = {
            'signals_processed': 0,
            'matches': 0,
            'discrepancies': 0,
            'legacy_executes': 0,
            'plugin_executes': 0,
            'shadow_signals': 0
        }
        self.stats = self._stats  # Alias for compatibility
        
        # Enabled plugins for shadow mode
        self._shadow_plugins: set = set()
        self.registered_plugins: Dict[str, Any] = {}  # Plugin registry
        
        # Virtual orders (shadow trades)
        self._virtual_orders: List[Dict[str, Any]] = []
        
        # Execution history and mismatches
        self.execution_history: List[Dict[str, Any]] = []
        self.mismatches: List[Dict[str, Any]] = []
        
        logger.info("ShadowModeManager initialized")
    
    # ==================== Mode Control ====================
    
    def set_mode(self, mode: ExecutionMode):
        """Set execution mode"""
        old_mode = self.mode
        self.mode = mode
        self.execution_mode = mode  # Alias for compatibility
        logger.info(f"Execution mode changed: {old_mode.value} -> {mode.value}")
    
    def get_mode(self) -> ExecutionMode:
        """Get current execution mode"""
        return self.mode
    
    def set_execution_mode(self, mode: ExecutionMode):
        """Set execution mode (alias for set_mode)"""
        self.set_mode(mode)
    
    def get_execution_mode(self) -> ExecutionMode:
        """Get current execution mode (alias for get_mode)"""
        return self.get_mode()
    
    def enable_shadow_plugin(self, plugin_id: str):
        """Enable a plugin for shadow mode"""
        self._shadow_plugins.add(plugin_id)
        logger.info(f"Plugin enabled for shadow mode: {plugin_id}")
    
    def disable_shadow_plugin(self, plugin_id: str):
        """Disable a plugin from shadow mode"""
        self._shadow_plugins.discard(plugin_id)
        logger.info(f"Plugin disabled from shadow mode: {plugin_id}")
    
    def register_plugin(self, plugin_id: str, plugin: Any):
        """Register a plugin for shadow mode tracking"""
        self.registered_plugins[plugin_id] = plugin
        logger.info(f"Plugin registered: {plugin_id}")
    
    def unregister_plugin(self, plugin_id: str):
        """Unregister a plugin from shadow mode tracking"""
        if plugin_id in self.registered_plugins:
            del self.registered_plugins[plugin_id]
            logger.info(f"Plugin unregistered: {plugin_id}")
    
    def is_plugin_in_shadow(self, plugin_id: str) -> bool:
        """Check if plugin is in shadow mode"""
        return plugin_id in self._shadow_plugins
    
    def get_shadow_plugins(self) -> List[str]:
        """Get list of plugins in shadow mode"""
        return list(self._shadow_plugins)
    
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
        
        # If in shadow mode, record as shadow signal
        if self.is_plugin_in_shadow(plugin_id):
            self._stats['shadow_signals'] += 1
    
    # ==================== Virtual Orders ====================
    
    def record_virtual_order(
        self,
        plugin_id: str,
        signal_id: str,
        order_params: Dict[str, Any]
    ):
        """
        Record a virtual order (shadow trade).
        These are orders that would have been placed if not in shadow mode.
        """
        virtual_order = {
            'plugin_id': plugin_id,
            'signal_id': signal_id,
            'timestamp': datetime.now().isoformat(),
            'order_params': order_params,
            'status': 'virtual'
        }
        self._virtual_orders.append(virtual_order)
        logger.info(f"Virtual order recorded: {plugin_id} - {order_params.get('symbol', 'N/A')}")
        return virtual_order
    
    def get_virtual_orders(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent virtual orders"""
        return self._virtual_orders[-limit:]
    
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
    
    def is_shadow_mode_active(self) -> bool:
        """Check if shadow mode is active"""
        return self.mode in [ExecutionMode.SHADOW, ExecutionMode.PLUGIN_SHADOW]
    
    # ==================== Reporting ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get shadow mode statistics"""
        return {
            **self._stats,
            'mode': self.mode.value,
            'shadow_plugins': list(self._shadow_plugins),
            'virtual_orders_count': len(self._virtual_orders),
            'match_rate': (
                self._stats['matches'] / self._stats['signals_processed'] * 100
                if self._stats['signals_processed'] > 0 else 0
            )
        }
    
    def get_discrepancies(self, limit: int = 100) -> List[ComparisonResult]:
        """Get recent discrepancies"""
        discrepancies = [c for c in self._comparisons if not c.match]
        return discrepancies[-limit:]
    
    def compare_results(self, legacy_result: Dict[str, Any], plugin_result: Dict[str, Any], signal_id: str) -> Dict[str, Any]:
        """Compare legacy and plugin results for a signal"""
        match = legacy_result.get('action') == plugin_result.get('action')
        
        comparison = {
            'signal_id': signal_id,
            'timestamp': datetime.now().isoformat(),
            'match': match,
            'legacy': legacy_result,
            'plugin': plugin_result
        }
        
        if not match:
            comparison['discrepancy_type'] = 'action_mismatch'
            comparison['discrepancy_details'] = f"Legacy: {legacy_result.get('action')}, Plugin: {plugin_result.get('action')}"
            self.mismatches.append(comparison)
        
        self.execution_history.append(comparison)
        return comparison
    
    def record_plugin_execution(self, plugin_id: str, signal_id: str, result: Dict[str, Any]):
        """Record a plugin execution result"""
        execution = {
            'plugin_id': plugin_id,
            'signal_id': signal_id,
            'timestamp': datetime.now().isoformat(),
            'result': result
        }
        self.execution_history.append(execution)
        logger.debug(f"Plugin execution recorded: {plugin_id} -> {result.get('action', 'unknown')}")
    
    def get_recent_mismatches(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent mismatches between legacy and plugin decisions"""
        return self.mismatches[-count:]
    
    def get_execution_history(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-count:]
    
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
Shadow Signals: {stats['shadow_signals']}
Virtual Orders: {stats['virtual_orders_count']}

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
    
    def export_virtual_orders(self, filepath: str):
        """Export virtual orders to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self._virtual_orders, f, indent=2)
        
        logger.info(f"Exported {len(self._virtual_orders)} virtual orders to {filepath}")
    
    def reset_stats(self):
        """Reset statistics (for testing)"""
        self._stats = {
            'signals_processed': 0,
            'matches': 0,
            'discrepancies': 0,
            'legacy_executes': 0,
            'plugin_executes': 0,
            'shadow_signals': 0
        }
        self._decisions.clear()
        self._comparisons.clear()
        self._virtual_orders.clear()
        logger.info("Shadow mode stats reset")
