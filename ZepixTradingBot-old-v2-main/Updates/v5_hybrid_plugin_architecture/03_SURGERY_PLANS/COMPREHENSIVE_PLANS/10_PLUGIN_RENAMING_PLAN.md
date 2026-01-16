# PLAN 10: PLUGIN RENAMING & STRUCTURE

**Date:** 2026-01-15
**Priority:** P2 (Medium)
**Estimated Time:** 1-2 days
**Dependencies:** Plans 01-09

---

## 1. OBJECTIVE

Rename and restructure plugins to follow consistent naming conventions. Currently plugins have inconsistent names that don't reflect their purpose. After this plan:

1. **Consistent Naming** - All plugins follow `{strategy}_{timeframe}` pattern
2. **Clear Folder Structure** - Organized by strategy type
3. **Updated References** - All code references updated
4. **Documentation** - Plugin registry updated

**Current Problem (from Study Report 04, GAP-9):**
- `combined_v3` should be `v3_combined_5m` (or similar)
- V6 plugins have inconsistent naming
- Folder structure doesn't match naming
- Plugin registry has old names

**Target State:**
- V3: `v3_combined_5m`, `v3_combined_15m`, `v3_combined_1h`
- V6: `v6_price_action_1m`, `v6_price_action_5m`, `v6_price_action_15m`, `v6_price_action_1h`
- Clear folder structure
- All references updated

---

## 2. SCOPE

### In-Scope:
- Rename plugin folders
- Rename plugin classes
- Update plugin IDs
- Update all code references
- Update configuration files
- Update database references
- Update documentation

### Out-of-Scope:
- Changing plugin functionality
- Adding new plugins
- Removing plugins

---

## 3. CURRENT STATE ANALYSIS

### Current Plugin Structure:

```
src/logic_plugins/
├── combined_v3/           # Should be v3_combined/
│   ├── __init__.py
│   ├── config.json
│   ├── plugin.py
│   └── ...
├── price_action_1m/       # Should be v6_price_action_1m/
├── price_action_5m/       # Should be v6_price_action_5m/
├── price_action_15m/      # Should be v6_price_action_15m/
└── price_action_1h/       # Should be v6_price_action_1h/
```

### Current Plugin IDs:
- `combined_v3` → Should be `v3_combined`
- `price_action_1m` → Should be `v6_price_action_1m`
- `price_action_5m` → Should be `v6_price_action_5m`
- `price_action_15m` → Should be `v6_price_action_15m`
- `price_action_1h` → Should be `v6_price_action_1h`

---

## 4. GAPS ADDRESSED

| Gap | Description | How Addressed |
|-----|-------------|---------------|
| GAP-9 | Plugin Naming Convention | Rename all plugins |
| REQ-1.3 | Folder Structure | Reorganize folders |
| REQ-1.4 | Plugin Registry | Update registry |

---

## 5. IMPLEMENTATION STEPS

### Step 1: Define New Naming Convention

**Naming Pattern:** `{version}_{strategy}_{timeframe}`

**V3 Plugins:**
| Old Name | New Name | Description |
|----------|----------|-------------|
| `combined_v3` | `v3_combined` | V3 Combined Logic (multi-timeframe) |

**V6 Plugins:**
| Old Name | New Name | Description |
|----------|----------|-------------|
| `price_action_1m` | `v6_price_action_1m` | V6 1-minute scalping |
| `price_action_5m` | `v6_price_action_5m` | V6 5-minute scalping |
| `price_action_15m` | `v6_price_action_15m` | V6 15-minute intraday |
| `price_action_1h` | `v6_price_action_1h` | V6 1-hour swing |

---

### Step 2: Create Rename Script

**File:** `scripts/rename_plugins.py` (NEW)

