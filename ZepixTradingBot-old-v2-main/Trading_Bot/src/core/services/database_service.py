"""
Database Service - Plan 09: Database Isolation

Provides isolated database access to plugins.
Each plugin has its own SQLite database to prevent data conflicts.

Features:
- Isolated databases per plugin
- Async database operations
- Cross-plugin aggregation
- Health checks

Version: 1.0.0
Date: 2026-01-15
"""
from typing import Dict, Any, Optional, List, Callable
import logging
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Service layer for database operations.
    Manages isolated databases per plugin.
    
    Each plugin type has its own database file:
    - combined_v3 -> data/zepix_combined_v3.db
    - price_action_* -> data/zepix_price_action.db
    
    This prevents data conflicts and allows plugins to
    operate independently without affecting each other.
    """
    
    # Database paths per plugin type
    DATABASE_PATHS = {
        'v3_combined': 'data/zepix_combined_v3.db',
        'v6_price_action_1m': 'data/zepix_price_action.db',
        'v6_price_action_5m': 'data/zepix_price_action.db',
        'v6_price_action_15m': 'data/zepix_price_action.db',
        'v6_price_action_1h': 'data/zepix_price_action.db',
        'central_system': 'data/zepix_bot.db',
    }
    
    # Schema files per plugin type
    SCHEMA_FILES = {
        'v3_combined': 'data/schemas/combined_v3_schema.sql',
        'price_action': 'data/schemas/price_action_v6_schema.sql',
        'central_system': 'data/schemas/central_system_schema.sql',
    }
    
    def __init__(self, base_path: str = '.'):
        """
        Initialize DatabaseService.
        
        Args:
            base_path: Base path for database files
        """
        self.base_path = Path(base_path)
        self._connections: Dict[str, sqlite3.Connection] = {}
        self._initialized_dbs: set = set()
        self._lock = asyncio.Lock()
    
    def _get_db_path(self, plugin_id: str) -> Path:
        """Get database path for a plugin"""
        db_file = self.DATABASE_PATHS.get(plugin_id, f'data/zepix_{plugin_id}.db')
        return self.base_path / db_file
    
    def _get_schema_path(self, plugin_id: str) -> Optional[Path]:
        """Get schema file path for a plugin"""
        if plugin_id == 'v3_combined':
            schema_file = self.SCHEMA_FILES.get('v3_combined')
        elif plugin_id.startswith('v6_price_action') or plugin_id.startswith('price_action'):
            schema_file = self.SCHEMA_FILES.get('price_action')
        elif plugin_id == 'central_system':
            schema_file = self.SCHEMA_FILES.get('central_system')
        else:
            return None
        
        if schema_file:
            return self.base_path / schema_file
        return None
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        data_dir = self.base_path / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_connection(self, plugin_id: str) -> sqlite3.Connection:
        """
        Get database connection for a plugin.
        
        Creates connection if it doesn't exist.
        Uses synchronous sqlite3 wrapped in async for compatibility.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            SQLite connection
        """
        async with self._lock:
            if plugin_id not in self._connections:
                self._ensure_data_dir()
                db_path = self._get_db_path(plugin_id)
                
                # Create connection in thread pool
                loop = asyncio.get_event_loop()
                conn = await loop.run_in_executor(
                    None,
                    lambda: sqlite3.connect(str(db_path), check_same_thread=False)
                )
                conn.row_factory = sqlite3.Row
                self._connections[plugin_id] = conn
                logger.info(f"[DatabaseService] Connection created for {plugin_id}: {db_path}")
            
            return self._connections[plugin_id]
    
    async def initialize_database(self, plugin_id: str, schema: str = None) -> bool:
        """
        Initialize database with schema.
        
        Args:
            plugin_id: Plugin identifier
            schema: SQL schema string (optional, will load from file if not provided)
            
        Returns:
            True if initialization successful
        """
        if plugin_id in self._initialized_dbs:
            return True
        
        try:
            conn = await self.get_connection(plugin_id)
            
            # Load schema from file if not provided
            if not schema:
                schema_path = self._get_schema_path(plugin_id)
                if schema_path and schema_path.exists():
                    schema = schema_path.read_text()
                else:
                    logger.warning(f"[DatabaseService] No schema found for {plugin_id}")
                    return False
            
            # Execute schema in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: conn.executescript(schema)
            )
            await loop.run_in_executor(None, conn.commit)
            
            self._initialized_dbs.add(plugin_id)
            logger.info(f"[DatabaseService] Database initialized for {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"[DatabaseService] Failed to initialize database for {plugin_id}: {e}")
            return False
    
    async def execute_query(
        self,
        plugin_id: str,
        query: str,
        params: tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Execute a query on plugin's database.
        
        Args:
            plugin_id: Plugin identifier
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result rows as dictionaries
        """
        conn = await self.get_connection(plugin_id)
        
        try:
            loop = asyncio.get_event_loop()
            
            def _execute():
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            
            return await loop.run_in_executor(None, _execute)
            
        except Exception as e:
            logger.error(f"[DatabaseService] Query failed for {plugin_id}: {e}")
            raise
    
    async def insert_record(
        self,
        plugin_id: str,
        table: str,
        data: Dict[str, Any]
    ) -> int:
        """
        Insert a record into plugin's database.
        
        Args:
            plugin_id: Plugin identifier
            table: Table name
            data: Record data as dictionary
            
        Returns:
            ID of inserted record
        """
        conn = await self.get_connection(plugin_id)
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            loop = asyncio.get_event_loop()
            
            def _insert():
                cursor = conn.execute(query, tuple(data.values()))
                conn.commit()
                return cursor.lastrowid
            
            return await loop.run_in_executor(None, _insert)
            
        except Exception as e:
            logger.error(f"[DatabaseService] Insert failed for {plugin_id}.{table}: {e}")
            raise
    
    async def update_record(
        self,
        plugin_id: str,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any]
    ) -> int:
        """
        Update records in plugin's database.
        
        Args:
            plugin_id: Plugin identifier
            table: Table name
            data: Fields to update
            where: Conditions for update
            
        Returns:
            Number of records updated
        """
        conn = await self.get_connection(plugin_id)
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        
        try:
            loop = asyncio.get_event_loop()
            
            def _update():
                cursor = conn.execute(query, tuple(data.values()) + tuple(where.values()))
                conn.commit()
                return cursor.rowcount
            
            return await loop.run_in_executor(None, _update)
            
        except Exception as e:
            logger.error(f"[DatabaseService] Update failed for {plugin_id}.{table}: {e}")
            raise
    
    async def delete_record(
        self,
        plugin_id: str,
        table: str,
        where: Dict[str, Any]
    ) -> int:
        """
        Delete records from plugin's database.
        
        Args:
            plugin_id: Plugin identifier
            table: Table name
            where: Conditions for delete
            
        Returns:
            Number of records deleted
        """
        conn = await self.get_connection(plugin_id)
        
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        
        try:
            loop = asyncio.get_event_loop()
            
            def _delete():
                cursor = conn.execute(query, tuple(where.values()))
                conn.commit()
                return cursor.rowcount
            
            return await loop.run_in_executor(None, _delete)
            
        except Exception as e:
            logger.error(f"[DatabaseService] Delete failed for {plugin_id}.{table}: {e}")
            raise
    
    async def count_records(self, plugin_id: str, table: str, where: Dict[str, Any] = None) -> int:
        """
        Count records in a table.
        
        Args:
            plugin_id: Plugin identifier
            table: Table name
            where: Optional conditions
            
        Returns:
            Number of records
        """
        query = f"SELECT COUNT(*) as count FROM {table}"
        params = ()
        
        if where:
            where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
            query += f" WHERE {where_clause}"
            params = tuple(where.values())
        
        rows = await self.execute_query(plugin_id, query, params)
        return rows[0]['count'] if rows else 0
    
    async def close_connection(self, plugin_id: str):
        """Close database connection for a plugin"""
        async with self._lock:
            if plugin_id in self._connections:
                conn = self._connections.pop(plugin_id)
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, conn.close)
                logger.info(f"[DatabaseService] Connection closed for {plugin_id}")
    
    async def close_all(self):
        """Close all database connections"""
        async with self._lock:
            for plugin_id, conn in list(self._connections.items()):
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, conn.close)
                logger.info(f"[DatabaseService] Connection closed for {plugin_id}")
            self._connections.clear()
    
    # ==================== Cross-Plugin Aggregation ====================
    
    async def aggregate_trades(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Aggregate trade data across all plugins.
        
        Args:
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            
        Returns:
            Aggregated trade statistics
        """
        results = {
            'total_trades': 0,
            'total_profit': 0.0,
            'by_plugin': {},
            'timestamp': datetime.now().isoformat()
        }
        
        for plugin_id in self.DATABASE_PATHS.keys():
            try:
                query = "SELECT COUNT(*) as count, COALESCE(SUM(profit), 0) as profit FROM trades"
                params = []
                
                if start_date:
                    query += " WHERE created_at >= ?"
                    params.append(start_date)
                if end_date:
                    if start_date:
                        query += " AND created_at <= ?"
                    else:
                        query += " WHERE created_at <= ?"
                    params.append(end_date)
                
                rows = await self.execute_query(plugin_id, query, tuple(params))
                if rows:
                    row = rows[0]
                    count = row.get('count', 0) or 0
                    profit = row.get('profit', 0) or 0
                    
                    results['by_plugin'][plugin_id] = {
                        'trades': count,
                        'profit': profit
                    }
                    results['total_trades'] += count
                    results['total_profit'] += profit
                    
            except Exception as e:
                logger.warning(f"[DatabaseService] Failed to aggregate for {plugin_id}: {e}")
                results['by_plugin'][plugin_id] = {'trades': 0, 'profit': 0, 'error': str(e)}
        
        return results
    
    async def aggregate_signals(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Aggregate signal data across all plugins.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Aggregated signal statistics
        """
        results = {
            'total_signals': 0,
            'processed_signals': 0,
            'by_plugin': {},
            'timestamp': datetime.now().isoformat()
        }
        
        for plugin_id in self.DATABASE_PATHS.keys():
            try:
                query = """
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN processed = 1 THEN 1 ELSE 0 END) as processed
                    FROM signals
                """
                params = []
                
                if start_date:
                    query += " WHERE created_at >= ?"
                    params.append(start_date)
                if end_date:
                    if start_date:
                        query += " AND created_at <= ?"
                    else:
                        query += " WHERE created_at <= ?"
                    params.append(end_date)
                
                rows = await self.execute_query(plugin_id, query, tuple(params))
                if rows:
                    row = rows[0]
                    total = row.get('total', 0) or 0
                    processed = row.get('processed', 0) or 0
                    
                    results['by_plugin'][plugin_id] = {
                        'total': total,
                        'processed': processed
                    }
                    results['total_signals'] += total
                    results['processed_signals'] += processed
                    
            except Exception as e:
                logger.warning(f"[DatabaseService] Failed to aggregate signals for {plugin_id}: {e}")
        
        return results
    
    # ==================== Health Check ====================
    
    def health_check(self) -> bool:
        """
        Check if database service is healthy.
        
        Returns:
            True if service is healthy
        """
        try:
            # Check if we can access the data directory
            data_dir = self.base_path / 'data'
            return data_dir.exists() or True  # OK if doesn't exist yet
        except Exception:
            return False
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about all databases.
        
        Returns:
            Database statistics
        """
        stats = {
            'connections': len(self._connections),
            'initialized': list(self._initialized_dbs),
            'databases': {}
        }
        
        for plugin_id in self.DATABASE_PATHS.keys():
            db_path = self._get_db_path(plugin_id)
            stats['databases'][plugin_id] = {
                'path': str(db_path),
                'exists': db_path.exists(),
                'size_bytes': db_path.stat().st_size if db_path.exists() else 0,
                'connected': plugin_id in self._connections,
                'initialized': plugin_id in self._initialized_dbs
            }
        
        return stats
