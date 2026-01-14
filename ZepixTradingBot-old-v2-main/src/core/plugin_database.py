"""
Plugin Database - Isolated SQLite Database for Each Plugin

Part of V5 Hybrid Plugin Architecture - Batch 09
Provides isolated database access for each plugin with connection pooling.

Features:
- Per-plugin database isolation (V3 and V6 cannot access each other's data)
- Thread-safe connection pooling
- Automatic schema creation
- Transaction support
- Query logging and statistics

Version: 1.0.0
"""

import sqlite3
import os
import json
import threading
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager
from queue import Queue, Empty

logger = logging.getLogger(__name__)


@dataclass
class DatabaseStats:
    """Statistics for database operations"""
    total_queries: int = 0
    total_inserts: int = 0
    total_updates: int = 0
    total_selects: int = 0
    total_errors: int = 0
    last_query_time: Optional[datetime] = None
    connection_count: int = 0


class PluginDatabaseError(Exception):
    """Base exception for plugin database errors"""
    pass


class ConnectionPoolExhausted(PluginDatabaseError):
    """Raised when connection pool is exhausted"""
    pass


class PluginDatabase:
    """
    Manages isolated database for each plugin.
    
    Features:
    - Isolated database per plugin
    - Connection pooling for thread safety
    - Automatic schema creation
    - Transaction support
    """
    
    def __init__(
        self,
        plugin_id: str,
        db_dir: str = "data",
        pool_size: int = 5,
        timeout: float = 30.0
    ):
        self.plugin_id = plugin_id
        self.db_dir = db_dir
        self.pool_size = pool_size
        self.timeout = timeout
        
        self.db_path = os.path.join(db_dir, f"zepix_{plugin_id}.db")
        
        self._pool: Queue = Queue(maxsize=pool_size)
        self._pool_lock = threading.Lock()
        self._local = threading.local()
        
        self.stats = DatabaseStats()
        self._stats_lock = threading.Lock()
        
        self._initialize()
    
    def _initialize(self):
        """Initialize database and connection pool."""
        os.makedirs(self.db_dir, exist_ok=True)
        
        is_new_db = not os.path.exists(self.db_path)
        
        for _ in range(self.pool_size):
            conn = self._create_connection()
            self._pool.put(conn)
        
        if is_new_db:
            logger.info(f"Creating new database for plugin: {self.plugin_id}")
            self._create_schema()
        else:
            logger.info(f"Connected to existing database for plugin: {self.plugin_id}")
        
        with self._stats_lock:
            self.stats.connection_count = self.pool_size
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        
        return conn
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM trades")
        """
        conn = None
        try:
            conn = self._pool.get(timeout=self.timeout)
            yield conn
        except Empty:
            raise ConnectionPoolExhausted(
                f"Connection pool exhausted for plugin {self.plugin_id}"
            )
        finally:
            if conn:
                self._pool.put(conn)
    
    @contextmanager
    def transaction(self):
        """
        Execute operations within a transaction.
        
        Usage:
            with db.transaction() as conn:
                conn.execute("INSERT INTO trades ...")
                conn.execute("UPDATE stats ...")
        """
        with self.get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
    
    def _create_schema(self):
        """Create plugin database schema."""
        with self.get_connection() as conn:
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
                    order_type TEXT CHECK(order_type IN ('ORDER_A', 'ORDER_B')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_received ON signals_log(received_at)")
            
            cursor.execute("""
                INSERT OR IGNORE INTO plugin_info (plugin_id, version, last_started)
                VALUES (?, '1.0.0', ?)
            """, (self.plugin_id, datetime.now().isoformat()))
            
            conn.commit()
            logger.info(f"Schema created for plugin: {self.plugin_id}")
    
    def save_trade(self, trade_data: Dict[str, Any]) -> int:
        """
        Save trade to plugin database.
        
        Args:
            trade_data: Dictionary containing trade information
            
        Returns:
            Trade ID
        """
        with self._stats_lock:
            self.stats.total_inserts += 1
            self.stats.total_queries += 1
            self.stats.last_query_time = datetime.now()
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO trades 
                (mt5_ticket, symbol, direction, lot_size, entry_price, sl_price, tp_price,
                 signal_type, signal_data, logic_type, order_type, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade_data.get("ticket") or trade_data.get("mt5_ticket"),
                trade_data["symbol"],
                trade_data["direction"],
                trade_data["lot_size"],
                trade_data["entry_price"],
                trade_data.get("sl_price"),
                trade_data.get("tp_price"),
                trade_data.get("signal_type"),
                json.dumps(trade_data.get("signal_data", {})),
                trade_data.get("logic_type"),
                trade_data.get("order_type"),
                trade_data.get("status", "OPEN")
            ))
            
            trade_id = cursor.lastrowid
            logger.debug(f"Trade saved: {trade_id} for plugin {self.plugin_id}")
            return trade_id
    
    def update_trade(self, trade_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update existing trade.
        
        Args:
            trade_id: Trade ID to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful
        """
        with self._stats_lock:
            self.stats.total_updates += 1
            self.stats.total_queries += 1
            self.stats.last_query_time = datetime.now()
        
        allowed_fields = [
            "exit_time", "exit_price", "profit_pips", "profit_dollars",
            "status", "close_reason", "sl_price", "tp_price"
        ]
        
        fields_to_update = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not fields_to_update:
            return False
        
        fields_to_update["updated_at"] = datetime.now().isoformat()
        
        set_clause = ", ".join(f"{k} = ?" for k in fields_to_update.keys())
        values = list(fields_to_update.values()) + [trade_id]
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE trades SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def close_trade(
        self,
        trade_id: int,
        exit_price: float,
        profit_dollars: float,
        close_reason: str
    ) -> bool:
        """
        Close a trade.
        
        Args:
            trade_id: Trade ID to close
            exit_price: Exit price
            profit_dollars: Profit in dollars
            close_reason: Reason for closing
            
        Returns:
            True if successful
        """
        return self.update_trade(trade_id, {
            "exit_time": datetime.now().isoformat(),
            "exit_price": exit_price,
            "profit_dollars": profit_dollars,
            "status": "CLOSED",
            "close_reason": close_reason
        })
    
    def get_trade(self, trade_id: int) -> Optional[Dict[str, Any]]:
        """
        Get trade by ID.
        
        Args:
            trade_id: Trade ID
            
        Returns:
            Trade dictionary or None
        """
        with self._stats_lock:
            self.stats.total_selects += 1
            self.stats.total_queries += 1
            self.stats.last_query_time = datetime.now()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades WHERE id = ?", (trade_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_trade_by_ticket(self, mt5_ticket: int) -> Optional[Dict[str, Any]]:
        """
        Get trade by MT5 ticket.
        
        Args:
            mt5_ticket: MT5 ticket number
            
        Returns:
            Trade dictionary or None
        """
        with self._stats_lock:
            self.stats.total_selects += 1
            self.stats.total_queries += 1
            self.stats.last_query_time = datetime.now()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades WHERE mt5_ticket = ?", (mt5_ticket,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_open_trades(self) -> List[Dict[str, Any]]:
        """
        Get all open trades for this plugin.
        
        Returns:
            List of trade dictionaries
        """
        with self._stats_lock:
            self.stats.total_selects += 1
            self.stats.total_queries += 1
            self.stats.last_query_time = datetime.now()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM trades WHERE status = 'OPEN' ORDER BY entry_time DESC"
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_trades_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        Get trades for a specific date.
        
        Args:
            date: Date string (YYYY-MM-DD)
            
        Returns:
            List of trade dictionaries
        """
        with self._stats_lock:
            self.stats.total_selects += 1
            self.stats.total_queries += 1
            self.stats.last_query_time = datetime.now()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM trades WHERE DATE(entry_time) = ? ORDER BY entry_time DESC",
                (date,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_trades(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all trades (limited).
        
        Args:
            limit: Maximum number of trades to return
            
        Returns:
            List of trade dictionaries
        """
        with self._stats_lock:
            self.stats.total_selects += 1
            self.stats.total_queries += 1
            self.stats.last_query_time = datetime.now()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM trades ORDER BY entry_time DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def log_signal(self, signal_data: Dict[str, Any]) -> int:
        """
        Log received signal.
        
        Args:
            signal_data: Signal information
            
        Returns:
            Signal log ID
        """
        with self._stats_lock:
            self.stats.total_inserts += 1
            self.stats.total_queries += 1
            self.stats.last_query_time = datetime.now()
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO signals_log 
                (signal_type, symbol, direction, timeframe, raw_payload, processed, result)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                signal_data.get("signal_type"),
                signal_data.get("symbol"),
                signal_data.get("direction"),
                signal_data.get("timeframe"),
                json.dumps(signal_data.get("raw_payload", {})),
                signal_data.get("processed", False),
                signal_data.get("result")
            ))
            return cursor.lastrowid
    
    def update_daily_stats(self, date: str, stats: Dict[str, Any]):
        """
        Update daily statistics.
        
        Args:
            date: Date string (YYYY-MM-DD)
            stats: Statistics to update
        """
        with self._stats_lock:
            self.stats.total_queries += 1
            self.stats.last_query_time = datetime.now()
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM daily_stats WHERE date = ?", (date,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE daily_stats SET
                        total_trades = total_trades + ?,
                        winning_trades = winning_trades + ?,
                        losing_trades = losing_trades + ?,
                        total_profit_pips = total_profit_pips + ?,
                        total_profit_dollars = total_profit_dollars + ?,
                        updated_at = ?
                    WHERE date = ?
                """, (
                    stats.get("trades", 0),
                    stats.get("wins", 0),
                    stats.get("losses", 0),
                    stats.get("profit_pips", 0),
                    stats.get("profit_dollars", 0),
                    datetime.now().isoformat(),
                    date
                ))
            else:
                cursor.execute("""
                    INSERT INTO daily_stats 
                    (date, total_trades, winning_trades, losing_trades, 
                     total_profit_pips, total_profit_dollars)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    date,
                    stats.get("trades", 0),
                    stats.get("wins", 0),
                    stats.get("losses", 0),
                    stats.get("profit_pips", 0),
                    stats.get("profit_dollars", 0)
                ))
    
    def get_daily_stats(self, date: str) -> Optional[Dict[str, Any]]:
        """
        Get daily statistics.
        
        Args:
            date: Date string (YYYY-MM-DD)
            
        Returns:
            Statistics dictionary or None
        """
        with self._stats_lock:
            self.stats.total_selects += 1
            self.stats.total_queries += 1
            self.stats.last_query_time = datetime.now()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM daily_stats WHERE date = ?", (date,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute arbitrary SELECT query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        with self._stats_lock:
            self.stats.total_selects += 1
            self.stats.total_queries += 1
            self.stats.last_query_time = datetime.now()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._stats_lock:
            return {
                "plugin_id": self.plugin_id,
                "db_path": self.db_path,
                "pool_size": self.pool_size,
                "total_queries": self.stats.total_queries,
                "total_inserts": self.stats.total_inserts,
                "total_updates": self.stats.total_updates,
                "total_selects": self.stats.total_selects,
                "total_errors": self.stats.total_errors,
                "last_query_time": self.stats.last_query_time.isoformat() if self.stats.last_query_time else None,
                "connection_count": self.stats.connection_count
            }
    
    def close(self):
        """Close all connections in the pool."""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except Empty:
                break
        
        logger.info(f"Database closed for plugin: {self.plugin_id}")
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection is working
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


