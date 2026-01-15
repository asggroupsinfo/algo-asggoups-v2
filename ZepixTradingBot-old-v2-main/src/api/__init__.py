"""
API Module
Contains webhook handlers and routing endpoints

Part of Plan 02: Webhook Routing & Signal Processing
"""
from src.api.webhook_handler import app, webhook_endpoint, get_plugin_router

__all__ = ['app', 'webhook_endpoint', 'get_plugin_router']
