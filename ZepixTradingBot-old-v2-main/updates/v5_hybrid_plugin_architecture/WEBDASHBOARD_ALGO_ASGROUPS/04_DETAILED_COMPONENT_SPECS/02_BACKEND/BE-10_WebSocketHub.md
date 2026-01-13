# BE-10: WEBSOCKET HUB SPECIFICATION
**Component ID:** BE-10  
**Layer:** Real-time Communication  
**Path:** `/ws/live`

---

## 1. 📝 Overview
The "Heartbeat" of the dashboard. Pushes database updates, trade events, and system logs to the frontend instantly using `FastAPI` WebSockets.

## 2. 🔌 Connection Protocol

### Handshake
- **URL:** `wss://algo.asgroups/ws/live`
- **Auth:** Token passed in Query Param `?token=JWT...` (Browser standard) OR Header (if supported by client lib).
- **Validation:** Server verifies JWT. If invalid, Close connection (Code 4001).

## 3. 📡 Event Channels (Topics)

The client subscribes to everything by default (admin mode), or specific topics.

### A. `sys_status`
- **Payload:** `{"status": "RUNNING", "cpu": 12, "ram": 45}`
- **Frequency:** Every 5 seconds (Heartbeat).

### B. `trade_update`
- **Trigger:** New trade, Order fill, TP hit.
- **Payload:** Full trade object (see BE-07).

### C. `log_stream`
- **Trigger:** New log entry generated.
- **Payload:** `{"level": "INFO", "msg": "..."}`

### D. `notification`
- **Trigger:** Error or Critical Alert.
- **Payload:** `{"type": "error", "title": "Connection Lost"}`

## 4. 🧬 Connection Manager Logic
A singleton `ConnectionManager` class in Python handles:
- **Active Connections:** List of open sockets.
- **Broadcast:** Loop through list and `send_json()`.
- **Disconnect:** Remove socket from list on error.

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
```


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

