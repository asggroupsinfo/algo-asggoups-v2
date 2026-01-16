# PLAN 08: SERVICE API INTEGRATION

**Date:** 2026-01-15
**Priority:** P1 (High)
**Estimated Time:** 2-3 days
**Dependencies:** Plans 03-07

---

## 1. OBJECTIVE

Complete the ServiceAPI integration so plugins access ALL core services through a single, unified interface. Currently ServiceAPI exists but plugins don't use it consistently. After this plan:

1. **Single Entry Point** - All plugin-to-core communication via ServiceAPI
2. **Service Registration** - All services registered with ServiceAPI
3. **Service Discovery** - Plugins discover services dynamically
4. **Metrics Collection** - All service calls tracked

**Current Problem (from Study Report 04, GAP-6):**
- ServiceAPI exists but plugins call managers directly
- Not all services registered
- No service metrics
- Inconsistent service access patterns

**Target State:**
- Plugins ONLY use ServiceAPI for all operations
- All services registered and discoverable
- Service metrics collected
- Consistent access patterns

---

## 2. SCOPE

### In-Scope:
- Register all services with ServiceAPI
- Update plugins to use ServiceAPI exclusively
- Implement service discovery
- Implement service metrics
- Create service health checks

### Out-of-Scope:
- Creating new services (already done in Plans 03-07)
- Database operations (Plan 09)
- Plugin renaming (Plan 10)

---

## 3. CURRENT STATE ANALYSIS

### File: `src/core/plugin_system/service_api.py`

**Current Structure:**
- ServiceAPI class exists
- Some services registered
- Basic methods implemented
- **PROBLEM:** Not all services registered, plugins bypass it

**Current Services (incomplete):**
```python
class ServiceAPI:
    # Registered services
    order_service: OrderExecutionService
    risk_service: RiskCalculationService
    # MISSING: ReentryService, DualOrderService, ProfitBookingService, etc.
```

### File: `src/logic_plugins/combined_v3/plugin.py`

**Current Problem:**
- Plugin has direct references to services
- Bypasses ServiceAPI for some operations
- Inconsistent access patterns

---

## 4. GAPS ADDRESSED

| Gap | Description | How Addressed |
|-----|-------------|---------------|
| GAP-6 | Service API Integration | Complete service registration |
| REQ-3.1 | Plugin Service Access | Unified ServiceAPI access |
| REQ-3.2 | Service Discovery | Dynamic service lookup |
| REQ-3.3 | Service Metrics | Track all service calls |

---

## 5. IMPLEMENTATION STEPS

### Step 1: Complete ServiceAPI with All Services

**File:** `src/core/plugin_system/service_api.py`

