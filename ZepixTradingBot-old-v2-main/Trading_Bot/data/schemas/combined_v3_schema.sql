-- V3 Combined Logic Database Schema
-- File: data/zepix_combined.db
-- Version: 1.0.0
-- Date: 2026-01-14
-- Purpose: Isolated database for V3 Combined Logic Plugin trades

-- Main trades table for V3 dual-order system
CREATE TABLE IF NOT EXISTS combined_v3_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Order Identification
    order_a_ticket INTEGER UNIQUE,          -- Order A (TP Trail) ticket
    order_b_ticket INTEGER UNIQUE,          -- Order B (Profit Trail) ticket
    mt5_parent_ticket INTEGER,              -- Primary ticket for linking
    
    -- Basic Trade Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    entry_price REAL NOT NULL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    status TEXT CHECK(status IN ('OPEN', 'PARTIAL', 'CLOSED')) DEFAULT 'OPEN',
    
    -- V3 Specific: Signal Details
    signal_type TEXT NOT NULL,              -- 'Institutional_Launchpad', 'Liquidity_Trap', etc. (12 types)
    signal_timeframe TEXT,                  -- '5', '15', '60', '240'
    consensus_score INTEGER CHECK(consensus_score BETWEEN 0 AND 9),  -- 0-9 range
    position_multiplier REAL,               -- Calculated from consensus (0.2-1.0)
    
    -- V3 Specific: MTF 4-Pillar Trends (extracted indices 2-5)
    mtf_15m INTEGER CHECK(mtf_15m IN (-1, 0, 1)),   -- Index 2: 15-minute trend
    mtf_1h INTEGER CHECK(mtf_1h IN (-1, 0, 1)),     -- Index 3: 1-hour trend
    mtf_4h INTEGER CHECK(mtf_4h IN (-1, 0, 1)),     -- Index 4: 4-hour trend
    mtf_1d INTEGER CHECK(mtf_1d IN (-1, 0, 1)),     -- Index 5: 1-day trend
    mtf_raw_string TEXT,                    -- Original "1,1,-1,1,1,1" for reference
    
    -- V3 Specific: Routing
    logic_route TEXT CHECK(logic_route IN ('LOGIC1', 'LOGIC2', 'LOGIC3')),
    logic_multiplier REAL,                  -- 1.25 (L1), 1.0 (L2), 0.625 (L3)
    routing_reason TEXT,                    -- 'signal_override' or 'timeframe_routing'
    
    -- V3 Specific: Dual Order Details
    order_a_lot_size REAL,
    order_b_lot_size REAL,
    order_a_sl_price REAL,                  -- V3 Smart SL from Pine Script
    order_b_sl_price REAL,                  -- Fixed $10 SL (DIFFERENT from order_a)
    order_a_tp_price REAL,                  -- TP2 (extended target)
    order_b_tp_price REAL,                  -- TP1 (closer target)
    
    -- Order A Results
    order_a_exit_price REAL,
    order_a_exit_time TIMESTAMP,
    order_a_profit_pips REAL,
    order_a_profit_dollars REAL,
    order_a_status TEXT CHECK(order_a_status IN ('OPEN', 'CLOSED')),
    
    -- Order B Results
    order_b_exit_price REAL,
    order_b_exit_time TIMESTAMP,
    order_b_profit_pips REAL,
    order_b_profit_dollars REAL,
    order_b_status TEXT CHECK(order_b_status IN ('OPEN', 'CLOSED')),
    
    -- Combined P&L
    total_profit_pips REAL,
    total_profit_dollars REAL,
    commission REAL DEFAULT 0,
    swap REAL DEFAULT 0,
    
    -- Metadata
    trend_bypass_used BOOLEAN DEFAULT 0,    -- Was trend check bypassed?
    is_entry_v3_signal BOOLEAN DEFAULT 0,   -- Fresh v3 signal?
    close_reason TEXT,
    notes TEXT
);

