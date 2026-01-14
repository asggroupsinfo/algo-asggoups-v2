# Zepix Trading Bot V5 - User Guide

**Version:** 5.0.0  
**Last Updated:** 2026-01-14  
**Audience:** End Users (Traders)

---

## Welcome to V5 Hybrid Plugin Architecture

The Zepix Trading Bot V5 introduces a revolutionary **Plugin Architecture** that transforms how you interact with and manage your trading strategies. This guide will help you understand and use all the new features.

---

## What's New in V5?

### Key Improvements

The V5 architecture brings several major improvements over V4:

**Plugin-Based Strategies:** Each trading strategy (V3 Combined Logic, V6 Price Action) now runs as an independent plugin. This means you can enable, disable, or configure each strategy separately without affecting others.

**Isolated Databases:** Each plugin has its own database, so performance tracking and trade history are completely separate. No more mixing up which strategy made which trade.

**Health Monitoring:** The bot now monitors itself and can automatically restart unhealthy plugins. You'll get alerts if something goes wrong.

**Hot-Reload Configuration:** Change settings without restarting the bot. Just update the config and reload.

**Better Telegram Interface:** New sticky headers, rate limiting, and organized command menus make controlling the bot easier than ever.

---

## Understanding Plugins

### What is a Plugin?

A plugin is a self-contained trading strategy that runs independently within the bot. Think of it like an app on your phone - you can install multiple apps, and they don't interfere with each other.

### Available Plugins

#### Combined V3 Plugin (`combined_v3`)

This is your original V3 trading logic, now packaged as a plugin. It includes all three combined logics (LOGIC1, LOGIC2, LOGIC3) with the same behavior you're used to.

**Features:**
- 12 signal types from TradingView
- Dual order system (Order A + Order B)
- Multi-timeframe trend validation (4-Pillar MTF)
- Profit booking chains (TP1, TP2, TP3)
- Re-entry systems (SL Hunt, TP Continuation)

**Database:** `data/zepix_combined_v3.db`

#### Price Action V6 Plugins

The V6 Price Action system is split into four timeframe-specific plugins:

**price_action_1m** - 1-Minute scalping signals  
**price_action_5m** - 5-Minute short-term signals  
**price_action_15m** - 15-Minute swing signals  
**price_action_1h** - 1-Hour position signals

Each timeframe plugin processes signals independently with its own entry rules and risk parameters.

**Database:** `data/zepix_price_action.db` (shared by all V6 plugins)

---

## Telegram Commands

### Command Categories

The bot organizes commands into logical categories for easy access:

### 1. Trading Control

| Command | Description | Example |
|---------|-------------|---------|
| `/status` | View bot health and active plugins | Shows all plugin states |
| `/pause` | Pause all trading | Stops new entries |
| `/resume` | Resume trading | Allows new entries |
| `/trades` | View open trades | Lists all positions |
| `/signal_status` | Current signal states | Shows pending signals |

### 2. Plugin Management

| Command | Description | Example |
|---------|-------------|---------|
| `/plugins` | List all plugins | Shows enabled/disabled |
| `/enable_plugin <name>` | Enable a plugin | `/enable_plugin combined_v3` |
| `/disable_plugin <name>` | Disable a plugin | `/disable_plugin price_action_1m` |
| `/plugin_status <name>` | Detailed plugin info | `/plugin_status combined_v3` |
| `/config_reload <name>` | Reload plugin config | `/config_reload combined_v3` |

### 3. Performance & Analytics

| Command | Description | Example |
|---------|-------------|---------|
| `/performance` | Overall P&L summary | Win rate, total profit |
| `/daily_report` | Today's performance | Daily P&L breakdown |
| `/weekly_report` | Week performance | 7-day summary |
| `/plugin_stats` | Per-plugin breakdown | Compare strategies |
| `/pair_report` | Per-symbol stats | XAUUSD, EURUSD, etc. |

### 4. Strategy Control (V3)

| Command | Description | Example |
|---------|-------------|---------|
| `/logic_status` | View LOGIC1/2/3 states | Shows enabled/disabled |
| `/logic1_on` | Enable LOGIC1 | 5-minute signals |
| `/logic1_off` | Disable LOGIC1 | Stop 5-minute |
| `/logic2_on` | Enable LOGIC2 | 15-minute signals |
| `/logic2_off` | Disable LOGIC2 | Stop 15-minute |
| `/logic3_on` | Enable LOGIC3 | 1-hour signals |
| `/logic3_off` | Disable LOGIC3 | Stop 1-hour |

### 5. Risk Management

| Command | Description | Example |
|---------|-------------|---------|
| `/stats` | Current risk settings | Tier, limits, lot size |
| `/set_risk <percent>` | Set risk percentage | `/set_risk 1.5` |
| `/set_max_lot <size>` | Set maximum lot | `/set_max_lot 1.0` |
| `/daily_limit` | Check daily loss limit | Shows remaining |
| `/reset_daily` | Reset daily counters | Start fresh |

