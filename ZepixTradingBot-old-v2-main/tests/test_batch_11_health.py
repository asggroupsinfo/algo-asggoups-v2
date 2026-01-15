"""
Batch 11 Test Suite: Plugin Health Monitoring & Versioning System

Tests for:
1. PluginHealthMonitor - Health metrics collection, anomaly detection, auto-restart
2. VersionedPluginRegistry - Semantic versioning, compatibility checks, upgrade/rollback
3. ControllerBot - /health and /version commands
4. Integration tests - Full workflow testing

Test Categories:
- Health Metrics (availability, performance, resources, errors)
- Health Monitor (initialization, monitoring loop, alerts, zombie detection)
- Plugin Versioning (version creation, comparison, compatibility)
- Version Registry (registration, activation, upgrade, rollback)
- Telegram Commands (/health, /version, /upgrade, /rollback)
- Integration (full workflow)

Date: 2026-01-14
"""

import asyncio
import os
import sqlite3
import sys
import tempfile
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, AsyncMock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ============================================================
# Test: Health Metrics Data Classes
# ============================================================

class TestPluginAvailabilityMetrics:
    """Test PluginAvailabilityMetrics dataclass"""
    
    def test_create_availability_metrics(self):
        """Test creating availability metrics"""
        from monitoring.plugin_health_monitor import PluginAvailabilityMetrics
        
        metrics = PluginAvailabilityMetrics(
            plugin_id="test_plugin",
            is_running=True,
            is_responsive=True
        )
        
        assert metrics.plugin_id == "test_plugin"
        assert metrics.is_running is True
        assert metrics.is_responsive is True
    
    def test_health_status_healthy(self):
        """Test health status when plugin is healthy"""
        from monitoring.plugin_health_monitor import PluginAvailabilityMetrics, HealthStatus
        
        metrics = PluginAvailabilityMetrics(
            plugin_id="test_plugin",
            is_running=True,
            is_responsive=True,
            last_heartbeat=datetime.now()
        )
        
        assert metrics.health_status == HealthStatus.HEALTHY
    
    def test_health_status_dead(self):
        """Test health status when plugin is dead"""
        from monitoring.plugin_health_monitor import PluginAvailabilityMetrics, HealthStatus
        
        metrics = PluginAvailabilityMetrics(
            plugin_id="test_plugin",
            is_running=False,
            is_responsive=False
        )
        
        assert metrics.health_status == HealthStatus.DEAD
    
    def test_health_status_hung(self):
        """Test health status when plugin is hung"""
        from monitoring.plugin_health_monitor import PluginAvailabilityMetrics, HealthStatus
        
        metrics = PluginAvailabilityMetrics(
            plugin_id="test_plugin",
            is_running=True,
            is_responsive=False
        )
        
        assert metrics.health_status == HealthStatus.HUNG
    
    def test_health_status_stale(self):
        """Test health status when plugin is stale"""
        from monitoring.plugin_health_monitor import PluginAvailabilityMetrics, HealthStatus
        
        metrics = PluginAvailabilityMetrics(
            plugin_id="test_plugin",
            is_running=True,
            is_responsive=True,
            last_heartbeat=datetime.now() - timedelta(minutes=10)  # 10 minutes ago
        )
        
        assert metrics.health_status == HealthStatus.STALE


class TestPluginPerformanceMetrics:
    """Test PluginPerformanceMetrics dataclass"""
    
    def test_create_performance_metrics(self):
        """Test creating performance metrics"""
        from monitoring.plugin_health_monitor import PluginPerformanceMetrics
        
        metrics = PluginPerformanceMetrics(
            plugin_id="test_plugin",
            avg_execution_time_ms=100.0,
            p95_execution_time_ms=200.0
        )
        
        assert metrics.plugin_id == "test_plugin"
        assert metrics.avg_execution_time_ms == 100.0
        assert metrics.p95_execution_time_ms == 200.0
    
    def test_record_execution_time(self):
        """Test recording execution times"""
        from monitoring.plugin_health_monitor import PluginPerformanceMetrics
        
        metrics = PluginPerformanceMetrics(plugin_id="test_plugin")
        
        # Record some execution times
        for i in range(10):
            metrics.record_execution_time(float(i * 10))
        
        assert metrics.avg_execution_time_ms > 0
        assert len(metrics._execution_times) == 10


