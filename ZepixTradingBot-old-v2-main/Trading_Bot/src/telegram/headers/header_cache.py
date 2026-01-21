"""
Header Cache - Efficient Sticky Header Storage

Caches header content to prevent unnecessary re-rendering.

Version: 1.0.0
Created: 2026-01-21
Part of: TELEGRAM_V5_STICKY_HEADER
"""

import time
from typing import Dict, Optional

class HeaderCache:
    """Thread-safe cache for sticky header content"""

    def __init__(self, ttl_seconds: int = 2):
        self.cache: Dict[str, Dict] = {} # {style: {'content': str, 'timestamp': float}}
        self.ttl = ttl_seconds

    def get(self, style: str) -> Optional[str]:
        """Get cached header if valid"""
        if style in self.cache:
            entry = self.cache[style]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['content']
        return None

    def set(self, style: str, content: str):
        """Set cached header"""
        self.cache[style] = {
            'content': content,
            'timestamp': time.time()
        }
