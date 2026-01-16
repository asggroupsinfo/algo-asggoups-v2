# Zepix Trading Bot - V4 to V5 Migration Guide

**Version:** 1.0.0  
**Last Updated:** 2026-01-14  
**Audience:** Users upgrading from V4 to V5

---

## Overview

This guide walks you through upgrading your Zepix Trading Bot from V4 to the new V5 Hybrid Plugin Architecture. The migration process is designed to be safe and reversible, with your existing data preserved.

---

## Before You Begin

### Prerequisites

Before starting the migration, ensure you have:

1. **Backup of V4 Data**
   ```bash
   cp data/trading_bot.db data/trading_bot.db.v4_backup
   cp config/config.json config/config.json.v4_backup
   ```

2. **No Open Trades**
   - Close all open positions before migrating
   - Or note them down to manually re-enter after migration

3. **Python 3.9+**
   ```bash
   python --version
   # Should show Python 3.9 or higher
   ```

4. **Updated Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### What Changes in V5

| Aspect | V4 | V5 |
|--------|----|----|
| Architecture | Monolithic | Plugin-based |
| Database | Single `trading_bot.db` | Per-plugin databases |
| Configuration | Single `config.json` | Main config + plugin configs |
| Telegram | Single bot | 3-bot system (optional) |
| Strategies | Hardcoded | Loadable plugins |

---

## Migration Steps

### Step 1: Stop the V4 Bot

Ensure the V4 bot is completely stopped:

```bash
# If running as a service
sudo systemctl stop zepix-bot

# Or if running in terminal
# Press Ctrl+C to stop
```

Verify no processes are running:
```bash
ps aux | grep python | grep main.py
```

### Step 2: Backup Everything

Create a complete backup:

```bash
# Create backup directory
mkdir -p backups/v4_$(date +%Y%m%d)

# Backup database
cp data/trading_bot.db backups/v4_$(date +%Y%m%d)/

# Backup configuration
cp config/config.json backups/v4_$(date +%Y%m%d)/

# Backup logs (optional)
cp -r logs/ backups/v4_$(date +%Y%m%d)/
```

### Step 3: Update the Codebase

Pull the latest V5 code:

```bash
git fetch origin
git checkout main
git pull origin main
```

Or if you received a V5 package:
```bash
# Extract to a new directory first
unzip zepix-bot-v5.zip -d zepix-bot-v5-new

# Compare and merge carefully
```

### Step 4: Install New Dependencies

Install V5 dependencies:

```bash
pip install -r requirements.txt
```

For development tools (optional):
```bash
pip install -r requirements.txt[dev]
# Or
pip install black flake8 mypy pytest pre-commit
```

### Step 5: Migrate Trade History

Use the built-in migration tool to transfer your V4 trade history to V5:

```python
# Run in Python shell or create a script
from src.utils.data_migration_tool import create_migration_tool

# Create migration tool
tool = create_migration_tool(
    source_db="data/trading_bot.db",
    target_dir="data"
)

# Check V4 data summary
summary = tool.get_v4_summary()
print(f"Found {summary['total_trades']} trades to migrate")
print(f"Total P&L: ${summary['total_pnl']:.2f}")

# Dry run first (no changes made)
result = tool.migrate_to_v3_plugin(dry_run=True)
print(tool.format_migration_report(result))

# If dry run looks good, perform actual migration
if result.status.value == "completed":
    result = tool.migrate_to_v3_plugin(dry_run=False)
    print(tool.format_migration_report(result))
```

### Step 6: Update Configuration

#### 6.1 Main Configuration

Your V4 `config.json` needs to be updated for V5. Here's a comparison:

**V4 Configuration:**
```json
{
    "mt5": {
        "login": 12345678,
        "password": "your_password",
        "server": "YourBroker-Server"
    },
    "telegram": {
        "token": "your_bot_token",
        "chat_id": "your_chat_id"
    },
    "trading": {
        "risk_percentage": 1.5,
        "max_lot_size": 1.0,
        "daily_loss_limit": 500
    }
}
```

