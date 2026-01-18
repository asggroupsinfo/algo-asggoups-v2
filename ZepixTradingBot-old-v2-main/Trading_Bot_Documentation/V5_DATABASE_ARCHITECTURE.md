# V5 Database Architecture

**Version**: 1.0.0  
**Date**: 2026-01-18  
**Status**: IMPLEMENTED

---

## Overview

The V5 Hybrid Plugin Architecture uses a 3-database isolation strategy to ensure V3 and V6 plugins operate independently without data conflicts. Each database serves a specific purpose and contains tables tailored to its plugin type.

---

## 1. Three-Database Architecture

| Database | File | Purpose | Tables |
|----------|------|---------|--------|
| V3 Combined Logic | `data/zepix_combined_v3.db` | V3 plugin trades and signals | 4 |
| V6 Price Action | `data/zepix_price_action.db` | V6 plugin trades (all timeframes) | 7 |
| Central System | `data/zepix_bot.db` | Plugin registry, aggregation, config | 5 |

### Database Isolation Principle

The V5 architecture enforces strict database isolation:
- V3 and V6 plugins have completely separate databases
- No cross-contamination of trading data
- Central database aggregates data for dashboards only
- Each plugin type has its own schema optimized for its needs

---

## 2. V3 Combined Logic Database

**File**: `data/zepix_combined_v3.db`  
**Schema**: `data/schemas/combined_v3_schema.sql`

### Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `combined_v3_trades` | Main trades table for V3 dual-order system | order_a_ticket, order_b_ticket, signal_type, logic_route |
| `v3_profit_bookings` | Profit booking records for partial closes | trade_id, order_type, closed_percentage |
| `v3_signals_log` | All V3 signals received (processed or skipped) | signal_type, symbol, consensus_score |
| `v3_daily_stats` | Daily aggregated statistics | date, total_dual_entries, win_rate |

### V3 Trades Table Schema

The `combined_v3_trades` table stores all V3 dual-order trades with:
- Order A (TP Trail) and Order B (Profit Trail) tickets
- Signal details: type, timeframe, consensus score (0-9)
- MTF 4-pillar trends: 15m, 1H, 4H, 1D
- Logic routing: LOGIC1 (1.25x), LOGIC2 (1.0x), LOGIC3 (0.625x)
- Dual order lot sizes and SL/TP prices
- Individual order results and combined P&L

---

## 3. V6 Price Action Database

**File**: `data/zepix_price_action.db`  
**Schema**: `data/schemas/price_action_v6_schema.sql`

### Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `price_action_1m_trades` | 1M scalping trades (Order B only) | order_b_ticket, adx, confidence_score |
| `price_action_5m_trades` | 5M momentum trades (Dual orders) | order_a_ticket, order_b_ticket |
| `price_action_15m_trades` | 15M intraday trades (Order A only) | order_a_ticket, pulse_bull_count |
| `price_action_1h_trades` | 1H swing trades (Order A only) | order_a_ticket, trend_4h, trend_1d |
| `market_trends` | Shared trend data for all V6 plugins | symbol, timeframe, bull_count, bear_count |
| `v6_signals_log` | All V6 signals received | signal_type, plugin_target, adx |
| `v6_daily_stats` | Daily aggregated statistics | date, plugin_1m_trades, plugin_5m_trades |

### V6 Timeframe-Specific Tables

Each V6 timeframe has its own trades table with columns specific to that timeframe's trading strategy:

**1M Scalping**: Uses Order B only for quick exits, tracks spread and execution speed  
**5M Momentum**: Uses dual orders (A + B), tracks 15m trend alignment  
**15M Intraday**: Uses Order A only, tracks Trend Pulse bull/bear counts  
**1H Swing**: Uses Order A only, tracks 4H and 1D trend alignment

---

## 4. Central System Database

**File**: `data/zepix_bot.db`  
**Schema**: `data/schemas/central_system_schema.sql`

### Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `plugins_registry` | Registered plugins and their status | plugin_id, plugin_type, enabled, status |
| `aggregated_trades` | Synced trades from all plugins | plugin_id, mt5_ticket, profit_dollars |
| `system_config` | System-wide configuration | key, value |
| `system_events` | System event logging | event_type, plugin_id, severity |
| `sync_status` | Database sync tracking | plugin_id, last_sync_time |

### Pre-Populated Data

The Central database is pre-populated with:

**plugins_registry**:
- `combined_v3` - V3 Combined Logic plugin
- `price_action_1m` - V6 1M Scalping plugin
- `price_action_5m` - V6 5M Momentum plugin
- `price_action_15m` - V6 15M Intraday plugin
- `price_action_1h` - V6 1H Swing plugin

**system_config**:
- `bot_version` = "3.0.0"
- `architecture` = "dual_core_v3_v6"
- `v3_enabled` = "true"
- `v6_enabled` = "true"

---

## 5. How Plugins Use Databases

### DatabaseService Integration

The `DatabaseService` class in `src/core/services/database_service.py` manages database access:

