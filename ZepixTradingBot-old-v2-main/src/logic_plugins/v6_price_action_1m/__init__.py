"""
V6 Price Action 1M Plugin - Scalping Logic

Order Routing: ORDER B ONLY
Risk Multiplier: 0.5x
ADX Threshold: 20
Confidence Threshold: 80
Max Spread: 2 pips

Version: 1.0.0
Date: 2026-01-14
"""

from .plugin import V6PriceAction1mPlugin

__all__ = ['V6PriceAction1mPlugin']
