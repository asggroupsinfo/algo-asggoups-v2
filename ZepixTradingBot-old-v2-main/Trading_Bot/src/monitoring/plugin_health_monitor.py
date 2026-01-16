"""
Plugin Health Monitoring System

Monitors the health and performance of all V3 and V6 plugins in real-time,
detects anomalies, and alerts operators before issues escalate.

Health Dimensions:
1. Availability: Plugin running and responsive
2. Performance: Execution times within SLA
3. Accuracy: Signal quality and trade success rates
4. Resource Usage: Memory, CPU, database connections
5. Error Rate: Exceptions, failed operations

Version: 1.0.0
Date: 2026-01-14
"""

import asyncio
import logging
import sqlite3
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Plugin health status levels"""
    HEALTHY = "HEALTHY"
    STALE = "STALE"
    HUNG = "HUNG"
    DEAD = "DEAD"
    UNKNOWN = "UNKNOWN"


class AlertLevel(Enum):
    """Alert severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class PluginAvailabilityMetrics:
    """
    Plugin availability metrics
    """
    plugin_id: str
    is_running: bool = False
    is_responsive: bool = False
    last_heartbeat: datetime = field(default_factory=datetime.now)
    uptime_seconds: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    
    @property
    def health_status(self) -> HealthStatus:
        """Calculate health status based on availability metrics"""
        if not self.is_running:
            return HealthStatus.DEAD
        if not self.is_responsive:
            return HealthStatus.HUNG
        
        seconds_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
        if seconds_since_heartbeat > 300:  # 5 minutes
            return HealthStatus.STALE
        
        return HealthStatus.HEALTHY


@dataclass
class PluginPerformanceMetrics:
    """
    Plugin performance metrics
    """
    plugin_id: str
    avg_execution_time_ms: float = 0.0
    p95_execution_time_ms: float = 0.0
    p99_execution_time_ms: float = 0.0
    signals_processed_1h: int = 0
    orders_placed_1h: int = 0
    signal_accuracy_pct: float = 0.0
    win_rate_pct: float = 0.0
    
    # Execution time history for percentile calculation
    _execution_times: List[float] = field(default_factory=list)
    
    def record_execution_time(self, time_ms: float):
        """Record an execution time for percentile calculation"""
        self._execution_times.append(time_ms)
        # Keep last 1000 samples
        if len(self._execution_times) > 1000:
            self._execution_times = self._execution_times[-1000:]
        
        # Recalculate percentiles
        if self._execution_times:
            sorted_times = sorted(self._execution_times)
            n = len(sorted_times)
            self.avg_execution_time_ms = sum(sorted_times) / n
            self.p95_execution_time_ms = sorted_times[int(n * 0.95)] if n > 0 else 0
            self.p99_execution_time_ms = sorted_times[int(n * 0.99)] if n > 0 else 0


@dataclass
class PluginResourceMetrics:
    """
    Plugin resource usage metrics
    """
    plugin_id: str
    memory_usage_mb: float = 0.0
    memory_limit_mb: float = 1024.0
    cpu_usage_pct: float = 0.0
    db_connections_active: int = 0
    db_connections_max: int = 5
    db_query_time_avg_ms: float = 0.0
    open_file_handles: int = 0


@dataclass
class PluginErrorMetrics:
    """
    Plugin error metrics
    """
    plugin_id: str
    total_errors: int = 0
    critical_errors: int = 0
    warnings: int = 0
    error_rate_pct: float = 0.0
    last_error_message: str = ""
    last_error_timestamp: datetime = field(default_factory=lambda: datetime.min)
    
    # Error history
    _error_history: List[Dict] = field(default_factory=list)
    
    def record_error(self, message: str, is_critical: bool = False):
        """Record an error"""
        self._error_history.append({
            "message": message,
            "timestamp": datetime.now(),
            "is_critical": is_critical
        })
        
        # Keep last 100 errors
        if len(self._error_history) > 100:
            self._error_history = self._error_history[-100:]
        
        self.last_error_message = message
        self.last_error_timestamp = datetime.now()
        self.total_errors += 1
        if is_critical:
            self.critical_errors += 1


