# PLAN 06: AUTONOMOUS SYSTEM INTEGRATION

**Date:** 2026-01-15
**Priority:** P1 (High)
**Estimated Time:** 3-4 days
**Dependencies:** Plans 03, 04, 05

---

## 1. OBJECTIVE

Integrate the Autonomous System Manager into the plugin architecture. The ASM provides safety limits and profit protection. After this plan, plugins will properly use:

1. **Daily Recovery Limits** - Max recoveries per day
2. **Concurrent Recovery Limits** - Max simultaneous recoveries
3. **Profit Protection** - Skip recovery if existing profit too valuable
4. **Reverse Shield System (v3.0)** - Advanced hedge protection during SL recovery

**Current Problem (from Study Report 04, GAP-5 & Discoveries 4-7):**
- Plugins exist but NEVER call AutonomousSystemManager
- Daily/concurrent recovery limits not enforced by plugins
- Profit protection logic not used
- Reverse Shield System not integrated

**Target State:**
- Plugins call ASM for all safety checks
- Daily/concurrent limits enforced
- Profit protection active
- Reverse Shield integrated with recovery

---

## 2. SCOPE

### In-Scope:
- Wire plugins to AutonomousSystemManager
- Implement daily recovery limit checks
- Implement concurrent recovery limit checks
- Implement profit protection logic
- Integrate Reverse Shield System (v3.0)
- Track recovery statistics per plugin

### Out-of-Scope:
- Re-entry system (Plan 03 - already uses ASM)
- Telegram notifications (Plan 07)
- Database operations (Plan 09)

---

## 3. CURRENT STATE ANALYSIS

### File: `src/managers/autonomous_system_manager.py`

**Current Structure (from Study Report 01, Feature 7.1-7.5):**
- Lines 1-100: Imports, class definition, configuration
- Lines 101-200: Daily recovery limit tracking
- Lines 201-300: Concurrent recovery limit tracking
- Lines 301-400: Profit protection logic
- Lines 401-500: Reverse Shield System v3.0
- Lines 501-600: Statistics and reporting

**Key Methods:**
```python
class AutonomousSystemManager:
    # Configuration
    daily_recovery_limit: int = 20
    concurrent_recovery_limit: int = 3
    profit_protection_threshold: float = 100.0  # $100
    
    async def can_start_recovery(self) -> bool
    async def get_daily_recovery_count(self) -> int
    async def get_concurrent_recovery_count(self) -> int
    async def get_current_session_profit(self) -> float
    async def should_protect_profit(self) -> bool
    async def activate_reverse_shield(self, trade_id: str) -> bool
    async def deactivate_reverse_shield(self, trade_id: str) -> bool
```

### File: `src/managers/reverse_shield_manager.py` (Discovery 1)

**Current Structure:**
- Advanced hedge protection during SL recovery
- Creates opposite position to protect during recovery window
- Automatically closes hedge when recovery completes or fails

**Key Methods:**
```python
class ReverseShieldManager:
    async def activate_shield(self, trade_id: str, symbol: str, direction: str) -> str
    async def deactivate_shield(self, shield_id: str) -> bool
    async def get_active_shields(self) -> List[Dict]
```

---

## 4. GAPS ADDRESSED

| Gap/Discovery | Description | How Addressed |
|---------------|-------------|---------------|
| GAP-5 | Autonomous System Integration | Wire plugins to ASM |
| Discovery 1 | Reverse Shield System (v3.0) | Integrate with recovery |
| Discovery 4 | Profit Protection Logic | Implement in plugins |
| Discovery 5 | Daily/Concurrent Recovery Limits | Enforce in plugins |

---

## 5. IMPLEMENTATION STEPS

### Step 1: Create Autonomous System Interface for Plugins

**File:** `src/core/plugin_system/autonomous_interface.py` (NEW)

