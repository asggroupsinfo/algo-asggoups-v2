"""
Fixed Clock & Calendar Display System V5
Provides real-time IST time and date for V5 3-Bot Architecture

Features:
- Real-time IST clock display
- Calendar with date and day
- Integration with Sticky Headers
- Session Manager time provider

Version: 5.0.0
Date: 2026-01-15
Restored from V4 design, adapted for V5 architecture
"""

import asyncio
from datetime import datetime
from typing import Optional, Callable, List
import logging

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False

logger = logging.getLogger(__name__)


class FixedClockSystem:
    """
    Real-time IST clock for V5 Telegram system.
    
    Provides:
    - Current IST time
    - Formatted date and day
    - Callbacks for header updates
    - Integration with Session Manager
    """
    
    def __init__(self, timezone_name: str = 'Asia/Kolkata'):
        """
        Initialize Fixed Clock System.
        
        Args:
            timezone_name: Timezone name (default: Asia/Kolkata for IST)
        """
        self.timezone_name = timezone_name
        
        if HAS_PYTZ:
            self.timezone = pytz.timezone(timezone_name)
        else:
            self.timezone = None
            logger.warning("pytz not installed, using system timezone")
        
        self.is_running = False
        self._callbacks: List[Callable] = []
        self._stop_event = asyncio.Event()
        
        logger.info(f"FixedClockSystem initialized | Timezone: {timezone_name}")
    
    def get_current_time(self) -> datetime:
        """
        Get current time in configured timezone.
        
        Returns:
            datetime object in IST timezone
        """
        if self.timezone:
            return datetime.now(self.timezone)
        else:
            return datetime.now()
    
    def format_time_string(self) -> str:
        """
        Format time as HH:MM:SS IST.
        
        Returns:
            Formatted time string
        """
        current_time = self.get_current_time()
        return current_time.strftime("%H:%M:%S IST")
    
    def format_date_string(self) -> str:
        """
        Format date as DD MMM YYYY (Day).
        
        Returns:
            Formatted date string (e.g., "15 Jan 2026 (Wednesday)")
        """
        current_time = self.get_current_time()
        return current_time.strftime("%d %b %Y (%A)")
    
    def format_short_date(self) -> str:
        """
        Format date as DD-MM-YYYY.
        
        Returns:
            Short date string
        """
        current_time = self.get_current_time()
        return current_time.strftime("%d-%m-%Y")
    
    def format_clock_message(self) -> str:
        """
        Format combined clock and calendar message.
        
        Returns:
            Combined clock and date string for display
        """
        time_str = self.format_time_string()
        date_str = self.format_date_string()
        return f"🕐 {time_str} | 📅 {date_str}"
    
    def format_header_clock(self) -> str:
        """
        Format clock for sticky header (compact version).
        
        Returns:
            Compact clock string for header
        """
        current_time = self.get_current_time()
        time_str = current_time.strftime("%H:%M:%S")
        date_str = current_time.strftime("%d %b")
        day_str = current_time.strftime("%a")
        return f"🕐 {time_str} | 📅 {date_str} ({day_str})"
    
    def get_time_components(self) -> dict:
        """
        Get individual time components.
        
        Returns:
            Dictionary with hour, minute, second, date, day
        """
        current_time = self.get_current_time()
        return {
            "hour": current_time.hour,
            "minute": current_time.minute,
            "second": current_time.second,
            "date": current_time.strftime("%d %b %Y"),
            "day": current_time.strftime("%A"),
            "short_day": current_time.strftime("%a"),
            "timestamp": current_time.isoformat()
        }
    
    def get_minutes_since_midnight(self) -> int:
        """
        Get minutes since midnight (useful for session checks).
        
        Returns:
            Minutes since midnight in IST
        """
        current_time = self.get_current_time()
        return current_time.hour * 60 + current_time.minute
    
    def register_callback(self, callback: Callable):
        """
        Register callback for clock updates.
        
        Args:
            callback: Async function to call with clock message
        """
        self._callbacks.append(callback)
        logger.debug(f"Registered clock callback: {callback.__name__}")
    
    def unregister_callback(self, callback: Callable):
        """
        Unregister a callback.
        
        Args:
            callback: Callback to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            logger.debug(f"Unregistered clock callback: {callback.__name__}")
    
    async def start_clock_loop(self, update_interval: int = 1):
        """
        Start the clock update loop.
        
        Args:
            update_interval: Seconds between updates (default: 1)
        """
        if self.is_running:
            logger.warning("Clock loop already running")
            return
        
        self.is_running = True
        self._stop_event.clear()
        logger.info(f"Starting fixed clock loop (interval: {update_interval}s)")
        
        while self.is_running:
            try:
                clock_message = self.format_clock_message()
                
                # Notify all registered callbacks
                for callback in self._callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(clock_message)
                        else:
                            callback(clock_message)
                    except Exception as e:
                        logger.error(f"Clock callback error: {e}")
                
                # Wait for next update or stop signal
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=update_interval
                    )
                    if self._stop_event.is_set():
                        break
                except asyncio.TimeoutError:
                    pass  # Normal timeout, continue loop
                    
            except Exception as e:
                logger.error(f"Clock loop error: {e}")
                await asyncio.sleep(5)  # Wait before retry
        
        logger.info("Clock loop stopped")
    
    def stop_clock(self):
        """Stop the clock loop."""
        self.is_running = False
        self._stop_event.set()
        logger.info("Clock stop requested")
    
    def stop_clock_loop(self):
        """Stop the clock loop (alias for stop_clock)."""
        self.stop_clock()
    
    def get_status(self) -> dict:
        """
        Get clock system status.
        
        Returns:
            Status dictionary
        """
        return {
            "running": self.is_running,
            "timezone": self.timezone_name,
            "current_time": self.format_time_string(),
            "current_date": self.format_date_string(),
            "callbacks_registered": len(self._callbacks),
            "pytz_available": HAS_PYTZ
        }


# Singleton instance for global access
_clock_instance: Optional[FixedClockSystem] = None


def get_clock_system() -> FixedClockSystem:
    """
    Get the global clock system instance.
    
    Returns:
        FixedClockSystem singleton instance
    """
    global _clock_instance
    if _clock_instance is None:
        _clock_instance = FixedClockSystem()
    return _clock_instance


def format_ist_time() -> str:
    """
    Convenience function to get formatted IST time.
    
    Returns:
        Current IST time string
    """
    return get_clock_system().format_time_string()


def format_ist_date() -> str:
    """
    Convenience function to get formatted IST date.
    
    Returns:
        Current IST date string
    """
    return get_clock_system().format_date_string()


# Test function
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing FixedClockSystem...")
    
    clock = FixedClockSystem()
    
    print(f"Time: {clock.format_time_string()}")
    print(f"Date: {clock.format_date_string()}")
    print(f"Clock Message: {clock.format_clock_message()}")
    print(f"Header Clock: {clock.format_header_clock()}")
    print(f"Components: {clock.get_time_components()}")
    print(f"Minutes since midnight: {clock.get_minutes_since_midnight()}")
    print(f"Status: {clock.get_status()}")
    
    print("\nFixedClockSystem test complete!")
