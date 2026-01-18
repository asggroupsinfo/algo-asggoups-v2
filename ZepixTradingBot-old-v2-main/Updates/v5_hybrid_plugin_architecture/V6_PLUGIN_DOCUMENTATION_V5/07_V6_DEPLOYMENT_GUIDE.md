# V6 Price Action Plugin - Deployment Guide

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Plugin Implementations**: `v6_price_action_5m`, `v6_price_action_15m`, `v6_price_action_1h`

---

## Deployment Overview

This guide covers the complete deployment process for the V6 Price Action Plugin system within the V5 Hybrid Plugin Architecture. V6 uses three timeframe-specific plugins that can be deployed independently or together.

---

## 1. Prerequisites

### 1.1 System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.10+ |
| Memory | 2GB RAM minimum |
| Storage | 500MB for logs |
| Network | Stable internet connection |

### 1.2 Required Services

| Service | Purpose | Status |
|---------|---------|--------|
| MT5 Terminal | Order execution | Required |
| TradingView | Alert source | Required |
| Telegram Bot | Notifications | Required |
| PostgreSQL/SQLite | Trade persistence | Required |

### 1.3 Environment Variables

```bash
# .env file
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_mt5_server

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

DATABASE_URL=sqlite:///trading_bot.db

WEBHOOK_SECRET=your_webhook_secret
WEBHOOK_PORT=5000
```

---

## 2. Installation Steps

### 2.1 Clone Repository

```bash
git clone https://gitlab.com/asggroupsinfo/algo-asggoups-v1.git
cd algo-asggoups-v1/ZepixTradingBot-old-v2-main
```

### 2.2 Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2.3 Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

### 2.4 Initialize Database

```bash
# Run database migrations
python -m Trading_Bot.scripts.init_database
```

---

## 3. Plugin Configuration

### 3.1 Enable V6 Plugins

Edit `config/plugins.json`:

```json
{
  "plugins": {
    "v6_price_action_5m": {
      "enabled": true,
      "shadow_mode": true,
      "priority": 2
    },
    "v6_price_action_15m": {
      "enabled": true,
      "shadow_mode": false,
      "priority": 2
    },
    "v6_price_action_1h": {
      "enabled": true,
      "shadow_mode": false,
      "priority": 2
    }
  }
}
```

### 3.2 Configure V6 5m Plugin

Edit `config/v6_5m_settings.json`:

```json
{
  "plugin_id": "v6_price_action_5m",
  "enabled": true,
  "shadow_mode": true,
  "settings": {
    "min_confidence": "MEDIUM",
    "min_adx": 25,
    "require_trendline_break": true,
    "require_volume_confirmation": true,
    "min_tf_alignment": 4
  },
  "risk_management": {
    "risk_multiplier": 0.5,
    "base_lot": 0.05,
    "max_lot": 0.10
  },
  "dual_orders": {
    "enabled": true,
    "order_a_trailing": true,
    "order_b_profit_booking": true,
    "lot_split_ratio": 0.5
  }
}
```

### 3.3 Configure V6 15m Plugin

Edit `config/v6_15m_settings.json`:

```json
{
  "plugin_id": "v6_price_action_15m",
  "enabled": true,
  "shadow_mode": false,
  "settings": {
    "min_confidence": "MEDIUM",
    "min_adx": 25,
    "require_trendline_break": true,
    "require_volume_confirmation": true,
    "min_tf_alignment": 4
  },
  "risk_management": {
    "risk_multiplier": 1.0,
    "base_lot": 0.10,
    "max_lot": 0.20
  },
  "dual_orders": {
    "enabled": true,
    "order_a_trailing": true,
    "order_b_profit_booking": true,
    "lot_split_ratio": 0.5
  }
}
```

### 3.4 Configure V6 1H Plugin

Edit `config/v6_1h_settings.json`:

```json
{
  "plugin_id": "v6_price_action_1h",
  "enabled": true,
  "shadow_mode": false,
  "settings": {
    "min_confidence": "MEDIUM",
    "min_adx": 20,
    "require_trendline_break": false,
    "require_volume_confirmation": true,
    "min_tf_alignment": 4
  },
  "risk_management": {
    "risk_multiplier": 1.5,
    "base_lot": 0.15,
    "max_lot": 0.30
  },
  "dual_orders": {
    "enabled": true,
    "order_a_trailing": true,
    "order_b_profit_booking": true,
    "lot_split_ratio": 0.5
  }
}
```

