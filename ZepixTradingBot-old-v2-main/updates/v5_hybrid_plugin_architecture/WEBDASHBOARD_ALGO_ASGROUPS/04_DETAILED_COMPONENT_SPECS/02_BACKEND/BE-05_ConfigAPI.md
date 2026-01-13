# BE-05: CONFIGURATION API SPECIFICATION
**Component ID:** BE-05  
**Layer:** API Endpoint  
**Path:** `/api/config`
**Auth:** Editor/Admin

---

## 1. 📝 Overview
Read and write access to the bot's `config.json` structure stored in the database.

## 2. 🛣️ Endpoints

### 2.1 Get Configuration
**GET** `/api/config`
- **Response (200 OK):** Returns full JSON object.
  ```json
  {
    "exchange": "binance",
    "strategies": {
      "v3_combined": { "enabled": true, "multiplier": 1.5 },
      "v6_scalp": { "enabled": false }
    },
    "risk_management": {
      "stop_loss_pct": 2.5,
      "take_profit_pct": 5.0
    }
  }
  ```

### 2.2 Update Configuration
**PUT** `/api/config`
- **Body:** Partial or Full JSON config.
- **Logic:**
  1. **Validate:** Use Pydantic models to ensure types/ranges are correct.
  2. **Backup:** Save current config to `config_history` table.
  3. **Save:** Update `active_config` in DB.
  4. **Apply:** If bot is running, trigger "Hot Reload" or notify "Restart Required".

### 2.3 Validation Rules
- `stop_loss_pct`: Must be > 0.1 and < 50.
- `leverage`: Must be integer, max 125 (depending on exchange).
- `api_key`: Must not be empty if live trading enabled.

## 3. 🔄 Hot Reloading
Some settings (like SL/TP, Trailing Stop) can be updated without restarting the bot.
- API sends signal to Bot Process.
- Bot Process re-reads DB variables.
- Changes apply to *new* positions only.


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

