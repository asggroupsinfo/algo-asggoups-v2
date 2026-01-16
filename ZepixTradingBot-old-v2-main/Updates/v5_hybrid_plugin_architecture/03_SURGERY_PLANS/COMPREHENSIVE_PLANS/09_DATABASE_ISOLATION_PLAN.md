# PLAN 09: DATABASE ISOLATION

**Date:** 2026-01-15
**Priority:** P1 (High)
**Estimated Time:** 2-3 days
**Dependencies:** Plan 08 (Service API)

---

## 1. OBJECTIVE

Implement complete database isolation per plugin. Currently all plugins share the same database which causes data conflicts. After this plan:

1. **Separate Databases** - Each plugin has its own SQLite database
2. **Schema Isolation** - V3 schema separate from V6 schema
3. **Migration Support** - Migrate existing data to isolated databases
4. **Cross-Plugin Queries** - Aggregation queries across all plugins

**Current Problem (from Study Report 04, GAP-8):**
- All plugins share `zepix_trading.db`
- V3 and V6 data mixed in same tables
- No plugin-specific schemas
- Data conflicts possible

**Target State:**
- V3 plugin uses `zepix_combined_v3.db`
- V6 plugins use `zepix_price_action.db`
- Each plugin has isolated tables
- Cross-plugin aggregation supported

---

## 2. SCOPE

### In-Scope:
- Create isolated databases per plugin type
- Implement plugin-specific schemas
- Create database service for plugins
- Implement data migration from shared DB
- Implement cross-plugin aggregation

### Out-of-Scope:
- Changing database engine (staying with SQLite)
- Cloud database migration
- Real-time replication

---

## 3. CURRENT STATE ANALYSIS

### Current Database Structure:

**File:** `data/zepix_trading.db` (shared)

**Tables (mixed V3 and V6 data):**
```sql
-- Trades table (mixed)
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    strategy TEXT,  -- 'V3_COMBINED' or 'V6_PRICE_ACTION'
    symbol TEXT,
    direction TEXT,
    entry_price REAL,
    exit_price REAL,
    profit REAL,
    created_at TIMESTAMP
);

-- Signals table (mixed)
CREATE TABLE signals (
    id INTEGER PRIMARY KEY,
    strategy TEXT,
    signal_type TEXT,
    symbol TEXT,
    processed BOOLEAN,
    created_at TIMESTAMP
);
```

### Target Database Structure:

**File:** `data/zepix_combined_v3.db` (V3 only)
**File:** `data/zepix_price_action.db` (V6 only)

---

## 4. GAPS ADDRESSED

| Gap | Description | How Addressed |
|-----|-------------|---------------|
| GAP-8 | Database Isolation | Separate databases per plugin |
| REQ-4.1 | Plugin-Specific Schemas | Isolated schemas |
| REQ-4.2 | Data Migration | Migration tool |
| REQ-4.3 | Cross-Plugin Queries | Aggregation service |

---

## 5. IMPLEMENTATION STEPS

### Step 1: Create Database Service Interface

**File:** `src/core/plugin_system/database_interface.py` (NEW)

**Code:**
```python
"""
Database Interface for Plugins
Defines how plugins interact with their isolated databases
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Configuration for a plugin database"""
    plugin_id: str
    db_path: str
    schema_version: str
    tables: List[str]

class IDatabaseCapable(ABC):
    """Interface for plugins that use databases"""
    
    @abstractmethod
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration for this plugin"""
        pass
    
    @abstractmethod
    async def initialize_database(self) -> bool:
        """Initialize plugin's database with schema"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a query on plugin's database"""
        pass
    
    @abstractmethod
    async def insert_record(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a record into plugin's database"""
        pass
    
    @abstractmethod
    async def update_record(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update records in plugin's database"""
        pass
```

**Reason:** Defines clear contract for database operations.

---

### Step 2: Create Database Service

**File:** `src/core/services/database_service.py` (NEW)

