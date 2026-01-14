"""
Telegram Rate Limiter - Token Bucket Algorithm with Priority Queue
Prevents Telegram API rate limit violations (429 errors)

Telegram API Limits:
- 30 messages/second per bot (hard limit)
- 20 messages/minute to same chat (recommended)

Features:
- Token Bucket algorithm for smooth rate limiting
- Priority-based queue (CRITICAL > HIGH > NORMAL > LOW)
- Thread-safe implementation (uses threading.Lock)
- Queue overflow handling (drops LOW priority first)
- Statistics tracking

Version: 1.0.0
"""

import threading
import time
import logging
from collections import deque
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Callable, Any
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels for queue ordering"""
    LOW = 0       # Daily stats, non-urgent reports
    NORMAL = 1    # Regular notifications, menu responses
    HIGH = 2      # Entry/Exit alerts, trade notifications
    CRITICAL = 3  # Errors, stop-loss hits, PANIC actions


@dataclass
class ThrottledMessage:
    """Represents a queued message with metadata"""
    chat_id: str
    text: str
    priority: MessagePriority = MessagePriority.NORMAL
    parse_mode: str = "HTML"
    reply_markup: Optional[Dict] = None
    timestamp: datetime = field(default_factory=datetime.now)
    retries: int = 0
    max_retries: int = 3
    callback: Optional[Callable] = None
    message_id: Optional[str] = None
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = f"msg_{int(time.time() * 1000)}_{id(self)}"


class TokenBucket:
    """
    Token Bucket algorithm for rate limiting.
    Allows bursts while maintaining average rate.
    """
    
    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        refill_interval: float = 1.0
    ):
        """
        Initialize token bucket.
        
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per refill interval
            refill_interval: Seconds between refills
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.refill_interval = refill_interval
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = threading.Lock()
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        
        if elapsed >= self.refill_interval:
            intervals = int(elapsed / self.refill_interval)
            tokens_to_add = intervals * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now - (elapsed % self.refill_interval)
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens consumed, False if not enough tokens
        """
        with self._lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Calculate wait time until tokens available.
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Seconds to wait (0 if tokens available now)
        """
        with self._lock:
            self._refill()
            
            if self.tokens >= tokens:
                return 0.0
            
            tokens_needed = tokens - self.tokens
            intervals_needed = tokens_needed / self.refill_rate
            return intervals_needed * self.refill_interval
    
    def get_available_tokens(self) -> float:
        """Get current available tokens"""
        with self._lock:
            self._refill()
            return self.tokens


