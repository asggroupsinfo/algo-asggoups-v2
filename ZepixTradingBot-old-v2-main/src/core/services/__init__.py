"""
Core Services Module - Stateless service layer for V5 Hybrid Plugin Architecture

This module provides stateless services that wrap existing bot functionality
and expose it safely to plugins.

Services:
- OrderExecutionService: V3 Dual Order and V6 Conditional Order methods
- RiskManagementService: SL/TP calculation, ATR-based dynamic SL/TP, daily limits
- TrendManagementService: V3 4-Pillar and V6 Trend Pulse systems
- MarketDataService: Price, spread, and volatility data

Version: 1.0.0
Date: 2026-01-14
"""

from .order_execution_service import OrderExecutionService
from .risk_management_service import RiskManagementService
from .trend_management_service import TrendManagementService
from .market_data_service import MarketDataService

__all__ = [
    'OrderExecutionService',
    'RiskManagementService',
    'TrendManagementService',
    'MarketDataService'
]