@dataclass
class HealthSnapshot:
    """
    Complete health snapshot for a plugin at a point in time
    """
    plugin_id: str
    timestamp: datetime
    availability: PluginAvailabilityMetrics
    performance: PluginPerformanceMetrics
    resources: PluginResourceMetrics
    errors: PluginErrorMetrics
    
    @property
    def health_status(self) -> HealthStatus:
        """Get overall health status"""
        return self.availability.health_status
    
    @property
    def is_healthy(self) -> bool:
        """Check if plugin is healthy"""
        return self.health_status == HealthStatus.HEALTHY


@dataclass
class HealthAlert:
    """
    Health alert record
    """
    id: int = 0
    plugin_id: str = ""
    alert_level: AlertLevel = AlertLevel.INFO
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class PluginHealthMonitor:
    """
    Central health monitoring system for all plugins.
    
    Features:
    - Collect health metrics every 30 seconds
    - Detect anomalies using thresholds
    - Trigger alerts (Telegram + logs)
    - Store health history in database
    - Auto-restart crashed plugins
    - Zombie plugin detection
    """
    
    def __init__(
        self,
        plugin_registry=None,
        telegram_manager=None,
        db_path: str = "data/zepix_health.db",
        config: Dict = None
    ):
        """
        Initialize health monitor.
        
        Args:
            plugin_registry: PluginRegistry instance
            telegram_manager: MultiTelegramManager instance
            db_path: Path to health database
            config: Configuration dict
        """
        self.plugin_registry = plugin_registry
        self.telegram_manager = telegram_manager
        self.db_path = db_path
        self.config = config or {}
        
        # Health thresholds
        self.thresholds = {
            'max_execution_time_ms': self.config.get('max_execution_time_ms', 5000),
            'max_error_rate_pct': self.config.get('max_error_rate_pct', 5.0),
            'max_memory_usage_mb': self.config.get('max_memory_usage_mb', 500),
            'max_cpu_usage_pct': self.config.get('max_cpu_usage_pct', 80.0),
            'min_heartbeat_interval_sec': self.config.get('min_heartbeat_interval_sec', 300),
            'zombie_detection_threshold_sec': self.config.get('zombie_detection_threshold_sec', 600)
        }
        
        # Monitoring state
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._lock = threading.RLock()
        
        # Health data storage
        self._health_snapshots: Dict[str, deque] = {}  # plugin_id -> deque of snapshots
        self._latest_snapshots: Dict[str, HealthSnapshot] = {}  # plugin_id -> latest snapshot
        self._alerts: List[HealthAlert] = []
        self._alert_id_counter = 0
        
        # Alert throttling (prevent spam)
        self._last_alert_time: Dict[tuple, datetime] = {}  # (plugin_id, alert_type) -> timestamp
        self._alert_cooldown_sec = self.config.get('alert_cooldown_sec', 300)  # 5 minutes
        
        # Auto-restart tracking
        self._restart_attempts: Dict[str, int] = {}  # plugin_id -> restart count
        self._max_restart_attempts = self.config.get('max_restart_attempts', 3)
        
        # Callbacks
        self._alert_callbacks: List[Callable] = []
        self._restart_callbacks: List[Callable] = []
        
        # Initialize database
        self._init_database()
        
        logger.info("[PluginHealthMonitor] Initialized")
    
    def _init_database(self):
        """Initialize health database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Plugin health snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plugin_health_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_running BOOLEAN,
                    is_responsive BOOLEAN,
                    health_status TEXT,
                    uptime_seconds INTEGER,
                    avg_execution_time_ms REAL,
                    p95_execution_time_ms REAL,
                    signals_processed_1h INTEGER,
                    win_rate_pct REAL,
                    memory_usage_mb REAL,
                    cpu_usage_pct REAL,
                    db_connections_active INTEGER,
                    total_errors INTEGER,
                    error_rate_pct REAL
                )
            """)
            
            # Create index for efficient queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_health_plugin_time 
                ON plugin_health_snapshots (plugin_id, timestamp)
            """)
            
            # Health alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    alert_level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at DATETIME
                )
            """)
            
            # Create index for alerts
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_plugin_time 
                ON health_alerts (plugin_id, timestamp)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("[PluginHealthMonitor] Database initialized")
            
        except Exception as e:
            logger.error(f"[PluginHealthMonitor] Database init error: {e}")
    
    async def start_monitoring(self):
        """Start background health monitoring loop"""
        if self._running:
            logger.warning("[PluginHealthMonitor] Already running")
            return
        
        self._running = True
        logger.info("[PluginHealthMonitor] Starting health monitoring...")
        
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self._running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("[PluginHealthMonitor] Stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        check_interval = self.config.get('check_interval_sec', 30)
        
        while self._running:
            try:
                await self._collect_and_analyze_all_plugins()
                await asyncio.sleep(check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[PluginHealthMonitor] Loop error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_and_analyze_all_plugins(self):
        """Collect health metrics for all plugins and analyze"""
        if not self.plugin_registry:
            return
        
        plugins = self.plugin_registry.get_all_plugins()
        
        for plugin_id, plugin in plugins.items():
            try:
                # Collect all metric types
                availability = await self._collect_availability_metrics(plugin_id, plugin)
                performance = await self._collect_performance_metrics(plugin_id, plugin)
                resources = await self._collect_resource_metrics(plugin_id, plugin)
                errors = await self._collect_error_metrics(plugin_id, plugin)
                
                # Create snapshot
                snapshot = HealthSnapshot(
                    plugin_id=plugin_id,
                    timestamp=datetime.now(),
                    availability=availability,
                    performance=performance,
                    resources=resources,
                    errors=errors
                )
                
                # Store snapshot
                self._store_snapshot(snapshot)
                
                # Analyze for anomalies
                await self._analyze_health(snapshot)
                
                # Check for zombie plugins
                await self._check_zombie_plugin(plugin_id, availability)
                
            except Exception as e:
                logger.error(f"[PluginHealthMonitor] Failed to collect metrics for {plugin_id}: {e}")
    
    async def _collect_availability_metrics(
        self,
        plugin_id: str,
        plugin
    ) -> PluginAvailabilityMetrics:
        """Check if plugin is alive and responsive"""
        metrics = PluginAvailabilityMetrics(plugin_id=plugin_id)
        
        try:
            # Check if plugin is running (has enabled attribute)
            metrics.is_running = getattr(plugin, 'enabled', True)
            
            # Check responsiveness via ping or get_status
            if hasattr(plugin, 'ping'):
                try:
                    ping_result = await plugin.ping() if asyncio.iscoroutinefunction(plugin.ping) else plugin.ping()
                    metrics.is_responsive = bool(ping_result)
                except Exception:
                    metrics.is_responsive = False
            elif hasattr(plugin, 'get_status'):
                try:
                    status = plugin.get_status()
                    metrics.is_responsive = status is not None
                except Exception:
                    metrics.is_responsive = False
            else:
                # Assume responsive if plugin object exists
                metrics.is_responsive = True
            
            # Get last activity time
            if hasattr(plugin, 'last_activity_time'):
                metrics.last_heartbeat = plugin.last_activity_time
            elif hasattr(plugin, '_last_heartbeat'):
                metrics.last_heartbeat = plugin._last_heartbeat
            else:
                metrics.last_heartbeat = datetime.now()
            
            # Calculate uptime
            if hasattr(plugin, 'start_time'):
                metrics.start_time = plugin.start_time
                metrics.uptime_seconds = int((datetime.now() - plugin.start_time).total_seconds())
            elif hasattr(plugin, '_start_time'):
                metrics.start_time = plugin._start_time
                metrics.uptime_seconds = int((datetime.now() - plugin._start_time).total_seconds())
            
        except Exception as e:
            logger.warning(f"[PluginHealthMonitor] Plugin {plugin_id} availability check failed: {e}")
            metrics.is_running = False
            metrics.is_responsive = False
        
        return metrics
    
    async def _collect_performance_metrics(
        self,
        plugin_id: str,
        plugin
    ) -> PluginPerformanceMetrics:
        """Collect performance stats from plugin"""
        metrics = PluginPerformanceMetrics(plugin_id=plugin_id)
        
        try:
            # Try to get performance stats from plugin
            if hasattr(plugin, 'get_performance_stats'):
                stats = plugin.get_performance_stats()
                if asyncio.iscoroutine(stats):
                    stats = await stats
                
                metrics.avg_execution_time_ms = stats.get('avg_execution_ms', 0)
                metrics.p95_execution_time_ms = stats.get('p95_execution_ms', 0)
                metrics.p99_execution_time_ms = stats.get('p99_execution_ms', 0)
                metrics.signals_processed_1h = stats.get('signals_1h', 0)
                metrics.orders_placed_1h = stats.get('orders_1h', 0)
                metrics.signal_accuracy_pct = stats.get('signal_accuracy', 0)
                metrics.win_rate_pct = stats.get('win_rate', 0)
            
            # Try to get stats from plugin status
            elif hasattr(plugin, 'get_status'):
                status = plugin.get_status()
                if 'stats' in status:
                    stats = status['stats']
                    metrics.signals_processed_1h = stats.get('signals_processed', 0)
                    metrics.orders_placed_1h = stats.get('orders_placed', 0)
                    metrics.win_rate_pct = stats.get('win_rate', 0)
            
        except Exception as e:
            logger.warning(f"[PluginHealthMonitor] Plugin {plugin_id} performance check failed: {e}")
        
        return metrics
    
    async def _collect_resource_metrics(
        self,
        plugin_id: str,
        plugin
    ) -> PluginResourceMetrics:
        """Collect resource usage from plugin"""
        metrics = PluginResourceMetrics(plugin_id=plugin_id)
        
        try:
            # Try to get resource stats from plugin
            if hasattr(plugin, 'get_resource_stats'):
                stats = plugin.get_resource_stats()
                if asyncio.iscoroutine(stats):
                    stats = await stats
                
                metrics.memory_usage_mb = stats.get('memory_mb', 0)
                metrics.cpu_usage_pct = stats.get('cpu_pct', 0)
                metrics.db_connections_active = stats.get('db_connections', 0)
            
            # Try to get DB connection stats
            if hasattr(plugin, 'get_db_connection_stats'):
                db_stats = plugin.get_db_connection_stats()
                if asyncio.iscoroutine(db_stats):
                    db_stats = await db_stats
                
                metrics.db_connections_active = db_stats.get('active', 0)
                metrics.db_connections_max = db_stats.get('max', 5)
                metrics.db_query_time_avg_ms = db_stats.get('avg_query_time_ms', 0)
            
        except Exception as e:
            logger.warning(f"[PluginHealthMonitor] Plugin {plugin_id} resource check failed: {e}")
        
        return metrics
    
    async def _collect_error_metrics(
        self,
        plugin_id: str,
        plugin
    ) -> PluginErrorMetrics:
        """Collect error stats from plugin"""
        metrics = PluginErrorMetrics(plugin_id=plugin_id)
        
        try:
            # Try to get error stats from plugin
            if hasattr(plugin, 'get_error_stats'):
                stats = plugin.get_error_stats()
                if asyncio.iscoroutine(stats):
                    stats = await stats
                
                metrics.total_errors = stats.get('total_errors_1h', 0)
                metrics.critical_errors = stats.get('critical_errors_1h', 0)
                metrics.warnings = stats.get('warnings_1h', 0)
                metrics.error_rate_pct = stats.get('error_rate_pct', 0)
                metrics.last_error_message = stats.get('last_error_message', '')
                
                if 'last_error_time' in stats and stats['last_error_time']:
                    metrics.last_error_timestamp = stats['last_error_time']
            
            # Try to get from plugin status
            elif hasattr(plugin, 'get_status'):
                status = plugin.get_status()
                if 'errors' in status:
                    metrics.total_errors = status['errors'].get('total', 0)
                    metrics.last_error_message = status['errors'].get('last_message', '')
            
        except Exception as e:
            logger.warning(f"[PluginHealthMonitor] Plugin {plugin_id} error check failed: {e}")
        
        return metrics
    
    def _store_snapshot(self, snapshot: HealthSnapshot):
        """Store health snapshot in memory and database"""
        plugin_id = snapshot.plugin_id
        
        with self._lock:
            # Store in memory (keep last 100 snapshots per plugin)
            if plugin_id not in self._health_snapshots:
                self._health_snapshots[plugin_id] = deque(maxlen=100)
            
            self._health_snapshots[plugin_id].append(snapshot)
            self._latest_snapshots[plugin_id] = snapshot
        
        # Store in database (async-safe)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO plugin_health_snapshots (
                    plugin_id, timestamp, is_running, is_responsive, health_status,
                    uptime_seconds, avg_execution_time_ms, p95_execution_time_ms,
                    signals_processed_1h, win_rate_pct, memory_usage_mb, cpu_usage_pct,
                    db_connections_active, total_errors, error_rate_pct
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plugin_id,
                snapshot.timestamp.isoformat(),
                snapshot.availability.is_running,
                snapshot.availability.is_responsive,
                snapshot.health_status.value,
                snapshot.availability.uptime_seconds,
                snapshot.performance.avg_execution_time_ms,
                snapshot.performance.p95_execution_time_ms,
                snapshot.performance.signals_processed_1h,
                snapshot.performance.win_rate_pct,
                snapshot.resources.memory_usage_mb,
                snapshot.resources.cpu_usage_pct,
                snapshot.resources.db_connections_active,
                snapshot.errors.total_errors,
                snapshot.errors.error_rate_pct
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"[PluginHealthMonitor] Failed to store snapshot: {e}")
    
    async def _analyze_health(self, snapshot: HealthSnapshot):
        """Analyze metrics and trigger alerts if needed"""
        plugin_id = snapshot.plugin_id
        
        # Check availability
        if snapshot.health_status != HealthStatus.HEALTHY:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.CRITICAL,
                f"Plugin {plugin_id} is {snapshot.health_status.value}"
            )
        
        # Check performance
        if snapshot.performance.p95_execution_time_ms > self.thresholds['max_execution_time_ms']:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.WARNING,
                f"Plugin {plugin_id} slow: P95={snapshot.performance.p95_execution_time_ms:.0f}ms"
            )
        
        # Check resources
        if snapshot.resources.memory_usage_mb > self.thresholds['max_memory_usage_mb']:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.WARNING,
                f"Plugin {plugin_id} high memory: {snapshot.resources.memory_usage_mb:.1f}MB"
            )
        
        if snapshot.resources.cpu_usage_pct > self.thresholds['max_cpu_usage_pct']:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.WARNING,
                f"Plugin {plugin_id} high CPU: {snapshot.resources.cpu_usage_pct:.1f}%"
            )
        
        # Check errors
        if snapshot.errors.error_rate_pct > self.thresholds['max_error_rate_pct']:
            await self._trigger_alert(
                plugin_id,
                AlertLevel.HIGH,
                f"Plugin {plugin_id} high error rate: {snapshot.errors.error_rate_pct:.1f}%"
            )
    
    async def _check_zombie_plugin(self, plugin_id: str, availability: PluginAvailabilityMetrics):
        """Check for zombie (frozen/unresponsive) plugins and attempt restart"""
        if availability.health_status in [HealthStatus.DEAD, HealthStatus.HUNG]:
            # Check if we should attempt restart
            restart_count = self._restart_attempts.get(plugin_id, 0)
            
            if restart_count < self._max_restart_attempts:
                logger.warning(f"[PluginHealthMonitor] Zombie plugin detected: {plugin_id}, attempting restart ({restart_count + 1}/{self._max_restart_attempts})")
                
                await self._trigger_alert(
                    plugin_id,
                    AlertLevel.CRITICAL,
                    f"Zombie plugin detected: {plugin_id}. Attempting auto-restart."
                )
                
                # Attempt restart
                success = await self._restart_plugin(plugin_id)
                
                if success:
                    self._restart_attempts[plugin_id] = 0  # Reset on success
                    await self._trigger_alert(
                        plugin_id,
                        AlertLevel.INFO,
                        f"Plugin {plugin_id} successfully restarted."
                    )
                else:
                    self._restart_attempts[plugin_id] = restart_count + 1
            else:
                await self._trigger_alert(
                    plugin_id,
                    AlertLevel.CRITICAL,
                    f"Plugin {plugin_id} failed to restart after {self._max_restart_attempts} attempts. Manual intervention required."
                )
    
    async def _restart_plugin(self, plugin_id: str) -> bool:
        """Attempt to restart a crashed plugin"""
        try:
            if not self.plugin_registry:
                return False
            
            # Unload plugin
            if plugin_id in self.plugin_registry.plugins:
                plugin = self.plugin_registry.plugins[plugin_id]
                
                # Call shutdown if available
                if hasattr(plugin, 'shutdown'):
                    try:
                        if asyncio.iscoroutinefunction(plugin.shutdown):
                            await plugin.shutdown()
                        else:
                            plugin.shutdown()
                    except Exception as e:
                        logger.warning(f"[PluginHealthMonitor] Shutdown error for {plugin_id}: {e}")
                
                # Remove from registry
                del self.plugin_registry.plugins[plugin_id]
            
            # Reload plugin
            success = self.plugin_registry.load_plugin(plugin_id)
            
            # Notify callbacks
            for callback in self._restart_callbacks:
                try:
                    callback(plugin_id, success)
                except Exception as e:
                    logger.error(f"[PluginHealthMonitor] Restart callback error: {e}")
            
            return success
            
        except Exception as e:
            logger.error(f"[PluginHealthMonitor] Failed to restart plugin {plugin_id}: {e}")
            return False
    
    async def _trigger_alert(
        self,
        plugin_id: str,
        level: AlertLevel,
        message: str
    ):
        """Send alert if not throttled"""
        alert_key = (plugin_id, message)
        
        # Check if recently alerted (throttling)
        if alert_key in self._last_alert_time:
            elapsed = (datetime.now() - self._last_alert_time[alert_key]).total_seconds()
            if elapsed < self._alert_cooldown_sec:
                return  # Throttled
        
        # Create alert record
        with self._lock:
            self._alert_id_counter += 1
            alert = HealthAlert(
                id=self._alert_id_counter,
                plugin_id=plugin_id,
                alert_level=level,
                message=message,
                timestamp=datetime.now()
            )
            self._alerts.append(alert)
            
            # Keep last 1000 alerts
            if len(self._alerts) > 1000:
                self._alerts = self._alerts[-1000:]
        
        # Store in database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO health_alerts (plugin_id, alert_level, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (plugin_id, level.value, message, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"[PluginHealthMonitor] Failed to store alert: {e}")
        
        # Send Telegram notification
        if self.telegram_manager:
            emoji = {
                AlertLevel.CRITICAL: "🚨",
                AlertLevel.HIGH: "⚠️",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.INFO: "ℹ️"
            }.get(level, "ℹ️")
            
            try:
                await self.telegram_manager.send_notification(
                    text=f"{emoji} <b>Health Alert</b>\n{message}",
                    priority="CRITICAL" if level == AlertLevel.CRITICAL else "HIGH"
                )
            except Exception as e:
                logger.error(f"[PluginHealthMonitor] Failed to send Telegram alert: {e}")
        
        # Notify callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"[PluginHealthMonitor] Alert callback error: {e}")
        
        # Update throttle timestamp
        self._last_alert_time[alert_key] = datetime.now()
        
        logger.warning(f"[PluginHealthMonitor] Alert triggered: {message}")
    
    def register_alert_callback(self, callback: Callable):
        """Register callback for health alerts"""
        self._alert_callbacks.append(callback)
    
    def register_restart_callback(self, callback: Callable):
        """Register callback for plugin restarts"""
        self._restart_callbacks.append(callback)
    
    def get_latest_snapshots(self) -> List[HealthSnapshot]:
        """Get latest health snapshots for all plugins"""
        with self._lock:
            return list(self._latest_snapshots.values())
    
    def get_plugin_snapshot(self, plugin_id: str) -> Optional[HealthSnapshot]:
        """Get latest snapshot for specific plugin"""
        with self._lock:
            return self._latest_snapshots.get(plugin_id)
    
    def get_plugin_history(self, plugin_id: str, limit: int = 100) -> List[HealthSnapshot]:
        """Get health history for specific plugin"""
        with self._lock:
            if plugin_id in self._health_snapshots:
                snapshots = list(self._health_snapshots[plugin_id])
                return snapshots[-limit:]
            return []
    
    def get_recent_alerts(self, limit: int = 10, plugin_id: str = None) -> List[HealthAlert]:
        """Get recent health alerts"""
        with self._lock:
            alerts = self._alerts
            
            if plugin_id:
                alerts = [a for a in alerts if a.plugin_id == plugin_id]
            
            return alerts[-limit:]
    
    def get_unresolved_alerts(self) -> List[HealthAlert]:
        """Get all unresolved alerts"""
        with self._lock:
            return [a for a in self._alerts if not a.resolved]
    
    def resolve_alert(self, alert_id: int):
        """Mark an alert as resolved"""
        with self._lock:
            for alert in self._alerts:
                if alert.id == alert_id:
                    alert.resolved = True
                    alert.resolved_at = datetime.now()
                    break
        
        # Update in database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE health_alerts 
                SET resolved = TRUE, resolved_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), alert_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"[PluginHealthMonitor] Failed to resolve alert: {e}")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        snapshots = self.get_latest_snapshots()
        
        healthy_count = sum(1 for s in snapshots if s.is_healthy)
        unhealthy_count = len(snapshots) - healthy_count
        
        return {
            "total_plugins": len(snapshots),
            "healthy": healthy_count,
            "unhealthy": unhealthy_count,
            "unresolved_alerts": len(self.get_unresolved_alerts()),
            "last_check": datetime.now().isoformat(),
            "plugins": {
                s.plugin_id: {
                    "status": s.health_status.value,
                    "uptime": s.availability.uptime_seconds,
                    "error_rate": s.errors.error_rate_pct
                }
                for s in snapshots
            }
        }
    
    def format_health_dashboard(self) -> str:
        """Format health dashboard for Telegram display"""
        snapshots = self.get_latest_snapshots()
        
        if not snapshots:
            return "🏥 <b>Plugin Health Dashboard</b>\n\nNo plugins registered."
        
        text = "🏥 <b>Plugin Health Dashboard</b>\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for snapshot in snapshots:
            status_emoji = {
                HealthStatus.HEALTHY: "🟢",
                HealthStatus.STALE: "🟡",
                HealthStatus.HUNG: "🟠",
                HealthStatus.DEAD: "🔴",
                HealthStatus.UNKNOWN: "⚪"
            }.get(snapshot.health_status, "⚪")
            
            uptime_str = self._format_uptime(snapshot.availability.uptime_seconds)
            
            text += f"{status_emoji} <b>{snapshot.plugin_id}</b>\n"
            text += f"├ Status: {snapshot.health_status.value}\n"
            text += f"├ Uptime: {uptime_str}\n"
            text += f"├ Exec Time: {snapshot.performance.p95_execution_time_ms:.0f}ms (P95)\n"
            text += f"├ Memory: {snapshot.resources.memory_usage_mb:.1f}MB\n"
            text += f"├ CPU: {snapshot.resources.cpu_usage_pct:.1f}%\n"
            text += f"└ Error Rate: {snapshot.errors.error_rate_pct:.2f}%\n\n"
        
        # Recent alerts
        recent_alerts = self.get_recent_alerts(limit=5)
        if recent_alerts:
            text += "⚠️ <b>Recent Alerts (last 5):</b>\n"
            for alert in recent_alerts:
                age = self._format_time_ago(alert.timestamp)
                resolved = "✓" if alert.resolved else ""
                text += f"• [{age}] {alert.message} {resolved}\n"
        
        return text
    
    def _format_uptime(self, seconds: int) -> str:
        """Format uptime in human-readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as time ago"""
        delta = datetime.now() - timestamp
        seconds = int(delta.total_seconds())
        
        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        else:
            return f"{seconds // 86400}d ago"