**Changes:**
```python
"""
ServiceAPI - Single Entry Point for Plugin-to-Core Communication
Version 3.0 - Complete Service Integration
"""
from typing import Dict, Any, Optional, Type, Callable
import logging
from dataclasses import dataclass
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ServiceMetrics:
    """Metrics for a service"""
    calls: int = 0
    errors: int = 0
    total_time_ms: float = 0
    last_call: Optional[datetime] = None
    last_error: Optional[str] = None

class ServiceAPI:
    """
    Single entry point for all plugin-to-core communication.
    Plugins MUST use this API for all operations.
    """
    
    VERSION = "3.0.0"
    
    def __init__(self):
        # Service registry
        self._services: Dict[str, Any] = {}
        self._service_metrics: Dict[str, ServiceMetrics] = {}
        
        # Service health
        self._health_checks: Dict[str, Callable] = {}
        self._service_status: Dict[str, bool] = {}
        
        self._initialized = False
    
    # ==================== Service Registration ====================
    
    def register_service(self, name: str, service: Any, health_check: Optional[Callable] = None):
        """Register a service with the API"""
        self._services[name] = service
        self._service_metrics[name] = ServiceMetrics()
        
        if health_check:
            self._health_checks[name] = health_check
        
        self._service_status[name] = True
        logger.info(f"Service registered: {name}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service"""
        return self._services.get(name)
    
    def has_service(self, name: str) -> bool:
        """Check if a service is registered"""
        return name in self._services
    
    def list_services(self) -> list:
        """List all registered services"""
        return list(self._services.keys())
    
    # ==================== Core Services ====================
    
    # Order Execution
    @property
    def order_service(self):
        return self._services.get('order_execution')
    
    # Risk Calculation
    @property
    def risk_service(self):
        return self._services.get('risk_calculation')
    
    # Re-Entry Service (Plan 03)
    @property
    def reentry_service(self):
        return self._services.get('reentry')
    
    # Dual Order Service (Plan 04)
    @property
    def dual_order_service(self):
        return self._services.get('dual_order')
    
    # Profit Booking Service (Plan 05)
    @property
    def profit_booking_service(self):
        return self._services.get('profit_booking')
    
    # Autonomous Service (Plan 06)
    @property
    def autonomous_service(self):
        return self._services.get('autonomous')
    
    # Telegram Service (Plan 07)
    @property
    def telegram_service(self):
        return self._services.get('telegram')
    
    # Database Service (Plan 09)
    @property
    def database_service(self):
        return self._services.get('database')
    
    # ==================== Service Operations ====================
    
    async def execute_order(self, order_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an order through order service"""
        return await self._call_service('order_execution', 'execute_order', order_params)
    
    async def calculate_risk(self, symbol: str, lot_size: float) -> Dict[str, Any]:
        """Calculate risk through risk service"""
        return await self._call_service('risk_calculation', 'calculate_risk', symbol, lot_size)
    
    async def start_recovery(self, event) -> bool:
        """Start recovery through reentry service"""
        return await self._call_service('reentry', 'start_sl_hunt_recovery', event)
    
    async def create_dual_orders(self, signal: Dict, config_a, config_b):
        """Create dual orders through dual order service"""
        return await self._call_service('dual_order', 'create_dual_orders', signal, config_a, config_b)
    
    async def create_profit_chain(self, plugin_id: str, order_b_id: str, symbol: str, direction: str):
        """Create profit chain through profit booking service"""
        return await self._call_service('profit_booking', 'create_chain', plugin_id, order_b_id, symbol, direction)
    
    async def check_safety(self, plugin_id: str):
        """Check safety through autonomous service"""
        return await self._call_service('autonomous', 'check_recovery_allowed', plugin_id)
    
    async def send_notification(self, notification_type: str, message: str, **kwargs):
        """Send notification through telegram service"""
        return await self._call_service('telegram', 'send_notification', notification_type, message, **kwargs)
    
    # ==================== Service Call Wrapper ====================
    
    async def _call_service(self, service_name: str, method_name: str, *args, **kwargs):
        """Call a service method with metrics tracking"""
        service = self._services.get(service_name)
        if not service:
            logger.error(f"Service not found: {service_name}")
            return None
        
        method = getattr(service, method_name, None)
        if not method:
            logger.error(f"Method not found: {service_name}.{method_name}")
            return None
        
        # Track metrics
        metrics = self._service_metrics[service_name]
        metrics.calls += 1
        metrics.last_call = datetime.now()
        
        start_time = datetime.now()
        try:
            if asyncio.iscoroutinefunction(method):
                result = await method(*args, **kwargs)
            else:
                result = method(*args, **kwargs)
            
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            metrics.total_time_ms += elapsed
            
            return result
        except Exception as e:
            metrics.errors += 1
            metrics.last_error = str(e)
            logger.error(f"Service call failed: {service_name}.{method_name}: {e}")
            raise
    
    # ==================== Health & Metrics ====================
    
    async def check_health(self) -> Dict[str, bool]:
        """Check health of all services"""
        results = {}
        
        for name, check in self._health_checks.items():
            try:
                if asyncio.iscoroutinefunction(check):
                    results[name] = await check()
                else:
                    results[name] = check()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = False
        
        self._service_status.update(results)
        return results
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all services"""
        return {
            name: {
                'calls': m.calls,
                'errors': m.errors,
                'avg_time_ms': m.total_time_ms / m.calls if m.calls > 0 else 0,
                'last_call': m.last_call.isoformat() if m.last_call else None,
                'last_error': m.last_error
            }
            for name, m in self._service_metrics.items()
        }
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get status of all services"""
        return self._service_status.copy()
    
    # ==================== Initialization ====================
    
    async def initialize(self, services: Dict[str, Any]):
        """Initialize ServiceAPI with all services"""
        logger.info("Initializing ServiceAPI...")
        
        # Register all services
        for name, service in services.items():
            health_check = getattr(service, 'health_check', None)
            self.register_service(name, service, health_check)
        
        # Run initial health check
        await self.check_health()
        
        self._initialized = True
        logger.info(f"ServiceAPI initialized with {len(self._services)} services")
    
    def is_initialized(self) -> bool:
        """Check if ServiceAPI is initialized"""
        return self._initialized
```

