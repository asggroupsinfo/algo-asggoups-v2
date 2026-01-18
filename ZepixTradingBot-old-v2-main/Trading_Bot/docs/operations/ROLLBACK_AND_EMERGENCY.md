# ROLLBACK & EMERGENCY PROCEDURES
**Version:** 1.0
**Project:** Zepix Trading Bot v2.0

## 1. EMERGENCY SHUTDOWN (KILL SWITCH)
If the bot malfunctions (e.g., executing unwanted trades), immediately stop the process.

**Method 1: Console Termination**
- Focus the terminal window running the bot.
- Press **`Ctrl + C`**.
- Wait for "Bot Shutdown" message.
- If it doesn't stop, close the terminal window or use Task Manager (`python.exe`).

**Method 2: Force Kill (Windows Powerhell)**
```powershell
taskkill /IM python.exe /F
```

---

## 2. PANIC CLOSE (CLOSE ALL TRADES)
To immediately close ALL open positions without shutting down the bot:

**Via Telegram:**
1.  Send command: **`/panic`**
2.  Bot will reply with a confirmation menu.
3.  Click **"✅ YES - CLOSE ALL"**.
4.  Bot will market-close all positions managed by it.

**Via MetaTrader 5 (Manual Override):**
1.  Open MT5 Terminal.
2.  Go to **Trade** tab.
3.  Right-click any Position -> **"Close All"** (or manually close each).
4.  *Note: The bot effectively detects manual closures and updates its database, but it's safer to stop the bot first if Logic is erratic.*

---

## 3. ROLLBACK TO STABLE VERSION
If code changes cause issues, revert to the last stable backup.

**If using Git:**
```bash
git checkout main  # or tag v2.0-stable
```

**If using backups:**
1.  Stop the bot.
2.  Rename `Trading_Bot/src` to `Trading_Bot/src_broken`.
3.  Copy `Trading_Bot/src_backup` (if created) to `Trading_Bot/src`.
4.  Restart bot.

## 4. DATABASE CORRUPTION RECOVERY
If the database (`data/trading_data.db`) is corrupted:
1.  Stop the bot.
2.  Delete or rename `data/trading_data.db` to `data/trading_data.db.corrupt`.
3.  Restart bot.
4.  *Consequence:* Bot loses history of current session trades (will treat existing MT5 positions as "unknown" or manage them based on magic number if configured).

## 5. INCIDENT REPORTING
Log all emergency events:
- Time of incident.
- Symptoms (e.g., "Looping orders").
- Action taken (e.g., "Panic Close triggered").
- Logs: Copy `bot_startup.log` and `logs/trading.log` immediately.