**Code:**
```python
"""
Database Service
Provides isolated database access to plugins
"""
from typing import Dict, Any, Optional, List
import logging
import sqlite3
import aiosqlite
from pathlib import Path
from src.core.plugin_system.database_interface import DatabaseConfig

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service layer for database operations.
    Manages isolated databases per plugin.
    """
    
    # Database paths per plugin type
    DATABASE_PATHS = {
        'combined_v3': 'data/zepix_combined_v3.db',
        'price_action_1m': 'data/zepix_price_action.db',
        'price_action_5m': 'data/zepix_price_action.db',
        'price_action_15m': 'data/zepix_price_action.db',
        'price_action_1h': 'data/zepix_price_action.db',
    }
    
    def __init__(self, base_path: str = '.'):
        self.base_path = Path(base_path)
        self._connections: Dict[str, aiosqlite.Connection] = {}
        self._initialized_dbs: set = set()
    
    async def get_connection(self, plugin_id: str) -> aiosqlite.Connection:
        """Get database connection for a plugin"""
        db_path = self._get_db_path(plugin_id)
        
        if plugin_id not in self._connections:
            self._connections[plugin_id] = await aiosqlite.connect(db_path)
            self._connections[plugin_id].row_factory = aiosqlite.Row
        
        return self._connections[plugin_id]
    
    def _get_db_path(self, plugin_id: str) -> str:
        """Get database path for a plugin"""
        db_file = self.DATABASE_PATHS.get(plugin_id, f'data/zepix_{plugin_id}.db')
        return str(self.base_path / db_file)
    
    async def initialize_database(self, plugin_id: str, schema: str) -> bool:
        """Initialize database with schema"""
        if plugin_id in self._initialized_dbs:
            return True
        
        try:
            conn = await self.get_connection(plugin_id)
            await conn.executescript(schema)
            await conn.commit()
            self._initialized_dbs.add(plugin_id)
            logger.info(f"Database initialized for {plugin_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database for {plugin_id}: {e}")
            return False
    
    async def execute_query(
        self,
        plugin_id: str,
        query: str,
        params: tuple = ()
    ) -> List[Dict[str, Any]]:
        """Execute a query on plugin's database"""
        conn = await self.get_connection(plugin_id)
        
        try:
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Query failed for {plugin_id}: {e}")
            raise
    
    async def insert_record(
        self,
        plugin_id: str,
        table: str,
        data: Dict[str, Any]
    ) -> int:
        """Insert a record into plugin's database"""
        conn = await self.get_connection(plugin_id)
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            cursor = await conn.execute(query, tuple(data.values()))
            await conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Insert failed for {plugin_id}.{table}: {e}")
            raise
    
    async def update_record(
        self,
        plugin_id: str,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any]
    ) -> int:
        """Update records in plugin's database"""
        conn = await self.get_connection(plugin_id)
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        
        try:
            cursor = await conn.execute(query, tuple(data.values()) + tuple(where.values()))
            await conn.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Update failed for {plugin_id}.{table}: {e}")
            raise
    
    async def close_all(self):
        """Close all database connections"""
        for plugin_id, conn in self._connections.items():
            await conn.close()
            logger.info(f"Database connection closed for {plugin_id}")
        self._connections.clear()
    
    # ==================== Cross-Plugin Aggregation ====================
    
    async def aggregate_trades(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Aggregate trade data across all plugins"""
        results = {
            'total_trades': 0,
            'total_profit': 0.0,
            'by_plugin': {}
        }
        
        for plugin_id in self.DATABASE_PATHS.keys():
            try:
                query = "SELECT COUNT(*) as count, SUM(profit) as profit FROM trades"
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
                    results['by_plugin'][plugin_id] = {
                        'trades': row.get('count', 0) or 0,
                        'profit': row.get('profit', 0) or 0
                    }
                    results['total_trades'] += row.get('count', 0) or 0
                    results['total_profit'] += row.get('profit', 0) or 0
            except Exception as e:
                logger.warning(f"Failed to aggregate for {plugin_id}: {e}")
        
        return results
```

**Reason:** Provides isolated database access per plugin.

---

### Step 3: Create V3 Database Schema

**File:** `data/schemas/combined_v3_schema.sql`

