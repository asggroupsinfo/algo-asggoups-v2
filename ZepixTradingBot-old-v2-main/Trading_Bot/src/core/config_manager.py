"""
Config Manager - Dynamic Configuration Hot-Reload System

Part of V5 Hybrid Plugin Architecture - Batch 09
Enables runtime config changes without bot restart.

Features:
- File watching for config changes (watchdog or polling fallback)
- JSON schema validation before applying changes
- Observer pattern for notifying plugins of config changes
- Thread-safe config access
- Atomic config updates

Version: 1.0.0
"""

import json
import os
import time
import threading
import logging
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfigChangeType(Enum):
    """Type of configuration change"""
    ADDED = "added"
    MODIFIED = "modified"
    REMOVED = "removed"


@dataclass
class ConfigChange:
    """Represents a single config change"""
    key: str
    change_type: ConfigChangeType
    old_value: Any
    new_value: Any
    timestamp: datetime


class ConfigValidationError(Exception):
    """Raised when config validation fails"""
    pass


class ConfigManager:
    """
    Manages dynamic configuration loading and hot-reload.
    
    Features:
    - Watch config files for changes
    - Validate JSON schema before applying
    - Notify observers of changes
    - Thread-safe access
    """
    
    def __init__(self, config_path: str = "config/config.json",
                 plugin_config_dir: str = "config/plugins",
                 watch_interval: float = 2.0, enable_watching: bool = True):
        self.config_path = config_path
        self.plugin_config_dir = plugin_config_dir
        self.watch_interval = watch_interval
        self.enable_watching = enable_watching
        
        self.config: Dict[str, Any] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        
        self._observers: List[Callable[[List[ConfigChange]], None]] = []
        self._plugin_observers: Dict[str, List[Callable[[List[ConfigChange]], None]]] = {}
        
        self._lock = threading.RLock()
        self._running = False
        self._watch_thread: Optional[threading.Thread] = None
        
        self._last_modified: Dict[str, float] = {}
        self._change_history: List[ConfigChange] = []
        self._max_history = 100
        
        self._required_keys = [
            "telegram_token",
            "telegram_chat_id",
            "mt5_login",
            "mt5_password",
            "mt5_server"
        ]
        
        # Previous config for rollback support
        self.previous_config: Dict[str, Any] = {}
        
        self.load_config()
        self.load_all_plugin_configs()
        
        if enable_watching:
            self.start_watching()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load main configuration from JSON file.
        
        Returns:
            Dict containing configuration
        """
        with self._lock:
            try:
                if os.path.exists(self.config_path):
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        self.config = json.load(f)
                    
                    self._last_modified[self.config_path] = os.path.getmtime(self.config_path)
                    logger.info(f"Config loaded from {self.config_path}")
                else:
                    logger.warning(f"Config file not found: {self.config_path}")
                    self.config = {}
                
                return self.config.copy()
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in config file: {e}")
                raise ConfigValidationError(f"Invalid JSON: {e}")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                raise
    
    def load_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        """
        Load configuration for a specific plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Dict containing plugin configuration
        """
        with self._lock:
            config_file = os.path.join(self.plugin_config_dir, f"{plugin_id}_config.json")
            
            try:
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    self.plugin_configs[plugin_id] = config
                    self._last_modified[config_file] = os.path.getmtime(config_file)
                    logger.info(f"Plugin config loaded: {plugin_id}")
                    return config.copy()
                else:
                    logger.warning(f"Plugin config not found: {config_file}")
                    return {}
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in plugin config {plugin_id}: {e}")
                raise ConfigValidationError(f"Invalid JSON in {plugin_id} config: {e}")
            except Exception as e:
                logger.error(f"Error loading plugin config {plugin_id}: {e}")
                raise
    
    def load_all_plugin_configs(self):
        """Load all plugin configurations from plugin config directory."""
        if not os.path.exists(self.plugin_config_dir):
            logger.warning(f"Plugin config directory not found: {self.plugin_config_dir}")
            return
        
        for filename in os.listdir(self.plugin_config_dir):
            if filename.endswith('_config.json'):
                plugin_id = filename.replace('_config.json', '')
                try:
                    self.load_plugin_config(plugin_id)
                except Exception as e:
                    logger.error(f"Failed to load plugin config {plugin_id}: {e}")
    
    def reload_config(self) -> List[ConfigChange]:
        """
        Reload config and detect changes.
        
        Returns:
            List of ConfigChange objects describing what changed
        """
        with self._lock:
            old_config = self.config.copy()
            
            try:
                self.load_config()
                
                changes = self._diff_config(old_config, self.config, "")
                
                if changes:
                    logger.info(f"Config changes detected: {len(changes)} changes")
                    self._add_to_history(changes)
                    self._notify_observers(changes)
                
                return changes
                
            except Exception as e:
                logger.error(f"Error reloading config: {e}")
                self.config = old_config
                raise
    
    def reload_plugin_config(self, plugin_id: str) -> List[ConfigChange]:
        """
        Reload specific plugin config and detect changes.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            List of ConfigChange objects
        """
        with self._lock:
            old_config = self.plugin_configs.get(plugin_id, {}).copy()
            
            try:
                self.load_plugin_config(plugin_id)
                new_config = self.plugin_configs.get(plugin_id, {})
                
                changes = self._diff_config(old_config, new_config, f"plugins.{plugin_id}")
                
                if changes:
                    logger.info(f"Plugin {plugin_id} config changes: {len(changes)} changes")
                    self._add_to_history(changes)
                    self._notify_plugin_observers(plugin_id, changes)
                
                return changes
                
            except Exception as e:
                logger.error(f"Error reloading plugin config {plugin_id}: {e}")
                self.plugin_configs[plugin_id] = old_config
                raise
    
    def _diff_config(
        self,
        old: Dict[str, Any],
        new: Dict[str, Any],
        prefix: str = ""
    ) -> List[ConfigChange]:
        """
        Compare two configs and return list of changes.
        
        Args:
            old: Old configuration
            new: New configuration
            prefix: Key prefix for nested configs
            
        Returns:
            List of ConfigChange objects
        """
        changes = []
        now = datetime.now()
        
        all_keys = set(old.keys()) | set(new.keys())
        
        for key in all_keys:
            full_key = f"{prefix}.{key}" if prefix else key
            
            if key not in old:
                changes.append(ConfigChange(
                    key=full_key,
                    change_type=ConfigChangeType.ADDED,
                    old_value=None,
                    new_value=new[key],
                    timestamp=now
                ))
            elif key not in new:
                changes.append(ConfigChange(
                    key=full_key,
                    change_type=ConfigChangeType.REMOVED,
                    old_value=old[key],
                    new_value=None,
                    timestamp=now
                ))
            elif old[key] != new[key]:
                if isinstance(old[key], dict) and isinstance(new[key], dict):
                    changes.extend(self._diff_config(old[key], new[key], full_key))
                else:
                    changes.append(ConfigChange(
                        key=full_key,
                        change_type=ConfigChangeType.MODIFIED,
                        old_value=old[key],
                        new_value=new[key],
                        timestamp=now
                    ))
        
        return changes
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration against schema.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid
            
        Raises:
            ConfigValidationError if invalid
        """
        for key in self._required_keys:
            if key not in config:
                raise ConfigValidationError(f"Missing required key: {key}")
        
        if "risk_tiers" in config:
            for tier, settings in config["risk_tiers"].items():
                required = ["per_trade_cap", "daily_loss_limit", "max_total_loss"]
                for req in required:
                    if req not in settings:
                        raise ConfigValidationError(
                            f"Risk tier {tier} missing required key: {req}"
                        )
        
        return True
    
    def register_observer(self, callback: Callable[[List[ConfigChange]], None]):
        """
        Register callback for main config changes.
        
        Args:
            callback: Function to call when config changes
        """
        with self._lock:
            if callback not in self._observers:
                self._observers.append(callback)
                logger.debug(f"Registered config observer: {callback.__name__}")
    
    def unregister_observer(self, callback: Callable[[List[ConfigChange]], None]):
        """
        Unregister callback for config changes.
        
        Args:
            callback: Function to unregister
        """
        with self._lock:
            if callback in self._observers:
                self._observers.remove(callback)
                logger.debug(f"Unregistered config observer: {callback.__name__}")
    
    def register_plugin_observer(
        self,
        plugin_id: str,
        callback: Callable[[List[ConfigChange]], None]
    ):
        """
        Register callback for specific plugin config changes.
        
        Args:
            plugin_id: Plugin identifier
            callback: Function to call when plugin config changes
        """
        with self._lock:
            if plugin_id not in self._plugin_observers:
                self._plugin_observers[plugin_id] = []
            
            if callback not in self._plugin_observers[plugin_id]:
                self._plugin_observers[plugin_id].append(callback)
                logger.debug(f"Registered plugin observer for {plugin_id}")
    
    def unregister_plugin_observer(
        self,
        plugin_id: str,
        callback: Callable[[List[ConfigChange]], None]
    ):
        """
        Unregister callback for plugin config changes.
        
        Args:
            plugin_id: Plugin identifier
            callback: Function to unregister
        """
        with self._lock:
            if plugin_id in self._plugin_observers:
                if callback in self._plugin_observers[plugin_id]:
                    self._plugin_observers[plugin_id].remove(callback)
    
    def _notify_observers(self, changes: List[ConfigChange]):
        """Notify all main config observers of changes."""
        for callback in self._observers:
            try:
                callback(changes)
            except Exception as e:
                logger.error(f"Error in config observer {callback.__name__}: {e}")
    
    def _notify_plugin_observers(self, plugin_id: str, changes: List[ConfigChange]):
        """Notify plugin-specific observers of changes."""
        if plugin_id in self._plugin_observers:
            for callback in self._plugin_observers[plugin_id]:
                try:
                    callback(changes)
                except Exception as e:
                    logger.error(f"Error in plugin observer for {plugin_id}: {e}")
    
    def _add_to_history(self, changes: List[ConfigChange]):
        """Add changes to history (keep last N)."""
        self._change_history.extend(changes)
        if len(self._change_history) > self._max_history:
            self._change_history = self._change_history[-self._max_history:]
    
    def start_watching(self):
        """Start watching config files for changes."""
        if self._running:
            return
        
        self._running = True
        self._watch_thread = threading.Thread(
            target=self._watch_loop,
            daemon=True,
            name="ConfigWatcher"
        )
        self._watch_thread.start()
        logger.info(f"Config watcher started (interval: {self.watch_interval}s)")
    
    def stop_watching(self):
        """Stop watching config files."""
        self._running = False
        if self._watch_thread:
            self._watch_thread.join(timeout=5.0)
            self._watch_thread = None
        logger.info("Config watcher stopped")
    
    def _watch_loop(self):
        """Main watch loop - polls for file changes."""
        while self._running:
            try:
                if os.path.exists(self.config_path):
                    current_mtime = os.path.getmtime(self.config_path)
                    last_mtime = self._last_modified.get(self.config_path, 0)
                    
                    if current_mtime > last_mtime:
                        logger.info("Main config file changed, reloading...")
                        try:
                            self.reload_config()
                        except Exception as e:
                            logger.error(f"Failed to reload config: {e}")
                
                if os.path.exists(self.plugin_config_dir):
                    for filename in os.listdir(self.plugin_config_dir):
                        if filename.endswith('_config.json'):
                            config_file = os.path.join(self.plugin_config_dir, filename)
                            plugin_id = filename.replace('_config.json', '')
                            
                            current_mtime = os.path.getmtime(config_file)
                            last_mtime = self._last_modified.get(config_file, 0)
                            
                            if current_mtime > last_mtime:
                                logger.info(f"Plugin config changed: {plugin_id}")
                                try:
                                    self.reload_plugin_config(plugin_id)
                                except Exception as e:
                                    logger.error(f"Failed to reload plugin config {plugin_id}: {e}")
                
            except Exception as e:
                logger.error(f"Error in config watch loop: {e}")
            
            time.sleep(self.watch_interval)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get config value by key (supports dot notation).
        
        Args:
            key: Config key (e.g., "risk_tiers.5000.per_trade_cap")
            default: Default value if key not found
            
        Returns:
            Config value or default
        """
        with self._lock:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
    
    def get_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get configuration for a specific plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin configuration dict
        """
        with self._lock:
            return self.plugin_configs.get(plugin_id, {}).copy()
    
    def update(self, key: str, value: Any, save: bool = True) -> bool:
        """
        Update config value and optionally save to file.
        
        Args:
            key: Config key (supports dot notation)
            value: New value
            save: Whether to save to file
            
        Returns:
            True if successful
        """
        with self._lock:
            try:
                keys = key.split('.')
                config = self.config
                
                for k in keys[:-1]:
                    if k not in config:
                        config[k] = {}
                    config = config[k]
                
                old_value = config.get(keys[-1])
                config[keys[-1]] = value
                
                if save:
                    self._save_config()
                
                change = ConfigChange(
                    key=key,
                    change_type=ConfigChangeType.MODIFIED if old_value else ConfigChangeType.ADDED,
                    old_value=old_value,
                    new_value=value,
                    timestamp=datetime.now()
                )
                self._add_to_history([change])
                self._notify_observers([change])
                
                logger.info(f"Config updated: {key} = {value}")
                return True
                
            except Exception as e:
                logger.error(f"Error updating config: {e}")
                return False
    
    def _save_config(self):
        """Save config to file atomically."""
        temp_file = f"{self.config_path}.tmp"
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            if os.path.exists(self.config_path):
                os.replace(temp_file, self.config_path)
            else:
                os.rename(temp_file, self.config_path)
            
            self._last_modified[self.config_path] = os.path.getmtime(self.config_path)
            
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise
    
    def get_change_history(self, limit: int = 50) -> List[ConfigChange]:
        """
        Get recent config change history.
        
        Args:
            limit: Maximum number of changes to return
            
        Returns:
            List of ConfigChange objects
        """
        with self._lock:
            return self._change_history[-limit:]
    
    def batch_update(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """
        Update multiple config values at once.
        
        Args:
            updates: Dict of key-value pairs to update
            save: Whether to save to file
            
        Returns:
            True if all updates successful
        """
        with self._lock:
            try:
                # Store previous config for rollback
                self.previous_config = self.config.copy()
                
                changes = []
                for key, value in updates.items():
                    old_value = self.get(key)
                    
                    # Update the value
                    keys = key.split('.')
                    config = self.config
                    for k in keys[:-1]:
                        if k not in config:
                            config[k] = {}
                        config = config[k]
                    config[keys[-1]] = value
                    
                    # Record the change
                    change = ConfigChange(
                        key=key,
                        change_type=ConfigChangeType.MODIFIED if old_value else ConfigChangeType.ADDED,
                        old_value=old_value,
                        new_value=value,
                        timestamp=datetime.now()
                    )
                    changes.append(change)
                    self._record_change(change)
                
                if save:
                    self._save_config()
                
                self._notify_observers(changes)
                logger.info(f"Batch update: {len(updates)} values updated")
                return True
                
            except Exception as e:
                logger.error(f"Error in batch update: {e}")
                # Rollback
                self.config = self.previous_config.copy()
                return False
    
    def _record_change(self, change: ConfigChange):
        """
        Record a single config change to history.
        
        Args:
            change: ConfigChange object to record
        """
        self._change_history.append(change)
        if len(self._change_history) > self._max_history:
            self._change_history = self._change_history[-self._max_history:]
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get a config section by name.
        
        Args:
            section: Section name (e.g., 'risk_config', 'telegram')
            
        Returns:
            Dict containing section config or empty dict
        """
        with self._lock:
            return self.config.get(section, {}).copy()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get entire configuration.
        
        Returns:
            Complete config dict copy
        """
        with self._lock:
            return self.config.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get config manager status.
        
        Returns:
            Status dictionary
        """
        with self._lock:
            return {
                "watching": self._running,
                "watch_interval": self.watch_interval,
                "config_path": self.config_path,
                "plugin_config_dir": self.plugin_config_dir,
                "loaded_plugins": list(self.plugin_configs.keys()),
                "observer_count": len(self._observers),
                "plugin_observer_count": sum(
                    len(obs) for obs in self._plugin_observers.values()
                ),
                "change_history_count": len(self._change_history),
                "last_modified": {
                    path: datetime.fromtimestamp(mtime).isoformat()
                    for path, mtime in self._last_modified.items()
                }
            }


def create_config_manager(
    config_path: str = "config/config.json",
    plugin_config_dir: str = "config/plugins",
    enable_watching: bool = True
) -> ConfigManager:
    """
    Factory function to create ConfigManager instance.
    
    Args:
        config_path: Path to main config file
        plugin_config_dir: Directory containing plugin configs
        enable_watching: Whether to enable file watching
        
    Returns:
        ConfigManager instance
    """
    return ConfigManager(
        config_path=config_path,
        plugin_config_dir=plugin_config_dir,
        enable_watching=enable_watching
    )
