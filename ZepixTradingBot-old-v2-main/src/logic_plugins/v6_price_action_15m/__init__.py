"""
V6 Price Action 15M Plugin - Intraday Logic

Order Routing: ORDER A ONLY
Risk Multiplier: 1.0x
Requires Market State Check
Requires Trend Pulse Alignment

Version: 1.0.0
Date: 2026-01-14
"""

from .plugin import V6PriceAction15mPlugin

__all__ = ['V6PriceAction15mPlugin']
