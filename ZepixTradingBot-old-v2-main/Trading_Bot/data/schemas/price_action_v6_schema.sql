-- V6 Price Action Database Schema
-- File: data/zepix_price_action.db
-- Version: 1.0.0
-- Date: 2026-01-14
-- Purpose: Isolated database for V6 Price Action Plugin trades (1M, 5M, 15M, 1H)

-- 1M Scalping trades (ORDER B ONLY)
CREATE TABLE IF NOT EXISTS price_action_1m_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Order Identification
    order_b_ticket INTEGER UNIQUE,          -- 1M uses ORDER B ONLY
    
    -- Basic Trade Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    lot_size REAL NOT NULL,
    entry_price REAL NOT NULL,
    sl_price REAL,
    tp_price REAL,                          -- Uses TP1 (quick exit)
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    exit_price REAL,
    status TEXT CHECK(status IN ('OPEN', 'CLOSED')) DEFAULT 'OPEN',
    
    -- V6 1M Specific Fields
    adx REAL,
    adx_strength TEXT,                      -- 'STRONG', 'WEAK', 'NONE'
    confidence_score INTEGER,               -- 0-100
    confidence_level TEXT,                  -- 'HIGH', 'MODERATE'
    spread_pips REAL,                       -- Spread at entry
    market_state TEXT,                      -- 'TRENDING_BULLISH', 'SIDEWAYS', etc.
    
    -- Results
    profit_pips REAL,
    profit_dollars REAL,
    close_reason TEXT,
    
    -- Metadata
    execution_speed_ms INTEGER,             -- How fast was execution?
    slippage_pips REAL,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_v6_1m_status ON price_action_1m_trades(status);
CREATE INDEX IF NOT EXISTS idx_v6_1m_symbol ON price_action_1m_trades(symbol);

-- 5M Momentum trades (DUAL ORDERS)
CREATE TABLE IF NOT EXISTS price_action_5m_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Order Identification (DUAL ORDERS)
    order_a_ticket INTEGER UNIQUE,
    order_b_ticket INTEGER UNIQUE,
    
    -- Basic Trade Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    entry_price REAL NOT NULL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('OPEN', 'PARTIAL', 'CLOSED')) DEFAULT 'OPEN',
    
    -- V6 5M Specific Fields
    adx REAL,
    adx_strength TEXT,
    confidence_score INTEGER,
    trend_15m_aligned BOOLEAN,              -- Was 15m trend aligned?
    momentum_increasing BOOLEAN,            -- Momentum check result
    
    -- Dual Order Details
    order_a_lot_size REAL,
    order_b_lot_size REAL,
    order_a_sl_price REAL,
    order_b_sl_price REAL,
    order_a_tp_price REAL,                  -- TP2
    order_b_tp_price REAL,                  -- TP1
    
    -- Order A Results
    order_a_exit_price REAL,
    order_a_exit_time TIMESTAMP,
    order_a_profit_dollars REAL,
    order_a_status TEXT,
    
    -- Order B Results
    order_b_exit_price REAL,
    order_b_exit_time TIMESTAMP,
    order_b_profit_dollars REAL,
    order_b_status TEXT,
    
    -- Combined Results
    total_profit_dollars REAL,
    breakeven_moved BOOLEAN DEFAULT 0,      -- Did we move to breakeven after TP1?
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_v6_5m_status ON price_action_5m_trades(status);

-- 15M Intraday trades (ORDER A ONLY)
CREATE TABLE IF NOT EXISTS price_action_15m_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Order Identification (ORDER A ONLY)
    order_a_ticket INTEGER UNIQUE,
    
    -- Basic Trade Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    lot_size REAL NOT NULL,
    entry_price REAL NOT NULL,
    sl_price REAL,
    tp_price REAL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    status TEXT CHECK(status IN ('OPEN', 'CLOSED')) DEFAULT 'OPEN',
    
    -- V6 15M Specific Fields
    adx REAL,
    confidence_score INTEGER,
    market_state TEXT,                      -- MUST match signal direction
    pulse_bull_count INTEGER,               -- From Trend Pulse
    pulse_bear_count INTEGER,
    pulse_alignment_ok BOOLEAN,             -- bull_count > bear_count for BUY?
    
    -- Results
    exit_price REAL,
    profit_dollars REAL,
    close_reason TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_v6_15m_status ON price_action_15m_trades(status);

-- 1H Swing trades (ORDER A ONLY)
CREATE TABLE IF NOT EXISTS price_action_1h_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Order Identification (ORDER A ONLY)
    order_a_ticket INTEGER UNIQUE,
    
    -- Basic Trade Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    lot_size REAL NOT NULL,
    entry_price REAL NOT NULL,
    sl_price REAL,
    tp_price REAL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('OPEN', 'CLOSED')) DEFAULT 'OPEN',
    
    -- V6 1H Specific Fields
    trend_4h INTEGER,                       -- 4H trend value
    trend_1d INTEGER,                       -- 1D trend value
    higher_tf_aligned BOOLEAN,              -- 4H/1D alignment
    confidence_score INTEGER,
    
    -- Results
    exit_price REAL,
    exit_time TIMESTAMP,
    profit_dollars REAL,
    close_reason TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_v6_1h_status ON price_action_1h_trades(status);