**Code:**
```sql
-- Combined V3 Plugin Database Schema
-- Version: 1.0.0
-- Isolated database for V3 Combined Logic

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT UNIQUE NOT NULL,
    plugin_id TEXT DEFAULT 'combined_v3',
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    logic TEXT NOT NULL,  -- LOGIC1, LOGIC2, LOGIC3
    entry_price REAL NOT NULL,
    exit_price REAL,
    sl_price REAL,
    tp_price REAL,
    lot_size REAL NOT NULL,
    profit REAL DEFAULT 0,
    status TEXT DEFAULT 'open',  -- open, closed, cancelled
    close_reason TEXT,  -- SL_HIT, TP_HIT, MANUAL, REVERSAL
    order_a_id TEXT,
    order_b_id TEXT,
    chain_level INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    metadata TEXT  -- JSON for additional data
);

-- Signals table
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id TEXT UNIQUE NOT NULL,
    plugin_id TEXT DEFAULT 'combined_v3',
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL,  -- BUY, SELL
    logic TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    price REAL NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    result TEXT,  -- executed, rejected, expired
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Profit bookings table
CREATE TABLE IF NOT EXISTS profit_bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_id TEXT UNIQUE NOT NULL,
    trade_id TEXT NOT NULL,
    plugin_id TEXT DEFAULT 'combined_v3',
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    level INTEGER DEFAULT 0,
    orders_in_level INTEGER DEFAULT 1,
    orders_booked INTEGER DEFAULT 0,
    total_profit REAL DEFAULT 0,
    status TEXT DEFAULT 'active',  -- active, completed, sl_hunt, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
);

-- Recovery windows table
CREATE TABLE IF NOT EXISTS recovery_windows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recovery_id TEXT UNIQUE NOT NULL,
    trade_id TEXT NOT NULL,
    plugin_id TEXT DEFAULT 'combined_v3',
    symbol TEXT NOT NULL,
    recovery_type TEXT NOT NULL,  -- sl_hunt, tp_continuation, exit_continuation
    sl_price REAL,
    entry_price REAL,
    direction TEXT NOT NULL,
    window_minutes INTEGER NOT NULL,
    status TEXT DEFAULT 'monitoring',  -- monitoring, recovered, expired
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_created ON trades(created_at);
CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_processed ON signals(processed);
CREATE INDEX IF NOT EXISTS idx_profit_bookings_status ON profit_bookings(status);
CREATE INDEX IF NOT EXISTS idx_recovery_windows_status ON recovery_windows(status);
```

**Reason:** Isolated schema for V3 plugin.

---

### Step 4: Create V6 Database Schema

**File:** `data/schemas/price_action_v6_schema.sql`

**Code:**
```sql
-- Price Action V6 Plugin Database Schema
-- Version: 1.0.0
-- Isolated database for V6 Price Action plugins

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT UNIQUE NOT NULL,
    plugin_id TEXT NOT NULL,  -- price_action_1m, price_action_5m, etc.
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    timeframe TEXT NOT NULL,  -- 1m, 5m, 15m, 1h
    entry_price REAL NOT NULL,
    exit_price REAL,
    sl_price REAL,
    tp_price REAL,
    lot_size REAL NOT NULL,
    profit REAL DEFAULT 0,
    status TEXT DEFAULT 'open',
    close_reason TEXT,
    trend_pulse_state TEXT,  -- JSON for trend pulse data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    metadata TEXT
);

-- Signals table
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id TEXT UNIQUE NOT NULL,
    plugin_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    price REAL NOT NULL,
    trendline_break BOOLEAN DEFAULT FALSE,
    momentum_confirmed BOOLEAN DEFAULT FALSE,
    processed BOOLEAN DEFAULT FALSE,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Trend pulse states table
CREATE TABLE IF NOT EXISTS trend_pulse_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    trend_direction TEXT,  -- bullish, bearish, neutral
    momentum_score REAL,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timeframe)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_trades_plugin ON trades(plugin_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_timeframe ON trades(timeframe);
CREATE INDEX IF NOT EXISTS idx_signals_plugin ON signals(plugin_id);
CREATE INDEX IF NOT EXISTS idx_trend_pulse_symbol ON trend_pulse_states(symbol);
```

**Reason:** Isolated schema for V6 plugins.

---

### Step 5: Create Data Migration Tool

**File:** `src/utils/database_migration.py` (NEW)