**Reason:** Complete ServiceAPI with all services and metrics.

---

### Step 2: Create Service Initializer

**File:** `src/core/service_initializer.py` (NEW)

**Code:**
```python
"""
Service Initializer
Initializes and registers all services with ServiceAPI
"""
from typing import Dict, Any
import logging

from src.core.plugin_system.service_api import ServiceAPI
from src.core.services.order_execution_service import OrderExecutionService
from src.core.services.risk_calculation_service import RiskCalculationService
from src.core.services.reentry_service import ReentryService
from src.core.services.dual_order_service import DualOrderService
from src.core.services.profit_booking_service import ProfitBookingService
from src.core.services.autonomous_service import AutonomousService
from src.telegram.multi_telegram_manager import MultiTelegramManager

# Managers
from src.managers.reentry_manager import ReentryManager
from src.managers.recovery_window_monitor import RecoveryWindowMonitor
from src.managers.exit_continuation_monitor import ExitContinuationMonitor
from src.managers.dual_order_manager import DualOrderManager
from src.managers.risk_manager import RiskManager
from src.managers.profit_booking_manager import ProfitBookingManager
from src.managers.autonomous_system_manager import AutonomousSystemManager
from src.managers.reverse_shield_manager import ReverseShieldManager

logger = logging.getLogger(__name__)

class ServiceInitializer:
    """Initializes all services and registers them with ServiceAPI"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.service_api = ServiceAPI()
        
        # Managers (will be initialized)
        self._managers: Dict[str, Any] = {}
        
        # Services (will be initialized)
        self._services: Dict[str, Any] = {}
    
    async def initialize(self) -> ServiceAPI:
        """Initialize all services and return configured ServiceAPI"""
        logger.info("Initializing all services...")
        
        # Step 1: Initialize managers
        await self._initialize_managers()
        
        # Step 2: Initialize services
        await self._initialize_services()
        
        # Step 3: Register with ServiceAPI
        await self.service_api.initialize(self._services)
        
        logger.info("All services initialized")
        return self.service_api
    
    async def _initialize_managers(self):
        """Initialize all managers"""
        logger.info("Initializing managers...")
        
        # Risk Manager
        self._managers['risk'] = RiskManager(self.config.get('risk', {}))
        
        # Re-entry managers
        self._managers['reentry'] = ReentryManager(self.config.get('reentry', {}))
        self._managers['recovery_monitor'] = RecoveryWindowMonitor()
        self._managers['exit_monitor'] = ExitContinuationMonitor()
        
        # Dual order manager
        self._managers['dual_order'] = DualOrderManager(self.config.get('dual_order', {}))
        
        # Profit booking manager
        self._managers['profit_booking'] = ProfitBookingManager(self.config.get('profit_booking', {}))
        
        # Autonomous system managers
        self._managers['autonomous'] = AutonomousSystemManager(self.config.get('autonomous', {}))
        self._managers['reverse_shield'] = ReverseShieldManager()
        
        logger.info(f"Initialized {len(self._managers)} managers")
    
    async def _initialize_services(self):
        """Initialize all services"""
        logger.info("Initializing services...")
        
        # Order Execution Service
        self._services['order_execution'] = OrderExecutionService(
            self._managers['risk'],
            self.config.get('mt5', {})
        )
        
        # Risk Calculation Service
        self._services['risk_calculation'] = RiskCalculationService(
            self._managers['risk']
        )
        
        # Re-entry Service (Plan 03)
        self._services['reentry'] = ReentryService(
            self._managers['reentry'],
            self._managers['recovery_monitor'],
            self._managers['exit_monitor'],
            self._managers['autonomous']
        )
        
        # Dual Order Service (Plan 04)
        self._services['dual_order'] = DualOrderService(
            self._managers['dual_order'],
            self._managers['risk']
        )
        
        # Profit Booking Service (Plan 05)
        self._services['profit_booking'] = ProfitBookingService(
            self._managers['profit_booking']
        )
        
        # Autonomous Service (Plan 06)
        self._services['autonomous'] = AutonomousService(
            self._managers['autonomous'],
            self._managers['reverse_shield']
        )
        
        # Telegram Service (Plan 07)
        self._services['telegram'] = MultiTelegramManager(
            self.config.get('telegram', {})
        )
        await self._services['telegram'].initialize()
        
        logger.info(f"Initialized {len(self._services)} services")
    
    def get_service_api(self) -> ServiceAPI:
        """Get the configured ServiceAPI"""
        return self.service_api
    
    def get_manager(self, name: str) -> Any:
        """Get a manager by name"""
        return self._managers.get(name)
    
    def get_service(self, name: str) -> Any:
        """Get a service by name"""
        return self._services.get(name)
```

