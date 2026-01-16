"""
Versioned Plugin Registry - Semantic Versioning & Compatibility System

Implements semantic versioning and compatibility checks for V3 and V6 plugins
to enable safe updates, rollbacks, and A/B testing without breaking the system.

Key Features:
1. Semantic Versioning: MAJOR.MINOR.PATCH (e.g., 3.2.1, 6.1.0)
2. Compatibility Matrix: Track which plugin versions work together
3. Safe Updates: Prevent incompatible plugin combinations
4. Rollback Support: Revert to previous stable versions
5. A/B Testing: Run old and new versions side-by-side

Version: 1.0.0
Date: 2026-01-14
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


@dataclass
class PluginVersion:
    """
    Represents a plugin version with semantic versioning.
    
    Version Format: MAJOR.MINOR.PATCH
    - MAJOR: Breaking changes, API incompatible
    - MINOR: New features, backward compatible
    - PATCH: Bug fixes, no API changes
    """
    plugin_id: str
    major: int
    minor: int
    patch: int
    
    build_date: datetime = field(default_factory=datetime.now)
    commit_hash: str = ""
    author: str = "Zepix Team"
    
    # Compatibility constraints
    requires_api_version: str = "1.0.0"
    requires_db_schema: str = "1.0.0"
    
    # Feature flags
    features: List[str] = field(default_factory=list)
    deprecated: bool = False
    
    # Release notes
    release_notes: str = ""
    
    @property
    def version_string(self) -> str:
        """Get version as string (e.g., '3.2.1')"""
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @classmethod
    def from_string(cls, plugin_id: str, version_string: str) -> 'PluginVersion':
        """Create PluginVersion from version string"""
        parts = version_string.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid version string: {version_string}")
        
        return cls(
            plugin_id=plugin_id,
            major=int(parts[0]),
            minor=int(parts[1]),
            patch=int(parts[2])
        )
    
    def is_compatible_with(self, other: 'PluginVersion') -> bool:
        """
        Check if this version is compatible with another.
        
        Rules:
        - Same MAJOR version = compatible
        - Different MAJOR = incompatible
        - Different plugins don't conflict
        """
        if self.plugin_id != other.plugin_id:
            return True  # Different plugins don't conflict
        
        return self.major == other.major
    
    def is_newer_than(self, other: 'PluginVersion') -> bool:
        """Check if this version is newer than another"""
        if self.plugin_id != other.plugin_id:
            return False
        
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)
    
    def __str__(self) -> str:
        return f"{self.plugin_id} v{self.version_string}"
    
    def __repr__(self) -> str:
        return f"PluginVersion({self.plugin_id}, {self.version_string})"
    
    def __lt__(self, other: 'PluginVersion') -> bool:
        """Enable version comparison"""
        if self.plugin_id != other.plugin_id:
            return self.plugin_id < other.plugin_id
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PluginVersion):
            return False
        return (
            self.plugin_id == other.plugin_id and
            self.major == other.major and
            self.minor == other.minor and
            self.patch == other.patch
        )
    
    def __hash__(self) -> int:
        return hash((self.plugin_id, self.major, self.minor, self.patch))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "plugin_id": self.plugin_id,
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "version_string": self.version_string,
            "build_date": self.build_date.isoformat(),
            "commit_hash": self.commit_hash,
            "author": self.author,
            "requires_api_version": self.requires_api_version,
            "requires_db_schema": self.requires_db_schema,
            "features": self.features,
            "deprecated": self.deprecated,
            "release_notes": self.release_notes
        }


@dataclass
class VersionHistoryEntry:
    """Record of version activation/deactivation"""
    id: int = 0
    plugin_id: str = ""
    version_string: str = ""
    activated_at: datetime = field(default_factory=datetime.now)
    deactivated_at: Optional[datetime] = None
    reason: str = ""  # 'upgrade', 'rollback', 'migration', 'initial'


class VersionedPluginRegistry:
    """
    Enhanced plugin registry with version management.
    
    Features:
    - Semantic versioning for all plugins
    - Compatibility checking between versions
    - Safe upgrade/rollback functionality
    - Version history tracking
    - Dependency resolution
    """
    
    # Current system versions
    CURRENT_API_VERSION = "2.0.0"  # ServiceAPI version from Batch 07
    CURRENT_DB_SCHEMA = "1.0.0"
    
    def __init__(self, db_path: str = "data/zepix_versions.db"):
        """
        Initialize versioned plugin registry.
        
        Args:
            db_path: Path to version database
        """
        self.db_path = db_path
        
        # Active plugins: plugin_id -> PluginVersion
        self.active_plugins: Dict[str, PluginVersion] = {}
        
        # Available versions: plugin_id -> List[PluginVersion]
        self.available_versions: Dict[str, List[PluginVersion]] = {}
        
        # Version history
        self.version_history: List[VersionHistoryEntry] = []
        
        # Initialize database
        self._init_database()
        
        # Load existing versions
        self._load_plugin_versions()
        
        logger.info("[VersionedPluginRegistry] Initialized")
    
    def _init_database(self):
        """Initialize version database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Plugin versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plugin_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    major INTEGER NOT NULL,
                    minor INTEGER NOT NULL,
                    patch INTEGER NOT NULL,
                    build_date DATETIME NOT NULL,
                    commit_hash TEXT NOT NULL,
                    author TEXT NOT NULL,
                    requires_api_version TEXT NOT NULL,
                    requires_db_schema TEXT NOT NULL,
                    features TEXT NOT NULL,
                    deprecated BOOLEAN DEFAULT FALSE,
                    release_notes TEXT,
                    UNIQUE(plugin_id, major, minor, patch)
                )
            """)
            
            # Plugin version history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plugin_version_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    version_string TEXT NOT NULL,
                    activated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    deactivated_at DATETIME,
                    reason TEXT
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_versions_plugin 
                ON plugin_versions (plugin_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_plugin 
                ON plugin_version_history (plugin_id, activated_at)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("[VersionedPluginRegistry] Database initialized")
            
        except Exception as e:
            logger.error(f"[VersionedPluginRegistry] Database init error: {e}")
    
    def _load_plugin_versions(self):
        """Load all available plugin versions from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT plugin_id, major, minor, patch, build_date, 
                       commit_hash, author, requires_api_version, 
                       requires_db_schema, features, deprecated, release_notes
                FROM plugin_versions
                ORDER BY plugin_id, major DESC, minor DESC, patch DESC
            """)
            
            for row in cursor.fetchall():
                plugin_id = row[0]
                
                try:
                    build_date = datetime.fromisoformat(row[4]) if row[4] else datetime.now()
                except (ValueError, TypeError):
                    build_date = datetime.now()
                
                try:
                    features = json.loads(row[9]) if row[9] else []
                except (json.JSONDecodeError, TypeError):
                    features = []
                
                version = PluginVersion(
                    plugin_id=plugin_id,
                    major=row[1],
                    minor=row[2],
                    patch=row[3],
                    build_date=build_date,
                    commit_hash=row[5] or "",
                    author=row[6] or "Zepix Team",
                    requires_api_version=row[7] or "1.0.0",
                    requires_db_schema=row[8] or "1.0.0",
                    features=features,
                    deprecated=bool(row[10]),
                    release_notes=row[11] or ""
                )
                
                if plugin_id not in self.available_versions:
                    self.available_versions[plugin_id] = []
                
                self.available_versions[plugin_id].append(version)
            
            conn.close()
            
            logger.info(f"[VersionedPluginRegistry] Loaded {sum(len(v) for v in self.available_versions.values())} versions for {len(self.available_versions)} plugins")
            
        except Exception as e:
            logger.error(f"[VersionedPluginRegistry] Failed to load versions: {e}")
    
    def register_version(self, version: PluginVersion) -> bool:
        """
        Register a new plugin version in the database.
        
        Args:
            version: PluginVersion to register
            
        Returns:
            True if registered successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO plugin_versions (
                    plugin_id, major, minor, patch, build_date,
                    commit_hash, author, requires_api_version,
                    requires_db_schema, features, deprecated, release_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version.plugin_id,
                version.major,
                version.minor,
                version.patch,
                version.build_date.isoformat(),
                version.commit_hash,
                version.author,
                version.requires_api_version,
                version.requires_db_schema,
                json.dumps(version.features),
                version.deprecated,
                version.release_notes
            ))
            
            conn.commit()
            conn.close()
            
            # Update in-memory cache
            if version.plugin_id not in self.available_versions:
                self.available_versions[version.plugin_id] = []
            
            # Remove existing version if present
            self.available_versions[version.plugin_id] = [
                v for v in self.available_versions[version.plugin_id]
                if not (v.major == version.major and v.minor == version.minor and v.patch == version.patch)
            ]
            
            self.available_versions[version.plugin_id].append(version)
            self.available_versions[version.plugin_id].sort(reverse=True)
            
            logger.info(f"[VersionedPluginRegistry] Registered version: {version}")
            return True
            
        except Exception as e:
            logger.error(f"[VersionedPluginRegistry] Failed to register version: {e}")
            return False
    
    def activate_plugin(
        self,
        plugin_id: str,
        version: PluginVersion,
        force: bool = False
    ) -> Tuple[bool, str]:
        """
        Activate a specific plugin version.
        
        Args:
            plugin_id: Plugin identifier
            version: PluginVersion to activate
            force: Force activation even if incompatible
            
        Returns:
            (success, message)
        """
        # Check compatibility with currently active plugins
        for active_id, active_version in self.active_plugins.items():
            if not version.is_compatible_with(active_version):
                msg = f"{version} is incompatible with active {active_version}"
                logger.error(f"[VersionedPluginRegistry] {msg}")
                if not force:
                    return False, msg
        
        # Check API and DB schema requirements
        if not self._meets_requirements(version):
            msg = (
                f"{version} requires API {version.requires_api_version} "
                f"and DB schema {version.requires_db_schema}"
            )
            logger.error(f"[VersionedPluginRegistry] {msg}")
            if not force:
                return False, msg
        
        # Deactivate previous version if exists
        if plugin_id in self.active_plugins:
            self._record_deactivation(plugin_id, "upgrade")
        
        # Activate new version
        self.active_plugins[plugin_id] = version
        
        # Record activation
        self._record_activation(plugin_id, version, "activation")
        
        logger.info(f"[VersionedPluginRegistry] Activated {version}")
        return True, f"Activated {version}"
    
    def upgrade_plugin(
        self,
        plugin_id: str,
        target_version: str
    ) -> Tuple[bool, str]:
        """
        Upgrade plugin to a specific version.
        
        Args:
            plugin_id: Plugin identifier
            target_version: Target version string (e.g., '3.2.0')
            
        Returns:
            (success, message)
        """
        current = self.active_plugins.get(plugin_id)
        
        if not current:
            return False, f"Plugin {plugin_id} not currently active"
        
        # Find target version
        target = self._find_version(plugin_id, target_version)
        
        if not target:
            return False, f"Version {target_version} not found for {plugin_id}"
        
        # Check if downgrade
        if target < current:
            logger.warning(
                f"[VersionedPluginRegistry] Downgrading {plugin_id} from "
                f"{current.version_string} to {target.version_string}"
            )
        
        # Check compatibility
        if not current.is_compatible_with(target):
            return False, (
                f"Version {target_version} is incompatible with "
                f"current version {current.version_string} (MAJOR version mismatch)"
            )
        
        # Perform upgrade
        success, msg = self.activate_plugin(plugin_id, target, force=False)
        
        if success:
            self._record_activation(plugin_id, target, "upgrade")
            return True, f"Upgraded {plugin_id} to {target.version_string}"
        else:
            return False, f"Upgrade failed for {plugin_id}: {msg}"
    
    def rollback_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        """
        Rollback plugin to previous stable version.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            (success, message)
        """
        current = self.active_plugins.get(plugin_id)
        
        if not current:
            return False, f"Plugin {plugin_id} not currently active"
        
        # Get previous stable version (same MAJOR, lower MINOR/PATCH, not deprecated)
        available = sorted(
            [v for v in self.available_versions.get(plugin_id, [])
             if v.major == current.major and v < current and not v.deprecated],
            reverse=True
        )
        
        if not available:
            return False, f"No rollback version found for {plugin_id}"
        
        previous = available[0]
        
        # Perform rollback
        success, msg = self.activate_plugin(plugin_id, previous, force=True)
        
        if success:
            self._record_activation(plugin_id, previous, "rollback")
            return True, f"Rolled back {plugin_id} to {previous.version_string}"
        else:
            return False, f"Rollback failed for {plugin_id}: {msg}"
    
    def deprecate_version(self, plugin_id: str, version_string: str) -> bool:
        """
        Mark a version as deprecated.
        
        Args:
            plugin_id: Plugin identifier
            version_string: Version to deprecate
            
        Returns:
            True if deprecated successfully
        """
        version = self._find_version(plugin_id, version_string)
        
        if not version:
            return False
        
        version.deprecated = True
        
        # Update in database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE plugin_versions 
                SET deprecated = TRUE
                WHERE plugin_id = ? AND major = ? AND minor = ? AND patch = ?
            """, (plugin_id, version.major, version.minor, version.patch))
            
            conn.commit()
            conn.close()
            
            logger.info(f"[VersionedPluginRegistry] Deprecated {version}")
            return True
            
        except Exception as e:
            logger.error(f"[VersionedPluginRegistry] Failed to deprecate version: {e}")
            return False
    
    def get_active_version(self, plugin_id: str) -> Optional[PluginVersion]:
        """Get currently active version of plugin"""
        return self.active_plugins.get(plugin_id)
    
    def list_available_versions(self, plugin_id: str) -> List[PluginVersion]:
        """List all available versions of plugin"""
        return sorted(
            self.available_versions.get(plugin_id, []),
            reverse=True
        )
    
    def get_latest_version(self, plugin_id: str, include_deprecated: bool = False) -> Optional[PluginVersion]:
        """Get latest available version of plugin"""
        versions = self.available_versions.get(plugin_id, [])
        
        if not include_deprecated:
            versions = [v for v in versions if not v.deprecated]
        
        if not versions:
            return None
        
        return max(versions)
    
    def check_compatibility(self, version1: PluginVersion, version2: PluginVersion) -> bool:
        """Check if two versions are compatible"""
        return version1.is_compatible_with(version2)
    
    def get_version_history(self, plugin_id: str, limit: int = 10) -> List[VersionHistoryEntry]:
        """Get version activation history for plugin"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, plugin_id, version_string, activated_at, deactivated_at, reason
                FROM plugin_version_history
                WHERE plugin_id = ?
                ORDER BY activated_at DESC
                LIMIT ?
            """, (plugin_id, limit))
            
            history = []
            for row in cursor.fetchall():
                try:
                    activated_at = datetime.fromisoformat(row[3]) if row[3] else datetime.now()
                except (ValueError, TypeError):
                    activated_at = datetime.now()
                
                try:
                    deactivated_at = datetime.fromisoformat(row[4]) if row[4] else None
                except (ValueError, TypeError):
                    deactivated_at = None
                
                history.append(VersionHistoryEntry(
                    id=row[0],
                    plugin_id=row[1],
                    version_string=row[2],
                    activated_at=activated_at,
                    deactivated_at=deactivated_at,
                    reason=row[5] or ""
                ))
            
            conn.close()
            return history
            
        except Exception as e:
            logger.error(f"[VersionedPluginRegistry] Failed to get history: {e}")
            return []
    
    def _find_version(self, plugin_id: str, version_string: str) -> Optional[PluginVersion]:
        """Find specific version by version string"""
        try:
            major, minor, patch = map(int, version_string.split('.'))
        except (ValueError, AttributeError):
            return None
        
        for version in self.available_versions.get(plugin_id, []):
            if version.major == major and version.minor == minor and version.patch == patch:
                return version
        
        return None
    
    def _meets_requirements(self, version: PluginVersion) -> bool:
        """Check if plugin version meets system requirements"""
        # Compare versions (simplified string comparison)
        return (
            self._compare_versions(self.CURRENT_API_VERSION, version.requires_api_version) >= 0 and
            self._compare_versions(self.CURRENT_DB_SCHEMA, version.requires_db_schema) >= 0
        )
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare two version strings.
        
        Returns:
            1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        try:
            parts1 = list(map(int, v1.split('.')))
            parts2 = list(map(int, v2.split('.')))
            
            # Pad with zeros
            while len(parts1) < 3:
                parts1.append(0)
            while len(parts2) < 3:
                parts2.append(0)
            
            if parts1 > parts2:
                return 1
            elif parts1 < parts2:
                return -1
            return 0
            
        except (ValueError, AttributeError):
            return 0
    
    def _record_activation(self, plugin_id: str, version: PluginVersion, reason: str):
        """Record version activation in history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO plugin_version_history (plugin_id, version_string, activated_at, reason)
                VALUES (?, ?, ?, ?)
            """, (plugin_id, version.version_string, datetime.now().isoformat(), reason))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"[VersionedPluginRegistry] Failed to record activation: {e}")
    
    def _record_deactivation(self, plugin_id: str, reason: str):
        """Record version deactivation in history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update the most recent activation record
            cursor.execute("""
                UPDATE plugin_version_history 
                SET deactivated_at = ?
                WHERE plugin_id = ? AND deactivated_at IS NULL
                ORDER BY activated_at DESC
                LIMIT 1
            """, (datetime.now().isoformat(), plugin_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"[VersionedPluginRegistry] Failed to record deactivation: {e}")
    
    def format_version_dashboard(self) -> str:
        """Format version dashboard for Telegram display"""
        if not self.active_plugins:
            return "📦 <b>Active Plugin Versions</b>\n\nNo plugins registered."
        
        text = "📦 <b>Active Plugin Versions</b>\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for plugin_id, version in sorted(self.active_plugins.items()):
            deprecated_tag = " ⚠️ DEPRECATED" if version.deprecated else ""
            
            text += f"📌 <b>{plugin_id}</b>{deprecated_tag}\n"
            text += f"├ Version: <code>{version.version_string}</code>\n"
            text += f"├ Released: {version.build_date.strftime('%Y-%m-%d')}\n"
            
            if version.features:
                text += f"├ Features: {', '.join(version.features[:3])}\n"
            
            if version.commit_hash:
                text += f"└ Commit: <code>{version.commit_hash[:8]}</code>\n\n"
            else:
                text += f"└ Author: {version.author}\n\n"
        
        # System versions
        text += "🔧 <b>System Versions</b>\n"
        text += f"├ API: {self.CURRENT_API_VERSION}\n"
        text += f"└ DB Schema: {self.CURRENT_DB_SCHEMA}\n"
        
        return text
    
    def get_version_summary(self) -> Dict[str, Any]:
        """Get version summary for all plugins"""
        return {
            "active_plugins": {
                plugin_id: version.to_dict()
                for plugin_id, version in self.active_plugins.items()
            },
            "available_versions": {
                plugin_id: [v.version_string for v in versions]
                for plugin_id, versions in self.available_versions.items()
            },
            "system": {
                "api_version": self.CURRENT_API_VERSION,
                "db_schema": self.CURRENT_DB_SCHEMA
            }
        }


# Factory function for creating default versions
def create_default_plugin_versions() -> List[PluginVersion]:
    """Create default plugin versions for V3 and V6 plugins"""
    versions = []
    
    # V3 Combined Logic Plugin
    versions.append(PluginVersion(
        plugin_id="combined_v3",
        major=3,
        minor=0,
        patch=0,
        build_date=datetime.now(),
        commit_hash="batch08",
        author="Zepix Team",
        requires_api_version="2.0.0",
        requires_db_schema="1.0.0",
        features=["hybrid_sl", "dual_orders", "mtf_4pillar", "12_signal_types"],
        deprecated=False,
        release_notes="Initial V3 Combined Logic Plugin implementation"
    ))
    
    # V6 Price Action Plugins
    for tf, tf_name in [("1m", "1M Scalping"), ("5m", "5M Momentum"), ("15m", "15M Intraday"), ("1h", "1H Swing")]:
        versions.append(PluginVersion(
            plugin_id=f"price_action_{tf}",
            major=6,
            minor=0,
            patch=0,
            build_date=datetime.now(),
            commit_hash="batch10",
            author="Zepix Team",
            requires_api_version="2.0.0",
            requires_db_schema="1.0.0",
            features=["trend_pulse", "conditional_orders", "adx_filter", "shadow_mode"],
            deprecated=False,
            release_notes=f"Initial V6 {tf_name} Plugin implementation"
        ))
    
    return versions
