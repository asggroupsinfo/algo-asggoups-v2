# DATABASE MIGRATION PLAN - Plugin Isolation & Data Migration

**Objective:** Update database to support plugin isolation, add plugin_id tracking, and migrate existing data to new schema.

**Estimated Effort:** 3-4 hours

---

## PART 1: CURRENT DATABASE STATE

### 1.1 Current Database Files

| Database | Location | Purpose |
|----------|----------|---------|
| trading_bot.db | data/trading_bot.db | Main database (ALL data) |

### 1.2 Current Tables in trading_bot.db

| Table | Purpose | Plugin Isolation |
|-------|---------|------------------|
| trades | All trades | NO - no plugin_id column |
| reentry_chains | Re-entry chains | NO |
| sl_events | SL hunting events | NO |
| tp_reentry_events | TP re-entry events | NO |
| reversal_exit_events | Reversal exits | NO |
| system_state | System state | NO |
| profit_booking_chains | Profit chains | NO |
| profit_booking_orders | Profit orders | NO |
| profit_booking_events | Profit events | NO |
| trading_sessions | Trading sessions | NO |

### 1.3 Problem

All plugins share the same database and tables. There's no way to:
- Identify which plugin created a trade
- Calculate per-plugin performance
- Isolate plugin data

---

## PART 2: TARGET DATABASE STATE

### 2.1 New Database Structure

**Option A: Single Database with plugin_id Column (Recommended)**
```
data/trading_bot.db
├── trades (with plugin_id column)
├── reentry_chains (with plugin_id column)
├── ... (all tables with plugin_id)
```

**Option B: Separate Databases per Plugin**
```
data/
├── trading_bot.db (core/legacy)
├── zepix_v3_logic_combined.db
├── zepix_v6_logic_01_1min.db
├── zepix_v6_logic_02_5min.db
├── zepix_v6_logic_03_15min.db
├── zepix_v6_logic_04_1h.db
```

**Recommendation:** Option A (Single Database with plugin_id) for simplicity. Option B can be implemented later if needed.

### 2.2 Schema Changes

#### 2.2.1 Add plugin_id to trades Table

**Current Schema (database.py lines 15-51):**
```sql
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY,
    trade_id TEXT,
    symbol TEXT,
    entry_price REAL,
    exit_price REAL,
    sl_price REAL,
    tp_price REAL,
    lot_size REAL,
    direction TEXT,
    strategy TEXT,
    pnl REAL,
    commission REAL,
    swap REAL,
    comment TEXT,
    status TEXT,
    open_time DATETIME,
    close_time DATETIME,
    chain_id TEXT,
    chain_level INTEGER,
    is_re_entry BOOLEAN,
    order_type TEXT,
    profit_chain_id TEXT,
    profit_level INTEGER DEFAULT 0,
    session_id TEXT,
    sl_adjusted INTEGER DEFAULT 0,
    original_sl_distance REAL DEFAULT 0.0,
    logic_type TEXT,
    base_lot_size REAL DEFAULT 0.0,
    final_lot_size REAL DEFAULT 0.0,
    base_sl_pips REAL DEFAULT 0.0,
    final_sl_pips REAL DEFAULT 0.0,
    lot_multiplier REAL DEFAULT 1.0,
    sl_multiplier REAL DEFAULT 1.0
)
```

