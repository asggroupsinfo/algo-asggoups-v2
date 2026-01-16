"""
Profit Booking Service
Plan 05: Profit Booking Integration

Provides profit booking functionality to plugins via ServiceAPI:
- 5-Level Pyramid management
- $7 profit target per order
- Chain progression logic
- Profit Booking SL Hunt
- Chain persistence across restarts
"""
from typing import Dict, Any, Optional, List, Callable
import logging
import json
import os
from datetime import datetime

from src.core.plugin_system.profit_booking_interface import (
    ProfitChain, BookingResult, ChainStatus,
    PYRAMID_LEVELS, MAX_PYRAMID_LEVEL, PROFIT_TARGET_PER_ORDER
)

logger = logging.getLogger(__name__)


# Singleton instance
_profit_booking_service_instance: Optional['ProfitBookingService'] = None


def get_profit_booking_service(
    profit_booking_manager: Optional[Any] = None
) -> 'ProfitBookingService':
    """Get singleton instance of ProfitBookingService"""
    global _profit_booking_service_instance
    if _profit_booking_service_instance is None:
        _profit_booking_service_instance = ProfitBookingService(profit_booking_manager)
    return _profit_booking_service_instance


def reset_profit_booking_service():
    """Reset singleton (for testing)"""
    global _profit_booking_service_instance
    _profit_booking_service_instance = None