**Code:**
```python
"""
Autonomous System Interface for Plugins
Defines how plugins interact with safety systems
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SafetyCheckResult:
    """Result of a safety check"""
    allowed: bool
    reason: str
    daily_count: int
    daily_limit: int
    concurrent_count: int
    concurrent_limit: int
    current_profit: float
    profit_threshold: float

@dataclass
class ReverseShieldStatus:
    """Status of reverse shield"""
    active: bool
    shield_id: Optional[str]
    symbol: str
    direction: str
    hedge_order_id: Optional[str]

class IAutonomousCapable(ABC):
    """Interface for plugins that use autonomous safety systems"""
    
    @abstractmethod
    async def check_recovery_allowed(self) -> SafetyCheckResult:
        """
        Check if recovery is allowed based on all safety limits.
        Must be called before starting any recovery.
        """
        pass
    
    @abstractmethod
    async def activate_reverse_shield(self, trade_id: str, symbol: str, direction: str) -> ReverseShieldStatus:
        """
        Activate Reverse Shield for a trade during recovery.
        Creates hedge position to protect during recovery window.
        """
        pass
    
    @abstractmethod
    async def deactivate_reverse_shield(self, trade_id: str) -> bool:
        """
        Deactivate Reverse Shield after recovery completes or fails.
        """
        pass
    
    @abstractmethod
    async def increment_recovery_count(self) -> int:
        """Increment daily recovery count and return new count"""
        pass
    
    @abstractmethod
    async def get_safety_stats(self) -> Dict[str, Any]:
        """Get current safety statistics"""
        pass
```

**Reason:** Defines clear contract for autonomous system operations.

---

### Step 2: Create Autonomous System Service for Plugins

**File:** `src/core/services/autonomous_service.py` (NEW)