**Code:**
```python
"""
Database Migration Tool
Migrates data from shared database to isolated plugin databases
"""
from typing import Dict, Any, List
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Migrates data from shared to isolated databases"""
    
    def __init__(self, base_path: str = '.'):
        self.base_path = Path(base_path)
        self.shared_db = self.base_path / 'data' / 'zepix_trading.db'
        self.v3_db = self.base_path / 'data' / 'zepix_combined_v3.db'
        self.v6_db = self.base_path / 'data' / 'zepix_price_action.db'
    
    def migrate_all(self, dry_run: bool = True) -> Dict[str, Any]:
        """Migrate all data from shared to isolated databases"""
        results = {
            'v3_trades': 0,
            'v3_signals': 0,
            'v6_trades': 0,
            'v6_signals': 0,
            'errors': []
        }
        
        if not self.shared_db.exists():
            logger.warning("Shared database not found, nothing to migrate")
            return results
        
        try:
            # Connect to shared database
            shared_conn = sqlite3.connect(self.shared_db)
            shared_conn.row_factory = sqlite3.Row
            
            # Migrate V3 data
            v3_results = self._migrate_v3_data(shared_conn, dry_run)
            results['v3_trades'] = v3_results.get('trades', 0)
            results['v3_signals'] = v3_results.get('signals', 0)
            
            # Migrate V6 data
            v6_results = self._migrate_v6_data(shared_conn, dry_run)
            results['v6_trades'] = v6_results.get('trades', 0)
            results['v6_signals'] = v6_results.get('signals', 0)
            
            shared_conn.close()
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _migrate_v3_data(self, shared_conn, dry_run: bool) -> Dict[str, int]:
        """Migrate V3 data to isolated database"""
        results = {'trades': 0, 'signals': 0}
        
        # Get V3 trades
        cursor = shared_conn.execute(
            "SELECT * FROM trades WHERE strategy = 'V3_COMBINED'"
        )
        v3_trades = cursor.fetchall()
        
        if dry_run:
            results['trades'] = len(v3_trades)
            logger.info(f"[DRY RUN] Would migrate {len(v3_trades)} V3 trades")
        else:
            # Actually migrate
            v3_conn = sqlite3.connect(self.v3_db)
            for trade in v3_trades:
                self._insert_trade(v3_conn, dict(trade))
                results['trades'] += 1
            v3_conn.commit()
            v3_conn.close()
            logger.info(f"Migrated {results['trades']} V3 trades")
        
        # Get V3 signals
        cursor = shared_conn.execute(
            "SELECT * FROM signals WHERE strategy = 'V3_COMBINED'"
        )
        v3_signals = cursor.fetchall()
        
        if dry_run:
            results['signals'] = len(v3_signals)
            logger.info(f"[DRY RUN] Would migrate {len(v3_signals)} V3 signals")
        else:
            v3_conn = sqlite3.connect(self.v3_db)
            for signal in v3_signals:
                self._insert_signal(v3_conn, dict(signal))
                results['signals'] += 1
            v3_conn.commit()
            v3_conn.close()
            logger.info(f"Migrated {results['signals']} V3 signals")
        
        return results
    
    def _migrate_v6_data(self, shared_conn, dry_run: bool) -> Dict[str, int]:
        """Migrate V6 data to isolated database"""
        results = {'trades': 0, 'signals': 0}
        
        # Get V6 trades
        cursor = shared_conn.execute(
            "SELECT * FROM trades WHERE strategy LIKE 'V6_%'"
        )
        v6_trades = cursor.fetchall()
        
        if dry_run:
            results['trades'] = len(v6_trades)
            logger.info(f"[DRY RUN] Would migrate {len(v6_trades)} V6 trades")
        else:
            v6_conn = sqlite3.connect(self.v6_db)
            for trade in v6_trades:
                self._insert_trade(v6_conn, dict(trade))
                results['trades'] += 1
            v6_conn.commit()
            v6_conn.close()
            logger.info(f"Migrated {results['trades']} V6 trades")
        
        return results
    
    def _insert_trade(self, conn, trade: Dict[str, Any]):
        """Insert a trade record"""
        # Map old schema to new schema
        # Implementation depends on actual schema differences
        pass
    
    def _insert_signal(self, conn, signal: Dict[str, Any]):
        """Insert a signal record"""
        pass
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify migration was successful"""
        results = {
            'shared_trades': 0,
            'v3_trades': 0,
            'v6_trades': 0,
            'match': False
        }
        
        # Count in shared
        if self.shared_db.exists():
            conn = sqlite3.connect(self.shared_db)
            cursor = conn.execute("SELECT COUNT(*) FROM trades")
            results['shared_trades'] = cursor.fetchone()[0]
            conn.close()
        
        # Count in V3
        if self.v3_db.exists():
            conn = sqlite3.connect(self.v3_db)
            cursor = conn.execute("SELECT COUNT(*) FROM trades")
            results['v3_trades'] = cursor.fetchone()[0]
            conn.close()
        
        # Count in V6
        if self.v6_db.exists():
            conn = sqlite3.connect(self.v6_db)
            cursor = conn.execute("SELECT COUNT(*) FROM trades")
            results['v6_trades'] = cursor.fetchone()[0]
            conn.close()
        
        # Verify counts match
        results['match'] = (
            results['shared_trades'] == 
            results['v3_trades'] + results['v6_trades']
        )
        
        return results
```