---

## 4. TradingView Setup

### 4.1 Add Pine Script to Chart

1. Open TradingView
2. Go to Pine Editor
3. Paste `Signals_and_Overlays_V6_Enhanced_Build.pine`
4. Click "Add to Chart"
5. Configure indicator settings

### 4.2 Create Alerts for Each Timeframe

**5m Alert**:
1. Switch chart to 5m timeframe
2. Right-click → Add Alert
3. Configure:
   - **Condition**: Signals and Overlays V6 Enhanced → Any alert() function call
   - **Alert name**: V6 5m Alert
   - **Webhook URL**: `https://your-server.com/webhook/tradingview`
   - **Message**: `{{alert.message}}`

**15m Alert**:
1. Switch chart to 15m timeframe
2. Create alert with same settings
3. Name: V6 15m Alert

**1H Alert**:
1. Switch chart to 1H timeframe
2. Create alert with same settings
3. Name: V6 1H Alert

### 4.3 Alert Settings

| Setting | Value |
|---------|-------|
| Condition | Any alert() function call |
| Options | Once Per Bar Close |
| Expiration | Open-ended |
| Alert actions | Webhook URL |

---

## 5. Webhook Server Setup

### 5.1 Start Webhook Server

```bash
# Development mode
python -m Trading_Bot.webhook.server

# Production mode with gunicorn
gunicorn Trading_Bot.webhook.server:app -w 4 -b 0.0.0.0:5000
```

### 5.2 Verify Webhook

```bash
# Test V6 webhook endpoint
curl -X POST http://localhost:5000/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{"type":"entry_v6","signal_type":"Breakout_Entry","symbol":"EURUSD","tf":"15"}'
```

---

## 6. Bot Startup

### 6.1 Start Trading Bot

```bash
# Start main bot
python -m Trading_Bot.main

# Or with specific config
python -m Trading_Bot.main --config config/production.json
```

### 6.2 Verify Plugin Registration

Check logs for:
```
[INFO] Plugin Registry: Registering plugin v6_price_action_5m
[INFO] V6PriceAction5mPlugin: Initialized with shadow_mode=True
[INFO] Plugin Registry: Registering plugin v6_price_action_15m
[INFO] V6PriceAction15mPlugin: Initialized with shadow_mode=False
[INFO] Plugin Registry: Registering plugin v6_price_action_1h
[INFO] V6PriceAction1hPlugin: Initialized with shadow_mode=False
[INFO] Plugin Registry: All V6 plugins registered and ready
```

### 6.3 Verify MT5 Connection

Check logs for:
```
[INFO] MT5 Connection: Connected to server
[INFO] MT5 Connection: Account balance: $10,000.00
[INFO] MT5 Connection: Ready for trading
```

---

## 7. Shadow Mode Deployment

### 7.1 Recommended Deployment Strategy

Deploy V6 plugins in phases:

**Phase 1: All Shadow Mode**
```json
{
  "v6_price_action_5m": { "shadow_mode": true },
  "v6_price_action_15m": { "shadow_mode": true },
  "v6_price_action_1h": { "shadow_mode": true }
}
```

**Phase 2: Enable 15m (Most Tested)**
```json
{
  "v6_price_action_5m": { "shadow_mode": true },
  "v6_price_action_15m": { "shadow_mode": false },
  "v6_price_action_1h": { "shadow_mode": true }
}
```

**Phase 3: Enable 1H**
```json
{
  "v6_price_action_5m": { "shadow_mode": true },
  "v6_price_action_15m": { "shadow_mode": false },
  "v6_price_action_1h": { "shadow_mode": false }
}
```

**Phase 4: Enable 5m (Most Aggressive)**
```json
{
  "v6_price_action_5m": { "shadow_mode": false },
  "v6_price_action_15m": { "shadow_mode": false },
  "v6_price_action_1h": { "shadow_mode": false }
}
```

### 7.2 Shadow Mode Logs

```
[INFO] [SHADOW] V6 15m Signal received: entry_v6 | Breakout_Entry | EURUSD
[INFO] [SHADOW] Would validate: confidence=HIGH, adx=32.5
[INFO] [SHADOW] Would create dual orders: A=0.05, B=0.05
[INFO] [SHADOW] Would set SL: 1.08200, TP: 1.08800
```