### 6. Health Monitoring

| Command | Description | Example |
|---------|-------------|---------|
| `/health` | System health check | All components status |
| `/version` | Plugin versions | Shows all versions |
| `/upgrade <plugin>` | Upgrade plugin | `/upgrade combined_v3` |
| `/rollback <plugin>` | Rollback plugin | `/rollback combined_v3` |

### 7. Emergency Controls

| Command | Description | Example |
|---------|-------------|---------|
| `/emergency_stop` | STOP ALL TRADING | Closes all, disables all |
| `/close_all` | Close all positions | Immediate close |
| `/panic` | Quick panic button | Same as emergency_stop |

---

## Using the Plugin System

### Checking Plugin Status

To see which plugins are active:

```
Send: /plugins
```

Response:
```
PLUGIN STATUS

combined_v3: ENABLED
  Version: 1.0.0
  Trades Today: 5
  P&L: +$250.00

price_action_1m: DISABLED
price_action_5m: ENABLED
  Version: 1.0.0
  Trades Today: 2
  P&L: +$75.00

price_action_15m: ENABLED
price_action_1h: DISABLED
```

### Enabling/Disabling Plugins

To enable a plugin:
```
Send: /enable_plugin price_action_1m
```

To disable a plugin:
```
Send: /disable_plugin price_action_1m
```

### Viewing Plugin Performance

To see detailed stats for a specific plugin:
```
Send: /plugin_stats combined_v3
```

Response:
```
COMBINED_V3 STATISTICS

Today:
  Trades: 5
  Win Rate: 80%
  P&L: +$250.00

This Week:
  Trades: 23
  Win Rate: 74%
  P&L: +$1,250.00

This Month:
  Trades: 89
  Win Rate: 71%
  P&L: +$4,500.00
```

---

## Configuration Guide

### Plugin Configuration Files

Each plugin has its own configuration file:

**Combined V3:** `src/logic_plugins/combined_v3/config.json`  
**Price Action 1M:** `src/logic_plugins/price_action_1m/config.json`  
**Price Action 5M:** `src/logic_plugins/price_action_5m/config.json`  
**Price Action 15M:** `src/logic_plugins/price_action_15m/config.json`  
**Price Action 1H:** `src/logic_plugins/price_action_1h/config.json`

### Common Configuration Options

```json
{
    "plugin_id": "combined_v3",
    "version": "1.0.0",
    "enabled": true,
    "settings": {
        "max_lot_size": 1.0,
        "risk_percentage": 1.5,
        "daily_loss_limit": 500.0,
        "supported_symbols": ["XAUUSD", "EURUSD", "GBPUSD"],
        "shadow_mode": false
    }
}
```

**enabled:** Whether the plugin processes signals  
**max_lot_size:** Maximum lot size per trade  
**risk_percentage:** Risk per trade as % of balance  
**daily_loss_limit:** Maximum daily loss before auto-pause  
**supported_symbols:** Which symbols this plugin trades  
**shadow_mode:** If true, logs trades but doesn't execute

### Hot-Reload Configuration

After editing a config file, reload without restart:

```
Send: /config_reload combined_v3
```

The bot will validate the new config and apply changes immediately.

---

## Understanding Notifications

### Entry Alert Format

When a trade is placed, you'll receive:

```
ENTRY - combined_v3

Symbol: XAUUSD
Direction: BUY
Lot: 0.12 (Order A) + 0.24 (Order B)
Entry: 2030.50
SL: 2028.00 (-25 pips)
TP1: 2032.50 (+20 pips)
TP2: 2035.00 (+45 pips)
TP3: 2040.00 (+95 pips)
Time: 2026-01-14 14:30:15 IST
```

### Exit Alert Format

When a trade closes:

```
EXIT - combined_v3

Symbol: XAUUSD
Ticket: #12345
Direction: BUY -> CLOSED
Exit: 2032.50
Profit: +20 pips (+$200.00)
Duration: 2h 15m
Reason: TP1 Hit
```

### Profit Booking Alert

When partial profits are taken:

```
PROFIT BOOKING - combined_v3

Symbol: XAUUSD
Ticket: #12345
Level: TP1
Closed: 50% (0.06 lots)
Profit: +$100.00
Remaining: 0.06 lots
New SL: Breakeven
```

### Health Alert

If something goes wrong:

```
HEALTH ALERT

Plugin: combined_v3
Status: UNHEALTHY
Issue: Database connection timeout
Action: Auto-restart attempted
Result: RECOVERED
```

---

## Safety Features

### Daily Loss Limit

Each plugin has an independent daily loss limit. When reached:

