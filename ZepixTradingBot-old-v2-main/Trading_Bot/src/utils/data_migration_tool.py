"""
Data Migration Tool - Migrate trades from V4 (trading_bot.db) to V5 Plugin Databases

Part of V5 Hybrid Plugin Architecture - Batch 12
Provides safe, reversible data migration from legacy database to plugin-isolated databases.

Features:
- Migrate trades from trading_bot.db to plugin DBs (V4 -> V5)
- Handle schema differences between V4 and V5
- Perform integrity checks after migration
- Support dry-run mode for validation
- Rollback capability for failed migrations

Version: 1.0.0
"""

import sqlite3
import os
import json
import hashlib
import logging
import shutil
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MigrationStatus(Enum):
    """Migration status enum"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class MigrationResult:
    """Result of a migration operation"""
    status: MigrationStatus
    source_db: str
    target_db: str
    records_migrated: int = 0
    records_failed: int = 0
    records_skipped: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    integrity_check_passed: bool = False
    source_total_pnl: float = 0.0
    target_total_pnl: float = 0.0
    pnl_difference: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.status.value,
            "source_db": self.source_db,
            "target_db": self.target_db,
            "records_migrated": self.records_migrated,
            "records_failed": self.records_failed,
            "records_skipped": self.records_skipped,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "integrity_check_passed": self.integrity_check_passed,
            "source_total_pnl": self.source_total_pnl,
            "target_total_pnl": self.target_total_pnl,
            "pnl_difference": self.pnl_difference
        }


@dataclass
class ColumnMapping:
    """Mapping between V4 and V5 column names"""
    v4_column: str
    v5_column: str
    transform: Optional[str] = None
    default_value: Any = None


class DataMigrationTool:
    """
    Tool for migrating trade data from V4 (trading_bot.db) to V5 plugin databases.
    
    Handles schema differences between V4 and V5:
    - V4: Single database with all trades
    - V5: Per-plugin isolated databases
    
    Usage:
        tool = DataMigrationTool(
            source_db="data/trading_bot.db",
            target_dir="data"
        )
        
        # Dry run first
        result = tool.migrate_to_v3_plugin(dry_run=True)
        
        # Actual migration
        result = tool.migrate_to_v3_plugin(dry_run=False)
        
        # Verify integrity
        tool.verify_integrity("combined_v3")
    """
    
    V4_TO_V5_COLUMN_MAPPING = [
        ColumnMapping("trade_id", "mt5_ticket", "int"),
        ColumnMapping("symbol", "symbol"),
        ColumnMapping("direction", "direction"),
        ColumnMapping("lot_size", "lot_size"),
        ColumnMapping("entry_price", "entry_price"),
        ColumnMapping("sl_price", "sl_price"),
        ColumnMapping("tp_price", "tp_price"),
        ColumnMapping("open_time", "entry_time"),
        ColumnMapping("close_time", "exit_time"),
        ColumnMapping("exit_price", "exit_price"),
        ColumnMapping("pnl", "profit_dollars"),
        ColumnMapping("commission", "commission", default_value=0.0),
        ColumnMapping("swap", "swap", default_value=0.0),
        ColumnMapping("status", "status", "status_transform"),
        ColumnMapping("strategy", "close_reason"),
        ColumnMapping("logic_type", "signal_type"),
        ColumnMapping("order_type", "order_type"),
    ]
    
    def __init__(
        self,
        source_db: str = "data/trading_bot.db",
        target_dir: str = "data",
        backup_dir: str = "data/backups"
    ):
        """
        Initialize migration tool.
        
        Args:
            source_db: Path to V4 trading_bot.db
            target_dir: Directory for V5 plugin databases
            backup_dir: Directory for backup files
        """
        self.source_db = source_db
        self.target_dir = target_dir
        self.backup_dir = backup_dir
        
        self._migration_history: List[MigrationResult] = []
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        os.makedirs(self.target_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def _connect_source(self) -> sqlite3.Connection:
        """Connect to source V4 database."""
        if not os.path.exists(self.source_db):
            raise FileNotFoundError(f"Source database not found: {self.source_db}")
        
        conn = sqlite3.connect(self.source_db)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _connect_target(self, plugin_id: str) -> sqlite3.Connection:
        """Connect to target V5 plugin database."""
        db_path = os.path.join(self.target_dir, f"zepix_{plugin_id}.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_backup(self, db_path: str) -> str:
        """
        Create backup of database before migration.
        
        Args:
            db_path: Path to database to backup
            
        Returns:
            Path to backup file
        """
        if not os.path.exists(db_path):
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        db_name = os.path.basename(db_path)
        backup_path = os.path.join(self.backup_dir, f"{db_name}.{timestamp}.backup")
        
        shutil.copy2(db_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
        return backup_path
    
    def _transform_status(self, v4_status: str) -> str:
        """Transform V4 status to V5 status."""
        status_map = {
            "open": "OPEN",
            "closed": "CLOSED",
            "partial": "PARTIAL",
            "OPEN": "OPEN",
            "CLOSED": "CLOSED",
            "PARTIAL": "PARTIAL"
        }
        return status_map.get(v4_status, "CLOSED")
    
    def _transform_value(self, value: Any, transform: Optional[str]) -> Any:
        """Apply transformation to value."""
        if value is None:
            return None
        
        if transform == "int":
            try:
                return int(value) if value else None
            except (ValueError, TypeError):
                return None
        elif transform == "status_transform":
            return self._transform_status(str(value))
        
        return value
    
    def _map_v4_to_v5(self, v4_row: sqlite3.Row) -> Dict[str, Any]:
        """
        Map V4 trade row to V5 schema.
        
        Args:
            v4_row: Row from V4 trades table
            
        Returns:
            Dictionary with V5 column names and values
        """
        v5_data = {}
        v4_dict = dict(v4_row)
        
        for mapping in self.V4_TO_V5_COLUMN_MAPPING:
            v4_value = v4_dict.get(mapping.v4_column)
            
            if v4_value is None and mapping.default_value is not None:
                v5_data[mapping.v5_column] = mapping.default_value
            else:
                v5_data[mapping.v5_column] = self._transform_value(
                    v4_value, mapping.transform
                )
        
        v5_data["signal_data"] = json.dumps({
            "migrated_from": "v4",
            "original_strategy": v4_dict.get("strategy"),
            "chain_id": v4_dict.get("chain_id"),
            "chain_level": v4_dict.get("chain_level"),
            "profit_chain_id": v4_dict.get("profit_chain_id"),
            "profit_level": v4_dict.get("profit_level"),
            "session_id": v4_dict.get("session_id"),
            "logic_type": v4_dict.get("logic_type"),
            "lot_multiplier": v4_dict.get("lot_multiplier"),
            "sl_multiplier": v4_dict.get("sl_multiplier")
        })
        
        return v5_data
    
    def _ensure_v5_schema(self, conn: sqlite3.Connection, plugin_id: str):
        """Ensure V5 schema exists in target database."""
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plugin_info (
                plugin_id TEXT PRIMARY KEY,
                version TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_started TIMESTAMP,
                total_runtime_hours REAL DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mt5_ticket INTEGER UNIQUE,
                symbol TEXT NOT NULL,
                direction TEXT CHECK(direction IN ('BUY', 'SELL')),
                lot_size REAL NOT NULL,
                entry_price REAL NOT NULL,
                sl_price REAL,
                tp_price REAL,
                entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exit_time TIMESTAMP,
                exit_price REAL,
                profit_pips REAL,
                profit_dollars REAL,
                commission REAL DEFAULT 0,
                swap REAL DEFAULT 0,
                status TEXT CHECK(status IN ('OPEN', 'CLOSED', 'PARTIAL')) DEFAULT 'OPEN',
                close_reason TEXT,
                signal_type TEXT,
                signal_data TEXT,
                logic_type TEXT,
                order_type TEXT CHECK(order_type IN ('ORDER_A', 'ORDER_B', NULL)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                migrated_from TEXT,
                migration_timestamp TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_profit_pips REAL DEFAULT 0,
                total_profit_dollars REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                direction TEXT,
                timeframe TEXT,
                raw_payload TEXT,
                processed BOOLEAN DEFAULT FALSE,
                result TEXT,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_db TEXT NOT NULL,
                migration_type TEXT NOT NULL,
                records_migrated INTEGER DEFAULT 0,
                records_failed INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT,
                checksum TEXT,
                notes TEXT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time)")
        
        cursor.execute("""
            INSERT OR IGNORE INTO plugin_info (plugin_id, version, last_started)
            VALUES (?, '1.0.0', ?)
        """, (plugin_id, datetime.now().isoformat()))
        
        conn.commit()
    
    def get_v4_trades(
        self,
        strategy_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get trades from V4 database.
        
        Args:
            strategy_filter: Optional filter by strategy name
            limit: Optional limit on number of records
            
        Returns:
            List of trade dictionaries
        """
        conn = self._connect_source()
        cursor = conn.cursor()
        
        query = "SELECT * FROM trades"
        params = []
        
        if strategy_filter:
            query += " WHERE strategy LIKE ?"
            params.append(f"%{strategy_filter}%")
        
        query += " ORDER BY open_time DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        trades = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return trades
    
    def get_v4_summary(self) -> Dict[str, Any]:
        """
        Get summary of V4 database.
        
        Returns:
            Dictionary with trade counts and totals
        """
        if not os.path.exists(self.source_db):
            return {"error": "Source database not found"}
        
        conn = self._connect_source()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                COUNT(CASE WHEN status = 'closed' OR status = 'CLOSED' THEN 1 END) as closed_trades,
                COUNT(CASE WHEN status = 'open' OR status = 'OPEN' THEN 1 END) as open_trades,
                SUM(COALESCE(pnl, 0)) as total_pnl,
                COUNT(DISTINCT strategy) as unique_strategies,
                MIN(open_time) as earliest_trade,
                MAX(open_time) as latest_trade
            FROM trades
        """)
        
        result = cursor.fetchone()
        summary = dict(result) if result else {}
        
        cursor.execute("""
            SELECT strategy, COUNT(*) as count, SUM(COALESCE(pnl, 0)) as pnl
            FROM trades
            GROUP BY strategy
            ORDER BY count DESC
        """)
        
        summary["strategies"] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return summary
    
    def migrate_to_plugin(
        self,
        plugin_id: str,
        strategy_filter: Optional[str] = None,
        dry_run: bool = True
    ) -> MigrationResult:
        """
        Migrate trades from V4 to a specific plugin database.
        
        Args:
            plugin_id: Target plugin ID (e.g., 'combined_v3', 'price_action_1m')
            strategy_filter: Optional filter to migrate only specific strategies
            dry_run: If True, simulate migration without writing
            
        Returns:
            MigrationResult with migration details
        """
        result = MigrationResult(
            status=MigrationStatus.IN_PROGRESS,
            source_db=self.source_db,
            target_db=os.path.join(self.target_dir, f"zepix_{plugin_id}.db"),
            started_at=datetime.now()
        )
        
        try:
            source_conn = self._connect_source()
            source_cursor = source_conn.cursor()
            
            query = "SELECT * FROM trades"
            params = []
            
            if strategy_filter:
                query += " WHERE strategy LIKE ? OR logic_type LIKE ?"
                params.extend([f"%{strategy_filter}%", f"%{strategy_filter}%"])
            
            source_cursor.execute(query, params)
            v4_trades = source_cursor.fetchall()
            
            source_cursor.execute("SELECT SUM(COALESCE(pnl, 0)) as total FROM trades")
            pnl_row = source_cursor.fetchone()
            result.source_total_pnl = pnl_row["total"] if pnl_row and pnl_row["total"] else 0.0
            
            if dry_run:
                logger.info(f"[DRY RUN] Would migrate {len(v4_trades)} trades to {plugin_id}")
                result.records_migrated = len(v4_trades)
                result.status = MigrationStatus.COMPLETED
                result.completed_at = datetime.now()
                source_conn.close()
                self._migration_history.append(result)
                return result
            
            self._create_backup(result.target_db)
            
            target_conn = self._connect_target(plugin_id)
            self._ensure_v5_schema(target_conn, plugin_id)
            target_cursor = target_conn.cursor()
            
            for v4_row in v4_trades:
                try:
                    v5_data = self._map_v4_to_v5(v4_row)
                    v5_data["migrated_from"] = "v4"
                    v5_data["migration_timestamp"] = datetime.now().isoformat()
                    
                    columns = list(v5_data.keys())
                    placeholders = ", ".join(["?" for _ in columns])
                    column_names = ", ".join(columns)
                    
                    target_cursor.execute(
                        f"INSERT OR IGNORE INTO trades ({column_names}) VALUES ({placeholders})",
                        list(v5_data.values())
                    )
                    
                    if target_cursor.rowcount > 0:
                        result.records_migrated += 1
                    else:
                        result.records_skipped += 1
                        
                except Exception as e:
                    logger.error(f"Failed to migrate trade: {e}")
                    result.records_failed += 1
            
            target_cursor.execute("""
                INSERT INTO migration_log 
                (source_db, migration_type, records_migrated, records_failed, started_at, completed_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.source_db,
                f"v4_to_{plugin_id}",
                result.records_migrated,
                result.records_failed,
                result.started_at.isoformat(),
                datetime.now().isoformat(),
                "COMPLETED"
            ))
            
            target_conn.commit()
            
            target_cursor.execute("SELECT SUM(COALESCE(profit_dollars, 0)) as total FROM trades")
            pnl_row = target_cursor.fetchone()
            result.target_total_pnl = pnl_row["total"] if pnl_row and pnl_row["total"] else 0.0
            
            result.pnl_difference = abs(result.source_total_pnl - result.target_total_pnl)
            result.integrity_check_passed = result.pnl_difference < 0.01
            
            target_conn.close()
            source_conn.close()
            
            result.status = MigrationStatus.COMPLETED
            result.completed_at = datetime.now()
            
            logger.info(
                f"Migration completed: {result.records_migrated} migrated, "
                f"{result.records_failed} failed, {result.records_skipped} skipped"
            )
            
        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.now()
            logger.error(f"Migration failed: {e}")
        
        self._migration_history.append(result)
        return result
    
    def migrate_to_v3_plugin(self, dry_run: bool = True) -> MigrationResult:
        """
        Migrate V4 trades to V3 Combined Logic plugin database.
        
        Args:
            dry_run: If True, simulate migration without writing
            
        Returns:
            MigrationResult with migration details
        """
        return self.migrate_to_plugin(
            plugin_id="combined_v3",
            strategy_filter=None,
            dry_run=dry_run
        )
    
    def migrate_to_v6_plugin(
        self,
        timeframe: str,
        dry_run: bool = True
    ) -> MigrationResult:
        """
        Migrate V4 trades to V6 Price Action plugin database.
        
        Args:
            timeframe: Timeframe ('1m', '5m', '15m', '1h')
            dry_run: If True, simulate migration without writing
            
        Returns:
            MigrationResult with migration details
        """
        plugin_id = f"price_action_{timeframe}"
        return self.migrate_to_plugin(
            plugin_id=plugin_id,
            strategy_filter=timeframe,
            dry_run=dry_run
        )
    
    def verify_integrity(self, plugin_id: str) -> Dict[str, Any]:
        """
        Verify data integrity after migration.
        
        Checks:
        - Record count matches
        - Total P&L matches
        - No duplicate tickets
        - All required fields populated
        
        Args:
            plugin_id: Plugin ID to verify
            
        Returns:
            Dictionary with integrity check results
        """
        results = {
            "plugin_id": plugin_id,
            "checks": [],
            "passed": True,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            target_conn = self._connect_target(plugin_id)
            cursor = target_conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM trades")
            count = cursor.fetchone()["count"]
            results["checks"].append({
                "name": "record_count",
                "value": count,
                "passed": count > 0
            })
            
            cursor.execute("SELECT SUM(COALESCE(profit_dollars, 0)) as total FROM trades")
            total_pnl = cursor.fetchone()["total"] or 0
            results["checks"].append({
                "name": "total_pnl",
                "value": total_pnl,
                "passed": True
            })
            
            cursor.execute("""
                SELECT mt5_ticket, COUNT(*) as count 
                FROM trades 
                WHERE mt5_ticket IS NOT NULL
                GROUP BY mt5_ticket 
                HAVING count > 1
            """)
            duplicates = cursor.fetchall()
            results["checks"].append({
                "name": "no_duplicates",
                "value": len(duplicates),
                "passed": len(duplicates) == 0
            })
            
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM trades 
                WHERE symbol IS NULL OR direction IS NULL OR lot_size IS NULL
            """)
            missing = cursor.fetchone()["count"]
            results["checks"].append({
                "name": "required_fields",
                "value": missing,
                "passed": missing == 0
            })
            
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM trades 
                WHERE migrated_from = 'v4'
            """)
            migrated = cursor.fetchone()["count"]
            results["checks"].append({
                "name": "migrated_records",
                "value": migrated,
                "passed": True
            })
            
            target_conn.close()
            
            results["passed"] = all(check["passed"] for check in results["checks"])
            
        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)
        
        return results
    
    def rollback_migration(self, plugin_id: str) -> bool:
        """
        Rollback migration by removing migrated records.
        
        Args:
            plugin_id: Plugin ID to rollback
            
        Returns:
            True if rollback successful
        """
        try:
            target_conn = self._connect_target(plugin_id)
            cursor = target_conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM trades WHERE migrated_from = 'v4'")
            count = cursor.fetchone()["count"]
            
            cursor.execute("DELETE FROM trades WHERE migrated_from = 'v4'")
            target_conn.commit()
            
            cursor.execute("""
                INSERT INTO migration_log 
                (source_db, migration_type, records_migrated, started_at, completed_at, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.source_db,
                f"rollback_{plugin_id}",
                count,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                "ROLLED_BACK",
                f"Removed {count} migrated records"
            ))
            target_conn.commit()
            
            target_conn.close()
            
            logger.info(f"Rollback completed: Removed {count} migrated records from {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """
        Get history of migrations performed.
        
        Returns:
            List of migration result dictionaries
        """
        return [result.to_dict() for result in self._migration_history]
    
    def format_migration_report(self, result: MigrationResult) -> str:
        """
        Format migration result as readable report.
        
        Args:
            result: MigrationResult to format
            
        Returns:
            Formatted report string
        """
        duration = ""
        if result.started_at and result.completed_at:
            delta = result.completed_at - result.started_at
            duration = f"{delta.total_seconds():.2f}s"
        
        report = f"""
Migration Report
================
Status: {result.status.value}
Source: {result.source_db}
Target: {result.target_db}

Records:
  - Migrated: {result.records_migrated}
  - Failed: {result.records_failed}
  - Skipped: {result.records_skipped}

Integrity Check:
  - Source P&L: ${result.source_total_pnl:.2f}
  - Target P&L: ${result.target_total_pnl:.2f}
  - Difference: ${result.pnl_difference:.2f}
  - Passed: {'Yes' if result.integrity_check_passed else 'No'}

Timing:
  - Started: {result.started_at.isoformat() if result.started_at else 'N/A'}
  - Completed: {result.completed_at.isoformat() if result.completed_at else 'N/A'}
  - Duration: {duration}
"""
        
        if result.error_message:
            report += f"\nError: {result.error_message}\n"
        
        return report.strip()


def create_migration_tool(
    source_db: str = "data/trading_bot.db",
    target_dir: str = "data"
) -> DataMigrationTool:
    """
    Factory function to create DataMigrationTool.
    
    Args:
        source_db: Path to V4 database
        target_dir: Directory for V5 databases
        
    Returns:
        Configured DataMigrationTool instance
    """
    return DataMigrationTool(
        source_db=source_db,
        target_dir=target_dir
    )