**Code:**
```python
"""
Plugin Rename Script
Renames plugins to follow new naming convention
"""
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Rename mappings
PLUGIN_RENAMES = {
    'combined_v3': 'v3_combined',
    'price_action_1m': 'v6_price_action_1m',
    'price_action_5m': 'v6_price_action_5m',
    'price_action_15m': 'v6_price_action_15m',
    'price_action_1h': 'v6_price_action_1h',
}

# Files to update
FILES_TO_UPDATE = [
    'src/core/plugin_system/plugin_registry.py',
    'src/core/plugin_system/service_api.py',
    'src/core/trading_engine.py',
    'src/core/service_initializer.py',
    'src/core/services/database_service.py',
    'src/telegram/message_router.py',
    'config/plugins.json',
    'tests/**/*.py',
]

class PluginRenamer:
    """Renames plugins and updates all references"""
    
    def __init__(self, base_path: str = '.'):
        self.base_path = Path(base_path)
        self.plugins_path = self.base_path / 'src' / 'logic_plugins'
        self.changes_made: List[Tuple[str, str, str]] = []  # (file, old, new)
    
    def rename_all(self, dry_run: bool = True) -> Dict[str, any]:
        """Rename all plugins and update references"""
        results = {
            'folders_renamed': 0,
            'files_updated': 0,
            'references_updated': 0,
            'errors': []
        }
        
        # Step 1: Rename folders
        for old_name, new_name in PLUGIN_RENAMES.items():
            old_path = self.plugins_path / old_name
            new_path = self.plugins_path / new_name
            
            if old_path.exists():
                if dry_run:
                    print(f"[DRY RUN] Would rename: {old_path} -> {new_path}")
                else:
                    shutil.move(str(old_path), str(new_path))
                    print(f"Renamed: {old_path} -> {new_path}")
                results['folders_renamed'] += 1
        
        # Step 2: Update references in files
        for pattern in FILES_TO_UPDATE:
            files = list(self.base_path.glob(pattern))
            for file_path in files:
                if file_path.is_file():
                    updated = self._update_file_references(file_path, dry_run)
                    if updated:
                        results['files_updated'] += 1
                        results['references_updated'] += updated
        
        # Step 3: Update plugin class names
        for old_name, new_name in PLUGIN_RENAMES.items():
            plugin_file = self.plugins_path / new_name / 'plugin.py'
            if plugin_file.exists() or (dry_run and (self.plugins_path / old_name / 'plugin.py').exists()):
                self._update_plugin_class(plugin_file if plugin_file.exists() else self.plugins_path / old_name / 'plugin.py', old_name, new_name, dry_run)
        
        # Step 4: Update config.json files
        for old_name, new_name in PLUGIN_RENAMES.items():
            config_file = self.plugins_path / new_name / 'config.json'
            if config_file.exists() or (dry_run and (self.plugins_path / old_name / 'config.json').exists()):
                self._update_config_json(config_file if config_file.exists() else self.plugins_path / old_name / 'config.json', old_name, new_name, dry_run)
        
        return results
    
    def _update_file_references(self, file_path: Path, dry_run: bool) -> int:
        """Update plugin references in a file"""
        try:
            content = file_path.read_text()
            original_content = content
            
            for old_name, new_name in PLUGIN_RENAMES.items():
                # Update string references
                content = content.replace(f"'{old_name}'", f"'{new_name}'")
                content = content.replace(f'"{old_name}"', f'"{new_name}"')
                
                # Update import paths
                content = content.replace(
                    f'from src.logic_plugins.{old_name}',
                    f'from src.logic_plugins.{new_name}'
                )
                content = content.replace(
                    f'import src.logic_plugins.{old_name}',
                    f'import src.logic_plugins.{new_name}'
                )
            
            if content != original_content:
                if dry_run:
                    print(f"[DRY RUN] Would update: {file_path}")
                else:
                    file_path.write_text(content)
                    print(f"Updated: {file_path}")
                
                # Count changes
                changes = sum(
                    original_content.count(old) - content.count(old)
                    for old in PLUGIN_RENAMES.keys()
                )
                return abs(changes)
            
            return 0
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            return 0
    
    def _update_plugin_class(self, file_path: Path, old_name: str, new_name: str, dry_run: bool):
        """Update plugin class name"""
        try:
            content = file_path.read_text()
            
            # Convert names to class format
            old_class = self._to_class_name(old_name)
            new_class = self._to_class_name(new_name)
            
            new_content = content.replace(old_class, new_class)
            
            # Update plugin_id
            new_content = new_content.replace(
                f"plugin_id = '{old_name}'",
                f"plugin_id = '{new_name}'"
            )
            
            if new_content != content:
                if dry_run:
                    print(f"[DRY RUN] Would update class in: {file_path}")
                else:
                    file_path.write_text(new_content)
                    print(f"Updated class in: {file_path}")
        except Exception as e:
            print(f"Error updating class in {file_path}: {e}")
    
    def _update_config_json(self, file_path: Path, old_name: str, new_name: str, dry_run: bool):
        """Update config.json plugin_id"""
        try:
            import json
            content = file_path.read_text()
            config = json.loads(content)
            
            if config.get('plugin_id') == old_name:
                config['plugin_id'] = new_name
                
                if dry_run:
                    print(f"[DRY RUN] Would update config: {file_path}")
                else:
                    file_path.write_text(json.dumps(config, indent=2))
                    print(f"Updated config: {file_path}")
        except Exception as e:
            print(f"Error updating config {file_path}: {e}")
    
    def _to_class_name(self, plugin_id: str) -> str:
        """Convert plugin_id to class name"""
        # combined_v3 -> CombinedV3Plugin
        # v3_combined -> V3CombinedPlugin
        # v6_price_action_1m -> V6PriceAction1mPlugin
        parts = plugin_id.split('_')
        class_name = ''.join(p.capitalize() for p in parts) + 'Plugin'
        return class_name
    
    def verify_rename(self) -> Dict[str, bool]:
        """Verify all renames were successful"""
        results = {}
        
        for old_name, new_name in PLUGIN_RENAMES.items():
            old_path = self.plugins_path / old_name
            new_path = self.plugins_path / new_name
            
            results[new_name] = {
                'folder_exists': new_path.exists(),
                'old_folder_gone': not old_path.exists(),
                'plugin_file_exists': (new_path / 'plugin.py').exists() if new_path.exists() else False,
                'config_exists': (new_path / 'config.json').exists() if new_path.exists() else False
            }
        
        return results


if __name__ == '__main__':
    import sys
    
    dry_run = '--execute' not in sys.argv
    
    renamer = PluginRenamer()
    results = renamer.rename_all(dry_run=dry_run)
    
    print("\n=== Results ===")
    print(f"Folders renamed: {results['folders_renamed']}")
    print(f"Files updated: {results['files_updated']}")
    print(f"References updated: {results['references_updated']}")
    
    if dry_run:
        print("\nThis was a DRY RUN. Use --execute to apply changes.")
```