class PluginDatabaseManager:
    """
    Manages multiple plugin databases.
    
    Ensures each plugin has its own isolated database.
    """
    
    def __init__(self, db_dir: str = "data"):
        self.db_dir = db_dir
        self._databases: Dict[str, PluginDatabase] = {}
        self._lock = threading.Lock()
    
    def get_database(self, plugin_id: str) -> PluginDatabase:
        """
        Get or create database for plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            PluginDatabase instance
        """
        with self._lock:
            if plugin_id not in self._databases:
                self._databases[plugin_id] = PluginDatabase(
                    plugin_id=plugin_id,
                    db_dir=self.db_dir
                )
                logger.info(f"Created database for plugin: {plugin_id}")
            
            return self._databases[plugin_id]
    
    def close_all(self):
        """Close all plugin databases."""
        with self._lock:
            for plugin_id, db in self._databases.items():
                db.close()
            self._databases.clear()
            logger.info("All plugin databases closed")
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all databases.
        
        Returns:
            Dictionary of plugin_id -> stats
        """
        with self._lock:
            return {
                plugin_id: db.get_stats()
                for plugin_id, db in self._databases.items()
            }


def create_plugin_database(plugin_id: str, db_dir: str = "data") -> PluginDatabase:
    """
    Factory function to create PluginDatabase instance.
    
    Args:
        plugin_id: Plugin identifier
        db_dir: Database directory
        
    Returns:
        PluginDatabase instance
    """
    return PluginDatabase(plugin_id=plugin_id, db_dir=db_dir)