class TestPluginResourceMetrics:
    """Test PluginResourceMetrics dataclass"""
    
    def test_create_resource_metrics(self):
        """Test creating resource metrics"""
        from monitoring.plugin_health_monitor import PluginResourceMetrics
        
        metrics = PluginResourceMetrics(
            plugin_id="test_plugin",
            memory_usage_mb=256.0,
            cpu_usage_pct=25.0
        )
        
        assert metrics.plugin_id == "test_plugin"
        assert metrics.memory_usage_mb == 256.0
        assert metrics.cpu_usage_pct == 25.0


class TestPluginErrorMetrics:
    """Test PluginErrorMetrics dataclass"""
    
    def test_create_error_metrics(self):
        """Test creating error metrics"""
        from monitoring.plugin_health_monitor import PluginErrorMetrics
        
        metrics = PluginErrorMetrics(
            plugin_id="test_plugin",
            total_errors=5,
            critical_errors=1
        )
        
        assert metrics.plugin_id == "test_plugin"
        assert metrics.total_errors == 5
        assert metrics.critical_errors == 1
    
    def test_record_error(self):
        """Test recording errors"""
        from monitoring.plugin_health_monitor import PluginErrorMetrics
        
        metrics = PluginErrorMetrics(plugin_id="test_plugin")
        
        metrics.record_error("Test error", is_critical=False)
        assert metrics.total_errors == 1
        assert metrics.critical_errors == 0
        assert metrics.last_error_message == "Test error"
        
        metrics.record_error("Critical error", is_critical=True)
        assert metrics.total_errors == 2
        assert metrics.critical_errors == 1


class TestHealthSnapshot:
    """Test HealthSnapshot dataclass"""
    
    def test_create_health_snapshot(self):
        """Test creating health snapshot"""
        from monitoring.plugin_health_monitor import (
            HealthSnapshot, PluginAvailabilityMetrics, PluginPerformanceMetrics,
            PluginResourceMetrics, PluginErrorMetrics, HealthStatus
        )
        
        availability = PluginAvailabilityMetrics(
            plugin_id="test_plugin",
            is_running=True,
            is_responsive=True,
            last_heartbeat=datetime.now()
        )
        performance = PluginPerformanceMetrics(plugin_id="test_plugin")
        resources = PluginResourceMetrics(plugin_id="test_plugin")
        errors = PluginErrorMetrics(plugin_id="test_plugin")
        
        snapshot = HealthSnapshot(
            plugin_id="test_plugin",
            timestamp=datetime.now(),
            availability=availability,
            performance=performance,
            resources=resources,
            errors=errors
        )
        
        assert snapshot.plugin_id == "test_plugin"
        assert snapshot.health_status == HealthStatus.HEALTHY
        assert snapshot.is_healthy is True


class TestHealthAlert:
    """Test HealthAlert dataclass"""
    
    def test_create_health_alert(self):
        """Test creating health alert"""
        from monitoring.plugin_health_monitor import HealthAlert, AlertLevel
        
        alert = HealthAlert(
            id=1,
            plugin_id="test_plugin",
            alert_level=AlertLevel.CRITICAL,
            message="Test alert"
        )
        
        assert alert.id == 1
        assert alert.plugin_id == "test_plugin"
        assert alert.alert_level == AlertLevel.CRITICAL
        assert alert.resolved is False


# ============================================================
# Test: Plugin Health Monitor
# ============================================================