**Reason:** Automates the renaming process safely.

---

### Step 3: Update Plugin Registry

**File:** `src/core/plugin_system/plugin_registry.py`

**Changes:**
```python
# UPDATE plugin registry with new names

class PluginRegistry:
    """Registry of all available plugins"""
    
    # Plugin definitions with new names
    AVAILABLE_PLUGINS = {
        # V3 Plugins
        'v3_combined': {
            'class': 'V3CombinedPlugin',
            'module': 'src.logic_plugins.v3_combined.plugin',
            'description': 'V3 Combined Logic (multi-timeframe)',
            'strategy': 'V3_COMBINED',
            'timeframes': ['5m', '15m', '1h'],
            'enabled': True
        },
        
        # V6 Plugins
        'v6_price_action_1m': {
            'class': 'V6PriceAction1mPlugin',
            'module': 'src.logic_plugins.v6_price_action_1m.plugin',
            'description': 'V6 Price Action 1-minute scalping',
            'strategy': 'V6_PRICE_ACTION',
            'timeframe': '1m',
            'enabled': True
        },
        'v6_price_action_5m': {
            'class': 'V6PriceAction5mPlugin',
            'module': 'src.logic_plugins.v6_price_action_5m.plugin',
            'description': 'V6 Price Action 5-minute scalping',
            'strategy': 'V6_PRICE_ACTION',
            'timeframe': '5m',
            'enabled': True
        },
        'v6_price_action_15m': {
            'class': 'V6PriceAction15mPlugin',
            'module': 'src.logic_plugins.v6_price_action_15m.plugin',
            'description': 'V6 Price Action 15-minute intraday',
            'strategy': 'V6_PRICE_ACTION',
            'timeframe': '15m',
            'enabled': True
        },
        'v6_price_action_1h': {
            'class': 'V6PriceAction1hPlugin',
            'module': 'src.logic_plugins.v6_price_action_1h.plugin',
            'description': 'V6 Price Action 1-hour swing',
            'strategy': 'V6_PRICE_ACTION',
            'timeframe': '1h',
            'enabled': True
        }
    }
    
    # Backward compatibility mapping
    LEGACY_NAMES = {
        'combined_v3': 'v3_combined',
        'price_action_1m': 'v6_price_action_1m',
        'price_action_5m': 'v6_price_action_5m',
        'price_action_15m': 'v6_price_action_15m',
        'price_action_1h': 'v6_price_action_1h',
    }
    
    def get_plugin(self, plugin_id: str):
        """Get plugin by ID (supports legacy names)"""
        # Check for legacy name
        if plugin_id in self.LEGACY_NAMES:
            plugin_id = self.LEGACY_NAMES[plugin_id]
            logger.warning(f"Using legacy plugin name, please update to: {plugin_id}")
        
        return self.AVAILABLE_PLUGINS.get(plugin_id)
    
    def list_plugins(self, include_legacy: bool = False) -> List[str]:
        """List all plugin IDs"""
        plugins = list(self.AVAILABLE_PLUGINS.keys())
        if include_legacy:
            plugins.extend(self.LEGACY_NAMES.keys())
        return plugins
```

