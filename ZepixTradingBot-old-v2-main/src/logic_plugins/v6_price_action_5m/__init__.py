"""
V6 Price Action 5M Plugin - Momentum Logic

Order Routing: DUAL ORDERS (Order A + Order B)
Risk Multiplier: 1.0x
ADX Threshold: 25
Confidence Threshold: 70
Requires 15M Alignment

Version: 1.0.0
Date: 2026-01-14
"""

from .plugin import V6PriceAction5mPlugin

__all__ = ['V6PriceAction5mPlugin']