class TelegramRateLimiter:
    """
    Rate limiter for single Telegram bot.
    Enforces: 20 messages/minute, 30 messages/second
    Uses Token Bucket algorithm with priority queue.
    """
    
    def __init__(
        self,
        bot_name: str,
        max_per_minute: int = 20,
        max_per_second: int = 30,
        max_queue_size: int = 100,
        send_callback: Optional[Callable] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            bot_name: Name for logging
            max_per_minute: Max messages per minute (default 20)
            max_per_second: Max messages per second (default 30)
            max_queue_size: Max queued messages (default 100)
            send_callback: Function to call to send message
        """
        self.bot_name = bot_name
        self.max_per_minute = max_per_minute
        self.max_per_second = max_per_second
        self.max_queue_size = max_queue_size
        self.send_callback = send_callback
        
        # Token buckets for rate limiting
        # Per-second bucket: refills 30 tokens per second
        self.second_bucket = TokenBucket(
            capacity=max_per_second,
            refill_rate=max_per_second,
            refill_interval=1.0
        )
        
        # Per-minute bucket: refills ~0.33 tokens per second (20/60)
        self.minute_bucket = TokenBucket(
            capacity=max_per_minute,
            refill_rate=max_per_minute / 60.0,
            refill_interval=1.0
        )
        
        # Priority queues (separate for each priority level)
        self.queues: Dict[MessagePriority, deque] = {
            MessagePriority.CRITICAL: deque(),
            MessagePriority.HIGH: deque(),
            MessagePriority.NORMAL: deque(),
            MessagePriority.LOW: deque()
        }
        
        # Statistics
        self.stats = {
            "total_sent": 0,
            "total_queued": 0,
            "total_dropped": 0,
            "total_rate_limited": 0,
            "total_errors": 0,
            "by_priority": {p.name: 0 for p in MessagePriority}
        }
        
        # Control
        self._running = False
        self._processor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
    
    def start(self):
        """Start the rate limiter processor thread"""
        if self._running:
            logger.warning(f"{self.bot_name} rate limiter already running")
            return
        
        self._running = True
        self._stop_event.clear()
        self._processor_thread = threading.Thread(
            target=self._process_queue_loop,
            name=f"RateLimiter-{self.bot_name}",
            daemon=True
        )
        self._processor_thread.start()
        logger.info(f"{self.bot_name} rate limiter started (max {self.max_per_minute}/min)")
    
    def stop(self, timeout: float = 5.0):
        """Stop the rate limiter processor thread"""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        
        if self._processor_thread and self._processor_thread.is_alive():
            self._processor_thread.join(timeout=timeout)
            if self._processor_thread.is_alive():
                logger.warning(f"{self.bot_name} rate limiter thread did not stop cleanly")
        
        logger.info(f"{self.bot_name} rate limiter stopped")
    
    def enqueue(self, message: ThrottledMessage) -> bool:
        """
        Add message to queue.
        
        Args:
            message: ThrottledMessage to queue
            
        Returns:
            True if queued, False if dropped
        """
        with self._lock:
            total_queued = self._get_total_queued()
            
            # Check queue capacity
            if total_queued >= self.max_queue_size:
                # Try to drop LOW priority messages first
                if len(self.queues[MessagePriority.LOW]) > 0:
                    dropped = self.queues[MessagePriority.LOW].popleft()
                    self.stats["total_dropped"] += 1
                    logger.warning(
                        f"{self.bot_name}: Dropped LOW priority message to make room: "
                        f"{dropped.text[:50]}..."
                    )
                elif message.priority == MessagePriority.LOW:
                    # Don't queue new LOW if queue full
                    self.stats["total_dropped"] += 1
                    logger.warning(
                        f"{self.bot_name}: Queue full, dropping LOW priority: "
                        f"{message.text[:50]}..."
                    )
                    return False
                elif message.priority == MessagePriority.NORMAL:
                    # Drop oldest NORMAL if new is NORMAL or higher
                    if len(self.queues[MessagePriority.NORMAL]) > 0:
                        dropped = self.queues[MessagePriority.NORMAL].popleft()
                        self.stats["total_dropped"] += 1
                        logger.warning(
                            f"{self.bot_name}: Dropped NORMAL priority message: "
                            f"{dropped.text[:50]}..."
                        )
                    else:
                        self.stats["total_dropped"] += 1
                        return False
            
            # Enqueue message
            self.queues[message.priority].append(message)
            self.stats["total_queued"] += 1
            self.stats["by_priority"][message.priority.name] += 1
            
            return True
    
    def send_immediate(self, message: ThrottledMessage) -> bool:
        """
        Try to send message immediately (bypass queue for CRITICAL).
        Falls back to queue if rate limited.
        
        Args:
            message: ThrottledMessage to send
            
        Returns:
            True if sent immediately, False if queued
        """
        if message.priority == MessagePriority.CRITICAL:
            # CRITICAL messages try to send immediately
            if self._can_send():
                return self._send_message(message)
        
        # Otherwise queue it
        return self.enqueue(message)
    
    def _can_send(self) -> bool:
        """Check if we can send a message now"""
        return (
            self.second_bucket.get_available_tokens() >= 1 and
            self.minute_bucket.get_available_tokens() >= 1
        )
    
    def _consume_tokens(self) -> bool:
        """Consume tokens from both buckets"""
        if self.second_bucket.consume(1) and self.minute_bucket.consume(1):
            return True
        return False
    
    def _get_total_queued(self) -> int:
        """Get total messages in all queues"""
        return sum(len(q) for q in self.queues.values())
    
    def _get_next_message(self) -> Optional[ThrottledMessage]:
        """Get next message from queue (priority order)"""
        with self._lock:
            # Priority order: CRITICAL > HIGH > NORMAL > LOW
            for priority in [
                MessagePriority.CRITICAL,
                MessagePriority.HIGH,
                MessagePriority.NORMAL,
                MessagePriority.LOW
            ]:
                if len(self.queues[priority]) > 0:
                    return self.queues[priority].popleft()
            return None
    
    def _send_message(self, message: ThrottledMessage) -> bool:
        """
        Send message via callback.
        
        Args:
            message: ThrottledMessage to send
            
        Returns:
            True if sent successfully
        """
        if not self.send_callback:
            logger.error(f"{self.bot_name}: No send callback configured")
            return False
        
        try:
            # Consume tokens
            if not self._consume_tokens():
                self.stats["total_rate_limited"] += 1
                return False
            
            # Send via callback
            result = self.send_callback(
                chat_id=message.chat_id,
                text=message.text,
                parse_mode=message.parse_mode,
                reply_markup=message.reply_markup
            )
            
            if result:
                self.stats["total_sent"] += 1
                return True
            else:
                self.stats["total_errors"] += 1
                return False
                
        except Exception as e:
            logger.error(f"{self.bot_name}: Send error: {e}")
            self.stats["total_errors"] += 1
            return False
    
    def _process_queue_loop(self):
        """Main queue processor loop (runs in thread)"""
        logger.info(f"{self.bot_name}: Queue processor started")
        
        while self._running and not self._stop_event.is_set():
            try:
                # Check if we can send
                if not self._can_send():
                    # Wait for tokens to refill
                    wait_time = max(
                        self.second_bucket.get_wait_time(1),
                        self.minute_bucket.get_wait_time(1)
                    )
                    if wait_time > 0:
                        self._stop_event.wait(min(wait_time, 0.1))
                    continue
                
                # Get next message
                message = self._get_next_message()
                if message is None:
                    # Queue empty, wait a bit
                    self._stop_event.wait(0.1)
                    continue
                
                # Send the message
                success = self._send_message(message)
                
                if not success and message.retries < message.max_retries:
                    # Re-queue for retry
                    message.retries += 1
                    with self._lock:
                        self.queues[message.priority].appendleft(message)
                    self._stop_event.wait(0.5)  # Wait before retry
                
                # Small delay to spread out messages
                self._stop_event.wait(0.05)
                
            except Exception as e:
                logger.error(f"{self.bot_name}: Queue processor error: {e}")
                self._stop_event.wait(1.0)
        
        logger.info(f"{self.bot_name}: Queue processor stopped")
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        with self._lock:
            return {
                "bot": self.bot_name,
                "running": self._running,
                "queued": {
                    "critical": len(self.queues[MessagePriority.CRITICAL]),
                    "high": len(self.queues[MessagePriority.HIGH]),
                    "normal": len(self.queues[MessagePriority.NORMAL]),
                    "low": len(self.queues[MessagePriority.LOW]),
                    "total": self._get_total_queued()
                },
                "tokens": {
                    "per_second": self.second_bucket.get_available_tokens(),
                    "per_minute": self.minute_bucket.get_available_tokens()
                },
                "stats": self.stats.copy()
            }
    
    def clear_queue(self, priority: Optional[MessagePriority] = None):
        """
        Clear messages from queue.
        
        Args:
            priority: Specific priority to clear, or None for all
        """
        with self._lock:
            if priority:
                cleared = len(self.queues[priority])
                self.queues[priority].clear()
                logger.info(f"{self.bot_name}: Cleared {cleared} {priority.name} messages")
            else:
                total = self._get_total_queued()
                for q in self.queues.values():
                    q.clear()
                logger.info(f"{self.bot_name}: Cleared all {total} messages")


class MultiRateLimiter:
    """
    Manages rate limiters for multiple bots.
    Provides unified interface for the 3-bot system.
    """
    
    def __init__(self):
        self.limiters: Dict[str, TelegramRateLimiter] = {}
        self._lock = threading.Lock()
    
    def add_limiter(
        self,
        bot_name: str,
        max_per_minute: int = 20,
        max_per_second: int = 30,
        send_callback: Optional[Callable] = None
    ) -> TelegramRateLimiter:
        """
        Add a rate limiter for a bot.
        
        Args:
            bot_name: Name of the bot
            max_per_minute: Max messages per minute
            max_per_second: Max messages per second
            send_callback: Function to send messages
            
        Returns:
            The created TelegramRateLimiter
        """
        with self._lock:
            limiter = TelegramRateLimiter(
                bot_name=bot_name,
                max_per_minute=max_per_minute,
                max_per_second=max_per_second,
                send_callback=send_callback
            )
            self.limiters[bot_name] = limiter
            return limiter
    
    def get_limiter(self, bot_name: str) -> Optional[TelegramRateLimiter]:
        """Get rate limiter for a bot"""
        return self.limiters.get(bot_name)
    
    def start_all(self):
        """Start all rate limiters"""
        for limiter in self.limiters.values():
            limiter.start()
        logger.info(f"Started {len(self.limiters)} rate limiters")
    
    def stop_all(self):
        """Stop all rate limiters"""
        for limiter in self.limiters.values():
            limiter.stop()
        logger.info(f"Stopped {len(self.limiters)} rate limiters")
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics from all rate limiters"""
        return {name: limiter.get_stats() for name, limiter in self.limiters.items()}
    
    def get_health_status(self) -> Dict:
        """
        Get health status of all rate limiters.
        Returns warnings if any queue is getting full.
        """
        status = {
            "healthy": True,
            "warnings": [],
            "limiters": {}
        }
        
        for name, limiter in self.limiters.items():
            stats = limiter.get_stats()
            total_queued = stats["queued"]["total"]
            max_queue = limiter.max_queue_size
            
            limiter_status = {
                "running": stats["running"],
                "queue_usage": f"{total_queued}/{max_queue}",
                "queue_percent": (total_queued / max_queue) * 100 if max_queue > 0 else 0
            }
            
            # Warning if queue > 70% full
            if total_queued > max_queue * 0.7:
                status["warnings"].append(
                    f"{name} queue high: {total_queued}/{max_queue}"
                )
                status["healthy"] = False
            
            # Warning if messages dropped
            if stats["stats"]["total_dropped"] > 0:
                status["warnings"].append(
                    f"{name} dropped {stats['stats']['total_dropped']} messages"
                )
            
            status["limiters"][name] = limiter_status
        
        return status
