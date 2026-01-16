# V5 HYBRID PLUGIN ARCHITECTURE - DEEP DIVE

## Source Files
- `src/core/trading_engine.py` (2382 lines)
- `src/core/plugin_system/service_api.py` (1312 lines)
- `src/core/plugin_system/plugin_registry.py`
- `src/core/plugin_system/base_plugin.py` (121 lines)
- `src/telegram/multi_telegram_manager.py`
- `src/core/shadow_mode_manager.py`

## Overview
The V5 Hybrid Plugin Architecture is a modular trading system that delegates signal processing to specialized plugins while maintaining backward compatibility with legacy code. The architecture consists of three main layers: Orchestration (TradingEngine), Services (ServiceAPI), and Execution (Plugins).

## Architecture Diagram

```
                    ┌─────────────────────────────────────┐
                    │         TELEGRAM CLUSTER            │
                    │  ┌─────────┬─────────┬─────────┐   │
                    │  │Controller│Notifier │Analytics│   │
                    │  └────┬────┴────┬────┴────┬────┘   │
                    └───────┼─────────┼─────────┼────────┘
                            │         │         │
                    ┌───────▼─────────▼─────────▼────────┐
                    │         TRADING ENGINE              │
                    │  ┌─────────────────────────────┐   │
                    │  │     delegate_to_plugin()    │   │
                    │  └─────────────┬───────────────┘   │
                    └───────────────┼────────────────────┘
                                    │
                    ┌───────────────▼────────────────────┐
                    │           SERVICE API              │
                    │  ┌─────┬─────┬─────┬─────┬─────┐  │
                    │  │Order│Risk │Trend│Market│Tele │  │
                    │  │Exec │Mgmt │Mgmt │Data │gram │  │
                    │  └──┬──┴──┬──┴──┬──┴──┬──┴──┬──┘  │
                    └─────┼─────┼─────┼─────┼─────┼─────┘
                          │     │     │     │     │
                    ┌─────▼─────▼─────▼─────▼─────▼─────┐
                    │         PLUGIN REGISTRY            │
                    │  ┌─────────────────────────────┐   │
                    │  │  V3 Combined │ V6 1M/5M/15M/1H │
                    │  └─────────────────────────────┘   │
                    └────────────────────────────────────┘
                                    │
                    ┌───────────────▼────────────────────┐
                    │           MT5 CLIENT               │
                    │  ┌─────────────────────────────┐   │
                    │  │    MetaTrader 5 Terminal    │   │
                    │  └─────────────────────────────┘   │
                    └────────────────────────────────────┘
```

## Trading Engine (Orchestrator)

### Class Definition
```python
class TradingEngine:
    def __init__(self, config: Config, risk_manager: RiskManager, 
                 mt5_client: MT5Client, telegram_bot, 
                 alert_processor: AlertProcessor):
```

### Key Components
| Component | Purpose |
|-----------|---------|
| `plugin_registry` | Manages plugin discovery and loading |
| `service_api` | Unified service facade |
| `shadow_manager` | Shadow mode execution |
| `telegram_manager` | 3-bot notification system |
| `voice_alerts` | Voice notification system |
| `autonomous_manager` | Safety and risk controls |

### Plugin Delegation
```python
async def delegate_to_plugin(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delegate signal processing to the appropriate plugin.
    This is the ONLY entry point for plugin-based signal processing.
    """
    # Find the right plugin
    plugin = self.plugin_registry.get_plugin_for_signal(signal_data)
    
    if not plugin:
        return {"status": "error", "message": "no_plugin_found"}
    
    # Route to appropriate handler
    alert_type = signal_data.get('type', '')
    
    if 'entry' in alert_type.lower():
        result = await plugin.process_entry_signal(signal_data)
    elif 'exit' in alert_type.lower():
        result = await plugin.process_exit_signal(signal_data)
    elif 'reversal' in alert_type.lower():
        result = await plugin.process_reversal_signal(signal_data)
    else:
        result = await plugin.process_signal(signal_data)
    
    # Track metrics
    self._track_plugin_execution(plugin.plugin_id, signal_data, result)
    
    return result
```

### Plugin Failure Handling
```python
def _handle_plugin_failure(self, plugin_id: str, error: Exception):
    """Handle plugin failure - log, notify, potentially disable"""
    self._plugin_failures[plugin_id] = self._plugin_failures.get(plugin_id, 0) + 1
    
    # If too many failures, disable plugin
    if self._plugin_failures[plugin_id] >= 5:
        plugin = self.plugin_registry.get_plugin(plugin_id)
        if plugin:
            plugin.enabled = False
            self.telegram_bot.send_message(
                f"Plugin {plugin_id} disabled due to repeated failures"
            )
```

## ServiceAPI (Unified Facade)

### Class Definition
```python
class ServiceAPI:
    """
    Unified Service API - Single point of entry for all plugin operations.
    
    Plugins should ONLY interact with this class, never directly with
    MT5, RiskManager, or other managers.
    """
    VERSION = "3.0.0"
```

