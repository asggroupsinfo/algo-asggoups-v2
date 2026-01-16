"""
Service Initializer - Centralizes Service Initialization for V5 Hybrid Plugin Architecture

This module initializes and registers all services with ServiceAPI.
It is the single point of service creation and registration.

Plan 08: Service API Integration
- Initializes all managers
- Creates all services
- Registers services with ServiceAPI
- Runs initial health checks

Version: 1.0.0
Date: 2026-01-15
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ServiceInitializer:
    """
    Initializes all services and registers them with ServiceAPI.
    
    This class is responsible for:
    1. Initializing all managers (risk, reentry, dual order, etc.)
    2. Creating all services from managers
    3. Registering services with ServiceAPI
    4. Running initial health checks
    
    Usage:
        initializer = ServiceInitializer(config)
        service_api = await initializer.initialize()
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ServiceInitializer with configuration.
        
        Args:
            config: Bot configuration dictionary
        """
        self.config = config
        self.service_api = None
        
        # Managers (will be initialized)
        self._managers: Dict[str, Any] = {}
        
        # Services (will be initialized)
        self._services: Dict[str, Any] = {}
        
        self._initialized = False
    
    async def initialize(self, trading_engine=None) -> 'ServiceAPI':
        """
        Initialize all services and return configured ServiceAPI.
        
        Args:
            trading_engine: Optional TradingEngine instance for ServiceAPI
        
        Returns:
            Configured ServiceAPI instance
        """
        logger.info("[ServiceInitializer] Starting service initialization...")
        
        # Import ServiceAPI here to avoid circular imports
        from src.core.plugin_system.service_api import ServiceAPI
        
        # Create ServiceAPI
        if trading_engine:
            self.service_api = ServiceAPI(trading_engine)
        else:
            # Create a minimal ServiceAPI for testing
            self.service_api = self._create_minimal_service_api()
        
        # Step 1: Initialize managers
        await self._initialize_managers()
        
        # Step 2: Initialize services
        await self._initialize_services()
        
        # Step 3: Register services with ServiceAPI
        await self._register_services()
        
        # Step 4: Run initial health check
        await self.service_api.check_health()
        
        self._initialized = True
        logger.info(f"[ServiceInitializer] Initialization complete. {len(self._services)} services registered.")
        
        return self.service_api
    
    def _create_minimal_service_api(self):
        """Create a minimal ServiceAPI for testing without TradingEngine"""
        from src.core.plugin_system.service_api import ServiceAPI, ServiceMetrics, ServiceRegistration
        
        class MinimalEngine:
            """Minimal engine for testing"""
            def __init__(self):
                self.config = {}
                self.mt5_client = None
                self.risk_manager = None
                self.telegram_bot = None
                self.trading_enabled = False
        
        return ServiceAPI(MinimalEngine())
    
    async def _initialize_managers(self):
        """Initialize all managers"""
        logger.info("[ServiceInitializer] Initializing managers...")
        
        try:
            # Risk Manager
            from src.managers.risk_manager import RiskManager
            self._managers['risk'] = RiskManager(self.config.get('risk', {}))
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] RiskManager not available: {e}")
        
        try:
            # Re-entry managers (Plan 03)
            from src.managers.reentry_manager import ReentryManager
            from src.managers.recovery_window_monitor import RecoveryWindowMonitor
            from src.managers.exit_continuation_monitor import ExitContinuationMonitor
            
            self._managers['reentry'] = ReentryManager(self.config.get('reentry', {}))
            self._managers['recovery_monitor'] = RecoveryWindowMonitor()
            self._managers['exit_monitor'] = ExitContinuationMonitor()
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] Reentry managers not available: {e}")
        
        try:
            # Dual order manager (Plan 04)
            from src.managers.dual_order_manager import DualOrderManager
            self._managers['dual_order'] = DualOrderManager(self.config.get('dual_order', {}))
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] DualOrderManager not available: {e}")
        
        try:
            # Profit booking manager (Plan 05)
            from src.managers.profit_booking_manager import ProfitBookingManager
            self._managers['profit_booking'] = ProfitBookingManager(self.config.get('profit_booking', {}))
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] ProfitBookingManager not available: {e}")
        
        try:
            # Autonomous system managers (Plan 06)
            from src.managers.autonomous_system_manager import AutonomousSystemManager
            from src.managers.reverse_shield_manager import ReverseShieldManager
            
            self._managers['autonomous'] = AutonomousSystemManager(self.config.get('autonomous', {}))
            self._managers['reverse_shield'] = ReverseShieldManager()
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] Autonomous managers not available: {e}")
        
        logger.info(f"[ServiceInitializer] Initialized {len(self._managers)} managers")
    
    async def _initialize_services(self):
        """Initialize all services"""
        logger.info("[ServiceInitializer] Initializing services...")
        
        try:
            # Order Execution Service
            from src.core.services.order_execution_service import OrderExecutionService
            risk_manager = self._managers.get('risk')
            self._services['order_execution'] = OrderExecutionService(
                risk_manager,
                self.config.get('mt5', {})
            )
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] OrderExecutionService not available: {e}")
        
        try:
            # Risk Calculation Service
            from src.core.services.risk_calculation_service import RiskCalculationService
            risk_manager = self._managers.get('risk')
            self._services['risk_calculation'] = RiskCalculationService(risk_manager)
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] RiskCalculationService not available: {e}")
        
        try:
            # Re-entry Service (Plan 03)
            from src.core.services.reentry_service import ReentryService
            self._services['reentry'] = ReentryService(
                self._managers.get('reentry'),
                self._managers.get('recovery_monitor'),
                self._managers.get('exit_monitor'),
                self._managers.get('autonomous')
            )
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] ReentryService not available: {e}")
        
        try:
            # Dual Order Service (Plan 04)
            from src.core.services.dual_order_service import DualOrderService
            self._services['dual_order'] = DualOrderService(
                self._managers.get('dual_order'),
                self._managers.get('risk')
            )
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] DualOrderService not available: {e}")
        
        try:
            # Profit Booking Service (Plan 05)
            from src.core.services.profit_booking_service import ProfitBookingService
            self._services['profit_booking'] = ProfitBookingService(
                self._managers.get('profit_booking')
            )
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] ProfitBookingService not available: {e}")
        
        try:
            # Autonomous Service (Plan 06)
            from src.core.services.autonomous_service import AutonomousService
            self._services['autonomous'] = AutonomousService(
                self._managers.get('autonomous'),
                self._managers.get('reverse_shield')
            )
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] AutonomousService not available: {e}")
        
        try:
            # Telegram Service (Plan 07)
            from src.telegram.multi_telegram_manager import MultiTelegramManager
            telegram_config = self.config.get('telegram', {})
            self._services['telegram'] = MultiTelegramManager(telegram_config)
            await self._services['telegram'].initialize()
        except ImportError as e:
            logger.warning(f"[ServiceInitializer] MultiTelegramManager not available: {e}")
        except Exception as e:
            logger.warning(f"[ServiceInitializer] Telegram service init failed: {e}")
        
        logger.info(f"[ServiceInitializer] Initialized {len(self._services)} services")
    
    async def _register_services(self):
        """Register all services with ServiceAPI"""
        logger.info("[ServiceInitializer] Registering services with ServiceAPI...")
        
        for name, service in self._services.items():
            # Get health check if available
            health_check = getattr(service, 'health_check', None)
            self.service_api.register_service(name, service, health_check)
        
        logger.info(f"[ServiceInitializer] Registered {len(self._services)} services")
    
    def get_service_api(self) -> Optional['ServiceAPI']:
        """Get the configured ServiceAPI"""
        return self.service_api
    
    def get_manager(self, name: str) -> Optional[Any]:
        """Get a manager by name"""
        return self._managers.get(name)
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a service by name"""
        return self._services.get(name)
    
    def is_initialized(self) -> bool:
        """Check if initialization is complete"""
        return self._initialized
    
    async def shutdown(self):
        """Shutdown all services"""
        logger.info("[ServiceInitializer] Shutting down services...")
        
        # Shutdown telegram service
        telegram = self._services.get('telegram')
        if telegram and hasattr(telegram, 'shutdown'):
            await telegram.shutdown()
        
        self._initialized = False
        logger.info("[ServiceInitializer] Shutdown complete")


async def create_service_initializer(config: Dict[str, Any], trading_engine=None) -> 'ServiceAPI':
    """
    Factory function to create and initialize ServiceAPI.
    
    Args:
        config: Bot configuration
        trading_engine: Optional TradingEngine instance
    
    Returns:
        Configured ServiceAPI instance
    """
    initializer = ServiceInitializer(config)
    return await initializer.initialize(trading_engine)
