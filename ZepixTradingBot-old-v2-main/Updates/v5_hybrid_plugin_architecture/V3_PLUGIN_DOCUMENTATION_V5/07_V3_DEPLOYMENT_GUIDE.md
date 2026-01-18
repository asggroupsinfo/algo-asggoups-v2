# V3 Combined Logic Plugin - Deployment Guide

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-18  
**Plugin Implementation**: `src/logic_plugins/v3_combined/plugin.py`

---

## Deployment Overview

This guide covers the complete deployment process for the V3 Combined Logic Plugin within the V5 Hybrid Plugin Architecture.

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
# OR
DATABASE_URL=postgresql://user:pass@localhost/trading_bot

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
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

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

### 3.1 Enable V3 Plugin

Edit `config/plugins.json`:

```json
{
  "plugins": {
    "v3_combined": {
      "enabled": true,
      "shadow_mode": false,
      "priority": 1
    }
  }
}
```

### 3.2 Configure V3 Settings

Edit `config/v3_settings.json`:

```json
{
  "plugin_id": "v3_combined",
  "enabled": true,
  "shadow_mode": false,
  "settings": {
    "bypass_trend_check_for_v3_entries": true,
    "mtf_pillars_only": ["15m", "1h", "4h", "1d"],
    "min_consensus_score": 5,
    "aggressive_reversal_signals": [
      "Liquidity_Trap_Reversal",
      "Screener_Full_Bullish",
      "Screener_Full_Bearish"
    ],
    "conservative_exit_signals": [
      "Bullish_Exit",
      "Bearish_Exit"
    ]
  },
  "risk_management": {
    "logic1_multiplier": 0.5,
    "logic2_multiplier": 1.0,
    "logic3_multiplier": 1.5,
    "max_position_multiplier": 1.0,
    "base_lot_logic1": 0.05,
    "base_lot_logic2": 0.10,
    "base_lot_logic3": 0.15
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
3. Paste `ZEPIX_ULTIMATE_BOT_v3.0_FINAL.pine`
4. Click "Add to Chart"
5. Configure indicator settings

### 4.2 Create Alert

1. Right-click on chart
2. Select "Add Alert"
3. Configure:
   - **Condition**: ZEPIX ULTIMATE BOT v3.0 → Any alert() function call
   - **Alert name**: V3 Consolidated Alert
   - **Webhook URL**: `https://your-server.com/webhook/tradingview`
   - **Message**: `{{alert.message}}`

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
# Test webhook endpoint
curl -X POST http://localhost:5000/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{"type":"entry_v3","signal_type":"test","symbol":"EURUSD"}'
```

### 5.3 Configure Nginx (Production)

```nginx
server {
    listen 443 ssl;
    server_name your-server.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /webhook/tradingview {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
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
[INFO] Plugin Registry: Registering plugin v3_combined
[INFO] V3CombinedPlugin: Initialized with shadow_mode=False
[INFO] V3CombinedPlugin: ServiceAPI injected successfully
[INFO] Plugin Registry: v3_combined registered and ready
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

### 7.1 Enable Shadow Mode

For testing without real trades:

```json
{
  "plugin_id": "v3_combined",
  "enabled": true,
  "shadow_mode": true
}
```

### 7.2 Shadow Mode Behavior

- Signals are processed normally
- Validation and routing work as expected
- **NO orders are placed**
- All actions are logged with `[SHADOW]` prefix

### 7.3 Shadow Mode Logs

```
[INFO] [SHADOW] V3 Signal received: entry_v3 | Institutional_Launchpad | EURUSD
[INFO] [SHADOW] Would route to: LOGIC2
[INFO] [SHADOW] Would create dual orders: A=0.04, B=0.04
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
- [ ] Shadow mode tested successfully

### 8.2 Deployment

- [ ] Plugin enabled in config
- [ ] Shadow mode disabled (for live trading)
- [ ] Risk parameters reviewed
- [ ] Lot sizes appropriate for account
- [ ] Stop loss levels verified
- [ ] Take profit levels verified

### 8.3 Post-Deployment

- [ ] First signal received and processed
- [ ] First trade executed successfully
- [ ] Telegram notifications working
- [ ] Logs being written correctly
- [ ] No errors in error log

---

## 9. Monitoring

### 9.1 Log Files

| Log File | Content |
|----------|---------|
| `logs/trading_bot.log` | Main bot logs |
| `logs/v3_plugin.log` | V3 plugin specific logs |
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
    "v3_combined": {
      "enabled": true,
      "shadow_mode": false,
      "signals_processed": 42,
      "trades_executed": 15
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
| `/plugin v3` | V3 plugin status |

---

## 10. Rollback Procedure

### 10.1 Disable Plugin

```json
{
  "plugin_id": "v3_combined",
  "enabled": false
}
```

### 10.2 Close All Positions

```bash
# Via Telegram
/closeall v3

# Via command line
python -m Trading_Bot.scripts.close_all --plugin v3_combined
```

### 10.3 Restore Previous Version

```bash
# Checkout previous version
git checkout v1.0.0

# Restart bot
systemctl restart trading_bot
```

---

## 11. Troubleshooting

### 11.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No signals received | Webhook not configured | Check TradingView alert settings |
| Orders not executing | MT5 disconnected | Restart MT5 terminal |
| Telegram not working | Invalid token | Verify TELEGRAM_BOT_TOKEN |
| Plugin not loading | Config error | Check plugins.json syntax |

### 11.2 Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m Trading_Bot.main
```

### 11.3 Test Signal Processing

```bash
# Send test signal
python -m Trading_Bot.scripts.test_signal --type entry_v3 --signal Institutional_Launchpad
```

---

## 12. Maintenance

### 12.1 Daily Tasks

- Check error logs
- Verify MT5 connection
- Review open positions
- Check Telegram notifications

### 12.2 Weekly Tasks

- Review trade performance
- Check disk space for logs
- Update Pine Script if needed
- Review risk parameters

### 12.3 Monthly Tasks

- Full system backup
- Log rotation
- Performance review
- Configuration audit

---

**Document Status**: COMPLETE  
**Deployment Coverage**: 100%  
**V5 Architecture Compliance**: VERIFIED
