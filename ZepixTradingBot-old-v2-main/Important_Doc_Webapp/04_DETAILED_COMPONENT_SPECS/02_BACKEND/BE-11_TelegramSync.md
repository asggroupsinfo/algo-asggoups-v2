# BE-11: TELEGRAM SYNC LOGIC
**Component ID:** BE-11  
**Layer:** Service Integration  
**Goal:** Coexistence

---

## 1. 📝 Overview
Ensures that actions taken on the Web Dashboard are reflected on Telegram, and vice versa.

## 2. 🔩 State Synchronization

### Database as Source of Truth
Neither the Web Frontend nor the Telegram Bot holds state in memory. Both query the `bot_state` table.

- **Scenario:** User clicks "Stop" on Web.
  1. API updates `bot_state.is_running = False`.
  2. API broadcasts `sys_status` via WebSocket (Web UI updates).
  3. API calls `TelegramService.notify("Bot Stopped via Web")`.

- **Scenario:** User types `/start` on Telegram.
  1. Bot updates `bot_state.is_running = True`.
  2. Bot process starts trading loop.
  3. Bot process emits "Started" event used by WebSocket (Web UI updates).

## 3. 🤖 Telegram Service Spec
A Python service module `app/services/telegram_svc.py`.

```python
async def send_telegram_alert(message: str, chat_id: str):
    # Uses aiohttp to call Telegram API
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    await http_client.post(url, json=payload)
```

## 4. 🔏 Command Locking
To prevent race conditions:
- **Lock:** When a command is processing (e.g., Start Sequence), set `command_lock = True` in DB.
- **Reject:** If Telegram tries to start while Web is starting, reply: "⚠️ System busy, please wait."


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