### Service Registration
```python
def register_service(self, name: str, service: Any, health_check: Optional[Callable] = None):
    """Register a service with the API."""
    registration = ServiceRegistration(
        name=name,
        service=service,
        health_check=health_check
    )
    self._service_registry[name] = registration
    self._service_metrics[name] = ServiceMetrics()
```

### Registered Services
| Service | Property | Purpose |
|---------|----------|---------|
| `reentry` | `reentry_service` | SL Hunt, TP Continuation |
| `dual_order` | `dual_order_service` | Order A/B management |
| `profit_booking` | `profit_booking_service` | Profit chains |
| `autonomous` | `autonomous_service` | Safety checks |
| `telegram` | `telegram_service` | Notifications |
| `database` | `database_service` | Data persistence |

### Service Call with Metrics
```python
async def call_service(self, service_name: str, method_name: str, *args, **kwargs) -> Any:
    """Call a service method with metrics tracking."""
    service = self.get_service(service_name)
    method = getattr(service, method_name, None)
    
    # Track metrics
    metrics = self._service_metrics.get(service_name)
    if metrics:
        metrics.calls += 1
        metrics.last_call = datetime.now()
    
    start_time = datetime.now()
    try:
        if asyncio.iscoroutinefunction(method):
            result = await method(*args, **kwargs)
        else:
            result = method(*args, **kwargs)
        
        if metrics:
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            metrics.total_time_ms += elapsed
        
        return result
    except Exception as e:
        if metrics:
            metrics.errors += 1
            metrics.last_error = str(e)
        raise
```

### Health Checks
```python
async def check_health(self) -> Dict[str, bool]:
    """Check health of all registered services."""
    results = {}
    
    for name, registration in self._service_registry.items():
        if registration.health_check:
            try:
                results[name] = await registration.health_check()
                registration.is_healthy = results[name]
            except Exception:
                results[name] = False
                registration.is_healthy = False
        else:
            results[name] = True
    
    return results
```

## Plugin System

### Base Plugin
```python
class BaseLogicPlugin(ABC):
    """Base class for all trading logic plugins."""
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], service_api):
        self.plugin_id = plugin_id
        self.config = config
        self.service_api = service_api
        self.enabled = config.get("enabled", True)
        self.db_path = f"data/zepix_{plugin_id}.db"
    
    @abstractmethod
    async def process_entry_signal(self, alert: Any) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def process_exit_signal(self, alert: Any) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def process_reversal_signal(self, alert: Any) -> Dict[str, Any]:
        pass
```

### Plugin Interfaces
| Interface | Methods |
|-----------|---------|
| `ISignalProcessor` | `get_supported_strategies()`, `can_process_signal()`, `process_signal()` |
| `IOrderExecutor` | `execute_order()`, `modify_order()`, `close_order()` |
| `IReentryCapable` | `on_sl_hit()`, `on_tp_hit()`, `on_exit()`, `on_recovery_signal()` |
| `IDualOrderCapable` | `create_dual_orders()`, `get_order_a_config()`, `get_order_b_config()` |
| `IProfitBookingCapable` | `create_profit_chain()`, `on_profit_target_hit()`, `on_chain_sl_hit()` |
| `IAutonomousCapable` | `check_recovery_allowed()`, `activate_reverse_shield()` |
| `IDatabaseCapable` | `get_database_config()`, `initialize_database()`, `execute_query()` |

### Plugin Registry
```python
class PluginRegistry:
    """Manages plugin discovery, loading, and routing."""
    
    def discover_plugins(self):
        """Discover plugins in src/logic_plugins/"""
        pass
    
    def load_all_plugins(self):
        """Load and initialize all discovered plugins"""
        pass
    
    def get_plugin_for_signal(self, signal_data: Dict) -> Optional[BaseLogicPlugin]:
        """Find the appropriate plugin for a signal"""
        pass
```

## 3-Bot Telegram System

### Architecture
```
┌─────────────────────────────────────────────────────────┐
│                  TELEGRAM CLUSTER                        │
├─────────────────┬─────────────────┬─────────────────────┤
│  CONTROLLER BOT │  NOTIFIER BOT   │   ANALYTICS BOT     │
│  (Commands)     │  (Alerts)       │   (Reports)         │
├─────────────────┼─────────────────┼─────────────────────┤
│  /start         │  Trade Opened   │   Daily Summary     │
│  /status        │  Trade Closed   │   Performance       │
│  /plugin        │  SL Hit         │   Risk Analysis     │
│  /config        │  TP Hit         │   Plugin Stats      │
│  /pause         │  Recovery       │   Shadow Results    │
│  /resume        │  Errors         │   Trend Analysis    │
└─────────────────┴─────────────────┴─────────────────────┘
```