**Code:**
```python
"""
Autonomous System Service
Provides safety functionality to plugins via ServiceAPI
"""
from typing import Dict, Any, Optional
import logging
from src.managers.autonomous_system_manager import AutonomousSystemManager
from src.managers.reverse_shield_manager import ReverseShieldManager
from src.core.plugin_system.autonomous_interface import (
    SafetyCheckResult, ReverseShieldStatus
)

logger = logging.getLogger(__name__)

class AutonomousService:
    """
    Service layer for autonomous system operations.
    Plugins use this instead of calling managers directly.
    """
    
    def __init__(
        self,
        autonomous_manager: AutonomousSystemManager,
        reverse_shield_manager: ReverseShieldManager
    ):
        self.asm = autonomous_manager
        self.rsm = reverse_shield_manager
        
        # Track per-plugin statistics
        self._plugin_stats: Dict[str, Dict[str, int]] = {}
    
    async def check_recovery_allowed(self, plugin_id: str) -> SafetyCheckResult:
        """
        Comprehensive safety check before recovery.
        Checks daily limit, concurrent limit, and profit protection.
        """
        daily_count = await self.asm.get_daily_recovery_count()
        concurrent_count = await self.asm.get_concurrent_recovery_count()
        current_profit = await self.asm.get_current_session_profit()
        
        # Check daily limit
        if daily_count >= self.asm.daily_recovery_limit:
            return SafetyCheckResult(
                allowed=False,
                reason=f"Daily recovery limit reached ({daily_count}/{self.asm.daily_recovery_limit})",
                daily_count=daily_count,
                daily_limit=self.asm.daily_recovery_limit,
                concurrent_count=concurrent_count,
                concurrent_limit=self.asm.concurrent_recovery_limit,
                current_profit=current_profit,
                profit_threshold=self.asm.profit_protection_threshold
            )
        
        # Check concurrent limit
        if concurrent_count >= self.asm.concurrent_recovery_limit:
            return SafetyCheckResult(
                allowed=False,
                reason=f"Concurrent recovery limit reached ({concurrent_count}/{self.asm.concurrent_recovery_limit})",
                daily_count=daily_count,
                daily_limit=self.asm.daily_recovery_limit,
                concurrent_count=concurrent_count,
                concurrent_limit=self.asm.concurrent_recovery_limit,
                current_profit=current_profit,
                profit_threshold=self.asm.profit_protection_threshold
            )
        
        # Check profit protection
        if current_profit >= self.asm.profit_protection_threshold:
            return SafetyCheckResult(
                allowed=False,
                reason=f"Profit protection active (${current_profit:.2f} >= ${self.asm.profit_protection_threshold:.2f})",
                daily_count=daily_count,
                daily_limit=self.asm.daily_recovery_limit,
                concurrent_count=concurrent_count,
                concurrent_limit=self.asm.concurrent_recovery_limit,
                current_profit=current_profit,
                profit_threshold=self.asm.profit_protection_threshold
            )
        
        # All checks passed
        logger.info(f"Recovery allowed for plugin {plugin_id}")
        return SafetyCheckResult(
            allowed=True,
            reason="All safety checks passed",
            daily_count=daily_count,
            daily_limit=self.asm.daily_recovery_limit,
            concurrent_count=concurrent_count,
            concurrent_limit=self.asm.concurrent_recovery_limit,
            current_profit=current_profit,
            profit_threshold=self.asm.profit_protection_threshold
        )
    
    async def activate_reverse_shield(
        self,
        plugin_id: str,
        trade_id: str,
        symbol: str,
        direction: str
    ) -> ReverseShieldStatus:
        """
        Activate Reverse Shield for a trade.
        Creates hedge position to protect during recovery window.
        """
        try:
            shield_id = await self.rsm.activate_shield(trade_id, symbol, direction)
            
            if shield_id:
                logger.info(f"Reverse Shield activated: {shield_id} for {trade_id}")
                self._track_shield_activation(plugin_id)
                
                return ReverseShieldStatus(
                    active=True,
                    shield_id=shield_id,
                    symbol=symbol,
                    direction=direction,
                    hedge_order_id=None  # Will be set by RSM
                )
            else:
                return ReverseShieldStatus(
                    active=False,
                    shield_id=None,
                    symbol=symbol,
                    direction=direction,
                    hedge_order_id=None
                )
        except Exception as e:
            logger.error(f"Failed to activate Reverse Shield: {e}")
            return ReverseShieldStatus(
                active=False,
                shield_id=None,
                symbol=symbol,
                direction=direction,
                hedge_order_id=None
            )
    
    async def deactivate_reverse_shield(self, plugin_id: str, shield_id: str) -> bool:
        """Deactivate Reverse Shield"""
        try:
            success = await self.rsm.deactivate_shield(shield_id)
            if success:
                logger.info(f"Reverse Shield deactivated: {shield_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to deactivate Reverse Shield: {e}")
            return False
    
    async def increment_recovery_count(self, plugin_id: str) -> int:
        """Increment daily recovery count"""
        # Increment in ASM
        new_count = await self.asm.increment_daily_recovery_count()
        
        # Track per plugin
        self._track_recovery(plugin_id)
        
        return new_count
    
    def _track_recovery(self, plugin_id: str):
        """Track recovery for a plugin"""
        if plugin_id not in self._plugin_stats:
            self._plugin_stats[plugin_id] = {
                'recoveries_today': 0,
                'shields_activated': 0,
                'shields_successful': 0
            }
        self._plugin_stats[plugin_id]['recoveries_today'] += 1
    
    def _track_shield_activation(self, plugin_id: str):
        """Track shield activation for a plugin"""
        if plugin_id not in self._plugin_stats:
            self._plugin_stats[plugin_id] = {
                'recoveries_today': 0,
                'shields_activated': 0,
                'shields_successful': 0
            }
        self._plugin_stats[plugin_id]['shields_activated'] += 1
    
    def get_plugin_stats(self, plugin_id: str) -> Dict[str, Any]:
        """Get statistics for a plugin"""
        return self._plugin_stats.get(plugin_id, {
            'recoveries_today': 0,
            'shields_activated': 0,
            'shields_successful': 0
        })
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global autonomous system statistics"""
        return {
            'daily_recovery_count': await self.asm.get_daily_recovery_count(),
            'daily_recovery_limit': self.asm.daily_recovery_limit,
            'concurrent_recovery_count': await self.asm.get_concurrent_recovery_count(),
            'concurrent_recovery_limit': self.asm.concurrent_recovery_limit,
            'current_session_profit': await self.asm.get_current_session_profit(),
            'profit_protection_threshold': self.asm.profit_protection_threshold,
            'active_shields': len(await self.rsm.get_active_shields()),
            'plugin_stats': self._plugin_stats
        }
```

**Reason:** Provides clean service interface for autonomous system operations.

---

### Step 3: Update Combined V3 Plugin with Autonomous System Support

**File:** `src/logic_plugins/combined_v3/plugin.py`

