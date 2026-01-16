# CONFIG MANAGER

**File:** `src/core/config_manager.py`  
**Lines:** 622  
**Purpose:** Hot-reload configuration system for dynamic settings changes

---

## OVERVIEW

The Config Manager provides hot-reload capability for configuration changes without requiring bot restart. It monitors configuration files and applies changes in real-time.

### Key Features

1. **Hot-Reload:** Apply config changes without restart
2. **Validation:** Validate config before applying
3. **Rollback:** Automatic rollback on invalid config
4. **Notifications:** Telegram notifications on config changes
5. **Audit Trail:** Log all config changes

---

## CLASS STRUCTURE

### Definition (Lines 20-80)

```python
class ConfigManager:
    """
    Manages configuration with hot-reload capability.
    
    Features:
    - File-based configuration
    - Hot-reload without restart
    - Validation before apply
    - Automatic rollback on error
    - Change notifications
    """
    
    def __init__(self, config_path: str, callback=None):
        self.config_path = config_path
        self.callback = callback  # Called on config change
        self.logger = logging.getLogger(__name__)
        
        # Current configuration
        self.config: Dict[str, Any] = {}
        
        # Previous configuration (for rollback)
        self.previous_config: Dict[str, Any] = {}
        
        # Change history
        self.change_history: List[Dict] = []
        
        # File watcher
        self.watcher = None
        self.watching = False
        
        # Load initial config
        self._load_config()
```

---

## CONFIGURATION LOADING

### Load Config (Lines 82-140)

```python
def _load_config(self):
    """Load configuration from file"""
    try:
        with open(self.config_path, 'r') as f:
            new_config = json.load(f)
        
        # Validate config
        validation = self._validate_config(new_config)
        if not validation["valid"]:
            self.logger.error(f"Invalid config: {validation['errors']}")
            return False
        
        # Store previous for rollback
        self.previous_config = self.config.copy()
        
        # Apply new config
        self.config = new_config
        
        self.logger.info("Configuration loaded successfully")
        return True
        
    except FileNotFoundError:
        self.logger.error(f"Config file not found: {self.config_path}")
        return False
    except json.JSONDecodeError as e:
        self.logger.error(f"Invalid JSON in config: {e}")
        return False
    except Exception as e:
        self.logger.error(f"Config load error: {e}")
        return False

def reload_config(self) -> bool:
    """
    Reload configuration from file (hot-reload).
    
    Returns:
        bool: True if reload successful
    """
    self.logger.info("Reloading configuration...")
    
    success = self._load_config()
    
    if success:
        # Record change
        self._record_change("reload", {})
        
        # Notify callback
        if self.callback:
            self.callback(self.config)
        
        self.logger.info("Configuration reloaded successfully")
    else:
        # Rollback
        self.config = self.previous_config.copy()
        self.logger.warning("Config reload failed, rolled back")
    
    return success
```

---

## CONFIGURATION VALIDATION

### Validate Config (Lines 142-240)

```python
def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration structure and values.
    
    Validates:
    - Required keys present
    - Value types correct
    - Value ranges valid
    - Cross-field dependencies
    
    Args:
        config: Configuration to validate
        
    Returns:
        dict: {"valid": bool, "errors": list}
    """
    result = {"valid": True, "errors": []}
    
    # Required keys
    required_keys = [
        "mt5_login", "mt5_password", "mt5_server",
        "telegram_token", "telegram_chat_id",
        "symbol_config", "risk_tiers"
    ]
    
    for key in required_keys:
        if key not in config:
            result["valid"] = False
            result["errors"].append(f"Missing required key: {key}")
    
    # Validate symbol_config
    if "symbol_config" in config:
        for symbol, settings in config["symbol_config"].items():
            if "pip_size" not in settings:
                result["errors"].append(f"Missing pip_size for {symbol}")
            if "pip_value_per_std_lot" not in settings:
                result["errors"].append(f"Missing pip_value for {symbol}")
    
    # Validate risk_tiers
    if "risk_tiers" in config:
        for tier, settings in config["risk_tiers"].items():
            if "daily_loss_limit" not in settings:
                result["errors"].append(f"Missing daily_loss_limit for tier {tier}")
            if "max_total_loss" not in settings:
                result["errors"].append(f"Missing max_total_loss for tier {tier}")
    
    # Validate value ranges
    if config.get("rr_ratio", 0) <= 0:
        result["errors"].append("rr_ratio must be positive")
    
    if len(result["errors"]) > 0:
        result["valid"] = False
    
    return result
```