**Reason:** Centralizes service initialization.

---

### Step 3: Update Plugins to Use ServiceAPI Exclusively

**File:** `src/logic_plugins/combined_v3/plugin.py`

**Changes:**
```python
# UPDATE plugin to use ServiceAPI exclusively

class CombinedV3Plugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor, 
                       IReentryCapable, IDualOrderCapable, IProfitBookingCapable,
                       IAutonomousCapable):
    """
    Combined V3 Logic Plugin
    Uses ServiceAPI for ALL core operations
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._service_api: Optional[ServiceAPI] = None
    
    def set_service_api(self, service_api: ServiceAPI):
        """
        Inject ServiceAPI - the ONLY way to access core services.
        This replaces all individual service setters.
        """
        self._service_api = service_api
        logger.info(f"ServiceAPI injected into {self.plugin_id}")
    
    # ==================== ServiceAPI Access ====================
    
    @property
    def reentry_service(self):
        """Get re-entry service from ServiceAPI"""
        if not self._service_api:
            raise RuntimeError("ServiceAPI not initialized")
        return self._service_api.reentry_service
    
    @property
    def dual_order_service(self):
        """Get dual order service from ServiceAPI"""
        if not self._service_api:
            raise RuntimeError("ServiceAPI not initialized")
        return self._service_api.dual_order_service
    
    @property
    def profit_booking_service(self):
        """Get profit booking service from ServiceAPI"""
        if not self._service_api:
            raise RuntimeError("ServiceAPI not initialized")
        return self._service_api.profit_booking_service
    
    @property
    def autonomous_service(self):
        """Get autonomous service from ServiceAPI"""
        if not self._service_api:
            raise RuntimeError("ServiceAPI not initialized")
        return self._service_api.autonomous_service
    
    # ==================== Updated Methods Using ServiceAPI ====================
    
    async def process_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process signal using ServiceAPI"""
        if not self._service_api:
            logger.error("ServiceAPI not initialized")
            return None
        
        # Check safety via ServiceAPI
        safety_check = await self._service_api.check_safety(self.plugin_id)
        if not safety_check.allowed:
            logger.info(f"Signal blocked: {safety_check.reason}")
            return None
        
        # Create dual orders via ServiceAPI
        order_a_config = await self.get_order_a_config(signal)
        order_b_config = await self.get_order_b_config(signal)
        
        result = await self._service_api.create_dual_orders(
            signal, order_a_config, order_b_config
        )
        
        if result.error:
            logger.error(f"Order creation failed: {result.error}")
            return None
        
        # Create profit chain via ServiceAPI
        if result.order_b_id:
            await self._service_api.create_profit_chain(
                self.plugin_id,
                result.order_b_id,
                signal['symbol'],
                signal['signal_type']
            )
        
        # Send notification via ServiceAPI
        await self._service_api.send_notification(
            'trade_opened',
            f"Trade opened: {signal['symbol']} {signal['signal_type']}",
            order_a_id=result.order_a_id,
            order_b_id=result.order_b_id
        )
        
        return {
            'status': 'executed',
            'order_a_id': result.order_a_id,
            'order_b_id': result.order_b_id
        }
    
    async def on_sl_hit(self, event) -> bool:
        """Handle SL hit via ServiceAPI"""
        if not self._service_api:
            return False
        
        # Check safety
        safety_check = await self._service_api.check_safety(self.plugin_id)
        if not safety_check.allowed:
            return False
        
        # Start recovery via ServiceAPI
        return await self._service_api.start_recovery(event)
```

