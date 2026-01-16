"""
Risk Management Service - Stateless service for risk calculations

Provides pip-based SL/TP calculation, ATR-based dynamic SL/TP, and daily limit checks.
All methods are stateless - they use passed parameters and database for state.

Version: 1.0.0
Date: 2026-01-14
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)


class RiskManagementService:
    """
    Stateless service for risk management calculations.
    Wraps RiskManager and provides plugin-safe access to risk functions.
    """
    
    def __init__(self, risk_manager, config, mt5_client, pip_calculator):
        self._risk_manager = risk_manager
        self._config = config
        self._mt5 = mt5_client
        self._pip_calculator = pip_calculator
    
    async def calculate_lot_size(
        self,
        plugin_id: str,
        symbol: str,
        risk_percentage: float,
        stop_loss_pips: float,
        account_balance: float = None
    ) -> float:
        """
        Calculate safe lot size based on risk parameters
        
        Args:
            plugin_id: Plugin identifier for logging
            symbol: Trading symbol
            risk_percentage: Risk per trade (e.g., 1.5 = 1.5%)
            stop_loss_pips: Stop loss distance in pips
            account_balance: Account balance (auto-fetch if None)
        
        Returns:
            Calculated lot size
        """
        try:
            if account_balance is None:
                account_balance = self._mt5.get_account_balance()
            
            risk_amount = account_balance * (risk_percentage / 100.0)
            
            pip_value = self._pip_calculator.get_pip_value(symbol, 1.0)
            
            if pip_value <= 0 or stop_loss_pips <= 0:
                base_lot = self._risk_manager.get_fixed_lot_size(account_balance)
                logger.warning(
                    f"[RISK] {plugin_id}: Using fixed lot {base_lot} "
                    f"(pip_value={pip_value}, sl_pips={stop_loss_pips})"
                )
                return base_lot
            
            lot_size = risk_amount / (stop_loss_pips * pip_value)
            
            lot_size = max(0.01, round(lot_size, 2))
            
            max_lot = self._config.get("max_lot_size", 10.0)
            lot_size = min(lot_size, max_lot)
            
            logger.info(
                f"[RISK] {plugin_id}: Calculated lot={lot_size} "
                f"(risk={risk_percentage}%, sl={stop_loss_pips} pips, balance={account_balance})"
            )
            
            return lot_size
            
        except Exception as e:
            logger.error(f"[RISK] Error calculating lot size: {e}")
            return 0.01
    
    async def calculate_sl_pips(
        self,
        symbol: str,
        entry_price: float,
        sl_price: float
    ) -> float:
        """
        Calculate stop loss distance in pips
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            sl_price: Stop loss price
        
        Returns:
            SL distance in pips
        """
        try:
            pip_size = self._pip_calculator.get_pip_size(symbol)
            sl_pips = abs(entry_price - sl_price) / pip_size
            return round(sl_pips, 1)
        except Exception as e:
            logger.error(f"[RISK] Error calculating SL pips: {e}")
            return 0.0
    
    async def calculate_tp_pips(
        self,
        symbol: str,
        entry_price: float,
        tp_price: float
    ) -> float:
        """
        Calculate take profit distance in pips
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            tp_price: Take profit price
        
        Returns:
            TP distance in pips
        """
        try:
            pip_size = self._pip_calculator.get_pip_size(symbol)
            tp_pips = abs(tp_price - entry_price) / pip_size
            return round(tp_pips, 1)
        except Exception as e:
            logger.error(f"[RISK] Error calculating TP pips: {e}")
            return 0.0
    
    async def calculate_atr_sl(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        atr_value: float,
        atr_multiplier: float = 1.5
    ) -> float:
        """
        Calculate ATR-based dynamic stop loss price
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            entry_price: Entry price
            atr_value: Current ATR value
            atr_multiplier: Multiplier for ATR (default 1.5)
        
        Returns:
            Calculated SL price
        """
        try:
            sl_distance = atr_value * atr_multiplier
            
            if direction.upper() == 'BUY':
                sl_price = entry_price - sl_distance
            else:
                sl_price = entry_price + sl_distance
            
            digits = self._pip_calculator.get_digits(symbol)
            sl_price = round(sl_price, digits)
            
            logger.info(
                f"[ATR_SL] {symbol} {direction}: ATR={atr_value}, "
                f"Multiplier={atr_multiplier}, SL={sl_price}"
            )
            
            return sl_price
            
        except Exception as e:
            logger.error(f"[ATR_SL] Error calculating ATR SL: {e}")
            return 0.0
    
    async def calculate_atr_tp(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        atr_value: float,
        atr_multiplier: float = 2.0
    ) -> float:
        """
        Calculate ATR-based dynamic take profit price
        
        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            entry_price: Entry price
            atr_value: Current ATR value
            atr_multiplier: Multiplier for ATR (default 2.0)
        
        Returns:
            Calculated TP price
        """
        try:
            tp_distance = atr_value * atr_multiplier
            
            if direction.upper() == 'BUY':
                tp_price = entry_price + tp_distance
            else:
                tp_price = entry_price - tp_distance
            
            digits = self._pip_calculator.get_digits(symbol)
            tp_price = round(tp_price, digits)
            
            logger.info(
                f"[ATR_TP] {symbol} {direction}: ATR={atr_value}, "
                f"Multiplier={atr_multiplier}, TP={tp_price}"
            )
            
            return tp_price
            
        except Exception as e:
            logger.error(f"[ATR_TP] Error calculating ATR TP: {e}")
            return 0.0
    
    async def check_daily_limit(self, plugin_id: str) -> Dict[str, Any]:
        """
        Check if daily loss limit reached
        
        Args:
            plugin_id: Plugin identifier for logging
        
        Returns:
            Dict with daily loss info and can_trade status
        """
        try:
            account_balance = self._mt5.get_account_balance()
            risk_tier = self._risk_manager.get_risk_tier(account_balance)
            
            risk_tiers = self._config.get("risk_tiers", {})
            if risk_tier not in risk_tiers:
                return {
                    "daily_loss": 0.0,
                    "daily_limit": 0.0,
                    "remaining": 0.0,
                    "can_trade": False,
                    "error": f"Invalid risk tier: {risk_tier}"
                }
            
            risk_params = risk_tiers[risk_tier]
            daily_limit = risk_params.get("daily_loss_limit", 500.0)
            daily_loss = self._risk_manager.daily_loss
            remaining = max(0, daily_limit - daily_loss)
            can_trade = daily_loss < daily_limit
            
            logger.info(
                f"[DAILY_LIMIT] {plugin_id}: Loss=${daily_loss:.2f}, "
                f"Limit=${daily_limit:.2f}, Remaining=${remaining:.2f}, "
                f"CanTrade={can_trade}"
            )
            
            return {
                "daily_loss": daily_loss,
                "daily_limit": daily_limit,
                "remaining": remaining,
                "can_trade": can_trade,
                "risk_tier": risk_tier
            }
            
        except Exception as e:
            logger.error(f"[DAILY_LIMIT] Error checking daily limit: {e}")
            return {
                "daily_loss": 0.0,
                "daily_limit": 0.0,
                "remaining": 0.0,
                "can_trade": False,
                "error": str(e)
            }
    
    async def check_lifetime_limit(self, plugin_id: str) -> Dict[str, Any]:
        """
        Check if lifetime loss limit reached
        
        Args:
            plugin_id: Plugin identifier for logging
        
        Returns:
            Dict with lifetime loss info and can_trade status
        """
        try:
            account_balance = self._mt5.get_account_balance()
            risk_tier = self._risk_manager.get_risk_tier(account_balance)
            
            risk_tiers = self._config.get("risk_tiers", {})
            if risk_tier not in risk_tiers:
                return {
                    "lifetime_loss": 0.0,
                    "lifetime_limit": 0.0,
                    "remaining": 0.0,
                    "can_trade": False,
                    "error": f"Invalid risk tier: {risk_tier}"
                }
            
            risk_params = risk_tiers[risk_tier]
            lifetime_limit = risk_params.get("max_total_loss", 2000.0)
            lifetime_loss = self._risk_manager.lifetime_loss
            remaining = max(0, lifetime_limit - lifetime_loss)
            can_trade = lifetime_loss < lifetime_limit
            
            return {
                "lifetime_loss": lifetime_loss,
                "lifetime_limit": lifetime_limit,
                "remaining": remaining,
                "can_trade": can_trade,
                "risk_tier": risk_tier
            }
            
        except Exception as e:
            logger.error(f"[LIFETIME_LIMIT] Error checking lifetime limit: {e}")
            return {
                "lifetime_loss": 0.0,
                "lifetime_limit": 0.0,
                "remaining": 0.0,
                "can_trade": False,
                "error": str(e)
            }
    
    async def validate_trade_risk(
        self,
        plugin_id: str,
        symbol: str,
        lot_size: float,
        sl_pips: float
    ) -> Dict[str, Any]:
        """
        Validate if a trade meets risk requirements
        
        Args:
            plugin_id: Plugin identifier
            symbol: Trading symbol
            lot_size: Proposed lot size
            sl_pips: Stop loss in pips
        
        Returns:
            Dict with validation result and details
        """
        try:
            daily_check = await self.check_daily_limit(plugin_id)
            if not daily_check.get("can_trade", False):
                return {
                    "valid": False,
                    "reason": "Daily loss limit reached",
                    "details": daily_check
                }
            
            lifetime_check = await self.check_lifetime_limit(plugin_id)
            if not lifetime_check.get("can_trade", False):
                return {
                    "valid": False,
                    "reason": "Lifetime loss limit reached",
                    "details": lifetime_check
                }
            
            pip_value = self._pip_calculator.get_pip_value(symbol, lot_size)
            potential_loss = sl_pips * pip_value
            
            if potential_loss > daily_check.get("remaining", 0):
                return {
                    "valid": False,
                    "reason": f"Potential loss ${potential_loss:.2f} exceeds remaining daily limit ${daily_check['remaining']:.2f}",
                    "details": {
                        "potential_loss": potential_loss,
                        "remaining_daily": daily_check["remaining"]
                    }
                }
            
            return {
                "valid": True,
                "reason": "Trade risk validated",
                "details": {
                    "potential_loss": potential_loss,
                    "remaining_daily": daily_check["remaining"],
                    "remaining_lifetime": lifetime_check["remaining"]
                }
            }
            
        except Exception as e:
            logger.error(f"[VALIDATE_RISK] Error validating trade risk: {e}")
            return {
                "valid": False,
                "reason": f"Validation error: {str(e)}",
                "details": {}
            }
    
    async def get_fixed_lot_size(
        self,
        plugin_id: str,
        account_balance: float = None
    ) -> float:
        """
        Get fixed lot size based on account tier
        
        Args:
            plugin_id: Plugin identifier
            account_balance: Account balance (auto-fetch if None)
        
        Returns:
            Fixed lot size for current tier
        """
        try:
            if account_balance is None:
                account_balance = self._mt5.get_account_balance()
            
            lot_size = self._risk_manager.get_fixed_lot_size(account_balance)
            
            logger.debug(
                f"[FIXED_LOT] {plugin_id}: Balance=${account_balance:.2f}, "
                f"Lot={lot_size}"
            )
            
            return lot_size
            
        except Exception as e:
            logger.error(f"[FIXED_LOT] Error getting fixed lot size: {e}")
            return 0.01