class TestPluginHealthMonitor:
    """Test PluginHealthMonitor class"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def mock_plugin_registry(self):
        """Create mock plugin registry"""
        registry = Mock()
        
        # Create mock plugins
        mock_plugin = Mock()
        mock_plugin.enabled = True
        mock_plugin.get_status = Mock(return_value={"plugin_id": "test_plugin", "enabled": True})
        
        registry.get_all_plugins = Mock(return_value={"test_plugin": mock_plugin})
        registry.plugins = {"test_plugin": mock_plugin}
        
        return registry
    
    def test_monitor_initialization(self, temp_db):
        """Test health monitor initialization"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor(db_path=temp_db)
        
        assert monitor.db_path == temp_db
        assert monitor._running is False
        assert len(monitor._health_snapshots) == 0
    
    def test_monitor_database_init(self, temp_db):
        """Test database initialization"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor(db_path=temp_db)
        
        # Check tables exist
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert "plugin_health_snapshots" in tables
        assert "health_alerts" in tables
        
        conn.close()
    
    def test_monitor_thresholds(self, temp_db):
        """Test health monitor thresholds"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        
        config = {
            'max_execution_time_ms': 10000,
            'max_error_rate_pct': 10.0
        }
        
        monitor = PluginHealthMonitor(db_path=temp_db, config=config)
        
        assert monitor.thresholds['max_execution_time_ms'] == 10000
        assert monitor.thresholds['max_error_rate_pct'] == 10.0
    
    def test_get_latest_snapshots_empty(self, temp_db):
        """Test getting latest snapshots when empty"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor(db_path=temp_db)
        
        snapshots = monitor.get_latest_snapshots()
        assert len(snapshots) == 0
    
    def test_get_recent_alerts_empty(self, temp_db):
        """Test getting recent alerts when empty"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor(db_path=temp_db)
        
        alerts = monitor.get_recent_alerts()
        assert len(alerts) == 0
    
    def test_get_health_summary(self, temp_db):
        """Test getting health summary"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor(db_path=temp_db)
        
        summary = monitor.get_health_summary()
        
        assert "total_plugins" in summary
        assert "healthy" in summary
        assert "unhealthy" in summary
        assert summary["total_plugins"] == 0
    
    def test_format_health_dashboard_empty(self, temp_db):
        """Test formatting health dashboard when empty"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor(db_path=temp_db)
        
        dashboard = monitor.format_health_dashboard()
        
        assert "Plugin Health Dashboard" in dashboard
        assert "No plugins registered" in dashboard
    
    def test_register_alert_callback(self, temp_db):
        """Test registering alert callback"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor(db_path=temp_db)
        
        callback = Mock()
        monitor.register_alert_callback(callback)
        
        assert callback in monitor._alert_callbacks
    
    def test_register_restart_callback(self, temp_db):
        """Test registering restart callback"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor(db_path=temp_db)
        
        callback = Mock()
        monitor.register_restart_callback(callback)
        
        assert callback in monitor._restart_callbacks