-- Indexes for V3 trades
CREATE INDEX IF NOT EXISTS idx_v3_trades_status ON combined_v3_trades(status);
CREATE INDEX IF NOT EXISTS idx_v3_trades_symbol ON combined_v3_trades(symbol);
CREATE INDEX IF NOT EXISTS idx_v3_trades_signal_type ON combined_v3_trades(signal_type);
CREATE INDEX IF NOT EXISTS idx_v3_trades_logic_route ON combined_v3_trades(logic_route);
CREATE INDEX IF NOT EXISTS idx_v3_trades_entry_time ON combined_v3_trades(entry_time);

-- Profit bookings table for V3
CREATE TABLE IF NOT EXISTS v3_profit_bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER NOT NULL,              -- References combined_v3_trades.id
    order_type TEXT CHECK(order_type IN ('ORDER_A', 'ORDER_B')),
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_percentage REAL NOT NULL,
    closed_volume REAL NOT NULL,
    profit_pips REAL,
    profit_dollars REAL,
    reason TEXT,                            -- 'TP1', 'TP2', 'Manual', 'Trailing'
    FOREIGN KEY (trade_id) REFERENCES combined_v3_trades(id)
);

-- Signals log for V3
CREATE TABLE IF NOT EXISTS v3_signals_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signal_type TEXT NOT NULL,              -- All 12 signal types
    symbol TEXT NOT NULL,
    direction TEXT,
    timeframe TEXT,
    consensus_score INTEGER,
    mtf_raw_string TEXT,
    signal_json TEXT,                       -- Full alert payload
    processed BOOLEAN DEFAULT 0,
    trade_placed BOOLEAN DEFAULT 0,
    trade_id INTEGER,
    skip_reason TEXT,                       -- Why skipped (if any)
    FOREIGN KEY (trade_id) REFERENCES combined_v3_trades(id)
);

-- Re-entry chains table for V3 (SL Hunt Recovery, TP Continuation, Exit Continuation)
CREATE TABLE IF NOT EXISTS v3_reentry_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_id TEXT UNIQUE NOT NULL,
    plugin_id TEXT NOT NULL DEFAULT 'combined_v3',
    
    -- Chain Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    original_trade_id INTEGER,
    original_entry_price REAL,
    original_entry_time TIMESTAMP,
    
    -- Chain Status
    status TEXT CHECK(status IN ('ACTIVE', 'RECOVERY_MODE', 'STOPPED', 'COMPLETED')) DEFAULT 'ACTIVE',
    current_level INTEGER DEFAULT 0,
    max_level INTEGER DEFAULT 5,
    
    -- Re-entry Type
    reentry_type TEXT CHECK(reentry_type IN ('SL_HUNT', 'TP_CONTINUATION', 'EXIT_CONTINUATION')),
    
    -- Recovery Details
    last_sl_price REAL,
    last_tp_price REAL,
    recovery_threshold REAL DEFAULT 0.70,
    recovery_window_minutes INTEGER DEFAULT 30,
    
    -- Chain Results
    total_entries INTEGER DEFAULT 1,
    total_profit_dollars REAL DEFAULT 0,
    total_loss_dollars REAL DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Metadata
    stop_reason TEXT,
    metadata_json TEXT,
    
    FOREIGN KEY (original_trade_id) REFERENCES combined_v3_trades(id)
);

CREATE INDEX IF NOT EXISTS idx_v3_reentry_chains_status ON v3_reentry_chains(status);
CREATE INDEX IF NOT EXISTS idx_v3_reentry_chains_symbol ON v3_reentry_chains(symbol);
CREATE INDEX IF NOT EXISTS idx_v3_reentry_chains_plugin_id ON v3_reentry_chains(plugin_id);

-- Daily statistics for V3
CREATE TABLE IF NOT EXISTS v3_daily_stats (
    date TEXT PRIMARY KEY,
    total_dual_entries INTEGER DEFAULT 0,
    total_order_a_closed INTEGER DEFAULT 0,
    total_order_b_closed INTEGER DEFAULT 0,
    logic1_trades INTEGER DEFAULT 0,
    logic2_trades INTEGER DEFAULT 0,
    logic3_trades INTEGER DEFAULT 0,
    total_profit_dollars REAL DEFAULT 0,
    win_rate REAL DEFAULT 0,
    profit_factor REAL DEFAULT 0
);