**New Schema:**
```sql
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY,
    trade_id TEXT,
    plugin_id TEXT DEFAULT 'legacy',  -- NEW COLUMN
    symbol TEXT,
    entry_price REAL,
    exit_price REAL,
    sl_price REAL,
    tp_price REAL,
    lot_size REAL,
    direction TEXT,
    strategy TEXT,
    pnl REAL,
    commission REAL,
    swap REAL,
    comment TEXT,
    status TEXT,
    open_time DATETIME,
    close_time DATETIME,
    chain_id TEXT,
    chain_level INTEGER,
    is_re_entry BOOLEAN,
    order_type TEXT,
    profit_chain_id TEXT,
    profit_level INTEGER DEFAULT 0,
    session_id TEXT,
    sl_adjusted INTEGER DEFAULT 0,
    original_sl_distance REAL DEFAULT 0.0,
    logic_type TEXT,
    base_lot_size REAL DEFAULT 0.0,
    final_lot_size REAL DEFAULT 0.0,
    base_sl_pips REAL DEFAULT 0.0,
    final_sl_pips REAL DEFAULT 0.0,
    lot_multiplier REAL DEFAULT 1.0,
    sl_multiplier REAL DEFAULT 1.0
)
```

#### 2.2.2 Add plugin_id to Other Tables

**reentry_chains:**
```sql
ALTER TABLE reentry_chains ADD COLUMN plugin_id TEXT DEFAULT 'legacy';
```

**profit_booking_chains:**
```sql
ALTER TABLE profit_booking_chains ADD COLUMN plugin_id TEXT DEFAULT 'legacy';
```

**trading_sessions:**
```sql
ALTER TABLE trading_sessions ADD COLUMN plugin_id TEXT DEFAULT 'legacy';
```

---

## PART 3: MIGRATION SCRIPT

### 3.1 Migration Script: add_plugin_id.py

**Create file:** `src/utils/migrations/add_plugin_id.py`

```python
"""
Migration: Add plugin_id column to all tables.

This migration adds plugin_id tracking to enable per-plugin performance analysis.

Run: python -m src.utils.migrations.add_plugin_id
"""

import sqlite3
from datetime import datetime
import os

DB_PATH = 'data/trading_bot.db'
BACKUP_PATH = f'data/backups/trading_bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

def backup_database():
    """Create backup before migration."""
    import shutil
    os.makedirs('data/backups', exist_ok=True)
    shutil.copy(DB_PATH, BACKUP_PATH)
    print(f"Backup created: {BACKUP_PATH}")

def add_plugin_id_column(cursor, table_name):
    """Add plugin_id column to a table if it doesn't exist."""
    # Check if column exists
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'plugin_id' not in columns:
        print(f"Adding plugin_id to {table_name}...")
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN plugin_id TEXT DEFAULT 'legacy'")
        return True
    else:
        print(f"plugin_id already exists in {table_name}")
        return False

def migrate_existing_data(cursor):
    """
    Migrate existing trades to appropriate plugin_id based on logic_type.
    
    Mapping:
    - combinedlogic-1 -> v3-logic-01-5min
    - combinedlogic-2 -> v3-logic-02-15min
    - combinedlogic-3 -> v3-logic-03-1h
    - NULL/empty -> legacy
    """
    print("Migrating existing trade data...")
    
    # Map old logic_type to new plugin_id
    mappings = [
        ("combinedlogic-1", "v3-logic-01-5min"),
        ("combinedlogic-2", "v3-logic-02-15min"),
        ("combinedlogic-3", "v3-logic-03-1h"),
        ("LOGIC1", "v3-logic-01-5min"),
        ("LOGIC2", "v3-logic-02-15min"),
        ("LOGIC3", "v3-logic-03-1h"),
    ]
    
    for old_value, new_plugin_id in mappings:
        cursor.execute("""
            UPDATE trades 
            SET plugin_id = ? 
            WHERE logic_type = ? AND (plugin_id IS NULL OR plugin_id = 'legacy')
        """, (new_plugin_id, old_value))
        updated = cursor.rowcount
        if updated > 0:
            print(f"  Updated {updated} trades: {old_value} -> {new_plugin_id}")

def create_indexes(cursor):
    """Create indexes for plugin_id queries."""
    print("Creating indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_trades_plugin_id ON trades(plugin_id)",
        "CREATE INDEX IF NOT EXISTS idx_trades_plugin_status ON trades(plugin_id, status)",
        "CREATE INDEX IF NOT EXISTS idx_reentry_chains_plugin_id ON reentry_chains(plugin_id)",
        "CREATE INDEX IF NOT EXISTS idx_profit_booking_chains_plugin_id ON profit_booking_chains(plugin_id)",
        "CREATE INDEX IF NOT EXISTS idx_trading_sessions_plugin_id ON trading_sessions(plugin_id)",
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
            print(f"  Created: {index_sql.split('idx_')[1].split(' ')[0]}")
        except sqlite3.OperationalError as e:
            print(f"  Skipped (already exists): {e}")

def run_migration():
    """Run the complete migration."""
    print("=" * 60)
    print("DATABASE MIGRATION: Add plugin_id Column")
    print("=" * 60)
    
    # Step 1: Backup
    backup_database()
    
    # Step 2: Connect
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Step 3: Add columns
        tables_to_update = [
            'trades',
            'reentry_chains',
            'profit_booking_chains',
            'trading_sessions',
        ]
        
        for table in tables_to_update:
            add_plugin_id_column(cursor, table)
        
        # Step 4: Migrate existing data
        migrate_existing_data(cursor)
        
        # Step 5: Create indexes
        create_indexes(cursor)
        
        # Step 6: Commit
        conn.commit()
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        conn.rollback()
        print(f"\nMIGRATION FAILED: {e}")
        print(f"Restore from backup: {BACKUP_PATH}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
```