**Changes - Add Autonomous Interface:**
```python
# ADD imports
from src.core.plugin_system.autonomous_interface import (
    IAutonomousCapable, SafetyCheckResult, ReverseShieldStatus
)
from src.core.services.autonomous_service import AutonomousService

# UPDATE class definition
class CombinedV3Plugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor, 
                       IReentryCapable, IDualOrderCapable, IProfitBookingCapable,
                       IAutonomousCapable):
    """
    Combined V3 Logic Plugin with Autonomous System Support
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._autonomous_service: Optional[AutonomousService] = None
        self._active_shields: Dict[str, ReverseShieldStatus] = {}
    
    def set_autonomous_service(self, service: AutonomousService):
        """Inject autonomous service"""
        self._autonomous_service = service
    
    # ==================== IAutonomousCapable Implementation ====================
    
    async def check_recovery_allowed(self) -> SafetyCheckResult:
        """Check if recovery is allowed"""
        if not self._autonomous_service:
            return SafetyCheckResult(
                allowed=False,
                reason="AutonomousService not available",
                daily_count=0, daily_limit=0,
                concurrent_count=0, concurrent_limit=0,
                current_profit=0, profit_threshold=0
            )
        
        return await self._autonomous_service.check_recovery_allowed(self.plugin_id)
    
    async def activate_reverse_shield(self, trade_id: str, symbol: str, direction: str) -> ReverseShieldStatus:
        """Activate Reverse Shield for recovery protection"""
        if not self._autonomous_service:
            return ReverseShieldStatus(
                active=False, shield_id=None,
                symbol=symbol, direction=direction, hedge_order_id=None
            )
        
        # Check if shield is enabled in config
        if not self.config.get('reverse_shield_enabled', True):
            logger.info(f"Reverse Shield disabled for {self.plugin_id}")
            return ReverseShieldStatus(
                active=False, shield_id=None,
                symbol=symbol, direction=direction, hedge_order_id=None
            )
        
        status = await self._autonomous_service.activate_reverse_shield(
            self.plugin_id, trade_id, symbol, direction
        )
        
        if status.active:
            self._active_shields[trade_id] = status
        
        return status
    
    async def deactivate_reverse_shield(self, trade_id: str) -> bool:
        """Deactivate Reverse Shield"""
        if not self._autonomous_service:
            return False
        
        status = self._active_shields.pop(trade_id, None)
        if not status or not status.shield_id:
            return False
        
        return await self._autonomous_service.deactivate_reverse_shield(
            self.plugin_id, status.shield_id
        )
    
    async def increment_recovery_count(self) -> int:
        """Increment recovery count"""
        if not self._autonomous_service:
            return 0
        return await self._autonomous_service.increment_recovery_count(self.plugin_id)
    
    async def get_safety_stats(self) -> Dict[str, Any]:
        """Get safety statistics"""
        if not self._autonomous_service:
            return {}
        return self._autonomous_service.get_plugin_stats(self.plugin_id)
    
    # ==================== Update on_sl_hit to use safety checks ====================
    
    async def on_sl_hit(self, event: ReentryEvent) -> bool:
        """Handle SL hit with safety checks"""
        # Check if recovery is allowed
        safety_check = await self.check_recovery_allowed()
        if not safety_check.allowed:
            logger.info(f"Recovery blocked: {safety_check.reason}")
            return False
        
        # Activate Reverse Shield if enabled
        if self.config.get('reverse_shield_enabled', True):
            shield_status = await self.activate_reverse_shield(
                event.trade_id, event.symbol, event.direction
            )
            if shield_status.active:
                logger.info(f"Reverse Shield activated for {event.trade_id}")
        
        # Increment recovery count
        await self.increment_recovery_count()
        
        # Start SL Hunt Recovery (from Plan 03)
        return await self._reentry_service.start_sl_hunt_recovery(event)
    
    # ==================== Update on_recovery_signal to deactivate shield ====================
    
    async def on_recovery_signal(self, event: ReentryEvent) -> bool:
        """Handle recovery signal - deactivate shield"""
        # Deactivate Reverse Shield
        await self.deactivate_reverse_shield(event.trade_id)
        
        # Execute re-entry (from Plan 03)
        return await super().on_recovery_signal(event)
```

**Reason:** Implements autonomous system interface in V3 plugin.

---

### Step 4: Create Autonomous System Integration Tests

**File:** `tests/test_autonomous_integration.py` (NEW)