class ProfitBookingService:
    """
    Service layer for profit booking operations.
    Plugins use this instead of calling managers directly.
    
    Features:
    - 5-Level Pyramid: Level 0: 1, Level 1: 2, Level 2: 4, Level 3: 8, Level 4: 16
    - $7 profit target per order
    - Chain progression with automatic level advancement
    - Profit Booking SL Hunt on SL hit
    - Chain persistence across restarts
    """
    
    # Pyramid configuration
    PYRAMID_LEVELS = PYRAMID_LEVELS
    MAX_LEVEL = MAX_PYRAMID_LEVEL
    PROFIT_TARGET = PROFIT_TARGET_PER_ORDER
    
    def __init__(self, profit_booking_manager: Optional[Any] = None):
        """
        Initialize profit booking service.
        
        Args:
            profit_booking_manager: ProfitBookingManager instance (optional)
        """
        self.manager = profit_booking_manager
        
        # Track chains by plugin: plugin_id -> {chain_id: ProfitChain}
        self._plugin_chains: Dict[str, Dict[str, ProfitChain]] = {}
        
        # Order to chain mapping: order_id -> chain_id
        self._order_to_chain: Dict[str, str] = {}
        
        # Chain close callbacks: chain_id -> callback
        self._close_callbacks: Dict[str, Callable] = {}
        
        # Statistics
        self._stats = {
            'total_chains_created': 0,
            'total_chains_completed': 0,
            'total_profit_booked': 0.0,
            'total_orders_booked': 0,
            'sl_hunts_triggered': 0,
            'last_reset': datetime.now().isoformat()
        }
        
        # Persistence file path
        self._persistence_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', 'data', 'profit_chains.json'
        )
        
        # Load persisted chains on startup
        self._load_persisted_chains()
    
    def set_manager(self, manager: Any):
        """Inject profit booking manager"""
        self.manager = manager
        logger.info("ProfitBookingManager injected into ProfitBookingService")
    
    async def create_chain(
        self,
        plugin_id: str,
        order_b_id: str,
        symbol: str,
        direction: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ProfitChain]:
        """
        Create a new profit booking chain.
        
        Called when Order B is created. Initializes chain at Level 0.
        
        Args:
            plugin_id: Plugin identifier
            order_b_id: Order B identifier
            symbol: Trading symbol
            direction: Trade direction (BUY/SELL)
            metadata: Additional metadata
            
        Returns:
            ProfitChain if created successfully
        """
        # Generate chain ID
        chain_id = f"chain_{plugin_id}_{order_b_id}_{int(datetime.now().timestamp())}"
        
        # Create chain in manager if available
        if self.manager:
            try:
                manager_chain_id = await self.manager.create_profit_chain(order_b_id, symbol)
                if manager_chain_id:
                    chain_id = manager_chain_id
            except (AttributeError, TypeError) as e:
                logger.warning(f"Manager chain creation failed: {e}, using generated ID")
        
        # Create chain object
        chain = ProfitChain(
            chain_id=chain_id,
            plugin_id=plugin_id,
            symbol=symbol,
            direction=direction,
            level=0,
            orders_in_level=self.PYRAMID_LEVELS[0],
            orders_booked=0,
            total_profit=0.0,
            status=ChainStatus.ACTIVE,
            metadata=metadata or {}
        )
        
        # Track chain
        self._track_chain(plugin_id, chain)
        self._order_to_chain[order_b_id] = chain_id
        
        # Update stats
        self._stats['total_chains_created'] += 1
        
        # Persist chains
        self._persist_chains()
        
        logger.info(
            f"Profit chain created: {chain_id} for plugin {plugin_id}, "
            f"symbol {symbol}, direction {direction}"
        )
        return chain
    
    async def book_profit(
        self,
        chain_id: str,
        order_id: str,
        profit_amount: float = None
    ) -> BookingResult:
        """
        Book profit for an order in a chain.
        
        Called when order hits $7 target. May advance chain level.
        
        Args:
            chain_id: Chain identifier
            order_id: Order that hit profit target
            profit_amount: Profit amount (defaults to $7)
            
        Returns:
            BookingResult with profit and level info
        """
        if profit_amount is None:
            profit_amount = self.PROFIT_TARGET
        
        chain = self._get_chain_by_id(chain_id)
        if not chain:
            return BookingResult(
                success=False,
                order_id=order_id,
                profit_amount=0,
                chain_advanced=False,
                new_level=0,
                error="Chain not found"
            )
        
        if chain.status != ChainStatus.ACTIVE:
            return BookingResult(
                success=False,
                order_id=order_id,
                profit_amount=0,
                chain_advanced=False,
                new_level=chain.level,
                error=f"Chain not active: {chain.status.value}"
            )
        
        # Book profit in manager if available
        if self.manager:
            try:
                success = await self.manager.book_profit(chain_id, order_id)
                if not success:
                    logger.warning(f"Manager booking failed for {order_id}")
            except (AttributeError, TypeError) as e:
                logger.warning(f"Manager booking error: {e}")
        
        # Update chain state
        chain.orders_booked += 1
        chain.total_profit += profit_amount
        
        # Update stats
        self._stats['total_profit_booked'] += profit_amount
        self._stats['total_orders_booked'] += 1
        
        # Check if level should advance
        chain_advanced = False
        if chain.orders_booked >= self.PYRAMID_LEVELS[chain.level]:
            chain_advanced = await self._advance_level(chain)
        
        # Persist chains
        self._persist_chains()
        
        logger.info(
            f"Profit booked: {order_id} in chain {chain_id}, "
            f"amount: ${profit_amount:.2f}, total: ${chain.total_profit:.2f}, "
            f"level: {chain.level}, advanced: {chain_advanced}"
        )
        
        return BookingResult(
            success=True,
            order_id=order_id,
            profit_amount=profit_amount,
            chain_advanced=chain_advanced,
            new_level=chain.level
        )
    
    async def _advance_level(self, chain: ProfitChain) -> bool:
        """
        Advance chain to next pyramid level.
        
        Args:
            chain: ProfitChain to advance
            
        Returns:
            True if advanced, False if at max level
        """
        if chain.level >= self.MAX_LEVEL:
            logger.info(f"Chain {chain.chain_id} completed all levels")
            chain.status = ChainStatus.COMPLETED
            self._stats['total_chains_completed'] += 1
            return False
        
        # Advance level
        old_level = chain.level
        chain.level += 1
        chain.orders_in_level = self.PYRAMID_LEVELS[chain.level]
        chain.orders_booked = 0  # Reset for new level
        
        # Advance in manager if available
        if self.manager:
            try:
                await self.manager.advance_chain_level(chain.chain_id)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Manager level advance error: {e}")
        
        logger.info(
            f"Chain {chain.chain_id} advanced: Level {old_level} -> {chain.level}, "
            f"orders needed: {chain.orders_in_level}"
        )
        return True
    
    async def start_sl_hunt(self, chain_id: str) -> bool:
        """
        Start Profit Booking SL Hunt.
        
        Called when chain SL is hit. Triggers recovery mode.
        
        Args:
            chain_id: Chain identifier
            
        Returns:
            True if SL Hunt started successfully
        """
        chain = self._get_chain_by_id(chain_id)
        if not chain:
            logger.warning(f"Chain not found for SL Hunt: {chain_id}")
            return False
        
        chain.status = ChainStatus.SL_HUNT
        self._stats['sl_hunts_triggered'] += 1
        
        # Start SL hunt in manager if available
        if self.manager:
            try:
                success = await self.manager.start_profit_sl_hunt(chain_id)
                if success:
                    logger.info(f"Profit Booking SL Hunt started via manager: {chain_id}")
            except (AttributeError, TypeError) as e:
                logger.warning(f"Manager SL Hunt error: {e}")
        
        # Persist chains
        self._persist_chains()
        
        logger.info(f"Profit Booking SL Hunt started for chain {chain_id}")
        return True
    
    async def recover_chain(self, chain_id: str) -> bool:
        """
        Recover chain from SL Hunt.
        
        Called when SL Hunt recovery is successful.
        
        Args:
            chain_id: Chain identifier
            
        Returns:
            True if recovered successfully
        """
        chain = self._get_chain_by_id(chain_id)
        if not chain:
            return False
        
        if chain.status == ChainStatus.SL_HUNT:
            chain.status = ChainStatus.ACTIVE
            self._persist_chains()
            logger.info(f"Chain {chain_id} recovered from SL Hunt")
            return True
        
        return False
    
    def cancel_chain(self, chain_id: str, reason: str = "manual") -> bool:
        """
        Cancel a profit chain.
        
        Args:
            chain_id: Chain identifier
            reason: Cancellation reason
            
        Returns:
            True if cancelled successfully
        """
        chain = self._get_chain_by_id(chain_id)
        if not chain:
            return False
        
        chain.status = ChainStatus.CANCELLED
        chain.metadata['cancel_reason'] = reason
        chain.metadata['cancelled_at'] = datetime.now().isoformat()
        
        self._persist_chains()
        logger.info(f"Chain {chain_id} cancelled: {reason}")
        return True
    
    def _track_chain(self, plugin_id: str, chain: ProfitChain):
        """Track chain ownership by plugin"""
        if plugin_id not in self._plugin_chains:
            self._plugin_chains[plugin_id] = {}
        self._plugin_chains[plugin_id][chain.chain_id] = chain
    
    def _get_chain_by_id(self, chain_id: str) -> Optional[ProfitChain]:
        """Find chain by ID across all plugins"""
        for plugin_chains in self._plugin_chains.values():
            if chain_id in plugin_chains:
                return plugin_chains[chain_id]
        return None
    
    def get_chain_for_order(self, order_id: str) -> Optional[ProfitChain]:
        """Get chain for an order"""
        chain_id = self._order_to_chain.get(order_id)
        if chain_id:
            return self._get_chain_by_id(chain_id)
        return None
    
    def get_plugin_chains(self, plugin_id: str) -> List[ProfitChain]:
        """Get all chains for a plugin"""
        return list(self._plugin_chains.get(plugin_id, {}).values())
    
    def get_active_chains(self, plugin_id: str) -> List[ProfitChain]:
        """Get active chains for a plugin"""
        chains = self.get_plugin_chains(plugin_id)
        return [c for c in chains if c.status == ChainStatus.ACTIVE]
    
    def get_all_active_chains(self) -> List[ProfitChain]:
        """Get all active chains across all plugins"""
        active = []
        for plugin_chains in self._plugin_chains.values():
            for chain in plugin_chains.values():
                if chain.status == ChainStatus.ACTIVE:
                    active.append(chain)
        return active
    
    def get_chain_stats(self, plugin_id: str) -> Dict[str, Any]:
        """Get profit booking statistics for a plugin"""
        chains = self.get_plugin_chains(plugin_id)
        
        return {
            'total_chains': len(chains),
            'active_chains': len([c for c in chains if c.status == ChainStatus.ACTIVE]),
            'completed_chains': len([c for c in chains if c.status == ChainStatus.COMPLETED]),
            'sl_hunt_chains': len([c for c in chains if c.status == ChainStatus.SL_HUNT]),
            'cancelled_chains': len([c for c in chains if c.status == ChainStatus.CANCELLED]),
            'total_profit': sum(c.total_profit for c in chains),
            'chains_by_level': {
                level: len([c for c in chains if c.level == level])
                for level in range(self.MAX_LEVEL + 1)
            }
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global profit booking statistics"""
        return {
            **self._stats,
            'active_chains': len(self.get_all_active_chains()),
            'plugins_with_chains': len(self._plugin_chains)
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self._stats = {
            'total_chains_created': 0,
            'total_chains_completed': 0,
            'total_profit_booked': 0.0,
            'total_orders_booked': 0,
            'sl_hunts_triggered': 0,
            'last_reset': datetime.now().isoformat()
        }
    
    def _persist_chains(self):
        """Persist chains to file for restart recovery"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self._persistence_path), exist_ok=True)
            
            # Serialize chains
            data = {
                'chains': {},
                'order_to_chain': self._order_to_chain,
                'stats': self._stats,
                'saved_at': datetime.now().isoformat()
            }
            
            for plugin_id, chains in self._plugin_chains.items():
                data['chains'][plugin_id] = {}
                for chain_id, chain in chains.items():
                    data['chains'][plugin_id][chain_id] = {
                        'chain_id': chain.chain_id,
                        'plugin_id': chain.plugin_id,
                        'symbol': chain.symbol,
                        'direction': chain.direction,
                        'level': chain.level,
                        'orders_in_level': chain.orders_in_level,
                        'orders_booked': chain.orders_booked,
                        'total_profit': chain.total_profit,
                        'status': chain.status.value,
                        'created_at': chain.created_at.isoformat(),
                        'metadata': chain.metadata
                    }
            
            with open(self._persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Chains persisted to {self._persistence_path}")
        except Exception as e:
            logger.error(f"Failed to persist chains: {e}")
    
    def _load_persisted_chains(self):
        """Load persisted chains from file"""
        try:
            if not os.path.exists(self._persistence_path):
                logger.info("No persisted chains found")
                return
            
            with open(self._persistence_path, 'r') as f:
                data = json.load(f)
            
            # Restore chains
            for plugin_id, chains in data.get('chains', {}).items():
                self._plugin_chains[plugin_id] = {}
                for chain_id, chain_data in chains.items():
                    chain = ProfitChain(
                        chain_id=chain_data['chain_id'],
                        plugin_id=chain_data['plugin_id'],
                        symbol=chain_data['symbol'],
                        direction=chain_data['direction'],
                        level=chain_data['level'],
                        orders_in_level=chain_data['orders_in_level'],
                        orders_booked=chain_data['orders_booked'],
                        total_profit=chain_data['total_profit'],
                        status=ChainStatus(chain_data['status']),
                        created_at=datetime.fromisoformat(chain_data['created_at']),
                        metadata=chain_data.get('metadata', {})
                    )
                    self._plugin_chains[plugin_id][chain_id] = chain
            
            # Restore order mapping
            self._order_to_chain = data.get('order_to_chain', {})
            
            # Restore stats
            self._stats = data.get('stats', self._stats)
            
            logger.info(
                f"Loaded {sum(len(c) for c in self._plugin_chains.values())} "
                f"persisted chains from {self._persistence_path}"
            )
        except Exception as e:
            logger.error(f"Failed to load persisted chains: {e}")