---

## PART 4: UPDATE database.py

### 4.1 Update create_tables()

**File:** `src/database.py`

**Add after line 51 (in create_tables()):**

```python
# Add plugin_id column if it doesn't exist
try:
    cursor.execute('ALTER TABLE trades ADD COLUMN plugin_id TEXT DEFAULT "legacy"')
except sqlite3.OperationalError:
    pass  # Column already exists
```

### 4.2 Update save_trade()

**File:** `src/database.py` lines 229-277

**Current Code:**
```python
def save_trade(self, trade: Trade):
    try:
        cursor = self.conn.cursor()
        # ... existing code ...
        cursor.execute("""
            INSERT OR REPLACE INTO trades (
                trade_id, symbol, entry_price, ...
            ) VALUES (?, ?, ?, ...)
        """, (
            trade.trade_id, trade.symbol, trade.entry, ...
        ))
```

**New Code:**
```python
def save_trade(self, trade: Trade, plugin_id: str = "legacy"):
    try:
        cursor = self.conn.cursor()
        # ... existing code ...
        
        # Get plugin_id from trade or parameter
        trade_plugin_id = getattr(trade, 'plugin_id', None) or plugin_id
        
        cursor.execute("""
            INSERT OR REPLACE INTO trades (
                trade_id, plugin_id, symbol, entry_price, ...
            ) VALUES (?, ?, ?, ?, ...)
        """, (
            trade.trade_id, trade_plugin_id, trade.symbol, trade.entry, ...
        ))
```

### 4.3 Add New Query Methods

**Add to database.py:**