---

## HOT-RELOAD METHODS

### Update Setting (Lines 242-320)

```python
def update_setting(self, key: str, value: Any) -> bool:
    """
    Update a single setting with hot-reload.
    
    Args:
        key: Setting key (supports dot notation: "risk_tiers.tier1.daily_loss_limit")
        value: New value
        
    Returns:
        bool: True if update successful
    """
    try:
        # Parse key path
        keys = key.split(".")
        
        # Navigate to parent
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Store old value
        old_value = current.get(keys[-1])
        
        # Update value
        current[keys[-1]] = value
        
        # Validate new config
        validation = self._validate_config(self.config)
        if not validation["valid"]:
            # Rollback
            current[keys[-1]] = old_value
            self.logger.error(f"Setting update failed validation: {validation['errors']}")
            return False
        
        # Record change
        self._record_change("update", {
            "key": key,
            "old_value": old_value,
            "new_value": value
        })
        
        # Save to file
        self._save_config()
        
        # Notify callback
        if self.callback:
            self.callback(self.config)
        
        self.logger.info(f"Setting updated: {key} = {value}")
        return True
        
    except Exception as e:
        self.logger.error(f"Setting update error: {e}")
        return False
```

### Batch Update (Lines 322-380)

```python
def batch_update(self, updates: Dict[str, Any]) -> bool:
    """
    Update multiple settings atomically.
    
    Args:
        updates: Dict of key -> value updates
        
    Returns:
        bool: True if all updates successful
    """
    # Store backup
    backup = copy.deepcopy(self.config)
    
    try:
        # Apply all updates
        for key, value in updates.items():
            keys = key.split(".")
            current = self.config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        
        # Validate
        validation = self._validate_config(self.config)
        if not validation["valid"]:
            # Rollback all
            self.config = backup
            self.logger.error(f"Batch update failed: {validation['errors']}")
            return False
        
        # Record change
        self._record_change("batch_update", {"updates": updates})
        
        # Save
        self._save_config()
        
        # Notify
        if self.callback:
            self.callback(self.config)
        
        self.logger.info(f"Batch update successful: {len(updates)} settings")
        return True
        
    except Exception as e:
        self.config = backup
        self.logger.error(f"Batch update error: {e}")
        return False
```

---

## FILE WATCHING

### Start Watching (Lines 382-440)

```python
def start_watching(self):
    """Start watching config file for changes"""
    if self.watching:
        return
    
    self.watching = True
    self.watcher = threading.Thread(target=self._watch_file, daemon=True)
    self.watcher.start()
    
    self.logger.info("Config file watching started")

def stop_watching(self):
    """Stop watching config file"""
    self.watching = False
    self.logger.info("Config file watching stopped")

def _watch_file(self):
    """File watcher thread"""
    last_modified = os.path.getmtime(self.config_path)
    
    while self.watching:
        try:
            current_modified = os.path.getmtime(self.config_path)
            
            if current_modified > last_modified:
                self.logger.info("Config file changed, reloading...")
                self.reload_config()
                last_modified = current_modified
            
            time.sleep(1)  # Check every second
            
        except Exception as e:
            self.logger.error(f"File watch error: {e}")
            time.sleep(5)
```

---

## CHANGE HISTORY

### Record Change (Lines 442-480)