```python
DATABASE_PATHS = {
    'v3_combined': 'data/zepix_combined_v3.db',
    'v6_price_action_1m': 'data/zepix_price_action.db',
    'v6_price_action_5m': 'data/zepix_price_action.db',
    'v6_price_action_15m': 'data/zepix_price_action.db',
    'v6_price_action_1h': 'data/zepix_price_action.db',
    'central_system': 'data/zepix_bot.db',
}
```

### Plugin Database Access

Each plugin accesses its database through the ServiceAPI:

```python
# V3 plugin accessing its database
await service_api.database.insert_record(
    'v3_combined',
    'combined_v3_trades',
    trade_data
)

# V6 15m plugin accessing its database
await service_api.database.insert_record(
    'v6_price_action_15m',
    'price_action_15m_trades',
    trade_data
)
```

### Shared V6 Database

All V6 plugins share the same database file (`zepix_price_action.db`) but use different tables:
- 1M plugin → `price_action_1m_trades`
- 5M plugin → `price_action_5m_trades`
- 15M plugin → `price_action_15m_trades`
- 1H plugin → `price_action_1h_trades`
- All plugins → `market_trends` (shared)

---

## 6. Migration from Legacy Database

### Legacy Database

The old `trading_bot.db` is preserved and NOT deleted. It contains historical data from before the V5 architecture.

### Migration Strategy

1. **No automatic migration**: Legacy data remains in `trading_bot.db`
2. **New trades go to new databases**: All new V3/V6 trades use the new 3-database system
3. **Manual migration available**: If needed, a migration script can be created to move historical data

### Backward Compatibility

The V5 architecture maintains backward compatibility:
- Legacy `trading_bot.db` is preserved
- Old code paths can still access legacy data
- New plugins use new databases exclusively

---

## 7. Backup and Recovery

### Backup Strategy

All 3 databases should be backed up regularly:

```bash
# Backup all V5 databases
cp data/zepix_combined_v3.db data/backups/zepix_combined_v3_$(date +%Y%m%d).db
cp data/zepix_price_action.db data/backups/zepix_price_action_$(date +%Y%m%d).db
cp data/zepix_bot.db data/backups/zepix_bot_$(date +%Y%m%d).db
```

### Recovery Procedure

1. Stop the trading bot
2. Replace corrupted database with backup
3. Restart the trading bot
4. Verify data integrity

### Database Integrity Checks

```python
# Run integrity check on all databases
python scripts/initialize_v5_databases.py --verify-only
```

---

## 8. Initialization

### Using the Initialization Script

```bash
# Initialize all 3 databases
cd Trading_Bot
python scripts/initialize_v5_databases.py
```

### Expected Output

```
============================================================
V5 DATABASE INITIALIZATION SUMMARY
============================================================
Overall Status: SUCCESS

V3 Combined Logic Database:
  File: data/zepix_combined_v3.db
  Status: OK
  Tables: 5

V6 Price Action Database:
  File: data/zepix_price_action.db
  Status: OK
  Tables: 8

Central System Database:
  File: data/zepix_bot.db
  Status: OK
  Tables: 6

ALL DATABASES INITIALIZED SUCCESSFULLY
============================================================
```

---

## 9. Testing

### Running Database Tests

```bash
# Run all V5 database tests
cd Trading_Bot
python -m pytest tests/test_v5_database_creation.py -v
```

### Test Coverage

The test suite verifies:
- All 3 databases exist
- All expected tables are created
- Required columns are present
- Databases are queryable
- Pre-populated data is correct
- DatabaseService can connect to all databases
- No cross-contamination between V3 and V6

---

## 10. Database Schema Reference

### V3 Tables Summary

| Table | Columns | Indexes |
|-------|---------|---------|
| combined_v3_trades | 35 | 5 |
| v3_profit_bookings | 8 | 0 |
| v3_signals_log | 12 | 0 |
| v3_daily_stats | 9 | 0 |

### V6 Tables Summary

| Table | Columns | Indexes |
|-------|---------|---------|
| price_action_1m_trades | 18 | 2 |
| price_action_5m_trades | 22 | 1 |
| price_action_15m_trades | 17 | 1 |
| price_action_1h_trades | 16 | 1 |
| market_trends | 7 | 1 |
| v6_signals_log | 12 | 0 |
| v6_daily_stats | 8 | 0 |

### Central Tables Summary

| Table | Columns | Indexes |
|-------|---------|---------|
| plugins_registry | 10 | 0 |
| aggregated_trades | 11 | 2 |
| system_config | 3 | 0 |
| system_events | 5 | 0 |
| sync_status | 5 | 0 |

---

## Related Documentation

| Document | Location |
|----------|----------|
| Database Schema Designs | `Updates/v5_hybrid_plugin_architecture/01_PLANNING/09_DATABASE_SCHEMA_DESIGNS.md` |
| V5 Architecture Bible | `Trading_Bot_Documentation/V5_BIBLE/` |
| V3 Plugin Documentation | `Updates/v5_hybrid_plugin_architecture/V3_PLUGIN_DOCUMENTATION_V5/` |
| V6 Plugin Documentation | `Updates/v5_hybrid_plugin_architecture/V6_PLUGIN_DOCUMENTATION_V5/` |

---

**Document Status**: COMPLETE  
**Implementation Status**: VERIFIED  
**Test Status**: 21/21 PASSED