**V5 Configuration:**
```json
{
    "mt5": {
        "login": 12345678,
        "password": "your_password",
        "server": "YourBroker-Server"
    },
    "telegram": {
        "controller_bot": {
            "token": "your_controller_token",
            "chat_id": "your_chat_id"
        },
        "notification_bot": {
            "token": "your_notification_token",
            "chat_id": "your_chat_id"
        },
        "analytics_bot": {
            "token": "your_analytics_token",
            "chat_id": "your_chat_id"
        }
    },
    "plugins": {
        "combined_v3": {
            "enabled": true,
            "config_path": "src/logic_plugins/combined_v3/config.json"
        },
        "price_action_1m": {
            "enabled": false,
            "config_path": "src/logic_plugins/price_action_1m/config.json"
        }
    }
}
```

**Note:** If you only have one Telegram bot, you can use the same token for all three. The 3-bot system is optional.

#### 6.2 Plugin Configuration

Create or verify plugin configurations:

**Combined V3 Plugin** (`src/logic_plugins/combined_v3/config.json`):
```json
{
    "plugin_id": "combined_v3",
    "version": "1.0.0",
    "enabled": true,
    "metadata": {
        "name": "Combined V3 Logic",
        "description": "Original V3 combined trading logic",
        "author": "ASG Groups"
    },
    "settings": {
        "max_lot_size": 1.0,
        "risk_percentage": 1.5,
        "daily_loss_limit": 500.0,
        "supported_symbols": ["XAUUSD", "EURUSD", "GBPUSD"],
        "shadow_mode": false,
        "logic1_enabled": true,
        "logic2_enabled": true,
        "logic3_enabled": true
    }
}
```

### Step 7: Initialize V5 Databases

The V5 system will create new databases on first run. You can also initialize them manually:

```bash
# Start the bot briefly to initialize databases
python src/main.py &
sleep 10
kill %1

# Verify databases were created
ls -la data/
# Should show:
# - zepix_combined_v3.db
# - zepix_price_action.db (if V6 plugins enabled)
```

### Step 8: Verify Migration

Run the verification script:

```python
from src.utils.data_migration_tool import create_migration_tool

tool = create_migration_tool(
    source_db="data/trading_bot.db",
    target_dir="data"
)

# Verify data integrity
result = tool.verify_integrity(
    source_db="data/trading_bot.db",
    target_db="data/zepix_combined_v3.db"
)

print(f"Records match: {result['records_match']}")
print(f"P&L match: {result['pnl_match']}")
print(f"Source total: ${result['source_pnl']:.2f}")
print(f"Target total: ${result['target_pnl']:.2f}")
```

### Step 9: Start V5 Bot

Start the V5 bot:

```bash
python src/main.py
```

Expected output:
```
[INFO] MT5 connected
[INFO] Database initialized
[INFO] Plugin registry loaded
[INFO] Plugin 'combined_v3' initialized
[INFO] Telegram bots started
[INFO] Bot is running...
```

### Step 10: Verify Operation

Send test commands via Telegram:

```
/status
/plugins
/health
```

All should respond correctly.

---

## Configuration Mapping

### Trading Settings

| V4 Setting | V5 Location | Notes |
|------------|-------------|-------|
| `risk_percentage` | Plugin config `settings.risk_percentage` | Per-plugin now |
| `max_lot_size` | Plugin config `settings.max_lot_size` | Per-plugin now |
| `daily_loss_limit` | Plugin config `settings.daily_loss_limit` | Per-plugin now |
| `supported_symbols` | Plugin config `settings.supported_symbols` | Per-plugin now |

### Telegram Settings

| V4 Setting | V5 Location | Notes |
|------------|-------------|-------|
| `telegram.token` | `telegram.controller_bot.token` | Can use same token |
| `telegram.chat_id` | `telegram.controller_bot.chat_id` | Same for all bots |

### Strategy Settings

| V4 Setting | V5 Location | Notes |
|------------|-------------|-------|
| `logic1_enabled` | Plugin config `settings.logic1_enabled` | In combined_v3 |
| `logic2_enabled` | Plugin config `settings.logic2_enabled` | In combined_v3 |
| `logic3_enabled` | Plugin config `settings.logic3_enabled` | In combined_v3 |

---

## Rollback Procedure

If you need to revert to V4:

### Step 1: Stop V5 Bot

```bash
# Stop the V5 bot
sudo systemctl stop zepix-bot
# Or Ctrl+C if running in terminal
```

