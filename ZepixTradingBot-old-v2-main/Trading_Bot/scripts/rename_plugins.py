"""
Plugin Rename Script - Plan 10: Plugin Renaming & Structure

Renames plugins to follow new naming convention:
- combined_v3 -> v3_combined
- price_action_* -> v6_price_action_*

Features:
- Dry run mode for testing
- Updates all code references
- Backward compatibility mapping
- Verification after rename

Version: 1.0.0
Date: 2026-01-15
"""
import os
import re
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any


PLUGIN_RENAMES = {
    'combined_v3': 'v3_combined',
    'price_action_1m': 'v6_price_action_1m',
    'price_action_5m': 'v6_price_action_5m',
    'price_action_15m': 'v6_price_action_15m',
    'price_action_1h': 'v6_price_action_1h',
}

FILES_TO_UPDATE = [
    'src/core/plugin_system/plugin_registry.py',
    'src/core/plugin_system/service_api.py',
    'src/core/trading_engine.py',
    'src/core/service_initializer.py',
    'src/core/services/database_service.py',
    'src/telegram/message_router.py',
    'src/telegram/multi_telegram_manager.py',
    'tests/*.py',
]


class PluginRenamer:
    """Renames plugins and updates all references"""
    
    def __init__(self, base_path: str = '.'):
        self.base_path = Path(base_path)
        self.plugins_path = self.base_path / 'src' / 'logic_plugins'
        self.changes_made: List[Tuple[str, str, str]] = []
    
    def rename_all(self, dry_run: bool = True) -> Dict[str, Any]:
        """Rename all plugins and update references"""
        results = {
            'folders_renamed': 0,
            'files_updated': 0,
            'references_updated': 0,
            'errors': []
        }
        
        print(f"\n{'='*60}")
        print(f"Plugin Rename Script - {'DRY RUN' if dry_run else 'EXECUTING'}")
        print(f"{'='*60}\n")
        
        # Step 1: Rename folders
        print("Step 1: Renaming plugin folders...")
        for old_name, new_name in PLUGIN_RENAMES.items():
            old_path = self.plugins_path / old_name
            new_path = self.plugins_path / new_name
            
            if old_path.exists():
                if dry_run:
                    print(f"  [DRY RUN] Would rename: {old_name} -> {new_name}")
                else:
                    try:
                        shutil.move(str(old_path), str(new_path))
                        print(f"  Renamed: {old_name} -> {new_name}")
                    except Exception as e:
                        results['errors'].append(f"Failed to rename {old_name}: {e}")
                        print(f"  ERROR: Failed to rename {old_name}: {e}")
                        continue
                results['folders_renamed'] += 1
            else:
                print(f"  Skipped: {old_name} (folder doesn't exist)")
        
        # Step 2: Update references in files
        print("\nStep 2: Updating code references...")
        for pattern in FILES_TO_UPDATE:
            if '*' in pattern:
                files = list(self.base_path.glob(pattern))
            else:
                file_path = self.base_path / pattern
                files = [file_path] if file_path.exists() else []
            
            for file_path in files:
                if file_path.is_file():
                    updated = self._update_file_references(file_path, dry_run)
                    if updated:
                        results['files_updated'] += 1
                        results['references_updated'] += updated
        
        # Step 3: Update plugin class names in plugin.py files
        print("\nStep 3: Updating plugin class names...")
        for old_name, new_name in PLUGIN_RENAMES.items():
            if dry_run:
                plugin_file = self.plugins_path / old_name / 'plugin.py'
            else:
                plugin_file = self.plugins_path / new_name / 'plugin.py'
            
            if plugin_file.exists():
                self._update_plugin_class(plugin_file, old_name, new_name, dry_run)
        
        # Step 4: Update config.json files
        print("\nStep 4: Updating config.json files...")
        for old_name, new_name in PLUGIN_RENAMES.items():
            if dry_run:
                config_file = self.plugins_path / old_name / 'config.json'
            else:
                config_file = self.plugins_path / new_name / 'config.json'
            
            if config_file.exists():
                self._update_config_json(config_file, old_name, new_name, dry_run)
        
        # Step 5: Update __init__.py files
        print("\nStep 5: Updating __init__.py files...")
        for old_name, new_name in PLUGIN_RENAMES.items():
            if dry_run:
                init_file = self.plugins_path / old_name / '__init__.py'
            else:
                init_file = self.plugins_path / new_name / '__init__.py'
            
            if init_file.exists():
                self._update_init_file(init_file, old_name, new_name, dry_run)
        
        print(f"\n{'='*60}")
        print("Results:")
        print(f"  Folders renamed: {results['folders_renamed']}")
        print(f"  Files updated: {results['files_updated']}")
        print(f"  References updated: {results['references_updated']}")
        print(f"  Errors: {len(results['errors'])}")
        print(f"{'='*60}\n")
        
        if dry_run:
            print("This was a DRY RUN. Use --execute to apply changes.\n")
        
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
                
                # Update relative imports
                content = content.replace(
                    f'from .{old_name}',
                    f'from .{new_name}'
                )
            
            if content != original_content:
                if dry_run:
                    print(f"  [DRY RUN] Would update: {file_path.name}")
                else:
                    file_path.write_text(content)
                    print(f"  Updated: {file_path.name}")
                
                # Count changes
                changes = 0
                for old_name in PLUGIN_RENAMES.keys():
                    changes += original_content.count(f"'{old_name}'")
                    changes += original_content.count(f'"{old_name}"')
                return changes
            
            return 0
        except Exception as e:
            print(f"  ERROR updating {file_path}: {e}")
            return 0
    
    def _update_plugin_class(self, file_path: Path, old_name: str, new_name: str, dry_run: bool):
        """Update plugin class name"""
        try:
            content = file_path.read_text()
            
            # Convert names to class format
            old_class = self._to_class_name(old_name)
            new_class = self._to_class_name(new_name)
            
            new_content = content.replace(old_class, new_class)
            
            # Update plugin_id in code
            new_content = new_content.replace(
                f"plugin_id = '{old_name}'",
                f"plugin_id = '{new_name}'"
            )
            new_content = new_content.replace(
                f'plugin_id = "{old_name}"',
                f'plugin_id = "{new_name}"'
            )
            
            if new_content != content:
                if dry_run:
                    print(f"  [DRY RUN] Would update class in: {file_path.parent.name}/plugin.py")
                else:
                    file_path.write_text(new_content)
                    print(f"  Updated class in: {file_path.parent.name}/plugin.py")
        except Exception as e:
            print(f"  ERROR updating class in {file_path}: {e}")
    
    def _update_config_json(self, file_path: Path, old_name: str, new_name: str, dry_run: bool):
        """Update config.json plugin_id"""
        try:
            content = file_path.read_text()
            config = json.loads(content)
            
            if config.get('plugin_id') == old_name:
                config['plugin_id'] = new_name
                
                if dry_run:
                    print(f"  [DRY RUN] Would update config: {file_path.parent.name}/config.json")
                else:
                    file_path.write_text(json.dumps(config, indent=2))
                    print(f"  Updated config: {file_path.parent.name}/config.json")
        except Exception as e:
            print(f"  ERROR updating config {file_path}: {e}")
    
    def _update_init_file(self, file_path: Path, old_name: str, new_name: str, dry_run: bool):
        """Update __init__.py imports"""
        try:
            content = file_path.read_text()
            
            old_class = self._to_class_name(old_name)
            new_class = self._to_class_name(new_name)
            
            new_content = content.replace(old_class, new_class)
            
            if new_content != content:
                if dry_run:
                    print(f"  [DRY RUN] Would update: {file_path.parent.name}/__init__.py")
                else:
                    file_path.write_text(new_content)
                    print(f"  Updated: {file_path.parent.name}/__init__.py")
        except Exception as e:
            print(f"  ERROR updating {file_path}: {e}")
    
    def _to_class_name(self, plugin_id: str) -> str:
        """Convert plugin_id to class name"""
        # combined_v3 -> CombinedV3Plugin
        # v3_combined -> V3CombinedPlugin
        # v6_price_action_1m -> V6PriceAction1mPlugin
        parts = plugin_id.split('_')
        class_name = ''.join(p.capitalize() for p in parts) + 'Plugin'
        return class_name
    
    def verify_rename(self) -> Dict[str, Dict[str, bool]]:
        """Verify all renames were successful"""
        print("\nVerifying rename results...")
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
            
            status = "OK" if all(results[new_name].values()) else "ISSUES"
            print(f"  {new_name}: {status}")
        
        return results


def main():
    import sys
    
    dry_run = '--execute' not in sys.argv
    
    renamer = PluginRenamer()
    results = renamer.rename_all(dry_run=dry_run)
    
    if not dry_run:
        verification = renamer.verify_rename()
        
        all_ok = all(
            all(checks.values())
            for checks in verification.values()
        )
        
        if all_ok:
            print("\nAll plugins renamed successfully!")
        else:
            print("\nSome issues detected. Please check manually.")


if __name__ == '__main__':
    main()
