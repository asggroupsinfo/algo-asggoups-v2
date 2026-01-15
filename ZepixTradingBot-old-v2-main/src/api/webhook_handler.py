"""
Webhook Handler
Receives TradingView alerts and routes to appropriate plugins

Part of Plan 02: Webhook Routing & Signal Processing
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import json

from src.utils.signal_parser import SignalParser
from src.core.plugin_router import PluginRouter, get_plugin_router as _get_router

logger = logging.getLogger(__name__)

# FastAPI app instance
app = FastAPI(
    title="Zepix Trading Bot API",
    description="Webhook endpoint for TradingView alerts",
    version="2.0.0"
)

# Plugin router singleton
_plugin_router: Optional[PluginRouter] = None


def init_plugin_router(plugin_registry) -> PluginRouter:
    """
    Initialize the plugin router with a registry.
    Must be called before handling webhooks.
    
    Args:
        plugin_registry: PluginRegistry instance
        
    Returns:
        Initialized PluginRouter
    """
    global _plugin_router
    _plugin_router = _get_router(plugin_registry)
    logger.info("Webhook handler initialized with plugin router")
    return _plugin_router


def get_plugin_router() -> Optional[PluginRouter]:
    """
    Get the plugin router singleton.
    
    Returns:
        PluginRouter instance or None if not initialized
    """
    return _plugin_router


@app.post("/webhook")
async def webhook_endpoint(request: Request) -> JSONResponse:
    """
    Receive TradingView alerts and route to appropriate plugin.
    
    Flow:
    1. Receive raw alert
    2. Parse into standardized signal
    3. Validate signal
    4. Route to plugin
    5. Return result
    
    Returns:
        JSONResponse with processing result
    """
    try:
        # Get raw alert
        raw_alert = await request.json()
        logger.info(f"Received webhook alert: {raw_alert.get('type', raw_alert.get('strategy', 'unknown'))}")
        
        # Parse alert using SignalParser
        signal = SignalParser.parse(raw_alert)
        if not signal:
            logger.warning("Failed to parse alert")
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "Invalid alert format"}
            )
        
        # Validate signal
        if not SignalParser.validate(signal):
            logger.warning("Signal validation failed")
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "Signal validation failed"}
            )
        
        # Check if router is initialized
        router = get_plugin_router()
        if not router:
            logger.error("Plugin router not initialized")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Plugin router not initialized"}
            )
        
        # Route to plugin
        result = await router.route_signal(signal)
        
        if result:
            logger.info(f"Signal processed successfully: {result.get('status', 'unknown')}")
            return JSONResponse(
                status_code=200,
                content={"status": "success", "result": result}
            )
        else:
            logger.warning("No plugin processed the signal")
            return JSONResponse(
                status_code=200,
                content={"status": "warning", "message": "No plugin available for this signal"}
            )
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook: {e}")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid JSON format"}
        )
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/webhook/v3")
async def webhook_v3_endpoint(request: Request) -> JSONResponse:
    """
    Dedicated V3 webhook endpoint.
    Forces V3 strategy detection.
    """
    try:
        raw_alert = await request.json()
        raw_alert['strategy'] = 'V3_COMBINED'  # Force V3
        
        # Reuse main webhook logic
        request._body = json.dumps(raw_alert).encode()
        return await webhook_endpoint(request)
        
    except Exception as e:
        logger.error(f"V3 Webhook error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/webhook/v6")
async def webhook_v6_endpoint(request: Request) -> JSONResponse:
    """
    Dedicated V6 webhook endpoint.
    Forces V6 strategy detection.
    """
    try:
        raw_alert = await request.json()
        raw_alert['strategy'] = 'V6_PRICE_ACTION'  # Force V6
        
        # Parse and route
        signal = SignalParser.parse(raw_alert)
        if not signal:
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "Invalid V6 alert format"}
            )
        
        router = get_plugin_router()
        if not router:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Plugin router not initialized"}
            )
        
        result = await router.route_signal(signal)
        
        if result:
            return JSONResponse(
                status_code=200,
                content={"status": "success", "result": result}
            )
        else:
            return JSONResponse(
                status_code=200,
                content={"status": "warning", "message": "No V6 plugin available"}
            )
            
    except Exception as e:
        logger.error(f"V6 Webhook error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.get("/routing/stats")
async def routing_stats() -> JSONResponse:
    """Get plugin routing statistics"""
    router = get_plugin_router()
    if not router:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Router not initialized"}
        )
    
    stats = router.get_routing_stats()
    return JSONResponse(
        status_code=200,
        content={"status": "success", "stats": stats}
    )


@app.post("/routing/reset")
async def reset_routing_stats() -> JSONResponse:
    """Reset routing statistics"""
    router = get_plugin_router()
    if not router:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Router not initialized"}
        )
    
    router.reset_stats()
    return JSONResponse(
        status_code=200,
        content={"status": "success", "message": "Stats reset"}
    )


@app.get("/routing/plugins")
async def list_routing_plugins() -> JSONResponse:
    """List all plugins available for routing"""
    router = get_plugin_router()
    if not router:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Router not initialized"}
        )
    
    routes = router.get_available_routes()
    return JSONResponse(
        status_code=200,
        content={"status": "success", "plugins": routes}
    )


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint"""
    router = get_plugin_router()
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "router_initialized": router is not None,
            "version": "2.0.0"
        }
    )