-- Market trends table (Shared by all V6 plugins)
CREATE TABLE IF NOT EXISTS market_trends (
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,                -- '5', '15', '60', '240', '1440'
    bull_count INTEGER DEFAULT 0,
    bear_count INTEGER DEFAULT 0,
    market_state TEXT,                      -- 'TRENDING_BULLISH', 'TRENDING_BEARISH', 'SIDEWAYS', etc.
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changes TEXT,                           -- Comma-separated TF changes from TREND_PULSE
    PRIMARY KEY (symbol, timeframe)
);

CREATE INDEX IF NOT EXISTS idx_market_trends_symbol ON market_trends(symbol);

-- Signals log for V6
CREATE TABLE IF NOT EXISTS v6_signals_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signal_type TEXT NOT NULL,              -- 'BULLISH_ENTRY', 'BEARISH_ENTRY', 'TREND_PULSE'
    plugin_target TEXT,                     -- 'price_action_1m', '5m', '15m', '1h'
    symbol TEXT NOT NULL,
    timeframe TEXT,
    adx REAL,
    confidence_score INTEGER,
    signal_json TEXT,                       -- Full 15-field payload
    processed BOOLEAN DEFAULT 0,
    trade_placed BOOLEAN DEFAULT 0,
    trade_id INTEGER,
    skip_reason TEXT
);

-- Re-entry chains table for V6 (SL Hunt Recovery, TP Continuation, Exit Continuation)
CREATE TABLE IF NOT EXISTS v6_reentry_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_id TEXT UNIQUE NOT NULL,
    plugin_id TEXT NOT NULL,
    
    -- Chain Info
    symbol TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('BUY', 'SELL')),
    timeframe TEXT,
    original_trade_id INTEGER,
    original_entry_price REAL,
    original_entry_time TIMESTAMP,
    
    -- Chain Status
    status TEXT CHECK(status IN ('ACTIVE', 'RECOVERY_MODE', 'STOPPED', 'COMPLETED')) DEFAULT 'ACTIVE',
    current_level INTEGER DEFAULT 0,
    max_level INTEGER DEFAULT 3,
    
    -- Re-entry Type
    reentry_type TEXT CHECK(reentry_type IN ('SL_HUNT', 'TP_CONTINUATION', 'EXIT_CONTINUATION')),
    
    -- Recovery Details
    last_sl_price REAL,
    last_tp_price REAL,
    recovery_threshold REAL DEFAULT 0.70,
    recovery_window_minutes INTEGER DEFAULT 30,
    
    -- Higher TF Trend at Chain Start
    higher_tf TEXT,
    higher_tf_bull_count INTEGER,
    higher_tf_bear_count INTEGER,
    higher_tf_aligned BOOLEAN,
    
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
    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_v6_reentry_chains_status ON v6_reentry_chains(status);
CREATE INDEX IF NOT EXISTS idx_v6_reentry_chains_symbol ON v6_reentry_chains(symbol);
CREATE INDEX IF NOT EXISTS idx_v6_reentry_chains_plugin_id ON v6_reentry_chains(plugin_id);
CREATE INDEX IF NOT EXISTS idx_v6_reentry_chains_timeframe ON v6_reentry_chains(timeframe);

-- Profit bookings table for V6
CREATE TABLE IF NOT EXISTS v6_profit_bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER NOT NULL,
    plugin_id TEXT NOT NULL,
    chain_id TEXT,
    
    -- Booking Info
    order_type TEXT CHECK(order_type IN ('ORDER_A', 'ORDER_B')),
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_percentage REAL NOT NULL,
    closed_volume REAL NOT NULL,
    
    -- Results
    profit_pips REAL,
    profit_dollars REAL,
    
    -- Booking Reason
    reason TEXT,
    
    -- Higher TF Trend at Booking
    higher_tf_bull_count INTEGER,
    higher_tf_bear_count INTEGER,
    trend_aligned BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_v6_profit_bookings_plugin_id ON v6_profit_bookings(plugin_id);
CREATE INDEX IF NOT EXISTS idx_v6_profit_bookings_chain_id ON v6_profit_bookings(chain_id);

-- Daily statistics for V6
CREATE TABLE IF NOT EXISTS v6_daily_stats (
    date TEXT PRIMARY KEY,
    plugin_1m_trades INTEGER DEFAULT 0,
    plugin_5m_trades INTEGER DEFAULT 0,
    plugin_15m_trades INTEGER DEFAULT 0,
    plugin_1h_trades INTEGER DEFAULT 0,
    total_profit_dollars REAL DEFAULT 0,
    trend_pulse_updates INTEGER DEFAULT 0,
    win_rate REAL DEFAULT 0
);