**Reason:** Migrates existing data to isolated databases.

---

### Step 6: Update Plugins to Use Database Service

**File:** `src/logic_plugins/combined_v3/plugin.py`

**Changes:**
```python
# ADD database methods

class CombinedV3Plugin(..., IDatabaseCapable):
    """V3 Plugin with database isolation"""
    
    # Database schema
    DATABASE_SCHEMA = """
    -- V3 schema (loaded from file)
    """
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration"""
        return DatabaseConfig(
            plugin_id=self.plugin_id,
            db_path='data/zepix_combined_v3.db',
            schema_version='1.0.0',
            tables=['trades', 'signals', 'profit_bookings', 'recovery_windows']
        )
    
    async def initialize_database(self) -> bool:
        """Initialize plugin's database"""
        if not self._service_api:
            return False
        
        db_service = self._service_api.database_service
        return await db_service.initialize_database(
            self.plugin_id,
            self.DATABASE_SCHEMA
        )
    
    async def save_trade(self, trade_data: Dict[str, Any]) -> int:
        """Save trade to plugin's database"""
        db_service = self._service_api.database_service
        return await db_service.insert_record(
            self.plugin_id,
            'trades',
            trade_data
        )
    
    async def get_trades(self, status: str = None) -> List[Dict]:
        """Get trades from plugin's database"""
        db_service = self._service_api.database_service
        
        query = "SELECT * FROM trades"
        params = ()
        
        if status:
            query += " WHERE status = ?"
            params = (status,)
        
        return await db_service.execute_query(self.plugin_id, query, params)
```

**Reason:** Plugin uses isolated database.

---

## 6. DEPENDENCIES

### Prerequisites:
- Plan 08 (Service API) - Database service registration

### Blocks:
- Plan 10 (Renaming) - Database paths may change
- Plan 12 (E2E Testing) - Needs isolated databases

---

## 7. FILES AFFECTED

| File | Action | Description |
|------|--------|-------------|
| `src/core/plugin_system/database_interface.py` | CREATE | Interface |
| `src/core/services/database_service.py` | CREATE | Service |
| `data/schemas/combined_v3_schema.sql` | CREATE | V3 schema |
| `data/schemas/price_action_v6_schema.sql` | CREATE | V6 schema |
| `src/utils/database_migration.py` | CREATE | Migration tool |
| `src/logic_plugins/combined_v3/plugin.py` | MODIFY | Add database methods |

---

## 8. SUCCESS CRITERIA

1. ✅ V3 plugin uses isolated database
2. ✅ V6 plugins use isolated database
3. ✅ Data migration works
4. ✅ Cross-plugin aggregation works
5. ✅ No data conflicts between plugins
6. ✅ All tests pass

---

## 11. REFERENCES

- **Study Report 04:** GAP-8, REQ-4.1-4.3
- **Code Evidence:** `data/zepix_trading.db`

---

**END OF PLAN 09**
