"""
TTL Cache for lightweight DB read caching
"""
from threading import Lock
import time
import os
from typing import Optional, Any


class TTLCache:
    """Thread-safe TTL cache for lightweight DB read caching."""
    
    def __init__(self, ttl_seconds: int = 10, max_entries: int = 128):
        self.ttl = ttl_seconds
        self.max_entries = max_entries
        self._data: dict = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        now = time.time()
        with self._lock:
            payload = self._data.get(key)
            if not payload:
                return None
            value, expires = payload
            if expires < now:
                self._data.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any):
        """Set value in cache with TTL"""
        expires = time.time() + self.ttl
        with self._lock:
            if len(self._data) >= self.max_entries:
                # Remove oldest entry
                oldest_key = next(iter(self._data))
                self._data.pop(oldest_key, None)
            self._data[key] = (value, expires)

    def delete(self, key: str):
        """Delete key from cache"""
        with self._lock:
            self._data.pop(key, None)

    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._data.clear()


# Cache instances
UNREAD_CACHE_TTL = int(os.getenv('UNREAD_CACHE_TTL', '15'))
UNAPPROVED_CACHE_TTL = int(os.getenv('UNAPPROVED_CACHE_TTL', '10'))

unread_cache = TTLCache(ttl_seconds=UNREAD_CACHE_TTL, max_entries=2048)
unapproved_cache = TTLCache(ttl_seconds=UNAPPROVED_CACHE_TTL, max_entries=16)

