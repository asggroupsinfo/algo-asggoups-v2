# BE-15: ERROR HANDLING & EXCEPTIONS
**Component ID:** BE-15  
**Layer:** Backend Architecture  
**Scope:** Global

---

## 1. 📝 Philosophy
Standardized error responses ensure the Frontend can always show meaningful messages (Toasts) to the user.

## 2. 📄 Response Format
All errors return the same JSON structure:

```json
{
  "error": {
    "code": "AUTH_INVALID_TOKEN",
    "message": "The session token has expired. Please login again.",
    "details": { "expired_at": "..." } // Optional debug info
  }
}
```

## 3. 📚 Error Catalog

| HTTP Code | Internal Code | Message |
| :--- | :--- | :--- |
| **400** | `REQ_VALIDATION` | Invalid input data. |
| **401** | `AUTH_REQUIRED` | Missing or invalid token. |
| **403** | `PERM_DENIED` | You do not have permission (Viewer -> Admin). |
| **404** | `RSRC_NOT_FOUND` | Trade ID or User not found. |
| **409** | `STATE_CONFLICT` | Bot already running / Telegram lock active. |
| **429** | `RATE_LIMIT` | Too many requests. |
| **500** | `SYS_INTERNAL` | Unhandled exception (Check logs). |

## 4. 🧬 FastAPI Implementation
Uses `@app.exception_handler` to catch Python Exceptions and convert to above JSON.

```python
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": {"code": "REQ_VALIDATION", "message": str(exc)}}
    )
```


---

##  IMPORTANT IMPLEMENTATION & COMPLIANCE NOTE
1. **Codebase Synchronization:** Before implementing this component, ALWAYS scan the full ZepixTradingBot codebase for recent updates.
2. **Creative License:** This document is a foundational blueprint. The Agent is authorized to use creative freedom to make the Frontend modern, animated, and premium.
3. **Backend Alignment:** Backend and Database logic must be derived from a deep analysis of the *current* bot behavior and code structure.
4. **Live Verification:** After completing this file, you must perform a LIVE test to verify Web-Bot connectivity and functionality immediately.

