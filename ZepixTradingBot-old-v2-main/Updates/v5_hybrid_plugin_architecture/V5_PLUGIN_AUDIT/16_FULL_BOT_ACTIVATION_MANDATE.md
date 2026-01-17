# 🔥 FULL BOT ACTIVATION MANDATE (NO EXCUSES)

**Mandate ID:** 16_FULL_BOT_ACTIVATION_MANDATE  
**Date:** 2026-01-17  
**Priority:** 🔴 **CRITICAL - ZERO TOLERANCE**  
**Status:** **PENDING EXECUTION**

---

## 🎯 OBJECTIVE: RUN THE COMPLETE BOT (NOT JUST WEBHOOK)

Devin's previous attempt (Mandate 15) was **INCOMPLETE**. He only started the webhook server.

**THIS TIME:** Start the **FULL TRADING BOT** with ALL components active:
- ✅ MT5 Connection (Paper/Demo Account)
- ✅ Telegram Bot (Interactive Commands)
- ✅ Trading Engine (Signal Processing)
- ✅ Session Manager (Time-based Rules)
- ✅ V3 Plugin (Logic Loaded)
- ✅ Database (Tracking Active)

---

## 📋 EXECUTION STEPS (MANDATORY)

### STEP 1: ENVIRONMENT SETUP
1. **Create `.env` file** in `Trading_Bot/` with these settings:
   ```env
   # MT5 Configuration (Use DEMO account)
   MT5_LOGIN=YOUR_DEMO_ACCOUNT
   MT5_PASSWORD=YOUR_DEMO_PASSWORD
   MT5_SERVER=MetaQuotes-Demo
   
   # Telegram Configuration
   TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
   TELEGRAM_CHAT_ID=YOUR_CHAT_ID
   
   # Database
   DATABASE_PATH=data/zepix_combined.db
   
   # Mode
   TRADING_MODE=SHADOW
   ```

2. **Verify MT5 Installation:**
   - If on Windows: Ensure MT5 Terminal is installed
   - If on Linux/Cloud: Use MetaTrader5 Python library in virtual display mode

### STEP 2: START THE FULL BOT
**Command:**
```bash
cd Trading_Bot
python scripts/start_bot_standalone.py --full-mode
```

**OR (if no --full-mode flag exists):**
```bash
cd Trading_Bot/src
python -m main
```

**Expected Startup Logs (ALL MUST APPEAR):**
```
✅ Zepix Trading Bot V5 Started
✅ Database Initialized: zepix_combined.db
✅ MT5 Connected: Demo Account [12345678]
✅ Session Manager Loaded (Timezone: Asia/Kolkata)
✅ V3 Plugin Registered (combinedlogic-1/2/3)
✅ Trading Engine Ready
✅ Telegram Bot Started: @Algo_Asg_Controller_bot
✅ Webhook Server Running: http://0.0.0.0:5000
```

**If ANY component fails to load → FIX IT before proceeding.**

---

### STEP 3: TELEGRAM INTERACTIVE TEST
1. **Send `/start` to the bot on Telegram**
2. **Verify Response:**
   - Bot sends Main Menu with buttons
   - Buttons are clickable
   - Each button triggers a response

3. **Test Key Commands:**
   - `/status` → Should show System Status (CPU, RAM, Active Session)
   - Click **"Dashboard"** → Should show Trading Dashboard
   - Click **"Active Trades"** → Should show "No Active Trades" (if none)

**PROOF REQUIRED:** Video recording showing:
- Sending `/start`
- Receiving menu
- Clicking 2-3 buttons
- Bot responding correctly

---

### STEP 4: SHADOW MODE TRADE SIMULATION
**Inject a Test Signal:**

Create `tests/live_activation/inject_v3_signal.py`:
```python
import requests
import json

# V3 Alert Payload (Bullish EURUSD)
payload = {
    "symbol": "EURUSD",
    "signal": "BULLISH",
    "score": 10,
    "mtf_trends": "1,1,1,1,1,1",
    "logic": "combinedlogic-1",
    "timestamp": "2026-01-17T17:00:00"
}

# Send to Webhook
response = requests.post(
    "http://localhost:5000/webhook/tradingview",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print(f"Response: {response.status_code}")
print(f"Body: {response.json()}")
```

**Run:**
```bash
python tests/live_activation/inject_v3_signal.py
```

**Expected Behavior:**
1. **Webhook receives signal** → Logs: `📥 Alert Received: EURUSD BULLISH`
2. **V3 Plugin processes** → Logs: `🔌 V3 Plugin: Processing combinedlogic-1`
3. **Session Manager validates** → Logs: `✅ Symbol Allowed: EURUSD (London Session)`
4. **Trading Engine creates order** → Logs: `📊 SHADOW ORDER: EURUSD BUY 0.01 lots`
5. **Database records session** → Logs: `💾 Session Created: SES_20260117_170000_abc123`
6. **Telegram notification sent** → Message: `🚨 **ENTRY ALERT** EURUSD BUY (Shadow Mode)`

**PROOF REQUIRED:**
- Terminal logs showing ALL 6 steps
- Telegram screenshot showing the Entry Alert
- Database query: `SELECT * FROM trading_sessions WHERE symbol='EURUSD';` → Should return 1 row

---

## 🚫 UNACCEPTABLE RESPONSES

**DO NOT SAY:**
- ❌ "Webhook server is running" (We need FULL bot)
- ❌ "Telegram API is working" (We need INTERACTIVE commands)
- ❌ "MT5 requires Windows" (Use demo/paper mode or virtual display)
- ❌ "I sent a test message" (We need END-TO-END flow)

**ONLY ACCEPTABLE RESPONSE:**
✅ "Full bot is running. Here's proof: [Startup Logs] + [Telegram Video] + [Trade Simulation Logs]"

---

## 📊 DELIVERABLES (ALL MANDATORY)

1. **Startup Logs** (Text file: `logs/startup_20260117.log`)
2. **Telegram Interaction Video** (MP4: Shows `/start`, menu, button clicks)
3. **Trade Simulation Logs** (Text file: `logs/trade_simulation.log`)
4. **Database Dump** (SQL: `SELECT * FROM trading_sessions LIMIT 5;`)
5. **Screenshot** (Telegram Entry Alert message)

---

## ⏱️ DEADLINE: 2 HOURS

**Start Time:** 2026-01-17 17:10  
**End Time:** 2026-01-17 19:10

**If not completed:** Escalate to manual intervention.

---

**REMEMBER:** The bot is not "working" until it can:
1. Start without crashes
2. Respond to Telegram commands
3. Process a trading signal end-to-end
4. Send notifications

**NO SHORTCUTS. NO HALF-MEASURES. FULL ACTIVATION ONLY.** 🔥
