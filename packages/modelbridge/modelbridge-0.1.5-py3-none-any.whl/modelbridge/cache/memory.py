"""
In-memory cache implementation with LRU eviction
"""
import asyncio
from typing import Optional, Any, Dict, OrderedDict
from datetime import datetime, timedelta
import threading
import logging
import sys

from .base import CacheInterface, CacheEntry

logger = logging.getLogger(__name__)


class MemoryCache(CacheInterface):
    """Thread-safe in-memory cache with LRU eviction"""
    
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        super().__init__(ttl, max_size)
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._cleanup_task = None
        self._cleanup_interval = 300  # 5 minutes
        
    async def initialize(self) -> bool:
        """Initialize cache and start cleanup task"""
        try:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            logger.info(f"Memory cache initialized - TTL: {self.ttl}s, Max size: {self.max_size}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize memory cache: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown cache and cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        await self.clear()
        logger.info("Memory cache shutdown complete")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            # Check expiration
            if entry.is_expired():
                del self._cache[key]
                return None
            
            # Update access stats and move to end (most recently used)
            entry.access()
            self._cache.move_to_end(key)
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.ttl
            expires_at = datetime.utcnow() + timedelta(seconds=ttl) if ttl > 0 else None
            
            # Calculate approximate size
            size_bytes = self._calculate_size(value)
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                size_bytes=size_bytes
            )
            
            with self._lock:
                # If key exists, remove old entry
                if key in self._cache:
                    del self._cache[key]
                
                # Add new entry
                self._cache[key] = entry
                
                # Evict oldest entries if over max size
                while len(self._cache) > self.max_size:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                    self.stats['evictions'] += 1
                    logger.debug(f"Evicted oldest entry: {oldest_key[:16]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache key {key[:16]}...: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            
            if entry.is_expired():
                del self._cache[key]
                return False
            
            return True
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared {count} cache entries")
            return True
    
    async def size(self) -> int:
        """Get number of items in cache"""
        with self._lock:
            return len(self._cache)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_size_bytes = sum(
                entry.size_bytes or 0 
                for entry in self._cache.values()
            )
            
            return {
                **self.stats,
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': self.get_hit_rate(),
                'total_size_bytes': total_size_bytes,
                'avg_size_bytes': total_size_bytes / len(self._cache) if self._cache else 0,
                'oldest_entry': min(
                    (entry.created_at for entry in self._cache.values()),
                    default=None
                ),
                'newest_entry': max(
                    (entry.created_at for entry in self._cache.values()),
                    default=None
                )
            }
    
    async def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        expired_count = 0
        
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                expired_count += 1
        
        if expired_count > 0:
            logger.debug(f"Cleaned up {expired_count} expired cache entries")
        
        return expired_count
    
    async def get_entries_by_pattern(self, pattern: str) -> Dict[str, Any]:
        """Get all entries matching pattern (for debugging)"""
        with self._lock:
            matching = {}
            for key, entry in self._cache.items():
                if pattern in key:
                    matching[key] = {
                        'value': entry.value,
                        'created_at': entry.created_at,
                        'expires_at': entry.expires_at,
                        'access_count': entry.access_count,
                        'is_expired': entry.is_expired()
                    }
            return matching
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate memory size of value"""
        try:
            # Rough estimation - not exact but gives an idea
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (int, float)):
                return sys.getsizeof(value)
            elif isinstance(value, (list, dict)):
                return sys.getsizeof(str(value))
            else:
                return sys.getsizeof(str(value))
        except Exception:
            return 0
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired entries"""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                expired_count = await self.cleanup_expired()
                
                # Log stats periodically
                stats = await self.get_stats()
                logger.debug(
                    f"Memory cache: {stats['size']}/{self.max_size} entries, "
                    f"hit rate: {stats['hit_rate']:.2%}, "
                    f"expired cleaned: {expired_count}"
                )
                
            except asyncio.CancelledError:
                logger.debug("Memory cache cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in memory cache cleanup: {e}")
                await asyncio.sleep(60)  # Wait before retrying