**Reason:** Plugin uses ServiceAPI exclusively for all operations.

---

### Step 4: Create ServiceAPI Integration Tests

**File:** `tests/test_service_api_integration.py` (NEW)

**Code:**
```python
"""
Tests for ServiceAPI Integration
Verifies plugins use ServiceAPI correctly
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.plugin_system.service_api import ServiceAPI

class TestServiceAPI:
    """Test ServiceAPI"""
    
    @pytest.fixture
    def service_api(self):
        """Create ServiceAPI with mock services"""
        api = ServiceAPI()
        
        # Register mock services
        mock_order = MagicMock()
        mock_order.execute_order = AsyncMock(return_value={'order_id': 'test_001'})
        api.register_service('order_execution', mock_order)
        
        mock_reentry = MagicMock()
        mock_reentry.start_sl_hunt_recovery = AsyncMock(return_value=True)
        api.register_service('reentry', mock_reentry)
        
        mock_dual = MagicMock()
        mock_dual.create_dual_orders = AsyncMock()
        api.register_service('dual_order', mock_dual)
        
        mock_autonomous = MagicMock()
        mock_autonomous.check_recovery_allowed = AsyncMock()
        api.register_service('autonomous', mock_autonomous)
        
        return api
    
    def test_service_registration(self, service_api):
        """Test service registration"""
        assert service_api.has_service('order_execution')
        assert service_api.has_service('reentry')
        assert len(service_api.list_services()) == 4
    
    def test_service_access(self, service_api):
        """Test service access via properties"""
        assert service_api.order_service is not None
        assert service_api.reentry_service is not None
    
    @pytest.mark.asyncio
    async def test_service_call_tracking(self, service_api):
        """Test service call metrics"""
        await service_api.execute_order({'symbol': 'EURUSD'})
        
        metrics = service_api.get_metrics()
        assert metrics['order_execution']['calls'] == 1
    
    @pytest.mark.asyncio
    async def test_service_error_tracking(self, service_api):
        """Test error tracking"""
        service_api.order_service.execute_order = AsyncMock(side_effect=Exception("Test error"))
        
        with pytest.raises(Exception):
            await service_api.execute_order({'symbol': 'EURUSD'})
        
        metrics = service_api.get_metrics()
        assert metrics['order_execution']['errors'] == 1
    
    def test_missing_service(self, service_api):
        """Test missing service returns None"""
        assert service_api.get_service('nonexistent') is None
```

**Reason:** Verifies ServiceAPI integration works correctly.

---

## 6. DEPENDENCIES

### Prerequisites:
- Plans 03-07 (All services created)

### Blocks:
- Plan 09 (Database) - Uses ServiceAPI
- Plan 10 (Renaming) - Uses ServiceAPI

---

## 7. FILES AFFECTED

| File | Action | Description |
|------|--------|-------------|
| `src/core/plugin_system/service_api.py` | MODIFY | Complete implementation |
| `src/core/service_initializer.py` | CREATE | Service initialization |
| `src/logic_plugins/combined_v3/plugin.py` | MODIFY | Use ServiceAPI exclusively |
| `tests/test_service_api_integration.py` | CREATE | Tests |

---

## 8. SUCCESS CRITERIA

1. ✅ All services registered with ServiceAPI
2. ✅ Plugins use ServiceAPI exclusively
3. ✅ Service discovery works
4. ✅ Service metrics collected
5. ✅ Service health checks work
6. ✅ All tests pass

---

## 11. REFERENCES

- **Study Report 04:** GAP-6, REQ-3.1-3.3
- **Code Evidence:** `src/core/plugin_system/service_api.py`

---

**END OF PLAN 08**