**Reason:** Updates registry with new names and backward compatibility.

---

### Step 4: Update Target Folder Structure

**Target Structure:**
```
src/logic_plugins/
├── v3_combined/
│   ├── __init__.py
│   ├── config.json
│   ├── plugin.py
│   ├── signal_handlers.py
│   └── order_manager.py
├── v6_price_action_1m/
│   ├── __init__.py
│   ├── config.json
│   └── plugin.py
├── v6_price_action_5m/
│   ├── __init__.py
│   ├── config.json
│   └── plugin.py
├── v6_price_action_15m/
│   ├── __init__.py
│   ├── config.json
│   └── plugin.py
└── v6_price_action_1h/
    ├── __init__.py
    ├── config.json
    └── plugin.py
```

---

### Step 5: Create Verification Tests

**File:** `tests/test_plugin_naming.py` (NEW)

**Code:**
```python
"""
Tests for Plugin Naming Convention
Verifies all plugins follow naming convention
"""
import pytest
import re
from pathlib import Path

class TestPluginNaming:
    """Test plugin naming convention"""
    
    VALID_PATTERN = r'^v[36]_[a-z_]+(_\d+[mh])?$'
    
    @pytest.fixture
    def plugins_path(self):
        return Path('src/logic_plugins')
    
    def test_all_plugins_follow_convention(self, plugins_path):
        """Test all plugin folders follow naming convention"""
        for folder in plugins_path.iterdir():
            if folder.is_dir() and not folder.name.startswith('_'):
                assert re.match(self.VALID_PATTERN, folder.name), \
                    f"Plugin {folder.name} doesn't follow naming convention"
    
    def test_no_legacy_names_in_folders(self, plugins_path):
        """Test no legacy names exist"""
        legacy_names = ['combined_v3', 'price_action_1m', 'price_action_5m', 
                       'price_action_15m', 'price_action_1h']
        
        for folder in plugins_path.iterdir():
            assert folder.name not in legacy_names, \
                f"Legacy plugin name still exists: {folder.name}"
    
    def test_plugin_id_matches_folder(self, plugins_path):
        """Test plugin_id in config matches folder name"""
        import json
        
        for folder in plugins_path.iterdir():
            if folder.is_dir() and not folder.name.startswith('_'):
                config_file = folder / 'config.json'
                if config_file.exists():
                    config = json.loads(config_file.read_text())
                    assert config.get('plugin_id') == folder.name, \
                        f"Plugin ID mismatch in {folder.name}"
    
    def test_v3_plugins_exist(self, plugins_path):
        """Test V3 plugins exist with correct names"""
        v3_plugins = ['v3_combined']
        
        for plugin in v3_plugins:
            assert (plugins_path / plugin).exists(), \
                f"V3 plugin missing: {plugin}"
    
    def test_v6_plugins_exist(self, plugins_path):
        """Test V6 plugins exist with correct names"""
        v6_plugins = ['v6_price_action_1m', 'v6_price_action_5m', 
                     'v6_price_action_15m', 'v6_price_action_1h']
        
        for plugin in v6_plugins:
            assert (plugins_path / plugin).exists(), \
                f"V6 plugin missing: {plugin}"
```

**Reason:** Verifies naming convention is followed.

---

## 6. DEPENDENCIES

### Prerequisites:
- Plans 01-09 (All functionality implemented)

### Blocks:
- Plan 11 (Shadow Mode) - Uses new names
- Plan 12 (E2E Testing) - Uses new names

---

## 7. FILES AFFECTED

| File | Action | Description |
|------|--------|-------------|
| `src/logic_plugins/combined_v3/` | RENAME | To `v3_combined/` |
| `src/logic_plugins/price_action_*/` | RENAME | To `v6_price_action_*/` |
| `src/core/plugin_system/plugin_registry.py` | MODIFY | Update names |
| `scripts/rename_plugins.py` | CREATE | Rename script |
| `tests/test_plugin_naming.py` | CREATE | Tests |
| All files with plugin references | MODIFY | Update references |

---

## 8. SUCCESS CRITERIA

1. ✅ All plugins renamed to new convention
2. ✅ No legacy names in codebase
3. ✅ Plugin registry updated
4. ✅ All references updated
5. ✅ Backward compatibility maintained
6. ✅ All tests pass

---

## 11. REFERENCES

- **Study Report 04:** GAP-9, REQ-1.3-1.4
- **Code Evidence:** `src/logic_plugins/` directory

---

**END OF PLAN 10**
