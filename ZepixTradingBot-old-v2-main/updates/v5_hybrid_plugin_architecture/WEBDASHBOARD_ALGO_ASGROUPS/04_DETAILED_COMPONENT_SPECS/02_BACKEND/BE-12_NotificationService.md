# BE-12: NOTIFICATION SERVICE SPECIFICATION
**Component ID:** BE-12  
**Layer:** Service Logic  
**Goal:** Universal Alert Routing

---

## 1. 📝 Architecture
The notification system is a "Router" that takes an event and decides where to send it based on User Preferences.

**Inputs:** Trade Events, System Errors, Warning Logs.
**Outputs:** Database (History), WebSocket (Dashboard), Telegram (Mobile).

## 2. 🔔 Alert Types & Routing Table

| Alert Type | Level | Web Toast? | Telegram Msg? | Email? |
| :--- | :--- | :--- | :--- | :--- |
| **Trade Open** | INFO | ✅ Yes | ✅ Yes | ❌ No |
| **Trade Close** | INFO | ✅ Yes | ✅ Yes | ❌ No |
| **P&L Summary** | REPORT | ❌ No | ✅ Yes (Daily) | ❌ No |
| **Error** | CRITICAL | ✅ Yes (Persistent) | ✅ Yes (Urgent) | ✅ Yes (Future) |
| **Config Change** | INFO | ✅ Yes | ❌ No | ❌ No |

## 3. 🧬 Implementation Logic

```python
class NotificationRouter:
    async def send(self, event: Event):
        # 1. Always save to DB Audit Log
        await self.save_to_db(event)
        
        # 2. Push to Dashboard via WebSocket
        await ws_manager.broadcast(event.to_json())
        
        # 3. Check Telegram enabled pref
        if config.telegram_enabled and event.priority > LOW:
            await telegram_svc.send(event.message)
```

## 4. 🖼️ Message Formatting
- **Web:** JSON Object `{"title": "...", "body": "...", "color": "green"}`
- **Telegram:** Formatted HTML/Markdown with Emojis.
  `🟢 *BUY BTC/USDT* \nPrice: $42,000`


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

