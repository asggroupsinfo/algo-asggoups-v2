# WF-03: LIVE ALERT FLOW
**Component ID:** WF-03  
**Type:** Data Flow  
**Trigger:** TradingView Webhook

---

## 1. 📝 Description
How a signal travels from sources to the user's screen in real-time.

## 2. 🌊 Flow Diagram

```mermaid
graph TD
    TV[TradingView] -->|Webhook| API[FastAPI Webhook Endpoint]
    
    API -->|1. Parse & Verify| Logic[Strategy Engine]
    
    Logic -->|2. Decision: BUY| Order[Exchange Execution]
    
    Order -->|3. Fill Confirmed| DB[(Database)]
    
    DB -->|4. Save Trade| Stats[Daily Stats Aggregator]
    
    Logic -->|5. Notify| Router[Notification Router]
    
    Router -->|6a. WebSocket| Dashboard[Web Dashboard UI]
    Router -->|6b. API Call| Telegram[Telegram Bot]
    
    Dashboard -->|7. React State Update| Toast[Show Toast]
    Dashboard -->|8. Table Update| Table[Add Row to Grid]
```

## 3. ⚡ Latency Budget
- Webhook -> DB: < 100ms
- Webhook -> Websocket Push: < 200ms
- **Goal:** User sees trade on dashboard same second it happens.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