```python
def get_trades_by_plugin(self, plugin_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get trades for a specific plugin.
    
    Args:
        plugin_id: Plugin ID to filter by
        days: Number of days to look back
        
    Returns:
        List of trade dictionaries
    """
    cursor = self.conn.cursor()
    cursor.execute('''
        SELECT * FROM trades 
        WHERE plugin_id = ? AND close_time >= datetime('now', ?)
        ORDER BY close_time DESC
    ''', (plugin_id, f'-{days} days'))
    
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_plugin_statistics(self, plugin_id: str) -> Dict[str, Any]:
    """
    Get performance statistics for a specific plugin.
    
    Args:
        plugin_id: Plugin ID
        
    Returns:
        Dict with statistics
    """
    cursor = self.conn.cursor()
    cursor.execute('''
        SELECT 
            COUNT(*) as total_trades,
            COUNT(CASE WHEN pnl > 0 THEN 1 END) as winning_trades,
            COUNT(CASE WHEN pnl < 0 THEN 1 END) as losing_trades,
            SUM(pnl) as total_pnl,
            AVG(pnl) as avg_pnl,
            MAX(pnl) as best_trade,
            MIN(pnl) as worst_trade
        FROM trades
        WHERE plugin_id = ? AND status = 'closed'
    ''', (plugin_id,))
    
    result = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, result)) if result else {}

def get_all_plugin_statistics(self) -> Dict[str, Dict[str, Any]]:
    """
    Get performance statistics for all plugins.
    
    Returns:
        Dict with plugin_id as key and statistics as value
    """
    cursor = self.conn.cursor()
    cursor.execute('''
        SELECT 
            plugin_id,
            COUNT(*) as total_trades,
            COUNT(CASE WHEN pnl > 0 THEN 1 END) as winning_trades,
            SUM(pnl) as total_pnl,
            AVG(pnl) as avg_pnl
        FROM trades
        WHERE status = 'closed'
        GROUP BY plugin_id
    ''')
    
    results = {}
    for row in cursor.fetchall():
        plugin_id = row[0]
        results[plugin_id] = {
            'total_trades': row[1],
            'winning_trades': row[2],
            'total_pnl': row[3],
            'avg_pnl': row[4]
        }
    return results
```

---

## PART 5: UPDATE CONFIG FILES

### 5.1 Update Plugin Config Files

**Each plugin's config.json should specify its database:**

```json
{
  "plugin_id": "v3-logic-combined",
  "database": {
    "use_shared": true,
    "shared_db": "data/trading_bot.db",
    "isolated_db": "data/zepix_v3_logic_combined.db"
  }
}
```

---

## PART 6: DATA MIGRATION MAPPING

### 6.1 Old to New Plugin ID Mapping

| Old Value (logic_type) | New Value (plugin_id) |
|------------------------|----------------------|
| combinedlogic-1 | v3-logic-01-5min |
| combinedlogic-2 | v3-logic-02-15min |
| combinedlogic-3 | v3-logic-03-1h |
| LOGIC1 | v3-logic-01-5min |
| LOGIC2 | v3-logic-02-15min |
| LOGIC3 | v3-logic-03-1h |
| NULL | legacy |
| (empty) | legacy |

### 6.2 Preserve Historical Data

All existing trades will be preserved with:
- Original data unchanged
- New `plugin_id` column populated based on `logic_type`
- Trades without `logic_type` marked as `legacy`

---

## PART 7: ROLLBACK PLAN

### 7.1 Automatic Backup

Migration script creates backup at:
```
data/backups/trading_bot_YYYYMMDD_HHMMSS.db
```

### 7.2 Rollback Steps

```bash
# 1. Stop the bot
# 2. Restore backup
cp data/backups/trading_bot_YYYYMMDD_HHMMSS.db data/trading_bot.db

# 3. Restart bot
```

---

## PART 8: VERIFICATION CHECKLIST

After migration, verify:

- [ ] Backup created successfully
- [ ] plugin_id column added to trades table
- [ ] plugin_id column added to reentry_chains table
- [ ] plugin_id column added to profit_booking_chains table
- [ ] plugin_id column added to trading_sessions table
- [ ] Existing trades migrated to correct plugin_id
- [ ] Indexes created for plugin_id queries
- [ ] save_trade() accepts plugin_id parameter
- [ ] get_trades_by_plugin() works correctly
- [ ] get_plugin_statistics() works correctly
- [ ] Bot starts without database errors

---

## PART 9: EXECUTION ORDER

1. **Run migration script** (before any code changes)
2. **Update database.py** (add new methods)
3. **Update plugins** (pass plugin_id when saving trades)
4. **Test queries** (verify data isolation)

---

## SUCCESS CRITERIA

1. **All tables have plugin_id column**
2. **Existing data migrated correctly**
3. **New trades include plugin_id**
4. **Per-plugin statistics available**
5. **No data loss**
