-- Central System Database Schema
-- File: data/zepix_bot.db
-- Version: 1.0.0
-- Date: 2026-01-14
-- Purpose: Central database for plugin registry, aggregated trades, and system configuration

-- Plugin registry table
CREATE TABLE IF NOT EXISTS plugins_registry (
    plugin_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    plugin_type TEXT CHECK(plugin_type IN ('V3_COMBINED', 'V6_PRICE_ACTION')),
    version TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    installed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    database_path TEXT,
    status TEXT CHECK(status IN ('ACTIVE', 'DISABLED', 'ERROR')),
    error_message TEXT
);

-- Pre-populate with default plugins
INSERT OR IGNORE INTO plugins_registry VALUES 
    ('combined_v3', 'V3 Combined Logic', 'V3_COMBINED', '1.0.0', 1, datetime('now'), NULL, 'data/zepix_combined.db', 'ACTIVE', NULL),
    ('price_action_1m', 'V6 1M Scalping', 'V6_PRICE_ACTION', '1.0.0', 1, datetime('now'), NULL, 'data/zepix_price_action.db', 'ACTIVE', NULL),
    ('price_action_5m', 'V6 5M Momentum', 'V6_PRICE_ACTION', '1.0.0', 1, datetime('now'), NULL, 'data/zepix_price_action.db', 'ACTIVE', NULL),
    ('price_action_15m', 'V6 15M Intraday', 'V6_PRICE_ACTION', '1.0.0', 1, datetime('now'), NULL, 'data/zepix_price_action.db', 'ACTIVE', NULL),
    ('price_action_1h', 'V6 1H Swing', 'V6_PRICE_ACTION', '1.0.0', 1, datetime('now'), NULL, 'data/zepix_price_action.db', 'ACTIVE', NULL);

-- Aggregated trades table (synced from per-plugin DBs every 5 minutes)
CREATE TABLE IF NOT EXISTS aggregated_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL,
    plugin_type TEXT,
    mt5_ticket INTEGER,
    symbol TEXT,
    direction TEXT,
    lot_size REAL,
    entry_time TIMESTAMP,
    exit_time TIMESTAMP,
    profit_dollars REAL,
    status TEXT,
    FOREIGN KEY (plugin_id) REFERENCES plugins_registry(plugin_id)
);

CREATE INDEX IF NOT EXISTS idx_agg_trades_plugin ON aggregated_trades(plugin_id);
CREATE INDEX IF NOT EXISTS idx_agg_trades_time ON aggregated_trades(entry_time);

-- System configuration table
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pre-populate with default system config
INSERT OR IGNORE INTO system_config VALUES 
    ('bot_version', '3.0.0', datetime('now')),
    ('architecture', 'dual_core_v3_v6', datetime('now')),
    ('v3_enabled', 'true', datetime('now')),
    ('v6_enabled', 'true', datetime('now'));

-- System events table for logging
CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    plugin_id TEXT,
    description TEXT,
    severity TEXT CHECK(severity IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL'))
);

-- Sync status table for tracking database synchronization
CREATE TABLE IF NOT EXISTS sync_status (
    plugin_id TEXT PRIMARY KEY,
    last_sync_time TIMESTAMP,
    last_sync_success BOOLEAN,
    records_synced INTEGER DEFAULT 0,
    error_message TEXT,
    FOREIGN KEY (plugin_id) REFERENCES plugins_registry(plugin_id)
);
