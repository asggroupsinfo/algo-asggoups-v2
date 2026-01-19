# 💾 DATABASE SCHEMA DOCUMENTATION

**Created:** January 19, 2026  
**Bot Version:** V5 Hybrid Plugin Architecture  
**Database:** SQLite 3 (`data/trading_bot.db`)  
**Scope:** All tables for trading, analytics, sessions, and system state

---

## 📑 TABLE OF CONTENTS

1. [Database Overview](#database-overview)
2. [Core Trading Tables](#core-trading-tables)
3. [Re-entry System Tables](#re-entry-system-tables)
4. [Profit Booking Tables](#profit-booking-tables)
5. [Session Tracking Tables](#session-tracking-tables)
6. [System State Tables](#system-state-tables)
7. [Analytics Queries](#analytics-queries)
8. [Database Maintenance](#database-maintenance)

---

## 📊 DATABASE OVERVIEW

### **Database Location**
```
data/trading_bot.db
```

### **Connection Settings**
```python
conn = sqlite3.connect(
    'data/trading_bot.db',
    check_same_thread=False,
    timeout=30.0
)
conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
```

### **Table Summary**

| Table | Purpose | Records |
|-------|---------|---------|
| `trades` | All trade records | High |
| `reentry_chains` | Re-entry chain tracking | Medium |
| `sl_events` | SL hit events | Medium |
| `tp_reentry_events` | TP re-entry events | Medium |
| `reversal_exit_events` | Reversal exit tracking | Low |
| `profit_booking_chains` | Profit booking chains | Medium |
| `profit_booking_orders` | Profit booking orders | Medium |
| `profit_booking_events` | Profit booking events | Medium |
| `trading_sessions` | Trading session tracking | Medium |
| `system_state` | System state key-value | Low |

### **Entity Relationship Diagram (Text)**

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE SCHEMA                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐         ┌──────────────────┐                   │
│  │   trades    │◄───────►│  reentry_chains  │                   │
│  │  (Main)     │ chain_id│   (Re-entry)     │                   │
│  └──────┬──────┘         └────────┬─────────┘                   │
│         │                         │                              │
│         │ trade_id                │ chain_id                     │
│         ▼                         ▼                              │
│  ┌─────────────┐         ┌──────────────────┐                   │
│  │  sl_events  │         │tp_reentry_events │                   │
│  │ (SL Hits)   │         │  (TP Re-entry)   │                   │
│  └─────────────┘         └──────────────────┘                   │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │profit_booking_   │    │profit_booking_   │                   │
│  │    chains        │◄──►│    orders        │                   │
│  └────────┬─────────┘    └──────────────────┘                   │
│           │ chain_id                                             │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │profit_booking_   │                                           │
│  │    events        │                                           │
│  └──────────────────┘                                           │
│                                                                  │
│  ┌─────────────────┐     ┌─────────────────┐                    │
│  │trading_sessions │     │  system_state   │                    │
│  │  (Sessions)     │     │  (Key-Value)    │                    │
│  └─────────────────┘     └─────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📈 CORE TRADING TABLES

### **Table: `trades`**

**Purpose:** Store all trade records with full details

**Schema:**
```sql
CREATE TABLE trades (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Trade Identification
    trade_id TEXT UNIQUE,              -- MT5 ticket number
    
    -- Symbol & Direction
    symbol TEXT NOT NULL,              -- e.g., "XAUUSD"
    direction TEXT NOT NULL,           -- "BUY" or "SELL"
    
    -- Prices
    entry_price REAL,                  -- Entry price
    exit_price REAL,                   -- Exit price (NULL if open)
    sl_price REAL,                     -- Stop loss price
    tp_price REAL,                     -- Take profit price
    
    -- Position Size
    lot_size REAL NOT NULL,            -- Position size in lots
    
    -- Strategy & Logic
    strategy TEXT,                     -- Strategy name
    logic_type TEXT,                   -- "combinedlogic-1", "v6_15m", etc.
    
    -- Financial
    pnl REAL DEFAULT 0,                -- Profit/Loss in account currency
    commission REAL DEFAULT 0,         -- Commission paid
    swap REAL DEFAULT 0,               -- Swap charges
    
    -- Status & Timing
    status TEXT DEFAULT 'open',        -- "open", "closed", "cancelled"
    open_time DATETIME,                -- Trade open timestamp
    close_time DATETIME,               -- Trade close timestamp
    
    -- Comment
    comment TEXT,                      -- Trade comment/note
    
    -- Re-entry Chain Info
    chain_id TEXT,                     -- Re-entry chain ID
    chain_level INTEGER DEFAULT 1,     -- Level in chain (1, 2, 3, etc.)
    is_re_entry BOOLEAN DEFAULT FALSE, -- Is this a re-entry trade?
    
    -- Dual Order Info
    order_type TEXT,                   -- "DUAL_A", "DUAL_B", "SINGLE"
    
    -- Profit Booking Info
    profit_chain_id TEXT,              -- Profit booking chain ID
    profit_level INTEGER DEFAULT 0,    -- Profit booking level
    
    -- Session Info
    session_id TEXT,                   -- Trading session ID
    
    -- SL Adjustment Tracking
    sl_adjusted INTEGER DEFAULT 0,     -- Number of SL adjustments
    original_sl_distance REAL DEFAULT 0.0, -- Original SL distance
    
    -- V5 Timeframe Logic Fields
    base_lot_size REAL DEFAULT 0.0,    -- Base lot before multiplier
    final_lot_size REAL DEFAULT 0.0,   -- Final lot after multiplier
    base_sl_pips REAL DEFAULT 0.0,     -- Base SL before adjustment
    final_sl_pips REAL DEFAULT 0.0,    -- Final SL in pips
    lot_multiplier REAL DEFAULT 1.0,   -- Lot size multiplier used
    sl_multiplier REAL DEFAULT 1.0,    -- SL multiplier used
    
    -- Indexes
    INDEX idx_trades_symbol (symbol),
    INDEX idx_trades_status (status),
    INDEX idx_trades_close_time (close_time),
    INDEX idx_trades_chain_id (chain_id),
    INDEX idx_trades_logic_type (logic_type)
);
```

**Column Details:**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `trade_id` | TEXT | MT5 ticket number | "123456789" |
| `symbol` | TEXT | Trading symbol | "XAUUSD" |
| `direction` | TEXT | Trade direction | "BUY" or "SELL" |
| `entry_price` | REAL | Entry price | 2050.50 |
| `exit_price` | REAL | Exit price | 2065.00 |
| `sl_price` | REAL | Stop loss | 2040.00 |
| `tp_price` | REAL | Take profit | 2070.00 |
| `lot_size` | REAL | Position size | 0.1 |
| `logic_type` | TEXT | Plugin ID | "combinedlogic-1" |
| `pnl` | REAL | Profit/Loss | 125.50 |
| `status` | TEXT | Trade status | "closed" |
| `chain_id` | TEXT | Re-entry chain | "chain_abc123" |
| `order_type` | TEXT | Dual order type | "DUAL_A" |

**Sample Insert:**
```sql
INSERT INTO trades (
    trade_id, symbol, direction, entry_price, sl_price, tp_price,
    lot_size, strategy, logic_type, status, open_time, order_type
) VALUES (
    '123456789', 'XAUUSD', 'BUY', 2050.50, 2040.00, 2070.00,
    0.1, 'V3_HYBRID', 'combinedlogic-1', 'open', 
    datetime('now'), 'DUAL_A'
);
```

---

## 🔄 RE-ENTRY SYSTEM TABLES

### **Table: `reentry_chains`**

**Purpose:** Track re-entry chains (TP/SL/Exit continuation)

**Schema:**
```sql
CREATE TABLE reentry_chains (
    -- Primary Key
    chain_id TEXT PRIMARY KEY,
    
    -- Trade Info
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    
    -- Original Trade Reference
    original_entry REAL,               -- Original entry price
    original_sl_distance REAL,         -- Original SL distance
    
    -- Chain Progress
    max_level_reached INTEGER DEFAULT 1, -- Highest level reached
    
    -- Financial
    total_profit REAL DEFAULT 0,       -- Total chain profit
    
    -- Status
    status TEXT DEFAULT 'ACTIVE',      -- "ACTIVE", "COMPLETED", "STOPPED"
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);
```

**Example Query - Active Chains:**
```sql
SELECT * FROM reentry_chains 
WHERE status = 'ACTIVE' 
ORDER BY created_at DESC;
```

---

### **Table: `sl_events`**

**Purpose:** Track SL hit events for SL Hunt recovery

**Schema:**
```sql
CREATE TABLE sl_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Trade Reference
    trade_id TEXT,
    symbol TEXT,
    
    -- SL Details
    sl_price REAL,
    original_entry REAL,
    
    -- Timing
    hit_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Recovery Status
    recovery_attempted BOOLEAN DEFAULT FALSE,
    recovery_successful BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
);
```

**Analytics Query - SL Recovery Rate:**
```sql
SELECT 
    COUNT(*) as total_sl_hits,
    SUM(CASE WHEN recovery_attempted THEN 1 ELSE 0 END) as attempts,
    SUM(CASE WHEN recovery_successful THEN 1 ELSE 0 END) as successes,
    ROUND(100.0 * SUM(CASE WHEN recovery_successful THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN recovery_attempted THEN 1 ELSE 0 END), 0), 2) as success_rate
FROM sl_events
WHERE hit_time >= datetime('now', '-30 days');
```

---

### **Table: `tp_reentry_events`**

**Purpose:** Track TP continuation re-entries

**Schema:**
```sql
CREATE TABLE tp_reentry_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Chain Reference
    chain_id TEXT,
    symbol TEXT,
    
    -- TP Details
    tp_level INTEGER,                  -- TP1, TP2, TP3
    tp_price REAL,
    reentry_price REAL,
    
    -- Risk Adjustment
    sl_reduction_percent REAL,         -- SL reduction applied
    
    -- Result
    pnl REAL,
    
    -- Timing
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (chain_id) REFERENCES reentry_chains(chain_id)
);
```

---

### **Table: `reversal_exit_events`**

**Purpose:** Track reversal signal exits

**Schema:**
```sql
CREATE TABLE reversal_exit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Trade Reference
    trade_id TEXT,
    symbol TEXT,
    
    -- Exit Details
    exit_price REAL,
    exit_signal TEXT,                  -- "REVERSAL_BUY", "REVERSAL_SELL"
    
    -- Result
    pnl REAL,
    
    -- Timing
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
);
```

---

## 💰 PROFIT BOOKING TABLES

### **Table: `profit_booking_chains`**

**Purpose:** Track profit booking pyramid chains

**Schema:**
```sql
CREATE TABLE profit_booking_chains (
    -- Primary Key
    chain_id TEXT PRIMARY KEY,
    
    -- Position Info
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    base_lot REAL NOT NULL,            -- Starting lot size
    
    -- Chain Progress
    current_level INTEGER DEFAULT 0,   -- Current pyramid level
    
    -- Financial
    total_profit REAL DEFAULT 0,       -- Total booked profit
    
    -- Status
    status TEXT DEFAULT 'ACTIVE',      -- "ACTIVE", "COMPLETED", "STOPPED"
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### **Table: `profit_booking_orders`**

**Purpose:** Individual profit booking orders within a chain

**Schema:**
```sql
CREATE TABLE profit_booking_orders (
    -- Primary Key
    order_id TEXT PRIMARY KEY,
    
    -- Chain Reference
    chain_id TEXT,
    
    -- Level Info
    level INTEGER,                     -- Pyramid level (1, 2, 3, etc.)
    
    -- Targets
    profit_target REAL,                -- Profit target for this level
    sl_reduction INTEGER,              -- SL reduction % for this level
    
    -- Status
    status TEXT DEFAULT 'PENDING',     -- "PENDING", "TRIGGERED", "CLOSED"
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (chain_id) REFERENCES profit_booking_chains(chain_id)
);
```

---

### **Table: `profit_booking_events`**

**Purpose:** Log profit booking events

**Schema:**
```sql
CREATE TABLE profit_booking_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Chain Reference
    chain_id TEXT,
    
    -- Event Details
    level INTEGER,                     -- Level that triggered
    profit_booked REAL,                -- Profit booked at this level
    orders_closed INTEGER,             -- Orders closed
    orders_placed INTEGER,             -- New orders placed
    
    -- Timing
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (chain_id) REFERENCES profit_booking_chains(chain_id)
);
```

---

## 📅 SESSION TRACKING TABLES

### **Table: `trading_sessions`**

**Purpose:** Track trading sessions for analytics

**Schema:**
```sql
CREATE TABLE trading_sessions (
    -- Primary Key
    session_id TEXT PRIMARY KEY,
    
    -- Session Info
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    
    -- Signals
    entry_signal TEXT,                 -- Signal that started session
    exit_reason TEXT,                  -- Reason session ended
    
    -- Timing
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    
    -- Results
    total_pnl REAL DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    
    -- Status
    status TEXT DEFAULT 'ACTIVE',      -- "ACTIVE", "COMPLETED"
    
    -- Additional Data (JSON)
    metadata TEXT                      -- JSON blob for extra data
);
```

**Session Analytics Query:**
```sql
-- Get session breakdown
SELECT 
    session_id,
    symbol,
    direction,
    total_pnl,
    total_trades,
    ROUND(total_pnl / NULLIF(total_trades, 0), 2) as avg_pnl_per_trade,
    start_time,
    end_time,
    ROUND((julianday(end_time) - julianday(start_time)) * 24, 2) as duration_hours
FROM trading_sessions
WHERE status = 'COMPLETED'
ORDER BY total_pnl DESC
LIMIT 10;
```

---

## ⚙️ SYSTEM STATE TABLES

### **Table: `system_state`**

**Purpose:** Store system state key-value pairs

**Schema:**
```sql
CREATE TABLE system_state (
    -- Primary Key
    key TEXT PRIMARY KEY,
    
    -- Value
    value TEXT,
    
    -- Timing
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Common Keys:**
```sql
-- System state keys
INSERT OR REPLACE INTO system_state (key, value, updated_at) VALUES
('trading_enabled', 'true', datetime('now')),
('daily_loss', '0.0', datetime('now')),
('lifetime_loss', '0.0', datetime('now')),
('current_risk_tier', '2', datetime('now')),
('manual_lot_override', '0.0', datetime('now')),
('last_signal_time', '2026-01-19T10:30:00', datetime('now'));
```

---

## 📊 ANALYTICS QUERIES

### **Daily Performance Report**

```sql
SELECT 
    DATE(close_time) as trade_date,
    COUNT(*) as total_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
    ROUND(100.0 * SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate,
    ROUND(SUM(pnl), 2) as total_pnl,
    ROUND(AVG(pnl), 2) as avg_pnl,
    MAX(pnl) as best_trade,
    MIN(pnl) as worst_trade
FROM trades
WHERE status = 'closed'
    AND DATE(close_time) = DATE('now')
GROUP BY DATE(close_time);
```

### **Weekly Performance Report**

```sql
SELECT 
    strftime('%Y-W%W', close_time) as week,
    COUNT(*) as total_trades,
    ROUND(100.0 * SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate,
    ROUND(SUM(pnl), 2) as total_pnl,
    ROUND(AVG(pnl), 2) as avg_pnl
FROM trades
WHERE status = 'closed'
    AND close_time >= datetime('now', '-7 days')
GROUP BY week
ORDER BY week DESC;
```

### **Monthly Performance Report**

```sql
SELECT 
    strftime('%Y-%m', close_time) as month,
    COUNT(*) as total_trades,
    ROUND(100.0 * SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate,
    ROUND(SUM(pnl), 2) as total_pnl,
    ROUND(AVG(pnl), 2) as avg_pnl,
    COUNT(DISTINCT DATE(close_time)) as trading_days
FROM trades
WHERE status = 'closed'
    AND close_time >= datetime('now', '-30 days')
GROUP BY month;
```

### **Plugin Performance Comparison**

```sql
SELECT 
    logic_type as plugin,
    COUNT(*) as trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
    ROUND(100.0 * SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate,
    ROUND(SUM(pnl), 2) as total_pnl,
    ROUND(AVG(pnl), 2) as avg_pnl,
    ROUND(AVG(CASE WHEN pnl > 0 THEN pnl END), 2) as avg_win,
    ROUND(AVG(CASE WHEN pnl < 0 THEN pnl END), 2) as avg_loss
FROM trades
WHERE status = 'closed'
    AND logic_type IS NOT NULL
GROUP BY logic_type
ORDER BY total_pnl DESC;
```

### **V3 vs V6 Comparison**

```sql
SELECT 
    CASE 
        WHEN logic_type LIKE 'combinedlogic%' THEN 'V3_Combined'
        WHEN logic_type LIKE 'v6_%' THEN 'V6_PriceAction'
        ELSE 'Other'
    END as strategy_group,
    COUNT(*) as trades,
    ROUND(100.0 * SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate,
    ROUND(SUM(pnl), 2) as total_pnl,
    ROUND(AVG(pnl), 2) as avg_pnl
FROM trades
WHERE status = 'closed'
GROUP BY strategy_group;
```

### **V6 Timeframe Breakdown**

```sql
SELECT 
    logic_type as timeframe,
    COUNT(*) as trades,
    ROUND(100.0 * SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate,
    ROUND(SUM(pnl), 2) as total_pnl
FROM trades
WHERE status = 'closed'
    AND logic_type LIKE 'v6_%'
GROUP BY logic_type
ORDER BY trades DESC;
```

### **Symbol Performance**

```sql
SELECT 
    symbol,
    COUNT(*) as trades,
    ROUND(100.0 * SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate,
    ROUND(SUM(pnl), 2) as total_pnl,
    ROUND(AVG(pnl), 2) as avg_pnl
FROM trades
WHERE status = 'closed'
GROUP BY symbol
ORDER BY total_pnl DESC;
```

### **Re-entry Chain Statistics**

```sql
SELECT 
    COUNT(*) as total_chains,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active,
    ROUND(AVG(max_level_reached), 2) as avg_levels,
    MAX(max_level_reached) as max_level,
    ROUND(SUM(total_profit), 2) as total_chain_profit,
    ROUND(AVG(total_profit), 2) as avg_chain_profit,
    COUNT(CASE WHEN total_profit > 0 THEN 1 END) as profitable_chains
FROM reentry_chains;
```

### **Profit Booking Statistics**

```sql
SELECT 
    COUNT(*) as total_chains,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
    ROUND(AVG(current_level), 2) as avg_level,
    MAX(current_level) as max_level,
    ROUND(SUM(total_profit), 2) as total_booked,
    ROUND(AVG(total_profit), 2) as avg_per_chain
FROM profit_booking_chains;
```

### **Dual Order Performance**

```sql
SELECT 
    order_type,
    COUNT(*) as trades,
    ROUND(100.0 * SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate,
    ROUND(SUM(pnl), 2) as total_pnl,
    ROUND(AVG(pnl), 2) as avg_pnl
FROM trades
WHERE status = 'closed'
    AND order_type IN ('DUAL_A', 'DUAL_B')
GROUP BY order_type;
```

---

## 🛠️ DATABASE MAINTENANCE

### **Backup Script**

```python
import shutil
from datetime import datetime

def backup_database():
    """Create database backup"""
    source = 'data/trading_bot.db'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = f'data/backups/trading_bot_{timestamp}.db'
    
    shutil.copy2(source, backup)
    print(f"Backup created: {backup}")
```

### **Cleanup Old Data**

```sql
-- Delete trades older than 90 days
DELETE FROM trades 
WHERE close_time < datetime('now', '-90 days')
AND status = 'closed';

-- Delete old SL events
DELETE FROM sl_events
WHERE hit_time < datetime('now', '-90 days');

-- Delete completed chains older than 60 days
DELETE FROM reentry_chains
WHERE completed_at < datetime('now', '-60 days')
AND status = 'COMPLETED';
```

### **Optimize Database**

```sql
-- Vacuum to reclaim space
VACUUM;

-- Analyze for query optimization
ANALYZE;

-- Reindex
REINDEX;
```

### **Database Health Check**

```python
def check_database_health():
    """Check database integrity"""
    cursor = conn.cursor()
    
    # Integrity check
    cursor.execute("PRAGMA integrity_check")
    result = cursor.fetchone()
    if result[0] != 'ok':
        print(f"DATABASE INTEGRITY ERROR: {result[0]}")
        return False
    
    # Check foreign keys
    cursor.execute("PRAGMA foreign_key_check")
    fk_errors = cursor.fetchall()
    if fk_errors:
        print(f"FOREIGN KEY ERRORS: {fk_errors}")
        return False
    
    # Check table count
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """)
    tables = cursor.fetchall()
    print(f"Tables found: {len(tables)}")
    
    return True
```

### **Migration Script Template**

```python
def migrate_database_vX():
    """Migration script for version X"""
    cursor = conn.cursor()
    
    # Check current version
    cursor.execute("""
        SELECT value FROM system_state WHERE key = 'db_version'
    """)
    current_version = cursor.fetchone()
    
    if current_version and int(current_version[0]) >= X:
        print("Already at version X or higher")
        return
    
    # Run migrations
    migrations = [
        "ALTER TABLE trades ADD COLUMN new_column TEXT",
        # ... more migrations
    ]
    
    for migration in migrations:
        try:
            cursor.execute(migration)
            print(f"✅ {migration[:50]}...")
        except sqlite3.OperationalError as e:
            print(f"⚠️ Skipped (may already exist): {e}")
    
    # Update version
    cursor.execute("""
        INSERT OR REPLACE INTO system_state (key, value, updated_at)
        VALUES ('db_version', 'X', datetime('now'))
    """)
    
    conn.commit()
    print(f"Migration to version X complete")
```

---

## 📁 FILE: `src/database.py` Methods Summary

| Method | Purpose | Returns |
|--------|---------|---------|
| `create_tables()` | Initialize all tables | None |
| `save_trade(trade)` | Save/update trade | None |
| `save_chain(chain)` | Save re-entry chain | None |
| `save_sl_event(...)` | Log SL hit event | None |
| `get_trade_history(days)` | Get recent trades | List[Dict] |
| `get_chain_statistics()` | Chain performance | Dict |
| `get_sl_recovery_stats()` | SL recovery metrics | Dict |
| `get_tp_reentry_stats()` | TP re-entry metrics | Dict |
| `get_trades_by_date(date)` | Trades for specific date | List[Dict] |
| `save_profit_chain(chain)` | Save profit chain | None |
| `get_active_profit_chains()` | Active profit chains | List[Dict] |
| `get_profit_chain_stats()` | Profit chain metrics | Dict |
| `create_session(...)` | Create trading session | None |
| `close_session(...)` | Close trading session | None |
| `get_active_session(symbol)` | Get active session | Dict |
| `get_session_details(id)` | Detailed session info | Dict |
| `test_connection()` | Check DB connection | bool |

---

**Document Created:** January 19, 2026  
**Total Tables:** 10  
**Total Columns:** 80+  
**Status:** COMPLETE ✅

---

## ⚠️ DEVELOPER NOTE - IMPORTANT

**Bot Source Code Location:**  
`C:\Users\Ansh Shivaay Gupta\Downloads\ZepixTradingBot-New-v1\ZepixTradingBot-old-v2-main\Trading_Bot`

### Implementation Guidelines:

> ⚠️ **This is a Planning & Research Document - DO NOT Apply Blindly!**

**Implementation Process:**

1. **First, Complete Scan of the Bot**
   - Analyze the complete bot code
   - Understand the current architecture
   - Review existing implementations

2. **Map Ideas According to the Bot**
   - Check how the ideas given here will be implemented in the bot
   - Identify dependencies
   - Look for conflicts

3. **Create New Plan According to the Bot**
   - Create a new implementation plan according to the bot's current state
   - Adapt ideas that don't directly fit

4. **Make Improvements (Full Freedom)**
   - You have full freedom to improve the ideas
   - Use a better approach if available
   - Optimize according to the bot's architecture

5. **Then Implement**
   - Implement only after planning is complete

### Critical Rules:

| Rule | Description |
|------|-------------|
| ✅ **Idea Must Be Fully Implemented** | The core idea/concept must be fully implemented |
| ✅ **Improvements Allowed** | You can improve the implementation |
| ❌ **Idea Should Not Change** | The core concept of the idea must remain the same |
| ❌ **Do Not Apply Blindly** | First scan, plan, then implement |

**Remember:** This document provides ideas & possibilities - the final implementation will depend on the bot's actual architecture.

---

**END OF DOCUMENT**