### Step 2: Restore V4 Files

```bash
# Restore database
cp backups/v4_YYYYMMDD/trading_bot.db data/

# Restore configuration
cp backups/v4_YYYYMMDD/config.json config/
```

### Step 3: Checkout V4 Code

```bash
git checkout v4-stable
# Or restore from your V4 backup
```

### Step 4: Start V4 Bot

```bash
python src/main.py
```

---

## Troubleshooting

### Migration Tool Errors

**Error: "Source database not found"**
```
Solution: Verify the path to trading_bot.db
ls -la data/trading_bot.db
```

**Error: "Schema mismatch"**
```
Solution: Your V4 database may have a different schema.
Check the trades table structure:
sqlite3 data/trading_bot.db ".schema trades"
```

**Error: "P&L mismatch after migration"**
```
Solution: Some trades may have NULL values.
Run with verbose logging to identify issues:
tool.migrate_to_v3_plugin(dry_run=True, verbose=True)
```

### Bot Startup Errors

**Error: "Plugin not found"**
```
Solution: Verify plugin directory exists:
ls -la src/logic_plugins/combined_v3/
```

**Error: "Config validation failed"**
```
Solution: Check JSON syntax in config files:
python -m json.tool src/logic_plugins/combined_v3/config.json
```

**Error: "Database locked"**
```
Solution: Ensure no other process is using the database:
fuser data/zepix_combined_v3.db
```

### Telegram Errors

**Error: "Bot token invalid"**
```
Solution: Verify token in config.json
Test with: curl https://api.telegram.org/bot<TOKEN>/getMe
```

**Error: "Chat not found"**
```
Solution: Ensure chat_id is correct
Send /start to the bot first
```

---

## Post-Migration Checklist

After migration, verify:

- [ ] Bot starts without errors
- [ ] `/status` command responds
- [ ] `/plugins` shows combined_v3 enabled
- [ ] `/health` shows all green
- [ ] Trade history appears in `/performance`
- [ ] New trades are logged correctly
- [ ] Notifications are received
- [ ] Daily reports generate correctly

---

## Getting Help

If you encounter issues:

1. **Check Logs**
   ```bash
   tail -f logs/bot.log
   ```

2. **Verify Configuration**
   ```bash
   python -c "import json; json.load(open('config/config.json'))"
   ```

3. **Test Database**
   ```bash
   sqlite3 data/zepix_combined_v3.db "SELECT COUNT(*) FROM combined_v3_trades;"
   ```

4. **Contact Support**
   - Include error messages
   - Include relevant log excerpts
   - Describe steps taken

---

## Appendix: Database Schema Changes

### V4 Trades Table (32 columns)

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    trade_id TEXT,
    symbol TEXT,
    direction TEXT,
    lot_size REAL,
    entry_price REAL,
    exit_price REAL,
    sl_price REAL,
    tp_price REAL,
    pnl REAL,
    status TEXT,
    entry_time TEXT,
    exit_time TEXT,
    ...
);
```

### V5 Combined V3 Trades Table (75 columns)

```sql
CREATE TABLE combined_v3_trades (
    id INTEGER PRIMARY KEY,
    mt5_ticket INTEGER,
    symbol TEXT,
    trade_type TEXT,
    lot_size REAL,
    entry_price REAL,
    exit_price REAL,
    smart_sl REAL,
    tp1_price REAL,
    tp2_price REAL,
    tp3_price REAL,
    profit_dollars REAL,
    profit_pips REAL,
    status TEXT,
    entry_time TEXT,
    exit_time TEXT,
    plugin_id TEXT,
    logic_type TEXT,
    consensus_score INTEGER,
    ...
);
```

### Column Mapping

| V4 Column | V5 Column | Transformation |
|-----------|-----------|----------------|
| `trade_id` | `mt5_ticket` | Convert to integer |
| `direction` | `trade_type` | Direct copy |
| `pnl` | `profit_dollars` | Direct copy |
| `sl_price` | `smart_sl` | Direct copy |
| `status` | `status` | Map: "CLOSED" -> "closed" |
| `entry_time` | `entry_time` | Direct copy |
| `exit_time` | `exit_time` | Direct copy |

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-01-14