### Multi-Telegram Manager
```python
class MultiTelegramManager:
    """Manages the 3-bot Telegram cluster."""
    
    def __init__(self, config: Dict):
        self.controller_bot = ControllerBot(config.get("controller", {}))
        self.notifier_bot = NotifierBot(config.get("notifier", {}))
        self.analytics_bot = AnalyticsBot(config.get("analytics", {}))
    
    async def send_notification_async(self, notification_type: str, message: str, **kwargs):
        """Route notification to appropriate bot."""
        if notification_type in ['trade_opened', 'trade_closed', 'sl_hit', 'tp_hit']:
            await self.notifier_bot.send_message(message)
        elif notification_type in ['daily_summary', 'performance', 'analytics']:
            await self.analytics_bot.send_message(message)
        else:
            await self.controller_bot.send_message(message)
```

## Shadow Mode System

### Shadow Mode Manager
```python
class ShadowModeManager:
    """Manages shadow mode execution for paper trading."""
    
    def __init__(self, config: Dict):
        self._mode = ExecutionMode.LIVE
        self._shadow_plugins: Set[str] = set()
        self._virtual_orders: Dict[str, Dict] = {}
        self._plugin_decisions: Dict[str, List] = {}
    
    def set_mode(self, mode: ExecutionMode):
        """Set execution mode (LIVE, SHADOW, HYBRID)"""
        self._mode = mode
    
    def is_plugin_in_shadow(self, plugin_id: str) -> bool:
        """Check if plugin is in shadow mode"""
        return plugin_id in self._shadow_plugins
    
    def record_virtual_order(self, plugin_id: str, signal_id: str, order_params: Dict):
        """Record a virtual order for shadow mode tracking"""
        pass
```

### Execution Modes
| Mode | Description |
|------|-------------|
| `LIVE` | All plugins execute real trades |
| `SHADOW` | All plugins execute virtual trades |
| `HYBRID` | Some plugins live, some shadow |

## Data Flow

### Signal Processing Flow
```
1. TradingView Alert
   │
2. Webhook Handler (src/api/webhook_handler.py)
   │
3. Alert Processor (src/processors/alert_processor.py)
   │
4. Trading Engine (src/core/trading_engine.py)
   │
5. delegate_to_plugin()
   │
6. Plugin Registry → Find Plugin
   │
7. Plugin.process_entry_signal()
   │
8. ServiceAPI → Execute Order
   │
9. MT5 Client → Place Order
   │
10. Telegram Notification
```

### Order Execution Flow
```
1. Plugin creates order config
   │
2. ServiceAPI.place_order()
   │
3. Risk validation
   │
4. MT5Client.place_order()
   │
5. Order confirmation
   │
6. Database record
   │
7. Telegram notification
```

## Configuration

### Main Config Structure
```json
{
    "plugin_system": {
        "enabled": true,
        "auto_discover": true,
        "plugin_dir": "src/logic_plugins"
    },
    "telegram": {
        "controller": {
            "token": "...",
            "chat_id": "..."
        },
        "notifier": {
            "token": "...",
            "chat_id": "..."
        },
        "analytics": {
            "token": "...",
            "chat_id": "..."
        }
    },
    "shadow_mode": {
        "enabled": false,
        "default_mode": "LIVE",
        "shadow_plugins": []
    }
}
```

## Key Design Principles

### 1. Single Responsibility
Each component has a single, well-defined purpose:
- TradingEngine: Orchestration
- ServiceAPI: Service facade
- Plugins: Signal processing
- MT5Client: Order execution

### 2. Dependency Injection
Services are injected into plugins via ServiceAPI:
```python
plugin.set_service_api(service_api)
```

### 3. Interface Segregation
Plugins implement only the interfaces they need:
```python
class V3CombinedPlugin(BaseLogicPlugin, ISignalProcessor, IOrderExecutor, 
                       IReentryCapable, IDualOrderCapable, ...):
```

### 4. Database Isolation
Each plugin has its own isolated database:
```python
db_path = f"data/zepix_{plugin_id}.db"
```

### 5. Graceful Degradation
If a service fails, the system continues with fallbacks:
```python
if self._market_service:
    return await self._market_service.get_current_spread(symbol)
return 999.9  # Fallback value
```

## Monitoring and Metrics

### Service Metrics
```python
@dataclass
class ServiceMetrics:
    calls: int = 0
    errors: int = 0
    total_time_ms: float = 0.0
    last_call: Optional[datetime] = None
    last_error: Optional[str] = None
    
    @property
    def avg_time_ms(self) -> float:
        return self.total_time_ms / self.calls if self.calls > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        return (self.errors / self.calls * 100) if self.calls > 0 else 0.0
```

### Plugin Health Monitor
```python
class PluginHealthMonitor:
    """Monitors plugin health and performance."""
    
    def check_plugin_health(self, plugin_id: str) -> Dict:
        """Check health of a specific plugin"""
        pass
    
    def get_all_plugin_status(self) -> Dict[str, Dict]:
        """Get status of all plugins"""
        pass
```

## Version History
- v5.0.0 (2026-01-14): Initial V5 Hybrid Plugin Architecture
- Migrated from monolithic trading_engine.py
- Added plugin system with ServiceAPI
- Added 3-bot Telegram cluster
- Added shadow mode support
- Added comprehensive monitoring
