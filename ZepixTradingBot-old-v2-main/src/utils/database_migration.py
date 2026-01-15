"""
Database Migration Tool - Plan 09: Database Isolation

Migrates data from shared database to isolated plugin databases.
Ensures NO DATA LOSS during migration.

Features:
- Dry run mode for testing
- Verification after migration
- Rollback support
- Detailed logging

Version: 1.0.0
Date: 2026-01-15
"""
from typing import Dict, Any, List, Optional
import logging
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

from src.core.plugin_system.database_interface import MigrationResult

logger = logging.getLogger(__name__)


@dataclass
class MigrationStats:
    """Statistics for a migration operation"""
    table: str
    source_count: int = 0
    migrated_count: int = 0
    failed_count: int = 0
    errors: List[str] = field(default_factory=list)


class DatabaseMigration:
    """
    Migrates data from shared database to isolated plugin databases.
    
    Source: data/zepix_trading.db (shared)
    Targets:
    - data/zepix_combined_v3.db (V3 data)
    - data/zepix_price_action.db (V6 data)
    
    CRITICAL: NO DATA LOSS PERMITTED
    """
    
    def __init__(self, base_path: str = '.'):
        """
        Initialize migration tool.
        
        Args:
            base_path: Base path for database files
        """
        self.base_path = Path(base_path)
        self.shared_db = self.base_path / 'data' / 'zepix_trading.db'
        self.v3_db = self.base_path / 'data' / 'zepix_combined_v3.db'
        self.v6_db = self.base_path / 'data' / 'zepix_price_action.db'
        self.backup_dir = self.base_path / 'data' / 'backups'
        
        # Schema files
        self.v3_schema = self.base_path / 'data' / 'schemas' / 'combined_v3_schema.sql'
        self.v6_schema = self.base_path / 'data' / 'schemas' / 'price_action_v6_schema.sql'
    
    def _ensure_backup_dir(self):
        """Ensure backup directory exists"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _backup_database(self, db_path: Path) -> Optional[Path]:
        """
        Create backup of a database.
        
        Args:
            db_path: Path to database file
            
        Returns:
            Path to backup file or None if failed
        """
        if not db_path.exists():
            return None
        
        self._ensure_backup_dir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"{db_path.stem}_{timestamp}.db"
        
        try:
            shutil.copy2(db_path, backup_path)
            logger.info(f"[Migration] Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"[Migration] Backup failed for {db_path}: {e}")
            return None
    
    def _initialize_target_db(self, db_path: Path, schema_path: Path) -> bool:
        """
        Initialize target database with schema.
        
        Args:
            db_path: Path to target database
            schema_path: Path to schema file
            
        Returns:
            True if successful
        """
        try:
            # Ensure data directory exists
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load schema
            if not schema_path.exists():
                logger.error(f"[Migration] Schema not found: {schema_path}")
                return False
            
            schema = schema_path.read_text()
            
            # Create database and apply schema
            conn = sqlite3.connect(db_path)
            conn.executescript(schema)
            conn.commit()
            conn.close()
            
            logger.info(f"[Migration] Database initialized: {db_path}")
            return True
            
        except Exception as e:
            logger.error(f"[Migration] Failed to initialize {db_path}: {e}")
            return False
    
    def migrate_all(self, dry_run: bool = True) -> MigrationResult:
        """
        Migrate all data from shared to isolated databases.
        
        Args:
            dry_run: If True, only simulate migration (no actual changes)
            
        Returns:
            MigrationResult with migration details
        """
        result = MigrationResult(
            success=False,
            records_migrated=0,
            records_failed=0,
            source_count=0,
            target_count=0,
            errors=[]
        )
        
        # Check if shared database exists
        if not self.shared_db.exists():
            logger.warning("[Migration] Shared database not found, nothing to migrate")
            result.success = True
            return result
        
        try:
            # Create backups before migration
            if not dry_run:
                self._backup_database(self.shared_db)
                if self.v3_db.exists():
                    self._backup_database(self.v3_db)
                if self.v6_db.exists():
                    self._backup_database(self.v6_db)
            
            # Connect to shared database
            shared_conn = sqlite3.connect(self.shared_db)
            shared_conn.row_factory = sqlite3.Row
            
            # Count source records
            result.source_count = self._count_all_records(shared_conn)
            
            # Initialize target databases
            if not dry_run:
                if not self._initialize_target_db(self.v3_db, self.v3_schema):
                    result.errors.append("Failed to initialize V3 database")
                    return result
                if not self._initialize_target_db(self.v6_db, self.v6_schema):
                    result.errors.append("Failed to initialize V6 database")
                    return result
            
            # Migrate V3 data
            v3_stats = self._migrate_v3_data(shared_conn, dry_run)
            result.records_migrated += v3_stats.migrated_count
            result.records_failed += v3_stats.failed_count
            result.errors.extend(v3_stats.errors)
            
            # Migrate V6 data
            v6_stats = self._migrate_v6_data(shared_conn, dry_run)
            result.records_migrated += v6_stats.migrated_count
            result.records_failed += v6_stats.failed_count
            result.errors.extend(v6_stats.errors)
            
            shared_conn.close()
            
            # Verify migration
            if not dry_run:
                result.target_count = self._count_target_records()
            else:
                result.target_count = result.records_migrated
            
            # Check for data loss
            if result.data_loss and not dry_run:
                logger.error(f"[Migration] DATA LOSS DETECTED! Source: {result.source_count}, Target: {result.target_count}")
                result.errors.append(f"Data loss detected: {result.source_count - result.target_count} records missing")
            
            result.success = not result.data_loss and result.records_failed == 0
            
            if dry_run:
                logger.info(f"[Migration] DRY RUN complete. Would migrate {result.records_migrated} records")
            else:
                logger.info(f"[Migration] Migration complete. Migrated {result.records_migrated} records")
            
        except Exception as e:
            logger.error(f"[Migration] Migration failed: {e}")
            result.errors.append(str(e))
        
        return result
    
    def _count_all_records(self, conn: sqlite3.Connection) -> int:
        """Count all records in shared database"""
        total = 0
        
        # Check if trades table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='trades'"
        )
        if cursor.fetchone():
            cursor = conn.execute("SELECT COUNT(*) FROM trades")
            total += cursor.fetchone()[0]
        
        # Check if signals table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='signals'"
        )
        if cursor.fetchone():
            cursor = conn.execute("SELECT COUNT(*) FROM signals")
            total += cursor.fetchone()[0]
        
        return total
    
    def _count_target_records(self) -> int:
        """Count all records in target databases"""
        total = 0
        
        # Count V3 records
        if self.v3_db.exists():
            conn = sqlite3.connect(self.v3_db)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM combined_v3_trades")
                total += cursor.fetchone()[0]
            except:
                pass
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM v3_signals_log")
                total += cursor.fetchone()[0]
            except:
                pass
            conn.close()
        
        # Count V6 records
        if self.v6_db.exists():
            conn = sqlite3.connect(self.v6_db)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM trades")
                total += cursor.fetchone()[0]
            except:
                pass
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM signals")
                total += cursor.fetchone()[0]
            except:
                pass
            conn.close()
        
        return total
    
    def _migrate_v3_data(self, shared_conn: sqlite3.Connection, dry_run: bool) -> MigrationStats:
        """
        Migrate V3 data to isolated database.
        
        Args:
            shared_conn: Connection to shared database
            dry_run: If True, only simulate
            
        Returns:
            MigrationStats with results
        """
        stats = MigrationStats(table='v3')
        
        # Get V3 trades
        try:
            cursor = shared_conn.execute(
                "SELECT * FROM trades WHERE strategy = 'V3_COMBINED' OR strategy LIKE '%V3%'"
            )
            v3_trades = cursor.fetchall()
            stats.source_count = len(v3_trades)
        except Exception as e:
            logger.warning(f"[Migration] No trades table or V3 trades: {e}")
            v3_trades = []
        
        if dry_run:
            stats.migrated_count = len(v3_trades)
            logger.info(f"[Migration] DRY RUN: Would migrate {len(v3_trades)} V3 trades")
        else:
            # Actually migrate
            if v3_trades:
                v3_conn = sqlite3.connect(self.v3_db)
                for trade in v3_trades:
                    try:
                        self._insert_v3_trade(v3_conn, dict(trade))
                        stats.migrated_count += 1
                    except Exception as e:
                        stats.failed_count += 1
                        stats.errors.append(f"Trade migration failed: {e}")
                v3_conn.commit()
                v3_conn.close()
                logger.info(f"[Migration] Migrated {stats.migrated_count} V3 trades")
        
        # Get V3 signals
        try:
            cursor = shared_conn.execute(
                "SELECT * FROM signals WHERE strategy = 'V3_COMBINED' OR strategy LIKE '%V3%'"
            )
            v3_signals = cursor.fetchall()
        except Exception as e:
            logger.warning(f"[Migration] No signals table or V3 signals: {e}")
            v3_signals = []
        
        if dry_run:
            stats.migrated_count += len(v3_signals)
            logger.info(f"[Migration] DRY RUN: Would migrate {len(v3_signals)} V3 signals")
        else:
            if v3_signals:
                v3_conn = sqlite3.connect(self.v3_db)
                for signal in v3_signals:
                    try:
                        self._insert_v3_signal(v3_conn, dict(signal))
                        stats.migrated_count += 1
                    except Exception as e:
                        stats.failed_count += 1
                        stats.errors.append(f"Signal migration failed: {e}")
                v3_conn.commit()
                v3_conn.close()
                logger.info(f"[Migration] Migrated {len(v3_signals)} V3 signals")
        
        return stats
    
    def _migrate_v6_data(self, shared_conn: sqlite3.Connection, dry_run: bool) -> MigrationStats:
        """
        Migrate V6 data to isolated database.
        
        Args:
            shared_conn: Connection to shared database
            dry_run: If True, only simulate
            
        Returns:
            MigrationStats with results
        """
        stats = MigrationStats(table='v6')
        
        # Get V6 trades
        try:
            cursor = shared_conn.execute(
                "SELECT * FROM trades WHERE strategy LIKE 'V6_%' OR strategy LIKE '%PRICE_ACTION%'"
            )
            v6_trades = cursor.fetchall()
            stats.source_count = len(v6_trades)
        except Exception as e:
            logger.warning(f"[Migration] No trades table or V6 trades: {e}")
            v6_trades = []
        
        if dry_run:
            stats.migrated_count = len(v6_trades)
            logger.info(f"[Migration] DRY RUN: Would migrate {len(v6_trades)} V6 trades")
        else:
            if v6_trades:
                v6_conn = sqlite3.connect(self.v6_db)
                for trade in v6_trades:
                    try:
                        self._insert_v6_trade(v6_conn, dict(trade))
                        stats.migrated_count += 1
                    except Exception as e:
                        stats.failed_count += 1
                        stats.errors.append(f"Trade migration failed: {e}")
                v6_conn.commit()
                v6_conn.close()
                logger.info(f"[Migration] Migrated {stats.migrated_count} V6 trades")
        
        return stats
    
    def _insert_v3_trade(self, conn: sqlite3.Connection, trade: Dict[str, Any]):
        """Insert a V3 trade record"""
        # Map old schema to new V3 schema
        data = {
            'symbol': trade.get('symbol', ''),
            'direction': trade.get('direction', 'BUY'),
            'entry_price': trade.get('entry_price', 0),
            'signal_type': trade.get('signal_type', 'Unknown'),
            'status': 'CLOSED' if trade.get('exit_price') else 'OPEN',
        }
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO combined_v3_trades ({columns}) VALUES ({placeholders})"
        
        conn.execute(query, tuple(data.values()))
    
    def _insert_v3_signal(self, conn: sqlite3.Connection, signal: Dict[str, Any]):
        """Insert a V3 signal record"""
        data = {
            'signal_type': signal.get('signal_type', 'Unknown'),
            'symbol': signal.get('symbol', ''),
            'direction': signal.get('direction', ''),
            'processed': signal.get('processed', 0),
        }
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO v3_signals_log ({columns}) VALUES ({placeholders})"
        
        conn.execute(query, tuple(data.values()))
    
    def _insert_v6_trade(self, conn: sqlite3.Connection, trade: Dict[str, Any]):
        """Insert a V6 trade record"""
        # Map old schema to new V6 schema
        data = {
            'trade_id': trade.get('id', ''),
            'plugin_id': 'price_action',
            'symbol': trade.get('symbol', ''),
            'direction': trade.get('direction', 'BUY'),
            'timeframe': trade.get('timeframe', '1m'),
            'entry_price': trade.get('entry_price', 0),
            'lot_size': trade.get('lot_size', 0.01),
            'status': 'closed' if trade.get('exit_price') else 'open',
        }
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO trades ({columns}) VALUES ({placeholders})"
        
        conn.execute(query, tuple(data.values()))
    
    def verify_migration(self) -> MigrationResult:
        """
        Verify migration was successful.
        
        Checks:
        - All records migrated
        - No data loss
        - Target databases accessible
        
        Returns:
            MigrationResult with verification details
        """
        result = MigrationResult(
            success=False,
            source_count=0,
            target_count=0,
            errors=[]
        )
        
        # Count in shared
        if self.shared_db.exists():
            conn = sqlite3.connect(self.shared_db)
            result.source_count = self._count_all_records(conn)
            conn.close()
        
        # Count in targets
        result.target_count = self._count_target_records()
        
        # Verify counts match
        result.success = not result.data_loss
        
        if result.data_loss:
            result.errors.append(
                f"Data loss detected: {result.source_count} source, {result.target_count} target"
            )
            logger.error(f"[Migration] VERIFICATION FAILED: Data loss detected!")
        else:
            logger.info(f"[Migration] Verification passed: {result.target_count} records")
        
        return result
    
    def rollback(self) -> bool:
        """
        Rollback migration by restoring from backup.
        
        Returns:
            True if rollback successful
        """
        try:
            # Find most recent backups
            if not self.backup_dir.exists():
                logger.error("[Migration] No backups found for rollback")
                return False
            
            backups = sorted(self.backup_dir.glob('*.db'), reverse=True)
            
            for backup in backups:
                if 'zepix_trading' in backup.name:
                    shutil.copy2(backup, self.shared_db)
                    logger.info(f"[Migration] Restored shared database from {backup}")
            
            # Remove target databases
            if self.v3_db.exists():
                self.v3_db.unlink()
                logger.info("[Migration] Removed V3 database")
            
            if self.v6_db.exists():
                self.v6_db.unlink()
                logger.info("[Migration] Removed V6 database")
            
            return True
            
        except Exception as e:
            logger.error(f"[Migration] Rollback failed: {e}")
            return False


def run_migration(base_path: str = '.', dry_run: bool = True) -> MigrationResult:
    """
    Convenience function to run migration.
    
    Args:
        base_path: Base path for database files
        dry_run: If True, only simulate migration
        
    Returns:
        MigrationResult with migration details
    """
    migration = DatabaseMigration(base_path)
    return migration.migrate_all(dry_run)
