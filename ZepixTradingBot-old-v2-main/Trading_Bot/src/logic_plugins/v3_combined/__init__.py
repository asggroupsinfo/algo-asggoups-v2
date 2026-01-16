"""
Combined V3 Logic Plugin

This plugin implements the V3 Combined Logic system with:
- 12 signal types (7 entry, 2 exit, 2 info, 1 bonus)
- 2-tier routing matrix (signal override + timeframe routing)
- Dual order system (Order A: Smart SL, Order B: Fixed $10 SL)
- MTF 4-pillar trend validation
- Shadow mode support

Version: 1.0.0
Date: 2026-01-14
"""

from .plugin import V3CombinedPlugin

__all__ = ['V3CombinedPlugin']