---

## 8. Production Checklist

### 8.1 Pre-Deployment

- [ ] All environment variables configured
- [ ] Database initialized and migrated
- [ ] MT5 connection tested
- [ ] Telegram bot token verified
- [ ] Webhook endpoint accessible
- [ ] SSL certificate valid
- [ ] Shadow mode tested for all 3 plugins

### 8.2 Deployment

- [ ] V6 5m plugin configured (shadow mode recommended initially)
- [ ] V6 15m plugin configured
- [ ] V6 1H plugin configured
- [ ] Risk parameters reviewed for each plugin
- [ ] Lot sizes appropriate for account
- [ ] Confidence thresholds set appropriately

### 8.3 Post-Deployment

- [ ] First V6 signal received and processed
- [ ] First V6 trade executed successfully
- [ ] Telegram notifications working
- [ ] Logs being written correctly
- [ ] No errors in error log
- [ ] TrendManager updating correctly

---

## 9. Monitoring

### 9.1 Log Files

| Log File | Content |
|----------|---------|
| `logs/trading_bot.log` | Main bot logs |
| `logs/v6_5m_plugin.log` | V6 5m plugin logs |
| `logs/v6_15m_plugin.log` | V6 15m plugin logs |
| `logs/v6_1h_plugin.log` | V6 1H plugin logs |
| `logs/trades.log` | Trade execution logs |
| `logs/errors.log` | Error logs |

### 9.2 Health Check Endpoint

```bash
# Check bot health
curl http://localhost:5000/health

# Expected response
{
  "status": "healthy",
  "plugins": {
    "v6_price_action_5m": {
      "enabled": true,
      "shadow_mode": true,
      "signals_processed": 15,
      "trades_executed": 0
    },
    "v6_price_action_15m": {
      "enabled": true,
      "shadow_mode": false,
      "signals_processed": 28,
      "trades_executed": 12
    },
    "v6_price_action_1h": {
      "enabled": true,
      "shadow_mode": false,
      "signals_processed": 8,
      "trades_executed": 5
    }
  },
  "mt5_connected": true,
  "telegram_connected": true
}
```

### 9.3 Telegram Commands

| Command | Description |
|---------|-------------|
| `/status` | Get bot status |
| `/positions` | List open positions |
| `/trades` | Recent trade history |
| `/plugin v6_5m` | V6 5m plugin status |
| `/plugin v6_15m` | V6 15m plugin status |
| `/plugin v6_1h` | V6 1H plugin status |

---

## 10. Rollback Procedure

### 10.1 Disable Individual Plugin

```json
{
  "plugin_id": "v6_price_action_5m",
  "enabled": false
}
```

### 10.2 Disable All V6 Plugins

```json
{
  "v6_price_action_5m": { "enabled": false },
  "v6_price_action_15m": { "enabled": false },
  "v6_price_action_1h": { "enabled": false }
}
```

### 10.3 Close V6 Positions

```bash
# Via Telegram
/closeall v6

# Via command line
python -m Trading_Bot.scripts.close_all --plugin-prefix v6_
```

---

## 11. Troubleshooting

### 11.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No V6 signals received | Webhook not configured | Check TradingView alert settings |
| Wrong plugin receives signal | Timeframe mismatch | Verify tf field in alert |
| Orders not executing | Shadow mode enabled | Disable shadow mode |
| Confidence too low | ADX below threshold | Adjust min_adx setting |
| TrendManager validation fails | Trend conflict | Check TrendManager state |

### 11.2 Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m Trading_Bot.main
```

### 11.3 Test Signal Processing

```bash
# Send test V6 signal
python -m Trading_Bot.scripts.test_signal \
  --type entry_v6 \
  --signal Breakout_Entry \
  --tf 15
```

---

## 12. Maintenance

### 12.1 Daily Tasks

- Check error logs for each V6 plugin
- Verify MT5 connection
- Review open positions by plugin
- Check Telegram notifications

### 12.2 Weekly Tasks

- Review trade performance by plugin
- Compare 5m vs 15m vs 1H performance
- Check disk space for logs
- Review risk parameters

### 12.3 Monthly Tasks

- Full system backup
- Log rotation
- Performance review by plugin
- Configuration audit

---

**Document Status**: COMPLETE  
**Deployment Coverage**: 100%  
**V5 Architecture Compliance**: VERIFIED