1. Plugin automatically pauses trading
2. You receive a notification
3. Other plugins continue normally
4. Resets at midnight (configurable timezone)

To check remaining limit:
```
Send: /daily_limit combined_v3
```

### Shadow Mode

Test new strategies without real money:

```json
{
    "settings": {
        "shadow_mode": true
    }
}
```

In shadow mode:
- Signals are processed normally
- Trades are logged to database
- NO real orders are placed
- Perfect for testing

### Emergency Stop

If you need to stop everything immediately:

```
Send: /emergency_stop
```

This will:
1. Close ALL open positions across ALL plugins
2. Disable ALL plugins
3. Pause the entire bot
4. Require manual re-activation

---

## Performance Tracking

### Daily Report

Get a summary of today's trading:

```
Send: /daily_report
```

Response:
```
DAILY REPORT - 2026-01-14

Overall:
  Total Profit: +$350.50
  Win Rate: 75.0%
  Total Trades: 12

Per Plugin:
  combined_v3: +$275.00 (8 trades, 75% win)
  price_action_5m: +$75.50 (4 trades, 75% win)

Best Trade: XAUUSD +$120.00
Worst Trade: EURUSD -$45.00
```

### Weekly Report

```
Send: /weekly_report
```

Includes:
- 7-day P&L trend
- Win rate by day
- Best/worst performing days
- Plugin comparison

### Export Trade History

```
Send: /export_trades
```

Downloads a CSV file with all trades for analysis.

---

## Troubleshooting

### Bot Not Responding to Alerts

1. Check if plugin is enabled:
   ```
   /plugin_status combined_v3
   ```

2. Check if daily limit was hit:
   ```
   /daily_limit combined_v3
   ```

3. Check bot health:
   ```
   /health
   ```

4. Check logs:
   ```
   tail -f logs/bot.log
   ```

### Wrong Lot Size

Verify your configuration:
```json
{
    "settings": {
        "risk_percentage": 1.5,
        "max_lot_size": 1.0
    }
}
```

Then reload:
```
/config_reload combined_v3
```

### Plugin Shows UNHEALTHY

1. Check the health details:
   ```
   /health
   ```

2. Try manual restart:
   ```
   /disable_plugin combined_v3
   /enable_plugin combined_v3
   ```

3. Check database:
   ```
   ls -la data/zepix_combined_v3.db
   ```

### Not Receiving Notifications

1. Verify Telegram bot tokens in config
2. Check you're in the correct chat
3. Test with:
   ```
   /status
   ```
   Should respond immediately

---

## Best Practices

### 1. Monitor Daily

Check your daily report every evening to understand performance trends.

### 2. Use Shadow Mode First

When enabling a new plugin or changing settings, use shadow mode for at least a week to verify behavior.

### 3. Set Appropriate Limits

Configure daily loss limits based on your risk tolerance. Recommended: 2-5% of account balance.

### 4. Keep Plugins Updated

Check for updates regularly:
```
/version
```

### 5. Backup Configurations

Before making changes, backup your config files:
```bash
cp config/config.json config/config.json.backup
```

### 6. Review Losing Trades

Use the analytics commands to understand why trades lost and adjust accordingly.

---

## Quick Reference

### Most Used Commands

| Command | Purpose |
|---------|---------|
| `/status` | System health |
| `/plugins` | Plugin states |
| `/daily_report` | Today's P&L |
| `/enable_plugin <name>` | Turn on strategy |
| `/disable_plugin <name>` | Turn off strategy |
| `/emergency_stop` | Stop everything |

### File Locations

| File | Purpose |
|------|---------|
| `config/config.json` | Main configuration |
| `src/logic_plugins/<plugin>/config.json` | Plugin settings |
| `data/zepix_combined_v3.db` | V3 trade database |
| `data/zepix_price_action.db` | V6 trade database |
| `logs/bot.log` | Application logs |

### Support

For issues or questions:
- Check this guide first
- Review the logs
- Contact support with screenshots and log excerpts

---

## FAQ

**Q: Can I run multiple plugins at once?**  
A: Yes! Each plugin runs independently. You can have combined_v3 and price_action_5m both active.

**Q: Will plugins interfere with each other?**  
A: No. Each plugin has its own database and configuration. They don't share state.

**Q: How do I know which plugin placed a trade?**  
A: Check the MT5 order comment or the Telegram notification - both show the plugin name.

**Q: What happens if the bot crashes?**  
A: Open trades remain in MT5. When the bot restarts, it reconnects and continues monitoring.

**Q: Can I add my own plugin?**  
A: Yes! See the Developer Guide for instructions on creating custom plugins.

**Q: How do I migrate from V4?**  
A: See the Migration Guide (MIGRATION_GUIDE.md) for step-by-step instructions.

---

**Document Version:** 5.0.0  
**Last Updated:** 2026-01-14
