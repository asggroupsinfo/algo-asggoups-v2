"""
Database Sync Manager - Synchronization Between Plugin and Central Databases

Part of V5 Hybrid Plugin Architecture - Batch 09
Ensures reliable synchronization with error recovery and retry logic.

Features:
- Automatic sync every 5 minutes
- Retry logic with exponential backoff
- Manual sync trigger via /sync_manual command
- Health monitoring and alerts
- Complete audit trail

Version: 1.0.0
"""

import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Sync operation status"""
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"
    PENDING = "pending"


@dataclass
class SyncResult:
    """Result of a sync operation"""
    plugin_id: str
    status: SyncStatus
    records_synced: int
    error_message: Optional[str]
    duration_ms: int
    timestamp: datetime
    retry_count: int = 0


@dataclass
class SyncConfig:
    """Configuration for sync manager"""
    sync_interval_seconds: int = 300
    max_retries: int = 3
    retry_delay_seconds: int = 5
    backoff_multiplier: float = 2.0
    alert_threshold: int = 3
    max_history: int = 1000


class DatabaseSyncError(Exception):
    """Base exception for sync errors"""
    pass


class DatabaseSyncManager:
    """
    Enhanced sync manager with error recovery.
    
    Syncs trades from plugin databases (V3/V6) to central aggregated_trades table.
    """
    
    def __init__(
        self,
        config: Optional[SyncConfig] = None,
        v3_db_path: str = "data/zepix_combined_v3.db",
        v6_db_path: str = "data/zepix_price_action.db",
        central_db_path: str = "data/zepix_central.db"
    ):
        self.config = config or SyncConfig()
        
        self.v3_db_path = v3_db_path
        self.v6_db_path = v6_db_path
        self.central_db_path = central_db_path
        
        self.last_sync_time: Dict[str, datetime] = {}
        self.sync_history: List[SyncResult] = []
        
        self.consecutive_failures: Dict[str, int] = {}
        
        self._running = False
        self._sync_task: Optional[asyncio.Task] = None
        self._manual_sync_event = asyncio.Event()
        
        self.stats = {
            "total_syncs": 0,
            "total_success": 0,
            "total_failures": 0,
            "total_retries": 0,
            "total_records_synced": 0
        }
        
        self._alert_callback: Optional[callable] = None
        
        self._plugin_db_mapping = {
            "combined_v3": self.v3_db_path,
            "price_action_1m": self.v6_db_path,
            "price_action_5m": self.v6_db_path,
            "price_action_15m": self.v6_db_path,
            "price_action_1h": self.v6_db_path
        }
        
        self._table_mapping = {
            "combined_v3": "trades",
            "price_action_1m": "trades",
            "price_action_5m": "trades",
            "price_action_15m": "trades",
            "price_action_1h": "trades"
        }
    
    async def start(self):
        """Start automatic sync scheduler."""
        if self._running:
            logger.warning("Sync manager already running")
            return
        
        self._running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
        logger.info(
            f"Database sync manager started "
            f"(interval: {self.config.sync_interval_seconds}s)"
        )
    
    async def stop(self):
        """Stop sync scheduler."""
        self._running = False
        
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Database sync manager stopped")
    
    async def _sync_loop(self):
        """Main sync loop (runs at configured interval)."""
        while self._running:
            try:
                try:
                    await asyncio.wait_for(
                        self._manual_sync_event.wait(),
                        timeout=self.config.sync_interval_seconds
                    )
                    self._manual_sync_event.clear()
                    logger.info("Manual sync triggered")
                except asyncio.TimeoutError:
                    pass
                
                await self.sync_all_plugins()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                await asyncio.sleep(60)
    
    async def sync_all_plugins(self) -> List[SyncResult]:
        """
        Sync all plugins with retry logic.
        
        Returns:
            List of sync results for each plugin
        """
        results = []
        
        for plugin_id, db_path in self._plugin_db_mapping.items():
            result = await self._sync_plugin_with_retry(plugin_id, db_path)
            results.append(result)
        
        await self._check_and_alert_failures()
        
        return results
    
    async def sync_plugin(self, plugin_id: str) -> SyncResult:
        """
        Sync a specific plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            SyncResult
        """
        db_path = self._plugin_db_mapping.get(plugin_id)
        if not db_path:
            return SyncResult(
                plugin_id=plugin_id,
                status=SyncStatus.FAILED,
                records_synced=0,
                error_message=f"Unknown plugin: {plugin_id}",
                duration_ms=0,
                timestamp=datetime.now()
            )
        
        return await self._sync_plugin_with_retry(plugin_id, db_path)
    
    async def _sync_plugin_with_retry(
        self,
        plugin_id: str,
        plugin_db_path: str
    ) -> SyncResult:
        """
        Sync single plugin with retry logic.
        
        Retry Strategy:
        1. Try 1: Immediate
        2. Try 2: After retry_delay_seconds
        3. Try 3: After retry_delay * backoff_multiplier
        4. Try 4: After retry_delay * backoff_multiplier^2
        """
        retry_count = 0
        last_error = None
        
        while retry_count <= self.config.max_retries:
            try:
                result = await self._sync_plugin(plugin_id, plugin_db_path)
                
                if result.status == SyncStatus.SUCCESS or result.status == SyncStatus.SKIPPED:
                    self.consecutive_failures[plugin_id] = 0
                    return result
                else:
                    last_error = result.error_message
                    raise DatabaseSyncError(f"Sync failed: {last_error}")
                
            except Exception as e:
                retry_count += 1
                last_error = str(e)
                
                if retry_count <= self.config.max_retries:
                    delay = self.config.retry_delay_seconds * (
                        self.config.backoff_multiplier ** (retry_count - 1)
                    )
                    
                    logger.warning(
                        f"Sync failed for {plugin_id} "
                        f"(attempt {retry_count}/{self.config.max_retries}). "
                        f"Retrying in {delay}s... Error: {e}"
                    )
                    
                    self.stats["total_retries"] += 1
                    
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Sync FAILED for {plugin_id} after "
                        f"{self.config.max_retries} retries. Error: {e}"
                    )
                    
                    self.consecutive_failures[plugin_id] = (
                        self.consecutive_failures.get(plugin_id, 0) + 1
                    )
                    
                    result = SyncResult(
                        plugin_id=plugin_id,
                        status=SyncStatus.FAILED,
                        records_synced=0,
                        error_message=last_error,
                        duration_ms=0,
                        timestamp=datetime.now(),
                        retry_count=retry_count
                    )
                    
                    self._add_to_history(result)
                    self.stats["total_syncs"] += 1
                    self.stats["total_failures"] += 1
                    
                    return result
        
        return SyncResult(
            plugin_id=plugin_id,
            status=SyncStatus.FAILED,
            records_synced=0,
            error_message=last_error or "Unknown error",
            duration_ms=0,
            timestamp=datetime.now(),
            retry_count=retry_count
        )
    
    async def _sync_plugin(
        self,
        plugin_id: str,
        plugin_db_path: str
    ) -> SyncResult:
        """
        Perform actual sync (single attempt).
        
        Returns:
            SyncResult with outcome
        """
        start_time = datetime.now()
        
        try:
            import os
            if not os.path.exists(plugin_db_path):
                return SyncResult(
                    plugin_id=plugin_id,
                    status=SyncStatus.SKIPPED,
                    records_synced=0,
                    error_message=f"Database not found: {plugin_db_path}",
                    duration_ms=0,
                    timestamp=datetime.now()
                )
            
            if not os.path.exists(self.central_db_path):
                self._create_central_db()
            
            plugin_db = sqlite3.connect(plugin_db_path)
            central_db = sqlite3.connect(self.central_db_path)
            
            plugin_db.row_factory = sqlite3.Row
            
            try:
                last_synced_id = self._get_last_synced_id(central_db, plugin_id)
                
                new_records = self._fetch_new_records(
                    plugin_db,
                    plugin_id,
                    last_synced_id
                )
                
                if len(new_records) == 0:
                    duration = (datetime.now() - start_time).total_seconds() * 1000
                    
                    result = SyncResult(
                        plugin_id=plugin_id,
                        status=SyncStatus.SKIPPED,
                        records_synced=0,
                        error_message=None,
                        duration_ms=int(duration),
                        timestamp=datetime.now()
                    )
                    
                    self._add_to_history(result)
                    return result
                
                self._insert_to_central(central_db, plugin_id, new_records)
                
                central_db.commit()
                
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                self.stats["total_syncs"] += 1
                self.stats["total_success"] += 1
                self.stats["total_records_synced"] += len(new_records)
                
                self.last_sync_time[plugin_id] = datetime.now()
                
                logger.info(
                    f"Synced {len(new_records)} records for {plugin_id} "
                    f"in {int(duration)}ms"
                )
                
                result = SyncResult(
                    plugin_id=plugin_id,
                    status=SyncStatus.SUCCESS,
                    records_synced=len(new_records),
                    error_message=None,
                    duration_ms=int(duration),
                    timestamp=datetime.now()
                )
                
                self._add_to_history(result)
                
                return result
                
            finally:
                plugin_db.close()
                central_db.close()
                
        except Exception as e:
            self.stats["total_syncs"] += 1
            self.stats["total_failures"] += 1
            raise
    
    def _create_central_db(self):
        """Create central database with aggregated_trades table."""
        import os
        os.makedirs(os.path.dirname(self.central_db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.central_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aggregated_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT NOT NULL,
                plugin_type TEXT NOT NULL,
                source_trade_id INTEGER,
                mt5_ticket INTEGER,
                symbol TEXT,
                direction TEXT,
                lot_size REAL,
                entry_time TIMESTAMP,
                exit_time TIMESTAMP,
                profit_dollars REAL,
                status TEXT,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agg_plugin_id 
            ON aggregated_trades(plugin_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agg_entry_time 
            ON aggregated_trades(entry_time)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_status (
                plugin_id TEXT PRIMARY KEY,
                last_synced_id INTEGER DEFAULT 0,
                last_sync_time TIMESTAMP,
                sync_count INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created central database: {self.central_db_path}")
    
    def _get_last_synced_id(self, central_db, plugin_id: str) -> int:
        """Get the last synced record ID for this plugin."""
        cursor = central_db.execute("""
            SELECT COALESCE(last_synced_id, 0) as last_id
            FROM sync_status
            WHERE plugin_id = ?
        """, (plugin_id,))
        
        row = cursor.fetchone()
        return row[0] if row else 0
    
    def _fetch_new_records(
        self,
        plugin_db,
        plugin_id: str,
        last_synced_id: int
    ) -> List[Dict]:
        """Fetch new records from plugin database."""
        table_name = self._table_mapping.get(plugin_id, "trades")
        
        try:
            cursor = plugin_db.execute(f"""
                SELECT 
                    id,
                    mt5_ticket,
                    symbol,
                    direction,
                    lot_size,
                    entry_time,
                    exit_time,
                    profit_dollars,
                    status
                FROM {table_name}
                WHERE id > ?
                ORDER BY id
                LIMIT 1000
            """, (last_synced_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.OperationalError as e:
            logger.warning(f"Table {table_name} query failed for {plugin_id}: {e}")
            return []
    
    def _insert_to_central(
        self,
        central_db,
        plugin_id: str,
        records: List[Dict]
    ):
        """Insert records into central aggregated_trades table."""
        plugin_type = "V3_COMBINED" if plugin_id == "combined_v3" else "V6_PRICE_ACTION"
        
        max_id = 0
        
        for record in records:
            central_db.execute("""
                INSERT INTO aggregated_trades
                (plugin_id, plugin_type, source_trade_id, mt5_ticket, symbol, 
                 direction, lot_size, entry_time, exit_time, profit_dollars, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plugin_id,
                plugin_type,
                record.get("id"),
                record.get("mt5_ticket"),
                record.get("symbol"),
                record.get("direction"),
                record.get("lot_size"),
                record.get("entry_time"),
                record.get("exit_time"),
                record.get("profit_dollars"),
                record.get("status")
            ))
            
            if record.get("id", 0) > max_id:
                max_id = record["id"]
        
        central_db.execute("""
            INSERT OR REPLACE INTO sync_status 
            (plugin_id, last_synced_id, last_sync_time, sync_count)
            VALUES (?, ?, ?, COALESCE(
                (SELECT sync_count FROM sync_status WHERE plugin_id = ?), 0
            ) + 1)
        """, (plugin_id, max_id, datetime.now().isoformat(), plugin_id))
    
    def _add_to_history(self, result: SyncResult):
        """Add result to history (keep last N)."""
        self.sync_history.append(result)
        
        if len(self.sync_history) > self.config.max_history:
            self.sync_history = self.sync_history[-self.config.max_history:]
    
    async def _check_and_alert_failures(self):
        """Check for persistent failures and alert."""
        for plugin_id, failure_count in self.consecutive_failures.items():
            if failure_count >= self.config.alert_threshold:
                await self._send_sync_alert(plugin_id, failure_count)
    
    async def _send_sync_alert(self, plugin_id: str, failure_count: int):
        """Send alert about sync failures."""
        if self._alert_callback:
            try:
                await self._alert_callback(plugin_id, failure_count)
            except Exception as e:
                logger.error(f"Failed to send sync alert: {e}")
        
        logger.error(
            f"ALERT: {plugin_id} has {failure_count} consecutive sync failures"
        )
    
    def set_alert_callback(self, callback: callable):
        """
        Set callback for sync failure alerts.
        
        Args:
            callback: Async function(plugin_id, failure_count)
        """
        self._alert_callback = callback
    
    async def trigger_manual_sync(self) -> Dict[str, Any]:
        """
        Trigger immediate sync (bypasses interval wait).
        Used via /sync_manual command.
        
        Returns:
            Summary of sync results
        """
        logger.info("Manual sync triggered by admin")
        
        self._manual_sync_event.set()
        
        await asyncio.sleep(2)
        
        return {
            "triggered": True,
            "message": "Manual sync initiated. Check /sync_status for results.",
            "recent_results": [
                {
                    "plugin": r.plugin_id,
                    "status": r.status.value,
                    "records": r.records_synced
                }
                for r in self.sync_history[-5:]
            ]
        }
    
    def get_sync_health(self) -> Dict[str, Any]:
        """
        Get complete sync health status.
        
        Returns:
            Health status dictionary
        """
        now = datetime.now()
        
        health = {
            "overall_status": "HEALTHY",
            "plugins": {},
            "statistics": self.stats.copy(),
            "last_run": None,
            "is_running": self._running
        }
        
        for plugin_id in self._plugin_db_mapping.keys():
            last_sync = self.last_sync_time.get(plugin_id)
            failures = self.consecutive_failures.get(plugin_id, 0)
            
            if failures >= self.config.alert_threshold:
                status = "DEGRADED"
                health["overall_status"] = "DEGRADED"
            elif failures > 0:
                status = "WARNING"
                if health["overall_status"] == "HEALTHY":
                    health["overall_status"] = "WARNING"
            else:
                status = "HEALTHY"
            
            if last_sync:
                minutes_since = (now - last_sync).total_seconds() / 60
                last_sync_str = last_sync.strftime("%Y-%m-%d %H:%M:%S")
            else:
                minutes_since = 999
                last_sync_str = "Never"
            
            health["plugins"][plugin_id] = {
                "status": status,
                "last_sync": last_sync_str,
                "minutes_since_last_sync": int(minutes_since),
                "consecutive_failures": failures
            }
        
        if self.sync_history:
            health["last_run"] = self.sync_history[-1].timestamp.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        
        return health
    
    def get_sync_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent sync history.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of sync result dictionaries
        """
        return [
            {
                "plugin_id": r.plugin_id,
                "status": r.status.value,
                "records_synced": r.records_synced,
                "error_message": r.error_message,
                "duration_ms": r.duration_ms,
                "timestamp": r.timestamp.isoformat(),
                "retry_count": r.retry_count
            }
            for r in self.sync_history[-limit:]
        ]
    
    def reset_failure_count(self, plugin_id: str):
        """
        Reset consecutive failure count for a plugin.
        
        Args:
            plugin_id: Plugin identifier
        """
        if plugin_id in self.consecutive_failures:
            self.consecutive_failures[plugin_id] = 0
            logger.info(f"Reset failure count for {plugin_id}")


def create_sync_manager(
    v3_db_path: str = "data/zepix_combined_v3.db",
    v6_db_path: str = "data/zepix_price_action.db",
    central_db_path: str = "data/zepix_central.db"
) -> DatabaseSyncManager:
    """
    Factory function to create DatabaseSyncManager instance.
    
    Args:
        v3_db_path: Path to V3 plugin database
        v6_db_path: Path to V6 plugin database
        central_db_path: Path to central database
        
    Returns:
        DatabaseSyncManager instance
    """
    return DatabaseSyncManager(
        v3_db_path=v3_db_path,
        v6_db_path=v6_db_path,
        central_db_path=central_db_path
    )