**Code:**
```python
"""
Tests for Autonomous System Integration
Verifies plugins properly use safety limits and Reverse Shield
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.plugin_system.autonomous_interface import SafetyCheckResult, ReverseShieldStatus
from src.core.services.autonomous_service import AutonomousService

class TestAutonomousService:
    """Test autonomous service"""
    
    @pytest.fixture
    def service(self):
        """Create service with mocks"""
        mock_asm = MagicMock()
        mock_asm.daily_recovery_limit = 20
        mock_asm.concurrent_recovery_limit = 3
        mock_asm.profit_protection_threshold = 100.0
        mock_asm.get_daily_recovery_count = AsyncMock(return_value=5)
        mock_asm.get_concurrent_recovery_count = AsyncMock(return_value=1)
        mock_asm.get_current_session_profit = AsyncMock(return_value=50.0)
        
        mock_rsm = MagicMock()
        mock_rsm.activate_shield = AsyncMock(return_value='shield_001')
        mock_rsm.deactivate_shield = AsyncMock(return_value=True)
        mock_rsm.get_active_shields = AsyncMock(return_value=[])
        
        return AutonomousService(mock_asm, mock_rsm)
    
    @pytest.mark.asyncio
    async def test_recovery_allowed(self, service):
        """Test recovery allowed when all checks pass"""
        result = await service.check_recovery_allowed('combined_v3')
        
        assert result.allowed == True
        assert result.reason == "All safety checks passed"
    
    @pytest.mark.asyncio
    async def test_daily_limit_blocks_recovery(self, service):
        """Test daily limit blocks recovery"""
        service.asm.get_daily_recovery_count = AsyncMock(return_value=20)
        
        result = await service.check_recovery_allowed('combined_v3')
        
        assert result.allowed == False
        assert "Daily recovery limit" in result.reason
    
    @pytest.mark.asyncio
    async def test_concurrent_limit_blocks_recovery(self, service):
        """Test concurrent limit blocks recovery"""
        service.asm.get_concurrent_recovery_count = AsyncMock(return_value=3)
        
        result = await service.check_recovery_allowed('combined_v3')
        
        assert result.allowed == False
        assert "Concurrent recovery limit" in result.reason
    
    @pytest.mark.asyncio
    async def test_profit_protection_blocks_recovery(self, service):
        """Test profit protection blocks recovery"""
        service.asm.get_current_session_profit = AsyncMock(return_value=150.0)
        
        result = await service.check_recovery_allowed('combined_v3')
        
        assert result.allowed == False
        assert "Profit protection" in result.reason
    
    @pytest.mark.asyncio
    async def test_reverse_shield_activation(self, service):
        """Test Reverse Shield activation"""
        status = await service.activate_reverse_shield(
            'combined_v3', 'trade_001', 'EURUSD', 'BUY'
        )
        
        assert status.active == True
        assert status.shield_id == 'shield_001'
        assert status.symbol == 'EURUSD'
    
    @pytest.mark.asyncio
    async def test_reverse_shield_deactivation(self, service):
        """Test Reverse Shield deactivation"""
        success = await service.deactivate_reverse_shield('combined_v3', 'shield_001')
        
        assert success == True
```

**Reason:** Verifies autonomous system integration works correctly.

---

## 6. DEPENDENCIES

### Prerequisites:
- Plan 03 (Re-Entry) - Uses safety checks
- Plan 04 (Dual Orders) - Uses safety checks
- Plan 05 (Profit Booking) - Uses profit tracking

### Blocks:
- Plan 07 (3-Bot Telegram) - Needs safety status commands

---

## 7. FILES AFFECTED

| File | Action | Description |
|------|--------|-------------|
| `src/core/plugin_system/autonomous_interface.py` | CREATE | Interface |
| `src/core/services/autonomous_service.py` | CREATE | Service |
| `src/logic_plugins/combined_v3/plugin.py` | MODIFY | Add IAutonomousCapable |
| `tests/test_autonomous_integration.py` | CREATE | Tests |

---

## 8. SUCCESS CRITERIA

1. ✅ `IAutonomousCapable` interface created
2. ✅ `AutonomousService` created
3. ✅ V3 plugin implements autonomous checks
4. ✅ Daily recovery limit enforced
5. ✅ Concurrent recovery limit enforced
6. ✅ Profit protection works
7. ✅ Reverse Shield integrates with recovery
8. ✅ All tests pass

---

## 11. REFERENCES

- **Study Report 01:** Section 7 (Autonomous System - 5 features)
- **Study Report 04:** GAP-5, Discoveries 1, 4-5
- **Code Evidence:** `src/managers/autonomous_system_manager.py`, `src/managers/reverse_shield_manager.py`

---

**END OF PLAN 06**