class TestHealthMonitorAsync:
    """Test async methods of PluginHealthMonitor"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, temp_db):
        """Test starting and stopping monitoring"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        
        monitor = PluginHealthMonitor(db_path=temp_db)
        
        # Start monitoring
        await monitor.start_monitoring()
        assert monitor._running is True
        
        # Stop monitoring
        await monitor.stop_monitoring()
        assert monitor._running is False
    
    @pytest.mark.asyncio
    async def test_trigger_alert(self, temp_db):
        """Test triggering alert"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor, AlertLevel
        
        monitor = PluginHealthMonitor(db_path=temp_db)
        
        await monitor._trigger_alert("test_plugin", AlertLevel.WARNING, "Test alert message")
        
        alerts = monitor.get_recent_alerts()
        assert len(alerts) == 1
        assert alerts[0].message == "Test alert message"


# ============================================================
# Test: Plugin Version
# ============================================================

class TestPluginVersion:
    """Test PluginVersion dataclass"""
    
    def test_create_plugin_version(self):
        """Test creating plugin version"""
        from core.versioned_plugin_registry import PluginVersion
        
        version = PluginVersion(
            plugin_id="v3_combined",
            major=3,
            minor=2,
            patch=1
        )
        
        assert version.plugin_id == "v3_combined"
        assert version.major == 3
        assert version.minor == 2
        assert version.patch == 1
    
    def test_version_string(self):
        """Test version string property"""
        from core.versioned_plugin_registry import PluginVersion
        
        version = PluginVersion(
            plugin_id="v3_combined",
            major=3,
            minor=2,
            patch=1
        )
        
        assert version.version_string == "3.2.1"
    
    def test_version_from_string(self):
        """Test creating version from string"""
        from core.versioned_plugin_registry import PluginVersion
        
        version = PluginVersion.from_string("v3_combined", "3.2.1")
        
        assert version.plugin_id == "v3_combined"
        assert version.major == 3
        assert version.minor == 2
        assert version.patch == 1
    
    def test_version_compatibility_same_major(self):
        """Test version compatibility with same major version"""
        from core.versioned_plugin_registry import PluginVersion
        
        v1 = PluginVersion(plugin_id="test", major=3, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test", major=3, minor=1, patch=0)
        
        assert v1.is_compatible_with(v2) is True
        assert v2.is_compatible_with(v1) is True
    
    def test_version_compatibility_different_major(self):
        """Test version compatibility with different major version"""
        from core.versioned_plugin_registry import PluginVersion
        
        v1 = PluginVersion(plugin_id="test", major=3, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test", major=4, minor=0, patch=0)
        
        assert v1.is_compatible_with(v2) is False
        assert v2.is_compatible_with(v1) is False
    
    def test_version_compatibility_different_plugins(self):
        """Test version compatibility between different plugins"""
        from core.versioned_plugin_registry import PluginVersion
        
        v1 = PluginVersion(plugin_id="plugin_a", major=3, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="plugin_b", major=6, minor=0, patch=0)
        
        # Different plugins don't conflict
        assert v1.is_compatible_with(v2) is True
    
    def test_version_comparison(self):
        """Test version comparison"""
        from core.versioned_plugin_registry import PluginVersion
        
        v1 = PluginVersion(plugin_id="test", major=3, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test", major=3, minor=1, patch=0)
        v3 = PluginVersion(plugin_id="test", major=3, minor=1, patch=1)
        
        assert v1 < v2
        assert v2 < v3
        assert not v3 < v1
    
    def test_version_is_newer_than(self):
        """Test is_newer_than method"""
        from core.versioned_plugin_registry import PluginVersion
        
        v1 = PluginVersion(plugin_id="test", major=3, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test", major=3, minor=1, patch=0)
        
        assert v2.is_newer_than(v1) is True
        assert v1.is_newer_than(v2) is False
    
    def test_version_to_dict(self):
        """Test converting version to dict"""
        from core.versioned_plugin_registry import PluginVersion
        
        version = PluginVersion(
            plugin_id="test",
            major=3,
            minor=2,
            patch=1,
            features=["feature1", "feature2"]
        )
        
        d = version.to_dict()
        
        assert d["plugin_id"] == "test"
        assert d["version_string"] == "3.2.1"
        assert "feature1" in d["features"]


# ============================================================
# Test: Versioned Plugin Registry
# ============================================================

class TestVersionedPluginRegistry:
    """Test VersionedPluginRegistry class"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_registry_initialization(self, temp_db):
        """Test registry initialization"""
        from core.versioned_plugin_registry import VersionedPluginRegistry
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        assert registry.db_path == temp_db
        assert len(registry.active_plugins) == 0
    
    def test_registry_database_init(self, temp_db):
        """Test database initialization"""
        from core.versioned_plugin_registry import VersionedPluginRegistry
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        # Check tables exist
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert "plugin_versions" in tables
        assert "plugin_version_history" in tables
        
        conn.close()
    
    def test_register_version(self, temp_db):
        """Test registering a version"""
        from core.versioned_plugin_registry import VersionedPluginRegistry, PluginVersion
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        version = PluginVersion(
            plugin_id="test_plugin",
            major=1,
            minor=0,
            patch=0
        )
        
        success = registry.register_version(version)
        
        assert success is True
        assert "test_plugin" in registry.available_versions
    
    def test_activate_plugin(self, temp_db):
        """Test activating a plugin version"""
        from core.versioned_plugin_registry import VersionedPluginRegistry, PluginVersion
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        version = PluginVersion(
            plugin_id="test_plugin",
            major=1,
            minor=0,
            patch=0
        )
        
        registry.register_version(version)
        success, message = registry.activate_plugin("test_plugin", version)
        
        assert success is True
        assert "test_plugin" in registry.active_plugins
    
    def test_get_active_version(self, temp_db):
        """Test getting active version"""
        from core.versioned_plugin_registry import VersionedPluginRegistry, PluginVersion
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        version = PluginVersion(
            plugin_id="test_plugin",
            major=1,
            minor=0,
            patch=0
        )
        
        registry.register_version(version)
        registry.activate_plugin("test_plugin", version)
        
        active = registry.get_active_version("test_plugin")
        
        assert active is not None
        assert active.version_string == "1.0.0"
    
    def test_list_available_versions(self, temp_db):
        """Test listing available versions"""
        from core.versioned_plugin_registry import VersionedPluginRegistry, PluginVersion
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        v1 = PluginVersion(plugin_id="test_plugin", major=1, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test_plugin", major=1, minor=1, patch=0)
        
        registry.register_version(v1)
        registry.register_version(v2)
        
        versions = registry.list_available_versions("test_plugin")
        
        assert len(versions) == 2
    
    def test_get_latest_version(self, temp_db):
        """Test getting latest version"""
        from core.versioned_plugin_registry import VersionedPluginRegistry, PluginVersion
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        v1 = PluginVersion(plugin_id="test_plugin", major=1, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test_plugin", major=1, minor=1, patch=0)
        
        registry.register_version(v1)
        registry.register_version(v2)
        
        latest = registry.get_latest_version("test_plugin")
        
        assert latest is not None
        assert latest.version_string == "1.1.0"
    
    def test_format_version_dashboard_empty(self, temp_db):
        """Test formatting version dashboard when empty"""
        from core.versioned_plugin_registry import VersionedPluginRegistry
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        dashboard = registry.format_version_dashboard()
        
        assert "Active Plugin Versions" in dashboard
        assert "No plugins registered" in dashboard
    
    def test_get_version_summary(self, temp_db):
        """Test getting version summary"""
        from core.versioned_plugin_registry import VersionedPluginRegistry
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        summary = registry.get_version_summary()
        
        assert "active_plugins" in summary
        assert "available_versions" in summary
        assert "system" in summary


class TestVersionUpgradeRollback:
    """Test upgrade and rollback functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_upgrade_plugin(self, temp_db):
        """Test upgrading plugin"""
        from core.versioned_plugin_registry import VersionedPluginRegistry, PluginVersion
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        v1 = PluginVersion(plugin_id="test_plugin", major=1, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test_plugin", major=1, minor=1, patch=0)
        
        registry.register_version(v1)
        registry.register_version(v2)
        registry.activate_plugin("test_plugin", v1)
        
        success, message = registry.upgrade_plugin("test_plugin", "1.1.0")
        
        assert success is True
        assert registry.get_active_version("test_plugin").version_string == "1.1.0"
    
    def test_upgrade_plugin_incompatible(self, temp_db):
        """Test upgrading to incompatible version"""
        from core.versioned_plugin_registry import VersionedPluginRegistry, PluginVersion
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        v1 = PluginVersion(plugin_id="test_plugin", major=1, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test_plugin", major=2, minor=0, patch=0)
        
        registry.register_version(v1)
        registry.register_version(v2)
        registry.activate_plugin("test_plugin", v1)
        
        success, message = registry.upgrade_plugin("test_plugin", "2.0.0")
        
        assert success is False
        assert "incompatible" in message.lower()
    
    def test_rollback_plugin(self, temp_db):
        """Test rolling back plugin"""
        from core.versioned_plugin_registry import VersionedPluginRegistry, PluginVersion
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        v1 = PluginVersion(plugin_id="test_plugin", major=1, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test_plugin", major=1, minor=1, patch=0)
        
        registry.register_version(v1)
        registry.register_version(v2)
        registry.activate_plugin("test_plugin", v2)
        
        success, message = registry.rollback_plugin("test_plugin")
        
        assert success is True
        assert registry.get_active_version("test_plugin").version_string == "1.0.0"
    
    def test_rollback_no_previous_version(self, temp_db):
        """Test rollback when no previous version exists"""
        from core.versioned_plugin_registry import VersionedPluginRegistry, PluginVersion
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        v1 = PluginVersion(plugin_id="test_plugin", major=1, minor=0, patch=0)
        
        registry.register_version(v1)
        registry.activate_plugin("test_plugin", v1)
        
        success, message = registry.rollback_plugin("test_plugin")
        
        assert success is False
        assert "no rollback version" in message.lower()


class TestVersionDeprecation:
    """Test version deprecation functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_deprecate_version(self, temp_db):
        """Test deprecating a version"""
        from core.versioned_plugin_registry import VersionedPluginRegistry, PluginVersion
        
        registry = VersionedPluginRegistry(db_path=temp_db)
        
        version = PluginVersion(plugin_id="test_plugin", major=1, minor=0, patch=0)
        registry.register_version(version)
        
        success = registry.deprecate_version("test_plugin", "1.0.0")
        
        assert success is True
        
        # Check version is deprecated
        versions = registry.list_available_versions("test_plugin")
        assert versions[0].deprecated is True


# ============================================================
# Test: Controller Bot Commands
# ============================================================

class TestControllerBotHealthCommands:
    """Test Controller Bot health and version commands"""
    
    @pytest.fixture
    def mock_controller_bot(self):
        """Create mock controller bot"""
        from telegram.controller_bot import ControllerBot
        
        bot = ControllerBot(token="test_token", chat_id="test_chat")
        bot.send_message = Mock(return_value=123)
        
        return bot
    
    def test_health_command_no_monitor(self, mock_controller_bot):
        """Test /health command when monitor not configured"""
        result = mock_controller_bot.handle_health_command()
        
        assert result is not None
        mock_controller_bot.send_message.assert_called_once()
        call_args = mock_controller_bot.send_message.call_args[0][0]
        assert "not configured" in call_args
    
    def test_version_command_no_registry(self, mock_controller_bot):
        """Test /version command when registry not configured"""
        result = mock_controller_bot.handle_version_command()
        
        assert result is not None
        mock_controller_bot.send_message.assert_called_once()
        call_args = mock_controller_bot.send_message.call_args[0][0]
        assert "not configured" in call_args
    
    def test_health_command_with_monitor(self, mock_controller_bot):
        """Test /health command with monitor configured"""
        mock_monitor = Mock()
        mock_monitor.format_health_dashboard = Mock(return_value="Health Dashboard")
        
        mock_controller_bot._health_monitor = mock_monitor
        
        result = mock_controller_bot.handle_health_command()
        
        assert result is not None
        mock_monitor.format_health_dashboard.assert_called_once()
    
    def test_version_command_with_registry(self, mock_controller_bot):
        """Test /version command with registry configured"""
        mock_registry = Mock()
        mock_registry.format_version_dashboard = Mock(return_value="Version Dashboard")
        
        mock_controller_bot._version_registry = mock_registry
        
        result = mock_controller_bot.handle_version_command()
        
        assert result is not None
        mock_registry.format_version_dashboard.assert_called_once()
    
    def test_upgrade_command_no_args(self, mock_controller_bot):
        """Test /upgrade command without arguments"""
        mock_registry = Mock()
        mock_controller_bot._version_registry = mock_registry
        
        result = mock_controller_bot.handle_upgrade_command({}, args=None)
        
        assert result is not None
        call_args = mock_controller_bot.send_message.call_args[0][0]
        assert "Usage" in call_args
    
    def test_rollback_command_no_args(self, mock_controller_bot):
        """Test /rollback command without arguments"""
        mock_registry = Mock()
        mock_controller_bot._version_registry = mock_registry
        
        result = mock_controller_bot.handle_rollback_command({}, args=None)
        
        assert result is not None
        call_args = mock_controller_bot.send_message.call_args[0][0]
        assert "Usage" in call_args
    
    def test_get_health_summary_no_monitor(self, mock_controller_bot):
        """Test get_health_summary when monitor not configured"""
        summary = mock_controller_bot.get_health_summary()
        
        assert summary == {}
    
    def test_get_version_summary_no_registry(self, mock_controller_bot):
        """Test get_version_summary when registry not configured"""
        summary = mock_controller_bot.get_version_summary()
        
        assert summary == {}


class TestControllerBotDependencies:
    """Test Controller Bot dependency injection"""
    
    def test_set_dependencies(self):
        """Test setting dependencies"""
        from telegram.controller_bot import ControllerBot
        
        bot = ControllerBot(token="test_token", chat_id="test_chat")
        
        mock_health_monitor = Mock()
        mock_version_registry = Mock()
        
        bot.set_dependencies(
            health_monitor=mock_health_monitor,
            version_registry=mock_version_registry
        )
        
        assert bot._health_monitor == mock_health_monitor
        assert bot._version_registry == mock_version_registry


# ============================================================
# Test: Default Plugin Versions Factory
# ============================================================

class TestDefaultPluginVersions:
    """Test default plugin versions factory"""
    
    def test_create_default_versions(self):
        """Test creating default plugin versions"""
        from core.versioned_plugin_registry import create_default_plugin_versions
        
        versions = create_default_plugin_versions()
        
        assert len(versions) == 5  # 1 V3 + 4 V6 plugins
        
        # Check V3 plugin
        v3_versions = [v for v in versions if v.plugin_id == "v3_combined"]
        assert len(v3_versions) == 1
        assert v3_versions[0].major == 3
        
        # Check V6 plugins
        v6_versions = [v for v in versions if v.plugin_id.startswith("price_action_")]
        assert len(v6_versions) == 4
        for v in v6_versions:
            assert v.major == 6


# ============================================================
# Test: Integration
# ============================================================

class TestIntegration:
    """Integration tests for health monitoring and versioning"""
    
    @pytest.fixture
    def temp_health_db(self):
        """Create temporary health database"""
        fd, path = tempfile.mkstemp(suffix='_health.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def temp_version_db(self):
        """Create temporary version database"""
        fd, path = tempfile.mkstemp(suffix='_version.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_full_health_monitoring_workflow(self, temp_health_db):
        """Test full health monitoring workflow"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        from telegram.controller_bot import ControllerBot
        
        # Create health monitor
        monitor = PluginHealthMonitor(db_path=temp_health_db)
        
        # Create controller bot
        bot = ControllerBot(token="test_token", chat_id="test_chat")
        bot.send_message = Mock(return_value=123)
        
        # Set dependencies
        bot.set_dependencies(health_monitor=monitor)
        
        # Test health command
        result = bot.handle_health_command()
        
        assert result is not None
        bot.send_message.assert_called_once()
    
    def test_full_versioning_workflow(self, temp_version_db):
        """Test full versioning workflow"""
        from core.versioned_plugin_registry import VersionedPluginRegistry, PluginVersion
        from telegram.controller_bot import ControllerBot
        
        # Create version registry
        registry = VersionedPluginRegistry(db_path=temp_version_db)
        
        # Register versions
        v1 = PluginVersion(plugin_id="test_plugin", major=1, minor=0, patch=0)
        v2 = PluginVersion(plugin_id="test_plugin", major=1, minor=1, patch=0)
        
        registry.register_version(v1)
        registry.register_version(v2)
        registry.activate_plugin("test_plugin", v1)
        
        # Create controller bot
        bot = ControllerBot(token="test_token", chat_id="test_chat")
        bot.send_message = Mock(return_value=123)
        
        # Set dependencies
        bot.set_dependencies(version_registry=registry)
        
        # Test version command
        result = bot.handle_version_command()
        
        assert result is not None
        bot.send_message.assert_called_once()
        
        # Test upgrade
        bot.send_message.reset_mock()
        result = bot.handle_upgrade_command({}, args=["test_plugin", "1.1.0"])
        
        assert result is not None
        assert registry.get_active_version("test_plugin").version_string == "1.1.0"


class TestBackwardCompatibility:
    """Test backward compatibility with existing systems"""
    
    def test_health_monitor_no_plugin_registry(self):
        """Test health monitor works without plugin registry"""
        from monitoring.plugin_health_monitor import PluginHealthMonitor
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            monitor = PluginHealthMonitor(db_path=db_path)
            
            # Should work without plugin registry
            summary = monitor.get_health_summary()
            assert summary["total_plugins"] == 0
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_version_registry_standalone(self):
        """Test version registry works standalone"""
        from core.versioned_plugin_registry import VersionedPluginRegistry
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            registry = VersionedPluginRegistry(db_path=db_path)
            
            # Should work standalone
            summary = registry.get_version_summary()
            assert "active_plugins" in summary
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


# ============================================================
# Run Tests
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