```python
def _record_change(self, change_type: str, details: Dict):
    """Record a configuration change"""
    record = {
        "timestamp": datetime.now().isoformat(),
        "type": change_type,
        "details": details
    }
    
    self.change_history.append(record)
    
    # Keep only last 100 changes
    if len(self.change_history) > 100:
        self.change_history = self.change_history[-100:]

def get_change_history(self, count: int = 10) -> List[Dict]:
    """Get recent change history"""
    return self.change_history[-count:]
```

---

## GETTER METHODS

### Get Config Values (Lines 482-550)

```python
def get(self, key: str, default: Any = None) -> Any:
    """
    Get a config value by key.
    
    Args:
        key: Setting key (supports dot notation)
        default: Default value if key not found
        
    Returns:
        Config value or default
    """
    try:
        keys = key.split(".")
        current = self.config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
        
    except Exception:
        return default

def get_section(self, section: str) -> Dict[str, Any]:
    """Get an entire config section"""
    return self.config.get(section, {})

def get_all(self) -> Dict[str, Any]:
    """Get entire configuration"""
    return self.config.copy()
```

---

## TELEGRAM INTEGRATION

### Config Commands (Lines 552-622)

```python
async def handle_config_command(self, update, context):
    """Handle /config command"""
    args = context.args
    
    if not args:
        # Show current config summary
        summary = self._get_config_summary()
        await update.message.reply_text(summary)
        return
    
    if args[0] == "reload":
        success = self.reload_config()
        if success:
            await update.message.reply_text("Configuration reloaded successfully")
        else:
            await update.message.reply_text("Configuration reload failed")
        return
    
    if args[0] == "set" and len(args) >= 3:
        key = args[1]
        value = self._parse_value(args[2])
        success = self.update_setting(key, value)
        if success:
            await update.message.reply_text(f"Setting updated: {key} = {value}")
        else:
            await update.message.reply_text(f"Failed to update setting: {key}")
        return
    
    if args[0] == "get" and len(args) >= 2:
        key = args[1]
        value = self.get(key)
        await update.message.reply_text(f"{key} = {value}")
        return

def _get_config_summary(self) -> str:
    """Generate config summary for display"""
    return f"""
Configuration Summary
=====================
MT5 Server: {self.get('mt5_server')}
Symbols: {len(self.get('symbol_config', {}))}
Risk Tiers: {len(self.get('risk_tiers', {}))}
RR Ratio: {self.get('rr_ratio', 2.0)}
Dual Orders: {self.get('dual_order_config.enabled', True)}
Shadow Mode: {self.get('shadow_mode.enabled', False)}
"""
```

---

## CONFIGURATION STRUCTURE

### Full Config Example

```python
{
    # MT5 Settings
    "mt5_login": 12345678,
    "mt5_password": "password",
    "mt5_server": "ICMarkets-Demo",
    
    # Telegram Settings
    "telegram_token": "BOT_TOKEN",
    "telegram_chat_id": "CHAT_ID",
    
    # Symbol Configuration
    "symbol_config": {
        "EURUSD": {
            "pip_size": 0.0001,
            "pip_value_per_std_lot": 10.0,
            "min_lot": 0.01,
            "max_lot": 10.0
        }
    },
    
    # Risk Tiers
    "risk_tiers": {
        "tier1": {
            "min_balance": 0,
            "max_balance": 1000,
            "daily_loss_limit": 50,
            "max_total_loss": 200
        }
    },
    
    # Trading Settings
    "rr_ratio": 2.0,
    "simulate_orders": false,
    
    # Dual Order Config
    "dual_order_config": {
        "enabled": true
    },
    
    # Shadow Mode
    "shadow_mode": {
        "enabled": false,
        "default_mode": "legacy_only"
    }
}
```

---

## RELATED FILES

- `src/core/trading_engine.py` - Uses ConfigManager
- `src/telegram/config_commands.py` - Telegram commands
- `config.json` - Main config file
